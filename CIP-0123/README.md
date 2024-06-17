---
CIP: CIP-0123?
Title: Disaster Recovery Plan for Cardano
Category: Cardano Information
Status: Proposed
Authors:
    - Kevin Hammond <kevin.hammond@iohk.io>
	- Sam Leathers <samuel.leathers@iohk.io>
	- Alex Moser <alex.moser@cardanofoundation.org>
	- Steve Wagendorp <steve.wagendorp@cardanofoundation.org>
	- Rick McCracken
	- Adam Dean
Implementors: []
Discussions:
    - https://github.com/cardano-foundation/CIPs/pull/?
Created: 2024-06-17
License: CC-BY-4.0
---

<!-- Existing categories:

- Meta     | For meta-CIPs which typically serves another category or group of categories.
- Wallets  | For standardisation across wallets (hardware, full-node or light).
- Tokens   | About tokens (fungible or non-fungible) and minting policies in general.
- Metadata | For proposals around metadata (on-chain or off-chain).
- Tools    | A broad category for ecosystem tools not falling into any other category.
- Plutus   | Changes or additions to Plutus
- Ledger   | For proposals regarding the Cardano ledger (including Reward Sharing Schemes)
- Catalyst | For proposals affecting Project Catalyst / the Jörmungandr project

-->

## Abstract
<!-- A short (\~200 word) description of the proposed solution and the technical issue being addressed. -->
While the Cardano network has proved to be highly reliable, it is necessary to consider how the Cardano network can be recovered in the unlikely 
event of a major failure where the network does not recover itself.  This CIP considers three representative scenarios and explains
in outline how the chain could recover if each of these situations were to arise.



## Motivation: why is this CIP necessary?
<!-- A clear explanation that introduces the reason for a proposal, its use cases and stakeholders. If the CIP changes an established design then it must outline design issues that motivate a rework. For complex proposals, authors must write a Cardano Problem Statement (CPS) as defined in CIP-9999 and link to it as the `Motivation`. -->


## Specification
<!-- The technical specification should describe the proposed improvement in sufficient technical detail. In particular, it should provide enough information that an implementation can be performed solely on the basis of the design in the CIP. This is necessary to facilitate multiple, interoperable implementations. This must include how the CIP should be versioned, if not covered under an optional Versioning main heading. If a proposal defines structure of on-chain data it must include a CDDL schema in its specification.-->

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
Praos rollback limit of *k* blocks (currently 2,160).  In this case, the nodes
will not be able to rollback to rejoin the main chain, since this
would violate the required Praos guarantees.


#### Remediations

Disconnected nodes must be reconnected to the main chain by their operators.  This can be done
by truncating the local block database to a point before the chain fork and then resycing
against the main network.  This can be done by the `db-truncator` tool.

Full node wallets can also be recovered in the same way, though this
may require technical skills that the end users do not possess.  It
may be easier, if slower, for them to simply resynchronize their nodes
from genesis.  This could take some time.  An alternative might be to
restore using a Mithril or other signed snapshot.  In this case, care
needs to be taken to achieve the correct balance of trust against
speed of recovery.  



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
To avoid unexpected effects, this should be done by the end users, and not
by block producers acting on their behalf.

If they are not observant, stake pool operators, full node wallets and
other node users (e.g. explorers) could continue indefinitely on the minority
chain.  Such users should take care to be aware of this situation and
take steps to rejoin the main chain as quickly as possible.
A reliable and trusted public warning system should be considered that can alert users
and advise them on how to rejoin the main chain.


#### Timing Considerations

Partitions of less than 2,160 blocks will automatically rejoin the main chain.  With current Cardano settings, this represents
a period of up to 12 hours during which automatic rollback.


### Scenario 2: Failure to Make Blocks for an Extended Period of Time

Ouroboros Praos requires *at least* one block to be produced every *3k/f* slots.  With the current Cardano mainnet
settings, that is a 36 hour period.  Such an event is extremely unlikely, but if it were to happen then the network
would be unable to make any further blocks.

#### Mitigation

It is recommended to monitor the chain for block production.  If a low density period is observed, then block producers
should be notified, and efforts made to mint new blocks prior to the expiry of the *3k/f* window.  If this is not possible
then the remediation procedures should be followed.

#### Remediation

Identify a small group of block producing nodes that will be used to recover the chain.  This group should have
sufficient delegated stake to be capable of generating at least 9 blocks in a 36 hour window.
It should be isolated from the rest of the network.
The chain can then be recovered by resetting the wall clocks on the group of block producing nodes,
restarting them from the last good block on Cardano mainnet, playing forward the chain production
at high speed (10x usual speed is recommended), while inserting new empty blocks at the slots which
are allocated to the block producers.  An Ouroboros Genesis snapshot can be created once the recovery
nodes have caught up to real time. The recovery nodes can then be restarted with normal settings, including
connections to the network.  Ouroboros Genesis then allows other nodes in the network to rapidly resynchronize
with the newly restored chain.

#### Additional Effects on Cardano Users

Unlike Scenario 1, no transactions will be submitted that need to be resubmitted on the chain.
Users will, however, experience an extended period during which the chain is unavailable.
Applications and contracts should be designed with this possibility in mind.
Full node wallets and other node users should recover quickly once the network is restarted
but there may be a period of instability while network connections are re-established
and the Ouroboros Genesis snapshot is distributed across all nodes.

#### Timing Considerations

The chain will tolerate a gap of up to *3k/f* blocks (36 hours with current Cardano settings). 

### Scenario 3: Bad Blocks

In the event that a bad block was to be minted on-chain, then the chain

#### Remediation

### Mithril


## Recommended Actions

1. Monitor the network for periods of low density and take early action if an extended peroo.
2. Identify a collection of block producer nodes that has sufficient stake to mint least 9 blocks in any 36 hour window.
3. Set up emergency communication channels with stake pool operators and other community members.
4. Practice disaster recovery procedures on a regular basis.
5. Provide signed Mithril snapshots and a way for full node wallet users and others to recover from this snapshot.
6. 


## Rationale: how does this CIP achieve its goals?
<!-- The rationale fleshes out the specification by describing what motivated the design and what led to particular design decisions. It should describe alternate designs considered and related work. The rationale should provide evidence of consensus within the community and discuss significant objections or concerns raised during the discussion.

It must also explain how the proposal affects the backward compatibility of existing solutions when applicable. If the proposal responds to a CPS, the 'Rationale' section should explain how it addresses the CPS, and answer any questions that the CPS poses for potential solutions.
-->

## References

[Cardano Disaster Recovery Plan (May 2021)](https://iohk.io/en/research/library/papers/cardano-disaster-recovery-plan/)

[DB Truncator Tool]()

[DB Synthesizer Tool]()

[Ouroboros Genesis]()

[Mithril]()


## Copyright
<!-- The CIP must be explicitly licensed under acceptable copyright terms.  Uncomment the one you wish to use (delete the other one) and ensure it matches the License field in the header: -->

<!-- This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode). -->
<!-- This CIP is licensed under [Apache-2.0](http://www.apache.org/licenses/LICENSE-2.0). -->
