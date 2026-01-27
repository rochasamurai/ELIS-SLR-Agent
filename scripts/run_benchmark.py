#!/usr/bin/env python3
"""
ELIS Benchmark Validation Script - Darmawan (2021)

Purpose: Validate ELIS SLR Agent retrieval capabilities against published 
         semi-systematic review as recommended by supervisor.

Standard: Darmawan, I. (2021). E-voting adoption in many countries: 
          A literature review. Asian Journal of Comparative Politics, 6(4), 482-504.

Author: Carlos Rocha
Date: 2026-01-26
"""

import json
import yaml
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
import sys

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class BenchmarkValidator:
    """Validates ELIS retrieval against Darmawan 2021 benchmark."""

    def __init__(self, config_path: str = "configs/benchmark_config.yaml"):
        """Initialize validator with configuration."""
        self.config = self._load_config(config_path)
        self.gold_standard = self._load_gold_standard()
        self.results = {}

    def _load_config(self, config_path: str) -> Dict:
        """Load benchmark configuration."""
        config_file = PROJECT_ROOT / config_path
        if not config_file.exists():
            raise FileNotFoundError(f"Config file not found: {config_file}")

        with open(config_file, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)

        print(f"✓ Loaded configuration: {config['benchmark']['name']}")
        return config

    def _load_gold_standard(self) -> pd.DataFrame:
        """Load Darmawan's 78 studies as gold standard."""
        gold_file = PROJECT_ROOT / "data/benchmark/darmawan_2021_references.json"

        if not gold_file.exists():
            raise FileNotFoundError(f"Gold standard file not found: {gold_file}")

        with open(gold_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        df = pd.DataFrame(data["studies"])
        print(f"✓ Loaded gold standard: {len(df)} studies from Darmawan (2021)")
        return df

    def run_elis_search(self) -> pd.DataFrame:
        """
        Run ELIS search with benchmark parameters.
        """
        print("\n" + "="*70)
        print("ELIS SEARCH EXECUTION")
        print("="*70)
        
        search_params = self.config['search_parameters']
        print(f"Time period: {search_params['date_range']['start']} to {search_params['date_range']['end']}")
        print(f"Databases: {', '.join(search_params['databases'])}")
        print(f"Boolean string: {search_params['search_terms']['boolean_string'][:100]}...")
        
        # Import and use the adapter
        try:
            from benchmark_elis_adapter import run_benchmark_search
            results = run_benchmark_search(self.config)
            return results
        except ImportError as e:
            print(f"\n⚠️  ELIS adapter not found: {e}")
            print("Make sure benchmark_elis_adapter.py is in scripts/")
            return pd.DataFrame()
        except Exception as e:
            print(f"\n❌ Error running ELIS search: {e}")
            import traceback
            traceback.print_exc()
            return pd.DataFrame()

    def match_studies(self, elis_results: pd.DataFrame) -> Tuple[List, List, List]:
        """
        Match ELIS results against Darmawan's 78 studies.
        
        Strategy: Simple substring matching with lenient rules
        """
        if elis_results.empty:
            print("\n⚠️  No ELIS results to match")
            return [], self.gold_standard.to_dict('records'), []
        
        print("\n" + "="*70)
        print("MATCHING ELIS RESULTS AGAINST GOLD STANDARD")
        print("="*70)
        print(f"ELIS results: {len(elis_results)}")
        print(f"Gold standard: {len(self.gold_standard)}")
        
        matched = []
        missed = []
        matched_elis_indices = set()
        
        # Normalize ELIS results
        elis_normalized = elis_results.copy()
        if 'title' in elis_normalized.columns:
            elis_normalized['title_norm'] = (
                elis_normalized['title'].fillna('')
                .str.lower().str.strip()
                .str.replace(r'[^\w\s]', ' ', regex=True)
                .str.replace(r'\s+', ' ', regex=True)
            )
        
        # Match each gold standard study
        for idx, gold_study in self.gold_standard.iterrows():
            gold_title = str(gold_study.get('title', '')).lower().strip()
            gold_title_norm = ''.join(c if c.isalnum() or c.isspace() else ' ' for c in gold_title)
            gold_title_norm = ' '.join(gold_title_norm.split())  # Normalize spaces
            gold_year = gold_study.get('year')
            
            # Extract key words from gold title (remove stop words)
            stop_words = {'the', 'a', 'an', 'and', 'or', 'of', 'in', 'on', 'at', 'to', 'for', 'from', 'with'}
            gold_words = [w for w in gold_title_norm.split() if w not in stop_words and len(w) > 2]
            
            matched_idx = None
            match_method = None
            
            for elis_idx, elis_row in elis_normalized.iterrows():
                if elis_idx in matched_elis_indices:
                    continue
                
                elis_title_norm = elis_row.get('title_norm', '')
                if not elis_title_norm:
                    continue
                
                # Count matching key words
                matches = sum(1 for word in gold_words if word in elis_title_norm)
                match_ratio = matches / len(gold_words) if gold_words else 0
                
                # Match if >50% of key words match
                if match_ratio >= 0.50:
                    elis_year = elis_row.get('year')
                    
                    # If we have years, they should match
                    if gold_year and elis_year:
                        try:
                            if int(elis_year) == int(gold_year):
                                matched_idx = elis_idx
                                match_method = f"keywords+year ({match_ratio:.0%})"
                                break
                        except (ValueError, TypeError):
                            pass
                    else:
                        # No year available, accept keyword match
                        matched_idx = elis_idx
                        match_method = f"keywords ({match_ratio:.0%})"
                        break
            
            # Record result
            if matched_idx is not None:
                matched_elis_indices.add(matched_idx)
                gold_dict = gold_study.to_dict()
                gold_dict['match_method'] = match_method
                gold_dict['elis_title'] = elis_results.loc[matched_idx, 'title']
                matched.append(gold_dict)
            else:
                missed.append(gold_study.to_dict())
        
        # Additional studies
        additional = []
        for elis_idx in elis_normalized.index:
            if elis_idx not in matched_elis_indices:
                additional.append(elis_normalized.loc[elis_idx].to_dict())
        
        print(f"\n✓ Matched: {len(matched)}/{len(self.gold_standard)} ({len(matched)/len(self.gold_standard)*100:.1f}%)")
        print(f"  Missed: {len(missed)}")
        print(f"  Additional in ELIS: {len(additional)}")
        
        # Show match methods
        match_methods = {}
        for m in matched:
            method = m.get('match_method', 'unknown')
            match_methods[method] = match_methods.get(method, 0) + 1
        if match_methods:
            print(f"\n  Match methods:")
            for method, count in sorted(match_methods.items(), key=lambda x: -x[1]):
                print(f"    {method}: {count}")
        
        return matched, missed, additional

    def calculate_metrics(self, matched: List, missed: List, elis_total: int) -> Dict:
        """Calculate validation metrics."""
        gold_total = len(self.gold_standard)
        matched_count = len(matched)
        missed_count = len(missed)

        retrieval_rate = (matched_count / gold_total * 100) if gold_total > 0 else 0
        recall = retrieval_rate  # Same metric in this context

        precision = (matched_count / elis_total * 100) if elis_total > 0 else 0

        metrics = {
            "gold_standard_total": gold_total,
            "elis_results_total": elis_total,
            "matched_studies": matched_count,
            "missed_studies": missed_count,
            "retrieval_rate_percent": round(retrieval_rate, 1),
            "recall_percent": round(recall, 1),
            "precision_percent": round(precision, 1),
            "additional_studies": elis_total - matched_count,
            "test_date": datetime.now().isoformat(),
        }

        return metrics

    def generate_report(self, metrics: Dict, matched: List, missed: List) -> str:
        """Generate markdown validation report."""
        targets = self.config["validation_targets"]

        # Determine pass/fail
        passed = metrics["retrieval_rate_percent"] >= (
            targets["retrieval_rate_minimum"] * 100
        )
        status = "✅ PASS" if passed else "❌ FAIL"

        report = f"""# ELIS Benchmark Validation Report

**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Status:** {status}

## Benchmark Standard

**Paper:** Darmawan, I. (2021). E-voting adoption in many countries: A literature review.  
**Journal:** Asian Journal of Comparative Politics, 6(4), 482-504  
**DOI:** {self.config['benchmark']['standard_paper']['doi']}  
**Studies:** {metrics['gold_standard_total']} (2005-2020)  
**Databases Used by Darmawan:** Google Scholar, ACM Digital Library, Science Direct, J-STOR

## ELIS Configuration

**Search Terms:**
```
{self.config['search_parameters']['search_terms']['boolean_string']}
```

**Databases:** {', '.join(self.config['search_parameters']['databases'])}  
**Date Range:** {self.config['search_parameters']['date_range']['start']} to {self.config['search_parameters']['date_range']['end']}  
**Filters:** English language, peer-reviewed journal articles

## Validation Results

### Summary Metrics

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| **Retrieval Rate** | {metrics['retrieval_rate_percent']}% ({metrics['matched_studies']}/{metrics['gold_standard_total']}) | ≥{targets['retrieval_rate_minimum']*100}% | {'✅' if metrics['retrieval_rate_percent'] >= targets['retrieval_rate_minimum']*100 else '❌'} |
| **Precision** | {metrics['precision_percent']}% | ≥{targets['precision_minimum']*100}% | {'✅' if metrics['precision_percent'] >= targets['precision_minimum']*100 else '❌'} |
| **Recall** | {metrics['recall_percent']}% | ≥{targets['retrieval_rate_minimum']*100}% | {'✅' if metrics['recall_percent'] >= targets['retrieval_rate_minimum']*100 else '❌'} |
| **ELIS Total Results** | {metrics['elis_results_total']} | - | - |
| **Additional Studies** | {metrics['additional_studies']} | - | ℹ️ |

### Interpretation

**Matched Studies:** {metrics['matched_studies']}/{metrics['gold_standard_total']} studies from Darmawan's benchmark were successfully retrieved by ELIS.

**Missed Studies:** {metrics['missed_studies']} studies from Darmawan were not found by ELIS. See detailed list below.

**Additional Studies:** ELIS found {metrics['additional_studies']} additional studies not in Darmawan's review, likely due to:
- Broader database coverage (Scopus, Web of Science vs. Google Scholar)
- Systematic search methodology
- Different search string optimization

## Validation Outcome

"""

        if passed:
            report += f"""### ✅ VALIDATION PASSED

ELIS successfully retrieved **{metrics['retrieval_rate_percent']}%** of Darmawan's studies, exceeding the minimum threshold of {targets['retrieval_rate_minimum']*100}%.

**Conclusion:** ELIS demonstrates adequate retrieval capability for systematic literature review. The system is validated and credible for proceeding with the full ELIS systematic review.
"""
        else:
            report += f"""### ❌ VALIDATION FAILED

ELIS retrieved only **{metrics['retrieval_rate_percent']}%** of Darmawan's studies, below the minimum threshold of {targets['retrieval_rate_minimum']*100}%.

**Action Required:** 
1. Review search string optimization
2. Check database API configurations
3. Analyze missed studies for patterns
4. Refine screening rules
5. Re-run benchmark test
"""

        report += f"""

## Detailed Analysis

### Missed Studies ({len(missed)} studies)

"""
        if missed:
            report += "| ID | Year | Authors | Title |\n"
            report += "|---|------|---------|-------|\n"
            for study in missed[:10]:  # Show first 10
                report += f"| {study.get('id', 'N/A')} | {study.get('year', 'N/A')} | {study.get('authors', 'N/A')} | {study.get('title', 'N/A')[:60]}... |\n"

            if len(missed) > 10:
                report += f"\n*...and {len(missed) - 10} more. See `data/benchmark/missed_studies.csv` for complete list.*\n"
        else:
            report += "*No studies missed - perfect retrieval!*\n"

        report += f"""

### Sample Matched Studies ({min(10, len(matched))} of {len(matched)})

"""
        if matched:
            report += "| ID | Year | Authors | Title |\n"
            report += "|---|------|---------|-------|\n"
            for study in matched[:10]:
                report += f"| {study.get('id', 'N/A')} | {study.get('year', 'N/A')} | {study.get('authors', 'N/A')} | {study.get('title', 'N/A')[:60]}... |\n"
        else:
            report += "*No studies matched yet - ELIS search pending.*\n"

        report += """

## Next Steps

"""
        if passed:
            report += """1. ✅ Share validation report with supervisor
2. ✅ Proceed with OSF/Spiral protocol registration
3. ✅ Begin full ELIS systematic review
4. Document benchmark results in protocol methodology
"""
        else:
            report += """1. Analyze missed studies for common patterns
2. Optimize search strings based on findings
3. Verify database API connectivity
4. Re-run benchmark test
5. Iterate until validation passes
"""

        report += f"""

---

**Report Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Script:** `scripts/run_benchmark.py`  
**Configuration:** `configs/benchmark_config.yaml`  
**Gold Standard:** `data/benchmark/darmawan_2021_references.json`
"""

        return report

    def save_results(self, metrics: Dict, matched: List, missed: List, report: str):
        """Save validation results to files."""
        output_dir = PROJECT_ROOT / "data/benchmark"
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save metrics
        metrics_file = output_dir / "benchmark_results.json"
        with open(metrics_file, "w", encoding="utf-8") as f:
            json.dump(metrics, f, indent=2)
        print(f"\n✓ Saved metrics: {metrics_file}")

        # Save matched studies
        if matched:
            matched_file = output_dir / "matched_studies.json"
            with open(matched_file, "w", encoding="utf-8") as f:
                json.dump(matched, f, indent=2)
            print(f"✓ Saved matched studies: {matched_file}")

        # Save missed studies
        if missed:
            missed_file = output_dir / "missed_studies.json"
            with open(missed_file, "w", encoding="utf-8") as f:
                json.dump(missed, f, indent=2)
            print(f"✓ Saved missed studies: {missed_file}")

        # Save report
        report_file = PROJECT_ROOT / "docs/BENCHMARK_VALIDATION_REPORT.md"
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"✓ Saved report: {report_file}")

    def run(self):
        """Execute complete benchmark validation."""
        print("\n" + "=" * 70)
        print("ELIS BENCHMARK VALIDATION - Darmawan (2021)")
        print("=" * 70)
        print(f"Standard: {self.config['benchmark']['standard_paper']['title']}")
        print(f"Gold standard studies: {len(self.gold_standard)}")
        print("=" * 70)

        # Step 1: Run ELIS search
        elis_results = self.run_elis_search()

        # Step 2: Match studies
        matched, missed, additional = self.match_studies(elis_results)

        # Step 3: Calculate metrics
        metrics = self.calculate_metrics(matched, missed, len(elis_results))

        # Step 4: Generate report
        report = self.generate_report(metrics, matched, missed)

        # Step 5: Save results
        self.save_results(metrics, matched, missed, report)

        # Step 6: Display summary
        print("\n" + "=" * 70)
        print("BENCHMARK VALIDATION COMPLETE")
        print("=" * 70)
        print(f"Retrieval Rate: {metrics['retrieval_rate_percent']}%")
        print(
            f"Status: {'✅ PASS' if metrics['retrieval_rate_percent'] >= 70 else '❌ FAIL'}"
        )
        print("\nFull report: docs/BENCHMARK_VALIDATION_REPORT.md")
        print("=" * 70)

        return metrics


def main():
    """Main execution function."""
    try:
        validator = BenchmarkValidator()
        metrics = validator.run()

        # Exit with appropriate code
        sys.exit(0 if metrics["retrieval_rate_percent"] >= 70 else 1)

    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        sys.exit(2)


if __name__ == "__main__":
    main()
