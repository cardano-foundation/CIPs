---
CIP: ?
Title: Stake Aware Rankings
Author: Shawn McMurdo <shawn_mcmurdo@yahoo.com>
Discussions-To: 
Comments-Summary: 
Comments-URI: 
Status: Draft
Type: Standards
Created: 2020-09-15
License: Apache 2.0
Post-History: https://forum.cardano.org/t/how-to-improve-daedalus-rankings/40478
---

## Summary

Make Daedalus rankings less weighted by stake and thus more fair.

## Abstract

Modify the current ranking equation by decreasing the influence of stake in the rankings in order to give more fair rankings and improve the viability of the stake pool operator community and the network overall.  To do this we need to remove the stated goal of having k fully saturated pools and all other pools having no stake other than owner pledge, which goes against the Cardano goal of decentralization.

## Motivation

There are two main reasons for changing the current ranking equation.

1. Allow for more than k successful stakepools.

2. Provide better decentralization away from a very few stakepool operators creating many pools.

## Specification

This is a modification of the desirability function defined in section 5.6.1 Pool Desirability and Ranking of “Shelley Ledger: Delegation/Incentives Design Spec. (SL-D1 v.1.20, 2020/07/06)” as follows:

d(c, m, s, p) :=
 0  if f(s, p) <= c,
 (f(s, p) − c) * (1 − m)  otherwise.

where:
c = fixed cost
m = variable margin
s = pledge
p = apparent performance
f(s, p) = pool rewards
o = pool stake

The idea is to divide the desirability by o in the above equation to give a better indication of the value to the delegator.
This gives:

d(c, m, s, p, o) :=
 0  if f(s, p) <= c,
 ((f(s, p) − c) * (1 − m)) / o  otherwise.

In order to easily accomodate backwards compatability and provide a range of effect for stake, we can introduce a new parameter called stake_decentralization notated as sd.

d(c, m, s, p, o, sd) :=
 0  if f(s, p) <= c,
 ((f(s, p) − c) * (1 − m)) / (1 + (o * sd))  otherwise.

where stake_decentralization, sd, is any real number between 0 and 1 inclusive.

Setting sd to 0 restores the original desirability function.
Setting sd to 1 provides the most fair rankings of all pools.

This desirability result can then be made non-myopic for ranking purposes as follows:

dnm[n] :=
 average(d[1]...d[n])  if n <= (1 / h)
 (dnm[n - 1] * h) + (d[n] * (1 - h))  otherwise.
 
where:
n = epoch number beginning at n = 1 in the first epoch that the pool is eligible for potential rewards.
dnm[n] = the non-myopic desirability of the pool in the nth epoch.
h = historical influence factor, which is any real number between 0 and 1 exlusive.

As an example, setting h to 0.1 would mean that you would use the average of all epochs for the first 10 epochs and after that you would use 90% of the previous epoch's non-myopic historical desirability and 10% of the current epoch's desirability to arrive at the new non-myopic desirability.

## Rationale

Using this stake aware desirability equation gives a much more fair ranking of stakepools based on performance and pledge which will encourage delegators to choose better pools.
It will also bring the rankings more in line with the general Cardano principle of increasing decentralization.

## Backward Compatibility

This proposal is backwards compatible with the current desirability equation by setting the stake_decentralization, sd, to 0.

## Implementations

If someone will show me where the current desirability equation is implemented in the code, I could produce an implementation of this change as a pull request.

## Copyright

Copyright 2020 Shawn McMurdo

This CIP is licensed under the Apache-2.0 license.

