---
CIP: 37 
Title: Dynamic Saturation Based on Pledge
Status: Proposed
Category: Ledger
Authors:
  - Casey Gibson <caseygibson@protonmail.ch>
Implementors: []
Discussions:
  - https://github.com/cardano-foundation/CIPs/pull/163
Created: 2021-12-03
License: CC-BY-4.0  
---

## Abstract

The pledge should be used to calculate the saturation point of a pool: setting a maximum delegation proportional to pledge.

## Motivation: Why is this CIP necessary?

Currently Cardano has been plagued with an ever increasing amount of single entity Stake Pool Operators (SPO) creating multiple pools. The pools that are known to be operated by single entity SPOs account for just 18.72% of the total stake and 50% of the total stake can be attributed to at least 23 single entities (as of 3rd Dec 2021).

The vision of Cardano is that it everyone should be able to have the opportunity to be able to run a stake pool regardless of their financial capabilities and this is even more important for developing countries.

The issue we're currently facing is that many SPOs have been able to exploit a loophole that has allowed them to use their influence to create many sub-pools without any restrictions. As the size of their pools grow, instead of honouring the saturation limits already in place, they are bypassing them by creating more sub-pools. From a technical point, it is theoretically possible for a single entity to run enough stake pools to control more then 50% of the total stake. 

While unlikely, the system does not take into account external influences (eg. political) that could harm the system. Shelly has been active for less then 2 years and we are already seeing the risks on a small scale. As real world adoption continues, there could be situations in the next decade that could jeopardise the decentralisation of Cardano. One example could be that a political party could run a ISPO (Initial Stake Pool Offering) on a mass scale. Seeing as Cardano has the potential to be used for voting (even at a political level), the integrity of Cardano could be questioned if political parties controlled stake pools with large shares of total stake. 

The pledge used in a pool was meant to show how serious a SPO is and how much "skin in the game" they had. The idea was that if they have more pledge, they have more to lose if something goes wrong. This seems to have lost it's meaning as SPOs that already have a dominating position have created many sub-pools. Some have split up their pledge evenly, some have next to no pledge and have gained high amounts of stake through influential means. This has not only reduced the security of Cardano, but has also lost the meaning of having pledge in the pool. 

For example, a SPO might have a pledge of 30,000 ADA across 10 pools, while another SPO might have 1,000,000 pledge but only has 1 pool with a small amount of active stake. Seeing as the SPO with 1M pledge has more overall, they have more to lose and should be trusted more. Since there is no technical advantage to having a high pledge, the meaning and purpose of a pledge is redundant.

To make the pledge a meaningful metric that is fair to all SPOs and aligns with the core values of Cardano, the pledge should be used to calculate the saturation point of a pool. This will mean that SPOs, no matter how many pools they operate, will have a maximum saturation based on their total pledge. For example, if a pool operates a single pool and wanted to open up another pool with the same amount of stake, they will have to assign the equal amount of pledge against that new pool. If a pool wishes to up their saturation point, they will need to assign a higher amount of pledge.

This proposal has had active discussions for over 6 months and is now waiting for a review from IOG to provide feedback on the feasibility and soundness of the approach.

1. This CIP should be considered a medium priority as it directly impacts the health and growth of the Cardano ecosystem. Large Cardano pools have had several years to take advantage of the lack of oversight and have control of a large portion of mining operations. This continued lack of restrictions will further damage the trust and reliability of the framework.

2. Timelines around the implementation of the CIP will depend on urgency, however its implementation should be trivial as there are no new parameters required or risks involved. Further this CIP from a high-level aspect only requires an update to the existing algorithm. From an external context, the CIP will require trivial updates as it should be self-contained in cardano-node.

## Specification

For this to be able to work, there firstly needs to be an upper limit and a lower limit. The K parameter can still be used as the upper saturation limit of a single pool. As in, if a SPO has enough pledge assigned to a single pool, that pool will be able to run at the maximum saturation point of K. The lower limit is in place to safe guard small SPOs and allow them to grow.

An example of how Dynamic Saturation would be calculated:

500,000 ADA Pledged = Saturation point at 100% of K

250,000 ADA Pledged = Saturation point at 50% of K

125,000 ADA Pledged = Saturation point at 25% of K

62,500 ADA Pledged = Saturation point at 12.5% of K

To not penalise small pools, there should be a lower limit saturation point, such as 10% of K. Based on this, a pool with a pledge of 50,000 has the same saturation point as a pool with 25,000 pledge, both being 10% of K. This will allow smaller pools to still have some growth potential.

The only way a pool can receive more stake across all their pools without impacting their rewards is to increase their total pledge.

Example with SPO of 1,000,000 Pledge with current k implementation:

| Pools | Pledge    | Saturation Per Pool | Total Stake | Fees                 |
|-------|-----------|---------------------|-------------|----------------------|
| 1     | 1,000,000 | 100% of K           | ~65M        | 340 fee + margin     |
| 2     | 500,000   | 100% of K           | ~130M       | 340 fee + margin x2  |
| 4     | 250,000   | 100% of K           | ~260M       | 340 fee + margin x4  |
| 8     | 125,000   | 100% of K           | ~520M       | 340 fee + margin x8  |
| 16    | 62,500    | 100% of K           | ~1040M      | 340 fee + margin x16 |

Example with SPO of 1,000,000 Pledge with Dynamic Saturation:

| Pools | Pledge    | Saturation Per Pool | Total Stake | Fees                 |
|-------|-----------|---------------------|-------------|----------------------|
| 1     | 1,000,000 | 100% of K           | ~65M        | 340 fee + margin     |
| 2     | 500,000   | 100% of K           | ~130M       | 340 fee + margin x2  |
| 4     | 250,000   | 50% of K            | ~130M       | 340 fee + margin x4  |
| 8     | 125,000   | 25% of K            | ~130M       | 340 fee + margin x8  |
| 16    | 62,500    | 12.5% of K          | ~130M       | 340 fee + margin x16 |

As we can see above with the **current** implementation of K, a pool owner can split the pool and double their delegators active stake (or however many times they split).

The Dynamic Saturation method caps the pools so that the amount of total stake across all pools is the same no matter how much they split up their pledge and the only benefit will be the extra fee collected (340 ADA) per pool.

This will mean that the saturation metric will have a direct corelation to an SPOs total pledge.

### Proposals Based On Feedback

After some discussions among the community and some help from https://github.com/cffls, the below code example has been proposed for how the dynamic saturation could work.

```
let lovelace = 1000000;

function calc_sat(pledge){
    k = 500;
    e = 0.2;
    l = 125;
    total_supply = 33719282563 * lovelace;
    orig_sat = total_supply / k;
    new_sat = orig_sat * Math.max(e, min(1 / k, pledge / orig_sat * l));
    final_sat = max(new_sat, orig_sat);
    console.log(`pledge: ${pledge / lovelace}, sat: ${final_sat / lovelace}`);
}

function max(val1, val2){
    if(val1 < val2){
        return val1;
    }
    return val2;
}

function min(val1, val2){
    if(val1 > val2){
        return val1;
    }
    return val2;
}

calc_sat(50000 * lovelace);
calc_sat(100000 * lovelace);
calc_sat(150000 * lovelace);
calc_sat(250000 * lovelace);
calc_sat(500000 * lovelace);
calc_sat(750000 * lovelace);
calc_sat(1000000 * lovelace);
calc_sat(2000000 * lovelace);
```

Results:

```
[Log] pledge: 50000, sat: 13487713.0252
[Log] pledge: 100000, sat: 13487713.0252
[Log] pledge: 150000, sat: 18750000
[Log] pledge: 250000, sat: 31250000
[Log] pledge: 500000, sat: 62500000
[Log] pledge: 750000, sat: 67438565.126
[Log] pledge: 1000000, sat: 67438565.126
[Log] pledge: 2000000, sat: 67438565.126
```

## Rationale: How does this CIP achieve its goals?

Since a single entity SPO only has a certain amount of ADA they can pledge, they will eventually hit their saturation point no matter how many pools they create. The only way they can add more delegators is to increase their pledge. Once they run out of pledge and reach their saturation point, the delegators will have no choice but to move to another SPO and increase decentralisation.

In the above example, the base pledge of 500,000 ADA should be set as a parameter that can be adjusted in the future. E.g, if it is found that it is too low or too high to gain 100% saturation, it can be adjusted in the same way k can be adjusted.

One of the questions raised by the community was, will the lower limit stop the growth of small pools if it is set at a level where they can't reach the expected annual 5% return on ADA. This case could be handled a few ways, but the main aim would be to keep it at a sustainable amount for small pools.

1. The value is a percentage of k, such as 10%. This percentage could increase as needed, such as to 15% of k.
2. The value could be calculated based on the average of active stake compared to active pools. E.g, active stake = 23837 M / 3000 = saturation point of 7.94 M ADA

## Path to Active

### Acceptance Criteria

- [ ] The new relationship between pledge and saturation defined here is implemented in the Ledger and enacted through a hard-fork.

### Implementation Plan

- [ ] Agreement by the Ledger team as defined in [CIP-0084](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0084) under _Expectations for ledger CIPs_ including "expert opinion" on changes to rewards & incentives.

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode)
