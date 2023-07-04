---
CIP: 74
Title: Set minPoolCost to 0
Authors:
 - Robin of Loxley <adarobinhood@tutanota.com>
Category: Ledger
Status: Proposed
Created: 2022-10-17
Discussions:
 - https://forum.cardano.org/t/cip-69-set-minpoolcost-to-0/109309
 - https://github.com/cardano-foundation/CIPs/pull/358
Implementors: []
License: CC-BY-4.0
---

## Abstract

A minPoolCost of 340 ADA/epoch makes popularity the basis for pool desirability, causing preferred traits like pledge and performance to be overshadowed. This has promoted stake to centralize with operators who are effective at campaigning, but do not necessarily have any stake in the system of their own. We want to create a fair marketplace for stake pools that allows the network to decentralize with time; minPoolCost is averse to that goal.

## Motivation: why is this CIP necessary?

Popularity is currently the basis for desirability and defines which pools will receive high rewards and which won't. A pool with high popularity, low pledge, and low performance will offer significantly higher rewards than a pool with low popularity, high pledge, and high performance. With equal fee structures, a pool with 19.5MM pledge that is just starting out will be less desirable than a saturated pool with no pledge; a pool with 6MM pledge and perfect performance will be less desirable than a pool with 0 pledge and 90% performance. This makes it apparent we are not incentivizing a secure stable network and the network cannot self-correct if stake ends up in the wrong place.

The entirety of IOG's research is without a minPoolCost or any other minimum fee. The game theory design relied on stake pool operators (SPOs) having the ability to compete in a fair marketplace of pool desirability by modifying their pledge, cost, and margin in relation to other pools. Adding a minimum value to cost has removed the opportunity for operators to control their desirability outside of first gaining popularity. As a pool gains popularity it disproportionately gains desirability, allowing the operator to lower pledge and raise margin, while still maintaining higher desirability than a less popular pool with better fee structure and higher pledge. Operators can lie about their costs while still gaining utility. As long as the operator can maintain popularity they can exceed K indefinitely by opening more and more pools with a reward bonus instead of penalty. This significantly lowers the cost of a sybille attack, while making sybille behavior highly desirable and profitable. A sybille attacker, or anybody for that matter, should need stake in the system to compete for delegation, not just a rigorous marketing campaign.

The network is incentivizing the wrong behavior from SPOs which has made the network highly leveraged.

"The higher the leverage of the system, the worse its security [...] The lower the leverage of a blockchain system, the higher its degree of decentralization."

High security should always be the priority.

### Desired effects

Stake pool desirability will become a function of pledge, performance, cost, and margin instead of only popularity. Operators will need to consolidate and grow pledge while moderating fees to remain competitive with other pools on the market.

SPOs define their cost as an absolute value when submitting their registration.cert. They do not reference minPoolCost. Changing minPoolCost will not change any predefined costs. Pools that wish to leave their cost as-is can do so without any input. Pools that wish to lower their cost below 340 ADA/epoch will have to submit an updated registration.cert.

## Specification

"minPoolCost": 0

## Rationale: how does this CIP achieve its goals?

98% of all pools have their cost at 340 ADA/epoch or within + 10. As the price of ADA went from $0.3 to $3, almost no operators modified their cost. As the price of ADA dropped from $3 to $0.3, almost no operators modified their cost. This shows that the minPoolCost is not related to the real cost of operating a pool and the cost of a pool is no longer related to its utility.

We have a large body of research accompanied by simulations showing that removing minPoolCost will increase decentralization of the network and begin incentivizing the right behavior from SPOs and the delegating community.

A minPoolCost is not in Cardano's design specification. ALL published research is in favor of setting minPoolCost to 0.

### Research and References

Design Specification for Delegation and Incentives in Cardano
https://github.com/input-output-hk/cardano-ledger/releases/latest/download/shelley-delegation.pdf

Reward Sharing Schemes for Stake Pools
https://arxiv.org/pdf/1807.11218.pdf

Preventing Sybil attacks
https://iohk.io/en/blog/posts/2018/10/29/preventing-sybil-attacks/

Stake Pools in Cardano
https://iohk.io/en/blog/posts/2018/10/23/stake-pools-in-cardano/

Incentive Paper Lecture Series (Parts 1-7)
https://www.youtube.com/playlist?list=PLFLTrdAG7xRbAqhF3Tg8BeAea7Ard-ttn

The general perspective on staking in Cardano

## Path to Active

### Acceptance Criteria

- [ ] A protocol parameter update assigning `minPoolCost` to `0`.

### Implementation Plan

- [ ] Agreement by the Ledger team as defined in [CIP-0084](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0084) under _Expectations for ledger CIPs_ including "expert opinion" on changes to rewards & incentives.

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
