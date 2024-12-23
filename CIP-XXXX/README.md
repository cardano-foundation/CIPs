---
CIP: ?
Title: Full-data wallet connector
Status: Open
Category: Tools
Authors:
  - Giovanni Garufi <giovanni@mlabs.city>
Implementors: []
Discussions:
    - https://github.com/cardano-foundation/cips/pulls/?
Created: 2024-12-13
License: CC-BY-4.0
Version: 0.0.0
---

## Abstract


CIP-30 is the standard interface of communication between wallets and DApps. While this CIP has been instrumental in the development of dApps for Cardano, it also has some shortcomings that have been observed across several implementations.

We have identified and carried out two steps in the path to provide a better alternative to CIP-30:

- Defining a universal JSON encoding for Cardano domain types. CIP-30 requires CBOR encoding and decoding for data passed to and from the wallet, which is often an extra burden for the client. This problem is stated in [CPS-0011](https://github.com/cardano-foundation/CIPs/tree/master/CPS-0011) and a potential solution is given in [CIP-0116](link).

- Defining a universal query layer. CIP-30 is only concerned with obtaining data regarding the wallet, this forces dApps to integrate with other tools to query general blockchain data. This problem is stated in [CPS-0012](link) and a potential solution is given in [CIP-0139](link).


Finally, [CPS-0010](https://github.com/Ryun1/CIPs/blob/cps-wallet-connector/CPS-0010/README.md) defines the responsibilities for wallet connectors, and also introduces the vocabulary to distinguish between different kinds of wallets, based on the functionality they offer.

In this CIP we want to put these together, defining a wallet connector standard for a full-data wallet.

## Motivation: why is this CIP necessary?

CIP-30 is a universally accepted web-based wallet standard for Cardano. It provides a minimalistic interface that, in principle, can be used to build almost any kind of Cardano dApp. However, the way dApp<->wallet interaction is defined leads to suboptimal dApp architecture due to CIP-30 limits.

[CPS-0010](https://github.com/Ryun1/CIPs/blob/cps-wallet-connector/CPS-0010/README.md) discusses many limitations of CIP-30. In addition to the ones specified in the CPS, consider the following problems:

### Use of CBOR representations

CIP-30 standard uses CBOR encoding for all data passed from the wallet, e.g. addresses and UTxOs. Interpreting this data within the app requires CBOR decoding functionality that is tedious to implement manually, and so users resort to using cardano-serialization-lib or its close alternative, cardano-multiplatform-lib, which both require loading a WebAssembly blob of >1M in size.

For comparison, to start a new Web3 app on Ethereum there is no need to use a library for data serialization. It’s possible to interact with a provider object that is given by the wallet directly, although there are libraries to further simplify this. Using CBOR looks unnecessary for most dApps, given that JSON is a de-facto standard for web data serialization.

### Limited scope of available queries

Most dApps require interacting with scripts, which implies the need to query for available UTxOs locked at script addresses and other blockchain data. CIP-30 is intentionally limited in scope to management of UTxOs "owned" by the wallet itself.

Some other useful queries, like getting delegation and reward info, stake pool info, transaction metadata or contents, and epoch data, are also outside of scope.

As a result, dApp developers are forced to implement their own query layers on the backend side - which leads to one more problem - inconsistency between states of two query layers:

### Inconsistency of Query Layers

On Cardano, every running node has its own opinion on the set of currently unspent transaction outputs. Only eventual consistency is guaranteed.

Any dApp that interacts with a CIP-30 wallet has to deal with the inconsistency between the local cardano-node-based query layer and the light wallet query layer, especially when dApp workflow involves sending multiple transactions with the wallet in quick succession.

Thus, the goal of the developers is to ensure that the set of UTxOs available to the wallet and the set of UTxOs the backend cardano-node knows about are synchronized enough to not cause errors when a wallet or backend operations are performed. To give a few examples of potential issues, consider the following scenarios:

A dApp tries to balance a transaction with UTxOs from the wallet that is not yet available in dApp backend's cardano node, causing an error response during execution units evaluation
A transaction is passed for signing, but the wallet does not yet know about the UTxOs it spends, and thus refuses to sign it
A transaction is sent to the network via the dApp backend (bypassing CIP-30 submit method) and is confirmed there, but the wallet still does not know about its consumed inputs, and thus returns outdated data.


## Specification

The goal of this CIP is to provide a better alternative to CIP-30 which supports full data wallet. Specifically we make the following contributions:

- A clear separation between the connection mechanism and the actual API offered by the wallet connector
- Using JSON for Cardano domain types instead of CBOR
- Add a query layer API to enable a full data wallet
- Define this in a transport agnostic way

In it's current state, CIP-30 defines it API through a specific transport layer, namely an injected Javascript object.
In this CIP we want to be able to define an API without committing to a specific transport layer. Implementors of this API can choose to support this API through several transports such as: HTTP, an injected Javascript object, JSON-RPC etc.
Furthermore, we want to use JSON-schema to clearly define the types that each method, or operation, expects to receive or returns.
To keep the specification abstract we will use the word "operation" to describe the actions supported by the API, these would map to "endpoints" for an HTTP implementation of the API, or to "methods" for an implementation based on an injected Javascript object.


We will use the following schema to define operations:

```
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

We will reference several JSON-schemas throughout the document, these are:

- [cip-0116](link) which provides a JSON encoding of Cardano ledger types. Note that this CIP defines a schema for each ledger era. When referring to a type from this schema we refer to an `anyOf` of all the schemas in which that type is defined. [Maybe we should only reference the latest era and update the CIP in the future? our current definition requires to be perpetually backward compatible with old ledger types]
- [cip-0139](link) which provides definitions for types used in the query layer
- [appendix](#appendix) in which we define schemas for types required by the connection API and the error types

We will use an identifier in the anchor to refer to the schema where each type is defined. For example, if we want to reference the `Transaction` type, as defined in CIP-0116 we will use the following schema reference `{ "$ref": "#/cip-0116/Transaction" }`.

If an operation does not require any arguments as part of it's request, or does not return a meaningful response, we will represent this as an `{}` on the respective operation field. The arguments to an operation will always be represented as an object. If a field is not marked as `required`, then that argument is to be considered optional.

For each operation we will provide some details on how the implementation should behave. Note tht some of these are taken verbatim from CIP-30.

### Connection API

We start by defining the connection API. The role of this API is to provide generic information about the wallet and to allow the user to opt into the functionalities that they want the wallet to provide.

##### Enable

```
{
  "operation": "enable",
  "request": { "$ref": "#/appendix/Extensions" },
  "response": {},
  "errors": [
    { "$ref": "#/appendix/APIError" }
  ]
}
```

This is the entrypoint to start communication with the user's wallet. The wallet should request the user's permission to connect the web page to the user's wallet, and if permission has been granted, the APIs will be made available for the DApp to use. The wallet can choose to maintain a whitelist to not necessarily ask the user's permission every time access is requested, but this behavior is up to the wallet and should be transparent to web pages using this API. If a wallet is already connected this function should not request access a second time.

DApps can request a list of they expect as a list of CIP numbers capturing those extensions. This is used as an extensibility mechanism to document what functionalities can be provided by the wallet interface. We will see later in this document examples of what such extensions might be and which functionalities they will enable. New functionalities can be introduced via additional CIPs and may be all or partially supported by wallets.

DApps are expected to use this endpoint to perform an initial handshake and ensure that the wallet supports all their required functionalities. Note that it's possible for two extensions to be mutually incompatible (because they provide two conflicting features). While we may try to avoid this as much as possible while designing CIPs, it is also the responsibility of wallet providers to assess whether they can support a given combination of extensions, or not. Wallets should throw an error if either they do not support the required extension, or they deem the combination of extensions requested by the DApp to be incompatible.


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

A list of extensions supported by the wallet. Extensions may be requested by dApps on initialization. Some extensions may be mutually conflicting and this list does not thereby reflect what extensions will be enabled by the wallet. Yet it informs on what extensions are known and can be requested by dApps if needed.


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

### Extension APIs

The following section will define the APIs offered by extensions that can be requested through the `enable` operation. With a slight abuse of notation, we will define the operations defined in CIP-30, in the [Full API](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0030#full-api) as belonging to the `cip-30` extension.
We will also define the `cip-139` extension which enables wallet to use the Universal Query Layer API.

A wallet which enables both the `cip-30` and `cip-139` extension would then be considered a full-data wallet.

Future CIPs can add more extensions to the supported list.

#### CIP-30

This section defines the API for the `Full API` part of CIP-30. Enabling only this extension would give you an own-data wallet, which is essentially equivalent to what CIP-30 gives us today.

Operations that sign data MUST require additional user consent before being performed. Additional details will be specified in the section for each operation.
Note that this API differs slightly from CIP-30 Full API in that it drops an endpoint which is not required (`getExtensions`) and removes the option for pagination.

The removal of pagination follows the same [reasons](https://github.com/klntsky/CIPs/blob/klntsky/query-layer-cip/CIP-XXXX/README.md#pagination) pointed out in CIP-0139. In summary: pagination, while desirable, introduces some complications with the consistency of the returned results. We decide to drop it to keep the implementation as simple as possible, but welcome future CIPs to address this.

##### GetNetworkId

```
{
  "operation": "getNetworkId",
  "request": {},
  "response": { "type": "number" },
  "errors": [
    { "$ref": "#/appendix/APIError" }
  ]
}
```

Returns the network id of the currently connected account. 0 is testnet and 1 is mainnet but other networks can possibly be returned by wallets. Those other network ID values are not governed by this document. This result will stay the same unless the connected account has changed.

##### GetUtxos

```
{
  "operation": "getUtxos",
  "request": {
    "type": "object",
    "properties": {
      "amount": { "$ref": "#/cip-116/Value" }
    }
  },
  "response": { "$ref": "#/cip-116/TransactionUnspentOutput" },
  "errors": [
    { "$ref": "#/appendix/APIError" }
  ]
}
```

If amount is not supplied, this shall return a list of all UTXOs controlled by the wallet. If amount is present, this request shall be limited to just the UTXOs that are required to reach the combined ADA/multiasset value target specified in amount, and if this cannot be attained, an `APIError` with error code `NotSatisfiable` (and optionally an info string) must be returned. 

##### GetCollateral

```
{
  "operation": "getCollateral",
  "request": {
    "type": "object",
    "properties": {
      "amount": { "type": "number" }
    },
    "required": ["amount"]
  },
  "response": { "$ref": "#/cip-116/TransactionUnspentOutput" },
  "errors": [
    { "$ref": "#/appendix/APIError" }
  ]
}
```

The operation takes an amount parameter. (NOTE: some wallets may be ignoring the amount parameter, in which case it might be possible to call the function without it, but this behavior is not recommended!). Reasons why the amount parameter is required:

- Dapps must be motivated to understand what they are doing with the collateral, in case they decide to handle it manually.

- Depending on the specific wallet implementation, requesting more collateral than necessarily might worsen the user experience with that dapp, requiring the wallet to make explicit wallet reorganisation when it is not necessary and can be avoided.

- If dapps don't understand how much collateral they actually need to make their transactions work - they are placing more user funds than necessary in risk.

So requiring the amount parameter would be a by-spec behavior for a wallet. Not requiring it is possible, but not specified, so dapps should not rely on that and the behavior is not recommended.

This shall return a list of one or more UTXOs controlled by the wallet that are required to reach AT LEAST the combined ADA value target specified in amount AND the best suitable to be used as collateral inputs for transactions with plutus script inputs (pure ADA-only utxos). If this cannot be attained, an APIError with code `NotSatisfiable` and an explanation of the blocking problem shall be returned. NOTE: wallets are free to return utxos that add up to a greater total ADA value than requested in the amount parameter, but wallets must never return any result where utxos would sum up to a smaller total ADA value, instead in a case like that an error must be returned.

The main point is to allow the wallet to encapsulate all the logic required to handle, maintain, and create (possibly on-demand) the UTXOs suitable for collateral inputs. For example, whenever attempting to create a plutus-input transaction the dapp might encounter a case when the set of all user UTXOs don't have any pure entries at all, which are required for the collateral, in which case the dapp itself is forced to try and handle the creation of the suitable entries by itself. If a wallet implements this function it allows the dapp to not care whether the suitable utxos exist among all utxos, or whether they have been stored in a separate address chain (see #104), or whether they have to be created at the moment on-demand - the wallet guarantees that the dapp will receive enough utxos to cover the requested amount, or get an error in case it is technically impossible to get collateral in the wallet (e.g. user does not have enough ADA at all).

[The spec says that amount should agreed to be max 5 ada, is this enforced? The formulation in the CIP does not seem to be too precise]


##### GetBalance

```
{
  "operation": "getBalance",
  "request": {},
  "response": { "$ref": "#/cip-116/Value" },
  "errors": [
    { "$ref": "#/appendix/APIError" }
  ]
}
```

Returns the total balance available of the wallet. This is the same as summing the results of api.getUtxos(), but it is both useful to dApps and likely already maintained by the implementing wallet in a more efficient manner so it has been included in the API as well.


##### GetUsedAddresses

```
{
  "operation": "getUsedAddresses",
  "request": {},
  "response": {
    "type": "array",
    "items: { "$ref": "#/cip-116/Address" }
  },
  "errors": [
    { "$ref": "#/appendix/APIError" }
  ]
}
```

Returns a list of all used (included in some on-chain transaction) addresses controlled by the wallet.

##### GetUnusedAddresses

```
{
  "operation": "getUnusedAddresses",
  "request": {},
  "response": {
    "type": "array",
    "items: { "$ref": "#/cip-116/Address" }
  },
  "errors": [
    { "$ref": "#/appendix/APIError" }
  ]
}
```

Returns a list of unused addresses controlled by the wallet.

##### GetChangeAddress

```
{
  "operation": "getChangeAddress",
  "request": {},
  "response": { "$ref": "#/cip-116/Address" },
  "errors": [
    { "$ref": "#/appendix/APIError" }
  ]
}
```

Returns an address owned by the wallet that should be used as a change address to return leftover assets during transaction creation back to the connected wallet. This can be used as a generic receive address as well.

##### GetRewardAddresses

```
{
  "operation": "getRewardAddresses",
  "request": {},
  "response": {
    "type": "array",
    "items: { "$ref": "#/cip-116/RewardAddress" }
  },
  "errors": [
    { "$ref": "#/appendix/APIError" }
  ]
}
```

Returns the reward addresses owned by the wallet. This can return multiple addresses e.g. CIP-0018.

##### SignTx

```
{
  "operation": "signTx",
  "request": {
    "type": "object",
    "properties": {
      "tx": { "$ref": "#/cip-116/Transaction" },
      "partialSign": { "type": "boolean" }
    },
    "required": ["tx"]
  },
  "response": { "$ref": "#/cip-116/TransactionWitnessSet" },
  "errors": [
    { "$ref": "#/appendix/APIError" },
    { "$ref": "#/appendix/TxSignError" }
  ]
}
```

Requests that a user sign the unsigned portions of the supplied transaction. The wallet MUST ask the user for permission, and if given, try to sign the supplied transaction. If partialSign is true, the wallet only tries to sign what it can. If partialSign is false, or not supplied, and the wallet could not sign the entire transaction, `TxSignError` shall be returned with a `ProofGeneration` error code. Likewise if the user declined in either case it shall return the same error with a `UserDeclined` error code.

Only the portions of the witness set that were signed as a result of this call are returned to encourage dApps to verify the contents returned by this endpoint while building the final transaction.


##### SignData

```
{
  "operation": "signData",
  "request": {
    "type": "object",
    "properties": {
      "addr": { "$ref": #/cip-116/Address },
      "payload": { "$ref": "#/cip-116/ByteString" }
    },
    "required": ["addr", "payload"]
  },
  "response": { "$ref": "#/appendix/DataSignature" },
  "errors": [
    { "$ref": "#/appendix/APIError" },
    { "$ref": "#/appendix/DataSignError" }
  ]
}
```

[Is bytestring the correct type here?]

This endpoint utilizes the [CIP-0008 signing spec](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0008/README.md) for standardization/safety reasons. It allows the dApp to request the user to sign a payload conforming to said spec. The user's consent MUST be requested and the message to sign shown to the user. The payment key from `addr` will be used for base, enterprise and pointer addresses to determine the EdDSA25519 key used. The staking key will be used for reward addresses. This key will be used to sign the `COSE_Sign1`'s `Sig_structure` with the following headers set:

- `alg` (1) - must be set to EdDSA (-8)
- `kid` (4) - Optional, if present must be set to the same value as in the COSE_key specified below. It is recommended to be set to the same value as in the "address" header.
- `address` - must be set to the raw binary bytes of the address as per the binary spec

The payload is not hashed and no `external_aad` is used.

If the payment key for `addr` is not a P2Pk address then `DataSignError` will be returned with error code `AddressNotPK`. `ProofGeneration` error code shall be returned if the wallet cannot generate a signature (i.e. the wallet does not own the requested payment private key), and `UserDeclined` will be returned if the user refuses the request. The return shall be a `DataSignature` with `signature` set to the hex-encoded bytes of the `COSE_Sign1` object specified above and `key` shall be the hex-encoded bytes of a `COSE_Key` structure with the following headers set:

- `kty` (1) - must be set to `OKP` (1)
- `kid` (2) - Optional, if present must be set to the same value as in the `COSE_Sign1` specified above.
- `alg` (3) - must be set to `EdDSA` (-8)
- `crv` (-1) - must be set to `Ed25519` (6)
- `x` (-2) - must be set to the public key bytes of the key used to sign the `Sig_structure`

[What are these numbers appearing next to params? Copied them from cip-30 but not sure]

##### SubmitTx

```
{
  "operation": "submitTx",
  "request": {
    "type": "object",
    "properties": {
      "tx": { "$ref": "#/cip-116/Transaction" }
    },
    "required": ["tx"]
  },
  "response": { "$ref": "#/cip-116/TransactionHash" },
  "errors": [
    { "$ref": "#/appendix/APIError" },
    { "$ref": "#/appendix/TxSendError" }
  ]
}
```

As wallets should already have this ability, we allow dApps to request that a transaction be sent through it. If the wallet accepts the transaction and tries to send it, it shall return the transaction id for the dApp to track. The wallet is free to return the `TxSendError` with error code `Refused` if they do not wish to send it, or `Failure` if there was an error in sending it (e.g. preliminary checks failed on signatures).


#### CIP-139




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
      "type": "array"
      "items": {
          {
            "type": "object",
            "title": "Extension",
            "properties": {
              "cip": {
                "type": "number"
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

An extension is an object with a single field "cip" that describes a CIP number extending the API. For example:

```
{ "cip": 30 }
```


##### DataSignature

```
{
  "type": "object",
  "title": "DataSignature",
  "properties": {
    "signature": {
      "title": "Ed25519Signature",
      "type": "string",
      "format": "hex",
      "pattern": "^([0-9a-f][0-9a-f]){64}$"
    },
    "key": {
      "title": "Ed25519PublicKey",
      "type": "string",
      "format": "hex",
      "pattern": "^([0-9a-f][0-9a-f]){32}$"
    }
  },
  "required": ["signature", "key"],
}
```

An object representing some data that has been signed. It contains 2 fields: `signature` which contains the signed data, and `key` which contains the derived Ed25519 PubKey used to sign the data.

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

[Why are these negative? Seems arbitrary, is it too breaking to change them?]

- `InvalidRequest`: (-1) Inputs do not conform to this spec or are otherwise invalid.
- `InternalError`: (-2) An error occurred during execution of this API call.
- `Refused`: (-3) The request was refused due to lack of access - e.g. wallet disconnects.
- `AccountChange`: (-4) The account has changed. The dApp should call wallet.enable() to reestablish connection to the new account. The wallet should not ask for confirmation as the user was the one who initiated the account change in the first place.
- `NotSatisfiable`: (-5) The request is structurally correct, but the wallet can not satisfy it for some reason.

##### DataSignError

```
{
  "type": "object",
  "title": "DataSignError",
  "properties": {
    "code": {
      "type": "number",
      "title": "DataSignErrorCode"
      "enum": [1, 2, 3]
    },
    "info": {
      "type": "string"
    }
  },
  "required": ["code"],
}
```

- `ProofGeneration`: (1) Wallet could not sign the data (e.g. does not have the secret key associated with the address).
- `AddressNotPK`: (2) Address was not a P2PK address and thus had no SK associated with it.
- `UserDeclined`: (3) User declined to sign the data.

##### TxSendError

```
{
  "type": "object",
  "title": "TxSendError",
  "properties": {
    "code": {
      "type": "number",
      "title": "TxSendErrorCode"
      "enum": [1, 2]
    },
    "info": {
      "type": "string"
    }
  },
  "required": ["code"],
}
```

- `Refused`: (1) Wallet refuses to send the tx (could be rate limiting).
- `Failure`: (2) Wallet could not send the tx.

##### TxSignError

```
{
  "type": "object",
  "title": "TxSignError",
  "properties": {
    "code": {
      "type": "number",
      "title": "TxSignErrorCode"
      "enum": [1, 2]
    },
    "info": {
      "type": "string"
    }
  },
  "required": ["code"],
}
```

- `ProofGeneration`: (1) User has accepted the transaction sign, but the wallet was unable to sign the transaction (e.g. not having some of the private keys).
- `UserDeclined`: (2) User declined to sign the transaction.

## Rationale: how does this CIP achieve its goals?

???

## Path to Active

- ???

## Copyright


