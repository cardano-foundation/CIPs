---
CIP: 76
Title: Hash-Checked Data
Author: Maksymilian 'zygomeb' Brodowicz <zygomeb@gmail.com>
Status: Draft
Type: Standards
Created: 2022-10-25
License: CC-BY-4.0
---

## Simple Summary / Abstract

Hashing data on-chain is quite expensive from a computational perspective. Currently, however, we are forced to use the `serializeData` primitive combined with a hashing function of our choice. It would be computationally beneficial to let the node hash the data before running the smart contracts, giving us only a guarantee that this mapping is correct, just as we do with Datums presently.

Therefore we propose extending the ScriptContext's txInfoData from just a mapping between DatumHash and Datum to a more universal mapping between BuiltinByteString and BuiltinData.

## Motivation / History

We can repeat the same motivation as [CIP 42](https://cips.cardano.org/cips/cip42/), and more broadly emphasizing the want to leverage complex data structures on chain. 

When presented with either a datum inside a datum or in general, data behind a hash, we are forced to spend a lot of computational resources to first serialize and then hash and then check for equality. This comes up quite often when implementing counter-double-satisfation measures (payment to script double satisfied).

## Specification

### Extending the ScriptContext

We change the field `txInfoData` to `[(BuiltinByteString, BuiltinData)]`. Nominally, this changes nothing as the `DatumHash` and `Datum` types are equivalent to these. Importantly however, we allow any pair to be pushed to this list, and the node will hash the `BuiltinData` to verify that it matches the `BuiltinByteString`.

It is worth noting that we can keep the types as they are now.

## Rationale

Just as we use nodes to be the source of truth on hash equality for datums we should encourage the use of them for more data, if it can be known statically.

## Backwards compatibility

The change needs a new language version to function safely

## Path to Active

The appropriate changes need to be made to the node code.

## Copyright

This CIP is licensed under Apache-2.0