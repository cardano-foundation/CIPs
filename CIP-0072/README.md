---
CIP: 72
Title: Cardano DApp Registration & Discovery
Status: Draft
Category: Metadata	
Authors: 
  - Bruno Martins <bruno.martins@iohk.io>
Discussions:
  - https://github.com/cardano-foundation/CIPs/pull/355
Created: 2022-10-18
License: CC-BY-4.0
---

# CIP-0072: Cardano DApp Registration & Discovery

## **Abstract**
DApp developers do not have a standardised method to record immutable, persistent claims about their dApp(s) that their users can verify. A dApp developers needs to "register" their dApp by providing a set of claims about their dApp(s) that can be verified by the user. This CIP describes a standardised method for dApp developers to register their dApp(s) and for users to verify the claims made by the dApp developer.

This proposal aims to standardise the process of dApp registration and verification, and to provide a set of claims that dApp developers can use to register their dApp(s).

## **Motivation**
DApps can express a plethora of information. Some of this information could be claims about who the developer is, what is the dApp's associated metadata are, and more. This data lacks standarisation, persistence, and immutability. Data without these features, means that dApp users cannot verify if the dApp's expressed information is consistent across time. The goal of this CIP is to formalise how dApps register their information with a new transaction metadata format that can record the dApp's metadata, ownership, and potentially developer's identity. This formalisation means dApp users can verify if the data expressed by a dApp is consistent with what was registered on-chain.

Also having this formalisation facilitates any actor in the ecosystem to index and query this data, and provide a better user experience when it comes to dApp discovery and usage.

## **Definitions**
- **anchor** - A hash written on-chain that can be used to verify the integrity (by way of a cryptographic hash) of the data that is found off-chain.
- **dApp** - A decentralised application that is described by the combination of metadata, certificate and a set of used scripts.

## **Specification**

### **Developers / Publishers**
Developers and publishers of dApps can register their dApps by submitting a transaction on-chain that can be indexed and verified by stores, auditors and other actors. 

### **Stores / Auditors**
Store and auditors should be able to follow the chain and find when a new dApp registration is **anchored** on-chain. They should then perform *integrity* and *trust* validations on the dApp's certificate and metadata. 

#### **Off-chain Location Advertisement**
Each store and auditor should make public the location of their off-chain sources where they will look for the dApp's metadata based on certificates found on-chain. These can be advertised through their own API or publically available on a website.

Sample off-chain sources could be for example :
- [CIP-26](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0026) compliant servers
- IPFS

##### **Targetted Releases**
Each developer and publisher can choose to where to write metadata based on the information available from known stores & auditors. This gives **developers** and **publishers** the ability to perform targeted releases. (i.e to which stores and auditors)

#### **Suggested Validations**

- **`integrity`**: The dapp's metadata off-chain should match the metadata anchored on-chain.
- **`trust`**: The dApp's certificate should be signed by a trusted entity. It's up to the store/auditor to decide which entities are trusted and they should maintain and publish their own list of trusted entities. Although this entities might be well known, it's not the responsibility of this CIP to maintain this list.

### **On-chain dApp Registration certificate**

```json
{
	"subject": "d684512ccb313191dd08563fd8d737312f7f104a70d9c72018f6b0621ea738c5b8213c8365b980f2d8c48d5fbb2ec3ce642725a20351dbff9861ce9695ac5db8",
	"rootHash": "8c4e9eec512f5f277ab811ba75c991d51600c80003e892e601c6b6c19aaf8a33",
  "metadata": [
    "https://cip26.foundation.app/properties/d684512ccb313191dd08563fd8d737312f7f104a70d9c72018f6b0621ea738c5b8213c8365b980f2d8c48d5fbb2ec3ce642725a20351dbff9861ce9695ac5db8",
    "https://example.com/metadata.json",
    "ipfs://QmWmXcRqPzJn5yDh8cXqL1oYjHr4kZx1aYQ1w1yTfTJqNn",
  ],
  "schema_version": "0.0.1",
  "type": { 
    "action": "REGISTER",
    "releaseNumber": "1.0.0",
    "releaseName": "My First Release",
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
*`subject`*: Identifier of the claim subject (i.e dapp). A UTF-8 encoded string. This uniquess of this property cannot be guaranteed by the protocol and multiple claims for the same subject may exist therefore it is required to exist some mechanism to assert trust in the *veracity* of this property.

*`type`*: The type of the claim. This is a JSON object that contains the following properties: 
- *`action`*: The action that the certificate is asserting. It can take the following values: 
  - *`REGISTER`*: The certificate is asserting that the dApp is being registered for the first time. 
  - *`UPDATE`*: The certificate is asserting that the dApp is being updated.

*`rootHash`*: The hash of the metadata entire tree object. This hash is used by clients to verify the integrity of the metadata tree object. When reading a metadata tree object, the client should calculate the hash of the object and compare it with the `rootHash` property. If the two hashes don't match, the client should discard the object. The metadata tree object is a JSON object that contains the dApp's metadata. The metadata tree object is described in the next section.

This hash is calculated by taking the entire metadata tree object, ordering the keys in the object alphanumerically, and then hashing the resulting JSON string using the blake2b-256 hashing algorithm. The hash is encoded as a hex string.

*`metadata`*: An array of links to the dApp's metadata. The metadata is a JSON object that contains the dApp's metadata.

*`signature`*: The signature of the certificate. The signature is done over the blake2b hash of the certificate. The client should use the public key to verify the signature of the certificate. 

## Certificate JSON Schema
```json
{
	"$schema": "https://json-schema.org/draft/2019-09/schema",
	"$id": "https://example.com/person.schema.json",
    "title": "Person",
    "type": "object",
    "properties": {
      "subject": {
        "type": "string",
        "description": "Can be anything. Description of the registration",
      },
      "type": {
        "type": "object",
        "description": "Describes the releases, if they are new or an updates. Also states the versioning of such releases",
        "properties": {
          "action": {
          	"type": "string",
            "description": "Describes the action this certificate is claiming. I.e 'REGISTER', for a new dapp; or 'UPDATE' for a new release"
          },
          "releaseNumber": {
          	"type": "string",
            "description": "offical version of the release"
          },
          "releaseName": {
          	"type": "string",
            "description": "Dapp release name"
          }
		}
      },  
      "rootHash": {
        "type": "string",
        "description": "blake2b hash of the metadata describing the dApp"
      },
      "signature": {
        "description": "Age in years which must be equal to or greater than zero.",
        "type": "object",
        "properties": {
			"r": {
				"type": "string",
				"description": "hex representation of the R component of the signature"
			},
            "s": {
				"type": "string",
				"description": "hex representation of the S component of the signature"
			},
              
		},
		"required": ["r", "s", "algo", "pub"]
      }
    },
    "required": ["subject", "rootHash","type", "signature"]
}
```

## Metadata Label

When submitting the transaction metadata pick the following value for `transaction_metadatum_label`:

- `1667`: DApp Registration

## Offchain Metadata Format
The Dapp Registration certificate itself doesn't enforce a particular structure to the metadata you might fetch off-chain. However, we recommend that you use the following structure:

```json
{
  "$schema": "http://json-schema.org/draft-04/schema#",
  "type": "object",
  "properties": {
    "subject": {
      "type": "string"
    },
    "projectName": {
      "type": "string"
    },
    "link": {
      "type": "string"
    },
    "category": {
      "type": "string"
    },
    "subCategory": {
      "type": "string"
    },
    "description": {
      "type": "object",
      "properties": {
        "short": {
          "type": "string"
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
              "type": "integer"
            },
            "releaseName": {
              "type": "string"
            },
            "auditId": {
              "type": "string"
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
            "releaseName",
            "auditId",
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
          "properties": {
            "id": {
              "type": "string"
            },
            "name": {
              "type": "string"
            },
            "purpose": {
              "type": "string"
            },
            "type": {
              "type": "string"
            },
            "versions": {
              "type": "array",
              "items": [
                {
                  "type": "object",
                  "properties": {
                    "version": {
                      "type": "integer"
                    },
                    "plutusVersion": {
                      "type": "integer"
                    },
                    "fullScriptHash": {
                      "type": "string"
                    },
                    "scriptHash": {
                      "type": "string"
                    },
                    "contractAddress": {
                      "type": "string"
                    }
                  },
                  "required": [
                    "version",
                    "plutusVersion",
                    "fullScriptHash",
                    "scriptHash",
                    "contractAddress"
                  ]
                }
              ]
            },
          },
          "required": [
            "id",
            "name",
            "purpose",
            "type",
            "versions",
            "audits"
          ]
        }
      ]
    }
  },
  "required": [
    "subject",
    "projectName",
    "link",
    "twitter",
    "category",
    "subCategory",
    "description",
    "releases",
    "scripts"
  ]
}
```

## Example

```json
{
  "$schema": "http://json-schema.org/draft-04/schema#",
  "type": "object",
  "properties": {
    "subject": {
      "type": "string"
    },
    "projectName": {
      "type": "string"
    },
    "link": {
      "type": "string"
    },
    "category": {
      "type": "string"
    },
    "subCategory": {
      "type": "string"
    },
    "social": {
      "type": "object",
      "properties": {
        "twitter": {
          "type": "string"
        },
        "github": {
          "type": "string"
        },
        "website": {
          "type": "string"
        }
      }
    },
    "description": {
      "type": "object",
      "properties": {
        "short": {
          "type": "string"
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
              "type": "integer"
            },
            "releaseName": {
              "type": "string"
            },
            "auditId": {
              "type": "string"
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
            "releaseName",
            "auditId",
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
          "properties": {
            "id": {
              "type": "string"
            },
            "name": {
              "type": "string"
            },
            "purpose": {
              "type": "string"
            },
            "type": {
              "type": "string"
            },
            "versions": {
              "type": "array",
              "items": [
                {
                  "type": "object",
                  "properties": {
                    "version": {
                      "type": "integer"
                    },
                    "plutusVersion": {
                      "type": "integer"
                    },
                    "fullScriptHash": {
                      "type": "string"
                    },
                    "scriptHash": {
                      "type": "string"
                    },
                    "contractAddress": {
                      "type": "string"
                    }
                  },
                  "required": [
                    "version",
                    "plutusVersion",
                    "fullScriptHash",
                    "scriptHash",
                    "contractAddress"
                  ]
                }
              ]
            }
          },
          "required": [
            "id",
            "name",
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
    "category",
    "subCategory",
    "description",
    "releases",
    "scripts"
  ]
}
```

### **Stores Custom fields**
Each store might have their own requirements for the metadata. For example, some stores might require a field for logo, or screenshots links. The store's should adviertise what fields they require in their documentation so that developers are aware and they can include them in the metadata. 

### **Offchain Metadata Storage**

There are multiple options to store metadata offchain. The most common options are:
- IPFS
- CIP-26
- Bitbucket
- Regular HTTP server
