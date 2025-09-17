---
CIP: 153
Title: Plutus Core Builtin Type - MaryEraValue
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

We propose to extend the `Data` type in Plutus Core with a new constructor `Value BuiltinValue`, introducing native, first-class support for multi-asset values that adhere to the invariants of multi-asset values in the Cardano ledger.

This addition enables on-chain scripts to operate on multi-asset values directly and efficiently, without resorting to nested map encodings. It eliminates the need for costly emulation of value operations, reduces validator script size, enables faster execution, and significantly lowers the ex-unit budgets required to process multi-asset logic. By elevating multi-asset values to a primitive type, this change aligns Plutus Core more closely with its primary domain—expressing constraints over the transfer of value—and unlocks substantial improvements in performance, safety, and consistency across the smart contract ecosystem.

## Motivation: why is this CIP necessary?

UPLC is not a general-purpose programming language. It is a language specifically designed to write validation logic to set constraints for the creation and transfer of Value and Data across the Cardano blockchain. **Given that half of the entire purpose of this language is to express constraints over the creation and transfer of** `Value`, why is Value treated as a standard library concept rather than a first-class language primitive?

The value proposition of domain-specific languages like UPLC is that they are purpose-built for a specific problem space, and as such, are able to outperform general-purpose languages within that domain. This foundational consideration seems to have been largely absent from the historical design of Plutus. It is difficult to reconcile the absence of first-class support for `Value` in a language explicitly designed to manage the transfer of value.

Currently, Plutus Core has no concept of multi-asset values. Instead, `Value` is a standard library construct, implemented as a nested `Map`:

```haskell
newtype Value = Value (Map CurrencySymbol (Map TokenName Integer))
```
While this representation superficially resembles the structure of ledger-level values, it lacks the necessary semantic guarantees. The critical invariants upheld by the ledger—such as omitting zero-valued assets, eliminating empty maps, and maintaining canonical order—must be manually replicated in every implementation targeting Plutus Core. This makes secure and correct usage of `Value` significantly harder than it should be.

Smart contract languages like Plinth, Aiken, Plutarch, and Helios must each implement their own standard library for value manipulation, resulting in duplicated logic, inconsistent behavior, and non-trivial security risks. Even operations as fundamental as value equality and union require verbose logic to normalize entries—adding cost and complexity to every validator.

It should not be the responsibility of language authors or smart contract developers to implement secure and efficient operations over a type that is fundamental to the domain itself.

## Specification

### MaryEraValue

A _map_ is a collection of _values_ indexed by _keys_. We consider a map to be _well-defined_ when each key uniquely identifies each value, and when additional structural and semantic constraints are satisfied. The canonical representation of Mary-era multi-asset Values in Plutus Core is a nested map where the keys of the outer map are `AsData CurrencySymbol`s and the keys of the inner map are `AsData TokenName`s and the _values_ of the inner map are `AsData Integer` (representing the quantity of the asset).

Here are the important invariants of the PlutusCore representation of the Mary-era Value types from the Cardano ledger:
1. All _keys_ in the outer map are unique (each `CurrencySymbol` appears only once)
2. All _keys_ in the inner map are unique (each `TokenName` appears only once)
3. The _keys_ in the outer map are ordered lexographically (`CurrencySymbol`s appear in ascending order)
4. The _keys_ in the inner map are ordered lexographically (`TokenName`s appear in ascending order)
5. There are no empty inner maps (The _value_ associated with any given `CurrencySymbol` _key_ cannot be an empty map)
6. There are no zero-quantity _values_ in the inner maps (The _value_ associated with any given `TokenName` _key_ in an inner-map cannot be zero).

### Mary-era Value as a builtin type

We propose introducing a new builtin type, `BuiltinValue`, along with a set of builtins for efficient manipulation of multi-asset values. These builtins will enforce all invariants defined for multi-asset values in the Cardano ledger. Additionally propose extending the Data type with a new constructor to support BuiltinValue:

```haskell
data Data =
      Constr Integer [Data]
    | Map [(Data, Data)]
    | List [Data]
    | I Integer
    | B BS.ByteString
    | Value BuiltinValue
    -- ^ New constructor for `BuiltinValue`
```
This enables direct representation of BuiltinValue within `Data`, eliminating the expensive computation that would otherwise be required to convert back and forth between the `Data` representation of `Value` as nested Map structures and the `BuiltinValue` type.

### On the Necessity of a `Data` Constructor for `BuiltinValue`

Introducing a `BuiltinValue` type to Plutus Core without also adding a corresponding constructor to the `Data` type (i.e. `Value BuiltinValue`) would result in a fragmented and inefficient design. In such a scenario, smart contracts would require dedicated conversion builtins to translate between `BuiltinData`—the standard interface type in validators—and `BuiltinValue`. Although these conversions are linear in the size of the structure and less expensive than conversions like `Data → ScriptContext`, they are still nontrivial and, in practice, can become prohibitively expensive.

Consider, for instance, a `Value` containing hundreds of assets where a script only needs to access ADA. Converting the entire structure to a `BuiltinValue` simply to look up a single entry would be significantly more expensive than directly inspecting the original `Data` representation. Even more critically, this approach creates ambiguity for developers: they must decide when to convert, weigh the performance trade-offs, and handle two separate representations of the same underlying concept.

This defeats the entire purpose of introducing `BuiltinValue`, which is to simplify, secure, and optimize multi-asset handling in Plutus. If this proposal were to result in developers continuing to use nested `Map` structures within `Data` for performance reasons, it would not only fail to unify the representation of `Value` in Plutus Core—it would add yet another layer of complexity.

It is therefore a strong requirement of this proposal that `BuiltinValue` be made a first-class constructor within the `Data` type (i.e. `Value BuiltinValue`). Only with this addition can we ensure that all value-related logic is handled canonically, efficiently, and securely via the new builtins—eliminating the need for conversions or manual manipulation of `BuiltinData`.

### BuiltinValue Operations
We propose the introduction of the following builtin functions to support efficient and invariant-preserving manipulation of multi-asset values through a new `BuiltinValue` type.

These functions operate on the following types:
```haskell
type BuiltinValue -- A new primitive type
type BuiltinCurrencySymbol = BuiltinByteString
type BuiltinTokenName = BuiltinByteString
type BuiltinQuantity = BuiltinInteger
```

We propose the following set of builtin functions to accompany the new builtin type:
1. `insertCoin :: BuiltinCurrencySymbol -> BuiltinTokenName -> BuiltinInteger -> BuiltinValue -> BuiltinValue`
    - it returns a Mary-era Value with the `Coin` inserted, silently discarding any previous value.
      If the `BuiltinInteger` argument (the quantity) is zero, the `Coin` is removed.
2. `lookupCoin :: BuiltinCurrencySymbol -> BuiltinTokenName -> BuiltinValue -> BuiltinQuantity`
   - it returns the quantity of a given `Coin` in a Mary-era Value.
3. `unionValue :: BuiltinValue -> BuiltinValue -> BuiltinValue`
    - it merges two provided values
    - when there are collisions it adds the quantities, if the resulting sum is zero it removes the entry to maintain the Mary-era Value invariants (no zero-quantity entries, no empty inner maps) such that the result is a normalized value.
    - This operation is commutative and associative, thus makes `BuiltinValue` a commutative semigroup.
4. `valueContains :: BuiltinValue -> BuiltinValue -> Bool`
    - it compares the two Mary-era Values and determines if the first value is a superset of the second.
    - `valueContains a b == True` if and only if: for each `(currency, token, quantity)` in `b`, if `quantity > 0`, then `lookupCoin currency token a >= quantity`; if `quantity < 0`, then `lookupCoin currency token a == quantity`.
    - We require `==` for negative quantities, rather than `>=`,because (1) it avoids nonsensical behaviors like `valueContains [] [("c", "t", -1)] == True` (2) it preserves `valueContains` as a partial order.
5. `valueData :: BuiltinValue -> BuiltinData`
    - encodes a `BuiltinValue` as `BuiltinData`.
6. `unValueData :: BuiltinData -> BuiltinValue`
    - decodes a `BuiltinData` into a `BuiltinValue`, or fails if it is not one.

A note on `valueData` and `unValueData`: in Plutus V1, V2 and V3, the encoding of `BuiltinValue` in `BuiltinData` is identical to that of the [existing `Value` type](https://plutus.cardano.intersectmbo.org/haddock/latest/plutus-ledger-api/PlutusLedgerApi-V1-Value.html#t:Value) in plutus-ledger-api.
This ensures backwards compatibility.
Beginning in the Dijkstra era, a new `Value` constructor will be added to `BuiltinData`, making `valueData` and `unValueData` constant time operations for Plutus V4 onwards.

## Rationale: how does this CIP achieve its goals?

### Efficiency

Builtins are strictly more efficient than user-defined operations evaluated by the CEK machine. Today, operations on `Value` must be implemented at the Plutus level using nested `Map` structures and generic functional constructs. These are significantly slower and more memory-intensive than equivalent builtins due to their interpretive overhead and lack of optimization opportunities.

By introducing a dedicated `BuiltinValue` type and associated builtins, we enable:

- Elimination of the need to deconstruct and traverse deeply nested data-encoded maps to perform operations on `Value`s, which significantly improves execution efficiency.
- Drastically reduced script sizes, since `Value` operations no longer need to be defined in the bytecode of every validator; they are now provided natively by the language as builtins.

This directly addresses a major pain point for developers working with large or complex multi-asset values.

### Security & Abstraction

Introducing a single, standardized `BuiltinValue` type — including a constructor on `Data` and associated conversion builtins — eliminates the need for dual representations of multi-asset values. Without this, developers would be forced to evaluate trade-offs in every instance where value manipulation is required: either operate directly on `BuiltinData`, or incur the overhead of converting to and from SOP-style encodings in order to gain performance benefits from subsequent operations on the structured representation. This added friction increases both complexity and fragmentation across the ecosystem.

Instead, developers will have:

- A consistent and canonical representation of multi-asset values.
- Simple, expressive, and performant builtins for common operations.
- Fewer footguns and edge cases to reason about in critical onchain logic.

By elevating `Value` to a first-class builtin type, this CIP ensures that the semantics of `Value` and its operations are uniform across all languages targeting Plutus Core. Currently, each language (e.g., Aiken, Plutarch, Helios, Plu-Ts, etc.) must independently define a `Value` type and implement its operations in their standard libraries. This fragmentation introduces the risk of divergent behaviors and subtle inconsistencies across Cardano’s smart contract ecosystem.

With `BuiltinValue`, all implementations inherit a single, authoritative definition of `Value` and its operations, removing this burden from language authors and guaranteeing consistency across the entire platform.

This CIP ultimately shifts the responsibility for correctness and optimization away from the application layer and into the language itself — the appropriate place for enforcing invariants and performance guarantees for such a core domain primitive.

## Path to Active

### Acceptance Criteria

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
