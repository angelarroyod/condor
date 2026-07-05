"""Implied-vol solver tests: round-trip recovery, bisection fallback, arb bounds."""

from __future__ import annotations

import pytest

from condor.options import OptionKind
from condor.options.black_scholes import price
from condor.options.implied_vol import implied_vol


@pytest.mark.parametrize("kind", [OptionKind.CALL, OptionKind.PUT])
@pytest.mark.parametrize("sigma", [0.1, 0.25, 0.6, 1.2])
def test_round_trip_recovers_sigma(kind: OptionKind, sigma: float) -> None:
    S, K, T, r = 100.0, 105.0, 0.5, 0.03
    target = price(S, K, T, r, sigma, kind)
    recovered = implied_vol(target, S, K, T, r, kind)
    assert abs(recovered - sigma) < 1e-6
    # And it reprices.
    assert abs(price(S, K, T, r, recovered, kind) - target) < 1e-8


def test_deep_otm_uses_fallback_but_reprices() -> None:
    # Deep OTM: tiny vega, likely to trip Newton into the bisection branch.
    S, K, T, r, sigma = 100.0, 300.0, 0.25, 0.03, 0.8
    target = price(S, K, T, r, sigma, OptionKind.CALL)
    recovered = implied_vol(target, S, K, T, r, OptionKind.CALL)
    assert abs(price(S, K, T, r, recovered, OptionKind.CALL) - target) < 1e-6


def test_price_above_upper_bound_raises() -> None:
    with pytest.raises(ValueError, match="no-arbitrage"):
        implied_vol(150.0, 100.0, 100.0, 1.0, 0.05, OptionKind.CALL)  # > spot


def test_non_positive_expiry_raises() -> None:
    with pytest.raises(ValueError, match="time to expiry"):
        implied_vol(5.0, 100.0, 100.0, 0.0, 0.05, OptionKind.CALL)
