"""Phase 0 ASTA vocabulary bootstrapping workflow."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any
import sys

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sources.asta_mcp.adapter import AstaMCPAdapter
from sources.asta_mcp.vocabulary import VocabularyExtractor


DEFAULT_RESEARCH_QUESTIONS = [
    "electoral integrity technological strategies effectiveness",
    "voting system security audit trails verification",
    "election technology trust voter confidence",
    "biometric authentication voter registration",
    "blockchain voting transparency auditability",
    "paper ballot verification hybrid systems",
    "risk-limiting audit statistical methods",
    "voter verifiable paper audit trail VVPAT",
]


def parse_args() -> argparse.Namespace:
    """Parse CLI options for phase 0 run."""
    parser = argparse.ArgumentParser(
        description="Run ASTA Phase 0 vocabulary bootstrapping."
    )
    parser.add_argument(
        "--config",
        default="config/asta_config.yml",
        help="Path to ASTA config file.",
    )
    parser.add_argument(
        "--output",
        default="config/asta_extracted_vocabulary.yml",
        help="Output YAML path for extracted vocabulary.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Override candidates per query.",
    )
    return parser.parse_args()


def load_config(path: Path) -> dict[str, Any]:
    """Load YAML config if available, otherwise return empty config."""
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    return data if isinstance(data, dict) else {}


def deduplicate_candidates(papers: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Deduplicate papers by DOI, then title+year fallback."""
    deduped: list[dict[str, Any]] = []
    seen: set[str] = set()
    for paper in papers:
        doi = str(paper.get("doi", "")).strip().lower()
        title = str(paper.get("title", "")).strip().lower()
        year = str(paper.get("year", "")).strip()
        key = f"doi:{doi}" if doi else f"title_year:{title}|{year}"
        if key in seen:
            continue
        seen.add(key)
        deduped.append(paper)
    return deduped


def main() -> int:
    """Execute the Phase 0 ASTA scoping workflow."""
    args = parse_args()
    config = load_config(Path(args.config))

    mcp_cfg = config.get("asta_mcp", {}) if isinstance(config, dict) else {}
    evidence_window_end = mcp_cfg.get("evidence_window_end", "2025-01-31")

    phase_cfg = config.get("phases", {}).get("phase0_vocabulary", {})
    questions = phase_cfg.get("research_questions", DEFAULT_RESEARCH_QUESTIONS)
    if not isinstance(questions, list) or not questions:
        questions = DEFAULT_RESEARCH_QUESTIONS

    default_limit = phase_cfg.get("candidates_per_query", 100)
    limit = args.limit if args.limit is not None else default_limit

    extractor = VocabularyExtractor()
    asta = AstaMCPAdapter(evidence_window_end=evidence_window_end)

    all_candidates: list[dict[str, Any]] = []
    print("=" * 70)
    print("ELIS ASTA PHASE 0 - VOCABULARY BOOTSTRAPPING")
    print("=" * 70)
    print(f"Evidence window end: {evidence_window_end}")
    print(f"Research questions: {len(questions)}")
    print(f"Candidates per query: {limit}")
    print()

    for idx, query in enumerate(questions, start=1):
        print(f"[{idx}/{len(questions)}] Query: {query}")
        try:
            candidates = asta.search_candidates(query=query, limit=limit)
            all_candidates.extend(candidates)
            print(f"  Retrieved {len(candidates)} candidates")
        except Exception as exc:  # noqa: BLE001
            print(f"  Error: {exc}")

    unique_candidates = deduplicate_candidates(all_candidates)
    print()
    print(f"Total candidates (raw): {len(all_candidates)}")
    print(f"Total candidates (deduped): {len(unique_candidates)}")
    print()

    vocab_top_terms = int(phase_cfg.get("vocabulary_top_terms", 100))
    vocab_top_venues = int(phase_cfg.get("vocabulary_top_venues", 30))
    vocab_top_authors = int(phase_cfg.get("vocabulary_top_authors", 50))

    vocabulary = extractor.extract(
        unique_candidates,
        top_terms=vocab_top_terms,
        top_venues=vocab_top_venues,
        top_authors=vocab_top_authors,
    )

    output_file = Path(args.output)
    extractor.save_to_yaml(vocabulary, output_file)

    print("Top key terms:")
    for item in vocabulary.get("key_terms", [])[:15]:
        print(f"  - {item['term']} ({item['count']})")
    print()

    print("Boolean starter suggestions:")
    for suggestion in extractor.generate_boolean_suggestions(vocabulary, top_n=15):
        print(f"  {suggestion}")
    print()

    stats = asta.get_stats()
    print("ASTA adapter stats:")
    print(f"  - Requests: {stats['requests']}")
    print(f"  - Errors: {stats['errors']}")
    print(f"  - Rate-limit hits: {stats['rate_limit_hits']}")
    print()

    print("Outputs:")
    print(f"  - Vocabulary: {output_file}")
    print(f"  - Logs: runs/{asta.run_id}/asta/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
