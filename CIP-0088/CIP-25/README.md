# CIP 25/68: NFT Registration Format

## Top Level Index: 25 or 68

##### Type: Object | Required: Yes

Because this registration descriptor defines the "top-level" project information about an NFT project on Cardano, it can
be used with both CIP-25 or CIP-68 tokens and provide the same data. Projects that utilize CIP-25 or CIP-68 should make
sure to declare which NFT Metadata Standard they utilize in the feature set registration and then provide these project
details via the same index (25 or 68).

#### Properties

### Index 1 (Project Details)

##### Type: Object | Required: Yes

We use a CBOR-like data structure beginning with Index #1 for this format so that we maintain flexibility to add
additional indexes and additional informational data points in the future as the industry/community needs evolve. Index
#1 will serve to identify top-level information about the NFT project and should pertain to all tokens minted under
the specified policy ID.

#### Properties

### Index 0 (Policy Name)

##### Type: String | Required: Yes

There are several "names" generally associated with an NFT project. For the purposes of this CIP we will
consider this "Policy Name" as the name for all tokens under the given policy ID. Commonly referred to as a "Collection"
name by marketplaces.

**Example:**

```json
{
  "25|68": {
    "1": {
      "0": "SpaceBudz"
    }
  }
}
```

### Index 1 (Policy Description)

##### Type: Array of Strings | Required: No | Default: None

This is potentially self-descriptive but is an optional "description" of the NFTs under the given policy. Generally
found under the "Collection" page when exploring on marketplaces. Each string within the description array should be at
most 64 characters and explorers should display the description by concatenating each line with a space between. An empty
string should be treated as a paragraph break.

**Example:**

```json
{
  "25|68": {
    "1": {
      "1": [
        "10,000 SpaceBudz are out there.",
        "Where will your SpaceBudz take you?"
      ]
    }
  }
}
```

**Formatted Example:**

```text
10,000 SpaceBudz are out there. Where will your SpaceBudz take you?
```

### Index 2 (Project Image)

##### Type: URI Array | Required: No | Default: None

This entry should follow the "URI Array" syntax where the URI scheme is the first string entry of the array followed by
one or more strings comprising the path to the asset. In this way we can support HTTP, HTTPS, Arweave, and IPFS in a 
consistent fashion for maximum flexibility. Consumer projects should, where possible, cache these images locally to 
ensure image availability and consistent consumer experience until an updated registration is observed.

This image is generally used similar to a "PFP" type of image so should be in a square aspect ratio (1:1) and padded to
accommodate cropping depending on the platform.

**Example:**

```json
{
  "25|68": {
    "1": {
      "2": [
        "https://",
        "static.spacebudz.io",
        "/images/logo.png"
      ]
    }
  }
}
```

### Index 3 (Project Banner Image)

##### Type: URI Array | Required: No | Default: None

Following the same format for the Project Image URI Array above, this URI should point to a "banner image" that can be
used to represent the project and optionally be displayed by platforms.

The specified resource for both Project Image and Project Banner Image should be an image that is natively supported by
the HTML `<img>` tag.

**Example:**

```json
{
  "25|68": {
    "1": {
      "3": [
        "https://",
        "static.spacebudz.io",
        "/images/banner.jpg"
      ]
    }
  }
}
```

### Index 4 (Not Safe for Work [NSFW] Flag)

##### Type: Unsigned Integer | Required: No | Default: 0

This is a simple true/false field (1 = True, 0 = False, Default = 0) to represent whether the project contains
"Not Safe for Work" content that may not be suitable for all audiences.

**Example:**

```json
{
  "25|68": {
    "1": {
      "4": 0
    }
  }
}
```

### Index 5 (Social Media URIs)

##### Type: Object | Required: No | Default: None

This will be the only field where we will use named keys because social media platforms are so varied and rapidly
evolving. The object should consist of key:value pairs where the name of the platform should be the key and a URI Array
pointing to the project's social media profile is the value. Keys should always be all lowercase and consist of only
letters and numbers.

**Example:**

```json
{
  "25|68": {
    "1": {
      "5": {
        "twitter": [
          "https://",
          "twitter.com/spacebudzNFT"
        ],
        "discord": [
          "https://",
          "discord.gg/spacebudz"
        ]
      }
    }
  }
}
```

### Index 6 (Project Name)

##### Type: String | Required: No | Default: Policy Name

For projects that belong under an over-arching umbrella (such as Claymates, Virtua, etc.) where a single "project" may
have multiple NFT policies or "collections", this field allows a space for the "Project Name". This could also be the
name of the "artist" if an artist creates NFTs under multiple different policies.

If this field is not present, the Policy Name should be used (if necessary).

**Example:**

```json
{
  "25|68": {
    "1": {
      "0": "Cardano Island Vehicles",
      "6": "Virtua"
    }
  }
}
```

## Minimal Example

Below is a minimal example with only the singular required field present.

```json
{
  "25": {
    "1": {
      "0": "SpaceBudz"
    }
  }
}
```

## Complete Example

Below is a full example with all fields present.

```json
{
  "68": {
    "1": {
      "0": "SpaceBudz",
      "1": [
        "10,000 SpaceBudz are out there.",
        "Where will your SpaceBudz take you?"
      ],
      "2": [
        "https://",
        "static.spacebudz.io",
        "/images/logo.png"
      ],
      "3": [
        "https://",
        "static.spacebudz.io",
        "/images/banner.jpg"
      ],
      "4": 0,
      "5": {
        "twitter": [
          "https://",
          "twitter.com/spacebudzNFT"
        ],
        "discord": [
          "https://",
          "discord.gg/spacebudz"
        ]
      },
      "6": "SpaceBudz"
    }
  }
}
```

## Schema Definition

Please see [CIP25.schema.json](CIP25.schema.json) for a JSON schema definition of this format.
