# GitHub Actions Test Improvement Plan

**Date:** 2026-04-22  
**Purpose:** make GitHub Actions the authoritative merge gate for `black`, `ruff`, lint/validation, and `pytest`, while keeping `elis-server` as the supported local preflight environment for fast feedback and environment parity.  
**Validation owner:** Claude Code

---

## 1) Objective

Establish GitHub Actions as the single authoritative merge-gate execution surface for:

- formatting checks (`black --check`)
- linting (`ruff check`)
- blocking validation/lint-style gates
- `pytest`

Agent identities may still create commits, comments, `HANDOFF.md`, and `REVIEW_PE<N>.md`, but they must no longer be the authoritative source of pass/fail evidence for code-quality gates.

At the same time, `elis-server` should remain the preferred local preflight surface for contributors and agents who need rapid feedback before pushing.

---

## 2) Current State

The repository already runs core checks in [ci.yml](/c:/Users/carlo/ELIS-SLR-Agent/.github/workflows/ci.yml):

- `quality` runs `ruff` and `black`
- `tests` runs `pytest -q`
- `validate` runs manifest/schema validation
- additional CI checks run `review-evidence-check`, `current-pe-check`, `secrets-scope-check`, and SLR-specific validation

However, the workflow surface is still mixed:

- agent-runner workflows still install tooling and run checks locally in agent-owned jobs
- validator and implementer flows still treat local command output as first-class gate evidence
- bot tokens remain entangled with workflows that are partly about review/orchestration and partly about validation
- the repo process still invites duplicate execution of the same checks across CI and agent sessions
- the current plan does not yet distinguish clearly between:
  - portable, open-source-friendly checks that should always run in GitHub Actions
  - environment-specific checks that may still need `elis-server`

---

## 3) Target State

After this improvement:

1. GitHub Actions is the only blocking authority for portable code-quality and test gates:
   - `black`
   - `ruff`
   - lint/validation
   - `pytest`
2. Branch protection requires GitHub Actions checks, not agent-local command output.
3. `elis-server` is the supported local preflight environment for contributors and agents before push.
4. Agent workflows may run advisory smoke checks locally, but these do not decide merge eligibility.
5. Bot tokens are used only for repository mutations:
   - comments
   - labels
   - PR transitions
   - branch updates
   - formal review actions where structurally required
6. Validator review focuses on acceptance criteria, behavioural regressions, and audit evidence, while CI owns deterministic code execution.
7. Environment-specific checks are classified explicitly and are not silently mixed into the open-source PR gate unless they are reproducible in CI.

---

## 4) Proposed Changes

### 4.1 Make `ci.yml` the canonical blocking gate

Keep all blocking code-quality and test execution in [ci.yml](/c:/Users/carlo/ELIS-SLR-Agent/.github/workflows/ci.yml), with these jobs as the required merge surface:

- `quality`
- `tests`
- `validate`
- `current-pe-check`
- `secrets-scope-check`
- `review-evidence-check`
- `slr-quality-check`
- any other genuinely blocking repository checks already enforced there

Rule:

- if a check is blocking for merge, it must be runnable in GitHub Actions without an agent token

### 4.1a Distinguish portable checks from environment-specific checks

Define two test classes.

**Portable blocking checks**

- formatting
- linting
- schema/manifest validation
- unit and integration `pytest` that can run on standard GitHub-hosted runners

These belong in GitHub Actions and should be open-source reproducible.

**Environment-specific checks**

- host/runtime probes
- checks that depend on `elis-server` configuration
- checks that require local services, private infrastructure, or non-portable host assumptions

These may still run on `elis-server`, but they should be labelled explicitly and kept separate from the standard OSS merge gate unless they can be made reproducible in CI.

### 4.2 Separate CI from orchestration

Classify workflows into two groups.

**CI workflows**

- execute code checks
- require only read/minimal repository permissions
- use `actions/checkout` and standard Python setup
- do not depend on `CODEX_BOT_TOKEN`, `CLAUDE_BOT_TOKEN`, or similar agent secrets

**Orchestration workflows**

- dispatch agents
- post comments
- apply labels
- request review / record verdicts
- push commits where required

Rule:

- orchestration may use bot/App credentials
- code validation must not

### 4.3 Keep local runs on `elis-server`, but downgrade them to advisory status

Update the process so that agent-local runs of `black`, `ruff`, and `pytest` on `elis-server` are optional smoke checks rather than merge gates.

Expected wording change:

- local runs on `elis-server` help contributors and agents catch issues early
- only GitHub Actions results count as blocking gate evidence

### 4.3a Standardise command parity between local and CI

Document one canonical command set for both local and CI use wherever possible:

- `python -m black --check .`
- `python -m ruff check .`
- `python -m pytest -q`

If CI needs narrower or broader variants, document the reason explicitly so local and remote behaviour do not drift.

### 4.4 Update repository-facing workflow documents

Revise:

- [AGENTS.md](/c:/Users/carlo/ELIS-SLR-Agent/AGENTS.md)
- handoff expectations
- review expectations

to say that for code-quality gates the authoritative evidence is:

- GitHub Actions check name
- GitHub Actions run URL or PR check result

rather than only pasted local terminal output.

### 4.5 Reduce token use in non-mutating workflows

Review workflows such as:

- [implementer-runner.yml](/c:/Users/carlo/ELIS-SLR-Agent/.github/workflows/implementer-runner.yml)
- [validator-runner.yml](/c:/Users/carlo/ELIS-SLR-Agent/.github/workflows/validator-runner.yml)
- [auto-assign-validator.yml](/c:/Users/carlo/ELIS-SLR-Agent/.github/workflows/auto-assign-validator.yml)

and remove agent-token dependency from any step that is purely checking code or validating artefacts.

Bot/App credentials should remain only where the workflow must:

- push commits
- open/edit PRs
- post formal reviews or comments
- manage labels or PM routing

### 4.6 Align branch protection with the new rule

Configure the protected branch so merge depends on required GitHub Actions checks rather than on agent-local execution history.

This means:

- CI status checks become the formal pass/fail gate
- agent comments remain informative, not the code-execution authority

### 4.7 Preserve `elis-server` as the local developer reference environment

Document `elis-server` as:

- the preferred preflight environment for maintainers and agents
- the place to run host-specific checks that are not part of the OSS blocking gate
- a parity environment, not the sole authority for merge

This keeps the project practical for local operations without making mergeability depend on a private machine.

---

## 5) Implementation Sequence

### Phase A — Document the policy

1. Update `AGENTS.md` to define GitHub Actions as the authoritative execution surface for portable blocking gates.
2. Update `HANDOFF.md` expectations so code-quality gate sections may cite CI job results directly.
3. Update `REVIEW_PE<N>.md` guidance so validators distinguish:
   - CI-owned checks
   - validator-owned behavioural validation
4. Add explicit wording that `elis-server` is the supported local preflight environment, but not the merge authority.

### Phase B — Simplify workflow responsibilities

1. Audit `.github/workflows/` and classify each workflow as CI or orchestration.
2. Remove duplicated quality/test steps from orchestration workflows where they are not structurally needed.
3. Keep or add minimal smoke checks on `elis-server` only when they reduce wasted CI cycles, but mark them advisory.
4. Classify environment-specific checks separately from portable CI checks.

### Phase C — Harden CI as the single gate

1. Ensure `ci.yml` contains every blocking portable formatting/lint/testing job.
2. Ensure those jobs run without bot tokens.
3. Confirm required-check names are stable so branch protection can rely on them.
4. Confirm any host-specific `elis-server` checks are either:
   - non-blocking, or
   - moved to a reproducible runner strategy before being made blocking

### Phase D — Branch protection and close-out

1. Update required checks on `main`.
2. Validate that a PR with green CI but no local pasted agent output still satisfies the repository’s merge conditions.
3. Validate that a PR with local agent claims but failing CI is blocked.
4. Validate that local preflight on `elis-server` still remains documented and usable.

---

## 6) Validation Tasks For Claude Code

Claude Code should validate this plan by checking the following points in the repo:

### V-1 Workflow inventory

Confirm which workflows currently execute:

- `black`
- `ruff`
- `pytest`
- schema/manifest validation

and identify any duplication between CI and orchestration workflows.

Also classify which of those checks are portable and which are environment-specific.

### V-2 Token dependency audit

Confirm which workflows use:

- `CODEX_BOT_TOKEN`
- `CLAUDE_BOT_TOKEN`
- `PM_BOT_TOKEN`
- GitHub App tokens

and verify whether any of those token-dependent steps are performing code validation that should instead live in CI.

### V-3 Branch-protection readiness

Confirm that the existing `ci.yml` check names are suitable to become or remain required checks for merge.

Confirm separately whether any current host-specific checks should remain advisory rather than required.

### V-4 Process alignment

Check whether `AGENTS.md`, `HANDOFF.md`, and review practices currently require local pasted outputs in places where CI evidence should become canonical.

Also check whether local `elis-server` preflight is still documented clearly enough for maintainers.

### V-5 Risk review

Identify any workflow that would break if validation moved entirely to GitHub Actions, especially:

- validator-runner assumptions
- auto-merge assumptions
- review-evidence parsing
- PM arbitration / escalation flows
- any host-specific checks that cannot run on GitHub-hosted runners

---

## 7) Acceptance Criteria

This improvement plan is considered complete when Claude Code can confirm all of the following:

1. Every portable blocking code-quality/test gate is run in GitHub Actions.
2. No agent token is required to execute `black`, `ruff`, lint/validation, or `pytest` in the blocking CI path.
3. Agent-token workflows are limited to orchestration or repository mutation tasks.
4. Repository guidance clearly states that CI is the authoritative pass/fail source for portable code execution gates.
5. `elis-server` remains documented as the supported local preflight environment.
6. Branch protection can rely on GitHub Actions statuses alone for portable blocking gates.

---

## 8) Risks And Mitigations

### Risk 1 — Mixed authority remains

If local agent output and CI output are both treated as authoritative, confusion will persist.

Mitigation:

- define one authority only: GitHub Actions

for portable blocking checks

### Risk 2 — Orchestration workflows silently depend on local checks

Some runner workflows may assume local `black`/`ruff`/`pytest` results exist before they continue.

Mitigation:

- audit runner workflows and replace those assumptions with PR check inspection or CI-required status

### Risk 2a — `elis-server` parity is lost

If the plan over-corrects towards CI-only wording, maintainers may stop using `elis-server` for fast feedback and host-specific checks.

Mitigation:

- document `elis-server` as the preferred local preflight surface
- keep local command parity with CI where possible

### Risk 3 — Review files drift from CI truth

Agents may continue pasting stale local counts or incomplete command history.

Mitigation:

- change review guidance to cite CI runs for code-quality gates
- reserve local evidence for acceptance-criterion spot checks and behavioural validation

### Risk 4 — Branch protection names drift

If required check names change frequently, the governance model becomes brittle.

Mitigation:

- stabilise CI job names before making them the sole required checks

### Risk 5 — Host-specific checks are forced into the OSS merge gate

If non-portable runtime checks are made required without a reproducible CI runner path, contributors will be blocked by infrastructure they do not control.

Mitigation:

- classify such checks explicitly as environment-specific
- keep them advisory or move them to a reproducible CI surface before making them blocking

---

## 9) Recommended Next Step

Open a dedicated PE or chore branch that performs two concrete actions first:

1. update `AGENTS.md` so CI is the canonical authority for portable code-quality/test gates while `elis-server` remains the local preflight environment
2. refactor workflow responsibilities so `.github/workflows/ci.yml` is the only blocking execution surface for `black`, `ruff`, lint/validation, and `pytest`

That gives Claude Code a narrow, testable validation target before any broader workflow clean-up.

---

## 10) Validation Findings (Claude Code · 2026-04-22)

Claude Code validated §6 (V-1 through V-5) against the current repository state before PE-GHA-01 was opened. Findings are recorded here for CODEX to read at Step 0.

### V-1 — Workflow inventory

Workflows that execute `black` / `ruff` / `pytest`:

| Workflow | black | ruff | pytest | Classification |
|----------|-------|------|--------|----------------|
| `ci.yml` | ✓ check | ✓ check | ✓ `-q` | **Pure CI — no bot token** |
| `deep-review.yml` | ✓ check | ✓ check | ✓ `-q` | CI-style but not a required check |
| `autoformat.yml` | ✓ check + fix | ✓ check + fix | — | Mixed: pre-mutation checks then pushes via GitHub App token |
| `implementer-runner.yml` | installs only | installs only | — | Orchestration — installs tooling for agent session, no gate steps |
| `validator-runner.yml` | installs only | installs only | — | Orchestration — same |
| `pm-plan-load.yml` | installs only | installs only | — | Orchestration |

`ci.yml` is already the only workflow that runs these as pure, token-free blocking steps. The runner workflows install the tooling so agents invoke it locally — those local runs produce the pasted outputs in HANDOFF/REVIEW files, which is the structural gap this plan targets.

Duplication: `deep-review.yml` re-runs `black`, `ruff`, and `pytest` independently of `ci.yml` but is not a required check.

All checks in `ci.yml` run on `ubuntu-latest` with standard `actions/checkout` + `setup-python` — fully portable. No checks depend on `elis-server` configuration.

### V-2 — Token dependency audit

| Workflow | Tokens used | Code-validation steps behind token? |
|----------|-------------|--------------------------------------|
| `implementer-runner.yml` | `CODEX_BOT_TOKEN`, `CLAUDE_BOT_TOKEN`, `OPENAI_API_KEY`, `CLAUDE_CREDENTIALS_JSON` | No — tokens gate agent dispatch and repo mutation only |
| `validator-runner.yml` | same + `PM_BOT_TOKEN` | No — same pattern |
| `autoformat.yml` | `ELIS_APP_ID`, `ELIS_APP_PRIVATE_KEY` | Marginal — ruff/black run before the App-token push as pre-mutation checks, not independent blocking gates |
| `ci.yml` | None (`github.token` read-only for PR writes) | N/A |

No bot-token workflow runs `black`/`ruff`/`pytest` as a blocking merge gate. The actual problem is that agents invoke these tools locally in their sessions and paste the output as authoritative evidence, which `AGENTS.md` §2.4 and §6.4 currently require.

### V-3 — Branch-protection readiness

Current required status checks on `main` (verified via API):

| Check name | In `ci.yml`? | Currently required for merge? |
|-----------|-------------|-------------------------------|
| `quality` | ✓ | ✓ |
| `tests` | ✓ | ✓ |
| `validate` | ✓ | ✓ |
| `current-pe-check` | ✓ | ✗ |
| `secrets-scope-check` | ✓ | ✗ |
| `review-evidence-check` | ✓ | ✗ |
| `slr-quality-check` | ✓ | ✗ |

Four blocking-eligible `ci.yml` jobs are not yet required for merge. Phase D of this plan must add them to branch protection.

`auto-merge-on-pass.yml` Step 8 already checks `mergeable_state == 'clean'`, so expanding branch protection automatically tightens the auto-merge gate with no workflow changes needed.

All CI job names are stable string literals — safe to make required.

### V-4 — Process alignment

`AGENTS.md` gaps (lines confirmed by `grep`):

- §2.4 Evidence-first reporting: *"If a claim is not supported by pasted command output, it is not considered done."* — no CI alternative permitted
- §6.4 Quality gates: mandates pasting `black --check .`, `ruff check .`, `pytest -q` local terminal output in every Status Packet and REVIEW file
- No mention of GitHub Actions as authoritative execution surface
- No mention of CI run URLs as valid gate evidence
- No mention of `elis-server` as a local preflight environment

`check_review.py` (used by `review-evidence-check` CI job and `auto-merge-on-pass.yml`) requires a fenced code block in the `### Evidence` section but does not validate what is inside it — citing a CI run URL inside a code block already satisfies the parser. No script change is needed for Phase A.

**Phase A deliverable for CODEX:** update `AGENTS.md` §2.4 and §6.4 to (a) permit GitHub Actions check results as primary gate evidence for portable checks, and (b) add explicit language that `elis-server` is the supported local preflight environment and that local runs are advisory for portable gates.

### V-5 — Risk review

| Risk | Severity | Finding |
|------|----------|---------|
| `check_review.py` breaks if evidence format changes | Low | Accepts any fenced code block — no script change needed for Phase A |
| `auto-merge-on-pass.yml` breaks if required checks expand | None | `mergeable_state == 'clean'` already respects any new required checks |
| Validator/implementer runner prompts still instruct agents to paste local output | Medium | Prompts derive from `AGENTS.md`; once `AGENTS.md` is updated this propagates automatically |
| `deep-review.yml` duplicates `ci.yml` checks | Low | Not a required check — harmless; classify as advisory in Phase B |
| `elis-server` parity loss | Low | Additive documentation gap only — no breakage risk |
| `openclaw-config-sync-check` is non-portable | Low | Already annotated `non-blocking — Docker unavailable in CI`; no action needed for Phase A |

### Acceptance criteria pre-check

| AC | Criterion | Pre-check status |
|----|-----------|-----------------|
| AC-1 | Every portable blocking gate runs in GitHub Actions | ✓ Already true |
| AC-2 | No agent token required for blocking CI path | ✓ Already true |
| AC-3 | Agent-token workflows limited to orchestration/mutation | ✓ Already true at workflow level |
| AC-4 | Repository guidance states CI is authoritative | ✗ Gap — `AGENTS.md` §2.4 and §6.4 require local pasted output only |
| AC-5 | `elis-server` documented as local preflight environment | ✗ Gap — not mentioned in `AGENTS.md` |
| AC-6 | Branch protection relies on GitHub Actions alone | ⚠️ Partial — 3 of 7 ci.yml blocking jobs are required; 4 are not |

**AC-4 and AC-5 are the sole deliverables for Phase A (PE-GHA-01).** AC-6 is Phase D scope.
