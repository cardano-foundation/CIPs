---
CIP: 32
Title: Inline datums
Status: Active
Category: Plutus
Authors:
    - Michael Peyton Jones <michael.peyton-jones@iohk.io>
Implementors:
    - Michael Peyton Jones <michael.peyton-jones@iohk.io>
    - Jared Corduan <jared.corduan@iohk.io>
Discussions:
    - https://github.com/cardano-foundation/CIPs/pull/160
Created: 2021-11-29
License: CC-BY-4.0
---

## Abstract

We propose to allow datums themselves to be attached to outputs instead of datum hashes.
This will allow much simpler communication of datum values between users.

## Motivation: why is this CIP necessary?

Conceptually, datums are pieces of data that are attached to outputs.
However, in practice datums are implemented by attaching _hashes_ of datums to outputs, and requiring that the spending transaction provides the actual datum.

This is quite inconvenient for users.
Datums tend to represent the result of computation done by the party who creates the output, and as such there is almost no chance that the spending party will know the datum without communicating with the creating party.
That means that either the datum must be communicated between parties off-chain, or communicated on-chain by including it in the witness map of the transaction that creates the output ("extra datums").
This is also inconvenient for the spending party, who must watch the whole chain to spot it.

It would be much more convenient to just put the _datum itself_ in an output, which is what we propose.

### Use cases

We expect that, provided we are able to bring the cost low enough, a large proportion of dapp developers will make use of this feature, as it will simplify their systems substantially.

## Specification

Transaction outputs are changed so that the datum field can contain either a hash or a datum (an "inline datum").

The min UTXO value for an output with an inline datum depends on the size of the datum, following the `coinsPerUTxOWord` protocol parameter.

When an output with an inline datum is spent, the spending transaction does not need to provide the datum itself.

### Script context

Scripts are passed information about transactions via the script context.
The script context therefore needs to be augmented to contain information about inline datums.

Changing the script context will require a new Plutus language version in the ledger to support the new interface.

There are two changes in the new version of the interface:
- The datum field on transaction outputs can either be a hash or the actual datum.
- The datum field on transaction inputs can either be a hash or the actual datum.

The interface for old versions of the language will not be changed.
Scripts with old versions cannot be spent in transactions that include inline datums, attempting to do so will be a phase 1 transaction validation failure.

### CDDL

The CDDL for transaction outputs will change as follows to reflect the new alternative.
```
transaction_output =
  [ address
  , amount : value
  , ? datum : $hash32 / plutus_data
  ]
```
TODO: should there be a dedicated production for datum-hash-or-datum? Does it need to be tagged?

## Rationale: how does this CIP achieve its goals?

The key idea of this proposal is simply to restore the conceptually straightforward situation where datums are attached to outputs.
Historically, this was the way that the EUTXO model was designed, and switching to datum hashes on outputs was done to avoid bloating UTXO entries, which at that time (pre-multiasset) were constant-size (see [^1] page 7).

Now that we have variable-sized UTXO entries and the accounting to support them, we can restore inline datums.

Since inline datums change very little about the model apart from where data is stored, we don't need to worry about violating any of the other requirements of the ledger, but we do need to worry about the effect on the size of the UTXO set.

### UTXO set size

This proposal gives users a way to put much larger amounts of data into the UTXO set.
Won’t this lead to much worse UTXO set bloat?

The answer is that we already have a mechanism to discourage this, namely the minimum UTXO value.
If inline datums turns out to drive significantly increased space usage, then we may need to increase `coinsPerUTxOWord` in order to keep the UTXO size down.
That will be costly and inconvenient for users, but will still allow them to use inline datums where they are most useful and the cost is bearable.
Furthermore, we hope that we will in fact be able to _reduce_ `coinsPerUTxOWord` when the upcoming work on moving the UTXO mostly to on-disk storage is complete.

Another guard rail would be to enforce upper limits on the size of inline datums.
At the extreme, we could bound them to the size of a hash, which would guarantee no more space usage than today.
However, this is much worse for users, since it introduces a sharp discontinuity where an inline datum is entirely acceptable, until it crosses the size threshold at which point it is unacceptable, and there is no way to avoid this.
Generally we prefer to avoid such discontinuities in favour of gradually increasing costs.

In practice, what is implemented here may depend on whether the UTXO-on-disk work is completed by the time that this proposal is implemented.

### Other modes of specifying datums

We could deprecate the other methods of specifying datums (datum hashes or datum hashes+extra datums).
However, the other approaches also have some advantages.

- Transmission costs: creator pays versus consumer pays
    - Inline datums: creator pays
    - Datum hashes: consumer pays
    - Datum hashes+extra datums: both pay
- Min UTXO value costs
    - Inline datums: depends on data size
    - Datum hashes: fixed cost
    - Datum hashes+extra datums: fixed cost
- Privacy
    - Inline datums: datum is immediately public
    - Datum hashes: datum is not public until consumed
    - Datum hashes+extra datums: datum is immediately public, but only to chain-followers
- Communication of datums
    - Inline datums: easy on-chain communication
    - Datum hashes: off-chain communication necessary
    - Datum hashes+extra datums: complicated on-chain communication

Any one of these factors could be important to particular use cases, so it is good to retain the other options.

### The script context

#### Including information about inline datums

In principle we do not need to let scripts see whether a datum is inline or not.
We could pretend that inline datums are non-inline and insert them into the datum witness map.

The underlying question is: do we want scripts to be able to make assertions about whether datums are inline or not?
There are reasons to want to do this: _not_ using inline datums causes communication issues for users, and so it is quite reasonable that an application developer may want to be able to enforce their use.

Furthermore, as a general principle we try to keep the script context as faithful to real transactions as possible.
Even if the use for the information is not immediately obvious, we try to err on the side of providing it and letting users decide.

Hence we _do_ include information about inline datums in the script context.

#### Representation and backwards compatibility

There are a couple of options for how to change the representation of the script context to include the new information, and whether to make a backwards compatibility effort for old language versions.

For the new script context:

1. Match the ledger representation as much as possible: change the fields on inputs and outputs to be either a datum hash or a datum.
2. Try to only have one way to look up datums: put inline datums in the datum witness map and insert their hashes into the corresponding inputs and outputs; optionally add a boolean to inputs and outputs to indicate whether the datum was originally inline.

For backwards compatibility:

1. Don't try to represent inline datums for scripts using old language versions: old scripts simply can't be run in transactions that use inline datums (since we can't represent the information).
2. Rewrite inline datums as non-inline datums: put inline datums in the datum witness map and insert their hashes into the corresponding inputs and outputs.

For the new script context, option 1 has the significant advantage of matching the ledger representation of transactions.
This makes it easier to implement, and also avoids conceptual overhead for users who would have to distinguish the two ways of representing transactions.
While the conceptual distance here may be small, if we let it grow over time then it may become quite confusing.

We then have the choice of what to do about backwards compatibility.
Option 2 would work, but is more complicated for the ledger and is inconsistent in representation with our choice for the new script context (inline datums are sometimes represented faithfully, and sometimes put in the witness map).
Option 1 is simple, but doesn't allow old scripts to work with inline datums.
This would not be so bad if it just meant that old scripts could not be spent in transactions that include inline datums, but it also introduces a new way to make an unspendable output.
If a user creates an output with an old script and an inline datum, then any transaction spending that output will include an inline datum, which we would not allow.

Unfortunately, we cannot prevent users from creating such outputs in general, since script addresses do not include the script language, so the ledger cannot tell whether the inline datum is permissible or not.
Client code typically _will_ be able to do this, since it will usually know the script.

The mitigating factor is that we expect this to be uncommon in practice, particularly since we expect that most users will move to the new version relatively quickly, since we expect support for inline datums to be desirable, and released alongside other desirable features.

Hence we choose both option 1s and do _not_ provide backwards compatibility for old language versions.

## Path to Active

### Acceptance Criteria

- [x] Fully implemented in Cardano as of the Vasil protocol upgrade.

### Implementation Plan

- [x] Passes all requirements of both Plutus and Ledger teams as agreed to improve Plutus script efficiency and usability.

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).

[^1]: Chakravarty, Manuel M. T. et al., "The extended UTXO model"
