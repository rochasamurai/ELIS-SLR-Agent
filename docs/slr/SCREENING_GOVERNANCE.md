# Screening Governance (`PE-SLR-04`)

## Purpose

Define the governance rules for local screening on `elis-server`: provenance
preservation, borderline-case handling, reproducible audit bundles, and
capacity/throttling policy.

---

## AC-1 — Provenance and Rationale Fields

Every screening decision must be represented as a `ScreeningDecision` instance
with the following fields:

| Field | Type | Requirement |
|-------|------|-------------|
| `record_id` | `str` | Non-empty; unique within a review |
| `source_id` | `str` | Non-empty; external identifier (DOI, OpenAlex ID, etc.) |
| `title` | `str` | Paper title |
| `decision` | `str` | One of `included`, `excluded`, `borderline` |
| `rationale` | `str` | Non-empty; human- or agent-readable justification |
| `decided_at` | `str` | ISO 8601 UTC timestamp (`YYYY-MM-DDTHH:MM:SSZ`) |
| `reviewer` | `str` | Agent or user that made the decision (default: `"automated"`) |

Construction of a `ScreeningDecision` with an empty `rationale`, empty
`record_id`, empty `source_id`, or an invalid `decision` value raises
`ValueError` at instantiation time.

---

## AC-2 — Borderline Case Handling

A decision is considered borderline when either:
- `decision == "borderline"`, or
- `rationale` contains one of the uncertainty markers:
  `uncertain`, `borderline`, `ambiguous`, `unclear`, `inconclusive`,
  `marginal`, `review required`, `needs review`.

Use `surface_borderline_cases(decisions)` from `elis.screening_governance` to
extract all borderline decisions from a run for explicit human review.

Borderline IDs are included in every audit bundle so reviewers can find them
without re-scanning the full output.

---

## AC-3 — Audit Bundle

`generate_audit_bundle(review_id, decisions, policy)` returns a dict with:

```json
{
  "schema_version": "1.0",
  "review_id": "<review_id>",
  "stage": "screening-governance",
  "record_total": <int>,
  "decision_counts": { "included": <n>, "excluded": <n>, "borderline": <n> },
  "borderline_count": <int>,
  "borderline_ids": ["<sorted record_ids>"],
  "capacity_policy": { ... },
  "generated_at": "<ISO 8601 UTC>"
}
```

Bundles are reproducible: given the same decisions list and policy, all fields
except `generated_at` are deterministic. `borderline_ids` is always sorted.

---

## AC-4 — Capacity and Throttling Policy

The `CapacityPolicy` dataclass enforces resource limits on `elis-server`:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `max_records_per_run` | `100` | Hard cap on records per bounded pilot run |
| `max_records_per_batch` | `500` | Soft cap for bulk Appendix A imports |
| `max_concurrent_runs` | `1` | Maximum parallel screening processes (serialised by default) |
| `min_seconds_between_runs` | `0` | Minimum gap between consecutive runs (0 = no throttle) |

### Rationale

- **`max_records_per_run = 100`**: Keeps pilot runs fast and auditable on
  `elis-server` hardware. Increase only after confirming memory/CPU headroom.
- **`max_records_per_batch = 500`**: Prevents single bulk imports from
  exhausting available RAM during Appendix A ingestion.
- **`max_concurrent_runs = 1`**: Avoids I/O contention on the shared
  `artifacts/screening/` directory. Revisit if parallel review IDs are needed.
- **`min_seconds_between_runs = 0`**: No mandatory cooldown by default;
  operators may set this to `60` or higher on constrained hardware.

### Enforcement

```python
from elis.screening_governance import enforce_capacity, DEFAULT_CAPACITY_POLICY

bounded = enforce_capacity(records, DEFAULT_CAPACITY_POLICY)
```

`enforce_capacity` truncates the input list to `policy.max_records_per_run`.

Custom policies:

```python
from elis.screening_governance import CapacityPolicy

pilot_policy = CapacityPolicy(max_records_per_run=50, min_seconds_between_runs=30)
```

---

## Usage Example

```python
from elis.screening_governance import (
    CapacityPolicy,
    ScreeningDecision,
    enforce_capacity,
    generate_audit_bundle,
    surface_borderline_cases,
)
from elis.screening_local_contract import now_utc_iso  # if PE-SLR-03 is available

decisions = [
    ScreeningDecision(
        record_id="rec-001",
        source_id="doi:10.1/example",
        title="Electoral integrity and AI",
        decision="included",
        rationale="directly relevant to research question",
        decided_at="2026-04-21T00:00:00Z",
    ),
    ScreeningDecision(
        record_id="rec-002",
        source_id="doi:10.1/other",
        title="General machine learning survey",
        decision="borderline",
        rationale="uncertain scope overlap",
        decided_at="2026-04-21T00:00:00Z",
    ),
]

borderline = surface_borderline_cases(decisions)
bundle = generate_audit_bundle("review-001", decisions)
```
