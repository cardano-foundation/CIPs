---
CIP: 10
Title: Transaction Metadata Label Registry
Status: Active
Category: Metadata
Authors:
  - Sebastien Guillemot <sebastien@emurgo.io>
Implementors: N/A
Discussions:
  - https://github.com/cardano-foundation/CIPs/pull/34
  - https://forum.cardano.org/t/cip10-transaction-metadata-label-registry/41746
Created: 2020-10-31
License: CC-BY-4.0
---

## Abstract

Cardano transaction metadata forces metadata entries to namespace their content using an unsigned integer key. This specification is a registry of which use cases has allocated which number to avoid collisions.

## Motivation: why is this CIP necessary?

The top level of the transaction metadata CBOR object is a mapping of `transaction_metadatum_label` to the actual metadata where the `transaction_metadatum_label` represents an (ideally unique) key for a metadata use case. This allows enables the following:

1) Fast lookup for nodes to query all transactions containing metadata that uses a specific key
2) Allows a single transaction to include multiple metadata entries for different standards

## Specification

### Terminology

Transaction metadata refers to an optional CBOR object in every transaction since the start of the Shelley era. It is defined as the follow CDDL data structure

```
transaction_metadatum =
    { * transaction_metadatum => transaction_metadatum }
  / [ * transaction_metadatum ]
  / int
  / bytes .size (0..64)
  / text .size (0..64)

transaction_metadatum_label = uint

transaction_metadata =
  { * transaction_metadatum_label => transaction_metadatum }
```

### Structure

These are the reserved `transaction_metadatum_label` values

`transaction_metadatum_label` | description
----------------------------  | -----------------------
0 - 15                        | reserved\*
65536 - 131071                | reserved - private use

For the registry itself, please see [registry.json](./registry.json) in the machine-readable format. Please open your pull request against
this file.

\* It's best to avoid using `0` or any a similar number like `1` that other people are very likely to use. Prefer instead to generate a random number

## Rationale: how does this CIP achieve its goals?

Creating a registry for `transaction_metadatum_label` values has the following benefit:

1) It makes it easy for developers to know which `transaction_metadatum_label` to use to query their node if looking for transactions that use a standard
2) It makes it easy to avoid collisions with other standards that use transaction metadata

## Path to Active

### Acceptance Criteria

- [x] Consistent, long-term use by Cardano implementors of the metadata label registry by all applications requiring a universally acknowledged metadata label.
- [x] Consistent, long-term use in the CIP editing process: tagging, verifying, and merging new label requirements.

### Implementation Plan

- [x] Confirmed interest and cooperation in this metadata labelling standard and its `registry.json` convention by Cardano implementors: including NFT creators, data aggregators, and sidechains.

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode)
