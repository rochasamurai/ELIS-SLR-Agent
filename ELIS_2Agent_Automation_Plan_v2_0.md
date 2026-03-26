# ELIS — 2-Agent Autonomous Model Improvement Plan

**Version:** 3.2
**Date:** 2026-03-25
**Author:** PM (Carlo) + Claude Code (analysis and drafting)
**Base:** Assessment of the 2-Agent model on 2026-03-25 · AGENTS.md v2.0 · ELIS_MultiAgent_Implementation_Plan_v1_6.md

---

## Changelog

| Version | Date | Summary |
|---|---|---|
| v1.0 | 2026-03-25 | Initial plan — gap assessment and 4 automation phases (Phases A–D, 10 PEs) |
| v2.0 | 2026-03-25 | Addition of Phase 0 (auth without API keys) with PE-AUTH-01 and PE-AUTH-02; assessment and rejection of `agent-browser` for auth; addition of PE-SLR-HARVEST-WEB as a future SLR PE |
| v3.0 | 2026-03-25 | Addition of the Parallel Track Model (§ Parallelism) with PE-AUTO-11 (Parallel Track Scheduler); extension of CURRENT_PE.md to support Track B; authoring guidelines for parallelisable PEs; updated roadmap with parallel track diagram |
| v3.1 | 2026-03-25 | Addition of Phase E (Documentary Governance) with PE-PLAN-01 (Architecture Decision Records); hybrid 3-layer model (ADR + LESSONS_LEARNED + PM Journal); ADR template; first batch of 6 retroactive ADRs identified; rules for when to create an ADR integrated into the workflow |
| v3.2 | 2026-03-25 | Addition of the Session Continuity Model — "The PR is the operational memory"; mandatory resumability rule per PE; 3-layer memory model (technical / operational / authority); checkpoints by role; anti-patterns documented; reference to `TWO_AGENT_SESSION_CONTINUITY_RUNBOOK.md` |

---

## Executive Summary

The current 2-Agent model (CODEX + Claude Code, alternating implementer/validator per PE) has
solid governance but requires manual PO intervention at every PE: the PO performs PM-CHORE, assigns
the Validator, reads PR comments, and executes the merge. This plan transforms the model into an **autonomous
loop** where:

1. The **PM Agent** (ELIS on `elis-server`) receives a plan, opens each PE, notifies the agents, and
   closes the merge loop without human intervention.
2. The **Implementer + Validator** pair works entirely via GitHub Actions, PR comments, and
   REVIEW files.
3. When **divergence** occurs (>2 FAILs, scope dispute, technical blocker), the PM Agent arbitrates.
   Only in exceptional cases is the human PO notified.
4. Agents authenticate using **subscription tokens** (without API keys), reducing operational
   cost and dependency on API quotas.

The plan is divided into **6 phases** (Phase 0 + Phases A–E), totalling **14 automation PEs** plus
one future SLR PE.

> **Current state vs. target state:** Everything described from Phase B onwards (autonomous loop) is a
> **future target state**, not the current governance model. `AGENTS.md` remains
> **authoritative** until each automation PE is merged and explicitly adopted.
> Phases A–D do not replace or conflict with the current workflow — they extend it
> progressively after validation.

---

## Plan Structure

```
Phase 0  Auth without API keys       2 PEs   (pre-blocking)
Phase A  Foundation — structural gaps 3 PEs   (prerequisite for B)
Phase B  Autonomous loop             3 PEs   (prerequisite for C)
Phase C  PM Agent as arbiter         2 PEs   (prerequisite for D)
Phase D  Full operation              3 PEs   (+PE-AUTO-11 Parallel Scheduler)
Phase E  Documentary governance      1 PE    (PE-PLAN-01, parallel to any phase)
                                    ──────
Total                               14 automation PEs + 1 SLR PE (future)
```

**Cross-cutting capability (v3.0):** Parallel Track Model — independent PEs executed
simultaneously by both agents. Applicable in all phases where PEs have no
mutual dependency. See section [Parallel Track Model](#parallel-track-model).

**Cross-cutting capability (v3.1):** Architecture Decision Records (ADRs) — structured recording
of architectural decisions and their rationale. Phase E (PE-PLAN-01) creates the infrastructure and the
first retroactive batch. See section [Phase E — Documentary Governance](#phase-e--documentary-governance).

**Cross-cutting capability (v3.2):** Session Continuity — each PE must be resumable without
chat history. Progress is only considered durable when recorded in commits, PE artefacts
(`HANDOFF.md` / `REVIEW_PE<N>.md`), and PR comments. PM monitors via PR + `CURRENT_PE.md`,
not via session memory. See section [Session Continuity Model](#session-continuity-model).

---

## Parallel Track Model

### Observation Origin

During the execution of the PE-MS series (MiniServer), two independent workstreams ran
simultaneously:

| Track | PE | Branch | Implementer agent |
|---|---|---|---|
| A | PE-MS-07 (project store layout) | `feature/pe-ms-07-slr-project-store` | `infra-impl-claude` |
| B | Review of Plan v2.0 (PR #299) | `chore/review-2agent-automation-plan` | `infra-val-codex` |

Whilst Claude Code implemented PE-MS-07, CODEX reviewed the plan on another branch — without
file conflicts, without sequential dependency. When Track A was ready for validation,
CODEX (now free of Track B) validated PE-MS-07, and Claude Code responded to the plan review.

**Empirical conclusion:** the 2-Agent model naturally supports parallelism when PEs
are independent. The current gap is the absence of formalisation and sequencer support
for simultaneous dispatch.

---

### Parallel Track Definition

**Track** = a complete PE workstream (branch + implementer + validator) running
independently of another track in parallel.

The 2-Agent model supports a maximum of **2 simultaneous tracks** (one per agent-engine):

```
Track A: Claude Code implements → CODEX validates
Track B: CODEX implements       → Claude Code validates
```

The two tracks may be at different stages of the cycle:

```
Time →

Track A:  [impl]──────[val]──[merge]
Track B:     [impl]──────────[val]──[merge]
```

Whilst Track A is in validation, Track B may still be in implementation.
When Track A closes, the freed agent may begin Track B's validation — exactly
the pattern observed in PE-MS-07 / PR #299.

---

### Eligibility Criteria for Parallelism

A pair of PEs may run on parallel tracks **only if** all criteria are
satisfied:

| Criterion | Verification |
|---|---|
| **No mutual dependency** | Neither has the other in `depends_on` (direct or transitive) |
| **No file overlap** | File scopes do not intersect (verified by `check_parallel_eligibility.py` — compares `git diff --name-only origin/$BASE..HEAD` of both branches) |
| **Same base branch** | Both depart from the same `origin/$BASE` |
| **Different engines** | Track A uses Claude Code, Track B uses CODEX (or vice versa) — ensures each agent has a clear role |
| **No shared resource** | No single coordination file (e.g. `CURRENT_PE.md`) is modified by both simultaneously |

If any criterion fails, the pair must be executed sequentially.

---

### Plan Authoring Guidelines with Parallelism

When writing a new PE plan, the PM must:

**1. Map the dependency DAG**

```
PE-A ──depends──> PE-C
PE-B              PE-D ──depends──> PE-E
                  PE-B
```

PEs with no edge between them in the DAG are candidates for parallelism.

**2. Identify parallel cohorts**

A **parallel cohort** is a set of PEs that can be started simultaneously
because all their dependencies are already satisfied.

```yaml
# Example cohort in plan format
parallel_cohort_1:
  - PE-AUTH-01   # engine: claude
  - PE-AUTH-02   # engine: codex
  # Criterion: neither depends on the other; distinct files
```

**3. Mark PEs with `parallel_eligible`**

Each PE in the plan must have:
```yaml
parallel_eligible: true   # may run on a parallel track if cohort available
parallel_eligible: false  # must wait for dependencies to complete before starting
```

**4. Respect the 2-active-track limit**

With only 2 engine-agents (Claude Code + CODEX), the maximum of simultaneous tracks is 2.
Cohorts with >2 eligible PEs must be partitioned into sub-rounds.

**5. Prefer parallelism within same-phase cohorts**

PEs from different phases are rarely good candidates for parallelism because they tend to have
transitive dependencies between phases. Prioritise parallelism within the same phase.

---

### CURRENT_PE.md Extension for Track B

The current `CURRENT_PE.md` supports a single active PE. For parallelism, the structure is
extended with an optional Track B field:

```markdown
## Track A — Primary PE

| Field  | Value                              |
|--------|------------------------------------|
| PE     | PE-AUTO-04                         |
| Branch | feature/pe-auto-04-impl-runner     |

## Track B — Parallel PE (optional)

| Field  | Value                              |
|--------|------------------------------------|
| PE     | PE-AUTO-03                         |
| Branch | feature/pe-auto-03-precommit       |
| Status | implementing                       |
| Note   | Parallel to Track A — no mutual dependency confirmed |
```

**Rules:**
- Track B may only be populated if the eligibility criterion is satisfied
- `check_current_pe.py` validates that Track A and Track B have no dependency between them
- When Track B closes (merge), the field is removed — Track A remains as primary
- PM populates Track B manually (or the Sequencer via PE-AUTO-11)

---

### Cross-Validation Pattern

Parallelism creates an additional opportunity: when one track closes,
the freed agent may validate the other track once it reaches Gate 1 (ready-for-validation).
If Track B is still implementing when Track A closes, the freed agent waits for Gate 1.

**"Cross-Validate" Pattern:**

```
Track A:  [impl: Claude]──[PASS]──[merge]
                                ↘
Track B:       [impl: CODEX]────────[val: Claude]──[PASS]──[merge]
```

This maximises throughput: no agent sits idle between tracks.

**Rule:** The agent who has just implemented Track A CANNOT be the validator of
Track A (existing rule). But they can and should be the validator of Track B.

---

## Context Analysis — Browser-Based Authentication

### Document assessed

`open_claw_browser_auth_configuration_chat_gpt_claude.md` (ChatGPT, 2026-03-25)

### What was correct in the ChatGPT document

| Item | Status |
|---|---|
| `codex auth login` — OAuth browser flow | Valid — real mechanism of the Codex CLI |
| `claude setup-token` — headless token | Valid — supported by Claude Code |
| Do not copy cookies / do not intercept traffic | Correct — standard security practice |
| Role distribution (Codex=impl, Claude=validation) | Aligned with AGENTS.md |

### What was fabricated (hallucinations)

| Claim | Issue |
|---|---|
| `openclaw models auth login --provider openai-codex` | Command does not exist in OpenClaw |
| `openclaw models auth paste-token --provider anthropic` | Ditto — no evidence in codebase |
| `"$schema": "https://docs.openclaw.ai/schema/openclaw.json"` | Non-existent URL |
| Structure `agents.defaults.model.primary` + `agents.defaults.models` | Incompatible with real `openclaw.json` (`agents.list[]`) |
| `openai-codex/gpt-5.4` as model ID | The repo uses `openai/gpt-5.1-codex` |
| `openai/gpt-5-mini` | Model ID not confirmed in current ELIS runtime/config |
| `"context1m": false` | Fictitious Anthropic API parameter |

### Central architectural problem

OpenClaw calls the OpenAI and Anthropic APIs via HTTP with API keys
(`Authorization: Bearer sk-*`). The ChatGPT.com or Claude.ai browser session uses
session cookies that **are not accepted** by the `api.openai.com` or `api.anthropic.com` endpoint.
These are two completely separate authentication systems:

```
ChatGPT.com ←── browser session cookies ──→ chat.openai.com   (consumer web)
OpenAI API  ←── Authorization: Bearer sk-* ─→ api.openai.com  (developer API)
```

The correct solution to reduce API key dependency is to use CLI binaries
(`codex`, `claude`) as execution backends in CI runners, authenticated via
OAuth token (`codex auth login`) and setup-token (`claude setup-token`) respectively.

### Assessment of `vercel-labs/agent-browser`

**Repo:** `https://github.com/vercel-labs/agent-browser` · v0.22.2 · Rust · Apache-2.0

The `agent-browser` is a headless browser automation CLI (Rust + CDP + headless Chrome)
designed to be used **by** AI agents as a work tool — not as an
authentication mechanism.

| Proposed use | Assessment |
|---|---|
| Replace `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` in OpenClaw | **Not applicable** — does not interfere with HTTP API calls |
| Continuous auth for Codex/Claude in the autonomous loop | **Not applicable** — setup-token is already headless |
| One-time setup of `codex auth login` on a headless server | **Conditionally useful** — if port-forwarding is not feasible |
| SLR harvest from sources without a public API (IEEE, ACM, Springer) | **Adopt** — high-value use case |
| PM Agent web smoke tests | **Adopt in future** |

**Compatibility with elis-server:** ✓ Ubuntu 24.04 · x86_64 · headless · systemd-compatible

The `agent-browser` enters as a future PE in the SLR phase (see section PE-SLR-HARVEST-WEB), not
in Phase 0 for authentication.

---

## Phase 0 — Authentication Without API Keys

> **Objective:** Replace `OPENAI_API_KEY` and `ANTHROPIC_API_KEY` with subscription-based
> authentication in CI runners (GitHub Actions). This is a blocking prerequisite for Phase B,
> as agent runners must not depend on API keys.
>
> **Scope:** GitHub Actions runners. OpenClaw on `elis-server` retains API keys until
> support for CLI binaries as backends is verified (documented in PE-AUTH-02).

---

### PE-AUTH-01 · Codex CLI — OAuth Token for Headless Runners

| Field | Value |
|---|---|
| Domain | auth |
| Depends On | — |
| Implementer | `infra-impl-claude` |
| Validator | `infra-val-codex` |

**Context:** `codex auth login` opens a browser for the OAuth redirect. On a headless
runner, the interactive flow is not applicable. The proposed solution is an **offline token extraction**:
the PO runs `codex auth login` once on the local machine; the persisted token is extracted and
stored as a GitHub Secret.

> **⚠️ Mechanism to validate — do not assume as foundation until PE-AUTH-01 is complete:**
> The portability of the token generated by `codex auth login` between machines, and official
> support for headless reuse, are not publicly documented. The Pre-verification below is a
> **blocking prerequisite** — the exact mechanism is only determined after real execution.
> Later phases (PE-AUTO-04 onwards) depend on the outcome of this validation.

**Mandatory pre-verification before implementing:**

```bash
# On the PO's machine
codex auth login
# After browser callback, locate the token file (Windows PowerShell):
Get-ChildItem -Path "$env:USERPROFILE\.codex" -Filter "*.json" -Recurse -ErrorAction SilentlyContinue | Select-Object FullName
# Linux / macOS:
find ~/.codex ~/.config/openai -name "*.json" 2>/dev/null
```

> **Pre-verification finding (2026-03-26):** `codex auth status` subcommand is
> not supported in the current CLI (`error: unrecognized subcommand 'status'`).
> The mechanism is determined by inspecting `auth.json` directly.

Pre-verification result (PO machine `carlo-notebook`, Windows, `auth_mode=chatgpt`):

| Scenario | Mechanism adopted |
|---|---|
| `OPENAI_API_KEY` present as top-level field in `auth.json` | Store as GitHub Secret `OPENAI_API_KEY` — consumed directly by the Codex CLI via standard env var |

**Deliverables:**

- `docs/openclaw/CODEX_AUTH_SETUP.md` — runbook: generation, extraction, storage, renewal
- `scripts/extract_codex_token.py` — reads local `auth.json`, prints only metadata (field names, `auth_mode`, `last_refresh`, boolean presence) — never the value (rule `§13`)
- `scripts/verify_codex_auth.py` — verifies the runner environment: `OPENAI_API_KEY` set + `codex` on PATH + `codex --version` exits 0

```python
# scripts/verify_codex_auth.py
import os, shutil, subprocess, sys
api_key = os.environ.get("OPENAI_API_KEY", "")
if not api_key:
    print("FAIL: OPENAI_API_KEY is not set in environment.", file=sys.stderr)
    sys.exit(1)
print(f"OK: OPENAI_API_KEY is set (length={len(api_key)})")
result = subprocess.run(["codex", "--version"], capture_output=True, text=True, timeout=15)
if result.returncode != 0:
    sys.exit(1)
print(f"OK: codex --version → {result.stdout.strip()}")
```

**Acceptance Criteria:**

| # | Criterion |
|---|---|
| AC-1 | `OPENAI_API_KEY` secret is set in the runner environment and `codex --version` exits 0 |
| AC-2 | No token value appears in any CI log |
| AC-3 | `scripts/verify_codex_auth.py` exits 0 on the runner |
| AC-4 | Runbook documents the renewal procedure; expiry timing is not exposed by the current CLI — renewal trigger is runner authentication failure |
| AC-5 | `OPENAI_API_KEY` is injected from GitHub Secrets only — never hardcoded in workflow files |

**Documented limitations:**

- Subject to ChatGPT Plus usage limits — not equivalent to API throughput
- Token expires — mandatory renewal before each long PE series
- `codex auth status` subcommand not available in current CLI — expiry and quota cannot be polled programmatically; monitor via runner failures

---

### PE-AUTH-02 · Claude Code — setup-token in Runners and Verification on elis-server

| Field | Value |
|---|---|
| Domain | auth |
| Depends On | — (parallel to PE-AUTH-01) |
| Implementer | `infra-impl-codex` |
| Validator | `infra-val-claude` |

**Two contexts with different mechanisms:**

#### Context A: GitHub Actions runner (headless agents)

`claude setup-token` generates a token for CI/headless use — the official Anthropic mechanism.

```bash
# On the PO's machine — generate once
claude setup-token
# Output: token "sk-ant-st-..."
# Store as CLAUDE_SETUP_TOKEN in GitHub Secrets
```

On the runner:

```bash
export CLAUDE_SETUP_TOKEN="${{ secrets.CLAUDE_SETUP_TOKEN }}"
claude --version   # verify it works without ANTHROPIC_API_KEY
```

`scripts/verify_claude_auth.py`:

```python
import subprocess, sys, os
if not os.environ.get("CLAUDE_SETUP_TOKEN"):
    print("FAIL: CLAUDE_SETUP_TOKEN not set", file=sys.stderr)
    sys.exit(1)
result = subprocess.run(["claude", "--version"], capture_output=True)
if result.returncode != 0:
    print("FAIL: claude CLI not available", file=sys.stderr)
    sys.exit(1)
print("OK: claude auth ready")
```

#### Context B: OpenClaw on elis-server

Mandatory pre-verification — determines whether `ANTHROPIC_API_KEY` can be removed from elis-server:

```bash
# On elis-server — test all three hypotheses:

# Hypothesis 1: OpenClaw accepts CLAUDE_SETUP_TOKEN as an alternative environment variable
CLAUDE_SETUP_TOKEN=<token> openclaw agent run --agent-id infra-impl-claude --task "ping"

# Hypothesis 2: setup-token can be converted to a temporary API key
claude api-key --from-setup-token  # if it exists

# Hypothesis 3: OpenClaw does not support it — ANTHROPIC_API_KEY remains for elis-server
```

**If Context B is not supported:** `ANTHROPIC_API_KEY` remains on `elis-server` (documented
with a review date). The setup-token is applied only to CI runners (Context A).

**Deliverables:**

- `docs/openclaw/CLAUDE_AUTH_SETUP.md` — full runbook for both contexts
- `scripts/verify_claude_auth.py`
- Documented result of Context B verification

**Acceptance Criteria:**

| # | Criterion |
|---|---|
| AC-1 | Headless runner executes `claude --version` without `ANTHROPIC_API_KEY`, using `CLAUDE_SETUP_TOKEN` |
| AC-2 | No token value in any log |
| AC-3 | `scripts/verify_claude_auth.py` exits 0 |
| AC-4 | Context B documented with verification result (supported / not-supported / workaround) |
| AC-5 | If Context B not-supported: decision recorded with review date in runbook |

---

## Phase A — Foundation (structural gaps)

> **Objective:** Eliminate the three structural gaps that prevent reliable automation, identified
> in the assessment of 2026-03-25. Prerequisite for Phase B.

---

### PE-AUTO-01 · Bot Accounts and GitHub Fine-Grained PATs

| Field | Value |
|---|---|
| Domain | infra |
| Depends On | PE-AUTH-01, PE-AUTH-02 |
| Implementer | `infra-impl-claude` |
| Validator | `infra-val-codex` |

**Problem it solves:** Single-account GitHub constraint — the Validator cannot issue
a formal GitHub Review on their own PR (assessment §2.1).

**Three separate GitHub identities:**

| Account | Engine | Role | PAT Scopes |
|---|---|---|---|
| `elis-codex-bot` | CODEX | Implementer or Validator as per PE | Contents write, Pull requests write, Issues write |
| `elis-claude-bot` | Claude Code | Implementer or Validator as per PE | Contents write, Pull requests write, Issues write |
| `elis-pm-bot` | PM Agent / CI orchestration | Sequencer, arbiter, merge | Contents write, Pull requests write, Issues write, Workflows read |

Repository GitHub Secrets:

```
CODEX_BOT_TOKEN        ← PAT for elis-codex-bot
CLAUDE_BOT_TOKEN       ← PAT for elis-claude-bot
PM_BOT_TOKEN           ← PAT for elis-pm-bot
OPENAI_API_KEY         ← Codex CLI auth token (PE-AUTH-01; extracted from auth.json `OPENAI_API_KEY` field)
CLAUDE_SETUP_TOKEN     ← Claude Code setup-token (PE-AUTH-02)
```

**Branch protection updated for `main`:**

- Require 1 approving review from `elis-claude-bot` or `elis-codex-bot` (not the PR author)
- Mandatory status checks: `quality`, `tests`, `validate`, `gate-1`
- Direct push blocked — PRs mandatory

**Acceptance Criteria:**

| # | Criterion |
|---|---|
| AC-1 | `elis-codex-bot` opens PR and `elis-claude-bot` approves (without "Cannot approve your own PR") |
| AC-2 | Branch protection active — PR without green status check does not merge |
| AC-3 | Secrets configured — `verify_codex_auth.py` and `verify_claude_auth.py` exit 0 on runners |
| AC-4 | `OPENAI_API_KEY` and `ANTHROPIC_API_KEY` removed from agent runners |

---

### PE-AUTO-02 · CURRENT_PE.md Validation in CI

| Field | Value |
|---|---|
| Domain | infra |
| Depends On | PE-AUTO-01 |
| Implementer | `infra-impl-codex` |
| Validator | `infra-val-claude` |

**Problem it solves:** `CURRENT_PE.md` as a single point of failure without schema validation
(assessment §2.2). Eliminates the error class LL-05 (PE skipped due to incorrect manual edit).

**Deliverables:**

`scripts/check_current_pe.py` — verifies:

1. All required fields present and non-empty (`PE`, `Branch`, `Base branch`,
   `Plan file`, `Agent roles`)
2. PE ID in the correct format (`PE-[A-Z]+-[0-9]+`)
3. Branch follows convention `feature/pe-*` or `chore/*`
4. Status of the active PE is `planning` or `implementing`
5. **Alternation rule:** implementer engine ≠ engine of the last PE `merged` in the same domain
6. Agent roles are opposite (impl engine ≠ val engine)

CI step on pushes to `main` (`ci.yml`):

```yaml
- name: Validate CURRENT_PE.md
  run: python scripts/check_current_pe.py
```

**Acceptance Criteria:**

| # | Criterion |
|---|---|
| AC-1 | `check_current_pe.py` exits 0 on the current state of `CURRENT_PE.md` |
| AC-2 | Blank field → exits 1 with descriptive error message |
| AC-3 | Alternation rule violation → exits 1 |
| AC-4 | CI step active — push with invalid `CURRENT_PE.md` is blocked |
| AC-5 | 8 unit tests covering all validation cases |

---

### PE-AUTO-03 · Pre-commit Hooks + HANDOFF Namespacing

| Field | Value |
|---|---|
| Domain | infra |
| Depends On | PE-AUTO-02 |
| Implementer | `infra-impl-claude` |
| Validator | `infra-val-codex` |

**Problems it solves:**

- Absence of pre-commit hooks — black/ruff only checked in CI after push (assessment §2.5)
- `HANDOFF.md` at root overwritten at each PE — collision between PEs (assessment §2.4)

**`.pre-commit-config.yaml`:**

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 24.8.0
    hooks:
      - id: black
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.6.9
    hooks:
      - id: ruff
  - repo: local
    hooks:
      - id: scope-gate
        name: Agent scope gate
        entry: python scripts/check_agent_scope.py
        language: python
        pass_filenames: false
      - id: current-pe-validation
        name: Validate CURRENT_PE.md
        entry: python scripts/check_current_pe.py
        language: python
        files: CURRENT_PE.md
        pass_filenames: false
```

**HANDOFF Namespacing:**

```
handoffs/
  HANDOFF_PE-MS-06.md    ← immutable history (migrated from root)
  HANDOFF_PE-MS-05.md
  HANDOFF_PE-MS-04.md
  ...
HANDOFF.md               ← script-generated copy of the active PE
                           (NOT symlink — symlinks are fragile on Windows/git)
```

`pe_sequencer.py` writes the copy of `handoffs/HANDOFF_{ACTIVE_PE}.md` to the root
`HANDOFF.md` at each PE advance. Do not use symlinks — inconsistent behaviour
between Windows (core.symlinks=false by default) and Linux.

`check_handoff.py` updated to:
- Accept root `HANDOFF.md` (current form) during migration
- After full migration: also verify `handoffs/HANDOFF_{PE_ID}.md` based on
  `CURRENT_PE.md`

**Acceptance Criteria:**

| # | Criterion |
|---|---|
| AC-1 | `pre-commit run --all-files` exits 0 on the current repo state |
| AC-2 | `git commit` with a black error is blocked locally (pre-commit hook active) |
| AC-3 | Historical HANDOFFs migrated to `handoffs/` — root `HANDOFF.md` is a script-generated copy (not a symlink) |
| AC-4 | `check_handoff.py` exits 0 resolving via root `HANDOFF.md` and via `handoffs/HANDOFF_{PE_ID}.md` |
| AC-5 | Onboarding documentation updated with `pre-commit install` instruction |

---

## Phase B — Autonomous PE Loop

> **Objective:** The Implementer + Validator pair executes a complete PE without human intervention.
> The trigger is a push of `CURRENT_PE.md` by the PM Agent; the closure is the Gate 2 auto-merge.

---

### PE-AUTO-04 · Implementer Agent Runner

| Field | Value |
|---|---|
| Domain | infra |
| Depends On | PE-AUTH-01, PE-AUTH-02, PE-AUTO-01 |
| Implementer | `infra-impl-codex` |
| Validator | `infra-val-claude` |

**Trigger:** push of `CURRENT_PE.md` to `main` with status `planning → implementing`
(detected by `ci-current-pe.yml` → `workflow_dispatch` for `implementer-runner.yml`).

**`implementer-runner.yml` (fragment):**

```yaml
name: Implementer Agent Runner
on:
  workflow_dispatch:
    inputs:
      pe_id:       { required: true }
      branch:      { required: true }
      engine:      { required: true }   # codex | claude
      plan_file:   { required: true }
      base_branch: { required: true }

jobs:
  run-implementer:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Authenticate Codex CLI
        if: inputs.engine == 'codex'
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: python scripts/verify_codex_auth.py

      - name: Authenticate Claude CLI
        if: inputs.engine == 'claude'
        env:
          CLAUDE_SETUP_TOKEN: ${{ secrets.CLAUDE_SETUP_TOKEN }}
        run: python scripts/verify_claude_auth.py

      - name: Run Implementer Agent (CODEX)
        if: inputs.engine == 'codex'
        env:
          GH_TOKEN: ${{ secrets.CODEX_BOT_TOKEN }}
        run: |
          python scripts/run_codex_agent.py \
            --pe-id "${{ inputs.pe_id }}" \
            --plan "${{ inputs.plan_file }}" \
            --branch "${{ inputs.branch }}"

      - name: Run Implementer Agent (Claude)
        if: inputs.engine == 'claude'
        env:
          GH_TOKEN: ${{ secrets.CLAUDE_BOT_TOKEN }}
        run: |
          python scripts/run_claude_agent.py \
            --pe-id "${{ inputs.pe_id }}" \
            --plan "${{ inputs.plan_file }}" \
            --branch "${{ inputs.branch }}"
```

The scripts `run_codex_agent.py` / `run_claude_agent.py`:

1. Build the system prompt from `AGENTS.md` + `CURRENT_PE.md` + PE acceptance
   criteria from the plan
2. Invoke the CLI binary (`codex` / `claude`) with tool use (git, gh CLI, python)
3. Follow the §5.1 flow autonomously: implement → quality gates → HANDOFF → draft PR
   → ready PR → Status Packet
4. Have a `MAX_COMMITS=20` limit and a 4h timeout for safety

**Acceptance Criteria:**

| # | Criterion |
|---|---|
| AC-1 | Runner fires upon detecting a change in `CURRENT_PE.md` with status `implementing` |
| AC-2 | Auth via `OPENAI_API_KEY` (Codex) / `CLAUDE_SETUP_TOKEN` (Claude) — injected from GitHub Secrets, never hardcoded |
| AC-3 | PR opened by the correct account (`elis-codex-bot` or `elis-claude-bot`) |
| AC-4 | `HANDOFF.md` committed before the PR is converted to ready |
| AC-5 | Runner exits with exit 1 if `MAX_COMMITS` or timeout are reached |

---

### PE-AUTO-05 · Validator Agent Runner

| Field | Value |
|---|---|
| Domain | infra |
| Depends On | PE-AUTO-04 |
| Implementer | `infra-impl-claude` |
| Validator | `infra-val-codex` |

**Trigger:** Gate 1 CI posts the comment `@claude-code — assigned as Validator. Begin review.`
(already implemented in `auto-assign-validator.yml`). New workflow `validator-dispatch.yml`
detects the comment and triggers `validator-runner.yml` with the correct engine.

**Validator Runner Flow:**

1. Reads `HANDOFF.md` and verifies scope via `git diff --name-status`
2. Runs quality gates
3. Validates each AC verbatim from the plan
4. Adds adversarial tests
5. Writes `REVIEW_PE<N>.md` with verdict
6. Verifies with `check_review.py` before committing
7. Posts formal PR review via `elis-claude-bot` or `elis-codex-bot`
   (account opposite to the PR author — eliminating the single-account constraint)

**Acceptance Criteria:**

| # | Criterion |
|---|---|
| AC-1 | Validator triggers automatically after Gate 1 comment |
| AC-2 | `REVIEW_PE<N>.md` committed on the branch with verbatim evidence |
| AC-3 | Formal GitHub Review (`approve` / `request-changes`) posted by the opposite account |
| AC-4 | Gate 2 reads the verdict and auto-merges on PASS |
| AC-5 | On FAIL: Implementer receives fix assignment via PR comment from `elis-pm-bot` |

---

### PE-AUTO-06 · PE Sequencer — Automatic Advance Between PEs

| Field | Value |
|---|---|
| Domain | infra |
| Depends On | PE-AUTO-02, PE-AUTO-05 |
| Implementer | `infra-impl-codex` |
| Validator | `infra-val-claude` |

**Trigger:** `pull_request` type `closed` + `merged == true` on `feature/**` branches.

**`scripts/pe_sequencer.py`:**

1. Reads the plan and identifies the merged PE
2. Marks status `merged` in the `CURRENT_PE.md` registry
3. Identifies the next PE in the sequence respecting `Depends On` (DAG)
4. Applies the alternation rule to define the next implementer's engine
5. Opens a new branch via `git checkout -b`
6. Updates `CURRENT_PE.md` with the new PE, branch, and agent roles
7. Commits as `elis-pm-bot` with message `chore(pm): auto-advance to PE-XXXX`
8. Triggers `implementer-runner.yml` via `workflow_dispatch`

If there is no next PE available (unsatisfied dependency or end of series):
notifies the PM Agent on Discord and halts the loop awaiting PO instruction.

**Acceptance Criteria:**

| # | Criterion |
|---|---|
| AC-1 | After merging PE-N, `CURRENT_PE.md` is automatically updated to PE-N+1 |
| AC-2 | Alternation rule is respected — verified by `check_current_pe.py` |
| AC-3 | If next PE has an unsatisfied dependency: loop stops and notifies Discord |
| AC-4 | End of series: PM Agent posts completion summary on Discord |
| AC-5 | All automatic PM-CHOREs are recorded in the housekeeping table |

---

## Phase C — PM Agent as Arbiter

> **Objective:** The PM Agent (ELIS) resolves divergences between agents without escalating to the PO.
> Activated by the triggers below; the PO is only called in exceptional cases.

---

### PE-AUTO-07 · PM Agent Arbitration Protocol

| Field | Value |
|---|---|
| Domain | infra |
| Depends On | PE-AUTO-04, PE-AUTO-05 |
| Implementer | `infra-impl-claude` |
| Validator | `infra-val-codex` |

**Arbitration triggers:**

| Trigger | Condition | Detection |
|---|---|---|
| FAIL round 3 | Third FAIL cycle on the same PE | Counter in PR labels |
| Scope dispute | Validator claims out-of-scope, Implementer disagrees | Keyword in REVIEW file |
| Technical blocker | CI fails with `pm-escalation` flag | Workflow output |
| Timeout | Runner without a commit for >4h | Workflow elapsed time check |

**Arbitration flow (`pm-arbiter.yml`):**

```
Trigger detected
  └─> PM Agent reads:
        - CURRENT_PE.md (PE context)
        - acceptance criteria in the plan
        - HANDOFF.md (Implementer's position)
        - REVIEW_PE<N>.md (Validator's position)
        - git diff --name-status (real scope vs. declared)
  └─> Decides between 4 options:
        SIDE_IMPLEMENTER  → Validator over-scoped; PM justifies and instructs to accept
        SIDE_VALIDATOR    → Implementer must fix; post fix assignment
        SPLIT_PE          → Legitimate conflict; creates additional PE in plan
        ESCALATE_PO       → Beyond arbitration capacity; notifies human PO
  └─> Posts decision in PR as elis-pm-bot (section "## PM Arbitration")
  └─> Updates CURRENT_PE.md status → "arbitration-resolved" or "blocked"
  └─> Adds entry to LESSONS_LEARNED.md automatically
```

**Escalation criteria to human PO** (the only cases that reach the human):

- Architectural conflict requiring a product scope decision
- Ambiguity in the plan that the PM Agent cannot resolve from acceptance criteria
- >3 arbitration iterations on the same PE
- Any PE that touches production secrets or credentials

**Acceptance Criteria:**

| # | Criterion |
|---|---|
| AC-1 | Arbitration triggered automatically on FAIL round 3 |
| AC-2 | Decision posted as PR comment from `elis-pm-bot` with section `## PM Arbitration` |
| AC-3 | Entry created in `LESSONS_LEARNED.md` for each arbitration |
| AC-4 | ESCALATE_PO notifies PO on Discord with a structured summary |
| AC-5 | No PE in `blocked` for more than 24h without PO notification |

---

### PE-AUTO-08 · Discord Loop for Autonomous Operation

| Field | Value |
|---|---|
| Domain | infra |
| Depends On | PE-AUTO-06, PE-AUTO-07 |
| Implementer | `infra-impl-codex` |
| Validator | `infra-val-claude` |

The PM Agent already has Discord integration (PE-MS-03). This PE expands the protocol for the
autonomous loop, adding PE lifecycle events and PO control commands.

**Events reported automatically:**

```
[AUTO] PE-MS-07 started · Implementer: elis-codex-bot · Auth: OAuth ✓
[AUTO] PE-MS-07 Gate 1 PASS · Validator assigned: elis-claude-bot
[AUTO] PE-MS-07 FAIL round 2 · Arbiter triggered
[ARBITER] PE-MS-07 → SIDE_VALIDATOR · fix AC-3 scope
[AUTO] PE-MS-07 PASS · merged · next: PE-MS-08 auto-starting
[ESCALATE] PE-MS-09 requires PO decision · reason: architecture ambiguity
```

**PO Discord commands:**

| Command | Action |
|---|---|
| `!pe status` | Loop state — active PE, round, agents, auth quota |
| `!pe veto` | Applies `pm-review-required` to the open PR |
| `!pe pause` | Stops the sequencer after the current PE |
| `!pe resume` | Resumes the sequencer |
| `!pe auth-check` | Verifies OAuth/setup-token validity without printing values |
| `!pe override PASS` | Forces merge with mandatory audit entry in `LESSONS_LEARNED.md` |

**Acceptance Criteria:**

| # | Criterion |
|---|---|
| AC-1 | Each PE lifecycle event posted to Discord within 60s of the trigger |
| AC-2 | `!pe status` returns current state with autonomy rate |
| AC-3 | `!pe veto` applies label and stops sequencer in <30s |
| AC-4 | `!pe auth-check` reports token status without exposing values |
| AC-5 | ESCALATE_PO mentions the PO's `@` on Discord |

---

## Phase D — Full Operation

> **Objective:** The PO delivers a new plan and the system executes all PEs autonomously,
> with continuous visibility via Discord and dashboard.

---

### PE-AUTO-09 · Plan Loader — New Plan Ingestion

| Field | Value |
|---|---|
| Domain | infra |
| Depends On | PE-AUTO-06, PE-AUTO-08 |
| Implementer | `infra-impl-claude` |
| Validator | `infra-val-codex` |

**Deliverable:** `scripts/plan_loader.py` + JSON Schema `schemas/plan_schema.json`

Validations before starting the series:

1. Valid JSON schema (mandatory fields per PE: `id`, `domain`, `depends_on`,
   `implementer`, `validator`, `acceptance_criteria`)
2. All `depends_on` form a valid DAG (no cycles)
3. Alternation rule can be applied to the entire series without violations
4. First PE has `depends_on: []` or dependencies already `merged`

**Delivery interfaces:**

- **Discord:** `!plan load` with attached `.md` or `.json` file
- **Direct PR:** PO opens PR with the plan file. CI validates. PR approval = start authorisation.

**Acceptance Criteria:**

| # | Criterion |
|---|---|
| AC-1 | `plan_loader.py` exits 0 for a valid plan, 1 with diagnosis for invalid |
| AC-2 | Cycle in dependency DAG → rejected with cycle diagram |
| AC-3 | Alternation rule violation → rejected with indication of the problematic PE |
| AC-4 | `CURRENT_PE.md` generated automatically for the first PE |
| AC-5 | Discord `!plan load` confirms validation before starting sequencer |

---

### PE-AUTO-10 · Observability Dashboard

| Field | Value |
|---|---|
| Domain | infra |
| Depends On | PE-AUTO-09 |
| Implementer | `infra-impl-codex` |
| Validator | `infra-val-claude` |

**Deliverable:** `scripts/generate_pe_status_report.py`

Example output:

```
PE Series: ELIS MiniServer v1.6
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PE-MS-01  merged    2026-03-23  PASS (round 1)
PE-MS-02  merged    2026-03-23  PASS (round 1)
PE-MS-03  merged    2026-03-24  PASS (round 3 — 2 arbiter interventions)
PE-MS-04  merged    2026-03-25  PASS (round 1)
PE-MS-05  merged    2026-03-25  PASS (round 1)
PE-MS-06  active    —           implementing · elis-codex-bot · started 14:32
PE-MS-07  planned   —           waiting on PE-MS-06
PE-MS-08  planned   —           waiting on PE-MS-07
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Autonomy rate: 5/5 PEs merged without escalation (100%)
Arbiter interventions: 2 (PE-MS-03)
PO interventions: 0
Auth status: codex OK (expires 2026-04-25) · claude OK (no expiry)
```

Posted to Discord channel `#pe-status` every hour via PM Agent cron.

**Acceptance Criteria:**

| # | Criterion |
|---|---|
| AC-1 | Report generated correctly from the current state of `CURRENT_PE.md` |
| AC-2 | Autonomy rate calculated correctly |
| AC-3 | Auth validity status included without exposing values |
| AC-4 | PM Agent posts report to Discord every hour |
| AC-5 | `!pe status` uses the same report for on-demand response |

---

### PE-AUTO-11 · Parallel Track Scheduler

| Field | Value |
|---|---|
| Domain | infra |
| Depends On | PE-AUTO-06 (Sequencer), PE-AUTO-09 (Plan Loader) |
| Implementer | `infra-impl-claude` |
| Validator | `infra-val-codex` |

**Objective:** Extend `pe_sequencer.py` and `check_current_pe.py` to support simultaneous
dispatch of two independent PEs (Track A + Track B).

**Deliverables:**

- `scripts/pe_sequencer.py` — extension of the existing module:
  - Upon advancing after a merge, check whether there are ≥2 independent PEs ready in the DAG
  - If so: dispatch Track A **and** Track B simultaneously via `workflow_dispatch`
  - Assign alternating engines: Track A = current-engine, Track B = opposite-engine
  - Record both active tracks in `CURRENT_PE.md`

- `scripts/check_current_pe.py` — extension:
  - Accept the optional `Track A / Track B` structure
  - Validate that Track A and Track B have no mutual dependency (direct or transitive)
  - Reject Track B if `parallel_eligible: false` in the plan
  - (file overlap checking is the responsibility of `check_parallel_eligibility.py`, not this script)

- `scripts/check_parallel_eligibility.py` — new script:
  - Receives two PE IDs and the plan file
  - Returns `ELIGIBLE` or a list of failed criteria (no dependency, no file overlap, different engines)
  - Used by the sequencer and by PM manually

- `docs/openclaw/PARALLEL_TRACK_GUIDE.md` — operational guide:
  - How to identify parallel cohorts in a plan
  - How to manually populate `CURRENT_PE.md` Track B
  - How the sequencer decides on parallelism automatically

**Sequencer decision logic:**

```python
def next_dispatch(dag, merged_set, current_engine):
    ready = [pe for pe in dag if all(d in merged_set for d in pe.depends_on)]
    if len(ready) == 0:
        notify_discord("No PEs ready — waiting")
        return
    if len(ready) == 1 or not can_parallelize(ready[0], ready[1], dag):
        dispatch_single(ready[0], engine=current_engine)
        return
    # Two independent PEs available — parallel dispatch
    track_a, track_b = ready[0], ready[1]
    dispatch_track(track_a, engine=current_engine)
    dispatch_track(track_b, engine=opposite(current_engine))
    update_current_pe_dual_track(track_a, track_b)

def can_parallelize(pe_a, pe_b, dag):
    return (
        not has_dependency(pe_a, pe_b, dag) and
        not has_dependency(pe_b, pe_a, dag) and
        not scopes_overlap(pe_a, pe_b)
    )
```

**Acceptance Criteria:**

| # | Criterion |
|---|---|
| AC-1 | `check_parallel_eligibility.py` returns `ELIGIBLE` for PE-MS-07 ∥ PR #299 (`chore/review-2agent-automation-plan`) — empirical case documented in this plan; and returns `ELIGIBLE` for PE-AUTH-01 + PE-AUTH-02 as validation by structural criteria (no mutual dependency, distinct files) |
| AC-2 | `check_parallel_eligibility.py` returns `INELIGIBLE` for PEs with mutual dependency |
| AC-3 | Sequencer performs dual dispatch when DAG has ≥2 ready and eligible PEs |
| AC-4 | `check_current_pe.py` validates Track A + Track B structure and rejects invalid state |
| AC-5 | When Track A closes: Track B remains active; if Track B is at Gate 1 (ready-for-validation), the agent freed from Track A transitions immediately to Track B validation; if Track B is still in implementation, the agent waits for Track B to reach Gate 1 before beginning validation |
| AC-6 | `PARALLEL_TRACK_GUIDE.md` covers all 5 eligibility criteria with examples |

---

## Future PE — SLR Harvest Web

### PE-SLR-HARVEST-WEB · agent-browser for Sources Without a Public API

| Field | Value |
|---|---|
| Domain | slr |
| Depends On | PE-MS-06 (SLR phase workspaces) |
| Implementer | `harvest-impl-codex` |
| Validator | `harvest-val-claude` |

**Motivation:** The current SLR pipeline has 3 adapters (Crossref, OpenAlex, Scopus). Relevant
sources such as IEEE Xplore, ACM Digital Library, Springer Link, and Web of Science do not have
a free public API but do have web portals with advanced search support.

**`agent-browser`** (`vercel-labs/agent-browser` v0.22.2, Apache-2.0) is a headless browser
automation CLI in Rust, compatible with Ubuntu 24.04 x86_64, with a persistent daemon
and AES-256-GCM encryption of session state.

**Compatibility with elis-server:**

| Requirement | elis-server | agent-browser | Status |
|---|---|---|---|
| OS | Ubuntu 24.04.4 LTS | Linux x64 native | ✓ |
| Architecture | x86_64 | `agent-browser-linux-x64` | ✓ |
| Chrome | Not installed | `agent-browser install --with-deps` | ✓ |
| Display | Headless | Headless daemon by default | ✓ |
| Systemd | Active | `AGENT_BROWSER_IDLE_TIMEOUT_MS` | ✓ |
| Session encryption | `§13` requires | AES-256-GCM via env var | ✓ |
| Memory | 16 GB total | ~400 MB per Chrome instance | Monitor |

**Operational limitation:** `maxConcurrent: 1` for agents with `agent-browser` — avoid
parallel Chrome instances on the NUC8i7BEH.

**Scope of this PE:**

- Install `agent-browser` on `elis-server` as a tool available in harvest workspaces
- Configure session encryption (`AGENT_BROWSER_ENCRYPTION_KEY` in `.openclaw/.env`)
- Adapt the harvest pipeline to consume `agent-browser` output via JSONL
- Document the initial login procedure for each source (auth vault)

---

## Phase E — Documentary Governance

> **Objective:** Fill the gap identified in the assessment of 2026-03-25: the current model
> covers "what changed" (git) and "what went wrong" (LESSONS_LEARNED.md) well, but does not
> systematically capture the "why behind architectural decisions". Phase E implements the
> hybrid 3-layer model for recording the evolution of the solution.
>
> **Can run in parallel with any other phase** — has no runtime dependencies.

---

### 3-Layer History Model

```
┌─────────────────────────────────────────────────────────┐
│  LAYER 1 — "Architectural why"                          │
│  docs/decisions/ADR-NNN-*.md                            │
│  • One decision per file                                │
│  • Reviewed in PR — same governance as code             │
│  • Status: Proposed → Accepted → Superseded            │
│  • Searchable by topic, not by date                     │
├─────────────────────────────────────────────────────────┤
│  LAYER 2 — "What went wrong / what was learnt"          │
│  LESSONS_LEARNED.md (already exists — maintain and expand) │
│  • Error patterns + corrective rules                    │
│  • Positive insights (e.g. parallel tracks discovery)  │
├─────────────────────────────────────────────────────────┤
│  LAYER 3 — "What happened operationally"                │
│  PM Agent Journal (OpenClaw, elis-server)               │
│  • Log of session events, arbitrations, Discord cmds    │
│  • Not the primary source of architectural decisions    │
│  • Relevant decisions are distilled into ADR or LL      │
└─────────────────────────────────────────────────────────┘
```

**Why ADRs and not the Journal as the primary source:**

| Criterion | ADR (`docs/decisions/`) | Journal (OpenClaw) |
|---|---|---|
| Git-tracked | ✓ | ✗ by default |
| PR-reviewable | ✓ | ✗ |
| Searchable by topic | ✓ — 1 file/decision | ✗ — chronological |
| Evidence-first (§2.4) | ✓ — reviewed with code | ✗ |
| Survives reinstallation | ✓ | ✗ |
| Open-source standard | ✓ — AWS, Netflix, Google | ✗ |
| Captures discarded alternatives | ✓ — explicit field | Partial |

---

### ADR Template

Location: `docs/decisions/ADR-NNN-title-kebab-case.md`

```markdown
# ADR-NNN: Decision Title

**Status:** Proposed | Accepted | Superseded by ADR-XXX | Deprecated
**Date:** YYYY-MM-DD
**Authors:** <agents and PM involved>

## Context

The problem or situation that motivated the decision. Facts, not opinions.

## Decision

What was decided, in affirmative form. One decision per ADR.

## Consequences

### Positive
- ...

### Negative / trade-offs
- ...

### Neutral
- ...

## Discarded Alternatives

| Alternative | Reason for discarding |
|---|---|
| ... | ... |

## Evidence

References to PRs, commits, or plan sections that underpin the decision.
```

---

### When to Create an ADR

A new ADR must be created when:

1. **An architectural decision is made** that will affect multiple PEs or agents
2. **A significant alternative was assessed and discarded** (e.g. symlinks, agent-browser for auth)
3. **An empirically observed pattern is adopted as practice** (e.g. parallel tracks)
4. **A rule is added to AGENTS.md** for an architectural reason (not merely due to an error)
5. **A PE is redesigned** or a phase is restructured with future impact

An ADR **is not required** for:
- Minor bug fixes
- Purely operational changes (runbooks, utility scripts)
- Local implementation decisions within a single PE
- Validation findings (these go in REVIEW_PE or LESSONS_LEARNED)

---

### PE-PLAN-01 · Architecture Decision Records — Infrastructure and First Batch

| Field | Value |
|---|---|
| Domain | infra |
| Depends On | — (can start at any time) |
| Implementer | `infra-impl-claude` |
| Validator | `infra-val-codex` |
| parallel_eligible | true |

**Deliverables:**

- `docs/decisions/README.md` — ADR system guide: template, creation rules, status lifecycle, numbering convention
- `docs/decisions/ADR-001-two-agent-alternation-model.md`
- `docs/decisions/ADR-002-git-worktrees-pe-isolation.md`
- `docs/decisions/ADR-003-parallel-track-model.md`
- `docs/decisions/ADR-004-handoff-copy-not-symlink.md`
- `docs/decisions/ADR-005-agent-browser-rejected-for-auth.md`
- `docs/decisions/ADR-006-openclaw-as-native-runtime.md`
- Extension of `AGENTS.md` — rule §X: when to create an ADR (based on the rules above)

**First batch — expected content of each ADR:**

| ADR | Core decision | Discarded alternative |
|---|---|---|
| ADR-001 | Implementer/Validator alternation per PE; no fixed roles | Fixed roles per agent; single-agent review |
| ADR-002 | Git worktrees for isolation; one worktree per active PE | Branch switching with stash; temporary directories |
| ADR-003 | Parallel tracks when PEs are independent; maximum 2 | Always sequential; round-robin with >2 agents |
| ADR-004 | HANDOFF as script-generated copy, not symlink | Symlink `HANDOFF.md → handoffs/HANDOFF_{PE}.md` |
| ADR-005 | agent-browser for SLR web harvest, not for auth | Browser cookies as API key substitute |
| ADR-006 | OpenClaw as native orchestration runtime | Docker compose; direct API calls without runtime |

**Acceptance Criteria:**

| # | Criterion |
|---|---|
| AC-1 | `docs/decisions/README.md` present with template, lifecycle, and creation rules |
| AC-2 | 6 ADRs from the first batch present, with status `Accepted` and all fields completed |
| AC-3 | Each ADR has at least one discarded alternative documented |
| AC-4 | `AGENTS.md` updated with rule for when to create an ADR |
| AC-5 | ADR-003 (parallel tracks) references the empirical case PE-MS-07 ∥ PR #299 |
| AC-6 | ADR-004 (HANDOFF copy) references finding F4 from PR #299 as evidence |

---

## Session Continuity Model

> Full reference: `docs/_active/TWO_AGENT_SESSION_CONTINUITY_RUNBOOK.md`

### Problem

In long sessions, the chat context may be compacted whilst a PE is still in
progress. When relevant state exists only in session memory:

- implementation context is lost mid-PE
- validator state drifts between review rounds
- PM cannot infer real progress from the chat
- restarted sessions may repeat work or miss completed checkpoints

The correct solution is not to avoid compaction. It is to make each PE operationally resumable
from durable artefacts.

### Core Principle

**The PR is the operational memory.**

Chat is coordination. The PE branch and its artefacts are the source of continuity.

A fact is only safe if it exists in one of these places:

- code or docs committed on the PE branch
- `HANDOFF.md`
- `REVIEW_PE<N>.md`
- PR comments with status packets
- `CURRENT_PE.md` for role/branch/plan authority

If it exists only in chat, it is not durable.

### Mandatory Rule for Each PE

> Every active PE must be resumable without chat history. Progress is considered durable
> only when recorded in branch commits, `HANDOFF.md` / `REVIEW_PE<N>.md`, and PR
> comments. PM monitors agent activity via PR state and `CURRENT_PE.md`, not
> depending on long-running session continuity.

### 3-Layer Memory Model

| Layer | Where it lives | Content |
|---|---|---|
| Technical | `HANDOFF.md`, `REVIEW_PE<N>.md`, tests, PE docs | implementation and review state |
| Operational | PR comments with status packets | milestone reached, gate result, blocker, next actor |
| Authority | `CURRENT_PE.md` | active PE, branch, plan version, Implementer/Validator |

### Required Checkpoints by Role

**Implementer** — durable checkpoint at each milestone:

1. branch/worktree created and context read
2. first implementation commit made
3. draft PR opened
4. quality gates passing
5. `HANDOFF.md` complete
6. PR converted to ready-for-review

**Validator** — durable checkpoint at each milestone:

1. validation assignment accepted
2. scope diff verified
3. acceptance criteria exercised
4. adversarial validation complete
5. `REVIEW_PE<N>.md` committed
6. PASS or FAIL posted on the PR

### Session Rules

- Prefer short sessions with a closed objective; avoid "continue until the PE is ready"
- Commit before any pause — clean tree is mandatory, not optional
- PR comment after each significant milestone (gates green, HANDOFF updated, FAIL posted, etc.)

### Anti-Patterns

- Relying on chat history as the sole activity log
- Leaving the tree dirty at the end of a session
- Deferring `HANDOFF.md` or `REVIEW_PE<N>.md` until the end of work
- Making multiple large changes before the first checkpoint commit
- Posting only a single final PR comment after hours of work
- Assuming PM can reconstruct progress from memory rather than artefacts

---

## Roadmap and Dependencies

### Sequential Phase Diagram

```
Phase 0 (auth)           Phase A (foundation)    Phase B (loop)           Phase C/D (arbiter+full)
━━━━━━━━━━━━━━━━━━━━━━  ━━━━━━━━━━━━━━━━━━━━━━  ━━━━━━━━━━━━━━━━━━━━━━  ━━━━━━━━━━━━━━━━━━━━━━━
PE-AUTH-01 Codex OAuth  PE-AUTO-01 Bot accounts  PE-AUTO-04 Impl runner  PE-AUTO-07 Arbitration
PE-AUTH-02 Claude token PE-AUTO-02 CurrentPE CI  PE-AUTO-05 Val runner   PE-AUTO-08 Discord loop
(parallel ◀)            PE-AUTO-03 pre-commit     PE-AUTO-06 Sequencer   PE-AUTO-09 Plan loader
                                                                          PE-AUTO-10 Dashboard
                                                                          PE-AUTO-11 Parallel ◀
[ pre-verification ]    [ requires Phase 0 ]      [ requires Phase A ]   [ requires Phase B ]

Phase E (documentary governance) — parallel to any phase above:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PE-PLAN-01 ADR infra    ◀ no runtime dependencies; can start now
```

### Parallel Track Diagram (v3.0)

Shows how track parallelism operates **within each phase**:

```
Time →──────────────────────────────────────────────────────────────────────>

PHASE 0 (example with PE-AUTH-01 ∥ PE-AUTH-02 — eligible by structural criteria; empirical case is PE-MS-07 ∥ PR #299):

Track A │[PE-AUTH-01: impl-claude]──────[val-codex]──[merge]│
Track B │  [PE-AUTH-02: impl-codex]────────────[val-claude]──[merge]│

         ◀──────── ~3–5 days, both in parallel ────────▶

PHASE A (PE-AUTO-02 ∥ PE-AUTO-03 — independent, may be parallel):

Track A │[PE-AUTO-01: impl-codex]──[val-claude]──[merge]│
Track B │                               [PE-AUTO-02: impl-claude]──[val-codex]──[merge]│
Track A │                                                       [PE-AUTO-03: impl-codex]──...│

         ◀─── PE-AUTO-01 first (depends on Phase 0) ───▶◀── parallel after ──▶

PHASE D (PE-AUTO-11 extends sequencer for automatic dispatch):

Track A │[PE-AUTO-09]──[merge]──────────[val-codex]──[merge]│
Track B │              [PE-AUTO-10]──────────────[val-claude]──[merge]│
                       ↑ parallel dispatch via PE-AUTO-11
```

### Critical Dependencies

| PE | Depends on | Reason |
|---|---|---|
| PE-AUTO-01 | PE-AUTH-01 + PE-AUTH-02 | Runners need tokens before using bots |
| PE-AUTO-04 | PE-AUTH-01/02 + PE-AUTO-01 | Engine + separate GitHub identity |
| PE-AUTO-06 | PE-AUTO-02 | Sequencer only advances after CURRENT_PE.md validation |
| PE-AUTO-11 | PE-AUTO-06 + PE-AUTO-09 | Parallel scheduler requires functional sequencer and plan loader |
| PE-AUTH-02 Context B | Manual pre-verification | Result determines whether ANTHROPIC_API_KEY remains on elis-server |
| PE-SLR-HARVEST-WEB | PE-MS-06 | Harvest phase workspaces must exist |
| PE-PLAN-01 | none | ADR infrastructure does not depend on runtime; can start in parallel with any phase |

### Parallelism Opportunities Identified in the Current Plan

| Cohort | PEs | Eligibility criterion |
|---|---|---|
| Phase 0 | PE-AUTH-01 + PE-AUTH-02 | No mutual dependency; distinct files; opposite engines ✓ |
| Phase A (post PE-AUTO-01) | PE-AUTO-02 + PE-AUTO-03 | PE-AUTO-02 does not depend on PE-AUTO-03 and vice versa ✓ |
| Phase D | PE-AUTO-09 + PE-AUTO-10 | Dashboard does not depend directly on Plan Loader ✓ |
| Phase D | PE-AUTO-10 + PE-AUTO-11 | Parallel scheduler does not depend on dashboard ✓ |
| Phase E (any) | PE-PLAN-01 + any PE from another phase | ADRs are pure docs; no file overlap with automation code ✓ |

---

## Risks and Mitigations

| Risk | Prob. | Impact | Mitigation |
|---|---|---|---|
| Codex OAuth token expires during a long series | High | High | [TO VALIDATE in PE-AUTH-01] Mandatory manual renewal; `!pe auth-check` on-demand; quota monitoring mechanism to be determined after token validation |
| Implementer agent in commit loop | Medium | High | `MAX_COMMITS=20` and 4h timeout on runner; automatic exit 1 |
| PM Agent makes wrong arbitration decision | Medium | Medium | Every arbitration recorded in auditable PR comment; PO can review and use `!pe override` |
| GitHub rate limit from bot account usage | Low | High | Fine-grained PATs with minimum scope; `elis-pm-bot` separates merge operations from code operations |
| CURRENT_PE.md corrupted by sequencer | Low | High | `check_current_pe.py` blocks invalid state before dispatch; git history preserves state |
| Headless Chrome consumes excessive memory | Medium (harvest) | Medium | `maxConcurrent: 1` for agents with agent-browser; monitoring via PM Agent |
| OpenClaw does not support setup-token in Context B | High | Low | Documented in AC-5 of PE-AUTH-02; ANTHROPIC_API_KEY remains on elis-server with a review plan |
| File conflict between parallel tracks | Low | High | `check_parallel_eligibility.py` validates absence of overlap before dispatch; tracks with overlap are blocked and executed sequentially |
| Inconsistent state in dual-track CURRENT_PE.md | Low | High | `check_current_pe.py` validates Track A + B structure; sequencer only writes valid state; git history preserves previous state |
| Agent starts Track B before Track A closes (race condition) | Low | Medium | Sequencer controls dispatch; each track has an isolated branch — no shared state between active tracks |
| ADR created without adequate technical review | Medium | Medium | ADRs follow the same PE flow: PR opened, Validator reviews before merge |
| ADRs become outdated after architectural changes | Medium | Low | Rule in AGENTS.md: whenever a PE AC changes a documented architectural decision, create or supersede the corresponding ADR in the same PR |
| Context compaction mid-PE | High | Medium | Session Continuity Model (v3.2): incremental commits, PR comments per milestone, clean tree mandatory before pauses — see `TWO_AGENT_SESSION_CONTINUITY_RUNBOOK.md` |

---

## What Was NOT Incorporated from the ChatGPT Document

| Discarded item | Reason |
|---|---|
| `openclaw models auth login/paste-token` | Command does not exist in the real OpenClaw |
| JSON format `agents.defaults.model.primary` | Incompatible with the project's real `openclaw.json` |
| `openai-codex/gpt-5.4` / `openai/gpt-5-mini` | Model IDs not confirmed in ELIS runtime — repo uses `openai/gpt-5.1-codex` |
| `"context1m": false` | Fictitious Anthropic API parameter |
| `agent-browser` as API key substitute | Technically incompatible — browser cookies ≠ API keys |

---

*ELIS 2-Agent Automation Plan v3.2 · 2026-03-25*
