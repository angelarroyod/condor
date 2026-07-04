"""The provider seam.

Everything downstream (aggregator, worker, API) consumes ``Tick``/``Candle`` and
never touches a vendor SDK. Adding a real-time equities provider later means
implementing this Protocol — no changes to the engine or UI.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Protocol, runtime_checkable

from condor.marketdata.types import Tick


@runtime_checkable
class MarketDataProvider(Protocol):
    """Streams normalized trades for a set of symbols."""

    name: str

    def stream_trades(self, symbols: list[str]) -> AsyncIterator[Tick]:
        """Yield normalized ticks until cancelled. Implementations own reconnects."""
        ...
