---
CIP: ???
Title: Logical operations
Category: Plutus
Status: Proposed
Authors:
    - Koz Ross <koz@mlabs.city>
    - Sparsa Roychowdhury <sparsa.roychowdhury@mlabs.city>
Implementors: []
Discussions:
    - https://github.com/cardano-foundation/CIPs/pull/?
Created: YYYY-MM-DD
License: Apache-2.0
---

## Abstract

We describe the semantics of a set of logical operations for Plutus
`BuiltinByteString`s. Specifically, we provide descriptions for:

- Bitwise logical AND, OR, XOR and complement;
- Reading a bit value at a given index;
- Setting a bit value at a given index.

As part of this, we also describe the bit ordering within a `BuiltinByteString`,
and provide some laws these operations should obey.

## Motivation: why is this CIP necessary?

TODO: Add case for integer set

TODO: Another 1-2 example uses

## Specification

We describe the proposed operations in several stages. First, we specify a
scheme for indexing individual bits (rather than whole bytes) in a
`BuiltinByteString`. We then specify the semantics of each operation, as well as
giving costing expectations. Lastly, we provide some laws that these operations
are supposed to obey, as well as giving some specific examples of results from
the use of these operations.

### Bit indexing scheme

TODO: Specify this

### Operation semantics

TODO: Specify

### Laws and examples

TODO: Make some

## Rationale: how does this CIP achieve its goals?

TODO: Explain goals relative examples, give descriptions of non-existent
alternatives

## Path to Active

### Acceptance Criteria

TODO: Fill these in (lower priority)

### Implementation Plan

These operations will be implemented by MLabs, to be merged into Plutus Core
after review.

## Copyright

This CIP is licensed under [Apache-2.0](http://www.apache.org/licenses/LICENSE-2.0).
