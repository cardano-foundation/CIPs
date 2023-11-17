---
CIP: 90
Title: Extendable dApp-Wallet Web Bridge
Category: Wallets
Status: Proposed
Authors:
    - Ryan Williams <ryan.williams@iohk.io>
    - Martynas Kazlauskas <martynas.kazlauskas@iohk.io>
    - Matthias Benkort <matthias.benkort@cardanofoundation.org>
    - rooooooooob
Implementors: []
Discussions:
    - https://github.com/cardano-foundation/CIPs/pull/446
    - https://github.com/cardano-foundation/CIPs/pull/462
    - https://forum.cardano.org/t/cip-extendable-dapp-connector/114666
Created: 2023-02-12
License: CC-BY-4.0
---

## Abstract

This document describes a *base* web-wallet communication bridge accompanied by a scheme from which functionality can be added through API extensions.

This specification defines a wallet-dApp connection standard using injected Javascript object, with an extendable API interface.

## Motivation: why is this CIP necessary?

[CIP-30 | Cardano dApp-Wallet Web Bridge](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0030) facilitated the launch of dApp development on Cardano.
Yet it's functionality is limited in scope, which has led to multiple revisions, additions, and alterations.
Causing divergence between the capabilities of wallet implementations, making the development of compatible dApps cumbersome and error-prone.
This has lead to the adoption of a novel versioning scheme for CIP-30 called "CIP-30 extensions".

One drawback of extending CIP-30 has been that all connections enable the CIP-30 API endpoints by design.
This stops us as an ecosystem from moving on from CIP-30's design.
This specification can act as a skeleton from which functionality can be fleshed out in a modular fashion, without the impact of CIP-30's design.

To maintain backwards compatibility with CIP-30 implementations we enable CIP-30 endpoints by default.

This proposal is intended for dApp creators and Cardano wallet providers, with broad application to various types of Web3 applications.

## Specification

### Data Types

#### Extension

An extension is an object with a single field `"cip"` that describes a CIP number extending the API (as a plain integer, without padding).
For example:

```ts
{ "cip": 30 }
```

##### Known Extensions

This should act as the definitive list of known and accepted extensions to this proposal. 

| CIP                                                                           | Scope                           |
| ------------------------------------------------------------------------------|-------------------------------- |
| [CIP-0030](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0030)   | Generic interface               |
| [CIP-0095](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0095)   | Conway Ledger Era / Governance  |

### Extension CIPs

Extension authors should strive to construct self-contained specifications that do not overlap with other extensions, in scope, data types, error codes, or endpoints.
If there is overlap, then it is at the implementors discretion to merge as they see fit.
To attempt to avoid this, elements of extensions should be scope specific.

The creation of competing extensions scopes should be avoided; rather, extension scopes should be clear, non-ambiguous, and siloed. Ideally, the scope should be an attempt to solve a problem or address unrealized functionality in the set of dApp connector extensions.

Versioning of extensions should be avoided, once accepted through the CIP process extension's functionality should be static.
If an extension needs substantial updates replacing it with a successor is preferred.
Extensions replacing older extensions should clearly state their intent to do so.

All endpoints defined by extensions should be separated via namespacing.
Namespaced, endpoints must be preceded by `.cipXXXX.` from the `API` object, without any leading zeros.

For example; CIP-0123's endpoints should be accessed by:
```ts
api.cip123.endpoint1()
api.cip123.endpoint2()
```

##### Can extensions add their own Data Types, Error Types and Error Codes?

Yes.

##### Can extensions add their own endpoints?

Yes. Endpoints can be added to this proposal's [Extendable API](#extendable-api).

##### Can extensions overwrite/replace any part of this specification?

No.

##### Can extensions depend on other extensions?

No. Currently we do not allow this.

##### Should extensions follow a specific format?

Yes. They all are CIPs.

##### Are wallet expected to implement all extensions?

No. It's up to wallet providers to decide which extensions they ought to support.

### Error Types

#### ConnectorError

```js
ConnectorErrorCode {
	InvalidRequest: -1,
	InternalError: -2,
	Refused: -3,
}
ConnectorError {
	code: ConnectorErrorCode,
	info: string
}
```

* InvalidRequest - Arguments do not conform to this specification or are otherwise invalid - e.g. requested extension is not supported by the wallet.
* InternalError - An error occurred during execution of this API call.
* Refused - The request was refused due to lack of access - e.g. user rejected connection to this dApp.

### Initial API

In order to initiate communication from webpages to a user's Cardano wallet, the wallet must provide the following javascript API to the webpage. A shared, namespaced `cardano` object must be injected into the page if it did not exist already. Each wallet implementing this standard must then create a field in this object with a name unique to each wallet containing a `wallet` object with the following methods. The API is split into two stages to maintain the user's privacy, as the user will have to consent to `cardano.{walletName}.enable()` in order for the dApp to read any information pertaining to the user's wallet with `{walletName}` corresponding to the wallet's namespaced name of its choice.

#### `cardano.{walletName}.enable(extensions: Extension[] = [{ cip: 30 }]): Promise<API>`

Errors: `ConnectorError`

This is the entrypoint to start communication with the user's wallet.
The wallet should request the user's permission to connect the web page to the wallet, and if permission has been granted, the [Extendable API](#extendable-api) will be returned to the dApp to use.
The wallet can choose to maintain a whitelist to not necessarily ask the user's permission every time access is requested.
But this behavior is up to the wallet and should be transparent to web pages using this API.

Upon start, dApps can explicitly request a list of additional functionalities they expect as a list of CIP numbers capturing those extensions.
Note that it's possible for two extensions to be mutually incompatible (because they provide two conflicting features).
While we may try to avoid this as much as possible while designing CIPs, it is also the responsibility of wallet providers to assess whether they can support a given combination of extensions, or not.
Hence, wallets aren't expected to fail should they not recognize or not support a particular combination of extensions.
As a result, dApps may fail and inform their users or may use a different, less-efficient, strategy to cope with a lack of functionality.

Once a connection is established, this can be called multiple times by the dApp to request access to further extensions.
User permission must be asked if new extensions are requested.
If this is called without new extensions requests then no user permission is required.

**Note**: In order to improve backwards compatibility an empty `extensions` field should supply CIP-30 functionality, as if a CIP-30 `extension` object was provided.

#### cardano.{walletName}.isEnabled(): Promise\<Extension[]>

Errors: `ConnectorError`

Returns a list of extensions which have been enabled by the wallet.
If no wallet access has been granted then a `ConnectorError` with  `Refused` error code should be thrown.

#### cardano.{walletName}.supportedExtensions: Extension[] | undefined

A list of extensions supported by the wallet.
Extensions may be requested by dApps on initialization. Dapps can repeatably call `wallet.enable()` to add further extensions.
Some extensions may be mutually conflicting, and this list does not thereby reflect what extensions will be enabled by the wallet. Yet it informs on what extensions are known and can be requested by dApps if needed.

`undefined` is equivalent to `{cip: 30}`.

#### cardano.{walletName}.name: String

A name for the wallet which can be used inside of the dApp for the purpose of asking the user which wallet they would like to connect with.

#### cardano.{walletName}.icon: String

A URI image (e.g. data URI base64 or other) for img src for the wallet which can be used inside of the dApp for the purpose of asking the user which wallet they would like to connect with.

### Extendable API

Upon successful connection via `cardano.{walletName}.enable()`, a javascript object we will refer to as `API` (type) / `api` (instance) is returned to the dApp.
This type is defined by the extension CIP(s).

This is where extensions are free to add functionality as they see fit.
Furthermore, extensions are free to include additional sub-sections, naming their APIs as they see fit; an example could be an `Experimental API`.

## Rationale: how does this CIP achieve its goals?

This API does not offer *useful* functionality for dApp-Wallet interactions; rather, all useful functionality should be offered through extensions.
By keeping this API as a skeleton, we aim to avoid the chance of introducing functionality we come to regret later.
Instead, this proposal should be the minimum foundation required to build on top of.  

The alternative to this proposal is the addition of extensions to CIP-30's specification.
This would mean that the CIP-30 API would be included in all extended dApp-Wallet connections.
With the current landscape of dApps and wallets this seems fine, but it is uncertain if we want to indefinitely support the CIP-30 API.

By stripping functionality from this API we facilitate dApp-Wallet connections with less functions than CIP-30 API.
A use case for this is connections where minimal wallet information is wished to be shared with a dApp.

Here we attempt to mitigate the impact of succeeding CIP-30 as *the* Cardano wallet connector.
By enabling it's functionality by default at connection time and lifting many parts of it's Initial API.
This should minimize the impact this proposal could have on established dApps who support CIP-30.
By only adding what is necessary for extensions, we aim to reduce the required load for wallets to adopt this standard.

### Extensions

Extensions provide an extensibility mechanism and a way to negotiate (possibly conflicting) functionality between a dApp and a wallet provider.
There's rules enforced as for what extensions a wallet decide to support or enable.

Extensions can be seen as a smart versioning scheme.
Except that, instead of being a monotonically increasing sequence of numbers, they are multi-dimensional feature set that can be toggled on and off at will.
This is a versioning "à-la-carte" which is useful in a context where:

1. There are multiple concurrent standardization efforts on different fronts to accommodate a rapidly evolving ecosystem;
2. Not everyone agrees and has desired to support every existing standard;
3. There's a need from an API consumer standpoint to clearly identify what features are supported by providers.

By moving CIP-30 style modifications into a formalized extension scheme we aim to avoid fragmentation of functionality between different dApp-Wallet bridges.
Whilst avoiding the need for versioning.

By promoting siloed extensions, we aim to avoid the potential for webs of interdependencies between extensions.
Although this is restrictive; we believe it is better to start with restrictive guidelines then allow future flexibility as needs evolve.

## Path to Active

### Acceptance Criteria

- [ ] The interface is implemented and supported by various wallet providers.
- [ ] The interface is used by dApps to interact with wallet providers.
- [ ] Multiple extensions are developed and implemented.

### Implementation Plan

- [ ] Measure appetite for this proposal with wallet providers.

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).