---
CIP: ?
Title: Coins Per UTxO Byte
Authors: Jared Corduan <jared.corduan@iohk.io>
Status: Draft
Type: Informational
Created: 2022-05-19
License: CC-BY-4.0
Requires: CIP-0028
---

## Simple Summary/Abstract

This CIP extends CIP-0028 to introduce a change to one of the Alonzo protocol parameters in the Babbage era, namely `lovelacePerUTxOWord`.
We propose to have this updateable parameter be based on bytes instead of words (eight bytes).

## Motivation

Since the Shelley era, there has been an minimum number of lovelace requirement for every unspent transaction output.
This requirement acts like a deposit, guarding the network from dust (the proliferation of small-valued unspent transaction outputs).
Initially it was a constant value, since the Shelley era UTxO were simple and quite uniform.
Starting in the Mary era, however, the constant value was replace with a
[formula](https://cardano-ledger.readthedocs.io/en/latest/explanations/min-utxo-mary.html)
to account for the variability in outputs that contained multi-assets.
The formula was [changed again](https://cardano-ledger.readthedocs.io/en/latest/explanations/min-utxo-alonzo.html)
in the Alonzo era.
Both the Mary and the Alonzo era formulas provide an upper bound on the size in memory of an unspent transaction output in the Haskell implementation.
We would like to simplify the formula to instead count the number of bytes in the CBOR serialization.

## Specification


### Rename

The name of the protocol parameter is actually `coinsPerUTxOWord` in the Haskell implementation.
It should be renamed to `coinsPerUTxOByte`.

### Translation from the Alonzo era to the Babbage era

At the moment that the hard fork combinator translates the Alonzo era ledger state to the Babbage era,
the current value of `coinsPerUTxOWord` will be converted to

```
⌈ coinsPerUTxOWord / 8 ⌉
```

### The new minimum lovelace calculation

In the Babbage era, unspent transaction outputs will be required to contain _at least_

```
|serialized_output| * coinsPerUTxOByte
```

many lovelace.

## Rationale

We would like the formula for the minimum lovelace in a unspent transaction output
be simpler and easier to reason about by all users of the Cardano network, while at
the same time accounting for the size of the output.

## Backwards compatibility

The [translation](#translation-from-the-alonzo-era-to-the-babbage-era) section
explains how we will transition from the `coinsPerUTxOWord` parameter to the `coinsPerUTxOByte` parameter.
Starting in the Babbage era, update proposals that want to modify `coinsPerUTxOByte` must bear in mind
that the measurement is in bytes, not words.

## Path to Active

As of the time of this writing, this CIP has been implemented, but not release, in the Cardano ledger.

## Copyright

This CIP is licensed under Apache-2.0
