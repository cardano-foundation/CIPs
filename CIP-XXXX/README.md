---
CIP: /?
Title: x509 Replayability Protection Envelope
Category: MetaData
Status: Proposed
Authors:
    - Steven Johnson <steven.johnson@iohk.io>
    - Arissara Chotivichit <arissara.chotivichit@iohk.io>
Implementors: []
Discussions:
    - https://github.com/cardano-foundation/CIPs/pull/810
Created: 2023-10-24
License: CC-BY-4.0
---

## Abstract

x509 Certificate metadata and related metadata within a x509 Registration/Update transaction must be
protected against replayability.

## Motivation: why is this CIP necessary?

x509 certificate registration necessarily references data within the transaction body that it is attached to.
Preventing replayability of the verbatim Auxiliary data attached to a transaction prevents the relationships
between those references being altered and closes a potential attack vector where an unrelated registration update
is attached to a different transaction.

Rather than define an explicit issue with potential replayability of Metadata, we simply seek to prevent it
to close off a whole category of potential attacks.

## Specification

The [x509 Metadata Envelope CDDL] defines the technical specification of the Metadata Envelope.
The following description provides additional information and context to that formal specification.
Where this description and that specification are in disagreement, the specification prevails.

The metadata envelope has the following basic structure:

![x509 Secure Metadata Envelope structure](images/metadata-envelope-structure.svg)

The purpose of this data is to lock a particular set of Auxiliary data verifiably to its original transaction.
It cannot be permitted to take the Auxiliary data to another transaction and just attach it without it being detectable.

Because Plutus scripts cannot access the Auxiliary Data of a transaction,
this detection can **NOT** be done on-chain by ledger rules or Plutus scripts.
This metadata is designed to be processed by off-chain processors of this information.

### Detailed description of the fields in the metadata and their purpose

The metadata is encoded as a CBOR map, and follows the [specification for the encoding of all Cardano metadata].

#### Key: 0 = Purpose

Purpose is defined by the consuming dApp.
It allows a dApp to have their own privately named and managed namespace for certificates.
The x509 specifications presented here do not define how certificates must be created.
Nor the purpose they are used for, that is within control of each dApp.
These specifications define a universal framework to implement such systems from.

For each set of "Purposes" that a dApp has for role-based access or off-chain identity to on-chain identity management
the dApp will define a V4 UUID.
There is no central repository of these, though a dApp may publish the ID it uses and what it's used for.
The reason UUID V4 is chosen here is if properly chosen, they can be self-assigned without fear of collision
with another dApp and eliminate the need for a central registry to manage them.

A dApp can define multiple purposes to segment RBAC functions by class.
For example, Project Catalyst defines the following two Purposes:

| UUID-V4 | Purpose |
| --- | --- |
| ca7a1457-ef9f-4c7f-9c74-7f8c4a4cfa6c | Project Catalyst User Role Registrations |
| ca7ad312-a19b-4412-ad53-2a36fb14e2e5 | Project Catalyst Admin Role Registrations |

The reason in this case for having two purposes for the same application is to allow the rules
governing registration to be easier managed between the groups.
It also allows Admins to have a distinct identity when they are just users of the system.
Any dApp is free to have as many "purposes" defined as suits their goals.

#### Key 1: txn-inputs-hash

This is a 16-byte hash of the transaction inputs field from the transaction to which this auxiliary data
was originally attached. The hash is generated using BLAKE2b (16 bytes). This hash anchors the auxiliary data to a 
specific transaction. If the auxiliary data is moved to a new transaction, it is impossible for the `txn-inputs-hash` 
to remain the same, as UTXOs can only be spent once.

The transaction input fed into the hash function should be `[*[ tx_hash, tx_index ]]`, where `tx_hash` is the
transaction hash and `tx_index` is the index of the transaction within the block.

Example data
```cddl
   [[h'3086bad5f0232c5ecb6fdaa22ccad6797d9d9aea91c1cacaa8b97b8b56fdb4cb, 0]]
```

This is a key to preventing replayability of the metadata, but is not enough by itself as it needs to be able to be
made immutable, such that any change to this field can be detected.

#### Key 2: previous_transaction_id

This is a 32-byte hash of the previous transaction in a chain of registration updates made by the same user.
The hash is generated using BLAKE2b (32 bytes). The only registration which may not have it for a single user is their first.
Once their first registration is made, they may only update it.
Any subsequent update for that user who is not properly chained to the previous transaction will be ignored as invalid.

The user is identified by their Role 0 key, which must be defined in the first registration.
The Role 0 key also includes a reference to an on-chain key, such as a stake key hash.
This is important to establish the veracity of the link between the registrations and the transaction itself.

#### Keys 10, 11 or 12 - x509 Chunked Data

Except for the first registration, the chunked data is optional.
For example, if this metadata is simply being used to lock auxiliary data to a transaction, there does not need to be
any actual role or certificate updates.

The data required to register certificates or roles could be large.
The [specification for the encoding of all Cardano metadata] also introduces difficulties in encoding x509 certificates.

The contents of the x509 RBAC Registration data stored in this key is documented separately.
Its exact contents are not relevant for this specification except to note, that it will always define at least:

* A Role 0 signing key MUST always be defined.
  * And that key MUST be associated with an on-chain key such as a stake address hash.
* The RBAC Data will have references to the transaction it is attached to.
  It cannot be fully interpreted or validated independent of the transaction.

To save space and overcome the metadata encoding limitations, x509 RBAC data is preferable encoded as described:

1. The x509 Role Registration Data is prepared and encoded with [dCBOR].
   This is the raw encoded registration data.
2. The raw encoded registration data is then compressed with [Brotli].
   This is the Brotli compressed registration data.
3. The raw encoded registration data is then compressed with [ZSTD].
   This is the ZSTD compressed registration data.
4. Which ever data is smallest, Raw, Brotli compressed or ZStd compressed is then cut into 64 bytes chunks.
   All chunks must contain 64 bytes except for the last which can contain the residual.
5. These chunks are then encoded in an array of 64 bytes long byte strings.
   The appropriate key is used to identify the compression used.
    * 10 = Raw, no compression
    * 11 = Brotli Compressed
    * 12 = ZSTD Compressed

Due to the potential size of x509 certificates, compression is mandatory where it will reduce the space of the encoded data.
Any dApp can, if it chooses, only support either Brotli or ZSTD and not trial compress the data.
A conformant dApp **MUST NOT** store Raw data if it can be compressed.
A conformant dApp **MUST NOT** store data compressed if the compressed size is larger than the raw size.
Compressed Data can be larger than Raw Data if the data is small and not very compressible.
This is an artifact of overhead in the codec data stream itself.

The specification reserves keys 13-17 for future compression schemes.
Even though there are multiple keys defined, **ONLY** 1 may be used at a time.
There is only a single list of x509 chunks, and the key is used to define the compression used only.

i.e., it is invalid to use key 10 and 12 at the same time in the same envelope.

#### Key 99 - Validation Signature

Key 99 contains the signature, which can be verified with the signing key recorded against role 0.

It is a signature over the [entire auxiliary data] that will be attached to the transaction.
This includes not only the transaction's metadata, but all attached scripts.

As the auxiliary data key 99 is part of the auxiliary data, we end up with a catch-22.
We can't sign the data because we do not know what data will be stored in the signature field.
To mitigate this problem, the size of the signature will be known in advanced, based on the signature algorithm.
When the unsigned auxiliary data is prepared, the appropriate storage for the signature is pre-allocated
in the metadata, and is set to 0x00's.

The signature is calculated over this unsigned data, and the pre-allocated signature storage is replaced with the signature itself.

This ensures that there is no alteration to the auxiliary data in form or structure.
Validating the signature then is as simple as:

1. removing the signature data from the auxiliary data;
2. setting the storage for the signature back to 0, and;
3. validating the signature on the reconstructed unsigned auxiliary data.

### Validating the Auxiliary Data is attached to the correct transaction

The Transaction will have 3 pieces of information that must be validated to ensure the attached metadata
is carried with the correct transaction.

1. The UTXO Inputs when hashed MUST == [Key 1 - Transaction Inputs Hash](#key-1-txn-inputs-hash)
2. The [auxiliary data hash] must equal to the hash of the actual auxiliary data.
   1. This is likely always true, as it should be validated by the ledger rules.
3. The [vkeywitness] set MUST include a signature over the transaction with the key associated with Role 0.
   1. Note: Role 0 may have multiple associated keys, in which case there must be a witness for all of them.
   2. A missing witness means it is not possible to validate the auxiliary data truly was built for this transaction.

## Rationale: how does this CIP achieve its goals?

This specification creates a signed set of interlocking data between a transaction and its auxiliary data.
The interlock is constructed to avoid any catch-22 in setting up a transaction and to minimize complexity.

By signing off-chain data with an off-chain key, we simplify the process of signing auxiliary data,
this allows us to sign all the data in a way suitable to the needs of the method and not limited to any on-chain restrictions.

The off-chain key is explicitly associated with an on-chain key, such that signing with the on-chain key over
the registration transaction provides proof that the two keys are related and can be used interchangeably,
The off-chain key becomes a perfect proxy for the on-chain key/s.

Once constructed in the way documented, the auxiliary data may not be posted in a different transaction without it being detectable.

It is not currently possible to detect this on-chain, as plutus does not have the necessary functionality to allow it
to inspect all auxiliary data.
However, the purpose of this envelope is to ensure that off-chain construction of off
chain certificates and dApp role registration is secure.

This specification meets that criteria.

## Path to Active

### Acceptance Criteria

To-do.

### Implementation Plan

To-do.

## References

* [Cardano Metadata CDDL Specification][specification for the encoding of all Cardano metadata]
* [Cardano Auxiliary Data CDDL Specification][entire auxiliary data]
* [Cardano Transaction Auxiliary Data Hash Specification][auxiliary data hash]
* [Cardano vKeyWitness Specification][vkeywitness]
* [Deterministic CBOR Encoding][dCBOR]
* [Brotli Data Compression][Brotli]
* [ZSTD Data Compression][ZSTD]

## Copyright

This CIP is licensed under [CC-BY-4.0]

Code samples and reference material are licensed under [Apache 2.0]

<!-- References -->
[CC-BY-4.0]: https://creativecommons.org/licenses/by/4.0/legalcode
[Apache 2.0]: https://www.apache.org/licenses/LICENSE-2.0.html
[x509 Metadata Envelope CDDL]: ./x509-envelope.cddl
[specification for the encoding of all Cardano metadata]: https://github.com/IntersectMBO/cardano-ledger/blob/ab8d57cf43be912a336e872b68d1a2526c93dc6a/eras/conway/impl/cddl-files/conway.cddl#L511-L531
[dCBOR]: https://datatracker.ietf.org/doc/draft-mcnally-deterministic-cbor/
[Brotli]: https://github.com/google/brotli
[ZSTD]: https://github.com/facebook/zstd
[entire auxiliary data]: https://github.com/IntersectMBO/cardano-ledger/blob/ab8d57cf43be912a336e872b68d1a2526c93dc6a/eras/conway/impl/cddl-files/conway.cddl#L521-L531
[auxiliary data hash]: https://github.com/IntersectMBO/cardano-ledger/blob/ab8d57cf43be912a336e872b68d1a2526c93dc6a/eras/conway/impl/cddl-files/conway.cddl#L60
[vkeywitness]: https://github.com/IntersectMBO/cardano-ledger/blob/ab8d57cf43be912a336e872b68d1a2526c93dc6a/eras/conway/impl/cddl-files/conway.cddl#L436
