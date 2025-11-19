# ELIS SLR Agent

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Protocol](https://img.shields.io/badge/protocol-v1.8-purple.svg)](docs/ELIS_2025_SLR_Protocol_v1.8.pdf)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

> **Electoral Integrity Strategies - Systematic Literature Review Agent**  
> Open-source Python workflow for systematic literature reviews on electoral integrity, developed at Imperial College Business School.

---

## Table of Contents
- [What This Project Is](#what-this-project-is)
- [Why This Project Exists](#why-this-project-exists)
- [Information Sources](#information-sources)
- [How It Works](#how-it-works)
- [Project Structure](#project-structure)
- [Quick Start](#quick-start)
- [Usage Guide](#usage-guide)
- [Methodology](#methodology)
- [Current Status](#current-status)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [Documentation](#documentation)
- [Citation](#citation)
- [Acknowledgments](#acknowledgments)

---

## What This Project Is

The ELIS SLR Agent is a **reproducible, API-driven pipeline** for conducting systematic literature reviews in political science and electoral studies. It automates the retrieval, screening, and synthesis of academic literature across multiple databases.

**Key capabilities:**
- ✅ **Multi-source harvesting** — Queries 7 academic databases via APIs
- ✅ **Reproducible searches** — Version-controlled queries and configurations
- ✅ **Automated validation** — Schema-based data quality checks
- ✅ **Open methodology** — Full transparency and audit trail via GitHub
- ✅ **AI-assisted workflow** — LLM integration with human oversight

**Research Question:**  
*What operational and technological strategies have been shown to improve the integrity or auditability of electoral systems since 1990?*

**Principal Investigator:** Carlos Rocha (Imperial College Business School)  
**Supervisor:** Prof. Tommaso Valletti  
**Sponsor:** Instituto Voto Legal (IVL), São Paulo, Brazil

---

## Why This Project Exists

### The Research Problem

Electoral integrity is fundamental to democratic legitimacy, yet systematic evidence on what actually works remains fragmented across disciplines. Existing literature reviews tend to focus on:
- Single technologies (e.g., electronic voting security)
- Narrow aspects (e.g., voter turnout)
- Single countries or regions

**No consolidated review exists** that jointly examines technological, operational, and institutional strategies across both electronic and paper-based voting systems.

### The Solution

This project conducts a **comprehensive, interdisciplinary systematic review** covering:
- 🗳️ **Voting technologies** (electronic, paper, hybrid systems)
- ⚙️ **Operational mechanisms** (audits, transparency measures)
- 🏛️ **Institutional frameworks** (oversight, legal requirements)
- 🌍 **Global scope** (comparative evidence from 1990-2025)

### Impact

The synthesis aims to:
- 📊 **Inform policy design** — Evidence-based electoral reform recommendations
- 🔬 **Identify research gaps** — Guide future academic inquiry
- 🌐 **Support practitioners** — Actionable insights for election administrators
- 🎓 **Advance methodology** — Demonstrate AI-assisted systematic reviews

---

## Information Sources

### Overview

The review queries **7 academic databases** providing comprehensive coverage across political science, computer science, law, and governance. All sources provide documented APIs enabling reproducible automated searches.

### Implemented Sources (7 API Integrations)

1. ✅ **Scopus**  
   Multidisciplinary database with comprehensive coverage across political science, governance, law, and engineering.  
   *Coverage:* 90M+ records | *API:* Elsevier Scopus API

2. ✅ **Web of Science**  
   High-impact journal indexing platform enabling detailed citation analysis across disciplines.  
   *Coverage:* 100M+ records | *API:* Clarivate Web of Science API

3. ✅ **IEEE Xplore**  
   Technical literature repository covering electronic voting systems, cryptographic security, and system auditability.  
   *Coverage:* 6M+ documents | *API:* IEEE Xplore API

4. ✅ **Semantic Scholar**  
   AI-enhanced bibliographic database covering 200M+ papers across computer science and interdisciplinary research, with citation graphs and semantic indexing.  
   *Coverage:* 200M+ papers | *API:* Semantic Scholar API

5. ✅ **OpenAlex**  
   Open bibliographic database providing comprehensive metadata including institutions, citations, and concept tagging.  
   *Coverage:* 250M+ works | *API:* OpenAlex API

6. ✅ **CrossRef**  
   DOI registration agency providing publisher-verified metadata, enabling robust deduplication and citation tracking.  
   *Coverage:* 130M+ records | *API:* CrossRef REST API

7. ✅ **CORE**  
   Open access aggregator covering papers, theses, and preprints from institutional repositories worldwide.  
   *Coverage:* 300M+ documents | *API:* CORE API v3

### Source Selection Rationale

These sources were selected to provide:

- **Disciplinary breadth:** Coverage across political science, computer science, law, and governance
- **Methodological diversity:** Inclusion of both empirical studies and technical evaluations
- **API accessibility:** All sources provide documented APIs enabling reproducible automated searches
- **Complementary coverage:** Combination of subscription databases (Scopus, WoS, IEEE) and open sources (Semantic Scholar, OpenAlex, CORE) maximizes retrieval while supporting open science principles

### Unavailable Sources

The following sources were considered but not implemented due to API limitations:

- ❌ **ACM Digital Library** — No public API available
- ❌ **JSTOR** — No real-time API for systematic searches
- ❌ **Google Scholar** — Terms of Service restrictions on automated access

*Full methodology documented in [Protocol v1.8](docs/ELIS_2025_SLR_Protocol_v1.8.pdf), Section 3.2.*

---

## How It Works

### Workflow Overview
```
┌─────────────────────────────────────────────────────────────┐
│  1. SEARCH STRATEGY                                          │
│  Configure queries in YAML → Test with preflight scripts    │
└──────────────────┬──────────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────────┐
│  2. DATA HARVESTING                                          │
│  Run 7 harvest scripts → Query APIs → Collect metadata      │
└──────────────────┬──────────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────────┐
│  3. DATA CONSOLIDATION                                       │
│  Merge results → Deduplicate → Normalize → Validate         │
└──────────────────┬──────────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────────┐
│  4. SCREENING (Manual + AI-Assisted)                         │
│  Title/abstract → Full-text → Eligibility → Inclusion log   │
└──────────────────┬──────────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────────┐
│  5. DATA EXTRACTION                                          │
│  Extract study characteristics → Risk of bias → Outcomes    │
└──────────────────┬──────────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────────┐
│  6. SYNTHESIS & REPORTING                                    │
│  Thematic analysis → Confidence ratings → Final report       │
└─────────────────────────────────────────────────────────────┘
```

### Detailed Steps

#### 1. Search Strategy
- **Define queries** in `config/elis_search_queries.yml`
- **Test connectivity** using preflight scripts
- **Validate syntax** against each API's requirements
- **Document decisions** in protocol amendments

#### 2. Data Harvesting
Each source has two scripts:
- **Preflight script** (`*_preflight.py`) — Tests API connectivity and configuration
- **Harvest script** (`*_harvest.py`) — Executes search and retrieves results

All results saved to: `json_jsonl/ELIS_Appendix_A_Search_rows.json`

#### 3. Data Consolidation
- **Deduplication** — Identify duplicate records across sources
- **Normalization** — Standardize metadata fields
- **Validation** — Check completeness and data types
- **Enrichment** — Add citation counts, DOIs, full-text links

#### 4. Screening (Human-Led)
- **Title/abstract screening** — Apply inclusion/exclusion criteria
- **Full-text screening** — Detailed eligibility assessment
- **AI assistance** — LLMs suggest classifications (human validates)
- **Logging** — Record all decisions with rationales

#### 5. Data Extraction
- **Study characteristics** — Design, population, intervention
- **Risk of bias** — Structured assessment using adapted tools
- **Outcomes** — Primary and secondary outcomes
- **Confidence** — GRADE-CERQual ratings per theme

#### 6. Synthesis
- **Quantitative** — Descriptive statistics, frequency tables
- **Qualitative** — Thematic synthesis, narrative summary
- **Mixed methods** — Integration of findings
- **Reporting** — PRISMA-compliant manuscript

---

## Project Structure
```
ELIS-SLR-Agent/
│
├── config/
│   └── elis_search_queries.yml          # Search configuration (YAML)
│
├── docs/
│   ├── CHANGELOG.md                      # Protocol version history
│   ├── CONTRIBUTING.md                   # Contributor guidelines
│   ├── ELIS_2025_SLR_Protocol_v1.8.pdf  # Current protocol
│   └── README.md                         # Documentation overview
│
├── scripts/
│   ├── scopus_preflight.py              # Scopus API connectivity test
│   ├── scopus_harvest.py                # Scopus data harvester
│   ├── wos_preflight.py                 # Web of Science connectivity test
│   ├── wos_harvest.py                   # Web of Science harvester
│   ├── ieee_preflight.py                # IEEE Xplore connectivity test
│   ├── ieee_harvest.py                  # IEEE Xplore harvester
│   ├── semanticscholar_preflight.py     # Semantic Scholar connectivity test
│   ├── semanticscholar_harvest.py       # Semantic Scholar harvester
│   ├── openalex_preflight.py            # OpenAlex connectivity test
│   ├── openalex_harvest.py              # OpenAlex harvester
│   ├── crossref_preflight.py            # CrossRef connectivity test
│   ├── crossref_harvest.py              # CrossRef harvester
│   ├── core_preflight.py                # CORE connectivity test
│   └── core_harvest.py                  # CORE harvester
│
├── json_jsonl/
│   └── ELIS_Appendix_A_Search_rows.json # Consolidated search results
│
├── .github/
│   └── workflows/
│       ├── elis-scopus-preflight.yml    # Scopus CI workflow
│       ├── elis-wos-preflight.yml       # Web of Science CI workflow
│       ├── elis-ieee-preflight.yml      # IEEE Xplore CI workflow
│       ├── elis-semanticscholar-preflight.yml  # Semantic Scholar CI
│       ├── elis-openalex-preflight.yml  # OpenAlex CI workflow
│       ├── elis-crossref-preflight.yml  # CrossRef CI workflow
│       └── elis-core-preflight.yml      # CORE CI workflow
│
├── requirements.txt                      # Python dependencies
├── .env.example                          # Environment variables template
├── .gitignore                            # Git ignore rules
└── README.md                             # This file
```

### Key Files

#### Configuration
- **`config/elis_search_queries.yml`** — Search queries for all sources  
  [View file →](config/elis_search_queries.yml)

#### Documentation
- **`docs/ELIS_2025_SLR_Protocol_v1.8.pdf`** — Complete systematic review protocol  
  [View file →](docs/ELIS_2025_SLR_Protocol_v1.8.pdf)
- **`docs/CHANGELOG.md`** — Version history and amendments  
  [View file →](docs/CHANGELOG.md)

#### Core Scripts
- **Preflight scripts** — Test API connectivity before harvesting
- **Harvest scripts** — Execute searches and retrieve results
- **All scripts** documented with inline comments and docstrings

#### Output
- **`json_jsonl/ELIS_Appendix_A_Search_rows.json`** — Consolidated search results

---

## Quick Start

### Prerequisites

- **Python 3.11+** (tested on 3.11 and 3.12)
- **API keys** for subscription databases (see Configuration)
- **Git** for version control
- **Operating system:** macOS, Linux, or Windows (WSL recommended)

### Installation
```bash
# 1. Clone the repository
git clone https://github.com/rochasamurai/ELIS-SLR-Agent.git
cd ELIS-SLR-Agent

# 2. Create virtual environment (recommended)
python -m venv .venv

# Activate on Windows:
.venv\Scripts\activate

# Activate on macOS/Linux:
source .venv/bin/activate

# 3. Upgrade pip
python -m pip install --upgrade pip

# 4. Install dependencies
pip install -r requirements.txt --break-system-packages
```

### Configuration

Create a `.env` file in the project root:
```bash
# Copy template
cp .env.example .env

# Edit with your API keys
nano .env  # or use your preferred editor
```

**Required API keys:**
```bash
# Scopus (Elsevier)
SCOPUS_API_KEY=your_scopus_key_here
SCOPUS_INST_TOKEN=your_institution_token_here

# Web of Science (Clarivate)
WEB_OF_SCIENCE_API_KEY=your_wos_key_here

# IEEE Xplore
IEEE_EXPLORE_API_KEY=your_ieee_key_here

# CORE
CORE_API_KEY=your_core_key_here

# Optional but recommended
SEMANTIC_SCHOLAR_API_KEY=your_semantic_scholar_key_here
```

**Note:** OpenAlex and CrossRef provide public APIs that don't require authentication.

### Verify Installation
```bash
# Test all API connections
python scripts/scopus_preflight.py
python scripts/wos_preflight.py
python scripts/ieee_preflight.py
python scripts/semanticscholar_preflight.py
python scripts/openalex_preflight.py
python scripts/crossref_preflight.py
python scripts/core_preflight.py

# All should return: ✅ Connection successful
```

---

## Usage Guide

### Basic Workflow

#### 1. Test API Connectivity
```bash
# Run all preflight checks
python scripts/scopus_preflight.py
python scripts/wos_preflight.py
python scripts/ieee_preflight.py
python scripts/semanticscholar_preflight.py
python scripts/openalex_preflight.py
python scripts/crossref_preflight.py
python scripts/core_preflight.py
```

#### 2. Run Individual Harvesters
```bash
# Scopus
python scripts/scopus_harvest.py

# Web of Science
python scripts/wos_harvest.py

# IEEE Xplore
python scripts/ieee_harvest.py

# Semantic Scholar
python scripts/semanticscholar_harvest.py

# OpenAlex
python scripts/openalex_harvest.py

# CrossRef
python scripts/crossref_harvest.py

# CORE
python scripts/core_harvest.py
```

#### 3. Check Results
```bash
# View consolidated results
cat json_jsonl/ELIS_Appendix_A_Search_rows.json

# Count records
python -c "import json; data=json.load(open('json_jsonl/ELIS_Appendix_A_Search_rows.json')); print(f'Total records: {len(data)}')"
```

### Advanced Usage

#### Modify Search Queries
```bash
# Edit search configuration
nano config/elis_search_queries.yml

# Test new queries
python scripts/scopus_preflight.py  # Tests query syntax

# Run harvest with new queries
python scripts/scopus_harvest.py
```

#### Schedule Automated Runs
GitHub Actions workflows can be triggered:
- **Manually** — Actions tab → Select workflow → Run workflow
- **On schedule** — Configure cron in workflow YAML
- **On push** — Automatic CI/CD on code changes

#### Export Results
```bash
# Convert JSON to CSV (requires pandas)
python -c "
import json, pandas as pd
data = json.load(open('json_jsonl/ELIS_Appendix_A_Search_rows.json'))
df = pd.DataFrame(data)
df.to_csv('search_results.csv', index=False)
print('Exported to search_results.csv')
"
```

---

## Methodology

### AI-Assisted Workflow

This project integrates Large Language Models (LLMs) while maintaining rigorous human oversight:

**LLMs Used:**
- ChatGPT (OpenAI) — Query generation, code review
- Claude (Anthropic) — Synthesis suggestions, thematic analysis
- NotebookLM (Google) — Literature summarization

**AI Tasks:**
- 🤖 **Query generation** — Suggest search terms and Boolean logic
- 🤖 **Pattern detection** — Identify recurring themes in results
- 🤖 **Code assistance** — Generate and debug Python scripts
- 🤖 **Synthesis** — Suggest thematic clusters from extracted data

**Human Oversight:**
- ✅ **All final decisions** made by human reviewer
- ✅ **All AI outputs** validated before acceptance
- ✅ **Full audit trail** maintained in GitHub
- ✅ **No automated exclusions** — Every study manually reviewed

### Quality Assurance

**Risk of Bias Assessment:**
- Structured checklist adapted from PRISMA-P and Cochrane ROB-2
- Domain-level ratings: study design, data transparency, outcome measurement
- Independent assessment with documented rationales

**Confidence in Evidence:**
- GRADE-CERQual approach for qualitative/mixed-methods findings
- Four domains: methodological limitations, coherence, data adequacy, relevance
- Ratings: High, Moderate, Low, or Very Low confidence

**Version Control:**
- All decisions logged in GitHub with commit history
- Protocol amendments documented and versioned
- Data extraction forms tracked in version control
- Reproducible workflow enables replication studies

### Transparency Commitments

- 📖 **Open protocol** — Full methodology documented and registered
- 💻 **Open source** — All code publicly available on GitHub
- 📊 **Open data** — Search results and extracted data will be published
- 🔍 **Open audit trail** — Every decision documented and versioned

---

## Current Status

### Implementation Status

| Component | Status | Notes |
|-----------|--------|-------|
| **Protocol v1.8** | ✅ Complete | 7 sources finalized and documented |
| **Scopus** | ✅ Operational | Preflight + harvest scripts working |
| **Web of Science** | ✅ Operational | Preflight + harvest scripts working |
| **IEEE Xplore** | ✅ Operational | Preflight + harvest scripts working |
| **Semantic Scholar** | ✅ Operational | Preflight + harvest scripts working |
| **OpenAlex** | ✅ Operational | Preflight + harvest scripts working |
| **CrossRef** | ✅ Operational | Preflight + harvest scripts working |
| **CORE** | ⚠️ Operational | Occasional server timeouts (documented) |

### Review Progress

| Stage | Status | Records |
|-------|--------|---------|
| **Search** | 🔄 In Progress | ~15,000 expected |
| **Deduplication** | ⏳ Pending | TBD |
| **Title/Abstract Screening** | ⏳ Pending | TBD |
| **Full-Text Screening** | ⏳ Pending | TBD |
| **Data Extraction** | ⏳ Pending | TBD |
| **Synthesis** | ⏳ Pending | TBD |

**Expected completion:** Q2 2026

### Recent Updates

- ✅ **2025-11-19:** Protocol v1.8 finalized (7 sources documented)
- ✅ **2025-11:** CORE API integration completed
- ✅ **2025-10:** CrossRef API integration completed
- ✅ **2025-10:** OpenAlex API integration completed
- ✅ **2025-09:** Semantic Scholar API integration completed
- ✅ **2025-09:** IEEE Xplore API integration completed
- ✅ **2025-08:** Web of Science API integration completed
- ✅ **2025-08:** Scopus API integration completed

*Full changelog: [docs/CHANGELOG.md](docs/CHANGELOG.md)*

---

## Troubleshooting

### Common Issues

#### API Connection Failures

**Problem:** Preflight script returns authentication error.

**Solutions:**
```bash
# Check API key is set
echo $SCOPUS_API_KEY  # Should print your key

# Check .env file exists
cat .env

# Reload environment variables
source .env  # Linux/macOS
# or restart your terminal

# Test with curl (example for Scopus)
curl -H "X-ELS-APIKey: YOUR_KEY" \
  "https://api.elsevier.com/content/search/scopus?query=election"
```

#### Rate Limiting

**Problem:** "429 Too Many Requests" error.

**Solutions:**
- Most APIs have rate limits (e.g., 3 requests/second)
- Scripts include built-in delays
- If hit rate limit, wait 1 hour and retry
- Consider spreading harvests across multiple days

#### Empty Results

**Problem:** Harvest script returns 0 results.

**Solutions:**
```bash
# Check query syntax in config file
cat config/elis_search_queries.yml

# Test with simpler query first
# Edit YAML to use: query: "election"

# Check API status pages:
# - Scopus: status.elsevier.com
# - Web of Science: status.clarivate.com
# - IEEE: ieeexplore.ieee.org/about/help
```

#### JSON Parsing Errors

**Problem:** "JSONDecodeError: Expecting value" error.

**Solutions:**
```bash
# Check JSON file is valid
python -m json.tool json_jsonl/ELIS_Appendix_A_Search_rows.json

# If corrupted, delete and re-run harvest
rm json_jsonl/ELIS_Appendix_A_Search_rows.json
python scripts/scopus_harvest.py
```

#### CORE Server Errors

**Problem:** CORE API returns 502/503 errors intermittently.

**Solution:**
This is a known issue with CORE infrastructure. The harvest script automatically retries failed requests. If problems persist:
```bash
# Wait 30 minutes and retry
# CORE issues usually resolve quickly

# Check CORE status
curl https://api.core.ac.uk/v3/search/works?q=test
```

### Getting Help

- 📧 **Contact:** c.rocha@imperial.ac.uk
- 🐛 **Bug reports:** [Open an issue](https://github.com/rochasamurai/ELIS-SLR-Agent/issues)
- 📖 **Documentation:** See [docs/](docs/) folder
- 💬 **Questions:** Check [Protocol v1.8](docs/ELIS_2025_SLR_Protocol_v1.8.pdf) first

---

## Contributing

This is an active research project. While external contributions are not currently accepted, the codebase is open for:

### Permitted Uses
- ✅ **Replication studies** — Reproduce methodology for your own research
- ✅ **Methodology review** — Audit and verify our approach
- ✅ **Educational purposes** — Learn systematic review methods
- ✅ **Fork for adaptation** — Adapt for your own SLR project

### How to Adapt This Project
```bash
# 1. Fork the repository on GitHub

# 2. Clone your fork
git clone https://github.com/YOUR_USERNAME/ELIS-SLR-Agent.git

# 3. Modify search queries
# Edit: config/elis_search_queries.yml

# 4. Update protocol
# Edit: docs/ELIS_2025_SLR_Protocol_v1.8.pdf

# 5. Run your own systematic review
# Follow the same workflow documented here
```

### Citation Requirement

If you use this methodology or code in your research, please cite:
```bibtex
@software{rocha2025elis,
  author = {Rocha, Carlos},
  title = {ELIS SLR Agent: Systematic Literature Review on Electoral Integrity Strategies},
  year = {2025},
  publisher = {GitHub},
  url = {https://github.com/rochasamurai/ELIS-SLR-Agent},
  note = {Protocol v1.8}
}
```

### Guidelines for Derived Works

If adapting this project:
- ✅ Credit original methodology
- ✅ Document your modifications
- ✅ Share your protocol publicly (if possible)
- ✅ Maintain open science principles

See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for detailed guidelines.

---

## Documentation

### Core Documents

- **Protocol v1.8** — Complete systematic review methodology  
  [View PDF →](docs/ELIS_2025_SLR_Protocol_v1.8.pdf)

- **Changelog** — Version history and amendments  
  [View changelog →](docs/CHANGELOG.md)

- **Search Queries** — Configured search strategies  
  [View YAML →](config/elis_search_queries.yml)

### Protocol Sections

The Protocol v1.8 includes:
1. **Administrative Information** — Registration, authors, amendments
2. **Introduction** — Rationale and objectives
3. **Methods** — Eligibility criteria, search strategy, screening
4. **Quality Assessment** — Risk of bias, confidence ratings
5. **Annexes** — Search strings, data extraction forms, bias tools

### API Documentation

Each source has official API documentation:

- [Scopus API Docs](https://dev.elsevier.com/documentation/ScopusSearchAPI.wadl)
- [Web of Science API Docs](https://developer.clarivate.com/apis/wos)
- [IEEE Xplore API Docs](https://developer.ieee.org/docs)
- [Semantic Scholar API Docs](https://api.semanticscholar.org/)
- [OpenAlex API Docs](https://docs.openalex.org/)
- [CrossRef API Docs](https://www.crossref.org/documentation/retrieve-metadata/rest-api/)
- [CORE API Docs](https://core.ac.uk/documentation/api/)

---

## Citation

### Citing This Project
```bibtex
@software{rocha2025elis,
  author = {Rocha, Carlos},
  title = {ELIS SLR Agent: Systematic Literature Review on Electoral Integrity Strategies},
  year = {2025},
  publisher = {GitHub},
  url = {https://github.com/rochasamurai/ELIS-SLR-Agent},
  note = {Protocol v1.8}
}
```

### Citing the Protocol
```bibtex
@techreport{rocha2025protocol,
  author = {Rocha, Carlos},
  title = {Protocol for the Systematic Literature Review on Electoral Integrity Strategies (ELIS 2025)},
  institution = {Imperial College Business School},
  year = {2025},
  type = {Research Protocol},
  note = {Version 1.8}
}
```

---

## Acknowledgments

### People

- **Carlos Rocha** — Principal Investigator  
  Visiting Researcher, Imperial College Business School  
  📧 c.rocha@imperial.ac.uk | 🔗 [ORCID: 0009-0009-6741-2193](https://orcid.org/0009-0009-6741-2193)

- **Prof. Tommaso Valletti** — Research Supervisor  
  Professor of Economics, Imperial College Business School

### Institutions

- **Imperial College Business School** — Host institution
- **Instituto Voto Legal (IVL)** — Project sponsor, São Paulo, Brazil

### Data Providers

- **Elsevier** — Scopus API access
- **Clarivate** — Web of Science API access
- **IEEE** — IEEE Xplore API access
- **Semantic Scholar** — Open API (Allen Institute for AI)
- **OpenAlex** — Open bibliographic data (OurResearch)
- **CrossRef** — DOI metadata services
- **CORE** — Open access aggregation (Open University)

### Technology

Built with:
- Python 3.11+ | requests | pyyaml
- GitHub Actions for CI/CD
- Zotero for reference management
- ChatGPT, Claude, NotebookLM for AI assistance

---

## License

MIT License

Copyright (c) 2025 Carlos Rocha, Imperial College London

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

**[⬆ Back to top](#elis-slr-agent)**
