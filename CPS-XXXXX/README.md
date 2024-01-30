---
CPS: 12
Title: Query Layer Standardization
Status: Open
Category: Tools
Authors:
    - Vladimir Kalnitsky <vladimir@mlabs.city>
Proposed Solutions: []
Discussions:
    - https://github.com/cardano-foundation/CIPs/pull/625
    - `#wallet-connectors` in CIP editors Discord: https://discord.gg/tkp6r6ESJR
Created: 2023-11-27
---

## Abstract

Cardano lacks a standardized query layer. This leads to suboptimal tooling, dApp and wallet architecture.

## Problem

### Query Layers and Tooling

Lack of a standardized query layer results in multiple different implementations of roughly the same set of functionality:

- [Blockfrost](https://blockfrost.io/)
- [Koios](https://www.koios.rest/)
- [Maestro](https://www.gomaestro.org)
- [Ogmios](https://ogmios.dev/)

As a result, there is a need to support multiple incompatible APIs in downstream tools, examples of which are:

- [Mesh.js](https://meshjs.dev/providers)
- [Lucid](https://lucid.spacebudz.io/)
- [cardano-transaction-library](https://github.com/Plutonomicon/cardano-transaction-lib/blob/develop/doc/runtime.md)

Query layer providers are not identical, which means that the *promise* of abstracting away from a particular query layer provider completely, that an offchain library may want to give to its users, will either be left *unfulfilled* (i.e. some features will work with some providers, but not others) or the scope of the downstream API will have to be *reduced* to the very minimum that is covered by every supported query layer.

### Query Layers and Wallets

This CPS initiative originated in the discussion about [Extensive Wallet Standard CIP](https://github.com/cardano-foundation/CIPs/pull/620) in [Discord](https://discord.com/channels/971785110770831360/992011119872970762/1176567729017327737) ([invite](https://discord.gg/P59aNVN8zu)).

Every light wallet has its own backend infrastructure: functioning of the browser extension relies on the availability of the data sources. However, none of the wallets currently provide a way to override their query layer endpoint URLs.

In the past, users have encountered problems with ability to submit transactions due to limited mempool capacity, which resulted in some wallets providing a way to configure custom [tx-submit-api](https://github.com/blinklabs-io/tx-submit-api) endpoints - but this only covers transaction submission.

Tight coupling between wallets and query layers results in unnecessary economic burden imposed on wallets, and forces them to make opinionated choices (of query layer provider) that could otherwise be delegated to the end user, similarly to how it is done in Metamask with RPC provider selection.

The economic burden, in turn, results in discouraging of innovation in the wallet ecosystem, because there is a very strong pressure to keep wallet standards minimal coming from wallet providers.

Another downside of tight coupling between wallets and query layers is that, unlike Ethereum wallets, Cardano wallets can't be used to interact with dApps deployed to custom (private) testnets. Only public testnets are supported, and as a result in order to simply test a dApp end-to-end, it must be deployed to a public testnet. This is a privacy concern for dApp developers, because making on-chain contracts available publicly (although in a compiled form) before they are officially open-sourced can be seen as data breach.

### Centralization and Ecosystem Risks

Inability to interchange query layer providers results in vendor lock-in. Query layer providers are disincentivized to opensource their infrastructure setup or provide a competitive service. Dependency on a fixed set of entities to run the infrastructure makes it easier for adversaries to attack dApps by taking over the infrastructure.

## Use cases

- Wallets want to provide their end users with ability to run custom query layer software
- dApp developers want to avoid vendor lock-in
- New Cardano infrastructure providers want to join pools of interchangeable query layer suppliers, instead of replicating or deploying one of the many competing products

## Goals

1. Create an extensive query layer API specification that is not tied to any particular implementation

2. Describe how can it be used in different contexts: HTTP API, JavaScript interfaces, ???

## Open Questions

<!-- A set of questions to which any proposed solution should find an answer. Questions should help guide solutions design by highlighting some foreseen vulnerabilities or design flaws. Solutions in the form of CIP should thereby include these questions as part of their 'Rationale' section and provide an argued answer to each. -->

- How can we encourage query layer providers to adopt the solution?
- How can we encourage wallet developers to adopt the solution?
- How can we encourage dApp developers to adopt the solution?
