#!/usr/bin/env python3
"""
ELIS Benchmark Adapter

Converts benchmark configuration to ELIS format and executes searches.
Acts as a bridge between run_benchmark.py and ELIS search_mvp.py.

Author: Carlos Rocha
Date: 2026-01-26
"""

import sys
import yaml
import json
from pathlib import Path
from typing import Dict, List
import pandas as pd
from datetime import datetime

# Add project paths
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "elis"))


class BenchmarkElisAdapter:
    """Adapts benchmark config to ELIS search execution."""

    def __init__(self, benchmark_config: Dict):
        """Initialize with benchmark configuration."""
        self.config = benchmark_config
        self.results = []

    def create_elis_query_config(self) -> Dict:
        """
        Create ELIS-compatible query configuration for benchmark.

        Converts benchmark boolean string into ELIS config/elis_search_queries.yml format.
        """
        search_params = self.config["search_parameters"]

        # Extract dates
        start_year = int(search_params["date_range"]["start"].split("-")[0])
        end_year = int(search_params["date_range"]["end"].split("-")[0])

        # Create ELIS-compatible config
        elis_config = {
            "global": {
                "year_from": start_year,
                "year_to": end_year,
                "languages": ["en"],  # Benchmark is English only
                "max_results_per_source": 500,  # Higher limit for benchmark
                "job_result_cap": 0,  # Unlimited
            },
            "topics": [
                {
                    "id": "benchmark_darmawan_2021",
                    "enabled": True,
                    "description": "E-voting adoption benchmark (Darmawan 2021)",
                    "queries": [
                        # Split the boolean string into individual queries
                        search_params["search_terms"]["boolean_string"]
                    ],
                    "include_preprints": False,
                    "sources": search_params["databases"],
                }
            ],
        }

        return elis_config

    def save_temp_config(self, elis_config: Dict) -> Path:
        """Save temporary ELIS config file for benchmark."""
        temp_config_path = PROJECT_ROOT / "config" / "benchmark_temp_queries.yml"

        with open(temp_config_path, "w", encoding="utf-8") as f:
            yaml.dump(elis_config, f, default_flow_style=False, allow_unicode=True)

        print(f"✓ Created temporary ELIS config: {temp_config_path}")
        return temp_config_path

    def execute_search(self) -> pd.DataFrame:
        """
        Execute ELIS search with benchmark parameters.

        Returns DataFrame with search results.
        """
        print("\n🔍 Executing ELIS search for benchmark...")
        print(
            f"   Period: {self.config['search_parameters']['date_range']['start']} to {self.config['search_parameters']['date_range']['end']}"
        )
        print(
            f"   Databases: {', '.join(self.config['search_parameters']['databases'])}"
        )

        try:
            # Create ELIS-compatible config
            elis_config = self.create_elis_query_config()
            temp_config_path = self.save_temp_config(elis_config)

            # Import and run ELIS search
            print("\n⚠️  ELIS search integration pending:")
            print("   The search_mvp.py script needs to be called with:")
            print(f"   - Config: {temp_config_path}")
            print(f"   - Output: json_jsonl/ELIS_Appendix_A_Search_rows.json")
            print("\n   To complete integration:")
            print("   1. Modify search_mvp.py to accept config path parameter")
            print("   2. Call it from this adapter")
            print("   3. Parse the output JSON")

            # TODO: Complete integration
            # Option 1: Subprocess call
            # import subprocess
            # result = subprocess.run(
            #     ['python', 'scripts/elis/search_mvp.py', '--config', str(temp_config_path)],
            #     cwd=PROJECT_ROOT,
            #     capture_output=True
            # )

            # Option 2: Direct import and call
            # from search_mvp import main as run_elis_search
            # run_elis_search(config_path=str(temp_config_path))

            # For now, return empty DataFrame
            return pd.DataFrame()

        except Exception as e:
            print(f"❌ Error executing ELIS search: {e}")
            import traceback

            traceback.print_exc()
            return pd.DataFrame()

    def load_elis_results(self, output_path: Path = None) -> pd.DataFrame:
        """
        Load results from ELIS output JSON.

        Args:
            output_path: Path to search results JSON
        """
        if output_path is None:
            # Try benchmark results first, fall back to ELIS results
            benchmark_path = (
                PROJECT_ROOT / "json_jsonl" / "benchmark_search_results.json"
            )
            elis_path = PROJECT_ROOT / "json_jsonl" / "ELIS_Appendix_A_Search_rows.json"

            if benchmark_path.exists():
                output_path = benchmark_path
                print(f"✓ Using benchmark search results: {benchmark_path}")
            elif elis_path.exists():
                output_path = elis_path
                print(f"✓ Using ELIS results: {elis_path}")
            else:
                print("⚠️  No results files found")
                return pd.DataFrame()

        if not output_path.exists():
            print(f"⚠️  Results file not found: {output_path}")
            return pd.DataFrame()

        try:
            with open(output_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # First item is metadata
            if data and isinstance(data[0], dict) and data[0].get("_meta"):
                metadata = data[0]
                records = data[1:]
                print(f"✓ Loaded {len(records)} records")
                print(f"   Metadata: {metadata.get('protocol_version', 'unknown')}")
            else:
                records = data

            # Convert to DataFrame
            df = pd.DataFrame(records)
            return df

        except Exception as e:
            print(f"❌ Error loading results: {e}")
            import traceback

            traceback.print_exc()
            return pd.DataFrame()

    def normalize_results(self, elis_df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize ELIS results to benchmark matching format.

        Expected ELIS columns:
        - id, title, authors, year, doi, source, venue, abstract, etc.
        """
        if elis_df.empty:
            return elis_df

        # Create normalized DataFrame for matching
        normalized = pd.DataFrame()

        # Direct column mapping
        if "title" in elis_df.columns:
            normalized["title"] = elis_df["title"]
            normalized["title_normalized"] = (
                elis_df["title"]
                .str.lower()
                .str.strip()
                .str.replace(r"[^\w\s]", "", regex=True)
            )

        if "authors" in elis_df.columns:
            # ELIS authors is a list, convert to string
            normalized["authors"] = elis_df["authors"].apply(
                lambda x: ", ".join(x) if isinstance(x, list) else str(x)
            )
            normalized["authors_normalized"] = normalized["authors"].str.lower()

        if "year" in elis_df.columns:
            normalized["year"] = elis_df["year"]

        if "doi" in elis_df.columns:
            normalized["doi"] = elis_df["doi"]

        if "venue" in elis_df.columns:
            normalized["journal"] = elis_df["venue"]

        if "source" in elis_df.columns:
            normalized["database_source"] = elis_df["source"]

        # Keep original ELIS fields
        normalized["elis_id"] = elis_df.get("id", None)
        normalized["elis_source_id"] = elis_df.get("source_id", None)

        return normalized


def run_benchmark_search(benchmark_config: Dict) -> pd.DataFrame:
    """
    Main entry point for benchmark script.

    Args:
        benchmark_config: Benchmark configuration dict

    Returns:
        DataFrame with normalized search results
    """
    adapter = BenchmarkElisAdapter(benchmark_config)

    # Execute search (currently placeholder)
    raw_results = adapter.execute_search()

    # If search was executed, load and normalize results
    if not raw_results.empty:
        normalized = adapter.normalize_results(raw_results)
        return normalized

    # Try loading existing results if available
    elis_results = adapter.load_elis_results()
    if not elis_results.empty:
        print("✓ Using existing ELIS results")
        normalized = adapter.normalize_results(elis_results)
        return normalized

    # No results available
    print("⚠️  No ELIS results available - returning empty DataFrame")
    return pd.DataFrame()


if __name__ == "__main__":
    """Test the adapter independently."""

    # Load benchmark config
    config_path = PROJECT_ROOT / "configs" / "benchmark_config.yaml"
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    print("=" * 70)
    print("Testing ELIS Benchmark Adapter")
    print("=" * 70)

    # Test config creation
    adapter = BenchmarkElisAdapter(config)
    elis_config = adapter.create_elis_query_config()

    print("\nGenerated ELIS Config:")
    print(yaml.dump(elis_config, default_flow_style=False))

    # Test search execution
    results = run_benchmark_search(config)
    print(f"\nTest complete: {len(results)} results")

    if not results.empty:
        print("\nSample results:")
        print(results.head())
