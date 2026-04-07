---
CIP: 88
Title: Token Policy Registration
Category: Tokens
Status: Active
Authors:
    - Adam Dean <adam@crypto2099.io>
Implementors: 
    - VeriGlyph Nexus: https://nexus.veriglyph.io
    - VeriGlyph Seninel: https://seninel.veriglyph.io
    - Cardano Signer: https://github.com/gitmachtl/cardano-signer?tab=readme-ov-file#cip-88v2-calidus-pool-key-mode
Discussions:
    - https://github.com/cardano-foundation/cips/pull/467
Created: 2023-02-27
License: CC-BY-4.0
---

## Abstract

Currently, token projects (NFT or FT) have no mechanism to register the intent, details, or feature set of their minting
policy on-chain. This CIP will aim to create a method that is backwards compatible and enable projects to declare, and
update over time, the supported feature set and metadata details pertaining to their tokens.

This CIP will aim to make use of a hybrid (on and off-chain) information schema to enable maximum flexibility and
adaptability as new and novel use cases for native assets expand and grow over time.

## Motivation: Why is this CIP necessary?

This CIP was borne out of a distaste for the lack of on-chain token policy intent registration that has been cited as
both a centralization and security concern at various points over the preceding two years of native asset history on
Cardano.

***Example 1: The Cardano Token Registry***

Many Fungible Token (FT) projects require special treatment of their native assets such as decimal places for proper
display and formatting, project information, and token logo. As it stands, these projects must currently register via a
GitHub repository ([Cardano Token Registry](https://github.com/cardano-foundation/cardano-token-registry)) in order to
have their token properly appear in wallets. This GitHub repository is currently managed by the Cardano Foundation (CF).
While there is no reason to believe that the CF would take any malicious or nefarious action, forcing token projects to
register in this fashion introduces a point of centralization, _potential_ gate keeping, and ultimately reliance on the
interaction of a 3rd party (the human at CF responsible for merging pull requests) in order for projects to register, or
update, their information.

***Note:*** The original intent of the *CIP-26 Cardano Token Registry* was never to have a sole provider or
controller of the repository. However, time has shown that there is little interest from the community or various
service providers to contribute or participate in this or alternative solutions.

This CIP attempts to provide a decentralized solution to this problem.

***Example 2: Token Metadata Insecurity***

One of the stated rationales for [CIP-68](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0068) was that the
"original" Cardano NFT Metadata Standard ([CIP-25](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0025)) was
insecure in some example use cases. This is due to the link between the transactional metadata and the minting of native
assets. For example, a smart contract that cannot/does not validate against transaction metadata (i.e. Liquidity Pool
tokens) could have a malicious user inject CIP-25 metadata into the transaction, potentially inserting illicit, illegal,
or otherwise nefarious metadata information tied to the tokens which may be picked up and displayed to end users
unwittingly by explorers and wallets.

***Example 3: De-duplication of Data***

Similar to **Example 1** above, when it comes to Non-Fungible Token (NFT) projects
currently operating on the chain there is usually a desire to provide some level of information that pertains to all
tokens under the given policy. Examples include project/collection names, social media handles, and miscellaneous
project registration information. At current, this is generally solved by adding "static" fields in the metadata of
every token. By moving this project-specific information a layer higher, not only do we achieve a path to dynamism
but also reduce ledger bloat size by de-duplicating data.

Similarly, there are currently multiple marketplaces and decentralized exchanges (DEXes) in operation in the Cardano
ecosystem. At current, most DEXes pull information from the _Cardano Token Registry_ but there is no similar function
for NFT projects. As such, much information must be manually provided to individual marketplaces by the token projects
creating an undue burden on the project creators to provide a largely static amount of information via different web
forms and authentication schemes rather than simply publishing this information to the blockchain directly.

### CPS-0001: Metadata Discoverability and Trust

[CPS-0001](https://github.com/cardano-foundation/CIPs/pull/371) presents a problem of metadata discoverability and
trust.
This CIP attempts to address and solve several of the issues proposed in CPS-0001 but is most likely not a "complete"
solution and is rather narrowed (for the time being) to the scope of token projects although with some refinement to
the schema could potentially be expanded to support additional scopes.

#### Discoverability

The primary purpose of this CIP is to enhance discoverability of token projects utilizing and parsing only the
information contained on-chain. In the first version of this CIP we address the discoverability of top-level information
related to "Token Projects" such as NFT and FT projects needing to provide social media handles, human-friendly names,
etc.

The goal of both minimizing redundant data stored on-chain and enhancing discoverability of projects for platforms
like DExes and NFT Marketplaces is specifically referenced in Example #3 above.

Note that while some external chain indexing and validation will ultimately be required, there is no off-chain,
centralized or decentralized trusted repository of additional information required (although aspects of the metadata
provided may rely on off-chain storage solutions).

#### Correctness

This CIP aims to ensure metadata "correctness" on two different fronts.

1. **Actual Data Correctness**
    - This CIP utilizes a strongly-typed, numerically indexed data structure that should minimize common errors and
      omissions observed in less strictly-typed standards. Parsers of the data presented within the scope of this
      standard should ignore any non-specified or non-conforming data.
2. **Data Provenance**
    - Specifically in the context of correctness via proving provenance of the metadata, this CIP aims to address
      correctness via the same data witness standards utilized by CIP-26 although with a slightly modified data
      structure.
      Currently existing solutions for things like NFT Project verification standards rely on trust methods such as
      publishing a special message on your website, send us a DM from your Twitter account, and other less secure means
      of validating provenance of the data.

#### Trust

As mentioned in the *Data Provenance* note on Data Correctness above, this CIP minimizes the trust required by relying
on a verifiable witness signature versus currently existing solutions which largely rely on off-chain trust mechanisms
for proof of provenance. Therefore, we increase trust in the data by describing a relatively simple means of data
validation while decreasing the need for trust outside the scope of the on-chain metadata.

## Specification

Where applicable the 0 (zero) index of all specification documents is reserved for an optional integer version
identifier to enable future extensions to this and CIP-specific sub-standards.

A numeric-indexed structure is used to support required and optional fields in a format that is compatible with both
CBOR and JSON transport formats with minimal changes to the data structure and to minimize the possibility of
misspelling or capitalization issues.

### Modification and Extension of This Standard

This standard is likely to need frequent extension and modification, particularly relating to
[CIP-Specific Information](#6-cip-specific-information). Any group or individual wishing to extend or modify this
standard MUST comply to the following criteria:

- [ ] New CIPs SHOULD achieve the `Active` status prior to being included and documented in this directory after
  undergoing the
  regular community feedback and review process.
- [ ] Any change or modification to `required` fields in the root standard or a CIP's specific details MUST be written
  as a new `version`, MUST increment the version number by `1`, and MUST include new, versioned documentation for
  the CIP while leaving previous version documentation intact for backwards compatibility.
- [ ] Submissions for addition to this CIP MUST be made via a separate, dedicated pull request against this repository
  so that the format and documentation pertaining to CIP-88 specifically can undergo community review and feedback
  prior to inclusion here.
- [ ] Whenever possible, extensions to this CIP SHOULD attempt to introduce new indices and object definitions without
  changing or modifying existing data structures to enable new functionality and existing implementations to operate
  until newer standards can be adopted and enhance functionality rather than change it.
- [ ] New CIP submissions MUST follow the same paradigms and documentation examples as those found within the
  [CIPs](./CIPs) directory including:
    - [ ] a README.md document describing the fields, values, and rationale
    - [ ] a CBOR CDDL specification file
    - [ ] a JSON format schema file (_optional_)
    - [ ] a JSON example file showing all defined fields (_optional_)

### Registration Metadata Format

`Version: 1`

| Index | Name                                                 | Type  | Required | Notes                                                        |
|-------|------------------------------------------------------|-------|----------|--------------------------------------------------------------|
| 0     | Version                                              | UInt  | Yes      |                                                              |
| 1     | [Registration Payload](#registration-payload-object) | Map   | Yes      | Object describing and providing details for the token policy | 
| 2     | [Registration Witness](#registration-witness-array)  | Array | Yes      | Array of witness signatures used to validate the payload     |

### Registration Payload Object

The Token Registration Payload Object (TRPO) consists of 4 required fields and optional additional fields to
provide context and information. The top-level metadata label of **867** has been chosen for the purposes of this
standard.

#### Fields

| Index | Name                                        | Type   | Required | Notes/Examples                                                                                                                                                                                                                                    |
|-------|---------------------------------------------|--------|----------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 1     | Scope                                       | Array  | Yes      | An array defining the scope of this registration (for greater compatibility with CPS-0001). The first entry should be an unsigned integer value identifying the type of scope while the second entry addresses the specific scope of registration |
| 2     | Feature Set                                 | Array  | Yes      | An array of unsigned integers specifying none or more CIP standards utilized by the tokens of this project. Should reference the assigned CIP number.                                                                                             |
| 3     | Validation Method                           | Array  | Yes      | How should this payload be validated.                                                                                                                                                                                                             |
| 4     | Nonce                                       | UInt   | Yes      | A simple cache-busting nonce. Recommend to use the blockchain slot height at the time of submission. Only the highest observed nonce value should be honored by explorers.                                                                        |
| 5     | Oracle URI                                  | Array  | No       | Reserved for future use, URI to an informational oracle API for this policy                                                                                                                                                                       |
| 6     | [CIP Details](#6--cip-specific-information) | Object | No       | If one or more of the CIPs addressed in the Feature Set have additionally defined metadata, it may be added here                                                                                                                                  |

The following fields are required in all token registration submissions.

##### 1. Scope

Currently, this CIP concerns itself with the scope of *Tokens* with relation to CPS-0001 as described in the Motivation
section. However, the specification is left flexible to encapsulate additional scopes and contexts (Stake Pools, dApps,
etc.) should the specification become adopted and the community desire to expand the scope of this CIP.

**Scopes**

| ID  | Scope         | Format                             |
|-----|---------------|------------------------------------|
| 0   | Native Script | `[0, h'policyID', [h'policyHex']]` |

0. **Native Scripts**: Native scripts should be specified as an array with the first entry indicating the type (Native
Script), the second entry indicating the script hash (Policy ID) and the third entry consisting of an array with one or
more 64-byte strings constituting the hex-encoded CBOR representation of the Native Script itself. In this way, CIP-88
registration may be submitted on-chain prior to any tokens being minted and can be used by validators to confirm the
legitimacy of the certificate without any secondary information source.

**Example:**

`[0, h'3668b628d7bd0cbdc4b7a60fe9bd327b56a1902e89fd01251a34c8be', h'8200581c4bdb4c5017cdcb50c001af21d2488ed2e741df55b252dd3ab2482050']`

#### 2. Feature Set

The _Feature Set_ is a simple array of unsigned integer values representing the CIP standards that should be applied to
the subject scope.

**Example:**

`[25, 27]`

#### 3. Validation Method

In order to minimize issues relating to capitalization and misspellings, we should use a well-defined map of integer
values for validation methods that will be utilized by third party observers and processors to authenticate the payload.
The validation method entry should always be provided as an array with the first element being an unsigned integer
representing the method and additional entries providing additional context to the validation as required.

***Proposed Validation Methods***

| ID  | Type                   | Format                              | Notes                                                                                                                                                                                                                                                                                                                                                                                                                                      |
|-----|------------------------|-------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0   | Ed25519 Key Signature  | `[0]`                               | The most basic and simplistic approach to signing and validation. In this case the Registration Witness object could contain one or more pubkey + signed witness objects. The payload to be signed should be the hex-encoded CBOR representation of the Registration Payload object.                                                                                                                                                       |
| 1   | Beacon/Reference Token | `[1, [h'<policyId>',h'<assetId>']]` | Similar to the approach utilized by [CIP-27](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0027). We could attach this metadata during a mint transaction for a specially formatted token under the policy ID in question. CIP-27 uses a "nameless" token that has an empty "Asset ID" for example. This may be a validation method that lends itself better to supporting token projects that are minted via Smart Contract. |

**Examples:**

`[0]`,
`[1, [h'<policyId>',h'<assetId>']]`

#### 4. Nonce

The nonce value is utilized to prevent a replay attack vector. The nonce value should be an unsigned integer value that
is always at least one greater than the previously registered value.

**Example:**

`12345`

#### 5. Data Oracle URI

To be utilized and expanded upon in a separate CIP, this should be a valid URI pointing to a source of additional,
potentially dynamic information relating to the project and/or the tokens minted under it.

**Example:**

`[
"https://",
"oracle.mytokenproject.io/"
]`

#### 6. CIP-Specific Information

This entry, if present, should be a CIP ID indexed object containing additional information pertaining to that CIP.
When and where possible the CIP-Specific registration should follow the CBOR-like declaration syntax to ensure that
the content is well-formed and easily parseable.

| CIP | Name                          | Version | Status | CDDL                                       | Rationale             |
|-----|-------------------------------|---------|--------|--------------------------------------------|-----------------------|
| 25  | Token Metadata                | 1       | Active | [CIP25_v1.cddl](./CIPs/0025/CIP25_v1.cddl) | [CIP-25](./CIPs/0025) |
| 26  | Fungible Token Information    | 1       | Active | [CIP26_v1.cddl](./CIPs/0026/CIP26_v1.cddl) | [CIP-26](./CIPs/0026) |
| 27  | Token Royalties               | 1       | Active | [CIP27_v1.cddl](./CIPs/0027/CIP27_v1.cddl) | [CIP-27](./CIPs/0027) |
| 48  | Metadata References           | 1       | Draft  | [CIP48_v1.cddl](./CIPs/0048/CIP48_v1.cddl) | [CIP-48](./CIPs/0048) |
| 60  | Music Token Metadata          | 1       | Draft  | [CIP60_v1.cddl](./CIPs/0060/CIP60_v1.cddl) | [CIP-60](./CIPs/0060) |
| 68  | Datum Token Metadata          | 1       | Active | [CIP68_v1.cddl](./CIPs/0068/CIP68_v1.cddl) | [CIP-68](./CIPs/0068) |
| 86  | Token Metadata Update Oracles | 1       | Active | [CIP86_v1.cddl](./CIPs/0086/CIP86_v1.cddl) | [CIP-86](./CIPs/0086) |

***Note: CIP-0068 Tokens***

Due to a lack of clarity in the original language of CIP-0068, standards for fungible, non-fungible, and "rich" fungible
tokens have been added to the core standard. To accommodate for this, projects should use the CIP-68 data when using the
`222` (NFT) or `444` (RFT) tokens for top-level project information. Projects utilizing the `333` (FT) style tokens
should utilize the CIP-26 data structure to provide fungible token context.

***Beacon Token Registration***

Where applicable to a specific CIP, the CIP-specific registration may refer to a "beacon token". This is standardized
in this CIP as a two-element array consisting of the hex-encoded policy ID and asset ID of the token to be used as a
beacon token for the purposes of smart contract interactions. e.g. `[
h'<policy_id>',
h'<asset_id>'
]`

**Multiple Feature Set Example (CBOR):**

```cbor 
{
  25: {
    0: 1,
    1: {
      0: "Cool NFT Project",
      1: [
        "This is a description of my project",
        "longer than 64 characters so broken up into a string array"
      ],
      2: [
        "https://",
        "static.coolnftproject.io",
        "/images/icon.png"
      ],
      3: [
        "https://",
        "static.coolnftproject.io",
        "/images/banner1.jpg"
      ],
      4: 0,
      5: [
        [
          "twitter",
          [
            "https://",
            "twitter.com/spacebudzNFT"
          ]
        ],
        [
          "discord",
          [
            "https://",
            "discord.gg/spacebudz"
          ]
        ]
      ],
      6: "Virtua Metaverse"
    }
  },
  27: {
    0: 1,
    1: {
      1: "0.05",
      2: [
        "addr_test1qqp7uedmne8vjzue66hknx87jspg56qhkm4gp6ahyw7kaahevmtcux",
        "lpy25nqhaljc70094vfu8q4knqyv6668cvwhsq64gt89"
      ]
    }
  }
}
```

### Registration Witness Array

#### (Native Scripts)

The Witness Array included in the on-chain metadata should consist of an array of arrays with two elements, the public
key of the signing key and the signed key witness. If a script requires multiple signatures, enough signatures to meet
the criteria of the script should be included and required for proper validation of an updated token registration.

The signing payload should be the hex-encoded Token Registration Payload Object.

**Example**

```cbor
[
  [
    h'02b76ae694ce6549d4a20dce308bc7af7fa5a00c7d82b70001e044e596a35deb',
    h'23d0614301b0d554def300388c2e36b702a66e85432940f703a5ba93bfb1659a0717962b40d87523c507ebe24efbb12a2024bb8b14441785a93af00276a32e08'
  ],
  [
    h'26bacc7b88e2b40701387c521cd0c50d5c0cfa4c6c6d7f0901395757',
    h'secondSignatureByteString'
  ]
]
```

### Example NFT Token Registration Metadata

Below is a complete example of the hypothetical metadata payload for an NFT project registering their policy on-chain.

```cbor
{
  867: {
    0: 1,
    1: {
      1: [
        0, 
        h'3668b628d7bd0cbdc4b7a60fe9bd327b56a1902e89fd01251a34c8be', 
        h'8200581c4bdb4c5017cdcb50c001af21d2488ed2e741df55b252dd3ab2482050'
      ],
      2: [
        25,
        27
      ],
      3: [0],
      4: 12345,
      5: [
        "https://",
        "oracle.mycoolnftproject.io/"
      ],
      6: {
        25: {
          0: 1,
          1: {
            0: "Cool NFT Project",
            1: [
              "This is a description of my project",
              "longer than 64 characters so broken up into a string array"
            ],
            2: [
              "https://",
              "static.coolnftproject.io",
              "/images/icon.png"
            ],
            3: [
              "https://",
              "static.coolnftproject.io",
              "/images/banner1.jpg"
            ],
            4: 0,
            5: [
              [
                "twitter",
                [
                  "https://",
                  "twitter.com/spacebudzNFT"
                ]
              ],
              [
                "discord",
                [
                  "https://",
                  "discord.gg/spacebudz"
                ]
              ]
            ],
            6: "Virtua Metaverse"
          }
        },
        27: {
          0: 1,
          1: {
            1: "0.05",
            2: [
              "addr_test1qqp7uedmne8vjzue66hknx87jspg56qhkm4gp6ahyw7kaahevmtcux",
              "lpy25nqhaljc70094vfu8q4knqyv6668cvwhsq64gt89"
            ]
          }
        }
      }
    },
    2: [
      [
        h'02b76ae694ce6549d4a20dce308bc7af7fa5a00c7d82b70001e044e596a35deb',
        h'23d0614301b0d554def300388c2e36b702a66e85432940f703a5ba93bfb1659a0717962b40d87523c507ebe24efbb12a2024bb8b14441785a93af00276a32e08'
      ],
      [
        h'26bacc7b88e2b40701387c521cd0c50d5c0cfa4c6c6d7f0901395757',
        h'secondWitnessByteString'
      ]
    ]
  }
}
```

### Example Fungible Token Registration Metadata

```cbor
{
  867: {
    0: 1,
    1: {
      1: [
        0, 
        h'3668b628d7bd0cbdc4b7a60fe9bd327b56a1902e89fd01251a34c8be', 
        h'8200581c4bdb4c5017cdcb50c001af21d2488ed2e741df55b252dd3ab2482050'
      ],
      2: [
        26
      ],
      3: [0],
      4: 12345,
      5: [
        "https://",
        "oracle.tokenproject.io/"
      ],
      6: {
        26: {
          0: 1,
          1: [
            {
              0: [
                h"d894897411707efa755a76deb66d26dfd50593f2e70863e1661e98a0",
                h"7370616365636f696e73"
              ],
              1: "spacecoins",
              2: [
                "the OG Cardano community token",
                "-",
                "whatever you do, your did it!",
                "",
                "Learn more at https://spacecoins.io!"
              ],
              3: "SPACE",
              4: 0,
              5: [
                "https://",
                "spacecoins.io"
              ],
              6: [
                "ipfs://",
                "bafkreib3e5u4am2btduu5s76rdznmqgmmrd4l6xf2vpi4vzldxe25fqapy"
              ],
              7: [
                [
                  "ipfs://",
                  "bafkreibva6x6dwxqksmnozg44vpixja6jlhm2w7ueydkyk4lpxbowdbqly"
                ],
                "3507afe1daf05498d764dce55e8ba41e4acecd5bf42606ac2b8b7dc2eb0c305e"
              ],
              8: [
                h"d894897411707efa755a76deb66d26dfd50593f2e70863e1661e98a0",
                h"7370616365636f696e74"
              ]
            }
          ]
        }
      }
    },
    2: [
      [
        h'02b76ae694ce6549d4a20dce308bc7af7fa5a00c7d82b70001e044e596a35deb',
        h'23d0614301b0d554def300388c2e36b702a66e85432940f703a5ba93bfb1659a0717962b40d87523c507ebe24efbb12a2024bb8b14441785a93af00276a32e08'
      ]
    ]
  }
}
```

## Rationale: how does this CIP achieve its goals?

For this specification, I have drawn inspiration from
[CIP-36: Catalyst/Voltaire Registration Metadata Format](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0036)
which succinctly and canonically publishes data to the main chain (L1) via a metadata transaction and without any
required modification or customization to the underlying ledger.

By leveraging the existing signing keys present in native asset scripts from the beginning of the Mary Era on Cardano we
can enable all projects to update and provide additional, verified information about their project in a canonical,
verifiable, and on-chain way while also providing for additional off-chain information.

This makes this CIP backwards compatible with all existing standards (CIP-25, 26, 27, 68, etc) while also providing the
flexibility for future-proofing and adding additional context and information in the future as additional use cases,
utility, and standards evolve.

## Path to Active

### Acceptance Criteria

- [X] This CIP should receive feedback, criticism, and refinement from: CIP Editors and the community of people involved
  with token projects (both NFT and FT) to review any weaknesses or areas of improvement.
- [x] Guidelines and examples of publication of data as well as discovery and validation should be included as part of
  criteria for acceptance.
- [X] Specifications should be updated to be written in both JSON Schema and CBOR CDDL format for maximum compatibility.
- [x] Implementation and use demonstrated by the community: Token Projects, Blockchain Explorers, Wallets,
  Marketplaces/DEXes.

#### TO-DO ACCEPTANCE ACTIONS ####

- [x] Publish instructions and tooling for publication and verification of certificates
- [ ] Develop standard for validation of Smart Contract minted tokens

### Implementation Plan

1. Publish open source tooling and instructions related to the publication and verification of data utilizing this
   standard.
2. Achieve "buy in" from existing community actors and implementors such as: blockchain explorers, token marketplaces,
   decentralized exchanges, wallets.

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
