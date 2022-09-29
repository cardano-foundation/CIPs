---
CIP: 67
Title: Asset Name Label Registry
Authors: Alessandro Konrad <alessandro.konrad@live.de>, Thomas Vellekoop <thomas.vellekoop@iohk.io>
Status: Draft
Type: Informational
Created: 2022-07-13
License: CC-BY-4.0
---

## Abstract

This proposal defines a standard to classify Cardano native assets by the asset name.

## Motivation

As more assets are minted and different standards emerge to query data for these assets, it's getting harder for 3rd parties to determine the asset type and how to proceed with it. This standard is similar to [CIP-0010](../CIP-0010), but focuses on the asset name of an asset.


## Specification

To classify assets the `asset_name` needs to be prefixed the following `4 bytes` binary encoding:
```
[ 0000 | 2 bytes label_num | 1 byte checksum | 0000 ]
```
- The leading and ending four 0s are brackets
- `label_num` has a fixed size of 2 bytes (`Label range in decimal: [0, 65535]`). 
If `label_num` < 2 bytes the remaining bits need to be padded with 0s.
- `checksum` has a fixed size of 1 byte. The checksum is calculated by applying the CRC-8 algorithm on the `label_num (including the padded 0s)`. 
 
### Example:

#### Construct a label
We want to use the decimal label `222` for an asset name:

1. Convert to hex and pad with missing 0s => `0x00de`
2. Calculate CRC-8 checksum => `0x14`
3. Add brackes and combine label => `0x000de140`

#### Verify a label
We have the following asset name: `0x000de140`

1. Slice off the first 4 bytes of the asset name => `0x000de140`
2. Check if first 4 bits and last 4 bits are `0b0000` (`0x0`)
3. Slice of the 2 `label_num` bytes and apply them to the CRC-8 algorithm. If the result matches with the `checksum` byte a `valid` label was found and it can be returned. => `0x00de`
4. Convert to decimal => `222`


### Reserved labels

These are the reserved `asset_name_label` values

`asset_name_label`            | class | description              |
----------------------------  | ----- |  ----------------------- |
0 - 15                        | -     |  private use             |

### Adding an entry to the registry

To propose an addition to the registry edit the [registry.json](./registry.json) with your details, open a pull request against the CIPs repository and give a brief description of your project and how you intend to use the label for assets.

## Rationale

Asset name labels make it easy to classify assets. It's important to understand that an oblivious token issuer might use the prefix X for all kinds of things, leading to misinterpretation by clients that follow this standard. We can minimize this attack vector by making the label format obscure. Brackets, checksum and fixed size binary encoding make it unlikely someone follows this standard by accident.

## Reference Implementation(s)

- [Lucid TypeScript implementation of toLabel/fromLabel](https://github.com/spacebudz/lucid/blob/39cd2129101bd11b03b624f80bb5fe3da2537fec/src/utils/utils.ts#L500-L522)
- [Lucid TypeScript implementation of CRC-8](https://github.com/spacebudz/lucid/blob/main/src/misc/crc8.ts)

## Test Vectors

Keys represent labels in `decimal` numbers. Values represent the entire label including brackets and checksum in `hex`:

```yaml
0     : 00000000
1     : 00001070
23    : 00017650
99    : 000632e0
533   : 00215410
2000  : 007d0550
4567  : 011d7690
11111 : 02b670b0
49328 : 0c0b0f40
65535 : 0ffff240
```

## References

- CIP-0010: https://github.com/cardano-foundation/CIPs/blob/master/CIP-0010

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).