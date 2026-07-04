"""GET /api/quotes — latest price snapshot from the Redis cache."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from redis.asyncio import Redis

from condor.api.deps import get_redis
from condor.redis_bus import quote_key
from condor.schemas.market import QuoteOut

router = APIRouter(prefix="/api/quotes", tags=["quotes"])


@router.get("", response_model=list[QuoteOut])
async def latest_quotes(
    symbols: str = Query(..., description="Comma-separated symbols, e.g. BTCUSDT,ETHUSDT"),
    redis: Redis = Depends(get_redis),
) -> list[QuoteOut]:
    wanted = [s.strip().upper() for s in symbols.split(",") if s.strip()]
    if not wanted:
        return []
    raw = await redis.mget(*[quote_key(s) for s in wanted])
    return [QuoteOut.model_validate_json(v) for v in raw if v is not None]
