# ELIS A2A Gateway Specification — Phase 1

**Status:** Phase 1 — Local-only A2A gateway specification.
**Version:** 1.0
**Date:** 2026-05-09
**Binding:** `127.0.0.1:24001`

---

## 1. Overview

The A2A Gateway is a minimal, local-only HTTP/WebSocket service that routes structured
messages between the three Phase-1 agents:

- `elis-advisor`
- `elis-pm`
- `elis-supervisor`

The gateway is independent of both the Hermes gateway and the OpenClaw runtime. It runs as
a standalone process on the loopback interface only.

---

## 2. Network Binding

| Property | Value |
|----------|-------|
| Address | `127.0.0.1` |
| Port | `24001` |
| Protocol | HTTP / WebSocket |
| TLS | Not required (local-only loopback) |

The gateway MUST refuse to start if any non-loopback interface is configured.

---

## 3. Startup

```bash
# Start the A2A gateway
node /opt/elis/a2a/a2a-gateway.js

# Or using the wrapper script
bash /opt/elis/a2a/a2a-gateway.sh
```

Expected startup output:
```
[ELIS A2A Gateway] Binding to 127.0.0.1:24001
[ELIS A2A Gateway] Registered agents: elis-advisor, elis-pm, elis-supervisor
[ELIS A2A Gateway] Gateway ready
```

---

## 4. API Endpoints

### 4.1 Health Check

```
GET http://127.0.0.1:24001/health
```

Response:
```json
{
  "status": "ok",
  "a2a_version": "1.0",
  "agents": ["elis-advisor", "elis-pm", "elis-supervisor"]
}
```

### 4.2 Send Message

```
POST http://127.0.0.1:24001/message
Content-Type: application/json
```

Request body must validate against `schemas/a2a_envelope.schema.json`.

On acceptance:
```json
{"status": "accepted", "message_id": "550e8400-e29b-41d4-a716-446655440000"}
```

On validation failure:
```json
{"status": "rejected", "error": "Invalid envelope: recipient 'elis-unknown' is not a recognised agent identity"}
```

### 4.3 Receive Message (Polling)

```
GET http://127.0.0.1:24001/messages?agent=elis-pm&since=<ISO-8601-timestamp>
```

Response:
```json
{
  "messages": [
    {
      "a2a_version": "1.0",
      "message_id": "550e8400-e29b-41d4-a716-446655440000",
      "sender": "elis-advisor",
      "recipient": "elis-pm",
      "message_type": "structured_message",
      "timestamp": "2026-05-09T12:00:00Z",
      "payload": {
        "subject": "Evidence status check",
        "body": "Has PE-OPS-A2A-01 evidence been collected?"
      }
    }
  ]
}
```

### 4.4 Receive Message (WebSocket)

```
WS ws://127.0.0.1:24001/ws?agent=elis-pm
```

Messages are pushed to the WebSocket connection in real-time. Each message is a JSON
envelope as defined in `schemas/a2a_envelope.schema.json`.

---

## 5. Gateway Logic

### 5.1 Message Routing

```text
Incoming message →
  1. Validate envelope schema (reject if invalid)
  2. Validate sender identity (reject if unknown)
  3. Validate recipient identity (reject if unknown)
  4. Validate communication pair (reject if not in allowed pairs)
  5. Validate message_type (reject if not recognised)
  6. Check for prohibited content (reject if prohibited pattern detected)
  7. Queue message for recipient
  8. Return {"status": "accepted", "message_id": "<uuid>"}
```

### 5.2 Pair Validation Table

| Sender | Recipient | Allowed |
|--------|-----------|---------|
| elis-advisor | elis-pm | Yes |
| elis-advisor | elis-supervisor | Yes |
| elis-pm | elis-advisor | Yes |
| elis-pm | elis-supervisor | Yes |
| elis-supervisor | elis-advisor | Yes |
| elis-supervisor | elis-pm | Yes |
| *any* | *any other agent* | **No** |

### 5.3 Prohibited Content Patterns

The gateway MUST scan outgoing messages for the following prohibited patterns and reject
them if detected:

- GitHub write operations: `git push`, `git commit -m`, `gh pr create`, `gh pr merge`
- Config modifications: `config.yaml`, `openclaw.json` write references
- Secret/token operations: `export *TOKEN`, `export *SECRET`, `GH_TOKEN=`
- Service restarts: `systemctl restart`, `systemctl --user restart`
- PR/merge operations

---

## 6. Message Queue

The gateway maintains an in-memory message queue per agent:

| Agent | Queue |
|-------|-------|
| `elis-advisor` | Messages addressed to `elis-advisor` |
| `elis-pm` | Messages addressed to `elis-pm` |
| `elis-supervisor` | Messages addressed to `elis-supervisor` |

Messages older than their `ttl_seconds` value are purged from the queue.

---

## 7. Implementation Plan

### 7.1 Files

| File | Description |
|------|-------------|
| `/opt/elis/a2a/a2a-gateway.js` | Node.js HTTP/WebSocket gateway server |
| `/opt/elis/a2a/a2a-gateway.sh` | Convenience startup wrapper |
| `/opt/elis/a2a/package.json` | Node.js package manifest |

### 7.2 Dependencies

- Node.js 18+ (available via `/usr/bin/node` on elis-server)
- `ws` npm package for WebSocket support (or built-in `http` module for polling-only)

### 7.3 Startup Verification

```bash
# 1. Start the gateway
node /opt/elis/a2a/a2a-gateway.js &
sleep 1

# 2. Verify health endpoint
curl -s http://127.0.0.1:24001/health

# 3. Verify send endpoint
curl -s -X POST http://127.0.0.1:24001/message \
  -H 'Content-Type: application/json' \
  -d '{
    "a2a_version": "1.0",
    "message_id": "00000000-0000-0000-0000-000000000001",
    "timestamp": "2026-05-09T12:00:00Z",
    "sender": "elis-pm",
    "recipient": "elis-supervisor",
    "message_type": "diagnostic_query",
    "payload": {
      "subject": "Service check",
      "diagnostic_command": "status"
    }
  }'

# 4. Verify polling endpoint
curl -s "http://127.0.0.1:24001/messages?agent=elis-supervisor&since=2026-05-09T11:00:00Z"

# 5. Verify rejected message
curl -s -X POST http://127.0.0.1:24001/message \
  -H 'Content-Type: application/json' \
  -d '{
    "a2a_version": "1.0",
    "message_id": "00000000-0000-0000-0000-000000000002",
    "timestamp": "2026-05-09T12:00:00Z",
    "sender": "elis-pm",
    "recipient": "infra-impl-b",
    "message_type": "structured_message",
    "payload": {
      "subject": "Unauthorised",
      "body": "This should be rejected"
    }
  }'
```

---

## 8. Logging

The gateway logs to stdout with the following format:

```
[YYYY-MM-DDTHH:MM:SSZ] [LEVEL] [message_id] MESSAGE
```

Levels: `INFO`, `WARN`, `ERROR`

Example:
```
[2026-05-09T12:00:00Z] [INFO] [550e8400] Accepted message: elis-pm -> elis-supervisor (diagnostic_query)
[2026-05-09T12:00:01Z] [WARN] [00000000] Rejected message: sender=elis-pm, recipient=infra-impl-b (unknown agent)
```

Optionally, logs may be duplicated to `~/.elis/a2a/gateway.log`.

---

## 9. Shutdown

```bash
# Graceful shutdown
kill -TERM <PID>

# The gateway will:
# 1. Stop accepting new connections
# 2. Drain pending messages (up to 5 seconds)
# 3. Exit with code 0
```

---

## 10. Error Handling

| Condition | HTTP Status | Response |
|-----------|-------------|----------|
| Schema validation failure | 400 | `{"status": "rejected", "error": "..."}` |
| Unknown sender/recipient | 400 | `{"status": "rejected", "error": "..."}` |
| Disallowed pair | 400 | `{"status": "rejected", "error": "..."}` |
| Prohibited content | 400 | `{"status": "rejected", "error": "..."}` |
| Internal error | 500 | `{"status": "error", "error": "Internal server error"}` |
| Not found | 404 | `{"status": "error", "error": "Not found"}` |

---

## 11. Future Considerations (Out of Scope for Phase 1)

- Persistent message store (database backing)
- TLS for external access
- Additional agent identities beyond Phase 1
- Message encryption
- Authentication/authorisation beyond identity validation
- Full A2A agent discovery

---

## 12. Future Runtime Gates

Before any live A2A implementation is allowed, the following gates must be approved and evidenced separately:

1. schema artefact exists and validates;
2. runtime code is reviewed and committed;
3. launch mechanism / service unit is reviewed;
4. OpenClaw/Hermes config impact is reviewed (if any);
5. no credentials/secrets/auth changes are required;
6. live routing change is explicitly approved;
7. rollback/verification evidence is captured.

Phase 1 does not include these gates; it only defines the specification for later controlled implementation.
