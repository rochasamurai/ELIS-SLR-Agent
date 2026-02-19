# HANDOFF.md — PE-INFRA-04

## Summary

Implements PE-INFRA-04: Autonomous Operation + Secrets Security.

Introduces two GitHub Actions gate workflows (auto-assign-validator, auto-merge-on-pass),
four new CI scripts (check_status_packet.py, check_handoff.py, parse_verdict.py,
check_agent_scope.py), three secrets isolation artefacts (.agentignore, .env.example,
.gitignore hardening), and updates to AGENTS.md / CLAUDE.md / CODEX.md.

After this PE merges, Gate 1 (Validator assignment) and Gate 2 (auto-merge on PASS)
are enforced by CI automation. This is the last PE requiring a manual Validator
assignment request.

**Design decision:**
Gate automation replaces manual PM reading of Status Packets and verdicts.
PM authority is preserved via the `pm-review-required` label veto and branch
protection on main. Secrets isolation is structural (gitignore + agentignore +
CI scan) rather than trust-based (telling agents not to look).

## Files Changed

```
M    .gitignore                                    (AC-5 Layer 1 — secrets patterns appended)
A    .agentignore                                  (AC-5 Layer 2 — forbidden paths for agents)
A    .env.example                                  (AC-5 Layer 3 — placeholder env, safe to commit)
A    .github/workflows/auto-assign-validator.yml   (AC-1 — Gate 1 workflow)
A    .github/workflows/auto-merge-on-pass.yml      (AC-2 — Gate 2 workflow)
A    scripts/check_status_packet.py                (AC-3 — validate PR body completeness)
A    scripts/check_handoff.py                      (AC-3b — validate HANDOFF.md completeness)
A    scripts/parse_verdict.py                      (AC-4 — extract verdict from REVIEW file)
A    scripts/check_agent_scope.py                  (AC-5 Layer 4 — scan for secret-pattern files)
M    AGENTS.md                                     (AC-6 — §2.9 step 5, §2.10, §8 additions, §13)
M    CLAUDE.md                                     (AC-7 — autonomous gate + secrets sections)
M    CODEX.md                                      (AC-7 — autonomous gate + secrets sections)
A    HANDOFF.md                                    (this file)
```

**Note on check_role_registration.py:** This script already existed in release/2.0 and is
referenced by the auto-assign-validator.yml workflow. It was not modified (scope gate
confirms no diff). No new file was created.

## Acceptance Criteria

- [x] AC-1: `.github/workflows/auto-assign-validator.yml` created
  - Triggers on `workflow_run: ["ELIS - CI"]` completed (not `pull_request`)
  - Resolves PR via github-script using `context.repo.owner:branch` format
  - Verifies Status Packet, HANDOFF.md, and role registration
  - Posts Gate 1 assignment comment on success; PM notification on failure
- [x] AC-2: `.github/workflows/auto-merge-on-pass.yml` created
  - Triggers on push to `feature/**`, `chore/**`, `hotfix/**`
  - Parses verdict from REVIEW file via `parse_verdict.py`
  - Checks for `pm-review-required` veto label before merging
  - Auto-merges (squash) on PASS + no veto; PM notification on veto or FAIL
- [x] AC-3: `scripts/check_status_packet.py` created — stdlib only
  - Reads `PR_BODY` env var; checks all 5 required sections
  - Exit 0 on complete; exit 1 with specific missing section on failure
- [x] AC-3b: `scripts/check_handoff.py` created — stdlib only, `HANDOFF_PATH` env override
  - Reads `HANDOFF_PATH` env var (default: `HANDOFF.md`)
  - Checks all 4 required sections from AGENTS.md §12.2
  - Exit 0 on complete; exit 1 with specific missing section on failure
- [x] AC-4: `scripts/parse_verdict.py` created — stdlib only, `REVIEW_PATH` env override
  - Finds most recent `REVIEW_PE*.md` by mtime; returns IN_PROGRESS if none found
  - Parses `### Verdict` block; maps PASS/FAIL/IN PROGRESS to Actions output
  - Supports `GITHUB_OUTPUT` env for GitHub Actions; prints to stdout locally
- [x] AC-5: Secrets isolation — four layers
  - Layer 1: `.gitignore` hardened with secrets patterns (`.env.*`, `*.key`, `secrets/`, `.codex/`, `.claude/`, etc.)
  - Layer 2: `.agentignore` created — forbidden paths with `!.env.example` negation
  - Layer 3: `.env.example` created — placeholder values only
  - Layer 4: `scripts/check_agent_scope.py` — scans worktree, supports `!` negations, exits 1 on violation
- [x] AC-6: `AGENTS.md` updated
  - §2.9 step 5 added: `python scripts/check_agent_scope.py` in mid-session checkpoint
  - §2.10 added: autonomous gate operation description
  - §8 Do-not list: three secrets rules added
  - §13 Secrets isolation policy: four subsections added
- [x] AC-7: `CLAUDE.md` and `CODEX.md` updated
  - Autonomous gate operation (§2.10) section added
  - Secrets isolation (§13) section added
- [x] `check_agent_scope.py` returns exit 0 on current clean worktree
- [x] Scope gate shows exactly 12 PE files + HANDOFF.md = 13 files, nothing else
- [x] black / ruff / pytest PASS (445 passed)

## Validation Commands

### Quality gates

```
python -m black --check .
→ 101 files would be left unchanged.

python -m ruff check .
→ All checks passed!

python -m pytest
→ 445 passed, 17 warnings in 5.68s
```

### check_agent_scope.py on clean worktree

```
$ python scripts/check_agent_scope.py
Agent scope clean — no secret-pattern files detected in worktree.
Exit: 0
```

### AC-3: check_status_packet.py adversarial tests

```
-- Test 1: complete body (exit 0 expected) --
Status Packet OK — all required sections present.
Exit: 0

-- Test 2: missing Verdict section (exit 1 expected) --
Missing section: ### Verdict
Exit: 1

-- Test 3: empty body (exit 1 expected) --
ERROR: PR body is empty.
Exit: 1
```

### AC-3b: check_handoff.py adversarial tests

```
-- Test 1: complete HANDOFF.md (exit 0 expected) --
HANDOFF.md OK — all required sections present.
Exit: 0

-- Test 2: missing section (exit 1 expected) --
Missing section: ## Acceptance Criteria
Missing section: ## Validation Commands
Exit: 1

-- Test 3: file not found (exit 1 expected) --
ERROR: HANDOFF.md not found.
Exit: 1
```

### AC-4: parse_verdict.py adversarial tests

```
-- Test 1: PASS verdict (exit 0 expected) --
review_file=REVIEW_PE99.md
verdict=PASS
Verdict: PASS (file: REVIEW_PE99.md)
Exit: 0

-- Test 2: FAIL verdict (exit 0 expected) --
review_file=REVIEW_PE99.md
verdict=FAIL
Verdict: FAIL (file: REVIEW_PE99.md)
Exit: 0

-- Test 3: no REVIEW file (exit 0 expected) --
verdict=IN_PROGRESS
review_file=
No REVIEW_PE*.md file found — verdict set to IN_PROGRESS.
Exit: 0
```

### AC-5 Layer 4: check_agent_scope.py adversarial tests

```
-- Test 1: clean worktree (exit 0 expected) --
Agent scope clean — no secret-pattern files detected in worktree.
Exit: 0

-- Test 2: .env file present (exit 1 expected) --
WARNING: The following secret-pattern files exist in the worktree:
  .env
Agents must not read these files. Verify IDE context excludes them.
Exit: 1

-- Test 3: secrets/ directory present (exit 1 expected) --
WARNING: The following secret-pattern files exist in the worktree:
  secrets\prod.yml
Agents must not read these files. Verify IDE context excludes them.
Exit: 1
```

### Scope gate

```
$ git diff --name-status origin/release/2.0..HEAD
 M .gitignore
 M AGENTS.md
 M CLAUDE.md
 M CODEX.md
?? .agentignore
?? .env.example
?? .github/workflows/auto-assign-validator.yml
?? .github/workflows/auto-merge-on-pass.yml
?? scripts/check_agent_scope.py
?? scripts/check_handoff.py
?? scripts/check_status_packet.py
?? scripts/parse_verdict.py
```
