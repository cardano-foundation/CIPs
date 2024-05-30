# CIP-88 Extension: CIP-0066 | Datum Token Project Information

`Version: 1`

## Top-Level Fields

Both CIP-25 and CIP-68 are specifications describing a standard for storing and retrieving token metadata from the
chain. To this end, we have given them the same data structure although each will utilize their own numerical index in
the feature set and CIP-Specific details section of the registration.

These sections may be separated in the future if the respective CIPs diverge in terms of the data or information that
may be useful to provide about one format or the other in the future.

| index | name                     | type             | required | notes                                                                                                       |
|-------|--------------------------|------------------|----------|-------------------------------------------------------------------------------------------------------------|
| 0     | Version                  | Unsigned Integer | No       | Default: 1, which version of this specification is in use                                                   |
| 1     | Token Collection Details | Object           | Yes      | Provide additional context about this "Collection" for consumption by marketplaces, explorers, and wallets. |

The information registered here is helpful to aggregator services and marketplaces, it applies equally to both CIP-25
and CIP-68 metadata standards. A project utilizing one or the other should reference this documentation and include the
relevant information under index #6, prefixed by the number of the CIP (25 or 68) depending upon the metadata format.

## Token Collection Details Fields

| index | name                | type     | required |
|-------|---------------------|----------|----------|
| 0     | Collection Name     | String   | Yes      |
| 1     | Description         | Array    | No       |
| 2     | Project Image       | UriArray | No       |
| 3     | Project Banner      | UriArray | No       |
| 4     | NSFW Flag           | 0 or 1   | No       |
| 5     | Social Media        | Array    | No       |
| 6     | Project/Artist Name | String   | No       |

For details on what these fields represent and how they should be structured in the metadata, please refer to
[Token Project Details](../common/Token-Project-Details_v1.md)

## CIP-68 Example

```cbor 
{
  68: {
    0: 1,
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