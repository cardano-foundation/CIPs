---
CIP: XXXX
Title: Remove the `isValid` flag from standalone transaction serialization

Category: Ledger
Authors:
  - Teodora Danciu <teodora.danciu@iohk.io>
  - Alexey Kuleshevich <alexey.kuleshevich@iohk.io>
Implementors: N/A
Status: Proposed
Discussions:
  - https://github.com/cardano-foundation/CIPs/pull/xxx
Created: 2025-09-01
License: CC-BY-4.0
---

## Abstract

We propose removing the `isValid` boolean from the CBOR encoding of standalone transactions (e.g. for mempool).
This would not affect the serialization of the transactions within blocks.

## Motivation: why is this CIP necessary?

The `isValid` flag in standalone transaction CBOR is not intrinsic to the protocol or to the lendger-consensus boundary:
  * for block validation: the flag is not involved
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
transaction = [transaction_body, transaction_witness_set, auxiliary_data/ nil]
```

## Rationale: how does this CIP achieve its goals?

Removing the `isValid` flag from standalone transaction serialization simplifies the wire format without changing consensus or ledger semantics.

The trusted local client submission use case might be better expressed in a different way (for example, as a Node-to-Client submit parameter), rather than embedded in the transaction bytes.

## Path to Active

### Acceptance Criteria

- [ ] Transaction serializers and deserializers in [cardano-ledger](https://github.com/IntersectMBO/cardano-ledger) are implemented such that they follow the cddl specification described above, and reflected in the cddl specs
- [ ] The feature is integrated into [cardano-node](https://github.com/IntersectMBO/cardano-node) with necessary adjustments made to [ouroboros-consensus](https://github.com/IntersectMBO/ouroboros-consensus) and released as part of the Dijkstra era hard fork

### Implementation Plan

The implementation of this CIP should not proceed without an assessment of the potential impact on all the components that deserialise standalone transactions.

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).