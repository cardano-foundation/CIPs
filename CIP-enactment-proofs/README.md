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
The ledger checks the supplied governance action IDs against a permanent set of
enacted actions during phase 1 and exposes them in Plutus `TxInfo`. An agreed
historical snapshot initializes the set with all prior enactments.

## Motivation: Why is this CIP necessary?

Plutus scripts cannot directly check whether a governance action has enacted.
Requiring enactment in the transaction body lets a contract verify it and perform
its operation in one transaction, even after later actions in the same category
enact.

For proposals submitted in the transaction, contracts can require that a parent
action has enacted rather than remaining pending.

Like required signers, the field declares requirements that the ledger checks and
makes available to scripts.

## Specification

### Scope

The field covers all enactable actions under [CIP-1694](../CIP-1694/README.md):
protocol parameter changes, hard fork initiations, committee updates, motions of
no confidence, new constitutions, and treasury withdrawals. Information actions
do not enact.

### Ledger state

Add a `Set GovActionId` to governance state. At each epoch transition, insert the
IDs of all actions whose enactment takes effect. In the reference implementation,
these are the keys of `enactedActions` returned by
[`proposalsApplyEnactment`][apply-enactment] and committed by the
[`EPOCH` rule][epoch-enactment]. Do not insert pending ratification results,
expired actions, or actions removed because a competing action enacted.

Retain IDs when later actions enact, including every action enacted at the same
boundary. Store only IDs; action contents and parent links are not added. Include
the set in ledger-state serialization and snapshots, and restore it with the rest
of the state on rollback.

Validation uses the state immediately before applying the transaction, after any
epoch transition due for its block.

### Historical initialization

At activation, the set must contain all governance action IDs enacted previously
on that network. Initialize it from an agreed historical snapshot with a specified
cutoff chain point, identified by slot and block hash.

The network's upgrade configuration must fix that point and a hash of the
snapshot's canonical encoding. Nodes must reject a snapshot that does not match.
The snapshot contains each enacted ID once, sorted in ascending order by
transaction hash bytes and then numerical action index. Its exact encoding and
hash algorithm must be fixed before activation.

A candidate snapshot can be exported from [db-sync][db-sync-schema], using
`gov_action_proposal.enacted_epoch`, the proposal index, and the transaction hash,
restricted to the cutoff. Independent ledger replay must verify both its contents
and completeness. The hash establishes agreement on the list; replay establishes
its correctness.

The migration must also include all enactments between the cutoff and activation,
including those taking effect at the activation boundary. Nodes reconstructing
state and nodes restoring snapshots must produce the same set before validating
the first transaction under the new rules. The snapshot rollout and the mechanism
for collecting these intervening enactments remain activation prerequisites.

### Transaction-body field

Insert `enactment_fields` into the transaction-body map. Key `30` is a placeholder;
`gov_action_id` and `nonempty_set` reuse existing ledger types. The field follows
the [required-signers encoding][required-signers]. The fragment is also available
in [enactment.cddl](./enactment.cddl).

```cddl
enactment_fields = (
  ? 30 : required_enactments
)

required_enactments = nonempty_set<gov_action_id>

nonempty_set<a0> = #6.258([+ a0]) / [+ a0]

gov_action_id = [
  transaction_id : transaction_id,
  gov_action_index : uint .size 2
]

transaction_id = bytes .size 32
```

Omitting the field makes no enactment requirement. If present, it must contain at
least one distinct action ID. Empty collections, duplicate IDs, `nil`, and
malformed IDs are always rejected. The field does not assert that an action is
the latest or that another action has not enacted.

### Phase-1 validation

When `is_valid = true`, every supplied ID must belong to the enacted set. Any
missing ID causes a phase-1 failure reporting the missing IDs. The check also
applies to transactions without Plutus scripts.

When `is_valid = false`, skip these membership lookups. This follows the existing
[`validateTreasuryValue` check][treasury-check]. In that case, block inclusion alone
does not prove enactment.

### Plutus script context

Add the following field to `TxInfo`:

```haskell
txInfoRequiredEnactments :: [GovernanceActionId]
```

Construct this list solely from the transaction body, sorted in ascending order
by transaction hash bytes and then numerical action index, regardless of the order
in the body. Omission produces an empty list. Encode it as a Plutus Data list
using the existing `GovernanceActionId` encoding for each entry.

### Repeated reads and availability

IDs remain available after newer actions enact and can be required repeatedly.
Contracts can enforce single use through their own state. A rollback removes
enactments that are no longer part of the selected chain.

### Versioning and activation

This ledger-script interface change requires a hard fork and a new Plutus ledger
language version under [CIP-0035](../CIP-0035/README.md).

After activation, changes to the specified encoding or validation rules require a
new CIP that supersedes this one. The replacement CIP must define its protocol
activation and any further ledger language change.

The field is accepted from the activating protocol version onward, after the
historical set has been initialized.

This draft covers top-level transactions only.

## Rationale: How does this CIP achieve its goals?

Retaining enacted IDs keeps proofs available after subsequent enactments and
covers treasury withdrawals, which have no stored proposal root. This requires
permanent state beyond the latest roots currently retained by the ledger.

Supplying IDs in the transaction keeps script inputs fixed. Ledger state decides
whether the requirements are met; it does not change what the script sees.

### Lookup and storage costs

A balanced [Haskell `Set`][set-complexity] supports membership checks in
`O(log N)` time, where `N` is the number of enacted IDs. Checking `k` supplied IDs
takes `O(k log N)` time without scanning history. Transaction and block size
limits bound `k`, but validation costs must be benchmarked for large histories
and transactions filled with IDs, including unsuccessful lookups.

The set grows permanently with actual enactments. Submitting a proposal or
requiring an ID does not add an entry. Each entry stores a 32-byte transaction
hash and an action index, plus encoding and data-structure overhead. All full
validating nodes bear the storage cost; an in-memory set also increases RAM use
and snapshot read/write costs. There is no pruning rule.

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
- [ ] Implement the enacted set, state codecs, body codecs, phase-1 checks, and
      context translation.
- [ ] Publish the historical snapshot and replay verification, fix its hash in
      upgrade configuration, and demonstrate complete coverage through activation.
- [ ] Update the `plutus` repository's interface specification and implementation.
- [ ] Provide node queries for membership of supplied IDs and support in external
      transaction builders and script libraries.
- [ ] Publish encoding vectors and pass ledger integration tests covering the
      cases below.
- [ ] Benchmark lookup, memory, snapshot size, and snapshot read/write costs at
      large history sizes and maximum transaction and block sizes.
- [ ] Implementation present within block producing nodes used by 80%+ of stake.
- [ ] Activate the protocol change on Cardano mainnet.

Required test cases:

- Omitted fields; accepted set encodings; rejection of empty collections, `nil`,
  duplicate and malformed IDs; all-present and partly missing requirements.
- Both validation branches and unconditional structural checks; transactions
  without Plutus scripts; deterministic context encoding across input orderings.
- Every enactable action type, including treasury withdrawals; historical and
  repeated reads; all actions enacted at the same boundary remain available.
- Merely proposed or ratified actions, expired actions, removed competitors,
  information actions and unknown IDs fail membership checks; pending ratification
  and pulser progress do not add IDs.
- Full-history initialization, rejection of a wrong snapshot hash, replay
  detection of omitted or spurious entries, and coverage through activation.
- Equivalent results after replay, snapshot restoration, restart, and rollback,
  including removal of enactments from an abandoned branch.

### Implementation Plan

1. Obtain Plutus and Ledger review and resolve the version and encoding
   assignments and migration choices above.
2. Add the enacted set and its epoch-transition updates, state codecs and
   snapshot migration. Generate and independently verify the historical set.
3. Add the body field and codecs, and place the membership check alongside the
   current treasury value check.
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
[apply-enactment]: https://github.com/IntersectMBO/cardano-ledger/blob/d2e02427567ae650677ebf2e9c17f2a5e69c0dd4/eras/conway/impl/src/Cardano/Ledger/Conway/Governance/Proposals.hs#L492-L560
[epoch-enactment]: https://github.com/IntersectMBO/cardano-ledger/blob/d2e02427567ae650677ebf2e9c17f2a5e69c0dd4/eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Epoch.hs#L318-L329
[required-signers]: https://github.com/IntersectMBO/cardano-ledger/blob/d2e02427567ae650677ebf2e9c17f2a5e69c0dd4/eras/conway/impl/cddl/data/conway.cddl#L621-L623
[treasury-check]: https://github.com/IntersectMBO/cardano-ledger/blob/d2e02427567ae650677ebf2e9c17f2a5e69c0dd4/eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Ledger.hs#L375-L379
[db-sync-schema]: https://github.com/IntersectMBO/cardano-db-sync/blob/master/doc/schema.md#gov_action_proposal
[set-complexity]: https://hackage-content.haskell.org/package/containers-0.8/docs/Data-Set.html
[reward-funding]: https://docs.cardano.org/about-cardano/learn/pledging-rewards

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
