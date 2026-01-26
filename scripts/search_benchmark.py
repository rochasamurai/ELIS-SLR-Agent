#!/usr/bin/env python3
"""
Benchmark Search Script

Executes searches specifically for Darmawan (2021) benchmark validation.
Uses free APIs (Semantic Scholar, OpenAlex, arXiv) to avoid API key requirements.

Author: Carlos Rocha
Date: 2026-01-26
"""

import sys
import json
import yaml
import requests
import time
from pathlib import Path
from datetime import datetime
from typing import List, Dict

# Define PROJECT_ROOT first
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Now import ELIS harvest functions
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
from semanticscholar_harvest import search_semantic_scholar
from openalex_harvest import search_openalex
from core_harvest import search_core
from crossref_harvest import search_crossref
from scopus_harvest import search_scopus
from wos_harvest import search_wos
from ieee_harvest import search_ieee

class BenchmarkSearcher:
    """Execute benchmark searches using free academic APIs."""
    
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
    
    def search_semantic_scholar(self) -> List[Dict]:
        """Search Semantic Scholar (free API)."""
        print("\n🔍 Searching Semantic Scholar...")
        
        url = "https://api.semanticscholar.org/graph/v1/paper/search"
        
        # Simplify query for S2
        simple_query = 'e-voting OR "electronic voting" adoption'
        
        params = {
            'query': simple_query,
            'year': f'{self.year_from}-{self.year_to}',
            'fields': 'title,authors,year,venue,abstract,publicationDate,externalIds',
            'limit': 100
        }
        
        headers = {'User-Agent': 'ELIS-Benchmark/1.0 (research)'}
        
        try:
            response = requests.get(url, params=params, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            papers = data.get('data', [])
            print(f"  Found {len(papers)} results")
            
            # Normalize to ELIS format
            normalized = []
            for paper in papers:
                normalized.append({
                    'id': f"s2_{paper.get('paperId', 'unknown')}",
                    'title': paper.get('title', ''),
                    'authors': [a.get('name', '') for a in paper.get('authors', [])],
                    'year': paper.get('year'),
                    'venue': paper.get('venue', ''),
                    'abstract': paper.get('abstract', ''),
                    'doi': paper.get('externalIds', {}).get('DOI'),
                    'source': 'semanticscholar',
                    'source_id': paper.get('paperId'),
                    'retrieved_at': datetime.utcnow().isoformat() + 'Z'
                })
            
            return normalized
            
        except Exception as e:
            print(f"  ⚠️ Semantic Scholar error: {e}")
            return []
    
    def search_openalex(self) -> List[Dict]:
        """Search OpenAlex (free API)."""
        print("\n🔍 Searching OpenAlex...")
        
        url = "https://api.openalex.org/works"
        
        # Build OpenAlex query
        query = 'e-voting OR electronic voting'
        
        params = {
            'search': query,
            'filter': f'publication_year:{self.year_from}-{self.year_to}',
            'per_page': 100,
            'mailto': 'elis-benchmark@research.org'  # Polite pool
        }
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            works = data.get('results', [])
            print(f"  Found {len(works)} results")
            
            # Normalize to ELIS format
            normalized = []
            for work in works:
                authors = [a.get('author', {}).get('display_name', '') 
                          for a in work.get('authorships', [])]
                
                normalized.append({
                    'id': f"openalex_{work.get('id', '').split('/')[-1]}",
                    'title': work.get('title', ''),
                    'authors': authors,
                    'year': work.get('publication_year'),
                    'venue': work.get('primary_location', {}).get('source', {}).get('display_name', ''),
                    'abstract': work.get('abstract', ''),
                    'doi': work.get('doi', '').replace('https://doi.org/', '') if work.get('doi') else None,
                    'source': 'openalex',
                    'source_id': work.get('id'),
                    'retrieved_at': datetime.utcnow().isoformat() + 'Z'
                })
            
            return normalized
            
        except Exception as e:
            print(f"  ⚠️ OpenAlex error: {e}")
            return []
    
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
        print("BENCHMARK SEARCH EXECUTION")
        print("="*70)
        print(f"Query: {self.query[:100]}...")
        print(f"Period: {self.year_from}-{self.year_to}")
        print("="*70)
        
        all_results = []
        
        # Free APIs (no keys required)
        print("\n📚 FREE APIs:")
        all_results.extend(self.search_semantic_scholar())
        time.sleep(1)
        
        all_results.extend(self.search_openalex())
        time.sleep(1)
        
        # Add CORE
        print("\n🔍 Searching CORE...")
        try:
            core_results = search_core(self.query, self.year_from, self.year_to)
            print(f"  Found {len(core_results)} results")
            all_results.extend(core_results)
        except Exception as e:
            print(f"  ⚠️ CORE error: {e}")
        time.sleep(1)
        
        # Add CrossRef
        print("\n🔍 Searching CrossRef...")
        try:
            crossref_results = search_crossref(self.query, self.year_from, self.year_to)
            print(f"  Found {len(crossref_results)} results")
            all_results.extend(crossref_results)
        except Exception as e:
            print(f"  ⚠️ CrossRef error: {e}")
        time.sleep(1)
        
        # Paid APIs (require keys from GitHub secrets)
        print("\n🔐 PAID APIs (require keys):")
        
        # Scopus
        print("\n🔍 Searching Scopus...")
        try:
            scopus_results = search_scopus(self.query, self.year_from, self.year_to)
            print(f"  Found {len(scopus_results)} results")
            all_results.extend(scopus_results)
        except Exception as e:
            print(f"  ⚠️ Scopus error (may need API key): {e}")
        time.sleep(1)
        
        # Web of Science
        print("\n🔍 Searching Web of Science...")
        try:
            wos_results = search_wos(self.query, self.year_from, self.year_to)
            print(f"  Found {len(wos_results)} results")
            all_results.extend(wos_results)
        except Exception as e:
            print(f"  ⚠️ WoS error (may need API key): {e}")
        time.sleep(1)
        
        # IEEE
        print("\n🔍 Searching IEEE Xplore...")
        try:
            ieee_results = search_ieee(self.query, self.year_from, self.year_to)
            print(f"  Found {len(ieee_results)} results")
            all_results.extend(ieee_results)
        except Exception as e:
            print(f"  ⚠️ IEEE error (may need API key): {e}")
        
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
                'sources': ['semanticscholar', 'openalex'],
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