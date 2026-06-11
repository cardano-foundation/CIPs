---
CIP: 173
Title: Net Change Limit Parameter
Category: Ledger
Status: Proposed
Authors:
  - Ryan Wiley <rian222@gmail.com>
Implementors: []
Discussions:
  - Original PR: https://github.com/cardano-foundation/CIPs/pull/1129
Created: 2026-01-08
License: CC-BY-4.0
---

## Abstract

The Cardano Constitution requires treasury withdrawals to respect a net change limit (NCL). Today, NCL values are often expressed through on-chain Info Actions, which are not ledger-enforced and can produce ambiguity when multiple competing references exist.

This CIP defines a single canonical on-chain mechanism:

- the ledger maintains canonical rolling treasury state for a governance-configurable epoch window, and
- the ledger directly enforces the NCL when Treasury Withdrawal actions are considered for ratification.

If the ledger check fails, the Treasury Withdrawal action is not ratified and no treasury funds move. The governance-updatable parameters in scope are:

- `netChangeLimit`: integer percentage (`>= 0`), and
- `netChangePeriod`: positive integer number of epochs.

## Motivation: why is this CIP necessary?

The current NCL process relies on repeated social coordination around Info Actions. These references are not directly enforced by ledger rules and can conflict in period assumptions, approval timing, and interpretation.

This creates two problems:

- **Ambiguous source of truth.** Different actors can interpret different NCL references as authoritative.
- **Operational overhead.** Arithmetic admissibility checks remain largely procedural rather than being deterministically derived from the ledger state.

This CIP resolves those problems by using:

- a governance-configurable rolling window,
- ledger state for window revenue and withdrawals, and
- direct ledger enforcement of the NCL during Treasury Withdrawal ratification.

This preserves deterministic on-chain behavior, provides a single source of truth for the NCL, and mitigates simultaneous conflicting withdrawals by making ratification depend on canonical ledger state.

## Specification

### Protocol parameters

This CIP defines or updates two governance parameters:

- `netChangeLimit`: integer percentage, `>= 0`.
  - `0` is explicitly valid and means no Treasury Withdrawal action can pass the NCL check.
  - Values greater than `100` are valid and would simply allow deficit spending.
- `netChangePeriod`: positive integer number of epochs.

No upper bound is imposed by this CIP for either parameter. Bounds may optionally be imposed by Constitutional Guardrails.

### State semantics

The ledger MUST maintain a logical ring buffer with:

- exactly `netChangePeriod` entries,
- one pointer identifying the entry to be overwritten at the next epoch transition,
- each entry containing a tuple `(revenue, withdrawn)` for that entry's epoch.

Semantically, the window is the current epoch plus the previous `netChangePeriod - 1` completed epochs.
Immediately before an epoch transition, the pointed entry represents the oldest retained epoch in that window.

All monetary values are integer lovelace.

`revenue` for an entry is the cumulative treasury revenue accounted for that entry's epoch. Revenue MUST be non-negative and includes treasury inflows such as emissions, fees, donations, and returned proposal deposits.

`withdrawn` for an entry is the cumulative treasury amount withdrawn for that entry's epoch.

When a returned proposal deposit is credited to the treasury while Treasury Withdrawal actions are being processed, that amount MUST be counted immediately as revenue for the current epoch before checking any later Treasury Withdrawal action in the same processing sequence.

### Ratification enforcement

The normative enforcement path for this CIP is direct ledger checking during Treasury Withdrawal ratification.

At ratification-time evaluation of a Treasury Withdrawal action with amount `w`, the ledger MUST compute:

1. `windowRevenue = sum(entry.revenue for all entries)`
2. `windowWithdrawn = sum(entry.withdrawn for all entries)`
3. `cap = floor(netChangeLimit * windowRevenue / 100)`

The Treasury Withdrawal action is ratifiable iff:

`windowWithdrawn + w <= cap`

When the check fails:

- the Treasury Withdrawal action is marked as not ratified, and
- no treasury funds move for that action.

When the check succeeds:

- the Treasury Withdrawal action may be ratified according to the normal governance ratification rules, and
- the withdrawn amount contributes to the current epoch's `withdrawn` accounting before any later Treasury Withdrawal action is checked.

When multiple Treasury Withdrawal actions are processed in the same ratification step, the ledger MUST process them one at a time in the existing ledger order. This CIP does not change existing ledger behavior for insufficient treasury balance; existing first-in, first-out handling continues to apply.

### Parameter changes

Changes to `netChangePeriod` follow normal protocol parameter update behavior.

When `netChangePeriod` is shortened, the ledger MUST remove the oldest entries until the ring contains exactly `netChangePeriod` entries.

When `netChangePeriod` is lengthened, the ledger MUST add empty `(0, 0)` entries as the oldest entries until the ring contains exactly `netChangePeriod` entries.

### Epoch rollover

At each epoch transition, the ledger MUST:

1. finish accounting for the ending epoch's treasury revenue and withdrawals,
2. overwrite the pointed entry with `(revenue(E), withdrawn(E))` for epoch `E`,
3. advance the pointer to the next overwrite entry in the ring; if it is at the last entry, wrap to the first entry.

This ordering ensures NCL checks always evaluate the current canonical rolling window before any entry replacement.
Pointer advancement and overwrite MUST occur every epoch, including epochs with no treasury withdrawal activity.

### Bootstrap initialization

When this CIP's mechanism is first activated, the ledger MUST initialize the ring as follows:

- `netChangePeriod` is initialized to `73`,
- all 73 entries are set to `(bootstrapRevenueSeed, 0)`,
- `bootstrapRevenueSeed = 4,000,000,000,000` lovelace,
- the pointer is set to the entry that will be overwritten at the first epoch transition after activation.

After activation, normal epoch rollover semantics apply, and seeded entries are progressively overwritten by real epoch data. Later changes to `netChangePeriod` follow the resizing behavior defined above.

## Rationale: how does this CIP achieve its goals?

- **Direct ledger enforcement.** The ledger provides deterministic state and enforces NCL during Treasury Withdrawal ratification.
- **Single canonical calculation.** The ledger computes window sums, the cap, and ratification admissibility from canonical state.
- **Deterministic rollover and accounting.** Pointer advancement and entry overwrite semantics fully define rolling behavior across epochs.
- **Configurable period.** `netChangePeriod` allows governance to adjust the lookback window while preserving deterministic resizing behavior.
- **Bootstrap continuity.** Fixed seed initialization avoids blocking withdrawals during initial activation while converging automatically to measured data.

## Path to Active

### Acceptance Criteria

- **CIP process acceptance** by CIP Editors with complete and unambiguous state and ratification semantics.
- **Ledger implementation available** in a released node/ledger version that:
  - stores the normative ring state and pointer,
  - applies deterministic epoch rollover behavior, and
  - applies direct NCL checks during Treasury Withdrawal ratification.
- **Parameter update implementation available** in a released node/ledger version for both `netChangeLimit` and `netChangePeriod`, including deterministic `netChangePeriod` resizing.
- **Ratification enforcement implementation available** in a released node/ledger version such that failed NCL checks mark the Treasury Withdrawal action as not ratified and prevent treasury movement.
- **Conformance tests available** covering at least:
  - under-cap, exact-cap, and over-cap withdrawals,
  - `netChangeLimit = 0`,
  - `netChangePeriod` positive-integer validation,
  - NCL evaluation against the current canonical rolling window,
  - epoch-boundary ordering (account, write, then pointer advance),
  - epoch rollover pointer advancement in zero-activity epochs,
  - entry overwrite behavior after full `netChangePeriod` rotation,
  - shortening `netChangePeriod` drops oldest entries,
  - lengthening `netChangePeriod` adds oldest `(0, 0)` entries,
  - sequential processing of multiple Treasury Withdrawal actions in existing ledger order,
  - immediately counting returned proposal deposits as revenue before subsequent same-epoch withdrawal checks,
  - bootstrap initialization (`73 x (bootstrapRevenueSeed, 0)`) and progressive overwrite with measured data,
  - no treasury movement and not-ratified status on failed NCL checks.
- **Governance activation complete** through required governance / protocol rollout and initial on-chain parameter settings.

### Implementation Plan

- **Specification finalization**
  - Incorporate review feedback from governance bodies, implementors, and CIP Editors.
  - Lock terminology against existing governance and ledger documentation.
- **Ledger and node work**
  - Add/confirm protocol parameters `netChangeLimit` and `netChangePeriod`.
  - Implement normative ring state, revenue measurement, rollover, resizing, and bootstrap initialization behavior.
  - Implement direct NCL admissibility logic during Treasury Withdrawal ratification.
  - Ensure failed NCL checks mark the action as not ratified and block treasury movement.
- **Testing and validation**
  - Add deterministic conformance tests for window sums, arithmetic, rollover semantics, resizing, same-epoch sequential processing, and bootstrap behavior.
  - Validate no treasury movement occurs when NCL checks fail.
- **Governance rollout**
  - Submit and ratify required governance actions to activate implementation.
  - Set initial parameter values on-chain.

## References

- [Cardano Blockchain Ecosystem Constitution](https://docs.intersectmbo.org/archive/cardano-governance-archive/cardano-constitution/read-the-cardano-constitution), Article IV (Cardano Blockchain Ecosystem Budget), especially Section 3 (net change limit and withdrawal constraints).
- [CIP-1694: A First Step Towards On-Chain Decentralized Governance](../CIP-1694/README.md)

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
