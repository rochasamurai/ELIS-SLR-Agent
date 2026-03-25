# SLR Phase Workspace Provisioning

**Date:** 2026-03-25
**PE:** `PE-MS-06`
**Purpose:** replace the generic SLR workspaces with phase-specialized workspaces and align the source-controlled runtime to the Architecture v1.6 19-agent topology.

---

## Provisioned Workspace Set

| Workspace | Agents | Phase |
|---|---|---|
| `workspace-slr-harvest` | `harvest-impl-codex`, `harvest-val-claude` | Information sources, search, deduplication |
| `workspace-slr-screen` | `screen-impl-claude`, `screen-val-codex` | Study selection and exclusion reasons |
| `workspace-slr-extract` | `extract-impl-codex`, `extract-val-claude` | Data extraction and appraisal |
| `workspace-slr-synth` | `synth-impl-claude`, `synth-val-codex` | Narrative/tabular synthesis and evidence grading |
| `workspace-slr-prisma` | `prisma-impl-claude`, `prisma-val-codex` | PRISMA 2020 flow and checklist outputs |

All five workspaces contain:

- `AGENTS.md`
- `CLAUDE.md`
- `CODEX.md`

---

## Retired Generic Workspaces

The following source-controlled workspaces are retired by PE-MS-06:

- `workspace-slr-impl`
- `workspace-slr-val`

They are replaced by the 5 phase-specialized workspaces above. Any remaining live host copies should be removed on the next deployment sync.

---

## Runtime Config Change

`openclaw/openclaw.json` and `docs/openclaw/openclaw_sanitised.json` now declare:

- 19 total agents
- 10 phase-specialized SLR agents
- 0 generic `slr-*` agents

---

## Deployment Note

To make the source-controlled 19-agent topology live on `elis-server`:

```bash
bash scripts/deploy_openclaw_workspaces.sh
systemctl --user restart openclaw-gateway
openclaw doctor
```

The deploy script now copies the full workspace tree even when `rsync` is unavailable.
