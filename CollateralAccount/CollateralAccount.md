---
CIP: ?
Title: Collateral Account for HD Wallets
Authors: Sebastien Guillemot <seba@dcspark.io>
Comments-URI: https://forum.cardano.org/t/collateral-account-derivation/65879
Status: Draft
Type: Standards
Created: 2021-06-29
License: CC-BY-4.0
---

# Abstract

This document describes using a separate derivation path to ensure there is always sufficient collateral to execute UTXO smart contracts

# Motivation

Collateral input | As of Alonzo, transactions that call non-native smart contracts are required to put up collateral to cover the potential cost of smart contract execution failure. Inputs used as collateral has the following properties:

- Cannot contain any tokens (only ADA)
- Cannot be a script address
- Must be a UTXO input
- Must be at least some percentage of the fee in the tx (concrete percentage decided by a protocol parameter)
- Can be the same UTXO entry as used in regular tx input
- Is consumed entirely (no change) if the contract execution fails during phase 2 validation

We therefore need a way for the wallet to handle picking which inputs to use for collateral

## Naive solution

The naive solution would do the following steps
1. Add any regular input that satisfies the constraints as collateral as well
1. If collateral is still insufficient, look at the wallet UTXO for any other entry that can be added as collateral
1. If there are not enough UTXO entries that can be used as collateral, check if we can refactor the wallet UTXO to create enough UTXO entries that match the requirement
1. If refactoring can unblock the wallet, prompt the user to send a transaction to refactor their UTXO (and pay the tx fee associated with it) before sending their transaction. If refactoring can't unblock the wallet, tell the user they will need more ADA to call this smart contract

This however, causes the following problems:
1. This may cause users to risk more collateral than they are comfortable with. In general, software should run smart contracts locally to detect if a transaction would fail before sending and alert the user to avoid consuming the collateral, but relying on this is not ideal.
1. Although the refactor transaction can be created under the hood for in-software wallet, it will confused users when it shows up on their transaction history. For hardware wallets, it will require explicit approval from the user which is also possibly confusing.
1. Altough wallets can try and always pick UTXOs to make sure there is always a valid UTXO entry for collateral, it can't be guaranteed because the wallet state can always be changed by any dApp or other wallet that doesn't use the same logic to guarantee the presence of satisfactory collateral input
1. Multisig wallets don't have any non-script addresses in general and so would need some separate solution

So with this, we can see the naive solution is complicated while still having issues and an unintuitive user experience.



# Specification

Recall that [CIP1852](../CIP-1852) specifies the following derivation path

```
m / purpose' / coin_type' / account' / chain / address_index
```

We set `chain=3` to indicate the *collateral chain*.

## *address_index* value

Wallets MUST only use `address_index=0` for this specification. Since a single address can contain multiple UTXO entries, there is no need to derive other addresses (using more addresses would not provide any privacy benefit and would complicate address discovery).

We will call this specific derivation the *collateral account*.

## New solution for managing collateral

Wallets SHOULD only use UTXO entries of the collateral account as collateral in the transaction. If the collateral is insufficient, the wallet should tell the user to send more ADA to their collateral account.

The benefits of this solution are as follows:
1. Transactions in the history to add collateral can be clearly marked as such by wallet software.
1. Prompting the user to add ADA to their collateral account doesn't require explaining users about how UTXO works under the hood compared to the refactoring option.
1. No change required to input selection algorithms
1. Multisig (or other script-based wallets) are handled the same way as regular wallets
1. User only risks as much collateral as their are comfortable with

However, this solution also comes with downsides:

1. Reusing the same collateral account for all your smart contract calls gets rid of any privacy. However, base addresses in Cardano already forgo privacy and so users who want to call smart contracts with privacy will already need to handle things differently.
1. The blockchain can't stop people from sending tokens to somebody's collateral account. This doesn't harm the user (since other UTXO entries can still be used) and wallets will already need to implement a way for the user to withdraw from their collateral account so the impact should be minimal.
1. It's possible for the collateral account to contained mangled addresses (same as regular base addresses for the wallet), but empirically mangled addresses are rare and people should not be sending to collateral accounts directly anyway so this is of minimal concern
1. Support for a collateral account needs to be added to hardware wallets
1. If the user doesn't reduce the ADA in their collateral account when calling cheaper smart contracts, they are still be putting up more collateral than necessary

## Test vectors

recovery phrase
```
prevent company field green slot measure chief hero apple task eagle sunset endorse dress seed
```

collateral private key (including chaincode) for `m / 1852' / 1815' / 0' / 3 / 0`
```
40c7f7d3c03c3711e6c03ef828ba244f40f81ec915899483eda006bac0e5974480b77fe9816eb518cb190214b7368e76e3462a0caecfb1d3add8315bfe2e5616647312b7b6d29e0e577b9923594a12be4ded5f5e3a8f7d5249f33c97ecafa620
```

staking private key (including chaincode) for `m / 1852' / 1815' / 0' / 2 / 0`
```
b8ab42f1aacbcdb3ae858e3a3df88142b3ed27a2d3f432024e0d943fc1e597442d57545d84c8db2820b11509d944093bc605350e60c533b8886a405bd59eed6dcf356648fe9e9219d83e989c8ff5b5b337e2897b6554c1ab4e636de791fe5427
```

base address (with `network_id=1`)
```
addr1qy85lw87w0q6xns59y806v37xh6dafnf3w6kkn6x3p4pzsqwfdvw69hjqdklg9x94f8wxwlkldzsd8ycmxsj06904p9skhtxnm
```

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode)
