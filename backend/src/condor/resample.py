"""Resample 1-minute candles into higher timeframes on read.

The DB stores a single 1m resolution; ``5m / 1h / 1d`` are derived here so there
is exactly one write path. Pure function — the resampling math is unit-tested
(``tests/test_resample.py``).
"""

from __future__ import annotations

from condor.marketdata.types import Candle

# Supported read intervals → minutes per bar.
INTERVAL_MINUTES: dict[str, int] = {
    "1m": 1,
    "5m": 5,
    "1h": 60,
    "1d": 1440,
}


def _bucket_epoch_minute(candle: Candle, minutes: int) -> int:
    """Floor a candle's start to the target bucket, in epoch-minutes.

    Flooring against the Unix epoch (itself UTC midnight) means 1h bars align to
    the hour and 1d bars align to UTC midnight for free.
    """
    epoch_minute = int(candle.bucket_start.timestamp()) // 60
    return (epoch_minute // minutes) * minutes


def resample(candles: list[Candle], interval: str) -> list[Candle]:
    """Aggregate ascending, contiguous 1m ``candles`` into ``interval`` bars.

    Input must be sorted ascending by ``bucket_start`` and single-symbol. Gaps
    are fine — a bucket is emitted from whatever 1m bars it contains.
    """
    if interval not in INTERVAL_MINUTES:
        raise ValueError(f"unsupported interval: {interval!r}")
    minutes = INTERVAL_MINUTES[interval]
    if minutes == 1 or not candles:
        return list(candles)

    from datetime import UTC, datetime

    out: list[Candle] = []
    cur_key: int | None = None
    for c in candles:
        key = _bucket_epoch_minute(c, minutes)
        if key != cur_key:
            out.append(
                Candle(
                    bucket_start=datetime.fromtimestamp(key * 60, tz=UTC),
                    open=c.open,
                    high=c.high,
                    low=c.low,
                    close=c.close,
                    volume=c.volume,
                    trade_count=c.trade_count,
                )
            )
            cur_key = key
        else:
            agg = out[-1]
            out[-1] = Candle(
                bucket_start=agg.bucket_start,
                open=agg.open,
                high=max(agg.high, c.high),
                low=min(agg.low, c.low),
                close=c.close,
                volume=agg.volume + c.volume,
                trade_count=agg.trade_count + c.trade_count,
            )
    return out
