---
CIP: 168
Title: More `BuiltinValue` Functions
Category: Plutus
Status: Proposed
Authors:
    - fallen-icarus <modern.daidalos@gmail.com>
Implementors: []
Discussions: 
    - https://github.com/cardano-foundation/CIPs/pull/1090
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
> constraints over the creation and transfer of Value**, why is Value treated as a standard
> library concept rather than a first-class language primitive?

This was the motivation for [CIP-0153][1]. Given the overwhelming importance for validating `Value`,
it makes sense for `BuiltinValue` to have a reasonably disproportionate number of builtin operations
as compared to `BuiltinList` or `BuiltinArray`. The current builtins added in CIP-0153 do not cover
many of the use cases for `Value`. As a reference, see the Aiken stdlib's [functions on `Value`][2].
Functions like `tokens` and `policies` are not possible to implement using the CIP-0153 builtin
functions which means they will not benefit from the new `BuiltinValue` type. Plutus needs enough
builtins to cover the main operations on `BuiltinValue`, either through generalizable builtins or
dedicated ones.

As an example use case, [CIP-89-based distributed dApps][9] rely on special native assets (aka
Beacon Tokens) to tag UTxOs. These Beacon Token tags can then be used by off-chain indexers to
filter the UTxO set to see only the UTxOs relevant to that dApp. This functionality is critical for
supporting self-sovereign DeFi since it enables all users to get their own DeFi addresses - a
requirement for maintaining delegation control of DeFi assets. But as a consequence, these
distributed dApp protocols need to be very careful about how and when these Beacon Tokens are
minted/spent. [Cardano-Swaps][10] checks every transaction output to see if they contain beacon
tokens by calling `tokens` ([here][11]). Since `tokens` is just traversing the `Value` as a `List`,
this is significantly less efficient than the `O(1)` lookup possible by treating `Value` as a `Map`.
This inefficiency compounds when the Cardano-Swaps protocol is executed as part of a larger
transaction cart that involve other outputs and dApps.

## Specification

This CIP proposes adding the following new builtins functions:

```haskell
type BuiltinCurrencySymbol = BuiltinByteString

-- | A constant used for an empty value.
emptyValue :: BuiltinValue

-- | Convert a `BuiltinValue` to a `BuiltinList`. This is useful for pattern-matching.
valueToList :: BuiltinValue -> [(BuiltinCurrencySymbol, (BuiltinTokenName, BuiltinInteger)]

-- | Returns all policy ids found in the value.
policies :: BuiltinValue -> [BuiltinCurrencySymbol]

-- | Return all tokens and their quantities for the specified policy ids. It returns a
-- `BuiltinValue` so that the result can make use of the `lookupCoin` builtin added in CIP-0153.
-- It can always be converted to a `List` for pattern-matching using the `valueData` builtin added
-- in CIP-0153. 
restrictValueTo :: [BuiltinCurrencySymbol] -> BuiltinValue -> BuiltinValue

-- | Filters out the policies from the `BuiltinValue`.
filterOutPolicies :: [BuiltinCurrencySymbol] -> BuiltinValue -> BuiltinValue

-- | The number of policies present. If `BuiltinValue` is tracking its size, this should be a very
-- simple and efficient builtin.
policyCount :: BuiltinValue -> BuiltinInteger

-- | The number of asset names present across all of the policy ids. This could be useful after 
-- first restricting the `BuiltinValue` with `restrictValueTo`. If `BuiltinValue` is tracking 
-- its size, this should be a very simple and efficient builtin. Is this more efficient than
-- pattern-matching on the result of `restrictValueTo`???
assetCount :: BuiltinValue -> BuiltinInteger

-- | Value equality. I'm assuming this is `==`, but just in case it isn't actually supported on
-- `BuiltinValue` I'm adding it here.
valueEquals :: BuiltinValue -> BuiltinValue -> BuiltinBool
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
scaleValue :: BuiltinInteger -> BuiltinValue -> BuiltinValue

-- New functions
emptyValue :: BuiltinValue
valueToList :: BuiltinValue -> BuiltinList
policies :: BuiltinValue -> [BuiltinCurrencySymbol]
restrictValueTo :: [BuiltinCurrencySymbol] -> BuiltinValue -> BuiltinValue
filterOutPolicies :: [BuiltinCurrencySymbol] -> BuiltinValue -> BuiltinValue
policyCount :: BuiltinValue -> BuiltinInteger
assetCount :: BuiltinValue -> BuiltinInteger
valueEquals :: BuiltinValue -> BuiltinValue -> BuiltinBool
```

From these builtin functions, most of Aiken's stdlib `Value` functions can now make use of the
improved efficiency of CIP-0153's `BuiltinValue`. 

### Supported Higher-Level Functions

These are all taken from the [aiken `Value` functions][2].

```haskell
fromAsset :: BuiltinCurrencySymbol -> BuiltinTokenName -> BuiltinInteger -> BuiltinValue
fromAsset pol name quantity = insertCoin pol name quantity emptyValue

fromAssetList :: [(BuiltinCurrencySymbol, (BuiltinTokenName, BuiltinInteger))] -> BuiltinValue
fromAssetList xs = 
  foldr (\(pol, (name, quantity)) acc -> insertCoin pol name quantity acc) emptyValue xs

fromLovelace :: BuiltinInteger -> BuiltinValue
fromLovelace quantity = insertCoin "" "" quantity emptyValue

hasAnyNft :: BuiltinValue -> BuiltinCurrencySymbol -> BuiltinBool
hasAnyNft val pol = not $ null $ valueToList $ restrictValueTo [pol] val
    
hasAnyNftStrict :: BuiltinValue -> BuiltinCurrencySymbol -> BuiltinBool
hasAnyNftStrict val pol = restrictValueTo ["", pol] val == val
    
hasNft :: BuiltinValue -> BuiltinCurrencySymbol -> BuiltinTokenName -> BuiltinBool
hasNft val pol name = lookupCoin val pol name > 0
    
hasNftStrict :: BuiltinValue -> BuiltinCurrencySymbol -> BuiltinTokenName -> BuiltinBool
hasNftStrict val pol name = lookupCoin val pol name > 0 && restrictedResult == val
  where restrictedResult = restrictValueTo ["", pol] val

isZero :: BuiltinValue -> BuiltinBool
isZero = null . valueToList

match
  :: BuiltinValue
  -> BuiltinData
  -> (BuiltinInteger -> BuiltinInteger -> BuiltinBool)
  -> BuiltinBool
match left right_data assert_lovelace = assets_are_equal && lovelace_check_passes
  where
    left_lovelace = lovelaceOf left
    left_assets = withoutLovelace left

    right_value = unValueData right_data
    right_lovelace = lovelaceOf right_value
    right_assets = withoutLovelace right_value

    assets_are_equal = valueData left_assets == valueData right_assets
    lovelace_check_passes = assert_lovelace left_lovelace right_lovelace

lovelaceOf :: BuiltinValue -> BuiltinInteger
lovelaceOf val = lookupCoin val "" ""

policies :: BuiltinValue -> [BuiltinCurrencySymbol]
policies = policies

quantityOf :: BuiltinValue -> BuiltinCurrencySymbol -> BuiltinTokenName -> BuiltinInteger
quantityOf = lookupCoin

tokens :: BuiltinValue -> BuiltinCurrencySymbol -> [(TokenName, Integer)]
tokens val pol = case valueToList $ restrictValueTo [pol] val of
  [] -> []
  (_, ts):_ -> ts

add :: BuiltinValue -> BuiltinCurrencySymbol -> BuiltinTokenName -> BuiltinInteger -> BuiltinValue
add val pol name newQuantity = insertCoin pol name (current + newQuantity) val
  where current = lookupCoin val pol name

merge :: BuiltinValue -> BuiltinValue -> BuiltinValue
merge = unionValue

negate :: BuiltinValue -> BuiltinValue
negate = scaleValue (-1)

restrictedTo :: BuiltinValue -> [BuiltinCurrencySymbol] -> BuiltinValue
restrictedTo val ps = restrictValueTo ps val

withoutLovelace :: BuiltinValue -> BuiltinValue
withoutLovelace = filterOutPolicies [""]

subtractValue :: BuiltinValue -> BuiltinValue -> BuiltinValue
subtractValue val1 val2 = unionValue val1 $ negate val2

flatten :: BuiltinValue -> [(BuiltinCurrencySymbol , (BuiltinTokenName, BuiltinInteger))]
flatten = valueToList

flattenWith 
  :: BuiltinValue 
  -> (BuiltinCurrencySymbol -> BuiltinTokenName -> BuiltinInteger -> a) 
  -> [a]
flattenWith val f = map (\(pol, (name, q)) -> f pol name q) $ valueToList val

reduce 
  :: BuiltinValue 
  -> a 
  -> (a -> BuiltinCurrencySymbol -> BuiltinTokenName -> BuiltinInteger -> a) 
  -> a
reduce val initial f = foldr (\(pol, (name, q)) acc -> f acc pol name q) initial $ valueToList val
```

### Does this create a "Slippery Slope"?

All of the proposed builtins are simple operations commonly found on `Map` data structures. So the
author does not believe this CIP sets a precedence for "builtin bloat".

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

If the preliminary performance investigation was not successful, this CIP should be revised
according to the findings of the experiment. Otherwise, the implementation can proceed:

6. Determine the most appropriate costing functions for modelling the builtin's performance
and assign costs accordingly.
7. Add the new builtin functions to the appropriate sections in the [Plutus Core
Specification][7].
8. Formalize the new builtin functions in the [plutus-metatheory][8].
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
[10]: https://github.com/fallen-icarus/cardano-swaps "Cardano-Swaps"
[11]: https://github.com/fallen-icarus/cardano-swaps/blob/9ec41e7619f5ba9d3dd46dd194e2146098093721/aiken/lib/cardano_swaps/one_way_swap/utils.ak#L328 "`tokens` usage"
