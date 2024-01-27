---
CIP: ????
Title: Augment Spend Purpose
Category: Plutus
Status: Proposed
Authors:
    - Micah Kendall <micah@mcomp.tech>
Implementors: []
Discussions:
    - https://github.com/cardano-foundation/CIPs/pull/754
Created: 2024-01-27
License: CC-BY-4.0
---

## Abstract
<!-- A short (\~200 word) description of the proposed solution and the technical issue being addressed. -->

We should change the purpose Spend(OutputReference) to instead be Spend(OutputReference, ScriptHash), where ScriptHash is a bytearray / bytestring of the script hash.

## Motivation: why is this CIP necessary?
This makes common patterns in contract development much cheaper, but also more ergonomic.

## Specification
There should be a 2nd value in the Spend constructor for the script purpose, which is the script hash of the spending script.

## Rationale: how does this CIP achieve its goals?
We would have the script hash available as a constant-time lookup, instead of linear-time.

## Path to Active

### Acceptance Criteria
The plutus ledger team add the script hash as a second value inside the spend constructor.

### Implementation Plan
N/A as it is a very simple change

## Copyright

This CIP is free and unencumbered, released by it's author into the public domain.