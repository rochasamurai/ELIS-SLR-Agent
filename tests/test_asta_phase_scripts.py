"""Tests for ASTA Phase 2/3 helper functions."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

from scripts.phase2_asta_screening import (
    deduplicate_snippets,
    extract_paper_ids as extract_paper_ids_phase2,
    load_records as load_records_phase2,
)
from scripts.phase3_asta_extraction import (
    extract_paper_ids as extract_paper_ids_phase3,
    group_by_paper_id,
    load_records as load_records_phase3,
)


def test_phase2_load_records_json_and_jsonl(tmp_path: Path) -> None:
    """Phase 2 loader should parse both JSON and JSONL collections."""
    json_path = tmp_path / "papers.json"
    json_path.write_text(
        json.dumps({"papers": [{"paper_id": "p1"}, {"paper_id": "p2"}]}),
        encoding="utf-8",
    )
    records_json = load_records_phase2(json_path)
    assert len(records_json) == 2

    jsonl_path = tmp_path / "papers.jsonl"
    jsonl_path.write_text(
        json.dumps({"paper_id": "p3"}) + "\n" + json.dumps({"paper_id": "p4"}) + "\n",
        encoding="utf-8",
    )
    records_jsonl = load_records_phase2(jsonl_path)
    assert len(records_jsonl) == 2


def test_phase2_extract_paper_ids_and_deduplicate_snippets() -> None:
    """Phase 2 helpers should dedupe ids and snippet duplicates."""
    ids = extract_paper_ids_phase2(
        [
            {"paper_id": "x1"},
            {"paperId": "x2"},
            {"asta_id": "x1"},
            {"corpus_id": 123},
        ]
    )
    assert ids == ["x1", "x2", "123"]

    snippets = [
        {"paper_id": "x1", "snippet_text": "Alpha beta"},
        {"paper_id": "x1", "snippet_text": " alpha beta "},
        {"paper_id": "x2", "snippet_text": "Gamma"},
    ]
    deduped = deduplicate_snippets(snippets)
    assert len(deduped) == 2


def test_phase3_load_records_yaml_and_grouping(tmp_path: Path) -> None:
    """Phase 3 loader should parse YAML and group snippets by paper id."""
    yaml_path = tmp_path / "papers.yml"
    yaml_path.write_text(
        yaml.safe_dump({"records": [{"paper_id": "z1"}, {"paperId": "z2"}]}),
        encoding="utf-8",
    )
    records = load_records_phase3(yaml_path)
    assert len(records) == 2

    ids = extract_paper_ids_phase3(records)
    assert ids == ["z1", "z2"]

    grouped = group_by_paper_id(
        [
            {"paper_id": "z1", "snippet_text": "One"},
            {"paper_id": "z1", "snippet_text": "Two"},
            {"snippet_text": "Unknown id"},
        ]
    )
    assert len(grouped["z1"]) == 2
    assert len(grouped["unknown"]) == 1
