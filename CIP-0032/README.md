---
CIP: 32
Title: Inline datums
Authors: Michael Peyton Jones <michael.peyton-jones@iohk.io>
Comments-Summary: No comments
Comments-URI: 
Status: Draft
Type: Standards Track
Created: 2021-11-29
License: CC-BY-4.0
---

# Inline datums

## Abstract

We propose to allow datums themselves to be attached to outputs instead of datum hashes.
This will allow much simpler communication of datum values between users.

## Motivation

Conceptually, datums are pieces of data that are attached to outputs. 
However, in practice datums are implemented by attaching _hashes_ of datums to outputs, and requiring that the spending transaction provides the actual datum.

This is quite inconvenient for users. 
Datums tend to represent the result of computation done by the party who creates the output, and as such there is almost no chance that the spending party will know the datum without communicating with the creating party.
That means that either the datum must be communicated between parties off-chain, or communicated on-chain by attaching it to the transaction that creates the output (which is also inconvenient in that the spending party must watch the whole chain to spot it).

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

Old versions of the language will retain the old interface, but the construction of the script context in the old interface is also changed as follows: if either an input or an output has an inline datum, we replace it by its hash, and put the datum in the existing datum-hash-to-datum mapping.

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

## Rationale

The key idea of this proposal is simply to restore the conceptually straightforward situation where datums are attached to outputs.
Historically, this was the way that the EUTXO model was designed, and switching to datum hashes on outputs was done to avoid bloating UTXO entries, which at that time (pre-multiasset) were constant-size (see [1] page 7).

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

We could deprecate the other methods of specifying datums (datum hashes or datum hashes+optional datums).
However, the other approaches also have some advantages.

- Transmission costs: creator pays versus consumer pays
    - Inline datums: creator pays
    - Datum hashes: consumer pays
    - Datum hashes+optional datums: both pay
- Min UTXO value costs
    - Inline datums: depends on data size
    - Datum hashes: fixed cost
    - Datum hashes+optional datums: fixed cost
- Privacy
    - Inline datums: datum is immediately public
    - Datum hashes: datum is not public until consumed
    - Datum hashes+optional datums: datum is immediately public, but only to chain-followers
- Communication of datums
    - Inline datums: easy on-chain communication
    - Datum hashes: off-chain communication necessary
    - Datum hashes+optional datums: complicated on-chain communication

Any one of these factors could be important to particular use cases, so it is good to retain the other options.

### Changing the script context

We don't strictly need to change the script context.
We could use the fall-back approach that we use for the old interface, namely continuing to pretend that datums are always hashes, and providing the mapping from hashes to datums.
This would be functionally equivalent.

The only advantage of changing it is that it's more honest to the real representation of transactions, and therefore allows scripts to insist on inline datums if they want.
It's unclear whether this is desirable.

## References

[1]: Chakravarty, Manuel MT, et al. "The extended UTXO model." 
