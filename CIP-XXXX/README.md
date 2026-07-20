---
CIP: "?"
Title: Pruning Abandoned Pools
Category: Ledger
Status: Proposed
Authors:
    - Ryan Wiley <cerkoryn@gmail.com>
Implementors: []
Discussions:
    - Original PR: https://github.com/cardano-foundation/CIPs/pull/?
Created: 2026-07-10
License: CC-BY-4.0
---

## Abstract

Appendix C, "Design Option: Stale Stake", of the [Shelley Delegation and Incentives Design Specification](https://github.com/intersectmbo/cardano-ledger/releases/latest/download/shelley-delegation.pdf) identified "stale stake" as a potential issue. It is classified as stake that is delegated to a pool that is no longer operating, but never submitted a deregistration transaction.  Because an unavailable pool can still be elected to produce blocks, the specification recognized stale stake as a threat to chain growth and proposed pruning persistently non-performing pools. That design option was not included in the initial Shelley release and consequently, stake pools today can be assigned blocks via the slot lottery even though their operators have abandoned them, hurting chain density.

This CIP introduces a governance-updatable protocol parameter, `spoActivity`, measured in epochs. A registered pool is automatically pruned when it has neither produced a block on the adopted chain nor submitted an accepted pool registration certificate for `spoActivity` epochs. Producing a block or updating the registration renews the pool's expiration. The initial value recommendation is 73 epochs, approximately one year.

This CIP implements the deferred stale-stake objective through a deterministic activity period. Automatic pruning uses the existing pool-retirement behavior: the pool deposit is refunded according to the current rules, delegations to the pool are removed, and the pool must register again to return. Pruning changes delegation state only.  It does not move, lock, or confiscate delegated ADA, which remains spendable and can be redelegated by its owner. A pool that produces no blocks generates no new pool rewards. The mechanism does not attempt to infer private leader assignments or punish temporary underperformance.

## Motivation: Why is this CIP necessary?

Appendix C, "Design Option: Stale Stake", of the Shelley Delegation and Incentives Design Specification begins from a direct chain-growth problem: an elected pool that has stopped operating will not produce its block. It proposed monitoring apparent pool performance and pruning a pool when:

1. its apparent performance remained zero for a period of time
2. its stake made repeated leader election statistically likely.

The Shelley specification left this mechanism as a future design option and instead relied on delegators noticing reduced rewards and moving away. That response is incomplete when delegators are inactive, have lost their keys, or do not monitor pool performance. Because registration is persistent, a pool whose operator disappears without submitting a retirement certificate can remain registered indefinitely. Its delegated stake remains eligible for private leader elections, and any resulting unfulfilled opportunities reduce chain density.

The same persistent registration also affects governance. An SPO that does not vote is normally assigned an implicit `No`, except where its reward credential selects a predefined voting option with different behavior. Stake delegated to an abandoned but registered pool can therefore remain in the denominator for governance actions that require SPO approval while the operator is no longer participating. Obsolete pool and delegation entries also remain in ledger state.

This CIP completes the Shelley stale-stake design with a simpler inactivity test. The original statistical condition is difficult to apply uniformly because a large pool can be expected to produce blocks frequently while a functioning small pool may go many epochs without an opportunity. Instead, this CIP recognizes two deterministic and publicly observable proofs of pool activity:

- a block from the pool on the adopted chain
- an accepted registration or re-registration certificate for the pool.

A small pool that does not produce a block within the activity period can remain registered by submitting its current pool parameters again. An abandoned pool whose operator no longer uses the cold key will eventually be pruned.

The expected benefits are:

- improved chain density when stake delegated to abandoned pools is removed from the slot lottery
- removal of abandoned pools and their stake from the voting distributions for governance actions that require SPO approval, subject to the predefined voting-option exceptions
- pruning of obsolete pool and delegation state

The size of these effects is an empirical question. Canonical block counts alone cannot identify missed leader opportunities because private leader schedules are not public and competing leaders, forks, and ordinary downtime also affect observed block production. This CIP therefore does not attribute any measured block-density shortfall solely to inactive pools. It supplies a deterministic protocol rule for registrations whose operators have ceased both observable forms of pool activity.

### Examples of long-inactive registered pools

A Koios snapshot taken on 2026-07-10 during epoch 642, found registered, non-retiring pools with substantial active stake and activity gaps well beyond the proposed one-year period:

| Pool | Active stake | Latest canonical block | Latest registration update |
| --- | ---: | --- | --- |
| `pool1lq7...afnr3` | 7.24M ADA | Epoch 479, 2024-04-18 | 2020-12-10 |
| `MKM` | 1.94M ADA | Epoch 515, 2024-10-15 | 2023-08-09 |
| `CBUS` | 1.25M ADA | No canonical block found | 2022-12-17 |
| `FLY` | 1.04M ADA | Epoch 363, 2022-09-15 | 2021-08-17 |

These examples do not prove operator intent or loss of keys. They do show that the registered pool set contains pools behaving as abandoned: they retain delegated stake while producing no blocks and submitting no pool update for periods substantially longer than 73 epochs. Such pools continue to be assigned blocks by the protocol and implicitly vote `No` in all governance matters.

The community-operated [Non-Producing Pool Monitor](https://server-tools.grahamsnumberplus1.com/non_producing_pools_V1.html), maintained by the owner of the GNP1 pool, independently illustrates the stale-stake problem. It lists registered pools with at least 500,000 ADA of live stake that have not produced a block for two or more months, and compares each pool's declared pledge with stake at its owner addresses. An unmet pledge is presented as evidence that the operator may have walked away, while a met pledge may indicate a broken or misconfigured pool.

## Specification

### Definitions

For this CIP:

- **Activity epoch** is the epoch in which qualifying pool activity is recorded.
- **Qualifying pool activity** is either a canonical block produced by the pool or an accepted pool registration certificate for that pool.
- **Canonical block** is a block on the chain currently adopted by the node. Activity introduced by a block that is later rolled back is also rolled back.
- **Abandoned pool** is a registered pool that satisfies the inactivity test at an epoch boundary.
- **Automatic pruning** is the application of the existing pool-retirement behavior to an abandoned pool without requiring a retirement certificate from its operator.

### Protocol parameter

Add the governance-updatable protocol parameter:

```text
spoActivity : epoch_interval
```

`spoActivity` is a strictly positive integer number of epochs. A protocol-parameter update that sets it to zero or otherwise falls outside the `epoch_interval` encoding MUST be rejected. Its numeric CBOR key MUST be allocated during integration into the target ledger era so that it does not collide with other protocol parameters introduced by that era.

### Ledger state

Extend the pool state with:

```text
poolExpiration : PoolKeyHash -> Epoch
```

`poolExpiration` MUST have an entry for every registered pool. It records the epoch boundary at which the pool will be pruned unless qualifying activity renews it.

### Activity updates

When a block is adopted in epoch `A`, the block issuer's expiration MUST be set using the current value of `spoActivity`:

```text
poolExpiration[issuerPool] := A + spoActivity
```

Only activity on the adopted chain counts. Normal ledger rollback restores the expiration map to the state associated with the rollback point.

When a valid pool registration certificate is accepted in inclusion epoch `A`, the registered pool's expiration MUST be set using the current value of `spoActivity`:

```text
poolExpiration[registeredPool] := A + spoActivity
```

This rule applies both to first registration and re-registration of an existing pool. A re-registration MAY contain the same pool parameters as the registration it replaces.

The activity reset occurs when the certificate is accepted, not when any changed pool parameters become effective.

### Inactivity test

At the transition into epoch `E`, define the abandoned-pool set as:

```text
abandonedPools(E) =
  { pool |
      pool is registered
      and E >= poolExpiration[pool]
  }
```

The comparison is inclusive. Activity in epoch `A` with `spoActivity = P` sets the expiration to `A + P`. The pool remains registered through epoch `A + P - 1` and is first pruned at the transition into epoch `A + P`.

Activity included in the last eligible epoch resets the deadline. Activity included in the first block after the pruning boundary is too late to prevent pruning, because the epoch transition has already occurred. The operator may instead register the pool again under the normal registration rules.

### Pool pruning

At each epoch boundary, the set supplied to the existing pool-retirement transition MUST be the set union of:

1. pools whose explicit retirement becomes effective in that epoch
2. `abandonedPools(E)`.

Set union ensures that a pool appearing in both sets is processed only once. An explicit retirement takes effect first when its announced epoch is earlier than the pruning deadline; automatic pruning takes effect first when the inactivity deadline is earlier.

All existing pool-retirement effects apply unchanged, including:

- removing the pool's current and future parameter entries
- removing its scheduled retirement entry
- removing stake delegations to the pruned pool
- refunding the recorded pool deposit to the pool reward account when that reward account is registered
- transferring an unclaimed refund according to the existing treasury fallback
- excluding the pool and its former delegations from subsequent stake and SPO-voting snapshots according to existing snapshot timing.

The extended transition MUST also remove `poolExpiration[pool]`. This applies to both explicit retirement and automatic pruning, so the expiration map contains entries only for registered pools.

Automatic pruning MUST NOT refund a deposit twice or otherwise distinguish the value treatment of a pruned pool from an explicitly retired pool.

If a pruned pool registers again, it is a new registration under the existing rules. The appropriate pool deposit is required, and delegations deleted by pruning are not restored. Delegators must submit new delegation certificates.

### Bootstrap

When this feature is first activated, the ledger MUST:

1. set the initial value of the new `spoActivity` parameter.
2. set `poolExpiration[pool]` to `activationEpoch + spoActivity` for every pool registered at the activation boundary.

This gives every existing pool the same initial expiration without requiring historical activity to be reconstructed. No existing pool can be pruned until 73 epochs after activation.

### Parameter changes

Protocol-parameter changes take effect under the normal governance enactment rules and apply prospectively:

- Existing `poolExpiration` values MUST NOT be changed when `spoActivity` is enacted.
- The enacted value is used the next time a pool produces a canonical block or submits an accepted registration certificate.
- Increasing `spoActivity` does not extend an existing expiration unless the pool renews before that expiration.
- Decreasing `spoActivity` does not shorten an existing expiration. The pool adopts the shorter interval when it next renews.

This avoids a bulk rewrite of registered-pool state when the parameter changes. The new interval takes effect gradually as pools renew.

### Queries and operator visibility

Node protocol-parameter queries MUST expose `spoActivity`.

Ledger-state and supported query interfaces SHOULD expose, for each registered pool:

- `poolExpiration`
- any earlier explicitly scheduled retirement epoch.

No new CLI certificate command is required. An operator may renew activity using the existing pool registration workflow and the pool's current parameters.

### Versioning and backward compatibility

Existing pool registration and retirement certificate formats are unchanged. The target era adds `spoActivity` to the protocol-parameter encoding and `poolExpiration` to pool state. Parameter values are updated through the existing governance mechanism; a substantive change to the activity or pruning semantics requires a superseding CIP.

## Rationale: How does this CIP achieve its goals?

### Relationship to the Shelley stale-stake option

The Shelley design proposed pruning a zero-performance pool only when its stake made several leader elections statistically likely. That test minimizes false positives for small pools, but it requires a probability threshold and depends on stake over the observation window.

This proposal retains a long observation period and gives every operator a deterministic alternative to producing a block: an on-chain registration update. Pool size therefore does not affect the operator's ability to avoid pruning. A functioning but unlucky small pool can renew without waiting for a block, while a pool whose operator has abandoned both infrastructure and cold-key activity eventually leaves the registered set.

### Chain density

When stake is delegated to a registered but unavailable pool, the pool may win a private leader election and fail to produce the corresponding block. After the pool is pruned, its former delegations are no longer active stake. Future leader-election snapshots normalize over the remaining active stake under the existing consensus rules.

Using the epoch-642 snapshot and current mainnet settings, the affected stake at `spoActivity = 73` represents about 0.20% of active stake. A conditional estimate of its expected leader nominations per epoch is:

```text
432,000 slots * 0.05 active-slot coefficient * 0.002 stake share = 43.2
```

If all 41.88 million ADA in the candidate set belongs to unavailable pools, it would therefore account for roughly 43 forfeited leader opportunities per epoch on average.

### Governance participation

SPO voting power is calculated from the pool stake distribution used at ratification. Registered SPOs that do not vote normally default to `No`, subject to the predefined `AlwaysAbstain` and `AlwaysNoConfidence` behavior selected through the pool reward credential.

Pool pruning removes delegations to the pool. Under existing snapshot timing, the pool consequently leaves the stake distribution used for subsequent SPO ratification. Votes already recorded under that pool credential may remain in governance-action history, but they carry no pool stake after the relevant distribution no longer includes the pool.

This effect is secondary to the chain-density goal. Automatic pruning is not a general SPO voting-activity rule, and producing a block is sufficient to keep a non-voting pool registered.

### Initial value of `spoActivity`

Seventy-three epochs is approximately one year on Cardano mainnet. It limits automatic pruning to pools that have shown no qualifying activity across a long operational window and remains substantially longer than ordinary maintenance outages or upgrade delays.

A Koios analysis at epoch 642 evaluated every integer value from 12 through 73 epochs using the latest canonical block or accepted registration update for each registered, non-retiring pool. Four representative values are:

| `spoActivity` | Approximate period | Pools affected | Active stake affected |
| ---: | ---: | ---: | ---: |
| 12 epochs | 60 days | 1,694 | 79.66M ADA |
| 24 epochs | 120 days | 1,625 | 70.36M ADA |
| 36 epochs | 180 days | 1,570 | 59.57M ADA |
| 73 epochs | One year | 1,485 | 41.88M ADA |

At 73 epochs, the candidate population is approximately half of all registered pools but represents only about 0.20% of active stake in the snapshot. This indicates a large long tail of registrations with little stake. Compared with a 12-epoch value, the one-year period reduces affected active stake by approximately 37.78 million ADA while still addressing most of the potentially stale pool registrations. It is therefore a conservative initial value that minimizes disruption to active stake while establishing a finite lifetime for pools that show no activity for a full year.

At activation, every registered pool receives the same one-year expiration period. Pools that produce a block or submit a registration update during that year renew their expiration, but many of the 1,485 snapshot candidates could be pruned at the same boundary if they remain inactive. A uniform deadline gives every operator equal notice and avoids historical reconstruction or an arbitrary staggering rule. The resulting registered-pool count may fall sharply, but that change is not by itself a loss of operational decentralization.  It makes the count better reflect pools showing observable activity, while the affected stake in this snapshot is only about 0.20% of active stake.

Pruning does not automatically redelegate this stake. It removes the stale delegation from future block-production and SPO-voting distributions, while the ADA remains controlled by its owner and undelegated until that owner acts.

The value is intentionally updateable, but it must remain positive. Governance may select another period after operational experience. The new interval applies prospectively as pools renew, leaving already-stored expirations unchanged.

### Storing the expiration epoch

Storing `poolExpiration` performs the interval addition once, when qualifying activity occurs, and records the exact pruning boundary. The epoch transition still scans registered pools, but each inactivity check is a direct comparison and query interfaces can expose the stored deadline without recomputing it.

Prospective parameter changes are necessary to preserve this simple representation. Applying a new interval retroactively would require retaining the last activity epoch or rewriting every registered pool entry at enactment. Operators can adopt an increased interval before an existing deadline by producing a block or submitting a registration update.

### Security and operational considerations

- A registration update proves cold-key control, not that the pool's block-producing node is online. An operator can remain registered while deliberately not producing blocks by periodically re-registering.
- Automatic pruning is not slashing. No pool deposit, rewards, or delegated principal are confiscated.
- Pruning does not move delegated ADA or select a new pool for it. The stake remains spendable but does not participate in staking or earn new pool rewards until its owner redelegates.
- Initializing every registered pool with the same activation-derived expiration can cause many abandoned pools to be pruned at the same boundary.

## Path to Active

### Acceptance Criteria

- [ ] The formal ledger specification defines the parameter, state, activity renewal, pruning, bootstrap, and parameter-update rules in this CIP.
- [ ] Released ledger and node implementations conform to those rules, including rollback and interaction with explicit retirement.
- [ ] Supported node, CLI, and indexing interfaces expose `spoActivity` and `poolExpiration`.
- [ ] Automated tests demonstrate the specified state transitions and characterize epoch-boundary performance when many pools expire together.
- [ ] The required Constitutional Guardrails entry for `spoActivity` is in effect before the parameter can be changed via governance.

### Implementation Plan

- [ ] Add the rules to the formal ledger specification.
- [ ] Implement the new parameter, expiration state, bootstrap, activity updates, and pruning transition.
- [ ] Allocate the target-era parameter key and update serialization and query interfaces.
- [ ] Add conformance and performance tests for the implemented rules.

## References

- [Shelley Delegation and Incentives Design Specification, SL-D1 v1.21](https://github.com/intersectmbo/cardano-ledger/releases/latest/download/shelley-delegation.pdf), especially Section 3.3.4 and Appendix C, "Design Option: Stale Stake".
- [Non-Producing Pool Monitor](https://server-tools.grahamsnumberplus1.com/non_producing_pools_V1.html), a community tool maintained by the owner of the GNP1 pool.

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
