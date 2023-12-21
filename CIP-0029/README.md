---
CIP: 29
Title: Phase-1 Monetary Scripts Serialization Formats
Status: Active
Category: Tools
Authors:
  - Matthias Benkort <matthias.benkort@iohk.io>
Implementors:
  - IOG
Discussions:
  - https://github.com/cardano-foundation/CIPs/pull/117
Created: 2020-08-17
License: CC-BY-4.0
---

## Abstract

This specification describes how to serialize Phase-1 monetary scripts (a.k.a. _"native scripts"_) to various formats (JSON, CBOR) to facilitate inter-operability between applications.

## Motivation: why is this CIP necessary?

While the existence of scripts is well-known, and have an unambiguous on-chain representation. There's no agreed upon format for off-chain or higher-level interfaces for which a binary string is a poor fit. This CIP regroups both the on-chain binary format and other, more verbose, formats like JSON.

## Specification

This specification covers at present two serialization formats: JSON and CBOR. The CBOR matches exactly the on-chain representation and is extracted from the cardano-ledger-specs source code and put here as a convenient place to lookup while the source can change location over time.

### CBOR

The CBOR serialization format is given as a [CDDL specification in annexe](./phase-1-monetary-scripts.cddl). When a hash of the phase-1 monetary script is needed, it usually refers to a Blake2b-192 digest of the corresponding serialized script byte-string prefixed with a null byte: `\x00`.

### JSON

The JSON format is given as a [JSON schema in annexe](./phase-1-monetary-scripts.json). It is preferred in user interfaces such as command-lines or APIs, where some level of human inspection may be required.

### Notes

- Scripts may contain unbounded integers! Implementation parsing them, either from CBOR or JSON shall be prepared to handle possible big integers (>= 2^64).

### Test Vectors

```yaml
- json:
    { "type": "sig"
    , "keyHash": "00000000000000000000000000000000000000000000000000000000"
    }
  cbor:
    "8200581c00000000000000000000000000000000000000000000000000000000"
    
- json:
    { "type": "all"
    , "scripts":
      [ { "type": "sig"
        , "keyHash": "00000000000000000000000000000000000000000000000000000000"
        }
      , { "type": "any"
        , "scripts":
          [ { "type": "after"
            , "slot": 42
            }
          , { "type": "sig"
            , "keyHash": "00000000000000000000000000000000000000000000000000000001"
            }
          ]
        }
      ]
    }
  cbor:
    "8201828200581c000000000000000000000000000000000000000000000000000000008202828204182a8200581c00000000000000000000000000000000000000000000000000000001"

- json:
    { "type": "before"
    , "slot": 42
    }
  cbor:
    "8205182a"

- json:
    { "type": "atLeast"
    , "required": 2
    , "scripts":
      [ { "type": "sig", "keyHash": "00000000000000000000000000000000000000000000000000000000" }
      , { "type": "sig", "keyHash": "00000000000000000000000000000000000000000000000000000001" }
      , { "type": "sig", "keyHash": "00000000000000000000000000000000000000000000000000000002" }
      ]
    }
  cbor:
    "00830302838200581c000000000000000000000000000000000000000000000000000000008200581c000000000000000000000000000000000000000000000000000000018200581c00000000000000000000000000000000000000000000000000000002"
```

## Rationale: how does this CIP achieve its goals?

- The preimage for computing script hashes is prefixed with `\x00` to distinguish them from phase-2 monetary scripts (a.k.a Plutus Script) which are then prefixed with `\x01`. This is merely a discriminator tag.

- The current JSON format is based off the cardano-cli's format which has been used widely for minting tokens and is likely the most widely accepted format at the moment.

## Path to Active

### Acceptance Criteria

- [x] There exist official software releases supporting this serialization format:
  - [x] [cardano-cli](https://github.com/IntersectMBO/cardano-cli)
  - [x] [cardano-api](https://github.com/IntersectMBO/cardano-api)

### Implementation Plan

  - [x] Incorporating this serialization format into Cardano software libraries and command line tools.

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
