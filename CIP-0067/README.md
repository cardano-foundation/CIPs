---
CIP: 67
Title: Asset Name Label Registry
Status: Proposed
Category: Tokens
Authors: 
  - Alessandro Konrad <alessandro.konrad@live.de>
  - Thomas Vellekoop <thomas.vellekoop@iohk.io>
Implementors: N/A
Discussions:
 - https://github.com/cardano-foundation/CIPs/pull/298
 - https://github.com/cardano-foundation/CIPs/pull/586
Created: 2022-07-13
License: CC-BY-4.0
---

## Abstract

This proposal defines a standard to identify Cardano native assets by the asset name to put them in an asset class, as intended by their issuer.

## Motivation: why is this CIP necessary?

As more assets are minted and different standards emerge to query data for these assets, it's getting harder for 3rd parties to determine the asset class and associated extra assumptions that may arise from this identification. For example, if an asset is identified as a non-fungible token, a third party is interested in its onchain associated metadata. This standard is similar to [CIP-0010](../CIP-0010), but focuses on the asset name of a native asset.

## Specification

To give issuers the option to classify assets, the `asset_name` MUST be prefixed with 4 bytes encoding the following binary value:
```
[ 0000 | 16 bits label_num | 8 bits checksum | 0000 ]
```
- The leading and ending four 0s are brackets
- `label_num` has a fixed size of 2 bytes (`Label range in decimal: [0, 65535]`). 
If `label_num` < 2 bytes, the remaining bits MUST be left-padded with 0s.
- `checksum` has a fixed size of 1 byte. The checksum is calculated by applying the [CRC-8](#CRC-8) algorithm on the `label_num (including the padded 0s)`. 

### CRC-8

- Polynomial: `0x07`
- Lookup table:
```
[
  0x00, 0x07, 0x0e, 0x09, 0x1c, 0x1b, 0x12, 0x15, 0x38, 0x3f, 0x36, 0x31, 0x24,
  0x23, 0x2a, 0x2d, 0x70, 0x77, 0x7e, 0x79, 0x6c, 0x6b, 0x62, 0x65, 0x48, 0x4f,
  0x46, 0x41, 0x54, 0x53, 0x5a, 0x5d, 0xe0, 0xe7, 0xee, 0xe9, 0xfc, 0xfb, 0xf2,
  0xf5, 0xd8, 0xdf, 0xd6, 0xd1, 0xc4, 0xc3, 0xca, 0xcd, 0x90, 0x97, 0x9e, 0x99,
  0x8c, 0x8b, 0x82, 0x85, 0xa8, 0xaf, 0xa6, 0xa1, 0xb4, 0xb3, 0xba, 0xbd, 0xc7,
  0xc0, 0xc9, 0xce, 0xdb, 0xdc, 0xd5, 0xd2, 0xff, 0xf8, 0xf1, 0xf6, 0xe3, 0xe4,
  0xed, 0xea, 0xb7, 0xb0, 0xb9, 0xbe, 0xab, 0xac, 0xa5, 0xa2, 0x8f, 0x88, 0x81,
  0x86, 0x93, 0x94, 0x9d, 0x9a, 0x27, 0x20, 0x29, 0x2e, 0x3b, 0x3c, 0x35, 0x32,
  0x1f, 0x18, 0x11, 0x16, 0x03, 0x04, 0x0d, 0x0a, 0x57, 0x50, 0x59, 0x5e, 0x4b,
  0x4c, 0x45, 0x42, 0x6f, 0x68, 0x61, 0x66, 0x73, 0x74, 0x7d, 0x7a, 0x89, 0x8e,
  0x87, 0x80, 0x95, 0x92, 0x9b, 0x9c, 0xb1, 0xb6, 0xbf, 0xb8, 0xad, 0xaa, 0xa3,
  0xa4, 0xf9, 0xfe, 0xf7, 0xf0, 0xe5, 0xe2, 0xeb, 0xec, 0xc1, 0xc6, 0xcf, 0xc8,
  0xdd, 0xda, 0xd3, 0xd4, 0x69, 0x6e, 0x67, 0x60, 0x75, 0x72, 0x7b, 0x7c, 0x51,
  0x56, 0x5f, 0x58, 0x4d, 0x4a, 0x43, 0x44, 0x19, 0x1e, 0x17, 0x10, 0x05, 0x02,
  0x0b, 0x0c, 0x21, 0x26, 0x2f, 0x28, 0x3d, 0x3a, 0x33, 0x34, 0x4e, 0x49, 0x40,
  0x47, 0x52, 0x55, 0x5c, 0x5b, 0x76, 0x71, 0x78, 0x7f, 0x6a, 0x6d, 0x64, 0x63,
  0x3e, 0x39, 0x30, 0x37, 0x22, 0x25, 0x2c, 0x2b, 0x06, 0x01, 0x08, 0x0f, 0x1a,
  0x1d, 0x14, 0x13, 0xae, 0xa9, 0xa0, 0xa7, 0xb2, 0xb5, 0xbc, 0xbb, 0x96, 0x91,
  0x98, 0x9f, 0x8a, 0x8d, 0x84, 0x83, 0xde, 0xd9, 0xd0, 0xd7, 0xc2, 0xc5, 0xcc,
  0xcb, 0xe6, 0xe1, 0xe8, 0xef, 0xfa, 0xfd, 0xf4, 0xf3,
]
```
 
### Example:

#### Construct a label
We want to use the decimal label `222` for an asset name:

1. Convert to hex and pad with missing 0s => `0x00de`
2. Calculate CRC-8 checksum => `0x14`
3. Add brackets and combine label => `0x000de140`

#### Verify a label
We have the following asset name: `0x000de140`

1. Slice off the first 4 bytes of the asset name => `0x000de140`
2. Check if first 4 bits and last 4 bits are `0b0000` (`0x0`)
3. Slice off the 2 `label_num` bytes and apply them to the CRC-8 algorithm. If the result matches with the `checksum` byte, a `valid` label was found and it can be returned. => `0x00de`
4. Convert to decimal => `222`

### Reserved labels

These are the reserved `asset_name_label` values

| `asset_name_label` | class | description |
|--------------------|-------|-------------|
| 0 - 15             | -     | private use |

### Adding an entry to the registry

> The keywords "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL
> NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED",  "MAY", and
> "OPTIONAL" in this section are to be interpreted as described in
> [RFC 2119](https://datatracker.ietf.org/doc/html/rfc2119).

Those wishing to propose an addition to this registry **MUST** draft a new CIP describing the standard for implementing
the token. Once the CIP has achieved the `Under Review` status the proposer **SHALL** make the necessary edits to 
[registry.json](./registry.json). These changes **SHOULD** be submitted under a separate pull request against the CIP
repository and include a brief description of the standard and a link to the CIP Pull Request describing implementation
details.

### Test Vectors

Keys represent labels in `decimal` numbers. Values represent the entire label, including brackets and checksum in `hex`:

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

## Rationale: how does this CIP achieve its goals?

Asset name labels make it easy to identify native assets and classify them in their asset class intended by the issuer. Since the identification of these native assets is done by third parties, the design is focused on the usability for them.

First, the label should be quickly parsable with a first check. That is, an initial check on an asset name that is easy and will exclude a big subset of the available token names that do not follow standard. This is why the label starts and ends with `0000` in bits. Additionally, in its hex notation, this is differentiable by a human in its readable form, a more common representation.

Secondly, the remaining verification on whether a certain `asset_name_label` standard is followed should be a one shot calculation. Here we mean that the calculation of the check should be straightforward, the label should not be fitted via brute force by a third party. That's why the label contains the bit representation of the integer label it tries to follow.

Another thing that is important to understand is that an oblivious token issuer might not be aware of this standard. This could lead to the unintentional misinterpretation by third parties and injection attacks. We can minimize this attack vector by making the label format obscure. That is why the label also contains a checksum derived from the `asset_name_label` to add characters that are deterministically derived but look like nonsense. Together with the above zero "brackets", and the fixed size binary encoding, it make it unlikely someone follows this standard accidentally. The CRC-8 checksum is chosen for it low-impact on resources and its readily available implementations in multiple languages.

## Path to Active

### Acceptance Criteria

- [X] Get support for this CIP by wallets, explorers, minting platforms and other 3rd parties.
- [X] Get support by tools/libraries like Lucid, PlutusTx, cardano-cli, etc. to generate/verify labels.

### Implementation Plan

- [X] Provide reference implementations:
  - [X] [Lucid TypeScript implementation of toLabel/fromLabel](https://github.com/spacebudz/lucid/blob/39cd2129101bd11b03b624f80bb5fe3da2537fec/src/utils/utils.ts#L500-L522)
  - [X] [Lucid TypeScript implementation of CRC-8](https://github.com/spacebudz/lucid/blob/main/src/misc/crc8.ts)

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
