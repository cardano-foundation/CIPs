---
CIP: XXXX
Title: Governance Participant Compensation
Category: Ledger
Status: Proposed
Authors:
    - Thomas Lindseth <thomas.lindseth@intersectmbo.org>
Implementors: []
Discussions: 
    - https://github.com/cardano-foundation/CIPs/pull/1117
Created: 2025-11-29
License: CC-BY-4.0
---

## Abstract

This CIP introduces the **Compensatory Ledger Mechanism (CLM)**—a deterministic, protocol-level compensation system for governance actors participating in Cardano governance actions. A portion of each governance action’s deposit is automatically distributed to Constitutional Committee (CC) members, Delegated Representatives (DReps), and Stake Pool Operators (SPOs) who cast a valid vote.

This mechanism requires **no smart contracts**, **no Treasury withdrawals**, and **no manual triggers**, operating fully within Cardano’s ledger rules in a manner analogous to staking rewards. It creates an incentive-aligned, sustainable, and decentralized compensation model that reflects the real cost of governance participation.

---

## Motivation: why is this CIP necessary?

Cardano’s decentralized governance framework requires persistent engagement from CC members, DReps, and SPOs. These actors must analyze governance actions, evaluate technical and economic implications, and cast informed votes. This work incurs ongoing time, expertise, and operational costs. Without a reliable compensation model, several risks emerge:

### Governance Fatigue
Uncompensated governance labor leads to declining participation over time.

### Centralization Risks
Only large, well-funded entities can consistently afford to participate, reducing diversity and representation.

### Low Governance Participation / Quorum Instability
Without compensation, new and smaller actors lack incentives to engage, harming governance quality.

### Misaligned Incentives
Proposers incur no cost commensurate with the burden placed on reviewers and voters.

### Need for a Deterministic, Automated Mechanism
Any off-chain or trust-based compensation scheme introduces friction and reduces security.

The CLM addresses these issues by:
- Making governance participation economically feasible  
- Ensuring compensation flows only to active participants  
- Funding compensation from proposer deposits, aligning costs with governance load  
- Executing payments entirely through the ledger for maximum reliability  

---

## Specification

### New Protocol Parameters

The following fields are added to `PParams`:

| Parameter | Type | Description |
|----------|------|-------------|
| `ccCompensationRate` | UnitInterval | Portion of `govDeposit` allocated to CC. |
| `drepCompensationRate` | UnitInterval | Portion allocated to DReps. |
| `spoCompensationRate` | UnitInterval | Portion allocated to SPOs. |
| `drepWeightFactor` | UnitInterval | Fraction of DRep pool distributed stake-weighted. |
| `spoWeightFactor` | UnitInterval | Fraction of SPO pool distributed active-stake-weighted. |

**Constraint:**  
`ccCompensationRate + drepCompensationRate + spoCompensationRate ≤ MAX_COMP_RATE`  
where `MAX_COMP_RATE` is hard-coded (e.g., 0.25).

---

### Ledger Additions
The ledger should maintain two new optional mappings:

- `drepRewardAccounts : Map DRepID (Maybe RewardAddress)`
- `ccRewardAccounts   : Map CCHotCredential (Maybe RewardAddress)`

### DRep Registration Extension
DRep registration certificates should include:
- a DRep ID
- a deposit
- an optional anchor
- **an optional reward address**

Processing rule:
- If present → `drepRewardAccounts[drepID] = Just rewardAddress`
- If absent → `drepRewardAccounts[drepID] = Nothing`

### CC Hot Key Registration Extension
A CC hot key registration certificate should include:
- the cold credential
- the hot credential
- **an optional reward address**

Processing rule:
- If present → `ccRewardAccounts[hotCred] = Just rewardAddress`
- If absent → `ccRewardAccounts[hotCred] = Nothing`

### Compensation Trigger



Upon finalization of any governance action requiring a deposit—whether it **passes**, **fails**, or **expires**—the ledger automatically:

1. Finalizes deposit accounting  
2. Creates the compensation pools  
3. Distributes funds to voting governance actors  

This occurs atomically during governance-action completion.

---

## Compensation Eligibility Based on Relevant Governance Actor Groups

For each governance action type, the protocol specifies which governance actor groups are **relevant** to the ratification of that action. Only these *relevant* groups contribute to the tally for that action, and only these groups may generate compensation under the CLM.

Governance actor groups that are **non-relevant** for a given governance action type may cast votes, but their votes do **not** affect the tally and they do **not** receive compensation. Their associated portion of the compensation rate is **not consumed**.

Let `RelevantActors` be the set of governance actor groups relevant for the governance action type. Define:

```
EffectiveRate(group) =
    compensationRate(group), if group ∈ RelevantActors
    0, otherwise
```

Only these `EffectiveRate` values are used for compensation pot creation.

### Refund Behavior

Any portion of the governance deposit corresponding to compensation rates for **non-relevant** governance actor groups:

* is **not added** to any compensation pool,
* is **not consumed**, and
* remains part of the **refundable deposit** that may be returned to the proposer when the governance action finalizes.

Thus:

```
TotalCompensation = govDeposit × Σ(EffectiveRate(group))

RefundableDeposit = govDeposit − TotalCompensation
```

---

### Compensation Pot Creation

Let `govDeposit` be the required deposit for the governance action.

```
TotalCompensation =
  govDeposit × Σ(EffectiveRate(group))
```

Split into:

```
CC_Pool   = govDeposit × EffectiveRate(CC)
DRep_Pool = govDeposit × EffectiveRate(DRep)
SPO_Pool  = govDeposit × EffectiveRate(SPO)
```

The remainder is refund-eligible for the proposer when the action expires.

---

### Distribution Rules

#### Compensation to Constitutional Committee (Equal Share)

Only voting CC members are compensated.

```
Payout_CC = CC_Pool / numberOfVotingCCMembers
```

Non-voting CC members receive 0.

---

#### DRep Compensation (Hybrid Model)

##### Equal-Share Portion
```
EqualShareAmount = DRep_Pool × (1 − drepWeightFactor)
Payout_Equal_DRep = EqualShareAmount / numberOfVotingDReps
```

##### Stake-Weighted Portion  
Based on governance stake represented by voting DReps:

```
WeightedAmount = DRep_Pool × drepWeightFactor
Payout_Weighted_DRep =
  WeightedAmount × (stakeRepresentedByDRep / totalStakeOfVotingDReps)
```

##### Total DRep Payout
```
Payout_DRep = Payout_Equal_DRep + Payout_Weighted_DRep
```

---

#### SPO Compensation (Hybrid Model)

##### Equal-Share Portion
```
EqualShareAmount = SPO_Pool × (1 − spoWeightFactor)
Payout_Equal_SPO = EqualShareAmount / numberOfVotingSPOs
```

##### Stake-Weighted Portion  
Weighted by **block-producing active stake.

```
WeightedAmount = SPO_Pool × spoWeightFactor
Payout_Weighted_SPO =
  WeightedAmount × (activeStakeOfSPO / totalActiveStakeOfVotingSPOs)
```

##### Total SPO Payout

Payout_SPO = Payout_Equal_SPO + Payout_Weighted_SPO

### Eligibility
To receive CLM compensation, a governance actor must:
- cast a valid vote on the governance action, and
- have a registered reward address:
  - DReps: `drepRewardAccounts[drepID] = Just addr`
  - CC members: `ccRewardAccounts[hotCred] = Just addr`
  - SPOs: existing staking reward account

Actors without a reward address remain part of vote weighting but receive no payout.

---

### Deposit Finality

The compensation portion of the deposit corresponding to EffectiveRate(group) values greater than zero is consumed. Any portion corresponding to groups with EffectiveRate(group) = 0 (i.e., non-relevant governance actor groups) is not consumed and remains refundable.

---

## Rationale: how does this CIP achieve its goals?

### Ledger-Native Implementation Ensures Maximum Reliability
All compensation logic is implemented inside ledger rules.  
This guarantees:

- Deterministic execution  
- No dependency on smart contracts  
- No treasury governance or manual intervention  
- A trust model equivalent to ADA staking rewards  

---

### Incentive Alignment Through Hybrid Distribution
The hybrid model balances:

- **Equal-share rewards** → compensate time, labor, and research  
- **Stake-weighted rewards** → reflect responsibility and influence  

This prevents domination by large actors while recognizing the security contribution of higher-stake entities.

---

### Fair Cost Attribution via Proposer Deposits
Because proposer deposits fund compensation:

- Governance costs are paid by those creating that cost  
- Spam proposals are discouraged  
- The Treasury is untouched  
- The system remains self-sustaining  

---

### Promotes Broad Participation and Decentralization
By providing guaranteed compensation:

- Smaller actors can sustainably participate  
- Governance remains diverse and representative  
- Participation rates and quorum stability increase  

---

## Path to Active

### Acceptance Criteria

This CIP becomes **Active** when:

* [ ] All new protocol parameters are implemented in the ledger.  
* [ ] Distribution logic executes correctly on testnet.  
* [ ] A governance action on mainnet distributes compensation correctly.  
* [ ] Sufficient community and technical review confirms correctness and consensus.

---

### Implementation Plan

* **Community Discussion & Review**  
* **Ledger Engineering Review**  
* **Implementation**  
* **Testnet Deployment**  
* **Hard Fork Activation**  
* **Post-Deployment Monitoring**

---

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
