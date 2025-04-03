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

This CIP descibes a standardised method for certificates to be published and stored on-chain and for stakeholders to be able to verify the different claims of this certificate.

This CIP describes how a certification certificate can be registered on-chain and how to anchor it to a more detailed off-chain certification report.

## Motivation: why is this CIP necessary?

It is expected that evidence of various kinds of assurance of DApps is recorded in an immutable and verifiable way on the Cardano blockchain.
Three levels of certification are thought of at the time of this CIP: level 1 to 3. They were presented at the following [link](https://iohk.io/en/blog/posts/2021/10/25/new-certification-levels-for-smart-contracts-on-cardano/) and will be fully described in a future document.

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

### Certification issuers

Certification issuers will broadcast on-chain certificates that will represent the level of certification reached and present evidence of the work done.

Certification issuers will sign the transaction with the certification certificate as metadata from a known payment address. They will attest that they have done the work and prevent certificate forgeries.

### Suggested validations

- `integrity`: The DApp's metadata off-chain shall match the metadata **anchored** on-chain.
- `trust`: The DApp's certification metadata transaction shall be signed by a trusted certfication issuer. This means a list of wallets of certification issuers needs to be known. It will then be up to the DApp store to decide which certification issuers are really trusted and publish a list of their own trusted certification issuers. It is not in the scope of this CIP to establish such a list. 


### Certificate Schemas

The on-chain metadata should follow the following CDDL schema: [CDDL Schema version 1](./version_1_onchain.cddl). A JSON version of this schema is also available: [JSON Schema Version 1](./version_1_onchain.json).

If new version of the schemas are released, we will keep in this section all the previous ones.


### On-chain Metadata Properties

`subject`: Identifier of the claim subject (i.e dApp). A UTF-8 encoded string. The `subject` value needs to be the same as the one used for registering the DApp as per [CIP-0072](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0072). CIP-0072 gives no requirement or even recommendations on how to fill this value.

`type`: The type of the claim. This is a JSON object that contains the following properties:

- `action`: The action that the certificate is asserting. It can take the following values:
  - `CERTIFY`: The certificate is asserting that the dApp is being certified.
  - `AUDIT`: The certificate is asserting that an audit has been performed for this DApp. `AUDIT` shall come with a certification level `certificationLevel` of `0`.

  - `certificationLevel`: The certification level is an integer between 0 and 3. 0 is reserved for audits and reports that are not compliant with the certification standards. 1, 2, and 3 refers to the certification certificates referring to the three levels of certifications as defined by the certification working group.
  - `certificationIssuer`: The name of the certification issuer.

`rootHash`: The hash of the metadata entire tree object. This hash is used by clients to verify the integrity of the metadata tree object. When reading a metadata tree object, the client should calculate the hash of the object and compare it with the rootHash property. If the two hashes don't match, the client should discard the object. The metadata tree object is a JSON object that contains the dApp's metadata. The metadata tree object is described in the next section.

This hash is calculated by taking the entire metadata tree object, ordering the keys in the object alphanumerically, and then hashing the resulting JSON string using the **blake2b-256** hashing algorithm. The hash is encoded as a hex string.

`schemaVersion`: A versioning number for the json schema of the on-chain metadata. This current description shall be refered as `schemaVersion: 1`.

`metadata`: An array of links to the dApp's metadata. The metadata is a JSON object that follows the specification below.

Values for all fields shall be shorter than 64 characters to be able to be included on-chain.

### Metadata Label

When submitting the transaction metadata pick the following value for `transaction_metadatum_label`:

- `1304`: DApp Certification

### Example


```json
{
    "subject": "d684512ccb313191dd08563fd8d737312f7f104a70d9c72018f6b0621ea738c5",
    "rootHash": "4e9eec517ab811600c8a8c1ba75c992f5f27f8a330003e892e1d5a601c6b6c19",
    "metadata": [
    "https://example.com/metadata.json"],
    "schema_version": 1,
    "type": { 
        "action": "CERTIFY",
        "certificationLevel": 1,
        "certificateIssuer": "Example LLC.",
    },
}
```

### Off-chain Metadata Format

The Dapp Certification certificate is complemented by off-chain metadata that can be fetched from servers that will hosts the off-chain metadata file. 
The metadata can be self hosted by the DApp developer, the certificate issuer, on IPFS, or on any-third party service. The only requirement for a certificate to be valid is that at least one of the URL pointed in the `metadata` field points to a correct off-chain metadata JSON file whose hash is the same as the `rootHash` value.

### Off-chain Metadata Properties

`subject`, a mandatory string, Identifier of the claim subject (i.e dApp). A UTF-8 encoded string. This field is required to be the same as the on-chain `subject` field. 

`schemaVersion`, a mandatory string, used as a versioning number for the Json schema of the on-chain metadata. This current description shall be refered as `schemaVersion: 1`.

`certificateIssuer`, a mandatory object used to describe the certification issuer, that contains the following fields:

- `name`, a mandatory string, the name of the certification issuer
- `logo`, a string, a link to the logo of the certification issuer. The logo could be self-hosted in order to allow updates on the logo design.
- `social`, an object used to list all the different social contacts of the Certificate Issuer:
  - `twitter`, a string, the twitter handle of the Certificate Issuer
  - `github`, a string, the github handle of the Certificate Issuer
  - `contact`, a mandatory string, the contact email of the Certificate Issuer
  - `website`, a mandatory string, a link to the Certificate Issuer's website
  - `discord`, a string, a link to the Certificate Issuer's Discord server

`report`, an object that contains:

- `reportURLs`, an array of URLs, is a field where each link points to the same actual certification report for anyone to read. This ensures transparency in the findings, what was and was not considered in the certification process..
- `reportHash`, a string, is a field that is the blake2b-256 hash of the report pointed by the links in `reportURLs`.

`summary`, a string, that contains the summary of the report from the certification issuer.

`disclaimer`, a string, that contains the legal disclaimer from the certification issuer.

`script` an array of objects that represents the whole DApp's on-chain script. Each object is comprised of:
- `scriptHash`, a string, is the script hash or script hash+staking key
- `contractAddress`, a string, the script address

The off-chain metadata shall follow the following JSON schema [JSON Schema version 1](./version_1_offchain.json). If new schemas for the offchain metadata are released, the previous ones will also be linked in this section.

### Example

```json
{
  "subject": "d684512ccb313191dd08563fd8d737312f7f104a70d9c72018f6b0621ea738c5",
  "schemaVersion": 1,
  "certificationLevel": 1,
  "certificateIssuer": {
    "name": "Example LLC",
    "logo": "https://www.example.com/media/logo.svg",
    "social": {
        "contact": "contact@example.com",
        "link": "https://example.com",
        "twitter": "twiterHandle",
        "github": "githubHandle",
        "website": "https://www.example.com"
    }
  },
  "report": {
    "reportURLs": [
        "https://example.io/certificate.pdf",
        "ipfs://bafybeiemxfal3jsgpdr4cjr3oz3evfyavhwq"
        ],
    "reportHash": "c6bb42780a9c57a54220c856c1e947539bd15eeddfcbf3c0ddd6230e53db5fdd"
  },
  "summary": "This is the summary of the report.",
  "disclaimer": "This is the legal disclaimer from the report",
  "scripts": [
        {
          "smartContractInfo": {
            "era": "basho",
            "compiler": "plutusTx",
            "compilerVersion": "1.3.0",
            "optimizer": "plutonomy",
            "optimizerVersion": "v0.20220721",
            "progLang": "plutus-v2",
            "repository": "https://github.com/DAppDev/TestDApp/"
          },
          "scriptHash": "1dcb4e80d7cd0ed384da5375661cb1e074e7feebd73eea236cd68192",
          "contractAddress": "addr1wywukn5q6lxsa5uymffh2esuk8s8fel7a0tna63rdntgrysv0f3ms"
        },
        {
          "smartContractInfo": {
            "era": "basho",
            "compiler": "plutusTx",
            "compilerVersion": "1.3.0",
            "optimizer": "plutonomy",
            "optimizerVersion": "v0.20220721",
            "progLang": "plutus-v2",
            "repository": "https://github.com/DAppDev/TestDApp/"
          },
          "scriptHash": "6cd68191dcb4e80d7c5661cb1e074e7feebd73eea232d0ed384da537",
          "contractAddress": "addr1wywukn5q6lrdntgrysv0f7a0tna63ymffh23ms5uxsaesuk8s8fel"
        }
  ]
}
```

The metadata should be discoverable by all certification stakeholders, including end-users, DApp developers, and ecosystem components, such as light wallets and DApp stores. Information should be indexable by certification issuer, DApp developer, DApp and DApp version.

It should be possible for there to be multiple versions of metadata published by the same certification issuer for the same version of a DApp, particularly when a (minor) update of the evidence is necessary.

In such a case it should be possible to identify the most recent version of the report for that DApp version. It will also be the case that the same DApp may have certification metadata provided by multiple different certification issuers.

It will be possible for wallets to identify to users the certification status of a DApp when they are signing a transaction that is being submitted to a deployed DApp.

Registration update (see [CIP-0072](https://github.com/cardano-foundation/CIPs/pull/355)) mandates the DApp developer to list all the script hashes associated with the DApp. This enables to fully characterize the on-chain part of a DApp.
Similarly, the certification certificate mandates the certification issuer to list all the script hashes of the DApp.

Cross-checking the list of script information from both sources will allow for a wallet to get the latest version of the on-chain part of a DApp and checking if there is a corresponding certification associated.
The wallet would then be able to inform a user that they are about to sign a transaction for a DApp that is certified. The wallet could also link to the certificate on-chain, if the user wants to know more about the certificate.

Certificates could be filtered by either the wallet, the user, or both from their own lists of known and trusted auditors.


### Aggregators Custom Fields
Each aggregator or DApp store can add their own requirements for the metadata or can offer additional features if the report pointed by `reportURLs`.
The aggregator or DApp store should advertise their requirements in a documentation so that a certification issuer can format their report accordingly.
Similarly, certification issuers can format their report pointed by `reportURLs` as they please and document any design choice so that aggregators or DApp stores can offer additional features by parsing the report.

## Rationale: how does this CIP achieve its goals?

An on-chain solution is preferred as it allows for it to be checkable by any stakeholder and immutable.

Certificate are issued by certification issuers that sign the certificate transaction to prevent certificate forgeries.

This design allows for anyone to issue certificates as long as they sign it but other stakeholders are then free to maintain a list of the trusted certification issuers.

These certificates are self-standing and can be presented as-is by any stakeholder.

This proposal does not affect any backward compatibility of existing solution but is based on the work done for CIP72 on DApp registration and Discovery. It is also linked to CIP52 on Cardano audit best practices guidelines.

### Other designs considered

**Updates to registration entries**
This would have required DApp owner or certification issuers to add certificates to every registration making it harder to maintain a shared state between all stakeholders.
The chosen design requires to follow the chain to discover the certificates which should be expected from stakeholders.

## Path to Active

### Acceptance Criteria

Audits are being published on-chain using this CIP by auditors.

The Certification Working Group has produced the specification for the different certification levels, in a CIP or in another reference documents.

Certificates are being issued on-chain by multiple auditors and certification companies using this CIP.

Certificates are being displayed by multiple DApps stores or aggregators which uses this format.

Certificates for all three certification levels have been issued using this schema.

### Implementation Plan

- [x] This CIP will be discussed and agreed by the Cardano Certification Working Group where multiple auditors are being represented. This will ensure that certification issuer have agreed on the content and are ready to issue certificates under this format.

- [x] This CIP will be presented to the IOG Lace team and Cardano Fans team which will display certificates for DApps. This is to ensure that the format contains all the necessary information for a DApp store or an aggregator to correctly link and display a certificate from the on-chain and off-chain metadata.

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
