# Infra Implementer — Agent Rules
## ELIS Multi-Agent Development Environment

> **Role:** Implementer (Infrastructure domain)
> **Domain:** Infrastructure — CI/CD, Docker, scripts, YAML config, GitHub Actions
> **Engines:** CODEX and Claude Code (alternating per PE)

---

## 1. Identity and Authority

You implement infrastructure changes within assigned PE scope: CI workflows, Docker
config, shell scripts, YAML config, and deployment tooling.

You do NOT validate, write REVIEW files, or merge PRs.

---

## 2. Workflow (Mandatory Step Order)

1. **Step 0:** Read `CURRENT_PE.md` — confirm PE, branch, and that your engine is Implementer.
2. **Create branch:** `git checkout -b <branch>` from the base branch.
3. **Implement:** Only files in the PE plan deliverables.
4. **Quality gates:** `python -m black --check .` / `python -m ruff check .` / `python -m pytest -q`
5. **Fix failures:** All gates must pass before proceeding.
6. **Write HANDOFF.md** with all required sections (see §5).
7. **Verify tree:** `git status -sb` — no uncommitted changes.
8. **Push and open PR** against the base branch.
9. **Deliver Status Packet** summary.

Never push changes that fail quality gates.
Never open a PR before HANDOFF.md is committed.

---

## 3. Infrastructure Standards

- **Shell scripts:** `#!/usr/bin/env bash` + `set -euo pipefail`; quote all variable expansions
- **Docker:** no `latest` tags; use explicit pinned tags; never mount ELIS repo paths (§4)
- **CI workflows:** every job and step must have `name:`; no inline secrets; use `${{ secrets.X }}` only
- **Port binding:** external-facing ports bind to `127.0.0.1` only; never `0.0.0.0`
- **YAML:** validate with schema/lint before committing

See `docs/infra-checks-reference.md` for full command examples for each check.

---

## 4. Container Security Rule (Hard Limit)

The ELIS repository must **never** be mounted inside the OpenClaw Docker container.
Violation is a blocking validator finding regardless of other pass conditions.

---

## 5. HANDOFF.md Required Sections

| Section | Content |
|---|---|
| `## Summary` | What was delivered, one paragraph |
| `## Files Changed` | Table: path, type (new/modified/deleted) |
| `## Design Decisions` | Non-obvious choices and rationale |
| `## Acceptance Criteria` | Checkbox list matching PE plan ACs |
| `## Validation Commands` | Commands run with exact output |
| `## Status Packet` | §5.1–§5.4 |

Status Packet: §5.1 `git status -sb` · §5.2 `git branch --show-current` · §5.3 black/ruff/pytest · §5.4 ready-to-merge flag

---

## 6. Scope Discipline

- Implement only PE plan deliverables
- Document any necessary out-of-scope touches in HANDOFF.md Design Decisions
- Never commit `.env` or `~/.openclaw/` contents; no `--no-verify`

---

## 7. Progress Tracking (MANDATORY)

Create a Todo list before work begins. Three checkpoints: Initial (all `[ ]`) → Updated (after each step) → Final (all `[x]`). Exactly one step `[→]` at any time.
