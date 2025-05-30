---
CPS: ?
Title: Sticky Delegation
Status: Open
Category: Ledger
Authors:
  - "Cerkoryn <ByteBanditLLC@proton.me>"
Proposed Solutions:
  - CIP-Sticky Delegation
Discussions:
  - https://github.com/Cerkoryn/CIPs/discussions
  - https://matrix.to/#/#cardano-space:matrix.org
  - https://forum.cardano.org/t/pcp-k-parameter-earncoinpool/122701
Created: 2024-01-15

---
> [!IMPORTANT]  
> TODO: This draft is still very much a work-in-progress.  Feel free to contribute via discussions or by submitting a PR.

## **Abstract**

Cardano's blockchain is renowned for its advanced, non-custodial, liquid staking mechanism, built on the innovative Ouroboros architecture. It also pioneers in blockchain governance with its cutting-edge liquid democracy system, where decentralized representatives (dReps) garner voter delegation, propose, and make governance decisions based on the collective voting power. Despite these advancements, Cardano's implementation of Ouroboros encounters significant game-theoretic challenges in its Reward Sharing Scheme (RSS). These challenges are expected to intensify with the introduction of dRep delegation alongside existing stake pool options. This Cardano Problem Statement (CPS) is dedicated to outlining and examining one specific issue of "sticky delegation" thoroughly, with the goal of igniting the creation of Cardano Improvement Proposals (CIPs) or Parameter Change Proposals (PCPs) that can address them in a targeted and comprehensive manner.

## **Problem**

TLDR: Delegator stake should move more often than it does.  There are some cases where it seems to get "stuck" which will inevititably grow into a bigger problem the longer we wait to address it. The same thing will likely happen with dRep delegation too.

To define the problem we will break down "delegation" into five different types and two different modes.

### Delegation Types
- Active delegation
- Lazy delegation
- Dead delegation
- Retired delegation
- Undelegated ADA

**Active delegation:** Delegation that is engaged with the system.  These delegators pay attention to the actions of their stake pool operator (SPO) or dRep and will move their delegation in a timely manner if either of them act agaist the interests of the delegator or of the network as a whole. This delegation produces blocks, earns rewards, and provides voting power.
 
**Lazy delegation:** Delegation that is disengaged from the system.  This delegation is still capable of moving, but for some reason the delegators do not move their stake/voting power even when it is in their best interests to do so. This delegation produces blocks, earns rewards, and provides voting power.

**Dead delegation:** This delegation is completely incapable of moving no matter what.  This is the case when a delegator has lost the keys to their wallet or passed away after having delegated to an SPO or dRep. Under current ledger rules, this delegation will remain delegated forever and will continue to produce blocks, earn rewards, and have voting power.

**Retired delegation:** Delegation that is disengaged (either lazy or dead) but is also delegated to a retired stake pool or inactive dRep. Unlike lazy or dead delegation however, this ADA does not produce blocks*, earn rewards, or provide voting power.

**Undelegated ADA** This category is simply for ADA that is unstaked and/or undelegated to a dRep. It also does not produce blocks, earn rewards, or have voting power.

###### *Retired delegation can theoretically be selected to produce a block and could even do so provided that the pool is still running and up-to-date.  However, no rewards will be earned.

### Delegation Modes
- Delegating ADA as stake to a stake pool operator.
- Delegating ADA as voting power to a dRep.

To most readers these two delegation modes should be fairly self-explanatory.  However it is important to note that the current implementation of CIP-1694 includes a parameter called `drep_activity` measured in epochs.  If a dRep hasn't voted on a proposal in that amount of time, the collective voting power of all of their delegation will be removed from quorum and automatically counted as abstaining.  For the purposes of this CPS, this delegation is categorized similiarly to stake in retired stake pools as "retired delegation."


Fixing this could create a ripple effect that increases the significance of pledge (a0), encourages multi-pool operators to merge, helps us reach the ideal number of pools (k), and improves the staking reward for active delegators and SPOs.

> [!NOTE]
> According to [Reward Sharing Schemes for Stake Pools(2020)](https://arxiv.org/ftp/arxiv/papers/1807/1807.11218.pdf) p.23:
> 
> "Players who play myopically and Rational Ignorance. Myopic play is not in line with the way we
> model rational behavior in our analysis. We explain here how it is possible to force rational parties to
> play non-myopically. With respect to pool leaders we already mentioned in Section 2.3 that rational
> play cannot be myopic since the latter leads to unstable configurations with unrealistically high
> margins that are not competitive. Next we argue that it is also possible to force poolmembers to play
> non-myopically. The key idea is that the effect of delegation transactions should be considered only in
> regular intervals (as opposed to be effective immediately) and in a certain restricted fashion. This can
> be achieved by e.g., restricting delegation instructions to a specific subset of stakeholders at any given
> time in the ledger operation and making them effective at some designated future time of the ledger’s
> operation. Due to these restrictions, players will be forced to think ahead about the play of the other
> players, i.e., stakeholders will have to play based on their understanding of how other stakeholders
> will as well as the eventual size of the pools that are declared... 

Myopic play (i.e. delegators acting ignorantly) is assumed not to be rational because delegators need to be on their toes about where to switch their delegation to maximize their returns. In practice however, many delegators appear to be uninterested in moving their stake around.  I hypothesize that this is for two reasons:

- Most pools provide extremely similiar returns and so delegators are not interested in moving their stake around as they should.
- Staking rewards are very mediocre which causes delegators to lose interest in maximizing their yields.

> [!IMPORTANT]  
> TODO: Arguments for ISPOs/Charity pools, etc. contributing to game theory discrepencies?
> Predictions for dRep game theory?

Additionally, in some sense it is expected that inactive delegators should have their rewards lowered via parameter change:
> [!NOTE]
> ...A related problem is that of rational ignorance, where there is some significant inertia in terms of 
> stakeholders engaging with the system resulting to a large amount of stake remaining undelegated. 
> This can be handled by calibrating the total rewards R to lessen according to the total active stake delegated, 
> in this way incentivising parties to engage with the system."

> [!IMPORTANT]  
> TODO: Need data showing stake that hasn't moved.  Perhaps a chart with epoch on the x-axis and the amount of ADA in delegation Txs from just that epoch.  I imagine that would show a downward trend due to stake that was delegated during Shelley Era and then left untouched. Maybe some other charts focusing on pools instead?  Pools who have raised fees or lowered pledge on their delegates?  ADA delegate to retired pools?  Other charts or data?

![Old Josephine Info](https://pbs.twimg.com/media/Fi6tzIqXgAozFWt?format=jpg&name=large)
![Homer Script Info](https://matrix-client.matrix.org/_matrix/media/v3/download/matrix.org/MXwdYMpyqBZKQbSKcWyAjpHt)

> [!IMPORTANT]  
> TODO: Estimate dead stake in active pools by counting how much dead stake is left in pools after they retire.

## **Goals**

> [!IMPORTANT]  
> TODO: Finish this part

## **References**

[Reward Sharing Schemes for Stake Pools(2020)](https://arxiv.org/ftp/arxiv/papers/1807/1807.11218.pdf)

###### *The below references still need to be independently verified and/or updated to be more current.*

[Homer Script Info](https://matrix-client.matrix.org/_matrix/media/v3/download/matrix.org/MXwdYMpyqBZKQbSKcWyAjpHt)

[Old Josephine Info](https://pbs.twimg.com/media/Fi6tzIqXgAozFWt?format=jpg&name=large)


