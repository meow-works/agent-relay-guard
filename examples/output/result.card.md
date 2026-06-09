# Fix flaky timing test in parser module (task-042)

- Card type: result
- Risk: low

## Summary

Replaced the sleep-based wait in the parser test with a fake clock. The flaky failure no longer reproduces and the full test suite passes.

## Recommended decision

APPROVE

Reason: Small, test-only change with green CI and no production code touched.

## Next action

Merge the pull request.

## Decision options

1. APPROVE / 2. HOLD / 3. REJECT / 4. REVISE

Detail packet: task-042-detail
