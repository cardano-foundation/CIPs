---
CIP: 133
Title: Plutus support for Multi-Scalar Multiplication over BLS12-381
Status: Proposed
Category: Plutus
Authors:
    - Dmytro Kaidalov <dmytro.kaidalov@iohk.io>
    - Adam Smolarek <adam.smolarek@iohk.io>
    - Thomas Vellekoop <thomas.vellekoop@iohk.io>
Implementors:
    - IOG Plutus team
Discussions:
    - https://github.com/cardano-foundation/CIPs/pull/884
Created: 2024-08-22
License: CC-BY-4.0
---
## Abstract
The CIP proposes an extension of the current Plutus functions to provide support for the efficient computation of the multi-scalar multiplication over the BLS12-381 curve. This operation is crucial in a number of cryptographic protocols that can enhance the capabilities of the Cardano blockchain.

## Motivation: why is this CIP necessary?
Multi-scalar multiplication (MSM) is an algebraic group operation of the following form. Let $G$ be a group of prime order $p$. Let $g_0, g_1, ..., g_{N-1}$ be elements of $G$ and let $e_0, e_1, ..., e_{N-1}$ be elements of $Z_p$. Then, the multi-scalar multiplication $M$ is calculated as $M=\sum_{i=0}^{N-1} e_i \cdot g_i$.

This operation appears in many cryptographic protocols. Its naive implementation requires $N$ scalar multiplications and $N$ group additions. However, the performance can be significantly improved by employing advanced algorithms, such as the [Pippenger Approach](https://hackmd.io/@tazAymRSQCGXTUKkbh1BAg/Sk27liTW9). Moreover, it can be further optimized for a particular group type (e.g., for elliptic curve groups [[BH22](https://eprint.iacr.org/2022/1400.pdf), [L23](https://dspacemainprd01.lib.uwaterloo.ca/server/api/core/bitstreams/3b15ca4c-9125-4e45-9378-c5474eec6a07/content)]).

Multi-scalar multiplication appears in various cryptographic protocols, such as cryptographic signatures, zero-knowledge proofs, SNARK systems, and others. It is especially important in elliptic-curve-based SNARK proof systems, where large-scale MSMs can become a bottleneck in both proving and verification algorithms.

The recent Chang upgrade in Cardano included [CIP-0381](https://cips.cardano.org/cip/CIP-0381), which introduced built-in support for operations over the BLS12-381 elliptic curve (the implementation uses [blst](https://github.com/supranational/blst/tree/master) library). It made it feasible to implement various SNARK systems on-chain in Cardano. However, MSM still remains a bottleneck for many use cases. Implementing MSM naively, even using built-in functions for BLS12-381, consumes a significant portion of the computational budget of a transaction. It hinders implementation of such SNARK systems as KZG-based PLONK or Groth16, which require computations of MSM.

Our [benchmarks](https://github.com/input-output-hk/plutus-msm-bench) show that MSM of 10 $G1$ points over BLS12-381 curve consumes 7.74% of the computational budget of a transaction, while MSM of size more than 129 cannot fit into a single transaction at all. It impedes verification of complex circuits which might require much larger MSM.

We also did preliminary [benchmarks](https://github.com/dkaidalov/bench-blst-msm/) to compare an [optimized blst](https://github.com/supranational/blst/blob/e99f7db0db413e2efefcfd077a4e335766f39c27/src/multi_scalar.c) implementation of MSM with naive implementation using just blst group operations. We used Rust bindings to do these benchmarks (the underlying bindings are the same as used in [cardano-base for bslt](https://github.com/IntersectMBO/cardano-base/blob/master/cardano-crypto-class/src/Cardano/Crypto/EllipticCurve/BLS12_381/Internal.hs#L353), which means we can expect similar behavior for the Haskell stack). The results for G1 group are the following (more results in the [repository](https://github.com/dkaidalov/bench-blst-msm/)):

| MSM Size | MSM Optimized Average Time | MSM Naive Average Time | Ratio Naive/Optimized |
|---------:|---------------------------:|-----------------------:|----------------------:|
|       15 |                  728.565µs |                1.263ms |                  1.73 |
|       20 |                  816.508µs |                1.499ms |                  1.83 |
|       25 |                  956.735µs |                1.837ms |                  1.92 |
|       30 |                    1.022ms |                2.055ms |                  2.01 |
|       35 |                 428.765µs* |                2.715ms |                 6.13* |
|       40 |                   469.49µs |                2.882ms |                  6.33 |
|       45 |                  445.014µs |                3.288ms |                  7.37 |
|       50 |                  533.669µs |                3.933ms |                  7.38 |
|      100 |                   770.71µs |                7.307ms |                  9.48 |
|      200 |                    1.065ms |                14.07ms |                  13.2 |
|      300 |                    1.177ms |               21.605ms |                 18.34 |
|      400 |                    1.312ms |               27.405ms |                 20.87 |
|     1000 |                    2.584ms |               65.725ms |                 25.43 |
|     2000 |                    4.108ms |              131.453ms |                 31.99 |
|     3000 |                    5.510ms |              195.986ms |                 35.56 |
|     4000 |                     7.00ms |              263.722ms |                 37.67 |

\* _the sudden time improvement after 32 points is attributed to the inner workings of the blst library, which may operate differently for the MSM of size less than 32 (this should be carefully analyzed when establishing costing function for MSM built-in)._

As it can be seen the performance improvement rises quickly with the size of the MSM. Note that the current threshold for Plutus naive implementation is 129 points per transaction. Our [blst benchmarks](https://github.com/dkaidalov/bench-blst-msm/) show that naive MSM of size 129 takes approximately the same time as optimized MSM for more than 4000 points, which gives a hint to what improvements we can expect with a Plutus built-in for MSM. Moreover, these benchmarks do not account for the Plutus overhead to call many built-in BLS12 functions while implementing the naive MSM, so the final improvement may be even larger.
On the other hand, it is important to mention that if those points are brought into the script as input, their number would be constrained by the size of the script and by the computational complexity of points decompression. The benchmarks of points decompression in [CIP-0381](https://cips.cardano.org/cip/CIP-0381) shows that up to 300 G1 points can be passed as input to a 16kb script. However, in real cryptographic protocols typically only a part of the points involved in MSM is passed as input, while another part is computed during the execution (e.g., in PLONK-based SNARKs).

The availability of MSM built-in function in Plutus language will provide more efficient and reliable means to perform this important computation. Implementing an optimized MSM manually in Plutus deemed to be infeasible because of its complexity and because it operates at the level of basic curve operations.

A nonexclusive list of cryptographic protocols that would benefit from having MSM built-in for BLS12-381 curve:

1. The verification of pairing-based SNARKs over BLS12-381. For instance, the size of the MSM in Groth16 verifier depends on the number of public inputs. The size of the MSM in KZG-based PLONK verifier depends on the arithmetization structure.
2. Public key aggregation in [BLS multi-signature aggregation scheme](https://crypto.stanford.edu/~dabo/pubs/papers/BLSmultisig.html). It is a popular scheme that allows to aggregate many signatures into a common message, so that verifying the short multi-signature is fast.
3. A [cryptographic accumulator](https://github.com/perturbing/plutus-accumulator). It is a cryptographic primitive that allows a prover to succinctly commit to a set of values while being able to provide proofs of (non-)membership. Accumulators have found numerous applications including signature schemes, anonymous credentials, zero-knowledge proof systems, and others.

The above mentioned cryptographic protocols are used in many Cardano products, for instance:

- **Partner chains** - a crucial component for the scalability of Cardano. Its interoperability with Cardano relies on the ability to construct a secure bridge for message passing. A reliable trustless bridge requires SNARK proofs for efficient proving of the partner chain state.
- **Hydra** - a prominent layer-2 solution for scalability of Cardano. Hydra relies on a multisignature scheme, where all participants of the side channel need to agree on the new state. Moreover, Hydra tails could benefit from SNARKs for proving correct spending of a set of transactions.
- **Mithril** - a protocol for helping to scale the adoption of Cardano and its accessibility for users. It creates certified snapshots of the Cardano blockchain allowing to obtain a verified version of the current state without having to download and verify the full history of the blockchain. Mithril utilizes a stake-based threshold multisignature scheme based on elliptic curve pairings. Even though at the moment most use cases of Mithril relies on off-chain computations, eventually the Mithril certificates might also be verified in Plutus smart contracts.
- **Atala Prism** - a decentralized identification mechanism. One of the properties it can provide is anonymity: users can selectively disclose attributes of their certificate or prove statements without disclosing their identity. Up to date, the most efficient solutions for doing that use pairing-based zero-knowledge protocols.

In conclusion, integrating multi-scalar multiplication as a core built-in within Plutus is not only essential for enhancing cryptographic capabilities, but also for optimizing on-chain computations. The current approach of naive manual implementation in Plutus is inefficient for large-scale MSMs. Incorporating this function directly will streamline these operations, reduce transaction costs, and maintain the integrity of existing tools, thereby significantly advancing the Plutus ecosystem's functionality and user experience.

## Specification
The MSM for BLS12-381 is implemented in [blst](https://github.com/supranational/blst/blob/e99f7db0db413e2efefcfd077a4e335766f39c27/bindings/blst.h#L241) library, which is already a dependency for the [cardano-base](https://github.com/IntersectMBO/cardano-base/blob/master/cardano-crypto-class/src/Cardano/Crypto/EllipticCurve/). This library provides efficient and formally verified implementation of operations over the BLS12-381 elliptic curve. It has been used for implementing [CIP-0381](https://cips.cardano.org/cip/CIP-0381). Basically, we would like to expose several additional functions from this library in Plutus API.

### Function definition
We propose to define two new Plutus functions **bls12_381_G1_multiScalarMul** and **bls12_381_G2_multiScalarMul** as follows:

```hs
bls12_381_G1_multiScalarMul :: [Integer] -> [bls12_381_G1_element] -> bls12_381_G1_element
bls12_381_G2_multiScalarMul :: [Integer] -> [bls12_381_G2_element] -> bls12_381_G2_element
```

The types **bls12_381_G1_element** and **bls12_381_G2_element** are already introduced by [CIP-0381](https://cips.cardano.org/cip/CIP-0381). Given two arrays of scalars and group elements the functions compute multi-scalar multiplication for the corresponding subgroup. The arrays of scalars and group elements must be non-empty and of equal size. If the input arrays are empty or not equal, the functions must fail. These new functions naturally extend a set of operations over BLS12-381 defined by [CIP-0381](https://cips.cardano.org/cip/CIP-0381).

### Cost model
The computational impact of multi-scalar multiplication is complicated by it having dynamic-size arguments. Preliminary [benchmarks](https://github.com/dkaidalov/bench-blst-msm/) show that the computational complexity grows linearly with the size of the MSM. This should be reflected in the costing function.
It should also be taken into account that the efficiency of the MSM algorithm may vary [depending on the blst setup](https://github.com/supranational/blst/blob/master/src/multi_scalar.c#L61). 

There may be an extra complication in the costing procedure because all scalars have to be reduced modulo the order of the group before being passed to the blst functions (this happens [here](https://github.com/IntersectMBO/cardano-base/blob/6f9c20abdd3010e5a25356580cc968ba430101ad/cardano-crypto-class/src/Cardano/Crypto/EllipticCurve/BLS12_381/Internal.hs#L521) for the existing BLS12-381 scalar multiplication function in `cardano-crypto-class`). Presumably this is almost zero-cost for scalars already in the correct range, but if we pass in a very long list of very large scalars, the aggregated reduction time might be quite significant, and this must be taken into account in the costing function to guard against the possibility of a large amount of computation being done too cheaply.

## Rationale: how does this CIP achieve its goals?
Integrating these functions directly into Plutus will streamline cryptographic operations, reduce transaction costs, and uphold the integrity of existing cryptographic interfaces. It addresses current inefficiencies and enhances the cryptographic capabilities of the Plutus platform.

It will allow the implementation of complex cryptographic protocols on-chain in Plutus smart contracts, significantly expanding the capabilities of the Cardano blockchain.

## Path to Active

### Acceptance Criteria

We consider the following criteria to be essential for acceptance:

- [ ] The PR for this functionality is merged in the Plutus repository.
- [ ] This PR must include tests, demonstrating that it behaves as the specification requires in this CIP.
- [ ] A benchmarked use case is implemented in the Plutus repository, demonstrating that realistic use of this primitive does, in fact, provide major cost savings.

### Implementation Plan

- [x] IOG Plutus team consulted and accept the proposal.
- [x] Authors to provide preliminary benchmarks of naive MSM implementation in Plutus and blst MSM.
  - https://github.com/input-output-hk/plutus-msm-bench
  - https://github.com/dkaidalov/bench-blst-msm/

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).