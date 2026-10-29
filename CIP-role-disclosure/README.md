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
    - Original PR: https://github.com/cardano-foundation/CIPs/pull/?
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

A role is named by a URI under the `web+cardano:` scheme of CIP-0013, which
allows other CIPs to define further keywords. This CIP defines `drep` and
`cc` and reuses `stake`:

```abnf
roleuri   = "web+cardano://" ( stakerole / dreprole / ccrole )
stakerole = "stake?" poolhexid
dreprole  = "drep?" drepid
ccrole    = "cc?" ccid
poolhexid = 56LOWERHEX
drepid    = %x64.72.65.70.31 1*BECH32CHAR
ccid      = %x63.63.5F.63.6F.6C.64.31 1*BECH32CHAR
LOWERHEX  = %x30-39 / %x61-66
BECH32CHAR = %x30 / %x32-39 / %x61 / %x63-68 / %x6A-6E / %x70-7A
```

Quoted strings in ABNF are case-insensitive, so the identifiers are given as
code points: `drepid` begins with the bytes of `drep1`, `ccid` with those of
`cc_cold1`, and `BECH32CHAR` is the bech32 alphabet in lowercase.

1. `poolhexid` is the 28-byte pool ID (the blake2b-224 hash of the cold
   verification key) in lowercase hex, the single pool form of CIP-0013. The
   ticker form of CIP-0013 is not a role, because a ticker is not unique.
2. `drepid` is a CIP-0129 DRep identifier: bech32 with prefix `drep`, payload
   one header byte (`0x22` key hash, `0x23` script hash) and the 28-byte
   credential hash. `ccid` is a CIP-0129 cold credential: prefix `cc_cold`,
   header `0x12` or `0x13`, and the 28-byte hash. The checksum MUST be valid,
   the payload MUST be 29 bytes, and the header byte MUST be one of the two
   values given for the keyword. Any other header byte names a credential
   this CIP does not define, and the reference is invalid.
3. The scheme and the keyword are case-insensitive. The identifier is
   lowercase, as the grammar says: an uppercase or mixed-case identifier is
   invalid. CIP-0013 allows either case for the hex pool ID (`56HEXDIG`);
   the role form is stricter, so that the grammar alone decides. A tool MUST
   compare roles by the decoded credential, never by the URI string.

Examples:

```
web+cardano://stake?d9e2d181dfe21ab2ca7e95847b9a219e691ee1366d22569712390655
web+cardano://drep?drep1ytc6867ae0xmkekvmex79r9akyy28eu8nu03jf3xu9fle6c82l4eq
web+cardano://cc?cc_cold1zgf5jdusmxcrfqapu8ngf6j04u0wfzjc7sp9wnnlyfr0f4q68as9w
```

### The `Role` reference

A declaration is an entry in a `references` list:

```json
{
  "@type": "Role",
  "label": "Stake pool BKIND, operated by this DRep",
  "uri": "web+cardano://stake?d9e2d181dfe21ab2ca7e95847b9a219e691ee1366d22569712390655"
}
```

1. `@type` MUST be `Role` and `uri` MUST be a role URI.
2. `label` MUST be present and MUST NOT be empty or consist of whitespace
   only, and SHOULD say in words which role it is. Tools MUST NOT derive
   anything from it. A reference with a missing, empty or whitespace-only
   label is invalid and MUST be ignored when determining declarations. A tool SHOULD report
   the defect.
3. A `Role` reference declares that the person or entity that controls the
   credential the document belongs to also controls the credential in the
   URI. A reference to a role held by someone else MUST NOT use this type.
4. A document MAY carry several `Role` references. Entries that decode to
   the same credential count as one.

### Where a declaration lives

A declaration lives in a document whose hash a certificate carries, so that
every change is a signed transaction with a place in the chain's history.

1. **DRep**: in the CIP-119 document, in `body.references`. A DRep MAY
   declare stake pools (`stake`) and Constitutional Committee cold
   credentials (`cc`).
2. **Stake pool**: in the registered pool metadata document, the file whose
   hash is in the registration certificate, as a top-level key `references`
   with the same entries. A pool MAY declare DReps (`drep`) and cold
   credentials (`cc`). The registered pool metadata format limits the
   document to 512 bytes. The Appendix has a complete example of 296 bytes.
3. **Constitutional Committee**: a committee credential has no document of
   its own. A member who is also a DRep or a pool operator declares the
   committee role from that side.

Any other direction is invalid: a DRep declaring a DRep, a pool declaring a
pool, a document declaring its own credential. The extended pool metadata of
CIP-0006 is not a place for a declaration, see the Rationale.

### Versioning

The meaning of `Role` and the three URI forms are fixed by this CIP. A change
to either requires a new CIP that supersedes this one. Another CIP MAY add a
keyword for a new kind of governance credential under the extension rule of
CIP-0013. A tool treats a keyword it does not know as invalid.

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
   Declarations follow from the JSON structure; JSON-LD expansion or the
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

### Changes to CIP-0119 and CIP-0013

The JSON schema of CIP-0119 (`cip-0119.common.schema.json`) gains `Role` in
the enum of `@type` of a reference, next to `GovernanceMetadata`, `Other`,
`Link` and `Identity`. The context file (`cip-0119.common.jsonld`) gains the
term `"Role": "CIP119:RoleReference"` in the context of `references`. That
file defines `GovernanceMetadata` and `Other` today and not `Link` and
`Identity`, so a document defines the terms it uses in its own `@context`,
as the document in the Appendix does. The term lives in the namespace of
CIP-119 because it is a reference type of CIP-119 metadata, so a document
needs no reference to this CIP to use it. CIP-0013 registers the keywords
`drep` and `cc` next to `stake`.

### Backward compatibility

A tool that validates DRep metadata against the current CIP-119 schema
rejects a document with a `Role` reference until the schema change is
adopted, and what it then shows depends on the tool. A tool that reads
`references` without validating `@type` can show a `Role` reference as it
shows any reference, or ignore it. A key beyond the four of the delegation
specification at the top level of registered pool metadata is existing
practice, not a novelty of this CIP: at block 14130891 (epoch 664), of the
1,986 registered pools whose document matches the hash in their certificate,
1,074 carry such a key, 993 of them a key named `extended`, read from
db-sync and from the documents at their registered addresses.
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
label and a URI, and explorers already read it. A new type costs one enum
value and reaches readers through tools that exist today. A URI says what
kind of credential it names, and CIP-0013 already defines the pool form and
invites other keywords. Only the hex pool ID is a role, because a ticker can
be shared and can change.

**Only certificate-anchored documents.** Every version of the DRep document
and of the registered pool document is a signed transaction at a known place
in the chain. The extended pool metadata of CIP-0006 can be signed with a key
published in the main document, which proves who wrote it, but it can be
replaced by the same key without a transaction, so a reader cannot tell which
version was in force when. For a disclosure the Constitution ties to "before
engaging", the history matters.

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
   that credential's own valid document names it back.
2. The credentials are public on chain, but the link between them is new
   information: it connects the stake, the votes and the committee decisions
   of one holder. Declaring a role is a deliberate public disclosure, which is
   what the Constitution asks. The certificate and its hash are permanent, and
   the link can remain available once anyone has retrieved the document.
3. A `Role` reference adds about 150 bytes to a document and nothing
   executable.

## Path to Active

### Acceptance Criteria

1. [ ] The `Role` type is in the CIP-0119 context and schema, and the `drep`
       and `cc` keywords are registered in CIP-0013, or those CIPs refer to
       this one.
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
       2026-10-29.
2. [x] The pool metadata of BKIND carries a `Role` reference to the DRep,
       the first reciprocal pair: metadata hash
       `f9de5aa69eca5319d5c81f74023f7c84003e9d6bfbc80b6ca64ed526168b35b3`,
       transaction
       `994936264446dc53873dfc6cdbe504c4faec13e13d039eea418d1e04ef3b7e4d`,
       2026-10-29.
3. [x] The DRep list and pool list of smitblockchainops.nl read declarations
       over every pool and DRep on mainnet and show document status and
       relation for the pools and DReps they list, since 2026-10-29, as the
       first tool.

## Appendix

### A pool metadata document with a declaration (296 bytes)

```json
{"name":"Smit Blockchain Operations","ticker":"BKIND","homepage":"https://smitblockchainops.nl","description":"The trustworthy Cardano Stake Pool","references":[{"@type":"Role","label":"DRep of the operator","uri":"web+cardano://drep?drep1ytc6867ae0xmkekvmex79r9akyy28eu8nu03jf3xu9fle6c82l4eq"}]}
```

### A DRep metadata document with declarations

```json
{
  "@context": {
    "CIP100": "https://github.com/cardano-foundation/CIPs/blob/master/CIP-0100/README.md#",
    "CIP119": "https://github.com/cardano-foundation/CIPs/blob/master/CIP-0119/README.md#",
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
            "Role": "CIP119:RoleReference",
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
        "uri": "web+cardano://stake?d9e2d181dfe21ab2ca7e95847b9a219e691ee1366d22569712390655"
      }
    ]
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
   `web+cardano://drep?drep1ytc6867ae0xmkekvmex79r9akyy28eu8nu03jf3xu9fle6c82l4ex`
   (last character changed, checksum fails), or with
   `web+cardano://stake?BKIND` (a ticker), or with an identifier in uppercase
   or mixed case, or with a label of spaces only. Result: invalid, ignored.
   The same reference in an object that carries the key `uri` twice: the
   document is invalid, relation unknown.
6. **Wrong direction.** A DRep document with a `Role` reference to a `drep`
   URI. Result: invalid, ignored.
7. **Retired pool.** D declares pool P, and P's retirement epoch is the
   reading epoch or earlier. Result: invalid at that epoch, ignored. If P
   registered again after announcing the retirement and before the reading
   block, P is not retired and the reference is valid. A committee member
   whose expiration epoch is the reading epoch is still current.
8. **Former member.** D declares
   `web+cardano://cc?cc_cold1ztwq6mh5jkgwk6yq559qptw7zavkumtk7u2e2uh6rlu972slkt0rz`,
   whose term ended in epoch 653. Reading in epoch 664: declared, former
   member.

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
