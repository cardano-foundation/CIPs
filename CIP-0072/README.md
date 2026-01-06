---
CIP: 72
Title: Cardano dApp Registration & Discovery
Status: Proposed
Category: Metadata
Authors: 
  - Bruno Martins <bruno.martins@iohk.io>
  - Mateusz Czeladka <mateusz.czeladka@cardanofoundation.org>
  - Daniel Main <daniel.main@iohk.io>
Implementors: ["Lace Wallet dApp Store", "DappsOnCardano dApp Store"]
Discussions:
  - https://github.com/cardano-foundation/CIPs/pull/355
Created: 2022-10-18
License: CC-BY-4.0
---

## Abstract

dApp developers do not have a standardised method to record immutable, persistent claims about their dApp(s) that their users can verify. A dApp developer needs to "register" their dApp by providing a set of claims about their dApp(s) that can be verified by the user. This CIP describes a standardised method for dApp developers to register their dApp(s) on-chain and for users to verify the claims made by dApp developers.

This proposal aims to standardise the process of dApp registration and verification, and to provide a set of claims that dApp developers can use to register their dApp(s).

## Motivation: Why is this CIP necessary?

dApps can express a plethora of information. Some of this information could be claims about who the developer is, what the dApp's associated metadata is, and more. This data lacks standardisation, persistence, and immutability. Data without these features, means that dApp users cannot verify if the dApp's expressed information is consistent across time. The goal of this CIP is to formalise how dApps register their information with a new transaction metadata format that can record the dApp's metadata, ownership, and potentially developer's identity. This formalisation means dApp users can verify if the data expressed by a dApp is consistent with what was registered on-chain.

Also, having this formalisation facilitates any actor in the ecosystem to index and query this data, and provide a better user experience when it comes to dApp discovery and usage.

## Specification

### **Definitions**

- **anchor** - A hash written on-chain (rootHash) that can be used to verify the integrity (by way of a cryptographic hash) of the data that is found off-chain.
- **dApp** - A decentralised application that is described by the combination of metadata, certificate and a set of used scripts.
- **metadata claim** - Generically any attempt to map off-chain metadata to an on-chain subject. This specification looks at dApp specific metadata claims. Caution: it is highly recommended that dApp developers provide links to a specific snapshot (version) without removing all previous snapshots / version links. Some stores may choose not to show a dApp if all off-chain historical versions are not available but instead only latest snapshot. 
- **client** - Any ecosystem participant which follows on-chain data to consume metadata claims (i.e. dApp stores, wallets, auditors, block explorers, etc.).
- **dApp Store** - A dApp aggregator application which follows on-chain data looking for and verifying dApp metadata claims, serving their users linked dApp metadata.
- **publishers** - Entities which publish metadata claims on-chain, in the case of dApps the publishers are likely the dApp developer(s). 

### **Developers / Publishers**

Developers and publishers of dApps can register their dApps by submitting a transaction on-chain that can be indexed and verified by stores, auditors and other ecosystem actors.

### **Stores / Auditors**

Stores and auditors should be able to follow the chain and find when a new dApp registration is **anchored** on-chain. They should then perform *integrity* and *trust* validations on the dApp's certificate and metadata.

#### **Suggested Validations**

- **`integrity`**: The dApp's off-chain metadata should match the metadata **anchored** on-chain.
- **`trust`**: The dApp's certificate should be signed by a trusted entity. It's up to the store/auditor to decide which entities are trusted and they should maintain and publish their own list of trusted entities. Although this entities might be well known, it's not the responsibility of this CIP to maintain this list. These entities could be directly associated with developer/publisher or not.

### **On-chain dApp Registration**

```json
{
  "subject": "b37aabd81024c043f53a069c91e51a5b52e4ea399ae17ee1fe3cb9c44db707eb",
  "rootHash": "7abcda7de6d883e7570118c1ccc8ee2e911f2e628a41ab0685ffee15f39bba96",
  "metadata": [
    "https://foundation.app/my_dapp_7abcda/tart/",
    "7abcda7de6d883e7570118c1ccc8ee2e91",
    "e4ea399ae17ee1fe3cb9c44db707eb/",
    "offchain.json"
  ],
  "type": {
    "action": "REGISTER",
    "comment": "New release adding zapping support."
  }
}
```

### Properties

*`subject`*: Identifier of the claim subject (dApp). A UTF-8 encoded string, max 64 chars. The uniqueness of this property cannot be guaranteed by the protocol and multiple claims for the same subject may exist, therefore it is required to exist some mechanism to assert trust in the *veracity* of this property.

*`type`*: The type of the claim. This is a JSON object that contains the following properties: 

- *`action`*: The action that the certificate is asserting. It can take the following values: 
  - *`REGISTER`*: The certificate is asserting that the dApp is registered for the first time or is providing an update.
  - *`DE_REGISTER`*: The certificate is asserting that the dApp is deprecated / archived. So, no further dApp's on-chain update is expected.

*`rootHash`*: The blake2b-256 hash of the entire offchain metadata tree object. This hash is used by clients to verify the integrity of the metadata tree object. When reading a metadata tree object, the client should calculate the hash of the object and compare it with the `rootHash` property. If the two hashes don't match, the client should discard the object. The metadata tree object is a JSON object that contains the dApp's metadata. The metadata tree object is described in the next section. Please note that off-chain JSON must be converted into RFC 8765 canonical form before taking the hash!

*`metadata`*: Chunks of URLs that make up the dApp's metadata are arranged in an array to accommodate the 64-character limit per chunk, allowing for the support of longer URLs. The metadata itself is a JSON object compatible with RFC 8785, containing detailed information about the dApp

### On-chain Schemas

[On-chain CDDL for registration / de-registration (Version 2.0.0)](./version_2.0.0_onchain.cddl)

which also can be expressed using JSON schema:

[dApp on-chain certificate JSON Schema (Version 2.0.0)](./version_2.0.0_onchain.json)

### Metadata Label

When submitting the transaction metadata pick the following value for `transaction_metadatum_label`:

- `1667`: dApp Registration

### Off-chain Metadata Format

The dApp Registration certificate itself doesn't enforce a particular structure to the metadata you might fetch off-chain. However, we recommend that you use the following structure:

[Off-chain dApp Registration certificate schema (Version 2)](./version_2.0.0_offchain.json)

This schema describes the minimum required fields for a store to be able to display and validate your dApp.

### Example

```json
{
  "version": "1.0.0",
  "subject": "abcdef1234567890",
  "projectName": "My dApp",
  "link": "https://www.exampledapp.com",
  "companyName": "Amazing dApp Inc.",
  "companyEmail": "contact@myamazingdapp.com",
  "companyWebsite": "https://www.myamazingdapp.com",
  "logo": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAUAAA...",
  "categories": ["DeFi", "Games"],
  "screenshots": [
    "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD...",
    "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEASABIAAD..."
  ],
  "social": [
    {
      "name": "GitHub",
      "link": "https://github.com/exampledapp"
    },
    {
      "name": "Twitter",
      "link": "https://twitter.com/exampledapp"
    }
  ],
  "description": {
    "short": "This is a short description of the dApp, giving an overview of its features and capabilities."
  },
  "releases": [
    {
      "releaseNumber": "1.0.0",
      "releaseName": "Initial Release",
      "securityVulnerability": false,
      "comment": "First major release with all core features.",
      "scripts": [
        {
          "id": "script1",
          "version": "1.0.0"
        }
      ]
    }
  ],
  "scripts": [
    {
      "id": "script1",
      "name": "Example Script",
      "purposes": ["SPEND", "MINT"],
      "type": "PLUTUS",
      "versions": [
        {
          "version": "1.0.0",
          "plutusVersion": 1,
          "scriptHash": "abc123"
        }
      ]
    }
  ]
}
```

### **Stores Custom fields**

Each store might have their own requirements for the metadata. For example, some stores might require a field for logo, or screenshots links. The store's should adviertise what fields they require in their documentation so that developers are aware and they can include them in the metadata. 

### **Offchain Metadata Storage**

There are multiple options to store metadata offchain. The most common options are:

- [CIP-26](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0026) compliant servers
- [IPFS](https://ipfs.tech/)
- [Bitbucket](https://bitbucket.org/)
- Any REST JSON API

## Rationale: How does this CIP achieve its goals?

### Decoupling of dApp Registration From Certifications / Audits

We quickly reached a conclusion that it is better to separate them and keep scope of CIP smaller. During discussions it became clear that while there is
some overlap of certifications / audits with dApp registration, this overlap is small and can be even removed. At one point we wanted to couple 
certifications CIP to this CIP (e.g. via some link or dApp version) but we analyzed how dApp developers are currently following the process and we noticed
that in many cases certification / audit comes before an official dApp release on main-net. Having established it, we removed this link and not only
that dApp registration and certifications are different CIPs but they are very loosely coupled. Loose coupling has also disadvantages as it leads to a situation that in order to attest that a dApp is certified / audited, implementators will have to scan for all script hashes belonging to a dApp and check
whether those have been certified / explicitly mentioned in the audit.

### Small Metadata Anchor On Chain

This one is rather obvious but for the sake of completeness worth documenting. We analyzed how much we should put on-chain vs off-chain and we quickly reached the conclusion that it is better to keep small amount of data on-chain and larger chunk off-chain for which is what exactly CIP-26 is meant for.

### CIP-26 as *ONE* of Storage Layers

We believe that CIP-26 is geared towards storing this type of off-chain metadata format but we don't want by any means to stipulate / police this form of storage. In fact it is possible to use offchain metadata storage alternatives such as CIP-26 compatible server / direct http(s) hosting / IPFS, etc.

### How to Find Off-Chain Data?

We went back and forth whether we should actually store link (links) to off-chain metadata, eventually we settled on a solution that this is required
because there could be a situation that a dApp registration may have off-chain metadata stored somewhere but some stores have it, others don't have it. Now it is required that a dApp developer points to at least one store that has off-chain metadata (as a reference metadata).

### Optional Release Name?

Release Name is a field, which dApp developers can use on top of Release Version, it has been debated whether field should be mandatory or optional but eventually it has been agreed that we do not want to enforce this field, Release Name is an optional field, Release Version, however, needs to follow semver and is a mandatory field.

### Canonical JSON

At the begining neither on-chain, nor off-chain JSON has been following RFC 8785 (canonical JSON) but we reached a point that, due to consistency checks, we need to take hash of both on-chain and off-chain and this forced us to stipulate that both on-chain and off-chain metadata documents need to be converted
according to RFC 8785 before taking a blake2b-256 hash of them.

### Transaction Signature Scope

As any transaction in cardano network has a signature, which has a role to verify that a certain dApp owner made changes.

### Who Is The Owner?

Smart contracts are ownerless, it has been debated that there could be multiple claims to the same dApps from different parties.

The standard doesn't prevent anyone from making a claim, so it's up to the different operator to their diligence work and make their own choices of whom they trust. The signature should give the most confidence as anyone can collect known public keys from known development companies. Future CIP revisions can include DID's and Verifiable Credentials to tackle this problem in a more elegant way.

### DIDs

Since DIDs / Verifiable Credetials are not yet widely used in Cardano ecosystem, usage of them in this initial CIP version has been de-scoped.

### Categories

`Categories` is a predefined enum with values defined in the CIP / schema, it is *NOT* a free text field, rationale for this is that dApp developers will have no idea what ontology / classification to use, which will likely result in many duplicates of the same thing.

### Purpose Field As an Array or as a Single Item?

It may have been visible that we have a `purpose` field, which can be: "SPEND" or "MINT", those fields directly map to what is allowed by a Cardano Smart Contract. As of the time of writing CIP - PlutusTx does not allow a script to be both of type: "SPEND" and "MINT", however, there are new
languages on Cardano being worked on where they already allow one validator to be both spending UTxOs and minting tokens - all with the same script hash. To be open for the future it has been agreed to turn `purpose` field into `purposes` and make it a JSON array.

### Parametrised Scripts

On Cardano, there are parametrised scripts, meaning that before compilation takes place, it is possible to pass certain parameters instead of using `Datum`.
The consequence of this will be that as we pass different parameters, script hash will be changing. This is especially troublesome for things like certifications / audits but also dApp registration. This topic is being debated as part of CIP: https://github.com/cardano-foundation/CIPs/pull/385, however, it doesn't seem that there has been conclusion how to tackle this problem. For the moment, a new script hash (despite changing only a parameter) requires a re REGISTRATION to the existing dApp with a requirement to add new version(s) in the dApp's off-chain metadata.

### Often Changing Scripts

There are cases on Cardano main-net that script hashes are changing every day, most probably due to parameterised scripts. It is responsibility of the developers to issue an `REGISTRATION` command and provide on-chain and off-chain metadata following the change, for scripts that are changing daily / hourly it is envisaged that this process be automated by a dApp developer.

### Beacon Tokens Instead of Metadata

It has been argued that since anybody can make claims to dApps, this CIP instead of using metadata should use tokens. dApp developers
would mint token, which would ensure they are the owners of a given dApp. It is a certainly an interesting approach but shortcomings 
of the current solution can also be lifted by moving to DID based system and benefit of metadata is that it is easily queriable off chain
and currently stores can attest / validate multiple claims for the same dApp. Forcing dApp developers to MINT tokens would complicate this CIP
and potentially hinder it's adoption.

### Datums Instead of Metadata 

It has been suggested that we do not use metadata but rather Datums. Metadata cannot enforce format and Datums could. It has been rejected as
using Datums requires a smart contract and we want to keep this solution as accessible as possible. It is a GUI concern since if there is a 
some app that can attest validity and conformance to JSON schema - dApp Registration / Update MUST never be done that does not conform to the schema.

### Scripts / Releases Fields Are Not Required

We made a decision to change the schema so that scripts and releases are no longer required. This could help to get initial registration from dApp developers faster and some stores simply do not require dApps to add their scripts in order to be listed.

### Tags

We briefly discussed tags and we will likely introduce tags in the future. An array of tags to help stores / dApp developers categories where their dApp should show. This will complement `categories` field.

### DE_REGISTER

We added DE_REGISTER in additon to already existing `REGISTER`. The idea is that once dApp devs want to deprecate dApp they can now issue DE_REGISTER request.

### Type Field

`Type` field can be `PLUTUS` or `NATIVE`, we made it optional and there are already two dApps at least on Cardano at the time of writing, which are only using NATIVE scripts. This optional field helps to differentiante between NATIVE script based and NON_NATIVE dApps.

### Version Deprecation

We discussed scenario what to do in case a dApp team wants to deprecate a particular version. Upon a few iteration we settled on doing this in off-chain section.

### Version Security Vulnerability Flagging

It is not uncommon to see a dApp release a version and then release a fix in the new version and flag the previous version
as having security vulnerability. We are intoducing an optional field in the offchain json on the release level: `securityVulnerability": true.

### Comment Field (on-chain JSON)

We are introducing a field in the on-chain JSON only, which allows dApp development teams to provide a free text field
comment about changes they are making in a given (re-)registration request.

## Path to Active

We will evaluate for a few months if we have not missed any details, collect feedback from dApp developers, stores. We reserve right to make small changes in this time, while the proposal is in the `PROPOSED` status / state.
Once `Acceptance Criteria` are met and all comments / feedback from dApp developers is addressed, we will update the proposal to be in `ACTIVE` state.

### Acceptance Criteria

- At least 3 non trivial dApps from 3 different teams register on-chain / off-chain via following this CIP
- At least one Implementator (main-net) implements the store indexing this CIP metadata from on-chain

### Implementation Plan

- DappsOnCardano dApp Store: https://github.com/Cardano-Fans/crfa-dapp-registration-and-certification-service for DappsOnCardano.com
- Lace's Wallet dApp Store: https://github.com/input-output-hk/lace

## Copyright

[CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode)
