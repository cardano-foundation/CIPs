---
CIP: 68
Title: Datum Metadata Standard
Status: Active
Category: Tokens
Authors:
  - Alessandro Konrad <alessandro.konrad@live.de>
  - Thomas Vellekoop <thomas.vellekoop@iohk.io>
Implementors:
  - Alessandro Konrad (SpaceBudz)
  - 5Binaries (Blockfrost)
  - Smaug (Pool.pm)
Discussions:
  - https://github.com/cardano-foundation/CIPs/pull/299
  - https://github.com/cardano-foundation/CIPs/pull/359
  - https://github.com/cardano-foundation/CIPs/pull/458
  - https://github.com/cardano-foundation/CIPs/pull/471
  - https://github.com/cardano-foundation/CIPs/pull/494
  - https://github.com/cardano-foundation/CIPs/issues/520
  - https://github.com/cardano-foundation/CIPs/pull/586
Created: 2022-07-13
License: CC-BY-4.0
---

## Abstract

This proposal defines a metadata standard for native assets making use of output datums not only for NFTs but any asset
class.

## Motivation: why is this CIP necessary?

This proposal addresses a few shortcomings
of [CIP-0025](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0025):

- Lack of programmability;
- Difficult metadata update / evolution;
- Non-inspectable metadata from within Plutus validators

Besides these shortcomings CIP-0025 has
some [flaws](https://github.com/cardano-foundation/CIPs/pull/85#issuecomment-1054123645) in its design.
For people unaware of CIP-0025 or want to use a different way of minting or want to use a different metadata
format/mechanism you open up a protocol to metadata spoofing, because this standard is so established and metadata in
minting transactions are interpreted by most platforms by default. Since this standard is not enforced at the protocol
level there is no guarantee everyone will be aware of it or follow the rules. At the same time you limit and constraint
the capabilities of the ledger if everyone was forced to follow the rules of CIP-0025.

This standard tackles all these problems and offers many more advantages, not only for NFTs, but also for any asset
class that may follow. Additionally, this CIP will introduce a way to classify tokens so that third parties like wallets
can easily know what the kind of token it is.

## Specification

### Considerations

The basic idea is to have two assets issued, where one references the other. We call these two a `reference NFT` and
an `user token`, where the `user token` can be an NFT, FT or any other asset class that is transferable and represents
any value. So, the `user token` is the actual asset that lives in a user's wallet.

To find the metadata for the `user token` you need to look for the output, where the `reference NFT` is locked in. How
this is done concretely will become clear below. Moreover, this output contains a datum, which holds the metadata. The
advantage of this approach is that the issuer of the assets can decide how the transaction output with
the `reference NFT` is locked and further handled. If the issuer wants complete immutable metadata, the `reference NFT`
can be locked at the address of an unspendable script. Similarly, if the issuer wants the NFTs/FTs to evolve or wants a
mechanism to update the metadata, the `reference NFT` can be locked at the address of a script with arbitrary logic that
the issuer decides.

Lastly and most importantly, with this construction, the metadata can be used by a Plutus V2 script with the use of
reference inputs [CIP-0031](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0031). This will drive further
innovation in the token space.

### Labels

Each asset name must be prefixed by a label. The intent of this label is to identify the purpose of the token. For
example, a reference NFT is identified by the label 100 and so every token considered a reference NFT should start its
asset name with the hex `000643b0`. This is
following [CIP-0067](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0067), which specifies how the label
prefix should be formatted.

Examples of asset names:

| asset_name_label | asset_name_content | resulting_label_hex | resulting_content_hex | resulting_asset_name_hex     |
|------------------|--------------------|---------------------|-----------------------|------------------------------|
| 100              | GenToken           | 000643b0            | 47656e546f6b656e      | 000643b047656e546f6b656e     |
| 100              | NeverGonna         | 000643b0            | 4e65766572476f6e6e61  | 000643b04e65766572476f6e6e61 |
| 222              | GiveYouUp          | 000de140            | 47697665596f755570    | 000de14047697665596f755570   |

For simplicity purposes, the document will use the label `(100)` or `(<label>)` in the following documentation, but
understand it should follow the CIP-0067 specification.

### Reference NFT label

This is the registered `asset_name_label` value

| asset_name_label | class | description                                           |
|------------------|-------|-------------------------------------------------------|
| 100              | NFT   | Reference NFT locked at a script containing the datum |

### Constraints and conditions

For a correct relationship between the `user token` and the `reference NFT` a few conditions MUST be met.

- The `user token` and `reference NFT` MUST be under the same policy ID.
- For a specific `user token` there MUST exist exactly **one** `reference NFT`
- The `user token` and associated `reference NFT` MUST follow the standard naming pattern. The asset name of both assets
  is prefixed with its respective `asset_name_label` followed by a pattern defined by the asset class (e.g.
  asset_name_label 222)

Some remarks about the above,

1. The `user token` and `reference NFT` do not need to be minted in the same transaction. The order of minting is also
   not important.
2. It may be the case that there can be multiple `user tokens` (multiple asset names or quantity greater than 1)
   referencing the same `reference NFT`.

The datum in the output with the `reference NFT` contains the metadata at the first field of the constructor 0. The
version number is at the second field of this constructor. The third field allows for arbitrary plutus data. This could
be useful to forward relevant data to the plutus script:

```
big_int = int / big_uint / big_nint
big_uint = #6.2(bounded_bytes)
big_nint = #6.3(bounded_bytes)

metadata =
  { * metadata => metadata }
  / [ * metadata ]
  / big_int
  / bounded_bytes

version = int

; Custom user defined plutus data.
; Setting data is optional, but the field is required
; and needs to be at least Unit/Void: #6.121([])
extra = plutus_data

datum = #6.121([metadata, version, extra])
```

#### 222 NFT Standard

> **Note** Since `version >= 1`

Besides the necessary standard for the `reference NFT` we're introducing three specific token standards in this CIP.
Note that the possibilities are endless here and more standards can be built on top of this CIP for FTs, other NFTs,
rich fungible tokens, etc. The first is the `222` NFT standard with the registered `asset_name_label` prefix value

| asset_name_label | class | description                                                          |
|------------------|-------|----------------------------------------------------------------------|
| 222              | NFT   | NFT held by the user's wallet making use of CIP-0025 inner structure |

##### Class

The `user token` represents an NFT (non-fungible token).

##### Pattern

The `user token` and `reference NFT` MUST have an identical name, preceded by the `asset_name_label` prefix.

Example:\
`user token`: `(222)Test123`\
`reference NFT`: `(100)Test123`

##### Metadata

This is a low-level representation of the metadata, following closely the structure of CIP-0025. All UTF-8 encoded keys
and values need to be converted into their respective byte's representation when creating the datum on-chain.

```
files_details =
  {
    ? name : bounded_bytes, ; UTF-8
    mediaType : bounded_bytes, ; UTF-8
    src : uri,
    ; ... Additional properties are allowed
  }

metadata =
  {
    name : bounded_bytes, ; UTF-8

    ; The image URI must point to a resource with media type (mime type) `image/*`
    ; (for example `image/png`, `image/jpeg`, `image/svg+xml`, etc.)
    image : uri,

    ? description : bounded_bytes, ; UTF-8
    ? files : [* files_details]
    ; ... Additional properties are allowed
  }

; A valid Uniform Resource Identifier (URI) as a UTF-8 encoded bytestring.
; The URI scheme must be one of `https` (HTTP), `ipfs` (IPFS), `ar` (Arweave) or `data` (on-chain).
; Data URLs (on-chain data) must comply to RFC2397.
uri = bounded_bytes / [ * bounded_bytes ] ; UTF-8
  
; Custom user defined plutus data.
; Setting data is optional, but the field is required
; and needs to be at least Unit/Void: #6.121([])
extra = plutus_data

datum = #6.121([metadata, version, extra])

version = 1 / 2 / 3
```

Example datum as JSON:

```json
{
  "constructor": 0,
  "fields": [
    {
      "map": [
        {
          "k": {
            "bytes": "6E616D65"
          },
          "v": {
            "bytes": "5370616365427564"
          }
        },
        {
          "k": {
            "bytes": "696D616765"
          },
          "v": {
            "bytes": "697066733A2F2F74657374"
          }
        }
      ]
    },
    {
      "int": 1
    }
  ]
}
```

##### Retrieve metadata as 3rd party

A third party has the following NFT `d5e6bf0500378d4f0da4e8dde6becec7621cd8cbf5cbb9b87013d4cc.(222)TestToken` they want
to lookup. The steps are

1. Construct `reference NFT` from `user token`: `d5e6bf0500378d4f0da4e8dde6becec7621cd8cbf5cbb9b87013d4cc.(100)TestToken`
2. Look up `reference NFT` and find the output it's locked in.
3. Get the datum from the output and lookup metadata by going into the first field of constructor 0.
4. Convert to JSON and encode all string entries to UTF-8 if possible, otherwise leave them in hex.

##### Retrieve metadata from a Plutus validator

We want to bring the metadata of the NFT `d5e6bf0500378d4f0da4e8dde6becec7621cd8cbf5cbb9b87013d4cc.(222)TestToken` in
the Plutus validator context. To do this we

1. Construct `reference NFT`
   from `user token`: `d5e6bf0500378d4f0da4e8dde6becec7621cd8cbf5cbb9b87013d4cc.(100)TestToken` (off-chain)
2. Look up `reference NFT` and find the output it's locked in. (off-chain)
3. Reference the output in the transaction. (off-chain)
4. Verify validity of datum of the referenced output by checking if policy ID of `reference NFT` and `user token` and
   their asset names without the `asset_name_label` prefix match. (on-chain)

#### 333 FT Standard

> **Note** Since `version >= 1`

The second introduced standard is the `333` FT standard with the registered `asset_name_label` prefix value

| asset_name_label | class | description                                                                                      |
|------------------|-------|--------------------------------------------------------------------------------------------------|
| 333              | FT    | FT hold by the user's wallet making use of Cardano foundation off-chain registry inner structure |

##### Class

The `user token` is an FT (fungible token).

##### Pattern

The `user token` and `reference NFT` MUST have an identical name, preceded by the `asset_name_label` prefix.

Example:\
`user token`: `(333)Test123`\
`reference NFT`: `(100)Test123`

##### Metadata

This is a low-level representation of the metadata, following closely the structure of the Cardano foundation off-chain
metadata registry. All UTF-8 encoded keys and values need to be converted into their respective byte's representation
when creating the datum on-chain.

```
; Explanation here: https://developers.cardano.org/docs/native-tokens/token-registry/cardano-token-registry/

metadata =
  {
    name : bounded_bytes, ; UTF-8
    description : bounded_bytes, ; UTF-8
    ? ticker: bounded_bytes, ; UTF-8
    ? url: bounded_bytes, ; UTF-8
    ? decimals: int

    ; 'logo' does not follow the explanation of the token-registry, it needs to be a valid URI and not a plain bytestring.
    ; The logo URI must point to a resource with media type (mime type) `image/png`, `image/jpeg` or `image/svg+xml`.
    ? logo: uri,

    ; ... Additional properties are allowed
  }

; A valid Uniform Resource Identifier (URI) as a UTF-8 encoded bytestring.
; The URI scheme must be one of `https` (HTTP), `ipfs` (IPFS), `ar` (Arweave) or `data` (on-chain).
; Data URLs (on-chain data) must comply to RFC2397.
uri = bounded_bytes / [ * bounded_bytes ] ; UTF-8

; Custom user defined plutus data.
; Setting data is optional, but the field is required
; and needs to be at least Unit/Void: #6.121([])
extra = plutus_data

datum = #6.121([metadata, version, extra])

version = 1 / 2 / 3
```

Example datum as JSON:

```json
{
  "constructor": 0,
  "fields": [
    {
      "map": [
        {
          "k": {
            "bytes": "6E616D65"
          },
          "v": {
            "bytes": "5370616365427564"
          }
        },
        {
          "k": {
            "bytes": "6465736372697074696F6E"
          },
          "v": {
            "bytes": "54686973206973206D79207465737420746F6B656E"
          }
        }
      ]
    },
    {
      "int": 1
    }
  ]
}
```

##### Retrieve metadata as 3rd party

A third party has the following FT `d5e6bf0500378d4f0da4e8dde6becec7621cd8cbf5cbb9b87013d4cc.(333)TestToken` they want
to lookup. The steps are

1. Construct `reference NFT` from `user token`: `d5e6bf0500378d4f0da4e8dde6becec7621cd8cbf5cbb9b87013d4cc.(100)TestToken`
2. Look up `reference NFT` and find the output it's locked in.
3. Get the datum from the output and lookup metadata by going into the first field of constructor 0.
4. Convert to JSON and encode all string entries to UTF-8 if possible, otherwise leave them in hex.

##### Retrieve metadata from a Plutus validator

We want to bring the metadata of the FT `d5e6bf0500378d4f0da4e8dde6becec7621cd8cbf5cbb9b87013d4cc.(333)TestToken` in the
Plutus validator context. To do this we

1. Construct `reference NFT`
   from `user token`: `d5e6bf0500378d4f0da4e8dde6becec7621cd8cbf5cbb9b87013d4cc.(100)TestToken` (off-chain)
2. Look up `reference NFT` and find the output it's locked in. (off-chain)
3. Reference the output in the transaction. (off-chain)
4. Verify validity of datum of the referenced output by checking if policy ID of `reference NFT` and `user token` and
   their asset names without the `asset_name_label` prefix match. (on-chain)

#### 444 RFT Standard

> **Warning** Since `version >= 2`

The third introduced standard is the `444` Rich-FT standard with the registered `asset_name_label` prefix value

| asset_name_label | class | description                                                                                                                                     |
|------------------|-------|-------------------------------------------------------------------------------------------------------------------------------------------------|
| 444              | RFT   | RFT hold by the user's wallet making use of the union of CIP-0025 inner structure AND the Cardano foundation off-chain registry inner structure |

Rich-Fungible tokens don't fit cleanly into the other two FT/NFT classes of tokens and thus need their own standard. An
example of an RFT would be a fractionalized NFT. The single reference NFT `(100)` represents the NFT itself, and the
many `(444)` tokens represent the fractionalized shares. Minting 100 tokens and setting decimals to 2 would represent a
single NFT that is split into 100 fractions.

##### Class

The `user token` is an RFT (rich-fungible token).

##### Pattern

The `user token` and `reference NFT` MUST have an identical name, preceded by the `asset_name_label` prefix.

Example:\
`user token`: `(444)Test123`\
`reference NFT`: `(100)Test123`

##### Metadata

This is a low-level representation of the metadata, following closely the structure of CIP-0025 with the optional
decimals field added. All UTF-8 encoded keys and values need to be converted into their respective byte's representation
when creating the datum on-chain.

```
files_details =
  {
    ? name : bounded_bytes, ; UTF-8
    mediaType : bounded_bytes, ; UTF-8
    src : uri,
    ; ... Additional properties are allowed
  }

metadata =
  {
    name : bounded_bytes, ; UTF-8

    ; The image URI must point to a resource with media type (mime type) `image/*`
    ; (for example `image/png`, `image/jpeg`, `image/svg+xml`, etc.)
    image : uri,

    ? description : bounded_bytes, ; UTF-8
    ? decimals: int,
    ? files : [* files_details]
    ; ... Additional properties are allowed
  }

; A valid Uniform Resource Identifier (URI) as a UTF-8 encoded bytestring.
; The URI scheme must be one of `https` (HTTP), `ipfs` (IPFS), `ar` (Arweave) or `data` (on-chain).
; Data URLs (on-chain data) must comply to RFC2397.
uri = bounded_bytes ; UTF-8

; Custom user defined plutus data.
; Setting data is optional, but the field is required
; and needs to be at least Unit/Void: #6.121([])
extra = plutus_data

datum = #6.121([metadata, version, extra])

version = 3
```

Example datum as JSON:

```json
{
  "constructor": 0,
  "fields": [
    {
      "map": [
        {
          "k": {
            "bytes": "6E616D65"
          },
          "v": {
            "bytes": "5370616365427564"
          }
        },
        {
          "k": {
            "bytes": "6465736372697074696F6E"
          },
          "v": {
            "bytes": "54686973206973206D79207465737420746F6B656E"
          }
        },
        {
          "k": {
            "bytes": "696D616765"
          },
          "v": {
            "bytes": "697066733A2F2F74657374"
          }
        },
        {
          "k": {
            "bytes": "646563696D616C73"
          },
          "v": {
            "int": 2
          }
        }
      ]
    },
    {
      "int": 1
    }
  ]
}
```

##### Retrieve metadata as 3rd party

A third party has the following RFT `d5e6bf0500378d4f0da4e8dde6becec7621cd8cbf5cbb9b87013d4cc.(444)TestToken` they want
to lookup. The steps are

1. Construct `reference NFT` from `user token`: `d5e6bf0500378d4f0da4e8dde6becec7621cd8cbf5cbb9b87013d4cc.(100)TestToken`
2. Look up `reference NFT` and find the output it's locked in.
3. Get the datum from the output and lookup metadata by going into the first field of constructor 0.
4. Convert to JSON and encode all string entries to UTF-8 if possible, otherwise leave them in hex.

##### Retrieve metadata from a Plutus validator

We want to bring the metadata of the RFT `d5e6bf0500378d4f0da4e8dde6becec7621cd8cbf5cbb9b87013d4cc.(444)TestToken` in
the Plutus validator context. To do this we

1. Construct `reference NFT`
   from `user token`: `d5e6bf0500378d4f0da4e8dde6becec7621cd8cbf5cbb9b87013d4cc.(100)TestToken` (off-chain)
2. Look up `reference NFT` and find the output it's locked in. (off-chain)
3. Reference the output in the transaction. (off-chain)
4. Verify validity of datum of the referenced output by checking if policy ID of `reference NFT` and `user token` and
   their asset names without the `asset_name_label` prefix match. (on-chain)

### Extending & Modifying this CIP

> The keywords "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL
> NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED",  "MAY", and
> "OPTIONAL" in this section are to be interpreted as described in
> [RFC 2119](https://datatracker.ietf.org/doc/html/rfc2119).

All CIPs proposing to modify or extend this standard **MUST** include the language or a reference link to the extension
and modification language found in the 
[Extension Boilerplate](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0068/extension_boilerplate.md).

In order to prevent conflicting updates in the future; the addition of new asset classes following, or as part of, this
standard **MUST** be submitted as a new CIP providing their own justification, implementation, rationale, and community
review prior to official acceptance. Newly proposed `asset_name_labels` **SHOULD NOT** be added to
[CIP-0067](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0067) until the accompanying CIP has matured
through the community review and feedback stage to a point that it is considered in the `Under Review` status and is
assigned a tentative CIP number by the CIP Editors panel.

A brief reference to new asset classes **MAY** be added to this document after the accompanying CIP achieves
the `accepted` status. Documentation describing these token asset classes **MUST** be fully encapsulated within their
individual CIPs and a link **MUST** be provided to that CIP within this document.

If a modification or change is deemed necessary to one of the asset classes contained within this document: namely Asset
Name Labels: 100, 222, 333, or 444; which do not fundamentally change the nature, use, or reference of the tokens; it
**MAY** be made as a modification of this document. However, any change proposed that presents a non-backwards
compatible change **MUST** include an accompanying `version` field iteration and both specifications for the proposed,
current, and historical versions of the format **MUST** be maintained to assist future implementors who may encounter a
version of these tokens from any point in time with the following format:

```
#### Versions

1. [6d897eb](https://github.com/cardano-foundation/CIPs/tree/6d897eb60805a58a3e54821fe61284d5c5903764/CIP-XXXX)
2. [45fa23b](https://github.com/cardano-foundation/CIPs/tree/45fa23b60806367a3e52231e552c4d7654237678/CIP-XXXX)
3. [bfc6fde](https://github.com/cardano-foundation/CIPs/tree/bfc6fde340280d8b51f5a7131b57f4cc6cc5f260/CIP-XXXX)
4. **Current**
```

Each time a new version is introduced the previous version's link MUST be updated to match the last commit corresponding
to the previous version.

If a change is proposed that would fundamentally alter the nature of one or more of the `asset_name_labels` and their
associated tokens contained within this document, namely Asset Name Labels: 100, 222, 333, or 444; these changes
**MUST** be submitted via a new, separate CIP with its own justification, implementation, rationale, and community
review prior to official acceptance. These separate CIPs **MUST** include a plan for the obsolescence of any previous
versions of the affected tokens. `asset_name_labels` **MUST** only be marked obsolete once a modifying CIP achieves the
`accepted` status.

### Changelog

#### version 1

- NFT (222) & FT (333) asset classes

#### version 2

- Added new RFT asset class (444)

#### version 3

- Added [* bounded_bytes] support to the image and src tags on the metadata 

## Rationale: how does this CIP achieve its goals?

Without separation of `reference NFT` and `user token` you lose all flexibility and moving the `user token` would be
quite cumbersome as you would need to add the metadata everytime to the new output where the `user token` is sent to.
Hence, you separate metadata and `user token` and lock the metadata inside another UTxO, so you can freely move
the `user token` around.

In order to reference the correct UTxO containing the metadata, it needs to be authenticated, otherwise metadata
spoofing attacks become possible. One way to achieve that is by adding an NFT (`reference NFT`) to the UTxO. This NFT
needs to under the same Policy ID as the `user token`, followed by an asset name pattern defined in the standard. This
way you create a secure link between `reference NFT` and `user token` without the need for any extra data, and you can
make use of this off-chain and on-chain.

The security for the link is derived from the minting policy itself, so it's important to write the validator with the
right constraints and rules since this CIP solely defines the interface to keep flexibility as high as possible.

### Backward Compatibility

To keep metadata compatibility with changes coming in the future, we introduce a `version` field in the datum.

## Path to Active

### Acceptance Criteria

- [X] Open-source more practical implementations/projects which make use of this CIP.
- [X] Introduce a `version` integer datum field to increment for new asset classes or
changes to the on-chain format.

### Implementation Plan

- [X] Agree on a binary encoding for asset name labels
  in [CIP-0067](https://github.com/cardano-foundation/CIPs/pull/298).
- [X] Get support for this CIP by wallets, explorers, tools, minting platforms and other 3rd parties.
- [X] Minimal reference implementation making use of [Lucid](https://github.com/spacebudz/lucid) (
  off-chain), [PlutusTx](https://github.com/input-output-hk/plutus) (on-chain): [Implementation](./ref_impl)

## References

- [CIP 25 - Media NFT Metadata Standard](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0025)
- [CIP 31 - Reference inputs](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0031)
- [CIP 67 - Asset Name Label Registry](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0067)
- [RFC 3986 - Uniform Resource Identifier (URI)](https://www.rfc-editor.org/rfc/rfc3986)
- [RFC 2397 - The "data" URL scheme](https://datatracker.ietf.org/doc/html/rfc2397)

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
