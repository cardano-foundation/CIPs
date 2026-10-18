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

Cardano’s reward-distribution rules return a portion of each epoch’s distributable rewards pot to reserves rather than paying it to eligible delegators and stake pools. This CIP introduces **full-pot reward distribution** so realized emissions track the monetary expansion set by Rho more closely, while yields respond dynamically to changes in staking participation.

If the network’s total staking ratio remains roughly unchanged, this change is expected to increase rewards for eligible delegators and stake pool operators by a small annual percent. It preserves the prevailing eligibility rules and does not introduce reward-account expiry or change governance voting power.

## Motivation: Why is this CIP necessary?

Many users interpret staking rewards as akin to bank interest. If that were the intent, the ledger would not need operator selection, delegation, or performance‑based rewards. Yield could simply accrue automatically. In Cardano, **staking is voluntary and active**. It is how the protocol decides who gets to make blocks, and rewards compensate the combination of (a) **committing stake** to secure the network and (b) **selecting and monitoring** a competent, honest operator. "On a high level, the goal of the incentives mechanism is to incentivize stakeholders to follow the protocol and thereby to guarantee the secure and efficient operation of Cardano" (SL‑D5 §5.1)

Full‑pot distribution provides a stabilizing incentive: if the active-stake ratio falls low enough to threaten security, yields rise automatically for eligible delegators and SPOs, encouraging new delegation rather than letting rewards drip back to reserves. It also keeps realized emissions closer to the monetary expansion set by Rho.

## Specification

#### Current behavior (for context)

- **Rewards return-to-reserves.** After monetary expansion and fees are combined and the treasury cut is taken, the distributable rewards pot is scaled by the network’s active‑stake ratio; only that fraction is paid out, and the remainder is returned to reserves. This occurs because rewards are computed using only the active stake snapshot and any residual R not assigned to reward accounts (∆r₂ = R − Σrs) is returned to reserves, per the epoch‑boundary and reward‑update rules (SL‑D5 §11.1, §11.5, §11.8–§11.10).

This CIP intentionally limits itself to full-pot reward distribution. All other reward mechanics (e.g., pledge influence, saturation, treasury cut, and performance adjustments) are unchanged.

### Full‑pot reward distribution

- In each epoch, distribute the **full rewards pot** (monetary expansion + fees, less the treasury cut, blocks not produced [Eta], and unmet pledge) to eligible delegators and pools without returning any remainder to reserves **(i.e., eliminate the residual ∆r₂ described in SL‑D5 §11.10 and distribute that proportion as well)**.
- **Eligibility.** Eligibility follows the prevailing ledger rules. This CIP introduces no reward-account activity period or expiry rule and does not change governance voting power. It can be adopted independently of Time-Bound Delegation.

## Rationale: How does this CIP achieve its goals?

- **Dynamic & responsive yields.** Full‑pot distribution increases pool/delegator yield when participation drops and compresses it when participation rises, creating a simple and transparent balancing mechanism.
- **Alignment with policy.** Realized emissions track the monetary expansion set by Rho more closely (rather than being artificially reduced by the active‑stake ratio).

### Option to adjust Rho

Distributing the full-rewards pot will stop sending residual rewards back to reserves. If Rho is left unchanged, reserves will deplete faster by roughly that amount and true emissions will track much closer to the monetary expansion set by Rho. As a result, this will cause active participants to see a small boost to their annual yields. If the community prefers to preserve the current rate of emissions, the community can instead reduce Rho to offset this through a parameter change governance action. However, this will trade away the increase in rewards. This CIP intentionally leaves this choice out of scope.

This is a policy lever with clear tradeoffs: the community can preserve the current rate of emissions by lowering `Rho`, giving up the near-term yield uplift; or it can keep `Rho` and accept faster reserve depletion while distributing more rewards to eligible participants today.

### Prior rationale and revised censorship assessment

The Shelley-era design explicitly worried about an incentive for large pools to **censor delegation certificates** if rewards were distributed in ways that made existing actors worse off when new delegations appeared. To mitigate this, the specification chose (a) to normalize reward shares by **total stake** rather than active stake so that new delegations do not dilute incumbents’ proportional rewards. Also, (b) to send **undistributed** rewards back to reserves. See *Shelley Delegation & Incentives Design Spec.*, SL‑D1 v1.21 (2020‑07‑23), §5.5.1 “Relative Stake: Active vs Total” (p. 35), and change log rev. 17 (“undistributed rewards go to the reserves”). The spec also anticipated concerns about pools rejecting or disadvantaging delegation transactions (Appendix D.2, p. 52).

**Why this is acceptable to revisit now.** Today’s network conditions and incentives make sustained censorship of delegation transactions economically implausible and strategically dominated by other attack vectors:

- **Healthy stake distribution & coordination threshold.** With broad dispersion of block‑producing power, a would‑be censor would need to withhold a large number of small delegation transactions across many blocks and coordinate with many other producers to move rewards meaningfully. Any unilateral attempt simply fails whenever other producers include those transactions.
- **Externality of “success.”** Under full‑pot distribution, even a successful bout of censorship raises everyone else’s yields, not just the censor’s. This dilutes the payoff while increasing incentives for others to defect and include the transactions.
- **Richer targets exist.** In a DeFi‑enabled ecosystem, selective censorship of high‑value transactions (e.g., liquidations/arbitrages) offers a concentrated, private payoff from censoring few targeted transactions, whereas delegation censorship requires suppressing many of them for marginal gains.
- **Operational risk and visibility.** Prolonged, coordinated censorship would be conspicuous, invite social and governance backlash, and likely degrade a censor’s reputation and delegation flow, offsetting any transient gain.

These factors support removing the “return to reserves” scaling while keeping incentives aligned with **active participation**.

### Relationship to Time-Bound Delegation

[CIP-0163: Time-Bound Delegation](../CIP-0163/README.md) and this proposal were originally presented together in the [original CIP-163 discussion](https://github.com/cardano-foundation/CIPs/pull/1077). They are separated so that each can be reviewed, ratified, and activated independently.

If both proposals are adopted, reward-account expiry excludes long-dormant accounts from reward eligibility, while Dynamic Rewards distributes the full rewards pot among the remaining eligible participants. Higher per-unit yields when participation falls could then encourage delegation to return after large expirations. Dynamic Rewards alone continues to reward long-dormant accounts that remain eligible under the prevailing ledger rules.

### Evidence and modeling

- **Reserves trajectory** will be closer to true Rho after this CIP is implemented
  - Red = ADA in reserves if we followed Rho exactly
  - Yellow = ADA in reserves account for actual blocks produced (Eta) and missing pledge. This is the track the reserves is expected to follow after the inclusion of this CIP.
  - Green = Actual amount of ADA in reserves

  ![Reserve Depletion)](Fig1.png)

*Source: [https://x.com/C1cADA_Markus/status/1636023370532749314](https://x.com/C1cADA_Markus/status/1636023370532749314)*

- Estimated **~1% APY uplift** from full‑pot distribution:

Given:

We can calculate the expected ROI for an average pool with 35M stake and 1M pledge before this CIP as follows:

**Constants:**

- $S = 35,698,219,658$ (circulating supply)
- $\text{Reserves} = 6,955,875,027$
- $k = 500 \;\Rightarrow\; z_0 = 0.002$
- $a_0 = 0.3$
- $\rho = 0.003$
- $\tau = 0.2$

**Epoch rewards pot after treasury (not accounting for fees or missed blocks):**

$$
R = (\rho \cdot \mathrm{Reserves}) \cdot (1 - \tau) = 16{,}694{,}100.0648
$$

**Pool (average pool with 35M stake and 1M pledge):**

- $x = 35,000,000$ (stake)
- $y = 1,000,000$ (pledge)

$$
z = \frac{35{,}000{,}000}{35{,}698{,}219{,}658} = 0.000980441051
$$

$$
s = \frac{1{,}000{,}000}{35{,}698{,}219{,}658} = 0.000028012601
$$

$$
z' = \min(z, z_{0}), \quad s' = \min(s, z_{0})
$$

**Base reward (from Shelley formula):**

$$
B = \frac{R}{1+a_{0}} \left(
z' + s' \cdot a_{0} \cdot \frac{\,z' - s' \cdot \frac{(z_{0}-z')}{z_{0}}\,}{z_{0}}
\right)
$$

**For this pool:**

$$
B = 12{,}642.580060
$$

**Standard distribution (spec):** distributes $R$ to active pools and returns the rest to reserves

$$
f_{\mathrm{std}} = B = 12{,}642.580060
$$

```math
\begin{aligned}
\mathrm{ROI}_{\mathrm{pool,std}} &= \frac{f_{\mathrm{std}}}{x+y} \\
&= \frac{12{,}642.580060}{36{,}000{,}000} \\
&= 0.000351182779
\end{aligned}
```

```math
\begin{aligned}
\mathrm{Annual\ ROI} &= \left(1 + \mathrm{ROI}_{\mathrm{pool,std}}\right)^{73} - 1 \\
&= 0.025963163 \;\; (\approx 2.5963\%)
\end{aligned}
```

This gives us about **2.60% Annual ROI** for that pool.

---

**Full pot rewards distribution: distribute all of $R$ with no residual**

Let $W = \sum_i B_i$ over all eligible pools (whole circulation). Typically $W \approx 1$.

Then normalize:

$$
f_{\mathrm{full}} = R \cdot \frac{B}{W} \;\approx\; (1+a_{0}) \cdot B = 16{,}435.354078
$$

```math
\begin{aligned}
\mathrm{ROI}_{\mathrm{epoch,full}} &= \frac{f_{\mathrm{full}}}{x+y} \\
&= \frac{16{,}435.354078}{36{,}000{,}000} \\
&= 0.000456537613
\end{aligned}
```

```math
\begin{aligned}
\mathrm{ROI}_{\mathrm{annual,full}} &= \left(1 + \mathrm{ROI}_{\mathrm{epoch,full}}\right)^{73} - 1 \\
&= 0.033880957 \;\; (\approx 3.3881\%)
\end{aligned}
```

The result is about **3.39% Annual ROI**. Roughly a 0.79% increase.

**Note:** These calculations do not take into account any collected transaction fees, pool performance, or pool fees.

These effects are also modeled in the open source tool available at [https://spo-incentives.vercel.app/](https://spo-incentives.vercel.app/). Setting the rewards formula radio button to “Current” represents the current rewards calculation behavior. Setting it to “Full” represents the rewards calculation after applying this CIP. It is also recommended to experiment with the “Staked Ratio” slider under both of those settings to see how it will affect rewards.

## Path to Active

### Acceptance Criteria

- **CIP Editor Approval** – Cardano CIP Editors must confirm that the specification is complete, unambiguous, and internally consistent with existing CIPs.
- **Endorsement by Technical Bodies** – The Cardano Parameter-Change Proposals (PCP) Committee and the Intersect Technical Steering Committee (TSC) should both recommend the proposal as technically sound and aligned with the protocol’s long-term roadmap.
- **Stakeholder Concurrence** – A majority of stake pool operators (SPOs), ecosystem tooling maintainers, dReps, and other infrastructure providers must signal readiness to upgrade.
- **Governance Ratification** – The on-chain Hard-Fork Governance Action must pass the requisite dRep and Constitutional Committee thresholds, establishing legal-constitutional legitimacy and stakeholder support for the change.

### Implementation Plan

- **Community Deliberation (Preparation Phase)**
  - Publish the finalized CIP and present it to the PCP committee, TSC, CIP Editors, and wider community channels (Discord, X, Cardano Forum, etc.).
  - Collect structured feedback on full-pot reward distribution, its incentive effects, and reserve depletion, and iterate until broad technical consensus emerges.
- **Specification & Code Integration (Development Phase)**
  - Integrate the new rewards calculation logic into cardano-node and related libraries (ledger, CLI, wallet APIs).
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
