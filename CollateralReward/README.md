---
CIP: ?
Title: Collateral Reward
Authors: Sebastien Guillemot <seba@dcspark.io>
Status: Draft
Type: Standards
Created: 2022-02-10
License: CC-BY-4.0
---

# Abstract

This document describes providing change on phase-2 validation through the reward account

# Motivation

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

# Specification

If phrase-2 verification fails, we send any remaining ADA collateral and associated token to a reward address where the reward address is defined using the following cases for each collateral input:
2. If a base address, send the change to the reward StakeCredential of the address 
2. If a enterprise address, send the change to the payment StakeCredential of the address
3. If a pointer address, send to reward address registered at the pointer
4. Disable legacy addresses as collateral

Additionally, this requires updating the collateral requirement. The old requirement was defined as

```
ubalance (collateral txb ◁ utxo) ≥ quot (txfee txb * (collateralPercent pp)) 100
```

This would instead be replaced by the new function

```
ubalance (collateral txb ◁ utxo) ≥ (quot (txfee txb * (collateralPercent pp)) 100) + (inject (scaledMinDeposit v (minUTxOValue pp))) + keyDeposit pp
```

### Problems

- Making the rewards claimed due to phase-2 validation only claimable after the next epoch boundary is both a confusing user experience and also not desired because the epoch boundary already has too much to compute.
- Handling of enterprise addresses is non-intuitive
- We need to always include `keyDeposit pp` because we need to ensure the staking key is registered by the time this tx appears on-chain (no guarantees somebody doesn't deregister their staking key before the ttl of the transaction that will fail expires)
- This opens up a path for projects to "drop" tokens to reward addresses. To avoid this, probably the only solution would be to properly implement chimeric ledgers
- Tokens could accumulate beyond the protocol limits
    - too big to fit in a single tx (yet withdrawing partial rewards is further complexity)
    - Same applies to other protocol size limits like `MaxValSize`

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode)
