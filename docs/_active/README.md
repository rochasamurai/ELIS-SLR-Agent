# ELIS Documentation

This folder contains the core documentation for the ELIS Systematic Literature Review project.

---

## 📚 Core Documents

### [ELIS_2025_SLR_Protocol_v1.8.pdf](ELIS_2025_SLR_Protocol_v1.8.pdf)
**Systematic Review Protocol (Current Version)**

Complete methodology document following PRISMA-P 2015 guidelines. Includes:
- Research questions and objectives
- Information sources (7 API integrations)
- Search strategy and eligibility criteria
- Screening and data extraction procedures
- Risk of bias assessment
- Quality assurance methods
- Complete annexes with forms and tools

**Status:** Version 1.8 (2025-11-19) — Finalized  
**Pages:** 28  
**Format:** PDF

---

### [CHANGELOG.md](CHANGELOG.md)
**Protocol Version History**

Documents all changes to the systematic review protocol, including:
- Version 1.8 changes (finalized information sources)
- Source selection rationale
- Unavailable sources and alternatives
- Links to previous versions

**Status:** Current  
**Format:** Markdown

---

### [CONTRIBUTING.md](CONTRIBUTING.md)
**Contributor Guidelines**

Guidelines for:
- Replication studies
- Methodology review
- Adaptation for other projects
- Citation requirements
- Open science principles

**Status:** Current  
**Format:** Markdown

---

### [REPO_HYGIENE_PLAN_2026-02-05.md](REPO_HYGIENE_PLAN_2026-02-05.md)
**Repository Structure and Maintenance**

Comprehensive plan for repository hygiene, including:
- Benchmark restructure (`benchmarks/`)
- JSON-only data policy (no CSV/TSV/XLSX tracked)
- File review ledger ([FILE_REVIEW_LEDGER.md](FILE_REVIEW_LEDGER.md))
- Validation report retention policy
- CI guardrails and testing standards

**Status:** Implemented (2026-02-05)
**Format:** Markdown

---

## 📖 Additional Resources

### Main Project Documentation
See the [main README.md](../README.md) in the repository root for:
- Project overview and objectives
- Quick start guide
- Installation instructions
- Usage guide
- API source documentation
- Troubleshooting
- Current status

### Protocol Sections

The Protocol v1.8 includes eight main sections:

1. **Administrative Information**
   - Title and registration
   - Authors and contributions
   - Amendments history
   - Support and sponsorship

2. **Introduction**
   - Research rationale
   - Primary and secondary objectives
   - SPIDER conceptual framework

3. **Methods**
   - Eligibility criteria
   - Information sources (7 APIs)
   - Search strategy
   - Study records management
   - Outcomes and prioritization
   - Risk of bias assessment
   - Data synthesis approach
   - Confidence in evidence (CERQual)

4. **Ethical Considerations**
   - Human oversight of AI tools
   - Transparency requirements
   - Accountability measures

5. **Collaborative Review Process**
   - Single-reviewer approach
   - AI-assisted workflow
   - Version control transparency

6. **Annexes**
   - Annex A: PRISMA-P Checklist
   - Annex B: Search Strings
   - Annex C: Inclusion/Exclusion Log
   - Annex D: Data Extraction Form
   - Annex E: Risk of Bias Assessment
   - Annex F: Automation Workflow & AI
   - Annex G: Evidence Gap Confirmation
   - Annex H: Tools & Workflow Diagram

---

## 🔗 External Links

### Protocol Registration
- **Spiral (Imperial College London):** [Pending]
- **OSF (Open Science Framework):** [Pending]

### Related Documentation
- **GitHub Repository:** https://github.com/rochasamurai/ELIS-SLR-Agent
- **Search Configuration:** [`../config/elis_search_queries.yml`](../config/elis_search_queries.yml)

---

## 📊 Information Sources Overview

The review queries **7 academic databases**:

| # | Source | Type | Coverage | API |
|---|--------|------|----------|-----|
| 1 | **Scopus** | Subscription | 90M+ records | Elsevier |
| 2 | **Web of Science** | Subscription | 100M+ records | Clarivate |
| 3 | **IEEE Xplore** | Subscription | 6M+ documents | IEEE |
| 4 | **Semantic Scholar** | Open | 200M+ papers | Open API |
| 5 | **OpenAlex** | Open | 250M+ works | Open API |
| 6 | **CrossRef** | Open | 130M+ records | Open API |
| 7 | **CORE** | Open | 300M+ documents | Open API |

**Full source selection rationale:** Protocol v1.8, Section 3.2

---

## 🔄 Version History

| Version | Date | Key Changes |
|---------|------|-------------|
| **v1.8** | 2025-11-19 | Finalized 7 information sources with API documentation |
| v1.7 | 2025-11 | Initial source planning |
| v1.0-v1.6 | 2025-08 | Protocol development and refinement |

**Full history:** [CHANGELOG.md](CHANGELOG.md)

---

## 📧 Contact

**Principal Investigator:**  
Carlos Rocha  
Visiting Researcher  
Imperial College Business School  
📧 c.rocha@imperial.ac.uk  
🔗 [ORCID: 0009-0009-6741-2193](https://orcid.org/0009-0009-6741-2193)

---

## 📄 Citation

If referencing this documentation, please cite:
```bibtex
@techreport{rocha2025protocol,
  author = {Rocha, Carlos},
  title = {Protocol for the Systematic Literature Review on Electoral Integrity Strategies (ELIS 2025)},
  institution = {Imperial College Business School},
  year = {2025},
  type = {Research Protocol},
  note = {Version 1.8},
  url = {https://github.com/rochasamurai/ELIS-SLR-Agent}
}
```

---

**Last updated:** 2025-11-19  
**Protocol version:** 1.8  
**Status:** Active research project
