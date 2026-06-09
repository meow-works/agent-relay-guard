# Detail packet: task-042-detail

- Card ID: task-042
- Card type: result
- Risk: low
- Redactions: 0

## Overview

The test test_parser_timeout failed intermittently on slow CI runners because it waited a fixed 0.1 seconds for the parser worker to finish. The fix injects a fake clock into the worker so the timeout path is exercised deterministically. No production module was modified.

## Evidence

- pytest: 84 passed, 0 failed (3 consecutive runs)
- CI pipeline run #1234 green on all platforms
- Reproduced the original flake 4/50 times before the fix, 0/200 after

## Changes

- tests/test_parser.py: replaced sleep-based wait with injected fake clock
- tests/conftest.py: added fake_clock fixture

## Open questions

(none)
