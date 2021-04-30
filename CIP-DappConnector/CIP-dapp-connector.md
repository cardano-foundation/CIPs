---
CIP: ?
Title: Cardano dApp-Wallet Web Bridge
Authors: rooooooooob
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

## Data Types

### Bytes

A hex-encoded string of the corresponding bytes.

### cbor\<T>

A hex-encoded string representing [CBOR](https://tools.ietf.org/html/rfc7049) corresponding to `T` defined via [CDDL](https://tools.ietf.org/html/rfc8610) either inside of the [Shelley Mary binary spec](https://github.com/input-output-hk/cardano-ledger-specs/blob/0738804155245062f05e2f355fadd1d16f04cd56/shelley-ma/shelley-ma-test/cddl-files/shelley-ma.cddl) or, if not present there, from the [CIP-0008 signing spec](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0008/CIP-0008.md).
This representation was chosen when possible as it is consistent across the Cardano ecosystem and widely used by other tools, such as [cardano-serialization-lib](https://github.com/Emurgo/cardano-serialization-lib), which has support to encode every type in the binary spec as CBOR bytes.

### Paginate

```
type Paginate = {|
  page: number,
  limit: number,
|};
```
Used to specify optional pagination for some API calls. Limits results to {limit} each page, and uses a 0-indexing {page} to refer to which of those pages of {limit} items each.


## Error Types

### APIError

```
APIErrorCode {
	InvalidRequest: -1,
	InternalError: -2,
	Refused: -3,
}
APIError {
	code: APIErrorCode,
	info: string
}
```

### DataSignError

```
DataSignErrorCode {
	ProofGeneration: 1,
	AddressNotPK: 2,
	UserDeclined: 3,
	InvalidFormat: 4,
}
type DataSignError = {
	code: DataSignErrorCode,
	info: String
}
```

* ProofGeneration - Wallet could not sign the data (e.g. does not have the secret key associated with the address)
* AddressNotPK - Address was not a P2PK address and thus had no SK associated with it.
* UserDeclined - User declined to sign the data
* InvalidFormat - If a wallet enforces data format requirements, this error signifies that the data did not conform to valid formats.

* InvalidRequest - Inputs do not conform to this spec or are otherwise invalid.
* InternalError - An error occurred during execution of this API call.
* Refused - The request was refused due to lack of access - e.g. wallet disconnects.

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

In order to initiate communication from webpages to a user's Cardano wallet, the wallet must provide the following javascript functions to the webpage. These would likely be done via code injection into the webpage. The API is split into two stages to maintain the user's privacy, as the user will have to consent to `cardano_request_read_access()` in order for the dApp to read any information pertaining to the user's wallet. 

### cardano_request_read_access(): Promise\<bool>

Errors: APIError

This is the entrypoint to start communication with the user's wallet. The wallet should request the user's permission to connect the web page to the user's wallet, and if permission has been granted, the full API (`cardano` object) must be exposed to the webpage. The wallet can choose to maintain a whitelist to not necessarily ask the user's permission every time access is requested, but this behavior is up to the wallet and should be transparent to web pages using this API. If a wallet is already connected this function should do nothing and simply return true.

### cardano_check_read_access(): Promise\<bool>

Errors: APIError

Returns true if the full API (`cardano` object) was injected and the dApp has access to the user's wallet, and false otherwise.




## Full API

Upon successful connection via `cardano_request_read_access()`, a javascript object named `cardano` is injected with the following methods. All read-only methods (all but the signing functionality) should not require any as the user has already consented to the dApp reading information about the wallet's state when they agreed to `cardano_request_read_access()`. The remaining methods `cardano.sign_tx()`, `cardano.sign_tx_input()`, `cardano.sign_data()` must request the user's consent in an informative way for each and every API call in order to maintain security.

The API chosen here is for the minimum API necessary for dApp <-> Wallet interactions without convenience functions that don't strictly need the wallet's state to work. The API here is for now also only designed for Shelley's Mary hardfork and thus has NFT support. When Alonzo is released with Plutus support this API will have to be extended.

### cardano.get_utxos(amount: cbor\<value> = undefined, paginate: Paginate = undefined): Promise\<cbor\<transaction_output> | undefined>

Errors: `APIError`, `PaginateError`

If `amount` is `undefined`, this shall return a list of all UTXOs (unspent transaction outputs) controlled by the wallet. If `amount` is not `undefined`, this request shall be limited to just the UTXOs that are required to reach the combined ADA/multiasset value target specified in `amount`, and if this cannot be attained, `undefined` shall be returned. The results can be further paginated by `paginate` if it is not `undefined`.

### cardano.get_balance(): Promise\<cbor\<value>>

Errors: `APIError`

Returns the total balance available of the wallet. This is the same as summing the results of `cardano.get_utxos()`, but it is both useful to dApps and likely already maintained by the implementing wallet in a more efficient manner so it has been included in the API as well.

### cardano.get_used_addresses(paginate: Paginate = undefined): Promise\<\<cbor<address>[]>

Errors: `APIError`

Returns a list of all used (included in some on-chain transaction) addresses controlled by the wallet. The results can be further paginated by `paginate` if it is not `undefined`.

### cardano.get_unused_addresses(): Promise\<\<cbor<address>[]>

Errors: `APIError`

Returns a list of unused addresses controlled by the wallet.

### cardano.get_change_address(): Promise\<\<cbor<address>>

Errors: `APIError`

Returns an address owned by the wallet that should be used as a change address to return leftover assets during transaction creation back to the connected wallet. This can be used as a generic receive address as well.

### cardano.sign_tx(tx: cbor\<transaction_body>, metadata: cbor\<auxiliary_data> = undefined): Promise\<cbor\<transaction>>

Errors: `APIError`, `TxSignError`

Requests that a user sign the supplied transaction body. The wallet should ask the user for permission, and if given, try to sign the supplied body and return a signed transaction. If the wallet could not sign the transaction, `TxSignError` shall be returned with the `ProofGeneration` code. Likewise if the user declined it shall return the `UserDeclined` code.

### cardano.sign_tx_input(tx: cbor\<transaction_body>, index: number): Promise\<cbor\<transaction_witness_set>>

Errors: `APIError`, `TxSignError`

Provides lower-level ability for signing that produces the witnesses for just a single input in a transaction. This exists in case dApps need to construct a transaction to satisfy certain properties and the user might only own some of the inputs. The wallet should ask user permission for signing similar to `cardano.sign_tx_input()` and errors are handled in the same way.

### cardano.sign_data(addr: cbor\<address>, sig_structure: cbor\<Sig_structure>): Promise\<Bytes>

Errors: `APIError`, `DataSignError`

This endpoint utilizes the [CIP-0008 signing spec](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0008/CIP-0008.md) for standardization/safety reasons. It allows the dApp to request the user to sign data conforming to said spec. The user's consent should be requested and the details of `sig_structure` shown to them in an informative way. The  Please refer to the CIP-0008 spec for details on how to construct the sig structure.

### cardano.submit_tx(tx: cbor\<transaction>): Promise\<hash32>

Errors: `APIError`, `TxSendError`

As wallets should already have this ability, we allow dApps to request that a transaction be sent through it. If the wallet accepts the transaction and tries to send it, it shall return the transaction id for the dApp to track. The wallet is free to return the `TxSendError` with code `Refused` if they do not wish to send it, or `Failure` if there was an error in sending it (e.g. preliminary checks failed on signatures).

# Implementations

TODO: link to Yoroi's implementation once available
