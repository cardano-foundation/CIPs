---
CIP: 5
Title: Common Bech32 Prefixes 
Authors: Matthias Benkort <matthias.benkort@iohk.io>
Comments-URI: TODO
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

| Prefix            | Semantic                                         |
| ---               | ---                                              |
| `addr`            | Mainnet address                                  |
| `addr_test_{tag}` | A Testnet address with an associated network tag |
| `ed25519_pub`     | An Ed25519 public key                            |
| `ed25519_prv`     | An Ed25519 private key                           |
| `ed25519_xpub`    | An Ed25519 extended public key                   |
| `ed25519_xprv`    | An Ed25519 extended private key                  |
| `vrf_pub`         | A VRF public key                                 |
| `vrf_prv`         | A VRF private key                                |
| `kes_pub`         | A KES public key                                 |
| `kes_prv`         | A KES private key                                |
| `cert_pool_reg`   | An unsigned pool registration certificate        |
| `cert_pool_ret`   | An unsigned pool retirement certificate          |
| `cert_key_reg`    | An unsigned stake key registration certificate   |
| `cert_key_ret`    | An unsigned stake key retirement certificate     |

## Rationale

TODO

## Backwards compatibility

The only prior work done towards that direction has been [jcli](https://input-output-hk.github.io/jormungandr/jcli/introduction.html). Historically, prefixes evolved very organically and without any agreed-upon standard. jcli is however only compatible with Jörmungandr and is not intended to be compatible with the cardano-node. Therefore, there's little concern regarding compatibility here.

## Reference implementation

N/A

## Copyright

This CIP is licensed under Apache-2.0.
