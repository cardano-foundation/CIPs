---
CIP: "?"
Title: Required Governance Enactments
Category: Plutus
Status: Proposed
Authors:
    - keyanm <keyanmaskoot@gmail.com>
    - Philip DiSarro <phil@midgardlabs.io>
Implementors: []
Discussions: [] # Add the original PR link when submitted.
Created: 2026-09-28
License: CC-BY-4.0
---

## Abstract

This CIP introduces an optional `required_enactments` transaction-body field.
It maps each governance action ID to a requirement. Every requirement asks the
ledger to verify enactment. A transaction can also require the ID to be the
current root of a named governance purpose or to be outside all four roots.
The ledger checks these claims in phase 1 and exposes them in Plutus `TxInfo`.
Its permanent set of enacted IDs starts empty at activation.

## Motivation: Why is this CIP necessary?

Plutus scripts cannot directly check whether a governance action has enacted.
Requiring enactment in the transaction body lets a contract verify it and perform
its operation in one transaction, even after later actions in the same category
enact.

For proposals submitted in the transaction, contracts can require that a parent
action has enacted rather than remaining pending.

Contracts can also check which of the enacted actions they use are still
current roots. For example, a spending validator can require the current
committee root even when its transaction submits no governance proposal.

Like required signers, the field declares requirements that the ledger checks and
makes available to scripts.

## Specification

### Scope

The field covers all enactable actions under [CIP-1694](../CIP-1694/README.md):
protocol parameter changes, hard fork initiations, committee updates, motions of
no confidence, new constitutions, and treasury withdrawals. Information actions
do not enact.

Conway tracks one optional root for each of four governance purposes. Protocol
parameter changes, hard fork initiations, and new constitutions each have their
own tree. Committee updates and motions of no confidence share the committee
tree. Treasury withdrawals sit outside all four trees. [Ledger purpose definitions][action-purposes]

### Ledger state

Add a `Set GovActionId` to governance state. At each epoch transition under the
new rules, insert the IDs of all actions whose enactment takes effect. In the
reference implementation, these are the keys of `enactedActions` returned by
[`proposalsApplyEnactment`][apply-enactment] and committed by the
[`EPOCH` rule][epoch-enactment]. Do not insert pending ratification results,
expired actions, or actions removed because a competing action enacted.

Retain IDs when later actions enact, including every action enacted at the same
boundary. The baseline stores only IDs in the new set. Include it in ledger-state
serialization and snapshots, and restore it with the rest of the state on rollback.

Validation uses the state immediately before applying the transaction, after any
epoch transition due for its block. Read the four committed proposal roots from
`govStatePrevGovActionIds`. When several actions of one purpose enact at the
same boundary, its root is the final one committed at that boundary. Computing
root status requires no per-ID purpose, root flag, or parent history. [Committed root lookup][committed-roots]

### Initialization

The hard-fork transition initializes the set to empty. From that point, insert
only IDs whose enactment is processed under the new rules. Actions enacted before
activation are not added, and their IDs fail membership checks. No historical
snapshot or retrieval of pre-activation enactments is required.

An action proposed or ratified before activation is included if its enactment is
processed under the new rules. Every requirement checks membership in the set,
so even a still-current root that enacted before activation fails all three
requirements.

### Transaction-body field

The ledger uses Conway's existing `GovActionId` and `GovActionPurpose` types.
Each ID in `required_enactments` has one requirement.

```haskell
data EnactmentRequirement
  = Enacted
  | NonRoot
  | RootOf !GovActionPurpose
  deriving (Eq, Show)

newtype RequiredEnactments = RequiredEnactments
  (Map GovActionId EnactmentRequirement)
```

Expose `RequiredEnactments` as an opaque type. Transaction builders and the
ledger decoder use the same smart constructor, `mkRequiredEnactments`. It
checks the input entries before collecting them into a map and rejects an
empty collection, a repeated action ID, or a second `RootOf` for the same
purpose. Distinct IDs may carry the same `Enacted` or `NonRoot` requirement.

Insert `enactment_fields` into the transaction-body map. Key `30` is a
placeholder. The keys use the existing ledger `gov_action_id` encoding and the
values are unsigned integers. [CDDL fragment](./enactment.cddl)

```cddl
enactment_fields = (
  ? 30 : required_enactments
)

required_enactments = { + gov_action_id => enactment_requirement }

enactment_requirement =
    0  ; Enacted
  / 1  ; NonRoot
  / 2  ; RootOf PParamUpdatePurpose
  / 3  ; RootOf HardForkPurpose
  / 4  ; RootOf CommitteePurpose
  / 5  ; RootOf ConstitutionPurpose

gov_action_id = [
  transaction_id : transaction_id,
  gov_action_index : uint .size 2
]

transaction_id = bytes .size 32
```

Omitting the field makes no enactment requirement. The decoder rejects malformed
IDs, unknown requirement codes, and values of the wrong CBOR type, including
`nil`. These encoding rules and the smart constructor's checks apply regardless
of `is_valid`.

### Phase-1 validation

When `is_valid = true`, every supplied ID must belong to the enacted set. For
an ID that passes membership, apply the check named in its map entry.

| Requirement | Condition |
| --- | --- |
| `Enacted` | Membership suffices, regardless of whether the ID is a root. |
| `NonRoot` | The ID differs from every present root across the four purposes. |
| `RootOf purpose` | The named purpose has a root and its ID equals the supplied ID. |

For example, if committee action B succeeds committee action A, both satisfy
`Enacted`. A satisfies `NonRoot` and B satisfies `RootOf CommitteePurpose`.
An enacted treasury withdrawal satisfies `Enacted` and `NonRoot`.

A missing ID or a failed root claim causes a phase-1 failure. Report missing
IDs and identify failed root claims by ID and requirement. These rules also
apply to transactions without Plutus scripts.

When `is_valid = false`, skip both membership and root checks, following the
ledger's `validateTreasuryValue` check. Inclusion of such a transaction does
not authenticate its claims. [Treasury validation rule][treasury-check]

### Plutus script context

Mirror `EnactmentRequirement` and the four `GovActionPurpose` constructors in
the Plutus API. The baseline field uses the Plutus map and action ID types.

```haskell
newtype RequiredEnactments = RequiredEnactments
  (Map GovernanceActionId EnactmentRequirement)

-- Field of the Plutus TxInfo record
txInfoRequiredEnactments :: RequiredEnactments
```

Translate exactly the entries from the transaction body. Encode the wrapper
directly as a Plutus Data map, using the existing `GovernanceActionId` encoding
for keys and a Plutus Data integer with the corresponding requirement code
(`0`–`5`) for each value. Order entries by ascending transaction hash bytes
and then numerical action index, regardless of their order in the body. Omission
produces an empty map.

A script that needs to know an ID's root status must require `NonRoot` or
`RootOf purpose` for that ID. An `Enacted` entry leaves its root status unspecified.

#### Enriched context — open design question

The enriched alternative would let contracts inspect the original proposal
alongside the requirement the ledger checked. It would use the same
transaction-body map and give the existing `TxInfo` field a richer value type.

```haskell
data EnactedProposal = EnactedProposal
  { checkedRequirement :: EnactmentRequirement
  , originalProposal   :: ProposalProcedure
  }

newtype ResolvedEnactments = ResolvedEnactments
  (Map GovernanceActionId EnactedProposal)

-- Alternative field type in the Plutus TxInfo record
txInfoRequiredEnactments :: ResolvedEnactments
```

For a valid transaction, construct `ResolvedEnactments` by traversing the
checked requirements in baseline key order. For each ID, copy its requirement
and attach its authenticated original proposal. A `RootOf CommitteePurpose`
claim on ID B thus yields `EnactedProposal (RootOf CommitteePurpose) proposalB`
under key B. This preserves the restriction to one root claim per purpose.
Omission produces an empty map.

Encode `ResolvedEnactments` directly as a Plutus Data map. Encode each
`EnactedProposal` as constructor `0` with two fields in declaration order,
the requirement integer followed by the existing Plutus `ProposalProcedure`.
That procedure contains the original deposit, return credential, and governance
action. The existing translation omits the proposal metadata anchor. [Proposal translation][proposal-translation]

The storage and authentication design remains open for reviewer input, including
resolution behavior when `is_valid = false`. Adoption of this extension is not a
prerequisite for activating the baseline. Empty initialization at activation and
the exclusion of pre-activation enactments apply to either design.

### Repeated reads and availability

Recorded IDs can satisfy `Enacted` repeatedly, even after newer actions enact.
If a successor becomes the root before a transaction is included, a
`RootOf` claim on the former root fails in phase 1. The former root now
satisfies `NonRoot`. Contracts can enforce single use through their own state.
A rollback restores the enacted set and roots of the selected chain.

### Versioning and activation

This ledger-script interface change requires a hard fork and a new Plutus ledger
language version under [CIP-0035](../CIP-0035/README.md).

After activation, changes to the specified encoding or validation rules require a
new CIP that supersedes this one. The replacement CIP must define its protocol
activation and any further ledger language change.

The field is accepted from the activating protocol version onward. The hard-fork
transition initializes the enacted set as specified above.

This draft covers top-level transactions only.

## Rationale: How does this CIP achieve its goals?

Retaining enacted IDs keeps proofs available after subsequent enactments and
covers treasury withdrawals, which have no stored proposal root. This requires
permanent state beyond the latest roots currently retained by the ledger.

Starting with an empty set keeps activation independent of historical enactment
data.

The signed map fixes the IDs and requirements a script sees. A root change can
invalidate a claim before inclusion while the script inputs remain fixed.
Keying the map by ID gives each action one requirement. The smart constructor
can reject two claims on the same purpose's root before consulting ledger
state. The enriched context would additionally require authenticated proposal
contents for the requested IDs.

### Lookup and storage costs

A balanced [Haskell `Set`][set-complexity] supports membership checks in
`O(log N)` time, where `N` is the number of enacted IDs. A `RootOf` claim adds
one root lookup and a `NonRoot` claim adds at most four ID comparisons. For a
decoded map with `k` entries, the phase-1 state checks take `O(k log N + k)`
time. Each requirement code occupies one byte in its shortest CBOR encoding.
Transaction and block size limits bound `k`. Benchmark successful and failed
checks with large histories and transactions filled with requirements.

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

### Supplying proposal contents

The existing ledger removes enacted proposal records from active proposal
storage. Their full records are available in the `enactedActions` result of
[`proposalsApplyEnactment`][apply-enactment] at the enactment transition, but the
baseline's permanent ID set cannot reconstruct those contents later.

Reviewers are invited to help choose a practical source of authenticated values
for the enriched context. The following approaches remain open:

| Approach | Benefit | Additional work or cost |
| --- | --- | --- |
| Retain enacted proposal records | Direct lookup and reuse of proposal translation from the requested IDs | Permanent storage of variable-size records |
| Retain a content hash per enacted ID | Fixed-size commitment per ID | Proposal witness encoding, hashing, verification, and transaction data |
| Retain only enacted IDs | Preserves the baseline state representation | Authenticate supplied original transaction bodies against the transaction hash and select proposals by index, accounting for historical encodings and transaction size |

A governance action ID identifies a transaction and a proposal index. Supplying
a proposal record alone does not establish its association with that ID.

Existing proposal translation and Plutus Data maps can be reused. Each design
must make the same authenticated values available to context construction and
execution-budget estimation. The ID-only storage estimates above also do not
cover proposal payloads. A transaction containing a small set of IDs may resolve
to substantially more data, so context construction and resource accounting need
separate review.

### Compatibility

The new context requires scripts to target the new ledger language version.
Changing a deployed context layout would alter the arguments existing scripts
receive. The policy for combining this field with older scripts remains open.

### Open Questions

- Assign the transaction-body key and activation protocol version.
- Select the Plutus ledger language version and `TxInfo` field position, and
  define handling of transactions that also use older script versions.
- Should the desired enriched context be adopted, and which storage and
  authentication approach should supply the original proposal contents?
- If adopted, how should context construction, node queries, and off-chain
  execution-budget estimation obtain the same authenticated proposal data?
- What limits or fees should cover resolved proposal sizes and context
  construction if the enriched context is adopted?
- How should enriched context resolution handle unavailable or mismatched data
  when `is_valid = false`, given that the baseline skips membership and root checks?

These choices, community review, and an implementation commitment are pending.
The enrichment questions are conditional on adopting that extension.

## Path to Active

### Acceptance Criteria

- [ ] Assign the body key, activation version, Plutus ledger language version,
      and `TxInfo` field position.
- [ ] Implement the enacted set and state codecs, the requirements smart
      constructor and body codec, phase-1 membership and root checks, and
      translation to the selected Plutus context.
- [ ] Verify empty-set initialization at activation and accumulation of enactments
      processed under the new rules.
- [ ] Update the `plutus` repository's interface specification and implementation.
- [ ] Support querying membership of supplied IDs and the four committed roots.
      Support constructing requirements in transaction builders and reading the
      selected context in script libraries.
- [ ] Publish encoding vectors and pass ledger integration tests covering the
      cases below.
- [ ] Benchmark lookup, memory, snapshot size, and snapshot read/write costs at
      large history sizes and maximum transaction and block sizes.
- [ ] Implementation present within block producing nodes used by 80%+ of stake.
- [ ] Activate the protocol change on Cardano mainnet.

The required ledger integration tests cover the following cases.

- Omission produces an empty context map. All six codes round-trip through the
  body codec and translate to the specified Plutus Data integers. Context maps
  have identical key order across body input orderings.
- The builder and decoder reject empty maps, duplicate action IDs, and two
  `RootOf` claims for one purpose. The decoder rejects malformed IDs, `nil`,
  unknown codes, and wrong CBOR types. Exercise structural rejection with both
  values of `is_valid`.
- Check every ID in a valid transaction, including transactions without scripts
  and maps with partly missing IDs. An `is_valid = false` transaction skips
  membership and root comparisons even for missing IDs and false root claims.
- Each of the four `RootOf` claims succeeds only for the current root of its
  purpose. Cover an absent root, the root of a different purpose, and multiple
  distinct purposes in one map. Committee updates and no-confidence motions use
  the same root.
- `NonRoot` fails for each current root and succeeds for an enacted treasury
  withdrawal. `Enacted` succeeds in both cases. Repeated `Enacted` reads work
  for every enactable action type.
- Enact two successive parameter changes at one boundary. Both immediately
  satisfy `Enacted`. The first satisfies `NonRoot` and the final change
  satisfies `RootOf PParamUpdatePurpose`. A transaction signed with a former
  root fails its `RootOf` claim after a successor enacts.
- Merely proposed or ratified actions, expired actions, removed competitors,
  information actions and unknown IDs fail membership checks; pending ratification
  and pulser progress do not add IDs.
- Empty-set initialization at activation. All three requirements fail membership
  for pre-activation enactments, including any still-current root. Enactments
  processed under the new rules accumulate, including actions proposed or
  ratified before activation.
- Equivalent results after replay, snapshot restoration, restart, and rollback,
  including restoration of root status and removal of enactments from an
  abandoned branch.

If the enriched context is adopted, additional validation must cover:

- Each entry preserves the submitted requirement and resolves the original
  proposal for that ID. Cover every enactable action type, the constructor index
  and field order of `EnactedProposal`, exact key sets, empty maps on omission,
  and deterministic map ordering.
- Missing, mismatched, or forged proposal data under the selected authentication
  design, including resolution behavior in both validity branches.
- Identical proposal values after replay, snapshot restoration, and restart;
  rollback of the selected chain's enactments and any retained proposal data.
- Large resolved contexts, context-construction costs, and agreement between
  off-chain execution-budget estimates and ledger evaluation.

### Implementation Plan

1. Obtain Plutus and Ledger review and resolve the version and encoding
   assignments above.
2. Add the enacted set, empty-set initialization at the hard fork, epoch-transition
   updates, and state codecs for persistence and snapshots.
3. Add the body map and its smart constructor and codecs. Place membership and
   root checks alongside the current treasury value check.
4. Update the Plutus specification and implementation, node queries,
   transaction builders, and script libraries for the chosen context. If the
   enriched context is adopted, implement proposal authentication and resolution.
5. Add test vectors, integration tests and benchmarks; verify empty initialization,
   subsequent enactment tracking, and snapshot/replay agreement on a test network.
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
[action-purposes]: https://github.com/IntersectMBO/cardano-ledger/blob/d2e02427567ae650677ebf2e9c17f2a5e69c0dd4/eras/conway/impl/src/Cardano/Ledger/Conway/Governance/Procedures.hs#L663-L694
[committed-roots]: https://github.com/IntersectMBO/cardano-ledger/blob/d2e02427567ae650677ebf2e9c17f2a5e69c0dd4/eras/conway/impl/src/Cardano/Ledger/Conway/Governance.hs#L285-L286
[treasury-check]: https://github.com/IntersectMBO/cardano-ledger/blob/d2e02427567ae650677ebf2e9c17f2a5e69c0dd4/eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Ledger.hs#L375-L379
[proposal-translation]: https://github.com/IntersectMBO/cardano-ledger/blob/d2e02427567ae650677ebf2e9c17f2a5e69c0dd4/eras/conway/impl/src/Cardano/Ledger/Conway/TxInfo.hs#L732-L742
[set-complexity]: https://hackage-content.haskell.org/package/containers-0.8/docs/Data-Set.html
[reward-funding]: https://docs.cardano.org/about-cardano/learn/pledging-rewards

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
