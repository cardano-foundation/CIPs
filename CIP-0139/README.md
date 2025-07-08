---
CIP: 139
Title: Universal Query Layer
Category: Tools
Status: Proposed
Authors:
    - Vladimir Kalnitsky <klntsky@gmail.com>
    - Giovanni Garufi <giovanni@mlabs.city>
Implementors: []
Discussions:
    - https://discord.gg/MU8vHAgmGy
    - https://github.com/cardano-foundation/CIPs/pull/869
Solution-To: CPS-0012
Created: 2024-05-14
License: CC-BY-4.0
---

## Abstract

A transport-agnostic query layer specification for use in dApps and wallets.

## Motivation: why is this CIP necessary?

See [CPS-12](https://github.com/cardano-foundation/CIPs/pull/625) for motivation.

## Specification

The goal of this proposal is to define a standard, JSON-based, transport-agnostic query layer for wallets to implement which covers enough functionalities to be useful to a wide set of dApps.

We will start by discussing existing query layer designs for dApps, so we can properly define the use case for this CIP. 
Next, we will define the query layer API.
We attempt to define the API in a transport-agnostic way: the request and return types for each endpoint are as defined in CIP-0116, with a few notable exception where the corresponding CDDL type lacked some useful information (more on this can be found in the `Query Layer API` section). Finally, we end this section with some notes on rollbacks and pagination.

#### Existing Query Layer designs

There are two approaches to Cardano dApp development:

1. **Using customized chain followers**. A chain follower is a program that interacts with cardano-node and processes all incoming transactions, as well as rollbacks, to maintain consistent dApp-specific state. Example: [Carp](https://dcspark.github.io/carp/docs/intro/).

2. **Using general-purpose query layers**. General-purpose query layers allow to query blockchain data using a wide set of APIs that are not built with a particular dApp domain in mind. dApp state has to be constructed based on data returned from the queries. Examples: Blockfrost, Maestro.

The first approach allows for lower runtime resource consumption, but a general-purpose query layer has an advantage of being more easily reusable between dApps.

In this proposal, we are focusing on general-purpose querying only.

### Query Layer API

This section contains descriptions for methods & their parameter lists.

The scope of this section is loosely based on a [comparison table for existing Cardano query layers](./Query_Layer_API_Comparison.md).
The goal is to make it so that the API could be implemented via simple adapters that transform requests and responses to the appropriate formats.

The payload formats used below are either references to [CIP-0116 - Standard JSON encoding for Domain Types](https://cips.cardano.org/cip/CIP-0116), which specifies cardano domain types via a JSON schema, or references to the [Query Layer JSON schema](./query-layer.json) which we defined in this CIP to define some types that are not present in the CDDL spec.

[View the list of endpoints here](./endpoints.md)

### Transports

The API can be implemented across several transports. The goal is to allow several different clients, possibly written in different languages, to interact with wallets.
For this reason we provide an [Openapi schema](./open-api.json), a [JSON-RPC](./json-rpc.json) schema, and an interface for an [injected Javascript](./ts-api.md) object in Typescript.
We also generate a [specification](./cip-0144.md) of this API that is compatible with [CIP-0144 | Wallet Connector API]. This defines the API as a wallet extension that can be enabled by the user, enabling a full-data wallet
We generate these interfaces from a high level specification of the endpoints [source](https://github.com/mlabs-haskell/query-layer-impl), ensuring that the information is consistent and easily updatable for different choices of transport layer.

### Pagination

In CIP-30, pagination is not reliable: because there is no guarantee that the set of UTxOs does not change between calls. On the other hand, there are good reasons to want to paginate responses, especially when designing an universal query layer. There are, generally, no bounds on the number of results that will be returned by many of the queries we want the API to cover (e.g. there is no way to control how many UTxOs might ever be at a given script address).
Even if we remove pagination from this API, we still have the issue that the underlying provider being used to fetch the data, could be using pagination itself. While this is somewhat of an "implementation detail", it can still lead to issues for end-users interacting with this API.
In this CIP, we have decided to remove pagination from the API. While very useful to have, it introduces potential issues about consistency of the results that affect both dApp developers and end users.
We hope to revisit this topic in a future CIP, to come up with a solution that does not force us to pick between consistency and efficiency.

### Handling of rollbacks

Transaction rollbacks are essential to blockchains: local node's view of the chain may be different from other nodes'. During conflict resolution, the node may issue a rollback event, that should be handled by dApps.

Customized chain followers, at least in principle, allow for "live" rollback handling: that is, a user-facing dApp can subscribe to a local view of a part of the UTxO set.

General purpose query layers can also handle rollbacks just fine, but they don't propagate rollback events to dApps, because they do not possess any dApp-specific info to determine if a dApp *needs* to handle a particular rollback. dApps that work with general-purpose query layers follow pull-based architecture, rather than event subscription-based, which means they just request data as needed, instead of reacting to blockchain events.

In the context of this API, rollbacks should be acknowledged as a source of potential inconsistency between data pieces returned by different queries.

#### Error handling

Errors should be divided in two categories:

- domain errors
- transport errors (404, 500, etc)

Here we will only specify the domain errors. Users should also handle transport specific errors that can occur when interacting with the API.

##### Error Types

###### APIError

```
APIErrorCode {
	InvalidRequest: -1,
	InternalError: -2,
	Refused: -3,
	AccountChange: -4,
}
APIError {
	code: APIErrorCode,
	info: string
}
```

- InvalidRequest - Inputs do not conform to this spec or are otherwise invalid.
- InternalError - An error occurred during execution of this API call.
- Refused - The request was refused due to lack of access - e.g. wallet disconnects.
- AccountChange - The account has changed. The dApp should call wallet.enable() to reestablish connection to the new account. The wallet should not ask for confirmation as the user was the one who initiated the account change in the first place.

Note that the error codes and their meaning are copied from [CIP-30](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0030#apierror). The reason is that this API will most likely live "alongside" the CIP-30 API, so unifying the error types reduces burden on the users.

### Versioning

The API has an endpoint that must return the current version of the API implemented. While the CIP is in preparation, the version shall be set to 0.0.0. The moment this CIP is merged the version should be set to 1.0.0, and all implementations should return that as the current version. Any changes to the API should come in form of PRs to this CIP. Every change must update the version in accordance to SemVer.

## Rationale: how does this CIP achieve its goals?

This CIP originates from the work layed out in the wallet working group, and specifically to address [CPS-012](https://github.com/cardano-foundation/CIPs/blob/master/CPS-0012/README.md)

This CPS initiative originated in the discussion about [Extensive Wallet Standard CIP](https://github.com/cardano-foundation/CIPs/pull/620) on the CIP Discord server ([invite](https://discord.gg/P59aNVN8zu))
in the [`#general`](https://discord.com/channels/971785110770831360/992011119872970762/1176567729017327737) channel, continuing in a dedicated [`#query-layer-standard`](https://discord.com/channels/971785110770831360/1178763938389823598) channel.

This CIP attempts to solve the issues raised and discussed in these previous discussions and CPSs. At every step we have tried to get feedback for this CIP from the community, this includes: dApp and wallet developers, query layer providers, end users, etc.

We have attempted to define a minimal API to cover many use cases, but we expect this to evolve over time: either to fill in some gap we missed, or simply to keep up with the continuing evolution of Cardano itself. We encourage future authors to follow the versioning scheme defined above.

## Path to Active

### Acceptance Criteria

- [ ] There are at least two protocol adapter for any of the existing query layers that implements this spec, that can be run.
- [ ] There are at least two offchain library that implements a provider interface for this CIP, effectively making it usable with the protocol adapter in production.

### Implementation Plan

- [ ] Build at least one protocol adapter for any of the existing query layers that implements this spec
- [ ] Build at least one offchain library integration

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
