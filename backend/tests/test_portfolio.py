"""DB-backed portfolio service tests (equity + allocation). Require Postgres."""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from tests.conftest import requires_db

from condor.db.models import Account, Position, Symbol
from condor.portfolio import allocation, compute_equity

pytestmark = requires_db

D = Decimal


class FakeRedis:
    """No cached quote -> marks fall back to average cost."""

    async def get(self, _key: str) -> None:
        return None


async def _seed(factory: async_sessionmaker[AsyncSession]) -> Account:
    async with factory() as s:
        account = Account(label="demo", cash_balance=D("100000"))
        symbol = Symbol(symbol="BTCUSDT", name="Bitcoin", asset_class="crypto", provider="binance")
        s.add_all([account, symbol])
        await s.flush()
        s.add(
            Position(
                account_id=account.id, symbol_id=symbol.id, quantity=D("2"), avg_price=D("50")
            )
        )
        await s.commit()
        await s.refresh(account)
        return account


async def test_compute_equity_uses_avg_when_no_mark(
    db_factory: async_sessionmaker[AsyncSession],
) -> None:
    account = await _seed(db_factory)
    async with db_factory() as s:
        acct = await s.get(Account, account.id)
        assert acct is not None
        equity = await compute_equity(s, FakeRedis(), acct)  # type: ignore[arg-type]
    assert equity == D("100100")  # 100000 cash + 2 * 50 mark(=avg)


async def test_allocation_weights_sum_to_one(
    db_factory: async_sessionmaker[AsyncSession],
) -> None:
    account = await _seed(db_factory)
    async with db_factory() as s:
        acct = await s.get(Account, account.id)
        assert acct is not None
        entries = await allocation(s, FakeRedis(), acct)  # type: ignore[arg-type]

    by_symbol = {e.symbol: e for e in entries}
    assert set(by_symbol) == {"CASH", "BTCUSDT"}
    assert abs(sum(e.weight for e in entries) - 1.0) < 1e-9
    assert by_symbol["CASH"].weight > by_symbol["BTCUSDT"].weight
    assert by_symbol["BTCUSDT"].market_value == D("100")  # 2 * 50
