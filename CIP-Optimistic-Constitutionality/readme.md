---
CIP: 182
Title: Optimistic Constitutionality
Category: Ledger
Status: Proposed
Authors:
  - Alex Moser <alexander.moser@cardanofoundation.org>
Implementors:
  - N/A
Discussions:
  - https://github.com/cardano-foundation/CIPs/pull/XXXX
Created: 2026-03-18
License: CC-BY-4.0
---

## Abstract

This CIP proposes **Optimistic Constitutionality**, a modification to the governance ratification rules introduced by CIP-1694. Under the current model, all governance actions besides the "Motion of no-confidence," "Update committee/threshold," and "Info Action" require the Constitutional Committee (CC) to meet a positive vote threshold before they can be ratified. This proposal inverts that requirement: governance actions are **presumed constitutional by default** and proceed to ratification without dedicated CC approval, unless one or more CC members explicitly file an objection (a "constitutionality challenge"). When a CC member votes 'No' (when such a "constitutionality challenge" is triggered), the current model for CC approval, as originally designed by CIP-1694, re-activates and all other CC members should vote too, to either support the "constitutionality challenge" or overwrite it with approvals.

This change reduces the CC's operational burden from active interaction with every governance action to reactive oversight "on demand". The approach aligns with the empirical reality that DReps already filter harmful proposals effectively through their votes of preference. As a second-order effect, Optimistic Constitutionality substantially changes the cost of constitutionality verification for the network, and provides relief to the contentious question of CC compensation, which could still be enabled separately - but under different assumptions for effort spent. 

## Motivation

**A structural observation:**

Across the first ~100 governance actions on mainnet, no proposal was rejected by the CC where DReps would otherwise have approved it. Every proposal the CC found unconstitutional was independently rejected by DRep vote. DReps, acting in rational self-interest to protect their stake and the infrastructure their businesses rely on, have proven effective at identifying bad proposals without CC guidance.

This observation is the empirical foundation for Optimistic Constitutionality: if the CC almost never needs to override DRep consensus, why require the CC to actively approve every action?

### The Current Model's Inefficiencies

Under CIP-1694, the CC must reach its approval threshold for every governance action type that requires CC consent (all types except Info actions and No Confidence motions against themselves). This creates several problems:

1. **Late voting.** CC members empirically tend to vote in the final 20% of a governance action's lifetime, after DReps have already cast votes. This wastes DRep effort on proposals that the CC ultimately rejects.
2. **DRep discouragement.** When CC rejections arrive late, DReps who already spent time evaluating proposals see their work invalidated. Over time, this suppresses DRep participation.
3. **False urgency.** The requirement that CC members evaluate every proposal creates a baseline workload that scales linearly with governance activity, regardless of whether the proposals are contentious.
4. **Compensation pressure.** The active-approval model makes the "CC members must be compensated" argument seem self-evident, because their workload is indeed real and ongoing. Regardless, since the activation of Conway-era governance, the community has been unable to reach consensus on whether and how Constitutional Committee members should be compensated, despite mentions of this in (all versions so far of the) constitution. Optimistic Constitutionality aids to dissolve this by dramatically reducing the expected workload, and introduces new, more transparent possibilities for CC compensation, should that remain a desire.

## Specification

### Overview

The core change is to the ratification logic in the Conway ledger rules. 
After CIP-1694, and simplified, ignoring the different Action types, a governance action is ratified when all these 3 conditions are met:

#### After CIP-1694
```math
$$\text{RATIFIED} \iff \left(\frac{V_{\text{CC}}^{\text{yes}}}{|CC|} \geq T_{\text{CC}}\right) \wedge \left(\frac{S_{\text{DRep}}^{\text{yes}}}{S_{\text{DRep}}^{\text{active}}} \geq T_{\text{DRep}}\right) \wedge \left(\frac{S_{\text{SPO}}^{\text{yes}}}{S_{\text{SPO}}^{\text{delegated}}} \geq T_{\text{SPO}}\right)$$
```
`RATIFIED = (CC Yes votes ≥ CC threshold) AND (DRep Yes stake ≥ DRep threshold) AND (SPO Yes stake ≥ SPO threshold`

#### Under Optimistic Constitutionality, this logic scheme changes to:

```math
$$\text{RATIFIED} \iff \left(V_{\text{CC}}^{\text{no}} = 0 \;\lor\; \frac{V_{\text{CC}}^{\text{yes}}}{|CC|} \geq T_{\text{CC}}\right) \wedge \left(\frac{S_{\text{DRep}}^{\text{yes}}}{S_{\text{DRep}}^{\text{active}}} \geq T_{\text{DRep}}\right) \wedge \left(\frac{S_{\text{SPO}}^{\text{yes}}}{S_{\text{SPO}}^{\text{delegated}}} \geq T_{\text{SPO}}\right)$$
```
`RATIFIED = (zero CC no votes exist **OR** (CC Yes votes ≥ CC threshold)) **AND** (DRep Yes stake ≥ DRep threshold) **AND** (SPO Yes stake ≥ SPO threshold)`

Note that a CC 'yes' vote has no effect. Every CC member can voluntarily provide a yes vote, or abstain, to e.g. provide commentary. 

### Definitions

- **Constitutionality Challenge**: A CC member voting `No` on a governance action. This is the trigger that activates full CC threshold evaluation.
- **Unchallenged Action**: A governance action where no CC member has voted `No`. Such actions are considered constitutionally presumed-valid.
- **Challenged Action**: A governance action where at least one CC member has voted `No`. Full CC threshold logic applies.

### Detailed Ratification Rules

#### Unchallenged Actions (no CC `No` votes)

For any governance action type that currently requires CC approval:

- If **zero** CC members have cast a `No` vote, the CC approval condition is satisfied automatically.
- CC members MAY still vote `Yes` or `Abstain` on unchallenged actions, but these votes are not required for ratification.
- The DRep and SPO thresholds remain unchanged and must still be met for their respective Governance Action types.

#### Challenged Actions (one or more CC `No` votes)

- If **one or more** CC members cast a `No` vote for their respective allowed Governance Action types, the governance action transitions to "challenged" status. 
- Once challenged, the **existing CIP-1694 CC threshold logic applies in full**: the action requires CC Yes votes ≥ CC threshold to satisfy the CC approval condition.
- The threshold is evaluated as today: each current committee member has one vote, and the threshold is the governance parameter `committeeMinSize` / `committeeThreshold`.
- The DRep and SPO thresholds remain unchanged.

#### Actions That Do Not Require CC Approval

The following governance action types are **unaffected** by this proposal, as they do not require CC approval under CIP-1694:

- **Info Actions**: No ratification required.
- **Motion of No Confidence**: CC does not vote on motions against itself.
- **New Constitutional Committee / Threshold / Terms** (during no-confidence state): CC does not participate.

#### Guardrails Script

The guardrails script (proposal policy) continues to apply to Protocol Parameter Updates and Treasury Withdrawals exactly as today. Optimistic Constitutionality changes only the CC vote evaluation, not script-based enforcement.

#### Vote Semantics

| CC Vote | Current Meaning | New Meaning Under This CIP |
|---------|----------------|---------------------------|
| `Yes` | Approve constitutionality | Approve constitutionality (optional) |
| `No` | Reject as unconstitutional | **File a constitutionality challenge**; triggers full CC evaluation |
| `Abstain` | Explicit abstention | Explicit abstention  |
| (no vote) | Treated as `No` for threshold calculation | **Treated as implicit approval** |

> **Critical change:** Under CIP-1694, a CC member who does not vote is effectively counted against the action (since the threshold requires a sufficient number of `Yes` votes). Under this CIP, a CC member who does not vote is counted as implicitly approving. Only an explicit `No` vote signals disapproval.

### Ledger Rule Changes

The changes are localized to the `RATIFY` transition rule in the Conway ledger specification.

#### Current `ccApproved` Predicate (Simplified)

```haskell
-- Current: CC must reach threshold of Yes votes
ccApproved :: GovAction -> ConwayState -> Bool
ccApproved action st =
  let ccYes   = countCCVotes Yes action st
      ccSize  = committeeSize st
      thresh  = committeeThreshold st
  in  ccYes % ccSize >= thresh
```

#### Proposed `ccApproved` Predicate

```haskell
-- Proposed: Presumed approved unless challenged, then standard threshold
ccApproved :: GovAction -> ConwayState -> Bool
ccApproved action st =
  let ccNo    = countCCVotes No action st
      ccYes   = countCCVotes Yes action st
      ccSize  = committeeSize st
      thresh  = committeeThreshold st
  in  if ccNo == 0
      then True                         -- Unchallenged: optimistically approved
      else ccYes % ccSize >= thresh     -- Challenged: standard threshold applies
```

#### State Query Extensions

The local-state-query protocol should be extended to expose:

- Whether a governance action is currently challenged (has any CC `No` vote).
- The identity of the challenging CC member(s).
- Whether the action is in "optimistic" or "challenged" ratification mode.

### New Governance Protocol Parameter (Optional)

This CIP proposes an **optional** new governance protocol parameter:

- `ccOptimisticEnabled :: Bool` — Controls whether Optimistic Constitutionality is active. Default: `True` after activation. Can be set to `False` via a Protocol Parameter Change governance action to revert to CIP-1694 behavior.

This parameter provides a safety valve: if the community determines that Optimistic Constitutionality is being exploited or producing poor outcomes, it can be disabled through normal governance without requiring a hard fork.

### Interaction with CC Expiry and No-Confidence

- **Expired CC members**: An expired CC member's prior votes (including `No` votes) are discarded at expiry, consistent with current behavior. An action that was challenged only by a now-expired member reverts to unchallenged status.
- **No-confidence state**: When the CC is in a state of no-confidence, Optimistic Constitutionality does not apply — no governance actions can be ratified in this state, consistent with CIP-1694.

### Versioning

This specification is versioned by the CIP document itself. Changes to the specification require an amendment to this CIP or a superseding CIP.

## Rationale

### Why Not Just Remove the CC?

The CC serves a necessary constitutional function. Even if DReps empirically catch bad proposals, the CC provides a formalized, accountable body that acts as last line of defense and upholds the standard of the Constitution. Optimistic Constitutionality preserves this role while making it reactive rather than proactive. The CC remains essential as the body authorized to formally declare "this violates the Constitution" — a declaration that carries specific meaning and consequences.

### Effect on CC Compensation

Optimistic Constitutionality does not prescribe a compensation model, but it fundamentally reframes the economics:

- **Baseline workload drops dramatically.** CC members no longer need to review and vote on every governance action. They monitor governance activity and intervene only when they identify constitutional concerns.
- **"Sleeping at the wheel" risk.** an optimistic model creates a risk that CC members disengage entirely and miss the one action that requires intervention. This is a real concern, but it is mitigated by:
  - CC members are, and in fact must be, active Cardano community members who follow governance activity through their own stake, DRep delegations, or community participation already anyway.
  - Off-chain signaling (community forums, social media, direct outreach) creates organic alerting mechanisms.
  - Sufficient Redundancy: One single Constitutinality Challenge is enough to stop the optimistic approval - with 5 to 7 CC member seats, the risk of everyone missing their call for intervention becomes marginal, but definitely even lower than today's chance of not enough CCs voting in time. 
  - A Code of Conduct (developed in parallel) can establish minimum monitoring expectations.
- **Compensation models become lighter.** If compensation is still desired, it can be structured as a modest retainer for monitoring duty rather than a per-action payment, dramatically reducing costs to the treasury.
- **Alternative incentive models become viable.** With reduced expected effort, models such as proposer-funded constitutionality (where a governance action proposer pays for expedited CC review, in case it gets rejected) become more practical.
- **CIP-0149 (Optional DRep Compensation)** already establishes a metadata-based, opt-in, no-ledger-change compensation standard for DReps. A similar lightweight mechanism could be explored for CC members if compensation is desired, without burdening the treasury.

### Addressing Community Concerns

| Concern | How This CIP Addresses It |
|---------|--------------------------|
| CC members must be paid because their workload is high | Workload becomes reactive and low by default |
| Compensation attracts wrong candidates | Reduced workload means reduced compensation pressure; candidates motivated by reputation and influence remain competitive |
| Unpaid CC is unsustainable long-term | Monitoring duty is substantially lighter than active review; comparable to advisory board participation |
| CC votes too late, wasting DRep effort | Under optimistic model, DRep votes count regardless unless a CC challenge occurs; late CC action is a feature (they intervene only when needed) |
| Quality of CC votes is heterogeneous | Challenge mechanism incentivizes CC members to vote `No` only with genuine constitutional reasoning, not as a default |
| GAs are too generic, need better structure | Orthogonal concern (see CIP-0108 for governance metadata standards); this CIP does not preclude improved GA structure |

### Backward Compatibility

This proposal changes the semantics of CC non-voting from "implicit No" to "implicit approval." This is a **breaking change** to the ratification logic and requires a hard fork.

Governance actions submitted before the activation epoch follow the pre-existing rules. Actions whose voting period spans the activation boundary should be evaluated under the new rules from the activation epoch onward.

All existing CC credentials, hot/cold key infrastructure (CIP-0105), governance metadata standards (CIP-0100, CIP-0108, CIP-0136), and wallet integrations (CIP-0030, CIP-0095) remain compatible. The change is entirely within the ledger's `RATIFY` rule and does not affect transaction formats, certificate types, or on-chain data structures.

## Remaining Risk

### Power Abuse

Under Optimistic Constitutionality, CC members could single-handedly block all DRep- and SPO-approved, near-ratified Governance Actions by voting No up until the last block of an epoch, which would leave no time for the remaining CC to overrule the Constitutional Challenge. This risk is real, and currently known possible mitigations for it, such as introducing approval window extensions upon the first CC no vote are only increasing complexity, introduce new more complicated issues and are practically infeasible.
At the moment, the best mitigation for such power abuse would be to acknowledge this risk and rely on the possibilty to call out a state of no confidence - after a Governance Action got maliciously CC-blocked last minute.

## Path to Active

### Acceptance Criteria

1. The formal Conway ledger specification (`cardano-ledger`) is updated to reflect the modified `RATIFY` rule as described in this CIP.
2. The implementation is deployed on the `preview` testnet and exercised with both challenged and unchallenged governance actions.
3. The implementation is deployed on the `preprod` testnet with a functioning Constitutional Committee.
4. A hard fork governance action activating the new ledger era is ratified and enacted on Cardano mainnet.
5. The local-state-query protocol exposes challenge status for governance actions.

### Info Action
A community vote is most likely beneficial or even required for such a change, as it cannot individually be voted on within the hardfork GA, with which it would get activated. 

### Implementation Plan

This CIP requires a **hard fork** to activate, as it changes the ledger's ratification semantics.

#### Phase 1: Specification & Review

- Formal specification update to the Conway ledger rules (Agda/Haskell in `IntersectMBO/cardano-ledger`, `pragma-org/amaru`, `blinklabs-io/dingo` and others).
- Community review period (minimum 3 months) + .
- CIP editors and Ledger team review.

#### Phase 2: Testnet Deployment

- Implementation in `cardano-ledger` behind a feature flag tied to the new era.
- Deployment on `preview` testnet.
- Integration testing with governance tooling (GovTool, cardano-cli, Eternl, Lace).
- Deployment on `preprod` testnet.

#### Phase 3: Mainnet Activation

- Hard fork governance action submitted, requiring approval from the CC, DReps, and SPOs under the *current* (pre-Optimistic) rules.
- Upon ratification and enactment at the subsequent epoch boundary, Optimistic Constitutionality becomes active with `ccOptimisticEnabled :: Bool` set to `TRUE`.

#### Optional: Off-Chain Convention (Pre-Hard-Fork)

Before the hard fork, the current CC could voluntarily adopt an "optimistic" convention:

- CC members agree (via off-chain coordination or an Info Action) to vote `Yes` on all governance actions unless they intend to challenge constitutionality.
- CC members who identify a constitutional concern vote `No` and publish a rationale (per CIP-0136 metadata).
- This convention achieves the behavioral outcome of Optimistic Constitutionality without ledger changes, serving as a live experiment to validate the model.

## References

- [CIP-1694 — A First Step Towards On-Chain Decentralized Governance](https://github.com/cardano-foundation/CIPs/tree/master/CIP-1694)
- [CIP-0149 — Optional DRep Compensation](https://cips.cardano.org/cip/CIP-0149)
- [CIP-0100 — Governance Metadata](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0100/README.md)
- [CIP-0108 — Governance Metadata: Governance Actions](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0108/README.md)
- [CIP-0136 — Governance Metadata: Constitutional Committee Votes](https://cips.cardano.org/cip/CIP-0136)
- [CIP-0105 — Conway Era Key Chains for HD Wallets](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0105/README.md)
- [Conway Formal Ledger Specification](https://github.com/IntersectMBO/formal-ledger-specifications)
- [cardano-ledger (IntersectMBO)](https://github.com/IntersectMBO/cardano-ledger)

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/).
