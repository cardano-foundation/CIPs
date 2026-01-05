---
CIP: 0381
Title: Plutus support for Pairings over BLS12-381
Status: Active
Category: Plutus
Authors:
  - Iñigo Querejeta-Azurmendi <inigo.querejeta@iohk.io>
Implementors:
  - Kenneth MacKenzie <kenneth.mackenzie@iohk.io>
Discussions:
  - https://github.com/cardano-foundation/CIPs/pull/220
  - https://github.com/cardano-foundation/CIPs/pull/506
Created: 2022-02-11
License: Apache-2.0
---

## Abstract
This CIP proposes an extension of the current plutus functions to provide support for basic operations over BLS12-381 
curve to the plutus language. We expose a candidate implementation, and describe clearly the benefits that this 
would bring. In a nutshell, pairing friendly curves will enable a large number of cryptographic primitives that will 
be essential for the scalability of Cardano. 

## Motivation: why is this CIP necessary?
Pairing Friendly Curves are a type of curves that provide the functionality of computing pairings. A pairing is a 
binary function that maps two points from two groups to a third element in a third target group. For a more in-depth 
introduction to pairings, we recommend reading [Pairings for Beginners](https://www.craigcostello.com.au/tutorials) or 
[Pairings for Cryptographers](https://eprint.iacr.org/2006/165). For level of detail required in this document, it is 
sufficient to understand that a pairing is a map: e:G1 X G2 -> GT, which satisfies the following properties:

* Bilinearity: for all a,b in F^*_q, for all P in G1, Q in G2: e(aP,bQ)=e(P,Q)^(ab)
* Non-degeneracy: e != 1
* Computability: There exists an efficient algorithm to compute e

where G1, G2 and GT are three distinct groups of order a prime q.
Pairing computation is an expensive operation. However, they enable a range of interesting 
cryptographic primitives which can be used for scaling Cardano and many other use cases. We now
provide a list of use cases of pairings as well as an estimated operation count to understand the number of 
'expensive' operations that need to be computed for each of them (a preliminary benchmark can be found in 
Section 'Costing of function').

* **Sidechains** are a crucial component for the scalability of Cardano, and its interoperability with other 
chains/tokens/smart contracts. However, sidechains need to periodically commit their state to the Cardano mainnet to 
provide the same security guarantees as the latter. This periodical commitment is performed through a threshold 
signature by the dynamic committee of the Sidechain. The most interesting construction for medium sized committees 
is ATMS, presented in the paper [Proof of Stake Sidechains](https://cointhinktank.com/upload/Proof-of-Stake%20Sidechains.pdf), 
in Section 5.3, which requires pairings. We have yet not found an efficient solution that does not require pairings.
ATMS is a k-of-t threshold signature scheme (meaning that we need at least k signers to participate). 
* **Zero Knowledge Proofs** are an incredibly powerful tool. There exist different types of zero knowledge proofs, 
but the most succinct (and cheaper to verify) rely on pairings for verification. Zero knowledge proofs can be used 
to make Mithril certificates, or sidechain checkpoints even more succinct, or to create layer 2 solutions to provide 
scalability (by the means of [ZK-Rollups](https://ethereum.org/en/developers/docs/scaling/layer-2-rollups/), which 
are used to scale Ethereum, e.g. [Loopring](https://loopring.org/#/), [zkSync](https://zksync.io/) or 
[Aztec](https://aztec.network/) among others). Plonk verification is quite complex, and differs depending on the 
number of custom gates. Implementations may differ, and adding custom gates or blinders will affect these estimates. 
Pairing evaluations would not be affected, but scalar multiplications and additions over G1 will increase linearly with
respect to the additional gates and blinders. In general, it is not expected that the number of custom gates is larger
than a few dozens. In this section we expose the verifier complexity as described
[here](https://eprint.iacr.org/2019/953.pdf) (version last checked April 2022). We count every challenge computation
as a single hash evaluation. We omit the `scalar X scalar` multiplications and additions.We assume that point validation
is performed by the external C library, and therefore do not count that in this estimate. The computation is the following:
  * 6 hash computations
  * 1 vanishing polynomial (1 scalar exponentiation)
  * Quotient polynomial evaluation (1 scalar inverse)
  * First part of batch poly commitment (9 scalar mults and 9 additions in G1)
  * Fully batched poly commitment (5 scalar mults and 5 additions over G1)
  * Group encoded batch verification (1 scalar mult over G1)
  * Batch-validate all evaluations (3 scalar mults and 4 additions over G1, plus two Miller loops + final verify)
* **Hydra** is another crucial component for scalability of Cardano (there is a series of blog posts available, with a 
good summary of the solution [here](https://iohk.io/en/blog/posts/2021/09/17/hydra-cardano-s-solution-for-ultimate-scalability/)). 
Hydra relies on a multisignature scheme, where all participants of the side channel need to agree on the new state. 
This can be achieved with non-pairing friendly curves (as it is currently designed), but pairing based signature schemes 
provide much more elegant constructions that reduce interaction among signers. Moreover, Hydra tails could benefit from
SNARKs for proving correct spending of a set of transactions. For costing multisignatures we use BLS, whose verification 
is relatively simple. One only needs to compute 2 Miller loops and a final verify operation.Some applications might be 
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
  * 2 Miller loops + final verify
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
  * Proof verification reduces to a relation involving elements in G1 and G2. This verification does not require the
    pairing evaluation, but does require G1 and G2 additions and multiplications.
  * 2 Miller loops + final verify

## Specification
We now provide the technical specification. 

### Names and types/kinds for the new functions or types
The added types will be the following, all of which can be represented as a byte array. Even if these types are 
equivalent to byte arrays of a given size, it makes sense to include these types, to enforce deserialization, and 
therefore some checks on the data used by the smart contract. In particular, `bls12_381_G1_element` and
`bls12_381_G2_element` can only be generated 
with byte arrays that represent a point which is part of the prime order subgroup. On the other hand, 
`bls12_381_MlResult` can only be generated as a result of the `bls12_381_millerLoop` computatio.

* `bls12_381_G1_element`
* `bls12_381_G2_element`
* `bls12_381_MlResult`

We need to support the binary operation of G1 and G2 (which are additive groups), as well as the binary operation 
over MlResult (which is represented as a multiplicative group). We also want to enable hashing to G1 and G2.
In particular, we expose the hash to curve (which we denote with `hashToGroup`) algorithm as described in 
[hash to curve draft](https://datatracker.ietf.org/doc/html/draft-irtf-cfrg-hash-to-curve#section-8), 
using `BLS12381G1_XMD:SHA-256_SSWU_RO_` and `BLS12381G2_XMD:SHA-256_SSWU_RO_` for G1 and G2 respectively.
We do not include the type of the Scalar, nor operations related to it. These type of operations can already be 
performed with the `Integer` type. In particular, we need the following functions: 

* Group operations: 
    * `bls12_381_G1_add :: bls12_381_G1_element -> bls12_381_G1_element -> bls12_381_G1_element`
    * `bls12_381_G1_scalarMul :: Integer -> bls12_381_G1_element -> bls12_381_G1_element`
    * `bls12_381_G1_neg :: bls12_381_G1_element -> bls12_381_G1_element`
    * `bls12_381_G2_add :: bls12_381_G2_element -> bls12_381_G2_element -> bls12_381_G2_element`
    * `bls12_381_G2_scalarMul :: Integer -> bls12_381_G2_element -> bls12_381_G2_element`
    * `bls12_381_G2_neg :: bls12_381_G2_element -> bls12_381_G2_element`
    * `bls12_381_mulMlResult :: bls12_381_MlResult -> bls12_381_MlResult -> bls12_381_MlResult`
* Pairing operations:
    * `bls12_381_millerLoop :: bls12_381_G1_element -> bls12_381_G2_element -> bls12_381_MlResult`
    * `bls12_381_finalVerify :: bls12_381_MlResult -> bls12_381_MlResult -> Bool` This performs the final 
  exponentiation (see section `An important note on MlResult elements` below).
* Hash to curve. We include hash-to-curve functions, as per [Hashing to Elliptic Curves](https://datatracker.ietf.org/doc/html/draft-irtf-cfrg-hash-to-curve)
  internet draft. Refer to [this](#hash-to-curve) section for further details: 
  * `bls12_381_G1_hashToGroup :: ByteString -> ByteString -> bls12_381_G1_element`
  * `bls12_381_G2_hashToGroup :: ByteString -> ByteString -> bls12_381_G2_element`

On top of the elliptic curve operations, we also need to include deserialization functions, and equality definitions
among the G1 and G2 types. 

* Deserialisation (more information of the choice of compressed form over uncompressed form [here](#compressed-vs-decompressed)): 
  * `bls12_381_G1_compress :: bls12_381_G1_element -> ByteString`
  * `bls12_381_G1_uncompress :: ByteString -> bls12_381_G1_element`
  * `bls12_381_G2_compress :: bls12_381_G2_element -> ByteString`
  * `bls12_381_G2_uncompress :: ByteString -> bls12_381_G2_element`
* Equality functions:
  * `bls12_381_G1_equal :: bls12_381_G1_element -> bls12_381_G1_element -> Bool`
  * `bls12_381_G2_equal :: bls12_381_G2_element -> bls12_381_G2_element -> Bool`

This makes a total of 17 new functions and three new types. 

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

#### Hash to curve
We expose the hash-to-curve functions following the [Hashing to Elliptic Curves](https://datatracker.ietf.org/doc/html/draft-irtf-cfrg-hash-to-curve)
internet draft. The function signature takes as input two `ByteString`s and returns a point. The first 
`ByteString` is the message to be hashed, while the second `ByteString` is the Domain Separation Tag (DST). 
For more information on the DST, see [section 3.1](https://datatracker.ietf.org/doc/html/draft-irtf-cfrg-hash-to-curve#name-domain-separation-requireme)
of the internet draft. We limit the DST to be at most 255 bytes, following the standard specification. If 
applications require a domain separation tag that is longer than 255 bytes, they should convert it to a smaller
DST following the instructions of the standard draft (see [section 5.3.3](https://datatracker.ietf.org/doc/html/draft-irtf-cfrg-hash-to-curve#name-using-dsts-longer-than-255-)).

Some libraries expose the possibility to use yet another `ByteString` when calling the hash-to-curve function. 
See for example the [`blst` library](https://github.com/supranational/blst/blob/master/src/hash_to_field.c#L121).
We choose not to include this extra `ByteString` in the function signature, because it is not part of the standard
draft. In the case where we want to match a hash that did use this `aug` `ByteString`, one simply needs to prepend
that value to the message. One can verify that by running the test-vector generation script introduced in 
[cardano-base](https://github.com/input-output-hk/cardano-base/blob/master/cardano-crypto-tests/bls12-381-test-vectors/src/main.rs#L222..L231).

#### Compressed vs Decompressed
To recap, we have types `bls12_381_G1_element` and `bls12_381_G2_element` each of which is essentially a pair 
of values `(x,y)` that satisfy an equation of the form `y^2 = x^3+ax+b`.  The blst library provides two 
serialisation formats for these:

* The serialised format, where you have a bytestring encoding both the `x` and `y` coordinates of a point.  
  A serialised `bls12_381_G1_element` takes up 96 bytes and a serialised `bls12_381_G2_element` takes up 192 
  bytes.
* The compressed format, where you have a bytestring that only contains the `x` coordinate.  When you 
  uncompress a compressed point to get an in-memory point, the `y` coordinate has to be calculated from 
  the equation of the curve.  A compressed `bls12_381_G1_element` takes up 48 bytes and a compressed 
  `bls12_381_G2_element` takes 92 bytes.

The PLC implementation currently uses the compressed format for serialising `bls12_381_G1_element` and 
`bls12_381_G1_element`s.  There are at least three places where this is (or could be) used:

* Storing a group element as a bytestring inside a Data object which will be passed as a parameter to a script.
* During flat serialisation of PLC scripts (constants from G1 and G2 are converted into bytestrings and then 
  flat deals with these as usual).
* In the concrete PLC/UPLC syntax, where constants are written as hex strings representing compressed points.

The serialised format could also be used for all of these.  The advantage of doing that is that deserialisation 
is much cheaper than uncompression (which involves calculating a square root in a finite field, which is 
expensive in general), but the disadvantage is that the serialised format requires twice as much space as 
the compressed form.  We ran some benchmarks to determine CPU costs (in ExUnits) for both 
deserialisation, and uncompression and came up with the following:
```
bls12_381_G1_deserialize : 701442
bls12_381_G1_uncompress  : 16511372

bls12_381_G2_deserialize : 1095773
bls12_381_G2_uncompress  : 33114723
```

For G1 uncompression is about 23 times more expensive than deserialisation, and for G2 uncompression is about 
30 times more expensive than deserialisation.  The maximum CPU budget per script is currently 1,000,000,000, 
so a single G2 uncompression is about 0.3% of the total allowance, whereas a G2 deserialisation is about 0.01%.
This might seem like a compelling reason to prefer serialisation over compression, but our claim is that the time 
saving is not worthwhile because you can't fit enough serialised points into a script to make the speed gain 
significant. The bls12-381-costs program runs a number of benchmarks for execution costs of scripts that exercise 
the BLS builtins. One of these creates UPLC scripts which include varying numbers of compressed points and 
at run-time uncompresses them and adds them all together; bls-381-costs runs these scripts and prints out their 
costs as fractions of the maximum CPU budget and maximum script size (currently 16384). Here are the results:

Uncompress n G1 points and add the results
```
  n     script size             CPU usage               Memory usage
----------------------------------------------------------------------
  -      68   (0.4%)             100   (0.0%)             100   (0.0%) 
 10     618   (3.8%)       185801250   (1.9%)           45642   (0.3%)
 20    1168   (7.1%)       371912820   (3.7%)           88002   (0.6%)
 30    1718  (10.5%)       558024390   (5.6%)          130362   (0.9%)
 40    2268  (13.8%)       744135960   (7.4%)          172722   (1.2%)
 50    2818  (17.2%)       930247530   (9.3%)          215082   (1.5%)
 60    3368  (20.6%)      1116359100  (11.2%)          257442   (1.8%)
 70    3918  (23.9%)      1302470670  (13.0%)          299802   (2.1%)
 80    4468  (27.3%)      1488582240  (14.9%)          342162   (2.4%)
 90    5018  (30.6%)      1674693810  (16.7%)          384522   (2.7%)
100    5568  (34.0%)      1860805380  (18.6%)          426882   (3.0%)
110    6118  (37.3%)      2046916950  (20.5%)          469242   (3.4%)
120    6668  (40.7%)      2233028520  (22.3%)          511602   (3.7%)
130    7218  (44.1%)      2419140090  (24.2%)          553962   (4.0%)
140    7768  (47.4%)      2605251660  (26.1%)          596322   (4.3%)
150    8318  (50.8%)      2791363230  (27.9%)          638682   (4.6%)
```

Uncompress n G2 points and add the results
```
  n     script size             CPU usage               Memory usage
----------------------------------------------------------------------
  -      68   (0.4%)             100   (0.0%)             100   (0.0%) 
 10    1098   (6.7%)       363545910   (3.6%)           45984   (0.3%)
 20    2128  (13.0%)       728715130   (7.3%)           88704   (0.6%)
 30    3158  (19.3%)      1093884350  (10.9%)          131424   (0.9%)
 40    4188  (25.6%)      1459053570  (14.6%)          174144   (1.2%)
 50    5218  (31.8%)      1824222790  (18.2%)          216864   (1.5%)
 60    6248  (38.1%)      2189392010  (21.9%)          259584   (1.9%)
 70    7278  (44.4%)      2554561230  (25.5%)          302304   (2.2%)
 80    8308  (50.7%)      2919730450  (29.2%)          345024   (2.5%)
 90    9338  (57.0%)      3284899670  (32.8%)          387744   (2.8%)
100   10368  (63.3%)      3650068890  (36.5%)          430464   (3.1%)
110   11398  (69.6%)      4015238110  (40.2%)          473184   (3.4%)
120   12428  (75.9%)      4380407330  (43.8%)          515904   (3.7%)
130   13458  (82.1%)      4745576550  (47.5%)          558624   (4.0%)
140   14488  (88.4%)      5110745770  (51.1%)          601344   (4.3%)
150   15518  (94.7%)      5475914990  (54.8%)          644064   (4.6%)
```

It's clear from these figures that the limiting factor is the script size: about 300 G1 points or 150 G2 points
can be processed in a single script before exceeding the script size limit, but the maximum CPU usage is only 55% 
of the the maximum CPU budget. If the serialisation (involving both x- and y-coordinates) was used instead then 
there would be some saving in execution time, but a single script would only be able to process about half as 
many points and it's unlikely that the time savings would compensate for that. For example, uncompressing 50 G2 
points would cost about 1,655,000,000 CPU ExUnits and deserialising them would cost about 54,788,000, which is 
1,600,000,000 ExUnits cheaper. At the time of writing, this equates to 0.27 Ada. However, 50 serialised G2 
points take up 4800 more bytes than 50 compressed ones, and the extra bytes would cost 0.36 Ada. Thuis using 
serialisation would cost 0.09 Ada more than using compression for the same number of points.

In summary: even though uncompression is a lot more expensive per point than deserialisation, the size savings 
due to compression actually outweigh the speed gains due to serialisation because bytes per script are a lot 
more expensive than ExUnits per script in real terms. For this reason, we propose to support the compressed 
format and only the compressed format.

#### An important note on MlResult elements
We intentionally limit what can be done with the MlResult element. In fact, the only way that one can generate a
MlResult element is using the `bls12_381_millerLoop` function. Then these elements can only be used for operations among 
them (multiplication) and a final equality check (denoted `finalVerify`). In other words, MlResult elements are only there to eventually
perform some equality checks. We thought of including the inverse
function to allow division, but given that we simply allow for equality checks, if one needs to divide by `A`, 
then `A` can simply move to the other side of the equality sign. These limitations allow us for a performance 
trick, which is also used for the verification of BLS signatures. In a nutshell, a pairing is divided into two 
operations: (i) Miller loop, and (ii) final exponentiation. Both are expensive, but what we can do is first 
compute the Miller loop, which already maps two points from G1 and G2 to MlResult. Then we can use this result 
to perform the operations over these points (multiplications). Finally, when we want to check for equality, we invert 
one of the two points (or equivalently in this case we compute the conjugate), and multiply the result by the 
other point. Only now we compute the final exponentiation
and verify that the result is the identity element. In other words: 
* the 'partial pairing' function, `bls12_381_millerLoop` simply
computes the Miller loop
* the equality check function, `bls12_381_finalVerify`, first
computes an inverse, then a multiplication, a final exponentiation and checks that the element is the identity. 

While the results of the Miller loop are already elements in Fp12, they are not necessarily part of the group. This
is why we call the type used in the built-ins `bls12_381_MlResult` rather than `bls12_381_GT`.

Using the estimates in the section `Costing of functions`, we can see how this representation of
GT elements is beneficial. Assume that we want to check the following relation: 
`e(A,B) * e(C,D) =? e(E,F) * e(G,H)`. The Miller loop takes around 330us, and the final exponentiation
around 370us. A full pairing would be 700us, and therefore checking this relation would cost around
2,8ms. If, instead, we break down the pairing into a Miller loop and a final exponentiation, and only
compute the latter once, the cost of the relation above would be 330 * 4 + 370 = 1.7ms. 

For this reason it is important to limit what can be done with `bls12_381_MlResult`, as the pairing really is not the full
pairing operation, but only the Miller loop. 
### Source implementation
* [BLST](https://github.com/supranational/blst) library, providing the algebraic operations.
* [cardano-base](https://github.com/input-output-hk/cardano-base/tree/master/cardano-crypto-class/src/Cardano/Crypto/EllipticCurve)
with the haskell FFI to the BLST library.
* [plutus](https://github.com/input-output-hk/plutus/pull/5231)

Other libraries of interest
* [Ethereum support for BLS12-381](https://eips.ethereum.org/EIPS/eip-2537). Not directly relevant as this is an 
Ethereum Improvement Proposal for a precompiled solidity contracts.

### Comparison with existing functions
We present what would be the alternatives of using pairings in the different use cases presented above. 

* Sidechain bridges using the current technology would rely on either of the two possibilities: 
    * Require the bridge committee to interact during signature, or to rely on a precomputation phase. Current 
  solutions only support non-robust signature schemes, meaning that if one signer misbehaves, the whole signature 
  procedure needs to be restarted. This could seriously hinder sidechains.
    * Non-aggregation of signatures. This would result in a linear "checkpoint certificate" with respect to the 
    number of signers (both in communication and computation complexity). Basically, all committee members need to 
    submit their signature, and the smart contract needs to verify all ed25519 signatures. 
* Zero Knowledge Proofs cannot be verified with current functions available in Plutus. There exist proofs that can 
be instantiated over non-pairing friendly curves, but these result in logarithmic sized proofs and linear verification 
with respect to the computation to prove, while solutions that rely on pairings can be represented more concisely, and 
are cheaper to verify. 

### Reason for exposing curve operations API
One might be concerned of why we are exposing such low-level primitives, instead of exposing higher level protocol 
functions, such as `VerifyBlsSignature` or `VerifyZKP`. The motivation behind that is because pairings can enable a 
big number of use cases, and covering all of those can considerably extend the list of required functions. 

### Curve specifications
The BLS12-381 curve is fully defined by the following set of parameters (coefficient A=0 for all BLS12 curves). Taken from 
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
|x| (Miller loop scalar) = 0xd201000000010000
x is negative = true
```
One should note that base field modulus is equal to 3 mod 4 that allows an efficient square root extraction.

## Rationale: how does this CIP achieve its goals?
The reason for choosing the BLS12-381 over the BN256 curve is that the former is claimed to provide 128 bits of security,
while the latter was reduced to 100 bits of security after the extended number field sieve (a new algorithm to compute
the discrete logarithm) was [shown to reduce the security](https://eprint.iacr.org/2016/1102.pdf) of these curves.

An [EIP](https://eips.ethereum.org/EIPS/eip-2537) for precompiles of curve BLS12-381 already exists, but has been
stagnant for a while. Nonetheless, Zcash, MatterLabs and Consensys support BLS12-381 curve, so it is certainly widely
used in the space.

Further reading regarding curve BLS12-381 can be found [here](https://hackmd.io/@benjaminion/bls12-381) and the
references thereof cited. 

### Trustworthiness of implementations
* [BLST](https://github.com/supranational/blst) library—
[audited by NCC Group](https://research.nccgroup.com/wp-content/uploads/2021/01/NCC_Group_EthereumFoundation_ETHF002_Report_2021-01-20_v1.0.pdf) 
and [being formally verified](https://github.com/GaloisInc/BLST-Verification) by Galois.

We also have an [analysis by Duncan Coutts](https://github.com/cardano-foundation/CIPs/pull/220#issuecomment-1508306896https://github.com/cardano-foundation/CIPs/pull/220#issuecomment-1508306896)
for effects of including this library for continuous integration and long term maintainability:

In addition to security audits on the proposed implementation, it is important that we review the inclusion of 
the library for practical issues of build systems, and long term maintainability.

In particular in this case the library will be used in the chain format and in chain verification. This means 
we have special constraints that the format and verification logic must never change. Or more specifically: 
it must be possible forever to be able to verify the existing uses on the chain. So even if there are upgrades 
or format changes in future, it must still be possible to decode and verify the old uses. This is not a 
constraint that most software has, and so many libraries are not designed to work within that constraint.

The proposed implementation is https://github.com/supranational/blst

* The implementation is in C and assembly for x86 and ARM v8. This is good for the existing Haskell 
  implementation of the Cardano node because integrating with C libraries is relatively straightforward, it's 
  well supported by the build and CI system and does not pull in too many extra dependencies. (Contrast for 
  example if it were a Rust library where we would have serious practical problems on this front.)
* The implementation appears to have been designed with blockchain implementations in mind. This is a good 
  sign for the long term maintainability because it probably means that the library authors will continue to 
  support the existing format and semantics even if there are changes or improvements.
* The implementation is claimed to be compliant with draft IETF specifications. There is a risk that the 
  specs may change before being declared final, and the library may be updated to follow. There is a risk 
  that the Cardano community will have to support the old version forever. Though given the point above, 
  it's probably the case that library updates would still provide compatibility with the current IETF drafts 
  and serialisation formats.

So overall this seems like something the core development team and Cardano community could support long term 
without too high a cost. Though we should be aware of the risk that we may have to support an old version of 
the library, if the library gets changed in incompatible ways.

To ensure no compatibility surprises, it is worth considering forking the repository at a specific commit/version 
and building the node using that version. This is to guarantee the version remains available. Then for any future 
updates, the fork repo could be updated to a new version explicitly, with appropriate compatibility checks to 
ensure the existing on-chain uses are still compatible.
### Costing of function

We did some [preliminary costing](https://github.com/input-output-hk/plutus/tree/kwxm/BLS12_381/prototype/plutus-benchmark/bls-benchmarks) 
of the BLS functions and the following cost of the new built-in functions: 
```
bls12_381_G1_compress    : 3341914
bls12_381_G1_uncompress  : 16511372
bls12_381_G1_add         : 1046420
bls12_381_G1_equal       : 545063
bls12_381_G1_hashToCurve : 66311195 + 23097*x
bls12_381_G1_scalarMul   : 94607019 + 87060*x (we use 94955259, with x = 4)
bls12_381_G1_neg         : 292890
bls12_381_G2_compress    : 3948421
bls12_381_G2_uncompress  : 33114723
bls12_381_G2_add         : 2359410
bls12_381_G2_equal       : 1102635
bls12_381_G2_hashToCurve : 204557793 + 23271*x
bls12_381_G2_scalarMul   : 190191402 + 85902*x
bls12_381_G2_neg         : 307813
bls12_381_GT_finalVerify : 388656972
bls12_381_GT_millerLoop  : 402099373
bls12_381_GT_mul         : 2533975
blake2b_256                     : 358499 + 10186*x (521475, with x = 16)
addInteger                      : 85664 + 712*max(x,y) (88512, with x = y = 4)
multiplyInteger                 : 1000 + 55553*(x+y) (641924, with x = y = 4, and we include the price of modular reduction, as we need one per mult)
divideInteger                   : if x>y
then  809015 + 577*x*y
else  196500
modInteger                      : 196500  
expInteger                      : We estimate 32 mults and adds (23373952)
```

Using these preliminary benchmarks, we performed some estimates of how much it would cost to verify Groth16 or Plonk 
proofs using the bindings. Details can be found [here](https://hackmd.io/X80zXoxWQrqSLaO0nizjaA). The estimates for
Groth16 (~23% of the execution budget required for a proof verification) were confirmed by the benchmarks shared above.

### Plutus implementor
IOG internal. PR open for Plutus bindings https://github.com/input-output-hk/plutus/pull/5231

## Path to Active

### Acceptance Criteria

- [x] Confirmation from IOG Plutus Team that this curve support is included in a scheduled Plutus release.
  - Included within the Chang #1 hardfork 

### Implementation Plan

- [x] Confirmation from IOG Plutus Team that [CIP-0035 Processes](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0035#processes) for changes to Plutus have been satisfied.

## Copyright

This CIP is licensed under [Apache-2.0](https://www.apache.org/licenses/LICENSE-2.0).
