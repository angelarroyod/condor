"""Portfolio risk metrics from a daily equity curve.

Pure functions over a list of daily equity values. Deliberately stdlib-only
(``statistics`` + ``math``): the stack reserves numpy/scipy for pricing math, and
these statistics are simple enough not to need it — which keeps the tested
surface dependency-free.

Assumptions (documented, not hidden):
- Returns are simple daily returns ``rₜ = Eₜ/Eₜ₋₁ − 1`` on the daily-resampled
  equity curve (last snapshot per UTC day).
- Annualization uses ``TRADING_DAYS = 252``.
- Volatility is the sample standard deviation of daily returns × √252.
- Sharpe = (annualized mean return − risk-free rate) / annualized volatility,
  with the risk-free rate quoted per year.
- VaR is 1-day **historical** (non-parametric) at the given confidence, reported
  as a positive loss fraction.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from statistics import fmean, stdev

TRADING_DAYS = 252


@dataclass(frozen=True, slots=True)
class PortfolioMetrics:
    annualized_vol: float
    sharpe: float
    max_drawdown: float  # negative fraction (e.g. -0.23 = −23% peak-to-trough)
    var_95: float  # positive loss fraction at 95% confidence


def daily_returns(equity: list[float]) -> list[float]:
    return [equity[i] / equity[i - 1] - 1.0 for i in range(1, len(equity)) if equity[i - 1] != 0]


def annualized_volatility(returns: list[float]) -> float:
    if len(returns) < 2:
        return 0.0
    return stdev(returns) * math.sqrt(TRADING_DAYS)


def sharpe_ratio(returns: list[float], risk_free_rate: float = 0.0) -> float:
    if len(returns) < 2:
        return 0.0
    vol = annualized_volatility(returns)
    if vol == 0.0:
        return 0.0
    annualized_return = fmean(returns) * TRADING_DAYS
    return (annualized_return - risk_free_rate) / vol


def max_drawdown(equity: list[float]) -> float:
    """Largest peak-to-trough decline as a negative fraction (0.0 if none)."""
    peak = -math.inf
    worst = 0.0
    for value in equity:
        peak = max(peak, value)
        if peak > 0:
            worst = min(worst, value / peak - 1.0)
    return worst


def _percentile(sorted_values: list[float], pct: float) -> float:
    """Linear-interpolated percentile (numpy's default 'linear' method)."""
    if not sorted_values:
        return 0.0
    if len(sorted_values) == 1:
        return sorted_values[0]
    rank = (pct / 100.0) * (len(sorted_values) - 1)
    lo = math.floor(rank)
    hi = math.ceil(rank)
    frac = rank - lo
    return sorted_values[lo] + (sorted_values[hi] - sorted_values[lo]) * frac


def historical_var(returns: list[float], confidence: float = 0.95) -> float:
    """1-day historical VaR as a positive loss fraction (0.0 if no downside)."""
    if not returns:
        return 0.0
    tail = _percentile(sorted(returns), (1.0 - confidence) * 100.0)
    return max(0.0, -tail)


def compute_metrics(equity: list[float], risk_free_rate: float = 0.0) -> PortfolioMetrics | None:
    """All metrics from a daily equity curve, or None if too short."""
    returns = daily_returns(equity)
    if len(returns) < 2:
        return None
    return PortfolioMetrics(
        annualized_vol=annualized_volatility(returns),
        sharpe=sharpe_ratio(returns, risk_free_rate),
        max_drawdown=max_drawdown(equity),
        var_95=historical_var(returns, 0.95),
    )
