"""Average-cost position engine — pure, Decimal-exact, long **and** short.

``quantity`` is signed: positive = long, negative = short. Realized P&L only
crystallizes when a trade *reduces* the open position; adding merely re-averages
the entry. A trade larger than the open size *flips* the position: the whole
existing lot is closed (and realized) and a fresh lot opens at the fill price.

This module has zero I/O so the money math is exhaustively unit-tested. The DB
fill service maps a ``positions`` row to/from ``PositionState``.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class PositionState:
    quantity: Decimal = Decimal(0)  # signed
    avg_price: Decimal = Decimal(0)  # entry avg of the open quantity
    realized_pnl: Decimal = Decimal(0)  # cumulative


def _signed(side: str, quantity: Decimal) -> Decimal:
    if side == "buy":
        return quantity
    if side == "sell":
        return -quantity
    raise ValueError(f"invalid side: {side!r}")


def apply_fill(
    state: PositionState, side: str, quantity: Decimal, price: Decimal
) -> tuple[PositionState, Decimal]:
    """Apply a fill to ``state``; return ``(new_state, realized_delta)``.

    ``quantity`` is the (unsigned) filled size; ``side`` gives its direction.
    """
    if quantity <= 0:
        raise ValueError("fill quantity must be positive")

    q = state.quantity  # current signed size
    d = _signed(side, quantity)  # signed delta

    # Opening from flat.
    if q == 0:
        new = PositionState(d, price, state.realized_pnl)
        return new, Decimal(0)

    # Same direction — re-average, nothing realized.
    if (q > 0) == (d > 0):
        new_qty = q + d
        new_avg = (q * state.avg_price + d * price) / new_qty
        return PositionState(new_qty, new_avg, state.realized_pnl), Decimal(0)

    # Opposite direction — reduce, close, or flip.
    closing = min(abs(q), abs(d))
    sign = Decimal(1) if q > 0 else Decimal(-1)
    realized = closing * (price - state.avg_price) * sign
    new_qty = q + d

    if new_qty == 0:  # exact close
        new_avg = Decimal(0)
    elif (new_qty > 0) == (q > 0):  # partial reduce, same side remains
        new_avg = state.avg_price
    else:  # flipped past zero — remainder opens fresh at fill price
        new_avg = price

    return PositionState(new_qty, new_avg, state.realized_pnl + realized), realized
