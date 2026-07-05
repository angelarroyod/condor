"""Black-Scholes-Merton pricing and Greeks for European options.

Includes a continuous dividend yield ``q`` (``q=0`` recovers plain Black-Scholes;
crypto uses 0, equities can pass a yield). Conventions:
- ``vega`` is per 1.00 (100%) change in volatility.
- ``theta`` and ``rho`` are per 1.00 of their variable, annualized (per year /
  per 1.00 rate). The frontend divides theta by 365 for a per-day figure.

Degenerate inputs (``T<=0`` or ``sigma<=0``) return the discounted intrinsic
value so the IV solver and payoff code never divide by zero.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from scipy.stats import norm

from condor.options import OptionKind


@dataclass(frozen=True, slots=True)
class Greeks:
    delta: float
    gamma: float
    vega: float
    theta: float
    rho: float


def _d1_d2(S: float, K: float, T: float, r: float, sigma: float, q: float) -> tuple[float, float]:
    d1 = (math.log(S / K) + (r - q + 0.5 * sigma * sigma) * T) / (sigma * math.sqrt(T))
    return d1, d1 - sigma * math.sqrt(T)


def _intrinsic(S: float, K: float, kind: OptionKind) -> float:
    return max(S - K, 0.0) if kind == OptionKind.CALL else max(K - S, 0.0)


def price(
    S: float, K: float, T: float, r: float, sigma: float, kind: OptionKind, q: float = 0.0
) -> float:
    """Theoretical BSM price of a European option."""
    if T <= 0.0 or sigma <= 0.0:
        return _intrinsic(S, K, kind)
    d1, d2 = _d1_d2(S, K, T, r, sigma, q)
    disc_S = S * math.exp(-q * T)
    disc_K = K * math.exp(-r * T)
    if kind == OptionKind.CALL:
        return float(disc_S * norm.cdf(d1) - disc_K * norm.cdf(d2))
    return float(disc_K * norm.cdf(-d2) - disc_S * norm.cdf(-d1))


def greeks(
    S: float, K: float, T: float, r: float, sigma: float, kind: OptionKind, q: float = 0.0
) -> Greeks:
    """Analytic Greeks. Returns zeros for degenerate inputs."""
    if T <= 0.0 or sigma <= 0.0:
        return Greeks(0.0, 0.0, 0.0, 0.0, 0.0)

    d1, d2 = _d1_d2(S, K, T, r, sigma, q)
    sqrt_t = math.sqrt(T)
    pdf_d1 = float(norm.pdf(d1))
    disc_q = math.exp(-q * T)
    disc_r = math.exp(-r * T)

    gamma = disc_q * pdf_d1 / (S * sigma * sqrt_t)
    vega = S * disc_q * pdf_d1 * sqrt_t
    theta_term = -(S * disc_q * pdf_d1 * sigma) / (2.0 * sqrt_t)

    if kind == OptionKind.CALL:
        delta = disc_q * float(norm.cdf(d1))
        theta = theta_term - r * K * disc_r * float(norm.cdf(d2)) + q * S * disc_q * float(
            norm.cdf(d1)
        )
        rho = K * T * disc_r * float(norm.cdf(d2))
    else:
        delta = -disc_q * float(norm.cdf(-d1))
        theta = theta_term + r * K * disc_r * float(norm.cdf(-d2)) - q * S * disc_q * float(
            norm.cdf(-d1)
        )
        rho = -K * T * disc_r * float(norm.cdf(-d2))

    return Greeks(delta=delta, gamma=gamma, vega=vega, theta=theta, rho=rho)
