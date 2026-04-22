---
CPS: ?
Title: Quantum-Secure Cardano settlement layer
Category: Consensus
Status: Open
Authors:
    - Hamza Jeljeli <hamza.jeljeli@iohk.io>
    - Gamze Kilic <gamze.kilic@iohk.io>
    - Damien Robissout <damien.robissout@iohk.io>
    - Thomas Vellekoop <thomas.vellekoop@iohk.io>
Proposed Solutions: []
Discussions:
    - Original PR: https://github.com/cardano-foundation/CIPs/pull/1175
Created: 2026-04-02
License: CC-BY-4.0
---

## Abstract

<!-- A short (\~200 word) description of the target goals and the technical obstacles to those goals. -->

The prospect of a quantum-capable adversary is becoming increasingly credible, and with that, the Cardano blockchain should prepare for it.
This CPS describes the problems this QC adversary brings to Cardano. It has in scope all the cryptographic
primitives that are used in the base settlement layer of Cardano. The goal of this problem statement
is to describe the technical weaknesses in detail and pose a non-exhaustive overview of some replacement
primitives to show the impact and give a sense of the design space.

This CPS does not have the on-chain smart contract language Plutus in scope, as this is constrained by another set
of design principles that would clutter this discussion. That does not mean that this is not at risk against a QC adversary!
Quite the contrary, as described in [this pull request](https://github.com/cardano-foundation/CIPs/pull/1144).
Moreover, the impact of some of the design constraints in this CPS also constrains the Plutus context. But given that the
security of Plutus breaks if consensus is attacked, the priority of this broad discussion should focus on that first.

## Problem

Cardano relies on public-key cryptography for transaction authorization,
delegation, stake pool operations, and consensus-critical functions. The
security of the settlement layer therefore depends on cryptographic primitives
that were designed against classical attackers and may not remain secure
against sufficiently capable quantum attackers.

### Context: why this matters now

Quantum hardware continues to advance. More importantly, recent work continues
to reduce published resource estimates for quantum attacks on elliptic-curve
cryptography ([Ha, Lee, and Heo, 2024](https://www.nature.com/articles/s41598-024-54434-w);
[Babbush et al., 2026](https://research.google/pubs/securing-elliptic-curve-cryptocurrencies-against-quantum-vulnerabilities-resource-estimates-and-mitigations/)).
This reduces the margin between the time needed for migration and the time at
which such attacks may become feasible.

This matters at the Cardano settlement layer because migration of the base layer
cryptography is slow and coordination-heavy. Any change in this area affects
ledger rules, consensus, node implementations, wallets, stake pool operators,
exchanges, and other ecosystem participants. It also requires broad community
alignment and careful rollout planning. As a result, Cardano cannot wait until
the risk becomes immediate before preparing a migration path.

Cardano exposes many public keys on-chain, and some of them remain in use for
long periods of time. This increases the risk that long-exposed public keys
become attractive targets if quantum attacks on their corresponding private
keys become practical.

### Threat model: what breaks first in Cardano

The impact of a cryptographic break would not be the same across the system, so
the problem must be framed in terms of priority and system impact.

Signature schemes are the highest priority because they protect the root of
trust for transaction authorization and operational control. In Cardano, this
includes payment and staking keys, stake pool cold keys, and KES-based
block-signing keys. If they are broken, an adversary could forge
authorizations, move funds, or take control of critical operations. Since
public keys are exposed on-chain, long-lived keys are especially important
targets.

Verifiable Random Functions (VRFs) are critical for consensus security because
they are used for leader election and protocol randomness. If they are broken,
an adversary could bias or influence slot leadership and weaken the fairness
and security of consensus.

Delegation and stake authority are also critical because they determine how
stake is assigned and which stake pools act on its behalf. In Cardano, this
includes delegation certificates, stake credentials, and stake pool control
data. If they are broken, an adversary could redirect stake, alter control over
pool operations, or distort which pools are eligible to produce blocks.

The problem addressed by this CPS is therefore not only the future selection of
post-quantum primitives. It is the need to identify, prioritize, and frame the
cryptographic exposures of the Cardano settlement layer so that the ecosystem
can prepare a safe and coordinated migration path before it is forced into a
rushed response.

### What quantum attacks break

Quantum attacks do not affect all cryptographic primitives in the same way.
For this discussion, the two most important quantum algorithms are Shor's
algorithm and Grover's algorithm. They target different classes of
cryptographic assumptions and therefore lead to different kinds of migration
pressure.

Shor's algorithm is the most serious threat to the current Cardano settlement
layer because it attacks the mathematical assumptions behind widely deployed
public-key cryptography, including elliptic-curve cryptography. In practice,
this means that schemes based on these assumptions do not merely become weaker:
their security can collapse once a sufficiently capable quantum attacker
exists. In such a setting, public keys may become enough to recover the
corresponding private keys or to forge valid signatures.

At a high level, Shor's algorithm threatens public-key primitives such as
digital signatures, VRFs, aggregate signatures, and elliptic-curve-based proof
systems. In Cardano, this affects signature-based authorization,
VRF-based leader election, and protocols that rely on aggregated certificates
or elliptic-curve-based proofs.

Grover's algorithm affects a different class of primitives. It applies to
symmetric cryptography and hash-based constructions, such as hash functions
used throughout the protocol. Its impact is usually not a full break in the
same sense as Shor's algorithm. Instead, it reduces effective security levels,
which can often be addressed by stronger parameters, such as larger keys,
longer digests.

| Quantum algorithm  | Mainly affects                                      | High-level impact                                                 | Typical response                                               |
| ------------------ | --------------------------------------------------- | ----------------------------------------------------------------- | -------------------------------------------------------------- |
| Shor's algorithm   | Public-key cryptography                             | Can break the underlying security assumption                      | Replace vulnerable primitives with post-quantum alternatives   |
| Grover's algorithm | Symmetric cryptography and hash-based constructions | Reduces effective security levels rather than fully breaking them | Increase security parameters such as key sizes or digest sizes |

This helps explain why the threat model above gives higher priority to the
parts of the system that depend directly on public-key cryptography.

The same concern also appears in other important parts of the Cardano system.
Mithril relies on BLS-based aggregate signatures, while Ouroboros Leios, as
the next major consensus upgrade for Cardano, introduces aggregate-signature
certificates for endorser-block voting and certification. Zero-knowledge
systems that are already being integrated in the ecosystem may also rely on
elliptic-curve cryptography and would therefore be vulnerable to Shor's
algorithm. These examples show that the quantum threat is not limited to
today's settlement layer, but also affects important Cardano services and
future consensus designs.

## Overview of existing schemes
NIST has recently standardized several signature schemes that could be relevant to the migration of Cardano to PQC:

- ML-DSA: based on lattice problems (MLWE and MSIS). Rather large signatures (2.4KB) and key sizes (1.3KB) growing larger at more secure levels. Good efficiency both for signing (~0.65ms) and verification (~0.53ms) on average hardware. Prone to side-channel attacks due to its rejection sampling.
- FN-DSA: Based on NTRU lattices. Compact signatures (~690 bytes) and key sizes (~897 bytes), most size-efficient standardized PQC signature scheme. Moderate signing speed (~3.28ms) due to its Gaussian sampling. Gaussian sampling is also its main security weakness against side-channel attacks in the context of high-volume signing of Cardano stake pool operations.
- SLH-DSA: Based on hash function security (no new mathematical assumptions). Very large signatures (8KB to 50KB depending on parameters) with small key sizes (~32 bytes). Slow signing (~131.9ms) but fast verification. The most conservative and side-channel-friendly of the three schemes, as its security reduces entirely to well-understood hash function properties. Impractical for regular transaction signing in Cardano but well-suited to infrequently-used high-value keys such as governance credentials.

None of those standardized schemes offer a general solution which emphasize the need for agility when implementing the transition to PQC.

Some of the candidates for the second round of standardization:

- SQIsign: Based on isogenies, designed as a sigma protocol using Fiat-Shamir. Small signatures (~177 bytes) and public keys (~64 bytes). Signing remains slow despite recent improvements but the verification is fast. Good long-term candidate thanks to its size and native ZK structure, but need more study and improvements.
- FAEST: Security based on AES via a VOLEitH zero-knowledge proof of knowledge of an AES key. Signatures ~5–6 KB. Susceptible to side-channel attacks. Good candidate but still needs development and study.
- MAYO: Multivariate scheme based on the UOV (Unbalanced Oil and Vinegar) construction. Compact signatures (~300–500 bytes), constant-time-friendly implementation available. Strong non-lattice candidate with good sizes and low implementation complexity. Potential risk of breaks that happened before with multivariate schemes.

## Use Cases
<!-- A concrete set of examples written from a user's perspective, describing what and why they are trying to do. When they exist, this section should give a sense of the current alternatives and highlight why they are not suitable. -->

## Goals
<!-- A list of goals and non-goals a project is pursuing, ranked by importance. These goals should help understand the design space for the solution and what the underlying project is ultimately trying to achieve.

Goals may also contain requirements for the project. For example, they may include anything from a deadline to a budget (in terms of complexity or time) to security concerns.

Finally, goals may also serve as evaluation metrics to assess how good a proposed solution is. -->

## Open Questions
<!-- A set of questions to which any proposed solution should find an answer. Questions should help guide solutions design by highlighting some foreseen vulnerabilities or design flaws. Solutions in the form of CIP should thereby include these questions as part of their 'Rationale' section and provide an argued answer to each. -->

Quantum attacks and post-quantum cryptography are very active fields of study. The finalization of the first set of standards by the NIST happened less than two years ago and those schemes and their implementations are still under analysis by the community. The NIST is also continuing their standardization process to expend the number of standards, both for signatures and KEM. This poses the question of how and when to select the scheme that will be used to replace the current ones in Cardano.
With the advances in hardware and attacks, the move to post-quantum crytography cannot be delayed much longer but we need a thorough analysis of the existing schemes, standardized or not, to be sure to use the ones that fit our needs the most while being tested enough to give us confidence in using it.
Ultimately, the best solution for now would be to improve the cryptographic agility of Cardano and not commit to any particular scheme as the building block of the blockchain.

Below a non-exhaustive list of open questions that come at this stage:

- Given that we switch to newer PQ cryptography with sizable artifacts, how will this impact block propagation and general diffusion of messages?
- Given that we need to make room for sizable network messages, what flexibility remains in parameters such as `activeSlotsCoeff`?
- Given that the current PQ schemes are not battle tested, how can we remain flexible and agile in our design?

<!-- OPTIONAL SECTIONS: see CIP-9999 > Specification > CPS > Structure table -->

## Copyright

<!-- The CPS must be explicitly licensed under acceptable copyright terms. Uncomment the license you wish to use (delete the other one) and ensure it matches the License field in the header.

If AI/LLMs were used in the creation of the copyright text, the author may choose to include a disclaimer to describe their application within the proposal.
-->

<!-- This CPS is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode). -->
<!-- This CPS is licensed under [Apache-2.0](http://www.apache.org/licenses/LICENSE-2.0). -->
