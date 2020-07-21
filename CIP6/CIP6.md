---
CIP: 6
Title: Extended Metadata
Authors: Mike Fullman <mike@fullman.net>, Markus Gufler <gufmar@gmail.com>
Comments-URI: 
Status: Draft
Type: Standards
Created: 2020-07-20
License: Apache-2.0
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

#### On Chain referenced metadata file
We define one more line for the on chain referenced metadata file that references another json file on a url with the extended metadata.  The proposed metadata is as follows:

| key           | Value                                | Rules  |
| ---           | ---                                  | ---  |
|  `ticker`       | Pool ticker.  uppercase              | 5 Characters Maximum, Uppercase letters and numbers  |
|  `description` | Pool Description.  Text that describes the pool | 50 Characters Maximum |
|  `homepage` | A website URL for the pool| 64 Characters Maximum, must be a valid URL |
|  `name` | A name for the pool | 50 Characters Maximum |
|  `extended` | A url for extended metadata| Optional, 64 Characters Maximum, must be a valid URL |

#### Extended Metadata
The file located at the URL for extended data is a json compliant text file with the following fields:

| key           | Value                                | Rules |
| ---           | ---                                  | --- |
| `serial` | set to YYYYMMDDxx on every update | regex: `\d{10}` |
|  `itn.owner` | ITN pool public key | regex: `ed25519_pk1[a-z0-9]{58}` |
|  `itn.witness` | Mainnet pool id signed by the ITN pool owner secret key | regex: `ed25519_sig1[a-z0-9]{109}` |

Since this extended metadata file has no checksum and can be updated at any time by the pool operator, a **serial number** is useful to easily identify updates.

The purpose of this first (**itn**) extension is the verifiable linking of an ITN pool ticker with its counterpart in Mainnet to identify fraudulent duplicates.



#### Extended Metadata Schema

```
{
    "$schema": "http://json-schema.org/draft-07/schema",
    "$id": "http://example.com/example.json",
    "type": "object",
    "title": "The root schema",
    "description": "The root schema comprises the entire JSON document.",
    "default": {},
    "examples": [
        {
            "serial": 2020072001,
            "itn": {
                "owner": "ed25519_pk1...",
                "witness": "ed25519_sig1..."
            },
            "contact": {
                "abuse": "abuse@pooldomain.org",
                "support": "help@pooldomain.org",
                "social": {
                    "discord": "discordUser#1234",
                    "telegram": "@telegramUser",
                    "facebook": "facebookUser",
                    "reddit": "redditUser",
                    "twitter": "@twitterAccount"
                }
            },
            "CI": {
                "color-main": "#RRGGBB",
                "logo-vector": "<?xml version='1.0' ?><!DOCTYPE svg  PUBLIC '-//W3C//DTD SVG 1.1//EN'  'http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd'><svg enable-background='new 0 0 24 24' height='24px' id='Layer_1' version='1.1' viewBox='0 0 24 24' width='24px' xml:space='preserve' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'><g><path d='M12,0C5.4,0,0,5.4,0,12s5.4,12,12,12s12-5.4,12-12S18.6,0,12,0z M12,22C6.5,22,2,17.5,2,12S6.5,2,12,2s10,4.5,10,10   S17.5,22,12,22z'/><path d='M12,9c-1.1,0-2,0.9-2,2c0,0.6,0.3,1.1,0.7,1.5C10.3,12.9,10,13.4,10,14c0,1.1,0.9,2,2,2s2-0.9,2-2c0-0.6-0.3-1.1-0.7-1.5   c0.4-0.4,0.7-0.9,0.7-1.5C14,9.9,13.1,9,12,9z M12,15c-0.6,0-1-0.4-1-1s0.4-1,1-1s1,0.4,1,1S12.6,15,12,15z M12,12   c-0.6,0-1-0.4-1-1s0.4-1,1-1s1,0.4,1,1S12.6,12,12,12z'/><path d='M12,6c-3.3,0-6,2.7-6,6s2.7,6,6,6s6-2.7,6-6S15.3,6,12,6z M12,17c-2.8,0-5-2.2-5-5s2.2-5,5-5s5,2.2,5,5S14.8,17,12,17z'/></g></svg>"
            }
        }
    ],
    "required": [
        "serial"
    ],
    "additionalProperties": true,
    "properties": {
        "serial": {
            "$id": "#/properties/serial",
            "type": "integer",
            "title": "serial number",
            "description": "YYYYMMDDxx set on every update",
            "default": 0,
            "examples": [
                2020072001
            ],
            "pattern": "`\\d{10}`"
        },
        "itn": {
            "$id": "#/properties/itn",
            "type": "object",
            "title": "ITN relations",
            "description": "Link incentivised-testnet and mainnet tickers",
            "default": {},
            "examples": [
                {
                    "owner": "ed25519_pk1...",
                    "witness": "ed25519_sig1..."
                }
            ],
            "required": [],
            "additionalProperties": true,
            "properties": {
                "owner": {
                    "$id": "#/properties/itn/properties/owner",
                    "type": "string",
                    "title": "owner public key",
                    "description": "",
                    "default": "",
                    "examples": [
                        "ed25519_pk1..."
                    ],
                    "pattern": "`ed25519_pk1[a-z0-9]{58}`"
                },
                "witness": {
                    "$id": "#/properties/itn/properties/witness",
                    "type": "string",
                    "title": "signed pool id",
                    "description": "Mainnet pool id signed by the ITN pool owner secret key",
                    "default": "",
                    "examples": [
                        "ed25519_sig1..."
                    ],
                    "pattern": "`ed25519_sig1[a-z0-9]{109}`"
                }
            }
        },
        "contact": {
            "$id": "#/properties/contact",
            "type": "object",
            "title": "The contact schema",
            "description": "additional contact options",
            "default": {},
            "examples": [
                {
                    "abuse": "abuse@pooldomain.org",
                    "support": "help@pooldomain.org",
                    "social": {
                        "discord": "discordUser#1234",
                        "telegram": "@telegramUser",
                        "facebook": "facebookUser",
                        "reddit": "redditUser",
                        "twitter": "@twitterAccount"
                    }
                }
            ],
            "required": [],
            "additionalProperties": true,
            "properties": {
                "abuse": {
                    "$id": "#/properties/contact/properties/abuse",
                    "type": "string",
                    "title": "abuse contact",
                    "description": "email address",
                    "default": "",
                    "examples": [
                        "abuse@pooldomain.org"
                    ]
                },
                "support": {
                    "$id": "#/properties/contact/properties/support",
                    "type": "string",
                    "title": "support contact",
                    "description": "email address",
                    "default": "",
                    "examples": [
                        "help@pooldomain.org"
                    ]
                },
                "social": {
                    "$id": "#/properties/contact/properties/social",
                    "type": "object",
                    "title": "social channels",
                    "description": "optional social channels.",
                    "default": {},
                    "examples": [
                        {
                            "discord": "discordUser#1234",
                            "telegram": "@telegramUser",
                            "facebook": "facebookUser",
                            "reddit": "redditUser",
                            "twitter": "@twitterAccount"
                        }
                    ],
                    "required": [],
                    "additionalProperties": true,
                    "properties": {
                        "discord": {
                            "$id": "#/properties/contact/properties/social/properties/discord",
                            "type": "string",
                            "title": "discord user",
                            "description": ".",
                            "default": "",
                            "examples": [
                                "discordUser#1234"
                            ]
                        },
                        "telegram": {
                            "$id": "#/properties/contact/properties/social/properties/telegram",
                            "type": "string",
                            "title": "telegram user",
                            "description": ".",
                            "default": "",
                            "examples": [
                                "@telegramUser"
                            ]
                        },
                        "facebook": {
                            "$id": "#/properties/contact/properties/social/properties/facebook",
                            "type": "string",
                            "title": "facebook user",
                            "description": ".",
                            "default": "",
                            "examples": [
                                "facebookUser"
                            ]
                        },
                        "reddit": {
                            "$id": "#/properties/contact/properties/social/properties/reddit",
                            "type": "string",
                            "title": "reddit user",
                            "description": ".",
                            "default": "",
                            "examples": [
                                "redditUser"
                            ]
                        },
                        "twitter": {
                            "$id": "#/properties/contact/properties/social/properties/twitter",
                            "type": "string",
                            "title": "twitter account",
                            "description": ".",
                            "default": "",
                            "examples": [
                                "@twitterAccount"
                            ]
                        }
                    }
                }
            }
        },
        "CI": {
            "$id": "#/properties/CI",
            "type": "object",
            "title": "The CI schema",
            "description": "corporate identity and design",
            "default": {},
            "examples": [
                {
                    "color-main": "#RRGGBB",
                    "logo-vector": "<?xml version='1.0' ?><!DOCTYPE svg  PUBLIC '-//W3C//DTD SVG 1.1//EN'  'http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd'><svg enable-background='new 0 0 24 24' height='24px' id='Layer_1' version='1.1' viewBox='0 0 24 24' width='24px' xml:space='preserve' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'><g><path d='M12,0C5.4,0,0,5.4,0,12s5.4,12,12,12s12-5.4,12-12S18.6,0,12,0z M12,22C6.5,22,2,17.5,2,12S6.5,2,12,2s10,4.5,10,10   S17.5,22,12,22z'/><path d='M12,9c-1.1,0-2,0.9-2,2c0,0.6,0.3,1.1,0.7,1.5C10.3,12.9,10,13.4,10,14c0,1.1,0.9,2,2,2s2-0.9,2-2c0-0.6-0.3-1.1-0.7-1.5   c0.4-0.4,0.7-0.9,0.7-1.5C14,9.9,13.1,9,12,9z M12,15c-0.6,0-1-0.4-1-1s0.4-1,1-1s1,0.4,1,1S12.6,15,12,15z M12,12   c-0.6,0-1-0.4-1-1s0.4-1,1-1s1,0.4,1,1S12.6,12,12,12z'/><path d='M12,6c-3.3,0-6,2.7-6,6s2.7,6,6,6s6-2.7,6-6S15.3,6,12,6z M12,17c-2.8,0-5-2.2-5-5s2.2-5,5-5s5,2.2,5,5S14.8,17,12,17z'/></g></svg>"
                }
            ],
            "required": [],
            "additionalProperties": true,
            "properties": {
                "color-main": {
                    "$id": "#/properties/CI/properties/color-main",
                    "type": "string",
                    "title": "RGB color",
                    "description": "main theme color",
                    "default": "",
                    "examples": [
                        "#RRGGBB"
                    ]
                },
                "logo-vector": {
                    "$id": "#/properties/CI/properties/logo-vector",
                    "type": "string",
                    "title": "vector logo",
                    "description": "svg defined vector logo",
                    "default": "",
                    "examples": [
                        "<?xml version='1.0' ?><!DOCTYPE svg  PUBLIC '-//W3C//DTD SVG 1.1//EN'  'http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd'><svg enable-background='new 0 0 24 24' height='24px' id='Layer_1' version='1.1' viewBox='0 0 24 24' width='24px' xml:space='preserve' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'><g><path d='M12,0C5.4,0,0,5.4,0,12s5.4,12,12,12s12-5.4,12-12S18.6,0,12,0z M12,22C6.5,22,2,17.5,2,12S6.5,2,12,2s10,4.5,10,10   S17.5,22,12,22z'/><path d='M12,9c-1.1,0-2,0.9-2,2c0,0.6,0.3,1.1,0.7,1.5C10.3,12.9,10,13.4,10,14c0,1.1,0.9,2,2,2s2-0.9,2-2c0-0.6-0.3-1.1-0.7-1.5   c0.4-0.4,0.7-0.9,0.7-1.5C14,9.9,13.1,9,12,9z M12,15c-0.6,0-1-0.4-1-1s0.4-1,1-1s1,0.4,1,1S12.6,15,12,15z M12,12   c-0.6,0-1-0.4-1-1s0.4-1,1-1s1,0.4,1,1S12.6,12,12,12z'/><path d='M12,6c-3.3,0-6,2.7-6,6s2.7,6,6,6s6-2.7,6-6S15.3,6,12,6z M12,17c-2.8,0-5-2.2-5-5s2.2-5,5-5s5,2.2,5,5S14.8,17,12,17z'/></g></svg>"
                    ]
                }
            }
        }
    }
}
```



## Backwards compatibility

No fields are removed or changed in the current on chain metadata.  The new field `extended` is optional and not necessary to parse for any entities that do not need additional information about a pool

## Reference implementation

N/A

## Copyright

This CIP is licensed under Apache-2.0.
