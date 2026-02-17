# AUDIT.md — Two-Agent Workflow Audit (CODEX + Claude Code)

This audit is a lightweight, evidence-based review of how the two-agent workflow is operating in practice for ELIS SLR Agent v2.0, with a focus on preventing:
- branch contamination (mixing work from different PEs),
- PR conflicts and churn,
- missed acceptance criteria,
- unclear handoffs,
- avoidable back-and-forth with the human orchestrator.

This file MUST be read by both agents before producing their audit reports.

---

## 1) Audit Objectives

1. **Reduce errors**  
   Ensure each PE follows the same preflight, gating, and evidence discipline.

2. **Reduce conflicts in PRs**  
   Prevent overlapping edits, especially to canonical files (e.g., HANDOFF/REVIEW), and prevent “hidden” local changes.

3. **Simplify interactions with the human orchestrator**  
   Every agent update must include a consistent “Status Packet” so decisions can be made quickly.

---

## 2) Scope (What’s included)

- Behaviour on existing PEs and branches up to the date of the audit.
- Adherence to roles:
  - **CODEX** = Implementer/Validator
  - **Claude Code** = Validator/Implementer
- Adherence to “one PE = one branch = one PR”.
- Adherence to file ownership:
  - Implementer owns: feature code + PE documentation + `HANDOFF.md`
  - Validator owns: `REVIEW.md` + adversarial tests + minimal scope-safe fixes (only if necessary)

---

## 3) Audit Deliverables (Files to be created)

Each agent must produce and commit their own report file:

- `Audit_Report_Codex.md` (CODEX)
- `Audit_Report_Clauce.md` (Claude Code)

Each report MUST include:
- Evidence outputs (commands + pasted results)
- Deviations / incidents (what went wrong, why, how to prevent)
- Proposed workflow improvements (concrete and minimal)

---

## 4) The “Status Packet” (Mandatory in every agent update)

Whenever an agent reports progress to the orchestrator, they MUST paste the outputs of:

### 4.1 Repository state
```bash
git fetch --all --prune
git status -sb
git branch --show-current
git rev-parse HEAD
git log -5 --oneline --decorate
```

### 4.2 Scope / diff evidence (against release/2.0)
```bash
git diff --name-status origin/release/2.0..HEAD
git diff --stat        origin/release/2.0..HEAD
```

### 4.3 Local quality gates
```bash
python -m black --check .
python -m ruff check .
python -m pytest -q
```

### 4.4 PR state (if applicable)
```bash
gh pr list --state open --base release/2.0
# if a PR exists for this branch:
gh pr view <PR_NUMBER>
gh pr checks <PR_NUMBER>
```

---

## 5) Anti-Error Rules (Hard requirements)

1. **No branch switching with a dirty working tree**  
   If `git status -sb` shows `M` or `??`, stop and clean up before switching branches.

2. **No mixing PEs**  
   If you discover unrelated files in your diff, stop and split work into separate branches/PRs.

3. **No silent local edits**  
   If you made local edits, either commit them (on the correct branch) or isolate them (WIP branch). Avoid stashing unless it is truly temporary.

4. **Handoff must be explicit**  
   The Implementer’s `HANDOFF.md` must list every changed file and show exact validation commands executed.

5. **Validator must not rewrite implementation**  
   The Validator should only:
   - validate against acceptance criteria,
   - add adversarial tests,
   - record a verdict in `REVIEW.md`,
   - apply minimal, scope-safe fixes only if strictly required to meet criteria.

---

## 6) Recommended conflict-avoidance tactic: git worktrees

If you are actively switching between multiple PEs, use worktrees to eliminate checkout conflicts:

```bash
git fetch --all --prune
git worktree add ../ELIS_wt_pe1a feature/pe1a-manifest-schema
git worktree add ../ELIS_wt_pe2  feature/pe2-openalex
```

---

## 7) How to submit the audit

1. Each agent completes their report file (above).
2. Each agent commits their report on the branch they were working on OR on a dedicated audit branch (preferred):
   - `chore/audit-codex`
   - `chore/audit-claude`
3. Open PRs to `release/2.0` with audit reports only.
4. Orchestrator merges audit PRs after review.

End of AUDIT.md
