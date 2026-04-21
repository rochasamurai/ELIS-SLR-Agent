# Local Support Analysis (`PE-SLR-06`)

## Purpose

Provide bounded local support capabilities for bibliometric clustering and
discrepancy pre-analysis on review datasets running on `elis-server`. All
outputs are advisory-only and carry runtime safeguards that prevent them from
being used as final review decisions.

---

## AC-1 — Bibliometric Clustering

`cluster_by_title_similarity(records, threshold, max_records)` groups records
by title word-overlap similarity using the Jaccard index over non-trivial
word tokens.

### Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `records` | — | List of dicts with `record_id` and `title` keys |
| `threshold` | `0.5` | Minimum Jaccard similarity to place two records in the same cluster |
| `max_records` | `500` | Hard bound on input list before processing |

### Output

Returns `list[BibliometricCluster]`. Each cluster is:

| Field | Type | Description |
|-------|------|-------------|
| `cluster_id` | `str` | Deterministic sequential ID (`cluster-0000`, …) |
| `record_ids` | `tuple[str, …]` | Sorted record IDs in this cluster |
| `representative_title` | `str` | Title of the first record in the cluster |
| `similarity_basis` | `str` | Always `"jaccard-title-tokens"` |
| `advisory_only` | `bool` | Always `True` — enforced in `__post_init__` |

Output is deterministic for stable input. Every input record appears in exactly
one cluster.

### Usage

```python
from elis.local_support_analysis import cluster_by_title_similarity

records = [
    {"record_id": "rec-001", "title": "Machine learning in electoral systems"},
    {"record_id": "rec-002", "title": "Machine learning for electoral systems review"},
    {"record_id": "rec-003", "title": "Palaeontology of the Devonian period"},
]

clusters = cluster_by_title_similarity(records, threshold=0.4)
for c in clusters:
    print(c.cluster_id, c.record_ids)
```

---

## AC-2 — Discrepancy Pre-analysis (Advisory Artefacts Only)

`detect_discrepancies(records, similarity_threshold, max_records)` identifies
pairs of records with high title similarity as potential duplicates.

### Output — `DiscrepancyReport`

| Field | Type | Description |
|-------|------|-------------|
| `report_id` | `str` | Unique ID with UTC timestamp |
| `potential_duplicates` | `tuple[tuple[str, str], …]` | Sorted pairs of potentially duplicate record IDs |
| `conflict_count` | `int` | Number of duplicate pairs found |
| `generated_at` | `str` | ISO 8601 UTC timestamp |
| `advisory_only` | `bool` | Always `True` — enforced in `__post_init__` |
| `disclaimer` | `str` | Mandatory advisory disclaimer text |

Outputs are stored as advisory artefacts. They must not be used to exclude
records from screening without explicit human review.

---

## AC-3 — Runtime Safeguard

`DiscrepancyReport.as_final_decision()` raises `TypeError` unconditionally:

```python
report = detect_discrepancies(records)
report.as_final_decision()
# TypeError: DiscrepancyReport cannot be used as a final review decision.
# This output is advisory only and must not be used as a final review decision.
```

Constructing a `DiscrepancyReport` or `BibliometricCluster` with
`advisory_only=False` raises `ValueError` at construction time.

---

## AC-4 — Capacity Impact Measurement

`measure_capacity_impact(operation_fn, records, max_records, **kwargs)` wraps
any local analysis function and returns both its result and a `CapacityReport`:

| Field | Type | Description |
|-------|------|-------------|
| `operation` | `str` | Name of the wrapped function |
| `record_count` | `int` | Number of records actually processed (after bound) |
| `elapsed_seconds` | `float` | Wall-clock seconds for the operation |
| `max_records_used` | `int` | The `max_records` cap applied |
| `notes` | `str` | Optional operator notes |

### Usage

```python
from elis.local_support_analysis import (
    cluster_by_title_similarity,
    detect_discrepancies,
    measure_capacity_impact,
)

clusters, cap = measure_capacity_impact(
    cluster_by_title_similarity, records, max_records=500, threshold=0.5
)
print(f"Processed {cap.record_count} records in {cap.elapsed_seconds:.3f}s")

report, cap2 = measure_capacity_impact(
    detect_discrepancies, records, max_records=500
)
print(f"Found {report.conflict_count} potential duplicates")
```

### Capacity Defaults

| Parameter | Default | Rationale |
|-----------|---------|-----------|
| `DEFAULT_MAX_RECORDS` | `500` | Consistent with PE-SLR-04 `max_records_per_batch`; prevents unbounded O(n²) title comparison on elis-server |

The O(n²) comparison in both `cluster_by_title_similarity` and
`detect_discrepancies` means runtime scales quadratically with record count.
At 500 records the comparison loop executes ~125,000 iterations; at 1,000
records it executes ~500,000. The `max_records` cap keeps worst-case runtime
under 1 second on elis-server hardware for typical title lengths.

---

## Full Example

```python
from elis.local_support_analysis import (
    cluster_by_title_similarity,
    detect_discrepancies,
    measure_capacity_impact,
)

records = [
    {"record_id": "rec-001", "title": "Electoral integrity and AI monitoring"},
    {"record_id": "rec-002", "title": "Electoral integrity monitoring with AI"},
    {"record_id": "rec-003", "title": "Palaeontology of the Devonian period"},
]

# Cluster
clusters, cap = measure_capacity_impact(
    cluster_by_title_similarity, records, max_records=500, threshold=0.4
)
print(f"Clusters: {len(clusters)}, processed {cap.record_count} records")

# Discrepancy pre-analysis
report, cap2 = measure_capacity_impact(
    detect_discrepancies, records, max_records=500, similarity_threshold=0.5
)
print(f"Potential duplicates: {report.conflict_count}")
print(f"Advisory only: {report.advisory_only}")
```
