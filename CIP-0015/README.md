---
CIP: 15
Title: Registration Transaction Metadata Format
Category: Metadata
Status: Active
Authors:
    - Sebastien Guillemot <sebastien@dcspark.io>
    - Rinor Hoxha <rinor.hoxha@iohk.io>
    - Mikhail Zabaluev <mikhail.zabaluev@iohk.io>
Implementors:
    - Daedalus <https://daedaluswallet.io/>,
    - DcSpark <https://www.dcspark.io/>,
    - Eternl <https://eternl.io/>,
    - Flint <https://flint-wallet.com/>,
    - Project Catalyst <https://projectcatalyst.io/>,
    - Typhon <https://typhonwallet.io/>,
    - Yoroi <https://yoroi-wallet.com/>
Discussions:
    - https://forum.cardano.org/t/cip-catalyst-registration-metadata-format/44038
    - https://github.com/cardano-foundation/cips/pulls/58
Created: 2020-01-05
License: CC-BY-4.0
---

## Abstract

This CIP details a transaction metadata format, used by Cardano's [Project Catalyst](https://projectcatalyst.io) for voter registrations.

## Motivation: Why is this CIP necessary?

Project Catalyst uses a sidechain for it's voting system.
One of the desirable properties of this sidechain is that even if its' safety is compromised, it doesn't cause a loss of funds on Cardano mainnet. 
To achieve this, instead of using Cardano wallets' recovery phrase on the sidechain, we introduce the "voting key".

However, since Catalyst uses stake-based voting, a user needs to associate their mainnet Ada to their voting key. 
This can be achieved through a voter registration transaction.

We therefore need a voter registration transaction that serves three purposes:

1. Registers a voting key to be included in the sidechain
2. Associates Mainnet ada to this voting key
3. Declare an address to receive Catalyst voting rewards

## Specification

### Voting key format

A voting key is simply an ED25519 key. 
How this key is created is up to the wallet, although it is not recommended that the wallet derives this key deterministicly from a mnemonic used on Cardano.

### Registration metadata format

A Catalyst registration transaction is a regular Cardano transaction with a specific transaction metadata associated with it.

Notably, there should be four entries inside the metadata map:

Voting registration example:

```cddl
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

The entries under keys 1, 2, 3, and 4 represent the Catalyst voting key, the staking key on the Cardano network, the address to receive rewards, and a nonce, respectively. 
A registration with these metadata will be considered valid if the following conditions hold:

- The nonce is an unsigned integer (of CBOR major type 0) that should be monotonically rising across all transactions with the same staking key. 
  - The advised way to construct a nonce is to use the current slot number.
  - This is a simple way to keep the nonce increasing without having to access the previous transaction data.
- The reward address is a Shelley address discriminated for the same network this transaction is submitted to.

To produce the signature field, the CBOR representation of a map containing a single entry with key `61284` and the registration metadata map in the format above is formed, designated here as `sign_data`.
This data is signed with the staking key as follows: first, the blake2b-256 hash of `sign_data` is obtained. 
This hash is then signed using the Ed25519 signature algorithm. The signature metadata entry is added to the transaction under key 61285 as a CBOR map with a single entry that consists of the integer key 1 and signature as obtained above as the byte array value.

Signature example:

```cddl
61285: {
  // signature - ED25119 signature CBOR byte array
  1: "0x8b508822ac89bacb1f9c3a3ef0dc62fd72a0bd3849e2381b17272b68a8f52ea8240dcc855f2264db29a8512bfcd522ab69b982cb011e5f43d0154e72f505f007"
}
```
### Versioning

This CIP is not to be versioned using a traditional scheme, rather if any large technical changes require a new proposal to replace this one.
Small changes can be made if they are completely backwards compatible.

### Changelog

Catalyst Fund 3: 
- added the `reward_address` inside the `key_registration` field.

Catalyst Fund 4:
- added the `nonce` field to prevent replay attacks;
- changed the signature algorithm from one that signed `sign_data` directly to signing the Blake2b hash of `sign_data` to accommodate memory-constrained hardware wallet devices.

It was planned that since Fund 4, `registration_signature` and the `staking_pub_key` entry inside the `key_registration` field will be deprecated.
This has been deferred to a future revision of the protocol.

## Rationale: How does this CIP achieve its goals?

The described metadata format allows for the association of a voting key with a stake credential on a Cardano network.

### Associating stake with a voting key

Cardano uses the UTxO model so to completely associate a wallet's balance with a voting key (i.e. including enterprise addresses), we would need to associate every payment key to a voting key individually.
Although there are attempts at this (see [CIP-0008]), the resulting data structure is a little excessive for on-chain metadata (which we want to keep small).

Given the above, we choose to only associate staking keys with voting keys.
Since most Cardano wallets only use base addresses for Shelley wallet types, in most cases this should perfectly match the user's wallet.

### Future development

A future change of the Catalyst system may make use of a time-lock script to commit ADA on the mainnet for the duration of a voting period.
The voter registration metadata in this method will not need an association with the staking key.
Therefore, the `staking_pub_key` map entry and the `registration_signature` payload with key `61285` will no longer be required.

## Path to Active

### Acceptance Criteria

- [x] This metadata format is implemented by at least 3 wallets
  - Deadalus <https://daedaluswallet.io/>
  - Eternl <https://eternl.io/>,
  - Flint <https://flint-wallet.com/>,
  - Typhon <https://typhonwallet.io/>,
  - Yoroi <https://yoroi-wallet.com/>
- [x] This metadata format is used by Catalyst for at least 3 funds
  - This format has been used up to and included Catalyst fund 10

### Implementation Plan

- [x] Author(s) to provide a schema cddl file
  - See the [schema file](./schema.cddl)
- [x] Author(s) to provide a test vectors file
  -  See [test vector file](./test-vector.md)
- [x] Author(s) to provide a npm package to support the creation of this metadata format
  - [catalyst-registration-js](https://www.npmjs.com/package/@dcspark/catalyst-registration-js)

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).

[CIP-0008]: https://github.com/cardano-foundation/CIPs/blob/master/CIP-0008/README.md
