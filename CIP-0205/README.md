---
CIP: 205
Title: Removal of the scope check in Plutus Core
Category: Plutus
Status: Proposed
Authors:
  - Jacco Krijnen <jacco.krijnen@iohk.io>
Implementors: []
Discussions:
  - Plutus issue: https://github.com/IntersectMBO/plutus/issues/7368
  - Original PR: https://github.com/cardano-foundation/CIPs/pull/1278
Created: 2026-09-21
License: CC-BY-4.0
---


## Abstract

This CIP proposes the removal of the well-scopedness requirement from the Plutus
Core specification and the scope check from the Plutus implementation. Removing
the check reduces the work performed during transaction validation with a modest
change to the semantics of Untyped Plutus Core (UPLC).


## Motivation: Why is this CIP necessary?

### Background

The Plutus Core Language Specification[^plutus-spec] states in Section 2.1.3
that a UPLC program must be _well-scoped_, meaning it has no free variables. It
also states that the property must be checked before script execution in the
CEK machine. The _scope check_ is performed during phase 2 of transaction
validation and introduces overhead.

When a well-scoped ("closed") UPLC term is evaluated, we know that each variable
will be bound to a value by the time it is needed. This rules out
"unbound/undefined variable" errors at run-time. The purpose of the scope check
is to reject ill-scoped ("open") terms early.

The scope check is an accident of history and comes from the time when the CEK
machine operated on named variables, while the serialized AST used de Bruijn
indices. That required a conversion from de Bruijn indices to names, which
incidentally enforced well-scopedness. A scope check was kept to preserve that
behaviour. This "wasn't a conscious choice"[^bench].

[^plutus-spec]: [Plutus Core specification](https://plutus.cardano.intersectmbo.org/resources/plutus-core-spec.pdf)

### The scope check is costly

The plutus validation benchmark[^bench-code] shows[^bench] that the scope check
accounts for roughly 20% of script preparation time (decoding, version check and
scope check), and about 3% of total transaction validation time. Such work is
charged for only indirectly, with size-based fee parameters such as
`minFeeRefScriptCostPerByte`. A removal reduces work per script execution and
hence leaves room for future parameter recalibration and reduced fees.

For scripts that are large but fast to execute, the benefit could be much more
than 3%, especially since the fee associated with script size is exponential.
With the implementation of modules[^modules], more such script could arise.

Transaction throughput and developer adoption (which is hindered by high fees)
are both core pillars of Cardano's 2030 strategy[^2030-strategy]. This raises
the question: is the scope check worth it?

[^bench-code]: [Plutus contract validation benchmarks](https://github.com/IntersectMBO/plutus/tree/master/plutus-benchmark/validation)
[^bench]: [Original issue](https://github.com/IntersectMBO/plutus/issues/7368)
[^modules]: [CIP: Modules in UPLC](https://cips.cardano.org/cip/CIP-0152)
[^2030-strategy]: [Cardano 2030 Strategy](https://product.cardano.intersectmbo.org/vision/strategy-2030/)



### The scope check has limited benefit

The scope check statically guarantees that the CEK machine's environment will
have a value for each variable that is ever evaluated. This means that indexing
into the environment data structure always succeeds and is therefore
memory-safe. But since the data structure used by the CEK machine deals with
lookup failure, the operation is memory-safe, regardless of whether a variable
is free or bound. The scope check does not add additional safety.

A removal of the check does introduce one new case in the UPLC semantics: an
unbound variable cannot be evaluated, causing the CEK machine to terminate with
an error. Let us consider what the change means for ill-scoped and well-scoped
terms:

- Ill-scoped terms that hit this new failure would have also failed the scope
  check. The difference is that with the scope check, the failure happens
  earlier.

- Ill-scoped programs that contain free variables but don't evaluate them (dead
  code) will not hit the new failure mode. Here, the difference is that they
  would have been rejected by the scope check.

- For well-scoped programs nothing changes, except that no time is spent on the
  scope check. Removal is a conservative extension to the semantics: all
  variables that are evaluated will be bound to a value at run-time, so the new
  failure mode can never be reached.

Moreover, any program logic that can be written as an open term can already be
written with well-scoped UPLC: replace each free variable by `error`, and you
obtain a well-scoped program that behaves equivalently.

One may wonder if the underlying data structure for variable lookup could be
changed to exploit a scope check for performance. See the section
[below](#a-scope-check-for-array-based-cek-environments) for a discussion.

### The implementation does not rely on the scope check

No part of the Haskell CEK machine implementation relies on a term being
well-scoped. There has always been logic in place that needed to deal with
variable lookup failure[^cek-open-error]. The formalized Agda CEK machine would
require some changes, which we discuss in the Specification section below.

We are not aware of any other implementation of the CEK machine or tooling that
relies on the well-scopedness property. For example, the Amaru Rust
implementation deals with variable lookup failure in the same way as the Haskell
node.

[^cek-open-error]: [CEK machine logic for free variables](https://github.com/IntersectMBO/plutus/blob/57d6d00c307c802d8a5c0f92253205438a9180f4/plutus-core/untyped-plutus-core/src/UntypedPlutusCore/Evaluation/Machine/Cek/Internal.hs#L1085)


### The current scope check is unsound

The scope check in the Haskell node has a bug[^scope-bug], which causes it to
accept some open terms already. This should be fixed (independently of this
proposal), but in practice free variables have already been part of the
semantics for some time.

[^scope-bug]: [checkScope does not traverse Constr/Case: free variables inside SOP terms pass the ledger scope check](https://github.com/IntersectMBO/plutus/issues/7965)


### Developer tooling typically performs the scope check off-chain

Languages such as Aiken, Plinth and Plutarch already check for scoping
indirectly by means of a type checker, which guarantees well-scopedness of the
code. While hand-written UPLC may accidentally contain free variables, other
non-sensical programs (e.g. `2 + true`) are also allowed to run and fail in the CEK
machine.


## Specification

This specification covers changes to the Plutus Core language
specification[^plutus-spec], the implementation[^plutus-repo], the conformance
test suite[^plutus-conformance] and the formalized metatheory[^plutus-metatheory].

[^plutus-repo]: [Plutus repository](https://github.com/IntersectMBO/plutus)
[^plutus-conformance]: [Plutus conformance test suite](https://github.com/IntersectMBO/plutus/tree/master/plutus-conformance)


### The Plutus Core specification

The reduction semantics for free variables is given by the following rule:


```math
\frac{ }{x \to \texttt{error}}
```

The CEK semantics for free variables is given by the step:

```math
s; ρ ▷ x ↦ ◆    \text{(if x is not bound in ρ)}
```

Text in the specification is updated accordingly. For example:

- The paragraph about "Scoping" (Section 2.1.3) does not require terms to be
  well-scoped, but mentions that free variables are allowed.
- The definition of substitution should state that capture-avoidance is
  necessary because values may contain free variables.

### The Plutus Core implementation

The CEK machine should throw an `OpenTermEvaluatedMachineError` when trying to
evaluate a free variable, after charging a `BVar` step.

Only for Plutus language version ≤ 1.1.0, `mkTermToEvaluate` performs the scope
check. This applies to Plutus V1, V2, V3.

Some CEK machinery should be updated to deal with open terms properly. For
example `dichargeCekValue` [^discharge], even though that particular function is
not used for on-chain evaluation.

[^discharge]: [`dischargeCekValue` doesn't handle open terms correctly](https://github.com/IntersectMBO/plutus/issues/7526)

### The Agda metatheory

The plutus-metatheory formalisation in Agda[^plutus-metatheory] has
formalisations of scoped PLC and typed PLC. In addition to those, it should
include abstract syntax of UPLC without intrinsic scoping, as well as a
corresponding CEK machine and reduction semantics. Both semantics will implement
the rules for free variables as outlined above.

The existing formalisations for typed PLC and scoped PLC should not implement
free variables. They remain useful because they formalise intermediate
representations used in the Plinth compiler.

An equivalence between the well-scoped and unscoped CEK semantics (for
well-scoped terms) should be proved, to verify the claim of this CIP that
evaluation of well-scoped terms is unchanged.


[^plutus-metatheory]: [Plutus metatheory in Agda](https://github.com/IntersectMBO/plutus/tree/master/plutus-metatheory)

### The conformance test suite

The plutus conformance test suite should be extended with tests for open terms.
In particular it should test the following two behaviours:

- failure with an evaluation error due to open terms
- successful termination with free variables.


### Type of change and versioning

CIP-0035 lists typical changes to Plutus Core and how those affect the Plutus
language version (LV). Which change applies here is not directly obvious.
Consider for example:

> Changing the behaviour of a construct in the language

This sounds applicable, because evaluating variables can now fail. However, free
variables have never been a valid construct: the combination of concrete syntax
and the well-scopedness requirement ruled out terms with free variables.

Therefore, the following type of change is more appropriate:

> Adding a construct to the language

The proposed change therefore requires bumping the language version from 1.1.0
to 1.2.0, which in turn requires a hard fork.

No changes to the binary format or script-ledger interface are needed.



## Rationale: How does this CIP achieve its goals?

Removing well-scopedness from the specification and the implementation of the
CEK machine reduces the work for validating (closed) scripts. Eventually this
could be reflected in transaction costs if fee parameters can be adjusted.


### How does this affect transaction validation?

The change is backwards-compatible. Scripts that were deployed before the
removal use version 1.0.0 or 1.1.0 and this proposal does not change their
behaviour. New scripts may declare 1.2.0 and use Plutus without scope check.


<!--

(this commented text applies only if the scope check were to be guarded by PV
instead of language version)

Incoming transactions that were invalid due to a script failing the scope check
can be valid after the scope check removal. There are two scenarios:

- Either the ill-scoped script still fails (because it evaluated a free
  variable). There is no observable consensus change: a phase 2 failure means
  collateral is forfeited. The node may have to do some extra work evaluating
  the program, but it is compensated for that with the collateral.

- The script now succeeds (no free variable was on the execution path), so
  fees are paid in the usual way. Since this leads the ledger to accept more
  transaction, a PV check is in order to be able to validate the chain history.

Crucially, incoming transactions that currently succeed will keep succeeding
after removal. The node will save the overhead of performing the scope check on
all (reference) scripts used. This can eventually be reflected in lower fees.
-->


### Alternatives considered


#### Fixing the scope check instead of removing it

This would not solve the issue of the check being costly. Fixing the scope check
retro-actively for 1.0.0 and 1.1.0 requires a separate proposal. Such a fix is
also not backwards compatible, as there could be scripts that succeed (have
unused free variables, not covered by the scope check) which start failing after
a fix. Removal of the scope check is a conservative extension.

#### Moving the scope check to phase 1

This also does not address the check being costly. Instead, the node still has
to do the same amount of work, but cannot be compensated with collateral when
the check fails.

#### Keeping well-scopedness for CEK performance

There is currently no evidence that the well-scopedness invariant can result in
speed-ups in the CEK machine implementation.

If, however, in the future an optimisation is found that makes a scope check
worthwhile for script execution, this proposal does not prevent it. Before
execution, the node can perform the check and use an optimised CEK machine that
exploits the well-scopedness property. Otherwise, it can fall back to the
machine proposed in this CIP, which deals with open terms. Alternatively, the
scope check pass could replace free variables by `error` and proceed to evaluate
a now well-scoped term. That preserves free variable semantics as outlined in
this CIP.

#### A scope check for array-based CEK environments

The scope check statically determines that any variable will be bound to a value
at CEK machine run-time. More precisely, any variable lookup in the
_environment_[^spec-environments] (which maps in-scope variables to their bound
value) will succeed. The question arises whether environments can be implemented
in such a way that this guarantee is exploited for improved performance.

In the current Haskell CEK machine, environments do not exploit this guarantee
because the implementation is based on a linked data structure[^sbral-impl],
which as part of the lookup operation establishes whether a variable is present.

In contrast, a data structure that is based on contiguous memory (e.g. arrays),
can perform variable lookup efficiently with pointer arithmetic, which is only
memory-safe when indexing within array bounds. The scope check guarantees that
no run-time bounds check is required, and lookup will always be memory-safe.
That cost is now accounted for upfront, during the scope check.

However, it is unclear whether an array-based data structure is necessarily
better than the current environment structure, because while lookup may become
cheaper, extension of environments is constant time in the current data
structure, whereas arrays involve (linear) copying. Moreover, this proposal does
not prevent such an optimisation if it turned out to be beneficial (see the
[above section](#keeping-well-scopedness-for-cek-performance)).

[^spec-environments]: [Plutus Core Specification, Section 2.4 "The CEK Machine"](https://plutus.cardano.intersectmbo.org/resources/plutus-core-spec.pdf)
[^sbral-impl]: [Plutus implementation of environments](https://github.com/IntersectMBO/plutus/blob/master/plutus-core/index-envs/src/Data/RandomAccessList/SkewBinary.hs)


#### Fusing the scope check with script deserialization

An experiment has shown that fusing the scope check with deserialization
improves performance [^fusing], but it still requires work for each variable and
doesn't address the other parts of the motivation.

[^fusing]: [Experiment on fusing the scope check](https://github.com/IntersectMBO/plutus/issues/7368#issuecomment-3686732448)


#### Keeping well-scopedness to prevent mistakes in a CEK implementation

The Agda metatheory implements a CEK machine using intrinsically-scoped syntax
for UPLC. Intrinsic scoping ensures that certain scoping bugs are prevented by
Agda's type checker. For example, it is not possible to accidentally add open
terms to the CEK environment during execution.

Production implementations use programming languages that do not typically use
this level of type safety. In particular, the Haskell node uses plain abstract
syntax that has to deal with the free variable case anyway. Even though the
scope check is performed in those implementations, it does not by itself prevent
such bugs.

## Path to Active

### Acceptance Criteria

- [ ] The Plutus Core specification is updated with the semantics for free
  variables given in this CIP.
- [ ] The `plutus` repository contains an implementation of this CIP:
  - [ ] `mkTermToEvaluate` skips the scope check for language version 1.2.0 and
    above;
  - [ ] the Agda metatheory includes unscoped abstract syntax and a CEK machine
    over it;
  - [ ] the conformance test suite contains the open-term tests described in the
    Specification.
- [ ] `cardano-ledger` accepts Plutus Core language version 1.2.0 for PlutusV1,
  PlutusV2 and PlutusV3 from the target protocol version onwards.
- [ ] A node release containing the change is live on Cardano mainnet after the
  corresponding hard fork.

### Implementation Plan

The implementation will be performed by the Plutus Core team and released by
means of a hard fork, making language version 1.2.0 available for PlutusV1, V2
and V3.

## Copyright

This CIP is licensed under
[CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).

