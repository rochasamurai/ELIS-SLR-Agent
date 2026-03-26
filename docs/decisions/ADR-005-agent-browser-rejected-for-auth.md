# ADR-005: Agent Browser Rejected for Auth

**Status:** Accepted
**Date:** 2026-03-26
**Deciders:** PM (Carlo Rocha), CODEX, Claude Code

## Context

The ELIS SLR Agent performs web harvesting from academic databases (Crossref,
OpenAlex, Scopus, and others). Some sources require authenticated access:
Scopus API keys, institutional proxies, or session cookies obtained from
browser-based login flows.

One proposal was to use an agent-controlled browser (Playwright or similar) to
perform interactive login and extract session cookies, which would then be
injected into the harvest pipeline. This would allow the agent to access
paywalled content without requiring a static API key per source.

## Decision

An agent-controlled browser is **not used for authentication**. All
source-level authentication is handled through static API keys, subscription
tokens, or pre-authenticated environment variables configured by the operator.

The agent-browser capability (Playwright-based web harvest) is reserved for
**content retrieval only** — specifically, scraping public pages that do not
require login.

## Consequences

### Positive
- No dependency on interactive browser sessions, which are fragile (session
  expiry, CAPTCHA, DOM changes).
- Authentication state is fully operator-controlled and auditable; no credentials
  are extracted or stored by the agent at runtime.
- Simpler pipeline: API key in environment variable → authenticated request,
  with no browser lifecycle to manage.
- Reduces attack surface: agent cannot be manipulated into leaking session
  tokens extracted from a live browser session.

### Negative / trade-offs
- Sources without a public API (only browser-accessible) cannot be harvested
  through the authenticated path.
- Operator must manage static keys for each source; there is no automated
  credential refresh.

## Alternatives considered

### Alternative A — Browser-based login to extract session cookies

Use Playwright to drive an interactive login flow for each gated source, extract
the session cookie, and inject it into HTTP requests made by the harvest pipeline.

Discarded because:
- Session cookies expire, requiring re-login at unpredictable intervals.
- Many academic databases use CAPTCHA or two-factor authentication that an
  automated browser cannot complete.
- Storing extracted session cookies in the agent environment introduces
  credential-leakage risk.
- Institutional IP restrictions mean that a session from one network cannot be
  reused from another.

### Alternative B — Proxy through an institutional access server

Route all harvest requests through a proxy that already has institutional
credentials, avoiding the need for API keys.

Discarded for the current implementation because the ELIS runtime environment
(`elis-server`) is a VPS without institutional network access. If the project
ever moves to an institutional server, this alternative could be revisited.

## Evidence / references

- `ELIS_2Agent_Automation_Plan_v2_0.md` §Phase C — auth strategy using
  subscription tokens rather than browser-extracted credentials
- `elis/adapters/` — Crossref, OpenAlex, Scopus adapters use static API keys
  from environment variables; no browser auth path exists in the codebase
