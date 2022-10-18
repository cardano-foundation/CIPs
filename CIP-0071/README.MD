---
CIP: 066
Title: Pool Identity
Authors: Dennis Mittmann <dennis@iamx.id>
Status: Active
Type: Process
Created: 2022-10-18
License: CC-BY-4.0
---

## Abstract

This CIP defines a standard to verify Staking Pools using Decentralized Identifiers.

## Motivation

The verification process of the authenticity of Staking Pools is currently a centralized effort. 

## High Level Overview

## Practical Example

## Specification

### Structure

#### 1. DID

This is an example DID taken from the official [W3C specification](https://www.w3.org/TR/did-core/#did-syntaxg).
To keep the scope reasonable, this CIP will not explain the DID specification deeper. Please refer to the W3C specifation as linked above.
The only important thing to note is that inside the DID document the payload will contain the different social accounts that were linked to the DID document.

```
{
  "@context": [
    "https://www.w3.org/ns/did/v1",
    "https://w3id.org/security/suites/ed25519-2020/v1"
  ],
  "payload": {
    ...
  },
  "id": "did:example:123456789abcdefghi",
  "authentication": [{
    
    "id": "did:example:123456789abcdefghi#keys-1",
    "type": "Ed25519VerificationKey2020",
    "controller": "did:example:123456789abcdefghi",
    "publicKeyMultibase": "zH3C2AVvLMv6gmMNam3uVAjZpfkcJCwDwnZn6z3wXmqPV"
  }]
}
```
#### 3. Extendet Pool Metadata

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

## Cross-Chain Compatibility

To make this standard cross-chain compatible it is possible to set the value of the src parameter under files to a unique identifier on another blockchain, where the DID might be located.

## Backwards Compatibility

To keep NFT metadata compatible with changes coming up in the future, we use the **`version`** property.

## Rationale
The focus of this standard is on ease-of-use & flexibility. Using this standard it is possible to reference DIDs not only on Cardano but at any arbitrary location, even cross-chain. It is also relatively simple to understand and implement because it borrows heavily from pre-existing metadata standards.

## Path to Active

[IAMX](https://iamx.id/) and [NMKR](https://www.nmkr.io/) have created a reference implementation of the standard that can be viewed [here](https://cardanoscan.io/transaction/608dd4fba7df5c523a1dfdca8d48fd1d69e7e1995a342ceb01c8355c62a0845b?tab=metadata).

[IAMX](https://iamx.id/) will be creating a tool to create the DIDs that will be integrated natively into [NMKR](https://www.nmkr.io/) studio.

By displaying this solution at the Catalyst Guild Hall we hope to reach more creators that are willing to integrate this solution.

## References

- W3C DID Specification: https://www.w3.org/TR/did-core/#did-syntaxg
- CIP-0066

## Copyright

This CIP is licensed under CC-BY 4.0
