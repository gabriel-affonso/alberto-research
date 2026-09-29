from __future__ import annotations

from pathlib import Path

import pytest

from alberto_research.config import load_project_config, validate_project_config

EXAMPLES = sorted(Path("examples").glob("*.yaml"))


def test_examples_are_present() -> None:
    assert EXAMPLES, "at least one example project config must ship in examples/"


@pytest.mark.parametrize("example", EXAMPLES, ids=lambda p: p.name)
def test_shipped_examples_are_valid(example: Path) -> None:
    config = load_project_config(example)
    validate_project_config(config)
    assert config["id"]


@pytest.mark.parametrize("example", EXAMPLES, ids=lambda p: p.name)
def test_shipped_examples_keep_shadow_libraries_disabled(example: Path) -> None:
    """Shipped examples must never enable paywall-bypassing resolvers."""
    fulltext = load_project_config(example).get("fulltext") or {}
    assert fulltext.get("enable_scihub") in (None, False)
    assert fulltext.get("enable_annas_archive") in (None, False)


@pytest.mark.parametrize("example", EXAMPLES, ids=lambda p: p.name)
def test_shipped_examples_use_role_email_addresses(example: Path) -> None:
    """No personal contact address may ship in an example (CrossRef polite pool)."""
    email = (load_project_config(example).get("fulltext") or {}).get("unpaywall_email")
    if email:
        assert email.endswith("@example.com") or email.endswith("@example.test")


def test_example_project_config_loads() -> None:
    config = load_project_config(Path("examples/basic.yaml"))
    assert config["id"] == "alberto-research-example"
    assert config["timezone"] == "Europe/Lisbon"
    assert config["citation_chasing"]["enabled"] is True


def test_project_config_requires_threshold_range() -> None:
    config = load_project_config(Path("examples/basic.yaml"))
    config["screening_threshold"] = 1.2
    with pytest.raises(ValueError):
        validate_project_config(config)
