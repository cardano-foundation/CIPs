---
CPS: 14
Title: Register of CBOR Tags for Cardano Data structures
Category: Tools
Status: Open
Authors:
  - Steven Johnson <steven.johnson@iohk.io>
Proposed Solutions:
  - CIP-0114 | CBOR Tags Registry: https://github.com/cardano-foundation/CIPs/tree/master/CIP-0114
Discussions:
  - Original pull request: https://github.com/cardano-foundation/CIPs/pull/751
  - CIP-0114 pull request: https://github.com/cardano-foundation/CIPs/pull/752
Created: 2024-01-24
License: CC-BY-4.0
---

## Abstract

Cardano uses CBOR for a lot of data structures, both on and off chain.
CBOR defines a number of tags which identify the types of encoded data, and IANA maintain a registry of these tags.
Cardano data structures could benefit from consistent tagging of CBOR fields.

### **Acknowledgements**

Thank you to the following people who helped review this draft before it was published:

* Ryan Williams

## Problem

[CBOR] defines the ledger contents, transactions, and commonly the metadata attached to transactions.
For example [CIP-0036] metadata used for registering voters in Project Catalyst.
[CBOR] defines a set of [CBOR Tags] which are used to define the type of data being encoded.
While [CBOR] defines a basic set of [CBOR Tags] it also defines a [CBOR Tags Registry] to enable further tags to be defined.
[IANA][IANA - Homepage] maintains a registry of CBOR Tags at [IANA - CBOR Tags Registry][IANA].
[BCR-2020-006] defines CBOR tags related to some blockchain data structures.
Most (all?) of these are registered with IANA.

Without Tags, [CBOR] data types can become ambiguous and rely on comments in a specification to help resolve the contents.
[CBOR] tags unequivocally disambiguate the encoding of data.
They also help with forward compatibility and extensibility of data structures.

However, with the exception of [#6.258] there are no Cardano specific registered tags.
Also, Tag use in CIPs is currently haphazard and inconsistent.
For example, [CIP-0042] uses tag **#6.102**, which [IANA] list as "Unassigned".
This Tag is able to be assigned by IANA at any time.
It's unofficial use could break, if a decoder tries to interpret the data according to it's official [IANA] assignment.

Defining a CBOR tag for a Cardano data structure will also define a canonical representation for the data type so tagged.
This will help with interoperability and consistency of specification.
CIPs can simply refer to the Tag, and the CIP in which it is defined, rather than define how that data will be represented.

## Use Cases

In Project Catalyst CIP-36 a Voting key is defined as:

```cddl
$cip36_vote_pub_key /= bytes .size 32
```

This is a public [ED25519-BIP32] key.
If is used to validate that a Vote has been signed correctly by the registered voter.

However, there are a couple of issues:

1. How the Key is encoded is NOT defined.
   1. It is 32 bytes, but is it Big-endian or Little-endian encoded?
2. The kind of key is defined only in the words of the specification.

If there was a canonical specification for tagging and encoding [ED25519-BIP32] keys.
And say that tag was `7777`, then this could be defined simply as:

```cddl
$cip36_vote_pub_key /= #6.7777(bytes .size 32)
```

Without any extra information, it can be now determined the Key type that is valid, and the encoding.
This would lead to greater clarity and simpler specifications.

It would also allow simple and unambiguous extension.
Say Project Catalyst desired to also the use of Signing Public Keys as defined in [BCR-2023-011].
All it needs to do is define that `#6.40022` is a valid public key type.
The decoder would be able to unambiguously identify the key type.
The basic metadata encoding would not need to change, just the list of valid public key types.
A decoder based on an older version of the specification would be able to detect that the new key type was not supported.
This would provide forward compatibility.

## Goals

1. Definitive sources of truth for CBOR encoding of common Cardano data structures.
2. Uniform use of CBOR tags to unambiguously identify common Cardano data structures inside CBOR.
3. An easily accessible reference to all CBOR tags defined by CIPs, to help eliminate their re-definition.
4. Guidelines on the creation of new CBOR tags as data structures emerge, or existing data structures are formalized.
5. Clarity on who is responsible to have new Tags registered with IANA.

It is NOT a goal of this CPS to cause all pre-existing Cardano data structures to be standardized with CBOR tags.
Individual projects should evaluate if the existing tags are sufficient or if they require new ones for their purposes.
it would then be the responsibility of the project to raise a CIP to standardize the CBOR tag for the pre-existing data structure.

It is also not a goal of this CPS to define how general data structures are tagged.
The data structure should be either defined by a CIP or integral to Cardano.
An example is `ULID` this has no current CBOR Tag, but it is not defined by a CIP nor integral to Cardano.
Even though a CIPs metadata may use one, its formalization should be done outside the CIP process.

## Open Questions

* Should we define a canonical list of tags, the CIP they are defined in, and if they are IANA registered or not?
* Who should register the Tag with IANA?
  * Would this become a necessary part of the "path to Active" of any CIP which defines a CBOR tag?
* How should duplicate structures be handled (same data encoded differently with a different tag)?
* Should defining tags be their own CIP, or can they be part of a larger CIP?
* Should we define recommendations for the use of Tags in Metadata CIPs?

## References

* [CIP-0036 - Catalyst Registration Transaction Metadata Format (Updated)][CIP-0036]
* [CIP-0042 - New Plutus Builtin serialiseData][CIP-0042]
* [RFC8949 - Concise Binary Object Representation (CBOR)][CBOR]
* [BCR-2020-006 - Registry of Uniform Resource (UR) Types][BCR-2020-006]
* [BCR-2023-011 - UR Type Definitions for Public Key Cryptography][BCR-2023-011]
* [IANA CBOR Tag Registry][IANA]

## Copyright

This CPS is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).

[CIP-0036]: https://github.com/cardano-foundation/CIPs/tree/master/CIP-0036
[CIP-0042]: https://github.com/cardano-foundation/CIPs/blob/master/CIP-0042/README.md
[CBOR]: https://datatracker.ietf.org/doc/html/rfc8949
[CBOR Tags]: https://datatracker.ietf.org/doc/html/rfc8949#name-tagging-of-items
[CBOR Tags Registry]: https://datatracker.ietf.org/doc/html/rfc8949#ianatags
[IANA - Homepage]: https://www.iana.org/
[IANA]: https://www.iana.org/assignments/cbor-tags/cbor-tags.xhtml
[BCR-2020-006]: https://github.com/BlockchainCommons/Research/blob/master/papers/bcr-2020-006-urtypes.md
[ED25519-BIP32]: https://github.com/input-output-hk/adrestia/raw/bdf00e4e7791d610d273d227be877bc6dd0dbcfb/user-guide/static/Ed25519_BIP.pdf
[BCR-2023-011]: https://github.com/BlockchainCommons/Research/blob/master/papers/bcr-2023-011-public-key-crypto.md
