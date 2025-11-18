"""
Tests for validate_json.py validator.
"""

import json
import pytest
from scripts.validate_json import (
    load_json_file,
    load_schema,
    validate_records,
    validate_appendix,
    generate_report
)


class TestLoadJsonFile:
    """Tests for load_json_file function."""
    
    def test_load_valid_json_with_metadata(self, tmp_path):
        """Should load JSON and filter out metadata."""
        data = [
            {"_meta": True, "config": "test"},
            {"id": "1", "title": "Record 1"},
            {"id": "2", "title": "Record 2"}
        ]
        
        file = tmp_path / "test.json"
        file.write_text(json.dumps(data), encoding='utf-8')
        
        result = load_json_file(file)
        
        assert len(result) == 2
        assert result[0]["id"] == "1"
        assert result[1]["id"] == "2"
    
    def test_load_json_without_metadata(self, tmp_path):
        """Should handle JSON without metadata."""
        data = [
            {"id": "1", "title": "Record 1"},
            {"id": "2", "title": "Record 2"}
        ]
        
        file = tmp_path / "test.json"
        file.write_text(json.dumps(data), encoding='utf-8')
        
        result = load_json_file(file)
        
        assert len(result) == 2
    
    def test_load_empty_array(self, tmp_path):
        """Should handle empty array."""
        file = tmp_path / "empty.json"
        file.write_text("[]", encoding='utf-8')
        
        result = load_json_file(file)
        
        assert result == []
    
    def test_load_array_with_only_metadata(self, tmp_path):
        """Should return empty list if only metadata present."""
        data = [{"_meta": True, "config": "test"}]
        
        file = tmp_path / "meta_only.json"
        file.write_text(json.dumps(data), encoding='utf-8')
        
        result = load_json_file(file)
        
        assert result == []
    
    def test_invalid_json_raises_error(self, tmp_path):
        """Should raise ValueError for non-array JSON."""
        file = tmp_path / "invalid.json"
        file.write_text('{"not": "an array"}', encoding='utf-8')
        
        with pytest.raises(ValueError, match="Expected array"):
            load_json_file(file)
    
    def test_malformed_json_raises_error(self, tmp_path):
        """Should raise JSONDecodeError for malformed JSON."""
        file = tmp_path / "malformed.json"
        file.write_text("{invalid json}", encoding='utf-8')
        
        with pytest.raises(json.JSONDecodeError):
            load_json_file(file)
    
    def test_utf8_encoding(self, tmp_path):
        """Should handle UTF-8 characters correctly."""
        data = [
            {"id": "1", "title": "Testação Françai§ 中文"}
        ]
        
        file = tmp_path / "utf8.json"
        file.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')
        
        result = load_json_file(file)
        
        assert "Testação" in result[0]["title"]
        assert "中文" in result[0]["title"]


class TestLoadSchema:
    """Tests for load_schema function."""
    
    def test_load_valid_schema(self, tmp_path):
        """Should load valid JSON Schema."""
        schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "id": {"type": "string"}
            }
        }
        
        file = tmp_path / "schema.json"
        file.write_text(json.dumps(schema), encoding='utf-8')
        
        result = load_schema(file)
        
        assert result["type"] == "object"
        assert "properties" in result
    
    def test_load_empty_schema(self, tmp_path):
        """Should handle empty schema object."""
        file = tmp_path / "empty_schema.json"
        file.write_text("{}", encoding='utf-8')
        
        result = load_schema(file)
        
        assert result == {}


class TestValidateRecords:
    """Tests for validate_records function."""
    
    def test_validate_valid_records(self):
        """Should pass validation for valid records."""
        records = [
            {"id": "1", "name": "Alice"},
            {"id": "2", "name": "Bob"}
        ]
        
        schema = {
            "type": "object",
            "required": ["id", "name"],
            "properties": {
                "id": {"type": "string"},
                "name": {"type": "string"}
            }
        }
        
        is_valid, errors = validate_records(records, schema, "test.json")
        
        assert is_valid is True
        assert errors == []
    
    def test_validate_missing_required_field(self):
        """Should detect missing required fields."""
        records = [
            {"id": "1"},  # Missing 'name'
        ]
        
        schema = {
            "type": "object",
            "required": ["id", "name"],
            "properties": {
                "id": {"type": "string"},
                "name": {"type": "string"}
            }
        }
        
        is_valid, errors = validate_records(records, schema, "test.json")
        
        assert is_valid is False
        assert len(errors) > 0
        assert "name" in errors[0].lower() or "required" in errors[0].lower()
    
    def test_validate_wrong_type(self):
        """Should detect type mismatches."""
        records = [
            {"id": 123, "name": "Alice"},  # id should be string
        ]
        
        schema = {
            "type": "object",
            "required": ["id"],
            "properties": {
                "id": {"type": "string"}
            }
        }
        
        is_valid, errors = validate_records(records, schema, "test.json")
        
        assert is_valid is False
        assert len(errors) > 0
    
    def test_validate_empty_records(self):
        """Should handle empty record list."""
        schema = {"type": "object"}
        
        is_valid, errors = validate_records([], schema, "test.json")
        
        assert is_valid is True
        assert errors == []
    
    def test_validate_multiple_errors(self):
        """Should collect all validation errors."""
        records = [
            {"id": 1},           # Wrong type
            {"name": "Alice"},   # Missing id
            {"id": "3"}          # Missing name
        ]
        
        schema = {
            "type": "object",
            "required": ["id", "name"],
            "properties": {
                "id": {"type": "string"},
                "name": {"type": "string"}
            }
        }
        
        is_valid, errors = validate_records(records, schema, "test.json")
        
        assert is_valid is False
        assert len(errors) >= 3  # At least one error per record


class TestValidateAppendix:
    """Tests for validate_appendix function."""
    
    def test_validate_valid_appendix(self, tmp_path):
        """Should validate complete appendix file."""
        data = [
            {"_meta": True, "version": "1.0"},
            {"id": "1", "title": "Test"}
        ]
        
        schema = {
            "type": "object",
            "required": ["id"],
            "properties": {
                "id": {"type": "string"}
            }
        }
        
        json_file = tmp_path / "data.json"
        schema_file = tmp_path / "schema.json"
        
        json_file.write_text(json.dumps(data), encoding='utf-8')
        schema_file.write_text(json.dumps(schema), encoding='utf-8')
        
        is_valid, count, errors = validate_appendix(
            "Test Appendix",
            json_file,
            schema_file
        )
        
        assert is_valid is True
        assert count == 1
        assert errors == []
    
    def test_validate_file_not_found(self, tmp_path):
        """Should handle missing files gracefully."""
        missing_file = tmp_path / "nonexistent.json"
        schema_file = tmp_path / "schema.json"
        schema_file.write_text("{}", encoding='utf-8')
        
        is_valid, count, errors = validate_appendix(
            "Test",
            missing_file,
            schema_file
        )
        
        assert is_valid is False
        assert count == 0
        assert len(errors) > 0
        assert "not found" in errors[0].lower()
    
    def test_validate_invalid_json(self, tmp_path):
        """Should handle malformed JSON."""
        json_file = tmp_path / "bad.json"
        schema_file = tmp_path / "schema.json"
        
        json_file.write_text("{bad json}", encoding='utf-8')
        schema_file.write_text("{}", encoding='utf-8')
        
        is_valid, count, errors = validate_appendix(
            "Test",
            json_file,
            schema_file
        )
        
        assert is_valid is False
        assert count == 0
        assert "invalid json" in errors[0].lower()


class TestGenerateReport:
    """Tests for generate_report function."""
    
    def test_generate_report_all_valid(self):
        """Should generate report for all valid appendices."""
        results = {
            "Appendix A": (True, 100, []),
            "Appendix B": (True, 50, [])
        }
        
        report = generate_report(results)
        
        assert "Appendix A" in report
        assert "Appendix B" in report
        assert "✅ Valid" in report
        assert "100" in report
        assert "50" in report
    
    def test_generate_report_with_errors(self):
        """Should generate report showing errors."""
        results = {
            "Appendix A": (False, 10, ["Error 1", "Error 2"])
        }
        
        report = generate_report(results)
        
        assert "❌ Errors" in report
        assert "Error 1" in report
        assert "Error 2" in report
        assert "10" in report
    
    def test_generate_report_truncates_long_error_list(self):
        """Should truncate error list if too long."""
        errors = [f"Error {i}" for i in range(20)]
        results = {
            "Appendix A": (False, 20, errors)
        }
        
        report = generate_report(results)
        
        assert "Error 0" in report
        assert "Error 9" in report
        assert "... and 10 more errors" in report
    
    def test_generate_report_markdown_format(self):
        """Should generate valid markdown."""
        results = {
            "Test Appendix": (True, 5, [])
        }
        
        report = generate_report(results)
        
        assert report.startswith("# ELIS Validation Report")
        assert "##" in report  # Has headers
        assert "**" in report  # Has bold text
        assert "-" in report   # Has list items


class TestMain:
    """Tests for main() function."""
    
    def test_main_validates_all_appendices(self, tmp_path, monkeypatch):
        """Should validate all three appendices."""
        # Change to temp directory
        monkeypatch.chdir(tmp_path)
        
        # Create directory structure
        (tmp_path / "json_jsonl").mkdir()
        (tmp_path / "schemas").mkdir()
        (tmp_path / "validation_reports").mkdir()
        
        # Create valid data files
        for letter in ['A', 'B', 'C']:
            data = [
                {"_meta": True, "version": "1.0"},
                {"id": f"{letter}1", "source": "test", "retrieved_at": "2025-11-14T12:00:00Z", 
                 "query_topic": "test", "query_string": "test"}
            ]
            
            if letter == 'A':
                filename = "ELIS_Appendix_A_Search_rows.json"
                schema_name = "appendix_a.schema.json"
            elif letter == 'B':
                filename = "ELIS_Appendix_B_Screening_rows.json"
                schema_name = "appendix_b.schema.json"
            else:
                filename = "ELIS_Appendix_C_Extraction_rows.json"
                schema_name = "appendix_c.schema.json"
            
            json_file = tmp_path / "json_jsonl" / filename
            json_file.write_text(json.dumps(data), encoding='utf-8')
            
            # Create minimal schema
            schema = {
                "type": "object",
                "required": ["id", "source", "retrieved_at", "query_topic", "query_string"],
                "properties": {
                    "id": {"type": "string"},
                    "source": {"type": "string"},
                    "retrieved_at": {"type": "string"},
                    "query_topic": {"type": "string"},
                    "query_string": {"type": "string"}
                }
            }
            
            schema_file = tmp_path / "schemas" / schema_name
            schema_file.write_text(json.dumps(schema), encoding='utf-8')
        
        # Import and run main - it calls sys.exit(0)
        from scripts.validate_json import main
        
        # Expect sys.exit(0) for successful validation
        with pytest.raises(SystemExit) as excinfo:
            main()
        
        assert excinfo.value.code == 0
        
        # Check reports were created
        assert (tmp_path / "validation_reports" / "validation-report.md").exists()
        
        # Check for timestamped report
        report_files = list((tmp_path / "validation_reports").glob("*_validation_report.md"))
        assert len(report_files) >= 1
    
    def test_main_handles_missing_files(self, tmp_path, monkeypatch):
        """Should handle missing files gracefully."""
        monkeypatch.chdir(tmp_path)
        
        # Create only directory structure, no files
        (tmp_path / "json_jsonl").mkdir()
        (tmp_path / "schemas").mkdir()
        (tmp_path / "validation_reports").mkdir()
        
        from scripts.validate_json import main
        
        # Should exit gracefully even with missing files
        with pytest.raises(SystemExit) as excinfo:
            main()
        
        assert excinfo.value.code == 0


class TestIntegration:
    """Integration tests using real-world scenarios."""
    
    def test_full_validation_workflow(self, tmp_path):
        """Should validate complete workflow from file to report."""
        # Create realistic data
        data = [
            {
                "_meta": True,
                "protocol_version": "ELIS 2025",
                "record_count": 2
            },
            {
                "id": "doi:10.1234/test1",
                "title": "Test Paper 1",
                "year": 2025,
                "source": "scopus",
                "retrieved_at": "2025-11-14T12:00:00Z",
                "query_topic": "test",
                "query_string": "test query"
            },
            {
                "id": "doi:10.1234/test2",
                "title": "Test Paper 2",
                "year": 2024,
                "source": "scopus",
                "retrieved_at": "2025-11-14T12:00:00Z",
                "query_topic": "test",
                "query_string": "test query"
            }
        ]
        
        # Create simple schema
        schema = {
            "type": "object",
            "required": ["id", "source", "retrieved_at", "query_topic", "query_string"],
            "properties": {
                "id": {"type": "string"},
                "title": {"type": ["string", "null"]},
                "year": {"type": ["integer", "null"]},
                "source": {"type": "string"},
                "retrieved_at": {"type": "string"},
                "query_topic": {"type": "string"},
                "query_string": {"type": "string"}
            }
        }
        
        json_file = tmp_path / "appendix.json"
        schema_file = tmp_path / "schema.json"
        
        json_file.write_text(json.dumps(data), encoding='utf-8')
        schema_file.write_text(json.dumps(schema), encoding='utf-8')
        
        # Run validation
        is_valid, count, errors = validate_appendix(
            "Integration Test",
            json_file,
            schema_file
        )
        
        # Assert results
        assert is_valid is True
        assert count == 2  # Metadata filtered out
        assert errors == []
        
        # Generate report
        results = {"Test Appendix": (is_valid, count, errors)}
        report = generate_report(results)
        
        assert "Test Appendix" in report
        assert "✅ Valid" in report
        assert "2" in report
        