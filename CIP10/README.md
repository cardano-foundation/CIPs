---
CIP: 10
Title: Transaction Metadata Label Registry
Authors: Sebastien Guillemot <sebastien@emurgo.io>
Comments-URI: https://forum.cardano.org/t/cip10-transaction-metadata-label-registry/41746
Status: Draft
Type: Standards
Created: 2020-10-31
License: CC-BY-4.0
---

## Abstract

Cardano transaction metadata forces metadata entries to namespace their content using an unsigned integer key. This specification is a registry of which use cases has allocated which number to avoid collisions.

## Terminology

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

## Motivation

The top level of the transaction metadata CBOR object is a mapping of `transaction_metadatum_label` to the actual metadata where the `transaction_metadatum_label` represents an (ideally unique) key for a metadata use case. This allows enables the following:

1) Fast lookup for nodes to query all transactions containing metadata that uses a specific key
2) Allows a single transaction to include multiple metadata entries for different standards

Creating a registry for `transaction_metadatum_label` values has the following benefit:

1) It makes it easy for developers to know which `transaction_metadatum_label` to use to query their node if looking for transactions that use a standard
2) It makes it easy to avoid collisions with other standards that use transaction metadata

## Specification

These are the registered `transaction_metadatum_label` values

transaction_metadatum_label | description
----------------------------|-----------------------
0 - 15                      | reserved*
1967                        | nut.link metadata oracles registry
1968                        | nut.link metadata oracles data points
65536 - 131071              | reserved - private use

\* It's best to avoid using `0` or any a similar number like `1` that other people are very likely to use. Prefer instead to generate a random number

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode)
