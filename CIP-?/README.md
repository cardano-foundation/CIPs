---
CIP: ?
Title: Efficient scalars for BLS12-381
Status: Proposed
Category: Plutus
Authors:
    - Ilia Rodionov <hey@euony.me>
Implementors: []
Discussions:
    - https://github.com/cardano-foundation/CIPs/pull/1087
Created: 2025-09-11
License: CC-BY-4.0
---

## Abstract

The Chang upgrade in Cardano brought support for the BLS12-381 elliptic curve introduced
in [CIP-381](https://cips.cardano.org/cip/CIP-0381).
In accordance with the priority of keeping the number of primitives in Plutus Core as low as possible, 
only new types and operations for elements of $G1$ and $G2$ groups were introduced, 
as well as slightly restricted type `bls12_381_MlResult` for the target group $G_T$. 
Neither the elements of the _base field_ $F_p$ nor _scalar field_ $F_r$ 
got dedicated treatment on the grounds of the fact that all modular operations 
can be naively performed with the existing `Integer` and its regular arithmetic.
While this approach seems sensible (and arguably even should be preserved), it has several drawbacks.
Firstly, Plutus loses the ability to use more efficient modular arithmetic
over finite fields, which is exactly the reason why they are so popular in
cryptography.
Secondly, this complicates the implementation and cost model for some functions 
that expect an element of $T_r$ represented as an `Integer` 
(please refer to the "Cost model" section in CIP-133 for details).

An important step towards the optimization of common operations over BLS12-381 is done by 
[CIP-133](https://cips.cardano.org/cip/CIP-0133), which proposes 
the effective way to do _multi-scalar multiplication_ (MSM).
Scalar multiplication was the main bottleneck for many protocols 
since operations in $G_1$ and $G_2$ are relatively expensive.
But now, when we have more exunits freed by quick MSM, 
the relative share of resources spent on operations over the scalars 
might become even bigger.

In practice, some cryptographic protocols need to perform quite extensive arithmetic
over the _scalar field_ $F_r$, particularly when working with _polynomials in KZG commitments_.
This CIP presents a motivational example, discusses related benchmarks,
and considers different ways of evolving Plutus 
toward efficient implementation of scalars for BLS12-381 curve.

## Motivation: why is this CIP necessary?

### Example use case: multiplying binomials

As an example, let's consider _pairing-based cryptographic accumulators_ 
[[SKBP22]](https://dl.acm.org/doi/pdf/10.1145/3548606.3560676).
To verify a usually off-chain-calculated membership proof, 
the validator needs to calculate
$N+1$ coefficients $c_i$ for a _final polynomial_ $P(x)$ 
by multiplying given $N$ _normalized binomials_ $B_i$:

$$
\begin{align}
B_i(x) = x + a_i \qquad (i=1,\dots,n) \\
P(x) = \prod_{i=1}^N B_i(x) = \sum_{i=0}^{N} c_i \cdot x^i
\end{align}
$$

The straightforward way to solve this problem is the _schoolbook convolution_, 
which comes with $O(n^2)$ complexity.
This is what both
[Haskell](https://github.com/perturbing/plutus-accumulator/blob/main/plutus-accumulator/src/Plutus/Crypto/BlsUtils.hs#L499-L505)
and [Aiken](https://github.com/perturbing/plutus-accumulator/blob/main/aiken-bilinear-accumulator/lib/aiken_bilinear_accumulator/poly.ak#L3-L13) 
implementations of [plutus-accumulator](https://github.com/perturbing/plutus-accumulator) use.
It can be slightly improved by _the divide-and-conquer_ method by pairing binomials, multiplying them, and
recursively multiplying the results, though it's still quadratic just with better coefficients.

Although it may not be the best candidate for an on-chain setting,
it's worth mentioning _[Number Theoretic Transform (NTT)](https://wiki.algo.is/Number%20theoretic%20transform)_, 
which achieves sub-quadratic time complexity of $O(n \cdot \log n)$.
BLS12-381 was specifically designed in so that 
the multiplicative group ${F}_r^\times$ of size $(r-1)$
has $2^{32}$-nd roots of unity enabling efficient FFT/NTT operations on large polynomials.

The important thing is that both algorithms rely on _modular multiplication_ 
over the _scalar field_.

As soon as the coefficients for the final polynomial have been calculated 
they are (typically) used for scalar multiplication,
either by pointwise `bls12_381_g1_scalar_mul` and `bls12_381_g2_scalar_mul` built-ins
or by recently added multi-scalar multiplication that computes the whole batch in one go
using an optimized algorithm. 
Due to the use of `Integer` for representing scalars,
and since the results of those functions are the same
for the whole _congruence class_ of scalars,
they try to reduce scalar arguments implicitly 
to fit them into the field by calling [mod operation](https://github.com/IntersectMBO/cardano-base/blob/6f9c20abdd3010e5a25356580cc968ba430101ad/cardano-crypto-class/src/Cardano/Crypto/EllipticCurve/BLS12_381/Internal.hs#L521).
As mentioned in the beginning, this complicates the cost model
but also pushes developers towards the _use of unbounded integers_.
(An alternative and arguably clearer decision might be to throw if an argument falls out of the field.)
So nowadays, developers have three options to accomplish this task:

1. Skip the step of taking the modulus with `modInteger`, i.e., to use
   unbounded integers for the whole calculation of the coefficients, and
   exploit the fact that functions for scalar multiplication reduce scalars 
   under the hood.
   As we will see in a moment, this is the best way in terms of exunits.

2. Take care of staying within the field when calculating coefficients and
   pass integer values that represent proper scalars to the consuming functions.
   Despite the intuition and common sense, this turns out to be more
   expensive due to the cost of the modulo operation.
   
3. A variation of (2) is to use Aiken stdlib [Scalar](https://aiken-lang.github.io/stdlib/aiken/crypto/bls12_381/scalar.html#Scalar) 
   module or similar thing in your language of choice 
   that hides modular operation in a newtype, 
   which obviously increases the expenditure of exunits even more.

### Benchmarks

The Aiken benchmarks for all three options can be found in the PR
[here](https://github.com/perturbing/plutus-accumulator/pull/2).
To keep track of all costs and their relative amounts in the use case being analyzed,
let's break the whole thing down into three parts:

* (a) Calculating coefficients of the final polynomial
* (b) Producing commitment using scalar multiplication and group operation in $G_1$
* (c) Running the Miller loop and verifying the results

Part (a) performs the convolution to get the final coefficients using 
the three different methods 1,2, and 3 described above over random samples of 1–30 binomials.
We can observe the quadratic growth in all cases as expected.

Not surprisingly, the first benchmark gives the best result of `1,67B cpu / 5,19 M mem`:
only addition and multiplication are used, and although costs for both operations depend on the size of arguments,
even over integers up to _10k-bit_ length, the total is relatively cheap:

```aiignore
 (a, 1) final_poly_int

   memory units                                           cpu units
   ⡁⠈⠀⠁⠈⠀⠁⠈⠀⠁⠈⠀⠁⠈⠀⠁⠈⠀⠁⠈⠀⠁⠈⠀⠁⠈⠀⠁⠈⠀⠁⠈⠀⠁⠈⠀⠁⠈⢀⠕⡁ 5189564.0    ⡁⠈⠀⠁⠈⠀⠁⠈⠀⠁⠈⠀⠁⠈⠀⠁⠈⠀⠁⠈⠀⠁⠈⠀⠁⠈⠀⠁⠈⠀⠁⠈⠀⠁⠈⠀⠁⠈⢀⠕⡁ 1669321088.0
   ⠄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠔⠁⠀⠄              ⠄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠔⠁⠀⠄
   ⠂⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡠⠃⠀⠀⠀⠂              ⠂⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡠⠃⠀⠀⠀⠂
   ⡁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡠⠊⠀⠀⠀⠀⠀⡁              ⡁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡠⠊⠀⠀⠀⠀⠀⡁
   ⠄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠔⠊⠀⠀⠀⠀⠀⠀⠀⠄              ⠄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠔⠊⠀⠀⠀⠀⠀⠀⠀⠄
   ⠂⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠤⠊⠀⠀⠀⠀⠀⠀⠀⠀⠀⠂              ⠂⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠤⠊⠀⠀⠀⠀⠀⠀⠀⠀⠀⠂
   ⡁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡠⠊⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡁              ⡁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⠔⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡁
   ⠄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡠⠊⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠄              ⠄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡠⠊⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠄
   ⠂⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡠⠤⠒⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠂              ⠂⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡠⠒⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠂
   ⡁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⠤⠊⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡁              ⡁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠤⠊⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡁
   ⠄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⠤⠒⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠄              ⠄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠤⠒⠊⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠄
   ⠂⠀⠀⠀⠀⠀⠀⣀⡠⠤⠔⠉⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠂              ⠂⠀⠀⠀⠀⠀⠀⣀⣀⡠⠤⠒⠊⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠂
   ⠥⠤⠤⠖⠲⠊⠍⠠⠀⠄⠠⠀⠄⠠⠀⠄⠠⠀⠄⠠⠀⠄⠠⠀⠄⠠⠀⠄⠠⠀⠄⠠⠀⠄⠠⠀⠄⠠⠀⠄⠁ 29989.0      ⠥⠤⠤⠖⠲⠊⠍⠠⠀⠄⠠⠀⠄⠠⠀⠄⠠⠀⠄⠠⠀⠄⠠⠀⠄⠠⠀⠄⠠⠀⠄⠠⠀⠄⠠⠀⠄⠠⠀⠄⠁ 8513737.0
   1.0                                 30.0               1.0                                 30.0
```

If we try to stay in the field using the general `modInteger` after all operations with scalars,
we pay more, since the modulo operation contributes more than we save up on the size of arguments
for addition and multiplication, so we get extra `+0,18B cpu / +0,37M mem` exunits spent:

```aiignore
 (a, 2) final_poly_int_mod
 
   memory units                                           cpu units
   ⡁⠈⠀⠁⠈⠀⠁⠈⠀⠁⠈⠀⠁⠈⠀⠁⠈⠀⠁⠈⠀⠁⠈⠀⠁⠈⠀⠁⠈⠀⠁⠈⠀⠁⠈⠀⠁⠈⢀⠕⡁ 5554829.0    ⡁⠈⠀⠁⠈⠀⠁⠈⠀⠁⠈⠀⠁⠈⠀⠁⠈⠀⠁⠈⠀⠁⠈⠀⠁⠈⠀⠁⠈⠀⠁⠈⠀⠁⠈⠀⠁⠈⢀⠕⡁ 1847736704.0
   ⠄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠔⠁⠀⠄              ⠄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠔⠁⠀⠄
   ⠂⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡠⠃⠀⠀⠀⠂              ⠂⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡠⠃⠀⠀⠀⠂
   ⡁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡠⠊⠀⠀⠀⠀⠀⡁              ⡁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡠⠊⠀⠀⠀⠀⠀⡁
   ⠄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠔⠊⠀⠀⠀⠀⠀⠀⠀⠄              ⠄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠔⠊⠀⠀⠀⠀⠀⠀⠀⠄
   ⠂⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠤⠊⠀⠀⠀⠀⠀⠀⠀⠀⠀⠂              ⠂⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠤⠊⠀⠀⠀⠀⠀⠀⠀⠀⠀⠂
   ⡁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡠⠊⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡁              ⡁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡠⠊⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡁
   ⠄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡠⠊⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠄              ⠄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡠⠊⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠄
   ⠂⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡠⠤⠒⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠂              ⠂⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡠⠒⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠂
   ⡁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⠤⠊⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡁              ⡁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⠤⠊⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡁
   ⠄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⠤⠒⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠄              ⠄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⠤⠒⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠄
   ⠂⠀⠀⠀⠀⠀⠀⣀⡠⠤⠔⠉⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠂              ⠂⠀⠀⠀⠀⠀⠀⣀⣀⡠⠤⠒⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠂
   ⠥⠤⠤⠖⠲⠊⠍⠠⠀⠄⠠⠀⠄⠠⠀⠄⠠⠀⠄⠠⠀⠄⠠⠀⠄⠠⠀⠄⠠⠀⠄⠠⠀⠄⠠⠀⠄⠠⠀⠄⠁ 31605.0      ⠥⠤⠤⠖⠲⠊⠍⠠⠀⠄⠠⠀⠄⠠⠀⠄⠠⠀⠄⠠⠀⠄⠠⠀⠄⠠⠀⠄⠠⠀⠄⠠⠀⠄⠠⠀⠄⠠⠀⠄⠁ 9250599.0
   1.0                                 30.0               1.0                                 30.0
```

And if we do the same using `Scalar` module from Aiken, we apparently will incur the same overhead
plus additional exunits for the newtype, which turns out to be roughly in the same ballpark.
This might not be very significant, but could make `Scalar` a tool that some may prefer 
to avoid due to inefficiency:

```aiignore
 (a, 3) final_poly_scalar

   memory units                                           cpu units
   ⡁⠈⠀⠁⠈⠀⠁⠈⠀⠁⠈⠀⠁⠈⠀⠁⠈⠀⠁⠈⠀⠁⠈⠀⠁⠈⠀⠁⠈⠀⠁⠈⠀⠁⠈⠀⠁⠈⢀⠕⡁ 5997541.0    ⡁⠈⠀⠁⠈⠀⠁⠈⠀⠁⠈⠀⠁⠈⠀⠁⠈⠀⠁⠈⠀⠁⠈⠀⠁⠈⠀⠁⠈⠀⠁⠈⠀⠁⠈⠀⠁⠈⢀⠕⡁ 1956092032.0
   ⠄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠔⠁⠀⠄              ⠄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠔⠁⠀⠄
   ⠂⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡠⠃⠀⠀⠀⠂              ⠂⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡠⠃⠀⠀⠀⠂
   ⡁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠤⠊⠀⠀⠀⠀⠀⡁              ⡁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠤⠊⠀⠀⠀⠀⠀⡁
   ⠄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠔⠁⠀⠀⠀⠀⠀⠀⠀⠄              ⠄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠔⠁⠀⠀⠀⠀⠀⠀⠀⠄
   ⠂⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠔⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠂              ⠂⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠔⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠂
   ⡁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠤⠊⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡁              ⡁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠤⠊⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡁
   ⠄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡠⠔⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠄              ⠄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡠⠔⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠄
   ⠂⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡠⠔⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠂              ⠂⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡠⠔⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠂
   ⡁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡠⠒⠊⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡁              ⡁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⠤⠊⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡁
   ⠄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⠔⠉⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠄              ⠄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⠔⠉⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠄
   ⠂⠀⠀⠀⠀⠀⠀⣀⡠⠔⠒⠉⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠂              ⠂⠀⠀⠀⠀⠀⠀⣀⡠⠔⠒⠉⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠂
   ⠥⠤⠤⠖⠩⠉⠍⠠⠀⠄⠠⠀⠄⠠⠀⠄⠠⠀⠄⠠⠀⠄⠠⠀⠄⠠⠀⠄⠠⠀⠄⠠⠀⠄⠠⠀⠄⠠⠀⠄⠁ 45523.0      ⠥⠤⠤⠖⠲⠊⠍⠠⠀⠄⠠⠀⠄⠠⠀⠄⠠⠀⠄⠠⠀⠄⠠⠀⠄⠠⠀⠄⠠⠀⠄⠠⠀⠄⠠⠀⠄⠠⠀⠄⠁ 12851804.0
   1.0                                 30.0               1.0                                 30.0
```

Moving to part (b), which performs the calculation of the commitment in $G_1$ using scalar multiplication
and the group operation, we may expect to see some proportional payoff when passing unbounded out-of-field arguments.
Here we benchmark only the calculation of the commitment,
the sampling of final unbound/bound coefficients is done in separate `Fuzzer`s, 
i.e., outside the benchmark itself.
The results show that for some reason, this expectation is generally correct, 
but the difference is really very tiny. 
For the biggest input of 30 elements we pay `0,1B cpu`, which is roughly 
one-fourth of what we saved up earlier. 
The memory usage is not affected.

```aiignore
 (b, 1) g1_commitment_unbound
   memory units                                           cpu units
   ⡁⠈⠀⠁⠈⠀⠁⠈⠀⠁⠈⠀⠁⠈⠀⠁⠈⠀⠁⠈⠀⠁⠈⠀⠁⠈⠀⠁⠈⠀⠁⠈⠀⠁⠈⠀⠁⣈⡠⠕⡁ 254920.0     ⡁⠈⠀⠁⠈⠀⠁⠈⠀⠁⠈⠀⠁⠈⠀⠁⠈⠀⠁⠈⠀⠁⠈⠀⠁⠈⠀⠁⠈⠀⠁⠈⠀⠁⠈⠀⠁⣈⡠⠕⡁ 5908456448.0
   ⠄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡠⠊⠀⠀⠀⠄              ⠄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡠⠊⠀⠀⠀⠄
   ⠂⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡠⠤⠒⠁⠀⠀⠀⠀⠀⠂              ⠂⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡠⠤⠒⠁⠀⠀⠀⠀⠀⠂
   ⡁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠤⠊⠀⠀⠀⠀⠀⠀⠀⠀⠀⡁              ⡁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠤⠊⠀⠀⠀⠀⠀⠀⠀⠀⠀⡁
   ⠄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡠⠒⠊⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠄              ⠄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡠⠒⠊⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠄
   ⠂⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠤⠔⠊⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠂              ⠂⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠤⠔⠊⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠂
   ⡁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡠⠊⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡁              ⡁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡠⠊⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡁
   ⠄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⠔⠒⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠄              ⠄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⠔⠒⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠄
   ⠂⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡠⠤⠊⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠂              ⠂⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡠⠊⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠂
   ⡁⠀⠀⠀⠀⠀⠀⠀⠀⡠⠔⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡁              ⡁⠀⠀⠀⠀⠀⠀⠀⠀⡠⠔⠉⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡁
   ⠄⠀⠀⠀⠀⢀⡠⠒⠊⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠄              ⠄⠀⠀⠀⠀⢀⡠⠒⠊⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠄
   ⠂⠀⠀⡠⠒⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠂              ⠂⠀⠀⡠⠒⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠂
   ⠥⠪⠉⠄⠠⠀⠄⠠⠀⠄⠠⠀⠄⠠⠀⠄⠠⠀⠄⠠⠀⠄⠠⠀⠄⠠⠀⠄⠠⠀⠄⠠⠀⠄⠠⠀⠄⠠⠀⠄⠁ 22166.0      ⠥⠪⠉⠄⠠⠀⠄⠠⠀⠄⠠⠀⠄⠠⠀⠄⠠⠀⠄⠠⠀⠄⠠⠀⠄⠠⠀⠄⠠⠀⠄⠠⠀⠄⠠⠀⠄⠠⠀⠄⠁ 430848992.0
   1.0                                 30.0               1.0                                 30.0

 (b, 2/3) g1_commitment_field
   memory units                                           cpu units```
   ⡁⠈⠀⠁⠈⠀⠁⠈⠀⠁⠈⠀⠁⠈⠀⠁⠈⠀⠁⠈⠀⠁⠈⠀⠁⠈⠀⠁⠈⠀⠁⠈⠀⠁⠈⠀⠁⣈⡠⠕⡁ 254920.0     ⡁⠈⠀⠁⠈⠀⠁⠈⠀⠁⠈⠀⠁⠈⠀⠁⠈⠀⠁⠈⠀⠁⠈⠀⠁⠈⠀⠁⠈⠀⠁⠈⠀⠁⠈⠀⠁⣈⡠⠕⡁ 5892875264.0
   ⠄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡠⠊⠀⠀⠀⠄              ⠄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡠⠊⠀⠀⠀⠄
   ⠂⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡠⠤⠒⠁⠀⠀⠀⠀⠀⠂              ⠂⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡠⠤⠒⠁⠀⠀⠀⠀⠀⠂
   ⡁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠤⠊⠀⠀⠀⠀⠀⠀⠀⠀⠀⡁              ⡁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠤⠊⠀⠀⠀⠀⠀⠀⠀⠀⠀⡁
   ⠄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡠⠒⠊⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠄              ⠄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡠⠒⠊⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠄
   ⠂⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠤⠔⠊⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠂              ⠂⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠤⠔⠊⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠂
   ⡁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡠⠊⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡁              ⡁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡠⠊⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡁
   ⠄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⠔⠒⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠄              ⠄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⠔⠒⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠄
   ⠂⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡠⠤⠊⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠂              ⠂⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡠⠤⠊⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠂
   ⡁⠀⠀⠀⠀⠀⠀⠀⠀⡠⠔⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡁              ⡁⠀⠀⠀⠀⠀⠀⠀⠀⡠⠔⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡁
   ⠄⠀⠀⠀⠀⢀⡠⠒⠊⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠄              ⠄⠀⠀⠀⠀⢀⡠⠒⠊⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠄
   ⠂⠀⠀⡠⠒⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠂              ⠂⠀⠀⡠⠒⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠂
   ⠥⠪⠉⠄⠠⠀⠄⠠⠀⠄⠠⠀⠄⠠⠀⠄⠠⠀⠄⠠⠀⠄⠠⠀⠄⠠⠀⠄⠠⠀⠄⠠⠀⠄⠠⠀⠄⠠⠀⠄⠁ 22166.0      ⠥⠪⠉⠄⠠⠀⠄⠠⠀⠄⠠⠀⠄⠠⠀⠄⠠⠀⠄⠠⠀⠄⠠⠀⠄⠠⠀⠄⠠⠀⠄⠠⠀⠄⠠⠀⠄⠠⠀⠄⠁ 430848992.0
   1.0                                 30.0               1.0                                 30.0
```

The last part (c) that performs the actual pairing doesn't depend on the input size 
and has a constant cost of `1B / 5K mem`. 

Overall, we have the following distribution of cpu exunits for the biggest input in the benchmark:

|                 Part | Unbounded (1) | Percent | Reduced (2)   | Percent | Diffence     |  
|---------------------:|---------------|---------|---------------|---------|--------------|  
| **(a)** Coefficients | 1_669_321_088 | 19%     | 1_847_736_704 | 21%     | +178_415_616 |  
|   **(b)** Commitment | 5_908_456_448 | 68%     | 5_892_875_264 | 67%     | −15_581_184  |  
|      **(c)** Pairing | 1_098_158_336 | 13%     | 1_098_158_336 | 12%     | -            |  
|           **Total:** | 8_675_935_872 | -       | 8_838_770_304 | −       | +162_834_432 |

We haven't benchmarked _multi-scalar multiplication_ yet, but even using pointwise multiplication,
we can see that the percent spent on part (a) calculating coefficients is quite substantial,
and it will become bigger when part (b) becomes cheaper.

### Montgomery multiplication

Though `Integer`s can carry out required computations, for prime fields
there exists much more efficient methods for multiplication and addition.
[Montgomery multiplication](https://en.wikipedia.org/wiki/Montgomery_modular_multiplication)
seems to be a viable alternative for such and similar use cases that use 
multiplication over many scalars in one go since it's known to be much faster.

We did [preliminary benchmarks](https://github.com/euonymos/bench-montgomery) for multiplication of binomials 
to compare the optimized implementation in `blst` library (which is already used in Plutus for BLS12-381)
with naive implementation.
We used Rust bindings for `blst` and Rust-native `num-bigint` library. 
The underlying bindings are the same as those used in `cardano-base` for `bslt`, 
so we can expect similar behavior for the Haskell stack.
Each benchmark was executed 1000 times on Intel(R) Core(TM) i7-8550U CPU @ 1.80GHz.
Values show average time and standard deviation.

| Size | Montgomery Avg | Montgomery σ | Naive Avg    | Naive σ      | Speedup |
|-----:|----------------|--------------|--------------|--------------|---------|
|   10 | 101.734 µs     | 22.565 µs    | 685.302 µs   | 159.436 µs   | 6.74x   |
|   15 | 138.966 µs     | 26.496 µs    | 953.121 µs   | 251.909 µs   | 6.86x   |
|   20 | 186.083 µs     | 21.703 µs    | 1.363 ms     | 189.064 µs   | 7.33x   |
|   25 | 241.934 µs     | 30.409 µs    | 2.096 ms     | 370.952 µs   | 8.67x   |
|   30 | 298.265 µs     | 33.504 µs    | 2.926 ms     | 401.267 µs   | 9.81x   |
|   31 | 310.631 µs     | 33.857 µs    | 3.108 ms     | 334.523 µs   | 10.00x  |
|   32 | 328.822 µs     | 45.218 µs    | 3.461 ms     | 521.307 µs   | 10.52x  |
|   35 | 355.684 µs     | 49.508 µs    | 4.142 ms     | 579.682 µs   | 11.65x  |
|   40 | 396.741 µs     | 63.206 µs    | 5.474 ms     | 749.828 µs   | 13.80x  |
|   45 | 472.785 µs     | 85.491 µs    | 7.602 ms     | 1.501 ms     | 16.08x  |
|   50 | 534.158 µs     | 119.238 µs   | 10.226 ms    | 3.898 ms     | 19.14x  |
|  100 | 1.090 ms       | 239.000 µs   | 35.546 ms    | 8.156 ms     | 32.61x  |
|  200 | 3.042173ms     | 483.892µs    | 141.871796ms | 21.302688ms  | 46.64x  |
|  300 | 6.040093ms     | 1.034338ms   | 319.940927ms | 50.53683ms   | 52.97x  |
|  400 | 8.951528ms     | 901.017µs    | 500.398941ms | 49.487447ms  | 55.90x  |
| 1000 | 49.006538ms    | 4.043325ms   | 3.044053658s | 223.957115ms | 62.12x  |

The table shows that the performance improvement rises quickly with the number of binomials.
The provided figures for Montgomery multiplication _include_ time for converting the initial
vector of coefficients into the Montgomery form and back to integers in the end for the results.

### Summary

The way Plutus treats BLS12-381 scalars (and prime fields in general, for that matter) 
is understandable but not quite satisfying for several reasons.

The main argument showcased by this use case is that the significant share of work 
(20% using pointwise multiplication, which will be bigger with MSM)
can be done much faster and with less resource usage in terms of real performance.
Even for on-chain-plausible sizes of inputs, Montgomery multiplication can give
at least 30–40 times speed-up.

Additionally, there are other reasons to consider:

* It's counterintuitive since it clashes with the mental model of the finite field.
* Representation of field elements as `Integers` (and even worse, peculiarities of the cost model as we saw)
pushes developers to use unbounded integers, which may lead to misunderstanding and unexpected bugs.
* It complicates the cost model by (mis)using `Integer` type for scalars.
* `Scalar` module from Aiken buys some safety at the cost of additional expenses and likely won't be used.
* The choice of `Integer` also may require additional conversions, 
since the most probable source of scalars that scripts calculate is hashing functions
that return byte strings.

Incorporating the effective multiplication over the scalar field
directly will streamline such operations, reduce transaction costs,
thereby advancing the Plutus ecosystem in terms of functionality and dev experience.

### Impact

In Cardano, the multiplication of scalars in the BLS12-381 scalar field is used 
by cryptographic primitives that need polynomial arithmetic over — mostly
when dealing with polynomial commitments (KZG).

Those primitives are used in many Cardano products, just to mention a few:

- **Hydrozoa** (a brand-new layer-2 solution for Cardano) - 
uses pairing-based cryptographic accumulators to commit to a set of L2 utxos 
that can be withdrawn once a dispute is resolved in the rule-based regime of operation.
More specifically, the withdrawal transaction calculates the hashes of the outputs
and validates their membership in the accumulator using the proof provided.
MSM and efficient scalars can boost the number of utxos withdrawn in one go significantly.
- 
- TBD: add more examples

## Specification

> This is all the _very preliminary_ description. I am willing to work on it if the community
gives me the green light in general.

The various BLS12-381-specific operations for the scalar field $F_r$, including Montgomery multiplication 
are implemented in [blst](https://github.com/supranational/blst/blob/e99f7db0db413e2efefcfd077a4e335766f39c27/bindings/blst.h#L88-L105) library, 
which is already a dependency of [cardano-base](https://github.com/IntersectMBO/cardano-base/blob/master/cardano-crypto-class/src/Cardano/Crypto/EllipticCurve/). 
It has been used for implementing 
[CIP-381](https://cips.cardano.org/cip/CIP-0381) 
and [CIP-133](https://cips.cardano.org/cip/CIP-0133). 
Basically, we would like to expose several additional functions from this library in the Plutus API.

### New types definition

To represent a scalar in $F_r$ stored in the Montgomery form, a new opaque type `bls12_381_fr`
(which corresponds to `blst_fr` type) can be used along with introducing and eliminating from/to a _byte string_: 

```
bytestring_to_bls12_381_fr: [bool, 𝚋𝚢𝚝𝚎𝚜𝚝𝚛𝚒𝚗𝚐] -> bls12_381_fr
bls12_381_fr_to_bytestring :: [bool, bls12_381_fr] -> 𝚋𝚢𝚝𝚎𝚜𝚝𝚛𝚒𝚗𝚐
```

The conversion is little-endian if the first argument is `false` and big-endian if it is `true`.
We prefer not to choose the name `bls12_381_scalar` to avoid name clashes with existing functions
for _scalar multiplication_ like `bls12_381_G1_scalarMul`.

### Function definition

In addition to the conversion functions mentioned in the previous section,
we propose to define the only function for Montgomery modular multiplication
**bls12_381_fr_mul** as follows:

```
bls12_381_fr_mul :: [bls12_381_fr, bls12_381_fr] -> bls12_381_fr
```
TBD: Scalar and multi-scalar multiplication in $G1$ and $G2$ are typical downstream functions 
for `bls12_381_fr` values, but in the current Plutus, they use integers, i.e., double conversion is needed:
`bls12_381_fr -> bytestring -> integer` to call them.
The underlying `blst` functions take a pointer to raw bytes, i.e., `const byte *scalar`, so probably
we should consider ways of simplifying this by either having scalar multiplication that works with
byte arrays or providing a function to go directly from `bls12_381_fr` to `integer`.

TBD: Additionally, we might consider adding some other functions that `blst` [provides](https://github.com/supranational/blst/blob/e99f7db0db413e2efefcfd077a4e335766f39c27/bindings/blst.h#L88-L105).

### Cost model

The computational impact of Montgomery multiplication is straightforward, since the values of
type `bls12_381_fr` are statically limited to 255 bits, so for the newly added `bls12_381_fr_mul`
function we can use a static cost model.

TDB: Introduction of this type potentially allows simplifying cost models for some other functions.
Currently, scalars have to be reduced modulo the order of the group before being passed to the `blst` 
functions, see [cardano-base](https://github.com/IntersectMBO/cardano-base/blob/6f9c20abdd3010e5a25356580cc968ba430101ad/cardano-crypto-class/src/Cardano/Crypto/EllipticCurve/BLS12_381/Internal.hs#L521).

## Rationale: how does this CIP achieve its goals?

The availability of built-in functions in the Plutus language will provide a
more efficient way to perform this important type of computation,
bump the limits of operations that fit into a single transaction,
and reduce costs.

Implementing the Montgomery multiplication directly in Plutus should be technically possible
with CIP-122, but will hardly bring any improvements mentioned and so is not advisable.

## Path to Active

### Acceptance Criteria

We consider the following criteria to be essential for acceptance:

- [ ] The PR for this functionality is merged in the Plutus repository.
- [ ] This PR must include tests, demonstrating that it behaves as the specification requires in this CIP.
- [ ] A benchmarked use case is implemented in the Plutus repository, demonstrating that realistic use of this primitive does, in fact, provide major cost savings.

### Implementation Plan

- [ ] IOG Plutus team consulted and accept the proposal.
- [ ] Authors to provide preliminary benchmarks of naive vs. Montgomery multiplication for use cases in general and in Plutus:
  - https://github.com/euonymos/bench-montgomery

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
