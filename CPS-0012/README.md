---
CPS: 12
Title: Query Layer Standardization
Category: Tools
Status: Open
Authors:
    - Vladimir Kalnitsky <vladimir@mlabs.city>
    - Ryan Williams <ryan.williams@intersectmbo.org>
Proposed Solutions: []
Discussions:
    - Original pull request: https://github.com/cardano-foundation/CIPs/pull/625
Created: 2023-11-27
License: CC-BY-4.0
---

## Abstract

Query layer services abstract away the difficulties of indexing blockchains, offering builders API interfaces to access data. 

Cardano's query layers lack standardization.
This leads to suboptimal tooling, dApp and wallet architecture.

## Problem

Cardano nodes offer limited options for querying chain data.
For builders, running chain indexing infrastructure can alleviate the data availability issues of the Cardano node.
But this brings with it large overheads in running the nodes, chain followers, data storage and data access.

Query layer providers offer builders the opportunity to abstract away the infrastructure complexities of Cardano data availability, usually to some cost.
These providers are extremely useful and in turn are used as a foundational element for hundreds of tools.

Cardano has a range of query layer providers, each with their own interfaces and business motivations.
This can present issues for builders who wish to build with multiple providers.

### Query Layers and Tooling

Lack of a standardized query layer results in multiple different implementations of roughly the same set of functionality:

- [Blockfrost](https://blockfrost.io/)
- [Koios](https://www.koios.rest/)
- [Maestro](https://www.gomaestro.org)

As a result, there is a need to support multiple incompatible APIs in downstream tools, examples of which are:

- [Mesh.js](https://meshjs.dev/providers)
- [Lucid](https://lucid.spacebudz.io/)
- [cardano-transaction-library](https://github.com/Plutonomicon/cardano-transaction-lib/blob/develop/doc/runtime.md)
- [cardano-js-sdk](https://github.com/input-output-hk/cardano-js-sdk/tree/master/packages/core/src/Provider)

Query layer providers are not identical, which means that the *promise* of abstracting away from a particular query layer provider completely, that an offchain library may want to give to its users, will either be left *unfulfilled* (i.e. some features will work with some providers, but not others) or the scope of the downstream API will have to be *reduced* to the very minimum that is covered by every supported query layer.

### Query Layers and Wallets

This CPS initiative originated in the discussion about [Extensive Wallet Standard CIP](https://github.com/cardano-foundation/CIPs/pull/620) on the CIP Discord server ([invite](https://discord.gg/P59aNVN8zu))
in the [`#general`](https://discord.com/channels/971785110770831360/992011119872970762/1176567729017327737) channel, continuing in a dedicated [`#query-layer-standard`](https://discord.com/channels/971785110770831360/1178763938389823598) channel.

Every light wallet has its own backend infrastructure: functioning of the browser extension relies on the availability of the data sources. However, none of the wallets currently provide a way to override their query layer endpoint URLs.

In the past, users have encountered problems with ability to submit transactions due to limited mempool capacity, which resulted in some wallets providing a way to configure custom [tx-submit-api](https://github.com/blinklabs-io/tx-submit-api) endpoints - but this only covers transaction submission.

Tight coupling between wallets and query layers results in unnecessary economic burden imposed on wallets, and forces them to make opinionated choices (of query layer provider) that could otherwise be delegated to the end user, similarly to how it is done in Metamask with RPC provider selection.

The economic burden, in turn, results in discouraging of innovation in the wallet ecosystem, because there is a very strong pressure to keep wallet standards minimal coming from wallet providers.

Another downside of tight coupling between wallets and query layers is that, unlike Ethereum wallets, Cardano wallets can't be used to interact with dApps deployed to custom (private) testnets. Only public testnets are supported, and as a result in order to simply test a dApp end-to-end, it must be deployed to a public testnet. This is a privacy concern for dApp developers, because making on-chain contracts available publicly (although in a compiled form) before they are officially open-sourced can be seen as data breach.

### Centralization and Ecosystem Risks

The inability to interchange query layer providers results in vendor lock-in. Query layer providers are disincentivized to opensource their infrastructure setup or provide a competitive service. Dependency on a fixed set of entities to run the infrastructure makes it easier for adversaries to attack dApps by taking over the infrastructure.

Having accepted standards drastically reduces the complexity and cost for new providers to develop.
This creates a query layer marketplace where providers can be more easily compared by customers.

### Barriers to adoption

Such a standard could likely face resistance to adoption.

The potential risk for commercial offerings adopting this standard is the loss of the ability to differentiate themselves from competitors via data shape.

Differentiating themselves via data shape is useful in two ways for query layer providers.
Firstly, data providers each use their own unique infrastructure, so the costs of the same query are not uniform between providers.
By adjusting query shape, providers can adjust queries to suit their architecture, ensuring speed and reducing cost.

Secondly, is the potential monetary advantages.
Without a standard commercial providers are able to shape their data in a way to attract customers.
A provider's business model may be to charge per request, which incentivises them to keep the data small to increase the number of queries by customers.
A standardized set of queries would reduce the ability for providers to do this.

#### Mitigation

To mitigate the impact of varying provider architectures, authors of solutions should seek to involve query layer providers in the development of a standard.
This will allow providers to voice concerns over potentially expensive or awkward queries.

To address loss of avenue for differentiation, via data shape standard authors should seek to ensure there are other ways in which providers can differentiate.
These could be built into the standard such as optional batching, allowing providers to offer tiers of batching support for their endpoints.

## Use Cases

### Multi-Provider Wallets

Wallets may wish to allow users to bring their own data layer provider (on public or custom networks).
By having a standard interface wallets would be able to support this, which would reduce the wallet's operating costs.
For the users this gives them flexibility, redundancy and the option to run their wallet on their own infrastructure. 

### DApps Avoiding Lock-In

DApp developers don't want to tie their infrastructure to one query layer provider.
By being able to switch providers without the need for significant engineering, they can avoid providers which do not offer fair pricing.

### New Infrastructure Providers

New Cardano infrastructure providers want to be able join pools of interchangeable query layer suppliers.
Without standardization new providers must invest significant time to develop their own backends (including APIs).

## Goals

1. Create an extensive query layer API specification that is not tied to any particular implementation

2. Describe how can it be used in different contexts: HTTP API, JavaScript interfaces, browser-based wallets, standalone wallets, dApp backends.

3. A query layer standard which meets the needs of query layer providers, wallet developers and dApp developers.

## Open Questions

### How can we encourage query layer providers to adopt the solution?

Such standardization could have drawbacks for existing query layer providers.

The primary argument against such an initiative is the potential loss of business advantage from query layer providers.
As standardized providers would loose the ability to differentiate themselves via data shape and language.

For providers which charge per request this can negatively impact their ability to control their value proposition.
Such providers are currently incentivized to make the data returned via queries contain the least possible useful information.
Standards would mean providers would not be able to control the amount of data that is returned upon a query.
This would mean existing providers would have to adjust their business and value proposition to customers.

### How can we encourage wallet developers to adopt the solution?

For wallet providers, a standardized query layer would offer long term benefits which outweigh any upfront engineering costs.
With users being able to bring their own data providers, wallets will incur less costs to the use of their providers.

### How can we encourage dApp developers to adopt the solution?

DApp developers would benefit from a more open and competitive query layer market.
Developers will be able to choose the provider which best fits the needs of their dApp.

### How can we address multiple Cardano ledger eras?

How a standard distinguishes between data from different Cardano ledger eras is something that needs to be addressed.
Should providers be expected to support a superset of all Cardano eras?

## Acknowledgements

<details>
  <summary><strong>Workshop 1 - 2024-01-25</strong></summary>

  We would like to thank those that contributed to the first Query Layer Standardization workshop hosted by The Wallets Working Group ([see shared drive with resources](https://drive.google.com/drive/folders/1baSYHfWJdUh5dwRkHjY7qnaufjuO8sP2?usp=sharing)).

  Hosts:

  - Ryan Williams
  - Adam Dean

  Participants:

  - Dmang
  - George APEX Pool
  - Leo H
  - Marcin Szamotulski
  - Markus Gufler
  - Matt Davis
  - Matthieu Pizenberg
  - Michael Chappell
  - NEXUS Crypto
  - Nick Cook
  - Rhys Bartels-Waller
  - Ruslan Dudin
  - Torbjørn Løvseth Finnøy

</details>

## Copyright

This CPS is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).