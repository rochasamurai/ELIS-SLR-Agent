# PE-INFRA-03 — Implementer Assignment for CODEX
**Date:** 2026-02-19
**Agent:** CODEX
**Role:** Implementer
**Branch:** `chore/pe-infra-03-plan-agnostic`
**Base:** `release/2.0`
**PR title:** `chore(infra): release-plan agnostic workflow — CURRENT_PE.md as single source of truth (PE-INFRA-03)`

---

## Design rationale (read before implementing)

The current workflow is coupled to a specific release in three ways:

| Hardcoded reference | Appears in |
|---|---|
| `release/2.0` (base branch) | AGENTS.md §2.1, §2.6, §5.1, §6.3, §6.5, CLAUDE.md, CODEX.md, CURRENT_PE.md |
| `RELEASE_PLAN_v2.0.md` (plan file) | AGENTS.md §1, §5.1, §5.2, §2.9, CLAUDE.md, CODEX.md |
| `docs/_active/` (plan location) | AGENTS.md §1 |

When the project moves to v3.0 or any other release line, every one of those files must be edited manually — creating drift risk and the possibility of agents reading stale references mid-session.

### Single source of truth: `CURRENT_PE.md`

`CURRENT_PE.md` is already the PM-maintained runtime configuration file introduced in PE-INFRA-02.
It is the correct place to declare the active release context because:

- It is committed to the repo and readable by both agents at Step 0.
- It is already updated by the PM at the start of every PE.
- It survives context compression (agents re-read it at every mid-session checkpoint).
- It is the only file the PM needs to edit when switching release lines.

All other files (`AGENTS.md`, `CLAUDE.md`, `CODEX.md`) become release-agnostic by replacing
hardcoded references with the instruction: **"read the value from `CURRENT_PE.md`"**.

---

## 0) Preflight — before touching any file

1. Read `AGENTS.md` fully.
2. Read `CURRENT_PE.md` — confirm your role is `Implementer`.
3. Run and paste in opening Status Packet to PM:

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
git checkout -b chore/pe-infra-03-plan-agnostic origin/release/2.0
git status -sb
# Expected: nothing to commit, clean tree
```

---

## 2) Acceptance Criteria

Implement **all four ACs** below. No other files may be modified.

---

### AC-1 · Extend `CURRENT_PE.md` — add release context block

`CURRENT_PE.md` must become the single source of truth for all release-specific values.

Replace the entire contents of `CURRENT_PE.md` with this canonical template:

```markdown
# Current PE Assignment

> Maintained by PM. Update ALL fields at the start of every new PE or release.
> Both agents read this file as Step 0. It is the only file that needs editing
> when switching release lines.

---

## Release context

| Field          | Value                              |
|----------------|------------------------------------|
| Release        | v2.0                               |
| Base branch    | release/2.0                        |
| Plan file      | docs/_active/RELEASE_PLAN_v2.0.md  |
| Plan location  | docs/_active/                      |

---

## Current PE

| Field   | Value                                    |
|---------|------------------------------------------|
| PE      | PE-INFRA-03                              |
| Branch  | feature/pe-infra-03-plan-agnostic        |

---

## Agent roles

| Agent       | Role        |
|-------------|-------------|
| CODEX       | Implementer |
| Claude Code | Validator   |

---

## PM instructions

1. At the start of every PE: update `PE`, `Branch`, and `Agent roles` table.
2. At the start of every new release: update the entire `Release context` table.
3. Commit and push this file to the base branch before notifying agents to start.
4. If this file is absent or incomplete, agents must stop and notify PM.

## Agent instructions

- Step 0: read `Release context` to know the base branch and plan file for this session.
- Never hardcode `release/2.0` or `RELEASE_PLAN_v2.0.md` — always resolve from this file.
- If a field in this file is blank or missing, stop and notify PM.
```

**Verification:**

```bash
grep "Base branch"   CURRENT_PE.md   # must return the field
grep "Plan file"     CURRENT_PE.md   # must return the field
grep "Release"       CURRENT_PE.md   # must return the field
grep "Plan location" CURRENT_PE.md   # must return the field
```

---

### AC-2 · Update `AGENTS.md` — replace all hardcoded release references

#### Target references to replace

Search for every hardcoded occurrence of the following strings:

```bash
grep -n "release/2\.0"            AGENTS.md
grep -n "RELEASE_PLAN_v2\.0\.md"  AGENTS.md
grep -n "docs/_active/"           AGENTS.md
```

Paste the output in `HANDOFF.md` before editing, so the Validator can verify every hit was addressed.

#### Replacement rules

Apply these substitutions **everywhere** they appear in AGENTS.md:

| Find (hardcoded) | Replace with (agnostic instruction) |
|---|---|
| `release/2.0` (as a branch name in commands) | `<base-branch>` with a footnote: `# read base branch from CURRENT_PE.md → "Base branch"` |
| `RELEASE_PLAN_v2.0.md` | `<plan-file>` with a footnote: `# read plan file path from CURRENT_PE.md → "Plan file"` |
| `docs/_active/RELEASE_PLAN_v2.0.md` | `<plan-location>/<plan-file>` with a footnote pointing to CURRENT_PE.md |
| `origin/release/2.0` (in git commands) | `origin/<base-branch>` |

#### Specific sections requiring edits

**§1 Canonical references** — replace:
```
1. `docs/_active/RELEASE_PLAN_v2.0.md` (authoritative plan + acceptance criteria)
```
with:
```
1. `CURRENT_PE.md` → read `Plan file` field to locate the authoritative plan for this release.
   Example for v2.0: `docs/_active/RELEASE_PLAN_v2.0.md`
```

**§2.1 One PE = one branch = one PR** — replace:
```
Every PE is implemented on its own feature branch created from `release/2.0`.
The PR base is `release/2.0` unless the release plan explicitly states otherwise.
```
with:
```
Every PE is implemented on its own feature branch created from the base branch
declared in `CURRENT_PE.md` → `Base branch` field.
The PR base is that same branch unless the release plan explicitly states otherwise.
```

**§2.6 Rebase after every merge** — replace the two git commands:
```bash
git fetch origin
git rebase origin/release/2.0
```
with:
```bash
# BASE=$(grep "Base branch" CURRENT_PE.md | awk '{print $NF}')
git fetch origin
git rebase origin/$BASE
```

**§2.9 Mid-session context checkpoint** (added in PE-INFRA-02) — replace step 1:
```
1. Re-read the PE acceptance criteria in `RELEASE_PLAN_v2.0.md`.
```
with:
```
1. Re-read `CURRENT_PE.md` → locate `Plan file` → re-read the PE acceptance criteria in that file.
```

**§5.1 Implementer workflow** — replace step 2 git commands:
```bash
git rebase origin/release/2.0
git checkout -b feature/pe<N>-<scope> origin/release/2.0
```
with:
```bash
# BASE=$(grep "Base branch" CURRENT_PE.md | awk '{print $NF}')
git rebase origin/$BASE
git checkout -b feature/pe<N>-<scope> origin/$BASE
```

Also replace step 4 scope gate:
```bash
git diff --name-status origin/release/2.0..HEAD
```
with:
```bash
# BASE=$(grep "Base branch" CURRENT_PE.md | awk '{print $NF}')
git diff --name-status origin/$BASE..HEAD
```

**§5.2 Validator workflow** — same scope gate replacement as §5.1 step 4.

**§6.3 Status Packet — Scope evidence** — replace:
```bash
git diff --name-status origin/release/2.0..HEAD
git diff --stat        origin/release/2.0..HEAD
```
with:
```bash
# BASE=$(grep "Base branch" CURRENT_PE.md | awk '{print $NF}')
git diff --name-status origin/$BASE..HEAD
git diff --stat        origin/$BASE..HEAD
```

**§6.5 Status Packet — PR evidence** — replace:
```bash
gh pr list --state open --base release/2.0
```
with:
```bash
# BASE=$(grep "Base branch" CURRENT_PE.md | awk '{print $NF}')
gh pr list --state open --base $BASE
```

**§12.1 Branch protection** — replace inline mention of `release/2.0` with:
```
the base branch declared in `CURRENT_PE.md`
```

**Verification after all edits:**

```bash
grep -n "release/2\.0"           AGENTS.md
# Must return zero hits.

grep -n "RELEASE_PLAN_v2\.0\.md" AGENTS.md
# Must return zero hits.

grep -n "CURRENT_PE.md"          AGENTS.md
# Must return ≥ 8 hits (§1, §2.1, §2.6, §2.9, §5.1, §5.2, §6.3, §6.5, §12.1).
```

---

### AC-3 · Update `CLAUDE.md` and `CODEX.md` — remove hardcoded release references

#### In `CLAUDE.md`

Find and replace every hardcoded occurrence:

```bash
grep -n "release/2\.0\|RELEASE_PLAN_v2\.0\.md" CLAUDE.md
```

Paste grep output in HANDOFF.md before editing.

Apply these replacements:

In **Step 0 — Session start**, replace:
```
2. Read `CURRENT_PE.md` → confirm your role for this PE.
```
with:
```
2. Read `CURRENT_PE.md`:
   - Confirm your role (`Agent roles` table).
   - Note `Base branch` and `Plan file` — use these in every git command and plan reference.
   - If any field is blank or the file is absent → stop and notify PM.
```

In **§2.9 Mid-session checkpoint**, replace:
```
1. Re-read PE acceptance criteria in `RELEASE_PLAN_v2.0.md`.
```
with:
```
1. Re-read `CURRENT_PE.md` → `Plan file` field → re-read PE acceptance criteria in that file.
```

In **§6.3 Scope evidence**, replace:
```bash
git diff --name-status origin/release/2.0..HEAD
git diff --stat        origin/release/2.0..HEAD
```
with:
```bash
# BASE=$(grep "Base branch" CURRENT_PE.md | awk '{print $NF}')
git diff --name-status origin/$BASE..HEAD
git diff --stat        origin/$BASE..HEAD
```

In **§6.5 PR evidence**, replace:
```bash
gh pr list --state open --base release/2.0
```
with:
```bash
# BASE=$(grep "Base branch" CURRENT_PE.md | awk '{print $NF}')
gh pr list --state open --base $BASE
```

**Verification:**

```bash
grep -n "release/2\.0\|RELEASE_PLAN_v2\.0\.md" CLAUDE.md
# Must return zero hits.
```

#### In `CODEX.md`

Apply identical replacements as CLAUDE.md above (the two files must remain mirrors).

**Verification:**

```bash
grep -n "release/2\.0\|RELEASE_PLAN_v2\.0\.md" CODEX.md
# Must return zero hits.

# Do-not lists must still be identical:
diff <(grep "^- " CLAUDE.md) <(grep "^- " CODEX.md)
# Must return empty.
```

---

### AC-4 · Update `scripts/check_role_registration.py` — validate release context fields

Extend the script introduced in PE-INFRA-02 to also validate the new release context block.

Add the following checks **after** the existing agent-role checks, before the final success message:

```python
# Release context checks
REQUIRED_RELEASE_FIELDS = ["Release", "Base branch", "Plan file", "Plan location"]

for field in REQUIRED_RELEASE_FIELDS:
    if not any(line.strip().startswith(f"| {field}") for line in lines):
        print(f"ERROR: Release context field missing: '{field}'")
        sys.exit(1)
    # Check the value cell is not empty
    for line in lines:
        if line.strip().startswith(f"| {field}"):
            parts = [p.strip() for p in line.split("|")]
            # parts[0]=empty, parts[1]=field name, parts[2]=value, parts[3]=empty
            if len(parts) < 3 or not parts[2]:
                print(f"ERROR: Release context field '{field}' has no value.")
                sys.exit(1)
```

**Adversarial tests — run and paste all outputs verbatim in HANDOFF.md:**

```bash
# Test 1 — valid full file (existing test, must still pass)
python scripts/check_role_registration.py
# Expected: exit 0, "CURRENT_PE.md OK — role registration valid."

# Test 2 — missing "Base branch" field
python - <<'EOF'
content = open("CURRENT_PE.md").read()
bad = content.replace("| Base branch", "| Base branch REMOVED")
open("/tmp/CURRENT_PE_nobase.md", "w").write(bad)
EOF
CURRENT_PE_PATH=/tmp/CURRENT_PE_nobase.md python scripts/check_role_registration.py
# Expected: exit 1, "ERROR: Release context field missing: 'Base branch'"

# Test 3 — "Plan file" field present but empty value
python - <<'EOF'
import re
content = open("CURRENT_PE.md").read()
bad = re.sub(r'\| Plan file\s+\|[^|]+\|', '| Plan file      |                |', content)
open("/tmp/CURRENT_PE_emptyplan.md", "w").write(bad)
EOF
CURRENT_PE_PATH=/tmp/CURRENT_PE_emptyplan.md python scripts/check_role_registration.py
# Expected: exit 1, "ERROR: Release context field 'Plan file' has no value."
```

---

## 3) Scope gate (run before every commit)

```bash
# BASE=$(grep "Base branch" CURRENT_PE.md | awk '{print $NF}')
git diff --name-status origin/$BASE..HEAD
```

Expected files — **only these, nothing else:**

```
M    CURRENT_PE.md
M    AGENTS.md
M    CLAUDE.md
M    CODEX.md
M    scripts/check_role_registration.py
M    HANDOFF.md
```

If any other file appears → stop, do not commit, notify PM.

---

## 4) Quality gates

```bash
python -m black --check .
python -m ruff check .
python -m pytest -q
```

All three must pass. Paste full output verbatim in `HANDOFF.md`.

---

## 5) HANDOFF.md (commit before `git push`)

Must contain all five standard sections. Under `## Validation Commands`, paste verbatim:

- `grep -n "release/2\.0" AGENTS.md` → must show zero hits
- `grep -n "release/2\.0\|RELEASE_PLAN" CLAUDE.md` → must show zero hits
- `grep -n "release/2\.0\|RELEASE_PLAN" CODEX.md` → must show zero hits
- All 3 adversarial test outputs from AC-4
- black / ruff / pytest gate outputs

Also paste under `## Design Decisions`:
> "CURRENT_PE.md is the single source of truth for all release-specific values.
>  All other workflow files are now release-agnostic. To move to v3.0, the PM
>  edits only CURRENT_PE.md — no other workflow file requires changes."

---

## 6) Session-end checklist

```bash
git status -sb
# Must show: nothing to commit, working tree clean
```

---

## 7) Open PR

```bash
# BASE=$(grep "Base branch" CURRENT_PE.md | awk '{print $NF}')
gh pr create \
  --base $BASE \
  --head chore/pe-infra-03-plan-agnostic \
  --title "chore(infra): release-plan agnostic workflow — CURRENT_PE.md as single source of truth (PE-INFRA-03)" \
  --body "$(cat <<'EOF'
## Summary
Removes all hardcoded release references (release/2.0, RELEASE_PLAN_v2.0.md)
from AGENTS.md, CLAUDE.md, CODEX.md. CURRENT_PE.md is now the single source
of truth for base branch, plan file path, and plan location.
To adopt a new release line, PM edits only CURRENT_PE.md.

## Files Changed
- CURRENT_PE.md  (extended with release context block)
- AGENTS.md      (all hardcoded release references replaced)
- CLAUDE.md      (all hardcoded release references replaced)
- CODEX.md       (all hardcoded release references replaced)
- scripts/check_role_registration.py (release context field validation added)

## Test plan
- check_role_registration.py: 3 new adversarial tests (valid, missing field, empty value)
- grep verification: zero hits for release/2.0 and RELEASE_PLAN_v2.0.md in all workflow files
- black / ruff / pytest: all passing

## Status Packet
[paste §6.1–§6.5 outputs here]
EOF
)"
```

---

## 8) Deliver Status Packet to PM

Post the full Status Packet (§6.1–§6.5) and write:

> "PE-INFRA-03 implementation complete. Requesting PM assignment of Validator."

---

## Deliverables checklist

- [ ] `CURRENT_PE.md` — extended with Release context table (4 fields, all populated)
- [ ] `AGENTS.md` — zero hits for `release/2.0` and `RELEASE_PLAN_v2.0.md`
- [ ] `CLAUDE.md` — zero hits for `release/2.0` and `RELEASE_PLAN_v2.0.md`
- [ ] `CODEX.md` — zero hits for `release/2.0` and `RELEASE_PLAN_v2.0.md`
- [ ] `CLAUDE.md` and `CODEX.md` do-not lists still identical (`diff` returns empty)
- [ ] `scripts/check_role_registration.py` — 3 new release-context checks added
- [ ] 3 new adversarial test outputs pasted verbatim in `HANDOFF.md`
- [ ] Scope gate shows exactly 6 modified files (`HANDOFF.md` included), nothing else
- [ ] black / ruff / pytest all passing — output pasted verbatim
- [ ] `HANDOFF.md` committed on branch before PR opened
- [ ] PR open, Status Packet delivered to PM
