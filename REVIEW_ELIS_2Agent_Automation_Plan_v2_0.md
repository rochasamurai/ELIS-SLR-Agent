# Review — ELIS_2Agent_Automation_Plan_v2_0.md

**Date:** 2026-03-25  
**Reviewer:** CODEX

## Verdict

FAIL

## Findings

### 1. Blocking — `openai/gpt-5-mini` is incorrectly classified as nonexistent

The document states that `openai/gpt-5-mini` is a nonexistent model ID in the authentication/model analysis section and repeats that conclusion later in the exclusions section.

References:
- `ELIS_2Agent_Automation_Plan_v2_0.md:77`
- `ELIS_2Agent_Automation_Plan_v2_0.md:78`
- `ELIS_2Agent_Automation_Plan_v2_0.md:892`

Why this blocks:
- The plan uses this premise to discard an operational option that the project has already treated as valid in runtime practice.
- That makes the model/auth section technically inconsistent and likely to mislead future implementation work.

Recommended fix:
- Re-verify the supported OpenAI model IDs and correct the analysis.
- Separate "invalid IDs observed" from "valid fallback IDs currently used by ELIS."

### 2. Blocking — Fase 0 depends on speculative token portability for `codex auth login`

The plan treats offline extraction and reuse of a token from `codex auth login` as the production mechanism for headless runners, but the document does not establish that the token is portable, supported for this use, or stable outside the machine that performed the login.

References:
- `ELIS_2Agent_Automation_Plan_v2_0.md:140`
- `ELIS_2Agent_Automation_Plan_v2_0.md:141`
- `ELIS_2Agent_Automation_Plan_v2_0.md:142`
- `ELIS_2Agent_Automation_Plan_v2_0.md:159`
- `ELIS_2Agent_Automation_Plan_v2_0.md:166`

Why this blocks:
- Fase 0 is defined as a prerequisite for later automation phases.
- If the auth mechanism is not actually supported, the entire dependency chain becomes unstable.

Recommended fix:
- Reframe this as a validation PE first, not as an assumed foundation.
- Require explicit proof that the token mechanism is supported and portable before making it a dependency for later phases.

### 3. Blocking — autonomous merge/PM loop conflicts with the current governance model

The executive summary and later phases describe a future state where the PM Agent closes the merge loop without human intervention. That conflicts with the currently enforced governance model, where `CURRENT_PE.md` and the active workflow still preserve human PM authority and explicit control points.

References:
- `ELIS_2Agent_Automation_Plan_v2_0.md:21`
- `ELIS_2Agent_Automation_Plan_v2_0.md:26`
- `ELIS_2Agent_Automation_Plan_v2_0.md:27`
- `ELIS_2Agent_Automation_Plan_v2_0.md:441`
- `ELIS_2Agent_Automation_Plan_v2_0.md:444`
- `ELIS_2Agent_Automation_Plan_v2_0.md:578`
- `ELIS_2Agent_Automation_Plan_v2_0.md:588`
- `ELIS_2Agent_Automation_Plan_v2_0.md:606`

Why this blocks:
- As written, the document reads partly as a normative operating contract, not just a future-state proposal.
- That creates ambiguity against `AGENTS.md` and the currently validated PE workflow.

Recommended fix:
- Label these sections explicitly as target-state automation, not current governance.
- Add a transition rule stating that `AGENTS.md` remains authoritative until each automation PE is merged and adopted.

### 4. Medium — `HANDOFF.md` symlink strategy is fragile across Windows and Linux workflows

The proposal to make root `HANDOFF.md` a symlink to a namespaced file adds filesystem-specific behavior into a repo that is actively used from Windows worktrees and Linux runtime environments.

References:
- `ELIS_2Agent_Automation_Plan_v2_0.md:414`
- `ELIS_2Agent_Automation_Plan_v2_0.md:422`
- `ELIS_2Agent_Automation_Plan_v2_0.md:426`

Why this matters:
- Symlink behavior is more fragile on Windows and can add avoidable tooling variance.
- The same compatibility goal can likely be achieved with explicit canonical paths and script support, without making symlinks part of the core contract.

Recommended fix:
- Prefer a canonical namespaced file layout plus script compatibility.
- Keep root `HANDOFF.md` as generated/copied compatibility output only if truly needed.

### 5. Medium — some operational claims are still hypothesis-level, not evidence-backed

The document includes operational assumptions such as quota monitoring and renewal behavior that are plausible, but not yet demonstrated in the plan with verified evidence.

References:
- `ELIS_2Agent_Automation_Plan_v2_0.md:188`
- `ELIS_2Agent_Automation_Plan_v2_0.md:190`
- `ELIS_2Agent_Automation_Plan_v2_0.md:192`
- `ELIS_2Agent_Automation_Plan_v2_0.md:876`

Why this matters:
- These are reasonable design ideas, but they should be framed as hypotheses to validate, not settled operating facts.

Recommended fix:
- Tag unverified runtime assumptions explicitly.
- Move them into validation criteria or risks until proven.

## Overall Comment

The document is well organized and the phased decomposition is strong, but it currently mixes validated facts with speculative operating assumptions in a few critical places. The main issue is not the direction of the plan; it is that the auth and autonomy foundations are written as more settled than they appear to be. Correcting those assumptions would make the plan much safer to execute.
