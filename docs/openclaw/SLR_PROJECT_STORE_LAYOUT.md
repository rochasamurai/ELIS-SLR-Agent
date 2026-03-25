# SLR Project Store Layout

**Version:** 1.0
**PE:** PE-MS-07
**Date:** 2026-03-25
**Architecture ref:** `ELIS_SLR_AI_Platform_Conceptual_Architecture_v1_6.md` §5.4 · §5.6 · §8.1

---

## Purpose

SLR review artifacts must be isolated from the platform repo. Each systematic literature
review runs in its own **project store** — a self-contained directory under
`/opt/elis/projects/` on `elis-server`. This document defines the canonical layout,
MANIFEST schema, per-phase access policy, and PM visibility rules.

---

## Canonical Layout

```
/opt/elis/projects/<review-id>/
  MANIFEST.md     ← review metadata and phase status (required)
  harvest/        ← search exports, run manifests, dedup outputs
  screen/         ← inclusion decisions (title/abstract and full-text, JSONL)
  extract/        ← structured extraction sheets, one JSONL per study
  synth/          ← narrative and tabular synthesis artifacts
  prisma/         ← PRISMA 2020 flow data and diagram inputs
```

### Review ID convention

`<review-id>` must be a lowercase alphanumeric slug, hyphens allowed, no spaces.
Examples: `elis-slr-2026`, `ai-ehr-review-q1`, `systematic-review-ml-health`.

---

## MANIFEST.md Schema

Every project store root must contain a `MANIFEST.md` with at minimum these fields:

```markdown
# Review Manifest

review_id: <id>
title: <human-readable title>
created: YYYY-MM-DD
protocol_ref: <URL or repo-relative path to protocol document>
status: active

## Phase Status

| Phase   | Status  | Agent pair                              |
|---------|---------|------------------------------------------|
| harvest | pending | harvest-impl-codex / harvest-val-claude  |
| screen  | pending | screen-impl-claude / screen-val-codex    |
| extract | pending | extract-impl-codex / extract-val-claude  |
| synth   | pending | synth-impl-claude / synth-val-codex      |
| prisma  | pending | prisma-impl-claude / prisma-val-codex    |
```

Valid `status` values: `pending` · `active` · `complete` · `blocked`

---

## Per-Phase Access Policy

Each SLR phase agent pair has write access to its own subdirectory and read access
to upstream phases it depends on.

| Phase workspace | Writes to | Reads from | Must not write to |
|---|---|---|---|
| `workspace-slr-harvest` | `harvest/` | — | `screen/` `extract/` `synth/` `prisma/` |
| `workspace-slr-screen` | `screen/` | `harvest/` | `extract/` `synth/` `prisma/` |
| `workspace-slr-extract` | `extract/` | `harvest/` `screen/` | `synth/` `prisma/` |
| `workspace-slr-synth` | `synth/` | `harvest/` `screen/` `extract/` | `prisma/` |
| `workspace-slr-prisma` | `prisma/` | `harvest/` `screen/` `extract/` `synth/` | — |

All phase agents may read `MANIFEST.md` to confirm which review they are operating on.
No phase agent may modify `MANIFEST.md` without explicit PM approval.

---

## PM Visibility

The PM Agent requires **read** visibility over `/opt/elis/projects/*` per Architecture §5.6.

Permitted PM exec commands (read-only):

```bash
ls /opt/elis/projects/
ls /opt/elis/projects/<review-id>/
cat /opt/elis/projects/<review-id>/MANIFEST.md
```

PM reporting rule: when a PO asks about project store status, PM reads `MANIFEST.md`
and reports the Phase Status table verbatim. PM does not infer phase status from
directory contents.

PM must not write to project stores without explicit PO approval and an operator
executing the write. PM-authored writes to project stores are a policy violation.

---

## Tooling

### Create a new project store

```bash
python scripts/setup_project_store.py --review-id <id> --title "<title>" \
    [--protocol-ref <ref>] [--base-path /opt/elis/projects]
```

- Creates all required subdirectories (idempotent — safe to re-run).
- Writes `MANIFEST.md` if not already present.
- Exits 0 on success, 1 on error.

### Validate an existing project store

```bash
python scripts/check_project_store_layout.py --path /opt/elis/projects/<review-id>
# OK: project store '<review-id>' is valid — 5 subdirs, MANIFEST.md present
```

- Exits 0 if valid, 1 with specific error messages if not.

---

## Deployment Note

Project stores are **not** deployed by `deploy_openclaw_workspaces.sh`.
They are created on demand per review by the PM Agent (via operator exec)
or directly by the implementing agent during a harvest PE.

---

*SLR Project Store Layout · v1.0 · PE-MS-07 · 2026-03-25*
