---
CIP: ?
Title: Votes & Certificates on Cardano
Category: ?
Status:
Authors:
    - Pyrros Chaidos <pyrros.chaidos@iohk.io>
    - Raphaël Toledo <raphael.toledo@iohk.io>
    - Arnaud Bailly <arnaud.bailly@iohk.io>
Implementors:
    - Cardano Scaling team <https://github.com/cardano-scaling/alba>
Discussions: []
Created: 2024-08-01
License: CC-BY-4.0
---

## Abstract

This proposal specifies a cryptographic protocol for distributed and decentralised stake-based votes and compact certificates, based on the [Approximate Lower Bounds Arguments](https://iohk.io/en/research/library/papers/approximate-lower-bound-arguments/) research paper.

## Motivation: why is this CIP necessary?

Several existing or proposed extensions to Cardano protocol and network depend on a decentralised _stake-based_ voting and certificates production mechanism:

* [Mithril](https://mithril.network) is already in production and provides certificates using a centralised aggregator, but work is underway to decentralise signatures diffusion and aggregation,
* [Peras](https://peras.cardano-scaling.org) is an extension to Ouroboros Praos that depends on votes and certificates to provide _boosts_ to some blocks of the chain, in order to reach faster settlement certainty,
* [Leios](https://leios.cardano-scaling.org) is another proposed extension to Praos that depends on votes and certificates to _endorse_ blocks and increase overall throughput of the network.

In general, having a decentralised protocol in place to build some small proof that a large enough quorum of the network's stake-holders have "seen" some piece of information has a lot of potential use cases: checkpointing and snapshotting state come to mind, but any kind of knowledge that's shared by all SPOs could potentially be voted for and "proven" through a cryptographically secure certificate.

Those protocols shares a lot when it comes to the overall process they follow to build a _certificate_:

* SPOs can cast their vote independently on some known piece of information according to the amount of stake they represent,
* Votes are diffused across the network,
* Any party (the _prover_) can independently aggregate a large number of individual votes into a much smaller _certificate_,
* A certificate can be verified independently, guaranteeing the prover actually witnessed some quorum of votes.

## Specification

### General principles

TODO, see https://alba.cardano-scaling.org ?

### Votes

> [!WARNING]
>
> This should be rewritten and is copied verbatim from [Peras Tech report #2](https://peras.cardano-scaling.org/docs/reports/tech-report-2#votes--certificates)

#### Overview

Voting in Peras is mimicked after the _sortition_ algorithm used in Praos, e.g it is based on the use of a _Verifiable Random Function_ (VRF) by each stake-pool operator guaranteeing the following properties:

* The probability for each voter to cast their vote in a given round is correlated to their share of total stake,
* It should be computationally impossible to predict a given SPO's schedule without access to their secret key VRF key,
* Verification of a voter's right to vote in a round should be efficiently computable,
* A vote should be unique and non-malleable. (This is a requirement for the use of efficient certificates aggregation, see [below](#alba-certificates).)

Additionally we would like the following property to be provided by our voting scheme:

* Voting should require minimal additional configuration (i.e., key management) for SPOs,
* Voting and certificates construction should be fast in order to ensure we do not interfere with other operations happening in the node.

We have experimented with two different algorithms for voting, which we detail below.

#### Structure of votes

We have used an identical structure for single `Vote`s, for both algorithms. We define this structure as a CDDL grammar, inspired by the [block header](https://github.com/input-output-hk/cardano-ledger/blob/e2aaf98b5ff2f0983059dc6ea9b1378c2112101a/eras/conway/impl/cddl-files/conway.cddl#L27) definition from cardano-ledger:

```cddl
vote =
  [ voter_id         : hash32
  , voting_round     : round_no
  , block_hash       : hash32
  , voting_proof     : vrf_cert
  , voting_weight    : voting_weight
  , kes_period       : kes_period
  , kes_vkey         : kes_vkey
  , kes_signature    : kes_signature
  ]
```

This definition relies on the following primitive types (drawn from Ledger definitions in [crypto.cddl](https://github.com/input-output-hk/cardano-ledger/blob/e2aaf98b5ff2f0983059dc6ea9b1378c2112101a/eras/conway/impl/cddl-files/crypto.cddl#L1))

```cddl
round_no = uint .size 8
voting_weight = uint .size 8
vrf_cert = [bytes, bytes .size 80]
hash32 = bytes .size 32
kes_vkey = bytes .size 32
kes_signature = bytes .size 448
kes_period = uint .size 8
```

As already mentioned, `Vote` mimicks the block header's structure which allows Cardano nodes to reuse their existing VRF and KES keys. Some additional notes:

* Total vote size is **710 bytes** with the above definition,
* Unless explicitly mentioned, `hash` function exclusively uses 32-bytes Blake2b-256 hashes,
* The `voter_id` is it's pool identifier, ie. the hash of the node's cold key.

##### Casting vote

A vote is _cast_ by a node using the following process which paraphrases the [actual code](https://github.com/input-output-hk/peras-design/blob/4ab6fad30b1f8c9d83e5dfb2bd6f0fe235e1395c/peras-vote/src/Peras/Voting/Vote.hs#L293)

1. Define _nonce_ as the hash of the _epoch nonce_ concatenated to the `peras` string and the round number voted for encoded as 64-bits big endian value,
2. Generate a _VRF Certificate_ using the node's VRF key from this `nonce`,
3. Use the node's KES key with current KES period to sign the VRF certificate concatenated to the _block hash_ the node is voting for,
4. Compute _voting weight_ from the VRF certificate using _sortition_ algorithm (see details below).

##### Verifying vote

[Vote verification](https://github.com/input-output-hk/peras-design/blob/34196ee6e06ee6060c189116b04a2666450c5b75/peras-vote/src/Peras/Voting/Vote.hs#L392) requires access to the current epoch's _stake distribution_ and _stake pool registration_ information.

1. Lookup the `voter_id` in the stake distribution and registration map to retrieve their current stake and VRF verification key,
2. Compute the _nonce_ (see above),
3. Verify VRF certificate matches nonce and verification key,
4. Verify KES signature,
5. Verify provided KES verification key based on stake pool's registered cold verification key and KES period,
6. Verify provided _voting weight_ according to voting algorithm.

#### Leader-election like voting

The first algorithm is basically identical to the one used for [Mithril](https://mithril.network) signatures, and is also the one envisioned for [Leios](https://leios.cardano-scaling.org) (see Appendix D of the recent Leios paper). It is based on the following principles:

* The goal of the algorithm is to produce a number of votes targeting a certain threshold such that each voter receives a number of vote proportionate to $\sigma$, their fraction of total stake, according to the basic probability function $\phi(\sigma) = 1 - (1 - f)^\sigma$,
* There are various parameters to the algorithm:
    * $f$ is the fraction of slots that are "active" for voting
    * $m$ is the number of _lotteries_ each voter should try to get a vote for,
    * $k$ is the target total number of votes for each round (e.g., quorum) $k$ should be chosen such that $k = m \cdot \phi(0.5)$ to reach a majority quorum,
* When its turn to vote comes, each node run iterates over an index $i \in [1 \dots m]$, computes a hash from the _nonce_ and the index $i$, and compares this hash with $f(\sigma)$: if it is lower than or equal, then the node has one vote.
    * Note the computation $f(\sigma)$ is exactly identical to the one used for [leader election](https://github.com/intersectmbo/cardano-ledger/blob/f0d71456e5df5a05a29dc7c0ac9dd3d61819edc8/libs/cardano-protocol-tpraos/src/Cardano/Protocol/TPraos/BHeader.hs#L434).

We [prototyped](https://github.com/input-output-hk/peras-design/blob/73eabecd272c703f1e1ed0be7eeb437d937e1179/peras-vote/src/Peras/Voting/Vote.hs#L311) this approach in Haskell.

#### Sortition-like voting

The second algorithm is based on the _sortition_ process initially invented by [Algorand](https://web.archive.org/web/20170728124435id_/https://people.csail.mit.edu/nickolai/papers/gilad-algorand-eprint.pdf) and [implemented](https://github.com/algorand/sortition/blob/main/sortition.cpp) in their node. It is based on the same idea, namely that a node should have a number of votes proportional to their fraction of total stake, given a target "committee size" expressed as a fraction of total stake $p$. And it uses the fact the number of votes a single node should get based on these parameters follows a binomial distribution.

The process for voting is thus:

* Compute the individual probability of each "coin" to win a single vote $p$ as the ratio of expected committee size over total stake.
* Compute the binomial distribution $B(n,p)$ where $n$ is the node's stake.
* Compute a random number between 0 and 1 using _nonce_ as the denominator over maximum possible value (e.g., all bits set to 1) for the nonce as denominator.
* Use [bisection method](https://en.wikipedia.org/wiki/Bisection_method) to find the value corresponding to this probability in the CDF for the aforementioned distribution.

This yields a vote with some _weight_ attached to it "randomly" computed so that the overall sum of weights should be around expected committee size.

This method has also been [prototyped in Haskell](https://github.com/input-output-hk/peras-design/blob/73eabecd272c703f1e1ed0be7eeb437d937e1179/peras-vote/src/Peras/Voting/Vote.hs#L174).

#### Benchmarks

The `peras-vote` package provides some benchmarks comparing the two approaches, which gives us:

* Single Voting (Binomial): 139.5 μs
* Single Verification (binomial): 160.9 μs
* Single Voting (Taylor): 47.02 ms

:::note

The implementation takes some liberty with the necessary rigor suitable for cryptographic code, but the timings provided should be consistent with real-world production grade code. In particular, when using _nonce_ as a random value, we only use the low order 64 bits of the nonce, not the full 256 bits.

:::

### Certificates

#### Mithril certificates

Mithril certificates' construction is described in details in the [Mithril](https://iohk.io/en/research/library/papers/mithril-stake-based-threshold-multisignatures/) paper and is implemented in the [mithril network](https://github.com/input-output-hk/mithril). It's also described in the [Leios paper](https://iohk.io/en/research/library/papers/high-throughput-blockchain-consensus-under-realistic-network-assumptions/), in the appendix, as a potential voting scheme for Leios, and implicitly Peras.

Mithril certificates have the following features:

* They depend on BLS-curve signatures aggregation to produce a so-called _State based Threshold Multi-Signature_ that's easy to verify,
* Each node relies on a _random lottery_ as described in the [previous section](#leader-election-like-voting) to produce a vote weighted by their share of total stake,
* The use of BLS signatures implies nodes will need to generate and exchange specialized keys for the purpose of voting, something we know from [Mithril](https://mithril.network/doc/mithril/mithril-protocol/certificates) is somewhat tricky as it requires some form of consensus to guarantee all nodes have the exact same view of the key set.

#### ALBA

[Approximate Lower Bound Arguments](https://iohk.io/en/research/library/papers/approximate-lower-bound-arguments/) or _ALBAs_ in short, are a novel cryptographic algorithm based on a _telescope_ construction providing a fast way to build compact certificates out of a large number of _unique_ items. A lot more details are provided in the paper, on the [website](https://alba.cardano-scaling.org) and the [GitHub repository](https://github.com/cardano-scaling/alba) where implementation is being developed, we only provide here some key information relevant to the use of ALBAs in Peras.

##### Proving & verification time

ALBA's expected proving time is benchmarked in the following picture which shows mean execution time for generating a proof depending on: The _total_ number of votes, the actual number of votes ($s_p$), the honest ratio ($n_p$). Note that as proving time increases exponentially when $s_p \rightarrow total \cdot n_p$, we only show here the situation when $s_p = total$ and $s_p = total - total \cdot n_p / 2$ to ensure graph stays legible.
![ALBA Proving Time](/img/alba-proving.png)

The following diagram is an excerpt from the ALBA benchmarks highlighting verification. Note these numbers do not take into account the time for verifying individual votes. As one can observe directly from these graphs, verification time is independent from the number of items and only depends on the $n_p/n_f$ ratio.
![ALBA Verification Time](/img/alba-verifying.png)

In practice, as the number of votes is expected to be in the 1000-2000 range, and there is ample time in a round to guarantee those votes are properly delivered to all potential voting nodes (see below), we can safely assume proving time of about 5 ms, and verification time under a millisecond.

##### Certificate size

For a given set of parameters, namely fixed values for $\lambda_{sec}$, $\lambda_{rel}$, and $n_p/n_f$, the proof size is perfectly linear and only depends on the size of each vote.

Varying the security parameter and the honest votes ratio for a fixed set of 1000 votes of size 200 yields the following diagram, showing the critical factor in proof size increase is the $n_p/n_f$ ratio: As this ratio decreases, the number of votes to include in proof grows superlinearly.

![Proof size vs. λ and honest votes ratio](/img/alba-proof-size-lambda.svg)

#### Benchmarks

In the following tables we compare some relevant metrics between the two different kind of certificates we studied, Mithril certificates (using BLS signatures) and ALBA certificates (using KES signatures): Size of certificate in bytes, proving time (e.g., the time to construct a single vote), aggregation time (the time to build a certificate), and verification time.

For Mithril certificates, assuming parameters similar to mainnet's ($k=2422, m=20973, f=0.2$):

| Feature                         | Metric |
| ------------------------------- | ------ |
| Certificate size                | 56 kB  |
| Proving time (per vote)         | ~70 ms |
| Aggregation time                | 1.2 s  |
| Verification time (certificate) | 17 ms  |

For ALBA certificates, assuming 1000 votes, a honest to faulty ratio of 80/20, and security parameter $λ=128$. Note the proving time _does not_ take into account individual vote verification time, whereas certificate's verification time _includes_ votes verification time.

| Feature                         | Metric  |
| ------------------------------- | ------- |
| Certificate size                | 47 kB   |
| Proving time (per vote)         | ~133 us |
| Aggregation time                | ~5 ms   |
| Verification time (certificate) | 15 ms   |
|                                 |         |

## Rationale: how does this CIP achieve its goals?


> [!WARNING]
>
> Don't know what to put in there, we'll need several rounds of back and forth

The proposed scheme (votes structure and ALBAs) fills in all the requirements of a generic voting and certificate system that can be applied to any kind of data that's shared by all SPOs, or a sufficiently large fraction of them.

## Path to Active

### Acceptance Criteria

> [!WARNING]
>
> Not sure what to put here

ALBAs voting and certificate production is available to all block-producing nodes through an API.

### Implementation Plan
<!-- How I plan to meet the acceptance criteria -->

* Complete high-performance Rust library features & APIs
* Audit library for security
* Integrate library in cardano-node

## Acknowledgements

* [Approximate Lower Bound Arguments](https://doi.org/10.1007/978-3-031-58737-5_3),  _Pyrros Chaidos, Prof Aggelos Kiayias, Leonid Reyzin, Anatoliy Zinovyev_, May 2024, Eurocrypt'24

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
