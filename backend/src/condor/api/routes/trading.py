"""Trading endpoints: account, orders, positions, fills.

Phase 2 operates a single seeded **demo account** with no auth. Multi-user auth
is out of scope here; ``get_demo_account`` resolves the one account.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from condor.api.deps import get_redis
from condor.api.errors import AppError
from condor.db.base import get_session
from condor.db.models import Account, Fill, Order, Position, Symbol
from condor.engine.orders import cancel_order, place_order
from condor.redis_bus import get_latest_price
from condor.schemas.trading import AccountOut, FillOut, OrderCreate, OrderOut, PositionOut

router = APIRouter(prefix="/api", tags=["trading"])


async def get_demo_account(session: AsyncSession = Depends(get_session)) -> Account:
    account = await session.scalar(select(Account).order_by(Account.created_at).limit(1))
    if account is None:
        raise AppError("no account seeded — run condor.seed", code="no_account", status_code=404)
    return account


@router.post("/orders", response_model=OrderOut, status_code=201)
async def create_order(
    data: OrderCreate,
    session: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis),
    account: Account = Depends(get_demo_account),
) -> Order:
    return await place_order(session, redis, account.id, data)


@router.get("/orders", response_model=list[OrderOut])
async def list_orders(
    status: str | None = None,
    session: AsyncSession = Depends(get_session),
    account: Account = Depends(get_demo_account),
) -> list[Order]:
    stmt = select(Order).where(Order.account_id == account.id)
    if status is not None:
        stmt = stmt.where(Order.status == status)
    stmt = stmt.order_by(Order.created_at.desc()).limit(200)
    return list(await session.scalars(stmt))


@router.delete("/orders/{order_id}", response_model=OrderOut)
async def delete_order(
    order_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    account: Account = Depends(get_demo_account),
) -> Order:
    return await cancel_order(session, account.id, order_id)


@router.get("/fills", response_model=list[FillOut])
async def list_fills(
    session: AsyncSession = Depends(get_session),
    account: Account = Depends(get_demo_account),
) -> list[Fill]:
    stmt = (
        select(Fill)
        .where(Fill.account_id == account.id)
        .order_by(Fill.created_at.desc())
        .limit(200)
    )
    return list(await session.scalars(stmt))


@router.get("/positions", response_model=list[PositionOut])
async def list_positions(
    session: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis),
    account: Account = Depends(get_demo_account),
) -> list[PositionOut]:
    rows = await session.execute(
        select(Position, Symbol.symbol)
        .join(Symbol, Symbol.id == Position.symbol_id)
        .where(Position.account_id == account.id, Position.quantity != 0)
        .order_by(Symbol.symbol)
    )
    out: list[PositionOut] = []
    for pos, symbol in rows.all():
        mark = await get_latest_price(redis, symbol)
        unrealized = pos.quantity * (mark - pos.avg_price) if mark is not None else None
        out.append(
            PositionOut(
                symbol=symbol,
                quantity=pos.quantity,
                avg_price=pos.avg_price,
                realized_pnl=pos.realized_pnl,
                mark_price=mark,
                unrealized_pnl=unrealized,
            )
        )
    return out


@router.get("/account", response_model=AccountOut)
async def get_account(
    session: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis),
    account: Account = Depends(get_demo_account),
) -> AccountOut:
    rows = await session.execute(
        select(Position, Symbol.symbol)
        .join(Symbol, Symbol.id == Position.symbol_id)
        .where(Position.account_id == account.id, Position.quantity != 0)
    )
    equity = account.cash_balance
    for pos, symbol in rows.all():
        mark = await get_latest_price(redis, symbol)
        equity += pos.quantity * (mark if mark is not None else pos.avg_price)
    return AccountOut(
        id=account.id,
        label=account.label,
        cash_balance=account.cash_balance,
        equity=equity,
    )
