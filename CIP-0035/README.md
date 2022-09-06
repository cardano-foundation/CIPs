---
CIP: 35
Title: Plutus Core Evolution
Authors: Michael Peyton Jones <michael.peyton-jones@iohk.io>
Comments-Summary: No comments
Comments-URI: 
Status: Active
Type: Process
Created: 2022-02-09
License: CC-BY-4.0
---

# Evolution of Plutus Core in the Cardano ledger

## Abstract

This CIP proposes a process for proposing changes to Plutus Core, its builtins, and its interface to the Cardano ledger.

## Motivation

The Plutus Core language, its builtins, and its interface to the ledger are all likely to evolve significantly over time. There are many reasons for this:
- We may be able to increase performance, improve safety, or reduce script sizes by changing the language.
- We may be able to improve performance by providing builtin versions of expensive functions.
- We may need to provide builtin versions of sensitive functions (e.g. cryptography) in order to ensure access to high-quality implementations.
- We may find bugs in the implementation that need to be fixed.
- We may need to change the interface to the ledger in order to represent changes in transaction formats.
- We may wish to remove elements which have been deprecated due to the addition of improved versions.
- … and more

At the moment there is no process for making such changes other than the discretion of the core developers. 
This CIP gives a taxonomy of changes, explains how such changes might be implemented in Cardano, and prescribes processes for proposing such changes.

## Background

This CIP assumes general familiarity with Plutus Core and the Cardano ledger, but we give some brief background here.

### Plutus Core

_Plutus Core_ is a script language used in the Cardano ledger. For the purposes of this document, Plutus Core consists of various _language constructs_, and also _builtin types and functions_.

Plutus Core has a number of builtin types, such as integers, and builtin functions, such as integer addition. 
Builtin functions provide access to functionality that would be difficult or expensive to implement in Plutus Core code. 
Builtin functions can operate only over builtin types. Builtin types come with a _size metric_ which is used by costing functions. 
For example, the size metric for integers returns the bit-size of the integer.

The performance of Plutus Core scripts has two components: how expensive the script actually is to run (_real performance_) and how expensive we say it is to run in the ledger (_model performance_). 

Model performance is calculated by costing _evaluation_ in abstract resource units ("exunits") of CPU and memory. 
Individual steps of evaluation are costed, and builtin functions must also come with a _costing function_ that provides costing information for them. 
The costing function for a builtin function is a mathematical function which takes the sizes of the arguments (as computed by their size metrics), and returns an estimate of the budget that will be used to perform that function. 
For example, the costing function for addition says that the CPU and memory costs are both proportional to the maximum of the sizes of the input integers (with some appropriate constants).

Determining costing functions is done empirically, by running the function in question against a large number of inputs and choosing a costing function that fits the data well.

### Scripts in the Cardano ledger

The Cardano ledger recognizes various kinds of _scripts_ identified by _language_. 
This language tag is the only way that the ledger has to distinguish between different types of script. 
Hence if we require different behaviour, we need a new language.

We omit this distinction when talking about Plutus Core: we refer instead to Plutus Core _language versions_, which are actually entirely distinct _languages_ from the perspective of the ledger.
All Plutus Core language versions which are used in the ledger must be supported forever, in order to be able to validate the history of the chain.

Part of the specification of a language in the ledger is how scripts of that language are run, what arguments they are passed, how those arguments are structured, etc. 
We refer to this as the _ledger-script interface_.

Languages also have an associated subset of _protocol parameters_ which provide the ability to control some aspects of evaluation without a software update. 
The most notable example is a set of parameters which parameterize the costing of program execution.

### Types of change

This document considers the following types of change:

1. The Plutus Core language
    1. Adding a construct to the language
    2. Removing a construct from the language
    3. Changing the behaviour of a construct in the language
    4. Changing the binary format of the language in a backwards-compatible way
    5. Changing the binary format of the language in a backwards-incompatible way
2. The Plutus Core builtin functions and types
    1. Adding a new builtin function or type
    2. Removing a builtin function or type
    3. Changing the behaviour of a builtin function or type
3. The ledger-script interface
    1. Changing the interface between the ledger and the interpreter
4. Protocol parameters
    1. Improving model performance (i.e. changing the costing parameters so that scripts use less budget)
    2. Regressing model performance (i.e. changing the costing parameters so that scripts use more budget)
    3. Adding costing parameters
    4. Removing costing  parameters
5. Performance of the Plutus Core interpreter
    1. Improving real performance
    2. Regressing real performance

### Types of release

Changes to Plutus Core can be released onto Cardano in four ways, with ascending levels of difficulty:

1. A _protocol parameter_ change (PP), taking effect as soon as the new parameters are accepted (in a new epoch).
2. A _software update_ (SU) to the node, taking effect when nodes upgrade.
3. A _hard fork_ (HF) (accompanied by a software update), requiring a software update for the new protocol version, and taking effect after the hard fork.
4. A new Plutus Core _language version_ (LV), introduced in a hard fork, and taking effect for scripts that use the new version, but not for those that use the old version.

Intuitively, these correspond to how _compatible_ the change is.
- A backwards- and forwards-compatible change can be deployed with a software update, as nobody can perceive the difference.
- A backwards-compatible (but not forwards-compatible) change must be deployed in a hard fork, since it makes more blocks acceptable than before.
- A backwards-incompatible change requires a new Plutus Core language version, so that the ledger can distinguish them, and maintain the old behaviour for old scripts.

The following table lists, for each type of change in "Types of change", what kind of release it requires.

| Change                                                                     | Release            | Notes                                                                                               |
|----------------------------------------------------------------------------|--------------------|-----------------------------------------------------------------------------------------------------|
| Adding a language construct                                                | HF                 | Backwards-compatible.                                                                               |
| Removing a language construct                                              | LV                 | This will cause scripts which use this construct to be rejected, so is not backwards compatible.    |
| Changing the behaviour of a construct in the language                      | LV                 | This changes the behaviour of existing scripts, so is not backwards compatible.                     |
| Changing the binary format of the language in a backwards-compatible way   | HF                 | Safe even if it makes previously non-deserializable scripts deserializable.[^1]                     |
| Changing the binary format of the language in a backwards-incompatible way | LV                 |                                                                                                     |
| Adding a new builtin function or type                                      | HF (rarely LV[^2]) | Backwards-compatible. Requires a binary format change.                                              |
| Removing a builtin function or type                                        | LV                 | This will cause scripts which use this builtin to be rejected, so is not backwards compatible.      |
| Changing the behaviour of a builtin function or type                       | LV                 | This changes the behaviour of existing scripts, so is not backwards compatible.                     |
| Changing the interface between the ledger and the interpreter              | LV                 | The ledger must provide scripts with exactly the right interface. New interface means new language. |
| Improving model performance                                                | PP                 | _Must_ strictly follow an improvement in real performance.[^3]                                      |
| Regressing model performance                                               | PP                 |                                                                                                     |
| Adding cost model parameters                                               | HF                 | All nodes must recognize the new parameter.                                                         |
| Removing cost model parameters                                             | LV                 | Old scripts will require all the old parameters.                                                    |
| Improving real performance                                                 | SU                 |                                                                                                     |
| Regressing real performance                                                | SU                 | _Must_ strictly follow a regression in model performance.[^4]                                       |

[^1]: See "Are backwards-compatible binary format changes really safe?".
[^2]: The binary format change is backwards compatible unless it breaches the limit of how many builtin functions or types can be encoded, in which case that must be changed, forcing a new LV.
[^3]: See "Why do performance changes require extra steps?".
[^4]: See "Why do performance changes require extra steps?".

## Specification

This proposal deals only with the types of change listed in "Types of change", all others are out of scope.

### Changes that require a CIP

This proposal recommends that some of the changes listed in "Types of change" (specified below) should:

1. Be proposed in a CIP.
2. Go through additional process in addition to the [usual CIP process](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0001/README.md).

The additional process mostly takes the form of additional information that should be present in the CIP before it moves to particular stages.
As such, it is up to the CIP Editors to enforce this.

The requirement to propose a change via a CIP is, as all CIPs are, advisory. 
In exceptional circumstances or where swift action is required, we expect that changes may still be made without following this process. 
In such circumstances, a retrospective CIP SHOULD be made after the fact to record the changes and the rationale for them.

Changes that require a CIP do not have to each be in an individual CIP, they can be included in batches or in other CIPs. 
So, for example, a single CIP could propose multiple new builtin functions, or a CIP proposing a change to the ledger could also propose a change to the ledger-script interface.

#### Additions to the Plutus Core Builtins

Proposals for additions to the set of Plutus Core builtins SHOULD be proposed in a CIP and SHOULD adhere to the following additional process.

In order to move to Draft status, it MUST include:
- In the Specification:
    - Names and types/kinds for the new functions or types.
    - A source for the implementation (e.g. a library which can be linked against); or a generic description of the functionality which is implementable in any programming language.
    - In the Rationale:
    - An argument for the utility of the new builtins.

It SHOULD also include:
- In the Rationale
    - Examples of real-world use cases where the new additions would be useful.
    - A comparison with an implementation using the existing features, and an argument why the builtin is preferable (e.g. better performance).

In order to move to Proposed status, it MUST include:
- In the Specification:
    - For new types: a precise description of the measure used for the size of a value of that type.
    - For new builtin functions: a costing function for the builtin function.
- In the Rationale:
    - If an external implementation is provided: an argument that it is trustworthy.
    - Discussion of how any measures and costing functions were determined.

In order to move to Active status, the following must be true:
- The external implementations MUST be available.
- The `plutus` repository MUST be updated with an implementation including costing.
- The Plutus Core specification MUST be updated to include the new builtins.
- The ledger MUST be updated to include new protocol parameters to control costing of the new builtins.
- The completion of these steps MUST be tracked in the Path to Active section.

#### Other changes

Proposals for other additions, removals, or changes to behaviour of any part of Plutus Core or its builtins SHOULD be proposed in a CIP and SHOULD adhere to the following additional process.

In order to move to Active status, the following must be true:
- The `plutus` repository MUST be updated with an implementation of the proposal.
- For changes to Plutus Core itself, there MUST be a formal specification of the changes, either a sufficiently formal presentation in the CIP or a pull request to the Plutus Core specification.
- The completion of these steps MUST be tracked in the Path to Active section.

### Changes that do NOT require a CIP

#### Performance changes and protocol parameter updates

This CIP does not propose any process for proposing these changes. 

#### Bug fixes

A "bug fix" is a change to behaviour where:
- The implemented behaviour does not match the specification; or
- The specified behaviour is clearly wrong (in the judgement of relevant experts)

In this case the fix may be submitted directly to the `plutus` repository and is NOT required to go through the CIP process. 
It must still be released as appropriate. 
For example, if a bug fix changes behaviour, it will have to wait for a new Plutus Core language version.

### Implementing and releasing changes

This CIP does not cover the process of implementing changes.
As usual, the CIP process covers the design phase, and it is up to the implementor to ensure that their proposal is implemented, which may require additional work to meet the requirements of the maintainers of the Cardano code repositories (testing, implementation quality, approach), and so on.

Changes can be released after their CIPs have reached Active status. 
Different changes will require different releases as described in "Types of release".
This CIP does not cover the process by which changes are actually incorporated into releases after having been implemented.
In particular, there is NO assumption that a feature which requires a particular release will be included in the next such release, even after it has been implemented.

### Plutus Core CIP registry

Any CIP which proposes a type of change listed in "Types of change" MUST also add itself to this registry (in addition to the main registry).

| #  | Title             | Type of change          | Status |
|----|-------------------|-------------------------|--------|
| 31 | Reference inputs  | Ledger-script interface | Draft  |
| 32 | Inline datums     | Ledger-script interface | Draft  |
| 33 | Reference scripts | Ledger-script interface | Draft  |

## Rationale

### Why have a public process for changes?

Cardano is continuing to move towards decentralized governance within the Voltaire phase of development. 
Historically, key development and implementation decisions have been made by the core development team. 
This was important in the earliest stages of the platform’s evolution. 
However, this becomes less so as the platform starts to mature and is neither sustainable nor desirable in the long term.

Furthermore, while many changes to Cardano are obscure or not of interest to many community members, there is a much larger community who have a keen interest in changes to Plutus Core: dApp developers. 
Hence it is especially important to have a clear way for this community to be able to propose changes and see how they are progressing.

### Do removals and changes really need a new language version?

Not being able to make removals or changes to behaviour without a LV is quite painful. 
For example, it means that we cannot just fix bugs in the semantics: we must remain bug-for-bug compatible with any given LV.

It is tempting to think that if we can show that a particular behaviour has never been used in the history of the chain, then changing it is backwards-compatible, since it won’t change the validation of any of the actual chain. 
However, this is sadly untrue. 
The behaviour could be triggered (potentially deliberately) in the interval between the update proposal being accepted and it being implemented, which is extremely dangerous. 
So even if a bug is obscure, we cannot just fix it.

### Are backwards-compatible binary format changes really safe?

Changing the binary format in a backwards compatible way may mean that binary scripts which previously would have been invalid might now deserialize correctly into a program.

There is a worry here: scripts which fail execution (a phase 2 validation failure) actually get posted on the chain as failures. 
We must be careful not to turn any such failures into successes, otherwise we could break history.

However, we do not need to worry in this case, since checking that a script deserializes properly is a phase 1 validation check, so no scripts will be posted as failures due to failing to deserialize, so we cannot break any such postings by making deserialization more lenient.

### Why do performance changes require extra steps?

Performance changes must be carefully managed in order to avoid the possibility of an accidental hard fork.

Consider an example of improving performance. 
The interpreter gets 50% faster (real performance), which is released as a software update. 
Now, we want to lower the cost model parameters (model performance) so that users will be charged fewer resources for their scripts.

However, the parameter change means that scripts which previously would have exceeded the transaction/block limit become acceptable. 
The parameter change is not itself a hard fork, because all the nodes accept the new parameters by consensus. 
But if the model performance tracks real performance well, then nodes which have not adopted the software update may have issues with the real performance of these newly allowed scripts! 
In the worst case, they might suffer resource exhaustion, preventing them from following the new chain, which is tantamount to a hard fork.

This is a relatively unlikely scenario, since it requires a situation where nodes are close enough to their resource limits that an (effective) regression in real performance of scripts can push them over the edge. 
Nonetheless, the cautious approach is to not perform such parameter updates until we are sure that all nodes are using a version with the required software update, i.e. after the protocol version has been bumped in a hard fork.

Conversely, if (for some reason) we needed to regress the real performance of the interpreter, we should only do this after all the nodes have accepted a regression in model performance (increasing the cost model parameters).

### Why are we concerned about the implementations of builtins being trustworthy?

Builtin functions in Plutus Core are implemented via Haskell functions. Often these implementations come from somewhere else, e.g. a cryptography library written in C.

It is vitally important that these libraries are trustworthy. 
The Plutus Core package (and hence its dependencies) are linked into the Cardano node. 
A buffer overrun vulnerability in the implementation of a builtin function could therefore become an attack on a node.

### Why is the process for new builtins so much more structured?

We expect additions to builtins to be particularly common, and to have lots of interest from the community.

However, the process of adding new builtins is not totally straightforward, due in particular to the need to find a good implementation and to cost it. 
Surfacing these difficulties quickly is a key goal of this process.

Finally, builtins are a comparatively structured extension point for the language. 
In comparison, proposals for changes to Plutus Core itself are likely to be much more heterogeneous.

### Why are we reluctant to release new language versions?

Language versions (or more properly, languages from the ledger’s perspective) incur a large maintenance cost. 
Each one must continue to work, perfectly, in perpetuity. Furthermore, they may need their own, independent set of cost model protocol parameters, etc.

So it is very desirable to keep the number of language versions down. 
The simplest way to do this is to batch changes, and only release a new language version occasionally.

### Why include a CIP registry?

This is just to make it easy for those considering proposing a CIP following this process to see which CIPs have already been submitted. 
An alternative would be a standard title for CIPs, or perhaps some kind of CIP metadata to indicate that it follows the process in this CIP.

