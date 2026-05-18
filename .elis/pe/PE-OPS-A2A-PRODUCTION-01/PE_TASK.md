# PE-OPS-A2A-PRODUCTION-01 — Implement Production A2A Agent Communication Backbone

## PE_ID
PE-OPS-A2A-PRODUCTION-01

## Objective
Implement a production-safe internal A2A communication path on elis-server so ELIS agents can exchange reset acknowledgements, dispatch requests, validation requests, blocker reports, evidence notices, and lifecycle status without relying only on Discord thread/session routing.

## Opening packet
- Lane: Strict
- Baseline HEAD: `da7f9d505cfd6b3181e0720ea9a2f9678115147e`
- Branch: `feature/pe-ops-a2a-production-01`
- Implementer: `infra-impl-b`
- Validator: `infra-val-a`
- Supervisor verification role: read-only only

## First-pass files
- `CURRENT_PE.md`
- `.elis/pe/PE-OPS-A2A-PRODUCTION-01/PE_TASK.md`
- `.elis/pe/PE-OPS-A2A-PRODUCTION-01/DISPATCH_STATUS.md`
- `.elis/pe/PE-OPS-A2A-PRODUCTION-01/dispatch-status.json`
- `docs/governance/ELIS_A2A_Production_Backbone.md`
- `docs/governance/ELIS_A2A_Production_Security_Model.md`
- `docs/governance/ELIS_A2A_Production_Rollback.md`

## Phase 1 scope
- Docs/spec/design only
- Message contract and envelope
- Agent identity and routing model
- Delivery acknowledgement semantics
- Failure classification taxonomy
- Durable message log design
- Supervisor diagnostic visibility
- Lifecycle-status integration
- Discord remains PO-facing only

## Explicit exclusions
- runtime code
- service units
- OpenClaw/Hermes config mutation
- auth/secret changes
- runtime deployment
- service restart
- live routing mutation
- dispatch automation
- production cutover

## Runtime / service / config boundaries
- No runtime implementation in Phase 1.
- No service or daemon changes in Phase 1.
- No auth, secret, token, or environment mutation in Phase 1.
- No transport activation or live routing in Phase 1.

## Security model
- Authenticated agent identities only.
- Append-only durable audit log.
- Least-privilege dispatch.
- Explicit delivery ACKs.
- Classified failures, no silent drops.
- No arbitrary agent-to-agent injection.

## Rollback plan
- Keep Discord/session routing as fallback.
- Gate the new transport behind a disable switch.
- No destructive migration in Phase 1.
- Revert by branch/worktree only if needed.

## Evidence requirements
- Baseline HEAD must match `origin/main`.
- Clean worktree required before opening.
- Pasted command output required for all state claims.
- Routing/ACK claims require log or test evidence.
- Validator verdict must include inline evidence before the verdict line.

## Phase gates
1. PO approves the opening packet.
2. PM updates `CURRENT_PE.md` and creates the A2A branch from `origin/main`.
3. Implementer drafts the A2A backbone docs/spec/design only.
4. Validator verifies with tests and evidence.
5. Only then consider runtime/config/service changes.

## Handoff requirements
- Opening packet recorded in `CURRENT_PE.md`.
- Task file created at the approved path.
- Implementer dispatch deferred until PO approves the implementation packet.
