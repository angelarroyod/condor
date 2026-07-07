"""API DTOs for the options analytics endpoints.

These use ``float`` throughout: options pricing is the analytical path where
floats are acceptable (unlike the accounting paths, which stay Decimal).
"""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from condor.options import Direction, LegKind, OptionKind


class GreeksOut(BaseModel):
    delta: float
    gamma: float
    vega: float
    theta: float
    rho: float


class PriceInput(BaseModel):
    spot: float = Field(gt=0)
    strike: float = Field(gt=0)
    time_to_expiry: float = Field(gt=0, description="Years to expiry.")
    rate: float = 0.0
    volatility: float = Field(gt=0)
    kind: OptionKind
    dividend_yield: float = 0.0


class PriceOut(BaseModel):
    price: float
    greeks: GreeksOut


class ImpliedVolInput(BaseModel):
    price: float = Field(gt=0, description="Observed option price to invert.")
    spot: float = Field(gt=0)
    strike: float = Field(gt=0)
    time_to_expiry: float = Field(gt=0)
    rate: float = 0.0
    kind: OptionKind
    dividend_yield: float = 0.0


class ImpliedVolOut(BaseModel):
    implied_vol: float


class LegInput(BaseModel):
    kind: LegKind
    direction: Direction
    strike: float = Field(default=0.0, ge=0, description="Ignored for stock legs.")
    iv: float = Field(default=0.0, ge=0, description="Ignored for stock legs.")
    quantity: float = Field(default=1.0, gt=0)


class StrategyInput(BaseModel):
    legs: list[LegInput] = Field(min_length=1)
    spot: float = Field(gt=0)
    rate: float = 0.0
    time_to_expiry: float = Field(gt=0)
    dividend_yield: float = 0.0


class LegResultOut(BaseModel):
    premium: float
    greeks: GreeksOut


class PayoffPoint(BaseModel):
    spot: float
    pnl: float


class StrategyOut(BaseModel):
    legs: list[LegResultOut]
    net_premium: float
    theoretical_value: float
    aggregate: GreeksOut
    payoff: list[PayoffPoint]
    breakevens: list[float]
    max_profit: float
    max_loss: float
    max_profit_unbounded: bool
    max_loss_unbounded: bool


class SavedStrategyIn(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    definition: StrategyInput


class SavedStrategyOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    definition: StrategyInput
    created_at: datetime
