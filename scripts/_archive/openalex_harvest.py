"""
openalex_harvest.py — Backward-compatible wrapper.

Delegates to ``elis harvest openalex`` via the ELIS CLI.
See ``elis/sources/openalex.py`` for the adapter implementation.

CONFIGURATION MODES:
1. NEW (Recommended): --search-config config/searches/electoral_integrity_search.yml
   - Uses dedicated search configuration files
   - Supports tier-based max_results (testing/pilot/benchmark/production/exhaustive)
   - Project-specific settings

2. LEGACY (Backwards Compatible): Reads from config/elis_search_queries.yml
   - Maintains compatibility with existing workflows
   - Uses global max_results_per_source setting

Environment Variables:
- ELIS_CONTACT: Email for polite pool (faster rate limits — optional but recommended)

Outputs:
- JSON array in json_jsonl/ELIS_Appendix_A_Search_rows.json

Usage Examples:
  # New config format with tier
  python scripts/openalex_harvest.py --search-config config/searches/electoral_integrity_search.yml --tier production

  # New config format (uses default tier)
  python scripts/openalex_harvest.py --search-config config/searches/tai_awasthi_2025_search.yml

  # Legacy format (backwards compatible)
  python scripts/openalex_harvest.py

  # Override max_results regardless of config
  python scripts/openalex_harvest.py --max-results 500
"""

import sys

from elis.cli import main

if __name__ == "__main__":
    sys.exit(main(["harvest", "openalex"] + sys.argv[1:]))
