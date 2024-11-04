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

We have identified and carried out two steps in the path to provide a better alternative to CIP-30:

- Defining a universal JSON encoding for Cardano domain types. CIP-30 requires CBOR encoding and decoding for data passed to and from the wallet, which is often an extra burden for the client. This problem is stated in [CPS-0011](https://github.com/cardano-foundation/CIPs/tree/master/CPS-0011) and a potential solution is given in [CIP-0116](link).

- Defining a universal query layer. CIP-30 is only concerned with obtaining data regarding the wallet, this forces dApps to integrate with other tools to query general blockchain data. This problem is stated in [CPS-0012] and a potential solution is given in [CIP-????](link).

[CPS-0010](https://github.com/Ryun1/CIPs/blob/cps-wallet-connector/CPS-0010/README.md) defines the responsibilities for wallet connector, and also introduces the vocabulary to distinguish between different kinds of wallets, based on the functionality they offer.
In this CPS we hope to explain why a full-data wallet connector would be useful, and how putting all these pieces together we can make an improvement over CIP-30.

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

## Use cases
<!-- A concrete set of examples written from a user's perspective, describing what and why they are trying to do. When they exist, this section should give a sense of the current alternatives and highlight why they are not suitable. -->

The use cases listed in [CPS-0010](https://github.com/Ryun1/CIPs/blob/cps-wallet-connector/CPS-0010/README.md#use-cases),
which lists some use cases for wallet connectors, equally apply to this CPS as well.

Ultimately, the problem we are trying to solve is the "two sources of truth" that exist when a dApp has to both query the wallet for its own UTxO state, and then query some other data provider (blockfrost, maestro, a local node) for the state of the blockchain.

By giving the wallets direct control over the data-fetching API, we allow them to present an unified view of all the UTxOs, reducing the issues that currently happen because of wallet vs dApp UTxO contention, and making optimizations (i.e. transaction chaining) easier to implement and more robust.
This benefits both end users of the wallets, because it reduces the chance to build and submit transactions that will end up being phase-1 invalid,
and dApp developers by relieving them of having to deal with synchronization between the (local) wallet state and the (global) chain state.

## Goals
<!-- A list of goals and non-goals a project is pursuing, ranked by importance. These goals should help understand the design space for the solution and what the underlying project is ultimately trying to achieve.

Goals may also contain requirements for the project. For example, they may include anything from a deadline to a budget (in terms of complexity or time) to security concerns.

Finally, goals may also serve as evaluation metrics to assess how good a proposed solution is. -->

- Define a CIP that extends CIP-30 to provide a tighter interaction between wallets and dApps by following the principles outlined in CPS-0010.

- Build upon the work done in CIP-0116 and CIP-XXXX to offer a full transaction building API based on JSON instead of CBOR, and utilizing the query layer spec to fetch data from the blockchain.

- Provide a simple and unified view of wallet and blockchain data to dApps to prevent many of the pitfalls described above.

## Open Questions
<!-- A set of questions to which any proposed solution should find an answer. Questions should help guide solutions design by highlighting some foreseen vulnerabilities or design flaws. Solutions in the form of CIP should thereby include these questions as part of their 'Rationale' section and provide an argued answer to each. -->


### Translating CIP-30 API

There are some choices that will need to be done while translating the CIP-30 API to JSON. The types defined in [CIP-0116](./link) should provide almost all that is required, but types for errors, and other domain types used by CIP-30 will need to be added as well.
Furthermore, CIP-30 specifies options for pagination. While useful in practice, pagination has turned out to be complex to implement properly and is not supported in [CIP-XXXX](./). CIP authors should decide wether to attempt to support the pagination from CIP-30 or to drop it completely.

### Transaction building API

The new proposed interface allows to submit transactions directly as native JS objects.
It is currently not clear if it is worth adding a layer to the wallet connector to standardize transaction building.

APIs for transaction building also come in many flavors: there are prominent examples both of "declarative APIs", that allow building the transaction by specifying a set of constraints
that the transaction must respect, and the "imperative API", that allows building a transaction object directly. These two APIs don't necessarily rule each other out:
some implementations mix the two with input or transaction builders.

The CIP authors should decide if they want to add this interface to the CIP directly, or perhaps leave it as future work.
Should a transaction building API be added, our recommendation would be to aim to make it as close as possible with 
[cardano-serialization-lib](https://github.com/Emurgo/cardano-serialization-lib) which is widely used in the ecosystem and would be easy to adopt by many wallets.

### Other CIP-30 improvements

There are a few other issues with CIP-30 that are raised in CPS-0010. Since this CPS is advocating for a replacement to CIP-30, it would make sense to resolve some of those issues. However, since the update we are advocating for is already quite substantial, an argument can also be made to delay further changes to future and more specific CIPs.


--------


