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

Benchmarks show that the scope check accounts for roughly 20% of script
preparation time (decoding, version check and scope check), and about 3% of
total transaction validation time[^bench]. Such work is charged for only
indirectly, with size-based fee parameters such as `minFeeRefScriptCostPerByte`.
A removal reduces work per script execution and hence leaves room for future
parameter recalibration and reduced fees.

Transaction throughput and developer adoption (which is hindered by high fees)
are both core pillars of Cardano's 2030 strategy[^2030-strategy]. This raises
the question: is the scope check worth it?

[^bench]: [Original issue](https://github.com/IntersectMBO/plutus/issues/7368)
[^2030-strategy]: [Cardano 2030 Strategy](https://product.cardano.intersectmbo.org/vision/strategy-2030/)



### The scope check has limited benefit

A removal of the check introduces one new failure mode in the UPLC semantics: an
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
specification[^plutus-spec], the implementation, the conformance test suite and
the formalized metatheory.


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

### The Agda metatheory

The plutus-metatheory formalization in Agda[^plutus-metatheory] should include abstract syntax
without scoping restrictions and a corresponding CEK machine, in addition to the
scoped and typed formalisations (which cannot represent open terms). The CEK
machine will implement the semantics for free variables as outlined above.

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

There is no evidence that the well-scopedness invariant can result in speed-ups
in the CEK machine implementation.

If in the future an optimisation is found that makes a scope check worthwhile,
this proposal does not prevent it. Before script execution, the node could still
perform the scope check and use the optimised CEK machine on success, or fall
back to the un-optimised one when the check fails.

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

