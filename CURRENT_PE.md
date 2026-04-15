<!-- PM-CHORE bot-authored smoke test -->
# Current PE Assignment

<!-- PM-CHORE smoke test: auto-approve verification -->

> Maintained by PM. Update ALL fields at the start of every new PE or release.
> Both agents read this file as Step 0. It is the only file that needs editing
> when switching release lines.

---

## Release context

| Field          | Value                                                          |
|----------------|----------------------------------------------------------------|
| Release        | ELIS Hybrid SLR Execution Plan · v1.8.3                        |
| Base branch    | main                                                           |
| Plan file      | ELIS_MultiAgent_Implementation_Plan_v1_8_3.md                  |
| Plan location  | repo root                                                      |

---

## Current PE

| Field   | Value                                                          |
|---------|----------------------------------------------------------------|
| PE      | PE-INFRA-SLR-03                                               |
| Branch  | feature/pe-infra-slr-03-pm-control-plane-dispatch-hardening   |

> **Active PE.** PE-INFRA-SLR-03 hardens PM control-plane dispatch so PM can reliably
> notify assigned validators directly (with auditable ACK evidence), reducing manual relay
> dependency and stabilising autonomous gate progression.

---

## Agent roles

| Agent       | Role        |
|-------------|-------------|
| Claude Code | Implementer |
| CODEX       | Validator   |

> PE-INFRA-SLR-03: `infra-impl-claude` (Claude Code) as Implementer · `infra-val-codex` (CODEX @ `elis-server`) as Validator.

---

## Active PE Registry

| PE-ID       | Domain          | Implementer-agentId  | Validator-agentId  | Branch                                            | Status          | Last-updated |
|-------------|-----------------|----------------------|--------------------|---------------------------------------------------|-----------------|--------------|
| PE-INFRA-01 | infra           | infra-impl-codex     | infra-val-claude   | feature/pe-infra-01-branch-policy                 | merged          | 2026-02-18   |
| PE-INFRA-02 | infra           | infra-impl-codex     | prog-val-claude    | feature/pe-infra-02-role-registration             | merged          | 2026-02-19   |
| PE-INFRA-03 | infra           | infra-impl-codex     | prog-val-claude    | feature/pe-infra-03-release-agnostic              | merged          | 2026-02-19   |
| PE-INFRA-04 | infra           | infra-impl-claude    | infra-val-codex    | chore/pe-infra-04-autonomous-secrets              | merged          | 2026-02-20   |
| PE-OC-01    | openclaw-infra  | infra-impl-codex     | prog-val-claude    | feature/pe-oc-01-docker-setup                     | merged          | 2026-02-20   |
| PE-OC-02    | openclaw-infra  | infra-impl-claude    | infra-val-codex    | feature/pe-oc-02-pm-agent-telegram                | merged          | 2026-02-20   |
| PE-OC-03    | openclaw-infra  | infra-impl-codex     | prog-val-claude    | feature/pe-oc-03-active-pe-registry               | merged          | 2026-02-21   |
| PE-OC-04    | openclaw-infra  | infra-impl-claude    | infra-val-codex    | feature/pe-oc-04-agent-workspaces                 | merged          | 2026-02-21   |
| PE-INFRA-06 | infra           | infra-impl-codex     | prog-val-claude    | chore/single-account-review-runbook               | merged          | 2026-02-21   |
| PE-OC-05    | openclaw-infra  | infra-impl-codex     | prog-val-claude    | feature/pe-oc-05-slr-workspaces                   | merged          | 2026-02-21   |
| PE-INFRA-07 | infra           | infra-impl-codex     | prog-val-claude    | chore/pe-infra-07-milestone-governance            | merged          | 2026-02-21   |
| PE-OC-06    | openclaw-infra  | prog-impl-claude     | prog-val-codex     | feature/pe-oc-06-pe-assignment-alternation        | merged          | 2026-02-22   |
| PE-OC-07    | openclaw-infra  | prog-impl-codex      | prog-val-claude    | feature/pe-oc-07-gate-automation                  | merged          | 2026-02-22   |
| PE-OC-08    | openclaw-infra  | prog-impl-claude     | prog-val-codex     | feature/pe-oc-08-po-status-reporting              | merged          | 2026-02-22   |
| PE-OC-09    | openclaw-infra  | prog-impl-codex      | prog-val-claude    | feature/pe-oc-09-e2e-programs                     | merged          | 2026-02-22   |
| PE-OC-10    | slr             | slr-impl-claude      | slr-val-codex      | feature/pe-oc-10-e2e-slr                          | merged          | 2026-02-22   |
| PE-OC-11    | openclaw-infra  | infra-impl-codex     | prog-val-claude    | feature/pe-oc-11-security-hardening               | merged          | 2026-02-22   |
| PE-OC-12    | openclaw-infra  | prog-impl-claude     | prog-val-codex     | feature/pe-oc-12-fix-gate1-automation             | merged          | 2026-02-22   |
| PE-OC-13    | openclaw-infra  | prog-impl-codex      | prog-val-claude    | feature/pe-oc-13-slr-quality-ci                   | merged          | 2026-02-23   |
| PE-OC-14    | openclaw-infra  | prog-impl-claude     | prog-val-codex     | feature/pe-oc-14-status-reporter-domain-grouping  | merged          | 2026-02-23   |
| PE-OC-15    | openclaw-infra  | prog-impl-codex      | prog-val-claude    | feature/pe-oc-15-openclaw-doctor-ci               | merged          | 2026-02-23   |
| PE-OC-16    | openclaw-infra  | prog-impl-claude     | prog-val-codex     | feature/pe-oc-16-lessons-learned-log              | merged          | 2026-02-23   |
| PE-OC-17    | openclaw-infra  | prog-impl-codex      | prog-val-claude    | feature/pe-oc-17-live-telegram-integration        | merged          | 2026-02-24   |
| PE-OC-18    | openclaw-infra  | prog-impl-claude     | prog-val-codex     | feature/pe-oc-18-codex-agent-registration         | merged          | 2026-02-24   |
| PE-OC-19    | openclaw-infra  | prog-impl-codex      | prog-val-claude    | feature/pe-oc-19-infra-agent-registration         | merged          | 2026-02-24   |
| PE-OC-20    | openclaw-infra  | prog-impl-claude     | prog-val-codex     | feature/pe-oc-20-config-deployment-pipeline       | merged          | 2026-02-25   |
| PE-OC-21    | openclaw-infra  | prog-impl-codex      | prog-val-claude    | feature/pe-oc-21-infra-val-workspace              | merged          | 2026-02-26   |
| PM-CHORE-01 | housekeeping    | —                    | —                  | main (direct)                                     | merged          | 2026-03-03   |
| PE-VPS-01   | vps             | prog-impl-claude     | prog-val-codex     | feature/pe-vps-01-manifest-validation-blocking    | merged          | 2026-03-06   |
| PE-VPS-02   | vps             | prog-impl-codex      | prog-val-claude    | feature/pe-vps-02-manifest-schema-extension       | merged          | 2026-03-06   |
| PE-VPS-00   | vps             | infra-impl-codex     | infra-val-claude   | feature/pe-vps-00-miniserver-baseline             | merged          | 2026-03-21   |
| PE-MS-01    | infra           | infra-impl-claude    | infra-val-codex    | feature/pe-ms-01-pm-agent-identity                | merged          | 2026-03-23   |
| PE-MS-02    | infra           | infra-impl-codex     | infra-val-claude   | feature/pe-ms-02-pm-prompt-unification            | merged          | 2026-03-23   |
| PE-MS-03    | infra           | infra-impl-claude    | infra-val-codex    | feature/pe-ms-03-pm-discord-reporting             | merged          | 2026-03-24   |
| PE-MS-04    | infra           | infra-impl-codex     | infra-val-claude   | feature/pe-ms-04-agent-registry-alignment         | merged          | 2026-03-25   |
| PE-MS-05    | infra           | infra-impl-claude    | infra-val-codex    | feature/pe-ms-05-workspace-audit                  | merged          | 2026-03-25   |
| PE-MS-06    | infra           | infra-impl-codex     | infra-val-claude   | feature/pe-ms-06-slr-phase-workspaces             | merged          | 2026-03-25   |
| PE-MS-07    | infra           | infra-impl-claude    | infra-val-codex    | feature/pe-ms-07-slr-project-store                | merged          | 2026-03-25   |
| PE-MS-08    | infra           | infra-impl-codex     | infra-val-claude   | feature/pe-ms-08-e2e-validation                   | merged          | 2026-03-26   |
| PE-PLAN-01  | infra           | infra-impl-claude    | infra-val-codex    | feature/pe-plan-01-adr-infrastructure             | merged          | 2026-03-26   |
| PE-AUTH-01  | auth            | infra-impl-claude    | infra-val-codex    | feature/pe-auth-01-codex-oauth-token              | merged          | 2026-03-26   |
| PE-AUTH-02  | auth            | infra-impl-codex     | infra-val-claude   | feature/pe-auth-02-claude-setup-token             | merged          | 2026-03-26   |
| PE-AUTO-01  | infra           | infra-impl-claude    | infra-val-codex    | feature/pe-auto-01-bot-accounts-pats              | merged          | 2026-03-28   |
| PE-AUTO-02  | infra           | infra-impl-codex     | infra-val-claude   | feature/pe-auto-02-current-pe-ci-validation       | merged          | 2026-04-01   |
| PE-AUTO-03  | infra           | infra-impl-claude    | infra-val-codex    | feature/pe-auto-03-precommit-handoff-namespacing  | merged          | 2026-04-03   |
| PE-AUTO-04  | infra           | infra-impl-codex     | infra-val-claude   | feature/pe-auto-04-impl-runner                    | merged          | 2026-04-03   |
| PE-AUTO-05  | infra           | infra-impl-claude    | infra-val-codex    | feature/pe-auto-05-validator-runner               | merged          | 2026-04-07   |
| PE-AUTO-06  | infra           | infra-impl-codex     | infra-val-claude   | feature/pe-auto-06-pe-sequencer                   | merged          | 2026-04-08   |
| PE-AUTO-07  | infra           | infra-impl-claude    | infra-val-codex    | feature/pe-auto-07-pm-agent-arbitration-protocol  | merged          | 2026-04-08   |
| PE-AUTO-08  | infra           | infra-impl-codex     | infra-val-claude   | feature/pe-auto-08-discord-loop-for-autonomous-operation | merged          | 2026-04-09   |
| PE-AUTO-09  | infra           | infra-impl-claude    | infra-val-codex    | feature/pe-auto-09-plan-loader-new-plan-ingestion        | merged          | 2026-04-10   |
| PE-AUTO-10  | infra           | infra-impl-codex     | infra-val-claude   | feature/pe-auto-10-observability-dashboard               | merged          | 2026-04-10   |
| PE-AUTO-11  | infra           | infra-impl-claude    | infra-val-codex    | feature/pe-auto-11-parallel-track-scheduler              | merged          | 2026-04-10   |
| PE-AUTO-12  | infra           | infra-impl-codex     | infra-val-claude   | feature/pe-auto-12-elis-server-bot-review-identities     | merged          | 2026-04-12   |
| PE-AUTO-13  | infra           | infra-impl-claude    | infra-val-codex    | feature/pe-auto-13-gate2-retrigger                       | superseded      | 2026-04-12   |
| PE-SLR-01   | slr             | prog-impl-codex      | gemini-cli         | feature/pe-slr-01-harvest-workflow-contract               | merged         | 2026-04-13   |
| PE-SLR-02      | slr             | prog-impl-claude     | prog-val-codex     | feature/pe-slr-02-harvest-workflow-reliability-audit           | merged        | 2026-04-14   |
| PE-INFRA-SLR-01 | infra          | infra-impl-claude    | infra-val-codex    | feature/pe-infra-slr-01-role-based-agent-surface-normalisation | merged         | 2026-04-14   |
| PE-INFRA-SLR-02 | infra          | infra-impl-codex     | infra-val-claude   | feature/pe-infra-slr-02-distinct-review-identity-enforcement   | merged         | 2026-04-15   |
| PE-INFRA-SLR-03 | infra          | infra-impl-claude    | infra-val-codex    | feature/pe-infra-slr-03-pm-control-plane-dispatch-hardening    | implementing   | 2026-04-15   |
| PE-INFRA-SLR-04 | infra          | infra-impl-codex     | infra-val-claude   | feature/pe-infra-slr-04-model-agnostic-agent-naming-governance | planning       | 2026-04-15   |

Valid status values:
- `planning`
- `implementing`
- `gate-1-pending`
- `validating`
- `gate-2-pending`
- `merged`
- `blocked`
- `superseded`

PM housekeeping entries (prefix `PM-CHORE-XX`):
- Direct commits to main by PM, no PE workflow required.
- Used for plan file replacements, CURRENT_PE.md updates, and archive operations.

| Chore ID     | Description                                                                 | Date       |
|--------------|-----------------------------------------------------------------------------|------------|
| PM-CHORE-01  | Replaced `ELIS_MultiAgent_Implementation_Plan.md` (v1.0) with v1.1 at repo root. Archived v1.0 to `docs/_archive/2026-03/ELIS_MultiAgent_Implementation_Plan_v1_0.md`. Updated `CURRENT_PE.md` to reference v1.1 and open PE-VPS-01. | 2026-03-03 |
| PM-CHORE-02  | Created `ELIS_MultiAgent_Implementation_Plan_v1_2.md` to add PE-VPS-00 (Hostinger baseline) as a prerequisite. Updated `CURRENT_PE.md` to reference v1.2 and open PE-VPS-00 with CODEX as Implementer. | 2026-03-06 |
| PM-CHORE-03  | Added `ELIS_MultiAgent_Implementation_Plan_v1_3.md` and `ELIS_SLR_AI_Platform_Conceptual_Architecture_v1_5.md` via PR #291. Updated `CURRENT_PE.md` release name to "ELIS MiniServer Implementation Series" and plan file reference to v1.3. Updated `ROADMAP.md` Phase 1 entry. | 2026-03-21 |
| PM-CHORE-04  | Aligned PE-VPS-00 metadata to plan v1.3: branch renamed from Hostinger baseline to MiniServer baseline, and agent registry roles updated to `infra-impl-codex` / `infra-val-claude` for the `elis-server` target. | 2026-03-21 |
| PM-CHORE-05  | Closed PE-VPS-00 as merged after PR #290 landed on `main`. Set the current branch context back to `main` pending PM assignment of the next MiniServer functional PE. | 2026-03-21 |
| PM-CHORE-06  | Confirmed that plan v1.3 does not yet define a post-baseline MiniServer functional PE. Kept the project on `main` and marked the next step as PM planning/update of the authoritative plan before any new PE assignment. | 2026-03-21 |
| PM-CHORE-07  | Drafted `ELIS_MultiAgent_Implementation_Plan_v1_4.md` — 7-PE MiniServer functional series (PE-MS-01 to PE-MS-07) targeting production-ready PM Agent orchestration. Updated `CURRENT_PE.md` plan file reference to v1.4 and opened PE-MS-01 with `infra-impl-claude` as Implementer and `infra-val-codex` as Validator per alternation rule. | 2026-03-22 |
| PM-CHORE-08  | Replaced `ELIS_SLR_AI_Platform_Conceptual_Architecture_v1_5.md` with `ELIS_SLR_AI_Platform_Conceptual_Architecture_v1_6.md` and `ELIS_MultiAgent_Implementation_Plan_v1_4.md` with `ELIS_MultiAgent_Implementation_Plan_v1_5.md`. Archived the superseded versions to `docs/_archive/2026-03/`. Updated `CURRENT_PE.md` plan file reference to v1.5 while keeping PE-MS-01 active. | 2026-03-22 |
| PM-CHORE-09  | Closed PE-MS-01 as merged (PR #292). Adopted `ELIS_MultiAgent_Implementation_Plan_v1_6.md` — 8-PE series adding PM stabilization phase. Archived v1.5 to `docs/_archive/2026-03/`. Updated `CURRENT_PE.md` plan file reference to v1.6 and opened PE-MS-02 with `infra-impl-codex` as Implementer and `infra-val-claude` as Validator per alternation rule. | 2026-03-23 |
| PM-CHORE-10  | Closed PE-MS-02 as merged (PR #294, PASS verdict). Opened PE-MS-03 with `infra-impl-claude` as Implementer and `infra-val-codex` as Validator per alternation rule. | 2026-03-23 |
| PM-CHORE-11  | Closed PE-MS-03 as merged (PR #295, PASS verdict). Opened PE-MS-04 with `infra-impl-codex` as Implementer and `infra-val-claude` as Validator per alternation rule. | 2026-03-24 |
| PM-CHORE-12  | Closed PE-MS-04 as merged (PR #296, PASS verdict). Opened PE-MS-05 with `infra-impl-claude` as Implementer and `infra-val-codex` as Validator per alternation rule. | 2026-03-25 |
| PM-CHORE-13  | Closed PE-MS-05 as merged (PR #297, PASS verdict). Opened PE-MS-06 with `infra-impl-codex` as Implementer and `infra-val-claude` as Validator per alternation rule. | 2026-03-25 |
| PM-CHORE-14  | Closed PE-MS-06 as merged (PR #298, PASS verdict). Opened PE-MS-07 with `infra-impl-claude` as Implementer and `infra-val-codex` as Validator per alternation rule. | 2026-03-25 |
| PM-CHORE-15  | Closed PE-MS-07 as merged (PR #300, PASS verdict). Opened PE-MS-08 with `infra-impl-codex` as Implementer and `infra-val-claude` as Validator per alternation rule. | 2026-03-25 |
| PM-CHORE-16  | Closed PE-MS-08 as merged (PR #302, PASS verdict). MiniServer Implementation Series complete (PE-MS-01 to PE-MS-08). Transitioned release to ELIS 2-Agent Automation Plan (`ELIS_2Agent_Automation_Plan_v2_0.md`). Opened PE-PLAN-01 (ADR infrastructure and first batch) with `infra-impl-claude` as Implementer and `infra-val-codex` as Validator per alternation rule. | 2026-03-26 |
| PM-CHORE-17  | Closed PE-PLAN-01 as merged (PR #303, PASS verdict). Opened Phase 0 parallel tracks: PE-AUTH-01 (Codex CLI OAuth token, `infra-impl-claude` / `infra-val-codex`, Track A) and PE-AUTH-02 (Claude Code setup-token, `infra-impl-codex` / `infra-val-claude`, Track B). Both PEs start simultaneously per parallel track model. Removed stale merged worktrees. | 2026-03-26 |
| PM-CHORE-18  | Closed PE-AUTH-01 as merged (PR #304, PASS verdict). Removed `.worktrees/pe-auth-01`. PE-AUTH-02 (Track B) continues as sole active PE — CODEX Implementer, Claude Code Validator. | 2026-03-26 |
| PM-CHORE-19  | Closed PE-AUTH-02 as merged (PR #305, PASS verdict). Removed `.worktrees/pe-auth-02`. Opened PE-AUTO-01 (Bot Accounts and GitHub Classic PATs) with `infra-impl-claude` as Implementer and `infra-val-codex` as Validator. Both PE-AUTH-01 and PE-AUTH-02 dependencies satisfied. | 2026-03-26 |
| PM-CHORE-20  | Closed PE-AUTO-01 as merged (PR #306, PASS verdict). Removed `.worktrees/pe-auto-01`. Opened PE-AUTO-02 (CURRENT_PE.md Validation in CI) with `infra-impl-codex` as Implementer and `infra-val-claude` as Validator per alternation rule. | 2026-03-28 |
| PM-CHORE-21  | Closed PE-AUTO-02 as merged (PR #309, PASS verdict — continuation of #308). Opened PE-AUTO-03 (Pre-commit Hooks + HANDOFF Namespacing) with `infra-impl-claude` as Implementer and `infra-val-codex` as Validator per alternation rule. Logged AUTO-02 backlog item: gate-1 status lost on branch update, resolved by PE-AUTO-06. | 2026-04-01 |
| PM-CHORE-22  | Closed PE-AUTO-03 as merged (PR #310, PASS verdict — 1 FAIL iteration resolved). Removed `.worktrees/pe-auto-03`. Opened PE-AUTO-04 (Implementer Agent Runner) with `infra-impl-codex` as Implementer and `infra-val-claude` as Validator per alternation rule. | 2026-04-03 |
| PM-CHORE-23  | Closed PE-AUTO-04 as merged (PR #311, PASS verdict). Opened PE-AUTO-05 (Validator Agent Runner) with `infra-impl-claude` as Implementer and `infra-val-codex` as Validator per alternation rule. | 2026-04-03 |
| PM-CHORE-24  | Closed PE-AUTO-05 as merged (PR #312, PASS verdict — CODEX Round 16). Upgraded `elis-codex-bot` and `elis-claude-bot` to write collaborator access so bot reviews satisfy branch protection. Opened PE-AUTO-06 (PE Sequencer — Automatic Advance Between PEs) with `infra-impl-codex` as Implementer and `infra-val-claude` as Validator per alternation rule. | 2026-04-07 |
| PM-CHORE-25  | Closed PE-AUTO-06 as merged (PR #313, PASS verdict). Opened PE-AUTO-07 (PM Agent Arbitration Protocol) with `infra-impl-claude` as Implementer and `infra-val-codex` as Validator per alternation rule. Dependencies PE-AUTO-04 and PE-AUTO-05 satisfied. | 2026-04-08 |
| PM-CHORE-26  | Closed PE-AUTO-07 as merged (PR #314, PASS verdict — 6 FAIL iterations). Opened PE-AUTO-08 (Discord Loop for Autonomous Operation) with `infra-impl-codex` as Implementer and `infra-val-claude` as Validator per alternation rule. Dependencies PE-AUTO-06 and PE-AUTO-07 satisfied. | 2026-04-08 |
| PM-CHORE-27  | Closed PE-AUTO-08 as merged (PR #315, PASS verdict). Opened PE-AUTO-09 (Plan Loader — New Plan Ingestion) with `infra-impl-claude` as Implementer and `infra-val-codex` as Validator per alternation rule. Dependencies PE-AUTO-06 and PE-AUTO-08 satisfied. | 2026-04-09 |
| PM-CHORE-28  | Closed PE-AUTO-09 as merged (PR #316, PASS verdict — 1 FAIL iteration resolved). Opened PE-AUTO-10 (Observability Dashboard) with `infra-impl-codex` as Implementer and `infra-val-claude` as Validator per alternation rule. Dependency PE-AUTO-09 satisfied. | 2026-04-10 |
| PM-CHORE-29  | Closed PE-AUTO-10 as merged (PR #317, PASS verdict). Opened PE-AUTO-11 (Parallel Track Scheduler) with `infra-impl-claude` as Implementer and `infra-val-codex` as Validator per alternation rule. Dependencies PE-AUTO-06 and PE-AUTO-09 satisfied. | 2026-04-10 |
| PM-CHORE-30  | Closed PE-AUTO-11 as merged (PR #318, PASS verdict — 1 FAIL iteration resolved). All 14 automation PEs in `ELIS_2Agent_Automation_Plan_v2_0.md` are now merged. Plan complete. Awaiting PM assignment of next plan or release. | 2026-04-10 |
| PM-CHORE-31  | Extended the automation plan to include PE-AUTO-12 (elis-server Bot Review Identity Activation). Opened PE-AUTO-12 with `infra-impl-codex` as Implementer and `infra-val-claude` as Validator per alternation rule. This PE operationalises backlog item `ELIS-SERVER-01` so live PR review actions on `elis-server` use the correct bot identities instead of the PO account. | 2026-04-11 |
| PM-CHORE-32  | Closed PE-AUTO-12 as merged (PR #321, PASS verdict — 1 FAIL iteration resolved; manual merge by PO after gate-1/review timing gap exposed by PR #321). Extended the automation plan (v3.4) to include PE-AUTO-13 (Gate 2 Re-trigger on Bot Review Approval). Opened PE-AUTO-13 with `infra-impl-claude` as Implementer and `infra-val-codex` as Validator per alternation rule. Dependency PE-AUTO-12 satisfied. | 2026-04-12 |
| PM-CHORE-33  | Closed PE-AUTO-13 as superseded by Architecture v1.8 (PR #322 closed — scope blocked by `workflow` scope limitation of bot PAT; Gate 2 re-trigger resolved structurally under v1.8 as direct PM action). Adopted `ELIS_MultiAgent_Implementation_Plan_v1_8.md` as governing plan (Hybrid SLR Execution series). Transitioned release to "ELIS Hybrid SLR Execution Plan · v1.8". Opened PE-SLR-01 (Harvest Workflow Contract) with `prog-impl-claude` (Claude Code) as Implementer and `prog-val-codex` (CODEX) as Validator. Architecture v1.8 validated by Claude Code (adversarial independence rule restored, all other invariants confirmed). | 2026-04-12 |
| PM-CHORE-34  | Adopted `ELIS_MultiAgent_Implementation_Plan_v1_8_1.md` as a patch revision to v1.8 while keeping PE-SLR-01 active. Added `PE-INFRA-SLR-01` (Role-Based Agent Surface Normalisation) after PE-SLR-02, shifted downstream default staffing to preserve structural alternation, and formalised provider-neutral workflow surfaces as an explicit release criterion. | 2026-04-13 |
| PM-CHORE-35  | Adopted `ELIS_MultiAgent_Implementation_Plan_v1_8_2.md` as a patch revision to v1.8.1 while keeping PE-SLR-01 active. Added `PE-INFRA-SLR-02` (Distinct Review Identity Enforcement), formalised the requirement that validator-capable agents need distinct GitHub review identities on protected branches, and recorded `elis-gemini-bot` as the required onboarding path for recurring Gemini validator duty. | 2026-04-13 |
| PM-CHORE-36  | Closed PE-SLR-01 as merged (PR #323, PASS verdict). Opened PE-SLR-02 (Harvest Workflow Reliability and Audit) with `gemini-cli` as Implementer and `prog-val-codex` (CODEX @ `elis-server`) as Validator for the next Harvest reliability round. | 2026-04-13 |
| PM-CHORE-37  | Closed PE-SLR-02 as merged (PR #324, r3 PASS verdict — Claude Code as PM-authorised r3 Validator; admin merge after `gate-1` removed from required status checks to resolve structural timing gap). Opened PE-INFRA-SLR-01 (Role-Based Agent Surface Normalisation) with `infra-impl-claude` (Claude Code) as Implementer and `infra-val-codex` (CODEX) as Validator. Dependency PE-SLR-02 satisfied. | 2026-04-14 |
| PM-CHORE-38  | Adopted `ELIS_MultiAgent_Implementation_Plan_v1_8_3.md` as a patch revision to v1.8.2 while keeping PE-INFRA-SLR-01 active (`implementing`). Added `PE-INFRA-SLR-03` (PM Control-Plane Dispatch Hardening) with six orchestration reliability improvements: cross-agent visibility, direct PM dispatch with ACK contract, reachability/heartbeat gate, command contract, automatic runner fallback, and auditable event trail. Formalised Step 0 runtime evidence requirement for PE-INFRA-SLR-03: proof that PM cross-agent messaging is enabled (`tools.sessions.visibility=all` or equivalent) and one successful PM→validator dispatch/ACK exchange must appear in the opening Status Packet and PR comments before implementation starts. Registered PE-INFRA-SLR-02 and PE-INFRA-SLR-03 in Active PE Registry as `planning`. | 2026-04-14 |
| PM-CHORE-39  | Closed PE-INFRA-SLR-01 as merged (PR #328, PO-merged after formal APPROVE review). Opened PE-INFRA-SLR-02 (Distinct Review Identity Enforcement) with `infra-impl-codex` (CODEX) as Implementer and `infra-val-claude` (Claude Code) as Validator per alternation rule. Dependency PE-INFRA-SLR-01 satisfied. | 2026-04-14 |
| PM-CHORE-40  | PE-INFRA-SLR-02 scope update by PM/PO decision: AC-3 (`elis-gemini-bot` onboarding) moved to DEFERRED — out of scope for this PE, to be addressed in a dedicated later PE. PASS criteria for PE-INFRA-SLR-02 are AC-1, AC-2, AC-4, AC-5, and AC-6 using `elis-codex-bot` and `elis-claude-bot` identities only. Plan v1.8.3 AC table updated to reflect DEFERRED status. PR #329 opening Status Packet revised accordingly. | 2026-04-14 |
| PM-CHORE-41  | Added PE-INFRA-SLR-04 (Model-Agnostic Agent Naming Governance) to plan v1.8.3 and registered it as `planning`. Scope: replace model/provider-coupled agent IDs with role-capability naming, add migration map and policy enforcement, and keep runtime dispatch compatibility. Dependency: PE-INFRA-SLR-03. | 2026-04-15 |
| PM-CHORE-42  | Closed PE-INFRA-SLR-02 as merged (PR #329). Opened PE-INFRA-SLR-03 (PM Control-Plane Dispatch Hardening) with `infra-impl-claude` as Implementer and `infra-val-codex` as Validator per alternation rule. Dependency PE-INFRA-SLR-02 satisfied. | 2026-04-15 |

Alternation rule:
- For consecutive PEs in the same domain, the implementer engine must alternate (`codex` <-> `claude`).
- Validator engine must be opposite to implementer engine.
- Historical rows with status `merged` may predate alternation enforcement and are preserved as audit history.

---

## PM instructions

1. At the start of every PE: update `PE`, `Branch`, and `Agent roles` table.
2. At the start of every new release: update the entire `Release context` table.
3. Commit and push this file to the base branch before notifying agents to start.
4. If this file is absent or incomplete, agents must stop and notify PM.

## Agent instructions

- Step 0: read `Release context` to know the base branch and plan file for this session.
- Never hardcode specific branch names or plan filenames — always resolve from this file.
- If a field in this file is blank or missing, stop and notify PM.
