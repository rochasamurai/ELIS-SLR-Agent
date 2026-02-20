"""check_agent_scope.py — scan worktree for secret-pattern files.

Reads .agentignore from repo root, expands each pattern via glob,
and reports any real files that match. Lines starting with '!' are
negation patterns (whitelist), mirroring .gitignore semantics.
Exits 1 if violations found, 0 if clean.

Run in CI on every PR and locally at Step 0 of every agent session.
"""

import glob
import sys
from pathlib import Path


def _load_patterns(
    agentignore: Path,
) -> tuple[list[str], list[str]]:
    """Return (deny_patterns, allow_patterns) from .agentignore."""
    deny: list[str] = []
    allow: list[str] = []
    if not agentignore.exists():
        return deny, allow
    for line in agentignore.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("!"):
            allow.append(stripped[1:])
        else:
            deny.append(stripped)
    return deny, allow


def _expand(repo_root: Path, pattern: str) -> list[str]:
    # Directory-only patterns (e.g. "secrets/") must also scan their contents.
    base = glob.glob(str(repo_root / pattern), recursive=True)
    suffix = pattern.rstrip("/")
    if pattern.endswith("/"):
        base += glob.glob(str(repo_root / suffix / "**"), recursive=True)
    return base


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    agentignore = repo_root / ".agentignore"

    deny_patterns, allow_patterns = _load_patterns(agentignore)
    if not deny_patterns:
        print("Agent scope clean — no secret-pattern files detected in worktree.")
        return 0

    # Collect whitelisted paths
    allowed: set[str] = set()
    for pat in allow_patterns:
        for match in _expand(repo_root, pat):
            p = Path(match)
            if p.is_file():
                allowed.add(str(p.relative_to(repo_root)))

    violations: list[str] = []
    for pattern in deny_patterns:
        for match in _expand(repo_root, pattern):
            p = Path(match)
            if p.is_file():
                rel = str(p.relative_to(repo_root))
                if rel not in allowed:
                    violations.append(rel)

    if violations:
        print("WARNING: The following secret-pattern files exist in the worktree:")
        for v in sorted(set(violations)):
            print(f"  {v}")
        print("Agents must not read these files. Verify IDE context excludes them.")
        return 1

    print("Agent scope clean — no secret-pattern files detected in worktree.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
