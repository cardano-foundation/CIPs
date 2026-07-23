---
CIP: 9999
Title: Cardano Problem Statements
Category: Plutus
Status: Active
Authors:
    - Thomas Vellekoop <thomas.vellekoop@iohk.io>
    - Gamze Orhon Kilic <gamze.kilic@iohk.io>
Implementors: N/A
Discussions:
Created: 
License: CC-BY-4.0
---

## Abstract

## Problem

## Specs

### Poseidon

Poseidon is a cryptographic hash function designed to be efficient inside zero-knowledge proof systems (ZK-SNARKs, STARKs, PLONK, etc.). 
Unlike "traditional" hashes such as SHA-256 or Blake2b, which operate on bits and are
cheap on a CPU but extremely expensive to prove in a circuit, Poseidon operates directly over the elements of a large prime field `$F_p$`, where `$p$` is usually the scalar field of the elliptic curve underlying the proof system. 
Because its operations are native field additions and multiplications, the number of constraints needed to prove a Poseidon evaluation is orders of magnitude smaller than for a bit-oriented hash. 
This is what makes it "arithmetization-friendly".

#### The sponge construction

Poseidon hashes arbitrary-length input using the same **sponge** construction as Keccak/SHA-3. 
The internal state is a vector of `$t = r + c$` field elements:

- `r` (the *rate*): how many field elements of input are absorbed per step, and how many are squeezed out per step.
- `c` (the *capacity*): reserved elements that are never touched directly by input/output; they carry the security of the construction (roughly `$c \cdot \log_2(p)/2$` bits).

Hashing proceeds in two phases:

1. **Absorb**: the input (padded to a multiple of `r`) is split into chunks of `r` field elements.
   Each chunk is added into the first `r` elements of the state, then the whole state is run through the Poseidon **permutation** `P`.
2. **Squeeze**: after all input is absorbed, the first `r` elements of the state are read off as output.
   If more output is needed, `P` is applied again and more elements are read.

For the common fixed-arity case (e.g. hashing two field elements into one, as in a Merkle tree) this reduces to a single application of the permutation.

#### The permutation (HADES design)

The core of Poseidon is a fixed permutation `$P$` over `$\mathbb{F}_p^t$`, built as a substitution-permutation network following the **HADES** strategy. 
It applies a sequence of rounds, each composed of three steps:

1. **AddRoundConstants (ARC)**: add fixed, round-specific constants `$c_i$` to every state element.
   This breaks symmetry and acts like a key schedule.
2. **S-box (SubWords)**: the non-linear layer, raising elements to a fixed power, `$x \mapsto x^\alpha$`.
   `$\alpha$` is the smallest integer (commonly `$\alpha = 5$`, sometimes `$3$`) such that `$\gcd(\alpha, p - 1) = 1$`, which guarantees the map is a bijection.
3. **MixLayer (linear layer)**: multiply the state vector by a fixed `$t \times t$` MDS (Maximum Distance Separable) matrix `$M$`.
   This diffuses each element across the entire state.

The key HADES insight is mixing two kinds of rounds:

- **Full rounds (`$R_F$`)**: the S-box is applied to *all* `$t$` state elements.
- **Partial rounds (`$R_P$`)**: the S-box is applied to *only one* element; the rest pass through the non-linear layer untouched.

The rounds are arranged as `$R_F/2$` full rounds, then `$R_P$` partial rounds, then `$R_F/2$` full rounds. 
Full rounds provide strong security against statistical attacks (differential/linear), while the cheaper partial rounds provide algebraic security (against interpolation / Gröbner-basis attacks) at a fraction of the constraint cost. 

> **Notation:** the paper [1] uses two symbols for full rounds: `$R_f$` (lowercase) for the full rounds on *one* side, and `$R_F = 2R_f$` (uppercase) for the *total*. 
> Throughout this document `$R_F$` always denotes the total number of full rounds (so `$R_F/2$` on each side equals the paper's `$R_f$`). 
> The paper's statistical-security minimum is `$R_F \geq 6$`; the value `$R_F = 8$` used below is that minimum plus the recommended safety margin.

The S-box is the most expensive operation in a circuit, so applying it to one element instead of `$t$` for most rounds is where the savings come from. 
The exact round counts `$(R_F, R_P)$` are derived from `$p$`, `$t$`, and `$\alpha$` to give a target security level (typically 128 bits).

#### Parameters

A concrete Poseidon instance is fully specified by:

- the field `$p$`;
- the state size `$t$` (and hence rate `r` and capacity `c`);
- the S-box exponent `$\alpha$`;
- the round numbers `$(R_F, R_P)$`;
- the round constants `$c_i$` and the MDS matrix `$M$` (generated deterministically, e.g. from a Grain LFSR seeded by the other parameters).

Because these must match exactly on both the prover and verifier side, any use of Poseidon on Cardano needs a single, unambiguous parameter set fixed by the specification.

#### Concrete parameters

The parameter sets below are the de-facto values used across the Ethereum/ZK ecosystem (the `circomlib` reference implementation [5]), targeting **128-bit security** with S-box exponent **`$\alpha = 5$`**. 
They apply to the two prime fields most relevant to Cardano: the **BLS12-381** scalar field (`$p \approx 2^{255}$`, the curve exposed by Plutus built-ins) and the **BN254** scalar field (`$p \approx 2^{254}$`).

For `$\alpha = 5$`, the number of full rounds is fixed at **`$R_F = 8$`** (split as 4 rounds before and 4 after the partial rounds), while the number of partial rounds `$R_P$` grows with the state size `$t$`:

| Use case | `$t$` (rate `$r$` / capacity `$c$`) | `$\alpha$` | `$R_F$` | `$R_P$` |
|---|---|---|---|---|
| 2 → 1 (e.g. Merkle node) | 3 (`$r=2$`, `$c=1$`) | 5 | 8 | 57 |
| 4 → 1 | 5 (`$r=4$`, `$c=1$`) | 5 | 8 | 60 |

The full `circomlib` table of partial-round counts, indexed by `$t - 2$`, is:

```
R_P[t] = [56, 57, 56, 60, 60, 63, 64, 63, 60, 66, 60, 65, 70, 60, 64, 68]
         (t = 2, 3, 4, 5, ...)
```

The two fields are:

- **BLS12-381** scalar field: `p = 52435875175126190479447740508185965837690552500527637822603658699938581184513`
- **BN254** scalar field: `p = 21888242871839275222246405745257275088548364400416034343698204186575808495617`

> **Caveat:** these `R_F`/`R_P` values include a security margin and are the *deployed* de-facto standard, not necessarily the theoretical minima. 
> The Poseidon paper's own `calc_round_numbers.py` can produce slightly different counts depending on the margin and attack assumptions chosen. 
> This specification must therefore fix the exact generator script and its inputs (not merely the table), so that round constants, the MDS matrix, and round counts are reproducible bit-for-bit.

> **Note:** *Poseidon2* is a newer, drop-in successor that keeps the same round structure but uses a cheaper linear layer and constant schedule, giving better plain-CPU and circuit performance. 
> Which variant (and parameter set) to standardize is one of the design decisions this document addresses.

## References

1. L. Grassi, D. Khovratovich, C. Rechberger, A. Roy, M. Schofnegger. *Poseidon: A New Hash Function for Zero-Knowledge Proof Systems.* USENIX Security 2021. IACR ePrint [2019/458](https://eprint.iacr.org/2019/458).
2. L. Grassi, R. Lüftenegger, C. Rechberger, D. Rotaru, M. Schofnegger. *On a Generalization of Substitution-Permutation Networks: The HADES Design Strategy.* EUROCRYPT 2020. IACR ePrint [2019/1107](https://eprint.iacr.org/2019/1107).
3. L. Grassi, D. Khovratovich, M. Schofnegger. *Poseidon2: A Faster Version of the Poseidon Hash Function.* AFRICACRYPT 2023. IACR ePrint [2023/323](https://eprint.iacr.org/2023/323). Reference parameters: [HorizenLabs/poseidon2](https://github.com/HorizenLabs/poseidon2/blob/main/poseidon2_rust_params.sage).
4. G. Bertoni, J. Daemen, M. Peeters, G. Van Assche. *Cryptographic Sponge Functions* / *On the Indifferentiability of the Sponge Construction*, EUROCRYPT 2008. [keccak.team/sponge_duplex.html](https://keccak.team/sponge_duplex.html).
5. iden3. *circomlib*. Reference Poseidon circuit and round-number table: [circuits/poseidon.circom](https://github.com/iden3/circomlib/blob/master/circuits/poseidon.circom).

## Copyright

<!-- The CPS must be explicitly licensed under acceptable copyright terms. Uncomment the license you wish to use (delete the other one) and ensure it matches the License field in the header.

If AI/LLMs were used in the creation of the copyright text, the author may choose to include a disclaimer to describe their application within the proposal.
-->

<!-- This CPS is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode). -->
<!-- This CPS is licensed under [Apache-2.0](http://www.apache.org/licenses/LICENSE-2.0). -->