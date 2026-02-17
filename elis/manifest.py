"""Run manifest writer utility for PE1a."""

from __future__ import annotations

import hashlib
import json
import platform
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence


def write_manifest(manifest: Mapping[str, Any], manifest_path: str | Path) -> Path:
    """Write a manifest JSON sidecar file and return its path."""
    target = Path(manifest_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(dict(manifest), ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return target


def now_utc_iso() -> str:
    """Return current UTC timestamp in ISO-8601 format with trailing Z."""
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def short_commit_sha() -> str:
    """Return short git SHA when available; otherwise a schema-valid placeholder."""
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
        if len(out) >= 7:
            return out
    except Exception:
        pass
    return "unknown00"


def sha256_json(payload: Mapping[str, Any]) -> str:
    """Hash a mapping with stable JSON serialisation."""
    encoded = json.dumps(
        dict(payload), ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return f"sha256:{hashlib.sha256(encoded).hexdigest()}"


def manifest_path_for_output(output_path: str | Path) -> Path:
    """Return companion *_manifest.json path for a stage output."""
    out = Path(output_path)
    if out.suffix:
        return out.with_name(f"{out.stem}_manifest.json")
    return out.with_name(f"{out.name}_manifest.json")


def default_run_id(stage: str, source: str) -> str:
    """Build a compact run_id suitable for manifests."""
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    return f"{stamp}_{stage}_{source}"


def emit_run_manifest(
    *,
    stage: str,
    source: str,
    input_paths: Sequence[str],
    output_path: str,
    record_count: int,
    config_payload: Mapping[str, Any],
    run_id: str | None = None,
    started_at: str | None = None,
    finished_at: str | None = None,
    manifest_path: str | Path | None = None,
) -> Path:
    """Build and write a run manifest sidecar for a pipeline stage."""
    out_path = Path(output_path)
    target = (
        Path(manifest_path) if manifest_path else manifest_path_for_output(out_path)
    )
    manifest = {
        "schema_version": "1.0",
        "run_id": run_id or default_run_id(stage, source),
        "stage": stage,
        "source": source,
        "commit_sha": short_commit_sha(),
        "config_hash": sha256_json(config_payload),
        "started_at": started_at or now_utc_iso(),
        "finished_at": finished_at or now_utc_iso(),
        "record_count": int(record_count),
        "input_paths": list(input_paths),
        "output_path": str(out_path),
        "tool_versions": {"python": platform.python_version()},
    }
    return write_manifest(manifest, target)
