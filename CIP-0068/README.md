---
CIP:
Title: Datum Metadata Standard
Authors: Alessandro Konrad <alessandro.konrad@live.de>, Thomas Vellekoop <thomas.vellekoop@iohk.io>
Comments-URI:
Status: Draft
Type: Informational
Created: 2022-07-13
Post-History:
License: CC-BY-4.0
---

## Abstract

This proposal defines a metadata standard making use of output datums not only for NFTs but any asset class.

## Motivation

[CIP-0025](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0025) has plenty of limitations:

- zero programmability
- it is very hard to update/evolve the metadata
- the metadata are not readable from a plutus validator. 

This standard tackles all these problems and offers many more advantages not only for NFTs, but also for any asset class. Additionally, this CIP will introduce a way to classify tokens so that third parties like wallets can easily know what the kind of token it is.

## Considerations

The basic idea is to have two assets issued in the same transaction, where one references the other. We call these two a `reference NFT` and an `user token`, where the `user token` can be an NFT, FT or any other asset class that is transferable and represents any value. So, the `user token` is the actual asset that lives in a user's wallet.

To find the metadata for the `user token` you need to look for the output, where the `reference NFT` is locked in (this is tracable since they are forged in the same transaction). This output contains an inline datum, which holds the metadata. The advantage of this approach is that the issuer of the assets can decide how the transaction output with the `reference NFT` is locked and further handled. If the issuer wants complete immutable metadata, the `reference NFT` can be locked at the address of an unspendable script. Similarly, if the issuer wants the NFTs/FTs to evolve or wants a mechanism to update the metadata, the `reference NFT` can be locked at the address of a script with arbitrary logic that the issuer decides.

Lastly and most importantly, with this construction the metadata can be referenced by a PlutusV2 scripts with the use of reference inputs [CIP-0031](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0031). This will drive further innovation in the token space. 


## Specification

This is the registered `asset_name_label` value

| asset_name_label            | class        | description                                               |
| --------------------------- | ------------ | --------------------------------------------------------- |
| 100                         | NFT          | Reference NFT locked at a script containing the datum     |

The `user token` and `reference NFT` **MUST** be under the same policy id

For a specific `user token` there **MUST** exist exactly **one** `reference NFT`, but there can be multiple `user tokens` referencing the same `reference NFT`

If a specific `user token` has a quantity > 1, then they do all reference the same `reference NFT`

The `user token` and belonging `reference NFT` **MUST** follow a certain pattern. The asset name of boths assets is prefixed with its respective `asset_name_label` followed by a pattern defined by the asset class (e.g. asset_name_label 222)

The datum in the output with the `reference NFT` contains the metadata at the first field of the constructor 0. The version number is at the second field:
```
big_int = int / big_uint / big_nint
big_uint = #6.2(bounded_bytes)
big_nint = #6.3(bounded_bytes)

metadata =
  { * metadata => metadata }
  / [ * metadata ]
  / big_int
  / bounded_bytes
  
version = big_int

datum = #6.121([metadata, version])
```

## 222 NFT Standard

We are introducing two specific token standards in this CIP. Note the possibilities are endless here and more standards can be built on top of this CIP for FTs, other NFTs, semi fungible tokens, etc.


This is the registered `asset_name_label` value

| asset_name_label            | class        | description                                                          |
| --------------------------- | ------------ | -------------------------------------------------------------------- |
| 222                         | NFT          | NFT hold by the user's wallet making use of CIP-0025 inner structure |


### Class

The `user token` is an NFT.


### Pattern

The `user token` and `reference NFT` **MUST** have an identical name followed after the `asset_name_label` prefix.

Example:\
`user token`: `(222)Test123`\
`reference NFT`: `(100)Test123`


### Metadata

This is a low-level representation of the metadata following closely the structure of CIP-0025. All utf-8 encoded keys and values need to be converted into their respective bytes representation when creating the datum on-chain.

```
files_details = 
  {
    name : bounded_bytes, ; utf-8
    mediaType : bounded_bytes, ; utf-8
    src : bounded_bytes ; utf-8
  }

metadata = 
  {
    name : bounded_bytes, ; utf-8
    image : bounded_bytes, ; utf-8
    ? mediaType : bounded_bytes, ; utf-8
    ? description : bounded_bytes, ; utf-8
    ? files : [* files_details]
  }
  
datum = #6.121([metadata, 1]) ; version 1
```
Example datum as JSON:
```json
{"constructor" : 0, "fields": [{"map": [{"k": "6E616D65", "v": "5370616365427564"}, {"k": "696D616765", "v": "697066733A2F2F74657374"}]}, {"int": 1}]}
```

### Retrieve metadata as 3rd party

A third party has the following NFT `d5e6bf0500378d4f0da4e8dde6becec7621cd8cbf5cbb9b87013d4cc.(222)TestToken`:

1. Construct `reference NFT` from `user token`: `d5e6bf0500378d4f0da4e8dde6becec7621cd8cbf5cbb9b87013d4cc.(100)TestToken`
2. Look up `reference NFT` and find the utxo it's locked in.
3. Get the datum from the utxo and lookup metadata by going into the first field of constructor 0.
4. Convert to JSON and encode all string entries to UTF-8 if possible, otherwise leave them in hex.

### Retrieve metadata from a Plutus validator

We want to bring the metadata of the NFT `d5e6bf0500378d4f0da4e8dde6becec7621cd8cbf5cbb9b87013d4cc.(222)TestToken` in the Plutus validator context:

1. Construct `reference NFT` from `user token`: `d5e6bf0500378d4f0da4e8dde6becec7621cd8cbf5cbb9b87013d4cc.(100)TestToken` (off-chain)
2. Look up `reference NFT` and find the utxo it's locked in. (off-chain)
3. Reference the utxo in the transaction. (off-chain)
4. Verify validity of datum of the referenced utxo by checking if policy id of `reference NFT` and `user token` and their asset names without the `asset_name_label` prefix match. (on-chain)

## 333 FT Standard

This is the registered `asset_name_label` value

| asset_name_label            | class        | description                                                          |
| --------------------------- | ------------ | -------------------------------------------------------------------- |
| 333                         | FT           | FT hold by the user's wallet making use of Cardano foundation off-chain registry inner structure |


### Class

The `user token` is an FT (fungible token).


### Pattern

The `user token` and `reference NFT` **MUST** have an identical name followed after the `asset_name_label` prefix.

Example:\
`user token`: `(333)Test123`\
`reference NFT`: `(100)Test123`


### Metadata

This is a low-level representation of the metadata following closely the structure of the Cardano foundation off-chain metadata registry. All utf-8 encoded keys and values need to be converted into their respective bytes representation when creating the datum on-chain.

```
; Explanation here: https://developers.cardano.org/docs/native-tokens/token-registry/cardano-token-registry/

metadata = 
  {
    name : bounded_bytes, ; utf-8
    description : bounded_bytes, ; utf-8
    ? ticker: bounded_bytes, ; utf-8
    ? url: bounded_bytes, ; utf-8
    ? logo: bounded_bytes, ; utf-8
    ? decimals: big_int
  }
  
datum = #6.121([metadata, 1]) ; version 1
```
Example datum as JSON:
```json
{"constructor" : 0, "fields": [{"map": [{"k": "6E616D65", "v": "5370616365427564"}, {"k": "6465736372697074696F6E", "v": "54686973206973206D79207465737420746F6B656E"}]}, {"int": 1}]}
```

### Retrieve metadata as 3rd party

A third party has the following FT `d5e6bf0500378d4f0da4e8dde6becec7621cd8cbf5cbb9b87013d4cc.(333)TestToken`:

1. Construct `reference NFT` from `user token`: `d5e6bf0500378d4f0da4e8dde6becec7621cd8cbf5cbb9b87013d4cc.(100)TestToken`
2. Look up `reference NFT` and find the utxo it's locked in.
3. Get the datum from the utxo and lookup metadata by going into the first field of constructor 0.
4. Convert to JSON and encode all string entries to UTF-8 if possible, otherwise leave them in hex.

### Retrieve metadata from a Plutus validator

We want to bring the metadata of the FT `d5e6bf0500378d4f0da4e8dde6becec7621cd8cbf5cbb9b87013d4cc.(333)TestToken` in the Plutus validator context:

1. Construct `reference NFT` from `user token`: `d5e6bf0500378d4f0da4e8dde6becec7621cd8cbf5cbb9b87013d4cc.(100)TestToken` (off-chain)
2. Look up `reference NFT` and find the utxo it's locked in. (off-chain)
3. Reference the utxo in the transaction. (off-chain)
4. Verify validity of datum of the referenced utxo by checking if policy id of `reference NFT` and `user token` and their asset names without the `asset_name_label` prefix match. (on-chain)

## Backward Compatibility

To keep metadata compatibility with changes coming in the future, we introduce a `version` field in the datum.

## References

- CIP-0025: https://github.com/cardano-foundation/CIPs/blob/master/CIP-0025
- CIP-0031: https://github.com/cardano-foundation/CIPs/tree/master/CIP-0031

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).