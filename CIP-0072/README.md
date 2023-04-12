---
CIP: 72
Title: Cardano dApp Registration & Discovery
Status: Proposed
Category: Metadata	
Authors: 
  - Bruno Martins <bruno.martins@iohk.io>
  - Mateusz Czeladka <mateusz.czeladka@cardanofoundation.org>
Implementors: []
Discussions:
  - https://github.com/cardano-foundation/CIPs/pull/355
Created: 2022-10-18
License: CC-BY-4.0
---

## Abstract
dApp developers do not have a standardised method to record immutable, persistent claims about their dApp(s) that their users can verify. A dApp developer needs to "register" their dApp by providing a set of claims about their dApp(s) that can be verified by the user. This CIP describes a standardised method for dApp developers to register their dApp(s) and for users to verify the claims made by dApp developers.

This proposal aims to standardise the process of dApp registration and verification, and to provide a set of claims that dApp developers can use to register their dApp(s).

## Motivation: why is this CIP necessary?
dApps can express a plethora of information. Some of this information could be claims about who the developer is, what the dApp's associated metadata is, and more. This data lacks standardisation, persistence, and immutability. Data without these features, means that dApp users cannot verify if the dApp's expressed information is consistent across time. The goal of this CIP is to formalise how dApps register their information with a new transaction metadata format that can record the dApp's metadata, ownership, and potentially developer's identity. This formalisation means dApp users can verify if the data expressed by a dApp is consistent with what was registered on-chain.

Also, having this formalisation facilitates any actor in the ecosystem to index and query this data, and provide a better user experience when it comes to dApp discovery and usage.

## Specification

### **Definitions**
- **anchor** - A hash written on-chain (rootHash) that can be used to verify the integrity (by way of a cryptographic hash) of the data that is found off-chain.
- **dApp** - A decentralised application that is described by the combination of metadata, certificate and a set of used scripts.
- **metadata claim** - Generically any attempt to map off-chain metadata to an on-chain subject. This specification looks at dApp specific metadata claims.
- **client** - Any ecosystem participant which follows on-chain data to consume metadata claims (i.e. dApp stores, wallets, auditors, block explorers, etc.).
- **dApp Store** - A dApp aggregator application which follows on-chain data looking for and verifying dApp metadata claims, serving their users linked dApp metadata.
- **publishers** - Entities which publish metadata claims on-chain, in the case of dApps the publishers are likely the dApp developer(s).
- **auditors** - These are clients which maintain lists of trusted entities and metadata servers, checking metadata claims against these. 

### **Developers / Publishers**
Developers and publishers of dApps can register their dApps by submitting a transaction on-chain that can be indexed and verified by stores, auditors and other ecosystem actors.

### **Stores / Auditors**
Stores and auditors should be able to follow the chain and find when a new dApp registration is **anchored** on-chain. They should then perform *integrity* and *trust* validations on the dApp's certificate and metadata.

##### **Targetted Releases**
Each developer and publisher can choose where to write metadata based on the information available from known stores & auditors. This gives **developers** and **publishers** the ability to perform targeted releases. (i.e to which stores and auditors).

#### **Suggested Validations**
- **`integrity`**: The dApp's metadata off-chain should match the metadata **anchored** on-chain.
- **`trust`**: The dApp's certificate should be signed by a trusted entity. It's up to the store/auditor to decide which entities are trusted and they should maintain and publish their own list of trusted entities. Although this entities might be well known, it's not the responsibility of this CIP to maintain this list. These entities could be directly associated with developer/publisher or not.

### **On-chain dApp Registration Certificate**

The on chain dApp registration certificate MUST follow canonical JSON and be serialised according to RFC 8785 (https://www.rfc-editor.org/rfc/rfc8785). This stipulation is to avoid any ambigiutines in the signature calculation.

```json
{
	"subject": "d684512ccb313191dd08563fd8d737312f7f104a70d9c72018f6b0621ea738c5b8213c8365b980f2d8c48d5fbb2ec3ce642725a20351dbff9861ce9695ac5db8",
	"rootHash": "8c4e9eec512f5f277ab811ba75c991d51600c80003e892e601c6b6c19aaf8a33",
  "metadata": [
    "https://cip26.foundation.app/properties/d684512ccb313191dd08563fd8d737312f7f104a70d9c72018f6b0621ea738c5b8213c8365b980f2d8c48d5fbb2ec3ce642725a20351dbff9861ce9695ac5db8",
    "https://example.com/metadata.json",
    "ipfs://QmWmXcRqPzJn5yDh8cXqL1oYjHr4kZx1aYQ1w1yTfTJqNn",
  ],
  "type": { 
    "action": "REGISTER",
    "releaseNumber": "1.0.0"
  },
	"signature": {
		"r": "5114674f1ce8a2615f2b15138944e5c58511804d72a96260ce8c587e7220daa90b9e65b450ff49563744d7633b43a78b8dc6ec3e3397b50080",
		"s": "a15f06ce8005ad817a1681a4e96ee6b4831679ef448d7c283b188ed64d399d6bac420fadf33964b2f2e0f2d1abd401e8eb09ab29e3ff280600",
		"algo": "Ed25519−EdDSA",
		"pub": "b7a3c12dc0c8c748ab07525b701122b88bd78f600c76342d27f25e5f92444cde"
	}
}
```

### Properties
*`subject`*: Identifier of the claim subject (dApp). A UTF-8 encoded string. This uniqueness of this property cannot be guaranteed by the protocol and multiple claims for the same subject may exist, therefore it is required to exist some mechanism to assert trust in the *veracity* of this property.

*`type`*: The type of the claim. This is a JSON object that contains the following properties: 
- *`action`*: The action that the certificate is asserting. It can take the following values: 
  - *`REGISTER`*: The certificate is asserting that the dApp is being registered for the first time. 
  - *`UPDATE`*: The certificate is asserting that the dApp is being updated.

*`rootHash`*: The hash of the entire offchain metadata tree object. This hash is used by clients to verify the integrity of the metadata tree object. When reading a metadata tree object, the client should calculate the hash of the object and compare it with the `rootHash` property. If the two hashes don't match, the client should discard the object. The metadata tree object is a JSON object that contains the dApp's metadata. The metadata tree object is described in the next section.

To avoid ambiguities, the hash is calculated by taking the entire metadata tree object and it MUST be serialised according to RFC 8785 (https://www.rfc-editor.org/rfc/rfc8785) compatible json format. Once serialised resulting JSON MUST be hashed using blake2b-256 hashing algorithm. The result, a hash is then encoded as a hex string.

*`metadata`*: An array of links to the dApp's metadata. The metadata is a JSON compatible RFC 8785 object that contains the dApp's metadata.

*`signature`*: The signature of the certificate. The signature is done over the blake2b-256 hash of the certificate. The client should use the public key to verify the signature of the certificate. 

### dApp on-chain certificate JSON Schema
```json
{
   "$schema":"https://json-schema.org/draft/2019-09/schema",
   "$id":"https://example.com/dApp.schema.json",
   "title": "Cardano dApp Claim",
   "description": "Registration of update of Cardano dApp claim.",
   "type":"object",
   "properties":{
      "subject":{
         "type":"string",
         "description":"Identifier of the claim subject (dApp). A UTF-8 encoded string. Typically it is randomly generated hash by the dApp developer."
      },
      "rootHash":{
         "type":"string",
         "description":"blake2b hash of the metadata describing the dApp."
      },
      "metadata": {
        "type": "array",
        "items": {
          "type": "string",
          "description": "A valid url pointing to off-chain CIP-72 compatible metadata document.",
          "pattern": "(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]{2,}|www\.[a-zA-Z0-9]+\.[^\s]{2,})"
        }
      },
      "type":{
         "type":"object",
         "description":"Describes the releases, if they are new or an updates. Also states the versioning of such releases.",
         "properties":{
            "action":{
              "type":"string",
              "enum":["REGISTER", "UPDATE"],
              "description":"Describes the action this certificate is claiming. I.e 'REGISTER', for a new dapp; or 'UPDATE' for a new release"
            },
            "releaseNumber":{
               "type":"string",
               "description":"An official version of the release following semver format (major.minor.patch)."
            },
            "releaseName":{
               "type":"string",
               "description":"An optional dApp release name."
            }
         },
         "required":[
            "action",
            "releaseNumber"
         ]
      },
      "signature":{
         "description":"Signature of the whole canonical (RFC 8785) JSON document (except signature property).",
         "type":"object",
         "properties":{
            "r":{
               "type":"string",
               "description":"A hex representation of the R component of the signature."
            },
            "s":{
               "type":"string",
               "description":"A hex representation of the S component of the signature."
            },
            "algo":{
              "const":"Ed25519−EdDSA"
            },
            "pub":{
               "type":"string",
               "description":"A hex representation of the public key."
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
  "$schema": "http://json-schema.org/draft-04/schema#",
  "type":"object",
  "properties": {
    "subject": {
      "type":"string",
      "description": "A subject, it must match with subject stored on chain data."
    },
    "projectName": {
      "type":"string",
      "description": "A project name, e.g. My dApp."
    },
    "link": {
      "type":"string",
      "description": "Website presenting a dApp.",
      "pattern": "(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]{2,}|www\.[a-zA-Z0-9]+\.[^\s]{2,})"
    },      
    "projectName": {
      "type":"string",
      "description": "A project name, e.g. My dApp."
    },
    "logo": {
      "type":"string",
      "description": "URL to the logo or the base64 encoded image."
    },
    "categories": {
      "type":"array",
      "enum":["MARKETPLACE", "DEFI", "COLLECTION", "BRIDGE", "STABLECOIN", "NFT_MINTING_PLATFORM", "GAMING", "TOKEN_DISTRIBUTION", "COMMUNITY", "MOBILE_NETWORK", "SIDECHAIN", "LAYER_2"],
      "description": "One or more categories. Category MUST be one of the following schema definition."
    },
    "social": {
      "type":"object",
      "properties": {
        "website": {
          "type":"string",
          "description": "dApps website link.",
          "pattern": "(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]{2,}|www\.[a-zA-Z0-9]+\.[^\s]{2,})"
        },
        "twitter": {
          "type":"string",
          "description": "An optional Twitter link.",
          "pattern": "(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]{2,}|www\.[a-zA-Z0-9]+\.[^\s]{2,})"
        },
        "github": {
          "type":"string",
          "description": "An optional Github link.",
          "pattern": "(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]{2,}|www\.[a-zA-Z0-9]+\.[^\s]{2,})"
        },
        "discord": {
          "type":"string",
          "description": "An optional Discord link.",
          "pattern": "(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]{2,}|www\.[a-zA-Z0-9]+\.[^\s]{2,})"
        },
      },
      "required": ["website"]
    },
    "description": {
      "type": "object",
      "properties": {
        "short": {
          "type": "string",
          "description": "Short dApp description (No less than 40 and no longer than 168 characters).",
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
              "description": "Semver compatible release number (major.minor.patch), e.g. 1.2.3, where 1 is major, 2 is a minor and 3 is a patch.",
            },
            "releaseName": {
              "type": "string",
              "description": "An optional human readable release name, e.g. V1",
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
            "releaseNumber",
            "scripts"
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
              "description": "Unique Script ID (across all scripts from this dApp).",
            },
            "name":{
              "type":"string",
              "description": "An optional script name usually related to it's function.",
            },
            "purposes":{
              "type":"array",
              "enum":["SPEND", "MINT"],
              "description": "Purpouses of the script, SPEND or MINT (notice it can be both for some modern Cardano languages).",
            },
            "type":{
              "enum":["PLUTUS", "NATIVE"],
              "description": "Script Type. PLUTUS refers to the typical PlutusV1 or PlutusV2 scripts, where as NATIVE means there has been no Plutus directly used by this is a native script.",
            },
            "versions":{
              "type":"array",
              "items":[
                {
                  "type":"object",
                  "properties":{
                    "version":{
                      "type":"integer",
                      "description":"Script version, monotically increasing.",
                    },
                    "plutusVersion":{
                      "type":"integer",
                      "enum":[1, 2],
                    },
                    "scriptHash":{
                      "type":"string",
                      "description":"Full on-chain script hash (hex).",
                      "pattern":"[0-9a-fA-F]+"
                    },
                    "contractAddress": {
                      "type":"string",
                      "description":"An optional Bech32 contract address matching script's hash.",
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
            "purpose",
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
    "description",
    "releases",
    "scripts"
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
    "github": "https://github.com/my_dapp"
  },
  "categories": ["GAMING"],
  "description": {
    "short": "A story rich game where choices matter."
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


