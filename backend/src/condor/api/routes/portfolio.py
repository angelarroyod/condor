"""Portfolio & risk endpoints: equity curve, allocation, risk metrics."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from condor.analytics.risk import compute_metrics
from condor.api.deps import get_redis
from condor.api.routes.trading import get_demo_account
from condor.config import get_settings
from condor.db.base import get_session
from condor.db.models import Account, EquitySnapshot
from condor.portfolio import allocation, to_daily_equity
from condor.schemas.portfolio import AllocationOut, EquityPoint, MetricsOut

router = APIRouter(prefix="/api/portfolio", tags=["portfolio"])


@router.get("/equity", response_model=list[EquityPoint])
async def equity_curve(
    session: AsyncSession = Depends(get_session),
    account: Account = Depends(get_demo_account),
) -> list[EquitySnapshot]:
    stmt = (
        select(EquitySnapshot)
        .where(EquitySnapshot.account_id == account.id)
        .order_by(EquitySnapshot.ts)
        .limit(5000)
    )
    return list(await session.scalars(stmt))


@router.get("/allocation", response_model=list[AllocationOut])
async def portfolio_allocation(
    session: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis),
    account: Account = Depends(get_demo_account),
) -> list[AllocationOut]:
    entries = await allocation(session, redis, account)
    return [
        AllocationOut(symbol=a.symbol, market_value=a.market_value, weight=a.weight)
        for a in entries
    ]


@router.get("/metrics", response_model=MetricsOut | None)
async def risk_metrics(
    session: AsyncSession = Depends(get_session),
    account: Account = Depends(get_demo_account),
) -> MetricsOut | None:
    snapshots = list(
        await session.scalars(
            select(EquitySnapshot)
            .where(EquitySnapshot.account_id == account.id)
            .order_by(EquitySnapshot.ts)
        )
    )
    metrics = compute_metrics(to_daily_equity(snapshots), get_settings().risk_free_rate)
    if metrics is None:
        return None
    return MetricsOut(
        annualized_vol=metrics.annualized_vol,
        sharpe=metrics.sharpe,
        max_drawdown=metrics.max_drawdown,
        var_95=metrics.var_95,
    )
