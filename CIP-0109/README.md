---
CIP: 109
Title: Modular Exponentiation Built-in for Plutus Core
Status: Proposed
Category: Plutus
Authors:
    - Kenneth MacKenzie <kenneth.mackenzie@iohk.io>
    - Michael Peyton Jones <michael.peyton-jones@iohk.io>
    - Iñigo Querejeta-Azurmendi <inigo.querejeta@iohk.io>
    - Thomas Vellekoop <thomas.vellekoop@iohk.io>
Implementors:
    - Michael Peyton Jones <michael.peyton-jones@iohk.io>
    - Thomas Vellekoop <thomas.vellekoop@iohk.io>
Discussions:
    - https://github.com/cardano-foundation/CIPs/pull/641
Created: 2023-10-05
License: CC-BY-4.0
---
## Abstract
This CIP proposes an extension of the current plutus functions to provide support for the efficient calculation of modular exponentiation with inverses.

## Motivation: why is this CIP necessary?
Modular exponentiation is a cornerstone operation in numerous cryptographic protocols. The availability of such a function directly within Plutus will provide a more efficient and reliable means to perform this crucial computation. Therefore, the integration of such a Plutus core built-in is imperative to enhance cryptographic functionalities within the ecosystem.

More concretely, the key area where this function would contribute is that of finite field arithmetic, which is a basis for elliptic curves. In this context, a finite field is a set of integers modulo a prime number `p`. On this set, we have the basic operations of addition, multiplication, additive inversion (negation) and the multiplicative inversion (reciprocal), all reduced modulo the prime number `p`.

With the current built-in functions, most of these operations can be implemented relatively cheaply, except the reciprocal. This function can be implemented via either the Extended Euclidean algorithm or using Fermat's little theorem. Using the preliminary cost-model for plutus V3, both implementations still [consume](https://github.com/perturbing/mod-exp-bench/tree/558b6a47cb18d063b6a7324a15087f87fa3da673) around ~5% and ~9% of the CPU budget on mainnet. These benchmarks are performed for the scalar field of the BLS12-381 curve, which has a 255 bit prime modulus.

The result is that doing such computation in a practical setting on-chain is costly, and other methods should be used to find this multiplicative inverse. A cumbersome method for solving this issue, is calculating the inverse off-chain and bringing it in scope via a redeemer as a claimed inverse of another element. This method works, as one can cheaply check that the claimed inverse is indeed the unique inverse with one multiplication, one modulo reduction and one equality check with the multiplicative identity. In math notation this means that for a field element `a`, we off-chain compute `claimed_inverse_a`, such that on-chain we can check: `claimed_inverse_a * a = id`.

The drawback of this technique is that by transferring the calculation off-chain, we incur additional fees due to the increased size of the transaction, as CPU units are cheaper. The creator of the transaction is also burdened by this computation, which often precedes more intricate, non-trivial cryptographic calculations. In the application of zero knowledge, this calculation if often implemented in low-level code, and used via bindings, meaning that extracting these intermediary values breaks existing code and interfaces.

In conclusion, integrating modular exponentiation as a core built-in within Plutus is not only essential for enhancing cryptographic capabilities, but also for optimizing on-chain computations. The current approach, which offloads certain calculations like finding multiplicative inverses to off-chain processes, is inefficient and costly in terms of transaction size and computational burden on the transaction creators. Incorporating this function directly into Plutus will streamline these operations, reduce transaction costs, and maintain the integrity of existing tools, thereby significantly advancing the Plutus ecosystem's functionality and user experience.

A nonexclusive list of cryptographic protocols that use a field and would benefit from having this built-in are:

1. The verification of pairing based zero-knowledge proofs over BLS12-381. This pairing curve has a base field and a scalar field, with primes of size 381 and 255 bits respectively. In, for example, the proof system plonk, a verifier performs one reciprocal for each public input in the 255 bit scalar field.
2. Onchain public key aggregation for Schnorr over SECP256k1: effectively, this aggregation is the point addition of the two keys on the curve, which requires one reciprocal in the SECP256k1 base field (using a 256 bit prime).
3. A more interoperable interface for the BLS-12-381 built-ins: currently, the BLS-12-381 built-ins only expose a compressed version of a point, containing the `x` coordinate and some marked bits to describe how one can find the corresponding `y` in the base field. This calculation of finding `y` requires modular exponentiation in the field.

## Specification
Modular exponentiation is mathematically defined as the equivalence relation

$$
a \equiv b^{e} (\bmod{m})
$$

Here we have that the base $b$ is an integer, the exponent $e$ a non-negative integer and the modulus $m$ a positive integer. To be more specific, we want $e$ to be larger or equal to zero, and $m$ is larger than zero. This is because what we are effectively doing, is multiplying $e$ copies of $b$ and a modulo reduction by $m$. In this context, multiplying a negative number of copies of $b$ has no definition.


$$
\begin{equation}
a \equiv \underbrace{(b \times b \times ... \times b)}_{e \textrm{ times}} (\bmod{m} )
\end{equation}
$$

That said, in the context of multiplicative inversion, a negative exponent can be interpreted as taking the exponent of the inverse of the base number. That is

$$
\begin{equation}
b^{-e} (\bmod{m}) := (b^{-1})^{e} (\bmod{m})
\end{equation}
$$

We propose to also include this extension to the plutus built-in, for optimized inversion when this is possible. This is inversion is not guaranteed to exist for all numbers $b$, only when the modulus $m$ is a prime number this is guaranteed. We also propose that the built-in fails if this inverse does not exist, and if a modulus is provided that is smaller than one.

### Function definition
With the above, we define a new Plutus built-in function with the following type signature

```hs
modularExponentiation :: Integer -> Integer -> Integer -> Integer
```
here the first argument is the base, the second the exponent and the third the modulus. As mentioned above, the behavior of this function is that it fails if the modulus is not a positive integer, or if the inverse of the base does not exist for a negative exponent. For the lower level implementation, we propose the usage of the `integerPowMod` function in the `ghc-bignum` packages. This function has the desired functionality, is optimized, and is easy to integrate in the plutus stack.

### Cost model
The computational impact of modular exponentiation is complexified by it having three arguments. That said, observe that the integers used can always be bound by the modulus. Preliminary [benchmarks](https://github.com/perturbing/expFast-bench/tree/cca69b842050de9523493d52c20384bc50c80b22) on the time consumption of this `integerPowMod` function show that it can be costed constant in the size of its first argument (the base) and linear in the other two.

## Rationale: how does this CIP achieve its goals?
Integrating this function directly into Plutus will streamline cryptographic operations, reduce transaction costs, and uphold the integrity of existing cryptographic interfaces. It addresses current inefficiencies and enhances the cryptographic capabilities of the Plutus platform.

For completeness and an historic perspective, the above functionality can also be attained by a new built-in function that performs normal exponentiation, after which one can reduce with the already present built-in function `ModInteger`. In the creation of this CIP, this possibility was discussed but put aside. This method has the flaw that the intermediate value of these integers is not bound. Meaning that memory consumption is not efficient for practical use in this setting.

## Path to Active

### Acceptance Criteria

We consider the following criteria to be essential for acceptance:

- [ ] The PR for this functionality is merged in the Plutus repository.
- [ ] This PR must include tests, demonstrating that it behaves as the specification requires in this CIP.
- [ ] A benchmarked use case is implemented in the Plutus repository, demonstrating that realistic use of this primitive does, in fact, provide major cost savings.

### Implementation Plan

- [x] IOG Plutus team consulted and accept the proposal.
- [x] Author to provide preliminary benchmarks of time consumption.
  - https://github.com/perturbing/expFast-bench/tree/cca69b842050de9523493d52c20384bc50c80b22

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
