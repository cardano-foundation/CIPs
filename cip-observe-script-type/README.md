---
CIP: ?
Title: Observe Script Type
Status: Proposed
Category: Plutus
Authors:
    - Philip DiSarro <info@anastasialabs.com>
Implementors: []
Discussions: []
Created: 2024-1-8
License: CC-BY-4.0
---


<!-- Existing categories:

- Meta     | For meta-CIPs which typically serves another category or group of categories.
- Wallets  | For standardisation across wallets (hardware, full-node or light).
- Tokens   | About tokens (fungible or non-fungible) and minting policies in general.
- Metadata | For proposals around metadata (on-chain or off-chain).
- Tools    | A broad category for ecosystem tools not falling into any other category.
- Plutus   | Changes or additions to Plutus
- Ledger   | For proposals regarding the Cardano ledger (including Reward Sharing Schemes)
- Catalyst | For proposals affecting Project Catalyst / the Jörmungandr project

-->

## Abstract
<!-- A short (\~200 word) description of the proposed solution and the technical issue being addressed. -->
We propose to introduce a new Plutus scripts type `Observe` in addition to those currently available e (spending, certifying, rewarding, minting, drep). The purpose of this script type is to allow arbitrary validation logic to be decoupled from any ledger action. 
Since observe validators are decoupled from actions, you can run them in a transaction without needing to perform any associated action (ie you don't need to consume a script input, or mint a token, or withdraw from a staking script just to execute this validator). 

## Motivation: why is this CIP necessary?
<!-- A clear explanation that introduces the reason for a proposal, its use cases and stakeholders. If the CIP changes an established design then it must outline design issues that motivate a rework. For complex proposals, authors must write a Cardano Problem Statement (CPS) as defined in CIP-9999 and link to it as the `Motivation`. -->
Often in a plutus validator you want to check "a particular Plutus script checked this transaction", but it's annoying (and wasteful) to have to have to lock an output in a script and then check if that output is consumed, or mint a token, or whatever else just to trigger script validation. 

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
With this pattern DApps are able to process roughly 12-30 forwardNFTValidator UTxO's  per transaction without exceeding script budget limitations.
The time complexity of this validator is **O(n)** where n is the number of tx inputs. This logic is executed once per input being unlocked  / currency symbol being minted. 
The redundant execution of searching the inputs for a token is the largest throughput bottleneck for these DApps; it is **O(n*m)** where n is the number of inputs and m is the number of `forwardValidator` inputs + `forwardValidator` minting policies.
Using the stake validator trick, the time complexity of the forwarding logic is improved to **O(1)**. The forwardValidator logic becomes:
```haskell
forwardWithStakeTrick:: StakingCredential -> BuiltinData -> BuiltinData -> ScriptContext -> ()
forwardWithStakeTrick obsScriptCred tkIdx ctx = fst (head stakeCertPairs) == obsScriptCred 
  where 
    info = txInfo ctx 
    stakeCertPairs = AssocMap.toList (txInfoWdrl info)
```
IE check that the StakingCredential is in the first pair in the `txInfoWdrl`.  This script is **O(1)** in the case where you limit it to one Observe script, or if you don't want to break composability with other Observe scripts, then it becomes** O(obs_N)** where `obs_N` is the number of Observe validators that are executed in the transaction.

This proposal just makes this design pattern indepedent from implementation details of stake validators and withdrawals, and improves efficiency and readability for validators that implement it. 

## Specification
<!-- The technical specification should describe the proposed improvement in sufficient technical detail. In particular, it should provide enough information that an implementation can be performed solely on the basis of the design in the CIP. This is necessary to facilitate multiple, interoperable implementations. This must include how the CIP should be versioned. If a proposal defines structure of on-chain data it must include a CDDL schema in it's specification.-->
The type signature of this script type will be consistent with the type signature of minting and staking validators, namely:
```haskell
Redeemer -> ScriptContext -> () 
```

The type signature of the newly introduced `Purpose` will be:
```haskell
Observe Integer -- ^ where integer is the index into the observations 
```

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
  , txInfoObservations          :: [ScriptHash] -- ^ newly introduced list of observation scripts that executed in this tx. 
  }
```

## Rationale: how does this CIP achieve its goals?
<!-- The rationale fleshes out the specification by describing what motivated the design and what led to particular design decisions. It should describe alternate designs considered and related work. The rationale should provide evidence of consensus within the community and discuss significant objections or concerns raised during the discussion.

It must also explain how the proposal affects the backward compatibility of existing solutions when applicable. If the proposal responds to a CPS, the 'Rationale' section should explain how it addresses the CPS, and answer any questions that the CPS poses for potential solutions.
-->

## Path to Active

### Acceptance Criteria
<!-- Describes what are the acceptance criteria whereby a proposal becomes 'Active' -->

### Implementation Plan
<!-- A plan to meet those criteria. Or `N/A` if not applicable. -->

## Copyright
<!-- The CIP must be explicitly licensed under acceptable copyright terms. -->

[CC-BY-4.0]: https://creativecommons.org/licenses/by/4.0/legalcode
[Apache-2.0]: http://www.apache.org/licenses/LICENSE-2.0
