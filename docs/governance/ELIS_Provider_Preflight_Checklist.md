# ELIS Provider Preflight Checklist

**Status:** Canonical — v1.0  
**Date:** 2026-05-03  
**Owner:** Carlos Rocha, Product Owner  
**Applies to:** ELIS PM (at dispatch), Implementers and Validators (Step 0), Platform Monitor (diagnosis)  
**Authoritative sources:** ELIS_General_Guidance.md §10, AGENTS.md, LESSONS_LEARNED.md  
**Canonical record:** GitHub (this document)

---

## 1. Purpose

Before any PE execution, PM and agents must verify that the required AI providers and models are available, authenticated, and within rate limits. This prevents mid-execution failures from provider unavailability, expired tokens, quota exhaustion, or silent fallback.

---

## 2. Pre-Dispatch Provider Checks (PM)

### 2.1 Gateway Health

- [ ] OpenClaw gateway is running: `openclaw gateway status`
- [ ] Gateway start time is recent (not stuck since a previous crash)
- [ ] Discord connection is active (channels show `enabled`, `configured`, `running`)
- [ ] Telegram connection is active (if used)

### 2.2 Provider Authentication

- [ ] Required providers are registered in OpenClaw config
- [ ] API keys/tokens are set in environment or config
- [ ] No expired tokens (check last rotation date)
- [ ] If Codex OAuth: oauth token exists and is valid
- [ ] If Claude Code: setup token or API key is configured
- [ ] If Gemini CLI: authentication is configured
- [ ] Secrets isolation rule: never print, log, or include secret values in any output. Use existence checks only:
  ```bash
  # Safe — checks existence, does not print value
  [ -n "$VAR" ] && echo "set" || echo "unset"
  ```

### 2.3 Model Availability

- [ ] Default model responds: send a minimal test request
- [ ] Fallback models are available if primary is limited
- [ ] Model version matches the PE requirements

### 2.4 Rate-Limit Status

- [ ] No active 429 (usage-limit) errors in recent session logs
- [ ] Rate-limit headers indicate available quota
- [ ] If recent 429 observed: wait for cooldown before dispatch
- [ ] For long tasks: warn before starting
- [ ] For multi-step operational tasks: prefer fresh sessions
- [ ] Recommended session handoff above approximately 35K context tokens
- [ ] Stop on 429 usage-limit instead of repeated retries
- [ ] Do not enable fallback providers without PO approval

---

## 3. Provider Preflight for Codex CLI

### 3.1 OAuth Token Verification
```bash
# Check token presence (existence only — never print value)
# Assumes token file in standard location
[ -f "$CODEX_TOKEN_FILE" ] && echo "token file: present" || echo "token file: missing"
```

### 3.2 Known Failure Patterns
- `HTTP 429: The usage limit has been reached` — provider=openai-codex, model=gpt-5.5
- Codex CLI v0.118.0 headless invocation bug (PE-RUNNER-01 fixed this)
- `401 Unauthorized` — expired or revoked token

### 3.3 Recovery
- Token rotation requires: update env, container restart, `channels add`, second restart
- Rate-limit cooldown: wait before retry; do not retry 429 immediately
- Record rate-limit events as operational evidence

---

## 4. Provider Preflight for Claude Code

### 4.1 Authentication Verification
```bash
# Check API key presence (existence only — never print value)
[ -n "$ANTHROPIC_API_KEY" ] && echo "ANTHROPIC_API_KEY: set" || echo "ANTHROPIC_API_KEY: unset"
```

### 4.2 Known Failure Patterns
- OpenRouter API key missing from systemd user service environment (historic failure)
- Model unavailability (check `api.openrouter.ai/models` status)

### 4.3 Recovery
- Missing key: update systemd user service environment, restart OpenClaw
- Model failure: verify model ID, try fallback; record as operational evidence

---

## 5. Agent Step 0 Provider Checks

Before starting implementation or validation:

- [ ] OpenClaw gateway is reachable
- [ ] Model responds to a test prompt
- [ ] Rate-limit check: no recent 429 errors in session context
- [ ] If token estimate unavailable, use conservative behaviour
- [ ] Record provider readiness evidence in Status Packet:
  ```text
  Provider readiness:
  - Gateway: <status>
  - Model: <available/unavailable>
  - Rate limit: <ok/near-limit/429-active>
  ```

---

## 6. Platform Monitor Provider Checks

When Platform Monitor diagnoses provider failures:

- [ ] Check OpenClaw gateway logs for provider errors
- [ ] Verify credential files exist (do not read their contents)
- [ ] Check environment variable presence for each required provider
- [ ] Test provider connectivity with a minimal API call
- [ ] Check last provider rotation date (if applicable)
- [ ] Check systemd service environment for missing vars
- [ ] Check Docker container environment for secrets coverage
- [ ] Rule: `docker exec printenv` must never be used (prints secret values)

---

## 7. Provider Change Protocol

All provider configuration changes require PO approval:

1. PO approves the change.
2. Platform Monitor (Hermes) executes the change.
3. Verify change:
   - Token presence in correct location (existence check only)
   - Channel binding works (`channels status` shows `token:config`)
   - Test message delivery
4. Record change in LESSONS_LEARNED.md if a pattern emerges.
5. Rotate tokens in advance of expiry; do not wait for revoked-token failure.

---

## 8. Version History

| Version | Date       | Author | Changes |
|---------|------------|--------|---------|
| 1.0     | 2026-05-03 | PM     | Initial canonical consolidation from ELIS_General_Guidance.md §10, LESSONS_LEARNED.md. |
