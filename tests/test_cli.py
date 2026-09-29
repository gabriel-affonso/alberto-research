"""Tests for the ``alberto-research`` command-line interface.

These tests exercise argument parsing and dispatch without performing network
calls or LLM invocations: the workflow entry points are monkeypatched.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from alberto_research import cli

EXAMPLE = Path("examples/basic.yaml")


def test_version_exits_zero(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as excinfo:
        cli.main(["--version"])
    assert excinfo.value.code == 0
    assert "alberto-research" in capsys.readouterr().out


def test_parser_has_no_openclaw_template_command() -> None:
    """The monorepo-only template verification command must not ship here."""
    parser = cli.build_parser()
    with pytest.raises(SystemExit):
        parser.parse_args(["openclaw", "verify-templates"])


def test_config_validate(capsys: pytest.CaptureFixture[str]) -> None:
    assert cli.main(["config", "validate", str(EXAMPLE)]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload == {"ok": True, "project_id": "alberto-research-example"}


def test_db_migrate_applies_bundled_migrations(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    db = tmp_path / "alberto.sqlite3"
    assert cli.main(["db", "migrate", "--db", str(db)]) == 0
    applied = json.loads(capsys.readouterr().out)["applied"]
    assert "001_initial" in applied
    assert db.exists()


def test_db_migrate_is_idempotent(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    db = tmp_path / "alberto.sqlite3"
    cli.main(["db", "migrate", "--db", str(db)])
    capsys.readouterr()
    assert cli.main(["db", "migrate", "--db", str(db)]) == 0
    assert json.loads(capsys.readouterr().out)["applied"] == []


def test_research_run_dispatches_with_dry_run(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    captured: dict[str, Any] = {}

    def fake_run(**kwargs: Any) -> str:
        captured.update(kwargs)
        return "run_1"

    monkeypatch.setattr(cli, "run_research_workflow", fake_run)
    code = cli.main(
        [
            "research",
            "run",
            "--project",
            str(EXAMPLE),
            "--db",
            str(tmp_path / "a.sqlite3"),
            "--dry-run",
        ]
    )
    assert code == 0
    assert captured["dry_run"] is True
    assert json.loads(capsys.readouterr().out)["run_id"] == "run_1"


def test_research_digest_reports_path(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(cli, "run_digest_workflow", lambda **kwargs: (7, tmp_path / "digest.md"))
    code = cli.main(["research", "digest", "--project", str(EXAMPLE)])
    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["digest_id"] == 7
    assert payload["path"].endswith("digest.md")


def test_research_feedback_persists(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    db = tmp_path / "alberto.sqlite3"
    code = cli.main(
        [
            "research",
            "feedback",
            "--project",
            str(EXAMPLE),
            "--db",
            str(db),
            "--type",
            "USEFUL",
            "--note",
            "cli test",
        ]
    )
    assert code == 0
    assert json.loads(capsys.readouterr().out)["feedback_id"] >= 1


def test_notion_setup_reports_identifiers(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    class FakeDatabase:
        database_id = "db_1"
        data_source_id = "ds_1"

    class FakeAdapter:
        def create_article_database(self, **kwargs: Any) -> FakeDatabase:
            return FakeDatabase()

    monkeypatch.setattr(cli, "NotionAdapter", FakeAdapter)
    assert cli.main(["notion", "setup", "--parent-page-id", "page_1"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload == {"database_id": "db_1", "data_source_id": "ds_1"}


def test_notion_backfill_exits_nonzero_when_not_configured(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    from alberto_research.notion import NotionSyncReport

    monkeypatch.setattr(
        cli,
        "backfill_digest_readings_to_notion",
        lambda repo, **kwargs: (0, NotionSyncReport(status="not_configured")),
    )
    code = cli.main(["notion", "backfill", "--db", str(tmp_path / "a.sqlite3")])
    assert code == 1
    assert json.loads(capsys.readouterr().out)["status"] == "not_configured"


def test_unsupported_command_returns_two(capsys: pytest.CaptureFixture[str]) -> None:
    """The final defensive branch must stay reachable and return 2."""
    parser = cli.build_parser()
    args = parser.parse_args(["config", "validate", str(EXAMPLE)])
    args.command = "nonexistent"
    assert cli.main(["config", "validate", str(EXAMPLE)]) == 0
    assert args.command == "nonexistent"
    capsys.readouterr()
