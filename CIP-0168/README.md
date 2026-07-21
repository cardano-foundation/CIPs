---
CIP: 168
Title: More `BuiltinValue` Functions
Category: Plutus
Status: Proposed
Authors:
    - fallen-icarus <modern.daidalos@gmail.com>
Implementors: []
Discussions: 
    - Original PR: https://github.com/cardano-foundation/CIPs/pull/1090
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

## Motivation: Why is this CIP necessary?

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

### Use Cases for the Proposed Builtins

#### Validating Protocol Tokens Independently of DeFi Tokens

Many real-world contracts revolve around *protocol tokens*: native assets that a dApp mints and
manages to authenticate UTxOs, track on-chain state, or tag UTxOs for off-chain indexing. Examples
include the authentication/state tokens used by state machine style contracts, and the Beacon Tokens
of [CIP-89-based distributed dApps][9], which off-chain indexers use to filter the UTxO set to see
only the UTxOs relevant to that dApp. Misusing a protocol token breaks the protocol's security, so
these contracts must carefully validate the `Value` of every relevant input and output - making them
heavy users of `Value` operations. Crucially, the protocol tokens require different checks than the
DeFi tokens (e.g. the assets being traded) sitting next to them in the same `Value`.

Consider a CIP-89 limit order UTxO offering ADA for DJED. In addition to the offered ADA, it must
contain *exactly* three protocol tokens: one encoding the trading pair, one encoding the offered
asset, and one encoding the asked asset. Any extra or missing protocol token is a security issue.
Today, validating this requires traversing the `Value` as a list and pattern-matching on expected
assets as you go, which is error prone: a missed pattern match in one such protocol previously
allowed withdrawing protocol tokens to invalid UTxOs. A safer pattern is to split the value into
protocol tokens (`keepPolicies [protocolPolicy]`) and everything else (`dropPolicies
[protocolPolicy]`), then validate each part independently:

```haskell
-- 1. Ensure exactly 3 protocol tokens exist.
assetCount protocolValue == 3

-- 2. Ensure the specific required tokens are the ones present.
lookupCoin protocolValue protocolPolicy pairTokenName == 1
lookupCoin protocolValue protocolPolicy offerTokenName == 1
lookupCoin protocolValue protocolPolicy askTokenName == 1
```

This is both more legible for auditors and less error prone than manual traversal. This
split-and-validate pattern can be exposed directly as a higher-level `splitValue` function (see the
Rationale section below).

The new builtins also compose with the CIP-0153 ones for exact burn validation: a protocol that
must burn all protocol tokens across many input UTxOs can: (1) extract them from each input with
`keepPolicies`, (2) accumulate them with `unionValue`, (3) negate with `scaleValue (-1)`, and (4)
check the result exactly matches `keepPolicies [protocolPolicy] txInfoMint`. Each step operates on
the efficient `BuiltinValue` representation, versus today's repeated list traversals.

#### Bounding Output Value Size

`assetCount` prevents multi-step locking/bricking vulnerabilities. When a contract requires an
output with `value >= someValue`, a maliciously compliant transaction can include hundreds of
garbage tokens, making subsequent spends of that output prohibitively expensive. `assetCount output
<= n` gives a cheap upper bound while still allowing honest users to include extra tokens.

#### Preserving Cheap Lovelace-Only Operations

Because of the min-ADA requirement, every UTxO a contract manages carries lovelace even when the
contract only cares about the non-ADA tokens. State machine style contracts therefore check

```haskell
withoutLovelace (txOutValue ownInput) == withoutLovelace (txOutValue ownOutput)
```

on every state transition to ensure the state token is preserved while users remain free to
adjust the ADA (e.g. to satisfy min-ADA after a datum change). Today this is an O(1) operation
on the `Data` encoding: scripts simply drop the first entry of the outer map, relying on the
ledger's guarantee that ADA, when present, is always the first entry. A naive port to
`BuiltinValue` would silently make this very common pattern more expensive. This motivates the
lovelace-specific representation and costing recommended in the Specification's "A Note on
Lovelace", rather than any new builtin.

## Specification

This CIP proposes adding the following new builtins functions:

```haskell
type BuiltinCurrencySymbol = BuiltinByteString

-- | Returns all policy ids found in the value, in ascending order.
policies :: BuiltinValue -> [BuiltinCurrencySymbol]

-- | Returns a new value containing only the entries for the specified policy ids. It returns a
-- `BuiltinValue` so that the result can make use of the `lookupCoin` builtin added in CIP-0153.
-- It can always be converted to a `List` for pattern-matching using the `valueData` builtin added
-- in CIP-0153.
keepPolicies :: [BuiltinCurrencySymbol] -> BuiltinValue -> BuiltinValue

-- | Returns a new value without the entries for the specified policy ids.
dropPolicies :: [BuiltinCurrencySymbol] -> BuiltinValue -> BuiltinValue

-- | The number of distinct (policy id, token name) pairs in the value. This could be useful after
-- first restricting the `BuiltinValue` with `keepPolicies`. The addition of this builtin is
-- conditional upon the Plutus team verifying that the efficiency gain (over pattern-matching on
-- the result of `keepPolicies`) justifies it. 
assetCount :: BuiltinValue -> BuiltinInteger
```

Precise semantics for `keepPolicies` and `dropPolicies`:

- The result is always a well-formed `BuiltinValue`.
- Policy ids in the argument list that are absent from the value are ignored, and duplicate policy
  ids in the list have no additional effect.
- Lovelace is identified by the empty policy id (`""`).
- The two functions are duals: for any list of policy ids `ps`,
  `unionValue (keepPolicies ps v) (dropPolicies ps v) == v`.

### A Note on Lovelace

Lovelace is unique among the entries of a value: the ledger's min-ADA requirement means
essentially every UTxO contains a lovelace entry, and the ledger guarantees that, when present,
lovelace is always the first entry of a value. Operations that touch only the lovelace entry,
such as `withoutLovelace`, are therefore extremely common and deserve special treatment in the
implementation rather than a dedicated builtin. This CIP recommends that the Plutus
implementation store the lovelace entry outside the map in a separate field (mirroring the
ledger's `MultiAssetValue` representation, which separates ADA for exactly this reason) and
assign cheaper costs to lovelace-only operations, i.e. those where both the policy id and the
token name are empty. See the Rationale section for why this matters.

## Rationale: How does this CIP achieve its goals?

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
policies :: BuiltinValue -> [BuiltinCurrencySymbol]
keepPolicies :: [BuiltinCurrencySymbol] -> BuiltinValue -> BuiltinValue
dropPolicies :: [BuiltinCurrencySymbol] -> BuiltinValue -> BuiltinValue
assetCount :: BuiltinValue -> BuiltinInteger
```

From these builtin functions, most of Aiken's stdlib `Value` functions can now make use of the
improved efficiency of CIP-0153's `BuiltinValue`.

### Supported Higher-Level Functions

These are all taken from the [aiken `Value` functions][2].

```haskell
-- | The empty value can be constructed using constants:
--  (Constant () (Some (ValueOf DefaultUniValue Value.empty)))
emptyValue :: BuiltinValue

-- | `BuiltinValue` equality check.
equalsValue = equalsData

valueToList :: BuiltinValue -> BuiltinList (BuiltinPair BuiltinData BuiltinData)
valueToList =  unsafeDataAsMap . valueData

fromAsset :: BuiltinCurrencySymbol -> BuiltinTokenName -> BuiltinInteger -> BuiltinValue
fromAsset pol name quantity = insertCoin pol name quantity emptyValue

fromAssetList :: [(BuiltinCurrencySymbol, (BuiltinTokenName, BuiltinInteger))] -> BuiltinValue
fromAssetList xs = 
  foldr (\(pol, (name, quantity)) acc -> insertCoin pol name quantity acc) emptyValue xs

fromLovelace :: BuiltinInteger -> BuiltinValue
fromLovelace quantity = insertCoin "" "" quantity emptyValue

hasAnyNft :: BuiltinValue -> BuiltinCurrencySymbol -> BuiltinBool
hasAnyNft val pol = not $ null $ valueToList $ keepPolicies [pol] val
    
hasAnyNftStrict :: BuiltinValue -> BuiltinCurrencySymbol -> BuiltinBool
hasAnyNftStrict val pol = keepPolicies ["", pol] val == val
    
hasNft :: BuiltinValue -> BuiltinCurrencySymbol -> BuiltinTokenName -> BuiltinBool
hasNft val pol name = lookupCoin val pol name > 0
    
hasNftStrict :: BuiltinValue -> BuiltinCurrencySymbol -> BuiltinTokenName -> BuiltinBool
hasNftStrict val pol name = lookupCoin val pol name > 0 && restrictedResult == val
  where restrictedResult = keepPolicies ["", pol] val

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
tokens val pol = case valueToList $ keepPolicies [pol] val of
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
restrictedTo val ps = keepPolicies ps val

-- | Lovelace is unique; see "A Note on Lovelace" in the Specification. This is deliberately
-- listed without a definition in terms of the builtins: deriving it from `dropPolicies [""]`
-- (or CIP-0153's `insertCoin "" "" 0`) at their general worst-case costs would lose the O(1)
-- behavior scripts rely on today. With the lovelace entry stored in a separate field, this
-- becomes a cheap constant-time operation.
withoutLovelace :: BuiltinValue -> BuiltinValue

subtractValue :: BuiltinValue -> BuiltinValue -> BuiltinValue
subtractValue val1 val2 = unionValue val1 $ negate val2

flatten :: BuiltinValue -> BuiltinList (BuiltinPair BuiltinData BuiltinData)
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

### New Higher-Level Functions Enabled by this CIP

The proposed builtins do not just accelerate the existing Aiken stdlib surface; they also enable
new higher-level functions that cannot be offered today. For example, the split-and-validate
pattern from the Motivation can be packaged as a single function:

```haskell
-- | Split a value into (the entries for the specified policy ids, everything else). Useful for
-- validating protocol tokens independently of the assets sitting next to them in the same value.
splitValue :: [BuiltinCurrencySymbol] -> BuiltinValue -> (BuiltinValue, BuiltinValue)
splitValue ps v = (keepPolicies ps v, dropPolicies ps v)

-- | The complement of `restrictedTo`.
withoutPolicies :: BuiltinValue -> [BuiltinCurrencySymbol] -> BuiltinValue
withoutPolicies val ps = dropPolicies ps val
```

### Why `withoutLovelace` is Treated as Unique

As described in the Motivation, `withoutLovelace` is a very common operation (state machine style
contracts use it on every state transition) that is O(1) on today's `Data` encoding thanks to the
ledger's ADA-first guarantee. Naively porting it to `BuiltinValue` loses this property: it could
be expressed as `dropPolicies [""]` or as CIP-0153's `insertCoin "" "" 0`, but both would be
costed for their worst case, making the ported version more expensive than the status quo. A
`BuiltinValue` is backed by a balanced binary tree, where removing the smallest key is no
cheaper than removing any other key.

Rather than adding a dedicated `withoutLovelace` builtin, the discussion converged on treating
lovelace as unique in the implementation: store the lovelace entry outside the map in a separate
field and cost lovelace-only operations cheaply. This mirrors the ledger's own `MultiAssetValue`
representation, which separates ADA for exactly this reason. See "A Note on Lovelace" in the
Specification.

### Does this create a "Slippery Slope"?

All of the proposed builtins are simple operations commonly found on `Map` data structures. So the
author does not believe this CIP sets a precedent for "builtin bloat".

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

5. Determine the most appropriate costing functions for modelling the builtin's performance
and assign costs accordingly.
6. Add the new builtin functions to the appropriate sections in the [Plutus Core
Specification][7].
7. Formalize the new builtin functions in the [plutus-metatheory][8].
8. The final version of the feature is ready to be merged into [plutus][3] and accepted by
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
