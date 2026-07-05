"""Stateless options analytics endpoints: price, implied vol, strategy payoff."""

from __future__ import annotations

from dataclasses import asdict

from fastapi import APIRouter

from condor.api.errors import AppError
from condor.options.black_scholes import greeks, price
from condor.options.implied_vol import implied_vol
from condor.options.strategy import Leg, analyze
from condor.schemas.options import (
    GreeksOut,
    ImpliedVolInput,
    ImpliedVolOut,
    LegResultOut,
    PayoffPoint,
    PriceInput,
    PriceOut,
    StrategyInput,
    StrategyOut,
)

router = APIRouter(prefix="/api/options", tags=["options"])


@router.post("/price", response_model=PriceOut)
async def option_price(data: PriceInput) -> PriceOut:
    g = greeks(
        data.spot, data.strike, data.time_to_expiry, data.rate, data.volatility, data.kind,
        data.dividend_yield,
    )
    p = price(
        data.spot, data.strike, data.time_to_expiry, data.rate, data.volatility, data.kind,
        data.dividend_yield,
    )
    return PriceOut(price=p, greeks=GreeksOut(**asdict(g)))


@router.post("/implied-vol", response_model=ImpliedVolOut)
async def option_implied_vol(data: ImpliedVolInput) -> ImpliedVolOut:
    try:
        iv = implied_vol(
            data.price, data.spot, data.strike, data.time_to_expiry, data.rate, data.kind,
            data.dividend_yield,
        )
    except ValueError as exc:
        raise AppError(str(exc), code="iv_unsolvable", status_code=422) from exc
    return ImpliedVolOut(implied_vol=iv)


@router.post("/strategy", response_model=StrategyOut)
async def option_strategy(data: StrategyInput) -> StrategyOut:
    legs = [Leg(leg.kind, leg.direction, leg.strike, leg.iv, leg.quantity) for leg in data.legs]
    a = analyze(legs, data.spot, data.rate, data.time_to_expiry, data.dividend_yield)
    return StrategyOut(
        legs=[
            LegResultOut(premium=r.premium, greeks=GreeksOut(**asdict(r.greeks))) for r in a.legs
        ],
        net_premium=a.net_premium,
        theoretical_value=a.theoretical_value,
        aggregate=GreeksOut(**asdict(a.aggregate)),
        payoff=[PayoffPoint(spot=s, pnl=pnl) for s, pnl in a.payoff],
        breakevens=a.breakevens,
        max_profit=a.max_profit,
        max_loss=a.max_loss,
        max_profit_unbounded=a.max_profit_unbounded,
        max_loss_unbounded=a.max_loss_unbounded,
    )
