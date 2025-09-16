#!/usr/bin/env python3
"""
ELIS Validation Script (Extended, fail-only-on-BLOCKER)

Purpose
-------
1. Check the minimal repository structure (directories and key files).
2. Verify the presence of the canonical XLSX file in /docs.
3. Generate a Markdown report under validation_reports/ with a unique timestamped name.
4. Exit with code 1 only if a [BLOCKER] issue is found; otherwise exit 0.

Usage
-----
python scripts/validate_json.py
"""

from __future__ import annotations
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import List

# ---------- Repository paths ----------
ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = ROOT / "docs"
SCHEMAS_DIR = ROOT / "schemas"
DATA_DIR = ROOT / "json_jsonl"
REPORTS_DIR = ROOT / "validation_reports"
CANON_XLSX = DOCS_DIR / "ELIS_Data_Sheets_2025-08-19_v1.0.xlsx"

# ---------- Time helpers ----------
utc_now = lambda: datetime.now(timezone.utc)
ts_isoz = lambda: utc_now().strftime("%Y-%m-%dT%H:%M:%SZ")     # e.g. 2025-09-16T15:42:10Z
ts_date = lambda: utc_now().strftime("%Y-%m-%d")               # e.g. 2025-09-16
ts_full = lambda: utc_now().strftime("%Y-%m-%d_%H%M%S")        # e.g. 2025-09-16_154210

# ---------- Validation checks ----------
def scan() -> List[str]:
    """
    Perform structural checks and return a list of findings.
    Prefixes:
      - [BLOCKER] → must fail the CI (exit 1)
      - [MINOR]   → advisory only
    """
    findings: List[str] = []

    # Required directories
    for d in (DOCS_DIR, SCHEMAS_DIR, DATA_DIR, REPORTS_DIR):
        if not d.exists():
            findings.append(f"[BLOCKER] Missing required directory: {d.relative_to(ROOT)}")

    # Required root-level files
    if not (ROOT / "README.md").exists():
        findings.append("[MINOR] Missing README.md at repository root")
    if not (ROOT / "CHANGELOG.md").exists():
        findings.append("[MINOR] Missing CHANGELOG.md at repository root")

    # Canonical XLSX
    if not CANON_XLSX.exists():
        findings.append(f"[BLOCKER] Canonical XLSX not found: {CANON_XLSX.relative_to(ROOT)}")

    # Obsolete files to be removed
    for junk in (DATA_DIR / "desktop.ini", SCHEMAS_DIR / "desktop.ini"):
        if junk.exists():
            findings.append(f"[MINOR] Obsolete file present: {junk.relative_to(ROOT)}")

    return findings

# ---------- Report writer ----------
def write_report(findings: List[str]) -> Path:
    """
    Write a Markdown validation report with a unique timestamp.
    Returns the path to the generated file.
    """
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    out = REPORTS_DIR / f"{ts_date()}_{ts_full()}_validation_report.md"

    # Header and metadata
    lines: List[str] = [
        "# 📑 ELIS Validation Report\n",
        f"**Generated:** {ts_isoz()}  \n",
        "**Scope:** Automatic repository validation (structure, canonical docs)\n\n",
        "---\n\n",
        "## ✅ Summary\n",
    ]

    # Overall status
    if any("BLOCKER" in f for f in findings):
        lines.append("- Status: **Issues detected (BLOCKER present)**\n")
    elif findings:
        lines.append("- Status: **Findings detected (no blocker)**\n")
    else:
        lines.append("- Status: **All critical checks passed**\n")
    lines.append("\n---\n\n")

    # Checks executed
    lines += [
        "## 1) Checks Executed\n",
        "- Directories: `docs/`, `schemas/`, `json_jsonl/`, `validation_reports/`\n",
        "- Root files: `README.md`, `CHANGELOG.md`\n",
        f"- Canonical XLSX: `{CANON_XLSX.name}` in `/docs`\n",
        "\n---\n\n",
    ]

    # Findings
    lines.append("## 2) Findings\n")
    if findings:
        for f in findings:
            lines.append(f"- {f}\n")
    else:
        lines.append("- No issues found.\n")
    lines += [
        "\n---\n\n",
        "## 3) Next Steps\n",
        "1. Remove obsolete files (e.g., `desktop.ini`).\n",
        "2. Keep the canonical XLSX in `/docs` and updated.\n",
        "3. (Optional) Extend validation to check JSON/JSONL against schemas/XLSX.\n",
        "\n---\n\n",
        "*Aligned with ELIS Protocol v1.41 and Agent Prompt v2.0.*\n",
    ]

    out.write_text("".join(lines), encoding="utf-8")
    print(f"Validation report written to {out}")  # Log for Actions
    return out

# ---------- Main ----------
def main() -> int:
    """
    Execute the checks and generate the report.
    Returns 1 if a [BLOCKER] is found, otherwise 0 (pipeline passes with warnings).
    """
    findings = scan()
    write_report(findings)
    return 1 if any("BLOCKER" in f for f in findings) else 0

if __name__ == "__main__":
    sys.exit(main())
