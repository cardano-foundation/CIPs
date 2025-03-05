---
CIP: 1853
Title: HD (Hierarchy for Deterministic) Stake Pool Cold Keys for Cardano
Status: Proposed
Category: Wallets
Authors:
  - Rafael Korbas <rafael.korbas@vacuumlabs.com>
Implementors:
    - Vacuum Labs <https://vacuumlabs.com/>
Discussions:
  - https://github.com/cardano-foundation/CIPs/pull/56
  - https://forum.cardano.org/t/stake-pool-cold-keys-hd-derivation/43360
Created: 2020-12-14
License: CC-BY-4.0
---

## Abstract

[CIP-1852] establishes how Shelley-era hierarchical deterministic (HD) wallets should derive their keys. This document is a follow-up of this CIP specifying how stake pool cold keys should be derived.

## Motivation: why is this CIP necessary?

(Hierarchical) deterministic derivation of stake pool cold keys enables their restorability from a seed and most importantly, their management on hardware wallet devices. This in turn mitigates man-in-the middle attacks to which pool operators would otherwise be vulnerable if they managed their stake pool cold keys on a device not specifically hardened against alteration of the data to be signed/serialized without operator's explicit consent.

## Specification

Using `1853'` as the purpose field, we define the following derivation path structure for stake pool cold keys:

```
m / purpose' / coin_type' / usecase' / cold_key_index'
```

Example: `m / 1853' / 1815' / 0' / 0'`

Here the `usecase` is currently fixed to `0'`.

Given that stake pool cold keys are cryptographically the same as wallet keys already covered in CIP-1852, the master node and subsequent child keys derivation **MUST** be implemented in the same way as specified for wallets in CIP-1852.

## Rationale: how does this CIP achieve its goals?

### Why introducing a new purpose?

Stake pools are not wallets and the core concept of "accounts" is not applicable to them, nor are they supposed to be related to a user's wallet in any meaningful way. Therefore treating stake pool cold keys as another "chain" within CIP-1852 specification would rather be a deviation from CIP-1852 than its logical extension. Hence we establish a separate purpose and path structure for stake pool cold keys, having their specifics and differences from standard "wallet" keys in mind.

### Why keeping `coin_type` in the path?

`coin_type` is kept in order to remain consistent with the "parent" CIP-1852 and also to leave space for the possibility that some Cardano hard-fork/clone in the future would reuse this specification to derive their own stake pool cold keys.

### `usecase` field

Similarly as we have the `chain` path component in CIP-1852 paths for different types of wallet keys, it's plausible that in the future, there could be multiple varieties of stake pools. One such example of a possible future extension of this CIP could be pools managed by a group of operators instead of a single operator, for which a separate set of stake pool cold keys, driven by this parameter, could make sense both from logical and security perspective.

### Hardened derivation at `cold_key_index`

Each stake pool is supposed to be managed separately so there is currently no incentive to connect them via a parent public key.

### Hardened derivation at `usecase`

We chose hardened derivation at the usecase index as there is no incentive to mix the stake pool cold keys with other potential usecases and if there was such incentive, it would most likely be more appropriate to create a separate usecase/purpose for that.

## Path to Active

### Acceptance Criteria

- [ ] Standardisation of this derivation path among three wallets as of the Shelley ledger era.
    - Ledger App Cardano <https://github.com/LedgerHQ/app-cardano>

### Implementation Plan

- [x] Common agreement on the above Motivation, Rationale and Specification during the planning of Cardano's Shelley release.

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).

[CIP-1852]: https://github.com/cardano-foundation/CIPs/blob/master/CIP-1852
