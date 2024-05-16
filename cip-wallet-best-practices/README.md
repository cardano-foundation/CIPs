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
Diversity brings advantages, but can lead to disperse functionalities.

Here we describe a common set of best practices for wallet implementors, in aims to improve security and user experience across the ecosystem.
Whilst these recommendations cannot be enforced, by documenting them we aim to bring awareness to them for wallets

## Motivation: why is this CIP necessary?
<!-- A clear explanation that introduces the reason for a proposal, its use cases and stakeholders. If the CIP changes an established design then it must outline design issues that motivate a rework. -->

This proposal intends to improve the security and user experience base lines for all wallets in the Cardano ecosystem.

The stakeholders of this proposal are wallet users and wallet implementors.

- Cardano wallets are quite different from a lot of other ecosystem wallets

### Security

- documenting best practices ensures that all wallet implementors can at least be aware, first step to conforming
- improve security baselines, no excuses
- may help users choose *safer* wallets

### Inconsistent user experience

- inherently complex things, derivation/addresses are hard to explain
- lead to a worse experience causing people to leave the ecosystem
- can lead to confusion for users across wallets, could lead to mistakes

## Specification

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

### Meta

- open source
- should attempt to conform to standards/ formally describe
- password protected
  
### Staking

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
