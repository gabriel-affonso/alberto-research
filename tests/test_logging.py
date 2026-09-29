"""Tests for structured logging and log-level resolution."""

from __future__ import annotations

import json
import logging

from alberto_research.logging import (
    LOGGER_NAMESPACE,
    JsonFormatter,
    configure_logging,
    resolve_log_level,
)


def make_record(**extra: object) -> logging.LogRecord:
    record = logging.LogRecord(
        name="alberto_research.test",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="hello %s",
        args=("world",),
        exc_info=None,
    )
    for key, value in extra.items():
        setattr(record, key, value)
    return record


def test_json_formatter_emits_expected_fields() -> None:
    payload = json.loads(JsonFormatter().format(make_record()))
    assert payload["level"] == "INFO"
    assert payload["logger"] == "alberto_research.test"
    assert payload["message"] == "hello world"
    assert "timestamp" in payload


def test_json_formatter_includes_run_id_when_present() -> None:
    payload = json.loads(JsonFormatter().format(make_record(run_id="run_42")))
    assert payload["run_id"] == "run_42"


def test_json_formatter_includes_traceback() -> None:
    try:
        raise ValueError("boom")
    except ValueError:
        import sys

        record = logging.LogRecord(
            name="alberto_research.test",
            level=logging.ERROR,
            pathname=__file__,
            lineno=1,
            msg="failed",
            args=(),
            exc_info=sys.exc_info(),
        )
    payload = json.loads(JsonFormatter().format(record))
    assert "ValueError: boom" in payload["exc_info"]


def test_resolve_log_level_defaults_when_unset(monkeypatch) -> None:
    monkeypatch.delenv("LOG_LEVEL", raising=False)
    assert resolve_log_level() == logging.INFO


def test_resolve_log_level_reads_environment(monkeypatch) -> None:
    monkeypatch.setenv("LOG_LEVEL", "debug")
    assert resolve_log_level() == logging.DEBUG


def test_resolve_log_level_ignores_invalid_value(monkeypatch) -> None:
    monkeypatch.setenv("LOG_LEVEL", "not-a-level")
    assert resolve_log_level() == logging.INFO


def test_configure_logging_attaches_single_handler(monkeypatch) -> None:
    monkeypatch.setenv("LOG_LEVEL", "WARNING")
    configure_logging()
    logger = logging.getLogger(LOGGER_NAMESPACE)
    assert len(logger.handlers) == 1
    assert logger.level == logging.WARNING
    assert isinstance(logger.handlers[0].formatter, JsonFormatter)


def test_configure_logging_accepts_explicit_level() -> None:
    configure_logging(logging.ERROR)
    assert logging.getLogger(LOGGER_NAMESPACE).level == logging.ERROR
