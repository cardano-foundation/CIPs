---
CIP: 066
Title: NFT Identity
Authors: Patrick Tobler <patrick.tobler@nmkr.io>, Dennis Mittmann <dennis@iamx.id>
Status: Active
Type: Process
Created: 2022-07-06
License: CC-BY-4.0
---

## Abstract

This CIP defines a standard to verify NFT projects using Decentralized Identifiers.

## Motivation

The verification process of the authenticity of NFT projects is currently a centralized effort, that is completely in the hands of the NFT platforms. 

Most of these platforms create a centralized database of verified projects and have arbitrary rules that define which NFTs get verified on the respective platform. Not only is this not scalable because it relies on a case-to-case verification process often done manually and requires the NFT creators to go through the verification process on an increasing amount of different platforms, but it is also highly centralized and doesn't utilize a global cross-platform verification method.

## High Level Overview

By connecting an NFT collection to one or multiple Digital Identifiers, the creator of the NFT collection has the option to attach verification data points to the collection. 

Each of these data points stores information about a direct connection between the NFT collection and some sort of identity medium. This identity medium could be a scoial account, a KYC process, a phone number or anything else where an identity is directly linked to an account or something similar.

The data points connected to the NFT collection are publicly visible and can be audited by anyone. Either manually or programmatically.

The creator can choose which identity data points he wants to connect to the collection and the auditor can then choose if he trusts these data points enough to interact with the colleciton or not.

## Practical Example

Let's imagine Paris Hilton wants to release an NFT collection on Cardano.

How would potential customers of this NFT collection normally identify this collection as a real collection that was published by her? They would most likely make use of the source of the information about this collection as his verification method.

In this case, if they know that Paris Hiltons Twitter Account with millions of followers is legit and they trust that this account really belongs to Paris Hilton, they would trust a tweet from this account about the new collection.
The same goes for Instagram, Facebook and all other of her offical Social Media accounts.

Now what can Paris Hilton do to verify that all of these accounts are connected directly to this NFT collection without posting about the collection on all of these accounts?

She can use an Identity Provider, where she can simply connect the accounts of her liking using OAuth or any other login standard. Then this Identity Provider can issue a Decentralized Identifier Document (DID) and reference all the accounts that Paris Hilton has just connected using OAuth. 
Now that this DID is created, Paris Hilton can link it on-chain to her new NFT collection.
Once the DID is linked to the NFT collection on-chain, the NFT platofrms can simply query this information and display to the end-users/potential buyers of these NFTs which social accounts are unmistakeably linked to the collection.

The end-users/potential buyers then can judge for themselves if they want to trust these social accounts or not. THe more trustworthy social accounts are connected to the collection, the more likely it is that the end-users will trust the authenticity of the collection.

## Specification

This is the registered `transaction_metadatum_label` value

| transaction_metadatum_label | description  |
| --------------------------- | ------------ |
| 725                         | NFT Identity |


### Structure

There are three different key components to this structure.

| component                   | description                                                                                                                |
| --------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| DID                         | The actual Decentralized Identity Document where the information about the connected identity data points is stored.       |
| Unnamed Token               | This token is minted under the policy ID of the NFT collection. It defines the connecton to the DID or the Identity Token. |
| Identity Token              | This token is optional and only relevant if the DID needs to be changeable.                                                |


#### 1. DID

This is an example DID taken from the official [W3C specification](https://www.w3.org/TR/did-core/#did-syntaxg).
To keep the scope reasonable, this CIP will not explain the DID specification deeper. Please refer to the W3C specifation as linked above.

```
{
  "@context": [
    "https://www.w3.org/ns/did/v1",
    "https://w3id.org/security/suites/ed25519-2020/v1"
  ]
  "id": "did:example:123456789abcdefghi",
  "authentication": [{
    
    "id": "did:example:123456789abcdefghi#keys-1",
    "type": "Ed25519VerificationKey2020",
    "controller": "did:example:123456789abcdefghi",
    "publicKeyMultibase": "zH3C2AVvLMv6gmMNam3uVAjZpfkcJCwDwnZn6z3wXmqPV"
  }]
}
```

#### 2. Unnamed Token

This is an unnamed token, as first described in the [CIP-0027](hhttps://github.com/cardano-foundation/CIPs/tree/master/CIP-0027).

It stores information about the location of either the DID or the Identity Token in the metadata of its minting transaction.

```
{
  "725": {
    "<policy_id>": {
        "<collection_name>": {
            "@context": <uri | array>,
            "type": <string>,
            "files": [{
                "name": <string>,
                "mediaType": <mime_type>,
                "src": <string | array>,
                <other_properties>
            }],
            <other_properties>
        }
    },
    "version": <version_id>
  }
}
```

| identifier                  | description                                                         | optional |
| --------------------------- | ------------------------------------------------------------------- | -------  |
| policy_id                   | The policy of the NFT collection                                    | no       |
| collection_name             | The name of the NFT collection                                      | no       |
| @context                    | Rerefences to the DID standard                                      | yes      |
| type                        | Verification method type from W3C specification                     | no       |
| name                        | Name of the DID                                                     | yes      |
| mediaType                   | The mediaType of the referenced file                                | no       |
| src                         | A link to the DID file or an asset_fingerprint to an Identity Token | no       |
| other_properties            | Extensions of the standard                                          | yes      |
| version                     | Version of the NFT Identity standard                                | no       |



#### 3. Identity Token

This token can be created under a seperate policy ID, so that it can be used for multiple collections at once.
The policy can also be left unlocked in case the identity information requires changes at some later date. 

```
{
  "725": {
    "<policy_id>": {
        "<collection_name>": {
            "@context": <uri | array>,
            "type": <string>,
            "files": [{
                "name": <string>,
                "mediaType": <mime_type>,
                "src": <uri | array>,
                <other_properties>
            }],
            <other properties>
        }
    },
    "version": <version_id>
  }
}
```

## Example Implementation

#### 1. DID Document

In this example the DID Document is stored on IPFS.

```
coming soon
```

#### 2. Unnamed Token

```
{
  "725":{
    "version": "1.0",
    "fdb275fb75db33313626e0361fc763b6995e97db312be87590e48aa1": {
        "CIP0066Test": {
            "type": "Ed25519VerificationKey2020",
            "files": [
                {
                    "src": "ipfs://QmacjTQe5q1ur2FbqW9TehScoP7cZEcAWnSA6gz4FEEMi2",
                    "name": "CIP-0066_NMKR_IAMX",
                    "mediaType": "application/ld+json"
                }
            ],
            "payload": {
                "date": "Fri, 08 Jul 2022 09:03:43 GMT",
                "accounts": {
                    "twitter": {
                        "handle": [
                            "https://twitter.com/nmkr_io",
                            "https://twitter.com/IAM_X_IDENTITY"
                        ]
                    },
                    "website": [
                        "https://www.nmkr.io/",
                        "https://www.iamx.id/"
                    ]
                },
                "policyID": "fdb275fb75db33313626e0361fc763b6995e97db312be87590e48aa1",
                "description": "CIP-0066 NFT-Identity by NMKR.IO and IAMX.ID"
            },
            "@context": "https://github.com/IAMXID/did-method-iamx"
        }
    }
} }
```

## Cross-Chain Compatibility

To make this standard cross-chain compatible it is possible to set the value of the src parameter to a unique identifier on another blockchain.

## Backwards Compatibility

To keep NFT metadata compatible with changes coming up in the future, we use the **`version`** property.

## Rationale
The focous of this standard is on easy-of-use & flexibility. Using this standard it is possible to reference DIDs not only on Cardano but at any arbitrary location, even cross-chain. It is also relatively simple to understand and implement because it borrows heavily from pre-existing metadata standards.

## Path to Active

[IAMX](https://iamx.id/) and [NMKR](https://www.nmkr.io/) have created a reference implementation of the standard that can be viewed [here](https://cardanoscan.io/transaction/608dd4fba7df5c523a1dfdca8d48fd1d69e7e1995a342ceb01c8355c62a0845b?tab=metadata).

[IAMX](https://iamx.id/) will be creating a tool to create the DIDs that will be integrated nativel into [NMKR](https://www.nmkr.io/) studio.

By displaying this solution at the Catalyst Guild Hall we hope to reach more creators that are willing to integrate this solution.

## References

- W3C DID Specification: https://www.w3.org/TR/did-core/#did-syntaxg
- CIP-0025 that introduced the unnamed Token: hhttps://github.com/cardano-foundation/CIPs/tree/master/CIP-0027

## Copyright

This CIP is licensed under Apache-2.0
