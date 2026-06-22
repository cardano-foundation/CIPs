---
CPS: ?
Title: DRep Voting Power Concentration
Category: Tools
Status: Open
Authors:
    - Maureen Wepngong <maureen@giiyotech.com>
    - Danielle Stanko <danielle.stanko@iohk.io>
Proposed Solutions: []
Discussions:
    - Original PR: https://github.com/cardano-foundation/CIPs/pull/1211
Created: 2026-06-11
License: CC-BY-4.0
---

## Abstract

Stake-weighted voting models have a structural tendency to concentrate power over time, where those with more voting power tend to gain even more over time, [^1], and empirically, this leads to low voting participation where small holders cannot justify the cost of analyzing proposals when they perceive their vote to be powerless [^2][^3]. The mitigations tend to require identity-based mechanisms that tie voting weight to verified entities rather than to stake alone [^1]. Cardano governance, by design, does not rely on identity. This creates an open and unsolved question: can voting power concentration, voter apathy and principal-agent problems [^4] be managed effectively in a stake-weighted governance system without identity? The risk of delegation being split across multiple credentials to circumvent any concentration mechanism remains a vulnerability that any proposed solution must consider in its design.

This CPS surfaces DRep voting power concentration as a priority governance challenge for Cardano and opens an investigation into whether Cardano's unique governance structure offers novel technical mechanisms for managing concentration in the absence of identity. The CPS does not propose a specific solution; it frames the problem, surveys community discussions to date, and outlines the open questions any future CIP responding to this CPS should answer. It is connected to but distinct from CPS-0020, which addresses DRep incentives. The two efforts must be coordinated so that incentive design does not work against concentration mitigation, or vice versa.

## Problem

Cardano's on-chain governance model gives Delegate Representatives (DReps) voting power proportional to delegated stake. The current ledger rules place no upper bound on the amount of stake that can be delegated to a single DRep credential, and the current CIP-0119 DRep registration metadata standard contains no fields that allow wallets or explorers to surface saturation, distribution, or activity signals to delegators at the point of choice. This design has known centralizing tendencies that are now being observed in practice, although not to the extent seen in other DAOs, providing a window of opportunity to avoid severe voting power centralization among DReps in Cardano:

- Forum threads and polls from January through March 2025 (and continuing into 2026), governance roundtables in 2026, and off-chain sources like workshops, interviews and surveys from the Beyond Minimum Viable Governance project consistently surface community concern over top DReps holding disproportionate stake.
- The Nakamoto coefficient for DRep voting power has been declining, indicating that effective voting control is concentrating among fewer participants.
- Community discussions have explored approaches such as saturation points, voting power caps, and delegation distribution mechanisms, suggesting the community recognizes the problem but has not converged on a technical solution.

The deeper problem is structural. Stake-weighted voting tends to centralize over time, and common mitigation strategies such as quadratic voting must introduce identity to be effective against multi-credential circumvention [^1], tying voting weight to verified entities rather than to stake alone.

Cardano governance does not use identity. The community may, in the future, reject identity-based mechanisms entirely.

This leaves an open question that has not been answered elsewhere: how, if at all, can a stake-weighted governance system manage power concentration without relying on identity and without compromising the skin-in-the-game benefit of stake-weighted voting? Waiting for identity to be implemented (and adopted) is not an adequate response, because:

- There is no guarantee the community will accept identity-based mechanisms.
- Concentration is beginning to occur now and may pose meaningful governance risks before any identity solution is ready.
- Cardano's governance architecture, including DReps and SPOs, may offer novel technical mechanisms that have not yet been explored. Most other models only have one voting body, and many do not offer delegation.
- Imperfect mechanisms may exist such as introducing costs, incentives, or frictions that discourage one entity from splitting into multiple DReps to avoid limits on single-DRep voting power, but have not yet been seriously considered.

This CPS opens an investigation into that question.

Community discussions to date have explored several broad directions, including saturation mechanisms, voting power caps, delegation distribution mechanisms, wallet UX interventions, and incentive-based approaches. No clear consensus has emerged, motivating the need for a structured investigation of the problem space.

## Use Cases

**A long-term ADA holder wants to delegate to a DRep aligned with their values.**

Today, they open a DRep explorer that defaults to sorting by voting power. The DReps with the most voting power are the most visible. The holder, with limited time and no easy way to evaluate quality, picks from the top of the list. Their delegation reinforces the existing concentration. They would prefer a system that surfaces aligned DReps without defaulting to the largest, but no protocol-supported mechanism exists.

**A small DRep with strong governance expertise wants to grow their delegation base.**

They publish rationales, vote consistently, and engage in community discussions. Despite this, their voting power remains low because new delegators are funneled through wallet UX and explorer defaults to the largest DReps. They observe that the system rewards size, not quality, and consider stopping their participation.

**A large DRep is concerned about contributing to concentration.**

A large DRep is concerned that continued growth in delegated voting power may contribute to concentration. However, there is currently no protocol-supported mechanism for communicating delegation preferences or influencing future delegation behavior.

**A delegator wants to distribute stake across multiple DReps.**

A delegator wants to spread their stake across multiple DReps to avoid contributing to any single DRep's accumulation. Multi-DRep delegation flows are not defined at the ledger or wallet standard level. Each wallet implements delegation independently, and most surface a single-DRep model only.

**A wallet wants to surface saturation information to delegators.**

A wallet wants to surface information to delegators about a DRep's current level of delegated voting power relative to a preferred or recommended threshold. There is currently no protocol-defined signal indicating whether a DRep has reached a preferred or recommended level of delegated voting power. The wallet therefore has no protocol-supported data on which to base such a UI.

## Goals

The goals of this CPS, ranked by importance:

1. **Establish DRep voting power concentration as a recognized technical problem** in the Cardano protocol and standards ecosystem, with shared understanding of which technical artifacts (ledger rules, metadata standards, and wallet behavior) contribute to it and could address it.

2. **Open investigation into protocol-level and standards-level mechanisms** for managing concentration in a stake-weighted governance system that does not use identity. Mechanisms under investigation may include ledger rule changes (saturation curves, self-cap signaling at the credential level), metadata extensions (CIP-0119 successors defining optional saturation or distribution fields), and wallet and explorer behavior standards.

3. **Coordinate with CPS-0020 (DRep incentives)** so that any concentration solution and any incentive solution are designed to be compatible. The two problems are connected: poorly designed incentives can worsen concentration, and poorly designed concentration limits can undermine incentives.

4. **Surface and address the technical vulnerabilities** any solution must navigate, including the risk that any cap or saturation mechanism is circumvented by splitting delegation across multiple DRep credentials, and the risk that wallet and explorer defaults continue to undo any protocol-level mitigation.

5. **Provide a technical reference point** for future CIPs in the Ledger, Wallets, Metadata, and Meta categories that propose specific solutions to the problem framed here.

## Open Questions

Any proposed CIP responding to this CPS should address the following:

### On the Problem

- What is the appropriate metric (or set of metrics) for "too much" concentration in Cardano DRep governance? Nakamoto coefficient? Gini? Saturation point? Some combination?
- At what point does concentration become an active risk to governance integrity, rather than a long-term concern?
- How do we account for the fact that some concentration may be legitimate (e.g., trusted institutional delegates and delegation that is concentrated but represents the will of the community), while other concentration may be problematic (e.g., a small number of entities controlling outcomes for their own benefit)?
- Before any technical intervention is proposed, what modelling, simulations, or research should be conducted to understand the likely effects on delegation patterns, voter participation, governance quality, and power distribution?

### On Ledger-Level Mechanisms

- Can the ledger introduce a saturation curve on DRep voting weight, modeled on the SPO K-parameter? What is the appropriate functional form (linear taper, exponential, threshold-based)?
- What is the appropriate saturation parameter value, and how should it be modeled against current and projected ADA distribution?
- Should a DRep credential be able to declare an on-chain self-cap at registration or update time, and have it enforced by the ledger?
- Should the ledger enforce a hard upper bound on delegation to a single DRep credential, or rely on saturation curves only?
- How does any ledger-level mechanism interact with the existing delegation lifecycle (registration, update, retirement) defined in the Conway era?

### On DRep Metadata (CIP-0119 and Successors)

- Should CIP-0119 be extended with optional metadata fields for a self-declared delegation cap or saturation preference, even before any ledger enforcement exists?
- Should CIP-0119 include fields that wallets can use to surface activity signals (rationale rate, voting record completeness, recent participation)?
- Should CIP-0119 include a field for the DRep to signal that they are closed to new delegation?

### On Wallet and Explorer Standards

- Should a CIP define wallet UI standards for surfacing saturation, alternative DReps, or delegation distribution warnings at the point of one-click delegation?
- Should a CIP define standards for DRep explorer sort and filter dimensions so that voting power is not the only or default ordering, for example surfacing participation rate, rationale quality, or consistency instead?
- Should multi-DRep delegation flows be defined as a wallet standard, so that delegators can distribute stake across multiple DReps from within their wallet?

### On Multi-Credential Circumvention

- Without identity, any cap or saturation mechanism can be circumvented by splitting delegation across multiple DRep credentials. What economic or structural mechanisms (deposits, registration cost, on-chain proof of activity) can raise the cost of multi-credential circumvention enough to make any cap or saturation mechanism meaningful?
- How can any saturation or cap mechanism avoid creating an incentive to flood the system with many small DRep credentials?

### On Unintended Consequences

- Could concentration mitigation reduce the quality of governance work, if smaller DReps lack the accountability, expertise, or capacity of larger ones?
- Could payment for governance work (CPS-0020) create voters who do the bare minimum to qualify for compensation, reducing rationale and vote quality? How should concentration mechanisms be designed to avoid amplifying this risk?
- How should concentration mechanisms and incentive mechanisms (CPS-0020) be designed so they support rather than undermine each other?
- Should solutions in both areas be sequenced or developed in parallel?

## References

### Cardano Community Discussions

- [Do you think that a DRep's voting power should be capped?](https://forum.cardano.org/t/do-you-think-that-a-dreps-voting-power-should-be-capped/142533) - Cardano Forum poll and discussion
- "Delegation saturation for DReps" Cardano Forum discussion: https://forum.cardano.org/t/delegation-saturation-for-dreps/137589
- [Cardano's Governance Game Problem and How to Solve It](https://coffeepool.jp/notes/cardanos-governance-game-problem-and-how-to-solve-it-eng/) - Coffee Pool analysis
- Cardano Foundation governance commitment and delegation strategy: https://cardanofoundation.org/blog/strengthens-commitment-governance-drep
- DRep Voting Power Saturation Research, Project Catalyst Fund 14: https://projectcatalyst.io/funds/14/cardano-open-ecosystem/drep-voting-power-saturation-research
- Cardano State of Governance Report 2026 (Beyond MVG project deliverable): https://drive.google.com/file/d/1INAVHFd8MSvitdQ6oKzxqdyLqx-jhGGu/view?usp=drive_link

### Related CPS / CIP Discussions

- CPS-0020 (DRep incentives), coordinated effort referenced throughout this CPS
- Governance tagging discussion in CIP repo: https://github.com/cardano-foundation/CIPs/issues/937#issuecomment-2575800139

### Cross-Ecosystem Research

- Uniswap Delegate Reward Working Group: https://gov.uniswap.org/t/temp-check-uniswap-delegate-reward-3-months-cycle-1/23837

[^1]: "Concave is the New Linear: The Impossibility of Anti-Plutocratic DAO Governance" https://arxiv.org/html/2605.18990v1

[^2]: Empirical study of DAO voting power and concentration (arXiv) https://arxiv.org/pdf/2204.01176

[^3]: Gov/Acc research program https://gov-acc.metagov.org/Phase-1-Results

[^4]: "Fairness in Token Delegation: Mitigating Voting Power Concentration in DAOs" https://arxiv.org/html/2510.05830v2

## Copyright

This CPS is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
