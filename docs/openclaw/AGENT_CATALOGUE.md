# OpenClaw Agent Catalogue

> Generated 2026-02-26. Source of truth: `openclaw/openclaw.json` and workspace `AGENTS.md` files.

---

## 1. Agent Overview (13 agents)

| ID | Domain | Role | Model | Workspace |
|---|---|---|---|---|
| `pm` | — | Orchestrator / Project Manager | GPT-5.1 Codex | `workspace-pm` |
| `prog-impl-codex` | Programs | Implementer | GPT-5.1 Codex | `workspace-prog-impl` |
| `prog-impl-claude` | Programs | Implementer | Claude Sonnet 4.6 | `workspace-prog-impl` |
| `prog-val-codex` | Programs | Validator | GPT-5.1 Codex | `workspace-prog-val` |
| `prog-val-claude` | Programs | Validator | Claude Sonnet 4.6 | `workspace-prog-val` |
| `slr-impl-codex` | SLR | Implementer | GPT-5.1 Codex | `workspace-slr-impl` |
| `slr-impl-claude` | SLR | Implementer | Claude Sonnet 4.6 | `workspace-slr-impl` |
| `slr-val-codex` | SLR | Validator | GPT-5.1 Codex | `workspace-slr-val` |
| `slr-val-claude` | SLR | Validator | Claude Sonnet 4.6 | `workspace-slr-val` |
| `infra-impl-codex` | Infrastructure | Implementer | GPT-5.1 Codex | `workspace-infra-impl` |
| `infra-impl-claude` | Infrastructure | Implementer | Claude Sonnet 4.6 | `workspace-infra-impl` |
| `infra-val-codex` | Infrastructure | Validator | GPT-5.1 Codex | `workspace-infra-val` ⚠️ |
| `infra-val-claude` | Infrastructure | Validator | Claude Sonnet 4.6 | `workspace-infra-val` ⚠️ |

> ⚠️ `workspace-infra-val` does not yet exist in the repo. `infra-val-codex` and
> `infra-val-claude` are declared in `openclaw.json` but have no AGENTS.md, CLAUDE.md,
> or CODEX.md. These agents cannot operate until the workspace is created and deployed.

---

## 2. Agent Functional Descriptions

### 2.1 PM Agent (`pm`)

**Model:** GPT-5.1 Codex
**Channel:** Telegram (PO only — sole externally-bound agent)

The PM Agent is the sole orchestrator. It is the only agent the PO interacts with
directly via Telegram. All 10 worker agents are internal and are never exposed to the PO.

**Responsibilities:**
- Receive PE (Programmable Execution) assignments from PO via Telegram
- Enforce the alternation rule: for consecutive PEs in the same domain, the Implementer
  engine must alternate (CODEX ↔ Claude Code); Validator is always the opposite engine
- Read and update `CURRENT_PE.md` (Active PE Registry)
- Assign the correct Implementer for Gate 1 and Validator for Gate 2
- Manage Gate 1 → Gate 2 transitions
- Report project status to PO on request
- Escalate blockers that exceed agent authority (>2 FAIL iterations, scope disputes,
  release decisions)

**Constraints:**
- Does NOT write code
- Does NOT validate PRs
- Does NOT merge PRs
- Does NOT make technical decisions

---

### 2.2 Programs Implementers (`prog-impl-codex`, `prog-impl-claude`)

**Domain:** Python source, CLI extensions, source adapters, unit and integration tests
**Workspace:** `workspace-prog-impl` (shared; engine determined by CURRENT_PE.md)

Both agents share identical rules. The active engine alternates per PE per the
alternation rule enforced by PM.

**Responsibilities:**
- Implement Python source changes within the assigned PE scope
- Run quality gates: `black --check`, `ruff`, `pytest` — all must pass before PR
- Write `HANDOFF.md` with all required sections before pushing
- Open PR against the base branch
- Deliver a Status Packet to PM

**Constraints:**
- May only touch files listed in the PE plan deliverables
- May not write `REVIEW_PE*.md`
- May not merge PRs
- Must document any out-of-scope changes in HANDOFF.md and notify PM before proceeding

---

### 2.3 Programs Validators (`prog-val-codex`, `prog-val-claude`)

**Domain:** Python source, CLI, adapters, tests
**Workspace:** `workspace-prog-val` (shared; engine is always opposite of Implementer)

**Responsibilities:**
- Fetch and review the Implementer's PR diff (`gh pr diff`)
- Verify CI is green before issuing Stage 2 verdict
- Run at least one adversarial (negative-path) test
- Post **Stage 1** evidence comment (scope, logic, adversarial test results)
- Post **Stage 2** verdict comment (PASS / FAIL)
- Commit `REVIEW_PE_<N>.md` to the feature branch
- Submit a formal GitHub PR review (`approve` for PASS, `request-changes` for FAIL)
- On FAIL: list blocking findings; on PASS: confirm all ACs met

**Single-account fallback:** If reviewer and PR author share the same GitHub account,
post FAIL verdict as a plain comment and apply `pm-review-required` label.

**Constraints:**
- May not implement feature scope
- May not write HANDOFF.md
- Must not push to feature branches except for REVIEW file and authorized minimal fixes
- Must not issue PASS while CI is failing

---

### 2.4 SLR Implementers (`slr-impl-codex`, `slr-impl-claude`)

**Domain:** Systematic Literature Review artifacts
**Workspace:** `workspace-slr-impl`

**Responsibilities:**
- Produce and update SLR artifacts in a reproducible and auditable way:
  - Screening decisions (`include` / `exclude` + reason code)
  - Data extraction sheets (structured field map per included study)
  - PRISMA flow records (identification, screening, eligibility, inclusion)
  - Synthesis notes (narrative or tabular)
  - Protocol deviation log (dated, justified, approved)
- Run `check_slr_quality.py` in addition to standard quality gates
- Ensure internal consistency of PRISMA stage counts

**SLR acceptance criteria types (every PE must cover all five):**
1. Eligibility compliance — decisions map to explicit inclusion/exclusion criteria
2. Extraction completeness — mandatory fields non-empty
3. Traceability — each included study has source ID + decision provenance
4. PRISMA consistency — stage counts internally consistent
5. Reproducibility — same inputs and rules produce same outputs

---

### 2.5 SLR Validators (`slr-val-codex`, `slr-val-claude`)

**Domain:** Systematic Literature Review
**Workspace:** `workspace-slr-val`

Same two-stage comment protocol as programs validators, plus SLR-specific checks:

1. **Eligibility-rule fidelity** — inclusion/exclusion decisions align with protocol criteria
2. **Dual-reviewer agreement threshold** — agreement metric meets configured minimum
3. **PRISMA arithmetic consistency** — stage totals and transitions internally consistent
4. **Extraction-to-synthesis traceability** — synthesized claims map back to extracted studies

Protocol violations and missing provenance links are **blocking findings**.

---

### 2.6 Infrastructure Implementers (`infra-impl-codex`, `infra-impl-claude`)

**Domain:** CI/CD, Docker, shell scripts, GitHub Actions, YAML config, deployment tooling
**Workspace:** `workspace-infra-impl`

**Responsibilities:**
- Implement infrastructure changes within PE scope
- Comply with infra-specific standards:
  - Shell scripts: `#!/usr/bin/env bash` + `set -euo pipefail`; all variables quoted
  - Docker: no `latest` tags; explicit pinned tags; external ports bind to `127.0.0.1` only
  - CI workflows: every job/step has a `name:`; no inline secrets; `${{ secrets.X }}` only
  - YAML: validate with schema or lint step before committing
- **Hard limit (§5.4):** The ELIS repository must NEVER be mounted inside the OpenClaw
  Docker container. Workspace files are deployed host-side via `deploy_openclaw_workspaces.sh`.

---

### 2.7 Infrastructure Validators (`infra-val-codex`, `infra-val-claude`) ⚠️

**Domain:** Infrastructure
**Workspace:** `workspace-infra-val` — **does not yet exist**

These agents are declared in `openclaw.json` but are not operational. The workspace
must be created (AGENTS.md + CLAUDE.md + CODEX.md) before they can be assigned.

When operational, they will follow the same two-stage comment protocol as programs
validators, with additional infra-specific security checks (port bindings, secret
handling, container isolation).

---

## 3. How Agents Collaborate with PM

```
PO (Telegram)
     │  plain text commands (assign, status, escalate)
     ▼
  [ pm ]  ─── reads CURRENT_PE.md (domain, alternation, base branch)
     │
     ├──▶  assigns Implementer (prog/slr/infra × codex/claude)
     │          │
     │          ▼
     │     Implementer:
     │       1. create branch from base branch
     │       2. implement PE deliverables
     │       3. run quality gates (black / ruff / pytest [/ check_slr_quality.py])
     │       4. write HANDOFF.md
     │       5. push branch + open PR
     │       6. deliver Status Packet to PM
     │          │
     │     CI Gate 1 bot comment posted on PR
     │          │
     ├──▶  assigns Validator (opposite engine)
     │          │
     │          ▼
     │     Validator:
     │       1. fetch PR diff + read HANDOFF.md
     │       2. verify CI green
     │       3. run adversarial test
     │       4. post Stage 1 evidence comment
     │       5. commit REVIEW_PE_<N>.md to feature branch
     │       6. post Stage 2 verdict + formal GitHub PR review
     │          │
     │     ┌────┴────┐
     │   PASS       FAIL
     │     │          │
     │     ▼          └──▶ PM routes required fixes to Implementer
     │   Gate 2              (repeat from Implementer step 2)
     │   (merge)             Max 2 FAIL iterations before PM escalates to PO
     │     │
     ▼     ▼
PO ← status reply (PE merged / blocked)
```

**Alternation rule enforced by PM at assignment time:**

| Previous Implementer (same domain) | Next Implementer | Next Validator |
|---|---|---|
| None (first PE in domain) | codex | claude |
| codex | claude | codex |
| claude | codex | claude |

---

## 4. Validation Plan — per Agent

### 4.1 PM Agent

| Test | Command / Action | Expected outcome |
|---|---|---|
| Channel health | `docker exec openclaw node openclaw.mjs channels status` | `enabled, configured, running, mode:polling, token:config` |
| PO sends `status` | Telegram: send `status` | PM replies with Active PE Registry table within 30 s |
| PE assignment | Telegram: send `assign PE-TEST-01: smoke test` | PM replies with §2.2 format (PE-ID, Implementer, Validator, Branch, Status: planning) |
| Registry updated | Check CURRENT_PE.md after assignment | New row present with `planning` status |
| Alternation enforced | Assign 2 consecutive PEs in same domain | Engines alternate correctly |
| Duplicate PE rejected | Assign same PE-ID twice | PM returns error, no duplicate row written |
| Escalation trigger | Force >2 FAIL iterations on a PE | PM escalates to PO with blocker message |

---

### 4.2 Programs Implementers

| Test | Verification |
|---|---|
| Correct branch created | `git branch --show-current` matches CURRENT_PE.md branch field |
| Only in-scope files changed | `git diff --name-status origin/$BASE..HEAD` — no unrelated files |
| Quality gates pass | `black --check .` / `ruff check .` / `pytest -q` all exit 0 |
| HANDOFF.md complete before PR | All 6 sections present; committed before `git push` |
| PR targets correct base branch | `gh pr view` — base branch matches CURRENT_PE.md |
| Out-of-scope file | Agent flags in HANDOFF.md Design Decisions and notifies PM |

---

### 4.3 Programs Validators

| Test | Verification |
|---|---|
| Stage 1 comment posted first | PR comments — Stage 1 appears before Stage 2 |
| Stage 2 verdict posted | PR comments — Stage 2 present with PASS / FAIL |
| Formal GitHub review submitted | `gh pr view` — review state = `APPROVED` or `CHANGES_REQUESTED` |
| REVIEW_PE_*.md committed | File present on feature branch; `check_review.py` exits 0 |
| Adversarial test documented | Stage 1 comment contains negative-path test output |
| PASS blocked while CI failing | Val agent waits for green CI before Stage 2 |
| FAIL verdict on deliberate bug | Stage 2 FAIL with specific blocking finding listed |

---

### 4.4 SLR Implementers

| Test | Verification |
|---|---|
| Screening decisions include reason codes | Each decision row has a populated reason field |
| PRISMA counts consistent | Identification ≥ Screening ≥ Eligibility ≥ Inclusion; no negative transitions |
| `check_slr_quality.py` exits 0 | Run against output artifacts before PR |
| Protocol deviation logged | If any deviation, dated + justified entry in deviation log |
| Missing mandatory extraction field | Agent flags as incomplete, does not open PR |

---

### 4.5 SLR Validators

| Test | Verification |
|---|---|
| Eligibility-rule fidelity | Randomly audit 3 decisions against inclusion/exclusion criteria |
| PRISMA arithmetic | Inject mismatched count → blocking finding in Stage 1 |
| Inclusion violating criteria | Blocking finding; FAIL verdict |
| Missing traceability link | Blocked as extraction-to-synthesis traceability failure |
| Stage 1 + Stage 2 order | Stage 1 posted before Stage 2 |

---

### 4.6 Infrastructure Implementers

| Test | Verification |
|---|---|
| Shell script header | `#!/usr/bin/env bash` + `set -euo pipefail` present |
| Variable quoting | All `$VAR` references quoted as `"${VAR}"` |
| Port binding | External-facing ports use `127.0.0.1:X:X`, never `0.0.0.0` |
| No inline secrets in CI | `grep -r 'secrets\.' .github/` — only `${{ secrets.X }}` pattern |
| Container isolation | ELIS repo path not present in any `volumes:` mount |

---

### 4.7 Infrastructure Validators ⚠️

> **Prerequisite:** `workspace-infra-val` must be created and deployed.
> Suggested as PE-OC-21.

| Test (after workspace deployed) | Verification |
|---|---|
| Stage 1 + Stage 2 comments posted | Same protocol as programs validators |
| REVIEW file committed | `check_review.py` exits 0 |
| Security violation detected | Port `0.0.0.0` binding → blocking finding; FAIL verdict |
| Inline secret caught | CI workflow with literal secret → blocking finding |
| Container isolation violation | ELIS repo mount → §5.4 hard limit violation flagged |

---

## 5. Open Gap

`workspace-infra-val` is absent from the repository. `infra-val-codex` and
`infra-val-claude` are declared in `openclaw/openclaw.json` but have no workspace files.

**Required to close this gap:**
- Create `openclaw/workspaces/workspace-infra-val/` with `AGENTS.md`, `CLAUDE.md`, `CODEX.md`
- Run `scripts/deploy_openclaw_workspaces.sh` to deploy to host
- Restart container
- Verify agents appear in `node openclaw.mjs agent list`

This is a candidate for **PE-OC-21** (next in sequence; Implementer = CODEX per alternation).
