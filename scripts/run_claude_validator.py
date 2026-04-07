"""PE-AUTO-05 entrypoint for the Claude validator runner."""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure repo root is on sys.path regardless of invocation method
# (e.g. 'python scripts/run_claude_validator.py' vs 'python -m scripts.run_claude_validator').
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.validator_runner_common import run_validator


if __name__ == "__main__":
    sys.exit(run_validator(sys.argv, engine="claude"))
