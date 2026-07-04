"""Ingest worker entrypoint.

Wiring: provider trades -> per-symbol ``CandleAggregator`` -> (1) publish the
running candle's price to Redis for live fan-out, (2) upsert the in-progress 1m
candle to Postgres, (3) when a minute closes, finalize that bar.

The upsert on every tick means a worker restart recovers cleanly: it simply
resumes upserting the current minute (``ON CONFLICT DO UPDATE``); no partial
state is ever left inconsistent.
"""

from __future__ import annotations

import asyncio
import logging

from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from condor.config import get_settings
from condor.db.base import SessionLocal
from condor.db.models import Candle as CandleRow
from condor.db.models import Symbol
from condor.ingest.aggregator import CandleAggregator
from condor.logging import configure_logging
from condor.marketdata.binance import BinanceProvider
from condor.marketdata.types import Candle, Tick
from condor.redis_bus import make_redis, publish_tick
from condor.schemas.market import QuoteOut

log = logging.getLogger(__name__)


async def _load_symbol_ids(session: AsyncSession, symbols: list[str]) -> dict[str, int]:
    rows = await session.execute(
        select(Symbol.symbol, Symbol.id).where(Symbol.symbol.in_(symbols))
    )
    return {sym: sid for sym, sid in rows.all()}


async def _upsert_candle(session: AsyncSession, symbol_id: int, c: Candle) -> None:
    stmt = pg_insert(CandleRow).values(
        symbol_id=symbol_id,
        bucket_start=c.bucket_start,
        open=c.open,
        high=c.high,
        low=c.low,
        close=c.close,
        volume=c.volume,
        trade_count=c.trade_count,
    )
    stmt = stmt.on_conflict_do_update(
        index_elements=[CandleRow.symbol_id, CandleRow.bucket_start],
        set_={
            "high": stmt.excluded.high,
            "low": stmt.excluded.low,
            "close": stmt.excluded.close,
            "volume": stmt.excluded.volume,
            "trade_count": stmt.excluded.trade_count,
        },
    )
    await session.execute(stmt)
    await session.commit()


async def run() -> None:
    settings = get_settings()
    configure_logging(settings.log_level, as_json=settings.log_json)
    symbols = settings.symbol_list
    redis = make_redis()
    provider = BinanceProvider()
    aggregators: dict[str, CandleAggregator] = {s: CandleAggregator() for s in symbols}

    async with SessionLocal() as session:
        symbol_ids = await _load_symbol_ids(session, symbols)
        missing = set(symbols) - set(symbol_ids)
        if missing:
            log.warning("symbols_not_seeded", extra={"missing": sorted(missing)})

        log.info("ingest_started", extra={"symbols": symbols})
        async for tick in provider.stream_trades(symbols):
            await _handle_tick(session, redis, symbol_ids, aggregators, tick)


async def _handle_tick(
    session: AsyncSession,
    redis: Redis,
    symbol_ids: dict[str, int],
    aggregators: dict[str, CandleAggregator],
    tick: Tick,
) -> None:
    # 1. Live fan-out: publish the latest price + refresh the quote cache.
    quote = QuoteOut(symbol=tick.symbol, price=tick.price, ts=tick.ts)
    await publish_tick(redis, tick.symbol, quote.model_dump_json())

    # 2. Fold into the 1m candle; persist running + any just-closed bar.
    sid = symbol_ids.get(tick.symbol)
    if sid is None:
        return
    agg = aggregators[tick.symbol]
    closed = agg.push(tick)
    if closed is not None:
        await _upsert_candle(session, sid, closed)
    if agg.current is not None:
        await _upsert_candle(session, sid, agg.current)


def main() -> None:
    asyncio.run(run())


if __name__ == "__main__":
    main()
