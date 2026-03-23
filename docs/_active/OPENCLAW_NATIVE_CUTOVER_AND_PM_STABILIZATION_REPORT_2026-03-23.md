# OpenClaw Native Cutover and PM Stabilization Report

**Date:** 2026-03-23  
**Host:** `elis-server`  
**Scope:** Native OpenClaw cutover after Docker removal, PM Agent recovery, and next-step recommendation.

---

## Executive Summary

The current OpenClaw installation should **not** be discarded and rebuilt from scratch.
The native runtime is working, the channels are working, and the remaining issues have
been concentrated in the PM Agent control plane:

- prompt drift across multiple workspace files
- stale session reuse
- mismatched exec/approval behavior on Discord
- model fallback and rate-limit handling
- overly broad interpretation of what the PM Agent may infer from `CURRENT_PE.md`

The best-practice recommendation is to **return to the 2-Agent model** and complete the
OpenClaw installation through a short stabilization series, not through a fresh reinstall.

---

## Recommendation

### Confirmed

Yes, ELIS should return to the **2-Agent model (Implementer + Validator)** to complete the
OpenClaw installation and stabilization.

### Why

- The unresolved work is now governed engineering work, not basic host provisioning.
- The repo already has a PE governance system, audit trail, plan versioning, and role alternation rules.
- The PM Agent itself is part of the product surface and should be finished under the same implementation/validation discipline as the rest of ELIS.
- Reverting to ad hoc live fixes without PE discipline will keep reintroducing prompt drift and undocumented state changes.

### Not recommended

Do **not** delete the current installation and start over at this stage.

Reasons:

- Native `systemd` runtime is already operational.
- Discord and Telegram are both functionally connected.
- PM Agent can now answer identity and PE-status queries after targeted fixes.
- A clean reinstall would recreate host/channel/config risk without solving the root causes of prompt drift and session persistence.

---

## Work History Since Docker Removal

### 1. Docker Runtime Retirement

- Docker and Docker Compose were removed from `elis-server`.
- Native OpenClaw under `systemd --user` was retained as the production runtime.
- User lingering was enabled so the service can remain active outside an interactive login session.

### 2. Native Runtime Verification

- `openclaw-gateway.service` was verified as active.
- `openclaw doctor` and `openclaw channels status --probe` were used as the main runtime health checks.
- Telegram and Discord connectivity were revalidated after the cutover.

### 3. Discord Recovery

- Discord configuration was corrected so the native service could connect successfully.
- A status mismatch remained for a while between plain `channels status` and `channels status --probe`; the probe path was treated as the authoritative connectivity signal.

### 4. PM Workspace Recovery

- The PM workspace on `elis-server` was corrected to use the intended ELIS workspace instead of stale generic bootstrap behavior.
- PM identity files were restored and aligned so the agent no longer presented itself as a blank slate.
- Canonical governance entrypoints were established through workspace paths pointing to repo truth:
  - `~/openclaw/workspace-pm/CURRENT_PE.md`
  - `~/openclaw/workspace-pm/docs/AGENTS.md`
  - `~/openclaw/workspace-pm/docs/PLAN_v1_5.md`

### 5. Repo and Documentation Alignment

- Architecture was updated to `ELIS_SLR_AI_Platform_Conceptual_Architecture_v1_6.md`.
- Implementation plan was updated to `ELIS_MultiAgent_Implementation_Plan_v1_5.md`.
- Docker-era production assumptions were removed from the target operating model.
- A target host layout and PM contingency-model documentation were added to the repo.

### 6. PM Model Contingency Work

- Anthropic billing failures forced temporary PM failover work.
- `openai/gpt-5.4mini` was tested and rejected as an invalid model identifier.
- `openai/gpt-5-mini` was configured successfully for the PM Agent.
- OpenAI rate limits were observed intermittently during live Discord use, so model availability remains an operational concern.

### 7. PM Agent Response Recovery

- PM prompt files (`AGENTS.md`, `SOUL.md`, `MEMORY.md`) were cleaned up on the host.
- The PM Agent was moved away from stale direct reads of `/opt/elis/repo/CURRENT_PE.md` and toward workspace entrypoints.
- Stale PM sessions were cleared so new prompt rules actually took effect.
- The PM Agent was able to answer:
  - `Who are you?`
  - `What are the current PEs?`

### 8. Root Cause of the Latest Discord Failure

The remaining approval-timeout issue was caused by **Discord execs being issued as elevated commands** for the PM Agent.

Observed behavior:

- `cat ~/openclaw/workspace-pm/CURRENT_PE.md` was allowlisted
- but it still ran as an elevated command from Discord
- elevated commands went to the gateway approval queue
- the queue expired after 120 seconds

Fix applied:

- `agents.list.0.tools.elevated.enabled` was set to `false`
- the gateway was restarted
- PM session state was cleared again

Result:

- the PM Agent can now answer PE-status questions without approval timeouts in the validated local run path

---

## Current Assessment

### Working

- native OpenClaw runtime on `elis-server`
- Docker removed from production host
- Telegram works
- Discord works
- PM identity response works
- PM PE-status response works
- canonical workspace entrypoint pattern works

### Still weak

- PM Agent still formats large registry dumps poorly in Discord
- PM Agent conflates branches with worktrees unless explicitly constrained
- PM prompt stack is still spread across multiple live files
- model-rate-limit behavior is not yet governed by a formal validation runbook
- host fixes are ahead of source-controlled prompt files in some places

---

## Why So Many Issues Have Appeared

This has taken a long time because ELIS is not simply installing OpenClaw; it is building a
**custom orchestration layer** on top of OpenClaw.

The difficult parts have been:

- channel behavior differences between Discord, Telegram, local CLI, and gateway UI
- OpenClaw session persistence holding onto stale assumptions after prompt changes
- duplicated sources of truth across repo files, host workspace files, symlinks, and session memory
- approval policy interactions with Discord exec behavior
- cross-provider model failover and rate limits
- incremental migration from Docker assumptions to native host assumptions

This level of friction is **expected** in a new custom OpenClaw implementation, especially
when the PM Agent is both:

- a production operational bot, and
- an orchestrator for a governed engineering workflow

It is not ideal, but it is normal for an early custom deployment.

---

## Best-Practice Next Move

The next move should be a **stabilization pass under the 2-Agent model**, not another round
of ad hoc live tweaking and not a host rebuild.

Immediate priorities:

1. source-control the corrected PM prompt stack
2. add a validation rule that “worktrees” must come from `git worktree list`, not registry inference
3. constrain PM Discord outputs for large tables
4. define a clean session-reset runbook whenever PM prompt files change
5. validate PM behavior with explicit implementation and validator evidence

---

## Conclusion

The OpenClaw installation is recoverable and operational enough to continue.

The right path is:

- keep the current native installation
- stop treating the remaining issues as host-rebuild problems
- return to the 2-Agent model
- complete stabilization through planned implementation and validation work

---

*OpenClaw Native Cutover and PM Stabilization Report · 2026-03-23 · ELIS MiniServer (`elis-server`)*
