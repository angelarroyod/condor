"""Multi-leg strategy analytics: aggregate Greeks, payoff-at-expiration,
breakevens, and max profit/loss.

All legs share one expiry ``T`` and market (spot ``S``, rate ``r``, yield ``q``);
each leg carries its own implied vol. Max profit/loss come from a numeric sweep
over a wide spot grid rather than per-template formulas, so arbitrary custom
legs work with a single code path; an unbounded tail (e.g. long call) is flagged
instead of reported as a grid-edge number.
"""

from __future__ import annotations

from dataclasses import dataclass

from scipy.optimize import brentq

from condor.options import Direction, LegKind, OptionKind
from condor.options.black_scholes import Greeks, greeks, price

_STOCK_GREEKS = Greeks(delta=1.0, gamma=0.0, vega=0.0, theta=0.0, rho=0.0)

_GRID_POINTS = 241
_GRID_SPAN = 3.0  # sweep spot from 0 to 3× max(spot, strikes)


@dataclass(frozen=True, slots=True)
class Leg:
    kind: LegKind
    direction: Direction
    strike: float  # ignored for STOCK legs
    iv: float  # ignored for STOCK legs
    quantity: float = 1.0


@dataclass(frozen=True, slots=True)
class LegResult:
    premium: float
    greeks: Greeks


@dataclass(frozen=True, slots=True)
class StrategyAnalysis:
    legs: list[LegResult]
    net_premium: float  # + debit paid / − credit received
    theoretical_value: float  # current mark value of the position
    aggregate: Greeks
    payoff: list[tuple[float, float]]  # (spot_at_expiry, pnl)
    breakevens: list[float]
    max_profit: float
    max_loss: float
    max_profit_unbounded: bool
    max_loss_unbounded: bool


def _sign(direction: Direction) -> float:
    return 1.0 if direction == Direction.LONG else -1.0


def _leg_value_at_expiry(spot: float, leg: Leg) -> float:
    """What one unit of the leg is worth at expiry ``spot`` (stock = spot)."""
    if leg.kind == LegKind.STOCK:
        return spot
    if leg.kind == LegKind.CALL:
        return max(spot - leg.strike, 0.0)
    return max(leg.strike - spot, 0.0)


def _leg_premium(leg: Leg, S: float, r: float, T: float, q: float) -> float:
    if leg.kind == LegKind.STOCK:
        return S
    return price(S, leg.strike, T, r, leg.iv, OptionKind(leg.kind.value), q)


def _leg_greeks(leg: Leg, S: float, r: float, T: float, q: float) -> Greeks:
    if leg.kind == LegKind.STOCK:
        return _STOCK_GREEKS
    return greeks(S, leg.strike, T, r, leg.iv, OptionKind(leg.kind.value), q)


def _payoff_at(legs: list[Leg], premiums: list[float], spot: float) -> float:
    total = 0.0
    for leg, premium in zip(legs, premiums, strict=True):
        value = _leg_value_at_expiry(spot, leg)
        total += _sign(leg.direction) * leg.quantity * (value - premium)
    return total


def _weighted(legs: list[Leg], leg_greeks: list[Greeks], attr: str) -> float:
    """Position-signed, quantity-weighted sum of one Greek across legs."""
    total = sum(
        _sign(leg.direction) * leg.quantity * getattr(g, attr)
        for leg, g in zip(legs, leg_greeks, strict=True)
    )
    return float(total)


def analyze(
    legs: list[Leg], S: float, r: float, T: float, q: float = 0.0
) -> StrategyAnalysis:
    if not legs:
        raise ValueError("strategy needs at least one leg")

    premiums = [_leg_premium(leg, S, r, T, q) for leg in legs]
    leg_greeks = [_leg_greeks(leg, S, r, T, q) for leg in legs]

    leg_results = [
        LegResult(premium=p, greeks=g) for p, g in zip(premiums, leg_greeks, strict=True)
    ]
    net_premium = sum(
        _sign(leg.direction) * leg.quantity * p for leg, p in zip(legs, premiums, strict=True)
    )

    aggregate = Greeks(
        delta=_weighted(legs, leg_greeks, "delta"),
        gamma=_weighted(legs, leg_greeks, "gamma"),
        vega=_weighted(legs, leg_greeks, "vega"),
        theta=_weighted(legs, leg_greeks, "theta"),
        rho=_weighted(legs, leg_greeks, "rho"),
    )

    # Payoff sweep over [0, span × max(spot, strikes)].
    hi = _GRID_SPAN * max(S, *(leg.strike for leg in legs))
    step = hi / (_GRID_POINTS - 1)
    grid = [i * step for i in range(_GRID_POINTS)]
    payoff = [(s, _payoff_at(legs, premiums, s)) for s in grid]

    breakevens = _breakevens(legs, premiums, grid)
    pnls = [p for _, p in payoff]
    max_profit = max(pnls)
    max_loss = min(pnls)
    argmax = pnls.index(max_profit)
    argmin = pnls.index(max_loss)
    last = _GRID_POINTS - 1
    profit_unbounded = argmax == last and pnls[last] > pnls[last - 1]
    loss_unbounded = argmin == last and pnls[last] < pnls[last - 1]

    return StrategyAnalysis(
        legs=leg_results,
        net_premium=net_premium,
        theoretical_value=net_premium,  # single market snapshot: mark == entry value
        aggregate=aggregate,
        payoff=payoff,
        breakevens=breakevens,
        max_profit=max_profit,
        max_loss=max_loss,
        max_profit_unbounded=profit_unbounded,
        max_loss_unbounded=loss_unbounded,
    )


def _breakevens(legs: list[Leg], premiums: list[float], grid: list[float]) -> list[float]:
    """Spots where total P&L crosses zero (sign-change scan + brentq refine)."""
    roots: list[float] = []

    def f(s: float) -> float:
        return _payoff_at(legs, premiums, s)

    for a, b in zip(grid, grid[1:], strict=False):  # intentional pairwise offset
        fa, fb = f(a), f(b)
        if fa == 0.0:
            roots.append(a)
        elif fa * fb < 0.0:
            roots.append(float(brentq(f, a, b)))
    # Dedup near-equal roots.
    unique: list[float] = []
    for x in sorted(roots):
        if not unique or abs(x - unique[-1]) > 1e-6:
            unique.append(x)
    return unique
