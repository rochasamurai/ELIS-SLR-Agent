# ELIS Discord / PO Checkpoint Governance

**Status:** Canonical — v1.0  
**Date:** 2026-05-03  
**Owner:** Carlos Rocha, Product Owner  
**Applies to:** PM, PO Advisor, Platform Monitor, and PE threads

## 1. Purpose

This document defines how Discord is used for PE checkpoint communication.

- **Main Discord channel** = portfolio-level control and escalation.
- **PE thread** = operational checkpoint and audit trail.
- **GitHub** = canonical artefact and evidence record.
- **Task Flow** = lifecycle state.
- **Lobster** = deterministic execution.
- **Hermes / PO Advisor** = advisory and risk review.
- **Carlos** = approval authority.

## 2. Thread Rules

1. Use one Discord thread per PE when thread-based coordination is available.
2. Keep PE checkpoint messages compact and versioned by reference to GitHub artefacts.
3. Use the main channel only for portfolio-level updates, blocking issues, escalation, or approval requests.
4. Use the PE thread for implementation checkpoints, validator status, and brief status packets.
5. Do not treat Discord history as canonical; always anchor final state in GitHub.

## 3. Message Boundary Rules

- Keep Discord messages under 2,000 characters when possible.
- If a checkpoint exceeds the limit, split it into continuation messages.
- The first message should carry the primary status summary; continuation messages should be clearly labelled.
- Do not bury required evidence in a long unstructured thread post.

## 4. Compact PO Checkpoint Packet

A PE checkpoint message should normally include:

- PE ID
- current state
- commit hash or branch
- required artefact status
- blocker or next action
- whether the next owner is PM, implementer, validator, or PO

## 5. Boundary Summary

- **PM** coordinates and reports.
- **PO Advisor / Platform Monitor** advises and diagnoses.
- **Validators** report verdicts.
- **Implementers** report build status and handoff evidence.
- **No Discord message is authoritative unless the matching GitHub artefact exists.**
