"""Run manifest writer utility for PE1a."""

from __future__ import annotations

import hashlib
import importlib
import importlib.metadata
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


def _package_version() -> str:
    """Return installed package version, with a safe fallback for local runs."""
    try:
        return importlib.metadata.version("elis-slr-agent")
    except importlib.metadata.PackageNotFoundError:
        return "0.0.0+unknown"


def _collect_adapter_versions() -> dict[str, str]:
    """Return adapter version mapping (source -> version string)."""
    try:
        from elis.sources import available_sources, get_adapter
    except Exception:
        return {"unknown": "unknown"}

    versions: dict[str, str] = {}
    for source in available_sources():
        try:
            adapter_cls = get_adapter(source)
            module = importlib.import_module(adapter_cls.__module__)
            version = (
                getattr(module, "__version__", None)
                or getattr(module, "ADAPTER_VERSION", None)
                or "builtin"
            )
            versions[source] = str(version)
        except Exception:
            versions[source] = "unknown"
    return versions or {"unknown": "unknown"}


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
    model_family: str | None = None,
    model_family_justification: str = "No model used for this stage.",
    model_identifier: str | None = None,
    model_identifier_justification: str = "No model used for this stage.",
    model_version_snapshot: str | None = None,
    routing_policy_version: str = "unversioned",
    search_config_schema_version: str = "unknown",
    adapter_versions: Mapping[str, str] | None = None,
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

    started = started_at or now_utc_iso()
    finished = finished_at or now_utc_iso()
    repo_sha = short_commit_sha()

    manifest = {
        "schema_version": "2.0",
        "run_id": run_id or default_run_id(stage, source),
        "stage": stage,
        "source": source,
        "repo_commit_sha": repo_sha,
        # Backward-compatible alias for older consumers.
        "commit_sha": repo_sha,
        "config_hash": sha256_json(config_payload),
        "started_at": started,
        "finished_at": finished,
        "timestamp_utc": finished,
        "record_count": int(record_count),
        "input_paths": list(input_paths),
        "output_path": str(out_path),
        "model_family": model_family,
        "model_family_justification": model_family_justification,
        "model_identifier": model_identifier,
        "model_identifier_justification": model_identifier_justification,
        "model_version_snapshot": model_version_snapshot,
        "routing_policy_version": routing_policy_version,
        "search_config_schema_version": search_config_schema_version,
        "elis_package_version": _package_version(),
        "adapter_versions": dict(adapter_versions or _collect_adapter_versions()),
        "tool_versions": {"python": platform.python_version()},
    }
    return write_manifest(manifest, target)
