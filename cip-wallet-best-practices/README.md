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
While these recommendations cannot be enforced, by documenting them, we hope to bring awareness to them for all stakeholders.

## Motivation: why is this CIP necessary?

Caradno's architecture is fundamentally different from many other ecosystems.
This results in unique pitfalls for Cardano wallets which are not possible within different ecosystems.

The Cardano ecosystem enjoys a wide range of wallets, which is great for users, affording them a range of options.
Although this can bring challenges, ecosystem-level standardization can be difficult.

This proposal intends to improve the security and user experience base lines for all wallets in the Cardano ecosystem.

The stakeholders of this proposal are wallet users and wallet implementors.

### Security

By publicly documenting best practices we attempt to highlight potential security improvements for wallet implementors.
With pitfalls and solutions presented, wallets are made aware of challenges and mitigations.

### Inconsistent user experience

Conformity to standards results in more consistent user experience between wallets for users.
By collating a set of wallet standards which are preferred and adopted widely, we encourage further adoption.
This reduces the diparity between wallets, resulting in more consisten user experience.

## Specification

This specification aims to be a superset of best practices for all types of wallet.

### Meta

Wallets SHOULD;
- Open source
- conform to accepted standards
- use standard libraries
- allow users to do what they want, but can warn of dangerous situations

### Censorship

Wallets SHOULD;
- allow users to do what they want, but can warn of dangerous situations
- follow the permissionless philosophy of Cardano, and not censor.

### Keys

Wallets SHOULD;
- encrypt secret keys behind a passcode, thus only being able to use the secret key when user provides passcode to decrypt.
- never store the passcode in plain text, rather store a hash
- single address wallets should be aware that other wallets are multi-address
- be aware of relevant standards
- show bech32 encoded at all times
- address domain resolution (handles, ada domains, etc)

### Secrets

Wallets SHOULD;
- encrypted using user's passphrase
- decrypted secrets are in-memory for the least possible amount of time
- any references to secret objects should be overwritten with byte arrays with 0s
- user must always be asked to be able to decrypt secret key
- encrypted, as much as possible
- only decrypted for signing and derivation operations

### Transactions

Wallets SHOULD;
- inform of all assets being moved within a transaction
- strong warnings when wallet cannot verify the inputs to a transaction
- signing certificates with the wrong type of keys
  
### Staking

If wallets allow in-app staking then wallets SHOULD;
- allow delegation to all pools

### Governance

If wallets allow in-app governance features then wallets SHOULD;
- allow delegation to all DReps
- allow voting on all governance actions

## Rationale: how does this CIP achieve its goals?

A lot of these are already followed, but it is nice to have a formal list, for people to check against.

## Path to Active

### Acceptance Criteria

- [ ] Share proposal with all major Cardano wallet providers.

### Implementation Plan

#### Solicitation of feedback

- [x] Present first draft to the Wallets Working Group.
- [ ] Seek input from at least five wallet implementors.

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
