# CIP-26: Fungible Token Registration Format

## Top-Level Index: 26

### Type: Object | Required: Yes

### Properties

All properties should be numeric indexes with specific purposes. If the community desires an additional index to be
defined as part of the specification, it should be added in to this CIP so that documentation always remains intact.

If a property is null or not-applicable 

### Index: 1

#### Type: Array | Required: Yes | Items: Token Description Object(s)

The only current index for the CIP-26 Fungible Token registration is Index #1, an array of objects describing a fungible
token on the blockchain and its monetary policy information.

This entry is defined as an array of objects to handle the case when multiple fungible tokens exist under the same
Native Script.

### Token Description Object

#### Type: Object

#### Properties

#### Index 0 (Fingerprint)

##### Type: Array of Strings | Required: Yes

The 0 (zero) index of the object should be reserved for the "asset fingerprint". Here we use a two-item array consisting
of a string containing the hex-encoded Native Script "Policy ID" and then a string containing the hex-encoded "Asset ID".

**Example:**

```json
{
  "0": [
    "d894897411707efa755a76deb66d26dfd50593f2e70863e1661e98a0",
    "7370616365636f696e73"
  ]
}
```

#### Index 1 (Token Name)

##### Type: String | Required: Yes

This string represents the "display name" that should be used for this token.

**Example:**

```json 
{
  "1": "spacecoins"
}
```

#### Index 2 (Ticker/Symbol)

##### Type: String | Required: Yes

This string represents the ticker or lookup symbol for the token.

**Example:**

```json
{
  "2": "SPACE"
}
```

#### Index 3 (Description)

##### Type: Array of Strings | Required: No | Default: None

Because of the 64-character limit for Cardano on-chain metadata, the description should always be an array containing
zero or more strings of max-length 64 characters. For display purposes, this array or strings should be concatenated
with spaces between each entry and an "empty" string should be treated as a paragraph break (if supported).

**Example:**

```json
{
  "3": [
    "the OG Cardano community token",
    "-",
    "whatever you do, your did it!",
    "",
    "Learn more at https://spacecoins.io!"
  ]
}
```

**Formatted Example:**

```text 
the OG Cardano community token - whatever you do, your did it!

Learn more at https://spacecoins.io
```

#### Index 4 (Decimals)

##### Type: Unsigned Integer | Required: No | Default: 0

Because Cardano Native Assets always represent a singular, indivisible unit or lowest common denominator of currency,
one of the primary uses of the Cardano Token Registry (and hopefully this CIP in the future) is to inform wallets and
other aggregator sites of the proper display formatting for native assets when it comes to decimal representation.

Native tokens may represent a whole unit (0 decimal places) or some fraction of a whole. This is the same as how all
transactions on the blockchain are calculated in Lovelace (the base asset) but we refer to $ADA which is 1,000,000
Lovelace. i.e. If we were registering a hypothetical "ADA" token we would say that it has 6 decimal places.

**Example:**

```json
{
  "4": 6
}
```

#### Index 5 (Token URL)

##### Type: URI Array | Required: No | Default: None

To maintain consistency and stay within the bounds of Cardano's 64-character limit for strings inside of metadata, all
URI-type fields should consist of an array of strings containing two-or-more entries. The first entry should always be
the URI "scheme" (i.e. https://) and subsequent entries should consist of 64-character strings that may be concatenated
without spaces to form the "path" of the URI.

**Example:**

```json
{
  "5": [
    "https://",
    "spacecoins.io"
  ]
}
```

**Formatted Example:**

```text
https://spacecoins.io
```

#### Index 6 (Token Icon URI)

##### Type: URI Array | Required: No | Default: None

This entry should consist of a URI (following the same rules as [Index 5](#index-5--token-url-) above) to describe the
path to a logo that can be used to represent this token in wallets or display aggregators. The image should be a PNG
image with transparent background that is no larger than 64kb in size.

Minimum supported URI schemes that aggregators and display clients should support are: HTTP: `http://`, 
HTTPS: `https://`, Arweave: `ar://`, IPFS: `ipfs://`. Token Icons should be cached permanently (or until an updated
registration is observed on chain) if possible to minimize network latency and ensure availability issues for all users.

**IPFS Example:**

```json 
{
  "6": [
    "ipfs://",
    "bafkreib3e5u4am2btduu5s76rdznmqgmmrd4l6xf2vpi4vzldxe25fqapy"
  ]
}
```

**Arweave Example:**

```json
{
  "6": [
    "ar://",
    "WRi9jboeKx1fbjcvO5q0kshaMmdaYgDnYlMEy-loZeY"
  ]
}
```

#### Index 7 (Disclosure Documentation)

##### Type: Array | Required: No | Default: None

This entry is reserved for an upcoming/additional CIP [[insert link here]]() to introduce the concept of financial 
disclosure documentation for Cardano fungible token projects. The array should consist of two entries:

1. A URI Array (as described/documented above) as the first entry
2. The SHA256 Checksum of the document as the second entry

Because the checksum should be used as an additional layer of validation that the financial disclosure documentation has
not been tampered with or modified since publication, it is recommended that a project first publish and verify the 
checksum of their published document prior to publishing their updated token registration information.

Similarly, for consumers, a financial disclosure document should be ignored/omitted if the checksum does not match what
was retrieved.

It is recommended to publish financial disclosure documents via a "permanent" hosting solution such as Arweave or IPFS
whenever possible.

**IPFS Example:**

```json
{
  "7": [
    [
      "ipfs://",
      "bafkreibva6x6dwxqksmnozg44vpixja6jlhm2w7ueydkyk4lpxbowdbqly"
    ],
    "3507afe1daf05498d764dce55e8ba41e4acecd5bf42606ac2b8b7dc2eb0c305e"
  ]
}
```

#### Index 8 (Inline Datum Reference)

##### Type: UTXO Array | Required: No | Default: None

For projects that are interested in publishing their disclosure documentation via an inline datum for subsequent
consumption and usage within Smart Contracts, this index should contain a specialized array consisting of two string
entries:

1. The transaction hash
2. The transction index

**UTXO Array Example:**

```json
{
  "8": [
    "37da68d092f4e61feb237de5e86b404171b59d3880d340023a16a6983491736d",
    "0"
  ]
}
```

## Minimal Example

Below is a minimal (required fields only) example of the complete CIP-26 reference information required to be submitted.

```json
{
  "26": {
    "1": [
      {
        "0": [
          "d894897411707efa755a76deb66d26dfd50593f2e70863e1661e98a0",
          "7370616365636f696e73"
        ],
        "1": "spacecoins",
        "2": "SPACE"
      }
    ]
  }
}
```

## Complete Example

Below is a complete (all fields populated) example of the complete CIP-26 reference information to be submitted.

```json
{
  "26": {
    "1": [
      {
        "0": [
          "d894897411707efa755a76deb66d26dfd50593f2e70863e1661e98a0",
          "7370616365636f696e73"
        ],
        "1": "spacecoins",
        "2": "SPACE",
        "3": [
          "the OG Cardano community token",
          "-",
          "whatever you do, your did it!",
          "",
          "Learn more at https://spacecoins.io!"
        ],
        "4": 0,
        "5": [
          "https://",
          "spacecoins.io"
        ],
        "6": [
          "ipfs://",
          "bafkreib3e5u4am2btduu5s76rdznmqgmmrd4l6xf2vpi4vzldxe25fqapy"
        ],
        "7": [
          [
            "ipfs://",
            "bafkreibva6x6dwxqksmnozg44vpixja6jlhm2w7ueydkyk4lpxbowdbqly"
          ],
          "3507afe1daf05498d764dce55e8ba41e4acecd5bf42606ac2b8b7dc2eb0c305e"
        ],
        "8": [
          "37da68d092f4e61feb237de5e86b404171b59d3880d340023a16a6983491736d",
          "0"
        ]
      }
    ]
  }
}
```

## Schema Definition

Please see [CIP26.schema.json](CIP26.schema.json) for a JSON schema definition of this format.