# Agent Development Guide (AGENTS.md)

This file defines the **two‑agent development workflow** for **ELIS SLR Agent — Release Plan v2.0**.
It is mandatory for all **PEs** targeting the `release/2.0` line.

**Agents**
- **CODEX** (default: Implementer)
- **Claude Code** (default: Validator)

> Roles may rotate per PE if explicitly stated in the PE plan/assignment. If not stated, assume CODEX=Implementer and Claude Code=Validator.

---

## 0) Glossary (quick)

- **PE**: Planned Execution step in `RELEASE_PLAN_v2.0.md` (e.g., PE0a, PE1a, PE2…)
- **Implementer**: writes/changes product code + PE handoff documentation
- **Validator**: verifies acceptance criteria, adds adversarial tests, issues verdict in `REVIEW.md`
- **Status Packet**: the standard evidence bundle pasted to Carlos on every update
- **Worktree**: a separate working directory for a branch to avoid checkout conflicts and cross‑PE contamination

---

## 1) Canonical references (read first)

Before starting any work on a PE, every agent MUST read:

1. `docs/_active/RELEASE_PLAN_v2.0.md` (authoritative plan + acceptance criteria)
2. Any PE‑specific design notes referenced by the release plan
3. On the PE branch:
   - `HANDOFF.md` (Implementer) **or**
   - `REVIEW.md` (Validator)
4. `AUDITS.md` (audit expectations + report templates)

---

## 2) Operating rules (hard requirements)

### 2.1 One PE = one branch = one PR
- Every PE is implemented on its own feature branch created from `release/2.0`.
- The PR base is `release/2.0` unless the release plan explicitly states otherwise.

### 2.2 Clean working tree before any context switch
- **Do not switch branches in a dirty tree.**
- If `git status -sb` shows `M` or `??`, stop and clean up first:
  - commit on the correct branch **or**
  - move changes to a dedicated WIP branch **or**
  - (temporary only) stash, then immediately re‑apply to the correct branch.

### 2.3 File ownership
- Implementer owns:
  - all PE code changes
  - `HANDOFF.md`
  - non‑test deliverables declared in the PE
- Validator owns:
  - `REVIEW.md`
  - adversarial tests
  - minimal scope‑safe fixes **only if strictly required** to satisfy acceptance criteria

### 2.4 Evidence-first reporting (no “trust me”)
- Every agent update to Carlos MUST include the **Status Packet** (Section 6).
- If a claim is not supported by command output, it is not considered done.

---

## 3) Recommended practice: use git worktrees for active PEs

### 3.1 Why worktrees
Worktrees prevent:
- checkout failures (“local changes would be overwritten”),
- branch contamination (PE1 edits leaking into PE2),
- agent collisions on shared files (e.g., `HANDOFF.md` / `REVIEW.md`).

### 3.2 When to use
Use a worktree when **two or more PEs are active in parallel**, or when:
- a PE has an open PR and may need follow‑up fixes,
- Implementer and Validator are working concurrently on different branches.

### 3.3 Worktree rule
**If a PE is active, it should have its own worktree folder and its own VS Code window.**
Avoid “in‑place checkout” switching between active PE branches.

### 3.4 Commands (Windows / PowerShell friendly)
From the *main* repo folder:

```bash
git fetch --all --prune
mkdir -p ../ELIS_worktrees

# Example: create worktrees for active PEs
git worktree add ../ELIS_worktrees/pe1a feature/pe1a-manifest-schema
git worktree add ../ELIS_worktrees/pe2  feature/pe2-openalex
```

Open each worktree in its own VS Code window:

```bash
code ../ELIS_worktrees/pe1a
code ../ELIS_worktrees/pe2
```

When a PE is merged/closed:

```bash
git worktree remove ../ELIS_worktrees/pe1a
```

List worktrees:

```bash
git worktree list
```

---

## 4) Branch naming and PR conventions

### 4.1 Branch naming
Use one of:
- `feature/pe<id>-<short-scope>` (e.g., `feature/pe1a-manifest-schema`)
- `chore/<topic>` for non‑PE housekeeping (only if authorised)

### 4.2 PR naming
PR title format (recommended):
- `PE1a: Run manifest schema + writer utility`
- `PE2: OpenAlex stream adapters (CrossRef/OpenAlex/Scopus)`

### 4.3 PR creation (gh)
From the PE worktree:

```bash
gh pr create --base release/2.0 --head <branch> --title "PE1a: ..." --body-file HANDOFF.md
```

Validator updates can be pushed to the same branch; verdict goes to `REVIEW.md`.

---

## 5) PE lifecycle (step-by-step)

### 5.1 Implementer workflow (CODEX unless rotated)
1. **Preflight**: paste Status Packet to Carlos before starting (Section 6).
2. Create branch from `release/2.0` (or confirm it is correct).
3. Implement only the PE acceptance criteria.
4. Run local gates (`black`, `ruff`, `pytest`).
5. Update `HANDOFF.md`:
   - summary
   - complete file list
   - design decisions
   - acceptance criteria checklist + PASS/FAIL
   - exact validation commands run
6. Push branch + open PR to `release/2.0`.
7. Ask Validator to run validation.

### 5.2 Validator workflow (Claude Code unless rotated)
1. **Refuse validation if the Status Packet is missing**.
2. Read `HANDOFF.md` and verify scope matches `git diff --name-status`.
3. Validate acceptance criteria *verbatim* from `RELEASE_PLAN_v2.0.md`.
4. Add adversarial tests to cover:
   - schema rejection cases (missing fields, wrong types, boundaries)
   - determinism / idempotence
   - invalid inputs / edge cases
5. Run gates (`black`, `ruff`, `pytest`).
6. Update `REVIEW.md` with:
   - verdict PASS/FAIL
   - evidence summary (commands + outcomes)
   - non‑blocking observations
   - required fixes (if FAIL), with minimal scope guidance
7. Push validation commits to the same branch (only scope-safe changes).

---

## 6) Status Packet (mandatory in every update)

Paste command outputs exactly (no paraphrase). Run from the relevant worktree.

### 6.1 Repository state
```bash
git fetch --all --prune
git status -sb
git branch --show-current
git rev-parse HEAD
git log -5 --oneline --decorate
```

### 6.2 Scope evidence (against release/2.0)
```bash
git diff --name-status origin/release/2.0..HEAD
git diff --stat        origin/release/2.0..HEAD
```

### 6.3 Quality gates
```bash
python -m black --check .
python -m ruff check .
python -m pytest -q
```

### 6.4 PR evidence (if applicable)
```bash
gh pr list --state open --base release/2.0
# if you have a PR:
gh pr view <PR_NUMBER>
gh pr checks <PR_NUMBER>
```

---

## 7) Audit feature (AUDITS.md)

The project uses lightweight workflow audits to reduce churn and prevent repeated mistakes.

### 7.1 When audits run
- Triggered by Carlos when:
  - repeated checkout conflicts occur,
  - PR scope contamination is detected,
  - agent role boundaries are breached,
  - or at major milestones.

### 7.2 What audits produce
Each agent writes a report file and submits it via PR:

- `Audit_Report_Codex.md`
- `Audit_Report_Clauce.md` (spelling retained for compatibility)

See `AUDITS.md` for the full audit spec and report templates.

---

## 8) Minimal “do not do” list
- Do not switch branches with local edits in the same folder.
- Do not “helpfully” refactor unrelated code while inside a PE.
- Do not touch `REVIEW.md` unless you are the Validator.
- Do not declare PASS without the gates and the evidence outputs.

End of AGENTS.md
