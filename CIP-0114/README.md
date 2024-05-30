---
CIP: 114
Title: CBOR Tags Registry
Status: Proposed
Category: Tools
Authors:
  - Steven Johnson <steven.johnson@iohk.io>
Implementors: N/A
Discussions:
  - https://github.com/cardano-foundation/CIPs/pull/752
Created: 2020-01-25
License: CC-BY-4.0
---

## Abstract

Cardano typically uses CBOR to encode structured data.
For example, the Block data and individual transactions are all CBOR encoded.

CIPs define many of the individual data structures used by both the Ledger and Metadata attached to transactions.
This CIP defines a set of policies for the creation and maintenance of new CBOR tags for Cardano Data structures.
It also collates a list of all currently defined Tags for easy reference.
Finally, it recommends best practice for registering those Tags with IANA.

## Motivation: why is this CIP necessary?

This CIP is motivated by the problems outlined in [CPS-0014].

## Specification

[CBOR] defines a schemaless method of encoding data.
Part of that specification (3.4) defines how generic data can be tagged to assist in the proper interpretation of the encoded data.
Currently all Cardano data structures in both the Ledger and metadata do not widely use Tags.
Nor is there any standardized way to create a new tag for a Cardano data structure.

[IANA] maintains a registry of all [CBOR] Tags.
Anyone can submit a request to register a tag in the range of 32768-18446744073709551615.
These are known as *First Come First Served* tags.
To register a tag, an applicant must demonstrate where the Tag is defined, and also the format of the data.
If the data structure is defined by a CIP, the natural place to define its Tag is also in a CIP.

### Defining Tags

Tags can be defined for any data structure defined by a CIP or commonly used by Cardano.
Examples of commonly used data structures could be those encoded inside the Cardano block or transaction.
Tags should be defined by the following process:

1. If a [CBOR] tag is desired for an application, first the applicant MUST check that one does not already exist.
   If it does, then the pre-existing TAG must be used, as well as the defined canonical encoding.
   This is to prevent redundant and wasteful re-tagging of the same data structures.
2. Otherwise the application may define a [CBOR] Tag for the necessary data structures as follows:
   1. The CIP which defines the data structure can also define a Tag and its encoding in [CBOR]. **(Preferred)**
   2. Alternatively, if the data structure is already defined by a CIP, then there are two possibilities.
      1. The original CIP is edited to add Tags and their canonical representation in [CBOR].
      2. A supplementary CIP can be made that simply defines the TAG and canonical representation.
        Such a CIP would reference the original CIP to define the data structure itself.
   3. CIP authors would select an unused [CBOR] Tag in the [IANA Registry][IANA], and assign it to their data structure.
      1. The CIP should add to its "Path to Active" that the selected Tag/s have been successfully registered with [IANA].
         This allows the CIP to be edited with the final Tag once [IANA] have accepted and published the registration.
   4. CIP Authors would include in their PR an addition to the Cardano [CBOR Tag Registry](#tag-registry).

### Registration of TAGS with IANA

Registration of the Tag with IANA is the sole responsibility of the CIP author.
CIPs should not proceed to Active if they define unregistered Tags on data structures.
This is to prevent abuse of the Tag number space.

*NOTE: Tags defined by any CIP or marked as not registered with IANA in the `registry.json` MUST NOT be used outside of testing.
Tags not registered with IANA are subject to change during the IANA registration process.*

### Usage of Tags within a CIP

CIPs, such as metadata CIPs can freely define when and how tags are used with any CBOR data structure.
For example, a CIP may require that a particular field is always tagged.
They may also define that a field need not be tagged if it is the typical data structure.
Only less common or unusual data structures would be tagged in this case.
A CIP may also define that Tags are not used, and only the canonical encoding.

### Canonical Encoding

When a Tag is defined, its Canonical encoding must also be defined.
This is to ensure that all data that is tagged is encoded in a uniform manor.
Even if a CIP does NOT use a tag, it should preferably use the canonical encoding for the data structure.
This is to prevent fragmentation and confusion amongst compliant encoders and decoders of the various data structures.

If a pre-existing data structure is being tagged, then its most common current encoding should be used as the Canonical encoding.
It should not be re-defined.

For example `ED25519-BIP32` public keys are commonly encoded as a byte array.
The array is 32 bytes long with the most significant byte of the key appearing first in the array.
If a Tag is defined for this public key, it should simply define the Tag.
Its Canonical encoding MUST follow this common encoding scheme.

If a CIP does not refer to a Tag, nor the Canonical encoding specification for the data structure,
AND it does not define an alternative encoding.
Then the application implementing the encoding should assume it is encoded canonically.
This helps ensure backward compatibility with pre-existing CIPs where Tags are not used.

### Tag Registry

Similar to [CIP-0010] this CIP defines a registry of all known tags.
The format of the registry is defined by the json schema: [CIP Tag Registry Schema].
New entries MUST be added to the [CIP Tag Registry] in a PR for a CIP that first defines a new CBOR Tag.
They MUST be updated when the Tag is accepted or rejected by IANA.
The registry clearly notes if the tag is currently known to be registered or not.
If a Tag is not yet registered then any implementor must be aware that its possible the Tag number could change and is not final.
Unregistered tags MUST not be used in any main net on-chain metadata or data structures.
They should only be used for testing purposes until registration is complete.

## Rationale: how does this CIP achieve its goals?

Creating a [registry][CIP Tag Registry] for `CIP Tag` values has the following benefit:

1) It makes it easy for developers to know which `CIP Tags` to use, and if they have been registered or not.
2) It makes it easy to avoid collisions with other standards that use CIP Tags.
3) It helps CIP authors to find appropriate CIP tags for their use case, or to define new tags.

The process for defining and registering Tags should help provide clarity about how a CIP tag can be defined.
It also provides clarity on the responsibility CIP authors have to register the tags they create.
If a CIP author is not prepared to take on that responsibility they should not create a Tag.

## Path to Active

### Acceptance Criteria

- [ ] [CPS-0014] is accepted.
- [ ] At least 1 CIPs are accepted into the Tag registry for historical tags.
- [ ] At least 1 CIPs are accepted into the Tag registry for new tags.
- [ ] At least 3 CIPs of any kind are accepted into the Tag registry.

### Implementation Plan

- [ ] Author to write the first CBOR tag CIP.

## References

- [CPS-0014 -  Register of CBOR Tags for Cardano Data structures][CPS-0014]
- [RFC8949 - Concise Binary Object Representation (CBOR)][CBOR]
- [IANA CBOR Tag Registry][IANA]

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode)

[CPS-0014]: https://github.com/cardano-foundation/CIPs/tree/master/CPS-0014
[CBOR]: https://datatracker.ietf.org/doc/rfc8949/
[IANA]: https://www.iana.org/assignments/cbor-tags/cbor-tags.xhtml
[CIP Tag Registry Schema]: ./registry.schema.json
[CIP Tag Registry]: ./registry.json
