---
CIP: 163
Title: Time-Bound Delegation
Category: Ledger
Status: Proposed
Authors:
  - Ryan Wiley <rian222@gmail.com>
Implementors: []
Discussions:
  - Original PR: https://github.com/cardano-foundation/CIPs/pull/1077
Created: 2025-08-15
License: CC-BY-4.0
---

## Abstract

Cardano’s staking and on‑chain voting have drifted toward passivity. As described in CPS-0022, long‑lived “set‑and‑forget” delegations let rewards and governance weight ossify, particularly in wallets that have been permanently lost, diluting staking rewards and voting power for engaged participants and harming network security. This CIP reframes delegation as an **active, periodically affirmed contribution to network security** and realigns incentives so rewards flow to those presently able to participate. It introduces **reward-account liveness with inactivity expiry**, with proof-of-life via any witness-bearing action on the staking credential.

This change encourages ongoing engagement and reduces sticky/lost‑stake externalities while respecting user property rights. Reward-account expiry changes eligibility for block production, rewards, and governance participation; it leaves the existing reward-distribution rules in place.

## Motivation: Why is this CIP necessary?

Many users interpret staking rewards as akin to bank interest. If that were the intent, the ledger would not need operator selection, delegation, or performance‑based rewards. Yield could simply accrue automatically. In Cardano, **staking is voluntary and active**. It is how the protocol decides who gets to make blocks, and rewards compensate the combination of (a) **committing stake** to secure the network and (b) **selecting and monitoring** a competent, honest operator. "On a high level, the goal of the incentives mechanism is to incentivize stakeholders to follow the protocol and thereby to guarantee the secure and efficient operation of Cardano" (SL‑D5 §5.1)

- Delegation is a liquid vote for a pool operator. Delegators are expected to reevaluate and move if performance, fees, or behavior change.
- Lost or inactive stake no longer contributes to present‑day security yet can lock in block‑production influence and siphon rewards from active participants.

This CIP addresses the broader drift toward **passive and indifferent delegations.** Securing the network is an **active act**, periodically affirmed by the holder, and rewarded accordingly. Reward-account inactivity introduces a light-touch **proof-of-life** via any witness-bearing action on the staking credential, covering both stake pool and dRep participation.

## Specification

#### Current behavior (for context)

- **Indefinite delegations.** Delegation certificates today have no expiry. Once a stake credential delegates to a stake pool or a dRep, that delegation remains valid indefinitely until the holder submits a new delegation (or deregisters the stake key).
- **Rewards return-to-reserves.** After monetary expansion and fees are combined and the treasury cut is taken, the distributable rewards pot is scaled by the network’s active‑stake ratio; only that fraction is paid out, and the remainder is returned to reserves. This occurs because rewards are computed using only the active stake snapshot and any residual R not assigned to reward accounts (∆r₂ = R − Σrs) is returned to reserves, per the epoch‑boundary and reward‑update rules (SL‑D5 §11.1, §11.5, §11.8–§11.10).

This CIP intentionally limits itself to reward-account inactivity expiry and its effects on eligibility. The reward formula and residual-return rules, pledge influence, saturation, and treasury cut are unchanged. Adoption of Dynamic Rewards is not required.

### Reward-account inactivity expiry (proof-of-life)

- Add a **single protocol parameter** (measured in epochs), to be set via governance:
  - `delegatorActivity`
- **Scope & terminology.** A *reward account* (i.e., staking credential) is the object that delegates, accrues, and withdraws rewards. The ledger maintains an `expirationEpoch` for each registered reward account.
- **Inactivity rule.** During epoch transitions, when stake and voting power are computed, **expired reward accounts** (those with `expirationEpoch < currentEpoch`) are **ignored** for pool leader election, rewards distribution, and governance tallying.
- **Proof-of-life.** Any action that requires a **witness by the reward account** resets its expiration to `currentEpoch + delegatorActivity`. Examples include: reward withdrawal, (re)delegation to an SPO, (re)delegation to a dRep, and stake-key registration or deregistration. (Wallets commonly withdraw rewards when submitting any transaction, so ordinary usage renews automatically.)
- **Ineligible for rewards.** For epochs in which a reward account is inactive, its epoch reward share is **not credited** to that account. The existing reward-distribution rules, including the return of undistributed residual rewards to reserves, continue to apply. This CIP does not redistribute those uncredited rewards to other accounts.
- **Migration.** On activation, determine the epoch that the last witness occurred for each reward account. Then initialize each account's `expirationEpoch` to that epoch plus `delegatorActivity`.

**Note:** The initial numeric value for `delegatorActivity` is intentionally **left undefined** here and will be chosen through community governance and deliberation. Potential jittering or lottery mechanisms to stagger per-epoch expiries are not mentioned in this proposal, but may be considered separately if operational data warrants it.

### Activity-period terminology

`delegatorActivity` names the period, measured in epochs, for which a reward account remains active after a qualifying witness. The name follows the existing DRep activity-period parameter, called `drepActivity` in [CIP-1694’s Registered DReps section](../CIP-1694/README.md#registered-dreps) and `dRepActivity` in the [ledger implementation](https://github.com/IntersectMBO/cardano-ledger/blob/master/eras/conway/impl/src/Cardano/Ledger/Conway/PParams.hs). It is also consistent with the proposed `spoActivity` parameter in [CIP-0193? | Auto-retirement of Abandoned Pools](https://github.com/cardano-foundation/CIPs/pull/1230). These parameters all describe activity periods renewed by qualifying actions; their qualifying actions and expiry rules remain specific to their respective proposals.

## Rationale: How does this CIP achieve its goals?

- **Active security & correct economics.** Periodic renewal makes delegation an affirmative act of securing the network. Engaged holders are compensated for informed operator selection, not mere passage of time.
- **Mitigate sticky stake.** Long‑dormant delegations can prop up legacy control of block production. Expirations reduce that inertia by requiring a simple, periodic affirmation from real, reachable owners.
- **Curbing ossification & compounding.** Expirations prevent unreachable wallets from indefinitely accumulating rewards or voting power without threatening their principal investment.
- **Respect for property.** No seizure or clawback occurs. Inactive accounts simply stop earning until the account becomes active again.
- **Governance clarity.** Because expired reward accounts contribute zero voting power, governance power reflects currently affirmed participation (CIP-1694’s “inactive dRep” guardrails remain complementary but insufficient on their own).
- **Sharper SPO accountability.** Periodic renewal nudges delegators to review operator fees, performance, and conduct. If a pool underperforms or raises costs, stake can organically reallocate on renewal.
- **Fairer path for new pools.** Expirations free stake that would otherwise remain inert with incumbents, reducing entrenched advantages from lost delegations and lowering barriers for competent new operators to attract delegation.

### Security consideration: participation shocks after large expirations

Introducing inactivity expiry could, in the short term, allow portions of stake to lapse if large wallets forget or delay renewal. This temporarily reduces the **active‑stake ratio**, widening the gap between total and active stake. In such windows, the cost for an adversary to assemble a large share of active stake is lower than usual, and block production can concentrate among a smaller set of pools until new delegations occur.

This risk must be assessed for time-bound delegation on its own. Its activation does not require the potential balancing mechanism described below.

### Relationship to Dynamic Rewards

The companion **Dynamic Rewards** proposal is being extracted from the [original CIP-163 discussion](https://github.com/cardano-foundation/CIPs/pull/1077). It redistributes rewards associated with inactive and capped-out stake using performance-adjusted capped weights, while retaining the pledge-dependent reward expression and failed-pledge withholding. Oversaturated pools can share through their capped portion, and separately governed changes to k or an adopted CIP-50 L can shift rewards toward less-saturated pools. The two proposals can be reviewed, ratified, and activated independently.

If both proposals are adopted, time-bound delegation limits eligibility to reward accounts with a qualifying witness within their activity period, while Dynamic Rewards normalizes rewards over the remaining performance-adjusted capped weights. This can increase rewards for reachable participants when other stake expires, providing an incentive for delegation to return. The pledge-dependent reward expression, failed-pledge withholding, and final accounting rules still apply. This potential balancing effect is conditional on the separate adoption of Dynamic Rewards; time-bound delegation alone does not provide it.

## Path to Active

### Acceptance Criteria

- **CIP Editor Approval** – Cardano CIP Editors must confirm that the specification is complete, unambiguous, and internally consistent with existing CIPs.
- **Consensus on initial parameter value** – An initial value for the new protocol parameter `delegatorActivity` in epochs must be agreed upon before hard-fork combinator (HFC) activation. The choice should consider operational viability, empirical analyses, and community feedback.
- **Endorsement by Technical Bodies** – The Cardano Parameter-Change Proposals (PCP) Committee and the Intersect Technical Steering Committee (TSC) should both recommend the proposal as technically sound and aligned with the protocol’s long-term roadmap.
- **Stakeholder Concurrence** – A majority of stake pool operators (SPOs), ecosystem tooling maintainers, dReps, and other infrastructure providers must signal readiness to upgrade.
- **Governance Ratification** – The on-chain Hard-Fork Governance Action must pass the requisite dRep and Constitutional Committee thresholds, establishing legal-constitutional legitimacy and stakeholder support for the change.

### Implementation Plan

- **Community Deliberation (Preparation Phase)**
  - Publish the finalized CIP revision and present it to the PCP committee, TSC, CIP Editors, and wider community channels (Discord, X, Cardano Forum, etc.).
  - Collect structured feedback, particularly on candidate values for `delegatorActivity`, and iterate until broad technical consensus emerges.
- **Specification & Code Integration (Development Phase)**
  - Once the initial parameter value is determined, integrate reward-account inactivity expiry, the corresponding stake and voting eligibility rules, and governance support for the new parameter into cardano-node and related libraries (ledger, CLI, wallet APIs).
  - Submit pull requests to the canonical repositories; obtain code reviews from IOG, CF, and community contributors.
  - Release a new protocol version that includes the changes made in this CIP.
  - Use a dedicated pre-production testnet that mirrors main-net parameters but enforces the new changes, allowing SPOs and exchanges to test end-to-end flows.
- **Readiness Sign-off (Testing Phase)**
  - Require at least two weeks of uninterrupted testnet stability plus green results from regression and property-based tests.
  - Monitor ecosystem dApps and tooling to confirm that major node implementations, explorers, wallets, and exchange integrations support the new rule set.
- **On-chain Governance (Ratification Phase)**
  - File the Hard-Fork Governance Action on-chain with the agreed initial parameter value tagged for the next hard fork event.
  - Modify the existing Cardano Constitution to include definitions and guardrails for the new protocol parameter and have it ratified by the tripartite government of Cardano.
  - Mobilize dRep outreach to ensure quorum and super-majority passage; concurrently, the Constitutional Committee validates procedural compliance.
- **Hard-Fork Activation (Deployment Phase)**
  - Upon successful vote, the hard fork event is automatically triggered upon epoch turnover.
  - Monitor main-net metrics during the changeover epoch; provide real-time support for any late-upgrading SPOs.

## References

- Kant, P.; Brünjes, L.; Coutts, D. *Design Specification for Delegation and Incentives in Cardano — Shelley* (SL‑D1 v1.21, 23 Jul 2020). Especially §5.5.1 “Relative Stake: Active vs Total” (p. 35); Appendix D.2 “Won’t stake pools reject delegation certificates that delegate away from them?” (p. 52); and change log rev. 17 (“Undistributed rewards go to the reserves, not to the treasury.”).
- Corduan, J.; Vinogradova, P.; Güdemann, M. *A Formal Specification of the Cardano Ledger* (Shelley Ledger: SL‑D5 v1.0, updated 23 Mar 2023). Section 11: Rewards and the Epoch Boundary — overview (§11.1), snapshots (§11.5), epoch transition (§11.8), rewards distribution (§11.9), and reward update/return‑to‑reserves residual (∆r₂) (§11.10).
- Wiley, R. [*CPS-0022: Lost Stake*](../CPS-0022/README.md) (2025).

## Acknowledgements

This CIP could not have been created without the support, assistance, and input of all participants in the community-led SPO Incentives Working Group.

- Stef M [RABIT]
- Rich Manderino [ECP]
- Wayne Cataldo [OTG]
- Homer [AAA]
- Chad [BBHMM]
- Mark H [UPSTR]
- Carlos Lopez de Lara [Input|Output]
- Pedro Lucas
- Seomon
- OYSTR Pool

## Copyright
This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
