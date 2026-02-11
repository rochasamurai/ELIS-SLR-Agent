# ASTA Integration in ELIS SLR Agent

## Overview

ASTA (Allen AI) is integrated into ELIS as a discovery and evidence-localization assistant via MCP.

Policy: `ASTA proposes, ELIS decides`.
ASTA is not treated as a canonical database source.

Canonical sources remain:
- Scopus
- Web of Science
- IEEE Xplore
- Semantic Scholar
- OpenAlex
- CrossRef
- CORE
- Google Scholar

## Integration Role

ELIS uses ASTA in three places:

1. Phase 0 vocabulary bootstrapping
- Run ASTA discovery queries.
- Extract terms/venues/authors.
- Improve Boolean search strings used in canonical harvests.

2. Phase 2 screening assistance (planned)
- Retrieve snippets for candidate papers.
- Pre-fill relevance evidence for human screening.

3. Phase 3 evidence localization (planned)
- Retrieve targeted snippets for extraction constructs.
- Human validates all extracted evidence.

## Reproducibility Controls

1. Frozen evidence window
- ASTA queries use `evidence_window_end: 2025-01-31`.

2. Full audit logs
- `runs/<run_id>/asta/requests.jsonl`
- `runs/<run_id>/asta/responses.jsonl`
- `runs/<run_id>/asta/normalized_records.jsonl`
- `runs/<run_id>/asta/errors.jsonl`

3. Decision independence
- ASTA output is advisory.
- Inclusion/exclusion decisions remain ELIS-controlled.

## Setup

1. Request API key:
- https://share.hsforms.com/1L4hUh20oT3mu8iXJQMV77w3ioxm

2. Set environment variable (PowerShell):
```powershell
$env:ASTA_TOOL_KEY = "your_key_here"
```

3. Configure integration:
- `config/asta_config.yml`

## Usage

Run Phase 0 vocabulary bootstrapping:

```powershell
python scripts/phase0_asta_scoping.py --config config/asta_config.yml --output config/asta_extracted_vocabulary.yml --limit 25
```

Outputs:
- Vocabulary file: `config/asta_extracted_vocabulary.yml`
- Audit logs: `runs/<run_id>/asta/`

## PRISMA Reporting Notes

Report ASTA separately from canonical source counts:
- terms contributed by ASTA
- ASTA-proposed candidates evaluated by ELIS criteria
- snippets retrieved for screening/extraction support

## References

- ASTA resources: https://allenai.org/asta/resources
- ASTA MCP docs: https://allenai.org/asta/resources/mcp
