# CODEX.md — CODEX Workflow Rules
> Load this file into CODEX project instructions or paste at session start.
> Mirrors CLAUDE.md. Treat every rule as always active.

---

## Role
Default role: **Implementer** — unless `CURRENT_PE.md` states otherwise.

---

## Step 0 — Session start (mandatory before any action)
1. Read `AGENTS.md` (full).
2. Read `CURRENT_PE.md`:
   - Confirm your role (`Agent roles` table).
   - Note `Base branch` and `Plan file` — use these in every git command and plan reference.
   - If any field is blank or the file is absent → stop and notify PM.
3. Read `HANDOFF.md` on the active branch if Implementer,
   or `REVIEW_PE<N>.md` if assigned as Validator.
4. Deliver opening Status Packet to PM and wait for acknowledgement before any file change.

---

## Hard rules (from AGENTS.md §2.4 · §2.7 · §2.8)

### §2.4 Evidence-first reporting
Every update to PM must include the full Status Packet.
Unverified claims are not considered done.

### §2.7 HANDOFF.md committed before PR is opened
Commit `HANDOFF.md` on the feature branch before `git push`.
Do not open a PR without it.

### §2.8 Validator does not self-start
If assigned as Validator, wait for explicit PM PR comment before beginning review.

---

## Autonomous gate operation (§2.10)
Gate 1 (Validator assignment) is posted by CI bot — treat it as PM assignment.
Gate 2 (merge) is executed by CI bot on PASS verdict + green CI.
PM veto: `pm-review-required` label on the PR blocks auto-merge.
Escalate to PM manually only for: scope disputes, >2 FAIL iterations,
release merges, role rotation, or CI `pm-escalation` flag.

---

## Mid-session checkpoint (§2.9)
Before every `git commit`:
1. Re-read `CURRENT_PE.md` → `Plan file` field → re-read PE acceptance criteria in that file.
2. Re-read `CURRENT_PE.md` — confirm role unchanged.
3. Run: `git diff --name-status origin/$BASE..HEAD`
4. Confirm no unrelated files in diff.

---

## Status Packet (§6) — paste in every PM update

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

## Do-not list (§8)
- Do not switch branches with local edits (use worktrees).
- Do not refactor unrelated code inside a PE.
- Do not touch `REVIEW_PE<N>.md` unless you are the Validator.
- Do not declare PASS without pasted gate outputs.
- Do not leave uncommitted files when ending a session.
- Do not open a PR without running the pre-commit scope gate first.
- Do not open a PR before `HANDOFF.md` is committed on the branch.
- Do not start a PE without rebasing onto current `origin/$BASE` (`BASE` from `CURRENT_PE.md`).
- Do not self-start as Validator without explicit PM assignment.
- Do not paraphrase command output — paste verbatim in Status Packet.
- Do not commit without completing the mid-session context checkpoint (§2.9).
- Do not start any PE without reading `CURRENT_PE.md` first (Step 0).

## Secrets isolation (§13)
- Read `.agentignore` at Step 0. None of those files may be open or in context.
- Run `python scripts/check_agent_scope.py` at Step 0 and at every commit.
- Never print, log, or include secret values in any output.
- If a secret is detected in context → close file, notify PM, stop.
