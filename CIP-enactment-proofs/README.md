---
CIP: "?"
Title: Required Governance Enactments
Category: Plutus
Status: Proposed
Authors:
    - keyanm <keyanmaskoot@gmail.com> # Replace the Git username with the author's name.
Implementors: []
Discussions: [] # Add the original PR link when submitted.
Created: 2026-09-28
License: CC-BY-4.0
---

## Abstract

This CIP introduces an optional `required_enactments` transaction-body field.
The ledger checks the supplied governance action IDs and their parents against a
permanent record of enacted actions during phase 1 and exposes these pairs in
Plutus `TxInfo`. An agreed historical snapshot initializes the record with all
prior enactments and their parent relationships.

## Motivation: Why is this CIP necessary?

Plutus scripts cannot directly check whether a governance action has enacted.
Requiring enactment in the transaction body lets a contract verify it and perform
its operation in one transaction, even after later actions in the same category
enact.

For proposals submitted in the transaction, contracts can require that a parent
action has enacted rather than remaining pending.

Contracts can also check an enacted action's recorded parent, and request further
entries to follow its ancestry.

Like required signers, the field declares requirements that the ledger checks and
makes available to scripts.

## Specification

### Scope

The field covers all enactable actions under [CIP-1694](../CIP-1694/README.md):
protocol parameter changes, hard fork initiations, committee updates, motions of
no confidence, new constitutions, and treasury withdrawals. Information actions
do not enact.

### Ledger state

Add the following types to governance state, using a `Map` indexed by action ID
and shared nodes for parent links:

```haskell
data EnactedAction = EnactedAction
  { actionId :: !GovActionId
  , parent   :: !(StrictMaybe EnactedAction)
  }

newtype EnactedActions = EnactedActions
  { byId :: Map GovActionId EnactedAction
  }
```

The parent link records the enacted action's original parent field, as identified
by [`withGovActionParent`][action-parent]. `SJust` references the node identified by
that field. Use `SNothing` for treasury withdrawals, which have no parent field,
and for actions whose original parent field was absent. Do not infer a parent
from a later governance root.

At each epoch transition, add nodes for all actions whose enactment takes effect.
In the reference implementation, these are the entries of `enactedActions`
returned by [`proposalsApplyEnactment`][apply-enactment] and committed by the
[`EPOCH` rule][epoch-enactment]. Do not insert pending ratification results,
expired actions, or actions removed because a competing action enacted.

Every map key must equal its node's `actionId`; reuse the same ID value for both.
A parent link must reference the same node stored under that parent's ID in
`byId`, reusing existing nodes without copying their ancestry. Construct parents
before children, including when both enact at the same epoch boundary. Every
referenced parent must be present in the map, and the parent graph must be acyclic.

Retain nodes when later actions enact, including every action enacted at the same
boundary. Store only IDs and parent links; no other action contents are added.
Include this state in ledger-state serialization and snapshots, and restore it
with the rest of the state on rollback.

Validation uses the state immediately before applying the transaction, after any
epoch transition due for its block.

### State serialization and sharing

Encode this state, including snapshots, as a table sorted in ascending order by
transaction hash bytes and then numerical action index. Each row stores its
action ID once and its parent as a zero-based index into the table, or `nil` for
no parent. Do not encode the map keys separately or recursively encode parent
nodes. Table order is independent of enactment order, so a parent index may
refer to an earlier or later row.

When loading, reject malformed IDs, duplicate or unsorted action IDs, invalid or
out-of-range parent indices, self-references, and cycles. Rebuild one shared node
per row, resolving parents before constructing children and reusing already
constructed nodes. Reconstruct `byId` using the same ID values as the node fields.

Use custom serialization, equality, and deep-evaluation handling that preserves
these invariants and avoids repeatedly traversing shared ancestry. Equality of
`EnactedActions` compares IDs and their immediate parent IDs across the complete
map. Deep evaluation processes each node once through the map or a visited-node
table. Generic recursive instances that traverse the full ancestry separately
for every entry are unsuitable.

### Historical initialization

At activation, the state must contain all governance action IDs enacted previously
on that network and their original parent relationships. Initialize it from an
agreed historical snapshot with a specified cutoff chain point, identified by
slot and block hash.

The network's upgrade configuration must fix that point and a hash of the
snapshot's canonical encoding. Nodes must reject a snapshot that does not match.
The snapshot uses the table described above. Its exact encoding and hash
algorithm must be fixed before activation.

A candidate snapshot can be exported from [db-sync][db-sync-schema], using
`gov_action_proposal.enacted_epoch`, the proposal index, and the transaction hash,
restricted to the cutoff, together with the original parent fields. Independent
ledger replay must verify enactment, completeness, and every parent relationship,
including absence claims. The hash establishes agreement on the table; replay
establishes its correctness.

The migration must also include all enactments between the cutoff and activation,
including their parents and those taking effect at the activation boundary.
Nodes reconstructing state and nodes restoring snapshots must produce the same
IDs and parent relationships, with shared nodes, before validating the first
transaction under the new rules. The snapshot rollout and the mechanism for
collecting these intervening enactments remain activation prerequisites.

### Transaction-body field

Insert `enactment_fields` into the transaction-body map. Key `30` is a placeholder;
`gov_action_id` and `nonempty_set` reuse existing ledger types. The field follows
the [required-signers encoding][required-signers]. The fragment is also available
in [enactment.cddl](./enactment.cddl).

```cddl
enactment_fields = (
  ? 30 : required_enactments
)

required_enactments = nonempty_set<required_enactment>

required_enactment = [
  action : gov_action_id,
  parent : gov_action_id / nil
]

nonempty_set<a0> = #6.258([+ a0]) / [+ a0]

gov_action_id = [
  transaction_id : transaction_id,
  gov_action_index : uint .size 2
]

transaction_id = bytes .size 32
```

Omitting the field makes no enactment requirement. If present, it must contain at
least one action-parent pair, with exactly one entry per action ID. Duplicate
action IDs are always rejected, even when their supplied parents differ; set
uniqueness of complete pairs alone is insufficient. Empty collections, `nil` as
the field or an entry, malformed pairs, and malformed action or parent IDs are
always rejected.

The parent must be the original parent ID, or `nil` to assert that the action has
no parent. This covers treasury withdrawals and actions whose original parent
field was absent. `nil` is an exact absence claim, not a request to skip checking
the parent. The field does not assert that an action is the latest or that another
action has not enacted.

A supplied parent need not have its own entry in the transaction. An additional
entry is needed only to expose that parent's parent to scripts.

### Phase-1 validation

When `is_valid = true`, look up each supplied action ID in `byId`. The node must
exist, and its recorded parent must match the supplied parent exactly: `nil`
matches only `SNothing`, and a supplied parent ID matches only `SJust` of a node
with that `actionId`. Any missing action or parent mismatch causes a phase-1
failure identifying the affected action IDs and whether each failure is a missing
action or a mismatched parent. The check also applies to transactions without
Plutus scripts.

When `is_valid = false`, skip these enactment and parent checks. This follows the
existing [`validateTreasuryValue` check][treasury-check]. In that case, block
inclusion alone does not prove enactment or the supplied parent relationship.
Structural checks, including uniqueness of action IDs, still apply in both
branches.

### Plutus script context

Add the following field to `TxInfo`:

```haskell
txInfoRequiredEnactments :: [(GovernanceActionId, Maybe GovernanceActionId)]
```

Construct this flat list of action-parent pairs solely from the transaction body,
sorted by action ID in ascending order by transaction hash bytes and then
numerical action index, regardless of the order in the body. Omission produces an
empty list. Translate `nil` to `Nothing` and a parent ID to `Just` that ID. Encode
the list using the standard Plutus Data encodings for pairs, `Maybe`, and
`GovernanceActionId`.

Do not consult ledger state to construct the context or recursively expand parent
links. For example, an entry `(child, Just parent)` exposes only that relationship;
exposing the parent's parent requires a separate `(parent, grandparent)` entry,
where `grandparent` is a `Maybe GovernanceActionId`.

### Repeated reads and availability

IDs and their recorded parents remain available after newer actions enact and
can be required repeatedly. Contracts can enforce single use through their own
state. A rollback restores both the map and parent links, removing enactments
that are no longer part of the selected chain.

### Versioning and activation

This ledger-script interface change requires a hard fork and a new Plutus ledger
language version under [CIP-0035](../CIP-0035/README.md).

After activation, changes to the specified encoding or validation rules require a
new CIP that supersedes this one. The replacement CIP must define its protocol
activation and any further ledger language change.

The field is accepted from the activating protocol version onward, after the
historical state has been initialized.

This draft covers top-level transactions only.

## Rationale: How does this CIP achieve its goals?

Retaining enacted IDs and their parent links keeps proofs available after
subsequent enactments and covers treasury withdrawals, which have no stored
proposal root. This requires permanent state beyond the latest roots currently
retained by the ledger. Shared nodes retain ancestry without copying it into
every descendant.

Supplying action-parent pairs in the transaction keeps script inputs fixed.
Ledger state decides whether the requirements are met; it does not change what
the script sees.

### Lookup and storage costs

A balanced [Haskell `Map`][map-complexity] supports lookup in `O(log N)` time,
where `N` is the number of enacted IDs. Each lookup is followed by constant-time
access to the immediate parent and comparison of its fixed-size ID or absence.
Checking `k` supplied pairs takes `O(k log N)` time without traversing ancestry.
Transaction and block size limits bound `k`, but validation costs must be
benchmarked for large histories and transactions filled with pairs, including
unsuccessful lookups and parent mismatches.

The map grows permanently with actual enactments. Submitting a proposal or
requiring an action does not add an entry. Each action stores a 32-byte
transaction hash and an action index, shared between the map key and node field.
Parent links add references and node overhead; they do not duplicate parent IDs
in memory. Snapshot rows use parent indices, but transaction pairs still contain
full parent IDs when present. All full validating nodes bear the storage cost;
the map and shared nodes also increase RAM use and snapshot read/write costs.
There is no pruning rule. Serialization, equality, and deep evaluation must be
benchmarked on long chains to detect repeated traversal of shared ancestry.

The refundable `govActionDeposit` and the approval required for enactment limit
growth. Locking the deposit also carries an opportunity cost, including forgone
staking rewards during the lock. This is an economic barrier to abuse, not a
direct payment for storage or a bound on its lifetime cost. The deposit is an
updatable protocol parameter, and rewards are funded from [reserves and
transaction fees][reward-funding]. This CIP adds no storage fee.

### Compatibility

The new context requires scripts to target the new ledger language version.
Changing a deployed context layout would alter the arguments existing scripts
receive. The policy for combining this field with older scripts remains open.

### Open Questions

- Assign the transaction-body key and activation protocol version.
- Select the Plutus ledger language version and `TxInfo` field position, and
  define handling of transactions that also use older script versions.
- Fix the historical snapshot encoding, hash algorithm, cutoff and distribution
  process, and the mechanism covering enactments through activation.

These choices, community review, and an implementation commitment are pending.

## Path to Active

### Acceptance Criteria

- [ ] Assign the body key, activation version, and Plutus context encoding.
- [ ] Implement the shared enacted nodes and lookup map, state codecs, body
      codecs, enactment and parent checks, and context translation.
- [ ] Publish the historical snapshot and replay verification, fix its hash in
      upgrade configuration, and demonstrate complete coverage of enactments and
      parent relationships through activation.
- [ ] Update the `plutus` repository's interface specification and implementation.
- [ ] Provide node queries for enactment and recorded parents of supplied IDs and
      support in external transaction builders and script libraries.
- [ ] Publish encoding vectors and pass ledger integration tests covering the
      cases below.
- [ ] Benchmark lookup, memory, snapshot size, and snapshot read/write costs at
      large history sizes and maximum transaction and block sizes, including
      equality and deep evaluation on long chains.
- [ ] Implementation present within block producing nodes used by 80%+ of stake.
- [ ] Activate the protocol change on Cardano mainnet.

Required test cases:

- Omitted fields; accepted set encodings; rejection of empty collections, `nil`
  fields or entries, malformed pairs and IDs, and duplicate action IDs with either
  identical or different parents; all-present and partly missing requirements.
- Correct and incorrect parent IDs, including a different enacted action as the
  claimed parent; valid `nil` claims for treasury withdrawals and actions whose
  original parent was absent; rejection of `nil` for actions with a parent and
  rejection of supplied parents for actions with none.
- Both validation branches and unconditional structural checks; transactions
  without Plutus scripts; skipping enactment and parent checks only when
  `is_valid = false`; deterministic context encoding across input orderings using
  the standard pair, `Maybe`, and ID encodings.
- A parent omitted from the transaction's own entries; an additional entry to
  expose its parent; context construction solely from supplied pairs without
  expanding ancestry or consulting ledger state.
- Every enactable action type, including treasury withdrawals; historical and
  repeated reads; all actions enacted at the same boundary remain available,
  including parents and children constructed in dependency order regardless of
  action ID ordering, and usable in the first transaction after that boundary.
- Merely proposed or ratified actions, expired actions, removed competitors,
  information actions and unknown IDs fail membership checks; pending ratification
  and pulser progress do not add IDs.
- Full-history initialization, rejection of a wrong snapshot hash, replay
  detection of omitted or spurious entries and incorrect parent relationships
  including absence claims, and coverage through activation.
- Snapshot tables with parent indices both before and after the child row;
  rejection of duplicate or unsorted IDs, invalid and out-of-range parent indices,
  self-references, and cycles; restoration of shared parent nodes and reuse of ID
  values between map keys and node fields.
- Equivalent results after replay, snapshot restoration, restart, and rollback,
  including removal of enactments from an abandoned branch and restoration of
  the selected chain's parent relationships without dangling links.
- Long ancestry chains during enactment, serialization, loading, equality, and
  deep evaluation, checking that shared ancestry is not repeatedly traversed or
  copied for each descendant.

### Implementation Plan

1. Obtain Plutus and Ledger review and resolve the version and encoding
   assignments and migration choices above.
2. Add the shared enacted nodes and lookup map, parent-aware epoch-transition
   updates, state codecs, equality, deep evaluation, and snapshot migration.
   Generate and independently verify historical enactments and parent links.
3. Add the body field and codecs, enforce uniqueness by action ID, and place the
   enactment and parent checks alongside the current treasury value check.
4. Update the Plutus specification and implementation, node queries,
   transaction builders, and script libraries.
5. Add test vectors, integration tests and benchmarks; verify complete historical
   initialization and snapshot/replay agreement on a test network.
6. Release the node and Plutus changes, then activate through a hard fork enabling
   the selected protocol version and new Plutus ledger language version.

## References

- [CIP-0001: CIP Process](../CIP-0001/README.md).
- [CIP-0035: Plutus Core Evolution](../CIP-0035/README.md).
- [CIP-0084: Cardano Ledger Evolution](../CIP-0084/README.md).
- [CIP-1694: A First Step Towards On-Chain Decentralized Governance](../CIP-1694/README.md).
- Reference ledger source below is pinned to commit
  [`d2e02427567ae650677ebf2e9c17f2a5e69c0dd4`][ledger-baseline].

[ledger-baseline]: https://github.com/IntersectMBO/cardano-ledger/tree/d2e02427567ae650677ebf2e9c17f2a5e69c0dd4
[action-parent]: https://github.com/IntersectMBO/cardano-ledger/blob/d2e02427567ae650677ebf2e9c17f2a5e69c0dd4/eras/conway/impl/src/Cardano/Ledger/Conway/Governance/Procedures.hs#L839-L862
[apply-enactment]: https://github.com/IntersectMBO/cardano-ledger/blob/d2e02427567ae650677ebf2e9c17f2a5e69c0dd4/eras/conway/impl/src/Cardano/Ledger/Conway/Governance/Proposals.hs#L492-L560
[epoch-enactment]: https://github.com/IntersectMBO/cardano-ledger/blob/d2e02427567ae650677ebf2e9c17f2a5e69c0dd4/eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Epoch.hs#L318-L329
[required-signers]: https://github.com/IntersectMBO/cardano-ledger/blob/d2e02427567ae650677ebf2e9c17f2a5e69c0dd4/eras/conway/impl/cddl/data/conway.cddl#L621-L623
[treasury-check]: https://github.com/IntersectMBO/cardano-ledger/blob/d2e02427567ae650677ebf2e9c17f2a5e69c0dd4/eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Ledger.hs#L375-L379
[db-sync-schema]: https://github.com/IntersectMBO/cardano-db-sync/blob/master/doc/schema.md#gov_action_proposal
[map-complexity]: https://hackage-content.haskell.org/package/containers-0.8/docs/Data-Map-Strict.html
[reward-funding]: https://docs.cardano.org/about-cardano/learn/pledging-rewards

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
