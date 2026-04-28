### PE-AUTO-04 · Implementer Agent Runner

| Field | Value |
|---|---|
| Domain | infra |

**Acceptance Criteria:**

| # | Criterion |
|---|---|
| AC-1 | Runner fires upon detecting a change in `CURRENT_PE.md` with status `implementing` |
| AC-2 | Auth via secrets only |
| AC-3 | PR opened by the correct account |
| AC-4 | `HANDOFF.md` committed before the PR is converted to ready |
| AC-5 | Runner exits 1 when budget is exceeded |

---
