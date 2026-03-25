"""check_workspace_completeness.py

Validates that every workspace declared in openclaw/openclaw.json has a
corresponding directory under openclaw/workspaces/ and contains at least
an AGENTS.md file.

Also checks that implementer and validator agents within each domain use
separate workspace directories (segmentation rule).

Exit 0 on clean, non-zero on any finding.
"""

from __future__ import annotations

import json
import pathlib
import sys
from typing import List

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
CONFIG_PATH = REPO_ROOT / "openclaw" / "openclaw.json"
WORKSPACES_DIR = REPO_ROOT / "openclaw" / "workspaces"

PM_REQUIRED_FILES = ["AGENTS.md", "MEMORY.md", "SOUL.md"]
STANDARD_REQUIRED_FILES = ["AGENTS.md", "CLAUDE.md", "CODEX.md"]
PHASE_WORKSPACES = {
    "workspace-slr-harvest",
    "workspace-slr-screen",
    "workspace-slr-extract",
    "workspace-slr-synth",
    "workspace-slr-prisma",
}
PHASE_DOMAINS = {"harvest", "screen", "extract", "synth", "prisma"}
GENERIC_SLR_WORKSPACES = {"workspace-slr-impl", "workspace-slr-val"}
REQUIRED_SLR_PHASE_IDS = {
    "harvest-impl-codex",
    "harvest-val-claude",
    "screen-impl-claude",
    "screen-val-codex",
    "extract-impl-codex",
    "extract-val-claude",
    "synth-impl-claude",
    "synth-val-codex",
    "prisma-impl-claude",
    "prisma-val-codex",
}
LEGACY_SLR_IDS = {
    "slr-impl-codex",
    "slr-impl-claude",
    "slr-val-codex",
    "slr-val-claude",
}


def _load_agents(config_path: pathlib.Path) -> list[dict]:
    if not config_path.exists():
        print(f"ERROR: {config_path} not found", file=sys.stderr)
        sys.exit(1)
    data = json.loads(config_path.read_text(encoding="utf-8"))
    return data.get("agents", {}).get("list", [])


def check_workspace_presence(agents: list[dict]) -> List[str]:
    """Every declared workspace must exist as a directory under openclaw/workspaces/."""
    errors = []
    seen: dict[str, str] = {}  # workspace_name → agent_id (first seen)
    for agent in agents:
        workspace = agent.get("workspace", "")
        agent_id = agent.get("id", "<unknown>")
        ws_name = workspace.split("/")[-1] if "/" in workspace else workspace
        if ws_name in seen:
            continue  # shared workspace already checked
        seen[ws_name] = agent_id
        ws_dir = WORKSPACES_DIR / ws_name
        if not ws_dir.is_dir():
            errors.append(
                f"workspace '{ws_name}' declared by agent '{agent_id}' "
                f"does not exist at {ws_dir}"
            )
    return errors


def check_required_files(agents: list[dict]) -> List[str]:
    """Every existing workspace directory must contain each required file."""
    errors = []
    seen: set[str] = set()
    for agent in agents:
        workspace = agent.get("workspace", "")
        ws_name = workspace.split("/")[-1] if "/" in workspace else workspace
        if ws_name in seen:
            continue
        seen.add(ws_name)
        ws_dir = WORKSPACES_DIR / ws_name
        if not ws_dir.is_dir():
            continue  # already reported by check_workspace_presence
        required_files = (
            PM_REQUIRED_FILES if ws_name == "workspace-pm" else STANDARD_REQUIRED_FILES
        )
        for required in required_files:
            if not (ws_dir / required).is_file():
                errors.append(
                    f"workspace '{ws_name}' is missing required file '{required}'"
                )
    return errors


def check_segmentation(agents: list[dict]) -> List[str]:
    """
    Infrastructure and programs domains require separate impl/val workspaces.
    Phase-specialized SLR domains intentionally use one shared workspace per phase.

    A domain is inferred from the agent ID prefix:
      infra-impl-* / infra-val-*  → domain 'infra'
      prog-impl-* / prog-val-*    → domain 'prog'
      harvest-impl-* / harvest-val-* → shared phase workspace
    """
    errors = []
    # build domain → {role → set of workspace names}
    domain_map: dict[str, dict[str, set[str]]] = {}
    for agent in agents:
        agent_id = agent.get("id", "")
        workspace = agent.get("workspace", "")
        ws_name = workspace.split("/")[-1] if "/" in workspace else workspace
        parts = agent_id.split("-")
        # expect pattern: <domain>-<role>-<engine>
        if len(parts) < 3:
            continue
        domain, role = parts[0], parts[1]
        domain_map.setdefault(domain, {}).setdefault(role, set()).add(ws_name)

    for domain, roles in domain_map.items():
        if "impl" not in roles or "val" not in roles:
            continue
        impl_ws = roles["impl"]
        val_ws = roles["val"]
        overlap = impl_ws & val_ws
        if domain in PHASE_DOMAINS:
            if not overlap:
                errors.append(
                    f"domain '{domain}': implementer and validator must share one phase workspace"
                )
            continue
        if overlap:
            errors.append(
                f"domain '{domain}': implementer and validator share workspace(s): "
                + ", ".join(sorted(overlap))
            )
    return errors


def check_slr_phase_cutover(agents: list[dict]) -> List[str]:
    """Ensure the runtime has fully moved from generic to phase-specific SLR agents."""
    agent_ids = {agent.get("id", "") for agent in agents}
    workspaces = {
        (
            agent.get("workspace", "").split("/")[-1]
            if "/" in agent.get("workspace", "")
            else agent.get("workspace", "")
        )
        for agent in agents
    }
    errors = []

    missing_phase_ids = sorted(REQUIRED_SLR_PHASE_IDS - agent_ids)
    if missing_phase_ids:
        errors.append(
            "missing phase-specialized SLR agent IDs: " + ", ".join(missing_phase_ids)
        )

    stale_ids = sorted(LEGACY_SLR_IDS & agent_ids)
    if stale_ids:
        errors.append(
            "legacy generic SLR agent IDs still present: " + ", ".join(stale_ids)
        )

    missing_phase_workspaces = sorted(PHASE_WORKSPACES - workspaces)
    if missing_phase_workspaces:
        errors.append(
            "missing phase-specialized SLR workspaces: "
            + ", ".join(missing_phase_workspaces)
        )

    stale_workspaces = sorted(GENERIC_SLR_WORKSPACES & workspaces)
    if stale_workspaces:
        errors.append(
            "legacy generic SLR workspaces still declared: "
            + ", ".join(stale_workspaces)
        )

    return errors


def main() -> int:
    agents = _load_agents(CONFIG_PATH)
    if not agents:
        print("ERROR: agents.list is empty", file=sys.stderr)
        return 1

    all_errors: List[str] = []
    all_errors.extend(check_workspace_presence(agents))
    all_errors.extend(check_required_files(agents))
    all_errors.extend(check_segmentation(agents))
    all_errors.extend(check_slr_phase_cutover(agents))

    if all_errors:
        for err in all_errors:
            print(f"FAIL: {err}", file=sys.stderr)
        return 1

    ws_names = sorted(
        {
            (
                a.get("workspace", "").split("/")[-1]
                if "/" in a.get("workspace", "")
                else a.get("workspace", "")
            )
            for a in agents
        }
    )
    print(
        f"OK: {len(agents)} agents, {len(ws_names)} workspace(s) — "
        "all present, all files complete, segmentation clean"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
