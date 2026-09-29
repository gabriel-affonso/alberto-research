"""Alberto Research: scientific research automation for OpenClaw.

Alberto Research discovers, screens, reads, synthesises and delivers scientific
literature. Deterministic work (provider calls, DOI normalisation, deduplication,
persistence, delivery) is plain Python; every LLM step is bounded by an explicit
contract and validated against a JSON Schema before anything is persisted.
"""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

try:  # pragma: no cover - trivial branch on installation state
    __version__ = version("alberto-research")
except PackageNotFoundError:  # pragma: no cover - running from a source checkout
    __version__ = "0.0.0.dev0"

__all__ = ["__version__"]
