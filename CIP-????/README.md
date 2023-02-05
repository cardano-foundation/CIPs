---
CIP: ?
Title: Untyped UPLC Builtins
Category: Plutus
Status: Proposed
Authors:
    - Niels Mündler <n.muendler@posteo.de>
Implementors: []
Discussions:
    - https://github.com/cardano-foundation/cips/pulls/?
Created: 2023-02-05
License: CC-BY-4.0
---

<!-- Existing categories:

- Meta                   | For meta-CIPs which typically serves another category or group of categories.
- Reward-Sharing Schemes | For CIPs discussing the reward & incentive mechanisms of the protocol.
- Wallets                | For standardisation across wallets (hardware, full-node or light).
- Tokens                 | About tokens (fungible or non-fungible) and minting policies in general.
- Metadata               | For proposals around metadata (on-chain or off-chain).
- Tools                  | A broad category for ecosystem tools not falling into any other category.
- Plutus                 | Changes or additions to Plutus
- Ledger                 | For proposals regarding the Cardano ledger
- Catalyst               | For proposals affecting Project Catalyst / the Jörmungandr project

-->

## Abstract
The Untyped Plutus Language Core has established itself as the target language for a host of emerging Smart Contract Languages.
These languages implement type safety in the following way: At compile time, types of variables are checked.
In the compiled output, type information is thus absent (and not required anymore, nor checked).
This proposal suggests to replace or enhance the set of builtin functions with builtin functions that are untyped i.e. their arguments
are just the arguments expected devoid of any type instantiations.
<!-- A short (\~200 word) description of the proposed solution and the technical issue being addressed. -->

## Motivation: why is this CIP necessary?
<!-- A clear explanation that introduces the reason for a proposal, its use cases and stakeholders. If the CIP changes an established design then it must outline design issues that motivate a rework. For complex proposals, authors must write a Cardano Problem Statement (CPS) as defined in CIP-9999 and link to it as the `Motivation`. -->
Many of the currently available UPLC builtin functions need to be forced between 1 and 3 times to get rid of type instantiations checked at a higher level language
of the toolstack (PLC), which most third party tools do not use.
Moreover, the forces do nothing more than burn cycles of nodes that evaluate contracts, since there is no actual type instantiation happening internally.
There is always demand to improve performance and reduce resource costs, which is achieved by this proposal.

## Specification
<!-- The technical specification should describe the proposed improvement in sufficient technical detail. In particular, it should provide enough information that an implementation can be performed solely on the basis of the design in the CIP. This is necessary to facilitate multiple, interoperable implementations. -->
For all existing UPLC Builtin Functions _x_ that require _n > 0_ forces for evaluation, this proposal suggests to implement the builtin function _x_
without any required forces.

There are two options for the implementation of this proposal.
Either the new functions are added to the set of available builtin functions or they replace the current functions.
This is up to discussion and shifts additional work to either the implementation of UPLC or the implementation of PLC.

Addition:
 - UPLC needs to support a more diverse set of operations, implying more resources needed for maintainance and secondary implementations

Replacement:
 - PLC will need to wrap builtin functions with delays internally to emulate the previous behaviour of the builtin functions


## Rationale: how does this CIP achieve its goals?
<!-- The rationale fleshes out the specification by describing what motivated the design and what led to particular design decisions. It should describe alternate designs considered and related work. The rationale should provide evidence of consensus within the community and discuss significant objections or concerns raised during the discussion.

It must also explain how the proposal affects the backward compatibility of existing solutions when applicable. If the proposal responds to a CPS, the 'Rationale' section should explain how it addresses the CPS, and answer any questions that the CPS poses for potential solutions.
-->
This proposal reduces the resources needed to evaluate builtin functions by removing the need to apply no-op force operations to them.

If the decision is to replace the builtin functions:
The resulting implementation will break backwardscompatability of implementing Plutus Smart Contracts.

## Path to Active

I need some advice on the following to sections. As I understand the specification and implementation of UPLC and PLC is currently under supervision of 

### Acceptance Criteria
<!-- Describes what are the acceptance criteria whereby a proposal becomes 'Active' -->

### Implementation Plan
<!-- A plan to meet those criteria. Or `N/A` if not applicable. -->


## Copyright
This CIP is licensed under [CC-BY-4.0]: https://creativecommons.org/licenses/by/4.0/legalcode
