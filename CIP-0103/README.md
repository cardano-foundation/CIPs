---
CIP: 103
Title: Web-Wallet Bridge - Bulk transaction signing
Category: Wallets
Status: Active
Authors:
    - Martín Schere
    - Ola Ahlman <ola.ahlman@tastenkunst.io>
Implementors: 
    - JPG Store <https://www.jpg.store>
    - Eternl <https://eternl.io/>
    - Typhon <https://typhonwallet.io/>
Discussions:
    - https://github.com/cardano-foundation/CIPs/pull/443
    - https://github.com/cardano-foundation/CIPs/pull/587
Created: 2023-09-03
License: CC-BY-4.0
---

## Abstract
This CIP extends [CIP-30 (Cardano dApp-Wallet Web Bridge)](https://cips.cardano.org/cips/cip30/) to provide an additional endpoint for dApp to sign multiple transactions in bulk.

## Motivation: Why is this CIP necessary?
Currently, there is no way to sign multiple transactions in bulk, and the experience of signing a chain of transactions is suboptimal. We propose the addition of a signTxs endpoint that enable wallets to create an array of interconnected transactions and sign them all at once.

## Specification

### Data Types
#### TransactionSignatureRequest

```ts
type TransactionSignatureRequest = {|
  cbor: cbor<transaction>,
  partialSign: bool = false,
|};
```

Used to represent a single transaction awaiting a user's signature. More details on {partialSign} can be found in [api.signTx](https://cips.cardano.org/cips/cip30/#apisigntxtxcbortransactionpartialsignboolfalsepromisecbortransactionwitnessset) defined in CIP-30.

### Error Types

#### APIError
See [CIP-30 (Cardano dApp-Wallet Web Bridge) APIError](https://cips.cardano.org/cips/cip30/#apierror)

#### TxSignError
See [CIP-30 (Cardano dApp-Wallet Web Bridge) TxSignError](https://cips.cardano.org/cips/cip30/#txsignerror)

#### TxSendError
See [CIP-30 (Cardano dApp-Wallet Web Bridge) TxSendError](https://cips.cardano.org/cips/cip30/#txsignerror)

### `api.cip103.signTxs(txs: TransactionSignatureRequest[]): Promise<cbor<transaction_witness_set>[]>`

Errors: `APIError`, `TxSignError`

Signs a list of transactions where each transaction can either be independent and/or as a sequence of interconnected transactions where a subsequent transaction depends on a previous one. The returned array of witness sets directly correspond to the elements in the `txs` parameter, aligning the witness set at index 0 with the transaction at index 0, and so forth.

On sign error for any transaction in the array, no witnesses are to be returned. Instead a `TxSignError` is to be thrown. The error message thrown should include a reference to the transaction that caused the sign error, by including the index for failing transaction that map to the input array transaction list.

There are certain things that should be considered by wallets implementing this CIP, namely user visibility of what is signed. Though not explicitly specified in this CIP, as it would be up to the wallet to find a good solution, the wallet should make it clear to the user that multiple transactions are to be signed, and to give a clear overview/summary of what is signed. In addition to visibility, the wallet shall process the input transaction array in the same order as input parameter to allow transactions to be chained by accepting a previous transaction in the array to be used as input in a following transaction.

### `api.cip103.submitTxs(txs: cbor<transaction>[]): Promise<hash32[]>`

Errors: `APIError`, `TxSendError`

Extends [CIP-30 (Cardano dApp-Wallet Web Bridge) submitTx](https://cips.cardano.org/cips/cip30/#apisubmittxtxcbortransactionpromisehash32) with the ability to submit transactions in bulk. Transactions are to be submitted in the same order as provided as inputs. All transactions provided as input should be attempted to be submitted even in case of error. If all transactions are successfully submitted, an array of transaction ids is to be returned. In the case of one or multiple `Refused | Failure`, a `TxSendError | hash32` array is thrown. Each entry in the array represents either a successful submit with `hash32` (transaction id), or in the case of `Refused | Failure`, a `TxSendError` object. In both cases, the response array directly corresponds to the elements in the `txs` parameter.

### Versioning
Once approved and final, the proposal must be superseded by another if changes break the specification. Minor adjustments are allowed if needed to improve readability and resolve uncertainties. 

## Rationale: How does this CIP achieve its goals?
Allowing for bulk signing and submission of transactions can greatly improve the user experience by reducing the amount of steps needed to sign more than one transaction. Allowing multiple transactions to be provided in the same API call also reduces the burden for transaction chaining that was previously mainly possible by keeping track of node mempool to know if input utxo's are available to be spent. Submitting multiple transactions would still be possible without `submitTxs` addition using the already defined [CIP-30 (Cardano dApp-Wallet Web Bridge) submitTx](https://cips.cardano.org/cips/cip30/#apisubmittxtxcbortransactionpromisehash32) endpoint by calling it multiple times. However, allowing a bulk submit endpoint speeds up submission when many transactions are to be submitted at once as you wouldn't have to await each individual submission. 

## Path to Active

### Acceptance Criteria
In order for this standard to be active, the following should be true:
- [x] Implemented by at least two wallets.
- [x] Adopted and used by at least one dApp or infrastructure tool to prove usability.

### Implementation Plan
N/A

## Copyright
This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).


