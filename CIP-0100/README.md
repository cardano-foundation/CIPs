---
CIP: 100
Title: Governance Metadata
Category: Metadata
Status: Active
Authors:
    - Pi Lanningham <pi@sundaeswap.finance>
Implementors: []
Discussions:
    - https://github.com/cardano-foundation/cips/pulls/556
Created: 2023-04-09
License: CC-BY-4.0
---

## Abstract

This Cardano Improvement Proposal (CIP) introduces a standardized and flexible metadata format for governance events in the Cardano ecosystem. While the ledger does not enforce the structure of metadata, providing a standard for metadata will enable better tooling, improved interoperability, and more consistent display across wallets, blockchain explorers, and other tools. This CIP aims to strike a balance between flexibility and structure to facilitate high-quality tooling, without limiting expressivity with regards to user expression.

For the many contributors to this proposal, see [Acknowledgements](#acknowledgements).

## Motivation

With the advent of the Voltaire era, Cardano is moving towards a decentralized governance model. CIP-1694 addresses a potential technical implementation of ledger rules for creating, voting on, and ratifying proposed changes to the ledger. The ledger has no mechanism or desire to validate this metadata, and as a result, the official specification leaves the format of this metadata unspecified.

To facilitate rich user experiences for the various governance actors, however, it would be beneficial to have a suggested universal format for this metadata, allowing deep and interconnected discovery and exploration of this metadata. This CIP seeks to provide that standard format, and a minimal set of fields for various governance actions, leaving the true depth of metadata to be defined later through the extensibility mechanism outlined below.

While this specification is written with CIP-1694 in mind, many of the ideas should be equally suitable for any other governance proposal, provided that proposal has a mechanism for attaching metadata to a governance action.

Explicitly, here are the goals this CIP is trying to satisfy:
 - Standardize a format for rich metadata related to cardano governance
 - Standardize a minimal and uncontroversial set of fields to support "Minimal Viable Governance"
 - Leave that format open to extension and experimentation
 - Enable tooling and ecosystem developers to build the best user experiences possible
 - Provide a set of best practices that tooling and ecosystem developers can rely on for the health and integrity of this data

## Specification

This section outlines the high level format and requirements of this standard.

      The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL
      NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED",  "MAY", and
      "OPTIONAL" in this document are to be interpreted as described in
      [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119).

- On chain metadata actions in CIP-1694 (and likely any alternative proposals) have the notion of an "Anchor"; this is the URL and a hash for additional, non-ledger metadata about the action.
- Tools which publish governance related transactions SHOULD publish metadata via these fields.
- While that content MAY be in any format, following any standard or non-standard, for the remainder of this document SHOULD/MUST will refer to documents that are following this specification.
- The content hosted at the anchor URL MUST be a JSON-LD document according to the rest of this specification.
- This document SHOULD include `@context` and `@type` fields below to aid in interpretation of the document.  
- The JSON document SHOULD be formatted for human readability, for the sake of anyone who is manually perusing the metadata.
- That content SHOULD be hosted on a content addressable storage medium, such as IPFS or Arweave, to ensure immutability and long term archival.
- The hash in the anchor MUST be the hash of the the raw bytes of the content, using the hashing algorithm specified in the `hashAlgorithm` field. Currently only blake2b-256 is supported.
- For the purposes of hashing and signature validation, we should use the [canonical RDF triplet representation](https://www.w3.org/TR/rdf-canon/), as outlined in the JSON-LD specification.

### Versioning

[JSON-LD](https://json-ld.org/) is a standard for describing interconnected JSON documents that use a shared vocabulary.

In a JSON-LD document, every field is uniquely tied to some globally unique identifier by means of an Internationalized Resource Identifier (IRI). Different machine-consumers can then know that they agree on the interpretation of these fields.

The shared vocabulary of fields is standardized within the scope of a document via a `@context` field. This allows a compositional / extensible approach to versioning, similar to the recent changes to [CIP-0030](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0030/README.md). Rather than specifying a version number and forcing competing standards to compete for what the "next" version number will include, instead a wide variety of standards are allowed and encouraged. Tool authors MAY support those which are the most beneficial or common. This creates an organic, collaborative evolution of the standard.

Note: Any URI's in the @context field SHOULD be content-addressable and robustly hosted; losing access to the schema is less dangerous than losing access to the metadata itself, but should still prefer strong and immutable storage options for the preservation of context.

 - A governance metadata document MAY include a `@context` field.
 - A governance metadata document MAY include a `@type` field, referring to a specific type of document from the included `@context`s. 
 - The `@context` field, if included, MUST be a valid JSON-LD @context field; the basics are described below. 
   - It MAY be a string, in which case it MUST be the IRI of a jsonld document describing the shared vocabulary to assume when interpreting the document.
   - It MAY be an object, where each key refers to a property name, and the value is either an IRI to a schema describing that field, or an object with that definition inlined.
   - It MAY be an array, including multiple contexts, which are merged in order with a "most-recently-defined-wins" mechanism.
   - For a full understanding of the @context field, refer to the [JSON-LD specification](https://www.w3.org/TR/json-ld/).
 - Each IRI in the `@context` field SHOULD refer to a schema hosted via a robust, content addressable, and immutable storage medium such as IPFS, Arweave, etc.
 - If the metadata document is missing the `@context` field, it will be assumed to refer to [./cip-0100.common.jsonld]
 - Future CIPs may standardize common contexts, and SHOULD attempt to reuse common terminology and SHOULD avoid naming collisions.
 - Tool authors MAY choose which contexts to support, but MUST make a best effort to display the metadata in the presence of unrecognized context, up to and including gracefully falling back to a raw display of the JSON document.

**Extensions to the governance metadata standard can take one of two forms**:
- CIP-0100 itself can be updated through the normal CIP process to provide additional clarity on any concepts that are giving people trouble with adoption, or to correct inaccuracies.
- A new CIP, which defines new JSON-LD vocabulary to extend this one, which seeks broad adoption.
- A new context document, used in the wild, but not officially standardized, and which doesn't seek broad adoption.

### Hosting

In CIP-1694 (and likely any alternative or future evolution of it), there are a number of certificates that can be attached to a transaction pertaining to governance; each of these is equipped with an "anchor", which is a URI at which can be found additional metadata.

While this metadata can be published anywhere, external hosting may be unavailable to some users. Therefore, we recognize the transaction metadata as an effective tool for a "common town square" for hosting and discoverability, and reserve [metadatum label 1694](../CIP-0010) for publishing governance related metadata on-chain.

With the help of [CIP-?](https://github.com/cardano-foundation/CIPs/pull/635), the anchor can then refer to the metadata of another transaction, or even the metadata of the transaction being published itself.

When published on-chain, the CBOR encoding of this metadata, when published on-chain, follows [the standard convention](https://developers.cardano.org/docs/get-started/cardano-serialization-lib/transaction-metadata/#json-conversion) used for converting JSON to CBOR in transaction metadata.

### Augmentations

Additionally, someone may wish to augment a previous piece of metadata with new information, divorced from the transaction that initially published it; this may be useful, for example, provide additional arguments in favor of or against a proposal, provide translations to other languages, provide a layman's explanation of a highly technical document, etc.

These use the same format, but leverage the `references` field to point to the documents that they wish to extend.

These can, in theory, be published anywhere, but the use of metadatum label 1694 mentioned above is particularly useful in this case.

### Context and Schema

We expect a rich ecosystem of CIPs to emerge defining different extensions, so this CIP provides only an initial base-line MVP of fields, defined in the following JSON-LD and JSON Schema files:

 - [JSON-LD Context](./cip-0100.common.jsonld)
 - [JSON Schema](./cip-0100.common.schema.json)

The rest of this document will provide a high level description of how these fields should be interpreted

### High level description

The following properties are considered common to all types of transactions, and the minimal set needed for "minimum viable governance":

- `hashAlgorithm`: The algorithm used to hash the document for the purposes of the on-chain anchor; currently only supports blake2b-256
- `authors`: The primary contributors and authors for this metadata document
  - An array of objects
  - Each object MAY have a `name` property, which serves as a display name
  - Each object MUST have a `witness` field, which contains a signature of the `body` of the document
  - The witness may define a `@context`, describing the manner in which the document has been witnessed
  - A default witness scheme context is described in a later section
  - Tooling authors SHOULD validate witnesses they understand
  - If witnesses aren't validated, tooling authors SHOULD emphasize this to the user
  - If absent or invalid, tooling authors SHOULD make this clear to the user
- `body`: The material contents of the document, separate for the purposes of signing
  - `references`
    - An array of objects
    - Each object specifies a `@type`, which is either "GovernanceMetadata" or "Other"
    - Each object specifies a `label`, which serves as a human readable display name
    - Each object specifies a `uri`; when the type is set to "GovernanceMetadata", the URI should point to another CIP-0100 compliant document
  - `comment`
    - Freeform text attached to the metadata; richer structures for justifying the transaction this is attached to is left to future CIPs
    - Tooling authors SHOULD emphasize that these comments represent the *authors* views, and may contain bias.
  - `externalUpdates`
    - A array of objects
    - Each object can have a `@context` defining how to interpret it
    - by default, assumed to just be an object with a `title` and `uri` field
    - The purpose is to allow "additional updates", that aren't written yet, such as a blog or RSS feed
    - Tooling authors MAY fetch and parse this metadata according to this standard,
    - If so, Tooling authors MUST emphasize that this information is second-class, given that it might have changed

Additionally, we highlight the following concepts native to json-ld that are useful in the context of governance metadata:
 - [@language](https://www.w3.org/TR/json-ld11/#string-internationalization)
   - The `@context` field SHOULD specify a `@language` property, which is an ISO 639-1 language string, to define a default language for the whole document
   - Specific sub-fields can specify different languages
   - The `@context` field may specify a `@container` property set to `@language`, in which case the property becomes a map with different translations of the property
   - Tooling authors MAY provide automatic translation, but SHOULD make the original prose easily available

### Hashing and Signatures

When publishing a governance action, the certificate has an "anchor", defined as a URI and a hash of the content at the URI.

For CIP-0100 compliant metadata, the hash in the anchor should be the blake2b-256 hash of the raw bytes received from the wire.
Hashing directly the original bytes ensures that there are no ambiguities, since the process doesn't depend on parsing the metadata, which can be the source of conflicts in different implementations.

A metadata has a number of authors, each of which MUST authenticate their endorsement of the document in some way.

This is left extensible, through the use of a new context, but for the purposes of this CIP, we provide a simple scheme.

Each author should have a witness. The witness will be an object with an `witnessAlgorithm` (set to ed25519), a `publicKey` (set to a base-16 encoded ed25519 public key), and a `signature`, set to the base-16 encoded signature of the body field.

Because the overall document may change, it is neccesary to hash a subset of the document that is known before any signatures are collected. This is the motivation behind the `body` field.

The signature is an ed25519 signature using the attached public key, and the payload set to the blake2b-256 hash of the `body` field. Specifically, this field is canonicalized in the following way.
- Canonicalize the whole document according to [this](https://w3c-ccg.github.io/rdf-dataset-canonicalization/spec/) specification.
- Identify the node-ID of the `body` node
- Filter the canonicalized document to include the body node, and all its descendents
- Ensure the file ends in a newline
- Hash the resulting file with blake2b-256

### Best Practices

This section outlines a number of other best practices for tools and user experiences built on top of this standard, as brainstormed by the Cardano community.

 - If the hash in the anchor doesn't match the computed hash of the content, it is imperative to make that obvious to the user.
   - Without this being obvious, there are severe and dramatic attack vectors for manipulating user votes, delegators, etc.
   - NOTE: The term "MUST" in the RFC-2119 sense isn't used here because it's unenforcable anyway, but if these hashes *aren't* checked, you **SHOULD** inform the user that you are not checking the integrity of the data.
   - You MAY do this by displaying a prominent warning, or potentially fully barring access to the content.
 - You SHOULD provide a way to access the raw underlying data for advanced or diligent users.
   - This MAY be in the form of a JSON viewer, or a simple link to the content.
 - You SHOULD gracefully degrade to a simple raw content view if the metadata is malformed in some way, or not understood.
 - You SHOULD provide links and cross references whenever the metadata refers to another object in some way
   - For example, a proposal may link to the sponsoring DReps, which may have their own view within the tool you're building
 - If you are hosting the content for the user, you SHOULD use a content-addressable hosting platform such as IPFS or Arweave
 - If the content is self-hosted, you SHOULD take care to warn the user about changing the content
   - For example, you CAN detect well-known content-addressable file storage platforms such as IPFS or Arweave, and display an extra warning if the content is not hosted on one of those

## Rationale: how does this CIP achieve its goals?

Here are the goals this CIP seeks to achieve, and the rationale for how this specific solution accomplishes them:

 - Standardize a format for rich metadata related to cardano governance
   - Standardizing on JSON-LD provides an industry standard, yet highly flexible format for effectively arbitrary structured data
 - Standardize a minimal and uncontroversial set of fields to support "Minimal Viable Governance"
   - This CIP specifies a minimal number of fields: hash-algorithm, authors, justification, external-updates, and @language
   - Each of these fields is essential for the global accessibility of this data, and enables tooling that promotes a well-informed voting populace
 - Leave that format open to extension and experimentation
   - JSON-LD has, built in, a mechanism for extending and experimenting with new field types
   - Anyone can extend this metadata, even independent of the CIP process, with their own field definitions
   - Tooling authors can, independently, choose which extensions to support natively, while also surfacing fields they don't recognize in more generic ways.
 - Enable tooling and ecosystem developers to build the best user experiences possible
   - The `@context` field of a JSON-LD document allows tooling authors to confidently and consistently interpret a known field within the metadata, with reduced risk of misinterpreting or misrepresenting the authors intent
   - This metadata can also reference other objects and documents in the ecosystem, providing for rich exploration needed for an informed voting populace.
 - Provide a set of best practices that tooling and ecosystem developers can rely on for the health and integrity of this data
   - This CIP has an explicit section of best practices, brainstormed with attendees of a workshop dedicated to the purpose.

The following alternatives were considered, and rejected:
 - Plain JSON documents
   - While ultimately flexible and simple, there is a risk that with no way to structure what is *officially* supported, and the interpretation of each field, tooling authors would have one hand tied behind their back, and would be limited to a minimum common denominator.
 - Canonicalising the whole document before hashing it
   - Canonicalising requires initially parsing the file as a json, which can by itself cause ambiguities
 - A custom JSON format, with reference to CIPs
  - An initial draft of this proposal had an `extensions` field that operated very similar to `@context`
  - Instead, this CIP chose to go with an industry standard format to leverage the existing tooling and thought that went into JSON-LD
 - CBOR or other machine encoding
  - The metadata in question, despite being proliferous, is not expected to to be an undue storage burden; It's not, for example, video data, or storing billions of records.
  - It is more important, then, that the metadata be human readable, so that tooling authors have the option to show this data in its raw format to a user, and for it to be loosely understandable even by non-technical users.

### Test Vectors

See [test-vector.md](./test-vector.md) for example.

## Path to Active

The path for this proposal to be considered active within the community focuses on 4 key stages: Feedback, Implementation, Adoption, and Extension.

### Acceptance Criteria

In order for this standard to be active, the following should be true:

 - [x] At least 1 month of feedback has been solicited, and any relevant changes with broad consensus to the proposal made
 - [ ] At least 2 client libraries in existence that support reading an arbitrary JSON file, and returning strongly typed representations of these documents
   - [cardano-governance-metadata-lib](https://github.com/SundaeSwap-finance/cardano-governance-metadata)
 - [x] At least 1 widely used *producer* of governance metadata (such as a wallet, or the cardano-cli)
   - [1694.io](https://www.1694.io)
   - [GovTool](https://gov.tools)
   - [Tempo.vote](https://tempo.vote)
 - [x] At least 1 widely used *consumer* of governance metadata (such as a blockchain explorer, governance explorer, voting dashboard, etc)
   - [1694.io](https://www.1694.io)
   - [Adastat](https://adastat.net)
   - [Cardanoscan](https://cardanoscan.io)
   - [GovTool](https://gov.tools)
   - [Tempo.vote](https://tempo.vote)
 - [x] At least 1 CIP in the "Proposed" status that outlines additional fields to extend this metadata
   - [CIP-108 | Governance Metadata - Governance Actions](../CIP-0108/README.md)
   - [CIP-119 | Governance metadata - DReps](../CIP-0119/README.md)
   - [CIP-136 | Governance metadata - Constitutional Committee votes](../CIP-0136/README.md)

### Community Tooling

Below you can find a growing list of community tools which let you sign / verify / canonize / manipulate governance metadata JSON-LD data:
- [cardano-signer](https://github.com/gitmachtl/cardano-signer?tab=readme-ov-file#cip-100--cip-108--cip-119-mode) : A tool to sign with author secret keys, verify signatures, canonize the body content (Linux/Arm/Win/Mac)
- [cardano-governance-metadata-lib](https://github.com/SundaeSwap-finance/cardano-governance-metadata) : A rust library for interacting with Cardano Governance Metadata conforming to CIP-100 (rust)

### Implementation Plan

The key stages to get this proposal to active, and the motivation for why each stage is valuable, is outlined below:

- Solicitation of feedback
  - While this proposal represents the input of many prominent community members, it is by no means exhaustive
  - This CIP should receive a moderate, but not egregious, amount of scrutiny and feedback within it's initial goals
- Implementation
  - The effectiveness of this standard is greatly amplified if tools and SDKs are built which allow parsing arbitrary data according to this standard
  - Sundae Labs has offered to build Rust and Golang libraries that capture the types outlined above, and implementations in other languages are welcome
  <!-- In particular, I would love to find someone to own the Haskell implementation for easy integration into the cardano-cli -->
- Adoption
  - This standard is most effective if it receives widespread adoption
  - Therefore, a path to active includes engaging prominent members of the ecosystem, such as wallets and explorers, to begin producing and consuming documents in accordance with the standard.
- Extension
  - Finally, this standard chooses to fully specify very little of the total surface area of what could be expressed in governance metadata
  - Therefore, to prove the extensibility of the standard, at least one follow-up CIP should be drafted, extending the set of fields beyond "Minimum Viable Governance"

## Acknowledgements

<details>
  <summary><strong>First draft/workshop</strong></summary>

  I would like to thank those that contributed to this first draft during the online workshop that was held on 2023-04-12.

 - CHIL Pool
 - Alex Djuric
 - Cody Butz
 - Felix Weber
 - Leo Pienasola
 - Markus Gufler
 - Michael Madoff
 - Mohamed Mahmoud
 - Thomas Upfield
 - William Ryan
 - Santiago Carmuega

</details>

<details>
  <summary><strong>Second draft</strong></summary>

  The following people helped with the second draft, out of band at at the Edinburgh workshop on 2023-07-12.

  - Ryan Williams
  - Matthias Benkort
  - All Edinburgh Workshop attendees

</details>
<details>
  <summary><strong>Second Workshop</strong></summary>

  The following people helped with the third draft during the online workshop held on 2023-11-02.

  - Mike Susko
  - Thomas Upfield
  - Lorenzo Bruno
  - Ryan Williams
  - Nils Peuser
  - Santiago Carmuega
  - Nick Ulrich
  - Ep Ep

</details>

<details>
  <summary><strong>Third Workshop</strong></summary>

  The following people helped with the third draft during the online workshop held on 2023-11-10.

  - Adam Dean
  - Rhys Morgan
  - Thomas Upfield
  - Marcel Baumberg

</details>

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
