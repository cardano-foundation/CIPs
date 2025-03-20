---
CIP: 148
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
We propose to allow the attachment of arbitrary, temporary data to transaction outputs within the script context. This data, akin to redeemers in their operational context, is intended to be used exclusively during the execution of Plutus scripts and thus are not recorded in the ledger state. This will facilitate a wide variety of smart contract design patterns, one of which can be used as a general solution for double satisfaction without sacrificing script composability.

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
The intention of the above contract is much clearer, the contract itself is more efficient, and associated transactions do not need to permanently add unwanted data to the ledger state (unlike the inline datum, reference script solutions). The tags can also be used more generally to convey information about the output to all the validators in the transaction (ie `tag = FullfilledSwapOrder` might signify that this is a fulfilled swap order from protocol XYZ or `tag = SignedOracleObservation BuiltinByteString Integer` might contain a signed message from an oracle that attests that the multi-asset value contained in the output is worth X USD).

We already have redeemers associated with each script to provide the smart contract with information that is only relevant during execution for similar reasons (ie redeemers allow us to associate arbitrary data with a script). This would be to transaction outputs what Redeemers are for scripts, allowing us to associate arbitrary data (relevant only during Phase 2 validation) to outputs.

Importantly, this CIP is not designed specifically as a solution to the double satisfaction problem / dApp composability problem. This is a general improvement to the smart contract platform on Cardano that enables a huge range of use-cases that are currently in-feasible. The core value add is the ability to associate arbitrary data with outputs without permanently writing that data to the UTxO set. Sure, it can be used to solve double satisfaction without sacrificing dApp composability (a property that is currently unique to this solution to DS); however, more generally it can be used to do things like tag specific outputs with the USD price of the multi-asset value they contain via a signed oracle message which is associated to the output via this `tag` field. It also could be used to index the location of relevant tokens within the output value map to make onchain token lookups **~O(1)** ; currently searching values is a very expensive and common operation, for instance if you need to find the total number of `pool_asset_a` in a DEX pool UTxO, or if you need to check for the presence of a some `state_thread_token`  (pretty much every dApp on Cardano). This is possible because the location of all tokens in the value of all outputs is known during transaction construction (nice property of deterministic transactions on Cardano), so you don't need to ever perform search on-chain (i.e. `valueOf`) instead we can just index the location of these tokens via the information in this `tag` field. So, when a contract comes across a `TxOut` with an `tag = 6` (index of state token) it could simply verify that the head of the 6th entry of the value map contains the state token (or provide two indices if it isn't the first token with that currency symbol in the value). 

Likewise this CIP is of critical importance to intent-based operations / smart contract account abstraction. Both of these involve expressing intent offchain which reduces the number of transactions required to execute a user action. For instance, right now when a user wants to interact with a DEX / orderbook they first must create their order (which conveys their intent i.e. to swap X asset A to Y asset B in DEX pool P, or to sell asset A for asset B at exchange rate of E on an orderbook) in a preliminary transaction, and then a second transaction is required to actually fulfil their request (i.e. batch process orders against the pool on an AMM DEX or match orders on an orderbook DEX), furthermore if you want to update your intent (ie. you want to swap your asset A for asset C instead of asset B or you want to increase slippage or update your sell price or even change the asset you are selling) all of these things will require an additional transaction (perhaps multiple). With this CIP, you can provide your intent as a signed message which in turns allows all aforementioned user operations to be fulfilled in a single transaction. The user doesn't need to submit and pay for a transaction to create a swap request / limit order, the instead they can just publicize a signed message that describes their intent (i.e. swap order with XYZ constraints) which can be consumed by dApps directly to allow them to spend funds from the account as long as they do so exactly as intended by the user (as described by the user's signed message). The user can then update their intent without performing a transaction by producing a new signed message that can then (with this CIP) be associated with the relevant input / outputs.

The core use-cases I have detailed so far are:
1. Intent-based operations / smart contract account abstraction
2. Convey general purpose information about the output to all the validators in the transaction (such that this information can be consumed by any validator, without any specific knowledge of the structure of the smart contract associated with this output). The format of this information can be established by standards.
3. Solution to the double satisfaction that does not sacrifice dApp composability.
4. Index relevant information within a TxOut that can be consumed by validators with specific knowledge of the purpose of this output (ie. for a DEX pool UTxO this might contain the index location of the `stateNFT` in the UTxO's Value)

The reason that redeemers can never truly serve this purpose, is because they contain information relevant to the execution of a specific script (and often completely irrelevant to any other scripts in the transaction). As such, even if the redeemer for a given script execution does indeed contain information that could be relevant to other scripts executing in the transaction, the other scripts will not be able to parse or understand that data (what part of the data is relevant to the execution of the given script, and what part of the data is relevant to a given output / other component of the transaction) without imposing some arbitrary standardization on the data-encoding of redeemers. Not only would such a standardization be incredibly inefficient (you would need to lookup the redeemer, parse the redeemer for the relevant portion of information, then find the corresponding information in the script context to which that information is associated), but it would be incredibly difficult to gain adoption for such a standardization since they have always been understood to be relevant only to the execution of the specific script and to other scripts with specific knowledge of that script, and as such different dApps have adopted vastly different encoding methods for redeemers (some redeemers are encoded as `BuiltinList`, as `Constr Integer [BuiltinData]`, as `B BuiltinByteString`, as `I Integer` and many other variants). 

To illustrate this concretely, imagine we try to use redeemers to tag outputs to address the double satisfaction problem, as follows:
```
utxo = UTxO
  [ (in0, fooScript: 10 Foo)
  , (in1, fooScript: 5 Foo)
  , (in2, barScript: 20 Bar)
  , (in3, 50 ADA)
  , (in4, 100 ADA)
  , (in5, 1000 ADA)
  ...
  ]
Tx
  { body = TxBody
    { inputs = [in0, in1, in2, in3, in4, in5]
    , outputs = [out0: 50 ADA, out1: 100 ADA, out2: 1000 ADA, out3: 15 Foo, out4: 20 Bar]
    }
  , wits = TxWits 
    { redeemers =
       [ (Redeemer (Spending in4), (Data [arg0, "Foo", out1], exUnits0)
       , (Redeemer (Spending in3), (Data [arg1, "Foo", out0], exUnits1)
       , (Redeemer (Spending in5), (Data [arg2, "Bar", out2], exUnits2)
       ]
    }
  }
```

The redeemer exists to provide information relevant to the execution of a specific script, as such it, it contains a format that is only comprehensible to the script itself. In the above example, `fooScript` and `barScript` can indeed view the redeemers list, but for `fooScript` to understand the redeemer of `barScript` it will need specific knowledge about the construction of that script, if the redeemer of a script is `BuiltinData` encoded in constructor format (ie. `Constr Index [BuiltinData]`) then the `fooScript` will need to know what field the fields in `barScript` mean to meaningfully interact with them (say it just searches for a `TxOutRef`, how can it know that the purpose of that `TxOutRef` is to uniquely identify the inputs? What if there are multiple input sources? What if a script uses `BuiltinData` encoded as `BuiltinList [BuiltinData]` instead of the constructor format?

More importantly though, is that because redeemers are specific to a given script execution, their information cannot be shared across all scripts in the transaction without extreme amounts of redundancy, security issues, and massive complexity. The purpose of this proposal is explicitly to provide a way to associate information to components of the transaction entirely decoupled from any individual script. Even in an ideal world, where we get every single script author to follow a standard that enforces the redeemer is encoded in constructor format, and that the first field in the constructor of any spending redeemer is encoded as `BuiltinList [BuiltinData]` that provides information relevant to components of the transaction, ie. identifies all the outputs that satisfy the spending conditions for that input, this still is completely infeasible. This is due to the fact that redeemers are all completely independent from each other, so `(Redeemer (Spending in4), (Data [arg0, "Foo", out1], exUnits0)` could claim that `out1` is the output that satisfies the spending conditions for `in4`, the input that script execution is validating, at the sime time, another redeemer, `(Redeemer (Spending in5), (Data [arg2, "Bar", out1], exUnits2)` could also claim that `out1` is the output being used to satisfy the spending conditions for `in5`, the input that its own script execution is validating. To use this to prevent double-satisfaction, because this information is not directly shared across all scripts executing in the transaction, for a given script execution to determine that no other script execution in the transaction is claiming the same output, it must traverse the entire redeemer list, parse each redeemer, and check that the claimed output does not match its own. Importantly, every single script input in the transaction must do the same, so if there are 40 script inputs, that would mean redundantly traversing the redeemers list 40 times, since the redeemers list contains a minimum of 40 elements (1 for each script input) that would mean traversing and parsing 1,600 redeemers, which is impossible due to Plutus budget constraints. This solution has a complexity of **O(n^2)**, quadratic complexity, which is absolutely awful. 

With tagging as proposed by this CIP, the information is shared across all script executions in the transaction, so there is no need to traverse anything, the information you need is directly in the relevant component of the transaction, so each spending script execution is responsible for checking only its own satifying outputs, in the above example of 40 script inputs and 40 satisfying outputs, this would mean zero redundant traversal. This solution has a complexity of **O(n)**, linear complexity, which is as efficient as possible. 

The above holds true not just for the double-satisfaction use-case, but for all other use-cases mentioned as-well. For instance, if we want to associate specific outputs with the USD price of the multi-asset value they contain via a signed oracle message, if redeemers are used and multiple script executions depend on the USD price of that outputs multi-asset value, there is no way to guarantee that all the scripts executions use the same signed oracle message, there could be two valid signed messages where the timestamp of the signed message is 30 seconds apart (and the USD value differs accordingly), this would cause unintended behavior in the composability of the scripts that are executing (if all the scripts use the same oracle provider, a user should not be able to choose whatever oracle signed message is favorable to each independent script execution). If instead a `tag` is used to associate this information to the output, because `tag` information is globally available to all executing scripts, this is not an issue at all, if the tag of an output has a oracle signed message of a given USD value for one script, it is guaranteed to be the same for all other scripts executing in the transaction.  

## Specification
We extend transaction body with a new field, a list of arbitrary data associated with components of the transaction (`tags`).

From a high level, this new field can be described as follows:
```haskell
data Purpose =
  Input
  | Output
  | Mint
  | Reward
  | Certifying

tags :: [(Int, Purpose, Tag)]
```

Although `tag` can be provided for any `Purpose`, their presence in the script context for now is limited to the `TxOut` type which is present in `txInfoInputs` and `txInfoOutputs`. This is subject to change in the future. 

### Script context

Scripts are passed information about transactions via the script context.
We propose to introduce `tag` to various components of the script context. For any given component of the script context, `tag` is entirely optional, so it can be empty, if defined then it represents arbitrary data associated to that component that is relevant to Plutus validators during Phase 2 validation. 

The `BuiltinData` representation of `tag` is a sum type equivalent to `Maybe` encoded in data representation. If a `tag` was provided in the transaction body, then the `BuiltinData` representation is `Constr 0 [BuiltinData]` (where the fields list consists of only one entry, the `plutus_data` provided by that tag in the transaction body). If a corresponding `tag` was not provided in the transaction body, then the `BuiltinData` representation is `Constr 1 []`. 

The new Plinth representation of `TxOut` proposed by this CIP is:
```haskell
data TxOut = TxOut
  { txOutAddress         :: Address
  , txOutValue           :: Value
  , txOutDatum           :: OutputDatum
  , txOutReferenceScript :: Maybe ScriptHash
  , txOutTag             :: Maybe BuiltinData
  }
  deriving stock (Show, Eq, Generic)
  deriving anyclass (NFData, HasBlueprintDefinition)
```

Changing the script context will require a new Plutus language version in the ledger to support the new interface. 

The interface for old versions of the language will not be changed. Scripts with old versions cannot be spent in transactions that include output tags, attempting to do so will be a phase 1 transaction validation failure.

### Transaction Body Modifications 

We propose to introduce tags as a new field into the transaction body.

### CDDL

The CDDL for the transaction body will change as follows to reflect the new field.
```
transaction_body = {0 : set<transaction_input>
                   , 1 : [* transaction_output]
                   , 2 : coin
                   , ? 3 : slot_no
                   , ? 4 : certificates
                   , ? 5 : withdrawals
                   , ? 7 : auxiliary_data_hash
                   , ? 8 : slot_no
                   , ? 9 : mint
                   , ? 11 : script_data_hash
                   , ? 13 : nonempty_set<transaction_input>
                   , ? 14 : required_signers
                   , ? 15 : network_id
                   , ? 16 : transaction_output
                   , ? 17 : coin
                   , ? 18 : nonempty_set<transaction_input>
                   , ? 19 : voting_procedures
                   , ? 20 : proposal_procedures
                   , ? 21 : coin
                   , ? 22 : positive_coin
                   , ? 23 : nonempty_set<output_tag>
                   }
output_tag = [ index: unit, purpose: redeemer_tag, data: plutus_data ]
```

## Rationale: how does this CIP achieve its goals?
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
