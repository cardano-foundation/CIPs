---
CIP: 82
Title: Improved Rewards Scheme Parameters
Status: Proposed
Category: Ledger
Authors:
    - Tobias Fancee <tobiasfancee@gmail.com>
Implementors: []
Discussions:
    - https://forum.cardano.org/t/cip-improved-rewards-scheme-parameters/112409
Created: 2022-01-03
License: CC-BY-4.0
---

## Abstract

The current parameter settings of Cardano's rewards sharing scheme leave much to be desired in terms of fairness and promoting decentralization. minPoolCost puts small stakepools at a significant disadvantage. Replacing minPoolCost with a minPoolRate will ensure a level playing field for stakepools while providing sufficient sybil attack resistance. Additionally, the current setting of k, the optimal number of stakepools, is too low to provide an adequate pledge benefit. Increasing k will make the pledge benefit more effective and get delegations moving in hopes of helping single pool operators gain delegations.

The parameter changes in this proposal are an optimization of the current settings and are meant to improve the fairness and decentralization of Cardano. Furthermore, all changes suggested in this proposal have been specifically voiced by the Cardano community.

## Motivation: why is this CIP necessary?

### Definitions

**Stakepool Operator (SPO)**
- The operator of a stakepool, can be a single person or an entity.

**Multipool**
- A group or brand of stakepools operated by a single entity or stakepool operator.

**ROS**
- Return on staking (often annualized and represented as a percentage of the initial investment).

**Stakepool Viability Point**
- The amount of pledge required for a stakepool with zero delegations to distribute nonzero rewards to delegators (assuming minimum stakepool fees and ignoring luck in VRF block production, i.e., rewards are exactly proportional to stake).

**Stakepool Competitive Point**
- The amount of pledge required for a stakepool with zero delegations to offer the same ROS as a fully-saturated stakepool with zero pledge (assuming minimum stakepool fees).

**Stakepool Saturation Point**
- The maximum amount of total stake in a stakepool before total stakepool rewards are capped and ROS diminishes.

**Minimum Attack Vector (MAV)**
- Also known as the Nakamoto Coefficient, the MAV is the minimum number of entities required to capture more than 50% of a network. In the context of Cardano, this refers to the minimum number of SPOs required to capture more than 50% of active stake.

**Sybil Attack**
- An attack on an online system where an entity tries to take over the network by creating many identities or nodes.

### Cardano’s Declining MAV

Cardano’s declining MAV is a real problem as the network matures and gains more users. Ideally MAV should increase or stay consistent over time. However, this is currently not the case. This trend points to potential problems with the parameters set in the rewards sharing scheme. Now that staking on the network has matured, it is time to re-examine the rewards sharing scheme parameters and seek optimization. This proposal suggests changes that aim to increase the fairness and decentralization of the Cardano network.

### minPoolCost

minPoolCost sets a minimum fixed fee that a stakepool must collect from an epoch’s rewards before distributing to delegators. This parameter was added to the rewards sharing scheme to provide additional sybil attack protection. While this parameter has been successful at deterring sybil attacks on the Cardano network, it has been at the expense of fairness and decentralization. minPoolCost imposes a proportionally greater staking fee on small stakepools in contrast to larger pools. This discrepancy results in many small pools being unviable and the network centralizing around established pools. It is not uncommon for small stakepools with higher pledge to offer inferior rewards to that of large stakepools with much lower pledge. In this way, minPoolCost reduces the effectiveness of pledge in the rewards scheme. In order to create a level playing field for stakepools and increase the effectiveness of pledge, minPoolCost must be removed from the protocol.

### minPoolRate

The current pledge benefit favors established pools close to saturation as a means of sybil attack protection. Specifically, this property combats high pledge sybil pools (~1 mil ADA pledge) that could be set up by large entities such as centralized exchanges. In contrast to minPoolCost, the pledge benefit’s built-in sybil attack protection is significantly less aggressive and does not affect the viability of stakepools. In this way, it is a useful mechanism to combat sybil pools. However, the pledge benefit on its own has no means to combat zero fee sybil pools. Without minPoolCost, zero fee sybil pools could offer greater rewards than that of established stakepools that must set fees to pay for continued operation. In order to combat zero fee sybil pools without minPoolCost, minPoolRate must be added to the protocol. minPoolRate will set a minimum margin or percentage fee that operators can extract from an epoch’s staking rewards. This new parameter will protect established stakepools by ensuring that they collect sufficient revenue from operation while offering a competitive ROS. Additionally, minPoolRate can be updated to reflect current economic conditions. As minPoolRate enforces a proportional minimum fee, it does not affect the viability of stakepools. Unlike minPoolCost, minPoolRate will be able to provide sufficient sybil attack protection with the pledge benefit while maintaining a level playing field for stakepools. minPoolRate was originally proposed in CIP-0023.

### k, the optimal number of stakepools

k represents the optimal number of stakepools that the Cardano network can support. This is achieved through a saturation mechanism where after exceeding a saturation point a stakepool will earn no additional rewards. A stakepool larger than the saturation point will offer lower rewards than a stakepool at the saturation point. The parameter k is used to tune the saturation point. In addition to tuning the saturation point, k also affects the pledge benefit. The maximum pledge benefit exists when a pool is fully saturated. Therefore, increasing k will increase the number of optimal stakepools, decrease the saturation point, and make it easier for stakepools to achieve the maximum pledge benefit. Increasing the effect of the pledge benefit on rewards is imperative, as pledge currently has little effect on rewards allowing low pledge pools to proliferate through marketing alone. Furthermore, increasing k can be used to get stale delegations moving. This is especially useful in the case of saturated multipools, where delegators would have to reconsider their delegation potentially assisting small and medium sized pools. Any delegation flow from multipools to single pool operators will increase the decentralization of Cardano.

## Specification

This CIP proposes several parameter changes. In order to give SPOs and delegators enough time to react to the changes, this CIP is divided into 4 stages. The proposed time interval between stages is 3 epochs or 15 days. However, it is up to the implementors to determine the best time interval between stages. Parameters are changed in the following stages:

### Stage 1: minPoolCost decreased to 170 ADA

| Name of the Parameter | New Parameter (Y/N) | Deleted Parameter (Y/N) | Proposed Value | Summary Rationale for Change |
|-----------------------|---------------------|-------------------------|----------------|------------------------------|
| minPoolCost           | N                   | N                       | 170000000      | See Rationale Section.       |

### Stage 2: minPoolCost deleted, minPoolRate of 3% implemented (requires hardfork)

| Name of the Parameter | New Parameter (Y/N) | Deleted Parameter (Y/N) | Proposed Value | Summary Rationale for Change |
|-----------------------|---------------------|-------------------------|----------------|------------------------------|
| minPoolCost           | N                   | Y                       | N/A            | See Rationale Section.       |
| minPoolRate           | Y                   | N                       | 0.03           | See Rationale Section.       |

In order to ensure the compatibility of existing stakepool registration certificates with this CIP, the variable poolRateEff must be added to the protocol. This variable will be the effective margin used during stakepool fee calculation. Following the hardfork, poolRate will only be the value set by SPOs. poolRate will be superseded by minPoolRate if its value is lower than minPoolRate. This is demonstrated in the definition of poolRateEff:

$$poolRateEff = max(poolRate, minPoolRate)$$

### Stage 3: k increased to 750

| Name of the Parameter | New Parameter (Y/N) | Deleted Parameter (Y/N) | Proposed Value | Summary Rationale for Change |
|-----------------------|---------------------|-------------------------|----------------|------------------------------|
| stakePoolTargetNum    | N                   | N                       | 750            | See Rationale Section.       |

### Stage 4: k increased to 1000

| Name of the Parameter | New Parameter (Y/N) | Deleted Parameter (Y/N) | Proposed Value | Summary Rationale for Change |
|-----------------------|---------------------|-------------------------|----------------|------------------------------|
| stakePoolTargetNum    | N                   | N                       | 1000           | See Rationale Section.       |

## Rationale: how does this CIP achieve its goals?

### Principles

1.	Propose changes voiced by the community.
2.	Make Cardano staking fairer by eliminating aggressive anticompetitive features.
3.	Increase the effect of the pledge benefit on staking rewards.
4.	Get stale delegations moving and allow users to reconsider their delegation.
5.	Maintain sufficient sybil attack protection.

### Explanation

#### Stage 1: minPoolCost is decreased to 170 ADA

Stage 1 reduces minPoolCost from 340 ADA to 170 ADA. 170 ADA is proposed because it is half of the current minPoolCost and is close to what the USD value of minPoolCost was during the launch of Shelley. This value is more than sufficient to allow established community pools to stay profitable while enabling smaller pools to be more competitive. This value also maintains sybil attack resistance.

#### Stage 2: minPoolCost is deleted, minPoolRate of 3% is implemented (requires hardfork)

Stage 2 introduces the largest change to the network by deleting minPoolCost from the protocol in favor of a minPoolRate of 3%. 3% is proposed, as it allows established community pools to stay profitable when competing against minimum fee pools. This in combination with the pledge benefit provide sufficient sybil attack resistance while leveling the playing field for all stakepools. As pool size is significantly less important following this stage, pledge becomes a more important factor in choice of delegation. In contrast, Lido, Ethereum’s most popular liquid staking DApp, applies a 10% fee on participants' staking rewards.

#### Stage 3: k is increased to 750

Stage 3 increases k from 500 to 750. The purpose of stage 3 and stage 4 is two-fold. Firstly, increasing k increases the pledge benefit. The more effective the pledge benefit, the greater Cardano’s sybil attack resistance. Secondly, increasing k may get stale delegations moving again by oversaturating large pools. This will cause many delegators to reconsider their delegation, potentially helping smaller community pools find delegations. Increasing k is split into two stages to give SPOs sufficient time to react to the change. Furthermore, it is imperative that k is increased after stage 2, as small stakepools will only be competitive after minPoolCost has been removed.

#### Stage 4: k is increased to 1000

Stage 4 increases k from 750 to 1000. Stage 4 will further improve the pledge benefit and get more delegations moving. This is the final stage of this proposal.

### Test Cases and Sybil Attack Resistance

Below are test cases for the current rewards scheme and each stage of this proposal. The calculated values assume all pools are operating with minimum fees. Sybil pools are assumed to be small pools with no delegations. Community pools are assumed to be pools with significant delegation. As demonstrated below, this proposal allows community pools to have sufficient revenue (higher than the USD value of minPoolCost at the launch of Shelley) while creating a level playing field for all stakepools. Sybil attack resistance is maintained at every stage, as community pool ROS remains higher than sybil pool ROS. Data used for calculations was approximated from epoch 385. See [ImprovedRewardsSchemeParameters.xlxs](./ImprovedRewardsSchemeParameters.xlsx) for more test cases.

#### Current Rewards Scheme

Stakepool Viability Point: ~670,000 ADA

Stakepool Competitive Point: ~20,000,000 ADA

| Pool Type | Pool Stake        | Pool Pledge      | Pool Epoch Revenue | Delegator ROS         |
|-----------|-------------------|------------------|--------------------|-----------------------|
| Sybil     | 100,000.00 ADA    | 100,000.00 ADA   | 340 ADA            | Below Viability Point |
| Sybil     | 1,000,000.00 ADA  | 1,000,000.00 ADA | 340 ADA            | 1.2339%               |
| Community | 10,000,000.00 ADA | 100,000.00 ADA   | 340 ADA            | 3.5213%               |
| Community | Saturated         | 1,000,000.00 ADA | 340 ADA            | 3.7567%               |

#### Proposed - Stage 1

Stakepool Viability Point: ~335,000 ADA

Stakepool Competitive Point: ~16,500,000 ADA

| Pool Type | Pool Stake        | Pool Pledge      | Pool Epoch Revenue | Delegator ROS         |
|-----------|-------------------|------------------|--------------------|-----------------------|
| Sybil     | 100,000.00 ADA    | 100,000.00 ADA   | 170 ADA            | Below Viability Point |
| Sybil     | 1,000,000.00 ADA  | 1,000,000.00 ADA | 170 ADA            | 2.4977%               |
| Community | 10,000,000.00 ADA | 100,000.00 ADA   | 170 ADA            | 3.6498%               |
| Community | Saturated         | 1,000,000.00 ADA | 170 ADA            | 3.7749%               |

#### Proposed - Stage 2

Stakepool Viability Point: 1 ADA

Stakepool Competitive Point: 1 ADA

| Pool Type | Pool Stake        | Pool Pledge      | Pool Epoch Revenue | Delegator ROS |
|-----------|-------------------|------------------|--------------------|---------------|
| Sybil     | 100,000.00 ADA    | 100,000.00 ADA   | 1.52 ADA           | 3.6615%       |
| Sybil     | 1,000,000.00 ADA  | 1,000,000.00 ADA | 15.24 ADA          | 3.6617%       |
| Community | 10,000,000.00 ADA | 100,000.00 ADA   | 152.42 ADA         | 3.6631%       |
| Community | Saturated         | 1,000,000.00 ADA | 1081.06 ADA        | 3.6773%       |

#### Proposed - Stage 3

Stakepool Viability Point: 1 ADA

Stakepool Competitive Point: 1 ADA

| Pool Type | Pool Stake        | Pool Pledge      | Pool Epoch Revenue | Delegator ROS |
|-----------|-------------------|------------------|--------------------|---------------|
| Sybil     | 100,000.00 ADA    | 100,000.00 ADA   | 1.52 ADA           | 3.6615%       |
| Sybil     | 1,000,000.00 ADA  | 1,000,000.00 ADA | 15.24 ADA          | 3.6620%       |
| Community | 10,000,000.00 ADA | 100,000.00 ADA   | 152.49 ADA         | 3.6639%       |
| Community | Saturated         | 1,000,000.00 ADA | 720.44 ADA         | 3.6853%       |

#### Proposed - Stage 4

Stakepool Viability Point: 1 ADA

Stakepool Competitive Point: 1 ADA

| Pool Type | Pool Stake        | Pool Pledge      | Pool Epoch Revenue | Delegator ROS |
|-----------|-------------------|------------------|--------------------|---------------|
| Sybil     | 100,000.00 ADA    | 100,000.00 ADA   | 1.52 ADA           | 3.6615%       |
| Sybil     | 1,000,000.00 ADA  | 1,000,000.00 ADA | 15.24 ADA          | 3.6624%       |
| Community | 10,000,000.00 ADA | 100,000.00 ADA   | 152.52 ADA         | 3.6646%       |
| Community | Saturated         | 1,000,000.00 ADA | 542.82 ADA         | 3.6932%       |

### Backward Compatibility

This proposal includes several parameter changes and changes to ledger rules. Specifically, stage 2 of this proposal will require a hardfork to introduce a new parameter, delete a parameter, and modify the stakepool fee calculation equation. As mentioned in the specification section, the stakepool fee calculation equation must be modified in order to ensure current stakepool registration certificates are compatible with this CIP.

## Path to Active

### Acceptance Criteria

#### For Stages 1, 3, and 4
1. The raw transaction for the parameter update is built.
2. Transaction is signed.
3. Transaction is submitted.
4. Parameter update is accepted by majority of the network.
5. Parameter update is confirmed.

#### For Stage 2

1. Necessary research and development is completed for the changes to the ledger rules.
2. New version of cardano-node supporting the changes to the ledger rules is released.
2. Raw transaction signaling the hardfork is built.
3. Transaction is signed.
4. Transaction is submitted.
5. Hardfork is accepted by majority of the network.
6. Hardfork and changes to ledger rules are confirmed.

### Implementation Plan

Each stage will be an individual update. Stages 1, 3, and 4 will be parameter updates. Stage 2 will require a hardfork.

Before implementation, engineering and research teams must review the feasibility and potential consequences of the proposal, create the implementation for each update, and decide on the time interval between updates.

As previously mentioned, implementation will occur in the following stages:

1. minPoolCost is decreased to 170 ADA
2. minPoolCost is deleted, minPoolRate of 3% is implemented (requires hardfork)
3. k is increased to 750
4. k is increased to 1000

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
