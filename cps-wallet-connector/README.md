---
CPS: ?
Title: Cardano Wallet Connectors
Status: Open
Category: Wallets
Authors:
    - Ryan Williams <ryan.williams@iohk.io>
Proposed Solutions: []
Discussions:
    - https://github.com/cardano-foundation/cips/pulls/?
Created: 2023-07-28
---

## Abstract

Wallets are a foundational element of web 3, being the primary interface between users and blockchains.
Wallet-web bridges allow users to connect their wallet to web-based stacks, allowing a wide range of specialized experiences.

Wallet web-bridge standards consist of two parts; connection standard and API.
With the connection standard defining how the wallet and dApp initiate communication, this could be over injected Javascript object, WebRTC, WebTorrent, etc.
The API defines what communications look like between the dApp and wallet post connection.

This problem statement is concerned with the issues surrounding Cardano's current and future wallet-web bridges.
These interfaces are difficult to define and historically have been even harder to iterate upon.
We wish to provide a comprehensive catalog of the current offerings; and their drawbacks to be able to make suggestions on future standards.

## Problem
<!-- A more elaborate description of the problem and its context. This section should explain what motivates the writing of the CPS document. -->

The core motivation of this document is to catalog the current state of Cardano's wallet connectors, discuss their flaws and identify keys concerns for future connector authors to be aware of.
We hope that by discussing the issues we will inspire the next generation of Cardano wallet connectors so that the ecosystem can grow beyond it's first iterations.

Ineffective dApp-connectors can cause a range of issues for wallets, dApp developers and thus users.
Due to the nature of these connections there can often be unforeseen impacts of small design decisions.

For users, connectors should be widely supported across platforms, secure and decentralized.
For dApps, connectors should be expressive and extendable.
For wallets, connectors should be secure, extendable and should not expect wallet's to go beyond their standard activities.

### Core Concerns

#### 1. Secure connection
Security should remain of paramount concern within web 3.
Connection standards must strive to above all not compromise the security of wallets or dApps.
Connection standards should be aware of potential impacts of standard security vunrabilities, such as man-in-middle attacks.
Furthermore, standards should seek to be censorship resistant, by an ecosystem offering multiple connection standards we move in this direction.

#### 2. Secure API
The security of the API itself should again remain paramount.
This means that no secret information should ever be allowed to leave the wallet.
Furthermore if an operation requires the wallet to use a secret, the user should always be made aware. 

#### 3. Range of supported connection
Connection standards should ideally support a wide range of wallets and dApp platforms.
For example, connection which are accessible via desktop or mobile devices should be prioritized more so than those which only support one platform.

#### 4. Expressive API
APIs should allow for an expressive range of information to be exchanged.
Generally communication should be allowed two ways.

#### 5. Versioned
Connection standards and APIs should be explicitly versioned.
Furthermore, ideally APIs should allow for optional extendability to facilitate specialization.
Clear scope of versions / extensions.

#### 6. Preserve role of wallet
APIs should be written to have a clear scope, understanding the potential strains placed on wallet providers.
APIs, at a base level, should focus on preserving the base role of the wallet of controlling cryptographic operations.

### Context
// todo

Here we will add context to the current state of Cardano's wallet connectors. 

#### Cardano Wallet-Web Bridge history
- Lack of ecosystem cohesion around Role of the Wallet
- Reactive standard following other ecosystems
- Combination of connection and API in one standard
- CIP-30
- CIP-13 URI schemes
- CIP-45
- CIP-90
- CIP-95
- CIP-103
- CIP-104 -- impact of sharing account public key?

#### Historical Issues
- CIP-30 - Limited scope
- CIP-30 - Lack of versioning
- CIP-30 - injected object limiting
- Lack of ecosystem focus, wallet expected to do a lot
- Look at the issues on Github

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
Whilst most wallet softwares generally offer a users a range of features, at their core all wallets are primarily concerned with the management of cryptographic operations.
The majority of wallets build on this by using a chain indexer, so information related to the wallets crypto credentials can be gathered and presented to users.
Any operation beyond core cryptographic functions should be considered to be optionally extra by wallets and thus not included in base connector standards.

### Strive for interoperable and extensible APIs
Design APIs which are interoperable between connection standards and wallet types.
Design APIs which are optionally extensible, allowing for creation of specialized connections.
Aim to use the CIP process.

### Prioritize Security
Clearly identify and articulate known potential security concerns.
Utilize the collective knowledge of CIPs and open source development.

## Open Questions
<!-- A set of questions to which any proposed solution should find an answer. Questions should help guide solutions design by highlighting some foreseen vulnerabilities or design flaws. Solutions in the form of CIP should thereby include these questions as part of their 'Rationale' section and provide an argued answer to each. -->

// todo

### Can a universal connector be pursued?
- many types of wallet
- many types of platform
- Should / can a universal connector be pursued whilst maintaining other properties

### Can a universal API be pursued?  
- should we pursue fully connection standard agnostic APIs?
- or should some connection types only support some APIs?

### How interoperable can standards be with those of other ecosystems?
- What are the priorities for this ecosystem?
- other than Cardano crypto