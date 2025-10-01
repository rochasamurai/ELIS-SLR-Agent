"""
Smoke tests for Step B agent output (screening decisions).
Ensures the agent outputs contain the expected fields and structure.
"""
import json
from scripts import agent

def test_step_b_outputs(tmp_path):
    # Use a temporary directory for agent output files.
    temp_dir = tmp_path / "json_jsonl"
    temp_dir.mkdir()

    # Override agent file paths to use the temporary directory.
    agent.ART_DIR = temp_dir
    agent.A_FILE = temp_dir / "ELIS_Appendix_A_Search_rows.json"
    agent.B_FILE = temp_dir / "ELIS_Appendix_B_Screening_rows.json"
    agent.C_FILE = temp_dir / "ELIS_Appendix_C_Extraction_rows.json"

    # Create a dummy Appendix A input file for the agent to process.
    sample_search_data = [
        {
            "id": "A-TEST1",
            "search_query": "test query",
            "source": "UnitTest",
            "executed_at": "2025-01-01T00:00:00Z"
        }
    ]
    agent.A_FILE.write_text(json.dumps(sample_search_data))

    # Run the agent to produce outputs.
    result = agent.run()

    # The result should be a dict with keys 'a', 'b', 'c'.
    assert isinstance(result, dict)
    assert "a" in result and "b" in result and "c" in result

    # The 'a' list should reflect the input search data.
    assert result["a"] and result["a"][0]["id"] == "A-TEST1"

    # There should be at least one included and one excluded decision in 'b'.
    decisions = {entry.get("decision") for entry in result["b"]}
    assert "included" in decisions
    assert "excluded" in decisions

    # Every screening entry should have 'decision' and 'reason' fields.
    for entry in result["b"]:
        assert "decision" in entry
        assert "reason" in entry
        assert entry["decision"] in ("included", "excluded")
        if entry["decision"] == "excluded":
            # Excluded entries must include a non-empty reason.
            assert entry["reason"]

    # Each included screening entry should have a corresponding extraction entry.
    included_ids = [entry["id"] for entry in result["b"] if entry["decision"] == "included"]
    assert included_ids, "Expected at least one included screening entry"
    for ext in result["c"]:
        assert ext["screening_id"] in included_ids
        # Extraction entries should contain required fields.
        assert "key_findings" in ext
        assert "extracted_at" in ext

    # Verify that output files were created and match the returned data.
    for file_path, data in [
        (agent.A_FILE, result["a"]),
        (agent.B_FILE, result["b"]),
        (agent.C_FILE, result["c"]),
    ]:
        assert file_path.exists(), f"Output file not found: {file_path}"
        loaded_data = json.loads(file_path.read_text())
        assert loaded_data == data
