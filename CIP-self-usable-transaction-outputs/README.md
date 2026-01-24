---
CIP: 172
Title: Self-Usable Transaction Outputs
Status: Proposed
Category: Ledger
Authors:
    - Carlos Tomé Cortiñas <carlos.tome-cortinas@iohk.io>
Implementors:
Discussions:
Created: 2026-01-15
License: CC-BY-4.0
---

## Abstract

We propose to allow transactions to reference scripts and data present on their
own outputs during validation.

## Motivation: why is this CIP necessary?

Transaction outputs carry scripts (via reference scripts) and/or data (via
inline datum). However, the Cardano ledger currently enforces a restriction
that prevents a transaction from satisfying its validation requirements using
scripts and data contained within its own outputs.

This restriction creates a specific inefficiency: if a transaction produces an
output containing a script or datum that is also required to validate that same
transaction, the transaction cannot utilize the copy present in the output.
Instead, the transaction must provide a redundant copy of the same script or
data (e.g., in the transaction witnesses).

This forced redundancy increases transaction size, and thus transaction fees,
directly inflating the costs incurred by users.

The key idea of this CIP is to remove this restriction, allowing transactions
to reference their own outputs for validation purposes.

### Use cases

#### Nested transactions: order-agnostic script sharing across a batch

The nested transactions CIP specifies that scripts are to be shared among all
sub- and top-level transactions within a batch (see [CIP, Changes to
Transaction
Validity](https://github.com/carlostome/CIPs/tree/master/CIP-0118#changes-to-transaction-validity)).

With the current restriction, this requirement can only be partially achieved
by sharing scripts either (1) from transaction witnesses or (2) via reference
inputs that point to outputs of sub-transactions in the same batch which have
already been applied to the UTxO state.

With the proposed change in this CIP, the requirement can be achieved allowing
scripts to be shared directly from transaction outputs, regardless of which
sub- or top-level transaction they appear in. This eliminates the dependency on
processing order and enables more flexible script sharing within the batch.

## Specification

There is an [Agda
specification](https://github.com/IntersectMBO/formal-ledger-specifications/tree/carlos/usable-outputs)
prototype of the proposed changes (for Conway).

### Changes to the ledger logic

- The function `txscripts` needs to be modified to include scripts from `txouts`.
- The function `getDatum` needs to be modified to include data from `txouts`.

## Rationale: how does this CIP achieve its goals?

The current ledger logic prohibits transactions from accessing their own
outputs during validation. However, this restriction comes at the cost of
redundancy when the same script or datum serves dual purposes: being included
in an output for future use and being required for current validation.

This CIP achieves its goal by relaxing this restriction so that validation may
reference scripts and data committed in the transaction body’s outputs, which
removes the need to carry duplicate copies in witnesses and reduces transaction
size and fees.

## Path to Active

### Acceptance Criteria

- Fully implemented in Cardano node

### Implementation Plan

- TODO

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
