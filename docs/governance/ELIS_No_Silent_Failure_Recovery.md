# ELIS No Silent Failure Recovery

**Status:** Canonical — v1.0  
**Date:** 2026-05-03  
**Owner:** Carlos Rocha, Product Owner  
**Applies to:** ELIS PM, PE Watchdog, Platform Monitor  
**Authoritative sources:** ELIS_General_Guidance.md §2.3, §6.5, AGENTS.md §2.4, LESSONS_LEARNED.md LL-02, LL-13, LL-16  
**Canonical record:** GitHub (this document, PE artefacts, Status Packets)

---

## 1. Purpose

A "silent failure" occurs when an agent run produces no verifiable artefacts, omits required outputs, or reports success without evidence. The ELIS operating model treats such outcomes as failures — not successes. This document defines how to detect, report, and recover from silent failures.

> **Doctrine:** A run that produces no required artefacts (commit, HANDOFF, Status Packet, or REVIEW) is not a success. Valid outcomes are PASS, FAIL, or BLOCKED — each backed by evidence.

---

## 2. What Constitutes Silent Failure

### 2.1 Artefact Absence
| Symptom | Example | Detection Method |
|---------|---------|-----------------|
| No commit | Agent says "done" but `git log` shows no new commit | `git log --oneline origin/$BASE..HEAD` returns empty |
| No HANDOFF.md | Agent reports implementation complete but no HANDOFF exists | `ls HANDOFF.md` returns `No such file` |
| No Status Packet | Update says "everything works" with no command output | Read agent's message — no fenced code blocks with command output |
| No REVIEW file | Validator says "PASS" in chat only, no REVIEW.md | `ls REVIEW*` returns `No such file` |
| No PR review | Validator says "PASS" but no formal GitHub review | `gh pr view $PR --json reviews` shows empty |

### 2.2 Evidence Fraud (from LESSONS_LEARNED.md LL-02)
| Symptom | Example | Detection Method |
|---------|---------|-----------------|
| Fabricated test counts | "8 new tests added" with no corresponding test files | `git diff --name-status origin/$BASE..HEAD` — no test files |
| Stale HEAD SHA | HANDOFF shows a SHA that doesn't match branch tip | `git rev-parse HEAD` vs HANDOFF §6.2 |
| Claimed checks not run | "black: PASS" but no evidence of running `black --check` | No black output in Status Packet |
| AC-STATUS mismatch | AC marked as PARTIAL in final HANDOFF | Read AC table — PARTIAL is not valid for final submission |

### 2.3 Wrong-Path Success
| Symptom | Example | Detection Method |
|---------|---------|-----------------|
| Output from wrong repo | Agent reports files changed in `/opt/elis/repo` instead of worktree | Check `git rev-parse --show-toplevel` in the Status Packet |
| Cross-worktree contamination | Agent writes to another PE's worktree | `git status -sb` from correct worktree shows no changes |

---

## 3. Detection

### 3.1 PM Detection
PM monitors for silent failure by:
1. Reading every agent update for required Status Packet fields.
2. Verifying artefact existence after reported completion.
3. Cross-referencing claims against actual `git diff` and `git log` output.
4. Running `python scripts/check_current_pe.py` to verify registry integrity.
5. Checking Watchdog verdict for `MISSING_ARTEFACTS` or `STUCK`.

### 3.2 Watchdog Detection
Watchdog detects silent failure by:
1. Polling the worktree for artefact files (HANDOFF.md, REVIEW, commits).
2. Verifying Status Packet claims against actual repo state.
3. Detecting stuck runs (no changes within timeout).
4. Detecting missing PR deliverables (PR comment, formal review).

### 3.3 Validator Detection
Validator detects silent failure in implementer output by:
1. Running all checks independently — not relying on implementer's claims.
2. Verifying HANDOFF AC status matches actual implementation.
3. Checking that every claim in HANDOFF has supporting evidence.
4. Confirming that the Evidence section contains at least one fenced code block.
5. Not accepting "PARTIAL" as an AC status in a final HANDOFF.

### 3.4 Platform Monitor Detection (Hermes)
Platform Monitor detects silent failure related to platform issues:
1. Inspect OpenClaw gateway logs for provider errors.
2. Check Discord/Telegram for undelivered messages.
3. Verify repository cleanliness when operational failures occur.
4. Prepare cleanup plans for PO approval.

---

## 4. Classification

| Type | Code | Description |
|------|------|-------------|
| Artefact gap | `A1` | Required artefact (commits/HANDOFF/REVIEW) missing |
| Evidence gap | `A2` | Status Packet omits key evidence fields |
| Fabricated evidence | `A3` | Claimed artefacts or test results do not exist |
| Wrong path | `B1` | Work done in wrong repo or worktree |
| Stale path | `B2` | Session refers to old session state, not current branch state |
| Stale branch | `B3` | Branch not rebased — work targets old base |
| Platform failure | `P1` | Provider/model unreachable; gateway down; token expired |
| Rate-limit | `P2` | 429 usage-limit blocked execution |
| Partial success | `S1` | Agent reports success but ACs are only partially met |
| No delivery | `C1` | PR review or PM message not delivered |

---

## 5. Recovery Procedure

### 5.1 Read-Only Diagnosis
1. Identify the silent failure type and code.
2. Verify the agent's reported state against actual repo artefacts.
3. Collect evidence: command output, file existence checks, git logs.
4. Do not modify any files during diagnosis.

### 5.2 Report to PM
```text
Silent Failure Report
Type: <code>
Detected: <how it was found>
Agent: <agent name>
Session: <session ID>
Claims: <what the agent reported>
Actual state: <what exists (or doesn't)>
Evidence: <command output or file listing>
Impact: <what is blocked>
```

### 5.3 PM Decision
PM determines the recovery path:

| Condition | Recovery |
|-----------|----------|
| Artefacts missing (A1-A2) | PM directs agent to retry with explicit artefact requirements |
| Evidence fabricated (A3) | PM directs agent to re-run and paste actual output; may escalate to PO |
| Wrong path (B1-B2) | PM stops session; re-dispatches with correct worktree; logs to LESSONS_LEARNED.md |
| Stale branch (B3) | PM stops session; agent rebases; re-dispatches |
| Platform failure (P1) | PM tasks Platform Monitor with diagnosis and repair |
| Rate-limit (P2) | PM waits for cooldown; may split work into smaller PEs |
| Partial success (S1) | PM decides: re-scope ACs, or direct agent to complete remaining ACs |
| No delivery (C1) | PM checks Discord/PR status; may re-send |

### 5.4 PO Escalation
Escalate to PO if:
- Agent used the wrong repo/worktree (requires verification and possible rollback)
- Artefacts are missing and agent is unreachable
- Branch contamination is detected
- A workaround would weaken governance
- A cleanup action may delete useful evidence

---

## 6. Prevention

### 6.1 Agent-Level Prevention
- **Evidence-first reporting:** every claim must be backed by pasted command output (AGENTS.md §2.4).
- **Mid-session checkpoint:** before every commit, re-read CURRENT_PE.md and run scope gate (AGENTS.md §2.9).
- **Fresh session:** every implementation and validation phase uses a fresh session ID (ELIS_General_Guidance.md §6.2).
- **Task packet adherence:** only modify files listed in PE_TASK.md.
- **Status Packet completeness:** always include §6.1 through §6.5 fields.

### 6.2 PM-Level Prevention
- **Preflight checks:** run Gatekeeper before every dispatch.
- **Artefact gates:** define required artefacts before dispatch begins.
- **Watchdog monitoring:** monitor PE progress after dispatch.
- **Checkpoint review:** verify HANDOFF AC status before notifying Validator.

### 6.3 Platform-Level Prevention
- Provider preflight: verify gateway, auth, and rate limits before dispatch.
- Token management: rotate tokens in advance of expiry.
- Provider readiness logging: record readiness state at PE start.

---

## 7. Version History

| Version | Date       | Author | Changes |
|---------|------------|--------|---------|
| 1.0     | 2026-05-03 | PM     | Initial canonical consolidation from ELIS_General_Guidance.md §2.3, §6.5, AGENTS.md §2.4, LESSONS_LEARNED.md LL-02, LL-13, LL-16. |
