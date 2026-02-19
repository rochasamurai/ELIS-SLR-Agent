# PE-INFRA-02 — Implementer Assignment for CODEX
**Date:** 2026-02-19
**Agent:** CODEX
**Role:** Implementer
**Branch:** `feature/pe-infra-02-role-registration`
**Base:** `release/2.0`
**PR title:** `chore(infra): role registration mechanism + CLAUDE.md + CODEX anchor (PE-INFRA-02)`

---

## 0) Preflight — before touching any file

1. Read `AGENTS.md` fully.
2. Read `docs/_active/RELEASE_PLAN_v2.0.md`.
3. Run the following and paste output in your opening Status Packet to PM:

```bash
git fetch origin
git status -sb
git log -5 --oneline --decorate
git diff --name-status origin/release/2.0..HEAD
```

4. **Do not start implementation until PM acknowledges your opening Status Packet.**

---

## 1) Branch setup

```bash
git fetch origin
git checkout -b feature/pe-infra-02-role-registration origin/release/2.0
git status -sb
# Expected: nothing to commit, clean tree
```

---

## 2) Acceptance Criteria

Implement **all five ACs** below. No other files may be modified.

---

### AC-1 · Create `CURRENT_PE.md` at repo root

Create the file with this exact content and structure:

```markdown
# Current PE Assignment

> Maintained by PM. Update at the start of every new PE.
> Both agents read this file as Step 0 before any work.

PE: PE-INFRA-02
Branch: feature/pe-infra-02-role-registration

| Agent       | Role         |
|-------------|--------------|
| CODEX       | Implementer  |
| Claude Code | Validator    |

## PM instructions
- Edit `PE:` and `Branch:` fields at the start of every PE.
- Update the Role column when rotating agents.
- Commit and push to `release/2.0` before notifying agents to start.
- If this file is absent or an agent's name is not listed, agents must stop and notify PM.
```

**Verification:**

```bash
cat CURRENT_PE.md
# Must show all fields above with no deviation.
```

---

### AC-2 · Update `AGENTS.md` — three targeted edits

#### Edit 1 — Replace the rotation rule in §0 Glossary

Find this line in §0:

```
> Default rotation: CODEX implements odd PEs, Claude Code implements even PEs — or as assigned.
> Always confirm the current assignment with the PM before starting.
```

Replace with:

```
> Role assignment is structural, not advisory.
> Every agent reads `CURRENT_PE.md` at repo root as Step 0 to determine its role for the current PE.
> If `CURRENT_PE.md` is absent or the agent's name is not listed, the agent must stop immediately and notify PM.
> The PM edits and commits `CURRENT_PE.md` to `release/2.0` before any PE begins.
> The PM retains full override authority by editing `CURRENT_PE.md` at any time.
```

#### Edit 2 — Add §2.9 Mid-session context checkpoint

At the end of Section 2 (Operating rules), after §2.8, add:

```markdown
### 2.9 Mid-session context checkpoint
Before every `git commit`, the active agent must:
1. Re-read the PE acceptance criteria in `RELEASE_PLAN_v2.0.md`.
2. Re-read `CURRENT_PE.md` to confirm its role has not changed.
3. Run the scope gate: `git diff --name-status origin/release/2.0..HEAD`
4. Confirm no unrelated files appear in the diff.
Only then proceed with the commit.
```

#### Edit 3 — Add one line to §8 Do-not list

Append to the §8 list:

```
- Do not commit without completing the mid-session context checkpoint (§2.9).
- Do not start any PE without reading `CURRENT_PE.md` first (Step 0).
```

**Verification:**

```bash
grep -n "CURRENT_PE.md" AGENTS.md
# Must return at least 4 hits (§0, §2.9, §8, and the new Step 0 reference).

grep -n "2.9" AGENTS.md
# Must return the new §2.9 heading and the §8 reference.
```

---

### AC-3 · Create `CLAUDE.md` at repo root

Create the file with this exact content (≤ 120 lines, rules only, no prose):

```markdown
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
```

**Verification:**

```bash
wc -l CLAUDE.md
# Must be ≤ 120

grep -c "##" CLAUDE.md
# Must return ≥ 5 (Role, Step 0, Hard rules, Status Packet, Do-not list)
```

---

### AC-4 · Create `CODEX.md` at repo root

Create the file with this exact content:

```markdown
# CODEX.md — CODEX Workflow Rules
> Load this file into CODEX project instructions or paste at session start.
> Mirrors CLAUDE.md. Treat every rule as always active.

---

## Role
Default role: **Implementer** — unless `CURRENT_PE.md` states otherwise.

---

## Step 0 — Session start (mandatory before any action)
1. Read `AGENTS.md` (full).
2. Read `CURRENT_PE.md` → confirm your role for this PE.
   - If file is absent or your name is not listed → stop and notify PM immediately.
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

## Mid-session checkpoint (§2.9)
Before every `git commit`:
1. Re-read PE acceptance criteria in `RELEASE_PLAN_v2.0.md`.
2. Re-read `CURRENT_PE.md` — confirm role unchanged.
3. Run: `git diff --name-status origin/release/2.0..HEAD`
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
git diff --name-status origin/release/2.0..HEAD
git diff --stat        origin/release/2.0..HEAD

# §6.4 Quality gates
python -m black --check .
python -m ruff check .
python -m pytest -q

# §6.5 PR evidence
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
- Do not open a PR without the scope gate passing first.
- Do not open a PR before `HANDOFF.md` is committed.
- Do not start a PE without rebasing onto `origin/release/2.0`.
- Do not self-start as Validator without explicit PM assignment.
- Do not paraphrase command output — paste verbatim.
- Do not commit without completing the mid-session checkpoint (§2.9).
- Do not start any PE without reading `CURRENT_PE.md` first (Step 0).
```

**Verification:**

```bash
diff <(grep "^- " CLAUDE.md) <(grep "^- " CODEX.md)
# Must return empty (do-not lists are identical).
```

---

### AC-5 · Create `scripts/check_role_registration.py`

Pure Python stdlib. No external dependencies.

Logic:

- Read `CURRENT_PE.md` from repo root.
- If file does not exist → `print("ERROR: CURRENT_PE.md not found.")` and `exit(1)`.
- Check that the file contains a line starting with `PE:` → if missing → `print("ERROR: PE field missing.")` and `exit(1)`.
- Check that the file contains a line starting with `Branch:` → if missing → `print("ERROR: Branch field missing.")` and `exit(1)`.
- Check that both `CODEX` and `Claude Code` appear in the file → if either is missing → `print("ERROR: Agent <name> not listed in CURRENT_PE.md.")` and `exit(1)`.
- Check that each agent has exactly one role declared (`Implementer` or `Validator`) → if any agent has neither → `print("ERROR: Agent <name> has no valid role.")` and `exit(1)`.
- Check that the two agents do not hold the same role → if both are `Implementer` or both `Validator` → `print("ERROR: Both agents have the same role. Roles must differ.")` and `exit(1)`.
- If all checks pass → `print("CURRENT_PE.md OK — role registration valid.")` and `exit(0)`.

**Verification — run three adversarial tests and paste all outputs in HANDOFF.md:**

```bash
# Test 1 — valid file
python scripts/check_role_registration.py
# Expected: exit 0, "CURRENT_PE.md OK — role registration valid."

# Test 2 — missing file
mv CURRENT_PE.md CURRENT_PE.md.bak
python scripts/check_role_registration.py
mv CURRENT_PE.md.bak CURRENT_PE.md
# Expected: exit 1, "ERROR: CURRENT_PE.md not found."

# Test 3 — both agents same role (edit a temp copy)
python - <<'EOF'
content = open("CURRENT_PE.md").read().replace("Validator", "Implementer")
open("/tmp/CURRENT_PE_bad.md", "w").write(content)
EOF
CURRENT_PE_PATH=/tmp/CURRENT_PE_bad.md python scripts/check_role_registration.py
# Expected: exit 1, "ERROR: Both agents have the same role."
```

> Note: make `CURRENT_PE_PATH` an env-var override in the script so the test can point it at `/tmp/CURRENT_PE_bad.md` without touching the real file.

---

## 3) Pre-commit scope gate (run before every commit)

```bash
git diff --name-status origin/release/2.0..HEAD
```

Expected files — **only these, nothing else:**

```
A    CURRENT_PE.md
M    AGENTS.md
A    CLAUDE.md
A    CODEX.md
A    scripts/check_role_registration.py
```

If any other file appears → stop, do not commit, notify PM.

---

## 4) Quality gates (run before opening PR)

```bash
python -m black --check .
python -m ruff check .
python -m pytest -q
```

All three must pass. Paste full output verbatim in `HANDOFF.md`.

---

## 5) HANDOFF.md (commit before `git push`)

`HANDOFF.md` must contain these sections, completed in full:

```markdown
## Summary
## Files Changed
## Design Decisions
## Acceptance Criteria
## Validation Commands
```

Under `## Validation Commands`, paste verbatim output of:
- All three adversarial tests from AC-5.
- `pre-commit run --all-files` (if pre-commit is active from PE-INFRA-01).
- black, ruff, pytest gate outputs.

---

## 6) Session-end checklist

```bash
git status -sb
# Must show: nothing to commit, working tree clean
```

If any `M` or `??` appear — commit or WIP-commit before stopping. Never leave untracked files across a session boundary.

---

## 7) Open PR

```bash
gh pr create \
  --base release/2.0 \
  --head feature/pe-infra-02-role-registration \
  --title "chore(infra): role registration mechanism + CLAUDE.md + CODEX anchor (PE-INFRA-02)" \
  --body "$(cat <<'EOF'
## Summary
Implements the role registration mechanism identified as the missing 15% of the two-agent workflow.

## Files Changed
- CURRENT_PE.md (new)
- AGENTS.md (§0 rotation rule replaced, §2.9 added, §8 updated)
- CLAUDE.md (new)
- CODEX.md (new)
- scripts/check_role_registration.py (new)

## Test plan
- check_role_registration.py: 3 adversarial tests (valid file, missing file, duplicate roles)
- black / ruff / pytest: all passing

## Status Packet
[paste §6.1–§6.5 outputs here]
EOF
)"
```

---

## 8) Deliver Status Packet to PM

After PR is open, post the full Status Packet (all of §6.1–§6.5) to the PM and explicitly write:

> "PE-INFRA-02 implementation complete. Requesting PM assignment of Validator."

---

## Deliverables checklist

- [ ] `CURRENT_PE.md` — created, all fields present
- [ ] `AGENTS.md` — §0 updated, §2.9 added, §8 updated, no other sections touched
- [ ] `CLAUDE.md` — created, ≤ 120 lines, all 5 sections present
- [ ] `CODEX.md` — created, do-not list matches `CLAUDE.md` exactly
- [ ] `scripts/check_role_registration.py` — created, stdlib only, env-var path override present
- [ ] 3 adversarial test outputs pasted verbatim in `HANDOFF.md`
- [ ] `HANDOFF.md` — committed on branch before PR opened
- [ ] Scope gate shows exactly 5 files, nothing else
- [ ] black / ruff / pytest all passing — output pasted verbatim
- [ ] PR open, Status Packet delivered to PM
