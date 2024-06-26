---
CIP: 75
Title: Fair Stake Pool Rewards
Status: Proposed
Category: Ledger
Authors:
    - Tobias Fancee <tobiasfancee@gmail.com>
Implementors: []
Discussions:
    - https://forum.cardano.org/t/cip-fair-stakepool-rewards/109368
Created: 2022-10-21
License: CC-BY-4.0
---

## Abstract
The current reward sharing scheme of Cardano is unfair and anticompetitive. As a result, Cardano has become more centralized over time. The high minimum fixed fee and current pledge benefit favor large stakepools and leave small stakepools at a significant disadvantage. The current scheme allows large pools with low pledge to be more attractive than smaller pools with higher pledge leading to centralization and potential Goldfinger attacks. Furthermore, k, the parameter representing the optimal number of stakepools, is set too low resulting in an ineffective pledge benefit, the formation of multipools, and a low incentive for stakepools to increase pledge over time. Finally, the current setting of a0, the pledge influence parameter, gives an unnecessarily large boost in rewards to fully pledged private pools resulting in significantly less rewards for public pools and their delegators.

This proposal retains most of the original reward sharing scheme, but makes changes to ensure fairness, increase decentralization, and reduce the viability of Goldfinger attacks. By removing the minimum fixed fee, adjusting the pledge benefit, increasing k, and reducing a0, a more egalitarian network can be achieved.

## Motivation: why is this CIP necessary?

### Definitions

**Minimum Fixed Fee**
- Protocol parameter minPoolCost.

**Margin**
- Stakepool parameter PoolRate (percentage fee).

**Public Stakepool**
- A stakepool with a margin that is less than 100%.

**Private Stakepool**
- A stakepool that is not seeking delegation with a margin of 100%.

**Stakepool Operator (SPO)**
- The operator of a stakepool, can be a single person or an entity.

**Multipool**
- A group or brand of stakepools operated by a single entity or stakepool operator.

**ROS**
- Return on staking (often annualized and represented as a percentage of the initial investment).

**Leverage**
- The ratio between a stakepool’s total stake and pledge.

**Stakepool Viability Point**
- The amount of pledge required for a stakepool with zero delegations to distribute nonzero rewards to delegators (assuming minimum stakepool fees and ignoring luck in VRF block production, i.e., rewards are exactly proportional to stake).

**Stakepool Competitive Point**
- The amount of pledge required for a stakepool with zero delegations to offer the same ROS as a fully-saturated stakepool with zero pledge (assuming minimum stakepool fees).

**Stakepool Saturation Point**
- The maximum amount of total stake in a stakepool before total stakepool rewards are capped and ROS diminishes.

**Unsaturated Pledge Benefit Penalty**
- The amount of potential pledge benefit (in ADA or represented as a percentage) a stakepool loses for being unsaturated. The penalty is larger the smaller the stakepool.

**Minimum Attack Vector (MAV)**
- Also known as the Nakamoto Coefficient, the MAV is the minimum number of entities required to capture more than 50% of a network. In the context of Cardano, this refers to the minimum number of SPOs required to capture more than 50% of active stake.

**Goldfinger Attack**
- An attack on a cryptocurrency protocol where the objective is to attack the protocol or network in order to make profit by shorting the native cryptocurrency.

**Sybil Attack**
- An attack on an online system where an entity tries to take over the network by creating many identities or nodes.

### The Current Rewards Equation

In section 10.8 Rewards Distribution Calculation of “A Formal Specification of the Cardano Ledger” (git revision 1.1-486-g301fede) the current rewards calculation equation is described by the function $maxPool$:

$$maxPool = \frac{R}{1 + a0} \cdot (o + p \cdot a0 \cdot \frac{o - p \frac{z0 - o}{z0}}{z0})$$

where: $maxPool$ = maximum rewards for a stake pool, $R = ((reserve \cdot rho) + fees) \cdot (1 - tau), o = min(poolstake / totalstake, z0) = z0$ for fully saturated pool, $p = min(pledge / totalstake, z0)$, and $z0 = 1 / k$

Current protocol parameters: $k = 500, rho = 0.003, a0 = 0.3$, and $tau = 0.2$

The current reward sharing scheme which includes the rewards calculation equation and the minimum fixed fee are inadequate in promoting decentralization as evident by Cardano’s currently low MAV relative to k. This is due to its anticompetitive features which are discussed in this section.

### The Minimum Fixed Fee

The minimum fixed fee or minPoolCost was apparently included for additional sybil attack protection. However, it’s effect has been the opposite allowing stakepools with low pledge to offer greater rewards than pools with higher pledge in some cases. Moreover, the minimum fixed fee is certainly problematic as it places an unfair burden on small pools by enforcing a disproportionally larger fee than that of larger stakepools, reducing the ROS of small pools and incentivizing delegation to larger stakepools. This leads to centralization of the network around established stakepools, leaving less opportunity for smaller stakepools that may have greater pledge or community presence.

### The Current Pledge Benefit

The current pledge benefit in the rewards equation is a function of the total stake in a pool that is significantly biased towards large stakepools that are close to saturation. Specifically, the current equation penalizes the pledge benefit of small pools. The smaller the pool, the larger the penalty. This unsaturated pledge benefit penalty combined with the minimum fixed fee leads to illogical rewards where large pools with low pledges can offer delegators higher ROS than smaller pools with significantly higher pledges. As a result, delegators are incentivized to delegate to larger stakepools even if they have lower pledges leading to network centralization.

The unsaturated pledge benefit penalty is part of the current rewards calculation equation and can be described by the equation:

$$Unsaturated Pledge Benefit Penalty = \frac{R}{1 + a0} \cdot p \cdot a0 \cdot \frac{p \frac{z0 - o}{z0}}{z0}$$

See [UnsaturatedPledgeBenefitPenalty.xlxs](./UnsaturatedPledgeBenefitPenalty.xlxs) to calculate the current unsaturated pledge benefit penalty for a stakepool.

### Goldfinger Attacks

The minimum fixed fee and current pledge benefit introduce a potential security threat to the Cardano protocol: Goldfinger attacks. The current reward scheme puts all small stakepools at a disadvantage regardless of pledge centralizing the network around established stakepools rather than pools with the most attractive pledge and fee combination. When SPOs with low stake (pledge) in the protocol are allowed to dominate consensus, they have a potential alternative incentive to attack the network in order make profit by shorting ADA. Because these stakepools have low stake in the protocol (operate with low or even zero pledge), they would be able make profit without any significant loss other than future staking rewards. With leverage, the attackers could make significantly more profit shorting ADA than years of staking.

### The Optimal Number of Stakepools, k

The current setting of k, the parameter representing the optimal number of stakepools, is set too low to provide an effective pledge benefit leaving little incentive for pools to increase pledge over time. Specifically, with a small k value, a fully pledged pledge benefit is far from achievable for most SPOs. An ineffective pledge benefit leads to the formation of multipools with high leverage, as operators can split their pledge into multiple stakepools without a significant decrease in ROS in the resulting stakepools.

### The Pledge Influence Parameter, a0

The current setting of a0, the pledge influence parameter, gives an unnecessarily large boost in rewards to very high pledge and fully pledged private pools. Specifically, the current setting of a0 results in approximately 30% greater rewards for fully pledged private pools. This boost in rewards unfortunately results significantly less rewards for public pools that commonly have low pledges relative to the saturation point. Given that most Cardano users are delegators and not SPOs, this exclusive boost for high pledge pools decreases Cardano’s overall attractiveness as a staking protocol. Additionally, having a high a0 setting only accelerates the wealth (ADA) disparity between large entities operating private pools and delegators who make up majority of the ecosystem.

## Specification

### The Proposed Rewards Calculation Equation

The proposed rewards calculation equation is a modification of the current equation that removes the unsaturated pledge benefit penalty:

$$maxPool = \frac{R}{1 + a0} \cdot (o + p \cdot a0 \cdot \frac{o}{z0})$$

where: $maxPool$ = maximum rewards for a stake pool, $R = ((reserve \cdot rho) + fees) \cdot (1 - tau), o = min(poolstake / totalstake, z0) = z0$ for fully saturated pool, $p = min(pledge / totalstake, z0)$, and $z0 = 1 / k$

### The Proposed Parameter Values

The proposed parameter values are the following:

| Name of the Parameter | New Parameter (Y/N) | Deleted Parameter (Y/N) | Proposed Value | Summary Rationale for Change |
|-----------------------|---------------------|-------------------------|----------------|------------------------------|
| minPoolCost           | N                   | Y                       | N/A            | See Rationale Section.       |
| stakePoolTargetNum    | N                   | N                       | 1000           | See Rationale Section.       |
| poolPledgeInfluence   | N                   | N                       | 0.2            | See Rationale Section.       |

## Rationale: how does this CIP achieve its goals?

### Principles

The main goal of this proposal is to ensure fairness in stakepool rewards. This is achieved by including these principles in the design:

1.	Eliminate all anticompetitive features. These include any parts of the design that treat stakepools differently based on anything other than pledge or declared fees.
2.	Ensure that the pledge benefit is fair and corresponds to a consistent boost in ROS no matter pool size. In other words, assuming the same fees, two pools with the same pledge should always offer the same ROS.
3.	Ensure that the pledge benefit is effective and incentivizes increasing pledge over time.
4.	Reduce the large rewards disparity between private pools and delegators and increase Cardano’s overall attractiveness as a staking protocol.

### Explanation

The current reward sharing scheme includes two notable anticompetitive features. These features are the minimum fixed fee and the unsaturated pledge benefit penalty. This proposal removes these features to ensure fairness and promote adequate competition between stakepools. Removing these anticompetitive features promotes delegation to pools with most attractive pledge and fee combinations rather than established large pools and multipools. This results in fairer competition among stakepools and lower possibility of Goldfinger attacks as the pledge benefit is effective at all stakepool sizes. Greater decentralization is also possible as small stakepools will be able to offer competitive returns and potentially extract delegation from low pledge multipools.

To ensure a more effective pledge benefit and incentivize increasing pledge over time, this proposal increases the current value of k from 500 to 1000. This allows a fully pledged pledge benefit to be closer for all SPOs and will force multipools to split pledge and reduce pledge benefit if they wish to continue operating with the same leverage. Additionally, a change in the value of k will give many stagnant delegators an incentive to reconsider their delegations giving smaller stakepools an opportunity at increasing delegation.

Finally, to reduce the large rewards disparity between private pools and delegators, this proposal reduces the setting of a0 from 0.3 to 0.2. The current setting of a0 results in approximately 30% greater rewards for fully pledged private pools. This proposal reduces this disparity to 20% to create a fairer rewards distribution. The result is an overall increase in rewards for delegators as most public pools operate with low pledges relative to the saturation point. Given that delegators make up majority of users, this reduction in a0 will make Cardano a much more competitive staking investment in contrast to other blockchains.

These proposed changes to Cardano’s reward sharing scheme are aimed at ensuring fairness, increasing decentralization, and creating a more egalitarian staking ecosystem.

### Test Cases

Stakepool viability and competitive points can give some insight into the fairness of the reward scheme. These points are essentially start-up costs required to run viable and competitive stakepools. These points are very high and out of reach for many SPOs with the current scheme. This proposal effectively minimizes these points.

Current stakepool viability point: ~625,000 ADA

Current stakepool competitive point: ~19,000,000 ADA

Proposal stakepool viability point: 1 ADA

Proposal stakepool competitive point: 1 ADA

See [FairStakepoolRewards.xlxs](./FairStakepoolRewards.xlsx) to compare stakepool ROS between the current and proposed scheme.

### Backward Compatibility

This proposal includes parameter changes, one parameter removal, and a change to the rewards calculation. Because of the parameter removal and changes to the rewards calculation, a hardfork will be necessary for implementation.

## Path to Active

### Acceptance Criteria

Each stage will be an individual protocol update. The first two updates will be protocol parameter updates. The third and final update will require a hardfork.

Before implementation, engineering and research teams must review the feasibility and potential consequences of the proposal, create the implementation for each update, and decide on the time interval between updates.

1. The protocol update is created, including all necessary changes.
2. The raw transaction for the protocol update is built.
3. Transaction is signed.
4. Transaction is submitted.
5. Protocol update is confirmed.

### Implementation Plan

Implementation can be staged to reduce shock to the network:

1.	Decrease minPoolCost from 340 ADA to 100 ADA and increase k from 500 to 750.
2.	Increase k from 750 to 1000, decrease minPoolCost from 100 ADA to 0 ADA, and decrease a0 from 0.3 to 0.2.
3.	Remove minPoolCost from the protocol and implement the new rewards calculation equation.

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
