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

This CIP defines a single canonical on-chain mechanism with a clear split of responsibilities:

- the ledger maintains canonical rolling treasury state for a fixed 73-epoch window
- the guardrail script performs the admissibility check for Treasury Withdrawals at enactment time.

If the guardrail check fails, the Treasury Withdrawal is not enacted and no treasury funds move. The only governance-updatable parameter in scope is:

- `netChangeLimit`: integer percentage (`>= 0`).

## Motivation: why is this CIP necessary?

The current NCL process relies on repeated social coordination around Info Actions. These references are not directly enforced by ledger rules and can conflict in period assumptions, approval timing, and interpretation.

This creates two problems:

- **Ambiguous source of truth.** Different actors can interpret different NCL references as authoritative.
- **Operational overhead.** Arithmetic admissibility checks remain largely procedural rather than being deterministically derived from canonical state.

This CIP resolves those problems by using:

- a fixed 73-epoch rolling window (no mutable period parameter),
- canonical ledger state for window revenue and withdrawals, and
- a guardrail-script enactment check against that state.

This preserves deterministic on-chain behavior while keeping policy enforcement in the guardrail script path defined by governance.

## Specification

### Protocol parameter

This CIP defines or updates one governance parameter:

- `netChangeLimit`: integer percentage, `>= 0`.
  - `0` is explicitly valid and means no treasury withdrawals can be enacted.
  - Values greater than `100` are valid and would simply allow deficit spending.

No upper or lower bounds are imposed by this CIP for `netChangeLimit`. Bounds may optionally be imposed through constitutional guardrails.

### State semantics

The ledger MUST maintain a logical fixed-size ring buffer with:

- exactly `73` slots,
- one pointer identifying the slot to be overwritten at the next epoch transition,
- each slot containing a tuple `(revenue, withdrawn)` for that slot's epoch.

Semantically, the window is the current epoch plus the previous 72 completed epochs.
Immediately before an epoch transition, the pointed slot represents the oldest retained epoch in that 73-epoch window.

All monetary values are integer lovelace.

`withdrawn` for a slot is the cumulative treasury amount enacted for that slot's epoch.

Let `treasuryEnd(E)` be the treasury balance at the end of epoch `E`, measured before accounting for Treasury Withdrawals enacted in epoch `E`.

Define slot revenue for epoch `E` as:

`revenue(E) = treasuryEnd(E) - treasuryEnd(E - 1)`

This CIP allows signed intermediate revenue values in state. As a safeguard, negative aggregate revenue is clamped as described below when computing the cap.

### Admissibility and guardrail enforcement

The normative enforcement path for this CIP is the guardrail script check at Treasury Withdrawal enactment.

At an epoch transition, the check MUST use the pre-write snapshot of all 73 slots, including the pointed overwrite slot before it is replaced.

At enactment-time evaluation of a Treasury Withdrawal with amount `w`:

1. `windowRevenue = sum(slot.revenue for all 73 slots)`
2. `windowWithdrawn = sum(slot.withdrawn for all 73 slots)`
3. `effectiveRevenue = max(windowRevenue, 0)`
4. `cap = floor(netChangeLimit * effectiveRevenue / 100)`

The withdrawal is admissible iff:

`windowWithdrawn + w <= cap`

When the check fails:

- the withdrawal action is not enacted, and
- no treasury funds move for that action.

When the check succeeds:

- the action is enacted, and
- the enacted amount contributes to `withdrawn(E)` for the ending epoch `E`, which is written during rollover.

### Epoch rollover

At each epoch transition, the ledger MUST:

1. perform Treasury Withdrawal guardrail checks for boundary enactment against the pre-write 73-slot snapshot,
2. compute `revenue(E) = treasuryEnd(E) - treasuryEnd(E - 1)` for ending epoch `E`,
3. overwrite the pointed slot with `(revenue(E), withdrawn(E))` for epoch `E`,
4. advance the pointer by one position modulo 73 to identify the next overwrite slot.

This ordering ensures guardrail checks always evaluate a full 73-epoch historical window before any slot replacement.
Pointer advancement and overwrite MUST occur every epoch, including epochs with no treasury withdrawal activity.

### Bootstrap initialization

When this CIP's mechanism is first activated, the ledger MUST initialize the ring as follows:

- all 73 slots are set to `(bootstrapRevenueSeed, 0)`,
- `bootstrapRevenueSeed = 4,000,000,000,000` lovelace,
- the pointer is set to the slot that will be overwritten at the first epoch transition after activation.

After activation, normal epoch rollover semantics apply, and seeded slots are progressively overwritten by real epoch data.

## Rationale: how does this CIP achieve its goals?

- **Canonical on-chain state with script policy enforcement.** The ledger provides deterministic state and the guardrail script enforces at enactment.
- **Deterministic rollover and accounting.** Pointer advancement and slot overwrite semantics fully define rolling behavior across epochs.
- **Bootstrap continuity.** Fixed seed initialization avoids blocking withdrawals during initial activation while converging automatically to measured data.

## Path to Active

### Acceptance Criteria

- **CIP process acceptance** by CIP Editors with complete and unambiguous state and guardrail semantics.
- **Ledger implementation available** in a released node/ledger version that:
  - stores the normative 73-slot ring state and pointer,
  - applies deterministic epoch rollover behavior, and
  - provides the required state for guardrail-script admissibility checks at enactment.
- **Guardrail enforcement implementation available** in a released node/ledger version such that failed checks prevent enactment and treasury movement.
- **Conformance tests available** covering at least:
  - under-cap, exact-cap, and over-cap withdrawals,
  - `netChangeLimit = 0`,
  - guardrail evaluation against the pre-write 73-slot snapshot at epoch transition,
  - epoch-boundary ordering (check, write, then pointer advance),
  - epoch rollover pointer advancement in zero-activity epochs,
  - slot overwrite behavior after full 73-epoch rotation,
  - cap computation with negative aggregate revenue clamped to zero,
  - bootstrap initialization (`73 x (bootstrapRevenueSeed, 0)`) and progressive overwrite with measured data,
  - no treasury movement on failed guardrail checks.
- **Governance activation complete** through required governance / protocol rollout and initial on-chain `netChangeLimit` setting.

### Implementation Plan

- **Specification finalization**
  - Incorporate review feedback from governance bodies, implementors, and CIP Editors.
  - Lock terminology against existing governance and ledger documentation.
- **Ledger and node work**
  - Add/confirm protocol parameter `netChangeLimit`.
  - Implement normative ring state (`73` slots + pointer), revenue measurement, rollover, and bootstrap initialization behavior.
  - Expose required canonical state for guardrail-script admissibility checks at enactment.
- **Guardrail script work**
  - Implement NCL admissibility logic against canonical ledger state per this CIP.
  - Ensure failure blocks enactment and treasury movement.
- **Testing and validation**
  - Add deterministic conformance tests for window sums, arithmetic, rollover semantics, and bootstrap behavior.
  - Validate no treasury movement occurs when guardrail checks fail.
- **Governance rollout**
  - Submit and ratify required governance actions to activate implementation and applicable guardrail script.
  - Set initial parameter values on-chain.

## References

- [Cardano Blockchain Ecosystem Constitution](https://docs.intersectmbo.org/archive/cardano-governance-archive/cardano-constitution/read-the-cardano-constitution), Article IV (Cardano Blockchain Ecosystem Budget), especially Section 3 (net change limit and withdrawal constraints).
- [Cardano Blockchain Ecosystem Constitution](https://docs.intersectmbo.org/archive/cardano-governance-archive/cardano-constitution/read-the-cardano-constitution), Appendix I, Treasury Guardrails.
- [CIP-1694: A First Step Towards On-Chain Decentralized Governance](../CIP-1694/README.md)

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
