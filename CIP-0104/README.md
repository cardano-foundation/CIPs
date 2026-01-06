---
CIP: 104
Title: Web-Wallet Bridge - Account public key
Category: Wallets
Status: Proposed
Authors:
    - Ola Ahlman <ola.ahlman@tastenkunst.io>
    - Andrew Westberg <andrewwestberg@gmail.com>
Implementors:
- Eternl <https://eternl.io/>
- newm-chain <https://newm.io/>
- Gero <https://gerowallet.io/>
Discussions:
    - https://github.com/cardano-foundation/cips/pulls/588
Created: 2023-09-03
License: CC-BY-4.0
---

## Abstract
This CIP extends [CIP-30 (Cardano dApp-Wallet Web Bridge)](https://cips.cardano.org/cips/cip30/) to provide an additional endpoint for dApp to get the extended account public key from a connected wallet.

## Motivation: Why is this CIP necessary?
Normally it's up to the wallet to handle the logic for utxo selection, derived addresses etc through the established CIP-30 api. Sometimes however, dApp needs greater control due to subpar utxo selection or other specific needs that can only be handled by chain lookup from derived address(es). This moves the control and complexity from wallet to dApp for those dApps that prefer this setup. A dApp has better control and can make a more uniform user experience. By exporting only the account public key, this gives read-only access to the dApp.

## Specification
A new endpoint is added namespaced according to this cip extension number that returns the connected account extended public key as [`cbor<T>`](https://cips.cardano.org/cips/cip30/#cbort) defined in CIP30.

### 1. `api.cip104.getAccountPub(): Promise<cbor<Bip32PublicKey>>`

Errors: APIError

Returns hex-encoded string representing cbor of extended account public key. Throws APIError if needed as defined by CIP30.

Wallets implementing this CIP should, but not enforced, request additional access from the user to access this endpoint as it allows for complete read access to account history and derivation paths.

## Rationale: How does this CIP achieve its goals?
Raw cbor is returned instead of bech32 encoding to follow specification of other CIP30 endpoints.

## Path to Active

### Acceptance Criteria
In order for this standard to be active, the following should be true:
 - Implemented by at least two wallets.
 - Adopted and used by at least one dApp or infrastructure tool to prove usability.

### Implementation Plan
Communication with additional wallets established to widen availability

## Copyright
This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).

