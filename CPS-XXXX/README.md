---
CPS: ?
Title: Ouroboros not accounting for typical global network delays causes centralisation
Status: Open
Category: ?
Authors: Terminada
Proposed Solutions: []
Discussions: https://github.com/cardano-foundation/CIPs/pull/?
Created: 2024-10-22
License: CC-BY-4.0
---

# CPS-XXXX: Ouroboros not accounting for typical global network delays causes centralisation

## Abstract
An underlying assumption in the design of Cardano's Ouroboros protocol is that the probability of a stake pool being permitted to update the ledger is proportional to the relative stake of that pool.  However, the current implementation does not properly realise this design goal.

Minor network delays endured by some participants cause them to face a greater number of fork battles.  The result is that more geographically decentralised participants do not obtain participation that is proportional to their relative stake.  This is both a fairness and security issue.

## Problem
The [Ouroboros Praos paper](<https://eprint.iacr.org/2017/573.pdf>) states that it is the "*probability of being permitted to issue a block*" that "is proportional to the relative stake a player has in the system".  However, it is clear from the security analysis section that it is the _probability of contributing to the ledger_ that is supposed to be proportional to the relative stake of the participant.  This is an important distinction because it matters little if a player has stake weighted permission to make blocks if the protocol later disproportionately drops that players blocks despite their honest performance.

With the current Ouroboros implementation where slots have 1 second duration, it is not uncommon to have consecutive slot leaders that are only 1 second apart.  Remote participants may be unable to receive the previous block within 1 second and so these block producers will make blocks that result in forks.  Ouroboros settles such forks by preferring the fork whose terminal block has the lowest VRF value.  This seems like a fair method because it is deterministic, neither player can alter the outcome, and each player has an equal chance of winning.  However, the problem is that the more geographically decentralised players will face a disproportionately greater number of "fork battles".  This in turn means that they will get more of their blocks dropped.  The net result is that more geographically decentralised participants do not receive stake weighted _probability of contributing to the ledger_.  This is not only unfair, but also represents a deviation from the Ouroboros security analysis assumptions.

This might seem like a minor problem, but the effect is significant.  If the majority of the network reside in USA - Europe with close connectivity and less than 1 second propagation delays, then those participant pools will see 5% of their blocks suffering "fork battles" which will only occur when another pool is awarded the exact same slot (ie: a "slot battle").  They will lose half of these battles on average causing 2.5% of their blocks to get dropped, or "orphaned".

However, for a pool that happens to reside on the other side of the world where network delays might be just over 1 second, this pool will suffer "fork battles" not only with pools awarded the same slot, but also the slot before, and the slot after.  In other words, this geographically decentralised pool will suffer 3 times the number of slot battles, amounting to 15% of its blocks, and resulting in 7.5% of its blocks getting dropped.  The numbers are even worse for a pool suffering 2 second network delays because it will suffer 5 times the number of "fork battles" and see 12.5% of its blocks "orphaned".  This not only results in an unfair reduction in rewards, but also the same magnitude reduction in contribution to the ledger.

Even the high quality infrastructure of a first world country like Australia is not enough to reliably overcome this problem due to its geographical location.  But is it reasonable to expect all block producers across the world to receive blocks in under one second whenever the internet becomes congested, or if block size is increased following parameter changes?  Unfortunately, the penalty for a block producer that cannot sustain this remarkable feat of less than 1 second block receipt and propagation, is 3 times as many "fork battles" resulting in 7.5% "orphaned" blocks rather than 2.5%.

Considering that most stake pools are competing over 1% or less in fees, these are big numbers.  The obvious solution for the remote pool is to move its block producer to a server housed in USA or Europe.  This illustrates not only the centralisation problem created, but also the reduction in security that flows from running a block producer on someone elses computing hardware.

## Goals
Cardano should live up to its [11 blockchain tenets](<https://iohk.io/en/blog/posts/2024/10/11/the-11-blockchain-tenets-towards-a-blockchain-bill-of-rights/>) proposed by Prof Aggelos Kiayias, in particular T8 and T11 which speak to treating participants fairly without asymmetries.

## Possible Solutions
1. Modify how stake pools calculate their slot leadership by including ```mod 2``` or ```mod 3``` in the formula so that only every second or third slot is a possible leader slot.  Then adjust other parameters so that the Cardano network still produces a block every 20 seconds on average.

    A consequence of this change would be an increased number of true "slot battles", where two pools are awarded the exact same slot.  However such battles are fairly settled by preferring the lowest block VRF and cannot be gamed by a malicious actor.

2. Increase the slot duration to 2 or 3 seconds.  However this could have consequences for dapps that have assumed a slot will always be 1 second.

## Considerations
1. What is a reasonable expectation for block producers housed across the world to achieve in terms of network delays?  Is 2 seconds of network delay enough time before block producers get penalised, or would 3 seconds be more appropriate?

2. What internet infrastructure and geographical location does Cardano consider as a minimum requirement in order to fairly contribute to its ledger?

3. It would seem to be an advantage to encourage fair participation from people residing in countries on the other side of the globe because this might provide resilience against political or other attacks localised to Europe or USA.

4. Would there be any impact on the Ouroboros 5 second delta parameter?

5. Would it be appropriate to make the window in which the block VRF tie breaker rule is applied also the same 2 or 3 seconds so that only blocks with the exact same slot number are deterministicly settled using the block VRF, otherwise the node would prefer its current block?  Such a change would remove the ability of malicious actors to deliberately cause a fork with the previous block when they know their block VRF is lower.

6. What effect could any change have on the solution to [issue #2913: Consensus should favor expected slot height to ward off delay attack](<https://github.com/IntersectMBO/ouroboros-network/issues/2913>)?

## Arguments against correcting this unfairness
1. It doesn't matter where the block producer is warehoused because block production is like a virtual service that can be run from anywhere.  What really matters is ownership of the pledge and stake, not ownership of the computing hardware.  If you live on the other side of the world, just rent a virtual server in Frankfurt or Los Angeles for your block producer.

- Centralising Cardano infrastructure to data centres potentially hands control over the software, as well as selective control over block propagation between nodes, to BigTech data centre owners.

2. The internet infrastructure is centred in USA and USA is more politically stable and less likely to have its internet infrastructure compromised through acts of war.  If conflict between USA, China, and Russia ensues then the undersea cables to Japan, Australia and New Zealand could get damaged.  Therefore it makes sense that Cardano block production should be slightly advantaged in USA and slightly disadvantaged in Japan, Australia and New Zealand.

- Japan, Australia and New Zealand are very politically stable and it might actually be a good idea to _fairly_ incentivise participation from people living in those areas.  If internet connectivity was to be affected by cyber warfare, the targets of such attacks may not be predictable today.

- The bottom line is that if I have 0.001% of stake in the system then I should get 0.001% of access to the system.  Likewise with scaling that up, if good actors possess 51% of the stake then they should have 51% of the control, as this is a fundamental assumption protecting Cardano.  I hope that the Cardano community won't step away from this fundamental mathematics based approach in favour of some sort of subjective human inference about where they think block producers should be warehoused for political or other reasons.

3. Internet transmission is improving so in the future 1 second might be sufficient for block propagation across the entire globe.

- This unfairness problem doesn't seem hard to fix.  If / when internet speeds improve then it should be straightforward to recalibrate the software again.

4. Won't halving or one-third'ing the number of potential leader slots reduce the number of blocks and therefore reduce the throughput?

- Possible solution 1 also involves adjusting other parameters so that the target rate of block production remains unchanged.  Actually, it seems likely that the realised throughput would slightly increase.  The reason for this is that [possible solution 1](#Possible-Solutions) would eliminate forks caused by 1 second propagation delays which currently are wasted throughput.

5. If my pool is located close to the majority then I am benefitting from this unfairness so why should I vote for this to be fixed?

- See section: [Goals](#Goals).  Hopefully most people in Cardano want to build a fair system for everyone no matter where they live.

## Copyright
This CIP is licensed under [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/legalcode).

****
