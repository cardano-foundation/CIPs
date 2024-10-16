---
CIP: 139
Title: Plutus Core Builtin Type - `ByteStringMap`
Category: Plutus
Status: Proposed
Authors:
    - Michael Peyton Jones <michael.peyton-jones@iohk.io>
    - Ana Pantilie <ana.pantilie@iohk.io>
Implementors: []
Discussions:
    - https://github.com/cardano-foundation/CIPs/pull/921
Created: 2024-10-03
License: CC-BY-4.0
---

## Abstract

We propose a `ByteStringMap` type for Plutus Core. This type will have logarithmic time lookups, which are difficult to achieve in Plutus Core programs today.


## Motivation: why is this CIP necessary?

### Map data structures

A _map_ is a collection of _values_ indexed by _keys_. We consider a map to be _well-defined_ if each key uniquely identifies each value. A basic map implementation provides, at the very least, a way to define an empty map, an operation to insert new key-value associations into an existing map, an operation to lookup values based on an input key and an operation to delete entries from the map.

### Performance and Plutus Core implementations

To provide map operations with good asymptotic performance, it is necessary to implement a fairly complex data structure such as a red-black tree. Implementing such data structures in Plutus Core programs themselves has been attempted multiple times in the past, but unfortunately we have found that the high overhead and large memory cost outweigh any theoretical algorithmic improvements (see [attempt 1][3] and [attempt 2][2]).

The only practical way to implement maps in Plutus Core is by using an association list representation. Lists are known to have poor asymptotic performance for usual map operations. To make matters worse, maps are in many cases central to developing smart contract logic, specifically maps with `ByteString` keys. See [CPS-0013][1] for more details on how smart contracts heavily depend on `ByteString` maps.

Another attempt to mitigate the performance restrictions imposed by the list implementation was to specialise the Plutus Core implementation [into an association list with `ByteString` keys][4]. Unfortunately, this approach also failed.

We concluded that embedding maps into Plutus Core cannot be done without incurring high performance costs.

### Map as a builtin type

The only remaining solution is to consider introducing a builtin map type.

Unfortunately, the builtin language has a significant limitation: it does not allow for higher-order builtin functions. As of the time of writing, builtin functions may not receive other functions as arguments, but there is ongoing work to lift this restriction. However, due to complex design considerations, repeated applications of function arguments will incur high performance costs. Since maps are recursive data structures, these high performance costs will be accumulated and such an approach will still not be feasible.

Why are higher-order builtin functions necessary? Map keys must be processed (or simply, just compared) in order to be able to build and operate over well-defined maps. For arbitrary key types, that would only be possible by passing the required processing or comparison functions as arguments to the builtin functions.

The only way to implement a builtin map with a (builtin) polymorphic key type would be to modify the builtins language itself. A compiler would have to only allow the construction of maps with key types which are known a priori to possess some property (such as a total ordering). The Plutus Core evaluator would have to check for this as well. The implementation itself would not be too complicated, but we must first consider how this would change the formal semantics of the builtins language.

Given the above, the only immediate solution is to implement a builtin map type which is specialised to `ByteString` keys but remains polymorphic in the value type. We believe that this solution should be good enough for most practical use-cases, and maybe even surpass a fully polymorphic map type in performance.


## Specification

We propose the addition of the following builtin type: `ByteStringMap` of kind `Type -> Type`.
- It represents a map associating keys of type `ByteString` with values of any builtin type.
- The new builtin type should be implemented using a tree data structure allowing for logarithmic-time map operations.
- We consider the costing size of a `ByteStringMap` to be equal to the size of its corresponding representation as an association list.
- The binary encoding of `ByteStringMap`s is equivalent to its encoding as an association list.

**Note**: Here `Type` is the universe of all builtin types, since we do not consider types formed out of applying builtin types to arbitrary types to be inhabited.

We propose the following set of builtin functions to accompany the new builtin type:
1. `insertBSMap :: forall v . ByteString -> v -> ByteStringMap v -> ByteStringMap v`
    - it returns a map with the input key updated to the new value, silently discarding any previous value
    - it uses logarithmic time in the `ByteStringMap` argument, linear time in the `ByteString` argument, and logarithmic memory in the `ByteStringMap` argument
2. `lookupBSMap :: forall v . ByteString -> (() -> v) -> ByteStringMap v -> v`
    - it returns the value for a given key in the map; if the key is missing, it returns the default value of type `() -> a` 
    - its implementation depends on, as of the time of writing, ongoing work in supporting higher-order builtin functions; see the next section for the motivation behind this choice
    - it uses logarithmic time in the `ByteStringMap` argument, linear time in the `ByteString` argument and constant memory
3. `deleteBSMap :: forall v . ByteString -> ByteStringMap v -> ByteStringMap v`
    - it returns a map without the key-value association identified by the input key
    - it uses logarithmic time in the `ByteStringMap` argument, linear time in the `ByteString` argument and logarithmic memory in the `ByteStringMap` argument
4. `unionBSMap :: forall v . ByteStringMap v -> ByteStringMap v -> ByteStringMap v`
    - it merges the two input maps, left-biased when there are key collisions
    - it uses linear time in the sum of the first and second arguments, and linear memory in the sum of the first and second arguments
5. `bsMapToList :: forall v . ByteStringMap v -> List (Pair ByteString v)`
    - it transforms the map into an association list
    - the resulting list should be ordered (in ascending order of the keys)
    - it is linear in the size of the `ByteStringMap`
6. `listToBSMap :: forall v . List (Pair ByteString v) -> ByteStringMap v`
    - it transforms an association list into a map, right-biased in the case of duplicate keys
    - it has `O(n * logn)` time complexity, where `n` is the size of the list
    - it has linear space complexity
    - if the input list does not contain duplicate keys and is ordered (in ascending order of the keys), the space and time complexity will be linear

## Rationale: how does this CIP achieve its goals?

### Constructing `ByteStringMap`s

The first concern we have to address is the reasoning behind not introducing a builtin function for constructing empty `ByteStringMap`s. Since maps are polymorphic in the value type, such a function would require receiving a type tag to know which type of concrete empty map to construct. This provides for an awkward interface to users, and it can easily be avoided by delegating the responsibility of constructing empty map constants to the compiler.

`insertBSMap` and `deleteBSMap` remain fundamental operations which we must expose as builtin functions.

One seemingly unnecessary addition is `unionBSMap`, as it may be implemented in Plutus Core by traversing the elements of one of the maps and calling `insertBSMap`. However, as outlined by [CPS-0013][1], `ByteStringMap` should provide an optimal implementation of the Plutus Tx `Value` type, and the operations on `Value`s depend heavily on map unions. Therefore, for performance reasons, we prefer to expose this functionality as a builtin function.

The final map-constructing operation we have decided to include is `listToBSMap`. The motivation for introducing this builtin is providing quick internalisation of `Data` encoded maps. The `Data` encoding of maps is list-based, and is internalised into the builtin language by decoding the data `Map` constructor as a builtin list of pairs. For maps where the key type is `ByteString`, we now offer the optimised representation of `ByteStringMap`, and it is natural that we provide the most cost-efficient way of transforming such lists of pairs into `ByteStringMap`s.

### Querying `ByteStringMap`s

Map lookups are essential, so we must provide `lookupBSMap`, but there remains the question of how to provide a total function with this functionality.

As mentioned earlier, we have decided to base the implementation of this builtin on an upcoming feature, because it is the least invasive way of providing a total implementation and it leverages future improvements to the builtins language.

With the proposed signature of `lookupBSMap`, users will be able to provide any default value for when the lookup fails, including `error`.

### Traversing `ByteStringMap`s

Unfortunately, due to the limitations presented earlier we cannot provide an effective builtin fold over maps.

However, we can provide a transformation to builtin lists, which can be traversed using the existing list builtins. Iteration over the list representation of a map offers access to both the key and value at each step, therefore it is the most general bulk-operator we can expose.

## Path to Active

## Acceptance Criteria

- [ ] The feature is implemented according to the implementation plan and merged into
the master branch of the [plutus repository][5].
- [ ] [cardano-ledger][6] is updated to include new protocol parameters to control costing of
the new builtins.
- [ ] The feature is integrated into [cardano-node][7] and released as part of a hard fork.

### Implementation Plan

The implementation of this CIP should not proceed without an empirical assessment of the effectiveness of the new primitives, as per the following plan:

1. Implement the new primitives according to the specification.
2. Assign a preliminary cost to the new builtin functions. Consider similar operations and their current costs.
3. Create variants of the [existing benchmarks][8] and potentially add some more.
4. Check that the `ByteStringMap` variants are indeed significantly faster.

If the preliminary performance investigation was not successful, this CIP should be revised
according to the findings of the experiment. Otherwise, the implementation can proceed:

5. Determine the most appropriate costing functions for modelling the builtin's performance
and assign costs accordingly.
6. Add the new builtin type and functions to the appropriate sections in the [Plutus Core
Specification][9].
7. Formalize the new builtin type and functions in the [plutus-metatheory][10].
8. The final version of the feature is ready to be merged into [plutus][5] and accepted by
the Plutus Core team.

## Copyright
This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).

[1]: https://cips.cardano.org/cps/CPS-0013 "CPS-0013"
[2]: https://github.com/IntersectMBO/plutus/pull/5697 "red-black-2"
[3]: https://github.com/IntersectMBO/plutus/pull/692 "red-black-1"
[4]: https://github.com/IntersectMBO/plutus/pull/5779 "specialised-bytestringmap"
[5]: https://github.com/IntersectMBO/plutus "plutus"
[6]: https://github.com/IntersectMBO/cardano-ledger "cardano-ledger"
[7]: https://github.com/IntersectMBO/cardano-node "cardano-node"
[8]: https://github.com/IntersectMBO/plutus/tree/master/plutus-benchmark/script-contexts "script-context-benchmarks"
[9]: https://plutus.cardano.intersectmbo.org/resources/plutus-core-spec.pdf "Formal Specification of the Plutus Core Language"
[10]: https://github.com/IntersectMBO/plutus/tree/master/plutus-metatheory "plutus-metatheory"