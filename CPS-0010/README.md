---
CPS: 10
Title: Wallet Connectors
Status: Open
Category: Wallets
Authors:
    - Ryan Williams <ryan.williams@iohk.io>
    - Vladimir Kalnitsky <vladimir@mlabs.city>
Proposed Solutions: []
Discussions:
    - https://github.com/cardano-foundation/cips/pulls/619
Created: 2023-07-28
---

## Abstract
Wallets are a foundational element of Web3, being the primary interface between users and blockchains.
Wallet connectors allow users to connect their wallet to web-based stacks, allowing a wide range of specialized experiences.

Wallet connector standards consist of two parts; connection standard and API.
With the connection standard defining how the wallet and dApp initiate communication, for example using an injected Javascript object.
The API defines what communications look like between the dApp and wallet post connection.

This problem statement is concerned with the issues surrounding Cardano's current and future wallet connectors.
These interfaces are difficult to define and historically have been even harder to iterate upon.
We wish to provide a comprehensive catalogue of the current offerings and their drawbacks to be able to make suggestions on future standards.

### Acknowledgments

<details>
  <summary><strong>First workshop - 2023-11-27</strong></summary>

  I would like to thank those that contributed to the first workshop hosted by Adam Dean and Ryan Williams ([see presentation slides with notes](https://docs.google.com/presentation/d/1lXw1yMf-Hyp1eVfaFnbTV9897r6pZEd6zpvLNMqT3cI/)).
  - Beatrice Anihiri
  - Denis Kalinin
  - Evgenii Lisitskii
  - George APEX Pool
  - George Flerovsky
  - George Humphreys
  - Hernán Rajchert
  - Jack Rousian
  - Joshua Marchand
  - Ken Fritschy
  - Ken-Erik Ølmheim
  - Leo H
  - Marcel Baumberg
  - Martynas Kazlaukas
  - Michael Chappell
  - Mircea Hasegan
  - Nicolas Ayotte
  - Rhys Bartels-Waller
  - Robert Phair
  - Rodolpho Ribeiro
  - Steven Johnson
  - Teodora Sevastru Lunn
  - Thomas Lindseth
  - Thomas Upfield
  - Vladimir Kalnitsky

</details>


## Problem
<!-- A more elaborate description of the problem and its context. This section should explain what motivates the writing of the CPS document. -->

The core motivation of this document is to outline the current state of Cardano's wallet connectors, discuss their flaws, and identify key concerns for future connector authors to be aware of.
We hope that by discussing the issues, we will inspire the next generation of Cardano wallet connectors so that the ecosystem can grow beyond its first connector iterations.

Ineffective connectors can cause a range of issues for wallets, dApp developers, and thus users.
Due to the nature of these connections, there can often be unforeseen impacts of small design decisions.

For users, connectors should offer secure and reliable compatibility with a wide range of dApps.
For dApps, connectors should be reliable, provide stable and rich APIs
For wallets, connectors should be secure and extendable, and you should not expect wallets to go beyond their standard activities.

### Core Concerns

#### 1. Secure connection
Security should remain of paramount concern within Web3.
Connection standards must strive to, above all, not compromise the security of wallets or dApps.
Connection standards should be aware of the potential impacts of standard security vulnerabilities, such as man-in-the-middle attacks.

#### 2. Secure API
The security of the API itself should again remain paramount.
This means that no secret information should ever be allowed to leave the wallet.

#### 3. Range of supported connection
Connection standards should ideally support a wide range of wallets and dApp platforms.
This means we shouldn't assume a software environment (e.g., JavaScript in the browser) and define the APIs using schema languages widely used in language-agnostic contexts.

#### 4. Expressive API
APIs should allow for an expressive range of information to be exchanged.
Communication should be expressive in both directions.
APIs should be language agnostic.

#### 5. Versioned
Connection standards and APIs should be explicitly versioned to clearly allow upgrades.
Furthermore, ideally, APIs should allow for optional extendability to facilitate specialization.
Versions and extensions should have clearly defined scopes.

#### 6. Respect the role of wallet
APIs should be written to have a clear scope, understanding the potential strains placed on wallet providers.
APIs, at a base level, should focus on preserving the base [role of the wallet](#clear-role-of-wallet).

### Context

#### Cardano Connector History
[CIP-30](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0030/README.md) is *the* fundamental wallet connector standard for Cardano.
This standard has facilitated the emergence of dApp development on Cardano by defining both a connection standard and an API.
It is, to date, the only wallet connector standard to see wide adoption in the ecosystem.
Using an injected Javascript object for communication between wallets and web-based stacks
Since its' authoring, CIP-30 has seen continued iteration with changes to its API.

##### CIP-30 Alternatives
Since CIP-30's authoring there have only been two other competing standards, in CIP-45 | Decentralized WebRTC dApp-Wallet Communication ([#395](https://github.com/cardano-foundation/CIPs/pull/395)) and CIP-90 | Extendable dApp-Wallet Web Bridge ([#462](https://github.com/cardano-foundation/CIPs/pull/462/)).
Although neither of of this standards have seen wide adoption.

Although not a direct competitor, CIP-13 could be seen as an alternative standard, which fits some wallet connection niches.

##### CIP-30 Extensions
- CIP-62
- CIP-95
- CIP-103
- CIP-104 -- impact of sharing account public key?

#### Historical Issues
- Lack of ecosystem cohesion around Role of the Wallet
- Combination of connection and API in one standard
- Lack of ecosystem focus, wallet expected to do a lot -> not clearly defined what the role is
- Encouraged emulated wallets
- Typescript APIs limiting
- No way for dApp to subscribe to wallet events

#### Solutions
- CIP-30 - extendibility mechanism
- CIP-30 - not changing anymore

## Use cases
<!-- A concrete set of examples written from a user's perspective, describing what and why they are trying to do. When they exist, this section should give a sense of the current alternatives and highlight why they are not suitable. -->

### NFT Marketplace
Alice wishes to buy a NFT from an smart contract based NFT marketplace for an agreed price because she wishes to support the artist.
Alice wants to be able to use a familiar website interface where she can browse rendered NFTs then select and buy on the same site.

Without the dApp and her wallet communicating it is very difficult to construct the needed transaction to buy the NFT Alice wants.

### Simple Wallet Login
Bob wants to use his wallet to login to a website.
The website requires that Bob presents both; his public credentials and also prove his ownership of them.

It is difficult for Bob to produce and share proof of ownership for public credentials in a secure way without the dApp and wallet communicating.

### dApp Developer
Carol is a dApp developer, who wants many users to be able interact with her dApp via web interface.
She wants to be able to support a wide range of wallets and platforms to maximize potential user base.
Whilst she wants the API standards to be expressive so that her dApp is able to offer a range of functionality.

### Wallet provider
Dave has created a wallet, he wants to minimize the cost of running his wallet.

Without clear role of the wallet, and optional API extension scoping Dave's infrastructure may be asked to do many operations incurring cost.

## Goals
<!-- A list of goals and non-goals a project is pursuing, ranked by importance. These goals should help understand the design space for the solution and what the underlying project is ultimately trying to achieve.

Goals may also contain requirements for the project. For example, they may include anything from a deadline to a budget (in terms of complexity or time) to security concerns.

Finally, goals may also serve as evaluation metrics to assess how good a proposed solution is. -->
### Clear Role of Wallet
Whilst most wallet softwares generally offer a users a range of features, at their core all wallets are concerned with the management of cryptographic operations.
The majority of wallets build on this by using a chain indexer, so information related to the wallets crypto credentials can be gathered and presented to users.
Any operation beyond core cryptographic functions should be considered to be optionally extra by wallets.

By only expecting wallet to support cryptographic operations we define a universal rule for all wallet connectors.
This means at a minimum all dApps can expect from wallets during connection is cryptographic operations.
Although, dApps should be able to request additional functionalities on connection if they wish.

This does not mean that all connections must support cryptographic operations.

#### Types of Wallet by Query Layer configuration

All possible wallet standards can be divided into three groups based on a single criterion: what data they provide to dApps via the API endpoint.

This division is important because each of the groups allows for different dApp architectures.

Note that the groups are nested: every wallet is a no-data wallet and every full-data wallet is also an own-data wallet if we look at the dApp architectures they enable.

##### No-data wallets

No-data wallets do not provide data queries and are only concerned with cryptographic operations (e.g. hardware wallets).
All management of UTxOs is placed on dApps side.
No-data wallets can use multiple addresses, but they do not allow to query for available UTxOs and do not indicate which of the addresses are actually used on-chain.

These wallets may even rely on dApps to derive addresses, by sharing the root public key.


![diagram showing wallet and dApp architecture for no-data wallets](./no-data-wallet.drawio.png)

This design ensures that wallets can function without a query layer and thus without runtime infrastructure needed.

##### Own-data wallets

Own-data wallets provide chain queries related to users' own data and wallet state (users' addresses and utxos).
CIP-30 falls into this category.

![diagram showing possible wallet and dApp architecture for own-data wallets](./own-data-wallet.drawio.png)

This architecture has two major issues:

- **Unclear separation of concerns** - while wallets provide certain functions for dApp developers, they have no means to enforce their use, and naturally some developers opt to using their own query layers when they see fit, with consequences that are hard to predict. For example, the wallet may not allow signing a transaction that consumes an UTxO it considers "locked".

- **Two sources of truth problem** - on Cardano, every running node has its own opinion on the set of currently unspent transaction outputs. Only [eventual consistency](https://en.wikipedia.org/wiki/Eventual_consistency) is guaranteed. Any dApp that interacts with an own-data wallet has to deal with the inconsistency between local `cardano-node`-based query layer and light wallet query layer, especially when dApp workflow involves sending multiple interactions with the wallet in quick succession. For example, a wallet may refuse to sign a transaction containing an UTxO it does not (yet) know about.

Even if we enforce clear separation of concerns in the standards, e.g. by stating that sending a transaction bypassing the wallet is not allowed, the problem of two sources of truth will remain.

##### Full-data wallets

Full-data wallets allow to query blockchain data outside of user's scope (i.e. anything not covered by own-data wallets).

![diagram showing possible wallet and dApp architecture for full-data wallets](./full-data-wallet.drawio.png)

Depending on dApp needs, full-data wallets open a way to implement fully-functional dApps that use non-local blockchain data without the need for the developer to maintain dApp backend infrastructure. As a result, more decentralized and censorship-resistant architectures become possible: a dApp can be distributed as a set of files, and deployed to IPFS or static hosting websites.

Full-data wallets enable "single source of truth" architecture: no need to work around data inconsistency between two query layers.

They are more expensive to operate due to higher query layer requirements, but the risks could be lowered by letting query layer providers and wallet developers be separate entities. That would also allow the end users to choose query layer providers they trust more rather than being forced to trust wallet's infrastructure as well as code, and, optionally, use their own query layer deployments, thus alleviating the need to trust any external wallet backend while enjoying the usual interface.

### Strive for interoperable and extensible APIs
Design APIs which are interoperable between connection standards and wallet types.
Design APIs which are optionally extensible, allowing for creation of specialized connections.
Aim to use the CIP process.

### Prioritize Security
Clearly identify and articulate known potential security concerns.
Utilize the collective knowledge of CIPs and open source development.

## Open Questions
<!-- A set of questions to which any proposed solution should find an answer. Questions should help guide solutions design by highlighting some foreseen vulnerabilities or design flaws. Solutions in the form of CIP should thereby include these questions as part of their 'Rationale' section and provide an argued answer to each. -->

### Should we provide historical data in full-data wallets?

Historical data includes (but is not limited to):

- metadata and contents of past transactions
- spent transaction outputs
- past epoch metadata
- past stake delegations

### Can a universal connector be pursued?

Every wallet connector that simply adds functionality on top of another standard can be considered a valid implementation of the base standard.
If the set of standards is designed in a way that allows for extensions without conflicts, then a superset of all standards can be considered a universal connector. How to make it possible to clearly define a "universal connector" and whether it is useful at all remains to be seen.

### Can a universal API be pursued?

Platform differences are a concern: by using specifications that do not rely on assumptions about data transfer methods, software environment or programming language, it is possible to create a standard that is truly reusable across platforms.

There are many types of dApp architectures enabled by different wallet types, but there is no requirement to use the APIs provided by wallets, so dApps that use simpler standards should still remain functional when used with their extensions.

Does that open a way to define a universal API?

### How interoperable can standards be with those of other ecosystems?

Cardano is sufficiently different from most of the blockchains that aim to unify their wallet standards.

What options do we have for integration with Cardano sidechains, rollups, hardforks, private testnets, etc.?
