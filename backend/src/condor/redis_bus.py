"""Redis helpers: live-price pub/sub channels + latest-quote cache.

Channel layout: one channel per symbol (``ticks:BTCUSDT``) so a WebSocket client
only receives the symbols it subscribed to. Latest quote is cached at
``quote:{symbol}`` for the REST snapshot endpoint.
"""

from __future__ import annotations

import json
from decimal import Decimal

from redis.asyncio import Redis

from condor.config import get_settings


def make_redis() -> Redis:
    return Redis.from_url(get_settings().redis_url, decode_responses=True)


def ticks_channel(symbol: str) -> str:
    return f"ticks:{symbol.upper()}"


def quote_key(symbol: str) -> str:
    return f"quote:{symbol.upper()}"


async def publish_tick(redis: Redis, symbol: str, payload: str) -> None:
    """Publish a serialized tick and refresh the latest-quote cache."""
    sym = symbol.upper()
    await redis.publish(ticks_channel(sym), payload)
    await redis.set(quote_key(sym), payload)


async def get_latest_price(redis: Redis, symbol: str) -> Decimal | None:
    """Latest traded price from the quote cache, or None if never seen."""
    raw = await redis.get(quote_key(symbol))
    if raw is None:
        return None
    return Decimal(str(json.loads(raw)["price"]))
