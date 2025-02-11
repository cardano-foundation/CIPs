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
On the other hand, the [Disaster Recovery Plan](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0135) intervenes when the chain does not grow at all for 36 hours.
These two specifications do not address an observed growth rate less than 2160 per 36 hr but greater than zero, nor does any other specification.

Such low growth rates become plausible when the assumptions of the Praos argument are violated for an extended period of time.
Global-scale disasters, infrastructure attacks, local outages, eclipse attacks, bugs, negligent misconfiguration, etc could all cause it.

## Problem

### Introduction

Some events within the ledger and protocol rules are scheduled based on the assumption that 36 hr ensures settlement.
No established document names this property, since it's typically justified via the Cardano Common Prefix property, the Cardano Chain Growth property, and _modus ponens_: the 2161th youngest block is settled and the honest chain grows by at least 2160 blocks in 36 hr.
The off-by-one in that logic is inconsequential, since the Chain Growth failure probability is negligibly greater for 2161 blocks in 36 hr.

The property will be referred to as _Immutable Age_ within this CPS.
The following lists a couple notable examples.

- The security argument of the Praos protocol makes the simplifying assumption that all of the chains that honest nodes would ever consider necessarily agree on the leader schedule [^excessive-proof].
  The ledger rules therefore snapshot certain values (eg the stake distribution, the nonce, etc) no later than 36 hr before the snapshotted value begins to affect the leader schedule.

- Beyond just the leader schedule, the ledger rules similarly ensure all values relevant to header validation (eg the max block size protocol parameter) are determined at least 36 hr before they take effect[^HFC-double].
  This enables a key network optimization: nodes first exchange comparatively small headers instead of blocks, and then only fetch the underlying blocks for the longest header chain.
  The 36 hr delay is required because a node must now be able to validate up to 2161 headers before having fetched the preceding 2160 ancestor blocks.
  The node would never need to validate the 2162th header before fetching the preceding 2161 blocks, since Common Prefix ensures it would never need to see the 2162th alternative header before deciding to switch chains.

Suprisingly, however, no part of the node directly enforces Chain Growth.
This is at least partly due to Praos intentionally tolerating _dynamic availability_, where the participation level is allowed to fluctuate, as long as the honest parties always have more stake than the adversary [^self-healing].
In other words, Immutable Age doesn't necessarily require Chain Growth.
If 75% of total stake was honest but offline[^honest-offline], and 15% was online and honest, and the remaining 9% was adversarial, then a Praos network might still be secure, since 15 > 9.
The key dynamics are that the online honest nodes will be elected much more often than the adversarial nodes during the 36 hr.
Despite not growing 2160 blocks per 36 hr, those honest nodes will still settle each successful block before it becomes 36 hr old, since the adversary is too weak to cause a deep/old enough rollback to disrupt that.

On the other hand, it's possible that the design of some Cardano node or the design of some tooling that the Cardano community has come to rely on does assume Chain Growth, either directly or indirectly and either intentionally or accidentally --- despite the node not explicitly enforcing Chain Growth.
The Cardano chain has not yet ever violated Chain Growth.
Many users and contributors tend to only consider/expect the growth that has been typically observed to be near 2160 blocks per 12 hr.
It is not commonly considered that a strong adversary could slow that down to the Chain Growth limit, or even more so if some honest stake is not well-connected, well-configured, etc.

There are many reasons participation might be low (see next section).
And there are many questions that arise about the possible behaviors of the node in such scenarios.
If growth is very low, do we expect the Cardano node to keep minting blocks?
Dynamic availability assumes we do, but maybe the community doesn't want to retain a weak portion of the chain and would prefer the Disaster Recovery Plan repairs it.
If the node should keep minting, do we expect it to continue to effectively mitigate DoS attack vectors?
When do we expect the node to switch away from a sparse chain if a denser one eventually arrives?
Do we expect the node/CLI tools/etc to obediently respond to queries even if the current answer might change if a denser chain arrives?

### Anticipated Options and Scenarios for the Chain Selection Rules

The following mutually exclusive options seem to cover the design space of the more fundamental questions of which chains the node would select/switch to, but each has unique advantages and disadvantages.
A relevant CIP, for example, might identify alternative options, introduce an insight that clarifies which of these is preferable, or maybe identify a way to combine them (eg conditions for switching between them).
CIPs might also address the other aspects of the node's behavior within these options and/or scenarios (eg withholding replies to queries).

- *AssumeImmutableAge* (AssumeIA).
  The node will always switch to a longer chain with exactly one exception: unless doing so would rollback more than 2160 blocks.
  This limit is justified by the Common Prefix property of the Praos security argument as instantiated for Cardano.
  Note the absence of the Chain Growth property: the node would rollback up to 2160 blocks regardless of their age.

  With this option, the node would select a sparse chain and would also be able to switch away from all but the youngest 2160 blocks on it, regardless of how many slots they span.

- *EnforceImmutableAge* (EnforceIA).
  As a refinement of AssumeIA, the node will switch to a longer chain unless doing so would rollback more than 2160 blocks and/or a block that is more than 36 hr older than the current selection's tip [^wall-clock-age].
  This limit is a disjunction of Common Prefix and Chain Growth.

  With this option, the node would select a sparse chain and would also be able to switch away from any of the youngest 2160 blocks, but only those that are younger than 36 hrs.

- *EnforceChainGrowth* (EnforceCG).
  In addition to AssumeIA, the node rejects any chain that has less than 2160 blocks per 36 hr (even if selecting it wouldn't require rolling back more than 2160 blocks).

  With this option, the node would never select a sparse chain; it'd select a prefix of it with degrading density but reject the first block that is more than 36 hr younger than its 2161st ancestor.

Outside of any scenario, EnforceIA and EnforceCG introduce some simplifying invariants compared to AssumeIA, simply because they are explicit.
They also have costs, discussed in the specific scenarios below.

  - The EnforceIA node can ignore chains that branch off more than 36 hr ago, even if they would only requiring rolling back at most 2160 blocks.

  - The EnforceCG node can (temporarily) ignore all blocks that are more than 36 hr younger than its 2161st youngest block.

It's possible that an AssumeIA node can be sufficiently resilient despite not having those additional invariants, but its security argument becomes more complicated.
That means mistakes are more likely, and it's more difficult to correctly add features, new protocols, etc.

These options should also be contrasted by considering the following scenarios.

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
  TODO see the questions at the end of the introduction, for example.

- The specification within such a CIP ought to make it simpler for authors of Cardano nodes and tools to analyze their resource usage bounds.
  For example, EnforceCG guarantees that the Cardano node will never select nor relay a chain that has less than 2160 blocks per 36 hr interval, which limits how many slots per block some tool might need to allocate on average.
  Even if the specification instead went to the extreme of declaring the node's behavior as "undefined" in a low participation scenario, the resource usage wouldn't even need to consider scenarios when Chain Growth is violated.
  (Though if a node is expected to be in a known state if it survives such a scenario, then its behavior during the scenario cannot be entirely undefined.)

## Copyright

This CPS is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).

[^excessive-proof]: Caveat.
  It's unclear whether Praos actually requires this, but the existing proof relies on it.

[^HFC-double]: Aside.
  The Hard Fork Combinator currently requires 72 hr forewarning for transitions between eras, but that's beyond the scope of this document.
  Also, as of Conway, the Cardano ledger happens to give 5 days of forewarning, since it needs to conservatively incrementalize the expensive vote tabulation.

[^self-healing]: Aside.
  Praos also features self-healing, where it can tolerate the adversary temporarily having a stake majority, but that's beyond the scope of this document.

[^honest-offline]: Caveat.
  The assumption that the offline stake is honest is an over-simplification, but something along those lines is necessary for Ouroboros Genesis, for example.

[^wall-clock-age]: Clarification.
  It's simpler to calculate the age of a block on the selected chain with respect to its tip.
  It is seems possible to instead calculate the age with respect to the wall clock, but that will certainly have more corner cases and likely more restrictions, due to the Hard Fork Combinator concerns.
  Moreover, in the interesting scenarios, the tip of the selection will be "close enough" to the wall clock "often enough" that this distinction is irrelevant.
