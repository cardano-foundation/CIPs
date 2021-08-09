---
CIP: ?
Title: Prepay Fixed Fee
Authors: Odin Stark <odinspool@gmail.com>, Shawn McMurdo <shawn_mcmurdo@yahoo.com>
Comments-URI: https://forum.cardano.org/t/prepay-fixed-fee-cip/?????
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

TODO Need to look at specs and see what relevant changes need to be made.

## Rationale

TODO Need to add detailed explanation.
In summary, the proposed parameter changes would create a more fair marketplace for stakepools, provide more fair rewards for delegators to smaller pools and would reduce incentives for centralization providing a more resilient network.

## Backward Compatibility

TODO Need a statement about compatability.

## Test Cases

TODO Need a statement about test cases.

## Implementations

This would require changes in the way cardano-node calculates pool and delegator rewards.

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode)

