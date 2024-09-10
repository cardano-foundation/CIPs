---
CIP: 35
Title: Changes to Plutus Core
Status: Active
Category: Meta
Authors:
  - Michael Peyton Jones <michael.peyton-jones@iohk.io>
Implementors: N/A
Discussions:
  - https://github.com/cardano-foundation/CIPs/pull/215
  - https://github.com/cardano-foundation/CIPs/pull/428
  - https://github.com/cardano-foundation/CIPs/pull/437
  - https://github.com/cardano-foundation/CIPs/pull/484
Created: 2022-02-09
License: CC-BY-4.0
---

# Changes to Plutus Core

## Abstract

This CIP specifies a process for proposing changes to Plutus Core, its builtins, and its interface to the Cardano ledger.
It gives a taxonomy of typical changes, and explains how these changes may be made, which in some cases requires a CIP.
It introduces the 'Plutus' CIP category for tracking these.

## Motivation: why is this CIP necessary?

The Plutus Core language, its builtins, and its interface to the ledger are all likely to evolve significantly over time. There are many reasons for this:
- We may be able to increase performance, improve safety, or reduce script sizes by changing the language.
- We may be able to improve performance by providing builtin versions of expensive functions.
- We may need to provide builtin versions of sensitive functions (e.g. cryptography) in order to ensure access to high-quality implementations.
- We may find bugs in the implementation that need to be fixed.
- We may need to change the interface to the ledger in order to represent changes in transaction formats.
- We may wish to remove elements which have been deprecated due to the addition of improved versions.
- … and more

This CIP gives a taxonomy of changes, explains how such changes might be implemented in Cardano, and prescribes processes for proposing such changes.

## Background

This CIP assumes general familiarity with Plutus Core and the Cardano ledger, but we give some brief background here.

### Plutus Core

_Plutus Core_ is a script language used in the Cardano ledger. 
For the purposes of this document, Plutus Core consists of various _language constructs_, and also _builtin types and functions_.

Plutus Core has a number of builtin types, such as integers, and builtin functions, such as integer addition. 
Builtin functions provide access to functionality that would be difficult or expensive to implement using the basic constructs of Plutus Core, which is otherwise little more than the untyped lambda calculus.
Builtin functions can operate only over builtin types or arbitrary Plutus Core terms treated opaquely. 
Builtin types come with a _size metric_ which is used by costing functions. 
For example, the size metric for integers returns the bit-size of the integer.

The performance of Plutus Core scripts has two components: how expensive the script actually is to run (_real performance_) and how expensive we say it is to run in the ledger (_model performance_). 

Model performance is calculated by costing _evaluation_ in abstract resource units ("exunits") of CPU and memory. 
Individual steps of evaluation are costed, and builtin functions must also come with a _costing function_ that provides costing information for them. 
The costing function for a builtin function is a mathematical function which takes the sizes of the arguments (as computed by their size metrics), and returns an estimate of the budget that will be used to perform that function. 
For example, the costing function for addition says that the CPU and memory costs are both proportional to the maximum of the sizes of the input integers (with some appropriate constants).

Determining costing functions is done empirically, by running the function in question against a large number of inputs and choosing a costing function that fits the data well.

Plutus Core has a _language version_ (LV).
This is the version of the Plutus Core programming language itself, and it controls e.g. which constructs are available in the language.
Changing any of the features which are guarded by the language version requires a new language version to be supported by the chain.
Note that changing the set of builtin types or functions does _not_ require a new language version; any individual Plutus Core language version is compatible with any set of builtin types and functions.

Depending on the type of change, a major or minor bump to the language version may be required.
The following table shows typical examples.

| Change                                                | Type  | Notes                     |
|-------------------------------------------------------|-------|---------------------------|
| Adding a construct to the language                    | Minor | Backwards-compatible.     |
| Removing a construct from the language                | Major | Not backwards-compatible. |
| Changing the behaviour of a construct in the language | Major | Not backwards-compatible. |
| Changing the binary format of the language in a backwards-compatible way | Minor | Safe even if it makes previously non-deserializable scripts deserializable.[^backwards-safe] |
| Changing the binary format of the language            | Major | Not backwards-compatible. |

[^backwards-safe]: See "Are backwards-compatible binary format changes really safe?".

Since we always need a new Plutus Core langauge version for any change to the language, in the rest of this document we will focus on the introduction of a new langauge version as the proxy for changes to the language.

### Scripts in the Cardano ledger

The Cardano ledger recognizes various kinds of _scripts_ identified by _language_.
This language tag is the only way that the ledger has to distinguish between different types of script.
Hence if we require different behaviour, we need a new language.
We refer to these languages as _ledger languages_ (LLs).

Part of the specification of a language in the ledger is how scripts of that language are run, what arguments they are passed, how those arguments are structured, etc. 
We refer to this as the _ledger-script interface_.

Because we want to occasionally change e.g. the ledger-script interface for Plutus Core scripts, this means we need several ledger languages which all run scripts written in Plutus Core.[^ledger-language-versions]
All Plutus Core ledger languages which are used in the ledger must be supported forever, in order to be able to validate the history of the chain.

[^ledger-language-versions]: The Plutus Core family of ledger languages are sometimes referred to as the Plutus Core _ledger language versions_, and named as such ("PlutusV1", "PlutusV2" etc.) although they actually entirely distinct _languages_ from the perspective of the ledger. In this document we will use the more precise language and refer to them just as distinct ledger languages.

Ledger languages also have an associated subset of the _protocol parameters_. 
These parameters provide the ability to control some aspects of evaluation without a software update. 
The most notable example is a set of parameters which parameterize the costing of program execution.
Hence, a different Plutus Core ledger language can have a different set of costing protocol parameters.

We can change the behaviour of ledger languages in a backwards compatible way with new protocol versions.
This ensures that the new behaviour only becomes available at a particular time in the history of the chain.

Overall the combination of ledger language and protocol version controls:
- The protocol parameters which are available
- The ledger-script interface
- The Plutus Core language versions that are available
- The set of builtin types and values that are available

### Types of change

This document considers the following types of change:

1. The Plutus Core language
    1. Adding a new Plutus Core language version 
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
4. A new Plutus Core _ledger language_ (LL), introduced in a hard fork, and taking effect for scripts that use the new language, but not for those that use the old language.

Intuitively, these correspond to how _compatible_ the change is.
- A backwards- and forwards-compatible change can be deployed with a software update, as nobody can perceive the difference.
- A backwards-compatible (but not forwards-compatible) change must be deployed in a hard fork, since it makes more blocks acceptable than before.
- A backwards-incompatible change requires a new Plutus Core ledger language, so that the ledger can distinguish them, and maintain the old behaviour for old scripts.

The following table lists, for each type of change in "Types of change", what kind of release it requires.

| Change                                                                     | Release            | Notes                                                                                               |
|----------------------------------------------------------------------------|--------------------|-----------------------------------------------------------------------------------------------------|
| Adding a new Plutus Core language version                                 | HF                 | Backwards-compatible since the new behaviour is guarded by the new LV. |
| Adding a new builtin function or type                                      | HF (rarely LL[^binary-backwards]) | Backwards-compatible. Requires a binary format change.                                              |
| Removing a builtin function or type                                        | LL                 | This will cause scripts which use this builtin to be rejected, so is not backwards compatible.      |
| Changing the behaviour of a builtin function or type                       | LL                 | This changes the behaviour of existing scripts, so is not backwards compatible.                     |
| Changing the interface between the ledger and the interpreter              | LL                 | The ledger must provide scripts with exactly the right interface. New interface means new language. |
| Improving model performance                                                | PP                 | _Must_ strictly follow an improvement in real performance.[^why-perf-1]                                      |
| Regressing model performance                                               | PP                 |                                                                                                     |
| Adding cost model parameters                                               | HF                 | All nodes must recognize the new parameter.                                                         |
| Removing cost model parameters                                             | LL                 | Old scripts will require all the old parameters.                                                    |
| Improving real performance                                                 | SU                 |                                                                                                     |
| Regressing real performance                                                | SU                 | _Must_ strictly follow a regression in model performance.[^why-perf-2]                                       |

[^binary-backwards]: The binary format change is backwards compatible unless it breaches the limit of how many builtin functions or types can be encoded, in which case that must be changed, forcing a new LL.
[^why-perf-1]: See "Why do performance changes require extra steps?".
[^why-perf-2]: See "Why do performance changes require extra steps?".

## Specification

### Scope

This CIP deals with the types of change listed in "Types of change".
That list aims to cover the most typical changes to Plutus Core, but it is not exhaustive.
CIPs which do not propose changes in the list but whose authors believe they significantly affect Plutus Core should nonetheless be assigned to the Plutus category.

Additionally, there is significant overlap with the Ledger category around the ledger-script interface and the protocol parameters.
CIPs which change these parts of Cardano should generally use the Plutus category and not the Ledger category, although the Editors may ask the Ledger reviewers to comment.

### The Plutus reviewers

The following table gives the current set of reviewers for Plutus CIPs.

| Name                 | Email                        | GitHub username |
|----------------------|------------------------------|-----------------|
| Ziyang Liu           | ziyang.liu@iohk.io           | zliu41          |

### Changes that require a CIP

This proposal requires that some of the changes listed in "Types of change" (specified below) should:

1. Be proposed in a CIP.
2. Go through additional process in addition to the [usual CIP process](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0001/README.md).

The additional process mostly takes the form of additional information that should be present in the CIP before it moves to particular stages.

The requirement to propose a change via a CIP is, as all CIPs are, advisory. 
In exceptional circumstances or where swift action is required, we expect that changes may still be made without following this process. 
In such circumstances, a retrospective CIP SHOULD be made after the fact to record the changes and the rationale for them.

Changes that require a CIP do not have to each be in an individual CIP, they can be included in batches or in other CIPs. 
So, for example, a single CIP could propose multiple new builtin functions, or a CIP proposing a change to the ledger could also propose a change to the ledger-script interface.

### Processes

All changes that require a CIP SHOULD adhere to the following generic process.

In order to move to Proposed status:
- The Specification MUST include:
    - The type of change that is being proposed.
    - For changes to Plutus Core itself, a formal specification of the changes which is precise enough to update the Plutus Core specification from.
- The Acceptance Criteria MUST include:
    - The external implementations are available.
    - The `plutus` repository is updated with the specification of the proposal.
    - The `plutus` repository is updated with an implementation of the proposal.
- The Implementation Plan MUST include:
    - The type of release that the change requires.

#### Additions to the Plutus Core Builtins

Proposals for additions to the set of Plutus Core builtins SHOULD be proposed in a CIP and SHOULD adhere to the following additional process.

In order to move to Proposed status:
- The Specification MUST include:
    - Names and types/kinds for the new functions or types.
    - A source for the implementation (e.g. a library which can be linked against); or a generic description of the functionality which is implementable in any programming language.
    - For new types
        - A description of how constants of this type will be serialized and deserialized.
        - A precise description of the measure used for the size of a value of that type.
    - For new builtin functions: a costing function for the builtin function.
- The Rationale MUST include:
    - If an external implementation is provided: an argument that it satisfies the following non-exhaustive list of criteria:
        - It is trustworthy 
        - It always terminates
        - It (or its Haskell bindings) never throw any exceptions
        - Its behaviour is predictable (e.g. does not have worst-case behaviour with much worse performance)
    - Discussion of how any measures and costing functions were determined.
- The Acceptance Criteria MUST include:
    - The ledger is updated to include new protocol parameters to control costing of the new builtins.
        
The Rationale of a CIP should always be a clear argument for why the CIP should be adopted.
In this case we recommend including:
- An argument for the utility of the new builtins.
- Examples of real-world use cases where the new additions would be useful.
- If feasible, a comparison with an implementation using the existing features, and an argument why the builtin is preferable (e.g. better performance).

#### Protocol parameter updates

Protocol parameter updates that affect Plutus Core should be proposed in the Ledger category and following its processes.
The only additional process required is review by the Plutus reviewers.

#### Performance changes 

This CIP does not require any process for proposing performance changes. 

#### Bug fixes

A "bug fix" is a change to behaviour where:
- The implemented behaviour does not match the specification; or
- The specified behaviour is clearly wrong (in the judgement of relevant experts)

In this case the fix may be submitted directly to the `plutus` repository and is NOT required to go through the CIP process. 
It must still be released as appropriate. 
For example, if a bug fix changes behaviour, it will have to wait for a new Plutus Core ledger language.

#### Other changes

Proposals for other additions, removals, or changes to behaviour of any part of Plutus Core or its builtins SHOULD be proposed in a CIP.

## Rationale: how does this CIP achieve its goals?

### Do removals and changes really need a new ledger language?

Not being able to make removals or changes to behaviour without a LL is quite painful. 
For example, it means that we cannot just fix bugs in the semantics: we must remain bug-for-bug compatible with any given LL.

It is tempting to think that if we can show that a particular behaviour has never been used in the history of the chain, then changing it is backwards-compatible, since it won’t change the validation of any of the actual chain. 
However, this is sadly untrue. 

1. The behaviour could be triggered (potentially deliberately) in the interval between the update proposal being accepted and it being implemented. This is extremely dangerous and could lead to an un-managed hard fork.
2. The behaviour could be triggered in a script which has not yet been executed on the chain, but whose hash is used to lock an output. This could lead to that output being unexpectedly un-spendable, or some other change in behaviour. Moreover, since we only have the hash of the script, we have no way of telling whether this is the case.

So even if a behaviour is obscure, we cannot just change it.

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

### Why are we reluctant to release new ledger language?

Ledger languages incur a large maintenance cost. 
Each one must continue to work, perfectly, in perpetuity. Furthermore, they may need their own, independent set of cost model protocol parameters, etc.

So it is very desirable to keep the number of ledger languages down. 
The simplest way to do this is to batch changes, and only release a new ledger language occasionally.

## Path to Active

### Acceptance Criteria

This CIP requires the acceptance of the Plutus team, which it has in virtue of its authorship.

### Implementation Plan

No implementation is required.

## Copyright

This CIP is licensed under [CC-BY-4.0][].

[CC-BY-4.0]: https://creativecommons.org/licenses/by/4.0/legalcode
