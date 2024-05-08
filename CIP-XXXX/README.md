---
CIP: /?
Title: Project Catalyst Role Registrations
Category: MetaData
Status: Proposed
Authors:
    - Steven Johnson<steven.johnson@iohk.io>
Implementors: []
Discussions:
    - https://github.com/cardano-foundation/CIPs/pull/814
Created: 2023-10-24
License: CC-BY-4.0
---

## Abstract

Project Catalyst requires better role registration and is utilizing x509 certificate RBAC for this purpose.
This document defines how that standard is applied to Project Catalyst role registrations.

## Motivation: why is this CIP necessary?

As the project catalyst dApp grew,
it became clear there was a need for an extensible and flexible Role based Access control system to support its needs.

This CIP builds upon the x509 RBAC Specification CIPs and defines how they are used for Project Catalyst Roles.

## Specification

Project Catalyst defines 2 dApp ID's.

| dApp ID | Role Group |
| --- | --- |
| `ca7a1457-ef9f-4c7f-9c74-7f8c4a4cfa6c` | Project Catalyst User Role Registrations |
| `ca7ad312-a19b-4412-ad53-2a36fb14e2e5` | Project Catalyst Admin Role Registrations |

User Roles are self registered by individual users.
Admin roles are managed.

We define these two RBAC Role Groups to allow them to be managed in an easier way.

### Project Catalyst User Role Registrations

The following user roles are defined:

| Role ID | Role Description |
| -- | -- |
| 0 | Voter |
| 1 | Delegated Representative |
| 2 | Voter Delegation |
| 3 | Proposer |

Further User roles will be added to this specification as those roles are defined.

#### Voter Role

Voters are the most basic role within Project Catalyst.
They can Vote and Comment on Proposals.
They MAY earn rewards for their participation, and MAY earn reputation.

X509 registrations require a Role 0 registration.
Role 0 is the Basic Voter Role.

The Role 0 registration certificate MUST be linked to AT LEAST ONE stake address on-chain.
It can be linked to multiple stake addresses, but they must all be witnessed in the transaction to be valid.

The Voters Role 0 signing key from their certificate is also used by the voter to:

1. Establish their identity to backend systems (Decentralized Authorization).
2. Sign votes in a Catalyst event.
3. Witness Comments made on proposals.

The Certificate MUST be self signed.
Currently CA's are not supported for Catalyst User Roles.

The Project Catalyst dApp generates a Public/Private key pair and creates the user Role 0 certificate,
associates it with their on-chain stake address, and signs the certificate.

This allows each user to have full custody of their own Catalyst voting identity.
They may also change their Signing Key at any time by rolling their Role 0 certificate as described
in the x509 metadata specifications.

In the initial implementation the Signing key used in the certificate MUST BE an ED25519 certificate.
No other kind of signature algorithm is allowed.

#### Delegated Representative (dRep)

A dRep is a registration that is made, which allows for voters to give their voting power to the dRep who
then votes on their behalf.

dReps must register a simple signing key, it must be referenced to the first signing key in the simple key array.
dReps do not use certificates to manage their signing key.

dReps may register a new Payment address, if they do not register a new payment address, the payment address
registered to Role 0 will be used for the dRep rewards.

dReps MAY attach extra information to their registration:

| Data Key | Information |
| -- | -- |
| 10 | Name |
| 11 | [ + URL Link to Profile ] |
| 12 | ADA Handle |

#### Voter Delegation

A Voter Delegation role assigns a voters voting power to a registered dRep.

The dRep, will use the voters voting power, pooled with other delegations to vote on behalf of the voter.

Delegation does not define a signing key, not an encryption key.

Delegation roles ONLY contain a dApp specific data as defined here:

| Data Key | Information |
| -- | -- |
| 10 | `[ + Delegation Record] / undefined` |
| 11 | Optional Time to live |
| 12 | Optional fund id |
| 13 | Optional purpose |

##### Delegation Record

Key 10 defines an array of Delegation records.

The formal structure of the Delegation Record is defined as:

```cddl
delegation_registration = [ + delegation_record ] / undefined

delegation_record = (
    simple_delegation /
    weighted_delegation
)

simple_delegation = drep_key_hash
weighted_delegation = [ drep_key_hash, weight ]

drep_key_hash = bytes .size 16
weight = uint
```

* `delegation_registration` is either an array of delegation_records OR `undefined`.
  `undefined` means that any previous delegation that was active is terminated.
  The voter retains their voting power in this case.
* An individual `delegation_record` can be either a `simple_delegation` or a `weighted_delegation`.
* `simple_delegation` is just the hash of the drep voting key to be delegated to.
  A weight of `1` is assumed if there are multiple delegations.
* `weighted_delegation` allows the weight to be defined, it is a positive integer.
  Weight apportions a voters voting power between all dReps delegated to.

Voting Power weighted apportionment is a function of the wights.
The total of the weights is added to give `total_weight`.
Each dRep get `voting power * (weight / total_weight)` worth of voting power from the delegation.
In the event there is any residual voting power, it is assigned to the final dRep in the list.

##### Optional Time To Live

This is a unit, and is the time expressed as seconds since 1970 UTC.
When this time is reached, the delegation is automatically cancelled, if it was not previously de-registered.

Time To Live can be used to remove a delegation at any time.
However, if the Delegation has been used to vote before the Time to Live expired, the voter may not ALSO Vote.

This allows the TTL to act as a safety.
For example, if the TTL is set to 10 days into a 15 day voting period,
then the dRep MUST vote within the first 10 days, after which they lose the delegation.
Having lost the delegation, the Voter may vote at any time in the final 5 days.
If however, the dRep voted in the first 10 days, the Voter may not vote in the last 5.
Even though they delegation expired.
That is because it is only valid to vote once on a proposal during a fund and the voter
already voted (via the valid, at the time, delegation).

##### Optional Fund ID

This is simply the ID of the fund.
It is a `uint`.
This defines the Fund for which the delegation is active.

##### Optional Delegation Purpose

This field can ONLY be defined if the `Fund ID` field is defined.

The Purpose defines what the delegation is for.
For example, in Catalyst it is defined as the number of the challenge or category in the fund the delegation is used for.
The delegation in this case is only valid for this Purpose on the specified Fund.

##### Multiple Delegations

It is possible for a Voter to have multiple simultaneous delegations.
In this case, the most specific delegation that has not expired is the one that is used.

For example, IF there is a delegation for Fund 15, Challenge 3, and no other delegations.
Then the voter can vote on every other challenge, except for Challenge 3 in that Fund.
Challenge 3 can be voted on by the dReps that were delegated.

In another example, if a voter has a general delegation, but also a specific delegation for Fund 15, Challenge 3.
Then the general delegations can vote on behalf of the voter for any fund/challenge
EXCEPT for Fund 15, Challenge 3.
For Fund 15, Challenge 3 ONLY the specific delegations for the Challenge/Fund may vote for the voter.

##### Validity

The Fund may impose rules on the construction of a delegation.
The delegation will not be valid if it does not conform to those rules.
For example, the Fund can define that ALL delegations Must expire 10 days within a 15 day voting window.
In which case, for a delegation to be valid, the TTL MUST be set appropriately.

This allows for great flexibility in how delegations work, but also allows fund specific rules to be created.
Without limiting the general usefulness of the registration format itself.

#### Proposer Registration

Registering as a proposer allows the registered entity to:

1. Create and Edit their own proposals both anonymously and publicly.
2. Jointly Edit proposals with other registered proposers.
3. Respond to comments on public proposals.
4. Sign a proposal either singly or jointly for submission and consideration in a Catalyst Fund.
5. Be paid to a certified payment address if the proposal wins.

Proposers MUST define a Proposers signature public key.
It must be a simple public key of the type ED25519, and it must reference the second signing key in the simple key array.

The proposer registration may OPTIONALLY define an encryption key.
Currently only X25519 encryption is supported, and this must be a reference to the second or third key in the simple key array.
IF the key is an ED25519 key, the X25519 public key is derived from it.
Otherwise if the key is an X25519 key, it is used as specified.

This allows the Propers signing key to also be used as a public encryption key.

A Proposer may ONLY work on private encrypted proposals if they have a published public encryption key.
The proposer may change their public encryption key at any time by posting an update to their registration.

Proposers MAY attach extra information to their registration:

| Data Key | Information |
| -- | -- |
| 10 | Name |
| 11 | [ + URL Link to Profile ] |
| 12 | ADA Handle |

If the proposers registration does not define a payment key,
the Role 0 payment key is used for the proposers payment key.

Because the purpose of a Proposer is to earn funding from the Catalyst Fund,
A proposal registration is INVALID if it does not have an associated payment address.

#### dApp purpose specific keys

Project Catalyst defines the following data which can be declared globally in any registration.

| Data Key | Information |
| -- | -- |
| 200 | Name |
| 201 | [ + URL Link to Profile ] |
| 202 | ADA Handle |

If any of these data items is defined in a registration,
they will be used if the matching key is absent in either a dRep or Proposer registration.

This allows for an individual that is both a dRep and a Proposer to share the same extended data about their registration.

### Project Catalyst Admin Role Registrations

| Role ID | Role Description |
| -- | -- |
| 0 | General Admin Role |

#### General Admin Role

Project Catalyst will register on-chain a registration for it's CA.
The CA will be associated with a known stake address.
The assignment of the CA to the known catalyst stake address establishes trust in the
Admin CA and ensures that other fraudulent CA's can not be registered.

The Admin CA can then issue other certificates for admins.
It may also revoke them.
It can also create a 2nd layer of CA's to create Admin users.

An example of the relationship between CA's and certificates is:

![Certificate Chain](./images/certificate-chain.svg)

The CA defined in this way, or the intermediate CA does not have any Admin privileges.

Only End Entity Certificates have Admin privileges.
Initially all registered project catalyst admins have all admin privileges in the system.

However, if required, an extension within the Role 0 certificate.
That is issued to theAdmin by the CA or intermediate CA.
Can define restrictions to the Admin role.
It is the responsibility of the CA to ensure the
permissions encoded in the admins Role 0 certificate are correct.

The CA or Intermediate CA may revoke an admins certificate at any time.
They do so by publishing the Admins certificate hash in a revocation list signed by the CA.

If an Admin user has their certificate revoked, they lose all Admin functionality.

This system allows a trusted and verifiable CA to register administrators and prevents fraudulent admins being registered.

Each Admin and CA must have a Stake Address associated with their registration certificate.

Admins are Role 0, so their signing key is defined by their certificate.
They may also register an Encryption key by referencing a key at index 0 of the simple key list.

The encryption key must be an X25519 public key if registered.

Admin users must NOT register a payment key, and they have no other data associated with their role registration.

### Special Roles not defined by x509 certificates

There is one special role within project catalyst which is not defined by the
Role registration.

An Unregistered Voter.

#### Unregistered Voter

Project Catalyst will have the concept of an UNREGISTERED voter.
A Voter may sign a vote with either their registered Voting Key, OR
They may sign it with their stake address.

As long as the stake address is valid, then anyone with a wallet can vote.
Even if they have not registered as a catalyst voter.

Alternatively a Voter who has a faulty registration or has lost their private voting
key may still vote in a fund with their Stake address signing their vote.
This acts as a fail safe in these cases.

Regardless of which key is used to sign the vote, a voter may ONLY vote once per fund per proposal.
All possible voting signature keys are considered equivalent.

Stake addresses may only be used for voting and can not be used for other functions assigned to Role 0.

## Rationale: how does this CIP achieve its goals?

## Path to Active

### Acceptance Criteria

### Implementation Plan

## Copyright

This CIP is licensed under [CC-BY-4.0]

Code samples and reference material are licensed under [Apache 2.0]

[CC-BY-4.0]: https://creativecommons.org/licenses/by/4.0/legalcode
[Apache 2.0]: https://www.apache.org/licenses/LICENSE-2.0.html
