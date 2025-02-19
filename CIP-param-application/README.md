---
CIP: ????
Title: On-Chain Parameter Application
Status: Proposed
Category: Plutus
Authors:
    - Philip DiSarro <info@anastasialabs.com>
    - Keyan M. <keyanmaskoot@gmail.com>
    - Microproofs <kwhitemsg@gmail.com>
Implementors: []
Discussions: 
    - https://github.com/cardano-foundation/CIPs/pull/934/
Created: 2024-11-06
License: CC-BY-4.0
---

## Abstract
We propose a new Plutus builtin function `builtinApplyParams` with the
signature `BuiltinByteString -> [BuiltinByteString] -> BuiltinByteString` in
order to enable simple and low cost on-chain check for validating instances of
unapplied scripts.

## Motivation: why is this CIP necessary?
Complex contracts tend to depend on multiple scripts, and in some cases,
validation from scripts with some unknown parameters are required.

As a simple example, assume a minting script which needs to validate that the
destination of its token is a parameterized spending script that is uniquely
instantiated for a user.

The [current solution](#alternatives), is costly and relatively complex. With
our proposed builtin function, the minting script of the example above can
be provided with the unapplied script (either directly or indirectly), and have
arbitrary values applied to it as parameters.

## Specification

### Function Definition

We propose the Plutus builtin function `builtinApplyParams`, with the following
type signature:
```hs
builtinApplyParams :: BuiltinByteString -> [BuiltinByteString] -> BuiltinByteString
```

Where the first argument is the unapplied script's CBOR, and
the `BuiltinByteString` list is CBOR bytes of all the parameters that are to be
applied in order. Finally, output will be the fully/partially applied script
CBOR.


### Cost Model

TODO


## Rationale: how does this CIP achieve its goals?

Using the [provided example](#motivation-why-is-this-cip-necessary), the minting
script can have access to the unapplied script:
* Either by direct inclusion as a parameter (which can lead to a large script size)
* Or providing a UTxO as a parameter that houses the unapplied script so that
  the minting script can read it without becoming excessively large

Furthermore, arbitrary parameters can be provided via the redeemer which can be
used to generate an instance's script hash.

In short, we'll get:
* Easier and cheaper parameter verification on-chain
* A more automation-friendly build for such architectures
* Less error prone builds

### Alternatives 

Implementing such a validation on-chain would involve a few steps.

First, the whole target contract has to be wrapped within an outer function
which the parameters will be applied to. This leads to single occurances of
the parameters throughout the script's CBOR.

Secondly, each parameter will be required to have fixed lengths in order to
allow validation of the bytes surrounding parameters. This can be achieved by
assuming these parameters are all hashes, and that their corresponding values
will be provided via the redeemer.

Next, in order to validate a given script is an instance of a known script,
first bytes of an instance must be provided (up until where the parameters are
placed). With this "prefix" at hand, the instance's CBOR can be constructed
on-chain as such:
```hs
let appliedCBOR =
  prefix <> param0 <> paramHeader <> param1 <> paramHeader <> param2 <> postfix
```

Where `postfix` is similar to `prefix`, but for the rest of the script until its
end. Note that `paramHeader` can be reused based on the presumption that all
parameters are of equal lengths.

Finally, this `appliedCBOR` can be hashed to attain its corresponding script
credential.

## Path to Active

### Acceptance Criteria
- [ ] Fully implemented in Cardano.

### Implementation Plan
- [ ] Passes all requirements of both Plutus and Ledger teams as agreed to improve Plutus script efficiency and usability.

## Copyright
This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).

[CC-BY-4.0]: https://creativecommons.org/licenses/by/4.0/legalcode
[Apache-2.0]: http://www.apache.org/licenses/LICENSE-2.0
