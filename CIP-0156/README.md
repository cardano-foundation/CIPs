---
CIP: 156
Title: Plutus Core Builtin Function - `multiIndexArray`
Category: Plutus
Status: Proposed
Authors:
    - Yura Lazaryev <yuriy.lazaryev@iohk.io>
    - Philip DiSarro <info@anastasialabs.com>
Implementors:
    - IOG Plutus Team <https://iohk.io>
Discussions:
    - Original PR: https://github.com/cardano-foundation/CIPs/pull/1050
    - CIP-0156 | array-first argument order for multiIndexArray: https://github.com/cardano-foundation/CIPs/pull/1234
Created: 2025-07-07
License: CC-BY-4.0
---

## Abstract

We propose adding a new builtin function, `multiIndexArray`, to Plutus Core. This function takes an array and a list of integer indices, returning a list of the array elements at those positions in the specified order.

## Motivation: Why is this CIP necessary?

Plutus Core arrays (CIP-0138) support O(1) individual lookup via `indexArray`. However, extracting multiple elements requires repeated calls to `indexArray`, which:

1. Increases script size and execution cost.
2. Complicates on-chain logic for batching lookups or reordering.
3. Prevents efficient bulk access and traversal in a user-defined order.

A single `multiIndexArray` call reduces code and cost overhead by batching lookups and delivering elements in the desired sequence.

## Specification

Add the following builtin function:

```haskell
multiIndexArray :: forall a. Array a -> List Integer -> List a
```

- **Inputs**:
  1. An `Array a` to index.
  2. A `List Integer` of zero-based indices, in the order elements should be retrieved.
- **Output**: A `List a` containing the elements at the specified indices, in the same order. In case of repeated indices, the same element is returned multiple times.
- **Error handling**: The entire call fails, with the same error semantics as `indexArray`, if either:
  1. any index is out of bounds (< 0 or ≥ lengthOfArray), or
  2. the index list contains more than 1024 indices.

  Both conditions are checked while the index list is traversed, so a call that violates both fails on whichever the traversal reaches first.
- **Cost**: CPU usage is quadratic in the length of the index list. Memory usage is linear in it.

## Rationale: How does this CIP achieve its goals?

By batching multiple lookups into one builtin, `multiIndexArray`:

- Eliminates repetitive script code for loops or folds over `indexArray`.
- Reduces execution budget and size overhead of repeated builtins.
- Guarantees elements are returned in caller-specified order, enabling efficient streaming or traversal.

The index list is capped at 1024 entries because the cost model can only observe how many indices a call passes, and how long walking a list of indices takes is not determined by that count alone once the list grows large. The cap bounds the builtin to a domain over which a single cost curve follows the measurements closely, so a call is charged near what it actually costs; 1024 is also well above realistic use, which reads tens of elements rather than thousands. Raising the cap later would require a second variant of the builtin, so that scripts already on chain keep their current behaviour.

### Alternatives considered

- **List of Maybe a**: Returning `Nothing` for out-of-bounds indices would require a `Maybe` builtin type, increasing complexity.
- **Default value argument**: Allowing a default on lookup failure complicates strict evaluation and error detection.
- **Slice and manual mapping**: Users could write a `slice` or fold, but this remains code-heavy and costly.
- **Returning Array plus helper**: Have `multiIndexArray :: Array a -> List Integer -> Array a` return an `Array a` of selected elements and provide a new helper `arrayToList :: Array a -> List a`. This avoids constructing a list directly but requires adding `arrayToList` as a builtin and introduces extra conversion and costing complexity.
- **Indices-first argument order**: `List Integer -> Array a -> List a`. Array-first is used instead to match `indexArray :: Array a -> Int -> a`, keeping the array builtins consistent and letting callers partially apply a fixed array.

Failing on first error mirrors `indexArray` and keeps the API simple.

## Path to Active

### Acceptance Criteria

- [x] Merge implementation into the Plutus Core repo.
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
