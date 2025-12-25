---
CIP: /?
Title: Preparing and Signing x509 Metadata
Category: MetaData
Status: Proposed
Authors:
    - Steven Johnson<steven.johnson@iohk.io>
Implementors: []
Discussions:
    - https://github.com/cardano-foundation/CIPs/pull/813
Created: 2023-10-24
License: CC-BY-4.0
---

<!-- markdownlint-disable MD025-->
# Role Based Access Control Registration

## Abstract

This document defines how a dApp will use the wallet connect interfaces of CIP-30 to produce and sign
x509 registration transactions.

## Motivation: why is this CIP necessary?

The x509 certificate metadata CIPs are complex, and it is required to clearly document how they
can be produced using standard tooling.

The primary motivation is that the registration can be produced with existing interfaces.

Wallets MAY OPTIONALLY detect this registration format and display it in a more meaningful way to users.
But that is not required.

The aim is to have broad interoperability with ALL wallets that already implement CIP-30.

## Specification

### Components of an individual transaction

![Cardano Transaction Anatomy](./images/cardano-transaction.svg)

### Creation and Signing procedure

![Creation/Signing procedure](../x509-envelope-metadata/images/metadata-envelope-process.svg)

### Wallet interaction

CIP 30 defines two main functions.

1. signData
2. signTransaction

We deliberately do NOT use signData.
The reason is signData has limitations, primarily it can ONLY sign data with a single key.

it is also incapable of creating data that can not be replayed across transactions, which is a requirement.

Accordingly, the entire transaction is produced using `signTransaction`.

Following the procedure described above, the prepared transaction and complete metadata
(which has been pre-signed with the role 0 keys of the user) are sent to the wallet to be signed.

The Transaction MUST include where appropriate extra keys in `required signers` in the transaction to properly
link the off-chain role keys with on-chain keys.

The wallet DOES NOT need to know that the metadata has this requirement, it simply sees the keys it needs to witness
the transaction with, and prompts the user to sign.

#### Enhanced UX

The Role registration metadata is general in form.

A Wallet MAY elect to detect that it is signing a role registration and
present the data in a form which is easier for the user to reason through.

It may also be aware of key supported dApps and provide even further information.
It can also perform both universal and dApp specific validity checks against the registration to ensure
it is properly structured by the dApp.

However, the Wallet should simply WARN the user if it detects a problem, and not prevent the user from
signing the transaction.

Once the wallet has signed the transaction, the dApp will have a fully signed role registration transaction and metadata.
It will be impossible for the dApp or anyone else to separate the metadata from the transaction and retain its validity.
It is impossible to replay the metadata on a new transaction and it retain validity.

With the complete transaction properly signed, it can then be posted on-chain.

### Posting the transaction

Once the transaction has been properly constructed and signed, anyone with a copy of it can post it on-chain.

it is recommended that dApps post the transaction to their own backend logic, which handles posting the data on-chain
vs posting the data on-chain through the wallet.

The reason for this, is this affords the dApp backend the opportunity to
validate the registration data in its entirety before posting it on-chain.

It is preferable to inform a user their registration is invalid or has problems
BEFORE they spend the ADA required to post the transaction,
and the only authoritive way this can be achieved is through the dApp.

having validated the registration would be valid if posted on-chain, it is then posted by the dapp on-chain.

Once the dApp sees the registration appear in the ledger,
it is now confirmed that not only was the registration valid, but that the transaction itself was valid,
properly spent valid UTXOs, etc.

The dApp may cache registration data it received from users,
but it should never act on it until it has been seen validly posted on-chain.

## Rationale: how does this CIP achieve its goals?

This CIP defines wallet interactions and how CIP-30 is used to create and
post transactions that conform to the x509 metadata specification.

## Path to Active

To-do.

### Acceptance Criteria

To-do.

### Implementation Plan

To-do.

## References

To-do.

## Copyright

This CIP is licensed under [CC-BY-4.0]

Code samples and reference material are licensed under [Apache 2.0]

[CC-BY-4.0]: https://creativecommons.org/licenses/by/4.0/legalcode
[Apache 2.0]: https://www.apache.org/licenses/LICENSE-2.0.html
