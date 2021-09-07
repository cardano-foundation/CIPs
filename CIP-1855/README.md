---
CIP: 1855
Title: Forging policy keys for HD Wallets
Authors: Samuel Leathers <samuel.leathers@iohk.io>, John Lotoski <john.lotoski@iohk.io>, Michael Bishop <michael.bishop@iohk.io>
Comments-Summary: Multi-party transaction signing and key management for HD wallets.
Comments-URI: https://github.com/cardano-foundation/CIPs/wiki/Comments:CIP-1855
Status: Draft
Type: Standards
Created: 2021-06-02
License: CC-BY-4.0
---

# Abstract

This document describes how to derive forging policy keys used for minting/burning tokens.

## Glossary


Term     | Definition
---      | ---
HD       | Hierarchical Deterministic, refers to wallets as described in [BIP-0032].

# Motivation

## Overview 

Forging tokens is derived from a script policy. The script policy includes hashes of keys needed to forge new tokens and must be witnessed by the keys with hashes listed. 

# Specification

## HD Derivation

We consider the following HD derivation paths similarly to [CIP-1852]:

```
m / purpose' / coin_type' / policy_ix'
```


To associate policy keys to a wallet, we reserve however `purpose=1855'` to reserve for policy keys for forging tokens. The coin type remains `coin_type=1815'` to identify Ada as registered in [SLIP-0044]. We use a hardened index for each policy key as derivation is not needed.

We can summarize the various paths and their respective domain in the following table:

| `purpose` | `coin_type` | `policy_ix`         |
| ---       | ---         | ---                 |
| `1855'`   | `1815'`     | `[2^31 .. 2^32-1]` |


### Rationale

- ERC20 Converter IOHK is developing needs to keep track of policy keys. Rather than having randomly generated policy keys, a policy key can be associated with a mnemonic which is easier to backup.
- A 3rd party may want to have multiple tokens tied to same mnemonic, so we allow an index to specify the token.

- We use a different purpose for mainly two reasons:

  - It prevents mixing up standard wallets with policy keys used for forging.

  - Using a different purpose also fits well the use-case on hardware wallets who can still rely on a single root seed to manage many types of wallets. 

### Examples

- `m/1855’/1815’/0’`
- `m/1855’/1815’/1’`
- `m/1855’/1815’/2’`


# Backwards Compatibility

N/A (no preceding implementation or design).

# Reference Implementation

None yet.

# Related Work

Description                                  | Link
---                                          | ---
BIP-0032 - HD Wallets                        | https://github.com/bitcoin/bips/blob/master/bip-0032.mediawiki
CIP-5 - Common Bech32 Prefixes               | https://github.com/cardano-foundation/CIPs/tree/master/CIP-0005
CIP-1852 - Cardano HD Wallets                | https://github.com/cardano-foundation/CIPs/tree/master/CIP-1852
A Formal Specification of the Cardano Ledger | https://hydra.iohk.io/job/Cardano/cardano-ledger-specs/shelleyLedgerSpec/latest/download-by-type/doc-pdf/ledger-spec


# Copyright

CC-BY-4.0

[BIP-0032]: https://github.com/bitcoin/bips/blob/master/bip-0032.mediawiki
[CIP-0005]: https://github.com/cardano-foundation/CIPs/tree/master/CIP-0005
[CIP-1852]: https://github.com/cardano-foundation/CIPs/blob/master/CIP-1852
[ledger-spec.pdf]: https://hydra.iohk.io/job/Cardano/cardano-ledger-specs/shelleyLedgerSpec/latest/download-by-type/doc-pdf/ledger-spec
[SLIP-0044]: https://github.com/satoshilabs/slips/blob/master/slip-0044.md
