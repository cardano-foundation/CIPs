---
CIP: 3
Title: Wallet Key Generation
Status: Active
Category: Wallets
Authors:
    - Matthias Benkort <matthias.benkort@cardanofoundation.org>
    - Sebastien Guillemot <seba@dcspark.io>
Implementors:
    - Matthias Benkort <matthias.benkort@cardanofoundation.org>
    - Sebastien Guillemot <seba@dcspark.io>
Discussions:
    - https://github.com/input-output-hk/implementation-decisions/pull/18
    - https://github.com/cardano-foundation/cips/pull/33
    - https://github.com/cardano-foundation/cips/pull/76
    - https://github.com/cardano-foundation/cips/pull/132
Created: 2020-05-07
License: CC-BY-4.0
---

## Abstract

Many wallets utilize some way of mapping a sentence of words (easy to read and write for humans) uniquely back and forth to a sized binary data (harder to remember).

This document outlines the various mapping algorithms used in the Cardano ecosystem.

## Motivation: why is this CIP necessary?

The philosophy of cryptocurrencies is that you are in charge of your own finances. Therefore, it is very anti-thematic for wallet software to lock in a user by explicitly describing the algorithm used to derive keys for a wallet (both the master key and key derivation)

To this end, this document outlines all the relevant key generation algorithms used in the Cardano ecosystem.

## Specification

### Recovery Phrase (mnemonic) Generation

Conversion from a recovery phrase to entropy is the same as described in [BIP39](https://github.com/bitcoin/bips/blob/master/bip-0039/bip-0039-wordlists.md).

### Hierarchical Deterministic Wallets

In Cardano, hierarchical deterministic (abbrev. HD) wallets are similar to those described in [BIP-0032](https://github.com/bitcoin/bips/blob/master/bip-0032.mediawiki). Notably, we use a variation called [ED25519-BIP32](https://github.com/input-output-hk/adrestia/raw/bdf00e4e7791d610d273d227be877bc6dd0dbcfb/user-guide/static/Ed25519_BIP.pdf). A reference implementation can be found [here](https://docs.rs/ed25519-bip32/).

### Master Key Generation

The master key generation is the mean by which on turns an initial entropy into a secure cryptographic key.

More specifically, the generation is a function from an initial seed to an extended private key (abbrev. XPrv) composed of:

- 64 bytes: an extended Ed25519 secret key composed of:
  - 32 bytes: Ed25519 curve scalar from which few bits have been tweaked according to ED25519-BIP32
  - 32 bytes: Ed25519 binary blob used as IV for signing
- 32 bytes: chain code for allowing secure child key derivation

#### History

Throughout the years, Cardano has used different styles of master key generation:

| Name                                    | Used by         | Address prefix in Byron | Is deprecated? | Is Recommended? |
|-----------------------------------------|-----------------|-------------------------|----------------|-----------------|
| [Byron](./Byron.md)                     | Daedalus        | Ddz                     | Yes            | No              |
| [Icarus](./Icarus.md)                   | Yoroi, Daedalus | Ae2                     | No             | Yes             |
| [Icarus-Trezor](./Icarus.md)            | Trezor          | Ae2                     | No             | No              |
| [Ledger/BitBox02](./Ledger_BitBox02.md) | Ledger/BitBox02 | Ae2                     | No             | No              |

## Rationale: how does this CIP achieve its goals?

This CIP is merely to document the existing standards and not to provide rationales for the various methods used.

However, you can learn more at the following links:

- [Adrestia documentation](https://cardano-foundation.github.io/cardano-wallet/concepts/master-key-generation)
- [SLIP-0010](https://github.com/satoshilabs/slips/blob/master/slip-0010.md)
- [SLIP-0023](https://github.com/satoshilabs/slips/blob/master/slip-0023.md)

## Path to Active

### Acceptance Criteria

- [x] Each generation method is documented and provides test vectors in a language-agnostic way.
- [x] There exists reference implementations in various languages for each method.
- [x] At least 2 Cardano wallets (e.g. Yoroi & Daedalus) implement these methods.

### Implementation Plan

- [x] Implementation of each algorithm will be carried out in Yoroi and Daedalus (via cardano-wallet) by Emurgo and Input Output respectively.

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
