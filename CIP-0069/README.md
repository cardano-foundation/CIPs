---
CIP: 69
Title: Script Signature Unification
Category: Plutus
Authors:
  - Maksymilian 'zygomeb' Brodowicz <zygomeb@gmail.com>
Implementors: N/A
Status: Active
Discussions:
  - https://github.com/cardano-foundation/CIPs/pull/321
Created: 2022-08-23
License: CC-BY-4.0
---

## Abstract

This CIP unifies the arguments given to all types of Plutus scripts currently available (spending, certifying, rewarding, minting) by removing the argument of a datum.

For a while now every builder, myself included have struggled with the mutual dependency issue (two validators that need to know each other's hash) when designing dapps and it is widely considered a substantial barrier to safe protocols and one that limits our design space considerably.

The exact change would be to have every validator take as argument the redeemer and then the script context. Datums, only relevant to locking validators would be able to be provided by either looking them up in the ScriptContext or by extending the `Spending` constructor of `TxInfo` to carry `(TxOutRef, Datum)`.

## Motivation: Why is this CIP necessary?

### Multi-purpose Scripts

As it stands the scripts being made on cardano often suffer this problem, and the tokens usually are made to be able to be minted at any time. This leads to further checks being made on the frontend and further fragilitiy of the systems we create. When a mutual dependency arises we are forced to choose which script gets to statically know what's the hash of the other, and which has to be provided 'during runtime'.

- Use Case 1: Minting validator checks datum given to spending validator. The spending validator requires the token be present as witness of the datum's correctness.

- Use Case 2 (taken from Optim's Liquidity Bonds): Unique NFT is minted to give a unique identifier to a loan, that then gets reused by Bond Tokens. The spending validators require that NFT be present.

- Use Case 3 (taken from Minswap's Dex V1): NFT is minted for the same reason as above. It allows a minting policy to later mint LP tokens with that unique id token name.

We see a similar pattern repeating over and over again as witnessed by dapp developers and auditors alike. By allowing the multi-purpose scripts (spending and any other) we increase the security of Cardano by giving us more confidence and allowing to design protocols that have their architecture driven by Cardano's features, not limited by Cardano's language.

This primarily manifests in the ability to use a single validator for both minting and spending but the proposed solution makes it possible to use one validator for any and all purposes at once.

### No Datum Spend Purpose

One of the major footguns of Plutus scripts is if a user sends to the script with a wrong or missing datum. This has happened in the case of the Nami wallet having a bug that caused the wrong address to be chosen. There are other instances of user error where they send from a CEX to a script address. A wrong datum can be handled by the Plutus scripts themselves by having an alternative execution branch if type does not match the expected datum type. But in the case of no datum the script is not run and fails in phase 1 validation. The other motivation of this CIP is to be able to create spend scripts that can handle the no datum case.

I see three major use cases when it comes to running spend scripts without datums:

- Use Case 1: A script that acts as a wallet for users. By having no datum spending the user can send directly from exchanges or have friends send to their smart contract wallet with no datum needed.

- Use Case 2: As a DAO treasury. The funds in this script would be controlled by a DAO and anyone can donate/contribute to the DAO without a datum.

- Use Case 3: Allow dApp protocols to have a claim or withdraw mechanism (similar to Ethereum for tokens sent to a contract without call) for claiming tokens sent without a datum.

I'd be remiss if I didn't mention CIP-0112 which has been expanded to improve native script capabilities to provide an alternative solution for use case 1 and 2. But for use case 3, CIP-0112 does not enable a "claim or withdraw mechanism" for contracts.

## Specification

### Removing the datum argument

All the script purposes have a form of ```Redeemer -> ScriptContext -> a``` except the Spending one. It has the following form: ```Datum -> Redeemer -> ScriptContext -> a```. This is enforced by the Cardano ledger.

We propose to make the following modification:

The signature of all scripts will be ```ScriptContext -> a```.
The `ScriptInfo` type is a union type with a variant for each script purpose.
It is the same as `ScriptPurpose`, except for the additional optional datum in spending scripts.

```haskell
-- | The context that the currently-executing script can access.
data ScriptContext = ScriptContext
  { scriptContextTxInfo     :: TxInfo
  -- ^ information about the transaction the currently-executing script is included in
  , scriptContextRedeemer   :: V2.Redeemer
  -- ^ Redeemer for the currently-executing script
  , scriptContextScriptInfo :: ScriptInfo
  -- ^ the purpose of the currently-executing script, along with information associated
  -- with the purpose
  }

-- | Like `ScriptPurpose` but with an optional datum for spending scripts.
data ScriptInfo
  = MintingScript V2.CurrencySymbol
  | SpendingScript V3.TxOutRef (Haskell.Maybe V2.Datum)
  | RewardingScript V2.Credential
  | CertifyingScript
      Haskell.Integer
      -- ^ 0-based index of the given `TxCert` in `txInfoTxCerts`
      TxCert
  | VotingScript Voter
  | ProposingScript
      Haskell.Integer
      -- ^ 0-based index of the given `ProposalProcedure` in `txInfoProposalProcedures`
      ProposalProcedure
```

The datum in `SpendingScript` is optional, which will allow the execution of spending scripts without a datum.
One more change will be needed on the ledger side in order to make the Datum optional for spending scripts.
The ledger UTXOW rule needs to be relaxed, this ledger rule checks if a utxo has an existing datum if the address's payment credential is a phase 2 validation script.

The ScriptPurpose type used in the Redeemers Map is left the same.
It is used to uniquely identify a Plutus script within a transaction.


## Rationale: How does this CIP achieve its goals?

Unifying of the script signature is a very elegant solution to the problem, streamlining the experience of developing on cardano.
It begs the question if it should be added as an argument to all validators, to further emphasize that fact.


This CIP turns all scripts into 1 arg scripts with a Script Context union type for each purpose.

### Backward compatibility

This change is not backward compatible; it must be introduced in a new Plutus language version.
Node code must be modified.

## Path to Active

### Acceptance Criteria

- [x] The change has been implemented in the Plutus codebase, integrated in the ledger and released through a hard-fork.
  - Included within the Chang #1 hardfork

### Implementation Plan

The Cardano Ledger and Cardano Plutus teams would need to implement this in following repositories:
  IntersectMBO/plutus
  IntersectMBO/cardano-ledger

The following languages that compile to uplc would need to update to support the new ScriptContext argument that
is passed in for the next Plutus Version:
Aiken
Helios
Opshin
Plu-ts
Plutarch
Scalus

## Copyright

This CIP is licensed under Apache-2.0
