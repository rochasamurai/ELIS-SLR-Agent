# PARALLEL_TRACK_GUIDE.md — Parallel Track Scheduler

> Operational guide for the PE-AUTO-11 parallel-track feature.
> Covers eligibility criteria, CURRENT_PE.md dual-track format,
> manual population of Track B, and automatic sequencer behaviour.

---

## 1. Overview

The parallel track scheduler allows two independent PEs to execute simultaneously
as Track A and Track B. This reduces release wall-clock time when the dependency
DAG has multiple independent branches ready at the same time.

**Key constraint:** parallel tracks must not share file scope, must have no mutual
dependency (direct or transitive), and must use opposite implementer engines.

---

## 2. Eligibility Criteria

`scripts/check_parallel_eligibility.py` checks five conditions before approving a
parallel pair. A pair is `ELIGIBLE` only when all criteria pass:

| # | Criterion | Checked by |
|---|---|---|
| 1 | Both PE IDs exist in the plan | `check_eligibility()` |
| 2 | No **direct** dependency between them (in either direction) | `check_eligibility()` |
| 3 | No **transitive** dependency between them (in either direction) | `check_eligibility()` |
| 4 | **Opposite implementer engines** (one codex, one claude) | `check_eligibility()` |
| 5 | No file-scope overlap (tracked separately via `check_parallel_eligibility.py`) | Out of scope for current implementation; document explicitly in HANDOFF.md when encountered |

### Examples — ELIGIBLE

**PE-AUTH-01 + PE-AUTH-02:**

- PE-AUTH-01 (`infra-impl-claude`) depends on `[]` (no prerequisites inside the pair)
- PE-AUTH-02 (`infra-impl-codex`) depends on `[]`
- No mutual dependency, opposite engines → `ELIGIBLE`

**PE-MS-07 + a PM-chore branch:**

- PE-MS-07 is a domain-independent infra PE with no dependency on the chore branch
- No shared files between an infra PE and a housekeeping branch → `ELIGIBLE`

### Examples — INELIGIBLE

**Direct dependency:**

```
PE-AUTO-09 depends_on [PE-AUTO-06]
```

PE-AUTO-09 and PE-AUTO-06 → `INELIGIBLE` — PE-AUTO-09 directly depends on PE-AUTO-06.

**Transitive dependency:**

```
PE-C depends_on [PE-B]
PE-B depends_on [PE-A]
```

PE-A and PE-C → `INELIGIBLE` — PE-C transitively depends on PE-A.

**Same engine:**

```
PE-X: implementer = infra-impl-codex
PE-Y: implementer = infra-impl-codex
```

PE-X and PE-Y → `INELIGIBLE` — same implementer engine; parallel tracks must use
opposite engines so each agent has an independent implementation track.

---

## 3. CURRENT_PE.md Dual-Track Format

When the sequencer performs a parallel dispatch it rewrites the `## Current PE`
section from single-track:

```markdown
## Current PE

| Field   | Value                              |
|---------|------------------------------------|
| PE      | PE-AUTO-11                         |
| Branch  | feature/pe-auto-11-...             |
```

to dual-track:

```markdown
## Current PE

| Field          | Value                                              |
|----------------|----------------------------------------------------|
| Track A PE     | PE-AUTO-11                                         |
| Track A Branch | feature/pe-auto-11-parallel-track-scheduler        |
| Track B PE     | PE-AUTO-12                                         |
| Track B Branch | feature/pe-auto-12-observability-extension         |
```

The Agent roles table reflects Track A's implementer engine for the current session.

When Track A closes (its PR is merged), the sequencer switches back to single-track
with Track B as the sole active PE and updates the Agent roles table accordingly.

---

## 4. Manual Population of Track B

If the sequencer did not automatically set up dual-track (e.g. the plan predates
PE-AUTO-11, or the sequencer was bypassed), PM can manually populate Track B:

1. Run `check_parallel_eligibility.py PE-X PE-Y <plan_file>` to confirm `ELIGIBLE`.
2. Create the Track B branch from `main`:
   ```bash
   git checkout main
   git checkout -b feature/pe-y-<title>
   git push -u origin feature/pe-y-<title>
   ```
3. Edit `CURRENT_PE.md` — replace the `## Current PE` single-track table with the
   dual-track format shown above.
4. Add Track B to the Active PE Registry with status `implementing`.
5. Commit and push to `main`:
   ```bash
   git add CURRENT_PE.md
   git commit -m "chore(pm): PM-CHORE-XX — open Track B PE-Y in parallel with PE-X"
   git push
   ```
6. Notify both agents of their track assignment.

---

## 5. Sequencer Automatic Decision Logic

```python
# Pseudo-code from scripts/pe_sequencer.py advance_current_pe()

merged_set = {merged PEs from registry}

# 1. Dual-track: Track A just closed
if is_dual_track(CURRENT_PE.md):
    mark Track A as merged
    switch CURRENT_PE.md to single-track with Track B
    return action="track_a_closed"

# 2. Find all ready PEs
all_ready = [pe for pe in plan if all(dep in merged_set for dep in pe.depends_on)]

# 3. Parallel dispatch if ≥2 ready and eligible
if len(all_ready) >= 2:
    for candidate in all_ready[1:]:
        if check_eligibility(all_ready[0], candidate) == ELIGIBLE:
            dispatch both as Track A + Track B
            update CURRENT_PE.md to dual-track format
            return action="dual_advance"

# 4. Single dispatch (default)
dispatch all_ready[0]
return action="advance"
```

---

## 6. AC-5 — Track A Closes While Track B Is Active

When Track A's PR is merged, the sequencer (`advance_current_pe`) detects
dual-track mode and performs the following:

1. Marks Track A as `merged` in the Active PE Registry.
2. Rewrites `## Current PE` back to single-track with Track B as the active PE.
3. Updates the Agent roles table to Track B's implementer engine.
4. Appends a PM chore entry recording the track change.
5. Returns `action="track_a_closed"` with Track B's ID and branch.

The agent freed from Track A:
- If Track B is at Gate 1 (ready for validation): transitions immediately to
  Track B validation after receiving the `track_a_closed` advance event.
- If Track B is still implementing: waits for Track B to reach Gate 1 before
  beginning validation.

This ensures no agent is idle while independent work is available.

---

*ELIS SLR Agent · PARALLEL_TRACK_GUIDE.md · Claude Code · 2026-04-10*
