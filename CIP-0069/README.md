---
CIP: 69
Title: Script Signature Unification
Category: Plutus
Authors:
  - Maksymilian 'zygomeb' Brodowicz <zygomeb@gmail.com>
Implementors: N/A
Status: Proposed
Discussions:
  - https://github.com/cardano-foundation/CIPs/pull/321
Created: 2022-08-23
License: CC-BY-4.0
---

## Abstract

This CIP unifies the arguments given to all types of Plutus scripts currently available (spending, certifying, rewarding, minting) by removing the argument of a datum.

For a while now every builder, myself included have struggled with the mutual dependency issue (two validators that need to know each other's hash) when designing dapps and it is widely considered a substantial barrier to safe protocols and one that limits our design space considerably.

The exact change would be to have every validator take as argument the redeemer and then the script context. Datums, only relevant to locking validators would be able to be provided by either looking them up in the ScriptContext or by extending the `Spending` constructor of `TxInfo` to carry `(TxOutRef, Datum)`.

## Motivation: why is this CIP necessary?

As it stands the scripts being made on cardano often suffer this problem, and the tokens usually are made to be able to be minted at any time. This leads to further checks being made on the frontend and further fragilitiy of the systems we create. When a mutual dependency arises we are forced to choose which script gets to statically know what's the hash of the other, and which has to be provided 'during runtime'.

- Use Case 1: Minting validator checks datum given to spending validator. The spending validator requires the token be present as witness of the datum's correctness.

- Use Case 2 (taken from Optim's Liquidity Bonds): Unique NFT is minted to give a unique identifier to a loan, that then gets reused by Bond Tokens. The spending validators require that NFT be present.

- Use Case 3 (taken from Minswap's Dex V1): NFT is minted for the same reason as above. It allows a minting policy to later mint LP tokens with that unique id token name.

We see a similar pattern repeating over and over again as witnessed by dapp developers and auditors alike. By allowing the multi-purpose policies (spending and any other) we increase the security of Cardano by giving us more confidence and allowing to design protocols that have their architecture driven by Cardano's features, not limited by Cardano's language.

This primarily manifests in the ability to use a single validator for both minting and spending but the proposed solution makes it possible to use one validator for any and all purposes at once.

## Specification

### Removing the datum argument

All the script purposes have a form of `Redeemer -> ScriptContext -> a` except the `Spending` one.
It has the following form: `Datum -> Redeemer -> ScriptContext -> a`. This is enforced by the Cardano ledger.

We modify the general signature to be `ScriptArgs -> ScriptContext -> a`.

```hs
data ScriptArgs =
    RedeemerOnly Redeemer
  | RedeemerAndDatum Redeemer Datum
```

## Rationale: how does this CIP achieve its goals?

Unifying of the script signature is a very elegant solution to the problem, streamlining the experience of developing on cardano.
Given that accessing the datum is almost always made by a spending script, it makes sense to introduce that argument back to the `ScriptPurpose` that now plays a more important role.
It begs the question if it should be added as an argument to all validators, to further emphasize that fact.

## Backwards compatibility

This change is not backwards compatible; it must be introduced in a new Plutus language version.
Node code must be modified.

## Path to Active

### Acceptance Criteria

- [ ] The change has been implemented in the Plutus codebase, integrated in the ledger and released through a hard-fork.

### Implementation Plan

None.

## Copyright

This CIP is licensed under Apache-2.0
