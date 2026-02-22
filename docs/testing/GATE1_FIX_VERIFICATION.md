# Gate 1 Fix Verification — PE-OC-12

## Date

2026-02-22

## Scope

PE-OC-12 fixes the perpetual `failure` status of the `Auto-assign Validator` workflow
(`auto-assign-validator.yml`). Gate 1 automation was broken on every PR since PE-OC-07
introduced it.

---

## Root Cause

### Symptom

Every `Auto-assign Validator` run completed with `conclusion: failure`. The "Notify PM
on failure" step posted `⚠️ Gate 1 — manual PM review required` to every PR, forcing PM
to manually assign the Validator on every single PE.

### Investigation

```text
gh api repos/rochasamurai/ELIS-SLR-Agent/actions/runs/22283804534/jobs \
  --jq '.jobs[0].steps[] | {name: .name, conclusion: .conclusion}'

Set up job              → success
Checkout PR head        → success
Set up Python           → success
Install dependencies    → success
Resolve PR number/body  → success
Verify Status Packet    → FAILURE   ← root cause
Verify HANDOFF.md       → skipped
Verify role registration→ skipped
Auto-assign Validator   → skipped
Notify PM on failure    → success   ← posts manual-review comment
```

### Root cause

`check_status_packet.py` read the PR body via the `PR_BODY` environment variable and
checked for section headers (`### Verdict`, `### Branch / PR`, `### Gate results`,
`### Scope`, `### Ready to merge`) that agents **never include in PR bodies**.

Agents write the Status Packet into `HANDOFF.md` under:
- `## Status Packet`
- `### 6.1 Working-tree state`
- `### 6.2 Repository state`
- `### 6.3 Scope evidence`
- `### 6.4 Quality gates`
- `### 6.5 Ready to merge`

Because the PR body never contained those headers, the script always exited 1,
the auto-assign step was skipped, and the "manual review required" comment was always
posted.

---

## Fix Applied

### `scripts/check_status_packet.py`

Rewrote to read `HANDOFF.md` directly from the checked-out working tree (using
`HANDOFF_PATH` env var with fallback to `HANDOFF.md`), mirroring the approach used
by `check_handoff.py`. Updated required sections to match HANDOFF.md Status Packet
format (`## Status Packet`, `### 6.1` … `### 6.5`).

### `.github/workflows/auto-assign-validator.yml`

Removed the `env: PR_BODY: ${{ steps.pr.outputs.body }}` from the "Verify Status
Packet completeness" step — no longer needed since the script reads from disk.

### `tests/test_check_status_packet.py`

Added 8 unit tests covering:
- Full HANDOFF.md with all sections → exit 0
- Missing `## Status Packet` header → exit 1
- Missing individual `### 6.x` subsections → exit 1
- Empty file → exit 1
- Missing file → exit 1
- Custom `HANDOFF_PATH` env var → exit 0

---

## Acceptance Criteria Results

### AC-1 · `Auto-assign Validator` workflow completes with `success` on a new PR

**Evidence (local simulation):**

```text
# Simulate the check_status_packet.py check against a real HANDOFF.md

HANDOFF_PATH=HANDOFF.md python scripts/check_status_packet.py
Status Packet OK — all required sections present in HANDOFF.md.
rc: 0
```

The HANDOFF.md at repo root contains all required Status Packet sections
(`## Status Packet`, `### 6.1`–`### 6.5`). The script now exits 0 instead of 1.

**Note:** AC-1 will be fully confirmed by observing a successful `Auto-assign Validator`
CI run on this PR (#274). The workflow run URL will be linked here once the CI
completes.

### AC-2 · Validator is assigned automatically without PM manual intervention

Same dependency as AC-1 — will be confirmed by the CI run on this PR.

---

## Quality Gates

```text
python -m black --check .   → 115 files would be left unchanged
python -m ruff check .      → All checks passed
python -m pytest            → 542 passed, 17 warnings
```

8 new tests in `tests/test_check_status_packet.py` (was 534, now 542).
