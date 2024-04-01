---
CPS: 11
Title: Universal JSON Encoding for Domain Types
Status: Open
Category: Tools
Authors:
    - Vladimir Kalnitsky <vladimir@mlabs.city>
Proposed Solutions: []
Discussions:
    - https://github.com/cardano-foundation/cips/pulls/742
Created: 2024-01-10
License: CC-BY-4.0
---

## Abstract

dApps require the use of communication protocols that facilitate data transfer between:

- query layer providers and dApps
- wallets and dApps
- wallets and query layer providers
- dApp frontends and backends
- different dApps
- Cardano blockchain indexers and their API consumers

Usually these protocols include a specification of Cardano domain types, i.e. ledger block and all of its sub-components.

## Problem

Cardano domain types have canonical CDDL definitions (for every era), but when it comes to use in web apps, where JSON is the universally accepted format, there is no definite standard.

As a result, software solutions are incompatible with each other, and dApp developers are forced to write code for conversions that could in principle be unnecessary, because the semantics of different JSON layouts are often the same. In particular, this problem is very real when offchain libraries need to provide support for different query layer providers (examples: [Lucid](https://lucid.spacebudz.io/docs/getting-started/choose-provider/), [Mesh.js](https://meshjs.dev/providers), [cardano-transaction-lib](https://github.com/Plutonomicon/cardano-transaction-lib/blob/develop/doc/runtime.md), [Atlas](https://haddock.atlas-app.io/GeniusYield-Providers.html)).

The [initiative](https://github.com/cardano-foundation/CIPs/pull/625) to standardize query layers on Cardano is currently blocked due to absence of a standardized JSON data schema. However, such a schema would be useful in contexts other than query layers, which is the reason why this CPS is separate.

## Use cases

- dApp developers want to have a definite encoding of JSON data, so that they don't need to specify the format themselves
- dApp developers want to be sure they will be able to reuse data coming from different sources (third parties) without format changes
- dApp developers want to provide external APIs that must be easily consumable
- Query layer developers want to make sure their APIs will be easily consumable
- Multiple service/product owners, who utilize different competing JSON encoding conventions want to converge to a single convention

## Goals

The main goal of a CIP that corresponds to this CPS is to construct a JSON schema that explicitly defines all domain types for the current era. This CIP should evolve in sync with the Cardano Ledger CDDL specification, so that when a new era spec comes out, a new JSON schema file is provided with the needed modifications.

Optional goals:

- Providing support for eras older than the current one. The goal of the spec is to be used across different software solutions that run on Cardano mainnet. Compatibility with past ledger versions should be provided only as long as there is a real need.

Non-goals:

- Maintain roundtrip property for conversion between JSON and CBOR: this is impossible, because CBOR uses varying binary encodings for arrays and maps.
- Provide support for different eras in a single schema. Specifications should be kept in separate files.
- Maintain correctness of signatures for transactions encoded as JSON: this is impossible in the general case, because signature validity depends on binary layout determined by CBOR encoding. Conventions may apply to preserve signatures, but they are out of scope of the standard, because they apply to CBOR encoding, not JSON.
- Making the encoding as compact as possible (reducing encoded data size)

## Open Questions

- What's the best approach to specifying address formats in json-schema format?
- Should the schema be concerned with different representations of addresses (bech32 vs. hex)?
- How can we programmatically or manually test the constructed schema file?
- How to encode long integer arithmetic? Some JSON encoding implementations simply refuse to handle long integers, e.g. [CSL](https://github.com/Emurgo/cardano-serialization-lib/blob/4a35ef11fd5c4931626c03025fe6f67743a6bdf9/rust/src/plutus.rs#L1370).
- [RFC8949](https://www.rfc-editor.org/rfc/rfc8949.html#name-converting-data-between-cbo) and [RFC8610](https://datatracker.ietf.org/doc/html/rfc8610#appendix-E) contain recommendations for developers who want to maintain interoperability with JSON. Can we apply these in our context?

## Copyright

This CPS is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
