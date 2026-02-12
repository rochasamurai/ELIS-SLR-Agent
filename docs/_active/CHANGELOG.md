@"
# Protocol Changelog

## Version 1.8 (2025-11-19)

**Updated Section 3.2 - Information Sources**

### Changes
- Finalized information sources based on API availability assessment
- Total sources: 7 operational APIs (exceeding original 6-source protocol target)

### Information Sources

**Primary Sources:**

1. **Scopus** – Multidisciplinary database with comprehensive coverage across political science, governance, law, and engineering.

2. **Web of Science** – High-impact journal indexing platform enabling detailed citation analysis across disciplines.

3. **IEEE Xplore** – Technical literature repository covering electronic voting systems, cryptographic security, and system auditability.

4. **Semantic Scholar** – AI-enhanced bibliographic database covering 200M+ papers across computer science and interdisciplinary research, with citation graphs and semantic indexing.

5. **OpenAlex** – Open bibliographic database (250M+ works) providing comprehensive metadata including institutions, citations, and concept tagging.

6. **CrossRef** – DOI registration agency providing publisher-verified metadata for 130M+ records, enabling robust deduplication and citation tracking.

7. **CORE** – Open access aggregator covering 300M+ papers, theses, and preprints from institutional repositories worldwide.

### Source Selection Rationale

These sources were selected to provide:
- **Disciplinary breadth:** Coverage across political science, computer science, law, and governance
- **Methodological diversity:** Inclusion of both empirical studies and technical evaluations
- **API accessibility:** All sources provide documented APIs enabling reproducible automated searches
- **Complementary coverage:** Combination of subscription databases (Scopus, WoS, IEEE) and open sources (Semantic Scholar, OpenAlex, CORE) maximizes retrieval while supporting open science principles

### Unavailable Sources

The following originally planned sources were not implemented due to API limitations:
- **ACM Digital Library** – No public API available
- **JSTOR** – No real-time API available
- **Google Scholar** – Terms of Service restrictions on automated access

---

## Version 1.7 and Earlier

See project repository history for previous protocol versions and implementation details.
"@ | Out-File -FilePath "docs\CHANGELOG.md" -Encoding utf8
