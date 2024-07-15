---
CIP: ????
Title: SpendMany script purpose 
Category: Plutus
Status: Proposed
Authors:
    - Matteo Coppola <m.coppola.mazzetti@gmail.com>
Implementors: 
    - 
Discussions:
    - 
Created: 2024-07-13
License: Apache-2.0
---

## Abstract

This CIP proposes to replace the current Spend purpose with another one called SpendMany, removing the need of computational waste and higher fees when a transaction validates multiple inputs coming from the same script.

SpendMany is executed only once for the whole transaction and it comes with 2 parameters:
- The current script hash
- The list of the indexes of the inputs that are being spent from this script  
The second parameter is used to easily identify all the current script inputs in the script Context.

As this change could take a while to be implemented, this CIP proposes also another quick workaround:
we add in the Context a Map<Hash, List<InputIndex>> where the keys are the transaction's script hashes and the values are lists containing the indexes of the Inputs that come from these scripts.

## Motivation: why is this CIP necessary?

After years of Cardano smart contract development and sharing the experience with different teams, we came to the conclusion that there's no smart contract - except for trivial cases - that needs to validate each script utxo separately.
Even when a single utxo must be validated, all the recent smart contracts allow composability, permitting multiple inputs from the same script to be validated in the same transaction. When this is done for each utxo separately, developers need to add important redundant security checks to avoid double spending vulnerabilities.

Additionally, most of the times, the smart contract should also validate conditions of the transaction as a whole, for example the validity range or the sum of the Values of all the Inputs.
Validating N inputs separately means wasting a lot of resources (computational and transaction fees) because these conditions must be checked N times.
To circumvent this and get more performant smart contracts, the development community came up with the "Withdraw Zero" trick, which consists in using a separated WithdrawFrom script that will be executed only once for the full transaction. While this is a dirty hack used to circumvent the current status of the validator specification, it also still requires to check that the WithdrawFrom script is present for each script Input, wasting resources.

These problems have been briefly discussed in CPS-0004.

It is therefore necessary to replace the existing Spend purpose with a new one that I called SpendMany.
The objective is to reduce the time complexity from O(n) to O(1) while keeping the development experience easy.
Please note that the name doesn't necessarily need to be changed, but here we will use SpendMany here to refer to these CIP changes.

The SpendMany purpose completely replaces the Spend purpose, because simply adding the new purpose would require extremely difficult changes in the ledger code and because, as discussed above, it covers 100% of the Spend validation use cases.

By using SpendMany we officially get rid of the need of using dirty hacks and unnecessary computation.

Even if it's not a dependency, this CIP works very well with the [CIP for Transaction Inputs as Unordered Set](https://github.com/cardano-foundation/CIPs/pull/758).

Even if this CIP looks as an alternative to [CIP-112](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0112), they can perfectly co-exist.

If the changes formalized by this CIP can't be implemented within a reasonable timeframe, I at least suggest to implement the following change: adding in the script Context a new field called inputIndexesByScriptHashes of type ```Map<Hash, List<Int>>``` where the keys are the transaction's script hashes and the values are lists containing the indexes of the Inputs that come from these scripts.
This change will allow to easily validate all the script inputs with either the CIP-112 or the already existing "Withdraw Zero" hack.

## Specification

The type signature of this script type will be the same of the usual Spend validator, except without any Datum, as it can be easily derived for each input, making the type signature the same of Minting and Staking validators:

```Redeemer -> ScriptContext -> () ```

The type signature of the newly introduced Purpose will be:

```SpendMany ByteArray List<Int>```

where:
- ByteArray is the current script hash
- List<Int> is the list of Input indexes that must be validated by this script. These are the usual inputs that would normally trigger the execution of Spend validation logic.

### Alternative workaround:
If SpendMany can't be implemented we should at least add the field inputIndexesByScriptHashes in the script Context :
```
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
  , inputIndexesByScriptHashes  :: Map ScriptHash [Haskell.Integer] -- ^ newly introduced list of inputs for each script 
  }
```

## Rationale: how does this CIP achieve its goals?

This CIP removes the need of unprofessional hacks to achieve whole-transaction validation while also achieving better computational efficiency.
A simple chnage of the Spend purpose in SpendMany can simplify the developer experience, giving visibility of all the inputs to validate at once.

### Alternatives
* We could decide to accept the withdraw-zero staking script trick as an adequate solution, and just preserve the nonsensical withdraw zero case in future language versions.
* [CIP-112](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0112) is a possible valid alternative, but makes the development experience more complicated and doesn't provide an easy list of all the inputs validated by the current validator.

## Path to Active

### Acceptance Criteria

- [ ] These rules included within a official Plutus version, and released via a major hard fork.

### Implementation Plan

- [ ] Passes all requirements of both Plutus and Ledger teams as agreed to improve Plutus script efficiency and usability.


## Copyright

This CIP is licensed under [Apache-2.0](http://www.apache.org/licenses/LICENSE-2.0).