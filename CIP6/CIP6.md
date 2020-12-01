---
CIP: 6
Title: Extended Metadata
Authors: Markus Gufler <gufmar@gmail.com>, Mike Fullman <mike@fullman.net>
Comments-URI:
Status: Draft
Type: Standards
Created: 2020-07-20 original draft
Updated: 2020-11-24 2nd key-pair for validation
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
| `extHashUrl` | A URL with the extended metadata hash | optional, 128 Characters Maximum, must be a valid URL |
| `extVkey` | the public Key for verification | optional, 68 Characters |

In order to include the additional ext Field data, we suggest increasing the maximum size of the main metadata file from currently 512 to 1024 bytes.

### Extended Metadata - flexible but validable

In difference to the main metadata, the extended metadata should be updateable without having to use the cold key of the pool and without having to perform an on-chain transaction. The consumer of these data should still have the possibility to verify the authenticity of the data.

The operator notes all his additional pool information in the extended metadata (`extData.json`).

We propose the pool operator generate a new public-secret key-pair (`extData.skey` and `extData.vkey`)

```shell
cardano-cli shelley node key-gen 
  --cold-verification-key-file extData.vkey 
  --cold-signing-key-file extData.skey 
  --operational-certificate-issue-counter-file extData.counter
```

Then a new (not available yet) `cardano-cli` command generate the signed hash (`extData.sign`) .

```shell
cardano-cli shelley stake-pool rawdata-hash
  --raw-metadata-file extData.json
  --signing-key-file extData.skey
  --out-file extData.sign
```

The operator now:

- has the `extData.json` and `extData.sign` files
- will publish them at some https:// URL (probably same host as the main metadata)
- use the `extData.vkey` string and the two extend file URLs to re-register the main metadata

This re-registration of the main metadata file with the `extData.vkey` and the two URLs is only necessary once. Afterwards, the operator can update his extended metadata at any time, generate the new signature and put both files online.

### Extended Metadata structure

In the following we describe a first minimal version of the extended Json file format

Since this extended metadata file can be updated at any time by the pool operator, a **serial number** is useful to easily identify updates.

There are main thematic sections with respective subordinate data fields:

- the **itn** section is about the verifiable linking of an ITN pool ticker with its counterpart in Mainnet to identify fraudulent duplicates. (already used as not standardized extension)
- the **pool** section contains additional information about the pool instance
- the **operator** section contains additional information about the people operating this pool
- the **owner** section contains additional information about the pool owner(s)



ToDo: describe the initial basic format, and a standard on how future CIPs need to approach an evolution of the extended metadata schema



#### Extended Metadata Schema
```
work in progress
```



#### Infrastructure Mapping
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

#### Operating System Mapping
```
[
    {"Code": "linux", "Name": "Linux"},
    {"Code": "osx", "Name": "Apple OSX"},
    {"Code": "win", "Name": "Windows"},
    {"Code": "freebsd", "Name": "FreeBSD"},
    {"Code": "undisclosed", "Name": "Undisclosed"}
]
```

#### Pool Status Mapping
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

No fields are removed or changed in the current on chain metadata.  The new `ext...` fields are optional and not necessary to parse for any entities that do not need additional information about a pool

## Reference implementation

N/A

## Copyright

This file is documentation, and therefore subject to CC-BY-4.0 (and not subject to Apache 2.0).
