# agent-relay-guard

[![CI](https://github.com/meow-works/agent-relay-guard/actions/workflows/ci.yml/badge.svg)](https://github.com/meow-works/agent-relay-guard/actions/workflows/ci.yml)

`agent-relay-guard` is a small local CLI for turning structured reports from AI coding agents into something a maintainer can review quickly: a short approval card and a separate detail packet.

The card is for the decision. The detail packet is for the evidence.

## Why this exists

AI coding agents can produce useful work, but they can also produce long reports. When every handoff is a wall of text, the maintainer still has to slow down, find the decision point, check the risk, and decide what should happen next.

This project is meant to make that handoff smaller and more consistent. An agent or automation system writes a structured JSON report. `agent-relay-guard` validates it and renders a review card with four possible decisions: `APPROVE`, `HOLD`, `REJECT`, or `REVISE`.

It does not make the decision. It gives the maintainer a steadier surface to make one.

## What it does

`agent-relay-guard` reads one structured JSON input and checks it against the bundled schema. From that input, it can render:

- a short approval card in Markdown or JSON
- a separate detail packet with the longer evidence
- a `redaction_count` showing how many likely-secret values were replaced

The card only includes summary fields and a reference to the detail packet. Longer material such as evidence, file changes, and open questions stays in the detail output, so the main card stays readable.

## What it does not do

This is not an agent, a notification bot, or a hosted service.

It does not call an LLM, parse free-form natural language, make network requests, run a server, or send messages to Discord, Telegram, GitHub comments, or any other destination. It renders local output to stdout or to the file path you choose.

That boundary is intentional. Delivery can be handled later by a wrapper, bot, dashboard, or CI workflow. Keeping delivery outside the core keeps this tool easier to test and avoids mixing rendering logic with tokens, webhooks, or service-specific behavior.

## How it fits into a review workflow

A practical setup might look like this:

1. An AI coding agent prepares a structured JSON report for a proposed task, current progress, or completed result.
2. `agent-relay-guard` validates that report and renders the card/detail pair.
3. Another layer, such as a script, dashboard, GitHub comment workflow, Discord bot, or Telegram bot, can deliver the rendered output.
4. The maintainer reads the short card first and opens the detail packet only when more context is needed.

In other words, this repository is the rendering layer. It is the part that makes the review artifact stable before anything posts it somewhere else.

## Quick start

Requires Python 3.11+. No runtime dependencies.

```bash
pip install .

agent-relay-guard validate examples/input/result.json
agent-relay-guard render examples/input/result.json
agent-relay-guard render examples/input/result.json --format json
agent-relay-guard detail examples/input/result.json --format json
agent-relay-guard schema
```

Or without installing:

```bash
PYTHONPATH=src python3 -m agent_relay_guard.cli render examples/input/result.json
```

## Example output

From the structured input in
[`examples/input/result.json`](examples/input/result.json), `render` produces
this approval card:

```markdown
# Fix flaky timing test in parser module (task-042)

- Card type: result
- Risk: low

## Summary

Replaced the sleep-based wait in the parser test with a fake clock. The flaky
failure no longer reproduces and the full test suite passes.

## Recommended decision

APPROVE

Reason: Small, test-only change with green CI and no production code touched.

## Next action

Merge the pull request.

## Decision options

1. APPROVE / 2. HOLD / 3. REJECT / 4. REVISE

Detail packet: task-042-detail
```

The long-form evidence stays out of the card; `detail` renders it separately.
See [`examples/`](examples/) for the complete input, card, and detail packet.

## CLI commands

| Command | Purpose |
| --- | --- |
| `validate INPUT` | Validate an input file against the schema |
| `render INPUT --format markdown\|json [--output PATH]` | Render the routine approval card |
| `detail INPUT --format markdown\|json [--output PATH]` | Render the separated detail packet |
| `schema` | Print the input JSON Schema |

When `--output` is omitted, output goes to stdout.

Exit codes: `0` success, `1` validation or input error (invalid JSON, schema
violation), `2` CLI usage or IO error (unknown options or a missing command —
argparse exits with 2 — as well as unreadable input or unwritable output).

## Input contract

See [`src/agent_relay_guard/schemas/input.schema.json`](src/agent_relay_guard/schemas/input.schema.json)
(also printed by `agent-relay-guard schema`) and the sample at
[`examples/input/result.json`](examples/input/result.json).

Fixed enums:

- `card_type`: `progress | instruction | result`
- `risk`: `low | medium | high | critical | unknown`
- `recommended_decision`: `APPROVE | HOLD | REJECT | REVISE`

`schema_version` must be exactly `"1.0"`.

## Card / detail separation

The routine card never includes detail bodies (overview, evidence, changes,
open questions). It carries only short whitelisted fields plus a
`detail_packet_id`, derived deterministically as `{id}-detail`. The detail
packet carries the long-form content under the same id.

Both card JSON and detail packet always include `redaction_count`, even when
it is `0`.

See [`examples/output/`](examples/output/) for the rendered card and detail
packet produced from the sample input.

## Redaction limits

Redaction is a small safety net, **not** a complete secret scanner. It
replaces a few high-confidence patterns (bearer authorization values, private
key blocks, and `token` / `secret` / `password` / `api_key` style assignments)
with `[REDACTED]`. Removing secrets before input is the caller's
responsibility.

## Data boundary

This repository is a standalone open-source project. It does not contain
business logic, customer data, credentials, or private operational details
from any other project. Inputs are expected to be structured JSON supplied by
the caller; the tool does not run a persistent service, keep internal
storage, or send data anywhere. It only writes the output file you request
with `--output`.

## Current slice limitations

All three card types (`result`, `progress`, and `instruction`) ship with
examples and end-to-end tests. Live
delivery adapters are intentionally out of scope.

The stable public interfaces are the CLI and the JSON Schema. Internal Python
modules are not a stable API.

## Roadmap

The next useful work is not to make the core larger for its own sake. It is to make the review workflow around it easier to understand and safer to build.

Near-term directions include:

- improving validation diagnostics as real invalid inputs appear
- adding practical workflow examples for AI coding agents and maintainers
- documenting wrapper patterns for GitHub comments, Discord, Telegram, and dashboards without putting delivery code in the core
- clarifying what should be stable before the next tagged release

These are future maintenance directions, not features included in the current release. The core should stay local, predictable, and based on structured JSON input.

## Tests

```bash
python3 -m pytest tests/
```

Tests use only temporary directories and never access the network.

## License

Apache-2.0. See [LICENSE](LICENSE).
