"""Portfolio service: equity, allocation, and the periodic equity snapshotter.

``compute_equity`` is the single source of truth for account equity, shared by
the ``/api/account`` route and the snapshotter so the two never drift.
"""

from __future__ import annotations

import asyncio
import logging
import uuid
from dataclasses import dataclass
from datetime import UTC, date, datetime
from decimal import Decimal

from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from condor.db.models import Account, EquitySnapshot, Position, Symbol
from condor.redis_bus import get_latest_price

log = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class Allocation:
    symbol: str
    market_value: Decimal  # signed (short positions are negative)
    weight: float  # share of gross exposure (|cash| + Σ|position value|)


async def _position_marks(
    session: AsyncSession, redis: Redis, account_id: uuid.UUID
) -> list[tuple[str, Decimal, Decimal]]:
    """(symbol, signed quantity, mark price) for open positions; mark falls back
    to average cost when no live price is cached."""
    rows = await session.execute(
        select(Position, Symbol.symbol)
        .join(Symbol, Symbol.id == Position.symbol_id)
        .where(Position.account_id == account_id, Position.quantity != 0)
    )
    out: list[tuple[str, Decimal, Decimal]] = []
    for pos, symbol in rows.all():
        mark = await get_latest_price(redis, symbol)
        out.append((symbol, pos.quantity, mark if mark is not None else pos.avg_price))
    return out


async def compute_equity(session: AsyncSession, redis: Redis, account: Account) -> Decimal:
    """Account equity = cash + Σ signed quantity × mark price."""
    equity = account.cash_balance
    for _symbol, qty, mark in await _position_marks(session, redis, account.id):
        equity += qty * mark
    return equity


async def allocation(session: AsyncSession, redis: Redis, account: Account) -> list[Allocation]:
    marks = await _position_marks(session, redis, account.id)
    values = [(sym, qty * mark) for sym, qty, mark in marks]
    gross = abs(account.cash_balance) + sum((abs(v) for _s, v in values), Decimal(0))
    if gross == 0:
        gross = Decimal(1)
    result = [Allocation("CASH", account.cash_balance, float(abs(account.cash_balance) / gross))]
    result.extend(Allocation(sym, value, float(abs(value) / gross)) for sym, value in values)
    return result


async def write_snapshot(session: AsyncSession, redis: Redis, account: Account) -> None:
    equity = await compute_equity(session, redis, account)
    session.add(
        EquitySnapshot(
            account_id=account.id,
            ts=datetime.now(UTC),
            equity=equity,
            cash=account.cash_balance,
        )
    )
    await session.commit()


def to_daily_equity(snapshots: list[EquitySnapshot]) -> list[float]:
    """Resample snapshots to one point per UTC day (the day's last snapshot)."""
    by_day: dict[date, float] = {}
    for snap in snapshots:
        by_day[snap.ts.date()] = float(snap.equity)
    return [by_day[day] for day in sorted(by_day)]


async def run_snapshotter(
    session_factory: async_sessionmaker[AsyncSession], redis: Redis, interval: float
) -> None:
    """Background loop writing one equity snapshot per ``interval`` seconds."""
    log.info("snapshotter_started", extra={"interval_s": interval})
    while True:
        await asyncio.sleep(interval)
        try:
            async with session_factory() as session:
                account = await session.scalar(
                    select(Account).order_by(Account.created_at).limit(1)
                )
                if account is not None:
                    await write_snapshot(session, redis, account)
        except asyncio.CancelledError:
            raise
        except Exception:
            log.exception("snapshot_failed")
