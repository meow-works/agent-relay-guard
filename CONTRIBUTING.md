# Contributing to agent-relay-guard

Thanks for your interest in contributing!

`agent-relay-guard` is a small, local CLI that converts structured JSON input
from AI coding agents into short, maintainer-ready approval cards and
separated detail packets. It is deterministic and offline by design: no LLM
calls, no network access, no external services.

## What contributions are welcome right now

The project is in an early, deliberately small stage. The most helpful
contributions are:

- Bug reports with a minimal reproduction
- Small documentation fixes
- Schema and validation improvements
- Tests for existing behavior

Small, focused pull requests are much easier to review and merge than large
ones. If a change grows beyond one topic, please split it.

## What is out of scope (or needs discussion first)

To keep the core small and safe, the following are out of scope for now, or
need an issue discussion before any implementation:

- Live agent integrations
- Network services of any kind
- Secrets handling
- Vendor-specific automation
- Broad LLM extraction features

If you are unsure whether an idea fits, please open an issue first and ask.

## Development

Requires Python 3.11+. No runtime dependencies.

```bash
python3 -m pytest tests/
```

Tests must use only temporary directories and must not access the network.

## License

By contributing, you agree that your contributions will be licensed under the
Apache-2.0 license.
