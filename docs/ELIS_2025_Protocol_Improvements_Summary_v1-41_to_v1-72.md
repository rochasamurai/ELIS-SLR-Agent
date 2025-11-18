# ELIS 2025 Protocol Improvements Summary

## Version Comparison: v1.41 (August 2025) → v1.7.2 (November 2025)

### Document Information
- **Protocol Title:** Systematic Literature Review on Electoral Integrity Strategies (ELIS 2025)
- **Principal Investigator:** Carlos Rocha (Imperial College Business School)
- **Supervisor:** Professor Tommaso Valletti
- **Previous Version:** v1.41, dated August 19, 2025
- **Current Version:** v1.7.2, dated November 11, 2025

---

## Executive Summary

Version 1.7.2 represents a substantial evolution of the ELIS protocol, with comprehensive improvements in methodological rigor, transparency, reproducibility, and operational guidance. The new version includes eight detailed annexes, enhanced quality assessment frameworks, and explicit AI governance procedures.

---

## Major Improvements

### 1. Enhanced Methodological Framework

#### SPIDER Framework Integration
- **Addition:** Comprehensive SPIDER framework (Sample, Phenomenon of Interest, Design, Evaluation, Research type) explicitly defined and operationalized
- **Rationale:** Better accommodation of qualitative and mixed-methods studies alongside quantitative research
- **Location:** Section 2.3 with detailed table defining each component

#### GRADE-CERQual Approach
- **Addition:** Modified GRADE-CERQual methodology for assessing confidence in synthesized findings
- **Components:** Four assessment domains
  - Methodological Limitations
  - Coherence
  - Data Adequacy
  - Relevance
- **Output:** Four-level confidence ratings (High, Moderate, Low, Very Low)
- **Location:** Section 3.8 and Annex E.2

#### Risk of Bias Assessment
- **Enhancement:** Structured, multi-domain risk of bias tool adapted from PRISMA-P, Cochrane ROB-2, and Norris et al. (2014)
- **Domains:**
  - Study design appropriateness
  - Data transparency
  - Outcome measurement clarity
  - Selection of reported results (when applicable)
  - Conflicts of interest (when applicable)
- **Location:** Section 3.6 and Annex E.1

---

### 2. Expanded Documentation: Eight Comprehensive Annexes

#### Annex A: PRISMA-P 2015 Checklist
- Complete mapping of protocol to PRISMA-P requirements
- Item-by-item compliance demonstration
- Section references for each checklist item

#### Annex B: Search Strings
- Database-specific search strategies for:
  - Scopus
  - Web of Science
  - IEEE Xplore
  - ACM Digital Library
  - JSTOR
  - Google Scholar
- Syntax adaptations for each platform
- Search dates and iteration strategy documented

#### Annex C: Inclusion/Exclusion Log Template
- Structured decision recording framework
- Fields: Study ID, Citation, Decision, Exclusion Reason, Notes
- Predefined exclusion reason categories
- Real-time tracking procedures

#### Annex D: Data Extraction Form
- Comprehensive field definitions covering:
  - Bibliographic information
  - Study context (country, electoral modality)
  - Intervention characteristics
  - Study design and evaluation methods
  - Multiple outcomes per study
  - Risk of bias summary
- **JSON Schema:** Machine-readable format with validation
- Example extraction provided in both tabular and JSON formats

#### Annex E: Evidence Quality Assessments
- **E.1:** Risk of Bias Tool and Rating Log (per study)
  - Domain-specific assessment criteria
  - Rating scale and documentation requirements
  - Example log entries
- **E.2:** CERQual Confidence Rating Template (per synthesized finding)
  - Finding-level assessment framework
  - JSON-formatted confidence ratings
  - Integration with risk of bias data

#### Annex F: Automation Workflow & AI
- Stage-by-stage automation mapping
- Tool-specific roles (Zotero, ELIS SLR Agent, LLMs, GitHub)
- Human oversight protocols for each stage
- Commitment to UKRIO principles
- Audit trail procedures

#### Annex G: Evidence Gap Confirmation
- **Purpose:** Validation of rationale statement regarding absence of consolidated systematic reviews
- **Method:** Structured review of peer-reviewed literature (2015-2025)
- **Findings:** Confirmation of evidence gap with supporting citations
- **Notable Existing Reviews:** Comparative table showing coverage gaps
- **PRQ Justification:** Explanation of causal framing

#### Annex H: Workflow Diagram & Tools
- Visual representation of review pipeline
- Tool integration flow
- Interaction between automation and human validation
- Simplified reference for understanding the process

---

### 3. Strengthened AI Transparency and Governance

#### Explicit AI Usage Documentation
- **Addition:** Complete disclosure of AI tools at each review stage
- **Tools Documented:**
  - ELIS SLR Agent (open-source Python workflow)
  - ChatGPT, Claude.ai, NotebookLM (LLMs for pattern detection)
  - Zotero (reference management)
  - GitHub (version control and audit)

#### Human Oversight Protocols
- **Principle:** AI assists, humans decide
- **Documentation:** Every AI-assisted output logged and versioned
- **Validation:** All final decisions require human reviewer verification
- **Accountability:** Lead researcher responsible for integrity of findings

#### UK Research Integrity Office (UKRIO) Compliance
- Explicit commitment to UKRIO principles for AI use in research
- Transparency requirements met through GitHub logging
- No AI-generated content accepted without verification
- Proper citation and plagiarism avoidance protocols

#### Audit Trail
- Version control via GitHub for all stages
- No automatic deletion of AI-assisted outputs
- Full traceability from initial screening to final synthesis
- Public accessibility of decision logs

---

### 4. Improved Data Management

#### JSON Schema Implementation
- **Purpose:** Ensure consistency and machine-readability
- **Validation:** Automatic flagging of non-conforming entries
- **Fields:** Predefined allowed values for key variables
- **Example:** Outcome type must be "Primary" or "Secondary"

#### Structured Outputs
- Data extraction in both CSV and JSON formats
- Risk of bias logs in tabular and JSON formats
- CERQual assessments in JSON format
- GitHub repository integration for data sharing

#### Reproducibility Enhancement
- Complete data extraction templates provided
- Schema definitions available in project repository
- Final datasets to be deposited on Zenodo or OSF
- Open-access commitment for all review data

---

### 5. Clarified Research Questions

#### Primary Research Question (PRQ) Refinement
- **Original (implied):** What strategies improve electoral integrity?
- **Enhanced:** "What operational and technological strategies have been shown to improve the integrity or auditability of electoral systems since 1990?"

#### Methodological Sub-question (MSQ)
- **Addition:** "What types of empirical designs and evaluation frameworks have been used to assess the effectiveness of electoral integrity strategies since 1990?"
- **Purpose:** Systematic documentation of research methods in the field

#### Analytical Sub-questions
Newly structured sub-questions:
1. **Systems & Mechanisms:** What specific technological or operational mechanisms have been associated with increased auditability or verifiability?
2. **Institutional Conditions:** Under what institutional, legal, or regulatory conditions have these mechanisms been implemented?
3. **Trust & Perception:** How have these strategies influenced public trust, voter confidence, or perceptions of electoral integrity?
4. **Regional Variation:** What regional patterns or cross-national differences are observed?

#### "Shown to Improve" Clarification
- Explicit definition provided in Section 2.2
- Includes multiple evidence types:
  - Experimental and quasi-experimental studies
  - Comparative observational research
  - Technical evaluations
  - Structured qualitative analyses
- Commitment to distinguish robust from suggestive findings

---

### 6. Enhanced Quality Assessment

#### Study-Level Assessment
- Multi-domain risk of bias evaluation
- Structured rating system (Low/Moderate/High)
- Documentation requirements for each domain
- Cross-referencing with CERQual assessments

#### Finding-Level Assessment
- CERQual methodology applied to synthesized themes
- Four-domain evaluation framework
- Confidence ratings support interpretation
- Explicit discussion of evidence strength

#### Integration of Assessments
- Risk of bias data informs confidence ratings
- High-bias studies limit confidence even with coherent findings
- Transparent discussion of evidence quality trade-offs
- Summary tables planned for final review

---

### 7. Better Search Strategy

#### Database-Specific Documentation
- **Addition:** Complete search strings for all six databases
- **Customization:** Syntax adapted to each platform's requirements
- **Examples:**
  - Scopus: TITLE-ABS-KEY queries
  - Web of Science: TS (Topic) searches
  - IEEE Xplore: Technical keyword emphasis
  - ACM Digital Library: HCI and usability terms
  - JSTOR: Broad full-text searches
  - Google Scholar: Iterative, citation-following approach

#### Database Selection Justification
- **Scopus:** Multidisciplinary coverage across political science, governance, law, engineering
- **Web of Science:** High-impact journals and citation analysis
- **IEEE Xplore:** Technical literature on electronic voting systems
- **ACM Digital Library:** Human-computer interaction and system design
- **JSTOR:** Foundational and historical literature
- **Google Scholar:** Grey literature, working papers, theses

#### Search Process Documentation
- Search dates recorded (November 6-10, 2025)
- Export procedures documented
- Result counts tracked
- Update procedures specified
- Grey literature strategy explained

#### Reproducibility Features
- All queries provided in full
- Filters and limits documented
- Search logs available in project repository
- Iterative refinement process described

---

### 8. Outcomes and Prioritization

#### Clear Outcome Hierarchy
- **Primary Outcomes:**
  - Successful implementation of audits or verifiability mechanisms
  - Detection and reporting of anomalies, errors, or tampering
  - Evidence of procedural transparency or compliance improvements
  - Reduction in error rates through system design interventions

- **Secondary Outcomes:**
  - Changes in public trust or voter confidence
  - Voter usability and satisfaction with systems
  - Institutional capacity or oversight effectiveness

#### Design Link Assessment
- **New Feature:** Outcome-level assessment of connection to system design
- **Purpose:** Prioritize outcomes directly attributable to specific features
- **Implementation:** Yes/No flag in data extraction
- **Rationale:** Focus on actionable, design-relevant findings

#### Reporting Strategy
- Primary outcomes prioritized in synthesis
- Secondary outcomes reported when design-linked
- Attitudinal findings included only if clearly within scope
- Transparent discussion of outcome selection

---

## Additional Improvements

### 9. Collaborative Review Process (Section 5)
- Acknowledgment of single-reviewer limitations
- ELIS SLR Agent as algorithmic "second reviewer"
- GitHub transparency enables virtual collaboration
- Procedures for future collaborator integration documented

### 10. Registration and Archiving
- OSF registration commitment prior to full-text screening
- Spiral (Imperial College) institutional repository deposition
- PROSPERO not applicable (non-health topic)
- Version history and amendments tracked on OSF

### 11. Ethical Considerations (Section 4)
- Explicit statement: no human subjects, no ethical approval required
- Research integrity principles emphasized
- AI usage ethical framework established
- Data handling and citation standards affirmed

### 12. Amendments Process (Section 1.4)
- Semantic versioning adopted (v1.7, v1.8, etc.)
- Public CHANGELOG.md in GitHub repository
- OSF version history integration
- Major amendments flagged in final report

---

## Structural Improvements

### Document Organization
- More logical flow from rationale to methods
- Clear section numbering and cross-referencing
- Consistent formatting throughout
- Professional presentation with Imperial College branding

### Terminology Consistency
- Standardized definitions (e.g., "electoral integrity," "auditability")
- Consistent use of technical terms
- Glossary implicit through framework definitions
- Precise language throughout

### Citation and Attribution
- Enhanced author contributions section
- ORCID identifiers included
- Guarantor of review explicitly identified
- Supervisor role clarified

---

## Implementation Implications

### For the Review Process
1. **Increased Rigor:** Multiple quality checkpoints ensure robust findings
2. **Enhanced Transparency:** Full audit trail supports credibility
3. **Improved Reproducibility:** Detailed procedures enable replication
4. **Better Synthesis:** Structured frameworks support systematic analysis

### For Future Users
1. **Template Value:** Other researchers can adapt this protocol
2. **Methodological Innovation:** AI-assisted SLR framework demonstrated
3. **Open Science Model:** Complete transparency in all stages
4. **Quality Standards:** Sets benchmark for electoral integrity research

### For Policy Impact
1. **Evidence Quality:** Confidence ratings guide interpretation
2. **Actionable Findings:** Design-linked outcomes support implementation
3. **Cross-System Insights:** Comparative approach enables learning
4. **Transparency:** Policy recommendations traceable to evidence

---

## Quantitative Summary

| Aspect | v1.41 | v1.7.2 | Change |
|--------|-------|--------|--------|
| Page Count | ~15 pages | 27 pages | +80% |
| Annexes | 0-2 basic | 8 comprehensive | +400% |
| Search Databases | Listed | Detailed strings | Full documentation |
| Quality Assessment | Basic | Multi-framework | GRADE-CERQual added |
| AI Documentation | Limited | Comprehensive | Full governance |
| Data Formats | Implied | JSON schema | Machine-readable |
| Outcome Categories | Mentioned | Hierarchical | Priority framework |
| Version Control | Not specified | GitHub integrated | Full audit trail |

---

## Key Takeaways

1. **Methodological Maturity:** The protocol has evolved from a draft framework to a comprehensive, publication-ready document
2. **Transparency Leadership:** Sets new standard for AI-assisted systematic reviews
3. **Interdisciplinary Approach:** Successfully integrates political science, computer science, and policy research methods
4. **Practical Utility:** Provides complete operational templates for review execution
5. **Scientific Rigor:** Multiple quality frameworks ensure robust evidence synthesis
6. **Open Science Exemplar:** Full transparency and reproducibility throughout
7. **Policy Relevance:** Clear pathway from evidence to actionable recommendations
8. **Future-Proof:** Adaptable framework for electoral integrity research

---

## Recommendations for Future Versions

While v1.7.2 represents substantial improvement, potential future enhancements could include:

1. **Pilot Testing Results:** Incorporate lessons learned from initial screening
2. **Inter-Rater Reliability:** If additional reviewers join, document agreement statistics
3. **Stakeholder Feedback:** Integrate input from electoral management bodies
4. **Regional Workshops:** Findings validation with regional election experts
5. **Living Review Protocol:** Procedures for ongoing updates as new evidence emerges

---

## Conclusion

Version 1.7.2 of the ELIS protocol represents a comprehensive, rigorous, and transparent framework for systematic evidence synthesis on electoral integrity strategies. The improvements span methodological frameworks, documentation depth, AI governance, data management, and quality assessment. This protocol is now positioned to produce a high-impact systematic review that can inform both academic research and practical electoral policy design.

The protocol's commitment to open science, reproducibility, and transparent AI use establishes it as a model for future evidence synthesis efforts in electoral studies and beyond.

---

## Document Information

**Prepared by:** Claude (Anthropic AI)  
**Date:** November 18, 2025  
**Based on:** ELIS Protocol v1.41 and v1.7.2 comparison  
**Purpose:** Documentation for /docs directory  
**Format:** Markdown (.md)

**Related Documents:**
- ELIS_2025_SLR_Protocol_v1_7_2.pdf
- Protocol_SLR_Electoral_Integrity_Strategies_v1-41.docx
- GitHub Repository: ELIS SLR Agent
- OSF Registration: [To be added upon registration]

---

*For questions or clarifications regarding protocol improvements, contact:*  
**Carlos Rocha** (c.rocha@imperial.ac.uk)
Visiting Researcher, Imperial College Business School
