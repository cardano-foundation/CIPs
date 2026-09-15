---
CIP: 167
Title: Remove isValid from transactions
Category: Ledger
Status: Proposed
Authors:
  - Teodora Danciu <teodora.danciu@iohk.io>
  - Alexey Kuleshevich <alexey.kuleshevich@iohk.io>
Implementors: N/A
Discussions:
  - Original PR: https://github.com/cardano-foundation/CIPs/pull/1089
Created: 2025-09-01
License: CC-BY-4.0
---

## Abstract

We propose removing the `isValid` boolean from the CBOR encoding of standalone transactions (e.g. for mempool).
Within blocks, transactions continue to carry an `is_valid` flag, but as the trailing element of each transaction, set by the block producer (see CIP-0176); it is not part of the serialization used by the transaction author.

## Motivation: Why is this CIP necessary?

The `isValid` flag in standalone transaction CBOR is not intrinsic to the protocol or to the ledger-consensus boundary:
  * it is not signed by the transaction creator, so anyone can set it to any value they like.
  * for block validation: the value that is used is the one that was set by the consensus protocol
  * for remote submissions from untrusted nodes: the node ignores the incoming flag, evaluates the transaction as if `isValid = True`, if phase-2 fails for that reason alone - admits it to the mempool with `isValid = False` so collateral can be collected.

The only remaining use is local submission from trusted clients (like cardano-cli), where the node reads the flag to avoid unintended collateral burn.
This use is important, but perhaps the transaction bytes are not the best layer to encode that intent.

Removing the flag simplifies encoding/decoding, slightly reduces on-wire size, and eliminates semantic ambiguity. Futhermore, because the flag is non-witnessed (excluded from the transaction ID), it cannot be trusted; keeping it invites inconsistency and confusion.

## Specification

Currently, a stand-alone transaction is serialized like this:

```cddl
transaction = [transaction_body, transaction_witness_set, bool, auxiliary_data/ nil]
```

The proposal is to change it to:
```cddl
mempool_transaction =
  [transaction_body, transaction_witness_set, auxiliary_data/ nil]
  / [transaction_body, transaction_witness_set, true, auxiliary_data/ nil]
```

The second alternative exists only for backwards compatibility during the transition to the era that adopts this CIP (transactions in a mempool at the hard fork boundary may still carry the flag): the legacy `is_valid` position is accepted on decoding, but only with the value `true`.
Encoders must always produce the first alternative.
In the following era the legacy alternative will be removed, so it is strongly recommended to encode transactions without the flag.

Inside a block, a transaction is serialized with a trailing `is_valid` flag appended by the block producer, after all the fields supplied by the transaction author:

```cddl
block_transaction =
  [transaction_body, transaction_witness_set, auxiliary_data/ nil, bool]
```

The in-block format is specified by CIP-0176; it is shown here only to clarify the relationship between the two formats.

## Rationale: How does this CIP achieve its goals?

Removing the `isValid` flag from standalone transaction serialization simplifies the wire format without changing consensus or ledger semantics.

The trusted local client submission use case might be better expressed in a different way (for example, as a Node-to-Client submit parameter), rather than embedded in the transaction bytes.

Keeping the block-producer-supplied `is_valid` flag as the trailing element of the in-block transaction (rather than as a block-level index list) keeps the author-supplied fields as a contiguous prefix and provides a natural position for future block-producer-supplied fields, such as the proposed `feeChangeAmount`.

## Path to Active

### Acceptance Criteria

- [ ] Transaction serializers and deserializers in [cardano-ledger](https://github.com/IntersectMBO/cardano-ledger) are implemented such that they follow the cddl specification described above, and reflected in the cddl specs
- [ ] The feature is integrated into [cardano-node](https://github.com/IntersectMBO/cardano-node) with necessary adjustments made to [ouroboros-consensus](https://github.com/IntersectMBO/ouroboros-consensus) and released as part of the Dijkstra era hard fork

### Implementation Plan

The implementation of this CIP should not proceed without an assessment of the potential impact on all the components that deserialise standalone transactions.

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
