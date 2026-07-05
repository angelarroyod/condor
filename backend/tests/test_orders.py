"""DB-backed engine tests: idempotency, realized P&L + cash, concurrency lock.

Require Postgres (``TEST_DATABASE_URL``); skipped otherwise.
"""

from __future__ import annotations

import asyncio
import uuid
from collections.abc import Iterator
from decimal import Decimal

import pytest
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from tests.conftest import requires_db

from condor.config import get_settings
from condor.db.models import Account, Order, Position, Symbol
from condor.engine.enums import OrderSide, OrderStatus, OrderType
from condor.engine.orders import _execute_fill, place_order
from condor.schemas.trading import OrderCreate

pytestmark = requires_db

D = Decimal


class FakeRedis:
    """Minimal stand-in: no quote cached, so limits rest as pending."""

    async def get(self, _key: str) -> None:
        return None


@pytest.fixture(autouse=True)
def _zero_costs(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """Deterministic math: no slippage, no fee."""
    monkeypatch.setenv("SLIPPAGE_BPS", "0")
    monkeypatch.setenv("FEE_FLAT", "0")
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


async def _setup(factory: async_sessionmaker[AsyncSession], cash: str) -> tuple[uuid.UUID, int]:
    async with factory() as s:
        acct = Account(label="demo", cash_balance=D(cash))
        sym = Symbol(symbol="BTCUSDT", name="Bitcoin", asset_class="crypto", provider="binance")
        s.add_all([acct, sym])
        await s.flush()
        ids = (acct.id, sym.id)
        await s.commit()
        return ids


def _order(account_id: uuid.UUID, symbol_id: int, side: OrderSide, qty: str) -> Order:
    return Order(
        account_id=account_id,
        symbol_id=symbol_id,
        idempotency_key=str(uuid.uuid4()),
        side=side.value,
        type=OrderType.MARKET.value,
        quantity=D(qty),
        status=OrderStatus.PENDING.value,
    )


async def test_buy_then_partial_sell_realizes_pnl(
    db_factory: async_sessionmaker[AsyncSession],
) -> None:
    account_id, symbol_id = await _setup(db_factory, "100000")

    async with db_factory() as s:
        buy = _order(account_id, symbol_id, OrderSide.BUY, "10")
        s.add(buy)
        await s.flush()
        await _execute_fill(s, buy, D(100))  # cash 100000 -> 99000
        await s.commit()

    async with db_factory() as s:
        sell = _order(account_id, symbol_id, OrderSide.SELL, "4")
        s.add(sell)
        await s.flush()
        await _execute_fill(s, sell, D(130))  # +520 -> 99520
        await s.commit()

    async with db_factory() as s:
        acct = await s.get(Account, account_id)
        pos = await s.get(Position, {"account_id": account_id, "symbol_id": symbol_id})
        assert acct is not None and pos is not None
        assert acct.cash_balance == D("99520")
        assert pos.quantity == D("6")
        assert pos.avg_price == D("100")
        assert pos.realized_pnl == D("120")  # 4 * (130 - 100)


async def test_idempotent_placement(db_factory: async_sessionmaker[AsyncSession]) -> None:
    account_id, symbol_id = await _setup(db_factory, "100000")
    redis = FakeRedis()
    key = "abc-123"
    req = OrderCreate(
        symbol="BTCUSDT",
        side=OrderSide.BUY,
        type=OrderType.LIMIT,
        quantity=D("1"),
        limit_price=D("1"),  # far from market -> rests pending
        idempotency_key=key,
    )

    async with db_factory() as s:
        first = await place_order(s, redis, account_id, req)  # type: ignore[arg-type]
    async with db_factory() as s:
        second = await place_order(s, redis, account_id, req)  # type: ignore[arg-type]
        count = await s.scalar(select(func.count()).select_from(Order))

    assert first.id == second.id
    assert count == 1


async def test_concurrent_orders_cannot_oversell_cash(
    db_factory: async_sessionmaker[AsyncSession],
) -> None:
    # Cash 100; two racing buys of 1 @ 80 (cost 80 each). Only one can fill.
    account_id, symbol_id = await _setup(db_factory, "100")

    async def buy() -> str:
        async with db_factory() as s:
            order = _order(account_id, symbol_id, OrderSide.BUY, "1")
            s.add(order)
            await s.flush()
            await _execute_fill(s, order, D(80))
            await s.commit()
            return order.status

    results = await asyncio.gather(buy(), buy())

    assert sorted(results) == [OrderStatus.FILLED.value, OrderStatus.REJECTED.value]
    async with db_factory() as s:
        acct = await s.get(Account, account_id)
        assert acct is not None
        assert acct.cash_balance == D("20")  # exactly one 80 debit, never negative
