"""Implied volatility solver: Newton-Raphson with a bisection fallback.

Newton is fast when vega is healthy; it steps from a seed of 0.2 (20% vol). If a
step leaves the ``[VOL_MIN, VOL_MAX]`` bracket or vega collapses, we fall back to
bisection, which is slower but guaranteed to converge inside the bracket. Prices
outside the no-arbitrage bounds have no implied vol and raise ``ValueError``.
"""

from __future__ import annotations

import math

from condor.options import OptionKind
from condor.options.black_scholes import _d1_d2, price

VOL_MIN = 1e-6
VOL_MAX = 5.0
_MAX_ITER = 100
_TOL = 1e-8


def _vega(S: float, K: float, T: float, r: float, sigma: float, q: float) -> float:
    from scipy.stats import norm

    d1, _ = _d1_d2(S, K, T, r, sigma, q)
    return float(S * math.exp(-q * T) * norm.pdf(d1) * math.sqrt(T))


def _no_arb_bounds(
    S: float, K: float, T: float, r: float, q: float, kind: OptionKind
) -> tuple[float, float]:
    disc_S = S * math.exp(-q * T)
    disc_K = K * math.exp(-r * T)
    if kind == OptionKind.CALL:
        return max(disc_S - disc_K, 0.0), disc_S
    return max(disc_K - disc_S, 0.0), disc_K


def implied_vol(
    target: float,
    S: float,
    K: float,
    T: float,
    r: float,
    kind: OptionKind,
    q: float = 0.0,
) -> float:
    """Volatility that reprices ``kind`` to ``target``. Raises if unattainable."""
    if T <= 0.0:
        raise ValueError("implied vol undefined for non-positive time to expiry")
    lo_price, hi_price = _no_arb_bounds(S, K, T, r, q, kind)
    if target < lo_price - _TOL or target > hi_price + _TOL:
        raise ValueError(f"price {target} outside no-arbitrage bounds [{lo_price}, {hi_price}]")

    sigma = 0.2
    for _ in range(_MAX_ITER):
        diff = price(S, K, T, r, sigma, kind, q) - target
        if abs(diff) < _TOL:
            return sigma
        v = _vega(S, K, T, r, sigma, q)
        if v < 1e-8:
            break  # vega too small — hand off to bisection
        step = diff / v
        sigma -= step
        if not (VOL_MIN < sigma < VOL_MAX):
            break  # left the bracket — hand off to bisection

    # Bisection fallback over the full bracket.
    lo, hi = VOL_MIN, VOL_MAX
    for _ in range(_MAX_ITER):
        mid = 0.5 * (lo + hi)
        diff = price(S, K, T, r, mid, kind, q) - target
        if abs(diff) < _TOL:
            return mid
        if diff > 0:
            hi = mid
        else:
            lo = mid
    return 0.5 * (lo + hi)
