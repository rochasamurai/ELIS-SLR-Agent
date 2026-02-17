# AUDITS.md — Two‑Agent Workflow Audits (CODEX + Claude Code)

This document defines how workflow audits are performed for ELIS SLR Agent v2.0.
Audits are practical, evidence-based, and designed to reduce:
- branch contamination,
- PR conflicts/churn,
- missed acceptance criteria,
- unclear handoffs,
- unnecessary back‑and‑forth with the orchestrator.

---

## 1) Audit objectives

1. **Reduce errors**
2. **Reduce PR conflicts**
3. **Simplify interactions with Carlos**
4. **Make behaviour reproducible** (evidence over narrative)

---

## 2) Audit deliverables

Each agent must create and submit their own report:

- `Audit_Report_Codex.md` (CODEX)
- `Audit_Report_Clauce.md` (Claude Code)

Reports must include:
- pasted command outputs (Status Packet),
- incidents/deviations + root cause,
- minimal, concrete improvements.

Templates are provided in the repo root by default.

---

## 3) Mandatory evidence (“Status Packet”)

Every audit report MUST include:

### 3.1 Repository state
```bash
git fetch --all --prune
git status -sb
git branch --show-current
git rev-parse HEAD
git log -5 --oneline --decorate
```

### 3.2 Scope evidence
```bash
git diff --name-status origin/release/2.0..HEAD
git diff --stat        origin/release/2.0..HEAD
```

### 3.3 Quality gates
```bash
python -m black --check .
python -m ruff check .
python -m pytest -q
```

### 3.4 PR evidence (if applicable)
```bash
gh pr list --state open --base release/2.0
gh pr view <PR_NUMBER>
gh pr checks <PR_NUMBER>
```

---

## 4) Audit execution (recommended)

### 4.1 Use a dedicated audit branch
```bash
git checkout -b chore/audit-codex
# or
git checkout -b chore/audit-claude
```

### 4.2 Add your report file, commit, push, PR
```bash
git add Audit_Report_*.md
git commit -m "chore(audit): add <agent> workflow audit report"
git push -u origin <branch>
gh pr create --base release/2.0 --title "chore(audit): <agent> workflow audit" --body "Adds workflow audit report."
```

---

## 5) Non‑negotiable audit conclusions (if issues found)

If the audit finds any of the following, the report MUST propose a concrete prevention rule:
- working on a dirty tree,
- branch switching conflicts,
- mixed PE changes,
- missing Status Packets,
- validator editing implementer-owned files without necessity.

---

## 6) Recommended prevention: git worktrees

If multiple PEs are active, audits should recommend adopting worktrees.

Example:
```bash
git worktree add ../ELIS_worktrees/pe1a feature/pe1a-manifest-schema
git worktree add ../ELIS_worktrees/pe2  feature/pe2-openalex
```

End of AUDITS.md
