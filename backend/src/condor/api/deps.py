"""Shared FastAPI dependencies."""

from __future__ import annotations

from typing import cast

from fastapi import Request
from redis.asyncio import Redis


def get_redis(request: Request) -> Redis:
    """The app-scoped Redis client created in the lifespan handler."""
    return cast(Redis, request.app.state.redis)
