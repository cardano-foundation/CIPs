---
CIP: 88
Title: Token Policy Registration
Category: Tokens
Status: Proposed
Authors:
  - Adam Dean <adam@crypto2099.io>
Implementors: N/A
Discussions: https://github.com/cardano-foundation/cips/pull/467
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

Many Fungible Token (FT) projects require special treatment of their NAs such as decimal places for proper display and
formatting, project information, and token logo. As it stands, these projects must currently register via a GitHub
repository ([Cardano Token Registry](https://github.com/cardano-foundation/cardano-token-registry)) in order to have
their token properly appear in wallets. This GitHub repository is currently managed by the Cardano Foundation (CF).
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
      standard
      should ignore any non-specified or non-conforming data.
2. **Data Provenance**
    - Specifically in the context of correctness via proving provenance of the metadata, this CIP aims to address
      correctness via the same data witness standards utilized by CIP-26 although with a slightly modified data
      structure.
      Currently existing solutions for things like NFT Project verification standards rely on trust methods such as
      publish a special message on your website, send us a DM from your Twitter account, and other less secure means of
      validating provenance of the data.

#### Trust

As mentioned in the *Data Provenance* note on Data Correctness above, this CIP minimizes the trust required by relying
on a verifiable witness signature versus currently existing solutions which largely rely on off-chain trust mechanisms
for proof of provenance. Therefore, we increase trust in the data by describing a relatively simple means of data
validation while decreasing the need for trust outside the scope of the on-chain metadata.

## Specification

Where applicable the 0 (zero) index of all specification documents is reserved for an optional semantic version
identifier to enable future extensions to this and CIP-specific sub-standards.

A numeric-indexed structure is used to support required and optional fields in a format that is compatible with both
CBOR and JSON transport formats with minimal changes to the data structure and to minimize the possibility of
misspelling or capitalization issues.

### Registration Metadata Format

`Version: 1.0.0`

| Index | Name                                                 | Type   | Required | Notes                                                        |
|-------|------------------------------------------------------|--------|----------|--------------------------------------------------------------|
| 0     | Version                                              | String | No       |                                                              |
| 1     | [Registration Payload](#registration-payload-object) | Map    | Yes      | Object describing and providing details for the token policy | 
| 2     | [Registration Witness](#registration-witness-array)  | Array  | Yes      | Array of witness signatures used to validate the payload     |

### Registration Payload Object

The Token Registration Payload Object (TRPO) consists of 4 required fields and then optional, additional fields to
provide additional context and information as part of the registration payload. The top-level metadata label of **867**
has been chosen for the purposes of this standard.

#### Fields

| Index | Name                                | Type  | Required | Notes/Examples                                                                                                                                                                                                                                    |
|-------|-------------------------------------|-------|----------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 1     | Scope                               | Array | Yes      | An array defining the scope of this registration (for greater compatibility with CPS-0001). The first entry should be an unsigned integer value identifying the type of scope while the second entry addresses the specific scope of registration |
| 2     | Feature Set                         | Array | Yes      | An array of unsigned integers specifying none or more CIP standards utilized by the tokens of this project. Should reference the assigned CIP number.                                                                                             |
| 3     | Validation Method                   | Array | Yes      | How should this payload be validated.                                                                                                                                                                                                             |
| 4     | Nonce                               | UInt  | Yes      | A simple cache-busting nonce. Recommend to use the blockchain slot height at the time of submission. Only the highest observed nonce value should be honored by explorers.                                                                        |
| 5     | Oracle URI                          | Array | No       | Reserved for future use, URI to an informational oracle API for this policy                                                                                                                                                                       |
| 6     | [CIP Details](#cip-specific-fields) | Array | No       | If one or more of the CIPs addressed in the Feature Set have additionally defined metadata, it may be added here                                                                                                                                  |

The following fields are required in all token registration submissions.

##### 1. Scope

Currently, this CIP concerns itself with the scope of *Tokens* with relation to CPS-0001 as described in the Motivation
section. However, the specification is left flexible to encapsulate additional scopes and contexts (Stake Pools, dApps,
etc.) should the specification become adopted and the community desire to expand the scope of this CIP.

**Scopes**

| ID  | Scope         | Format             |
|-----|---------------|--------------------|
| 0   | Token Project | `[0, h'policyID']` |

**Example:**

`[0, h'00000002df633853f6a47465c9496721d2d5b1291b8398016c0e87ae']`

#### 2. Feature Set

**Example:**

`[25, 27]`

#### 3. Validation Method

In order to minimize issues relating to capitalization and misspellings, we should use a well-defined map of integer
values for validation methods that will be utilized by third party observers and processors to authenticate the payload.
The validation method entry should always be provided as an array with the first element being an unsigned integer
representing the method and additional entries providing additional context to the validation as required.

***Proposed Validation Methods***

| ID  | Type                   | Format                  | Notes                                                                                                                                                                                                                                                                                                                                                                                                                                      |
|-----|------------------------|-------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0   | Ed25519 Key Signature  | `[0]`                   | The most basic and simplistic approach to signing and validation. In this case the Registration Witness object could contain one or more pubkey + signed witness objects. The payload to be signed should be the hex-encoded CBOR representation of the Registration Payload object.                                                                                                                                                       |
| 1   | Beacon/Reference Token | `[1, [h'policyId',h'']` | Similar to the approach utilized by [CIP-27](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0027). We could attach this metadata during a mint transaction for a specially formatted token under the policy ID in question. CIP-27 uses a "nameless" token that has an empty "Asset ID" for example. This may be a validation method that lends itself better to supporting token projects that are minted via Smart Contract. |

**Examples:**

`[0]`,
`[1, [h'policyId',h'']`

#### 4. Nonce

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

These additional CIPs/Schemas to be determined by the community could include:

- CIP-25 &amp; CIP-68 NFT Project top-level project information
- CIP-26 FT Project Monetary Policy information
- CIP-27 NFT Project Royalty information
- CIP-48 Metadata References information
- CIP-60 Music NFT information

***Beacon Token Registration***

Where applicable to a specific CIP, the CIP-specific registration may refer to a "beacon token". This is standardized
in this CIP as a two-element array consisting of the hex-encoded policy ID and asset ID of the token to be used as a
beacon token for the purposes of smart contract interactions.

##### CIP-Specific Fields

| index | name                | type   | required | notes                             |
|-------|---------------------|--------|----------|-----------------------------------|
| 25    | NFT Project         | Object | No       | CIP-25 NFT Project details        |
| 26    | FT Project          | Object | No       | CIP-26 FT Project details         |
| 27    | NFT Royalties       | Object | No       | CIP-27 NFT Royalty details        |
| 48    | Metadata References | Object | No       | CIP-48 Metadata Reference details |
| 60    | Music NFT Project   | Object | No       | CIP-60 Music NFT details          |
| 68    | NFT Project         | Object | No       | CIP-68 NFT Project details        |

**Example:**

```cbor
{
    867: {
        0: "1.0.0",
        1: {
            6: {
                25: {
                    0: "1.5.7",
                    1: {...details...}
                },
                27: {...}
            }
        },
        2: [...]
    }
}
```

##### CIP-25 & CIP-68: Non-Fungible Tokens / Policy Information

`Version: 1.0.0`

***CIP-25 & CIP-68 Top-Level Object Fields***

Both CIP-25 and CIP-68 are specifications describing a standard for storing and retrieving NFT metadata from the chain.
To this end, we have given them the same data structure although each will utilize their own numerical index in the
feature set and CIP-Specific details section of the registration.

These sections may be separated in the future if the respective CIPs diverge in terms of the data or information that
may be useful to provide about one format or the other diverge in the future.

| index | name                | type   | required | notes                                                                                                                                      |
|-------|---------------------|--------|----------|--------------------------------------------------------------------------------------------------------------------------------------------|
| 0     | Version             | String | No       | Default: "1.0.0", which version of this specification is in use                                                                            |
| 1     | NFT Project Details | Object | No       | Provide additional context and information about this particular NFT "Collection" for consumption by marketplaces, explorers, and wallets. |

See [CIP25](CIP-25) for a description of a non-fungible token project policy registration.
([CIP25.json](CIP-25/CIP25.json) as an example, [CIP25.schema.json](CIP-25/CIP25.schema.json) for schema documentation).

The information registered here is helpful to aggregator services and marketplaces, it applies equally to
both CIP-25 and CIP-68 metadata standards. A project utilizing one or the other should reference this documentation and
include the relevant information under index #6, prefixed by the number of the CIP (25 or 68) depending upon the
metadata format.

***NFT Project Details Fields***

| index | name                | type     | required | notes                                                                                                                                                                                                                                                                                  |
|-------|---------------------|----------|----------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0     | Collection Name     | String   | Yes      | The "Collection" name that applies specifically to the tokens minted under this policy.                                                                                                                                                                                                |
| 1     | Description         | Array    | No       | An array of strings containing a brief "description" of this project                                                                                                                                                                                                                   |
| 2     | Project Image       | UriArray | No       | An array of strings describing a URI to a "profile image" that may be used for this project.                                                                                                                                                                                           |
| 3     | Project Banner      | UriArray | No       | An array of strings describing a URI to a "banner image" that may be used for this project.                                                                                                                                                                                            |
| 4     | NSFW Flag           | 0 or 1   | No       | "Not Safe for Work" flag. Do the assets within this project contain sensitive material that may not be suitable for all audiences and should potentially be obfuscated or hidden. 0 = no sensitive content, "Safe for Work"; 1 = sensitive content, "Not Safe for Work"                |
| 5     | Social Media        | Array    | No       | A structured array of social media handles for the project. Each entry of the array should be itself an array. The first entry should be a string containing the "name" of the social media platform. The second entry should be an array describing the URI to the social media site. |
| 6     | Project/Artist Name | String   | No       | If this policy is part of a larger project or series from a specific artist or project, this field can be used to contain that name.                                                                                                                                                   |

**CIP-25 Example:**

```cbor 
{
  25: {
    0: "1.0.0",
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
  }
}
```

**CIP-68 Example:**

```cbor 
{
  68: {
    0: "1.0.0",
    1: {
      0: "SpaceBudz v2",
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
      6: "SpaceBudz"
    }
  }
}
```

##### CIP-26: Fungible Tokens / Monetary Policy

`Version: 1.0.0`

***CIP-26 Top-Level Object Fields***

| index | name            | type                   | required | notes                                                                                     |
|-------|-----------------|------------------------|----------|-------------------------------------------------------------------------------------------|
| 0     | Version         | String                 | No       | Default: "1.0.0", which version of this specification is in use                           |
| 1     | Fungible Tokens | Array\<Token Details\> | No       | An array of one or more fungible token registration objects covered by this registration. |

See [CIP26](CIP-26) for a description of a fungible token specific registration ([CIP26.json](CIP-26/CIP26.json) as an
example, [CIP26.schema.json](CIP-26/CIP26.schema.json) for schema documentation). This information can replace the
information currently housed in
the [Cardano Token Registry](https://github.com/cardano-foundation/cardano-token-registry) and is based on the format
currently used in those registrations along with a few additional fields.

Because it is possible that multiple fungible tokens could be minted under a single Policy ID, the format for CIP-26
tokens is slightly different. Here we include an array of fungible token details inside of an array to enable multiple
tokens under the same policy to be registered in a single transaction.

**Example:**

```cbor
{
    867: {
        0: "1.0.0",
        1: {
            6: {
                26: {
                    0: "1.0.0",
                    1: [
                        [...Fungible Token Details...],
                        [...Fungible Token 2 Details...]
                    ]
                }
            }
        },
        2: [...]
    }
}
```

***Token Details Fields***

| index | name                 | type     | required | notes                                                                                                                                                                                                                 |
|-------|----------------------|----------|----------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0     | Subject              | Array    | Yes      | An array identifying the specific token being registered. The first entry should be the hex-encoded Policy ID and the second entry should be the hex-encoded Asset ID of the token.                                   |
| 1     | Token Name           | String   | Yes      | The full "display name" of the token.                                                                                                                                                                                 |
| 2     | Description          | Array    | Yes      | A description for the token. This should be an array of zero or more strings.                                                                                                                                         |
| 3     | Token Ticker         | String   | No       | A short "ticker" identifier for the token. Usually 1 to 5 characters.                                                                                                                                                 |
| 4     | Token Decimals       | UInt     | No       | How many decimal places this token should be treated as having to create a "whole unit". Default is 0. e.g. Lovelace has 6 decimal places                                                                             |
| 5     | Token Website        | UriArray | No       | An array describing the URI to a website for the token.                                                                                                                                                               |
| 6     | Token Image          | UriArray | No       | An array describing the URI to a thumbnail image to be used for the token. Recommended 64px by 64px resolution, transparent background PNG file.                                                                      |
| 7     | Financial Disclosure | Array    | No       | To be used in a *to be written* CIP. This array should provide a URI to a formatted financial disclosure document as well as a SHA256 checksum hash of the file contents.                                             |
| 8     | Beacon Token         | Array    | No       | An array identifying a token to be used as a "beacon token" for the project. Purposes and format TBD. This token would be used as a reference input in smart contracts and provide context and data via inline datum. |

**Example:**

```cbor
{
  26: {
    0: "1.0.0",
    1: [
      {
        0: [
          "d894897411707efa755a76deb66d26dfd50593f2e70863e1661e98a0",
          "7370616365636f696e73"
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
        5: ["https://","spacecoins.io"],
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
          "d894897411707efa755a76deb66d26dfd50593f2e70863e1661e98a0",
          "7370616365636f696e74"
        ]
      }
    ]
  }
}
```

##### CIP-27: Cardano NFT Royalty Information

`Version: 1.0.0`

***CIP-27 Top-Level Object Fields***

| index | name            | type   | required | notes                                                           |
|-------|-----------------|--------|----------|-----------------------------------------------------------------|
| 0     | Version         | String | No       | Default: "1.0.0", which version of this specification is in use |
| 1     | Royalty Details | Object | No       | An object detailing the project royalties as defined in CIP-27  |

***Royalty Details Fields***

| index | name              | type   | required | notes                                                                                                           |
|-------|-------------------|--------|----------|-----------------------------------------------------------------------------------------------------------------|
| 1     | Rate              | String | Yes      | This should be a floating point number between 0.000000 - 1.000000 representing the rate of royalties requested |
| 2     | Recipient Address | Array  | Yes      | This should be an array containing a single address in BECH32 format to be paid royalties                       |
| 3     | Reference Token   | Array  | No       | Not formally part of CIP-27 (as of this writing)                                                                |
| 4     | Datum Format      | *      | No       | Not formally part of CIP-27 (as of this writing)                                                                |

**Notes:**

Two fields are defined here which are not formally part of the CIP-27 specification as of the time of this writing.
A pointer to a "Beacon" or Reference Token that may utilize an inline datum format to inject information into smart
contracts and a Datum Format which would enable marketplaces to pay royalties to a smart contract address allowing for
greater royalty flexibility. Making further argument for the presence or lack thereof of these data points in CIP-27 is
outside the scope of this CIP.

**Example (CBOR):**

```cbor 
{
  27: {
    0: "1.0.0",
    1: {
      1: "0.05",
      2: [
        "addr_test1qqp7uedmne8vjzue66hknx87jspg56qhkm4gp6ahyw7kaahevmtcux",
        "lpy25nqhaljc70094vfu8q4knqyv6668cvwhsq64gt89"
      ],
      3: [
        "d894897411707efa755a76deb66d26dfd50593f2e70863e1661e98a0",
        "7370616365636f696e73"
      ],
      4: {
        0,
        ""
      }
    }
  }
}
```

##### CIP-48: Metadata References Standard

CIP-48 has been proposed to extend on-chain metadata formats to support "references" which could be:

1. Shared/Repeated pieces of content
2. Pointers or References to other on-chain information

CIP-88 could help support the definition and standardization of the reference definitions at a top-level, allowing
references declared within individual token metadata to be easily identified and replaced.

***CIP-48: Top-Level Object Fields***

| index | name              | type   | required | notes                                                          |
|-------|-------------------|--------|----------|----------------------------------------------------------------|
| 0     | Version           | String | No       | Default "1.0.0", which version of this specification is in use |
| 1     | Reference Details | Object | No       | An object detailing CIP-48 references in use                   |

***Reference Details Fields***

| index | name       | type  | required | notes                  |
|-------|------------|-------|----------|------------------------|
| 1     | References | Array | No       | An array of References |

***Reference Fields***

| index | name    | type   | required | notes                                                                                                                 |
|-------|---------|--------|----------|-----------------------------------------------------------------------------------------------------------------------|
| 0     | Name    | String | Yes      | A case sensitive path identifier for this reference                                                                   |
| 1     | Type    | Enum   | Yes      | An enum of accepted types of references which may include direct payloads or pointers to other sources of information |
| 2     | Payload | Object | Yes      | A "Reference Payload" object containing the information to be substituted in place of the reference                   |

**TODO: Expand Support for CIP-48**

##### CIP-60: Music NFT Standard

`Version: 1.0.0`

The author of this CIP lacks a technical understanding of the many informational fields specific to the music industry
which are found in CIP-60. The co-authors of CIP-60 are invited and asked to help in defining which fields may be better
suited to a top-level informational scope.

**TODO: Expand Support for CIP-60**

**Multiple Feature Set Example (CBOR):**

```cbor 
{
  25: {
    0: "1.0.0",
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
    0: "1.0.0",
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

### (Native Scripts)

The Witness Array included in the on-chain metadata should consist of an array of arrays with two elements, the public
key hash of the signing key (as included in the native script) and the signed key witness. If a script requires multiple
signatures, enough signatures to meet the criteria of the script should be included and required for proper validation
of an updated token registration.

The signing payload should be the hex-encoded Token Registration Payload Object.

**Example**

```cbor
[
  [
    h'e97316c52c85eab276fd40feacf78bc5eff74e225e744567140070c3j',
    h'bytestringsignature'
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
    0: "1.0.0",
    1: {
      1: h'00000002df633853f6a47465c9496721d2d5b1291b8398016c0e87ae',
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
          0: "1.0.0",
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
          0: "1.0.0",
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
        h'e97316c52c85eab276fd40feacf78bc5eff74e225e744567140070c3j',
        h'firstWitnessByteString'
      ],
      [
        h'26bacc7b88e2b40701387c521cd0c50d5c0cfa4c6c6d7f0901395757',
        h'secondWitnessByteString'
      ]
    ]
  }
}
```

### Example FT Token Registration Metadata

```cbor
{
  867: {
    0: "1.0.0",
    1: {
      1: h'00000002df633853f6a47465c9496721d2d5b1291b8398016c0e87ae',
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
          0: "1.0.0",
          1: [
            {
              0: [
                "d894897411707efa755a76deb66d26dfd50593f2e70863e1661e98a0",
                "7370616365636f696e73"
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
                "d894897411707efa755a76deb66d26dfd50593f2e70863e1661e98a0",
                "7370616365636f696e74"
              ]
            }
          ]
        }
      }
    },
    2: [
      [
        h'e97316c52c85eab276fd40feacf78bc5eff74e225e744567140070c3j',
        h'witnessByteString'
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

- [ ] This CIP should receive feedback, criticism, and refinement from: CIP Editors and the community of people involved
  with token projects (both NFT and FT) to review any weaknesses or areas of improvement.
- [ ] Guidelines and examples of publication of data as well as discovery and validation should be included as part of
  of criteria for acceptance.
- [ ] Specifications should be updated to be written in both JSON Schema and CBOR CDDL format for maximum compatibility.
- [ ] Implementation and use demonstrated by the community: Token Projects, Blockchain Explorers, Wallets,
  Marketplaces/DEXes.

#### TO-DO ACCEPTANCE ACTIONS ####

- [ ] Convert schema specifications to CDDL format
- [ ] Publish instructions and tooling for publication and verification

### Implementation Plan

1. Publish open source tooling and instructions related to the publication and verification of data utilizing this
   standard.
2. Achieve "buy in" from existing community actors and implementors such as: blockchain explorers, token marketplaces,
   decentralized exchanges, wallets.

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).