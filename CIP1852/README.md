---
CIP: 1852
Title: HD (Hierarchy for Deterministic) Wallets for Cardano
Authors: Sebastien Guillemot <sebastien@emurgo.io>, Matthias Benkort <matthias.benkort@iohk.io>
Comments-URI: https://forum.cardano.org/t/cip1852-hd-wallets-for-cardano/41740
Status: Draft
Type: Standards
Created: 2019-10-28
License: CC-BY-4.0
---

## Abstract

During the *Byron* era, all wallets simply followed [BIP44](https://github.com/bitcoin/bips/blob/master/bip-0044.mediawiki). Starting with the Shelley hardfork, Cardano makes use of both the *UTXO model* and the *account model*. To support both transaction models from the same master key, we introduce a new purpose type `1852` that is an extension of [BIP44](https://github.com/bitcoin/bips/blob/master/bip-0044.mediawiki)

## Terminology

### Derivation style

Cardano does not use [BIP32](https://github.com/bitcoin/bips/blob/master/bip-0032.mediawiki) but actually uses [BIP32-Ed25519](https://cardanolaunch.com/assets/Ed25519_BIP.pdf). The `-Ed25519` suffix is often dropped in practice (ex: we say the Byron release of Cardano supports [BIP44](https://github.com/bitcoin/bips/blob/master/bip-0044.mediawiki) but in reality this is BIP44-Ed25519).

The Byron implementation of Cardano uses `purpose = 44'` (note: this was already a slight abuse of notation because Cardano implements BIP44-Ed25519 and not standard BIP44).

There are two (incompatible) implementations of BIP32-Ed25519 in Cardano:

1) HD Random (notably used initially in Daedalus)
2) HD Sequential (notably used initially in Icarus)

The difference is explained in more detail in [CIP3](../CIP3)

### Meaning of *account*

The term "account" is unfortunately an overloaded term so we clarify all its uses here

#### 1) "Account" as a BIP44 derivation level

BIP44 uses the term "account" as one derivation level to mean the following

> This level splits the key space into independent user identities, so the wallet never mixes the coins across different accounts.

To differentiate this from other usage, we sometimes refer to it as an `account'` (the bip32 notation) or a BIP44 Account.

#### 2) "Account" as a transaction model

Blockchains like Ethereum does not use the UTXO model and instead uses the [*Account model*](https://github.com/ethereum/wiki/wiki/Design-Rationale#accounts-and-not-utxos) for transactions.

#### 3) "Chimeric Account" as a wallet component

A chimeric wallet is a wallet that supports both the UTXO model and the account model using a single mnemonic. We say a *Chimeric Account* is the account model component of the chimeric wallet. The relationship between the Account model and the UTXO model is explored in the [Chimeric Ledger paper](https://eprint.iacr.org/2018/262.pdf)

### Staking Key

A chimeric account key used inside a *reward addresses* or a *base addresses* is called a staking key.

## Motivation

### Motivation for a new purpose

Byron-era wallets don't support the delegation style required for Shelley. Instead, new address types such as *base address* were created. If we reused the same purpose, then given the derivation path `m / 44' / 1815' / 0' / 0 / 0`, wallet software would not know whether or not to handle this as a Byron-era wallet or a Shelley-era wallet. By using a separate purpose, it is now clear `44'` always indicates Byron-era and `1852'` always indicates the Shelley-era. `1852` was chosen as it is the year of death of Ada Lovelace (following the fact that the `coin_type` value for Cardano is `1815` for her year of birth)

Changing the purpose helps avoid the confusion of BIP44 vs BIP44-ED25519

### Motivation for extending bip44

Starting with Shelley, Cardano uses the account model certain keys such as *staking keys*. We want the these keys to be deterministically generated from a recovery phrase which is generating it from a pre-determined derivation path similar to [BIP32](https://github.com/bitcoin/bips/blob/master/bip-0032.mediawiki). Generally it's best to only use a cryptographic key for a single purpose, and so it's best to make the staking key be separate from any key used for UTXO addresses.

## Specification

Recall that BIP44 specifies the following derivation path

```
m / purpose' / coin_type' / account' / change / address_index
```

Here, `change` can be either

- `0` indicating an *external chain*
- `1` indicating an *internal chain*

We extend this to add a new level

- `2` indicating a *chimeric account*

resulting in the following

```
m / purpose' / coin_type' / account' / 2 / account_index
```

Wallets **MUST** implement this new scheme using the master node derivation algorithm from Icarus with sequential addressing (see [CIP3](../CIP3) for more information)

### *account_index* value

We RECOMMEND wallets only use `account_index=0` for compatibility with existing software. This also avoids the need for chimeric account discovery.

Wallets that use multiple chimeric accounts are REQUIRED to use sequential indexing with no gaps. This is to make detection of mangle addresses (addresses where the payment key belongs to the user, but the staking key doesn't) easier.

*Note*: an observer looking at the blockchain will be able to tell if two staking keys belong to the same user if they are generated from the same wallet with different `account_index` values because the payment keys inside the *base addresses* will be the same.

## Test vectors

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

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode)