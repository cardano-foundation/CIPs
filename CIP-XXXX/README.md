---
CIP: XXX
Title: Own-data Wallet Extension
Category: Tools
Status: Proposed
Authors:
  - Giovanni Garufi <giovanni@mlabs.city>
Implementors: []
Discussions:
    - https://github.com/cardano-foundation/cips/pulls/957
Created: 2024-02-05
License: CC-BY-4.0
Solution-To: CPS-0010
---

## Abstract


In this CIP we build upon the work laid out in [CIP-0144 | Wallet Connector API](https://github.com/cardano-foundation/CIPs/pull/957), which introduces a CIP-30 compatible wallet connection API. Our contribution is to define an extension which, when enabled, would result in what [CPS-0010](https://github.com/cardano-foundation/CIPs/blob/master/CPS-0010/README.md) defines as an "own-data wallet".


## Motivation: why is this CIP necessary?

[CIP-0144 | Wallet Connector API](link) introduces a new wallet connection API. However, a wallet can not do much without enabling some extensions. Here we present an extension that is equivalent to the familiar CIP-30 (In particular it implements the [full-api](https://cips.cardano.org/cip/CIP-30#full-api) section of CIP-30). Enabling this extension would give users a wallet that has the same capabilities as a CIP-30 wallet, this is defined as an "own-data wallet" in CPS-10.


## Specification

Following what is outlined in CIP-0144 we will use the same transport-agnostic format to define the API. See [here](link/#Transport-agnostic-operations) for more details.

We will reference several JSON schemas throughout the document, these are:

- [CIP-116 | Standard JSON encoding for Domain Types](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0116) which provides a JSON encoding of Cardano ledger types. Note that this CIP defines a schema for each ledger era. When referring to a type from this schema we refer to an `anyOf` of all the schemas in which that type is defined.
- [appendix](#appendix) in which we define schemas for types required by this extension and the error types

We will use an identifier in the anchor to refer to the schema where each type is defined. For example, if we want to reference the `Transaction` type, as defined in CIP-116 we will use the following schema reference `{ "$ref": "#/cip-116/Transaction" }`.

If an operation does not require any arguments as part of it's request, or does not return a meaningful response, we will represent this as an `{}` on the respective operation field. The arguments to an operation will always be represented as an object. If a field is not marked as `required`, then that argument is to be considered optional.

For each operation we will provide some details on how the implementation should behave. Note that some of these are taken verbatim from CIP-30.

#### CIP-XXXX

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

##### ApiVersion

```
{
  "operation": "apiVersion",
  "request": {},
  "response": { "$ref": "#/appendix/SemVer" },
  "errors": []
}
```

Returns the API version for the CIP-XXXX extension. This must correspond to the value of `CIP-XXXX` specified in this document, appropriately transformed into a `SemVer` object.

### Versioning

The version of this extension will be tracked in the table below.

While the CIP is in preparation, the version shall be set to `0.0.0`. The moment this CIP is merged the version shall be set to `1.0.0`, and all implementations should consider that the current version. Any changes to the connection API should come in form of PRs to this CIP.

| API | Version |
| --- | --- |
| CIP-XXXX | 0.0.0 |


### Appendix

This appendix contains additional schemas for types that are used in the APIs.

#### CIP-XXXX API Data Types


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

## Rationale: how does this CIP achieve its goals?

The goal of this CIP is to define an extension to enable an "own-data wallet". We build upon the work done in [CIP-0144 | Wallet Connector API](https://github.com/cardano-foundation/CIPs/pull/957) and define an extension compatible with that CIP.

## Path to Active

CIP-0144 includes a [section](link/#CIP-30-Backwards-compatibility) which introduces the idea of a wrapper, that takes a CIP-30 compatible API, and makes it CIP-0144 compatible. Since in this CIP we are simply replicating the functionality offered by CIP-30, something very similar would be possible here. Implementors of this wrapper must take care of the following differences between this CIP and CIP-30.

- JSON is used instead of CBOR. The wrapper must take care of translating arguments and results.
- This API has no pagination, while CIP-30 generally does. The wrapper can either implement pagination locally, or error and inform the user if they request it.
- In the original CIP-30, the `api` object returned has, on the top-level, the methods that we expect on `api.cip30`. The wrapper must take care to translate calls appropriately.
- CIP-30 endpoints will return `null` in some situations where the request is correct, but not satisfiable. In this CIP we introduce an error code specifically for that. The wrapper will need to check some results for `null` and throw an appropriate error.

### Acceptance Criteria

- [ ] There is at least one implementation for a CIP-30 compatibility wrapper as explained in the preceding section.
- [ ] Two or more wallets implement support for this CIP.

### Implementation Plan

- [ ] Implement a wrapper that takes a CIP-30 compatible API and transforms it to be compatible with CIP-XXXX.

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
