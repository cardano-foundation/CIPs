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

The Cardano Constitution requires treasury withdrawals to respect a net change limit. Today, the net change limit is set via on-chain Info Actions that must be repeatedly voted on. In practice, multiple NCL Info Actions can coexist with different periods, thresholds, and approval timing, creating ambiguity about which one is legitimate and how the Constitutional Committee (CC) should treat those actions.

This CIP removes that ambiguity by defining a single ledger-enforced mechanism.

It introduces two governance-updatable protocol parameters:

- `netChangeLimit`: integer percentage (`>= 0`)
- `netChangePeriod`: epoch lookback window (`> 0`)

The ledger computes a withdrawal cap from recent treasury revenue (fees + emissions) and rejects Treasury Withdrawal governance actions at enactment when they exceed the remaining headroom.

`cap(E) = floor(netChangeLimit * revenue(E) / 100)`

where `revenue(E)` is treasury revenue over the previous `netChangePeriod` epochs.

This creates a single canonical on-chain source of truth for this rule while preserving constitutional guardrails as a complementary mechanism for constraining parameter values.

## Motivation: why is this CIP necessary?

The net change limit is currently set via on-chain Info Actions, which creates a repetitive and operationally heavy voting cycle. Those NCLs are typically forward-looking projections rather than backward-looking measurements of realized treasury flows. Multiple NCL Info Actions are often discussed or voted around the same period, and they may differ in projected period, approval thresholds, and approval timing. This leads to ambiguity about which NCL should govern treasury withdrawals.

Key ambiguities include:

- Competing NCL references. If multiple NCL Info Actions exist, should the legitimate one be the highest approved, the most recent approved, or something else?
- CC role boundary. Should the CC approve NCL Info Actions themselves, or only use NCL when assessing the constitutionality of subsequent Treasury Withdrawals?

This CIP moves to a ledger-enforced, lookback-based model over realized treasury revenue and withdrawals. Ledger-native enforcement is needed so that:

- Rule application is deterministic. Equivalent actions are treated equivalently by all nodes.
- Interpretation ambiguity is removed. Code is law.
- Governance overhead is reduced. CC review no longer carries primary responsibility for arithmetic limit checks.
- Budgeting remains adaptive to revenue. Spending capacity still scales from recent treasury inflows.

## Specification

### Overview

This CIP defines a ledger rule that enforces a net change limit for **Treasury Withdrawal** governance actions.

### Protocol parameters

This CIP defines or updates two governance parameters:

- `netChangeLimit`: integer percentage, `>= 0`.
  - `0` is explicitly valid and means no treasury withdrawals can be enacted.
  - Values greater than `100` are valid and would simply allow deficit spending.
- `netChangePeriod`: integer number of epochs, `> 0`.

No upper or lower bounds are imposed by this CIP for either parameter. These could optionally be set in the Constitution and enforced by guardrail scripts.

### Revenue and withdrawal accounting

For an enactment occurring in epoch `E`, let `N = netChangePeriod`.

The lookback window is the previous `N` epochs:

`[E - N, E - 1]`

The current epoch `E` is excluded from revenue lookback.

Define:

- `revenue(E)`: sum of treasury inflows from **fees + emissions** over `[E - N, E - 1]`.
- `usedPast(E)`: sum of treasury withdrawals enacted over `[E - N, E - 1]`.
- `usedCurrent(E, i)`: sum of treasury withdrawals already enacted earlier in epoch `E` before evaluating action `i`, using existing deterministic ledger enactment order.

Then:

- `cap(E) = floor(netChangeLimit * revenue(E) / 100)`
- `used(E, i) = usedPast(E) + usedCurrent(E, i)`

All arithmetic is in lovelace integers.

### Enforcement rule

For a Treasury Withdrawal action `i` with amount `w(i)`, enactment is allowed iff:

`used(E, i) + w(i) <= cap(E)`

If this inequality fails, the ledger **must reject enactment** of that Treasury Withdrawal action and **no treasury funds move** for that action.

If multiple Treasury Withdrawal actions are enacted in the same epoch, checks are sequential in existing deterministic enactment order, and each successful enactment updates `usedCurrent(E, i)` for subsequent checks.

### History edge behavior

This CIP defines behavior for incomplete historical coverage:

- If fewer than `netChangePeriod` prior epochs are available (e.g., early life of the rule), enforcement uses all available prior epochs.
- If `netChangePeriod` is increased beyond currently retained history, enforcement applies immediately using available retained history, and effective lookback grows as additional epochs accumulate.

Implementations may use any internal representation (including optimized storage), but observable enforcement behavior must match this specification.

### Guardrails integration

The normative enforcement path for withdrawal-limit violations is direct ledger rejection as defined above.

Guardrail scripts are complementary in this CIP and may be used to constrain allowed ranges (upper/lower bounds) for `netChangeLimit` and `netChangePeriod` through constitutional processes. Withdrawal-limit enforcement in this CIP does not depend on selecting a script path.

## Rationale: how does this CIP achieve its goals?

- **Closes the enforcement gap.** The ledger, not humans, enforces the net change limit rule.
- **Deterministic and auditable.** The cap and admissibility check are fully specified and reproducible.
- **Revenue-linked sustainability.** Withdrawals are bounded by recent treasury inflows from fees + emissions.

## Path to Active

### Acceptance Criteria

- **CIP process acceptance** by CIP Editors with complete and unambiguous ledger-enforcement semantics.
- **Ledger implementation available** in a released node/ledger version that enforces this rule for Treasury Withdrawals.
- **Conformance tests available** covering at least:
  - under-cap, exact-cap, and over-cap withdrawals
  - multiple withdrawals in one epoch
  - `netChangeLimit = 0`
  - short-history startup behavior
  - raised-`netChangePeriod` behavior with partial retained history.
- **Governance activation complete** through required protocol update / hard fork process and initial parameter setting on-chain.

### Implementation Plan

- **Specification finalization**
  - Incorporate review feedback from governance bodies, implementors, and CIP Editors.
  - Lock terminology against existing governance and ledger docs.
- **Ledger and node work**
  - Add/confirm protocol parameters `netChangeLimit` and `netChangePeriod` with bounds in this CIP.
  - Implement rolling-window revenue and withdrawal accounting behavior per this spec.
  - Enforce enactment-time rejection for over-limit Treasury Withdrawals.
- **Testing and validation**
  - Add deterministic conformance tests for window, arithmetic, same-epoch ordering, and edge cases.
  - Validate no treasury movement occurs for over-limit actions.
- **Governance rollout**
  - Submit and ratify required governance actions to activate implementation.
  - Set initial parameter values on-chain.
- **Constitution and guardrails alignment**
  - Define constitutional/guardrail bounds for parameter updates as a complementary control.

## References

- [Cardano Blockchain Ecosystem Constitution](https://docs.intersectmbo.org/archive/cardano-governance-archive/cardano-constitution/read-the-cardano-constitution), Article IV (Cardano Blockchain Ecosystem Budget), especially Section 3 (net change limit and withdrawal constraints).
- [Cardano Blockchain Ecosystem Constitution](https://docs.intersectmbo.org/archive/cardano-governance-archive/cardano-constitution/read-the-cardano-constitution), Appendix I, Treasury Guardrails (TREASURY-01a and TREASURY-02a).
- [CIP-1694: A First Step Towards On-Chain Decentralized Governance](../CIP-1694/README.md)

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
