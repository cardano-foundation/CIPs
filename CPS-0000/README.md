---
CPS: ?
Title: Quantum secure Cardano settlement layer
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

## Problem
Cardano relies on public-key cryptography for transaction authorization,
delegation, stake pool operations, and consensus-critical functions. The
security of the settlement layer therefore depends on cryptographic primitives
that were designed against classical attackers and may not remain secure
against sufficiently capable quantum attackers.

### Context: why this matters now

Quantum hardware continues to progress. More importantly, the estimated
resources needed to attack currently deployed public-key cryptography continue
to decrease. This reduces confidence in long safety margins and suggests that
practical attacks may arrive earlier than previously expected.

This matters at the Cardano settlement layer because migration of base-layer
cryptography is slow and coordination-heavy. Any change in this area affects
ledger rules, consensus, node implementations, wallets, stake pool operators,
exchanges, and other ecosystem participants. It also requires broad community
alignment and careful rollout planning. As a result, Cardano cannot wait until
the risk becomes immediate before preparing a migration path.

Cardano also exposes many public keys on-chain, and some of them remain valid
for long periods of time. This creates a "harvest now, exploit later" risk:
keys visible today may become useful targets if current cryptographic
assumptions weaken in the future.

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

<!-- OPTIONAL SECTIONS: see CIP-9999 > Specification > CPS > Structure table -->

## Copyright
<!-- The CPS must be explicitly licensed under acceptable copyright terms. Uncomment the license you wish to use (delete the other one) and ensure it matches the License field in the header.

If AI/LLMs were used in the creation of the copyright text, the author may choose to include a disclaimer to describe their application within the proposal.
-->

<!-- This CPS is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode). -->
<!-- This CPS is licensed under [Apache-2.0](http://www.apache.org/licenses/LICENSE-2.0). -->
