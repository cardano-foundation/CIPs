---
CIP: 153
Title: Plutus Core Builtin Type - `MaryEraValue`
Category: Plutus
Status: Proposed
Authors:
    - Philip DiSarro <philipdisarro@gmail.com>
Implementors: []
Discussions:
    - https://github.com/cardano-foundation/CIPs/pull/921
Created: 2024-10-03
License: CC-BY-4.0
---

## Abstract

We propose to introduce a number of functions for safely and efficiently working with `BuiltinData` as Value, alternatively we propose a `BuiltinMaryEraValue` type for Plutus Core.

## Motivation: why is this CIP necessary?

UPLC is not a general-purpose programming language. It is a language specifically designed to write validation logic to set constraints for the creation and transfer of Value and Data across the Cardano blockchain. Given that half of the entire purpose of this language is to add constraints to the creation and transfer of Value, why should Value be a “standard library concept”?
The whole value proposition behind domain specific languages (ie UPLC) is that the design is informed by and tailored to, the problem space. As such, it should be better suited to the task in that domain than a general-purpose language. To me it seems like this has not been taken into consideration much historically in the design of Plutus. How is there not first-class language support for Values in a domain specific language designed primarily to manage the transfer of Value?

Currently Mary-era (multi-asset) Values are represented in PlutusCore as a nested builtin map, `Map CurrencySymbol (Map TokenName Integer)`. The issue is that in reality multi-asset Values in the Cardano ledger are not Maps as such, a generic `ByteStringMap` type is not sufficient, because Values are nested maps with *very important* invariants. The failure to understand and take into account these invariants lead to a lot of common vulnerabilities in onchain code. 

For a concrete example, if we want to implement `unionValue` with `ByteStringMap` and limited higher order builtins it would look like:

```haskell
unionValue v =
 let res = builtinUnionWith (builtinUnionWith (builtinAddInteger)) v
     res2 = builtinMapValues (builtinMapFilterKeys (builtinEquals 0)) res
 in builtinMapFilterKeys ((/=) BI.null) res2
```

This requires a non-trivial number of limited higher order builtins, and is not a very intuitive function to define. Language designers targeting Plutus Core (Aiken, Plutarch, Plu-Ts, Scalus, Purus, Helios) will still need to implement the value operations using the `ByteStringMap` in their standard library which means that on top of being less performant than executing natively, there is still security risk that some implementation is insecure. On top of all that, the above implementation is non-canonical! This means that different language standard libraries could implement `unionValue` differently (for instance not filtering 0 entries or empty inner map entries) and then implement `equalsValue` to handle equality regardless of zero entries or empty map entries (ex. Plinth currently does this). 
 
We argue that it should not be the responsibility of language authors to implement secure operations over a type that is primitive to the domain task.

### MaryEraValue 

A _map_ is a collection of _values_ indexed by _keys_. We consider a map to be _well-defined_ if each key uniquely identifies each value. The canonical representation of Mary-era multi-asset Values in PlutusCore is a nested map where the keys of the outer map are `AsData CurrencySymbol`s and the keys of the inner map are `AsData TokenName`s and the _values_ of the inner map are `AsData Integer` (representing the quantity of the asset). 

Here are the important invariants of the PlutusCore representation of the Mary-era Value types from the Cardano ledger:
1. All _keys_ in the outer map are unique (each `CurrencySymbol` appears only once)
2. All _keys_ in the inner map are unique (each `TokenName` appears only once)
3. The _keys_ in the outer map are ordered lexographically (`CurrencySymbol`s appear in ascending order)
4. The _keys_ in the inner map are ordered lexographically (`TokenName`s appear in ascending order)
5. There are no empty inner maps (The _value_ associated with any given `CurrencySymbol` _key_ cannot be an empty map)
6. There are no zero-quantity _values_ in the inner maps (The _value_ associated with any given `TokenName` _key_ in an inner-map cannot be zero).

### Mary-era Value as a builtin type

The only remaining solutions are to consider:

1. Introduce builtin operations for efficient manipulation of `BuiltinData = Value` that take into consideration the invariants of ledger multi-asset values.
2. Introduce a new builtin type `BuiltinMaryEraValue` with efficient Value operations that take into consideration the invariants of ledger multi-asset values. 


## Specification

We propose the addition of the following builtin functions: 

All functions below work with:
```
type BuiltinMaryEraValue = BuiltinData -- or possibly (BuiltinList BuiltinCurrencySymbol (BuiltinMap BuiltinTokenName BuiltinData)) 
type BuiltinCurrencySymbol = BuiltinByteString
type BuiltinTokenName = BuiltinByteString
type BuiltinQuantity = BuiltinInteger 
```

We propose the following set of builtin functions to accompany the new builtin type:
1. `insertCoin :: BuiltinCurrencySymbol -> BuiltinTokenName -> BuiltinInteger -> BuiltinMaryEraValue -> BuiltinMaryEraValue`
    - it returns a Mary-era Value with the `Coin` inserted, silently discarding any previous value
2. `deleteCoin :: BuiltinCurrencySymbol -> BuiltinTokenName -> BuiltinMaryEraValue -> BuiltinMaryEraValue`
    - it returns a Mary-era Value with the `Coin` removed, or unmodified if the `Coin` was not present. 
3. `lookupCoin :: BuiltinCurrencySymbol -> BuiltinTokenName -> BuiltinMaryEraValue -> BuiltinQuantity`
   - it returns the quantity of a given `Coin` in a Mary-era Value. 
4. `unionValues :: BuiltinList BuiltinMaryEraValue -> BuiltinMaryEraValue`
    - it merges all the values in the provided list
    - when there are collisions it adds the quantities, if the resulting sum is zero it removes the entry to maintain the Mary-era Value invariants (no zero-quantity entries, no empty inner maps) such that the result is a normalized value. 
    - this is not strictly necessary, however, it becomes extremely useful if we get limited higher order builtins, or even a `fieldMap` builtin. 
5. `unionValue :: BuiltinMaryEraValue -> BuiltinMaryEraValue -> BuiltinMaryEraValue`
    - it merges two provided values
    - when there are collisions it adds the quantities, if the resulting sum is zero it removes the entry to maintain the Mary-era Value invariants (no zero-quantity entries, no empty inner maps) such that the result is a normalized value. 
6. `valueContains :: BuiltinMaryEraValue -> BuiltinMaryEraValue -> Bool`
    - it strictly compares the two Mary-era Values and determines if the first value is a superset of the second.
    - returns true if Value `a` contains each and every `Coin` in Value `b` with greater or equal quantities.
    - returns false if Value `b` contains any `Coin` that is not contained in Value `a`, or if Value `b` contains a greater quantity of any `Coin` than Value `a`.

## Rationale: how does this CIP achieve its goals?

### Efficiency

Builtins are strictly more efficient than CEK operations. 

### Security and Abstraction

The introduction of a canonical implementation of standard multi-asset value operations vastly improves ecosystem security and 

## Path to Active

## Acceptance Criteria

- [ ] The feature is implemented according to the implementation plan and merged into
the master branch of the [plutus][6] repository.
- [ ] [cardano-ledger][1] is updated to include new protocol parameters to control costing of
the new builtins.
- [ ] The feature is integrated into [cardano-node][2] and released as part of a hard fork.

### Implementation Plan

The implementation of this CIP should not proceed without an empirical assessment of the effectiveness of the new primitives, as per the following plan:

1. Implement the new primitives according to the specification.
2. Assign a preliminary cost to the new builtin functions. Consider similar operations and their current costs.
3. Create variants of the [existing benchmarks][3] and potentially add some more.
4. Check that the builtin operations over `BuiltinData = Value` are indeed significantly faster.

If the preliminary performance investigation was not successful, this CIP should be revised
according to the findings of the experiment. Otherwise, the implementation can proceed:

5. Determine the most appropriate costing functions for modelling the builtin's performance
and assign costs accordingly.
6. Add the new builtin type and functions to the appropriate sections in the [Plutus Core
Specification][4].
7. Formalize the new builtin type and functions in the [plutus-metatheory][5].
8. The final version of the feature is ready to be merged into [plutus][6] and accepted by
the Plutus Core team.

## Copyright
This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).

[1]: https://github.com/IntersectMBO/cardano-ledger "cardano-ledger"
[2]: https://github.com/IntersectMBO/cardano-node "cardano-node"
[3]: https://github.com/IntersectMBO/plutus/tree/master/plutus-benchmark/script-contexts "script-context-benchmarks"
[4]: https://plutus.cardano.intersectmbo.org/resources/plutus-core-spec.pdf "Formal Specification of the Plutus Core Language"
[5]: https://github.com/IntersectMBO/plutus/tree/master/plutus-metatheory "plutus-metatheory"
[6]: https://github.com/IntersectMBO/plutus/ "plutus"
