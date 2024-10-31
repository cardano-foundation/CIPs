---
CIP: 138
Title: Plutus Core Builtin Type - `Array`
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

## Motivation: why is this CIP necessary?

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

For arrays we have chosen the following representation, based on the one currently
implemented in the [flat][8] encoding for the [Haskell `Array` type][9].

We define the result of encoding a Plutus Core array of type `Array a`
and with length `n`, as follows:
- Let:
    - `Ea` be an encoding function for `a`, i.e. it is of type `a -> ByteString`.
    - `Ei` be an encoding function for `Integer`
    - `++` be bytestring concatenation
    - `bin(i)` be the binary representation for any number `i`.
- The first bits in the resulting sequence will be `Ei(0) ++ Ei(n-1)`, that is the
encoding of the first index followed by the encoding of the last.
- As binary, arrays are split into _blocks_ of `255` elements. For each block, the first
bits in the block encoding represent the number of elements in the block. This can be decided
as follows:
    - there will be `n div 255` blocks where the next bits are `bin(255)`
    - and, if `n mod 255 > 0`, one final block where the next bits are `bin(n mod 255)`. 
- Inside each block, the next bits come from encoding all the elements pertaining to
the block:
    - we will refer to each block as `b0 ... bm` where `m+1` is the number of blocks;
    - `indexArray` is a function with the same behaviour as the proposed `indexArray` builtin,
    since it is fixed, we omit the array argument for brevity;
    - for the block `bi`, the bit sequence will be:
    `Ea(indexArray(i*255)) ++ Ea(indexArray(i*255 + 1)) ++ ... ++ Ea(indexArray(i*255 + m))`.
- After all blocks have been encoded, the resulting binary sequence is appended with exactly
`8` bits of value `0`. 

***Remarks***:
- Empty arrays are represented as: `Ei(0) ++ Ei(-1) ++ 00000000`. This follows from the
encoding described above, as `n` is `0` and there are no elements to encode.
- The decoding of arrays is, of course, the inverse of the encoding function.

<details>
    <summary>
    Expand to see examples of applying the above encoding strategy to arrays of different element types.
    </summary>

    ------------
    -- Example 1
    >>> encode [1] as an array:
    00000000 00000000 00000001 00000010 00000000

    -- the first and last indices are 0, the number of elements is 1
    -- 00000010 is the encoding of 1 of type Integer
    -- the bytestring ends with 8 bits of value 0

    ------------
    -- Example 2
    >>> encode [1, 1, 1] as an array:
    00000000 00000100 00000011 00000010 00000010 00000010 00000000
    -- ^ 0      ^ 2      ^ 3      ^ 1      ^ 1      ^ 1 
    
    ------------
    -- Example 3
    >>> encode [11, 22, 33, 44] as an array:
    00000000 00000110 00000100 00010110 00101100 01000010 01011000 00000000
    -- ^ 0     ^ 3     ^ 4     ^ 11      ^ 22     ^ 33     ^ 44

    ------------
    -- Example 4
    >>> encode [True, True, True] as an array:
    00000000 00000100 00000011 11100000 000

    -- True is encoded as a single bit of value 1
    -- notice how the eight final zeros are split between multiple bytes

    ------------
    -- Example 5
    >>> encode [True ... True] (255 times) 
    00000000 11111100 00000011 11111111 11111111 11111111 11111111 11111111 11111111 11111111 11111111 11111111 11111111 11111111 11111111 11111111 11111111 11111111 11111111 11111111 11111111 11111111 11111111 11111111 11111111 11111111 11111111 11111111 11111111 11111111 11111111 11111111 11111111 11111111 11111111 11111110 0000000

    -- 11111100 00000011 is the representation of 254, the last index
    -- 11111111 is the total number of elements in the block, 255
    -- True is encoded to 1, so the bytes get filled except the last one, since 255 does not divide by 8
    -- there are again 8 final zeros split between the two last bytes

    ------------
    -- Example 6
    >>> encode [True ... True] (256 times)
    00000000 11111110 00000011 11111111 11111111 11111111 11111111 11111111 11111111 11111111 11111111 11111111 11111111 11111111 11111111 11111111 11111111 11111111 11111111 11111111 11111111 11111111 11111111 11111111 11111111 11111111 11111111 11111111 11111111 11111111 11111111 11111111 11111111 11111111 11111111 11111110 00000011 00000000

    -- again, since True does not encode to full bytes, the above example can be tricky to decode, but is nevertheless correct
    -- 0 0000001 is the beginning of the second block, it represents the number of elements in the block which is 1
    -- immediately after, there is 1 bit which is the encoding of the single element of this block
    -- and finally, the last 8 zeros 

</details>


## Rationale: how does this CIP achieve its goals?

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
[9]: https://hackage.haskell.org/package/array-0.5.4.0/docs/Data-Array.html#t:Array "Haskell Array"