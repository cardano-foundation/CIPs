---
CIP: ?
Title: Tag / Redeemer field in TxOut
Category: Plutus
Status: Proposed
Authors:
    - Philip DiSarro <info@anastasialabs.com>
Implementors: N/A
Discussions:
    - https://plutus.readthedocs.io/en/latest/reference/writing-scripts/common-weaknesses/double-satisfaction.html
    - https://github.com/cardano-foundation/CIPs/pull/735
Created: 2024-01-04
License: CC-BY-4.0
---

## Abstract
We propose to allow the attachment of arbitrary, temporary data to transaction outputs within the script context. This data, akin to redeemers in their operational context, is intended to be used exclusively during the execution of Plutus scripts and thus are not recorded by the ledger. This will facilitate a wide variety of smart contract design patterns, one of which can be used as a general solution for double satisfaction without sacrificing script composability.

## Motivation: why is this CIP necessary?
Often smart contract logic for most DApps involves associating arbitrary data with transaction outputs. Currently, there are a number of design patterns that are used to achieve this association, but each of these design patterns have significant drawbacks. The limitations of existing solutions have made a wide variety of DApps and design patterns infeasable in practice due to script budget constraints and high complexity of required code.  

One obvious use-cases for output tags is to prevent the double satisfaction problem. Currently, the most popular solution for double satisfaction is to include the `TxOutRef` of the input in the datum of the corresponding output and then when validating that the output correctly satisfies the spending conditions for the corresponding input the validator checks that the `TxOutRef` of the input matches the `TxOutRef` in the datum of the output. One issue with this solution to double satisfaction is that it breaks general composability since the output won't be able to contain datums used by other protocols (since the datum is already occupied by the TxOutRef of the corresponding input). Another issue with this approach is that this data permanently bloats the size of the chain even though it is only relevant during the execution of smart contracts. The only reason this data is stored in the datum is so that it can be accessed in the context of Phase 2 validation; the data is not actually relevant to future transactions and thus there is no real reason for it to be permenantly stored on the blockchain in UTxOs.

Other solutions involve enforcing that the index of the input in transaction inputs must correspond to the output at the same index of transaction outputs (ie `elemAt i txInfoInputs` corresponds to `elemAt i txInfoOutputs`. This really complicates transaction building, and often results in tons of fragmented UTxOs because the length of the `txInfoOutputs` list must be padded with filler UTxOs to match the indices of the required inputs. 

The addition of `blake2b_224` in Plutus V3 enabled another design pattern to associate arbitrary data with transaction outputs. This design pattern can be used to prevent double satisfaction without sacrificing script composability. With the new `blake2b_224` primitive, we are able to hash things to the same format as `ScriptHash` and thus in a roundabout way we can validate against the contents of a reference scripts (which can be associated to outputs via the reference script field). Through this, we can associate arbitrary data to outputs without sacrificing script composability:
```haskell
spendValidator :: BuiltinData -> Integer -> ScriptContext -> () 
spendValidator _ outIdx ctx = 
 let ownInputRefHash = blake2b_224 (appendByteString (appendByteString "0100004881" (blake2b_224 (serialiseData (txOutRef ownInput)))) "0001")
     Just ownOutputRefScriptHash = txOutReferenceScript ownOutput
  in traceIfFalse "Output does not correspond to own input" (ownInputRefHash == ownOutputRefScriptHash) 
 where
    ownInput :: TxInInfo
    ownInput = case findOwnInput ctx of
        Nothing -> traceError "wrong script type / own input not found"
        Just i  -> i
    
    ownOutput :: TxOut 
    ownOutput = elemAt outIdx (txInfoOutputs (txInfo ctx))
```
_Note: you must prepend the Plutus version to "0100004881" for the above to work in production._

When constructing a transaction to interact with the above validator we attach a reference script to each script output (for which we need to check correspondence). The reference script we attach is:
```lisp
(program 3.0.0 
    (con bytestring #TX_OUT_REF_HASH)
)
```
where `TX_OUT_REF_HASH` is the hash of the `TxOutRef` of the input for which this output corresponds to.  This trick offers a general solution to the double satisfaction problem but it doesn't solve the issues of dumping information that is only relevant during that one execution onto the chain forever. In-fact it only serves to exacerbate the issue, since we must store a reference script into the chain for each output that we want to associate arbitrary data to. 

If this CIP is adopted, the above validator could be simplified to:
```haskell
spendValidator :: BuiltinData -> Integer -> ScriptContext -> () 
spendValidator _ outIdx ctx = 
 let ownOutputTag = txOutTag ownOutput
  in traceIfFalse "Output does not correspond to own input" (ownOutputTag == txOutRef ownInput)
 where
    ownInput :: TxInInfo
    ownInput = case findOwnInput ctx of
        Nothing -> traceError "wrong script type / own input not found"
        Just i  -> i
    
    ownOutput :: TxOut 
    ownOutput = elemAt outIdx (txInfoOutputs (txInfo ctx))
```
The intention of the above contract is much clearer, the contract itself is more efficient, and associated transactions do not need to permanently add unwanted data to the chain (unlike the inline datum, reference script solutions). The tags can also be used more generally to convey information about the output to all the validators in the transaction (ie `tag = FullfilledSwapOrder` might signify that this is a fulfilled swap order from protocol XYZ or `tag = SignedOracleObservation BuiltinByteString Integer` might contain a signed message from an oracle that attests that the Value contained in the output is worth X USD).

We already have redeemers associated with each script to provide the smart contract with information that is only relevant during execution for similar reasons (ie redeemers allow us to associate arbitrary data with a script). This would be to TxOuts what Redeemers are for scripts, allowing us to associate arbitrary data (relevant only during Phase 2 validation) to outputs.

## Specification
We extend transaction witness set with a new list of arbitrary data associated with transaction outputs (`output_tags`).

### Script context

Scripts are passed information about transactions via the script context.
We propose to introduce a new field `tag` to the `TxOut`s in the script context.

```haskell
tag :: Maybe BuiltinData 
```

Changing the script context will require a new Plutus language version in the ledger to support the new interface. We propose the addition of a `tag` field to all the `TxOut` elements in `TxInfoOutputs` in the script context. This field will contain arbitrary data associated to the output that is relevant to Plutus validators during Phase 2 validation. 

The interface for old versions of the language will not be changed.
Scripts with old versions cannot be spent in transactions that include output tags, attempting to do so will be a phase 1 transaction validation failure.

Note that for simplicity, we propose that the `tag` field in `TxOut`s in transaction inputs in the script context always be empty (ie set to `Nothing`). There are certainly use-cases where one might want to associate arbitrary data to inputs for use in Phase 2 validation; however these use-cases are few and far between compared to those for outputs. 



### Output tags in transaction witness set 

In keeping consistent with the design of redeemers, we propose to introduce this information into the witness set as redeemers are.

### CDDL

The CDDL for the transaction witness set will change as follows to reflect the new field.
```
transaction_witness_set =
  { ? 0: [* vkeywitness ]
  , ? 1: [* native_script ]
  , ? 2: [* bootstrap_witness ]
  , ? 3: [* plutus_v1_script ]
  , ? 4: [* plutus_data ]
  , ? 5: [* redeemer ]
  , ? 6: [* plutus_v2_script ]
  , ? 7: [* plutus_v3_script ]
  , ? 8: [* output_tag ] ; 
  }

output_tag = [ index: unit, data: plutus_data ]
```

Note that although we propose to add `tag` as a field to `TxOut`s in the script context, we don't actually put them there in the CDDL. This is because the purpose of `output_tag` is to hold arbitrary data that associated to the output that is only relevant in the context of evaluating Plutus validators during Phase 2 validation. This data is not meant to be stored in UTxOs. 

This means that when constructing the script context the ledger must add each the data in each `output_tag` to the `TxOut` at the matching index in the transaction outputs. If there is a compelling case to be made to introduce this tagging for `TxOut`s in the transaction inputs in the script context (ie to associate arbitrary data to transaction inputs during Plutus validator execution) then this can be extended to introduce a 9th field to the witness set `[* output_tag]` to contain the arbitrary data that the ledger can then associate with `TxOut`s in transaction inputs in the script context. 

## Rationale: how does this CIP achieve its goals?
<!-- The rationale fleshes out the specification by describing what motivated the design and what led to particular design decisions. It should describe alternate designs considered and related work. The rationale should provide evidence of consensus within the community and discuss significant objections or concerns raised during the discussion.

It must also explain how the proposal affects the backward compatibility of existing solutions when applicable. If the proposal responds to a CPS, the 'Rationale' section should explain how it addresses the CPS, and answer any questions that the CPS poses for potential solutions.
-->
The core idea of this proposal is to introduce a mechanism by which we can associate arbitrary data (that is only relevant during Phase 2 validation) with transaction outputs without sacrificing script composability or wastefully storing this data into the chain.  

There are a few possible alternatives for where to store the arbitrary data associated with outputs. 

#### 1: The transaction outputs

The most straightforward approach would be to add this information directly into the transaction outputs and modify the `transaction_output` CDDL accordingly:

```
post_alonzo_transaction_output =
  { 0 : address
  , 1 : value
  , ? 2 : datum_option ; datum option
  , ? 3 : script_ref   ; script reference
  , ? 4 : output_tag   ; plutus_data associated with this output
  }
```

The issue with this is that we don't actually want this data to be stored in UTxOs in the ledger, since it is never again relevant after Phase 2 validation. 

#### 2: A new output tags field in the script context

Another approach would be to add the following field to the script context:
```haskell
outputTags :: [ (Integer, BuiltinData) ]
```
The `Integer` represents the index of the output in the transaction outputs for which the data is associated to. The issue with this is that without any support for constant-time index lookup, iterating through this list in a plutus validator will eat into the script budget (ex-units/mem/size). This issue becomes especially bad when there are multiple validators that need to lookup the data associated with an output (or outputs) since the traversal of this list must be done redundantly across all such validators. One of the biggest efficiency improvements that DApps received in Plutus V2 was from the fact that Inline Datums made it no longer necessary to iterate through the datum map to find the datum associated with each output. If we went with this approach, we would be reintroducing that bottleneck which seems clearly undesirable. 


## Path to Active

### Acceptance Criteria
- [ ] These rules included within a official Plutus version, and released via a major hard fork.

### Implementation Plan
- [ ] Passes all requirements of both Plutus and Ledger teams as agreed to improve Plutus script efficiency and usability.

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
