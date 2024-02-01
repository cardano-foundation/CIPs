---
CIP: xxx
Title: Transaction Inputs as List
Category: Plutus
Status: Proposed
Authors:
  - Jonathan Rodriguez <info@anastasialabs.com>
Implementors: []
Discussions:
  - https://github.com/cardano-foundation/CIPs/pull/?
Created: 2024-02-01
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
We propose the introduction of a new structure for transaction inputs aimed at significantly enhancing the execution efficiency of Plutus contracts. 

This CIP facilitates explicit ordering of transaction inputs, diverging from the current state. This explicit ordering enables seamless arrangement of input scripts intended for utilization within the application's business logic. 

Consequently, this implementation alleviates the necessity to set an index list through the redeemer to gather the required inputs from the transaction. Additionally, it mitigates the computational overhead associated with ensuring the uniqueness of the index list.

## Motivation: why is this CIP necessary?
<!-- A clear explanation that introduces the reason for a proposal, its use cases and stakeholders. If the CIP changes an established design then it must outline design issues that motivate a rework. For complex proposals, authors must write a Cardano Problem Statement (CPS) as defined in CIP-9999 and link to it as the `Motivation`. -->
According to the Alonzo CDDL [Transaction body](https://github.com/IntersectMBO/cardano-ledger/blob/c158b4298d34cdef3340e600739422ca72a713cd/eras/alonzo/impl/cddl-files/alonzo.cddl#L55), the inputs of a transaction body are represented as a set, leading to the inputs being ordered lexicographically by the ledger.

The primary issue with strictly ordering inputs lexicographically is that many projects must resort to passing index numbers through the redeemer to select the correct input from the transaction inputs. This practice introduces inefficiencies and potential vulnerabilities to vector attacks if the passing of indexes through the redeemer is incorrectly implemented.

Currently, most projects are transitioning away from housing all business logic within the spending validator, as it is executed for every unspent transaction output (UTxO). This can be illustrated as follows:
```mermaid
graph LR
    TX[ Transaction ]
    subgraph Spending Script
    S1((Input 1))
    S2((Input 2))
    S3((Input 3))
    end
    S1 -->|validates \n Business logic| TX
    S2 -->|validates \n Business logic| TX
    S3 -->|validates \n Business logic| TX
    TX --> A1((Output 1))
    TX --> A2((Output 2))
    TX --> A3((Output 3))
```

Consequently, projects are now relying on implementing minting policies or staking validators to validate their business logic. This dramatically reduces the script execution of the spending validator and increases the throughput of their applications.

```mermaid
graph LR
    TX[ Transaction ]
    subgraph Spending Script
    S1((UTxO 1))
    S2((UTxO 2))
    S3((UTxO 3))
    end
    S1 -->|validates \n StakingCredential| TX
    S2 -->|validates \n StakingCredential| TX
    S3 -->|validates \n StakingCredential| TX
    ST{{Staking Script}} -.-o |validates Business Logic| TX
    TX --> A1((Output 1))
    TX --> A2((Output 2))
    TX --> A3((Output 3))
```
However, in this approach, the minting or staking validator requires a list of indices to be passed from the redeemer to select the correct inputs within the transaction input list. One vulnerability of this implementation is that the list of indices must be unique to prevent double validation, which could allow someone to unlock inputs without proper validation.

To mitigate such attacks, one approach is to compute the uniqueness of this index list, but this can result in costly computations if the business logic requires validation of a large number of inputs. A simpler approach to mitigate these hacks is to offer flexibility by explicitly allowing the order of inputs to be determined by a transaction builder instead of the ledger. This eliminates the need to pass indexes through the redeemer.

## Specification
<!-- The technical specification should describe the proposed improvement in sufficient technical detail. In particular, it should provide enough information that an implementation can be performed solely on the basis of the design in the CIP. This is necessary to facilitate multiple, interoperable implementations. This must include how the CIP should be versioned, if not covered under an optional Versioning main heading. If a proposal defines structure of on-chain data it must include a CDDL schema in its specification.-->
As per protocol specifications, the transaction body is structured as follows:
```
transaction_body =
 { 0 : set<transaction_input>    ; inputs
 , 1 : [* transaction_output]
 , 2 : coin                      ; fee
 , ? 3 : uint                    ; time to live
 , ? 4 : [* certificate]
 , ? 5 : withdrawals
 , ? 6 : update
 , ? 7 : auxiliary_data_hash
 , ? 8 : uint                    ; validity interval start
 , ? 9 : mint
 , ? 11 : script_data_hash       ; New
 , ? 13 : set<transaction_input> ; Collateral ; new
 , ? 14 : required_signers       ; New
 , ? 15 : network_id             ; New
 }
```

Specifically, the inputs are currently represented as a set:
```
0 : set<transaction_input>    ; inputs
```

The proposed solution suggests modifying the inputs to a list format:
```
0 : [* transaction_input]    ; inputs
```



## Rationale: how does this CIP achieve its goals?
<!-- The rationale fleshes out the specification by describing what motivated the design and what led to particular design decisions. It should describe alternate designs considered and related work. The rationale should provide evidence of consensus within the community and discuss significant objections or concerns raised during the discussion.

It must also explain how the proposal affects the backward compatibility of existing solutions when applicable. If the proposal responds to a CPS, the 'Rationale' section should explain how it addresses the CPS, and answer any questions that the CPS poses for potential solutions.
-->
The motivation behind this CIP stems from the observed limitations and inefficiencies associated with the current lexicographical ordering of transaction inputs. Currently, the strict lexicographical ordering necessitates the passing of index numbers through the redeemer to select the appropriate input, leading to potential inefficiencies and vulnerabilities to vector attacks.

To mitigate these issues, the proposed solution suggests transitioning from a set-based representation of transaction inputs to a list-based representation.

This CIP tries to revive the original draft [CIP-0051](https://github.com/cardano-foundation/CIPs/pull/231)

### Alternatives
#### 1. Retain the existing set-based representation with additional validation mechanisms: 

This approach involves maintaining the current set-based representation of transaction inputs while implementing additional validation mechanisms to guarantee the uniqueness of index lists.
However, it was determined that such approaches could introduce complexity and computational overhead

#### 2. Hash the spending outref and use it for datum tagging: 
  
This alternative suggests hashing the spending outref of the script input and employing it for datum tagging to enforce the uniqueness of outputs. However, this method introduces extra overhead to the datum structure.

## Path to Active

### Acceptance Criteria
<!-- Describes what are the acceptance criteria whereby a proposal becomes 'Active' -->
[] Fully implemented in Cardano.

### Implementation Plan
<!-- A plan to meet those criteria or `N/A` if an implementation plan is not applicable. -->

<!-- OPTIONAL SECTIONS: see CIP-0001 > Document > Structure table -->
[] Passes all requirements of both Plutus and Ledger teams as agreed to improve Plutus script efficiency and usability.


## Copyright
<!-- The CIP must be explicitly licensed under acceptable copyright terms.  Uncomment the one you wish to use (delete the other one) and ensure it matches the License field in the header:

<!-- This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode). -->
<!-- This CIP is licensed under [Apache-2.0](http://www.apache.org/licenses/LICENSE-2.0). -->

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
