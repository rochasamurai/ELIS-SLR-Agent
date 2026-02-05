"""
benchmark_2_integration.py

Integrates benchmark-2 (Tai & Awasthi 2025) with ELIS harvest scripts.
Executes searches across all available databases and performs matching.

This is the bridge between the benchmark runner and ELIS harvest scripts.
"""

import sys
import json
import yaml
import shutil
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# Add parent directory to path to import ELIS modules
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

# Add benchmark-2 directory to path
BENCHMARK_DIR = Path(__file__).parent
sys.path.insert(0, str(BENCHMARK_DIR))

# Import benchmark runner
from benchmark_2_runner import Benchmark2Executor, FuzzyMatcher

# Database harvest script mapping
HARVEST_SCRIPTS = {
    "Scopus": "scopus_harvest.py",
    "Web of Science": "wos_harvest.py",
    "OpenAlex": "openalex_harvest.py",
    "CrossRef": "crossref_harvest.py",
    "Google Scholar": "google_scholar_harvest.py",
    "Semantic Scholar": "semanticscholar_harvest.py",
    "CORE": "core_harvest.py",
    "IEEE Xplore": "ieee_harvest.py",
}


class ELISBenchmark2Bridge:
    """Bridge between ELIS harvest scripts and Benchmark 2 runner"""

    def __init__(self, config_file: str = "configs/benchmark_2_config.yaml"):
        self.repo_root = REPO_ROOT
        self.scripts_dir = self.repo_root / "scripts"
        self.config_dir = self.repo_root / "config"
        self.output_file = (
            self.repo_root / "json_jsonl" / "ELIS_Appendix_A_Search_rows.json"
        )

        # Benchmark config
        self.benchmark_config_file = Path(__file__).parent / config_file
        self.benchmark_config = self.load_benchmark_config()

        # ELIS config
        self.elis_config_file = self.config_dir / "elis_search_queries.yml"
        self.elis_config_backup = self.config_dir / "elis_search_queries.yml.backup"

    def load_benchmark_config(self) -> Dict:
        """Load benchmark configuration"""
        with open(self.benchmark_config_file, "r") as f:
            return yaml.safe_load(f)

    def backup_elis_config(self):
        """Backup original ELIS config"""
        if self.elis_config_file.exists():
            shutil.copy(self.elis_config_file, self.elis_config_backup)
            print(f"✓ Backed up ELIS config to {self.elis_config_backup}")

    def restore_elis_config(self):
        """Restore original ELIS config"""
        if self.elis_config_backup.exists():
            shutil.copy(self.elis_config_backup, self.elis_config_file)
            print(f"✓ Restored ELIS config from backup")
            self.elis_config_backup.unlink()  # Delete backup

    def create_benchmark_elis_config(self, database_name: str) -> Dict:
        """
        Create ELIS config for benchmark query.

        Returns the config dict that will be written to YAML.
        """
        # Get benchmark search strategy
        search_strategy = self.benchmark_config["search_strategy"]
        query = search_strategy["query_string"].strip()
        date_start = search_strategy["date_range"]["start"]
        date_end = search_strategy["date_range"]["end"]

        # Map database names to ELIS source identifiers
        source_mapping = {
            "Scopus": "scopus",
            "Web of Science": "web_of_science",
            "OpenAlex": "openalex",
            "CrossRef": "crossref",
            "Google Scholar": "google_scholar",
            "Semantic Scholar": "semantic_scholar",
            "CORE": "core",
            "IEEE Xplore": "ieee_xplore",
        }

        source_id = source_mapping.get(
            database_name, database_name.lower().replace(" ", "_")
        )

        # Create ELIS config
        elis_config = {
            "global": {
                "year_from": int(date_start.split("-")[0]),
                "year_to": int(date_end.split("-")[0]),
                "languages": ["en"],
                "max_results_per_source": 500,  # Increased for benchmark
                "job_result_cap": 0,  # Unlimited for benchmark
            },
            "topics": [
                {
                    "id": "benchmark_tai_awasthi_2025",
                    "enabled": True,
                    "description": f"Benchmark query for Tai & Awasthi (2025) - {database_name}",
                    "queries": [query],
                    "include_preprints": False,
                    "sources": [source_id],
                }
            ],
        }

        return elis_config

    def write_elis_config(self, config: Dict):
        """Write config to ELIS config file"""
        with open(self.elis_config_file, "w") as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)
        print(f"✓ Wrote benchmark config to {self.elis_config_file}")

    def call_harvest_script(self, database_name: str) -> List[Dict]:
        """
        Call an ELIS harvest script for a specific database.

        Returns list of retrieved results.
        """
        script_name = HARVEST_SCRIPTS.get(database_name)

        if not script_name:
            print(f"  [SKIP] {database_name} - No harvest script available")
            return []

        script_path = self.scripts_dir / script_name

        if not script_path.exists():
            print(f"  [ERROR] {database_name} - Script not found: {script_path}")
            return []

        print(f"\n{'='*80}")
        print(f"SEARCHING: {database_name}")
        print(f"{'='*80}")

        try:
            # 1. Backup current ELIS config
            self.backup_elis_config()

            # 2. Write benchmark config
            benchmark_config = self.create_benchmark_elis_config(database_name)
            self.write_elis_config(benchmark_config)

            # 3. Clear previous results
            if self.output_file.exists():
                self.output_file.unlink()
                print(f"✓ Cleared previous results")

            # 4. Run harvest script
            print(f"\n▶ Running: {script_name}")
            result = subprocess.run(
                [sys.executable, str(script_path)],
                cwd=str(self.repo_root),
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout per database
            )

            # 5. Check for errors
            if result.returncode != 0:
                print(f"  ✗ ERROR: Script failed with return code {result.returncode}")
                print(f"  STDERR: {result.stderr}")
                return []

            print(f"  ✓ Script completed successfully")

            # 6. Read results
            if not self.output_file.exists():
                print(f"  ⚠ No results file generated")
                return []

            with open(self.output_file, "r", encoding="utf-8") as f:
                results = json.load(f)

            print(f"  ✓ Retrieved: {len(results)} results")

            # 7. Transform to benchmark format
            formatted_results = []
            for result in results:
                formatted_results.append(
                    {
                        "title": result.get("title", ""),
                        "authors": result.get("authors", ""),
                        "year": result.get("year", ""),
                        "journal": result.get("journal", result.get("source", "")),
                        "doi": result.get("doi", ""),
                        "abstract": result.get("abstract", ""),
                        "source_database": database_name,
                        "raw_metadata": result,
                    }
                )

            return formatted_results

        except subprocess.TimeoutExpired:
            print(f"  ✗ TIMEOUT: Script exceeded 5 minute limit")
            return []

        except Exception as e:
            print(f"  ✗ ERROR: {type(e).__name__}: {e}")
            return []

        finally:
            # 8. Always restore original config
            self.restore_elis_config()

    def execute_benchmark(self, databases: List[str] = None) -> Dict:
        """
        Execute benchmark across specified databases.

        Args:
            databases: List of database names to search. If None, uses all available.

        Returns:
            Dict with benchmark results
        """
        if databases is None:
            # Use Phase 1 databases from config
            databases = self.benchmark_config["execution"]["phases"]["phase1"][
                "databases"
            ]

        print("\n" + "=" * 80)
        print("ELIS BENCHMARK 2 - PHASE 1 EXECUTION")
        print("Paper: Tai & Awasthi (2025) - Agile Government")
        print("=" * 80)
        print(f"\nDatabases to search: {', '.join(databases)}")
        print(
            f"Gold standard studies: {self.benchmark_config['validation']['gold_standard']['count']}"
        )

        # Execute searches
        all_results = []
        db_contribution = {}

        start_time = datetime.now()

        for db in databases:
            results = self.call_harvest_script(db)
            all_results.extend(results)
            db_contribution[db] = len(results)

        print("\n" + "=" * 80)
        print("SEARCH COMPLETE")
        print("=" * 80)
        print(f"\nTotal retrieved (with duplicates): {len(all_results)}")

        # Deduplication
        print("\nDEDUPLICATION")
        print("-" * 80)
        unique_results = self.deduplicate(all_results)
        print(f"After deduplication: {len(unique_results)}")

        # Matching
        print("\nMATCHING AGAINST GOLD STANDARD")
        print("-" * 80)

        # Load gold standard
        gold_standard_file = (
            Path(__file__).parent
            / self.benchmark_config["validation"]["gold_standard"]["file"]
        )
        with open(gold_standard_file, "r", encoding="utf-8") as f:
            gold_standard = json.load(f)

        matched, missed = self.match_studies(gold_standard, unique_results)

        # Calculate metrics
        total_matched = len(matched)
        retrieval_rate = total_matched / len(gold_standard)
        precision = total_matched / len(unique_results) if unique_results else 0
        recall = retrieval_rate
        f1 = (
            2 * (precision * recall) / (precision + recall)
            if (precision + recall) > 0
            else 0
        )

        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()

        print(f"\nMatched: {total_matched}/{len(gold_standard)} ({retrieval_rate:.1%})")
        print(f"Precision: {precision:.1%}")
        print(f"Recall: {recall:.1%}")
        print(f"F1 Score: {f1:.3f}")
        print(f"\nExecution time: {execution_time:.2f} seconds")

        # Prepare results
        result = {
            "benchmark_id": "TAI_AWASTHI_2025",
            "phase": "PHASE_1",
            "execution_date": start_time.isoformat(),
            "total_gold_standard": len(gold_standard),
            "total_retrieved": len(unique_results),
            "total_matched": total_matched,
            "retrieval_rate": retrieval_rate,
            "precision": precision,
            "recall": recall,
            "f1_score": f1,
            "execution_time_seconds": execution_time,
            "databases_used": databases,
            "database_contribution": db_contribution,
            "matched_studies": matched,
            "missed_studies": missed,
        }

        return result

    def deduplicate(self, studies: List[Dict]) -> List[Dict]:
        """Remove duplicate studies"""
        seen_titles = set()
        unique = []

        for study in studies:
            norm_title = FuzzyMatcher.normalize_text(study.get("title", ""))
            if norm_title and norm_title not in seen_titles:
                seen_titles.add(norm_title)
                unique.append(study)

        return unique

    def match_studies(self, gold_standard: List[Dict], retrieved: List[Dict]) -> tuple:
        """Match retrieved studies against gold standard"""
        matched = []
        missed = []

        for gold_study in gold_standard:
            found = False

            for retrieved_study in retrieved:
                if FuzzyMatcher.match_study(gold_study, retrieved_study):
                    matched.append(
                        {
                            "gold_standard_id": gold_study["reference_id"],
                            "title": gold_study["title"],
                            "authors": gold_study["authors"],
                            "year": gold_study["year"],
                            "matched_title": retrieved_study["title"],
                            "source_database": retrieved_study.get(
                                "source_database", "Unknown"
                            ),
                        }
                    )
                    found = True
                    break

            if not found:
                missed.append(
                    {
                        "reference_id": gold_study["reference_id"],
                        "title": gold_study["title"],
                        "authors": gold_study["authors"],
                        "year": gold_study["year"],
                    }
                )

        return matched, missed

    def save_results(self, result: Dict):
        """Save results to files"""
        results_dir = Path(__file__).parent / "results"
        results_dir.mkdir(exist_ok=True)

        print("\n" + "=" * 80)
        print("SAVING RESULTS")
        print("=" * 80)

        # JSON results
        json_file = results_dir / "benchmark_2_phase1_results.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
        print(f"✓ Saved: {json_file}")

        # Matched studies
        matched_file = results_dir / "benchmark_2_matched_studies.json"
        with open(matched_file, "w", encoding="utf-8") as f:
            json.dump(result["matched_studies"], f, indent=2)
        print(f"✓ Saved: {matched_file}")

        # Missed studies
        missed_file = results_dir / "benchmark_2_missed_studies.json"
        with open(missed_file, "w", encoding="utf-8") as f:
            json.dump(result["missed_studies"], f, indent=2)
        print(f"✓ Saved: {missed_file}")


def main():
    """Main execution function"""
    print("\n" + "=" * 80)
    print("ELIS BENCHMARK 2 - INTEGRATION WITH ELIS HARVEST SCRIPTS")
    print("=" * 80 + "\n")

    # Initialize bridge
    bridge = ELISBenchmark2Bridge()

    # Execute benchmark with Phase 1 databases
    result = bridge.execute_benchmark()

    # Save results
    bridge.save_results(result)

    print("\n" + "=" * 80)
    print("BENCHMARK EXECUTION COMPLETE")
    print("=" * 80)
    print(f"\nRetrieval Rate: {result['retrieval_rate']:.1%}")
    print(
        f"Status: {'✓ SUCCESS' if result['retrieval_rate'] >= 0.50 else '✗ BELOW MINIMUM'}"
    )
    print()


if __name__ == "__main__":
    main()
