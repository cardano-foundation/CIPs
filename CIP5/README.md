---
CIP: 5
Title: Common Bech32 Prefixes
Authors: Matthias Benkort <matthias.benkort@iohk.io>
Comments-URI: https://forum.cardano.org/t/cip5-common-bech32-prefixes/35189
Status: Draft
Type: Standards
Created: 2020-05-28
License: Apache-2.0
---

## Abstract

This CIP defines a set of common prefixes (or so-called human-readable part in the [bech32](https://github.com/bitcoin/bips/blob/master/bip-0173.mediawiki)) encoding format) for various bech32-encoded binary data across the Cardano eco-system.

## Motivation

Many tools used within the Cardano eco-system are manipulating binary data. Binary data are typically encoded as hexadecimal text strings when shown in a user interface (might it be a console, a url or a structured document from a server). From the user perspective, it can be difficult to distinguish between various encoded data. From the tools developer perspective, it can also be difficult to validate inputs based only on raw bytes (in particular when encoded data often have the same length).

Therefore, we can leverage bech32 for binary data encoding, with a set of common prefixes that can be used across tools and software to disambiguate payloads.

## Specification

We define the following set of common prefixes with their corresponding semantic. Any software willing to represent binary data in a human-friendly way should abide by these guidelines. Should a data-type be missing, we encourage developers to update this CIP and register a new prefix.

| Prefix       | Semantic                                |
| ---          | ---                                     |
| `addr_vk`    | Address verification key                |
| `addr_sk`    | Address signing key                     |
| `addr_xvk`   | Address extended verification key       |
| `addr_xsk`   | Address extended signing key            |
| `addr`       | Mainnet address                         |
| `addr_test`  | Testnet address                         |
| `stake_vk`   | Stake address verification key          |
| `stake_sk`   | Stake address signing key               |
| `stake_xvk`  | Stake address extended verification key |
| `stake_xsk`  | Stake address extended signing key      |
| `stake`      | Mainnet stake address                   |
| `stake_test` | Testnet stake address                   |
| `pool`       | Pool Id                                 |
| `pool_vk`    | Pool operator verification key          |
| `pool_sk`    | Pool operator signing key               |
| `kes_vk`     | KES verification key                    |
| `kes_sk`     | KES signing key                         |
| `vrf_vk`     | VRF verification key                    |
| `vrf_sk`     | VRF signing key                         |

## Rationale

#### About the `_test` suffix

Address already contains a discriminant tag, yet it requires one to peek at the internal binary payload. With Base58-encoded addresses, people have been used to look at first few characters and distinguish address this way. Not only this is cumbersome, but it is also made harder with both Shelley and Bech32-encoded addresses. On the one hand, the "common" part of the internal payload is much less than in Byron addresses and thus, the first bytes of the payload are varying much more. Plus, the bech32 prefix which can now be fixed makes it even more error-prone.

Therefore, having a clear human-readable indicator regarding the network discrimination is useful.

#### About `addr`

Addresses probably are the most user-facing object in the current Cardano eco-system. Being able to clearly identify them

> :bulb: Open question: with side-chains and multi-currencies coming soon, would it make sense to include the currency in the bech32 prefix? e.g. `ada1...` or `ada_addr1.`

#### About `stake`

Stake _addresses_ are references to reward account. They are used in many manipulation involving rewards (registering stake key, delegating, fetching reward balance etc..). We therefore make it a "first-class" object and assign it a dedicated prefix.

#### About `sk` & `vk`

Both are rather transparent abbreviations for **s**igning **k**ey and **v**erification **k**ey.

#### About `xsk` & `xvk`

The prefix `x` is typically used in cryptography to refer to e**x**tended keys (e.g. `xpub`, `xprv` ...). Following this convention, we prefix `sk` and `vk` as such when they refer to extended keys.

## Backwards compatibility

The only prior work done towards that direction has been [jcli](https://input-output-hk.github.io/jormungandr/jcli/introduction.html). Historically, prefixes evolved very organically and without any agreed-upon standard. jcli is however only compatible with Jörmungandr and is not intended to be compatible with the cardano-node. Therefore, there's little concern regarding compatibility here.

## Reference implementation

N/A

## Copyright

This CIP is licensed under Apache-2.0.
