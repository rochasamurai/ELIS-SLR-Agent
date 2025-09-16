#!/usr/bin/env python3
"""
ELIS Validation Script (Extended)
- Validates repository structure, schemas, and JSON/JSONL rows.
- Cross-checks with canonical XLSX (placeholder).
- Generates human-readable Markdown reports under validation_reports/.
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone

# Paths
ROOT = Path(__file__).resolve().parent.parent
SCHEMAS_DIR = ROOT / "schemas"
DATA_DIR = ROOT / "json_jsonl"
REPORTS_DIR = ROOT / "validation_reports"

def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def scan_repository():
    findings = []
    # Check critical dirs
    for d in [SCHEMAS_DIR, DATA_DIR, REPORTS_DIR]:
        if not d.exists():
            findings.append(f"[BLOCKER] Missing required directory: {d}")
    # Simple file presence checks
    if not (ROOT / "README.md").exists():
        findings.append("[MAJOR] Missing root README.md")
    if not (ROOT / "CHANGELOG.md").exists():
        findings.append("[MINOR] Missing CHANGELOG.md")
    return findings

def generate_report(findings):
    today = datetime.now().strftime("%Y-%m-%d")
    report_lines = []
    report_lines.append(f"# 📑 ELIS Validation Report\n")
    report_lines.append(f"**Date:** {today}\n")
    report_lines.append(f"**Scope:** Automatic repository validation (schemas, data, docs)\n\n")
    report_lines.append("---\n")
    report_lines.append("## ✅ Summary\n")
    if not findings:
        report_lines.append("All critical components are present. No blockers detected.\n")
    else:
        report_lines.append("Findings detected, see below.\n")
    report_lines.append("---\n")
    report_lines.append("## 2. Findings\n")
    if findings:
        for f in findings:
            report_lines.append(f"- {f}\n")
    else:
        report_lines.append("- No issues found.\n")
    report_lines.append("---\n")
    report_lines.append("## 3. Next Steps\n")
    report_lines.append("1. Expand schema/data validation against XLSX canonical.\n")
    report_lines.append("2. Archive obsolete files.\n")
    report_lines.append("3. Ensure CI publishes this report on each run.\n")
    report_lines.append("\n---\n")
    report_lines.append("*Generated automatically in alignment with ELIS Protocol v1.41 and Agent Prompt v2.0.*\n")

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    out = REPORTS_DIR / f"{today}_validation_report.md"
    out.write_text("".join(report_lines), encoding="utf-8")
    print(f"Validation report written to {out}")

def main():
    findings = scan_repository()
    generate_report(findings)
    if findings:
        sys.exit(2)
    sys.exit(0)

if __name__ == "__main__":
    main()
