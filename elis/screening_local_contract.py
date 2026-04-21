"""Local screening contract helpers for PE-SLR-03.

This module defines a review-scoped local screening contract for `elis-server`:
- review-specific workspace paths
- schema-bound input/output expectations
- bounded pilot execution with auditable artefacts
"""

from __future__ import annotations

import importlib
import json
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


RUNTIME_STATE_DIR_NAMES = {".openclaw", ".claude", ".codex", ".config"}


def now_utc_iso() -> str:
    """Return current UTC timestamp in ISO format with `Z` suffix."""
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def _is_under_runtime_state(path: Path) -> bool:
    """Return True when path parts include a known runtime-state directory."""
    lowered = {part.lower() for part in path.resolve().parts}
    return any(name.lower() in lowered for name in RUNTIME_STATE_DIR_NAMES)


def assert_non_runtime_storage(path: Path) -> None:
    """Fail fast if the target path is in runtime state directories."""
    if _is_under_runtime_state(path):
        raise ValueError(
            "Screening artefacts must be stored outside runtime state directories: "
            f"{path}"
        )


@dataclass(frozen=True)
class ScreeningWorkspaceContract:
    """Stable path contract for review-scoped local screening artefacts."""

    review_id: str
    root: Path = Path("artifacts/screening")

    def review_root(self) -> Path:
        return self.root / self.review_id

    def input_dir(self) -> Path:
        return self.review_root() / "input"

    def output_dir(self) -> Path:
        return self.review_root() / "output"

    def audit_dir(self) -> Path:
        return self.review_root() / "audit"

    def appendix_a_input(self) -> Path:
        return self.input_dir() / "ELIS_Appendix_A_Search_rows.json"

    def appendix_b_output(self) -> Path:
        return self.output_dir() / "ELIS_Appendix_B_Screening_rows.json"

    def pilot_report(self) -> Path:
        return self.audit_dir() / "screening_pilot_report.json"

    def pilot_manifest(self) -> Path:
        return self.audit_dir() / "screening_pilot_manifest.json"

    def appendix_a_schema(self) -> Path:
        return Path("schemas/appendix_a.schema.json")

    def appendix_b_schema(self) -> Path:
        return Path("schemas/appendix_b.schema.json")

    def published_appendix_b(self) -> Path:
        return Path("json_jsonl/ELIS_Appendix_B_Screening_rows.json")

    def ensure_dirs(self) -> None:
        """Create contract directories after storage safety checks."""
        assert_non_runtime_storage(self.review_root())
        self.input_dir().mkdir(parents=True, exist_ok=True)
        self.output_dir().mkdir(parents=True, exist_ok=True)
        self.audit_dir().mkdir(parents=True, exist_ok=True)


def detect_asreview_installation() -> dict[str, Any]:
    """Detect whether ASReview is runnable on host."""
    cli_result: dict[str, Any] | None = None
    try:
        proc = subprocess.run(
            ["asreview", "--version"],
            check=False,
            capture_output=True,
            text=True,
        )
        cli_result = {
            "returncode": proc.returncode,
            "stdout": (proc.stdout or "").strip(),
            "stderr": (proc.stderr or "").strip(),
        }
    except FileNotFoundError:
        cli_result = {"returncode": 127, "stdout": "", "stderr": "asreview not found"}

    module_available = True
    module_version: str | None = None
    try:
        module = importlib.import_module("asreview")
        module_version = str(getattr(module, "__version__", "unknown"))
    except Exception:
        module_available = False

    cli_ok = cli_result["returncode"] == 0 if cli_result else False
    installed = bool(cli_ok or module_available)
    return {
        "installed": installed,
        "cli": cli_result,
        "python_module_available": module_available,
        "python_module_version": module_version,
    }


def _load_appendix_a(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError(f"Appendix A payload must be a JSON array: {path}")
    rows: list[dict[str, Any]] = []
    for row in payload:
        if isinstance(row, dict) and not row.get("_meta"):
            rows.append(row)
    return rows


def _to_appendix_b_rows(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    decided_at = now_utc_iso()
    rows: list[dict[str, Any]] = []
    for record in records:
        source_id = str(
            record.get("source_id")
            or record.get("id")
            or record.get("doi")
            or record.get("openalex_id")
            or ""
        ).strip()
        title = str(record.get("title") or "(untitled)").strip()
        rid = str(record.get("id") or source_id or title).strip()
        rows.append(
            {
                "id": rid or "unknown",
                "source_id": source_id or rid or "unknown",
                "title": title,
                "decision": "included",
                "reason": "bounded-pilot-candidate",
                "decided_at": decided_at,
            }
        )
    return rows


def run_bounded_screening_pilot(
    *,
    contract: ScreeningWorkspaceContract,
    appendix_a_path: Path,
    record_cap: int = 100,
) -> dict[str, Any]:
    """Run bounded local pilot and persist auditable outputs."""
    contract.ensure_dirs()
    assert_non_runtime_storage(contract.appendix_b_output())
    assert_non_runtime_storage(contract.pilot_report())
    assert_non_runtime_storage(contract.pilot_manifest())

    records = _load_appendix_a(appendix_a_path)
    bounded_records = records[: max(0, int(record_cap))]
    appendix_b_rows = _to_appendix_b_rows(bounded_records)

    contract.appendix_b_output().write_text(
        json.dumps(appendix_b_rows, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    report = {
        "review_id": contract.review_id,
        "stage": "screening-pilot",
        "appendix_a_input_path": appendix_a_path.as_posix(),
        "appendix_b_output_path": contract.appendix_b_output().as_posix(),
        "appendix_a_schema_path": contract.appendix_a_schema().as_posix(),
        "appendix_b_schema_path": contract.appendix_b_schema().as_posix(),
        "record_cap": int(record_cap),
        "records_seen": len(records),
        "records_processed": len(bounded_records),
        "records_written": len(appendix_b_rows),
        "stored_outside_runtime_state": True,
        "generated_at": now_utc_iso(),
    }
    contract.pilot_report().write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    manifest = {
        "schema_version": "1.0",
        "review_id": contract.review_id,
        "stage": "screening",
        "pilot_mode": "bounded",
        "record_cap": int(record_cap),
        "artefacts": {
            "appendix_b_output": contract.appendix_b_output().as_posix(),
            "pilot_report": contract.pilot_report().as_posix(),
        },
        "generated_at": now_utc_iso(),
    }
    contract.pilot_manifest().write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    return report
