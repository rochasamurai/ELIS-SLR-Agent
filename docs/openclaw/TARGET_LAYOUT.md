# OpenClaw Target Layout on `elis-server`

> Target date: 2026-03-22
> Scope: native OpenClaw runtime, canonical repo placement, workspace layout, and PM Agent access rules

---

## 1. Recommended Architecture

ELIS should use:

- one canonical platform repo for governance, application code, infrastructure code, and OpenClaw definitions
- multiple narrowly scoped OpenClaw workspaces separated by domain and role
- separate SLR project repositories or data directories for review artifacts
- one PM workspace with read access across all ELIS repos and workspaces

This is the preferred architecture over "one repo and one workspace per agent group" because:

- governance needs a single source of truth (`CURRENT_PE.md`, plans, audits, release history)
- implementers and validators need different rules and write surfaces
- SLR research artifacts should be isolated from platform/runtime config
- PM needs visibility across the whole system, but worker agents should keep least-privilege scope

---

## 2. Canonical Paths on `elis-server`

### 2.1 Platform repo

Canonical ELIS platform repo:

```text
/opt/elis/repo
```

This repo is the source of truth for:

- `CURRENT_PE.md`
- implementation plans
- governance docs
- application code
- infrastructure code
- `openclaw/` workspace definitions and sanitized runtime config

Recommended branch policy:

- checked-out branch on host: `main`
- feature branches live in GitHub and in disposable worktrees when needed
- PM Agent reads from `main` unless a PE explicitly requires branch-aware inspection

### 2.2 OpenClaw runtime state

Native OpenClaw runtime state:

```text
/home/samurai/.openclaw
```

This state directory holds:

- live `openclaw.json`
- channel bindings
- session state
- approvals
- logs and runtime metadata

It is operational state, not the audit source of truth.

### 2.3 OpenClaw workspaces root

Canonical host workspace root:

```text
/home/samurai/openclaw
```

Each workspace is a host directory under this root. The legacy path:

```text
/home/samurai/workspace-pm
```

may exist only as a compatibility symlink to:

```text
/home/samurai/openclaw/workspace-pm
```

No other duplicate workspace trees should exist.

### 2.4 SLR project storage

SLR review content should not live inside the platform repo by default. Use one of:

```text
/opt/elis/projects/<review-id>
/opt/elis/projects/<review-id>.git
```

Each review/project area should hold:

- search exports
- screening decisions
- extraction sheets
- synthesis notes
- PRISMA outputs

This keeps research data separate from platform code and OpenClaw runtime state.

---

## 3. Workspace Layout

### 3.1 PM workspace

```text
/home/samurai/openclaw/workspace-pm
```

Purpose:

- orchestrate PEs
- read governance state
- report status to PO
- trigger and monitor gates

Contents:

- `SOUL.md`
- `AGENTS.md`
- `IDENTITY.md`
- `USER.md`
- `MEMORY.md`
- `memory/`
- `docs/` for stable reference links when needed

Best practice:

- prefer symlinks for canonical governance files instead of copied mirrors
- `CURRENT_PE.md` should resolve to `/opt/elis/repo/CURRENT_PE.md`
- plan references should resolve to files in `/opt/elis/repo`

### 3.2 Infrastructure workspaces

```text
/home/samurai/openclaw/workspace-infra-impl
/home/samurai/openclaw/workspace-infra-val
```

Purpose:

- infrastructure implementers: deployment, service management, CI/CD, host automation, OpenClaw config
- infrastructure validators: infra review, adversarial validation, security checks

### 3.3 Software workspaces

```text
/home/samurai/openclaw/workspace-prog-impl
/home/samurai/openclaw/workspace-prog-val
```

Purpose:

- application/code implementers: Python, CLI, adapters, tests
- application validators: code review and validation only

### 3.4 SLR workspaces

Recommended phase-specific layout:

```text
/home/samurai/openclaw/workspace-slr-harvest
/home/samurai/openclaw/workspace-slr-screen
/home/samurai/openclaw/workspace-slr-extract
/home/samurai/openclaw/workspace-slr-synth
/home/samurai/openclaw/workspace-slr-prisma
```

Purpose:

- isolate instructions and quality criteria by SLR phase
- reduce cross-phase rule contamination

These workspaces should reference active SLR project directories under `/opt/elis/projects/`.

---

## 4. Repo Strategy

### 4.1 Platform repo

Keep one platform repo:

```text
/opt/elis/repo
```

Do not split infrastructure and software into separate top-level repos unless there is a strong operational reason. ELIS governance currently depends on one authoritative:

- `CURRENT_PE.md`
- base branch
- plan file chain
- audit trail
- PR workflow

Splitting platform code into multiple repos would complicate:

- PE assignment
- alternation history
- validator routing
- release auditing
- PM status reporting

### 4.2 SLR project repos

Use separate repos or data stores per review when research output needs its own lifecycle.

Recommended pattern:

```text
/opt/elis/projects/<review-id>
```

Optional Git-backed pattern:

```text
/opt/elis/projects/<review-id>/.git
```

Use these when:

- the review has its own provenance and publication timeline
- multiple reviews run concurrently
- data retention and export requirements differ from platform code

---

## 5. PM Agent Access Rules

### 5.1 PM visibility model

The PM Agent should be the only agent with read access across all ELIS control surfaces:

- platform repo at `/opt/elis/repo`
- OpenClaw workspaces under `/home/samurai/openclaw`
- SLR project directories under `/opt/elis/projects`
- GitHub PR/issue metadata through `gh`
- OpenClaw health/config/status commands

This is required for accurate orchestration.

### 5.2 PM write model

PM write access should stay narrow.

Auto-approved writes:

- none by default

Approval-gated writes:

- update runtime-safe PM workspace files when explicitly intended
- `git -C /opt/elis/repo commit`
- `git -C /opt/elis/repo push`
- `gh pr comment`
- `gh pr edit`
- `openclaw config set ...`
- `systemctl --user restart openclaw-gateway`

Blocked:

- secret reads
- environment dumps
- destructive filesystem commands
- package install/remove commands
- permission/ownership changes

### 5.3 PM read allowlist

Recommended read allowlist categories:

```text
cat /opt/elis/repo/CURRENT_PE.md
cat /opt/elis/repo/AGENTS.md
cat /opt/elis/repo/ELIS_MultiAgent_Implementation_Plan_*.md
git -C /opt/elis/repo status *
git -C /opt/elis/repo log *
git -C /opt/elis/repo diff *
gh pr list *
gh pr view *
gh issue list *
openclaw doctor*
openclaw channels status*
openclaw config get*
openclaw approvals get*
ls /home/samurai/openclaw/*
cat /home/samurai/openclaw/workspace-pm/*
cat /home/samurai/openclaw/workspace-*/AGENTS.md
ls /opt/elis/projects/*
cat /opt/elis/projects/*/manifest.*
```

Use the smallest safe pattern that still lets PM operate without manual babysitting.

### 5.4 PM best-practice constraints

The PM Agent should:

- read canonical files directly from `/opt/elis/repo`
- avoid relying on copied governance files that can drift stale
- use workspace-local identity files only for PM identity and session behavior
- never require full shell access to answer routine status questions
- remain read-mostly, with elevated actions explicitly gated

### 5.5 PM model contingency

Recommended PM model policy:

- primary: `openrouter/deepseek/deepseek-v4-pro`
- contingency: `openrouter/deepseek/deepseek-v3.2`

Best-practice rule:

- do not enable automatic fallback unless the installed OpenClaw build is verified to scope fallback safely for PM
- until that is proven, treat `deepseek-v3.2` as a manual operator failover for PM only
- record the switch as degraded mode in the operational log or handoff

---

## 6. Worker Agent Access Model

### 6.1 Infrastructure agents

Read:

- `/opt/elis/repo`
- infra workspace
- relevant deployment docs

Write:

- platform repo files within assigned PE scope
- infra workspace artifacts if the PE requires them

Do not grant default read access to SLR project data.

### 6.2 Software agents

Read:

- `/opt/elis/repo`
- program workspace
- interface/config docs needed for integration

Write:

- application code and tests within PE scope

Do not grant default write access to infra runtime state or SLR project data.

### 6.3 SLR agents

Read:

- SLR phase workspace
- assigned project directory under `/opt/elis/projects/<review-id>`
- protocol/guideline files required for the review

Write:

- only the assigned SLR project directory and approved result artifacts

Do not grant default write access to `/opt/elis/repo` or OpenClaw runtime config.

---

## 7. Native Runtime Rules

Target runtime is native systemd, not Docker.

Service:

```text
~/.config/systemd/user/openclaw-gateway.service
```

Operational commands:

```bash
systemctl --user status openclaw-gateway
systemctl --user restart openclaw-gateway
journalctl --user -u openclaw-gateway -n 100
openclaw doctor
openclaw channels status --probe
```

`docker-compose.yml` may remain in the repo only as a historical migration artifact. It is not the production runtime contract for `elis-server`.

---

## 8. Recommended End State

The preferred end state on `elis-server` is:

```text
/opt/elis/repo
/opt/elis/projects/<review-id>...
/home/samurai/.openclaw
/home/samurai/openclaw/workspace-pm
/home/samurai/openclaw/workspace-prog-impl
/home/samurai/openclaw/workspace-prog-val
/home/samurai/openclaw/workspace-infra-impl
/home/samurai/openclaw/workspace-infra-val
/home/samurai/openclaw/workspace-slr-harvest
/home/samurai/openclaw/workspace-slr-screen
/home/samurai/openclaw/workspace-slr-extract
/home/samurai/openclaw/workspace-slr-synth
/home/samurai/openclaw/workspace-slr-prisma
```

Architecture summary:

- one platform repo
- many least-privilege workspaces
- separate SLR project stores
- PM read-all, write-narrow

That is the architecture recommended for ELIS.
