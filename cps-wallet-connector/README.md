---
CPS: 10
Title: Wallet Connectors
Status: Open
Category: Wallets
Authors:
    - Ryan Williams <ryan.williams@iohk.io>
Proposed Solutions: []
Discussions:
    - https://github.com/cardano-foundation/cips/pulls/619
Created: 2023-07-28
---

## Abstract
Wallets are a foundational element of Web3, being the primary interface between users and blockchains.
Wallet-web bridges allow users to connect their wallet to web-based stacks, allowing a wide range of specialized experiences.

Wallet web-bridge standards consist of two parts; connection standard and API.
With the connection standard defining how the wallet and dApp initiate communication, for example it could be over injected Javascript object.
The API defines what communications look like between the dApp and wallet post connection.

This problem statement is concerned with the issues surrounding Cardano's current and future wallet-web bridges.
These interfaces are difficult to define and historically have been even harder to iterate upon.
We wish to provide a comprehensive catalog of the current offerings; and their drawbacks to be able to make suggestions on future standards.

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

The core motivation of this document is to catalog the current state of Cardano's wallet connectors, discuss their flaws and identify keys concerns for future connector authors to be aware of.
We hope that by discussing the issues we will inspire the next generation of Cardano wallet connectors so that the ecosystem can grow beyond it's first iterations.

Ineffective dApp-connectors can cause a range of issues for wallets, dApp developers and thus users.
Due to the nature of these connections there can often be unforeseen impacts of small design decisions.

For users, connectors should be widely supported across platforms, secure and decentralized.
For dApps, connectors should be reliable, provide stable and rich APIs.
For wallets, connectors should be secure, extendable and should not expect wallet's to go beyond their standard activities.

### Core Concerns

#### 1. Secure connection
Security should remain of paramount concern within Web3.
Connection standards must strive to above all not compromise the security of wallets or dApps.
Connection standards should be aware of potential impacts of standard security vulnerabilities, such as man-in-middle attacks.
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
Connection standards and APIs should be explicitly versioned to clearly allow upgrades.
Furthermore, ideally APIs should allow for optional extendability to facilitate specialization.
Clear scope of versions / extensions.
- Should consider tiers of wallet - can be tricky to see adoption for dApps, dApss prefer lowest denominator.

#### 6. Respect the role of wallet
APIs should be written to have a clear scope, understanding the potential strains placed on wallet providers.
APIs, at a base level, should focus on preserving the base [role of the wallet](#clear-role-of-wallet).

### Context
Here we will add context to the current state of Cardano's wallet connectors. 

#### Cardano Wallet-Web Bridge History
[CIP-30](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0030/README.md) is *the* fundamental wallet connector standard for Cardano.
This standard has facilitated the emergence of dApp development on Cardano by defining both a connection standard and an API.
It is, to date, the only wallet connector standard to see wide adoption in the ecosystem.
Using an injected Javascript object for communication between wallets and web-based stacks.
Since its' authoring CIP-30 has seen continued iteration, with changes to its API.

##### CIP-30 Alternatives
Since CIP-30's authoring there have only been two other competing standards, in CIP-45 | Decentralized WebRTC dApp-Wallet Communication ([#395](https://github.com/cardano-foundation/CIPs/pull/395)) and CIP-90 | Extendable dApp-Wallet Web Bridge ([#462](https://github.com/cardano-foundation/CIPs/pull/462/)).
Although neither of of this standards have seen wide adoption.

Although not a direct competitor, CIP-13 could be seen as an alternative standard.
This standard

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
Whilst most wallet softwares generally offer a users a range of features, at their core all wallets are primarily concerned with the management of cryptographic operations.
The majority of wallets build on this by using a chain indexer, so information related to the wallets crypto credentials can be gathered and presented to users.
Any operation beyond core cryptographic functions should be considered to be optionally extra by wallets and thus not included in base connector standards.

#### Types of Wallet
No-data - just base crypto (i.e. HWWs) 
- places all management of UTxOs on dApps (could be applied for Voltaire - just approve votes, not care about UTxOs)
- Could just share root public key -> so dApp discovers addresses
- All wallets! - the most inclusive. Is interesting for future applications.
- Embedded wallets?
- script wallets?
- Can just be library
Own-data - knows about it’s own data (used addresses, utxos, etc.)
- Two sources of truth problem (CIP30)
- Hard to draw the lines between these
Full-data - can index chain for any information
- (Could add expense to wallet providers)
- dApps can ask wallet for any chain info
- Single source of truth
- Gives users the ability to choose source of truth
- Adam; User able to bring their own data - running local node etc.
- Data API to be out of scope for this CPS.
- Probably not historical state, but certainly ledger state

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