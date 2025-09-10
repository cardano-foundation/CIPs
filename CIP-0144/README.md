---
CIP: 144
Title: Extensible Wallet Connector Framework
Category: Tools
Status: Proposed
Authors:
  - Giovanni Garufi <giovanni@mlabs.city>
Implementors: []
Discussions:
    - https://github.com/cardano-foundation/cips/pulls/957
Created: 2024-12-13
License: CC-BY-4.0
Solution-To: CPS-0010
---

## Abstract


CIP-30 is the standard interface of communication between wallets and dApps. While this CIP has been instrumental in the development of dApps for Cardano, it also has some shortcomings that have been observed across several implementations.

[CPS-0010](https://github.com/cardano-foundation/CIPs/blob/master/CPS-0010/README.md) outlines the shortcomings of CIP-30. In this CIP we aim to address some of the issues pointed out by CPS-10: splitting up the connection API from the functionality provided by the [full API](https://cips.cardano.org/cip/CIP-30#full-api), defining the API in a transport agnostic way and defining a versioning mechanism for the connection API and its extensions.

This CIP only aims to re-define the connection API from CIP-30, leaving the full API and other extensions for future CIPs. CIPs that want to build upon this work should use the following naming convention: `CIP-XXXX | Wallet Connector - <CIP name>`. Once such a CIP is proposed, it should also be added to the table below so all extensions can be easily visible from one place.


| Extension CIP | Link | Description |
| --- | --- | --- |
| CIP-0147 - Wallet Connector - Own-data wallet | https://github.com/cardano-foundation/CIPs/pull/986 | Extension to enable an own-data wallet, matching the full API that was provided in CIP-30 |
## Motivation: why is this CIP necessary?

CIP-30 is a universally accepted web-based wallet standard for Cardano. It provides a minimalistic interface that, in principle, can be used to build almost any kind of Cardano dApp. However, the way dApp<->wallet interaction is defined leads to suboptimal dApp architecture due to CIP-30 limits.

### CPS-10

[CPS-0010](https://github.com/Ryun1/CIPs/blob/cps-wallet-connector/CPS-0010/README.md) discusses several limitations of CIP-30. In this CIP we try to solve the issues pointed out in that CPS. There are still some areas to improve on: things like the event listener API are intentionally left out of this CIP to prevent bloat of scope. We welcome future CIPs, or updates to this CIP to refine any limitation that is not tackled in this document.

### Use of CBOR representations

In addition to the points described in CPS-10, the CIP-30 standard uses CBOR encoding for all data passed from the wallet, e.g. addresses and UTxOs. Interpreting this data within the app requires CBOR decoding functionality that is tedious to implement manually, and so users resort to using cardano-serialization-lib or its close alternative, cardano-multiplatform-lib, which both require loading a WebAssembly blob of >1M in size.

For comparison, to start a new Web3 app on Ethereum there is no need to use a library for data serialization. It’s possible to interact with a provider object that is given by the wallet directly, although there are libraries to further simplify this. Using CBOR looks unnecessary for most dApps, given that JSON is a de-facto standard for web data serialization.

In this work we build on the work carried out in [CIP-0116](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0116) defining a universal JSON encoding for Cardano domain types.

## Specification

The goal of this CIP is to provide a better alternative to CIP-30, providing a base on which we can define a CIP-30 compatible API, and further extensions in the future. Specifically we make the following contributions:

- A clear separation between the connection mechanism and the different APIs offered by the wallet.
- Using JSON for Cardano domain types instead of CBOR
- Add versioning support to the extension API
- Define the API in a transport agnostic way

### Transport agnostic operations

In its current state, CIP-30 defines it API through a specific transport layer, namely an injected Javascript object.
In this CIP we want to be able to define an API without committing to a specific transport layer. Implementors of this API can choose to support this API through several transports such as: HTTP, an injected Javascript object, JSON-RPC etc.
Furthermore, we want to use JSON-schema to clearly define the types that each method, or operation, expects to receive or returns.
To keep the specification abstract we will use the word "operation" to describe the actions supported by the API: these would map to "endpoints" for an HTTP implementation of the API, or to "methods" for an implementation based on an injected Javascript object.


We will use the following schema to define operations:

```json
{
  "operation": { "type": "string" },
  "request": { "type": "object" },
  "response": { "type": "object" },
  "errors": {
    "type": "array",
    "items": { "type": "object" }
  }
}
```

where `operation` will be the identifier for the operation, `request` and `response` will be the JSON-schemas for the request and response types respectively, and `errors` will be a list of schemas for the errors that the operation may raise.
We do not add an explicit scope to operation names, we do however encourage transport-specific implementations of this API to pick the scoping structure that makes more sense to them.

We will reference several JSON schemas throughout the document, these are:

- [CIP-116 | Standard JSON encoding for Domain Types](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0116) which provides a JSON encoding of Cardano ledger types. Note that this CIP defines a schema for each ledger era. When referring to a type from this schema we refer to an `anyOf` of all the schemas in which that type is defined.
- [appendix](#appendix) in which we define schemas for types required by the connection API and the error types

We will use an identifier in the anchor to refer to the schema where each type is defined. For example, if we want to reference the `Transaction` type, as defined in CIP-116 we will use the following schema reference `{ "$ref": "#/cip-116/Transaction" }`.

If an operation does not require any arguments as part of it's request, or does not return a meaningful response, we will represent this as an `{}` on the respective operation field. The arguments to an operation will always be represented as an object. If a field is not marked as `required`, then that argument is to be considered optional.

For each operation we will provide some details on how the implementation should behave. Note that some of these are taken verbatim from CIP-30.

### Connection API

The role of the connection API is to provide generic information about the wallet and to allow the user to opt into the functionalities (or extensions) that they want the wallet to provide.

##### Enable

```json
{
  "operation": "enable",
  "request": { "$ref": "#/appendix/Extensions" },
  "response": {},
  "errors": [
    { "$ref": "#/appendix/APIError" }
  ]
}
```

This is the entrypoint to start communication with the user's wallet. The wallet should request the user's permission to connect the web page to the user's wallet, and if permission has been granted, the APIs will be made available for the dApp to use. The wallet can choose to maintain a whitelist to not necessarily ask the user's permission every time access is requested, but this behavior is up to the wallet and should be transparent to web pages using this API. If a wallet is already connected this function should not request access a second time.

Through the `extension` field, dApps can request a list of what functionality they expect as a list of CIP numbers (and optional versions) capturing those extensions. This is used as an extensibility mechanism to document what functionalities can be provided by the wallet interface. We will see later in this document examples of what such extensions might be and which functionalities they will enable. New functionalities can be introduced via additional CIPs and may be all or partially supported by wallets.

When requesting the functionalities of a cip extension, dApps can optionally specify a version number for it. Every cip extension defined in the future, must also define a versioning scheme following SemVer. When the version argument is not specified, wallets should take that as the greater version they implement. In this context - and for the rest of this discussion - we will assume versions are ordered with the canonical ordering of SemVer. If the dApp requests a specific version of an extension, wallets can only accept the request if a version of the extension they implement has:

- the same major value as the one requested by the dApp AND
  - a greater minor value as the one requested by the dApp, OR
  - an equal minor value AND
    - a greater or equal patch value as the one requested by the dApp

If multiple versions satisfy these requirements, then wallets must return the greatest version amongst all candidate versions.

DApps are expected to use this endpoint to perform an initial handshake and ensure that the wallet supports all their required functionalities. Note that it's possible for two extensions to be mutually incompatible (because they provide two conflicting features). While we may try to avoid this as much as possible while designing CIPs, it is also the responsibility of wallet providers to assess whether they can support a given combination of extensions, or not. Wallets should throw an error with code `NotSatisfiable` if either they do not support the required extension, or they deem the combination of extensions requested by the dApp to be incompatible. In this case, it is up to the dApp to decide to retry with different requirements, or to give up on establishing a connection with the wallet.

##### IsEnabled

```
{
  "operation": "isEnabled",
  "request": {},
  "response": { "type": "boolean" },
  "errors": [
    { "$ref": "#/appendix/APIError" }
  ]
}
```

Returns true if the dApp is already connected to the user's wallet, or if requesting access would return true without user confirmation (e.g. the dApp is whitelisted), and false otherwise.


##### SupportedExtensions

```
{
  "operation": "supportedExtensions",
  "request": {},
  "response": { "$ref": "#/appendix/Extensions" },
  "errors": []
}
```

A list of extensions and versions supported by the wallet. Extensions may be requested by dApps on initialization. Some extensions may be mutually conflicting and this list does not thereby reflect what extensions will be enabled by the wallet. Yet it informs on what extensions are known and can be requested by dApps if needed. Note that if a wallet supports multiple versions of the same CIP, then it must return each one of them as an element in the response.


##### Name

```
{
  "operation": "name",
  "request": {},
  "response": { "type": "string" },
  "errors": []
}
```

A name for the wallet which can be used inside of the dApp for the purpose of asking the user which wallet they would like to connect with.

##### Icon

```
{
  "operation": "icon",
  "request": {},
  "response": { "type": "string" },
  "errors": []
}
```

A URI image (e.g. data URI base64 or other) for img src for the wallet which can be used inside of the dApp for the purpose of asking the user which wallet they would like to connect with.

##### ApiVersion

```
{
  "operation": "apiVersion",
  "request": {},
  "response": { "$ref": "#/appendix/SemVer" },
  "errors": []
}
```

Returns the API version for the wallet connection API. This must correspond to the value of `Connection-API` specified in this document, appropriately transformed into a `SemVer` object.

### Versioning

In this CIP we define a semantic versioning (SemVer) scheme that will be used by the connection API. Extensions defined in other CIPs (e.g. [CIP-XXX | Own data wallet](https://github.com/cardano-foundation/CIPs/pull/986)) must follow the same versioning schema.

While the CIP is in preparation, the version shall be set to `0.0.0`. The moment this CIP is merged the version shall be set to `1.0.0`, and all implementations should consider that the current version. Any changes to the connection API should come in form of PRs to this CIP.

| API | Version |
| --- | --- |
| Connection-API | 0.0.0 |


### Appendix

This appendix contains additional schemas for types that are used in the APIs.

#### Connection API Data Types

##### Extensions

```
{
  "type": "object",
  "title": "Extensions",
  "properties": {
    "extensions": {
      "type": "array",
      "items": {
          {
            "type": "object",
            "title": "Extension",
            "properties": {
              "cip": {
                "type": "number"
              },
              "version: {
                "$ref": "#/appendix/SemVer"
              }
            },
            "required": ["cip"],
          }
      }
    }
  },
  "required": ["extensions"],
}
```

An extension is an object with a "cip" field that describes a CIP number extending the API, and an optional version specified according to SemVer. For example:

```
{ "cip": 30 }
```


##### SemVer

```
{
  "type": "object",
  "title": "SemVer",
  "properties": {
    "major": {
      "title": "Major",
      "type": "number",
    },
    "minor": {
      "title": "Minor",
      "type": "number",
    },
    "patch": {
      "title": "Patch",
      "type": "number",
    }
  },
  "required": ["major", "minor", "patch"],
}
```

#### Errors

This section lists the possible errors the wallet connector may return. Each error is specified by an error code, and an optional info string describing the cause of the error. Below each error we list names for all the error codes, and a brief description of when they should be used. Other than when the spec dictates the use of a specific error code, wallets can choose the error code they deem more applicable to the situation. Wallets can also extend these errors with additional codes should they feel the need to.

##### APIError

```
{
  "type": "object",
  "title": "APIError",
  "properties": {
    "code": {
      "type": "number",
      "title": "APIErrorCode"
      "enum": [-1, -2, -3, -4, -5]
    },
    "info": {
      "type": "string"
    }
  },
  "required": ["code"],
}
```

- `InvalidRequest`: (-1) Inputs do not conform to this spec or are otherwise invalid.
- `InternalError`: (-2) An error occurred during execution of this API call.
- `Refused`: (-3) The request was refused due to lack of access - e.g. wallet disconnects.
- `AccountChange`: (-4) The account has changed. The dApp should call wallet.enable() to reestablish connection to the new account. The wallet should not ask for confirmation as the user was the one who initiated the account change in the first place.
- `NotSatisfiable`: (-5) The request is structurally correct, but the wallet can not satisfy it for some reason.


#### Transport specific connectors

While this CIP attempts to define an API in a transport agnostic way, implementations will be forced to pick a specific transport. In the spec we have not given specifics on how to namespace and generally structure the api in an implementation. This is both because details depend on the underlying transport that is chosen to implement the API, but also because we wanted to make backwards compatibility with the original CIP-30 proposal as easy as possible.

Each transport specific implementation will make a choice on how to namespace access to the operations. In the following we give a description of how this should work for an implementation using an injected javascript object. Support for different transports can be added to this CIP in form of PRs.

##### Injected Javascript Object

In this spec we define how to provide access to the operations defined in this CIP on an injected javascript object.
We aim to define this in a way that is backwards compatible with existing CIP-30 implementations. 

In order to initiate communication from webpages to a user's Cardano wallet, the wallet must provide the following javascript API to the webpage.
A shared, namespaced `cardano` object must be injected into the page if it did not exist already. Each wallet implementing this standard must then create a field in this object with a name unique to each wallet containing a wallet object implementing the connection API.

Upon successful connection via `cardano.{walletName}.enable()`, a javascript object we will refer to as `api` is returned to the dApp.
If the user requested any extensions they will be available under `api.cipXXXX`, without any leading zeros.

For example; CIP-0123's endpoints should be accessed by:

```
api.cip123.endpoint1()
api.cip123.endpoint2()
```

###### CIP-30 Backwards compatibility

Given this definition, we can take an existing CIP-30 compliant wallet, and make it compatible with this CIP with a wrapper.

This wrapper will be relatively small, but must still take care in unifying the differences between this CIP and the connection api from CIP-30. There is a list of some notable differences to keep in mind:

- JSON is used instead of CBOR. The wrapper must take care of translating arguments and results.
- CIP-30 allows for a situation where the user requests some extensions in the enable call, but despite the wallet not supporting those extensions, the `enable` call succeeds. This makes it so the dApps always have to check what extensions were actually enabled. In this CIP we don't allow that, so the wrapper must take care of calling `api.getExtension` after `cardano.{walletName}.enable` to check all required extensions are enabled, if that's not the case then throw an error.
- Add an `api.apiVersion` method that returns the version for the connector

Implementing this wrapper is out of scope of this CIP, but we welcome any effort in this direction, as it would make transitioning to this CIP easier for most wallets.


## Rationale: how does this CIP achieve its goals?

The goal of this CIP is to define the standard for a new wallet connector. This connector improves on CIP-30 by defining an independent connection API and giving dApp developers a finer-grained choice on which functionalities to enable via the extension mechanism.
The goal is to be able to clearly differentiate and communicate the type of wallet that is needed, following the distinction made in the [wallet role](https://github.com/cardano-foundation/CIPs/blob/master/CPS-0010/README.md#4-work-within-the-role-of-wallet) section of CPS-10.

There are two CIPs that are connected with this one:
- [CIP-0147 | Own data wallet](https://github.com/cardano-foundation/CIPs/pull/986) which defines an extension for an [own-data wallet](https://github.com/cardano-foundation/CIPs/blob/master/CPS-0010/README.md#own-data-wallets) which is equivalent to what CIP-30 offers today
- [CIP-0139 | Universal Query Layer](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0139) which defines an extension for a [full-data wallet](https://github.com/cardano-foundation/CIPs/blob/master/CPS-0010/README.md#full-data-wallets) which allows the wallet to track blockchain data that is outside of the user's scope

## Path to Active

### Acceptance Criteria

- [ ] There is at least one implementation for a CIP-30 compatibility wrapper as explained in the `CIP-30 Backwards compatibility` section
- [ ] Two or more wallets implement support for this CIP.

### Implementation Plan

- [ ] Implement a wrapper that takes a CIP-30 compatible API and transforms it to be compatible with CIP-0144.

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
