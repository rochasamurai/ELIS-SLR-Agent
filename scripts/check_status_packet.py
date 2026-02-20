"""check_status_packet.py — validate PR body Status Packet completeness.

Used by auto-assign-validator.yml (Gate 1).
Reads the PR_BODY environment variable and verifies all required sections
are present. Exits 1 on any failure, 0 on success.
"""

import os
import sys

REQUIRED_SECTIONS = [
    "### Verdict",
    "### Branch / PR",
    "### Gate results",
    "### Scope",
    "### Ready to merge",
]


def main() -> int:
    body = os.environ.get("PR_BODY", "")
    if not body.strip():
        print("ERROR: PR body is empty.")
        return 1

    missing = [s for s in REQUIRED_SECTIONS if s not in body]
    if missing:
        for section in missing:
            print(f"Missing section: {section}")
        return 1

    print("Status Packet OK — all required sections present.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
