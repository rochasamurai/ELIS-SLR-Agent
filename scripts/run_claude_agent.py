"""PE-AUTO-04 entrypoint for the Claude implementer runner."""

from __future__ import annotations

import sys

from scripts.implementer_runner_common import run_implementer


if __name__ == "__main__":
    sys.exit(run_implementer(sys.argv, engine="claude"))
