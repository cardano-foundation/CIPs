# CIP-88 Extension:  CIP-0026 | Fungible Tokens / Monetary Policy

`Version: 1`

## Top-Level Fields

| index | name            | type                   | required | notes                                                                                     |
|-------|-----------------|------------------------|----------|-------------------------------------------------------------------------------------------|
| 0     | Version         | Unsigned Integer       | No       | Default: 1, which version of this specification is in use                                 |
| 1     | Fungible Tokens | Array\<Token Details\> | No       | An array of one or more fungible token registration objects covered by this registration. |

See [CIP26_v1.cddl](./CIP26_v1.cddl) for a full CBOR CDDL spec, [CIP26_v1.json](./CIP26_v1.json) as an example, and
[CIP26_v1.schema.json](./CIP26_v1.schema.json) for schema documentation. This information can replace the information
currently housed in the [Cardano Token Registry](https://github.com/cardano-foundation/cardano-token-registry) and is
based on the format currently used in those registrations along with a few additional fields.

Because it is possible that multiple fungible tokens could be minted under a single Policy ID, the format for CIP-26
tokens is slightly different. Here we include an array of fungible token details inside an array to enable multiple
tokens under the same policy to be registered in a single transaction.

**Example:**

```cbor
{
    867: {
        0: 1,
        1: {
            6: {
                26: {
                    0: 1,
                    1: [
                        [...Fungible Token 1 Details...],
                        [...Fungible Token 2 Details...]
                    ]
                }
            }
        },
        2: [...]
    }
}
```

## Fungible Token Details Fields

| index | name                                 | type                                  | required |
|-------|--------------------------------------|---------------------------------------|----------|
| 0     | [Subject](#0--subject)               | [Token Identifier](#token-identifier) | Yes      |
| 1     | [Token Name](#1--token-name)         | String                                | Yes      |
| 2     | [Description](#2--description)       | Array                                 | Yes      |
| 3     | [Token Ticker](#3--token-ticker)     | String                                | No       |
| 4     | [Token Decimals](#4--token-decimals) | Unsigned Integer                      | No       |
| 5     | [Token Website](#5--token-website)   | [URI Array](#uri-array)               | No       |
| 6     | [Token Image](#6--token-image)       | [URI Array](#uri-array)               | No       |
| 7     | [Beacon Token](#7--beacon-token)     | [Token Identifier](#token-identifier) | No       |

### Field Notes

#### 0: Subject

***Type: [Token Identifier](#token-identifier) | Required: Yes***

A Token Identifier identifying the specific token being registered.

**Example:** `[h'd894897411707efa755a76deb66d26dfd50593f2e70863e1661e98a0',h'7370616365636f696e73']`

#### 1: Token Name

***Type: String | Required: Yes***

This is the full "display name" of the token.

**Example:** `"spacecoins"`

#### 2: Description

***Type: Array | Required: Yes***

A plain-text description for the token. This should be an array of zero or more strings.

**Example:** `[
"the OG Cardano community token",
"-",
"whatever you do, your did it!",
"",
"Learn more at https://spacecoins.io!"
]`

#### 3: Token Ticker

***Type: String | Required: No | Default: [Token Name](#1--token-name)***

A short "ticker" identifier for the token. Usually 1 to 5 characters.

**Example:** `"SPACE"`

#### 4: Token Decimals

***Type: Unsigned Integer | Required: No | Default: 0***

How many decimal places this token should be treated as having to create a "whole unit". Default is 0 (no decimals).
Lovelace has 6 decimal places (1.000001)

**Example:** `6`

#### 5: Token Website

**Type: [URI Array](#uri-array) | Required: No | default: Null**

A valid [URI Array](#uri-array) object describing the URI to the token website.

**Example:** `["https://","www.spacecoins.io"]`

#### 6: Token Image

**Type: [URI Array](#uri-array) | Required: No | Default: Null**

A valid [URI Array](#uri-array) describing the URI to a thumbnail image to be used for the token. Recommended 64px by
64px resolution, transparent background PNG file.

**Example:** `["ipfs://","bafkreibva6x6dwxqksmnozg44vpixja6jlhm2w7ueydkyk4lpxbowdbqly"]`

#### 7: Beacon Token

**Type: [Token Identifier](#token-identifier) | Required: No | Default: Null**

A valid [Token Identifier](#token-identifier) to be used as a _"beacon token"_ for the project. Purposes and format
TBD. This token could be used as a reference input in smart contracts and provide context and data via inline datum.

#### Token Identifier

A token identifier is an array that MUST contain two entries. The first entry MUST be the byte-encoded Policy ID. The
second entry MUST be the byte-encoded Asset ID.

**Example:** `[h'<policy_id>',h'<asset_id>']`

#### URI Array

A URI Array ([Schema Definition](../common/uri-array.schema.json)) is an array of two or more strings that can be
concatenated to create a valid URI. The first entry of the URI Array must define the _URI
scheme_ (`https://, ar://, ipfs://, etc`) and subsequent entries define the path and any arguments that may be required
(`www.spacecoins.io`).

**Example:**
`["https://", "www.spacecoins.io"]`, `["ar://", "abc123"]`, `["ipfs://", "bafkreibva6x6dwxqksmnozg44vpixja6jlhm2w7ueydkyk4lpxbowdbqly"]`

## CIP-26 Example

```cbor
{
  26: {
    0: 1,
    1: [
      {
        0: [
          h'd894897411707efa755a76deb66d26dfd50593f2e70863e1661e98a0',
          h'7370616365636f696e73'
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
          h'd894897411707efa755a76deb66d26dfd50593f2e70863e1661e98a0',
          h'7370616365636f696e74'
        ]
      }
    ]
  }
}
```