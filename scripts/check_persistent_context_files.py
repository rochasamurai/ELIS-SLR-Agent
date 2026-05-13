#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REQUIRED = [
    Path('.openclaw'),
    Path('HEARTBEAT.md'),
    Path('IDENTITY.md'),
    Path('SOUL.md'),
    Path('TOOLS.md'),
    Path('USER.md'),
]


def main() -> int:
    p = argparse.ArgumentParser(description="Check persistent context files")
    p.add_argument("--repo", default=".")
    args = p.parse_args()
    repo = Path(args.repo).resolve()
    missing = [str(path) for path in REQUIRED if not (repo / path).exists()]
    if missing:
        print(f"MISSING:{','.join(missing)}", file=sys.stderr)
        return 2
    print("PERSISTENT_CONTEXT_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
