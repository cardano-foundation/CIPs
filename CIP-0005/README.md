---
CIP: 5
Title: Common Bech32 Prefixes
Category: Tools
Status: Active
Authors:
  - Matthias Benkort <matthias.benkort@cardanofoundation.org>
Implementors: N/A
Discussions:
  - https://forum.cardano.org/t/cip5-common-bech32-prefixes/35189
  - https://github.com/cardano-foundation/CIPs/pull/427
  - https://github.com/cardano-foundation/CIPs/pull/342
  - https://github.com/cardano-foundation/CIPs/pull/251
  - https://github.com/cardano-foundation/CIPs/pull/177
  - https://github.com/cardano-foundation/CIPs/pull/31
Created: 2020-05-28
License: Apache-2.0
---

## Abstract

This CIP defines a set of common prefixes (or so-called human-readable part in the [bech32](https://github.com/bitcoin/bips/blob/master/bip-0173.mediawiki)) encoding format) for various bech32-encoded binary data across the Cardano eco-system.

## Motivation: why is this CIP necessary?

Many tools used within the Cardano eco-system are manipulating binary data. Binary data are typically encoded as hexadecimal text strings when shown in a user interface (might it be a console, a url or a structured document from a server). From the user perspective, it can be difficult to distinguish between various encoded data. From the tools developer perspective, it can also be difficult to validate inputs based only on raw bytes (in particular when encoded data often have the same length).

Therefore, we can leverage bech32 for binary data encoding, with a set of common prefixes that can be used across tools and software to disambiguate payloads.

## Specification

We define the following set of common prefixes with their corresponding semantic. Any software willing to represent binary data in a human-friendly way should abide by these guidelines. Should a data-type be missing, we encourage developers to update this CIP and register a new prefix.

### Keys

| Prefix             | Meaning                                            | Contents                           |
| ---                | ---                                                | ---                                |
| `acct_sk`          | CIP-1852's account private key                     | Ed25519 private key                |
| `acct_vk`          | CIP-1852's account public key                      | Ed25519 public key                 |
| `acct_xsk`         | CIP-1852's extended account private key            | Ed25519-bip32 extended private key |
| `acct_xvk`         | CIP-1852's extended account public key             | Ed25519 public key with chain code |
| `acct_shared_sk`   | CIP-1854's account private key                     | Ed25519 private key                |
| `acct_shared_vk`   | CIP-1854's account public key                      | Ed25519 public key                 |
| `acct_shared_xsk`  | CIP-1854's extended account private key            | Ed25519-bip32 extended private key |
| `acct_shared_xvk`  | CIP-1854's extended account public key             | Ed25519 public key with chain code |
| `addr_sk`          | CIP-1852's address signing key                     | Ed25519 private key                |
| `addr_vk`          | CIP-1852's address verification key                | Ed25519 public key                 |
| `addr_xsk`         | CIP-1852's address extended signing key            | Ed25519-bip32 extended private key |
| `addr_xvk`         | CIP-1852's address extended verification key       | Ed25519 public key with chain code |
| `addr_shared_sk`   | CIP-1854's address signing key                     | Ed25519 private key                |
| `addr_shared_vk`   | CIP-1854's address verification key                | Ed25519 public key                 |
| `addr_shared_xsk`  | CIP-1854's address extended signing key            | Ed25519-bip32 extended private key |
| `addr_shared_xvk`  | CIP-1854's address extended verification key       | Ed25519 public key with chain code |
| `gov_sk`           | Governance vote signing key                        | Ed25519 private key                |
| `gov_vk`           | Governance vote verification key                   | Ed25519 public key                 |
| `cvote_sk`         | CIP-36's vote signing key                          | Ed25519 private key                |
| `cvote_vk`         | CIP-36's vote verification key                     | Ed25519 public key                 |
| `kes_sk`           | KES signing key                                    | KES signing key                    |
| `kes_vk`           | KES verification key                               | KES verification key               |
| `policy_sk`        | CIP-1855's policy private key                      | Ed25519 private key                |
| `policy_vk`        | CIP-1855's policy public key                       | Ed25519 public key                 |
| `pool_sk`          | Pool operator signing key                          | Ed25519 private key                |
| `pool_vk`          | Pool operator verification key                     | Ed25519 public key                 |
| `root_sk`          | CIP-1852's root private key                        | Ed25519 private key                |
| `root_vk`          | CIP-1852's root public key                         | Ed25519 public key                 |
| `root_xsk`         | CIP-1852's extended root private key               | Ed25519-bip32 extended private key |
| `root_xvk`         | CIP-1852's extended root public key                | Ed25519 public key with chain code |
| `root_shared_sk`   | CIP-1854's root private key                        | Ed25519 private key                |
| `root_shared_vk`   | CIP-1854's root public key                         | Ed25519 public key                 |
| `root_shared_xsk`  | CIP-1854's extended root private key               | Ed25519-bip32 extended private key |
| `root_shared_xvk`  | CIP-1854's extended root public key                | Ed25519 public key with chain code |
| `stake_sk`         | CIP-1852's stake address signing key               | Ed25519 private key                |
| `stake_vk`         | CIP-1852's stake address verification key          | Ed25519 public key                 |
| `stake_xsk`        | CIP-1852's extended stake address signing key      | Ed25519-bip32 extended private key |
| `stake_xvk`        | CIP-1852's extended stake address verification key | Ed25519 public key with chain code |
| `stake_shared_sk`  | CIP-1854's stake address signing key               | Ed25519 private key                |
| `stake_shared_vk`  | CIP-1854's stake address verification key          | Ed25519 public key                 |
| `stake_shared_xsk` | CIP-1854's extended stake address signing key      | Ed25519-bip32 extended private key |
| `stake_shared_xvk` | CIP-1854's extended stake address verification key | Ed25519 public key with chain code |
| `vrf_sk`           | VRF signing key                                    | VRF signing key                    |
| `vrf_vk`           | VRF verification key                               | VRF verification key               |

### Hashes

| Prefix             | Meaning                                            | Contents                                                 |
| ---                | ---                                                | ---                                                      |
| `asset`            | Fingerprint of a native asset for human comparison | See [CIP-0014]                                           |
| `pool`             | Pool operator verification key hash (pool ID)      | blake2b\_224 digest of an operator verification key       |
| `script`           | Script hash                                        | blake2b\_224 digest of a serialized transaction script    |
| `addr_vkh`         | Address verification key hash                      | blake2b\_224 digest of a payment verification key         |
| `addr_shared_vkh`  | Shared address verification key hash               | blake2b\_224 digest of a payment verification key         |
| `policy_vkh`       | Policy verification key hash                       | blake2b\_224 digest of a policy verification key          |
| `stake_vkh`        | Stake address verification key hash                | blake2b\_224 digest of a delegation verification key      |
| `stake_shared_vkh` | Shared stake address verification key hash         | blake2b\_224 digest of a delegation verification key      |
| `req_signer_vkh`   | Required signer verification key hash              | blake2b\_224 digest of a required signer verification key |
| `vrf_vkh`          | VRF verification key hash                          | blake2b\_256 digest of a VRF verification key             |
| `datum`            | Output datum hash                                  | blake2b\_256 digest of output datum                       |
| `script_data`      | Script data hash                                   | blake2b\_256 digest of script data                        |

### Miscellaneous

| Prefix       | Meaning               | Contents                                                      |
| ---          | ---                   | ---                                                           |
| `addr`       | Mainnet address       | Network tag, payment credential and optional stake credential |
| `addr_test`  | Testnet address       | Network tag, payment credential and optional stake credential |
| `stake`      | Mainnet stake address | Network tag and stake credential                              |
| `stake_test` | Testnet stake address | Network tag and stake credential                              |

## Rationale: how does this CIP achieve its goals?

### About the `_test` suffix

Address already contains a discriminant tag, yet it requires one to peek at the internal binary payload. With Base58-encoded addresses, people have been used to look at first few characters and distinguish address this way. Not only this is cumbersome, but it is also made harder with both Shelley and Bech32-encoded addresses. On the one hand, the "common" part of the internal payload is much less than in Byron addresses and thus, the first bytes of the payload are varying much more. Plus, the bech32 prefix which can now be fixed makes it even more error-prone.

Therefore, having a clear human-readable indicator regarding the network discrimination is useful.

### About `addr`

Addresses probably are the most user-facing object in the current Cardano eco-system. Being able to clearly identify them

> :bulb: Open question: with side-chains and multi-currencies coming soon, would it make sense to include the currency in the bech32 prefix? e.g. `ada1...` or `ada_addr1.`

### About `stake`

Stake _addresses_ are references to reward account. They are used in many manipulation involving rewards (registering stake key, delegating, fetching reward balance etc..). We therefore make it a "first-class" object and assign it a dedicated prefix.

### About `sk` & `vk`

Both are rather transparent abbreviations for **s**igning **k**ey and **v**erification **k**ey.

### About `xsk` & `xvk`

The prefix `x` is typically used in cryptography to refer to e**x**tended keys (e.g. `xpub`, `xprv` ...). Following this convention, we prefix `sk` and `vk` as such when they refer to extended keys.

### About `vkh`

An abbreviation for **v**erification **k**ey **h**ash.

Verification key hashes are commonly utilized throughout the Cardano
eco-system. For example, they're used in stake pool registration and
retirement certificates, stake key registration, delegation, and
deregistration certificates, etc. As a result, it seems useful to have a
human-readable prefix by which one can discern the different kinds of
verification key hashes.

### Backwards compatibility

The only prior work done towards that direction has been [jcli](https://input-output-hk.github.io/jormungandr/jcli/introduction.html). Historically, prefixes evolved very organically and without any agreed-upon standard. jcli is however only compatible with Jörmungandr and is not intended to be compatible with the cardano-node. Therefore, there's little concern regarding compatibility here.

## Path to Active

### Acceptance Criteria

- [x] There is a variety of tools and services utilizing this standard:
  - [x] Trezor, Ledger
  - [x] cardano-cli
  - [x] cardano-wallet
  - [x] Blockfrost
  - [x] cardanoscan, cexplorer
  - ... and more

### Implementation Plan

- Available JavaScript library: [cip5-js](https://www.npmjs.com/package/@dcspark/cip5-js)

## Copyright

This CIP is licensed under Apache-2.0.

[CIP-0014]: https://github.com/cardano-foundation/CIPs/blob/645243e30b5aae109a70ec2b47af70dcc808bc56/CIP-0014
