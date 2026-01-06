---
CIP: 16
Title: Cryptographic Key Serialisation Formats
Status: Active
Category: Tools
Authors:
  - Luke Nadur <luke.nadur@iohk.io>
Implementors:
  - jcli <https://github.com/input-output-hk/catalyst-core/tree/main/src/jormungandr/jcli>
  - cardano-signer <https://github.com/gitmachtl/cardano-signer>
  - cardano-serialization-lib <https://github.com/Emurgo/cardano-serialization-lib>
Discussions:
  - https://github.com/cardano-foundation/CIPs/pull/57
Created: 2020-12-21
License: Apache-2.0
---

## Abstract

This CIP defines serialisation formats for the following types of
cryptographic keys across the Cardano eco-system:

- Regular Ed25519 keys

- [BIP32-Ed25519](https://ieeexplore.ieee.org/document/7966967) extended keys
  (Ed25519 extended keys with BIP32-style derivation)

## Motivation: Why is this CIP necessary?

Throughout the Cardano eco-system, different projects have used different
serialisation formats for cryptographic keys.

For example, for BIP32-Ed25519 extended signing keys, the
[`cardano-crypto`](https://github.com/input-output-hk/cardano-crypto)
implementation supports a 128-byte binary serialization format, while
[`jcli`](https://input-output-hk.github.io/jormungandr/jcli/introduction.html)
and
[`cardano-addresses`](https://github.com/input-output-hk/cardano-addresses)
supports a 96-byte binary serialization format.

Another example would be
[`cardano-cli`](https://github.com/input-output-hk/cardano-node) which
supports a custom JSON format, referred to as "text envelope", (which can be
used for serialising keys) that isn't supported by other projects in the
eco-system.

This has introduced compatibility problems for both users and developers:

- Users cannot easily utilize their keys across different tools and software
  in the Cardano eco-system as they may be serialized in different ways.

- Developers wanting to support the different serialisation formats may need
  to write potentially error-prone (de)serialisation and conversion
  operations.

Therefore, this CIP aims to define standard cryptographic key serialisation
formats to be used by projects throughout the Cardano eco-system.

## Specification

### Verification Keys

For the verification (public) key binary format, we simply use the raw 32-byte
Ed25519 public key data.

This structure should be Bech32 encoded, using one of the appropriate `*_vk`
prefixes defined in CIP-0005.

### Extended Verification Keys

For extended verification (public) keys, we define the following 64-byte
binary format:

```
+-----------------------+-----------------------+
| Public Key (32 bytes) | Chain Code (32 bytes) |
+-----------------------+-----------------------+
```

That is, a 32-byte Ed25519 public key followed by a 32-byte chain code.

This structure should be Bech32 encoded, using one of the appropriate `*_xvk`
prefixes defined in CIP-0005.

### Signing Keys

For the signing (private) key binary format, we simply use the raw 32-byte
Ed25519 private key data.

This structure should be Bech32 encoded, using one of the appropriate `*_sk`
prefixes defined in CIP-0005.

### Extended Signing Keys

For extended signing (private) keys, we define the following 96-byte binary
format:

```
+---------------------------------+-----------------------+
| Extended Private Key (64 bytes) | Chain Code (32 bytes) |
+---------------------------------+-----------------------+
```

That is, a 64-byte Ed25519 extended private key followed by a 32-byte chain
code.

This structure should be Bech32 encoded, using one of the appropriate `*_xsk`
prefixes defined in CIP-0005.

## Rationale: How does this CIP achieve its goals?

### Extended Signing Key Format

As mentioned in the [Abstract](#abstract), the original
[`cardano-crypto`](https://github.com/input-output-hk/cardano-crypto)
implementation defined a 128-byte binary serialization format for
BIP32-Ed25519 extended signing keys:

```
+---------------------------------+-----------------------+-----------------------+
| Extended Private Key (64 bytes) | Public Key (32 bytes) | Chain Code (32 bytes) |
+---------------------------------+-----------------------+-----------------------+
```

However, as it turns out, keeping around the 32-byte Ed25519 public key is
redundant as it can easily be derived from the Ed25519 private key (the first
32 bytes of the 64-byte extended private key).

Therefore, because other projects such as
[`jcli`](https://input-output-hk.github.io/jormungandr/jcli/introduction.html)
and
[`cardano-addresses`](https://github.com/input-output-hk/cardano-addresses)
already utilize the more compact 96-byte format, we opt to define that as the
standard.

## Path to Active

### Acceptance Criteria

- [x] Confirm support by applications and tools from different developers:
  - [x] [jcli](https://github.com/input-output-hk/catalyst-core/tree/main/src/jormungandr/jcli)
  - [x] [cardano-signer](https://github.com/gitmachtl/cardano-signer)
  - [x] [cardano-serialization-lib](https://github.com/Emurgo/cardano-serialization-lib)

### Implementation Plan

N/A

## Copyright

This CIP is licensed under [Apache-2.0](https://www.apache.org/licenses/LICENSE-2.0).
