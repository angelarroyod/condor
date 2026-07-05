"""European options analytics: Black-Scholes-Merton pricing, Greeks, implied vol,
and multi-leg strategy payoffs. Pure math — floats are fine here (this is the
analytical pricing path, not an accounting path)."""

from enum import StrEnum


class OptionKind(StrEnum):
    CALL = "call"
    PUT = "put"


class LegKind(StrEnum):
    """A strategy leg — an option or the underlying (for covered calls etc.)."""

    CALL = "call"
    PUT = "put"
    STOCK = "stock"


class Direction(StrEnum):
    LONG = "long"
    SHORT = "short"
