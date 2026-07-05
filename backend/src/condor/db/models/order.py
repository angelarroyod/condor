"""Orders — market/limit, with an idempotency key for safe placement retries."""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
    UniqueConstraint,
    Uuid,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from condor.db.base import Base

_QTY = Numeric(30, 8)
_PRICE = Numeric(20, 8)


class Order(Base):
    __tablename__ = "orders"
    __table_args__ = (
        UniqueConstraint("account_id", "idempotency_key", name="uq_orders_idempotency"),
        # Matcher scans pending limits per symbol; blotter lists per account+status.
        Index("ix_orders_symbol_status", "symbol_id", "status"),
        Index("ix_orders_account_status", "account_id", "status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    account_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("accounts.id", ondelete="CASCADE"), index=True
    )
    symbol_id: Mapped[int] = mapped_column(ForeignKey("symbols.id", ondelete="CASCADE"))
    idempotency_key: Mapped[str] = mapped_column(String(64))

    side: Mapped[str] = mapped_column(String(8))
    type: Mapped[str] = mapped_column(String(8))
    limit_price: Mapped[Decimal | None] = mapped_column(_PRICE, nullable=True)
    quantity: Mapped[Decimal] = mapped_column(_QTY)
    filled_quantity: Mapped[Decimal] = mapped_column(_QTY, default=Decimal(0), server_default="0")
    avg_fill_price: Mapped[Decimal | None] = mapped_column(_PRICE, nullable=True)

    status: Mapped[str] = mapped_column(String(16), default="pending", server_default="pending")
    reject_reason: Mapped[str | None] = mapped_column(String(128), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    filled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
