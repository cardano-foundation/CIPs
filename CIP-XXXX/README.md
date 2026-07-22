---
CIP: XXXX
Title: Support for On-Disk Ledger State through Diffs
Category: Ledger, Indexers
Authors:
  - kostas Dermentzis <kostas.dermentzis@iohk.io>
Implementors: N/A
Status: Proposed
Discussions:
  - https://drive.google.com/file/d/1l0g2a3nnAA-Zo58TsHD2gzcsyaLOcflF/view
Created: 2025-11-10
License: CC-BY-4.0
---

## Abstract

We propose extending the ledger code with Diffs to improve modularity and support projects such as DBSync. Indexers like DBSync want to maintain a fully indexable ledger state on disk. However this becomes difficult to achieve, due to the complexity of the ledger rules. Because the ledger code is pure and side-effect-free, indexers cannot directly observe incremental state changes. Diffs provide an explicit representation of those effects.

## Motivation: why is this CIP necessary?

### Main motivation

DBSync currently relies on the main ledger API:

```haskell
applySignal :: State -> Signal -> (State, Events)
```

DBSync then uses the results in the following way:
```haskell
updateDB :: State -> Block -> Events -> DBAction ()
```

- **Signal** is usually a block or a tx, or could be a more fine-grained part of the tx.
- **Events** are metadata derived during intermediate stages of applying a signal. They are not usually part of the final State.

While this model has worked for years, it has one main limitation: **incomplete change tracking**. Events are generally ad hoc and do not provide a complete record of state changes. This makes it difficult to maintain live data in the database, as opposed to data only captured at epoch snapshots. One of the most frequent requests we get as DBSync maintainers is to properly maintain live data.


## Specification

A key observation is that `applySignal` both identifies which parts of the state need to change and applies those changes. We can separate these concerns:
```haskell
findDiffs  :: State -> Signal -> [Diff]
applyDiffs :: State -> [Diff] -> State
```
Diffs describe every change caused by a Signal, down to specific state components.
With Diffs, DBSync could maintain accurate, real-time ("live") views of ledger structures.

### Structure of the Diffs

A Diff is a formalized, serializable description of all state changes that occur when applying a Signal to a given State. It should be annotated by the part of the state that changes and by the specific delta.
Unlike existing ledger events, Diffs don't need to be annotated by the ledger rule where they came from. They can be represented as a large sum type of all possible changes, where each part corresponds to one leaf of the ledger state tree structure.

```haskell
data Diff era =
    -- NewEpochState
    DNesEL DeltaEpochNo
    --   ...
    --  EpochState
    --   ChainAccountState
  | DCasTreasury !DeltaCoin
    --    ...
    --   LedgerState
    --    UTxOState
  | DUTxO (DeltaUTxO era)
  | DUtxosDeposited DeltaCoin

    --    CertState
    --     VState
  | DCommitteeState (DeltaMap DrepCredential DRepState)
    --      ...
    --     PState
  | DPsStakePools (DeltaMap KeyHashStake StakePoolState)
    --      ...
    --     DState
    --      Accounts
  | DAccounts (DeltaMap StakeCreds (ConwayAccountState era))

data DeltaUTxO era =
    DeleteUTxO (UTxO era)
  | InsertUTxO (UTxO era)

data DeltaMap k v =
    DeleteMap (Map k v)
  | InsertMap (Map k v)
  | UpdateMap (Map k (v, v)) -- old and new value

```

### Reversibility

Indexers need to follow the tip of the chain, which is not finalised since rollbacks are possible. For that reason, Diffs should be reversible without additional context.

```haskell
reverseDiff :: Diff -> Diff
```

A Diff is reversible if all information necessary to reconstruct the previous state is retained within it. For example this Diff

```haskell
UpdateMap k v
```

is not reversible, since the old value is lost. However these are

```haskell
reverseDiff (UpdateMap (Map.singleton k (v, v'))) =
  (UpdateMap (Map.singleton k (v', v)))

reverseDiff (DeleteMap (Map.singleton k v)) =
  (InsertMap (Map.singleton k v))
```

### Order of the Diffs

The list of Diffs produced by `findDiffs` must be ordered according to the logical order in which changes occur during signal application, especially Diffs that change the same part of the ledger. Implementations may reorder Diffs across different state components for efficiency, but such reordering must be stable, the relative order of Diffs affecting the same component must be preserved.

### Composability

It should be possible to group and combine Diffs that affect the same structure. This allows to collapse intermediate updates into a single semantic change and reduce the number of database updates. Example:

```haskell
compose :: [Diff] -> [Diff]
compose
  [ DCasTreasury (DeltaCoin v1)
  , DUTxO (InsertUTxO u1)
  , DCasTreasury (DeltaCoin v2)
  , DUTxO (InsertUTxO u2)
  ] =
  [ DCasTreasury (DeltaCoin (v1 + v2))
  , DUTxO (InsertUTxO (u1 UTxO.union u2)) -- pseudocode
  ]
```

### Triggers

A Trigger is a Diff, annotated by the Signal id that generated it. Triggers differ from Diffs in that they are not explicitly part of or easily derived by a block, tx or era transition. This separation allows to, as an initial step, define only a minimal set of Diffs, as long as it's easy to derive the full set, given the Signal.

```haskell
type Trigger = (SignalId, DiffTrigger)
findTriggers :: State -> Signal -> (State, [Trigger])
createDiffs :: [Trigger] -> Signal -> [Diff]
```

Here
- `Signal` can be {Block, Tx, Slot, Epoch Boundary}
- `SignalId` can be a more fine-grained signal, as it appears in the STS ledger rules. Some examples are tx hash, (tx hash,certificate index), (tx hash,vote index), epoch boundary.
- `DiffTrigger` can be a synonym for Diff, or a "smaller" type if possible.

For example, given a tx, its `DUTxO` Diff, or a new vote addition is quite straight forward to derive. However a tx may also cause a pool to lose its pledge, or a vote may cause a previous vote to be invalidated. These events can be captured by Triggers.

Triggers
- reduce the complexity and surface area required in the core ledger libraries (see Path to Active below)
- can be used to derive full Diffs in a separate package (e.g. ledger-indexer-api).
- provide a compact representation suitable for storage or transmission (see mini-protocol extension below)

### Extending the mini-protocol (optional)

DBSync still needs to replay the ledger and create the Diffs, but the node could provide them through an extension of its protocol. Currently the chainsync protocol only provides new blocks, or rollbacks to previous points. This extension could provide Diffs, or Triggers, next to the blocks. It would still be the responsibility of DBSync to store the Diffs and reverse them in case of a rollback. It would provide big performance improvements to indexers.

This has been discussed before and there are some challenges, like finding a format for the Diffs, having their compatibility broken frequently etc. Specification of such a protocol extension is out of scope for this CIP but is a natural follow-up once Diffs/Triggers are standardized.

### Serialization

Diffs must be serializable and deserializable in a way that preserves determinism and era-awareness. Their serialization could follow the same approach used for UTxO-HD Outputs, leveraging the Mempack encoding framework.

### Future Diffs

The ledger code splits expensive computation, like reward calculation and drep distribution, into incremental steps, called pulsing computations. It makes sure to complete the computation when the data are necessary, usually before an epoch boundary. Pulsing computation can be seen as future Diffs, meaning Diffs that will have a future impact. It could be useful to create Diffs, that include the Pulsers and the time (slot or epoch) where they will have an effect.

### Prediction Diffs

In addition, especially related to Governance, it would be useful to have vote predictions about running governance actions. These could be reports about how close an action is to ratification or what is still failing.

### Relation to Leios

Diffs can be a first step towards parallel and modular validation of transactions, as required by architectures such as Leios. A structured ledger API lets specialized roles (e.g. block producers, relays, indexers) consume only the parts they need.

## Rationale: how does this CIP achieve its goals?

This CIP achieves making the ledger code more modular with Diffs. While the code still remains pure, without side effects, it makes these side effects explicit, complete and defines them properly.

### Diffs as Testing/Auditing Tool

Diffs provide an alternative way to validate ledger correctness: applying the sequence of Diffs from an initial state to a given point must yield the same state as applying the ledger rules directly.

In a way, Diffs resemble a double-entry bookeeping system, they make it straightforward to:
- verify that every Signal is balance-preserving across relevant accounts (e.g. reserves, treasury, rewards, UTxO),
- track the complete history of specific accounts (e.g. a stake key, the treasury, reserves).

## Path to Active

Steps to be taken are
- Define `Triggers` in existing ledger packages
- Define `Diff` types and `createDiffs` in a separate package (e.g. `ledger-indexer-api`) that does not need to be a node dependency.
- As a first step, support only the latest era (Conway currently).
- Ιntegrate with an indexer (e.g. DBSync) for evaluation.

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).

