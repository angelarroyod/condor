"""Open positions — one row per (account, symbol). Signed quantity: +long/-short.

Unrealized P&L is never stored; it is computed on read from the latest price.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column

from condor.db.base import Base


class Position(Base):
    __tablename__ = "positions"

    account_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("accounts.id", ondelete="CASCADE"), primary_key=True
    )
    symbol_id: Mapped[int] = mapped_column(
        ForeignKey("symbols.id", ondelete="CASCADE"), primary_key=True
    )
    quantity: Mapped[Decimal] = mapped_column(Numeric(30, 8), default=Decimal(0))
    avg_price: Mapped[Decimal] = mapped_column(Numeric(20, 8), default=Decimal(0))
    realized_pnl: Mapped[Decimal] = mapped_column(
        Numeric(30, 8), default=Decimal(0), server_default="0"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
