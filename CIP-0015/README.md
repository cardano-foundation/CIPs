---
CIP: 15
Title: Catalyst Registration Transaction Metadata Format
Authors: Sebastien Guillemot <sebastien@emurgo.io>, Rinor Hoxha <rinor.hoxha@iohk.io>, Mikhail Zabaluev <mikhail.zabaluev@iohk.io>
Comments-URI: https://forum.cardano.org/t/cip-catalyst-registration-metadata-format/44038
Status: Draft
Type: Standards
Created: 2020-01-05
License: CC-BY-4.0
---

## Abstract

Cardano uses a sidechain for its treasury system. One needs to "register" to participate on this sidechain by submitting a registration transaction on the mainnet chain. This CIP details the registration transaction format.

## Motivation

Cardano uses a sidechain for its treasury system ("Catalyst"). One of the desirable properties of this sidechain is that even if its safety is compromised, it doesn't cause loss of funds on the main Cardano chain. To achieve this, instead of using your wallet's recovery phrase on the sidechain, we need to use a brand new "voting key".

However, since 1 ADA = 1 vote, a user needs to associate their mainnet ADA to their new voting key. This can be achieved through a registration transaction.

We therefore need a registration transaction that serves three purposes:

1. Registers a "voting key" to be included in the sidechain
2. Associates mainnet ADA to this voting key
3. Declare an address to receive Catalyst rewards

## Specification

### Voting key format

A voting key is simply an ED25519 key. How this key is created is up to the wallet.

### Associating stake with a voting key

This method has been used since Fund 2.
For future fund iterations, a new method making use of time-lock scripts may
be introduced as described [below][future-development].

Recall: Cardano uses the UTXO model so to completely associate a wallet's balance with a voting key (i.e. including enterprise addresses), we would need to associate every payment key to a voting key individually. Although there are attempts at this (see [CIP8](../CIP-0008/CIP-0008.md)), the resulting data structure is a little excessive for on-chain metadata (which we want to keep small)

Given the above, we choose to only associate staking keys with voting keys. Since most Cardano wallets only use base addresses for Shelley wallet types, in most cases this should perfectly match the user's wallet.

### Registration metadata format

A Catalyst registration transaction is a regular Cardano transaction with a specific transaction metadata associated with it.

Notably, there should be four entries inside the metadata map:

Voting registration example:
```
61284: {
  // voting_key - CBOR byte array
  1: "0xa6a3c0447aeb9cc54cf6422ba32b294e5e1c3ef6d782f2acff4a70694c4d1663",
  // stake_pub - CBOR byte array
  2: "0xad4b948699193634a39dd56f779a2951a24779ad52aa7916f6912b8ec4702cee",
  // reward_address - CBOR byte array
  3: "0x00588e8e1d18cba576a4d35758069fe94e53f638b6faf7c07b8abd2bc5c5cdee47b60edc7772855324c85033c638364214cbfc6627889f81c4",
  // nonce
  4: 5479467
}
```

The entries under keys 1, 2, 3, and 4 represent the Catalyst voting key,
the staking key on the Cardano network, the address to receive rewards,
and a nonce, respectively. A registration with these metadata will be
considered valid if the following conditions hold:

- The nonce is an unsigned integer (of CBOR major type 0) that should be 
  monotonically rising across all transactions with the same staking key.
  The advised way to construct a nonce is to use the current slot number.
  This is a simple way to keep the nonce increasing without having to access
  the previous transaction data.
- The reward address is a Shelley address discriminated for the same network
  this transaction is submitted to.

To produce the signature field, the CBOR representation of a map containing
a single entry with key 61284 and the registration metadata map in the
format above is formed, designated here as `sign_data`.
This data is signed with the staking key as follows: first, the
blake2b-256 hash of `sign_data` is obtained. This hash is then signed
using the Ed25519 signature algorithm. The signature metadata entry is
added to the transaction under key 61285 as a CBOR map with a single entry
that consists of the integer key 1 and signature as obtained above as the byte array value.

Signature example:
```
61285: {
  // signature - ED25119 signature CBOR byte array
  1: "0x8b508822ac89bacb1f9c3a3ef0dc62fd72a0bd3849e2381b17272b68a8f52ea8240dcc855f2264db29a8512bfcd522ab69b982cb011e5f43d0154e72f505f007"
}
```

### Metadata schema

See the [schema file](./schema.cddl)

# Test vector

See [test vector file](./test-vector.md)

### Future development

[future-development]: #future-development

A future change of the Catalyst system may make use of a time-lock script to commit ADA on the mainnet for the duration of a voting period. The voter registration metadata in this method will not need an association
with the staking key. Therefore, the `staking_pub_key` map entry
and the `registration_signature` payload with key 61285 will no longer
be required.

## Changelog

Fund 3 added the `reward_address` inside the `key_registration` field.

Fund 4:
- added the `nonce` field to prevent replay attacks;
- changed the signature algorithm from one that signed `sign_data` directly
  to signing the Blake2b hash of `sign_data` to accommodate memory-constrained hardware wallet devices.

It was planned that since Fund 4, `registration_signature` and the `staking_pub_key` entry inside the `key_registration` field will be deprecated.
This has been deferred to a future revision of the protocol.

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode)
