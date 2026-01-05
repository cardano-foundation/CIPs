---
CIP: 17
Title: Cardano Delegation Portfolio
Status: Inactive (abandoned for lack of interest)
Category: Tools
Authors:
  - Matthias Benkort <matthias.benkort@cardanofoundation.org>
Implementors: []
Discussions:
  - https://github.com/cardano-foundation/CIPs/pull/82
Created: 2020-04-02
License: CC-BY-4.0
---

## Abstract

This document details a common format for sharing Cardano delegation portfolio across various tools and wallets. 

## Motivation: why is this CIP necessary?

Stakeholders have indicated the desire to split their stake in various sizes and delegate to n pools from a single wallet/mnemonic. Albeit there are no monetary incentive for users to do this, the desire to drive decentralisation is sufficiently prevalent to justify it. Furthermore, stakeholders want to introduce a certain social element to this activity by sharing their delegation portfolio with other stakeholders. This specification should help to standardize the representation of portfolios across tools for more interoperability. 

## Specification

### Overview

We'll use JSON as a data format for it is commonly used and supported across many programming languages, and is also relatively readable on itself. Portfolios should abide by the [JSON schema given in appendix](CIP-0017.json). 

At minima, a portfolio should cover a list of delegation choices (pools and weights) and have a human-readable name for easier identification. 

### Weights

For each pool, we demand a `weight` which can capture a certain stake proportion within the portfolio. The value is an integer, and relative to other weights in the portfolio. For example, a portfolio with two pools and respective weights of `1` and `2` means that we expect users to assign twice more stake to the second pool than the first. Fundamentally, this means that for every 3 Ada, 1 Ada should go to the first pool, and 2 Ada should go to the second. Note that this is equivalent to having weights of `10`/`20` or `14` / `28`. Weights are ultimately interpreted as fractions.

Portfolios which treat all stake pools equally should use the same weight (e.g. `1`) for each pool. 

### Example

```json
{ "name": "Metal 🤘"
, "description": "Pools supporting Metal music across the world."
, "pools": 
  [ { "id": "d59123f4dce7c62fa74bd37a759c7ba665dbabeb28f08b4e5d4802ca"
    , "name": "Dark Tranquility"
    , "ticker": "DARK"
    , "weight": 42
    }
  , { "id": "5f3833027fe8c8d63bc5e75960d9a22df52e41bdf62af5b689663c50"
    , "ticker": "NITRO"
    , "weight": 14
    }
  , { "id": "a16abb03d87b86f30bb743aad2e2504b126286fe744d3d2f6a0b4aec"
    , "name": "Loudness"
    , "ticker": "LOUD"
    , "weight": 37
    }
  , { "id": "9f9bdee3e053e3102815b778db5ef8d55393f7ae83b36f906f4c3a47"
    , "weight": 25
    }
  ]
}
```

## Rationale: how does this CIP achieve its goals?

1. JSON is widely used, widely supported and quite lightweight. Makes for a reasonable choice of data format.

2. Using JSON schema for validation is quite common when dealing with JSON and it's usually sufficiently precise to enable good interoperability. 

3. The portfolio should only capture information that are not subject to radical change. That is, stake pools parameters like pledge or fees are excluded since they can be changed fairly easily using on-chain certificate updates. 

4. The JSON schema doesn't enforce any `additionalProperties: false` for neither the top-level object definition nor each stake pool objects. This allows for open extension of the objects with custom fields at the discretion of applications implementing this standard. The semantic of well-known properties specified in this document is however fixed.

5. Since the portfolio format isn't _immediately user-facing_, we favor base16 over bech32 for the pool id's encoding for there's better support and tooling for the former.

### Backwards Compatibility

#### Adafolio

The format used by [Adafolio](https://adafolio.com) share a lot of similarities with the proposed format in this CIP. In order to power its frontend user interface, Adafolio contains however several fields which we consider _too volatile_ and unnecessary to the definition of a portfolio. This doesn't preclude the format used by Adafolio as a valid portfolio format (see also point (4). in the rationale above).

The only point of incompatibility regards the `pool_id` field (in Adafolio) vs the `id` field (in this proposal) which we deem more consistent with regards to other field. 

## Path to Active

### Acceptance Criteria

- [ ] At least one pair of applications (wallets, explorers or other tools) together support the following:
  - [ ] generation of the specified portfolio file format
  - [ ] interpretation and use of the specified portfolio file format

### Implementation Plan

- [ ] Provide a reference implementation and/or parsing library to read and/or write files in this schema.

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
