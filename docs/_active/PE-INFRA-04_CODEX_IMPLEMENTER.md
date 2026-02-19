> Rules authority: AGENTS.md. This document is the operational narrative only.
> In any conflict between this file and AGENTS.md, AGENTS.md governs.

# PE-INFRA-04 — Autonomous Operation + Secrets Security
**Date:** 2026-02-19
**Agent:** CODEX
**Role:** Implementer
**Branch:** `chore/pe-infra-04-autonomous-secrets`
**Base:** `release/2.0`
**PR title:** `chore(infra): autonomous agent gates + secrets isolation (PE-INFRA-04)`

---

## Design rationale (read before implementing)

### Problem 1 — PM approval bottleneck

The current workflow has two hard PM gates per PE:

```
Implementer done → PM reviews → assigns Validator     (Gate 1)
Validator done   → PM reviews → merges or iterates    (Gate 2)
```

For a project with many PEs running in sequence or in parallel, this creates
a synchronous dependency on a single human for every state transition.
Governance best practice distinguishes between:

- **Controls that require human judgement** — scope decisions, merge authority,
  conflict resolution, audit triggers. These stay with the PM.
- **Controls that can be automated** — evidence verification, quality gates,
  role validation, handoff completeness. These should be enforced by CI,
  not by the PM reading Status Packets manually.

The fix is not to remove the PM. It is to replace manual PM verification steps
with automated gates so the PM only acts when automation cannot — and agents
can proceed continuously when all automated gates pass.

### Problem 2 — Secrets exposure

Neither CODEX nor Claude Code should ever read API keys, database credentials,
tokens, or any other secret values used by the project. Both agents:
- have IDE context enabled (open files are automatically included in prompts)
- can read any file in the worktree directory
- may log or transmit context to external model endpoints

Without explicit exclusion, a `.env` file or hardcoded credential in any
tracked or untracked file is a secret leak waiting to happen.

---

## Governance model after PE-INFRA-04

```
BEFORE                                  AFTER
──────────────────────────────────────  ────────────────────────────────────
Gate 1: PM reads Status Packet          Gate 1: CI bot reads Status Packet
        PM assigns Validator manually           Bot auto-assigns Validator
                                                if all automated checks pass
                                                PM notified but not blocking

Gate 2: PM reads verdict                Gate 2: CI bot verifies PASS verdict
        PM merges manually                      Auto-merge on PASS + CI green
                                                PM retains veto (branch protection)

PM required for:                        PM required for:
- All decisions (current)               - Scope disputes
                                        - Audit triggers
                                        - Release merges (base → main)
                                        - Rotating agent roles
                                        - Any CI escalation flag
```

The PM moves from **approving every transition** to **governing exceptions**.
Every routine PE still produces a full audit trail. Nothing bypasses the rules —
the rules are enforced by machines instead of by manual reading.

---

## 0) Preflight

1. Read `AGENTS.md` fully.
2. Read `CURRENT_PE.md` — confirm role is Implementer.
3. Run and paste in opening Status Packet:

```bash
git fetch origin
git status -sb
git log -5 --oneline --decorate
BASE=$(grep "Base branch" CURRENT_PE.md | awk '{print $NF}')
git diff --name-status origin/$BASE..HEAD
```

4. Do not start until PM acknowledges opening Status Packet.

---

## 1) Branch setup

```bash
BASE=$(grep "Base branch" CURRENT_PE.md | awk '{print $NF}')
git fetch origin
git checkout -b chore/pe-infra-04-autonomous-secrets origin/$BASE
git status -sb
```

---

## 2) Acceptance Criteria

### AC-1 · Automated Gate 1 — CI auto-assigns Validator

**What it replaces:** PM manually reading Status Packet and posting
`@claude-code — assigned as Validator. Begin review.`

**How it works:** A GitHub Actions workflow triggers when a PR to the base branch
receives a new commit where CI is fully green. It verifies the Status Packet
skeleton in the PR body is complete, then posts the Validator assignment comment
automatically. The PM receives a notification but is not a blocking dependency.

#### Create `.github/workflows/auto-assign-validator.yml`

```yaml
name: Auto-assign Validator

on:
  workflow_run:
    # Must match the 'name:' field in ci.yml exactly.
    workflows: ["ELIS - CI"]
    types: [completed]

permissions:
  contents: read
  pull-requests: write
  issues: write

jobs:
  gate-1:
    name: Verify Status Packet and assign Validator
    runs-on: ubuntu-latest
    # Only run when CI succeeded on a non-main branch PR.
    if: |
      github.event.workflow_run.conclusion == 'success' &&
      github.event.workflow_run.event == 'pull_request' &&
      github.event.workflow_run.head_branch != 'main'

    steps:
      - name: Checkout PR head
        uses: actions/checkout@v4
        with:
          ref: ${{ github.event.workflow_run.head_sha }}

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install -e ".[dev]"

      - name: Resolve PR number and body
        id: pr
        uses: actions/github-script@v7
        with:
          script: |
            const prs = await github.rest.pulls.list({
              owner: context.repo.owner,
              repo: context.repo.repo,
              head: `${context.repo.owner}:${context.payload.workflow_run.head_branch}`,
              state: 'open'
            });
            if (prs.data.length === 0) {
              core.warning('No open PR found for this branch — skipping auto-assign.');
              core.setOutput('number', '');
              return;
            }
            core.setOutput('number', String(prs.data[0].number));
            core.setOutput('body', prs.data[0].body || '');

      - name: Verify Status Packet completeness
        if: steps.pr.outputs.number != ''
        run: python scripts/check_status_packet.py
        env:
          PR_BODY: ${{ steps.pr.outputs.body }}

      - name: Verify HANDOFF.md present and complete
        if: steps.pr.outputs.number != ''
        run: python scripts/check_handoff.py

      - name: Verify role registration
        if: steps.pr.outputs.number != ''
        run: python scripts/check_role_registration.py

      - name: Auto-assign Validator via PR comment
        if: success() && steps.pr.outputs.number != ''
        uses: actions/github-script@v7
        with:
          script: |
            const prNumber = parseInt('${{ steps.pr.outputs.number }}');
            const body = [
              '## 🤖 Gate 1 — automated',
              '',
              'All automated checks passed:',
              '- ✅ Status Packet complete',
              '- ✅ HANDOFF.md present with all required sections',
              '- ✅ Role registration valid',
              '- ✅ CI quality gates green',
              '',
              '@claude-code — assigned as Validator. Begin review.',
              '',
              '_PM notified. No manual approval required for routine PEs._',
              '_PM veto: close this PR to block merge._'
            ].join('\n');
            await github.rest.issues.createComment({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: prNumber,
              body
            });

      - name: Notify PM on failure
        if: failure() && steps.pr.outputs.number != ''
        uses: actions/github-script@v7
        with:
          script: |
            const prNumber = parseInt('${{ steps.pr.outputs.number }}');
            await github.rest.issues.createComment({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: prNumber,
              body: '## ⚠️ Gate 1 — manual PM review required\n\nAutomated checks did not pass. PM must review and assign Validator manually.'
            });
```

---

### AC-2 · Automated Gate 2 — CI auto-merge on Validator PASS

**What it replaces:** PM manually reading `REVIEW_PEN.md` and clicking merge.

**How it works:** A workflow triggers when a new commit is pushed to a feature branch.
It reads `REVIEW_PEN.md` on the branch, parses the verdict field, and if the verdict
is `PASS` and all CI checks are green, it merges the PR automatically.
The PM retains full veto authority via branch protection (1 approving review required
is removed from routine PEs — the PM can re-enable it for any PE by adding the
`pm-review-required` label to the PR).

#### Create `.github/workflows/auto-merge-on-pass.yml`

```yaml
name: Auto-merge on Validator PASS

on:
  push:
    branches:
      - 'feature/**'
      - 'chore/**'
      - 'hotfix/**'

jobs:
  gate-2:
    name: Parse verdict and auto-merge if PASS
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Parse verdict from REVIEW file
        id: verdict
        run: python scripts/parse_verdict.py
        # Outputs: verdict=PASS|FAIL|IN_PROGRESS, review_file=REVIEW_PEN.md

      - name: Check for PM veto label
        id: labels
        uses: actions/github-script@v7
        with:
          script: |
            const { data: pr } = await github.rest.pulls.list({
              owner: context.repo.owner,
              repo: context.repo.repo,
              head: `${context.repo.owner}:${context.ref_name}`,
              state: 'open'
            });
            if (pr.length === 0) { core.setOutput('veto', 'no-pr'); return; }
            const labels = pr[0].labels.map(l => l.name);
            core.setOutput('veto', labels.includes('pm-review-required') ? 'true' : 'false');
            core.setOutput('pr_number', pr[0].number);

      - name: Auto-merge if PASS and no veto
        if: |
          steps.verdict.outputs.verdict == 'PASS' &&
          steps.labels.outputs.veto == 'false'
        uses: actions/github-script@v7
        with:
          script: |
            const prNumber = parseInt('${{ steps.labels.outputs.pr_number }}');
            await github.rest.pulls.merge({
              owner: context.repo.owner,
              repo: context.repo.repo,
              pull_number: prNumber,
              merge_method: 'squash',
              commit_title: `Merge PE: auto-merged on Validator PASS`
            });
            await github.rest.issues.createComment({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: prNumber,
              body: '## ✅ Gate 2 — auto-merged\n\nValidator PASS verdict confirmed. PR merged automatically.\nPM audit trail: REVIEW file committed on branch.'
            });

      - name: Notify PM — veto label present
        if: |
          steps.verdict.outputs.verdict == 'PASS' &&
          steps.labels.outputs.veto == 'true'
        uses: actions/github-script@v7
        with:
          script: |
            const prNumber = parseInt('${{ steps.labels.outputs.pr_number }}');
            await github.rest.issues.createComment({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: prNumber,
              body: '## 🔒 Gate 2 — PM approval required\n\nValidator PASS confirmed but `pm-review-required` label is set.\nPM must manually approve and merge.'
            });

      - name: Notify PM — FAIL verdict
        if: steps.verdict.outputs.verdict == 'FAIL'
        uses: actions/github-script@v7
        with:
          script: |
            const prNumber = parseInt('${{ steps.labels.outputs.pr_number }}');
            await github.rest.issues.createComment({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: prNumber,
              body: '## ❌ Gate 2 — FAIL verdict\n\nValidator issued FAIL. Assigning Implementer to fix blocking findings.\n\n@codex — read REVIEW file on this branch. Fix blocking findings only. Deliver updated Status Packet.'
            });
```

---

### AC-3 · `scripts/check_status_packet.py` — validate PR body completeness

Pure Python stdlib. Reads the `PR_BODY` environment variable (set by the workflow).

Required sections to check for (exact strings):

```python
REQUIRED_SECTIONS = [
    "### Verdict",
    "### Branch / PR",
    "### Gate results",
    "### Scope",
    "### Ready to merge",
]
```

Logic:
- If `PR_BODY` env var is empty or unset → `print("ERROR: PR body is empty.")` and `exit(1)`.
- For each missing section → `print(f"Missing section: {section}")` and `exit(1)`.
- If all present → `print("Status Packet OK — all required sections present.")` and `exit(0)`.

**Adversarial tests — paste all outputs verbatim in HANDOFF.md:**

```bash
# Test 1 — complete PR body
export PR_BODY="### Verdict
PASS
### Branch / PR
Branch: feature/test
### Gate results
black: PASS
### Scope
M AGENTS.md
### Ready to merge
YES"
python scripts/check_status_packet.py
# Expected: exit 0

# Test 2 — missing Verdict section
export PR_BODY="### Branch / PR
Branch: feature/test
### Gate results
black: PASS
### Scope
M AGENTS.md
### Ready to merge
YES"
python scripts/check_status_packet.py
# Expected: exit 1, "Missing section: ### Verdict"

# Test 3 — empty PR body
export PR_BODY=""
python scripts/check_status_packet.py
# Expected: exit 1, "ERROR: PR body is empty."
```

---

### AC-3b · `scripts/check_handoff.py` — validate HANDOFF.md completeness

Pure Python stdlib. Called by `auto-assign-validator.yml` to ensure HANDOFF.md is present
and contains all required sections (per AGENTS.md §12.2).

Required sections:

```python
REQUIRED_SECTIONS = [
    "## Summary",
    "## Files Changed",
    "## Acceptance Criteria",
    "## Validation Commands",
]
```

Logic:
- Read the path from the `HANDOFF_PATH` env var (default: `HANDOFF.md` at repo root).
- If the file does not exist → `print("ERROR: HANDOFF.md not found.")` and `exit(1)`.
- For each missing section → `print(f"Missing section: {section}")` and `exit(1)`.
- If all present → `print("HANDOFF.md OK — all required sections present.")` and `exit(0)`.

**Adversarial tests — paste all outputs verbatim in HANDOFF.md:**

```bash
# Test 1 — complete HANDOFF.md
cat > /tmp/HANDOFF_test.md << 'EOF'
## Summary
...
## Files Changed
...
## Acceptance Criteria
...
## Validation Commands
...
EOF
HANDOFF_PATH=/tmp/HANDOFF_test.md python scripts/check_handoff.py
# Expected: exit 0, "HANDOFF.md OK — all required sections present."

# Test 2 — missing section
cat > /tmp/HANDOFF_test.md << 'EOF'
## Summary
...
## Files Changed
...
EOF
HANDOFF_PATH=/tmp/HANDOFF_test.md python scripts/check_handoff.py
# Expected: exit 1, "Missing section: ## Acceptance Criteria"

# Test 3 — file not found
HANDOFF_PATH=/tmp/nonexistent.md python scripts/check_handoff.py
# Expected: exit 1, "ERROR: HANDOFF.md not found."
```

---

### AC-4 · `scripts/parse_verdict.py` — extract verdict from REVIEW file

Pure Python stdlib. Used by the auto-merge workflow.

Logic:
- Find the most recent `REVIEW_PE*.md` file at repo root
  (sort by modification time, take the latest).
- If no REVIEW file exists → `print("verdict=IN_PROGRESS")` set as GitHub
  Actions output and `exit(0)` (not a failure — PE may not have been validated yet).
- Read the file and find the line immediately after `### Verdict`.
- Strip whitespace. Expected values: `PASS`, `FAIL`, `IN PROGRESS`.
- Set GitHub Actions output: `echo "verdict=<VALUE>" >> $GITHUB_OUTPUT`.
- Also set: `echo "review_file=<filename>" >> $GITHUB_OUTPUT`.
- If the verdict line is absent or unrecognised →
  `print("ERROR: Verdict field missing or unrecognised.")` and `exit(1)`.

**Adversarial tests — paste all outputs verbatim in HANDOFF.md:**

```bash
# Test 1 — PASS verdict
cat > /tmp/REVIEW_PE99.md << 'EOF'
## Agent update — Claude Code / PE99 / 2026-02-19
### Verdict
PASS
### Branch / PR
Branch: feature/pe99-test
EOF
REVIEW_PATH=/tmp python scripts/parse_verdict.py
# Expected: verdict=PASS

# Test 2 — FAIL verdict
cat > /tmp/REVIEW_PE99.md << 'EOF'
## Agent update — Claude Code / PE99 / 2026-02-19
### Verdict
FAIL
EOF
REVIEW_PATH=/tmp python scripts/parse_verdict.py
# Expected: verdict=FAIL

# Test 3 — no REVIEW file present
REVIEW_PATH=/tmp/nonexistent python scripts/parse_verdict.py
# Expected: verdict=IN_PROGRESS, exit 0
```

Add a `REVIEW_PATH` env-var override (defaulting to repo root `.`) so tests
can point at `/tmp` without touching real files.

---

### AC-5 · Secrets isolation — four-layer defence

This AC has no single file. It is a set of coordinated controls.

#### Layer 1 — `.gitignore` hardening

Append to `.gitignore` (do not replace existing content):

```gitignore
# ── Secrets isolation (PE-INFRA-04) ──────────────────────────────
# Environment and secrets files
.env
.env.*
!.env.example
*.env
secrets/
.secrets/
*_secrets.*
*_credentials.*
*_key.*
*.pem
*.p12
*.pfx
*.key
!*.pub.key

# IDE context files that may expose environment
.vscode/settings.json
.idea/

# Local agent config that may contain tokens
.codex/
.claude/
codex_config.*
claude_config.*
```

#### Layer 2 — `.agentignore` (new file at repo root)

Create `.agentignore` — this file is read by `scripts/check_agent_scope.py`
(see Layer 4) to verify agents are not accessing excluded paths.
It also serves as documentation for both agents of what is out of bounds.

```
# .agentignore — paths agents must never read, reference, or include in context
# Both CODEX and Claude Code must treat these as forbidden.
# Any agent that reads a path matching these patterns is in violation.

.env
.env.*
secrets/
.secrets/
*.pem
*.key
*.p12
*.pfx
*.token
*_credentials.*
*_secrets.*
.codex/
.claude/
~/.netrc
~/.ssh/
~/.aws/credentials
~/.config/gh/hosts.yml
GITHUB_TOKEN
ANTHROPIC_API_KEY
OPENAI_API_KEY
```

#### Layer 3 — `.env.example` (new file at repo root)

Create `.env.example` documenting all required environment variables
with placeholder values only. This is the only `.env*` file committed to the repo.
Agents may read this file — it contains no real values.

```bash
# .env.example — copy to .env and fill in real values
# THIS FILE IS SAFE TO COMMIT. Never commit .env with real values.

# Anthropic
ANTHROPIC_API_KEY=your-anthropic-api-key-here

# OpenAI
OPENAI_API_KEY=your-openai-api-key-here

# GitHub
GITHUB_TOKEN=your-github-pat-here

# Project-specific
ELIS_DB_URL=postgresql://user:password@host:5432/dbname
ELIS_S3_BUCKET=your-bucket-name
ELIS_LOG_LEVEL=INFO
```

#### Layer 4 — `scripts/check_agent_scope.py`

Pure Python stdlib. Scans the worktree for any file that both:
(a) matches a pattern in `.agentignore`, AND
(b) exists as a real file (not just a gitignore pattern)

If any such files are found, it prints a warning listing them.
This script runs in CI as a pre-merge check and can be run locally
by either agent as part of their pre-commit scope gate.

Logic:
- Read `.agentignore` — skip blank lines and lines starting with `#`.
- For each pattern, use `glob.glob(pattern, recursive=True)` from repo root.
- Collect all matches that are real files (not directories).
- If any matches found:
  - `print("WARNING: The following secret-pattern files exist in the worktree:")`
  - List each file.
  - `print("Agents must not read these files. Verify IDE context excludes them.")`
  - `exit(1)`
- If no matches:
  - `print("Agent scope clean — no secret-pattern files detected in worktree.")`
  - `exit(0)`

Add this check to `.github/workflows/ci.yml` as a new job `secrets-scope-check`
that runs on every PR.

**Adversarial tests — paste all outputs verbatim in HANDOFF.md:**

```bash
# Test 1 — clean worktree (no .env files)
python scripts/check_agent_scope.py
# Expected: exit 0, "Agent scope clean..."

# Test 2 — .env file present
echo "ANTHROPIC_API_KEY=sk-test-1234" > .env
python scripts/check_agent_scope.py
rm .env
# Expected: exit 1, lists .env as a violation

# Test 3 — secrets/ directory present
mkdir -p secrets && echo "token: abc123" > secrets/prod.yml
python scripts/check_agent_scope.py
rm -rf secrets/
# Expected: exit 1, lists secrets/prod.yml
```

---

### AC-6 · Update `AGENTS.md` — add §2.10 and §13

#### §2.10 — Autonomous gate operation

Add after §2.9:

```markdown
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
```

#### §13 — Secrets isolation policy

Add new section §13:

```markdown
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
```

#### Update §2.9 mid-session checkpoint — add secrets check

Append to the existing §2.9 step list:

```
5. Run: python scripts/check_agent_scope.py
   If exit code is 1 → stop, close any secret-pattern files, notify PM.
```

#### Update §8 Do-not list — add secrets rules

Append:

```
- Do not open, read, or reference any file listed in `.agentignore`.
- Do not include secret values in Status Packets, HANDOFF.md, or any PR content.
- Do not proceed if `check_agent_scope.py` returns exit code 1.
```

---

### AC-7 · Update `CLAUDE.md` and `CODEX.md` — add autonomous gate + secrets sections

#### In both files, add after the `## Step 0` section:

```markdown
## Autonomous gate operation (§2.10)
Gate 1 (Validator assignment) is posted by CI bot — treat it as PM assignment.
Gate 2 (merge) is executed by CI bot on PASS verdict + green CI.
PM veto: `pm-review-required` label on the PR blocks auto-merge.
Escalate to PM manually only for: scope disputes, >2 FAIL iterations,
release merges, role rotation, or CI `pm-escalation` flag.
```

#### In both files, add after the `## Do-not list` section:

```markdown
## Secrets isolation (§13)
- Read `.agentignore` at Step 0. None of those files may be open or in context.
- Run `python scripts/check_agent_scope.py` at Step 0 and at every commit.
- Never print, log, or include secret values in any output.
- If a secret is detected in context → close file, notify PM, stop.
```

---

## 3) Scope gate

```bash
BASE=$(grep "Base branch" CURRENT_PE.md | awk '{print $NF}')
git diff --name-status origin/$BASE..HEAD
```

Expected files — **only these, nothing else (12 files):**

```
M    .gitignore
A    .agentignore
A    .env.example
A    .github/workflows/auto-assign-validator.yml
A    .github/workflows/auto-merge-on-pass.yml
A    scripts/check_status_packet.py
A    scripts/check_handoff.py
A    scripts/check_agent_scope.py
A    scripts/parse_verdict.py
M    AGENTS.md
M    CLAUDE.md
M    CODEX.md
A    HANDOFF.md
```

---

## 4) Quality gates

```bash
python -m black --check .
python -m ruff check .
python -m pytest -q
```

---

## 5) HANDOFF.md

Standard five sections. Under `## Validation Commands`, paste verbatim:
- All adversarial test outputs from AC-3, AC-4, and AC-5 (Layer 4)
- black / ruff / pytest outputs
- `python scripts/check_agent_scope.py` on clean worktree (must be exit 0)

Under `## Design Decisions`, include:

> "Gate automation replaces manual PM reading of Status Packets and verdicts.
>  PM authority is preserved via the pm-review-required label veto and branch
>  protection on main. Secrets isolation is structural (gitignore + agentignore +
>  CI scan) rather than trust-based (telling agents not to look)."

---

## 6) Open PR

```bash
BASE=$(grep "Base branch" CURRENT_PE.md | awk '{print $NF}')
gh pr create \
  --base $BASE \
  --head chore/pe-infra-04-autonomous-secrets \
  --title "chore(infra): autonomous agent gates + secrets isolation (PE-INFRA-04)" \
  --body "$(cat <<'EOF'
### Verdict
IN PROGRESS

### Branch / PR
Branch: chore/pe-infra-04-autonomous-secrets
PR: this PR
Base: release/2.0

### Gate results
black: PASS
ruff:  PASS
pytest: N passed

### Scope
[paste git diff --name-status output]

### Ready to merge
NO — awaiting Validator assignment
EOF
)"
```

---

## 7) Deliver Status Packet to PM

Post §6.1–§6.5 and write:

> "PE-INFRA-04 implementation complete. Requesting Validator assignment.
>  Note: after this PE merges, Gate 1 will auto-assign the Validator via CI.
>  This is the last PE requiring a manual Validator assignment request."

---

## Deliverables checklist

- [ ] `.gitignore` — secrets patterns appended
- [ ] `.agentignore` — created, all forbidden paths listed
- [ ] `.env.example` — created, placeholder values only, no real secrets
- [ ] `.github/workflows/auto-assign-validator.yml` — created
- [ ] `.github/workflows/auto-merge-on-pass.yml` — created
- [ ] `scripts/check_status_packet.py` — created, stdlib only
- [ ] `scripts/check_handoff.py` — created, stdlib only, HANDOFF_PATH env override
- [ ] `scripts/parse_verdict.py` — created, stdlib only, REVIEW_PATH env override
- [ ] `scripts/check_agent_scope.py` — created, stdlib only
- [ ] `AGENTS.md` — §2.9 updated, §2.10 added, §8 updated, §13 added
- [ ] `CLAUDE.md` — autonomous gate + secrets sections added
- [ ] `CODEX.md` — autonomous gate + secrets sections added
- [ ] All adversarial test outputs pasted verbatim in HANDOFF.md
- [ ] `check_agent_scope.py` returns exit 0 on current worktree
- [ ] Scope gate shows exactly 11 files, nothing else
- [ ] black / ruff / pytest passing
- [ ] `HANDOFF.md` committed before PR opened
- [ ] Status Packet delivered to PM
