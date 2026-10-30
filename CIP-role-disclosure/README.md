---
CIP: "?"
Title: Disclosure of Governance Roles
Category: Metadata
Status: Proposed
Authors:
    - Smit Blockchain Operations (Pool BKIND) <developmentbkind@gmail.com>
Implementors:
    - Smit Blockchain Operations (BKIND) <https://smitblockchainops.nl>
Discussions:
    - Original PR: https://github.com/cardano-foundation/CIPs/pull/1311
Solution To:
    - CPS-0016: https://github.com/cardano-foundation/CIPs/tree/master/CPS-0016
Created: 2026-10-29
License: CC-BY-4.0
---

## Abstract

This CIP defines how a stake pool or a DRep declares, in the metadata that a
certificate already anchors on chain, which other governance roles the same
person or entity holds: stake pool, DRep, or Constitutional Committee member.
The declaration is a reference of the type `Role` whose URI names the
credential of the other role. A tool can then read which roles are declared,
which declarations are reciprocal, and for which pairs two valid documents
declare nothing. The CIP makes disclosure machine-readable. It does not prove
common ownership and it does not judge whether a disclosure is complete.

## Motivation: Why is this CIP necessary?

The Cardano Constitution, Article II, Section 3, paragraph 2, states that
"anyone holding multiple roles must publicly disclose such overlaps before
engaging in any on-chain governance actions." It does not say where or in
what form. Three things follow:

1. There is no standard machine-readable form for such a disclosure. It
   appears in free text: in a DRep's CIP-119 metadata, on a website, on
   social media. A tool can search free text, but it cannot discover and
   interpret such a sentence in an interoperable way, and a reader cannot
   check that it is complete.
2. CIP-119 has generic references and the registered pool metadata has free
   text, but neither defines a reference type for a governance role. A name
   or a ticker in free text is not a unique, credential-based link.
3. The roles themselves are on chain, each under its own credential. What is
   missing is the link between the credentials, stated by the holder, in a
   place that a certificate anchors and a tool can read.

This CIP supplies that link and nothing else. It does not weigh roles, judge
overlaps, or change what any role may do.

## Specification

The key words MUST, MUST NOT, SHOULD and MAY are to be interpreted as described
in RFC 2119.

### Role URIs

A role is named by a URI under the `web+cardano:` scheme of CIP-0013. CPS-0016
registers the authorities of that scheme and requires an extension to use a
new, unique authority. This CIP uses two:

1. `addr`, registered by CIP-0134, for a DRep credential and for a
   Constitutional Committee cold credential, in their CIP-0129 bech32 form.
2. `pool`, registered by this CIP, for a stake pool, in the bech32 form of
   CIP-0005 (prefix `pool`, the 28-byte pool ID).

The `stake` authority of CIP-0013 and the `drep` authority of CIP-0162 are
instructions to a wallet to delegate. They are not role URIs, and a tool MUST
NOT read them as declarations.

```abnf
roleuri    = "web+cardano://" ( poolrole / dreprole / ccrole )
poolrole   = "pool/" poolid
dreprole   = "addr/" drepid
ccrole     = "addr/" ccid
poolid     = %x70.6F.6F.6C.31 1*BECH32CHAR
drepid     = %x64.72.65.70.31 1*BECH32CHAR
ccid       = %x63.63.5F.63.6F.6C.64.31 1*BECH32CHAR
BECH32CHAR = %x30 / %x32-39 / %x61 / %x63-68 / %x6A-6E / %x70-7A
```

Quoted strings in ABNF are case-insensitive, so the identifiers are given as
code points: `poolid` begins with the bytes of `pool1`, `drepid` with those
of `drep1`, `ccid` with those of `cc_cold1`, and `BECH32CHAR` is the bech32
alphabet in lowercase.

1. `poolid` is the bech32 of the 28-byte pool ID (the blake2b-224 hash of
   the cold verification key) with prefix `pool`, as CIP-0005 defines it.
   The checksum MUST be valid and the payload MUST be 28 bytes.
2. `drepid` is a CIP-0129 DRep identifier: bech32 with prefix `drep`, payload
   one header byte (`0x22` key hash, `0x23` script hash) and the 28-byte
   credential hash. `ccid` is a CIP-0129 cold credential: prefix `cc_cold`,
   header `0x12` or `0x13`, and the 28-byte hash. The checksum MUST be valid,
   the payload MUST be 29 bytes, and the header byte MUST be one of the two
   values given for the prefix. Any other header byte names a credential
   this CIP does not define, and the reference is invalid.
3. CIP-0134 admits other strings under `addr`, among them the CIP-0105 forms
   with prefixes `drep_vk`, `drep_script`, `cc_cold_vk` and `cc_cold_script`.
   Those are not role URIs: a credential has one role URI, the CIP-0129 form,
   so that two documents that name the same credential name it the same way.
4. The scheme and the authority are case-insensitive. The identifier is
   lowercase, as the grammar says: an uppercase or mixed-case identifier is
   invalid. A tool MUST compare roles by the decoded credential, never by the
   URI string.

Examples:

```
web+cardano://pool/pool1m83drqwlugdt9jn7jkz8hx3pne53acfkd539d9cj8yr92dr4k9y
web+cardano://addr/drep1ytc6867ae0xmkekvmex79r9akyy28eu8nu03jf3xu9fle6c82l4eq
web+cardano://addr/cc_cold1zgf5jdusmxcrfqapu8ngf6j04u0wfzjc7sp9wnnlyfr0f4q68as9w
```

### The `Role` reference

A declaration is an entry in a `references` list:

```json
{
  "@type": "Role",
  "label": "Stake pool BKIND, operated by this DRep",
  "uri": "web+cardano://pool/pool1m83drqwlugdt9jn7jkz8hx3pne53acfkd539d9cj8yr92dr4k9y"
}
```

1. `@type` MUST be `Role` and `uri` MUST be a role URI. In a CIP-119
   document the term `Role` is defined by the context of this CIP, see
   "Context and schema" below.
2. `label` MUST be present and MUST NOT be empty or consist of whitespace
   only, and SHOULD say in words which role it is. Tools MUST NOT derive
   anything from it. A reference with a missing, empty or whitespace-only
   label is invalid and MUST be ignored when determining declarations. A tool
   SHOULD report the defect.
3. A `Role` reference declares that the person or entity that controls the
   credential the document belongs to also controls the credential in the
   URI. A reference to a role held by someone else MUST NOT use this type.
4. A document MAY carry several `Role` references. Entries that decode to
   the same credential count as one.

### Where a declaration lives

A declaration lives in a document whose hash a certificate carries. Every
version has its hash anchored in a certificate contained in a transaction
authorized by the declaring credential, with a place in the chain's history.

1. **DRep**: in the CIP-119 document, in `body.references`, the list that
   CIP-100 and CIP-119 already define. A DRep MAY declare stake pools
   (`pool`) and Constitutional Committee cold credentials (`addr` with a
   `cc_cold1` identifier). Nothing else in the document changes.
2. **Stake pool**: in the registered pool metadata document, the file whose
   hash is in the registration certificate. That format has no `references`
   field in its specification, so the declaration is a top-level key `references` holding a list
   with the same entries. A pool MAY declare DReps and cold credentials
   (`addr`). The registered pool metadata format limits the document to 512
   bytes. The Appendix has a complete example of 296 bytes.
3. **Constitutional Committee**: a committee credential has no document of
   its own. A member who is also a DRep or a pool operator declares the
   committee role from that side.

Any other direction is invalid: a DRep declaring a DRep, a pool declaring a
pool, a document declaring its own credential. The extended pool metadata of
CIP-0006 is not a place for a declaration, see the Rationale.

### Versioning

The meaning of `Role`, the `pool` authority and the use of `addr` for the two
credential forms are fixed by this CIP. A change to any of them requires a
new CIP that supersedes this one. A new kind of governance credential needs
a new CIP under CPS-0016. A tool treats an authority or an identifier form it
does not know as invalid.

### How a tool reads declarations

A tool reads the chain at one block and reports the epoch of that block.
The latest certificate is the latest one at or before that block. A pool is
retired when its latest retirement certificate has a retirement epoch not
after that epoch and no later registration certificate supersedes it, since
the ledger removes the pool at the start of the retirement epoch and a new
registration cancels a pending retirement. A committee member is
current while that epoch is not after its expiration epoch, since the ledger
counts a member as expired only when the current epoch is greater
(cardano-ledger, Conway `Ratify`). The population a tool reads is the one of
reference validity below: the pools registered and not retired, and the
DReps registered, active or not. A retired pool or a deregistered DRep is
not read, whatever its last document says.

**Document status.** For a pool, the document is the one named by its latest
registration certificate. For a DRep, the one named by the anchor of its
latest registration or update certificate. The status is the result of this
tool's own attempt, not a property of the chain: two tools with different
fetch capabilities can report different statuses for one document. The
status is one of:

1. **valid**: fetched, the blake2b-256 of the exact bytes received equals the
   hash on chain, and the content conforms: for a pool a JSON object, for a
   DRep a JSON object whose `body` is an object, the CIP-100 structure that
   CIP-119 builds on. An object with a duplicate key does not conform.
   Declarations follow from the JSON structure. JSON-LD expansion or the
   `@context` does not change which references count.
2. **no anchor**: the latest certificate carries no metadata.
3. **unreachable**: the tool tried to fetch the document and could not.
4. **hash mismatch**: fetched, but the hash differs.
5. **invalid**: the hash matches, but the content does not conform.
6. **not fetched**: the tool has not tried yet. A tool reports this status
   rather than one of the others, since it has observed nothing.

Only a valid document carries declarations. The other statuses carry none,
and a tool MUST NOT treat them as "nothing declared". In a valid document,
a `references` value that is not an array carries no declarations, and an
entry that is not an object is ignored.

**Reference validity.** A `Role` reference in a valid document is valid when
its URI parses and the credential exists on the network the tool reads: a
pool registered and not retired at that block, a DRep registered at that
block, or a cold credential that is or was a committee member at that block.
Otherwise it is invalid and ignored.

**The relation between a pool P and a DRep D** is one of:

1. **reciprocal**: both documents are valid, P declares D and D declares P.
2. **declared by pool**: both valid, only P declares D.
3. **declared by DRep**: both valid, only D declares P.
4. **not declared**: both valid, neither declares the other.
5. **unknown**: at least one document is not valid.

**A committee role** is at most declared, because the committee side cannot
answer. A tool reports with it whether the credential is a **current**
member (in the committee at that block, not expired, not resigned) or
a **former** member.

**A tool MUST NOT:**

1. Infer a role from a shared name, a shared website, a delegation, a vote or
   any other signal, and present it as a declaration.
2. Present a reciprocal relation as proof that one person or entity controls
   both credentials. It proves that both credentials authorized certificates
   anchoring documents that name each other.
3. Present "not declared" or "unknown" as the absence of an overlap, or as
   compliance with the Constitution.

Whether a disclosure was in place when an earlier vote was cast is out of
scope. A tool reads the latest documents.

### Context and schema

This CIP defines its terms in its own namespace, as CIP-0136 does for its
reference type, and changes neither CIP-0100, CIP-0119 nor CIP-0013.

1. The prefix `CIPxxxx` (the number of this CIP once assigned) expands to
   `https://github.com/cardano-foundation/CIPs/blob/master/CIP-xxxx/README.md#`.
2. The term `Role` is `CIPxxxx:RoleReference`, declared inside the context
   of `references` of a CIP-119 document, next to the CIP-100 terms. The
   Appendix shows a complete document.
3. This CIP ships `cip-xxxx.common.jsonld` with that context and
   `cip-xxxx.common.schema.json`, a `reference` definition whose `@type`
   enum holds `Role`, for validators that want to accept it. Both files are
   added to the CIP directory once the number is assigned. The Appendix
   shows their content.
4. Registered pool metadata is plain JSON without a context. There the value
   `Role` of `@type` is defined by this text.

The `pool` authority is registered under CPS-0016 by this CIP.

### Backward compatibility

A tool that validates DRep metadata against the current CIP-119 schema
rejects a document with a `Role` reference until it also accepts the schema
of this CIP, and what it then shows depends on the tool. A tool that reads
`references` without validating `@type` can show a `Role` reference as it
shows any reference, or ignore it.

A key beyond the four of the delegation specification at the top level of
registered pool metadata is existing practice, not a novelty of this CIP: at
block 14130891 (epoch 664), of the 1,986 registered pools whose document
matches the hash in their certificate, 1,074 carry such a key, 993 of them a
key named `extended`, read from db-sync and from the documents at their
registered addresses. The registration certificate carries the metadata URL
and hash. The ledger does not parse the JSON document. cardano-db-sync parses
the four fields and ignores other keys.

Whether a given wallet or explorer tolerates one more key is that tool's
behavior, and a pool MUST keep its document within 512 bytes, for example
with compact JSON and shorter free text, or omit the declaration.

## Rationale: How does this CIP achieve its goals?

**A standard for declarations, not for identity.** Two credentials that name
each other prove that each authorized a certificate anchoring a document that
names the other. They do not prove that one person controls both, since two
parties can agree to name each other. The CIP therefore calls the strongest
state "reciprocal" and says what a tool may and may not conclude. The
Constitution asks for a disclosure. This CIP gives it a form a program can
read and leaves truth and completeness with the holder.

**References and URIs.** CIP-119 already has `references` with a type, a
label and a URI, and explorers already read it. A new type in this CIP's own
namespace reaches readers through tools that exist today and changes no other
CIP. CIP-0134 already gives a DRep and a committee credential a URI form, so
this CIP reuses it. A pool had no such form: the `stake` authority of
CIP-0013 and the `drep` authority of CIP-0162 are delegation instructions for
a wallet, and a declaration must not be one. Hence the `pool` authority.
Only the pool ID is a role, because a ticker can be shared and can change.

**Only certificate-anchored documents.** Every version of the DRep document
and of the registered pool document has its hash anchored in a certificate
contained in a transaction authorized by the declaring credential, at a known
place in the chain. The extended pool metadata of CIP-0006 can be signed with a key
published in the main document, which proves who wrote it, but it can be
replaced by the same key without a transaction, so a reader cannot tell which
version was in force when. For a disclosure the Constitution ties to "before
engaging", the history matters.

**Why reciprocity and not a signature.** A declaration could carry a
signature by the other credential over a nonce, so that one document proves
the link. A bare signature that can be verified against the credential hash
alone works only for key credentials. Native multisig and Plutus credentials
require script-specific evidence and witnesses, so one uniform signature
field cannot serve every credential. Five of the seven current committee cold
credentials are scripts, and so is the DRep of the Cardano Foundation. Used
as the sole proof mechanism, a signature would exclude script DReps and would
not cover most committee members. Registration and update certificates
support both key and script credentials, which is why the CIP keeps
certificate-anchored declarations and reciprocity. For a committee credential
there is no metadata certificate, so the CIP claims no reciprocal proof
there: that relation stays one-sided. An optional signature proof for key
credentials can be defined in a later CIP.

**Status before relation, and current before former.** A missing or broken
document says nothing about what its holder declares, so it gives "unknown"
and never "not declared". A committee credential stays in the chain's history
forever, so a former member is shown as former. The ledger gives a committee
credential no anchor, which is why the committee side cannot speak in
metadata. A later CIP could change that.

**No weighing.** Whether an overlap is a problem is for the reader, the
Constitution and the voting bodies. This CIP makes it readable and stops.

### Security and privacy

1. A `Role` reference is a claim authorized by one credential about another.
   Tools MUST NOT present it as acknowledged by the other credential unless
   that credential's own valid document names it back. A false claim by one
   side is therefore visible as what it is: "declared by" that side when
   both documents are valid, and "unknown" when the other document is not,
   never a confirmation.
2. The credentials are public on chain, but the link between them is new
   information: it connects the stake, the votes and the committee decisions
   of one holder. Declaring a role is a deliberate public disclosure, which is
   what the Constitution asks. The certificate and its hash are permanent, and
   the link can remain available once anyone has retrieved the document.
3. A `Role` reference adds about 150 bytes to a document and nothing
   executable.

## Path to Active

### Acceptance Criteria

1. [ ] The context and schema files of this CIP are published with it, and
       at least one public CIP-119 validator accepts a document that uses
       them.
2. [ ] At least two independent public tools read declarations over every
       pool and DRep on mainnet and show document status and relation for
       the pools and DReps they list.
3. [ ] At least ten DReps and ten stake pools on mainnet carry a `Role`
       reference, and at least five pool and DRep pairs are reciprocal.

### Implementation Plan

1. [x] The DRep metadata of BKIND
       (drep1ytc6867ae0xmkekvmex79r9akyy28eu8nu03jf3xu9fle6c82l4eq) carries
       a `Role` reference to pool BKIND: anchor hash
       `2a41fdeebcd1432e0feb12c68af612c4e2cbd0004a2ee785619d9e6058bd9c3e`,
       transaction
       `9593900f25cdb6310cb76761ec3e228e0ac9b8a8563c6bc454785a9c6e9dfc8e`,
       2026-10-29. It uses the URI forms of the first draft and will be
       updated to the forms of this text once the number is assigned.
2. [x] The pool metadata of BKIND carries a `Role` reference to the DRep,
       the first reciprocal pair: metadata hash
       `f9de5aa69eca5319d5c81f74023f7c84003e9d6bfbc80b6ca64ed526168b35b3`,
       transaction
       `994936264446dc53873dfc6cdbe504c4faec13e13d039eea418d1e04ef3b7e4d`,
       2026-10-29. Same remark.
3. [x] The DRep list and pool list of smitblockchainops.nl read declarations
       over every pool and DRep on mainnet and show document status and
       relation for the pools and DReps they list, since 2026-10-29, as the
       first tool.
4. [ ] Once the number is assigned: the DRep metadata and the pool metadata
       of BKIND move to the URI forms and the context of this text, and the
       context and schema files are added to the CIP directory.

## Appendix

### A pool metadata document with a declaration (296 bytes)

```json
{"name":"Smit Blockchain Operations","ticker":"BKIND","homepage":"https://smitblockchainops.nl","description":"The trustworthy Cardano Stake Pool","references":[{"@type":"Role","label":"DRep of the operator","uri":"web+cardano://addr/drep1ytc6867ae0xmkekvmex79r9akyy28eu8nu03jf3xu9fle6c82l4eq"}]}
```

### A DRep metadata document with declarations

```json
{
  "@context": {
    "CIP100": "https://github.com/cardano-foundation/CIPs/blob/master/CIP-0100/README.md#",
    "CIP119": "https://github.com/cardano-foundation/CIPs/blob/master/CIP-0119/README.md#",
    "CIPxxxx": "https://github.com/cardano-foundation/CIPs/blob/master/CIP-xxxx/README.md#",
    "hashAlgorithm": "CIP100:hashAlgorithm",
    "body": {
      "@id": "CIP119:body",
      "@context": {
        "references": {
          "@id": "CIP119:references",
          "@container": "@set",
          "@context": {
            "GovernanceMetadata": "CIP100:GovernanceMetadataReference",
            "Other": "CIP100:OtherReference",
            "Link": "CIP119:LinkReference",
            "Identity": "CIP119:IdentityReference",
            "Role": "CIPxxxx:RoleReference",
            "label": "CIP100:reference-label",
            "uri": "CIP100:reference-uri"
          }
        },
        "givenName": "CIP119:givenName",
        "objectives": "CIP119:objectives",
        "motivations": "CIP119:motivations",
        "qualifications": "CIP119:qualifications"
      }
    }
  },
  "hashAlgorithm": "blake2b-256",
  "body": {
    "givenName": "BKIND",
    "objectives": "Example.",
    "motivations": "Example.",
    "qualifications": "Example.",
    "references": [
      {
        "@type": "Identity",
        "label": "Personal website, shows this DRep ID and the pool ID",
        "uri": "https://smitblockchainops.nl"
      },
      {
        "@type": "Role",
        "label": "Stake pool BKIND, operated by this DRep",
        "uri": "web+cardano://pool/pool1m83drqwlugdt9jn7jkz8hx3pne53acfkd539d9cj8yr92dr4k9y"
      }
    ]
  }
}
```

### The context file of this CIP

```json
{
  "@context": {
    "CIPxxxx": "https://github.com/cardano-foundation/CIPs/blob/master/CIP-xxxx/README.md#",
    "Role": "CIPxxxx:RoleReference"
  }
}
```

### The schema fragment of this CIP

```json
{
  "reference": {
    "title": "Reference",
    "type": "object",
    "required": ["@type", "label", "uri"],
    "properties": {
      "@type": {"type": "string", "enum": ["GovernanceMetadata", "Other", "Link", "Identity", "Role"]},
      "label": {"type": "string", "minLength": 1},
      "uri": {"type": "string"}
    }
  }
}
```

### Test vectors

Each vector gives what a tool sees and what it MUST report.

1. **Reciprocal.** P's document is valid and declares D, D's is valid and
   declares P. Result: reciprocal.
2. **One side.** As 1, but D's document declares nothing. Result: declared
   by pool.
3. **Nothing.** Both valid, neither declares the other. Result: not declared.
4. **Not valid.** P's document is valid and declares D. D's anchor URL gives
   no response, or serves bytes with another hash, or D's latest certificate
   has no anchor, or the tool has not tried D's URL yet. Result: D's status
   unreachable, hash mismatch, no anchor or not fetched, relation unknown,
   even if the bytes served declare P.
5. **Invalid URI.** A `Role` reference with
   `web+cardano://addr/drep1ytc6867ae0xmkekvmex79r9akyy28eu8nu03jf3xu9fle6c82l4ex`
   (last character changed, checksum fails), or with
   `web+cardano://pool/BKIND` (a ticker), or with
   `web+cardano://stake?d9e2d181dfe21ab2ca7e95847b9a219e691ee1366d22569712390655`
   (a delegation instruction, not a role URI), or with
   `web+cardano://addr/drep_vk1...` (a CIP-0105 form), or with an identifier
   in uppercase or mixed case, or with a label of spaces only. Result:
   invalid, ignored. The same reference in an object that carries the key
   `uri` twice: the document is invalid, relation unknown.
6. **Wrong direction.** A DRep document with a `Role` reference to a `drep`
   URI. Result: invalid, ignored.
7. **Retired pool.** D declares pool P, and P's retirement epoch is the
   reading epoch or earlier. Result: invalid at that epoch, ignored. If P
   registered again after announcing the retirement and before the reading
   block, P is not retired and the reference is valid. A committee member
   whose expiration epoch is the reading epoch is still current.
8. **Former member.** D declares
   `web+cardano://addr/cc_cold1ztwq6mh5jkgwk6yq559qptw7zavkumtk7u2e2uh6rlu972slkt0rz`,
   whose term ended in epoch 653. Reading in epoch 664: declared, former
   member.

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
