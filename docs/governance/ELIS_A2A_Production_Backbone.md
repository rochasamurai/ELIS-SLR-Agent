# ELIS A2A Production Backbone

## Purpose
Define the phase-1 docs/spec/design baseline for a production-safe internal A2A communication path on elis-server.

## Non-goals
- runtime implementation
- live routing changes
- service restart
- config/auth/secret mutation
- dispatch automation
- production cutover

## Scope
- agent identity model
- message envelope and routing contract
- delivery acknowledgement semantics
- failure classification taxonomy
- durable message log design
- supervisor diagnostic visibility
- lifecycle-status integration

## Contract
- A2A messages must be authenticated and traceable.
- Every delivery attempt must have an ACK or a classified failure.
- Message history must be durable and auditable.
- Discord remains the PO-facing interface.

## Phase-1 boundaries
This document is design-only. It does not define runtime code, daemon behavior, or transport activation details.

## Evidence expectation
Any later implementation claim must be backed by command output, tests, or durable logs.
