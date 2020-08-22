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
The file located at the URL for extended data is a json compliant text file with the following top level fields:

| key           | Description                                |
| ---           | ---                                  |
| `serial` | set to YYYYMMDDxx on every update |
|  `itn` | ITN pool validation data |
|  `info` | Corporate image, contacts and about details |
| `pools` | Pool details |

Since this extended metadata file has no checksum and can be updated at any time by the pool operator, a **serial number** is useful to easily identify updates.

The purpose of this first (**itn**) extension is the verifiable linking of an ITN pool ticker with its counterpart in Mainnet to identify fraudulent duplicates.

#### Complete Extended Metadata Example
```
{
    "serial": 2020072001,
    "itn": {
        "owner": "ed25519_pk1...",
        "witness": "ed25519_sig1..."
    },
    "info": {
        "CI": {
            "logo_url_png_icon_64x64": "https://mycoolpool.com/icon.png",
            "logo_url_png_logo": "https://mycoolpool.com/logo.png",
            "color_main": "#RRGGBB",
            "logo_vector": "<?xml version='1.0' ?><!DOCTYPE svg  PUBLIC '-//W3C//DTD SVG 1.1//EN'  'http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd'><svg enable-background='new 0 0 24 24' height='24px' id='Layer_1' version='1.1' viewBox='0 0 24 24' width='24px' xml:space='preserve' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'><g><path d='M12,0C5.4,0,0,5.4,0,12s5.4,12,12,12s12-5.4,12-12S18.6,0,12,0z M12,22C6.5,22,2,17.5,2,12S6.5,2,12,2s10,4.5,10,10   S17.5,22,12,22z'/><path d='M12,9c-1.1,0-2,0.9-2,2c0,0.6,0.3,1.1,0.7,1.5C10.3,12.9,10,13.4,10,14c0,1.1,0.9,2,2,2s2-0.9,2-2c0-0.6-0.3-1.1-0.7-1.5   c0.4-0.4,0.7-0.9,0.7-1.5C14,9.9,13.1,9,12,9z M12,15c-0.6,0-1-0.4-1-1s0.4-1,1-1s1,0.4,1,1S12.6,15,12,15z M12,12   c-0.6,0-1-0.4-1-1s0.4-1,1-1s1,0.4,1,1S12.6,12,12,12z'/><path d='M12,6c-3.3,0-6,2.7-6,6s2.7,6,6,6s6-2.7,6-6S15.3,6,12,6z M12,17c-2.8,0-5-2.2-5-5s2.2-5,5-5s5,2.2,5,5S14.8,17,12,17z'/></g></svg>"
        },
        "social": {
            "twitter_handle": "coolpool",
            "telegram_handle": "coolpool",
            "facebook_handle": "coolpool",
            "youtube_handle": "coolpool",
            "twitch_handle": "coolpool",
            "discord_handle": "coolpool",
            "github_handle": "coolpool"
        },
        "contact": {
            "abuse": "abuse@pooldomain.org",
            "support": "help@pooldomain.org"
        },
        "company": {
            "name": "Company Name",
            "addr": "Street, Number",
            "city": "London",
            "country": "UK",
            "company_id": "123456789",
            "vat_id": "GB123456789"
        },
        "operator": {
            "country": "UK",
            "sex": "FEMALE"
        },
        "about": {
            "team_affiliation": [
                "ISPPA",
                "Cardano Ambassador"
            ],
            "me": "Long description of me",
            "server": "long description of server details",
            "company": "long description of company details"
        },
        "rss": "https://mycoolpool.com/xml/poolrss.xml"
    },
    "pools": [{
            "id": "0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f",
            "country": "UK",
            "os": "LINUX",
            "infrastructure": "AWS",
            "status": "act",
            "saturated_recommend":"0a0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f"
        },
        {
            "id": "0a0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f",
            "country": "UK",
            "os": "LINUX",
            "infrastructure": "AWS",
            "status": "act",
            "saturated_recommend":"0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f"
        }
    ]
}
```

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
            "info": {
                "CI": {
                    "logo_url_png_icon_64x64": "https://mycoolpool.com/icon.png",
                    "logo_url_png_logo": "https://mycoolpool.com/logo.png",
                    "color_main": "#RRGGBB",
                    "logo_vector": "<?xml version='1.0' ?><!DOCTYPE svg  PUBLIC '-//W3C//DTD SVG 1.1//EN'  'http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd'><svg enable-background='new 0 0 24 24' height='24px' id='Layer_1' version='1.1' viewBox='0 0 24 24' width='24px' xml:space='preserve' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'><g><path d='M12,0C5.4,0,0,5.4,0,12s5.4,12,12,12s12-5.4,12-12S18.6,0,12,0z M12,22C6.5,22,2,17.5,2,12S6.5,2,12,2s10,4.5,10,10   S17.5,22,12,22z'/><path d='M12,9c-1.1,0-2,0.9-2,2c0,0.6,0.3,1.1,0.7,1.5C10.3,12.9,10,13.4,10,14c0,1.1,0.9,2,2,2s2-0.9,2-2c0-0.6-0.3-1.1-0.7-1.5   c0.4-0.4,0.7-0.9,0.7-1.5C14,9.9,13.1,9,12,9z M12,15c-0.6,0-1-0.4-1-1s0.4-1,1-1s1,0.4,1,1S12.6,15,12,15z M12,12   c-0.6,0-1-0.4-1-1s0.4-1,1-1s1,0.4,1,1S12.6,12,12,12z'/><path d='M12,6c-3.3,0-6,2.7-6,6s2.7,6,6,6s6-2.7,6-6S15.3,6,12,6z M12,17c-2.8,0-5-2.2-5-5s2.2-5,5-5s5,2.2,5,5S14.8,17,12,17z'/></g></svg>"
                },
                "social": {
                    "twitter_handle": "coolpool",
                    "telegram_handle": "coolpool",
                    "facebook_handle": "coolpool",
                    "youtube_handle": "coolpool",
                    "twitch_handle": "coolpool",
                    "discord_handle": "coolpool",
                    "github_handle": "coolpool"
                },
                "contact": {
                    "abuse": "abuse@pooldomain.org",
                    "support": "help@pooldomain.org"
                },
                "company": {
                    "name": "Company Name",
                    "addr": "Street, Number",
                    "city": "London",
                    "country": "UK",
                    "company_id": "123456789",
                    "vat_id": "GB123456789"
                },
                "operator": {
                    "country": "UK",
                    "sex": "FEMALE"
                },
                "about": {
                    "team_affiliation": [
                        "ISPPA",
                        "Cardano Ambassador"
                    ],
                    "me": "Long description of me",
                    "server": "long description of server details",
                    "company": "long description of company details"
                },
                "rss": "https://mycoolpool.com/xml/poolrss.xml"
            },
            "pools": [
                {
                    "id": "0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f",
                    "country": "UK",
                    "os": "LINUX",
                    "infrastructure": "AWS",
                    "status": "act",
                    "saturated_recommend": "0a0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f"
                },
                {
                    "id": "0a0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f",
                    "country": "UK",
                    "os": "LINUX",
                    "infrastructure": "AWS",
                    "status": "act",
                    "saturated_recommend": "0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f"
                }
            ]
        }
    ],
    "required": [
        "serial",
    ],
    "properties": {
        "serial": {
            "default": 0,
            "description": "YYYYMMDDxx set on every update",
            "examples": [
                2020072001
            ],
            "title": "Serial Number",
            "pattern": "`\\d{10}`"
        },
        "itn": {
            "default": {},
            "description": "Link incentivised-testnet and mainnet tickers",
            "examples": [
                {
                    "owner": "ed25519_pk1...",
                    "witness": "ed25519_sig1..."
                }
            ],
            "required": [
                "owner",
                "witness"
            ],
            "title": "ITN relations",
            "properties": {
                "owner": {
                    "default": "",
                    "description": "Public key of ITN pool",
                    "examples": [
                        "ed25519_pk1..."
                    ],
                    "title": "owner public key"
                },
                "witness": {
                    "default": "",
                    "description": "Mainnet pool id signed by the ITN pool owner secret key",
                    "examples": [
                        "ed25519_sig1..."
                    ],
                    "title": "signed pool id"
                }
            },
            "additionalProperties": true
        },
        "info": {
            "$id": "#/properties/info",
            "type": "object",
            "title": "The info schema",
            "description": "An explanation about the purpose of this instance.",
            "default": {},
            "examples": [
                {
                    "CI": {
                        "logo_url_png_icon_64x64": "https://mycoolpool.com/icon.png",
                        "logo_url_png_logo": "https://mycoolpool.com/logo.png",
                        "color_main": "#RRGGBB",
                        "logo_vector": "<?xml version='1.0' ?><!DOCTYPE svg  PUBLIC '-//W3C//DTD SVG 1.1//EN'  'http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd'><svg enable-background='new 0 0 24 24' height='24px' id='Layer_1' version='1.1' viewBox='0 0 24 24' width='24px' xml:space='preserve' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'><g><path d='M12,0C5.4,0,0,5.4,0,12s5.4,12,12,12s12-5.4,12-12S18.6,0,12,0z M12,22C6.5,22,2,17.5,2,12S6.5,2,12,2s10,4.5,10,10   S17.5,22,12,22z'/><path d='M12,9c-1.1,0-2,0.9-2,2c0,0.6,0.3,1.1,0.7,1.5C10.3,12.9,10,13.4,10,14c0,1.1,0.9,2,2,2s2-0.9,2-2c0-0.6-0.3-1.1-0.7-1.5   c0.4-0.4,0.7-0.9,0.7-1.5C14,9.9,13.1,9,12,9z M12,15c-0.6,0-1-0.4-1-1s0.4-1,1-1s1,0.4,1,1S12.6,15,12,15z M12,12   c-0.6,0-1-0.4-1-1s0.4-1,1-1s1,0.4,1,1S12.6,12,12,12z'/><path d='M12,6c-3.3,0-6,2.7-6,6s2.7,6,6,6s6-2.7,6-6S15.3,6,12,6z M12,17c-2.8,0-5-2.2-5-5s2.2-5,5-5s5,2.2,5,5S14.8,17,12,17z'/></g></svg>"
                    },
                    "social": {
                        "twitter_handle": "coolpool",
                        "telegram_handle": "coolpool",
                        "facebook_handle": "coolpool",
                        "youtube_handle": "coolpool",
                        "twitch_handle": "coolpool",
                        "discord_handle": "coolpool",
                        "github_handle": "coolpool"
                    },
                    "contact": {
                        "abuse": "abuse@pooldomain.org",
                        "support": "help@pooldomain.org"
                    },
                    "company": {
                        "name": "Company Name",
                        "addr": "Street, Number",
                        "city": "London",
                        "country": "UK",
                        "company_id": "123456789",
                        "vat_id": "GB123456789"
                    },
                    "operator": {
                        "country": "UK",
                        "sex": "FEMALE"
                    },
                    "about": {
                        "team_affiliation": [
                            "ISPPA",
                            "Cardano Ambassador"
                        ],
                        "me": "Long description of me",
                        "server": "long description of server details",
                        "company": "long description of company details"
                    },
                    "rss": "https://mycoolpool.com/xml/poolrss.xml"
                }
            ],
            "properties": {
                "CI": {
                    "default": {},
                    "description": "All details related to corporate image",
                    "examples": [
                        {
                            "logo_url_png_icon_64x64": "https://mycoolpool.com/icon.png",
                            "logo_url_png_logo": "https://mycoolpool.com/logo.png",
                            "color_main": "#RRGGBB",
                            "logo_vector": "<?xml version='1.0' ?><!DOCTYPE svg  PUBLIC '-//W3C//DTD SVG 1.1//EN'  'http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd'><svg enable-background='new 0 0 24 24' height='24px' id='Layer_1' version='1.1' viewBox='0 0 24 24' width='24px' xml:space='preserve' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'><g><path d='M12,0C5.4,0,0,5.4,0,12s5.4,12,12,12s12-5.4,12-12S18.6,0,12,0z M12,22C6.5,22,2,17.5,2,12S6.5,2,12,2s10,4.5,10,10   S17.5,22,12,22z'/><path d='M12,9c-1.1,0-2,0.9-2,2c0,0.6,0.3,1.1,0.7,1.5C10.3,12.9,10,13.4,10,14c0,1.1,0.9,2,2,2s2-0.9,2-2c0-0.6-0.3-1.1-0.7-1.5   c0.4-0.4,0.7-0.9,0.7-1.5C14,9.9,13.1,9,12,9z M12,15c-0.6,0-1-0.4-1-1s0.4-1,1-1s1,0.4,1,1S12.6,15,12,15z M12,12   c-0.6,0-1-0.4-1-1s0.4-1,1-1s1,0.4,1,1S12.6,12,12,12z'/><path d='M12,6c-3.3,0-6,2.7-6,6s2.7,6,6,6s6-2.7,6-6S15.3,6,12,6z M12,17c-2.8,0-5-2.2-5-5s2.2-5,5-5s5,2.2,5,5S14.8,17,12,17z'/></g></svg>"
                        }
                    ],
                    "title": "Corporate Image Details",
                    "properties": {
                        "logo_url_png_icon_64x64": {
                            "default": "",
                            "description": "A small logo, 64x64 max size",
                            "examples": [
                                "https://mycoolpool.com/icon.png"
                            ],
                            "pattern": "https?://(?:[a-z0-9\\-]+\\.)+[a-z]{2,6}(?:/[^/#?]+)+\\.png$",
                            "title": "The logo_url_png_icon_64x64"
                        },
                        "logo_url_png_logo": {
                            "default": "",
                            "description": "A pool logo",
                            "examples": [
                                "https://mycoolpool.com/logo.png"
                            ],
                            "pattern": "https?://(?:[a-z0-9\\-]+\\.)+[a-z]{2,6}(?:/[^/#?]+)+\\.png$",
                            "title": "A url to a pool logo"
                        },
                        "color_main": {
                            "default": "",
                            "description": "HTML RGB color code with corporate background theme color",
                            "examples": [
                                "#RRGGBB"
                            ],
                            "title": "Background color",
                            "pattern": "^[0-9a-fA-F]{6}$"
                        },
                        "logo_vector": {
                            "default": "",
                            "description": "svg defined vector logo",
                            "examples": [
                                "<?xml version='1.0' ?><!DOCTYPE svg  PUBLIC '-//W3C//DTD SVG 1.1//EN'  'http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd'><svg enable-background='new 0 0 24 24' height='24px' id='Layer_1' version='1.1' viewBox='0 0 24 24' width='24px' xml:space='preserve' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'><g><path d='M12,0C5.4,0,0,5.4,0,12s5.4,12,12,12s12-5.4,12-12S18.6,0,12,0z M12,22C6.5,22,2,17.5,2,12S6.5,2,12,2s10,4.5,10,10   S17.5,22,12,22z'/><path d='M12,9c-1.1,0-2,0.9-2,2c0,0.6,0.3,1.1,0.7,1.5C10.3,12.9,10,13.4,10,14c0,1.1,0.9,2,2,2s2-0.9,2-2c0-0.6-0.3-1.1-0.7-1.5   c0.4-0.4,0.7-0.9,0.7-1.5C14,9.9,13.1,9,12,9z M12,15c-0.6,0-1-0.4-1-1s0.4-1,1-1s1,0.4,1,1S12.6,15,12,15z M12,12   c-0.6,0-1-0.4-1-1s0.4-1,1-1s1,0.4,1,1S12.6,12,12,12z'/><path d='M12,6c-3.3,0-6,2.7-6,6s2.7,6,6,6s6-2.7,6-6S15.3,6,12,6z M12,17c-2.8,0-5-2.2-5-5s2.2-5,5-5s5,2.2,5,5S14.8,17,12,17z'/></g></svg>"
                            ],
                            "title": "vector logo"
                        }
                    },
                    "additionalProperties": true
                },
                "social": {
                    "$id": "#/properties/info/properties/social",
                    "type": "object",
                    "title": "The social schema",
                    "description": "An explanation about the purpose of this instance.",
                    "default": {},
                    "examples": [
                        {
                            "twitter_handle": "coolpool",
                            "telegram_handle": "coolpool",
                            "facebook_handle": "coolpool",
                            "youtube_handle": "coolpool",
                            "twitch_handle": "coolpool",
                            "discord_handle": "coolpool",
                            "github_handle": "coolpool"
                        }
                    ],

                    "properties": {
                        "twitter_handle": {
                            "default": "",
                            "description": "Twitter handle without leading @",
                            "examples": [
                                "coolpool"
                            ],
                            "title": "The twitter_handle schema",
                            "pattern": "^(\\w){1,15}$"
                        },
                        "telegram_handle": {
                            "default": "",
                            "description": "An explanation about the purpose of this instance.",
                            "examples": [
                                "coolpool"
                            ],
                            "title": "The telegram_handle schema"

                        },
                        "facebook_handle": {
                            "default": "",
                            "description": "An explanation about the purpose of this instance.",
                            "examples": [
                                "coolpool"
                            ],
                            "title": "The facebook_handle schema",
                            "pattern": "^(\\w){1,55}$"
                        },
                        "youtube_handle": {
                            "$id": "#/properties/info/properties/social/properties/youtube_handle",
                            "type": "string",
                            "title": "The youtube_handle schema",
                            "description": "An explanation about the purpose of this instance.",
                            "default": "",
                            "examples": [
                                "coolpool"
                            ]
                        },
                        "twitch_handle": {
                            "$id": "#/properties/info/properties/social/properties/twitch_handle",
                            "type": "string",
                            "title": "The twitch_handle schema",
                            "description": "An explanation about the purpose of this instance.",
                            "default": "",
                            "examples": [
                                "coolpool"
                            ]
                        },
                        "discord_handle": {
                            "$id": "#/properties/info/properties/social/properties/discord_handle",
                            "type": "string",
                            "title": "The discord_handle schema",
                            "description": "An explanation about the purpose of this instance.",
                            "default": "",
                            "examples": [
                                "coolpool"
                            ]
                        },
                        "github_handle": {
                            "$id": "#/properties/info/properties/social/properties/github_handle",
                            "type": "string",
                            "title": "The github_handle schema",
                            "description": "An explanation about the purpose of this instance.",
                            "default": "",
                            "examples": [
                                "coolpool"
                            ]
                        }
                    },
                    "additionalProperties": true
                },
                "contact": {
                    "$id": "#/properties/info/properties/contact",
                    "type": "object",
                    "title": "The contact schema",
                    "description": "An explanation about the purpose of this instance.",
                    "default": {},
                    "examples": [
                        {
                            "abuse": "abuse@pooldomain.org",
                            "support": "help@pooldomain.org"
                        }
                    ],

                    "properties": {
                        "abuse": {
                            "default": "",
                            "description": "Abuse contact email",
                            "examples": [
                                "abuse@pooldomain.org"
                            ],
                            "title": "Abuse Contact email"
                        },
                        "support": {
                            "default": "",
                            "description": "Support contact email",
                            "examples": [
                                "help@pooldomain.org"
                            ],
                            "title": "Support Contact Email"
                        }
                    },
                    "additionalProperties": true
                },
                "company": {
                    "$id": "#/properties/info/properties/company",
                    "type": "object",
                    "title": "Company Details",
                    "description": "Contact details of company",
                    "default": {},
                    "examples": [
                        {
                            "name": "Company Name",
                            "addr": "Street, Number",
                            "city": "London",
                            "country": "UK",
                            "company_id": "123456789",
                            "vat_id": "GB123456789"
                        }
                    ],
                    "properties": {
                        "name": {
                            "$id": "#/properties/info/properties/company/properties/name",
                            "type": "string",
                            "title": "Company Name",
                            "description": "Company Name.",
                            "default": "",
                            "examples": [
                                "Company Name"
                            ]
                        },
                        "addr": {
                            "$id": "#/properties/info/properties/company/properties/addr",
                            "type": "string",
                            "title": "Company ddress",
                            "description": "Company ddress",
                            "default": "",
                            "examples": [
                                "5534 HappyPool Lane"
                            ]
                        },
                        "city": {
                            "$id": "#/properties/info/properties/company/properties/city",
                            "type": "string",
                            "title": "Company City",
                            "description": "Company City",
                            "default": "",
                            "examples": [
                                "London"
                            ]
                        },
                        "country": {
                            "$id": "#/properties/info/properties/company/properties/country",
                            "type": "string",
                            "title": "Company Country",
                            "description": "ISO 3166-2 2-letter country code",
                            "default": "",
                            "examples": [
                                "UK"
                            ]
                        },
                        "company_id": {
                            "$id": "#/properties/info/properties/company/properties/company_id",
                            "type": "string",
                            "title": "company id",
                            "description": "company id",
                            "default": "",
                            "examples": [
                                "123456789"
                            ]
                        },
                        "vat_id": {
                            "$id": "#/properties/info/properties/company/properties/vat_id",
                            "type": "string",
                            "title": "company vat id",
                            "description": "company vat id",
                            "default": "",
                            "examples": [
                                "GB123456789"
                            ]
                        }
                    },
                    "additionalProperties": true
                },
                "operator": {
                    "$id": "#/properties/info/properties/operator",
                    "type": "object",
                    "title": "The operator schema",
                    "description": "An explanation about the purpose of this instance.",
                    "default": {},
                    "examples": [
                        {
                            "country": "UK",
                            "sex": "0"
                        }
                    ],
                    "required": [
                        "country",
                        "sex"
                    ],
                    "properties": {
                        "country": {
                            "$id": "#/properties/info/properties/operator/properties/country",
                            "type": "string",
                            "title": "The country schema",
                            "description": "ISO 3166-2 2-letter country code",
                            "default": "",
                            "examples": [
                                "UK"
                            ]
                        },
                        "sex": {
                            "$id": "#/properties/info/properties/operator/properties/sex",
                            "type": "string",
                            "title": "The sex schema",
                            "description": "ISO/IEC 5218 sex",
                            "default": "",
                            "examples": [
                                "1"
                            ]
                        }
                    },
                    "additionalProperties": true
                },
                "about": {
                    "$id": "#/properties/info/properties/about",
                    "type": "object",
                    "title": "The about schema",
                    "description": "An explanation about the purpose of this instance.",
                    "default": {},
                    "examples": [
                        {
                            "team_affiliation": [
                                "ISPPA",
                                "Cardano Ambassador"
                            ],
                            "me": "Long description of me",
                            "server": "long description of server details",
                            "company": "long description of company details"
                        }
                    ],
                    "properties": {
                        "team_affiliation": {
                            "$id": "#/properties/info/properties/about/properties/team_affiliation",
                            "type": "array",
                            "title": "Team Affiliations",
                            "description": "Case insensitive affiliations.  Matching performed on entire string.",
                            "default": [],
                            "examples": [
                                [
                                    "ISPPA",
                                    "Cardano Ambassador"
                                ]
                            ],
                            "additionalItems": true,
                            "items": {
                                "$id": "#/properties/info/properties/about/properties/team_affiliation/items",
                                "anyOf": [
                                    {
                                        "$id": "#/properties/info/properties/about/properties/team_affiliation/items/anyOf/0",
                                        "type": "string",
                                        "title": "Team Name",
                                        "description": "Case insensitive affiliations.  Matching performed on entire string.",
                                        "default": "",
                                        "examples": [
                                            "ISPPA",
                                            "Cardano Ambassador"
                                        ]
                                    }
                                ]
                            }
                        },
                        "me": {
                            "$id": "#/properties/info/properties/about/properties/me",
                            "type": "string",
                            "title": "Long Description Me",
                            "description": "Long Description.  valid HTML tags are <b><p><br>",
                            "default": "",
                            "examples": [
                                "Long description of me"
                            ]
                        },
                        "server": {
                            "$id": "#/properties/info/properties/about/properties/server",
                            "type": "string",
                            "title": "Long Description Server",
                            "description": "Long Description.  valid HTML tags are <b><p><br>",
                            "default": "",
                            "examples": [
                                "long description of server details"
                            ]
                        },
                        "company": {
                            "$id": "#/properties/info/properties/about/properties/company",
                            "type": "string",
                            "title": "Long Description Company",
                            "description": "Long Description.  valid HTML tags are <b><p><br>",
                            "default": "",
                            "examples": [
                                "long description of company details"
                            ]
                        }
                    },
                    "additionalProperties": true
                },
                "rss": {
                    "$id": "#/properties/info/properties/rss",
                    "type": "string",
                    "title": "Rss Feed",
                    "description": "URL to an RSS feed",
                    "default": "",
                    "examples": [
                        "https://mycoolpool.com/xml/poolrss.xml"
                    ]
                }
            },
            "additionalProperties": true
        },
        "pools": {
            "$id": "#/properties/pools",
            "type": "array",
            "title": "Pool List",
            "description": "Long Description.",
            "default": [],
            "examples": [
                [
                    {
                        "id": "0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f",
                        "country": "UK",
                        "os": "LINUX",
                        "infrastructure": "AWS",
                        "status": "act",
                        "saturated_recommend": "0a0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f"
                    },
                    {
                        "id": "0a0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f",
                        "country": "UK",
                        "os": "LINUX",
                        "infrastructure": "AWS",
                        "status": "act",
                        "saturated_recommend": "0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f"
                    }
                ]
            ],
            "additionalItems": true,
            "items": {
                "$id": "#/properties/pools/items",
                "anyOf": [
                    {
                        "$id": "#/properties/pools/items/anyOf/0",
                        "type": "object",
                        "title": "Pool",
                        "description": "",
                        "default": {},
                        "examples": [
                            {
                                "id": "0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f",
                                "country": "UK",
                                "os": "LINUX",
                                "infrastructure": "AWS",
                                "status": "act",
                                "saturated_recommend": "0a0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f"
                            }
                        ],
                        "required": [
                            "id",
                        ],
                        "properties": {
                            "id": {
                                "$id": "#/properties/pools/items/anyOf/0/properties/id",
                                "type": "string",
                                "title": "The poolid",
                                "description": "Valid Mainnet Pool Id (hex format)",
                                "default": "",
                                "examples": [
                                    "0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f"
                                ]
                            },
                            "country": {
                                "$id": "#/properties/pools/items/anyOf/0/properties/country",
                                "type": "string",
                                "title": "Pool country",
                                "description": "ISO 3166-2 2-letter country code",
                                "default": "",
                                "examples": [
                                    "UK"
                                ]
                            },
                            "os": {
                                "$id": "#/properties/pools/items/anyOf/0/properties/os",
                                "type": "string",
                                "title": "Pool Operating System",
                                "description": "Pool Operating System",
                                "default": "",
                                "examples": [
                                    "LINUX",
                                    "OSX",
                                    "WIN",
                                    "FREEBSD",
                                    "UNDISCLOSED"
                                ]
                            },
                            "infrastructure": {
                                "$id": "#/properties/pools/items/anyOf/0/properties/infrastructure",
                                "type": "string",
                                "title": "Pool Infrastructure",
                                "description": "Pool infrastructure Platform",
                                "default": "",
                                "examples": [
                                    "AWS",
                                    "GOOGLE",
                                    "AZURE",
                                    "DIGITALOCEAN",
                                    "BAREMETALL",
                                    "BAREMETALH",
                                    "OVH",
                                    "HETZNER",
                                    "VULTR",
                                    "GODADDY",
                                    "ARUBA",
                                    "HOSTINGER",
                                    "OTHERVPS",
                                    "LPCSBC",
                                    "UNDISCLOSED"
                                ]
                            },
                            "status": {
                                "$id": "#/properties/pools/items/anyOf/0/properties/status",
                                "type": "string",
                                "title": "Pool Status",
                                "description": "Pool Current Status",
                                "default": "",
                                "examples": [
                                    "ACT","RET","OFF","EXP","DNU"
                                ]
                            },
                            "saturated_recommend": {
                                "$id": "#/properties/pools/items/anyOf/0/properties/saturated_recommend",
                                "type": "string",
                                "title": "Saturated Recommend",
                                "description": "If the pool is saturated recommend this pool",
                                "default": "",
                                "examples": [
                                    "0a0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f"
                                ]
                            }
                        },
                        "additionalProperties": true
                    }
                ]
            }
        }
    },
    "additionalProperties": true
}
```


## Infrastructure Mapping
```
[
    {"Code": "aws", "Name": "Amazon Cloud"},
    {"Code": "google", "Name": "Google Cloud"},
    {"Code": "azure", "Name": "Microsoft Cloud"},
    {"Code": "digitalocean", "Name": "Digital Ocean"},
    {"Code": "baremetall", "Name": "Bare Metal Server(local)"},
    {"Code": "baremetalh", "Name": "Bare Metal Server(hosted)"},
    {"Code": "ovh", "Name": "OVH Cloud"},
    {"Code": "hetzner", "Name": "Hetzner"},
    {"Code": "vultr", "Name": "Vultr"},
    {"Code": "godaddy", "Name": "Go Daddy"},
    {"Code": "aruba", "Name": "Aruba"},
    {"Code": "hostinger", "Name": "Hostinger"},
    {"Code": "othervps", "Name": "Other VPS"},
    {"Code": "lpcsbc", "Name": "Low Power/Cost SBC (pi, rockspi, etc)"},
    {"Code": "undisclosed", "Name": "Undisclosed"}
]
```

## Operating System Mapping
```
[
    {"Code": "linux", "Name": "Linux"},
    {"Code": "osx", "Name": "Apple OSX"},
    {"Code": "win", "Name": "Windows"},
    {"Code": "freebsd", "Name": "FreeBSD"},
    {"Code": "undisclosed", "Name": "Undisclosed"}
]
```

## Pool Status Mapping
```
[
    {"Code": "act","Name": "Active"},
    {"Code": "ret","Name": "Retired"},
    {"Code": "off","Name": "Offline for Maintenance"},
    {"Code": "exp","Name": "Experimental"},
    {"Code": "dnu","Name": "Do Not Delegate To This Pool"}
]
```
## Backwards compatibility

No fields are removed or changed in the current on chain metadata.  The new field `extended` is optional and not necessary to parse for any entities that do not need additional information about a pool

## Reference implementation

N/A

## Copyright

This CIP is licensed under Apache-2.0.
