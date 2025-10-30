---
CIP: ????
Title: Sign transaction IDs together with guards
Status: Proposed
Category: Ledger
Authors:
    - Polina Vinogradova <polina.vinogradova@iohk.io>
    - Nicolas Henin <nicolas.henin@iohk.io>
Implementors: []
Discussions:
    - https://github.com/cardano-foundation/CIPs/pull/1110
Created: 2025-10-29
License: CC-BY-4.0
---

## Abstract
We propose the following change to the ledger signature checking mechanism : instead of signing just the transaction ID, users
will now be required to sign the hash of the pair of (i) transaction ID and (ii) the hash of the guards listed in the transaction body.
This way, key holders will have no need to inspect the transaction they are signing in 
order to be sure that the transaction satisfied its guards (if posted on-chain). 

## Motivation: why is this CIP necessary?

This CIP (which depends on CIP-0118) serves both a practical and a conceptual purpose.

**Conceptually :** In recent years, intent-centric ledger models have been gaining a lot of momentum (e.g. Anoma, Khalani, CoW Swap, UniswapX, etc.).
There are many benefits to intent-centric design, not the least of which is that users do not need to care about the details of 
how their intent is fulfilled. In the case of Cardano, this would be the details of the transaction that fulfills it. Cardano 
is already moving towards intent-based design in its plan to introduce Nested Transactions in CIP-0118. CIP-0118 suggests that 
intents are expressed as sub-transactions, and a complete batch (i.e. a fully valid top-level transaction) fulfills a given 
sub-transaction's intent. This CIP takes this a step further : intents can be expressed as smart contracts, further distancing 
users from the need to be concerned with how exactly their intents are fulfilled, as long as they satisfy the constraints they 
specify using a smart contract script. 

The functionality of expressing an intent as a guard script (i.e. a Plutus script that 
is required to be executed by a transaction) is already part of CIP-0118. This CIP merely introduces a conceptual separation of 
intent and the transaction that satisfies it. That is, by signing an intent-transaction pair ,
a user gets assurance that the transaction satisfies it (assuming it ends up being validated by the ledger) without ever 
having to inspect the transaction.

**Practically :** The practical need for this stems from an intent-based ultra-light client design that is currently in the progress.
Such a light client has the capacity to submit an intent in the form of a script, but includes a requirement that it 
does not inspect the transaction 
that is constructed to solve it. We require a way to guarantee to such a client that their intent is solved by the transaction 
they sign (in the case that the transaction is validated by the ledger and posted on-chain).


## Specification

### Ledger Changes 

During transaction deserialization, the `MemoBytes` mechanism (an abstraction for a data type that encodes its own serialization) will be 
used to store the bytes of the CDDL field containing the guards of the transaction. 
The following values will be computed in the process of transaction processing : 

- `guardsHash`, which will be computed by hashing the bytes of the guards, and 
- `txidAndGuards`, which will be computed by hashing the concatenation `(txid ++ guardsHash)`

Signature checking will now check that each key signed `txidAndGuards`.

### CDDL

No change necessary.

### Nested Transactions

It appears that there are no special cases required for sub- or top-level- transactions. In both cases, 
all signatures will be checked on data constructed using the mechanism described above.

### Plutus 

Plutus scripts are not able to see the signatures on a transaction, only the signing keys. 
It appears that this change can be implemented without requiring a new version of Plutus.

### CLI

To support this change, the CLI will have to be modified to implement the new signing strategy.

### Backwards Compatibility

This change will be best suited for a hard fork (e.g. alongside Nested Transactions) that already does not have backwards compatibility 
since it will not itself be backwards compatible. 

## Future Intent DSL Development

The work described in this section is not part of the proposal being made here, but rather is a future outlook on 
how intents could function using this feature. 

A Plutus script is both hard to compose and hard to parse into instructions about what is required of a 
transaction. To address this, we envision relying on very narrow-domain DSLs, each tailored to only a specific 
usecase. The idea is to have as few as one or two expression constructors, such as for the case of sending funds 
from wallet to wallet:

`SendMoney : List KeyHash x Value x Address x Address -> Exp`

Then, an expression `exp` in this DSL would be compiled to a Plutus script `scr` and the pair `(exp , scr)`
would be sent to an intent solver. The solver would use `exp` to build a transaction with ID `txid` (which includes 
`scr` as one of its guards). The solver would 
then check that the resulting transaction satisfies the script `scr` by validating it against the current ledger state (except 
for checking the clients's signature, which is not yet attached).
The client will then get back `hash (txid ++ hash scr)` to sign. 

## Rationale: how does this CIP achieve its goals?

The goal of this CIP is to describe a mechanism for intent validation without transaction inspection. That is, a user knows that a transaction 
they signed (according to the new signing mechanism) either satisfies their intent (expressed as a guard script)
or is discarded - without the need to inspect the transaction body. 
We have specified the required signing mechanism and rule 
changes required to ensure this, and explained why this is guaranteed above.

### Alternatives 

We are (in parallel to making this CIP) working on a ZK-based solution that will allow proving to users that a given 
transaction ID corresponds to a transaction that includes 
in its list of guard scripts a specific script. Using blind signatures, our benchmarks show that generating the 
necessary proof in an average case may take ~5s
(link to paper will be provided when it becomes public). This is significantly slower than performing two additional 
hashing operations. 

## Path to Active

### Acceptance Criteria
- [ ] Rule and TxBody structure changes are implemented in the ledger repo and included in an upcoming major hard fork.
      
### Implementation Plan
- [ ] Passes all requirements of both Plutus and Ledger teams as agreed to improve Plutus script efficiency and usability.
      
## Copyright
This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).

[CC-BY-4.0]: https://creativecommons.org/licenses/by/4.0/legalcode
[Apache-2.0]: http://www.apache.org/licenses/LICENSE-2.0