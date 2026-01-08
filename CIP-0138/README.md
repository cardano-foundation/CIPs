---
CIP: 138
Title: Plutus Core Builtin Type - Array
Category: Plutus
Status: Proposed
Authors:
    - Michael Peyton Jones <michael.peyton-jones@iohk.io>
    - Ana Pantilie <ana.pantilie@iohk.io>
Implementors: []
Discussions:
    - https://github.com/cardano-foundation/CIPs/pull/915
Created: 2024-09-18
License: CC-BY-4.0
---

## Abstract

We propose an array builtin type for Plutus Core. This type will have constant-time lookup,
which is a useful feature that is otherwise not possible to achieve. 

## Motivation: Why is this CIP necessary?

The first part of [CPS-0013][1] outlines in great detail the motivation for introducing this
new builtin type.

To summarize, it is currently not possible to write a data structure with constant-time
lookup in Plutus Core. We propose to solve this problem by introducing an array type into
Plutus Core's builtin language, as it is the standard example of a data structure
with this property, and it is a key component of many classical algorithms and data
structures.

Access to an array type would provide significant performance improvement opportunities to
users of Plutus Core, since currently they must rely on suboptimal data structures such as
lists for looking up elements inside a collection.

## Specification

We add the following builtin type: `Array` of kind `Type -> Type` representing
a one-dimensional array type with indices of type `Integer`. Elements are indexed
consecutively starting from `0`.

***Note***: Here `Type` is the universe of all _builtin_ types, since we do not consider
types formed out of applying builtin types to arbitrary types to be inhabited.

The `Array` builtin type should be implemented with a fixed-size immutable array structure
that has constant-time lookup.

We add the following builtin functions:

1. `indexArray` of type `forall a . Integer -> Array a -> a`.
    - It returns the element at the given index in the array, or fails with an error if the
    index is outside the bounds of the array.
    - It uses constant time and constant memory.
2. `lengthOfArray` of type `forall a . Array a -> Integer`
    - It returns the length of the array.
    - It uses constant time and constant memory.
3. `listToArray` of type `forall a . List a -> Array a`
    - It converts the argument builtin list into a builtin array.
    - It uses linear time and linear memory.

### Binary serialisation and deserialisation

As with all Plutus Core builtin types, arrays must have a fixed binary representation.

For arrays, this representation will be based on the one currently implemented in the [flat][8] encoding
for the [Haskell `List` type][9].  Plutus Core arrays must be converted to lists before being serialised,
and deserialisation is performed by using the flat decoder for lists and converting the result to an array.

## Rationale: How does this CIP achieve its goals?

### Choice of builtin functions and their specification

The following section presents the reasoning behind the above specification of a Plutus
core builtin array type.

It is important to mention that we based our decisions on the desire to keep the builtin
language as small as possible, i.e. to not introduce types or functions
which are not essential for definitional purposes or essential for providing a practical
interface to users.

It also discusses some alternatives or additions which should be considered as part of the
[preliminary investigation](#implementation-plan).

### Providing safe lookups

The `indexArray` builtin function is necessary, since access to constant-time lookup is the main
requirement outlined in this CIP. However, there remains the question of how users should
deal with the function's partiality.
We considered the following options:

1. Introduce another new builtin type, one which implements `Maybe` semantics. The type
signature for `indexArray` would become `forall a . Integer -> Array a -> Maybe a` and it
would return `Nothing` for out-of-bounds lookups.
    - The obvious disadvantage is the necessity of adding another new builtin type (there is
    no `Maybe` builtin type in Plutus Core), which would further increase the complexity of
    the builtin language.
    - Another disadvantage would be that this solution is the most costly: users will incur
    additional costs in deconstructing the returned `Maybe`.

2. Failed lookups return a default value provided by the caller:
`indexArray :: forall a . Integer -> a -> Array a -> a`.
    - This solution is problematic whenever there is no sensible default value and
    the user wants the function to fail. Since Plutus Core is strict, it is not possible
    to pass `error` as the default value without it getting evaluated before the call and
    terminating execution immediately.
    - As of the time of writing, builtin functions cannot be higher-order. However, that is
    subject to change in the near future when pattern matching builtins will be supported by
    Plutus Core. This feature would allow a safe version of `indexArray` with type `forall a .
    Integer -> (() -> a) -> Array a -> a` to be expressible in the builtins language.

3. Include `lengthOfArray` and require the user to perform appropriate length guards before
calling `indexArray`.
    - This is a familiar option from other languages.
    - By definition arrays are fixed-size and their length is available in constant time.
    - It also allows users to omit bounds checks when they know a priori that the
    index is in bounds.

After considering these three options, we concluded that the addition of
the `lengthOfArray` builtin function is both necessary and sufficient for introducing a
well-defined array type into the builtin language.

### Constructing arrays

The last required functionality for having a practical interface is the ability to
construct arrays.

Due to our decision of providing immutable arrays, it is difficult (or very expensive) to build up arrays incrementally.
A naive approach would require repeated copying and potentially the usage of quadratic
space and time.

A more appropriate approach would be to construct the array in bulk,
however that would require an intermediate representation of a collection of elements. Fortunately this already exists in the builtin language in the form of builtin lists.
We can then naturally introduce a function which transforms lists into arrays: `listToArray`.


### Slices

Many array-like data structures support cheap _slices_, e.g. a function with the following
type signature: `slice :: Integer -> Integer -> Array a -> Array a`, which produces a _view_
of the original array between the two indices (similarly, the same can be achieved using an
`indexArray` and a `lengthOfArray`).

We do not propose to add `slice` to our builtin set, since it is very easy to build a data
structure that supports slices on top of `array`, simply by tracking some additional
integers to track the subset of the array that is in view.

### Arrays in `Data`

In [CPS-0013][1] the idea of representing the arguments to the `Data` constructor
`Constr` as an `Array` in Plutus Core was presented as being more appropriate than
the current list representation.

A significant requirement in implementing this modification is maintaining backwards
compatibility. Therefore, we cannot simply modify the internal representation of `Data`.

One idea would be to add a new builtin such as the following:
`unConstrDataArray :: Data -> (Integer, Array Data)`. However, this builtin will
inevitably have linear time complexity since it is based on a list traversal. So
it does not actually solve the original problem, unless it can be shown experimentally
that, in practice, these lists are usually small enough for the transformation to be negligible.

## Path to Active

### Acceptance Criteria

- [ ] The feature is implemented according to the implementation plan and merged into
the master branch of the [plutus repository][5].
- [ ] [cardano-ledger][6] is updated to include new protocol parameters to control costing of
the new builtins.
- [ ] The feature is integrated into [cardano-node][7] and released as part of a hard fork.

### Implementation Plan

The implementation of this CIP should not proceed without an empirical assessment of the effectiveness of the new primitives, as per the following plan:

1. Implement the new primitives according to the specification, including the experimental
versions discussed in the CIP.
2. Assign a preliminary cost to the new builtin functions. Consider similar operations and their
current costs.
3. Create variants of the [existing benchmarks][4] and potentially add some more.
4. From the total set of newly implemented builtins, find a minimal but practical set of
primitives which are indeed significantly faster in both real-time performance and modelled costs.
5. If such a set does not exist, find out why. This means that the preliminary investigation
was not successful. If it does, revise the specification to include
the final set of primitives.

If the preliminary performance investigation was not successful, this CIP should be revised
according to the findings of the experiment. Otherwise, the implementation can proceed:

6. Determine the most appropriate costing functions for modelling the builtin's performance
and assign costs accordingly.
6. Add the new builtin type and functions to the appropriate sections in the [Plutus Core
Specification][2].
7. Formalize the new builtin type and functions in the [plutus-metatheory][3].
8. The final version of the feature is ready to be merged into [plutus][5] and accepted by
the Plutus Core team.

## Copyright
This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).

[1]: https://cips.cardano.org/cps/CPS-0013 "CPS-0013"
[2]: https://plutus.cardano.intersectmbo.org/resources/plutus-core-spec.pdf "Formal Specification of the Plutus Core Language"
[3]: https://github.com/IntersectMBO/plutus/tree/master/plutus-metatheory "plutus-metatheory"
[4]: https://github.com/IntersectMBO/plutus/tree/master/plutus-benchmark/list "List benchmarks"
[5]: https://github.com/IntersectMBO/plutus "plutus"
[6]: https://github.com/IntersectMBO/cardano-ledger "cardano-ledger"
[7]: https://github.com/IntersectMBO/cardano-node "cardano-node"
[8]: https://hackage.haskell.org/package/flat "flat"
[9]: https://hackage.haskell.org/package/base-4.21.0.0/docs/Data-List.html "Haskell List"
