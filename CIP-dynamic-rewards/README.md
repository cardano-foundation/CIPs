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

Cardano’s reward rules leave rewards unallocated when stake is inactive or exceeds a pool’s reward saturation cap. This CIP redistributes those amounts among participating pools using their capped reward weights, rather than returning those amounts to reserves. The cap continues to constrain each pool’s relative reward weight, while changes to k or an independently adopted CIP-50 pledge-leverage parameter L shift rewards toward pools less constrained by those caps.

The proposal retains the pledge-dependent reward expression, including its `1 + a₀` denominator, the declared-pledge check, observed block performance, and the network-wide production adjustment. Rewards forgone through the retained pledge term or a failed pledge declaration can still return to reserves. It introduces no reward-account expiry and does not change governance voting power or the stake used for block leader election.

## Motivation: Why is this CIP necessary?

Many users interpret staking rewards as akin to bank interest. If that were the intent, the ledger would not need operator selection, delegation, or performance‑based rewards. Yield could simply accrue automatically. In Cardano, **staking is voluntary and active**. It is how the protocol decides who gets to make blocks, and rewards compensate the combination of (a) **committing stake** to secure the network and (b) **selecting and monitoring** a competent, honest operator. "On a high level, the goal of the incentives mechanism is to incentivize stakeholders to follow the protocol and thereby to guarantee the secure and efficient operation of Cardano" (SL‑D5 §5.1)

Redistributing rewards associated with inactive and capped-out stake provides two participation incentives: higher rewards can encourage delegation to return when stake becomes inactive, and tighter reward caps can shift payouts toward less-saturated pools instead of sending the saturation-related shortfall to reserves. This also supports separately governed changes to k or an adopted CIP-50 L.

## Specification

### Current behavior (for context)

The maximum pool reward function uses pool stake and declared pledge relative to total stake. It caps reward-bearing stake at the applicable saturation limit. Actual pool rewards also depend on meeting declared pledge and observed block production. Unallocated residual rewards return to reserves under the reward-update rules (SL-D5 §11.10).

Inactive stake, reward-bearing stake capped by k or an adopted pledge-leverage rule, and the pledge-dependent reward term are distinct contributors to that residual. This CIP redistributes the first two while retaining the pledge-dependent reward term and declared-pledge check.

### Capped reward weights

Use the same rewards snapshot, protocol parameters, and observed block counts as the existing reward calculation. Define:

- $R$: the pot supplied to the pool reward calculation, after existing monetary-expansion, fee, treasury, and network-wide production adjustments.
- $S$: the existing total-stake denominator; $A$: the existing total active stake; $\alpha=A/S$.
- $\sigma_i$: pool $i$'s total stake divided by $S$; $s_i$: its declared pledge divided by $S$; $z_0=1/k$.
- $c_i$: the pool's reward-bearing capped stake, expressed relative to $S$.
- $\pi_i$: the existing apparent-performance multiplier, with $\pi_i=0$ for a pool that produced no blocks.

If $S=0$, $A=0$, or $R=0$, distribute no pool rewards and retain the existing final accounting rules. Do not evaluate ratios with a zero denominator.

Under the existing k cap:

$$
c_i=\min(\sigma_i,z_0).
$$

If [CIP-0050: Pledge Leverage-Based Staking Rewards](../CIP-0050/README.md) is separately adopted, also apply its leverage cap:

$$
c_i=\min(\sigma_i,z_0,Ls_i).
$$

CIP-50 is not a prerequisite for this proposal. Neither cap changes the pool stake used for block leader election. An oversaturated pool's entire delegated stake can still contribute to leader election, while only its capped portion enters the reward expression.

Let the common normalization denominator be:

$$
N=\sum_j \pi_j c_j.
$$

The sum covers the registered pools in the rewards snapshot. Include the capped weight of a block-producing pool even if it fails its declared-pledge check; otherwise that separate forfeiture would be redistributed as well. Do not include the pledge bonus or the full pool reward entitlement in $N$.

Use observed performance in this denominator, not just the unweighted sum of capped stake. This keeps the common payout budget consistent with the same performance multipliers used to pay pools, including epochs with very uneven production. Compute $N$ with exact arithmetic before rounding individual rewards.

### Normalized rewards

Let $B_i$ be the existing unrounded maximum pool reward before its performance multiplier. Apply the existing declared-pledge check: if it fails, set $B_i=0$. For a pool that meets its pledge, retain the existing reward expression, including its `1 + a₀` denominator. In the Shelley formula, with $s'_i=\min(s_i,z_0)$:

$$
B_i=\frac{R}{1+a_0}\left(
c_i+s'_ia_0\frac{c_i-s'_i\frac{z_0-c_i}{z_0}}{z_0}
\right).
$$

For $N>0$, replace the unrounded maximum by:

$$
\widehat B_i=\frac{B_i}{N}.
$$

Then apply the existing maximum-reward coin rounding, the existing performance multiplier $\pi_i$, and the existing pool reward allocation and rounding rules. Before rounding, the pool reward is therefore:

$$
Q_i=\frac{\pi_i B_i}{N}.
$$

All eligible pools can receive normalized rewards, including oversaturated pools through their capped weights. There is no separate eligibility cliff at saturation: stake above the cap adds no reward weight, and delegators share the resulting pool reward under the existing allocation rules. Pool costs and margins are unchanged.

A failed declared pledge still gives zero pool rewards. Its weight remains in $N$, so that forfeiture is not redistributed. If $N=0$, including when there are no block-producing pools with positive capped weight, distribute no pool rewards and retain the existing residual-return behavior. Never divide by zero.

This changes where the rewards associated with inactive and capped-out stake go: they increase normalized pool rewards instead of being returned merely because those stake portions earn no reward weight. The separate pledge-dependent reductions remain. The residual $\Delta r_2$ and final accounting rules are retained, including the existing treatment of rounding and unregistered reward accounts.

### Budget and limiting cases

For $R>0$ and $c_i>0$, define $h_i=B_i/(Rc_i)$; take $h_i=0$ otherwise. Under the retained reward and pledge-fulfillment rules, $0\le h_i\le1$. The allocation can be written:

$$
Q_i=R\left(\frac{\pi_i c_i}{N}\right)h_i.
$$

The weights $\pi_i c_i/N$ sum to one when $N>0$. Consequently, total unrounded pool rewards cannot exceed $R$, and the existing rounding cannot increase that total. The unearned pledge-dependent and failed-pledge portions can remain unallocated and return to reserves.

Under the current performance rule, $\pi_i=\beta_i/(\sigma_i/\alpha)$ for a block-producing pool, where $\beta_i$ is its share of blocks actually produced. If no saturation cap binds, $c_i=\sigma_i$ and $N=\alpha$. The formula then reduces to inverse-active-stake normalization. If active stake is also 100%, it reproduces current rewards. With oversaturated pools, $N$ reflects the capped weights, so saturation-related rewards are redistributed even when all stake is active.

This is not normalization by $\sum_i B_i$. It does not force total payouts to $R$ or to $R/(1+a_0)$ independently of the retained pledge term. It adds no protocol parameter, requires no adoption of Time-Bound Delegation, and does not change governance voting power.

### Pledge terminology

- **Unmet declared pledge** means the pool owners' eligible stake delegated to their pool is less than the pledge declared in the pool registration. Under the existing pledge-fulfillment check, such a pool receives no pool rewards even if it produces blocks. This is an eligibility failure, not a description of a pool that declares a low pledge and meets it.
- **Unpledged delegated stake** is stake delegated to a pool that is not part of the owners' pledge. It still contributes to the pool's stake and can earn delegation rewards; its presence does not mean that the pool's declared pledge is unmet.
- **Rewards forgone through lower pledge** are the additional rewards a pool could have earned with a larger, fulfilled pledge under the pledge-dependent reward formula. These are distinct from rewards withheld because the pool fails to meet its declared pledge.

For example, a pool with 75M ADA in total stake and a declared, fulfilled pledge of 5M ADA has 70M ADA of unpledged delegated stake. It meets its pledge. The rewards it could earn by pledging more are a separate matter from failing the declared-pledge check. The 70M ADA should not be described as an "unmet pledge," nor should all rewards attributable to that delegated stake be described as returning to reserves.

The [ledger's pledge-fulfillment check](https://github.com/IntersectMBO/cardano-ledger/blob/d6eec237df7884aa7ee9854b4b1a83679d9eb99b/eras/shelley/impl/src/Cardano/Ledger/Shelley/Rewards.hs) and [pledge-dependent maximum reward function](https://github.com/IntersectMBO/cardano-ledger/blob/d6eec237df7884aa7ee9854b4b1a83679d9eb99b/libs/cardano-ledger-core/src/Cardano/Ledger/State/SnapShots.hs) implement these two different concepts. This CIP redistributes the reductions attributable to inactive and capped-out stake. It retains the pledge-dependent reward expression and the withholding caused by a failed declared-pledge check.

## Rationale: How does this CIP achieve its goals?

- **Responsive yields.** Inactive and capped-out stake no longer reduces the allocation budget merely by contributing no reward weight. Normalization raises rewards for participating capped weights, providing an incentive for delegation to return or move to a pool offering a better reward per ADA.
- **Support for saturation changes.** Increasing k, or decreasing an adopted CIP-50 L when its cap binds, reduces the relative reward weights of affected pools. Redistributing the saturation-related shortfall increases rewards available to other pools instead of diverting that shortfall to reserves. Oversaturated pools can still share through their below-cap portion.
- **Pledge incentives preserved.** The existing pledge-dependent expression and its `1 + a₀` denominator remain. A low but fulfilled pledge is distinct from a failed declaration, and neither is erased by normalizing the full reward entitlements to a predetermined total payout.

### Option to adjust Rho

Redistributing rewards associated with inactive and capped-out stake reduces the corresponding return to reserves. With Rho unchanged, reserves deplete faster by the extra amount paid out. The retained pledge term, failed-pledge withholding, and existing final accounting can still leave residual returns. The network-wide production adjustment remains in place before the rewards pot is formed. If the community prefers to preserve its current rate of emissions, it can reduce Rho through a separate governance action, trading away some or all of the yield uplift. This CIP leaves that choice and any new Rho value out of scope.

### Prior rationale and revised censorship assessment

The Shelley-era design explicitly worried about an incentive for large pools to **censor delegation certificates** if rewards were distributed in ways that made existing actors worse off when new delegations appeared. To mitigate this, the specification chose (a) to normalize reward shares by **total stake** rather than active stake so that new delegations do not dilute incumbents’ proportional rewards. Also, (b) to send **undistributed** rewards back to reserves. See *Shelley Delegation & Incentives Design Spec.*, SL‑D1 v1.21 (2020‑07‑23), §5.5.1 “Relative Stake: Active vs Total” (p. 35), and change log rev. 17 (“undistributed rewards go to the reserves”). The spec also anticipated concerns about pools rejecting or disadvantaging delegation transactions (Appendix D.2, p. 52).

**Why this is acceptable to revisit now.** Today’s network conditions and incentives make sustained censorship of delegation transactions economically implausible and strategically dominated by other attack vectors:

- **Healthy stake distribution & coordination threshold.** With broad dispersion of block‑producing power, a would‑be censor would need to withhold a large number of small delegation transactions across many blocks and coordinate with many other producers to move rewards meaningfully. Any unilateral attempt simply fails whenever other producers include those transactions.
- **Externality of “success.”** Where censorship reduces reward-bearing capped stake and increases normalized payouts, the benefit is shared among other rewarded pools. This dilutes the censor's private payoff while increasing incentives for others to include the transactions. The effect depends on which pools and reward weights are affected.
- **Richer targets exist.** In a DeFi‑enabled ecosystem, selective censorship of high‑value transactions (e.g., liquidations/arbitrages) offers a concentrated, private payoff from censoring few targeted transactions, whereas delegation censorship requires suppressing many of them for marginal gains.
- **Operational risk and visibility.** Prolonged, coordinated censorship would be conspicuous, invite social and governance backlash, and likely degrade a censor’s reputation and delegation flow, offsetting any transient gain.

These factors support redistributing the rewards associated with inactive and capped-out stake while keeping incentives aligned with **active participation**. The saturation caps still constrain relative reward weights, and the existing pledge-fulfillment and block-performance rules remain in effect.

### Relationship to Time-Bound Delegation

[CIP-0163: Time-Bound Delegation](../CIP-0163/README.md) and this proposal were originally presented together in the [original CIP-163 discussion](https://github.com/cardano-foundation/CIPs/pull/1077). They can be reviewed, ratified, and activated independently.

If both proposals are adopted, reward-account expiry excludes long-dormant accounts from the active stake and reward eligibility used by the ledger. Dynamic Rewards then redistributes rewards over the remaining performance-adjusted capped weights, retaining the pledge-dependent reward expression and failed-pledge withholding. Dynamic Rewards alone continues to reward long-dormant accounts that remain eligible under the prevailing ledger rules.

### Evidence and modeling

The historical reserve-consumption comparison below illustrates the gap between theoretical monetary expansion and realized reserve depletion. It does not isolate the inactive-stake and saturation components or forecast this CIP's effects. In particular, this proposal retains residual returns attributable to the other reward rules, so no curve should be treated as its expected reserve trajectory without further modeling.

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
\right) \approx 12{,}642.580060.
$$

The new unrounded maximum is:

$$
B_{\mathrm{dynamic}} = \frac{B}{N}.
$$

A numeric result requires the common denominator $N$, using the network's capped stakes and observed performance; it cannot be inferred from this single pool. **For illustration only**, assume $N=0.65$ and retain the pool's performance multiplier of one. Then:

$$
B_{\mathrm{dynamic}} = \frac{12{,}642.580060}{0.65} \approx 19{,}450.123169.
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

The difference in this assumed scenario is about **1.4675 percentage points**, not a network-wide APY prediction. When no cap binds, $N=\alpha$; when active stake is also 100%, $N=1$ and current rewards are unchanged. The `1 + a₀` denominator is present in both calculations; the uplift comes from the normalization of performance-adjusted capped weights.

#### Effect of tightening a saturation cap

To isolate saturation, consider a separate simplified example with $S=200$ ADA, $R=1,000$ ADA, $a_0=0$, fulfilled pledge, and apparent-performance multipliers of one. Pool A has 100 ADA of stake and Pool B has 20 ADA. With k changing from 4 to 8, the saturation cap falls from 50 to 25 ADA:

| Quantity | Cap of 50 ADA | Cap of 25 ADA |
| --- | ---: | ---: |
| Pool A capped stake | 50 ADA | 25 ADA |
| Pool B capped stake | 20 ADA | 20 ADA |
| $N$ | $70/200=0.35$ | $45/200=0.225$ |
| Pool A reward | 714.29 ADA | 555.56 ADA |
| Pool B reward | 285.71 ADA | 444.44 ADA |
| Total pool rewards | 1,000 ADA | 1,000 ADA |

Pool A remains oversaturated and shares only through its capped weight. Tightening its cap shifts rewards toward Pool B, which remains below the cap. No saturation-related amount is returned to reserves in this cap-only example. A nonzero $a_0$ would retain the pledge-dependent reductions specified above.

For the $a_0=0$ cap-only example, the same caps and allocations result if the global cap is held at 100 ADA, both pools have 5 ADA of fulfilled pledge, and an independently adopted CIP-50 L changes from 10 to 5. The leverage cap then falls from 50 to 25 ADA while Pool B remains below it. Neither example changes the stake used for leader election.

With $a_0=0.3$, Pool B's reward increases from approximately 225.38 to 361.37 ADA in the k example, and from approximately 222.42 to 345.98 ADA in the L example. The retained pledge term leaves part of the pot unallocated in these cases.

The [SPO Incentives simulator](https://spo-incentives.vercel.app/) explores related policies, but its published [Full and Max calculations](https://github.com/Cerkoryn/SPO-Incentives/blob/7186366e70f79d50268e8a4482369005626ab509/src/lib/utils/graphs.ts) normalize by full pool factors. Full retains the `1 + a₀` denominator and sets a modeled aggregate budget of $R/(1+a_0)$; Max removes it and sets a budget of $R$. This CIP instead normalizes performance-adjusted capped stake before the retained pledge term and declared-pledge withholding. The simulator also omits actual block-performance and owner-pledge-fulfillment checks, so neither mode is a reference implementation of this specification.

## Path to Active

### Acceptance Criteria

- **Reward conformance** – Tests must cover redistribution after tighter k and CIP-50 L caps, oversaturated pools sharing only through capped weights, preserved pledge-related reserve returns, failed declared pledge, zero normalization weight, uneven block production, and conservation of the rewards pot. With no binding cap, the current performance rule must reproduce inverse-active-stake normalization; with full active stake and no binding cap, current rewards must be unchanged.
- **CIP Editor Approval** – Cardano CIP Editors must confirm that the specification is complete, unambiguous, and internally consistent with existing CIPs.
- **Endorsement by Technical Bodies** – The Cardano Parameter-Change Proposals (PCP) Committee and the Intersect Technical Steering Committee (TSC) should both recommend the proposal as technically sound and aligned with the protocol’s long-term roadmap.
- **Stakeholder Concurrence** – A majority of stake pool operators (SPOs), ecosystem tooling maintainers, dReps, and other infrastructure providers must signal readiness to upgrade.
- **Governance Ratification** – The on-chain Hard-Fork Governance Action must pass the requisite dRep and Constitutional Committee thresholds, establishing legal-constitutional legitimacy and stakeholder support for the change.

### Implementation Plan

- **Community Deliberation (Preparation Phase)**
  - Publish the finalized CIP and present it to the PCP committee, TSC, CIP Editors, and wider community channels (Discord, X, Cardano Forum, etc.).
  - Collect structured feedback on redistribution through capped reward weights, its incentive effects, and reserve depletion, and iterate until broad technical consensus emerges.
- **Specification & Code Integration (Development Phase)**
  - Compute the common normalization denominator from the rewards snapshot, applicable caps, and observed performance, then integrate the normalized reward calculation into cardano-node and related libraries (ledger, CLI, wallet APIs). Retain the pledge term, pledge-fulfillment check, caps, and existing rounding and final accounting rules.
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
