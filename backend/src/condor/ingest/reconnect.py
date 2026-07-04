"""Exponential backoff with full jitter for WS reconnects.

Pure and deterministic given an injected ``rand`` — so the backoff schedule is
unit-tested (``tests/test_reconnect.py``) without sleeping. A successful, stable
connection calls ``reset()`` to drop back to the base delay.
"""

from __future__ import annotations

import random
from collections.abc import Callable


class Backoff:
    def __init__(
        self,
        *,
        base: float = 1.0,
        factor: float = 2.0,
        cap: float = 60.0,
        rand: Callable[[], float] = random.random,
    ) -> None:
        self.base = base
        self.factor = factor
        self.cap = cap
        self._rand = rand
        self._attempt = 0

    def reset(self) -> None:
        self._attempt = 0

    def next_delay(self) -> float:
        """Full-jitter delay: uniform(0, min(cap, base * factor**attempt))."""
        ceiling = min(self.cap, self.base * (self.factor**self._attempt))
        self._attempt += 1
        return self._rand() * ceiling
