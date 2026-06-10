# External adapter patterns

This document describes conceptual ways to deliver rendered `agent-relay-guard` output without making the core tool responsible for delivery.

## Core boundary

`agent-relay-guard` validates structured JSON and renders a card and detail packet to stdout or requested output files. It performs no delivery, network, authentication, bot, or webhook work.

The core is responsible for stable review artifacts. External adapters are responsible for where those artifacts go.

## Data flow

A typical integration can be viewed as:

    AI agent or automation
    -> structured JSON
    -> agent-relay-guard
    -> card and detail packet
    -> optional external adapter
    -> maintainer-facing destination

The maintainer-facing destination might be a GitHub comment, a chat message, a dashboard, a CI artifact, or another review surface. Those destinations are outside the core tool.

## Adapter responsibilities

An external adapter may be responsible for:

- selecting which rendered artifact to deliver
- authentication and credential management
- posting and destination-specific formatting
- access control and data retention
- retry, rate-limit, and failure handling
- keeping the card and detail packet appropriately separated

The adapter should not require `agent-relay-guard` itself to know about service tokens, webhook URLs, chat channels, or hosted infrastructure.

## Example patterns

### GitHub comments

An external workflow may publish the short card as a GitHub comment and make the detail packet available separately under its own access policy.

The adapter owns GitHub authentication, posting behavior, and any decision about whether detail packets should be linked, attached, stored as artifacts, or kept private.

### Discord or Telegram

An external bot may deliver rendered output to a chat destination. The bot, credentials, destination selection, and network behavior remain outside this repository.

The core output should already be reviewable before the bot posts it.

### Dashboard

A dashboard may present the short card first and reveal the detail packet only when a maintainer requests it.

In this pattern, the dashboard owns user access, storage, retention, and any audit log behavior.

### CI wrapper

A CI job may run the CLI locally, retain the rendered artifacts, and pass them to a separate delivery step.

The CI wrapper owns environment configuration, permissions, and any posting or artifact-upload behavior.

## Security notes

- Do not place secrets in core input or rendered output.
- Treat redaction as a limited safety net, not complete secret detection.
- Keep tokens, webhook URLs, and service credentials in the adapter layer.
- Allow rendered output to be reviewed before external posting where practical.
- Apply destination-specific access controls to detail packets.
- Keep adapter logs and stored artifacts within the same information boundary as the rendered card and detail packet.

These are conceptual integration patterns. No adapters or delivery integrations are included in `agent-relay-guard`.
