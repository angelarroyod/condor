"""API DTOs for the trading engine."""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from condor.engine.enums import OrderSide, OrderType


class OrderCreate(BaseModel):
    symbol: str
    side: OrderSide
    type: OrderType
    quantity: Decimal = Field(gt=0)
    limit_price: Decimal | None = None
    idempotency_key: str = Field(min_length=1, max_length=64)


class OrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    symbol_id: int
    side: str
    type: str
    quantity: Decimal
    limit_price: Decimal | None
    filled_quantity: Decimal
    avg_fill_price: Decimal | None
    status: str
    reject_reason: str | None
    created_at: datetime


class FillOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    order_id: uuid.UUID
    symbol_id: int
    side: str
    price: Decimal
    quantity: Decimal
    fee: Decimal
    created_at: datetime


class PositionOut(BaseModel):
    """A position enriched with live mark price + unrealized P&L."""

    symbol: str
    quantity: Decimal
    avg_price: Decimal
    realized_pnl: Decimal
    mark_price: Decimal | None
    unrealized_pnl: Decimal | None


class AccountOut(BaseModel):
    id: uuid.UUID
    label: str
    cash_balance: Decimal
    equity: Decimal  # cash + Σ position market value
