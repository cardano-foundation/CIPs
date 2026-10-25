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
- Lost or inactive stake cannot respond to operator misconduct by redelegating, yet can lock in block‑production influence and continue accumulating rewards. It can still raise the stake required by an external attacker; the concern here is its inability to respond if its existing representative becomes adversarial.

This CIP addresses the broader drift toward **passive and indifferent delegations.** Securing the network is an **active act**, periodically affirmed by the holder, and rewarded accordingly. Reward-account inactivity introduces a light-touch **proof-of-life** via any witness-bearing action on the staking credential, covering both stake pool and dRep participation.

## Specification

#### Current behavior (for context)

- **Indefinite delegations.** Delegation certificates today have no expiry. Once a stake credential delegates to a stake pool or a dRep, that delegation remains valid indefinitely until the holder submits a new delegation (or deregisters the stake key).
- **Rewards return-to-reserves.** After monetary expansion and fees are combined and the treasury cut is taken, pool rewards depend on stake relative to the existing total-stake denominator, reward saturation, pledge, and observed block production. Any residual R not assigned to rewards (∆r₂ = R − Σrs) is returned to reserves, per the epoch-boundary and reward-update rules (SL-D5 §11.1, §11.5, §11.8–§11.10). The active-stake ratio is not the only source of that residual.

### Reward-account inactivity expiry (proof-of-life)

- Add a **single protocol parameter** (measured in epochs), to be set via governance:
  - `delegatorActivity`
- **Scope & terminology.** A *reward account* (i.e., staking credential) is the object that delegates, accrues, and withdraws rewards. The ledger maintains an `expirationEpoch` for each registered reward account.
- **Inactivity rule.** During epoch transitions, when stake and voting power are computed, **expired reward accounts** (those with `expirationEpoch < currentEpoch`) are **ignored** for pool leader election, rewards distribution, and governance tallying. An account remains unexpired throughout its stored `expirationEpoch`; it first becomes expired in the following epoch.
- **Proof-of-life.** Any action that requires a **witness by the reward account** resets its expiration to `currentEpoch + delegatorActivity`. Examples include reward withdrawal, (re)delegation to an SPO or dRep, stake-key deregistration, stake-key registration where its certificate requires that witness, and pool registration or updates requiring a witness from that credential as a pool owner. Ordinary wallet usage can renew automatically when the wallet includes a qualifying action such as a reward withdrawal.
- **Ineligible for rewards.** For epochs in which a reward account is inactive, its epoch reward share is **not credited** to that account. The existing reward-distribution rules, including the return of undistributed residual rewards to reserves, continue to apply. This CIP does not redistribute those uncredited rewards to other accounts.
- **Parameter changes.** Updating `delegatorActivity` does not retime existing stored expiration dates or reactivate expired accounts. The next qualifying witness resets the date using the period then in force. The reset remains `currentEpoch + delegatorActivity`, so a shorter period can move a previously stored future expiration earlier.
- **Migration.** On activation, initialize `expirationEpoch` for each reward account to `activationEpoch + delegatorActivity`, giving the account a full activity period from activation.  This is done to prevent computationally expensive historical lookups to get the last qualifying staking-credential witness for every single reward account on the hard fork boundary.

Only authorization required for the staking credential counts. Receiving funds or spending an output using only its payment credential does not itself renew the reward account. A legacy Shelley stake-registration certificate does not require the staking-credential witness and therefore does not qualify merely by registering the account; the Conway registration form that specifies the deposit does require it. This follows the [ledger review's distinction between direct proof and indirect activity](https://github.com/cardano-foundation/CIPs/pull/1077#issuecomment-3458476624). It clarifies the existing witness rule rather than requiring explicit periodic redelegation.

**Note:** The initial numeric value for `delegatorActivity` is intentionally **left undefined** here and will be chosen through community governance and deliberation. Potential jittering or lottery mechanisms to stagger per-epoch expiries are not mentioned in this proposal, but may be considered separately if operational data warrants it.

### Epoch boundaries

Let a qualifying witness occur in epoch $t$, with activity period $d$. The stored expiration is $t+d$, the last unexpired epoch is $t+d$, and the first expired epoch is $t+d+1$. The qualifying epoch and the following $d$ epochs are therefore included. For an illustrative $t=100$ and $d=2$:

| Epoch | Stored expiration | Account status under the expiry rule |
| --- | --- | --- |
| 100 | 102 | Unexpired |
| 101 | 102 | Unexpired |
| 102 | 102 | Unexpired |
| 103 | 102 | Expired |

This example does not select an initial parameter value. If governance permits $d=0$, the account is unexpired in the qualifying epoch and expires in the next one.

### Eligibility and reward calculation

Expiry determines whether a reward account's associated stake can participate in leader election, rewards, and governance under the other prevailing eligibility rules. It does not assign a reward weight to each account. An unexpired account can still receive no rewards, for example if its pool fails its declared pledge or produces no blocks.

Pool saturation and block performance remain separate parts of the reward calculation after account eligibility is determined. A saturation cap limits the pool's reward-bearing stake but does not expire its delegators' accounts or cap their contribution to leader election or governance. Eligible delegators continue to share their pool's payment under the existing allocation rules.

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

This risk may be assessed for time-bound delegation on its own or it may be considered in conjunction with the [Dynamic Rewards CIP](https://github.com/Cerkoryn/CIPs/tree/cip-dynamic-rewards/CIP-dynamic-rewards)

### Evidence for the activity period

The [historical inactivity chart linked by the parameter ballot](https://raw.githubusercontent.com/Cerkoryn/governance-reference/refs/heads/main/delegatorInactivity_values.jpg) and [per-pool inactivity search](https://earncoinpool.com/CIP-163.html) provide dated observations of transaction inactivity. They are not measurements of permanently lost stake or forecasts of how many accounts would actually expire after notice and opportunities to renew. The author also [corrected an earlier analysis](https://github.com/cardano-foundation/CIPs/pull/1077#issuecomment-3358578912) because inbound-only transactions had incorrectly indicated activity.

## Path to Active

### Acceptance Criteria

- **Expiry conformance** – Tests must cover the inclusive expiration epoch and the following expired epoch; zero-period arithmetic; renewal of active and expired accounts; migration with a historical qualifying witness, including dates before and equal to activation; the full activation period for accounts without a qualifying witness history; and parameter increases and decreases leaving stored dates unchanged until a qualifying witness uses the new period. Stake and voting snapshot tests must apply the same comparison to the epoch for which eligibility is computed.
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
