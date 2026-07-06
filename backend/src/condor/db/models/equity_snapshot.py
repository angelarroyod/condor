"""Periodic account equity snapshots — the source for the equity curve and the
daily-return risk metrics."""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from condor.db.base import Base


class EquitySnapshot(Base):
    __tablename__ = "equity_snapshots"

    account_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("accounts.id", ondelete="CASCADE"), primary_key=True
    )
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), primary_key=True)
    equity: Mapped[Decimal] = mapped_column(Numeric(30, 8))
    cash: Mapped[Decimal] = mapped_column(Numeric(30, 8))
