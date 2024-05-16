---
CIP: ?
Title: Wallet best practices
Category: Wallets
Status: Proposed
Authors:
    - Ryan Williams <ryan.williams@intersectmbo.org>
Implementors: []
Discussions:
    - https://github.com/cardano-foundation/CIPs/pull/815
Created: 2024-05-08
License: CC-BY-4.0
---

## Abstract

Cardano boasts a wide and competitive wallet ecosystem.
Diversity brings advantages but can also lead to disperse functionalities.

Here we describe a common set of best practices for wallet implementors that aim to improve wallet security and user experience across the ecosystem.
While these recommendations cannot be enforced, by documenting them, we aim to bring awareness to them for all stakeholders.

## Motivation: why is this CIP necessary?

The Cardano ecosystem enjoys a wide range of wallets, this is great for users, affording them a range of options.
Although this can bring challenges, ecosystem level standardization can be difficult.

This proposal intends to improve the security and user experience base lines for all wallets in the Cardano ecosystem.

The stakeholders of this proposal are wallet users and wallet implementors.

### Security

- documenting best practices ensures that all wallet implementors can at least be aware, first step to conforming
- improve security baselines, no excuses
- may help users choose *safer* wallets

### Inconsistent user experience

- inherently complex things, derivation/addresses are hard to explain
- lead to a worse experience causing people to leave the ecosystem
- can lead to confusion for users across wallets, could lead to mistakes

## Specification

### Meta

- open source
- should attempt to conform to standards/ formally describe
- passcode protected
- should allow users to do what they want, but can warn of dangerous situations

### Derivation/ Addresses

- single address wallets should be aware that other wallets are multi-address
- be aware of relevant standards

### Secrets

- encrypted using user's passphrase
- decrypted secrets are in-memory for the least possible amount of time
- any references to secret objects should be overwritten with byte arrays with 0s
- user must always be asked to be able to decrypt secret key
- encrypted, as much as possible
- only decrypted for signing and derivation operations

### Transactions

- inform of all assets being moved within a transaction
- strong warnings when wallet cannot verify the inputs to a transaction
- signing certificates with the wrong type of keys
  
### Staking

- should allow delegation to all

### dApp Connector

### Governance

## Rationale: how does this CIP achieve its goals?

A lot of these are already followed, but it is nice to have a formal list, for people to check against.

## Path to Active

### Acceptance Criteria

- [ ]
- [ ]
- [ ]

### Implementation Plan

- [ ] Present this proposal to the Wallets Working Group
- [ ] Seek input from at least five wallet implementors

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
