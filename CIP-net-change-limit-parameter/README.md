---
CIP: ?
Title: Net Change Limit Parameter
Category: Ledger
Status: Proposed
Authors:
  - Ryan Wiley <rian222@gmail.com>
Implementors: []
Discussions: []
Created: 2026-01-08
License: CC-BY-4.0
---

## Abstract

The Cardano Constitution requires treasury withdrawals and budgets to respect a net change limit for the treasury balance. Today, that limit is set as a periodic governance value that expires, forcing repeated proposals and votes. This CIP converts the Net Change Limit (NCL) into two updatable protocol parameters: `netChangeLimit` (a percentage) and `netChangePeriod` (an epoch lookback count). Together, they define an adaptive cap based on recent treasury revenue:

`cap = (netChangeLimit / 100) * (treasury revenue over the previous netChangePeriod epochs)`

The cap applies to Cardano Blockchain ecosystem budgets and treasury withdrawals, directly tying spending to revenue over a recent, on-chain period. The ledger does not enforce this cap directly; instead, Constitutional Committee (CC) members use these parameters and ledger data to evaluate constitutionality under the Constitution's treasury guardrails. This design removes repeated "set a new NCL" votes while keeping constitutional oversight intact.

## Motivation: why is this CIP necessary?

The Constitution requires that (a) treasury withdrawals not violate a net change limit and (b) such withdrawals occur under an approved budget, with the Constitutional Committee ensuring constitutionality. Today, the NCL is treated as a time-bound governance value that must be re-proposed and re-ratified on a recurring basis. This leads to:

- **Redundant voting and fatigue.** The community must repeatedly vote on substantially the same limit to avoid expiry.
- **Inconsistent budgeting cadence.** Budgets and withdrawals must align with the timing of NCL renewals rather than with operational needs.
- **Procedural overhead.** Constitutional Committee review and governance action scheduling are burdened by periodic re-authorization that does not change policy intent.

By making NCL an updatable protocol parameter, Cardano can keep a standing, constitutionally grounded cap that is adjustable when needed but not forced to expire. This is consistent with the Constitution's treasury guardrails while making governance more predictable and less repetitive.

## Specification

### Overview

This CIP introduces two protocol parameters that define the Net Change Limit (NCL):

- `netChangeLimit`: **positive integer percentage** (e.g., 20 means 20%). May be greater than 100.
- `netChangePeriod`: **positive integer** number of epochs used as the revenue lookback window (default **73** epochs, ~1 year).

These parameters are classified as **governance parameters** and are updatable via the standard protocol parameter change governance action. This CIP **recommends** a default value for `netChangePeriod` of **73 epochs** (approximately one year) to align with the Constitution's expected budget cadence; governance may adjust it as needed. The value of `netChangeLimit` is intentionally left to governance and will be selected through the implementation plan. The parameters do not introduce any new ledger enforcement rules for treasury withdrawals or budgets; instead, they are used by the Constitutional Committee to assess constitutionality.

### Cap definition

For any point-in-time constitutional review of a budget or treasury withdrawal action, the NCL cap is computed as:

`cap = (netChangeLimit / 100) * (treasury revenue over the previous netChangePeriod epochs)`

**Treasury revenue** for the lookback period is defined as the sum of all inflows to the treasury recorded on-chain for those epochs, excluding withdrawals. In practice, this is derived from ledger-recorded treasury changes (e.g., treasury cut of rewards, fees, donations, or other protocol-defined inflows), as observed on-chain.

### Application to governance actions

The Constitutional Committee should use the computed cap when evaluating:

- **Cardano Blockchain ecosystem budgets** (Info actions) that authorize treasury withdrawals.
- **Treasury withdrawal actions** that request ada from the treasury.

The CC must determine:

1. Treasury revenue over the prior `netChangePeriod` epochs.
2. Treasury outflows already **executed** within the same `netChangePeriod` lookback window.
3. Treasury outflows already **allocated/authorized** (e.g., approved budgets and treasury withdrawals that have not yet been executed), which **count against the cap immediately upon approval**.
4. Whether the new action would cause total treasury outflows to exceed the NCL cap.

If the cap would be exceeded, the action should be deemed unconstitutional and not be ratified.

### Non-ledger enforcement

This CIP **does not** add a ledger rule to reject withdrawals that exceed the cap. Enforcement is constitutional and procedural:

- The Constitution already requires that withdrawals not violate the net change limit and that the CC affirm constitutionality.
- The new parameters provide a standing, updatable definition of the net change limit for that review.

## Rationale: how does this CIP achieve its goals?

- **Aligns with constitutional guardrails.** The Constitution mandates a net change limit for treasury withdrawals and requires CC review. This CIP makes the limit explicit, updatable, and consistently applied.
- **Reduces redundant voting.** By parameterizing the NCL instead of treating it as an expiring governance action, the community avoids repeated votes to re-establish the same limit.
- **Improves predictability.** Budgets and withdrawals can be planned against a stable, formula-based cap derived from recent treasury revenue.
- **Maintains human oversight.** Because the ledger does not enforce this cap, the CC retains discretion to interpret constitutional requirements and evaluate real-world context, consistent with its mandate.
- **Direct revenue linkage.** Using a lookback of actual treasury inflows ties spending capacity to recent revenue, improving sustainability and predictability.
- **Compatible with future guardrails.** The Constitution anticipates that guardrails (including on-chain scripts) may be introduced later. This CIP prepares the parameter structure now, while allowing guardrails to define safe bounds later.

## Path to Active

### Acceptance Criteria

- **CIP Editor approval** confirming completeness, clarity, and alignment with the CIP process.
- **Consensus on initial parameter values** for `netChangeLimit` and `netChangePeriod` prior to activation, including a vote on `netChangeLimit` and confirmation of the default 73-epoch lookback or an alternative.
- **Governance ratification** of a protocol update that introduces these parameters, plus an on-chain parameter update setting initial values.
- **Constitutional alignment** affirmed by the Constitutional Committee, including acknowledgment that treasury guardrails are satisfied using these parameters.

### Implementation Plan

- **Specification finalization**
  - Publish the CIP draft and gather feedback from governance bodies, dReps, SPOs, and CIP Editors.
  - Adjust the parameter definitions for clarity if needed.
- **Ledger and tooling updates**
  - Introduce `netChangeLimit` and `netChangePeriod` as protocol parameters in the ledger and node implementation.
  - Update governance tooling, budgeting workflows, and CC review guidance to use the new cap formula.
- **Governance activation**
  - Submit a protocol update (hard fork governance action if required) to add the new parameters.
  - Submit a protocol parameter update action to set initial values, including a community vote to set `netChangeLimit`.
- **Constitution and guardrails**
  - Submit a Constitution update governance action to define guardrails for the new parameters, consistent with the Constitution.
  - Ratify the updated Constitution.
- **Operational rollout**
  - Document the CC process for computing treasury revenue and evaluating the cap.
  - Monitor early applications to ensure the method is consistent across reviews.

## References

- [Cardano Blockchain Ecosystem Constitution](https://docs.intersectmbo.org/archive/cardano-governance-archive/cardano-constitution/read-the-cardano-constitution), Article IV (Cardano Blockchain Ecosystem Budget), especially Section 3 (net change limit and withdrawal constraints).
- [Cardano Blockchain Ecosystem Constitution](https://docs.intersectmbo.org/archive/cardano-governance-archive/cardano-constitution/read-the-cardano-constitution), Appendix I, Treasury Guardrails (TREASURY-01a and TREASURY-02a).

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
