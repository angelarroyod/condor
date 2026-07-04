"""GET /api/symbols — tradable instruments."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from condor.db.base import get_session
from condor.db.models import Symbol
from condor.schemas.market import SymbolOut

router = APIRouter(prefix="/api/symbols", tags=["symbols"])


@router.get("", response_model=list[SymbolOut])
async def list_symbols(session: AsyncSession = Depends(get_session)) -> list[Symbol]:
    result = await session.scalars(
        select(Symbol).where(Symbol.is_active.is_(True)).order_by(Symbol.symbol)
    )
    return list(result)
