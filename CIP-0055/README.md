---
CIP: 55
Title: Protocol Parameters (Babbage Era)
Status: Active
Category: Ledger
Authors:
  - Jared Corduan <jared.corduan@iohk.io>
Implementors:
  - IOG
Discussions:
  - https://github.com/cardano-foundation/CIPs/pull/265
Created: 2022-05-19
License: Apache-2.0
---

## Abstract

This CIP extends CIP-0028 to introduce a change to one of the Alonzo protocol parameters in the Babbage era, namely `lovelacePerUTxOWord`.
We propose to have this updateable parameter be based on bytes instead of words (eight bytes).
Additionally, two Alonzo era protocol parameters were removed, namely the decentralization parameter and the extra entropy parameter.

## Motivation: Why is this CIP necessary?

### Lovelace Per UTxO Byte

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

### Transitional Praos

Two Alonzo era protocol parameters need to be removed for the Babbage era, since they relate to `TPraos`.
Transitional Praos (named `TPraos` in the code base) is the addition of two features to
[Praos](https://iohk.io/en/research/library/papers/ouroboros-praosan-adaptively-securesemi-synchronous-proof-of-stake-protocol/),
which were added to provide a smooth transition from
[Ouroboros-BFT](https://iohk.io/en/research/library/papers/ouroboros-bfta-simple-byzantine-fault-tolerant-consensus-protocol).
In particular, Transitional Praos included an overlay schedule which could be tuned by the `d` parameter
(`d == 1` means that all the blocks are produced by the BFT nodes, `d == 0` means that none of them are).
It also included a way of injecting extra entropy into the epoch nonce.
The extra entropy feature was used precisely once, and was
[explained wonderfully](https://iohk.io/en/blog/posts/2021/03/29/the-secure-transition-to-decentralization)
by one of the original authors of the Praos paper.

The Babbage era removes both of the "transitional" features of TPraos, rendering the decentralization parameter
and the extra entropy parameter useless.

## Specification

The removal of the decentralization parameter and the extra entropy parameter is self explanatory.
We now describe the specification of the `coinsPerUTxOByte` parameter.

### Rename

The name of the protocol parameter is actually `coinsPerUTxOWord` in the Haskell implementation.
It should be renamed to `coinsPerUTxOByte`.

### Translation from the Alonzo era to the Babbage era

At the moment that the hard fork combinator translates the Alonzo era ledger state to the Babbage era,
the current value of `coinsPerUTxOWord` will be converted to

```
⌊ coinsPerUTxOWord / 8 ⌋
```

### The new minimum lovelace calculation

In the Babbage era, unspent transaction outputs will be required to contain _at least_

```
(160 + |serialized_output|) * coinsPerUTxOByte
```

many lovelace. The constant overhead of 160 bytes accounts for the transaction input
and the entry in the UTxO map data structure (20 words * 8 bytes).

## Rationale: How does this CIP achieve its goals?

We would like the formula for the minimum lovelace in a unspent transaction output
be simpler and easier to reason about by all users of the Cardano network, while at
the same time accounting for the size of the output.

### Backwards compatibility

The [translation](#translation-from-the-alonzo-era-to-the-babbage-era) section
explains how we will transition from the `coinsPerUTxOWord` parameter to the `coinsPerUTxOByte` parameter.
Starting in the Babbage era, update proposals that want to modify `coinsPerUTxOByte` must bear in mind
that the measurement is in bytes, not words.

The two protocol parameters that have been removed, `d` and `extraEntropy`, can no longer be used
in protocol parameter updates.

## Path to Active

### Acceptance Criteria

- [x] The Babbage ledger era is activated.
- [x] Documented parameters have been in operational use by Cardano Node and Ledger as of the Babbage ledger era.

### Implementation Plan

- [x] Babbage ledger era parameters are deemed correct by working groups at IOG.

## Copyright

This CIP is licensed under [Apache-2.0](https://www.apache.org/licenses/LICENSE-2.0).
