---
CPS: "?"
Title: Multi-Node Feature Coordination
Category: Meta
Status: Open
Authors:
  - Adam Dean <adam@crypto2099.io>
Proposed Solutions: []
Discussions:
  - Original PR: https://github.com/cardano-foundation/CIPs/pull/?
Created: 2026-11-24
License: CC-BY-4.0
---

## Abstract

Cardano introduces new protocol features through hard forks, and since the
Plomin hard fork in January 2025 each hard fork has been enacted through a Hard
Fork Initiation governance action ([CIP-1694]). Six independent node
implementations now produce blocks. However, no defined process decides how a
proposed feature becomes a target for a future hard fork, how it is built and
tested across every implementation, or how each implementation acknowledges
that it is ready. This CPS aims to describe that missing pipeline and the
problems its absence causes for CIP authors, node implementers, and governance
participants.

## Problem

A protocol feature passes through five stages on its way to mainnet:

1. **Proposed:** the feature is described, usually in a CIP.
2. **Accepted:** the feature is chosen as a target for a specific hard fork.
3. **Built:** every node implementation implements the feature.
4. **Tested:** each implementation is shown to conform to the feature's
   specification.
5. **Ready:** each implementation team acknowledges that a release contains the
   full set of target features.

The CIP process covers the first stage, and on-chain governance covers the
switch that follows the last. [CIP-0001] states that the CIP process "does not
govern the process by which proposed changes to the Cardano protocol are
implemented and deployed." No document assigns the stages in between to
anyone.

When cardano-node was the only node implementation, the contents of its next
release were, in practice, the contents of the next hard fork. Blocks are now
produced on mainnet and public testnets by [cardano-node], [Amaru], [Dingo],
[Bean], [Tsunagi], and [Gerolamo]. Each team needs to know what the next hard
fork contains, which specification to build against, and when the work must be
finished.

### No Shared Target for Implementations

Without an agreed list of target features, an implementation team learns what
a hard fork contains by following the development of cardano-node. A team that
works this way starts late, may build against code rather than a stable
specification, and has no recognized point at which to raise implementation
cost or risk before the feature set is fixed. Every additional implementation
pays that cost again.

### Proposals Without a Path to a Hard Fork

A CIP for a protocol change can be merged, reviewed by the relevant enlisted
team, and still have no route to mainnet. [CIP-0001] states that "A positive
review by any enlisted project representative does not constitute a commitment
to implement the CIP. It is still the CIP author's responsibility to create an
implementation plan and identify implementors." Nothing selects among
`Proposed` CIPs, so an author cannot tell whether a proposal is waiting on
review, on a decision, or on nobody.

### Ratification Without a Defined Scope

Beyond the metadata anchor common to every governance action, a Hard Fork
Initiation action carries one item: "The new (greater) major protocol version"
([CIP-1694]). Its rationale may describe the features it enables, but nothing
ties that description to an agreed list. The [Cardano Constitution] requires
such actions to "undergo sufficient technical review and scrutiny as mandated
by the Guardrails" (Article II, Section 6). Its guardrails for the action cover
protocol version numbers, node upgrade levels, and new protocol parameters, and
none of them describes which features the hard fork enables.

Delegated representatives (DReps), stake pool operators (SPOs), and the
Constitutional Committee therefore ratify a version number whose contents were
chosen elsewhere, by no defined process, and with no shared record of which
implementations support it.

## Use Cases

### Proposing a Feature

* In 2020 [CIP-0001] defined the CIP process. [CIP-0035] in 2022 and
  [CIP-0084] in 2023 defined review processes for the Plutus and Ledger
  categories.
* In 2022 [CIP-0035] noted that "The requirement to propose a change via a CIP
  is, as all CIPs are, advisory." In exceptional circumstances a change may
  reach a hard fork without a CIP and be recorded in a retrospective CIP after
  the fact.

There is no single place to see every candidate feature for a future hard
fork, whether it began as a CIP, as research, or as a change in one
implementation.

### Accepting a Feature for a Hard Fork

* In 2022 [CIP-0059] defined the terms for ledger eras and intra-era hard
  forks. Its feature table records what past hard forks contained, not how
  their contents were chosen.
* Between 2024 and 2025, [CIP-0152], [CIP-0167], [CIP-0176], and [CIP-0178]
  each named the Dijkstra era hard fork as their release target. No document
  in this repository records the scope of that hard fork, which CIPs it
  includes, or how that list was agreed.
* In 2025 and 2026, [CIP-0163] and [CIP-0207] wrote their own pipeline into
  their Acceptance Criteria, in nearly identical wording: "Endorsement by
  Technical Bodies", "Stakeholder Concurrence", and "Governance Ratification".
  Each names two committees as endorsers. The path is defined within each CIP,
  and nothing obliges the named committees to follow it.

There is no defined point at which a feature becomes a target for a specific
hard fork, no record of who agreed to it, and no defined way to defer or remove
a feature once it is targeted.

### Building Across Implementations

* In January 2026 [CIP-0001] was amended so that a protocol CIP becomes
  `Active` by "being live on the Cardano mainnet within one or more
  implementations".
* In 2025 [CIP-0167] and [CIP-0176] set their implementation criterion as the
  feature being "integrated into cardano-node" and "released as part of the
  Dijkstra era hard fork". No other implementation is named.
* In 2025 [CIP-0164] listed "Implement / integrate necessary changes to
  `cardano-node` and other node implementations" in its Implementation Plan.
  It defines no way for those other implementations to commit to the work.

Implementation teams have no defined way to commit to a feature, report
progress on it, or raise its implementation cost and risk before it is
accepted.

### Testing and Conformance

* In 2025 [CIP-0164] planned "node-level, but implementation-independent
  conformance test suites" for Leios, and [CIP-0165] proposed a canonical
  ledger state that would allow "full conformance testing".
* In 2026 [CPS-0034] set out the need for Plutus Core conformance: "For
  Cardano's node diversity, it is vital that the Plutus Core evaluators in all
  node implementations produce identical results." Its scope is Plutus
  evaluation only.

No conformance suite is defined for each hard fork across the ledger,
consensus, and network layers. No document assigns responsibility for
maintaining such a suite, and no test result is tied to a feature's inclusion.

### Acknowledging Readiness

* In 2022 [CIP-1694] made Hard Fork Initiation a governance action that
  "requires a prior software upgrade", and noted that a hard fork "requires
  coordination between stake pool operators, wallet providers, DApp developers,
  and the node release team".
* In 2026 [CPS-0036] and [CIP-0203] described how a block producer can report
  its software in the block header, including "readiness for an upcoming hard
  fork". Reporting is voluntary and describes what an operator runs, not
  whether an implementation conforms.

There is no defined way for an implementation team to declare that a release
contains the full set of target features and passes its conformance tests, or
for governance participants to check that declaration before they vote.

The ecosystem coordination that follows implementation readiness, such as SPO,
exchange, and tooling upgrades and the timing of the governance action, already
takes place before each hard fork and is outside the scope of this CPS.
Implementation readiness is the input that coordination depends on.

We welcome additional or expanded use cases to be added to this section.

## Goals

A solution to this CPS should, in order of importance:

- [ ] Define how a feature is accepted as a target for a specific hard fork,
      and how a targeted feature is deferred or removed, with each decision and
      its reasons recorded publicly.
- [ ] Give node implementation teams a defined part in that decision, so that
      implementation cost and risk are known before a feature is accepted.
- [ ] Keep one public list of candidate and accepted features for future hard
      forks, whatever their origin.
- [ ] Require an implementation-independent specification for each accepted
      feature, stable enough for every implementation to build against.
- [ ] Require conformance tests for each accepted feature that every
      implementation can run, with a defined passing result.
- [ ] Let each implementation team declare that a release contains the full set
      of target features and passes its conformance tests, in a form others can
      verify.
- [ ] Let governance participants see which features a Hard Fork Initiation
      enables, and which implementations have declared readiness, before they
      vote.
- [ ] Apply equally to intra-era hard forks and to new eras.

This CPS does not aim to:

* replace or redefine the ecosystem coordination that precedes each hard fork;
* prescribe how any implementation team organizes its own development;
* change the ratification thresholds of [CIP-1694].

## Open Questions

1. Must every protocol change that requires a hard fork begin as a CIP, and
   where are candidate features from other origins recorded?
2. Who decides that a feature is accepted for a specific hard fork, and how are
   implementation teams, CIP editors, and governance participants represented
   in that decision?
3. When is the set of target features for a hard fork fixed, and how is a
   feature added, deferred, or removed after that point?
4. What must a specification contain before implementation teams are expected
   to build against it, and who maintains it when an implementation finds it
   ambiguous or wrong?
5. Who owns the conformance tests for the ledger, consensus, network, and
   Plutus layers, and what result counts as passing?
6. Can a hard fork proceed when one or more implementations have not completed
   the set of target features, and if so, what threshold is enough?
7. How does an implementation team declare readiness, and how can others
   verify it?
8. How should a Hard Fork Initiation action be tied to the set of target
   features it enables, so that voters know what they ratify?
9. How does the pipeline handle a change that cannot wait for it, such as a
   security fix that requires a hard fork?
10. How is implementation work across several independent teams funded?

## Acknowledgements

This CPS was drafted with the assistance of AI, using Claude Opus 5.5.

## Copyright

This CPS is licensed under [CC-BY-4.0].

[CC-BY-4.0]: https://creativecommons.org/licenses/by/4.0/legalcode

[CIP-0001]: https://github.com/cardano-foundation/CIPs/tree/master/CIP-0001

[CIP-0035]: https://github.com/cardano-foundation/CIPs/tree/master/CIP-0035

[CIP-0059]: https://github.com/cardano-foundation/CIPs/tree/master/CIP-0059

[CIP-0084]: https://github.com/cardano-foundation/CIPs/tree/master/CIP-0084

[CIP-0152]: https://github.com/cardano-foundation/CIPs/tree/master/CIP-0152

[CIP-0163]: https://github.com/cardano-foundation/CIPs/tree/master/CIP-0163

[CIP-0164]: https://github.com/cardano-foundation/CIPs/tree/master/CIP-0164

[CIP-0165]: https://github.com/cardano-foundation/CIPs/tree/master/CIP-0165

[CIP-0167]: https://github.com/cardano-foundation/CIPs/tree/master/CIP-0167

[CIP-0176]: https://github.com/cardano-foundation/CIPs/tree/master/CIP-0176

[CIP-0178]: https://github.com/cardano-foundation/CIPs/tree/master/CIP-0178

[CIP-0203]: https://github.com/cardano-foundation/CIPs/tree/master/CIP-0203

[CIP-0207]: https://github.com/cardano-foundation/CIPs/tree/master/CIP-0207

[CIP-1694]: https://github.com/cardano-foundation/CIPs/tree/master/CIP-1694

[CPS-0034]: https://github.com/cardano-foundation/CIPs/tree/master/CPS-0034

[CPS-0036]: https://github.com/cardano-foundation/CIPs/tree/master/CPS-0036

[Cardano Constitution]: https://github.com/IntersectMBO/cardano-constitution/blob/main/cardano-constitution-2/cardano-constitution-2.txt.md

[cardano-node]: https://github.com/IntersectMBO/cardano-node

[Amaru]: https://github.com/pragma-org/amaru

[Dingo]: https://github.com/blinklabs-io/dingo

[Bean]: https://bean.zw3rk.com/

[Tsunagi]: https://github.com/cryptoleo79/tsunagi-preview

[Gerolamo]: https://github.com/HarmonicLabs/gerolamo
