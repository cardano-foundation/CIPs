---
CIP: 156
Title: Plutus Core Builtin Function - multiIndexArray
Category: Plutus
Status: Proposed
Authors:
    - Yura Lazaryev <yuriy.lazaryev@iohk.io>
    - Philip DiSarro <info@anastasialabs.com>
Implementors: []
Discussions:
    - https://github.com/cardano-foundation/CIPs/pull/1050
Created: 2025-07-07
License: CC-BY-4.0
---

## Abstract

We propose adding a new builtin function, `multiIndexArray`, to Plutus Core. This function takes a list of integer indices and an array, returning a list of the array elements at those positions in the specified order.

## Motivation: why is this CIP necessary?

Plutus Core arrays (CIP-0138) support O(1) individual lookup via `indexArray`. However, extracting multiple elements requires repeated calls to `indexArray`, which:

1. Increases script size and execution cost.
2. Complicates on-chain logic for batching lookups or reordering.
3. Prevents efficient bulk access and traversal in a user-defined order.

A single `multiIndexArray` call reduces code and cost overhead by batching lookups and delivering elements in the desired sequence.

## Specification

Add the following builtin function:

```haskell
multiIndexArray :: forall a. List Integer -> Array a -> List a
```

- **Inputs**:
  1. A `List Integer` of zero-based indices, in the order elements should be retrieved.
  2. An `Array a` to index.
- **Output**: A `List a` containing the elements at the specified indices, in the same order. In case of repeated indices, the same element is returned multiple times.
- **Error handling**: If any index is out of bounds (< 0 or ≥ lengthOfArray), the entire call fails with the same error semantics as `indexArray`.
- **Cost**: Time and memory usage are linear in the length of the index list.

## Rationale: how does this CIP achieve its goals?

By batching multiple lookups into one builtin, `multiIndexArray`:

- Eliminates repetitive script code for loops or folds over `indexArray`.
- Reduces execution budget and size overhead of repeated builtins.
- Guarantees elements are returned in caller-specified order, enabling efficient streaming or traversal.

### Alternatives considered

- **List of Maybe a**: Returning `Nothing` for out-of-bounds indices would require a `Maybe` builtin type, increasing complexity.
- **Default value argument**: Allowing a default on lookup failure complicates strict evaluation and error detection.
- **Slice and manual mapping**: Users could write a `slice` or fold, but this remains code-heavy and costly.
- **Returning Array plus helper**: Have `multiIndexArray :: List Integer -> Array a -> Array a` return an `Array a` of selected elements and provide a new helper `arrayToList :: Array a -> List a`. This avoids constructing a list directly but requires adding `arrayToList` as a builtin and introduces extra conversion and costing complexity.

Failing on first error mirrors `indexArray` and keeps the API simple.

## Path to Active

### Acceptance Criteria

- [ ] Merge implementation into the Plutus Core repo.
- [ ] Update `cardano-ledger` costing parameters for `multiIndexArray`.
- [ ] Integrate into `cardano-node` and schedule for a protocol upgrade.

### Implementation Plan

1. Add `multiIndexArray` to Plutus Core spec and runtime.
2. Define preliminary cost model (linear in index list length for both CPU usage and memory usage).
3. Write conformance tests covering valid and out-of-bounds cases.
4. Extend an E2E test suite to include `multiIndexArray` scenarios.
5. Benchmark against manual `indexArray` loops to refine costing.
6. Update formal documentation (`plutus-metatheory`, spec PDF).
7. Complete integration and include in the next hard fork.

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
