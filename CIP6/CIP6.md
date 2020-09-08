---
CIP: 6
Title: Extended Metadata
Authors: Mike Fullman <mike@fullman.net>, Markus Gufler <gufmar@gmail.com>
Comments-URI:
Status: Draft
Type: Standards
Created: 2020-07-20
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
            "logo_vector": "https://mycoolpool.com/logo.svg"
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
            "support": "help@pooldomain.org",
            "telegram_admin":"coolpool"
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
            "sex": "2"
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
    "pool": {
        "id": "0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f",
        "country": "UK",
        "os": "LINUX",
        "infrastructure": "AWS",
        "status": "act",
        "saturated_recommend":"0a0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f"
    }

}
```

#### Extended Metadata Schema

see incorporated file [schema.json](schema.json)

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

This file is documentation, and therefore subject to CC-BY-4.0 (and not subject to Apache 2.0).
