---
CIP: XXXX
Title: Optimistic Constitutionality
Category: Ledger, Governance
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

This CIP proposes **Optimistic Constitutionality**, a modification to the governance ratification rules introduced by CIP-1694. Under the current model, every governance action requires the Constitutional Committee (CC) to reach a positive vote threshold before it can be ratified. This proposal inverts that requirement: governance actions are **presumed constitutional by default** and proceed to ratification without dedicated CC approval, unless one or more CC members explicitly file an objection (a "constitutionality challenge"). When a CC member votes 'No' (when such a "constitutionality challenge" is triggered), the current model for CC approval, as originally designed by CIP-1694, re-activates and all other CC members should vote too, to either support the "constitutionality challenge" or overwrite it with approvals.

This change reduces the CC's operational burden from active interaction with every governance action to reactive oversight "on demand". The approach aligns with the empirical reality that DReps already filter harmful proposals effectively through their votes of preference. As a second-order effect, Optimistic Constitutionality substantially changes the cost of constitutionality verification for the network, and provides relief to the contentious question of CC compensation, which could still be enabled separately - but under different assumptions for effort spent. 

## Motivation

**A structural observation:**

Across the first ~100 governance actions on mainnet, no proposal was rejected by the CC where DReps would otherwise have approved it. Every proposal the CC found unconstitutional was independently rejected by DRep vote. DReps, acting in rational self-interest to protect their stake and the infrastructure their businesses rely on, have proven effective at identifying bad proposals without CC guidance.

This observation is the empirical foundation for Optimistic Constitutionality: if the CC almost never needs to override DRep consensus, why require the CC to actively approve every action?

### The Current Model's Inefficiencies

Under CIP-1694, the CC must reach its approval threshold for every governance action type that requires CC consent (all types except Info actions and No Confidence motions against themselves). This creates several problems:

1. **Late voting.** CC members empirically vote in the final 20% of a governance action's lifetime, after DReps have already cast votes. This wastes DRep effort on proposals that the CC ultimately rejects.
2. **DRep discouragement.** When CC rejections arrive late, DReps who already spent time evaluating proposals see their work invalidated. Over time, this suppresses DRep participation.
3. **False urgency.** The requirement that CC members evaluate every proposal creates a baseline workload that scales linearly with governance activity, regardless of whether the proposals are contentious.
4. **Compensation pressure.** The active-approval model makes the "CC members must be compensated" argument seem self-evident, because their workload is indeed real and ongoing. Optimistic Constitutionality dissolves this framing by dramatically reducing the expected workload.

### The CC Compensation Dilemma

Since the activation of Conway-era governance, the community has been unable to reach consensus on whether and how Constitutional Committee members should be compensated. The positions are well-documented and deeply held:

**In favor of compensation:**

- CC members bear responsibility for protecting the ecosystem and should not be expected to perform this work for free indefinitely.
- Without compensation, the quality of CC membership may degrade over time as capable individuals cannot justify the time investment.
- Compensation paired with a Code of Conduct creates accountability — the community gains a clear basis for removing underperforming members.

**Against compensation:**

- The exposure, reputation, and networking opportunities of CC membership are themselves powerful incentives. Professional service firms, legal practices, and advisory firms benefit from the visibility.
- Financial compensation at the rates discussed constitutes a full salary in many parts of the world, and will attract candidates motivated by the payment rather than by genuine commitment to Cardano's governance.
- Once compensation is introduced, it is nearly impossible to reverse. It creates bureaucratic overhead (performance management, disputes over effort, rate renegotiation) without an executive authority to adjudicate conflicts.
- Paying per governance action incentivizes participation quantity, not quality — a CC member may simply vote yes/no/abstain "for vibes" to collect payment.
- No empirical evidence yet exists that CC compensation is necessary; candidates continue to step forward, and no CC member has resigned due to lack of payment.
## Specification

### Overview

The core change is to the ratification logic in the Conway ledger rules. Today, a governance action is ratified when:

1. The CC approves (CC Yes votes ≥ CC threshold), **AND**
2. DReps approve (DRep Yes stake ≥ DRep threshold), **AND**
3. SPOs approve (where applicable)

Under Optimistic Constitutionality, condition (1) is replaced:

1. **No CC challenge exists** (zero CC members have voted `No`), **OR** the CC approves under the existing threshold logic (CC Yes votes ≥ CC threshold), **AND**
2. DReps approve (unchanged), **AND**
3. SPOs approve (unchanged, where applicable)

### Definitions

- **Constitutionality Challenge**: A CC member voting `No` on a governance action. This is the trigger that activates full CC threshold evaluation.
- **Unchallenged Action**: A governance action where no CC member has voted `No`. Such actions are considered constitutionally presumed-valid.
- **Challenged Action**: A governance action where at least one CC member has voted `No`. Full CC threshold logic applies.

### Detailed Ratification Rules

#### Unchallenged Actions (no CC `No` votes)

For any governance action type that currently requires CC approval:

- If **zero** CC members have cast a `No` vote, the CC approval condition is satisfied automatically.
- CC members MAY still vote `Yes` or `Abstain` on unchallenged actions (for signaling purposes), but these votes are not required for ratification.
- The DRep and SPO thresholds remain unchanged and must still be met.

#### Challenged Actions (one or more CC `No` votes)

- If **one or more** CC members cast a `No` vote, the governance action transitions to "challenged" status.
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
| `Yes` | Approve constitutionality | Approve constitutionality (optional unless challenged) |
| `No` | Reject as unconstitutional | **File a constitutionality challenge**; triggers full CC evaluation |
| `Abstain` | Explicit abstention | Explicit abstention (does not trigger challenge) |
| (no vote) | Treated as `No` for threshold calculation | **Treated as implicit approval** (does not trigger challenge) |

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
- **Alternative incentive models become viable.** With reduced expected effort, models such as proposer-funded constitutionality review (where a governance action proposer optionally pays for expedited CC review) become more practical.
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

## Path to Active

### Acceptance Criteria

1. The formal Conway ledger specification (`cardano-ledger`) is updated to reflect the modified `RATIFY` rule as described in this CIP.
2. The implementation is deployed on the `preview` testnet and exercised with both challenged and unchallenged governance actions.
3. The implementation is deployed on the `preprod` testnet with a functioning Constitutional Committee.
4. A hard fork governance action activating the new ledger era is ratified and enacted on Cardano mainnet.
5. The local-state-query protocol exposes challenge status for governance actions.

### Implementation Plan

This CIP requires a **hard fork** to activate, as it changes the ledger's ratification semantics.

#### Phase 1: Specification & Review

- Formal specification update to the Conway ledger rules (Agda/Haskell in `IntersectMBO/cardano-ledger`).
- Community review period (minimum 3 months).
- CIP editors and Ledger team review.

#### Phase 2: Testnet Deployment

- Implementation in `cardano-ledger` behind a feature flag tied to the new era.
- Deployment on `preview` testnet.
- Integration testing with governance tooling (GovTool, cardano-cli, Eternl, Lace).
- Deployment on `preprod` testnet.

#### Phase 3: Mainnet Activation

- Hard fork governance action submitted, requiring approval from the CC, DReps, and SPOs under the *current* (pre-Optimistic) rules.
- Upon ratification and enactment at the subsequent epoch boundary, Optimistic Constitutionality becomes active.

#### Optional: Off-Chain Convention (Pre-Hard-Fork)

Before the hard fork, the current CC could voluntarily adopt an "optimistic" convention:

- CC members agree (via off-chain coordination or an Info Action) to vote `Yes` on all governance actions unless they intend to challenge constitutionality.
- CC members who identify a constitutional concern vote `No` and publish a rationale (per CIP-0136 metadata).
- This convention achieves the behavioral outcome of Optimistic Constitutionality without ledger changes, serving as a live experiment to validate the model.

> **Risk:** A voluntary convention is not enforceable. A CC member could defect by not voting, effectively blocking actions under the current "non-vote = implicit No" semantics. The hard fork is required for the full guarantee.

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
