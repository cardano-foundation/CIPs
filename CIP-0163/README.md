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
  - Separation of Concerns PR: https://github.com/cardano-foundation/CIPs/pull/1307
Created: 2025-08-15
License: CC-BY-4.0
---

## Abstract

Cardano’s staking and on‑chain voting have drifted toward passivity. As described in CPS-0022, long‑lived “set‑and‑forget” delegations let rewards and governance weight ossify, particularly in wallets that have been permanently lost, diluting staking rewards and voting power for engaged participants and harming network security. This CIP reframes delegation as an **active, periodically affirmed contribution to network security** and realigns incentives so rewards flow to those presently able to participate. It introduces **reward-account liveness with inactivity expiry**, with proof-of-life via any witness-bearing action on the staking credential.

This change encourages ongoing engagement and reduces sticky/lost‑stake externalities while respecting user property rights. Reward-account expiry changes eligibility for block production, rewards, and governance participation; it leaves the existing reward-distribution rules in place.

## Motivation: Why is this CIP necessary?

Many users interpret staking rewards as akin to bank interest. If that were the intent, the ledger would not need operator selection, delegation, or performance‑based rewards. Yield could simply accrue automatically. In Cardano, **staking is voluntary and active**. It is how the protocol decides who gets to make blocks, and rewards compensate the combination of (a) **committing stake** to secure the network and (b) **selecting and monitoring** a competent, honest operator. "On a high level, the goal of the incentives mechanism is to incentivize stakeholders to follow the protocol and thereby to guarantee the secure and efficient operation of Cardano" ([SL-D1, Overview of Incentives](https://github.com/IntersectMBO/cardano-ledger/blob/d6eec237df7884aa7ee9854b4b1a83679d9eb99b/eras/shelley/design-spec/shelley-delegation.tex#L2576-L2581)).

- Delegation is a liquid vote for a pool operator. Delegators are expected to reevaluate and move if performance, fees, or behavior change.
- Lost or inactive stake cannot respond to operator misconduct by redelegating, yet can lock in block‑production influence and continue accumulating rewards. It does still raise the stake required by an attacker attempting a majority attack; the concern here is its inability to respond if its existing representative becomes adversarial.

This CIP addresses the broader drift toward **passive and indifferent delegations.** Securing the network is an **active act**, periodically affirmed by the holder, and rewarded accordingly. Reward-account inactivity introduces a light-touch **proof-of-life** via any witness-bearing action on the staking credential, covering both stake pool and dRep participation.

## Specification

#### Current behavior (for context)

- **Indefinite delegations.** Delegation certificates today have no expiry. Once a stake credential delegates to a stake pool or a dRep, that delegation remains valid indefinitely until the holder submits a new delegation (or deregisters the stake key).
- **Rewards return-to-reserves.** After monetary expansion and fees are combined and the treasury cut is taken, pool rewards depend on stake relative to the existing total-stake denominator, reward saturation, pledge, and observed block production. Any residual R not assigned to rewards (∆r₂ = R − Σrs) is returned to reserves, per the epoch-boundary and reward-update rules ([SL-D5 overview](https://github.com/IntersectMBO/cardano-ledger/blob/d6eec237df7884aa7ee9854b4b1a83679d9eb99b/eras/shelley/formal-spec/epoch.tex#L41-L94), [snapshots](https://github.com/IntersectMBO/cardano-ledger/blob/d6eec237df7884aa7ee9854b4b1a83679d9eb99b/eras/shelley/formal-spec/epoch.tex#L390-L505), [epoch transition](https://github.com/IntersectMBO/cardano-ledger/blob/d6eec237df7884aa7ee9854b4b1a83679d9eb99b/eras/shelley/formal-spec/epoch.tex#L865), [rewards distribution](https://github.com/IntersectMBO/cardano-ledger/blob/d6eec237df7884aa7ee9854b4b1a83679d9eb99b/eras/shelley/formal-spec/epoch.tex#L1050), and [reward update](https://github.com/IntersectMBO/cardano-ledger/blob/d6eec237df7884aa7ee9854b4b1a83679d9eb99b/eras/shelley/formal-spec/epoch.tex#L1276)). The active-stake ratio is not the only source of that residual.

### Reward-account inactivity expiry (proof-of-life)

- Add a **single nullable protocol parameter**, `delegatorActivity`, whose numeric value is a nonnegative epoch count. Introduce it as `null` at the hard fork. Community governance can subsequently choose the first numeric period through a parameter-change governance action.
- **Scope & terminology.** A *reward account* (i.e., staking credential) is the object that delegates, accrues, and withdraws rewards. The ledger maintains an `expirationEpoch` for each registered reward account while expiry is enabled; it may be unset while expiry is disabled.
- **Disabled state.** When `delegatorActivity` is `null`, expiry imposes no additional eligibility restriction. Continue to apply all other existing eligibility rules. Do not compare unset expiration dates or evaluate arithmetic involving `null`.
- **Inactivity rule.** With a numeric period in force, an account is expired when `expirationEpoch < currentEpoch`. It remains unexpired throughout its stored `expirationEpoch` and first becomes expired in the following epoch. Exclude expired accounts' stake when creating new eligible pool snapshots and when computing governance voting power, using the timing rules below. Do not rewrite existing pool snapshots.
- **Proof-of-life.** While expiry is enabled, any action that requires a **witness by the reward account** resets its expiration to `currentEpoch + delegatorActivity`. Examples include reward withdrawal, (re)delegation to an SPO or dRep, stake-key deregistration, stake-key registration where its certificate requires that witness, and pool registration or updates requiring a witness from that credential as a pool owner. Deregistration removes the account's expiry state along with its registration. Ordinary wallet usage can renew automatically when the wallet includes a qualifying action such as a reward withdrawal. While expiry is disabled, qualifying actions do not need to maintain an expiration date.
- **Ineligible for rewards accrual.** An expired account is ineligible to contribute stake to newly formed reward-eligible snapshots. It has no reward entitlement arising from stake excluded from those snapshots. Rewards earned through earlier eligible snapshots continue through the existing calculation and payment pipeline, even if the account subsequently expires. Existing reward-distribution and residual-return rules continue to apply; this CIP does not introduce redistribution to other accounts.
- **Numeric parameter changes.** Changing one numeric `delegatorActivity` value to another does not retime existing stored expiration dates or reactivate expired accounts. The next qualifying witness resets the date using the period then in force. The reset remains `currentEpoch + delegatorActivity`, so a shorter period can move a previously stored future expiration earlier.
- **Enabling or re-enabling expiry.** On every transition from `null` to a numeric period in epoch `e`, initialize every registered account's expiration to `e + delegatorActivity`, before computing new eligibility under that period. Every account receives a full activity period from that epoch, irrespective of any previous expiration date or witness history. An account first registered while expiry is enabled receives `registrationEpoch + delegatorActivity`. 
- **Disabling expiry.** Changing a numeric period to `null` removes the expiry restriction from subsequent eligibility computations, including newly formed pool snapshots. Old dates are ignored while disabled and replaced by the full grace-period initialization if expiry is re-enabled. 
- **Migration.** Introduce the parameter as `null`, with no expiry filtering and no requirement to populate expiration dates at the hard fork. No historical witness lookup is required. The first numeric parameter enactment uses the enabling rule above, rather than retroactively expiring accounts based on old activity.

Only authorization required for the staking credential counts. Receiving funds or spending an output using only its payment credential does not itself renew the reward account. A legacy Shelley stake-registration certificate does not require the staking-credential witness and therefore does not qualify merely by registering the account; the Conway registration form that specifies the deposit does require it. This follows the [ledger review's distinction between direct proof and indirect activity](https://github.com/cardano-foundation/CIPs/pull/1077#issuecomment-3458476624). It clarifies the existing witness rule rather than requiring explicit periodic redelegation.

**Note:** `null` is the initial disabled value, not a numeric activity period. The first numeric value for `delegatorActivity` is intentionally **left undefined** here and will be chosen through community governance and deliberation. Potential jittering or lottery mechanisms to stagger per-epoch expiries are not mentioned in this proposal, but may be considered separately if operational data warrants it.

### Epoch boundaries

With expiry enabled, let a qualifying witness occur in epoch $t$, with numeric activity period $d$. The stored expiration is $t+d$, the last unexpired epoch is $t+d$, and the first expired epoch is $t+d+1$. The qualifying epoch and the following $d$ epochs are therefore included. For an illustrative $t=100$ and $d=2$:

| Epoch | Stored expiration | Account status under the expiry rule |
| --- | --- | --- |
| 100 | 102 | Unexpired |
| 101 | 102 | Unexpired |
| 102 | 102 | Unexpired |
| 103 | 102 | Expired |

This example does not select an initial numeric parameter value. At $d=0$, the account is unexpired in the qualifying epoch and expires in the next one. Zero therefore enables a zero-period expiry rule; it is distinct from `null`, which disables expiry.

### Pool snapshot timing

Determine expiry eligibility when a new `mark` snapshot is formed, using the epoch being entered and the parameter state effective for that snapshot. If a numeric period has just been enabled, apply the full grace-period initialization before this check. Retain the snapshot's eligible stake and delegation data as it progresses through `set` and `go`. Expiration, renewal, and parameter changes after its creation do not retroactively re-filter it. Implementations need not add expiration metadata to historical snapshots solely to repeat the expiry check later.

The [Shelley reward cycle](https://github.com/IntersectMBO/cardano-ledger/blob/d6eec237df7884aa7ee9854b4b1a83679d9eb99b/eras/shelley/formal-spec/epoch.tex#L41-L94) and [worked snapshot example](https://github.com/IntersectMBO/cardano-ledger/blob/d6eec237df7884aa7ee9854b4b1a83679d9eb99b/eras/shelley/formal-spec/epoch.tex#L210-L225) establish the following lineage for one snapshot:

| Epoch | Stage of the snapshot created at the boundary entering epoch $n$ | Use and expiry treatment |
| --- | --- | --- |
| $n$ | `mark` | Capture stake and delegation with expiry eligibility evaluated in epoch $n$. |
| $n+1$ | `set` | Use the retained eligible stake for pool leader election and production in epoch $n+1$. |
| $n+2$ | `go` | Calculate rewards for production in epoch $n+1$ using the retained snapshot, subject to the other reward rules. |
| Boundary entering $n+3$ | Reward update applied | Apply the resulting rewards through the existing epoch-boundary process; do not deny previously earned rewards because the account has since expired. |

In the expiration example above, if the account is not renewed, the new `mark` snapshot at the boundary entering epoch 103 excludes its stake. That exclusion reaches `set` in epoch 104 and `go` in epoch 105, with the corresponding reward update applied at the boundary entering epoch 106. The earlier snapshot taken entering epoch 102 can still support production in epoch 103 and rewards calculated in epoch 104 and applied entering epoch 105. A renewal likewise affects future snapshots rather than changing ones already formed.

Explorers and SPO tools should use the eligible pool stake in the snapshot corresponding to the production epoch when estimating leader schedules or block-production luck. An account's current expiry status is not a substitute for that historical snapshot.

### Governance timing

Governance voting power follows the prevailing Conway governance stake-distribution and ratification timing, not the pool `mark`/`set`/`go` reward pipeline. At the computation that forms the governance voting power used by those rules, apply the expiry comparison using that computation's epoch and the parameter state then in force. With a numeric period, expired accounts contribute no voting stake to that computation; with `null`, expiry adds no restriction. Preserve any already formed governance distribution for the decisions for which the prevailing rules use it. Renewal or a parameter transition affects subsequent computations, without rewriting completed tallies or other historical state.

### Eligibility and reward calculation

When enabled, expiry determines whether a reward account's associated stake enters newly formed eligible distributions for leader election, rewards, and governance under the timing and other eligibility rules above. It does not assign a reward weight to each account. An unexpired account can still receive no rewards, for example if its pool fails its declared pledge or produces no blocks.

Pool saturation and block performance remain separate parts of the reward calculation after account eligibility is determined. A saturation cap limits the pool's reward-bearing stake but does not expire its delegators' accounts or cap their contribution to leader election or governance. Eligible delegators continue to share their pool's payment under the existing allocation rules.

## Rationale: How does this CIP achieve its goals?

- **Active security & correct economics.** Periodic renewal makes delegation an affirmative act of securing the network. Engaged holders are compensated for informed operator selection, not mere passage of time.
- **Mitigate sticky stake.** Long‑dormant delegations can prop up legacy control of block production. Expirations reduce that inertia by requiring a simple, periodic affirmation from real, reachable owners.
- **Curbing ossification & compounding.** Expirations prevent unreachable wallets from indefinitely accumulating rewards or voting power without threatening their principal investment.
- **Respect for property.** No seizure or clawback occurs. Expiry removes stake from future eligible distributions until renewed or expiry is disabled; rewards already earned through earlier snapshots remain payable under the existing rules.
- **Governance clarity.** Excluding expired reward accounts when governance voting power is computed makes that power reflect affirmed participation (CIP-1694’s “inactive dRep” guardrails remain complementary but insufficient on their own).
- **Sharper SPO accountability.** Periodic renewal nudges delegators to review operator fees, performance, and conduct. If a pool underperforms or raises costs, stake can organically reallocate on renewal.
- **Fairer path for new pools.** Expirations free stake that would otherwise remain inert with incumbents, reducing entrenched advantages from lost delegations and lowering barriers for competent new operators to attract delegation.

### Security consideration: participation shocks after large expirations

Introducing inactivity expiry could, in the short term, allow portions of stake to lapse if large wallets forget or delay renewal. This temporarily reduces the **active‑stake ratio**, widening the gap between total and active stake. In such windows, the cost for an adversary to assemble a large share of active stake is lower than usual, and block production can concentrate among a smaller set of pools until new delegations occur.

This risk may be assessed for time-bound delegation on its own or it may be considered in conjunction with the [Dynamic Rewards proposal](https://github.com/cardano-foundation/CIPs/pull/1306).

### Evidence for the activity period

The [adoption ballot's supporting links](https://app.ekklesia.vote/ballots/69fb4bef11b259b0b192d40b/proposals/69fb4bef11b259b0b192d40e) collect the original CIP discussion, forum discussion, seminar recording and slides, modeling tool, and FAQ. The [parameter-value ballot](https://app.ekklesia.vote/ballots/69fb4bef11b259b0b192d40b/proposals/69fb4bef11b259b0b192d40f) considered periods around two to six years, alongside shorter and longer alternatives. These are exploratory choices, not established safe minimums, maximums, or an agreed initial numeric value.

The parameter ballot dates the [historical inactivity chart](https://raw.githubusercontent.com/Cerkoryn/governance-reference/e12d2b585d817890f1878372616abc6345b76265/delegatorInactivity_values.jpg) to October 15, 2025. This link pins the repository-hosted artifact to a specific commit; the commit date is not the observation date. The [per-pool inactivity search](https://earncoinpool.com/CIP-163.html) is a live external tool rather than an immutable research snapshot. Its results and the historical chart describe transaction inactivity, not necessarily the absence of a qualifying staking-credential witness. They do not measure permanently lost stake or predict how many accounts would actually expire after notice and opportunities to renew. The author also [corrected an earlier analysis](https://github.com/cardano-foundation/CIPs/pull/1077#issuecomment-3358578912) because inbound-only transactions had incorrectly indicated activity.

These materials are dated background and may have become stale. Some describe the earlier bundled proposal, use the old parameter name, or assume retroactive migration rather than the full grace period specified here. Presentations and external tools without an identifiable immutable version remain background links, not implementation references. A governance proposal selecting the first numeric period should use refreshed analysis of qualifying witnesses, operational readiness, and the effects of the grace period and snapshot timing.

## Path to Active

### Acceptance Criteria

- [ ] **Expiry conformance** – Tests must cover null at hard-fork introduction; disabled operation without null arithmetic; null-to-numeric activation and reactivation giving every registered account a full grace period before eligibility is computed; numeric-to-null disabling; inclusive expiration and the following expired epoch; zero as distinct from null; first registration while enabled or disabled; renewal of active and expired accounts; deregistration; and numeric parameter increases and decreases leaving stored dates unchanged until a qualifying witness uses the new period. No historical witness lookup is required.
- [ ] **Snapshot conformance** – Tests must capture expiry eligibility when `mark` is formed and retain it through `set`, `go`, and the resulting reward update. Cover expiration, renewal, disabling and re-enabling after a snapshot was created; previously earned rewards; and the epoch-102/103 example above. Governance tests must apply the expiry comparison at the prevailing governance stake-distribution computation, without introducing the pool snapshot delay or rewriting historical distributions or tallies.
- [ ] **CIP Editor Approval** – Cardano CIP Editors must confirm that the specification is complete, unambiguous, and internally consistent with existing CIPs.
- [ ] **Nullable parameter and governance support** – The ledger and tooling must support `delegatorActivity` as null or a nonnegative epoch count, introduce it as null, and support later parameter-change governance actions. Selecting the first numeric period is a separate governance decision, informed by refreshed empirical analysis, operational viability, and community feedback; no numeric value is required before hard-fork activation.
- [ ] **Endorsement by Technical Bodies** – The Cardano Parameter-Change Proposals (PCP) Committee and the Intersect Technical Steering Committee (TSC) should both recommend the proposal as technically sound and aligned with the protocol's long-term roadmap.
- [ ] **Stakeholder Concurrence** – A majority of stake pool operators (SPOs), ecosystem tooling maintainers, dReps, and other infrastructure providers must signal readiness to upgrade.
- [ ] **Governance Ratification** – The on-chain Hard-Fork Governance Action must pass the requisite dRep and Constitutional Committee thresholds, establishing legal-constitutional legitimacy and stakeholder support for the change.

### Implementation Plan

- **Community Deliberation (Preparation Phase)**
  - Publish the finalized CIP revision and present it to the PCP committee, TSC, CIP Editors, and wider community channels (Discord, X, Cardano Forum, etc.).
  - Collect structured feedback, particularly on candidate values for `delegatorActivity`, and iterate until broad technical consensus emerges.
- **Specification & Code Integration (Development Phase)**
  - Integrate nullable reward-account inactivity expiry, the corresponding snapshot and voting eligibility rules, and parameter-change governance support into cardano-node and related libraries (ledger, CLI, wallet APIs). Introduce `delegatorActivity` as `null`; development and hard-fork activation do not depend on selecting a numeric period.
  - Submit pull requests to the canonical repositories; obtain code reviews from IOG, CF, and community contributors.
  - Release a new protocol version that includes the changes made in this CIP.
  - Use a dedicated pre-production testnet that mirrors main-net parameters and tests both null and numeric periods, including enable/disable/re-enable transitions, full grace periods, and snapshot delays, allowing SPOs and exchanges to test end-to-end flows.
- **Readiness Sign-off (Testing Phase)**
  - Require at least two weeks of uninterrupted testnet stability plus green results from regression and property-based tests.
  - Monitor ecosystem dApps and tooling to confirm that major node implementations, explorers, wallets, and exchange integrations support the new rule set.
- **On-chain Governance (Ratification Phase)**
  - File the Hard-Fork Governance Action on-chain to introduce the functionality with `delegatorActivity` set to `null`, targeting the next hard fork event.
  - Modify the existing Cardano Constitution to include definitions and guardrails for the new protocol parameter and have it ratified by the tripartite government of Cardano.
  - Mobilize dRep outreach to ensure quorum and super-majority passage; concurrently, the Constitutional Committee validates procedural compliance.
- **Hard-Fork Activation (Deployment Phase)**
  - Upon successful vote, the hard fork event is automatically triggered upon epoch turnover.
  - Monitor main-net metrics during the changeover epoch; provide real-time support for any late-upgrading SPOs.
- **First Numeric Period (Separate Parameter-Change Governance Action)**
  - After community deliberation and refreshed activity analysis, propose a numeric `delegatorActivity` value through the prevailing parameter-change governance process.
  - On enactment in epoch `e`, give every registered account an expiration of `e + delegatorActivity` before computing new eligible distributions. Communicate the grace period and snapshot delays to wallets, explorers, and SPOs. The same full grace-period rule applies whenever expiry is re-enabled.

## References

- Kant, P.; Brünjes, L.; Coutts, D. [*Design Specification for Delegation and Incentives in Cardano — Shelley*](https://github.com/IntersectMBO/cardano-ledger/blob/d6eec237df7884aa7ee9854b4b1a83679d9eb99b/eras/shelley/design-spec/shelley-delegation.tex) (SL‑D1 v1.21, 23 Jul 2020). Especially §5.5.1 “Relative Stake: Active vs Total” (p. 35); Appendix D.2 “Won’t stake pools reject delegation certificates that delegate away from them?” (p. 52); and change log rev. 17 (“Undistributed rewards go to the reserves, not to the treasury.”).
- Corduan, J.; Vinogradova, P.; Güdemann, M. [*A Formal Specification of the Cardano Ledger*](https://github.com/IntersectMBO/cardano-ledger/blob/d6eec237df7884aa7ee9854b4b1a83679d9eb99b/eras/shelley/formal-spec/epoch.tex) (Shelley Ledger: SL‑D5 v1.0, updated 23 Mar 2023). Section 11: Rewards and the Epoch Boundary — overview (§11.1), snapshots (§11.5), epoch transition (§11.8), rewards distribution (§11.9), and reward update/return‑to‑reserves residual (∆r₂) (§11.10).
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
