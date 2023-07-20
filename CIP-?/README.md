---
CIP: ?
Title: Governance Action Metadata Standard
Category: Metadata
Status: Proposed
Authors:
    - Pi Lanningham <pi@sundaeswap.finance>
Implementors: []
Discussions:
    - https://github.com/cardano-foundation/cips/pulls/?
Created: 2023-04-09
License: CC-BY-4.0
---

## Abstract

This Cardano Improvement Proposal (CIP) introduces a standardized and flexible metadata format for governance actions in the Cardano ecosystem. While the ledger does not enforce the structure of metadata, providing a standard for metadata will enable better tooling, improved interoperability, and more consistent display across wallets, blockchain explorers, and other tools. This CIP aims to strike a balance between flexibility and structure to facilitate high-quality tooling, without limiting expressivity with regards to user expression.

### Acknowledgements

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
  - Matthias Bankort
  - All Edinburgh Workshop attendees
</details>

## Motivation

With the advent of the Voltaire era, Cardano is moving towards a decentralized governance model. CIP-1694 addresses a potential technical implementation of ledger rules for creating, voting on, and ratifying proposed changes to the ledger. The ledger has no mechanism or desire to validate this metadata, and as a result, the official specification leaves the format of this metadata unspecified.

To facilitate rich user experiences for the various governance actors, however, it would be beneficial to have a suggested universal format for this metadata, allowing deep and interconnected discovery and exploration of this metadata. This CIP seeks to provide that standard format, and a minimal set of fields for various governance actions, leavine the true depth of metadata to be defined later through the extensibility mechanism outlined below.

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
- The hash included in the anchor MUST be a tagged hash, such as `SHA256:{hash}`

<!--
Open questions:
 - Should we pick a specific hash, instead of using a tagged hash?
 - what hashes are supported?
-->

### Versioning

[JSON-LD](https://json-ld.org/) is a standard for describing interconnected JSON documents that use a shared vocabulary.

In a JSON-LD document, every field is uniquely tied to some globally unique identifier by means of an Internationalized Resource Identifier (IRI). Different machine-consumers can then know that they agree on the interpretation of these fields.

The shared vocabulary of fields is standardized within the scope of a document via a `@context` field. This allows a compositional / extensible approach to versioning, similar to the recent changes to [CIP-0030](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0030/README.md). Rather than specifying a version number and forcing competing standards to compete for what the "next" version number will include, instead a wide variety of standards are allowed and encouraged. Tool authors MAY support those which are the most beneficial or common. This creates an organic, collaborative evolution of the standard.

 - A governance metadata document MAY include a `@context` field.
 - A governance metadata document MAY include a `@type` field, referring to a specific type of document from the included `@context`s. 
 - The `@context` field, if included, MUST be a valid JSON-LD @context field; the basics are described below. 
   - It MAY be a string, in which case it MUST be the IRI of a jsonld document describing the shared vocabulary to assume when interpreting the document.
   - It MAY be an object, where each key refers to a property name, and the value refers to the IRI describing how that field should be interpreted.
   - It MAY be an array, including multiple contexts, which are processed in order.
   - For a full understanding of the @context field, refer to the [JSON-LD specification](https://www.w3.org/TR/json-ld/).
 - If the metadata document is missing the `@context` field, it will be assumed to refer to [./cip-?.common.jsonld]
 - Future CIPs may standardize common contexts, and SHOULD attempt to reuse common terminology and SHOULD avoid naming collisions.
 - Tool authors MAY choose which contexts to support, but MUST make a best effort to display the metadata in the presence of unrecognized context, up to and including gracefully falling back to a raw display of the JSON document.

### Governance Transaction Types

In CIP-1694 (and likely any alternative or future evolution of it), there are a number of certificates that can be attached to a transaction pertaining to governance; each of these is equipped with an "anchor", which can refer to an external document. This CIP provides the following JSON-LD schemas intended to represent a fairly minimal set of properties and types for each type of transaction:

 - [Common Definitions](./cip-?.common.jsonld)
 - [Governance Action](./cip-?.action.jsonld)
 - [DRep (Voter) Registration](./cip-?.registration.jsonld)
 - [DRep (Voter) Retirement](./cip-?.retirement.jsonld)
 - [DRep (Voter) Vote](./cip-?.vote.jsonld)
 - [DRep (Voter) Delegation](./cip-?.delegation.jsonld)
 - [Constitutional Committee Vote](./cip-?.cc-vote.jsonld)

<!-- The above schemas aren't written yet; this is one of the areas I could use some help in, and I didn't want that to be a further impediment to me getting this draft out the door, as it's taken me long enough as it is -->

Additionally, someone may wish to augment a previous piece of metadata with new information, divorced from the transaction that initially published it; this may be useful, for example, to provide additional arguments in favor of or against a proposal, provide translations to other languages, provide a layman's explanation of a highly technical document, etc.

To this end, this CIP reserves [metadatum label 1694](../CIP-0010/README.md) for publishing these kinds of augments on-chain. This CIP also provides a special JSON-LD schema specifically for these documents:

 - [Augmentation](./cip-?.augmentation.jsonld)

NOTE: These actions are based on CIP-1694, but could be repurposed for any governance CIP with minimal changes.

The rest of this document will provide a high level description of the properties described in each of the schemas above.

#### Common properties

The following properties are considered common to all types of transactions, and the minimal set needed for "minimum viable governance":

 - Authors: The primary contributors and authors for this metadata document
   - An array of objects
   - Each object may have an address, a display name, and optionally a WC3 DID
   - Each address mentioned MUST sign the transaction
   - Tooling authors SHOULD validate these signatures; if absent or invalid, tooling authors SHOULD make this clear in the UI
   <!-- Open to other suggestions for how to securely prove authenticity / endorsement -->
 - Language: the ISO 639-1 that any prose in this metadata is written in
   - Tooling authors MAY provide automatic translation, but SHOULD make the original prose easily available
 - Justification
   - Freeform text that explains *why* this proposal / vote / registration / retirement is being proposed / made / etc.
   - Tooling authors MAY emphasize that this justification represents the view of the authors only
 - External updates
   - A array of objects
   - Each object may have a URL, and a type
   - The purpose is to allow "additional updates", that aren't locked in by a hash
   - Tooling authors MAY fetch and parse this metadata according to this standard,
   - If so, Tooling authors MUST emphasize that this information is second-class, given that it might have changed
  <!-- Types TBD; I was thinking something like "Blog", "Twitter Feed", "RSS", and "Metadata" -->

#### Specific fields

This CIP currently doesn't standardize any fields specific to each type of transaction, beyond specifying a `@type` for each type of transaction.

<!--
#### Governance Action

 - Authorship history
  - First draft written timestamp
  - Other drafts / timestamps (reference)
  - Final draft timestamp
 - Time and materials budget
 - Time limit / sensitivity information
   - Urgent hardfork to fix a bug
   - Payout deadline
 
 - Proposal-type specific proposals
   - No Confidence
   - New CC
   - Constitution
   - Protocol Parameters
    - Simulation data
   - Treasury Payout
    - category 
    - payment target information (if different from author)
      (Including signature)
   - Info
     - Content

#### DRep Registration

 - Platform / Values
 - DID / Social Media / Website
 - Group / Organization
 - Stake Pool information?

#### DRep Retirement

 - Recommended Replacement
   - Who do you suggest your delegators delegate to in your stead?
 - Press release? (is this just justification?)
 - "I'll come back if ___"
 - "This is in protest of {governance action}"

#### Vote Casting

 - 

#### Vote Delegation

 - 

#### Cast Constitutional Committee Vote

 -  -->

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

<!--
Notes from workshop:
 - Markus wants to think deeply about pool metadata, and the notion of extended metadata and if there are lessons we can learn from that
 - Should we have a notion of where to find "addendums", which might change / be added; we can't update this metadata because it will change the hash, but we can have a type of data that is "less permanent" for example revisions, new information that comes to light, a DRep has their mind changed on a vote, etc.
-->

## Rationale: how does this CIP achieve its goals?

Here are the goals this CIP seeks to achieve, and the rationale for how this specific solution accomplishes them:

 - Standardize a format for rich metadata related to cardano governance
   - Standardizing on JSON-LD provides an industry standard, yet highly flexible format for effectively arbitrary structured data
 - Standardize a minimal and uncontroversial set of fields to support "Minimal Viable Governance"
   - This CIP fully specifies the Authors, Language, Justification, and External Updates fields
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
 - A custom JSON format, with reference to CIPs
  - An initial draft of this proposal had an `extensions` field that operated very similar to `@context`
  - Instead, this CIP chose to go with an industry standard format to leverage the existing tooling and thought that went into JSON-LD
 - CBOR or other machine encoding
  - The metadata in question, despite being proliferous, is not expected to to be an undue storage burden; It's not, for example, video data, or storing billions of records.
  - It is more important, then, that the metadata be human readable, so that tooling authors have the option to show this data in its raw format to a user, and for it to be loosely understandable even by non-technical users.

## Path to Active

The path for this proposal to be considered active within the community focuses on 4 key stages: Feedback, Implementation, Adoption, and Extension.

### Acceptance Criteria

In order for this standard to be active, the following should be true:

 - At least 1 month of feedback has been solicited, and any relevant changes with broad consensus to the proposal made
 - At least 2 client libraries in existence that support reading an arbitrary JSON file, and returning strongly typed representations of these documents
 - At least 1 widely used *producer* of governance metadata (such as a wallet, or the cardano-cli)
 - At least 1 widely used *consumer* of governance metadata (such as a blockchain explorer, governance explorer, voting dashboard, etc)
 - At least 1 CIP in the "Proposed" status that outlines additional fields to extend this metadata

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

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).