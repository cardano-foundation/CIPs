---
CIP: 105
Title: Conway era Key Chains for HD Wallets
Status: Active
Category: Wallets
Authors:
  - Ryan Williams <ryan.williams@intersectmbo.org>
Implementors:
  - Eternl <https://eternl.io/>
  - Lace <https://www.lace.io/>
  - Mesh <https://meshjs.dev/>
  - NuFi <https://nu.fi/>
  - Ryan Williams <ryan.williams@intersectmbo.org>
  - Pawel Jakubas <pawel.jakubas-ext@cardanofoundation.org>
  - Typhon <https://typhonwallet.io/>
  - Vespr <https://vespr.xyz/>
  - Yoroi <https://yoroi-wallet.com/>
  - Gero <https://gerowallet.io/>
Discussions:
  - https://github.com/cardano-foundation/cips/pulls/597
Created: 2023-09-22
License: CC-BY-4.0
---

## Abstract

The Conway Ledger era introduces many new features to Cardano, notably features to support community governance via CIP-1694.
This includes the introduction of the new first class credentials; `drep_credential`, `committee_cold_credential` and `committee_hot_credential`.

We propose a HD wallet key derivation paths for registered DReps and constitutional committee members to deterministically derive keys from which credentials can be generated.
Such keys are to be known as DRep keys, constitutional committee cold keys and constitutional committee hot keys.
Here we define some accompanying tooling standards.

> **Note** this proposal assumes knowledge of the Conway ledger design (see
> [draft ledger specification](https://github.com/IntersectMBO/cardano-ledger/blob/d2d37f706b93ae9c63bff0ff3825d349d0bd15df/eras/conway/impl/cddl-files/conway.cddl))
> and
> [CIP-1694](https://github.com/cardano-foundation/CIPs/blob/master/CIP-1694/README.md).

## Motivation: why is this CIP necessary?

In the Conway ledger era, DRep credentials allow registered DReps to be identified on-chain, in DRep registrations, retirements, votes, and in vote delegations from ada holders.
Whilst constitutional committee members can be recognized by their cold credentials within update committee governance actions, authorize hot credential certificate and resign cold key certificates.
Constitutional committee hot credential can be observed within the authorize hot key certificate and votes.

CIP-1694 terms these DRep credentials as DRep IDs, which are either generated from blake2b-224 hash digests of Ed25519 public keys owned by the DRep, or are script hash-based.
Similarly, both the hot and cold credentials for constitutional committee members can be generated from public key digests or script hashes.

This CIP defines a standard way for wallets to derive DRep and constitutional committee keys.

Since it is best practice to use a single cryptographic key for a single purpose, we opt to keep DRep and committee keys separate from other keys in Cardano.

By adding three paths to the [CIP-1852 | HD (Hierarchy for Deterministic) Wallets for Cardano](https://github.com/cardano-foundation/CIPs/blob/master/CIP-1852/README.md), we create an ecosystem standard for wallets to be able to derive DRep and constitutional committee keys.
This enables DRep and constitutional committee credential restorability from a wallet seed phrase.

Stakeholders for this proposal are wallets that follow the CIP-1852 standard and tool makers wishing to support DReps and or constitutional committee members.
This standard allows DReps and constitutional committee members to use alternative wallets whilst being able to be correctly identified.
By defining tooling standards, we enable greater interoperability between governance-focussed tools.

## Specification

### Derivation

#### DRep Keys

Here we describe DRep key derivation as it pertains to Cardano wallets that follow the CIP-1852 standard.

To differentiate DRep keys from other Cardano keys, we define a new `role` index of `3`:

`m / 1852' / 1815' / account' / 3 / address_index`

We strongly recommend that a maximum of one set of DRep keys should be associated with one wallet account, which can be achieved by setting `address_index=0`.

#### DRep ID

Tools and wallets can generate a DRep ID (`drep_credential`) from the Ed25519 public DRep key (without chaincode) by creating a blake2b-224 hash digest of the key.
As this is key-based credential it should be marked as entry `0` in a credential array. DRep Identifier is further specified in [CIP-0129](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0129/README.md).

#### Constitutional Committee Cold Keys

Here we describe constitutional committee cold key derivation as it pertains to Cardano wallets that follow the CIP-1852 standard.

To differentiate constitutional committee cold keys from other Cardano keys, we define a new `role` index of `4`:

`m / 1852' / 1815' / account' / 4 / address_index`

We strongly recommend that a maximum of one set of constitutional committee cold keys should be associated with one wallet account, which can be achieved by setting `address_index=0`.

#### Constitutional Committee Cold Credential

Tools and wallets can generate a constitutional committee cold credential (`committee_cold_credential`) from the Ed25519 public constitutional committee cold key (without chaincode) by creating a blake2b-224 hash digest of the key.
As this is key-based credential it should be marked as entry `0` in a credential array.

#### Constitutional Committee Hot Keys

Here we describe constitutional committee hot key derivation as it pertains to Cardano wallets that follow the CIP-1852 standard.

To differentiate constitutional committee hot keys from other Cardano keys, we define a new `role` index of `5`:

`m / 1852' / 1815' / account' / 5 / address_index`

We strongly recommend that a maximum of one set of constitutional committee hot keys should be associated with one wallet account, which can be achieved by setting `address_index=0`.

#### Constitutional Committee Hot Credential

Tools and wallets can generate a constitutional committee hot credential (`committee_hot_credential`) from the Ed25519 public constitutional committee hot key (without chaincode) by creating a blake2b-224 hash digest of the key.
As this is key-based credential it should be marked as entry `0` in a credential array.

### Bech32 Encoding

These are also described in [CIP-0005 | Common Bech32 Prefixes](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0005/README.md), but we include them here for completeness.

> **Note** we also include the prefixes for script-based credentials in the following subsections, for completeness.

#### DRep Keys

DRep keys and DRep IDs should be encoded in Bech32 with the following prefixes:

| Prefix        | Meaning                                                 | Contents                                                           |
| ------------- | --------------------------------------------------------| ------------------------------------------------------------------ |
| `drep_sk`     | CIP-1852’s DRep signing key                             | Ed25519 private key                                                |
| `drep_vk`     | CIP-1852’s DRep verification key                        | Ed25519 public key                                                 |
| `drep_xsk`    | CIP-1852’s DRep extended signing key                    | Ed25519-bip32 extended private key                                 |
| `drep_xvk`    | CIP-1852’s DRep extended verification key               | Ed25519 public key with chain code                                 |
| `drep`        | [DEPRECATED] DRep verification key hash (DRep ID)       | blake2b\_224 digest of a delegate representative verification key  |
| `drep_vkh`    | Delegate representative verification key hash           | blake2b\_224 digest of a delegate representative verification key  |
| `drep_script` | Delegate representative script hash                     | blake2b\_224 digest of a serialized delegate representative script |

#### Constitutional Committee Cold Keys

Constitutional cold keys and credential should be encoded in Bech32 with the following prefixes:

| Prefix           | Meaning                                                               | Contents                                                               |
| ---------------- | --------------------------------------------------------------------- | ---------------------------------------------------------------------  |
| `cc_cold_sk`     | CIP-1852’s constitutional committee cold signing key                  | Ed25519 private key                                                    |
| `cc_cold_vk`     | CIP-1852’s constitutional committee verification signing key          | Ed25519 private key                                                    |
| `cc_cold_xsk`    | CIP-1852’s constitutional committee cold extended signing key         | Ed25519-bip32 extended private key                                     |
| `cc_cold_xvk`    | CIP-1852’s constitutional committee extended verification signing key | Ed25519 public key with chain code                                     |
| `cc_cold`        | [DEPRECATED] Constitutional committee cold verification key hash (cold credential) | blake2b\_224 digest of a consitutional committee cold verification key |
| `cc_cold_vkh`    | Constitutional committee cold verification key hash (cold credential) | blake2b\_224 digest of a consitutional committee cold verification key |
| `cc_cold_script` | Constitutional committee cold script hash (cold credential)           | blake2b\_224 digest of a serialized constitutional committee cold script |

#### Constitutional Committee Hot Keys

Constitutional hot keys and credential should be encoded in Bech32 with the following prefixes:

| Prefix          | Meaning                                                               | Contents                                                              |
| --------------- | --------------------------------------------------------------------- | --------------------------------------------------------------------- |
| `cc_hot_sk`     | CIP-1852’s constitutional committee hot signing key                   | Ed25519 private key                                                   |
| `cc_hot_vk`     | CIP-1852’s constitutional committee verification signing key          | Ed25519 private key                                                   |
| `cc_hot_xsk`    | CIP-1852’s constitutional committee hot extended signing key          | Ed25519-bip32 extended private key                                    |
| `cc_hot_xvk`    | CIP-1852’s constitutional committee extended verification signing key | Ed25519 public key with chain code                                    |
| `cc_hot`        | [DEPRECATED] Constitutional committee hot verification key hash (hot credential) | blake2b\_224 digest of a consitutional committee hot verification key |
| `cc_hot_vkh`    | Constitutional committee hot verification key hash (hot credential)   | blake2b\_224 digest of a consitutional committee hot verification key |
| `cc_hot_script` | Constitutional committee hot script hash (hot credential)             | blake2b\_224 digest of a serialized constitutional committee hot script |

### Tooling Definitions

#### DRep Keys

Supporting tooling should clearly label these key pairs as "DRep Keys".

Examples of acceptable `keyType`s for supporting tools:

| `keyType`                                   | Description                                       |
| ------------------------------------------- | ------------------------------------------------- |
| `DRepSigningKey_ed25519`                    | Delegate Representative Signing Key               |
| `DRepExtendedSigningKey_ed25519_bip32`      | Delegate Representative Extended Signing Key      |
| `DRepVerificationKey_ed25519`               | Delegate Representative Verification Key          |
| `DRepExtendedVerificationKey_ed25519_bip32` | Delegate Representative Extended Verification Key |

For hardware implementations:

| `keyType`                     | Description                                       |
| ----------------------------- | ------------------------------------------------- |
| `DRepHWSigningFile_ed25519`   | Hardware Delegate Representative Signing File     |
| `DRepVerificationKey_ed25519` | Hardware Delegate Representative Verification Key |

#### Constitutional Committee Cold Keys

Supporting tooling should clearly label these key pairs as "Constitutional Committee Cold Keys".

Examples of acceptable `keyType`s for supporting tools:

| `keyType`                                                          | Description                                             |
| ------------------------------------------------------------------ | ------------------------------------------------------- |
| `ConstitutionalCommitteeColdSigningKey_ed25519`                    | Constitutional Committee Cold Signing Key               |
| `ConstitutionalCommitteeColdExtendedSigningKey_ed25519_bip32`      | Constitutional Committee Cold Extended Signing Key      |
| `ConstitutionalCommitteeColdVerificationKey_ed25519`               | Constitutional Committee Cold Verification Key          |
| `ConstitutionalCommitteeColdExtendedVerificationKey_ed25519_bip32` | Constitutional Committee Cold Extended Verification Key |

For hardware implementations:

| `keyType`                                            | Description                                             |
| ---------------------------------------------------- | ------------------------------------------------------- |
| `ConstitutionalCommitteeColdHWSigningFile_ed25519`   | Hardware Constitutional Committee Cold Signing File     |
| `ConstitutionalCommitteeColdVerificationKey_ed25519` | Hardware Constitutional Committee Cold Verification Key |

#### Constitutional Committee Hot Keys

Supporting tooling should clearly label these key pairs as "Constitutional Committee Hot Keys".

| `keyType`                                                         | Description                                            |
| ----------------------------------------------------------------- | ------------------------------------------------------ |
| `ConstitutionalCommitteeHotSigningKey_ed25519`                    | Constitutional Committee Hot Signing Key               |
| `ConstitutionalCommitteeHotExtendedSigningKey_ed25519_bip32`      | Constitutional Committee Hot Extended Signing Key      |
| `ConstitutionalCommitteeHotVerificationKey_ed25519`               | Constitutional Committee Hot Verification Key          |
| `ConstitutionalCommitteeHotExtendedVerificationKey_ed25519_bip32` | Constitutional Committee Hot Extended Verification Key |

For hardware implementations:

| `keyType`                                           | Description                                            |
| --------------------------------------------------- | ------------------------------------------------------ |
| `ConstitutionalCommitteeHotHWSigningFile_ed25519`   | Hardware Constitutional Committee Hot Signing File     |
| `ConstitutionalCommitteeHotVerificationKey_ed25519` | Hardware Constitutional Committee Hot Verification Key |

### Deprecated Governance ID Definition
The previous governance key IDs defined by this standard have been superseded by the definitions provided in [CIP-0129]. Tools implementing this standard are encouraged to consider adopting [CIP-0129]. Tools that already support [CIP-0129] maintain backward compatibility with the legacy formats specified below but should consider fully transitioning to [CIP-0129] to standardize key formats across the ecosystem. This will help avoid multiple formats and ensure consistency.

This CIP previously also lacked `_vkh` key definitions, which are now added above possible due to the upgrades defined in [CIP-0129]. For detailed information on the new specification and the rationale behind the upgrade, please refer to [CIP-0129].

#### DRep Keys

| Prefix          | Meaning                                                               | Contents                                                              |
| --------------- | --------------------------------------------------------------------- | --------------------------------------------------------------------- |
| `drep`        | Delegate representative verification key hash (DRep ID) | blake2b\_224 digest of a delegate representative verification key  |
| `drep_script` | Delegate representative script hash (DRep ID)           | blake2b\_224 digest of a serialized delegate representative script |

#### Constitutional Committee Cold Keys

| Prefix          | Meaning                                                               | Contents                                                              |
| --------------- | --------------------------------------------------------------------- | --------------------------------------------------------------------- |
| `cc_cold`        | Constitutional committee cold verification key hash (cold credential) | blake2b\_224 digest of a consitutional committee cold verification key   |
| `cc_cold_script` | Constitutional committee cold script hash (cold credential)           | blake2b\_224 digest of a serialized constitutional committee cold script |

#### Constitutional Committee Hot Keys

| Prefix          | Meaning                                                               | Contents                                                              |
| --------------- | --------------------------------------------------------------------- | --------------------------------------------------------------------- |
| `cc_hot`        | Constitutional committee hot verification key hash (hot credential) | blake2b\_224 digest of a consitutional committee hot verification key   |
| `cc_hot_script` | Constitutional committee hot script hash (hot credential)           | blake2b\_224 digest of a serialized constitutional committee hot script |

### Versioning

This CIP is not to be versioned using a traditional scheme, rather if any large technical changes are required then a new proposal must replace this one.
Small changes can be made if they are completely backwards compatible with implementations, but this should be avoided.

## Rationale: how does this CIP achieve its goals?

### Derivation

By standardizing derivation, naming, and tooling conventions we primarily aim to enable wallet interoperability.
By having a standard to generate DRep and constitutional committee credentials from mnemonics, we allow wallets to always be able to discover a user’s governance activities.

#### Why add a new roles to the 1852 path?

This approach mirrors how stake keys were rolled out, see [CIP-0011 | Staking key chain for HD wallets](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0011/README.md).
We deem this necessary since these credentials sit alongside each other in the Conway ledger design.

The alternative would be to define a completely different derivation paths, using a different index in the purpose field, similar to the specification outlined within [CIP-0036](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0036/README.md#derivation-path), but this could introduce complications with HW wallet implementations.

#### Why not multi-DRep/CC wallet accounts?

We believe the overhead that would be introduced by multi-DRep accounts or multi-constitutional-committee is an unjustified expense.
Future iterations of this specification may expand on this, but at present this is seen as unnecessary.
This avoids the need for DRep, cc hot or cc cold key discovery.

We model this on how stake keys are generally handled by wallets.
If required, another CIP could, of course, introduce a multi-DRep/CC method.

### Encoding

#### Why not allow network tags?

For simplicity, we have omitted network tags within the encoding.
This is because we have modeled DRep IDs and CC credentials on stake pool operator IDs, which similarly do not include a network tag.

The advantage of including a network tag would be to reduce the likelihood of mislabelling a DRep’s network of operation (eg Preview v Cardano mainnet).

### Test vectors

See [Test Vectors File](./test-vectors.md).

## Path to Active

### Acceptance Criteria

- [x] The DRep derivation path is used by three wallet/tooling implementations.
  - [Nufi](https://assets.nu.fi/extension/sanchonet/nufi-cwe-sanchonet-latest.zip)
  - [Lace](https://chromewebstore.google.com/detail/lace-sanchonet/djcdfchkaijggdjokfomholkalbffgil?hl=en)
  - [Yoroi](https://chrome.google.com/webstore/detail/yoroi-nightly/poonlenmfdfbjfeeballhiibknlknepo/related)
  - [demos wallet](https://github.com/Ryun1/cip95-demos-wallet)
- [x] The constitutional committee derivation paths are used by two implementations.
  - [csl-examples](https://github.com/Ryun1/csl-examples/)
  - [cardano-addresses](https://github.com/IntersectMBO/cardano-addresses/)

### Implementation Plan

- [x] Author to provide an example implementation inside a HD wallet.
  - [csl-examples/cip-1852-keys.js](https://github.com/Ryun1/csl-examples/blob/main/examples/CIP-1852/cip-1852-keys.js)

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).

[CIP-0129]: (https://github.com/cardano-foundation/CIPs/blob/master/CIP-0129/README.md)
[DEPRECATED]: #deprecated-governance-id-definition
