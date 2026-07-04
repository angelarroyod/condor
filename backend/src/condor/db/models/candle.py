"""1-minute OHLCV time series.

Only the 1m base resolution is stored; higher timeframes are resampled on read
(``condor.resample``). The composite PK ``(symbol_id, bucket_start)`` is also the
index for the sole query shape — a per-symbol time-range scan — and gives the
worker a natural upsert target for the in-progress minute.

Prices/volume are ``NUMERIC``, never float: this data becomes fill prices and
P&L downstream.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from condor.db.base import Base

_PRICE = Numeric(20, 8)
_VOLUME = Numeric(30, 8)


class Candle(Base):
    __tablename__ = "candles"

    symbol_id: Mapped[int] = mapped_column(
        ForeignKey("symbols.id", ondelete="CASCADE"), primary_key=True
    )
    bucket_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), primary_key=True)
    open: Mapped[Decimal] = mapped_column(_PRICE)
    high: Mapped[Decimal] = mapped_column(_PRICE)
    low: Mapped[Decimal] = mapped_column(_PRICE)
    close: Mapped[Decimal] = mapped_column(_PRICE)
    volume: Mapped[Decimal] = mapped_column(_VOLUME)
    trade_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
