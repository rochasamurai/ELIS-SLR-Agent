"""Unit tests for ASTA vocabulary extraction."""

from __future__ import annotations

from pathlib import Path

import yaml

from sources.asta_mcp.vocabulary import VocabularyExtractor


def test_extract_counts_terms_venues_and_authors() -> None:
    extractor = VocabularyExtractor()
    papers = [
        {
            "title": "Electoral integrity and voter verification",
            "abstract": "Voter verification improves electoral trust.",
            "venue": "Journal of Election Security",
            "authors": ["Alice Doe", "Bob Ray"],
            "year": 2024,
        },
        {
            "title": "Risk-limiting audit methods",
            "abstract": "Audit methods improve verification.",
            "venue": "Journal of Election Security",
            "authors": [{"name": "Alice Doe"}, {"author": "Carol Lin"}],
            "year": 2023,
        },
    ]

    vocab = extractor.extract(papers, top_terms=10, top_venues=10, top_authors=10)

    assert vocab["statistics"]["total_papers"] == 2
    assert vocab["statistics"]["papers_with_abstract"] == 2
    assert vocab["venues"][0]["venue"] == "Journal of Election Security"
    assert vocab["venues"][0]["count"] == 2
    authors = {item["author"]: item["count"] for item in vocab["authors"]}
    assert authors["Alice Doe"] == 2


def test_save_to_yaml_writes_file(tmp_path: Path) -> None:
    extractor = VocabularyExtractor()
    vocab = {
        "statistics": {"total_papers": 1},
        "key_terms": [{"term": "verification", "count": 3}],
        "venues": [],
        "authors": [],
    }
    output = tmp_path / "asta_vocab.yml"
    extractor.save_to_yaml(vocab, output)
    assert output.exists()

    loaded = yaml.safe_load(output.read_text(encoding="utf-8"))
    assert loaded["key_terms"][0]["term"] == "verification"


def test_generate_boolean_suggestions_returns_chunks() -> None:
    extractor = VocabularyExtractor()
    vocab = {
        "key_terms": [{"term": f"term{i}", "count": 10 - i} for i in range(12)],
    }
    suggestions = extractor.generate_boolean_suggestions(vocab, top_n=12)
    assert len(suggestions) == 3
    assert suggestions[0].startswith("(")
    assert "OR" in suggestions[0]
