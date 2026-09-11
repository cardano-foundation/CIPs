---
CPS: "?"
Title: Application and transaction-builder friction in the current minUTxO implementation
Category: Ledger
Status: Open
Authors:
  - Nicolas Henin <nicolas.henin@iohk.io>
  - Will Gould <will.gould@iohk.io>
  - Polina Vinogradova <polina.vinogradova@iohk.io>
Proposed Solutions: []
Discussions: []
Created: 2026-07-28
License: CC-BY-4.0
---

## Abstract

Cardano's current minUTxO rule requires every new transaction output to contain a
minimum amount of ada based on a fixed per-output overhead and the output's serialised
size. This size-sensitive requirement provides **economic coordination** for
persistent UTxO state. However, the required ada is represented as ordinary output
value, which creates additional friction.

The minimum is determined from the complete serialised `TxOut`, including any datum
or reference script. The ada used to satisfy it remains ordinary coin in `TxOut.Value`,
alongside the ada and native assets the application intends the output to carry.
The same ada can serve both purposes. The ledger records no separate deposit or
backing balance, and control of all ada follows the output's spending condition.

This coupling creates **accidental implementation friction** beyond the **necessary
resource friction** of protecting the live UTxO set. It can prevent a standalone
payment below minUTxO, make a token sender supply ada later controlled by the recipient,
and require ada in application state that does not participate in staking. High
fan-out and successor-output top-ups amplify the funding and transaction-building
burden.

This CPS documents these frictions and their current workarounds, and sets goals for
reducing them while preserving protection of the live UTxO set.

## Problem

### The current minUTxO rule

Under the current Babbage and Conway rule, every newly created output `o` must
satisfy [[1]](#ref-1):

```math
\mathrm{coin}(o)
\geq
\mathrm{minUTxO}(o)
=
\left(
160+\mathrm{sizeInBytes}(\mathrm{TxOut}(o))
\right)
\times
\mathrm{coinsPerUTxOByte}
```

Four properties of the rule are relevant here:

1. it applies separately to every newly created output;
2. larger encoded outputs generally require more ada;
3. the required ada is ordinary ada inside `TxOut.Value`; and
4. control of that ada follows the output's spending condition.

The required ada is not a transaction fee, a payment to an SPO or the treasury, or a
burn. Nor is it recorded as a separate ledger deposit: it remains part of the
output's value and is consumed with the rest of that value.

When an output is consumed, its ada can already fund new outputs and transaction
fees in the same transaction. Consolidating outputs or reducing their size can make
ada available for other uses, subject to the minima of the outputs that remain.
Ada in a live output may also participate in staking, depending on its address and
stake credential.

### Applicative value and operational backing

Two roles are relevant here:

| Role | Meaning | Current representation |
|---|---|---|
| **Applicative value** | The ada and native assets the application intends the output to carry | Present in `TxOut.Value`, but not identified separately from operational backing |
| **Operational backing** | The economic role played by the output's ada in satisfying minUTxO | Not represented separately; enforced as a lower bound on ada in the same `Value` |

The same ada can serve both as applicative value and as operational backing. For
example, ada sent as a payment can also satisfy the output's minUTxO requirement.
Conversely, a datum or reference script can increase the required ada even though
neither is stored in `Value`. The creating transaction must source enough ada; once
the output exists, its spending condition controls it.

### Necessary resource friction and accidental implementation friction

Protecting persistent ledger state entails **necessary resource friction**. Under
minUTxO, keeping an output live requires ada to remain assigned to it. A different
representation of the same backing requirement still needs to fund it.

The current rule also ties that funding to application outputs: each output must
carry its own minimum under its own spending condition. This constrains the intended
transfer, the allocation of control over ada, and the construction of application
state. The question is which constraints are needed for resource protection and
which are **accidental implementation friction** that can be reduced through changes
to funding, representation, or application interfaces.

Lowering `coinsPerUTxOByte` preserves the representation but can reduce the burden or
make particular payments possible. Its effects on resource protection must be
considered alongside those improvements.

## Use Cases

The use cases are grouped by where the friction appears:

- **Business-flow friction:** what the application can represent, who must supply the
  required ada, and what coordination the operation requires.
  - [1. The frozen wallet](#use-case-frozen-wallet)
  - [2. Sending less than minUTxO](#use-case-below-minutxo)
  - [3. Funding ada controlled by the recipient](#use-case-fund-for-someone-else)
  - [4. Ada held in non-staking application state](#use-case-non-staking-state)
- **Transaction-builder friction:** the work required to size outputs, source ada,
  and balance a valid transaction.
  - [5. Transaction construction and change balancing](#use-case-transaction-construction)
  - [6. High-fan-out distribution](#use-case-high-fan-out)
  - [7. Successor-output top-up](#use-case-continuing-output)

### Business-flow friction

<a id="use-case-frozen-wallet"></a>

#### 1. The frozen wallet

An available output contains an asset or application state that must be preserved. At
the current protocol parameters, it contains exactly the minimum ada required by an
equivalent successor. No other source of ada is available to the transaction.

| Aspect | Explanation |
|---|---|
| **Why minUTxO matters** | The output is spendable, but all of its ada is needed by the successor. The transaction cannot satisfy both the successor's minimum and its own minimum fee. |
| **Current workarounds** | Supply ada from another input or withdrawal, obtain a fee sponsor, or consolidate funds in advance. Each requires extra liquidity, preparation, or another participant. |

Separating the same backing from output value would still leave no surplus for the
fee.

<a id="use-case-below-minutxo"></a>

#### 2. Sending less than minUTxO

A user wants to create an independent output containing either `x` ada, where
`0 < x < minUTxO(o)`, or a native token with no intended ada transfer. The sender wants
the payment to complete without waiting for the recipient to join the transaction.

| Aspect | Explanation |
|---|---|
| **Why minUTxO matters** | The small ada payment cannot be represented exactly as a new output. The token must be accompanied by ada. |
| **Current workarounds** | Aggregate payments, or co-spend and recreate an existing recipient output. These options change the flow or require recipient coordination. |

<a id="use-case-fund-for-someone-else"></a>

#### 3. Funding ada controlled by the recipient

A sender wants to push a native token to a new recipient output without transferring
ada. The recipient supplies neither an input nor funding. Unlike use case 2, the
concern here is who supplies and later controls the required ada.

| Aspect | Explanation |
|---|---|
| **Why minUTxO matters** | The sender must source the ada required by the new output, but the recipient controls that ada after the output is created. The sender has no separate claim to recover it. |
| **Current workarounds** | Co-spend and recreate an existing recipient output, use a recipient-funded pull or claim flow instead of a push flow, or reduce the new output's size. The first two require coordination or change the flow; the last only reduces the amount. |

<a id="use-case-non-staking-state"></a>

#### 4. Ada held in non-staking application state

When application state is held at an address that does not participate in staking,
each state output must still carry minUTxO.

| Aspect | Explanation |
|---|---|
| **Why minUTxO matters** | Each state output must carry ada that earns no staking rewards while the state remains live. |
| **Current workarounds** | Use a suitable stake credential where the application design permits it, reduce the output size, or represent the state with fewer outputs. |

### Transaction-builder friction

A transaction builder must reason about three different economic roles:

- **applicative value:** the ada and native assets the application intends to carry;
- **transaction fee:** the cost of the transaction; and
- **operational backing:** the ada needed to satisfy each output's minUTxO.

Applicative value and operational backing share `TxOut.Value`, even though they serve
different purposes. The minimum depends on the complete serialised `TxOut`, so changes
to its address, `Value`, datum, or reference script can change the required ada. This
includes changes to the asset bundle of a change output during balancing.

<a id="use-case-transaction-construction"></a>

#### 5. Transaction construction and change balancing

A builder constructs a multi-asset transfer or state transition that creates
token-bearing, script-locked, or change outputs, some carrying a datum or reference
script. CIP-68 and CIP-89 provide examples of such output patterns [[2]](#ref-2)
[[3]](#ref-3).

| Aspect | Explanation |
|---|---|
| **Why minUTxO matters** | The builder must calculate the minimum for every output and allocate enough ada. Adding an input can change the asset bundle, size, and minUTxO of the change output, requiring another balancing pass. |
| **Current workarounds** | Libraries and wallets can automate minimum calculation and balancing, subject to the application's output and funding constraints. |

<a id="use-case-high-fan-out"></a>

#### 6. High-fan-out distribution

This case repeats the sender-funded output from use case 3 across many recipients, as
in an airdrop, reward distribution, or exchange-withdrawal batch.

| Aspect | Explanation |
|---|---|
| **Why minUTxO matters** | Every recipient output requires its own minimum. For token-only distributions, the sender must source and transfer the sum of those minima. The builder must allocate the ada and balance the transaction. |
| **Current workarounds** | Reduce output sizes, split the distribution across transactions, or use a recipient-funded claim flow. Splitting spreads the work without reducing each output's minimum; claiming changes who initiates and funds the transfer. |

<a id="use-case-continuing-output"></a>

#### 7. Successor-output top-up

An application consumes a state output and creates a larger successor, or recreates it
after `coinsPerUTxOByte` has increased.

| Aspect | Explanation |
|---|---|
| **Why minUTxO matters** | The consumed output's ada can be reused, but may not cover the successor's increased minimum. Any remaining shortfall must be funded. |
| **Current workarounds** | Use other funds already available to the transaction, retain an ada buffer in the state, or add a funding input. A buffer commits funds in advance; an additional input requires a funding path. |

Before fees and other outputs are considered, the shortfall is the positive
difference between the successor's minimum and the ada recovered from the state
input.

A stable tariff can make this lifecycle issue less visible. Changing
`coinsPerUTxOByte` does not debit or invalidate existing outputs; new outputs,
including successors, must meet the parameters in force when validated
[[4]](#ref-4). Ada recovered from an input can therefore fall short even when
application state is unchanged.

Proposals with explicit deposits must also distinguish historical allocation,
current funding requirements, and the amount available for release after a parameter
change, and explain how any shortfall or surplus is handled.

## Goals

### Properties that must be preserved

Any proposed solution must:

1. **Protect persistent ledger state.** Maintain protection against adversarial
   accumulation of live-output count and size through a rule the ledger can validate
   locally and deterministically. Compare the protection of the live stock with the
   current rule; a charge that only slows creation is not an equivalent guarantee.
2. **Preserve ledger correctness.** Value must remain conserved, existing outputs
   must remain spendable, and the transition to any new rules must be unambiguous.

### Outcomes to improve

1. **Reduce accidental implementation friction.** Allow applications to express their
   intended output content with fewer constraints from the representation of
   operational backing.
2. **Reduce business-flow friction.** Reduce the funding and coordination burdens
   identified in the use cases without shifting them invisibly to another participant
   or layer.
3. **Simplify transaction building.** Reduce the complexity of funding, allocation,
   balancing, and top-up logic in applications, wallets, and SDKs.
4. **Limit ecosystem disruption.** Avoid unnecessary trust, infrastructure, and
   migration requirements.

### Evaluation requirements

A proposed solution should:

- compare every use case with the current rule and effective existing workarounds,
  including parameter changes where relevant;
- state whether each pain point is removed, reduced, unchanged, or shifted, and
  identify who bears remaining burdens or regressions;
- use reproducible transactions to compare total ada required, fees, intended
  transfers, and recoverable backing, counting ada that serves overlapping roles
  only once; and
- show which application or builder logic disappears, distinguishing that improvement
  from a change in funding, pricing, or participants.

Examples should cover outputs with no intended ada, ada below the current minimum,
and ada sufficient to satisfy it. They should follow backing through creation,
continuation, consolidation, and release, including changes in the requirement.

Selecting an optimal tariff or a particular deposit, account, or settlement design
is outside this CPS's scope.

## Open Questions

1. If a capacity-pricing parameter such as `coinsPerUTxOByte` increases, should an
   application provide additional funding when it recreates an output without
   increasing its size, or should its existing funding remain sufficient?
2. If the representation of ada required for minUTxO changes, how can deployed
   contracts that check exact ada amounts continue to operate?
3. When an output is no longer useful to an application and the fee to spend it
   exceeds the ada that spending it would free, is it acceptable for it to remain in
   the UTxO set indefinitely, or should there be an additional incentive to remove it?
4. If a solution uses explicit deposits, should they be stored in each output or
   managed separately by the ledger? If managed separately, should each deposit fund
   one output, or could a deposit fund several? Could transactions using shared
   funding still proceed independently?

## References

<a id="ref-1"></a>

1. [*CIP-55: Protocol Parameters (Babbage
   Era)*](https://cips.cardano.org/cip/CIP-0055). The specification defines the
   per-byte minUTxO calculation for Babbage outputs.

<a id="ref-2"></a>

2. [*CIP-68: Datum Metadata
   Standard*](https://cips.cardano.org/cip/CIP-0068).

<a id="ref-3"></a>

3. [*CIP-89: Distributed DApps and Beacon
   Tokens*](https://cips.cardano.org/cip/CIP-0089).

<a id="ref-4"></a>

4. [*Cardano Ledger: Babbage UTxO
   validation*](https://github.com/nhenin/cardano-ledger/blob/bef480ebd/eras/babbage/impl/src/Cardano/Ledger/Babbage/Rules/Utxo.hs#L399).
   The minimum-output check uses the transaction's newly created outputs and the
   current protocol parameters.

## Copyright

This CPS is licensed under
[CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
