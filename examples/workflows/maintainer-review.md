# Maintainer review workflow example

This walkthrough shows three checkpoints where a maintainer may review structured output from an AI coding agent.

The shipped fixtures use independent fictional tasks. They illustrate the three card types, but they do not represent one task changing state over time.

## 1. Review the proposed scope

Use the instruction fixture before work begins:

- Input: `../input/instruction.json`
- Card: `../output/instruction.card.md`
- Detail: `../output/instruction.detail.md`

The maintainer checks the proposed scope and chooses `APPROVE`, `HOLD`, `REJECT`, or `REVISE`. The recommended decision is guidance, not an automatic authorization.

## 2. Review work in progress

Use the progress fixture when work has started but a decision or additional evidence is still needed:

- Input: `../input/progress.json`
- Card: `../output/progress.card.md`
- Detail: `../output/progress.detail.md`

This example recommends `HOLD` because a required cross-platform check is still pending.

## 3. Review the completed result

Use the result fixture after implementation and verification:

- Input: `../input/result.json`
- Card: `../output/result.card.md`
- Detail: `../output/result.detail.md`

The maintainer reviews the short result card and opens the detail packet when the evidence or changed files need closer inspection.

## Render a checkpoint

For example, render the instruction card:

    agent-relay-guard render examples/input/instruction.json --format markdown --output examples/output/instruction.card.md

Render the matching detail packet:

    agent-relay-guard detail examples/input/instruction.json --format markdown --output examples/output/instruction.detail.md

Replace `instruction` with `progress` or `result` to render the other fixtures.

Delivery is separate from this workflow. An optional external wrapper may post the rendered files elsewhere, but `agent-relay-guard` itself performs no network or notification work.
