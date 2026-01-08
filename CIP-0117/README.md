---
CIP: 117
Title: Explicit script return values
Category: Plutus
Status: Active
Authors:
    - Michael Peyton Jones <michael.peyton-jones@iohk.io>
Implementors: 
    - Michael Peyton Jones <michael.peyton-jones@iohk.io>
Discussions:
    - https://github.com/cardano-foundation/CIPs/pull/747
Created: 2024-01-22
License: CC-BY-4.0
---

## Abstract

Today, Plutus Core scripts signal success or failure exclusively by whether the script terminates normally or abnormally (with an error).
This leads to some false positives, where a script terminates normally, but this was not intended by the author.
We propose to additionally look at what the script evaluates to when checking for success or failure.

## Motivation: Why is this CIP necessary?

Consider the following Plutus scripts, intended to be used as minting policy scripts:

```
\redeemer -> \datum -> \script-context -> (builtin error)
```

```
\redeemer -> \script-context -> (con false)
```

Today, both of these will unconditionally succeed! 

1. Minting policies only receive two arguments, but this script expects three before it does any work. It therefore evaluates successfully to a lambda.
2. This script evaluates _successfully_ to `(con false)`, but the return value is irrelevant since it terminates successfully.

In both cases the user has made a mistake, but this result is that the script fails _open_, that is, anyone can spend such an output.
A variant of the first mistake is for a script to expect too _few_ arguments, but this will almost always result in an error and so fail closed.[^failing-open]

[^failing-open]: It is not universally clear whether it is good to fail open or closed, but generally for systems like this we tend to fail closed, and it is also easier to detect such failures during testing.

Historically, Plutus Core was going to be a typed language, and at least the first kind of error would have been caught by the typechecker. 
However, today there is little stopping people from making such mistakes.

While these mistakes are relatively easily avoidable (any good smart contract toolkit should prevent them), it is nonetheless a potential landmine for users.

## Specification

The specification for checking whether a Plutus Core script accepts a transaction changes as follows (the new part is in brackets):

> A Plutus Core script S with arguments A1...An accepts a transaction if 'eval(S A1 ... An)' succeeds [and evaluates to the builtin constant 'unit'].

This change is not backwards-compatible and will need to go into a new Plutus ledger language.

## Rationale: How does this CIP achieve its goals?

Since the return value of a script will now be significant, a script will only succeed if the whole thing evaluates to 'unit'.
This is very unlikely to happen by accident: mistakes in the number of arguments or in what to return will result in failure.

### Alternatives 

- The status quo is not terrible, and we could simply accept it.
- The return value could be a boolean constant, with 'true' indicating success and 'false' indicating failure.
    - This is slightly more complicated, and technically we only need a designated success value, since "anything else" indicates failure. We don't need to distinguish between "normal exit indicating rejection of the transaction" and "abnormal exit".
- We could specifically detect when a script returns a lambda, and say that that is a failure.
    - This is patching up one particular hole, whereas the proposal here has much more coverage by failing everything that doesn't quite specifically return 'true'.

## Path to Active

### Acceptance Criteria

- [x] The proposal is implemented in the Ledger.
- [x] The ledger changes are released on Mainnnet.

### Implementation Plan

- [x] The Plutus team will implement the changes to the Ledger.

## Copyright

This CIP is licensed under [CC-BY-4.0][].

[CC-BY-4.0]: https://creativecommons.org/licenses/by/4.0/legalcode
