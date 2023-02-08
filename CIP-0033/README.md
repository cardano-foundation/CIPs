---
CIP: 33
Title: Reference scripts
Authors:
    - Michael Peyton Jones <michael.peyton-jones@iohk.io>
Implementors:
    - Michael Peyton Jones <michael.peyton-jones@iohk.io>
    - Jared Corduan <jared.corduan@iohk.io>
Status: Active
Category: Plutus
Created: 2021-11-29
License: CC-BY-4.0
Requires: CIP-31
---

# Reference scripts

## Abstract

We propose to allow scripts ("reference scripts") to be attached to outputs, and to allow reference scripts to be used to satisfy script requirements during validation, rather than requiring the spending transaction to do so.
This will allow transactions using common scripts to be much smaller.

## Motivation

Script sizes pose a significant problem. This manifests itself in two ways:
1. Every time a script is used, the transaction which caused the usage must supply the whole script as part of the transaction. This bloats the chain, and passes on the cost of that bloat to users in the form of transaction size fees.
2. Transaction size limits are problematic for users. Even if individual scripts do not hit the limits, a transaction which uses multiple scripts has a proportionally greater risk of hitting the limit.

We would like to alleviate these problems.

The key idea is to use reference inputs and modified outputs which carry actual scripts ("reference scripts"), and allow such reference scripts to satisfy the script witnessing requirement for a transaction.
This means that the transaction which _uses_ the script will not need to provide it at all, so long as it referenced an output which contained the script.

## Specification

We extend transaction outputs with a new optional field, which contains a script (a "reference script").

The min UTXO value for an output with an additional script field depends on the size of the script, following the `coinsPerUTxOWord` protocol parameter.

When we are validating a transaction and we look for the script corresponding to a script hash, in addition to the scripts provided in the transaction witnesses, we also consider any reference scripts from the outputs referred to by the inputs of the transaction.

### Script context

Scripts are passed information about transactions via the script context.
We propose to augment the script context to include some information about reference scripts.

Changing the script context will require a new Plutus language version in the ledger to support the new interface.
The change is: a new optional field is added to outputs and inputs to represent reference scripts.
Reference scripts are represented by their hash in the script context.

The interface for old versions of the language will not be changed.
Scripts with old versions cannot be spent in transactions that include reference scripts, attempting to do so will be a phase 1 transaction validation failure.

### CDDL

The CDDL for transaction outputs will change as follows to reflect the new field.
```
transaction_output =
  [ address
  , amount : value
  , ? datum : $hash32
  , ? ref_script : plutus_script
  ]
```
TODO: can we use a more generic type that allows _any_ script in a forwards-compatible way?

## Rationale

The key idea of this proposal is stop sending frequently-used scripts to the chain every time they are used, but rather make them available in a persistent way on-chain.

The implementation approach follows in the wake of CIP-31 (Reference inputs) and CIP-32 (Inline datums).
The former considers how to do data sharing on chain, and concludes that referencing UTXOs is a good solution.
The latter shows how we can safely store substantial data in UTXOs by taking advantage of existing mechanisms for size control.

It is therefore natural to use the same approach for scripts: put them in UTXOs, and reference them using reference inputs.

### Storing scripts in outputs

There are a few possible alternatives for where to store reference scripts in outputs.

#### 1: The address field

In principle, we could add an "inline scripts" extension that allowed scripts themselves to be used in the address field instead of script hashes.
We could then use such scripts as reference scripts.

However, this approach suffers from a major confusion about the functional role of the script.
You would only be able to provide a reference script that _also_ controlled the spending of the output.
This is clearly not what you want: the reference script could be anything, perhaps a script only designed for use in quite specific circumstances; whereas in many cases the user will likely want to retain control over the output with a simple public key.

#### 2: The datum field

With inline datums, we could put reference scripts in the datum field of outputs.

This approach has two problems.
First, there is a representation confusion: we would need some way to know that a particular datum contained a reference script.
We could do this implicitly, but it would be better to have an explicit marker.

Secondly, this prevents having an output which is locked by a script that needs a datum _and_ has a reference script in it.
While this is a more unusual situation, it's not out of the question.
For example, a group of users might want to use a Plutus-based multisig script to control the UTXO with a reference script in it.

#### 3: A new field

A new field is the simplest solution: it avoids these problems because the new field clearly has one specific purpose, and we do not overload the meanings of the other fields.

### UTXO set size

This proposal gives people a clear incentive to put large amounts (i.e. kilobytes) of data in outputs as reference scripts.

This is essentially the same problem which is faced in CIP-32, and we can take the same stance.
We don't want to bloat the UTXO set unnecessarily, but we already have mechanisms for limiting that (in the form of the min UTXO value), and these should work transparently for reference scripts as they will for inline datums.

### Changing the script context

We don't strictly need to change the script context.
We could simply omit any information about reference scripts carried by outputs.
This would mean that we don't need to change the interface.

We don't have obvious use cases for the information about reference scripts, but the community may come up with use cases, and our general policy is to try and include as much information about the transaction as we can, unless there is a good reason not to.

We also have the question of what to do about old scripts.
We can't really present the information about reference scripts to them in a faithful way, there is nowhere to put the information.
We could omit the information entirely, but this is dangerous in a different way.
Omitting information may lead scripts to make assumptions about the transaction that are untrue; for this reason we prefer not to silently omit information as a general principle.
That leaves us only one option: reject transactions where we would have to present information about reference scripts to old scripts.
