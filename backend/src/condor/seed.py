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
from condor.db.models import Account, EquitySnapshot, Symbol
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
        await session.commit()
    log.info("seeded", extra={"symbols": len(rows), "equity_backfill": backfilled})


if __name__ == "__main__":
    asyncio.run(seed())
