"""Unit tests for 1m -> higher-timeframe resampling (pure math)."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest

from condor.marketdata.types import Candle
from condor.resample import resample


def _minute_series(n: int, start_price: int = 100) -> list[Candle]:
    """n contiguous 1m candles starting 2026-01-01 00:00 UTC; close = open+1."""
    base = datetime(2026, 1, 1, 0, 0, tzinfo=UTC)
    out = []
    for i in range(n):
        p = Decimal(start_price + i)
        out.append(
            Candle(
                bucket_start=base + timedelta(minutes=i),
                open=p,
                high=p + Decimal("2"),
                low=p - Decimal("1"),
                close=p + Decimal("1"),
                volume=Decimal("10"),
                trade_count=5,
            )
        )
    return out


def test_1m_is_passthrough() -> None:
    series = _minute_series(3)
    assert resample(series, "1m") == series


def test_empty_input() -> None:
    assert resample([], "5m") == []


def test_unsupported_interval_raises() -> None:
    with pytest.raises(ValueError, match="unsupported interval"):
        resample(_minute_series(1), "7m")


def test_5m_aggregates_five_bars() -> None:
    out = resample(_minute_series(5), "5m")
    assert len(out) == 1
    bar = out[0]
    assert bar.bucket_start == datetime(2026, 1, 1, 0, 0, tzinfo=UTC)
    assert bar.open == Decimal("100")  # first open
    assert bar.close == Decimal("105")  # last close (104 + 1)
    assert bar.high == Decimal("106")  # max high = 104 + 2
    assert bar.low == Decimal("99")  # min low = 100 - 1
    assert bar.volume == Decimal("50")  # 5 * 10
    assert bar.trade_count == 25


def test_5m_splits_into_aligned_buckets() -> None:
    # 7 one-minute bars -> [00:00-00:04] and [00:05-00:06]
    out = resample(_minute_series(7), "5m")
    assert [b.bucket_start.minute for b in out] == [0, 5]
    assert out[0].trade_count == 25
    assert out[1].trade_count == 10  # 2 remaining bars


def test_1d_aligns_to_utc_midnight() -> None:
    # A bar late in the day must still land in the 00:00 daily bucket.
    late = Candle(
        bucket_start=datetime(2026, 1, 1, 23, 59, tzinfo=UTC),
        open=Decimal("1"),
        high=Decimal("1"),
        low=Decimal("1"),
        close=Decimal("1"),
        volume=Decimal("1"),
        trade_count=1,
    )
    out = resample([late], "1d")
    assert out[0].bucket_start == datetime(2026, 1, 1, 0, 0, tzinfo=UTC)
