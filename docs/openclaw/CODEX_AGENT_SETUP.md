# OpenClaw Agent Settings

**Document purpose:** Define the ELIS OpenClaw multi-agent model policy, including PM coordination, implementer/validator separation, and a named escalation path.

**Scope:** PM agent, programme agents, infrastructure agents, SLR agents, validator agents, implementer agents, and escalation/arbitration workflow.

---

## 1. Executive Summary

The recommended ELIS/OpenClaw setup should separate routine implementation, independent validation, PM coordination, and high-risk arbitration.

Core principle:

```txt
Cheap / fast models implement.
Stronger / independent models validate.
MiMo arbitrates only when necessary.
PM coordinates and records decisions.
```

The first-version configuration uses these model roles:

```txt
PM:           openrouter/deepseek/deepseek-v4-pro
Fallback:     openrouter/deepseek/deepseek-v3.2

Implementers: openrouter/qwen/qwen3-coder-flash
              openrouter/deepseek/deepseek-v4-flash

Validators:   openrouter/deepseek/deepseek-v4-pro
              openrouter/z-ai/glm-5.1

Escalation:   openrouter/xiaomi/mimo-v2.5-pro
```

This structure is functional and has three advantages:

1. **Lower routine cost** by using Flash/Coder models for implementation.
2. **Better role separation** between implementation and validation.
3. **Clear escalation path** by reserving MiMo for arbitration.

---

## 2. Recommended Model Roles

### 2.1 PM Agent

```txt
pm
Primary:  openrouter/deepseek/deepseek-v4-pro
Fallback: openrouter/deepseek/deepseek-v3.2
```

**Role:** coordination, task assignment, handoff review, validator routing, release governance, escalation decisions.

**Rationale:** DeepSeek V4 Pro is appropriate for PM coordination because it supports long-context reasoning, code-aware planning, and multi-step agent workflow supervision. DeepSeek V3.2 is the lower-cost fallback for continuity.

---

### 2.2 Implementer Agents

```txt
impl-a: openrouter/qwen/qwen3-coder-flash
impl-b: openrouter/deepseek/deepseek-v4-flash
```

**Role:** repository edits, workflow changes, implementation tasks, coding repairs, documentation updates, test additions.

**Rationale:** implementers should be cost-efficient and coding-oriented. Qwen3 Coder Flash is the coding-specialist agent. DeepSeek V4 Flash is the fast general implementation model.

---

### 2.3 Validator Agents

```txt
val-a: openrouter/deepseek/deepseek-v4-pro
val-b: openrouter/z-ai/glm-5.1
```

**Role:** independent review, technical validation, deterministic behaviour checks, schema/manifest review, CI review, release-gate review.

**Rationale:** validators should not simply mirror implementers. DeepSeek V4 Pro provides strong reasoning and long-context review. GLM-5.1 provides independent model-family diversity and stronger cross-checking.

---

### 2.4 Escalation Agent

```txt
escalation-reviewer: openrouter/xiaomi/mimo-v2.5-pro
```

**Role:** arbitration, conflict resolution, high-risk review, repeated failure review, PM-requested independent judgement.

**Rationale:** MiMo-V2.5-Pro should not be used as an ordinary fallback for every PM request. It should be reserved for situations where the cost of a mistake exceeds the cost of using a stronger arbitration model.

---

## 3. Fallback vs Escalation

Fallback and escalation are different mechanisms.

| Mechanism | Trigger | Purpose | Example |
|---|---|---|---|
| Fallback | Primary model error, outage, rate limit, context failure | Keep the agent running | PM primary model fails, so PM uses DeepSeek V3.2 |
| Escalation | Disagreement, uncertainty, failed validation, high-risk change | Improve decision quality | Validator A says PASS, Validator B says FAIL, so PM calls MiMo |

**Fallback is technical continuity.**

**Escalation is governance arbitration.**

Therefore, MiMo-V2.5-Pro should be configured as a named escalation agent, not merely as a fallback model.

---

## 4. Complete Agent Matrix

### 4.1 PM

```txt
pm — openrouter/deepseek/deepseek-v4-pro
fallback — openrouter/deepseek/deepseek-v3.2
escalates to — escalation-reviewer
```

---

### 4.2 Prog — Programs

```txt
prog-impl-a — openrouter/qwen/qwen3-coder-flash
prog-impl-b — openrouter/deepseek/deepseek-v4-flash

prog-val-a  — openrouter/deepseek/deepseek-v4-pro
prog-val-b  — openrouter/z-ai/glm-5.1
```

---

### 4.3 Infra — Infrastructure

```txt
infra-impl-a — openrouter/qwen/qwen3-coder-flash
infra-impl-b — openrouter/deepseek/deepseek-v4-flash

infra-val-a  — openrouter/deepseek/deepseek-v4-pro
infra-val-b  — openrouter/z-ai/glm-5.1
```

---

### 4.4 SLR — Harvest

```txt
harvest-impl-a — openrouter/deepseek/deepseek-v4-flash
harvest-impl-b — openrouter/qwen/qwen3-coder-flash

harvest-val-a  — openrouter/deepseek/deepseek-v4-pro
harvest-val-b  — openrouter/z-ai/glm-5.1
```

---

### 4.5 SLR — Screen

```txt
screen-impl-a — openrouter/deepseek/deepseek-v4-flash
screen-impl-b — openrouter/qwen/qwen3-coder-flash

screen-val-a  — openrouter/deepseek/deepseek-v4-pro
screen-val-b  — openrouter/z-ai/glm-5.1
```

---

### 4.6 SLR — Extract

```txt
extract-impl-a — openrouter/qwen/qwen3-coder-flash
extract-impl-b — openrouter/deepseek/deepseek-v4-flash

extract-val-a  — openrouter/deepseek/deepseek-v4-pro
extract-val-b  — openrouter/z-ai/glm-5.1
```

---

### 4.7 SLR — Synth

```txt
synth-impl-a — openrouter/deepseek/deepseek-v4-flash
synth-impl-b — openrouter/qwen/qwen3-coder-flash

synth-val-a  — openrouter/deepseek/deepseek-v4-pro
synth-val-b  — openrouter/z-ai/glm-5.1
```

---

### 4.8 SLR — Prisma

```txt
prisma-impl-a — openrouter/deepseek/deepseek-v4-flash
prisma-impl-b — openrouter/qwen/qwen3-coder-flash

prisma-val-a  — openrouter/deepseek/deepseek-v4-pro
prisma-val-b  — openrouter/z-ai/glm-5.1
```

---

### 4.9 Escalation

```txt
escalation-reviewer — openrouter/xiaomi/mimo-v2.5-pro
```

---

## 5. OpenClaw Model Allow-List

Use this as the conceptual model policy in `openclaw.json` or the equivalent OpenClaw settings file.

```json
{
  "env": {
    "OPENROUTER_API_KEY": "sk-or-..."
  },
  "agents": {
    "defaults": {
      "model": {
        "primary": "openrouter/deepseek/deepseek-v4-pro",
        "fallbacks": [
          "openrouter/deepseek/deepseek-v3.2"
        ]
      },
      "models": {
        "openrouter/deepseek/deepseek-v4-pro": {
          "alias": "deepseek-v4-pro",
          "purpose": "PM coordination, high-quality validation, long-context reasoning"
        },
        "openrouter/deepseek/deepseek-v3.2": {
          "alias": "deepseek-v3.2",
          "purpose": "PM fallback and lower-cost reasoning fallback"
        },
        "openrouter/deepseek/deepseek-v4-flash": {
          "alias": "deepseek-v4-flash",
          "purpose": "low-cost implementation, routine coding, SLR pipeline edits"
        },
        "openrouter/qwen/qwen3-coder-flash": {
          "alias": "qwen3-coder-flash",
          "purpose": "coding-specialist implementation agent"
        },
        "openrouter/z-ai/glm-5.1": {
          "alias": "glm-5.1",
          "purpose": "independent validation, long-horizon code review, engineering-grade review"
        },
        "openrouter/xiaomi/mimo-v2.5-pro": {
          "alias": "mimo-v2.5-pro",
          "purpose": "escalation, arbitration, conflict resolution, high-risk review"
        }
      }
    }
  }
}
```

---

## 6. Logical Agent Registry

This is a logical registry for agent assignment. The exact schema may need adjustment depending on the OpenClaw version installed on the ELIS server.

```json
{
  "agents": {
    "pm": {
      "role": "project-manager",
      "model": {
        "primary": "openrouter/deepseek/deepseek-v4-pro",
        "fallbacks": [
          "openrouter/deepseek/deepseek-v3.2"
        ]
      },
      "can_call": [
        "prog-impl-a",
        "prog-impl-b",
        "prog-val-a",
        "prog-val-b",
        "infra-impl-a",
        "infra-impl-b",
        "infra-val-a",
        "infra-val-b",
        "harvest-impl-a",
        "harvest-impl-b",
        "harvest-val-a",
        "harvest-val-b",
        "screen-impl-a",
        "screen-impl-b",
        "screen-val-a",
        "screen-val-b",
        "extract-impl-a",
        "extract-impl-b",
        "extract-val-a",
        "extract-val-b",
        "synth-impl-a",
        "synth-impl-b",
        "synth-val-a",
        "synth-val-b",
        "prisma-impl-a",
        "prisma-impl-b",
        "prisma-val-a",
        "prisma-val-b",
        "escalation-reviewer"
      ]
    },

    "prog-impl-a": {
      "role": "programs-implementer",
      "model": "openrouter/qwen/qwen3-coder-flash"
    },
    "prog-impl-b": {
      "role": "programs-implementer",
      "model": "openrouter/deepseek/deepseek-v4-flash"
    },
    "prog-val-a": {
      "role": "programs-validator",
      "model": "openrouter/deepseek/deepseek-v4-pro"
    },
    "prog-val-b": {
      "role": "programs-validator",
      "model": "openrouter/z-ai/glm-5.1"
    },

    "infra-impl-a": {
      "role": "infrastructure-implementer",
      "model": "openrouter/qwen/qwen3-coder-flash"
    },
    "infra-impl-b": {
      "role": "infrastructure-implementer",
      "model": "openrouter/deepseek/deepseek-v4-flash"
    },
    "infra-val-a": {
      "role": "infrastructure-validator",
      "model": "openrouter/deepseek/deepseek-v4-pro"
    },
    "infra-val-b": {
      "role": "infrastructure-validator",
      "model": "openrouter/z-ai/glm-5.1"
    },

    "harvest-impl-a": {
      "role": "slr-harvest-implementer",
      "model": "openrouter/deepseek/deepseek-v4-flash"
    },
    "harvest-impl-b": {
      "role": "slr-harvest-implementer",
      "model": "openrouter/qwen/qwen3-coder-flash"
    },
    "harvest-val-a": {
      "role": "slr-harvest-validator",
      "model": "openrouter/deepseek/deepseek-v4-pro"
    },
    "harvest-val-b": {
      "role": "slr-harvest-validator",
      "model": "openrouter/z-ai/glm-5.1"
    },

    "screen-impl-a": {
      "role": "slr-screen-implementer",
      "model": "openrouter/deepseek/deepseek-v4-flash"
    },
    "screen-impl-b": {
      "role": "slr-screen-implementer",
      "model": "openrouter/qwen/qwen3-coder-flash"
    },
    "screen-val-a": {
      "role": "slr-screen-validator",
      "model": "openrouter/deepseek/deepseek-v4-pro"
    },
    "screen-val-b": {
      "role": "slr-screen-validator",
      "model": "openrouter/z-ai/glm-5.1"
    },

    "extract-impl-a": {
      "role": "slr-extract-implementer",
      "model": "openrouter/qwen/qwen3-coder-flash"
    },
    "extract-impl-b": {
      "role": "slr-extract-implementer",
      "model": "openrouter/deepseek/deepseek-v4-flash"
    },
    "extract-val-a": {
      "role": "slr-extract-validator",
      "model": "openrouter/deepseek/deepseek-v4-pro"
    },
    "extract-val-b": {
      "role": "slr-extract-validator",
      "model": "openrouter/z-ai/glm-5.1"
    },

    "synth-impl-a": {
      "role": "slr-synthesis-implementer",
      "model": "openrouter/deepseek/deepseek-v4-flash"
    },
    "synth-impl-b": {
      "role": "slr-synthesis-implementer",
      "model": "openrouter/qwen/qwen3-coder-flash"
    },
    "synth-val-a": {
      "role": "slr-synthesis-validator",
      "model": "openrouter/deepseek/deepseek-v4-pro"
    },
    "synth-val-b": {
      "role": "slr-synthesis-validator",
      "model": "openrouter/z-ai/glm-5.1"
    },

    "prisma-impl-a": {
      "role": "slr-prisma-implementer",
      "model": "openrouter/deepseek/deepseek-v4-flash"
    },
    "prisma-impl-b": {
      "role": "slr-prisma-implementer",
      "model": "openrouter/qwen/qwen3-coder-flash"
    },
    "prisma-val-a": {
      "role": "slr-prisma-validator",
      "model": "openrouter/deepseek/deepseek-v4-pro"
    },
    "prisma-val-b": {
      "role": "slr-prisma-validator",
      "model": "openrouter/z-ai/glm-5.1"
    },

    "escalation-reviewer": {
      "role": "escalation-arbitrator",
      "model": "openrouter/xiaomi/mimo-v2.5-pro",
      "mode": "read-only-review",
      "called_by": [
        "pm"
      ]
    }
  }
}
```

---

## 7. Escalation Reviewer Identity

Create this file:

```txt
.openclaw/agents/escalation-reviewer/agent.md
```

Recommended content:

```md
# ELIS Escalation Reviewer

You are the ELIS escalation reviewer.

Your role is to provide independent arbitration when the PM agent identifies disagreement, failed validation, high-risk changes, repeated failure, or material uncertainty.

You are not a routine implementer. Your normal mode is read-only review.

## Inputs

You may receive:

1. Original task brief.
2. Implementer output.
3. Validator review.
4. Diff or file excerpts.
5. Test results.
6. HANDOFF.md.
7. REVIEW.md.
8. Relevant governance rules.
9. PM escalation reason.

## Decision options

Return exactly one of:

- PASS
- FAIL
- CONDITIONAL PASS
- NEEDS HUMAN DECISION

## Review criteria

Assess:

1. Whether the implementation satisfies the task.
2. Whether the validator’s objections are technically valid.
3. Whether the change preserves deterministic ELIS behaviour.
4. Whether schemas, manifests, CI, release logic, documentation and tests remain consistent.
5. Whether the evidence supports the conclusion.
6. Whether there is hidden risk to reproducibility, auditability, governance, security or maintainability.
7. Whether the task should return to an implementer or proceed to human decision.

## Output format

Return:

1. Verdict.
2. Reasoning summary.
3. Blocking findings.
4. Non-blocking findings.
5. Required changes.
6. Recommended PM decision.
7. Confidence: High, Medium or Low.

## Constraints

Do not implement changes unless explicitly authorised.

Do not approve a change if evidence is missing.

Do not rely on assumptions when the repository, diff, test output or governance document can be checked.

If the issue concerns release governance, CI, schemas, manifests, credentials, reproducibility or auditability, apply a conservative standard.
```

---

## 8. PM Escalation Rule

Add this section to the PM agent identity.

```md
## Escalation Rule

The PM must call `escalation-reviewer` when any of the following occurs:

1. Any validator returns FAIL.
2. Two validators disagree.
3. A validator returns CONDITIONAL PASS on a release-gating task.
4. The task touches schemas, manifests, CI, release logic, security, credentials, auditability, reproducibility or governance documents.
5. The same task fails validation twice.
6. The PM cannot determine whether the implementer or validator is correct.
7. The validator expresses material uncertainty.
8. The expected cost of error exceeds the cost of escalation.

The PM must record the escalation reason in HANDOFF.md, REVIEW.md or the task activity log.

Escalation is not fallback. Fallback is used when a model fails technically. Escalation is used when judgement quality, independence or risk control requires stronger review.
```

---

## 9. Recommended Operating Policy

### 9.1 Normal Task

```txt
PM assigns task
→ implementer edits
→ validator reviews
→ PM closes or returns task
```

### 9.2 High-Risk Task

```txt
PM assigns task
→ implementer edits
→ validator reviews
→ escalation-reviewer arbitrates
→ PM decides
```

### 9.3 Failed Validation

```txt
Validator = FAIL
→ PM sends findings back to implementer
→ implementer fixes
→ validator rechecks
→ if second failure, call escalation-reviewer
```

### 9.4 Validator Conflict

```txt
Validator A = PASS
Validator B = FAIL
→ PM calls escalation-reviewer
→ escalation-reviewer gives arbitration verdict
```

---

## 10. Recommended Human Oversight Rules

The escalation reviewer should return `NEEDS HUMAN DECISION` when:

1. The evidence is incomplete.
2. The repository state cannot be inspected reliably.
3. The validators disagree on a legal, methodological or governance interpretation.
4. The change affects published ELIS methodology.
5. The change could alter the meaning of PRISMA, screening, extraction or synthesis outputs.
6. The change affects secrets, credentials, API keys or deployment security.
7. The model cannot establish deterministic behaviour from the available evidence.

---

## 11. Final Recommended Model List

```txt
PM
- openrouter/deepseek/deepseek-v4-pro
- fallback: openrouter/deepseek/deepseek-v3.2

Implementers
- openrouter/qwen/qwen3-coder-flash
- openrouter/deepseek/deepseek-v4-flash

Validators
- openrouter/deepseek/deepseek-v4-pro
- openrouter/z-ai/glm-5.1

Escalation
- openrouter/xiaomi/mimo-v2.5-pro
```

---

## 12. Benefits of the First-Version Configuration

This configuration is stronger than the current DeepSeek/MiMo mirror setup because it provides:

1. **Lower routine cost** by using Flash/Coder models for implementation.
2. **Better role separation** between implementation and validation.
3. **Higher validator independence** by including GLM-5.1 as a different model family.
4. **Controlled use of expensive MiMo** only for arbitration and high-risk review.
5. **Clear distinction between fallback and escalation.**
6. **Better audit trail** because escalation must be recorded by the PM.
7. **Better ELIS governance alignment** with reproducibility, auditability and deterministic release discipline.

---

## 13. Implementation Notes

Before deploying this configuration:

1. Verify current OpenClaw schema and supported agent registry syntax.
2. Verify model IDs directly in OpenRouter.
3. Confirm whether OpenClaw passes OpenRouter-specific provider routing parameters.
4. Test each model using a preflight workflow.
5. Ensure the PM can call the escalation reviewer explicitly.
6. Ensure the escalation reviewer is read-only by default.
7. Require PM to record the escalation reason in `HANDOFF.md`, `REVIEW.md`, or equivalent task logs.

---

## 14. Preflight Test

Run a preflight task for each configured agent:

```txt
Task: Return your agent name, model ID, role, and whether you are an implementer, validator, PM or escalation reviewer. Do not edit files.
```

Expected result:

1. Every agent returns the correct role.
2. No agent uses an unapproved model.
3. PM can call implementers.
4. PM can call validators.
5. PM can call escalation-reviewer.
6. Escalation reviewer remains read-only unless explicitly authorised.

---

## 15. Next Step

Create a small OpenClaw configuration test branch:

```txt
feature/openclaw-agent-settings-v1
```

Then add:

```txt
.openclaw/agents/pm/agent.md
.openclaw/agents/escalation-reviewer/agent.md
.openclaw/agents/prog-impl-a/agent.md
.openclaw/agents/prog-val-a/agent.md
.openclaw/agents/infra-impl-a/agent.md
.openclaw/agents/infra-val-a/agent.md
```

After that, run a preflight validation before deploying the full matrix.
