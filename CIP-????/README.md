---
CIP: ???
Title: multi-arity uplc lambda node
Category: Plutus
Status: Proposed
Authors:
    - Michele Nuzzi <michele@harmoniclabs.tech>
Implementors: []
Discussions:
    - https://github.com/cardano-foundation/CIPs/pull/?
Created: 2025-06-02
License: CC-BY-4.0
---

<!-- Existing categories:

- Meta     | For meta-CIPs which typically serves another category or group of categories.
- Wallets  | For standardisation across wallets (hardware, full-node or light).
- Tokens   | About tokens (fungible or non-fungible) and minting policies in general.
- Metadata | For proposals around metadata (on-chain or off-chain).
- Tools    | A broad category for ecosystem tools not falling into any other category.
- Plutus   | Changes or additions to Plutus
- Ledger   | For proposals regarding the Cardano ledger (including Reward Sharing Schemes)
- Catalyst | For proposals affecting Project Catalyst / the Jörmungandr project

-->

## Abstract
<!-- A short (\~200 word) description of the proposed solution and the technical issue being addressed. -->
This CIP proposes a new CIP node for an uplc tree.

The node is intended to have the same effect of n consecutive lambda nodes for 1/n the cost. Improving contracts in all measurable metrics (size, cpu, memory)

([See rendered proposal in branch](https://github.com/HarmonicLabs/multi-arity-lambda/blob/master/CIP-%3F%3F%3F%3F/README.md))

## Motivation: why is this CIP necessary?
<!-- A clear explanation that introduces the reason for a proposal, its use cases and stakeholders. If the CIP changes an established design then it must outline design issues that motivate a rework. For complex proposals, authors must write a Cardano Problem Statement (CPS) as defined in CIP-9999 and link to it as the `Motivation`. -->

Patterns like
```uplc
(lam a (lam b (lam c <body>)))
```
are increasingly common in uplc contracts.

These are not only used to represent functions with arity greater than 1, but also to destructure SoP enocded values, or to introduce multiple "letted" values in scope (witch in plutus v3 is done using a case/constr).

## Specification
<!-- The technical specification should describe the proposed improvement in sufficient technical detail. In particular, it should provide enough information that an implementation can be performed solely on the basis of the design in the CIP. This is necessary to facilitate multiple, interoperable implementations. This must include how the CIP should be versioned, if not covered under an optional Versioning main heading. If a proposal defines structure of on-chain data it must include a CDDL schema in its specification.-->

This CIP proposes the `func` node, which is encoded with arity n, intended to have the same effect as n consecutive lambda nodes.

The new node should have tag `10` (in binary: `1010`).

Once encountered, other 4 bits are expected indicating the arity of the function node.

Because we already have the `lam` node to indicate a function with arity 1, and `delay` can be interpreted as arity 0, the 4 arity bits can specify arity between 2 and 17 inclusive on both sides.

Encoding any arity greater than 17 will require at least 2 nodes,
for example arity 18 can be encoded as `(func 17 a b c ... (lam r <body>))`,
and arity 19 can be encoded as `(func 17 a b c ... (func 2 r s <body>))`.

## Rationale: how does this CIP achieve its goals?
<!-- The rationale fleshes out the specification by describing what motivated the design and what led to particular design decisions. It should describe alternate designs considered and related work. The rationale should provide evidence of consensus within the community and discuss significant objections or concerns raised during the discussion.

It must also explain how the proposal affects the backward compatibility of existing solutions when applicable. If the proposal responds to a CPS, the 'Rationale' section should explain how it addresses the CPS, and answer any questions that the CPS poses for potential solutions.
-->

The proposal does not impact backward compatibility by choice. The original lambda nodes are left in plutus both for backward compatibility and to save 4 bits on arity 1 functions.

## Path to Active

Included in Plutus V4.

### Acceptance Criteria
<!-- Describes what are the acceptance criteria whereby a proposal becomes 'Active' -->

Included in Plutus V4.

### Implementation Plan
<!-- A plan to meet those criteria or `N/A` if an implementation plan is not applicable. -->
N/A

<!-- OPTIONAL SECTIONS: see CIP-0001 > Document > Structure table -->

## Copyright
<!-- The CIP must be explicitly licensed under acceptable copyright terms. Uncomment the license you wish to use (delete the other one) and ensure it matches the License field in the header.

If AI/LLMs were used in the creation of the copyright text, the author may choose to include a disclaimer to describe their application within the proposal.
-->

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
<!-- This CIP is licensed under [Apache-2.0](http://www.apache.org/licenses/LICENSE-2.0). -->
