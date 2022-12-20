---
CPS: ?
Title: Spending Scripts Can't Actualize the Full Potential of eUTxO
Status: Open
Category: Smart Contracts
Authors: 
  - fallen-icarus <modern.daidalos@gmail.com>
Proposed Solutions: []
Discussions:
  - https://github.com/cardano-foundation/CIPs/issues/417
Created: 2022-12-20
---

## Abstract
Spendings scripts are currently executed once for every UTxO being consumed from a script address. However, there are use cases where the validity of the transaction depends on the transaction as a whole and not on any individual UTxO. As of now, scripts are forced to be executed once per UTxO even if these extra executions are completely redundant. The eUTxO architecture allows a script to see the entire transaction information which means it is already possible to create scripts that validatre based on the transaction as a whole. The problem is that there is no way to use such a script without redundant executions. Not only does this waste computational resources, but it can also result in the transaction fee growing quadratically based on the number ot UTxOs being consumed from the relevant script address.

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
The second and third inputs are from the same script address. This particular script is a basic swap script that checks if the value being withdrawn from the script address is less than or equal to the value being deposited to the script address times a predefined ratio (the conversion rate between the two assets). The script itself passes or fails based on the entire transaction. The fact that two UTxOs are being consumed instead of one does not change the validity of the transaction. 

The problem is that, with the current design, this script is forced to be executed once for every UTxO being consumed from the script address. And since the validity depends on the transaction as a whole, which hasn't changed between executions, these extra executions are completely redundant. 

Being that my script checks all the inputs and outputs in the transaction to determine validity, below is the transaction fee estimation based on the number of UTxOs:
``` Txt
tx fee = # ref script executions * ( 0.3 ADA + 0.02 ADA * ( # input utxos + # output utxos ) )
``` 
The transaction fee increases linearly for every utxo (inputs + outputs) in the transaction, then quadratically if the reference script needs to be executed more than once.

## Use Cases
Any time a script's result depends on the entire transaction. The use cases I have personally encountered are:
1. Atomic Swaps
2. A multisig address where the owners want to withdraw more than one UTxO at a time

## Goals
1. Stop redundantly executing scripts.
2. Do not remove the option to allow script execution per UTxO. There could be cases where this option is more efficient than having to traverse the transaction information to get the relevant datum.
3. Try to use the ledger as is. The ways scripts are stored onchain should not change unless absolutely necesary.
4. Try to leave the developer experience as untouched as possible. We don't want to make developers re-learn things.
5. Allow backwards compatibility of scripts without opening up security holes.

## Open Questions
1. Would this require a hardfork?
2. Would this require a new version of plutus?

---
## Possible High-Level Solution
I am ignorant about certain lower-level implementation details but to the best of my knowledge, the following idea would not require a hardfork but would require a new version of plutus.

Scripts whos validation depends on the transaction as a whole will be referred to as tx-level scripts while scripts whos validation depends on an individual utxo will be referred to as utxo-level scripts.

I believe it is worth noting that minting scripts already function with the desired behavior. Consider this transaction:
``` Bash
cardano-cli transaction build \
  --tx-in fadae52f0323d7178c8116aa6adce31aba3ad6c561cbe5b31009251f742aa1bb#1 \
  --tx-out "$(cat ../../assets/wallets/01.addr) 2000000 lovelace + 1000 ${alwaysSucceedSymbol}.${tokenName}" \
  --tx-out "$(cat ../../assets/wallets/02.addr) 2000000 lovelace + 50 ${alwaysSucceedSymbol}.${tokenName}" \
  --mint "1050 ${alwaysSucceedSymbol}.${tokenName}" \
  --mint-script-file alwaysSucceedsMintingPolicy.plutus \
  --mint-redeemer-file unit.json \
  --tx-in-collateral af3b8901a464f53cb69e6e240a506947154b1fedbe89ab7ff9263ed2263f5cf5#0 \
  --change-address $(cat ../../assets/wallets/01.addr) \
  --protocol-params-file "${tmpDir}protocol.json" \
  --testnet-magic 1 \
  --out-file "${tmpDir}tx.body"
```
Here the minting script is only executed once despite minting occurring in two different outputs. At a high level, minting scripts are written like this:
``` Haskell
-- | minting policy before being compiled to plutus
mkMintPolicy :: Redeemer -> ScriptContext -> Bool
mkMintPolicy r ctx = ...
```
while spending scripts are written like this:
``` Haskell
-- | validator function before being compiled to plutus
mkValidator :: Datum -> Redeemer -> ScriptContext -> Bool
mkValidator d r ctx = ...
```
The fact that the spending script handles a datum while the minting script does not should immediately jump out. Taking inspiration from the fact that minting policies do not use datums (while also recognizing that spending scripts do), I propose the following high level change to the way spending scripts are written:
``` Haskell
-- | new validator function before being compiled to plutus
mkValidator :: Maybe Datum -> Redeemer -> ScriptContext -> Bool
mkValidator Nothing r ctx = {- the case where the script can be used at a transaction level -}
mkValidator (Just d) r ctx = {- the case where the script can be used at the utxo level -}
```
Then the basic cardano-cli usage would be (re-using my swap transaction example):
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
I removed the `spending-tx-in-reference` lines and added `tx-level-spending-tx-in-reference` and `tx-level-spending-reference-tx-in-redeemer-file` after `change-address`. If validation needs to be done at the utxo-level, the original `spending-tx-in-reference` lines can still be used.

When the spending script is used with the `tx-level-reference-script` option, `Nothing` is passed in for the `Maybe Datum`. On the other hand, when `spending-tx-in-reference` is used like usual, the datum will be parsed and passed with the `Just`. This way the code explicitly handles both the tx-level case and the utxo-level case.

The above cardano-cli example also uses a difference version of plutus. This seems required since previous versions do not use a `Maybe Datum`.

Using this technique, it would also be theoretically possible to spend a utxo at a script address even if it doesn't have a datum attached. This assumes the script can be used at the transaction level.

### What if a malicious entity forcibly passes in the wrong version of the datum (`Nothing` when it should be `Just d` or vice versa)?
 The script logic can be written to account for this so I argue it is up to the developer to defend against this kind of attack. A simple error message when the wrong version is used could suffice for most use cases. For my use case, the code would be:
``` Haskell
mkValidator :: Maybe Datum -> Redeemer -> ScriptContext -> Bool
mkValidator (Just _) _ _ = traceError "Not meant to be used at the utxo level"  -- ^ I don't want the script used in this case
mkValidator Nothing r ctx = {- do what I want -}
```

### Can multiple transaction level scripts be used in one transaction?
I don't see why not. The node is capable of detecting if all relevant scripts are present in the transaction. The transaction would only be valid if all necessary scripts succeed. 
