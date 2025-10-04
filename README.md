# ELIS SLR Agent
<!--
  This README is the authoritative project overview for PMs and engineers.
  It intentionally includes hyperlinks for easy navigation and HTML comments
  (like this one) to document design decisions without cluttering the page.
-->

> **Current release:** [v0.1.1-mvp](https://github.com/rochasamurai/ELIS-SLR-Agent/releases)  
> **Status:** CI green; Data Contract v1.0 (MVP) frozen via JSON Schemas.

---

## Table of contents
- [What this repository is](#what-this-repository-is)
- [Repository map](#repository-map)
- [Data Contract v1.0 (MVP)](#data-contract-v10-mvp)
- [Quick start](#quick-start)
- [Workflows (GitHub Actions)](#workflows-github-actions)
- [Governance & branch protection](#governance--branch-protection)
- [Release process](#release-process)
- [Troubleshooting](#troubleshooting)
- [Frequently asked questions](#frequently-asked-questions)
- [Contributing](#contributing)
- [Changelog](#changelog)
- [Licence](#licence)

---

## What this repository is
The ELIS SLR Agent is a small, reproducible pipeline component used to generate
and validate three operational artefacts for a Systematic Literature Review (SLR):

- **Appendix A — Search**
- **Appendix B — Screening**
- **Appendix C — Data Extraction**

The repository ships a **toy agent** (for smoke tests and demos), a **validator**
(backed by JSON Schema), and CI that enforces formatting, linting and basic
contract validation for every change.

> If you are a PM, read the **Quick start** and **Release process**. If you are an engineer,
> see **Repository map**, **Workflows** and **Governance**.

---

## Repository map
> Jump directly to important files and folders.

- **Agent and tools**
  - `scripts/agent.py` — toy agent that produces A/B/C artefacts.  
    ↳ Open: <https://github.com/rochasamurai/ELIS-SLR-Agent/blob/main/scripts/agent.py>
  - `scripts/validate_json.py` — JSON artefact validator.  
    ↳ Open: <https://github.com/rochasamurai/ELIS-SLR-Agent/blob/main/scripts/validate_json.py>

- **Schemas (Data Contract v1.0)**
  - Appendix A — `schemas/appendix_a.schema.json`  
    ↳ Open: <https://github.com/rochasamurai/ELIS-SLR-Agent/blob/main/schemas/appendix_a.schema.json>
  - Appendix B — `schemas/appendix_b.schema.json`  
    ↳ Open: <https://github.com/rochasamurai/ELIS-SLR-Agent/blob/main/schemas/appendix_b.schema.json>
  - Appendix C — `schemas/appendix_c.schema.json`  
    ↳ Open: <https://github.com/rochasamurai/ELIS-SLR-Agent/blob/main/schemas/appendix_c.schema.json>

- **CI & automation** (all under `.github/workflows/`)  
  - CI — `ci.yml` (quality, tests, validate)  
    ↳ Open: <https://github.com/rochasamurai/ELIS-SLR-Agent/blob/main/.github/workflows/ci.yml>
  - Autoformat — `autoformat.yml`  
    ↳ Open: <https://github.com/rochasamurai/ELIS-SLR-Agent/blob/main/.github/workflows/autoformat.yml>
  - Bot Commit — `bot-commit.yml` (create/update a single file on a branch)  
    ↳ Open: <https://github.com/rochasamurai/ELIS-SLR-Agent/blob/main/.github/workflows/bot-commit.yml>
  - Agent Run — `agent-run.yml`  
    ↳ Open: <https://github.com/rochasamurai/ELIS-SLR-Agent/blob/main/.github/workflows/agent-run.yml>
  - Validate — `elis-validate.yml`  
    ↳ Open: <https://github.com/rochasamurai/ELIS-SLR-Agent/blob/main/.github/workflows/elis-validate.yml>
  - Deep Review — `deep-review.yml` (optional heavy gate)  
    ↳ Open: <https://github.com/rochasamurai/ELIS-SLR-Agent/blob/main/.github/workflows/deep-review.yml>
  - Housekeeping — `housekeeping.yml`  
    ↳ Open: <https://github.com/rochasamurai/ELIS-SLR-Agent/blob/main/.github/workflows/housekeeping.yml>
  - Export Docx — `export-docx.yml`  
    ↳ Open: <https://github.com/rochasamurai/ELIS-SLR-Agent/blob/main/.github/workflows/export-docx.yml>

- **Other**
  - Change log — `CHANGELOG.md`  
    ↳ Open: <https://github.com/rochasamurai/ELIS-SLR-Agent/blob/main/CHANGELOG.md>
  - Requirements — `requirements.txt`  
    ↳ Open: <https://github.com/rochasamurai/ELIS-SLR-Agent/blob/main/requirements.txt>
  - Test suite — `tests/`  
    ↳ Open: <https://github.com/rochasamurai/ELIS-SLR-Agent/tree/main/tests>
  - Artefacts folder — `json_jsonl/` (agent output)  
    ↳ Open: <https://github.com/rochasamurai/ELIS-SLR-Agent/tree/main/json_jsonl>

---

## Data Contract v1.0 (MVP)
The data contract is expressed as three JSON Schemas. They capture **only the
minimal fields** required for MVP; additional fields can be proposed later via PRs.

- Appendix A (Search): <https://github.com/rochasamurai/ELIS-SLR-Agent/blob/main/schemas/appendix_a.schema.json>  
- Appendix B (Screening): <https://github.com/rochasamurai/ELIS-SLR-Agent/blob/main/schemas/appendix_b.schema.json>  
- Appendix C (Extraction): <https://github.com/rochasamurai/ELIS-SLR-Agent/blob/main/schemas/appendix_c.schema.json>

<!-- Design choice: keep schemas intentionally small to make review and governance simpler. -->

---

## Quick start
> Works on Python 3.11+. Tested on macOS/Linux; Windows users should prefer WSL.

```bash
# 1) Create and activate a virtual environment (recommended)
python -m venv .venv && . .venv/bin/activate

# 2) Install runtime and dev tools
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install ruff==0.6.9 black==24.8.0 pytest

# 3) Generate toy artefacts (writes to json_jsonl/)
python scripts/agent.py

# 4) Validate artefacts (non-blocking; prints a short report)
python scripts/validate_json.py

# 5) Run tests (if any)
pytest -q
```

- Run CI manually: open **Actions → ELIS - CI → Run workflow**.  
- Try the agent in read-only mode on GitHub: **Actions → ELIS - Agent Run**.

---

## Workflows (GitHub Actions)
<!--
  Only the essentials are required for MVP. Heavy gates (typing/security/audit)
  exist but are optional and can be turned on by labelling PRs or manual runs.
-->

### 1) ELIS - CI (`ci.yml`)
- **quality:** Ruff + Black (check). Fails on issues.  
- **tests:** Runs only when `tests/**/*.py` exists; **exit 5** (“no tests collected”) is treated as success.  
- **validate:** Always runs; **non-blocking**; produces/updates a Markdown report.

Open file: <https://github.com/rochasamurai/ELIS-SLR-Agent/blob/main/.github/workflows/ci.yml>

### 2) ELIS - Bot Commit (`bot-commit.yml`)
Create/update one file on a working branch, commit it and optionally open/refresh a PR to `main`.
Inputs include `file_path`, `content_raw` or `content_b64`, `commit_message`, `base_branch`, `work_branch`, `open_pr`.

Open file: <https://github.com/rochasamurai/ELIS-SLR-Agent/blob/main/.github/workflows/bot-commit.yml>

### 3) ELIS - Autoformat (`autoformat.yml`)
Formats code with Black, normalises line endings, and can open a PR to `main` when configured.

Open file: <https://github.com/rochasamurai/ELIS-SLR-Agent/blob/main/.github/workflows/autoformat.yml>

### 4) ELIS - Agent Run (`agent-run.yml`)
Runs the toy agent against a chosen ref and uploads artefacts as build artifacts.

Open file: <https://github.com/rochasamurai/ELIS-SLR-Agent/blob/main/.github/workflows/agent-run.yml>

### 5) ELIS - Validate (`elis-validate.yml`)
Ensures a validation report exists; opens/refreshes a PR (`ci/validation-report`) only when the report changed.

Open file: <https://github.com/rochasamurai/ELIS-SLR-Agent/blob/main/.github/workflows/elis-validate.yml>

### Optional gates
- **Deep Review:** <https://github.com/rochasamurai/ELIS-SLR-Agent/blob/main/.github/workflows/deep-review.yml>  
- **Export Docx:** <https://github.com/rochasamurai/ELIS-SLR-Agent/blob/main/.github/workflows/export-docx.yml>  
- **Housekeeping:** <https://github.com/rochasamurai/ELIS-SLR-Agent/blob/main/.github/workflows/housekeeping.yml>

---

## Governance & branch protection
- **Required checks:** `quality`, `validate`. (`tests` runs when present.)  
- **Style & lint:** Black (format), Ruff (lint).  
- **Change pattern:** One file per commit where possible; clear, conventional commit messages.  
- **Merging:** Squash & merge; **delete head branches** after merge.  
- **Branch protection:** applied on `main` to enforce required checks.

> Tip: For small, independent edits use **ELIS - Bot Commit** with a short-lived working branch (e.g. `elis-bot-schemas-a`).

---

## Release process
1. Ensure `main` is green (CI passing).  
2. Draft a release: **Releases → Draft a new release**.  
3. Tag e.g. `v0.1.1-mvp`, target `main`, and publish (not a pre-release).  
4. Include concise notes (what changed; why).  
5. Optionally run: **ELIS - Agent Run** and **ELIS - Housekeeping**.

- Releases page: <https://github.com/rochasamurai/ELIS-SLR-Agent/releases>  
- Tags view: <https://github.com/rochasamurai/ELIS-SLR-Agent/tags>

---

## Troubleshooting

**Black “would reformat …” on CI**  
Run **ELIS - Autoformat** against your working branch or format locally with:  
`black .`

**Ruff I001 (imports unsorted)**  
Run `ruff --fix .` locally.

**Non fast-forward when pushing from automation**  
Use a fresh short-lived working branch or re-run **ELIS - Bot Commit**, which resets the branch safely.

**Base64 errors**  
Prefer `content_raw` for text; the workflow converts `\n` sequences to real newlines and normalises CRLF→LF.

---

## Frequently asked questions

**Is `validate` required to pass for merging?**  
No. It is **non-blocking** by design; it produces a report and a PR when the report changes.

**Can we validate strict RFC 3339 `date-time`?**  
Yes. Add `jsonschema[format-nongpl]` and enable `FormatChecker` in `scripts/validate_json.py` if stricter checking is desired.

**Where do artefacts go?**  
To the `json_jsonl/` directory at the repo root (created on first run).

---

## Contributing
- Prefer small, focused PRs.  
- Keep comments and documentation in **UK English**.  
- Follow repository style: Black and Ruff; CI must be green prior to merging.

---

## Changelog
See `CHANGELOG.md`: <https://github.com/rochasamurai/ELIS-SLR-Agent/blob/main/CHANGELOG.md>

---

## Licence
Internal project for the ELIS SLR Agent. External licence text is intentionally omitted here.
