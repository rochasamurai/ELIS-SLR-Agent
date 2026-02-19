> Rules authority: AGENTS.md. This document is the operational narrative only.
> In any conflict between this file and AGENTS.md, AGENTS.md governs.

# ELIS SLR Agent — Complete Two-Agent Development Workflow
**Post PE-INFRA-03 | VS Code · CODEX · Claude Code**
**Document version:** 2026-02-19
**Supersedes:** inline descriptions in AGENTS.md §5

---

## 0) Overview

This document describes the end-to-end development workflow for the ELIS SLR Agent project
after the three infrastructure PEs (PE-INFRA-01, PE-INFRA-02, PE-INFRA-03) are fully merged.
It is the operational reference for the PM and both agents.

### The three participants

| Participant | Tool | VS Code surface | Default role |
|---|---|---|---|
| **PM** | Human | Observes both panels, merges PRs | Orchestrator |
| **CODEX** | OpenAI Codex VS Code extension (GPT-5.3-Codex) | Left sidebar panel | Implementer |
| **Claude Code** | Anthropic Claude Code VS Code extension | Right sidebar panel | Validator |

### The VS Code workspace layout

```
┌─────────────────┬──────────────────────────┬──────────────────────┐
│  CODEX          │   Open files (editor)     │  Claude Code         │
│  (Implementer)  │                           │  (Validator)         │
│  Left sidebar   │   PE-INFRA-XX.md          │  Right sidebar       │
│                 │   HANDOFF.md              │                       │
│  GPT-5.3-Codex  │   AGENTS.md              │  75% context shown   │
│  Agent mode     │   CURRENT_PE.md           │  in status bar       │
│  Medium effort  │                           │                       │
└─────────────────┴──────────────────────────┴──────────────────────┘
│  Status bar: chore/pe-infra-xx-scope  ◎ 0  ⚠ 0                   │
└───────────────────────────────────────────────────────────────────┘
```

Each active PE branch has its own worktree folder, opened as a separate VS Code
workspace window when two or more PEs run in parallel. A single active PE may
share the main workspace window as shown in the screenshot above.

---

## 1) Infrastructure files (installed by PE-INFRA-01 through PE-INFRA-03)

After all three infrastructure PEs are merged, the following files govern the workflow:

| File | Purpose | Installed by | Status |
|---|---|---|---|
| `CURRENT_PE.md` | Single source of truth: release context + active PE + agent roles | PE-INFRA-02 | ✅ merged |
| `AGENTS.md` | Full operating rules, lifecycle, enforcement | PE-INFRA-02/03 | ✅ merged |
| `CLAUDE.md` | Auto-loaded into every Claude Code session; survives context compression | PE-INFRA-02 | ✅ merged |
| `CODEX.md` | Loaded into CODEX project instructions at session start | PE-INFRA-02 | ✅ merged |
| `scripts/check_role_registration.py` | Validates `CURRENT_PE.md` structure in CI | PE-INFRA-02/03 | ✅ merged |
| `scripts/check_handoff.py` | Validates `HANDOFF.md` section presence in CI | PE-INFRA-01 | ⏳ pending |
| `.pre-commit-config.yaml` | Runs black, ruff, pytest on every local `git commit` | PE-INFRA-01 | ⏳ pending |
| `.github/workflows/ci.yml` | CI: black, ruff, pytest, handoff-check on every PR | PE-INFRA-01 | ⏳ pending |
| `.github/pull_request_template.md` | Pre-fills Status Packet skeleton on every new PR | PE-INFRA-01 | ⏳ pending |
| `docs/templates/HANDOFF_template.md` | HANDOFF.md template with all required sections | PE-INFRA-01 | ⏳ pending |

### CURRENT_PE.md structure (the single source of truth)

```markdown
## Release context
| Field          | Value                             |
|----------------|-----------------------------------|
| Release        | v2.0                              |
| Base branch    | release/2.0                       |
| Plan file      | docs/_active/RELEASE_PLAN_v2.0.md |
| Plan location  | docs/_active/                     |

## Current PE
| Field  | Value                        |
|--------|------------------------------|
| PE     | PE-N                         |
| Branch | feature/peN-scope            |

> **Branch naming convention:** use `feature/peN-<scope>` for code PEs and
> `chore/<topic>` for infrastructure, docs, or config-only PEs.
> Both prefixes are valid; the CI compliance checker accepts either.

## Agent roles
| Agent       | Role        |
|-------------|-------------|
| CODEX       | Implementer |
| Claude Code | Validator   |
```

When the project moves to a new release line, **only this file changes**.
`AGENTS.md`, `CLAUDE.md`, and `CODEX.md` require no edits.

---

## 2) Phase 0 — New release setup (once per release line)

The PM performs this once when a new release begins (v3.0, v4.0, etc.).

```bash
# 1. Update CURRENT_PE.md — Release context table only
#    Edit: Release, Base branch, Plan file, Plan location

# 2. Configure branch protection on the new base branch (GitHub → Settings → Branches)
#    - CI status checks must pass before merge
#    - At least 1 approving review (PM) required
#    - Direct pushes blocked — PRs only

# 3. Commit and push CURRENT_PE.md to the new base branch
git add CURRENT_PE.md
git commit -m "chore: initialise release context for vX.0"
git push origin <new-base-branch>
```

No other workflow file requires editing. The entire agent workflow
resolves the new base branch and plan file from `CURRENT_PE.md` at runtime.

---

## 3) Phase 1 — PE start (repeated for every PE)

**Owner: PM**

```bash
# 1. Edit CURRENT_PE.md — update three fields only:
#    PE identifier, Branch name, Agent roles table (rotate if needed)

# 2. Validate the file is well-formed locally
python scripts/check_role_registration.py
# Expected: "CURRENT_PE.md OK — role registration valid."

# 3. Commit via a small chore PR (base branch is protected — direct push blocked)
git checkout -b chore/open-pe-N origin/$BASE
git add CURRENT_PE.md
git commit -m "chore: open PE-N — assign CODEX=Implementer, ClaudeCode=Validator"
git push -u origin chore/open-pe-N
gh pr create --base $BASE --head chore/open-pe-N \
  --title "chore: open PE-N" --body "Advance CURRENT_PE.md to PE-N."
# Merge the PR, then notify CODEX.

# 4. Notify CODEX:
#    "PE-N is open. You are assigned as Implementer.
#     Read CURRENT_PE.md and send your opening Status Packet before any work."
```

PM waits for CODEX's opening Status Packet. Nothing else proceeds.

---

## 4) Phase 2 — Implementer session (CODEX)

**Owner: CODEX | VS Code: left sidebar panel | Mode: Agent, Medium effort**

### Step 0 — Session start (mandatory, no exceptions)

```bash
# CODEX reads these three files in order before touching anything:
# 1. AGENTS.md          — operating rules
# 2. CURRENT_PE.md      — role confirmation + base branch + plan file
# 3. <plan-file>        — acceptance criteria for this PE (path from CURRENT_PE.md)
```

If `CURRENT_PE.md` is absent or CODEX's name is not listed → stop and notify PM.

### Step 1 — Opening Status Packet to PM

CODEX pastes the following verbatim and waits for PM acknowledgement:

```bash
# §6.1 Working-tree state
git status -sb
git diff --name-status
git diff --stat

# §6.2 Repository state
git fetch --all --prune
git branch --show-current
git rev-parse HEAD
git log -5 --oneline --decorate

# §6.3 Scope evidence
BASE=$(grep "Base branch" CURRENT_PE.md | awk '{print $NF}')
git diff --name-status origin/$BASE..HEAD
git diff --stat        origin/$BASE..HEAD

# §6.4 Quality gates
python -m black --check .
python -m ruff check .
python -m pytest -q

# §6.5 PR evidence
gh pr list --state open --base $BASE
```

**PM must acknowledge before CODEX writes a single line of code.**

### Step 2 — Branch creation

```bash
BASE=$(grep "Base branch" CURRENT_PE.md | awk '{print $NF}')
git fetch origin
git checkout -b feature/peN-scope origin/$BASE
git status -sb
# Expected: nothing to commit, clean tree
```

### Step 3 — Implementation

CODEX implements **only** the PE acceptance criteria. No unrelated changes.
CODEX's IDE context is enabled so open files and selections are automatically
included in its context — the center panel shows the files being edited in real time.

### Step 4 — Mid-session checkpoint (before every `git commit`)

```bash
# 1. Re-read CURRENT_PE.md → Plan file field → re-read PE acceptance criteria
# 2. Confirm role in CURRENT_PE.md has not changed
# 3. Run scope gate:
BASE=$(grep "Base branch" CURRENT_PE.md | awk '{print $NF}')
git diff --name-status origin/$BASE..HEAD
# Verify: only PE-scope files appear. If unrelated files show → stop, do not commit.
```

The pre-commit hooks (installed by PE-INFRA-01) run automatically on `git commit`:
- `python -m black --check .`
- `python -m ruff check .`
- `python -m pytest tests/ -q --tb=short`

Any hook failure blocks the commit. CODEX fixes before retrying.

### Step 5 — HANDOFF.md

```bash
# Copy the template
cp docs/templates/HANDOFF_template.md HANDOFF.md

# Fill in all five sections:
# ## Summary            — what this PE does and why
# ## Files Changed      — every file added/modified/deleted
# ## Design Decisions   — non-obvious choices
# ## Acceptance Criteria — each AC from plan file, marked PASS/FAIL
# ## Validation Commands — verbatim gate outputs, no paraphrase
```

HANDOFF.md must be **committed on the feature branch before `git push`**.
This is a hard rule (AGENTS.md §2.7). The CI `handoff-check` job enforces it.

### Step 6 — Session-end check and push

```bash
git status -sb
# Must show: nothing to commit, working tree clean
# If M or ?? appear → commit or WIP-commit before stopping

BASE=$(grep "Base branch" CURRENT_PE.md | awk '{print $NF}')
git push origin feature/peN-scope

gh pr create \
  --base $BASE \
  --head feature/peN-scope \
  --title "feat(peN): short description" \
  --body "$(cat .github/pull_request_template.md)"
```

### Step 7 — Closing Status Packet to PM

CODEX posts the full §6.1–§6.5 Status Packet and writes:

> "PE-N implementation complete. Requesting PM assignment of Validator."

**CODEX then stops. It does not continue working.**

---

## 5) Phase 3 — PM Gate 1 (before validation begins)

**Owner: PM**

PM checks four things before assigning the Validator:

| Check | How |
|---|---|
| Scope diff matches PE requirements | Read `git diff --name-status` in Status Packet |
| Quality gates all passed | Confirm black / ruff / pytest outputs in Status Packet |
| `HANDOFF.md` is committed on the branch | Visible in CI `handoff-check` job result |
| CI is green | GitHub PR checks all passing |

**If anything is missing:** PM sends CODEX a list of required fixes.
CODEX fixes and delivers an updated Status Packet. PM does not assign Validator until clean.

**When satisfied**, PM posts a single comment on the PR:

```
@claude-code — assigned as Validator. Begin review.
```

This PR comment is the **binding authorisation signal**. The Validator does not start without it.

---

## 6) Phase 4 — Validator session (Claude Code)

**Owner: Claude Code | VS Code: right sidebar panel | Context: CLAUDE.md auto-loaded**

### Step 0 — Session start (mandatory, no exceptions)

Claude Code's `CLAUDE.md` is auto-loaded at every session start and survives context
compression. It instructs Claude Code to:

1. Read `AGENTS.md` fully.
2. Read `CURRENT_PE.md` → confirm role is Validator, resolve base branch and plan file.
3. Read `HANDOFF.md` on the active branch.
4. Confirm PM authorisation exists (PR comment). If absent → do not start, notify PM.

### Step 1 — Refuse if Status Packet is missing

If CODEX's Status Packet is absent or incomplete, Claude Code notifies PM and waits.
It does not begin validation without a complete packet.

### Step 2 — Scope verification (blocking)

```bash
BASE=$(grep "Base branch" CURRENT_PE.md | awk '{print $NF}')
git diff --name-status origin/$BASE..HEAD
```

Output must **exactly match** the files declared in `HANDOFF.md`.
Any mismatch — file in diff but not in HANDOFF, or vice versa — is an immediate
**blocking finding**. Claude Code does not proceed past this check until resolved.

### Step 3 — Acceptance criteria validation

Claude Code validates each AC **verbatim** from the plan file (path from `CURRENT_PE.md`).
Not from HANDOFF.md. Not from memory. From the authoritative plan file.

### Step 4 — Adversarial tests

Claude Code adds tests in `tests/test_peN_*.py` covering:
- Schema rejection (missing fields, wrong types, boundary values)
- Determinism / idempotence
- Invalid inputs / edge cases specific to this PE

### Step 5 — Full quality gates

```bash
python -m black --check .
python -m ruff check .
python -m pytest -q
```

All outputs pasted verbatim. No paraphrase.

### Step 6 — Verdict

Claude Code writes `REVIEW_PEN.md` using the standard format:

```
## Agent update — Claude Code / PE-N / <date>

### Verdict
PASS / FAIL

### Branch / PR
Branch: feature/peN-scope
PR: #NNN (open)
Base: <base-branch>

### Gate results
black: PASS / FAIL
ruff:  PASS / FAIL
pytest: N passed, M failed (M pre-existing)
PE-specific tests: N/N passed

### Scope (diff vs base branch)
<paste git diff --name-status output>

### Required fixes (if FAIL)
- <minimal description of each blocking finding>

### Ready to merge
YES / NO — reason if NO
```

Claude Code pushes `REVIEW_PEN.md` + adversarial tests to the **same branch**
(validator-owned files only). It then delivers the verdict in **two forms**:

1. **PR comment** — posts the verdict summary directly on the PR so PM and CODEX
   can read it without navigating to files. Minimum content:
   - PASS: one-line summary + "Ready to merge."
   - FAIL: bulleted list of each blocking finding + "CODEX: fix items above before re-requesting review."

2. **Formal GitHub PR review** — in addition to the comment:
   - `approve` for PASS
   - `request-changes` for FAIL

The PR comment is the **readable handshake**; the formal review is the **branch-protection signal** that blocks or allows merge.

### Step 7 — Closing Status Packet to PM

Claude Code delivers the full §6.1–§6.5 Status Packet and stops.

> Context usage is visible in the VS Code status bar (e.g. "75% used").
> At high context usage, `CLAUDE.md` ensures rules remain active even if
> conversation history is compressed.

---

## 7) Phase 5 — PM Gate 2 (merge or iteration)

**Owner: PM**

### If PASS

```bash
# PM merges the PR on GitHub (branch protection enforces CI green + 1 approval)
# Then updates CURRENT_PE.md for the next PE:
BASE=$(grep "Base branch" CURRENT_PE.md | awk '{print $NF}')
# Edit: PE, Branch, and Agent roles fields
git add CURRENT_PE.md
git commit -m "chore: close PE-N, open PE-N+1"
git push origin $BASE
```

### If FAIL

PM reads `REVIEW_PEN.md`, then posts a PR comment assigning CODEX to fix:

```
@codex — FAIL verdict on PR #NNN. Fix blocking findings in REVIEW_PEN.md.
Deliver updated Status Packet when done.
```

The workflow re-enters **Phase 2**. CODEX reads `REVIEW_PEN.md`, implements
**only** the listed fixes (no scope creep), updates HANDOFF.md, delivers a new
Status Packet. PM re-assigns Claude Code. Claude Code appends a **new dated section**
to `REVIEW_PEN.md` — it never overwrites prior findings — and issues a new verdict.

If more than two FAIL/fix iterations occur, PM triggers an audit (AGENTS.md §7).

---

## 8) Phase 6 — Post-merge hygiene

After any PR merges to the base branch:

```bash
# Every active feature branch must rebase before continuing
BASE=$(grep "Base branch" CURRENT_PE.md | awk '{print $NF}')
git fetch origin
git rebase origin/$BASE

# Check drift
git merge-base origin/$BASE HEAD
# If this returns the tip of the base branch, the branch is current.

# Remove merged worktree
git worktree remove ../ELIS_worktrees/peN
git worktree list
```

---

## 9) Parallel PE management (worktrees)

When two or more PEs are active simultaneously:

```bash
git fetch --all --prune
mkdir -p ../ELIS_worktrees

# Create one worktree per active PE
git worktree add ../ELIS_worktrees/peN  feature/peN-scope
git worktree add ../ELIS_worktrees/peM  feature/peM-scope

# Open each in its own VS Code window
# Each window has the three-panel layout: CODEX left, files centre, Claude Code right
code ../ELIS_worktrees/peN
code ../ELIS_worktrees/peM

# Remove when PE is merged
git worktree remove ../ELIS_worktrees/peN
```

Each window operates on its own branch directory. CODEX and Claude Code each read
`CURRENT_PE.md` from their own worktree, so role assignment is unambiguous even
when multiple PEs are open simultaneously — as long as the PM updates
`CURRENT_PE.md` correctly per PE.

---

## 10) Full workflow at a glance

```
ONE TIME PER RELEASE
─────────────────────────────────────────────────────────────────────
PM edits CURRENT_PE.md (Release context) → commits to base branch
PM configures branch protection on GitHub
└─► Entire workflow is now release-agnostic


FOR EVERY PE
─────────────────────────────────────────────────────────────────────

  PM: update CURRENT_PE.md (PE + Branch + Roles) → commit → notify CODEX
          │
          ▼
  CODEX:  Step 0 → read CURRENT_PE.md → confirm Implementer role
          Opening Status Packet → wait for PM ack
          Create branch → implement → mid-session checkpoints
          Quality gates → HANDOFF.md → push → open PR
          Closing Status Packet → request Validator assignment → STOP
          │
          ▼
  PM Gate 1: review Status Packet → CI green → post PR comment assigning Validator
          │
          ▼
  Claude Code: CLAUDE.md auto-loaded → read CURRENT_PE.md → confirm Validator role
               Scope check (blocking) → validate ACs from plan file
               Adversarial tests → quality gates → REVIEW_PEN.md
               GitHub PR review (approve / request-changes) → Status Packet → STOP
          │
          ├─► PASS: PM merges → update CURRENT_PE.md for next PE → loop
          │
          └─► FAIL: PM assigns CODEX to fix → CODEX fixes → re-validate → loop
                    (> 2 iterations → PM triggers audit)
```

---

## 11) What changed after PE-INFRA-03 specifically

| Before PE-INFRA-01/02/03 | After all three infrastructure PEs |
|---|---|
| AGENTS.md provided manually by user each session | `CLAUDE.md` auto-loaded; `CODEX.md` in project instructions |
| Agents guessed their role from rotation rule | Agents read `CURRENT_PE.md` at Step 0 — structural, not advisory |
| Role forgotten after context compression | Mid-session checkpoint re-reads `CURRENT_PE.md` at every commit |
| `release/2.0` hardcoded in 20+ places | All workflow files resolve base branch from `CURRENT_PE.md` at runtime |
| New release required editing multiple files | New release = edit `CURRENT_PE.md` once, push once |
| No CI check for HANDOFF.md | `handoff-check` CI job blocks merge if sections are missing |
| No pre-commit hooks | black + ruff + pytest run on every local commit |
| Role registration unvalidated | `check_role_registration.py` validates `CURRENT_PE.md` in CI |

---

*End of ELIS_WORKFLOW_POST_PE-INFRA-03.md*
