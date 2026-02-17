"""Thin wrapper — delegates to ``elis harvest crossref``.

Usage is unchanged::

    python scripts/crossref_harvest.py --search-config config/searches/electoral_integrity_search.yml --tier production
    python scripts/crossref_harvest.py --max-results 500
    python scripts/crossref_harvest.py
"""

from __future__ import annotations

import sys

from elis.cli import main

if __name__ == "__main__":
    raise SystemExit(main(["harvest", "crossref"] + sys.argv[1:]))
