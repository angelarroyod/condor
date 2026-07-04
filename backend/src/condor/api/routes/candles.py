"""GET /api/symbols/{symbol}/candles — 1m base rows, resampled on read."""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from condor.api.errors import AppError
from condor.db.base import get_session
from condor.db.models import Candle as CandleRow
from condor.db.models import Symbol
from condor.marketdata.types import Candle
from condor.resample import INTERVAL_MINUTES, resample
from condor.schemas.market import CandleOut

router = APIRouter(prefix="/api/symbols", tags=["candles"])


@router.get("/{symbol}/candles", response_model=list[CandleOut])
async def get_candles(
    symbol: str,
    interval: str = Query("1m"),
    start: datetime | None = None,
    end: datetime | None = None,
    limit: int = Query(500, ge=1, le=5000),
    session: AsyncSession = Depends(get_session),
) -> list[Candle]:
    if interval not in INTERVAL_MINUTES:
        raise AppError(
            f"interval must be one of {sorted(INTERVAL_MINUTES)}",
            code="bad_interval",
            status_code=422,
        )

    symbol_id = await session.scalar(select(Symbol.id).where(Symbol.symbol == symbol.upper()))
    if symbol_id is None:
        raise AppError(f"unknown symbol: {symbol}", code="symbol_not_found", status_code=404)

    stmt = select(CandleRow).where(CandleRow.symbol_id == symbol_id)
    if start is not None:
        stmt = stmt.where(CandleRow.bucket_start >= start)
    if end is not None:
        stmt = stmt.where(CandleRow.bucket_start < end)
    # Resample needs ascending contiguous 1m bars; fetch newest `limit` then flip.
    stmt = stmt.order_by(CandleRow.bucket_start.desc()).limit(limit)

    rows = list(await session.scalars(stmt))
    rows.reverse()
    base = [
        Candle(r.bucket_start, r.open, r.high, r.low, r.close, r.volume, r.trade_count)
        for r in rows
    ]
    return resample(base, interval)
