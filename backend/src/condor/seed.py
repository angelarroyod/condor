"""Seed reference data + demo account. Idempotent — safe to re-run.

    python -m condor.seed

Also backfills a synthetic daily equity history for the demo account so the
risk dashboard is populated on first boot. This is clearly labelled demo data;
the live snapshotter appends real points on top of it.
"""

from __future__ import annotations

import asyncio
import logging
import random
from datetime import UTC, datetime, timedelta
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from condor.config import get_settings
from condor.db.base import SessionLocal
from condor.db.models import Account, EquitySnapshot, Fill, Order, Position, Strategy, Symbol
from condor.logging import configure_logging

log = logging.getLogger(__name__)

_NAMES = {
    "BTCUSDT": "Bitcoin / Tether",
    "ETHUSDT": "Ethereum / Tether",
    "SOLUSDT": "Solana / Tether",
}

_BACKFILL_DAYS = 180


async def _backfill_equity(session: AsyncSession, account: Account) -> int:
    """Seed ~180 days of synthetic daily equity (fixed-seed random walk)."""
    count = await session.scalar(
        select(func.count())
        .select_from(EquitySnapshot)
        .where(EquitySnapshot.account_id == account.id)
    )
    if count:
        return 0
    rng = random.Random(42)  # demo data, not security-sensitive
    equity = float(account.cash_balance)
    start = datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(
        days=_BACKFILL_DAYS
    )
    rows = []
    for day in range(_BACKFILL_DAYS + 1):
        equity *= 1.0 + rng.gauss(0.0004, 0.02)  # ~slight drift, 2% daily vol
        rows.append(
            EquitySnapshot(
                account_id=account.id,
                ts=start + timedelta(days=day),
                equity=Decimal(str(round(equity, 2))),
                cash=account.cash_balance,
            )
        )
    session.add_all(rows)
    return len(rows)


# A couple of pre-filled demo trades so positions/blotter/allocation aren't empty
# on first boot. (symbol, quantity, fill price) — labelled demo data.
_DEMO_TRADES = [("BTCUSDT", "0.5", "63000"), ("ETHUSDT", "5", "1800")]


async def _seed_demo_trades(
    session: AsyncSession, account: Account, symbol_ids: dict[str, int]
) -> int:
    """Insert filled demo orders + fills + positions (idempotent per account)."""
    existing = await session.scalar(
        select(func.count()).select_from(Order).where(Order.account_id == account.id)
    )
    if existing:
        return 0
    spent = Decimal(0)
    for symbol, qty_s, price_s in _DEMO_TRADES:
        sid = symbol_ids.get(symbol)
        if sid is None:
            continue
        qty, price = Decimal(qty_s), Decimal(price_s)
        order = Order(
            account_id=account.id,
            symbol_id=sid,
            idempotency_key=f"seed-{symbol}",
            side="buy",
            type="market",
            quantity=qty,
            filled_quantity=qty,
            avg_fill_price=price,
            status="filled",
            filled_at=datetime.now(UTC),
        )
        session.add(order)
        await session.flush()
        session.add(
            Fill(
                order_id=order.id,
                account_id=account.id,
                symbol_id=sid,
                side="buy",
                price=price,
                quantity=qty,
                fee=Decimal(0),
            )
        )
        session.add(
            Position(account_id=account.id, symbol_id=sid, quantity=qty, avg_price=price)
        )
        spent += qty * price
    account.cash_balance = account.cash_balance - spent
    return len(_DEMO_TRADES)


async def _seed_saved_strategy(session: AsyncSession) -> int:
    """One saved options strategy (an iron condor) for the demo."""
    existing = await session.scalar(select(func.count()).select_from(Strategy))
    if existing:
        return 0
    definition = {
        "legs": [
            {"kind": "put", "direction": "long", "strike": 80, "iv": 0.6, "quantity": 1},
            {"kind": "put", "direction": "short", "strike": 90, "iv": 0.6, "quantity": 1},
            {"kind": "call", "direction": "short", "strike": 110, "iv": 0.6, "quantity": 1},
            {"kind": "call", "direction": "long", "strike": 120, "iv": 0.6, "quantity": 1},
        ],
        "spot": 100,
        "rate": 0.05,
        "time_to_expiry": 0.0822,
        "dividend_yield": 0,
    }
    session.add(Strategy(name="Demo Iron Condor", definition=definition))
    return 1


async def seed() -> None:
    settings = get_settings()
    configure_logging(settings.log_level, as_json=settings.log_json)
    rows = [
        {
            "symbol": s,
            "name": _NAMES.get(s, s),
            "asset_class": "crypto",
            "provider": "binance",
        }
        for s in settings.symbol_list
    ]
    async with SessionLocal() as session:
        stmt = pg_insert(Symbol).values(rows).on_conflict_do_nothing(index_elements=["symbol"])
        await session.execute(stmt)

        # One demo account with the configured starting cash (idempotent).
        account = await session.scalar(select(Account).where(Account.label == "demo"))
        if account is None:
            account = Account(label="demo", cash_balance=settings.starting_cash)
            session.add(account)
            await session.flush()

        backfilled = await _backfill_equity(session, account)

        sym_rows = await session.execute(select(Symbol.symbol, Symbol.id))
        symbol_ids = {symbol: sid for symbol, sid in sym_rows.all()}
        trades = await _seed_demo_trades(session, account, symbol_ids)
        strategies = await _seed_saved_strategy(session)

        await session.commit()
    log.info(
        "seeded",
        extra={
            "symbols": len(rows),
            "equity_backfill": backfilled,
            "demo_trades": trades,
            "saved_strategies": strategies,
        },
    )


if __name__ == "__main__":
    asyncio.run(seed())
