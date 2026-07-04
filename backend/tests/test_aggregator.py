"""Unit tests for the 1-minute candle aggregator (pure math)."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

from condor.ingest.aggregator import CandleAggregator, fold_tick, minute_bucket
from condor.marketdata.types import Tick


def _tick(sec: int, price: str, qty: str = "1") -> Tick:
    return Tick(
        symbol="BTCUSDT",
        price=Decimal(price),
        quantity=Decimal(qty),
        ts=datetime(2026, 1, 1, 12, 0, sec, tzinfo=UTC),
    )


def test_minute_bucket_floors_to_minute() -> None:
    ts = datetime(2026, 1, 1, 12, 34, 56, 789, tzinfo=UTC)
    assert minute_bucket(ts) == datetime(2026, 1, 1, 12, 34, 0, tzinfo=UTC)


def test_fold_builds_ohlcv() -> None:
    c = None
    for t in [_tick(0, "100", "1"), _tick(10, "105", "2"), _tick(20, "98", "3")]:
        c = fold_tick(c, t)
    assert c is not None
    assert (c.open, c.high, c.low, c.close) == (
        Decimal("100"),
        Decimal("105"),
        Decimal("98"),
        Decimal("98"),
    )
    assert c.volume == Decimal("6")
    assert c.trade_count == 3


def test_push_emits_closed_candle_on_rollover() -> None:
    agg = CandleAggregator()
    assert agg.push(_tick(10, "100")) is None  # opens minute 12:00
    assert agg.push(_tick(50, "110")) is None  # still 12:00

    # A tick in 12:01 closes the 12:00 bar and returns it.
    closed = agg.push(
        Tick("BTCUSDT", Decimal("120"), Decimal("1"), datetime(2026, 1, 1, 12, 1, 5, tzinfo=UTC))
    )
    assert closed is not None
    assert closed.bucket_start == datetime(2026, 1, 1, 12, 0, tzinfo=UTC)
    assert closed.close == Decimal("110")
    # The new running bar is the 12:01 minute.
    assert agg.current is not None
    assert agg.current.bucket_start == datetime(2026, 1, 1, 12, 1, tzinfo=UTC)
    assert agg.current.open == Decimal("120")


def test_out_of_order_tick_is_dropped() -> None:
    agg = CandleAggregator()
    agg.push(
        Tick("BTCUSDT", Decimal("100"), Decimal("1"), datetime(2026, 1, 1, 12, 5, 0, tzinfo=UTC))
    )
    stale = agg.push(_tick(30, "999"))  # 12:00 — earlier than the open 12:05 bar
    assert stale is None
    assert agg.current is not None
    assert agg.current.bucket_start == datetime(2026, 1, 1, 12, 5, tzinfo=UTC)
    assert agg.current.close == Decimal("100")  # untouched by the stale tick
