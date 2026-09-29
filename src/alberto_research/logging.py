from __future__ import annotations

import json
import logging
import os
import sys
from datetime import UTC, datetime
from typing import Any

LOGGER_NAMESPACE = "alberto_research"


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if hasattr(record, "run_id"):
            payload["run_id"] = record.run_id
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(payload, sort_keys=True)


def resolve_log_level(default: int = logging.INFO) -> int:
    """Resolve the log level from ``LOG_LEVEL``, falling back to ``default``."""
    raw = os.environ.get("LOG_LEVEL", "").strip().upper()
    if not raw:
        return default
    level = logging.getLevelName(raw)
    return level if isinstance(level, int) else default


def configure_logging(level: int | None = None) -> None:
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger(LOGGER_NAMESPACE)
    root.handlers[:] = [handler]
    root.setLevel(resolve_log_level() if level is None else level)
