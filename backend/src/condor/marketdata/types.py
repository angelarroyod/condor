"""Normalized market-data value objects, provider-agnostic.

These are what a ``MarketDataProvider`` emits after translating a source's wire
format. Prices/quantities are ``Decimal`` — this data feeds fills and P&L in
Phase 2, so it stays exact from the moment it enters the system.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class Tick:
    """A single executed trade."""

    symbol: str
    price: Decimal
    quantity: Decimal
    ts: datetime  # trade time, timezone-aware UTC


@dataclass(frozen=True, slots=True)
class Candle:
    """An OHLCV bar. ``bucket_start`` is the UTC bar-open boundary."""

    bucket_start: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal
    trade_count: int
