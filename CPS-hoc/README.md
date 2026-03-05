---
CPS: TBD
Title: Approaches to Higher-Order Costing
Category: Plutus
Status: Open
Authors: Koz Ross <koz@mlabs.city>
Proposed Solutions: []
Discussions:
    - Original pull request: https://github.com/cardano-foundation/CIPs/pull/1146
Created: 2026-02-04
License: Apache-2.0
---

## Abstract

Currently, costing of builtins makes most higher-order builtins (namely those
that take function arguments) impossible to add to Plutus Core. Such builtins
could provide significant performance and functionality improvements, and there
are no semantic reasons that we could not implement such builtins. Thus, an
expansion of the costing of higher-order builtins would allow significant
improvements in terms of expressiveness and performance.

## Problem

[Costing][costing], or the Plutus cost model, is an important feature of Cardano
scripts and their execution. This assigns, to every script, a cost in both
execution units (corresponding to time used) and memory. As part of this, every
Plutus builtin operation is given a cost based on the arguments it is given: the
exact method of calculation used for current builtins is given
[here][plutus-cost-model-doc]. Determining how this cost is calculated is an
important requirement for any new builtin to be added to Plutus Core.

Currently, costs are calculated for builtins on the basis of either the _sizes_
of arguments, or their _value_, the second of which being used only for integers
and bytestring lengths. For the builtins that currently exist, this works fine,
as they are all essentially _first-order_ (meaning, none of them take function
arguments). However, if we ever wanted to add [higher-order][higher-order] builtins 
(specifically those that takes function arguments), this approach becomes
inadequate. More specifically:

* A function's size is not a meaningful indicator of its evaluation costs. Even
  if we have access to the function's code, a small function could require a lot
  of resources to evaluate (for example, it may involve a fixed point finding
  operation).
* A function argument may be called an arbitrary number of times by a
  higher-order builtin. While this may be predictable for some builtins based on
  other arguments given to them, there is no guarantee this can be done in
  general.

Thus, higher-order builtins cannot, in general, be costed at the moment. There
is one notable exception to this case, which used to exist in the `CaseList` and
`CaseData` builtins, with parentheses added for clarity:

```
CaseList :: b -> (a -> [a] -> b) -> ([a] -> b)

CaseData :: (Integer -> [Data] -> b) -> ([(Data, Data)] -> b) -> ([Data] -> b)
-> (Integer -> b) -> (ByteString -> b) -> (Data -> b)
```

We can see that both `CaseList` and `CaseData` are actually 'doubly
higher-order' in their intent: not only do they _take_ functions as arguments,
they also return a function. These could be costed for the following reasons:

* None of the function arguments are ever called by the builtin: we instead construct 
  a 'dispatch function'. This calls the appropriate function argument based on its
  (first-order) argument, and this can be treated as a regular lambda.
* The only thing the 'dispatch function' ends up doing is a pattern match on a
  data type, followed by a dispatch call, which introduces only a fixed and
  known amount of overhead.

While these builtins no longer exist, they represent the maximum capability for
higher-order builtin costing available to us currently.

## Use cases

Higher-order functions are ubiquitous in functional programming, and thus, use
cases abound. While UPLC (and any higher-level language targeting it) gives us
the ability to define many higher-order functions, in some cases, this isn't
efficient, or even sufficient. To demonstrate cases where higher-order builtins
would give us significant benefits, we give a few examples below.

### Builtin arrays and `GenerateArray`

[CIP-138][cip-138] introduced builtin arrays to UPLC, and has been implemented
into Plutus Core. In particular, in addition to the new array type, CIP-138
introduced three builtin operations:

* `LengthOfArray`, which returns the number of elements in its argument as an
  `Integer`;
* `IndexArray`, which given an array and an `Integer` index, produces the
  element at that index in constant time; and
* `ListToArray`, which converts a builtin list into a builtin array with the
  same contents in the same order.

Currently, CIP-138 arrays lack a `Data` encoding, and no existing ledger type
makes use of them. Thus, they currently act as a 'transient' type within
scripts. However, there are two significant limitations to this use case:

* There is no way to programmatically create a builtin array without first going
  through a builtin list; and
* Given an existing array, there is no way to produce a modified version. The
  only option is to first convert to a builtin list (using a hand-rolled loop
  over indexes), then convert to an array again.

Both of these mean that any non-trivial computation involving arrays onchain
requires a large number of intermediate lists. Not only do these take up onchain
resources that shouldn't really have to be spent, given that they require a lot
of 'hand rolling', they increase the possibility of errors (such as the infamous
'off by one'). 

These issues become an even bigger problem if CIP-138 arrays were to get a
native `Data` encoding, or if their use in ledger types were to increase. Unless
scripts only need to check lengths or access elements, working with arrays
provided by datums or ledger types would be much less convenient than for lists,
which would paradoxically make such improvements far less useful than if they
kept using lists.

One solution would be to provide a builtin similar to the following:

```
GenerateArray :: Integer -> (Integer -> a) -> Array a
```

This builtin, which exists in both [`vector`][vector-generate] and
[`massiv`][massiv-generate], is powerful enough to solve both of the stated
problems, and plenty more besides. With a builtin like `GenerateArray`,
constructing many onchain arrays becomes a matter of a single builtin with two
fairly small arguments, rather than an entire builtin list. Additionally, with
the existence of `IndexArray`, 'derived' arrays (that is, modified versions of
arrays that already exist) become very easy if `GenerateArray` is also
available.

Furthermore, the potential of such a builtin is not limited to just solving
these two problems. `GenerateArray` can be used to define a range of operations
over 'pull arrays', with fusion of intermediate structures being done
automatically. For example, if we consider the following operations:

```haskell
mapArray :: (a -> b) -> Array a -> Array b

zipArray :: (a -> b -> c) -> Array a -> Array b -> Array c
```

we then note that we have the following rewrites, which can be done
automatically:

* `mapArray f . generate len g = generate len (f . g)`
* `zipArray f (generate len1 g1) (generate len2 g2) = generate (min len1 len2) (\i -> f (g1 i) (g2 i))`
* `mapArray f . mapArray g = mapArray (f . g)`
* `zipArray f (mapArray g1 arr1) (mapArray g2 arr2) = zipArray (\x y -> f (g1 x) (g2 y)) arr1 arr2`

This allows 'collapsing' a large pipeline of operations into just a single call
to a builtin, with a few compositions. Such techniques have already [demonstrated
their performance benefits][pull-array-article], but are fundamentally _still_
required to use an intermediate builtin list to produce a builtin array.

The availability of `GenerateArray` would enable a large number of optimization
techniques, as well as many other array operations, to be defined easily. This
could make CIP-138 arrays much better to use for everyone. However, given
current limitations, such a builtin could not be costed. 

### Programmable bootstrapping with TFHE

[TFHE][tfhe] is an approach to [fully homomorphic
encryption][homomorphic-encryption]. More specifically, TFHE allows us to
operate on encrypted data without decrypting it first, using a (representation
of) any Boolean circuit, which can _also_ be encrypted if desired. This second
capability (termed 'programmable bootstrapping') is powerful, and highly
complementary to the chain itself. We have discussed the specific ways in which
TFHE onchain could be beneficial [elsewhere][tfhe-cps] in more detail.

To make this possible, we would need a builtin such as the following:

```
TfheApply :: ByteString -> ByteString -> ByteString
```

Here, the first argument is an (encrypted) representation of a Boolean circuit,
and the second is some encrypted data to apply the circuit to. The result is
also encrypted. 

Although `TfheApply` isn't technically higher-order, costing such an operation
would run into many of the same problems. Furthermore, unlike `GenerateArray`
above, where we at least have some understanding of what the argument and
computation are, with `TfheApply`, we know almost nothing (by design). In some
sense, `TfheApply` represents a 'worst-case' situation for higher-order costing,
as we have almost no information to go on about what the computation being done
is, or what said computation is being applied to.

## Goals

The primary goal would be to find a solution that allows as many higher-order
builtins to be costed as possible. While something like `TfheApply` is unlikely
to ever be costable in practice, `GenerateArray` or similar could be. 

One major
component of this goal would be some means to determien the impact of a function
argument on the cost of a builtin, similarly to how size and value are used now
for first-order arguments. It is quite likely that not every function could be
'measured' in this way (something we discuss further in the 'Open Questions'
section), it is likely that a non-trivial number could be. Another component
would be some ability for the model to be 'told' that the number of calls to a
function argument is bounded in some way: for example, `GenerateArray` described
above would call its function argument exactly `max (0, n)` where `n` is the
`Integer` argument specifying desired length. This 'bound' may not be an exact
number, but a range (for example 'at most once', 'between `n` and `2n` times,
etc), which would also ideally be possible to cost.

Furthermore, it would benefit future contributors of builtins if the specifics
of which higher-order builtins can be costed and why was documented in an
easily-accessible way, regardless of what
'expansion' of current costing possibilities we consider. This would need to
explain the principles of how costing is performed, and what exactly the
limitations of the costing mechanism are.

## Open Questions

The largest open question for any expansion of higher-order costing capabilities
is this: how do we 'measure' a function argument? In the context of UPLC, we
have an advantage in that any function's body is 'visible' to us (in the sense
that we have its source available). However, in order to 'measure' a function
without simulating it, we have to consider the 'static analyzability' of UPLC.
Being an untyped lambda calculus, UPLC is very powerful, being capable of
expressing a [fixed-point combinator][fixed-point]. Any function argument
containing a fixed-point combinator application could essentially run for an
arbitrary amount of time, and thus consume arbitrary resources, and in general,
trying to determine any useful 'measure' for arbitrary UPLC functions would
amount to solving the halting problem.

This naturally leads to another open question: what should we do about the
possibility of fixed-point combinators in function arguments? This question is
difficult to answer for two reasons. Firstly, fixed-point combinators are not unique
(although practically, only a few would ever get used), and there are in fact
[infinitely many possible fixed-point combinators][infinite-fixed-points]. Secondly, 
it is considered good practice to use [CTFE][ctfe] on applications of a
fixed-point combinator to avoid the overhead of purely 'administrative' beta
reductions (namely, ones which aren't dependent in any way on the argument). An
example of this using the [X combinator][x-combinator] with an arbitrary `F`
applied:

```
1. X F -- initial
2. (\f -> M (\y -> f y y)) F -- definition of X
3. M (\y -> F y y) -- beta reduction
4. (\x -> x x) (\y -> F y y) -- definition of M
5. (\y -> F y y) (\y -> F y y) -- beta reduction
```

This construction 'hides' the existence of the fixed-point combinator originally
used, which would make its detection even harder. This technique is not
theoretical: at minimum, [Plutarch][plutarch-fix] makes use of it for reasons of
efficiency.

Outright banning fixed-point combinators from UPLC, while providing a
'canonical' fixed-point combinator application in UPLC `Term`s would be a
possible solution to this problem, but this is unlikely to be workable: since
UPLC is an untyped calculus, fixed-point combinators can exist in it, and making
them un-constructable is a large undertaking, possibly requiring quite invasive
changes. While this could arguably be part of a larger slate of improvements to
UPLC, this would put it firmly outside the scope of this CPS. However, without
_some_ way of handling the 'measuring' of applications of a fixed-point, it is
hard to see how 'measuring' function arguments in general could ever happen.

Another possibility would involve restricting function arguments to higher-order
builtins to only applying builtins. This would avoid the problem of fixed-point
combinator use, as no builtin provides this capability. This, however, is
extremely restrictive: in particular, the standard `let` transform is forbidden
by this. Arguably, this is less of a problem, as adding a `let` 'arm' to UPLC
`Term`s is both easy and backwards-compatible. Furthermore, it is worth mentioning 
that many (arguably even most) higher-order builtins
would not require (or even want) function arguments that apply arbitrary
functions.

## Copyright

This CPS is licensed under [Apache-2.0](http://www.apache.org/licenses/LICENSE-2.0).

[cip-138]: https://cips.cardano.org/cip/CIP-138
[vector-generate]: https://hackage-content.haskell.org/package/vector-0.13.2.0/docs/Data-Vector-Generic.html#v:generate
[massiv-generate]: https://hackage-content.haskell.org/package/massiv-1.0.5.0/docs/Data-Massiv-Array.html#v:makeArray 
[pull-array-article]: https://www.mlabs.city/blog/performance-pull-arrays-and-plutarch
[tfhe]: https://tfhe.github.io/tfhe/
[homomorphic-encryption]: https://en.wikipedia.org/wiki/Homomorphic_encryption 
[tfhe-cps]: https://github.com/mlabs-haskell/CIPs/blob/tfhe/CPS-tfhe/README.md
[costing]: https://plutus.cardano.intersectmbo.org/docs/delve-deeper/cost-model
[plutus-cost-model-doc]: https://github.com/IntersectMBO/plutus/blob/master/doc/cost-model-overview/cost-model-overview.pdf
[higher-order]: https://en.wikipedia.org/wiki/Higher-order_function
[fixed-point-combinator]: https://en.wikipedia.org/wiki/Fixed-point_combinator
[infinite-fixed-points]: https://www.brics.dk/RS/04/25/BRICS-RS-04-25.pdf
[ctfe]: https://en.wikipedia.org/wiki/Compile-time_function_execution
[x-combinator]: https://en.wikipedia.org/wiki/Fixed-point_combinator#Other_fixed-point_combinators
[plutarch-fix]: https://github.com/Plutonomicon/plutarch-plutus/blob/master/Plutarch/Internal/Fix.hs#L54-L65
