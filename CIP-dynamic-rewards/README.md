---
CIP: "?"
Title: Dynamic Rewards
Category: Ledger
Status: Proposed
Authors:
  - Ryan Wiley <rian222@gmail.com>
Implementors: []
Discussions:
  - Original bundled proposal: https://github.com/cardano-foundation/CIPs/pull/1077
Created: 2026-10-18
License: CC-BY-4.0
---

## Abstract

Cardano’s reward calculation uses pool stake and pledge relative to the ledger’s total stake. When some stake is inactive, this reduces the rewards allocated to participating pools and delegators. This CIP removes that inactive-stake reduction by scaling the existing pool reward calculation by the inverse of the active-stake ratio.

The proposal preserves the existing pledge-dependent reward formula, including its `1 + a₀` denominator, saturation limits, pledge-fulfillment check, and performance adjustments. It does not require the entire rewards pot to be paid out: residual rewards arising from those other rules continue to return to reserves. It preserves the prevailing eligibility rules and does not introduce reward-account expiry or change governance voting power.

## Motivation: Why is this CIP necessary?

Many users interpret staking rewards as akin to bank interest. If that were the intent, the ledger would not need operator selection, delegation, or performance‑based rewards. Yield could simply accrue automatically. In Cardano, **staking is voluntary and active**. It is how the protocol decides who gets to make blocks, and rewards compensate the combination of (a) **committing stake** to secure the network and (b) **selecting and monitoring** a competent, honest operator. "On a high level, the goal of the incentives mechanism is to incentivize stakeholders to follow the protocol and thereby to guarantee the secure and efficient operation of Cardano" (SL‑D5 §5.1)

Active-stake-ratio normalization provides a participation incentive: when the active-stake ratio falls, the inverse-ratio reward factor rises for eligible delegators and SPOs. The proposal restores the inactive-stake portion while retaining the distinct economic effects of pledge, saturation, and performance.

## Specification

### Current behavior (for context)

The maximum pool reward function uses pool stake and declared pledge relative to total stake. Actual pool rewards also depend on meeting the declared pledge, block production, and the existing saturation and performance rules. Any unallocated residual rewards return to reserves under the reward-update rules (SL-D5 §11.10). The inactive-stake ratio and forgone pledge-dependent rewards are different contributors to that residual.

### Active-stake-ratio normalization

Let:

- $R$ be the rewards pot supplied to the existing pool reward calculation, after the existing monetary-expansion, fee, treasury, and epoch-production adjustments.
- $S$ be the total stake used as the denominator in the existing pool reward formula.
- $A$ be the existing total active stake from the same rewards snapshot.
- $\alpha = A/S$ be the active-stake ratio.

Use the existing snapshot definitions of $S$ and $A$. In particular, do not reduce $A$ because a pool fails its declared-pledge check, is above saturation, or receives lower performance rewards. Such reductions must not increase other pools' rewards through a second normalization. If Time-Bound Delegation is separately adopted, its eligibility rules determine the stake included in those snapshots.

For $S > 0$ and $A > 0$, scale the unrounded maximum pool reward by $1/\alpha$. Equivalently, replace the factor

$$
\frac{R}{1+a_0}
$$

in the existing maximum pool reward function with

$$
\frac{R}{\alpha(1+a_0)}.
$$

All other terms retain their existing definitions: relative pool stake and pledge continue to use $S$, the saturation threshold is unchanged, and the pledge-dependent expression is unchanged. Apply the scaling before the maximum pool reward's existing coin rounding, then apply the existing pledge-fulfillment, performance, reward allocation, and rounding rules. Pool costs and margins are unchanged.

A pool that does not meet its declared pledge still receives zero pool rewards. A pool that declares a lower pledge and meets it remains eligible but retains the lower maximum reward implied by that pledge. Rewards forgone because of pledge, saturation, performance, or the existing allocation and rounding rules are not redistributed by this CIP; residual returns continue to follow the existing rules. If $A=0$ or $S=0$, do not divide by $\alpha$: no pool rewards are distributed, and the existing residual-return rules apply.

This is **not** normalization by the sum of pool reward entitlements. Do not set payouts to $R B_i / \sum_j B_j$, which would redistribute the entire pot, and do not force total payouts to $R/(1+a_0)$. The total payout depends on the existing pool-specific reward reductions. The residual $\Delta r_2$ is retained; only the reduction attributable to the inactive-stake ratio is removed.

This CIP adds no protocol parameter. It can be adopted independently of Time-Bound Delegation and introduces no reward-account activity period or expiry rule, or change to governance voting power.

### Pledge terminology

- **Unmet declared pledge** means the pool owners' eligible stake delegated to their pool is less than the pledge declared in the pool registration. Under the existing pledge-fulfillment check, such a pool receives no pool rewards even if it produces blocks. This is an eligibility failure, not a description of a pool that declares a low pledge and meets it.
- **Unpledged delegated stake** is stake delegated to a pool that is not part of the owners' pledge. It still contributes to the pool's stake and can earn delegation rewards; its presence does not mean that the pool's declared pledge is unmet.
- **Rewards forgone through lower pledge** are the additional rewards a pool could have earned with a larger, fulfilled pledge under the pledge-dependent reward formula. These are distinct from rewards withheld because the pool fails to meet its declared pledge.

For example, a pool with 75M ADA in total stake and a declared, fulfilled pledge of 5M ADA has 70M ADA of unpledged delegated stake. It meets its pledge. The rewards it could earn by pledging more are a separate matter from failing the declared-pledge check. The 70M ADA should not be described as an "unmet pledge," nor should all rewards attributable to that delegated stake be described as returning to reserves.

The [ledger's pledge-fulfillment check](https://github.com/IntersectMBO/cardano-ledger/blob/d6eec237df7884aa7ee9854b4b1a83679d9eb99b/eras/shelley/impl/src/Cardano/Ledger/Shelley/Rewards.hs) and [pledge-dependent maximum reward function](https://github.com/IntersectMBO/cardano-ledger/blob/d6eec237df7884aa7ee9854b4b1a83679d9eb99b/libs/cardano-ledger-core/src/Cardano/Ledger/State/SnapShots.hs) implement these two different concepts. This CIP changes only the reward reduction attributable to the inactive-stake ratio; the other sources of undistributed rewards remain subject to the existing rules.

## Rationale: How does this CIP achieve its goals?

- **Dynamic & responsive yields.** Removing the inactive-stake reduction increases reward rates for otherwise eligible participants at a given rewards pot. The inverse-ratio factor rises when participation falls and falls when it rises, providing an incentive for delegation to return.
- **Pledge incentives preserved.** Both the pledge-dependent expression and its `1 + a₀` denominator remain. A low but fulfilled pledge is not confused with a failed pledge declaration, and its lower reward entitlement is not erased by redistributing all residual rewards.
- **Emission policy.** Realized emissions reflect the reward rules without the additional reduction attributable to inactive stake. They can still be below the gross monetary expansion because of the retained pledge, saturation, performance, and residual-return rules.

### Option to adjust Rho

Removing the inactive-stake reduction increases payouts relative to the current calculation when the active-stake ratio is below one and rewards are payable. With Rho unchanged, this reduces the corresponding return to reserves and accelerates reserve depletion by that amount. Other residual returns continue. If the community prefers to preserve the current rate of emissions, it can reduce Rho through a separate parameter-change governance action, trading away some or all of the yield uplift. This CIP leaves that choice and any new Rho value out of scope.

### Prior rationale and revised censorship assessment

The Shelley-era design explicitly worried about an incentive for large pools to **censor delegation certificates** if rewards were distributed in ways that made existing actors worse off when new delegations appeared. To mitigate this, the specification chose (a) to normalize reward shares by **total stake** rather than active stake so that new delegations do not dilute incumbents’ proportional rewards. Also, (b) to send **undistributed** rewards back to reserves. See *Shelley Delegation & Incentives Design Spec.*, SL‑D1 v1.21 (2020‑07‑23), §5.5.1 “Relative Stake: Active vs Total” (p. 35), and change log rev. 17 (“undistributed rewards go to the reserves”). The spec also anticipated concerns about pools rejecting or disadvantaging delegation transactions (Appendix D.2, p. 52).

**Why this is acceptable to revisit now.** Today’s network conditions and incentives make sustained censorship of delegation transactions economically implausible and strategically dominated by other attack vectors:

- **Healthy stake distribution & coordination threshold.** With broad dispersion of block‑producing power, a would‑be censor would need to withhold a large number of small delegation transactions across many blocks and coordinate with many other producers to move rewards meaningfully. Any unilateral attempt simply fails whenever other producers include those transactions.
- **Externality of “success.”** Under active-stake-ratio normalization, even a successful bout of censorship raises everyone else’s yields, not just the censor’s. This dilutes the payoff while increasing incentives for others to defect and include the transactions.
- **Richer targets exist.** In a DeFi‑enabled ecosystem, selective censorship of high‑value transactions (e.g., liquidations/arbitrages) offers a concentrated, private payoff from censoring few targeted transactions, whereas delegation censorship requires suppressing many of them for marginal gains.
- **Operational risk and visibility.** Prolonged, coordinated censorship would be conspicuous, invite social and governance backlash, and likely degrade a censor’s reputation and delegation flow, offsetting any transient gain.

These factors support removing the reward reduction attributable to the inactive-stake ratio while keeping incentives aligned with **active participation**. They do not justify removing the separate pledge, saturation, or performance rules.

### Relationship to Time-Bound Delegation

[CIP-0163: Time-Bound Delegation](../CIP-0163/README.md) and this proposal were originally presented together in the [original CIP-163 discussion](https://github.com/cardano-foundation/CIPs/pull/1077). They are separated so that each can be reviewed, ratified, and activated independently.

If both proposals are adopted, reward-account expiry excludes long-dormant accounts from the active stake and reward eligibility used by the ledger, while Dynamic Rewards removes the inactive-stake reduction for remaining participants. The inverse-ratio factor could encourage delegation to return after large expirations. The separate pledge and other residual-return rules still apply. Dynamic Rewards alone continues to reward long-dormant accounts that remain eligible under the prevailing ledger rules.

### Evidence and modeling

The historical reserve-consumption comparison below illustrates the gap between theoretical monetary expansion and realized reserve depletion. It does not isolate the inactive-stake component or forecast this CIP's effects. In particular, this proposal retains residual returns attributable to the other reward rules, so no curve should be treated as its expected reserve trajectory without further modeling.

![Historical reserve consumption](Fig1.png)

*Source: [Reserve-consumption comparison by C1cADA Markus](https://x.com/C1cADA_Markus/status/1636023370532749314).*

#### Illustrative reward calculation

Retain the following historical inputs for illustration; they are not a current mainnet forecast:

- $S = 35,698,219,658$ (total stake)
- $\text{Reserves} = 6,955,875,027$
- $k = 500 \;\Rightarrow\; z_0 = 0.002$
- $a_0 = 0.3$
- $\rho = 0.003$
- $\tau = 0.2$

Ignoring transaction fees and missed blocks, the rewards pot after treasury is:

$$
R = (\rho \cdot \mathrm{Reserves}) \cdot (1 - \tau) = 16{,}694{,}100.0648.
$$

Consider a pool with total stake $x=35,000,000$ ADA, **including** a declared and fulfilled pledge $y=1,000,000$ ADA. Pledge is part of the pool stake, so it is not added to $x$ again when calculating ROI. Assume an apparent-performance multiplier of one and ignore pool costs and margins.

$$
\sigma = \frac{x}{S} = 0.000980441051, \qquad
s = \frac{y}{S} = 0.000028012601
$$

$$
\sigma' = \min(\sigma,z_0), \qquad s' = \min(s,z_0)
$$

The existing unrounded maximum pool reward is:

$$
B = \frac{R}{1+a_0}\left(
\sigma' + s'a_0\frac{\sigma' - s'\frac{z_0-\sigma'}{z_0}}{z_0}
\right) = 12{,}642.580060.
$$

The new unrounded maximum is:

$$
B_{\mathrm{dynamic}} = \frac{B}{\alpha}.
$$

A numeric result requires the network's active-stake ratio, which cannot be inferred from this single pool. **For illustration only**, assume $\alpha=0.65$. Then:

$$
B_{\mathrm{dynamic}} = \frac{12{,}642.580060}{0.65} = 19{,}450.123169.
$$

Holding those epoch returns constant and compounding over 73 epochs gives:

$$
\mathrm{ROI}_{\mathrm{annual,current}}
= \left(1+\frac{12{,}642.580060}{35{,}000{,}000}\right)^{73}-1
\approx 2.6715\%
$$

$$
\mathrm{ROI}_{\mathrm{annual,dynamic}}
= \left(1+\frac{19{,}450.123169}{35{,}000{,}000}\right)^{73}-1
\approx 4.1390\%.
$$

The difference in this assumed scenario is about **1.4675 percentage points**, not a network-wide APY prediction. At $\alpha=1$, the normalization factor is one and the existing reward calculation is unchanged. The `1 + a₀` denominator is present in both calculations; the uplift comes from $1/\alpha$, not from multiplying by $1+a_0$ or distributing all of $R$.

The [SPO Incentives simulator](https://spo-incentives.vercel.app/) explores related reward policies, but its published [Full and Max calculations](https://github.com/Cerkoryn/SPO-Incentives/blob/7186366e70f79d50268e8a4482369005626ab509/src/lib/utils/graphs.ts) normalize by the sum of pool factors. Full retains the `1 + a₀` denominator and sets an aggregate budget of $R/(1+a_0)$; Max removes it and sets a budget of $R$. Neither mode is a reference implementation of the inactive-stake-only normalization specified here. Estimates for this CIP must retain pool-specific residual returns and use the network's actual active-stake ratio.

## Path to Active

### Acceptance Criteria

- **Reward conformance** – Tests must cover normalization at partial active stake, unchanged behavior at an active-stake ratio of one, zero active stake, low but fulfilled pledge, failed declared pledge, and residual returns from pledge and saturation limits.
- **CIP Editor Approval** – Cardano CIP Editors must confirm that the specification is complete, unambiguous, and internally consistent with existing CIPs.
- **Endorsement by Technical Bodies** – The Cardano Parameter-Change Proposals (PCP) Committee and the Intersect Technical Steering Committee (TSC) should both recommend the proposal as technically sound and aligned with the protocol’s long-term roadmap.
- **Stakeholder Concurrence** – A majority of stake pool operators (SPOs), ecosystem tooling maintainers, dReps, and other infrastructure providers must signal readiness to upgrade.
- **Governance Ratification** – The on-chain Hard-Fork Governance Action must pass the requisite dRep and Constitutional Committee thresholds, establishing legal-constitutional legitimacy and stakeholder support for the change.

### Implementation Plan

- **Community Deliberation (Preparation Phase)**
  - Publish the finalized CIP and present it to the PCP committee, TSC, CIP Editors, and wider community channels (Discord, X, Cardano Forum, etc.).
  - Collect structured feedback on active-stake-ratio normalization, its incentive effects, and reserve depletion, and iterate until broad technical consensus emerges.
- **Specification & Code Integration (Development Phase)**
  - Integrate the active-stake-ratio normalization into cardano-node and related libraries (ledger, CLI, wallet APIs), retaining the existing pledge, saturation, performance, and rounding rules.
  - Submit pull requests to the canonical repositories; obtain code reviews from IOG, CF, and community contributors.
  - Release a new protocol version that includes the changes made in this CIP.
  - Use a dedicated pre-production testnet that mirrors main-net parameters but enforces the new changes, allowing SPOs and exchanges to test end-to-end flows.
- **Readiness Sign-off (Testing Phase)**
  - Require at least two weeks of uninterrupted testnet stability plus green results from regression and property-based tests.
  - Monitor ecosystem dApps and tooling to confirm that major node implementations, explorers, wallets, and exchange integrations support the new rule set.
- **On-chain Governance (Ratification Phase)**
  - File the Hard-Fork Governance Action on-chain for the rewards calculation change, targeting the next hard fork event.
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
