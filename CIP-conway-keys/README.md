---
CIP: ?
Title: Conway Era Key Chains for HD Wallets
Status: Proposed
Authors:
  - Ryan Williams <ryan.williams@iohk.io>
Implementors: []
Discussions:
    - https://github.com/cardano-foundation/cips/pulls/?
Created: 2023-09-22
License: CC-BY-4.0
---

## Abstract

The Conway Ledger era introduces many new features to Cardano, notably features
to support community governance via CIP-1694. This includes the introduction of
a new first class credential; `drep_credential`.

We propose a HD wallet key derivation path for registered DReps to
deterministically derive keys from which DRep credentials can be generated. Such
keys are to be known as DRep keys, and here we define some accompanying tooling
standards.

> **Note** this proposal assumes knowledge of the Conway ledger design (see
> [draft](https://github.com/input-output-hk/cardano-ledger/tree/master/eras/conway/test-suite/cddl-files))
> and
> [CIP-1694](https://github.com/cardano-foundation/CIPs/blob/master/CIP-1694/README.md).

## Motivation: why is this CIP necessary?

In the Conway ledger era, DRep credentials allow registered DReps to be
identified on-chain, in DRep registrations, retirements, votes, and also in vote
delegations from normal ada holders.

CIP-1694 terms these credentials as DRep IDs, which are either generated from
blake2b-224 hash digests of Ed25519 public keys owned by the DRep, are script
ids, or are pre-defined (Abstain/No Confidence, used for voting purposes only).

This CIP defines a standard way for wallets to derive DRep keys.

Since it is best practice to use a single cryptographic key for a single
purpose, we opt to keep DRep keys separate from other keys in Cardano.

By adding a path to the
[CIP-1852 | HD (Hierarchy for Deterministic) Wallets for Cardano](https://github.com/cardano-foundation/CIPs/blob/master/CIP-1852/README.md),
we create an ecosystem standard for wallets to be able to derive DRep Keys. This
enables DRep credential restorability from a wallet seed phrase.

Stakeholders for this proposal are wallets that follow the CIP-1852 standard and
tool makers wishing to support DReps. This standard allows DReps to use
alternative wallets whilst being able to be correctly identified. By defining
tooling standards, we enable greater interoperability between
governance-focussed tools.

## Specification

### Derivation

Here we describe DRep Key derivation as it pertains to Cardano wallets that
follow the CIP-1852 standard.

To differentiate DRep keys from other Cardano keys, we define a new `role` index
of `3`:

`m / 1852' / 1815' / account' / 3 / address_index`

We strongly recommend that a maximum of one set of DRep keys should be
associated with one wallet account, which can be achieved by setting
`address_index=0`.

### DRep ID

Tools and wallets can generate a DRep ID (`drep_credential`) from the Ed25519
public DRep key (without chaincode) by creating a Blake2b_224 hash digest of the
key.

### Bech32 Encodings

DRep Keys and DRep IDs should be encoded in Bech32 with the following prefixes:

| Prefix     | Meaning                                   | Contents                           |
| ---------- | ----------------------------------------- | ---------------------------------- |
| `drep_sk`  | CIP-1852’s DRep signing key               | Ed25519 private key                |
| `drep_vk`  | CIP-1852’s DRep verification key          | Ed25519 public key                 |
| `drep_xsk` | CIP-1852’s DRep extended signing key      | Ed25519-bip32 extended private key |
| `drep_xvk` | CIP-1852’s DRep extended verification key | Ed25519 public key with chain code |
| `drep`     | DRep credential                           | DRep credential                    |

These are also described in
[CIP-0005 | Common Bech32 Prefixes](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0005/README.md),
but we include them here for completeness.

### Tooling Definitions

Supporting tooling should clearly label these key pairs as "DRep Keys".

Examples of acceptable `keyType`s for supporting tools:

| `keyType`                                   | Description                    |
| ------------------------------------------- | ------------------------------ |
| `DRepSigningKey_ed25519`                    | DRep Signing Key               |
| `DRepExtendedSigningKey_ed25519_bip32`      | DRep ExtendedSigning Key       |
| `DRepVerificationKey_ed25519`               | DRep Verification Key          |
| `DRepExtendedVerificationKey_ed25519_bip32` | DRep Extended Verification Key |

For hardware implementations:

| `keyType`                     | Description                    |
| ----------------------------- | ------------------------------ |
| `DRepHWSigningFile_ed25519`   | Hardware DRep Signing File     |
| `DRepVerificationKey_ed25519` | Hardware DRep Verification Key |

## Rationale: how does this CIP achieve its goals?

### Derivation

By standardizing derivation, naming, and tooling conventions we primarily aim to
enable wallet interoperability. By having a standard to generate DRep
credentials from mnemonics, we allow wallets to always be able to discover a
user’s governance activities.

#### Why add a new role to the 1852 path?

This approach mirrors how stake keys were rolled out, see
[CIP-0011 | Staking key chain for HD wallets](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0011/README.md).
We deem this necessary since these credentials sit alongside each other in the
Conway ledger design.

The alternative would be to define a completely different derivation path, using
a different index in the purpose field, similar to the specification outlined
within
[CIP-0036](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0036/README.md#derivation-path),
but this could introduce complications with HW wallet implementations.

#### Why not multi-DRep wallet accounts?

We believe the overhead that would be introduced by multi-DRep accounts is an
unjustified expense. Future iterations of this specification may expand on this,
but at present this is seen as unnecessary. This avoids the need for DRep Key
discovery.

We model this on how stake keys are generally handled by wallets. If required,
another CIP could, of course, introduce a multi-DRep method.

### Encoding

#### Why not allow network tags?

For simplicity, we have omitted network tags within the encoding. This is
because we have modeled DRep IDs on stake pool operator IDs, which similarly do
not include a network tag. The advantage of including a network tag would be to
reduce the likelihood of mislabelling a DRep’s network of operation (eg Preview
v Cardano mainnet).

## Path to Active

### Acceptance Criteria

- [ ] The derivation path is used by three wallet implementers (software and/or
      hardware).
- [ ] The tooling definitions are used across at least two tools.

### Implementation Plan

- [ ] Author to provide an example implementation inside a HD wallet.

## Copyright

This CIP is licensed under
[CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
