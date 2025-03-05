---
CPS: 13
Title: Better builtin data structures in Plutus
Status: Proposed
Category: Plutus
Authors:
    - Michael Peyton Jones <michael.peyton-jones@iohk.io>
    - Philip DiSarro <philip.disarro@iohk.io>
    - Pi Lanningham <pi@sundaeswap.finance>
Discussions:
Created: 2023-12-14
License: CC-BY-4.0
---

## Abstract

Plutus Core lacks builtin data structures with good asymptotic performance for some use cases.

## Problem

Plutus Core has a few builtin data structures, but these are mostly used to make a minimally adequate representation of the `Data` type. 
It does not have builtin data structures optimized for performance.

Users can implement their own data structures (since Plutus Core is an expressive programming language), but in practice this has not happened much. 
In particular, we will focus on two examples here:

1. Arrays with constant-time lookup
2. Maps with logarithmic-time lookup (also Sets, but we can treat them as a special case of Maps)

Both of these are difficult to implement in Plutus Core:

1. Arrays are (we believe) impossible without some kind of primitive with constant-time lookup
2. Maps are possible but are typically moderately complex data structures which require a lot of code, and this has not been done in practice

## Use cases

### Arrays

#### Order matching

A common pattern in DEXs is to have a list of inputs/outputs to match up in a datum. 
In some cases the order is highly significant, e.g. earlier orders should be processed first, and the outcome of processing an earlier order may affect later ones.

For example, we might have:
```
inputIdxs :: BuiltinList Integer
outputIdxs :: BuiltinList Integer
```
We then want to go through these lists, looking up the corresponding inputs and outputs and check some property (e.g. that the value is directly transferred from one to the other).

This requires a quadratic amount of work, which puts a low ceiling on how many orders can be processed at once. 
Empirically, many are capped at about 30, whereas if they were limited only by the amount of space in the transaction for inputs and outputs the limit would be hundreds.

If we had arrays with constant time indexing, we could make this linear instead. 
Note that unless we also implemented the "Data fields" suggestion below we would still need to do a linear amount of work to create arrays for the transaction inputs and outputs from the lists in the script context.

#### Data fields

The `Data` type has a `Constr` alternative which is used for encoding datatype constructors. 
This is used for encoding the script context, and is used by languages such as Aiken extensively for representing user-defined datatypes also.

The fields of the constructor are encoded in a list; hence to access a particular field the compiled code needs to do a linear amount of work. 
If the arguments to a `Constr` were an array, we could access the fields in constant time.

Similarly, the `List` and `Map` constructors of `Data` could use arrays.

### Maps

#### Operations on `Value`

The `Value` type is a nested map: it is a map from bytestrings (representing policy IDs) to maps from bytestrings (representing token names) to integers (representing quantities).
Since map operations are currently linear, this means that even simple operations like checking whether one value is less than another can have quadratic cost.

This would be much better if map operations were logarithmic cost.

#### Indexing by party

Many applications have a known set of participants identified by some bytestring, typically a public key. 
It is therefore natural to store per-party state in a map indexed by the party identifier.

Since map operations currently have much worse complexity than a good map data structure (often linear/quadratic instead of logarithmic/linear), this is needlessly expensive and imposes a limit on the number of parties.

## Goals

1. Reduce the cost of operations on `Value` by a factor of 2-10
2. Reduce the cost of a matching algorithm such that we can handle hundreds of matches for the same cost it currently takes to do 30.

## Open questions

- Can we implement a set/map data structure in Plutus Core code that has acceptable performance and doesn’t require too much size overhead?
- Do we need generic maps or is a map-from-bytestring sufficient? What about map-from-integer?
    - Generic maps are harder since we typically need to know how to order the key type
- Is an array type useful even if it is immutable?
    - We are unlikely to be able to offer mutable arrays
- Are builtin data structures useful enough even if they can only contain builtin types?
    - This would mean that complex data structures would have to be stored inside arrays as `Data`, rather than using Scott encoding or sum-of-products representation
- Can we feasibly change the structure of the builtin `Data` type so that `Constr` arguments are in an array?
    - We would need to retain both versions for backwards compatibility
    
## References

- https://x.com/Quantumplation/status/1733298551571038338?s=20

## Copyright

This CPS is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
