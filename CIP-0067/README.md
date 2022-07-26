---
CIP:
Title: Asset Name Label Registry
Authors: Alessandro Konrad <alessandro.konrad@live.de>, Thomas Vellekoop <thomas.vellekoop@iohk.io>
Comments-URI:
Status: Draft
Type: Informational
Created: 2022-07-13
Post-History:
License: CC-BY-4.0
---

## Abstract

This proposal defines a standard to classify Cardano native assets by the asset name.

## Motivation

As more assets are minted and different standards emerge to query data for these assets, it's getting harder for 3rd parties to determine the asset type and how to proceed with it. This standard is similar to [CIP-0010](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0010), but focuses on the asset name of an asset.


## Specification

To classify assets the `asset_name` needs to be prefixed with an opening and closing parentheses and the label in between: `({Label})`.
 
For example:

UTF-8 encoded: `(123)TestToken`\
HEX encoded: `283132332954657374546F6B656E`


These are the reserved `asset_name_label` values

`asset_name_label`            | description
----------------------------  | -----------------------
0 - 15                        | reserved\*
65536 - 131071                | reserved - private use

For the registry itself, please see [registry.json](./registry.json) in the machine-readable format. Please open your pull request against
this file.

## Rationale

Asset name labels make it easy to classify assets. It's important to understand that a registered label standard itself doesn't provide any security off-chain nor on-chain as they can be spoofed. Only in combination with the Policy ID security can be derived from the minting policy.


## References

- CIP-0010: https://github.com/cardano-foundation/CIPs/blob/master/CIP-0010

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).