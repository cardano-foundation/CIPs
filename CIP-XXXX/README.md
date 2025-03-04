---
CIP: ?
Title: Extensive Light Wallet Standard
Category: Wallets
Status: Proposed
Authors:
    - Vladimir Kalnitsky <vladimir@mlabs.city>
Implementors: []
Discussions:
    - https://github.com/cardano-foundation/cips/pulls/620
    - [Cardano Working Groups Discord server](https://discord.gg/XFjAzsQyaM)
Created: 2023-11-14
License: CC-BY-4.0
---

## Abstract
<!-- A short (\~200 word) description of the proposed solution and the technical issue being addressed. -->

This document describes a webpage-based communication bridge allowing dApps to interface with Cardano wallets. The interface extends CIP-30. Improvements over the original standard are:

- More data queries
- Interfaces that allow transaction building on the wallet side
- Use of JSON instead of CBOR

## Motivation: why is this CIP necessary?

### Existing problems of dApp development

CIP-30 is a universally accepted web-based wallet standard for Cardano. It provides a minimalistic interface that, in principle, can be used to build almost any kind of Cardano dApp. However, the way dApp<->wallet interaction is defined leads to suboptimal dApp architecture due to CIP-30 limits.

Consider the following problems:

#### Manual Transaction Building

On Cardano, the whole process of constructing transactions is delegated to the off-chain code. This process typically includes:

1. Fetching the data from the blockchain, using either CIP-30 interface, custom backend, or, most commonly, both
2. Determining the parameters (or constraints) the transaction should have using internal dApp logic
3. Constructing a skeleton of the transaction given data from the previous steps
4. Making the transaction structure valid for stage1 and stage2 of the validation process - balancing (making sum of outputs plus fees equal to sum of inputs), estimating execution units, and attaching script data (“datums”) and redeemers.
5. Serializing the transaction to CBOR format (commonly via cardano-serialization-lib)
6. Passing the serialized transaction for signature and submission

It is clear that steps 3, 4 and 5 are purely technical: most (however, not all) dApps would opt out of having to deal with these if only they could.

#### Use of CBOR representations

CIP-30 standard uses CBOR encoding for all data passed from the wallet, e.g. addresses and UTxOs. Interpreting this data within the app requires CBOR decoding functionality that is tedious to implement manually, and so users resort to using `cardano-serialization-lib` or its close alternative, `cardano-multiplatform-lib`, which both require loading a WebAssembly blob of >1M in size.

For comparison, to start a new Web3 app on Ethereum there is no need to use a library for data serialization. It’s possible to interact with a provider object that is given by the wallet directly, although there are libraries to further simplify this. Using CBOR looks unnecessary for most dApps, given that JSON is a de-facto standard for web data serialization.

#### Limited scope of available queries

Most dApps require interacting with scripts, which implies the need to query for available UTxOs locked at script addresses and other blockchain data. CIP-30 is intentionally limited in scope to management of UTxOs "owned" by the wallet itself.

Some other useful queries, like getting delegation and reward info, stake pool info, transaction metadata or contents, and epoch data, are also outside of scope.

As a result, dApp developers are forced to implement their own query layers on the backend side - which leads to one more problem - inconsistency between states of two query layers:

#### Inconsistency of Query Layers

On Cardano, every running node has its own opinion on the set of currently unspent transaction outputs. Only eventual consistency is guaranteed.

Any dApp that interacts with a CIP-30 wallet has to deal with the inconsistency between the local cardano-node-based query layer and the light wallet query layer, especially when dApp workflow involves sending multiple transactions with the wallet in quick succession.

Thus, the goal of the developers is to ensure that the set of UTxOs available to the wallet and the set of UTxOs the backend cardano-node knows about are synchronized enough to not cause errors when a wallet or backend operations are performed. To give a few examples of potential issues, consider the following scenarios:


- A dApp tries to balance a transaction with UTxOs from the wallet that is not yet available in dApp backend's cardano node, causing an error response during execution units evaluation
- A transaction is passed for signing, but the wallet does not yet know about the UTxOs it spends, and thus refuses to sign it
- A transaction is sent to the network via the dApp backend (bypassing CIP-30 submit method) and is confirmed there, but the wallet still does not know about its consumed inputs, and thus returns outdated data.

### Principles of this CIP

In order to build a well-thought standard, we must first establish our principles and then specify the APIs according to these principles, users' needs and the scope of the standard.

#### Layered control over transaction building

Different users require different levels of control over transaction building process, for reasons such as optimising fees, ensuring proper ordering of transaction inputs, or backwards compatibility.

There are three conceptual levels of control:

- **CL1.** transaction constraints level - the user only cares about particular requirements a transaction must satisfy in order to be valid in the context of the app, such as sending a certain amount to an address, consuming a UTxO, or submitting a stake delegation.
- **CL2.** transaction contents level - the user cares about particular details of transaction structure, such as number and contents of change outputs, or ordering of inputs.
- **CL3.** CBOR level - the user cares about cbor layout of the transaction, in particular, about key ordering in maps and definite/indefinite length serialization format of CBOR arrays

The goal of this standard is to satisfy the needs of everyone, however, we don't want to force the users who want to work on a high level to deal with lower levels of abstraction. This would be a major advantage over CIP-30, that delegates transaction building to the user completely.

However, we also don't aim at providing a more *restrictive* interface. Providing a single high-level interface would not be enough for users with extra requirements: such a standard would be a regression from CIP-30.

#### Statelessness

All APIs must be stateless for ease of debugging: assuming on-chain state is constant, all API endpoints must return the same responses regardless of any previous API calls, with the only exception being rate limiting errors.

## Specification

### Query layer

Query layer must be available under `api.cipXXXX.query`, where XXXX is the number of this CIP.

#### Scope

Particular endpoint specs for the query layer are TBD.

Here's a proposed list of endpoints that are needed:

##### UTxO queries

Get UTxOs by address - adapt [kupo-like interface](https://cardanosolutions.github.io/kupo/#section/Patterns) that allows to query by address components with wildcards.

##### Staking and rewards

- Get staking rewards by stake address
- Get staking history by stake address

##### Era summaries

- Get a summary of eras

##### Epochs & protocol parameters

- Get latest epoch's protocol parameters
- Get lastest epoch info
- Get any epoch's protocol parameters (by epoch number)
- Get any epoch's info (by epoch number)

##### Data by hash

- Get scripts by hash
- Get datums by hash

##### Transactions

- Transaction contents by hash
- Transaction status by hash

##### Assets

- Asset history by policy ID (mint/burn)

##### Stake pools

- Get list of stake pools
- Get pool parameters by pool ID
- Get pool history by pool ID
- Get pool metadata by pool ID
- Get pool relays by pool ID
- Get pool delegators by pool ID
- Get pool blocks by pool ID
- Get pool certificates by pool ID

### Constraints interface

Constraints interface is a way for dApps to create transactions without having to deal with transaction structure. Effectively, when constraints interface is used, the wallet becomes fully responsible for tasks such as balancing, change generation, fee estimation and CBOR encoding.

While freeing dApp developers from having to deal with low-level details, constraints interface opens a possibility to implement wallet-specific features that would be impossible to have with CIP-30, using which dApp assumes full control. For example:

- ability to edit a transaction to perform additional actions: for example, sending ADA or tokens
- merging multiple transactions from different dApps together (assuming script validators are written in a way that allows that)
- ensuring change distribution between addresses: for example, multi-delegation feature that

#### Scope

A TBD list of constraints for dApps to use.

- Pay to address (with optional datum and optional reference script)
- Spend a UTxO
  * PubKey address
  * Native Script address
  * Plutus Script address
  * Native Script address via a reference input
  * Plutus Script address via a reference input
- Reference a UTxO
- Mint currency
  * Plutus Scripts
  * Native Scripts
  * Plutus Scripts via reference inputs
  * Native Scripts via reference inputs
- Set validity interval
- Require signature from PubKey
- Set transaction validity to `false`
- Delegate stake to
  * Plutus Script
  * Native Script
  * PubKey
- Withdraw stake from
  * Plutus Script
  * Native Script
  * PubKey
- Register stake
  * ScriptHash
  * PubKey
- Deregister stake scripts / pubkeys
  * Native Script
  * Plutus Script
  * PubKey

### JsonTx API

Defines serialization of Transaction type (and its parts) as JSON.

TBD

## Rationale: how does this CIP achieve its goals?

### Backwards compatibility

This standard is compatible with CIP-30 and uses its extension mechanism.

<!-- The rationale fleshes out the specification by describing what motivated the design and what led to particular design decisions. It should describe alternate designs considered and related work. The rationale should provide evidence of consensus within the community and discuss significant objections or concerns raised during the discussion.

It must also explain how the proposal affects the backward compatibility of existing solutions when applicable. If the proposal responds to a CPS, the 'Rationale' section should explain how it addresses the CPS, and answer any questions that the CPS poses for potential solutions.
-->

## Path to Active

### Acceptance Criteria
<!-- Describes what are the acceptance criteria whereby a proposal becomes 'Active' -->

- [ ] Implemented by at least one of production wallets
- TBD

### Implementation Plan
<!-- A plan to meet those criteria. Or `N/A` if not applicable. -->

## Copyright
<!-- The CIP must be explicitly licensed under acceptable copyright terms. -->

[CC-BY-4.0]: https://creativecommons.org/licenses/by/4.0/legalcode
[Apache-2.0]: http://www.apache.org/licenses/LICENSE-2.0
