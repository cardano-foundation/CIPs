---
CIP: ?
Title: Tune Parameters minPoolCost and K
Author: Robin of Loxley <adarobinhood@tutanota.com>
Comments-URI:https://forum.cardano.org/t/cip-robinhood-tune-parameters-minpoolcost-and-k/105543/1
Status: Proposed
Type: Standards
Created: 2022-08-01
License: CC-BY-4.0
---

## Summary/Abstract:

The current parameters overvalue the disincentive (minPoolCost), which in turn devalues the incentive (pledge) to the end user. By tuning some parameters we can balance the two so they begin working together.


## Definitions:

**minPoolCost:** The mandatory fixed fee imposed on all delegators currently set at 340 ADA/epoch/pool. It's important to note 'the [minPoolCost] parameter is not part of the original reward sharing scheme' and has not been simulated. The last two years have been the test of its function and effectiveness. By comparing real world stake distribution with the simulated distribution from {ref.2} we can see its effects on the network.

**baseline:** The reward rate of a pool with 0 pledge, 0 margin, and 0 fixed fee. This is the best reward rate a sybille pool can offer without a minPoolCost. This is the reward rate of a private pool with just the owner's stake - ex. BNP & AVENGERS pools. Shown in green {fig.1}.

**tipping_point:** This is the point on the plotted reward function where the slope of the tangent is equal to 2.5x10^-10.  Tipping_point is the amount of stake required to make a pool begin to offer favorable rewards, and also represents the minimum pledge required to balance the incentive of pledge with the disincentive of minPoolCost. With current parameters this is equal to 10M ADA. Shown as the junction of red and black {fig.1}

**danger_zone:** The danger_zone is the part of the plotted reward function who's tangent slope is less than 2.5x10^-10. Danger_zone represents the total pool stake the minPoolCost disincentivizes against by offering relatively low rewards. The danger_zone is shown in red and more favorable rewards are in black {fig.1}.

**real set of pools:** These are pools that actually exist on-chain. The real set of public pledge values are between 0 and 10M with no public pledge between 10M and saturation. Only 3 public pools' pledge exceed the tipping_point.

**sybille attack** - an attacker with low stake tries to gain a majority of stake by creating lots of pools with low cost.


## Motivation:

The minPoolCost apparently provides sybille protection by making a pool with low stake unattractive. A pool operator can make the pool more attractive by adding stake of their own as pledge to exceed the tipping_point; or, instead of pledging, the operator can campaign for stake delegation.

The tipping_point is currently out of reach of 99.9% of all public pools' pledge, making campaigning the basis for stake distribution. This centralizes stake with operators that are effective at campaigning but do not necessarily have any stake in the system of their own. Coincidentally, the parameter meant to increase sybille protection can have the opposite effect if its value is set too high.

With the tipping_point too great, pools with relatively high pledge are left to compete with pledge-less pools to exceed the tipping point. Pledge-less pools that have managed to saturate show historically much higher reward rates than pools with higher pledge who failed to gain popularity.

"Our game theoretic analysis has shown that if stakeholders try to maximize their rewards in a “short-sighted” (myopic) way (pool members joining the pool with the highest rewards at this moment[...]), chaotic behaviour will ensue." {ref.1}

Delegators are more likely to stake with a pledge-less high total stake pool than a high pledged low stake pool despite the latter providing higher non-myopic rewards. This illustrates the imbalance of the incentive (pledge) and the disincentive (minPoolCost).

A sybille attacker should need stake in the system to compete for delegation, not a rigorous marketing campaign.

If few pools are able to buy-in past the tipping_point, it's apparent we have set the tipping_point too high. Lowering the minPoolCost lowers the tipping_point. Reducing the minPoolCost dramatically will point the network toward its desired equilibrium outlined in the original RSS paper {ref.2}.


Pledge benefit incentivizes operators to consolidate their pledge to receive higher reward on their stake and also makes their pool more attractive; pledge benefit incentivizes delegators to lower operator leverage by hunting for the best rewarding pool. Pledge-less pools hit a reward ceiling and are unable to compete with higher pledged pools, making them less attractive.

Presently, pledge has a rather weak reputation, with many people believing that it's not effective or noticeable enough. Currently, only 21 public pools can offset a meager 1% margin with their pledge. There is a large gap between public pledge and saturation, with the majority of pledge benefit noticed within that gap. Only a few private corporations, IOG included, are benefiting from high pledge rewards {fig.2}. We need to bring pledge benefit to within our real set of pools.

Raising a0 will make pledge benefit more noticeable, but this would mostly benefit the small handful of corporations that have pledged to saturation and would only barely effect the majority. It would not change the gap between the founders and everybody else. We need a change that will benefit the most people.

The solutions in this CIP will solve all of the above mentioned problems. It will exponentially benefit more people/entities than in will detriment.


## Solution:

Change the minPoolCost from 340 ADA/epoch to 10 ADA/epoch and raise K from 500 to 2000.


## Specification:

"minPoolCost": 10000000
"stakePoolTargetNum": 2000


## Rationale:

With minPoolCost set at 340 ADA/epoch the tipping point is 10M ADA. By lowering it to 10 ADA/epoch the tipping point drops to 1.75M {fig.4}. Now any pool with ≥ 1.75M pledge will no longer be competing with a sybille attacker for their first delegators. This tipping_point was chosen because it represents an upper-middle level of pledge within the real set of pools. An entrepreneur is far more likely to find 1.75M ADA investor over a 10M ADA investor. 

As previously mentioned, there was no minPoolCost in {ref.2}. We have treated the mainnet like a testnet by deploying an untested, unsimulated, unproven method of sybille protection. 2 years is a generous test period. Time to evaluate the data and tweak these parameters.


Earlier proposed changes of K to 750 or 1000 are far too small. We would still have a tremendous gap between real public pledge and saturation (between the rich founders and everybody else). Raising K by four times its present value will make pledge four times more noticeable and bridge the mentioned gap {fig.3}. Pledge only being somewhat more noticeable won't be enough to change pledge's tarnished reputation. 'Pledge is now 4x more effective' in an article headline and YouTube title will grab the layperson's attention. It will change the narrative from 'pledge has no value' to 'pledge is preferred'. This will all be done while decreasing the rewards paid to saturated pools.

Making pledge more effective could also help solve the problem of exchanges, despite having no stake of their own, making >20% of the blocks. BNP is simply being greedy with their stake. It is more profitable to run their own pledge-less pools than to pay a fee to an SPO. Only a few public pools currently offer greater than baseline rewards, thanks to the imbalance mentioned above. If more pools could offer greater than baseline rewards, exchanges like Binance and Coinbase could choose to make more ADA by delegating to community pools.

At all times we need to incentivize decentralization!


Raising K will force a shakeup of the current stake distribution, which is quite centralized at the moment. Many delegators will be forced to revaluate their pool choice, hopefully for the better.

Scheduling the shakeup in conjunction with pledge becoming more effective opens a great opportunity to reeducate the population of delegators on how the reward function works and what effects parameters have on their reward rates.

This is not so much a change as a tuning of the originally applied incentive/disincentive scheme. The simulations from the original RSS paper show there is no danger of lowering the minPoolCost too low, so long as pledge is 'meaningful' within our real set of pools.


## Effects:

These changes will lower the reward rate of the pledge saturated pools while increasing rewards for all delegators. Pool operators will be able to set their own prices more in line with their actual cost of running the pool. Saturation point will be reduced from ~69M to ~17M. Pledge will become four times more effective at incentivizing decentralized stake delegation.


## Backwards Compatibility:

This proposed change is fully backwards compatible and will not require a hard-fork. Adjusting parameters is 'easy' and will require no code rewrites. This change can be implemented immediately.

## Graphs
All graphs were generated using data through epoch 353.
___
**{fig.1}** Definitions
<img src="{fig.1} Definitions.png">
___
**{fig.2}** Currently unfair pledge gap & poor effectiveness

___
**{fig.3}** Proposed

___
**{fig.4}** Compare Danger Zones


## References:

**{ref.1}** - Design Specification for Delegation and Incentives in Cardano, Philipp Kant, Lars Brünjes, Duncan Coutts, https://hydra.iohk.io/build/3744897/download/1/delegation_design_spec.pdf

**{ref.2}** - Reward Sharing Schemes for Stake Pools, Lars Brünjes, Aggelos Kiayias, Elias Koutsoupias, Aikaterini-Panagiota Stouka, https://arxiv.org/ftp/arxiv/papers/1807/1807.11218.pdf

___
