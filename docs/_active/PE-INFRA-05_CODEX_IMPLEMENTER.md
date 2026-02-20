# PE-INFRA-05 — CODEX Implementer Prompt
## Validator Evidence Enforcement + Two-Stage Comment Protocol

**PE:** PE-INFRA-05
**Base branch:** resolve from `CURRENT_PE.md`
**Target:** `release/2.0` (or whatever base branch CURRENT_PE.md specifies)
**Risk:** Low
**Effort:** ~6h
**Dependencies:** PE-INFRA-04 (auto-assign-validator, auto-merge-on-pass — both in place)

---

## Background and motivation

During post-v2.0.0 validation of PR #258, the Validator (Claude Code) issued a PASS verdict
before completing content verification — specifically before reading `RELEASE_PLAN_v2.0.md`
to check Section 5 compliance claims. The violation was caught by PM human review, not by
any automated gate.

Root cause: the auto-merge gate (`auto-merge-on-pass.yml`) only checks that the REVIEW file
contains a valid `### Verdict` line. It does not verify that the REVIEW file contains actual
evidence (command output, file reads) supporting the verdict. A Validator can write PASS in a
REVIEW file with empty or missing evidence sections and the gate will merge.

This PE closes that gap with two complementary mechanisms:

1. **`scripts/check_review.py`** — validates that a REVIEW file is structurally complete
   and contains at least one evidence block before the auto-merge gate proceeds.
2. **Two-stage PR comment protocol** — the REVIEW file template gains a mandatory
   `### Evidence` section; `auto-merge-on-pass.yml` runs `check_review.py` as Gate 2b
   before merge.

---

## Acceptance criteria

### AC-1 — `check_review.py` validates REVIEW file structure

`python scripts/check_review.py` (with `REVIEW_FILE` env var pointing to a REVIEW file) must:

- Exit 1 if the file is missing.
- Exit 1 if any of the following required sections are absent:
  - `### Verdict`
  - `### Gate results`
  - `### Scope`
  - `### Required fixes`
  - `### Evidence`
- Exit 1 if the `### Evidence` section contains no fenced code block (``` ``` ```).
  A REVIEW file with `### Evidence\n\n(none)` or empty evidence is invalid.
- Exit 1 if `### Verdict` is FAIL and `### Required fixes` body is empty or contains
  only "None" (a FAIL verdict must always list at least one required fix).
- Exit 0 on a structurally valid REVIEW file.
- Support `REVIEW_FILE` env var (exact path) consistent with `parse_verdict.py`.
- Support `REVIEW_PATH` env var (directory scan by mtime) as fallback.

### AC-2 — Gate 2b in `auto-merge-on-pass.yml`

`auto-merge-on-pass.yml` must run `check_review.py` as a new step (`gate-2b`) between
the parse-verdict step and the auto-merge step. Auto-merge must not proceed if Gate 2b
fails. Specifically:

- Gate 2b runs only when `verdict == 'PASS'` (skip on FAIL or IN_PROGRESS).
- If Gate 2b exits 1, the workflow posts a comment to the PR:
  `Gate 2b — REVIEW file missing evidence section. Validator must update REVIEW file
  with command outputs before merge.`
  and sets the workflow to failure (no merge).
- If Gate 2b exits 0, auto-merge proceeds as before.

### AC-3 — `check_review.py` added to CI

`ci.yml` must include a `review-evidence-check` job that runs `check_review.py` on any
`REVIEW_*.md` file changed in the PR diff. If no REVIEW file is changed, the job exits 0
(skip). This prevents a Validator from committing an evidence-free REVIEW file.

### AC-4 — REVIEW file template updated

`reports/agent_activity/templates/REVIEW_REQUEST_TEMPLATE.md` must gain a mandatory
`### Evidence` section with the following subsections:

```markdown
### Evidence

#### Files read
- `<path>` — <what was checked>

#### Commands run
\```
<paste command and output here>
\```

#### Key claims verified
| Claim | Source | Result |
|-------|--------|--------|
| <claim> | <file or command output> | PASS / FAIL |
```

The template must include a comment: `<!-- At least one fenced code block required in
this section. check_review.py will fail if Evidence section is empty. -->`

### AC-5 — AGENTS.md updated

Add a new rule under §2.4 (Evidence-first reporting):

> **2.4.1 REVIEW file evidence requirement (hard)**
> Every `REVIEW_PE<N>.md` file MUST contain a `### Evidence` section with at least one
> fenced code block showing actual command output or file content. A verdict without
> inline evidence is invalid and will be rejected by Gate 2b.
> The Validator MUST complete all verification steps before writing the `### Verdict`
> line. Verdict-before-evidence is a workflow violation regardless of the final verdict
> value.

---

## Deliverables

### New files

| File | Purpose |
|------|---------|
| `scripts/check_review.py` | REVIEW file evidence validator |
| `tests/test_check_review.py` | Unit tests (see §Test requirements) |

### Modified files

| File | Change |
|------|--------|
| `.github/workflows/auto-merge-on-pass.yml` | Add Gate 2b step running `check_review.py` |
| `.github/workflows/ci.yml` | Add `review-evidence-check` job |
| `reports/agent_activity/templates/REVIEW_REQUEST_TEMPLATE.md` | Add `### Evidence` section |
| `AGENTS.md` | Add §2.4.1 evidence requirement rule |
| `HANDOFF.md` | Document this PE per standard format |

---

## `check_review.py` design

```python
"""check_review.py — validate REVIEW file evidence completeness.

Used by auto-merge-on-pass.yml (Gate 2b) and ci.yml (review-evidence-check).
Exits 1 if required sections are missing or Evidence section has no code block.
Exits 0 on a valid REVIEW file.

File selection: same priority as parse_verdict.py:
  1. REVIEW_FILE env var — exact path.
  2. REVIEW_PATH env var — directory scan by mtime. Default ".".
"""

REQUIRED_SECTIONS = [
    "### Verdict",
    "### Gate results",
    "### Scope",
    "### Required fixes",
    "### Evidence",
]

# Evidence section must contain at least one fenced code block.
# Scan only from ### Evidence header to next ### header (or EOF).
```

Key implementation notes:
- Reuse `_find_review_file()` pattern from `parse_verdict.py` for file selection.
- To check the Evidence section: locate `### Evidence`, collect lines until the next
  `###` header or EOF, check for at least one line starting with ` ``` `.
- To check FAIL + empty Required fixes: locate `### Required fixes`, collect body
  lines until next `###`, strip, check if all remaining non-empty lines are "None".
- Do NOT re-parse verdict — that is `parse_verdict.py`'s responsibility.

---

## Test requirements (`tests/test_check_review.py`)

Minimum 8 test cases covering:

| # | Scenario | Expected exit |
|---|----------|--------------|
| 1 | Missing REVIEW_FILE | 1 |
| 2 | Missing `### Evidence` section | 1 |
| 3 | `### Evidence` present but no code block | 1 |
| 4 | FAIL verdict + empty Required fixes | 1 |
| 5 | FAIL verdict + "None" as Required fixes | 1 |
| 6 | PASS verdict + valid Evidence with code block | 0 |
| 7 | FAIL verdict + at least one fix listed | 0 |
| 8 | Multi-section REVIEW (re-validation appended) — last Evidence section checked | 0 |

Tests must use `tmp_path` fixtures (no real REVIEW files). Do not depend on any real
repo file for passing tests.

---

## Scope constraints (AGENTS.md §2.1)

- Do NOT modify `parse_verdict.py` — verdict parsing is separate from evidence validation.
- Do NOT modify existing REVIEW files — template change is forward-only.
- Do NOT change Gate 1 (`auto-assign-validator.yml`) — Gate 2b is an addition to Gate 2.
- `check_review.py` must be importable: no `sys.exit()` at module level.

---

## Quality gates (run before updating HANDOFF.md)

```
python -m black --check scripts/check_review.py tests/test_check_review.py
python -m ruff check scripts/check_review.py tests/test_check_review.py
python -m pytest tests/test_check_review.py -v
python -m pytest -q   # full suite — must stay green
```

---

## HANDOFF.md requirements

Update `HANDOFF.md` with:
- Summary covering all 5 ACs
- Files Changed list (new + modified)
- Acceptance Criteria table (AC-1 through AC-5)
- Validation Commands with pasted output (pytest results, black, ruff)
- Evidence section: paste actual `check_review.py` runs against a valid and an invalid
  temp REVIEW file showing correct exit codes
- Status Packet fields (AGENTS.md §6)

HANDOFF.md must be committed before opening the PR (AGENTS.md §5.1 step order).

---

## Workflow — two-agent protocol for this PE

| Step | Owner | Action |
|------|-------|--------|
| 0 | PM | Update `CURRENT_PE.md`: PE=PE-INFRA-05, Branch=chore/pe-infra-05-review-evidence, roles |
| 1 | CODEX | Read `CURRENT_PE.md`, `AGENTS.md`, this file, `HANDOFF.md` |
| 2 | CODEX | Create branch `chore/pe-infra-05-review-evidence` from base branch |
| 3 | CODEX | Implement all deliverables (AC-1 through AC-5) |
| 4 | CODEX | Run quality gates (black, ruff, pytest) |
| 5 | CODEX | Update `HANDOFF.md` with evidence |
| 6 | CODEX | Verify clean tree (`git status -sb`) |
| 7 | CODEX | Push branch + open PR targeting base branch |
| 8 | CODEX | Post Status Packet as PR comment |
| 9 | PM | Notify Claude Code (Validator) to start |
| 10 | Claude Code | Read REVIEW from HANDOFF.md, run check_review.py adversarially |
| 11 | Claude Code | Post evidence comment (files read, commands run) |
| 12 | Claude Code | Post verdict comment + commit REVIEW_PE_INFRA_05.md |
| 13 | PM | Merge if PASS |

**Note on step 11/12:** The Validator MUST post an evidence-only comment first (step 11),
then the verdict (step 12). This is the two-stage protocol this PE enforces for all future
PEs — and the Validator must model it correctly during this PE's own validation.

---

*Authored by: Claude Code (Validator) — 2026-02-20*
*Ratified by: PM before CODEX begins*
