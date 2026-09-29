from __future__ import annotations

import sqlite3
from importlib import resources
from pathlib import Path


def default_migrations_dir() -> Path:
    """Return the directory holding the bundled SQL migrations.

    Migrations ship inside the installed package so that ``alberto-research db
    migrate`` works from a wheel, not only from a source checkout.
    """
    bundled = resources.files("alberto_research").joinpath("migrations")
    path = Path(str(bundled))
    if path.is_dir():
        return path
    # Fallback for legacy layouts that keep migrations at the repository root.
    return Path(__file__).resolve().parents[3] / "migrations"


def applied_versions(conn: sqlite3.Connection) -> set[str]:
    conn.execute(
        "CREATE TABLE IF NOT EXISTS schema_migrations "
        "(version TEXT PRIMARY KEY, applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)"
    )
    return {
        row["version"] for row in conn.execute("SELECT version FROM schema_migrations").fetchall()
    }


def apply_migrations(conn: sqlite3.Connection, migrations_dir: Path | None = None) -> list[str]:
    directory = migrations_dir or default_migrations_dir()
    versions = applied_versions(conn)
    applied: list[str] = []
    for path in sorted(directory.glob("*.sql")):
        version = path.stem
        if version in versions:
            continue
        with conn:
            conn.executescript(path.read_text(encoding="utf-8"))
            conn.execute("INSERT OR IGNORE INTO schema_migrations(version) VALUES (?)", (version,))
        applied.append(version)
    return applied
