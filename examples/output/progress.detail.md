# Detail packet: task-051-detail

- Card ID: task-051
- Card type: progress
- Risk: medium
- Redactions: 0

## Overview

The new lint subcommand validates config files against the documented format and reports line-level errors. Rule definitions, error formatting, and unit tests are complete. The remaining work is a cross-platform check: path normalization on Windows has not been exercised, and one helper uses os.path.join in a way that needs verification there.

## Evidence

- pytest: 41 passed locally on Linux
- lint subcommand verified against 6 sample config files
- Windows path handling check: not yet run

## Changes

- src/cli/lint.py: new lint subcommand with rule engine
- tests/test_lint.py: unit tests for all current rules

## Open questions

- Does path normalization behave the same on Windows runners?
