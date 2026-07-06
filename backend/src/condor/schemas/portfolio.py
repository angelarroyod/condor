"""API DTOs for the portfolio & risk dashboard."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class EquityPoint(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ts: datetime
    equity: Decimal
    cash: Decimal


class AllocationOut(BaseModel):
    symbol: str
    market_value: Decimal
    weight: float


class MetricsOut(BaseModel):
    annualized_vol: float
    sharpe: float
    max_drawdown: float
    var_95: float
