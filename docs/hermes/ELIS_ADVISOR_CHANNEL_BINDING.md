# ELIS Advisor Channel Binding

## Purpose

This document proposes how ELIS Advisor should be bound to Discord for the Hermes pilot.

## Canonical channel

- Name: `<#1502602267931578378>`
- Channel ID: `1502602267931578378`
- Status: approved pilot target channel

## Binding notes

Recommended pilot binding:
- use the existing Hermes default profile
- bind ELIS Advisor to the dedicated `<#1502602267931578378>` channel
- disable auto-threading for the channel if supported via `no_thread_channels`
- avoid a separate Discord bot for the pilot
- do not introduce new provider/model secrets

## Proposed routing intent

The pilot should be constrained to the advisor channel only.
The safest starting point is a whitelist-style binding for the dedicated channel, plus an explicit no-thread override.

Likely config shape in Hermes terms:
- `discord.allowed_channels`: include `1502602267931578378`
- `discord.no_thread_channels`: include `1502602267931578378`
- `discord.channel_prompts`: attach the ELIS Advisor system prompt to `1502602267931578378`

## Channel prompt intent

The channel prompt should instruct the agent to:
- act as ELIS Advisor only
- provide verdict, evidence, risk, next safest action, and draft message
- avoid dispatch, validation, config changes, GitHub writes, or merges
- use UK English

## Open questions

- channel ID is known: `1502602267931578378`
- whether the live host should use `allowed_channels` or `free_response_channels` for final behaviour
- whether the channel should remain mention-gated or respond to every message in-channel

## Verification

Before live routing:
- confirm the channel exists
- confirm the channel ID
- confirm the proposed config patch
- confirm restart/reload requirements
- confirm rollback steps
