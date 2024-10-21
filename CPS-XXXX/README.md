---
CPS: ?
Title: Full-data wallet connector
Status: Open
Category: Tools
Authors:
    - Giovanni Garufi <giovanni@mlabs.city>
Proposed Solutions: []
Discussions:
    - https://github.com/cardano-foundation/cips/pulls/?
Created: YYYY-MM-DD
---

## Abstract
<!-- A short (\~200 word) description of the target goals and the technical obstacles to those goals. -->

CIP-30 is the standard interface of communication between wallets and DApps. While this CIP has been instrumental in the development of dApps for Cardano, it also has some shortcomings that have been observed across several implementations.

We have identified three steps in the path to provide a better alternative to CIP-30:

- Defining a universal JSON encoding for Cardano domain types. CIP-30 requires CBOR encoding and decoding for data passed to and from the wallet, which is often an extra burden for the client. This problem is stated in [CPS-0011](https://github.com/cardano-foundation/CIPs/tree/master/CPS-0011) and it's corresponding [CIP-0116](link).

- Defining a universal query layer. CIP-30 is only concerned with obtaining data regarding the wallet, this forces dApps to integrate with other tools to query general blockchain data. This problem is stated in [CPS-0012] and it's corresponding [CIP-????](link).

- Define an API for transaction building. This is the last step required to build a full-data wallet connector as specified in [CPS-0010](https://github.com/Ryun1/CIPs/blob/cps-wallet-connector/CPS-0010/README.md#full-data-wallets).

[CPS-0010](https://github.com/Ryun1/CIPs/blob/cps-wallet-connector/CPS-0010/README.md) defines the responsibilities for wallet connector, and also introduces the vocabulary to distinguish between different kinds of wallets, based on the functionality they offer. In this CPS we hope to explain the need and our design for a full-data wallet connector.

## Problem
<!-- A more elaborate description of the problem and its context. This section should explain what motivates the writing of the CPS document. -->

CIP-30 is a universally accepted web-based wallet standard for Cardano. It provides a minimalistic interface that, in principle, can be used to build almost any kind of Cardano dApp. However, the way dApp<->wallet interaction is defined leads to suboptimal dApp architecture due to CIP-30 limits.


Consider the following problems:

### Use of CBOR representations

CIP-30 standard uses CBOR encoding for all data passed from the wallet, e.g. addresses and UTxOs. Interpreting this data within the app requires CBOR decoding functionality that is tedious to implement manually, and so users resort to using cardano-serialization-lib or its close alternative, cardano-multiplatform-lib, which both require loading a WebAssembly blob of >1M in size.

For comparison, to start a new Web3 app on Ethereum there is no need to use a library for data serialization. It’s possible to interact with a provider object that is given by the wallet directly, although there are libraries to further simplify this. Using CBOR looks unnecessary for most dApps, given that JSON is a de-facto standard for web data serialization.

### Limited scope of available queries

Most dApps require interacting with scripts, which implies the need to query for available UTxOs locked at script addresses and other blockchain data. CIP-30 is intentionally limited in scope to management of UTxOs "owned" by the wallet itself.

Some other useful queries, like getting delegation and reward info, stake pool info, transaction metadata or contents, and epoch data, are also outside of scope.

As a result, dApp developers are forced to implement their own query layers on the backend side - which leads to one more problem - inconsistency between states of two query layers:

### Inconsistency of Query Layers

On Cardano, every running node has its own opinion on the set of currently unspent transaction outputs. Only eventual consistency is guaranteed.

Any dApp that interacts with a CIP-30 wallet has to deal with the inconsistency between the local cardano-node-based query layer and the light wallet query layer, especially when dApp workflow involves sending multiple transactions with the wallet in quick succession.

Thus, the goal of the developers is to ensure that the set of UTxOs available to the wallet and the set of UTxOs the backend cardano-node knows about are synchronized enough to not cause errors when a wallet or backend operations are performed. To give a few examples of potential issues, consider the following scenarios:

A dApp tries to balance a transaction with UTxOs from the wallet that is not yet available in dApp backend's cardano node, causing an error response during execution units evaluation
A transaction is passed for signing, but the wallet does not yet know about the UTxOs it spends, and thus refuses to sign it
A transaction is sent to the network via the dApp backend (bypassing CIP-30 submit method) and is confirmed there, but the wallet still does not know about its consumed inputs, and thus returns outdated data.

### No support for transaction building

Finally, CIP-30 leaves the burden of building transactions fully in the hands of the user.
This necessarily forces users to add another layer to their frontend (cardano-transaction-library, cardano-serialization-library, etc) to actually construct, balance and serialize transactions.

The problem is further exacerbated by the fact that these extra layers for transaction building usually offer diverse API, both in terms of coverage and overall approach to transaction building. This makes switching between different transaction-building libraries very complicated.

Finally, some concerns around transaction building such as balancing or coin selection, are both hard to implement correctly, and may have significant consequences for the users that are building and submitting transactions. Forcing libraries to re-implement solutions to this problem fragments the efforts and research that is done in these topics.

## Use cases
<!-- A concrete set of examples written from a user's perspective, describing what and why they are trying to do. When they exist, this section should give a sense of the current alternatives and highlight why they are not suitable. -->

The use cases listed in [CPS-0010](https://github.com/Ryun1/CIPs/blob/cps-wallet-connector/CPS-0010/README.md#use-cases).

## Goals
<!-- A list of goals and non-goals a project is pursuing, ranked by importance. These goals should help understand the design space for the solution and what the underlying project is ultimately trying to achieve.

Goals may also contain requirements for the project. For example, they may include anything from a deadline to a budget (in terms of complexity or time) to security concerns.

Finally, goals may also serve as evaluation metrics to assess how good a proposed solution is. -->

- Define a CIP that extends CIP-30 to provide a tighter interaction between wallets and dApps.

- Build upon the work done in CIP-0116 and CIP-XXXX to offer a full transaction building API based on JSON instead of CBOR, and utilizing the query layer spec to query the blockchain.

- Define a transaction building API which is based on JSON and is expressive enough to cover many possible different use cases.

- Provide a simple and unified view of wallet and blockchain data to dApps to prevent many of the pitfalls described above.

## Open Questions
<!-- A set of questions to which any proposed solution should find an answer. Questions should help guide solutions design by highlighting some foreseen vulnerabilities or design flaws. Solutions in the form of CIP should thereby include these questions as part of their 'Rationale' section and provide an argued answer to each. -->

### Choice of transaction building API

Historically transaction-building APIs for Cardano are either "imperative" or "declarative". The difference between the two is that in the imperative case, the user is operating and building the transaction directly, while in the declarative case the user specifies a set of constraints that the transaction should have, and then a transaction that satisfies those constraints is build from there.
An example of the imperative approach is the API offered by [cardano-api](insert-link), while an example of the declarative one is the [Contract monad](insert-link). It is still unclear which of these two approach is superior to the other, or even if there is a significant difference between the two. A CIP implementing a solution for this CPS would have to decide on which of the two approaches to follow.

There is also another interesting aspect to transaction building, namely that different users require different levels of control over transaction building process for reasons such as: optimizing fees, ensuring proper ordering of transaction inputs, or backwards compatibility.

There are three conceptual levels of control:

- CL1. transaction constraints level - the user only cares about particular requirements a transaction must satisfy in order to be valid in the context of the app, such as sending a certain amount to an address, consuming a UTxO, or submitting a stake delegation.
- CL2. transaction contents level - the user cares about particular details of transaction structure, such as number and contents of change outputs, or ordering of inputs.
- CL3. CBOR level - the user cares about CBOR layout of the transaction, in particular, about key ordering in maps and definite/indefinite length serialization format of CBOR arrays

A solution must allow all three levels of controls, without forcing users to care about details from lower levels, if they don't need to.

### Other CIP-30 improvements



--------


