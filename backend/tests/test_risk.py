"""Risk-metric tests against hand-computed values."""

from __future__ import annotations

import math

from condor.analytics.risk import (
    annualized_volatility,
    compute_metrics,
    daily_returns,
    historical_var,
    max_drawdown,
    sharpe_ratio,
)


def test_daily_returns() -> None:
    r = daily_returns([100.0, 110.0, 99.0])
    assert len(r) == 2
    assert abs(r[0] - 0.1) < 1e-12
    assert abs(r[1] - (-0.1)) < 1e-12


def test_flat_equity_is_all_zero() -> None:
    eq = [100.0, 100.0, 100.0, 100.0]
    r = daily_returns(eq)
    assert annualized_volatility(r) == 0.0
    assert sharpe_ratio(r) == 0.0
    assert max_drawdown(eq) == 0.0
    assert historical_var(r) == 0.0


def test_max_drawdown() -> None:
    # Peak 120, trough 90 -> -25%.
    assert abs(max_drawdown([100.0, 120.0, 90.0, 110.0]) - (-0.25)) < 1e-12


def test_annualized_volatility_matches_formula() -> None:
    r = [0.01, -0.01, 0.01, -0.01]
    # sample stdev = sqrt(sum(sq)/(n-1)); mean 0 -> sqrt(0.0004/3).
    expected = math.sqrt(0.0004 / 3) * math.sqrt(252)
    assert abs(annualized_volatility(r) - expected) < 1e-12


def test_historical_var_linear_percentile() -> None:
    r = [-0.05, -0.02, 0.0, 0.01, 0.03]
    # 5th percentile: rank 0.2 between -0.05 and -0.02 -> -0.05 + 0.2*0.03 = -0.044.
    assert abs(historical_var(r, 0.95) - 0.044) < 1e-12


def test_sharpe_ratio() -> None:
    r = [0.02, 0.0, 0.01]  # mean 0.01, sample stdev 0.01
    vol = 0.01 * math.sqrt(252)
    expected = (0.01 * 252) / vol
    assert abs(sharpe_ratio(r, 0.0) - expected) < 1e-9


def test_compute_metrics_needs_two_returns() -> None:
    assert compute_metrics([100.0]) is None
    assert compute_metrics([100.0, 101.0]) is None  # only 1 return
    assert compute_metrics([100.0, 101.0, 102.0]) is not None
