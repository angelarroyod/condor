"""Execution price mechanics — pure, Decimal-exact.

Slippage models the price you actually get versus the quoted mid: a buy pays up,
a sell receives less. Kept separate from the DB fill service so it is unit-tested
in isolation.
"""

from __future__ import annotations

from decimal import Decimal

_BPS = Decimal("10000")


def apply_slippage(price: Decimal, side: str, slippage_bps: Decimal) -> Decimal:
    """Adverse-fill price for ``side`` given ``slippage_bps`` basis points."""
    factor = slippage_bps / _BPS
    if side == "buy":
        return price * (Decimal(1) + factor)
    if side == "sell":
        return price * (Decimal(1) - factor)
    raise ValueError(f"invalid side: {side!r}")


def notional(price: Decimal, quantity: Decimal) -> Decimal:
    """Trade value in quote currency."""
    return price * quantity
