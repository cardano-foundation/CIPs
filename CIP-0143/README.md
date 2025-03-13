---
CIP: 143
Title: Interoperable Programmable Tokens
Category: Tokens
Status: Inactive (incorporated into candidate CIP-0113)
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

### Programmable Logic Minting Policy

The `mkProgrammableLogicMinting` smart contract is responsible for the minting and issuance of new programmable tokens. Additionally, the contract ensures that an entry is added to the onchain directory linked list that permenantly associates the issued programmable token with its transfer script logic and issuer script logic. 

```haskell
mkProgrammableLogicMinting :: 
    Credential -- Minting logic credential
    -> ScriptContext 
    -> ()  
mkProgrammableLogicMinting mintingLogicCred = ... 
```

The contract accepts a single parameter, *mintingLogicCred* that defines the specialized the minting logic for the programmable token. `mintingLogicCred` must be a `ScriptCredential` of a [withdraw-zero rewarding script](https://github.com/Anastasia-Labs/design-patterns/blob/main/stake-validator/STAKE-VALIDATOR-TRICK.md).

#### Supported Actions

The minting policy supports two actions:

##### Token Registration (`PRegisterPToken`)

- Enforces that an immutable entry for the programmable token is inserted into the programmable token directory.
- The directory entry associates the programmable token with a transfer logic script and a issuer logic script.
  - The transfer logic script is a withdraw-zero script that must be invoked in every user transaction that spends the programmable token.
  - The issuer logic script is a withdraw-zero script that must be invoked in every permissioned transaction that spends the programmable token.
    - A permissioned action is an action that can only be performed by the token issuer, that bypasses the normal transfer logic of the system. An example is seizure / clawbacks which allow the issuer of a programmable token to reclaim the token from any UTxO at their discretion. 
- Enforces that only a single new type of programmable token is issued in the transaction.
- Enforces that all minted programmable tokens must be sent to the `programmableLogicBase` contract. 
- Enforces that the `mintingLogicCred` script is executed in the transaction see [the withdraw-zero trick](https://github.com/Anastasia-Labs/design-patterns/blob/main/stake-validator/STAKE-VALIDATOR-TRICK.md) 

##### Token Minting/Burning (`PMintPToken`)

- Responsible for validating the minting / burning of programmable tokens.
- If this action is used to mint programmable tokens, then it enforces that all minted programmable tokens must be sent to the `programmableLogicBase` contract.
- Enforces that the `mintingLogicCred` script is executed in the transaction see [the withdraw-zero trick](https://github.com/Anastasia-Labs/design-patterns/blob/main/stake-validator/STAKE-VALIDATOR-TRICK.md)

### Programmable Logic Base Script

The `mkProgrammableLogicBase` is a spending script that manages the ownership and transfer of programmable tokens. The `mkProgrammableLogicBase` script forwards its logic to the `mkProgrammableLogicGlobal` via [the withdraw-zero trick](https://github.com/Anastasia-Labs/design-patterns/blob/main/stake-validator/STAKE-VALIDATOR-TRICK.md). The `mkProgrammableLogicGlobal` script is responsible for ensuring that programmable tokens must always remain within the `mkProgrammableLogicBase` script and that the associated `transferLogicScript` is invoked (or  in the case of a permissioned action, that the associated `issuerLogicScript` is invoked) for each unique programmable token spent.

#### Ownership Mechanism

The system enforces that programmable tokens must all reside at the `mkProgrammableLogicBase` script. As such the payment credential of any UTxO that contains programmable tokens will always be the `mkProgrammableLogicBase` script credential. This system leverages staking credentials to identify and manage ownership. This approach ensures that programmable tokens remain secure and can only be transferred by their rightful owners. The owner of a UTxO at the `mkProgrammableLogicBase` script is determined by its staking credential. If the UTxO's staking credential is a public key credential, then any transaction that spends that UTxO must be signed by the public key; the system refers to all such required signatures in a transaction as the transaction's required public key witnesses. If the UTxO's staking credential is a script credential then the associated script must be invoked in the transaction via [the withdraw-zero trick](https://github.com/Anastasia-Labs/design-patterns/blob/main/stake-validator/STAKE-VALIDATOR-TRICK.md); we refer to all such required scripts as the transaction's required script witnesses.

#### Supported Actions

The `mkProgrammableLogicGlobal` (and thus the `mkProgrammableLogicBase`) supports two actions:

```haskell
data ProgrammableLogicGlobalRedeemer
  = PTransferAct
      { proofs :: [PTokenProof]
      }
  | PSeizeAct
      { seizeInputIdx :: Integer
      , seizeOutputIdx :: Integer
      , directoryNodeIdx :: Integer
      }
```

Where `PTokenProof` is defined as,
```haskell
data PTokenProof
  = PTokenExists { nodeIdx :: Integer }
  | PTokenDoesNotExist { nodeIdx :: Integer }
```

##### Transfer Action (`PTransferAct`)
- Traverse the transaction inputs and compute the sum of all value spent from the `mkProgrammableLogicBase` script, which we refer to as the `totalValueSpent`.
  - Enforce that the required witness for each input is present in the transaction
      - If the staking credential of the input is a payment credential then the public key hash must be present in the transaction signatories.
      - If the staking credential of the input is a script credential then the associated script must be invoked in the transaction. 
- Simultaneously traverse the currency symbols in `totalValueSpent` and the `PTransferAct` proof list and compute the `totalProgrammableValueSpent` (value consisting of only programmable tokens).
  - If a proof for a given currency symbol, `currentSymbol`, is `PTokenExists { nodeIdx ... }` then the reference input indexed by `nodeIdx` must satisfy the following:
    - The reference input must be a valid programmable token directory node (i.e. it must contain a token with the `directoryNode` currency symbol).
    - It must be the correct directory node for `currentSymbol` (i.e. the currency symbol must be equal to the node's key).
    - The directory node's transfer logic script must be executed in the transaction.
    - Together, these conditions enforce that the `currentSymbol` is indeed a programmable token and that the `transferLogicScript` associated with the programmable token is executed. 
  - If a proof for a given currency symbol, `currentSymbol`, is `PTokenDoesNotExist { nodeIdx ... }` then the reference input indexed by `nodeIdx` must satisfy the following:
    - The reference input must be a valid programmable token directory node (i.e. it must contain a token with the `directoryNode` currency symbol).
    - The directory node's `key` must be lexographically less than the `currentSymbol` and the directory node's `next` must be lexographically greater than the `currentSymbol`. 
    - Together, these conditions enforce that the `currentSymbol` is not a programmable token. 
- Traverse the transaction outputs and compute `totalProgrammableValueProduced`, the sum of all value produced to the `mkProgrammableLogicBase` script.
- Enforce that the `totalProgrammableValueProduced` is greater than or equal to the `totalProgrammableValueSpent`.
  - This insures that programmable tokens always remain at the `mkProgrammableLogicBase` script.

##### Seize Action (`PSeizeAct`)
- Enforce that the transaction input indexed by `seizeInputIdx`, which we refer to as the `programmableTokenInput`, is a UTxO from the `mkProgrammableLogicBase` script.
- Enforce that there is only a single input from the `mkProgrammableLogicBase` script in the transaction.
- Enforce that the reference input indexed by `directoryNodeIdx`, which we refer to as the `indexedDirectoryNode`, is a valid directory node (i.e. it must contain a token with the `directoryNode` currency symbol).
- Enforce that the `issuerLogicScript` in the directory node is invoked in the transaction.
- Enforce the the transaction output indexed by `seizeOutputIdx`, which we refer to as the `programmableTokenOutput`, satisfies the following criteria:
  - The address of the `programmableTokenOutput` equal to the address of the `programmableTokenInput`.
  - The value in the `programmableTokenOutput` is equal to the value in the `programmableTokenInput` after filtering the currency symbol of the programmable token associated with the `indexedDirectoryNode` (the node's `key`).
  - The datum in the `programmableTokenOutput` is equal to the datum in the `programmableTokenInput`
  - Together these conditions enforce that the permissioned actions of a programmable token are limited in scope such that they can only be used to transfer the associated programmable token from UTxOs, and cannot be used to modify those UTxOs in any other manner. 

The system guarantees that each programmable token must have a transfer logic script (located in the associated directory node in the directory linked list). The transfer logic script for a programmable token is the smart contract that must be executed in every transaction that spends the programmable token. For example to have a stable coin that supports freezing / arrestability this script might require a non-membership merkle proof in a blacklist. This must be a staking script (or an observer script once CIP-112 is implemented), see 
[the withdraw-zero trick](https://github.com/Anastasia-Labs/design-patterns/blob/main/stake-validator/STAKE-VALIDATOR-TRICK.md) for an explanation.

This framework doesn't require custom indexers to find user / script UTxOs, instead they can be easily queried by all existing indexers / wallets. For example, to obtain all the smart tokens in a user's wallet you can construct a franken-address where the payment credential is the `mkProgrammableLogicBase` credential and the staking credential is the user's public key credential and then query this address (in the same way you would query any normal address). 

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
1. Each user gets their own programmable token address that can be easily derived their credentials.
2. Interoperability with existing dApps
3. Introduces no new risk / vulnerabilities into existing protocols
4. Doesn't require changes to the ledger
5. Smart tokens cannot be revoked by dApps that fail to follow the standard (unlike the CIP 68 case in which they can)
6. Very low effort (relative to the existing proposals) to implement and get it to production / mainnet adoption
7. Completely permissionless and natively interoperable with other smart tokens. IE anyone can mint their own smart tokens with their own custom logic and the correctness of their behavior will be enforced

## Path to Active

### Acceptance Criteria
- [x] Issuance of at-least one smart token via the proposed framework on the following networks:
  - [x] 1. Preview testnet
  - [x] 2. [Mainnet](https://cexplorer.io/asset/asset1dk6zekxuyuc6up56q7nkd7084k609k3gfl27n8/mint#data) 
- [x] End-to-end tests of programmable token logic including arrestability, transfer fees, and blacklisting. 
- [x] Finally, a widely adopted wallet that can read and display programmable token balances to users and allow the user to conduct transfers of such tokens. 

### Implementation Plan
- [x] Implement the contracts detailed in the specification. Done [here](https://github.com/input-output-hk/wsc-poc/tree/main/src/lib/SmartTokens).
- [x] Implement the offchain code required to query programmable token balances and construct transactions to transfer such tokens. Done [here](https://github.com/input-output-hk/wsc-poc/tree/main/src/lib/Wst/Offchain).

## Copyright
This CIP is licensed under [Apache-2.0](http://www.apache.org/licenses/LICENSE-2.0).
