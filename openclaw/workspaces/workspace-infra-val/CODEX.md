# CODEX.md — workspace-infra-val (CODEX Workflow Rules)
> Load into CODEX project instructions or paste at session start.
> Mirrors CLAUDE.md. Treat every rule as always active.

---

## Role
Fixed role in this workspace: **Validator**
(unless `CURRENT_PE.md` explicitly states otherwise for a rotation)

---

## Step 0 — Session start (mandatory before any action)
1. Read `AGENTS.md` in this workspace (full).
2. Read `CURRENT_PE.md` at repo root:
   - Confirm `infra-val-codex` appears in the `Agent roles` table.
   - Note `Base branch` and `Plan file`.
   - If either is blank or your agent ID is absent → stop, notify PM.
3. Read `HANDOFF.md` on the active feature branch.
4. Wait for explicit PM assignment before beginning review.
   Signal: PM PR comment or CI Gate 1 comment assigning `infra-val-codex`.
   Do not self-start (§2.8 of root AGENTS.md).

---

## Hard rules

### Evidence-first (§2.4)
Every update to PM must include the full Status Packet.
Unverified claims are not considered done.

### REVIEW file before verdict (§2.4.1)
Complete all checks and write the `### Evidence` section before writing `### Verdict`.
Verdict-before-evidence is a workflow violation.

### Two-form verdict delivery (§5.2)
1. Stage 1 PR comment (evidence first)
2. Stage 2 PR comment (verdict)
3. Formal GitHub PR review (`--approve` or `--request-changes`)

A chat reply without all three deliverables is an incomplete verdict.

### §5.4 Hard limit — ELIS mount isolation
The ELIS repository path must NEVER appear in any `volumes:` mount in any Docker Compose or
container configuration file. This check is mandatory on every PE and cannot be waived.

### Validator does not self-start (§2.8)
Wait for explicit PM assignment. Starting without assignment is an out-of-role violation.

### CI green before PASS (§3.2 of workspace AGENTS.md)
Do not issue PASS while CI is failing. Wait for green CI before Stage 2 verdict.

---

## Infra checks — quick reference (run all, paste output verbatim)

```bash
# Shell header
grep -rn "#!/usr/bin/env bash" <scripts>
grep -rn "set -euo pipefail"   <scripts>

# Port binding — 0.0.0.0 is BLOCKING
grep -rn "0\.0\.0\.0" <compose_files> <scripts>

# Docker latest tags — BLOCKING
grep -rn ":latest" <dockerfiles> <compose_files>

# CI secrets — only ${{ secrets.X }} allowed
grep -rn "secrets\." .github/workflows/<changed_workflows>

# §5.4 ELIS mount — BLOCKING if any hit
grep -rn "volumes:" <compose_files> | grep -i "elis"

# CI job/step naming
# (see workspace AGENTS.md §3.2.7 for python check)

# YAML validity
python -c "import yaml; yaml.safe_load(open('<file>'))" && echo "YAML valid"
```

---

## REVIEW file check (mandatory before push)
```bash
REVIEW_FILE=REVIEW_PE_<N>.md python scripts/check_review.py
# Must exit 0 before pushing
```

---

## Status Packet (paste in every PM update)

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
# BASE=$(grep "Base branch" CURRENT_PE.md | awk '{print $NF}')
git diff --name-status origin/$BASE..HEAD
git diff --stat        origin/$BASE..HEAD

# §6.4 Quality gates
python -m black --check .
python -m ruff check .
python -m pytest -q

# §6.5 PR evidence
# BASE=$(grep "Base branch" CURRENT_PE.md | awk '{print $NF}')
gh pr list --state open --base $BASE
gh pr view <PR_NUMBER>
```

---

## Do-not list
- Do not implement or modify infrastructure scope.
- Do not write `HANDOFF.md`.
- Do not push to feature branches except for REVIEW file and adversarial tests.
- Do not issue PASS while CI is failing.
- Do not waive the §5.4 ELIS mount check.
- Do not self-start without PM or CI Gate 1 assignment.
- Do not deliver verdict in chat only — PR comment + formal review are required.
- Do not push a REVIEW file without running `check_review.py` first (must exit 0).
- Do not paraphrase command output — paste verbatim.
- Do not commit without completing the mid-session context checkpoint (§2.9 root AGENTS.md).

## Secrets isolation (§13 root AGENTS.md)
- Read `.agentignore` at Step 0. None of those files may be open or in context.
- Run `python scripts/check_agent_scope.py` at Step 0 and at every commit.
- Never print, log, or include secret values in any output.
- If a secret is detected in context → close file, notify PM, stop.
