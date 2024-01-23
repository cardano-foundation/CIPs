---
CIP: 111
Title: Wallet Transaction Caching
Status: Proposed
Category: Wallets
Authors:
    - Josh Marchand <josh@securitybot.info>
Implementors: []
Discussions:
 - https://github.com/cardano-foundation/CIPs/pull/733
Created: 2023-12-22
License: CC-BY-4.0
---

## Abstract

This CIP extends [CIP-0030 Cardano dApp-Wallet Web Bridge](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0030/) and [CIP-0103? | Web-Wallet Bridge - Bulk Transaction Signing](https://github.com/cardano-foundation/CIPs/pull/587) to allow wallets to provide a complete and accurate summary of transactions that spend outputs that don't exist on chain yet when possible, and clearly communicate to the user risks when they cannot.

## Motivation: why is this CIP necessary?

Transaction chaining, building transactions that spend outputs of transactions that aren't settled on chain, allows dApps to quickly do several on-chain transactions instead of waiting for each individual transaction to settle before building and submitting the next one. This is a powerful feature that has allowed dApps to provide seamless experiences to users. However, due to the transactions data structure, wallets are unable to provide a complete and accurate summary of these chained transactions when prompting users for a signature.

A transaction input, which is a reference to a previous transaction output, is defined in the [babbage CDDL](https://github.com/IntersectMBO/cardano-ledger/blob/master/eras/babbage/impl/cddl-files/babbage.cddl) as follows:

```
transaction_input = [ transaction_id : $hash32
                    , index : uint
                    ]
```

Therefore, in order for a wallet to know what assets are being spent by a transaction, it must have access to the transaction that the input is referencing. This is not a problem when the transaction inputs reference transactions that have settled on chain. However, when a transaction is being signed that spends outputs that don't exist on chain yet, the wallet cannot know what the spent UTxOs actually contain.

A malicious actor could take advantage of this by creating two transactions that are chained together. The first transaction would be a transaction that spends a user's UTxOs and creates new UTxOs that are locked by the user's address. The second transaction would then spend these new UTxOs and send the funds to the attacker's address. The malicious actor would then prompt the user to sign both transactions, using [CIP 30's signTx](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0030/README.md#apisigntxtx-cbortransaction-partialsign-bool--false-promisecbortransaction_witness_set) endpoint. The first transaction summary would show nothing malicious, and the user would thus sign it. The second transaction would show an incorrect or incomplete transaction summary, and because user's are used to seeing those summaries from other dApps, they may sign the second transaction, effectively sending all their assets to the attacker.

Simply caching signed tranasctions before they appear on chain and refusing to sign transactions that spend outputs that don't exist on chain yet would solve this problem. However, this would break some transaction chaining done by dApps, where they reference UTxOs that were created in a transaction that didn't involve the user but hasn't settled yet. Therefore, the best solution would be to cache signed transactions and display a clear warning to the user when a transaction includes inputs that reference outputs that can't be found.

## Specification

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in [RFC 2119](https://datatracker.ietf.org/doc/html/rfc2119).

### Defintions

**Wallet**: A wallet is any software that manages a user's private keys and provides basic cryptographic operations such as signing data, for the purpose of interacting with the Cardano blockchain.

---

A wallet MUST maintain a cache of signed transactions that have not yet settled on chain. This cache MAY have a maximum size, and if the cache is full, the wallet MAY remove transactions from the cache, beginning with the oldest transaction to store a newer transaction. The wallet MAY remove cached transactions once they are seen on chain.

If a user signs a transaction through the [CIP-30 signTx](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0030/README.md#apisigntxtx-cbortransaction-partialsign-bool--false-promisecbortransaction_witness_set) endpoint, the [CIP-103? signTxs](https://github.com/cardano-foundation/CIPs/blob/508ea0557bcd17d793da90312789165dcef8a4db/CIP-0103/README.md#apicip103signtxstxs-transactionsignaturerequest-promisecbortransaction_witness_set) endpoint, or any other CIP-30 extension that allows signing transactions, the wallet MUST cache the signed transaction with a TTL (time-to-live) greater than or equal to the [TTL of the transaction](https://github.com/IntersectMBO/cardano-ledger/blob/master/eras/babbage/impl/cddl-files/babbage.cddl#L57C8-L57C9). The wallet MUST NOT remove the transaction from the cache until the TTL has expired, the transaction has been seen on chain, or the cache is full and the wallet needs to remove transactions to make room for newer transactions.

When displaying a transaction summary to the user, the wallet MUST search for the outputs referenced by inputs in the following order:

1. The latest known on-chain UTxO set
2. The cache of signed transactions
3. The set of transactions being signed

If a transaction contains an input that references an output that cannot be found, the wallet MUST display a warning to the user that the transaction includes unidentifiable inputs. The style and wording of this warning is left up to the wallet. The wallet MAY prevent the user from signing a transaction with unidentified inputs, but this may cause issues when interacting with some dApps.

## Rationale: how does this CIP achieve its goals?

The proposed approach allows wallets to provide a complete and accurate summary of transactions without prohibiting transaction chaining or requiring dApps to change the way they interface with wallets.

Although it cannot entirely reduce the risk of a malicious actor tricking a user into signing a transaction that they didn't intend to, it will hopefully reduce the risk by showing an accurate summary of the transaction more often and, when not possible, displaying a clear warning to the user.

## Path to Active

### Acceptance Criteria

In order for this standard to be considered 'Active', the following criteria must be met:

- [ ] A thorough review by all relevant stakeholders
- [ ] Implementation in at least two Cardano wallets

### Implementation Plan

N/A

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
