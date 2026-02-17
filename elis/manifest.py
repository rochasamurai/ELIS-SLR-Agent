"""Run manifest writer utility for PE1a."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping


def write_manifest(manifest: Mapping[str, Any], manifest_path: str | Path) -> Path:
    """Write a manifest JSON sidecar file and return its path."""
    target = Path(manifest_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(dict(manifest), ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return target
