"""FastAPI application factory + lifespan."""

from __future__ import annotations

import asyncio
import contextlib
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from condor.api.errors import install_error_handlers
from condor.api.routes import candles, options, quotes, symbols, trading, ws
from condor.config import get_settings
from condor.db.base import SessionLocal
from condor.engine.orders import run_matcher
from condor.logging import configure_logging
from condor.redis_bus import make_redis


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    configure_logging(settings.log_level, as_json=settings.log_json)
    app.state.redis = make_redis()
    # Limit-order matcher runs as a background task inside the API process.
    matcher = asyncio.create_task(run_matcher(SessionLocal, app.state.redis))
    try:
        yield
    finally:
        matcher.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await matcher
        await app.state.redis.aclose()


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="Condor API", version="0.1.0", lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    install_error_handlers(app)

    app.include_router(symbols.router)
    app.include_router(candles.router)
    app.include_router(quotes.router)
    app.include_router(trading.router)
    app.include_router(options.router)
    app.include_router(ws.router)

    @app.get("/health", tags=["meta"])
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
