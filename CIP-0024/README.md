---
CIP: 24
Title: Non-Centralizing Rankings
Authors:
  - Shawn McMurdo <shawn_mcmurdo@yahoo.com>
Category: Wallets
Status: Proposed
Discussions:
  - https://forum.cardano.org/t/how-to-improve-daedalus-rankings/40478
  - https://github.com/cardano-foundation/CIPs/pull/21
Implementors: []
Created: 2020-09-15
License: CC-BY-4.0
---

## Abstract

Modify the current Daedalus ranking system by removing the centralizing Nash Equilibrium goal of the ranking methodology in order to give more fair rankings and improve the viability of the stake pool operator community and the network overall.  To do this we need to remove the stated goal of having k fully saturated pools and all other pools having no stake other than owner pledge, which goes against the Cardano goal of decentralization.

## Motivation: Why is this CIP necessary?

There are two main reasons for changing the current ranking methodology:

1. Allow for more than k successful stake pools.

2. Provide better decentralization away from a very few stake pool operators creating many pools.

## Specification

This is a modification of the ranking methodology defined in section 5.6 Non-Myopic Utility of “Shelley Ledger: Delegation/Incentives Design Spec. (SL-D1 v.1.20, 2020/07/06)” as follows:

1. Remove the following statement from section 5.6:

"The idea is to first rank all pools by “desirability”, to then assume that the k most desirable
pools will eventually be saturated, whereas all other pools will lose all their members, then to
finally base all reward calculations on these assumptions."

2. Remove the following statement from section 5.6.1:

"We predict that pools with rank ≤ k will eventually be saturated, whereas pools with rank
> k will lose all members and only consist of the owner(s)."

3. Add the following to section 5.6.1:

For all pools with proposed_pool_stake greater than saturation_warning_stake add k to their rank.
Where:
proposed_pool_stake = pool_live_stake + proposed_user_stake
saturation_warning_stake = (total_stake / k) * saturation_warning_level
saturation_warning_level is a real number greater than 0 representing the percent of saturation which is undesirable.  A proposed value for saturation_warning_level is 0.95 meaning 95% saturated.

For example, if a pool has non-myopic desirability rank of 3, pool_live_stake of 207m ADA, proposed_user_stake of 100k ADA with total_stake of 31.7b ADA, k = 150 and saturation_warning_level = 0.95, we would calculate:
207m + 100k > (31.7b / 150) * 0.95
and see that
207.1m > 200.8m
is true so we would change the pool rank to 153 (3 + k) and all pools previously ranked 4 through 153 would move up 1 rank.

4. Remove secion 5.6.2.

5. Remove section 5.6.3.

6. Remove section 5.6.4.

7. Add to secion 5.6.5.

For example, apparent performance, desirability and ranking can be made non-myopic for ranking purposes as follows:

dnm[n] :=
 average(d[1]...d[n],and[n + 1]...and[i])  if n < i
 average(d[1]...d[n])  if n = i
 (dnm[n - 1] * h) + (d[n] * (1 - h))  otherwise.
 
where:
n = epoch number beginning at n = 1 in the first epoch that the pool is eligible for potential rewards.
dnm[n] = the non-myopic desirability of the pool in the nth epoch.
d[n] = the desirability in the nth epoch unaware of historical desirability.
and[n] = the average desirability of the network as a whole in the nth epoch unaware of historical desirability.
h = historical influence factor, which is any real number between 0 and 1 exlusive.
i = integer(1 / h) which is the initial number of epochs during which we use the average desirability

As an example, setting h to 0.1 would mean that the initial number of epochs for using the averaging functions (i) would be 10.  If a pool has been eligible to receive rewards (n) for 3 epochs then we use the average of the pool's desirability for those 3 epochs and the overall network desirability for the prior 7 epochs.  After the 10th epoch we would use 90% of the previous epoch's non-myopic historical desirability and 10% of the current epoch's desirability to arrive at the new non-myopic desirability.

This gives a more reasonable ranking for newer pools that do not have enough historical data to provide fair rankings.

## Rationale: How does this CIP achieve its goals?

Using this non-centralizing ranking methodology gives a more fair ranking of stake pools based on performance, pledge and saturation which will encourage delegators to choose better pools.
It will also bring the rankings more in line with the general Cardano principle of increasing decentralization.

## Path to Active

### Acceptance Criteria

- [ ] One or more wallet software implements this new ranking approach.

### Implementation Plan

- [ ] Author has offered to produce an implementation of this change as a cardano-wallet / Daedalus pull request if shown where the current desirability equation is implemented in the code.

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).

