# AGENTS.md — workspace-infra-val
> Workspace: `workspace-infra-val`
> Agents: `infra-val-codex`, `infra-val-claude`
> Domain: Infrastructure Validation
> Role: **Validator** (both agents — active engine is always opposite of Implementer per alternation rule)

---

## 1. Scope

This workspace governs Infrastructure Validators. Every PE assigned to this workspace targets
infrastructure artifacts: CI/CD workflows, Docker Compose files, shell scripts, GitHub Actions
YAML, and deployment tooling.

Validators in this workspace do **not** implement features. They review, test, and issue verdicts.

---

## 2. Mandatory pre-session reads (Step 0)

Before any action in a session:

1. Read `AGENTS.md` (this file — full).
2. Read `CURRENT_PE.md` at repo root:
   - Confirm your agent ID appears in the `Agent roles` table.
   - Note `Base branch` and `Plan file`.
   - If either field is blank or your agent ID is absent → stop, notify PM.
3. Read the Implementer's `HANDOFF.md` on the active feature branch.
4. Wait for explicit PM assignment before beginning review (§2.8 of root AGENTS.md).
   Assignment signal: PM PR comment — `@<agent-id> — assigned as Validator. Begin review.`
   or equivalent CI Gate 1 comment.

---

## 3. Validation protocol

### 3.1 Two-stage comment protocol (mandatory, always)

**Stage 1 — Evidence comment** (posted before Stage 2):
- Scope diff vs base branch
- Each infra-specific check result (§3.2) with pasted command output
- At least one adversarial / negative-path test result
- Any pre-existing defects found (not blocking unless new)

**Stage 2 — Verdict comment** (posted after Stage 1 is complete):
- PASS or FAIL
- If FAIL: numbered list of blocking findings only
- If PASS: confirmation that all acceptance criteria are met

Both comments must appear on the active PR before any chat reply is considered a verdict.
A chat reply without both PR deliverables is an incomplete verdict (§5.2 of root AGENTS.md).

### 3.2 Infrastructure-specific checks (all mandatory per PE)

Run each check and paste verbatim output in the Stage 1 comment:

#### 3.2.1 Shell script header compliance
```bash
# Every shell script in the PR diff must have both lines
grep -rn "#!/usr/bin/env bash" <changed_scripts>
grep -rn "set -euo pipefail"   <changed_scripts>
```
Missing either line on any script → **blocking finding**.

#### 3.2.2 Variable quoting
```bash
# Unquoted variable references are a security risk
grep -Pn '\$\{?[A-Za-z_][A-Za-z0-9_]*\}?' <changed_scripts> | grep -v '"'
# Review output — any unquoted $VAR in non-trivial context → blocking finding
```

#### 3.2.3 Port binding isolation
```bash
# External-facing ports must bind to 127.0.0.1, never 0.0.0.0
grep -rn "0\.0\.0\.0" <changed_compose_files> <changed_scripts>
```
Any `0.0.0.0:X:X` mapping → **blocking finding**.

#### 3.2.4 Docker image tag policy
```bash
# No :latest tags allowed — must use pinned, explicit tags
grep -rn ":latest" <changed_dockerfiles> <changed_compose_files>
```
Any `:latest` tag → **blocking finding**.

#### 3.2.5 CI secret handling
```bash
# Only ${{ secrets.X }} pattern is permitted — no inline secrets
grep -rn "secrets\." .github/workflows/<changed_workflows>
# Review: any pattern other than ${{ secrets.X }} → blocking finding
```

#### 3.2.6 Container isolation — §5.4 hard limit
```bash
# ELIS repo path must NEVER appear in any volumes: mount
grep -rn "volumes:" <changed_compose_files> | grep -i "elis"
grep -rn "ELIS" <changed_compose_files>
```
Any ELIS repo path in a `volumes:` mount → **§5.4 hard limit violation — blocking finding**.
This check is non-negotiable and cannot be waived by PM.

#### 3.2.7 CI job/step naming
```bash
# Every job and step in changed workflows must have a name:
python -c "
import yaml, sys
with open('<workflow_file>') as f:
    w = yaml.safe_load(f)
for job_id, job in w.get('jobs', {}).items():
    assert 'name' in job, f'Job {job_id} missing name:'
    for i, step in enumerate(job.get('steps', [])):
        assert 'name' in step, f'Job {job_id} step {i} missing name:'
print('CI naming: PASS')
"
```
Missing `name:` on any job or step → **blocking finding**.

#### 3.2.8 YAML schema / lint
```bash
# Validate changed YAML files
python -c "import yaml; yaml.safe_load(open('<file>'))" && echo "YAML valid"
# Or use yamllint if available
yamllint <changed_yaml_files>
```
Invalid YAML → **blocking finding**.

### 3.3 Adversarial tests (at least one per PE)

Write and run at least one negative-path test targeting the infrastructure change.
Examples:
- Confirm a workflow step fails correctly when a required secret is absent
- Confirm `docker compose config` fails on an intentionally malformed compose file
- Confirm a shell script with `set -euo pipefail` exits non-zero on a missing variable

Paste the adversarial test command and its output verbatim in the Stage 1 comment.

---

## 4. REVIEW file

File: `REVIEW_PE_INFRA_<N>.md` (or `REVIEW_PE_<ID>.md` per PE naming convention)
Location: repo root
Owned by: Validator

Required sections (enforced by `scripts/check_review.py`):
- `### Verdict` — PASS / FAIL
- `### Gate results` — black / ruff / pytest + infra-specific check results
- `### Scope` — pasted `git diff --name-status` output
- `### Required fixes` — blocking findings (empty section if PASS)
- `### Evidence` — at least one fenced code block with actual command output

Before pushing the REVIEW file:
```bash
REVIEW_FILE=REVIEW_PE_<N>.md python scripts/check_review.py
```
Do not push a REVIEW file that exits non-zero.

---

## 5. Formal GitHub PR review

After posting both Stage 1 and Stage 2 comments:
- PASS → `gh pr review <PR_NUMBER> --approve --body "PASS — all infra checks met. See REVIEW file."`
- FAIL → `gh pr review <PR_NUMBER> --request-changes --body "FAIL — blocking findings listed in Stage 2 comment and REVIEW file."`

Single-account fallback: if reviewer and PR author share the same GitHub account and GitHub
blocks the review action, post FAIL verdict as a plain comment and apply `pm-review-required` label:
```bash
gh pr edit <PR_NUMBER> --add-label "pm-review-required"
```

---

## 6. Do-not list (infra-val specific)

- Do not implement or modify infrastructure scope.
- Do not write `HANDOFF.md`.
- Do not push to feature branches except for `REVIEW_PE_<N>.md` and adversarial test files.
- Do not issue PASS while CI is failing — wait for green CI before Stage 2.
- Do not waive the §5.4 ELIS mount isolation check under any circumstances.
- Do not skip the port binding check (§3.2.3) even for internal-only compose changes.
- Do not self-start — always wait for PM or CI Gate 1 assignment.
- Do not deliver a verdict only in chat — both PR comment and formal review are required.
- Do not push a REVIEW file without running `check_review.py` first.

---

## 7. Escalation triggers

Escalate to PM (do not proceed autonomously) when:
- A §5.4 violation (ELIS mount) is detected — always escalate regardless of iteration count.
- More than two FAIL/fix iterations on a single PE.
- Scope of PR changes extends beyond infrastructure domain.
- Inline secret value is detected in any PR file — notify PM immediately, do not include value in any output.
- CI is failing for reasons unrelated to the PE (pre-existing CI breakage).

---

End of AGENTS.md — workspace-infra-val
