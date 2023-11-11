---
CIP: ???
Title: Cardano dApp-MutlisigWallet Web Bridge
Status: Proposed
Category: Wallets
Authors: 
  - Leo
Implementors: NA
Discussions:
Created: 2023-10-12
License: CC-BY-4.0
---

## Abstract

This document describes a webpage-based communication bridge allowing webpages (i.e. dApps) to interface with Cardano Multisig-wallets. It follows the specification format of CIP-30 as it attempts to make implementing this connector as easy as possible for applications that have already successfully implemented CIP-30. This document is a work in progress and is not yet finalized. It is expected to be updated as the ecosystem evolves. 


## Motivation: why is this CIP necessary?

In order to facilitate future dApp development, we will need a way for dApps to communicate with multisig wallets, given the unique complexities of native script based address special provisions need to be made to make the connector compatible with them.  

Specifically apps building transactions need to be able to get the following information from the wallet:
- Script descriptor 
- Script Requirements list 
- Collateral donator (since native script based addresses cannot provide collateral for transactions)

Additionally apps need to be able to submit a transaction to the wallet for signing in an asynchronous manner, as gathering of signatures can take a long time and each wallet provider will have its own way of handling this process. 

## Specification

### Data Types

#### KeyHash

A hex-encoded string of the corresponding bytes. This represents the hash of the public key used to sign transactions.

```ts
type KeyHash = String
```


#### ScriptRequirements

```ts
type ScriptRequirementsCode = {
	Signer: 1,
	Before: 2,
	After: 3,
}
type ScriptRequirements = {
	code: ScriptRequirementsCode,
	value: KeyHash|number,
}
```

#### Address

A string representing an address in either bech32 format, or hex-encoded bytes. All return types containing `Address` must return the hex-encoded bytes format, but must accept either format for inputs.

#### Bytes

A hex-encoded string of the corresponding bytes.

#### cbor\<T>

A hex-encoded string representing [CBOR](https://tools.ietf.org/html/rfc7049) corresponding to `T` defined via [CDDL](https://tools.ietf.org/html/rfc8610) either inside of the [Shelley Multi-asset binary spec](https://github.com/input-output-hk/cardano-ledger-specs/blob/0738804155245062f05e2f355fadd1d16f04cd56/shelley-ma/shelley-ma-test/cddl-files/shelley-ma.cddl) or, if not present there, from the [CIP-0008 signing spec](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0008/README.md).
This representation was chosen when possible as it is consistent across the Cardano ecosystem and widely used by other tools, such as [cardano-serialization-lib](https://github.com/Emurgo/cardano-serialization-lib), which has support to encode every type in the binary spec as CBOR bytes.

#### DataSignature

```ts
type DataSignature = {|
  signature: cbor\<COSE_Sign1>,
  key: cbor\<COSE_Key>,
|};
```

#### TransactionUnspentOutput

If we have CBOR specified by the following CDDL referencing the Shelley-MA CDDL:

```cddl
transaction_unspent_output = [
  input: transaction_input,
  output: transaction_output,
]
```

then we define

```ts
type TransactionUnspentOutput = cbor<transaction_unspent_output>
```

This allows us to use the output for constructing new transactions using it as an output as the `transaction_output` in the Shelley Multi-asset CDDL does not contain enough information on its own to spend it.

#### Paginate

```ts
type Paginate = {|
  page: number,
  limit: number,
|};
```
Used to specify optional pagination for some API calls. Limits results to {limit} each page, and uses a 0-indexing {page} to refer to which of those pages of {limit} items each. dApps should be aware that if a wallet is modified between paginated calls that this will change the pagination, e.g. some results skipped or showing up multiple times but otherwise the wallet must respect the pagination order.

#### Extension

An extension is an object with a single field `"cip"` that describes a CIP number extending the API (as a plain integer, without padding). For example:

```ts
{ "cip": 30 }
```

### Error Types

#### APIError


```ts
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


#### PaginateError

```ts
type PaginateError = {|
    maxSize: number,
|};
```
{maxSize} is the maximum size for pagination and if the dApp tries to request pages outside of this boundary this error is thrown.

#### TxError

```ts
TxErrorCode = {
	Refused: 1,
	Failure: 2,
}
type TxError = {
	code: TxErrorCode,
	info: String
}
```

* Refused - Wallet refuses to send the tx (could be rate limiting)
* Failure - Wallet could not send the tx

#### CompletedTxError

```ts
CompletedTxErrorCode = {
	NotFound: 1,
	NotReady: 2
}
```

* NotFound - The transaction with the given id was not found.
* NotReady - The transaction with the given id is not ready yet. 

### Initial API

In order to initiate communication from webpages to a user's Cardano wallet, the wallet must provide the following javascript API to the webpage. A shared, namespaced `cardanoMultisig` object must be injected into the page if it did not exist already. Each wallet implementing this standard must then create a field in this object with a name unique to each wallet containing a `wallet` object with the following methods. The API is split into two stages to maintain the user's privacy, as the user will have to consent to `cardanoMultisig.{walletName}.enable()` in order for the dApp to read any information pertaining to the user's wallet with `{walletName}` corresponding to the wallet's namespaced name of its choice.

#### cardanoMultisig.{walletName}.enable({ extensions: Extension[] } = {}): Promise\<API>

Errors: `APIError`

This is the entrypoint to start communication with the user's wallet. The wallet should request the user's permission to connect the web page to the user's wallet, and if permission has been granted, the full API will be returned to the dApp to use. The wallet can choose to maintain a whitelist to not necessarily ask the user's permission every time access is requested, but this behavior is up to the wallet and should be transparent to web pages using this API. If a wallet is already connected this function should not request access a second time, and instead just return the `API` object.

Upon start, dApp can explicitly request a list of additional functionalities they expect as a list of CIP numbers capturing those extensions. This is used as an extensibility mechanism to document what functionalities can be provided by the wallet interface. CIP-0030 provides a set of base interfaces that every wallet must support. Then, new functionalities are introduced via additional CIPs and may be all or partially supported by wallets.

dApps are expected to use this endpoint to perform an initial handshake and ensure that the wallet supports all their required functionalities. Note that it's possible for two extensions to be mutually incompatible (because they provide two conflicting features). While we may try to avoid this as much as possible while designing CIPs, it is also the responsability of wallet providers to assess whether they can support a given combination of extensions, or not. Hence wallets aren't expected to fail should they not recognize or not support a particular combination of extensions. Instead, they should decide what they enable and reflect their choice in the response to `api.getExtensions()` in the Full API. As a result, dApps may fail and inform their users or may use a different, less-efficient, strategy to cope with a lack of functionality.

It is at the extension author's discretion if they wish to separate their endpoints from the base API via namespacing. Although, it is highly recommend that authors do namespace all of their extensions. If namespaced, endpoints must be preceded by `.cipXXXX.` from the `API` object, without any leading zeros.

For example; CIP-0123's endpoints should be accessed by:
```ts
api.cip123.endpoint1()
api.cip123.endpoint2()
```

Authors should be careful when omitting namespacing. Omission should only be considered when creating endpoints to override those defined in this specification or other extensions. Even so when overriding; the new functionality should not prevent dApps from accessing past functionality thus overriding must ensure backwards compatibility.

Any namespace omission needs to be fully justified via the proposal's Rationale section, with explanation to why it is necessary. Any potential backwards compatibility considerations should be noted to give wallets and dApps a clear unambiguous direction.

##### Draft or Experimental Extensions

Extensions that are draft, in development, or prototyped should not use extension naming nor should they use official namspacing until assigned a CIP number. Draft extension authors are free to test their implementation endpoints by using the [Experimental API](#experimental-api). Once a CIP number is assigned implementors should move functionality out of the experimental API.

##### Can extensions depend on other extensions?

Yes. Extensions may have other extensions as pre-requisite. Some newer extensions may also invalidate functionality introduced by earlier extensions. There's no particular rule or constraints in that regards. Extensions are specified as CIP, and will define what it entails to enable them.

##### Should extensions follow a specific format?

Yes. They all are CIPs.

##### Can extensions add their own endpoints and/or error codes?

Yes. Extensions may introduce new endpoints or error codes, and modify existing ones. Although, it is recommended that endpoints are namespaced. Extensions may even change the rules outlined in this very proposal. The idea being that wallet providers should start off implementing this CIP, and then walk their way to implementing their chosen extensions.

##### Are wallet expected to implement all extensions?

No. It's up to wallet providers to decide which extensions they ought to support.


#### cardanoMultisig.{walletName}.isEnabled(): Promise\<bool>

Errors: `APIError`

Returns true if the dApp is already connected to the user's wallet, or if requesting access would return true without user confirmation (e.g. the dApp is whitelisted), and false otherwise. If this function returns true, then any subsequent calls to `wallet.enable()` during the current session should succeed and return the `API` object.

#### cardanoMultisig.{walletName}.apiVersion: String

The version number of the API that the wallet supports. Set to `1`.

#### cardanoMultisig.{walletName}.supportedExtensions: Extension[]

A list of extensions supported by the wallet. Extensions may be requested by dApps on initialization. Some extensions may be mutually conflicting and this list does not thereby reflect what extensions will be enabled by the wallet. Yet it informs on what extensions are known and can be requested by dApps if needed.

#### cardanoMultisig.{walletName}.name: String

A name for the wallet which can be used inside of the dApp for the purpose of asking the user which wallet they would like to connect with.

#### cardanoMultisig.{walletName}.icon: String

A URI image (e.g. data URI base64 or other) for img src for the wallet which can be used inside of the dApp for the purpose of asking the user which wallet they would like to connect with.

### Full API

Upon successful connection via `cardanoMultisig.{walletName}.enable()`, a javascript object we will refer to as `API` (type) / `api` (instance) is returned to the dApp with the following methods. All read-only methods (all but the signing functionality) should not require any user interaction as the user has already consented to the dApp reading information about the wallet's state when they agreed to `cardanoMultisig.{walletName}.enable()`. The remaining methods `api.signTx()` and `api.signData()` must request the user's consent in an informative way for each and every API call in order to maintain security.

The API chosen here is for the minimum API necessary for dApp <-> Wallet interactions without convenience functions that don't strictly need the wallet's state to work. The API here is for now also only designed for Shelley's Mary hardfork and thus has NFT support. When Alonzo is released with Plutus support this API will have to be extended.

#### api.getExtensions(): Promise\<Extension[]>

Errors: `APIError`

Retrieves the list of extensions enabled by the wallet. This may be influenced by the set of extensions requested in the initial `enable` request.

#### api.getNetworkId(): Promise\<number>

Errors: `APIError`

Returns the network id of the currently connected account. 0 is testnet and 1 is mainnet but other networks can possibly be returned by wallets. Those other network ID values are not governed by this document. This result will stay the same unless the connected account has changed.

#### api.getUtxos(amount: cbor\<value> = undefined, paginate: Paginate = undefined): Promise\<TransactionUnspentOutput[] | null>

Errors: `APIError`, `PaginateError`

If `amount` is `undefined`, this shall return a list of all UTXOs (unspent transaction outputs) controlled by the wallet. If `amount` is not `undefined`, this request shall be limited to just the UTXOs that are required to reach the combined ADA/multiasset value target specified in `amount`, and if this cannot be attained, `null` shall be returned. The results can be further paginated by `paginate` if it is not `undefined`.

#### api.getCollateral(params: { amount: cbor\<Coin> }): Promise\<TransactionUnspentOutput[] | null>

Errors: `APIError`

Native script based addresses cannot provide collateral for transactions. Using this function dApps can request the wallet to provide collateral for a transaction. The collateral must be a pure ADA UTXO, held by one of the signers in the list of signers returned by `api.getScriptRequirements()`.

dApp developers using this function should ensure that the collateral is returned to the original address, which should always be different from the change address. 

The function takes a required object with parameters. With a single **required** parameter for now: `amount`. (**NOTE:** some wallets may be ignoring the amount parameter, in which case it might be possible to call the function without it, but this behavior is not recommended!). Reasons why the `amount` parameter is required:
1. dApps must be motivated to understand what they are doing with the collateral, in case they decide to handle it manually.
2. Depending on the specific wallet implementation, requesting more collateral than necessary might worsen the user experience with that dapp, as it could require unnecessary wallet reorganisation.
3. If dApps don't understand how much collateral they actually need to make their transactions work - they are placing more user funds than necessary in risk.

So, requiring the amount parameter would be a behavior specified by the wallet.

This shall return a list of one or more UTXOs (unspent transaction outputs) controlled by the wallet that are required to reach **AT LEAST** the combined ADA value target specified in `amount` **AND** the best suitable to be used as collateral inputs for transactions with plutus script inputs (pure ADA-only utxos). If this cannot be attained, an error message with an explanation of the blocking problem shall be returned. **NOTE:** wallets are free to return utxos that add up to a **greater** total ADA value than requested in the `amount` parameter, but wallets must never return any result where utxos would sum up to a smaller total ADA value, instead in a case like that an error message must be returned.

The main point is to allow the wallet to encapsulate all the logic required to handle, maintain, and create (possibly on-demand) the UTXOs suitable for collateral inputs. For example, whenever attempting to create a plutus-input transaction the dapp might encounter a case when the set of all user UTXOs don't have any pure entries at all, which are required for the collateral, in which case the dapp itself is forced to try and handle the creation of the suitable entries by itself. If a wallet implements this function it allows the dapp to not care whether the suitable utxos exist among all utxos, or whether they have been stored in a separate address chain (see https://github.com/cardano-foundation/CIPs/pull/104), or whether they have to be created at the moment on-demand - the wallet guarantees that the dapp will receive enough utxos to cover the requested amount, or get an error in case it is technically impossible to get collateral in the wallet (e.g. user does not have enough ADA at all).

The `amount` parameter is required, specified as a `string` (BigNumber) or a `number`, and the maximum allowed value must be agreed to be something like 5 ADA. Not limiting the maximum possible value might force the wallet to attempt to purify an unreasonable amount of ADA just because the dapp is doing something weird. Since by protocol the required collateral amount is always a percentage of the transaction fee, it seems that the 5 ADA limit should be enough for the foreseeable future.

#### api.getCollateralAddress(): Promise\<Address>

For plutus V2 and later, partial collateral is supported. This function returns an address that can be used to add collateral to a transaction. The address returned must be owned by one of the signers in the list of signers returned by `api.getScriptRequirements()`. 

dApp developers can chose to use this address to add collateral to a transaction, or they can chose to use the `api.getCollateral()` function to get a list of UTXOs that can be used as collateral. If the dApp chooses to use this address, they must ensure that the address is not used for any other purpose, as the wallet may be using it to track collateral, and that the collateral return address is the same one.

#### api.getBalance(): Promise\<cbor\<value>>

Errors: `APIError`

Returns the total balance available of the wallet. This is the same as summing the results of `api.getUtxos()`, but it is both useful to dApps and likely already maintained by the implementing wallet in a more efficient manner so it has been included in the API as well.

#### api.getUsedAddresses(paginate: Paginate = undefined): Promise\<Address[]>

Errors: `APIError`

Returns a list of all used (included in some on-chain transaction) addresses controlled by the wallet. The results can be further paginated by `paginate` if it is not `undefined`.

#### api.getUnusedAddresses(): Promise\<Address[]>

Errors: `APIError`

Returns a list of unused addresses controlled by the wallet.

#### api.getChangeAddress(): Promise\<Address>

Errors: `APIError`

Returns an address owned by the wallet that should be used as a change address to return leftover assets during transaction creation back to the connected wallet. This can be used as a generic receive address as well.

#### api.getRewardAddresses(): Promise\<Address[]>

Errors: `APIError`

Returns the reward addresses owned by the wallet. This can return multiple addresses e.g. CIP-0018.

#### api.getScriptRequirements: Promise\<ScriptRequirement[]>

Errors: `APIError`

Returns a list of ScriptRequirements that will be used to validate any transaction sent to the wallet.

#### api.getScript(): Promise\<cbor\<nativeScript>>

Errors: `APIError`

Returns the CBOR-encoded native script that controls this wallet. 

#### api.submitUnsignedTx(tx: cbor\<unsignedTransaction>): Promise\<hash32>

Errors: `APIError`, `TxError`

Submits a transaction to the wallet for signing. The wallet should check that the transaction is valid, gather the required signatures, compose the finalized transaction, and submit the transaction to the network. If the transaction is valid and the wallet is able to sign it, the wallet should return the transaction hash. If the transaction is invalid or the wallet is unable to sign it, the wallet should throw a `TxError` with the appropriate error code. The wallet should not submit the transaction to the network if it is invalid or the wallet is unable to sign it.

If the transaction contains hidden metadata, the wallet should submit the transaction when it is ready, but return it to the dApp when the dApp calls the `getCompletedTx` function.

#### api.getCompletedTx(txId: hash32): Promise\<cbor\<transaction>>

Errors: `APIError`, `CompletedTxError`

If the transaction is not ready, the wallet should throw a `CompletedTxError` with the appropriate error code. If the transaction is ready, the wallet should return the CBOR-encoded completed transaction.

#### api.submitTx(tx: cbor\<transaction>): Promise\<hash32>

Errors: `APIError`, `TxError`

As wallets should already have this ability, we allow dApps to request that a transaction be sent through it. If the wallet accepts the transaction and tries to send it, it shall return the transaction id for the dApp to track. The wallet is free to return the `TxError` with code `Refused` if they do not wish to send it, or `Failure` if there was an error in sending it (e.g. preliminary checks failed on signatures).

### Experimental API

Multiple experimental namespaces are used:
- under `api` (ex: `api.experimental.myFunctionality`).
- under `cardanoMultisig.{walletName}` (ex: `window.cardanoMultisig.{walletName}.experimental.myFunctionality`)

The benefits of this are:
1. Wallets can add non-standardized features while still following the CIP30 structure
1. dApp developers can use these functions explicitly knowing they are experimental (not stable or standardized)
1. New features can be added to CIP30 as experimental features and only moved to non-experimental once multiple wallets implement it
1. It provides a clear path to updating the CIP version number (when functions move from experimental -> stable)

## Rationale: how does this CIP achieve its goals?

See justification and explanations provided with each API endpoint.

### Extensions

Extensions provide an extensibility mechanism and a way to negotiate (possibly conflicting) functionality between a DApp and a wallet provider. There's rules enforced as for what extensions a wallet decide to support or enable. The current mechanism only gives a way for wallets to communicate their choice back to a DApp.

We use object as extensions for now to leave room for adding fields in the future without breaking all existing interfaces. At this point in time however, objects are expected to be singleton.

Extensions can be seen as a smart versioning scheme. Except that, instead of being a monotonically increasing sequence of numbers, they are multi-dimensional feature set that can be toggled on and off at will. This is a versioning "à-la-carte" which is useful in a context where:

1. There are multiple concurrent standardization efforts on different fronts to accommodate a rapidly evolving ecosystem;
2. Not everyone agrees and has desired to support every existing standard;
3. There's a need from an API consumer standpoint to clearly identify what features are supported by providers.

#### Namespacing Extensions

By encouraging the explicit namespacing of each extension we aim to improve the usability of extensions for dApps. By allowing special cases where namespacing can be dropped we maintain good flexibility in extension design.

## Path to Active

### Acceptance Criteria

- [ ] The interface is implemented and supported by various wallet providers.
- [ ] The interface is used by dApps to interact with wallet providers. 
  
### Implementation Plan

- [ ] Provide some reference implementation of wallet providers
  - [leo42/BroClanWallet]
## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
