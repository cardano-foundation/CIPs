---
CPS: ?
Title: Managing DRep Voting Power Concentration in Stake-Weighted Governance
Category: Meta
Status: Open
Authors:
    - Maureen Wepngong <maureen@giiyotech.com>
    - Danielle Stanko <danielle.stanko@iohk.io>
Proposed Solutions: []
Discussions:
    - Original pull request: - https://github.com/cardano-foundation/CIPs/pull/1211
Created: 2026-06-11
License: CC-BY-4.0
---

## Abstract

Stake-weighted voting models have a structural tendency to concentrate power over time — those with more voting power gain even more over time [1], and empirically, this leads to low voting participation where small holders cannot justify the cost of analyzing proposals when they perceive their vote to be powerless [2, 3]. The mitigations tend to require identity-based mechanisms that tie voting weight to verified entities rather than to stake alone [1]. Cardano governance, by design, does not rely on identity. This creates an open and unsolved question: can voting power concentration, voter apathy and principal-agent problems [4] be managed effectively in a stake-weighted governance system without identity? The risk of delegation being split across multiple credentials to circumvent any concentration mechanism remains a vulnerability that any proposed solution must consider in its design.

This CPS surfaces DRep voting power concentration as a priority governance challenge for Cardano and opens an investigation into whether Cardano's unique governance structure offers novel mechanisms — technical, social, or both — for managing concentration in the absence of identity. The CPS does not propose a specific solution; it frames the problem, surveys community discussions to date, and outlines the open questions any future solution must answer. It is connected to but distinct from CPS-020, which addresses DRep incentives. The two efforts must be coordinated so that incentive design does not work against concentration mitigation, or vice versa.

## Problem

Cardano's on-chain governance model gives Delegate Representatives (DReps) voting power proportional to delegated stake. This design has known centralizing tendencies that are now being observed in practice, although not to the extent seen in other DAOs, providing a window of opportunity to avoid severe voting power centralization among DReps in Cardano:

- Forum threads and polls from January through March 2025 (and continuing into 2026), governance roundtables in 2026, and off-chain sources like workshops, interviews and surveys from the Beyond Minimum Viable Governance project consistently surface community concern over top DReps holding disproportionate stake.
- The Nakamoto coefficient for DRep voting power has been declining, indicating that effective voting control is concentrating among fewer participants.
- Community polls have favored a 50M ADA saturation point over a hard numeric cap or a limit on the number of DReps, suggesting the community recognizes the problem but has not converged on a solution.

The deeper problem is structural. Stake-weighted voting tends to centralize over time, and common mitigation strategies such as quadratic voting must introduce identity to be effective against Sybil strategies [1], tying voting weight to verified entities rather than to stake alone.

Cardano governance does not use identity. The community may, in the future, reject identity-based mechanisms entirely.

This leaves an open question that has not been answered elsewhere: how, if at all, can a stake-weighted governance system manage power concentration without relying on identity and without compromising the skin-in-the-game benefit of stake-weighted voting? Waiting for identity to be implemented (and adopted) is not an adequate response, because:

- There is no guarantee the community will accept identity-based mechanisms.
- Concentration is beginning to occur now and may pose meaningful governance risks before any identity solution is ready.
- Cardano's governance structure (DReps, SPOs, CC, and the Constitution) may itself offer novel mechanisms that have not yet been explored. Most other models only have one voting body, and many do not offer delegation.
- Imperfect mechanisms may exist such as introducing costs, incentives, or frictions that discourage one entity from splitting into multiple DReps to avoid limits on single-DRep voting power, but have not yet been seriously considered.

This CPS opens an investigation into that question.

## Use Cases

**A long-term ADA holder wants to delegate to a DRep aligned with their values.**

Today, they open a DRep explorer that defaults to sorting by voting power. The DReps with the most voting power are the most visible. The holder, with limited time and no easy way to evaluate quality, picks from the top of the list. Their delegation reinforces the existing concentration. They would prefer a system that surfaces aligned DReps without defaulting to the largest, but no efficient mechanism exists.

**A small DRep with strong governance expertise wants to grow their delegation base.**

They publish rationales, vote consistently, and engage in community discussions. Despite this, their voting power remains low because new delegators are funneled through wallet UX and explorer defaults to the largest DReps. They observe that the system rewards size, not quality, and consider stopping their participation.

**A large DRep wants to voluntarily limit their own delegation to avoid contributing to concentration.**

They recognize that their accumulating voting power may be unhealthy for the system and would prefer to cap their delegation at a meaningful level, redirecting new delegators to smaller, equally capable DReps. However, DReps currently have no mechanism to refuse or limit delegation. They cannot self-cap. The only options available are to publicly discourage delegation (with no enforcement) or to stop participating entirely, both of which produce worse outcomes than the original problem.

**The community wants governance power to remain distributed.**

Several governance decisions and community actions suggest a preference for avoiding excessive concentration of governance power. The Constitution prohibits administrators from using treasury-controlled ADA to participate in governance through DRep delegation and establishes principles that discourage governance influence through custodially held assets. Large ecosystem actors have also taken different approaches to governance participation, including distributing delegation across multiple DReps, refraining from participating directly as DReps, or publicly acknowledging concentration concerns.

These examples demonstrate that many ecosystem participants recognize concentration as a governance risk and have attempted to mitigate it through voluntary actions, constitutional guardrails, or governance norms.

However, these measures do not address the underlying structural tendency for stake-weighted delegation to concentrate over time. They rely on continued voluntary compliance and provide limited protection if future participants choose not to follow the same norms.

## Goals

The goals of this CPS, ranked by importance:

1. **Establish DRep voting power concentration as a recognized priority problem in Cardano governance**, with shared understanding of its mechanics, current state, and structural drivers.

2. **Open investigation into mechanisms for managing concentration in a stake-weighted, identity-free governance system.** Solutions may be technical (protocol-level, application-level), social (community norms, social contracts such as the Cardano Constitution, coordination), or hybrid.

3. **Coordinate with CPS-020 (DRep incentives)** so that any concentration solution and any incentive solution are designed to be compatible. The two problems are connected: poorly designed incentives can worsen concentration, and poorly designed concentration limits can undermine incentives.

4. **Surface and address the structural concerns** that any proposed solution must navigate, including the risk of delegation being split across multiple credentials to circumvent caps, low-power DRep flooding, the role of explorer defaults, and risks to the quality of governance work.

## Existing Solution Directions

Community discussions to date have produced several recurring approaches for addressing DRep voting power concentration. While no consensus has emerged, these discussions help define the current solution space and identify areas requiring further investigation.

### DRep Saturation

One of the most frequently discussed approaches is DRep saturation, inspired by stake pool saturation. Under this model, a DRep would have a recommended or enforced voting power threshold, after which additional delegation would either become less effective or be redirected elsewhere.

Advocates argue that saturation could encourage broader distribution of voting power while preserving stakeholder choice. Critics note that any saturation mechanism may be vulnerable to circumvention through multiple DRep registrations unless accompanied by additional safeguards.

References:
- Delegation Saturation for DReps: https://forum.cardano.org/t/delegation-saturation-for-dreps/137589
- DRep Voting Power Saturation Research (Catalyst Fund 14): https://projectcatalyst.io/funds/14/cardano-open-ecosystem/drep-voting-power-saturation-research

### Hard Voting Power Caps

Another commonly proposed approach is imposing a maximum amount of voting power that any single DRep can control. Variants include fixed caps, dynamic caps, and protocol-enforced limits.

Supporters view caps as a direct method for preventing excessive concentration. Opponents argue that hard caps may undermine stake-weighted governance principles and may be ineffective if delegation can simply be split across multiple DRep identities.

References:
- Do You Think That a DRep's Voting Power Should Be Capped?: https://forum.cardano.org/t/do-you-think-that-a-dreps-voting-power-should-be-capped/142533
- Governance roundtable discussions on voting power concentration (2026)

### Delegation Discovery and Wallet UX Improvements

Some discussions focus on improving how delegators discover and evaluate DReps rather than restricting delegation directly. Suggestions include changing explorer ranking systems, highlighting rationale quality and participation rates, surfacing smaller DReps more prominently, and improving governance information available through wallets.

These approaches attempt to influence delegation behaviour through information and user experience rather than protocol-level constraints.

References:
- Beyond Minimum Viable Governance workshops, interviews, and surveys (2025–2026)
- Governance Health Working Group discussions
- Cardano governance roundtables (2026)

### Multi-DRep Delegation

Another proposed direction is allowing stakeholders to delegate voting power across multiple DReps rather than selecting a single representative.

Advocates argue this could naturally distribute voting power and reduce concentration. Open questions remain regarding usability, governance complexity, and whether users would meaningfully diversify their delegations in practice.

References:
- Governance roundtable discussions on voting power concentration (2026)
- Beyond Minimum Viable Governance workshops (2026)

### Institutional Delegation Strategies

Some proposals focus on the behaviour of large stakeholders rather than individual delegators. This includes encouraging ecosystem institutions, exchanges, and custodial providers to distribute delegations across multiple DReps.

The Cardano Foundation's current practice of spreading delegation across multiple DReps is frequently cited as an example of this approach.

References:
- Cardano Foundation Governance Delegation Strategy: https://cardanofoundation.org/blog/strengthens-commitment-governance-drep

### Incentive-Based Approaches

Some community members have proposed aligning DRep incentives, compensation mechanisms, or participation rewards with broader decentralization goals. These discussions recognize that concentration and incentive design are interconnected and should not be considered independently.

References:
- CPS-020 (DRep Incentives)
- Uniswap Delegate Reward Working Group: https://gov.uniswap.org/t/temp-check-uniswap-delegate-reward-3-months-cycle-1/23837

This CPS does not endorse any specific solution. Rather, it documents the primary approaches currently being discussed and highlights the questions that any future proposal should address.

## Open Questions

Any proposed solution (CIP, governance action, social standard, or other) responding to this CPS should address the following:

### On the Problem

1. What is the appropriate metric (or set of metrics) for "too much" concentration in Cardano DRep governance? Nakamoto coefficient? Gini? Saturation point? Some combination?
2. At what point does concentration become an active risk to governance integrity, rather than a long-term concern?
3. How do we account for the fact that some concentration may be legitimate (e.g., trusted institutional delegates and delegation that is concentrated but represents the will of the community), while other concentration may be problematic (e.g., a small number of entities controlling outcomes for their own benefit)?

### On Solutions Without Identity

4. Does Cardano's unique governance structure, including DReps, SPOs, the Constitutional Committee, and the Constitution itself, offer mechanisms for managing voting power concentration that other governance systems do not have?
5. Can saturation-based mechanisms, similar to the SPO K-parameter, be applied to DRep voting power? If so, what would they look like in practice? Saturation mechanisms may require wallet and explorer support so that users can understand when a DRep is approaching or has exceeded a recommended threshold and can easily discover alternative DReps. By contrast, hard caps could potentially be enforced at the ledger level, but may introduce different risks and trade-offs.
6. What role can wallet design, DRep explorers, and delegation interfaces play in distributing delegation more broadly without protocol-level changes? Are UX improvements and social mechanisms sufficient on their own, or are stronger interventions required? Specifically, should delegation tools prioritize factors such as participation rate, rationale quality, expertise, or consistency over voting power when presenting DReps to users?
7. How can large stakeholders, including exchanges, custodial wallets, and ecosystem institutions, be encouraged to support a more distributed governance ecosystem? Are voluntary delegation strategies sufficient, or should additional mechanisms be explored?
8. Should DReps have the ability to self-limit or refuse additional delegation once they reach a chosen threshold? Currently, DReps have no direct mechanism to discourage or prevent further delegation even when they believe additional concentration may be harmful to governance.
9. Could multi-DRep delegation, allowing delegators to split voting power across multiple DReps, materially improve voting power distribution? What effects might such a system have on governance participation, voter behaviour, and concentration metrics?
10. Without identity, any concentration mitigation mechanism may be vulnerable to multi-credential circumvention, where a single actor operates multiple DRep identities to bypass caps, saturation thresholds, or other concentration controls. What technical, economic, social, constitutional, or governance mechanisms could make such behaviour sufficiently costly, difficult, or unattractive?
11. Can constitutional norms, community standards, transparency requirements, or Constitutional Committee oversight play a meaningful role in discouraging multi-credential behaviour where protocol-level enforcement is not possible?
12. Before any governance or technical intervention is proposed, what modelling, simulations, or research should be conducted to understand the likely effects on delegation patterns, voter participation, governance quality, and power distribution?

### On Unintended Consequences

13. Could concentration mitigation reduce the quality of governance work, if smaller DReps lack the accountability, expertise or capacity of larger ones?
14. Does concentrated delegation represent the same risks as concentrated stake ownership in other models, or should different levels of concentration be tolerated for delegated voting power?
15. Does the stickiness of delegated voting power affect whether DRep concentration should be considered a governance risk in the same way as concentrated ADA ownership?
16. If delegators rarely change their delegation choices in practice, does concentrated DRep voting power create governance risks similar to concentrated stake holdings?
17. Conversely, if delegation patterns demonstrate meaningful movement over time, should concentration be viewed as less concerning because DReps remain accountable to their delegators through the ability to redelegate?

### On Coordination with CPS-020

18. Could payment for governance work (CPS-020) create voters who do the bare minimum to qualify for compensation, reducing rationale and vote quality? How should concentration mechanisms be designed to avoid amplifying this risk?
19. How should concentration mechanisms and incentive mechanisms be designed so they support rather than undermine each other?
20. Should solutions in both areas be sequenced (one first, then the other), or developed in parallel?
21. What governance body or working group should coordinate across both efforts?

## References

### Cardano Community Discussions

- "Do you think that a DRep's voting power should be capped?" — Cardano Forum poll and discussion: https://forum.cardano.org/t/do-you-think-that-a-dreps-voting-power-should-be-capped/142533
- "Delegation saturation for DReps" — Cardano Forum discussion: https://forum.cardano.org/t/delegation-saturation-for-dreps/137589
- "Cardano's Governance Game Problem and How to Solve It" — Coffee Pool analysis: https://coffeepool.jp/notes/cardanos-governance-game-problem-and-how-to-solve-it-eng/
- Cardano Foundation governance commitment and delegation strategy: https://cardanofoundation.org/blog/strengthens-commitment-governance-drep
- DRep Voting Power Saturation Research — Project Catalyst Fund 14: https://projectcatalyst.io/funds/14/cardano-open-ecosystem/drep-voting-power-saturation-research
- Cardano State of Governance Report 2026 (Beyond MVG project deliverable): https://drive.google.com/file/d/1INAVHFd8MSvitdQ6oKzxqdyLqx-jhGGu/view?usp=drive_link

### Related CPS / CIP Discussions

- CPS-020 (DRep incentives) — coordinated effort referenced throughout this CPS
- Governance tagging discussion in CIP repo: https://github.com/cardano-foundation/CIPs/issues/937#issuecomment-2575800139

### Cross-Ecosystem Research

- [1] "Concave is the New Linear: The Impossibility of Anti-Plutocratic DAO Governance": https://arxiv.org/html/2605.18990v1
- [2] Empirical study of DAO voting power and concentration (arXiv): https://arxiv.org/pdf/2204.01176
- [3] Gov/Acc research program: https://gov-acc.metagov.org/Phase-1-Results
- [4] "Fairness in Token Delegation: Mitigating Voting Power Concentration in DAOs": https://arxiv.org/html/2510.05830v2
- Uniswap Delegate Reward Working Group: https://gov.uniswap.org/t/temp-check-uniswap-delegate-reward-3-months-cycle-1/23837

## Copyright

This CPS is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
