# OpenClaw Runtime Registry Audit

**Date:** 2026-03-24  
**PE:** `PE-MS-04`  
**Host:** `elis-server`  
**Purpose:** capture the as-operated runtime roster and normalize it to canonical host paths

---

## Summary

The live native OpenClaw runtime is still operating a **13-agent** configuration.
That runtime does not yet match the **19-agent** Architecture v1.6 target, but it
does provide a stable baseline for PE-MS-04:

- the active agent IDs are known
- the runtime no longer depends on `/app/...` container paths
- the source-controlled runtime config can now be normalized to canonical host paths

This PE does **not** add the missing phase-specialized SLR agents. That work remains
for later PEs in the series.

---

## Live Evidence Captured

Command executed successfully from the notebook:

```text
ssh elis-server "openclaw config get agents.list --json"
```

Observed live agent IDs and declared workspaces:

```text
pm | /home/samurai/openclaw/workspace-pm | openai/gpt-5-mini
slr-impl-codex | workspace-slr-impl | openai/gpt-5.1-codex
slr-impl-claude | workspace-slr-impl | anthropic/claude-sonnet-4-6
slr-val-codex | workspace-slr-val | openai/gpt-5.1-codex
slr-val-claude | workspace-slr-val | anthropic/claude-sonnet-4-6
prog-impl-codex | workspace-prog-impl | openai/gpt-5.1-codex
prog-impl-claude | workspace-prog-impl | anthropic/claude-sonnet-4-6
prog-val-codex | workspace-prog-val | openai/gpt-5.1-codex
prog-val-claude | workspace-prog-val | anthropic/claude-sonnet-4-6
infra-impl-codex | workspace-infra-impl | openai/gpt-5.1-codex
infra-impl-claude | workspace-infra-impl | anthropic/claude-sonnet-4-6
infra-val-codex | workspace-infra-val | openai/gpt-5.1-codex
infra-val-claude | workspace-infra-val | anthropic/claude-sonnet-4-6
```

---

## Findings

### 1. Runtime count gap

Current runtime count: **13 agents**  
Architecture v1.6 target: **19 agents**

Missing from live runtime:

- `harvest-impl-codex`
- `harvest-val-claude`
- `screen-impl-claude`
- `screen-val-codex`
- `extract-impl-codex`
- `extract-val-claude`
- `synth-impl-claude`
- `synth-val-codex`
- `prisma-impl-claude`
- `prisma-val-codex`

Legacy generic SLR IDs still present:

- `slr-impl-codex`
- `slr-impl-claude`
- `slr-val-codex`
- `slr-val-claude`

### 2. Path-format drift

The live runtime currently mixes:

- one canonical absolute path for `pm`
- relative workspace names for all other agents

PE-MS-04 normalizes the source-controlled config to canonical absolute host paths for
all currently registered agents.

### 3. Native-runtime alignment

No live agent entry captured in this audit uses `/app/...`. The remaining path issue is
relative-vs-absolute normalization, not Docker-path contamination.

---

## Deliverables Produced by PE-MS-04

- `openclaw/openclaw.json`
  normalized source-controlled runtime config using canonical host paths
- `docs/openclaw/openclaw_sanitised.json`
  redacted reviewable runtime reference
- `docs/openclaw/AGENT_CATALOGUE.md`
  updated to distinguish current runtime snapshot from architecture target

---

## Next PEs

- `PE-MS-05` audits existing workspaces against the role/domain split
- `PE-MS-06` provisions phase-specialized SLR workspaces
- `PE-MS-07` aligns SLR project-store visibility rules
- `PE-MS-08` completes end-to-end operational validation on `elis-server`

---

*OpenClaw Runtime Registry Audit · 2026-03-24*
