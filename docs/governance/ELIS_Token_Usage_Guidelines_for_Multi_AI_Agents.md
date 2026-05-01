# ELIS Token Usage Guidelines for Multi-AI Agents

**Document status:** Draft v1.0  
**Scope:** ELIS-SLR-Agent, OpenClaw, Codex, Claude Code, OpenRouter-backed models, local and VPS agent sessions  
**Purpose:** Define conceptual rules for reducing token consumption, preserving auditability, and avoiding uncontrolled prompt/context growth in ELIS multi-agent workflows.  
**Related documents:**
- `docs/governance/ELIS_General_Guidance.md`
- `docs/governance/ELIS_Multi_Agent_Governance_Architecture_v2.md`
- `docs/governance/ELIS_Multi_Agent_Governance_Implementation_Plan_v2.md`
- `docs/governance/ELIS_Token_Usage_Guidelines_Implementation_Plan.md`

---

## 1. Executive Principle

ELIS agents must treat context as an explicit engineering resource.

The default operating model is:

> **Small supervisor context, specialist context on demand, raw evidence for final validation.**

The PM agent should coordinate work. It should not carry all project doctrine, all tools, all skills, all channel history, or full repository state in every run. Heavy context must be loaded only by the agent that needs it and only for the duration of the specific task.

---

## 2. Problem Statement

Recent local telemetry showed one OpenRouter-backed PM session with:

- **Agent/session:** `agent:pm:discord:channel:1498628408572383282`
- **Model:** `deepseek/deepseek-v4-pro`
- **Input tokens:** 152,958
- **Output tokens:** 1,060
- **Estimated cost:** approximately USD 0.067 at cached rate

The critical pattern is that output was tiny compared with input. Cost was therefore driven almost entirely by prompt and context size, not by long replies.

Known PM context contributors included:

| Context Layer | Observed Size |
|---|---:|
| `systemPrompt` | 45,932 characters |
| tools schema | 31,729 characters |
| skills | 7,302 characters |
| `AGENTS.md` | 11,999 characters |

This is inconsistent with a cost-efficient PM role. The PM should usually operate in a compact routing and governance mode.

---

## 3. Design Goals

The guidelines aim to achieve:

1. **90% reduction target** for normal PM input tokens.
2. **Stable PM routing quality** despite reduced context.
3. **No weakening of the Implementer/Validator protocol.**
4. **No reliance on compressed summaries as final validation evidence.**
5. **Provider-cost control**, especially for OpenRouter-backed fallback or escalation models.
6. **Compatibility with local `elis-server`, Docker/OpenClaw, Codex OAuth, Claude Code, and specialist agents.**

---

## 4. Token Budget Targets

### 4.1 Normal PM Session

| Metric | Target |
|---|---:|
| Input tokens | 8,000–15,000 |
| Output tokens | As needed; normally <2,000 |
| Hard warning | 8,000 input tokens |
| Hard stop | 15,000 input tokens unless escalated |

### 4.2 Full PM Escalation Session

| Metric | Target |
|---|---:|
| Input tokens | 15,000–30,000 |
| Hard warning | 20,000 input tokens |
| Hard stop | 30,000 input tokens unless explicitly approved |

### 4.3 Specialist Agent Session

| Agent Type | Normal Budget | Escalated Budget |
|---|---:|---:|
| Program implementer | 15k–40k | 60k |
| Program validator | 15k–40k | 60k |
| Infrastructure implementer | 10k–30k | 50k |
| Infrastructure validator | 10k–30k | 50k |
| Research/synthesis agent | 20k–60k | task-specific |

Specialist agents may carry heavier task-specific context, but only after the PM has delegated a scoped task.

---

## 5. Agent Role Principles

### 5.1 PM Agent

The PM agent should:

- classify tasks;
- select implementer and validator agents;
- define acceptance criteria;
- enforce handoff and review discipline;
- monitor cost and escalation;
- maintain a rolling task summary;
- avoid direct code editing unless explicitly requested.

The PM agent should not normally carry:

- full repository context;
- full `AGENTS.md` doctrine;
- all skills;
- all tool schemas;
- long Discord/channel history;
- full CI logs;
- full diffs unless reviewing a specific escalation.

### 5.2 Implementer Agents

Implementer agents may load:

- relevant source files;
- relevant tests;
- selected specs;
- task-specific skills;
- command outputs needed to implement the change.

They should produce concise `HANDOFF.md` content or equivalent handoff notes.

### 5.3 Validator Agents

Validator agents may load:

- implementation diff;
- relevant tests;
- schemas and acceptance criteria;
- raw validation evidence.

Validator agents must not rely only on PM summaries when issuing a final verdict.

---

## 6. Context Loading Rules

### 6.1 Default Rule

Load the minimum context needed to make the next correct decision.

### 6.2 Always-Loaded Context

Always-loaded PM context must be limited to:

1. PM mission statement.
2. Implementer/Validator rule.
3. cost policy summary.
4. active task state.
5. short agent roster.
6. latest unresolved blocker, if any.

Target: **under 5,000 input tokens.**

### 6.3 Demand-Loaded Context

Demand-load the following only when the task requires them:

- full specialist skills;
- release-plan details;
- SDD governance documents;
- security policy;
- Docker/OpenClaw infrastructure notes;
- full `AGENTS.md` variants;
- large diffs;
- full logs;
- long research documents.

### 6.4 Forbidden Default Context

Do not inject by default:

- all project files;
- all skill bodies;
- all tool schemas;
- full channel history;
- full previous agent transcripts;
- old validation failures after they have been resolved.

---

## 7. Prompt Architecture

### 7.1 PM Prompt Layers

Use a layered prompt model:

```text
pm_core.md                 # always loaded, very small
agent_roster.md            # compact routing table
cost_policy.md             # compact policy
active_task_summary.md     # rolling summary, refreshed per task
```

Optional layers:

```text
release_rules.md           # release tasks only
sdd_rules.md               # SDD tasks only
security_rules.md          # security-sensitive tasks only
openrouter_policy.md       # model routing or cost review only
specialist_agent_rules.md  # loaded only for selected specialist
```

### 7.2 Root `AGENTS.md`

The root `AGENTS.md` should be short because it is often loaded automatically by coding-agent harnesses.

Target size: **under 2,000 characters.**

The root file should contain only:

- core workflow rules;
- Implementer/Validator independence;
- `HANDOFF.md` and `REVIEW.md` discipline;
- minimal repository principles;
- instruction to load specialist rules only when needed.

### 7.3 Specialist Agent Files

Move detailed instructions into specialist files, for example:

```text
.openclaw/agents/pm-full.md
.openclaw/agents/prog-implementer.md
.openclaw/agents/prog-validator.md
.openclaw/agents/infra-implementer.md
.openclaw/agents/infra-validator.md
.openclaw/agents/researcher.md
.openclaw/agents/security-reviewer.md
```

---

## 8. Tool Schema Governance

Tool schemas are often large and expensive. The PM must not carry every tool schema by default.

### 8.1 PM Default Tools

The PM should normally have only:

```text
read_recent_messages
send_message
list_agents
delegate_task
create_task
read_task_status
record_decision
```

### 8.2 Specialist-Only Tools

The following tools should normally be reserved for specialist agents or explicit escalation:

```text
shell execution
filesystem writes
git writes
docker control
browser automation
large repository search
large document ingestion
email/calendar operations
deployment operations
```

### 8.3 Tool Activation Rule

A tool schema should be injected only if the current agent is authorised and likely to use it in the current task.

---

## 9. Skills Governance

Skills should be treated as modular, demand-loaded capabilities.

### 9.1 Skills Index

The PM may receive a short skills index:

```text
release_planning — release gates and PE planning
code_review — validator review tasks
repo_hygiene — HANDOFF/REVIEW checks
cost_audit — token and cost telemetry
infra_ops — Docker, VPS, OpenClaw operations
security_review — risk and permission review
```

### 9.2 Skill Body Loading

Full skill bodies should be loaded only by the agent selected for a task.

### 9.3 Skill Security

All third-party skills must be reviewed before installation. Skills can contain unsafe instructions, prompt injections, tool-poisoning patterns, or malicious execution steps.

---

## 10. Conversation and Channel History

### 10.1 Rolling Summary

Discord, Telegram, or long chat history must be replaced with a rolling summary.

The rolling summary should include:

```text
current objective
latest decision
active task
assigned agents
open blockers
latest validation verdict
next action
```

Target size: **under 1,500 tokens.**

### 10.2 History Inclusion Rule

Include raw prior messages only when:

- the user explicitly asks for them;
- the previous wording is legally, technically, or procedurally material;
- a validation dispute requires exact history.

Otherwise, use summaries.

---

## 11. Model Routing and Provider Cost Policy

### 11.1 PM Default Provider

PM should default to the lowest-cost reliable provider available for coordination tasks, currently Codex OAuth in the user’s intended configuration.

### 11.2 OpenRouter Restrictions

OpenRouter-backed PM calls should be blocked unless one of the following applies:

- explicit user request;
- Codex OAuth unavailable;
- architecture decision;
- validation conflict;
- security-sensitive escalation;
- repeated specialist failure;
- model-specific capability requirement.

### 11.3 OpenRouter Context Limit

No PM OpenRouter call should exceed **30,000 input tokens** without explicit recorded justification.

### 11.4 Codex OAuth Usage-Limit Handling

Codex OAuth usage limits are not the same as OpenAI API-key RPM/TPM limits.

When Hermes or another OAuth-backed agent receives:

```text
HTTP 429: The usage limit has been reached
```

the agent must:

- stop safely instead of repeatedly retrying;
- record the provider, model, approximate message/token context, and task attempted;
- avoid mutating files after the limit event;
- recommend a fresh session or PO-approved fallback provider;
- distinguish this from OpenRouter credit exhaustion and OpenAI API-key quota/RPM/TPM limits.

Fallback providers must not be enabled automatically unless the PO has explicitly approved the fallback path.


---

## 12. Summaries, Compression, and Raw Evidence

Summaries are allowed for routing and coordination.

Raw evidence is required for:

- final validator verdicts;
- CI gates;
- release certification;
- schema validation results;
- security review findings;
- audit artefacts.

Compressed or summarised evidence must not be the only basis for `REVIEW.md`.

---

## 13. Telemetry Requirements

Each agent run should record:

```text
session id
agent id
role
provider
model
input tokens
output tokens
cached input tokens, if available
estimated cost
context layers loaded
tools schemas loaded
skills loaded
history strategy: raw / summary / mixed
escalation reason, if any
```

For PM sessions, additionally record:

```text
pm mode: pm-lite / pm-full
hard budget used
budget warning triggered: yes/no
OpenRouter allowed: yes/no
OpenRouter reason, if used
```

---

## 14. Acceptance Thresholds

A normal PM session is compliant if:

- input tokens are under 15,000;
- no heavy tools are loaded unless needed;
- no full skill bodies are loaded by default;
- root `AGENTS.md` remains under 2,000 characters;
- OpenRouter is not used unless justified;
- rolling summary replaces long channel history.

A PM session is non-compliant if:

- input tokens exceed 30,000 without recorded escalation;
- OpenRouter receives a large prompt without justification;
- full channel history is injected without need;
- full tool schemas are always loaded;
- stale validation failures remain in context after resolution;
- summaries are used as final validation evidence.

---

## 15. Operational Checklist

Before each PM call:

```text
[ ] Is this pm-lite or pm-full?
[ ] Is the user request included exactly?
[ ] Is long history summarised?
[ ] Are only PM tools loaded?
[ ] Are skills represented by index only?
[ ] Is AGENTS.md compact?
[ ] Is input under budget?
[ ] Is OpenRouter disabled unless explicitly justified?
```

Before each validator verdict:

```text
[ ] Raw diff reviewed?
[ ] Raw test output or CI output reviewed?
[ ] Relevant schema files reviewed if applicable?
[ ] Acceptance criteria checked?
[ ] HANDOFF.md checked?
[ ] REVIEW.md updated with latest verdict?
```

---

## 16. References

- OpenClaw documentation, “System prompt”: https://docs.openclaw.ai/concepts/system-prompt
- OpenAI Agents SDK, “Context management”: https://openai.github.io/openai-agents-python/context/
- OpenAI Cookbook, “Context Engineering — Short-Term Memory Management”: https://developers.openai.com/cookbook/examples/agents_sdk/session_memory
- Anthropic Engineering, “Effective context engineering for AI agents”: https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- Anthropic, “Best practices for Claude Code”: https://code.claude.com/docs/en/best-practices
- HumanLayer, “Writing a good CLAUDE.md”: https://www.humanlayer.dev/blog/writing-a-good-claude-md
- Google Developers Blog, “Architecting efficient context-aware multi-agent framework for production”: https://developers.googleblog.com/architecting-efficient-context-aware-multi-agent-framework-for-production/
- VoltAgent, “awesome-openclaw-skills”: https://github.com/VoltAgent/awesome-openclaw-skills
