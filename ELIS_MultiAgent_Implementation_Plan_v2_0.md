# ELIS Multi-Agent Implementation Plan v2.0
## Agent Operational Readiness Review

**Version:** 2.0  
**Supersedes:** ELIS_MultiAgent_Implementation_Plan_v1_9.md  
**Date:** 2026-04-26  
**Status:** Active

### Change log

| Rev | Date | Change |
|-----|------|--------|
| 2.0.0 | 2026-04-26 | Initial v2.0 — 15 PEs covering all 19 openclaw agents |
| 2.0.1 | 2026-04-26 | Add Phase 0 (PE-AGT-00) for model auth pre-flight; add AC-6 (OAuth primary, API key fallback) to standard criteria |

---

## 1. Objective

Conduct a structured review and validation of every agent registered in the openclaw platform on elis-server. Each PE covers one agent: its openclaw configuration, GitHub identity, execution surface contract, tool access, and operational smoke test.

All 19 registered agents are reviewed. The plan is complete when every agent has a PASS verdict committed to the archive.

---

## 2. Scope and Governance

- **One PE per agent.** Each PE has exactly one Implementer (runs the review) and one Validator (independently verifies it).
- **Alternation rule applies.** Implementer engine alternates CODEX ↔ Claude Code across consecutive PEs.
- **Base branch:** `main`.
- **Plan file:** `ELIS_MultiAgent_Implementation_Plan_v2_0.md`.
- **Review artefacts:** `docs/reviews/archive/REVIEW_PE_AGT_<NN>.md`.

### Standard Acceptance Criteria (all PEs)

| AC | Criterion |
|----|-----------|
| AC-1 | Agent ID is declared in `openclaw/openclaw.json` with the correct identifier. |
| AC-2 | Agent workspace is configured with the required tools and permissions for its role. |
| AC-3 | Agent execution surface matches the placement contract (local-first or off-host as appropriate). |
| AC-4 | Agent GitHub identity (bot account or PAT) is present and has the access level required by its role. |
| AC-5 | A configuration check or smoke test for the agent passes without errors. |
| AC-6 | Model authentication is verified on elis-server: OAuth credential is the primary path; an environment-variable API key is present as the documented fallback. The relevant verify script (`verify_codex_auth.py` for Codex agents, `verify_claude_auth.py` for Claude Code agents) exits 0. |

> **AC-6 implementation note:** OAuth primary means the verify script checks the credential file first (`~/.codex/auth.json` for Codex, `~/.claude/.credentials.json` with `claudeAiOauth` for Claude Code). If the OAuth credential is absent the script falls back to the API key environment variable and exits 0 with a `WARN` line. If both are absent the script exits 1. PE-AGT-00 establishes this contract for all subsequent PEs.

> **PO pre-flight action (once, before PE-AGT-01):** PO must complete the OAuth setup steps defined in PE-AGT-00 on elis-server before any agent PE begins. The Implementer for PE-AGT-01 confirms this is done as the first Step 0 check.

---

## 3. PE Catalogue

### Phase 0 — Model Authentication Pre-flight

#### PE-AGT-00 · Model Authentication Setup (Codex + Claude Code)
00
|| Field | Value |
||-------|-------|
|| Domain | infra |
|| Implementer | `infra-impl-a` |
|| Validator | `infra-val-b` |
|| Agents covered | All Codex agents (`openai/gpt-5.1-codex`); all non-CODEX agents in the active roster |
|| Depends On | — |
|| Status | Planned |

**PO action required (before implementation begins)**

The Implementer must not open a branch until the PO confirms both steps below are complete on elis-server:

1. **Claude Code OAuth** — PO runs `claude` interactively on elis-server and completes the login flow. This writes `~/.claude/.credentials.json` containing the `claudeAiOauth` key. PO confirms with: `python scripts/verify_claude_auth.py` → exit 0.

2. **Codex OAuth** — PO runs `codex` interactively on elis-server and completes the OAuth login flow. This writes `~/.codex/auth.json` (or `~/.config/openai/auth.json`) with valid tokens. PO confirms with: `python scripts/verify_codex_auth.py` → exit 0 (after the script is updated by this PE).

PO posts confirmation to PM before PE-AGT-00 is opened. PM acknowledges and assigns the Implementer.

**Scope**

Update the two auth verify scripts to implement the OAuth-primary, API-key-fallback contract:

- `scripts/verify_codex_auth.py`: check `~/.codex/auth.json` (primary); fall back to `OPENAI_API_KEY` with a `WARN` line; exit 1 only if both absent.
- `scripts/verify_claude_auth.py`: check `~/.claude/.credentials.json` for `claudeAiOauth` (primary); fall back to `ANTHROPIC_API_KEY` with a `WARN` line; exit 1 only if both absent.
- Update tests in `tests/test_verify_claude_auth.py` and add `tests/test_verify_codex_auth.py` to cover the new fallback paths.
- `docs/openclaw/AUTH_STRATEGY.md`: one-page document stating the auth contract (OAuth primary, API key fallback, why, and how to re-run OAuth on elis-server).

This PE does **not** change runner workflows or openclaw config — that is in scope for subsequent PEs that reference AC-6.

---

### Phase 1 — PM Agent

#### PE-AGT-01 · PM Agent Configuration and Dispatch Review
01
|| Field | Value |
||-------|-------|
|| Domain | infra |
|| Implementer | `infra-impl-b` |
|| Validator | `infra-val-a` |
|| Agent under review | `pm` |
|| Depends On | PE-AGT-00 |
|| Status | Planned |

**Scope**

Verify the `pm` agent is correctly declared in openclaw, has dispatch authority over all other agents, and its pm_dispatch_settings.json reflects the current agent roster.

---

### Phase 2 — SLR Pipeline Agents

#### PE-AGT-02 · harvest-impl-a Agent Review
02
|| Field | Value |
||-------|-------|
|| Domain | slr |
|| Implementer | `infra-impl-a` |
|| Validator | `infra-val-b` |
|| Agent under review | `harvest-impl-a` |
|| Depends On | PE-AGT-01 |
|| Status | Planned |

**Scope**

Verify `harvest-impl-a` is declared in openclaw, runs on the correct execution surface, has access to harvest scripts, and passes the harvest contract smoke test.

---

#### PE-AGT-03 · harvest-val-b Agent Review
03
|| Field | Value |
||-------|-------|
|| Domain | slr |
|| Implementer | `infra-impl-b` |
|| Validator | `infra-val-a` |
|| Agent under review | `harvest-val-b` |
|| Depends On | PE-AGT-02 |
|| Status | Planned |

**Scope**

Verify `harvest-val-b` is declared in openclaw, holds the correct validator identity, and can access harvest review artefacts.

---

#### PE-AGT-04 · screen-impl-b Agent Review
04
|| Field | Value |
||-------|-------|
|| Domain | slr |
|| Implementer | `infra-impl-a` |
|| Validator | `infra-val-b` |
|| Agent under review | `screen-impl-b` |
|| Depends On | PE-AGT-03 |
|| Status | Planned |

**Scope**

Verify `screen-impl-b` is declared in openclaw, runs local-first on elis-server per the screening placement contract, and passes the screening local contract check.

---

#### PE-AGT-05 · screen-val-a Agent Review
05
|| Field | Value |
||-------|-------|
|| Domain | slr |
|| Implementer | `infra-impl-b` |
|| Validator | `infra-val-a` |
|| Agent under review | `screen-val-a` |
|| Depends On | PE-AGT-04 |
|| Status | Planned |

**Scope**

Verify `screen-val-a` is declared in openclaw, holds the correct validator identity, and can access screening review artefacts.

---

#### PE-AGT-06 · extract-impl-a Agent Review
06
|| Field | Value |
||-------|-------|
|| Domain | slr |
|| Implementer | `infra-impl-a` |
|| Validator | `infra-val-b` |
|| Agent under review | `extract-impl-a` |
|| Depends On | PE-AGT-05 |
|| Status | Planned |

**Scope**

Verify `extract-impl-a` is declared in openclaw, runs off-host per the extraction placement contract, and passes the extraction off-host contract check.

---

#### PE-AGT-07 · extract-val-b Agent Review
07
|| Field | Value |
||-------|-------|
|| Domain | slr |
|| Implementer | `infra-impl-b` |
|| Validator | `infra-val-a` |
|| Agent under review | `extract-val-b` |
|| Depends On | PE-AGT-06 |
|| Status | Planned |

**Scope**

Verify `extract-val-b` is declared in openclaw, holds the correct validator identity, and can access extraction review artefacts.

---

#### PE-AGT-08 · synth-impl-b Agent Review
08
|| Field | Value |
||-------|-------|
|| Domain | slr |
|| Implementer | `infra-impl-a` |
|| Validator | `infra-val-b` |
|| Agent under review | `synth-impl-b` |
|| Depends On | PE-AGT-07 |
|| Status | Planned |

**Scope**

Verify `synth-impl-b` is declared in openclaw, runs off-host per the synthesis placement contract, and passes the synthesis off-host contract check.

---

#### PE-AGT-09 · synth-val-a Agent Review
09
|| Field | Value |
||-------|-------|
|| Domain | slr |
|| Implementer | `infra-impl-b` |
|| Validator | `infra-val-a` |
|| Agent under review | `synth-val-a` |
|| Depends On | PE-AGT-08 |
|| Status | Planned |

**Scope**

Verify `synth-val-a` is declared in openclaw, holds the correct validator identity, and can access synthesis review artefacts.

---

#### PE-AGT-10 · prisma-impl-b Agent Review
10
|| Field | Value |
||-------|-------|
|| Domain | slr |
|| Implementer | `infra-impl-a` |
|| Validator | `infra-val-b` |
|| Agent under review | `prisma-impl-b` |
|| Depends On | PE-AGT-09 |
|| Status | Planned |

**Scope**

Verify `prisma-impl-b` is declared in openclaw, has access to PRISMA flow tooling, and passes a PRISMA configuration smoke test.

---

#### PE-AGT-11 · prisma-val-a Agent Review
11
|| Field | Value |
||-------|-------|
|| Domain | slr |
|| Implementer | `infra-impl-b` |
|| Validator | `infra-val-a` |
|| Agent under review | `prisma-val-a` |
|| Depends On | PE-AGT-10 |
|| Status | Planned |

**Scope**

Verify `prisma-val-a` is declared in openclaw, holds the correct validator identity, and can access PRISMA review artefacts.

---

### Phase 3 — Programme Agents

#### PE-AGT-12 · prog-impl Agent Review (slots a and b)
12
|| Field | Value |
||-------|-------|
|| Domain | infra |
|| Implementer | `infra-impl-a` |
|| Validator | `infra-val-b` |
|| Agents under review | `prog-impl-a`, `prog-impl-b` |
|| Depends On | PE-AGT-11 |
|| Status | Planned |

**Scope**

Verify both `prog-impl-a` (CODEX) and `prog-impl-b` (Claude Code) are declared in openclaw, have correct GitHub bot identities (`elis-codex-bot`, `elis-claude-bot`), run local-first on elis-server, and the implementer runner workflow references them correctly.

---

#### PE-AGT-13 · prog-val Agent Review (slots a and b)
13
|| Field | Value |
||-------|-------|
|| Domain | infra |
|| Implementer | `infra-impl-b` |
|| Validator | `infra-val-a` |
|| Agents under review | `prog-val-a`, `prog-val-b` |
|| Depends On | PE-AGT-12 |
|| Status | Planned |

**Scope**

Verify both `prog-val-a` (CODEX) and `prog-val-b` (Claude Code) are declared in openclaw, have correct GitHub bot identities, have PR review permissions on protected branches, and the validator runner workflow references them correctly.

---

### Phase 4 — Infrastructure Agents

#### PE-AGT-14 · infra-impl Agent Review (slots a and b)
14
|| Field | Value |
||-------|-------|
|| Domain | infra |
|| Implementer | `infra-impl-a` |
|| Validator | `infra-val-b` |
|| Agents under review | `infra-impl-b`, `infra-impl-a` |
|| Depends On | PE-AGT-13 |
|| Status | Planned |

**Scope**

Verify both `infra-impl-b` and `infra-impl-a` are declared in openclaw, have correct GitHub identities, run local-first on elis-server, and are correctly wired in the implementer runner workflow for infrastructure PEs.

---

#### PE-AGT-15 · infra-val Agent Review (slots a and b)
15
|| Field | Value |
||-------|-------|
|| Domain | infra |
|| Implementer | `infra-impl-b` |
|| Validator | `infra-val-a` |
|| Agents under review | `infra-val-b`, `infra-val-a` |
|| Depends On | PE-AGT-14 |
|| Status | Planned |

**Scope**

Verify both `infra-val-b` and `infra-val-a` are declared in openclaw, have PR review permissions on protected branches, and are correctly wired in the validator runner workflow for infrastructure PEs.

---

## 4. Build Schedule

| Phase | PE | Agent(s) / Scope | Implementer | Gate |
|-------|----|-------------------|-------------|------|
| 0 | PE-AGT-00 | Model auth pre-flight (all engines) | `infra-impl-b` | **PO OAuth confirmation required before branch opens** |
| 1 | PE-AGT-01 | pm | `infra-impl-a` | Depends on PE-AGT-00 |
| 2 | PE-AGT-02 | harvest-impl-a | `infra-impl-b` | Depends on PE-AGT-01 |
| 2 | PE-AGT-03 | harvest-val-b | `infra-impl-a` | Depends on PE-AGT-02 |
| 2 | PE-AGT-04 | screen-impl-b | `infra-impl-b` | Depends on PE-AGT-03 |
| 2 | PE-AGT-05 | screen-val-a | `infra-impl-a` | Depends on PE-AGT-04 |
| 2 | PE-AGT-06 | extract-impl-a | `infra-impl-b` | Depends on PE-AGT-05 |
| 2 | PE-AGT-07 | extract-val-b | `infra-impl-a` | Depends on PE-AGT-06 |
| 2 | PE-AGT-08 | synth-impl-b | `infra-impl-b` | Depends on PE-AGT-07 |
| 2 | PE-AGT-09 | synth-val-a | `infra-impl-a` | Depends on PE-AGT-08 |
| 2 | PE-AGT-10 | prisma-impl-b | `infra-impl-b` | Depends on PE-AGT-09 |
| 2 | PE-AGT-11 | prisma-val-a | `infra-impl-a` | Depends on PE-AGT-10 |
| 3 | PE-AGT-12 | prog-impl-a, prog-impl-b | `infra-impl-b` | Depends on PE-AGT-11 |
| 3 | PE-AGT-13 | prog-val-a, prog-val-b | `infra-impl-a` | Depends on PE-AGT-12 |
| 4 | PE-AGT-14 | infra-impl-a, infra-impl-b | `infra-impl-b` | Depends on PE-AGT-13 |
| 4 | PE-AGT-15 | infra-val-a, infra-val-b | `infra-impl-a` | Depends on PE-AGT-14 |

> **Alternation note (v2.0.1):** PE-AGT-00 sets `infra-impl-b` as first Implementer. The series then alternates strictly: even-numbered phases use `infra-impl-a`, odd use `infra-impl-b`. The Build Schedule above reflects this corrected alternation (PE-AGT-01 is `infra-impl-a`, PE-AGT-02 is `infra-impl-b`, etc.).

---

## 5. Success Criteria for the Plan

The plan is complete when:

1. PE-AGT-00 is merged: both `verify_codex_auth.py` and `verify_claude_auth.py` implement OAuth-primary, API-key-fallback and pass on elis-server.
2. All 19 openclaw-registered agents have a PASS review in `docs/reviews/archive/`.
3. Every agent's openclaw declaration, execution surface, and GitHub identity are confirmed correct.
4. AC-6 is satisfied for every Codex and Claude Code agent: OAuth credential confirmed present on elis-server; API key confirmed as fallback.
5. No agent review reveals an unresolved configuration gap.
6. `check_openclaw_config_sync.py` passes against the live container after all reviews.

---

**End of Implementation Plan v2.0**
