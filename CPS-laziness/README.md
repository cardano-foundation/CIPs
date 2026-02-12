---
CPS: TBD
Title: Approaches to true laziness in UPLC
Category: Plutus
Status: Open
Authors: Koz Ross <koz@mlabs.city>
Proposed Solutions: []
Discussions:
    - Original PR: https://github.com/cardano-foundation/CIPs/pull/?
Created: 2026-02-12
License: Apache-2.0
---

## Abstract

UPLC has strict evaluation, and while `Delay` and `Force` can simulate
non-strictness, it is at the risk of re-evaluation, as a `Delay`ed computation
has no 'memory' of being `Force`d. This means that 'true' laziness or
non-strictness doesn't exist in UPLC, limiting performance.

## Problem

UPLC has [strict evaluation][strict-evaluation]. Given the specifics of the
onchain environment, as well as the inherent predictability and familiarity of
this model, this is a good default choice. However, the ability to delay
evaluation of arguments can sometimes be an advantage for performance. As a
result, many languages offer such a possibility, typically as a pair of 'delay'
and 'force' constructs, which respectively 'wrap up' a computation and 'unwrap'
and evaluate it. Ideally, any such 'wrapped' computation does not get
re-evaluated every time it is 'unwrapped': the computation is evaluated once
when first demanded, then the result is cached. 

UPLC contains the `Delay` and `Force` as part of its specification, which are
designed to provide the ability to delay and request evaluation respectively.
However, there is a significant limitation to these constructs: repeated use of
`Force` on the same `Delay`ed computation forces its recomputation every time.
This is a significant limitation, as now, to avoid unnecessary work, developers
must ensure that `Force` is not used multiple times on the same computation.
While few script or dApp developers write UPLC directly, this problem translates
to any framework or language targeting UPLC. Thus, we cannot have 'true'
laziness (or non-strictness) embedded into UPLC without significant work, if
it's possible at all.

## Use cases

We provide several examples of situations where 'true' laziness would improve
performance, or the developer experience, in ways that are difficult or
impossible to achieve today.

### Memoization or tabulation algorithms

[Memoization][memoization] is an important technique, particularly in functional
programming. It effectively allows us to 'remember' the results of computations
for later use without necessarily having to 'run' the computation right away. In
the context of UPLC, this capability is quite important, as the 'easy' method of
performing memoization involves mutable state, which isn't available. 

Currently, this is difficult to do. While `Delay` and `Force` can provide the
'delayed execution' effect required for memoization, but as `Force` has no
'memory' of whether a `Delay`ed computation has been executed, this mechanism
alone isn't sufficient. While working around this in some settings is possible,
it is not easy, and in many cases can introduce more problems than it solves.

### Easier to write Haskell-like code

One source of friction when writing scripts or dApps for Cardano, particularly
when using Plinth, is that UPLC's strict semantics are quite surprising for
developers familiar with Haskell. While not all developers writing such scripts
are Haskellers, a great many are, and Plinth in particular is designed to be as
transparent as possible to developers familiar with Haskell. However, laziness
is a large part of Haskell's semantics, and currently, providing anything even
similar to it in generated UPLC code from any framework (Plinth or not) is
difficult. This largely stems from `Delay` and `Force` only simulating 'true'
laziness, as it has no 'memory' of which `Delay`ed computations have been forced
or not.

We give a more specific example below using Plutarch to illustrate just how
difficult this can become.

### Boehm-Berrarducci encodings and escape continuations

As part of the [Grumplestiltskin project][grumplestiltskin], we often needed
'auxilliary values' as part of basic operations. Such values may vary _between_
script executions, but not within them, and without these values, the basic
operations in question cannot even be defined. Two good examples of such
'auxilliary values' are finite field order and elliptic curve constants: both
are needed for almost any operation over Galois field elements and elliptic
curves respectively. However, as the goal of Grumplestiltskin is to allow the
use of arbitrary Galois fields and elliptic curves, operations are forced to be
non-specific in these 'auxilliary values', despite any given execution of a
script only using one specific set of such values.

There are two ways to resolve this problem. The first is to force every value of
interest (finite field element or curve point) to carry these 'auxilliary
values'. In Plutarch, this would look like the following:

```haskell
data FieldElement (s :: S) = 
    FieldElement (Term s PNatural) -- the actual element
                 (Term s PPositive) -- the field order

data CurvePoint (s :: S) = 
    CurvePointInfinity |
    CurvePoint (Term s FieldElement) -- x coordinate
               (Term s FieldElement) -- y coordinate
               (Term s PInteger) -- curve A constant
               (Term s PInteger) -- curve B constant
```

However, this has numerous downsides:

* The representations for those values become much larger. This is especially
  bad for field elements, as they go from being (essentially) a single builtin
  `Integer` to requiring a `Data` or SOP encoding. This means higher script
  costs.
* Operations that create new values wouldn't change any of these 'auxilliary
  values'. This means that we would spend a lot of unnecessary effort on
  rebuilding data that never changes.
* Representational reducancy is almost guaranteed. 'CurvePoint' demonstrates
  this clearly: `FieldElement`s already carry the field order, but as we need
  _two_ `FieldElement`s for an elliptic curve point, we end up storing the field
  order twice. Not only is this wasteful, it also can create invalid
  representations we now have to be careful about.

These downsides are not acceptable in the resource-constrained environment of
the chain. The alternative solution is to represent field elements and curve
points as [Boehm-Berrarducci encodings][boehm-berrarducci]. In Plutarch, the
above examples would look like this:

```haskell
data FieldElementBB (s :: S) = 
    FieldElementBB (
        forall (r :: S -> Type) . Term s ((PNatural :--> PPositive :--> r) :--> r)
        )

data CurvePointBB (s :: S) = 
    CurvePointBB (
        forall (r :: S -> Type) . 
            Term s (r :--> (FieldElement :--> FieldElement :--> PInteger :--> PInteger :--> r) :--> r)
            )
```

This approach addresses the disadvantages of the previous attempt:

* As Boehm-Berrarducci encodings are lambdas, they are much smaller than the
  equivalent `Data` or SOP representations. Furthermore, construction of new
  values only requires making a new lambda (which may call the lambdas of other
  Boehm-Berrarducci forms), which is quite efficient.
* As we only _must_ call these Boehm-Berrarducci lambdas when we need to produce
  a result (of a different type), 'fields' of data structures represented this
  way need only be evaluated once. 

However, due to UPLC's inherent strictness, we cannot get the benefit of the
second of these. In fact, even when _composing_ Boehm-Berrarducci forms, we can
end up with surprising blowups in execution unit and memory use, which cannot
always be worked around. 

For an example of such a situation, consider the group operation for curve 
points. If either curve point is the point at infinity, we produce the other
argument, as the point at infinity is the neutral element for the group 
operation. Ideally, we want to return the argument unchanged, and un-evaluated.
However, in a Boehm-Berrarducci encoding, to even _establish_ whether a given
argument is the point at infinity or not, we must call the argument's
continuation in the new lambda. Ideally, this should only happen when needed.
However, this doesn't happen in practice. If we assume the result of the group
operation provides `whenInf` and `whenNot` handlers, and we have argument
Boehm-Berrarducci encodings `k1` and `k2`, we must write the following:

```haskell
k1 (k2 whenInf whenNot) $ \x1 y1 curveA curveB -> 
    k2 (k1 whenInf whenNot) $ \x2 y2 _ _ -> 
        -- rest of the computation
```

As UPLC is strict, the resulting computation ends up evaluating far more than it
should:

* `k2 whenInf whenNot` _must_ be evaluated every time, even if `k1` is _not_ the
  point at infinity; and
* If `k1` is not the point at infinity, `k1 whenInf whenNot` _must_ be
  evaluated, even if `k2` is not the point at infinity.

This means that any performance advantage we could have gained is completely
eliminated, especially if the 'chain of computations' becomes large. Given that
scalar group multiplication on elliptic curves must be done using
[exponentiation by squaring][exponentiation-by-squaring], long 'chains of
computation' are inevitable. 

Using `Delay` and `Force` here is of no help. While making the
arguments to `k1` (and `k2`) delayed would avoid the over-evaluation problem
above, it leads to a different problem: re-evaluation. As delayed computations
in UPLC have no 'memory' of being forced, every force requires re-evaluation. In
cases where we have repeated uses of the same point in a computation, or the
point at infinity, this leads to a _lot_ of duplicate evaluation, which once
again destroys performance. Furthermore, the additional `Delay` and `Force`
required increases code size, potentially linearly with the 'chain of
computation' size.

Thus, currently, no matter what we do, we are forced to choose inefficiency.
This is not a theoretical problem: Grumplestiltskin demonstrates that this
results in significant, and unnecessary, performance penalties. In this
particular case, this is especially painful, as code like this is 'hot' and will
be used often.

## Goals

Aside from the essential goal that 'true' laziness must memoize the results of
evaluations, multiple other goals must be met for any implementation. We define
these below, along with reasons why they are needed.

### Existing scripts must not be affected

Due to the large number of scripts already deployed, adding 'true' laziness to
UPLC should not affect how those scripts run. More specifically, 'true' laziness
should be an explicitly opt-in capability, and any scripts that do not make use
of it specifically should not change in how they run. This goal specifically
precludes 'global' or 'implicit' laziness, as is done in GHC.

This is essential for stability and developer experience, as 'mandatory
retrofits' are impractical at best and impossible at worst. In the context of
the chain this is particularly important, as changing an already-deployed script
is difficult. Furthermore, changing the evaluation semantics of scripts
'globally' is risky in general, as it may cause subtle changes that affect
script logic that may be difficult to detect or solve.

### No changes to existing functionality

Any existing part of UPLC should continue to behave as previously. This
precludes 'extending' or 'retrofitting' `Delay` and `Force`.

The justification for this is similar to the previous goal: scripts that already
exist, or that don't require 'true' laziness, should remain unaffected. However,
there is a secondary reason due to the 'double meaning' of `Force` in UPLC:

* A request to evaluate a `Delay`ed computation; and 
* A stand-in for a type variable instantiation for a builtin.

This would make any 'retrofit' of `Force` both difficult and confusing.

### Minimal

Adding 'true' laziness to UPLC should change as little as is reasonable. While
extending the default universe or adding new builtins are both essentially
inevitable, changes beyond this should be considered carefully, and ideally
avoided. Ideally, `Term` should not change if at all possible.

This goal stems from the desire to reduce the change surface required from
Plutus. While adding new members of the default universe, and new builtins,
involves effort, it fundamentally doesn't require changing UPLC's structure
itself. `Delay` and `Force` in their current form are constructs of `Term`, and
are thus more 'fundamental': the inclusion of anything similar would have
significantly larger knock-on effects, and would be best avoided.

### Universal

It should be possible to 'lazify' any computation that a developer might want,
provided it is not parameterized by arguments. Thus, whether the developer wants
a 'lazified' application of a builtin, a user-defined lambda, or anything
similar, provided that the arguments cannot vary, it should be possible.

This goal stems from developer expectations above all: there should not be any
practical reason why a computation not dependent on arguments _shouldn't_ be
'lazifiable'. Furthermore, this would ensure the maximum number of future use
cases are supported.

## Open Questions

Even within the bounds of the goals listed above, a lot of possibilities remain.
Two questions in particular need to be addressed:

* How will UPLC make 'true' laziness available to developers?
* How should 'true lazy' computations be costed?

Questions of implementation specifics into Plutus' codebase also arise, but we
believe that, once the two prior questions are answered, implementation
specifics should no longer be uncertain.

It's worth noting that the exact semantics of 'true' laziness are not under
dispute: the intent is to mimic `Delay` and `Force` as they currently exist, but
with the possibility of avoiding recomputation. Indeed, it is difficult to
imagine what other semantics we could choose given the goals stated above,
particularly universality. While in theory, 'laziness' (or 'non-strictness')
can and do vary in their behaviour, in practice, given the goal of universality
and the fact that onchain data types are quite varied in their structure, there
really is only one option.

We will discuss the two major open questions in more detail below.

### Making 'true' laziness available

In order for script developers (or perhaps more likely, implementers of
script-writing frameworks like Plinth or Plutarch) to use 'true' laziness, UPLC
must provide suitable constructs. Exactly what this should look like is an
important consideration. Realistically, one of two possibilities is likely:

* A dedicated type for 'wrapped lazy' computations in the default universe,
  together with builtins for building and running such; or
* A new construction within `Term`, similar to current `Force` and `Delay`.

There are benefits and drawbacks to both choices. 'Leaving `Term` alone' has the
advantage of being simpler to implement (and target), but requires some way of
avoiding the strictness of UPLC evaluation to begin with. More precisely, a
careless design for a builtin to 'construct' a 'true' lazy computation could end
up doing nothing: if we end up evaluating the argument to the builtin, we've
gained nothing. Modifying `Term` prevents this problem ever arising, but
will lead to 'knock-on' effects throughout both Plutus and the ecosystem. While
we believe that avoiding modification of `Term` is the better choice, it may
paradoxically end up being _more_ difficult _not_ to modify `Term`.

### Costing 'true' laziness

[Costing][costing], or more precisely the Plutus cost model, is an important
feature of Cardano scripts and their execution. A key part of this is the
costing of builtins, which is based on their arguments. Given that one of the
suggested interfaces for 'true' laziness is via builtins, how such builtins
would be costed may require consideration. The most important aspect is that 
the cost of computing a 'true' lazy computation should only be 'paid' once, as
otherwise, the whole construction is somewhat meaningless. While this isn't
necessarily a huge issue, it must still be considered for any solution based on
builtins.

## Copyright

This CPS is licensed under [Apache-2.0](http://www.apache.org/licenses/LICENSE-2.0).

[grumplestiltskin]: https://github.com/mlabs-haskell/grumplestiltskin
[boehm-berrarducci]: https://okmij.org/ftp/tagless-final/course/Boehm-Berarducci.html
[exponentiation-by-squaring]: https://en.wikipedia.org/wiki/Exponentiation_by_squaring 
[costing]: https://plutus.cardano.intersectmbo.org/docs/delve-deeper/cost-model
[strict-evaluation]: https://en.wikipedia.org/wiki/Evaluation_strategy#Strict_evaluation
[memoization]: https://en.wikipedia.org/wiki/Memoization
