"""Vocabulary extraction utilities for ASTA Phase 0 scoping."""

from __future__ import annotations

import re
from collections import Counter
from pathlib import Path
from typing import Any

import yaml


DEFAULT_STOPWORDS = {
    # determiners, pronouns, prepositions, conjunctions
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "been",
    "between",
    "both",
    "but",
    "by",
    "do",
    "does",
    "each",
    "for",
    "from",
    "had",
    "has",
    "have",
    "how",
    "however",
    "if",
    "in",
    "including",
    "into",
    "is",
    "it",
    "its",
    "may",
    "more",
    "most",
    "not",
    "of",
    "on",
    "one",
    "only",
    "or",
    "other",
    "our",
    "over",
    "own",
    "such",
    "than",
    "that",
    "the",
    "their",
    "them",
    "then",
    "there",
    "these",
    "they",
    "this",
    "those",
    "through",
    "to",
    "very",
    "was",
    "we",
    "were",
    "what",
    "when",
    "where",
    "which",
    "while",
    "who",
    "will",
    "with",
    "would",
    # generic academic filler
    "all",
    "also",
    "among",
    "analysis",
    "approach",
    "based",
    "can",
    "data",
    "development",
    "different",
    "findings",
    "first",
    "given",
    "high",
    "important",
    "information",
    "issues",
    "key",
    "method",
    "methods",
    "new",
    "number",
    "paper",
    "potential",
    "proposed",
    "provide",
    "quality",
    "research",
    "results",
    "several",
    "show",
    "significant",
    "some",
    "specific",
    "study",
    "time",
    "two",
    "use",
    "used",
    "using",
    "various",
    "well",
    # LaTeX noise
    "usepackage",
}


class VocabularyExtractor:
    """Extract terms, venues, and authors from ASTA candidate records."""

    def __init__(
        self,
        min_term_length: int = 3,
        stopwords: set[str] | None = None,
    ) -> None:
        self.min_term_length = min_term_length
        self.stopwords = stopwords if stopwords is not None else DEFAULT_STOPWORDS

    def extract(
        self,
        papers: list[dict[str, Any]],
        top_terms: int = 100,
        top_venues: int = 30,
        top_authors: int = 50,
    ) -> dict[str, Any]:
        """Build a vocabulary summary from a list of candidate papers."""
        term_counter: Counter[str] = Counter()
        venue_counter: Counter[str] = Counter()
        author_counter: Counter[str] = Counter()

        papers_with_abstract = 0
        for paper in papers:
            text_parts: list[str] = []
            title = paper.get("title")
            abstract = paper.get("abstract")
            if isinstance(title, str) and title.strip():
                text_parts.append(title)
            if isinstance(abstract, str) and abstract.strip():
                text_parts.append(abstract)
                papers_with_abstract += 1

            for token in self._tokenize(" ".join(text_parts)):
                term_counter[token] += 1

            venue = paper.get("venue") or paper.get("journal")
            if isinstance(venue, str) and venue.strip():
                venue_counter[venue.strip()] += 1

            for author in self._extract_authors(paper.get("authors")):
                author_counter[author] += 1

        key_terms = [
            {"term": term, "count": count}
            for term, count in term_counter.most_common(top_terms)
        ]
        top_venues_list = [
            {"venue": venue, "count": count}
            for venue, count in venue_counter.most_common(top_venues)
        ]
        top_authors_list = [
            {"author": author, "count": count}
            for author, count in author_counter.most_common(top_authors)
        ]

        return {
            "statistics": {
                "total_papers": len(papers),
                "papers_with_abstract": papers_with_abstract,
                "unique_terms": len(term_counter),
                "unique_venues": len(venue_counter),
                "unique_authors": len(author_counter),
            },
            "key_terms": key_terms,
            "venues": top_venues_list,
            "authors": top_authors_list,
        }

    def save_to_yaml(self, vocabulary: dict[str, Any], output_path: Path) -> None:
        """Write extracted vocabulary to YAML."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", encoding="utf-8") as handle:
            yaml.safe_dump(vocabulary, handle, sort_keys=False, allow_unicode=False)

    def generate_boolean_suggestions(
        self, vocabulary: dict[str, Any], top_n: int = 15
    ) -> list[str]:
        """Generate lightweight Boolean starter blocks from top terms."""
        terms = [t.get("term") for t in vocabulary.get("key_terms", [])]
        clean_terms = [str(t).strip() for t in terms if t]
        top = clean_terms[:top_n]
        if not top:
            return []

        quoted = ['"{}"'.format(term.replace('"', "")) for term in top]
        if len(quoted) <= 5:
            return [f"({' OR '.join(quoted)})"]

        blocks: list[str] = []
        chunk = 5
        for i in range(0, len(quoted), chunk):
            section = quoted[i : i + chunk]
            blocks.append(f"({' OR '.join(section)})")
        return blocks

    def _tokenize(self, text: str) -> list[str]:
        if not text:
            return []
        lowered = text.lower()
        tokens = re.findall(r"[a-z0-9][a-z0-9\-]+", lowered)
        return [
            token
            for token in tokens
            if len(token) >= self.min_term_length and token not in self.stopwords
        ]

    @staticmethod
    def _extract_authors(raw_authors: Any) -> list[str]:
        names: list[str] = []
        if isinstance(raw_authors, list):
            for item in raw_authors:
                if isinstance(item, str) and item.strip():
                    names.append(item.strip())
                elif isinstance(item, dict):
                    name = item.get("name") or item.get("author")
                    if isinstance(name, str) and name.strip():
                        names.append(name.strip())
        elif isinstance(raw_authors, str) and raw_authors.strip():
            names.append(raw_authors.strip())
        return names
