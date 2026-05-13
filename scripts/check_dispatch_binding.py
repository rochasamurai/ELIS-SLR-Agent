#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

AGENT_WORKTREE_MAP = {
    "pm": "/opt/elis/agent-worktrees/pm",
    "infra-impl-a": "/opt/elis/agent-worktrees/infra-impl-a",
    "infra-impl-b": "/opt/elis/agent-worktrees/infra-impl-b",
    "infra-val-a": "/opt/elis/agent-worktrees/infra-val-a",
    "infra-val-b": "/opt/elis/agent-worktrees/infra-val-b",
    "github-agent": "/opt/elis/agent-worktrees/github-agent",
    "infra-impl-claude": "/opt/elis/agent-worktrees/infra-impl-b",
    "infra-val-claude": "/opt/elis/agent-worktrees/infra-val-a",
    "infra-impl-codex": "/opt/elis/agent-worktrees/infra-impl-a",
    "infra-val-codex": "/opt/elis/agent-worktrees/infra-val-b",
}

_PRESERVED_CONTEXT_FILES = {
    "AGENTS.md",
    "HEARTBEAT.md",
    "IDENTITY.md",
    "SOUL.md",
    "TOOLS.md",
    "USER.md",
}


def git(cmd: list[str], cwd: Path) -> str:
    return subprocess.check_output(["git", *cmd], cwd=cwd, text=True).strip()


def _is_pe_specific_runtime(path: str) -> bool:
    parts = Path(path).parts
    return any(part.startswith("PE-") for part in parts)


def _is_untracked_or_dirty(path: str) -> tuple[bool, str]:
    rel = Path(path)
    if str(rel) == ".openclaw" or str(rel).startswith(".openclaw/"):
        return True, "preserved runtime/context root"
    if rel.name in _PRESERVED_CONTEXT_FILES and len(rel.parts) == 1:
        return True, "preserved runtime/context file"
    return False, "not protected"


def _legacy_agent_check(agent: str) -> int:
    print(f"Agent: {agent}")
    worktree = AGENT_WORKTREE_MAP.get(agent)
    if not worktree:
        print(f"Unknown agent ID: {agent}")
        return 1
    if not Path(worktree).exists():
        return 1
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description="Check PE dispatch binding")
    p.add_argument("--repo", default=".")
    p.add_argument("--agent")
    p.add_argument("--pe-id")
    p.add_argument("--branch")
    p.add_argument("--head")
    p.add_argument("--worktree")
    p.add_argument(
        "--mode", choices=["implementer", "validator"], default="implementer"
    )
    args = p.parse_args()
    if args.agent:
        return _legacy_agent_check(args.agent)
    if not args.pe_id or not args.head or not args.worktree:
        p.error("the following arguments are required: --pe-id, --head, --worktree")
    repo = Path(args.repo).resolve()
    worktree = Path(args.worktree).resolve()
    if git(["rev-parse", "--show-toplevel"], repo) != str(repo):
        print("WORKTREE_MISMATCH: repo root mismatch", file=sys.stderr)
        return 2
    current_branch = git(["branch", "--show-current"], worktree)
    if args.mode == "implementer":
        if not args.branch:
            print("MISSING_BRANCH", file=sys.stderr)
            return 3
        if current_branch != args.branch:
            print("WRONG_BRANCH", file=sys.stderr)
            return 3
    else:
        if current_branch:
            print("EXPECTED_DETACHED_HEAD", file=sys.stderr)
            return 3
    if git(["rev-parse", "HEAD"], worktree) != args.head:
        print("WRONG_HEAD", file=sys.stderr)
        return 4
    if git(["status", "--short", "--untracked-files=no"], worktree):
        print("DIRTY_WORKTREE", file=sys.stderr)
        return 5
    pe_task = repo / ".elis" / "pe" / args.pe_id / "PE_TASK.md"
    if not pe_task.exists():
        print("MISSING_PE_TASK", file=sys.stderr)
        return 6
    print(f"OK {args.pe_id} {args.branch} {args.head}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
