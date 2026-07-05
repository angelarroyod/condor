"""Black-Scholes-Merton pricing/Greeks tests, including textbook values,
put-call parity, and finite-difference cross-checks."""

from __future__ import annotations

import math

from condor.options import OptionKind
from condor.options.black_scholes import greeks, price


def test_textbook_atm_values() -> None:
    # Hull, S=K=100, T=1, r=5%, sigma=20%, no dividend.
    call = price(100, 100, 1.0, 0.05, 0.20, OptionKind.CALL)
    put = price(100, 100, 1.0, 0.05, 0.20, OptionKind.PUT)
    assert abs(call - 10.4506) < 1e-3
    assert abs(put - 5.5735) < 1e-3


def test_put_call_parity() -> None:
    S, K, T, r, sigma, q = 120.0, 100.0, 0.75, 0.03, 0.35, 0.02
    call = price(S, K, T, r, sigma, OptionKind.CALL, q)
    put = price(S, K, T, r, sigma, OptionKind.PUT, q)
    lhs = call - put
    rhs = S * math.exp(-q * T) - K * math.exp(-r * T)
    assert abs(lhs - rhs) < 1e-9


def test_greek_signs_and_bounds() -> None:
    c = greeks(100, 100, 1.0, 0.05, 0.2, OptionKind.CALL)
    p = greeks(100, 100, 1.0, 0.05, 0.2, OptionKind.PUT)
    assert 0.0 < c.delta < 1.0
    assert -1.0 < p.delta < 0.0
    assert c.gamma > 0.0 and c.vega > 0.0
    # Same-strike call/put share gamma and vega.
    assert abs(c.gamma - p.gamma) < 1e-12
    assert abs(c.vega - p.vega) < 1e-12


def test_delta_matches_finite_difference() -> None:
    S, K, T, r, sigma = 105.0, 100.0, 0.5, 0.04, 0.25
    h = 1e-4
    up = price(S + h, K, T, r, sigma, OptionKind.CALL)
    dn = price(S - h, K, T, r, sigma, OptionKind.CALL)
    numeric_delta = (up - dn) / (2 * h)
    assert abs(greeks(S, K, T, r, sigma, OptionKind.CALL).delta - numeric_delta) < 1e-5


def test_vega_matches_finite_difference() -> None:
    S, K, T, r, sigma = 105.0, 100.0, 0.5, 0.04, 0.25
    h = 1e-5
    up = price(S, K, T, r, sigma + h, OptionKind.CALL)
    dn = price(S, K, T, r, sigma - h, OptionKind.CALL)
    numeric_vega = (up - dn) / (2 * h)
    assert abs(greeks(S, K, T, r, sigma, OptionKind.CALL).vega - numeric_vega) < 1e-4


def test_degenerate_inputs_return_intrinsic() -> None:
    assert price(120, 100, 0.0, 0.05, 0.2, OptionKind.CALL) == 20.0
    assert price(80, 100, 1.0, 0.05, 0.0, OptionKind.PUT) == 20.0
