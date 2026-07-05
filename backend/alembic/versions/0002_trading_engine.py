"""trading engine: accounts, orders, fills, positions

Revision ID: 0002
Revises: 0001
Create Date: 2026-07-04
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_QTY = sa.Numeric(30, 8)
_PRICE = sa.Numeric(20, 8)


def upgrade() -> None:
    op.create_table(
        "accounts",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("label", sa.String(length=64), nullable=False),
        sa.Column("cash_balance", sa.Numeric(30, 8), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "orders",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("account_id", sa.Uuid(), nullable=False),
        sa.Column("symbol_id", sa.SmallInteger(), nullable=False),
        sa.Column("idempotency_key", sa.String(length=64), nullable=False),
        sa.Column("side", sa.String(length=8), nullable=False),
        sa.Column("type", sa.String(length=8), nullable=False),
        sa.Column("limit_price", _PRICE, nullable=True),
        sa.Column("quantity", _QTY, nullable=False),
        sa.Column("filled_quantity", _QTY, server_default="0", nullable=False),
        sa.Column("avg_fill_price", _PRICE, nullable=True),
        sa.Column("status", sa.String(length=16), server_default="pending", nullable=False),
        sa.Column("reject_reason", sa.String(length=128), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("filled_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["account_id"], ["accounts.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["symbol_id"], ["symbols.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("account_id", "idempotency_key", name="uq_orders_idempotency"),
        sa.CheckConstraint("side IN ('buy','sell')", name="ck_orders_side"),
        sa.CheckConstraint("type IN ('market','limit')", name="ck_orders_type"),
        sa.CheckConstraint(
            "status IN ('pending','filled','cancelled','rejected')", name="ck_orders_status"
        ),
    )
    op.create_index("ix_orders_account_id", "orders", ["account_id"])
    op.create_index("ix_orders_symbol_status", "orders", ["symbol_id", "status"])
    op.create_index("ix_orders_account_status", "orders", ["account_id", "status"])

    op.create_table(
        "fills",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("order_id", sa.Uuid(), nullable=False),
        sa.Column("account_id", sa.Uuid(), nullable=False),
        sa.Column("symbol_id", sa.SmallInteger(), nullable=False),
        sa.Column("side", sa.String(length=8), nullable=False),
        sa.Column("price", _PRICE, nullable=False),
        sa.Column("quantity", _QTY, nullable=False),
        sa.Column("fee", _QTY, server_default="0", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["account_id"], ["accounts.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["symbol_id"], ["symbols.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_fills_account_created", "fills", ["account_id", "created_at"])

    op.create_table(
        "positions",
        sa.Column("account_id", sa.Uuid(), nullable=False),
        sa.Column("symbol_id", sa.SmallInteger(), nullable=False),
        sa.Column("quantity", _QTY, nullable=False),
        sa.Column("avg_price", _PRICE, nullable=False),
        sa.Column("realized_pnl", _QTY, server_default="0", nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["account_id"], ["accounts.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["symbol_id"], ["symbols.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("account_id", "symbol_id"),
    )


def downgrade() -> None:
    op.drop_table("positions")
    op.drop_index("ix_fills_account_created", table_name="fills")
    op.drop_table("fills")
    op.drop_index("ix_orders_account_status", table_name="orders")
    op.drop_index("ix_orders_symbol_status", table_name="orders")
    op.drop_index("ix_orders_account_id", table_name="orders")
    op.drop_table("orders")
    op.drop_table("accounts")
