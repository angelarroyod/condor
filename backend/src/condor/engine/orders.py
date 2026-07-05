"""Order placement, fill execution, and the limit-order matcher.

Correctness rests on a per-account row lock: ``_execute_fill`` takes
``SELECT ... FOR UPDATE`` on the account before touching cash, so two orders
racing on the same account are serialized and can never oversell the balance.
Idempotent placement is enforced by the ``(account_id, idempotency_key)`` unique
constraint. See ``tests/test_orders.py`` (requires Postgres).
"""

from __future__ import annotations

import asyncio
import logging
import uuid
from datetime import UTC, datetime
from decimal import Decimal

from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from condor.api.errors import AppError
from condor.config import get_settings
from condor.db.models import Account, Fill, Order, Position, Symbol
from condor.engine.enums import OrderSide, OrderStatus, OrderType
from condor.engine.execution import apply_slippage
from condor.engine.position import PositionState, apply_fill
from condor.redis_bus import get_latest_price
from condor.schemas.trading import OrderCreate

log = logging.getLogger(__name__)


def _crosses(side: str, market_price: Decimal, limit_price: Decimal) -> bool:
    if side == OrderSide.BUY:
        return market_price <= limit_price
    return market_price >= limit_price


async def place_order(
    session: AsyncSession, redis: Redis, account_id: uuid.UUID, data: OrderCreate
) -> Order:
    """Validate, persist, and (if marketable) fill an order. Idempotent."""
    symbol_id = await session.scalar(
        select(Symbol.id).where(Symbol.symbol == data.symbol.upper())
    )
    if symbol_id is None:
        raise AppError(f"unknown symbol: {data.symbol}", code="symbol_not_found", status_code=404)
    if data.type == OrderType.LIMIT and data.limit_price is None:
        raise AppError("limit_price required for limit orders", code="bad_limit", status_code=422)

    # Idempotency: a repeated key returns the original order untouched.
    existing: Order | None = await session.scalar(
        select(Order).where(
            Order.account_id == account_id, Order.idempotency_key == data.idempotency_key
        )
    )
    if existing is not None:
        return existing

    order = Order(
        account_id=account_id,
        symbol_id=symbol_id,
        idempotency_key=data.idempotency_key,
        side=data.side.value,
        type=data.type.value,
        quantity=data.quantity,
        limit_price=data.limit_price,
        status=OrderStatus.PENDING.value,
    )
    session.add(order)
    try:
        await session.flush()
    except IntegrityError:
        # Concurrent placement with the same key won the race — return the winner.
        await session.rollback()
        existing = await session.scalar(
            select(Order).where(
                Order.account_id == account_id, Order.idempotency_key == data.idempotency_key
            )
        )
        if existing is not None:
            return existing
        raise

    ref = await get_latest_price(redis, data.symbol)
    if data.type == OrderType.MARKET:
        if ref is None:
            order.status = OrderStatus.REJECTED.value
            order.reject_reason = "no_market_price"
        else:
            await _execute_fill(session, order, ref)
    elif ref is not None and _crosses(order.side, ref, order.limit_price):  # type: ignore[arg-type]
        # Immediately marketable limit — fills at its limit price.
        await _execute_fill(session, order, order.limit_price)  # type: ignore[arg-type]
    # else: resting limit, left pending for the matcher.

    await session.commit()
    return order


async def _execute_fill(session: AsyncSession, order: Order, ref_price: Decimal) -> None:
    """Fill ``order`` at ``ref_price`` (+slippage) under a per-account row lock.

    Mutates cash, position, the order, and appends a fill — all in the caller's
    transaction. Sets the order to ``rejected`` (not filled) on insufficient cash.
    """
    settings = get_settings()
    account = await session.get(Account, order.account_id, with_for_update=True)
    if account is None:  # pragma: no cover — FK guarantees presence
        raise AppError("account not found", code="account_not_found", status_code=404)

    exec_price = apply_slippage(ref_price, order.side, settings.slippage_bps)
    qty = order.quantity
    fee = settings.fee_flat
    value = exec_price * qty

    if order.side == OrderSide.BUY:
        cost = value + fee
        if account.cash_balance < cost:
            order.status = OrderStatus.REJECTED.value
            order.reject_reason = "insufficient_funds"
            return
        account.cash_balance -= cost
    else:
        account.cash_balance += value - fee

    position = await session.get(
        Position,
        {"account_id": order.account_id, "symbol_id": order.symbol_id},
        with_for_update=True,
    )
    prior = (
        PositionState(position.quantity, position.avg_price, position.realized_pnl)
        if position is not None
        else PositionState()
    )
    new_state, _realized = apply_fill(prior, order.side, qty, exec_price)
    if position is None:
        session.add(
            Position(
                account_id=order.account_id,
                symbol_id=order.symbol_id,
                quantity=new_state.quantity,
                avg_price=new_state.avg_price,
                realized_pnl=new_state.realized_pnl,
            )
        )
    else:
        position.quantity = new_state.quantity
        position.avg_price = new_state.avg_price
        position.realized_pnl = new_state.realized_pnl

    session.add(
        Fill(
            order_id=order.id,
            account_id=order.account_id,
            symbol_id=order.symbol_id,
            side=order.side,
            price=exec_price,
            quantity=qty,
            fee=fee,
        )
    )
    order.status = OrderStatus.FILLED.value
    order.filled_quantity = qty
    order.avg_fill_price = exec_price
    order.filled_at = datetime.now(UTC)


async def cancel_order(
    session: AsyncSession, account_id: uuid.UUID, order_id: uuid.UUID
) -> Order:
    order = await session.get(Order, order_id, with_for_update=True)
    if order is None or order.account_id != account_id:
        raise AppError("order not found", code="order_not_found", status_code=404)
    if order.status != OrderStatus.PENDING.value:
        raise AppError(
            f"cannot cancel order in status {order.status}", code="not_cancellable", status_code=409
        )
    order.status = OrderStatus.CANCELLED.value
    await session.commit()
    return order


async def sweep_limits(session_factory: async_sessionmaker[AsyncSession], redis: Redis) -> int:
    """Fill any resting limit orders whose limit price the market has crossed.

    Polls the pending set (usually empty) rather than every tick. Returns the
    number of orders filled. Fills at the resting limit price.
    """
    async with session_factory() as session:
        stmt = (
            select(Order)
            .where(Order.status == OrderStatus.PENDING.value, Order.type == OrderType.LIMIT.value)
            .with_for_update(skip_locked=True)
        )
        pending = list(await session.scalars(stmt))
        if not pending:
            return 0

        symbol_ids = {o.symbol_id for o in pending}
        rows = await session.execute(
            select(Symbol.id, Symbol.symbol).where(Symbol.id.in_(symbol_ids))
        )
        names: dict[int, str] = {sid: sym for sid, sym in rows.all()}

        filled = 0
        for order in pending:
            price = await get_latest_price(redis, names[order.symbol_id])
            if price is None or order.limit_price is None:
                continue
            if _crosses(order.side, price, order.limit_price):
                await _execute_fill(session, order, order.limit_price)
                filled += 1
        if filled:
            await session.commit()
        return filled


async def run_matcher(
    session_factory: async_sessionmaker[AsyncSession], redis: Redis, interval: float = 1.0
) -> None:
    """Background loop: sweep crossable limit orders every ``interval`` seconds.

    ponytail: 1s polling ceiling is fine for paper trading; switch to a
    tick-driven consumer if sub-second limit latency ever matters.
    """
    log.info("matcher_started", extra={"interval_s": interval})
    while True:
        await asyncio.sleep(interval)
        try:
            n = await sweep_limits(session_factory, redis)
            if n:
                log.info("limits_filled", extra={"count": n})
        except asyncio.CancelledError:
            raise
        except Exception:
            log.exception("matcher_sweep_failed")
