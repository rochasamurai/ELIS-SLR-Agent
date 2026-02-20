# Agent Development Guide (AGENTS.md)

This file defines the **two‑agent development workflow** for **ELIS SLR Agent — Release Plan v2.0**.
It is mandatory for all **PEs** targeting the `<base-branch>` line.

**Agents**
- **CODEX** (default: Implementer)
- **Claude Code** (default: Validator)

> Role assignment is structural, not advisory.
> Every agent reads `CURRENT_PE.md` at repo root as Step 0 to determine its role for the current PE.
> If `CURRENT_PE.md` is absent or the agent's name is not listed, the agent must stop immediately and notify PM.
> The PM edits and commits `CURRENT_PE.md` to `<base-branch>` before any PE begins.
> The PM retains full override authority by editing `CURRENT_PE.md` at any time.

---

## 0) Glossary (quick)

- **PE**: Planned Execution step in `<plan-file>` (e.g., PE0a, PE1a, PE2…)
- **PM**: Project Manager — orchestrates PE assignments, authorises Validator start, approves merges, and receives all Status Packets.
- **Implementer**: writes/changes product code + PE handoff documentation
- **Validator**: verifies acceptance criteria, adds adversarial tests, issues verdict in `REVIEW_PE<N>.md`
- **Status Packet**: the standard evidence bundle required in every agent update to the PM (Section 6)
- **Worktree**: a separate working directory for a branch (prevents checkout conflicts and cross‑PE contamination)
- **Scope gate**: running `git diff --name-status origin/<base-branch>..HEAD` before every commit to verify no unrelated files crept in

---

## 1) Canonical references (read first)

Before starting any work on a PE, every agent MUST read:

0. `CURRENT_PE.md` (authoritative role assignment for the active PE)
1. `CURRENT_PE.md` → read `Plan file` to locate the authoritative plan for this release.
   Example path format: `<plan-location>/<plan-file>`
2. `AGENTS.md` (this file — workflow rules)
3. `AUDITS.md` (audit expectations)
4. On the PE branch: `HANDOFF.md` (Implementer) **or** `REVIEW_PE<N>.md` (Validator)

---

## 2) Operating rules (hard requirements)

### 2.1 One PE = one branch = one PR
- Every PE is implemented on its own feature branch created from the base branch
  declared in `CURRENT_PE.md` → `Base branch` field.
- The PR base is that same branch unless the release plan explicitly states otherwise.
- Never mix changes from different PEs on the same branch. If `git diff` shows unrelated files, **stop and split**.

### 2.2 Clean working tree before any context switch
- **Never switch branches with a dirty tree.**
- Before `git checkout`, `git rebase`, or `git stash`: run `git status -sb`.
- If output shows `M` or `??`, clean up first:
  - commit on the correct branch **or**
  - move changes to a dedicated WIP branch **or**
  - stash (temporary only — unstash immediately on the correct branch).

### 2.3 File ownership
- **Implementer owns:** all PE code, `HANDOFF.md`, non-test deliverables declared in the PE.
- **Validator owns:** `REVIEW_PE<N>.md`, adversarial tests, minimal scope‑safe fixes **only if strictly required** to satisfy acceptance criteria.
- Neither agent modifies files owned by the other without explicit instructions from the PM.

### 2.4 Evidence‑first reporting (no "trust me")
- Every agent update to the PM MUST include the **Status Packet** (Section 6).
- If a claim is not supported by pasted command output, it is not considered done.

### 2.4.1 REVIEW file evidence requirement (hard)
- Every `REVIEW_PE<N>.md` file MUST contain a `### Evidence` section with at least one
  fenced code block showing actual command output or file content. A verdict without
  inline evidence is invalid and will be rejected by Gate 2b.
- The Validator MUST complete all verification steps before writing the `### Verdict`
  line. Verdict-before-evidence is a workflow violation regardless of the final verdict
  value.

### 2.5 Atomic session boundaries — commit before ending
- **Before ending a work session, `git status -sb` must show a clean tree.**
- If files remain uncommitted, commit them on the correct branch with a descriptive message before stopping.
- Never leave implementation files as untracked `??` across a session boundary.
- Stashing across sessions is prohibited; use a WIP commit instead (`git commit -m "wip: ..."`).

### 2.6 Rebase after every `<base-branch>` merge
- After any PR is merged to `<base-branch>`, every active feature branch **must be rebased** before continuing:
  ```bash
  # BASE=$(grep "Base branch" CURRENT_PE.md | awk '{print $NF}')
  git fetch origin
  git rebase origin/$BASE
  ```
- Check drift: `git merge-base origin/$BASE HEAD` — if this returns the tip of `origin/$BASE`, the branch is current.

### 2.7 HANDOFF.md committed before PR is opened
- `HANDOFF.md` is an Implementer deliverable and must be committed on the feature branch **before** `git push` and PR creation.
- Opening a PR without a committed `HANDOFF.md` is a workflow violation. The PR must arrive complete in one push.

### 2.8 Validator does not self-start
- The Validator **waits for explicit PM authorisation** before beginning validation.
- The PM assigns the Validator after receiving the Implementer's Status Packet (§5.1 step 9).
- Assignment may be issued as a short PR comment (for example: `@claude-code — assigned as Validator. Begin review.`).
- A Validator who starts without PM assignment is out of role.

### 2.9 Mid-session context checkpoint
Before every `git commit`, the active agent must:
1. Re-read `CURRENT_PE.md` → locate `Plan file` → re-read the PE acceptance criteria in that file.
2. Re-read `CURRENT_PE.md` to confirm its role has not changed.
3. Run the scope gate: `git diff --name-status origin/$BASE..HEAD` (`BASE` from `CURRENT_PE.md`).
4. Confirm no unrelated files appear in the diff.
5. Run: `python scripts/check_agent_scope.py`
   If exit code is 1 → stop, close any secret-pattern files, notify PM.
Only then proceed with the commit.

### 2.10 Autonomous gate operation
Gate 1 and Gate 2 are enforced by CI automation after PE-INFRA-04.

**Gate 1 (Validator assignment):**
- CI verifies Status Packet completeness, HANDOFF.md, role registration,
  and quality gates automatically on every PR push.
- On success, CI posts the Validator assignment comment. Agents treat this
  comment as equivalent to a PM assignment.
- On failure, CI flags the PR for manual PM review. Agents wait.

**Gate 2 (merge):**
- CI reads the REVIEW file verdict after every push to a feature branch.
- On PASS + CI green + no `pm-review-required` label → CI merges automatically.
- On FAIL → CI posts the fix assignment comment to the Implementer.
- PM retains full veto authority by adding the `pm-review-required` label
  to any PR at any time.

**PM escalation triggers (unchanged — always require PM):**
- Scope disputes between agents
- More than two FAIL/fix iterations (audit trigger, §7)
- Any release merge (feature branch → base branch is automated;
  base branch → main always requires PM)
- Agent role rotation
- Any CI job that exits with the `pm-escalation` flag

---

## 3) Recommended practice: use git worktrees for active PEs

### 3.1 Why worktrees
Worktrees prevent:
- checkout failures ("local changes would be overwritten"),
- branch contamination (PE1 edits leaking into PE2),
- agent collisions on shared files (e.g., `HANDOFF.md` / `REVIEW_PE<N>.md`).

### 3.2 When to use
Worktrees are **required** when **two or more PEs are active in parallel**, or when:
- a PE has an open PR and may need follow‑up fixes while another PE is in progress,
- Implementer and Validator are working concurrently on different branches.

A single active PE with no parallel work may use a standard checkout instead.

### 3.3 Worktree rule
**Each active PE branch must have its own worktree folder.**
Avoid "in‑place checkout" switching between active PE branches.

### 3.4 Commands (Windows / PowerShell friendly)
From the *main* repo folder:

```bash
git fetch --all --prune
mkdir -p ../ELIS_worktrees

# Create worktrees for active PEs
git worktree add ../ELIS_worktrees/pe4  feature/pe4-dedup
git worktree add ../ELIS_worktrees/pe5  feature/pe5-asta

# Open each in its own VS Code window
code ../ELIS_worktrees/pe4
code ../ELIS_worktrees/pe5

# Remove when PE is merged
git worktree remove ../ELIS_worktrees/pe4

# List all worktrees
git worktree list
```

---

## 4) Branch naming and PR conventions

### 4.1 Branch naming
Use one of:
- `feature/pe<id>-<short-scope>` (e.g., `feature/pe4-dedup`)
- `hotfix/pe<id>-<short-scope>` for post-merge corrective fixes
- `chore/<topic>` for non‑PE housekeeping (only if authorised by PM)

### 4.2 PR title format
- `feat(pe4): deterministic dedup + clusters (elis dedup)`
- `fix(pe6): archive validate_json.py + fix elis-validate.yml trigger`
- `chore(audit): Claude Code workflow audit report`

### 4.3 PR creation
```bash
# BASE=$(grep "Base branch" CURRENT_PE.md | awk '{print $NF}')
gh pr create --base $BASE --head <branch> --title "feat(pe<N>): ..." --body "$(cat <<'EOF'
## Summary
...
## Test plan
...
EOF
)"
```

---

## 5) PE lifecycle (step-by-step)

### 5.1 Implementer workflow (CODEX unless rotated)

1. **Preflight — before any work begins:**
   - Read all canonical references (Section 1).
   - Confirm your role assignment for this PE with the PM.
   - Paste the opening Status Packet to the PM. No work starts before the PM acknowledges.
2. Rebase onto current `<base-branch>`:
   ```bash
   # BASE=$(grep "Base branch" CURRENT_PE.md | awk '{print $NF}')
   git fetch origin
   git rebase origin/$BASE   # on any existing branch, or:
   git checkout -b feature/pe<N>-<scope> origin/$BASE
   ```
3. Implement **only** the PE acceptance criteria (no unrelated changes).
4. **Pre-commit scope gate** (run before every `git commit`):
   ```bash
   # BASE=$(grep "Base branch" CURRENT_PE.md | awk '{print $NF}')
   git diff --name-status origin/$BASE..HEAD
   # Verify: only PE-scope files appear. If unrelated files show, stop and split.
   ```
5. Run quality gates:
   ```bash
   python -m black --check .
   python -m ruff check .
   python -m pytest tests/<pe-specific>.py -v
   ```
6. Update `HANDOFF.md` with:
   - summary
   - complete changed-file list
   - design decisions
   - acceptance criteria checklist (PASS/FAIL for each)
   - exact validation commands and their output (pasted verbatim — not paraphrased)
7. **Session-end check**: `git status -sb` must be clean before any push.
8. Push branch + open PR to the base branch declared in `CURRENT_PE.md`. (`HANDOFF.md` must already be committed — see §2.7.)
9. Deliver Status Packet to PM + explicitly ask PM to assign the Validator.
   - Preferred channel: include/refresh the Status Packet in the PR body or PR comment.

> **PM gate:** PM receives Status Packet, reviews it, and explicitly assigns the Validator.
> Validator does not start without this assignment.

---

### 5.2 Validator workflow (Claude Code unless rotated)

1. **Wait for PM assignment.** Do not begin without explicit PM authorisation (§2.8).
   - Preferred assignment signal: PM PR comment on the active PR.
2. **Refuse if Status Packet is missing.** Notify PM and wait for a complete packet.
3. Read `HANDOFF.md` and verify scope:
   ```bash
   # BASE=$(grep "Base branch" CURRENT_PE.md | awk '{print $NF}')
   git diff --name-status origin/$BASE..HEAD
   ```
   Output must match the files declared in `HANDOFF.md`. Any mismatch is a blocking finding.
4. Validate each acceptance criterion **verbatim** from `<plan-file>`. No substitutions.
5. Add adversarial tests covering:
   - schema rejection cases (missing fields, wrong types, boundary values)
   - determinism / idempotence
   - invalid inputs / edge cases specific to the PE
6. Run full quality gates (Section 6.3).
7. Write verdict in `REVIEW_PE<N>.md` using the standard format (Section 9).
8. If any newly discovered pre-existing defect is not already in §11, add it now.
9. Push validation commits to the **same branch** (validator-owned files only: `REVIEW_PE<N>.md` + adversarial tests).
10. Deliver verdict + Status Packet using a **GitHub PR review comment** (`approve` for PASS, `request-changes` for FAIL) using the standard format (Section 9).
    - PM may still receive a direct summary message, but the PR review is the binding live handshake record.
    - `REVIEW_PE<N>.md` remains mandatory as the durable on-branch artifact.

> **PM gate:** PM receives verdict. If PASS → PM merges. If FAIL → PM assigns Implementer to fix (§5.3).

---

### 5.3 Iteration loop (FAIL → fix → re-validate)

When the Validator issues a FAIL verdict:

**Implementer:**
1. Read `REVIEW_PE<N>.md` on the same branch.
2. Implement only the "Required fixes (blocking)" items — no scope creep.
3. Re-run scope gate and quality gates (§5.1 steps 4–5).
4. Update `HANDOFF.md`: mark fixed criteria PASS, paste new gate outputs.
5. Commit to the same branch (do not open a new PR).
6. Deliver updated Status Packet to PM + ask PM to re-assign the Validator.
   - Preferred channel: reply in PR thread with fix summary + commit SHA and request re-review.

> **PM gate:** PM receives updated Status Packet, reviews it, and re-assigns the Validator.

**Validator:**
1. Re-read `REVIEW_PE<N>.md` and `HANDOFF.md` to confirm fixes address all blocking findings.
2. Re-run full quality gates.
3. Update `REVIEW_PE<N>.md` with a new dated verdict section (do not overwrite prior findings).
4. Push to same branch and post an updated PR review/comment verdict + Status Packet.

Repeat until verdict is PASS. If more than two iterations occur, the PM may call an audit (§7).

---

## 6) Status Packet (mandatory in every agent update)

Paste command outputs exactly (no paraphrase). Run from the relevant worktree.

### 6.1 Working‑tree state (catches uncommitted work)
```bash
git status -sb
git diff --name-status
git diff --stat
```
> This is distinct from the committed-diff check below. Both are required.

### 6.2 Repository state
```bash
git fetch --all --prune
git branch --show-current
git rev-parse HEAD
git log -5 --oneline --decorate
```

### 6.3 Scope evidence (against `origin/<base-branch>`)
```bash
# BASE=$(grep "Base branch" CURRENT_PE.md | awk '{print $NF}')
git diff --name-status origin/$BASE..HEAD
git diff --stat        origin/$BASE..HEAD
```

### 6.4 Quality gates
```bash
python -m black --check .
python -m ruff check .
python -m pytest -q
```
> Include PE-specific test count alongside full-suite count.

### 6.5 PR evidence (if applicable)
```bash
# BASE=$(grep "Base branch" CURRENT_PE.md | awk '{print $NF}')
gh pr list --state open --base $BASE
gh pr view <PR_NUMBER>
```

---

## 7) Audit feature (AUDITS.md)

### 7.1 When audits run
Triggered by the PM when:
- repeated checkout conflicts occur,
- PR scope contamination is detected,
- agent role boundaries are breached,
- more than two FAIL/fix iterations occur on a single PE,
- or at major milestones.

### 7.2 What audits produce
Each agent writes a report in `reports/audits/` and submits it via a dedicated PR:

- `reports/audits/Audit_Report_Codex.md`
- `reports/audits/Audit_Report_Claude.md`

See `AUDITS.md` for the full audit spec and report templates.

---

## 8) Do‑not list

- Do not switch branches with local edits in the same folder (use worktrees).
- Do not refactor unrelated code while inside a PE.
- Do not touch `REVIEW_PE<N>.md` unless you are the Validator.
- Do not declare PASS without pasted gate outputs.
- Do not leave uncommitted implementation files when ending a session.
- Do not open a PR without running the pre-commit scope gate first.
- Do not open a PR before `HANDOFF.md` is committed on the branch (§2.7).
- Do not start on a PE without rebasing onto the current `origin/$BASE` (`BASE` from `CURRENT_PE.md`).
- Do not self-start as Validator without explicit PM assignment (§2.8).
- Do not paraphrase command output — paste it verbatim in the Status Packet.
- Do not commit without completing the mid-session context checkpoint (§2.9).
- Do not start any PE without reading `CURRENT_PE.md` first (Step 0).
- Do not open, read, or reference any file listed in `.agentignore`.
- Do not include secret values in Status Packets, HANDOFF.md, or any PR content.
- Do not proceed if `check_agent_scope.py` returns exit code 1.

---

## 9) Standard verdict and PM update format

Every agent update to the PM — whether an interim progress report or a final verdict — must use this format.

```
## Agent update — <AGENT_NAME> / <PE_ID> / <date>

### Verdict
PASS / FAIL / IN PROGRESS

### Branch / PR
Branch: feature/pe<N>-<scope>
PR: #NNN (open / merged)
Base: <base-branch-from-CURRENT_PE.md>

### Gate results
black: PASS / FAIL
ruff:  PASS / FAIL
pytest: N passed, M failed (M pre-existing — not this PE)
PE-specific tests: N/N passed

### Scope (diff vs <base-branch-from-CURRENT_PE.md>)
<paste git diff --name-status output>

### Required fixes (if FAIL)
- <minimal description of each blocking finding>

### Ready to merge
YES / NO — reason if NO

### Next
[who does what] → [next PE / action]
```

---

## 10) Per-PE REVIEW files

Validation verdicts are written to **per-PE files** rather than a single overwritten `REVIEW.md`:

- File: `REVIEW_PE<N>.md` (e.g., `REVIEW_PE4.md`, `REVIEW_PE5.md`)
- Location: repo root
- Owned by: Validator
- Written once per PE; never overwritten by a subsequent PE
- On re-validation after a FAIL, **append** a new dated section — do not overwrite prior findings.
- Live handshake channel: PR review comments are used for PASS/FAIL signalling and fix/re-review loops.
- Durable artifact rule: PR comments do **not** replace `REVIEW_PE<N>.md`; the file must still be committed.

The root `REVIEW.md` is retained as a pointer to the most recent validation for quick reference.

---

## 11) Known defects register

Pre-existing issues that are tracked but do not block current PEs:

| Defect | File | Introduced | Blocking? | Owner |
|--------|------|-----------|-----------|-------|
| `datetime.utcnow()` deprecation warnings | `elis/pipeline/screen.py` | Pre-v2.0 | No | TBD |

**Rule:** Any new PE that touches `elis/cli.py` must update `tests/test_cli.py` to stay current.
Any Validator who finds a new pre-existing defect not in this table must add it here (§5.2 step 8).

---

## 12) Enforcement mechanisms

Text instructions alone cannot guarantee compliance. The following structural controls enforce the workflow without relying on agent discipline.

### 12.1 Tier 1 — Automated (cannot be bypassed)

**Branch protection on the base branch declared in `CURRENT_PE.md`** _(configure in GitHub → Settings → Branches)_:
- All CI status checks must pass before merge is allowed.
- At least 1 approving review (PM) required.
- Direct pushes blocked — PRs only.

**Currently active CI checks** (`.github/workflows/ci.yml`):
- `python -m black --check .` — formatting gate.
- `python -m ruff check .` — lint gate.
- `python -m pytest -q` — full test suite.

**Planned CI checks** _(not yet implemented — add to `ci.yml`)_:
- HANDOFF.md presence and section check: verify that `HANDOFF.md` contains required
  headers (`## Summary`, `## Files Changed`, `## Acceptance Criteria`, `## Validation Commands`)
  before merge is allowed.

**Planned: pre-commit hooks** (`.pre-commit-config.yaml`) _(not yet implemented)_:
- Run black, ruff, and pytest on every local `git commit`.
- Prevents "fix later" drift between commits and the final push.

### 12.2 Tier 2 — Structural prompting (reduces drift)

**PR template** (`.github/pull_request_template.md`) — _active_:
Every PR opens with a pre-filled Status Packet skeleton. The PM can verify at a glance
whether all required fields are present before authorising merge.

**`CLAUDE.md` for Claude Code** _(planned — not yet implemented)_:
Critical workflow rules — "update HANDOFF.md before opening PR", "Status Packet mandatory
before any work", "wait for PM assignment before validating" — duplicated in `CLAUDE.md`,
which is always loaded into Claude Code's system prompt and survives context compression.

**`HANDOFF.md` fill-in template** _(planned — not yet implemented)_:
A template file (`docs/templates/HANDOFF_template.md`) with all required sections
pre-populated. Implementers copy it rather than writing from memory.

### 12.3 Tier 3 — Human checkpoints

**PM gates (two explicit decision points per PE):**
1. **Before Validator starts** — PM receives Implementer Status Packet and explicitly assigns Validator (preferred: PR comment assignment).
2. **Before merge** — PM receives Validator verdict and Status Packet (preferred: PR review comment + `REVIEW_PE<N>.md`). Merge only on explicit GO.

**Audit trigger** (§7): Any workflow deviation observed by any party triggers an audit report.
The record creates accountability and a pattern log across PEs.

---

## 13) Secrets isolation policy

### 13.1 What agents must never access
Both CODEX and Claude Code are prohibited from reading, referencing,
printing, logging, or including in any prompt or output:
- Any file matching patterns in `.agentignore`
- Any environment variable containing a credential, token, or key
- Any value that appears to be a secret (matches patterns: sk-*, ghp_*, xox*, etc.)

### 13.2 Structural controls
- `.gitignore` excludes all secret-pattern files from version control.
- `.agentignore` documents forbidden paths explicitly for agent reference.
- `.env.example` is the only committed env file — contains placeholders only.
- `scripts/check_agent_scope.py` runs in CI on every PR.
- IDE context (CODEX Agent mode, Claude Code extension) automatically
  includes open files — agents must not open secret-pattern files in the editor.

### 13.3 Agent responsibility
At Step 0 of every session, each agent reads `.agentignore` and confirms
that none of the listed files are open in the editor or included in context.
If a secret-pattern file is detected in context, the agent must:
1. Close the file immediately.
2. Notify the PM.
3. Not proceed until the PM confirms the exposure is contained.

### 13.4 What to do if a secret is accidentally exposed
- Do not include the value in any further output.
- Notify PM immediately with the file name only (not the value).
- PM rotates the exposed credential before the session continues.
- PM adds the incident to the defects register (§11) with status Blocking.

---

End of AGENTS.md

