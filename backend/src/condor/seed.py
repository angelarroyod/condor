"""Seed reference data (default symbols). Idempotent — safe to re-run.

    python -m condor.seed
"""

from __future__ import annotations

import asyncio
import logging

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert

from condor.config import get_settings
from condor.db.base import SessionLocal
from condor.db.models import Account, Symbol
from condor.logging import configure_logging

log = logging.getLogger(__name__)

_NAMES = {
    "BTCUSDT": "Bitcoin / Tether",
    "ETHUSDT": "Ethereum / Tether",
    "SOLUSDT": "Solana / Tether",
}


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
        exists = await session.scalar(select(Account.id).where(Account.label == "demo"))
        if exists is None:
            session.add(Account(label="demo", cash_balance=settings.starting_cash))

        await session.commit()
    log.info("seeded", extra={"symbols": len(rows), "demo_account": exists is None})


if __name__ == "__main__":
    asyncio.run(seed())
