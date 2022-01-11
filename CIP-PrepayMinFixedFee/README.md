---
CIP: ?
Title: Prepay Min Fixed Fee
Authors: Odin Stark <odinspool@gmail.com>, Shawn McMurdo <shawn_mcmurdo@yahoo.com>
Comments-URI: https://forum.cardano.org/t/prepay-min-fixed-fee-cip/81605
Status: Draft
Type: Standards
Created: 2021-08-08
License: CC-BY-4.0
---

## Simple Summary

Create a more fair marketplace for stakepools by paying the minimum fixed pool fee to qualifying pools before calculating pool and delegator rewards.

## Abstract

The current minimum fixed pool fee places a large and unfair burden on delegators to pools with smaller amounts of stake.
This incentivizes people to delegate to pools with higher stake causing centralization and creating an unequal playing field for stakepool operators.
Paying the minimum fixed pool fee before calculating pool and delegator rewards eliminates the imbalance between stakepools with less or more stake allowing for fair competition between stakepools and more fair rewards for delegators to stakepools with less stake.

## Motivation

Paying the minimum fixed pool fee before calculating pool and delegator rewards creates a more fair marketplace for all stakepool operators, gives delegators to pools with less stake more fair rewards, and increases decentralization, which is a goal of Cardano.

## Specification

The minimum fixed pool fee, minPoolCost, will be paid to each pool making at least one block in the epoch out of the total rewards for the epoch before the normal payment of rewards to pools and delegators.
Only the minimum fixed fee is prepaid. Any difference between the minPoolCost and the pool's declared fixed fee would still be paid out of the pool rewards as is done now.
This proposal does not change the process for payment of the pool variable fee.
This proposal does not change the amount of ADA coming from the reserve or going to the treasury.
It adjusts the payment of rewards to pools and delegators only.

We introduce a cap on the prepaid fees of 2 * minPoolCost * stakePoolTargetNum (aka k or nOpt).
We will call this the prepaidFeeCap.
If there are more than 2 * stakePoolTargetNum block producing pools in an epoch then the prepaidFeeCap is divided equally among all pools making blocks.  In this case, each pool will receive somewhat less than the minimum fixed fee as the prepaid part of the pool rewards. The difference between the prepaid amount and the pool’s declared fixed fee would be paid out of the pool rewards as is done currently.


## Rationale

To clarify the rationale and better understand the impact that this change would have, we present the following examples.

Given:
* 4 pools (A, B, C, and D) having total stake of 1m, 5m, 10m, and 50m ADA respectively.
* Each pool has a pledge of 100k ADA, fixed fee of 340 ADA and variable fee of 1%.
* Each pool has an example delegator who stakes 100k ADA.
* In an epoch, the pools have equal luck and perform equally well, making blocks proportional to their stake (A = 1, B = 5, C = 10, and D = 50).
* The total rewards available after treasury contribution is 21m ADA.
* The total number of blocks minted is 21k.

This gives us:
* 21m ADA / 21k blocks = 1000 ADA per block (current)
* (21m ADA - (1000 pools * 340 ADA)) / 21k blocks = 983.8 ADA per block (proposed)
* Current Pool A rewards after fees = 1000 - 340 - (660 * 0.01) = 653.4 ADA
* Proposed Pool A rewards after fees = 983.8 - (983.8 * 0.01) = 974.0 ADA
* Current Pool B rewards after fees = 5000 - 340 - (4660 * 0.01) = 4613.4 ADA
* Proposed Pool B rewards after fees = 4919 - (4919 * 0.01) = 4869.8 ADA
* Current Pool C rewards after fees = 10000 - 340 - (9660 * 0.01) = 9563.4 ADA
* Proposed Pool C rewards after fees = 9838 - (9838 * 0.01) = 9739.6 ADA
* Current Pool D rewards after fees = 50000 - 340 - (49660 * 0.01) = 49163.4 ADA
* Proposed Pool D rewards after fees = 49190 - (49190 * 0.01) = 48698.1 ADA

The chart below shows the amount of fees earned by the SPO, the amount of rewards earned by the delegator and the effective fee percent paid by the delegator for each of the 4 pools in the current and proposed models.

Who     Current         Proposed
---     -------         --------
SPO A   346.6 ADA       349.8 ADA
Del A    65.3 ADA        97.4 ADA
Fee A    34.7%            2.6%

SPO B   386.6 ADA       389.2 ADA
Del B    92.3 ADA        97.4 ADA
Fee B     7.7%            2.6%

SPO C   436.6 ADA       438.4 ADA
Del C    95.6 ADA        97.4 ADA
Fee C     4.4%            2.6%

SPO D   836.6 ADA       831.9 ADA
Del D    98.3 ADA        97.4 ADA
Fee D     1.7%            2.6%

As you can see from this example, a delegator delegating to a pool with 50m ADA total stake receives over 50% more rewards (98.3 / 65.3) than if they delegated to a pool with 1m total stake, even though the pools are performing equally well.
This is a flaw in the current design that causes centralization to popular pools rather than better performing pools.
The proposal creates a much more fair marketplace for stakepools, removes the unfair fee burden placed on delegators to small pools and incentivizes a more performant network while maintaining similar payouts to stakepool operators as they currently receive.

## Backward Compatibility

No backwards compatability is needed.

## Test Cases

Any existing test cases that compare real and expected reward amounts would need to be updated.

## Implementations

This would require changes in the way cardano-node calculates pool and delegator rewards.

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode)

