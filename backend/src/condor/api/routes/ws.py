"""WS /ws/prices — bridge Redis tick channels to the browser.

The client connects with ``?symbols=BTCUSDT,ETHUSDT``. We subscribe to those
Redis channels and forward every message. A disconnected client cancels the
pump cleanly and the Redis subscription is always closed in ``finally``.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from condor.redis_bus import make_redis, ticks_channel

router = APIRouter(tags=["ws"])
log = logging.getLogger(__name__)


@router.websocket("/ws/prices")
async def prices_ws(websocket: WebSocket, symbols: str = Query("")) -> None:
    wanted = [s.strip().upper() for s in symbols.split(",") if s.strip()]
    if not wanted:
        await websocket.close(code=1008, reason="no symbols requested")
        return

    await websocket.accept()
    redis = make_redis()
    pubsub = redis.pubsub()
    await pubsub.subscribe(*[ticks_channel(s) for s in wanted])
    log.info("ws_client_connected", extra={"symbols": wanted})
    try:
        async for message in pubsub.listen():
            if message.get("type") == "message":
                await websocket.send_text(message["data"])
    except WebSocketDisconnect:
        log.info("ws_client_disconnected", extra={"symbols": wanted})
    finally:
        await pubsub.aclose()  # type: ignore[no-untyped-call]  # redis-py async stub gap
        await redis.aclose()
