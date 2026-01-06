---
CIP: 7
Title: Curve Pledge Benefit
Authors:
  - Shawn McMurdo <shawn_mcmurdo@yahoo.com>
Category: Ledger
Status: Proposed
Created: 2020-08-11
Discussions:
  - https://github.com/cardano-foundation/CIPs/pull/12
  - https://forum.cardano.org/t/protocol-parameters-pledge-and-sybil-resistance/35100
  - https://github.com/input-output-hk/cardano-node/issues/1518
Implementors: []
License: Apache 2.0
---

## Abstract

Modifying the current rewards calculation equation by substituting a n-root curved relationship between pledge and pledge benefit rewards for the current linear relationship will better achieve the original design goal of incentivizing pledge to help prevent Sybil attacks.
This also reduces the unfortunate side effect in the current equation that over rewards private pools which provide no additional security benefit.

## Motivation: Why is this CIP necessary?

There are two main reasons for changing the current linear a0 pledge benefit factor in the rewards equation.

1. Pools pledging less than 1 million ADA see very little reward benefit.  This is not a strong incentive for pool operators as at current prices that is approximately $150,000 USD.

2. Private pools get massive reward benefit without providing any additional protection against Sybil attacks. Why should a private pool make 29% more rewards than a pool with 5m ADA pledge while doing the same work?

## Specification

This is a modification of the maxPool function defined in section 11.8 Rewards Distribution Calculation of “A Formal Specification of the Cardano Ledger”.

maxPool = (R / (1 + a0)) * (o + (s * a0 * ((o - (s * ((z0 - o) / z0))) / z0)))

where:
R = ((reserve * rho) + fees) * (1 - tau)
o = min(pool_stake / total_stake, z0) = z0 for fully saturated pool
s = pledge / total_stake
z0 = 1 / k
and the following are current protocol parameters:
k = 150
rho = 0.0022
a0 = 0.3
tau = .05

The idea is to replace s in the above equation with an n-root curve expression of pledge rather than the linear pledge value.

We use an expression called crossover to represent the point where the curve crosses the line and the benefit in the new and original equations is identical.
Because the a0 pledge benefit is spread over the pledge range from 0 to saturation there is a dependence on k and total_stake.
Since k and total_stake will likely change over time it is best to express crossover in terms of k and total_stake as follows:

crossover = total_stake / (k * crossover_factor)

where crossover_factor is any real number greater than or equal to 1.
So crossover_factor is essentially a divisor of the pool saturation amount.
For example, setting crossover_factor to 20 with k = 150 and total_stake = 31 billion gives a crossover of approximately 10.3 million.

Also, we can parameterize the n-root curve exponent.
This gives us:

s = pow(pledge, (1 / curve_root)) * pow(crossover, ((curve_root - 1) / curve_root)) / total_stake

The curve_root could be set to any integer greater than 0 and when set to 1 produces the current rewards equation.
The curve_root is n in n-root. For example, 1 = linear, 2 = square root, 3 = cube root, 4 = fourth root, etc.

By making this modification to the rewards equation we introduce two new protocol parameters, crossover_factor and curve_root, that need to be set thoughtfully.

### Test Cases

See rewards.php for some simple PHP code that allows you to try different values for crossover_factor and curve_root and compare the resulting rewards to the current equation.
For usage, run "php -f rewards.php help".

An interesting set of parameters as an example is:

curve_root = 3
crossover_factor = 8

Running "php -f rewards.php 3 8" produces:

Assumptions
Reserve: 14b
Total stake: 31.7b
Tx fees: 0
Fully Saturated Pool
Rewards available in epoch: 29.3m
Pool saturation: 211.3m

Curve root: 3
Crossover factor: 8
Crossover: 26.4m

Pledge	Rewards	Benefit	Alt Rwd	Alt Bnft
0k	150051	0%	150051	0%
10k	150053	0%	150458	0.27%
50k	150062	0.01%	150747	0.46%
100k	150073	0.01%	150928	0.58%
200k	150094	0.03%	151156	0.74%
500k	150158	0.07%	151551	1%
1m	150264	0.14%	151941	1.26%
2m	150477	0.28%	152432	1.59%
5m	151116	0.71%	153282	2.15%
10m	152181	1.42%	154122	2.71%
20m	154311	2.84%	155180	3.42%
50m	160702	7.1%	157012	4.64%
100m	171352	14.2%	158821	5.84%
211.3m	195067	30%	161305	7.5%

As you can see this gives meaningful pledge benefit rewards to pools pledging less than 1m ADA.

## Rationale: How does this CIP achieve its goals?

Using the n-root curve pledge benefit shows a much more reasonable distribution of pledge related rewards which will encourage meaningful pledges from more pool operators thus making the network more secure against Sybil attacks.
It also provides higher rewards for higher pledge without disproportionately rewarding a very few private pool operators who provide no additional security value to the network.
This modification maintains the general principles of the current rewards equation and does not introduce any hard limits.
It improves the incentives that were originally designed to make them more meaningful for the majority of pool operators.

### Backward Compatibility

This proposal is backwards compatible with the current reward function by setting the curve_root parameter to 1.

## Path to Active

### Acceptance Criteria

- [ ] The new equation is implemented in the ledger and enacted through a hard-fork.

### Implementation Plan

- [ ] Agreement by the Ledger team as defined in [CIP-0084](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0084) under _Expectations for ledger CIPs_ including "expert opinion" on changes to rewards & incentives.

- [ ] Author has offered to produce an implementation of this change as a pull request if shown where the current maxPool reward equation is implemented in the code.

## Copyright

2020 Shawn McMurdo. This CIP is licensed under [Apache-2.0](https://www.apache.org/licenses/LICENSE-2.0).

