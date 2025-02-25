---
CIP: /?
Title: Role based Access Control Registration
Category: MetaData
Status: Proposed
Authors:
    - Steven Johnson <steven.johnson@iohk.io>
    - Arissara Chotivichit <arissara.chotivichit@iohk.io>
Implementors: []
Discussions:
    - https://github.com/cardano-foundation/CIPs/pull/811
Created: 2023-10-24
License: CC-BY-4.0 / Apache 2.0
---

## Abstract

A dApp, such as Project Catalyst, needs robust, secure and extensible means for users to register under various roles
and for the dApp to be able to validate actions against those roles with its users.

While these Role-based registrations are required for future functionality of Project Catalyst, they are also
intended to be generally useful to any dApp with User roles.

## Motivation: why is this CIP necessary?

CIP-0036 contains a limited form of role registration limited to voter and dRep registrations.

However, Project Catalyst has a large (and growing) number of roles identified in the system, all of
which can benefit from on-chain registration.

A non-exhaustive example list of the roles Project Catalyst needs to identify securely are:

1. Proposers.
2. Co-Proposers.
3. Proposal Reviewers.
4. Voters.
5. Representative voters.
6. Tally committee members.
7. Administrators.
8. Audit committee members.

An individual dApp may have its own unique list of roles it wishes users to register for.
Roles are such that an individual user may hold multiple roles, one of the purposes of this
CIP is to allow the user to unambiguously assert they are acting in the capacity of a selected role.

CIP-0036 offers a "purpose" field, but offers no way to manage it, and offers no way to allow it to be used unambiguously.
The "purpose" field therefore is insufficient for the needs of identifying roles.

CIP-0036 also does not allow the voting key to be validated.
This makes it impossible to determine if the registration voting key is usable, and owned by the registering user, or has
been duplicated from another registration on-chain or is just a random number.

It also offers no way to identify the difference between a voter registering for themselves, and a voter registering to be a dRep.

These are some of the key reasons, CIP-0036 is insufficient for future Project Catalyst needs.

Registering for various roles and having role-specific keys is generally useful for any dApp.
While this CIP is motivated to solve problems with Project Catalyst, it is also intended to be generally applicable to other dApps.

There are a number of interactions with a user in a dApp like Catalyst which require authentication.
However, forcing all authentication through a wallet has several disadvantages.

* Wallets only are guaranteed to provide `signData` if they implement CIP-0030, and that only allows a single signature.
* There are multiple keys controlled by a wallet, and it is useful to ensure that all keys reflected are valid.
* It is equally important to ensure that registrations prove custody/ownership of certain on-chain identities,
  such as registered stake address or dRep registration.
* Metadata in a transaction is inaccessible to Plutus scripts.
* Wallets could present raw data to be signed to the user, and that makes the UX poor because the user would have difficulty
  knowing what they are signing.
* Wallets could be extended to recognize certain metadata and provide better UX, but that shifts dApp UX to every wallet.
* Putting on-chain keys in metadata can be redundant if those keys are already witnessed in the transaction.
* Some authentication needs to change with regularity, such as authentication tokens to a backend service,
  and this would require potentially excessive wallet interactions.
  This would lower UX quality and could impact participation.

The proposal here is to register dApp specific keys and identity, but strongly associate it with on-chain identity,
such as Stake Public Keys, Payment Keys and dRep Keys, such that off chain interactions can be fully authenticated,
and only on-chain interaction requires interaction with a Wallet.

## Specification

Role registration is encapsulated inside a [x509 Envelope] metadata record.
This enables the data to both be compressed and use broader [CBOR] encoding vs raw on-chain metadata.

This specification covers the general use of the x509 registration format and is not specific to any dApp.
dApps can utilize any subset of the features defined herein, and dApps define their own roles.

To maintain a robust set of role registration capabilities, Role registration involves:

1. Creation of a root certificate for a user or set of users and associating it with an on-chain source of trust.
2. Obtaining for each user of a dapp, or a set of users, their root certificate.
3. Deriving role specific keys from the root certificate.
4. Optionally registering for those roles on-chain.
5. Signing and/or encrypting data with the root certificate or a derived key, or a certificate issued by a previously
   registered root certificate.

Effectively we map the blockchain as PKI (Public Key Infrastructure) and define the methods a dapp can use to exploit this PKI.

### Mapping the PKI to Cardano

A PKI consists of:

* A certificate authority (CA) that stores, issues and signs the digital certificates;
  * Each dApp *MAY* control its own CA,  the user trusts the dApp as CA implicitly (or explicitly) by using the dApp.
  * It is also permissible for root certificates to be self signed, effectively each user becomes their own CA.
  * However all Certificates are associated with blockchain addresses, typically one or more Stake Public Key.
    * A certificate could be associated with multiple Stake Addresses, Payment Addresses, or DRep Public Keys, as required.
  * A dApp may require that a well known public CA is used.
  The chain of trust can extend off chain to centralized CAs.
  * DAOs or other organizations can also act as a CA for their members.
  * This is intentionally left open so that the requirements of the dApp can be flexibly accommodated.
* A registration authority (RA) which verifies the identity of entities requesting their digital certificates
  to be stored at the CA;
  * Each dApp is responsible for identifying certificates relevant for its use that are stored on-chain and are their own RA.
  * The dApp may choose not to do any identifying.
  * The dApp can rely on decentralized identity to verify identity in a trustless way.
* A central directory—i.e., a secure location in which keys are stored and indexed;
  * This is the blockchain itself.
  * As mentioned above, the chain of trust can extend off-chain to traditional Web2 CA's.
* A certificate management system managing things like the access to stored certificates or the delivery of the
  certificates to be issued;
  * This is managed by each dApp according to its requirements.
* A certificate policy stating the PKI's requirements concerning its procedures.
  Its purpose is to allow outsiders to analyze the PKI's trustworthiness.
  * This is also defined and managed by each dApp according to its requirements.

### The role x.509 plays in this scheme

We leverage the x.509 PKI primitives.
We intentionally take advantage of the significant existing code bases and infrastructure which already exists.

#### Certificate formats

X.509 certificates can be encoded in:

* Binary DER format
* [CBOR Encoded X.509 Certificates][C509].

### Metadata Structure

The formal definition of the x509 certificate payload is [here](./x509-roles.cddl).

The format can be visualized as:

![x509 Registration Format](./images/x509-roles.svg)

### Metadata Encoding

* The metadata will be encoded with [CBOR].
* The [CBOR] metadata will be encoded strictly according to [CBOR - Core Deterministic Encoding Requirements].
* There **MUST NOT** be any duplicate keys in a map.
* UTF-8 strings **MUST** be valid UTF-8.
* Tags **MUST NOT** be used unless specified in the specification.
* Any Tags defined in the specification are **REQUIRED**, and they **MUST** be present in the encoded data.
  * Fields which should be tagged, but which are not tagged will be considered invalid.

These validity checks apply only to the encoding and decoding of the metadata itself.
There are other validity requirements based on the role registration data itself.
Each dApp may have further validity requirements beyond those stated herein.

### High level overview of Role Registration metadata

At a high level, Role registration will collect the following data:

1. An [optional list](#x509-certificate-lists) of DER format X.509 certificates.
2. An [optional list](#x509-certificate-lists) of [CBOR Encoded X.509 Certificates][C509]
3. An [optional list](#simple-public-keys) list of tagged simple public keys.
4. An [optional certificate revocation](#certificate-revocation-list) set.
5. An [optional set](#role-definitions) of role registration data.
6. An [optional list](#dapp-specific-registration-data) of purpose specific data.

### X.509 Certificate Lists

There can be two lists of certificates.
1. X.509 Certificate
2. CBOR Encoded X.509 Certificate (C509)
Functionally, these two types are identical, differing only in their encoding format.

*DER Format certificates* are used when the only certificate source is a legacy off-chain certificate. 
While these are supported for legacy purposes, they are not preferred because:
- They can be converted (or "transcoded") into C509 format.
- They tend to be larger than their C509 equivalents.

Preferably all certificates will either be 
- Uniquely encoded as C509 encoded certificates, or
- Transcoded from a DER format X.509 certificate into its C509 equivalent.

The only feature about the certificate that impacts the role registration is that certificates
may embed references to on-chain keys.

In the case where a certificate does embed a reference to an on-chain key,
the key **SHOULD** be present in the witness set of the transaction.
Individual dApps can strengthen this requirement to **MUST**.

By including the Signature in the transaction, we are able to make a verifiable link between the
off-chain certificate and the on-chain identity. 
This process is secure and cannot be forged.

For more details on how certificates are stored, refer to the section on
[Storing Certificates and Public Key](#storing-certificates-and-public-key)

#### Plutus access to X.509 certificates

Plutus is currently incapable of reading any metadata attached to a transaction.
This specification allows for C509 encoded certificates to be present in the datum output of the transaction itself.
Any C509 certificates present in the metadatum of the transaction are considered to be part of the C509
certificate list for the purposes of this specification.

A C509 certificate in a metadatum that is to be included in the registration **MUST** be included in the C509 certificate list
as a reference.

The reference defines the metadatum the C509 certificate can be found in the transaction outputs,
and the offset in that metadatum is where the certificate is located.
The Certificates **MUST** be in the same transaction as the Metadatum, it is not possible to refer to a certificate
embedded in metadatum in another transaction.

Certificates in metadatum that are not linked in this way are ignored for the purpose of this specification.

Transaction outputs at key 1 of the transaction can contain any number of arrays of certificates.
This is only limited by the transaction itself.

### Simple Public Keys

Rather than require full certificates, dApps can use simple public keys.
The simple public key list is for that purpose.
The list acts as an array, the index in the array is the offset of the key.

The latest key set is what is currently active for the role.

These keys are usable to sign data for a role, but are not a replacement for certificates, and some roles may not allow their use.

For more details on how public keys are stored, refer to the section on
[Storing Certificates and Public Key](#storing-certificates-and-public-key)

### Certificate Revocation List

The certificate revocation list is used by an `issuer` of a certificate to revoke any certificate they have issued.
The certificate is considered revoked as soon as it appears in the revocation list.
If a self signed certificate is to be rolled, a registration will revoke the previously self signed certificate and
simultaneously register a new certificate.

This ensures that the roles registered always have a valid certificate and allows registration to be dynamically updated.

The revocation list is simply a list of blake2b-128 hashes of the certificate/s to be revoked.
Note, as stated above the only party that can revoke a certificate is the issuer, so the metadata must be posted by the issuer using
their own role 0 key.

Any certificate that is revoked which was used to issue other certificates results in ALL certificates issued by the
revoked certificate also being revoked.

### Role definitions

Roles are defined in a list.
A user can register for any available role, and they can enroll in more than one role in a single registration transaction.

The validity of the registration is as per the rules for roles defined by the dApp itself.

Role registration data is further divided into:

1. [A Role number](#role-number)
2. An [Optional reference](#reference-to-a-role-signing-key) to the roles signing key
3. An [Optional reference](#reference-to-a-role-encryption-key) to the roles encryption key
4. An [Optional reference](#on-chain-payment-key-reference) to the on-chain payment key to use for the role.
5. And an [Optional](#role-extended-data-keys) dApp defined set of role specific data.

#### Role Number

All roles, except for Role 0, are defined by the dApp.

Role 0 is the primary role and is used to sign the metadata and declare on-chain/off-chain identity linkage.
All compliant implementations of this specification use Role 0 in this way.

dApps can extend what other use cases Role 0 has, but it will always be used to secure the Role registrations.

For example, in Catalyst Role 0 is a basic voters role.
Voters do not need to register for any other role to have basic interaction with project Catalyst.

The recommendation is that Role 0 be used by dApps to give the minimum level of access the dApp requires and
other extended roles are defined as Role 1+.

#### Reference to a role signing key

Each role can optionally be used to sign data.
If the role is intended to sign data, the key it uses to sign **MUST** be declared in this field.
This is a reference to either a registered certificate for the identity posting the registration,
or one of the defined simple public keys.

A dApp can define is roles allow the use of certificates, or simple public keys, or both.

A reference to a key/certificate can be a cert in the same registration, or any previous registration.
If the certificate is revoked, the role is unusable for signing unless and until a new signing certificate
is registered for the role.

#### Reference to a role encryption key

A Role may require the ability to transfer encrypted data.
In this case, the registration can include the public key used by the role to encrypt the roles data.

Public key encryption works with a pair of keys: a public key (which is shared and can be used by anyone) and a private key (which is kept secret by the owner). The public key can only be used to encrypt data that can then only be decrypted by the holder of the corresponding private key.

When two users have their public keys registered, they can use these keys off-chain to securely exchange information, such as performing a key exchange or encrypting messages that can only be read by the holder of the private key.

The Role encryption key must be a reference to a key that supports public key encryption, and not just a signing key.
If the key referenced does not support public key encryption, the registration is invalid.

#### On-chain payment key reference

Some dApps may require a user to register their payment key, so that rewards (native tokens or NFT's)
can be sent or for other use cases.

Registrations like CIP-0015/CIP-0036 for catalyst include a payment key.
However, a fundamental problem with these metadata standards is there is no way to validate:

1. The payment key declared is valid and capable of receiving payments.
2. That the entity posting the registration actually owns the payment key registered.

It is important that payment keys be verifiable and provably owned to the registrar.

A Payment key reference in this CIP solves this problem by only allowing a reference to transaction output.

The reference is a simple unsigned integer.
The integer represent the index of the transaction outputs.
For example, integer 0 refers to index 0 of the transaction outputs.

For the payment key to be validated, it must be witnessed in the transaction, this can be achieved by either:
* Using the same payment key from an input to the transaction as an output.
* If the payment key is not an input to the transaction, including it in the Required Signers field of the transaction.
Payment keys which are not witnessed are invalid, as they can not be proven to both be:
* Owned and controlled by the wallet signing the transaction and posting the registration.
* Spendable.
Ensuring this validity reduces the risk of invalid payments, or paying the wrong individuals, and eliminates the need to make "trial" payments to validate an address is payable.

If the transaction output address **IS** also an input to the transaction,
then the same proof has already been attached to the transaction.

However, if the transaction output is not also an input, the transaction **MUST** include the output address
in the required signers field, and the transaction must carry a witness proving the payment key is owned.

This provides guarantees that the entity posting the registration has posted a valid payment address, and that they control it.

If a payment address is not able to be validated, then the entire registration metadata is invalid.

#### Role extended data keys

Each dApp can declare that roles can have either mandatory or optional data items that can be posted with any role registration.

Each role can have a different set of defined role registration data.
It is not required that all roles have the same data.

As the role data is dApp specific, it is not detailed here.
Each dApp will need to produce a specification of what role specific data it requires, and how it is validated.

### dApp specific registration data

Each dApp can define data which is required for registration to the dApp.
This data can be defined as required or optional by the dApp.

The data is global and applies to all roles registered by the same identity.

This can include information such as ADA Handles, or reputation data associated with a registration.

As this data is dApp specific it is not detailed here.

### Storing certificates and public key
X.509 certificates, C509 certificates, and public keys are stored in an array. This array follows specific rules for managing changes and updates to the items it contains.

CBOR allows elements of an array to be skipped or marked as absent using [CBOR Undefined/Absent Tags].
- Undefined (`0xf7`): This tag indicates that no change should be made to the corresponding element in the array.
- Absent (`0xd8 0x1f 0xf7`): This tag is used to mark an element as removed, meaning that any key at that position is considered removed.

Examples:

```txt
[Key 1, Key 2, Key 3] +
[undefined, absent, undefined]
```

would result in:

```txt
[Key 1, undefined, Key 3]
```
Here, Key 2 has been removed (marked as `absent`), and Key 1 and Key 3 remain unchanged (the `undefined` entries indicate no modification to these positions).

If this was followed with:

```txt
[undefined, undefined, undefined, undefined, Key 5]
```

we would then have the resultant set of keys:

```txt
[Key 1, undefined, Key 3, undefined, Key 5]
```
In this case, the new Key 5 has been added to the array, and the previous keys remain intact with `undefined` markers indicating no change.

**Notes**
For certificates, marking it as absent does not mark the certificate as invalid, but it means the certificate
is not listed in the current list anymore. To revoke the certificate, it must be listed in 
[certificate-revocation-list](#certificate-revocation-list)

### Registration validity

Any registration metadata must be 100% valid, or the entire registration data set is rejected as invalid.

For example, given three roles were registered, Role 0, 1, and 2.
Role 0 is perfectly fine, as is Role 1.
However Role 2 has an error with the payment key.
None of the role registrations will take effect.

#### Role 0 Specific requirements

1. Certificate Index 0 Reserved for Role 0:
- Index 0 in both the X.509 certificate list and the C509 certificate list is reserved for Role 0.
- When registration made, either of the X.509 certificate list or C509 certificate list **MUST** contains certificate in index 0 (but not both).
- This means for other roles, if certificate is needed, index 0 in these lists **MUST** be set to `undefined`.

2. Updating Role 0 Certificate:
- Any updates to the certificate associated with Role 0 require a new Role 0 registration to be posted.
- The updated registration **MUST** reference the correct certificate.
- No other role is permitted to modify the certificate or certificate index for Role 0.

3. C509 Certificate Reference:
- Role 0 **MUST NOT** reference a C509 certificate in Metadatum.   
  
4. Signing Key for Role 0:
- Role 0 **MUST** have a signing key set to 0 (since 0 refers to the reserved index 0 of the certificate).
- The certificate **MUST** include a reference to the on-chain identity(ies) that are bound to the registration.
- The signing key **MUST** be a certificate, not a simple public key.

5. Simple Public Keys for Role 0:
- Simple Public Keys **MUST NOT** be set.
- In case for other roles, if simple public key is needed, index 0 in this list **MUST** be set to `undefined`
  
6. Encryption Key Reference for Role 0:
- Role 0 **MUST NOT** contain any reference to an encryption key.

### Optional fields

As role registration is cumulative and each new registration for an entity on a dApp simply updates a previous
registration, then all fields are optional.

The individual posting the registration **ONLY** needs to post the data that has changed or is being added.
This is intended to minimize the amount of on-chain data.
It does mean that a registration state can only be known by collecting all registration for an individual from the chain.

### First Registration

The very first registration must have the following features:

1. It **MUST** have a certificate that is appropriately issued (either self signed or issued by a trusted CA).
   1. The certificate requirement is defined by each dApp.
   2. The certificate **MUST** link to at least 1 on-chain identity.
      dApps define what the required identities are.
      It is valid for a dApp to require multiple on-chain identities to be referenced.
      However, general validity can be inferred by the presence or lack of a referenced on-chain identity.
      1. Either currently a Stake Address; or
      2. Another on-chain identity key (such as dRep).
   3. The transaction **MUST** be witnessed by **ALL** the Role 0 referenced on-chain identities.
      1. If the address is not a natural address to witness the transaction, it **MUST** be included in the
          required signers field of the transaction.
          And it **MUST** appear in the witness set.
2. It **MUST** have a Role 0 defined, that references the certificate.
3. It **MUST** be signed by the Role 0 certificate.

Once the Role 0 certificate is registered, the entity is registered for the dApp.
Provided the dApp will accept the individuals registration.

Other certificates **DO NOT** need to have references to the on-chain identity of the user.
However, if they do, they **MUST** be witnessed in the transaction to prove they are validly held and referenced.

### De-registering

Once a user has registered for Role 0, the only way they can de-register is to revoke their Role 0 key.
If the Role 0 key is revoked, and is not replaced in the same transaction with a new key, then all
registration data for that user is revoked.

A user could then create a new registration with a new Role 0 certificate,
but they would also need to register for any Roles again.

This is because if the Role 0 certificate is not immediately rolled over, then all role registrations are deemed terminated.

It is also possible for a de-registration to cause a linked registration to use a new on-chain identity.

For example, if the current Role 0 registration referenced Stake address 123,
and a new registration is posted that revokes the old cert, and posts a new cert referencing Stake address 456,
then the on-chain stake address identity will have changed from 123 to 456.

Note: in the case of a CA revoked certificate,
the subject must have registered a new Role 0 certificate before the issuer revokes it.

Otherwise, they will become de-registered when the issuer revokes their certificate, and they must then completely re-register.

## Rationale: how does this CIP achieve its goals?

To-do.

## Path to Active

* All related CIP's are implemented in a MVP implementation for Project Catalyst.
* All implementation details have been refined allowing unambiguous implementation for the MVP.
* Appropriate community driven feedback has occurred to allow the specification to mature.

### Acceptance Criteria

To-do.

### Implementation Plan

To-do.

## References

* [CC-BY-4.0]
* [Apache 2.0]
* [CBOR]
* [CBOR - Core Deterministic Encoding Requirements]
* [C509]
* [CBOR Undefined/Absent Tags]

## Copyright

This CIP is licensed under [CC-BY-4.0]

Code samples and reference material are licensed under [Apache 2.0]

[CC-BY-4.0]: https://creativecommons.org/licenses/by/4.0/legalcode
[Apache 2.0]: https://www.apache.org/licenses/LICENSE-2.0.html
[CBOR]: https://www.rfc-editor.org/rfc/rfc8949.html
[CBOR - Core Deterministic Encoding Requirements]: https://www.rfc-editor.org/rfc/rfc8949.html#section-4.2.1
[C509]: https://datatracker.ietf.org/doc/html/draft-ietf-cose-cbor-encoded-cert-07
[CBOR Undefined/Absent Tags]: https://github.com/svaarala/cbor-specs/blob/master/cbor-absent-tag.rst
[X509 Envelope]: https://not.yet.defined
