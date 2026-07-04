"""Binance public WebSocket provider (no API key required).

Subscribes to the combined ``@trade`` stream and normalizes each message into a
``Tick``. Reconnects on any drop with jittered exponential backoff; a clean run
resets the backoff. The heartbeat is Binance's own ping/pong, handled by the
``websockets`` client.
"""

from __future__ import annotations

import asyncio
import json
import logging
from collections.abc import AsyncIterator
from datetime import UTC, datetime
from decimal import Decimal

import websockets

from condor.config import get_settings
from condor.ingest.reconnect import Backoff
from condor.marketdata.types import Tick

log = logging.getLogger(__name__)


class BinanceProvider:
    name = "binance"

    def __init__(self, ws_base: str | None = None) -> None:
        self._ws_base = ws_base or get_settings().binance_ws_url

    def _url(self, symbols: list[str]) -> str:
        streams = "/".join(f"{s.lower()}@trade" for s in symbols)
        return f"{self._ws_base}?streams={streams}"

    @staticmethod
    def _parse(raw: str | bytes) -> Tick | None:
        msg = json.loads(raw)
        data = msg.get("data", msg)
        if data.get("e") != "trade":
            return None
        return Tick(
            symbol=data["s"],
            price=Decimal(data["p"]),
            quantity=Decimal(data["q"]),
            ts=datetime.fromtimestamp(data["T"] / 1000, tz=UTC),
        )

    async def stream_trades(self, symbols: list[str]) -> AsyncIterator[Tick]:
        url = self._url(symbols)
        backoff = Backoff()
        while True:
            try:
                async with websockets.connect(url, ping_interval=20, ping_timeout=20) as ws:
                    log.info("binance_connected", extra={"symbols": symbols})
                    backoff.reset()
                    async for raw in ws:
                        tick = self._parse(raw)
                        if tick is not None:
                            yield tick
            except asyncio.CancelledError:
                raise
            except Exception as exc:  # noqa: BLE001 — reconnect on any transport error
                delay = backoff.next_delay()
                log.warning(
                    "binance_disconnected",
                    extra={"error": str(exc), "retry_in_s": round(delay, 2)},
                )
                await asyncio.sleep(delay)
