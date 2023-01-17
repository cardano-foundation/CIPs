---
CPS: ?
Title: Spending Script Redundant Executions
Status: Open
Category: Plutus
Authors: 
  - fallen-icarus <modern.daidalos@gmail.com>
Proposed Solutions: []
Discussions:
  - https://github.com/cardano-foundation/CIPs/issues/417
Created: 2022-12-20
---

## Abstract
Spendings scripts are currently executed once for every UTxO being consumed from a script address. However, there are use cases where the validity of the transaction depends on the transaction as a whole and not on any individual UTxO. The eUTxO architecture allows a spending script to see the entire transaction context which means it is already possible to create scripts that validate based on the transaction as a whole. As of now, spending scripts that do this are forced to be executed once per UTxO even if these extra executions are completely redundant. Not only does this waste computational resources, but it can also result in the transaction fee growing quickly based on the number ot UTxOs being consumed from the relevant script address. There is a technique that can be used to minimize this limitation but it has its own drawbacks. 

## Problem
Currently, all scripts require some variation of the following for every utxo being consumed from the script address:

``` Bash
  --tx-in <script_utxo_to_be_spent> \
  --spending-tx-in-reference <script_ref_utxo> \
  --spending-plutus-script-v2 \
  --spending-reference-tx-in-inline-datum-present \
  --spending-reference-tx-in-redeemer-file <script_redeemer> \
```
If three utxos were to be spent from this script address, then you would need three of these:

``` Bash
  --tx-in <first_script_utxo_to_be_spent> \
  --spending-tx-in-reference <script_ref_utxo> \
  --spending-plutus-script-v2 \
  --spending-reference-tx-in-inline-datum-present \
  --spending-reference-tx-in-redeemer-file <script_redeemer> \
  --tx-in <second_script_utxo_to_be_spent> \
  --spending-tx-in-reference <script_ref_utxo> \
  --spending-plutus-script-v2 \
  --spending-reference-tx-in-inline-datum-present \
  --spending-reference-tx-in-redeemer-file <script_redeemer> \
  --tx-in <third_script_utxo_to_be_spent> \
  --spending-tx-in-reference <script_ref_utxo> \
  --spending-plutus-script-v2 \
  --spending-reference-tx-in-inline-datum-present \
  --spending-reference-tx-in-redeemer-file <script_redeemer> \
```

What this translates to is that this script will be executed three times (once for each grouping). But what if the script validates based off of the transaction context as a whole and not any individual UTxO? How can we use this "transaction level" script so that it is only executed once? There is no need to execute it more than once because the transaction context will be exactly the same for each execution. Another way to look at it is that we want a script to be able act like a payment skey where only one signature is needed no matter how many UTxOs are spent from the corresponding address.

This brings us to the problem: **The current design does not allow for a spending script to be executed only once no matter how many UTxOs are spent from the corresponding script address.** This is unfortunate since the eUTxO architecture allows writing such scripts. As a result, any time a developer writes a "transaction level" script, the script will be redundantly executed for each additional UTxO being spent from the script's address. These redundant executions are a waste of scarce resources and result in much higher fees for end users. **The current design prevents developers from using the full potential of the eUTxO.** 

### The Current Alternative
The alternative involves taking advantage of the fact that staking scripts do not suffer from the same limitation as spending scripts.

> Given a [spending] script **s**, you can turn it into a [spending] script **s'** that checks that 0 ADA is withdrawn from a [staking] script **s''** with the same logic as **s**. This is a transformation that is valid for any [spending] script.    -- @L-as

In a nut shell, you use a staking script **AS** a spending script. Here is how the above transaction example would look with this technique:

``` Bash
  --tx-in <first_script_utxo_to_be_spent> \
  --spending-tx-in-reference <script_ref_utxo> \
  --spending-plutus-script-v2 \
  --spending-reference-tx-in-inline-datum-present \
  --spending-reference-tx-in-redeemer-file <script_redeemer> \
  --tx-in <second_script_utxo_to_be_spent> \
  --spending-tx-in-reference <script_ref_utxo> \
  --spending-plutus-script-v2 \
  --spending-reference-tx-in-inline-datum-present \
  --spending-reference-tx-in-redeemer-file <script_redeemer> \
  --tx-in <third_script_utxo_to_be_spent> \
  --spending-tx-in-reference <script_ref_utxo> \
  --spending-plutus-script-v2 \
  --spending-reference-tx-in-inline-datum-present \
  --spending-reference-tx-in-redeemer-file <script_redeemer> \
  --withdrawal <staking_addr>+0 \
  --withdrawal-script-file <staking_script> \
  --withdrawal-redeemer-file <staking_redeemer>
```

There are three new `--withdrawal` lines at the end. The transaction level logic is in the staking script. Meanwhile, the spending script just checks that the required staking script is executed AND 0 ADA is withdrawn from the rewards address in the transaction.

The only requirement to use this trick is that the script address must have been created using the `s'` spending script and the `s''` staking script. The staking address DOES NOT need to actually have rewards or even be delegated for this trick to work.

With this method, the main computation is only executed once no matter how many UTxOs are spent from the script address.

#### The Drawbacks

1. This trick now means that everything requires two plutus scripts instead of just one. While the spending script can be made extremely small, this doesn't change the fact that two are now needed.
2. This trick DOES NOT stop the redundant executions; the spending script will still redundantly check if the required staking script was executed. This trick just minimizes the cost of the redundant executions by moving the heavy computation into a script that is only executed once per transaction.
3. This is not the intended use for staking scripts.

## Use Cases
Any time a spending script's result depends on the entire transaction and not on any particular UTxO.

1. P2P Atomic Swaps - within one transaction, the value entering the script address must be some proportion of the value leaving the script address
2. P2P Lending - within one transaction, the amount borrowed must be some proportion of the amount posted as collateral. Likewise, the amount of collateral reclaimed depends on how much of the loan has been repaid.
3. DAOs
4. Multisig applications that require more complex logic than what is possible with native scripts

## Goals
1. Stop redundantly executing spending scripts.
2. Do not remove the option to allow script execution per UTxO. There are still cases where the script should validate based off individual UTxOs. Also, there could be cases where this option is more efficient than having to traverse the transaction's context to get the relevant datum. An example of this latter case is when only one UTxO is consumed from a script address.
3. Try to use the ledger as is. The way scripts are stored onchain should not change unless absolutely necessary.
4. Try to leave the developer experience as untouched as possible. We don't want to make developers re-learn plutus.
5. Do not add too much new overhead to already resource constrained plutus scripts.

## Open Questions
1. Would this require a hardfork?
2. Would this require a new version of plutus?