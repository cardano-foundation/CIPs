---
CIP: ????
Title: Sums-of-products in Plutus Core
Authors: Michael Peyton Jones <michael.peyton-jones@iohk.io>
Status: Proposed
Category: Plutus
Created: 2023-01-30
License: CC-BY-4.0
---

# CIP-XXX: Sums-of-products in Plutus Core

## Abstract

Plutus Core does not contain any native support for datatypes.
Instead, users who want to use structured data must _encode_ it; a typical approach is to use [Scott encoding][].
This CIP proposes to add native support for datatypes to Plutus Core, and to use that support to implement more efficient interchange of the script context between the ledger and scripts.
These changes will provide very substantial speed and size improvements to scripts.

## Motivation: why is this CIP necessary?

### Background

#### 1. Datatypes in Plutus Core

The first designs of Plutus Core had native support for datatypes.
In the interest of keeping the language as small and simple as possible, this was removed in favour of encoding datatype values using [Scott encoding][].

Experiments at the time showed that the performance penalty of using Scott encoding over native datatypes was not too great.
But we might expect that we should be able to do better with a native implementation, and indeed we can.

#### 2. 'Lifting' and 'Unlifting'

This section talks about Haskell, but the same problem applies in other languages.

Given a Haskell value, how do you translate it into the equivalent Plutus Core term ('lifting')?
It's clear what to do for a Haskell value of one of the Plutus Core builtin types (just turn it into a constant), but it's much more complicated for a Haskell value that is a datatype value: you have to know how to do all the complicated Scott-encoding work.

This means that it's difficult to specify how to do lifting for structured data.
For example, if we want users (or the ledger!) to create Plutus Core terms representing structured data, it will be difficult to explain how to do it.

There is also the opposite direction: how can we turn a Plutus Core term back into a Haskell value ('unlifting)'?
Again, it's clear how to do this for builtin types and very unclear how to do it for datatypes. 
Doing anything with a Scott-encoded datatype usually requires applying it to arguments and _evaluating_ it.
It's not reasonable to require the Plutus Core evaluator just to work out what a term means.

In practice this makes Plutus Core terms very opaque.

#### 3. The 'Data' Type

The design of the EUTXO model rests on passing arguments to the script for the redeemer, datum, and script context.
But we hit upon the problem of how to _represent_ this information.

The first design was to encode each argument as a Plutus Core term, and pass it directly to the script.
However, this had several problems:
1. At that point, the on-chain form of Plutus Core was typed, and we would ideally want to typecheck the application before peforming it. But this could be expensive.
2. As we saw above, Plutus Core terms representing structured data are very opaque, so using them for redeemers and datums would make those values very opaque to users.
3. Creating the script context would require the ledger to take a Haskell value and lift it into a Plutus Core term, which as we've seen is difficult.

The solution that we chose was to pick a single generic structured data type which would be used for data interchange between the ledger and scripts.
This is the 'Data' type.

However, Data is not the natural representation of structured values inside a script, that would be as datatypes.
So this means we often want a decoding step where the script translates Data into its own representation.

### Problems With the Status Quo

There are a few problems with the status quo.

#### 1. Decoding the Script Context is Too Expensive

As we progressed to more realistic (or indeed, real) examples, two things became clear:
1. Real-world script contexts can be large, especially due to the complexity of values stored in outputs
2. The cost of processing the script context is too high in any case

These combine to make decoding real world script contexts prohibitive in many cases.
Budget profiling of our examples in `plutus-use-cases` revealed that many were spending 30-40% of their budget just on decoding the script context, which is unacceptable.

In reality, this is well known among developers, and most have moved to _not_ decoding the script context, and instead working directly with the underlying Data object.
This is much more error prone, but at least provides a workaround.

#### 2. Everything Can Always be Faster

The Plutus Core interpreter has got a lot faster over the last few years (at least one order of magnitude, possibly two by now).
However, there continues to be relentless pressure on script resource usage.
This will always be the case: no matter how fast we make things, things can _always_ be faster or cheaper and it will improve throughput and save people money.

That means that significant performance gains are always compelling.

#### 3. Creating and Analyzing Plutus Core Terms is Difficult

As discussed above, both lifting and unlifting are currently very tricky or impossible.

## Specification

This specification has two parts: firstly a change to Plutus Core, and secondly a change to the ledger interface to scripts for a new Plutus language version.

### 1. Plutus Core Changes

The following new term constructors are added to the Plutus Core language:[^typed-plutus-core]
```
-- Packs the fields (ts) into a construtor value tagged with i
(constr i ts)

-- Inspects the tag on t and passes its fields to the corresponding case branch
(case t cs)
```

[^typed-plutus-core]: See Appendix 1 for changes to Typed Plutus Core.

The small-step reduction rules for these terms are:

$$
\mathrm{CONSTR\_SUB}\frac{t_i \rightarrow t'_i}{(\mathrm{constr}\ e\ t_1 \ldots t_n) \rightarrow (\mathrm{constr}\ e\ t'_1 \ldots t'_n)}
$$

$$
\mathrm{CASE\_SUB}\frac{t \rightarrow t'}{(\mathrm{case}\ t\ c_1 \ldots c_m) \rightarrow (\mathrm{case}\ t'\ c_1 \ldots c_m)}
$$

$$
\mathrm{CASE\_EVAL}\frac{e \leq m}{(\mathrm{case}\ (\mathrm{constr}\ e\ t_1 \ldots t_n)\ c_1 \ldots c_m) \rightarrow [c_e\ t_1 \ldots t_n]}
$$

$$
\mathrm{CASE\_ERR}\frac{e \gt m}{(\mathrm{case}\ (\mathrm{constr}\ e\ t_1 \ldots t_n)\ c_1 \ldots c_m) \rightarrow (\mathrm{error})}
$$

Note that `CASE_SUB` does not reduce branches and `CASE_EVAL` preserves only the selected case branch.
This means that only the chosen case branch is evaluated, and so `case` is _not_ strict in the other branches.[^strict]

[^strict]: See 'Why is case not stict?' for more discussion.

A new Plutus Core minor language version V is added to indicate support for these terms.
They are illegal before that version.

#### Costing

All steps in the CEK machine have costs, all of which are constant.
This will be new costs for the steps for evaluating `constr` and `case`.

There is a potential problem because `constr` and `case` have a variable number of children, unlike all the existing constructs. The risk is that we could end up doing a linear amount of work but only paying a constant cost.

However:
- `constr`s arguments are all evaluated in turn, so we are sure to pay a linear price.
- `case`'s branches are _not_ all evaluated, but the only place we could do a linear amount work is in selecting the chosen branch. But this can be avoided in the implementation by storing the cases in a datastructure with constant-time indexing.

### 2. Ledger Changes

A new Plutus ledger language L is added to the ledger.
The Plutus Core language version V is both allowed and required in L (since the changes to the ledger-script interface will require sums-of-products). 
Optionally, we may choose to backport support for the Plutus Core language version V to earlier Plutus ledger languages, since it only adds more features.

The ledger-script interface changes in L as follows:
- Instead of the script context argument being a Data object, it is now a Plutus Core term.
- The translation of the script context into Data is replaced by a translation of the script context into a Plutus Core term.

The full specification of the new translation is to be determined in collaboration with the ledger team, but broadly:
- Integers and bytestrings are translated to Plutus Core integers and bytestrings instead of using the `I` and `B` Data constructors.
- Constructors are translated to Plutus Core `const` terms instead of using the Data `Constr` constructor.
- Uses of the `Map` and `List` Data constructors will need more specific handling but will be translated in line with their underlying dataype representation in Plutus Core.

## Rationale: how does this CIP achieve its goals?

### Benefits

#### 1. Avoid Decoding the Script Context

This CIP solves problem 1 in the most drastic way possible: it removes it entirely.
With the proposed ledger interface changes the script context is passed across _already decoded_, so there is zero work for the script to do.

#### 2. Faster Processing of Structured Data

Most Plutus Core programs spend a significant amount of their time operating on datatypes, so we would expect that a performance improvement here would make a significant difference.

Indeed, this seems to be true.
Our benchmarks[^see-appendix-3] show that this CIP leads to 0-30% real-time speedups depending on the program (the 0% is a primality tester that is mostly doing arithmetic, the 30% is mostly doing datatype manipulation). This is a very significant improvement, and should result in a similar reduction in budget usage.

[^see-appendix-3]: See Appendix 3 for the table of results.

#### 3. Simple Lifting and Unlifting

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

#### Is this still worth it if users aren't decoding the script context?

The issues with decoding the script context only apply to users who actually try and decode it; many people have moved on to just using the underlying Data object instead.
Arguably that saps the motivation for this proposal.

There are two responses to this:
1. This proposal seems worth it on the basis of its other benefits (benefits 2 and 3).
2. Removing the problems with decoding the script context may allow users to return to that approach, which can be more ergonomic (and potentially cheaper, since builtin calls are expensive).

### Alternatives

#### 1. Use Sums _and_ Products Instead

The current solution is a sums-of-products solution, i.e. we have an introduction and elimination form for objects that have _both_ a tag and a list of fields.
We could instead separate these two parts out and have an introduction and elimination form for sums, likewise for products.

That would look something like this:
```
-- Tags a term with a tag
(tag i t)
-- Inspects a tagged term for the tag, and passes the 
-- inner term to the case function corresponding to the tag
(case t cs)

-- Constructs a product with the given fields
(prod ts)
-- Accesses the i'th field of the given product
(index i t)
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

## Path to Active

### Acceptance Criteria

- [ ] Implementation in `plutus`, including specification and costing of the new operations
- [ ] Further benchmarking with additional real-world examples
- [ ] `plutus` changes integrated into `cardano-ledger`, including specification

### Implementation Plan

This plan will be implemented by Michael Peyton Jones and the Plutus Core team with assistance from the Ledger team.

A prototype implementation already exists and is functional.

## Appendices

### Appendix 1: Changes to Typed Plutus Core

While Typed Plutus Core is not part of the specification of Cardano, it is still interesting and informative to give the changes here.
Plutus Core was originally conceived of as a typed language, and making sure that we can express the changes cleanly in a typed setting means that we ensure that the semantics make sense and that it will continue to be easy to compile to Plutus Core from typed languages.

We add the following new type constructors to the type language of Typed Plutus Core:
```
(sum tys)
(prod tys)
```
These correspond to sum and product types.
While we are not using sums-and-products at the term level, we can keep it at the type level since that does not affect evaluation.

We add the following new term constructors to the Typed Plutus Core language:
```
(constr ty i ts)
(case ty t cs)
```

These are identical to their untyped cousins, except that they include a type annotation for the type of the whole term. 
These make the typing rules much simpler, as otherwise we lack enough information to pin down the whole type.

The typing rules for the new terms are:

$$
\frac{\Gamma \vdash t_i : ty_i,\ rty = (\mathrm{sum\ s_1 \ldots s_e \ldots s_m}), s_e = (\mathrm{prod}\ ty_1 \ldots ty_n)}{\Gamma \vdash (\mathrm{constr}\ rty\ e\ t_1 \ldots t_n) : rty}
$$

$$
\frac{\Gamma \vdash t : tty,\ tty = (\mathrm{sum}\ s_1 \ldots s_n), s_i = (\mathrm{prod}\ p_{i_1} \ldots p_{i_m}),\ \Gamma \vdash c_i : p_{i_1} \rightarrow \ldots \rightarrow p_{i_m} \rightarrow rty}{\Gamma \vdash (\mathrm{case}\ rty\ t\ c_1 \ldots c_n) : rty}
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
  { P1 r} 
  -- case alternatives
  (\(x : X) (y : Y) -> b1) 
  (\(z : Z) -> b2
]
```

**P3: Explicit construction**

```
constr 1 xx yy
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

#### Nofib

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

## Copyright 

This CIP is licensed under [CC-BY-4.0][].

[CC-BY-4.0]: https://creativecommons.org/licenses/by/4.0/legalcode
[Scott encoding]: https://en.wikipedia.org/wiki/Mogensen%E2%80%93Scott_encoding
