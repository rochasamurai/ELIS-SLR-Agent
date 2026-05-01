# ELIS Token Usage Guidelines — Implementation Plan

**Document status:** Draft v1.0  
**Scope:** ELIS-SLR-Agent, OpenClaw, Codex, Claude Code, OpenRouter, local `elis-server`, Dockerised agent sessions  
**Objective:** Implement the ELIS Token Usage Guidelines with measurable reduction in PM input tokens, controlled OpenRouter usage, and preserved Implementer/Validator audit discipline.  
**Related documents:**
- `docs/governance/ELIS_General_Guidance.md`
- `docs/governance/ELIS_Multi_Agent_Governance_Architecture_v2.md`
- `docs/governance/ELIS_Multi_Agent_Governance_Implementation_Plan_v2.md`
- `docs/governance/ELIS_Token_Usage_Guidelines_for_Multi_AI_Agents.md`

---

## 1. Implementation Objective

Reduce normal PM input-token consumption by at least **85%**, with a stretch target of **90%**, while preserving:

- task routing quality;
- Implementer/Validator independence;
- `HANDOFF.md` and `REVIEW.md` discipline;
- raw validation evidence;
- deterministic ELIS pipeline governance;
- model-provider cost control.

The target is to move PM sessions from approximately **153k input tokens** to **10k–15k input tokens** for routine coordination.

---

## 2. Baseline

Recent telemetry identified one expensive PM OpenRouter-backed session:

```text
session: agent:pm:discord:channel:1498628408572383282
model: deepseek/deepseek-v4-pro
input tokens: 152,958
output tokens: 1,060
estimated cost: approximately USD 0.067 at cached rate
```

Known prompt contributors:

```text
systemPrompt: 45,932 chars
tools schema: 31,729 chars
skills: 7,302 chars
AGENTS.md: 11,999 chars
```

Diagnosis:

> The PM session was prompt-heavy and low-output. Cost was driven by context injection, not response generation.

---

## 3. Target State

### 3.1 PM Profiles

Create two PM modes:

```text
pm-lite — default low-context coordinator
pm-full — explicit escalation mode
```

### 3.2 Target Budgets

| Profile | Warning | Hard Stop | Intended Use |
|---|---:|---:|---|
| `pm-lite` | 8k input tokens | 15k input tokens | routine coordination |
| `pm-full` | 20k input tokens | 30k input tokens | architecture, release, validation conflict |

Escalation from `pm-lite` to `pm-full` must record the reason and the triggering task.

### 3.3 Expected Reduction

| Layer | Current | Target |
|---|---:|---:|
| PM system prompt | 45,932 chars | <8,000 chars |
| tools schema | 31,729 chars | <6,000 chars |
| skills | 7,302 chars | <1,500 chars index |
| root `AGENTS.md` | 11,999 chars | <2,000 chars |
| Discord/channel history | unbounded | rolling summary <1,500 tokens |

---

## 4. Work Package Overview

| Work Package | Name | Owner Role | Priority |
|---|---|---|---|
| WP1 | Baseline telemetry harness | Implementer | P0 |
| WP2 | PM profile split | Implementer | P0 |
| WP3 | Prompt diet | Implementer | P0 |
| WP4 | Root `AGENTS.md` minimisation | Implementer | P0 |
| WP5 | Tool schema gating | Implementer | P0 |
| WP6 | Skills index and demand loading | Implementer | P1 |
| WP7 | Channel history summarisation | Implementer | P1 |
| WP8 | OpenRouter guardrails | Implementer | P0 |
| WP9 | Validator gates | Validator | P0 |
| WP10 | Documentation and release integration | PM + Validator | P1 |
| WP11 | Rollout and migration order | PM | P0 |

---

## 5. WP1 — Baseline Telemetry Harness

### Objective

Create a repeatable way to measure input tokens, output tokens, loaded context layers, tool schemas, skills, model, provider, and estimated cost per agent run.

### Tasks

1. Identify where OpenClaw records local session telemetry.
2. Add or confirm capture of:

```text
session id
agent id
role
profile: pm-lite / pm-full / specialist
provider
model
input tokens
output tokens
cached input tokens
estimated cost
system prompt size
tool schema size
skills size
AGENTS.md size
history size
loaded files
escalation reason
```

3. Create a small reporting script or command:

```bash
python scripts/token_audit.py --last 20 --agent pm
```

4. Produce a baseline table for the latest PM sessions.

### Deliverables

```text
scripts/token_audit.py
docs/reports/token_baseline_pm.md
```

### Acceptance Criteria

```text
PASS if telemetry shows per-run token/cost breakdown by context layer.
FAIL if the validator cannot reproduce the reported totals.
```

---

## 6. WP2 — PM Profile Split

### Objective

Separate routine PM coordination from full-context PM escalation.

### Tasks

1. Create or configure `pm-lite`.
2. Create or configure `pm-full`.
3. Set `pm-lite` as the default PM profile.
4. Restrict `pm-full` to explicit escalation triggers.

### Suggested Configuration

```yaml
pm-lite:
  description: Default low-context PM coordinator
  provider: openai-codex
  model: gpt-5.4-mini
  max_input_tokens: 15000
  default_tools: routing_only
  skills: index_only
  history: rolling_summary
  openrouter: disabled_by_default

pm-full:
  description: Escalated PM for architecture and release decisions
  provider: openai-codex
  model: gpt-5.4
  max_input_tokens: 30000
  default_tools: selected_by_task
  skills: demand_loaded
  history: relevant_recent_context
  openrouter: fallback_only_with_reason
```

### Deliverables

```text
.openclaw/profiles/pm-lite.yaml
.openclaw/profiles/pm-full.yaml
```

### Acceptance Criteria

```text
PASS if normal PM calls use pm-lite by default.
PASS if pm-full requires an escalation reason.
FAIL if routine PM calls can still inject full PM context.
```

---

## 7. WP3 — Prompt Diet

### Objective

Reduce PM system prompt from approximately 45,932 characters to under 8,000 characters.

### Tasks

1. Extract mandatory PM rules from the current system prompt.
2. Remove examples, historical explanations, and long doctrine.
3. Move detailed material to demand-loaded reference files.
4. Create compact PM prompt files.

### Proposed Files

```text
.openclaw/context/pm_core.md
.openclaw/context/pm_full_extension.md
.openclaw/context/cost_policy.md
.openclaw/context/agent_roster.md
```

### Draft `pm_core.md`

```md
# PM Core

Coordinate ELIS multi-agent development. Use the Implementer/Validator protocol. Keep context small. Delegate implementation and validation to independent specialist agents.

Rules:
1. Do not let the same agent implement and validate the same task.
2. Every implementation task must produce or update HANDOFF.md when applicable.
3. Every validation task must produce or update REVIEW.md with the latest verdict.
4. Prefer small, reversible changes.
5. Do not load large files, full logs, full tool schemas, or long history unless needed.
6. Use summaries for routing, but raw evidence for final validation.
7. OpenRouter is fallback/escalation only and requires a reason.
8. Default to pm-lite unless escalation criteria are met.
```

### Deliverables

```text
.openclaw/context/pm_core.md
.openclaw/context/pm_full_extension.md
.openclaw/context/cost_policy.md
```

### Acceptance Criteria

```text
PASS if pm-lite system prompt is under 8,000 characters.
PASS if mandatory governance rules remain present.
FAIL if Implementer/Validator independence is omitted.
```

---

## 8. WP4 — Root `AGENTS.md` Minimisation

### Objective

Reduce root `AGENTS.md` from approximately 11,999 characters to under 2,000 characters.

### Tasks

1. Replace root `AGENTS.md` with a compact bootstrap.
2. Move detailed instructions into specialist files.
3. Add a loading rule that specialist files must be read only when relevant.

### Proposed Structure

```text
AGENTS.md
.openclaw/agents/pm-full.md
.openclaw/agents/prog-implementer.md
.openclaw/agents/prog-validator.md
.openclaw/agents/infra-implementer.md
.openclaw/agents/infra-validator.md
.openclaw/agents/researcher.md
.openclaw/agents/security-reviewer.md
```

### Root `AGENTS.md` Target Content

```md
# ELIS Agent Rules

Use the Implementer/Validator protocol.

Mandatory workflow:
- Implementer performs changes.
- Independent validator reviews changes.
- HANDOFF.md records implementation details when applicable.
- REVIEW.md records the latest validation verdict.
- Do not leave stale FAIL verdicts after fixes.

Repository principles:
- Less is more.
- Preserve deterministic outputs.
- Prefer canonical paths.
- Avoid duplicate legacy flows.

Load specialist instructions from `.openclaw/agents/` only when the task requires them.
```

### Deliverables

```text
AGENTS.md
.openclaw/agents/*.md
```

### Acceptance Criteria

```text
PASS if root AGENTS.md is under 2,000 characters.
PASS if specialist rules are available on demand.
FAIL if root AGENTS.md still embeds detailed specialist doctrine.
```

---

## 9. WP5 — Tool Schema Gating

### Objective

Reduce PM tool schema injection by at least 75%.

### Tasks

1. List all tools currently available to PM.
2. Classify each as:

```text
PM default
PM escalation
specialist only
forbidden for PM
```

3. Configure `pm-lite` with routing/status tools only.
4. Configure `pm-full` with selected tools by task.
5. Move shell/git/docker/write tools to specialist profiles.

### PM Default Tool Allowlist

```text
read_recent_messages
send_message
list_agents
delegate_task
create_task
read_task_status
record_decision
```

### Specialist-Only Tools

```text
shell execution
filesystem write
git write
docker control
browser automation
large repository search
deployment operations
```

### Deliverables

```text
.openclaw/tools/pm-lite-tools.yaml
.openclaw/tools/pm-full-tools.yaml
.openclaw/tools/specialist-tools.yaml
```

### Acceptance Criteria

```text
PASS if pm-lite tool schema is under 6,000 characters.
PASS if shell/write tools are not injected into pm-lite.
FAIL if PM still receives all tool schemas by default.
```

---

## 10. WP6 — Skills Index and Demand Loading

### Objective

Replace always-loaded skills with a compact skills index.

### Tasks

1. Create a skills index.
2. Move full skill bodies into dedicated files.
3. Ensure PM sees names, descriptions, and paths only.
4. Ensure specialist agents load full skill content only when selected.

### Proposed Skills Index

```md
# Skills Index

- release_planning: release gates and PE planning. Path: `.openclaw/skills/release_planning/SKILL.md`
- code_review: validator review tasks. Path: `.openclaw/skills/code_review/SKILL.md`
- repo_hygiene: HANDOFF/REVIEW checks. Path: `.openclaw/skills/repo_hygiene/SKILL.md`
- cost_audit: token and cost telemetry. Path: `.openclaw/skills/cost_audit/SKILL.md`
- infra_ops: Docker, VPS, OpenClaw operations. Path: `.openclaw/skills/infra_ops/SKILL.md`
- security_review: permissions and supply-chain risk. Path: `.openclaw/skills/security_review/SKILL.md`
```

### Deliverables

```text
.openclaw/skills/index.md
.openclaw/skills/*/SKILL.md
```

### Acceptance Criteria

```text
PASS if PM receives only the skills index by default.
PASS if full skills are loaded only after task selection.
FAIL if full skill bodies remain always injected.
```

---

## 11. WP7 — Channel History Summarisation

### Objective

Prevent Discord or Telegram channel history from becoming an unbounded token sink.

### Tasks

1. Create a rolling summary file or memory object for each PM channel.
2. Replace raw history with compact task state.
3. Include raw prior messages only when required.

### Rolling Summary Template

```md
# Channel Working Summary

Current objective:

Latest decision:

Active task:

Assigned implementer:

Assigned validator:

Open blockers:

Latest validation verdict:

Next action:
```

### Deliverables

```text
.openclaw/state/channel_summaries/<channel_id>.md
```

### Acceptance Criteria

```text
PASS if normal PM channel context is under 1,500 tokens.
PASS if exact history can still be retrieved when needed.
FAIL if full channel history is injected by default.
```

---

## 12. WP8 — OpenRouter Guardrails

### Objective

Prevent accidental OpenRouter spend from large PM prompts.

### Tasks

1. Disable OpenRouter for `pm-lite` by default.
2. Require escalation reason for PM OpenRouter calls.
3. Block PM OpenRouter calls above 30,000 input tokens unless explicitly approved.
4. Log all PM OpenRouter usage.

### Suggested Policy

```yaml
openrouter_policy:
  pm-lite:
    enabled: false
  pm-full:
    enabled: fallback_only
    require_reason: true
    hard_limit_input_tokens: 30000
    allowed_reasons:
      - codex_oauth_unavailable
      - architecture_decision
      - validation_conflict
      - security_escalation
      - repeated_agent_failure
      - explicit_user_request
```

### Deliverables

```text
.openclaw/policies/openrouter_policy.yaml
```

### Acceptance Criteria

```text
PASS if PM OpenRouter calls require a reason.
PASS if PM OpenRouter calls above 30k input tokens are blocked.
FAIL if OpenRouter can be used by PM silently.
```

---

## 12A. Codex OAuth Usage-Limit Guardrail

### Objective

Handle Codex OAuth usage-limit failures separately from OpenAI API-key RPM/TPM limits and OpenRouter credit exhaustion.

### Required behaviour

When an OAuth-backed Hermes/OpenClaw path receives:

```text
HTTP 429: The usage limit has been reached
```

the agent or wrapper must:

1. Stop safely after the first failed retry cycle.
2. Record provider, model, approximate context size, task, and timestamp.
3. Avoid mutating files after the limit event.
4. Recommend `SESSION_HANDOFF` or a fresh session.
5. Require PO approval before fallback to another provider.
6. Never treat repeated 429 retries as productive work.

### Deliverables

```text
docs/checklists/codex_oauth_usage_limit_checklist.md
```

### Acceptance Criteria

```text
PASS if Codex OAuth 429 usage-limit events are classified separately from API RPM/TPM and OpenRouter credit failures.
PASS if fallback providers require a recorded PO approval.
FAIL if the agent silently retries until the user receives only a failed response.
```


## 13. WP9 — Validator Gates

### Objective

Ensure token reduction does not weaken ELIS validation discipline.

### Tasks

1. Add validator checklist for token-guideline compliance.
2. Validate raw evidence for final verdicts.
3. Confirm no stale `REVIEW.md` state.
4. Confirm `HANDOFF.md` exists where required.
5. Confirm PM summaries do not replace validation evidence.

### Validator Checklist

```text
[ ] pm-lite used for routine PM session?
[ ] input tokens under 15k?
[ ] OpenRouter disabled or justified?
[ ] root AGENTS.md under 2,000 chars?
[ ] PM tools restricted to routing/status?
[ ] skills index used instead of full skills?
[ ] long channel history summarised?
[ ] raw validation evidence preserved?
[ ] HANDOFF.md present where applicable?
[ ] REVIEW.md latest verdict is not stale?
```

### Deliverables

```text
docs/checklists/token_guidelines_validator_checklist.md
```

### Acceptance Criteria

```text
PASS if validator can independently confirm token-guideline compliance.
FAIL if PM savings are achieved by hiding evidence required for validation.
```

---

## 14. WP10 — Documentation and Release Integration

### Objective

Make token governance part of the ELIS development protocol.

### Tasks

1. Add the conceptual guidelines document to project documentation.
2. Add this implementation plan to project documentation.
3. Reference both from release planning documents.
4. Add a token-budget section to future PE templates.
5. Add telemetry review to release-candidate checks.

### Proposed Locations

```text
docs/governance/ELIS_General_Guidance.md
docs/governance/ELIS_Token_Usage_Guidelines_for_Multi_AI_Agents.md
docs/governance/ELIS_Token_Usage_Guidelines_Implementation_Plan.md
docs/checklists/token_guidelines_validator_checklist.md
docs/checklists/codex_oauth_usage_limit_checklist.md
```

### Acceptance Criteria

```text
PASS if token governance is visible in the repo and referenced by PE templates.
FAIL if the documents exist but are not operationally connected to agent workflows.
```

---

## 15. Implementation Sequence

### Phase 1 — Safe Immediate Reduction

1. Create `pm-lite` and `pm-full` profiles.
2. Reduce PM system prompt.
3. Reduce root `AGENTS.md`.
4. Disable OpenRouter for `pm-lite`.
5. Add context hard stop for PM.

Expected saving: **50%–70%**.

### Phase 2 — Structural Reduction

1. Gate tool schemas.
2. Replace full skills with skills index.
3. Add rolling channel summary.
4. Add token telemetry reporting.

Expected cumulative saving: **75%–90%**.

### Phase 3 — Governance Integration

1. Add validator checklist.
2. Add PE template token-budget section.
3. Add release-candidate token audit.
4. Review OpenRouter exceptions monthly.

Expected result: durable cost control.

---

## 16. Preflight / Self-Test Workflow

Before enabling the new PM configuration, run a local preflight.

### Manual Preflight

```bash
# 1. Measure current PM bootstrap size
python scripts/token_audit.py --agent pm --last 5

# 2. Run pm-lite dry run
openclaw run --agent pm-lite --dry-run "Classify this task and assign implementer/validator."

# 3. Confirm OpenRouter is blocked for pm-lite
openclaw run --agent pm-lite --provider openrouter --dry-run "Test OpenRouter guardrail."

# 4. Confirm pm-full requires reason
openclaw run --agent pm-full --dry-run "Escalate architecture decision." --reason "architecture_decision"

# 5. Validate root AGENTS.md size
python scripts/check_file_size.py AGENTS.md --max-chars 2000
```

### Expected Results

```text
pm-lite dry run succeeds under 15k input tokens.
pm-lite OpenRouter direct use is blocked.
pm-full accepts OpenRouter only with reason.
AGENTS.md size check passes.
Tool schema loaded into pm-lite is routing/status only.
```

---

## 17. Suggested GitHub Actions Workflow Dispatch

Create a preflight workflow so the user can validate the token-governance configuration manually before using it in production.

```yaml
name: Token Governance Preflight

on:
  workflow_dispatch:

jobs:
  token-governance-preflight:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Check root AGENTS.md size
        run: |
          python - <<'PY'
          from pathlib import Path
          p = Path('AGENTS.md')
          if not p.exists():
              raise SystemExit('AGENTS.md is missing')
          size = len(p.read_text(encoding='utf-8'))
          print(f'AGENTS.md chars: {size}')
          if size > 2000:
              raise SystemExit('AGENTS.md exceeds 2,000 characters')
          PY

      - name: Check required token governance docs
        run: |
          test -f docs/governance/ELIS_Token_Usage_Guidelines_for_Multi_AI_Agents.md
          test -f docs/governance/ELIS_Token_Usage_Guidelines_Implementation_Plan.md

      - name: Check PM profile files
        run: |
          test -f .openclaw/profiles/pm-lite.yaml
          test -f .openclaw/profiles/pm-full.yaml

      - name: Check OpenRouter policy file
        run: |
          test -f .openclaw/policies/openrouter_policy.yaml
```

---

## 18. Definition of Done

The implementation is complete when:

```text
[ ] pm-lite is default for routine PM sessions.
[ ] pm-lite normal input tokens are <=15k.
[ ] pm-full requires escalation reason.
[ ] OpenRouter PM calls require justification.
[ ] PM OpenRouter calls above 30k input tokens are blocked.
[ ] root AGENTS.md is under 2,000 characters.
[ ] PM system prompt is under 8,000 characters.
[ ] PM tools are routing/status only by default.
[ ] skills are represented by an index by default.
[ ] Discord/channel history is summarised.
[ ] raw validation evidence remains available.
[ ] validator checklist is committed.
[ ] token governance preflight passes.
```

---

## 19. References

- OpenClaw documentation, “System prompt”: https://docs.openclaw.ai/concepts/system-prompt
- OpenAI Agents SDK, “Context management”: https://openai.github.io/openai-agents-python/context/
- OpenAI Cookbook, “Context Engineering — Short-Term Memory Management”: https://developers.openai.com/cookbook/examples/agents_sdk/session_memory
- Anthropic Engineering, “Effective context engineering for AI agents”: https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- Anthropic, “Best practices for Claude Code”: https://code.claude.com/docs/en/best-practices
- HumanLayer, “Writing a good CLAUDE.md”: https://www.humanlayer.dev/blog/writing-a-good-claude-md
- Google Developers Blog, “Architecting efficient context-aware multi-agent framework for production”: https://developers.googleblog.com/architecting-efficient-context-aware-multi-agent-framework-for-production/
- VoltAgent, “awesome-openclaw-skills”: https://github.com/VoltAgent/awesome-openclaw-skills
