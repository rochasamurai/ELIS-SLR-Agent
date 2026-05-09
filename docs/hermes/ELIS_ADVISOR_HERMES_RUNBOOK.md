# ELIS Advisor Hermes Runbook

## Purpose

Read-only preparation and later live configuration guidance for the ELIS Advisor Hermes pilot.

## Current pilot decision

- Canonical name: ELIS Advisor
- Hermes profile: existing default profile for the pilot
- Discord target: dedicated channel `<#1502602267931578378>`
- No separate Discord bot for the pilot
- No new provider/model secrets for the pilot
- No OpenClaw config changes
- No live Hermes config edit yet

## Proposed live Hermes patch

This is a proposal only.
Do not apply until PO approves the exact patch.

```yaml
discord:
  allowed_channels:
    - "1502602267931578378"
  no_thread_channels:
    - "1502602267931578378"
  channel_prompts:
    "1502602267931578378": |
      You are ELIS Advisor.
      You are advisory-only.
      Return:
      1. Verdict
      2. Correct recipient
      3. Evidence
      4. Risk
      5. Next safest action
      6. Draft message
      Use UK English.
      Do not dispatch agents, validate, modify config, write to GitHub, or merge.
```

## Required checks before applying any live patch

- confirm `1502602267931578378` is the live channel ID
- confirm the patch syntax matches the live Hermes config format
- confirm the channel prompt is correct
- confirm whether mention gating is still desired
- confirm rollback path

## Restart / reload

A Hermes gateway restart or reload is expected after any live config change.

Suggested sequence:
1. back up current Hermes config
2. apply the exact approved patch
3. restart `hermes-gateway.service`
4. verify status and routing behaviour
5. verify the advisor responds only in the intended channel

## Rollback

If the patch misbehaves:
1. restore the previous config snapshot
2. restart or reload Hermes gateway again
3. verify the old routing state is restored
4. record the failure and the restored state

## Validation checklist

- [ ] channel exists
- [ ] channel ID recorded
- [ ] proposed patch approved
- [ ] no new secrets required
- [ ] no separate bot required for the pilot
- [ ] gateway restart plan recorded
- [ ] rollback plan recorded
