---
CIP: 11
Title: Staking key chain for HD wallets
Status: Active
Category: Wallets
Authors:
  - Sebastien Guillemot <sebastien@emurgo.io>
  - Matthias Benkort <matthias.benkort@iohk.io>
Implementors: N/A
Discussions:
  - https://github.com/cardano-foundation/CIPs/pull/33
  - https://forum.cardano.org/t/staking-key-chain-for-hd-wallets/41857
  - https://github.com/cardano-foundation/CIPs/pull/37
Created: 2020-11-04
License: CC-BY-4.0
---

## Abstract

Starting with the Shelley hardfork, Cardano makes use of both the *UTXO model* and the *account model*. To support both transaction models from the same master key, we allocate a new chain for [CIP-1852].

## Motivation: Why is this CIP necessary?

Generally it's best to only use a cryptographic key for a single purpose, and so it's best to make the staking key be separate from any key used for UTXO addresses.

## Specification

> **Note** The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in [RFC 2119](https://tools.ietf.org/html/rfc2119).

Recall that [CIP-1852] specifies the following derivation path:

```
m / purpose' / coin_type' / account' / chain / address_index
```

We set `chain=2` to indicate the *staking key chain*. Keys in this chain MUST follow the accounting model for transactions and SHOULD be used for *reward addresses*

### *address_index* value

We RECOMMEND wallets only use `address_index=0` for compatibility with existing software. This also avoids the need for staking key discovery.

Wallets that use multiple staking keys are REQUIRED to use sequential indexing with no gaps. This is to make detection of mangle addresses (addresses where the payment key belongs to the user, but the staking key doesn't) easier.

*Note*: an observer looking at the blockchain will be able to tell if two staking keys belong to the same user if they are generated from the same wallet with different `address_index` values because the payment keys inside the *base addresses* will be the same.

### Test vectors

recovery phrase
```
prevent company field green slot measure chief hero apple task eagle sunset endorse dress seed
```

private key (including chaincode) for `m / 1852' / 1815' / 0' / 2 / 0`
```
b8ab42f1aacbcdb3ae858e3a3df88142b3ed27a2d3f432024e0d943fc1e597442d57545d84c8db2820b11509d944093bc605350e60c533b8886a405bd59eed6dcf356648fe9e9219d83e989c8ff5b5b337e2897b6554c1ab4e636de791fe5427
```

reward address (with `network_id=1`)
```
stake1uy8ykk8dzmeqxm05znz65nhr80m0k3gxnjvdngf8azh6sjc6hyh36
```

## Rationale: How does this CIP achieve its goals?

### Meaning of *account*

The term "account" is unfortunately an overloaded term so we clarify all its uses here:

#### 1) "Account" as a BIP44 derivation level

BIP44 uses the term "account" as one derivation level to mean the following

> This level splits the key space into independent user identities, so the wallet never mixes the coins across different accounts.
To differentiate this from other usage, we sometimes refer to it as an `account'` (the bip32 notation) or a BIP44 Account.

#### 2) "Account" as a transaction model

Blockchains like Ethereum does not use the UTXO model and instead uses the [*Account model*](https://github.com/ethereum/wiki/wiki/Design-Rationale#accounts-and-not-utxos) for transactions.

## Path to Active

### Acceptance Criteria

- [x] All notable wallet and tooling providers follow this method of key derivation.

### Implementation Plan

- [x] This method of key derivation has been agreed as canonical and has been included in [CIP-1852].
- [x] This method of key derivation has been supported by all wallet and tool providers beginning with the Shelley ledger era.

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).

[CIP-1852]: https://github.com/cardano-foundation/CIPs/blob/master/CIP-1852/README.md
