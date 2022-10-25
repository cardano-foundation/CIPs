---
CIP: 68
Title: Datum Metadata Standard
Authors: Alessandro Konrad <alessandro.konrad@live.de>, Thomas Vellekoop <thomas.vellekoop@iohk.io>
Comments-URI:
Status: Proposed
Type: Informational
Created: 2022-07-13
Post-History:
License: CC-BY-4.0
---

## Abstract

This proposal defines a metadata standard for native assets making use of output datums not only for NFTs but any asset class.

## Motivation

This proposal addresses a few shortcomings of [CIP-0025](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0025):

- Lack of programmability;
- Difficult metadata update / evolution;
- Non-inspectable metadata from within Plutus validators...

Besides these shortcomings CIP-0025 has some [flaws](https://github.com/cardano-foundation/CIPs/pull/85#issuecomment-1054123645) in its design.
For people unaware of CIP-0025 or want to use a different way of minting or want to use a different metadata format/mechanism you open up a protocol to metadata spoofing, because this standard is so established and metadata in minting transactions are interpreted by most platforms by default. Since this standard is not enforced at the protocol level there is no guarantee everyone will be aware of it or follow the rules. At the same time you limit and constraint the capabilities of the ledger if everyone was forced to follow the rules of CIP-0025. 

This standard tackles all these problems and offers many more advantages, not only for NFTs, but also for any asset class that may follow. Additionally, this CIP will introduce a way to classify tokens so that third parties like wallets can easily know what the kind of token it is.


## Specification

### Considerations

The basic idea is to have two assets issued, where one references the other. We call these two a `reference NFT` and an `user token`, where the `user token` can be an NFT, FT or any other asset class that is transferable and represents any value. So, the `user token` is the actual asset that lives in a user's wallet.

To find the metadata for the `user token` you need to look for the output, where the `reference NFT` is locked in. How this is done concretely will become clear below. Moreover, this output contains a datum, which holds the metadata. The advantage of this approach is that the issuer of the assets can decide how the transaction output with the `reference NFT` is locked and further handled. If the issuer wants complete immutable metadata, the `reference NFT` can be locked at the address of an unspendable script. Similarly, if the issuer wants the NFTs/FTs to evolve or wants a mechanism to update the metadata, the `reference NFT` can be locked at the address of a script with arbitrary logic that the issuer decides.

Lastly and most importantly, with this construction, the metadata can be used by a PlutusV2 script with the use of reference inputs [CIP-0031](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0031). This will drive further innovation in the token space. 

### Reference NFT label

This is the registered `asset_name_label` value

| asset_name_label            | class        | description                                               |
| --------------------------- | ------------ | --------------------------------------------------------- |
| 100                         | NFT          | Reference NFT locked at a script containing the datum     |

### Constraints and conditions

For a correct relationship between the `user token` and the `reference NFT` a few conditions **must** be met.
- The `user token` and `reference NFT` **must** be under the same policy ID. 
- For a specific `user token` there **must** exist exactly **one** `reference NFT`
- The `user token` and associated `reference NFT` **must** follow the standard naming pattern. The asset name of both assets is prefixed with its respective `asset_name_label` followed by a pattern defined by the asset class (e.g. asset_name_label 222)

Some remarks about the above,
1. The `user token` and `reference NFT` do not need to be minted in the same transaction. The order of minting is also not important.
2. It may be the case that there can be multiple `user tokens` (multiple asset names or quantity greater than 1) referencing the same `reference NFT`.

The datum in the output with the `reference NFT` contains the metadata at the first field of the constructor 0. The version number is at the second field of this constructor:
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

datum = #6.121([metadata, version])
```

## 222 NFT Standard

Besides the necessary standard for the `reference NFT` we're introducing two specific token standards in this CIP. Note that the possibilities are endless here and more standards can be built on top of this CIP for FTs, other NFTs, semi fungible tokens, etc. The first is the `222` NFT standard with the registered `asset_name_label` prefix value

| asset_name_label            | class        | description                                                          |
| --------------------------- | ------------ | -------------------------------------------------------------------- |
| 222                         | NFT          | NFT hold by the user's wallet making use of CIP-0025 inner structure |


### Class

The `user token` represents an NFT (non-fungible token).

### Pattern

The `user token` and `reference NFT` **must** have an identical name, preceded by the `asset_name_label` prefix.

Example:\
`user token`: `(222)Test123`\
`reference NFT`: `(100)Test123`


### Metadata

This is a low-level representation of the metadata, following closely the structure of CIP-0025. All UTF-8 encoded keys and values need to be converted into their respective byte's representation when creating the datum on-chain.

```
files_details = 
  {
    ? name : bounded_bytes, ; UTF-8
    mediaType : bounded_bytes, ; UTF-8
    src : bounded_bytes ; UTF-8
  }

metadata = 
  {
    name : bounded_bytes, ; UTF-8
    image : bounded_bytes, ; UTF-8
    ? mediaType : bounded_bytes, ; UTF-8
    ? description : bounded_bytes, ; UTF-8
    ? files : [* files_details]
  }
  
datum = #6.121([metadata, 1]) ; version 1
```
Example datum as JSON:
```json
{"constructor" : 0, "fields": [{"map": [{"k": "6E616D65", "v": "5370616365427564"}, {"k": "696D616765", "v": "697066733A2F2F74657374"}]}, {"int": 1}]}
```

### Retrieve metadata as 3rd party

A third party has the following NFT `d5e6bf0500378d4f0da4e8dde6becec7621cd8cbf5cbb9b87013d4cc.(222)TestToken` they want to lookup. The steps are

1. Construct `reference NFT` from `user token`: `d5e6bf0500378d4f0da4e8dde6becec7621cd8cbf5cbb9b87013d4cc.(100)TestToken`
2. Look up `reference NFT` and find the output it's locked in.
3. Get the datum from the output and lookup metadata by going into the first field of constructor 0.
4. Convert to JSON and encode all string entries to UTF-8 if possible, otherwise leave them in hex.

### Retrieve metadata from a Plutus validator

We want to bring the metadata of the NFT `d5e6bf0500378d4f0da4e8dde6becec7621cd8cbf5cbb9b87013d4cc.(222)TestToken` in the Plutus validator context. To do this we

1. Construct `reference NFT` from `user token`: `d5e6bf0500378d4f0da4e8dde6becec7621cd8cbf5cbb9b87013d4cc.(100)TestToken` (off-chain)
2. Look up `reference NFT` and find the output it's locked in. (off-chain)
3. Reference the output in the transaction. (off-chain)
4. Verify validity of datum of the referenced output by checking if policy ID of `reference NFT` and `user token` and their asset names without the `asset_name_label` prefix match. (on-chain)

## 333 FT Standard

The second introduced standard is the `333` FT standard with the registered `asset_name_label` prefix value

| asset_name_label            | class        | description                                                          |
| --------------------------- | ------------ | -------------------------------------------------------------------- |
| 333                         | FT           | FT hold by the user's wallet making use of Cardano foundation off-chain registry inner structure |


### Class

The `user token` is an FT (fungible token).


### Pattern

The `user token` and `reference NFT` **must** have an identical name, preceded by the `asset_name_label` prefix.

Example:\
`user token`: `(333)Test123`\
`reference NFT`: `(100)Test123`


### Metadata

This is a low-level representation of the metadata, following closely the structure of the Cardano foundation off-chain metadata registry. All UTF-8 encoded keys and values need to be converted into their respective byte's representation when creating the datum on-chain.

```
; Explanation here: https://developers.cardano.org/docs/native-tokens/token-registry/cardano-token-registry/

metadata = 
  {
    name : bounded_bytes, ; UTF-8
    description : bounded_bytes, ; UTF-8
    ? ticker: bounded_bytes, ; UTF-8
    ? url: bounded_bytes, ; UTF-8
    ? logo: uri,
    ? decimals: int
  }

; A URI as a UTF-8 encoded bytestring.
; The URI scheme must be one of `https`, `ipfs` or `data`
; Do not encode plain file payloads as URI.
; 'logo' does not follow the explanation of the token-registry, it needs to be a valid URI and not a plain bytestring.
; Only use the following media types: `image/png`, `image/jpeg`, `image/svg+xml`
uri = bounded_bytes 
  
datum = #6.121([metadata, 1]) ; version 1
```
Example datum as JSON:
```json
{"constructor" : 0, "fields": [{"map": [{"k": "6E616D65", "v": "5370616365427564"}, {"k": "6465736372697074696F6E", "v": "54686973206973206D79207465737420746F6B656E"}]}, {"int": 1}]}
```

### Retrieve metadata as 3rd party

A third party has the following FT `d5e6bf0500378d4f0da4e8dde6becec7621cd8cbf5cbb9b87013d4cc.(333)TestToken` they want to lookup. The steps are

1. Construct `reference NFT` from `user token`: `d5e6bf0500378d4f0da4e8dde6becec7621cd8cbf5cbb9b87013d4cc.(100)TestToken`
2. Look up `reference NFT` and find the output it's locked in.
3. Get the datum from the output and lookup metadata by going into the first field of constructor 0.
4. Convert to JSON and encode all string entries to UTF-8 if possible, otherwise leave them in hex.

### Retrieve metadata from a Plutus validator

We want to bring the metadata of the FT `d5e6bf0500378d4f0da4e8dde6becec7621cd8cbf5cbb9b87013d4cc.(333)TestToken` in the Plutus validator context. To do this we 

1. Construct `reference NFT` from `user token`: `d5e6bf0500378d4f0da4e8dde6becec7621cd8cbf5cbb9b87013d4cc.(100)TestToken` (off-chain)
2. Look up `reference NFT` and find the output it's locked in. (off-chain)
3. Reference the output in the transaction. (off-chain)
4. Verify validity of datum of the referenced output by checking if policy ID of `reference NFT` and `user token` and their asset names without the `asset_name_label` prefix match. (on-chain)

## Rationale

Without seperation of `reference NFT` and `user token` you lose all flexibility and moving the `user token` would be quite cumbersome as you would need to add the metadata everytime to the new output where the `user token` is sent to. Hence you separate metadata and `user token` and lock the metadata inside another UTxO, so you can freely move the `user token` around.

In order to reference the correct UTxO containing the metadata, it needs to be authenticated, otherwise metadata spoofing attacks become possible. One way to achieve that is by adding an NFT (`reference NFT`) to the UTxO. This NFT needs to under the same Policy ID as the `user token`, followed by an asset name pattern defined in the standard. This way you create a secure link between `reference NFT` and `user token` without the need for any extra data and you can make use of this off-chain and on-chain. 

The security for the link is derived from the minting policy itself, so it's important to write the validator with the right constraints and rules since this CIP solely defines the interface to keep flexibility as high as possible.


## Backward Compatibility

To keep metadata compatibility with changes coming in the future, we introduce a `version` field in the datum.


## Path to Active

- Agree on a binary encoding for asset name labels in [CIP-0067](https://github.com/cardano-foundation/CIPs/pull/298).
- Get support for this CIP by wallets, explorers, tools, minting platforms and other 3rd parties.
- Minimal reference implementation making use of [Lucid](https://github.com/spacebudz/lucid) (off-chain), [PlutusTx](https://github.com/input-output-hk/plutus) (on-chain):
[Implementation](./ref_impl/)
- Open-source more practical implementations/projects which make use of this CIP.


## References

- CIP-0025: https://github.com/cardano-foundation/CIPs/blob/master/CIP-0025
- CIP-0031: https://github.com/cardano-foundation/CIPs/tree/master/CIP-0031

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).

