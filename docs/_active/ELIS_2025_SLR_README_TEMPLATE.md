# ELIS 2025 SLR

Systematic Literature Review repository for **Electoral Integrity Strategies (ELIS 2025)**.

## 1. Overview
- Review type: Standard SLR (with possible future living-review activation by amendment).
- Topic: Operational and technological strategies improving electoral integrity/auditability.
- Coverage window: 1990-2025.

## 2. Current Status
- Protocol version: `v2.0`
- Phase: `<bootstrap | search | screening | extraction | synthesis>`
- Latest run: `<run-id>`

## 3. Repository Map
- `protocol/`: protocol and amendments
- `planning/`: eligibility, outcomes, RoB framework
- `configs/`: source configs and run manifests
- `runs/`: run-by-run inputs/outputs/logs/hashes
- `screening/`: title/abstract and full-text decisions
- `extraction/`: schema and extracted datasets
- `rob/`: risk-of-bias assessments
- `reporting/`: PRISMA artifacts and manuscript inputs
- `audits/`: reproducibility and process audits

## 4. Reproducibility Policy (Hard Requirements)
Each run must record:
- ELIS agent ref (`tag` or commit SHA)
- exact commands and runtime environment
- input manifest/config hashes
- output hashes
- operator and UTC timestamps

Runs without complete provenance are invalid.

## 5. Quickstart
1. Copy `.env.example` to local `.env` and set API credentials.
2. Confirm protocol + eligibility are frozen for current cycle.
3. Create a run folder under `runs/YYYY-MM-DD_run-<id>/`.
4. Execute pipeline steps (`harvest -> dedup -> merge -> screen -> validate`).
5. Save logs, manifests, and hashes in the run folder.
6. Open PR with run evidence and updated decision artifacts.

## 6. Governance
- No direct pushes to `main`.
- One logical change per PR.
- Any protocol deviation requires a dated amendment file in `protocol/amendments/`.
- All include/exclude decisions must be traceable to immutable `study_id`.

## 7. Integration with ELIS-SLR-Agent
Pin ELIS agent explicitly per run:
- `agent_repo`
- `agent_ref`
- `agent_release`

Do not run production SLR cycles against unpinned `main`.

## 8. Citation and License
- Citation metadata: `CITATION.cff`
- License: `<define>`

## 9. Contacts
- PM / Lead: `<name>`
- Method validator: `<name>`
- Data curator: `<name>`
