---
CIP: 132
Title: New Plutus Builtin dropList
Status: Proposed
Category: Plutus
Authors:
    - Philip DiSarro <info@anastasialabs.com>
Implementors: []
Discussions:
    - https://github.com/cardano-foundation/CIPs/pull/767
Created: 2024-02-25
License: CC-BY-4.0
---

## Abstract
This document describes the addition of a new Plutus builtin `dropList` with the signature `Integer -> List a -> List a` that drops a given number of elements the list. This drastically increases the efficiency of `elemAt` which is currently a huge throughput bottleneck for many DApps. 

## Motivation: why is this CIP necessary?
The deterministic script evaluation property of the ledger (also stated as "script interpreter arguments are fixed") is a unique characteristic of the Cardano ledger that allows us to perform powerful optimizations that are not possible in systems with indeterminstic script evaluation. For instance, searching for elements in a data structure can 
be done entirely off-chain, and then we simply provide the onchain code with the index (via redeemer) to where the element we want to find is supposed to be, and then check (onchain) that it is indeed the element we were expecting. This design pattern of passing the indices of elements required for validation logic in the redeemer is commonly referred to as redeemer-indexing. 
Even though it is still a very powerful optimization in its current state, it is currently bottlenecked by the lack of a builtin that applies tail a given number of times to a list. Currently, any implementation of `elemAt :: Integer -> List a -> a` or `drop` requires the use of the fixed point combinator (Y combinator) which has a significant cost in onchain code.
                            
Consider the naive approach:
```haskell
{- | Fixpoint recursion. Used to encode recursive functions.
     Hopefully this illustrates the overhead that this incurs. 
-}
pfix :: Term s (((a :--> b) :--> a :--> b) :--> a :--> b)
pfix = phoistAcyclic $
  punsafeCoerce $
    plam' $ \f ->
      plam' (\(x :: Term s POpaque) -> f # plam' (\(v :: Term s POpaque) -> punsafeCoerce x # x # v))
        # punsafeCoerce (plam' $ \(x :: Term s POpaque) -> f # plam' (\(v :: Term s POpaque) -> punsafeCoerce x # x # v))

-- | Lazy if-then-else
-- Two forces + two delays + builtinIfThenElse
pif :: Term s PBool -> Term s a -> Term s a -> Term s a
pif b case_true case_false = pforce $ (pforce $ punsafeBuiltin PLC.IfThenElse) # b # pdelay case_true # pdelay case_false 
     
pelemAt' :: PIsListLike l a => Term s (PInteger :--> l a :--> a)
pelemAt' = phoistAcyclic $
  pfix #$ plam $ \self n xs ->
    pif
      (n #== 0)
      (phead # xs)
      (self # (n - 1) #$ ptail # xs)

pelemAt' # 5 # (pconstant [1,2,3,4,5])
-- the function `self` must be passed as an argument to each recursive call.
-- each recursive call results in:
--   uplc Apply operations to apply the arguments `n` and `xs` to `self`
--   lazy ifThenElse (two forces + two delays + builtinIfThenElse)
--   builtinEqualsInteger
--   builtinSubtractInteger
--   uplc Apply operations to apply the arguments (including `self`, `n` and `xs`) to the fixed-point recursive function
``` 
As you can see, the naive `elemAt` implementation is quite inefficient. This is a huge efficiency bottleneck for many DApps which use `elemAt` many times to locate elements at indices specified in the redeemer. In an attempt to address this, many protocols use the following heuristic optimization (where the number of skips is determined through trial and error based on the DApps throughput in testing):
```
pelemAtFast :: PIsListLike l a => Term s (PInteger :--> l a :--> a)
pelemAtFast = phoistAcyclic $
  pfix #$ plam $ \self n xs ->
    pif
      (n #> 10)
      (self # (n - 1) #$ ptail #$ ptail #$ ptail #$ ptail #$ ptail #$ ptail #$ ptail #$ ptail #$ ptail #$ ptail # xs)
      (pelemAtFast2 # n # xs)

pelemAtFast2 :: PIsListLike l a => Term s (PInteger :--> l a :--> a)
pelemAtFast2 = phoistAcyclic $
  pfix #$ plam $ \self n xs ->
      (pif
         (n #> 5) 
         (self # (n - 5) #$ ptail #$ ptail #$ ptail #$ ptail #$ ptail # xs)
         (pif (n #== 0) (phead # xs) (pelemAt' # (n - 1) # (ptail # xs))))
```
This drastically reduces the amount of recursion we have to do which greatly increases the efficiency of this function in practice. However, it should be clear to see that there is still a huge degree of inefficiency in this implementation. Also it is difficulty to determine the correct magic numbers to skip, and the performance
varies drastically depending on the cut-off values chosen for `n` as-well as the number of different skip-cases (in this case we have skip cases for both `n > 10` and `n > 5`). 

## Specification

### Function definition
We define a new Plutus built-in function with the following type signature:
```haskell
builtinDropList :: BuiltinInteger -> BuiltinList a -> BuiltinList a
```

Similar to the behavior of the `indexOfByteString` builtin, this new builtin will simply error if the provided index is out of bounds for the list.


### Cost Model
Although the `BuiltinList` type is a recursive data-type, costing should be relatively straightforward. 
We propose to define a cost model linear in the size of `n`, the number of elements to drop. What remains is to find a proper coefficient and offset for that linear model, which should be quite easy. 


## Rationale: how does this CIP achieve its goals?
* Easy to implement as it reuses existing code of the Plutus codebase;
* The built-in is generic enough to cover a wider set of use-cases;
* The built-in is still relevant even if we get constant lookup index data-structures since there are occasions where BuiltinList would be preferred;
* This directly addresses the big performance bottleneck that the fixed-point recursion implementation of `elemAt` and `drop` impose on many DApps;

### Alternatives 

- We could decide to accept the heuristic `elemAtFast` implementation as  as an adequate solution.
- We could provide a more generic builtin that applies a function recursively `n` times (seems complicated and bad idea). 
- We could try to reduce the overhead introduced by aspects of the `elemAt` by making the language / compiler more performant (still can't imagine we would be able to get anywhere near the performance of this builtin).

## Path to Active

### Acceptance Criteria
- [ ] Fully implemented in Cardano.
      
### Implementation Plan
- [ ] Passes all requirements of both Plutus and Ledger teams as agreed to improve Plutus script efficiency and usability.
      
## Copyright
This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).

[CC-BY-4.0]: https://creativecommons.org/licenses/by/4.0/legalcode
[Apache-2.0]: http://www.apache.org/licenses/LICENSE-2.0
