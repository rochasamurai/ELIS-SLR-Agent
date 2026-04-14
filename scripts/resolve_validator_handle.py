"""Resolve the current validator handle from CURRENT_PE.md via identity mapping."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from elis.reviewer_identity import ReviewerIdentityError, review_handle_for_engine
from scripts.implementer_runner_common import RunnerError, parse_current_pe


def main() -> int:
    current_pe_path = Path(os.environ.get("CURRENT_PE_PATH", "CURRENT_PE.md"))
    output_path = os.environ.get("GITHUB_OUTPUT", "").strip()

    try:
        context = parse_current_pe(current_pe_path)
        handle = review_handle_for_engine(context.validator_engine)
    except (RunnerError, ReviewerIdentityError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1

    lines = [
        f"mention={handle}",
        f"engine={context.validator_engine}",
        f"pe_id={context.pe_id}",
    ]
    if output_path:
        with open(output_path, "a", encoding="utf-8") as handle_file:
            handle_file.write("\n".join(lines) + "\n")
    else:
        print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
