# HANDOFF.md — PE-INFRA-05

## Summary
- Implemented `scripts/check_review.py` to enforce REVIEW structure/evidence requirements.
- Added `tests/test_check_review.py` with adversarial coverage (9 tests).
- Added Gate 2b in `.github/workflows/auto-merge-on-pass.yml` to block PASS verdicts without evidence.
- Added `review-evidence-check` job in `.github/workflows/ci.yml` for changed `REVIEW_*.md` files.
- Updated review template and workflow rules (`AGENTS.md` §2.4.1).

## Files Changed
- `scripts/check_review.py` (new)
- `tests/test_check_review.py` (new)
- `.github/workflows/auto-merge-on-pass.yml` (modified)
- `.github/workflows/ci.yml` (modified)
- `reports/agent_activity/templates/REVIEW_REQUEST_TEMPLATE.md` (modified)
- `AGENTS.md` (modified)
- `HANDOFF.md` (this file)

## Design Decisions
- File discovery mirrors `scripts/parse_verdict.py` (`REVIEW_FILE` first, fallback to latest by `REVIEW_PATH`).
- Section parsing validates the latest appended validation section in iterative review files.
- FAIL verdict requires non-empty actionable `### Required fixes` (rejects empty/`None`).
- Gate 2b runs only for PASS verdicts to preserve FAIL/IN_PROGRESS behavior.
- CI review-evidence job skips cleanly when no `REVIEW_*.md` file is changed.

## Acceptance Criteria
- [x] AC-1 `scripts/check_review.py` created with required failure/pass behavior.
- [x] AC-2 Gate 2b added to `.github/workflows/auto-merge-on-pass.yml`.
- [x] AC-3 `review-evidence-check` job added to `.github/workflows/ci.yml`.
- [x] AC-4 `reports/agent_activity/templates/REVIEW_REQUEST_TEMPLATE.md` updated with mandatory `### Evidence`.
- [x] AC-5 `AGENTS.md` updated with §2.4.1 hard evidence rule.

## Validation Commands
```text
python -m black --check scripts/check_review.py tests/test_check_review.py
All done! ✨ 🍰 ✨
2 files would be left unchanged.
```

```text
python -m ruff check scripts/check_review.py tests/test_check_review.py
All checks passed!
```

```text
python -m pytest tests/test_check_review.py -v
============================= test session starts =============================
platform win32 -- Python 3.14.0, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Users\carlo\ELIS-SLR-Agent
configfile: pyproject.toml
collected 9 items

tests\test_check_review.py .........                                     [100%]

============================== 9 passed in 0.30s ==============================
```

```text
python -m pytest -q
........................................................................ [ 15%]
........................................................................ [ 31%]
........................................................................ [ 47%]
........................................................................ [ 63%]
........................................................................ [ 79%]
........................................................................ [ 95%]
......................                                                   [100%]
============================== warnings summary ===============================
... (existing known deprecation warnings in screen/search modules)
```

```text
# Valid review file
REVIEW evidence check PASS (review_valid_peinfra05.md)
Exit: 0
```

```text
# Invalid review file (Evidence section has no fenced block)
ERROR: Evidence section must include at least one fenced code block.
Exit: 1
```

## Status Packet

### 6.1 Working-tree state
```text
git status -sb
## chore/pe-infra-05-review-evidence...origin/main
 M .github/workflows/auto-merge-on-pass.yml
 M .github/workflows/ci.yml
 M AGENTS.md
 M reports/agent_activity/templates/REVIEW_REQUEST_TEMPLATE.md
?? scripts/check_review.py
?? tests/test_check_review.py
```

### 6.2 Repository state
```text
git fetch --all --prune
(no output)

git branch --show-current
chore/pe-infra-05-review-evidence
```

### 6.3 Scope evidence
```text
git diff --name-status
M	.github/workflows/auto-merge-on-pass.yml
M	.github/workflows/ci.yml
M	AGENTS.md
M	reports/agent_activity/templates/REVIEW_REQUEST_TEMPLATE.md
```

### 6.4 Quality gates
```text
black: PASS
ruff: PASS
pytest (PE-specific): 9 passed
pytest (full): 454 passed
```

### 6.5 PR evidence
```text
PR not opened yet at handoff update time.
```

## Hotfix Addendum — 2026-02-20 (post-validator follow-up)

Scope: non-blocking follow-up requested by Validator on PR #259.

- File changed: `.github/workflows/auto-merge-on-pass.yml` only.
- Change:
  - from `base="release/2.0"`
  - to dynamic base resolution:
    `base=$(gh pr list --head "$GITHUB_REF_NAME" --json baseRefName -q '.[0].baseRefName' 2>/dev/null || echo "main")`

Reason:
- Avoid hardcoded deleted branch (`release/2.0`) and align REVIEW-file diffing with the active PR base branch.

Validation rerun:
- `python -m black --check .` -> PASS
- `python -m ruff check .` -> PASS
- `python -m pytest -q` -> 454 passed, 17 warnings (pre-existing deprecation warnings)

## Hotfix Addendum — 2026-02-20 (re-validation round 2)

Scope: blocking Validator finding F1 on PR #259.

- File changed: `.github/workflows/ci.yml` only.
- Change:
  - from `git fetch origin "$base" --depth=1`
  - to `git fetch origin "$base"`

Reason:
- Three-dot diff (`origin/$base...HEAD`) requires merge-base; shallow base fetch caused `no merge base` (exit 128).

Validation rerun:
- `python -m black --check .` -> PASS
- `python -m ruff check .` -> PASS
- `python -m pytest -q` -> 454 passed, 17 warnings
