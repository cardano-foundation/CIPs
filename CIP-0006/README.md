---
CIP: 6
Title: Stake Pool Extended Metadata
Status: Active
Category: Tools
Authors:
  - Markus Gufler <gufmar@gmail.com>
  - Mike Fullman <mike@fullman.net>
Implementors:
  - pooltool.io
  - cexplorer.io
Discussions:
  - https://github.com/cardano-foundation/CIPs/pull/15
Created: 2020-07-20
License: CC-BY-4.0
---

## Abstract

This CIP defines the concept of extended metadata for pools that is referenced from the pool registration data stored on chain.

## Motivation: Why is this CIP necessary?

As the ecosystem around Cardano stake pools proliferate so will the desire to slice, organize and search pool information dynamically.  Currently the metadata referenced on chain provides 512 bytes that can be allocated across the four information categories ([delegation-design-specification Section 4.2)](https://github.com/IntersectMBO/cardano-ledger/releases/latest/download/shelley-delegation.pdf):

| key           | Value                                |  Rules  |
| ---           | ---                                  |  ---  |
|  `ticker` | Pool ticker.  uppercase | 5 Characters Maximum, Uppercase letters and numbers |
|  `description` | Pool Description.  Text that describes the pool | 50 Characters Maximum |
|  `homepage` | A website URL for the pool  | 64 Characters Maximum, must be a valid URL |
|  `name` | A name for the pool | 50 Characters Maximum |

Many additional attributes can be envisioned for future wallets, pool explorers, and information aggregators.  The proposal below outlines an initial strategy for capturing this extended metadata.

## Specification

> **Note** Updated: 2020-11-24 2nd key-pair for validation 2021-02-08 json schema

### On Chain referenced (main) metadata file

We define two more fields for the on chain referenced metadata file that references another JSON file on a URL with the extended metadata.  The proposed metadata is as follows:

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

## Rationale: How does this CIP achieve its goals?

In the following we describe a first minimal version of the extended JSON file format.

Since this extended metadata file can be updated at any time by the pool operator, a **serial number** is useful for consuming applications and services to identify updates.

There are main thematic sections with respective subordinate data fields:

- the **itn** section is about the verifiable linking of an ITN pool ticker with its counterpart in Mainnet to identify fraudulent duplicates. (already used as not standardized extension)
- the **pool** section contains additional information about the pool instance
  - the pool.**contact** section contains information for additional information and contact data 
  - the pool.**media_assets** section contains additional information about the pools media files and colors
  - the pool.**itn** section is an optional section for ITN pool operators  

The full schema is given in annexe as [schema.json][]

<details>
  <summary>See JSON example</summary>

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
</details>

### Backwards compatibility

No fields are removed or changed in the current on chain metadata.  The new `ext...` fields are optional and not necessary to parse for any entities that do not need additional information about a pool

## Path to Active

### Acceptance Criteria

- [x] There exist at least two explorers which make use of this extended metadata structure or very close equivalent:
  - [x] pooltool.io
  - [x] cexplorer.io

### Implementation Plan

- [x] Provide direct support for this specification in stake pool explorers and other tools.

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).

[schema.json]: https://raw.githubusercontent.com/cardano-foundation/CIPs/master/CIP-0006/schema.json
