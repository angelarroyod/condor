"""Fold a stream of trades into 1-minute OHLCV candles.

The math here is pure and deterministic — no clock, no I/O — so it is fully
covered by unit tests (``tests/test_aggregator.py``). The ingest worker owns the
side effects (persist the closed candle, publish the running one).
"""

from __future__ import annotations

from datetime import datetime

from condor.marketdata.types import Candle, Tick


def minute_bucket(ts: datetime) -> datetime:
    """Floor a timestamp to its minute boundary (its candle's ``bucket_start``)."""
    return ts.replace(second=0, microsecond=0)


def fold_tick(candle: Candle | None, tick: Tick) -> Candle:
    """Fold ``tick`` into the running candle for its minute.

    ``candle is None`` (or a tick in a fresh minute) opens a new bar seeded from
    the tick. Otherwise OHLC/volume/count are updated in place. Callers are
    responsible for detecting the minute rollover — see ``CandleAggregator``.
    """
    bucket = minute_bucket(tick.ts)
    if candle is None or candle.bucket_start != bucket:
        return Candle(
            bucket_start=bucket,
            open=tick.price,
            high=tick.price,
            low=tick.price,
            close=tick.price,
            volume=tick.quantity,
            trade_count=1,
        )
    return Candle(
        bucket_start=candle.bucket_start,
        open=candle.open,
        high=max(candle.high, tick.price),
        low=min(candle.low, tick.price),
        close=tick.price,
        volume=candle.volume + tick.quantity,
        trade_count=candle.trade_count + 1,
    )


class CandleAggregator:
    """Stateful per-symbol 1m aggregator.

    ``push`` returns the just-*closed* candle when a tick opens a new minute,
    otherwise ``None``. The still-forming candle is always available via
    ``current`` (published live; persisted as an upsert).
    """

    __slots__ = ("_current",)

    def __init__(self) -> None:
        self._current: Candle | None = None

    def push(self, tick: Tick) -> Candle | None:
        bucket = minute_bucket(tick.ts)
        closed: Candle | None = None
        if self._current is not None and bucket != self._current.bucket_start:
            if bucket < self._current.bucket_start:
                # ponytail: assumes a monotonic per-symbol trade stream (true for
                # Binance). An out-of-order tick is dropped rather than corrupting
                # a closed bar. Upgrade to a reorder buffer only if a provider
                # actually delivers unordered trades.
                return None
            closed = self._current
            self._current = None
        self._current = fold_tick(self._current, tick)
        return closed

    @property
    def current(self) -> Candle | None:
        return self._current
