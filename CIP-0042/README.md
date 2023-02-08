---
CIP: 42
Title: New Plutus built-in serialiseData
Authors: Matthias Benkort <matthias.benkort@iohk.io>, Sebastian Nagel <sebastian.nagel@iohk.io>
Discussions-To: https://github.com/cardano-foundation/CIPs/pull/218
Comments-URI: https://github.com/cardano-foundation/CIPs/pull/218
Category: Plutus
Status: Active
Type: Standards Track
Created: 2022-02-09
License: Apache-2.0
Requires: CIP-35

---

# New Plutus built-in serialiseData

## Abstract

This document describes the addition of a new Plutus builtin for serialising `BuiltinData` to `BuiltinByteString`.

## Motivation

As part of developing on-chain script validators for [the Hydra Head protocol](https://eprint.iacr.org/2020/299), we stumble across a peculiar need for on-chain scripts: we need to verify and compare digests obtained from hashing elements of the script's surrounding transaction.

In this particular context, those elements are transaction outputs (a.k.a. `TxOut`). While Plutus already provides built-in for hashing data-structure (e.g. `sha2_256 :: BuiltinByteString -> BuiltinByteString`), it does not provide generic ways of serialising some data type to `BuiltinByteString`.

In an attempt to pursue our work, we have implemented [an on-chain library (plutus-cbor)][plutus-cbor] for encoding data-types as structured [CBOR / RFC 8949][CBOR] in a _relatively efficient_ way (although still quadratic, it is as efficient as it can be with Plutus' available built-ins) and measured the memory and CPU cost of encoding `TxOut` **in a script validator on-chain**.

![](https://i.imgur.com/AtHE0p4.png)

The above graph shows the memory and CPU costs **relative against a baseline**, of encoding a `TxOut` using `plutus-cbor` in function of the number of assets present in that `TxOut`. The costs on the y-axis are relative to the maximum execution budgets (as per mainnet's parameters, December 2021) allowed for a single script execution. As can be seen, this is of linear complexity, i.e. O(n) in terms of the number of assets. These results can be reproduced using the [encoding-cost][] executable in our repository.

> Note that we have also calculated similar costs for ada-only `TxOut`, in function of the number of `TxOut` which is about twice as worse but of similar linear shape.

We we can see on the graph, the cost is manageable for a small number of assets (or equivalently, a small number of outputs) but rapidly becomes limiting. Ideally, we would prefer the transaction size to be the limiting factor when it comes to the number of outputs we can handle in a single validation.

Besides, in our discussions with the Marlowe team, we also discovered that they shared a similar problem when it came to serialising merkleized ASTs.

Underneath it all, it seems that it would be beneficial to have a new built-in at our disposal to serialise any Plutus `BuiltinData` to `BuiltinByteString` such that validators could leverage more optimized implementations and bytestring builders via built-ins than what's available on-chain, hopefully reducing the overall memory and CPU costs.

## Specification

### Function definition

We define a new Plutus built-in function with the following type signature:

```hs
serialiseData :: BuiltinData -> BuiltinByteString
```

### Binary data format

Behind the scene, we expect this function to use a well-known encoding format to ease construction of such serialisation off-chain (in particular, for non-Haskell off-chain contract codes). A natural choice of binary data format in this case is [CBOR][] which is:

1. Efficient;
2. Relatively simple;
3. Use pervasively across the Cardano ecosystem

Furthermore, the Plutus' ecosystem already provides [a _quite opinionated_ implementation of a CBOR encoder][encodeData] for built-in `Data`. For the sake of documenting it as part of this proposal, we provide here-below the CDDL specification of that existing implementation:

```cddl
plutus_data =
    constr<plutus_data>
  / { * plutus_data => plutus_data }
  / [ * plutus_data ]
  / big_int
  / bounded_bytes

constr<a> =
    #6.121([])
  / #6.122([a])
  / #6.123([a, a])
  / #6.124([a, a, a])
  / #6.125([a, a, a, a])
  / #6.126([a, a, a, a, a])
  / #6.127([a, a, a, a, a, a])
  ; similarly for tag range: #6.1280 .. #6.1400 inclusive
  / #6.102([uint, [* a]])

big_int = int / big_uint / big_nint
big_uint = #6.2(bounded_bytes)
big_nint = #6.3(bounded_bytes)

bounded_bytes = bytes .size (0..64)
```

> NOTE: The CDDL specification is extracted from the wider [alonzo_cddl specification][] of the Cardano ledger.

### Cost Model

The `Data` type is a recursive data-type, so costing it properly is a little tricky. The Plutus source code defines an instance of `ExMemoryUsage` for `Data` with [the following interesting note](https://github.com/input-output-hk/plutus/blob/37b28ae0dc702e3a66883bb33eaa5e1156ba4922/plutus-core/plutus-core/src/PlutusCore/Evaluation/Machine/ExMemory.hs#L205-L225):

> This accounts for the number of nodes in a `Data` object, and also the sizes of the contents of the nodes.  This is not ideal, but it seems to be the best we can do. At present this only comes into play for 'equalsData', which is implemented using the derived implementation of '==' [...].

We propose to re-use this instance to define a cost model linear in the size of data defined by this instance. What remains is to find a proper coefficient and offset for that linear model. To do so, we can benchmark the execution costs of encoding arbitrarily generated `Data` of various sizes, and retro-fit the cost into a linear model (provided that the results are still attesting for that type of model).

Benchmarking and costing `serialiseData` was done in [this PR](https://github.com/input-output-hk/plutus/pull/4480) according to this strategy. As the benchmark is not very uniform, because some cases of `Data` "structures" differ in CPU time taken to process, the linear model is used as an **upper bound** and thus conservatively overestimating actual costs.

## Rationale

* Easy to implement as it reuses existing code of the Plutus codebase;
* Such built-in is generic enough to also cover a wider set of use-cases, while nicely fitting ours;
* Favoring manipulation of structured `Data` is an appealing alternative to many `ByteString` manipulation use-cases;
* CBOR as encoding is a well-known and widely used standard in Cardano, existing tools can be used;
* The hypothesis on the cost model here is that serialisation cost would be proportional to the `ExMemoryUsage` for `Data`; which means, given the current implementation, proportional to the number and total memory usage of nodes in the `Data` tree-like structure.
* Benchmarking the costs of serialising `TxOut` values between [plutus-cbor][] and [cborg][] confirms [cborg][] and the existing [encodeData][]'s implementation in Plutus as a great candidate for implementing the built-in:

  ![](https://i.imgur.com/6GWrIHb.png)

  Results can be reproduced with the [plutus-cbor benchmark][].

## Path To Active

- [x] Using the existing _sizing metric_ for `Data`, we need to determine a costing function (using existing tooling / benchmarks? TBD)
- [x] The Plutus team updates plutus to add the built-in to PlutusV1 and PlutusV2 and uses a suitable cost function
- [ ] The binary format of `Data` is documented and embraced as an interface within `plutus`.
- [ ] Release it as a backward-compatible change within the next hard-fork

## Alternatives

* We have identified that the cost mainly stems from concatenating bytestrings; so possibly, an alternative to this proposal could be a better way to concatenate (or to cost) bytestrings (Builders in Plutus?)

* If costing for `BuiltinData` is unsatisfactory, maybe we want have only well-known input types, e.g. `TxIn`, `TxOut`, `Value` and so on.. `WellKnown t => t -> BuiltinByteString`

## Backward Compatibility

* Additional built-in: so can be added to PlutusV1 and PlutusV2 without breaking any existing script validators. A hard-fork is however required as it would makes more blocks validate.

## Copyright

This CIP is licensed under Apache-2.0

[CBOR]: https://www.rfc-editor.org/rfc/rfc8949
[plutus-cbor]: https://github.com/input-output-hk/hydra-poc/tree/a4b843a040897e45120cb63b666d965759091651/plutus-cbor
[cborg]: https://hackage.haskell.org/package/cborg-0.2.4.0
[encoding-cost]: https://github.com/input-output-hk/hydra-poc/tree/759fee84475f951aaf2f35acdb8ab82094ec5fbf/plutus-cbor/exe/encoding-cost/Main.hs
[alonzo_cddl specification]: https://github.com/input-output-hk/cardano-ledger/blob/aebd64e015ec0825776c256faed9d8632712beb0/eras/alonzo/test-suite/cddl-files/alonzo.cddl#L276-L296
[encodeData]: https://github.com/input-output-hk/plutus/blob/1f31e640e8a258185db01fa899da63f9018c0e85/plutus-core/plutus-core/src/PlutusCore/Data.hs#L108
[plutus-cbor benchmark]: https://github.com/input-output-hk/hydra-poc/tree/759fee84475f951aaf2f35acdb8ab82094ec5fbf/plutus-cbor/bench/Main.hs
