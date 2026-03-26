# ADR-006: OpenClaw as Native Orchestration Runtime

**Status:** Accepted
**Date:** 2026-03-26
**Deciders:** PM (Carlo Rocha), CODEX, Claude Code

## Context

The ELIS PM Agent needs a runtime environment that can:

- maintain a persistent conversation session across reboots
- expose the agent to multiple channels (Telegram, Discord)
- enforce an exec-approvals allowlist before running shell commands
- restart automatically on failure
- integrate with the existing Linux system (elis-server)

The initial PE-VPS-00 baseline used Docker Compose to run the gateway and
agent services. As the MiniServer series (PE-MS-01 to PE-MS-08) progressed,
the Docker-based setup was replaced incrementally with a native OpenClaw
installation managed by `systemd --user`.

## Decision

OpenClaw is used as the **native orchestration runtime** for the PM Agent on
elis-server. The gateway and agent processes run as `systemd --user` services,
not inside Docker containers. Configuration, workspace entrypoints, and
exec-approval rules are managed through OpenClaw's native CLI (`openclaw`).

## Consequences

### Positive
- Native `systemd --user` integration: automatic restart on failure, standard
  `journalctl` logging, and `systemctl enable` for start-on-boot.
- Lower overhead than Docker: no container runtime, no image layers, no port
  mapping.
- OpenClaw's exec-approvals system (`exec-approvals.json`) provides a
  structured allowlist that can be audited without inspecting Docker volumes.
- Standard Linux tooling (`systemctl`, `journalctl`, `ls`) works on the
  workspace without Docker exec indirection.

### Negative / trade-offs
- Native installation is host-specific; reproducing the environment on a
  different server requires re-running the install procedure
  (`docs/openclaw/NATIVE_INSTALL.md`).
- Upgrading OpenClaw requires operator action on the host; there is no
  container image tag to pin.
- The Docker-based setup (PE-VPS-00 baseline) is now superseded; any rollback
  to Docker would require restoring the old Compose configuration.

## Alternatives considered

### Alternative A — Docker Compose

Run the OpenClaw gateway and PM Agent as Docker Compose services.

Used as the baseline in PE-VPS-00 and the early MiniServer series. Replaced
by native install because:
- Added Docker-specific operational overhead (`docker exec`, volume mounts,
  image rebuilds) to every maintenance task.
- The exec-approvals allowlist needed to be managed inside a container, making
  audit harder.
- The agent workspace (`~/openclaw/workspace-pm/`) is naturally a host directory;
  mounting it as a Docker volume added fragility during redeployment
  (`rsync --delete` would interact unpredictably with mounted volumes).

### Alternative B — Direct API calls without a runtime

Each agent session makes API calls directly, without a persistent gateway
process.

Discarded because:
- No persistent session store: conversation history is lost between invocations.
- No channel multiplexing: separate processes would be needed for Telegram and
  Discord.
- No exec-approvals enforcement: shell command safety would have to be
  reimplemented per-invocation.

## Evidence / references

- `docs/openclaw/NATIVE_INSTALL.md` — native installation procedure
- `docs/openclaw/DEPLOYMENT.md` — deployment and workspace setup
- `docs/openclaw/NATIVE_OPERATIONS_AND_RESTORE_RUNBOOK.md` — operations guide
- PE-MS-08 (PR #302) — end-to-end validation of the native runtime on elis-server
- `systemctl --user status openclaw-gateway` — service confirmed active since
  2026-03-26 in PE-MS-08 validation evidence
