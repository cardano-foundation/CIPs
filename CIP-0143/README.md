---
CIP: 143
Title: Interoperable Programmable Tokens
Category: Tokens
Status: Proposed
Authors:
    - Philip DiSarro <philipdisarro@gmail.com>
Implementors: []
Discussions:
    - https://github.com/cardano-foundation/CIPs/pull/444
Created: 2024-12-3
License: Apache-2.0
---

## Abstract

This CIP proposes a robust framework for the issuance of interoperable programmable tokens on Cardano. Unlike all its predecessors, this framework allows these tokens to be used in existing dApps, and does not require dApps to be developed specifically for these tokens. 

## Motivation: why is this CIP necessary?

This CIP proposes a solution to Cardano Problem Statement 3 ([CPS-0003](https://github.com/cardano-foundation/CIPs/pull/382/files?short_path=5a0dba0#diff-5a0dba075d998658d72169818d839f4c63cf105e4d6c3fe81e46b20d5fd3dc8f)).

With this framework we achieve programmability over the transfer of tokens (meta-tokens) and their lifecycle without sacrificing composability with existing dApps. 

Answers to the open questions of CPS-0003:

1) How to support wallets to start supporting validators?

For every user address you can easily derive the equivalent smart token address. So to obtain a users total wallet balance including their programmable tokens, the wallet can query their programmable token address and their normal address and combine the two results.  

2) How would wallets know how to interact with these tokens? - smart contract registry?

For any given programmable token transfer, wallets can easily determine which stake script needs to be invoked (that contains the transfer logic) directly from the chain (no offchain registry required) by querying the original minting tx. 

3) Is there a possibility to have a transition period, so users won't have their funds blocked until the wallets start supporting smart tokens?

This framework will not cause any funds to be blocked. Transfers of non-programmable tokens will remain unaffected.

4) Can this be achieved without a hard fork?

Yes, this framework has been possible since the Chang hard fork. 

5) How to make validator scripts generic enough without impacting costs significantly?

The impact that the required script executions have on the cost of transactions is negligible.  


## Specification

### Smart Token Directory & Minting policy
This smart contracts is responsible for the minting / creation of new programmable tokens and for maintaining an merkle patricia forestry of all smart tokens and their respective transfer policies, we call this the `directoryRootHash`. 

```Haskell
-- directoryUTxO: a UTxO containing a state token NFT
--   address: ownScriptHash
--   value: ada <> directoryStateTokenNFT
--   datum: BuiltinByteString - the merkle patricia forestry root of the smart token directory

-- Script Logic:
--    enforces that all minted tokens must be sent to instantiations of a base parameter script (the `ProgrammableLogicBaseScript` contract)
--    enforces that an entry with the key as `ownCurrencySymbol`, and the value as the script hash of it's `transferLogicScript` must be inserted into the merkle root in the datum of the directoryUTxO.
--    Enforces that the transaction only mints tokens with `ownScriptHash` as their currency symbol in this transaction (no other tokens are minted).
```

Note that in this design there is only a single smart token directory UTxO. If we expect issuance of such token to be infrequent, then this is not an issue. However, if we expect issuance of programmable tokens to be a common occurrance than an [onchain linked list](https://github.com/Anastasia-Labs/plutarch-linked-list) data-structure should be used instead to prevent concurrency issues due to UTxO contention. In this case, each node on the linked list would contain the only Ada and a `nodeNFT` (which certifies that it is a valid linked list node, and as such the correctness of it's datum is enforced by the smart contract) and the datum of each node would contain:
```
data ProgrammableTokenDirectoryNode = ProgrammableTokenDirectoryNode
  { key :: CurrencySymbol 
  -- ^ Currency Symbol of the programmable token associated with this directory entry
  , next :: CurrencySymbol 
  -- ^ Currency Symbol of the programmable token associated with the next node in this directory.
  , transferLogicScript :: ScriptHash 
  -- ^ The transfer logic script that must be executed in every transaction that spends the programmable token associated with this directory entry. 
  }
```
In either case, there is only a single directory (a single directory UTxO / single directory linked list) for all programmable tokens.

### Transfer Logic Scripts
The system guarantees that each programmable token must have a transfer logic script (located in either the directory UTxO or the directory linked list depending on the implementation). The transfer logic script for a programmable token is the smart contract that must be executed in every transaction that spends the programmable token. For example to have a stable coin that supports freezing / arrestability this script might require a non-membership merkle proof in a blacklist. This must be a staking script (or an observer script once CIP-112 is implemented), see 
[the withdraw-zero trick](https://github.com/Anastasia-Labs/design-patterns/blob/main/stake-validator/STAKE-VALIDATOR-TRICK.md) for an explanation.

### Programmable Logic Base Script
This is a spending script that accepts 1 parameter, a credential which identifies the owner of the value that it locks.

```Haskell
-- Script Logic:
--   Enforces that the witness associated with the credential `cred` is present in the transaction.
--     If the Credential is a PubKeyCredential then the public key hash must be present in txInfoSignatories
--     If the Credential is a ScriptCredential then the script must be present in txInfoWithdrawals (ie the script must be invoked in the tx)
--   For all non-ada tokens in the Spending script (directory UTxO implementation) either:
--     a. A non-membership proof of the token in the `directoryRootHash` must be provided in the transaction (this proves that the token is not a programmable token)
--     b. A membership proof of the token in the `directoryRootHash` must be provided, and the associated `transferLogicScript` is present in `txInfoWithdrawals`.
--   For all non-ada tokens in the Spending script (onchain linked list directory implementation) either:
--     a. Two adjacent node UTxOs in the onchain directory linked list such that the key of one is lexographically less than the currency symbol of the token, and the other is
--        lexographically greater than the currency symbol of the token must be provided as reference inputs (this proves that the token is not a programmable token)        
--     b. The node UTxO in the onchain directory linked list associated with the currency symbol must be provided as a reference input, and the associated `transferLogicScript` is present --        in `txInfoWithdrawals`.
--    
--   Enforces that outputs containing programmable tokens must be instances of `ProgrammableLogicBaseScript` (this ensures that the system is closed and programmable tokens cannot be 
--   smuggled). If the destination of a programmable token is a `ProgrammableLogicBaseScript` parameterized by a non-script credential (public key hash / public key staking credential)
--   then the output UTxO must only contain ada and the programmable token. This ensures that if a user's programmable token is frozen or otherwise ineligible for transfer due to its
--   transfer logic script, it will not cause other unaffiliated tokens to be locked. Note that such situations are unavoidable for dApp protocols (freezing a token in a liquidity pool
--   will cause the pool to be inoperable), as such we do not impose this restriction on transfers to script based instances of `ProgrammableLogicBaseScript`.

mkProgrammableBaseScript :: Credential -> ScriptContext -> ()
mkProgrammableBaseScript cred ctx = ...
```

This framework doesn't require custom indexers to find user / script UTxOs, instead they can be easily queried by all existing indexers / wallets. For example, to obtain all the smart tokens in a user's wallet you can query their programmable token address (in the same way you would query any normal address). You can derive the user's programmable token address deterministically by applying their Credential to the `ProgrammableLogicBaseScript`.

## Rationale: how does this CIP achieve its goals?

The existing proposed frameworks for programmable tokens are:
1. Ethereum Account Abstraction (emulate Ethereum accounts via Plutus contract data)
2. Smart Tokens - CIP 113
3. Arrestable assets - CIP 125

The issue with all of the above is that they are not interoperable with existing dApps. Thus entirely new dApps protocols would need to be developed specifically for transacting with the proposed smart tokens. Furthermore, in some of the above CIPs, each smart-token enabled dApp must be thoroughly audited to ensure that it is a closed system (ie. there is no way for tokens to be smuggled to non-compliant addresses) and thus there needs to be a permissioned whitelist of which addresses are compliant.

Additionally, these proposed solutions attempt to maintain interoperability:
1. CIP 68 Smart Tokens
2. Transfer Scripts (ledger changes required)

The CIP 68 approach allows the tokens to be used anywhere but if the contract does not obey the logic then the token can be invalidated (ie revoked). So if you put it into a liquidity pool and the batcher does not obey the token logic then your tokens can be revoked and it wouldn't be your fault.
The transfer scripts proposal is to introduce a new Plutus script type that would need to be invoked in any transaction that spends a smart token (identified by the policy id). The issue with this approach is that it introduces a huge potential for vulnerabilities and exploits to the existing ledger and these vulnerabilities are responsible for the vast majority of exploits and centralization risks in ecosystems with fully programmable tokens (ie Ethereum). Regardless, this means that these tokens could not be used on existing dApps, since they would require a new Plutus version with new features, and the ledger does not allow contracts that use new features to co-exist in transactions with contract from previous versions where those features did not exist. 

Furthermore, all of the aforementioned proposals would require custom indexers and infrastructure to locate a user's (or smart contract's) programmable tokens. You could not simply query an address, instead you would need to query UTxOs from the contracts and check their datum / value (depending on the CIP) to determine the owner.

The above factors motivated the design of this framework. Some of the core unique properties of this framework include: 
1. Each users gets their own smart tokens address (that can be derived from staking keys, pub key hashes, and script hashes)
2. Interoperability with existing dApps
3. Introduces no new risk / vulnerabilities into existing protocols
4. Doesn't require changes to the ledger
5. Smart tokens cannot be revoked by dApps that fail to follow the standard (unlike the CIP 68 case in which they can)
6. Very low effort (relative to the existing proposals) to implement and get it to production / mainnet adoption
7. Completely permissionless and natively interoperable with other smart tokens. IE anyone can mint their own smart tokens with their own custom logic and the correctness of their behavior will be enforced


## Path to Active

### Acceptance Criteria
Issuance of at-least one smart token via the proposed framework on the following networks:
1) Preview testnet
2) Mainnet

End-to-end tests of programmable token logic including arrestability, transfer fees, and blacklisting. 

Finally, a widely adopted wallet that can read and display programmable token balances to users and allow the user to conduct transfers of such tokens. 

### Implementation Plan
Implement the contracts detailed in the specification, and implement the offchain code required to query programmable token balances and construct transactions to transfer such tokens. 


## Copyright
This CIP is licensed under [Apache-2.0](http://www.apache.org/licenses/LICENSE-2.0).
