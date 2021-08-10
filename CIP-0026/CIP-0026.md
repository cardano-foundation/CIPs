---
CIP: CIP-0026
Title: Cardano Off-Chain Metadata
Author: Matthias Benkort <matthias.benkort@iohk.io>, Michael Peyton Jones <michael.peyton-jones@iohk.io>, Polina Vinogradova <polina.vinogradova@iohk.io>
Comments-Summary: No comments yet
Comments-URI: https://github.com/CardanoFoundation/CIPs/pulls/112
Status: Draft
Type: Process
Created: 2021-08-10
License: CC-BY-4.0
---

# Abstract

We introduce a standard for off-chain metadata that can map opaque on-chain identifiers to metadata suitable for human consumption. This will support user-interface components, and allow resolving trust issues in a moderately decentralized way.

# Motivation

On the blockchain, we tend to refer to things by hashes or other opaque identifiers. But these are not very human friendly:
* In the case of hashes, we often want to know the preimage of the hash, such as
   * The script corresponding to an output locked by a script hash
   * The public key corresponding to a public key hash
* We want other metadata as appropriate, such as
   * A human-friendly name
   * The name of the creator, their website, an icon, etc. etc.
* We would like such metadata to be integrated into the UI of our applications
   * For example, if I’ve accepted a particular name for a currency, I’d like to see that name everywhere in the UI instead of the hash
* We want the security model of such metadata to be sound
   * For example, we don’t want users to be phished by misleading metadata

We think there is a case for a metadata distribution system that would fill these needs in a consistent fashion. This would be very useful for Plutus, multi-asset support, and perhaps even some of the existing Cardano infrastructure. Moreover, since much of the metadata which we want to store is not determined by the blockchain, we propose a system that is independent of the blockchain, and relies on non-blockchain trust mechanisms.

The Rationale section provides additional justifications for the design decisions in this document.

## Use Cases

### Hashed Content

Many pieces of information on the Cardano blockchain are stored as hashes, and only revealed at later stages when required for validation. This is the case for example of scripts (Plutus or phase-1), datums, and public keys. It is likely that (some) users will want to know the preimages of those hashes in a somewhat reliable way and, before they are revealed on-chain.

### Off-Chain Metadata

Unlike some (un)popular opinions suggest, a blockchain is a poor choice for a content database. Blockchains are intrinsically ledgers and they are good at recording events or hashes. Yet, there are several elements for which hashes aren't providing a great user experience and to which we would rather attach some human-readable metadata (like names, websites, contact details etc...). This is the case for stake pool for instance for which [SMASH](https://github.com/input-output-hk/smash/) already provides a solution. This is also the case for monetary policies and scripts. In both cases, having the ability to attach extra metadata to _some_ hash with a way to ensure the authenticity of the data is useful.

# Specification

This specification covers some parts of a bigger system likely involving multiple components. What part is being implemented and by who is considered out of the scope of this specification. We however envision a setup in which users have access to a client application (a.k.a the wallet), which itself is able to connect to some remote server. We assume the server to also offer a user-interface (either via a graphical user-interface or a application programming interface) for accepting content. 

## Hash Function

There are several places in this document where we need an arbitrary hash function. We will  henceforth refer to this simply as “hash”. The hash function MUST be **Blake2b-256** (unless explicitly said otherwise). The hash of a string is the hash of the bytes of the string according to its encoding.

## Metadata Structure

Metadata consists of a mandatory _metadata subject_, and a number of _metadata properties_ which describes that subject. Each property consists of a mapping from _property names_ to _property values_, _sequence numbers_ and _signatures_.

Metadata subjects, property names, and property values must all be represented as UTF-8 encoded strings. In addition, property values must parse as valid JSON.

There is no particular interpretation attached to a metadata subject: it can be anything (see however the special-case of phase-1 monetary policy below). We anticipate however that the primary use-case for it will be something that appears on the blockchain, like the hash of a script.

We will refer to a whole metadata as a _metadata object_ and to a particular property assignment for a particular metadata subject as a _metadata entry_. We will say that a metadata object is _well-formed_ when it validates according to the [JSON-schema specification given in annex](./schema.json). To be valid, a metadata object MUST be (at least) well-formed.

```json
{
  "subject": "a5408d0db0d942fd80374",
  "contact": {
    "value": "Cid Kramer",
    "sequenceNumber": 0,
    "signatures": [
      {
        "signature": "79a4601",
        "publicKey": "bc77d04"
      }
    ]
  }
}
```

### Sequence Numbers

Metadata entries MUST have a `sequenceNumber` associated with them. This is a monotonically increasing integer which is used to ensure that clients and servers do not revert to “earlier” versions of an entry. Upon receiving new metadata objects, servers SHOULD verify the sequence number for each entry already known for that subject and reject submissions with a lower sequence number. 

### Attestation Signatures

Metadata entries MAY have attestations `signatures` associated with them, in the form of an array of objects. Attestation signatures are indeed annotated. An annotated signature for a message is an object with of a `publicKey`, and a `signature` of a specified message (see below) by the corresponding private key.

> <sub>░ note ░</sub> 
> 
> When we say “signature” in the rest of this document we mean “annotated signature”.

An attestation signature for an entry is a signature of the entry message:

```js
hash(
  hash(CBOR(subject)) + 
  hash(CBOR(name)) + 
  hash(CBOR(value)) + 
  hash(CBOR(sequenceNumber))
)
```

where `+` designates the concatenation of two bytestrings and `CBOR` designates a function which encodes its input into binary according to [RFC-8949](https://www.rfc-editor.org/rfc/rfc8949). That is, JSON strings are encoded as major type 3, JSON integers as major types 0 or 1, JSON floats as major type 7, JSON arrays as major type 4, JSON objects as major type 5, JSON booleans as major type 7 and JSON null as major type 7; according to the specification.

For example, the attestation message for the example entry above is:

```js
hash(
  hash(0x75613534303864306462306439343266643830333734) +  // text "a5408d0db0d942fd80374"
  hash(0x67636F6E74616374) +                              // text "contact"
  hash(0x6A436964204B72616D6572) +                        // text "Cid Kramer"
  hash(0x00)                                              // uint 0
)
// cd731afcc904c521e0c6b3cc0b560b8157ee29c3e41cd15f8dc8984edf600029
```

The `publicKey` and the `signature` MUST be base16-encoded and stored as JSON strings. All signatures must be verifiable through the **Ed25519 digital signature** scheme and public keys must therefore be 32-byte long Ed25519 public keys. 


## Well-known Properties

The following properties are considered well-known, and the JSON in their values MUST have the given structure and semantic interpretation. New properties can be added to this list by amending this CIP. The role of well-known properties is to facilitate integration between applications implementing this CIP. Nevertheless, registries are encouraged to **not** restrict properties to only this limited set but, registries (or metadata servers) MUST verify the well-formedness of those properties when present in a metadata object.

<details>
  <summary><code>preimage</code></summary>

```json
{ 
    "type": "object", 
    "description": "A hashing algorithm identifier and a base16-enocoded bytestring, such that the bytestring is the preimage of the metadata subject under that hash function.",
    "requiredProperties": [ "alg", "msg" ],
    "properties": { 
        "alg": { 
            "type": "string", 
            "description": "A hashing algorithm identifier. The length of the digest is given by the subject.", 
            "enum": [ "sha1", "sha", "sha3", "blake2b", "blake2s", "keccak", "md5" ] 
        }, 
        "msg": { 
            "type": "string", 
            "description": "The actual preimage.",
            "encoding": "base16"
        }
    }
}
```
</details>


<details>
  <summary><code>name</code></summary>

```json
{
    "type": "string",
    "description": "A human-readable name for the metadata subject, suitable for use in an interface or in running text.",
    "maxLength": 50,
    "minLength": 1
}
```
</details>


<details>
  <summary><code>description</code></summary>

```json
{
    "type": "string",
    "description": "A longer description of the metadata subject, suitable for use when inspecting the metadata subject itself.",
    "maxLength": 500
}
```
</details>

<details>
  <summary><code>ticker</code></summary>

```json
{
  "type": "string",
  "description": "A short identifier for the metadata subject, suitable to show in listings or tiles.",
  "maxLength": 5,
  "minLength": 2
}
```
</details>

<details>
  <summary><code>decimals</code></summary>

```json
{
  "type": "integer",
  "description": "When the metadata subject refers to a monetary policy, refers to the number of decimals of the currency.",
  "minimum": 0,
  "maximum": 19
},
```
</details>

<details>
  <summary><code>url</code></summary>

```json
{
    "type": "string",
    "description": "A universal resource identifier pointing to additional information about the metadata subject.",
    "format": "uri",
    "maxLength": 250
}
```
</details>

<details>
  <summary><code>logo</code></summary>

```json
{
  "type": "string",
  "description": "An `image/png` object which is 64KB in size at most.",
  "encoding": "base64",
  "maxLength": 87400
}
```
</details>

## Verifying Metadata 

### General Case

Applications that want to display token metadata MUST verify signatures of metadata entries against a set of trusted keys for certain subjects. We will call such applications _"clients"_. Conceptually we expect clients to maintain a mapping of many subjects to many verification keys. In case where a metadata entry contains no signatures, when none of the provided signatures was produced by a known key for the corresponding subject or when none of the provided signatures verifies: the metadata entry MUST be considered invalid and not be presented to end-users.

Note that:

- In this scenario, a single valid signature is sufficient to consider a metadata entry valid but there can be many signatures (invalid or valid). So long as one is valid, the entry is considered verified.

- The verification is done per _entry_. That is, a metadata object may contain both verified and unverified entries. Plus, entries under the same subject may be verified by different keys. 

The way by which the trusted keys are registered into clients is unspecified although we already consider the following, **non-overlapping**, **complementary**, options:

1. Clients MAY explicitly prompt the consumer / end-user about whether to accept a certain entry. While this is unpractical for some cases (e.g. token metadata), it may be relevant for some.

1. Clients MAY come with a set of pre-configured well-known trusted keys chosen at the discretion of the application editor. 

2. End-users SHOULD have the ability to add/remove keys from their trusted set. This allows end-users to introduce trusted keys they know before they end up in the pre-configured set (which likely follow the application release cycle). In this context, keys are advertised by the signing authority by some means, for instance, on social media or on another form of public key registry (e.g. [keybase.io](http://keybase.io/))

3. Mappings of subjects to keys MAY be recorded on-chain, using transaction metadata and an appropriate label registered on [CIP-0010](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0010/CIP-0010.md). In some scenarios, the context within which the transaction is signed may be enough to reliably trust the legitimacy of a mapping. For example, in the case of a monetary policy, one could imagine _registering trusted keys_ in the same transaction minting tokens. Because the transaction is inserted in the ledger, it must have been signed by the token issuer and therefore, the specified keys are without doubt acknowledged by the token issuer. As a result, clients having access to on-chain data can automatically discover new mappings from observing the chain. 

### Special Case: Phase-1 Monetary Policies

> <sub>░ note ░</sub> 
> 
> This approach is now considered superseded by the more general approach. While it has some nice properties, new applications should consider sticking to the general case **even for phase-1 monetary policies**. Servers who seek backward-compatibility should implement both. 

We consider the case of phase-1 monetary policies introduced during the Allegra era of Cardano. Such policies are identified by a simple (native) script which is validated by the ledger during the so-called phase-1 validations. Such scripts are made of key hashes, combined via a set of basic first-order logic primitives (ALL, ANY-OF, N-OF...) such that, it is possible to statically verify whether a set of signatures would validate the script. 

These scripts therefore make relatively good verification mechanisms for metadata associated with phase-1 monetary policies. Hence, we introduce the following well-known property:

<details>
  <summary><code>policy</code></summary>

```json
{ 
  "type": "string",
  "description": "A CBOR-serialized phase-1 monetary policy, used as a pre-image to produce a policyId.",
  "encoding": "base16",
  "minLength": 56,
  "maxLength": 120
}
```
</details>

<br/>

Metadata objects that contain an extra top-level property `policy` MUST therefore abide by the following rules:

1. Their subject MUST be an `assetId`, encoded in base16; where the `assetId` is the concatenation of a `policyId` (28 bytes) and an `assetName` (up to 32 bytes). 
2. The `policy` MUST therefore re-hash (through blake2b-224) into the first 28 bytes of the metadata's subject (the policy id).
3. Every metadata entry MUST have a set of signatures such that, the monetary script given in policy can be validated using the provided signatures, irrespective of the time constraints. Said differently, the public keys from the annotated signature must re-hash into key hashes present in the policy AND each key must verify its associated signature AND the provided signatures must
be sufficient to validate the monetary script according to the semantic given by the cardano ledger without considering the time constraints.

For example, consider the following phase-1 monetary policy, represented in JSON:

```json
{
    "type": "all",
    "scripts": [
        {
            "keyHash": "2B0C33E73D2A70733EDC971D19E2CAFBADA1692DB2D35E7DC9453DF2",
            "type": "sig"
        },
        {
            "keyHash": "E2CAFBADA1692DB2D35E7DC9453DF22B0C33E73D2A70733EDC971D19",
            "type": "sig"
        }
    ]
}
```

To validate such a policy, each entry would require 2 signatures: 

- from `2B0C33E73D2A70733EDC971D19E2CAFBADA1692DB2D35E7DC9453DF2`
- and from `E2CAFBADA1692DB2D35E7DC9453DF22B0C33E73D2A70733EDC971D19`

The policy MAY also contain some additional time constraints (VALID-AFTER, VALID-BEFORE) specifying a certain slot number. For the sake of verifying policies, these should be ignored and consider _valid_. 

## Recommendations For Metadata Servers

The following section gives some recommendations to application developers willing to implement a metadata server / registry. Following these recommendations will facilitate interoperability between applications and also, provide some good security foundation for the server. In this context, what we refer to as a _metadata server_ is a web server that exposes the functionality of a simple key-value store, where the keys are metadata subjects and property names, and the values are their property values.

#### Querying Metadata

The metadata server SHOULD implement the following HTTP methods:

```
GET /metadata/{subject}/property/{property name}
```

This SHOULD return the property value for the given property name (if any) associated with the subject. This is returned as a single-entry JSON object whose key is the property name and return the complete JSON entry for that subject+name (including `value`, `sequenceNumber` and `signatures`).

The metadata server SHOULD set the Content-Length header to allow clients to decide if they wish to download sizeable metadata.

```
GET /metadata/{subject}/properties
```

This SHOULD return all the property names which are available for that subject (if any). These are returned as a JSON list of strings.

```
GET /metadata/{subject}
```

This SHOULD return the full metadata object associated with this subject, including the subject and all properties associated with it. 

```
POST /metadata/query
REQUEST BODY : a JSON object with the keys:
  “subjects” : A list of subjects, encoded as strings in the same way as the queries above.
  “properties” : An optional list of property names, encoded as strings in the same way as the query above.
```

This endpoint provides a way to batch queries, making several requests of the server with only one HTTP request.

If only `“subjects”` is supplied, this query SHOULD return a list of subjects with all their properties. The response format will be as similar as possible to the `GET /metadata/{subject}` request, but nested inside a list.

If `“subjects”` and `“properties”` are supplied, the query will return a list of subjects, with their properties narrowed down to only those specified by `“properties”`.

> <sub>░ suggestion ░</sub> 
>
> Metadata servers MAY provide other methods of querying metadata, such as:
> 
> * Searching for all mappings whose “name” property value is a particular string
> * Searching for all metadata items which are signed by a particular cryptographic key, or uploaded by a particular user

#### Modifying metadata

The metadata server needs some way to add and modify metadata entries. The method for doing so is largely up to the implementor, but recommend to abide by the following rules:

1. The server MUST only accept updates for metadata entries that have a higher sequence number than the previous entry.
1. The server MUST always verify well-formedness of metadata entries before accepting them.
1. The server MUST always cryptographically verify metadata entries' signatures before accepting them.
1. The server MAY reject entries with no signatures. 
1. The server MAY support the POST, PUT, and DELETE verbs to modify metadata entries.

#### Authentication

If the server supports modifications to metadata entries, it SHOULD provide some form of authentication which controls who can modify them. Servers MUST NOT use the attestation signatures on metadata entries as part of authentication (with the exception of phase-1 monetary policy). Attestation signatures are per-entry, and are orthogonal to determining who controls the metadata for a subject.

Simple systems may want to use little more than cryptographic signatures, but more sophisticated systems could have registered user accounts and control access in that way.

#### Audit

The metadata server MAY provide a mechanism auditing changes to metadata, for example by storing the update history of an entry and allowing users to query it (via the API or otherwise).

#### Hardening

Allowing unrestricted updates to non-verifiable metadata would allow malicious users to “squat” or take over another user’s metadata subjects. This is why we recommend that server implementations have some kind of authentication system to mitigate this.

One approach is to have a system of “ownership” of metadata subjects. This notion of ownership is vague, although in some cases there are obvious choices (e.g. for a multisig minting policy, the obvious owners are the signatories who can authorize minting). It is up to the server to pick a policy for how to decide on owners, and enforce security; or indeed to take a different approach entirely. 

See the earlier “Authentication” section for a description of a possible approach to managing ownership.

Depending on the authentication mechanism they use, servers may also need to worry about replay attacks, where an attacker submits a (correctly signed) old record to “revert” a legitimate change.  However, these can be unconditionally prevented by correctly implementing sequence numbers as described earlier, which prevents old entries from being accepted.

## Recommendations For Metadata Clients

Similar to the recommendations for metadata servers, this section gives some recommendations to application developers willing to implement a metadata client. Following these recommendations will facilitate interoperability between applications and also, provide some good security foundation for the clients. A metadata client refers to the component that communicates with a metadata server and maintains the user’s trusted metadata mapping. This may be implemented as part of a larger system, or may be an independent component (which could be shared between multiple other systems, e.g. a wallet frontend and a blockchain explorer).

- The metadata client MUST allow the metadata server (or servers) that it references to be configured by the end-user.
- The metadata client MUST maintain a local mapping of trusted keys and metadata entries.
- The metadata client MUST only accept updates with a higher sequence number than the entry it currently has.
- The metadata client MUST always verify well-formedness or metadata entries before accepting them.
- The metadata client MUST always verify any signatures on metadata entries before accepting them.
- The metadata client SHOULD allow browsing of its trusted keys.
- The metadata client SHOULD allow modifications of its trusted keys by the end-user.
- The metadata client SHOULD use a Trust On First Use (TOFU) strategy for updating this store. When an update is requested for a metadata entry, the client should query the server, but not trust the resulting metadata entry unless the user agrees to use it (either by explicit consent, or implicitly via the set of trusted keys). If the entry is trusted, it should be copied to the local store.
- The metadata client MAY be configurable to limit the amount downloaded.
- The metadata client MAY accept user updates for metadata entries.

# Rationale

## Interfaces and progressive enhancement

The design space for a metadata server is quite large. For example, any of the following examples could work, or other combinations of these features:

- A single centralized server maintained by the Cardano Foundation, and updated by emailing the administrator (no user-facing front end website)
- An open-source federation of servers with key-based authentication.
- A commercial server with an account-based system, a web-frontend, and a payments system for storage.

This design aims to be agnostic about the details of the implementation, by specifying only a very simple interface between the client, server, and system-component users (wallet, etc.). This allows:
- Progressive enhancement of servers over time. Initially servers may provide a very bare-bones implementation, but this can be improved later.
- Competition between multiple implementations, including from third parties.

## Decentralization

For much of the metadata we are concerned with there is no “right” answer. The metadata server is thus playing a key trusted role - even if that trust is partial because users can rely on attestation signatures. We therefore believe that it is critical that we allow users to choose which metadata server (or servers) they refer to.

An analogy is with DNS nameservers: these are a trusted piece of infrastructure for any particular user, but users have a choice of which nameservers to use, and can use multiple.

This also makes it possible for these servers to be a true piece of community infrastructure, rather than something wedded to a major player (although we hope that the Cardano Foundation and IOHK will produce a competitive offering).

## Verifiable vs non-verifiable metadata

A key distinction is between metadata that is verifiably correct and that which is non-verifiable.

The key example of verifiable metadata is hashe pre-images. Where the metadata subject is a hash, the preimage of that hash is verifiable metadata, since we can simply hash it and check that it matches. This covers several cases that we are interested in:

- Mapping script hashes to the script
- Mapping public key hashes to the public key

However, most metadata is non-verifiable:

- Human-readable names for scripts are not verifiable: there is no “right” answer to what the name of a script is.
- Many scripts do not have an obvious “owner” (certainly this is true for Plutus scripts), but even for those which do (e.g. phase-1 monetary scripts) this does not mean that the owner is trusted! See the “Security” section below for more discussion on trust.
- Any associations with authors, websites, icons, etc are similarly non-verifiable as there is no basis for establishing trust.

## Security

Most of the security considerations relate to non-verifiable metadata. Verifiable metadata can generally always be accepted as is (provided that it is verified). Our threat model is that non-verifiable metadata may always have been provided by an attacker.

Accepting non-verifiable metadata blindly can lead to attacks. For example, a malicious server or user might attempt to name their currency “Ada”. If we blindly accept this and overwrite the existing mapping for “Ada”, this would lead to easy phishing attacks. The approach we take is heavily inspired by petname systems, GPG keyservers, and local address books. The user always has a local mapping which is trusted, and then adding to or updating that mapping requires explicit user consent, unless we can prove that this is trustworthy (i.e. the metadata is verifiable).

How can users decide whether to trust an update? This is where the attestation signatures come into play. If a user trusts the entity which signs the metadata record, that may be sufficient for them to accept it as a legitimate update. 

Clients could also be tricked into downloading large amounts of metadata that the user does not want. For this reason clients should expose some kind of configurable download limiting, and we suggest that the server set the Content-Length header to support this. However, this problem is no worse than that faced by the average web browser, so we do not think it will be a problem in practice.

Clients also need to worry about replay attacks, where they are sent old (correctly signed) records in an attempt to “roll back” a legitimate update. The easiest way to avoid this is to correctly implement sequence numbers, in which case old updates will be rejected.

## Data storage location

This design needs to store a fair amount of data in a shared location. We might wonder whether we should use the blockchain for this: we could store metadata updates in transaction metadata.

However, storing this information on-chain does not actually help us:

- The trust model for metadata is different than that of the ledger and transactions. The only trust we have (and can expect to have) in the metadata is that it is signed by a particular key, regardless of the purpose or nature of the data. E.g. when posting a script, there is no explicit association between the script and the signing key other than the owner of the key choosing to post it
- The metadata is precisely that: metadata. While it is about the chain, it does not directly affect ledger state transitions and therefore we should not require it to be associated with a specific transaction.

Besides, on-chain storage comes with considerable downsides:

- Higher cost to users for modifications and storage
- Increases in the UTXO size
- Awkwardness of querying the data
- Size limits on transaction metadata

For this reason, we think that a traditional database is a much better fit. However, it would be perfectly possible for someone to produce an implementation that was backed by the chain if they believed that that could be competitive.

## Storage cost

Metadata may potentially be sizable. For example, preimages of hashes can in principle be any size!

Servers will want some way to manage this to avoid abuse. However, this is a typical problem faced by web services and can be solved in the usual ways: size limits per account, charging for storage, etc.

# Backwards compatibility

See [Special Case: Phase-1 Monetary Policies](#special-case--phase--1-monetary-policies) which covers existing implementations. 

# Reference implementation

- https://github.com/input-output-hk/offchain-metadata-tools

# Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode)
