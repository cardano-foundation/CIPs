---
CIP: 85
Title: Sums-of-products in Plutus Core
Authors: 
  - Michael Peyton Jones <michael.peyton-jones@iohk.io>
Implementors: 
  - Michael Peyton Jones <michael.peyton-jones@iohk.io>
Status: Active
Category: Plutus
Created: 2023-01-30
Discussions: 
  - https://github.com/cardano-foundation/CIPs/pull/455
License: CC-BY-4.0
---

## Abstract

Plutus Core does not contain any native support for datatypes.
Instead, users who want to use structured data must _encode_ it; a typical approach is to use [Scott encoding][].
This CIP proposes to add native support for datatypes to Plutus Core using sums-of-products (SOPs), and to use that support more efficient scripts, and better code-generation for compilers targeting Plutus Core.

## Motivation: Why is this CIP necessary?

### Background

#### 1. Datatypes in Plutus Core

The first designs of Plutus Core had native support for datatypes.
In the interest of keeping the language as small and simple as possible, this was removed in favour of encoding datatype values using [Scott encoding][].

[Experiments](https://github.com/input-output-hk/plutus/blob/96fd25649107658fc911c53e347032bedce624e9/doc/notes/fomega/scott-encoding-benchmarks/results/test-results.md) at the time showed that the performance penalty of using Scott encoding over native datatypes was not too large, and so we could realistically use Scott encoding.
But we might expect that we should be able to do better with a native implementation, and indeed we can.

#### 2. 'Lifting' and 'Unlifting'

This section talks about Haskell, but the same problem applies in other languages.

Given a Haskell value, how do you translate it into the equivalent Plutus Core term ('lifting')?
It's clear what to do for a Haskell value of one of the Plutus Core builtin types (just turn it into a constant), but it's much more complicated for a Haskell value that is a datatype value: you have to know how to do all the complicated Scott-encoding work.

For example:
- `1` lifts to `(con integer 1)` (easy enough)
- `Just 1` lifts to `(delay (lam case_Nothing (lam case_Just [case_Just (con integer 1)])))` (much more complicated)

This means that it's difficult to specify how to do lifting for structured data.
For example, if we want users (or the ledger!) to create Plutus Core terms representing structured data, it will be difficult to explain how to do it.

There is also the opposite direction: how can we turn a Plutus Core term back into a Haskell value ('unlifting)'?
Again, it's clear how to do this for builtin types and very unclear how to do it for datatypes. 
Doing anything with a Scott-encoded datatype usually requires applying it to arguments and _evaluating_ it.
It's not reasonable to require the Plutus Core evaluator just to work out what a term means.

For example:
- `(con integer 1)` clearly unlifts to `1`
- `(delay (lam case_Nothing (lam case_Just [caseJust (con integer 1)])))` should unlift to `Just `, but this is hard to see. Scott encodings are not even canonical (there can be many terms that represent the same Scott-encoded value), so it is hard to know what they represent in general.

In practice this makes Plutus Core terms very opaque and difficult to work with.

#### 3. The `Data` Type

The design of the EUTXO model rests on passing arguments to the script for the redeemer, datum, and script context.
But we hit upon the problem of how to _represent_ this information.

The first design was to encode each argument as a Plutus Core term (using Scott-encoding for structued data), and pass it directly to the script.
However, this had several problems:
1. At that point, the on-chain form of Plutus Core was typed, and we would ideally want to typecheck the application before peforming it. But this could be expensive.
2. As we saw above, Plutus Core terms representing structured data are very opaque, so using them for redeemers and datums would make those values very opaque to users.
3. Creating the script context would require the ledger to take a Haskell value and lift it into a Plutus Core term, which as we've seen is non-trivial.

The solution that we chose was to pick a single generic structured data type which would be used for data interchange between the ledger and scripts.
This is the `Data` type.

However, `Data` is not the natural representation of structured values inside a script, that would be as datatypes.
So this means we often want a decoding step where the script translates `Data` into its own representation.

### Why change anything?

#### 1. Everything Can Always be Faster

The Plutus Core interpreter has got a lot faster over the last few years (at least one order of magnitude, possibly two by now).
However, there continues to be relentless pressure on script resource usage.
This will always be the case: no matter how fast we make things, things can _always_ be faster or cheaper and it will improve throughput and save people money.

That means that significant performance gains are always compelling.

#### 2. Creating and Analyzing Plutus Core Terms is Difficult

As discussed above, both lifting and unlifting are currently very tricky or impossible.

#### 3. Working with Data is Clumsy and Slow

The `Data` type is used in many places as a representation of structured data:
1. The script context is represented as `Data`
2. Some language toolchains that target PLC use `Data` for all structured data, rather than Scott encoding or similar.

However, working with `Data` is not very pleasant.
Deconstructing a datatype encoded as `Data` requires multiple steps, each of which has to go through the builtins machinery, which imposes additional overhead.
Our benchmarks show that this is very 3x slower even than Scott encoding datatypes.

## Specification

### Plutus Core Changes

The following new term constructors are added to the Plutus Core language:[^typed-plutus-core]
```

t ::=
  ...

  -- Packs the fields into a constructor value tagged with i
  | (constr i t...)
  -- Inspects the tag on t and passes its fields to the corresponding case branch
  | (case t t...)
```

Tags start from 0, with 0 being the first case branch, and so on.

[^typed-plutus-core]: See Appendix 1 for changes to Typed Plutus Core.

The small-step reduction rules for these terms are:

$$
\mathrm{CONSTR\_{SUB\_i}}\frac{i \in [0, n], t_i \rightarrow t'_i}{(\mathrm{constr}\ e\ t_0 \ldots t_n) \rightarrow (\mathrm{constr}\ e\ t_0 \ldots t_i' \ldots t_n)}
$$

$$
\mathrm{CASE\_SUB}\frac{t \rightarrow t'}{(\mathrm{case}\ t\ c_0 \ldots c_m) \rightarrow (\mathrm{case}\ t'\ c_0 \ldots c_m)}
$$

$$
\mathrm{CASE\_EVAL}\frac{e \in [0,m]}{(\mathrm{case}\ (\mathrm{constr}\ e\ t_0 \ldots t_n)\ c_0 \ldots c_m) \rightarrow [c_e\ t_0 \ldots t_n]}
$$

$$
\mathrm{CASE\_NOBRANCH}\frac{e \notin [0,m]}{(\mathrm{case}\ (\mathrm{constr}\ e\ t_0 \ldots t_n)\ c_0 \ldots c_m) \rightarrow (\mathrm{error})}
$$

Note that `CASE_SUB` does not reduce branches and `CASE_EVAL` preserves only the selected case branch.
This means that only the chosen case branch is evaluated, and so `case` is _not_ strict in the other branches.[^strict]

[^strict]: See 'Why is case not strict?' for more discussion.

Also, note that case branches are arbitrary terms, and can be anything which can be applied.
That means that, for example, it is legal to use a builtin as a case branch, or an expression which evaluates to a function.
However, the most typical case will probably be a literal lambda.

A new Plutus Core minor language version 1.1.0 is added to indicate support for these terms.
They are illegal before that version.

#### Costing

All steps in the CEK machine have costs, all of which are constant.
There are cost model parameters which set the costs for each step.
This will therefore be new cost model paramters governing the costs for the steps for evaluating `constr` and `case`.

There is a potential problem because `constr` and `case` have a variable number of children, unlike all the existing constructs. The risk is that we could end up doing a linear amount of work but only paying a constant cost.

However:
- `constr`s arguments are all evaluated in turn, so we are sure to pay a linear price.
- `case`'s branches are _not_ all evaluated, but the only place we could do a linear amount work is in selecting the chosen branch. But this can be avoided in the implementation by storing the cases in a datastructure with constant-time indexing.

## Rationale: How does this CIP achieve its goals?

### Benefits

#### 1. Faster Processing of Structured Data

Most Plutus Core programs spend a significant amount of their time operating on datatypes, so we would expect that a performance improvement here would make a significant difference.

Indeed, this seems to be true.
Our benchmarks show that this CIP leads to:

1. A 0-30% real-time speedup in example programs that do generic computation work, versus Scott encoding[^scott-vs-data] (the 0% is a primality tester that is mostly doing arithmetic, the 30% is mostly doing data manipulation). 
2. A small global slowdown of 2-4%.

Note that the speedup from point 1 is inclusive of the slowdown from point 2.

[^scott-vs-data]: See "Can't we just implement datatypes using `Data` itself?" for comparison with using `Data` directly.

#### 2. Simple Lifting and Unlifting

Today, lifting is complicated, and unlifting is mostly impossible.
With this CIP lifting becomes very simple, and unlifting becomes not only possible but simple.
Our prototype implementation contains code-generation to generate lifting and unlifting code in Haskell, but it is straightforward enough that you could easily do it in any language.

There are still some limitations, e.g. you cannot lift or unlift structures that contain functions, but this is not that unusual (similarly, you typically can't serialise such structures).

### Costs

The costs of this proposal are substantial.

Plutus Core today has only 8 kinds of term, this proposal adds 2 more, an increase of 25%.
Additionally, the new term types are the first term types which have a variable number of children.
Both of these changes increase implementation complexity throughout the system: everything that processes Plutus Core terms must now handle the new cases, and handle the variable numbers of children.

This change also modestly expends our novelty budget.
Plutus Core is a deliberately conservative language: for the most part it is just the untyped lambda calculus.
The proposed new features for sums-of-products are also conservative, and follow a very typical pattern.
But they are not _quite_ as standard as the untyped lambda calculus.

Moreover, a change like this would be very painful to reverse, so we should seriously consider the costs before proceeding.

### Discussion

#### Why is case not strict?

This makes it different to all other Plutus Core terms, but we believe it is the expected behaviour: _no_ language has strict case destructuring.

Consider e.g.

```haskell
case (Just 1) of 
   Just x -> print "Success!"
   Nothing -> error "Failure!"
```

Even in a strict language like Rust, nobody would expect this to evaluate the `Nothing` branch and evaluate to an error.

Furthermore, this additional laziness has significant performance benefits, see Appendix 2 for more discussion.

#### Can't we just implement datatypes using `Data` itself?

`Data` is expressive enough to encode datatypes, indeed this is why it is possible to encode the script context into it.
It's performant enough that people who work with the script context as `Data` are able to get by.
Moreover, lifting and unlifting to `Data` is very easy.
So why not just use it to encode _all_ datatypes?[^aiken]

[^aiken]: The Aiken language does this.

There are two reasons:

1. `Data` cannot contain functions, so it's less expressive than either SOPs or Scott-encoding.
2. The performance is much worse.

To justify 2, we benchmarked some list processing using datatypes implemented with SOPs and with `Data`, and the `Data` version is over 3x worse (not accounting for overhead, so the real figure may be higher).

### Alternatives

#### 1. Use Sums _and_ Products Instead

The current solution is a sums-of-products solution, i.e. we have an introduction and elimination form for objects that have _both_ a tag and a list of fields.
We could instead separate these two parts out and have an introduction and elimination form for sums, likewise for products.

That would look something like this:
```
t ::=
  ...

  -- Tags a term with a tag
  | (tag i t)
  -- Inspects a tagged term for the tag, and passes the 
  -- inner term to the case function corresponding to the tag
  | (case t t...)

  -- Constructs a product with the given fields
  | (prod t...)
  -- Accesses the i'th field of the given product
  | (index i t)
```

This is cleaner in some ways, and was the first prototype we implemented, but it has the following problems:
- It adds two more term constructors to the language
- It is significantly slower in practice, because the combined operation of processing a sum-of-products is extremely common

#### 2. Bind Case Variables in the Syntax for Case Branches

The design presented here allows the case branches to be arbitrary terms, which must be evaluated and then applied to the fields.

A more complex design would be to have the bindings for the variables be part of the case expression instead. That is, the current design does this:

```
(case (constr 1 a b) (\x -> t1) (\x y -> t2))
```
(the literal lambdas here could be arbitrary terms)

whereas we could do this:

```
(case (constr 1 x y) (alt x t1) (alt x y t2))
```

The effect of this is that we know statically that we have a function, and we can jump right into evaluating the _body_ of the case branch instead of first having to evaluate it to a function and apply the arguments.

This saves us a small but meaningful amount of overhead at the cost of making the implementation significantly more complex.

We prototyped this version and it was noticeably faster (~10%).
However, performance investigations showed that we can realize a significant amount of the performance gain through other means, leaving only about 3% unclaimed.[^see-appendix-2]
We think that this is an acceptable cost for a simpler implementation.

[^see-appendix-2]: See Appendix 2 for more details.

#### 3. Unsaturated `constr` and `case`

Both `constr` and `case` in this proposal are _saturated_, meaning that they have all of the arguments that they need explicitly provided in the AST.
This is not the only option. 

We could easily have unsaturated `constr`, by making `(constr i)` a _function_ that then needs to be applied to its arguments. 
This would be mildly more complicated to implement, since we wouldn't know how _many_ arguments to expect, and so we would need to always be able to add aditional arguments to a `constr` value, but this would be manageable.

Unsaturated `case` is more complicated. 
While the tag on the scrutinee `constr` value tells us which branch we are going to take in the end, we don't know how many branches we need in total.
In principle we could extend the tags on constructors to include not only the selected tag but also the maximum tag.
That would allow us to know how many case branches we need.
A more serious problem is that we would not be able to be non-strict in the branches any more, as they would be passed as function arguments and hence forced.

The main advantage of unsaturated `constr` and `case` is that it would avoid the need for n-ary terms in the language, as both would then have a fixed number of children.
However, it makes them more complex to work with, and likely less efficient to implement.
Finally, this is simply a less common design, and so conservatism suggests sticking to the more standard approach unless there is a compelling reason not to.

## Path to Active

### Acceptance Criteria

- [x] `plutus` changes
    - [x] Specification 
    - [x] Production implementation
    - [x] Costing of the new operations
- [x] `cardano-ledger` changes
    - [x] Implementation of new ledger language including SOPs
- [x] Further benchmarking 
    - [x] Ensure that regressions on existing scripts do not occur 
    - [x] Check additional real-world examples
- [x] Release
    - [x] New Plutus language version supported in a released node version
    - [x] New ledger language supported in a released node version

### Implementation Plan

This plan will be implemented by Michael Peyton Jones and the Plutus Core team with assistance from the Ledger team.
The changes will be in the `PlutusV3` ledger language at the earliest, which will probably arrive in the Conway ledger era.

## Appendices

### Appendix 1: Changes to Typed Plutus Core

While Typed Plutus Core is not part of the specification of Cardano, it is still interesting and informative to give the changes here.
Plutus Core was originally conceived of as a typed language, and making sure that we can express the changes cleanly in a typed setting means that we ensure that the semantics make sense and that it will continue to be easy to compile to Plutus Core from typed languages.

We add one new type constructors and one auxiliary constructor to the type language of Typed Plutus Core:
```
-- List of types. This is an auxiliarry syntactic form, not a type!
tyl ::= [ty...]

ty ::= 
  ...

  -- Sum-of-products type, has n children, each of which is a list of types
  | (sop tyl...)
```
This corresponds to a sum-of-products type, and it has one list of types for each constructor, giving the argument types.

We add the following new term constructors to the Typed Plutus Core language:
```
t ::= 
  ...

  | (constr ty i t...)
  | (case ty t t...)
```

These are identical to their untyped cousins, except that they include a type annotation for the type of the whole term. 
These make the typing rules much simpler, as otherwise we lack enough information to pin down the whole type.

The typing rules for the new terms are:

$$
\frac{\Gamma \vdash t_i : p_i,\ ty_{\mathrm{result}} = (\mathrm{sop}\ s_0 \ldots s_e \ldots s_m), s_e = [p_0 \ldots p_n]}{\Gamma \vdash (\mathrm{constr}\ ty_{\mathrm{result}}\ e\ t_0 \ldots t_n) : ty_{\mathrm{result}}}
$$

$$
\frac{\Gamma \vdash t : ty_{\mathrm{scrutinee}},\ ty_{\mathrm{scrutinee}} = (\mathrm{sop}\ s_0 \ldots s_n), s_i = [p_{i_0} \ldots p_{i_m}],\ \Gamma \vdash c_i : p_{i_0} \rightarrow \ldots \rightarrow p_{i_m} \rightarrow ty_{\mathrm{result}}}{\Gamma \vdash (\mathrm{case}\ ty_{\mathrm{result}}\ t\ c_0 \ldots c_n) : ty_{\mathrm{result}}}
$$

The reduction rules are essentially the same since the types do not affect evaluation.

### Appendix 2: Performance Analysis

Performance testing of the various prototypes revealed the following interesting facts:
1. Scott encoding is surprisingly performant.
2. It's tricky to say why sums-of-products is so much better.
3. Binding case variables makes a modest difference, but we can achieve the same in other ways.

Let's look at these in turn.

#### Why is Scott encoding so good?

To see why Scott encoding is so good, let's look at what happens when we 1) construct, and 2) destruct a typical datatype value, using sums-of-products but _without_ binding case variables.
We'll do this in the typed setting for clarity.

Let’s consider four programs, corresponding to creation and destruction of `data XYZ = MkXY X Y | MkZ Z`.

**P1: Scott-encoded construction**

```
[
  -- Scott-encoded constructor for MkXY
  (\(x : X) (y : Y) . (/\ R . \(xyc : X -> Y -> R) (zc : Z -> R) . xyc x y) 
  xx 
  yy
]
```

**P2: Scott-encoded destruction**

```
[ 
  { P1 r } 
  -- case alternatives
  (\(x : X) (y : Y) -> b1) 
  (\(z : Z) -> b2
]
```

**P3: Explicit construction**

```
constr 0 xx yy
```

**P4: Explicit matching**

```
case P3 (\(x : X) (y : Y) . b1) (\(z : Z) . b2)
```

P1 vs P3

- P1
  - Evaluate the function, evaluate the argument, apply the argument (x2 for two arguments)
  - Return a closure containing the two arguments in the environment
- P3
  - Allocate an array
  - Evaluate the argument and put it into the array (x2 for two arguments)
  - Return the value containing the tag and the array

P2 vs P4

- P2
  - Evaluate the scrutinee
  - Force the scrutinee (type instantiation)
  - Evaluate the resulting function, evaluate the argument, apply the argument (x2 for two branch arguments)
  - Evaluate the branch function, evaluate the argument, apply the argument (x2 for two constructor arguments)
  - Enter the branch body
- P4
  - Evaluate the scrutinee
  - Look at the tag
  - Evaluate the case branch (x2 for two branch arguments)
  - Apply the branch function to the constructor arguments (x2 for two constructor arguments)
  - Enter the branch body

Scott encoding isn't doing anything clearly unnecessary: it's quite efficient at constructing values (because it just returns a function closure right away), and it's quite efficient at deconstructing values (because it just loads the constructor arguments into an environment and then applies the branch).

In particular, both ways we have to do a similar amount of work in a) evaluating the branch function, b) applying it to its arguments.

#### Why is sums-of-products better at all?

There are a few advantages for sums-of-products.
The most important is that it does not evaluate all the case branches, only the one it needs. Whereas Scott-encoding passes the case branches as simple function arguments, so they are always evaluated before we proceed.

This makes a surprising amount of difference.
We are performing so few steps already for each datatype match that adding a few more to evaluate unused case branches makes a difference.

#### What about binding case variables?

Binding case variables allows us to get rid of some of the work identified in the previous sections.
A `constr` that binds case variables has two differences:
1. The body of the case branch is _known_, rather than potentially being an arbitrary lambda that we will need to resolve by doing evaluation.
2. The constructor arguments can be loaded into the environment _all in one go_, rather than taking requiring multiple steps through the evaluator for each evaluation.

In practice it seems that difference 1 makes a significant amount of difference, because even if the case branch is a literal lambda, we are forced to allocate a value for the lambda.
Optimizing the evaluator to avoid this allocation removes a significant part of the advantage.

Difference 2 does not seem to make as large a difference. If we did see a big difference here then we might want to investigate adding multi-lambdas to Plutus Core in order to gain this benefit in other places. In practice, however, it does not seem to be that significant, and prototypes of multi-lambdas have not performed well.

### Appendix 3: Benchmark results

Throughout, the following commits are referenced:
- `master`: `df9b23f59852d11776fde382720df830c6163238`
- `sums-of-products`: `e98b284204070053b2e64bb66c7aa0832520afec`

These represent somewhat arbitrary snapshots.
The `sums-of-products` branch represents the current prototype, and `master` is it's merge-base with `plutus`'s `master` branch.
These may be updated at a future date.

#### Nofib

These are benchmarks taken from the `nofib` benchmark suite used by GHC.
They are defined in `plutus-benchmark/nofib`.
They are not totally comprehensive, but they represent a reasonable survey of programs that do various kinds of general computation.

These benchmarks are re-compiled from Haskell each time, so the comparison does not represent faster evaluation of the same script, but rather than we can now compile datatype operations using the new terms, which are faster overall.

| Script             | `master` | `sums-of-products` | Change |
|:-------------------|:--------:|:------------------:|:------:|
| clausify/formula1  | 18.99 ms | 14.07 ms           | -25.9% |
| clausify/formula2  | 24.33 ms | 18.10 ms           | -25.6% |
| clausify/formula3  | 66.30 ms | 48.93 ms           | -26.2% |
| clausify/formula4  | 96.71 ms | 72.88 ms           | -24.6% |
| clausify/formula5  | 417.8 ms | 302.7 ms           | -27.5% |
| knights/4x4        | 59.00 ms | 49.18 ms           | -16.6% |
| knights/6x6        | 152.2 ms | 127.8 ms           | -16.0% |
| knights/8x8        | 248.4 ms | 207.6 ms           | -16.4% |
| primetest/05digits | 32.39 ms | 32.33 ms           | -0.2%  |
| primetest/08digits | 58.97 ms | 59.02 ms           | +0.1%  |
| primetest/10digits | 82.44 ms | 82.83 ms           | +0.5%  |
| primetest/20digits | 168.8 ms | 169.3 ms           | +0.3%  |
| primetest/30digits | 246.7 ms | 248.9 ms           | +0.9%  |
| primetest/40digits | 338.8 ms | 341.7 ms           | +0.9%  |
| primetest/50digits | 329.1 ms | 331.1 ms           | +0.6%  |
| queens4x4/bt       | 10.03 ms | 8.904 ms           | -11.2% |
| queens4x4/bm       | 14.18 ms | 12.58 ms           | -11.3% |
| queens4x4/bjbt1    | 12.80 ms | 11.16 ms           | -12.8% |
| queens4x4/bjbt2    | 13.42 ms | 11.90 ms           | -11.3% |
| queens4x4/fc       | 31.96 ms | 28.30 ms           | -11.5% |
| queens5x5/bt       | 132.9 ms | 113.7 ms           | -14.4% |
| queens5x5/bm       | 167.2 ms | 143.1 ms           | -14.4% |
| queens5x5/bjbt1    | 160.8 ms | 137.0 ms           | -14.8% |
| queens5x5/bjbt2    | 167.4 ms | 145.6 ms           | -13.0% |
| queens5x5/fc       | 398.8 ms | 351.5 ms           | -11.9% |

The results indicate that the speedup is more associated with programs that do lots of datatype manipulation, rather than those that do a lot of numerical work (which in Plutus Core means calling lots of builtin functions).
However, we don't see any regression even in the primality tester, which is very numerically heavy (the noise threshold for the benchmarks is ~1%).

#### Validation 

These benchmarks are some real-world examples taken from `plutus-use-cases`.
They are defined in `plutus-benchmark/validation`.
They thus represent real-world workloads.

The validation benchmarks are _not_ recompiled, they are specific saved Plutus Core programs.
These benchmarks thus only show changes in the performance of the Plutus Core evaluator itself.

| Script                   | `master` | `sums-of-products` | Change |
|:-------------------------|:--------:|:------------------:|:------:|
| auction_1-1              | 150.3 μs | 158.6 μs           | +5.5%  |
| auction_1-2              | 652.2 μs | 684.8 μs           | +5.0%  |
| auction_1-3              | 638.2 μs | 678.7 μs           | +6.3%  |
| auction_1-4              | 194.9 μs | 205.9 μs           | +5.6%  |
| auction_2-1              | 153.7 μs | 161.9 μs           | +5.3%  |
| auction_2-2              | 648.8 μs | 687.2 μs           | +5.9%  |
| auction_2-3              | 858.0 μs | 895.6 μs           | +4.4%  |
| auction_2-4              | 638.2 μs | 676.8 μs           | +6.0%  |
| auction_2-5              | 195.1 μs | 205.1 μs           | +5.1%  |
| crowdfunding-success-1   | 182.6 μs | 187.6 μs           | +2.7%  |
| crowdfunding-success-2   | 182.4 μs | 187.9 μs           | +3.0%  |
| crowdfunding-success-3   | 182.2 μs | 187.8 μs           | +3.1%  |
| currency-1               | 237.9 μs | 249.5 μs           | +4.9%  |
| escrow-redeem_1-1        | 331.7 μs | 342.8 μs           | +3.3%  |
| escrow-redeem_1-2        | 330.5 μs | 343.4 μs           | +3.9%  |
| escrow-redeem_2-1        | 386.0 μs | 403.0 μs           | +4.4%  |
| escrow-redeem_2-2        | 385.0 μs | 404.3 μs           | +5.0%  |
| escrow-redeem_2-3        | 386.4 μs | 403.7 μs           | +4.5%  |
| escrow-refund-1          | 134.9 μs | 140.9 μs           | +4.4%  |
| future-increase-margin-1 | 237.8 μs | 250.3 μs           | +5.3%  |
| future-increase-margin-2 | 522.0 μs | 538.2 μs           | +3.1%  |
| future-increase-margin-3 | 521.7 μs | 536.5 μs           | +2.8%  |
| future-increase-margin-4 | 489.9 μs | 508.8 μs           | +3.9%  |
| future-increase-margin-5 | 859.0 μs | 873.8 μs           | +1.7%  |
| future-pay-out-1         | 237.7 μs | 248.7 μs           | +4.6%  |
| future-pay-out-2         | 524.5 μs | 540.3 μs           | +3.0%  |
| future-pay-out-3         | 525.8 μs | 537.7 μs           | +2.3%  |
| future-pay-out-4         | 862.0 μs | 878.5 μs           | +1.9%  |
| future-settle-early-1    | 237.7 μs | 248.6 μs           | +4.6%  |
| future-settle-early-2    | 521.7 μs | 537.5 μs           | +3.0%  |
| future-settle-early-3    | 525.5 μs | 537.1 μs           | +2.2%  |
| future-settle-early-4    | 642.1 μs | 656.0 μs           | +2.2%  |
| game-sm-success_1-1      | 379.3 μs | 391.5 μs           | +3.2%  |
| game-sm-success_1-2      | 166.4 μs | 178.3 μs           | +7.2%  |
| game-sm-success_1-3      | 639.2 μs | 669.1 μs           | +4.7%  |
| game-sm-success_1-4      | 193.5 μs | 206.6 μs           | +6.8%  |
| game-sm-success_2-1      | 379.7 μs | 389.6 μs           | +2.6%  |
| game-sm-success_2-2      | 166.0 μs | 178.5 μs           | +7.5%  |
| game-sm-success_2-3      | 641.2 μs | 670.1 μs           | +4.5%  |
| game-sm-success_2-4      | 193.3 μs | 207.1 μs           | +7.1%  |
| game-sm-success_2-5      | 644.1 μs | 668.8 μs           | +3.8%  |
| game-sm-success_2-6      | 193.6 μs | 206.5 μs           | +6.7%  |
| multisig-sm-1            | 394.5 μs | 405.5 μs           | +2.8%  |
| multisig-sm-2            | 385.2 μs | 392.8 μs           | +2.0%  |
| multisig-sm-3            | 386.5 μs | 394.5 μs           | +2.1%  |
| multisig-sm-4            | 385.8 μs | 404.2 μs           | +4.8%  |
| multisig-sm-5            | 567.7 μs | 583.0 μs           | +2.7%  |
| multisig-sm-6            | 391.7 μs | 405.5 μs           | +3.5%  |
| multisig-sm-7            | 382.7 μs | 394.3 μs           | +3.0%  |
| multisig-sm-8            | 389.3 μs | 395.8 μs           | +1.7%  |
| multisig-sm-9            | 387.1 μs | 404.4 μs           | +4.5%  |
| multisig-sm-10           | 567.4 μs | 583.3 μs           | +2.8%  |
| ping-pong-1              | 320.6 μs | 327.4 μs           | +2.1%  |
| ping-pong-2              | 319.1 μs | 327.0 μs           | +2.5%  |
| ping-pong_2-1            | 182.2 μs | 190.6 μs           | +4.6%  |
| prism-1                  | 139.2 μs | 150.2 μs           | +7.9%  |
| prism-2                  | 404.5 μs | 412.2 μs           | +1.9%  |
| prism-3                  | 339.4 μs | 359.4 μs           | +5.9%  |
| pubkey-1                 | 118.6 μs | 123.7 μs           | +4.3%  |
| stablecoin_1-1           | 962.4 μs | 976.3 μs           | +1.4%  |
| stablecoin_1-2           | 163.7 μs | 174.2 μs           | +6.4%  |
| stablecoin_1-3           | 1.103 ms | 1.120 ms           | +1.5%  |
| stablecoin_1-4           | 174.0 μs | 185.4 μs           | +6.6%  |
| stablecoin_1-5           | 1.391 ms | 1.418 ms           | +1.9%  |
| stablecoin_1-6           | 215.4 μs | 227.5 μs           | +5.6%  |
| stablecoin_2-1           | 962.4 μs | 981.3 μs           | +2.0%  |
| stablecoin_2-2           | 163.5 μs | 174.2 μs           | +6.5%  |
| stablecoin_2-3           | 1.099 ms | 1.117 ms           | +1.6%  |
| stablecoin_2-4           | 173.6 μs | 184.8 μs           | +6.5%  |
| token-account-1          | 174.1 μs | 181.2 μs           | +4.1%  |
| token-account-2          | 312.8 μs | 334.3 μs           | +6.9%  |
| uniswap-1                | 408.0 μs | 425.4 μs           | +4.3%  |
| uniswap-2                | 203.9 μs | 211.7 μs           | +3.8%  |
| uniswap-3                | 1.779 ms | 1.830 ms           | +2.9%  |
| uniswap-4                | 282.6 μs | 297.6 μs           | +5.3%  |
| uniswap-5                | 1.139 ms | 1.180 ms           | +3.6%  |
| uniswap-6                | 276.2 μs | 288.4 μs           | +4.4%  |
| vesting-1                | 339.8 μs | 356.0 μs           | +4.8%  |

This is an average slowdown of 4%, which is not good at all. We do not want to have a negative impact on scripts that don't use the new constructs.

However, this slowdown is very difficult to avoid.
The GHC Core (GHC's intermediate language for Haskell programs) for both versions looks nearly identical, with the only differences being the introduction of new code for the new cases.
We believe that this indicates that GHC simply produces slightly slower code when we have more constructs, even if those code paths are not used.
In particular, there are some threshold effects when you cross certain numbers of constructors.

We tested this by doing an experiment that simply adds new unused constructors to the Plutus Core term type and evaluator frame type.
This caused a slowdown of on average 2%.
That's not enough to completely explain the loss, but we suspect that similar causes account for the rest (investigation is ongoing).

This is still bad -- a slowdown is still a slowdown -- but it's less bad because it's unavoidable if we ever want to increase the size of the language.
We will pay this cost whenever we decide expand the language.
Especially if the cost comes from threshold effects, it may be a one-time cost that we just have to pay on some occasion.

#### Datatypes using 'Data'

This benchmark compares lists implemented three ways: using SOPs, using builtin lists, and using `Data`.
It is defined in `plutus-benchmark/lists`.
The benchmark task is summing a list of 100 integers.
All three versions are using the Plutus Tx compiler, so any overhead is identical, and the only difference is how the list operations are implemented in the end.
There almost certainly is a decent amount of overhead (we did not attempt to measure it here), so the proportional difference in the underlying operations may in fact be greater.

| Benchmark     | CPU budget usage | Memory budget usage |
|:-------------:|:----------------:|:-------------------:|
| SOP lists     | 136797800        | 505300              |
| Builtin lists | 165182654        | 524632              |
| `Data` lists  | 427357685        | 1360262             |

Using `Data` is much worse.
This is not terribly surprising: pattern-matching on a datatype encoded using `Data` requires multiple builtin calls:

- A call to `ChooseData` to identify the type of `Data`
- A call to `UnConstrData` to get the tag and arguments as a builtin pair
- A call to `Fst` to get the tag
- Some number of calls to builtin operations on integers to work out which branch to take given the tag
- A call to `Snd` to get the args
- Some number of calls to `Head`/`Tail` to extract the arguments to be used

On the other hand, for SOPs this is a single machine step.

## Copyright

This CIP is licensed under [CC-BY-4.0][].

[CC-BY-4.0]: https://creativecommons.org/licenses/by/4.0/legalcode
[Scott encoding]: https://en.wikipedia.org/wiki/Mogensen%E2%80%93Scott_encoding

