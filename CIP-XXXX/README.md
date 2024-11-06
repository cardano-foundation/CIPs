---
CIP:
Title: Universal Query Layer
Category: Tools
Status: Proposed
Authors:
    - Vladimir Kalnitsky <klntsky@gmail.com>
    - Giovanni Garufi <giovanni@mlabs.city>
Implementors: []
Discussions:
    - https://discord.gg/MU8vHAgmGy
Created: 2024-05-14
License: CC-BY-4.0
Version: 0.0.0
---

## Abstract
<!-- A short (\~200 word) description of the proposed solution and the technical issue being addressed. -->

A transport-agnostic query layer specification for use in dApps and wallets.

## Motivation: why is this CIP necessary?

See [CPS-12](https://github.com/cardano-foundation/CIPs/pull/625) for motivation.

## Specification

<!-- The technical specification should describe the proposed improvement in sufficient technical detail. In particular, it should provide enough information that an implementation can be performed solely on the basis of the design in the CIP. This is necessary to facilitate multiple, interoperable implementations. This must include how the CIP should be versioned, if not covered under an optional Versioning main heading. If a proposal defines structure of on-chain data it must include a CDDL schema in its specification.-->

The goal of this proposal is to define a standard, JSON-based, transport-agnostic query layer for wallets to implement which covers enough functionalities to be useful to a wide set of dApps.

We will start by discussing existing query layer designs for dApps, so we can properly define the use case for this CIP. 
Next, we will define the query layer API.
We attempt to define the API in a transport-agnostic way: the request and return types for each endpoint are as defined in CIP-0116, with a few notable exception where the corresponding CDDL type lacked some useful information (more on this can be found in the `Methods` section). Finally, we end this section with some notes on rollbacks and pagination.

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

#### Versioning

The API has an endpoint that must return the current version of the API implemented. While the CIP is in preparation, the version shall be set to 0.0.0. The moment this CIP is merged the version should be set to 1.0.0, and all implementations should return that as the current version. Any changes to the API should come in form of PRs to this CIP. Every change must update the version in accordance to SemVer.

### Pagination

In CIP-30, pagination is not reliable, because there is no guarantee that the set of UTxOs does not change between calls. This behavior is not suitable for DeFi: consistency should be prioritized, and pagination should be avoided.

### Transports

The API can be implemented across several transports. The goal is to allow several different clients, possibly written in different languages, to interact with wallets.
For this reason we provide an [Openapi schema](./open-api.json), a [JSON-rcp](./json-rpc.json) schema, and an interface for an [injected Javascript](./ts-api.md) object in Typescript.
We generate these interfaces from a high level specification of the endpoints [source](./link-to-ql-impl), ensuring that the information is consistent and easily updatable for different choices of transport layer.

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

## Rationale: how does this CIP achieve its goals?

<!-- The rationale fleshes out the specification by describing what motivated the design and what led to particular design decisions. It should describe alternate designs considered and related work. The rationale should provide evidence of consensus within the community and discuss significant objections or concerns raised during the discussion.

It must also explain how the proposal affects the backward compatibility of existing solutions when applicable. If the proposal responds to a CPS, the 'Rationale' section should explain how it addresses the CPS, and answer any questions that the CPS poses for potential solutions.
-->

This CIP originates from the work layed out in the wallet working group, and specifically to address [CPS-012](https://github.com/klntsky/CIPs/blob/klntsky/query-layer-cps/CPS-0012/README.md)

This CPS initiative originated in the discussion about [Extensive Wallet Standard CIP](https://github.com/cardano-foundation/CIPs/pull/620) on the CIP Discord server ([invite](https://discord.gg/P59aNVN8zu))
in the [`#general`](https://discord.com/channels/971785110770831360/992011119872970762/1176567729017327737) channel, continuing in a dedicated [`#query-layer-standard`](https://discord.com/channels/971785110770831360/1178763938389823598) channel.

This CIP attempts to solve the issues raised and discussed in these previous discussions and CPSs. At every step we have tried to get feedback for this CIP from the community, this includes: dApp and wallet developers, query layer providers, end users, etc.

We have attempted to define a minimal API to cover many use cases, but we expect this to evolve over time: either to fill in some gap we missed, or simply to keep up with the continuing evolution of Cardano itself. We encourage future authors to follow the versioning scheme defined above.

## Path to Active

### Acceptance Criteria
<!-- Describes what are the acceptance criteria whereby a proposal becomes 'Active' -->

- [ ] There is at least one protocol adapter for any of the existing query layers that implements this spec, that can be run.
- [ ] There is at least one offchain library that implements a provider interface for this CIP, effectively making it usable with the protocol adapter in production.

### Implementation Plan
<!-- A plan to meet those criteria or `N/A` if an implementation plan is not applicable. -->

- [ ] Build at least one protocol adapter for any of the existing query layers that implements this spec
- [ ] Build at least one offchain library integration

<!-- OPTIONAL SECTIONS: see CIP-0001 > Document > Structure table -->

## Copyright
<!-- The CIP must be explicitly licensed under acceptable copyright terms.  Uncomment the one you wish to use (delete the other one) and ensure it matches the License field in the header: -->

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
<!-- This CIP is licensed under [Apache-2.0](http://www.apache.org/licenses/LICENSE-2.0). -->
