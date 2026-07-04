"""Structured logging via the stdlib only — no extra dependency.

``configure_logging`` installs a JSON (or key=value) formatter on the root
logger. Application code uses ``logging.getLogger(__name__)`` and passes context
through the ``extra=`` kwarg; those keys land in the structured output.
"""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from typing import Any

# stdlib LogRecord attributes we never want to duplicate into the payload.
_RESERVED = set(logging.makeLogRecord({}).__dict__) | {"message", "asctime", "taskName"}


class StructuredFormatter(logging.Formatter):
    """Render each record as one JSON object (or key=value line)."""

    def __init__(self, *, as_json: bool = True) -> None:
        super().__init__()
        self.as_json = as_json

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "ts": datetime.fromtimestamp(record.created, tz=UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        # Anything passed via extra= that isn't a standard LogRecord field.
        for key, value in record.__dict__.items():
            if key not in _RESERVED:
                payload[key] = value
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)

        if self.as_json:
            return json.dumps(payload, default=str)
        return " ".join(f"{k}={v}" for k, v in payload.items())


def configure_logging(level: str = "INFO", *, as_json: bool = True) -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(StructuredFormatter(as_json=as_json))
    root = logging.getLogger()
    root.handlers[:] = [handler]
    root.setLevel(level.upper())
