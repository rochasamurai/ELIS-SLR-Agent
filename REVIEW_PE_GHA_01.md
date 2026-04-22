# REVIEW — PE-GHA-01 · GitHub Actions CI Authority and `elis-server` Preflight Documentation

**Validator:** `gha-val-b` (Claude Code)
**Reviewed at:** 2026-04-22
**PR:** #364

---

### Verdict

PASS

---

### Gate results

```
gh pr checks 364
→ quality                pass
  tests                  pass
  validate               pass
  current-pe-check       pass
  secrets-scope-check    pass
  review-evidence-check  pass
  slr-quality-check      pass
  openclaw-health-check  pass
  openclaw-doctor-check  pass
  openclaw-security-check pass
  add_and_set_status     pass
  deep-review            skipping

python -m black --check . (local preflight)
→ All checks passed!

python -m ruff check . (local preflight)
→ All checks passed!

python -m pytest -q --basetemp=.tmp/gha01-pytest-clean --cache-clear (local preflight)
→ 2 failed, remainder passed
  FAILED tests/test_verify_claude_auth.py::test_fails_when_credentials_file_missing
  FAILED tests/test_verify_claude_auth.py::test_fails_when_credentials_file_lacks_oauth_key
  (2 pre-existing failures unrelated to PE-GHA-01; CI tests: pass)
```

---

### Scope

```
git diff --name-status origin/main..HEAD

M  AGENTS.md
M  HANDOFF.md
A  REVIEW_PE_GHA_01.md
A  docs/decisions/ADR-011-github-actions-authority-for-portable-gates.md
M  docs/decisions/README.md
```

5 files. Scope matches HANDOFF.md. No unrelated changes.

---

### Required fixes

None.

---

### Evidence

**AC-4 — Repository guidance states CI is authoritative for portable blocking gates**

`AGENTS.md` §2.4 now reads:

```text
For portable blocking gates (`black`, `ruff`, lint/validation, and `pytest`), the
authoritative pass/fail source is GitHub Actions CI. Local runs on `elis-server`
are supported as preflight checks for fast feedback, but they do not override CI.
```

The same policy is stated consistently in §5.1 (implementer quality gates), §5.2
(validator quality gates), §6 (Status Packet header), §6.4 (quality gate commands),
and §12.1 (structural controls). All six locations updated — no orphaned contradictory
language remains.

**AC-5 — `elis-server` documented as supported local preflight environment**

`AGENTS.md` §6.4 now reads:

```text
Local runs on `elis-server` are the preferred preflight environment for maintainers
and agents, but they are advisory for merge authority.
```

Named explicitly in §2.4, §5.1, §5.2, §6, §6.4, and §12.1. The role is
formalised — not removed.

**ADR-011 present and indexed**

```text
docs/decisions/ADR-011-github-actions-authority-for-portable-gates.md
→ Status: Accepted · Date: 2026-04-22

docs/decisions/README.md
→ | ADR-011 | GitHub Actions authority for portable gates | Accepted | 2026-04-22 |
```

**pytest pre-existing failures**

The 2 failures in `test_verify_claude_auth.py` are pre-existing and unrelated
to PE-GHA-01. The PE changes are pure documentation and cannot affect test
execution. CI `tests` is green. Not a blocking finding.

---

**Re-validation round 2 — 2026-04-22**

HANDOFF updated at `97404a1` with refreshed pytest evidence (`--cache-clear`
cleared the prior PermissionError). Scope and AC status unchanged. PASS
verdict confirmed.
