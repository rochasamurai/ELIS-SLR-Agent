# ELIS SLR AI VPS — Implementation & Validation Plan

**Project:** ELIS SLR AI Platform — VPS Migration with OpenClaw + Docker  
**Model:** 2-Agent Dev (CODEX + Claude Code)  
**Version:** v1.0 — 2026-03-02  
**Author:** rochasamurai × Claude (Anthropic)  
**Status:** Planning

---

## Overview

This plan covers the migration and hosting of the ELIS SLR AI Platform on a VPS, running **OpenClaw + Docker**, with Discord as the primary interface. It follows the structured **PE (Plan Episode)** model established in `ELIS_MultiAgent_Implementation_Plan.md` and extends the 2-Agent dev pattern (CODEX for architecture/scaffolding, Claude Code for implementation/validation).

Each PE is a discrete, auditable unit of work with a clear owner, deliverable, and validation gate.

---

## Discord vs. Telegram: Platform Recommendation

**Recommendation: Discord ✅**

Based on the velvet-shark/OpenClaw 50-day workflow review and ELIS operational needs, Discord is the superior interface for the following reasons:

| Criterion | Discord | Telegram |
|---|---|---|
| Channel isolation per workflow | ✅ Native (channels per context) | ❌ Groups blur contexts |
| Model routing per channel | ✅ Supported in OpenClaw config | ❌ Not natively supported |
| Dev/monitoring separation | ✅ `#monitoring`, `#research`, `#briefing` | ❌ Requires bots + workarounds |
| Webhook & bot ecosystem | ✅ Rich, well-documented | ⚠️ Functional but limited |
| Cron job reporting | ✅ Clean channel-targeted delivery | ⚠️ Clutters main chats |
| Multi-agent coordination visibility | ✅ Each agent can target specific channel | ❌ Noisy in flat structure |
| Prompt injection risk surface | ✅ Lower (controlled server membership) | ⚠️ Higher (open groups) |
| Mobile UX for review/approval gates | ✅ Excellent | ✅ Excellent |

**Claude's note:** Telegram is fine for personal use, but for a research platform like ELIS — where you need audit trails, workflow separation, and multi-agent coordination reporting — Discord's server/channel architecture maps directly to your PE model. The ability to route model tiers (Opus for deep SLR screening, Haiku for validation summaries) per channel is a significant operational advantage.

---

## Architecture Overview

```
VPS (Ubuntu 24 LTS)
├── OpenClaw Gateway (Docker container)
│   ├── Discord Bot (primary interface)
│   ├── MCP Servers (GitHub, Gmail, GCal)
│   └── Secrets via Docker secrets / .env (not committed)
├── ELIS SLR Agent (Docker container)
│   ├── elis CLI (harvest, merge, dedup, screen, validate)
│   ├── /runs/<run_id>/ (authoritative output)
│   └── /json_jsonl/ (compatibility export)
├── Postgres (Docker container — metadata & audit logs)
├── Nginx reverse proxy (HTTPS termination)
└── GitHub Actions CI (remote — schema/validator enforcement)
```

**2-Agent Dev Model:**
- **CODEX** → Architects, scaffolds, writes infrastructure configs (docker-compose, nginx, env templates), reviews schemas
- **Claude Code** → Implements, validates, runs tests, writes REVIEW_PE files, enforces Data Contract

---

## PE Structure

Each PE follows the ELIS convention:
1. **Objective** — what this episode accomplishes
2. **Agent Owner** — CODEX or Claude Code (or both, with handoff point)
3. **Tasks** — ordered, auditable steps
4. **Validation Gate** — pass/fail criteria before next PE begins
5. **Artifacts** — files committed to repo
6. **Claude's Recommendations** — observations and risk flags

---

## PE-VPS-00: VPS Baseline Provisioning

**Objective:** Provision a clean VPS, apply security hardening, and validate the host environment before any application layer is deployed.

**Agent Owner:** CODEX (architecture) → Claude Code (validation)

**Tasks:**
1. Select VPS provider. Recommended: Hetzner CX21 (2 vCPU, 4GB RAM, 40GB NVMe) or DigitalOcean Droplet (equivalent). Choose EU region if ELIS handles electoral data with GDPR implications.
2. Provision Ubuntu 24 LTS. Enable UFW: allow SSH (22), HTTP (80), HTTPS (443). Block all else.
3. Create non-root deploy user `elis`. Add SSH key. Disable password auth and root SSH.
4. Install Docker Engine (not Docker Desktop) and Docker Compose v2.
5. Configure Tailscale for private network access. Expose nothing on public IP except 80/443.
6. Set timezone (`Europe/Lisbon` or operator TZ), enable unattended-upgrades for security patches.
7. Create `/opt/elis/` as project root with subdirectories: `config/`, `secrets/`, `data/`, `logs/`.
8. Apply `fail2ban` with SSH jail.

**Validation Gate:**
- `docker info` returns clean output as `elis` user
- UFW rules confirmed: only 22/80/443 open on public interface
- Tailscale node visible in tailnet
- `fail2ban-client status sshd` shows active jail

**Artifacts:** `docs/_active/VPS_BASELINE.md`, updated `CHANGELOG.md`

**Claude's Recommendations:**
- Do NOT expose the OpenClaw gateway port (default 3000) on the public internet. Proxy through Nginx with auth, or keep Tailscale-only. The velvet-shark guide explicitly recommends "Tailscale everything."
- Budget note: Hetzner CX21 at ~€4.51/month is sufficient for ELIS v2.0 workloads. Upgrade to CX31 (4 vCPU, 8GB) if you add the ASTA enrichment pipeline concurrently.
- Enable automatic security upgrades (`unattended-upgrades`) from day one. Don't defer this.

---

## PE-VPS-01: Secrets & Environment Management (OpenClaw New Release)

**Objective:** Implement the OpenClaw secrets management improvements in the VPS environment. Ensure zero secrets in git history.

**Agent Owner:** CODEX (schema design) → Claude Code (implementation + audit)

**Tasks:**
1. Review OpenClaw's new release secrets management documentation. Identify which secrets are now managed by the gateway vs. requiring manual env injection.
2. Create `/opt/elis/secrets/` as a Docker secrets volume (not bind-mounted from repo).
3. Define `.env.example` template (already exists in repo — audit and extend for VPS context):
   - `ANTHROPIC_API_KEY`
   - `DISCORD_BOT_TOKEN`
   - `GITHUB_TOKEN` (for backup automation)
   - `ELIS_DB_PASSWORD`
   - Any new OpenClaw secrets from new release
4. Configure OpenClaw gateway to consume secrets from Docker secrets or environment injection (not from config files in repo).
5. Run `git log --all --full-history -- "**/*.env"` and `truffleHog` scan on repo to confirm no historical secret leakage.
6. Update `.gitignore` and `.claudeignore` to block `.env`, `secrets/`, `*.key`, `*.pem`.
7. Document secret rotation procedure in `docs/_active/SECRETS_ROTATION.md`.

**Validation Gate:**
- `truffleHog filesystem --directory /opt/elis` returns zero findings
- No `.env` files present in Docker image layers (`docker history` inspection)
- OpenClaw gateway starts successfully reading secrets from Docker secrets volume
- `git status` in repo shows no untracked secret files

**Artifacts:** Updated `.env.example`, `docs/_active/SECRETS_ROTATION.md`, `REVIEW_PE_VPS_01.md`

**Claude's Recommendations:**
- The velvet-shark backup script (workflow #3) already includes a pre-backup secret scan with placeholder substitution. Adopt this pattern verbatim for the nightly GitHub backup job.
- Treat the OpenClaw `SOUL.md` and `MEMORY.md` as sensitive — they may contain operational context that reveals system architecture. Include them in the backup secret scan.
- Consider using `sops` (Mozilla) or `age` for at-rest encryption of secret files on VPS disk, especially if the provider doesn't offer encrypted volumes by default.
- **Risk flag:** OpenClaw's new release may change the format of the gateway config file. Validate that existing ELIS `config/` files are compatible before deploying. Pin the OpenClaw version in `docker-compose.yml`.

---

## PE-VPS-02: Docker Compose Stack Deployment

**Objective:** Deploy the full ELIS + OpenClaw stack as a Docker Compose service, with health checks and restart policies.

**Agent Owner:** CODEX (compose file) → Claude Code (deploy + validate)

**Tasks:**
1. Author `docker-compose.yml` (or extend existing) with services:
   - `openclaw-gateway` — OpenClaw image, pinned version, Discord bot token injected
   - `elis-agent` — ELIS SLR Agent image built from repo `Dockerfile`
   - `postgres` — Postgres 16-alpine, persistent volume, non-default port
   - `nginx` — Reverse proxy with Let's Encrypt (use `nginx-proxy` + `acme-companion` pattern)
2. Define named volumes: `elis-data`, `postgres-data`, `openclaw-state`
3. Set `restart: unless-stopped` on all services. Set health checks on `openclaw-gateway` and `postgres`.
4. Configure Nginx to:
   - Proxy `/` to OpenClaw gateway (internal only, or Tailscale IP)
   - Redirect HTTP → HTTPS
   - Set security headers (`X-Frame-Options`, `Content-Security-Policy`, etc.)
5. Run `docker compose up -d` and verify all containers reach `healthy` status.
6. Test Discord bot responds in `#monitoring` channel.
7. Run `elis --help` inside `elis-agent` container.

**Validation Gate:**
- `docker compose ps` shows all services as `running (healthy)`
- Discord bot acknowledges in `#monitoring`: "ELIS VPS stack online"
- `elis validate schemas/row.schema.json data/benchmark/` passes inside container
- Nginx returns 200 on health endpoint with valid TLS cert (Let's Encrypt)

**Artifacts:** `docker-compose.yml` (updated), `nginx/default.conf`, `REVIEW_PE_VPS_02.md`

**Claude's Recommendations:**
- Do not use `docker-compose.yml` bind mounts for `runs/` output directory in production — use named volumes and expose outputs via `elis export-latest`. This prevents permission drift.
- Set `POSTGRES_PASSWORD` via Docker secret, not environment variable in compose file.
- Use a `healthcheck` on the OpenClaw gateway container that pings the internal API endpoint (e.g., `GET /health`) rather than just checking if the process is running. This catches silent failures.
- Pin OpenClaw image tag. Never use `:latest` in production. Record the pinned version in `CHANGELOG.md` as part of this PE.

---

## PE-VPS-03: Discord Channel Architecture & Model Routing

**Objective:** Configure Discord server and OpenClaw channel routing to support ELIS workflows with appropriate model tiers.

**Agent Owner:** Claude Code (configuration + documentation)

**Tasks:**
1. Create/configure Discord server with ELIS-specific channels:
   - `#monitoring` — server health, cron reports, Docker alerts
   - `#elis-harvest` — harvest job triggers and output
   - `#elis-screen` — screening results, validation flags
   - `#elis-research` — deep SLR research queries (Opus)
   - `#briefing` — daily ELIS run summaries (Sonnet)
   - `#dev` — CODEX + Claude Code coordination, PR links, PE reviews
2. Configure OpenClaw model routing per channel (in gateway config):
   - `#elis-research`, `#elis-screen` → `claude-opus-4` (complex reasoning)
   - `#elis-harvest`, `#briefing`, `#monitoring` → `claude-sonnet-4-6` (balanced)
   - `#dev` (scaffolding tasks, quick checks) → `claude-haiku-4-5` (fast, cheap)
3. Configure channel-isolated contexts (no bleed between `#elis-research` and `#monitoring`).
4. Test each channel with a typed trigger and verify model routing in OpenClaw logs.
5. Document channel purpose and model assignment in `docs/_active/DISCORD_ARCHITECTURE.md`.

**Validation Gate:**
- Each channel responds with correct model identifier in debug output
- No context bleed confirmed by cross-channel test: query in `#elis-harvest` does not appear in `#elis-research` context
- `#monitoring` receives automated "stack healthy" ping from cron

**Artifacts:** `docs/_active/DISCORD_ARCHITECTURE.md`, OpenClaw gateway config snippet, `REVIEW_PE_VPS_03.md`

**Claude's Recommendations:**
- Follow the velvet-shark channel architecture from workflow #15 as your baseline. It is validated across 50+ days of real use.
- Use Opus **only** for `#elis-research` and full SLR screening tasks. ELIS data validation and harvest tasks are Sonnet or Haiku work. This directly reduces API costs.
- Create a `#dev` channel explicitly for the 2-Agent coordination loop. CODEX should report scaffolding completions here; Claude Code should post validation results here. This creates a natural audit trail aligned with your `REVIEW_PE_*.md` pattern.
- **Cost note:** With Opus at ~$15/MTok input, reserve it for tasks that require multi-hop reasoning (screening relevance, synthesis). A single SLR harvest + dedup cycle does not need Opus.

---

## PE-VPS-04: ELIS CLI Integration & Smoke Tests

**Objective:** Validate that the full ELIS v2.0 CLI pipeline runs correctly inside the VPS Docker environment.

**Agent Owner:** Claude Code

**Tasks:**
1. Pull `release/2.0` branch inside `elis-agent` container.
2. Run full pipeline smoke test with benchmark dataset (`data/benchmark/`):
   ```
   elis harvest openalex --search-config config/search_config.yaml
   elis merge --inputs runs/<run_id>/harvest_openalex.json
   elis dedup --input runs/<run_id>/appendix_a.json
   elis screen --input runs/<run_id>/appendix_a_deduped.json
   elis validate schemas/row.schema.json runs/<run_id>/appendix_b.json
   elis export-latest --run-id <run_id>
   ```
3. Verify `runs/<run_id>/` structure is authoritative and `json_jsonl/` export matches.
4. Run `pytest tests/` inside container. All tests must pass.
5. Verify GitHub Actions CI (`/.github/workflows/`) triggers correctly on push from VPS environment.
6. Post smoke test results to `#monitoring` Discord channel via OpenClaw.

**Validation Gate:**
- Full pipeline completes without errors on benchmark dataset
- `elis validate` passes on all stage outputs
- `pytest tests/` → 0 failures
- GitHub Actions CI green on test push

**Artifacts:** `docs/_active/VPS_SMOKE_TEST_RESULTS.md`, `REVIEW_PE_VPS_04.md`

**Claude's Recommendations:**
- Run smoke tests against `data/benchmark/` only — never against live API endpoints during validation. Mock harvests where possible.
- Add a VPS-specific smoke test script (`scripts/vps_smoke_test.sh`) that wraps the full pipeline and can be triggered from `#elis-harvest` via OpenClaw. This becomes your "is the platform healthy?" one-click check.
- Validate that the Data Contract v1.0 frozen schema is respected inside the container. The schema must not drift between local development and VPS environment.

---

## PE-VPS-05: Automation & Cron Scheduling

**Objective:** Configure cron-driven ELIS workflows via OpenClaw, including maintenance, backup, and monitoring jobs.

**Agent Owner:** CODEX (cron design) → Claude Code (implementation)

**Tasks:**
1. Define cron schedule for ELIS operational jobs:
   - `04:00` — OpenClaw self-update (as in velvet-shark workflow #3)
   - `04:30` — Full backup to private GitHub repo (with secret scan + placeholder substitution)
   - `04:45` — Docker image pull check (detect new pinned version if available)
   - `07:00` — Daily ELIS briefing to `#briefing` (run summary, pending tasks, schema validation status)
   - `*/30 07:00-23:00` — Health check: Docker service status → `#monitoring`
2. Implement OpenClaw secret scan in backup job (adapt velvet-shark workflow #3 backup prompt).
3. Configure cron definitions in OpenClaw gateway config.
4. Test each cron job by manual trigger before enabling schedule.
5. Document cron schedule in `docs/_active/CRON_SCHEDULE.md`.

**Validation Gate:**
- All cron jobs trigger successfully on manual run
- `#monitoring` receives heartbeat pings
- Backup job pushes to GitHub with no raw secrets (verify with `truffleHog` on backup commit)
- Update job reports version in `#monitoring`

**Artifacts:** `docs/_active/CRON_SCHEDULE.md`, OpenClaw cron config, `REVIEW_PE_VPS_05.md`

**Claude's Recommendations:**
- Adapt the velvet-shark backup prompt (workflow #3) with minimal changes — it is production-tested. The key addition for ELIS is to include `schemas/`, `config/`, and `runs/<latest_run_id>/` manifest files in the backup scope.
- Set cron jobs to run between 04:00–05:00 UTC to avoid competing with any live SLR harvest jobs.
- Add a `#monitoring` alert if the backup job fails. Silent backup failure is the most common VPS operational risk.
- **2-Agent note:** CODEX should define the cron schedule and job parameters. Claude Code should implement and validate each job before it goes live. Write a `REVIEW_PE_VPS_05.md` with pass/fail per job.

---

## PE-VPS-06: Security Hardening & Audit

**Objective:** Apply final security layer across the full VPS + OpenClaw + Docker stack. Validate against OpenClaw security documentation.

**Agent Owner:** Claude Code

**Tasks:**
1. Run the OpenClaw security audit (reference the `docs.openclaw.ai/gateway/security` page). Verify all recommendations are implemented.
2. Apply email/external content prompt injection protection (velvet-shark rule: "Treat external content as hostile").
3. Confirm draft-only mode for any email integration. ELIS does not currently use email workflows — document this as a deliberate constraint.
4. Run `docker scout cves` or `trivy image` on all Docker images. Remediate any HIGH or CRITICAL CVEs.
5. Verify least-privilege: OpenClaw gateway user inside container is non-root.
6. Confirm Nginx security headers pass: `securityheaders.com` scan or equivalent.
7. Review `.claudeignore` and `.agentignore` — ensure VPS-specific paths are excluded from agent context.
8. Write `REVIEW_PE_VPS_06.md` with findings and remediations.

**Validation Gate:**
- `trivy image` → zero HIGH/CRITICAL CVEs on all images
- OpenClaw security check → all items green
- Nginx security headers → grade A or higher
- No root-running containers (`docker ps` + `docker inspect` audit)
- `.claudeignore` excludes `secrets/`, `/opt/elis/config/*.env`, `logs/`

**Artifacts:** `REVIEW_PE_VPS_06.md`, updated `.claudeignore`, `AUDITS.md` entry

**Claude's Recommendations:**
- This PE must not be skipped or abbreviated. Security hardening is a one-time cost with ongoing payoff.
- The OpenClaw new release focuses on secrets management — make sure this PE validates that the new release's security improvements are actually active and not just installed.
- Add a recurring monthly cron job at `05:30` on the 1st of each month that re-runs the security audit and posts a summary to `#monitoring`. Treat this as a living audit, not a one-time check.
- Document all deferred items (items you know about but choose to accept) in `AUDITS.md` with a rationale. This is consistent with the ELIS audit policy.

---

## PE-VPS-07: HANDOFF & Documentation

**Objective:** Produce complete operational documentation and HANDOFF file for the VPS environment. Close the PE cycle.

**Agent Owner:** Claude Code (documentation) → CODEX (review)

**Tasks:**
1. Update `HANDOFF.md` with VPS-specific operational runbook:
   - How to restart services
   - How to trigger manual pipeline run
   - How to rotate secrets
   - How to restore from GitHub backup
2. Update `README.md` with VPS deployment instructions.
3. Update `CHANGELOG.md` with all PE-VPS-00 through PE-VPS-06 entries.
4. Archive any deprecated local-only scripts to `scripts/_archive/` with explanatory note.
5. Create `docs/_active/POST_DEPLOY_FUNCTIONAL_TEST_PLAN.md` — a living document for ongoing platform validation.
6. Tag release in GitHub: `v2.1.0-vps` (or appropriate version bump per semver policy).
7. Post final summary to `#briefing` Discord channel: "ELIS VPS deployment complete. PE-VPS-00 through PE-VPS-07 validated."

**Validation Gate:**
- `HANDOFF.md` peer-reviewed by CODEX agent
- `CHANGELOG.md` entries present for all VPS PEs
- GitHub tag exists: `v2.1.0-vps`
- Final briefing posted to Discord

**Artifacts:** Updated `HANDOFF.md`, `README.md`, `CHANGELOG.md`, `docs/_active/POST_DEPLOY_FUNCTIONAL_TEST_PLAN.md`, `REVIEW_PE_VPS_07.md`

---

## PE Summary Table

| PE | Title | Owner | Key Deliverable | Gate |
|---|---|---|---|---|
| VPS-00 | Baseline Provisioning | CODEX → CC | Hardened VPS host | UFW + Tailscale confirmed |
| VPS-01 | Secrets Management | CODEX → CC | Zero secrets in git | truffleHog clean |
| VPS-02 | Docker Stack | CODEX → CC | Full stack healthy | All containers healthy |
| VPS-03 | Discord Architecture | CC | Channel routing live | Model routing verified |
| VPS-04 | ELIS CLI Smoke Tests | CC | Pipeline validated | pytest + CI green |
| VPS-05 | Cron Automation | CODEX → CC | All jobs scheduled | Backup to GitHub |
| VPS-06 | Security Audit | CC | CVE-clean, audit logged | Trivy + OpenClaw audit |
| VPS-07 | HANDOFF & Docs | CC → CODEX | Operational runbook | Tag released |

---

## 2-Agent Coordination Protocol (VPS Context)

Following the ELIS `AGENTS.md` pattern, the 2-agent model operates as:

**CODEX (Architect/Scaffolder):**
- Authors docker-compose, nginx configs, cron definitions, env templates
- Defines schema for new VPS-specific configs
- Posts scaffolding completion notices to `#dev`
- Does NOT execute `docker compose up` or push to production

**Claude Code (Implementer/Validator):**
- Executes deployments, runs tests, writes REVIEW_PE files
- Validates each PE gate before signaling readiness
- Posts validation results to `#dev`
- Owns `CHANGELOG.md` entries and `AUDITS.md` updates
- Escalates blockers to CODEX via `#dev` with specific error context

**Handoff Signal Convention:**
```
CODEX → CC:  "[PE-VPS-NN] scaffold ready. Files: [list]. Awaiting validation."
CC → CODEX:  "[PE-VPS-NN] validated ✅ / BLOCKED ❌ — [issue]"
```

This mirrors the existing `CURRENT_PE.md` + `HANDOFF.md` protocol from the ELIS repo.

---

## Cost & Resource Estimates

| Resource | Estimate | Notes |
|---|---|---|
| VPS (Hetzner CX21) | ~€5/month | Sufficient for ELIS v2.0 + OpenClaw |
| Anthropic API (Opus) | ~$15–30/month | Only for `#elis-research` + deep screening |
| Anthropic API (Sonnet) | ~$5–10/month | Harvest, dedup, daily workflows |
| Anthropic API (Haiku) | ~$1–2/month | Monitoring, health checks |
| Total estimated | ~€25–50/month | Scales with SLR volume |

**Optimization:** Route harvest + validation tasks to Haiku. Reserve Opus for multi-document synthesis and relevance screening only. See velvet-shark cost tips (calculator.vlvt.sh).

---

## Risk Register

| Risk | Severity | Mitigation |
|---|---|---|
| OpenClaw new release breaks existing config | High | Pin version in docker-compose. Validate in PE-VPS-01 before any other PE. |
| Secret leakage in git history | Critical | truffleHog scan in PE-VPS-01 gate. Nightly backup scan. |
| Docker volume data loss on VPS restart | High | Named volumes + nightly backup to GitHub. |
| Prompt injection via harvested sources | Medium | Apply OpenClaw "treat external content as hostile" policy (PE-VPS-06). |
| Discord bot token compromise | High | Store in Docker secret, not env. Rotate quarterly (document in SECRETS_ROTATION.md). |
| ELIS Data Contract drift between local and VPS | Medium | Run `elis validate` on every deploy as part of PE-VPS-04 gate. |

---

## Claude's Overall Recommendations

1. **Start with PE-VPS-01 (Secrets) before PE-VPS-02 (Docker Stack).** The OpenClaw new release specifically improves secrets management — understanding its new model before building the stack prevents having to re-architect the secrets layer later.

2. **Discord is the right call.** The channel-per-workflow architecture maps perfectly to the ELIS PE model. You can effectively have one Discord channel per active PE, with model routing tuned to task complexity. This is a meaningful productivity gain over Telegram's flat structure.

3. **Keep the 2-Agent boundary strict.** The CODEX/Claude Code split works because each agent has a clear responsibility. On the VPS, resist the temptation to let Claude Code do infrastructure scaffolding — that's CODEX territory. The discipline pays off in auditability.

4. **The nightly backup job is non-negotiable.** VPS environments have real failure modes (provider issues, disk exhaustion, misconfiguration). The velvet-shark backup prompt (workflow #3) is production-proven. Adopt it with the ELIS-specific additions (schemas/, runs/ manifest) from day one.

5. **Don't rush PE-VPS-06 (Security).** The OpenClaw new release's security improvements are the reason you're migrating. Validate them thoroughly. A clean `REVIEW_PE_VPS_06.md` is one of the most valuable artifacts this plan produces.

6. **Version everything.** Tag `v2.1.0-vps` on completion. The ELIS repo's audit trail and reproducibility guarantees only hold if every state change is tagged and logged in CHANGELOG.md.

---

*Plan authored using the ELIS 2-Agent dev model. Reference repos: [ELIS-SLR-Agent](https://github.com/rochasamurai/ELIS-SLR-Agent) · [OpenClaw 50-day workflows](https://gist.github.com/velvet-shark/b4c6724c391f612c4de4e9a07b0a74b6)*
