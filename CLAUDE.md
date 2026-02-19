# CLAUDE.md — Claude Code Workflow Rules
> This file is auto-loaded into every Claude Code session.
> It survives context compression. Treat every rule here as always active.

---

## Role
Default role: **Validator** — unless `CURRENT_PE.md` states otherwise.

---

## Step 0 — Session start (mandatory before any action)
1. Read `AGENTS.md` (full).
2. Read `CURRENT_PE.md` → confirm your role for this PE.
   - If file is absent or your name is not listed → stop and notify PM immediately.
3. Read `HANDOFF.md` (if Validator) or `REVIEW_PE<N>.md` (if Implementer) on the active branch.
4. Confirm you have explicit PM authorisation before proceeding.
   - Validator: wait for PM PR comment assigning you. Do not self-start.
   - Implementer: wait for PM acknowledgement of your opening Status Packet.

---

## Hard rules (from AGENTS.md §2.4 · §2.7 · §2.8)

### §2.4 Evidence-first reporting
Every update to PM must include the full Status Packet (see below).
If a claim is not supported by pasted command output, it is not considered done.

### §2.7 HANDOFF.md committed before PR is opened
`HANDOFF.md` must be committed on the feature branch before `git push` and PR creation.
Opening a PR without a committed `HANDOFF.md` is a workflow violation.

### §2.8 Validator does not self-start
Wait for explicit PM authorisation before beginning validation.
PM assigns via PR comment: `@claude-code — assigned as Validator. Begin review.`
Starting without this assignment is an out-of-role violation.

---

## Mid-session checkpoint (§2.9)
Before every `git commit`:
1. Re-read PE acceptance criteria in `RELEASE_PLAN_v2.0.md`.
2. Re-read `CURRENT_PE.md` — confirm role unchanged.
3. Run: `git diff --name-status origin/release/2.0..HEAD`
4. Confirm no unrelated files in diff.

---

## Status Packet (§6) — paste in every PM update

### §6.1 Working-tree state
```bash
git status -sb
git diff --name-status
git diff --stat
```

### §6.2 Repository state
```bash
git fetch --all --prune
git branch --show-current
git rev-parse HEAD
git log -5 --oneline --decorate
```

### §6.3 Scope evidence
```bash
git diff --name-status origin/release/2.0..HEAD
git diff --stat        origin/release/2.0..HEAD
```

### §6.4 Quality gates
```bash
python -m black --check .
python -m ruff check .
python -m pytest -q
```

### §6.5 PR evidence
```bash
gh pr list --state open --base release/2.0
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
- Do not start a PE without rebasing onto current `origin/release/2.0`.
- Do not self-start as Validator without explicit PM assignment.
- Do not paraphrase command output — paste verbatim in Status Packet.
- Do not commit without completing the mid-session context checkpoint (§2.9).
- Do not start any PE without reading `CURRENT_PE.md` first (Step 0).
