---
CIP: XXXX
Title: Compensatory Ledger Mechanism
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

### **1. Governance Fatigue**
Uncompensated governance labor leads to declining participation over time.

### **2. Centralization Risks**
Only large, well-funded entities can consistently afford to participate, reducing diversity and representation.

### **3. Low Governance Participation / Quorum Instability**
Without compensation, new and smaller actors lack incentives to engage, harming governance quality.

### **4. Misaligned Incentives**
Proposers incur no cost commensurate with the burden placed on reviewers and voters.

### **5. Need for a Deterministic, Automated Mechanism**
Any off-chain or trust-based compensation scheme introduces friction and reduces security.

The CLM addresses these issues by:
- Making governance participation economically feasible  
- Ensuring compensation flows only to active participants  
- Funding compensation from proposer deposits, aligning costs with governance load  
- Executing payments entirely through the ledger for maximum reliability  

---

## Specification

### 1. New Protocol Parameters

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

### 2. Compensation Trigger

Upon finalization of any governance action requiring a deposit—whether it **passes**, **fails**, or **expires**—the ledger automatically:

1. Finalizes deposit accounting  
2. Creates the compensation pools  
3. Distributes funds to voting governance actors  

This occurs atomically during governance-action completion.

---

### 3. Compensation Pot Creation

Let `govDeposit` be the required deposit for the governance action.

```
TotalCompensation =
  govDeposit × (ccCompensationRate + drepCompensationRate + spoCompensationRate)
```

Split into:

```
CC_Pool   = govDeposit × ccCompensationRate
DRep_Pool = govDeposit × drepCompensationRate
SPO_Pool  = govDeposit × spoCompensationRate
```

The remainder is refund-eligible for the proposer if the action passes.

---

### 4. Distribution Rules

#### **4.1 Compensation to Constitutional Committee (Equal Share)**

Only voting CC members are compensated.

```
Payout_CC = CC_Pool / numberOfVotingCCMembers
```

Non-voting CC members receive 0.

---

#### **4.2 DRep Compensation (Hybrid Model)**

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

#### **4.3 SPO Compensation (Hybrid Model)**

##### Equal-Share Portion
```
EqualShareAmount = SPO_Pool × (1 − spoWeightFactor)
Payout_Equal_SPO = EqualShareAmount / numberOfVotingSPOs
```

##### Stake-Weighted Portion  
Weighted by **block-producing active stake**.

```
WeightedAmount = SPO_Pool × spoWeightFactor
Payout_Weighted_SPO =
  WeightedAmount × (activeStakeOfSPO / totalActiveStakeOfVotingSPOs)
```

##### Total SPO Payout
```
Payout_SPO = Payout_Equal_SPO + Payout_Weighted_SPO
```

---

### 5. Deposit Finality

The compensation portion of the deposit:

- **is always consumed**, regardless of proposal outcome  
- **is never refundable to the proposer**  

This internalizes governance processing costs.

---

## Rationale: how does this CIP achieve its goals?

### **1. Ledger-Native Implementation Ensures Maximum Reliability**
All compensation logic is implemented inside ledger rules.  
This guarantees:

- Deterministic execution  
- No dependency on smart contracts  
- No treasury governance or manual intervention  
- A trust model equivalent to ADA staking rewards  

---

### **2. Incentive Alignment Through Hybrid Distribution**
The hybrid model balances:

- **Equal-share rewards** → compensate time, labor, and research  
- **Stake-weighted rewards** → reflect responsibility and influence  

This prevents domination by large actors while recognizing the security contribution of higher-stake entities.

---

### **3. Fair Cost Attribution via Proposer Deposits**
Because proposer deposits fund compensation:

- Governance costs are paid by those creating that cost  
- Spam proposals are discouraged  
- The Treasury is untouched  
- The system remains self-sustaining  

---

### **4. Promotes Broad Participation and Decentralization**
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
