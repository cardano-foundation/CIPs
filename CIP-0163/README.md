---
CIP: 163
Title: Time-Bound Delegation with Dynamic Rewards
Category: Ledger
Status: Proposed
Authors:
  - Ryan Wiley rian222@gmail.com
Implementors: []
Discussions:
  - https://github.com/cardano-foundation/CIPs/pull/1077
Created: 2025-08-15
License: CC-BY-4.0
---

## Abstract

Cardano’s staking and on‑chain voting have drifted toward passivity. As described in CPS-0022, long‑lived “set‑and‑forget” delegations let rewards and governance weight ossify, particularly in wallets that have been permanently lost, diluting staking rewards and voting power engaged participants and harming network security. This CIP reframes delegation as an **active, periodically affirmed contribution to network security** and realigns incentives so rewards flow to those presently and capable of participating. At a high level, it introduces (i) **reward-account liveness with inactivity expiry** (proof-of-life via any witness-bearing action on the staking credential), and (ii) **full-pot reward distribution** to currently eligible delegators and pools each epoch.

If the network’s total staking ratio remains roughly unchanged, these changes are expected to increase rewards for all delegators and stake pool operators by a small annual percent. Together, these changes encourage ongoing engagement, reduce sticky/lost‑stake externalities, and keep realized emissions consistent with monetary policy while respecting user property rights.

## Motivation: why is this CIP necessary?

Many users interpret staking rewards as akin to bank interest. If that were the intent, the ledger would not need operator selection, delegation, or performance‑based rewards. Yield could simply accrue automatically. In Cardano, **staking is voluntary and active**. It is how the protocol decides who gets to make blocks, and rewards compensate the combination of (a) **committing stake** to secure the network and (b) **selecting and monitoring** a competent, honest operator. "On a high level, the goal of the incentives mechanism is to incentivize stakeholders to follow the protocol and thereby to guarantee the secure and efficient operation of Cardano" (SL‑D5 §5.1)

- Delegation is a liquid vote for a pool operator. Delegators are expected to reevaluate and move if performance, fees, or behavior change.
- Lost or inactive stake no longer contributes to present‑day security yet can lock in block‑production influence and siphon rewards from active participants.

This CIP addresses the broader drift toward **passive and indifferent delegations.** Securing the network is an **active act**, periodically affirmed by the holder, and rewarded accordingly. Reward-account inactivity introduces a light-touch **proof-of-life** via any witness-bearing action on the staking credential, covering both stake pool and dRep participation. Furthermore, full‑pot distribution provides a stabilizing incentive: if total stake falls low enough to threaten security, yields rise automatically for active delegators and SPOs, encouraging new delegation rather than letting rewards drip back to reserves.

## Specification

#### Current behavior (for context)

- **Indefinite delegations.** Delegation certificates today have no expiry. Once a stake credential delegates to a stake pool or a dRep, that delegation remains valid indefinitely until the holder submits a new delegation (or deregisters the stake key).
- **Rewards return-to-reserves.** After monetary expansion and fees are combined and the treasury cut is taken, the distributable rewards pot is scaled by the network’s active‑stake ratio; only that fraction is paid out, and the remainder is returned to reserves. This occurs because rewards are computed using only the active stake snapshot and any residual R not assigned to reward accounts (∆r₂ = R − Σrs) is returned to reserves, per the epoch‑boundary and reward‑update rules (SL‑D5 §11.1, §11.5, §11.8–§11.10).

This CIP intentionally limits itself to two changes to the ledger rules. All other reward mechanics (e.g., pledge influence, saturation, treasury cut) are unchanged:

### 1) Reward-account inactivity expiry (proof-of-life)

- Add a **single protocol parameter** (measured in epochs), to be set via governance:
  - `delegatorInactivity`
- **Scope & terminology.** A *reward account* (i.e., staking credential) is the object that delegates, accrues, and withdraws rewards. The ledger maintains an `expirationEpoch` for each registered reward account.
- **Inactivity rule.** During epoch transitions, when stake and voting power are computed, **expired reward accounts** (those with `expirationEpoch < currentEpoch`) are **ignored** for pool leader election, rewards distribution, and governance tallying.
- **Proof-of-life.** Any action that requires a **witness by the reward account** resets its expiration to `currentEpoch + delegatorInactivity`. Examples include: reward withdrawal, (re)delegation to an SPO, (re)delegation to a dRep, and stake-key registration or deregistration. (Wallets commonly withdraw rewards when submitting any transaction, so ordinary usage renews automatically.)
- **Ineligible for rewards.** For epochs in which a reward account is inactive, its epoch reward share is **not credited** to that account. Those uncredited rewards are instead distributed with the rest of the rewards pot (see next section).
- **Migration.** On activation, determine the epoch that the last witness occurred for each rewards account.  Then initialize each account's `expirationEpoch` to that epoch plus `delegatorInactivity`.

### 2) Full‑pot reward distribution

- In each epoch, distribute the **full rewards pot** (monetary expansion + fees, less the treasury cut, blocks not produced [Eta], and unmet pledge) to eligible delegators and pools without returning any remainder to reserves **(i.e., eliminate the residual ∆r₂ described in SL‑D5 §11.10 and distribute that proportion as well)**.
- “Eligibility” remains exactly as today, except that stake controlled by an **expired reward account** does **not** earn rewards (and expired reward accounts contribute **no** governance voting power).

**Note:** The initial numeric value for `delegatorInactivity` is intentionally **left undefined** here and will be chosen through community governance and deliberation. Potential jittering or lottery mechanisms to stagger per-epoch expiries are not mentioned in this proposal, but may be considered separately if operational data warrants it.

## Rationale: how does this CIP achieve its goals?

- **Active security & correct economics.** Periodic renewal makes delegation an affirmative act of securing the network. Engaged holders are compensated for informed operator selection, not mere passage of time.
- **Mitigate sticky stake.** Long‑dormant delegations can prop up legacy control of block production. Expirations reduce that inertia by requiring a simple, periodic affirmation from real, reachable owners.
- **Curbing ossification & compounding.** Expirations prevent unreachable wallets from indefinitely accumulating rewards or voting power without threatening their principal investment.
- **Dynamic & responsive yields.** Full‑pot distribution increases pool/delegator yield when participation drops and compresses it when participation rises, creating a simple and transparent balancing mechanism.
- **Alignment with policy.** Realized emissions track the monetary expansion set by Rho more closely (rather than being artificially reduced by the active‑stake ratio).
- **Respect for property.** No seizure or clawback occurs. Inactive accounts simply stop earning until the account becomes active againn.
- **Governance clarity.** Because expired reward accounts contribute zero voting power, governance power reflects currently affirmed participation (CIP-1694’s “inactive dRep” guardrails remain complementary but insufficient on their own).
- **Sharper SPO accountability.** Periodic renewal nudges delegators to review operator fees, performance, and conduct. If a pool underperforms or raises costs, stake can organically reallocate on renewal.
- **Fairer path for new pools.** Expirations free stake that would otherwise remain inert with incumbents, reducing entrenched advantages from lost delegations and lowering barriers for competent new operators to attract delegation.

### Option to adjust Rho

Distributing the full-rewards pot will stop sending residual rewards back to reserves. If Rho is left unchanged, reserves will deplete faster by roughly that amount and true emissions will track much closer to the monetary expansion set by Rho. As a result, this will cause active participants to see a small boost to their annual yields. If the community prefers to preserve the current rate of emissions, the community can instead reduce Rho to offset this through a parameter change governance action. However, this will trade away the increase in rewards. This CIP intentionally leaves this choice out of scope.

A key practical advantage of distributing the full rewards pot while tightening eligibility for rewards (e.g., by requiring a witness within `delegatorInactivity` epochs) and optionally lowering `Rho` to compensate is that it slows the depletion of reserves, yet still marginally increases rewards for active delegators and SPOs. Empirical projections (e.g., Leios/CPS modeling and CPS‑22 forecasts) suggest sustaining current reward trajectories could require materially higher transaction throughput or faster reserve drawdown. By excluding long‑dormant credentials from the payout base we simply avoid paying rewards to wallets that are unlikely to ever reuse them. That reduction in the set of eligible reward accounts lengthens reserve lifetime in a predictable way while still delivering higher per‑unit yields to genuinely active delegators and SPOs.
 
This is a policy lever with clear tradeoffs: the community can preserve the nominal emission schedule by lowering `Rho`, which maintains the same long‑term reserve trajectory but gives up the near‑term yield uplift for active participants; or the community can keep `Rho` and accept faster nominal depletion while shifting more reward flow to active participants today. Because the change is expressed as an eligibility rule rather than a confiscation, it preserves property rights and is operationally simple to reason about.  It therefore offers a modest, low‑risk way to buy more runway for broader, longer‑term value‑creation efforts (e.g., higher fees/tx volume, DeFi growth) that are the real sustainable solution.

### Prior rationale and revised censorship assessment

The Shelley-era design explicitly worried about an incentive for large pools to **censor delegation certificates** if rewards were distributed in ways that made existing actors worse off when new delegations appeared. To mitigate this, the specification chose (a) to normalize reward shares by **total stake** rather than active stake so that new delegations do not dilute incumbents’ proportional rewards. Also, (b) to send **undistributed** rewards back to reserves. See *Shelley Delegation & Incentives Design Spec.*, SL‑D1 v1.21 (2020‑07‑23), §5.5.1 “Relative Stake: Active vs Total” (p. 35), and change log rev. 17 (“undistributed rewards go to the reserves”). The spec also anticipated concerns about pools rejecting or disadvantaging delegation transactions (Appendix D.2, p. 52).

**Why this is acceptable to revisit now.** Today’s network conditions and incentives make sustained censorship of delegation renewals economically implausible and strategically dominated by other attack vectors:

- **Healthy stake distribution & coordination threshold.** With broad dispersion of block‑producing power, a would‑be censor would need to withhold a large number of small delegation transactions across many blocks and coordinate with many other producers to move rewards meaningfully. Any unilateral attempt simply fails whenever other producers include those transactions.
- **Externality of “success.”** Under full‑pot distribution, even a successful bout of censorship raises everyone else’s yields, not just the censor’s. This dilutes the payoff while increasing incentives for others to defect and include the transactions.
- **Richer targets exist.** In a DeFi‑enabled ecosystem, selective censorship of high‑value transactions (e.g., liquidations/arbitrages) offers a concentrated, private payoff from censoring few targeted transactions, whereas delegation censorship requires suppressing many of them for marginal gains.
- **Operational risk and visibility.** Prolonged, coordinated censorship would be conspicuous, invite social and governance backlash, and likely degrade a censor’s reputation and delegation flow, offsetting any transient gain.

These factors, together with periodic account-liveness expiry/renewal that naturally spreads liveness-reset actions over time, support removing the “return to reserves” scaling while keeping incentives aligned with **active participation**.

### Security consideration: participation shocks after large expirations

Introducing inactivity expiry could, in the short term, allow portions of stake to lapse if large wallets forget or delay renewal. This temporarily reduces the **active‑stake ratio**, widening the gap between total and active stake. In such windows, the cost for an adversary to assemble a large share of active stake is lower than usual, and block production can concentrate among a smaller set of pools until new delegations occur.

**Balancing mechanism in this CIP.** The proposal deliberately pairs expirations with full‑pot reward distribution. Because the entire pot is distributed over the then‑active stake, the per‑unit yield rises automatically when participation drops and compresses when it rises. This creates a fast, transparent negative‑feedback loop:

- If active stake decreases, epoch yield increases for active delegators/SPOs. Capital is attracted back until the security margin normalizes.
- Likewise if active stake increases, epoch yield decreases. Though without changes to Rho the net result of this CIP will still increase rewards all the way up to 100% of active-stake ratio.

This dynamic couples network security to real participation and reduces the risk of active-stake dropping too low.

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
- **Consensus on initial parameter value(s)** – An initial value for the new protocol parameter `delegatorInactivity` in epochs must be agreed upon before hard-fork combinator (HFC) activation. The choice should consider operational viability, empirical analyses, and community feedback.
- **Endorsement by Technical Bodies** – The Cardano Parameter-Change Proposals (PCP) Committee and the Intersect Technical Steering Committee (TSC) should both recommend the proposal as technically sound and aligned with the protocol’s long-term roadmap.
- **Stakeholder Concurrence** – A majority of stake pool operators (SPOs), ecosystem tooling maintainers, dReps, and other infrastructure providers must signal readiness to upgrade.
- **Governance Ratification** – The on-chain Hard-Fork Governance Action must pass the requisite dRep and Constitutional Committee thresholds, establishing legal-constitutional legitimacy and stakeholder support for the change.

### Implementation Plan

- **Community Deliberation (Preparation Phase)**
  - Publish the finalized CIP revision and present it to the PCP committee, TSC, CIP Editors, and wider community channels (Discord, X, Cardano Forum, etc.).
  - Collect structured feedback, particularly on candidate values for the new parameter values and iterate until broad technical consensus emerges.
- **Specification & Code Integration (Development Phase)**
  - Once initial parameter values are determined, integrate the new rewards calculation logic, delegation certificate expiry, and governance features for the new parameters into cardano-node and related libraries (ledger, CLI, wallet APIs).
  - Submit pull requests to the canonical repositories; obtain code reviews from IOG, CF, and community contributors.
  - Release a new protocol version that includes the changes made in this CIP.
  - Use a dedicated pre-production testnet that mirrors main-net parameters but enforces the new changes, allowing SPOs and exchanges to test end-to-end flows.
- **Readiness Sign-off (Testing Phase)**
  - Require at least two weeks of uninterrupted testnet stability plus green results from regression and property-based tests.
  - Monitor ecosystem dApps and tooling to confirm that major node implementations, explorers, wallets, and exchange integrations support the new rule set.
- **On-chain Governance (Ratification Phase)**
  - File the Hard-Fork Governance Action on-chain with the agreed initial parameter values tagged for the next hard fork event.
  - Modify the existing Cardano Constitution to include definitions and guardrails for the new protocol parameters and have it ratified by the tripartite government of Cardano.
  - Mobilize dRep outreach to ensure quorum and super-majority passage; concurrently, the Constitutional Committee validates procedural compliance.
- **Hard-Fork Activation (Deployment Phase)**
  - Upon successful vote, the hard fork event is automatically triggered upon epoch turnover.
  - Monitor main-net metrics during the changeover epoch; provide real-time support for any late-upgrading SPOs.

## References

- Kant, P.; Brünjes, L.; Coutts, D. *Design Specification for Delegation and Incentives in Cardano — Shelley* (SL‑D1 v1.21, 23 Jul 2020). Especially §5.5.1 “Relative Stake: Active vs Total” (p. 35); Appendix D.2 “Won’t stake pools reject delegation certificates that delegate away from them?” (p. 52); and change log rev. 17 (“Undistributed rewards go to the reserves, not to the treasury.”).
- Corduan, J.; Vinogradova, P.; Güdemann, M. *A Formal Specification of the Cardano Ledger* (Shelley Ledger: SL‑D5 v1.0, updated 23 Mar 2023). Section 11: Rewards and the Epoch Boundary — overview (§11.1), snapshots (§11.5), epoch transition (§11.8), rewards distribution (§11.9), and reward update/return‑to‑reserves residual (∆r₂) (§11.10).
- Wiley, R. *CPS-0022: Sticky Stake and Time-Bound Delegation* (2025). Available at: https://github.com/Cerkoryn/CIPs/blob/sticky-stake/CPS-0022/README.md.

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