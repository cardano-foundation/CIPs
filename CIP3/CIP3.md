---
CIP: 3
Title: Wallet key generation
Authors: Matthias Benkort <matthias.benkort@iohk.io>, Sebastien Guillemot <sebastien@emurgo.io>
Comments-Summary: No comments yet.
Comments-URI: https://github.com/cardano-foundation/CIPs/wiki/Comments:CIP-0003
Status: Draft
Type: Standards
Created: 2020-05-07
License: Apache-2.0
---

## Abstract

Many wallets utilize some way of mapping a sentence of words (easy to read and write for humans) uniquely back and forth to a sized binary data (harder to remember).

This document outlines the various mapping algorithms used in the Cardano ecosystem.

## Motivation

The philosophy of cryptocurrencies is that you are in charge of your own finances. Therefore, it is very anti-thematic for wallet software to lock in a user by explicitly describing the algorithm used to derive keys for a wallet (both the master key and key derivation)

To this end, this document outlines all the relevant key generation algorithms used in the Cardano ecosystem.

## Specification

### Recovery Phrase (mnemonic) Generation

Conversion from a recovery phrase to entropy is the same as described in [BIP39](https://github.com/bitcoin/bips/blob/master/bip-0039/bip-0039-wordlists.md).

### Hierarchical Deterministic Wallets

In Cardano, hierarchical deterministic (abbrev. HD) wallets are similar to those described in [BIP-0032](https://github.com/bitcoin/bips/blob/master/bip-0032.mediawiki). Notably, we use a variation called [ED25519-BIP32](https://github.com/input-output-hk/adrestia/raw/master/user-guide/static/Ed25519_BIP.pdf). A reference implementation can be found [here](https://docs.rs/ed25519-bip32/)

### Master Key Generation

The master key generation is the mean by which on turns an initial entropy into a secure cryptographic key.

More specifically, the generation is a function from an initial seed to an extended private key (abbrev. XPrv) composed of:

- 64 bytes: an extended Ed25519 secret key composed of:
  - 32 bytes: Ed25519 curve scalar from which few bits have been tweaked according to ED25519-BIP32
  - 32 bytes: Ed25519 binary blob used as IV for signing
- 32 bytes: chain code for allowing secure child key derivation

#### History

Throughout the years, Cardano has used different styles of master key generation:

|  Name          |  Created by |  Address prefix in Byron |  Is deprecated? |
|----------------|-------------|--------------------------|-----------------|
|  Byron         |  Daedalus   |  Ddz                     |  Yes            |
|  Icarus        |  Yoroi      |  Ae2                     |  No             |
|  Icarus-Trezor |  Trezor     |  Ae2                     |  No             |
|  Ledger        |  Ledger     |  Ae2                     |  No             |

# Rationale

This CIP is merely to document the existing standards and not to provide rationales for the various methods used.

However, you can learn more at the following links:

- [Adrestia documentation](https://input-output-hk.github.io/adrestia/docs/key-concepts/hierarchical-deterministic-wallets/)
- [SLIP-0010](https://github.com/satoshilabs/slips/blob/master/slip-0010.md)
- [SLIP-0023](https://github.com/satoshilabs/slips/blob/master/slip-0023.md)

## Reference implementations

We provide a description, reference implementation and test vectors for each algorithm

#### Byron

```js
function generateMasterKey(seed) {
    return hashRepeatedly(seed, 1);
}

function hashRepeatedly(key, i) {
    (iL, iR) = HMAC
        ( hash=SHA512
        , key=key
        , message="Root Seed Chain " + UTF8NFKD(i)
        );

    let prv = tweakBits(SHA512(iL));

    if (prv[31] & 0b0010_0000) {
        return hashRepeatedly(key, i+1);
    }

    return (prv + iR);
}

function tweakBits(data) {
    // * clear the lowest 3 bits
    // * clear the highest bit
    // * set the highest 2nd bit
    data[0]  &= 0b1111_1000;
    data[31] &= 0b0111_1111;
    data[31] |= 0b0100_0000;

    return data;
}
```

##### Test vectors

```
mnemonic: install neither high supreme hurdle tissue excite lava census harbor purpose shine
master key: 309c18090ec559d4c8e377b9b19b84804a4fc430e862ef99d97f1cceccad124d92d7336d2d598affefc05c806fe2ff71cfc0fb78bfdb539178dbfcc567a04e358077d66a909e93f4577b5784b8c1c4ff3c77e706449f1c21793a79fc2abb68a9
```

#### Icarus

Icarus master key generation style supports setting an extra password as an arbitrary byte array of any size. This password acts as a second factor applied to cryptographic key retrieval. When the seed comes from an encoded recovery phrase, the password can therefore be used to add extra protection in case where the recovery phrase were to be exposed.

```js
function generateMasterKey(seed, password) {
    let data = PBKDF2
        ( kdf=HMAC-SHA512
        , iter=4096
        , salt=seed
        , password=password
        , outputLen=96
        );

    return tweakBits(data);
}

function tweakBits(data) {
    // on the ed25519 scalar leftmost 32 bytes:
    // * clear the lowest 3 bits
    // * clear the highest bit
    // * clear the 3rd highest bit
    // * set the highest 2nd bit
    data[0]  &= 0b1111_1000;
    data[31] &= 0b0001_1111;
    data[31] |= 0b0100_0000;

    return data;
}
```

##### Test vectors

```
mnemonic: eight country switch draw meat scout mystery blade tip drift useless good keep usage title
master key: c065afd2832cd8b087c4d9ab7011f481ee1e0721e78ea5dd609f3ab3f156d245d176bd8fd4ec60b4731c3918a2a72a0226c0cd119ec35b47e4d55884667f552a23f7fdcd4a10c6cd2c7393ac61d877873e248f417634aa3d812af327ffe9d620
```

```
mnemonic: eight country switch draw meat scout mystery blade tip drift useless good keep usage title
passphrase: foo (as utf8 bytes)
master key: 70531039904019351e1afb361cd1b312a4d0565d4ff9f8062d38acf4b15cce41d7b5738d9c893feea55512a3004acb0d222c35d3e3d5cde943a15a9824cbac59443cf67e589614076ba01e354b1a432e0e6db3b59e37fc56b5fb0222970a010e
```

#### Icarus-Trezor

When used < 24 words, the algorithm is the same as **Icarus**

When using 24 words, **TODO**

*Note*: Trezor also allows users to set an additional [passphrase](https://wiki.trezor.io/Passphrase)

##### Test vectors

**TODO**: test vector for 24 words

**TODO**: test vector with passphrase


#### Ledger

```js
function generateMasterKey(seed, password) {
    let data = PBKDF2
        ( kdf=HMAC-SHA512
        , iter=2048
        , salt="mnemonic" + UTF8NFKD(password)
        , password=UTF8NFKD(spaceSeparated(toMnemonic(seed)))
        , outputLen=64
        );

    let cc = HMAC
        ( hash=SHA256
        , key="ed25519 seed"
        , message=UTF8NFKD(1) + seed
        );

    let (iL, iR) = hashRepeatedly(data);

    return (tweakBits(iL) + iR + cc);
}

function hashRepeatedly(message) {
    let (iL, iR) = HMAC
        ( hash=SHA512
        , key="ed25519 seed"
        , message=message
        );

    if (iL[31] & 0b0010_0000) { 
        return hashRepeatedly(iL + iR);
    }

    return (iL, iR);
}

function tweakBits(data) {
    // * clear the lowest 3 bits
    // * clear the highest bit
    // * set the highest 2nd bit
    data[0]  &= 0b1111_1000;
    data[31] &= 0b0111_1111;
    data[31] |= 0b0100_0000;

    return data;
}
```

*Note*: Ledger also allows users to set an additional [passphrase](https://support.ledger.com/hc/en-us/articles/115005214529-Advanced-passphrase-security)

##### Test vectors

```
mnemonic: recall grace sport punch exhibit mad harbor stand obey short width stem awkward used stairs wool ugly trap season stove worth toward congress jaguar
master key: a08cf85b564ecf3b947d8d4321fb96d70ee7bb760877e371899b14e2ccf88658104b884682b57efd97decbb318a45c05a527b9cc5c2f64f7352935a049ceea60680d52308194ccef2a18e6812b452a5815fbd7f5babc083856919aaf668fe7e4
```

**TODO**: test vector with passphrase

## Copyright

This CIP is licensed under Apache-2.0