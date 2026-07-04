# Condor

A web-based **paper trading terminal** with real-time market data, a simulated
execution engine, an options strategy lab, and a portfolio risk dashboard.

> Dark, professional trading-terminal aesthetic. Runs entirely on **free data
> sources** — no paid API keys. `docker compose up` and it streams.

**Status:** Phase 1 (market data infrastructure) in progress.

## Stack

| Layer    | Tech |
|----------|------|
| Backend  | Python 3.12 · FastAPI (async) · Pydantic v2 · SQLAlchemy 2 · Alembic |
| Data     | PostgreSQL 16 · Redis (pub/sub + cache) |
| Frontend | React 18 · TypeScript (strict) · Vite · Tailwind · lightweight-charts |
| Infra    | Docker Compose · GitHub Actions (ruff · mypy · pytest · tsc · eslint) |

Live crypto via Binance public WebSocket (`BTCUSDT`, `ETHUSDT`, `SOLUSDT` by
default). Delayed equities via `yfinance`. All providers sit behind a
`MarketDataProvider` interface.

## Design decisions

- **1-minute base candles, resampled on read.** The DB stores one resolution;
  `5m / 1h / 1d` are aggregated server-side. Bounded storage, one write path.
- **`Decimal` / `NUMERIC` on every money-adjacent value.** Prices, volumes,
  balances, P&L — never `float`. Floats are confined to pricing formulas
  (Phase 3).
- **Trade stream → in-house 1m aggregation.** We fold Binance trades into
  candles ourselves (pure, unit-tested `CandleAggregator`); the kline stream
  re-seeds the in-progress minute on reconnect for clean recovery.
- **Redis fan-out.** The ingest worker publishes ticks to Redis; the API
  bridges Redis pub/sub to browser WebSocket clients.

## Quickstart

```bash
cp .env.example .env
docker compose up --build
# web:  http://localhost:5173
# api:  http://localhost:8000/docs
```

## Development

```bash
make dev     # run stack
make test    # backend pytest
make lint    # ruff + mypy (backend), eslint + tsc (web)
make seed    # seed reference data
```

## License

MIT
