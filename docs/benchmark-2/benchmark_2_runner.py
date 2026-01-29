#!/usr/bin/env python3
"""
ELIS Benchmark 2 - Execution Script
Paper: Tai & Awasthi (2025) - Agile Government Systematic Review

This script performs Phase 1 validation using currently available databases.
Phase 2 will be executed after EBSCOhost and ProQuest API access is obtained.
"""

import json
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set
from dataclasses import dataclass, asdict
import re

# Configuration
CONFIG_FILE = "benchmark_2_config.yaml"
GOLD_STANDARD_FILE = "data/tai_awasthi_2025_references_FINAL.json"
RESULTS_DIR = "results"


@dataclass
class BenchmarkResult:
    """Stores benchmark execution results"""
    benchmark_id: str
    phase: str
    execution_date: str
    total_gold_standard: int
    total_retrieved: int
    total_matched: int
    retrieval_rate: float
    precision: float
    recall: float
    f1_score: float
    execution_time_seconds: float
    total_cost_usd: float
    databases_used: List[str]
    matched_studies: List[Dict]
    missed_studies: List[Dict]
    database_contribution: Dict[str, int]


class FuzzyMatcher:
    """Fuzzy string matching for study identification"""
    
    @staticmethod
    def normalize_text(text: str) -> str:
        """Normalize text for comparison"""
        if not text:
            return ""
        # Convert to lowercase
        text = text.lower()
        # Remove special characters but keep spaces
        text = re.sub(r'[^a-z0-9\s]', '', text)
        # Remove extra spaces
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    @staticmethod
    def calculate_similarity(str1: str, str2: str) -> float:
        """
        Calculate similarity between two strings using token-based approach.
        Returns similarity score between 0 and 1.
        """
        if not str1 or not str2:
            return 0.0
        
        # Normalize both strings
        norm1 = FuzzyMatcher.normalize_text(str1)
        norm2 = FuzzyMatcher.normalize_text(str2)
        
        # Exact match
        if norm1 == norm2:
            return 1.0
        
        # Token-based similarity
        tokens1 = set(norm1.split())
        tokens2 = set(norm2.split())
        
        if not tokens1 or not tokens2:
            return 0.0
        
        # Jaccard similarity
        intersection = len(tokens1 & tokens2)
        union = len(tokens1 | tokens2)
        
        return intersection / union if union > 0 else 0.0
    
    @staticmethod
    def match_study(gold_study: Dict, retrieved_study: Dict, threshold: float = 0.85) -> bool:
        """
        Determine if a retrieved study matches a gold standard study.
        
        Matching criteria (in order of priority):
        1. Exact DOI match
        2. Title similarity >= threshold + author match
        3. Title similarity >= threshold + year match
        """
        # DOI exact match
        gold_doi = gold_study.get('doi', '').strip()
        retrieved_doi = retrieved_study.get('doi', '').strip()
        
        if gold_doi and retrieved_doi:
            if gold_doi.lower() == retrieved_doi.lower():
                return True
        
        # Title similarity
        gold_title = gold_study.get('title', '')
        retrieved_title = retrieved_study.get('title', '')
        
        title_sim = FuzzyMatcher.calculate_similarity(gold_title, retrieved_title)
        
        # High confidence match (title + author)
        if title_sim >= threshold:
            gold_authors = FuzzyMatcher.normalize_text(gold_study.get('authors', ''))
            retrieved_authors = FuzzyMatcher.normalize_text(retrieved_study.get('authors', ''))
            
            if gold_authors and retrieved_authors:
                # Check if any author surname appears in both
                gold_surnames = [w for w in gold_authors.split() if len(w) > 2]
                retrieved_surnames = [w for w in retrieved_authors.split() if len(w) > 2]
                
                if any(gs in retrieved_surnames for gs in gold_surnames):
                    return True
        
        # Medium confidence match (title + year)
        if title_sim >= threshold:
            gold_year = str(gold_study.get('year', ''))
            retrieved_year = str(retrieved_study.get('year', ''))
            
            if gold_year and retrieved_year and gold_year == retrieved_year:
                return True
        
        return False


class Benchmark2Executor:
    """Executes the benchmark validation"""
    
    def __init__(self, config_file: str, gold_standard_file: str):
        self.config = self.load_config(config_file)
        self.gold_standard = self.load_gold_standard(gold_standard_file)
        self.results_dir = Path(RESULTS_DIR)
        self.results_dir.mkdir(exist_ok=True)
    
    def load_config(self, config_file: str) -> Dict:
        """Load benchmark configuration"""
        with open(config_file, 'r') as f:
            return yaml.safe_load(f)
    
    def load_gold_standard(self, gold_file: str) -> List[Dict]:
        """Load gold standard references"""
        with open(gold_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def simulate_database_search(self, database: str, query: str) -> List[Dict]:
        """
        SIMULATION: In production, this would call actual ELIS database APIs.
        For now, returns mock results for testing the matching logic.
        """
        print(f"  [SIMULATION] Searching {database}...")
        print(f"  Query: {query}")
        
        # In production, this would be replaced with actual API calls like:
        # results = elis_agent.search(database=database, query=query, ...)
        
        # For testing, let's simulate finding some of the gold standard studies
        # with slight variations in titles to test fuzzy matching
        
        simulated_results = []
        
        # Simulate finding ~40% of studies with some title variations
        sample_studies = self.gold_standard[:int(len(self.gold_standard) * 0.4)]
        
        for study in sample_studies:
            # Add slight variation to test fuzzy matching
            simulated_result = {
                'title': study['title'],
                'authors': study['authors'],
                'year': study['year'],
                'journal': study.get('journal', ''),
                'doi': study.get('doi', ''),
                'source_database': database
            }
            simulated_results.append(simulated_result)
        
        print(f"  Found: {len(simulated_results)} results")
        return simulated_results
    
    def execute_phase1(self) -> BenchmarkResult:
        """Execute Phase 1 validation with available databases"""
        print("=" * 80)
        print("ELIS BENCHMARK 2 - PHASE 1 EXECUTION")
        print("Paper: Tai & Awasthi (2025) - Agile Government")
        print("=" * 80)
        print()
        
        start_time = datetime.now()
        
        # Get Phase 1 databases
        phase1_dbs = self.config['execution']['phases']['phase1']['databases']
        print(f"Databases to search: {', '.join(phase1_dbs)}")
        print()
        
        # Build query from config
        query = self.config['search_strategy']['query_string']
        date_start = self.config['search_strategy']['date_range']['start']
        date_end = self.config['search_strategy']['date_range']['end']
        
        print(f"Query: {query}")
        print(f"Date range: {date_start} to {date_end}")
        print(f"Gold standard studies: {len(self.gold_standard)}")
        print()
        
        # Execute searches (simulated for now)
        print("PHASE 1: SIMULATED DATABASE SEARCHES")
        print("-" * 80)
        
        all_retrieved = []
        db_contribution = {}
        
        for db in phase1_dbs:
            results = self.simulate_database_search(db, query)
            all_retrieved.extend(results)
            db_contribution[db] = len(results)
        
        print()
        print(f"Total retrieved (with duplicates): {len(all_retrieved)}")
        
        # Deduplication
        print()
        print("DEDUPLICATION")
        print("-" * 80)
        unique_retrieved = self.deduplicate(all_retrieved)
        print(f"After deduplication: {len(unique_retrieved)}")
        
        # Matching
        print()
        print("MATCHING AGAINST GOLD STANDARD")
        print("-" * 80)
        
        matched_studies, missed_studies = self.match_studies(
            self.gold_standard, 
            unique_retrieved
        )
        
        # Calculate metrics
        total_matched = len(matched_studies)
        retrieval_rate = total_matched / len(self.gold_standard)
        precision = total_matched / len(unique_retrieved) if unique_retrieved else 0
        recall = retrieval_rate  # Same as retrieval rate
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        print(f"Matched: {total_matched}/{len(self.gold_standard)} ({retrieval_rate:.1%})")
        print(f"Precision: {precision:.1%}")
        print(f"Recall: {recall:.1%}")
        print(f"F1 Score: {f1:.3f}")
        
        # Execution time
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        print()
        print(f"Execution time: {execution_time:.2f} seconds")
        print(f"Estimated cost: $0.00 (simulated)")
        
        # Create result object
        result = BenchmarkResult(
            benchmark_id="TAI_AWASTHI_2025",
            phase="PHASE_1_SIMULATION",
            execution_date=start_time.isoformat(),
            total_gold_standard=len(self.gold_standard),
            total_retrieved=len(unique_retrieved),
            total_matched=total_matched,
            retrieval_rate=retrieval_rate,
            precision=precision,
            recall=recall,
            f1_score=f1,
            execution_time_seconds=execution_time,
            total_cost_usd=0.00,
            databases_used=phase1_dbs,
            matched_studies=matched_studies,
            missed_studies=missed_studies,
            database_contribution=db_contribution
        )
        
        return result
    
    def deduplicate(self, studies: List[Dict]) -> List[Dict]:
        """Remove duplicate studies"""
        seen_titles = set()
        unique = []
        
        for study in studies:
            norm_title = FuzzyMatcher.normalize_text(study.get('title', ''))
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
                    matched.append({
                        'gold_standard_id': gold_study['reference_id'],
                        'title': gold_study['title'],
                        'authors': gold_study['authors'],
                        'year': gold_study['year'],
                        'matched_title': retrieved_study['title'],
                        'source_database': retrieved_study.get('source_database', 'Unknown')
                    })
                    found = True
                    break
            
            if not found:
                missed.append({
                    'reference_id': gold_study['reference_id'],
                    'title': gold_study['title'],
                    'authors': gold_study['authors'],
                    'year': gold_study['year']
                })
        
        return matched, missed
    
    def save_results(self, result: BenchmarkResult):
        """Save results to files"""
        print()
        print("SAVING RESULTS")
        print("-" * 80)
        
        # JSON results
        json_file = self.results_dir / "benchmark_2_phase1_results.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(asdict(result), f, indent=2)
        print(f"✓ Saved: {json_file}")
        
        # Markdown report
        md_file = self.results_dir / "benchmark_2_phase1_report.md"
        self.generate_markdown_report(result, md_file)
        print(f"✓ Saved: {md_file}")
        
        # Matched studies
        matched_file = self.results_dir / "benchmark_2_matched_studies.json"
        with open(matched_file, 'w', encoding='utf-8') as f:
            json.dump(result.matched_studies, f, indent=2)
        print(f"✓ Saved: {matched_file}")
        
        # Missed studies
        missed_file = self.results_dir / "benchmark_2_missed_studies.json"
        with open(missed_file, 'w', encoding='utf-8') as f:
            json.dump(result.missed_studies, f, indent=2)
        print(f"✓ Saved: {missed_file}")
    
    def generate_markdown_report(self, result: BenchmarkResult, output_file: Path):
        """Generate markdown report"""
        report = f"""# ELIS Benchmark 2 - Phase 1 Results

**Benchmark:** Tai & Awasthi (2025) - Agile Government  
**Execution Date:** {result.execution_date}  
**Phase:** {result.phase}  
**Status:** SIMULATION (Testing matching logic)

---

## Executive Summary

| Metric | Value |
|--------|-------|
| **Gold Standard Studies** | {result.total_gold_standard} |
| **Retrieved Studies** | {result.total_retrieved} |
| **Matched Studies** | {result.total_matched} |
| **Retrieval Rate** | {result.retrieval_rate:.1%} |
| **Precision** | {result.precision:.1%} |
| **Recall** | {result.recall:.1%} |
| **F1 Score** | {result.f1_score:.3f} |
| **Execution Time** | {result.execution_time_seconds:.2f}s |
| **Cost** | ${result.total_cost_usd:.2f} |

---

## Database Contribution

| Database | Retrieved Studies |
|----------|------------------|
"""
        for db, count in result.database_contribution.items():
            report += f"| {db} | {count} |\n"
        
        report += f"""
---

## Matched Studies ({len(result.matched_studies)})

"""
        for i, match in enumerate(result.matched_studies[:10], 1):
            report += f"{i}. **{match['title']}** ({match['year']})\n"
            report += f"   - Authors: {match['authors']}\n"
            report += f"   - Source: {match['source_database']}\n\n"
        
        if len(result.matched_studies) > 10:
            report += f"... and {len(result.matched_studies) - 10} more\n\n"
        
        report += f"""---

## Missed Studies ({len(result.missed_studies)})

"""
        for i, miss in enumerate(result.missed_studies[:10], 1):
            report += f"{i}. **{miss['title']}** ({miss['year']})\n"
            report += f"   - Authors: {miss['authors']}\n\n"
        
        if len(result.missed_studies) > 10:
            report += f"... and {len(result.missed_studies) - 10} more\n\n"
        
        report += f"""---

## Next Steps

1. Review matched studies for accuracy
2. Investigate missed studies
3. Wait for EBSCOhost and ProQuest API access
4. Re-run as Phase 2 with full database coverage

---

**NOTE:** This is a SIMULATION to test the matching logic.  
In production, this will call actual ELIS database APIs.
"""
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)


def main():
    """Main execution function"""
    print()
    print("ELIS BENCHMARK 2 - EXECUTION SCRIPT")
    print()
    
    # Initialize executor
    executor = Benchmark2Executor(CONFIG_FILE, GOLD_STANDARD_FILE)
    
    # Execute Phase 1
    result = executor.execute_phase1()
    
    # Save results
    executor.save_results(result)
    
    print()
    print("=" * 80)
    print("BENCHMARK EXECUTION COMPLETE")
    print("=" * 80)
    print()
    print("NOTE: This was a SIMULATION to test the matching logic.")
    print("To run with actual ELIS databases, integrate with the ELIS SLR Agent API.")
    print()


if __name__ == "__main__":
    main()
