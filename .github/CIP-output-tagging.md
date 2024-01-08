---
CIP: ?
Title: Tag / Redeemer field in TxOut
Category: Plutus
Status: Proposed
Authors:
    - Philip <info@anastasialabs.com>
Implementors: N/A
Discussions:
    - https://plutus.readthedocs.io/en/latest/reference/writing-scripts/common-weaknesses/double-satisfaction.html
Created: 2024-01-04
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

# Tag / Redeemer Field for TxOut

## Abstract
We propose to allow the attachment of arbitrary, temporary data to transaction outputs within the script context. This data, akin to redeemers in their operational context, is intended to be used exclusively during the execution of Plutus scripts and thus are not recorded by the ledger. This will facilitate a wide variety of smart contract design patterns, one of which can be used as a general solution for double satisfaction without sacrificing script composability.

## Motivation: why is this CIP necessary?
Often smart contract logic for most DApps involves associating arbitrary data with transaction outputs. Currently, there are a number of design patterns that are used to achieve this association, but each of these design patterns have significant drawbacks. The limitations of existing solutions have made a wide variety of DApps and design patterns infeasable in practice due to script budget constraints and high complexity of required code.  

## Specification
<!-- The technical specification should describe the proposed improvement in sufficient technical detail. In particular, it should provide enough information that an implementation can be performed solely on the basis of the design in the CIP. This is necessary to facilitate multiple, interoperable implementations. This must include how the CIP should be versioned. If a proposal defines structure of on-chain data it must include a CDDL schema in it's specification.-->
We extend transaction witness set with a new list of arbitrary data associated with transaction outputs (`output_tags`).

### Script context

Scripts are passed information about transactions via the script context.
We propose to augment the script context to include some information about reference scripts.

Changing the script context will require a new Plutus language version in the ledger to support the new interface.
The change is: a new optional field is added to outputs and inputs to represent reference scripts.
Reference scripts are represented by their hash in the script context.

The interface for old versions of the language will not be changed.
Scripts with old versions cannot be spent in transactions that include reference scripts, attempting to do so will be a phase 1 transaction validation failure.

### CDDL

The CDDL for the transaction witness set will change as follows to reflect the new field.
```
transaction_witness_set =
  { ? 0: [* vkeywitness ]
  , ? 1: [* native_script ]
  , ? 2: [* bootstrap_witness ]
  , ? 3: [* plutus_v1_script ]
  , ? 4: [* plutus_data ]
  , ? 5: [* redeemer ]
  , ? 6: [* plutus_v2_script ] ; New
  }
```
TODO: can we use a more generic type that allows _any_ script in a forwards-compatible way?




## Rationale: how does this CIP achieve its goals?
<!-- The rationale fleshes out the specification by describing what motivated the design and what led to particular design decisions. It should describe alternate designs considered and related work. The rationale should provide evidence of consensus within the community and discuss significant objections or concerns raised during the discussion.

It must also explain how the proposal affects the backward compatibility of existing solutions when applicable. If the proposal responds to a CPS, the 'Rationale' section should explain how it addresses the CPS, and answer any questions that the CPS poses for potential solutions.
-->

## Path to Active

### Acceptance Criteria
<!-- Describes what are the acceptance criteria whereby a proposal becomes 'Active' -->

### Implementation Plan
<!-- A plan to meet those criteria. Or `N/A` if not applicable. -->

## Copyright
<!-- The CIP must be explicitly licensed under acceptable copyright terms. -->

[CC-BY-4.0]: https://creativecommons.org/licenses/by/4.0/legalcode
[Apache-2.0]: http://www.apache.org/licenses/LICENSE-2.0
