---
CIP: 128
Title: Preserving Order of Transaction Inputs
Category: Ledger
Status: Proposed
Authors:
  - Jonathan Rodriguez <info@anastasialabs.com>
Implementors: []
Discussions:
  - https://github.com/cardano-foundation/CIPs/pull/758
Created: 2024-02-01
License: CC-BY-4.0
---


## Abstract

We propose the introduction of a new structure for transaction inputs aimed at enhancing the execution efficiency of Plutus contracts.

This CIP facilitates the preservation of input ordering from a submitted transaction, diverging from the current state where the ledger reorders transaction inputs lexicographically. Preserving the input ordering from a submitted transaction enables a validator to efficiently identify the required inputs in accordance with its validation logic, thus eliminating the need to use unnecessary computation by traversing all transaction inputs or performing sorting within the validator itself.

Furthermore, this implementation offers the potential to enhance existing design patterns already used in production, specifically by improving the ability to group and match inputs and outputs located at the specific index positions.

## Motivation: Why is this CIP necessary?

According to the Babbage CDDL [transaction_body](https://github.com/IntersectMBO/cardano-ledger/blob/master/eras/babbage/impl/cddl-files/babbage.cddl) , the inputs and reference inputs of a transaction body are represented as a set, which indicates the non-duplicate inputs. However, the ledger not only process the [transaction_inputs](https://github.com/IntersectMBO/cardano-ledger/blob/0274cf65dbb79773122b69dfd36a8299eec2783f/eras/babbage/impl/cddl-files/babbage.cddl#L75-L77) as a set , but also orders them lexicographically, first by `transaction_id` and then by `index`.

The primary issue with the ledger ordering inputs lexicographically is that validators must traverse all the inputs or sort them within the validator to find the required inputs for the validation logic. This process can lead to inefficiencies and increases the risk of exceeding the execution budget specially when processing a large set of inputs.

For instance, consider a spending validator that needs to access its own input and output. Each function described below necessitates traversing all inputs and outputs to fulfill such validation:

 ```haskell
findOwnInput :: ScriptContext -> Maybe TxInInfo
findOwnInput ScriptContext{scriptContextTxInfo=TxInfo{txInfoInputs}, scriptContextPurpose=Spending txOutRef} =
    find (\TxInInfo{txInInfoOutRef} -> txInInfoOutRef == txOutRef) txInfoInputs
findOwnInput _ = Nothing
 ```

 ```haskell
getContinuingOutputs :: ScriptContext -> [TxOut]
getContinuingOutputs ctx
    | Just TxInInfo{txInInfoResolved=TxOut{txOutAddress}} <- findOwnInput ctx =
        filter (f txOutAddress) (txInfoOutputs $ scriptContextTxInfo ctx)
    where
        f addr TxOut{txOutAddress=otherAddress} = addr == otherAddress
getContinuingOutputs _ = traceError "Lf" -- "Can't get any continuing outputs"
```

```haskell
validatorA :: BuiltinData -> BuiltinData -> ScriptContext -> Bool
validatorA _datum _redeemer context =
  validateWithInputOutput input output
  where
    Just (TxInInfo {txInInfoResolved = input}) = findOwnInput context
    [output] = getContinuingOutputs context
    validateWithInputOutput _ _ = True
```

Furthermore, preserving the order of inputs from the submitted transaction will facilitate the utilization of index redeemer patterns that many projects are transitioning to, as illustrated below.

```haskell
validatorIndex :: BuiltinData -> Integer -> ScriptContext -> Bool
validatorIndex _datum index ScriptContext {scriptContextTxInfo = txInfo, scriptContextPurpose = Spending txOutRef} =
  validateInputOutput input output && txOutRef == intxOutRef
  where
    inputs = txInfoInputs txInfo
    outputs = txInfoOutputs txInfo
    TxInInfo {txInInfoOutRef = intxOutRef, txInInfoResolved = input} = inputs P.!! index
    output = outputs P.!! index
    validateWithInputOutput _ _ = True
```

Given the deterministic nature of the extended UTXO model, the determination of inputs and outputs can already be achieved through the off-chain code, eliminating the necessity to find or traverse inputs and outputs within the validator.

## Specification
As per protocol specifications, the transaction body is structured as follows:

```
transaction_body =
  { 0 : set<transaction_input>    ; inputs
  , 1 : [* transaction_output]
  , 2 : coin                      ; fee
  , ? 3 : uint                    ; time to live
  , ? 4 : [* certificate]
  , ? 5 : withdrawals
  , ? 6 : update
  , ? 7 : auxiliary_data_hash
  , ? 8 : uint                    ; validity interval start
  , ? 9 : mint
  , ? 11 : script_data_hash
  , ? 13 : set<transaction_input> ; collateral inputs
  , ? 14 : required_signers
  , ? 15 : network_id
  , ? 16 : transaction_output     ; collateral return; New
  , ? 17 : coin                   ; total collateral; New
  , ? 18 : set<transaction_input> ; reference inputs; New
  }
```

Specifically, the inputs and reference inputs are currently represented as a set:
```
0 : set<transaction_input>    ; inputs
```
```
18 : set<transaction_input> ; reference inputs; New
```

The proposed solution suggests modifying the inputs representation to an `oset` type:
> An `oset` type behaves much like a `set` but remembers the order in which the elements were originally inserted. 
```
0 : oset<transaction_input>    ; inputs
```
```
18 : oset<transaction_input> ; reference inputs; New
```


## Rationale: How does this CIP achieve its goals?
The motivation behind this CIP stems from observed limitations and inefficiencies associated with the current lexicographical ordering of transaction inputs.

The strict lexicographical ordering mandated by the ledger requires traversing inputs to locate the appropriate inputs for the validation logic, which can lead to execution inefficiencies.

To address these issues, the proposed solution suggests transitioning from an `set` based representation of transaction inputs and reference inputs to an `oset` type, which preserves the order of elements.

This CIP tries to revive the original draft [CIP-0051](https://github.com/cardano-foundation/CIPs/pull/231)

### Alternatives
#### 1. Retain the existing set-based representation:

This approach involves maintaining the current set-based representation of transaction inputs and reference inputs.

## Path to Active

### Acceptance Criteria
- [ ] Included within a Plutus version within a Cardano mainnet hardfork.

### Implementation Plan
- [ ] Passes all requirements of both Plutus and Ledger teams as agreed to improve Plutus script efficiency.


## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
