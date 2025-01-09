---
CIP: 144
Title: Full-data wallet connector
Category: Tools
Status: Proposed
Authors:
  - Giovanni Garufi <giovanni@mlabs.city>
Implementors: []
Discussions:
    - https://github.com/cardano-foundation/cips/pulls/957
Created: 2024-12-13
License: CC-BY-4.0
---

## Abstract


CIP-30 is the standard interface of communication between wallets and dApps. While this CIP has been instrumental in the development of dApps for Cardano, it also has some shortcomings that have been observed across several implementations.

We have identified and carried out two steps in the path to provide a better alternative to CIP-30:

- Defining a universal JSON encoding for Cardano domain types. CIP-30 requires CBOR encoding and decoding for data passed to and from the wallet, which is often an extra burden for the client. This problem is stated in [CPS-0011](https://github.com/cardano-foundation/CIPs/tree/master/CPS-0011) and a potential solution is given in [CIP-0116](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0116).

- Defining a universal query layer. CIP-30 is only concerned with obtaining data regarding the wallet, this forces dApps to integrate with other tools to query general blockchain data. This problem is stated in [CPS-0012](https://github.com/cardano-foundation/CIPs/tree/master/CPS-0012) and a potential solution is given in [CIP-0139](https://github.com/cardano-foundation/CIPs/pull/869).


Finally, [CPS-0010](https://github.com/cardano-foundation/CIPs/blob/master/CPS-0010/README.md) defines the responsibilities for wallet connectors, and also introduces the vocabulary to distinguish between different kinds of wallets, based on the functionality they offer.

In this CIP we want to put these together, defining a wallet connector standard for a full-data wallet.

## Motivation: why is this CIP necessary?

CIP-30 is a universally accepted web-based wallet standard for Cardano. It provides a minimalistic interface that, in principle, can be used to build almost any kind of Cardano dApp. However, the way dApp<->wallet interaction is defined leads to suboptimal dApp architecture due to CIP-30 limits.

Consider the following problems:

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

### CPS-10

[CPS-0010](https://github.com/Ryun1/CIPs/blob/cps-wallet-connector/CPS-0010/README.md) discusses several other limitations of CIP-30. In this CIP we try to solve the issues pointed out in that CPS. There are still some areas to improve on: things like the event listener API are intentionally left out of this CIP to prevent bloat of scope. We welcome future CIPs, or updates to this CIP to refine any limitation that is not tackled in this document.

## Specification

The goal of this CIP is to provide a better alternative to CIP-30 which supports full data wallet. Specifically we make the following contributions:

- A clear separation between the connection mechanism and the different APIs offered by the wallet.
- Using JSON for Cardano domain types instead of CBOR
- Add a query layer API to enable a full data wallet
- Add versioning support to the extension API
- Define this in a transport agnostic way

In its current state, CIP-30 defines it API through a specific transport layer, namely an injected Javascript object.
In this CIP we want to be able to define an API without committing to a specific transport layer. Implementors of this API can choose to support this API through several transports such as: HTTP, an injected Javascript object, JSON-RPC etc.
Furthermore, we want to use JSON-schema to clearly define the types that each method, or operation, expects to receive or returns.
To keep the specification abstract we will use the word "operation" to describe the actions supported by the API: these would map to "endpoints" for an HTTP implementation of the API, or to "methods" for an implementation based on an injected Javascript object.


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
We do not add an explicit scope to operation names, we do however encourage transport-specific implementations of this API to pick the scoping structure that makes more sense to them.

We will reference several JSON schemas throughout the document, these are:

- [cip-116](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0116) which provides a JSON encoding of Cardano ledger types. Note that this CIP defines a schema for each ledger era. When referring to a type from this schema we refer to an `anyOf` of all the schemas in which that type is defined. *[Maybe we should only reference the latest era and update the CIP in the future? our current definition requires to be perpetually backward compatible with old ledger types]*
- [cip-139](https://github.com/cardano-foundation/CIPs/pull/869) which provides definitions for types used in the query layer
- [appendix](#appendix) in which we define schemas for types required by the connection API and the error types

We will use an identifier in the anchor to refer to the schema where each type is defined. For example, if we want to reference the `Transaction` type, as defined in CIP-116 we will use the following schema reference `{ "$ref": "#/cip-116/Transaction" }`.

If an operation does not require any arguments as part of it's request, or does not return a meaningful response, we will represent this as an `{}` on the respective operation field. The arguments to an operation will always be represented as an object. If a field is not marked as `required`, then that argument is to be considered optional.

For each operation we will provide some details on how the implementation should behave. Note that some of these are taken verbatim from CIP-30.

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

Returns the API version for the wallet connection API. This must correspond to the value of `Version-Connection-API` specified in this document, appropriately transformed into a `SemVer` object.


### Extension APIs

The following section will define the APIs offered by extensions that can be requested through the `enable` operation. With a slight abuse of notation, we will define the operations defined in CIP-30, in the [Full API](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0030#full-api) as belonging to the `cip-30` extension.
We will also define the `cip-139` extension which enables wallet to use the Universal Query Layer API.

A wallet which enables both the `cip-30` and `cip-139` extension would then be considered a full-data wallet.

`Note`: Several of the endpoints offered by the extension APIs, are there to query some on-chain resource. Unless explicitly specified, wallets are always free to omit or add some of the resources returned.
While it may sound confusing to allow this behavior, the intention is for wallets to be able to track and reconcile some local information, even if it is not necessarily available on-chain.
An example where this caveat becomes quite useful, is with *transaction chaining*. When a wallet supports that they may allow the user to submit several transactions which depend on each other,
without having to wait for each one to be approved by other nodes. When a wallet does that, it will mark some UTxOs internally as *spent*, and will avoid returning them in a `getUtxos` query, for example.
Wallets are in charge of keeping their internal state in sync with the results of the various queries that different extensions support.

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
  "response": {
    "type": "array",
    "items": {
      "$ref": "#/cip-116/TransactionUnspentOutput"
    }
  },
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
  "response": {
    "type": "array",
    "items": {
      "$ref": "#/cip-116/TransactionUnspentOutput"
    }
  },
  "errors": [
    { "$ref": "#/appendix/APIError" }
  ]
}
```

The operation takes an amount parameter. (NOTE: some wallets may be ignoring the amount parameter, in which case it might be possible to call the function without it, but this behavior is not recommended!). Reasons why the amount parameter is required:

- DApps must be motivated to understand what they are doing with the collateral, in case they decide to handle it manually.

- Depending on the specific wallet implementation, requesting more collateral than necessarily might worsen the user experience with that dapp, requiring the wallet to make explicit wallet reorganisation when it is not necessary and can be avoided.

- If dApps don't understand how much collateral they actually need to make their transactions work - they are placing more user funds than necessary in risk.

So requiring the amount parameter would be a by-spec behavior for a wallet. Not requiring it is possible, but not specified, so dApps should not rely on that and the behavior is not recommended.

This shall return a list of one or more UTXOs controlled by the wallet that are required to reach AT LEAST the combined ADA value target specified in amount AND the best suitable to be used as collateral inputs for transactions with plutus script inputs (pure ADA-only utxos). If this cannot be attained, an `APIError` with code `NotSatisfiable` and an explanation of the blocking problem shall be returned. NOTE: wallets are free to return utxos that add up to a greater total ADA value than requested in the amount parameter, but wallets must never return any result where utxos would sum up to a smaller total ADA value, instead in a case like that an error must be returned.

The main point is to allow the wallet to encapsulate all the logic required to handle, maintain, and create (possibly on-demand) the UTXOs suitable for collateral inputs. For example, whenever attempting to create a plutus-input transaction the dapp might encounter a case when the set of all user UTXOs don't have any pure entries at all, which are required for the collateral, in which case the dapp itself is forced to try and handle the creation of the suitable entries by itself. If a wallet implements this function it allows the dapp to not care whether the suitable utxos exist among all utxos, or whether they have been stored in a separate address chain (see #104), or whether they have to be created at the moment on-demand - the wallet guarantees that the dapp will receive enough utxos to cover the requested amount, or get an error in case it is technically impossible to get collateral in the wallet (e.g. user does not have enough ADA at all).


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
    "items": { "$ref": "#/cip-116/Address" }
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
    "items": { "$ref": "#/cip-116/Address" }
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
    "items": { "$ref": "#/cip-116/RewardAddress" }
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
      "addr": { "$ref": "#/cip-116/Address" },
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

This section defines the API for the `Query Layer API` as defined in CIP-139. Enabling this extension, alongside the `cip-30` extension, would give you a full-data wallet.

##### Utxos

###### Asset

```
{
  "operation": "getUtxosByAsset",
  "request": {
    "type": "object",
    "properties": {
      "asset_name": {
        "$ref": "#/cip-116/AssetName"
      },
      "minting_policy_hash": {
        "$ref": "#/cip-116/ScriptHash"
      }
    },
    "required": [
      "asset_name",
      "minting_policy_hash"
    ]
  },
  "response": {
    "type": "object",
    "properties": {
      "utxos": {
        "type": "array",
        "items": {
          "$ref": "#/cip-116/TransactionUnspentOutput"
        }
      }
    },
    "required": [
      "utxos"
    ]
  },
  "errors": [
    {
      "$ref": "#/appendix/APIError"
    }
  ]
}
```

Get all UTxOs that contain some of the specified asset.

###### Transaction Hash

```
{
  "operation": "getUtxosByTransactionHash",
  "request": {
    "$ref": "#/cip-139/TransactionHash"
  },
  "response": {
    "type": "object",
    "properties": {
      "utxos": {
        "type": "array",
        "items": {
          "$ref": "#/cip-116/TransactionUnspentOutput"
        }
      }
    },
    "required": [
      "utxos"
    ]
  },
  "errors": [
    {
      "$ref": "#/appendix/APIError"
    }
  ]
}
```

Get all UTxOs produced by the transaction.

###### Address

```
{
  "operation": "getUtxosByAddress",
  "request": {
    "$ref": "#/cip-116/Address"
  },
  "response": {
    "type": "object",
    "properties": {
      "utxos": {
        "type": "array",
        "items": {
          "$ref": "#/cip-116/TransactionUnspentOutput"
        }
      }
    },
    "required": [
      "utxos"
    ]
  },
  "errors": [
    {
      "$ref": "#/appendix/APIError"
    }
  ]
}
```

Get all UTxOs present at the address.

###### Payment Credential

```
{
  "operation": "getUtxosByPaymentCredential",
  "request": {
    "$ref": "#/cip-116/Credential"
  },
  "response": {
    "type": "object",
    "properties": {
      "utxos": {
        "type": "array",
        "items": {
          "$ref": "#/cip-116/TransactionUnspentOutput"
        }
      }
    },
    "required": [
      "utxos"
    ]
  },
  "errors": [
    {
      "$ref": "#/appendix/APIError"
    }
  ]
}
```

Get all UTxOs present at the addresses which use the payment credential.

###### Stake Credential

```
{
  "operation": "getUtxosByStakeCredential",
  "request": {
    "$ref": "#/cip-116/RewardAddress"
  },
  "response": {
    "type": "object",
    "properties": {
      "utxos": {
        "type": "array",
        "items": {
          "$ref": "#/cip-116/TransactionUnspentOutput"
        }
      }
    },
    "required": [
      "utxos"
    ]
  },
  "errors": [
    {
      "$ref": "#/appendix/APIError"
    }
  ]
}
```

Get all UTxOs present at the addresses which use the stake credential.

##### Block

###### Number

```
{
  "operation": "getBlockByNumber",
  "request": {
    "$ref": "#/cip-139/UInt64"
  },
  "response": {
    "$ref": "#/cip-116/Block"
  },
  "errors": [
    {
      "$ref": "#/appendix/APIError"
    }
  ]
}
```

Get the block with the supplied block number.

###### Hash

```
{
  "operation": "getBlockByHash",
  "request": {
    "$ref": "#/cip-116/BlockHash"
  },
  "response": {
    "$ref": "#/cip-116/Block"
  },
  "errors": [
    {
      "$ref": "#/appendix/APIError"
    }
  ]
}
```

Get the block with the supplied block hash.

##### Transaction

###### Hash

```
{
  "operation": "getTransactionByHash",
  "request": {
    "$ref": "#/cip-139/TransactionHash"
  },
  "response": {
    "$ref": "#/cip-116/Transaction"
  },
  "errors": [
    {
      "$ref": "#/appendix/APIError"
    }
  ]
}
```

Get the transaction with the supplied transaction hash.

###### Block Number

```
{
  "operation": "getTransactionByBlockNumber",
  "request": {
    "$ref": "#/cip-139/UInt64"
  },
  "response": {
    "type": "object",
    "properties": {
      "transactions": {
        "type": "array",
        "items": {
          "$ref": "#/cip-116/Transaction"
        }
      }
    },
    "required": [
      "transactions"
    ]
  },
  "errors": [
    {
      "$ref": "#/appendix/APIError"
    }
  ]
}
```

Get all transactions contained in the block with the supplied block number [].

###### Block Hash

```
{
  "operation": "getTransactionByBlockHash",
  "request": {
    "$ref": "#/cip-116/BlockHash"
  },
  "response": {
    "type": "object",
    "properties": {
      "transactions": {
        "type": "array",
        "items": {
          "$ref": "#/cip-116/Transaction"
        }
      }
    },
    "required": [
      "transactions"
    ]
  },
  "errors": [
    {
      "$ref": "#/appendix/APIError"
    }
  ]
}
```

Get all transactions contained in the block with the supplied block hash.

##### Datum

###### Hash

```
{
  "operation": "getDatumByHash",
  "request": {
    "$ref": "#/cip-116/DataHash"
  },
  "response": {
    "$ref": "#/cip-116/PlutusData"
  },
  "errors": [
    {
      "$ref": "#/appendix/APIError"
    }
  ]
}
```

Get the datum that hashes to the supplied data hash.

##### Plutus Script

###### Hash

```
{
  "operation": "getPlutusScriptByHash",
  "request": {
    "$ref": "#/cip-116/ScriptHash"
  },
  "response": {
    "$ref": "#/cip-116/PlutusScript"
  },
  "errors": [
    {
      "$ref": "#/appendix/APIError"
    }
  ]
}
```

Get the plutus script that hashes to the supplied script hash.

##### Native Script

###### Hash

```
{
  "operation": "getNativeScriptByHash",
  "request": {
    "$ref": "#/cip-116/ScriptHash"
  },
  "response": {
    "$ref": "#/cip-116/NativeScript"
  },
  "errors": [
    {
      "$ref": "#/appendix/APIError"
    }
  ]
}
```

Get the native script that hashes to the supplied script hash.

##### Metadata

###### Transaction Hash

```
{
  "operation": "getMetadataByTransactionHash",
  "request": {
    "$ref": "#/cip-139/TransactionHash"
  },
  "response": {
    "$ref": "#/cip-116/TransactionMetadatum"
  },
  "errors": [
    {
      "$ref": "#/appendix/APIError"
    }
  ]
}
```

Get the metadata present on the transaction with the supplied transaction hash.

##### Protocol Parameters

###### Latest

```
{
  "operation": "getProtocolParametersByLatest",
  "request": {},
  "response": {
    "$ref": "#/cip-139/ProtocolParams"
  },
  "errors": [
    {
      "$ref": "#/appendix/APIError"
    }
  ]
}
```

Get the latest protocol parameters.

###### Epoch

```
{
  "operation": "getProtocolParametersByEpoch",
  "request": {
    "$ref": "#/cip-139/UInt32"
  },
  "response": {
    "$ref": "#/cip-139/ProtocolParams"
  },
  "errors": [
    {
      "$ref": "#/appendix/APIError"
    }
  ]
}
```

Get the protocol parameters at the supplied epoch number.

##### Votes

###### Cc Id

```
{
  "operation": "getVotesByCcId",
  "request": {
    "$ref": "#/cip-139/CCHotId"
  },
  "response": {
    "type": "object",
    "properties": {
      "votes": {
        "type": "array",
        "items": {
          "$ref": "#/cip-139/VoteInfo"
        }
      }
    },
    "required": [
      "votes"
    ]
  },
  "errors": [
    {
      "$ref": "#/appendix/APIError"
    }
  ]
}
```

Votes cast by the supplied cc credential.

###### Spo Id

```
{
  "operation": "getVotesBySpoId",
  "request": {
    "$ref": "#/cip-139/PoolPubKeyHash"
  },
  "response": {
    "type": "object",
    "properties": {
      "votes": {
        "type": "array",
        "items": {
          "$ref": "#/cip-139/VoteInfo"
        }
      }
    },
    "required": [
      "votes"
    ]
  },
  "errors": [
    {
      "$ref": "#/appendix/APIError"
    }
  ]
}
```

Votes cast by the supplied stake pool operator.

###### Drep Id

```
{
  "operation": "getVotesByDrepId",
  "request": {
    "$ref": "#/cip-139/DRepId"
  },
  "response": {
    "type": "object",
    "properties": {
      "votes": {
        "type": "array",
        "items": {
          "$ref": "#/cip-139/VoteInfo"
        }
      }
    },
    "required": [
      "votes"
    ]
  },
  "errors": [
    {
      "$ref": "#/appendix/APIError"
    }
  ]
}
```

Votes cast by the supplied DRep.

###### Proposal Id

```
{
  "operation": "getVotesByProposalId",
  "request": {
    "$ref": "#/cip-139/ProposalId"
  },
  "response": {
    "type": "object",
    "properties": {
      "votes": {
        "type": "array",
        "items": {
          "$ref": "#/cip-139/VoteInfo"
        }
      }
    },
    "required": [
      "votes"
    ]
  },
  "errors": [
    {
      "$ref": "#/appendix/APIError"
    }
  ]
}
```

Votes cast on the supplied proposal.

##### Drep

###### All

```
{
  "operation": "getAllDreps",
  "request": {},
  "response": {
    "type": "object",
    "properties": {
      "dreps": {
        "type": "array",
        "items": {
          "$ref": "#/cip-139/DRepInfo"
        }
      }
    },
    "required": [
      "dreps"
    ]
  },
  "errors": [
    {
      "$ref": "#/appendix/APIError"
    }
  ]
}
```

Get all the known DReps.

###### Id

```
{
  "operation": "getDrepById",
  "request": {
    "$ref": "#/cip-139/DRepId"
  },
  "response": {
    "$ref": "#/cip-139/DRepInfo"
  },
  "errors": [
    {
      "$ref": "#/appendix/APIError"
    }
  ]
}
```

Get a specific DRep by id.

###### Stake Credential

```
{
  "operation": "getDrepByStakeCredential",
  "request": {
    "$ref": "#/cip-116/RewardAddress"
  },
  "response": {
    "$ref": "#/cip-139/DRepInfo"
  },
  "errors": [
    {
      "$ref": "#/appendix/APIError"
    }
  ]
}
```

Get the DRep that the stake credential has delegated to.

##### Committee Member

###### All

```
{
  "operation": "getAllCommitteeMembers",
  "request": {},
  "response": {
    "type": "object",
    "properties": {
      "cc_members": {
        "type": "array",
        "items": {
          "$ref": "#/cip-139/CCMember"
        }
      }
    },
    "required": [
      "cc_members"
    ]
  },
  "errors": [
    {
      "$ref": "#/appendix/APIError"
    }
  ]
}
```

Get all known committee members.

###### Id

```
{
  "operation": "getCommitteeMemberById",
  "request": {
    "$ref": "#/cip-139/CCHotId"
  },
  "response": {
    "$ref": "#/cip-139/CCMember"
  },
  "errors": [
    {
      "$ref": "#/appendix/APIError"
    }
  ]
}
```

Get a specific Committee member by id.

##### Pool

###### All

```
{
  "operation": "getAllPools",
  "request": {},
  "response": {
    "type": "object",
    "properties": {
      "pools": {
        "type": "array",
        "items": {
          "$ref": "#/cip-139/Pool"
        }
      }
    },
    "required": [
      "pools"
    ]
  },
  "errors": [
    {
      "$ref": "#/appendix/APIError"
    }
  ]
}
```

Get all known stake pools.

###### Id

```
{
  "operation": "getPoolById",
  "request": {
    "$ref": "#/cip-139/PoolPubKeyHash"
  },
  "response": {
    "$ref": "#/cip-139/Pool"
  },
  "errors": [
    {
      "$ref": "#/appendix/APIError"
    }
  ]
}
```

Get a specific stake pool by id.

##### Proposal

###### All

```
{
  "operation": "getAllProposals",
  "request": {},
  "response": {
    "type": "object",
    "properties": {
      "proposals": {
        "type": "array",
        "items": {
          "$ref": "#/cip-139/Proposal"
        }
      }
    },
    "required": [
      "proposals"
    ]
  },
  "errors": [
    {
      "$ref": "#/appendix/APIError"
    }
  ]
}
```

Get all known proposals.

###### Id

```
{
  "operation": "getProposalById",
  "request": {
    "$ref": "#/cip-139/ProposalId"
  },
  "response": {
    "$ref": "#/cip-139/Proposal"
  },
  "errors": [
    {
      "$ref": "#/appendix/APIError"
    }
  ]
}
```

Get a specific proposal by id.

##### Era

###### Summary

```
{
  "operation": "getEraBySummary",
  "request": {},
  "response": {
    "type": "object",
    "properties": {
      "summary": {
        "type": "array",
        "items": {
          "$ref": "#/cip-139/EraSummary"
        }
      }
    },
    "required": [
      "summary"
    ]
  },
  "errors": [
    {
      "$ref": "#/appendix/APIError"
    }
  ]
}
```

Get the start and end of each era along with parameters that can vary between hard forks.


### Versioning

In this CIP we are defining two different APIs: the connection API for wallets, and the CIP-30 *[maybe this should have another name to prevent confusion?]* extension which enables an own-data wallet. These two are separate components, below there is a table with separate entries for the versions of the connection API and CIP-30 Extension respectively. 

While the CIP is in preparation, these versions shall be set to `0.0.0`. The moment this CIP is merged the versions shall be set to `1.0.0`, and all implementations should consider that the current version. Any changes to either API should come in form of PRs to this CIP.

|     |    |
| --- | --- |
| Version-Connection-API | 0.0.0 |
| Version-CIP-30-Extension | 0.0.0 |


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


#### Transport specific connectors

While this CIP attempts to define an API in a transport agnostic way, implementations will be forced to pick a specific transport. In the spec we have not given specifics on how to
namespace and generally structure the api in an implementation. This is both because details depend on the underlying transport that is chosen to implement the API, but also because
we wanted to make backwards compatibility with the original CIP-30 proposal as easy as possible.

Each transport specific implementation will make a choice on how to namespace access to the operations. In the following we give a description of how this should work for an implementation
using an injected javascript object. Support for different transports can be added to this CIP in form of PRs.

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

This wrapper will be relatively small, but must still take care in unifying the differences between this CIP and CIP-30. There is a list of some notable differences to keep in mind:

- JSON is used instead of CBOR. The wrapper must take care of translating arguments and results.
- This API has no pagination, while CIP-30 generally does. The wrapper can either implement pagination locally, or error and inform the user if they request it.
- In the original CIP-30, the `api` object returned has, on the top-level, the methods that we expect on `api.cip30`. The wrapper must take care to translate calls appropriately.
- CIP-30 allows for a situation where the user requests some extensions in the enable call, but despite the wallet not supporting those extensions, the `enable` call succeeds. This makes it so the dApps always have to check what extensions were actually enabled. In this CIP we don't allow that, so the wrapper must take care of calling `api.getExtension` after `cardano.{walletName}.enable` to check all required extensions are enabled, if that's not the case then throw an error.
- CIP-30 endpoints will return `null` in some situations where the request is correct, but not satisfiable. In this CIP we introduce an error code specifically for that. The wrapper will need to check some results for `null` and throw an appropriate error.
- Add an `api.apiVersion` method that returns the version for the connector

Implementing this wrapper is out of scope of this CIP,
but we welcome any effort in this direction, as it would make transitioning to this CIP easier for most wallets.


## Rationale: how does this CIP achieve its goals?

The goal of this CIP is to define the standard for a new wallet connector. This connector improves on CIP-30, both by fixing some of the shortcomings that
have been identified over time, and by extending its capabilities to be able to perform more queries.

We split the contributions of this CIP in two categories:

- Improve CIP-30
  - Introducing a transport agnostic way to define the behavior of these APIs
  - Separating the connection API from the different extension APIs the wallet can offer
  - Using JSON for Cardano domain types instead of CBOR
  - Making versioning explicit and adding support for specifying versions when enabling an extension

- Universal Query Layer extension
  - Adding a query layer extension API to enable a full data wallet


## Path to Active

- Implementing a wrapper that takes a CIP-30 compatible API and transforms it to be compatible with CIP-XXXX.
- This CIP depends on CIP-139 to be active, in particular wallets need to support the queries required by the `cip-139` extension.
- Two or more wallets implement support for this CIP.

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
