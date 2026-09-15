---
CIP: 192
Title: Transaction Fee-Change Field
Category: Ledger
Status: Proposed
Authors:
    - Polina Vinogradova <polina.vinogradova@iohk.io>
    - Will Gould <will.gould@iohk.io>
Implementors:
  - Input Output Engineering <https://iohk.io>
Discussions:
  - Tiered Pricing repo internal discussion: https://github.com/input-output-hk/tiered-pricing/pull/36
  - Original PR: https://github.com/cardano-foundation/CIPs/pull/1218
Created: 2026-06-26
License: CC-BY-4.0
---

## Abstract

This proposal discusses a mechanism for users to receive change for fee overpayment. 
The amount of change given is the difference between the minimum fee calculated for that 
transaction and the fee specified by the transaction. The change is sent to the 
account address specified by that transaction. 

## Motivation: Why is this CIP necessary?

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

A new optional field `feeChangeAccount` is added to the transaction body `TxBody` 

```
feeChangeAccount : Maybe AccountAddress
```

Where the `AccountAddress` in `feeChangeAccount` is the address of an account to which the
compensation is credited. Using an account address rather than a payment address
ensures the credit is handled through the account based mechanism introduced in CIP-159
and does not need to be reflected in a transaction output. Making the change 
address optional allows for backwards compatibility. 

### Ledger rule changes

#### Transaction validity

No additional signing requirements are imposed, as it is not mandatory for a 
user to output fee change into an address they own. 

**`feeChangeAccount` provided.** When a transaction provides 
this address, the following changes to ledger rules are required :

(1) To the *produced* calculation :

- the `txfee` summand is replaced with `collectedFee pp utxo tx`

`collectedFee pp utxo tx = minfee pp utxo tx`

- a summand is added `feeChange pp utxo txb`, where we define 

`feeChange pp utxo txb = txfee - collectedFee pp utxo tx`

(2) `minfee pp utxo tx` goes into the fee pot (instead of `txfee`, as before)

(3) `collectedFee pp utxo tx - minfee pp utxo tx` goes into the treasury (`0` in this CIP)

(4) `feeChangeAccount` is checked to be registered

(5) After processing all other account-based operations by the transaction,
we update the account balance with account address `feeChangeAccount` by 
increasing it by `feeChange pp utxo txb`

Note that `feeChange ≥ 0` follows from the existing minimum-fee rule.



**`feeChangeAccount` not provided.** When this value is `feeChangeAccount = Nothing`

(1) The `minfee pp utxo tx` goes into the fee pot

(2) The entire rest of the specified fee, i.e. `txfee tx - minfee pp utxo tx` goes into the treasury.


**Collateral collection** In the case that Phase-2 validation fails, and only collateral 
is collected, no changes are necessary. Any overpayment goes to the fee pot as in the 
previous eras. The incentives for users to write only validating scripts remain 
aligned.


#### Fee accounting

Note that both calculations `collectedFee` and `feeChange` would be replaced 
by whichever rules for calculating fee change will be required by future
fee calculation changes.

#### `TxInfo`

No changes to `TxInfo` are required. 

#### Plutus scripts

This change will require a new version of Plutus to be released. It will also require 
that old-version Plutus scripts are not allowed to be run on transactions that provide 
a non-`Nothing` account address `feeChangeAccount`.

As in prior eras, all Plutus scripts
should be blind to any data not fixed at the time of transaction construction, including 
the fee change provided (i.e. `txInfoFee` is still `txfee`). The change provided will be finalized at the time of block construction. So, the `feeChange` amount cannot be used to predict the outcome of 
script validation at the time of construction. 
This change to the ledger also makes it
impossible for a script to itself check the produced/consumed balance, which we 
discuss briefly in [Tooling](#tooling).


#### CBOR encoding

The `feeChangeAccount` field is encoded in the transaction body map under a new key `x`.
The key `x` is the next available field number in the era into which it is added.
The value will be encoded as `bytes` representing the account address.

```
transaction_body =
  { ..existing fields..
  , ? x : account_address   ; feeChangeAccount
  }
```

## Rationale: How does this CIP achieve its goals?

### Choice of account address over payment address

Account addresses are already used for staking rewards and pool
deposits, and crucially for CIP-159 making them a natural fit.
Crediting an account ensures the UTxO set changes remain predictable 
locally. Most importantly accounts do not have any minimal deposit requirement, like minUTxO, thus change returned can be as low as 1 lovelace.

### Opt-in via optional field

By making `feeChangeAccount` optional, this CIP imposes zero overhead on transactions that
do not wish to participate in the compensation mechanism. It also means the change
can be deployed before the change calculation formula is finalized, without any
observable effect on the assessment of validity of current transactions. Finally, it allows backwards compatibility 
with transactions from previous eras.


#### Tooling

Most tooling support for Plutus smart contracts will require updates. Support for a new version of 
Plutus will be required. Moreover, scripts will have to be upgraded to account for the possibility 
that they may have access only to incomplete data about asset relocation, and be unable to 
reconstruct a local preservation of value check 
for the transaction. This is because they will not have access to the amount of change given to 
the account address (a value not necessarily predictable at the time of transaction construction).

### Alternatives considered

- **Refund amount specified by the block producer**: We could add a new field `changeAmount : Coin` 
  to the transaction, instead of a transaction body, similar to the `isValid` flag. This field 
  can be modified by the block producer at the time of block construction to reflect the 
  correctly calculated change amount. This may be a valuable addition for for use by tools 
  in the ecosystem, however, it will not necessarily 
  make a difference to node safety or functionality. 
- **Implicit refund into the change output**: rejected because it requires the ledger
  to locate and modify a specific UTxO output, which would compromise the deterministic
   validation of Plutus scripts
- **Fixed portion of fee refunded**: rejected because the correct amount depends
  on fee dynamics that are not yet fully specified.

## Path to Active

### Acceptance criteria

- [ ] Ledger changes live on Mainnet and included in a hard fork.
- [ ] Latest version of `cardano-cli` supports fee change specification by default.
- [ ] At least 2 mainstream Cardano wallets support fee change specification.

### Implementation plan

- [x] Agreement upon this CIP by a representative group of community members
- [ ] Update the formal ledger specification (`TxBody`, UTXO rule).
- [ ] Update node ledger implementation/CDDL once the formal spec is stable.
- [ ] Update wallet SDKs and tooling.
- [ ] Testnet deployment: addressing all major concerns
- [ ] Mainnet deployment: addressing all major concerns

## References

- [1] Kiayias, A.; Koutsoupias, E.; Lazos, P.; Stouras, G.
  *Tiered Mechanisms for Blockchain Transaction Fees.* arXiv:2304.06014, 2023

## Copyright

This CIP is licensed under
[CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
