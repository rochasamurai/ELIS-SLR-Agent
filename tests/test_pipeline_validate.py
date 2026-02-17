"""Tests for elis.pipeline.validate — validator module."""

from __future__ import annotations

import json

import pytest

from elis.pipeline.validate import (
    generate_report,
    load_json_file,
    validate_appendix,
    validate_records,
)


class TestLoadJsonFile:
    def test_filters_meta(self, tmp_path):
        data = [
            {"_meta": True, "config": "test"},
            {"id": "1", "title": "Record 1"},
        ]
        f = tmp_path / "test.json"
        f.write_text(json.dumps(data), encoding="utf-8")
        result = load_json_file(f)
        assert len(result) == 1
        assert result[0]["id"] == "1"

    def test_non_array_raises(self, tmp_path):
        f = tmp_path / "bad.json"
        f.write_text('{"not": "array"}', encoding="utf-8")
        with pytest.raises(ValueError, match="Expected array"):
            load_json_file(f)


class TestValidateRecords:
    def test_valid(self):
        records = [{"id": "1", "name": "Alice"}]
        schema = {
            "type": "object",
            "required": ["id", "name"],
            "properties": {"id": {"type": "string"}, "name": {"type": "string"}},
        }
        ok, errors = validate_records(records, schema, "test.json")
        assert ok is True
        assert errors == []

    def test_missing_field(self):
        records = [{"id": "1"}]
        schema = {
            "type": "object",
            "required": ["id", "name"],
            "properties": {"id": {"type": "string"}, "name": {"type": "string"}},
        }
        ok, errors = validate_records(records, schema, "test.json")
        assert ok is False
        assert len(errors) > 0


class TestValidateAppendix:
    def test_valid(self, tmp_path):
        data = [{"_meta": True}, {"id": "1"}]
        schema = {
            "type": "object",
            "required": ["id"],
            "properties": {"id": {"type": "string"}},
        }
        jf = tmp_path / "data.json"
        sf = tmp_path / "schema.json"
        jf.write_text(json.dumps(data), encoding="utf-8")
        sf.write_text(json.dumps(schema), encoding="utf-8")
        ok, count, errors = validate_appendix("Test", jf, sf)
        assert ok is True
        assert count == 1

    def test_missing_file(self, tmp_path):
        ok, count, errors = validate_appendix(
            "Test", tmp_path / "nope.json", tmp_path / "s.json"
        )
        assert ok is False
        assert "not found" in errors[0].lower()


class TestGenerateReport:
    def test_all_valid(self):
        results = {"Appendix A": (True, 10, [])}
        report = generate_report(results)
        assert "Appendix A" in report
        assert "Valid" in report
        assert "10" in report

    def test_with_errors(self):
        results = {"Appendix A": (False, 5, ["Error 1", "Error 2"])}
        report = generate_report(results)
        assert "Errors" in report
        assert "Error 1" in report
