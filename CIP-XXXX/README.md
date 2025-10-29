---
CIP: XXXX
Title: Default SPO vote
Category: Ledger
Authors:
  - Teodora Danciu <teodora.danciu@iohk.io>
  - Alexey Kuleshevich <alexey.kuleshevich@iohk.io>
Implementors: N/A
Status: Proposed
Discussions:
  - https://github.com/cardano-foundation/CIPs/pull/1108
  - https://github.com/IntersectMBO/cardano-ledger/issues/4645
Created: 2025-10-28
License: CC-BY-4.0
---

## Abstract

We propose introducing an explicit mechanism for SPOs to define their default governance vote as part of their pool's registration parameters.
This would replace the current indirect approach, which relies on delegating the pool’s reward account to predefined DReps AlwaysNoConfidence and AlwaysAbstain.

## Motivation: why is this CIP necessary?

The current approach was always intended as a temporary workaround. While it solved the immediate problem (as discussed in [cardano-ledger#4645](https://github.com/IntersectMBO/cardano-ledger/issues/4645)), it introduces several issues:
  * It is not transparent or easily inspectable what a pool’s default vote actually is, making it difficult to understand how undelegated or non-voting stake will behave in governance actions.
  * It couples operational reward accounts with governance semantics, constraining how SPOs can use their reward accounts.
  * It can distort governance outcomes, as SPOs who do not configure their reward accounts may unintentionally default to voting No, potentially skewing proposal results.

By contrast, providing SPOs with a clear, explicit default vote parameter allows them to opt in or out of governance participation transparently, mitigating the coupling between financial and governance mechanisms and reducing long-term bias in voting behaviour.

## Specification

### Current behaviour

The "default vote" determines how *not voting* counts toward the ratification of a proposal.
For SPOs, this is currently implemented as folllows:
  * `HardForkInitiation` proposals: default is `No`
  * `NoConfidence` proposals:
      - if the pool's reward account is delegated to `AlwaysNoConfidence`, the default is `Yes`
      - otherwise, `No`
  * `UpdateCommittee` and `ParameterUpdate` (for security-group parameters) proposals:
      - if the pool reward account is delegated to `AlwaysAbstain`, the default is `Abstain`
      - otherwise, `No`

### Proposed changes

Add a new non-optional field to the pool parameters that specifies the SPO's default vote, with 3 possible values:
  * `DefaultNoConfidence`: `Yes` on `NoConfidence`, `No` on all other actions (matches delegation to `AlwaysNoConfidence`)
  * `DefaultAbstain`: `Abstain` on all actions (matches delegation to `AlwaysAbstain`)
  * `NoDefault`: `No` on all actions (matches no delegation to a default DRep)

<br>

Currently the pool parameters are specified in cddl like this:

```cddl
pool_params =
  ( operator       : pool_keyhash
    , vrf_keyhash    : vrf_keyhash
    , pledge         : coin
    , cost           : coin
    , margin         : unit_interval
    , reward_account : reward_account
    , pool_owners    : set<addr_keyhash>
    , relays         : [* relay]
    , pool_metadata  : pool_metadata/ nil
  )
```

The proposed definition is:
```cddl
pool_params =
  ( operator       : pool_keyhash
    , vrf_keyhash    : vrf_keyhash
    , pledge         : coin
    , cost           : coin
    , margin         : unit_interval
    , reward_account : reward_account
    , pool_owners    : set<addr_keyhash>
    , relays         : [* relay]
    , pool_metadata  : pool_metadata/ nil
    , default_vote   : stakepool_default_vote
  )

stakepool_default_vote = default_vote_abstain / default_vote_no_confidence / no_default_vote
default_vote_abstain = 0
default_vote_no_confidence = 1
no_default_vote  = 2
```

This change requires a hard fork, since it modifies transaction serialization.

### Migration of currently configured default votes

At the hard-fork boundary, the pool parameters of each existing pool will be updated to reflect the implicit preference currently expressed through its reward account delegation.
For each pool, we'll set the new `defaultVote` parameter to:
  * `DefaultAbstain`, if the reward account is delegated to `AlwaysAbstain`
  * `DefaultNoConfidence`, if the reward account is delegated to `AlwaysNoConfidence`
  * `NoDefault`, if the reward account is not delegated to a defaul DRep

## Path to Active

### Acceptance Criteria

- [ ] Transaction serializers and deserializers in [cardano-ledger](https://github.com/IntersectMBO/cardano-ledger) are implemented such that they follow the cddl specification described above, and reflected in the cddl specs
- [ ] The migration of the existing default vote preferences is implemented in ledger
- [ ] The feature is integrated into [cardano-node](https://github.com/IntersectMBO/cardano-node) with necessary adjustments made to [ouroboros-consensus](https://github.com/IntersectMBO/ouroboros-consensus) and released as part of the Dijkstra era hard fork

### Implementation Plan

- [ ] Add support for a new pool parameter without changing serialization in existing eras
- [ ] Implement and test migration logic to populate the new parameter at the hard-fork boundary.

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).