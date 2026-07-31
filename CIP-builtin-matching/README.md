---
CIP: "?"
Title: Builtin pattern matching in Untyped Plutus Core
Category: Plutus
Status: Proposed
Authors:
  - Seungheon Oh <seungheon.oh@iohk.io>
Implementors:
  - Seungheon Oh <seungheon.oh@iohk.io>
Discussions:
  - Original PR: https://github.com/cardano-foundation/CIPs/pull/1236
  - Implementation PR: https://github.com/IntersectMBO/plutus/pull/7852
Created: 2026-07-30
License: CC-BY-4.0
---

## Abstract

This proposal adds a `Match` term and a universe-specific builtin-pattern type to Untyped Plutus Core (UPLC). `Match` performs ordered, recursive pattern matching on builtin constants and can capture values from nested `Data`, integers, byte strings, lists, and pairs. Captured values are applied to the handler associated with the first successful pattern.

The proposal addresses the limited expressiveness of builtin `Case`, especially when deconstructing known `Data` structures such as script contexts. It retains `Case` for inexpensive shallow dispatch while providing a more expressive operation for direct and nested matching. Matching work is charged incrementally according to the pattern operations, structural traversal, and failed alternatives performed at runtime.

This proposal covers UPLC syntax and serialization, CEK evaluation, costing, and conformance tests. Typed Plutus Core (TPLC), Plutus IR (PIR), Plinth, PlutusTx libraries, and compiler optimizations that generate or transform `Match` are outside its initial scope.

## Motivation: Why is this CIP necessary?

Builtin casing extended the `Case` term so that it can inspect builtin constants of type integer, list, boolean, and unit. Because a `Case` branch carries no pattern information, its meaning is fixed by its position. For integers, for example, the first branch matches `0`, the second matches `1`, and so on.

This limited form of casing still provides significant performance improvements for integers, lists, and booleans because it avoids the overhead of calling builtin functions. Similar improvements are desirable for `Data`, the builtin type most often used to represent smart-contract inputs.

### Prior approaches to matching `Data`

An initial approach extended builtin casing directly to the five constructors of `Data`, effectively providing a more efficient `chooseData`. This offered limited practical value: contracts rarely use `chooseData` by itself, and known structures such as script contexts can already be deconstructed more efficiently with partial builtins such as `unConstrData`.

A more useful approach is to match `Data.Constr` directly when casing on `Data`. This can improve programs that inspect script contexts, but it introduces an arity problem in TPLC and PIR. `Data.Constr` is an untyped runtime value whose number of fields is not known by the type system. A handler with the wrong number of arguments may therefore partially apply instead of failing:

```haskell
case (Data.Constr 0 [Data.I 1])
  (\x y -> x)

-- Evaluates to: \y -> Data.I 1
```

Atomic multi-lambda and multi-application were proposed to detect such length mismatches:

```haskell
(\[x y] -> x) [Data.I 1, Data.I 2] -- Evaluates
(\[x y] -> x) [Data.I 1]           -- Fails due to arity mismatch
```

That design requires new AST terms and specialized CEK handling while still providing only limited matching on `Data.Constr`. A dedicated `Let` term has similar implementation costs and similarly limited semantics. Both designs also overlap with existing lambda/application behavior.

Since these approaches require new syntax and non-trivial CEK changes, this proposal instead introduces one general pattern-matching term. It supports direct and nested matching across builtin values while keeping the CEK integration close to the existing implementation of builtin `Case`.

### Use cases and stakeholders

The primary use case is efficient deconstruction of known `Data` structures, particularly ledger script contexts. The same operation also supports selective matching and capture in builtin lists, pairs, integers, byte strings, booleans, and unit.

The direct stakeholders are:

- authors and users of UPLC-producing compilers;
- implementors of Plutus Core evaluators, serializers, and analysis tools;
- ledger and node implementors responsible for language-version and cost-model support; and
- smart-contract developers whose scripts repeatedly inspect structured builtin values.

## Specification

### Scope and type of change

This proposal makes two related changes:

1. It adds a new UPLC language construct, `Match`, together with universe-specific pattern syntax. Under CIP-0035, adding a language construct is a backward-compatible minor Plutus Core language-version change.
2. It adds CEK cost-model parameters for entering a match, processing a pattern step, traversing a structural edge, and proceeding to the next alternative.

This proposal specifies the default-universe patterns. It does not require all Plutus Core universes to use those patterns; pattern matching remains universe-specific.

### Abstract syntax

The UPLC term type gains a `Match` constructor. Its pattern type is supplied by the builtin universe:

```haskell
-- module UntypedPlutusCore.Core.Type
data Term name uni fun ann
  = ...
  | Match
      !ann
      !(Term name uni fun ann)
      !(Vector (BuiltinPattern uni, Term name uni fun ann))
```

A `Match` contains:

- a scrutinee term; and
- an ordered vector of pattern/handler alternatives.

The default universe defines the following field endings and builtin patterns:

```haskell
-- module PlutusCore.Default.Universe
data DefaultPatternFieldEnd
  = DefaultPatternFieldsExact
  | DefaultPatternFieldsPrefixWildcard
  | DefaultPatternFieldsPrefixCapture

data DefaultBuiltinPattern
  = DefaultPatternWildcard
  | DefaultPatternCapture
  | DefaultPatternInteger !Int64
  | DefaultPatternByteString !ByteString
  | DefaultPatternBool !Bool
  | DefaultPatternUnit
  | DefaultPatternList
      !DefaultPatternFieldEnd
      !(Vector DefaultBuiltinPattern)
  | DefaultPatternPair
      !DefaultBuiltinPattern
      !DefaultBuiltinPattern
  | DefaultPatternDataConstr
      !Word64
      !DefaultPatternFieldEnd
      !(Vector DefaultBuiltinPattern)
  | DefaultPatternDataMap
      !DefaultPatternFieldEnd
      !(Vector DefaultBuiltinPattern)
  | DefaultPatternDataList
      !DefaultPatternFieldEnd
      !(Vector DefaultBuiltinPattern)
  | DefaultPatternDataI !DefaultBuiltinPattern
  | DefaultPatternDataB !DefaultBuiltinPattern
```

`DefaultPatternWildcard` accepts the value at the current position without capturing it. `DefaultPatternCapture` accepts and records the current value. These correspond roughly to `_` and a variable binding in a Haskell pattern.

The scalar patterns match the corresponding integer, byte string, boolean, or unit value. Pair, list, and `Data` patterns recursively match their contents. `DefaultPatternDataConstr` additionally matches the constructor tag.

For builtin lists, `Data.Constr` fields, `Data.List`, and `Data.Map`, `DefaultPatternFieldEnd` distinguishes:

- an exact match, in which the number of fields or elements must equal the number of child patterns; and
- a prefix match, in which the child patterns match the beginning of the structure and the remaining suffix may be captured.

### Concrete syntax

In the textual form, `match` is followed by its scrutinee and one or more `pattern` alternatives. Each alternative contains a pattern followed by its handler:

```lisp
(program 1.2.0
  (match (con data (Constr 7 [I 1, B #aa, I 9]))
    (pattern
      ; Match Data.Constr 8 [<bind>, Data.List [_, _], ...]
      ; The handler must accept one data capture.
      (data-constr 8
        (prefix
          (bind)
          (data-list (wildcard) (wildcard))
          (wildcard)))
      (error))
    (pattern
      ; Match Data.Constr 7 [Data.I <bind>, ...] and bind the suffix.
      ; The handler must accept an integer and a list of data.
      (data-constr 7
        (prefix
          (data-i (bind))
          (bind)))
      (lam integerCapture (lam rest rest)))
    (pattern
      ; Match [_, <bind>, _, <bind>, ...].
      ; The handler must accept two values of the list element type.
      (list
        (prefix
          (wildcard)
          (bind)
          (wildcard)
          (bind)
          (wildcard)))
      (lam a (lam b a)))
    (pattern
      (wildcard)
      (error))))
```

In Flat, `Match` uses term-constructor tag `10`, followed by its annotation, scrutinee, and a list of alternatives. Each alternative encodes its pattern followed by its handler term.

Default builtin patterns use a four-bit tag:

| Tag | Pattern | Following payload |
|----:|---------|-------------------|
| 0 | wildcard | none |
| 1 | capture | none |
| 2 | integer | `Int64` |
| 3 | byte string | `ByteString` |
| 4 | boolean | `Bool` |
| 5 | unit | none |
| 6 | exact builtin list | child-pattern list |
| 7 | pair | left pattern, right pattern |
| 8 | exact `Data.Constr` | `Word64` tag, child-pattern list |
| 9 | exact `Data.Map` | child-pattern list |
| 10 | exact `Data.List` | child-pattern list |
| 11 | `Data.I` | child pattern |
| 12 | `Data.B` | child pattern |
| 13 | prefix | structural descriptor and one-bit rest tag |

For prefix tag `13`, the structural descriptor is one of tags `6`, `8`, `9`, or `10`, with the same payload as its exact form. A final one-bit tag selects whether the unconsumed suffix is ignored (`0`) or captured (`1`). Other pattern tags, structural descriptors, and rest tags are invalid.

### Evaluation

`Match` is evaluated as follows:

1. Evaluate the scrutinee.
2. If the result is not a builtin constant, evaluation fails. Otherwise, inspect alternatives in source order.
3. Match an alternative depth-first, from left to right, recording captures as they are reached.
4. On a mismatch, discard that alternative's pending work and captures, then try the next alternative.
5. On success, select that alternative's handler and apply the captured values to it in source order.
6. If no alternative matches, evaluation fails explicitly.

Alternatives that are not selected are not evaluated. A handler must accept one argument for each capture in its associated pattern. Wildcards do not add handler arguments.

An implementation may maintain an explicit work stack for pending siblings and fields and a separate capture accumulator. The reference implementation discards both in constant time when an alternative fails. On success, it reverses the capture accumulator into source order and constructs the applications of the selected handler.

### CEK integration

The reference implementation introduces `FrameMatches`, analogous to `FrameCases`. After the scrutinee is evaluated, this frame dispatches to the universe-specific matcher. If a pattern succeeds with captured values, the frame passes those values through `FrameAwaitFunConN` so that they are applied to the selected handler.

Universe-specific matching is exposed through a type class:

```haskell
newtype PatternMatchM s a = PatternMatchM
  { runPatternMatchM :: (PatternWork -> ST s ()) -> ST s a
  }

class MatchBuiltin uni where
  type BuiltinPattern uni

  matchBuiltin
    :: Some (ValueOf uni)
    -> Vector (BuiltinPattern uni, term)
    -> PatternMatchM
         s
         (HeadSpine Text term (Some (ValueOf uni)))
```

Like `CaseBuiltin`, `MatchBuiltin` separates universe-specific behavior from the CEK machine. Unlike `CaseBuiltin`, it runs in `PatternMatchM`, allowing matching work to be charged as traversal proceeds.

The `MatchBuiltin DefaultUni` instance sets `BuiltinPattern DefaultUni` to `DefaultBuiltinPattern` and recursively traverses that syntax. Captures are accumulated during traversal. If the current alternative later fails, its captures are discarded before matching continues with the next alternative.

### Costing

All work performed by `Match` is charged incrementally. Matching steps are divided into four CEK step kinds:

```haskell
data StepKind
  = ...
  | BMatch
  | BPattern
  | BStructural
  | BMatchNext
```

- `BMatch` accounts for entering the `Match` term.
- `BPattern` accounts for root and scalar matching, byte-string words, captures, and wildcards.
- `BStructural` accounts for child or field edges and bounded arity probes in recursively matched lists, pairs, and `Data`.
- `BMatchNext` accounts for abandoning a failed alternative and probing the next one.

Each scalar match, structural traversal, capture, wildcard, and alternative transition increments the appropriate counter directly. This permits arbitrary pattern depth and width without an uncosted traversal or an arbitrary syntactic bound.

The initial values for these parameters are estimates based on local measurements. They must be calibrated against a representative CEK benchmark suite before activation.

### Versioning

`Match` is introduced in Plutus Core language version 1.2.0 and is invalid in earlier language versions. Existing language versions and existing `Case` terms retain their current syntax and behavior.

The specification version of this feature is therefore Plutus Core language version 1.2.0. Any incompatible change to the syntax, serialization, or evaluation behavior specified here requires a subsequent language version. Compatible clarifications to this document may follow the normal CIP revision process.

## Rationale: How does this CIP achieve its goals?

### Direct and recursive deconstruction

`Match` attaches explicit patterns to alternatives, allowing a program to select a handler based on the value and shape of a builtin constant. Recursive patterns allow a program to reach a needed field without constructing and evaluating a chain of partial destructors and guards. Captures expose only the values needed by the selected handler.

This is particularly useful for known `Data` structures. A script can match a constructor tag, check nested structure, and capture selected fields in a single evaluator operation.

### Relationship to `Case`

`Match` is functionally more expressive than builtin-value `Case`. For example:

```lisp
(case 4
  (error)
  (con integer 10)
  (error)
  (error)
  (con integer 20))
```

can be written as:

```lisp
(match 4
  (pattern (integer 1) (con integer 10))
  (pattern (integer 4) (con integer 20)))
```

This can reduce script size because `Match` names the integer values of interest instead of requiring all preceding branches to be present.

This proposal does not deprecate builtin-value `Case`. For shallow operations such as unconsing a list or matching a boolean, `Case` should remain faster because it avoids initializing and traversing the general matcher.

### Incremental costing

Pattern size alone does not determine runtime work: an early mismatch may inspect only a prefix, while a successful nested pattern may traverse many fields. Incremental charging follows the work actually performed and ensures that arbitrary patterns remain bounded by the script budget.

An alternative design computed each pattern's size before matching. It reduced evaluator overhead but required either:

- the Flat decoder to inject the encoded pattern size into the AST, making decoding part of the trusted costing path; or
- an uncosted look-ahead traversal before matching.

Neither requirement was justified by the measured performance benefit, so this proposal uses incremental costing.

### Alternatives considered

#### Direct `Data` casing

Assigning the five `Data` constructors to fixed `Case` branches is simple but mainly accelerates `chooseData`. It does not efficiently deconstruct known nested structures, which is the common script-context use case.

#### Multi-lambda and multi-application

Atomic application of multiple arguments can detect constructor-field arity mismatches, but it requires two new language terms and specialized CEK behavior. It also raises a distinction between ordinary nested lambdas and multi-lambdas while providing only limited matching functionality.

#### A dedicated `Let` term

A `Let` term could bind a row of values but still requires CEK support for that row and overlaps with lambda/application as a binding mechanism. Like multi-lambda, it does not provide general nested matching.

The proposed `Match` term concentrates these use cases into one ordered pattern-matching operation and integrates with the CEK in a manner similar to `Case`.

### Backward compatibility

The change is backward-compatible at the Plutus Core language level because `Match` is guarded by a new minor language version. Scripts using earlier versions continue to parse and evaluate with unchanged semantics.

Nodes and tools that do not support the new language version cannot accept scripts using `Match`; activation therefore requires a hard fork that introduces the language version and its cost-model parameters. No existing script is rewritten, and `Case` remains available.

### Performance

The following local benchmarks compare `Match` with existing deconstruction using partial builtins, optionally guarded by `chooseData`, or builtin `Case`. They measure CEK wall-clock time rather than calibrated on-chain execution units.

#### Capturing one deeply positioned value

| Input and target                  | Traditional baseline      | Traditional CEK | `Match` CEK | Traditional / `Match` |
|-----------------------------------|---------------------------|----------------:|------------:|----------------------:|
| `Data.Constr`, field 1,024        | direct `UnConstrData`     |       33.628 us |    5.119 us |                 6.50x |
|                                   | guarded with `ChooseData` |       33.479 us |    5.230 us |                 6.38x |
| `Data.List`, field 1,024          | direct `UnListData`       |       33.775 us |    5.283 us |                 6.42x |
|                                   | guarded with `ChooseData` |       33.525 us |    5.150 us |                 6.56x |
| Builtin list, element 1,024       | builtin `Case`            |       33.675 us |    5.131 us |                 6.51x |
| 64 nested `Data.Constr` layers    | direct destructors        |       21.719 us |    2.240 us |                 9.70x |
|                                   | guarded with `ChooseData` |       31.068 us |    2.297 us |                13.74x |
| 64 nested `Data.List` layers      | direct destructors        |       13.108 us |    1.969 us |                 6.67x |
|                                   | guarded with `ChooseData` |       21.523 us |    2.001 us |                10.67x |
| 64 alternating Constr/List layers | direct destructors        |       17.998 us |    2.127 us |                 8.46x |
|                                   | guarded with `ChooseData` |       26.110 us |    2.158 us |                12.10x |

Each benchmark captures the innermost value. For a wide list, this is the last element; for nested structures, this is the innermost value. In these cases, `Match` is at least six times faster in the measured CEK runtime.

#### Capturing multiple values

| Input and target                                | Traditional baseline      | Traditional CEK | `Match` CEK | Traditional / `Match` |
|-------------------------------------------------|---------------------------|----------------:|------------:|----------------------:|
| `Data.Constr`, all 1,024 fields captured        | direct `UnConstrData`     |       35.523 us |   20.502 us |                 1.75x |
|                                                 | guarded with `ChooseData` |       35.257 us |   20.674 us |                 1.67x |
| `Data.List`, all 1,024 fields captured          | direct `UnListData`       |       34.978 us |   20.359 us |                 1.72x |
|                                                 | guarded with `ChooseData` |       35.297 us |   20.712 us |                 1.72x |
| Builtin list, all 1,024 elements captured       | builtin `Case`            |       34.369 us |   20.443 us |                 1.68x |
| 64 nested `Data.Constr` layers, 192 captures    | direct destructors        |       21.252 us |    4.929 us |                 4.29x |
|                                                 | guarded with `ChooseData` |       31.078 us |    5.091 us |                 6.10x |
| 64 nested `Data.List` layers, 192 captures      | direct destructors        |       12.887 us |    4.943 us |                 2.59x |
|                                                 | guarded with `ChooseData` |       21.461 us |    4.935 us |                 4.30x |
| 64 alternating Constr/List layers, 192 captures | direct destructors        |       17.663 us |    5.075 us |                 3.48x |
|                                                 | guarded with `ChooseData` |       26.182 us |    5.041 us |                 5.21x |

Capturing values is more expensive because each captured value must be stored and later applied to the handler. The performance gap therefore narrows when every field is captured, but all measured cases remain faster with `Match`.

The cost parameters used for these measurements are not fully calibrated. Preliminary CPU and memory budgets improved by between 10% and 90%, depending on the amount of capture work. Typical script-context use is expected to capture only a few fields; with the initial conservative parameters, the observed budget improvement in those cases was approximately 40% to 60%.

### Typed integration and compiler support

TPLC, PIR, and compiler support are not part of the initial implementation specified by this proposal.

A later typed implementation can derive the capture-argument types of each handler from its pattern and the normalized scrutinee type. Given the result type of the `Match` expression, a type checker can check each handler against the function type formed by its capture types followed by the result type. This is similar to builtin casing but requires a static pattern annotator corresponding to the runtime matcher:

```haskell
class AnnotatePatternBuiltin pat uni where
  annotateCaseBuiltin
    :: UniOf term ~ uni
    => PatOf term ~ pat
    => Type TyName uni pat ann
    -> [(pat, term)]
    -> Either Text [(term, [Type TyName uni ann])]
```

Exhaustiveness checking is not required for evaluation semantics because failure to match any alternative is an explicit CEK failure.

### Remaining implementation considerations

The following implementation questions do not change the specified behavior:

- Whether `PatternMatchM`, currently an `ST` wrapper used for costing, can be made less CEK-specific without reducing performance.
- Whether internal match-cost counters should remain in `StepKind` or move to a separate mechanism while preserving the same charged work.
- How to expand the benchmark and budget-calibration suite before activation.

## Path to Active

### Acceptance Criteria

- [ ] The `plutus` repository contains an updated Plutus Core specification defining:
  - [ ] the `Match` term and default-universe pattern syntax;
  - [ ] textual and Flat serialization;
  - [ ] ordered matching, capture application, mismatch, and failure semantics; and
  - [ ] Plutus Core language version 1.2.0 as the version that introduces the feature.
- [ ] The `plutus` repository contains:
  - [ ] a production implementation of syntax, serialization, and CEK evaluation;
  - [ ] conformance tests covering scalar, structural, nested, prefix, exact, capture, fallback, and failure behavior;
  - [ ] calibrated costs for `BMatch`, `BPattern`, `BStructural`, and `BMatchNext`; and
  - [ ] benchmarks showing the effect on representative and adversarial inputs.
- [ ] External implementations or independent test implementations are available.
- [ ] The ledger supports the new Plutus Core language version and all required cost-model parameters.
- [ ] The feature is released in a Cardano node version.
- [ ] The released implementation is present in block-producing nodes representing at least 80% of active stake.

### Implementation Plan

The reference implementation adds `Match` to UPLC and its Flat encoding, implements universe-specific matching in the CEK machine, and provides costing, benchmarks, and conformance tests in the `plutus` repository.

The change requires Plutus Core language version 1.2.0 and new cost-model parameters. Under CIP-0035, these are introduced through a hard fork. Ledger integration must gate the new language version and supply the calibrated parameters. Activation should occur only after specification review, cost calibration, conformance testing, independent implementation or test implementation, and release in the node.

## References

- [CIP-0001: CIP Process](https://cips.cardano.org/cip/CIP-0001)
- [CIP-0035: Plutus Core Evolution](https://cips.cardano.org/cip/CIP-0035)
- [CIP-0085: Sums-of-products in Plutus Core](https://cips.cardano.org/cip/CIP-0085)
- [IntersectMBO/plutus issue #5777](https://github.com/IntersectMBO/plutus/issues/5777)
- [IntersectMBO/plutus issue #6225](https://github.com/IntersectMBO/plutus/issues/6225)
- [IntersectMBO/plutus issue #6602](https://github.com/IntersectMBO/plutus/issues/6602)
- [IntersectMBO/plutus pull request #7209](https://github.com/IntersectMBO/plutus/pull/7209)

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
