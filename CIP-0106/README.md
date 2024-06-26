---
CIP: 106
Title: Web-Wallet Bridge - Multisig wallets
Status: Proposed
Category: Wallets
Authors: 
  - Leo
Implementors: 
  - BroClanWallet 
Discussions:
  - https://github.com/cardano-foundation/CIPs/pull/617
Created: 2023-10-12
License: CC-BY-4.0
---

## Abstract

This document describes a CIP-30 extension allowing webpages (i.e. dApps) to interface with Cardano Multisig-wallets. This document is a work in progress and is not yet finalized. It is expected to be updated as the ecosystem evolves. 

## Motivation: why is this CIP necessary?

In order to facilitate future dApp development, we will need a way for dApps to communicate with multisig wallets, given the unique complexities of native script based addresses. Special provisions need to be made to make the connector compatible with them.  

Specifically, apps building transactions need to be able to get the following information from the wallet:
- Script descriptor
  - Any transaction consuming a UTXO from a Plutus-based address must attach the corresponding script. 
- `ScriptRequirements`
  - The `TxContext` that is required to be able to validate the transaction. It encompasses all the possible combinations of requirements for the transaction to be valid, as such it is represented by an array of `ScriptRequirement` objects.
- Change Datum
  - The datum that will be used as the change output for the transaction. This is required for wallets based on Plutus V2 and before, as the change output must contain a datum to be valid and spendable.
  
Additionally, apps need to be able to submit a transaction to the wallet for signing in an asynchronous manner, as gathering of signatures can take a long time and each wallet provider will have its own way of handling this process. 

Finally, the signTx() and signData() endpoints will have to be disabled when using this extension since they are not compatible with native script based addresses.

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
type ScriptRequirement = {
    code: ScriptRequirementsCode,
    value: KeyHash|number,
}
```

### Aditional Error Types

#### CompletedTxError

```ts
CompletedTxErrorCode = {
	NotFound: 1,
	NotReady: 2
}
```

* NotFound - The transaction with the given id was not found.
* NotReady - The transaction with the given id is not ready yet. 

### Additional API Endpoints

#### api.cip106.getCollateralAddress(): Promise\<Address>

For Plutus V2 and later, partial collateral is supported. This function returns an address that can be used to add collateral to a transaction. The address returned must be owned by one of the signers in the list of signers returned by `api.getScriptRequirements()`. 

dApp developers can choose to use this address to add collateral to a transaction, or they can choose to use the `api.getCollateral()` function to get a list of UTXOs that can be used as collateral. If the dApp chooses to use this address, they must ensure that the address is not used for any other purpose, as the wallet may be using it to track collateral, and that the collateral return address is the same one.

#### api.cip106.getScriptRequirements: Promise\<ScriptRequirement[]>

Errors: `APIError`

Returns a list of ScriptRequirements that will be used to validate any transaction sent to the wallet.

#### api.cip106.getScript(): Promise\<cbor\<nativeScript>>

Errors: `APIError`

Returns the CBOR-encoded native script that controls this wallet. 

#### api.cip106.submitUnsignedTx(tx: cbor\<unsignedTransaction>): Promise\<hash32>

Errors: `APIError`, `TxError`

Submits a transaction to the wallet for signing. The wallet should check that the transaction is valid, gather the required signatures, compose the finalized transaction, and submit the transaction to the network. If the transaction is valid and the wallet is able to sign it, the wallet should return the transaction hash. If the transaction is invalid or the wallet is unable to sign it, the wallet should throw a `TxError` with the appropriate error code. The wallet should not submit the transaction to the network if it is invalid or the wallet is unable to sign it.

If the transaction contains hidden metadata, the wallet should not submit the transaction when it is ready, but return it to the dApp when the dApp calls the `getCompletedTx` function.

#### api.cip106.getCompletedTx(txId: hash32): Promise\[<cbor\<transaction>,cbor<transaction_witness_set>>]

Errors: `APIError`, `CompletedTxError`

If the transaction is not ready, the wallet should throw a `CompletedTxError` with the appropriate error code. If the transaction is ready, the wallet should return the CBOR-encoded transaction and the signatures.

### Altered API endpoints 

#### api.getCollateral(params: { amount: cbor\<Coin> }): Promise\<TransactionUnspentOutput[] | null>

Native script based addresses cannot provide collateral for transactions. Using this function, dApps can request the wallet to provide collateral for a transaction. The collateral must be a pure ADA UTXO, held by one of the signers in the list of signers returned by `api.getScriptRequirements()`.

### Disabled API endpoints

When connecting to a wallet using this extension the following endpoints will be disabled:

#### `api.signTx(tx: cbor<transaction>, partialSign: bool = false): Promise<cbor<transaction_witness_set>>` 


#### `api.signData(addr: Address, payload: Bytes): Promise<DataSignature>`

These endpoints should return an error if called when using this extension. 

## Rationale: how does this CIP achieve its goals?

See justification and explanations provided with each API endpoint.


## Path to Active

### Acceptance Criteria

- [ ] The interface is implemented and supported by multiple wallet providers.
- [ ] The interface is used by multiple dApps to interact with wallet providers. 
	
### Implementation Plan

- [x] Provide some reference implementation of wallet providers
	- [leo42/BroClanWallet](https://github.com/leo42/BroClanWallet)

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
