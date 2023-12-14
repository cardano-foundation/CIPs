---
CPS: ?
Title: Universal JSON encoding of domain types
Status: Open
Category: Tools
Authors:
    - Vladimir Kalnitsky <vladimir@mlabs.city>
Proposed Solutions: []
Discussions:
    - https://github.com/cardano-foundation/cips/pulls/?
Created: 2023-11-30
---

<!-- Existing categories:

- Meta     | For meta-CIPs which typically serves another category or group of categories.
- Wallets  | For standardisation across wallets (hardware, full-node or light).
- Tokens   | About tokens (fungible or non-fungible) and minting policies in general.
- Metadata | For proposals around metadata (on-chain or off-chain).
- Tools    | A broad category for ecosystem tools not falling into any other category.
- Plutus   | Changes or additions to Plutus
- Ledger   | For proposals regarding the Cardano ledger (including Reward Sharing Schemes)
- Catalyst | For proposals affecting Project Catalyst / the Jörmungandr project

-->

## Abstract
<!-- A short (\~200 word) description of the target goals and the technical obstacles to those goals. -->

dApps require the use of communication protocols that facilitate data transfer between:

- query layer providers and dApps
- wallets and dApps
- wallets and query layer providers
- dApp frontends and backends
- different dApps

Usually these protocols include a specification of Cardano domain types, i.e. ledger block and all its components.

## Problem

Cardano domain types have canonical CDDL definitions (for every era), but when it comes to use in web apps, where JSON is the universally accepted format, there is no definite standard.

As a result, software solutions are incompatible with each other, and dApp developers are forced to write code for conversions that could in princible be unnecessary, because the semantics of different JSON layouts are often the same. In particular, this problem is very real when dApps need to provide support for different query layer providers.

The [initiative](https://github.com/cardano-foundation/CIPs/pull/625) to standardize query layers on Cardano is currently blocked due to absence of a standardized JSON data schema. However, such a schema would be useful in contexts other than query layers, so this CPS is separate.

<!-- A more elaborate description of the problem and its context. This section should explain what motivates the writing of the CPS document. -->

## Use cases
<!-- A concrete set of examples written from a user's perspective, describing what and why they are trying to do. When they exist, this section should give a sense of the current alternatives and highlight why they are not suitable. -->

- dApp developers want to have a definite encoding of JSON data, so that they don't need to specify the format themselves
- dApp developers want to be sure they will be able to reuse data coming from different sources (third parties) without format changes
- dApp developers want to provide external APIs that must be easily consumable
- Query layer developers want to make sure their APIs will be easily consumable
- Multiple service/product owners, who utilize different competing JSON encoding conventions want to converge to a single convention

## Goals

<!-- A list of goals and non-goals a project is pursuing, ranked by importance. These goals should help understand the design space for the solution and what the underlying project is ultimately trying to achieve.

Goals may also contain requirements for the project. For example, they may include anything from a deadline to a budget (in terms of complexity or time) to security concerns.

Finally, goals may also serve as evaluation metrics to assess how good a proposed solution is. -->

Non-goals:

- Maintain roundtrip property for conversion between JSON and CBOR: this is impossible, because CBOR uses varying binary encodings for arrays and maps.
- Provide support for different eras in a single schema
- Maintain correctness of signatures for transactions encoded as JSON: this is impossible in the general case, because signature validity depends on binary layout determined by CBOR encoding. Conventions may apply to preserve signatures, but they are out of scope of the standard, because they apply to CBOR encoding, not JSON.
- Making the encoding as compact as possible (reducing encoded data size)

## Open Questions
<!-- A set of questions to which any proposed solution should find an answer. Questions should help guide solutions design by highlighting some foreseen vulnerabilities or design flaws. Solutions in the form of CIP should thereby include these questions as part of their 'Rationale' section and provide an argued answer to each. -->

-
