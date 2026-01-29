"""
benchmark_2_integration.py

Integrates benchmark-2 (Tai & Awasthi 2025) with ELIS harvest scripts.
Executes searches across all available databases and performs matching.

This is the bridge between the benchmark runner and ELIS harvest scripts.
"""

import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime

# Add parent directory to path to import ELIS modules
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

# Import benchmark runner
sys.path.insert(0, str(Path(__file__).parent))
from benchmark_2_runner import Benchmark2Executor, FuzzyMatcher

# Database harvest script mapping
HARVEST_SCRIPTS = {
    "Scopus": "scopus_harvest.py",
    "Web of Science": "wos_harvest.py",
    "OpenAlex": "openalex_harvest.py",
    "CrossRef": "crossref_harvest.py",
    "Google Scholar": None,  # Not implemented in ELIS yet
    "Semantic Scholar": "semanticscholar_harvest.py",
    "CORE": "core_harvest.py",
    "IEEE Xplore": "ieee_harvest.py"
}

class ELISBenchmark2Bridge:
    """Bridge between ELIS harvest scripts and Benchmark 2 runner"""
    
    def __init__(self):
        self.repo_root = REPO_ROOT
        self.scripts_dir = self.repo_root / "scripts"
        self.output_file = self.repo_root / "json_jsonl" / "ELIS_Appendix_A_Search_rows.json"
    
    def call_harvest_script(self, database_name: str, query: str):
        """
        Call an ELIS harvest script for a specific database.
        
        Note: This is a placeholder. In production, you would:
        1. Temporarily modify config/elis_search_queries.yml with benchmark query
        2. Call the harvest script
        3. Read results from json_jsonl/ELIS_Appendix_A_Search_rows.json
        4. Restore original config
        """
        script_name = HARVEST_SCRIPTS.get(database_name)
        
        if not script_name:
            print(f"  [SKIP] {database_name} - No harvest script available")
            return []
        
        script_path = self.scripts_dir / script_name
        
        if not script_path.exists():
            print(f"  [ERROR] {database_name} - Script not found: {script_path}")
            return []
        
        print(f"  [TODO] {database_name} - Would call: {script_name}")
        print(f"         Query: {query}")
        print(f"         (Implementation needed: modify config, run script, parse results)")
        
        # TODO: Actual implementation
        # 1. Backup current config
        # 2. Write benchmark query to config
        # 3. Run: subprocess.run([sys.executable, str(script_path)])
        # 4. Read results from output_file
        # 5. Restore config
        
        return []  # Placeholder

def main():
    """Main execution function"""
    print("\n" + "="*80)
    print("ELIS BENCHMARK 2 - INTEGRATION WITH ELIS HARVEST SCRIPTS")
    print("="*80 + "\n")
    
    # Initialize bridge
    bridge = ELISBenchmark2Bridge()
    
    print("Repository root:", bridge.repo_root)
    print("Scripts directory:", bridge.scripts_dir)
    print("Output file:", bridge.output_file)
    print()
    
    # Show available databases
    print("Available ELIS Harvest Scripts:")
    print("-" * 80)
    for db, script in HARVEST_SCRIPTS.items():
        status = "✓" if script else "✗"
        print(f"  {status} {db:20s} → {script if script else 'Not available'}")
    
    print()
    print("="*80)
    print("INTEGRATION STATUS: PENDING")
    print("="*80)
    print()
    print("Next steps:")
    print("1. Implement config file modification in call_harvest_script()")
    print("2. Add proper error handling and result parsing")
    print("3. Integrate with benchmark_2_runner.py matching logic")
    print("4. Test with single database first (e.g., OpenAlex)")
    print("5. Run full benchmark with all databases")
    print()

if __name__ == "__main__":
    main()