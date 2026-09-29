"""Entry point for ``python -m alberto_research``."""

from __future__ import annotations

import sys

from alberto_research.cli import main

if __name__ == "__main__":
    sys.exit(main())
