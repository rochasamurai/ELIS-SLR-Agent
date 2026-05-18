# ELIS A2A Production Security Model

## Goals
- authenticated agent identities only
- least-privilege message delivery
- explicit delivery acknowledgements
- auditability for all dispatch and reply events

## Threats addressed
- spoofed agent identity
- silent message loss
- uncontrolled fan-out
- undocumented retries
- hidden routing failures

## Controls
- durable append-only log
- message correlation identifiers
- failure classification on every non-ACK outcome
- supervisor visibility for diagnostic review
- no arbitrary agent-to-agent injection

## Out of scope for Phase 1
- auth/secret changes
- runtime transport implementation
- live routing mutation
- service or daemon restart
- deployment changes

## Evidence model
Security claims require either tests, command output, or persisted log evidence.
