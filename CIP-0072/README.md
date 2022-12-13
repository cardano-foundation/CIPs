---
CIP: 72
Title: Cardano DApp Registration
Authors: Bruno Martins <bruno.martins@iohk.io>
Status: Draft
Type: Standards
Created: 2022-10-18
License: CC-BY-4.0
---

## **Abstract**
DApp developers do not have a standardised method to record immutable, persistent claims about their dApp(s) that their users can verify. A dApp developers needs to "register" their dApp by providing a set of claims about their dApp(s) that can be verified by the user. This CIP describes a standardised method for dApp developers to register their dApp(s) and for users to verify the claims made by the dApp developer.

This proposal aims to standardise the process of dApp registration and verification, and to provide a set of claims that dApp developers can use to register their dApp(s).

## **Motivation**
DApps can express a plethora of information. Some of this information could be claims about who the developer is, what is the dApp's associated metadata are, and more. This data lacks standarisation, persistence, and immutabulity. Data without these features, means that dApp users cannot verify if the dApp's expressed information is consistent across time. The goal of this CIP is to formalise how dApps register their information with a new transaction metadata format that can record the dApp's metadata, ownership, and potentially developer's identity. This formalisation means dApp users can verify if the data expressed by a dApp is consistent with what was registered on-chain.

Also having this formalisation facilitates any actor in the ecosystem to index and query this data, and provide a better user experience when it comes to dApp discovery and usage.

## **Specification**

### **On-chain dApp Registration certificate**

```json
{
	"subject": "d684512ccb313191dd08563fd8d737312f7f104a70d9c72018f6b0621ea738c5b8213c8365b980f2d8c48d5fbb2ec3ce642725a20351dbff9861ce9695ac5db8",
	"rootHash": "8c4e9eec512f5f277ab811ba75c991d51600c80003e892e601c6b6c19aaf8a33",
  "type": "REGISTER",
  "cip26": ["http://somelocation.io/", "http://somelocation2.io/"],
	"did": "did:ada:f2019bd31a8530fb67c6d81da758dfa9a65be09d835cf2cd361d595a8858301d",
	"signature": {
		"r": "5114674f1ce8a2615f2b15138944e5c58511804d72a96260ce8c587e7220daa90b9e65b450ff49563744d7633b43a78b8dc6ec3e3397b50080",
		"s": "a15f06ce8005ad817a1681a4e96ee6b4831679ef448d7c283b188ed64d399d6bac420fadf33964b2f2e0f2d1abd401e8eb09ab29e3ff280600",
		"algo": "Ed25519−EdDSA",
		"pub": "b7a3c12dc0c8c748ab07525b701122b88bd78f600c76342d27f25e5f92444cde"
	}
}
```

### Properties
*`subject`*: Identifier of the claim subject (i.e dapp). A UTF-8 encoded string. This uniquess of this property cannot be guaranteed by the protocol and multiple claims for the same subject may exist therefore it is required to exist some mechanism to assert trust in the *veracity* of this property. This can be done by knowning verifying the signature against a trusted / known public key or by using Decentralized Identifiers (DIDs) as described in the [DID Specification](https://www.w3.org/TR/did-core/).

*`type`*: The type of the claim. A UTF-8 encoded string. The value of this property can have the value `REGISTER` or `UPDATE`. The `REGISTER` type is used to register a new dApp. The `UPDATE` type is used to update the metadata of an existing dApp.

*`rootHash`*: The hash of the metadata entire tree object. This hash is used by clients to verify the integrity of the metadata tree object. When reading a metadata tree object, the client should calculate the hash of the object and compare it with the `rootHash` property. If the two hashes don't match, the client should discard the object. The metadata tree object is a JSON object that contains the dApp's metadata. The metadata tree object is described in the next section.

This hash is calculated by taking the entire metadata tree object, ordering the keys in the object alphanumerically, and then hashing the resulting JSON string using the blake2b hashing algorithm. The hash is encoded as a hex string.

*`cip26`*: An array of URLs that point to the location of the dApp's metadata. The client should try to fetch the metadata from the first URL in the array. If the client fails to fetch the metadata from the first URL, it should try the second URL, and so on. If the client fails to fetch the metadata from all URLs, it should consider the metadata to be invalid.

The format of the metadata tree object is described in the [CIP-26](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0026) specification.

*`did`*(optional): The DID of the dApp's developer. The DID is used to verify the authenticity of the certificate. The client should use the DID to fetch the developer's public key from the Cardano blockchain. The client should then use the public key to verify the signature of the certificate. This field is *optional* and can be used by identity centric dApps to verify the authenticity of the developer.

*`signature`*: The signature of the certificate. The signature is done over the blake2b hash of the certificate. The client should use the public key to verify the signature of the certificate. If a DID is provided, the client should use the DID to fetch the developer's public from the DID Document. If a DID is not provided, the client should use the public key provided in the signature object or from a already known public key.

## Certificate JSON Schema
```json
{
  "$schema": "http://json-schema.org/draft-04/schema#",
  "type": "object",
  "properties": {
    "subject": {
      "type": "string"
    },
    "type": {
      "type": "string",
      "enum": [
        "REGISTER",
        "UPDATE"
      ]
    },
    "rootHash": {
      "type": "string"
    },
    "cip26": {
      "type": "array",
      "items": [
        {
          "type": "string"
        }
      ]
    },
    "did": {
      "type": "string"
    },
    "signature": {
      "type": "object",
      "properties": {
        "r": {
          "type": "string"
        },
        "s": {
          "type": "string"
        },
        "algo": {
          "type": "string"
        },
        "pub": {
          "type": "string"
        }
      },
      "required": [
        "r",
        "s",
        "algo",
        "pub"
      ]
    }
  },
  "required": [
    "subject",
    "rootHash",
    "cip26",
    "signature"
  ]
}
```