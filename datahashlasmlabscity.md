---
CIP: ?
Title: New Plutus built-in `dataHash`
Authors: Las Safin <las@mlabs.city>
Discussions-To:
Comments-URI:
Status: Draft
Type: Standards Track
Created: 2022-02-15
* License: Apache-2.0
* Requires: 35
* Replaces: 36
---

# New Plutus built-in `dataHash`

## Abstract

We propose adding a new built-in `dataHash` for calculating the hash of `Data` on-chain,
in such a way that it is coherent with `txInfoData`.

## Motivation

This is useful for essentially "putting" `Data` into token names, the contents of which a script
can access by having the concrete `Data` be passed in the redeemer (whether it's a minting policy
or validator).

It is also possible to verify signatures of (hashes of) `Data` with this built-in.

This likely has many other uses, as it's a powerful feature.

Currently it is essentially infeasible to do this without the built-in, as it's
very expensive to first serialise the `Data` into CBOR then hashing it using `blake2b_256`.

## Specification

### Function definition

The new built-in is:

```haskell
dataHash :: data -> bytestring
```

The reason for the name is that an off-chain `dataHash` already exists.

The semantics should be such that for any key-value pair `(k, v)` in `txInfoData`,
it should be true that `k == dataHash v`.

### Cost model

The CPU cost should be linear in the size metric of the input.

The memory cost of `blake2b_256` is constant, but the memory cost
of serialisation might not be constant even if it's streamed.

It's possible that the memory cost will be linear with the depth of
the data, in which case it might make sense to make the memory
cost logarithmic in the size metric.

## Rationale

A possible alternative is CIP-36, which proposes a function `serialiseData`, such that
`blake2b_256 . serialiseData` is equal to `dataHash`.

The reason `dataHash` is considered to be a better approach by the author,
is that in practice, all sensible uses of `serialiseData` are also possible
using `dataHash`.

Hashing using a different algorithm isn't something you need in practice,
because no existing protocol hashes Plutus's `Data` with something other
than `blake2b_256`. If in a future version of Plutus the hashing algorithm
were to be changed, then `dataHash` would also be changed accordingly.

With this approach, you can not inspect the raw serialised `Data`,
however, this is not something that is useful in practice, as the
serialised `Data` doesn't give you any useful information other
than its hash.

Another important point to note is that `dataHash` is potentially more
efficient on large `Data`, since the hash can be computed without storing
the entire serialisation of the `Data` in memory.

Implementation-wise, it should also be simpler than `serialiseData`, since
there are no considerations wrt. what the format of the serialisation should be,
because it's never exposed to users.

## Backward Compatibility

Adding this built-in doesn't break older transactions. There is the option
of adding this built-in in only Plutus V2.

## Implementations

Issues for the status of the Implementation:
- https://github.com/input-output-hk/plutus/issues/4167
- https://input-output.atlassian.net/browse/OBT-370

## Copyright

This CIP is licensed under Apache-2.0
