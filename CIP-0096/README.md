---
CIP: 96
Title: On-chain dApp Certification Metadata
Category: Metadata
Status: Proposed
Authors:
    - Romain Soulat <romain.soulat@iohk.io>
    - Nicolas Jeannerod <nicolas.jeannerod@tweag.io>
    - Mathieu Montin <mathieu.montin@tweag.io>
    - M. Ali Modiri <mixaxim@gimbalabs.io>
    - Simon Thompson <simon.thompson@iohk.io>
Implementors: []
Discussions:
    - https://github.com/cardano-foundation/CIPs/pull/499
    - https://github.com/input-output-hk/Certification-working-group/pull/18
    - https://docs.google.com/document/d/1vC4cS-gMLIvgduSh5Fipn_lU_0Ou0NY4X_a9lWJz2B8
Created: 2023-02-23
License: CC-BY-4.0
---


## Abstract

Certification is the process of providing various kinds of assurance of DApps through the provision of verifiable, trustworthy metadata linking to relevant evidence of assurance, such as audit reports, test run data, formal verification proofs etc.

Currently, certification does not have a standardised way to be stored and presented to all stakeholders (DApp developer, DApp stores, end-users, auditors, ...) in an immutable, persistent and verifiable way.

This CIP describes a standardised method for certificates to be published on-chain as verifiable Non-Fungible Tokens (NFTs) and for stakeholders to be able to verify the different claims of this certificate.

This CIP describes how a certification certificate can be minted as a CIP-68 compliant NFT, storing its core metadata on-chain in its datum, and how to anchor it to a more detailed off-chain certification report.

## Motivation: why is this CIP necessary?

It is expected that evidence of various kinds of assurance of dApps is recorded in an immutable and verifiable way on the Cardano blockchain. Three levels of certification are thought of at the time of this CIP: level 1 to 3. They were presented at the following [link](https://iohk.io/en/blog/posts/2021/10/25/new-certification-levels-for-smart-contracts-on-cardano/) and will be fully described in a future document.

Level 1 will be used for testing through automated tooling. This level will be designed to give continual assurance that a smart contract verifies a range of properties. Level 1 covers the discovery of different types of bugs or issues. It should be thought as low cost and low effort if a DApp developer already has a sound testing practice in place. It will still bring a substantial level of assurance. It will be possible to be integrated into a continuous development and testing practice so that, even nightly builds and releases should be certifiable.
Level 2 will be used for in-depth audit. It will be done by third-party auditors, following [CIP-52](https://cips.cardano.org/cips/cip52/). It will be a more in-depth analysis and review of what can be achieved in level 1.
Level 3 will be used for formal verification. This level is more specialized and is used to bring a full mathematical assurance that critical aspects of the smart contract.

Those level of certification and their standards are yet to be defined. The Cardano Certification Working Group will be one place where those standards are discussed.
In order to bootstrap the use of this CIP, an "AUDIT" type with a certification level of 0 has been added in the possible metadata. This will allow auditors and other "certification" issuers to publish on-chain information about the verification that was done on a particular DApp. The "AUDIT" type could also be used in the future to publish audit reports on-chain that do not meet the future standards for certification but are however useful for the ecosystem.

The metadata should be discoverable by all certification stakeholders, including end-users, DApp developers, and ecosystem components, such as light wallets and DApp stores. Information should be indexable by certification issuer, DApp developer, DApp and DApp version.

### Use-cases and Stakeholders

DApp developers will seek certification from one of the issuers, according to their desired level of certification and will refer to the certificate on several platforms (e.g. on their website or in their DApp registration on a DApp store).

Certification is to be provided by certification issuers including: testing services (level 1), auditors (level 2), and verification services (level 3). Certification issuers will issue these certificates referring to a particular version of a DApp that has succesfully gone through a certification process. More details can be found about the certification levels on this [blogpost](https://iohk.io/en/blog/posts/2021/10/25/new-certification-levels-for-smart-contracts-on-cardano/). The [Certification Working Group](https://github.com/input-output-hk/Certification-working-group/) will work on establishing more formally those certification levels.

DApp stores and light wallets will be able to pull DApps information from DApps registration or chain exploring and will link a DApp to a corresponding set of certificates.

End-user will interact with a DApp through a wallet and will be able to check the different certificates obtained by the DApp.

One use-case would be for a wallet to maintain a list of valid certificates, and the corresponding DApp.
It could then both: verify that the user interacts with the latest version of the DApp through the Registration metadata of CIP-0072, and that the contract was certified using the corresponding metadata from this proposed CIP.

## Specification

### Definitions

- **anchor** - A hash written on-chain that can be used to verify the integrity (by way of a cryptographic hash) of the data that is found off-chain.
- **DApp** - A decentralised application that is described by the combination of metadata, certificate and a set of scripts.
- **dApp Store** - A dApp aggregator application which follows on-chain data looking for and verifying dApp metadata claims, serving their users linked dApp metadata.
- **Certification issuers** - A company that issues certification certificates on-chain.

### Evaluation issuers

Evaluation issuers will mint on-chain evaluation that will represent the level of certification desired and present evidence of the work done.

The minting policy for these NFTs must be controlled by each evaluation issuer. This policy ID could be used as the root of trust for evaluation, preventing evaluation forgeries.

### On-chain datum Schemas

The on-chain metadata stored in the reference token's datum should follow the following CDDL schema. This replaces the previous transaction metadata schema.
````cddl
; CIP-96 Certification Datum (version 1)
certification_datum = {
    certificationLevel: uint,
    scriptHashs: [text],
    evaluation_report: [[*text]]
    rootHash: text,
    schemaVersion: uint
}
````

### On-chain Metadata Properties

<!-- `subject`: Identifier of the claim subject (i.e dApp). A UTF-8 encoded string. The `subject` value needs to be the same as the one used for registering the DApp as per [CIP-0072](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0072). CIP-0072 gives no requirement or even recommendations on how to fill this value. -->

<!-- `type`: The type of the claim. This is a JSON object that contains the following properties: -->
<!-- 
- `action`: The action that the certificate is asserting. It can take the following values:
  - `CERTIFY`: The certificate is asserting that the dApp is being certified.
  - `AUDIT`: The certificate is asserting that an audit has been performed for this DApp. `AUDIT` shall come with a certification level `certificationLevel` of `0`. -->

- `certificationLevel`: The certification level is an integer between 0 and 3. 0 is reserved for audits and reports that are not compliant with the certification standards. 1, 2, and 3 refers to the certification certificates referring to the three levels of certifications as defined by the certification working group.
- `scriptHashs`: An array of strings, each string is the script Hash of a script that is part of the scope of the evaluated DApp. The list must be ordered.
- `evaluation_report`: An array of links to the evaluation report. The evaluation report is expected to be a PDF file that contains the evidence of the evaluation's issuer work. The links can be self-hosted by the evaluation issuer, on IPFS, or on any third-party service. The only requirement for an evaluation to be valid is that at least one of the URLs pointed in this field points to a correct evaluation report file whose hash is the same as the `rootHash` value.
- `rootHash`: A blake2b-256 hash of the evaluation report. This is used to verify the integrity of the off-chain report that is linked in the `evaluation_report` field. 
- `schemaVersion`: A versioning number for the json schema of the on-chain metadata. This current description shall be refered as `schemaVersion: 1`.

<!-- `metadata`: An array of links to the dApp's metadata. The metadata is a JSON object that follows the specification below. -->

Values for all fields shall be shorter than 64 characters to be able to be included on-chain.

### Example of Reference Token UTXO Datum
```json
{
    "certificationLevel": 2,
    "scriptHashs": [
        "f8b1c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8g9h0i1j2k3l4m5n6o7p8q9r0s1t"
    ],
    "evaluation_report": [
        "https://example.com/evaluation-report.pdf",
        "https://ipfs.io/ipfs/QmT5NvUtoM5nXQxWZy",
        "https://example.com/evaluation-report-2.pdf"
    ],
    "rootHash": "abcd1234efgh5678ijkl9012mnop3456qrst7890uvwx1234yzab5678cdef9012",
    "schemaVersion": 1
}
```
TODO:  To check and improve???


## Rationale: how does this CIP achieve its goals?

An on-chain solution is preferred as it allows for it to be checkable by any stakeholder and immutable.

This revised design leverages CIP-68 to represent certificates as first-class on-chain assets (NFTs). This provides several key advantages over the original transaction metadata approach.

### Why Use CIP-68 (Metadata NFT) over Transaction Metadata?
1. Enhanced Discoverability
2. On-Chain Updatability: If an issuer needs to update a evaluation's metadata (e.g., add a new URL to the metadata array or update the rootHash to a new report version), they can do so by creating a new UTXO for the reference token with the updated datum. This action does not change the user-facing NFT, which retains its asset ID. This provides a clean mechanism for versioning and updates without creating confusing, immutable historical entries in transaction metadata.
3. Stronger Trust Model: Trust is anchored to the NFT's policy ID. A wallet or dApp store can maintain a list of trusted policy IDs corresponding to known evaluation issuers. This is a more robust and cryptographically secure method of verification than checking the signature of a past transaction, as the policy itself governs the entire lifecycle of the certificate NFT.
4. Ownership: As a native token, the evaluation NFT can be held, transferred, used in smart contracts, or displayed in any wallet that supports NFTs. This makes the certificate a more versatile and integrated part of the Cardano ecosystem.
5. Script validation: Scripts can then use the presence of a specific evaluation NFT to authorize some key lifecycle actions of a Dapp, such as allowing a DApp to be upgraded or deployed. This provides trust to end-users that the DApp will always remain in a given evaluation state and that an operator will not be able to change the DApp's version without going through the evaluation process again.

### Other designs considered

#### Transaction Metadata (Original Design)
The initial design of this CIP used transaction metadata label `1304`. While functional, this approach lacks the easy updatability, and use in contract logic offered by the CIP-68 standard. The ecosystem has since moved towards using token-based metadata standards for these reasons, making the CIP-68 approach the clear path forward.

**Updates to registration entries**
This would have required DApp owner or certification issuers to add certificates to every registration making it harder to maintain a shared state between all stakeholders.
The chosen design requires to follow the chain to discover the certificates which should be expected from stakeholders.

## Path to Active

### Acceptance Criteria

Evaluation reports are being published on-chain using this CIP by auditors.

Evaluations are being issued on-chain by multiple auditors using this CIP.

### Implementation Plan


## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
