---
CIP: 135
Title: Disaster Recovery Plan for Cardano networks
Category: Tools
Status: Active
Authors:
    - Kevin Hammond <kevin.hammond@iohk.io>
    - Sam Leathers <samuel.leathers@iohk.io>
    - Alex Moser <alex.moser@cardanofoundation.org>
    - Steve Wagendorp <steve.wagendorp@cardanofoundation.org>
    - Andrew Westberg <andrewwestberg@gmail.com>
    - Nicholas Clarke <nicholas.clarke@tweag.io>
Implementors: N/A
Discussions:
    - https://github.com/cardano-foundation/CIPs/pull/893
Created: 2024-06-17
License: CC-BY-4.0
---

## Abstract

While the Cardano mainnet and other networks have proven to be highly resilient, it is necessary to proactively 
consider the possible recovery mechanisms and procedures that may be required in the unlikely 
event of a major failure where the network is unable to recover itself. 

This CIP considers three representative scenarios and addresses specific considerations relevant 
in each case:  

Scenario 1 - __Long-Lived Network Partition__  
Scenario 2 - __Failure to Make Blocks for an Extended Period of Time__  
Scenario 3 - __Bad Blocks Minted on Chain__  

To ensure successful recovery in the event of a chain failure, it's crucial to establish effective 
communication channels and exercise recovery procedures in advance to familiarize the community and 
stake pool operators (SPOs) with the process.

This CIP is based on an earlier IOHK technical report that is referenced below, supplemented by internal 
documentation and discussions that have not been publicly released. It should be considered to be a living 
document that is reviewed and revised on a regular basis.  

Note that although the focus of disaster recovery is on Cardano mainnet, since this is the greatest risk
of loss of funds, the recovery procedures are generic and apply to other Cardano
networks, including SanchoNet, Preview, PreProd or private networks.
Appropriate adjustments may need to be made to reflect differences in timing or other concerns.


## Motivation: Why is this CIP necessary?

This CIP is needed to familiarize stakeholders with the processes and procedures that should be 
followed in the unlikely event that the Cardano mainnet, or another Cardano network, encounters
a situation where the built-in on-chain recovery mechanisms fail.

## Specification

While the exact recovery process will depend on the unique nature of the failure, there are three main scenarios we can consider.

### Scenario 1: Long-Lived Network Partition

Ouroboros Praos is designed to cope with real-world networking
conditions, in which some nodes may temporarily be disconnected from
the network.  In this case, the network will continue to make blocks,
perhaps at some lower chain density (reflecting the temporary loss of
stake to the network as a whole).  As nodes rejoin the network, they
will then participate in normal block production once again. In this
way, the network remains resilient to changes in connectivity.

If many nodes become disconnected, the network could divide into two
or more completely disconnected parts.  Each part of the network could
then form its own chain, backed by the stake that is participating in
its own partition.  Under normal conditions, Praos will also deal with
this situation.  When the partitioned group of nodes reconnects, the
longest chain will dominate, and the shorter chain will be discarded.
The nodes on the shorter chain will automatically rollback to the
point where the fork occurred, and then rejoin the main chain.  This
is perfectly normal.  Such forks will typically last only a few
blocks.

However, in an extreme situation, the partition may persist beyond the
Praos rollback limit of *k* blocks (currently 2,160 blocks on mainnet). 
In this case, the nodes will not be able to rollback to rejoin the main chain, since this
would violate the required Praos guarantees.


#### Remediations

Disconnected nodes must be reconnected to the main chain by their operators. This can be done 
by truncating the local block database to a point before the chain fork and then resyncing 
against the main network, using the `db-truncator` tool, for example.

Full node wallets can also be recovered in the same way, though this may require technical 
skills that the end users do not possess. It may be easier, if slower, for them to simply 
resynchronize their nodes from the start of the chain (i.e. from the genesis block).

Ouroboros Genesis provides additional resilience when recovering from long lived network partitions. 
In Praos nodes resyncing from a point before the chain fork could still in some cases follow the 
alternative chain (if it is the first one seen) and extra mechanisms may be needed to avoid this 
possibility. In Praos, for example, this may require that all participants on the alternative chain 
truncate the local block database prior to the partition being resolved. In Ouroboros Genesis 
when resyncing from a point before the chain fork, the chain selection rules will ensure 
selection of the correct path for the main chain assuming the partition has been resolved.

Alternative methods to resynchronise the node to the main chain might
include the use of Mithril or other signed snapshots.  These would
allow faster recovery.  However, in this case, care needs to be taken
to achieve the correct balance of trust against speed of recovery.

#### Additional Effects on Cardano Users

Although block producing nodes will rejoin the main network following the remediation
described above, the blocks that they have
minted while they were disconnected will not be included in the main
chain.  This may have real world effects that will not be
automatically remedied when the nodes rejoin the main chain.  For
example, transactions may have been processed that have significant
real world value, or assumptions may have been made about chains of
evidence/validity, or the timing of transactions. End users should be
aware of the possibility and include provisions in their contracts to
cover this eventuality.  It may be necessary to resubmit some or all of the
transactions that were processed on the minority chain onto the main chain.
To avoid unexpected effects, this should be done by the end users/applications, and not
by block producers acting on their behalf.

If they are not observant, stake pools, full node wallets and
other node users (e.g. explorers) could continue indefinitely on the minority
chain.  Such users should take care to be aware of this situation and
take steps to rejoin the main chain as quickly as possible.
A reliable and trusted public warning system should be considered that can alert users
and advise them on how to rejoin the main chain.


#### Timing Considerations

On Cardano mainnet, partitions of less than 2,160 blocks will automatically rejoin the main chain.  With current Cardano mainnet settings, this represents
a period of up to 12 hours during which automatic rollback will occur.  If the partition exceeds 2,160 blocks, then the
procedure described above will be necessary to allow nodes to rejoin the main chain.  Other Cardano networks may have different
timing characteristics.


### Scenario 2: Failure to Make Blocks for an Extended Period of Time

Ouroboros Praos requires *at least* one block to be produced every *3k/f* slots.  With the current Cardano mainnet
settings, that is a 36 hour period.  Such an event is extremely unlikely, but if it were to happen then the network
would be unable to make any further blocks.

#### Mitigation

It is recommended to monitor the chain for block production.  If a low density period is observed, then block producers
should be notified, and efforts made to mint new blocks prior to the expiry of the *3k/f* window.  If this is not possible
then the remediation procedures should be followed.

#### Remediation

Identify a small group of block producing nodes that will be used to recover the chain.  For Cardano mainnet, this group should have
sufficient delegated stake to be capable of generating at least 9 blocks in a 36 hour window.
It should be isolated from the rest of the network.
The chain can then be recovered by resetting the wall clocks on the group of block producing nodes,
restarting them from the last good block on the Cardano network, playing forward the chain production
at high speed (10x usual speed is recommended), while inserting new empty blocks at the slots which
are allocated to the block producers. The recovery nodes can then be restarted with normal settings, including
connections to the network.  Ouroboros Genesis then allows other nodes in the network to rapidly resynchronize
with the newly restored chain.  This would leave one or more gaps in the chain, interspersed with empty blocks.

##### Rewards Donation by Recovery Block Producers

In order to avoid allegations of unfair behaviour, block producing nodes that are used to recover the network should
donate any rewards that they receive during recovery to the treasury.


#### Additional Effects on Cardano Users

Unlike Scenario 1, no transactions will be submitted that need to be resubmitted on the chain.
Users will, however, experience an extended period during which the chain is unavailable.
Cardano applications and contracts should be designed with this possibility in mind.
Full node wallets and other node users should recover quickly once the network is restarted
but there may be a period of instability while network connections are re-established
and the Ouroboros Genesis snapshot is distributed across all nodes.


#### Timing Considerations

The chain will tolerate a gap of up to *3k/f* slots (36 hours with current Cardano mainnet settings).
A period of low chain density could have security implications that affect dynamic availability 
and leave open the possibility for future long range attacks. This may be particularly 
relevant should chain recovery be performed as described above (using less stake than is required 
for an honest majority). To mitigate the presence of an extended period of low chain density we may 
need to make use of the lightweight checkpointing mechanism in Ouroborus Genesis. Alternatively, Mithril 
could also be used to provide certified snapshots to stake pools as a means to verify the correct state of the ledger.

The adoption of Mithril for fast bootstrapping by light clients and edge nodes should help to mitigate risks 
for the types of users on the network that do not participate in consensus.

As described below, Ouroboros Genesis snapshots may also be useful as part of the recovery process.


### Scenario 3: Bad Blocks Minted on Chain

In the event that a bad block was to be minted on-chain, then some or all validators might be unable to process the block.
They would therefore stop, and be unable to restart.  Wallet and other nodes might be unable to synchronise beyond the
point of the bad block.

#### Remediation

Depending on the cause of the issue and its severity, alternative remediations might be possible. 

**Scenario 3.1**: if some existing node versions were able to process the block, but others were not, then
the chain would continue to grow at a lower chain density.  SPOs would need to be persuaded to upgrade (or downgrade)
to a suitable node version that would allow the chain to continue.  The chain density would then gradually recover to its normal level.
Other users would need to upgrade (or downgrade) to a version of the node that could follow the full chain.

**Scenario 3.2**: if no node version was able to process the block and a
gap of less than *3k/f* slots existed, then the chain could be rolled
back immediately before the bad block was created, and nodes
restarted from this point.  The chain would then grow as normal, with a small gap around the bad block.
In this case, care would need to be taken that the rogue transaction was not accidentally reinserted into the chain.  
This might involve clearing node mempools, applying filters on the transaction, or developing and deploying a new node version that 
rejected the bad block.

**Scenario 3.3**: an alternative to rolling back would be to develop and deploy a "hot-fix" node that could
accept the bad block, either as an exception, or as new acceptable behaviour.  
Nodes would then be able to incorporate the bad block as part of the chain,
minting new blocks as usual, or following the chain.
In this case, the bad block would persist on-chain indefinitely and future nodes
would also need to accept the bad block.  Such an approach is best used when the rejected block has behaviour
that was unanticipated, but which is benign in nature.  This will leave no abnormal gaps in the chain.

**Scenario 3.4**: if more than *3k/f* slots have passed since the bad block was minted, then it will be necessary to roll back the chain immediately
prior to the bad block as in Scenario 3.2, and then proceed as described for Scenario 2.  As with Scenario 2, this will leave
a series of gaps in the chain that are interspersed with empty blocks.

#### Timing Considerations

If more than *3k/f* slots have passed since the bad block was minted on-chain (36 hours with current Cardano mainnet settings),
then a mix of recovery techniques will be needed, as described in Scenario 3.4.  When deciding on the correct recovery
technique for Scenarios 3.1-3.3, consideration should be given as to whether the recovery can be successfully completed before *3k/f* slots
have elapsed.  In case of doubt, the procedure for Scenario 3.4 should be followed.

### Using Ouroboros Genesis Snapshots

Any of the above conditions may result in a period of lower chain density. The
updated consensus mechanism introduced in Ouroboros Genesis relies on making
chain density comparisons to assist a node when catching up with the network,
in order to reduce the reliance on having trusted peers when syncing. As
such, low-density periods pose a potential security risk for the future; they
are periods where a motivated adversary could perform a long-range attack by
building a higher density chain.

In order to mitigate this, Genesis introduces the concepts of lightweight
checkpoints. A lightweight checkpoint is effectively a block point - a
combination of block number and hash - which can be distributed along with the
node. Unlike Mithril Snapshots (see below), Genesis lightweight snapshots are not assured by any committee - rather, they form part of the trusted codebase distributed with the node, or by other parties.

When syncing, a Genesis node will refuse to validate past the block number of any lightweight checkpoint if the chain does not contain the correct block at that point.

Genesis snapshots play two potential roles in disaster recovery:

1. In scenarios where the network is split, a lightweight snapshot could guide
   a node from the abandoned partition in connecting to the main partition. In
   general this should not be needed, however, since the main partition should win
   out in any Genesis density comparisons. This usage also falls closer to
   scenario 2, in that it relies on an external source imposing a chain selection,
   which must then be trusted by all parties.
2. Following a disaster recovery procedure, a sufficient number of blocks
   covering the low density period should be added to the list of lightweight
   checkpoints. These would serve the purpose of preventing a subsequent
   long-range attack.

Note that, in this second scenario, concerns about the legitimacy of the
checkpoint are much less salient. The checkpoint can be issued post disaster
recovery, at such a time where the points it contains are in the past, and are
both agreed upon and easy to verify for all honest parties.


### Using Mithril Snapshots

Mithril is a stake-based threshold multi-signatures scheme. One of the applications of this protocol in Cardano
is to create certified snapshots of the Cardano blockchain. Mithril snapshots allow nodes or applications
to obtain a verified copy of the current state of the blockchain without having to download and verify the full history.

SPOs that participate in the Mithril network provide signed snapshots to a Mithril aggregator that 
is responsible for collecting individual signatures from Mithril signers and aggregating them into a multi-signature. 
Using this capability, the Mithril aggregator can then provide certified snapshots of the Cardano blockchain that
can potentially be used as a trusted source for recovery purposes.

Provided that it gains sufficient adoption on the Cardano network and that
snapshots continue to be signed by an honest majority of stake pools
following a chain recovery event, Mithril may therefore provide an
alternative solution to Ouroboros Genesis checkpoints as a way to
verify the correct state of the ledger


### Recommended Actions for Cardano mainnet

1. Monitor Cardano mainnet for periods of low density and take early action if an extended period is observed.
2. Identify a collection of block producer nodes that has sufficient stake to mint at least 9 blocks in any 36 hour window.
3. Set up emergency communication channels with stake pool operators and other community members.
4. Practice disaster recovery procedures on a regular basis.
5. Provide signed Mithril snapshots and a way for full node wallet users and others to recover from this snapshot.
6. Determine how to employ Ouroboros Genesis snapshots as part of the disaster recovery process

#### Community Engagement

One of the key requirements for successful disaster recovery will be proper engagement with the community.

1. Identify stake pool operators (SPOs) who can assist with disaster recovery
2. Discuss disaster recovery requirements with Intersect's Technical Working Groups and Security Council
3. Identify and establish the right communications channels with the community, including Intersect
4. Set up regular disaster recovery practice sessions

### Change Log

| Version | Date | Description |
| -------- | -------- | ------- |
| 0.1 | 2024-08-30 | Initial submitted version |
| 0.2 | 2024-09-10 | Revised version to emphasize genericity of recovery techniques |
| 0.3 | 2024-09-18 | Revised version following CIP editors meeting |

## Rationale: How does this CIP achieve its goals?

This CIP outlines key disaster recovery scenarios that the Cardano community should understand to mitigate
potential network outages. As a living document, it will be regularly reviewed and updated to inform 
stakeholders and encourage more detailed contingency planning. The CIP aims to facilitate discussions, 
establish recovery procedures, and encourage regular recovery practice exercises to ensure preparedness 
and validation of recovery actions in the event of an outage.

## Path to Active

### Acceptance criteria

- [x] The proposal has been reviewed by the community and sufficiently advertised on various channels.
    - [x] Intersect Technical Groups
    - [x] Intersect Discord Channels
    - [x] Cardano Forum

- [x] All major concerns or feedback have been addressed.

### Implementation Plan

N/A

## References

[Cardano Disaster Recovery Plan (May 2021)](https://iohk.io/en/research/library/papers/cardano-disaster-recovery-plan/)

[Cardano Incident Reports](https://updates.cardano.intersectmbo.org/tags/incident)

[January 2023 Block Production Temporary Outage](https://updates.cardano.intersectmbo.org/2023-04-17-ledger)

[DB Truncator Tool](https://github.com/IntersectMBO/ouroboros-consensus/tree/486753d0b7d6b0d09621d1ef8be85e5117ff3d1e/ouroboros-consensus-cardano/app)

[DB Synthesizer Tool](https://github.com/IntersectMBO/ouroboros-consensus/tree/486753d0b7d6b0d09621d1ef8be85e5117ff3d1e/ouroboros-consensus-cardano/app)

[Ouroboros Genesis](https://iohk.io/en/research/library/papers/ouroboros-genesis-composable-proof-of-stake-blockchains-with-dynamic-availability/)

[Mithril](https://github.com/input-output-hk/mithril)


## Copyright

 This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
