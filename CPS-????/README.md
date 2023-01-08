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
Spendings scripts are currently executed once for every UTxO being consumed from a script address. However, there are use cases where the validity of the transaction depends on the transaction as a whole and not on any individual UTxO. The eUTxO architecture allows a spending script to see the entire transaction context which means it is already possible to create scripts that validate based on the transaction as a whole. As of now, spending scripts that do this are forced to be executed once per UTxO even if these extra executions are completely redundant. Not only does this waste computational resources, but it can also result in the transaction fee growing quickly based on the number ot UTxOs being consumed from the relevant script address. There is a trick that can be used to minimize this limitation but it has its own drawbacks. At the end of this CPS is a proposed solution that not only addresses these redundant executions but would also make it possible to spend script utxos that have missing/wrong datums.

## Problem
Consider the following transaction:
``` Bash
cardano-cli transaction build \
  --tx-in c1d01ea50fd233f9fbaef3a295ba607a72c736e58c9c9df588abf4e5009ad4fe#0 \
  --tx-in 622034715b64318e9e2176b7ad9bb22c3432f360293e9258729ce23c1999b9d8#2 \
  --spending-tx-in-reference 622034715b64318e9e2176b7ad9bb22c3432f360293e9258729ce23c1999b9d8#0 \
  --spending-plutus-script-v2 \
  --spending-reference-tx-in-inline-datum-present \
  --spending-reference-tx-in-redeemer-file $swapRedeemerFile \
  --tx-in 766555130db8ff7b50fc548cbff3caa0d0557ce5af804da3b993cd090f1a8c3a#1 \
  --spending-tx-in-reference 622034715b64318e9e2176b7ad9bb22c3432f360293e9258729ce23c1999b9d8#0 \
  --spending-plutus-script-v2 \
  --spending-reference-tx-in-inline-datum-present \
  --spending-reference-tx-in-redeemer-file $swapRedeemerFile \
  --tx-out "$(cat ../assets/wallets/01.addr) 2000000 lovelace + 300 c0f8644a01a6bf5db02f4afe30d604975e63dd274f1098a1738e561d.54657374546f6b656e0a + 0 c0f8644a01a6bf5db02f4afe30d604975e63dd274f1098a1738e561d.4f74686572546f6b656e0a" \
  --tx-out "$(cat ${swapScriptAddrFile}) + 4000000 lovelace + 0 c0f8644a01a6bf5db02f4afe30d604975e63dd274f1098a1738e561d.54657374546f6b656e0a + 250 c0f8644a01a6bf5db02f4afe30d604975e63dd274f1098a1738e561d.4f74686572546f6b656e0a" \
  --tx-out-inline-datum-file $swapDatumFile \
  --tx-in-collateral bc54229f0755611ba14a2679774a7c7d394b0a476e59c609035e06244e1572bb#0 \
  --change-address $(cat ../assets/wallets/01.addr) \
  --protocol-params-file "${tmpDir}protocol.json" \
  --testnet-magic 1 \
  --out-file "${tmpDir}tx.body"
```

The second and third inputs are from the same script address. This particular script is a basic atomic swap script that checks if the value being withdrawn from the script address is less than or equal to the value being deposited to the script address multiplied by a predefined ratio (the conversion rate between the two assets). The script itself passes or fails based on the entire transaction. The fact that two UTxOs are being consumed instead of one does not change the validity of the transaction. 

The problem is that, with the current design, this script is forced to be executed once for every UTxO consumed from the corresponding script address. And since the validity depends on the transaction as a whole, which hasn't changed between executions, these extra executions are completely redundant.

Being that the atomic swap script checks all the inputs and outputs in the transaction to determine validity, below is the transaction fee estimation with the current limitation:

``` Txt
tx fee = 0.3 ADA * #swap_ref_script_executions + 0.02 ADA * ( #input_utxos + #output_utxos)
``` 

As the equation shows, when the swap script must be exected once per UTxO, the fee can grow quite large very quickly. Meanwhile, if the redundant exectutions were not there, the fee would grow very slowly.

## The Trick To Minimize This Limitation
The trick involves taking advantage of the fact that staking scripts do not suffer from the same limitation as spending scripts.

> Given a [spending] script **s**, you can turn it into a [spending] script **s'** that checks that 0 ADA is withdrawn from a [staking] script **s''** with the same logic as **s**. This is a transformation that is valid for any [spending] script.    -- @L-as


In a nut shell, you use a staking script **AS** a spending script. Here is how the above transaction example would look with this trick:

``` Bash
cardano-cli transaction build \
  --tx-in c1d01ea50fd233f9fbaef3a295ba607a72c736e58c9c9df588abf4e5009ad4fe#0 \
  --tx-in 622034715b64318e9e2176b7ad9bb22c3432f360293e9258729ce23c1999b9d8#2 \
  --spending-tx-in-reference 622034715b64318e9e2176b7ad9bb22c3432f360293e9258729ce23c1999b9d8#0 \
  --spending-plutus-script-v2 \
  --spending-reference-tx-in-inline-datum-present \
  --spending-reference-tx-in-redeemer-file $swapRedeemerFile \
  --tx-in 766555130db8ff7b50fc548cbff3caa0d0557ce5af804da3b993cd090f1a8c3a#1 \
  --spending-tx-in-reference 622034715b64318e9e2176b7ad9bb22c3432f360293e9258729ce23c1999b9d8#0 \
  --spending-plutus-script-v2 \
  --spending-reference-tx-in-inline-datum-present \
  --spending-reference-tx-in-redeemer-file $swapRedeemerFile \
  --tx-out "$(cat ../assets/wallets/01.addr) 2000000 lovelace + 300 c0f8644a01a6bf5db02f4afe30d604975e63dd274f1098a1738e561d.54657374546f6b656e0a + 0 c0f8644a01a6bf5db02f4afe30d604975e63dd274f1098a1738e561d.4f74686572546f6b656e0a" \
  --tx-out "$(cat ${swapScriptAddrFile}) + 4000000 lovelace + 0 c0f8644a01a6bf5db02f4afe30d604975e63dd274f1098a1738e561d.54657374546f6b656e0a + 250 c0f8644a01a6bf5db02f4afe30d604975e63dd274f1098a1738e561d.4f74686572546f6b656e0a" \
  --tx-out-inline-datum-file $swapDatumFile \
  --withdrawal "$(cat ${stakingScriptAddrFile})+0" \
  --withdrawal-script-file $stakingScriptFile \
  --withdrawal-redeemer-file $swapRedeemerFile \
  --tx-in-collateral bc54229f0755611ba14a2679774a7c7d394b0a476e59c609035e06244e1572bb#0 \
  --change-address $(cat ../assets/wallets/01.addr) \
  --protocol-params-file "${tmpDir}protocol.json" \
  --testnet-magic 1 \
  --out-file "${tmpDir}tx.body"
```

There are three new `--withdrawal` lines. The logic for the atomic swap is in the staking script. The actual spending script just checks that the required staking script was executed AND 0 ADA was withdrawn from the reward address.

The only requirement to use this trick is that the swap address was created using the `s'` spending script and the `s''` staking script. The staking address DOES NOT need to actually have rewards or even be delegated for this trick to work.

With this method, the main computation is only executed once.

### The Drawbacks

1. This trick now means that everything requires two plutus scripts instead of just one. While the spending script can be made extremely small, this doesn't change the fact that two are now needed.
2. This trick DOES NOT stop the redundant executions; the spending script will still redundantly check if the required staking script was executed. This trick just minimizes the cost of the redundant executions by moving the heavy computation into a script that is only executed once per transaction.
3. This is not the intended use for staking scripts.

## Use Cases
Any time a spending script's result depends on the entire transaction and not on any particular UTxO.

1. P2P Atomic Swaps
2. P2P Lending
3. Certain DAO applications
4. Certain Multisig applications that require more complex logic than what is possible with native scripts

## Goals
1. Stop redundantly executing spending scripts.
2. Do not remove the option to allow script execution per UTxO. There are still cases where the script should validate based off individual UTxOs. Also, there could be cases where this option is more efficient than having to traverse the transaction's context to get the relevant datum. An example of this latter case is when only one UTxO is consumed from a script address.
3. Try to use the ledger as is. The way scripts are stored onchain should not change unless absolutely necessary.
4. Try to leave the developer experience as untouched as possible. We don't want to make developers re-learn plutus.
5. Do not add too much new overhead to already resource constrained plutus scripts.

## Open Questions
1. Would this require a hardfork?
2. Would this require a new version of plutus?

---
## Possible High-Level Solution
What follows is my high-level suggestion for how to solve this issue. As a bonus based on the way my solution would work, it would also become possible to spend script UTxOs that having missing/incorrect datums. To the best of my knowledge, this solution would not require a hardfork but would require a new version of plutus.

*Scripts whose validation depends on the transaction as a whole will be referred to as **tx-level scripts** while scripts whose validation depends on an individual utxo will be referred to as **utxo-level scripts**.*

In addition to staking scripts, minting scripts also already execute based off the transaction as a whole. At a high level, minting, staking, and spending plutus scripts are written like this:

``` Haskell
-- | minting policy before being compiled to plutus
mkMintingScript :: Redeemer -> ScriptContext -> Bool
mkMintingScript r ctx = ...

-- | Staking script before being compiled to plutus
mkStakingScript :: Redeemer -> ScriptContext -> Bool
mkStakingScript r ctx = ...

-- | Spending script before being compiled to plutus
mkSpendingScript :: Datum -> Redeemer -> ScriptContext -> Bool
mkSpendingScript d r ctx = ...
```

### Part 1
The first part of the solution involves changing the way spending scripts are written to this:

``` Haskell
-- | New spending script before being compiled to plutus
mkValidator :: Maybe Datum -> Redeemer -> ScriptContext -> Bool
mkValidator Nothing r ctx = {- the case where the script can be used at a transaction level -}
mkValidator (Just d) r ctx = {- the case where the script can be used at the utxo level -}
```

### Part 2
The second part involves **EXPLICITLY** telling the node which version to use. Here would be my atomic swap transaction using the transaction level version:

``` Bash
cardano-cli transaction build \
  --tx-in c1d01ea50fd233f9fbaef3a295ba607a72c736e58c9c9df588abf4e5009ad4fe#0 \
  --tx-in 622034715b64318e9e2176b7ad9bb22c3432f360293e9258729ce23c1999b9d8#2 \
  --spending-plutus-script-v3 \
  --spending-reference-tx-in-inline-datum-present \
  --tx-in 766555130db8ff7b50fc548cbff3caa0d0557ce5af804da3b993cd090f1a8c3a#1 \
  --spending-plutus-script-v3 \
  --spending-reference-tx-in-inline-datum-present \
  --tx-out "$(cat ../assets/wallets/01.addr) 2000000 lovelace + 300 c0f8644a01a6bf5db02f4afe30d604975e63dd274f1098a1738e561d.54657374546f6b656e0a + 0 c0f8644a01a6bf5db02f4afe30d604975e63dd274f1098a1738e561d.4f74686572546f6b656e0a" \
  --tx-out "$(cat ${swapScriptAddrFile}) + 4000000 lovelace + 0 c0f8644a01a6bf5db02f4afe30d604975e63dd274f1098a1738e561d.54657374546f6b656e0a + 250 c0f8644a01a6bf5db02f4afe30d604975e63dd274f1098a1738e561d.4f74686572546f6b656e0a" \
  --tx-out-inline-datum-file $swapDatumFile \
  --tx-in-collateral bc54229f0755611ba14a2679774a7c7d394b0a476e59c609035e06244e1572bb#0 \
  --change-address $(cat ../assets/wallets/01.addr) \
  --tx-level-spending-tx-in-reference 622034715b64318e9e2176b7ad9bb22c3432f360293e9258729ce23c1999b9d8#0 \
  --tx-level-spending-reference-tx-in-redeemer-file $swapRedeemerFile \
  --protocol-params-file "${tmpDir}protocol.json" \
  --testnet-magic 1 \
  --out-file "${tmpDir}tx.body"
```

I removed the `spending-tx-in-reference` and the `spending-reference-tx-in-redeemer-file` lines and added `tx-level-spending-tx-in-reference` and `tx-level-spending-reference-tx-in-redeemer-file` after `change-address`. 

Right after the actual script `tx-in`s are `--spending-plutus-script-v3` and `--spending-reference-tx-in-inline-datum-present`. Keeping the datum flags here allows for "mixing and matching" inline datums and datum hashes. On the other hand, it is okay to move the redeemer flag to the end since plutus would still assume all UTxOs from a script address to be using the same redeemer.

If validation needs to be done at the utxo-level, the original transaction can still be used (possibly with the `utxo-level` prefix attached) but the `spending-plutus-script-v2` flag would be changed to `spending-plutus-script-v3`. This seems required since previous plutus scripts do not use a `Maybe Datum`.

When the spending script is used with the `tx-level-reference-script` option, `Nothing` is passed in for the `Maybe Datum`. On the other hand, when `spending-tx-in-reference` is used like usual, the datum will be parsed and passed with the `Just`. This way the code explicitly handles both the tx-level case and the utxo-level case. Using this technique, there would be no need for an on-chain encoding of a missing datum. Theoretically, all UTxOs could now be consumed as long as the tx-level script logic is used. This includes UTxOs that have incorrect/missing datums.

### How will the node know if all required scripts are present?
The node is already capable of detecting whether all required witnesses are present.

### What if a malicious entity forcibly passes in the wrong version of the datum (`Nothing` when it should be `Just d` or vice versa)?
The script logic can be written to account for this so I argue it is up to the developer to defend against this kind of attack. A simple error message when the wrong version is used could suffice for most use cases. For my use case, the code could be:

``` Haskell
mkValidator :: Maybe Datum -> Redeemer -> ScriptContext -> Bool
mkValidator (Just _) _ _ = traceError "Not meant to be used at the utxo level"
mkValidator Nothing r ctx = {- do what I want -}
```

### Can multiple transaction level scripts be used in one transaction?
I don't see why not. The node is capable of detecting if all relevant scripts are present in the transaction. The transaction would only be valid if all necessary scripts succeed.

### How would the `Maybe Datum` be represented at a low-level?
(I do not know much about the low-level design of plutus so I could be way off with this part.)

I do not know if it is possible but perhaps the `Nothing` can be represented with an invalid de bruijn constructor value of (-1) like:

``` JSON
{"constructor":-1,"fields":[]}
```

All de bruijn indexes are supposed to be natural numbers so the (-1) is guaranteed to not be used for real datums. The idea is similar to using `undefined` in Haskell where it points to a thunk that is guaranteed to raise an exception. This invalid representation for `BuiltinData` would need to be hard-coded into plutus.
