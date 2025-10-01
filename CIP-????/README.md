---
CIP: ??
Title: More `BuiltinValue` Functions
Category: Plutus
Status: Proposed
Authors:
    - fallen-icarus <modern.daidalos@gmail.com>
Implementors: []
Discussions: []
Created: 2025-10-01
License: CC-BY-4.0
---

## Abstract

[CIP-0153][1] added a new `BuiltinValue` type to make working with on-chain values more efficient.
However, it added only a few builtin functions for working with this new `BuiltinValue` type which
limits its real world usability. Adding and maintaining builtin functions is costly, but the
importance of validating values in the eUTxO model justifies a wider range of builtin functions for
this purpose. With this in mind, this CIP proposes a few extra builtin functions to improve the
usability of this new `BuiltinValue` type while still trying to minimize the overall maintenance
burden.

## Motivation: why is this CIP necessary?

> UPLC is not a general-purpose programming language. It is a language specifically designed to
> write validation logic to set constraints for the creation and transfer of Value and Data across
> the Cardano blockchain. **Given that half of the entire purpose of this language is to express
> constraints over the creation and transfer of** `Value`, why is Value treated as a standard
> library concept rather than a first-class language primitive?

This was the motivation for [CIP-0153][1]. Given the overwhelming importance for validating `Value`,
it makes sense for `BuiltinValue` to have a reasonably disproportionate number of builtin operations
as compared to `BuiltinList` or `BuiltinArray`. The current builtins added in CIP-0153 do not cover
many of the use cases for `Value`. As a reference, see the Aiken stdlib's [functions on `Value`][2].
Functions like `tokens`, `negate`, and `policies` are not possible to implement using the CIP-0153
builtin functions which means they will not benefit from the new `BuiltinValue` type. Plutus needs
enough builtins to cover the main operations on `BuiltinValue`, either through generalizable
builtins or dedicated ones.

## Specification

This CIP proposes adding the following new builtins functions:

```haskell
type BuiltinCurrencySymbol = BuiltinByteString

-- | Negate all values in a `BuiltinValue`.
negate :: BuiltinValue -> BuiltinValue

-- | Intersection of two `BuiltinValue`s. Returns data in the first value for the (policy ids, token
-- names) existing in both values.
intersection :: BuiltinValue -> BuiltinValue -> BuiltinValue

-- | Returns all policy ids found in the value.
policies :: BuiltinValue -> List [BuiltinCurrencySymbol]

-- | Return all tokens and their quantities for a given policy id. It returns a `BuiltinValue` so
-- that the result can make use of the `lookupCoin` builtin added in CIP-0153. It can always be
-- converted to a `List` for pattern-matching using the `valueData` builtin added in CIP-0153.
-- See the Rationale section for why `intersection` isn't used instead.
lookupTokens :: BuiltinCurrencySymbol -> BuiltinValue -> BuiltinValue
```

## Rationale: how does this CIP achieve its goals?

After this CIP, the total set of `BuiltinValue` functions will be:

```haskell
-- CIP-0153 functions
insertCoin :: BuiltinCurrencySymbol -> BuiltinTokenName -> BuiltinInteger -> BuiltinValue -> BuiltinValue
lookupCoin :: BuiltinValue -> BuiltinCurrencySymbol -> BuiltinTokenName -> BuiltinInteger
valueContains :: BuiltinValue -> BuiltinValue -> Bool
unionValue :: BuiltinValue -> BuiltinValue -> BuiltinValue
valueData :: BuiltinValue -> BuiltinData
unValueData :: BuiltinData -> BuiltinValue

-- New functions
negate :: BuiltinValue -> BuiltinValue
intersection :: BuiltinValue -> BuiltinValue -> BuiltinValue
policies :: BuiltinValue -> List [BuiltinCurrencySymbol]
lookupTokens :: BuiltinCurrencySymbol -> BuiltinValue -> BuiltinValue
```

From these builtin functions, most of Aiken's stdlib `Value` functions can now make use of the
improved efficiency of CIP-0153's `BuiltinValue`. The single `intersection` function enables all
kinds of higher-level filtering functions using only a single builtin function. While `intersection`
is not a trivial function, it is very similar to `unionValue` which has already been costed for
CIP-0153.

> [!NOTE] 
> While `lookupTokens` could also be implemented using `intersection`, `lookupTokens` is just a
> simple outer map value lookup. It should be a very simple builtin to cost and maintain so
> accepting the performance hit from `intersection` instead likely isn't justified. For reference,
> Aiken's `tokens` function is used many times in a single contract execution (once per tx output)
> for protocols designed based on [CIP-89][9] which means the overhead from using `intersection`
> would quickly add up.

### Does this create a "Slippery Slope"?

Aside from `intersection`, all other proposed builtins are simple operations commonly found on `Map`
data structures. So the author does not believe this CIP sets a precedence for "builtin bloat".

## Path to Active

### Acceptance Criteria

- [ ] The feature is implemented according to the implementation plan and merged into
the master branch of the [plutus][3] repository.
- [ ] [cardano-ledger][4] is updated to include new protocol parameters to control costing of
the new builtins.
- [ ] The feature is integrated into [cardano-node][5] and released as part of a hard fork.

### Implementation Plan

The implementation of this CIP should not proceed without an empirical assessment of the
effectiveness of the new primitives, as per the following plan:

1. Implement the new primitives according to the specification.
2. Assign a preliminary cost to the new builtin functions. Consider similar operations and their
   current costs.
3. Create variants of the [existing benchmarks][6] and potentially add some more.
4. Check that the builtin operations over `BuiltinValue` are indeed significantly faster.
5. Check that `lookupTokens` is significantly faster and/or uses significantly less execution memory
   than a comparable implementation using `intersection`.

If the preliminary performance investigation was not successful, this CIP should be revised
according to the findings of the experiment. Otherwise, the implementation can proceed:

6. Determine the most appropriate costing functions for modelling the builtin's performance
and assign costs accordingly.
7. Add the new builtin type and functions to the appropriate sections in the [Plutus Core
Specification][7].
8. Formalize the new builtin type and functions in the [plutus-metatheory][8].
9. The final version of the feature is ready to be merged into [plutus][3] and accepted by
the Plutus Core team.

## Copyright
This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).

[1]: https://github.com/cardano-foundation/CIPs/tree/master/CIP-0153/README.md "CIP-0153"
[2]: https://aiken-lang.github.io/stdlib/cardano/assets.html "Aiken `Value` functions"
[3]: https://github.com/IntersectMBO/plutus/ "plutus"
[4]: https://github.com/IntersectMBO/cardano-ledger "cardano-ledger"
[5]: https://github.com/IntersectMBO/cardano-node "cardano-node"
[6]: https://github.com/IntersectMBO/plutus/tree/master/plutus-benchmark/script-contexts "script-context-benchmarks"
[7]: https://plutus.cardano.intersectmbo.org/resources/plutus-core-spec.pdf "Formal Specification of the Plutus Core Language"
[8]: https://github.com/IntersectMBO/plutus/tree/master/plutus-metatheory "plutus-metatheory"
[9]: https://github.com/cardano-foundation/CIPs/blob/master/CIP-0089/README.md "Beacon Tokens CIP"
