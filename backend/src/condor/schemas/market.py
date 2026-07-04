"""API DTOs for market-data endpoints (Pydantic v2)."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class SymbolOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    symbol: str
    name: str
    asset_class: str
    provider: str


class CandleOut(BaseModel):
    """Serialized as strings for prices to preserve Decimal precision on the wire."""

    model_config = ConfigDict(from_attributes=True)

    bucket_start: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal
    trade_count: int


class QuoteOut(BaseModel):
    symbol: str
    price: Decimal
    ts: datetime
