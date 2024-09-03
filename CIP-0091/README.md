---
CIP: 91
Title: Don't force Built-In functions
Category: Plutus
Status: Proposed
Authors:
    - Niels Mündler <n.muendler@posteo.de>
Implementors: []
Discussions:
    - https://github.com/cardano-foundation/cips/pulls/459
Created: 2023-02-05
License: CC-BY-4.0
---

## Abstract
The Untyped Plutus Language Core (UPLC) has established itself as the target language for a host of emerging Smart Contract Languages. These languages implement type safety by checking the types of variables at compile time. In the compiled output, type information is absent and no longer required or checked. This proposal suggests replacing or enhancing the set of builtin functions with untyped builtin functions, whose arguments are devoid of any type instantiations. This change aims to improve performance and reduce resource costs.

## Motivation: why is this CIP necessary?
Many currently available UPLC builtin functions require forcing between 1 and 3 times to eliminate type instantiations checked at a higher level language of the toolstack (PLC), which most third-party tools do not use. These forces only burn cycles of nodes that evaluate contracts, since there is no actual type instantiation happening internally. By removing the need for these no-op force operations, this proposal aims to enhance performance and reduce resource costs.

There is one data point as to how much performance improvement this may bring in the non-optimized case [here](https://github.com/input-output-hk/plutus/issues/4183#issuecomment-957934430). However, the performance improvement in the optimized case is generally constant: One can bind the forced builtins to a variable at the outermost layer of the UPLC program and from there on just use the forced builtins.

## Specification

For all existing UPLC Builtin Functions _x_ that require _n > 0_ forces for evaluation, this proposal suggests to implement the builtin function _x'_
without any required forces.

This proposal suggests that all existing UPLC Builtin Functions _x_ be *replaced* by _x'_. Generally, this proposal also suggests that no further Builtin Functions be defined that require `force`.

## Rationale: how does this CIP achieve its goals?

This proposal reduces the resources needed to evaluate builtin functions by removing the need to apply no-op force operations to them. However, the actual performance impact might be negligible, and the main impact could be on simplifying the language and making it easier for compiler writers. These are weaker reasons than widespread performance improvements. Implementing this proposal may also require a new Plutus ledger language, as described in CIP-35, due to the non-backwards-compatible changes.

The implementation will break the backward compatibility for future Plutus Smart Contracts.

## Path to Active

### Acceptance Criteria

- [ ] `plutus` changes
    - [ ] Specification 
    - [ ] Production implementation
    - [ ] Costing of the new operations
- [ ] `cardano-ledger` changes
    - [ ] Specification, _including_ specification of the script context translation to a Plutus Core term
    - [ ] Implementation of new ledger language, including new ledger-script interface
- [ ] Further benchmarking 
    - [ ] Check additional real-world examples
- [ ] Release
    - [ ] New Plutus language version supported in a released node version
    - [ ] New ledger language supported in a released node version

### Implementation Plan

It is currently not planned to implement this proposal.

## Copyright
This CIP is licensed under [CC-BY-4.0]: https://creativecommons.org/licenses/by/4.0/legalcode
