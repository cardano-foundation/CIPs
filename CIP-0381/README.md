---
CIP: 0381
Title: Plutus support for Pairings over BLS12_381
Authors: Iñigo Querejeta-Azurmendi <inigo.querejeta@iohk.io>
Discussions-To: https://github.com/cardano-foundation/CIPs/pull/220
Comments-URI: https://github.com/cardano-foundation/CIPs/pull/220
Category: Plutus
Status: Proposed
Type: Standards Track
Created: 2022-02-11
License: Apache-2.0
---


## Abstract
This CIP proposes an extension of the current plutus functions to provide support for basic operations over BLS12_381 
curve to the plutus language. We expose a candidate implementation, and describe clearly the benefits that this 
would bring. In a nutshell, pairing friendly curves will enable a large number of cryptographic primitives that will 
be essential for the scalability of Cardano. 

## Motivation
Pairing Friendly Curves are a type of curves that provide the functionality of computing pairings. A pairing is a 
binary function that maps two points from two groups to a third element in a third target group. For a more in-depth 
introduction to pairings, we recommend reading [Pairings for Beginners](https://www.craigcostello.com.au/tutorials) or 
[Pairings for Cryptographers](https://eprint.iacr.org/2006/165). For level of detail required in this document, it is 
sufficient to understand that a pairing is a map: e:G1 X G2 -> GT, which satisfies the following properties:

* Bilinearity: for all a,b in F^*_q, for all P in G1, Q in G2: e(aP,bQ)=e(P,Q)^(ab)
* Non-degeneracy: e != 1
* Computability: There exists an efficient algorithm to compute e

where G1, G2 and GT are three distinct groups of order a prime q. Given that all three groups have the same
order, we can refer to the scalars of each group using the same type/structure.
Pairing computation is an expensive operation. However, they enable a range of interesting 
cryptographic primitives which can be used for scaling Cardano and many other use cases. We now
provide a list of use cases of pairings as well as an estimate operation count to understand the number of 
'expensive' operations that need to be computed for each of them (a preliminary benchmark can be found in 
Section 'Costing of function').

* **Sidechains** are a crucial component for the scalability of Cardano, and its interoperability with other 
chains/tokens/smart contracts. However, sidechains need to periodically commit their state to the Cardano mainnet to 
provide the same security guarantees as the latter. This periodical commitment is performed through a threshold 
signature by the dynamic committee of the Sidechain. The most interesting construction for medium sized committees 
is ATMS, presented in the paper [Proof of Stake Sidechains](https://cointhinktank.com/upload/Proof-of-Stake%20Sidechains.pdf), 
in section 5.2 and requires pairings. We have yet not found an efficient solution that does not require pairings.
ATMS is a k-of-t threshold signature scheme (meaning that we need at least k signers to participate). Let
n <= t - k be the number of signers that did not participate in the ATMS signature. ATMS verification proceeds
as follows:
  * Check that n <= t - k
  * n (log_2(t) hash computations + equality checks) (this is a very pessimistic upper bound. In practice, it's much less)
  * n G1 additions and 1 G1 negation
  * 2 miller loops + final verify
* **Zero Knowledge Proofs** are an incredibly powerful tool. There exist different types of zero knowledge proofs, 
but the most succinct (and cheaper to verify) rely on pairings for verification. Zero knowledge proofs can be used 
to make Mithril certificates, or sidechain checkpoints even more succinct, or to create layer 2 solutions to provide 
scalability (by the means of [ZK-Rollups](https://ethereum.org/en/developers/docs/scaling/layer-2-rollups/), which 
are used to scale Ethereum, e.g. [Loopring](https://loopring.org/#/), [zkSync](https://zksync.io/) or 
[Aztec](https://aztec.network/) among others). Plonk verification is quite complex, and differs depending on the 
number of custom gates. Implementations may differ, and adding custom gates or blinders will affect these estimates. 
Pairing evaluations would not be affected, but scalar multiplications and additions over G1 will increase linearly with
respect to the additional gates and blinders. In general, it is not expected that the number of custom gates surpasses
the dozens. In this section we expose the verifier complexity as described
[here](https://eprint.iacr.org/2019/953.pdf) (version last checked April 2022). We count every challenge computation
as a single hash evaluation. We omit the `scalar X scalar` multiplications and additions.We assume that point validation
is performed by the external C library, and therefore do not count that in this estimate. The computation is the following:
  * 6 hash computations
  * 1 vanishing polynomial (1 scalar exponentiation)
  * Quotient polynomial evaluation (1 scalar inverse)
  * First part of batch poly commitment (9 scalar mults and 9 additions in G1)
  * Fully batched poly commitment (5 scalar mults and 5 additions over G1)
  * Group encoded batch verification (1 scalar mult over G1)
  * Batch-validate all evaluations (3 scalar mults and 4 additions over G1, plus two miller loops + final verify)
* **Hydra** is another crucial component for scalability of Cardano (there is a series of blog posts available, with a 
good summary of the solution [here](https://iohk.io/en/blog/posts/2021/09/17/hydra-cardano-s-solution-for-ultimate-scalability/)). 
Hydra relies on a multisignature scheme, where all participants of the side channel need to agree on the new state. 
This can be achieved with non-pairing friendly curves (as it is currently designed), but pairing based signature schemes 
provide much more elegant constructions that reduce interaction among signers. Moreover, Hydra tails could benefit from
SNARKs for proving correct spending of a set of transactions. For costing multisignatures we use BLS, whose verification 
is relatively simple. One only needs to compute 2 miller loops and a final verify operation.Some applications might be 
interested in a smart contract aggregating signatures or keys. For this, we require n
group additions over G1 and G2 respectively, for n the number of submitted signatures.
* **Mithril** currently does not require plutus support. However, Mithril, as a technology, allows for signature generation
representing all stakeholders of Cardano (or any proof of stake system). These types of certificates might eventually 
be used for certifying sidechains, and plutus support will be crucial. Again, Mithril relies on pairing based signatures.
Let k be the number of submitted signatures (as above, k is a security parameter determining the number of
required signatures). However, in mithril k << N where N is the total number of eligible signers. Mithril
verification goes as follows:
  * Check the k is large enough
  * k G1 additions
  * k G2 additions
  * k (log_2(N) hash computations + equality checks)
  * 2 miller loops + final verify
* **ATALA** is a decentralized identification mechanism. One of the properties they want to provide is anonymity: users 
can selectively disclose attributes of their certificate or prove statements regarding them without disclosing their identity. 
Up to date, the most recent, efficient and interesting solutions to provide these are pairing based 
([Hyperledger Fabric/Idemix standardisation effort](https://hyperledger-fabric.readthedocs.io/en/release-2.2/idemix.html#underlying-cryptographic-protocols), 
[coconut credentials used by Nym](https://blog.nymtech.net/nyms-coconut-credentials-an-overview-4aa4e922cd51), among 
others). We use Coconut certs as an example. There is no decision on what type of construction we will
eventually use. Coconut credentials (and other types of credentials we are looking at) are built in a way that
it is efficient to prove statements about attributes. To this end, it is required to build, and be able to verify,
relations over discrete logarithm values. However, for sake of simplicity in this computation, we consider the
simplest form of anonymous credentials, which contains no attributes. We note that proving statements regarding
attributes does not require further pairing evaluations.
  * Proof verification to a relation involving elements in G1 and G2. This verification does not require the
    pairing evaluation, but does require G1 and G2 additions and multiplications.
  * 2 miller loops + final verify

## Specification
We now provide the technical specification. 

### Names and types/kinds for the new functions or types
The added types will be the following, all of which can be represented as a byte array. Even if these types are 
equivalent to byte arrays of a given size, it makes sense to include these types, to enforce deserialization, and 
therefore some checks on the data used by the smart contract. In particular, all three types can only be achieved 
with byte arrays that represent a point which is part of the prime order subgroup. 

* `BLS12_381G1Element`
* `BLS12_381G2Element`
* `BLS12_381GTElement`

We need to support the binary operation of G1 and G2 (which are additive groups), as well as the binary operation 
over GT (which is represented as a multiplicative group). We also want to enable hashing to G1 and G2.
In particular, we expose the hash to curve (which we denote with `H2G1` and `H2G2` for G1 and G2 
respectively) algorithm as described in 
[hash to curve draft](https://datatracker.ietf.org/doc/html/draft-irtf-cfrg-hash-to-curve#section-8), 
using `BLS12381G1_XMD:SHA-256_SSWU_RO_` and `BLS12381G2_XMD:SHA-256_SSWU_RO_` for G1 and G2 respectively.
We do not include the type of the Scalar, nor operations related to it. These type of operations can already be 
performed with the Integral type. In particular, we need the following functions: 

* Group operations: 
    * `BLS12_381_G1_add :: BLS12_381G1Element -> BLS12_381G1Element -> BLS12_381G1Element`
    * `BLS12_381_G1_mult :: Integer -> BLS12_381G1Element -> BLS12_381G1Element`
    * `BLS12_381_G1_neg :: BLS12_381G1Element -> BLS12_381G1Element`
    * `BLS12_381_H2G1 :: ByteString -> BLS12_381G1Element`
    * `BLS12_381_G2_add :: BLS12_381G2Element -> BLS12_381G2Element -> BLS12_381G2Element`
    * `BLS12_381_G2_mult :: Integer -> BLS12_381G2Element -> BLS12_381G2Element`
    * `BLS12_381_G2_neg :: BLS12_381G2Element -> BLS12_381G2Element`
    * `BLS12_381_H2G2 :: ByteString -> BLS12_381G2Element`
    * `BLS12_381_GT_mul :: Blst12381GTElement -> Blst12381GTElement -> Blst12381GTElement`
* Pairing operations:
    * `BLS12_381_ppairing_ml :: BLS12_381G1Element -> BLS12_381G2Element -> BLS12_381GTElement`
    * `BLS12_381_final_verify :: BLS12_381GTElement -> BLS12_381GTElement -> bool` This performs the final 
  exponentiation (see section `An important note on GT elements` below).

On top of the elliptic curve operations, we also need to include deserialization functions, and equality definitions
among the G1 and G2 types. 

* Deserialisation: 
  * `serialiseG1 :: Bls12_381G1Element -> ByteString`
  * `deserialiseG1 :: ByteString -> Bls12_381G1Element`
  * `serialiseG2 :: Bls12_381G2Element -> ByteString`
  * `deserialiseG2 :: ByteString -> Bls12_381G2Element`
  * `deserialiseGT :: ByteString -> Bls12_381GTElement`
* Equality functions:
  * `eq :: BLS12_381G1Element -> BLS12_381G1Element -> bool`
  * `eq :: BLS12_381G2Element -> BLS12_381G2Element -> bool`

This makes a total of 18 new functions and three new types. 

We follow the [ZCash Bls12-381 specification](https://github.com/supranational/blst#serialization-format) for the
serialization of elements:
* Fq elements are encoded in big-endian form. They occupy 48 bytes in this form.
* Fq2 elements are encoded in big-endian form, meaning that the Fq2 element c0 + c1 * u is represented by the Fq
  element c1 followed by the Fq element c0. This means Fq2 elements occupy 96 bytes in this form.
* The group G1 uses Fq elements for coordinates. The group G2 uses Fq2 elements for coordinates.
* G1 and G2 elements are encoded in compressed form (just the x-coordinate). G1 elements occupy 48 bytes and
  G2 elements occupy 96 bytes.

The most-significant three bits of a G1 or G2 encoding should be masked away before the coordinate(s) are
interpreted. These bits are used to unambiguously represent the underlying element:
* The most significant bit, when set, indicates that the point is in compressed form.
* The second-most significant bit indicates that the point is at infinity. If this bit is set, the remaining bits of
  the group element's encoding should be set to zero.
* The third-most significant bit is set if (and only if) this point is in compressed form, and it is not the point at
  infinity and its y-coordinate is the lexicographically largest of the two associated with the encoded x-coordinate.

We include the serialisation of the generator of G1 and the generator of G2:
* generator G1:
```
[151, 241, 211, 167, 49, 151, 215, 148, 38, 149, 99, 140, 79, 169, 172, 15, 195, 104, 140, 79, 151, 116, 185, 
5, 161,78, 58, 63, 23, 27, 172, 88, 108, 85, 232, 63, 249, 122, 26, 239, 251, 58, 240, 10, 219, 34, 198, 187]
```
* generator G2:
```
[147, 224, 43, 96, 82, 113, 159, 96, 125, 172, 211, 160, 136, 39, 79, 101, 89, 107, 208, 208, 153, 32, 182, 
26, 181, 218, 97, 187, 220, 127, 80, 73, 51, 76, 241, 18, 19, 148, 93, 87, 229, 172, 125, 5, 93, 4, 43, 126, 
2, 74, 162, 178, 240, 143, 10, 145, 38, 8, 5, 39, 45, 197, 16, 81, 198, 228, 122, 212, 250, 64, 59, 2, 180, 
81, 11, 100, 122, 227, 209, 119, 11, 172, 3, 38, 168, 5, 187, 239, 212, 128, 86, 200, 193, 33, 189, 184]
```

#### An important note on GT elements
We intentionally limit what can be done with the GT element. In fact, the only way that one can generate a 
GT element is using the `BLS12_381_ppairing_ml` function. Then these elements can only be used for operations among 
them (mult) and a final equality check (denote `final_verify`). In other words, GT elements are only there to eventually
perform some equality checks. We thought of including the inverse
function to allow division, but given that we simply allow for equality checks, if one needs to divide by `A`, 
then `A` can simply move to the other side of the equality sign. These limitations allow us for a performance 
trick, which is also used for the verification of BLS signatures. In a nutshell, a pairing is divided into two 
operations: (i) Miller loop, and (ii) final exponentiation. Both are expensive, but what we can do is first 
compute the miller loop, which already maps two points from G1 and G2 to GT. Then we can use this result 
to perform the operations over these points (mults). Finally, when we want to check for equality, we invert 
one of the two points (or equivalently in this case we compute the conjugate), and multiply the result by the 
other point. Only now we compute the final exponentiation
and verify that the result is the identity element. In other words: 
* the 'partial pairing' function, `BLS12_381_ppairing_ml` (stands for partial pairing miller loop) simply
computes the miller loop
* the equality check function, `final_verify`, first
computes an inverse, then a multiplication, a final exponentiation and checks that the element is the identity. 

Using the estimates exposed in the section `Costing of function`, we can see how this representation of
GT elements is beneficial. Assume that we want to check the following relation: 
`e(A,B) * e(C,D) =? e(E,F) * e(G,H)`. The miller look takes around 330us, and the final exponentiation
around 370us. A full pairing would be 700us, and therefore checking this relation would cost around
2,8ms. If, instead, we break down the pairing into a miller loop and a final exponentiation, and only
compute the latter once, the cost of the relation above would be 330 * 4 + 370 = 1,7ms. 
                                         
For this reason it is important to limit what can be done with GTElements, as the pairing really is not the full 
pairing operation, but only the miller loop. 
### Source implementation
* [BLST](https://github.com/supranational/blst) library, providing the algebraic operations.
* [cardano-base](https://github.com/input-output-hk/cardano-base/tree/bls12-381/cardano-crypto-class/src/Cardano/Crypto/EllipticCurve)
with the haskell FFI to the BLST library.

Other libraries of interest
* [Ethereum support for BLS12_381](https://eips.ethereum.org/EIPS/eip-2537). Not directly relevant as this is an 
Ethereum Improvement Proposal for a precompiled solidity contracts.

### Comparison with existing function
We present what would be the alternatives of using pairings in the different use cases presented above. 

* Sidechain bridges using the current technology would rely on either of the two possibilities: 
    * Require the bridge committee to interact during signature, or to rely on a precomputation phase. Current 
  solutions only support non-robust signature schemes, meaning that if one signer misbehaves, the whole signature 
  procedure needs to be restarted. This could seriously hinder sidechains.
    * Non-aggregation of signatures. This would result in a linear "checkpoint certificate" with respect to the 
    number of signers (both in communication and computation complexity). Basically, all committee members need to 
    submit their signature, and the smart contract needs to verify all ed25519 signatures. 
* Zero Knowledge Proofs cannot be verified with current functions available in Plutus. There exists proofs that can 
be instantiated over non-pairing friendly curves, but these result in logarithmic sized proofs and linear verification 
with respect to the computation to prove, while solutions that rely on pairings can be represented more concisely, and 
are cheaper to verify. 

### Reason for exposing curve operations API
One might be concerned of why we are exposing such low-level primitives, instead of exposing higher level protocol 
functions, such as `VerifyBlsSignature` or `VerifyZKP`. The motivation behind that is because pairings can enable a 
big number of use cases, and covering all of those can considerably extend the list of required functions. 

### Curve specifications
BLS12 curve is fully defined by the following set of parameters (coefficient A=0 for all BLS12 curves). Taken from 
[EIP 2537](https://eips.ethereum.org/EIPS/eip-2537):
```
Base field modulus = 0x1a0111ea397fe69a4b1ba7b6434bacd764774b84f38512bf6730d2a0f6b0f6241eabfffeb153ffffb9feffffffffaaab
B coefficient = 0x000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000004
Main subgroup order = 0x73eda753299d7d483339d80809a1d80553bda402fffe5bfeffffffff00000001
Extension tower
Fp2 construction:
Fp quadratic non-residue = 0x1a0111ea397fe69a4b1ba7b6434bacd764774b84f38512bf6730d2a0f6b0f6241eabfffeb153ffffb9feffffffffaaaa
Fp6/Fp12 construction:
Fp2 cubic non-residue c0 = 0x000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001
Fp2 cubic non-residue c1 = 0x000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001
Twist parameters:
Twist type: M
B coefficient for twist c0 = 0x000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000004
B coefficient for twist c1 = 0x000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000004
Generators:
G1:
X = 0x17f1d3a73197d7942695638c4fa9ac0fc3688c4f9774b905a14e3a3f171bac586c55e83ff97a1aeffb3af00adb22c6bb
Y = 0x08b3f481e3aaa0f1a09e30ed741d8ae4fcf5e095d5d00af600db18cb2c04b3edd03cc744a2888ae40caa232946c5e7e1
G2:
X c0 = 0x024aa2b2f08f0a91260805272dc51051c6e47ad4fa403b02b4510b647ae3d1770bac0326a805bbefd48056c8c121bdb8
X c1 = 0x13e02b6052719f607dacd3a088274f65596bd0d09920b61ab5da61bbdc7f5049334cf11213945d57e5ac7d055d042b7e
Y c0 = 0x0ce5d527727d6e118cc9cdc6da2e351aadfd9baa8cbdd3a76d429a695160d12c923ac9cc3baca289e193548608b82801
Y c1 = 0x0606c4a02ea734cc32acd2b02bc28b99cb3e287e85a763af267492ab572e99ab3f370d275cec1da1aaa9075ff05f79be
Pairing parameters:
|x| (miller loop scalar) = 0xd201000000010000
x is negative = true
```
One should note that base field modulus is equal to 3 mod 4 that allows an efficient square root extraction.

### Rationale
The reason for choosing BLS12_381 over BN256 curve is that the former is claimed to provide 128 bits of security,
while the latter was reduced to 100 bits of security after the extended number field sieve (a new algorithm to compute
the discrete logarithm) was [shown to reduce the security](https://eprint.iacr.org/2016/1102.pdf) of these curves.

An [EIP](https://eips.ethereum.org/EIPS/eip-2537) for precompiles of curve BLS12_381 already exists, but has been
stagnant for a while. Nonetheless, Zcash, MatterLabs and Consensys support BLS12_381 curve, so it is certainly widely
used in the space.

Further reading regarding curve BLS12_381 can be found [here](https://hackmd.io/@benjaminion/bls12-381) and the
references thereof cited. 
## Path to Proposed
To move this draft to proposed, we need to argue the trustworthiness of `blst` library, cost all functions and 
include these functions to Plutus. Furthermore, before proceeding to `Proposed`, we will provide a Haskell implementation 
of one of the algorithms that we want to do on-chain, implemented in terms of the primitives we are going to provide. 
This will help in benchmarking the viability of using these primitives on main-net. 

### Trustworthiness of implementations
* [BLST](https://github.com/supranational/blst) library—
[audited by NCC Group](https://research.nccgroup.com/wp-content/uploads/2021/01/NCC_Group_EthereumFoundation_ETHF002_Report_2021-01-20_v1.0.pdf) 
and [being formally verified](https://github.com/GaloisInc/BLST-Verification) by Galois
### Costing of function

We performed some benchmarks on the curve operations that can be used to cost each of the functions. We performed 
the benchmarks on a 2,7 GHz Quad-Core Intel Core i7, using the `blst` library. Further benchmarks are required
to provide final costings of functions.
Deserialization functions check that elements are part of the prime order subgroup. The pairing evaluation only
computes the miller loop, and the final verify of GTs computes an inversion in GT, a multiplication, a final 
exponentiation and a check wrt the identity element (more info in section An important note on GT elements).

* Group operations:
  * G1 addition: 806 ns
  * G1 multiplication:  20,5 us 
  * G1 negation: 12 ns
  * G1 Hash to group: 61,8 us
  * G2 addition: 1,6 us
  * G2 multiplication: 40,5 us
  * G2 negation: 18 ns
  * G2 Hash to group: 167,2 us
  * GT multiplication: 2 us
* Pairing operations:
  * Miller loop: 330,2 us
  * Final verify: 371.2 us
* Deserialization: 
  * G1: 63,8 us
  * G2: 77 us
* Equality checks:
  * G1: 228 ns
  * G2: 656 ns

### Plutus implementor
IOHK internal. We currently have implemented the FFI binding in 
[`cardano-base`](https://github.com/input-output-hk/cardano-base/pull/266).

### Haskell implementation of ATMS
We will provide a Haskell implementation of ATMS verification to understand the complexity of such a procedure.

## Path to Active
Release in upcoming update.
