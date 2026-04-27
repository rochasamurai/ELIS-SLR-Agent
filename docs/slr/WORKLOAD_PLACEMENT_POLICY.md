# Workload Placement Policy — PE-SLR-09

## Purpose

Define and enforce practical placement safeguards for `elis-server` so local SLR
work remains within host capacity while Extraction and Synthesis stay off-host.

## Canonical Policy

- Policy version: `1.0`
- Maximum local concurrency: `1`
- Allowed local workload classes:
  - `screening`
  - `lightweight-support`
  - `metadata-triage`
  - `bibliometric-preanalysis`
- Off-host-only workload classes:
  - `harvest`
  - `extraction`
  - `synthesis`

This policy is implemented in `elis/workload_placement_policy.py` as
`DEFAULT_WORKLOAD_PLACEMENT_POLICY`.

## Enforcement Rules

1. Local requests are validated via `enforce_local_workload_request()`.
2. If local capacity is full, new local work is deferred (`recommended_action=defer`).
3. Off-host classes are rejected for local execution with a runtime error.
4. Promotion from local helper/screening classes to off-host classes is blocked by
   `prevent_local_promotion()`.

## Capacity-Triggered Throttling Guidance

Use `capacity_triggered_throttling(queue_depth, memory_pressure_percent)`:

- Trigger throttling when queue depth exceeds policy concurrency.
- Trigger throttling when memory pressure is `>= 80%`.
- During throttling:
  - defer new local runs;
  - pause non-essential local helper runs;
  - keep Extraction and Synthesis pinned off-host.

## PM Reporting Surface

PM can report workload placement using `report_workload_classes()` which returns:

- policy version;
- max local concurrency;
- local workload classes;
- off-host workload classes;
- throttle guidance statements.

## Validation Command

```bash
python -m pytest tests/test_workload_placement_policy.py -v
```
