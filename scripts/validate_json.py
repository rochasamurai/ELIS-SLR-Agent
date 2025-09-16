#!/usr/bin/env python3
"""
ELIS Validation Script (Extended, fail-only-on-BLOCKER)

What it does
- Scans basic repo structure (docs/, schemas/, json_jsonl/, validation_reports/).
- Checks presence of key docs (README.md, CHANGELOG.md, XLSX canonical in /docs).
- Writes a human-readable Markdown report to validation_reports/YYYY-MM-DD_validation_report.md.
- Exits with code 1 ONLY if a BLOCKER is found; otherwise exits 0 (so CI stays green on non-critical issues).
"""

from __future__ import annotations
import sys
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List

# ---- Paths ----
ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = ROOT / "docs"
SCHEMAS_DIR = ROOT / "schemas"
DATA_DIR = ROOT / "json_jsonl"
REPORTS_DIR = ROOT / "validation_reports"
CANON_XLSX = DOCS_DIR / "ELIS_Data_Sheets_2025-08-19_v1.0.xlsx"  # canonical reference

# ---- Utils ----
def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def today_str() -> str:
    return datetime.now().strftime("%Y-%m-%d")

# ---- Validation steps (lightweight; schema/data deep checks can be added later) ----
def scan_repository() -> List[str]:
    findings: List[str] = []
    # Required directories
    for d in (DOCS_DIR, SCHEMAS_DIR, DATA_DIR, REPORTS_DIR):
        if not d.exists():
            findings.append(f"[BLOCKER] Missing required directory: {d.relative_to(ROOT)}")

    # Required top-level docs
    if not (ROOT / "README.md").exists():
        findings.append("[MINOR] Missing README.md at repo root")
    if not (ROOT / "CHANGELOG.md").exists():
        findings.append("[MINOR] Missing CHANGELOG.md at repo root")

    # Canonical XLSX presence
    if not CANON_XLSX.exists():
        findings.append(f"[BLOCKER] Canonical XLSX not found: {CANON_XLSX.relative_to(ROOT)}")

    # Quick housekeeping
    for junk in (DATA_DIR / "desktop.ini", SCHEMAS_DIR / "desktop.ini"):
        if junk.exists():
            findings.append(f"[MINOR] Obsolete file present: {junk.relative_to(ROOT)} (remove)")

    return findings

# ---- Report generation ----
def generate_report(findings: List[str]) -> Path:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    out = REPORTS_DIR / f"{today_str()}_validation_report.md"

    lines: List[str] = []
    lines.append("# 📑 ELIS Validation Report\n")
    lines.append(f"**Generated:** {utc_now()}  \n")
    lines.append("**Scope:** Automatic repository validation (structure, canonical docs)\n\n")
    lines.append("---\n\n")
    lines.append("## ✅ Summary\n")
    if any("BLOCKER" in f for f in findings):
        lines.append("- Status: **Issues detected (BLOCKER present)**\n")
    elif findings:
        lines.append("- Status: **Findings detected (no blocker)**\n")
    else:
        lines.append("- Status: **All critical checks passed**\n")
    lines.append("\n---\n\n")

    lines.append("## 1) Checks Executed\n")
    lines.append("- Directories present: `docs/`, `schemas/`, `json_jsonl/`, `validation_reports/`\n")
    lines.append("- Root docs present: `README.md`, `CHANGELOG.md`\n")
    lines.append(f"- Canonical XLSX: `{CANON_XLSX.name}` in `/docs`\n")
    lines.append("\n---\n\n")

    lines.append("## 2) Findings\n")
    if findings:
        for f in findings:
            lines.append(f"- {f}\n")
    else:
        lines.append("- No issues found.\n")
    lines.append("\n---\n\n")

    lines.append("## 3) Next Steps\n")
    lines.append("1. Remove obsolete files (e.g., `desktop.ini`).\n")
    lines.append("2. Keep the canonical XLSX in `/docs` and updated.\n")
    lines.append("3. (Optional) Extend this script to validate JSON/JSONL against schemas and XLSX.\n")
    lines.append("\n---\n\n")
    lines.append("*Aligned with ELIS Protocol v1.41 and Agent Prompt v2.0.*\n")

    out.write_text("".join(lines), encoding="utf-8")
    print(f"Validation report written to {out}")
    return out

# ---- Main ----
def main() -> int:
    findings = scan_repository()
    generate_report(findings)

    # Fail CI only when a BLOCKER exists
    if any("BLOCKER" in f for f in findings):
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
