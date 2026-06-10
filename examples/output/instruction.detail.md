# Detail packet: task-063-detail

- Card ID: task-063
- Card type: instruction
- Risk: low
- Redactions: 0

## Overview

The README's Configuration section does not state the default request timeout, and two users have asked about it in discussions. This card proposes a documentation-only pull request that adds the default value and one override example. Nothing has been changed yet; work starts only after this card is approved.

## Evidence

- Two separate user questions about the default timeout in project discussions
- README Configuration section currently omits the default value

## Changes

- Proposed: README.md: state the default timeout value in the Configuration section
- Proposed: README.md: add one example showing how to override the timeout

## Open questions

- Should the override example show seconds or milliseconds?
