---
CIP: 36
Title: Catalyst/Voltaire Registration Transaction Metadata Format (Updated)
Authors: Giacomo Pasini <giacomo.pasini@iohk.io>, Kevin Hammond <kevin.hammond@iohk.io>, Mark Stopka <mark.stopka@perlur.cloud>
Comments-URI: https://forum.cardano.org/t/cip-catalyst-registration-metadata-format/44038
Status: Proposed
Type: Standards
Created: 2021-12-06
License: CC-BY-4.0
---

## Abstract

Cardano uses a sidechain for its treasury system. One needs to "register" to participate on this sidechain by submitting a registration transaction on the mainnet chain. This CIP details the registration transaction format.
This is a revised version of the original CIP-15.

## Motivation

Cardano uses a sidechain for its treasury system ("Catalyst") and for other voting purposes. One of the desirable properties of this sidechain is that even if its safety is compromised, it doesn't cause loss of funds on the main Cardano chain. To achieve this, instead of using your wallet's recovery phrase on the sidechain, we need to use a brand new "voting key".

However, since 1 ADA = 1 vote, a user needs to associate their mainnet ADA to their new voting key. This can be achieved through a registration transaction.

In addition, to encourage participation by a broader range of ADA holders, it should be possible to delegate one's rights to vote to (possibly multiple) representatives and/or expert voters. Such delegations will still be able to receive Catalyst rewards. 

We therefore need a registration transaction that serves three purposes:

1. Registers a "voting key" to be included in the sidechain and/or delegates to existing "voting key"s
2. Associates mainnet ADA to this voting key(s)
3. Declares a payment address to receive Catalyst rewards


Note: This schema does not attempt to differentiate delegations from direct registrations, as the two options have exactly the same format.  It also does not distinguish between delegations that are made as "private" arrangements (proxy votes)
from those that are made by delegating to representatives who promote themselves publicly.
Distinguishing these possibilities is left to upper layers or future revisions of this standard, if required.
In this document, we will use the term 'delegations' to refer to all these possibilities.

## Specification

### Registration metadata format

A registration transaction is a regular Cardano transaction with a specific transaction metadata associated with it.

Notably, there should be five entries inside the metadata map:
 - A non-empty array of delegations, as described below;
 - A stake address for the network that this transaction is submitted to (to point to the Ada that is being delegated);
 - A Shelley payment address (see [CIP-0019](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0019)) discriminated for the same network this transaction is submitted to, to receive rewards.
 - A nonce that identifies that most recent delegation
 - A non-negative integer that indicates the purpose of the vote. This is an optional field to allow for compatibility with CIP-15. For now, we define 0 as the value to use for Catalyst, and leave others for future use. A new registration should not invalidate a previous one with a different voting purpose value.

### Delegation format

A delegation assigns (a portion of) the ADA controlled by one or more UTxOs on mainnet to the voting key in the sidechain as voting power.  The UTxOs can be identified via the stake address at some designated point in time.

Each delegation therefore contains:
  - a voting key: simply an ED25519 public key. This is the spending credential in the sidechain that will receive voting power from this delegation. For direct voting it's necessary to have the corresponding private key to cast votes in the sidechain. How this key is created is up to the wallet.
  - the weight that is associated with this key: this is a 4-byte unsigned integer (CBOR major type 0, The weight may range from 0 to 2^32-1) that represents the relative weight of this delegation over the total weight of all delegations in the same registration transaction.

### Voting key 

The terms "(CIP-36) voting keys" and "(CIP-36) vote keys" should be used interchangeably to indicate the keys described in this specification. But it should be made clear that implementations should favour the term "(CIP-36) vote" and that the association of both terms aims to reduce the possibility of confusion.

The term governance should not be associated with these keys nor should these keys be associated with other vote or voting keys used in the ecosystem. When discussing these keys in a wider context they should be specified by such terminology as "CIP-36 vote keys" or "CIP-36 style vote keys".

#### Derivation path

To avoid linking voting keys directly with Cardano spending keys, the voting key derivation path must start with a specific segment:

`m / 1694' / 1815' / account' / chain / address_index`

We recommend that implementors only use `address_index`=0 to avoid the need for voting key discovery.

#### Tooling

Supporting tooling should clearly define and differentiate this as a unique key type, describing such keys as "CIP-36 vote keys". When utilizing Bech32 encoding the appropriate `cvote_sk` and `cvote_vk` prefixes should be used as described in [CIP-05](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0005)

Examples of acceptable `keyType`s for supporting tools:

| `keyType` | Description |
| --------- | ----------- |
| `CIP36VoteSigningKey_ed25519` | Catalyst Vote Signing Key |
| `CIP36VoteExtendedSigningKey_ed25519` | Catalyst Vote Signing Key |
| `CIP36VoteVerificationKey_ed25519` | Catalyst Vote Verification Key |
| `CIP36VoteExtendedVerificationKey_ed25519` | Catalyst Vote Verification Key |

For hardware implementations:
| `keyType` | Description |
| --------- | ----------- |
| `CIP36VoteVerificationKey_ed25519` | Hardware Catalyst Vote Verification Key |
| `CIP36VoteHWSigningFile_ed25519` | Hardware Catalyst Vote Signing File |

The intention with this design is that if projects beyond Catalyst implement this specification they are able to add to themselves `keyType` **Description**s.

### Associating voting power with a voting key

This method has been used since Fund 2.
For future fund iterations, a new method making use of time-lock scripts may
be introduced as described [below][future-development].

Recall: Cardano uses the UTXO model so to completely associate a wallet's balance with a voting key (i.e. including enterprise addresses), we would need to associate every payment key to a voting key individually. Although there are attempts at this (see [CIP-0008]), the resulting data structure is a little excessive for on-chain metadata (which we want to keep small)

Given the above, we choose to associate staking credentials with voting keys. At the moment, the only supported staking credential is a staking key. Since most Cardano wallets only use base addresses for Shelley wallet types, in most cases this should perfectly match the user's wallet.

The voting power that is associated with each delegated voting key is derived from the user's total voting power
as follows.

1. The total weight is calculated as a sum of all the weights;
2. The user's total voting power is calculated as a whole number of ADA (rounded down);
3. The voting power associated with each voting key in the delegation array is calculated as the weighted fraction of the
   total voting power (rounded down);
4. Any remaining voting power is assigned to the last voting key in the delegation array.

This ensures that the voter's total voting power is never accidentally reduced through poor choices of weights,
and that all voting powers are exact ADA.

### Example - Registration

Voting registration example:
```
61284: {
  // delegations - CBOR byte array 
  1: [["0xa6a3c0447aeb9cc54cf6422ba32b294e5e1c3ef6d782f2acff4a70694c4d1663", 1], ["0x00588e8e1d18cba576a4d35758069fe94e53f638b6faf7c07b8abd2bc5c5cdee", 3]],
  // stake_pub - CBOR byte array
  2: "0xad4b948699193634a39dd56f779a2951a24779ad52aa7916f6912b8ec4702cee",
  // payment_address - CBOR byte array
  3: "0x00588e8e1d18cba576a4d35758069fe94e53f638b6faf7c07b8abd2bc5c5cdee47b60edc7772855324c85033c638364214cbfc6627889f81c4",
  // nonce
  4: 5479467
  // voting_purpose: 0 = Catalyst
  5: 0
}
```
The entries under keys 1, 2, 3, 4 and 5 represent the Catalyst delegation array,
the staking credential on the Cardano network, the payment address to receive rewards,
a nonce, and a voting purpose, respectively. A registration with these metadata will be
considered valid if the following conditions hold:

- The nonce is an unsigned integer (of CBOR major type 0) that should be 
  monotonically rising across all transactions with the same staking key.
  The advised way to construct a nonce is to use the current slot number.
  This is a simple way to keep the nonce increasing without having to access
  the previous transaction data.
- The payment address is a Shelley payment address discriminated for the same network
  this transaction is submitted to.
- The delegation array is not empty
- The weights in the delegation array are not all zero


Delegation to the voting key `0xa6a3c0447aeb9cc54cf6422ba32b294e5e1c3ef6d782f2acff4a70694c4d1663` will have relative weight 1 and delegation to the voting key `0x00588e8e1d18cba576a4d35758069fe94e53f638b6faf7c07b8abd2bc5c5cdee` relative weight 3 (for a total weight of 4).
Such a registration will assign 1/4 and 3/4 of the value in ADA to those keys respectively, with any remainder assigned to the second key.

The registration witness depends on the type of stake credential used.
To produce the witness field in case of a staking public key, the CBOR representation of a map containing
a single entry with key 61284 and the registration metadata map in the
format above is formed, designated here as `sign_data`.
This data is signed with the staking key as follows: first, the
blake2b-256 hash of `sign_data` is obtained. This hash is then signed
using the Ed25519 signature algorithm. The witness metadata entry is
added to the transaction under key 61285 as a CBOR map with a single entry
that consists of the integer key 1 and signature as obtained above as the byte array value.

Witness example:
```
61285: {
  // witness - ED25119 signature CBOR byte array
  1: "0x8b508822ac89bacb1f9c3a3ef0dc62fd72a0bd3849e2381b17272b68a8f52ea8240dcc855f2264db29a8512bfcd522ab69b982cb011e5f43d0154e72f505f007"
}
```

### Deregistration metadata format (Catalyst)

This deregistration format is currently only specified for Catalyst (vote_purpose=0), other voting chain purposes may handle a deregistration in a different way.
There was a discussion before if an empty delegation array could also be used to fulfil a deregistration. This idea was cancelled, because it would currently require additional resources in the Hardware-Wallets state machine to do additional checks about an empty array. So the decision was made to leave the registration part untouched and only add the deregistration via the unused key 61286. Wallets/Tools are not forced to support this deregistration method.

Definition:
- A deregistration removes all the voting power (associated stake amount) for the provided stake credential from the delegated vote-public-keys.
- A deregistration resets the state of the stake credential on the voting chain like they were never registered before.
- A deregistration transaction is a regular Cardano transaction with a specific transaction metadata associated with it.

Notably, there should be three entries inside the metadata map (key 61286):
 - The public key of the stake signing key
 - A nonce that identifies that most recent deregistration.
 - A non-negative integer that indicates the purpose of the vote. For now, we define 0 as the value to use for Catalyst, and leave others for future use.

Be aware, the deregistration metadata key is 61286, and not 61284 like it is used for a registration! The registraton metadata format and specification is independent from the deregistration one, and may not be supported by all wallets/tools.
 
### Example - Deregistration (Catalyst)

```
{
  61286: {
    // stake_pub - CBOR byte array
    1: "0x57758911253f6b31df2a87c10eb08a2c9b8450768cb8dd0d378d93f7c2e220f0",
    // nonce
    2: 74412400,
    // voting_purpose: 0 = Catalyst
    3: 0
  },
  61285: {
    // witness - ED25119 signature CBOR byte array
    1: "0xadb7c90955c348e432545276798478f02ee7c2be61fd44d22f9de22131d9bcf0b23eb413766b74b9e7ba740e71266467a5d35363411346972db9e7b710b00603"
  }
}
```
CBOR-Hex:
`A219EF66A301582057758911253F6B31DF2A87C10EB08A2C9B8450768CB8DD0D378D93F7C2E220F0021A046F7170030019EF65A1015840ADB7C90955C348E432545276798478F02EE7C2BE61FD44D22F9DE22131D9BCF0B23EB413766B74B9E7BA740E71266467A5D35363411346972DB9E7B710B00603`

The entries under keys 1, 2 and 3 represent the staking credential on the Cardano network, a nonce, and a voting purpose, respectively.
A deregistration with these metadata will be considered valid if the following conditions hold:

- The stake credentials is a stake public-key byte array (of CBOR major type 2)
- The nonce is an unsigned integer (of CBOR major type 0) that should be 
  monotonically rising across all transactions with the same staking key.
  The advised way to construct a nonce is to use the current slot number.
  This is a simple way to keep the nonce increasing without having to access
  the previous transaction data.
- The voting_purpose is an unsigned integer (of CBOR major type 0)

To produce the witness field in case of a staking public key, the CBOR representation of a map containing
a single entry with key 61286 and the deregistration metadata map in the
format above is formed, designated here as `sign_data`.
This data is signed with the staking key as follows: first, the
blake2b-256 hash of `sign_data` is obtained. This hash is then signed
using the Ed25519 signature algorithm. The witness metadata entry is
added to the transaction under key 61285 as a CBOR map with a single entry
that consists of the integer key 1 and signature as obtained above as the byte array value.


### Metadata schema

See the [schema file](./schema.cddl)

# Test vector

See [test vector file](./test-vector.md)

### Future development

[future-development]: #future-development

A future change of the Catalyst system may make use of a time-lock script to commit ADA on the mainnet for the duration of a voting period. The voter registration metadata in this method will not need an association
with a staking credential. Therefore, the `staking_credential` map entry
and the `registration_witness` payload with key 61285 will no longer
be required.

## Changelog

Fund 3 added the `reward_address` inside the `key_registration` field.

Fund 4:
- added the `nonce` field to prevent replay attacks;
- changed the signature algorithm from one that signed `sign_data` directly
  to signing the Blake2b hash of `sign_data` to accommodate memory-constrained hardware wallet devices.

It was planned that since Fund 4, `registration_signature` and the `staking_pub_key` entry inside the `key_registration` field will be deprecated.
This has been deferred to a future revision of the protocol.

Fund 8: 
 - renamed the `voting_key` field to `delegations` and add support for splitting voting power across multiple vote keys.
 - added the `voting_purpose` field to limit the scope of the delegations.
 - rename the `staking_pub_key` field to `stake_credential` and `registration_signature` to `registration_witness` to allow for future credentials additions.

Fund 10:
- Replaced the `reward_address` field with `payment_address` field, keeping it at index 3. Stipulating that `payment_address` must be a Shelley payment address, otherwise voting reward payments will not be received.
  - **Note:** up to Catalyst's Fund 9, voting rewards were paid via MIR transfer to a stake address provided within the `reward_address` field. From Fund 10 onwards, a regular payment address must be provided in the `payment_address` field to receive voting rewards. This allows Catalyst to avoid MIR transfers and instead pay voting rewards via regular transactions.

Fund 11:
 - added the `deregistration` metadata format.

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode)

[CIP-0008]: https://github.com/cardano-foundation/CIPs/tree/master/CIP-0008
