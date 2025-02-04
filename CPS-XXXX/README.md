---
CPS: XXXX
Title: Node Behavior during Low Participation
Status: Draft
Category: Consensus
Authors:
    - Nicolas Frisby <nick.frisby@iohk.io> <nicolas.frisby@moduscreate.com>
Proposed Solutions: []
Discussions:
    - https://github.com/cardano-foundation/CIPs/pull/982
Created: 2025-02-04
License: CC-BY-4.0
---

## Abstract

It is unclear how the Cardano node should behave when the best chain it has access to is so sparse that it violates the Praos security argument's lower bound on Chain Growth.
This CPS motivates that question, lists some relevant concerns, and hopefully attracts some useful CIPs.

The [Praos security argument](https://eprint.iacr.org/2017/573) assigns overwhelming probability to a lower bound on growth under the assumption that all honest parties are participating and together control more stake than the adversary.
For Cardano specifically, that Chain Growth property has been instantiated as at least 2160 blocks of growth during each 36 hr interval, whereas the expected Cardano growth is 2160 blocks per 12 hr (assuming full participation).
On the other hand, the [Disaster Recovery Plan](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0135), intervenes when the chain does not grow at all for 36 hours.
These two specifications do not address an observed growth rate less than 2160 per 36 hr but greater than zero, nor does any other specification.

Such low growth rates become plausible when the assumptions of the Praos argument are violated for an extended period of time.
Global-scale disasters, infrastructure attacks, local outages, eclipse attacks, bugs, negligent misconfiguration, etc could all cause it.

## Problem

The following mutually exclusive options seem to cover the design space, but each has unique advantages and disadvantages.

- *AssumeImmutableAge* (AssumeIA).
  The node will not switch to a chain if doing so would rollback more than 2160 blocks regardless of their age.
  This limit is justified by the Common Prefix property of the Praos security argument as instantiated for Cardano.
  (Note the absence of the Chain Growth property.)

- *EnforceImmutableAge* (EnforceIA).
  As a refinement of AssumeIA, the node will not switch to a chain if doing so would rollback more than 2160 blocks and/or a block that is more than 36 hr old (TODO: should age be with respect to the wall clock or the selection's tip?).
  This limit is a disjunction of Common Prefix and Chain Growth.

- *EnforceChainGrowth* (EnforceCG).
  In addition to AssumeIA, the node rejects any chain that has less than 2160 blocks per 36 hr (even if selecting it wouldn't require rolling back any blocks).

These options can be compared by considering the following scenarios.

- *TwoThirdsInaccessible*.
  Suppose more than 2/3rds of stake was knocked offline (eg by a solar flare) such that less than 1/3rd of all stake was active for more than 36 hr, but it all remained connected.

    - The other scenarios all involve this one to some degree, so it serves as a baseline.

    - If the adversary controls less than half of the surviving stake, then it still cannot defeat Praos during the outage.

    - Note that the chain would have a growth rate less than 2160 per 36 hr but greater than zero.
      
    - If the whole network implemented AssumeIA, then the 2161th youngest block would be at least three times older than usual (36+ hr instead of 12 hr).
      Since the nodes and/or other Cardano community tooling might have been designed around the guarantee of at most 36 hrs for 2160 blocks, they could fail outright or become more vulnerable to possible DoS attacks during the outage.

    - If the whole network implemented EnforceIA, then the nodes would not face increased risks.
      The 2160 disjunct in the EnforceIA definition is an optimization for when the chain is growing faster than 2160 blocks per 36 hr.

    - If the whole network implemented EnforceCG, then the Recovery Plan would be unavoidable (once the affected stake was back online).
      The silver lining is that all nodes would be able to switch to the repaired chain automatically, without needing manual intervention.

- *GranularPartitions*.
  Suppose the block-producing nodes of the Cardano network are partitioned and/or knocked offline (eg by a global infrastructure attack) such that no partition has more than 1/3rd of all stake for more than 36 hr.

    - The TwoThirdsInaccessible scenario applies within each group of connected nodes.

    - If the whole network implemented EnforceCG, then the Recovery Plan would be unavoidable.
      The silver lining is that all nodes would be able to switch to the repaired chain automatically, without needing manual intervention.

    - If the whole network implemented AssumeIA, then any nodes on a chain that grew less than 2160 blocks during the partition would automatically switch to a denser chain once connectivity was re-established.
      If multiple chains grew by 2160 blocks, then some nodes will require manual intervention: it depends on which of those chains each node sees upon re-establishing connection.
      If only one chain grew by 2160 blocks, then the whole network would recover without needing any manual intervention.
      However, recall that the TwoThirdsInaccessible scenario applies, so perhaps all of these AssumeIA nodes failed during the outage.
      Even if automatic recovery were possible, the community might decide that the Disaster Recovery Plan is the only fair option, and then all nodes would require manual intervention.

    - If the whole network implemented EnforceIA, then no nodes would be able to switch away from the blocks they minted during the partition when connectivity was re-established.
      At most one group of nodes wouldn't need manual intervention.
      And all groups would need it in the case of the Disaster Recovery Plan.

- *SkewedPartitions*.
  Suppose the block-producing nodes of the Cardano network are partitioned and/or knocked offline (eg by an eclipse attack) such that some partitions have more than 1/3rd of all stake for more than 36 hr.

    - The GranularPartitions scenario mostly applies, with one key exception: one or two groups were not in a TwoThirdsInaccessible scenario.
      (It could actually be more than two groups, but only if the adversary is overtly minting blocks in multiple groups).
      If it's one group, then it has the highest density and the nodes in it were not at risk during the partition, regardless of which option they implement.

    - The only question then is whether the groups with less than 1/3rd stake need manual intervention.
      For EnforceCG they don't, for EnforceIA they do, and for AssumeIA it depends on how many blocks they grew during the partition.

- *BadStake*.
  Suppose a bug that was latent for several releases enables an attack vector that ends up splitting the network such that only 1/3rd of stake remains on the valid chain while 2/3rds of stake incorrectly accepts and extends an invalid block that cannot be accepted (eg the adversary distorted the stake distribution).
  For example, suppose there are two popular implementations of the Cardano node, and the bug affects the one deployed by 2/3rds of stake.

    - If the buggy implementation cannot deploy a hot patch to the vast majority of their users within less than 24 hr, then this partition would persist indefinitely without manual intervention for the nodes on the unacceptable chain.
      (Depending on the severity of the bug, the adversary might be able to accelerate their block production immediately, which would reduce that 24 hr window of opportunity even further.)

    - If the patch isn't adopted quickly enough, then the Recovery Plan or similar such off-chain cooperation requiring eventual manual intervention might be the only way for the community to agree on an outcome, eg due to the qualitative culpability difference between this bug and, say, a solar flare.

    - If the Recovery Plan is not used, then the acceptable chain is effectively in the TwoThirdsInaccessbile scenario.
      As such, EnforceIA is the only option that avoids the chain halting and increased risk for the non-buggy nodes.

### Summary

There are multiple mutually-exclusive options, and which is most appealing depends on the details of the low participation scenario.
Without more information, no single option seems best for the node.

In the following table: :tada: is good, :warning: is bad, and :-1: is in the middle/unclear/disappointing.

| Option | Keys behaviors when a group's chain grows by less than 2160 blocks per 36 hr | Complexity |
| - | - | - |
| EnforceCG | :warning: chain will stop growing, and thus :tada: the node will be able to switch off it, and :tada: the resource usage need not increase | :tada: the specification provides a simple guarantee for for downstream tools |
| EnforceIA | :tada: chain will grow, but :warning: the node will be unable to switch off it after 36 hr regardless of growth rate, and :tada: the resource usage need not increase | :-1: only bounds rollback block count and slot count for downstream tools (no density lower bound) |
| AssumeIA | :tada: chain will grow, and :-1: the node might able to switch off it after 36 hr depending on growth rate, but :warning: the resource usage may increase | :-1: only bounds rollback block count for downstream tools (no density lower bound) |
 
Note well that these three options are merely what has already been considered.
There may be others to find and assess.
For example, perhaps the node should implement all three, and the node operator could choose between them.
Vigilant operators could then switch their node's behavior depending on which scenario they believe the network is in.
Or perhaps there is an as-of-yet unidentified option that supercedes all of these.

## Goals

- Any CIP that solves this CPS must specify how the node should behave when the best chain it has access to grows by less than 2160 blocks per 36 hr.

- The specification within such a CIP ought to make it simpler for authors of Cardano nodes and tools to analyze their resource usage bounds.
  For example, EnforceCG guarantees that the Cardano node will never select nor relay a chain that has less than 2160 blocks per 36 hr interval, which limits how many slots per block some tool might need to allocate on average.
  Even if the specification instead went to the extreme of declaring the node's behavior as "undefined" in a low participation scenario, the resource usage wouldn't even need to consider scenarios when Chain Growth is violated.
  (Though if a node is expected to be in a known state if it survives such a scenario, then its behavior during the scenario cannot be entirely undefined.)

## Copyright

This CPS is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
