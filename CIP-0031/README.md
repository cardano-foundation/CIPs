---
CIP: 31
Title: Reference inputs
Authors:
    - Michael Peyton Jones <michael.peyton-jones@iohk.io>
Implementors:
    - Michael Peyton Jones <michael.peyton-jones@iohk.io>
    - Jared Corduan <jared.corduan@iohk.io>
Status: Active
Category: Plutus
Created: 2021-11-29
License: CC-BY-4.0
---

## Abstract

We introduce a new kind of input, a _reference_ input, which allows looking at an output without spending it.
This will facilitate access to information stored on the blockchain without the churn associated with spending and recreating UTXOs.

## Motivation

Datums in transaction outputs provide a way to store and access information on the blockchain.
However, they are quite constrained in a number of ways.
Most notably, in order to access the information which is contained in them, you have to _spend_ the output that the datum is attached to.

This has a number of undesirable features:
1. Even if the output is recreated after being spent, it is still a _new_ output. Any other user who wishes to look at the data cannot spend the old output (which is gone), but must rather spend the new output (which they will not know about until the next block). In practice this throttles some applications to one "operation" per block.
2. Looking at the _information_ in the datum requires _spending_ the output, which means that care must be taken over the distribution of any funds in the output (possibly requiring scripts), and spending conditions must be met. This is overly stringent, inconvenient, and expensive.

We would like to have a mechanism for accessing the information in datums that avoids these issues.

### Use cases

Here are some cases where we expect this to be helpful.

1. Inspecting the state (datum, or locked value) of an on-chain application without having to consume the output, e.g. checking the current state of a stablecoin state machine.
2. On-chain data providers that store data in outputs, to be referenced by other scripts.
3. (With inline datums) Creating a single UTXO with data to be used in multiple subsequent transactions, but only paying the cost for submitting it once.

### Enabling further improvements

This proposal was designed in tandem with two further proposals which make use of reference scripts, CIP-32 (Inline datums) and CIP-33 (Reference scripts).
A full assessment of the worth of this proposal should take into account the fact that it is an enabler for these other proposals.

## Specification

### Reference inputs

We introduce a new kind of transaction input, a reference input.
Transaction authors specify inputs as either normal (spending) inputs or reference inputs.

A reference input is a transaction input, which is linked to a particular transaction output as normal, except that it _references_ the output rather than _spending_ it. That is:

- A referenced output must exist in the UTXO set.
- Any value on a referenced output is _not_ considered when balancing the transaction.
- The spending conditions on referenced outputs are _not_ checked, nor are the witnesses required to be present.
    - i.e. validators are not required to pass (nor are the scripts themselves or redeemers required to be present at all), and signatures are not required for pubkey outputs.
- Referenced outputs are _not_ removed from the UTXO set if the transaction validates.
- Reference inputs _are_ visible to scripts.

For clarity, the following two behaviours which are present today are unchanged by this proposal:

1. Transactions must _spend_ at least one output.[^1]
2. Spending an output _does_ require the spending conditions to be checked.[^2]

[^1]: This restriction already exists, and is important. It seems unnecessary, since transactions must always pay fees and fees must come from somewhere, but fees could in principle be paid via reward withdrawals, so the requirement to spend a UTXO is relevant.
[^2]: That is, this proposal does not change outputs or the spending of outputs, it instead adds a new way of _referring_ to outputs.

### Script context

Scripts are passed information about transactions via the script context.
The script context therefore needs to be augmented to contain information about reference inputs.

Changing the script context will require a new Plutus language version in the ledger to support the new interface.
The change in the new interface is: a _new_ field is added to the structure which contains the list of reference inputs.

The interface for old versions of the language will not be changed.
Scripts with old versions cannot be spent in transactions that include reference inputs, attempting to do so will be a phase 1 transaction validation failure.

### Extra datums

Today, transactions can contain extra datums that are not required for validation.
Currently the extra datums must all be pre-images of datum hashes that appear in outputs.
We change this so that the extra datums can also be pre-images of datum hashes that appear in reference inputs.[^3]

Note that the existing mechanism includes the hash of the extra datum structure in the transaction body, so that additional datums cannot be stripped by an attacker without voiding transaction signatures.

[^3]: Pre-images of datum hashes that appear in _spent_ inputs are of course mandatory.

### CDDL

The CDDL for transaction bodies will change to the following to reflect the new field.
```
transaction_body =
 { 0 : set<transaction_input>    ; inputs
 ...
 , ? 16 : set<transaction_input> ; reference inputs
 }
```

## Rationale

The key idea of this proposal is to use UTXOs to carry information.
But UTXOs are currently a bad fit for distributing information.
Because of locality, we have to include outputs that we use in the transaction, and the only way we have of doing that is to _spend_ them - and a spent output cannot then be referenced by anything else.
To put it another way: outputs are resource-like, but information is not resource-like.

The solution is to add a way to _inspect_ ("reference") outputs without spending them.
This allows outputs to play double duty as resource containers (for the value they carry) and information containers (for the data they carry).

### Requirements

We have a number of requirements that we need to fulfil.
- Determinism
    - It must be possible to predict the execution of scripts precisely, given the transaction.
- Locality
    - All data involved in transaction validation should be included in the transaction or the outputs which it spends (or references).
- Non-interference
    - As far as possible, transactions should not interfere with others. The key exception is when transactions consume resources that other transactions want (usually by consuming UTXO entries).
- Replay protection
    - The system should not be attackable (e.g. allow unexpected data reads) by replaying old traffic.
- Storage control and garbage-collection incentives
    - The amount of storage required by the system should have controls that prevent it from overloading nodes, and ideally should have incentives to shrink the amount of storage that is used over time.
- Optimized storage
    - The system should be amenable to optimized storage solutions.
- Data transfer into scripts
    - Scripts must have a way to observe the data.
- Tool and library support
    - It should not be too difficult for tools and libraries to work with the new system.
- Hydra
    - The system should be usable without compromising the needs of Hydra, such as parallel processing of independent parts of the transaction graph.

Reference inputs satisfy these requirements, mostly by inheriting them from the corresponding properties of UTXOs.

- Referencing an output still requires the output to be presented as part of the transaction and be unspent, so determinism is preserved.
- Referenced outputs appear as transaction inputs, so locality is preserved.
- Outputs can be referenced multiple times, so we have non-interference even under heavy usage of referencing. Conflicts can occur only if the output is actually spent.
- Replay protection is inherited because a transaction must always spend at least one UTXO, and UTXOs can only be spent once.
- Storage control is inherited from control of the UTXO set, via the min UTXO value incentives. Data can be "retired" by spending the input (rather than referencing it), reclaiming the min UTXO value.
- Optimized storage is inherited directly from work on improving UTXO storage.
- Data transfer into scripts works automatically since scripts can see transaction inputs.
- Tools and libraries will only have to deal with a new kind of transaction input, and unless they care about scripts they can likely ignore them entirely.
- Hydra is able to work with reference inputs (see below).

### Why UTXOs?

There are various approaches to augmenting Cardano with the ability to store and retrieve data more easily.
All of these require some kind of resource-like system for the _storage_ that is used for data.
The main argument in favour of the reference input approach is that it reuses our existing resource-like system: UTXOs.

As we've seen above, this allows us to satisfy most of our requirements for free.
Any other approach would need new solutions to these problems.

As a brief example, suppose we wanted to instead implement data storage as an on-chain, hash-indexed data store (a proposal we considered).

Then we would need to answer a lot of questions:
- How is the data accessed and retrieved? Are these stateful operations? Does this make transaction ordering more significant, threatening determinism?
- How is the storage usage controlled? Do people pay for storing data? Do they pay for a fixed period, or perpetually? How is data retired?
- How is the storage going to be implemented? How will this affect node memory usage?
- How are scripts going to access the data in the store?
- How will tools interact with and visualize the store and changes to it?

### How should we present the information to scripts?

Scripts definitely need to see reference inputs.
But we have at least two options for how we represent this in the script context: put the reference inputs in their own field; or include them with the other inputs, but tag them appropriately.

Keeping them separate seems wise given the potential for confusing reference inputs for normal inputs.
That would be quite a dangerous programming error, as it might lead a script to believe that e.g. an output had been spent when in fact it had only been referenced.

We also have the question of what to do about old scripts.
We can't really present the information about reference inputs to them in a faithful way: representing them as spending inputs would be wildly misleading, and there is nowhere else to put them.
We could omit the information entirely, but this is dangerous in a different way.
Omitting information may lead scripts to make assumptions about the transaction that are untrue; for this reason we prefer not to silently omit information as a general principle.
That leaves us only one option: reject transactions where we would have to present information about reference inputs to old scripts.

### Accessing the datums of reference inputs

Currently this proposal has somewhat limited utility, because datums in outputs are just hashes, and the spending party is required to find and provide the preimage themselves.
Therefore the CIP-32 proposal for inline datums is complementary, as it allow UTXOs to carry the data itself rather than a hash.

In the mean time (or if CIP-32 is not implemented), we still want users to be _able_ to provide the datums corresponding to datum hashes in reference outputs, so that at least it is possible to reference the data, albeit clumsily.
The easiest solution here is to reuse the existing mechanism for providing pre-images of datum hashes which appear in outputs.

Providing datum hash pre-images remains optional, since there are reasons to use reference inputs even without looking at the datum, e.g. to look at the value in an output.

### Accessing the value locked in outputs

The motivation of this proposal mainly requires looking at the _datums_ of outputs.
But reference inputs allow us to do more: they let us look at the _value_ locked in an output (i.e. how much Ada or other tokens it contains).

This is actually a very important feature.
Since anyone can lock an output with any address, addresses are not that useful for identifying _particular_ outputs on chain, and instead we usually rely on looking for particular tokens in the value locked by the output.
Hence, if a script is interested in referring to the data attached to a _particular_ output, it will likely want to look at the value that is locked in the output.

For example, an oracle provider would need to distinguish the outputs that they create (with good data) from outputs created by adversaries (with bad data).
They can do this with a token, so long as scripts can then see the token!

### Hydra

We want reference inputs to be usable inside Hydra heads.
This raises a worry: since Hydra processes independent parts of the transaction graph in parallel, what happens if it accepts one transaction that references an output, and one that spends the output, but then the first transaction gets put into a checkpoint before the second?

Fortunately, Hydra already has to deal with double-spend conflicts of this kind (although in the naive protocol this results in a decommit).
This proposal simply introduces a new kind of conflict, a reference-spend conflict.
Reference-spend conflicts should be handled by the same mechanism that is used to handle double-spend conflicts.

### Controlling referencing

One thing that a user might want to do is to control who can reference an output.
For example, an oracle provider might want to only allow a transaction to reference a particular output if the transaction also pays them some money.

Reference inputs alone do _not_ provide any way to do this.
Another mechanism would be required, but there is no consensus on what the design should be, so it is currently out of scope for this proposal.
A brief summary of a few options and reasons why they are not obvious choices is included below.

A key issue is that the choice to control referencing must lie with the _creator_ of the output, not the _spender_.
Therefore we _must_ include some kind of change to outputs so that the creator can record their requirements.

#### Check inputs

A "check input" is like a reference input except that the spending conditions _are_ checked.
That is, it acts as proof that you _could_ spend the input, but does not in fact spend it.

Since check inputs cause validator scripts to be run, it seems like they could allow us to control referencing.
There are two wrinkles:

- The same script would be used for both referencing and spending, overloading the meaning of the validator script. This is still _usable_, however, since the redeemer could be used to indicate which action is being taken.
- We would need a flag on outputs to say "this output cannot be referenced, but only checked". Exactly what this should look like is an open question, perhaps it should be generic enough to control all the possible ways in which an output might be used (of which there would be three).

#### Referencing conditions

"Referencing conditions" would mean adding a new field to outputs to indicate under what conditions the output may be referenced.
This could potentially be an entire additional address, since the conditions might be any of the normal spending conditions (public key or script witnessing).

However, this would make outputs substantially bigger and more complicated.

### Related work

Reference inputs are very similar to Ergo's "data inputs".
We chose to name them differently since "data" is already a widely used term with risk for confusion.
We might also want to introduce other "verb" inputs in future.
