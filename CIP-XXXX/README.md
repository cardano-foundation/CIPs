---
CIP: ?
Title: First-class errors in Plutus
Category: Plutus
Status: Proposed
Authors:
    - Las Safin <me@las.rs>
Implementors:
    - Las Safin <me@las.rs>
Discussions:
    - https://github.com/cardano-foundation/cips/pulls/?
Created: 2023-03-01
License: CC-BY-4.0
---

## Abstract

Plutus is a strictly evaluated language, where users heavily rely on **impure** errors
to cause transaction failure to rule out invalid cases.

We propose three changes:
- Make `error` a first-class value you can pass around. Using it does not inherently
  cause an error.
- Change condition for script success from not erring to returning `True`.
- Erase type abstractions and type applications entirely when going from
  TPLC to UPLC rather than turning them into `delay` and `force`.

## Motivation: why is this CIP necessary?

Users write code in the style of `if cond then error else False`, which is unidiomatic and also problematic,
since the seemingly equivalent `cond && error` will **always err**.
This is not a good situation, and issues have been opened about it before,
notably https://github.com/input-output-hk/plutus/issues/4114 (over a year ago!).
The issue was righly not deemed a "vulnerability" or "bug", yet it is quite clearly a misfeature.

The current design in fact **encourages impurity**, as the return value of scripts is ignored entirely;
only the effects matter. This is entirely antithetical to the design of Plutus.
With the changes in this CIP, users will naturally return `False` in cases that are
disallowed explicitly, `True` when it's allowed explicitly, and all other cases are
disallowed "implicitly" as they're also not `True`.

There is also the issue of efficiency: `delay` and `force`s have added more of an
overhead than initially assumed, and a common trick used by alternative toolchains is to
avoid emitting these. PlutusTx still emits these as it targets TPLC, the erasure of which into UPLC
adds this overhead.
However, removing this from the erasure itself doesn't just help PlutusTx get closer to the alternative
toolchains, but also means that all built-ins will no longer need to be forced before application.

Making Plutus lazy would also solve the problems, yet this has not been done as a strict language
is easier to reason about wrt. budgetting. Instead, we turn to making errors first-class values.

## Specification

The changes below would need to take effect in a new ledger era and Plutus version.
It is not yet clear which, as that depends on when it gets implemented.

### Plutus Core

To solve this problem at its root, this CIP proposes making errors **first-class values**.
Errors are no longer a special type of term that "infect" their environment, but can instead
be passed around freely. Using an error incorrectly is of course still an error, hence it still
bubbles up in that respect.

We remove the following small-step reduction rule:
```
f {(error)} -> (error)
```
from [Plutus Core Specification](https://github.com/input-output-hk/plutus/blob/72d82f9d04cbef144727fad1f86ce43476e4cc63/doc/plutus-core-spec/untyped-reduction.tex#L133).

#### Built-ins

Errors passed to a built-in only cause an error if the built-in attempts
to inspect it, i.e. morally pattern-match on it in the Haskell definition.

The matter of costing is a bit more complicated:
Arguments are still always in WHNF, and hence we still derive the cost from their
size. We can regard an error as a member of every type, and assign it a size in every type.
The size can be any constant, as it would be if it were explicitly added as a new
constructor to every built-in type.
If it is used, evaluation of the built-in halts immediately.
If it isn't used, it doesn't use any compute.
Whether it should take from the budget if not used is up to the implementors.

### Ledger

[`runPLCScript`](https://github.com/input-output-hk/cardano-ledger/blob/f58187e1f2ebb7bbd9f5c3072cab5b1b6568c93f/eras/alonzo/formal-spec/utxo.tex#L213) from the ledger will need a new version that checks
that the result is `True`, not that it didn't fail. This change can be done
transparently in the Plutus library by adding another version of evaluateScriptRestricting
with an equivalent type but for a new version of Plutus.

## Rationale

Plutus isn't made lazy by this change, errors are instead not immediately propagated up.
Errors are less special-cased now, as evident by the removal of a rule, not addition.

One (somewhat obvious) issue is that `error` isn't the only source of divergence.
As @effectfully pointed out, the following is still problematic:
```haskell
let factorial n = ifThenElse (n == 0) 1 (factorial (n - 1))
in factorial 2
```
The arguments to `ifThenElse` are evaluated first, leading to infinite recursion.
Fixing this would require making Plutus to some extent lazy, which is a much larger change.

Is this change still worth it in light of this?
Even _purely_ for the sake of making scripts more functional, it would still be worth it.
Very few people will make their own `loopforever` function to replicate the old `error` to write impure scripts.
It is a bonus that we in addition 1) simplify the language 2) remove a foot-gun for new Plutusers/Plutors/Plutonites
3) make Plutus scripts more efficient by removing `delay` and `force` from the erasure.

It is not immediately obvious that the third step is possible, as we still have the above issue.
The common example (from [Well-Typed](https://well-typed.com/blog/2022/08/plutus-cores/)) is:
```haskell
let* !boom = λ {a} -> ERROR
     !id   = λ {a} (x :: a) -> x
in λ (b :: Bool) -> ifThenElse {∀ a. a -> a} b boom id
```
Indeed, this example works _without_ adding delays to type abstractions,
as the untyped form
```haskell
f = λ b -> ifThenElse b ERROR (λ x -> x)
```
is precisely the example we seek to make work.
`f True ()` will fail as expected,
while `f False ()` will return `()` as expected.

### Backward compatibility

This CIP has the issue of old scripts not being portable to the new version trivially.
You need to make sure your script isn't making use of any impure assumptions.

## Path to Active

### Acceptance Criteria

It would be needed to implement the necessary changes in `cardano-ledger` and `plutus`.

### Implementation Plan

#### Implementation of built-ins

This section does not have to be followed and is merely initial speculation
on how to implement this feature.

The implementation of built-in functions in the Plutus library must
change to support built-ins that don't inspect all arguments, notably `ifThenElse`.
The naive way would be to translate errors to `undefined` and catch that impurely, yet this is hardly satisfying.

Built-ins defined by `makeBuiltinMeaning` would, for a Plutus function of type `a0 -> a1 -> ... -> an`,
be defined by a Haskell-function `forall m. m a0 -> m a1 -> ... m an` instead.
If you don't bind an argument, it is not used, hence evaluation will still succeed
regardless of whether it is an error.
If it is bound, but is an error, then it will return an error as usual.

To reduce the changes needed, you could instead of changing `makeBuiltinMeaning` provide
an alternative `makeLazyBuiltinMeaning` with the above functionality, changing the original
function to instead bind all arguments immediately, as most built-ins would do anyway.

With this, the implementation of `ifThenElse` would be
```haskell
toBuiltinMeaning DefaultFunVX IfThenElse =
  makeLazyBuiltinMeaning
    (\b x y -> b >>= \case True -> x ; False -> y)
    (runCostingFunThreeArguments . paramIfThenElse)
```

## Copyright

[CC-BY-4.0]: https://creativecommons.org/licenses/by/4.0/legalcode
[Apache-2.0]: http://www.apache.org/licenses/LICENSE-2.0
