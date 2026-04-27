---
CPS: 28
Title: Approaches to non-strict UPLC evaluation
Category: Plutus
Status: Open
Authors:
    - Koz Ross <koz@mlabs.city>
Proposed Solutions: []
Discussions:
    - Original PR: https://github.com/cardano-foundation/CIPs/pull/1150
Created: 2026-02-12
License: Apache-2.0
---

## Abstract

UPLC has [call-by-value][call-by-value] as its evaluation strategy. While
`Delay` and `Force` can be used to adjust when evaluation occurs, it risks
repeat evaluation: a `Delay`ed computation has no 'memory' of being `Force`d.
This means that [non-strict evaluation][non-strict-evaluation] is not easily
implemented in UPLC. This limits convenience, complicates performance, and
inhibits re-use of code, all of which are significant problems for the
applications for which UPLC is designed.

## Problem

UPLC is the language of the onchain Cardano environment: all scripts ultimately
must be written (directly or indirectly) in it. The onchain environment is
strongly resource-constrained, and also has high correctness requirements
relative other code. For that reason, it is essential that UPLC satisfies the
following criteria, in the given order:

1. _Predictability:_ Evaluation of UPLC must behave in an easy-to-understand way
   with regard to performance and resource usage.
2. _Minimalism:_ Optimizing UPLC to use fewer resources must be both possible
   and easy.
3. _Convenience:_ UPLC must not be harder to use to write the sorts of code that
   script developers want. Due to UPLC's low-level nature, this instead
   transfers to making the work of developers of higher-level languages and
   frameworks (such as Plutarch) easier, specifically regarding optimization and
   code generation.

One of the choices made in service of these criteria was the use of [strict
evaluation][strict-evaluation], also known as [call-by-value][call-by-value] for
the SECP machine that runs UPLC programs. This choice as a default is a good one
given the criteria given above, particularly that of predictability.
Furthermore, it is a common, and well-understood, choice, made by many other
languages, satisfying the convenience criterion as well.

At the same time, there are frequently cases where strict evaluation sacrifices
performance. As a result, many languages contain some means of avoiding strict
evaluation in specific cases, while using strict evaluation in general. UPLC
makes some concession to this with the `Force` and `Delay` primitives. More
precisely, `Delay` forces the SECP machine to not evaluate the UPLC term it is
applied to until `Force` is applied. This is effectively ['thunking'][thunking].
However, repeated use of `Force` on the same `Delay`ed term will re-evaluate
that term each time. Thus, while on the surface, it may appear that UPLC can
have on-demand [call-by-need][call-by-need] evaluation, it is in fact up to the
writer of the UPLC (whether a human or a framework) to ensure that `Delay`ed
computations are not recomputed. This is a known problem, described in multiple
places in the Cardano ecosystem: for example, the [Plutarch documentation of 
`Delay` and
`Force`](https://plutarch-plutus.org/Introduction/DelayAndForce.html). 

This limitation makes it difficult to perform the kinds of optimizations done by
languages with 'proper' support for call-by-need, whether language-wide (such as
GHC) or not. This impacts directly on both the minimalism and convenience
criteria:

* Techniques such as shortcut fusion, deforestation or similar, common to
  functional programming (and Haskell in particular) are a tedious, repetitive,
  manual, brittle process, often involving 'dropping out' of a higher-level
  framework or view of the problem.
* Compositionality of code suffers due to unnecessary intermediate allocations
  (if written 'at the high level') or overly-specific re-implementations of more
  general functionality (if written with performance at the forefront).
* When combined with the absence of mutability, there is no general or
  straightforward way to provide the benefits of call-by-need without
  significant work from the developer of either the script, the framework, or
  frequently both.

This creates a situation where 'wheel-reinvention' is not just commonplace, but
practically inevitable, making development longer, more complex, and less
enjoyable, for all concerned. This counts _especially_ for developers coming
from Haskell backgrounds: in particular, Plinth, designed as a direct embedding
_into_ GHC Haskell, ends up forcing its users to re-learn everything they know
due to the change to strict evaluation without any straightforward way to
recover call-by-need. While some limited techniques are available in some
frameworks (for example, [Plutarch pull arrays][plutarch-pull-array]), these
tend to be one-off or niche methods, that take significant effort to design, and
often are still lacking relative what a language like GHC Haskell can do 'for
free'.

## Use Cases

We provide several examples where having call-by-need evaluation would be
beneficial to script developers, framework developers, or both. With UPLC as it
is today, each of these cases is difficult to address, if not impossible.

### List (and stream) fusion

The list is _the_ first-class data structure in UPLC (as in Haskell): almost
anything requiring a linear collection in UPLC must be done with lists. To this
end, GHC Haskell takes significant steps to ensure that intermediate lists are
not generated. For example, code of the form

```haskell
foldl' f x . map g $ xs
```

would be compiled into effectively

```haskell
foldl' (\acc y -> f acc (g y)) x xs
```

This kind of optimization, known as _stream fusion_, is taken essentially for
granted by Haskell developers, who constitute a significant number of Cardano
script and dApp developers as well. This is made possible in large part by GHC
Haskell being a call-by-need language: without it, [problems arise][reuse] with
excessive evaluation. 

Furthermore, in the context of UPLC, these kinds of techniques are even more
important than in a language such as Haskell. This is for two reasons:

* The execution environment for UPLC is far more resource-constrained. Thus,
  intermediate allocations, or any evaluation over the minimum required,
  potentially makes a script unviable far more quickly than an analogous program
  would be in a general computation environment.
* The other major method of avoiding intermediate allocations (mutability) is
  not available at all.

This makes fusion-style techniques extremely important for performance. This is
not a theoretical problem: work done [in Plutarch with pull
arrays][plutarch-pull-array] using another variant of stream fusion, shows
significant performance improvements in array computations, especially as the
'pipeline' of operations becomes larger. 

While it _is_ possible to implement such optimizations without direct support
for call-by-need in UPLC, it is both much more difficult, and much less general.
Solving such problems 'once and for all' is not possible in general, forcing
either narrow and restrictive frameworks or developers hand-rolling fused loops,
which do not generalize and cannot be reused. Plutarch pull array code is a good 
demonstration of this deficiency in action: while it _can_ significantly
out-perform naive code, it cannot eliminate all intermediates, only works for a
small class of operations, and does not interact well with indexing operations
until the array has been 'materialized'. 

Furthermore, in some cases, even such a manual approach is of no help. A good,
if extremely detailed, example of this problem is the [Grumplestiltskin
project][grumple]. As this project is designed to support cryptographic schemes
using elliptic curves over finite fields (and their extensions), many operations
require large numbers of intermediate curve points. These can be fairly
non-trivial structures, involving multiple auxilliary values, with many
intermediate operations, and thus, intermediate structures. In other onchain
languages, this problem is addressed via mutable arrays, an option unavailable
to UPLC. Furthermore, the [fusion-driven solution][grumple-fusion], while
better, is still forced to over-evaluate, without a clear way to avoid it, due
to a lack of true call-by-need. This creates significant performance problems
that simply do not need to exist, but that cannot be solved without
significant, repeated, tedious and _highly_ expert developer work.

### Generating efficient UPLC from Haskell-like code

[Plinth][plinth] (formerly `plutus-tx`) is the standard framework for writing
Cardano scripts, included in the Plutus repositories. It is designed to be a direct
embedding into Haskell: this is in contrast with Plutarch or Aiken, which are
both standard eDSLs. The goal of this choice is to allow any Haskell developer
to be able to write Cardano scripts without having to learn a new language, eDSL
or otherwise.

In practice, however, this goal is not really attained. Plinth is call-by-value,
even though it is embedded in a language that is call-by-need. This happens
because call-by-need is difficult to implement in UPLC without either
significant compiler analysis, or direct user intervention. This is unsatisfying
for both users _and_ maintainers of Plinth:

* Maintainers are forced to provide a sub-par experience, due to
  the difficulty of mimicking familiar Haskell semantics.
* Users are effectively forced to learn a new language _anyway_, as much of what
  they expect to work a certain way in Haskell does not work that way in Plinth.

This problem is particularly apparent in Plinth, but other frameworks, like
Plutarch, do not escape it either. Essentially, any maintainer of any framework
generating UPLC is forced to choose one of the following:

* Completely delegate any responsibility for performance that could be obtained
  via call-by-need to users, bypassing the benefits of the framework; or
* Perform costly and complex analysis as part of their framework's compilation
  pipeline, requiring significant maintenance and testing (as well as subsequent
  fixes when issues inevitably arise), detracting from other maintenance,
  documentation etc.

Stream fusion, as well as many similar techniques, could be
automated, or mostly automated, by such frameworks, just as they are in GHC
Haskell. However, without a straightforward approach to non-strict evaluation in
UPLC, this is difficult or outright impossible without requiring a lot of user
intervention. Furthermore, users are generally not knowledgeable, or interested,
enough to pursue such goals, to say nothing of the result forcing tedious and
error-prone re-implementation of the same general techniques.

## Goals

Any implementation of non-strict evaluation support must meet multiple goals. We
define these below, along with why we feel they are necessary.

### Existing scripts should not become worse

Due to the large number of scripts already deployed, any solution should not
make such scripts worse simply by existing. More specifically, existing scripts
should not consume more resources than they did previously: becoming _more_
efficient is fine, but _less_ efficient would not be. Moreover, the _results_ of
those scripts should not change either. This precludes any 'global' or
'implicit' change in the UPLC evaluation strategy.

This is essential for stability and developer experience, as 'mandatory
retrofits' are impractical at best, and impossible at worst. In the specific
context of the chain, this is particularly important, as changing an
already-deployed script is difficult. Furthermore, changing the evaluation
semantics of scripts 'globally' is risky in general, as this can cause subtle
changes that affect script logic while being difficult to solve.

### Minimal and clear

Adding non-strict evaluation to UPLC should both change as little as is
reasonable, and also not introduce unnecessarily many constructions, or
unnecessarily complex ones. While the _exact_ specifics of 'unnecessarily many'
or 'unnecessarily complex' are hard to gauge, ideally, the mechanism should not
be any more complex to implement or understand than `Force` and `Delay`
currently are.

We need this goal to ensure that both the change surface to Plutus, and the
extra work needed by maintainers of scripts and frameworks is reduced. 

### Universal

It should be possible to use non-strict evaluation on any computation that a
developer might want, provided it is not parameterized by arguments. Thus,
whether a developer wants a non-strict application of a builtin, a user-defined
lambda, or anything similar, provided that the arguments cannot vary, it should
be possible.

This goal stems from developer expectations above all: there should not be any
practice reason why a computation not dependent on arguments should be forced to
be strict. Furthermore, this notion of 'universality' future-proofs us against
the maximum number of possible use cases.

## Open Questions

Even within the bounds of the goals listed above, a lot of possibilities remain.
One question in particular need to be addressed: should `Delay` and `Force` be 
retrofitted to behave as on-demand call-by-need? On the surface, this appears
like an elegant solution, as it is essentially invisible at the user level, 
whether the user is a script developer or a framework developer. However, given
that this retrofit would require `Delay` or `Force` to become more complicated,
the question of performance becomes concerning, especially for existing scripts. 

To see why this could be an issue, consider any existing, optimized script. In
any such script, the developer(s) would have taken care to not `Force` any
`Delay`ed computation more than once. If `Force` were retrofitted to avoid
recomputation, the script does not benefit; however, the added complexity of
`Delay` and `Force` (and associated performance hit) would still be taken by
that script. 

A [test of this kind of retrofit][lazy-delay-force] supports this conclusion to
some degree. The given implementation increases the cost of `Delay` and `Force`
roughly by a factor of 2. However, for existing scripts using `Delay` and
`Force` optimally (that is, not `Force`ing any `Delay`ed computation more than
once), the overhead is less than 3%. However, poorly-optimized programs lose
significantly more, ranging from 10% to as much as 90%. While this suggests that
retrofitting `Delay` and `Force` isn't free, it may be considered worth it over
adding new operations.

## Copyright

This CPS is licensed under [Apache-2.0](http://www.apache.org/licenses/LICENSE-2.0).

[call-by-value]: https://en.wikipedia.org/wiki/Evaluation_strategy#Call_by_value
[non-strict-evaluation]: https://en.wikipedia.org/wiki/Evaluation_strategy#Non-strict_evaluation 
[strict-evaluation]: https://en.wikipedia.org/wiki/Evaluation_strategy#Strict_evaluation
[thunking]: https://en.wikipedia.org/wiki/Thunk#Functional_programming
[call-by-need]: https://en.wikipedia.org/wiki/Evaluation_strategy#Call_by_need
[plutarch-pull-array]: https://www.mlabs.city/blog/performance-pull-arrays-and-plutarch
[costing]: https://plutus.cardano.intersectmbo.org/docs/delve-deeper/cost-model
[lazy-delay-force]: https://github.com/user-attachments/files/26065364/lazy-delay-force.pdf
[plinth]: https://github.com/IntersectMBO/plutus/tree/master/plutus-tx
[reuse]: https://augustss.blogspot.com/2011/05/more-points-for-lazy-evaluation-in.html
[grumple]: https://github.com/mlabs-haskell/grumplestiltskin/tree/milestone-3
[grumple-fusion]: https://github.com/cardano-foundation/CIPs/pull/1150#issuecomment-4172833957
