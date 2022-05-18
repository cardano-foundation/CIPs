---
CIP: 30
Title: Cardano dApp-Wallet Web Bridge
Authors: rooooooooob
Comments-URI: https://github.com/cardano-foundation/CIPs/pull/88
Status: Draft
Type: Standards
Created: 2021-04-29
License: CC-BY-4.0
---

# Abstract

This documents describes a webpage-based communication bridge allowing webpages (i.e. dApps) to interface with Cardano wallets. This is done via injected javascript code into webpages. This specification defines the manner that such code is to be accessed by the webpage/dApp, as well as defining the API for dApps to communicate with the user's wallet. This document currently concerns the Shelley-Mary era but will have a second version once Plutus is supported. This specification is intended to cover similar use cases as web3 for Ethereum or [EIP-0012](https://github.com/ergoplatform/eips/pull/23) for Ergo. The design of this spec was based on the latter.


# Motivation

In order to facilitate future dApp development, we will need a way for dApps to communicate with the user's wallet. While Cardano does not yet support smart contracts, there are still various use cases for this, such as NFT management. This will also lay the groundwork for an updated version of the spec once the Alonzo hardfork is released which can extend it to allow for Plutus support.



# Specification

## Version

The API specified in this document will count as version 0.1.0 for version-checking purposes below.

## Data Types

### Address

A string represnting an address in either bech32 format, or hex-encoded bytes. All return types containing `Address` must return the bech32 format, but must accept either format for inputs.

### Bytes

A hex-encoded string of the corresponding bytes.

### cbor\<T>

A hex-encoded string representing [CBOR](https://tools.ietf.org/html/rfc7049) corresponding to `T` defined via [CDDL](https://tools.ietf.org/html/rfc8610) either inside of the [Shelley Mult-asset binary spec](https://github.com/input-output-hk/cardano-ledger-specs/blob/0738804155245062f05e2f355fadd1d16f04cd56/shelley-ma/shelley-ma-test/cddl-files/shelley-ma.cddl) or, if not present there, from the [CIP-0008 signing spec](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0008/CIP-0008.md).
This representation was chosen when possible as it is consistent across the Cardano ecosystem and widely used by other tools, such as [cardano-serialization-lib](https://github.com/Emurgo/cardano-serialization-lib), which has support to encode every type in the binary spec as CBOR bytes.

### DataSignature

```
type DataSignature = {|
  signature:cbor\<COSE_Sign1>,
  key: cbor\<COSE_Key>,
|};
```

### TransactionUnspentOutput

If we have CBOR specified by the following CDDL referencing the Shelley-MA CDDL:
```cddl
transaction_unspent_output = [
  input: transaction_input,
  output: transaction_output,
]
```
then we define
```
type TransactionUnspentOutput = cbor<transaction_unspent_output>
```

This allows us to use the output for constructing new transactions using it as an output as the `transaction_output` in the Shelley Multi-asset CDDL does not contain enough information on its own to spend it.

### Paginate

```
type Paginate = {|
  page: number,
  limit: number,
|};
```
Used to specify optional pagination for some API calls. Limits results to {limit} each page, and uses a 0-indexing {page} to refer to which of those pages of {limit} items each. dApps should be aware that if a wallet is modified between paginated calls that this will change the pagination, e.g. some results skipped or showing up multiple times but otherwise the wallet must respect the pagination order.


## Error Types

### APIError

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

### DataSignError

```
DataSignErrorCode {
	ProofGeneration: 1,
	AddressNotPK: 2,
	UserDeclined: 3,
}
type DataSignError = {
	code: DataSignErrorCode,
	info: String
}
```

* ProofGeneration - Wallet could not sign the data (e.g. does not have the secret key associated with the address)
* AddressNotPK - Address was not a P2PK address and thus had no SK associated with it.
* UserDeclined - User declined to sign the data

### PaginateError

```
type PaginateError = {|
    maxSize: number,
|};
```
{maxSize} is the maximum size for pagination and if the dApp tries to request pages outside of this boundary this error is thrown.

### TxSendError

```
TxSendErrorCode = {
	Refused: 1,
	Failure: 2,
}
type TxSendError = {
	code: TxSendErrorCode,
	info: String
}
```

* Refused - Wallet refuses to send the tx (could be rate limiting)
* Failure - Wallet could not send the tx

### TxSignError

```
TxSignErrorCode = {
	ProofGeneration: 1,
	UserDeclined: 2,
}
type TxSignError = {
	code: TxSignErrorCode,
	info: String
}
```

* ProofGeneration - User has accepted the transaction sign, but the wallet was unable to sign the transaction (e.g. not having some of the private keys)
* UserDeclined - User declined to sign the transaction



## Initial API

In order to initiate communication from webpages to a user's Cardano wallet, the wallet must provide the following javascript API to the webpage. A shared, namespaced `cardano` object must be injected into the page if it did not exist already. Each wallet implementing this standard must then create a field in this object with a name unique to each wallet containing a `wallet` object with the following methods. The API is split into two stages to maintain the user's privacy, as the user will have to consent to `cardano.{walletName}.enable()` in order for the dApp to read any information pertaining to the user's wallet with `{walletName}` corresponding to the wallet's namespaced name of its choice.

### cardano.{walletName}.enable(): Promise\<API>

Errors: APIError

This is the entrypoint to start communication with the user's wallet. The wallet should request the user's permission to connect the web page to the user's wallet, and if permission has been granted, the full API will be returned to the dApp to use. The wallet can choose to maintain a whitelist to not necessarily ask the user's permission every time access is requested, but this behavior is up to the wallet and should be transparent to web pages using this API. If a wallet is already connected this function should not request access a second time, and instead just return the `API` object.

### cardano.{walletName}.isEnabled(): Promise\<bool>

Errors: APIError

Returns true if the dApp is already connected to the user's wallet, or if requesting access would return true without user confirmation (e.g. the dApp is whitelisted), and false otherwise. If this function returns true, then any subsequent calls to `wallet.enable()` during the current session should succeed and return the `API` object.

### cardano.{walletName}.apiVersion: String

The version number of the API that the wallet supports.


### cardano.{walletName}.name: String

A name for the wallet which can be used inside of the dApp for the purpose of asking the user which wallet they would like to connect with.

### cardano.{walletName}.icon: String

A URI image (e.g. data URI base64 or other) for img src for the wallet which can be used inside of the dApp for the purpose of asking the user which wallet they would like to connect with.


## Full API

Upon successful connection via `cardano.{walletName}.enable()`, a javascript object we will refer to as `API` (type) / `api` (instance) is returned to the dApp with the following methods. All read-only methods (all but the signing functionality) should not require any user interaction as the user has already consented to the dApp reading information about the wallet's state when they agreed to `cardano.{walletName}.enable()`. The remaining methods `api.signTx()` and `api.signData()` must request the user's consent in an informative way for each and every API call in order to maintain security.

The API chosen here is for the minimum API necessary for dApp <-> Wallet interactions without convenience functions that don't strictly need the wallet's state to work. The API here is for now also only designed for Shelley's Mary hardfork and thus has NFT support. When Alonzo is released with Plutus support this API will have to be extended.

### api.getNetworkId(): Promise\<number>

Errors: `APIError`

Returns the network id of the currently connected account. 0 is testnet and 1 is mainnet but other networks can possibly be returned by wallets. Those other network ID values are not governed by this document. This result will stay the same unless the connected account has changed.

### api.getUtxos(amount: cbor\<value> = undefined, paginate: Paginate = undefined): Promise\<TransactionUnspentOutput[] | null>

Errors: `APIError`, `PaginateError`

If `amount` is `undefined`, this shall return a list of all UTXOs (unspent transaction outputs) controlled by the wallet. If `amount` is not `undefined`, this request shall be limited to just the UTXOs that are required to reach the combined ADA/multiasset value target specified in `amount`, and if this cannot be attained, `null` shall be returned. The results can be further paginated by `paginate` if it is not `undefined`.

### api.getCollateral(params: { amount: cbor\<Coin> }): Promise\<TransactionUnspentOutput[] | null>

Errors: `APIError`

The function takes a required object with parameters. With a single **required** parameter for now: `amount`. (**NOTE:** some wallets may be ignoring the amount parameter, in which case it might be possible to call the function without it, but this behavior is not recommended!). Reasons why the `amount` parameter is required:
1. Dapps must be motivated to understand what they are doing with the collateral, in case they decide to handle it manually.
2. Depending on the specific wallet implementation, requesting more collateral than necessarily might worsen the user experience with that dapp, requiring the wallet to make explicit wallet reorganisation when it is not necessary and can be avoided.
3. If dapps don't understand how much collateral they actually need to make their transactions work - they are placing more user funds than necessary in risk.

So requiring the `amount` parameter would be a by-spec behavior for a wallet. Not requiring it is possible, but not specified, so dapps should not rely on that and the behavior is not recommended.

This shall return a list of one or more UTXOs (unspent transaction outputs) controlled by the wallet that are required to reach **AT LEAST** the combined ADA value target specified in `amount` **AND** the best suitable to be used as collateral inputs for transactions with plutus script inputs (pure ADA-only utxos). If this cannot be attained, an error message with an explanation of the blocking problem shall be returned. **NOTE:** wallets are free to return utxos that add up to a **greater** total ADA value than requested in the `amount` parameter, but wallets must never return any result where utxos would sum up to a smaller total ADA value, instead in a case like that an error message must be returned.

The main point is to allow the wallet to encapsulate all the logic required to handle, maintain, and create (possibly on-demand) the UTXOs suitable for collateral inputs. For example, whenever attempting to create a plutus-input transaction the dapp might encounter a case when the set of all user UTXOs don't have any pure entries at all, which are required for the collateral, in which case the dapp itself is forced to try and handle the creation of the suitable entries by itself. If a wallet implements this function it allows the dapp to not care whether the suitable utxos exist among all utxos, or whether they have been stored in a separate address chain (see https://github.com/cardano-foundation/CIPs/pull/104), or whether they have to be created at the moment on-demand - the wallet guarantees that the dapp will receive enough utxos to cover the requested amount, or get an error in case it is technically impossible to get collateral in the wallet (e.g. user does not have enough ADA at all).

The `amount` parameter is required, specified as a `string` (BigNumber) or a `number`, and the maximum allowed value must be agreed to be something like 5 ADA. Not limiting the maximum possible value might force the wallet to attempt to purify an unreasonable amount of ADA just because the dapp is doing something weird. Since by protocol the required collateral amount is always a percentage of the transaction fee, it seems that the 5 ADA limit should be enough for the foreseable future.

### api.getBalance(): Promise\<cbor\<value>>

Errors: `APIError`

Returns the total balance available of the wallet. This is the same as summing the results of `api.getUtxos()`, but it is both useful to dApps and likely already maintained by the implementing wallet in a more efficient manner so it has been included in the API as well.

### api.getUsedAddresses(paginate: Paginate = undefined): Promise\<Address[]>

Errors: `APIError`

Returns a list of all used (included in some on-chain transaction) addresses controlled by the wallet. The results can be further paginated by `paginate` if it is not `undefined`.

### api.getUnusedAddresses(): Promise\<Address[]>

Errors: `APIError`

Returns a list of unused addresses controlled by the wallet.

### api.getChangeAddress(): Promise\<Address>

Errors: `APIError`

Returns an address owned by the wallet that should be used as a change address to return leftover assets during transaction creation back to the connected wallet. This can be used as a generic receive address as well.

### api.getRewardAddresses(): Promise\<Address[]>

Errors: `APIError`

Returns the reward addresses owned by the wallet. This can return multiple addresses e.g. CIP-0018.

### api.signTx(tx: cbor\<transaction>, partialSign: bool = false): Promise\<cbor\<transaction_witness_set>>

Errors: `APIError`, `TxSignError`

Requests that a user sign the unsigned portions of the supplied transaction. The wallet should ask the user for permission, and if given, try to sign the supplied body and return a signed transaction. If `partialSign` is true, the wallet only tries to sign what it can. If `partialSign` is false and the wallet could not sign the entire transaction, `TxSignError` shall be returned with the `ProofGeneration` code. Likewise if the user declined in either case it shall return the `UserDeclined` code. Only the portions of the witness set that were signed as a result of this call are returned to encourage dApps to verify the contents returned by this endpoint while building the final transaction.

### api.signData(addr: Address, payload: Bytes): Promise\<DataSignature>

Errors: `APIError`, `DataSignError`

This endpoint utilizes the [CIP-0008 signing spec](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0008/CIP-0008.md) for standardization/safety reasons. It allows the dApp to request the user to sign a payload conforming to said spec. The user's consent should be requested and the message to sign shown to the user. The payment key from `addr` will be used for base, enterprise and pointer addresses to determine the EdDSA25519 key used. The staking key will be used for reward addresses. This key will be used to sign the `COSE_Sign1`'s `Sig_structure` with the following headers set:

* `alg` (1) - must be set to `EdDSA` (-8)
* `kid` (4) - Optional, if present must be set to the same value as in the `COSE_key` specified below. It is recommended to be set to the same value as in the `"address"` header.
* `"address"` - must be set to the raw binary bytes of the address as per the binary spec, without the CBOR binary wrapper tag

The payload is not hashed and no `external_aad` is used.

If the payment key for `addr` is not a P2Pk address then `DataSignError` will be returned with code `AddressNotPK`. `ProofGeneration` shall be returned if the wallet cannot generate a signature (i.e. the wallet does not own the requested payment private key), and `UserDeclined` will be returned if the user refuses the request. The return shall be a `DataSignature` with `signature` set to the hex-encoded CBOR bytes of the `COSE_Sign1` object specified above and `key` shall be the hex-encoded CBOR bytes of a `COSE_Key` structure with the following headers set:

* `kty` (1) - must be set to `OKP` (1)
* `kid` (2) - Optional, if present must be set to the same value as in the `COSE_Sign1` specified above.
* `alg` (3) - must be set to `EdDSA` (-8)
* `crv` (-1) - must be set to `Ed25519` (6)
* `x` (-2) - must be set to the public key bytes of the key used to sign the `Sig_structure`

### api.submitTx(tx: cbor\<transaction>): Promise\<hash32>

Errors: `APIError`, `TxSendError`

As wallets should already have this ability, we allow dApps to request that a transaction be sent through it. If the wallet accepts the transaction and tries to send it, it shall return the transaction id for the dApp to track. The wallet is free to return the `TxSendError` with code `Refused` if they do not wish to send it, or `Failure` if there was an error in sending it (e.g. preliminary checks failed on signatures).

## Experimental API

Multiple experimental namespaces are used:
- under `api` (ex: `api.experimental.myFunctionality`).
- under `cardano.{walletName}` (ex: `window.cardano.{walletName}.experimental.myFunctionality`)

The benefits of this are:
1. Wallets can add non-standardized features while still following the CIP30 structure
1. dApp developers can use these functions explicitly knowing they are experimental (not stable or standardized)
1. New features can be added to CIP30 as experimental features and only moved to non-experimental once multiple wallets implement it
1. It provides a clear path to updating the CIP version number (when functions move from experimental -> stable)

# Implementations

[nami-wallet](https://github.com/Berry-Pool/nami-wallet/blob/master/src/pages/Content/injected.js)

[yoroi-wallet](https://github.com/Emurgo/yoroi-frontend/blob/develop/packages/yoroi-ergo-connector/src/inject.js)
