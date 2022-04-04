---
CIP: 989
Title: KYC/CDD for ISPOs
Authors: John Woods  <john.woods@iohk.io>, <john@postquantum.dev>
Comments-Summary: No comments
Comments-URI: 
Status: Draft
Type: Standards Track
Created: 2021-12-17
License: CC-BY-4.0
---

# KYC/CDD for ISPOs

## Abstract
We introduce a mechanism to enable delegators to securely provide identifying information about themselves, which can be leveraged by SPOs to perform appropriate KYC/CDD. The approach also provides bilateral privacy between participants.

This article outlines a technical approach to ensure SPO (stake pool operators) are empowered to receive data regarding the identity of ADA holders delegating their stake to a pool. 

## Motivation
The motivation is simple. Emerging crypto-assets have been a generational leap in technology, both as a money system and as a platform for decentralized finance.

That said, crypto-assets are not exempt nor precluded from regulatory oversight. Indeed, we may expect potentially heightened scrutiny from regulatory bodies worldwide (SEC, FCA, ECB, etc) in certain contexts.

Ergo, the goal of this CIP is to proactively develop an approach whereby the Cardano protocol itself provides a mechanism which SPOs may choose to utilize, in order to obtain data they can in-turn consume to perform appropriate identification checks which they may be jurisdictionally required to execute, on their delegators/stakers. 

### Use cases
Following are examples use-cases where we expect this to be helpful:

1. To verify customer identity and validity during initial stake pool offerings. 
2. To provide a mechanism by which staking of Cardano assets can contain a DID (Decentralized Identity) as metadata. 

### Extensibility 
This proposal was designed with extensibility in mind. The solution is designed to be loosely coupled and extensible in order to provide a mechanism to deliver a DID to an authority in contexts other than ISPOs.

### Simplicity of delivery 
This proposal is being designed to avoid the need for overly complicated development/delivery. Thus changes to the Ledger layer will be minimized.


## Specification

### Requirements
We have a number of requirements that we need to meet:

- Privacy 
    - All DID data should be completely confidential, visible only between the two concerned parties (end-user and SPO), the data should enjoy end-to-end encryption (E2E).
- Low Friction
    - The process of delegating stake and submitting a DID to an SPO should be frictionless, that is, trivially executable by an "average" end-user, and not requiring a high degree of technical competence. 
- Information minimization 
    - The solution should aim to minimize the quantity of data requiring transfer when submitting a DID.
- Low Cost
    - The process of delegating stake and submitting a DID should not be expensive in terms of fees incurred on the end-user.


- Integrity
    - The process of delegating stake and submitting a DID should be verifiably unmodified from the submitters (end-users) intent.
- Authenticity/Cryptographic Veracity
    - The process of delegating stake and executing the KYC/CDD check on a DID should be verifiably authentic to a high degree of certainty.
- Non-Repudiation
    - The process of delegating stake and submitting a DID should boast the property of non-repudiation, that is, it should be impossible for the submitter to deny ownership of the ISPO request.

### DIDs
A DID is a self sovereign decentralized identity, which lives on-chain. It enables a user to prove their identity to a high degree of veracity, by leveraging the fact that the DID is protected by a decentralized protocol.

Ultimately, a DID is an attestation conferred upon a user from some other known and trusted entity/entities.

The existing PRISM protocol enables the use of Decentralized Identifiers (DIDs) and Verifiable Credentials (VC).

DID's are attached to a specific end-user public key, and verifiable via issuing a signature from the corresponding private key, after checking the DID status on PRISM.

Thus, end-users may confirm ownership of a DID by providing an EdDSA signature with the correct private key. 

DIDs are binary data encoded as hexadecimal and Base64, as an example:

`(did:prism:7e5b03ee503c6d63ca814c64b1e6affd3e16d5eafb086ac667ae63b44ea23f2b:CmAKXhJcCgdtYXN0ZXIwEAFCTwoJc2VjcDI1NmsxEiA4BHOH6oJYfe_pVSqXl69HcRW304Mk4ExOwJye9VWcGBogOBL32BWDzjqnSqoQss8x_qv_02fwyrEL13QCKT9KRoQ=,207)`

### Binding of DID & Stake Delegation
We require a mechanism to bind an end-user's DID to the stake delegation destined for an ISPO.

We can leverage the existing staking mechanism. During the process of delegating stake, an end-user will register a _delegation certificate_, this certificate permits a given SPO to include said end-user's ADA as part of their stake distribution.

A DID may be submitted, as encrypted meta-data in the **same transaction** that delivers the underlying delegation certificate. Critically the transaction body is signed by both the spending private/secret key and the staking private/secret key. This has a number of serendipitous consequences:

* The SPO hosting the ISPO can verify the end-user has ownership of the secret staking key required to validly delegate stake to the SPO.
* The SPO hosting the ISPO can verify the end-user has ownership of the secret spending key required to sign the transaction which itself includes the DID as a transaction metadata field.
* We can use the end-users staking key in an ECDH (Elliptic Curve Diffie-Hellman) interaction to generate shared symmetric key material.

This approach essentially cryptographically binds a DID to a stake delegation.

### DID Privacy
In order to submit a valid DID for a given ISPO event, an end-user must include a DID in the transaction metadata which is being submitted to register stake.
This DID information should be confidential and only visible to the concerned parties (end-user and SPO). Thus we propose a mechanism for cryptographic key agreement between end-user and SPO in a non-interaction fashion, the resulting key material can be used to protect the DID data.

We will leverage `static:static ECDH` (Elliptic curve Diffie-Hellman) in order to agree a symmetric key, this process will leverage the end-user's existing staking key pair, and require a **new hot key pair** on the SPO side, known as the *DID decryption key pair*. This process assumes the same curve and curve generator point are being used by both parties.


#### Key Agreement Process
$$
\text{Where}\ sa,Pa=\text{the end-user staking key pair, secret and public respectively.} \\
\text{Where}\ sb,Pb=\text{the SPO DID decryption key pair, secret and public respectively.} \\\\
\text{Scalar multiplication on a cryptographic elliptic curve, defined over a large prime order Galois field of:}\\
\text{\{$sa \cdot Pb$\} and, \{$sb \cdot Pa$\} respectively, will yield the same point on the curve to both parties.} \\
\text{Passing the $x$ coordinate of this resulting point through a key derivation function/hash function will yield a shared symmetric key of $256-bits$.}
$$

We could upgrade the key agreement process to `ephemeral:ephemeral` (ECDHE), however, this would require interaction between end-user and SPO at delegation time, `ephemeral:static` is an easier option, if we include the ephemeral public key counterpart in the transaction metadata when posting the staking certificate. `ed25519` public keys are only `32 bytes` owing to the fact that they use compressed form representations by default, therefore inclusion of this key will not bloat the transaction.

We can use the shared symmetric key material with a strong symmetric cipher such as `XChaCha-Poly1305` or `XSalsa20-Poly1305` to protect the DID data.

Evidently the end-user requires the public counterpart of the SPO's DID decryption key pair in order to execute the ECDH interaction and finalize the key agreement process, which is discussed in the following section.

#### Disseminating the SPO DID Decryption Public Key
We can leverage the fact that SPO's must post their stake pool registration certificate on chain. This registration process includes a number of fields already in a JSON format. We can extend this dataset to include both the SPO hot DID decryption public key, and a signature on the same from their SPO cold key (similar to how KES keys are signed). 

This ensures end-users can know they are encrypting their DID for the intended SPO, by verifying the signature on the SPO's DID decryption public key prior to using it to encrypt any data. Example:

```json
{
  "name": "TestPool",
  "description": "Testing Pool",
  "ticker": "TEST",
  "homepage": "https://teststakepool.com",
  "did_pubkey": someEd25519PubKey,
  "did_sig": someEdDSASignature,
}
```

This change to SPO registration certificates would require a hard-fork due to requisite Ledger changes.


### SPO Retrieval of DID data
The process described above requires the underlying SPO is able to retrieve a DID from each stake delegation transaction bound for said SPO. Thus an additional tool/service would be required, which could be developed as part of this CIP. The tool would be used to query the ledger on a set cadence, fetch the array of delegates, pull their DID from their respective transaction's metadata and process the DID.
