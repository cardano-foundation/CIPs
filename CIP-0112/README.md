---
CIP: 112
Title: Observe Script Type
Status: Proposed
Category: Plutus
Authors:
    - Philip DiSarro <info@anastasialabs.com>
Implementors: []
Discussions: 
    - https://github.com/cardano-foundation/CIPs/pull/418/
Created: 2024-01-08
License: CC-BY-4.0
---

## Abstract
We propose to introduce a new Plutus scripts type `Observe` in addition to those currently available (spending, certifying, rewarding, minting, drep). The purpose of this script type is to allow arbitrary validation logic to be decoupled from any ledger action. 
Since observe validators are decoupled from actions, you can run them in a transaction without needing to perform any associated action (ie you don't need to consume a script input, or mint a token, or withdraw from a staking script just to execute this validator). 
Additionally, we propose to introduce a new assertion to native scripts that they can use to check that a particular script hash is in `required_observers` (which in turn enforces that the script must be executed successfully in the transaction). This addresses a number of technical issues discussed in other CIPs and CPS such as the redundant execution of spending scripts, and the inability to effectively use native scripts in conjunction with Plutus scripts. 

## Motivation: Why is this CIP necessary?
Often in a plutus validator you want to check "a particular (different) Plutus script checked this transaction", but it's annoying (and wasteful) to have to have to lock an output in a script and then check if that output is consumed, or mint a token, or whatever else just to trigger script validation. 

Currently the main design pattern used to achieve this is a very obscure trick involving staking validators and the fact that you can withdraw 0 from a staking validator to trigger the script validation. A summary of the trick is:
Implement all the intended validation logic in a Plutus staking validator, we will call this validator `s_v`. To check that this validator was executed in the transaction you check if the credential of `s_v` (`StakingCredential`) is present in `txInfoWdrl`, this guarantees that `s_v` was checked in validation. 
This relies on the fact that unlike in `txInfoMint` the ledger does not filter out 0 amount entries in `txInfoWdrl`. This means that you are allowed to build transactions that withdraw zero from a staking credential which in-turn triggers the staking script associated with that credential to execute in the transaction,
which makes it available in `txInfoWdrl`. This is a enables a very efficient design pattern for checking logic that is shared across multiple scripts.

For instance, a common design pattern is a token based forwarding validator in which the validator defers its logic to another validator by checking that a state token is present in one of the transaction inputs:
```haskell
forwardNFTValidator :: AssetClass -> BuiltinData -> BuiltinData -> ScriptContext -> () 
forwardNFTValidator stateToken _ _ ctx = assetClassValueOf stateToken (valueSpent (txInfo ctx)) == 1
```
This pattern is common in protocols that use the batcher architecture. Some protocols improve on the pattern by including the index of the input with the state token in the redeemer:
```haskell
forwardNFTValidator :: AssetClass -> BuiltinData -> Integer -> ScriptContext -> () 
forwardNFTValidator stateToken _ tkIdx ctx =  assetClassValueOf stateToken (txInInfoResolved (elemAt tkIdx (txInfoInputs (txInfo ctx)))) == 1 

forwardMintPolicy:: AssetClass -> Integer -> ScriptContext -> () 
forwardMintPolicy stateToken tkIdx ctx =  assetClassValueOf stateToken (txInInfoResolved (elemAt tkIdx (txInfoInputs (txInfo ctx)))) == 1 
```
The time complexity of this validator is **O(n)** where n is the number of tx inputs. This logic is executed once per input being unlocked  / currency symbol being minted. 
The redundant execution of searching the inputs for a token is the largest throughput bottleneck for these DApps; it is **O(n*m)** where n is the number of inputs and m is the number of `forwardValidator` inputs + `forwardValidator` minting policies.
Using the stake validator trick, the time complexity of the forwarding logic is improved to **O(1)**. The forwardValidator logic becomes:
```haskell
forwardWithStakeTrick:: StakingCredential -> BuiltinData -> BuiltinData -> ScriptContext -> ()
forwardWithStakeTrick obsScriptCred tkIdx ctx = fst (head stakeCertPairs) == obsScriptCred 
  where 
    info = txInfo ctx 
    stakeCertPairs = AssocMap.toList (txInfoWdrl info)

stakeValidatorWithSharedLogic :: AssetClass -> BuiltinData -> ScriptContext -> () 
stakeValidatorWithSharedLogic stateToken _rdmr ctx = assetClassValueOf stateToken (valueSpent (txInfo ctx)) == 1
```
For the staking validator trick (demonstrated above), we are simply checking that the StakingCredential of the the staking validator containing the shared validation logic is in the first pair in `txInfoWdrl`. If the StakingCredential is present in `txInfoWdrl`, that means the staking validator (with our shared validation logic) successfully executed in the transaction. This script is **O(1)** in the case where you limit it to one shared logic validator (staking validator), or if you don't want to break composability with other staking validator, 
then it becomes **O(obs_N)** where `obs_N` is the number of Observe validators that are executed in the transaction as you have to verify that the StakingCredential is present in `txInfoWdrl`.

The proposed changes in this CIP enable this design pattern to exist indepedently from implementation details of stake validators and withdrawals, and improve efficiency and readability for validators that implement it. Furthermore, with the proposed extension to native scripts, we are able to completely get rid of the redundant spending script executions like so:
```haskell
observationValidator ::  AssetClass -> BuiltinData -> ScriptContext -> ()
observationValidator stateToken _redeemer ctx = assetClassValueOf stateToken (valueSpent (txInfo ctx)) == 1
```
We simply include the script hash of the above `observationValidator` in the `required_observers` field in the transaction body and we lock
all the UTxOs that we would like to share the same spending condition into the following native script:
```json
{
  "type": "observer",
  "keyHash": "OUR_OBSERVATION_SCRIPT_HASH"
}
```
The above solution (enabled by this CIP) is more clear, concise, flexible and efficient than the alternatives discussed above.

## Specification
The type signature of this script type will be consistent with the type signature of minting and staking validators, namely:
```haskell
Redeemer -> ScriptContext -> () 
```

The type signature of the newly introduced `Purpose` will be:
```haskell
Observe Integer -- ^ where integer is the index into the observations list.
```

### Script context

Scripts are passed information about transactions via the script context.
We propose to augment the script context to include information about the observation scripts that are executed in the transaction.

Changing the script context will require a new Plutus language version in the ledger to support the new interface.
The change is: a new field is added to the script context which represents the list of observers that must be present in the transaction. 

The interface for old versions of the language will not be changed.
Scripts with old versions cannot be spent in transactions that include observation scripts, attempting to do so will be a phase 1 transaction validation failure.

A new field will be introduced into the script context:

```haskell
-- | TxInfo for PlutusV3
data TxInfo = TxInfo
  { txInfoInputs                :: [V2.TxInInfo]
  , txInfoReferenceInputs       :: [V2.TxInInfo]
  , txInfoOutputs               :: [V2.TxOut]
  , txInfoFee                   :: V2.Value
  , txInfoMint                  :: V2.Value
  , txInfoTxCerts               :: [TxCert]
  , txInfoWdrl                  :: Map V2.Credential Haskell.Integer
  , txInfoValidRange            :: V2.POSIXTimeRange
  , txInfoSignatories           :: [V2.PubKeyHash]
  , txInfoRedeemers             :: Map ScriptPurpose V2.Redeemer
  , txInfoData                  :: Map V2.DatumHash V2.Datum
  , txInfoId                    :: V2.TxId
  , txInfoVotingProcedures      :: Map Voter (Map GovernanceActionId VotingProcedure)
  , txInfoProposalProcedures    :: [ProposalProcedure]
  , txInfoCurrentTreasuryAmount :: Haskell.Maybe V2.Value
  , txInfoTreasuryDonation      :: Haskell.Maybe V2.Value
  , txInfoObservations          :: [V2.Credential] -- ^ newly introduced list of observation scripts that executed in this tx. 
  }
```

### CDDL

The CDDL for transaction body will change as follows to reflect the new field.
```
transaction_body =
  { 0 : set<transaction_input>             ; inputs
  , 1 : [* transaction_output]
  , 2 : coin                               ; fee
  , ? 3 : uint                             ; time to live
  , ? 4 : certificates
  , ? 5 : withdrawals
  , ? 7 : auxiliary_data_hash
  , ? 8 : uint                             ; validity interval start
  , ? 9 : mint
  , ? 11 : script_data_hash
  , ? 13 : nonempty_set<transaction_input> ; collateral inputs
  , ? 14 : required_observers              ; Upgraded `required_signers`
  , ? 15 : network_id
  , ? 16 : transaction_output              ; collateral return
  , ? 17 : coin                            ; total collateral
  , ? 18 : nonempty_set<transaction_input> ; reference inputs
  , ? 19 : voting_procedures               ; Voting procedures
  , ? 20 : proposal_procedures             ; Proposal procedures
  , ? 21 : coin                            ; current treasury value
  , ? 22 : positive_coin                   ; donation
  }
; addr_keyhash variant is included for backwards compatibility and will be 
; deprecated in the future era, because `credential` already contains `addr_keyhash`.
required_observers = nonempty_set<credential / addr_keyhash>
```

We rename the `required_signers` field to `required_observers`, promoting it from a list of public key hashes to a list of credentials (i.e. either a KeyHash or ScriptHash). This is consistent with other parts of the transaction that are unlocked by a script or a key witness. `required_observers` (field 14) is a set of credentials that must be satisfied by the transaction. For public key credentials, if the corresponding signature is not in the witness set, the transaction will fail in phase 1. For script credentials, if the associated scripts is not present in the witness set or as a reference script and executed in the transaction, the transaction will fail in phase 1 validation. This way Plutus scripts can check the script context to know which observation scripts were executed in the transaction. Similarly, since native script conditions use the `required_observers` field, it is natural that they are now able to require that other scripts observed the transaction (an extension of the ability to check for the presence of key signatures). 

### Native Script Extension

The BNF notation for the abstract syntax of native scripts change as follows to reflect the new field.

```BNF
<native_script> ::=
             <RequireSignature>  <vkeyhash>
           | <RequireObserver>   <scripthash>
           | <RequireTimeBefore> <slotno>
           | <RequireTimeAfter>  <slotno>

           | <RequireAllOf>      <native_script>*
           | <RequireAnyOf>      <native_script>*
           | <RequireMOf>        <num> <native_script>*
```

Native scripts are typically represented in JSON syntax. We propose the following JSON representation for the `RequireObserver` constructor:
```JSON
{
  "type": "observer",
  "keyHash": "OBSERVATION_SCRIPT_HASH"
}
```


## Rationale: How does this CIP achieve its goals?

Currently Plutus scripts (and native scripts) in a transaction will only execute when the transaction performs the associated ledger action (ie. a Plutus minting policy will only execute if the transaction mints or burns tokens with matching currency symbol). The only exception is the withdraw zero trick which relies on an obscure mechanic where zero amount withdrawals are not filtered by the ledger. Now using `required_observers` we can specify a list of scripts (supports both native and Plutus scripts) to be executed in the transaction independent of any ledger actions. The newly introduced `txInfoObservations` field in the script context provides a straightforward way for scripts to check that "a particular script validated this transaction".

This change is not backwards-compatible and will need to go into a new Plutus language version.

### Alternatives 

- We could decide to accept the withdraw-zero staking script trick as an adequate solution, and just preserve the nonsensical withdraw zero case in future language versions. 
- The staking script trick could be abstracted away from the developer by smart contract languages that compile to UPLC. 
    - This can be dangerous since by distancing the developer from what is actually happening you open up the door for the developer to act on misguided assumptions. 

## Path to Active

### Acceptance Criteria
- [ ] These rules included within a official Plutus version, and released via a major hard fork.
      
### Implementation Plan
- [ ] Passes all requirements of both Plutus and Ledger teams as agreed to improve Plutus script efficiency and usability.
      
## Copyright
This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).

[CC-BY-4.0]: https://creativecommons.org/licenses/by/4.0/legalcode
[Apache-2.0]: http://www.apache.org/licenses/LICENSE-2.0
