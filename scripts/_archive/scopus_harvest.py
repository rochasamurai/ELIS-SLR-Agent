"""Thin wrapper — delegates to ``elis harvest scopus``.

Usage is unchanged::

    python scripts/scopus_harvest.py --search-config config/searches/electoral_integrity_search.yml --tier production
    python scripts/scopus_harvest.py --max-results 500
    python scripts/scopus_harvest.py
"""

from __future__ import annotations

import sys

from elis.cli import main

if __name__ == "__main__":
    raise SystemExit(main(["harvest", "scopus"] + sys.argv[1:]))
