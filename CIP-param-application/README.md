---
CIP: ????
Title: On-Chain Parameter Application
Status: Proposed
Category: Plutus
Authors:
    - Keyan M. <keyanmaskoot@gmail.com>
Implementors: []
Discussions: 
    - https://github.com/cardano-foundation/CIPs/pull/999/
Created: 2024-11-04
License: CC-BY-4.0
---

## Abstract
We propose a new Plutus builtin function `builtinApplyParams` with the
signature `BuiltinByteString -> [BuiltinData] -> ScriptHash` in order to enable
simple and low cost on-chain check for validating instances of unapplied
scripts.

## Motivation: why is this CIP necessary?
Complex contracts tend to depend on multiple scripts, and in some cases,
validation from scripts with some unknown parameters are required.

As a simple example, assume a minting script which needs to validate that the
destination of its token is a a parameterized spending that is uniquely
instantiated for a user.

The current solution involves wrapping the spending script with an inner lambda,
expecting the parameters as hashed values to ensure their constant lengths, and
expect each parameter to be provided via the redeemer. This approach allows
slicing unapplied CBOR of the applied script at specific indexes in order to
validate the presence of the expected hash.

This, however, is a costly and relatively complex approach.

With our proposed builtin function, the minting script of the example above can
be provided with the unapplied script (either directly or indirectly), and have
arbitrary values applied to it as parameters.

## Specification

### Function Definition

we propose the Plutus builtin function `builtinApplyParams`, with the following
type signature:
```hs
builtinApplyParams :: BuiltinByteString -> [BuiltinData] -> ScriptHash
```

Where the first argument is the unapplied script's CBOR, and
the `BuiltinData` list is all the parameters that are to be applied in order.
Finally the result will be hash of the applied script.


### Cost Model

TODO


## Rationale: how does this CIP achieve its goals?

With a builtin function, we'll get cheap and simple on-chain parameter
validation. Consequently, this will enable easier implementation of advanced
contracts with enhanced guarantees.

### Alternatives 

Please see example above under the [motivation section](#motivation-why-is-this-cip-necessary).

## Path to Active

### Acceptance Criteria
- [] Fully implemented in Cardano.

### Implementation Plan
- [] Passes all requirements of both Plutus and Ledger teams as agreed to improve Plutus script efficiency and usability.

## Copyright
This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).

[CC-BY-4.0]: https://creativecommons.org/licenses/by/4.0/legalcode
[Apache-2.0]: http://www.apache.org/licenses/LICENSE-2.0
