---
CIP: 1852
Title: HD (Hierarchy for Deterministic) Wallets for Cardano
Status: Active
Category: Wallets
Authors:
  - Sebastien Guillemot <sebastien@emurgo.io>
  - Matthias Benkort <matthias.benkort@cardanofoundation.org>
Implementors: N/A
Discussions:
  - https://github.com/cardano-foundation/CIPs/pull/33
  - https://forum.cardano.org/t/cip1852-hd-wallets-for-cardano/41740
Created: 2019-10-28
License: CC-BY-4.0
---

## Abstract

Cardano extends the [BIP44](https://github.com/bitcoin/bips/blob/master/bip-0044.mediawiki) by adding new chains used for different purposes. This document outlines how key derivation is done and acts as a registry for different chains used by Cardano wallets.

## Motivation: Why is this CIP necessary?

For Cardano, we use a new purpose field `1852'` instead of `44'` like in BIP44. There are three main reasons for this:

1) During the Byron-era, `44'` was used. Since Byron wallets use a different algorithm for generating addresses from public keys, using a different purpose type allows software to easily know which address generation algorithm given just the derivation path (ex: given `m / 44' / 1815' / 0' / 0 / 0`, wallet software would know to handle this as a Byron-era wallet and not a Shelley-era wallet).
2) Using a new purpose helps bring attention to the fact Cardano is using `BIP32-Ed25519` and not standard `BIP32`.
3) Using a new purpose allows us to extend this registry to include more Cardano-specific functionality in the future

`1852` was chosen as it is the year of death of Ada Lovelace (following the fact that the `coin_type` value for Cardano is `1815` for her year of birth)

## Specification

Using `1852'` as the purpose field, we defined the following derivation path:

```
m / purpose' / coin_type' / account' / role / index
```

Example: `m / 1852' / 1815' / 0' / 0 / 0`

Here, `role` can be the following

| Name                              | Value | Description
| ---                               | ----- | ------------
| External chain                    | `0`   | Same as defined in [BIP44](https://github.com/bitcoin/bips/blob/master/bip-0044.mediawiki)
| Internal chain                    | `1`   | Same as defined in [BIP44](https://github.com/bitcoin/bips/blob/master/bip-0044.mediawiki)
| Staking Key                       | `2`   | See [CIP-0011](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0011/README.md)
| DRep Key                          | `3`   | See [CIP-0105](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0105/README.md)
| Constitutional Committee Cold Key | `4`   | See [CIP-0105](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0105/README.md)
| Constitutional Committee Hot Key  | `5`   | See [CIP-0105](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0105/README.md)

Wallets **MUST** implement this new scheme using the master node derivation algorithm from Icarus with sequential addressing (see [CIP3](https://cips.cardano.org/cips/cip3) for more information)

## Rationale: How does this CIP achieve its goals?

### Derivation style

Cardano does not use [BIP32](https://github.com/bitcoin/bips/blob/master/bip-0032.mediawiki) but actually uses [BIP32-Ed25519](https://input-output-hk.github.io/adrestia/static/Ed25519_BIP.pdf). The `-Ed25519` suffix is often dropped in practice (ex: we say the Byron release of Cardano supports [BIP44](https://github.com/bitcoin/bips/blob/master/bip-0044.mediawiki) but in reality this is BIP44-Ed25519).

The Byron implementation of Cardano uses `purpose = 44'` (note: this was already a slight abuse of notation because Cardano implements BIP44-Ed25519 and not standard BIP44).

There are two (incompatible) implementations of BIP32-Ed25519 in Cardano:

1) HD Random (notably used initially in Daedalus)
2) HD Sequential (notably used initially in Icarus)

The difference is explained in more detail in [CIP-0003](../CIP-0003).

### Future extensions

As a general pattern, new wallet schemes should use a different purpose if they intend to piggy-back on the same structure but for a different use-case (see for instance [CIP-1854](../CIP-1854)).

The `role` can however be extending with new roles so long as they have no overlapping semantic with existing roles. If they do, then they likely fall into the first category of extension and would better be done via a new purpose.

## Path to Active

### Acceptance Criteria

- [x] Standardisation of this derivation path among all wallets as of the Shelley ledger era.

### Implementation Plan

- [x] Common agreement on the above Motivation, Rationale and Specification during the planning of Cardano's Shelley release.

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
