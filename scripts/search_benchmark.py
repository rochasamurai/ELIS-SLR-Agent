#!/usr/bin/env python3
"""
Benchmark Search Script

Executes searches specifically for Darmawan (2021) benchmark validation.
Uses all available ELIS database harvesters.

Author: Carlos Rocha
Date: 2026-01-26
"""

import sys
import json
import yaml
import time
from pathlib import Path
from datetime import datetime
from typing import List, Dict

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

# Import ELIS harvest functions
from semanticscholar_harvest import semanticscholar_search, transform_semanticscholar_entry
from openalex_harvest import openalex_search, transform_openalex_entry
from core_harvest import core_search, transform_core_entry
from crossref_harvest import crossref_search, transform_crossref_entry
from scopus_harvest import scopus_search, transform_scopus_entry
from wos_harvest import wos_search, transform_wos_entry
from ieee_harvest import ieee_search, transform_ieee_entry
from google_scholar_harvest import google_scholar_search, transform_google_scholar_entry

class BenchmarkSearcher:
    """Execute benchmark searches using all ELIS database APIs."""
    
    def __init__(self, config_path: str):
        """Initialize with benchmark configuration."""
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.query = self._build_query()
        self.year_from = self.config['global']['year_from']
        self.year_to = self.config['global']['year_to']
        self.results = []
    
    def _build_query(self) -> str:
        """Extract query from config."""
        topics = self.config.get('topics', [])
        if topics and topics[0].get('queries'):
            return topics[0]['queries'][0]
        return ""
    
    def search_all_databases(self) -> List[Dict]:
        """Search all available databases."""
        all_results = []
        
        # Semantic Scholar
        print("\n🔍 Searching Semantic Scholar...")
        try:
            simple_query = 'e-voting OR "electronic voting" adoption'
            results = semanticscholar_search(simple_query, limit=100, max_results=200)
            normalized = [self._normalize_entry(transform_semanticscholar_entry(r), 'semanticscholar') for r in results]
            print(f"  Found {len(normalized)} results")
            all_results.extend(normalized)
        except Exception as e:
            print(f"  ⚠️ Error: {e}")
        time.sleep(1)
        
        # OpenAlex
        print("\n🔍 Searching OpenAlex...")
        try:
            query = 'e-voting OR electronic voting'
            results = openalex_search(query, per_page=100, max_results=200)
            normalized = [self._normalize_entry(transform_openalex_entry(r), 'openalex') for r in results]
            print(f"  Found {len(normalized)} results")
            all_results.extend(normalized)
        except Exception as e:
            print(f"  ⚠️ Error: {e}")
        time.sleep(1)
        
        # CORE
        print("\n🔍 Searching CORE...")
        try:
            query = 'e-voting OR "electronic voting" adoption'
            results = core_search(query, limit=100, max_results=200)
            normalized = [self._normalize_entry(transform_core_entry(r), 'core') for r in results]
            print(f"  Found {len(normalized)} results")
            all_results.extend(normalized)
        except Exception as e:
            print(f"  ⚠️ Error: {e}")
        time.sleep(1)
        
        # CrossRef
        print("\n🔍 Searching CrossRef...")
        try:
            query = 'e-voting electronic voting adoption'
            results = crossref_search(query, rows=100, max_results=200)
            normalized = [self._normalize_entry(transform_crossref_entry(r), 'crossref') for r in results]
            print(f"  Found {len(normalized)} results")
            all_results.extend(normalized)
        except Exception as e:
            print(f"  ⚠️ Error: {e}")
        time.sleep(1)
        
        # Scopus (requires API key)
        print("\n🔍 Searching Scopus...")
        try:
            query = 'e-voting OR "electronic voting" AND adoption'
            results = scopus_search(query, count=25, max_results=200)
            normalized = [self._normalize_entry(transform_scopus_entry(r), 'scopus') for r in results]
            print(f"  Found {len(normalized)} results")
            all_results.extend(normalized)
        except Exception as e:
            print(f"  ⚠️ Scopus error (may need API key): {e}")
        time.sleep(1)
        
        # Web of Science (requires API key)
        print("\n🔍 Searching Web of Science...")
        try:
            query = 'e-voting OR "electronic voting" AND adoption'
            results = wos_search(query, limit=50, max_results=200)
            normalized = [self._normalize_entry(transform_wos_entry(r), 'wos') for r in results]
            print(f"  Found {len(normalized)} results")
            all_results.extend(normalized)
        except Exception as e:
            print(f"  ⚠️ WoS error (may need API key): {e}")
        time.sleep(1)
        
        # IEEE (requires API key)
        print("\n🔍 Searching IEEE Xplore...")
        try:
            query = '("e-voting" OR "electronic voting") AND adoption'
            results = ieee_search(query, max_records=200)
            normalized = [self._normalize_entry(transform_ieee_entry(r), 'ieee') for r in results]
            print(f"  Found {len(normalized)} results")
            all_results.extend(normalized)
        except Exception as e:
            print(f"  ⚠️ IEEE error (may need API key): {e}")   

        # Google Scholar (via Apify)
        print("\n🎓 Searching Google Scholar (via Apify)...")
        try:
            query_simple = 'e-voting OR "electronic voting" adoption'
            results = google_scholar_search(query_simple, max_items=200, 
                                          newer_than=self.year_from, 
                                          older_than=self.year_to)
            normalized = [self._normalize_entry(transform_google_scholar_entry(r), 'google_scholar') for r in results]
            print(f"  Found {len(normalized)} results")
            all_results.extend(normalized)
        except Exception as e:
            print(f"  ⚠️ Google Scholar error: {e}")
        
        return all_results
        
    def _normalize_entry(self, entry: Dict, source: str) -> Dict:
        """Normalize entry to standard format."""
        return {
            'id': f"{source}_{entry.get('id', 'unknown')}",
            'title': entry.get('title', ''),
            'authors': entry.get('authors', []),
            'year': entry.get('year'),
            'venue': entry.get('venue', ''),
            'abstract': entry.get('abstract', ''),
            'doi': entry.get('doi'),
            'source': source,
            'source_id': entry.get('source_id', entry.get('id')),
            'retrieved_at': datetime.utcnow().isoformat() + 'Z'
        }
    
    def deduplicate(self, results: List[Dict]) -> List[Dict]:
        """Remove duplicates by DOI and title."""
        seen_dois = set()
        seen_titles = set()
        unique = []
        
        for item in results:
            doi = item.get('doi')
            title = item.get('title', '').lower().strip()
            
            # Check DOI first
            if doi and doi in seen_dois:
                continue
            
            # Check title
            if title and title in seen_titles:
                continue
            
            # Add to unique
            if doi:
                seen_dois.add(doi)
            if title:
                seen_titles.add(title)
            
            unique.append(item)
        
        return unique
    
    def run(self) -> List[Dict]:
        """Execute all searches and return deduplicated results."""
        print("="*70)
        print("BENCHMARK SEARCH EXECUTION - ALL DATABASES")
        print("="*70)
        print(f"Query: {self.query[:100]}...")
        print(f"Period: {self.year_from}-{self.year_to}")
        print("="*70)
        
        # Search all databases
        all_results = self.search_all_databases()
        
        # Deduplicate
        unique_results = self.deduplicate(all_results)
        
        print(f"\n✓ Total results: {len(all_results)}")
        print(f"✓ After deduplication: {len(unique_results)}")
        
        return unique_results
    
    def save(self, results: List[Dict], output_path: str):
        """Save results in ELIS format."""
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        
        # Add metadata
        data = [
            {
                '_meta': True,
                'protocol_version': 'ELIS Benchmark (Darmawan 2021)',
                'retrieved_at': datetime.utcnow().isoformat() + 'Z',
                'query': self.query,
                'year_range': f'{self.year_from}-{self.year_to}',
                'sources': ['semanticscholar', 'openalex', 'core', 'crossref', 'scopus', 'wos', 'ieee', 'google_scholar'],
                'record_count': len(results)
            }
        ]
        data.extend(results)
        
        with open(output, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"\n✓ Saved {len(results)} results to: {output}")


def main():
    """Main execution."""
    config_path = PROJECT_ROOT / "config" / "benchmark_temp_queries.yml"
    output_path = PROJECT_ROOT / "json_jsonl" / "benchmark_search_results.json"
    
    if not config_path.exists():
        print(f"❌ Config not found: {config_path}")
        sys.exit(1)
    
    searcher = BenchmarkSearcher(str(config_path))
    results = searcher.run()
    searcher.save(results, str(output_path))
    
    print("\n" + "="*70)
    print("BENCHMARK SEARCH COMPLETE")
    print("="*70)


if __name__ == '__main__':
    main()
    