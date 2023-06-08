---
CIP: 72
Title: Cardano dApp Registration & Discovery
Status: Proposed
Category: Metadata
Authors: 
  - Bruno Martins <bruno.martins@iohk.io>
  - Mateusz Czeladka <mateusz.czeladka@cardanofoundation.org>
Implementors: ["Lace Wallet dApp Store", "DappsOnCardano dApp Store"]
Discussions:
  - https://github.com/cardano-foundation/CIPs/pull/355
Created: 2022-10-18
License: CC-BY-4.0
---

## Abstract

dApp developers do not have a standardised method to record immutable, persistent claims about their dApp(s) that their users can verify. A dApp developer needs to "register" their dApp by providing a set of claims about their dApp(s) that can be verified by the user. This CIP describes a standardised method for dApp developers to register their dApp(s) on-chain and for users to verify the claims made by dApp developers.

This proposal aims to standardise the process of dApp registration and verification, and to provide a set of claims that dApp developers can use to register their dApp(s).

## Motivation: why is this CIP necessary?

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

### **On-chain dApp Registration Certificate**

The on-chain dApp registration certificate MUST follow canonical JSON and be serialised according to RFC 8785 (https://www.rfc-editor.org/rfc/rfc8785). This stipulation is to avoid any ambigiutines in the signature calculation.

```json
{
  "subject": "b37aabd81024c043f53a069c91e51a5b52e4ea399ae17ee1fe3cb9c44db707eb",
  "rootHash": "7abcda7de6d883e7570118c1ccc8ee2e911f2e628a41ab0685ffee15f39bba96",
  "metadata": [
    "https://foundation.app/my_dapp_7abcda.json"
  ],
  "type": {
    "action": "REGISTER",
    "comment": "New release adding zapping support."
  },
  "signature": {
   "r": "27159ce7d992c98fb04d5e9a59e43e75f77882b676fc6b2ccb8e952c2373da3e",
   "s": "16b59ab1a9e349cd68d232f7652f238926dc24a2e435949ebe2e402a6557cfb4",
   "algo": "Ed25519−EdDSA",
   "pub": "b384b53d5fe9f499ecf088083e505f40d2a6c123bf7201608494fdb89a051b80"
  }
}
```

### Properties

*`subject`*: Identifier of the claim subject (dApp). A UTF-8 encoded string, max 64 chars. The uniqueness of this property cannot be guaranteed by the protocol and multiple claims for the same subject may exist, therefore it is required to exist some mechanism to assert trust in the *veracity* of this property.

*`type`*: The type of the claim. This is a JSON object that contains the following properties: 

- *`action`*: The action that the certificate is asserting. It can take the following values: 
  - *`REGISTER`*: The certificate is asserting that the dApp is registered for the first time or is providing an update.
  - *`DE_REGISTER`*: The certificate is asserting that the dApp is deprecated / archived. So, no further dApp's on-chain update is expected.

*`rootHash`*: The hash of the entire offchain metadata tree object. This hash is used by clients to verify the integrity of the metadata tree object. When reading a metadata tree object, the client should calculate the hash of the object and compare it with the `rootHash` property. If the two hashes don't match, the client should discard the object. The metadata tree object is a JSON object that contains the dApp's metadata. The metadata tree object is described in the next section. Please note that off-chain JSON must be converted into RFC 8765 canonical form before taking the hash!

*`metadata`*: An array of links to the dApp's metadata. The metadata is a JSON compatible RFC 8785 object that contains the dApp's metadata.

*`signature`*: The signature of the certificate. The publishers generate the signature is by first turning on-chain JSON into a canonical form (RFC 8765), hashing it with blake2b-256 and generating a signature of the hash. Stores / clients can verify the signature by repeating the process, they can use the public key to verify the signature of the certificate. Fields used for canonical JSON: ["subject", "rootHash", "metadata","type"]. Please note that a signature should be generated of blake2b-256 hash as a byte array, not as a hex represented string(!).

### On chain CDDL for registration / de-registration

```
string = bstr .size (1..64) ; tstr / string from 1 up to 64 chars only

sig_256 = bstr .size (64..64) ; 256 bytes signature (256 / 64 = 4 bytes)

transaction_metadata = {
  1667: on-chain_metadata
}

on-chain_metadata = {
  subject: string,
  rootHash: sig_256,
  metadata: [+ string] / [+ string / [+ string]],
  type: registration / de-registration,
  signature: signature,
}

registration = {
  action: "REGISTER",
  ? comment: string,
}

de-registration = {
  action: "DE_REGISTER",
  ? comment: string,
}

signature = {
  r: string,
  s: string,
  algo: text .regexp "Ed25519-EdDSA",
  pub: string,
}
```

which can be expressed using JSON schema.

### dApp on-chain certificate JSON Schema

```json
{
    "$schema":"https://json-schema.org/draft/2020-12/schema",
    "$id":"https://example.com/dApp.schema.json",
    "title": "Cardano dApp Claim",
    "description": "Registration of Cardano dApp claim.",
    "type":"object",
    "properties":{
       "subject":{
          "type":"string",
                "minLength": 1,
                "maxLength": 64,
                "pattern":"^[0-9a-fA-F]{1,64}$",
                "description":"Identifier of the claim subject (dApp). A UTF-8 encoded string, must be max 64 chars. Typically it is randomly generated hash by the dApp developer."
       },
       "rootHash":{
          "type":"string",
                "minLength": 64,
                "maxLength": 64,
                "pattern":"^[0-9a-fA-F]{64}$",
               "description":"blake2b-256 hash of the metadata describing the off-chain part of the dApp."
       },
       "metadata": {
         "type": "array",
         "description": "An array of valid URLs pointing to off-chain CIP-72 compatible metadata document. If an individual URL is longer than 64 characters, it must be expressed as an array of strings (where each string may contain at most 64 characters).",
         "items": {
           "anyOf": [{
             "type": "string",
               "minLength": 1,
               "maxLength": 64
             }, {
             "type": "array",
             "items": {
               "type": "string",
               "minLength": 1,
               "maxLength": 64
             }
           }],
           "examples": ["https://raw.githubusercontent.com/org/repo/offchain.json", ["https://raw.githubusercontent.com/long-org-name/", "long-repo-name/offchain.json"], "ipfs://QmbQDvKJeo2NgGcGdnUiUFibTzuKNK5Uij7jzmK8ZccmWp", ["ipfs://QmbQDvKJeo2NgGcGdnUiaAdADA", "UFibTzuKNKc0jA390alDAD5Uij7jzmK8ZccmWp"]]
         }
       },
       "type":{
          "type":"object",
          "description":"Describes the releases, if they are new or an updates.",
          "properties":{
             "action":{
               "type":"string",
               "enum":["REGISTER", "DE_REGISTER"],
               "description":"Describes the action this certificate is claiming; i.e 'REGISTER', for a new dApp or an update, DE_REGISTER for asserting that the dApp's development is stopped, and it is deprecated. So, no further dApp's on-chain update is to be expected."
             },
             "comment": {
                "type": "string",
                "minLength": 1,
                "maxLength": 64,
                "description": "A free text field to provide details about this particular changes (64 chars limited)."
             }
          },
          "required":[
             "action"
          ]
       },
       "signature":{
          "description":"Signature of the blake2b-256 hash of whole canonical (RFC 8785) JSON document (except signature property).",
          "type":"object",
          "properties":{
             "r":{
                "type":"string",
                "description":"A hex representation of the R component of the signature.",
                "minLength": 64,
                "maxLength": 64,
                "pattern":"^[0-9a-fA-F]{64}$"
             },
             "s":{
                "type":"string",
                "description":"A hex representation of the S component of the signature.",
                "minLength": 64,
                "maxLength": 64,
                "pattern":"^[0-9a-fA-F]{64}$"
             },
             "algo":{
               "const":"Ed25519-EdDSA"
             },
             "pub":{
                "type":"string",
                "description":"A hex representation of the public key.",
                "minLength": 64,
                "maxLength": 64,
                "pattern":"^[0-9a-fA-F]{64}$"
             }
          },
          "required":[
             "r",
             "s",
             "algo",
             "pub"
          ]
       }
    },
    "required":[
       "subject",
       "rootHash",
       "type",
       "signature"
    ]
 }
 ```

### Metadata Label

When submitting the transaction metadata pick the following value for `transaction_metadatum_label`:

- `1667`: dApp Registration

### Off-chain Metadata Format

The dApp Registration certificate itself doesn't enforce a particular structure to the metadata you might fetch off-chain. However, we recommend that you use the following structure:

```json
{
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type":"object",
    "properties": {
      "subject": {
        "type":"string",
        "minLength": 1,
        "maxLength": 64,
        "pattern":"^[0-9a-fA-F]{1,64}$",
        "description": "A subject, it must match with subject stored on chain data. A UTF-8 encoded string, 1 - 64 chars."
      },
      "projectName": {
        "type":"string",
        "description": "A project name, e.g. My dApp."
      },
      "link": {
        "type":"string",
        "description": "Website presenting a dApp.",
        "pattern": "(https?:\/\/(?:www\\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\\.[^\\s]{2,}|www\\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\\.[^\\s]{2,}|https?:\/\/(?:www\\.|(?!www))[a-zA-Z0-9]+\\.[^\\s]{2,}|www\\.[a-zA-Z0-9]+\\.[^\\s]{2,})"
      },      
      "logo": {
        "type":"string",
        "description": "URL to the logo or the base64 encoded image."
      },
      "categories": {
        "type":"array",
        "items": {
          "type": "string",
          "enum":["Games", "DeFi", "Gambling", "Exchanges", "Collectibles", "Marketplaces", "Social", "Other"]
        },
        "description": "One or more categories. Category MUST be one of the following schema definition."
      },
      "social": {
        "type":"object",
        "properties": {
          "website": {
            "type":"string",
            "description": "dApps website link.",
            "pattern": "(https?:\/\/(?:www\\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\\.[^\\s]{2,}|www\\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\\.[^\\s]{2,}|https?:\/\/(?:www\\.|(?!www))[a-zA-Z0-9]+\\.[^\\s]{2,}|www\\.[a-zA-Z0-9]+\\.[^\\s]{2,})"
          },
          "twitter": {
            "type":"string",
            "description": "An optional Twitter link.",
            "pattern": "(https?:\/\/(?:www\\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\\.[^\\s]{2,}|www\\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\\.[^\\s]{2,}|https?:\/\/(?:www\\.|(?!www))[a-zA-Z0-9]+\\.[^\\s]{2,}|www\\.[a-zA-Z0-9]+\\.[^\\s]{2,})"
          },
          "github": {
            "type":"string",
            "description": "An optional Github link.",
            "pattern": "(https?:\/\/(?:www\\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\\.[^\\s]{2,}|www\\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\\.[^\\s]{2,}|https?:\/\/(?:www\\.|(?!www))[a-zA-Z0-9]+\\.[^\\s]{2,}|www\\.[a-zA-Z0-9]+\\.[^\\s]{2,})"
          },
          "discord": {
            "type":"string",
            "description": "An optional Discord link.",
            "pattern": "(https?:\/\/(?:www\\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\\.[^\\s]{2,}|www\\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\\.[^\\s]{2,}|https?:\/\/(?:www\\.|(?!www))[a-zA-Z0-9]+\\.[^\\s]{2,}|www\\.[a-zA-Z0-9]+\\.[^\\s]{2,})"
          }
        },
        "required": ["website"]
      },
      "description": {
        "type": "object",
        "properties": {
          "short": {
            "type": "string",
            "description": "Short dApp description (no less than 40 and no longer than 168 characters).",
            "minLength": 40,
            "maxLength": 168
          },
          "long": {
            "type": "string",
            "description": "An optional long dApp description (no less than 40 and no longer than 1008 characters).",
            "minLength": 40,
            "maxLength": 1008
          }
        },
        "required": [
          "short"
        ]
      },
      "releases": {
        "type": "array",
        "items": [
          {
            "type": "object",
            "properties": {
              "releaseNumber": {
                "type": "string",
                "pattern": "^(0|[1-9][0-9]*)\\.(0|[1-9][0-9]*)\\.(0|[1-9][0-9]*)(-((0|[1-9][0-9]*|[0-9]*[a-zA-Z-][0-9a-zA-Z-]*)(\\.(0|[1-9][0-9]*|[0-9]*[a-zA-Z-][0-9a-zA-Z-]*))*))?(\\+([0-9a-zA-Z-]+(\\.[0-9a-zA-Z-]+)*))?$",
                "description": "Semver compatible release number (major.minor.patch) or (major.minor.patch-some_text) e.g. 1.2.3 or 1.1.1-alpha"
              },
              "releaseName": {
                "type": "string",
                "description": "An optional human readable release name, e.g. V1"
              },
              "securityVulnerability": {
                "type": "boolean",
                "description": "Indicates that a given version has a security vulnerability."
              },
              "comment": {
                "type": "string",
                "description": "A free text field to provide comment about this particular release, e.g. new features it brings, etc."
              },
              "scripts": {
                "type": "array",
                "items": [
                  {
                    "type": "object",
                    "properties": {
                      "id": {
                        "type": "string"
                      },
                      "version": {
                        "type": "integer"
                      }
                    },
                    "required": [
                      "id",
                      "version"
                    ]
                  }
                ]
              }
            },
            "required": [
              "releaseNumber"
            ]
          }
        ]
      },
      "scripts": {
        "type": "array",
        "items": [
          {
            "type": "object",
            "properties":{
              "id": {
                "type":"string",
                "description": "Unique Script ID (across all scripts from this dApp)."
              },
              "name":{
                "type":"string",
                "description": "An optional script name usually related to it's function."
              },
              "purposes":{
                "type":"array",
                "items": {
                    "type": "string",
                      "enum":["SPEND", "MINT"]
                },
                "description": "Purposes of the script, SPEND or MINT (notice it can be both for some modern Cardano languages)."
              },
              "type":{
                "enum":["PLUTUS", "NATIVE"],
                "description": "Script Type. PLUTUS refers to the typical PlutusV1 or PlutusV2 scripts, where as NATIVE means there has been no Plutus directly used by this is a native script."
              },
              "versions":{
                "type":"array",
                "items":[
                  {
                    "type":"object",
                    "properties":{
                      "version":{
                        "type":"integer",
                        "description":"Script version, monotonically increasing."
                      },
                      "plutusVersion":{
                        "type":"integer",
                        "enum":[1, 2]
                      },
                      "scriptHash":{
                        "type":"string",
                        "description":"Full on-chain script hash (hex).",
                        "pattern":"[0-9a-fA-F]+"
                      },
                      "contractAddress": {
                        "type":"string",
                        "description":"An optional Bech32 contract address matching script's hash."
                      }
                    },
                    "required": [
                      "version",
                      "plutusVersion",
                      "scriptHash"
                    ]
                  }
                ]
              }
            },
            "required": [
              "id",
              "purposes",
              "type",
              "versions"
            ]
          }
        ]
      }
    },
    "required": [
      "subject",
      "projectName",
      "link",
      "social",
      "categories",
      "description"
    ]
  }
  ```

This schema describes the minimum required fields for a store to be able to display and validate your dApp. You can add any other fields you want to the metadata, but we recommend that you use at least the ones described above.

### Example

```json
{
  "subject": "9SYAJPNN",
  "projectName": "My Project",
  "link": "https://myProject.app",
  "logo": "https://myProject.app/logo.png",
  "social": {
    "github": "https://mywebsite.com",
    "twitter": "https://twitter.com/my_dapp",
    "website": "https://github.com/my_dapp"
  },
  "categories": ["Games"],
  "description": {
    "short": "A story rich game where choices matter. This game is very addictive to play :)"
  },
  "releases": [
    {
      "releaseNumber": "1.0.0",
      "releaseName": "V1",
      "scripts": [
        {
          "id": "PmNd6w",
          "version": 1
        }
      ]
    }
  ],
  "scripts": [
    {
      "id": "PmNd6w",
      "name": "marketplace",
      "purposes": ["SPEND"],
      "type": "PLUTUS",
      "versions": [
        {
          "version": 1,
          "plutusVersion": 1,
          "scriptHash": "711dcb4e80d7cd0ed384da5375661cb1e074e7feebd73eea236cd68192",
          "contractAddress": "addr1wywukn5q6lxsa5uymffh2esuk8s8fel7a0tna63rdntgrysv0f3ms"
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

## Rationale: how does this CIP achieve its goals?

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

### On-Chain Signature Scope

On-chain part has a signature, which has a role to verify that a certain dApp owner made changes. In the initial version, a blake2b-256 signature was needed only for `rootHash` but following discussion, due to security concerns, decision has been made that the signature should attest the whole on-chain canonical JSON except signature field itself (because it would end up in an infinite recursion).

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

### Schema Version

We discussed and analyzed idea of schema version and or even whole CIP version. It turns out that CIP is already versioned by CIP-??? where ??? is version number. During this CIP being in `PROPOSED` state we reserve our right to make small changes to the schema / document, after CIP becomes active, it will require a new CIP. This is the current process, which other CIPs are also following.

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
