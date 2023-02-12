---
CIP: ????
Title: Extendable dApp-Wallet Web Bridge
Category: Wallets
Status: Proposed
Authors:
    - Ryan Williams <ryan.williams@iohk.io>
    - Martynas Kazlauskas <martynas.kazlauskas@iohk.io>
    - Matthias Benkort <matthias.benkort@cardanofoundation.org>
Implementors: []
Discussions:
    - https://github.com/cardano-foundation/CIPs/pull/446
    - https://github.com/cardano-foundation/cips/pulls/?
Created: 2022-02-12
License: CC-BY-4.0
---

## Abstract

This document describes a *base* dApp-Wallet communication bridge accompanied by an extension scheme from which functionality can be added through extensions.

This specification defines the manner which javascript code is injected into webpages, accessed by the webpage/dApp, as well as defining the API for dApps to communicate with the user's wallet.

## Motivation: why is this CIP necessary?

This *base* API intends to standardize the initial dApp-Wallet connection while defining a path for how functionality can be enhanced through future CIP extensions. All wallet providers are expected to support this API with future extensions supported at the wallet's discretion.

[CIP-30 | Cardano dApp-Wallet Web Bridge](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0030) facilitated the launch of dApp development on Cardano. Yet it's functionality is limited in scope leading to multiple revisions of the specification. Causing divergence between capabilities of wallet implementations, making the development of compatible dApps cumbersome and error-prone.

This proposal aims to act as a skeleton from which functionality can be fleshed out in a modular fashion. With the first supported extension containing CIP-30's `Full API` functionality. This proposal lifts the `Initial API` from CIP-30 and places it here. This is an attempt to improve the backwards compatibility of this proposal as by implementing this proposal no CIP-30 functionality is lost.

This proposal is intended for dApp creators and Cardano wallet providers, with broad application to various types of Web3 applications.

## Specification

### Data Types

#### Extension

An extension is an object with a single field `"cip"` that describe a CIP number extending the API (as a plain integer, without padding). For example:

```
{ "cip": 30 }
```
##### Known Extensions

This should act as the definitive list of known and accepted extensions, all extensions which have  been processed through the CIP process should be added here. 

| CIP    | Scope                           |
| ------ | ------------------------------- |
| CIP-30 | Base interface                  |

##### Can extensions add their own datatypes?

Yes.

##### Can extensions extend the initial API?

No. Only if this specification itself if replaced.

##### Can extensions depend on other extensions?

Yes. Extensions may have other extensions as pre-requisite. Some newer extensions may also invalidate functionality introduced by earlier extensions. There's no particular rule or constraints in that regards. Extensions are specified as CIP, and will define what it entails to enable them.

##### Should extensions follow a specific format?

Yes. They all are CIPs.

##### Can extensions add their own endpoints and/or error codes?

Yes. Extensions may introduce new endpoints or error codes, and modify existing ones. Extensions may even change the rules outlined in this very proposal. The idea being that wallet providers should start off implementing this CIP, and then walk their way to implementing their chosen extensions.

##### Are wallet expected to implement all extensions?

No. It's up to wallet providers to decide which extensions they ought to support.

### Error Types

#### APIError

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

* InvalidRequest - Inputs do not conform to this spec or are otherwise invalid.
* InternalError - An error occurred during execution of this API call.
* Refused - The request was refused due to lack of access - e.g. wallet disconnects.
* AccountChange - The account has changed. The dApp should call `wallet.enable()` to reestablish connection to the new account. The wallet should not ask for confirmation as the user was the one who initiated the account change in the first place.

### Initial API

In order to initiate communication from webpages to a user's Cardano wallet, the wallet must provide the following javascript API to the webpage. A shared, namespaced `cardano` object must be injected into the page if it did not exist already. Each wallet implementing this standard must then create a field in this object with a name unique to each wallet containing a `wallet` object with the following methods. The API is split into two stages to maintain the user's privacy, as the user will have to consent to `cardano.{walletName}.enable()` in order for the dApp to read any information pertaining to the user's wallet with `{walletName}` corresponding to the wallet's namespaced name of its choice.

#### cardano.{walletName}.enable(extensions: Extension[] = []): Promise\<API>

Errors: APIError

This is the entrypoint to start communication with the user's wallet. The wallet should request the user's permission to connect the web page to the user's wallet, and if permission has been granted, the [Full API](#full-api) will be returned to the dApp to use. The wallet can choose to maintain a whitelist to not necessarily ask the user's permission every time access is requested. But this behavior is up to the wallet and should be transparent to web pages using this API. If a wallet is already connected this function should not request access a second time, and instead just return the `API` object.

Upon start, dApp can explicitly request a list of additional functionalities they expect as a list of CIP numbers capturing those extensions. This is used as an extensibility mechanism to document what functionalities can be provided by the wallet interface. New functionalities are introduced via additional CIPs and may be all or partially supported by wallets.

dApps are expected to use this endpoint to perform an initial handshake and ensure that the wallet supports all of their required functionalities. Note that it's possible for two extensions to be mutually incompatible (because they provide two conflicting features). While we may try to avoid this as much as possible while designing CIPs, it is also the responsibility of wallet providers to assess whether they can support a given combination of extensions, or not. Hence, wallets aren't expected to fail should they not recognize or not support a particular combination of extensions. Instead, they should decide what they enable and reflect their choice in the `cardano.{walletName}.extensions` field of the [Full API](#full-api). As a result, dApps may fail and inform their users or may use a different, less-efficient, strategy to cope with a lack of functionality.

**Note**: In order to preserve backwards compatibility an empty `extensions` field should supply CIP-30 functionality, as if a CIP-30 `extension` object was provided.

#### cardano.{walletName}.isEnabled(): Promise\<bool>

Errors: APIError

Returns true if the dApp is already connected to the user's wallet, or if requesting access would return true without user confirmation (e.g. the dApp is whitelisted), and false otherwise. If this function returns true, then any subsequent calls to `wallet.enable()` during the current session should succeed and return the `API` object.

#### cardano.{walletName}.supportedExtensions: Extension[]

A list of extensions supported by the wallet. Extensions may be requested by dApps on initialization. Some extensions may be mutually conflicting and this list does not thereby reflect what extensions will be enabled by the wallet. Yet it informs on what extensions are known and can be requested by dApps if needed.

#### cardano.{walletName}.name: String

A name for the wallet which can be used inside of the dApp for the purpose of asking the user which wallet they would like to connect with.

#### cardano.{walletName}.icon: String

A URI image (e.g. data URI base64 or other) for img src for the wallet which can be used inside of the dApp for the purpose of asking the user which wallet they would like to connect with.

### Full API

Upon successful connection via `cardano.{walletName}.enable()`, a javascript object we will refer to as `API` (type) / `api` (instance) is returned to the dApp with the following method.

This is where extensions are free to add functionality as they see fit. Furthermore extensions are free to include additional sections, naming their APIs as they see fit, an example could be an `Experimental API`.

#### api.getExtensions(): Promise\<Extension[]>

Retrieves the list of extensions enabled by the wallet. This may be influenced by the set of extensions requested in the initial `enable` request.

## Rationale: how does this CIP achieve its goals?

This API does not offer *useful* functionality for dApp-Wallet interactions; rather, all useful functionality should be offered through extensions. By keeping this API as a skeleton, we aim to avoid the chance of introducing functionality we come to regret later. Instead, this proposal should be the minimum foundation required to build on top of.  

The alternative to this proposal is the addition of extensions to CIP-30's specification. This would mean that the CIP-30 API would be included in all extended dApp-Wallet connections. With the current landscape of dApps and wallets this seems fine, but it is uncertain if we want to indefinitely support the CIP-30 API.

By stripping functionality from this API we facilitate dApp-Wallet connections with less functions than CIP-30 API. A use case for this is connections where minimal wallet information is wished to be shared with a dApp.

Here we attempt to mitigate the impact of succeeding CIP-30 as *the* Cardano wallet connector, by enabling it's functionality by default at connection time. This should minimize the impact this proposal could have on established dApps who support CIP-30. By only adding what is necessary for extensions we aim to reduce the required load for wallets to adopt this standard.

### Extensions

Extensions provide an extensibility mechanism and a way to negotiate (possibly conflicting) functionality between a dApp and a wallet provider. There's rules enforced as for what extensions a wallet decide to support or enable. The current mechanism only gives a way for wallets to communicate their choice back to a dApp.

We use object as extensions for now to leave room for adding fields in the future without breaking all existing interfaces. At this point in time however, objects are expected to be singleton.

Extensions can be seen as a smart versioning scheme. Except that, instead of being a monotonically increasing sequence of numbers, they are multi-dimensional feature set that can be toggled on and off at will. This is a versioning "à-la-carte" which is useful in a context where:

1. There are multiple concurrent standardization efforts on different fronts to accommodate a rapidly evolving ecosystem;
2. Not everyone agrees and has desired to support every existing standard;
3. There's a need from an API consumer standpoint to clearly identify what features are supported by providers.

By moving CIP-30 style modifications into a formalized extension scheme we aim to avoid fragmentation of functionality between different dApp-Wallet bridges.

## Path to Active

### Acceptance Criteria

- [ ] The interface is implemented and supported by various wallet providers.
- [ ] The interface is used by dApps to interact with wallet providers.

### Implementation Plan

- [ ] Measure appetite for this proposal with wallet providers.

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).