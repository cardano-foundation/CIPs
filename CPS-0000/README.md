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

## Use Cases
<!-- A concrete set of examples written from a user's perspective, describing what and why they are trying to do. When they exist, this section should give a sense of the current alternatives and highlight why they are not suitable. -->

## Goals
<!-- A list of goals and non-goals a project is pursuing, ranked by importance. These goals should help understand the design space for the solution and what the underlying project is ultimately trying to achieve.

Goals may also contain requirements for the project. For example, they may include anything from a deadline to a budget (in terms of complexity or time) to security concerns.

Finally, goals may also serve as evaluation metrics to assess how good a proposed solution is. -->

## Open Questions
<!-- A set of questions to which any proposed solution should find an answer. Questions should help guide solutions design by highlighting some foreseen vulnerabilities or design flaws. Solutions in the form of CIP should thereby include these questions as part of their 'Rationale' section and provide an argued answer to each. -->
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
