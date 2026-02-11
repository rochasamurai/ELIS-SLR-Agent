# ELIS SLR Agent - ASTA Integration Development Plan

**Project**: Electoral Integrity Strategies - Systematic Literature Review Agent  
**Integration**: ASTA (Allen AI) via Model Context Protocol (MCP)  
**Repository**: https://github.com/rochasamurai/ELIS-SLR-Agent  
**Plan Version**: 1.0  
**Date**: February 7, 2026  

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Architecture Overview](#architecture-overview)
3. [Development Phases](#development-phases)
4. [Testing Strategy](#testing-strategy)
5. [Documentation Requirements](#documentation-requirements)
6. [Risk Mitigation](#risk-mitigation)

---

## Prerequisites

### Required Before Starting

- [x] Existing ELIS SLR Agent infrastructure (8 databases operational)
- [x] Python 3.9+ environment
- [x] Git repository with clean `main` branch
- [ ] ASTA_TOOL_KEY obtained (https://share.hsforms.com/1L4hUh20oT3mu8iXJQMV77w3ioxm)
- [ ] Understanding of existing ELIS harvest workflow
- [ ] Access to Darmawan-2021 benchmark data

### Environment Setup Check

```powershell
# Verify Python environment
python --version  # Should be 3.9+

# Verify Git status
cd C:\Users\carlo\ELIS-SLR-Agent
git status  # Should be clean

# Verify existing harvest scripts work
python scripts/scopus_harvest.py --help

# Check directory structure
tree /F /A config scripts sources json_jsonl
```

---

## Architecture Overview

### Integration Philosophy

**ASTA is a discovery and evidence-localization assistant, NOT a 9th database.**

```
┌─────────────────────────────────────────────────────────────┐
│                    ELIS SLR WORKFLOW                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Phase 0: ASTA Vocabulary Bootstrapping                    │
│  ┌──────────────────────────────────────┐                  │
│  │  ASTA Discovery → Extract Terms      │                  │
│  │  ↓                                    │                  │
│  │  Enhance Boolean Queries             │                  │
│  └──────────────────────────────────────┘                  │
│           ↓                                                 │
│  Phase 1: Canonical Database Harvesting                    │
│  ┌──────────────────────────────────────┐                  │
│  │  Scopus, WoS, IEEE, etc.             │  ← 8 Databases  │
│  │  (Enhanced with ASTA vocabulary)     │                  │
│  └──────────────────────────────────────┘                  │
│           ↓                                                 │
│  Phase 2: ASTA-Assisted Screening                          │
│  ┌──────────────────────────────────────┐                  │
│  │  ASTA Snippet Search                 │                  │
│  │  ↓                                    │                  │
│  │  Pre-fill relevance evidence         │                  │
│  │  ↓                                    │                  │
│  │  Human decides inclusion/exclusion   │  ← ELIS decides │
│  └──────────────────────────────────────┘                  │
│           ↓                                                 │
│  Phase 3: ASTA Evidence Localization                       │
│  ┌──────────────────────────────────────┐                  │
│  │  Targeted snippet queries            │                  │
│  │  ↓                                    │                  │
│  │  Extract specific constructs         │                  │
│  │  ↓                                    │                  │
│  │  Human validates extractions         │  ← ELIS validates│
│  └──────────────────────────────────────┘                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘

CRITICAL POLICY: "ASTA proposes, ELIS decides"
```

### Directory Structure (New)

```
ELIS-SLR-Agent/
├── sources/                    # NEW: Source adapters
│   └── asta_mcp/              # NEW: ASTA MCP adapter
│       ├── __init__.py
│       ├── adapter.py         # Core MCP client
│       ├── vocabulary.py      # Vocabulary extraction
│       └── snippets.py        # Snippet search utilities
├── scripts/
│   ├── phase0_asta_scoping.py        # NEW: Vocabulary bootstrapping
│   ├── phase2_asta_screening.py      # NEW: Screening assistance
│   └── phase3_asta_extraction.py     # NEW: Evidence localization
├── config/
│   ├── asta_config.yml               # NEW: ASTA configuration
│   └── asta_extracted_vocabulary.yml # NEW: Generated vocabulary
├── runs/                      # NEW: Run-specific logs
│   └── <run_id>/
│       └── asta/
│           ├── requests.jsonl
│           ├── responses.jsonl
│           └── normalized_records.jsonl
└── tests/
    └── test_asta_adapter.py   # NEW: ASTA unit tests
```

---

## Development Phases

### **PHASE 0: Setup and Infrastructure (Week 1, Days 1-2)**

#### **Step 0.1: Get ASTA Tool Key**

**Objective**: Obtain API credentials for ASTA MCP access

**Tasks**:
1. Visit https://share.hsforms.com/1L4hUh20oT3mu8iXJQMV77w3ioxm
2. Request ASTA_TOOL_KEY
3. Add to `.env` file

```powershell
# Add to .env (do NOT commit)
echo "ASTA_TOOL_KEY=your_key_here" >> .env
```

**Validation**:
```powershell
# Test API key works
curl -X POST https://asta-tools.allen.ai/mcp/v1 `
  -H "Content-Type: application/json" `
  -H "x-api-key: $env:ASTA_TOOL_KEY" `
  -d '{"method":"tools/list"}'
```

**Acceptance Criteria**:
- ✅ API key received
- ✅ Key added to `.env`
- ✅ Test call returns available tools
- ✅ `.env` in `.gitignore`

**Git**: No commit yet (credentials only)

---

#### **Step 0.2: Create Feature Branch**

**Objective**: Isolate ASTA development from `main` branch

```powershell
cd C:\Users\carlo\ELIS-SLR-Agent

# Create and switch to feature branch
git checkout -b feature/asta-integration

# Verify branch
git branch
```

**Acceptance Criteria**:
- ✅ On `feature/asta-integration` branch
- ✅ Branch pushed to GitHub

```powershell
git push -u origin feature/asta-integration
```

---

#### **Step 0.3: Create Directory Structure**

**Objective**: Set up directories for ASTA integration

```powershell
# Create new directories
New-Item -ItemType Directory -Force -Path "sources\asta_mcp"
New-Item -ItemType Directory -Force -Path "runs"
New-Item -ItemType Directory -Force -Path "tests"

# Create __init__.py files
New-Item -ItemType File -Path "sources\__init__.py"
New-Item -ItemType File -Path "sources\asta_mcp\__init__.py"
```

**Acceptance Criteria**:
- ✅ `sources/asta_mcp/` directory exists
- ✅ `runs/` directory exists
- ✅ Python package structure valid

**Git Commit**:
```powershell
git add sources/ runs/ tests/
git commit -m "feat: create directory structure for ASTA integration"
git push
```

---

#### **Step 0.4: Add ASTA Dependencies**

**Objective**: Update `requirements.txt` with ASTA-specific packages

```powershell
# Add to requirements.txt
@"
# ASTA MCP Integration
requests>=2.31.0
pyyaml>=6.0
"@ | Add-Content requirements.txt

# Install dependencies
pip install -r requirements.txt
```

**Acceptance Criteria**:
- ✅ Dependencies installed
- ✅ No conflicts with existing packages
- ✅ `pip check` passes

```powershell
pip check
```

**Git Commit**:
```powershell
git add requirements.txt
git commit -m "feat: add ASTA MCP dependencies"
git push
```

---

### **PHASE 1: Core MCP Adapter (Week 1, Days 3-5)**

#### **Step 1.1: Create Base MCP Client**

**Objective**: Implement core ASTA MCP communication layer

**File**: `sources/asta_mcp/adapter.py`

```python
"""
ASTA MCP Adapter for ELIS SLR Agent
Provides discovery and evidence-localization capabilities via Allen AI's MCP endpoint

Policy: "ASTA proposes, ELIS decides" - ASTA is NOT a canonical search source
"""

import os
import json
import requests
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import time

class AstaMCPAdapter:
    """
    ASTA Scientific Corpus Tool adapter via Model Context Protocol
    
    Operating modes:
    1. Discovery: Vocabulary bootstrapping, candidate generation
    2. Evidence: Snippet localization for screening/extraction
    
    All operations are logged for PRISMA audit trail.
    """
    
    def __init__(self, evidence_window_end: str = "2025-01-31", run_id: Optional[str] = None):
        """
        Initialize ASTA MCP adapter
        
        Args:
            evidence_window_end: ISO date (YYYY-MM-DD) - frozen evidence cutoff
            run_id: Optional run identifier for logging (auto-generated if None)
        """
        self.base_url = "https://asta-tools.allen.ai/mcp/v1"
        self.api_key = os.getenv('ASTA_TOOL_KEY')
        
        if not self.api_key:
            print("⚠️  Warning: ASTA_TOOL_KEY not set. Rate limits will be lower.")
            print("   Request key at: https://share.hsforms.com/1L4hUh20oT3mu8iXJQMV77w3ioxm")
        
        self.headers = {
            'Content-Type': 'application/json',
            'x-api-key': self.api_key
        } if self.api_key else {'Content-Type': 'application/json'}
        
        self.evidence_window_end = evidence_window_end
        
        # Logging setup for PRISMA auditability
        self.run_id = run_id or datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        self.log_dir = Path(f"runs/{self.run_id}/asta")
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Statistics
        self.stats = {
            'requests': 0,
            'errors': 0,
            'rate_limit_hits': 0
        }
    
    def _call_mcp_tool(self, tool_name: str, arguments: Dict, timeout: int = 30) -> Dict:
        """
        Internal method: Call ASTA MCP tool with error handling and logging
        
        Args:
            tool_name: MCP tool name (e.g., "search_papers_by_relevance")
            arguments: Tool arguments
            timeout: Request timeout in seconds
            
        Returns:
            MCP response dictionary
            
        Raises:
            requests.HTTPError: On API errors
        """
        payload = {
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        # Log request
        self._log_request(tool_name, payload)
        self.stats['requests'] += 1
        
        try:
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload,
                timeout=timeout
            )
            
            # Handle rate limiting
            if response.status_code == 429:
                self.stats['rate_limit_hits'] += 1
                print(f"⚠️  Rate limit hit. Waiting 5 seconds...")
                time.sleep(5)
                # Retry once
                response = requests.post(
                    self.base_url,
                    headers=self.headers,
                    json=payload,
                    timeout=timeout
                )
            
            response.raise_for_status()
            result = response.json()
            
            # Log response
            self._log_response(tool_name, result)
            
            return result
            
        except requests.exceptions.HTTPError as e:
            self.stats['errors'] += 1
            self._log_error(tool_name, str(e))
            raise
    
    def _log_request(self, operation: str, payload: Dict):
        """Log raw request for PRISMA auditability"""
        log_file = self.log_dir / "requests.jsonl"
        with open(log_file, 'a', encoding='utf-8') as f:
            log_entry = {
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'operation': operation,
                'payload': payload
            }
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
    
    def _log_response(self, operation: str, response: Dict):
        """Log raw response for PRISMA auditability"""
        log_file = self.log_dir / "responses.jsonl"
        with open(log_file, 'a', encoding='utf-8') as f:
            log_entry = {
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'operation': operation,
                'response': response
            }
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
    
    def _log_normalized(self, operation: str, records: List[Dict]):
        """Log normalized records for PRISMA auditability"""
        log_file = self.log_dir / "normalized_records.jsonl"
        with open(log_file, 'a', encoding='utf-8') as f:
            log_entry = {
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'operation': operation,
                'count': len(records),
                'records': records
            }
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
    
    def _log_error(self, operation: str, error: str):
        """Log errors"""
        log_file = self.log_dir / "errors.jsonl"
        with open(log_file, 'a', encoding='utf-8') as f:
            log_entry = {
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'operation': operation,
                'error': error
            }
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
    
    def get_stats(self) -> Dict:
        """Return adapter statistics"""
        return self.stats.copy()
    
    def __repr__(self):
        return f"AstaMCPAdapter(window={self.evidence_window_end}, run={self.run_id})"
```

**Validation Test**: `tests/test_asta_adapter.py`

```python
"""
Unit tests for ASTA MCP Adapter
"""
import pytest
import os
from sources.asta_mcp.adapter import AstaMCPAdapter

def test_adapter_initialization():
    """Test adapter initializes correctly"""
    adapter = AstaMCPAdapter(evidence_window_end="2025-01-31")
    
    assert adapter.evidence_window_end == "2025-01-31"
    assert adapter.base_url == "https://asta-tools.allen.ai/mcp/v1"
    assert adapter.run_id is not None
    assert adapter.stats['requests'] == 0

def test_adapter_requires_api_key_warning(capsys):
    """Test warning when API key not set"""
    # Temporarily remove API key
    old_key = os.environ.get('ASTA_TOOL_KEY')
    if old_key:
        del os.environ['ASTA_TOOL_KEY']
    
    adapter = AstaMCPAdapter()
    captured = capsys.readouterr()
    
    assert "Warning: ASTA_TOOL_KEY not set" in captured.out
    
    # Restore key
    if old_key:
        os.environ['ASTA_TOOL_KEY'] = old_key

def test_log_directory_creation():
    """Test that log directory is created"""
    adapter = AstaMCPAdapter()
    
    assert adapter.log_dir.exists()
    assert adapter.log_dir.is_dir()

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
```

**Run Tests**:
```powershell
# Install pytest if needed
pip install pytest

# Run tests
python -m pytest tests/test_asta_adapter.py -v
```

**Acceptance Criteria**:
- ✅ `AstaMCPAdapter` class created
- ✅ Logging infrastructure works
- ✅ All unit tests pass
- ✅ Code follows ELIS conventions (type hints, docstrings)

**Git Commit**:
```powershell
git add sources/asta_mcp/adapter.py tests/test_asta_adapter.py
git commit -m "feat: implement base ASTA MCP adapter with logging"
git push
```

---

#### **Step 1.2: Implement Discovery Mode - search_candidates()**

**Objective**: Add paper search capability for vocabulary bootstrapping

**Add to `sources/asta_mcp/adapter.py`**:

```python
    # Add to AstaMCPAdapter class
    
    def search_candidates(self, 
                         query: str, 
                         limit: int = 100,
                         venues: Optional[List[str]] = None) -> List[Dict]:
        """
        Discovery mode: Find candidate papers for scoping/vocabulary
        
        This is NOT a canonical search - it's exploratory.
        Use results to:
        1. Extract vocabulary for Boolean queries
        2. Identify key authors/venues
        3. Generate seed papers for snowballing
        
        Args:
            query: Natural language research question
            limit: Max results (default 100)
            venues: Optional list of venue names to filter by
        
        Returns:
            List of candidate papers (NOT yet screened by ELIS criteria)
            
        Example:
            >>> adapter = AstaMCPAdapter()
            >>> papers = adapter.search_candidates(
            ...     query="electoral integrity voting technology",
            ...     limit=50
            ... )
            >>> print(f"Found {len(papers)} candidates")
        """
        
        arguments = {
            "keyword": query,
            "fields": "title,abstract,authors,year,doi,url,venue,fieldsOfStudy,citationCount,isOpenAccess",
            "limit": limit,
            "publication_date_range": f"2000-01-01:{self.evidence_window_end}"
        }
        
        if venues:
            arguments["venues"] = ",".join(venues)
        
        result = self._call_mcp_tool("search_papers_by_relevance", arguments)
        
        # Extract and normalize papers
        papers = self._extract_papers_from_mcp(result)
        
        # Log normalized records
        self._log_normalized("search_candidates", papers)
        
        print(f"✅ Found {len(papers)} candidate papers for: '{query}'")
        
        return papers
    
    def _extract_papers_from_mcp(self, mcp_response: Dict) -> List[Dict]:
        """
        Extract and normalize papers from MCP response
        
        MCP returns: {'content': [{'type': 'text', 'text': '<json>'}]}
        """
        papers = []
        
        content = mcp_response.get('content', [])
        
        for item in content:
            if item.get('type') == 'text':
                text = item.get('text', '')
                
                # Try to parse as JSON
                try:
                    data = json.loads(text)
                    
                    # Handle different response formats
                    if 'data' in data:
                        # Semantic Scholar API format
                        for paper in data['data']:
                            papers.append(self._normalize_paper(paper))
                    elif isinstance(data, list):
                        # Direct list format
                        for paper in data:
                            papers.append(self._normalize_paper(paper))
                    elif isinstance(data, dict) and 'paperId' in data:
                        # Single paper format
                        papers.append(self._normalize_paper(data))
                        
                except json.JSONDecodeError:
                    # Not JSON, skip
                    continue
        
        return papers
    
    def _normalize_paper(self, asta_paper: Dict) -> Dict:
        """
        Normalize ASTA paper to ELIS schema
        
        ELIS schema fields:
        - source, title, authors, year, doi, abstract, url, venue, etc.
        """
        return {
            'source': 'ASTA_MCP',
            'asta_id': asta_paper.get('paperId'),
            'corpus_id': asta_paper.get('corpusId'),
            'title': asta_paper.get('title', ''),
            'authors': [
                author.get('name', '') 
                for author in asta_paper.get('authors', [])
            ],
            'year': asta_paper.get('year'),
            'doi': self._extract_doi(asta_paper),
            'arxiv_id': self._extract_arxiv_id(asta_paper),
            'abstract': asta_paper.get('abstract', ''),
            'url': asta_paper.get('url', ''),
            'venue': asta_paper.get('venue', ''),
            'publication_date': asta_paper.get('publicationDate'),
            'fields_of_study': asta_paper.get('fieldsOfStudy', []),
            'is_open_access': asta_paper.get('isOpenAccess', False),
            'citation_count': asta_paper.get('citationCount', 0),
            'tldr': self._extract_tldr(asta_paper),
            'retrieved_at': datetime.utcnow().isoformat() + 'Z',
            'evidence_window': self.evidence_window_end
        }
    
    def _extract_doi(self, paper: Dict) -> Optional[str]:
        """Extract DOI from externalIds"""
        external_ids = paper.get('externalIds', {})
        return external_ids.get('DOI') if external_ids else None
    
    def _extract_arxiv_id(self, paper: Dict) -> Optional[str]:
        """Extract ArXiv ID from externalIds"""
        external_ids = paper.get('externalIds', {})
        return external_ids.get('ArXiv') if external_ids else None
    
    def _extract_tldr(self, paper: Dict) -> Optional[str]:
        """Extract TL;DR summary"""
        tldr = paper.get('tldr')
        return tldr.get('text') if tldr and isinstance(tldr, dict) else None
```

**Test File**: Add to `tests/test_asta_adapter.py`

```python
def test_search_candidates_basic(mocker):
    """Test basic search_candidates functionality"""
    # Mock the MCP API call
    mock_response = {
        'content': [{
            'type': 'text',
            'text': json.dumps({
                'data': [{
                    'paperId': 'abc123',
                    'title': 'Test Paper',
                    'authors': [{'name': 'John Doe'}],
                    'year': 2024,
                    'abstract': 'Test abstract',
                    'venue': 'Test Conference'
                }]
            })
        }]
    }
    
    mocker.patch.object(
        AstaMCPAdapter,
        '_call_mcp_tool',
        return_value=mock_response
    )
    
    adapter = AstaMCPAdapter()
    papers = adapter.search_candidates("test query", limit=10)
    
    assert len(papers) == 1
    assert papers[0]['title'] == 'Test Paper'
    assert papers[0]['source'] == 'ASTA_MCP'

@pytest.mark.integration
def test_search_candidates_real_api():
    """
    Integration test with real ASTA API
    Requires ASTA_TOOL_KEY in environment
    """
    if not os.getenv('ASTA_TOOL_KEY'):
        pytest.skip("ASTA_TOOL_KEY not set")
    
    adapter = AstaMCPAdapter()
    papers = adapter.search_candidates(
        query="electoral integrity technology",
        limit=5
    )
    
    assert len(papers) > 0
    assert all('title' in p for p in papers)
    assert all('source' in p for p in papers)
    
    print(f"\n✅ Real API test: Found {len(papers)} papers")
```

**Run Tests**:
```powershell
# Unit tests (with mocking)
python -m pytest tests/test_asta_adapter.py -v -k "not integration"

# Integration test (requires API key)
python -m pytest tests/test_asta_adapter.py -v -m integration
```

**Acceptance Criteria**:
- ✅ `search_candidates()` method works
- ✅ Paper normalization to ELIS schema
- ✅ Logging captures all requests/responses
- ✅ Unit tests pass
- ✅ Integration test with real API succeeds

**Git Commit**:
```powershell
git add sources/asta_mcp/adapter.py tests/test_asta_adapter.py
git commit -m "feat: implement search_candidates() for discovery mode"
git push
```

---

#### **Step 1.3: Implement Evidence Mode - snippet_search()**

**Objective**: Add snippet search for evidence localization

**Add to `sources/asta_mcp/adapter.py`**:

```python
    # Add to AstaMCPAdapter class
    
    def find_snippets(self,
                     query: str,
                     paper_ids: Optional[List[str]] = None,
                     venues: Optional[List[str]] = None,
                     limit: int = 100) -> List[Dict]:
        """
        Evidence mode: Find specific evidence snippets from papers
        
        Snippets are ~500-word excerpts from title/abstract/body text.
        
        Use for:
        1. Screening assistance - pre-fill relevance checks
        2. Extraction support - locate specific constructs
        3. Quality assessment - find methodology descriptions
        
        Args:
            query: Specific construct to find (e.g., "audit mechanism")
            paper_ids: Optional - limit to specific papers (max 100)
            venues: Optional - limit to specific venues
            limit: Max snippets to return (default 100, max 250)
        
        Returns:
            List of snippets with provenance
            
        Example:
            >>> adapter = AstaMCPAdapter()
            >>> snippets = adapter.find_snippets(
            ...     query="voter verifiable paper audit trail",
            ...     limit=50
            ... )
            >>> for s in snippets[:3]:
            ...     print(f"{s['paper_title']}: {s['snippet_text'][:100]}...")
        """
        
        arguments = {
            "query": query,
            "limit": min(limit, 250),  # ASTA max is 250
            "inserted_before": self.evidence_window_end
        }
        
        if paper_ids:
            # Limit to 100 paper IDs (ASTA constraint)
            arguments["paper_ids"] = ",".join(paper_ids[:100])
        
        if venues:
            arguments["venues"] = ",".join(venues)
        
        result = self._call_mcp_tool("snippet_search", arguments, timeout=60)
        
        # Extract snippets
        snippets = self._extract_snippets_from_mcp(result)
        
        # Log normalized snippets
        self._log_normalized("find_snippets", snippets)
        
        print(f"✅ Found {len(snippets)} snippets for: '{query}'")
        
        return snippets
    
    def _extract_snippets_from_mcp(self, mcp_response: Dict) -> List[Dict]:
        """
        Extract snippets from MCP response
        
        Snippet format:
        {
            'snippet_text': '...',
            'paper_id': '...',
            'paper_title': '...',
            'score': float
        }
        """
        snippets = []
        
        content = mcp_response.get('content', [])
        
        for item in content:
            if item.get('type') == 'text':
                text = item.get('text', '')
                
                try:
                    data = json.loads(text)
                    
                    # Handle different response formats
                    if 'data' in data:
                        for snippet in data['data']:
                            snippets.append(self._normalize_snippet(snippet))
                    elif isinstance(data, list):
                        for snippet in data:
                            snippets.append(self._normalize_snippet(snippet))
                    elif isinstance(data, dict) and 'snippet' in data:
                        snippets.append(self._normalize_snippet(data))
                        
                except json.JSONDecodeError:
                    continue
        
        return snippets
    
    def _normalize_snippet(self, asta_snippet: Dict) -> Dict:
        """Normalize ASTA snippet to ELIS schema"""
        return {
            'snippet_text': asta_snippet.get('snippet', asta_snippet.get('text', '')),
            'paper_id': asta_snippet.get('paperId', asta_snippet.get('paper_id', '')),
            'paper_title': asta_snippet.get('title', ''),
            'paper_year': asta_snippet.get('year'),
            'paper_doi': asta_snippet.get('doi'),
            'score': asta_snippet.get('score', 0.0),
            'snippet_source': 'ASTA_MCP',
            'retrieved_at': datetime.utcnow().isoformat() + 'Z'
        }
```

**Add Test**:

```python
def test_find_snippets_basic(mocker):
    """Test basic find_snippets functionality"""
    mock_response = {
        'content': [{
            'type': 'text',
            'text': json.dumps({
                'data': [{
                    'snippet': 'Test snippet text about voting',
                    'paperId': 'xyz789',
                    'title': 'Voting Systems',
                    'year': 2023,
                    'score': 0.95
                }]
            })
        }]
    }
    
    mocker.patch.object(
        AstaMCPAdapter,
        '_call_mcp_tool',
        return_value=mock_response
    )
    
    adapter = AstaMCPAdapter()
    snippets = adapter.find_snippets("voting technology", limit=10)
    
    assert len(snippets) == 1
    assert 'voting' in snippets[0]['snippet_text'].lower()
    assert snippets[0]['snippet_source'] == 'ASTA_MCP'
```

**Acceptance Criteria**:
- ✅ `find_snippets()` method works
- ✅ Snippet normalization works
- ✅ Paper ID filtering works
- ✅ Tests pass

**Git Commit**:
```powershell
git add sources/asta_mcp/adapter.py tests/test_asta_adapter.py
git commit -m "feat: implement find_snippets() for evidence mode"
git push
```

---

#### **Step 1.4: Implement get_paper() for Metadata Enrichment**

**Add to `sources/asta_mcp/adapter.py`**:

```python
    # Add to AstaMCPAdapter class
    
    def get_paper(self, paper_id: str) -> Optional[Dict]:
        """
        Fetch full metadata for a specific paper
        
        Supports multiple ID formats:
        - Semantic Scholar ID: abc123...
        - CorpusId:12345
        - DOI:10.1234/xyz
        - ArXiv:2101.12345
        - PMID:12345678
        - URL:https://arxiv.org/abs/...
        
        Args:
            paper_id: Paper identifier in any supported format
        
        Returns:
            Full paper metadata or None if not found
            
        Example:
            >>> adapter = AstaMCPAdapter()
            >>> paper = adapter.get_paper("DOI:10.1145/1234567")
            >>> if paper:
            ...     print(f"Title: {paper['title']}")
            ...     print(f"Citations: {paper['citation_count']}")
        """
        
        arguments = {
            "paper_id": paper_id,
            "fields": "title,abstract,authors,year,doi,url,venue,publicationDate,references,citations,fieldsOfStudy,isOpenAccess,citationCount,tldr"
        }
        
        try:
            result = self._call_mcp_tool("get_papers", arguments, timeout=15)
            
            # Extract single paper
            papers = self._extract_papers_from_mcp(result)
            
            if papers:
                paper = papers[0]
                self._log_normalized("get_paper", [paper])
                print(f"✅ Retrieved paper: {paper.get('title', 'Unknown')[:60]}...")
                return paper
            else:
                print(f"⚠️  Paper not found: {paper_id}")
                return None
                
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                print(f"⚠️  Paper not found: {paper_id}")
                return None
            raise
```

**Add Test**:

```python
@pytest.mark.integration
def test_get_paper_real_api():
    """Test fetching a real paper by DOI"""
    if not os.getenv('ASTA_TOOL_KEY'):
        pytest.skip("ASTA_TOOL_KEY not set")
    
    adapter = AstaMCPAdapter()
    
    # Use a known DOI
    paper = adapter.get_paper("DOI:10.1145/3411764.3445518")
    
    assert paper is not None
    assert 'title' in paper
    assert 'authors' in paper
    assert len(paper['authors']) > 0
    
    print(f"\n✅ Retrieved: {paper['title']}")
```

**Acceptance Criteria**:
- ✅ `get_paper()` works with multiple ID formats
- ✅ Returns None for non-existent papers
- ✅ Tests pass

**Git Commit**:
```powershell
git add sources/asta_mcp/adapter.py tests/test_asta_adapter.py
git commit -m "feat: implement get_paper() for metadata enrichment"
git push
```

---

### **PHASE 2: Vocabulary Extraction (Week 1, Day 5 - Week 2, Day 1)**

#### **Step 2.1: Create Vocabulary Extraction Module**

**Objective**: Build vocabulary extraction from ASTA candidates

**File**: `sources/asta_mcp/vocabulary.py`

```python
"""
Vocabulary extraction from ASTA candidate papers
Extracts: terms, venues, authors, fields of study
Purpose: Enhance Boolean queries for canonical databases (Scopus/WoS)
"""

from collections import Counter
from typing import List, Dict
import re
from pathlib import Path
import yaml

class VocabularyExtractor:
    """
    Extract searchable vocabulary from ASTA candidate papers
    
    Output used to enhance ELIS Boolean queries for Scopus, WoS, etc.
    """
    
    def __init__(self):
        # Common stopwords to exclude
        self.stopwords = {
            'that', 'this', 'with', 'from', 'have', 'were', 'been',
            'their', 'which', 'these', 'such', 'than', 'more', 'other',
            'also', 'when', 'there', 'they', 'each', 'some', 'about',
            'into', 'through', 'during', 'before', 'after', 'above',
            'below', 'between', 'under', 'again', 'further', 'then',
            'once', 'here', 'there', 'where', 'what', 'while', 'both'
        }
    
    def extract(self, candidate_papers: List[Dict]) -> Dict:
        """
        Extract vocabulary from candidate papers
        
        Args:
            candidate_papers: List of papers from ASTA search_candidates()
        
        Returns:
            {
                'key_terms': [...],
                'venues': [...],
                'authors': [...],
                'fields_of_study': [...],
                'statistics': {...}
            }
        """
        
        all_terms = []
        venues = []
        authors = []
        fields = []
        
        for paper in candidate_papers:
            # Extract fields of study
            fields.extend(paper.get('fields_of_study', []))
            
            # Extract venue
            if paper.get('venue'):
                venues.append(paper['venue'])
            
            # Extract authors
            for author in paper.get('authors', []):
                if author:
                    authors.append(author)
            
            # Extract terms from title and abstract
            title = paper.get('title', '').lower()
            abstract = paper.get('abstract', '').lower()
            
            # Extract multi-word phrases (bigrams, trigrams)
            phrases = self._extract_phrases(title, abstract)
            all_terms.extend(phrases)
            
            # Extract single words
            words = re.findall(r'\b[a-z]{4,}\b', f"{title} {abstract}")
            all_terms.extend(words)
        
        # Count frequencies
        term_counts = Counter([t for t in all_terms if t not in self.stopwords])
        venue_counts = Counter(venues)
        author_counts = Counter(authors)
        field_counts = Counter(fields)
        
        vocabulary = {
            'key_terms': [
                {'term': term, 'count': count} 
                for term, count in term_counts.most_common(100)
            ],
            'venues': [
                {'venue': venue, 'count': count} 
                for venue, count in venue_counts.most_common(30)
            ],
            'authors': [
                {'author': author, 'count': count} 
                for author, count in author_counts.most_common(50)
            ],
            'fields_of_study': [
                {'field': field, 'count': count} 
                for field, count in field_counts.most_common(20)
            ],
            'statistics': {
                'total_papers': len(candidate_papers),
                'unique_terms': len(term_counts),
                'unique_venues': len(venue_counts),
                'unique_authors': len(author_counts),
                'unique_fields': len(field_counts)
            }
        }
        
        return vocabulary
    
    def _extract_phrases(self, title: str, abstract: str) -> List[str]:
        """
        Extract meaningful multi-word phrases
        
        Focus on:
        - Technical terms (e.g., "risk-limiting audit")
        - Method names (e.g., "end-to-end verification")
        - Domain concepts (e.g., "voter registration database")
        """
        text = f"{title} {abstract}"
        
        # Simple bigram and trigram extraction
        words = re.findall(r'\b[a-z]+\b', text)
        
        bigrams = [
            f"{words[i]} {words[i+1]}" 
            for i in range(len(words)-1)
            if words[i] not in self.stopwords and words[i+1] not in self.stopwords
        ]
        
        trigrams = [
            f"{words[i]} {words[i+1]} {words[i+2]}" 
            for i in range(len(words)-2)
            if all(w not in self.stopwords for w in words[i:i+3])
        ]
        
        return bigrams + trigrams
    
    def save_to_yaml(self, vocabulary: Dict, output_file: Path):
        """Save vocabulary to YAML for use in query design"""
        with open(output_file, 'w', encoding='utf-8') as f:
            yaml.dump(vocabulary, f, default_flow_style=False, allow_unicode=True)
        
        print(f"💾 Vocabulary saved to: {output_file}")
    
    def generate_boolean_suggestions(self, vocabulary: Dict, top_n: int = 20) -> List[str]:
        """
        Generate Boolean query suggestions from vocabulary
        
        Returns:
            List of suggested search terms for Scopus/WoS
        """
        suggestions = []
        
        # Top terms
        top_terms = [item['term'] for item in vocabulary['key_terms'][:top_n]]
        
        # Group related terms
        # (This is simplified - in practice, use semantic clustering)
        suggestions.append(f"# Top {top_n} terms from ASTA discovery:")
        suggestions.append(" OR ".join([f'"{term}"' for term in top_terms]))
        
        return suggestions
```

**Test File**: `tests/test_vocabulary.py`

```python
"""
Tests for vocabulary extraction
"""
import pytest
from sources.asta_mcp.vocabulary import VocabularyExtractor

def test_vocabulary_extraction():
    """Test vocabulary extraction from sample papers"""
    
    sample_papers = [
        {
            'title': 'Risk-Limiting Audit for Election Integrity',
            'abstract': 'This paper presents a risk-limiting audit method for verifying election results.',
            'authors': ['Alice Smith', 'Bob Jones'],
            'venue': 'USENIX Security',
            'fields_of_study': ['Computer Science', 'Election Security']
        },
        {
            'title': 'Voter Registration Database Management',
            'abstract': 'We propose a secure voter registration database system.',
            'authors': ['Alice Smith', 'Carol White'],
            'venue': 'ACM CCS',
            'fields_of_study': ['Computer Science', 'Database Systems']
        }
    ]
    
    extractor = VocabularyExtractor()
    vocab = extractor.extract(sample_papers)
    
    assert 'key_terms' in vocab
    assert 'venues' in vocab
    assert 'authors' in vocab
    assert 'fields_of_study' in vocab
    assert 'statistics' in vocab
    
    assert vocab['statistics']['total_papers'] == 2
    assert vocab['statistics']['unique_authors'] == 3  # Alice, Bob, Carol
    
    # Check top author
    top_author = vocab['authors'][0]
    assert top_author['author'] == 'Alice Smith'
    assert top_author['count'] == 2

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
```

**Acceptance Criteria**:
- ✅ Vocabulary extraction works
- ✅ Phrase extraction captures multi-word terms
- ✅ Output saved as YAML
- ✅ Tests pass

**Git Commit**:
```powershell
git add sources/asta_mcp/vocabulary.py tests/test_vocabulary.py
git commit -m "feat: implement vocabulary extraction from ASTA candidates"
git push
```

---

#### **Step 2.2: Create Phase 0 Script - Vocabulary Bootstrapping**

**Objective**: User-facing script for vocabulary bootstrapping

**File**: `scripts/phase0_asta_scoping.py`

```python
"""
ELIS Phase 0: ASTA Vocabulary Bootstrapping

Use ASTA to discover vocabulary before finalizing Boolean queries.
This is where ASTA adds the most value to ELIS.

Usage:
    python scripts/phase0_asta_scoping.py

Output:
    - config/asta_extracted_vocabulary.yml
    - runs/<run_id>/asta/*.jsonl (audit logs)
"""

import sys
from pathlib import Path

# Add sources to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sources.asta_mcp.adapter import AstaMCPAdapter
from sources.asta_mcp.vocabulary import VocabularyExtractor
import yaml

def main():
    """
    Execute Phase 0: Vocabulary Bootstrapping
    
    Steps:
    1. Load research questions from config
    2. Query ASTA for candidates
    3. Extract vocabulary
    4. Save for Boolean query enhancement
    """
    
    print("="*70)
    print("ELIS PHASE 0: ASTA VOCABULARY BOOTSTRAPPING")
    print("="*70)
    print()
    
    # Initialize ASTA adapter
    print("🔧 Initializing ASTA adapter...")
    asta = AstaMCPAdapter(evidence_window_end="2025-01-31")
    print(f"   Evidence window: {asta.evidence_window_end}")
    print(f"   Run ID: {asta.run_id}")
    print()
    
    # Research questions (from your ELIS protocol)
    research_questions = [
        "electoral integrity technological strategies effectiveness empirical evidence",
        "voting system security audit trails verification mechanisms",
        "election technology trust voter confidence measurement",
        "biometric authentication voter registration database integrity",
        "blockchain voting transparency auditability end-to-end verification",
        "paper ballot verification hybrid systems election security",
        "risk-limiting audit statistical methods election integrity",
        "voter verifiable paper audit trail VVPAT systems"
    ]
    
    print(f"📋 Research questions: {len(research_questions)}")
    for i, rq in enumerate(research_questions, 1):
        print(f"   {i}. {rq[:60]}...")
    print()
    
    # Collect candidates from ASTA
    all_candidates = []
    
    for i, rq in enumerate(research_questions, 1):
        print(f"🔍 [{i}/{len(research_questions)}] ASTA Discovery: {rq[:50]}...")
        
        try:
            candidates = asta.search_candidates(
                query=rq,
                limit=100  # Get top 100 per query
            )
            
            all_candidates.extend(candidates)
            print(f"   ✅ Found {len(candidates)} candidates")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            continue
    
    print()
    print(f"📊 Total candidates collected: {len(all_candidates)}")
    print()
    
    # Extract vocabulary
    print("📚 Extracting vocabulary...")
    extractor = VocabularyExtractor()
    vocabulary = extractor.extract(all_candidates)
    
    # Display statistics
    stats = vocabulary['statistics']
    print(f"   ✅ Extraction complete:")
    print(f"      - Unique terms: {stats['unique_terms']}")
    print(f"      - Unique venues: {stats['unique_venues']}")
    print(f"      - Unique authors: {stats['unique_authors']}")
    print(f"      - Unique fields: {stats['unique_fields']}")
    print()
    
    # Display top results
    print("🔑 TOP 20 KEY TERMS (use in Boolean queries):")
    for item in vocabulary['key_terms'][:20]:
        print(f"   - {item['term']:40s} (count: {item['count']})")
    print()
    
    print("📖 TOP 15 VENUES:")
    for item in vocabulary['venues'][:15]:
        print(f"   - {item['venue']:50s} (count: {item['count']})")
    print()
    
    print("👥 TOP 20 AUTHORS:")
    for item in vocabulary['authors'][:20]:
        print(f"   - {item['author']:40s} (count: {item['count']})")
    print()
    
    # Save vocabulary
    output_file = Path('config/asta_extracted_vocabulary.yml')
    output_file.parent.mkdir(parents=True, exist_ok=True)
    extractor.save_to_yaml(vocabulary, output_file)
    
    # Generate Boolean suggestions
    print("💡 BOOLEAN QUERY SUGGESTIONS:")
    suggestions = extractor.generate_boolean_suggestions(vocabulary, top_n=15)
    for suggestion in suggestions:
        print(f"   {suggestion}")
    print()
    
    # Display stats
    asta_stats = asta.get_stats()
    print("📈 ASTA API Statistics:")
    print(f"   - Total requests: {asta_stats['requests']}")
    print(f"   - Errors: {asta_stats['errors']}")
    print(f"   - Rate limit hits: {asta_stats['rate_limit_hits']}")
    print()
    
    # Next steps
    print("="*70)
    print("✅ PHASE 0 COMPLETE")
    print("="*70)
    print()
    print("📁 Outputs:")
    print(f"   - Vocabulary: {output_file}")
    print(f"   - Audit logs: runs/{asta.run_id}/asta/")
    print()
    print("🎯 NEXT STEPS:")
    print("   1. Review extracted vocabulary in config/asta_extracted_vocabulary.yml")
    print("   2. Use top terms to enhance Boolean queries in config/elis_search_queries.yml")
    print("   3. Proceed to canonical database harvesting (Scopus, WoS, etc.)")
    print()
    print("💡 TIP: Focus on terms with count > 5 for high-relevance vocabulary")
    print()

if __name__ == '__main__':
    main()
```

**Run Phase 0**:
```powershell
# Execute Phase 0
python scripts/phase0_asta_scoping.py
```

**Acceptance Criteria**:
- ✅ Script runs without errors
- ✅ Vocabulary saved to `config/asta_extracted_vocabulary.yml`
- ✅ Audit logs created in `runs/<run_id>/asta/`
- ✅ Output includes actionable vocabulary

**Git Commit**:
```powershell
git add scripts/phase0_asta_scoping.py
git commit -m "feat: add Phase 0 vocabulary bootstrapping script"
git push
```

---

### **PHASE 3: Configuration and Documentation (Week 2, Days 2-3)**

#### **Step 3.1: Create ASTA Configuration File**

**File**: `config/asta_config.yml`

```yaml
# ASTA MCP Integration Configuration
# ELIS SLR Agent - Electoral Integrity Strategies

asta_mcp:
  # MCP endpoint
  endpoint: "https://asta-tools.allen.ai/mcp/v1"
  
  # Evidence window (frozen cutoff for reproducibility)
  evidence_window_end: "2025-01-31"
  
  # Operating modes
  modes:
    discovery:
      enabled: true
      default_limit: 100
      max_limit: 500
    
    evidence:
      enabled: true
      default_snippet_limit: 100
      max_snippet_limit: 250
  
  # API configuration
  api:
    timeout_seconds: 30
    retry_on_rate_limit: true
    retry_delay_seconds: 5
  
  # Logging
  logging:
    enabled: true
    log_requests: true
    log_responses: true
    log_normalized: true
    log_directory: "runs"
  
  # Integration policy
  policy:
    canonical_sources:
      - scopus
      - wos
      - ieee
      - semanticscholar
      - openalex
      - crossref
      - core
      - googlescholar
    
    asta_role: "discovery_and_evidence_assistant"
    decision_authority: "ELIS"
    audit_requirement: "all_operations_logged"

# Phase execution parameters
phases:
  phase0_vocabulary:
    research_questions:
      - "electoral integrity technological strategies effectiveness"
      - "voting system security audit trails verification"
      - "election technology trust voter confidence"
      - "biometric authentication voter registration"
      - "blockchain voting transparency auditability"
      - "paper ballot verification hybrid systems"
      - "risk-limiting audit statistical methods"
      - "voter verifiable paper audit trail VVPAT"
    
    candidates_per_query: 100
    vocabulary_top_terms: 100
    vocabulary_top_venues: 30
    vocabulary_top_authors: 50
  
  phase2_screening:
    snippet_queries:
      - "audit mechanism"
      - "verification protocol"
      - "security threat model"
      - "implementation case study"
      - "effectiveness evaluation"
    
    snippets_per_query: 100

# PRISMA compliance
prisma:
  asta_contribution_reporting:
    - "Papers proposed by ASTA"
    - "Papers uniquely found by ASTA"
    - "Vocabulary terms contributed"
    - "Evidence snippets retrieved"
  
  exclusion_policy: "ASTA proposals evaluated against ELIS criteria"
  transparency: "All ASTA operations logged in runs/<run_id>/asta/"
```

**Git Commit**:
```powershell
git add config/asta_config.yml
git commit -m "feat: add ASTA configuration file"
git push
```

---

#### **Step 3.2: Update ELIS Protocol Documentation**

**File**: `docs/ASTA_Integration.md`

```markdown
# ASTA Integration in ELIS SLR Agent

## Overview

ASTA (Allen Institute for AI's Scholarly Trustworthy Agentic AI) is integrated into the ELIS SLR Agent as a **discovery and evidence-localization assistant** via the ASTA Scientific Corpus Tool (Model Context Protocol).

**Critical Policy**: "ASTA proposes, ELIS decides"  
ASTA is NOT a canonical search source. Canonical sources remain:
- Scopus
- Web of Science
- IEEE Xplore
- Semantic Scholar
- OpenAlex
- CrossRef
- CORE
- Google Scholar

## Integration Architecture

### ASTA Role in ELIS Workflow

```
Phase 0: Vocabulary Bootstrapping (Pre-Search)
  ↓
  ASTA discovery → Extract terms → Enhance Boolean queries
  ↓
Phase 1: Canonical Database Harvesting
  ↓
  Scopus, WoS, etc. (using ASTA-enhanced queries)
  ↓
Phase 2: ASTA-Assisted Screening
  ↓
  ASTA snippet search → Pre-fill evidence → Human decides
  ↓
Phase 3: ASTA Evidence Localization
  ↓
  Targeted snippets → Extract constructs → Human validates
```

## Reproducibility Controls

### 1. Frozen Evidence Window

All ASTA queries use `evidence_window_end = 2025-01-31` to ensure:
- Papers are from before knowledge cutoff
- Reproducible results across runs
- Temporal consistency with benchmark

### 2. Verbatim Logging

All ASTA operations logged in `runs/<run_id>/asta/`:
- `requests.jsonl` - All MCP requests
- `responses.jsonl` - All MCP responses
- `normalized_records.jsonl` - Normalized papers/snippets
- `errors.jsonl` - Error logs

### 3. Canonical Independence

**Policy**: ASTA proposes candidates and locates evidence. ELIS criteria determine inclusion/exclusion.

This ensures:
- PRISMA compliance
- Audit trail clarity
- No "black box" screening

## Usage

### Phase 0: Vocabulary Bootstrapping

```bash
python scripts/phase0_asta_scoping.py
```

**Output**:
- `config/asta_extracted_vocabulary.yml`
- Vocabulary for enhancing Boolean queries

### Phase 2: Screening Assistance (Future)

```bash
python scripts/phase2_asta_screening.py --papers included_candidates.json
```

**Output**:
- Evidence snippets for each paper
- Pre-filled relevance assessments

### Phase 3: Evidence Localization (Future)

```bash
python scripts/phase3_asta_extraction.py --papers final_included.json
```

**Output**:
- Targeted snippets for data extraction
- Construct-specific evidence

## PRISMA Reporting

### Methods Section Template

```
2.3 ASTA Integration - Discovery and Evidence Localization

ASTA (Allen AI) was integrated as a discovery and evidence-localization
assistant via the ASTA Scientific Corpus Tool (MCP). ASTA is NOT counted 
as a canonical search source.

Phase 0 - Vocabulary Bootstrapping:
- ASTA discovery queries on 8 core research questions
- Extracted: 100 key terms, 30 venues, 50 authors
- Enhanced Boolean queries for Scopus/WoS

Reproducibility:
- Evidence window: 2025-01-31
- All operations logged: runs/<run_id>/asta/
- Policy: "ASTA proposes, ELIS decides"

ASTA Contribution:
- Vocabulary terms discovered: XX
- Papers uniquely proposed: XX (XX% subsequently included)
- Evidence snippets: XX across XX papers
```

## API Key

Request ASTA_TOOL_KEY at:
https://share.hsforms.com/1L4hUh20oT3mu8iXJQMV77w3ioxm

Free tier available. Higher limits with API key.

## References

- ASTA Resources: https://allenai.org/asta/resources
- MCP Documentation: https://allenai.org/asta/resources/mcp
- AstaBench: https://github.com/allenai/asta-bench
```

**Git Commit**:
```powershell
git add docs/ASTA_Integration.md
git commit -m "docs: add ASTA integration documentation"
git push
```

---

#### **Step 3.3: Update Main README**

**Add to `README.md`**:

```markdown
## ASTA Integration

ELIS integrates with ASTA (Allen AI) for vocabulary bootstrapping and evidence localization.

### Quick Start

1. Get ASTA_TOOL_KEY: https://share.hsforms.com/1L4hUh20oT3mu8iXJQMV77w3ioxm
2. Add to `.env`: `ASTA_TOOL_KEY=your_key_here`
3. Run Phase 0: `python scripts/phase0_asta_scoping.py`

### Documentation

See [docs/ASTA_Integration.md](docs/ASTA_Integration.md) for full details.

**Policy**: "ASTA proposes, ELIS decides" - ASTA is NOT a canonical search source.
```

**Git Commit**:
```powershell
git add README.md
git commit -m "docs: update README with ASTA integration"
git push
```

---

### **PHASE 4: Testing and Validation (Week 2, Days 4-5)**

#### **Step 4.1: End-to-End Integration Test**

**File**: `tests/test_integration_asta.py`

```python
"""
End-to-end integration tests for ASTA in ELIS
"""
import pytest
import os
from pathlib import Path
import yaml

@pytest.mark.integration
@pytest.mark.slow
def test_phase0_full_workflow():
    """
    Full Phase 0 workflow test
    Requires ASTA_TOOL_KEY
    """
    if not os.getenv('ASTA_TOOL_KEY'):
        pytest.skip("ASTA_TOOL_KEY required")
    
    # Import after path setup
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    
    from sources.asta_mcp.adapter import AstaMCPAdapter
    from sources.asta_mcp.vocabulary import VocabularyExtractor
    
    # Step 1: ASTA discovery
    asta = AstaMCPAdapter(evidence_window_end="2025-01-31")
    
    candidates = asta.search_candidates(
        query="electoral integrity technology",
        limit=20  # Small for testing
    )
    
    assert len(candidates) > 0
    assert all('title' in p for p in candidates)
    
    # Step 2: Vocabulary extraction
    extractor = VocabularyExtractor()
    vocab = extractor.extract(candidates)
    
    assert vocab['statistics']['total_papers'] == len(candidates)
    assert len(vocab['key_terms']) > 0
    
    # Step 3: Save vocabulary
    output_file = Path('tests/test_output/vocabulary.yml')
    output_file.parent.mkdir(parents=True, exist_ok=True)
    extractor.save_to_yaml(vocab, output_file)
    
    assert output_file.exists()
    
    # Step 4: Verify logs
    assert asta.log_dir.exists()
    assert (asta.log_dir / "requests.jsonl").exists()
    assert (asta.log_dir / "responses.jsonl").exists()
    
    print(f"\n✅ Full Phase 0 workflow test passed")
    print(f"   - Candidates: {len(candidates)}")
    print(f"   - Vocabulary terms: {len(vocab['key_terms'])}")
    print(f"   - Logs: {asta.log_dir}")

if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
```

**Run Integration Test**:
```powershell
python -m pytest tests/test_integration_asta.py -v -s -m integration
```

**Acceptance Criteria**:
- ✅ Full workflow executes successfully
- ✅ All components work together
- ✅ Logs are created
- ✅ Output files generated

---

#### **Step 4.2: Benchmark Validation Against Darmawan-2021**

**File**: `tests/test_asta_benchmark.py`

```python
"""
Validate ASTA against Darmawan-2021 benchmark
Check if ASTA finds known relevant papers
"""
import pytest
import os
from pathlib import Path

@pytest.mark.integration
@pytest.mark.benchmark
def test_asta_benchmark_recall():
    """
    Test if ASTA finds papers from Darmawan-2021 benchmark
    """
    if not os.getenv('ASTA_TOOL_KEY'):
        pytest.skip("ASTA_TOOL_KEY required")
    
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    
    from sources.asta_mcp.adapter import AstaMCPAdapter
    
    # Load benchmark DOIs (from your Darmawan benchmark)
    # This is a sample - replace with actual benchmark DOIs
    benchmark_dois = [
        "10.1145/3274694.3274743",  # Sample DOI
        "10.1109/SP.2019.00009",     # Sample DOI
        # Add actual Darmawan benchmark DOIs
    ]
    
    asta = AstaMCPAdapter(evidence_window_end="2025-01-31")
    
    # Search broadly
    candidates = asta.search_candidates(
        query="electoral integrity voting systems verification",
        limit=200
    )
    
    # Check how many benchmark papers were found
    found_dois = {p.get('doi') for p in candidates if p.get('doi')}
    benchmark_found = found_dois & set(benchmark_dois)
    
    recall = len(benchmark_found) / len(benchmark_dois) if benchmark_dois else 0
    
    print(f"\n📊 ASTA Benchmark Validation:")
    print(f"   Benchmark papers: {len(benchmark_dois)}")
    print(f"   Found by ASTA: {len(benchmark_found)}")
    print(f"   Recall: {recall:.1%}")
    
    # Log which papers were found/missed
    print(f"\n✅ Found:")
    for doi in benchmark_found:
        print(f"   - {doi}")
    
    if set(benchmark_dois) - benchmark_found:
        print(f"\n❌ Missed:")
        for doi in set(benchmark_dois) - benchmark_found:
            print(f"   - {doi}")
    
    # Assertion: Should find at least 60% of benchmark papers
    assert recall >= 0.6, f"ASTA recall too low: {recall:.1%}"

if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
```

**Acceptance Criteria**:
- ✅ ASTA finds ≥60% of Darmawan benchmark papers
- ✅ Benchmark validation documented

---

### **PHASE 5: Deployment and Merge (Week 2, Day 5)**

#### **Step 5.1: Pre-Merge Checklist**

```powershell
# Run all tests
python -m pytest tests/ -v

# Check code style
flake8 sources/asta_mcp/ scripts/phase0_asta_scoping.py

# Verify documentation complete
Get-Content docs/ASTA_Integration.md
Get-Content README.md

# Check Git status
git status
git log --oneline -10
```

**Pre-Merge Requirements**:
- ✅ All tests pass
- ✅ Documentation complete
- ✅ Code reviewed
- ✅ No sensitive data in commits
- ✅ `.env` in `.gitignore`

---

#### **Step 5.2: Create Pull Request**

```powershell
# Push final changes
git push origin feature/asta-integration

# Create PR on GitHub
# Title: "feat: ASTA MCP integration for vocabulary bootstrapping"
# Description: Include testing results, documentation links
```

**PR Template**:
```markdown
## ASTA Integration - Phase 0 Implementation

### Changes
- ✅ ASTA MCP adapter (`sources/asta_mcp/adapter.py`)
- ✅ Vocabulary extraction (`sources/asta_mcp/vocabulary.py`)
- ✅ Phase 0 script (`scripts/phase0_asta_scoping.py`)
- ✅ Configuration (`config/asta_config.yml`)
- ✅ Documentation (`docs/ASTA_Integration.md`)
- ✅ Tests (unit + integration)

### Testing
- Unit tests: XX passing
- Integration tests: XX passing
- Benchmark validation: XX% recall on Darmawan-2021

### Documentation
- [ASTA Integration Guide](docs/ASTA_Integration.md)
- README updated
- All code documented with docstrings

### Next Steps
- Phase 2: Screening assistance
- Phase 3: Evidence localization

### Policy
**"ASTA proposes, ELIS decides"** - ASTA is NOT a canonical search source
```

---

#### **Step 5.3: Merge to Main**

```powershell
# After PR approval, merge
git checkout main
git pull origin main
git merge feature/asta-integration
git push origin main

# Tag the release
git tag -a v0.2.0-asta-phase0 -m "ASTA Phase 0: Vocabulary Bootstrapping"
git push origin v0.2.0-asta-phase0
```

---

## Testing Strategy

### Unit Tests
- `test_asta_adapter.py` - Adapter functionality
- `test_vocabulary.py` - Vocabulary extraction
- Mock MCP API responses

### Integration Tests
- `test_integration_asta.py` - Full Phase 0 workflow
- Real ASTA API calls (requires key)

### Benchmark Tests
- `test_asta_benchmark.py` - Darmawan-2021 validation
- Measure recall on known papers

### Test Execution

```powershell
# All tests (unit + integration)
python -m pytest tests/ -v

# Unit tests only (fast)
python -m pytest tests/ -v -k "not integration"

# Integration tests (requires API key)
python -m pytest tests/ -v -m integration

# Benchmark tests
python -m pytest tests/ -v -m benchmark

# With coverage
pip install pytest-cov
python -m pytest tests/ --cov=sources.asta_mcp --cov-report=html
```

---

## Documentation Requirements

### Code Documentation
- ✅ All functions have docstrings
- ✅ Type hints for all parameters
- ✅ Example usage in docstrings

### User Documentation
- ✅ `docs/ASTA_Integration.md` - Full integration guide
- ✅ `README.md` - Quick start section
- ✅ `config/asta_config.yml` - Inline comments

### PRISMA Documentation
- ✅ Methods section template
- ✅ Contribution reporting framework
- ✅ Audit log specifications

---

## Risk Mitigation

### Risk 1: API Rate Limits

**Mitigation**:
- ✅ Implement retry logic with backoff
- ✅ Log all rate limit hits
- ✅ Recommend getting ASTA_TOOL_KEY
- ✅ Phase 0 limited to reasonable query count

### Risk 2: MCP API Changes

**Mitigation**:
- ✅ Version lock MCP endpoint
- ✅ Comprehensive error logging
- ✅ Tests catch breaking changes
- ✅ Document API version used

### Risk 3: PRISMA Non-Compliance

**Mitigation**:
- ✅ "ASTA proposes, ELIS decides" policy
- ✅ All operations logged
- ✅ Clear documentation of ASTA role
- ✅ ASTA NOT counted as canonical source

### Risk 4: Data Loss

**Mitigation**:
- ✅ All outputs saved (vocabulary, logs)
- ✅ Git version control
- ✅ Run IDs for reproducibility
- ✅ Backup logs directory

---

## Success Criteria

### Phase 0 Success Metrics

- ✅ Vocabulary extracted from ASTA
- ✅ ≥50 high-quality search terms identified
- ✅ ≥20 relevant venues identified
- ✅ All operations logged for audit
- ✅ Darmawan benchmark recall ≥60%
- ✅ Zero PRISMA compliance issues

### Code Quality

- ✅ All tests passing
- ✅ Test coverage ≥80%
- ✅ No linting errors
- ✅ Complete documentation

### Integration Quality

- ✅ Works with existing ELIS infrastructure
- ✅ No breaking changes to current workflow
- ✅ Clear separation of concerns
- ✅ Extensible for Phase 2 & 3

---

## Timeline Summary

| Phase | Duration | Deliverables |
|-------|----------|--------------|
| Phase 0: Setup | Days 1-2 | Environment, directories, dependencies |
| Phase 1: Core Adapter | Days 3-5 | MCP client, search, snippets, metadata |
| Phase 2: Vocabulary | Days 5-6 | Extraction module, Phase 0 script |
| Phase 3: Configuration | Days 7-8 | Config files, documentation |
| Phase 4: Testing | Days 9-10 | Unit tests, integration tests, benchmark |
| Phase 5: Deployment | Day 10 | PR, merge, release |

**Total: ~10 working days (2 weeks)**

---

## Future Phases (Not in Current Plan)

### Phase 2: Screening Assistance
- Snippet search during screening
- Pre-fill relevance evidence
- Human validation workflow

### Phase 3: Evidence Localization
- Targeted snippet extraction
- Construct-specific queries
- Extraction field pre-population

---

## Conclusion

This development plan provides a systematic, testable approach to integrating ASTA into ELIS while:
- Maintaining PRISMA compliance
- Preserving existing workflow
- Creating audit trails
- Following "ASTA proposes, ELIS decides" policy

**Next Action**: Begin with Step 0.1 (Get ASTA Tool Key)
