---
CIP: XXXX
Title: Non-segregated Block Body Serialization
Category: Ledger
Authors:
  - Teodora Danciu <teodora.danciu@iohk.io>
  - Alexey Kuleshevich <alexey.kuleshevich@iohk.io>
Implementors: N/A
Status: Proposed
Discussions:
  - https://github.com/IntersectMBO/cardano-ledger/issues/5046
  - https://github.com/cardano-foundation/CIPs/pull/1084
Created: 2025-07-30
License: CC-BY-4.0
---

## Abstract

We propose changing the CBOR encoding of a block body from a segregated layout to a plain sequence of transactions.
Current layout: all transaction bodies are concatenated and encoded first, followed by their witness sets, then followed by auxiliary-data hashes, and finally followed by validity flags.
Proposed layout: each transaction is serialized in full before the next transaction is written to the stream.

## Motivation: why is this CIP necessary?

Segregated serialization of [CIP-0118? | Nested Transactions](https://github.com/cardano-foundation/CIPs/pull/862) would be challenging both to specify and implement.
Separating and concatenating components across nested and non-nested transactions introduces complexity that is error-prone and potentially inefficient, as it may require tracking offsets and performing additional buffering and copying at runtime.

Currently, segregated serialization also complicates the logic used by Consensus to estimate transaction sizes when selecting transactions to fit within a block. Switching to a format where full transactions are encoded sequentially would simplify this process.

Considering - in hindsight - the original motivation for adopting segregated serialization rather than the more natural and predictable way of serializing a list of transactions - it's unclear whether it provides any real benefit.
The intent was to enable static validation of a transaction without decoding its witnesses. However, this benefit conflicts with the need for strict field evaluation, which is essential to prevent space leaks caused by retaining the original block bytes for an indeterminate period.

Moreover, the current segregated layout, if it was used for its intended purpose mentioned above, conflicts with incremental decoding of blocks being received over the wire - for which there is a need.
Our decoders consume bytes on demand until the entire BlockBody structure is exhausted. As a result, the node decodes the full block - including all witness data - in a single pass. The segregated format therefore provides no practical benefit for partial or streaming validation.

Moreover, time spent doing deserialization amounts to a small fraction of the whole time spent applying the whole block to the ledger state, even when it is done without validating transactions.

A significant benefit that we will get from the proposed change is reduction in complexity, both for the cardano-node core components, as well as various tools that handles chain data in some capacity.

## Specification

Currently, a block is serialized like this:

```cddl
block =
  [ header
  , transaction_bodies       : [* transaction_body]
  , transaction_witness_sets : [* transaction_witness_set]
  , auxiliary_data_set       : {* transaction_index => auxiliary_data}
  , invalid_transactions     : [* transaction_index]
  ]
```

The proposal is to change it to:
```cddl
block =
  [ header
  , block_body
  ]

block_body =
  [ transactions : [* transaction]
  , invalid_transactions : [* transaction_index]
  ]

transaction =
  [  transaction_body, transaction_witness_set, true, auxiliary_data/ nil
  // transaction_body, transaction_witness_set, auxiliary_data/ nil
  ]
```

Note that we propose keeping invalid transaction indices separately, because:
  * the `isValid` flag - which determines validity -  is controlled by the block producing node, not by the transaction creator;
  * it's more efficient: we serialize indices only for invalid transactions, which are a small minority.

## Rationale: how does this CIP achieve its goals?

Serializing transactions in sequence directly supports more complex constructs - such as nested transactions - by eliminating the need to coordinate disjointed segments across different levels of structure.

### Ecosystem Impact

This change only impacts tools that work directly with block (de)serialization, such as alternative nodes and indexers. These tools make up a relatively small part of the Cardano tooling ecosystem. For them, the change is beneficial: without it, nested transactions would lead to a much more complex and error-prone block serialization format.

No transaction construction, serialization, or submission tooling is affected by this CIP.

## Path to Active

### Acceptance Criteria

- [ ] Block serializers and deserializers in [cardano-ledger](https://github.com/IntersectMBO/cardano-ledger) are implemented such that they follow the cddl specification described above, and reflected in the cddl specs
- [ ] The feature is integrated into [cardano-node](https://github.com/IntersectMBO/cardano-node) and released as part of the Dijkstra era hard fork

### Implementation Plan

The implementation of this CIP should not proceed without an assessment of the potential impact on all the components that deserialise blocks.
Leios and Peras R&D teams should also be aware of these changes.

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
