# HANDOFF.md — PE-OC-21 · Infra Validator Workspace

**Implementer:** prog-impl-codex (CODEX)
**Date:** 2026-02-26
**Branch:** feature/pe-oc-21-infra-val-workspace
**Base branch:** main

---

## Summary

Creates the missing `workspace-infra-val` directory so that `infra-val-codex` and
`infra-val-claude` can receive PE assignments, load rules, and operate. The three
workspace files (`AGENTS.md`, `CLAUDE.md`, `CODEX.md`) define the Infra Validator
role, all mandatory infra-specific checks, the two-stage comment protocol, and the
§5.4 ELIS mount isolation hard limit.

---

## Files Changed

```
A  openclaw/workspaces/workspace-infra-val/AGENTS.md    (199 lines)
A  openclaw/workspaces/workspace-infra-val/CLAUDE.md    (147 lines)
A  openclaw/workspaces/workspace-infra-val/CODEX.md     (139 lines)
```

No existing files modified.

---

## Design Decisions

- **AGENTS.md structure** mirrors `workspace-prog-val/AGENTS.md` with infra-specific
  additions (§3.2 checks 1–8).
- **Infra-specific blocking categories** are enumerated as mandatory named checks,
  not advisory guidelines, to match the acceptance criteria wording ("blocking
  finding" language used throughout).
- **§5.4 hard limit** (ELIS mount isolation) is called out in AGENTS.md, CLAUDE.md,
  and CODEX.md to ensure neither engine can miss it.
- **Two-stage comment protocol** is defined first in AGENTS.md §3.1 so both engines
  see it before the per-check detail.
- **CLAUDE.md / CODEX.md** are mirrors of each other with engine-specific identifiers
  (`infra-val-claude` vs `infra-val-codex`) in Step 0, per the pattern established
  in existing workspaces.

---

## Acceptance Criteria

| # | Criterion | Status |
|---|-----------|--------|
| AC-1 | `workspace-infra-val/AGENTS.md` defines ≥3 infra-specific blocking categories: (a) `0.0.0.0` port binding, (b) ELIS repo path in volumes mount, (c) inline secret in CI workflow | **PASS** |
| AC-2 | `workspace-infra-val/CLAUDE.md` and `CODEX.md` present with engine-specific guidance | **PASS** |
| AC-3 | `scripts/deploy_openclaw_workspaces.sh` deploys new workspace to host without error | **PASS** |
| AC-4 | After deployment + container restart, `check_openclaw_config_sync.py` exits 0 | **PASS** |

---

## Validation Commands

```text
grep -n "blocking finding" openclaw/workspaces/workspace-infra-val/AGENTS.md
63:Any `0.0.0.0:X:X` mapping → **blocking finding**.
77:Any `:latest` tag → **blocking finding**.
99:Any ELIS repo path in a `volumes:` mount → **§5.4 hard limit violation — blocking finding**.
116:Missing `name:` on any job or step → **blocking finding**.
125:Invalid YAML → **blocking finding**.

ls openclaw/workspaces/workspace-infra-val/
AGENTS.md  CLAUDE.md  CODEX.md

bash scripts/deploy_openclaw_workspaces.sh
OpenClaw workspaces deployed to: /c/Users/carlo/openclaw
OpenClaw config deployed to: /c/Users/carlo/.openclaw/openclaw.json (channels/meta preserved)

Restart the container to apply the new config:
  docker compose down && docker compose up -d

docker compose restart && python scripts/check_openclaw_config_sync.py
Container openclaw  Started
Declared agents (13): pm, slr-impl-codex, slr-impl-claude, slr-val-codex, slr-val-claude,
  prog-impl-codex, prog-impl-claude, prog-val-codex, prog-val-claude,
  infra-impl-codex, infra-impl-claude, infra-val-codex, infra-val-claude
Live agents (13): pm, slr-impl-codex, slr-impl-claude, slr-val-codex, slr-val-claude,
  prog-impl-codex, prog-impl-claude, prog-val-codex, prog-val-claude,
  infra-impl-codex, infra-impl-claude, infra-val-codex, infra-val-claude
OK: all declared agents are present in the live container.

python -m black --check .
All done! ✨ 🍰 ✨  118 files would be left unchanged.

python -m ruff check .
All checks passed!

python -m pytest
556 passed, 17 warnings in 6.40s

git diff --name-status origin/main..HEAD
A	openclaw/workspaces/workspace-infra-val/AGENTS.md
A	openclaw/workspaces/workspace-infra-val/CLAUDE.md
A	openclaw/workspaces/workspace-infra-val/CODEX.md
```
