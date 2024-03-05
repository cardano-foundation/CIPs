---
CIP: 115
Title: CBOR tag definition - ED25519-BIP32 Keys
Category: Tools
Status: Proposed
Authors:
    - Steven Johnson <steven.johnson@iohk.io>
Implementors: N/A
Discussions:
    - https://github.com/cardano-foundation/cips/pulls/753
Created: 2024-01-19
License: CC-BY-4.0
---

## Abstract

[CIP-0003] defines [ED25519-BIP32] Keys, Key derivation and a signature scheme.
This CIP defines CBOR Tags and formalizes the Canonical encoding of data structures for [CIP-0003].
The intention is to have these tags registered in the [IANA CBOR Tag Registry].

## Motivation: why is this CIP necessary?

Project Catalyst is in the process of defining new CBOR data structures.
We needed a way to reliably disambiguate different 32 byte strings.
Rather than making a non-standard encoding scheme specific to our structures we would like to use standard [CBOR] Tags.

This CIP is informed by [CPS-0014] and [CIP-0114].

Without this Tag definition, a metadata CIP which uses [ED25519-BIP32] public keys:

- Is likely to just encode public keys as a byte string of 32 bytes; and
- Needs to redundantly define how the keys are encoded in the byte string.
- May encode these keys differently to another CIP, which can lead to confusion and potential error.

[BIP32] also defines `secp256k1` keys which are also 32 bytes long.
This CIP would help disambiguate between these keys and inform the decoder which key is being utilized.

## Specification

| Type | [CBOR] Tag | Type | Size | [IANA CBOR Tag Registry] |
| -- | -- | -- | -- | -- |
| [ED25519-BIP32 Private Key](#ed25519-bip32-private-key) | 32771 | bstr | 32 | To submit |
| [ED25519-BIP32 Extended Private Key](#ed25519-bip32-extended-private-key) | 32772 | bstr | 64 | To submit |
| [ED25519-BIP32 Public Key](#ed25519-bip32-public-key) | 32773 | bstr | 32 | To submit |
| [ED25519-BIP32 Signature](#ed25519-bip32-signature) | 32774 | bstr | 64 | To submit |

*NOTE: These tags are preliminary and subject to change until IANA registration is complete.
They MUST not be used outside of testing purposes.
They MUST not be used in any data intended to be posted to main-net.*

### ED25519-BIP32 Private Key

This key is defined in [ED25519-BIP32].

This is encoded as a byte string of size 32 bytes.

#### [CDDL]

```cddl
ed25519_private_key = #6.32771(bstr .size 32)
```

Data for the key inside the byte string is encoded in [network byte order].

### ED25519-BIP32 Extended Private Key

This key is defined in [ED25519-BIP32].

This is encoded as a byte string of size 64 bytes.

#### [CDDL]

```cddl
ed25519_extended_private_key = #6.32772(bstr .size 64)
```

Data for the key inside the byte string is encoded in [network byte order].

### ED25519-BIP32 Public Key

This key is defined in [ED25519-BIP32].

This is encoded as a byte string of size 32 bytes.

#### [CDDL]

```cddl
ed25519_public_key = #6.32773(bstr .size 32)
```

Data for the key inside the byte string is encoded in [network byte order].

### ED25519-BIP32 Signature

[ED25519-BIP32] defines how signatures can be generated on data from private keys.
These signatures are defined to be 64 bytes long.

Signatures are encoded as a byte string of size 64 bytes.

#### [CDDL]

```cddl
ed25519_bip32_signature = #6.32774(bstr .size 64)
```

Data for the signature inside the byte string is encoded in [network byte order].

## Rationale: how does this CIP achieve its goals?

By defining concrete CBOR tags, it is possible for metadata to unambiguously mark the kind of data encoded.
This is conformant with the intent of Tags in [CBOR], and aligns with [CIP-CBOR-TAGS].

An official published spec is required to register these Tags with [IANA][IANA CBOR Tag Registry].
This document also serves that purpose.

## Path to Active

### Acceptance Criteria

- [ ] These tags to be included in [CIP-CBOR-TAGS].
- [ ] One downstream CIP uses at least one of the tags defined in this CIP.
- [ ] IANA register all the tags as defined herein.

### Implementation Plan

- [ ] Tags are to be used by Project Catalyst for CBOR data structure definitions.
- [ ] Project Catalyst will also make the application to [IANA][IANA CBOR Tag Registry] to register the Tags.

## References

- [CPS-0014 -  Register of CBOR Tags for Cardano Data structures][CPS-0014]
- [CIP-0003 - Wallet Key Generation][CIP-0003]
- [CIP-0114 - CBOR Tags Registry][CIP-0114]
- [RFC8949 - Concise Binary Object Representation (CBOR)][CBOR]
- [RFC8610 - Concise Data Definition Language (CDDL)][CDDL]
- [RFC1700 Data Notations (Network Byte Order)][network byte order]
- [BIP32 - Hierarchical Deterministic Wallets][BIP32]
- [ED25519-BIP32 - Hierarchical Deterministic Keys over a Non-linear Keyspace][ED25519-BIP32]
- [IANA CBOR Tag Registry]

## Copyright

This CIP is licensed under [CC-BY-4.0]

Code samples and reference material are licensed under [Apache 2.0]

[CC-BY-4.0]: https://creativecommons.org/licenses/by/4.0/legalcode
[Apache 2.0]: https://www.apache.org/licenses/LICENSE-2.0.html
[CBOR]: https://www.rfc-editor.org/rfc/rfc8949.html
[CDDL]: https://www.rfc-editor.org/rfc/rfc8610
[CIP-0003]: https://cips.cardano.org/cip/CIP-0003
[BIP32]: https://github.com/bitcoin/bips/blob/master/bip-0032.mediawiki
[IANA CBOR Tag Registry]: https://www.iana.org/assignments/cbor-tags/cbor-tags.xhtml
[network byte order]: https://datatracker.ietf.org/doc/html/rfc1700
[ED25519-BIP32]: https://github.com/input-output-hk/adrestia/raw/bdf00e4e7791d610d273d227be877bc6dd0dbcfb/user-guide/static/Ed25519_BIP.pdf
[CPS-0014]: https://github.com/cardano-foundation/CIPs/tree/master/CPS-0014
[CIP-0114]: https://github.com/cardano-foundation/CIPs/tree/master/CIP-0114
