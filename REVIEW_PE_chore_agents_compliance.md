# REVIEW — chore/agents-compliance-automation (PR #228)

## Agent update — Claude Code / chore-agents-compliance / 2026-02-18

### Verdict
PASS (with 1 non-blocking warning)

### Branch / PR
Branch: `chore/agents-compliance-automation`
PR: #228 (open)
Base: `release/2.0`

### Gate results
black: PASS (`python -m black --check scripts/agents_compliance_check.py`)
ruff:  PASS (`python -m ruff check scripts/agents_compliance_check.py`)
pytest: 437 passed, 0 failed, 17 warnings (deprecation only — pre-existing, not this PR)

### Scope (diff vs `origin/release/2.0`)
```
A  .github/workflows/agents-compliance.yml
M  .github/workflows/ci.yml
M  .github/workflows/deep-review.yml
A  scripts/agents_compliance_check.py
```
Clean — all 4 files are directly within the stated purpose of the PR. No regressions.

### Acceptance review

**`scripts/agents_compliance_check.py`**
- Branch naming validation (`ALLOWED_BRANCH_PATTERNS`) matches AGENTS.md §4.1. ✓
- PE branch HANDOFF.md checks (file exists + appears in changed files) enforce §2.7. ✓
- Cross-PE REVIEW file contamination detection is correct. ✓
- Chore branch warnings for `elis/` and `scripts/` touches are appropriate. ✓
- Three-dot diff (`origin/{base_ref}...HEAD`) is the correct comparison for PR scope. ✓
- `check_repo_prereqs()` references are all live files in the repo. ✓

**`.github/workflows/agents-compliance.yml`**
- Triggers on `pull_request` to `release/2.0` — correct. ✓
- Runs on opened/synchronize/reopened/edited/ready_for_review — correct events. ✓
- Reads the GitHub event payload to resolve base/head refs — correct pattern. ✓

**`.github/workflows/ci.yml` + `deep-review.yml`**
- Add `release/2.0` to `pull_request.branches` — critical fix.
  Previously, CI and deep-review did not run on PE PRs targeting `release/2.0`. ✓

### Warning (non-blocking)

**`agents-compliance.yml` — shallow base fetch may miss merge base on old branches**

```yaml
- name: Fetch base branch
  run: |
    git fetch origin "${{ github.event.pull_request.base.ref }}" --depth=1
```

The `--depth=1` fetches only the tip commit of `release/2.0`. The three-dot diff
(`origin/release/2.0...HEAD`) must compute the merge base between the two branches.
If `release/2.0` has advanced many commits since the feature branch was created,
the merge base may not be in the fetched history, causing the diff to fail silently
or fall back to a two-dot comparison (reporting all differences, not just PR changes).

**Recommended fix** (can be applied in a follow-up PR or in this branch before merge):
```yaml
- name: Fetch base branch
  run: |
    git fetch origin "${{ github.event.pull_request.base.ref }}"
```
Remove `--depth=1` entirely. Alternatively use `--depth=50` if fetch time is a concern.

### Required fixes (if FAIL)
None — verdict is PASS.

### Ready to merge
YES — pending PM go-ahead and resolution of PR #227 (which adds the AGENTS.md
enforcement documentation that PR #228 implements).

### Note on merge order
PR #227 (AGENTS.md updates + PR template) and PR #228 (compliance automation)
are complementary. PR #228 implements the Tier 1 CI enforcement described in
PR #227 §12. Suggested merge order: #227 first, then #228 to avoid a brief
window where §12 describes enforcement that hasn't landed yet. Either order is
technically safe — the workflow is additive and does not break anything on merge.

### Next
PM merges PR #227 (if re-validation passes) → PM merges PR #228 →
address shallow-fetch warning in follow-up chore PR or PR #228 before merge.
