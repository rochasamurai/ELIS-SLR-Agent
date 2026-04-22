# REVIEW — PE-GHA-02 · Workflow Classification and Branch Protection Hardening

**Validator:** `gha-val-a` (CODEX @ `elis-server`)
**Reviewed at:** 2026-04-22
**PR:** #367

---

### Verdict

FAIL

---

### Gate results

```text
gh pr checks 367
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
  deep-review            skipping

gh api repos/rochasamurai/ELIS-Multi-AI-Agent-Platform/branches/main
→ protection.required_status_checks.contexts:
  quality
  tests
  validate
```

---

### Scope

```text
git diff --name-status origin/main..HEAD

M  .github/workflows/auto-merge-on-pass.yml
M  .github/workflows/autoformat.yml
M  .github/workflows/ci.yml
M  .github/workflows/deep-review.yml
M  .github/workflows/implementer-runner.yml
M  .github/workflows/validator-runner.yml
A  HANDOFF.md
A  REVIEW_PE_GHA_02.md
A  docs/_active/PE_GHA_02_PHASE_C_PM_ACTION.md
A  docs/decisions/ADR-012-workflow-classification.md
M  docs/decisions/README.md
```

Scope is PE-GHA-02-related, but the implementation does not yet satisfy all Phase B/C/D acceptance criteria.

---

### Required fixes

- Implement AC-6 fully, not as a PM follow-up doc only. The repository state must show the hardened required checks on `main`, or the PE scope must be explicitly re-scoped by PM before PASS is possible.
- Align ADR-012 and the workflow files. Either add `# Classification:` headers to the remaining workflow files covered by the ADR, or narrow the ADR/hand-off claims so they match the implementation actually delivered.

---

### Evidence

**Finding 1 — AC-6 remains incomplete, and the branch itself admits that**

The handoff marks AC-6 as `PARTIAL` rather than `PASS`:

```text
HANDOFF.md
47: | AC-1 | Every portable blocking gate runs in GitHub Actions | PASS (pre-existing; confirmed) |
48: | AC-2 | No agent token required for blocking CI path | PASS (pre-existing; confirmed) |
49: | AC-3 | Agent-token workflows limited to orchestration/mutation | PASS — classification headers make the boundary explicit |
50: | AC-4 | Repository guidance states CI is authoritative | PASS (PE-GHA-01) |
51: | AC-5 | `elis-server` documented as local preflight environment | PASS (PE-GHA-01) |
52: | AC-6 | Branch protection relies on GitHub Actions alone | PARTIAL — 3 of 7 portable-gate jobs required; Phase C PM action documents the 4 remaining additions |
```

The Phase C document also states the four checks are still missing from branch protection:

```text
docs/_active/PE_GHA_02_PHASE_C_PM_ACTION.md
15: | `quality` | ✓ |
16: | `tests` | ✓ |
17: | `validate` | ✓ |
18: | `current-pe-check` | ✗ |
19: | `secrets-scope-check` | ✗ |
20: | `review-evidence-check` | ✗ |
21: | `slr-quality-check` | ✗ |
25: Add the four missing checks to branch protection using the GitHub UI or CLI.
```

Live branch metadata from GitHub matches that document. `main` still requires only three checks:

```text
gh api repos/rochasamurai/ELIS-Multi-AI-Agent-Platform/branches/main

"protected": true,
"required_status_checks": {
  "contexts": [
    "quality",
    "tests",
    "validate"
  ]
}
```

That means Phase C is documented but not implemented, so AC-6 is not yet satisfied.

**Finding 2 — ADR-012 overstates the delivered workflow classification coverage**

ADR-012 claims a repo-wide implementation:

```text
docs/decisions/ADR-012-workflow-classification.md
19: Every workflow file is classified as one of three types:
64: Each workflow file in the categories above carries a `# Classification:` comment
65: on its first line for machine-readability and human clarity.
```

But many workflow files still have no `# Classification:` first line, for example:

```text
.github/workflows/agent-run.yml
1: name: ELIS - Agent Run

.github/workflows/auto-assign-validator.yml
1: name: Auto-assign Validator

.github/workflows/pm-arbiter.yml
1: name: PM Arbiter
```

The PR only adds classification headers to six workflow files, so the ADR and handoff currently claim broader implementation than the branch actually contains.

**Non-blocking note — CI on the PR is green**

```text
gh pr checks 367
→ quality                pass
  tests                  pass
  validate               pass
  current-pe-check       pass
  secrets-scope-check    pass
  review-evidence-check  pass
  slr-quality-check      pass
```

That confirms the PR branch itself is healthy, but it does not change the fact that `main` branch protection has not yet been hardened and the new ADR currently overclaims the delivered classification coverage.

---

**Re-validation round 2 — 2026-04-22**

### Verdict

PASS

### Gate results

```text
gh pr checks 367
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
  deep-review            skipping

gh api repos/rochasamurai/ELIS-Multi-AI-Agent-Platform/branches/main
→ protection.required_status_checks.contexts:
  quality
  tests
  validate
  current-pe-check
  secrets-scope-check
  review-evidence-check
  slr-quality-check
```

### Scope

```text
git diff --name-status origin/main..HEAD

M  .github/workflows/agent-automerge.yml
M  .github/workflows/agent-run.yml
M  .github/workflows/agents-compliance.yml
M  .github/workflows/auto-assign-validator.yml
M  .github/workflows/auto-merge-on-pass.yml
M  .github/workflows/autoformat.yml
M  .github/workflows/benchmark_2_phase1.yml
M  .github/workflows/benchmark_validation.yml
M  .github/workflows/bot-auth-verify.yml
M  .github/workflows/bot-commit.yml
M  .github/workflows/check-parallel-governance-pr.yml
M  .github/workflows/ci-current-pe.yml
M  .github/workflows/ci.yml
M  .github/workflows/deep-review.yml
M  .github/workflows/elis-agent-nightly.yml
M  .github/workflows/elis-agent-screen.yml
M  .github/workflows/elis-agent-search.yml
M  .github/workflows/elis-housekeeping.yml
M  .github/workflows/elis-imports-convert.yml
M  .github/workflows/elis-search-preflight.yml
M  .github/workflows/elis-validate.yml
M  .github/workflows/export-docx.yml
M  .github/workflows/implementer-runner.yml
M  .github/workflows/notify-pm-agent.yml
M  .github/workflows/pe-sequencer.yml
M  .github/workflows/pm-arbiter.yml
M  .github/workflows/pm-chore-approve.yml
M  .github/workflows/pm-discord-command.yml
M  .github/workflows/pm-observability-dashboard.yml
M  .github/workflows/pm-plan-load.yml
M  .github/workflows/projects-autoadd.yml
M  .github/workflows/projects-runid.yml
M  .github/workflows/test_database_harvest.yml
M  .github/workflows/validator-dispatch.yml
M  .github/workflows/validator-runner.yml
A  docs/_active/PE_GHA_02_PHASE_C_PM_ACTION.md
A  docs/decisions/ADR-012-workflow-classification.md
M  docs/decisions/README.md
M  HANDOFF.md
M  REVIEW_PE_GHA_02.md
```

39 implementation files plus this review update. Scope remains within PE-GHA-02.

### Required fixes

None.

### Evidence

**AC-3 — workflow classification coverage now matches ADR-012**

The workflow scan now finds no unclassified workflow files:

```text
Get-ChildItem .github/workflows -Filter *.yml |
  ForEach-Object {
    $first = (Get-Content $_.FullName -TotalCount 1)
    if ($first -notmatch '^# Classification:') { $_.Name }
  }

→ no output
```

`HANDOFF.md` now also reflects the repo-wide coverage:

```text
HANDOFF.md
15: - **Phase B** — every workflow file in `.github/workflows/` now carries a
16:   `# Classification:` header (CI / CI Advisory / Mixed / Orchestration) making
17:   the CI-vs-orchestration boundary self-documenting. All 35 workflow files
18:   classified. ADR-012 records the rule.
```

**AC-6 — branch protection now relies on GitHub Actions alone**

Live GitHub branch metadata now shows all seven portable-gate checks required on `main`:

```text
gh api repos/rochasamurai/ELIS-Multi-AI-Agent-Platform/branches/main

"required_status_checks": {
  "contexts": [
    "quality",
    "tests",
    "validate",
    "current-pe-check",
    "secrets-scope-check",
    "review-evidence-check",
    "slr-quality-check"
  ]
}
```

That resolves the prior AC-6 blocker.

**Phase D — hardened gate remains green on the PR**

```text
gh pr checks 367
→ quality                pass
  tests                  pass
  validate               pass
  current-pe-check       pass
  secrets-scope-check    pass
  review-evidence-check  pass
  slr-quality-check      pass
```

**Residual note**

`docs/_active/PE_GHA_02_PHASE_C_PM_ACTION.md` still describes the earlier pre-hardening state, but the live branch protection and the acceptance criteria are now satisfied. That document is stale historical guidance rather than a remaining blocker for PE-GHA-02.
