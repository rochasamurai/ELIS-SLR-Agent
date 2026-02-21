# SLR Domain Specification

## 1. Purpose

This document defines SLR-domain artifacts, quality gates, and acceptance criteria for
OpenClaw PE-OC-05 and subsequent SLR-domain PEs.

## 2. Artifact Types

- Screening decisions: include/exclude decisions with explicit reason codes.
- Data extraction sheets: structured variables per included study.
- PRISMA flow records: stage counts for identification, screening, eligibility, inclusion.
- Synthesis notes: textual/tabular synthesis linked to extracted evidence.
- Protocol deviation log: dated rationale for approved deviations.

## 3. Minimum Fields

### 3.1 Screening decisions

Each row must include:
- `study_id`
- `decision` (`include` | `exclude`)
- `reason_code`

### 3.2 Data extraction

Each row must include:
- `study_id`
- `country`
- `design`
- `sample_size`
- `outcomes`

### 3.3 PRISMA record

Required integers:
- `identified`
- `screened`
- `eligible`
- `included`

Monotonic rule:
- `identified >= screened >= eligible >= included`

### 3.4 Agreement

Required:
- `metric`
- `value`
- `threshold`

Rule:
- `value >= threshold`

## 4. SLR Quality Gates

1. Eligibility compliance: decisions map to explicit criteria.
2. Extraction completeness: required extraction fields populated.
3. PRISMA consistency: stage arithmetic is coherent.
4. Dual-reviewer agreement threshold met.
5. Traceability: synthesis outputs map to source studies.
6. Citation format validation: references use stable source identifiers.

## 5. Acceptance Criteria Reference

For PE-OC-05 validator checks:
- Implementer workspace defines at least five SLR acceptance criteria types.
- Validator workspace defines at least three SLR methodological checks distinct from code-only validation.
- `scripts/check_slr_quality.py` exits 0 for compliant payload.
- SLR agent IDs are registered in OpenClaw configuration.
