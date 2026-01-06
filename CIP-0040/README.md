---
CIP: 40
Title: Collateral Output
Status: Active
Category: Ledger
Authors:
  - Sebastien Guillemot <seba@dcspark.io>
  - Jared Corduan <jared.corduan@iohk.io>
  - Andre Knispel <andre.knispel@iohk.io>
Implementors: N/A
Discussions:
  - https://github.com/cardano-foundation/CIPs/pull/216
Created: 2022-02-10
License: CC-BY-4.0
---

## Abstract

This document describes adding a new output type to transactions called Collateral Outputs.

## Motivation: Why is this CIP necessary?

As of Alonzo, transactions that call Plutus smart contracts are required to put up collateral to cover the potential cost of smart contract execution failure. Inputs used as collateral have the following properties:

1. Cannot contain any tokens (only ADA)
2. Cannot be a script address
3. Must be a UTXO input
4. Must be at least some percentage of the fee in the tx (concrete percentage decided by a protocol parameter)
5. Can be the same UTXO entry as used in non-collateral tx input
6. Is consumed entirely (no change) if the contract execution fails during phase 2 validation
7. Is not consumed if phase phase 2 validation succeeds

Additionally, there cannot be more than *maxColInputs* (protocol parameter) inputs and the inputs have to cover a percentage of the fee defined by *collateralPercent* (protocol parameter)

However,

- Restriction #1 is problematic because hardcore dApp users rarely have UTXO entries that do not contain any tokens. To combat this, wallets have created a special wallet-dependent "collateral" UTXO to reserve for usage of collateral for dApps which is not a great UX.
- Restriction #6 is problematic because wallets want to protect users from signing transactions with large collateral as they cannot verify whether or not the transaction will fail when submitted (especially true for hardware wallets)

## Specification

If phrase-2 verification fails, we can send outputs to a special output marked as the collateral output.

There are two ways to create collateral outputs

1. Add collateral outputs as a new field inside the transaction. This change is similar to how collateral inputs were created a new field
2. Change the definition of outputs as `TxOut = Addr × Value × DataHash? × Source?` where source (optional for backwards compatibility) is an enum `0 = regular output, 1 = collateral output`.

Option #1 provides the best backwards compatibility because we don't expect phase-2 validation to be a common occurrence and so wallets that (due to not being updated) never check collateral outputs will still in the overwhelming majority of cases return the correct result.

Additionally, this requires updating the collateral requirement.

If no collateral output is specified (and therefore no tokens are in the collateral input), then we keep the old definition

```
ubalance (collateral txb ◁ utxo) ≥ quot (txfee txb * (collateralPercent pp)) 100
```

However, if collateral output is specified, then
1. Each collateral output needs to satisfy the same minimum ADA requirement as regular outputs
2. Collateral output needs to be balanced according to `sum(collateral_input) = sum(collateral_output) + collateral_consumed`
Where `collateral_consumed` is equal to the old formula (`quot (txfee txb * (collateralPercent pp)) 100`). Note that when collateral is consumed, any certificate, etc. in the transaction is ignored so they have no impact on the change calculation.

## Rationale: How does this CIP achieve its goals?

### Self-contained balancing

Some use-cases like hardware wallets, who do not have access to the content of the collateral inputs, cannot easily check if the collateral is balanced. Similar to how we specify an explicit fee as part of the transaction body to tackle this problem, the transaction body also needs a new field that explicitly specified how much collateral will be consumed in the case of phase-2 validation failure.

## Path to Active

### Acceptance Criteria

- [x] Fully implemented in Cardano as of the Vasil protocol upgrade.

### Implementation Plan

- [x] Passes all Ledger team requirements for desirability and feasibility.

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
