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
# CPS-XXXX: Spending Script Redundant Executions

## Abstract
Spendings scripts are currently executed once for every UTxO being consumed from a script address. However, there are use cases where the validity of the transaction depends on the transaction as a whole and not on any individual UTxO. The eUTxO architecture allows a spending script to see the entire transaction context which means it is already possible to create scripts that validate based on the transaction as a whole. As of now, spending scripts that do this are forced to be executed once per UTxO even if these extra executions are completely redundant. Not only does this waste computational resources, but it can also result in the transaction fee growing quickly based on the number of UTxOs being consumed from the relevant script address. There is a technique that can be used to minimize this limitation but it has its own drawbacks. 

## Problem
Imagine a scenario where Alice would like to trustlessly swap assets with Bob. An atomic swap contract is used and any UTxOs that are to be swapped contain an inline datum of an asking price. Here is a table to represent all of Alice's available UTxOs to swap (at the atomic swap script address):

|UTxO ID| Asking Price|Amount|
|--|--|--|
| 1 | 1.5 DUST/ADA | 10 ADA |
| 2 | 2 DUST/ADA | 20 ADA |
| 3 | 1 DUST/ADA | 5 ADA |

If Bob wants to swap his DUST for Alice's ADA, he will need to satisfy Alice's asking price. As an example, if he wants to take all 10 ADA from UTxO 1, he will need to deposit 15 DUST to Alice's atomic swap address in the same transaction that consumes UTxO 1.

But what if he wants to swap his DUST for 25 ADA? That would require using at least two of Alice's UTxOs. Doing this is trivial for the atomic swap contract because it validates based off of the transaction as a whole: 

``` Txt
The value being deposited to the swap address must be >= 
  the value withdrawn from the swap address * 
  the weighted average asking price of all UTxOs being spent from the swap address
```

This brings us to the problem: **there is currently no way to efficiently use a spending script that validates based off of the transaction as a whole**. (These scripts will be called "transaction level spending scripts" for the rest of this CPS). With the current design of Cardano, if Bob consumed UTxO 2 and UTxO 3 in the same transaction to satisfy his desire for 25 ADA, the atomic swap contract will be executed twice. Since the transaction context doesn't change between executions, the second execution is completely redundant.

Any time a developer creates a transaction level spending script, it will be redundantly executed for every additional UTxO consumed from the corresponding script address. These redundant executions are a waste of scarce resources and result in much higher fees for end users. Not only that, but the inability to efficiently use these transaction level spending scripts significantly handicaps the use of the eUTxO model. The eUTxO model already allows for creating such spending scripts; developers are just unable to properly use them.

### The Current Alternative
The alternative involves taking advantage of the fact that staking scripts do not suffer from the same limitation as spending scripts.

> Given a [spending] script **s**, you can turn it into a [spending] script **s'** that checks that 0 ADA is withdrawn from a [staking] script **s''** with the same logic as **s**. This is a transformation that is valid for any [spending] script.    -- @L-as

In a nut shell, you use a staking script **AS** a spending script. The transaction level logic would be in the staking script. Meanwhile, the spending script just checks that both the required staking script is executed AND 0 ADA is withdrawn from the rewards address within the transaction. The withdrawal of the 0 ADA is necessary to force the staking script to be executed.

The only requirement to use this technique is that the script address must have been created using the `s'` spending script and the `s''` staking script. The staking address DOES NOT need to actually have rewards or even be delegated for this technique to work.

With this method, the main computation is only executed once no matter how many UTxOs are spent from the script address.

#### The Drawbacks

1. This technique now means that everything requires two plutus scripts instead of just one. While the spending script can be made extremely small, this doesn't change the fact that two are now needed.
2. This technique DOES NOT stop the redundant executions; the spending script will still redundantly check if the required staking script was executed. This trick just minimizes the cost of the redundant executions by moving the heavy computation into a script that is only executed once per transaction.
3. This is not the intended use for staking scripts.

## Use Cases
Any time a spending script's validation depends on the entire transaction and not on any particular UTxO.

1. P2P Atomic Swaps - within one transaction, the value entering the swap address must be some proportion of the value leaving the swap address
2. P2P Lending - within one transaction, the amount borrowed must be some proportion of the amount posted as collateral. Likewise, the amount of collateral reclaimed depends on how much of the loan is repaid.
3. DAOs
4. Multisig - within one transaction, the multisig threshold must be met

## Goals
1. Stop redundantly executing transaction level spending scripts.
2. Do not remove the option to allow script execution per UTxO. There are still use cases where the script should validate based off individual UTxOs. Also, there could be cases where this option is more efficient than having to traverse the transaction's context to get the relevant datum. An example of this latter case is when only one UTxO is consumed from a script address.
3. Try to use the ledger as is. The way scripts are stored onchain should not change unless absolutely necessary.
4. Try to leave the developer experience as untouched as possible. We don't want to make developers re-learn plutus.
5. Do not add too much new overhead to already resource constrained plutus scripts.

## Open Questions
1. Would this require a hardfork?
2. Would this require a new version of plutus?