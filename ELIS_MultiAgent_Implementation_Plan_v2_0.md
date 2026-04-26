# ELIS Multi-Agent Implementation Plan v2.0
## Agent Operational Readiness Review

**Version:** 2.0  
**Supersedes:** ELIS_MultiAgent_Implementation_Plan_v1_9.md  
**Date:** 2026-04-26  
**Status:** Active

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

---

## 3. PE Catalogue

### Phase 1 — PM Agent

#### PE-AGT-01 · PM Agent Configuration and Dispatch Review

|| Field | Value |
||-------|-------|
|| Domain | infra |
|| Implementer | `infra-impl-a` |
|| Validator | `infra-val-b` |
|| Agent under review | `pm` |
|| Depends On | — |
|| Status | Planned |

**Scope**

Verify the `pm` agent is correctly declared in openclaw, has dispatch authority over all other agents, and its pm_dispatch_settings.json reflects the current agent roster.

---

### Phase 2 — SLR Pipeline Agents

#### PE-AGT-02 · harvest-impl-a Agent Review

|| Field | Value |
||-------|-------|
|| Domain | slr |
|| Implementer | `infra-impl-b` |
|| Validator | `infra-val-a` |
|| Agent under review | `harvest-impl-a` |
|| Depends On | PE-AGT-01 |
|| Status | Planned |

**Scope**

Verify `harvest-impl-a` is declared in openclaw, runs on the correct execution surface, has access to harvest scripts, and passes the harvest contract smoke test.

---

#### PE-AGT-03 · harvest-val-b Agent Review

|| Field | Value |
||-------|-------|
|| Domain | slr |
|| Implementer | `infra-impl-a` |
|| Validator | `infra-val-b` |
|| Agent under review | `harvest-val-b` |
|| Depends On | PE-AGT-02 |
|| Status | Planned |

**Scope**

Verify `harvest-val-b` is declared in openclaw, holds the correct validator identity, and can access harvest review artefacts.

---

#### PE-AGT-04 · screen-impl-b Agent Review

|| Field | Value |
||-------|-------|
|| Domain | slr |
|| Implementer | `infra-impl-b` |
|| Validator | `infra-val-a` |
|| Agent under review | `screen-impl-b` |
|| Depends On | PE-AGT-03 |
|| Status | Planned |

**Scope**

Verify `screen-impl-b` is declared in openclaw, runs local-first on elis-server per the screening placement contract, and passes the screening local contract check.

---

#### PE-AGT-05 · screen-val-a Agent Review

|| Field | Value |
||-------|-------|
|| Domain | slr |
|| Implementer | `infra-impl-a` |
|| Validator | `infra-val-b` |
|| Agent under review | `screen-val-a` |
|| Depends On | PE-AGT-04 |
|| Status | Planned |

**Scope**

Verify `screen-val-a` is declared in openclaw, holds the correct validator identity, and can access screening review artefacts.

---

#### PE-AGT-06 · extract-impl-a Agent Review

|| Field | Value |
||-------|-------|
|| Domain | slr |
|| Implementer | `infra-impl-b` |
|| Validator | `infra-val-a` |
|| Agent under review | `extract-impl-a` |
|| Depends On | PE-AGT-05 |
|| Status | Planned |

**Scope**

Verify `extract-impl-a` is declared in openclaw, runs off-host per the extraction placement contract, and passes the extraction off-host contract check.

---

#### PE-AGT-07 · extract-val-b Agent Review

|| Field | Value |
||-------|-------|
|| Domain | slr |
|| Implementer | `infra-impl-a` |
|| Validator | `infra-val-b` |
|| Agent under review | `extract-val-b` |
|| Depends On | PE-AGT-06 |
|| Status | Planned |

**Scope**

Verify `extract-val-b` is declared in openclaw, holds the correct validator identity, and can access extraction review artefacts.

---

#### PE-AGT-08 · synth-impl-b Agent Review

|| Field | Value |
||-------|-------|
|| Domain | slr |
|| Implementer | `infra-impl-b` |
|| Validator | `infra-val-a` |
|| Agent under review | `synth-impl-b` |
|| Depends On | PE-AGT-07 |
|| Status | Planned |

**Scope**

Verify `synth-impl-b` is declared in openclaw, runs off-host per the synthesis placement contract, and passes the synthesis off-host contract check.

---

#### PE-AGT-09 · synth-val-a Agent Review

|| Field | Value |
||-------|-------|
|| Domain | slr |
|| Implementer | `infra-impl-a` |
|| Validator | `infra-val-b` |
|| Agent under review | `synth-val-a` |
|| Depends On | PE-AGT-08 |
|| Status | Planned |

**Scope**

Verify `synth-val-a` is declared in openclaw, holds the correct validator identity, and can access synthesis review artefacts.

---

#### PE-AGT-10 · prisma-impl-b Agent Review

|| Field | Value |
||-------|-------|
|| Domain | slr |
|| Implementer | `infra-impl-b` |
|| Validator | `infra-val-a` |
|| Agent under review | `prisma-impl-b` |
|| Depends On | PE-AGT-09 |
|| Status | Planned |

**Scope**

Verify `prisma-impl-b` is declared in openclaw, has access to PRISMA flow tooling, and passes a PRISMA configuration smoke test.

---

#### PE-AGT-11 · prisma-val-a Agent Review

|| Field | Value |
||-------|-------|
|| Domain | slr |
|| Implementer | `infra-impl-a` |
|| Validator | `infra-val-b` |
|| Agent under review | `prisma-val-a` |
|| Depends On | PE-AGT-10 |
|| Status | Planned |

**Scope**

Verify `prisma-val-a` is declared in openclaw, holds the correct validator identity, and can access PRISMA review artefacts.

---

### Phase 3 — Programme Agents

#### PE-AGT-12 · prog-impl Agent Review (slots a and b)

|| Field | Value |
||-------|-------|
|| Domain | infra |
|| Implementer | `infra-impl-b` |
|| Validator | `infra-val-a` |
|| Agents under review | `prog-impl-a`, `prog-impl-b` |
|| Depends On | PE-AGT-11 |
|| Status | Planned |

**Scope**

Verify both `prog-impl-a` (CODEX) and `prog-impl-b` (Claude Code) are declared in openclaw, have correct GitHub bot identities (`elis-codex-bot`, `elis-claude-bot`), run local-first on elis-server, and the implementer runner workflow references them correctly.

---

#### PE-AGT-13 · prog-val Agent Review (slots a and b)

|| Field | Value |
||-------|-------|
|| Domain | infra |
|| Implementer | `infra-impl-a` |
|| Validator | `infra-val-b` |
|| Agents under review | `prog-val-a`, `prog-val-b` |
|| Depends On | PE-AGT-12 |
|| Status | Planned |

**Scope**

Verify both `prog-val-a` (CODEX) and `prog-val-b` (Claude Code) are declared in openclaw, have correct GitHub bot identities, have PR review permissions on protected branches, and the validator runner workflow references them correctly.

---

### Phase 4 — Infrastructure Agents

#### PE-AGT-14 · infra-impl Agent Review (slots a and b)

|| Field | Value |
||-------|-------|
|| Domain | infra |
|| Implementer | `infra-impl-b` |
|| Validator | `infra-val-a` |
|| Agents under review | `infra-impl-a`, `infra-impl-b` |
|| Depends On | PE-AGT-13 |
|| Status | Planned |

**Scope**

Verify both `infra-impl-a` and `infra-impl-b` are declared in openclaw, have correct GitHub identities, run local-first on elis-server, and are correctly wired in the implementer runner workflow for infrastructure PEs.

---

#### PE-AGT-15 · infra-val Agent Review (slots a and b)

|| Field | Value |
||-------|-------|
|| Domain | infra |
|| Implementer | `infra-impl-a` |
|| Validator | `infra-val-b` |
|| Agents under review | `infra-val-a`, `infra-val-b` |
|| Depends On | PE-AGT-14 |
|| Status | Planned |

**Scope**

Verify both `infra-val-a` and `infra-val-b` are declared in openclaw, have PR review permissions on protected branches, and are correctly wired in the validator runner workflow for infrastructure PEs.

---

## 4. Build Schedule

| Phase | PE | Agent(s) reviewed | Implementer |
|-------|----|-------------------|-------------|
| 1 | PE-AGT-01 | pm | `infra-impl-a` |
| 2 | PE-AGT-02 | harvest-impl-a | `infra-impl-b` |
| 2 | PE-AGT-03 | harvest-val-b | `infra-impl-a` |
| 2 | PE-AGT-04 | screen-impl-b | `infra-impl-b` |
| 2 | PE-AGT-05 | screen-val-a | `infra-impl-a` |
| 2 | PE-AGT-06 | extract-impl-a | `infra-impl-b` |
| 2 | PE-AGT-07 | extract-val-b | `infra-impl-a` |
| 2 | PE-AGT-08 | synth-impl-b | `infra-impl-b` |
| 2 | PE-AGT-09 | synth-val-a | `infra-impl-a` |
| 2 | PE-AGT-10 | prisma-impl-b | `infra-impl-b` |
| 2 | PE-AGT-11 | prisma-val-a | `infra-impl-a` |
| 3 | PE-AGT-12 | prog-impl-a, prog-impl-b | `infra-impl-b` |
| 3 | PE-AGT-13 | prog-val-a, prog-val-b | `infra-impl-a` |
| 4 | PE-AGT-14 | infra-impl-a, infra-impl-b | `infra-impl-b` |
| 4 | PE-AGT-15 | infra-val-a, infra-val-b | `infra-impl-a` |

---

## 5. Success Criteria for the Plan

The plan is complete when:

1. All 19 openclaw-registered agents have a PASS review in `docs/reviews/archive/`.
2. Every agent's openclaw declaration, execution surface, and GitHub identity are confirmed correct.
3. No agent review reveals an unresolved configuration gap.
4. `check_openclaw_config_sync.py` passes against the live container after all reviews.

---

**End of Implementation Plan v2.0**
