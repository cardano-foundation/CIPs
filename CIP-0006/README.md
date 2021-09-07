---
CIP: 6
Title: Stake Pool Extended Metadata
Authors: Markus Gufler <gufmar@gmail.com>, Mike Fullman <mike@fullman.net>
Comments-URI: https://github.com/cardano-foundation/CIPs/pull/15
Status: Draft
Type: Standards
Created: 2020-07-20
Updated: 2020-11-24 2nd key-pair for validation 2021-02-08 json schema
License: CC-BY-4.0
---

## Abstract

This CIP defines the concept of extended metadata for pools that is referenced from the pool registration data stored on chain.

## Motivation

As the ecosystem around Cardano stake pools proliferate so will the desire to slice, organize and search pool information dynamically.  Currently the metadata referenced on chain provides 512 bytes that can be allocated across the four information categories ([delegation-design-specification Section 4.2)](https://hydra.iohk.io/build/790053/download/1/delegation_design_spec.pdf):

| key           | Value                                |  Rules  |
| ---           | ---                                  |  ---  |
|  `ticker` | Pool ticker.  uppercase | 5 Characters Maximum, Uppercase letters and numbers |
|  `description` | Pool Description.  Text that describes the pool | 50 Characters Maximum |
|  `homepage` | A website URL for the pool  | 64 Characters Maximum, must be a valid URL |
|  `name` | A name for the pool | 50 Characters Maximum |

Many additional attributes can be envisioned for future wallets, pool explorers, and information aggregators.  The proposal below outlines an initial strategy for capturing this extended metadata.

## Specification

### On Chain referenced (main) metadata file
We define two more fields for the on chain referenced metadata file that references another json file on a url with the extended metadata.  The proposed metadata is as follows:

| key           | Value                                | Rules  |
| ---           | ---                                  | ---  |
|  `ticker`       | Pool ticker.  uppercase              | 5 Characters Maximum, Uppercase letters and numbers  |
|  `description` | Pool Description.  Text that describes the pool | 50 Characters Maximum |
|  `homepage` | A website URL for the pool| 64 Characters Maximum, must be a valid URL |
|  `name` | A name for the pool | 50 Characters Maximum |
| `extDataUrl` | A URL for extended metadata | optional, 128 Characters Maximum, must be a valid URL |
| `extSigUrl` | A URL with the extended metadata signature | optional, 128 Characters Maximum, must be a valid URL |
| `extVkey` | the public Key for verification | optional, 68 Characters |

In order to include the additional ext Field data, we suggest increasing the maximum size of the main metadata file from currently 512 to 1024 bytes.

### Extended Metadata - flexible but validable

In difference to the main metadata, the extended metadata should be updateable without having to use the cold key of the pool and without having to perform an on-chain transaction. The consumer of these data should still have the possibility to verify the authenticity of the data.

The operator notes all his additional pool information in the extended metadata (`extData.json`).

We propose the pool operator generate a new public-secret key-pair (`extData.skey` and `extData.vkey`)

```shell
cardano-cli node key-gen 
  --cold-verification-key-file extData.vkey 
  --cold-signing-key-file extData.skey 
  --operational-certificate-issue-counter-file extData.counter
```

Then a new (not available yet) `cardano-cli` command generate the signature (`extData.sign`) .

```shell
cardano-cli stake-pool rawdata-sign
  --raw-metadata-file extData.json
  --signing-key-file extData.skey
  --out-file extData.sign
```

The operator now:

- has the `extData.json` and `extData.sign` files
- will publish them at some https:// URL (probably same host as the main metadata)
- set the published `extData.json` URL in the main metadata `extDataUrl` field
- set the published `extData.sign` URL in then main metadata `extSigUrl` field
- set the `extData.vkey` string in the main metadata `extVkey` field
- re-register the extended main metadata file on chain

This re-registration of the main metadata file with the `extData.vkey` and the two URLs is only necessary once. Afterwards, the operator can update his extended metadata at any time, compute the new signature with the `cardano-cli stake-pool rawdata-sign` command, and publish both files at the existing `extDataUrl` and `extSigUrl`.

### Extended Metadata structure

In the following we describe a first minimal version of the extended Json file format

Since this extended metadata file can be updated at any time by the pool operator, a **serial number** is useful for consuming applications and services to identify updates.

There are main thematic sections with respective subordinate data fields:

- the **itn** section is about the verifiable linking of an ITN pool ticker with its counterpart in Mainnet to identify fraudulent duplicates. (already used as not standardized extension)
- the **pool** section contains additional information about the pool instance
  - the pool.**contact** section contains information for additional information and contact data 
  - the pool.**media_assets** section contains additional information about the pools media files and colors
  - the pool.**itn** section is an optional section for ITN pool operators  



#### Extended Metadata Schema
```json
{
    "$id": "http://example.com/example.json",
    "$schema": "http://json-schema.org/draft-07/schema",
    "default": {},
    "description": "additional information for Cardano Stake Pools",
    "examples": [
        {
            "serial": 2020072001,
            "pool": {
                "id": "0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f",
                "country": "DE",
                "status": "act",
                "contact": {
                    "primary": "email",
                    "email": "help@pooldomain.org",
                    "facebook": "demopool",
                    "github": "demopool",
                    "feed": "https://demopool.com/xml/poolrss.xml",
                    "telegram": "demopool",
                    "twitter": "demopool"
                },
                "media_assets": {
                    "icon_png_64x64": "https://mydemopool.com/icon.png",
                    "logo_png": "https://mydemopool.com/logo.png",
                    "logo_svg": "https://mydemopool.com/logo.svg",
                    "color_fg": "#RRGGBB",
                    "color_bg": "#RRGGBB"
                },
                "itn": {
                    "owner": "ed25519_pk1...",
                    "witness": "ed25519_sig1..."
                }
            },
        }
    ],
    "maxLength": 4096,
    "required": [
        "serial",
        "pool"
    ],
    "title": "Extended stake pool metadata",
    "type": "object",
    "properties": {
        "serial": {
            "$id": "#/properties/serial",
            "default": 0,
            "description": "Integer number incremented on every update, by using YYYYMMDDxx (xx each day start by 01 and is incremented on each update",
            "examples": [
                2021012001
            ],
            "maxLength": 10,
            "minLength": 10,
            "required": [],
            "title": "serial number",
            "type": "integer"
        },
        "pool": {
            "$id": "#/properties/pool",
            "default": {},
            "description": "pool related metadata",
            "required": [
                "id"
            ],
            "title": "stake pool",
            "type": "object",
            "properties": {
                "id": {
                    "$id": "#/properties/pool/properties/id",
                    "type": "string",
                    "title": "Pool ID",
                    "description": "the pools unique id in hex format",
					"maxLength": 48,
					"minLength": 48,
                    "examples": [ "69579373ec20f2f82d2dc2360410350b308112f2939f92a" ]
                },
                "country": {
                    "$id": "#/properties/pool/properties/country",
                    "default": "",
                    "description": "3 letter country code as defined in https://www.iso.org/iso-3166-country-codes.html (alpha-3)",
					"maxLength": 3,
					"minLength": 3,
                    "examples": [ "JPN" ],
                    "title": "declared pool location",
                    "type": "string"
                },
                "status": {
                    "$id": "#/properties/pool/properties/status",
                    "default": "",
					"maxLength": 3,
					"minLength": 3,
                    "description": "the current operative status (see examples).",
                    "examples": [ "active", "retired", "offline", "experimental", "private" ],
                    "title": "pool status",
                    "type": "string"
                },
                "contact": {
                    "$id": "#/properties/pool/properties/contact",
                    "default": {},
                    "description": "Optional contact information.",
                    "examples": [
                        {
                            "primary": "email",
                            "email": "help@demopool.org",
                            "facebook": "demopool",
                            "github": "demopool",
                            "feed": "https://mydemopool.com/xml/poolrss.xml",
                            "telegram": "demopool",
                            "telegram_channel": "https://t.me/coolchannel",
                            "twitter": "demopool"
                        }
                    ],
                    "required": [
                        "primary"
                    ],
                    "title": "Pool contact data",
                    "type": "object",
                    "properties": {
                        "primary": {
                            "$id": "#/properties/pool/properties/contact/properties/primary",
                            "default": "email",
                            "description": "the pools prefered communication channel",
                            "title": "primary contact preference",
                            "type": "string"
                        },
                        "email": {
                            "$id": "#/properties/pool/properties/contact/properties/email",
                            "description": "valid email contact address",
                            "title": "email address",
                            "type": "string"
                        },
                        "facebook": {
                            "$id": "#/properties/pool/properties/contact/properties/facebook",
                            "description": "a user or page name",
                            "title": "facebook account",
                            "examples": [ "demopool" ],
                            "type": "string"
                        },
                        "github": {
                            "$id": "#/properties/pool/properties/contact/properties/github",
                            "description": "a github username",
                            "examples": [ "demopool" ],
                            "title": "github account",
                            "type": "string"
                        },
                        "feed": {
                            "$id": "#/properties/pool/properties/contact/properties/feed",
                            "default": "",
                            "description": "RSS feed URL",
                            "examples": [ "https://mydemopool.com/xml/poolrss.xml" ],
                            "title": "RSS feed",
                            "type": "string"
                        },
                        "telegram": {
                            "$id": "#/properties/pool/properties/contact/properties/telegram",
                            "description": "a telegram username",
                            "examples": [ "demopool" ],
                            "title": "telegram account",
                            "type": "string"
                        },
                        "twitter": {
                            "$id": "#/properties/pool/properties/contact/properties/twitter",
                            "description": "a twitter username",
                            "examples": [ "demopool" ],
                            "title": "twitter account",
                            "type": "string"
                        }
                    }
                },
                "media_assets": {
                    "$id": "#/properties/pool/properties/media_assets",
                    "type": "object",
                    "title": "The pools media assets",
                    "description": "Media file URLs and colors",
                    "required": [
                        "icon_png_64x64"
                    ],
                    "properties": {
                        "icon_png_64x64": {
                            "$id": "#/properties/pool/properties/media_assets/properties/icon_png_64x64",
                            "type": "string",
                            "title": "Pool Icon in PNG file format 64x64 px",
                            "description": "PNG image with exact 64x64 pixel size",
                            "examples": [ "https://mydemopool.com/media/icon64.png" ]
                        },
                        "logo_png": {
                            "$id": "#/properties/pool/properties/media_assets/properties/logo_png",
                            "type": "string",
                            "title": "Pool Logo in PNG file format",
                            "description": "PNG image (should have less than 250 kByte of file size)",
                            "examples": [ "https://mydemopool.com/media/logo.png" ]
                        },
                        "logo_svg": {
                            "$id": "#/properties/pool/properties/media_assets/properties/logo_svg",
                            "type": "string",
                            "title": "Pool Logo in SVG file format",
                            "description": "(shoud have less tha 250 kByte of file size)",
                            "examples": [ "https://mydemopool.com/media/logo.svg" ]
                        },
                        "color_fg": {
                            "$id": "#/properties/pool/properties/media_assets/properties/color_fg",
                            "type": "string",
                            "title": "Pool primary color",
                            "description": "RGB color code.",
                            "examples": [ "#AABBCC" ]
                        },
                        "color_bg": {
                            "$id": "#/properties/pool/properties/media_assets/properties/color_bg",
                            "type": "string",
                            "title": "Pool secondary color",
                            "description": "RGB color code.",
                            "default": "",
                            "examples": [ "#C0C0C0" ]
                        }
                    }
                },
                "itn": {
                    "$id": "#/properties/pool/properties/itn",
                    "type": "object",
                    "title": "ITN verification",
                    "description": "A proof of ownership for an established ITN pool brand.",
                    "required": [
                        "owner",
                        "witness"
                    ],
                    "properties": {
                        "owner": {
                            "$id": "#/properties/pool/properties/itn/properties/owner",
                            "type": "string",
                            "title": "the ITN pool owner public key",
                            "examples": [ "ed25519_pk1..." ]
                        },
                        "witness": {
                            "$id": "#/properties/pool/properties/itn/properties/witness",
                            "type": "string",
                            "title": "the secret key generated witness",
                            "examples": [ "ed25519_sig1..." ]
                        }
                    }
                }
            }
        }
    }
}
```

### JSON example

```json
{
  "serial": 870,
  "pool": {
    "id": "69579373ec20f2f82d2dc2360410350b308112f2939f92a",
    "country": "JPN",
    "status": "active",
    "contact": {
      "primary": "email",
      "email": "info@demopool.org",
      "facebook": "demopool12",
      "github": "demopooldev",
      "feed": "https://www.demopool.org/feed.xml",
      "telegram": "demopool",
      "twitter": "demopoolbird"
    },
    "media_assets": {
      "icon_png_64x64": "https://www.demopool.org/media/icon64.png",
      "logo_png": "https://www.demopool.org/media/logo.png",
      "logo_svg": "https://www.demopool.org/media/logo.svg",
      "color_fg": "#AABBCC",
      "color_bg": "#C0C0C0"
    },
    "itn": {
      "owner": "ed25519_pk1...",
      "witness": "ed25519_sig1..."
    }
  }
}
```



## Backwards compatibility

No fields are removed or changed in the current on chain metadata.  The new `ext...` fields are optional and not necessary to parse for any entities that do not need additional information about a pool

## Reference implementation

N/A

## Copyright

This file is documentation, and therefore subject to CC-BY-4.0 (and not subject to Apache 2.0).
