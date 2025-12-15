---
CIP: ????
Title: Removal of Epoch Boundary Blocks
Status: Draft
Category: Consensus
Authors:
  - Nicolas Frisby <nicolas.frisby@iohk.io> <nicolas.frisby@moduscreate.com>
Implementors:
  - TODO IOE? Tweag? Nicolas Frisby either way, most likely <nicolas.frisby@iohk.io> <nicolas.frisby@moduscreate.com>
  - TODO various tooling authors throughout the community?
Discussions:
  - Original tech debt Issue, https://github.com/IntersectMBO/ouroboros-consensus/issues/386
  - This PR, https://github.com/cardano-foundation/CIPs/pull/974
Created: 2025-01-29
License: CC-BY-4.0
---

## Abstract

Epoch Boundary Blocks (EBBs) are a historical mistake that spoils some natural invariants of the Ouroboros family of protocols while providing no benefit whatsoever.
The Cardano network stopped producing EBBs as of epoch 176 (several months before the end of the Byron era), but one EBB exists at the start of each prior epoch on the historical chain.
This proposal is to remove those EBBs from the historical chain, in order to ultimately simplify the node itself and probably some Cardano tooling as well.

## Motivation: why is this CIP necessary?

In the modern Cardano protocol for the Byron era (ie permissive BFT), an EBB influences no state, neither the protocol nor the ledger.
Relatedly, EBBs contain no transactions and are not signed — they contain even less information than an empty modern block.

An EBB's only consequence is an additional step on the chain's sequence of block hashes and the various exceptions, side-conditions, and corner cases necessary to accommodate EBBs in the node's specification and implementation.
The most egregious of which is that an EBB occupies the same slot as its successor and has the same difficulty (ie BlockNo) as its predecessor.
As an old, exotic, and useless class of block, EBBs have been initially overlooked in our subsequent design work many times and have ultimately wasted many hours of work as developers troubleshoot and ultimately determine how to accommodate EBBs via corner-cases etc.
But a great deal of the trouble with EBBs has been time lost coping with them in discussions that were not recorded in a manner that demonstrates the EBBs' obstruction.
Several former and current Consensus developers can attest to the trouble with EBBs, if that is deemed necessary.)

It is therefore desirable to remove EBBs from the historical chain, so that the  complications they necessitate can be eliminated from existing _and new_ nodes' specifications and implementations, except for the small set of prev-hash overrides proposed by this CIP.

However, doing so will disrupt some tooling that would otherwise expect the node to continue serving EBBs as part of the historical chain.
Moreover, new nodes alternative to the venerable Haskell reference Cardano implementation are in development.
Hence this CIP to open up the discussion of this adjustment of the historical chain to the community.

## Specification

The removal will proceed in stages.

- In Stage One, nodes would be relaxed to allow upstream chains to omit EBBs, using a minor patch to the validation logic to allow these known finite exceptions to the prev-hash condition.
  Regardless of whether it received EBBs when syncing the historical chain, this node would always store EBBs (even _ex nihilo_) and serve them to downstream nodes.

- Once Stage One is sufficiently widespread, Stage Two would delete EBBs from immutable and volatile storage upon startup — aka _database migration_ — and therefore it would no longer serve EBBs to downstream peers.
  This is when tooling such as db-sync, Mithril, etc would notice the change in behavior, which could be disruptive.

- Finally, once Stage Two is sufficiently widespread, Stage Three would forbid upstream peers from sending EBBs.

## Rationale: how does this CIP achieve its goals?

The staging ensures interop between each successive stage, such that each Stage's node and its predecessor node will always be able to sync to/from one another.

| Node Version | Proto Upstream | Proto Downstream | Storage |
| - | - | - | - |
| Stage Zero (ie today's node) | :red_circle: require EBBs | :red_circle: serve EBBs | :red_circle: store EBBs |
| Stage One | :yellow_circle: treat EBBs as optional | :red_circle: serve EBBs | :red_circle: store EBBs |
| Stage Two | :yellow_circle: treat EBBs as optional | :green_circle: skip EBBs | :green_circle: do not store EBBs |
| Stage Three | :green_circle: reject EBBs | :green_circle: skip EBBs | :green_circle: do not store EBBs |

As of Stage Three, all nodes would relay a chain that contains no EBBs and would never store them.
EBBs could now be entirely removed from the node specification and implementation, except for the prev-hash overrides described in this CIP.

If a Stage One node is itself syncing, it might omit an EBB when serving its (volatile) chain to an un-upgraded downstream peer that requires all EBBs be sent.
This is an acceptable failure case, because nodes/tools should not be syncing from syncing nodes.

### Alternative Stages

Instead of gating the next Stage on whether enough of the network has adopted the current Stage, the Stages could be gated by handshake versions.
This allows Stage One and Stage Two to be combined, at the cost of the additional complexity necessary for the Stage OneAndTwo node to conditionally require/send EBBs depending on the mini protocol version negotiated with each upstream/downstream peer.

| Handshake Version | Proto Upstream | Proto Downstream |
| - | - | - |
| X (ie today's latest handshake version) | :red_circle: require EBBs | :red_circle: serve EBBs |
| Y (>X) | :green_circle: reject EBBs | :green_circle: skip EBBs |

| Node Version | Allowed Handshake Versions | Storage |
| - | - | - |
| Stage Zero (ie today's node) |  ?≤v≤X | :red_circle: store EBBs |
| Stage OneAndTwo | ?≤v≤Y | :red_circle: store EBBs |
| Stage Three | Y≤v≤? | :green_circle: do not store EBBs |

The simpler plan seems generally preferable in the absence of any unanticipated urgency — we've already suffered EBBs for several years.
On the other hand, the handshake versions might make it easier for different implementations of the node coordinate progress on this CIP.

### Alternative Mitigations

- An alternative to removing EBBs would be to confine their difficulties to the Byron era.
  For example, if the Storage Layer were to differentiate between each era of the chain, then the main pain points of EBBs could at least be confined to the Byron era's Storage Layer logic.
  However, today's Storage Layer is era-agnostic, so this approach is not immediately available.
  There are some other reasons to make the Storage Layer differentiate between eras (eg Byron chains are 20x denser than subsequent eras), but those have not yet become a justification for the additional design complexity that would necessitate.
  And even if the Storage Layer could already differentiate eras, the changes would still pose similar issues to some of the community tooling (eg Mithril) as does this CIP, since the Storage Layer for historical eras after Byron would ideally be changed as well --- otherwise EBBs have not really been confined to Byron.
  Even so, this alternative would be disruptive to less tooling, since EBBs would (unfortunately) remain on the historical chain.

### Open Questions

TODO This section needs to be resolved as part of this PR before the status of this CIP can transition from Draft to Proposed.

- Deleting EBBs from the Storage Layer would spoil extant Mithril snapshots.
  In general, how would Mithril handle any kind of change to the on-disk representation of the historical chain---are migration paths permanently required, effectively?

- Discussion on this CIP's [PR](https://github.com/cardano-foundation/CIPs/pull/974) revealed that community tooling authors do not anticipate much disruption.

## Path to Active

### Acceptance Criteria

- A release of the Haskell reference Cardano node implementation and documentation satisfies Stage Three above: EBBs are never stored and never exchanged with peers.

- Optionally, the ledger specification and reference implementation removes all mention of EBBs, except for the prev-hash overrides.

- Once they're removed from the chain, it would be preferable for the EBBs to still be somehow available, even just for reference.

### Implementation Plan

- In Stage One, the node's initialization logic will delete any EBBs from volatile storage.
  (EBBs are typically only in the immutable storage, but upgrading in the middle of a fresh sync could result in an EBB in the volatile storage.)

- In Stage One, just before persisting an immutable block whose prev-hash is a known EBB, persist that EBB (sourced from a static lookup table --- LZ4 compression reduces each of the 176 EBBs down to about 30 kilobytes, so this table is affordable).

- In Stage One and Stage Two, discard a received EBB immediately after the BlockFetch client yields it — do not store it, do not consider selecting it, etc.

- In Stage One and Stage Two, the prev-hash field of a header received from upstream may either identify the previously sent header or the hash of an known EBB whose prev-hash field identifies the previously sent header.

- In Stage One and Stage Two, when finding paths in the volatile blocks, substitute any prev-hash field that refers to a known EBB by that EBB's prev-hash field.

- In Stage Two and Stage Three, the node's initialization logic should delete any EBBs from persistent storage — aka _database migration_.
  (EBBs are typically only in the immutable storage, but upgrading in the middle of a fresh sync could result in an EBB in the volatile storage.)

- In Stage Three, all changes for Stage One and Stage Two can be reverted except the database migration.
  Instead, the codec for Byron blocks will swap out the prev-hash field that identifies a known EBB with that EBB's prev-hash field, and moreover the codec will refuse to parse EBBs.

- At any point, the existing EBBs can be archived
  Any of the following three strategies would suffice.
    - Some tool that is small enough and easy enough to maintain alongside the reference node's source code would be able to regenerate the EBBs from the corresponding historical ledger states (the list of 176 EBB hashes is a lightweight and easy test suite)---recall that each EBB is merely a function of the incoming ledger state.
      The main difficulty would be rederiving the necessary logic, which has been irrelevant for several years (probably from <https://github.com/input-output-hk/cardano-sl/blob/1499214d93767b703b9599369a431e67d83f10a2/db/src/Pos/DB/Block/Lrc.hs#L244-L254>).
    - The 176 EBBs (several megabytes in total, when compressed) are somehow archived off-chain.
      The community would need to establish a best practice for this sort of archival, in a separate CIP presumably.
      Such a CIP would likely also be useful for any future work towards truncating the historical chain.
    - Since the 176 EBBs are relatively small, they could be chunked up and stored as UTxO datums on-chain.
      This last option may seem wasteful, but an extra several megabytes of ledger state will go unnoticed in the long run and it's the only way to trivially ensure that the EBBs are always accessible if the chain itself is.
      The main difficulty would be the fees for the necessary transactions and ensuring all the datums are easy to locate in the future.

## References

- The hashes and prev-hashes of all known EBBs, <https://github.com/IntersectMBO/ouroboros-consensus/blob/534c2c2107dcdb2b962c1483bb02a14beae2e608/ouroboros-consensus-cardano/src/byron/Ouroboros/Consensus/Byron/EBBs.hs>.
- The logic originally responsible for creating the payload of all known EBBs, <https://github.com/input-output-hk/cardano-sl/blob/1499214d93767b703b9599369a431e67d83f10a2/db/src/Pos/DB/Block/Lrc.hs#L244-L254>.

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
