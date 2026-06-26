---
CIP: ?
Title: Transaction Fee-Change Field
Category: Ledger
Status: Proposed
Authors:
    - Polina Vinogradova <polina.vinogradova@iohk.io>
    - Will Gould <will.gould@iohk.io>
Implementors:
  - Input Output Engineering <https://iohk.io>
Created: 2026-06-26
License: CC-BY-4.0
---

## Abstract

This proposal discusses a mechanism for users to receive change for fee overpayment. 
The amount of change given is the difference between the minimum fee calculated for that 
transaction and the fee specified by the transaction. The change is sent to the 
reward address specified by that transaction. 

## Motivation: why is this CIP necessary?

Cardano currently collects the exact fee a transaction declares; there is no
mechanism for the protocol to return any portion of it to the submitter. Future fee
schemes may require such a mechanism.

Two concrete drivers are dynamic and tiered pricing models, in either of which 
a transaction may end up being processed
at a lower effective fee than originally stated. For example, this may happen because network demand
at the time of inclusion was lower than anticipated, or because the transaction's
specified expected delay period was exceeded before it was entered into a block.
In both cases, monetary compensation of part of the stated transaction fee may be owed. 
That is, the transaction commits to an
upper bound on what it is willing to pay, and change is given when the actual
collected fee is lower. The mechanism we propose in this CIP facilitates this.

This CIP specifies that the amount of change is calculated as the difference between 
the minimum fee and the transaction fee. This is a placeholder calculation, 
since there is no concrete formula available for possible future fee pricing mechanisms. 
The goal here is solely to establish the on-chain channel through which change can be
returned, so that the transaction body format does not need to be revisited once the
fee calculation is agreed upon.

There is precedent for a fee change mechanism in 
[Ethereum](https://eips.ethereum.org/EIPS/eip-1559), which has been, to 
some extent, the inspiration for the mechanism discussed in this CIP.

## Specification

### New transaction body field

A new optional field `feeChangeAddr` is added to the transaction body `TxBody` :

```
feeChangeAddr : Maybe RwdAddr
```

Where the reward (staking) address `feeChangeAddr` is the address to which the
compensation is credited. Using a reward address rather than a payment address
ensures the credit is handled through the existing rewards-withdrawal mechanism
and does not need to be reflected in a transaction output. Making the change 
address optional allows for backwards compatibility. 

### Ledger rule changes

#### Transaction validity

No additional signing requirements are imposed, as it is not mandatory for a 
user to output fee change into an address they own. 

**`feeChangeAddr` provided.** When a transaction provides 
this address, the following changes to ledger rules are required :

(1) To the *produced* calculation :

- the `txb .txFee` summand is replaced with `collectedFee pp utxo tx`

`collectedFee pp utxo tx = minfee pp utxo tx`

- a summand is added `feeChange pp utxo txb`, where we define 

`feeChange pp utxo txb = txb .txFee - minfee pp utxo tx`

(2) In the `UTXO` rule, we add a check 

- `0 ≤ feeChange pp utxo txb`

(3) We update the reward on the ledger state with this calculation, 
which is performed after all other ledger state changes resulting from 
transaction processing :

```agda
rwds' = rwds ∪⁺ ❴ feeChangeAddr , feeChange ❵ᵐ
```
**`feeChangeAddr` not provided.** When this value is `feeChangeAddr = Nothing`, no changes 
to ledger rules are required.


#### Fee accounting

Note that both calculations `collectedFee` and `feeChange` would be replaced 
by whichever rules for calculating fee change will be required by future
fee calculation changes.

#### `TxInfo`

It is important to note that no changes to `TxInfo` are required. 

The reason for this is that all Plutus scripts
should be blind to the fee change provided. This value is not fixed at the time of 
transaction construction and therefore cannot be used to predict the outcome of 
script validation at the time of construction. Note here that this change may 
in the future make it 
impossible for a script to itself check the produced/consumed balance, as 
the `feeChange` calculation in future eras may require data not included 
in `TxInfo` (e.g. if it depends on how long the transaction was waiting in 
the mempool).

#### CBOR encoding

The `feeChange` field is encoded in the transaction body map under a new key `x`.
The key `x` is the next available field number in the era into which it is added.
The value will be encoded as `bytes` representing the reward address.

```
transaction_body =
  { ..existing fields..
  , ? x : reward_account   ; feeChange
  }
```


## Rationale: How does this CIP achieve its goals?

### Choice of reward address over payment address

Reward addresses are already used for staking rewards and pool
deposits, making them a natural fit.
Crediting a reward address ensures the UTxO set changes remain predictable 
locally. 

### Opt-in via optional field

By making `feeChange` optional, this CIP imposes zero overhead on transactions that
do not wish to participate in the compensation mechanism. It also means the change
can be deployed before the change calculation formula is finalized, without any
observable effect on current transactions. Finally, it allows backwards compatibility 
with transactions from previous eras.

### Alternatives considered

- **Implicit refund into the change output**: rejected because it requires the ledger
  to locate and modify a specific UTxO output, which would compromise the deterministic
   validation of Plutus scripts
- **Fixed portion of fee refunded**: rejected because the correct amount depends
  on fee dynamics that are not yet fully specified.

## Path to Active

### Acceptance criteria

- [ ]  This CIP has been communicated to, reviewed by, and agreed upon by a representative group of community members
- [ ]  All major concerns have been addressed

### Implementation plan

1. Update the formal ledger specification (`TxBody`, UTXO rule)
2. Update node ledger implementation/CDDL once the formal spec is stable.
3. Update wallet SDKs and tooling.
4. Test net deployment 
5. Main net deployment 

## References

- [1] Kiayias, A.; Koutsoupias, E.; Lazos, P.; Stouras, G.
  *Tiered Mechanisms for Blockchain Transaction Fees.* arXiv:2304.06014, 2023

## Copyright

This CIP is licensed under
[CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
