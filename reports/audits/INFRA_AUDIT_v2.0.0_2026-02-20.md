# ELIS SLR Agent — Infrastructure & Two-Agent Model Audit Report

**Date:** 2026-02-20
**Scope:** All infrastructure improvements delivered for the v2.0 release line
**Release:** v2.0.0 (tag `v2.0.0`, signed, Verified — main at audit time: `781ab53`)

---

## 1. Executive Summary

The two-agent development model (CODEX as Implementer, Claude Code as Validator) was fully
operationalized across the v2.0 release cycle. Seven product PEs (PE0a–PE6) were implemented
and validated. Four dedicated infrastructure PEs (INFRA-02 through INFRA-04 plus a compliance
automation chore) hardened the workflow from an informal checklist into an enforced, CI-gated
protocol. Five functional test rounds produced the final GO verdict for v2.0.0 on 2026-02-19.

**All PEs: PASS. Release: v2.0.0 shipped.**

---

## 2. Two-Agent Model — Protocol Evolution

### 2.1 Baseline (before v2.0 infra work)

The workflow existed as a document (`AGENTS.md`) but had no enforcement. Agents self-reported
compliance. Role assignment was ad hoc. No CI gate verified scope, handoff quality, or verdict
delivery. Context switches were handled manually with no protection against branch contamination.

### 2.2 Mechanisms delivered during v2.0

| Mechanism | PE / PR | What it enforces |
|-----------|---------|-----------------|
| AGENTS.md hard rules + PR template | #227 | Scope discipline, evidence-first reporting, clean-tree rule, rebase protocol |
| PR-comment handshake model | #234 | Validator posts verdict as PR comment before writing review file; PM authorizes merge only after comment |
| CLAUDE.md §5.2 verdict delivery rule | #249 | Verdict comment is a hard requirement, not advisory — blocks PM merge if absent |
| Role registration (PE-INFRA-02) | #242 | Agents self-register in `CURRENT_PE.md` on session start; scripts verify registration before handoff |
| CURRENT_PE.md as SSoT (PE-INFRA-03) | #245 | All release context (branch, plan file, roles) resolved from a single file; no hardcoded branch names |
| Autonomous gates + secrets isolation (PE-INFRA-04) | #255 | GitHub Actions auto-assigns Validator on PR open; auto-merges after PASS verdict; secrets never logged |
| AGENTS compliance CI gate | #228 | Every PR to `release/2.0` runs `agents_compliance_check.py` — branch naming, HANDOFF.md presence, cross-PE file contamination |

---

## 3. Infrastructure PE Delivery Record

### PE-INFRA-02 — Role Registration Mechanism (PR #242)

**Implementer:** CODEX | **Validator:** Claude Code
**Verdict:** PASS (first round)
**Scope:** `AGENTS.md`, `CLAUDE.md`, `CODEX.md`, `scripts/check_role_registration.py`, `CURRENT_PE.md`

Role registration was added as a mandatory Step 0: each agent writes a dated self-registration
entry into `CURRENT_PE.md` at the start of every PE. The script `check_role_registration.py`
verifies entries before handoff is accepted. This closed the gap where an agent could begin work
on the wrong PE without detection.

---

### PE-INFRA-03 — Release-Plan Agnostic Workflow (PR #245)

**Implementer:** CODEX | **Validator:** Claude Code
**Verdict:** PASS (first round)
**Scope:** `CURRENT_PE.md` structure, `AGENTS.md` §1 canonical references, all agent instructions

Eliminated all hardcoded references to `release/2.0` and `RELEASE_PLAN_v2.0.md` in agent
instructions. Every agent now resolves the active branch and plan file exclusively from
`CURRENT_PE.md`. Switching to a new release line requires editing exactly one file. Added the
rule: if any field in `CURRENT_PE.md` is blank, agents stop and notify PM.

---

### PE-INFRA-04 — Autonomous Agent Gates + Secrets Isolation (PR #255)

**Implementer:** CODEX | **Validator:** Claude Code
**Verdict:** FAIL → FAIL → PASS (3 rounds)
**Scope:** `.github/workflows/auto-assign-validator.yml`,
`.github/workflows/auto-merge-on-pass.yml`, `.github/workflows/ci.yml`,
`scripts/parse_verdict.py`, `scripts/check_agent_scope.py`, `scripts/check_handoff.py`,
`scripts/check_status_packet.py`, `.agentignore`, `.env.example`

This was the most complex infrastructure PE and required two re-validation cycles:

| Round | Finding | Status |
|-------|---------|--------|
| r1 | B-1: auto-merge did not gate on CI-green before merge | Fixed |
| r1 | B-2: `parse_verdict.py` selected wrong review file (mtime, not active PE) | Fixed |
| r1 | B-3: `check_agent_scope.py` had no CI job in `ci.yml` | Fixed |
| r2 | B-4: `parse_verdict.py` read first `### Verdict` in file, not last (re-validation sections accumulate) | Fixed |
| r3 | All clear | PASS |

**B-4 root cause and fix:** REVIEW files accumulate appended sections on each re-validation.
The verdict parser used `break` on the first `### Verdict` match, returning the oldest verdict.
Fix: removed `break` from the outer loop so all sections are scanned and the last match wins.
Verified adversarially: FAIL→PASS returns PASS; PASS→FAIL returns FAIL; annotated
"PASS (with note)" returns PASS.

**Delivered automation:**

| Workflow | Trigger | Action |
|----------|---------|--------|
| `auto-assign-validator.yml` | `workflow_run` on `ELIS - CI` success (non-main branches) | Auto-assigns Validator agent as PR reviewer |
| `auto-merge-on-pass.yml` | Push to `feature/**`, `chore/**`, `hotfix/**` | Parses `REVIEW_PE<N>.md` via `parse_verdict.py`; merges only if verdict=PASS, veto=false, AND `mergeable_state == clean` |
| `agents-compliance.yml` | PR opened/synchronized | Runs `agents_compliance_check.py`: branch naming, HANDOFF.md, cross-PE contamination |
| `ci.yml` (updated) | PR to `release/2.0` | Added `secrets-scope-check` job running `check_agent_scope.py` |

**Secrets isolation:** `.agentignore` instructs agents to never read `.env*` files.
`.env.example` documents all required env vars without real values. `ELISHttpClient` logs are
sanitized — auth headers/params are never written to stdout or CI logs.

---

### Compliance Automation Chore (PR #228)

**Implementer:** CODEX | **Validator:** Claude Code
**Verdict:** PASS (with 1 non-blocking warning)
**Non-blocking:** `--depth=1` shallow fetch in `agents-compliance.yml` may fail to compute
merge base on old branches. Accepted; can be addressed in a follow-up chore PR.

---

## 4. Product PE Validation Record

| PE | Title | PR | Implementer | Verdict | Rounds |
|----|-------|-----|-------------|---------|--------|
| PE0a | Package skeleton + CLI entrypoints | #208/#209 | CODEX | PASS | 1 |
| PE0b | MVP pipeline migration to `elis` pkg | #211 | CODEX | PASS | 1 |
| PE1a | Run manifest schema + writer utility | #212 | CODEX | PASS | 1 |
| PE1b | Wire manifests into stages + `merge --from-manifest` | #221 | CODEX | PASS | 1 |
| PE2 | Source adapter layer (OpenAlex, CrossRef, Scopus) | #210, #213, #214 | CODEX | PASS | 1 |
| PE3 | Canonical merge stage (`elis merge`) | #216 | CODEX | PASS | 1 |
| PE4 | Deterministic dedup + clusters (`elis dedup`) | #218 | CODEX | PASS | 1 |
| PE5 | ASTA sidecar integration | #220 | CODEX | PASS | 1 |
| PE6 | CLI cut-over, archive legacy scripts | #222 | CODEX | FAIL → PASS | 2 |

**PE6 re-validation:** Two findings (validate.yml trigger mismatch, stale `validate_json.py`
in scripts root) required hotfixes in PR #225 before PASS was issued.

---

## 5. Functional Test Qualification Rounds

FT qualification is a 12-suite end-to-end test of the full ELIS CLI pipeline on a live
environment.

| Round | PR | Suites Passed | Blocking Failures | Outcome |
|-------|-----|:---:|---------|---------|
| r1 | #233 | 5/12 | FT-06 (legacy validate), FT-07 (object-type JSON), FT-09 (Unicode/Windows), FT-10 (ASTA import), FT-03 (manifest path) | NO-GO |
| r2 | #237 | 6/12 | FT-01 contract (secrets gate), FT-03 (manifest path) | NO-GO |
| r3 | #239 | 9/12 | FT-03 (manifest merge path), FT-06, FT-09 | NO-GO |
| r4 | #247 | Stopped at FT-03 | FT-03 blocking | NO-GO |
| **r5** | **#252** | **12/12** | None (B-1 legacy data drift scoped out as known) | **GO** |

**Fixes applied between r4 and r5 (PR #254):**

| Finding | Fix | Location |
|---------|-----|----------|
| B-2/B-3: `elis validate` fails on object-type JSON; double-manifest artifacts | Detect JSON root type before iteration; skip `*_manifest.json` inputs | `elis/cli.py` |
| B-4: `UnicodeEncodeError` on Windows (cp1252 + `→` char) | Replace `→` with `->` in two f-string print statements | `elis/cli.py:425,429` |
| B-5: `ModuleNotFoundError: No module named 'sources'` in ASTA | Lazy import with `importlib`; module not required at CLI startup | `elis/agentic/asta.py` |

---

## 6. CI Enforcement Layer — Current State

Gates active on PRs to `release/2.0`. `ci.yml` also runs on `main`. Note: `agents-compliance.yml` is scoped to `release/2.0` only.

| Gate | Workflow | What it checks |
|------|----------|---------------|
| Lint | `ci.yml` | `ruff check`, `black --check` |
| Tests | `ci.yml` | `pytest` (445 tests, 0 failures at v2.0.0) |
| Secrets scope | `ci.yml` | `check_agent_scope.py` — no agent reads `.env*` |
| AGENTS compliance | `agents-compliance.yml` | Branch naming, HANDOFF.md presence, cross-PE contamination |
| Validator auto-assign | `auto-assign-validator.yml` | Assigns Validator reviewer after CI completes successfully |
| Auto-merge | `auto-merge-on-pass.yml` | Merges only on PASS verdict + CI green + no veto |

---

## 7. Tooling Inventory — Infrastructure Scripts

| Script | Purpose |
|--------|---------|
| `scripts/parse_verdict.py` | Extracts latest verdict from `REVIEW_PE*.md`; used by auto-merge gate; supports deterministic `REVIEW_FILE` env var and annotated verdicts |
| `scripts/check_agent_scope.py` | Verifies no agent reads secrets; run in CI |
| `scripts/check_handoff.py` | Validates HANDOFF.md is present and populated |
| `scripts/check_status_packet.py` | Verifies Status Packet fields in agent PR comments |
| `scripts/check_role_registration.py` | Confirms role registration in `CURRENT_PE.md` |
| `scripts/agents_compliance_check.py` | Full AGENTS.md compliance check: branch naming, file ownership, HANDOFF.md, cross-PE contamination |

---

## 8. Open Items and Known Limitations

| ID | Severity | Description | Status |
|----|----------|-------------|--------|
| NB-1 | Sev-2 | `agents-compliance.yml` uses `--depth=1` shallow fetch; may miss merge base on older branches | Accepted — follow-up chore |
| NB-2 | Sev-2 | FT-06 legacy `json_jsonl/` Appendix A data has pre-PE2 schema drift — `[ERR]` on legacy full-mode validate | Documented as known-data-drift exclusion |
| NB-3 | Sev-3 | `elis screen` produces no stdout summary (silent progress) | Observability gap only; tracked in plan |
| NB-4 | Sev-3 | `validate_appendix()` always returns rc=0 even on schema failure | Documented in tests; not regression-safe |

---

## 9. Release Artifacts

| Artifact | Value |
|----------|-------|
| Release tag | `v2.0.0` (signed SSH, Verified) |
| Main HEAD at audit | `781ab53` (v2.0.0 merge commit) |
| Preservation tag | `v1.0.0` (signed SSH, Verified) — pre-v2 main state |
| Maintenance branch | `maint/v1.x` (at `v1.0.0`) |
| Tag protection | Ruleset `protect-version-tags` — pattern `v*`, no-delete, no-force-push, Active |
| GitHub Releases | `v1.0.0` and `v2.0.0` published |
| Total PRs merged (v2.0 line) | 30+ PRs from PE0a through FT-r5 |
| Test suite | 445 passed, 0 failed |

---

*All infrastructure improvements are shipped and active. The two-agent model is fully enforced
by CI. No blocking items remain.*
