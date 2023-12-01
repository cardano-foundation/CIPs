---
CPS: ?
Title: ADA token supply exhaustion
Status: Open
Category: Token
Authors:
  - xezon
Proposed Solutions:
Discussions:
Created: 2023-11-30
---

## Abstract

The native Cardano ADA Token has a fixed maximum supply and a fixed smallest unit size, which means the ADA token has a finite life time until it is exhausted for the smallest possible unit division. Once it is exhausted, it becomes impossible to meet smaller transaction requirements with the native ADA token.

## Problem

The ADA token has a maximum supply of 45,000,000,000 and is divisible by 1,000,000 units. On first sight this looks like a lot, but it is not over a long time horizon with a large number of participants.

Based on the projected age distribution in the upcoming decades, we can take a look at some sample figures.

People within and above the working age are expected to participate in economic activity. The working age population is assumed within ages 15 to 64.

By year 2050 we estimate a population of

- 2.01 Billion of 14 and younger
- 7.00 Billion of 15 and older

Source: https://ourworldindata.org/age-structure

In the worst case (or best case) scenario, the ADA token could be used by around 7 Billion people at this time.

Assuming a fully diluted supply of ADA tokens, there would be

45,000,000,000 ADA / 7,000,000,000 = 6.43 ADA = 6,430,000 Lovelace on average for each person.

This still looks like a lot, but let us say we want Lovelace to be as divisible as USD Cent or EUR Cent: 0.01

Then 6,430,000 Lovelaces could be used as a familiar value equivalent of 64,300.00 USD - just to put it into perspective.

64,300.00 USD has some value, but is it enough?

### Why is this a problem?

ADA is meant to be the main reserve currency of the Cardano network. If we expect the network to serve a lot of people and communities for a very long time, then the ADA token needs to be usable for any kind of transactions - to flow to and from other projects within - no matter how small or big. A fixed token unit division combined with the fixed token supply means the token does not scale and it cannot be used for transactions over an infinite amount of time with an ever increasing population of network users.

### A compounding problem

Given the current deflationary design of the ADA token, this is a compounding problem. Naturally ADA tokens will be lost over time, because ADA holders can lose access to ADA tokens by mistake, accident or negligence.

We can calculate a fixed deflation with formula

```
A = P(1 + r/n)^nt

P is the principal
A is P + interest
r is the inflation rate
n is the compound count per year
t is the time in years
```

Assuming 1% of ADA tokens are lost every year over 100 years, then the maximum supply of 45,000,000,000 ADA would be reduced by 63.40% to 16,471,455,357 ADA.

```
45000000000 * ( ( 1 + ( -0.01 / 1 ) ) ^ (1 * 100) ) = 16471455357
```

Maximum supply after 100 years and 1% deflation: 16,471,455,357 ADA
Maximum supply after 200 years and 1% deflation: 6,029,085,368 ADA
Maximum supply after 300 years and 1% deflation: 2,206,840,233 ADA
Maximum supply after 400 years and 1% deflation: 807,774,897 ADA
Maximum supply after 500 years and 1% deflation: 295,671,736 ADA

Maximum supply after 100 years and 2% deflation: 5,967,880,015 ADA
Maximum supply after 200 years and 2% deflation: 791,457,597 ADA
Maximum supply after 300 years and 2% deflation: 104,962,755 ADA
Maximum supply after 400 years and 2% deflation: 13,920,113 ADA
Maximum supply after 500 years and 2% deflation: 1,846,079 ADA

It is just a matter of time until the ADA token can no longer be divided for an ever growing number of participants and requirements. It may take many decades or centuries to unfold, but it is inevitable. This ultimately also means there is a cap on the absolute adoption that the Cardano network can ever achieve through the native ADA token. Once the ADA supply exhaustion point is hit, small transactions can no longer be made with the ADA token and network users need to look for workarounds or alternatives.

### A distribution problem

The deflation problem is exacerbated by distribution inequalities. Naturally earlier ADA owners will hold larger portions of the total ADA supply and an ever larger number of newer network participants will deal with an ever decreasing portion of ADA tokens.

In 2023-11-30,
the 10 largest ADA addresses owned 8.63% of the total ADA supply.
the 20 largest ADA addresses owned 10.32% of the total ADA supply.
the 50 largest ADA addresses owned 15.04% of the total ADA supply.
the 100 largest ADA addresses owned 20.71% of the total ADA supply.

Source: https://www.coincarp.com/currencies/cardano/richlist/

Eventually the larger ADA holdings will trickle down to smaller ADA holders, but this imbalance of distribution likely will be present over the entire life time of the Cardano network.

Likely, because in the overall world market we do see the same inequalities, where a minority of people owns the majority of things.

> A study by the World Institute for Development Economics Research at United Nations University reports that the richest 1% of adults alone owned 40% of global assets in the year 2000, and that the richest 10% of adults accounted for 85% of the world total. The bottom half of the world adult population owned 1% of global wealth.

Source: https://en.wikipedia.org/wiki/Distribution_of_wealth

Therefore we can expect that the vast majority of ADA holders will deal with ADA values well below the fair distributed average (Total supply divided by number of users).

## Goals

Cardano's ADA needs strategies or properties that makes it immune from ever becoming exhausted by its smallest numerical unit.

A potential solution for the ADA token is to be divisible into a practically unlimited unit size.
