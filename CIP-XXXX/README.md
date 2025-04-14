---
CIP: ?
Title: Orthogonal Certificates
Status: Proposed
Category: Ledger
Authors:
    - Joshua Marchand <josh@securitybot.info>
Implementors: N/A
Discussions:
    - https://discord.gg/tsr7H6ApdT
    - https://github.com/cardano-foundation/CIPs/pull/1021
Created: 2025-04-13
License: CC-BY-4.0
---

## Abstract

This CIP proposes a simplified design of stake managmenet certificate types focused on simplicity and usability.

The current Conway era ledger specification includes multiple certificate types each representing different combinations of stake registration, delegation, and vote delegation. This proposal simplifies this specification by defining a set of orthogonal certificate types that can be composed to achieve the same functionality, making the ledger more intuitive and easier to document, use, and maintain.

## Motivation: why is this CIP necessary?

The Conway era introduces multiple certificate types for various stake operations including combinations of:

- Registering a stake credential
- Delegating stake to a pool
- Delegating voting power to a DRep

This approach results in many complex and convoluted certificate types, increasing complexity for developers and users. The number of certificate types would also grow combinatorially with new features, making it only harder to document, extend, and understand the certificates.

By redesigning the certificate types with orthogonal certificates, we can:
 - Make the system more intuitive for users and developers
 - Simplify documentation by having self-describing, single-purpose certificates
 - Make ledger implementations easier to maintain
 - Avoid combinatorial growth of certificates with future features


## Specification

### Current Certificates CDDL
The Conway era has multiple certificate types for stake related operations:
```
certificate = [stake_registration
               // stake_deregistration
               // stake_delegation
               // pool_registration
               // pool_retirement
               // reg_cert
               // unreg_cert
               // vote_deleg_cert
               // stake_vote_deleg_cert
               // stake_reg_deleg_cert
               // vote_reg_deleg_cert
               // stake_vote_reg_deleg_cert
               // auth_committee_hot_cert
               // resign_committee_cold_cert
               // reg_drep_cert
               // unreg_drep_cert
               // update_drep_cert]

stake_registration = (0, stake_credential)
stake_deregistration = (1, stake_credential)
stake_delegation = (2, stake_credential, pool_keyhash)
reg_cert = (7, stake_credential, coin)
unreg_cert = (8, stake_credential, coin)
stake_vote_deleg_cert = (10, stake_credential, pool_keyhash, drep)
stake_reg_deleg_cert = (11, stake_credential, pool_keyhash, coin)
stake_vote_reg_deleg_cert = (13, stake_credential, pool_keyhash, drep, coin)
...
```

### Proposed CDDL
While the current certificates may save a few bytes in the transaction when doing multiple actions in a single transaction, it greatly complicates certificates for both users and implementers.

Instead, we propose a much simpler certificate design with orthogonal certificates.
```
certificate = pool_registration
               / pool_retirement
               / auth_committee_hot_cert
               / resign_committee_cold_cert
               / reg_drep_cert
               / unreg_drep_cert
               / update_drep_cert
               / stake_registration_cert
               / stake_deregistration_cert
               / stake_delegation_cert
               / vote_delegation_cert

; New orthogonal certificates
stake_registration_cert = (N, stake_credential, coin)
stake_deregistration_cert = (N+1, stake_credential, coin)
stake_delegation_cert = (N+2, stake_credential, pool_keyhash)
vote_delegation_cert = (N+3, stake_credential, drep)

; Others remain unchanged
```

### Semantics
The orthogonal certificates creates a clear seperation of concerns, where each certificate has a clear, single responsibility:

- `stake_registration_cert` - Registers a specified stake credential
- `stake_deregistration_cert` - Deregisters a specified stake credential
- `stake_delegation_cert` - delegates the stake controlled by a specified stake credential to a specified pool
- `vote_delegation_cert` - delegates the voting power of a specified stake credential to a specified DRep

### Handling Multiple Certificates
To perform multiple operations, such as registration and stake delegation, multiple certificates would be included in a single transaction. The ledger would process certificates in the order that they are provided. If a stake delegation occurs before the registration of the specified stake credential, that delegation is invalid.


### Example Usage
To achieve the functionality of the current certificates:


| Existing Certificate | Orthogonal Certificate Equivalent |
| -------- | -------- |
| `reg_cert`              | `stake_registration_cert`       |
| `unreg_cert`            | `stake_deregistration_cert`     |
| `stake_delegation`      | `stake_delegation_cert`         |
| `stake_vote_deleg_cert` | `stake_delegation_cert` +  `vote_delegation_cert`   |
| `stake_reg_deleg_cert`      | `stake_registration_cert` + `stake_delegation_cert`   |
| `stake_vote_reg_deleg_cert` | `stake_registration_cert` + `stake_delegation_cert` + `vote_delegation_cert`  |


## Rationale: how does this CIP achieve its goals?

The orthogonal certificate provides **Conceptual Clarity** which has several benefits:
1. **Usage:** The transaction is the fundamental interface for Cardano. It should be as simple as possible for users.
2. **Documentation:** Each certificate is self-describing and encapsulates a single action, making documentation much easier to write.
3. **Implementation:** Implementing the ledger should be as simple as possible–without losing features or security–to reduce the risk of an incorrect implementation resulting in a fork.

While composite actions would require multiple certificates, multiple small certificates would only add a couple of bytes when compared to the composite certificates.

## Path to Active

### Acceptance Criteria

- [ ]Acceptance of the Ledger team, as well as alternative node implementation maintainers (Amaru, Dingo, and others)

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
