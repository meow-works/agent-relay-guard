# agent-relay-guard

[![CI](https://github.com/meow-works/agent-relay-guard/actions/workflows/ci.yml/badge.svg)](https://github.com/meow-works/agent-relay-guard/actions/workflows/ci.yml)

Convert long AI coding agent work reports into a short, maintainer-friendly
**approval card** plus a separated **detail packet** — deterministically,
offline, with no LLM involved.

## Why this exists

AI coding agents can produce long reports, review notes, and approval
requests. Maintainers should not have to read pages of unstructured long-form
output just to decide approve / hold / reject / revise.

`agent-relay-guard` turns structured agent output into a short approval card
with a fixed set of decisions, and keeps the longer evidence in a separated
detail packet for when it is actually needed. Because the transformation is
deterministic and offline — no LLM, no network — it works as a thin review
layer, not as yet another autonomous agent in the loop.

## What it does

- Reads one structured JSON input describing an agent's report.
- Validates it against a bundled JSON Schema.
- Renders a short routine **card** (Markdown or JSON) built only from
  whitelisted summary fields, with a fixed set of decision options:
  `APPROVE / HOLD / REJECT / REVISE`.
- Renders a separated **detail packet** carrying the long-form content
  (overview, evidence, changes, open questions).
- Applies simple redaction of high-confidence secret-like values to all
  output strings and reports a `redaction_count`.

## What it does not do

- No LLM calls, no natural-language parsing — input must already be structured.
- No network access, no tokens, no external services, no servers.
- No delivery to Discord/Telegram/etc. (out of scope for this slice).
- No complete secret scanning (see "Redaction limits").

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

The `result` and `progress` card types are implemented and tested end to end.
`instruction` is accepted by the schema but ships without samples or
dedicated tests yet; it will be added in a later slice. Live
delivery adapters are intentionally out of scope.

The stable public interfaces are the CLI and the JSON Schema. Internal Python
modules are not a stable API.

## Tests

```bash
python3 -m pytest tests/
```

Tests use only temporary directories and never access the network.

## License

Apache-2.0. See [LICENSE](LICENSE).
