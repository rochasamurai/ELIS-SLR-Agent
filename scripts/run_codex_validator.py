"""PE-AUTO-05 entrypoint for the CODEX validator runner."""

from __future__ import annotations

import sys

from scripts.validator_runner_common import run_validator


if __name__ == "__main__":
    sys.exit(run_validator(sys.argv, engine="codex"))
