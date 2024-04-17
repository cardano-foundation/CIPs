---
CIP: 106
Title: Web-Wallet Bridge - Mutlisig wallets
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

This document describes a CIP-30 extension allowing webpages (i.e. dApps) to interface with Cardano Plutus-wallets. This document is a work in progress and is not yet finalized. It is expected to be updated as the ecosystem evolves. 

## Motivation: why is this CIP necessary?

In order to facilitate future dApp development, we will need a way for dApps to communicate with plutus wallets, given the unique complexities of plutus based addresses. Special provisions need to be made to make the connector compatible with them.  

Specifically, apps building transactions need to be able to get the following information from the wallet:

- Script descriptor
- ScriptRequirements
- Change Datum

Additionally, apps need to be able to submit a transaction to the wallet for signing in an asynchronous manner, as gathering of signatures can take a long time and each wallet provider will have its own way of handling this process. 

Finally, the signData() endpoint will have to be disabled when using this extension since they are not compatible with plutus based addresses. plutus contracts cannot sign data, only validate transactions.

### Rationale for the required data

- Script descriptor:
    Any transaction consuming a UTxO from a plutus based address must attach the corresponding script. 

- ScriptRequirements
    The TxContext that is required to be able to validate the transaction. It encompasses all the possible combinations of requirements for the transaction to be valid, as such it is represented by an array of ScriptRequirement objects.

- Change Datum
    The datum that will be used as the change output for the transaction. This is required for wallets based on Plutus V2 and before, as the change output must contain a datum to be valid and spendable.

## Specification

### Versioning

To facilitate future updates, the API will be versioned. Newer version of the API have to be compatible with the previous versions. 

The current version of the API is 2.0, the major version number is derived from the version of Plutus that the API implements, and the minor version number is used for incremental updates within the same version of Plutus.

### Data Types

#### KeyHash

A hex-encoded string of the corresponding bytes. This represents the hash of the public key used to sign transactions.

```ts
type KeyHash = String
```

#### ScriptRequirements

Script requirements encapsulate all the possible requirements for a transaction to be valid. It includes the following fields:

- collateral: The list of inputs that will be used as collateral for the transaction.
- inputs: The list of inputs that will be used as inputs for the transaction.
- reference_inputs: The list of inputs that will be used as reference inputs for the transaction.
- outputs: The list of outputs that will be used for the transaction.
- mint: The amount of tokens that will be minted/burned in the transaction.
- certificates: The list of certificates that will be included in the transaction.
- withdrawals: The list of withdrawals that will be included in the transaction.
- validity_range: The validity range that the transaction must be valid in.
- signatories: The list of signatories that must sign the transaction.
- redeemers: The list of redeemers that will be used in the transaction.
- datums: The list of datums that will be used in the transaction.


```ts
type ScriptRequirement = {
  collateral?: List<transaction_input>,
  inputs?: List<transaction_input>,
  reference_inputs?: List<transaction_input>,
  outputs?: List<transaction_output>,
  mint?: Value,
  certificates?: List<Certificate>,
  withdrawals?: Dict<StakeCredential, Int>,
  validity_range?: ValidityRange,
  signatories?: List<KeyHash>,
  redeemers?: Dict<ScriptPurpose, Redeemer>,
  datums?: Dict<Hash<Blake2b_256, Data>, Data>
}
```

#### ValidityRange

```ts
type ValidityRange = {
  valid_before?: PosixTime,
  valid_after?: PosixTime,
}
```

#### Value
```ts
type Value = {
    amount: Coin,
    asset: String
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

## Motivation: why is this CIP necessary?

In order to facilitate future dApp development, we will need a way for dApps to communicate with Plutus wallets. Given the unique complexities of Plutus script-based addresses, special provisions need to be made to make the connector compatible with them.

Specifically, apps building transactions need to be able to get the following information from the wallet:

- Script descriptor
- Script Requirements list
- Collateral donator

Additionally, apps need to be able to submit a transaction to the wallet for signing in an asynchronous manner, as gathering of signatures can take a long time and each wallet provider will have its own way of handling this process.

Finally, the `signTx()` and `signData()` endpoints will have to be disabled when using this extension since they are not compatible with native-script-based addresses.

## Rationale for the required data

- Script descriptor: Any transaction consuming a UTxO from a native-script-based address must attach the corresponding script.
- Script Requirements list: 
    -- dApps need to know the scriptContext under which the transaction will be validated.
    -- dApps need to know the collateral donator to attack the collateral to the transaction.
    -- dApps need to know the Datum of the Utxos that it will be consuming.
    -- dApps need to know the Redeemers that will be used in the transaction.
- Change Datum
    -- dApps need to know the Datum that will be used as the change output for the transaction. This is mandatory for wallets based on Plutus V2 and before, as the change output must contain a datum to be valid and spendable.

### Additional API Endpoints

#### api.getScriptRequirements: Promise<ScriptRequirement[]>

Errors: `APIError`

Returns a list of `ScriptRequirements` that will be used to validate any transaction sent to the wallet. Every field in the `ScriptRequirements` object is optional, and the wallet should only include the fields that are relevant to the current transaction. 

For wallets with multiple spend conditions, separate entries in the list should be used to represent each spend condition. Wallet providers should implement UX to allow users to order the list of `ScriptRequirements` from most to least preferred. DApps should use the first entry in the list that is valid for the current transaction or select one based on the logic of their use-case.

#### api.getScript(): Promise[<number<plutusVersion>],<CBOR<plutusScript>>

Errors: `APIError`

Returns the CBOR-encoded Plutus script that controls this wallet. 

#### api.submitUnsignedTx(tx: CBOR<unsignedTransaction>): Promise<hash32>

Errors: `APIError`, `TxError`

Submits a transaction to the wallet for signing. The wallet should check that the transaction is valid, gather the required signatures, compose the finalized transaction, and submit the transaction to the network. If the transaction is valid and the wallet is able to sign it, the wallet should return the transaction hash. If the transaction is invalid or the wallet is unable to sign it, the wallet should throw a `TxError` with the appropriate error code. The wallet should not submit the transaction to the network if it is invalid or the wallet is unable to sign it.

If the transaction contains hidden metadata, the wallet should not submit the transaction when it is ready, but return it to the dApp when the dApp calls the `getCompletedTx` function.

It is expected that this will be the endpoint used by all wallets that require multiple signatures to sign a transaction. 

#### api.getCompletedTx(txId: hash32): Promise[<CBOR<transaction>,CBOR<transaction_witness_set>>]

Errors: `APIError`, `CompletedTxError`

If the transaction is not ready, the wallet should throw a `CompletedTxError` with the appropriate error code. If the transaction is ready, the wallet should return the CBOR-encoded transaction and the signatures.

### Altered API endpoints 

#### api.signTx(tx: CBOR<transaction>, partialSign: bool = false): Promise<CBOR<transaction_witness_set>>

This endpoint will now optionally return an error if the smart Wallet is a multiparty schema and signatures need to be gathered from multiple parties asynchronously. 

### Removed API endpoints
When connecting to a wallet using this extension the following endpoints will be disabled:

#### `api.getCollateral(params: { amount: CBOR<Coin> }): Promise<TransactionUnspentOutput[] | null>`

Collateral will be provided as an optional field in the `ScriptRequirements` object. This will allow the wallet to provide the collateral when needed, and the dApp to know if the wallet can provide collateral or not for various validation scenarios on the same wallet.

#### `api.signData(addr: Address, payload: Bytes): Promise<DataSignature>`

Plutus contracts cannot sign data, only validate transactions. This endpoint will be disabled when connecting to a wallet using this extension.

## Rationale: how does this CIP achieve its goals?

See justification and explanations provided with each API endpoint.

## Path to Active

### Acceptance Criteria

- [ ] The interface is implemented and supported by various wallet providers.
- [ ] The interface is used by DApps to interact with wallet providers. 

### Implementation Plan

- [ ] Provide some reference implementation of wallet providers
    - [leo42/BroClanWallet](#incomplete)

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).