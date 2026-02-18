---
CPS: 26
Title: Fully homomorphic encryption with programmable bootstrapping
Category: Plutus
Status: Open
Authors: Koz Ross <koz@mlabs.city>
Proposed Solutions: []
Discussions: 
    - Original PR: https://github.com/cardano-foundation/CIPs/pull/1143
Created: 2026-01-29
License: Apache-2.0
---

## Abstract

Fully homomorphic encryption, particularly TFHE, offers the ability for
encrypted operations on encrypted data: a powerful complement to the
decentralization and public visibility of the blockchain. This capability
already exists on other chains by way of the Zama protocol, but not on Cardano,
limiting what script and dApp developers can do relative those other chains.

## Problem

[Fully homomorphic encryption][fully-homomorphic-encryption] is a powerful
technique, allowing processing of encrypted data without requiring it to be
decrypted first. It is a natural complement to the blockchain's public
verifiability by allowing confidentiality of data as well. One solution in this
space, namely [TFHE][tfhe], stands above all others by offering _programmable
bootstrapping_. Put simply, programmable bootstrapping allows for arbitrary
Boolean circuits to be encrypted and applied to (also encrypted) data without
having to decrypt either. This creates a perfect combination with the blockchain
principle of 'your keys, your coins': only the holder of the TFHE key can know
what the input, the computation, and the answer are, but the chain can execute
these computations for them. Moreover, this capability is, by its definition,
post-quantum secure: an important consideration for all chains, including
Cardano.

So useful is this capability that a cross-chain protocol already exists to
provide TFHE capabilities, namely [Zama][zama], which gives such capabilities to
Ethereum, and most recently Solana. Thus, blockchain applications can already
realize the benefits of TFHE-powered fully homomorphic encryption, including
programmable bootstrapping, _today_. Unfortunately, Cardano does not support
fully homomorphic encryption directly, using TFHE or not, or whether by a
cross-chain protocol or natively. While in theory, such capabilities could be
implemented as part of a script, doing so would be prohibitively difficult,
assuming it is even feasible at all. These difficulties are similar to the
difficulties of implementing _any_ cryptographic capability as a script, as
evidenced by [the Grumplestiltskin project][grumplestiltskin], as well as the
[SHA512][sha512-plutus] and [Ed25519 signature verification][ed25519-plutus]
benchmarks in Plutus, which is why Cardano scripts have access to various
cryptographic primitives as builtin operations. Something similar would need to
exist for TFHE to be usable, but as current, it does not.

## Use Cases

The use cases for TFHE would primarily be similar to those that people use
regular cloud services for. Even in such cases, TFHE would be advantageous, as
the operators of the cloud service would not be able to do anything, or even
know about, either the data they were hosting or the operations the owner of
that data was asking them to perform on their behalf. In a blockchain setting,
this is even more important: as blockchains are public by their very definition,
any data or operations on them end up public as well, magnifying problems with
cloud services such as security and control over data. As a result, many such
applications cannot benefit from the decentralization of blockchains, as
revealing data, and what's being done with it, to the world is unacceptable.
With TFHE, this problem vanishes. Moreover, programmable bootstrapping allows
not only computation _hiding_, but potentially a lot of implementation power, as
any Boolean circuit could be used as the operation. This means that applications
would not be limited by the primitives provided by UPLC.

Several examples follow. Worth noting here is that all of these are already
possible on other chains by way of the Zama protocol.

### Onchain identity

The idea of sending identifying information to a service is typical for
'standard' cloud applications, such as when buying products online and booking
flights. However, doing so onchain is risky, as it makes a lot of sensitive
information public. TFHE would allow 'hiding' this data while still allowing it
to be processed onchain. In particular, the public-key variant of TFHE could
allow a 'double security' measure: a particular service could use your public
key to encrypt the Boolean circuit to be applied to your data, allowing you, but
nobody else, to inspect what it should do. 

### Confidential governance

Governance on Cardano is a significant and important feature, but currently,
voting is done 'in the clear', which makes it susceptible to bribery, blackmail
and biases. With TFHE, specific votes could be hidden, but their total still
determined as the result of a specific Boolean circuit applied to accumulate the
results.

### Onchain corporations

Managing a company, or entire organization, onchain is not currently thinkable,
as it would require revealing confidential information such as customer and
employee registers, financial information, trade secrets and other similar
information. Using TFHE, all of this could be kept confidential, while still
benefitting from decentralization and automation by way of (also encrypted)
Boolean circuits. Use of multiple keys could also ensure compartmentalization of
information: a given member of the organization would have access to a given
key, allowing them to know specific operations and data, but not others.

## Goals

The primary goal is to provide a builtin operation which, when given an
(encrypted) Boolean circuit and (encrypted) data, apply the circuit to the data
to produce a result (which is also encrypted). Other capabilities of TFHE,
including encryption and decryption, as well as encoding of Boolean circuits, do
not need to be provided, as they can, and should, be done offchain. This
operation should be usable as any other builtin, and ideally be as low-cost as
is feasible. While it would be beneficial to provide support for the offchain
TFHE operations in some capacity as well, how this should be done is beyond the
scope of this CPS.

The specific implementation of this builtin could be approached in one of three
ways:

* Making the Zama protocol available on Cardano (the _non-native_ approach); or
* Binding to `tfhe-rs` inside of Plutus Core (or some other Cardano dependency)
  and using it as a backend (the _FFI_ approach); or
* Implementing TFHE ourselves and integrating it into Plutus Core (the _native_
  approach).

From a developer experience perspective (that is, for those using TFHE in
scripts or dApps), which of these approaches gets chosen wouldn't matter much,
as the interface provided will be very similar in any of these cases. However,
other considerations make these three choices quite different in practice. We
discuss this further in the 'Open Questions' section. It is likely that a
research step would be neede before any decision on this can be made.

## Open Questions

Two major open questions exist with regard to providing TFHE capabilities to
onchain scripts: which approach to making TFHE available onchain should be used, and
how to address the interaction of costing and programmable bootstrapping.
Answers to these questions are related, but ultimately independent: whatever
choice is made for the first will impact, but not eliminate, the second. We
discuss these questions further below, and describe some of the implications of
possible solutions.

### Choice of approach

Each of the three previously-described approaches to making TFHE capabilities
available have advantages and drawbacks, which makes the choice between them
non-obvious. Which approach is the correct choice depends on many factors, some
of which will require further research to properly assess. We present the
factors we are currently aware of below.

The main benefit of the non-native approach is that the Zama protocol itself
provides the TFHE functionality, and the Cardano ecosystem would not have to
implement it at any level. Setting aside the resulting simplicity at the level
of Plutus Core and UPLC, this solution also reduces the maintenance burden on
Cardano, as improvements in Zama or their implementation of TFHE would not have
to be 'transferred over' before script and dApp developers could benefit.
However, the largest downside is that it is not clear whether Cardano support
for the Zama protocol could be done unilaterally: that is, without Zama's
involvement. If Zama would need to be involved somehow, this could complicate
matters significantly, including in ways not directly related to code.
Additionally, just because TFHE functionality would not have to be implemented
for the non-native approach, the necessary 'glue' to use the Zama protocol (and
its infrastructure) as part of Cardano scripts may require changes at the level
of the Cardano node implementation or other Cardano libraries, which may end up
being as much, or even more, work than implementing TFHE. Lastly, it is not
clear whether the interface (at the UPLC level, usable by scripts) we could get
by way of the Zama protocol would be suitable for Cardano scripts and dApps.

The FFI and native approaches, by contrast, are almost the direct opposite:
their largest advantage is that either of them could be done without the
involvement of any organization outside of the Cardano space, and Zama in
particular. Furthermore, having full control over the implementation would mean
two additional benefits:

* In the Cardano ecosystem, only Plutus Core would require changing; and
* The TFHE capabilities could potentially be used elsewhere, in ways not related
  to the chain, by other developers.

At the same time, both the FFI and native approaches pose non-trivial amounts of
work. While the FFI approach would be much easier (and Haskell bindings to Rust
code are [already in use][rust-binds] on Cardano), there are still
considerations that may make the native approach more attractive, as it would
reduce dependency on `tfhe-rs`, and may even perform better. However, to truly
answer this question requires further research and performance measurements, as
well as considerations around how such things would be integrated into Plutus
Core.

### Programmable bootstrapping and costing onchain

As programmable bootstrapping has the potential of representing _any_ Boolean
circuit, it effectively forms a sub-language of its own, outside of UPLC.
Furthermore, because TFHE allows for (representations of) such circuits to be
encrypted, we cannot even know what the circuit we have to compute with is, or
gain much insight into its size or complexity. However, all Cardano scripts have
a cost, determined by a costing function assigning numerical values to the
execution time and memory use of every builtin. Thus, any builtin that
evaluates TFHE-represented circuits must be given a cost too.

This poses a huge problem: how can we assign a cost to something we cannot
inspect? Even if the circuit itself were 'in the clear', this creates the same
problem as costing most higher-order builtins (builtins that take function
arguments). Although Boolean circuits are a more 'well-behaved' model than an
untyped lambda calculus like UPLC, it can still potentially 'hide' a lot of
computation and memory use. As costing is an important mechanism to ensure that
nodes are not accidentally (or maliciously) overloaded, some solution would have
to be found to solve this problem before TFHE capabilities could be added to the
chain.

One possible solution would involve restricting script developers to a fixed set
of 'primitive' circuits whose costs are predictable, and then require all other
circuits to be implemented in terms of them. While this would resolve the
costing issue, it is not without its downsides. One large downside is that the
amount of work to implement TFHE support would magnify, as this would now
require much more than a single builtin, while limiting the possibilities
available to developers. Worse still, this 'solution' directly attacks one of
the biggest benefits of TFHE and programmable bootstrapping, namely the ability
to 'hide' the computation you want to perform on the data. Thus, this solution
appears unviable.

As mentioned previously, this concern arises regardless of what approach we
choose. Even if the Cardano nodes would not perform TFHE computations
themselves, we must still somehow assess a cost to sending the computation via
the Zama protocol (and awaiting the result), which runs into the same issue as
doing the computation 'ourselves'.

## Copyright

This CPS is licensed under [Apache-2.0](http://www.apache.org/licenses/LICENSE-2.0).

[fully-homomorphic-encryption]: https://en.wikipedia.org/wiki/Homomorphic_encryption
[tfhe]: https://tfhe.github.io/tfhe/ 
[zama]: https://www.zama.org/
[grumplestiltskin]: https://github.com/mlabs-haskell/grumplestiltskin/tree/milestone-2
[sha512-plutus]: https://github.com/IntersectMBO/plutus/blob/master/plutus-benchmark/bitwise/src/PlutusBenchmark/SHA512.hs
[ed25519-plutus]: https://github.com/IntersectMBO/plutus/blob/master/plutus-benchmark/bitwise/src/PlutusBenchmark/Ed25519.hs
[rust-binds]: https://github.com/cardano-scaling/haskell-accumulator
