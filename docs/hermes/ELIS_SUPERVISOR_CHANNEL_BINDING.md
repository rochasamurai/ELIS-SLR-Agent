# ELIS Supervisor Channel Binding

## Purpose

This document proposes the Discord binding for ELIS Platform Monitor / Supervisor behaviour on Hermes.

## Canonical channel

- Name: `<#1494725349261709343>`
- Channel ID: `1494725349261709343`
- Status: approved platform-monitor channel

## Binding notes

Recommended pilot binding:
- use the existing Hermes default profile for the pilot
- bind Supervisor/Platform Monitor behaviour to `<#1494725349261709343>`
- keep the channel within the approved Hermes allowlist only
- no separate Discord bot for the pilot
- no new provider/model secrets

## Channel prompt intent

The channel prompt should instruct the agent to:
- act as ELIS Platform Monitor / Supervisor only
- diagnose Hermes/OpenClaw gateway issues
- verify auth, provider, model, path, and service status
- inspect logs
- verify Discord connectivity
- classify operational risk
- avoid dispatch, validation, config changes, GitHub writes, or merges
- use UK English

## Verification

Before live routing:
- confirm the channel exists
- confirm the channel ID
- confirm the proposed config patch
- confirm restart/reload requirements
- confirm rollback steps
