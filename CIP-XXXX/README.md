---
CIP: ?
Title: Web-Wallet Bridge: Bulk transaction signing
Category: Wallets
Status: Proposed
Authors:
    - Martín Schere
    - Ola Ahlman <ola.ahlman@tastenkunst.io>
Implementors: 
    - JPG Store <https://www.jpg.store>
    - Eternl
    - Typhon
Discussions:
    - https://github.com/cardano-foundation/CIPs/pull/443
    - https://github.com/cardano-foundation/CIPs/pull/587
Created: 2023-09-03
License: CC-BY-4.0
---

## Abstract
This CIP extends [CIP-30 (Cardano dApp-Wallet Web Bridge)](https://cips.cardano.org/cips/cip30/) to provide an additional endpoint for dApp to sign multiple transactions in bulk.

## Motivation: why is this CIP necessary?
Currently, there is no way to sign multiple transactions in bulk, and the experience of signing a chain of transactions is suboptimal. We propose the addition of a signTxs endpoint that enable wallets to create an array of interconnected transactions and sign them all at once.

## Specification

### TransactionSignatureRequest

```
type = TransactionSignatureRequest {|
  cbor: cbor\<transaction>,
  partialSign: bool = false,
|};
```

Used to represent a single transaction awaiting a user's signature. More details on {partialSign} can be found in [api.signTx](https://cips.cardano.org/cips/cip30/#apisigntxtxcbortransactionpartialsignboolfalsepromisecbortransactionwitnessset) defined in CIP-30.

### api.cip????.signTxs(txs: TransactionSignatureRequest[]): Promise\<cbor\<transaction_witness_set>[]>

Errors: `APIError`, `TxSignError`

Signs a chain of transactions, which can be described as a sequence of interconnected transactions where each subsequent transaction depends on the previous one. The returned array values of the witness set directly correspond to the elements in the `txs` parameter, aligning the witness set at index 0 with the transaction at index 0, and so forth.

## Rationale: how does this CIP achieve its goals?
Allowing for bulk signing of transactions can greatly improve user experience in certain situations. There are however certain things that should be considered by wallets implementing this CIP, namely user visibility of what is signed. Though not explicitly specified in this CIP, as it would be up to the wallet to find a good solution, the wallet should make it clear to the user that multiple transactions are to be signed, and to give a clear overview of what is signed. In addition to visibility, the wallet shall process the input transaction array in order to allow transactions to be chained by accepting a previous transaction in the array to be used as input in a following transaction.

## Path to Active

### Acceptance Criteria
In order for this standard to be active, the following should be true:
- [x] Implemented by at least two wallets.
- [x] Adopted and used by at least one dApp or infrastructure tool to prove usability.

### Implementation Plan
Already implemented by dApp(s) and wallet(s).

## Copyright
[CC-BY-4.0]: https://creativecommons.org/licenses/by/4.0/legalcode


