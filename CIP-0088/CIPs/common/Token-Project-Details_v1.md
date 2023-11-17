# CIP-88: NFT Project Details Specification

`Version: 1`

The Token Project Details specification attempts to provide top-level information about Token Projects for consumption
by wallets, blockchain explorers, and marketplaces to help avoid the hassle of project creators and maintainers needing
to notify and update all potential consumers about the details (name, description, etc) of their project.

It is broken out as a CIP-88 "Common" element as it is shared by at least CIP-25 and CIP-68 projects and potentially
other standards in the future.

***NFT Project Details Fields***

| Index | Name                                          | Type   | Required |
|-------|-----------------------------------------------|--------|----------|
| 0     | [Collection Name](#0--Collection-Name)        | String | Yes      |
| 1     | [Description](#1--Description)                | Array  | No       |
| 2     | [Project Image](#2--Project-Image)            | URI    | No       |
| 3     | [Project Banner](#3--Project-Banner)          | URI    | No       |
| 4     | [NSFW Flag](#4--NSFW-Flag)                    | 0 or 1 | No       |
| 5     | [Social Media](#5--Social-Media)              | Array  | No       |
| 6     | [Project/Artist Name](#6--ProjectArtist-Name) | String | No       |

**CBOR CDDL Specification**

A dedicated CDDL file can be found at: [token-project-details_v1.cddl](./token-project-details_v1.cddl)

```cbor 
; Token Project Details CDDL
; Version: 1

string = text .size (0..64)

; A uri should consist of a scheme and one or more path strings describing the path to the resource
; The first entry should contain the URI "Scheme" (e.g. "https://", "ftp://", "ar://", "ipfs://")
; One or more subsequent entries should describe the path of the URI

uri.scheme = text .size (5..64)
uri.path = text .size (1..64)
uri = {
    uri.scheme,
    + uri.path
}

; NFT Project Details
;
; Provide top-level information about NFT projects that can be useful to marketplaces and explorers

social-media-uri = {
    string,                      ; social media channel name
    uri                          ; social media URI
}

token-project-details = {
    0 : string,                  ; Collection Name
    ? 1 : [* string],            ; Description
    ? 2 : uri,                   ; Project Image
    ? 3 : uri,                   ; Project Banner
    ? 4 : 0 / 1,                 ; NSFW Flag (1 = true, 0 = false)
    ? 5 : [* social-media-uri],  ; Project social media
    ? 6 : string                 ; Project/Artist Name
}
```

## Field Notes

### 0: Collection Name

***Type: String | Required: Yes***

The "Collection" name that applies specifically to the tokens minted under this policy.

**Example:** `"SpaceBudz"`

### 1: Description

***Type: Array | Required: No***

An array of strings containing a brief "description" of this project

**Example:** `["10,000 SpaceBudz are out there.","Where will your SpaceBudz take you?"]`

### 2: Project Image

***Type: URI | Required: No***

An array of strings describing a URI to a "profile image" that may be used for this project.

**Example:** `["ipfs://", ""]`

### 3: Project Banner

***Type: URI | Required: No***

An array of strings describing a URI to a "banner image" that may be used for this project.

**Example:** `["ar://",""]`

### 4: NSFW Flag

***Type: 0 or 1 | Required: No | Default: 0***

"Not Safe for Work" flag. Do the assets within this project contain sensitive material that may not be suitable for all
audiences and should potentially be obfuscated or hidden. 0 = no sensitive content, "Safe for Work"; 1 = sensitive
content, "Not Safe for Work"

**Example:** `0`

### 5: Social Media

***Type: Array | Required: No***

An array of zero or more [social media handles](#social-media-handle) for the project. Each entry of the array should be
itself an array. The first entry should be a string containing the "name" of the social media platform. The second entry
should be an array describing the URI to the social media site.

### 6: Project/Artist Name

***Type: String | Required: No***

#### Social Media Handle

***Type: Array | Required: No***

A social media handle must be an array consisting of two entries. The first entry should be the string social media
platform identifier (i.e. `Twitter, Discord, etc`) while the second entry must be a _URI
Array_ ([Schema Definition](./uri-array.schema.json)) consisting of two or more elements. The first element of the URI
array MUST contain the URI Scheme as a string, while one or more subsequent string entries represent the URI path.

**Specification (CBOR)**

```cbor
social-media-title = text .size (1..64)
uri.scheme = text .size (5..64)
uri.path = text .size (1..64)

social-media-handle = {
  social-media-title,    ; Name of the social media platform (for labelling purposes)
  {                      ; URI Definition
    uri.scheme,          ; URI Scheme (i.e. https://, ar://, ipfs://, ftp://)
    + uri.path           ; One or more strings describing the path to the resource
  }
}
```

**Example:**

```cbor 
[
  [
    "Twitter",
    [
      "https://",
      "twitter.com"
    ]
  ],
  [
    "Discord",
    [
      "https://",
      "discord.gg/",
      "buffybot"
    ]
  ]
]
```

### 6: Project/Artist Name

***Type: String | Required: No***

If this policy is part of a larger project or series from a specific artist or project, this field can be used to
contain that name.

**Example:** `"Alessandro Konrad"`

## Complete Example

```cbor
{
  0: "Cool NFT Project",
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
  6: "Virtua Metaverse"
}
```