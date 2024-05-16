---
CIP: ????
Title: Bitwise operations
Category: Plutus
Status: Proposed
Authors:
    - Koz Ross <koz@mlabs.city>
Implementors: 
    - Koz Ross <koz@mlabs.city>
Discussions:
    - https://github.com/cardano-foundation/CIPs/pull/?
Created: 2024-05-16
License: Apache-2.0
---

## Abstract
<!-- A short (\~200 word) description of the proposed solution and the technical issue being addressed. -->

## Motivation: why is this CIP necessary?
<!-- A clear explanation that introduces the reason for a proposal, its use cases and stakeholders. If the CIP changes an established design then it must outline design issues that motivate a rework. For complex proposals, authors must write a Cardano Problem Statement (CPS) as defined in CIP-9999 and link to it as the `Motivation`. -->

## Specification
<!-- The technical specification should describe the proposed improvement in sufficient technical detail. In particular, it should provide enough information that an implementation can be performed solely on the basis of the design in the CIP. This is necessary to facilitate multiple, interoperable implementations. This must include how the CIP should be versioned, if not covered under an optional Versioning main heading. If a proposal defines structure of on-chain data it must include a CDDL schema in its specification.-->

## Rationale: how does this CIP achieve its goals?
<!-- The rationale fleshes out the specification by describing what motivated the design and what led to particular design decisions. It should describe alternate designs considered and related work. The rationale should provide evidence of consensus within the community and discuss significant objections or concerns raised during the discussion.

It must also explain how the proposal affects the backward compatibility of existing solutions when applicable. If the proposal responds to a CPS, the 'Rationale' section should explain how it addresses the CPS, and answer any questions that the CPS poses for potential solutions.
-->

## Path to Active

### Acceptance Criteria

We consider the following criteria to be essential for acceptance:

* A proof-of-concept implementation of the operations specified in this 
  document, outside of the Plutus source tree. The implementation must be in 
  GHC Haskell, without relying on the FFI.
* The proof-of-concept implementation must have tests, demonstrating that it 
  behaves as the specification requires.
* The proof-of-concept implementation must demonstrate that it will 
  successfully build, and pass its tests, using all GHC versions currently 
  usable to build Plutus (8.10, 9.2 and 9.6 at the time of writing), across 
  all [Tier 1][tier-1] platforms.

Ideally, the implementation should also demonstrate its performance 
characteristics by well-designed benchmarks.

### Implementation Plan

MLabs has begun the implementation of the [proof-of-concept][impl] as required in 
the acceptance criteria. Upon completion, we will send a pull request to 
Plutus with the implementation of the primitives for Plutus Core, mirroring 
the proof-of-concept.

## Copyright

This CIP is licensed under [Apache-2.0](http://www.apache.org/licenses/LICENSE-2.0).

[tier-1]: https://gitlab.haskell.org/ghc/ghc/-/wikis/platforms#tier-1-platforms
[impl]: https://github.com/mlabs-haskell/plutus-integer-bytestring/tree/koz/milestone-2
