---
CIP: 181
Title: Remove dRep Requirement for Reward Withdrawals
Category: Ledger
Status: Proposed
Authors:
  - Ryan Wiley <rian222@gmail.com>
Implementors: []
Discussions:
  - https://github.com/cardano-foundation/CIPs/pull/1159
Created: 2026-03-05
License: CC-BY-4.0
---

## Abstract

This CIP removes the requirement that a reward withdrawal be conditioned on governance voting delegation. Under the current Conway governance regime introduced by [CIP-1694](https://cips.cardano.org/cip/CIP-1694), rewards continue to accrue normally, but after the bootstrap phase a reward account may be prevented from withdrawing unless its stake credential is delegated for voting to a registered DRep or one of the predefined voting options. This proposal changes the ledger so reward withdrawals are accepted regardless of governance delegation status. The goal is to stop using access to earned staking rewards as a governance-participation lever.

## Motivation: why is this CIP necessary?

[CIP-1694](https://cips.cardano.org/cip/CIP-1694) introduced a deliberate incentive: after the bootstrap phase, reward accounts are blocked from withdrawing rewards unless their associated stake credential is also delegated for voting. The stated rationale was to help ensure high governance participation and therefore legitimacy.

That design choice was understandable during bootstrapping, but it is no longer necessary or noticeably helpful as an ongoing participation mechanism after full on-chain governance activation on mainnet on 2025-01-29 via the Plomin hard fork. Governance participation should be encouraged by governance tooling, representation quality, and future incentive design, not by restricting access to already-earned staking rewards.

This requirement creates three concrete problems.

First, it conditions access to earned rewards on a governance choice that many ADA holders may not yet be prepared to make. A holder may reasonably wish to keep earning staking rewards through stake pool delegation while postponing a voting delegation decision. Under the current rule, that holder is forced to combine two otherwise distinct decisions merely to withdraw rewards.

Second, making withdrawals contingent on voting delegation creates pressure toward convenience delegation flows in wallets and custodial interfaces. When the user is blocked from withdrawing unless some governance delegation is present, interfaces are incentivized to simplify the step by preselecting, defaulting, auto-populating, or otherwise steering the user toward a delegation outcome. Even when presented as convenience, this creates avoidable pressure that can concentrate voting power and distort representative choice.

This CIP adopts a simpler position: reward withdrawal and governance delegation should be decoupled. An ADA holder should be able to withdraw earned rewards without being required to delegate voting power first.

## Specification

### Rule change

The Conway-era ledger currently rejects some reward withdrawals when the withdrawing reward account is not engaged in governance delegation. In external tooling, this behavior is exposed through errors such as `ConwayWdrlNotDelegatedToDRep` and Ogmios' `ForbiddenWithdrawal` condition.

This CIP removes that withdrawal-specific governance-delegation check.

A transaction that is otherwise valid and includes a reward withdrawal MUST NOT be rejected on the basis that the withdrawing reward account, stake credential, or corresponding voting stake is not delegated to:

- a registered DRep,
- the predefined `Abstain` option, or
- the predefined `No Confidence` option.

Post-adoption, reward withdrawals are valid regardless of whether the withdrawing credential has an active voting delegation.

### Implementation notes

Implementations should remove the Conway reward-withdrawal validation path that rejects undelegated reward withdrawals. Wallets, custodians, APIs, and transaction submission layers should update any user-facing logic or documentation that implies reward withdrawal requires prior voting delegation.

## Rationale: how does this CIP achieve its goals?

This CIP achieves its goal by removing the coercive coupling between reward access and governance delegation while leaving the governance system otherwise unchanged.

[CIP-1694](https://cips.cardano.org/cip/CIP-1694) selected withdrawal gating as a way to address long-term participation after rejecting an active voting stake threshold approach. That choice was intended to increase participation. However, requiring governance delegation before reward withdrawal is a blunt instrument:

- it pressures users at the moment they are trying to access earned rewards,
- it conflates reward withdrawal with govenance representative selection,
- it encourages interface patterns optimized for completion rather than informed delegation, and
- it introduces a protocol-level dependency that has already required compatibility exceptions.

Removing the requirement is preferable to adding more carve-outs or automatic defaults.

### Backward compatibility

This CIP is a relaxation of an existing Conway-era validity rule. Transactions that are valid before this change remain valid after it. The principal change is that transactions withdrawing rewards from undelegated reward accounts become valid post-adoption.

This improves compatibility for tooling and wallet flows that should not need governance delegation merely to withdraw rewards. It also removes a class of submission failures currently surfaced by nodes and middleware.

## Path to Active

### Acceptance Criteria

- [ ] The Conway ledger specification is updated so reward withdrawals no longer depend on governance delegation status.
- [ ] `cardano-ledger` implements the rule change and includes regression tests covering withdrawals from undelegated reward accounts.
- [ ] `cardano-node` integrates the change and releases it as part of a Cardano hard fork.
- [ ] Wallets and transaction-submission tooling update user-facing messaging to reflect that reward withdrawal no longer requires prior voting delegation.
- [ ] The change is live on Cardano mainnet.

### Implementation Plan

- [ ] Amend the Conway-era formal specification to remove withdrawal rejection based on missing voting delegation.
- [ ] Update ledger tests to demonstrate that reward withdrawals from undelegated reward accounts are accepted after the fork.
- [ ] Update downstream tooling and documentation that currently expect `ConwayWdrlNotDelegatedToDRep` / `ForbiddenWithdrawal` for this case.

## References

- [CIP-1694: A First Step Towards On-Chain Decentralized Governance](https://cips.cardano.org/cip/CIP-1694)
- [CIP-0084: Cardano Ledger Evolution](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0084)
- [Plomin upgrade readiness](https://cardanoupgrades.docs.intersectmbo.org/plomin-upgrade/chang-upgrade-2-readiness)
- [Intersect Development Update #47 - January 31st](https://www.intersectmbo.org/news/intersect-development-update-47-january-31st)
- [Ogmios: SubmitTransactionFailureForbiddenWithdrawal](https://ogmios.dev/typescript/api/interfaces/_cardano_ogmios_schema.SubmitTransactionFailureForbiddenWithdrawal.html)

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
