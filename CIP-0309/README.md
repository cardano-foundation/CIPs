---
CIP: 309
Title: Proof of Existence Transaction Metadata
Category: Metadata
Status: Proposed
Authors:
  - Igor Shubovsky <igor@cardanowall.com>
Implementors:
  - CardanoWall <https://github.com/cardanowall>
Discussions:
  - https://github.com/cardano-foundation/CIPs/pull/?
Created: 2026-06-02
License: CC-BY-4.0
---

> Metadata **label 309** is reserved for "Proof of Existence record" in the
> [CIP-10 registry](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0010/registry.json)
> and is the load-bearing on-chain identifier for this specification. The CIP
> number 309 is a proposed alignment with that reservation; final assignment of
> the CIP number is the prerogative of the CIP editors during review.
> Implementations cite this specification by its on-chain label (309), so the
> proposed-versus-final distinction has no wire-format consequence.

This document is drafted against the
[CIP-0001 template](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0001/README.md)
so it can be submitted to `cardano-foundation/CIPs` with minimal editorial
change.

---

## Abstract

This CIP specifies the schema, algorithm registries, canonical encoding rules, and verification procedure for a **Proof of Existence (PoE)** record embedded in Cardano transaction metadata under metadata label **309** ("Proof of Existence record", reserved in [CIP-10](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0010/registry.json)). A PoE record commits one or more cryptographic content hashes to the chain; the block time of the transaction carrying the record is the authoritative witness that the content existed no later than that moment. Because the claim is content-addressed by a cryptographic digest, it is independent of where the content is hosted and of who published it.

A conformant verifier needs only the transaction metadata, optionally the content bytes, and a public blockchain explorer — **no issuer server, certificate authority, or trusted intermediary is required at any step**. Alongside the hash claim, the schema carries optional content-addressed discovery URIs (`ar://`, `ipfs://`), an OPTIONAL multi-recipient encryption envelope for off-chain ciphertext, OPTIONAL record-level [CIP-8](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0008/README.md) `COSE_Sign1` signatures, and supersedence pointers to prior records. Signatures attach at the record level only, are never required, and never name a publisher to trust. The record deliberately carries no filename, MIME type, title, description, free-form note, plaintext/ciphertext size field, issuer-identity field, certificate chain, or revocation primitive.

---

## Motivation: why is this CIP necessary?

A Proof of Existence is one of the simplest and most universally useful primitives an append-only public ledger can offer: "this content existed on or before this block." It underpins notarisation, intellectual-property timestamping, supply-chain attestation, journalism, and — with optional signatures — authorship attribution. Because the claim is content-addressed via a cryptographic hash, it is independent of where the content is hosted.

### Why Cardano native transaction metadata

A PoE is a structured cryptographic record — content hashes, optional encryption envelopes, optional signatures, optional URIs, optional supersedence pointers — not a single opaque blob. The substrate it anchors on materially affects how that structure is expressed and what it costs.

Cardano is unusually well-suited to a structured PoE record because its transaction metadata is a first-class, CBOR-structured, schema-agnostic field indexed by an integer label registered under [CIP-10](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0010/registry.json). Any transaction MAY carry any well-formed CBOR map under any label without invoking a script, without ABI-encoding, and without per-byte gas above the baseline transaction fee. CBOR natively supports raw byte strings, definite-length arrays, and integer-keyed maps — exactly the primitives a cryptographic record needs, with no base64 inflation for 32-byte digests and no JSON ambiguity at canonicalisation time.

By contrast:

- **Bitcoin** has no dedicated metadata field. `OP_RETURN` was introduced to mark a script output as unspendable, not as a metadata channel; community usage repurposed it. It is capped at 80 bytes per output and carries an unstructured byte sequence — sufficient for a single Merkle root, insufficient for a record that bundles multiple hashes, a signature envelope, and recipient slots in one transaction.
- **Ethereum** and EVM-compatible chains have no native metadata layer. Structured records are either ABI-encoded into smart-contract calldata (paying gas per byte and requiring contract-specific conventions) or written through a registry contract that inserts a trusted contract between writer and reader. Both add cost and indirection that Cardano metadata does not require.

This CIP uses Cardano's metadata facility where it is already strongest: structured, content-addressed, low-cost, script-free records carried natively in the transaction. The same record shape could in principle be mirrored on another substrate, but on the chains compared above it would require either a structural compromise (`OP_RETURN`) or a contractual indirection (calldata, registry contracts).

### What already exists and why it is insufficient

- **CIP-10** reserves label **309** for "Proof of Existence record" but leaves the schema unspecified. Prior ad-hoc PoE-like records on Cardano are not interoperable and are outside this CIP's scope.
- **CIP-20** (label 674) standardises a plain-text transaction message: no content-hash semantics, no algorithm identifiers, no storage references.
- **CIP-25 / CIP-68** standardise NFT metadata but presume a minting context (`policy_id` / `asset_name`) that a PoE does not have.
- **CIP-83** standardises encrypted transaction messages with weak default cryptography (AES-256-CBC + PBKDF2-10k + a fixed default passphrase) and a message-text-only scope.
- **CIP-100** uses JSON-LD and RDF canonicalisation, machinery disproportionate to a 32-byte hash claim.
- **CIP-170** anchors KERI-backed credential chains and assumes issuer identity and watcher networks — the opposite of what a generic PoE needs.
- **OpenTimestamps**, the **Ethereum Attestation Service**, **W3C Verifiable Credentials**, and **C2PA** each solve a related problem, but none meets all of: chain-only verifiability, issuer-agnosticism, storage-agnosticism, algorithm-agility, a post-quantum upgrade path, and deliberate simplicity.

### The five invariants

This CIP is written around five non-negotiable invariants:

1. **Content-first.** The cryptographic hash of the content is the primary assertion; every other field is metadata _about_ that hash.
2. **Issuer-agnostic.** Any wallet MAY publish a conformant PoE; a verifier does not need to trust the sender. Optional signatures bind a separate claim-author key and are never required.
3. **Storage-agnostic.** Content URIs are a plural list; no storage backend is privileged. The record is usable with no URI at all (hash-only PoE).
4. **Standalone-verifiable.** A verifier needs only the transaction metadata, optionally the content bytes, and public blockchain explorers. No issuer server is required at any step.
5. **Algorithm-agile.** Every cryptographic algorithm is referenced by a named identifier drawn from the extensible registries this CIP defines. Post-quantum protection of the sealed-PoE key path ships in v1 (the `mlkem768x25519` X-Wing hybrid KEM is registered alongside classical `x25519`); further post-quantum migration adds new identifiers without breaking existing verifiers.

---

## Conventions and terminology

The key words **MUST**, **MUST NOT**, **REQUIRED**, **SHOULD**, **SHOULD NOT**, **MAY**, and **OPTIONAL** in this document are to be interpreted as described in [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119) and [RFC 8174](https://www.rfc-editor.org/rfc/rfc8174) when, and only when, they appear in capitals.

**Notation.**

- **Byte strings** are shown as lowercase hexadecimal with no `0x` prefix; each pair of hex characters is one byte. Where a value is shown in **base64url** it is the unpadded form of [RFC 7515 §2](https://www.rfc-editor.org/rfc/rfc7515#section-2), and the encoding is named explicitly at that point.
- **CBOR** types follow [RFC 8949](https://www.rfc-editor.org/rfc/rfc8949): `bstr` denotes a byte string (major type 2, raw bytes — never a hex string inside CBOR), `tstr` denotes a text string (major type 3, valid UTF-8). Integers in CBOR are big-endian. Curve scalars and points follow each curve's native encoding ([RFC 7748](https://www.rfc-editor.org/rfc/rfc7748) little-endian for X25519; [RFC 8032](https://www.rfc-editor.org/rfc/rfc8032) little-endian seed for Ed25519).
- `<bytes:N>` denotes a typed byte string field of fixed length N bytes.

**Defined terms.**

- **Record body** — the single canonical-CBOR map that constitutes a PoE record, as obtained after reassembling the metadata-label-309 chunk array by byte concatenation (see [Canonical CBOR and metadata label 309 carriage](#canonical-cbor-and-metadata-label-309-carriage)). Every structural and cryptographic rule in this document operates on the reassembled record body, not on the chunk-array transport wrapper.
- **Item** — one entry in the record's `items` array: a content claim that carries one or more content hashes and OPTIONAL discovery URIs (see [Record model](#record-model)).
- **Content** — the bytes whose existence is attested. When an encryption envelope (`enc`) is present, "content" means the **plaintext** unless qualified.
- **Content hash** — a cryptographic digest of the content under a named hash algorithm from the hash registry [`../registries/hash-algorithms.json`](https://github.com/cardanowall/cip309/blob/main/registries/hash-algorithms.json); the primary claim of a PoE record.
- **Block time** — the time of the block containing the PoE transaction; the authoritative timestamp of the record. A PoE record carries no submitter-asserted timestamp.
- **Sealed PoE** — a PoE record whose content is encrypted off-chain, with the content-encryption key wrapped to one or more recipient public keys (or derived from a passphrase) through the on-chain `enc` envelope (see [Sealed PoE: multi-recipient encryption](#sealed-poe-multi-recipient-encryption)). The ciphertext lives at a content-addressed `ar://` or `ipfs://` URI.
- **Slot** — one recipient entry inside a sealed-PoE envelope, holding the key-encapsulation material and the wrapped content-encryption key for a single recipient public key (see [Sealed PoE: multi-recipient encryption](#sealed-poe-multi-recipient-encryption)).
- **Verifier** — software that checks a PoE record against this specification. Three roles are distinguished and defined in [Structural validation, verifier roles, and error codes](#structural-validation-verifier-roles-and-error-codes): a **structural validator** (a pure function over the record-body CBOR; no I/O, no signature cryptography, no decryption), a **public verifier** (fetches on-chain metadata, runs structural validation, and verifies record signatures; does not decrypt), and a **recipient verifier** (a public verifier that additionally holds a recipient KEM private key and performs sealed-PoE decryption plus plaintext-hash recomputation). Used without a qualifier, "verifier" denotes whichever role is relevant in context; prose that requires a specific role names it explicitly.

## Specification

The normative grammar for the record body is the CDDL schema in
[`../cddl/cip-309.cddl`](cip-309.cddl); per-component JSON Schemas in
[`../schemas/`](https://github.com/cardanowall/cip309/blob/main/schemas) mirror it for tooling. Algorithm identifiers are
drawn from the registries in [`../registries/`](https://github.com/cardanowall/cip309/blob/main/registries). Conformance
vectors are pinned under [`../conformance/`](https://github.com/cardanowall/cip309/blob/main/conformance). Where this prose
and the machine-readable grammar appear to differ, the grammar and the
conformance vectors are authoritative.

This section is organised as follows: the **record model** (this subsection)
defines the on-wire data shapes; [Canonical CBOR and metadata label 309
carriage](#canonical-cbor-and-metadata-label-309-carriage) defines how the
record body is serialised and transported on chain;
[Record-level signatures (COSE_Sign1)](#record-level-signatures-cose_sign1)
defines optional authorship signatures;
[Seed and key derivation](#seed-and-key-derivation),
[Sealed PoE: multi-recipient encryption](#sealed-poe-multi-recipient-encryption),
and [Algorithm registries and conformance profiles](#algorithm-registries-and-conformance-profiles)
define the cryptographic constructions; and
[Structural validation, verifier roles, and error codes](#structural-validation-verifier-roles-and-error-codes)
defines how a verifier processes a record and the error-code taxonomy it emits.

### Record model

#### Top-level structure

A PoE record **MUST** be placed under Cardano transaction metadata label `309`.
The label is reserved in the [CIP-10 registry](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0010/registry.json)
as "Proof of Existence record"; this CIP formalises its schema. A transaction
**MAY** carry additional metadata under other labels (for example a CIP-20 `674`
message); a verifier **MUST** ignore metadata under labels other than 309 when
processing PoE.

A transaction **MUST NOT** contain more than one PoE record. This is a natural
property of Cardano metadata, which is a map from integer label to value.

The PoE **record body** under label 309 is a CBOR map. Integer values denote
CBOR major type 0/1; strings denote major type 3 and **MUST** be valid UTF-8;
bytes denote major type 2; arrays denote major type 4; maps denote major type 5.
Keys marked **REQUIRED** are mandatory; keys marked **OPTIONAL** **MUST NOT**
appear with an empty value. The on-chain serialisation and the ≤ 64-byte
chunked carriage of this body are specified in
[Canonical CBOR and metadata label 309 carriage](#canonical-cbor-and-metadata-label-309-carriage);
everything in this subsection operates on the reassembled record-body bytes.

```
{
  "v":          1,                       ; REQUIRED — schema version (this CIP defines v=1)
  "items":      [ <item>, ... ],         ; OPTIONAL — array of item entries; see the "items OR merkle" invariant below
  "merkle":     [ <merkle-commit>, ... ] ; OPTIONAL — non-empty array of list commitments
  "supersedes": <bytes:32>,              ; OPTIONAL — tx hash of a prior PoE (see "Supersedence" below)
  "sigs":       [ <sig-entry>, ... ],    ; OPTIONAL — record-level signatures
  "crit":       [ <tstr>, ... ]          ; OPTIONAL — extension keys mandatory-to-understand
}
```

A conformant PoE record **MUST** commit to at least one of `items` (with ≥ 1
entry) or `merkle` (with ≥ 1 entry); a record carrying neither is rejected as
`SCHEMA_EMPTY_RECORD`. When `items` is present it **MUST** be a non-empty array
(an empty `items[]` is rejected as `SCHEMA_EMPTY_RECORD`); the same non-empty
rule applies to `merkle`. Neither `items` nor `sigs` carries a numeric cap on
entry count: the only ceiling is the live Cardano `maxTxSize`, and producers pay
per-byte fees that naturally bound record size. A structural validator
**MUST NOT** reject a record solely on the basis of a high entry count below
`maxTxSize`.

The total byte size of a label-309 record is bounded by the live Cardano
protocol parameter `maxTxSize` (16 384 bytes at protocol version 9 on mainnet,
subject to ledger parameter updates). This is the **only** size cap this CIP
imposes — the schema itself has no hard byte ceiling beyond what the ledger
enforces at submission time. Records that exceed `maxTxSize` are rejected by
Cardano nodes before any verifier sees them; a structural validator **MAY** emit
an advisory warning for records approaching the limit, but **MUST NOT** impose a
size cap below `maxTxSize`.

#### Exact-bytes scope of a PoE claim

A record commits a digest over a specific byte sequence — the exact bytes that
were hashed at publication time. The record makes **no claim** about higher-level
"document identity" beyond those bytes. Two files that a human would call "the
same document" produce different digests if their bytes differ in any way,
including (non-exhaustive): line-ending differences (`LF` vs `CRLF`); Unicode
normalisation differences (NFC vs NFD vs unnormalised input); PDF producer
metadata, modification timestamps, or incremental-save trailers; image container
metadata (EXIF, XMP, IPTC) and re-saves that rewrite headers without touching
pixel data; archive container variations (ZIP / gzip timestamps, ordering,
compression level); and trailing whitespace, BOM presence, or comment
normalisation in source files.

Canonicalisation of higher-level content (PDF/A normalisation, source-code
formatting, JSON canonicalisation, archive-stripping, etc.) is **out of scope**
of this CIP and is the producer's responsibility. Tooling that constructs PoE
records **SHOULD** document the exact byte form it hashes (e.g. "hashes the file
on disk byte-for-byte"; "first canonicalises JSON via [RFC 8785](https://www.rfc-editor.org/rfc/rfc8785),
then hashes") so verifiers can reproduce the input. UI consumers **SHOULD**
surface the on-record hash digests rather than file names; matching is by digest,
not by human-readable identity.

#### Version literal

`v` is a CBOR unsigned integer, not a semantic version string. This CIP defines
exactly `v == 1` (the literal integer `1`). A structural validator **MUST**
reject records with `v` outside its supported set with a typed error
(`SCHEMA_INVALID_LITERAL`); it **MUST NOT** panic, abort, or treat such a record
as a different metadata schema. The `v` integer bumps only when a change would
cause v1 parsers to misinterpret the record.

#### Forward compatibility and critical extensions

This CIP reserves the closed set of top-level base keys above: `v`, `items`,
`merkle`, `supersedes`, `sigs`, `crit`. A record **MAY** additionally carry
**extension keys** whose names match the regular expression `^x-.+` (vendor /
experimental namespace) or `^[a-z]+-.+` (companion-CIP namespace; the prefix
identifies the registering CIP).

A v1 structural validator **MUST** decode and preserve extension keys, **MUST
NOT** reject the record solely on their presence, and **MUST** surface them
informationally in the validation report without claiming verification of their
contents. Extension keys are part of the signed record body for signature
purposes (see [Record-level signatures (COSE_Sign1)](#record-level-signatures-cose_sign1)):
a record-level signature covers the entire record map minus `sigs[]`, including
any extension keys, so a relay or indexer cannot inject an extension key after
the signature has been produced.

A producer that requires a verifier to understand a non-base field **MUST** list
its name in a top-level `crit: [+ tstr]` array. A v1 verifier seeing any `crit`
entry it does not implement **MUST** emit `EXTENSION_UNSUPPORTED_CRITICAL` and
**MUST NOT** report `valid: true`.

Each entry in the top-level `crit` array **MUST** satisfy three structural rules:
(a) the entry's text value **MUST** match the extension-key pattern (`^x-.+` or
`^[a-z]+-.+`) — base keys **MUST NOT** appear in `crit[]`; (b) the entry **MUST**
be present as a key in the record map — a `crit` entry naming a field absent from
the record **MUST** be rejected; (c) duplicate entries **MUST** be rejected.
Violations emit `CRIT_SHAPE_INVALID`.

Unknown top-level keys that do **not** match either extension-key pattern (e.g.
typos of base names like `"supersedess"` or case variants like `"Sigs"`)
**MUST** be rejected as `SCHEMA_UNKNOWN_FIELD`. The pattern-based tolerance
preserves producer-side typo detection for the base set while opening a stable
namespace pool for future additions. Companion CIPs that move features out of
the base spec register their namespace prefix in a companion-CIP registry
(initial content: empty) and do **not** bump the top-level `v` — additive fields
under a registered namespace are not a v1-breaking change.

(IETF precedents: [RFC 9052 §3.1](https://www.rfc-editor.org/rfc/rfc9052#section-3.1)
COSE `crit`; [RFC 7515 §4.1.11](https://www.rfc-editor.org/rfc/rfc7515#section-4.1.11)
JWS `crit`; [RFC 7517 §4](https://www.rfc-editor.org/rfc/rfc7517#section-4) JWK
must-ignore.)

#### Item entries

Each `<item>` in the `items` array is a CBOR map:

```
{
  "hashes": {                       ; REQUIRED — non-empty CBOR map of <hash-alg-id> → <digest>
    "<hash-alg-id>": <bytes:32>,    ;   key = algorithm id; value = raw digest bytes
    ...                             ;   one entry per algorithm; no duplicates (CBOR map keys are unique)
  },
  "uris":   [ <uri-chunk-array>, ...], ; OPTIONAL — list of discovery URIs
  "enc":    <encryption-envelope>   ; OPTIONAL — sealed-PoE envelope. When present, the
                                    ;   item MUST also carry at least one content-hash entry in `hashes`.
}
```

v1 has **no per-item signature slot**. Authorship is expressed exclusively
through optional record-level signatures (see
[Record-level signatures (COSE_Sign1)](#record-level-signatures-cose_sign1)),
which cover every item entry in the record.

`hashes` is a non-empty **CBOR map** whose keys are hash-algorithm identifiers
(CBOR text strings from [`../registries/hash-algorithms.json`](https://github.com/cardanowall/cip309/blob/main/registries/hash-algorithms.json))
and whose values are 32-byte digests (CBOR byte strings, not hex-encoded). Every
entry in `hashes` commits to plaintext bytes: the value is the raw digest of the
plaintext content under that algorithm. The map form has three byte-level
consequences that are part of the spec contract:

- **Duplicate algorithms are impossible by construction.** CBOR map keys are
  unique per [RFC 8949 §3.1](https://www.rfc-editor.org/rfc/rfc8949#section-3.1);
  a record carrying two entries for the same algorithm is malformed CBOR (caught
  by canonical-CBOR decoding with duplicate-key rejection, surfaced as
  `MALFORMED_CBOR`).
- **Canonical ordering is automatic.** Canonical CBOR (see
  [Canonical CBOR and metadata label 309 carriage](#canonical-cbor-and-metadata-label-309-carriage))
  sorts map keys by the bytewise lexicographic order of their CBOR encoding. For
  the v1 hash registry, that yields `sha2-256` (CBOR major-type-3 length prefix
  `0x68`) before `blake2b-256` (`0x6b`). Two producers expressing the same
  logical hash set always emit byte-identical `hashes` maps, so signatures over
  the record body are stable across implementations.
- **No per-entry shape validation is needed.** The wire form is `text → bytes`;
  the structural validator checks key membership in the registry and value length
  per algorithm. There is no `{alg, h}` sub-map to close.

**Producer obligation:** every digest in `hashes` **MUST** be the digest of the
same plaintext byte sequence under its named algorithm; producing a record where
multiple entries describe different plaintexts is non-conformant. **Consumer
obligation when plaintext is available:** the consumer **MUST** recompute every
entry against the recovered plaintext and reject the record if any digest fails
to match. A public verifier processing a sealed record without a recipient key
holds no plaintext and therefore cannot perform content-hash recomputation; the
AEAD tag at decrypt time, plus the recipient verifier's post-decryption hash
recomputation (see
[Structural validation, verifier roles, and error codes](#structural-validation-verifier-roles-and-error-codes)),
are what enforce the producer obligation in that case.

`hashes` **MUST** contain at least one entry from the registry (the non-empty
CBOR map invariant in [`../cddl/cip-309.cddl`](cip-309.cddl)). A
single-entry record is fully conformant; producers **MAY** add a second entry
from a distinct hash family (e.g. `sha2-256` paired with `blake2b-256`) as
optional defense-in-depth against future cryptanalytic progress against one
family, but this is not required and structural validators **MUST NOT** emit a
warning for single-entry records (see [Hash algorithms](#hash-algorithms)).

If `uris` is present it **MUST** be a non-empty array, and each entry **MUST**
itself be a chunked text array (the chunking shape defined in
[Canonical CBOR and metadata label 309 carriage](#canonical-cbor-and-metadata-label-309-carriage)).
The chunking shape exists because Cardano transaction metadata limits **every**
CBOR text string to 64 bytes — a ledger-level constraint, not a convention of
this CIP. A single logical URI that exceeds 64 bytes (e.g. an `ipfs://<CIDv1>`)
**MUST** be split into a chunked-text array of byte-bounded pieces; consumers
reconstruct the URI by concatenating chunks in order. A single-URI item uses the
array form `[ ["ar://example-txid"] ]` (an outer one-element array whose single
element is itself a one-chunk array).

Reconstructed URIs **MUST** be absolute per
[RFC 3986 §4.3](https://www.rfc-editor.org/rfc/rfc3986#section-4.3) — they
**MUST** include a scheme and a hierarchical part, and **MUST NOT** contain a
fragment identifier (the `#` character is forbidden because PoE is a claim about
content bytes, not about a sub-component of a document). The v1 URI scheme
registry is:

| Scheme    | Self-authenticating | Notes                                                                                                                                                                                                                                                                    |
| --------- | ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `ar://`   | Yes                 | Arweave transaction id (43-char base64url). Form: `ar://<txid>`. Typically fits in one chunk.                                                                                                                                                                            |
| `ipfs://` | Yes (via CID)       | IPFS CIDv1 preferred. Form: `ipfs://<cid>` or `ipfs://<cid>/<path>` (the path navigates within the CID's DAG per standard IPFS URI semantics; the CID commits the entire DAG). CIDv1 base32 plus any path often exceeds 64 bytes and **MUST** then use multi-chunk form. |

The v1 fetch set is exactly `{ar://, ipfs://}` — content-addressed schemes only.
Producers **MUST NOT** emit URIs with any other scheme (`https://`, `http://`,
`file://`, `ftp://`, `data:`, etc.). PoE uses content-addressed storage
exclusively: each URI is bound to the referenced bytes by the storage layer's
integrity model — IPFS CIDs are direct multihashes of the content; Arweave
transaction IDs commit to the data via the signed transaction's `data_root` (a
Merkle root over the chunks) under Arweave consensus. Verification therefore does
not depend on host trustworthiness or availability beyond the storage layer. A
conformant structural validator **MUST** reject any reconstructed URI whose
scheme is not in `{ar://, ipfs://}` with `INVALID_URI`; this fails records before
any verifier-side network step. The closed set is a deliberate design choice, not
a temporary restriction — see
[Rationale: how does this CIP achieve its goals?](#rationale-how-does-this-cip-achieve-its-goals)
for the adoption trade-off.

An item entry **MAY** list multiple URIs (one outer-array entry per URI). This is
a **producer obligation**: at publication time, every listed URI **MUST** resolve
to plaintext bytes that satisfy the record's hash assertions (for unencrypted
entries) or to ciphertext bytes that decrypt to plaintext bytes satisfying those
assertions (for encrypted entries).

`uris` is **OPTIONAL** throughout — including when `enc` is present. A hash-only
PoE with `uris` omitted remains a valid claim (the record makes a
content-existence assertion without committing to a retrieval channel). A sealed
PoE with `uris` omitted is **also** valid: the producer expects ciphertext to be
delivered out-of-band rather than published on a public storage layer. In that
case the **structural** record is well-formed and structural validation passes;
a verifier with neither a URI nor local ciphertext input for an `enc`-bearing
item emits a verifier-layer error (see
[Structural validation, verifier roles, and error codes](#structural-validation-verifier-roles-and-error-codes))
rather than `valid: true`. This preserves the storage-agnostic invariant: where
the ciphertext is stored is a deployment decision, not a wire-format requirement.

When `enc` is present, every URI listed in the item points to ciphertext bytes.
Decrypting those bytes **MUST** yield exactly the original plaintext content bytes
and nothing else: no container, no embedded manifest, no encrypted metadata
wrapper. A recipient determines file type, extension, and preview safety from the
decrypted bytes themselves (for example by magic-byte detection) or by
out-of-band context. The full sealed-PoE construction is defined in
[Sealed PoE: multi-recipient encryption](#sealed-poe-multi-recipient-encryption).

#### Hash algorithms

A Proof of Existence is most often challenged via second-preimage resistance. For
all 256-bit hashes in [`../registries/hash-algorithms.json`](https://github.com/cardanowall/cip309/blob/main/registries/hash-algorithms.json),
known second-preimage attacks are at or near `2^256` classical / `2^128` Grover —
a single sound 256-bit hash already covers the realistic threat model. This CIP
therefore requires `hashes` to carry **at least one** entry per item; single-hash
records are fully conformant.

The v1 content-hash registry is:

| Identifier    | Digest length | Reference                                                                |
| ------------- | ------------- | ------------------------------------------------------------------------ |
| `sha2-256`    | 32 bytes      | [FIPS 180-4](https://csrc.nist.gov/pubs/fips/180-4/upd1/final) (SHA-256) |
| `blake2b-256` | 32 bytes      | [RFC 7693](https://www.rfc-editor.org/rfc/rfc7693) (BLAKE2b-256)         |

Both produce a 32-byte digest, fitting trivially in a single CBOR byte string.
A digest of any other length under one of these identifiers is rejected as
`HASH_DIGEST_LENGTH_MISMATCH`; an unregistered identifier is rejected as
`UNSUPPORTED_HASH_ALG`.

Producers **MAY** include multiple hashes from distinct design families in the
same item entry as optional defense-in-depth against future cryptanalytic
progress against one family (cf. MD5, SHA-1). `sha2-256` (SHA-2:
Merkle–Damgård / Davies–Meyer) and `blake2b-256` (BLAKE2: HAIFA over a
ChaCha-derived permutation) are independent families — a record listing both is
impugned only if both families break concurrently. This is a producer-side
trade-off (one extra 32-byte digest plus a short identifier) and is **not**
required by v1.

#### Top-level list commitments (`merkle[]`)

`merkle[]` is an OPTIONAL top-level array of list commitments, peer to `items`
and `sigs`. Each commitment binds the record to an ordered list of 32-byte leaves
via a canonical hash-tree construction. A single label-309 record **MAY** carry
multiple list commitments — a CI artefact set, an IoT event batch, and an
audit-log root may share one transaction.

A `merkle[i]` entry is a closed CBOR map:

| Field        | Type                | Status   | Semantics                                                                                                                                                  |
| ------------ | ------------------- | -------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `alg`        | tstr                | REQUIRED | Registered list-commitment algorithm identifier (see [`../registries/merkle-commitment-algorithms.json`](https://github.com/cardanowall/cip309/blob/main/registries/merkle-commitment-algorithms.json)) |
| `root`       | bytes .size 32      | REQUIRED | Canonical root over the producer's ordered leaf list                                                                                                       |
| `leaf_count` | uint                | REQUIRED | Number of leaves committed by `root` (binds the on-chain commitment to the off-chain leaves-list size)                                                     |
| `uris`       | [+ uri-chunk-array] | OPTIONAL | Content-addressed URI(s) at which the off-chain leaves-list file is fetchable                                                                              |

The v1 merkle-commitment registry holds one identifier:

| Identifier       | Root length | Construction                                                                                                                                                                                                                                                                                                                                                                                           |
| ---------------- | ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `rfc9162-sha256` | 32 bytes    | Binary Merkle tree per [RFC 9162 §2.1.1](https://www.rfc-editor.org/rfc/rfc9162#section-2.1.1), using SHA-256. A `0x00` byte prefixes each leaf input (`leaf = SHA-256(0x00 ‖ d)`) and a `0x01` byte prefixes each internal-node input (`internal = SHA-256(0x01 ‖ L ‖ R)`), which prevents second-preimage attacks that swap a leaf for an internal node. The root is the SHA-256 output of the tree. |

`root` **MUST** be 32 bytes; any other length is rejected as
`HASH_DIGEST_LENGTH_MISMATCH`. An unregistered `alg` is rejected as
`UNSUPPORTED_MERKLE_COMMIT_ALG`. `leaf_count` **MUST** be a uint ≥ 1.

The REQUIRED `leaf_count` field commits the leaf count to the chain alongside
the root. A verifier comparing the on-chain `merkle[i].leaf_count` against an
off-chain leaves-list whose own leaf count disagrees emits
`SCHEMA_MERKLE_LEAF_COUNT_MISMATCH` and rejects the record. The leaf count is a
small integer (≈ 2–3 wire bytes) that removes an entire class of
off-chain-substitution attacks (rebuilding a tree of different size that happens
to share a root for a particular leaf-position selection).

A Merkle root commits to a leaf-list structure; a `sha2-256` / `blake2b-256`
entry commits to plaintext bytes. The two compose with `enc` differently
(content hashes are recomputed after decrypt; Merkle roots are verified via
inclusion proof), so the list-commitment array is a separate top-level field
rather than an `items[i].hashes` entry. This keeps the two surfaces clean and
lets a verifier dispatch on commitment kind by field rather than by registry
lookup.

A single on-chain root binds an arbitrary-size off-chain leaf list; per-leaf
inclusion proofs let auditors verify any subset without re-publishing the whole
list. Two properties follow that a plain content hash cannot provide:

1. **Scale.** A 500-file CI-artefact set, a 100 000-event IoT stream, or any
   batch larger than `items[]` could carry directly all reduce to a single
   32-byte root and one transaction.
2. **Selective disclosure (witness-hiding).** The on-chain root reveals nothing
   about the leaves; the producer chooses which leaves (if any) to reveal later,
   and the rest remain private even after some are disclosed.

The construction is order-sensitive: permuting the leaf list yields a different
root, so producers **MUST** treat the leaf list as an ordered sequence (not a
set) and preserve its order across record publication, archival, and any
subsequent inclusion-proof generation.

Verifying a specific leaf is an inclusion-proof check against `merkle[i].root`,
not a hash-of-plaintext recompute. The plaintext-hash recomputation step
iterates `items[i].hashes` only; `merkle[]` is verified by the per-leaf
inclusion-proof path.

**Off-chain backup discipline.** The 32-byte root on chain is useless without an
off-chain record of the leaf list. Producers **MUST** persist the ordered leaf
list alongside the transaction reference. The recommended pattern is to publish
the leaves-list file at the same content-addressed URI listed in
`merkle[i].uris`; a verifier resolves the URI, parses the leaves-list document
(canonical CBOR form is normative; a JSON projection is informative only),
recomputes the canonical root, and matches it against `merkle[i].root`
byte-for-byte. A `merkle[i]` entry that omits `uris` denotes a producer-only
commitment with no public leaf list: the leaves-list bytes remain in producer
custody and verification is possible only when the producer (or a recipient the
producer entrusts) supplies the bytes out-of-band. Loss of the leaf list renders
the on-chain commitment unverifiable for any specific leaf.

**Scale-out for high-volume trees.** For producers committing to more than
approximately 100 000 leaves (CI/CD timestamping pipelines, IoT event
aggregators, archival institutions), implementers **SHOULD** use the
[C2SP `tlog-tiles`](https://github.com/C2SP/C2SP/blob/main/tlog-tiles.md) sharded
directory format and point `merkle[i].uris[]` at the
[`tlog-checkpoint`](https://github.com/C2SP/C2SP/blob/main/tlog-checkpoint.md)
file instead of a monolithic leaves-list file, reducing single-leaf
inclusion-proof verification from `O(n)` to `O(log n)`. Conformant verifiers are
**NOT** required to implement `tlog-tiles` parsing in v1; a verifier that fetches
a checkpoint it cannot parse reports `MERKLE_UNSUPPORTED` at the OPT-INFO
conformance tier, with severity governed by the escalation rule in
[Algorithm registries and conformance profiles](#algorithm-registries-and-conformance-profiles):
`info` when the record also carries an `items[i].hashes` claim the verifier
validates, `error` for merkle-only records. A successor revision **MAY** register
a normative tlog-tiles binding once production experience accumulates.

**`merkle[]` is independent of `items[]`.** The two top-level arrays are
orthogonal: a record **MAY** carry `merkle[]` alone (a root-only attestation over
an off-chain leaf list), `items[]` alone (per-leaf content-hash commitments), or
both. The structural validator enforces no binding between a `merkle[i]` entry
and any `items[j]` entry — neither URI equality, nor leaves-list content-hash
pairing, nor any field-level cross-reference. A producer that wishes to also
commit to the byte content of the leaves-list file **MAY** include a separate
`items[j]` entry whose `hashes` map carries the leaves-list content hash; doing
so is a producer-side choice with no structural enforcement.

The byte-exact leaf-hash, internal-node-hash, single-leaf-identity, and
inclusion-proof verifier construction is defined alongside the cryptographic
primitives; the canonical leaves-list CBOR schema is the normative off-chain
format. Reference implementations and the pinned 4-leaf-tree vector (root plus
per-leaf inclusion proofs) live under [`../conformance/`](https://github.com/cardanowall/cip309/blob/main/conformance).

#### Supersedence

`supersedes` is an OPTIONAL 32-byte Cardano transaction hash pointing at one
earlier PoE record. It is a service-independent append-only link: a later record
can point at a prior record without relying on an off-chain database, indexer, or
vendor-specific record id. A `supersedes` value whose length is not exactly 32
bytes is rejected as `SUPERSEDES_TX_INVALID_LENGTH`.

A verifier resolving `supersedes` **MUST** look up the referenced transaction
hash on the **same Cardano network as the transaction containing the superseding
record**. The field carries no network discriminator because none is needed — the
containing transaction is itself anchored to a specific network, and the same
32-byte value on a different network is unrelated. A verifier configured with a
gateway for a different network than the containing transaction is a verifier
configuration error, not a record-level concern.

A record **MAY** declare that it supersedes an earlier-published PoE.
Supersedence does **not** remove, revoke, or invalidate the prior record; the
chain is append-only and verifiers **MUST** continue to treat the prior record as
existent and independently verifiable. This CIP deliberately does not include a
reason enum or free-text explanation. Human meaning such as correction,
replacement, addendum, withdrawal, or policy status belongs in the new content
itself or in an application layer outside label 309.

A record **MAY** be superseded by multiple later records; the latest by block
time is the most recent supersedence unless a UI chooses another policy.
Supersedence is vulnerable to abuse: an adversary who does not control the
author's keys can still publish a record whose `supersedes` value points at the
author's record. Verifiers and UIs **SHOULD** display supersedence only when the
superseding record is signed by a key also present in the superseded record (or
by a policy the UI defines).

`supersedes` is **transaction-granular**, not item-granular: a successor record
cannot reference an individual `items[i]` inside a prior record. Producers
needing per-item lifecycle **SHOULD** either (a) publish **one logical claim per
record** so each supersedence acts on a single semantic claim, or (b) carry
per-item lifecycle state in an in-content manifest. Per-item supersedence would
require either a stable per-item identifier across records (an off-chain index
this CIP declines to standardise) or an inline diff encoding (significantly more
wire-format complexity for a niche use case).

**Authoring convention — one logical claim per record.** The recommended
record-construction pattern is to publish **one logical claim per record** — one
document, one bundle, one event, one batch root. The `items[]` array supports
multiple item entries primarily for the case where a single logical claim spans
multiple files that share one signature scope (a build-artefact set, a
multi-file release bundle). For unrelated claims, prefer one record per claim:

- **Per-author granularity.** Each author's contribution is its own record signed
  under that author's record-level signature. N independent records with one
  record-level signature each is cleaner than one shared record with N per-item
  signatures — the v1 format intentionally has no per-item signature slot.
- **Per-claim supersedence.** `supersedes` is transaction-granular. A producer
  anticipating future correction, withdrawal, or extension of a specific claim
  **SHOULD** publish that claim in its own record so the eventual `supersedes`
  pointer acts on a single semantic claim. Bundling multiple unrelated claims
  into one record collapses their lifecycles.
- **Per-claim selective disclosure.** When some claims are sealed and others are
  public, mixing them in one record means the public verifier sees the existence
  of the sealed items even though their contents are private. Splitting into
  separate records keeps the public surface scoped to the public claim.

The cost of the split is one Cardano transaction fee per record (typically
sub-cent at protocol v9); the wire format imposes no penalty. The convention is a
recommendation, not a requirement: a record bundling multiple unrelated claims
under one signature is on-wire valid, but the producer's trade-off against future
supersedence granularity should be deliberate.

### Canonical CBOR and metadata label 309 carriage

A PoE record is a CBOR value. This section defines two things that every conformant producer and verifier MUST agree on bit-for-bit: the **canonical (deterministic) CBOR** profile in which the record body is serialised, and the **metadata label 309 transport** under which those bytes travel on the Cardano chain. The canonical form is simultaneously the on-wire form and the signing input — there is one serialisation of a record, not a separate "wire" and "signed" encoding.

#### Canonical CBOR (deterministic encoding)

The record body and every value derived from it (notably the record-level signing input defined in [Record-level signatures (COSE_Sign1)](#record-level-signatures-cose_sign1)) **MUST** be encoded as canonical CBOR per [RFC 8949 §4.2.1](https://www.rfc-editor.org/rfc/rfc8949#section-4.2.1) "Core Deterministic Encoding Requirements". Concretely, an encoder **MUST** satisfy all of the following, and a decoder **MUST** reject any input that violates them with `MALFORMED_CBOR` (see [Structural validation, verifier roles, and error codes](#structural-validation-verifier-roles-and-error-codes)):

1. **Preferred serialisation (shortest form)** for every integer. The smallest additional-information encoding that represents the value **MUST** be used; a non-minimal integer encoding is rejected.
2. **Definite-length encoding** for every byte string, text string, array, and map. **Indefinite-length** (streaming) encodings **MUST NOT** appear and **MUST** be rejected with `MALFORMED_CBOR`.
3. **Map keys sorted in bytewise lexicographic order of their CBOR encoding.** Because each key's encoding begins with its major-type-and-length header, this is equivalent to ordering keys first by encoded length and then bytewise. The text keys this CIP defines sort deterministically under this rule with no producer discretion.
4. **No duplicate keys** in any map. A map containing two entries whose keys encode to identical bytes is rejected.
5. **UTF-8 for all text strings**, with no byte-order mark. A text string that is not well-formed UTF-8 is rejected.
6. **No semantic tags** unless this CIP explicitly requires them — and this CIP requires none. A bignum tag (tag 2/3) **MUST NOT** be emitted; integer values that fit a fixed-width representation are encoded tag-free.
7. **No floating-point or non-trivial simple values.** A PoE record carries only unsigned/negative integers, byte strings, text strings, arrays, maps, and (where a schema admits it) the simple values `true`/`false`/`null`. Major-type-7 floats (including an integral-valued float such as `1.0`), negative zero, and `undefined` **MUST** be rejected rather than silently coerced; otherwise two byte sequences that are not byte-identical could canonicalise to the same record and break cross-implementation parity.

Map keys throughout this CIP are CBOR text strings (major type 3). The same canonical profile applies uniformly: there is no separate "lenient" reader for on-chain records. Explorers and wallets MAY expose transaction metadata through lossy JSON projections, but a conformant verifier **MUST** validate the original transaction CBOR bytes, never a re-encoded JSON view.

Signers and verifiers **MUST** agree on this canonicalisation bit-for-bit; implementations **SHOULD** use a CBOR library that supports RFC 8949 deterministic encoding natively. The complete grammar for the canonical record body is the CDDL at [`../cddl/cip-309.cddl`](cip-309.cddl); conformance vectors that pin exact canonical bytes are at [`../conformance/`](https://github.com/cardanowall/cip309/blob/main/conformance).

#### Metadata label 309 and the chunk-array transport

A PoE record **MUST** be placed under Cardano transaction metadata label `309`. A transaction **MUST NOT** carry more than one PoE record — a natural consequence of Cardano metadata being a map from integer label to value. A transaction **MAY** carry additional metadata under other labels; a verifier **MUST** ignore every label other than 309 when processing PoE.

The Cardano ledger caps **both** CBOR byte strings (`bstr`, major type 2) and text strings (`tstr`, major type 3) inside transaction metadata at **64 bytes each**. This is a ledger constraint, not a CIP-309 convention: a transaction carrying any single `bstr` or `tstr` longer than 64 bytes is rejected by Cardano nodes at submission time, before any verifier sees it. CIP-309 therefore transports any logical value that may exceed 64 bytes as a CBOR **array of ≤ 64-byte chunks**, reassembled by byte concatenation before decoding.

**Whole-record-body carriage.** The record body is serialised once to canonical CBOR per the rules above. That single byte string is then split into a CBOR **array of byte strings, each between 1 and 64 bytes inclusive** (`[ 1* bstr .size (1..64) ]`), and stored under label 309 as that array. A verifier **MUST byte-concatenate the array elements in order to reassemble the canonical record body before structural validation.** Chunk boundaries carry **no** semantic meaning. A label-309 value that is a single byte string (a body that fits within 64 bytes) is its own reassembled body; a bare CBOR map directly under label 309 (a degenerate body that fits the 64-byte map cap) is the body with no reassembly step. Everything in the rest of this document operates on the reassembled record-body bytes; the CDDL at [`../cddl/cip-309.cddl`](cip-309.cddl) describes that reassembled body, not the chunk-array transport wrapper.

The maximum byte size of a label-309 record is bounded only by the live Cardano protocol parameter `maxTxSize`. CIP-309 imposes no schema-level byte ceiling below it: records exceeding `maxTxSize` are rejected by Cardano nodes before any verifier sees them. A structural validator **MUST NOT** reject a record solely on the basis of size below `maxTxSize`, and **MUST NOT** reject on a high entry count below that ceiling; producers pay per-byte fees that naturally bound record size.

**Two chunked shapes.** The same ≤ 64-byte discipline appears in two named shapes used by individual fields, in addition to the whole-body carriage above:

| Shape               | Wire form                   | Element major type | Used by                                                                                                                                                                                                                                                                                                         |
| ------------------- | --------------------------- | ------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `bytes-chunk-array` | `[ 1* bstr .size (1..64) ]` | 2 (byte string)    | the chunked `COSE_Sign1` and the OPTIONAL chunked `COSE_Key` of a signature entry (see [Record-level signatures (COSE_Sign1)](#record-level-signatures-cose_sign1)); the chunked X-Wing `kem_ct` of a hybrid sealed slot (see [Sealed PoE: multi-recipient encryption](#sealed-poe-multi-recipient-encryption)) |
| `uri-chunk-array`   | `[ 1* tstr .size (1..64) ]` | 3 (text string)    | the inner element of an item's or Merkle commitment's `uris` list                                                                                                                                                                                                                                               |

In both shapes a consumer reconstructs the logical value by concatenating the chunks in order. The chunk-array wrapper is **always required regardless of length**: a value that fits a single 64-byte chunk **MUST** still be encoded as a length-1 array, never as a bare `bstr` or `tstr`. Producers **SHOULD NOT** split a value into more chunks than necessary; gratuitous over-chunking wastes bytes without benefit. Values exceeding 64 bytes **MUST** be split across multiple ≤ 64-byte chunks.

A structural validator **MUST** enforce, for every chunked shape:

- **Per-chunk size `[1, 64]` bytes.** A zero-length chunk is rejected with the same code as an oversized chunk (`CHUNK_TOO_LARGE`).
- **The non-empty-array invariant** — at least one chunk MUST be present.
- **The major-type discriminator** — a `bytes-chunk-array` chunk **MUST** be major type 2 and a `uri-chunk-array` chunk **MUST** be major type 3; a mismatch is `SCHEMA_TYPE_MISMATCH`.
- **UTF-8 integrity for `uri-chunk-array`.** A producer **MUST NOT** split a multi-byte UTF-8 codepoint across chunks, so the reconstructed concatenation is valid UTF-8. The canonical decoder already rejects any non-UTF-8 text string as `MALFORMED_CBOR` before reassembly; a concatenation that nonetheless fails to decode as valid UTF-8 surfaces as `INVALID_URI`.

The error codes named above are defined in [`../registries/error-codes.json`](https://github.com/cardanowall/cip309/blob/main/registries/error-codes.json) and in [Structural validation, verifier roles, and error codes](#structural-validation-verifier-roles-and-error-codes).

#### URI shape rules for chunked URIs

Each reconstructed `uri-chunk-array` resolves to exactly one **absolute** URI with no fragment, whose scheme is in the closed fetch set `{ ar://, ipfs:// }`. The following shape checks run on the reassembled URI string, offline, before any verifier-side network step, so a malformed URI fails at the earliest possible layer.

**Scheme case-folding.** The URI scheme is case-insensitive per [RFC 3986 §3.1](https://www.rfc-editor.org/rfc/rfc3986#section-3.1): `ar://`, `Ar://`, and `AR://` denote the same scheme. A validator **MUST** lowercase the scheme component before matching it against the fetch set and dispatching to the per-scheme body rules; a mixed-case scheme is therefore not rejected on case grounds, and its body **MUST** still be shape-checked. Only the scheme is case-folded — the remainder of the URI (the Arweave txid, the IPFS CID, any path) is matched **verbatim**, because those are case-sensitive content addresses where a lowercased character would name different bytes. Producers **SHOULD** emit lowercase schemes.

- **`ar://<txid>` (Arweave).** The reconstructed URI **MUST** match `^ar://[A-Za-z0-9_-]{43}$` — 43 base64url characters, no padding, encoding Arweave's 256-bit transaction id. A mismatch emits `INVALID_URI` (reason `ar_txid_shape`). A query string, path, or fragment on an `ar://` URI is forbidden; the txid alone is the content address.
- **`ipfs://<cid>[/<path>]` (IPFS).** The reconstructed URI **MUST** be `ipfs://` followed by a CID, optionally followed by a `/`-prefixed path. The CID commits the entire DAG, so a path component navigates within already-committed bytes and does not weaken integrity. A validator **MUST** perform the full offline CID parse — split authority from path at the first `/`, multibase-decode, read the version byte, then the codec and multihash varints — and enforce the CID profile below, emitting `INVALID_URI` (reason `ipfs_cid_unsupported`) for any CID outside the profile. The parse is purely offline, so this mandate applies even to deployments that decline to fetch IPFS content; such a deployment accepts a well-formed CID structurally and then refuses every `ipfs://` URI at fetch time with `URI_TARGET_FORBIDDEN`.

These structural shape checks are independent of verifier-time fetch-policy checks: a URI that passes structural validation MAY still be refused at fetch time, but a URI that fails structural validation never reaches the fetch step.

#### CID profile

The phrase "valid CID" above resolves to the following normative profile. It constrains the multiformats space to a set small enough that every conformant validator can make deterministic accept/reject decisions, while preserving IPFS's self-authentication property (the URI binds the bytes via the multihash). Producers **MUST** emit only CIDs that fit this profile; validators **MUST** reject everything else with `INVALID_URI` (reason `ipfs_cid_unsupported`).

| Component                    | Accepted values                                                                                 | Notes                                                                                                                                                                                              |
| ---------------------------- | ----------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Version**                  | CIDv0, CIDv1                                                                                    | CIDv0 is the fixed shape `Qm…` (46-char base58btc, sha2-256 multihash, no path). New producers **SHOULD** emit CIDv1.                                                                              |
| **Multibase prefix (CIDv1)** | `b` (base32 lower), `B` (base32 upper), `f` (base16 lower), `F` (base16 upper), `z` (base58btc) | All other prefixes (e.g. `m`/`M` base64) **MUST** be rejected. Producers **SHOULD** prefer `b`.                                                                                                    |
| **Multicodec (CIDv1)**       | `0x55` (raw), `0x70` (dag-pb), `0x71` (dag-cbor)                                                | Covers single-file payloads (raw), directory roots for `ipfs://<cid>/<path>` (dag-pb), and structured payloads (dag-cbor). Other codecs **MUST** be rejected.                                      |
| **Multihash**                | `0x12` (sha2-256, 32-byte digest), `0xb220` (blake2b-256, 32-byte digest)                       | Mirrors the content-hash registry ([`../registries/hash-algorithms.json`](https://github.com/cardanowall/cip309/blob/main/registries/hash-algorithms.json)), so an implementer can reuse the same primitives. Other codes **MUST** be rejected. |

Future additions to this profile follow CIP-309's algorithm-agility model: any new multibase prefix, multicodec, or multihash code requires an amendment to this document and matching conformance vectors before a producer may emit it.

### Record-level signatures (COSE_Sign1)

Authorship in CIP-309 is an **opt-in claim, never a requirement.** A record
verifies as a Proof of Existence on the strength of its content hashes and the
block time of its transaction alone; a signature adds _who attests to this
record body_, and its absence does not weaken the existence claim. CIP-309 v1
defines exactly one signature level — **record-level** — carried in the
top-level `sigs` field. There is **no per-item signature slot**: a single
`COSE_Sign1` covers the entire record body uniformly (every item, every Merkle
commitment, every URI, the encryption envelope, the supersedence pointer if
present, and any extension keys).

A verified signature binds the **record body only.** It proves that the named
public key produced an Ed25519 signature over the canonical CBOR of the record
(minus `sigs`), prefixed with a domain separator. It does **not** prove that the
signer submitted the carrying transaction, paid its fee, controls any wallet
associated with the transaction, or chose any particular block time. The signed
bytes are portable: an identical record body MAY be republished by any party in
any later transaction (see [Security and Privacy Considerations](#security-and-privacy-considerations)).

`sigs` is OPTIONAL. When present it MUST be a non-empty array of **sig-entry**
maps. The registered signature algorithms are listed in
[`../registries/signature-algorithms.json`](https://github.com/cardanowall/cip309/blob/main/registries/signature-algorithms.json).

#### Sig-entry shape

Each `sigs[i]` is a **closed CBOR map** carrying:

- `cose_sign1` — REQUIRED. A `COSE_Sign1` structure ([CIP-8](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0008/README.md),
  [RFC 9052](https://www.rfc-editor.org/rfc/rfc9052)), CBOR-encoded to a byte
  string, then chunked into an array of CBOR byte strings each between 1 and 64
  bytes (see [Canonical CBOR and metadata label 309 carriage](#canonical-cbor-and-metadata-label-309-carriage)).
  A verifier reassembles the `COSE_Sign1` by byte-concatenating the chunks
  before decoding.
- `cose_key` — OPTIONAL. A CBOR-encoded `COSE_Key` blob carrying the signer's
  **public** key, chunked with the same ≤ 64-byte shape. Present only on the
  CIP-30 wallet path (see [Signer-key identification](#signer-key-identification)).

```
sigs = [
  { "cose_sign1": [ <bytes ≤64>, ... ] },                                  ; in-signature kid (identity-key signer)
  { "cose_sign1": [ <bytes ≤64>, ... ], "cose_key": [ <bytes ≤64>, ... ] }, ; cose_key side-channel (CIP-30 wallet)
  ...
]
```

No other keys are permitted. A `sigs[i]` that is not a map, is a map with keys
other than `cose_sign1` / `cose_key`, or is missing `cose_sign1`, MUST be
rejected as `SIG_ENTRY_INVALID_SHAPE`. Entries are self-contained: each carries
(or does not carry) its own signer-key blob; there is no parallel array, no
`null` placeholder, and no cross-field length invariant.

#### Signed payload and Sig_structure

`sigs` is **excluded** from the signed payload. A signer computes:

```
record_body        = remove_keys(record_map, ["sigs"])
record_body_bytes  = canonical_cbor(record_body)
SIG_DOMAIN_RECORD  = utf8("cardano-poe-record-sig-v1")          ; 25 bytes
to_sign            = SIG_DOMAIN_RECORD || record_body_bytes      ; byte concatenation
Sig_structure      = [ "Signature1", cose_protected_bytes, h'', to_sign ]
signature          = Ed25519-Sign(canonical_cbor(Sig_structure), signer key)
```

`Sig_structure` is the 4-element CBOR array of [RFC 9052 §4.4](https://www.rfc-editor.org/rfc/rfc9052#section-4.4):

1. **`Sig_structure[0]`** is the CBOR text string `"Signature1"` (the RFC 9052
   §4.4 context identifier). Encoded as canonical CBOR it occupies exactly 11
   bytes — the major-type-3 / length-10 header `0x6a` followed by the 10 UTF-8
   bytes of `"Signature1"`. Producers and verifiers MUST emit and consume this
   full 11-byte encoding, not the bare 10 UTF-8 bytes.
2. **`Sig_structure[1]`** is `cose_protected_bytes` — the same byte string that
   appears as `COSE_Sign1[0]` (the bstr-wrapped, canonical-CBOR-encoded
   protected-header map). Because the protected header always carries at least
   the `alg` entry (see [Signing algorithm](#signing-algorithm)), it is never
   empty in a conforming v1 record. Verifiers MUST use the producer's
   `cose_protected_bytes` verbatim and MUST NOT re-canonicalise the protected
   header during verification.
3. **`Sig_structure[2]`** is `external_aad`. In v1 it is **ALWAYS the empty byte
   string** `h''`. The domain separator is embedded into `Sig_structure[3]`, not
   here, because [CIP-30](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0030/README.md)
   `signData` — the only realistic wallet-signing path on Cardano — explicitly
   stipulates that `external_aad` is not used. Embedding the separator into the
   payload preserves the anti-replay property while keeping wallet-produced
   signatures byte-identical to verifier-side recomputation.
4. **`Sig_structure[3]`** is `to_sign`: the 25-byte UTF-8 prefix
   `cardano-poe-record-sig-v1` concatenated with the canonical-CBOR-encoded
   `record_body`. Producers MUST prepend the prefix before passing the bytes to
   any signing primitive (including a CIP-30 `signData` payload); verifiers MUST
   prepend the same prefix before recomputing `Sig_structure`. The prefix is the
   sole cross-protocol replay defence: a future metadata schema that happens to
   share the body shape cannot reuse a CIP-309 signature against itself, because
   its `to_sign` would carry a different prefix (or none).

**Detached payload.** The published `COSE_Sign1[2]` (the payload field of the
outer 4-element `COSE_Sign1` array, RFC 9052 §4.2) MUST be CBOR `null` (`0xF6`).
Any attached payload — including a zero-length byte string `h''` — MUST be
rejected as `MALFORMED_SIG_COSE_SIGN1`. The detached form pins the signed bytes
to the canonical record body the verifier recomputes; an attached payload would
let a producer sign borrowed bytes while the COSE structure still validates.

**Signature-set scope.** Because `sigs` is removed before signing, each
`sigs[i]` covers `{ v, items?, merkle?, supersedes?, crit?, <extensions?> }`
(with the "at least one of `items` / `merkle`" invariant of the
[Record model](#record-model) ensuring a non-empty claim, and any extension keys
covered) but does **not** cover the rest of the `sigs` array. Each signer
attests that the body they signed is the same body every other entry is bound
to; no signer attests to _which_ other signers co-signed. Applications needing a
binding "this set of co-signers, and no others" claim MUST express it at the
application layer (e.g. by committing a roster inside `items[].hashes`), not by
reading it off `sigs`.

**Signatures are fixed at submission time.** All co-signers MUST contribute their
`COSE_Sign1` entry to `sigs` before the carrying transaction is submitted.
Rebroadcasting an identical `record_body` in a separate transaction with a
different `sigs` set creates a separate, independent record at its own block
time — not an extension of the original. Verifiers, indexers, and UI consumers
MUST NOT collapse two transactions with identical `record_body` bytes into a
single "merged signers" view.

#### Signing algorithm

The only signature algorithm in v1 is **Ed25519** ([RFC 8032](https://www.rfc-editor.org/rfc/rfc8032)).
Two COSE protected-header `alg` labels select it:

| `alg` | Identifier                                                                                                                      | Status                                                                                                                    |
| ----- | ------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| `-8`  | `EdDSA`, the curve-agnostic COSE label, pinned to Ed25519 ([RFC 9053 §2.2](https://www.rfc-editor.org/rfc/rfc9053#section-2.2)) | **Mandatory.** Every conforming verifier MUST accept it; it is the only `alg` CIP-30 wallets emit on the `signData` path. |
| `-19` | `Ed25519`, fully-specified ([RFC 9864 §3.1](https://www.rfc-editor.org/rfc/rfc9864#section-3.1) IANA assignment)                | **Optional.** Verified identically to `-8` under the same strict Ed25519 primitive when accepted.                         |

Both labels are recorded in
[`../registries/signature-algorithms.json`](https://github.com/cardanowall/cip309/blob/main/registries/signature-algorithms.json).
The `alg` MUST appear in the **protected** header.

**Unrecognised signature algorithms do NOT invalidate the record.** A `sigs[i]`
whose inner `COSE_Sign1` carries an `alg` the verifier does not implement is
reported per-entry as `SIGNATURE_UNSUPPORTED` (informational severity, with the
unsupported `alg` value surfaced for diagnostics); it is not a record-level
error. The content claim — the `items[i].hashes` commitment — is structurally
valid regardless of signature-algorithm support, so an indexer rendering a
record with only future-algorithm signatures still surfaces it as a valid PoE
claim. A verifier that does implement `-19` verifies it identically to `-8`.

**Strict, non-cofactored verification.** A public verifier MUST verify Ed25519
under [RFC 8032 §5.1.7](https://www.rfc-editor.org/rfc/rfc8032#section-5.1.7)
**strict** rules:

- Non-canonical encodings of `R` or `S` (notably `S ≥ ℓ`, the group order) MUST
  be rejected.
- Small-subgroup / torsion-component public keys and `R` values MUST be
  rejected.
- The cofactored verification equation (ZIP-215 form) MUST NOT be substituted;
  the unscaled equation `[S]B = R + [k]A` is required.

A signature that fails strict verification is reported as `SIGNATURE_INVALID`.
Implementations MUST select a library mode that performs strict, non-cofactored
verification — a cofactored verifier accepts records a conforming verifier
rejects and is therefore non-conformant for v1.

**CIP-8 `hashed` mode.** [CIP-8](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0008/README.md)
defines an OPTIONAL **unprotected**-header field `"hashed": bool`, intended for
hardware co-signers with limited screen or signing-buffer capacity. When a
producer sets `hashed = true`, the `Sig_structure[3]` slot is the 28-byte digest
`Blake2b-224(to_sign)` rather than `to_sign` itself; the rest of `Sig_structure`
(the `"Signature1"` context, the protected-header bytes, and the empty
`external_aad`) is unchanged. Verifiers MUST inspect the unprotected header for
`"hashed"` and, when its value is `true`, perform this substitution before
strict Ed25519 verification; when the field is absent or `false`,
`Sig_structure[3]` is `to_sign` as above. Producers SHOULD confine
`hashed = true` to records whose `to_sign` exceeds the device's signing-buffer
limits; software and SDK-driven producers SHOULD NOT emit `hashed = true`,
because it does not reduce on-wire size and complicates verifier code paths.

#### Signer-key identification

A `COSE_Sign1` MUST carry the signer's public key — or an unambiguous,
self-contained reference to it — so a public verifier can resolve the key
without contacting any service. There are exactly two permitted carry-forms in
v1, distinguished by which keys appear inside the same `sigs[i]` map. **They are
mutually exclusive at the wire level.**

**Path 1 — in-signature `kid` (RECOMMENDED; covers identity-key signers).** The
32-byte raw Ed25519 public key is placed at COSE header label `4` (`kid`,
[RFC 9052 §3.1](https://www.rfc-editor.org/rfc/rfc9052#section-3.1)) inside the
**protected** header of the `COSE_Sign1`. Putting `kid` in the protected header
binds the claimed key to the signature: an adversary cannot rewrite it without
invalidating the signature. The producer emits a `sigs[i]` with no `cose_key`
field. This is the path used by [seed-derived identity keys](#seed-and-key-derivation).

> **`kid`-as-public-key convention.** RFC 9052 §3.1 defines `kid` as an opaque
> key identifier — typically a pointer to look up a key out of band. CIP-309
> path 1 uses a more compact convention: when the protected-header `kid` is
> **exactly 32 bytes**, it _is_ the raw Ed25519 public key, not a pointer to
> one. The 32-byte size discriminator is unambiguous because Ed25519 public keys
> are always 32 bytes ([RFC 8032 §5.1.5](https://www.rfc-editor.org/rfc/rfc8032#section-5.1.5))
> and v1 forbids overlapping COSE_Key types in this role. Verifiers MUST accept a
> 32-byte protected-header `kid` as a directly-usable Ed25519 public key with no
> out-of-band lookup. This is what makes the in-signature path
> service-independent. It is a deliberate, documented deviation from typical COSE
> usage, with IETF precedent in carrying short, self-describing credential bytes
> inline ([RFC 9528 EDHOC §3.5.3](https://www.rfc-editor.org/rfc/rfc9528#section-3.5.3)).
> A successor revision MAY register a dedicated COSE header label for an inline
> raw Ed25519 public key; v1 does not gate submission on such an allocation.

**Path 2 — `cose_key` side-channel (covers CIP-30 wallet signers).** A
[CIP-30](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0030/README.md)
`signData` call returns the signer's public key as a separate `COSE_Key` blob
(not inside the `COSE_Sign1`) and places the wallet's stake-address binding in
the protected header as `"address"`. When chaining such a signature into a
record, the producer MUST place the wallet's `COSE_Key` blob (chunked) into the
**same** `sigs[i]` entry under the key `cose_key`. The `COSE_Key` describes an
Ed25519 public key: label `1` (`kty`) = `1` (OKP), label `-1` (`crv`) = `6`
(Ed25519), label `-2` (`x`) = the 32-byte public key. If `alg` (label `3`) is
present it MUST be `-8`.

**Public key only — never a private key.** `sigs[i].cose_key` MUST describe only
the public half of the key pair. Producers MUST NOT include any private-key
material (the OKP/EC2 `d` field, COSE_Key label `-4`, or any other private-key
label in the [IANA COSE Key Type Parameters registry](https://www.iana.org/assignments/cose)).
A structural validator MUST decode the chunked `cose_key` blob and MUST reject
any entry carrying a private-key-material label as `SIG_PRIVATE_KEY_LEAKED`. The
check is load-bearing in a producer-side preflight (it prevents the publication
entirely, the only context that can actually stop the leak) and advisory on a
public verifier reading already-published chain data (the key MUST be considered
compromised; the verifier reports the same code so downstream consumers do not
treat the signature as authoritative).

**Wallet `address` ↔ `cose_key` binding (path 2).** On the wallet path the inner
`COSE_Sign1` protected header places the wallet's stake address at label
`"address"` as a 29-byte byte string per [CIP-19](https://cips.cardano.org/cips/cip19/):
a 1-byte network header (`0xe1` mainnet, `0xe0` testnet) followed by the 28-byte
`Blake2b-224` hash of the stake verification key. The Ed25519 signature alone
proves only that the key in `cose_key` signed the record body — the `address`
field is otherwise an unverified claim. Verifiers MUST independently recompute
`address_derived = network_header_byte || Blake2b-224(pubkey)` from the resolved
32-byte public key and reject the signature with `WALLET_ADDRESS_MISMATCH` if
`address_derived` does not byte-equal the protected-header `address`. UI
consumers MUST NOT surface the stake address as authenticated metadata without
this check passing. v1 binds the wallet path to **stake (reward) addresses
only** — a non-stake-address-format `"address"` fails the recomputation and is
rejected as `WALLET_ADDRESS_MISMATCH`; producers using CIP-30 wallets MUST
request `signData` with a stake-address argument. Path-1 records carry no
`address` claim and skip this step.

**Mutual exclusion.** A `sigs[i]` entry MUST carry **either** a 32-byte
protected-header `kid` and no `cose_key` field (path 1), **or** a `cose_key`
field and no 32-byte protected-header `kid` (path 2) — never both. An entry
carrying both MUST be rejected as `SIG_ENTRY_KID_COSE_KEY_CONFLICT`. The rule
removes an on-wire ambiguity that would otherwise let a consumer mis-classify a
path-1 signer as a wallet signer.

**Resolution.** Because the paths are mutually exclusive, signer-key resolution
is a wire-level discrimination, not a ranked precedence:

1. If the protected header carries a 32-byte `kid`, that value IS the signer's
   raw Ed25519 public key.
2. Otherwise, if `sigs[i].cose_key` is present, byte-concatenate its chunks,
   decode as `COSE_Key`, and extract the Ed25519 public key from label `-2`. The
   protected header MAY carry a non-32-byte `kid` (e.g. a 29-byte stake address)
   as bound metadata, but that value is not the signer key.

A protected-header `kid` that is present but not exactly 32 bytes, with no inline
`cose_key`, leaves the verifier with no way to resolve the signer; such a record
is a producer-side conformance error and MUST be reported as
`SIGNER_KEY_UNRESOLVED`. A verifier that cannot resolve a signer key by either
path MUST likewise report `SIGNER_KEY_UNRESOLVED` rather than silently accept the
signature.

**Unprotected `kid` is not a resolution path.** An unprotected-header `kid` sits
outside the COSE integrity envelope, so an untrusted relay or indexer can rewrite
it in transit without invalidating the signature. Verifiers MUST ignore the
unprotected `kid` when resolving a signer key (it MAY be surfaced as a UI
diagnostic but MUST NOT be consulted for resolution). Producer tooling that emits
`kid` only in the unprotected header (some early wallet builds) MUST mirror the
value into the protected header before publication.

#### Reporting signature results

The resolved `kid` is **unauthenticated as a name.** A verified signature proves
only that "this byte string is the public key of whoever signed this record" —
not "this byte string is a particular person's key." UI consumers MUST display
the verified public key (or its short fingerprint) and MUST NOT assert "signed by
&lt;name&gt;" without an out-of-band binding through which the key bytes were
independently authenticated.

UI consumers MUST also report the signature's **scope** accurately. A verified
`sigs[i]` proves that `<pubkey>` produced an Ed25519 signature over the record
body (prefixed with the domain separator) — nothing more. Acceptable phrasings:
"Signed by &lt;pubkey&gt; (signature over record body)", "Author signature:
&lt;pubkey&gt;". Unacceptable phrasings: "Submitted by &lt;pubkey&gt;",
"&lt;pubkey&gt; published this on &lt;date&gt;".

### Seed and key derivation

A CIP-309 cryptographic identity is exactly one thing: a 32-byte master
seed. Every public-key fact a verifier or sender ever consumes — the
Ed25519 key that signs PoE records, the X25519 key that receives classical
sealed PoE records, and the `mlkem768x25519` (X-Wing) hybrid key that
receives post-quantum sealed PoE records — is **derived deterministically**
from that seed via HKDF-SHA-256 with three distinct, version-tagged context
strings. There is no hierarchical-wallet derivation, no per-record subkey,
and no chain-code state: a small fixed set of leaf keys is expanded directly
from the seed.

**This section specifies derivation only.** How the 32-byte seed is
generated, stored, unlocked, recovered, or rotated is an implementation
concern and is OUT OF SCOPE for this standard. The on-wire format depends
only on the 32 bytes themselves and on the HKDF expansion defined here; an
implementation MAY produce the seed from a platform CSPRNG, import it from a
user-managed backup, or source it from any other 32-byte entropy the user
controls. Two seeds that are byte-equal MUST derive byte-equal keys.

#### Master seed

| Property      | Value                                                                                                                                                                                                                                                                         |
| ------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Length        | 32 bytes (256 bits), REQUIRED exactly                                                                                                                                                                                                                                         |
| Type          | Opaque entropy — NOT a curve scalar, NOT an algorithm-specific key                                                                                                                                                                                                            |
| Validity      | Any 32-byte value is a valid input. Implementations MUST NOT reject a seed for low-entropy patterns at the derivation API; the all-zero seed is a valid input and is used by the conformance vectors (see [`../conformance/`](https://github.com/cardanowall/cip309/blob/main/conformance)) for byte-exact reproducibility |
| Re-derivation | Not applicable — no hierarchy, no per-purpose child keys beyond the three defined below                                                                                                                                                                                       |

The seed is a **bare entropy source**, not a key in any algorithm's sense.
Algorithms are selected per derivation; the seed outlives them.

#### HKDF-SHA-256 derivation

The three long-term keypairs are independent HKDF-SHA-256 expansions
([RFC 5869](https://datatracker.ietf.org/doc/html/rfc5869)) of the same
input keying material — the seed — distinguished **only** by their `info`
strings. For all three, the salt is the empty byte string and the requested
output length is 32 bytes.

```
ed25519_secret = HKDF-SHA-256(
  ikm    = seed,                       ; <bytes:32>
  salt   = "" (empty, zero-length),    ; absent salt per RFC 5869 §2.2
  info   = "cardano-poe-ed25519-v1",   ; 22 ASCII bytes
  length = 32 )                        ; → <bytes:32>, the Ed25519 secret seed (RFC 8032 §5.1.5)

x25519_secret = HKDF-SHA-256(
  ikm    = seed,                       ; same <bytes:32>
  salt   = "" (empty, zero-length),
  info   = "cardano-poe-x25519-v1",    ; 21 ASCII bytes
  length = 32 )                        ; → <bytes:32>, the X25519 secret seed (clamped inside the library per RFC 7748 §5)

mlkem768x25519_secret = HKDF-SHA-256(
  ikm    = seed,                            ; same <bytes:32>
  salt   = "" (empty, zero-length),
  info   = "cardano-poe-mlkem768x25519-v1", ; 29 ASCII bytes
  length = 32 )                             ; → <bytes:32>, the X-Wing decapsulation-key seed
```

The three `info` strings MUST be the exact ASCII byte sequences below — no
leading or trailing whitespace, no zero terminator, no byte-order mark, no
newline:

| Derived keypair                               | `info` string                   | Byte length |
| --------------------------------------------- | ------------------------------- | ----------- |
| Ed25519 (signing)                             | `cardano-poe-ed25519-v1`        | 22          |
| X25519 (encryption)                           | `cardano-poe-x25519-v1`         | 21          |
| `mlkem768x25519` / X-Wing (hybrid encryption) | `cardano-poe-mlkem768x25519-v1` | 29          |

The salt MUST be a zero-length byte string. Per
[RFC 5869 §2.2](https://datatracker.ietf.org/doc/html/rfc5869#section-2.2),
an absent salt is treated as `HashLen` zero bytes — for SHA-256, 32 zero
bytes. The requested HKDF expansion length MUST be 32 bytes for each of the
three derivations.

For all three, the 32-byte HKDF output is the **secret seed**, not the curve
scalar or expanded private key. RFC 8032 §5.1.5 distinguishes the two: the
Ed25519 _secret seed_ is 32 bytes, while the _expanded private key_ is
`SHA-512(seed)` (64 bytes). Implementations MUST treat the 32-byte HKDF
output as the canonical secret representation and pass it as-is to the
Ed25519 sign and X25519 ECDH primitives; the SHA-512 expansion and
bit-clamping happen inside the primitive.

##### Domain separation

The `info` parameter is HKDF's domain-separation tag (RFC 5869 §3.1).
Re-using the same key material across structurally different algorithms —
even when their secret-key widths coincide — is unsound: an
algorithm-specific failure (a nonce-derivation flaw in Ed25519, a
side-channel on X25519 scalar multiplication, a defect in X-Wing key
generation) MUST NOT be able to cross-contaminate the other keys. The three
distinct tags enforce that boundary. The `-v1` suffix is the rotation hook:
a future revision MAY introduce `-v2` tags adopting a different curve, key
length, or derivation step without colliding with deployed v1 keys.

The hybrid keypair-derivation label `cardano-poe-mlkem768x25519-v1` carries
NO `-kek-` segment; it is distinct from the KEK-derivation label
`cardano-poe-kek-mlkem768x25519-v1` used during sealed-PoE encryption (see
[Sealed PoE: multi-recipient encryption](#sealed-poe-multi-recipient-encryption)),
so identity-key derivation and per-record key wrapping never share an `info`
string.

#### The derived keypairs

##### Ed25519 — signing

| Aspect          | Value                                                                                                                          |
| --------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| Public key      | 32 bytes; published on chain inside the COSE_Sign1 `kid` (protected-header label `4`) of every record the user signs           |
| Public-key role | The signer identifier for record-level COSE_Sign1; verifiers compare the raw 32 public-key bytes, never a human-readable label |
| Private key     | The 32-byte HKDF output (secret seed); never published                                                                         |
| Algorithm       | Ed25519, RFC 8032; COSE alg `-8` (EdDSA)                                                                                       |

The Ed25519 key is consumed by record-level signatures (see
[Record-level signatures (COSE_Sign1)](#record-level-signatures-cose_sign1)).

##### X25519 — classical encryption

| Aspect          | Value                                                                                                                                         |
| --------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| Public key      | 32 bytes; the encryption target a sender obtains for a classical sealed PoE record                                                            |
| Public-key role | The recipient key for the `x25519` KEM. It is NOT carried on a PoE record's encryption block; recipients trial-decrypt with their private key |
| Private key     | The 32-byte HKDF output (secret seed); never published                                                                                        |
| Algorithm       | X25519 ECDH, RFC 7748 (the classical KEM `x25519`)                                                                                            |

##### `mlkem768x25519` (X-Wing) — hybrid encryption

| Aspect                 | Value                                                                                                                                                                            |
| ---------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Decapsulation-key seed | The 32-byte HKDF output IS the complete X-Wing decapsulation key (implicit-rejection construction); the public key and per-decapsulation working material are recomputed from it |
| Public key             | 1216 bytes (`ML-KEM-768 encapsulation key, 1184 B ‖ X25519 public key, 32 B`), derived deterministically from the 32-byte seed via X-Wing key generation                         |
| Public-key role        | The recipient key for the hybrid `mlkem768x25519` KEM                                                                                                                            |
| Private key            | The 32-byte decapsulation-key seed; never published                                                                                                                              |
| Algorithm              | X-Wing = ML-KEM-768 + X25519 with a SHA3-256 combiner                                                                                                                            |

The X-Wing **seed**, not the expanded decapsulation key, is the canonical
private form: the 1216-byte public key (and, on each decapsulation, the
working key material) is recomputed from the 32-byte seed. This mirrors the
seed-vs-expanded-key distinction applied to Ed25519 and X25519 above. The
hybrid KEM and its slot shape are specified in
[Sealed PoE: multi-recipient encryption](#sealed-poe-multi-recipient-encryption);
its registry entry is [`../registries/kem-algorithms.json`](https://github.com/cardanowall/cip309/blob/main/registries/kem-algorithms.json).

##### Published versus private — summary

| Material                      | Length | Published on the wire?                                  |
| ----------------------------- | ------ | ------------------------------------------------------- |
| Master seed                   | 32 B   | NO                                                      |
| Ed25519 secret seed           | 32 B   | NO                                                      |
| Ed25519 public key            | 32 B   | YES — inside the COSE_Sign1 `kid` of each signed record |
| X25519 secret seed            | 32 B   | NO                                                      |
| X25519 public key             | 32 B   | NO on a PoE record; published only out-of-band          |
| X-Wing decapsulation-key seed | 32 B   | NO                                                      |
| X-Wing public key             | 1216 B | NO on a PoE record; published only out-of-band          |

A recipient public key never appears on a CIP-309 PoE record. Each
encryption slot carries only per-slot key material and a wrapped CEK; the
KEM identifier appears once on the encryption block. Senders obtain a
recipient public key out-of-band; this standard mandates no single discovery
channel, and key provenance is the sender's responsibility.

#### Recipient public-key and secret encodings

A sealed-PoE sender needs the recipient's KEM public key in a portable
string form. CIP-309 reuses the age ecosystem's Bech32 encodings, one
human-readable prefix (HRP) per registered KEM. The HRPs are pinned in the
KEM registry [`../registries/kem-algorithms.json`](https://github.com/cardanowall/cip309/blob/main/registries/kem-algorithms.json).

| KEM              | Recipient public key     | Public-key encoding (HRP)                                            | Secret / identity encoding (HRP)                                                             |
| ---------------- | ------------------------ | -------------------------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| `x25519`         | 32 B X25519 public key   | `age1` — a standard age v1 recipient string (`age1…`, 62 characters) | `AGE-SECRET-KEY-` (uppercase Bech32), carrying the 32 B X25519 secret seed                   |
| `mlkem768x25519` | 1216 B X-Wing public key | `age1pqc` — `age1pqc…`, 1960 characters                              | `AGE-SECRET-KEY-PQ-` (uppercase Bech32), carrying the 32 B X-Wing decapsulation-key **seed** |

**The hybrid identity is the 32-byte X-Wing decapsulation-key seed**, not
the expanded key: the 1216-byte public key derives from the seed. The value
the `AGE-SECRET-KEY-PQ-` string carries is exactly the 32-byte output of the
third HKDF expansion above (`info = "cardano-poe-mlkem768x25519-v1"`). The
compact seed is always the value backed up and imported.

**The `age1pqc` HRP is deliberate.** The post-quantum recipient string
encodes a 1216-byte public key and is therefore far longer than the
[BIP-173](https://github.com/bitcoin/bips/blob/master/bip-0173.mediawiki)
90-character Bech32 cap. That cap exists for human-typed, error-correction-
bounded payment addresses and does NOT apply here: implementations MUST
encode and decode the `age1pqc…` string **without** enforcing the
90-character limit, while still applying the Bech32 checksum and charset
rules. The HRP is `age1pqc` (NOT `age1pq`) by design — the shorter `age1pq`
prefix is claimed by an upstream native ML-KEM-768 + X25519 encoding for the
same primitive, and the distinct `age1pqc` HRP guarantees the two recipient
encodings never collide on the wire. The classical `age1…` string stays
within ordinary lengths; its handling is unchanged.

Both encodings are recipient-discovery conveniences. The KEM public key
never appears on a CIP-309 PoE record; senders obtain it out-of-band and the
standard mandates no single discovery channel.

### Sealed PoE: multi-recipient encryption

A **sealed PoE** publishes a public, permanent, timestamped commitment to a
plaintext digest while keeping the plaintext itself readable only by an intended
audience. The on-chain record carries the plaintext hash (public, anchored to
block time) and an encryption envelope (`enc`) carrying the key-delivery
material; the **ciphertext** lives off-chain at a content-addressed URI (`ar://`
or `ipfs://`) and is undecryptable without a matching unlock secret. PoE alone
gives the time claim but no audience binding; PoE plus open ciphertext gives no
privacy. Sealed PoE bridges the two.

The construction is an **age-style multi-recipient KEM-then-wrap** design: a
single content-encryption key (CEK) encrypts the plaintext once, and that CEK is
independently wrapped to each recipient under a per-slot key. It is **not** RFC
9180 HPKE: there is no `suite_id`, no `LabeledExtract`/`LabeledExpand` cascade.
Reviewers SHOULD evaluate it against the ECIES/DHIES literature and the
[age v1 specification](https://github.com/C2SP/C2SP/blob/main/age.md), from which
its stanza pattern derives.

> This sealed-PoE ciphertext envelope is the **content** encryption layer. It is
> distinct from, and out of scope against, any local at-rest envelope a client
> might use to store an identity's private keys. Nothing in this section concerns
> private-key storage.

The encryption envelope defines **two mutually-exclusive key-delivery paths**,
discriminated by field presence (no explicit mode tag):

- **`enc.slots` — multi-recipient KEM path.** N independently-wrapped recipient
  slots; the ciphertext is undecryptable without a private key matching one of
  the slots. Specified byte-exact below.
- **`enc.passphrase` — passphrase-derived path.** No slots; the CEK is derived
  directly from a normalised passphrase via `argon2id`. Specified in
  [Passphrase path](#passphrase-path) below.

Both paths share `enc.scheme`, `enc.aead`, and `enc.nonce`; they differ in which
of `slots`/`passphrase` is present, and consequently in the content-AEAD AAD
rule. The grammar admits both as a permissive superset; the cross-field rules are
normative (see [Envelope shape and exclusivity](#envelope-shape-and-exclusivity)).

#### Envelope shape and exclusivity

The sealed-PoE envelope carries its own version integer, `enc.scheme`, separate
from the top-level record `v`. `enc.scheme` is the construction-**family**
version: it fixes the cross-KEM parts of the construction — the slot-set MAC
schedule and the content-AEAD AAD layout. The per-slot KEM is **not** selected by
`enc.scheme`; it is selected by the `enc.kem` field, which fixes the slot shape
and the per-slot KEK derivation. Verifiers **MUST** require `enc.scheme == 1` and
reject any other value (`UNSUPPORTED_ENVELOPE_SCHEME`). Adding or changing a
per-slot KEM is an additive registry entry under the **same** `enc.scheme`; a
change to the MAC algorithm, its key derivation, or the AAD layout — which applies
to all KEMs at once — is what bumps `enc.scheme`.

The `enc` map under the multi-recipient path:

| field        | type  | rule                                                          |
| ------------ | ----- | ------------------------------------------------------------- |
| `scheme`     | uint  | REQUIRED. `1`.                                                |
| `aead`       | tstr  | REQUIRED. Content-AEAD identifier; `xchacha20-poly1305`.      |
| `nonce`      | bstr  | REQUIRED. 24 bytes (the content-AEAD nonce).                  |
| `kem`        | tstr  | REQUIRED when `slots` present (`x25519` or `mlkem768x25519`). |
| `slots`      | array | REQUIRED on this path. `[ 1* slot ]`, N ≥ 1.                  |
| `slots_mac`  | bstr  | REQUIRED when `slots` present. 32 bytes.                      |
| `passphrase` | map   | FORBIDDEN on this path.                                       |

The cross-field invariants the structural validator **MUST** enforce:

1. Records carrying both `slots` and `passphrase` → `ENC_EXCLUSIVITY_VIOLATION`.
2. Records carrying neither `slots` nor `passphrase` → `ENC_NO_KEY_PATH`.
3. `slots` present but `kem` absent → `ENC_KEM_REQUIRED`.
4. `slots` present but `slots_mac` absent → `ENC_SLOTS_MAC_REQUIRED`.
5. `slots_mac` present but `slots` absent → `ENC_SLOTS_REQUIRED`.
6. `passphrase` present together with any of `kem` / `slots` / `slots_mac` →
   `ENC_EXCLUSIVITY_VIOLATION`.
7. `slots` present but empty → `ENC_SLOTS_EMPTY`.

An item carrying an `enc` envelope **MUST** also declare at least one content-hash
in its `hashes` map (`ENC_REQUIRES_CONTENT_HASH`): the ciphertext is bound to the
plaintext only through that digest (see
[Plaintext-hash binding](#plaintext-hash-binding-and-the-sender-identity-verdict-split)).

The full grammar for `enc`, `slot`, and `passphrase-block` is the authoritative
machine artifact [`../cddl/cip-309.cddl`](cip-309.cddl); the cross-field
rules above are not expressible in CDDL and are enforced in a second pass.

#### KEM selection and the no-mixing rule

Two per-slot KEMs are registered under `enc.scheme = 1` **from the first release**
— the post-quantum hybrid is part of v1, not a later migration. `enc.kem` selects
the KEM, the slot shape, and the KEK derivation.

| `enc.kem`        | KEM                                   | recipient public key | slot shape                                            | KEK info label                      | HRP       |
| ---------------- | ------------------------------------- | -------------------- | ----------------------------------------------------- | ----------------------------------- | --------- |
| `x25519`         | X25519 (classical)                    | 32 B                 | `{ epk: bstr(32), wrap: bstr(48) }`                   | `cardano-poe-kek-v1`                | `age1`    |
| `mlkem768x25519` | X-Wing = ML-KEM-768 + X25519 (hybrid) | 1216 B               | `{ kem_ct: [1* bstr .size (1..64)], wrap: bstr(48) }` | `cardano-poe-kek-mlkem768x25519-v1` | `age1pqc` |

These identifiers are the registry entries
[`../registries/kem-algorithms.json`](https://github.com/cardanowall/cip309/blob/main/registries/kem-algorithms.json); the
content AEAD is [`../registries/aead-algorithms.json`](https://github.com/cardanowall/cip309/blob/main/registries/aead-algorithms.json).
An unregistered `enc.kem` → `UNSUPPORTED_KEM_ALG`; an unregistered `enc.aead` →
`UNSUPPORTED_AEAD_ALG`.

**No-mixing rule.** A single sealed-PoE item carries exactly **one** `enc.kem`;
every slot in `slots[]` uses that KEM and that slot shape. A file is all-classical
or all-hybrid — slots of different KEMs **MUST NOT** appear in the same `slots[]`.
A verifier **MUST** reject a record whose slot shapes are inconsistent with the
declared `enc.kem` (`ENC_SLOT_INVALID_SHAPE`): a classical-shaped slot under
`mlkem768x25519`, a hybrid-shaped slot under `x25519`, an `epk` field on a hybrid
slot, a `kem_ct` field on a classical slot, a stray key, or a missing required
key all violate the closed 2-key slot map.

**Producers SHOULD default to `mlkem768x25519`.** The hybrid KEM is secure against
both classical and harvest-now-decrypt-later quantum adversaries while retaining
X25519's classical security as a floor — the X-Wing combiner binds both shared
secrets. The classical `x25519` KEM remains available for recipients whose
published key is X25519-only.

The identifier `mlkem768x25519` deliberately omits hyphens, matching the
X-Wing/age ecosystem name for the construction. X-Wing parameters (see
[draft-connolly-cfrg-xwing-kem](https://datatracker.ietf.org/doc/draft-connolly-cfrg-xwing-kem/)):

```text
public key   : 1216 bytes = ML-KEM-768 ek (1184) || X25519 pk (32)
ciphertext   : 1120 bytes = ML-KEM-768 ct (1088) || X25519 ephemeral (32)
shared secret: 32 bytes
combiner     : SHA3-256( ss_MLKEM || ss_X25519 || ct_X25519 || pk_X25519 || label )
```

The X-Wing decapsulation key is a 32-byte seed (the public key derives
deterministically from the seed); ML-KEM uses implicit rejection.

#### Slot construction (sender)

The sender selects one KEM for the whole record, obtains N recipient public keys
out-of-band in that KEM's encoding (N ≥ 1), generates a single 32-byte CEK and a
24-byte content nonce, then for each recipient derives a per-slot KEK and wraps
the **same** CEK under it.

**`x25519` (classical).** A fresh ephemeral X25519 keypair per slot:

```text
priv_epk_i : randomBytes(32)                         ; fresh per slot
pub_epk_i  : x25519_publicKey(priv_epk_i)
shared_i   : x25519_sharedSecret(priv_epk_i, pub_R_i)
KEK_i      : HKDF-SHA-256(ikm  = shared_i,
                          salt = pub_epk_i || pub_R_i,   ; 64 bytes, ephemeral first
                          info = "cardano-poe-kek-v1",   ; 18 ASCII bytes
                          L    = 32)
wrap_i     : ChaCha20-Poly1305(key=KEK_i, nonce=zeros(12),
                               ad="cardano-poe-kek-v1", plaintext=CEK)   ; 48 bytes
slot_i     : { "epk": pub_epk_i, "wrap": wrap_i }
```

X25519 implementations **MUST** reject the all-zero shared secret
([RFC 7748](https://www.rfc-editor.org/rfc/rfc7748) §6.1); mainstream libraries
implement this transitively.

**`mlkem768x25519` (hybrid; X-Wing).**

```text
(kem_ct_i, shared_i) = XWing.Encapsulate(pub_R_i)    ; ct = 1120 B, ss = 32 B
KEK_i  : HKDF-SHA-256(ikm  = shared_i,
                      salt = "",                                       ; empty
                      info = "cardano-poe-kek-mlkem768x25519-v1",      ; 33 ASCII bytes
                      L    = 32)
wrap_i : ChaCha20-Poly1305(key=KEK_i, nonce=zeros(12),
                           ad="cardano-poe-kek-mlkem768x25519-v1", plaintext=CEK)  ; 48 B
slot_i : { "kem_ct": chunk64(kem_ct_i), "wrap": wrap_i }
```

The X25519 ephemeral is the trailing 32 bytes of `kem_ct_i`; a hybrid slot has
**no** separate `epk` field. `kem_ct` is the 1120-byte X-Wing ciphertext split
into a CBOR array of byte-strings each ≤ 64 bytes that reassembles, concatenated
in order, to exactly 1120 bytes. The ≤ 64-byte chunking follows the same rule the
record encoder applies to any oversized metadatum byte string under metadata
label 309 (the Cardano ledger caps each metadatum byte string at 64 bytes).

**Per-slot KEK domain separation.** Both KEMs derive a 32-byte KEK with
HKDF-SHA-256 but with KEM-specific salt and `info`. For `x25519` the salt is
`pub_epk || pub_R` (ephemeral first, recipient second, no length prefix): the
ephemeral half anchors the KEK to a slot-unique value, and the recipient half
binds the KEK to the specific recipient (defeating confused-deputy relay of an
`epk` against a different recipient). For `mlkem768x25519` the salt is empty —
the X-Wing combiner already absorbs the full transcript
(`ss_MLKEM || ss_X25519 || ct_X25519 || pk_X25519 || label`), so re-feeding those
values would be redundant; the distinct `info` label supplies the cross-KEM
domain separation so that no KEK derived under one KEM can equal a KEK derived
under the other on an identical 32-byte shared secret. The two `info` labels
**MUST** match the literals above byte-for-byte. The KDF is registered as an
internal building block in [`../registries/kdf-algorithms.json`](https://github.com/cardanowall/cip309/blob/main/registries/kdf-algorithms.json)
(it carries no wire identifier — it is fixed, not selectable).

**Per-slot wrap: zero-nonce ChaCha20-Poly1305.** The wrap uses RFC 8439
ChaCha20-Poly1305 (the 12-byte-nonce variant, **not** XChaCha20-Poly1305) with a
12-byte **zero** nonce, AAD set to the KEM's `info` label literal (never empty
AAD), producing exactly 48 bytes (32-byte CEK ciphertext + 16-byte Poly1305 tag).
The zero nonce is safe **only** because `KEK_i` is per-slot and used for exactly
one wrap: each slot draws fresh KEM randomness (a fresh X25519 ephemeral, or a
fresh X-Wing encapsulation), so `KEK_i` is unique per slot at negligible
collision probability. If any future revision lets `KEK_i` be reused (caching by
`(pub_R, epk)`, deterministic/colliding ephemerals, recipient deduplication that
reuses a slot), the zero nonce **MUST** be replaced with a fresh nonce in the
same change. Any modification of either KEM's KEK derivation is security-critical.

**Slot shuffle (REQUIRED).** The order in which a sender supplies recipient keys
is privileged metadata (e.g. "primary recipient first"). Publishing slots in
input order leaks it. The sender **MUST** shuffle `slots[]` with a CSPRNG (an
unbiased Fisher-Yates permutation — a plain `u32 % m` index draw skews toward low
residues and **MUST** be rejection-sampled to a uniform index) **before**
computing the slot-set MAC. The MAC binds the shuffled on-wire order.

#### Slot-set MAC

After the shuffle, the sender binds the full slot set to the CEK with an HMAC
keyed by an HKDF of the CEK:

```text
HMAC_KEY   : HKDF-SHA-256(ikm=CEK, salt="", info="cardano-poe-slots-mac-v1", L=32)
                                                ; info = 24 ASCII bytes
slots_cbor : canonicalCBOR(slots)               ; RFC 8949 §4.2.1
slots_mac  : HMAC-SHA-256(key=HMAC_KEY, msg=slots_cbor)   ; 32 bytes
```

The MAC algorithm (HMAC-SHA-256), its key derivation (HKDF-SHA-256 with info
`cardano-poe-slots-mac-v1`), and the content-AEAD AAD layout (`nonce ||
slots_mac`) are **fixed by `enc.scheme`** and identical for both KEMs. There is
no on-wire identifier for the slot-set MAC; exactly one construction is defined
per `enc.scheme` value. The MAC covers the full per-slot wire content of every
slot — `{ epk, wrap }` for `x25519`, `{ kem_ct, wrap }` for `mlkem768x25519`, so
the entire chunked `kem_ct` array is inside the MAC.

**Chunking-invariant `kem_ct`.** The MAC commits to a **canonical** chunking of
`kem_ct`, not to whatever ≤ 64-byte split landed on the wire. Before encoding
`slots` for the MAC, an implementation **MUST** canonicalize each hybrid slot's
`kem_ct`: reassemble the 1120-byte ciphertext, then re-split into the canonical
≤ 64-byte chunk sequence (full 64-byte chunks followed by a final remainder).
This makes the MAC depend on the `kem_ct` **bytes**, not on chunk boundaries —
chunk boundaries carry no semantic meaning. A verifier likewise canonicalizes
before recomputing the MAC: an honest record already emitting canonical chunks is
unaffected, a record re-chunked in transit (same bytes, different boundaries)
still verifies, and any byte flip in `kem_ct` still fails the MAC. Without this,
an attacker could re-chunk an honest envelope and break an honest recipient's MAC
match, leaving the ML-KEM ciphertext effectively unauthenticated.

The `slots_mac` length **MUST** be exactly 32 bytes (`ENC_SLOTS_MAC_INVALID_LENGTH`
on a wrong length) and **MUST** be verified in constant time.

#### Content encryption

The plaintext is encrypted once under the shared CEK with the content AEAD:

```text
ad_content : nonce || slots_mac                  ; 24 + 32 = 56 bytes, nonce first
ciphertext : XChaCha20-Poly1305(key=CEK, nonce=nonce, ad=ad_content, plaintext=plaintext)
```

The content AEAD is **XChaCha20-Poly1305** with a 24-byte random nonce. The
extended nonce lets stateless producers (browser tabs, CLI invocations, workers,
retries) draw a fresh nonce from a CSPRNG without coordinating counters; this is
its sole content-layer rationale. The AEAD AAD on the multi-recipient path is
**exactly `nonce || slots_mac`** (56 bytes) — implementations **MUST NOT** pass
empty AAD on this path. A mismatched AAD between producer and verifier surfaces as
an AEAD tag-verification failure, not a typed structural error.

The plaintext input is the exact original content bytes; the ciphertext **MUST**
decrypt back to those bytes and only those. The construction does **not** prepend,
append, or encrypt a filename, MIME type, size field, or any metadata wrapper.

The assembled `enc` map (`{ scheme, aead, kem, nonce, slots, slots_mac }`) is
carried in the on-chain CIP-309 record; the **ciphertext bytes are not placed on
chain**. The ciphertext is published to a content-addressed store and the
resulting URI lands in the item's `uris[]` — see
[Ciphertext storage](#ciphertext-storage-and-integrity).

Invariants for both KEMs: each `wrap` MUST be exactly 48 bytes
(`WRAP_LENGTH_MISMATCH` otherwise); `slots_mac` MUST be exactly 32 bytes; `nonce`
MUST be exactly 24 bytes (`NONCE_LENGTH_MISMATCH` otherwise); each `x25519` slot's
`epk` MUST be exactly 32 bytes (`KEM_EPK_LENGTH_MISMATCH` otherwise); each
`mlkem768x25519` slot's `kem_ct` MUST reassemble to exactly 1120 bytes
(`KEM_CT_LENGTH_MISMATCH` otherwise) and the slot MUST NOT carry an `epk` field;
`slots[]` MUST contain at least one entry. The canonical-CBOR input to the HMAC
MUST follow [RFC 8949](https://www.rfc-editor.org/rfc/rfc8949) §4.2.1.
Implementations **MUST** zeroize `priv_epk_i`, `shared_i`, `KEK_i`, `CEK`, and
`HMAC_KEY` on scope exit where the language exposes mutable byte buffers, and
SHOULD limit their lifetime via local scope where byte sequences are immutable.

#### Recipient decryption (trial-decrypt)

A recipient holds one KEM private key (a 32-byte X25519 scalar for `x25519`, or a
32-byte X-Wing decapsulation seed for `mlkem768x25519`). They iterate `slots[]`
and trial-decrypt each slot; recipient public keys are **not** on the wire, so
the recipient discovers their slot by attempting to open it. The slot-set MAC
check is folded **into** the slot loop: a slot is accepted only when its candidate
CEK also reproduces the on-wire `slots_mac`.

Before any KEM or AEAD primitive is invoked, the verifier **MUST** run shape
checks (partitioning-oracle defence): `scheme == 1`, `aead` registered, `kem`
registered, `nonce` 24 bytes, `slots_mac` 32 bytes, `slots` non-empty, the
recipient secret 32 bytes, and each `slot.wrap` exactly 48 bytes; for `x25519`
each `epk` 32 bytes with no `kem_ct`; for `mlkem768x25519` each `kem_ct`
reassembling to 1120 bytes with no `epk`.

```text
slots_cbor = canonicalCBOR(canonicalizeSlots(envelope.slots))   ; constant across the loop
if kem == "x25519": pub_R_local = x25519_publicKey(priv_R)      ; recipient salt half

for slot in envelope.slots:
    if kem == "x25519":
        shared = x25519_sharedSecret(priv_R, slot.epk)
        KEK    = HKDF-SHA-256(shared, salt=slot.epk || pub_R_local,
                              info="cardano-poe-kek-v1", L=32)
        ad_wrap = "cardano-poe-kek-v1"
    else:                                   ; mlkem768x25519
        kem_ct = concat(slot.kem_ct)        ; reassemble → 1120 bytes
        shared = XWing.Decapsulate(priv_R, kem_ct)
        KEK    = HKDF-SHA-256(shared, salt="",
                              info="cardano-poe-kek-mlkem768x25519-v1", L=32)
        ad_wrap = "cardano-poe-kek-mlkem768x25519-v1"

    candidate_CEK = ChaCha20-Poly1305_open(KEK, zeros(12), ad_wrap, slot.wrap)
    if open failed: continue
    HMAC_KEY = HKDF-SHA-256(candidate_CEK, salt="",
                            info="cardano-poe-slots-mac-v1", L=32)
    if constantTimeEqual(HMAC-SHA-256(HMAC_KEY, slots_cbor), envelope.slots_mac):
        CEK = candidate_CEK; accept

ad_content = envelope.nonce || envelope.slots_mac
plaintext  = XChaCha20-Poly1305_open(CEK, envelope.nonce, ad_content, ciphertext)
```

The folded MAC check is load-bearing. A malicious sender can construct a slot that
opens under a recipient's `priv_R` with an attacker-chosen CEK (no `priv_R`
knowledge required — standard encryption to the recipient's public key suffices).
If the recipient accepted the first AEAD-success as "ours", that forged slot would
shadow an honest slot and decryption would fail at the content layer even though a
valid slot exists later in the array. Requiring the candidate CEK to also produce
the `slots_mac` defeats slot-substitution, slot-removal, and slot-reorder attacks.
Implementations **MUST NOT** skip the `slots_mac` verification.

**Constant-time-across-slots requirement.** Within a single private key's pass,
the trial-decrypt loop **MUST** run over **all** slots regardless of an early
match — i.e. a constant number of slot operations per private key — so a
network-level observer cannot infer which slot index matched. A recipient who has
multiple private keys (e.g. archived keys across an identity rotation) iterates
private-key × slot; the per-private-key constant-time-N invariant holds for each
key. The loop **MAY** short-circuit across private keys (variable time leaks only
the weak "which key matched" signal, a documented trade-off), but **MUST** remain
constant-time across the slots of any single key. For the `x25519` KEM, when
iterating multiple keys the `pub_R` half of the HKDF salt **MUST** be re-derived
per key as `x25519.publicKey(currentKey)` — reusing a single `pub_R` across keys
computes the wrong KEK for every key but one. The hybrid KEM has no `pub_R` in its
salt, so this rule does not apply there.

**Decryption outcomes** (typed): no slot opens under `priv_R` (trial-decrypt
exhausted) → `WRONG_RECIPIENT_KEY`; a slot opens but no candidate CEK reproduces
the `slots_mac` (the slot set was tampered) → `TAMPERED_HEADER`; the content AEAD
fails after a CEK is recovered and the MAC verified (ciphertext, nonce, or
`slots_mac` modified in transit) → `TAMPERED_CIPHERTEXT`. These three codes are in
[`../registries/error-codes.json`](https://github.com/cardanowall/cip309/blob/main/registries/error-codes.json).

#### Plaintext-hash binding and the sender-identity verdict split

The item's `hashes` map **MUST always commit to the plaintext**, even when `enc`
is present. This is the load-bearing property: any party who later obtains the
plaintext can prove "this exact plaintext was committed at block time T". A
plaintext-bound hash is what makes the time claim meaningful — a ciphertext-only
attestation would only prove that _some_ ciphertext existed.

After decryption, the recipient — at the application layer — **MUST** recompute
the plaintext digests and compare against the on-chain commitments: the
`sha2-256` entry MUST match, and the `blake2b-256` entry MUST match if present. A
mismatch means the record's hash claim does not match the decrypted bytes; the
recipient **MUST** refuse to act on the plaintext. The structural validator
**MUST NOT** decrypt to verify hashes — it checks envelope shape only. Only the
holder of a matching `priv_R` can confirm _what the commitment is to_; the rest of
the world can confirm only that an immutable, timestamped commitment exists.

The record carries no separate ciphertext hash or size. None is needed: the
ciphertext lives at a content-addressed URI whose storage-layer integrity model
binds the URI to the bytes (see
[Ciphertext storage](#ciphertext-storage-and-integrity)).

**Sender-identity verdict split.** A sealed-PoE record MAY carry record-level
COSE_Sign1 signatures (see
[Record-level signatures (COSE_Sign1)](#record-level-signatures-cose_sign1)).
When present they bind the on-chain commitment — including the `enc` map, the
`hashes` claim, and the `uris[]` — to a sender identity. Whether a recipient
requires that binding is a deployment-policy decision, not a wire-format
constraint; the construction admits both signed sealed PoE (content claim plus
sender-identity claim) and unsigned sealed PoE (anonymous-publication use cases —
whistleblower drops, sealed-bid auctions, evidence escrow — where binding a sender
on-chain would defeat the purpose). The validator preserves the content claim
across signature-support gaps:

- **All signatures verify** → record valid; recipient gets both claims.
- **Some verify, others use unsupported algorithms** → record valid; the
  unsupported entries are surfaced informationally.
- **Every signature uses an unsupported algorithm** → `SIGNATURE_UNSUPPORTED`:
  sender identity cannot be confirmed, but the content claim (plaintext hash, URI,
  `enc` envelope) remains parseable. A recipient needing only the timestamped hash
  commitment MAY treat the record as authoritative for that claim; a recipient
  relying on sender-identity binding **MUST** treat it as not yet usable until a
  verifier with the algorithm support is reached.
- **No signatures at all** → structurally valid sealed PoE. The validator **MUST
  NOT** emit a failure verdict solely on the absence of signatures; whether the
  application accepts an unsigned record is a deployment-policy decision.

#### Passphrase path

The alternative key-delivery path replaces recipient slots with a passphrase. The
producer derives the CEK directly from a normalised passphrase; there is no
ephemeral keypair, no `epk`, no per-slot wrap, no slot-set MAC, and no
trial-decrypt loop.

```text
passphrase_bytes = utf8(normalize(passphrase))   ; NFKC → whitespace collapse → trim → UTF-8
CEK = argon2id(passphrase_bytes,
               salt   = enc.passphrase.salt,
               params = enc.passphrase.params,
               L      = 32)
ciphertext = XChaCha20-Poly1305(key=CEK, nonce=enc.nonce, ad=h'', plaintext=file_bytes)
```

The content AEAD AAD on this path is the **empty byte string** (`h''`) — there is
no slot set or slot-set MAC to bind; the integrity binding instead comes from the
canonical-CBOR `enc` map being covered by the Cardano transaction hash (and, when
present, record-level signatures). Producers and verifiers **MUST** select the AAD
rule by checking which of `slots`/`passphrase` is present before invoking the AEAD
primitive. These two AAD rules (`nonce || slots_mac` for slots, `h''` for
passphrase) are exhaustive and exclusive.

The `enc.passphrase` map is `{ alg, salt, params }`. The sole registered KDF is
`argon2id` (see [`../registries/kdf-algorithms.json`](https://github.com/cardanowall/cip309/blob/main/registries/kdf-algorithms.json));
an unregistered `alg` → `ENC_PASSPHRASE_ALG_UNSUPPORTED`. The validator enforces:

- `salt` length 16–64 bytes inclusive (`ENC_PASSPHRASE_SALT_TOO_SHORT` /
  `ENC_PASSPHRASE_SALT_TOO_LONG`; the 64-byte ceiling is the metadatum byte-string
  cap).
- `params = { m, t, p }` with `m ≥ 65 536` (KiB ≈ 64 MiB), `t ≥ 3`, `p ≥ 1`; any
  floor violation → `ENC_PASSPHRASE_ARGON2_PARAMS_TOO_LOW`. The output length is
  fixed at 32 bytes and is not carried in `params`.

Implementations MAY also enforce **upper** bounds against verifier-side DoS,
reporting `ENC_PASSPHRASE_PARAMS_EXCEED_POLICY`; such ceilings are non-normative
(hardware-dependent) and **MUST NOT** be conflated with the floor code.

> **Security trade-off (informative).** `salt` and `params` are public on chain in
> perpetuity; an attacker has unlimited offline time to brute-force the passphrase
> against the published parameters. Passphrase entropy is the only barrier.
> Producers **SHOULD** generate the passphrase via a CSPRNG (high-entropy
> word-list passphrases) rather than accepting a low-entropy user password,
> **SHOULD** present the generated passphrase to the user for distribution, and
> **MUST NOT** silently substitute a low-entropy default; producers accepting
> human-typed passphrases SHOULD surface a visible offline-brute-force warning.

#### Ciphertext storage and integrity

Sealed-PoE ciphertext is stored at a content-addressed URI carried in the item's
`uris[]`, using **exactly** the scheme set `{ ar://, ipfs:// }`. Both are
content-addressed: an `ipfs://<cid>` URI carries a multihash of the content
directly in the CID; an `ar://<txid>` URI carries a transaction ID that commits to
the data via the signed transaction's `data_root` (a Merkle root over the chunks)
under that storage layer's consensus. Either way the URI is bound to the
referenced bytes by the storage layer's integrity model, which is why sealed PoE
carries no separate on-chain ciphertext-commitment field: a gateway returning
bytes inconsistent with the URI is detectable by anyone who fetches it (recompute
the IPFS multihash, or validate the signed transaction and `data_root` on
Arweave). `uris[]` MAY be absent even when `enc` is present (out-of-band
ciphertext delivery), in which case the verifier acquires the ciphertext from
local input.

#### Forbidden patterns

- **MUST NOT** reuse a per-slot ephemeral across slots or records: a fresh X25519
  ephemeral per `x25519` slot, a fresh X-Wing encapsulation per `mlkem768x25519`
  slot. The zero-nonce wrap relies on per-slot KEK uniqueness.
- **MUST NOT** mix KEMs within one `slots[]` — one `enc.kem` per item.
- **MUST NOT** publish `slots[]` in input order — CSPRNG-shuffle is REQUIRED.
- **MUST NOT** place any recipient public key on the wire. The trial-decrypt
  design is a deliberate privacy feature; out-of-band recipient hints are an
  application concern, not part of the record.
- **MUST NOT** wrap the CEK with any nonce other than the 12-byte zero nonce, nor
  with empty wrap-AEAD AAD — the AAD is the KEM's `info` label literal.
- **MUST NOT** sign the ciphertext at the record level; record signatures cover
  the canonical-CBOR record body, which transitively binds the plaintext hash
  (via `hashes`) and the slot set (via `slots_mac`).
- **MUST NOT** store the plaintext at the `ar://`/`ipfs://` URI — only the
  ciphertext is published; plaintext is delivered out of band or held by the
  sender.
- **MUST NOT** reference sealed-PoE ciphertext through any scheme other than
  `ar://` or `ipfs://`; a non-content-addressed URI would require a separate
  on-chain ciphertext commitment that sealed PoE does not carry.
- **MUST NOT** log `CEK`, `KEK_i`, `HMAC_KEY`, `shared_i`, `priv_epk_i`, or
  `priv_R` at any level; zeroize or scope-limit these secrets.
- **MUST NOT** skip the `slots_mac` verification step — slot-substitution attacks
  succeed without it.

#### Recipient public-key discovery (out of scope, non-normative)

This standard deliberately does **not** specify how a sender obtains a recipient's
public key. A wire-format standard that prescribed a discovery mechanism would
couple adoption to a specific service, defeating the open-standard property.
Senders obtain recipient keys through whatever channel they trust (a published
recipient string on the recipient's own domain or social profile, a DNS record, a
self-attestation record on chain, an in-person handoff, a trusted key-book
operator). A verifier takes the recipient public-key bytes as input — 32 bytes for
`x25519`, 1216 bytes for `mlkem768x25519` — and makes no claim about whose key
they are; provenance is the sender's trust decision, exactly as when sending mail
to a PGP key. Recipients are discovered by **trial-decrypt only**: the receiver
searches the slot list with their own private key.

Recipient and identity strings are Bech32-encoded with the same checksum and
character-set rules as [BIP-173](https://github.com/bitcoin/bips/blob/master/bip-0173.mediawiki):
the `x25519` recipient uses HRP `age1` (32-byte X25519 public key) with secret-key
HRP `AGE-SECRET-KEY-`; the `mlkem768x25519` recipient uses HRP `age1pqc`
(1216-byte X-Wing public key, with the BIP-173 90-character length cap lifted to
accommodate the larger payload) with secret-key HRP `AGE-SECRET-KEY-PQ-` over the
32-byte X-Wing seed. The post-quantum HRP is `age1pqc`, **not** `age1pq`: the
latter is claimed by an upstream native ML-KEM-768+X25519 encoding, so the
distinct `age1pqc` prefix ensures a recipient string can never be mistaken for, or
parsed as, that upstream encoding even though both encode the same primitive.

#### Privacy and metadata exposure (informative)

The on-chain record reveals: the **count** of slots (the only
recipient-identity-adjacent leakage; count-hiding via slot padding is a possible
future extension, not part of the baseline); the **plaintext hash**; the
**timestamp** of the carrying transaction (block-time accurate to seconds — for
leaks where timing alone is sensitive, a meaningful exposure); and the **fact**
that the record is a sealed PoE (an observer can distinguish sealed from open
records and read `enc.kem` to tell classical from hybrid).

The on-chain record does **not** reveal: the recipient public keys (trial-decrypt
design); the plaintext bytes; or the relationship between two sealed records
targeting the same recipient — per-slot fresh ephemerals under either KEM
(independent `epk` values for `x25519`, independent `kem_ct` blobs for
`mlkem768x25519`) mean an observer cannot link records by recipient without
`priv_R`. Senders concerned about timing-correlation **MUST** batch publishes off
the critical timeline; wire-level cryptography cannot solve metadata-timing
attacks.

Conformance vectors for the wrap, unwrap, multi-private-key iteration, hybrid
re-chunking, and the negative input-validation cases are under
[`../conformance/sealed-poe/`](https://github.com/cardanowall/cip309/blob/main/conformance/sealed-poe).

### Algorithm registries and conformance profiles

CIP-309 references every cryptographic algorithm by a **named string identifier** drawn from one of six registries. An identifier is a stable, opaque token (for example `sha2-256`, `xchacha20-poly1305`, `mlkem768x25519`); each token is bound to exactly one algorithm with a stable public reference (an RFC, a FIPS publication, a CIP, an IANA codepoint, or a named internet-draft). This named-identifier ↔ stable-public-reference model is what makes the standard algorithm-agile: a verifier that does not recognise an identifier rejects the record with a typed error code (see [Structural validation, verifier roles, and error codes](#structural-validation-verifier-roles-and-error-codes)) — it MUST NOT crash and MUST NOT silently accept.

The identifier strings in this section are normative. Conformant implementations **MUST** encode them on-wire byte-for-byte as written.

The normative machine-readable form of every registry lives under [`../registries/`](https://github.com/cardanowall/cip309/blob/main/registries):

| Registry                          | File                                                                                                 | Wire role                              |
| --------------------------------- | ---------------------------------------------------------------------------------------------------- | -------------------------------------- |
| Hash algorithms                   | [`../registries/hash-algorithms.json`](https://github.com/cardanowall/cip309/blob/main/registries/hash-algorithms.json)                           | `items[i].hashes` map keys             |
| Merkle list-commitment algorithms | [`../registries/merkle-commitment-algorithms.json`](https://github.com/cardanowall/cip309/blob/main/registries/merkle-commitment-algorithms.json) | `merkle[i].alg`                        |
| AEAD algorithms                   | [`../registries/aead-algorithms.json`](https://github.com/cardanowall/cip309/blob/main/registries/aead-algorithms.json)                           | `enc.aead`                             |
| KEM algorithms                    | [`../registries/kem-algorithms.json`](https://github.com/cardanowall/cip309/blob/main/registries/kem-algorithms.json)                             | `enc.kem`                              |
| KDF algorithms                    | [`../registries/kdf-algorithms.json`](https://github.com/cardanowall/cip309/blob/main/registries/kdf-algorithms.json)                             | `enc.passphrase.alg`                   |
| Signature algorithms              | [`../registries/signature-algorithms.json`](https://github.com/cardanowall/cip309/blob/main/registries/signature-algorithms.json)                 | `COSE_Sign1` protected `alg`           |
| Error codes                       | [`../registries/error-codes.json`](https://github.com/cardanowall/cip309/blob/main/registries/error-codes.json)                                   | structural-validator / verifier output |

Where this prose and the registry JSON differ, the registry JSON is authoritative for the identifier set, the pinned length constants, and the typed error code emitted on each failure mode.

#### Identifier-carriage forms

CIP-309 carries algorithm identifiers in three on-wire shapes, selected by the structural needs of each registry:

1. **Direct value** — `<role>: "<alg-id>"` — for identifiers that carry no algorithm-specific parameters (e.g. `enc.aead: "xchacha20-poly1305"`, `enc.kem: "x25519"`).
2. **`alg`-field map** — `<role>: {"alg": "<id>", ...parameters}` — for identifiers that require algorithm-specific parameters (e.g. `merkle[i] = {"alg": "rfc9162-sha256", "root": ..., "leaf_count": ..., ...}`, `enc.passphrase = {"alg": "argon2id", "salt": ..., "params": ...}`).
3. **Map-key form** — `{<alg-id>: <value>}` — for identifiers used as CBOR map keys, which inherits RFC 8949 §3.1 duplicate-key uniqueness and §4.2.1 deterministic ordering (e.g. `items[i].hashes = {"sha2-256": <digest>, "blake2b-256": <digest>}`).

The three forms minimise wire bytes for each role: a single-token identifier is a bare string; a parameterised identifier lives in a structured map; map-key identifiers exploit CBOR's native uniqueness semantics. The inconsistency is byte-justified, not stylistic.

#### Conformance profiles

CIP-309 v1 defines four **conformance profiles** so that an implementation can advertise the subset of the standard it supports without having to implement every cryptographic primitive in the registry. A consumer (verifier, indexer, explorer plug-in, archival tool) is conformant if it correctly handles every record that uses **only** algorithms in its declared profile, and cleanly rejects records that require a higher profile with the appropriate `UNSUPPORTED_*` code.

| Profile                | Reads (what records this profile can process)                                                                                                                                                                                                                                  | Implementation surface (algorithms a verifier must implement)                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| ---------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **`core`**             | Hash-only PoE records — `items[i].hashes`, optional `uris`, optional top-level `merkle[]`, optional `supersedes`, no `enc`, no `sigs`.                                                                                                                                         | SHA-256, BLAKE2b-256, canonical CBOR (RFC 8949 §4.2.1), the Cardano metadata fetch / decode path, and the offline multibase / multihash CID parser. The `rfc9162-sha256` list-commitment identifier is **OPT-INFO** within `core`: a verifier MAY implement RFC 9162 §2.1.1 Merkle-fold + per-leaf inclusion-proof verification. A verifier that does not implement Merkle-fold reports each `merkle[i]` commitment as `MERKLE_UNSUPPORTED` (info-severity) and verifies the record's `items[i].hashes` content claim normally. |
| **`signed`**           | Everything `core` reads, plus records carrying record-level `sigs[]` (each entry a closed `{cose_sign1, cose_key?}` map; see [Record-level signatures (COSE_Sign1)](#record-level-signatures-cose_sign1)).                                                                     | All of `core`, plus strict non-cofactored Ed25519 (RFC 8032 §5.1.7), COSE_Sign1 (RFC 9052), and HMAC-SHA-256 / HKDF-SHA-256 where the spec requires them outside the `enc` envelope.                                                                                                                                                                                                                                                                                                                                            |
| **`sealed`**           | Everything `signed` reads, plus records carrying `enc` (sealed multi-recipient or passphrase). A `sealed` verifier is **public-verifier**-conformant: it parses the envelope, enforces the length checks, and verifies any `sigs[]` over the record body. It does NOT decrypt. | All of `signed`, plus **registered-identifier and length constants only** (no new crypto primitives): the AEAD nonce length (24 B for `xchacha20-poly1305`), the per-KEM slot-shape length constants (`x25519` — 32 B `epk`; `mlkem768x25519` — 1120 B reassembled `kem_ct`), the per-slot `wrap` length (48 B), the `slots_mac` length (32 B), and the KDF identifier `argon2id`. A `sealed`-profile verifier never invokes X25519, ML-KEM, HKDF, or any AEAD primitive.                                                       |
| **`recipient-sealed`** | Everything `sealed` reads, **and** decrypts records when given the recipient's KEM private key (an X25519 private key for `x25519` slots, an X-Wing decapsulation seed for `mlkem768x25519` slots).                                                                            | All of `sealed`, plus the full sealed-PoE decrypt path for both KEMs and the post-decryption plaintext-hash recomputation (see [Sealed PoE: multi-recipient encryption](#sealed-poe-multi-recipient-encryption)).                                                                                                                                                                                                                                                                                                               |

Profiles are **strict supersets**: `recipient-sealed` ⊃ `sealed` ⊃ `signed` ⊃ `core`. Every conformant implementation MUST declare its profile; third-party reviewers can then audit conformance against a defined subset rather than the full surface. A producer MAY emit records targeting any profile; the producer's own profile is the lowest profile a verifier must implement to read its output. Hash-only PoE records — the simplest and most adoptable case — require only the `core` profile, so a third-party `core`-only verifier is a meaningful interop target.

The structural validator and the verifier profile are orthogonal. The structural validator parses the full v1 schema regardless of profile — it MUST recognise `enc`, `sigs`, COSE_Sign1 shapes, KDF parameter maps, and every registry identifier well enough to emit the typed `UNSUPPORTED_*`/`SCHEMA_*`/`MALFORMED_*` codes. The structural validator answers "is this a well-formed v1 record?"; the profile answers "can this verifier verify this record end-to-end?".

#### Identifier-level conformance levels

Inside a given profile, every algorithm identifier carries one of these normative statuses:

- **MANDATORY-to-implement (M).** A conformant verifier in the relevant profile **MUST** be able to consume records carrying this identifier (parse, validate length constraints, perform the corresponding cryptographic operation when the rest of the record permits).
- **OPTIONAL-to-produce (O).** A v1 producer **MAY** emit this identifier; the verifier-side capability is still mandatory.
- **OPTIONAL-on-both-sides (OPT).** A v1 producer **MAY** emit this identifier and a verifier **MAY** implement it. A verifier that does not implement it **MUST** reject records carrying it with the corresponding `UNSUPPORTED_*` code, rather than silently downgrading or skipping.
- **OPTIONAL-with-info-on-skip (OPT-INFO).** A verifier that does **not** implement an OPT-INFO identifier surfaces the affected record element as an **info-severity** entry (e.g. `MERKLE_UNSUPPORTED`, `SIGNATURE_UNSUPPORTED`) and **continues** validating the rest of the record. This differs from OPT: an unimplemented OPT identifier rejects the record, whereas an unimplemented OPT-INFO identifier is skipped without invalidating the record. The OPT-INFO tier is reserved for identifiers whose presence does not invalidate other commitments in the record.

  **Severity escalation.** When an OPT-INFO identifier represents the record's **only** content commitment (e.g. a merkle-only record where the verifier does not implement Merkle-fold), the info-severity entry MUST escalate to `error` severity and the record-level verdict MUST be `failed`. A verifier that emits `valid` has, by construction, verified at least one content commitment.

- **Reserved (R).** Identifier is reserved for future revisions; no v1 producer emits it. v1 verifiers reject hash / AEAD / KEM / KDF Reserved identifiers as `UNSUPPORTED_*` (these primitives are load-bearing for content integrity / decryption / KDF, so a record using one is unverifiable). Signature-algorithm Reserved identifiers are handled differently: a `sigs[i]` carrying a Reserved `alg` is reported as `SIGNATURE_UNSUPPORTED` (informational) and does not by itself invalidate the record.

"RECOMMENDED" annotations indicate the preferred choice among multiple mandatory-to-implement options.

#### Hash algorithms (`items[i].hashes` map keys)

| Identifier    | Algorithm              | Design family         | Digest length | Status |
| ------------- | ---------------------- | --------------------- | ------------- | ------ |
| `sha2-256`    | SHA-256 (FIPS 180-4)   | SHA-2 (content hash)  | 32 B          | **M.** |
| `blake2b-256` | BLAKE2b-256 (RFC 7693) | BLAKE2 (content hash) | 32 B          | **M.** |

Both `sha2-256` and `blake2b-256` are MANDATORY-to-implement for verifiers so that a single-hash record under either identifier validates on every conformant implementation. A record MUST carry **at least one** entry in `hashes` per item; a single content-hash entry is fully conformant (see [Record model](#record-model)). Verifiers **MUST** reject records whose `hashes` map carries an unknown algorithm identifier as a key with `UNSUPPORTED_HASH_ALG` rather than silently skipping, and a digest of the wrong length with `HASH_DIGEST_LENGTH_MISMATCH`.

**v1 registry scope.** Only **32-byte-digest** algorithms may be added under v1 without a schema bump, because the grammar pins `hash-map = { + content-hash-alg => bytes32 }`. An addition whose digest length differs (e.g. SHA-512) requires a successor revision that updates the grammar — a top-level `v` bump (`v: 2`).

#### Merkle list-commitment algorithms (`merkle[i].alg`)

The list-commitment algorithms registered for `merkle[i].alg` are **disjoint** from the content-hash algorithms above. A list-commitment algorithm commits to an ordered list of 32-byte leaves; a content-hash algorithm commits to plaintext bytes. A `merkle[i].alg` value MUST be from this registry and MUST NOT be a content-hash identifier.

| Identifier       | Algorithm                                                                                                                                                                                                                                                                                                                                                                                                                                       | Root length | Status        |
| ---------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------- | ------------- |
| `rfc9162-sha256` | RFC 9162 §2.1.1 binary Merkle tree, SHA-256 underlying. The identifier is the IANA "COSE Verifiable Data Structure Algorithms" registry codepoint 1 (per [draft-ietf-cose-merkle-tree-proofs-18](https://datatracker.ietf.org/doc/draft-ietf-cose-merkle-tree-proofs/)); RFC 9162 §2.1.1 is a re-publication of [RFC 6962 §2.1](https://www.rfc-editor.org/rfc/rfc6962#section-2.1) with identical `0x00` leaf / `0x01` internal-node prefixes. | 32 B root   | **OPT-INFO.** |

The byte-level construction is normative below. The leaf prefix is `0x00`, the internal-node prefix is `0x01`; the prefixes prevent the second-preimage malleability of duplicate-leaf trees by domain-separating leaves from internal nodes. As an OPT-INFO identifier, a v1 verifier that does not implement Merkle list commitments reports each `merkle[i]` entry as `MERKLE_UNSUPPORTED` (info-severity) and verifies the record's `items[i].hashes` content claim normally. A merkle-only record (no `items[]`) verified by a non-Merkle implementation escalates `MERKLE_UNSUPPORTED` to `error` and the record-level verdict is `failed`. The structural error `UNSUPPORTED_MERKLE_COMMIT_ALG` is reserved for records whose `merkle[i].alg` is **not in the registered set above** (currently `{rfc9162-sha256}`) — a recognised OPT-INFO identifier that this verifier did not implement is `MERKLE_UNSUPPORTED`, NOT `UNSUPPORTED_MERKLE_COMMIT_ALG`. Verifiers **MUST** reject `merkle[i]` entries whose `alg` is not registered above with `UNSUPPORTED_MERKLE_COMMIT_ALG`.

##### Tree construction (RFC 9162 §2.1.1)

Let `L = (d_0, d_1, ..., d_{n-1})` be an ordered list of 32-byte values with `n ≥ 1`. The Merkle Tree Hash `MTH(L)` is defined recursively:

- If `n == 1`: `MTH(L) = SHA-256(0x00 || d_0)` — the single-leaf case.
- If `n > 1`: let `k` be the largest power of 2 strictly less than `n` (i.e. `k = 2^floor(log_2(n-1))`). Then `MTH(L) = SHA-256(0x01 || MTH(L[0:k]) || MTH(L[k:n]))` — the internal-node case.

An empty tree (`n == 0`) is **forbidden**; producers **MUST NOT** create records under this identifier with an empty leaf list. The `merkle[i].leaf_count` field (REQUIRED) lets a structural validator detect `leaf_count == 0` directly; it is also compared against the fetched leaves-list's `leaf_count`, emitting `SCHEMA_MERKLE_LEAF_COUNT_MISMATCH` on disagreement. Each `d_i` is a 32-byte sequence; the typical use places `d_i = SHA-256(content_i)`, but the construction is agnostic to leaf provenance — each leaf MUST be exactly 32 bytes.

##### Single-leaf identity

For `n == 1` the Merkle root is **NOT** equal to `d_0` — it is `SHA-256(0x00 || d_0)`. The leaf prefix prevents construction of an internal-node-shaped value that collides with a single leaf. Producers who want a single-file PoE **MUST** use the `sha2-256` or `blake2b-256` content-hash identifier directly, **NOT** a 1-leaf Merkle tree.

##### Inclusion proofs

For a leaf at index `i` in a tree with `n` leaves, an inclusion proof is the ordered list of sibling node hashes `p = (s_0, ..., s_{m-1})` along the path from the leaf to the root, where `m = 0` when `n == 1` and `1 ≤ m ≤ ceil(log_2(n))` when `n > 1`. The proof length is **variable** for unbalanced RFC 9162 trees: right-edge leaves under odd-leaf parents legitimately produce shorter proofs. The authoritative acceptance check is **algorithmic** — the reconstructed root MUST equal the published root byte-for-byte — not a length comparison:

```
verify_inclusion(d_i, i, n, proof) -> root:
    if n == 1:
        require proof == [] and i == 0
        return SHA-256(0x00 || d_i)
    require len(proof) >= 1
    k = largest_power_of_2_lt(n)
    sibling = proof[len(proof) - 1]   # top-level sibling, consumed first
    rest    = proof[0 : len(proof) - 1]
    if i < k:
        left  = verify_inclusion(d_i, i,     k,     rest)
        return SHA-256(0x01 || left || sibling)
    else:
        right = verify_inclusion(d_i, i - k, n - k, rest)
        return SHA-256(0x01 || sibling || right)
```

A verifier accepts the proof iff `verify_inclusion(d_i, i, n, proof) == expected_root` byte-for-byte. The standard iterative formulation in [RFC 9162 §2.1.3.2](https://www.rfc-editor.org/rfc/rfc9162#section-2.1.3.2) produces the same root and MAY be used; both formulations are normative and yield byte-identical results for all `n`, including non-power-of-2 trees. A receiver MUST NOT reject a proof solely because its length is less than `ceil(log_2(n))`.

#### AEAD algorithms (`enc.aead`)

The `enc.aead` field carries the **content AEAD algorithm only** — the symmetric primitive that encrypts the plaintext under the content-encryption key. KEM identifiers live in the KEM registry below (`enc.kem`); the two fields are orthogonal, and the content AEAD is KEM-independent. The per-slot CEK-wrap construction (`chacha20-poly1305` with a fixed zero nonce; see [Sealed PoE: multi-recipient encryption](#sealed-poe-multi-recipient-encryption)) is **not** a wire-selectable content AEAD and is deliberately absent from this registry.

| Identifier           | Algorithm                                                                                                                                           | Key  | Nonce | Tag  | Status                                                                                                                                                                                   |
| -------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- | ---- | ----- | ---- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `xchacha20-poly1305` | XChaCha20-Poly1305 (extended-nonce variant of [RFC 8439](https://www.rfc-editor.org/rfc/rfc8439), per `draft-irtf-cfrg-xchacha`; not itself an RFC) | 32 B | 24 B  | 16 B | **M.** The sole MANDATORY-to-implement content AEAD for `enc.scheme: 1`; producers **MUST** emit this identifier. The 24-byte random nonce is the safer default for stateless producers. |
| `aes-256-gcm`        | (reserved) AES-256-GCM ([NIST SP 800-38D](https://csrc.nist.gov/pubs/sp/800/38/d/final), [RFC 5116](https://www.rfc-editor.org/rfc/rfc5116))        | —    | —     | —    | **R.** Reserved for a future `enc.scheme` profile targeting RFC-only AEAD constraints. Not part of `enc.scheme: 1`; verifiers MUST reject records using it with `UNSUPPORTED_AEAD_ALG`.  |

The AEAD (authenticated-encryption) property is mandatory: unauthenticated ciphers (e.g. AES-CBC without a MAC, AES-CTR, raw ChaCha20) **MUST NOT** be used and **MUST** be rejected with `UNAUTHENTICATED_CIPHER_FORBIDDEN`. The on-wire spelling is exactly the hyphenated form `xchacha20-poly1305`; alternative spellings (e.g. `xchacha20poly1305` without the internal hyphen) **MUST NOT** be produced. The `enc.nonce` length MUST equal the registered nonce length of `enc.aead` (24 bytes for `xchacha20-poly1305`); a mismatch emits `NONCE_LENGTH_MISMATCH`.

XChaCha20-Poly1305 is the v1 default for practical nonce-safety, not because it has RFC status. A future requirement for an RFC-only content AEAD MUST be handled as a new sealed-PoE construction version (`enc.scheme: 2`); existing `enc.scheme: 1` records MUST continue to mean the XChaCha20-Poly1305 construction pinned in the conformance vectors.

#### KEM identifiers (`enc.kem`)

Both KEMs below are registered under `enc.scheme: 1` from the first release. `enc.kem` selects the per-slot KEM, the per-slot encapsulation shape, and the per-slot KEK derivation. The slot-set MAC, content AEAD, slot shuffle, and constant-time trial-decrypt are KEM-independent.

| Identifier       | Algorithm                                                                                                                                                                                                                                                                                                                                         | Public (encapsulation) key                                            | Ciphertext                                                                                                 | Shared secret | Status                                                                                   |
| ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- | ------------- | ---------------------------------------------------------------------------------------- |
| `x25519`         | X25519 ECDH ([RFC 7748](https://www.rfc-editor.org/rfc/rfc7748))                                                                                                                                                                                                                                                                                  | 32 B                                                                  | 32 B (the per-slot ephemeral public key carried as `slot.epk`)                                             | 32 B          | **M.** The classical, higher-capacity option; every conformant verifier MUST support it. |
| `mlkem768x25519` | X-Wing hybrid KEM ([draft-connolly-cfrg-xwing-kem](https://datatracker.ietf.org/doc/draft-connolly-cfrg-xwing-kem/)): ML-KEM-768 ([FIPS 203](https://csrc.nist.gov/pubs/fips/203/final)) ⊕ X25519 ([RFC 7748](https://www.rfc-editor.org/rfc/rfc7748)), combined with a SHA3-256 combiner ([FIPS 202](https://csrc.nist.gov/pubs/fips/202/final)) | 1216 B (ML-KEM-768 encapsulation key 1184 B ‖ X25519 public key 32 B) | 1120 B (ML-KEM-768 ciphertext 1088 B ‖ X25519 ephemeral public key 32 B), carried chunked as `slot.kem_ct` | 32 B          | **M.** Post-quantum hybrid; the RECOMMENDED producer default.                            |

`mlkem768x25519` is the X-Wing KEM. The shared secrets are combined by `SHA3-256(ss_MLKEM ‖ ss_X25519 ‖ ct_X25519 ‖ pk_X25519 ‖ label)`, where `label` is the six bytes `0x5c 0x2e 0x2f 0x2f 0x5e 0x5c`. The decapsulation key is a 32-byte seed (implicit-rejection KEM); the public key is derived from it. The combiner binds the X25519 ephemeral ciphertext and recipient X25519 public key into the shared secret, which is why the hybrid per-slot KEK derivation uses an empty HKDF salt. The full byte-level construction is normative in [Sealed PoE: multi-recipient encryption](#sealed-poe-multi-recipient-encryption).

`mlkem768x25519` (no internal hyphens) is the registry identifier, matching the X-Wing / age ecosystem spelling; this is a deliberate, documented exception to the otherwise-hyphenated identifier convention. Implementations **MUST** emit and accept exactly this spelling. Producers **SHOULD** default to `mlkem768x25519`; `x25519` is the explicit higher-capacity choice (an X25519 slot is ~82 B versus ~1.2 KB for a hybrid slot, fitting far more recipients in one record's byte budget). Verifiers **MUST** reject an unregistered `enc.kem` value with `UNSUPPORTED_KEM_ALG`, a wrong-length `epk` / reassembled `kem_ct` with `KEM_EPK_LENGTH_MISMATCH` / `KEM_CT_LENGTH_MISMATCH`, and a slot whose shape does not match `enc.kem` with `ENC_SLOT_INVALID_SHAPE`.

The Bech32 human-readable prefix of the recipient public-key encoding is `age1` for `x25519` and `age1pqc` for `mlkem768x25519`. The hybrid prefix is `age1pqc` — **NOT** `age1pq`, which collides with an upstream native ML-KEM-768 + X25519 encoding.

#### Passphrase-KDF identifiers (`enc.passphrase.alg`)

The KDF registry has two layers — the passphrase-style KDF that MAY appear on the wire as `enc.passphrase.alg`, and internal building blocks that MUST NOT appear there.

| Identifier | Algorithm                                                     | Required params                                                                                                                                                                                | Status                                                                                         |
| ---------- | ------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| `argon2id` | Argon2id ([RFC 9106](https://www.rfc-editor.org/rfc/rfc9106)) | `m` (memory KiB, **MUST** be ≥ 65 536 ≈ 64 MiB); `t` (iterations, **MUST** be ≥ 3); `p` (parallelism, **MUST** be ≥ 1). The output length is fixed at 32 bytes and is NOT carried in `params`. | **M.** The sole MANDATORY-to-implement passphrase KDF; v1 producers MUST emit this identifier. |

Argon2id is memory-hard, which raises the cost of offline brute-force against the published parameters, salt, and ciphertext. The `p ≥ 1` floor reflects a deliberate browser-compatibility constraint; security is dominated by the `m × t` product, and with `m ≥ 65 536 KiB` and `t ≥ 3` the margin under `p = 1` is adequate. The accompanying `enc.passphrase.salt` byte string **MUST** be between 16 and 64 bytes inclusive (the 64-byte ceiling reflects the Cardano metadata `bstr` cap, which constrains every `transaction_metadatum` byte string to 64 bytes). Validators **MUST** reject a salt shorter than 16 bytes with `ENC_PASSPHRASE_SALT_TOO_SHORT`, longer than 64 bytes with `ENC_PASSPHRASE_SALT_TOO_LONG`, and `argon2id` params below the minima with `ENC_PASSPHRASE_ARGON2_PARAMS_TOO_LOW`. Implementations MAY enforce non-normative upper bounds against verifier-side DoS, reporting `ENC_PASSPHRASE_PARAMS_EXCEED_POLICY` (a distinct code — the floor and ceiling codes MUST NOT be conflated).

**Internal building-block KDFs (MUST NOT appear as `enc.passphrase.alg`):** `hkdf-sha256` (HKDF-SHA-256, [RFC 5869](https://www.rfc-editor.org/rfc/rfc5869)) is the fixed extract-and-expand construction used for per-slot KEK derivation, slot-set MAC-key derivation, and seed → key derivation (see [Seed and key derivation](#seed-and-key-derivation) and [Sealed PoE: multi-recipient encryption](#sealed-poe-multi-recipient-encryption)). It carries no wire identifier and is not selectable. A record carrying `enc.passphrase.alg = "hkdf-sha256"` MUST be rejected as `ENC_PASSPHRASE_ALG_UNSUPPORTED` — HKDF is designed for high-entropy inputs, not for stretching low-entropy passphrases.

#### Signature algorithms (`COSE_Sign1` protected `alg`)

Record-level signatures are **always OPTIONAL** in CIP-309: authorship is an opt-in claim, never required for a record to verify. A signature's COSE protected `alg` MUST name a registered label; any other label surfaces as `SIGNATURE_UNSUPPORTED` at info severity and does not fail the record. Verification is strict, non-cofactored Ed25519 (RFC 8032 §5.1.7) regardless of which registered label is used (see [Record-level signatures (COSE_Sign1)](#record-level-signatures-cose_sign1)).

| COSE alg | Algorithm                                                                                                                                                                                                                                                         | Status                                                                                                                                                                                                                                                                       |
| -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `-8`     | EdDSA, curve-agnostic ([RFC 9053 §2.2](https://www.rfc-editor.org/rfc/rfc9053#section-2.2), [RFC 8032](https://www.rfc-editor.org/rfc/rfc8032); curve pinned to Ed25519 by the `kty=1`/`crv=6` COSE_Key constraint and the path-1 `kid`-as-public-key convention) | **M.** Mandatory for verifiers; the only `alg` CIP-30 wallets emit on the `signData` path.                                                                                                                                                                                   |
| `-19`    | Ed25519, fully-specified ([RFC 8032 §5.1](https://www.rfc-editor.org/rfc/rfc8032#section-5.1); [RFC 9864 §3.1](https://www.rfc-editor.org/rfc/rfc9864#section-3.1) IANA assignment)                                                                               | **OPT-INFO.** SDK-originated signatures MAY use `-19`. A verifier that implements it verifies it identically to `-8` under the Ed25519 primitive; a verifier that does not surfaces the `sigs[i]` as `SIGNATURE_UNSUPPORTED` and the record's content claim still validates. |
| `-7`     | (reserved) ES256 — ECDSA w/ SHA-256 over P-256 ([RFC 9053 §2.1](https://www.rfc-editor.org/rfc/rfc9053#section-2.1))                                                                                                                                              | **R.** Not standardised in v1; reported as `SIGNATURE_UNSUPPORTED`.                                                                                                                                                                                                          |
| `-49`    | (reserved) ML-DSA-65 ([draft-ietf-cose-dilithium](https://datatracker.ietf.org/doc/draft-ietf-cose-dilithium/))                                                                                                                                                   | **R.** Post-quantum signature; not in v1; reported as `SIGNATURE_UNSUPPORTED`.                                                                                                                                                                                               |

The IANA COSE Algorithms registry marks `-8` (EdDSA, curve-agnostic) as deprecated as of RFC 9864 in favour of the fully-specified `-19`. CIP-309 v1 nonetheless **keeps `alg = -8` as the MANDATORY signature identifier** because CIP-30 wallets emit `alg = -8` on the `signData` path, and v1 pins the curve to Ed25519 explicitly at two layers — the COSE_Key carries `kty = 1` (OKP) and `crv = 6` (Ed25519), and the path-1 32-byte protected-header `kid` convention is unambiguously an Ed25519 public key — so the deprecation's curve-ambiguity concern does not apply. The fully-specified `-19` codepoint is registered alongside `-8` at OPT-INFO tier.

#### Registry scope and provenance

The algorithm identifiers above form the **internal CIP-309 algorithm registry**: they live inside this CIP, are normative for it, and are extended only by a future revision of CIP-309 (a new identifier requires a successor version that lists it). CIP-309 deliberately does **not** propose registering these strings in [CIP-10](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0010/registry.json), because CIP-10 registers integer `transaction_metadatum_label` values — its scope is the top-level integer namespace `309` (already reserved by CIP-10 for "Proof of Existence record"), not the algorithm strings that live inside the value under that label.

COSE signature algorithm identifiers (the integers `-8`, `-19`, `-7`, `-49`) live in the [IANA COSE registry](https://www.iana.org/assignments/cose), not in CIP-309's internal registry, and are referenced by their IANA codepoints when used inside a `COSE_Sign1` protected header. The `rfc9162-sha256` Merkle identifier likewise references the IANA "COSE Verifiable Data Structure Algorithms" registry (codepoint 1).

#### Algorithm agility: the additive-only rule

CIP-309 uses string identifiers for every algorithm slot precisely so the registry can grow without breaking decoders for older records. To add a new identifier:

1. The primitive **MUST** have a stable public reference (RFC / FIPS / CIP / IANA codepoint / named internet-draft). **No novel cryptography** is admissible.
2. Add the identifier to the appropriate registry under [`../registries/`](https://github.com/cardanowall/cip309/blob/main/registries) with its pinned length constant and the typed error code emitted on each failure mode.
3. Ship a byte-pinned conformance vector under [`../conformance/`](https://github.com/cardanowall/cip309/blob/main/conformance) that exercises the new identifier.

Registry additions are **additive** and do **NOT** bump the wire `v` integer: an existing v1 verifier rejects the new identifier with the corresponding `UNSUPPORTED_*` code (or, for an OPT-INFO identifier, surfaces it as info), and a new v1 producer MAY emit the identifier as soon as the revision publishes. The algorithm-agility invariant guarantees that an unrecognised identifier produces a clean typed rejection — never silent acceptance, never a crash. Wire-format `v` bumps are reserved for breaking schema changes (a new REQUIRED key, a removed key, a changed type, or a digest length the current grammar cannot express) — not for registry additions.

**Post-quantum migration is already additive.** Post-quantum protection of the sealed-PoE key path ships in v1: the hybrid KEM `mlkem768x25519` (X-Wing) is registered alongside classical `x25519` under `enc.scheme: 1`, selected per-record via `enc.kem`. A further PQ migration (e.g. adding a standalone `ml-kem-768`, or a `ml-dsa-65` / `slh-dsa-sha2-128s` record signature) is a registry addition under the rule above — it requires no new `enc.scheme` profile and no wire-format version bump.

The following identifiers are **reserved** — they appear in the migration roadmap but MUST NOT be emitted by conformant producers and MUST be rejected by conformant verifiers with the appropriate code until they are registered:

- `ml-kem-768` — NIST ML-KEM-768 ([FIPS 203](https://csrc.nist.gov/pubs/fips/203/final)) used **standalone**, without the X25519 hybrid wrapper. Distinct from the registered hybrid `mlkem768x25519`. Goes in `enc.kem`; rejected by verifiers that do not implement it as `UNSUPPORTED_KEM_ALG`.
- `aes-256-gcm` — AES-256-GCM ([NIST SP 800-38D](https://csrc.nist.gov/pubs/sp/800/38/d/final)), an RFC-only content AEAD reserved for a future `enc.scheme` profile; rejected by v1 verifiers as `UNSUPPORTED_AEAD_ALG`.
- `ml-dsa-65` — NIST ML-DSA ([FIPS 204](https://csrc.nist.gov/pubs/fips/204/final)), a signature alternate to Ed25519; v1 verifiers surface `SIGNATURE_UNSUPPORTED` and the content claim remains valid.
- `slh-dsa-sha2-128s` — NIST SLH-DSA ([FIPS 205](https://csrc.nist.gov/pubs/fips/205/final)), a hash-based signature alternate; v1 verifiers surface `SIGNATURE_UNSUPPORTED` and the content claim remains valid.

#### Forbidden primitives

The following are explicitly excluded. Any code path that introduces one is a defect:

- **Unauthenticated symmetric encryption** — AES-CBC without a separate MAC, AES-CTR without a MAC, raw ChaCha20 without Poly1305, RC4 of any kind. Only AEADs from the registry above; an unauthenticated cipher in `enc.aead` is rejected with `UNAUTHENTICATED_CIPHER_FORBIDDEN`.
- **Non-deterministic CBOR for any signature payload** — all bytes that enter Ed25519 sign / verify MUST be produced by the canonical CBOR encoder (RFC 8949 §4.2.1). Indefinite-length encoding, non-canonical map ordering, and duplicate keys MUST be rejected on decode (see [Canonical CBOR and metadata label 309 carriage](#canonical-cbor-and-metadata-label-309-carriage)).
- **Re-deriving a key from a CIP-30 wallet signature** — CIP-30 wallet signatures are kept for record-signing only; re-deriving a key from a `signData` response is unsound and forbidden (see [Seed and key derivation](#seed-and-key-derivation)).
- **SHA-1, MD5, RIPEMD (any variant)** — not for hashing, not for HMAC, not for HKDF. Producers and verifiers MUST NOT emit or accept these algorithms.

#### CDDL grammar and JSON Schemas

The canonical machine-readable grammar for the record body is the CDDL ([RFC 8610](https://www.rfc-editor.org/rfc/rfc8610)) reproduced below; [`../cddl/cip-309.cddl`](cip-309.cddl) is the extracted canonical copy, and the JSON Schemas under [`../schemas/`](https://github.com/cardanowall/cip309/blob/main/schemas) are the same grammar expressed for JSON tooling. The grammar models the **reassembled record body** — the canonical-CBOR bytes obtained after byte-concatenating the ≤ 64-byte chunk array stored under metadata label 309; the chunk-array transport wrapper is reassembled before structural validation and is not modelled here (see [Canonical CBOR and metadata label 309 carriage](#canonical-cbor-and-metadata-label-309-carriage)).

The grammar and the JSON Schemas model only the **permissive structural superset** of well-formed shapes: the closed map shapes and the core byte lengths. They do **not** express cross-field invariants (e.g. `enc` key-path exclusivity, the items-or-merkle presence rule, algorithm-dependent nonce length, Merkle leaf-count binding) and they do **not** express registry membership of algorithm identifiers — every identifier rule below is the open `tstr` type, deliberately not a closed enum, because the registries above are authoritative for the accepted value set. Those constraints, and the precise typed error code a conformant verifier emits, are the second, typed-error pass over the decoded structure described in [Structural validation, verifier roles, and error codes](#structural-validation-verifier-roles-and-error-codes). A generic CDDL or JSON-Schema tool confirms only that a candidate record matches the permissive superset; full conformance requires the typed pass.

```cddl
; A conformant PoE record MUST carry at least one of `items` (>= 1 entry) or
; `merkle` (>= 1 entry); a record with both arrays absent (or both present but
; empty) is rejected as SCHEMA_EMPTY_RECORD. The invariant is enforced in the
; typed pass, not at the CDDL layer.
;
; Extension-key tolerance: keys matching the `^x-.+` or `^[a-z]+-.+` patterns
; are accepted; unknown keys outside either pattern are rejected as
; SCHEMA_UNKNOWN_FIELD by the typed pass. The CDDL admits any
; extension-key text string under the open `extension-key` rule below.
; Extension values are typed as `metadatum`, mirroring the parent
; transaction_metadata envelope: the ledger admits only the recursive
; metadatum type under label 309, so every field — base or
; extension — MUST be a metadatum or it cannot reach chain.
;
; A `metadatum` matches the Cardano ledger's transaction_metadatum
; recursive type (no floats, no tags, bstr/tstr <= 64 bytes). Every
; field a CIP-309 record carries — base or extension — MUST be a
; metadatum, because the entire record sits inside transaction_metadata
; under label 309 and the ledger rejects non-metadatum values at
; submission. The ledger CDDL definition of transaction_metadatum is
; the normative source for this type.
metadatum =
    { * metadatum => metadatum }
  / [ * metadatum ]
  / int
  / bstr .size (0..64)
  / tstr .size (0..64)

poe-record = {
  poe-common,
  ? "items": [ 1* item-entry ],
  ? "crit":  [ 1* tstr ],
  * extension-key => metadatum
}

poe-common = (
  "v": 1,
  ? "merkle": [ 1* merkle-commit ],
  ? "supersedes": bytes32,
  ? "sigs": [ 1* sig-entry ],
)

extension-key = tstr .regexp "^x-.+"
              / tstr .regexp "^[a-z]+-.+"

item-entry = {
  "hashes": hash-map,
  ? "uris": [ 1* uri-chunk-array ],
  ? "enc": enc,
}

; A non-empty CBOR map keyed by a content-hash algorithm identifier (text string
; from the content-hash registry) with the 32-byte digest as the value. Map-key
; uniqueness (RFC 8949 §3.1) makes duplicate algorithms structurally impossible.
hash-map = { + content-hash-alg => bytes32 }

; A merkle-commit binds the record to an ordered leaf list via a registered
; list-commitment algorithm. The list-commitment registry is disjoint
; from the content-hash registry: a `merkle[i].alg` text string MUST be a value
; from the list-commitment registry and MUST NOT be a content-hash identifier.
; `leaf_count` is REQUIRED and binds the on-chain commitment to the off-chain
; leaves-list size (rejected as SCHEMA_MERKLE_LEAF_COUNT_MISMATCH on mismatch).
merkle-commit = {
  "alg":        merkle-commit-alg,
  "root":       bytes32,
  "leaf_count": uint,
  ? "uris":     [ 1* uri-chunk-array ],
}

; `enc` is modelled as a permissive superset: a single map rule admits both
; the recipient-slot key path and the passphrase key path. Cross-field
; invariants are NOT expressed in the CDDL; the typed pass
; enforces them. Specifically:
;   - if `slots` is present, then `kem` and `slots_mac` are REQUIRED, and
;     `passphrase` is FORBIDDEN;
;   - if `passphrase` is present, then `kem` / `slots` / `slots_mac` are
;     FORBIDDEN;
;   - exactly one of `slots` or `passphrase` MUST be present
;     (ENC_NO_KEY_PATH and ENC_EXCLUSIVITY_VIOLATION cover the absence /
;     conflict cases).
enc = {
  enc-common,
  ? "kem":        kem-alg,
  ? "slots":      [ 1* slot ],
  ? "slots_mac":  bytes32,
  ? "passphrase": passphrase-block,
}

enc-common = (
  "scheme": 1,
  "aead":   aead-alg,
  "nonce":  bstr,
)

; A slot is one of two KEM-discriminated shapes; `enc.kem` selects which.
; The CDDL admits either shape structurally — the typed pass binds the
; chosen shape to `enc.kem` and emits ENC_SLOT_INVALID_SHAPE for a slot whose
; encapsulation fields do not match `enc.kem`, and the "no mixing" rule
; (every slot in one envelope shares one `enc.kem`) is enforced there. `wrap`
; is the KEM-independent 48-byte ChaCha20-Poly1305-wrapped CEK in both shapes.
slot = classical-slot / hybrid-slot

; enc.kem = "x25519": the per-slot X25519 ephemeral public key + wrapped CEK.
classical-slot = {
  "epk":  bytes32,
  "wrap": bytes48,
}

; enc.kem = "mlkem768x25519": the X-Wing ciphertext (1120 bytes) chunked into
; <=64-byte byte-strings, plus the wrapped CEK. There is NO `epk` — the X25519
; ephemeral is the trailing 32 bytes of the X-Wing ciphertext inside `kem_ct`.
; The chunks reassemble to exactly 1120 bytes; the typed pass enforces the
; reassembled length (KEM_CT_LENGTH_MISMATCH).
hybrid-slot = {
  "kem_ct": [ 1* bstr .size (1..64) ],
  "wrap":   bytes48,
}

; The `passphrase-block` rule pins `alg` as the open `kdf-alg` type (consistent
; with `merkle-commit-alg`, `aead-alg`, `kem-alg`): the CDDL accepts any text
; string and the typed pass enforces registry membership, emitting
; `ENC_PASSPHRASE_ALG_UNSUPPORTED` for an unknown identifier
; rather than a generic CDDL schema-mismatch. The `params` map is pinned as a
; CLOSED map for the registered alg:
;   - "argon2id" — params is exactly { m: uint, t: uint, p: uint }
; Extra keys in `params` MUST be rejected as `SCHEMA_UNKNOWN_FIELD`.
passphrase-block = {
  "alg":    kdf-alg,
  "salt":   bstr .size (16..64),
  "params": { "m": uint, "t": uint, "p": uint },
}

; A sig-entry is a closed CBOR map. "cose_sign1" is REQUIRED and carries the chunked
; CBOR-encoded COSE_Sign1 produced by the signer. "cose_key" is OPTIONAL and,
; when present, carries the chunked CBOR-encoded COSE_Key for the CIP-30 wallet
; path; it is omitted for the in-signature `kid` (identity-key) path. The field
; names describe what the bytes are on the wire: `cose_sign1` = COSE_Sign1,
; `cose_key` = COSE_Key. No other keys are permitted. The normative
; path-selection rules make path 1 (32-byte protected-header `kid`) and
; path 2 (`cose_key` side-channel) mutually exclusive at the wire level;
; SIG_ENTRY_KID_COSE_KEY_CONFLICT rejects records carrying both.
sig-entry = {
  "cose_sign1":  bytes-chunk-array,
  ? "cose_key":  bytes-chunk-array,
}

bytes-chunk-array = [ 1* bytes-chunk ]
bytes-chunk = bstr .size (1..64)

; A uri-chunk-array reconstructs to one absolute URI string. Each chunk is
; a tstr (CBOR major type 3) of <= 64 bytes — the Cardano ledger's tstr cap
; inside transaction_metadatum. Producers MUST NOT split a
; multi-byte UTF-8 codepoint across chunks.
uri-chunk-array = [ 1* uri-chunk ]
uri-chunk = tstr .size (1..64)

bytes32 = bstr .size 32

; bytes48 is the wrap length under enc.scheme: 1: 32-byte CEK + 16-byte
; ChaCha20-Poly1305 tag. The per-slot wrap is KEM-independent — identical for
; `x25519` and `mlkem768x25519` slots. A future enc.scheme profile with
; a different wrap AEAD MAY redefine this constant.
bytes48 = bstr .size 48

; Algorithm identifier strings are CBOR text strings (major type 3). The CDDL
; type is deliberately the open `tstr` rather than a closed enum: the algorithm
; registries are authoritative for the set of accepted values, and a verifier MUST
; emit the typed code from those registries (`UNSUPPORTED_HASH_ALG`,
; `UNSUPPORTED_MERKLE_COMMIT_ALG`, `UNSUPPORTED_AEAD_ALG`, `UNSUPPORTED_KEM_ALG`,
; `ENC_PASSPHRASE_ALG_UNSUPPORTED`) for any unrecognised value — not a generic
; CDDL schema-mismatch error. Conformant validators perform the registry-membership
; check in the domain pass, after the CDDL pass has confirmed the field is a
; CBOR text string of any value.
content-hash-alg   = tstr  ; see content-hash registry  (e.g. "sha2-256", "blake2b-256")
merkle-commit-alg  = tstr  ; see list-commitment registry (e.g. "rfc9162-sha256")
aead-alg           = tstr  ; see AEAD registry
kem-alg            = tstr  ; see KEM registry
kdf-alg            = tstr  ; see KDF registry

; ---------------------------------------------------------------------------
; Cross-field invariants (prose-only, NOT in CDDL).
;
; The `enc` rule admits any combination of `kem` / `slots` / `slots_mac` /
; `passphrase` keys at the CDDL layer; the following cross-field invariants are
; enforced by the typed-error pass, not the grammar:
;
;   - If `slots` is present, then `kem` and `slots_mac` are REQUIRED
;     (ENC_KEM_REQUIRED, ENC_SLOTS_MAC_REQUIRED) and `passphrase` is FORBIDDEN
;     (ENC_EXCLUSIVITY_VIOLATION).
;   - If `passphrase` is present, then `kem`, `slots`, and `slots_mac` are all
;     FORBIDDEN (ENC_EXCLUSIVITY_VIOLATION).
;   - Exactly one of `slots` or `passphrase` MUST be present; both absent →
;     ENC_NO_KEY_PATH.
;   - `slots_mac` present without `slots` → ENC_SLOTS_REQUIRED.
;
; Implementer guidance (non-normative). Implementations MAY consume this CDDL
; directly with a generic CDDL library; conformant typed-error reporting
; requires a second pass over the decoded structure to emit the precise codes
; (ENC_EXCLUSIVITY_VIOLATION, ENC_NO_KEY_PATH, ENC_KEM_REQUIRED,
; EXTENSION_UNSUPPORTED_CRITICAL, SCHEMA_UNKNOWN_FIELD,
; SCHEMA_MERKLE_LEAF_COUNT_MISMATCH, SIG_ENTRY_INVALID_SHAPE,
; SIG_ENTRY_KID_COSE_KEY_CONFLICT, SIG_PRIVATE_KEY_LEAKED, and so on). A
; single-pass implementation that emits a generic CDDL-mismatch error is
; conformant to the wire format but is NOT conformant to the typed-error
; contract; conformant verifiers MUST emit the precise codes.
; ---------------------------------------------------------------------------
```

### Structural validation, verifier roles, and error codes

CIP-309 correctness is checked in three layers. Each layer is a strict superset of the one before it, and each can be implemented and shipped independently.

1. **Structural validator (Part A).** A pure function over the reassembled CBOR bytes that claim to be a CIP-309 record. It performs schema and domain-rule conformance only: it MUST NOT touch the network, MUST NOT verify any signature cryptographically, and MUST NOT decrypt. It is profile-agnostic — it parses the full v1 schema (the grammar in [`../cddl/cip-309.cddl`](cip-309.cddl)) regardless of which subset a downstream verifier validates end-to-end.
2. **Public verifier (Part B, default mode).** Layers on top of the structural validator. Given a Cardano transaction reference it fetches the transaction metadata from a public blockchain explorer, runs the structural validator, verifies every embedded Ed25519 record signature, and optionally fetches and hash-checks plaintext content at `ar://` / `ipfs://` URIs. It does not decrypt.
3. **Recipient verifier (Part B, sealed-decrypt mode).** A public verifier that additionally holds one or more recipient KEM private keys — a 32-byte X25519 scalar for `x25519`, or a 32-byte X-Wing decapsulation seed for `mlkem768x25519` — and performs sealed-PoE decryption plus post-decryption plaintext-hash recomputation (see [Sealed PoE: multi-recipient encryption](#sealed-poe-multi-recipient-encryption)).

All three layers MUST run **without contacting any single-operator infrastructure**. This is a binding property of CIP-309 — a proof verifies given only the transaction metadata, optionally the content bytes, and a public blockchain explorer. It is restated as the service-independence property at the end of this section.

The authoritative error catalogue is the machine-readable registry [`../registries/error-codes.json`](https://github.com/cardanowall/cip309/blob/main/registries/error-codes.json); the conformance vectors that pin each failure mode to its code live under [`../conformance/`](https://github.com/cardanowall/cip309/blob/main/conformance) (validator-rejection cases in [`../conformance/validator/`](https://github.com/cardanowall/cip309/blob/main/conformance/validator), cross-service / service-independence cases in [`../conformance/cross-service/`](https://github.com/cardanowall/cip309/blob/main/conformance/cross-service)). A conformant implementation MUST emit exactly the SCREAMING_SNAKE_CASE codes defined there for the failure modes defined there; it MUST NOT introduce lowercase synonyms, `schema_*`-prefixed parser-internal codes, or free-form reason strings. The families summarized below are the index into that registry, not a substitute for it.

#### Part A — the structural validator

##### Function shape and purity

The structural validator is a single function from a byte string to a result:

```ts
validatePoeRecord(bytes: Uint8Array): ValidationResult

type ValidationResult =
  | { valid: true;  record: PoeRecord; warnings?: ValidationIssue[]; info?: ValidationIssue[] }
  | { valid: false; issues: ValidationIssue[] };

interface ValidationIssue {
  path: string;     // dotted path into the record (e.g. "items.0.hashes.0.alg")
  code: string;     // SCREAMING_SNAKE_CASE code from the registry
  severity?: 'error' | 'warning' | 'info';  // defaults to 'error' if omitted
  message: string;  // human-readable explanation including the offending value
}
```

The validator MUST be **pure**: it performs no I/O, allocates no global state, and emits deterministic output for any given input. All issues MUST be sorted by `path` so that output is byte-stable across runs and across language implementations. A record's `valid: true` verdict MUST NOT be reported when any `error`-severity issue is present; `warning`- and `info`-severity issues MUST be surfaced but MUST NOT by themselves fail the record.

The reassembly of the chunked record body — byte-concatenation of the metadata-label-309 array of ≤ 64-byte byte strings — and the unwrapping of the carrying transaction's auxiliary data happen **before** the validator runs (see [Canonical CBOR and metadata label 309 carriage](#canonical-cbor-and-metadata-label-309-carriage)); the validator receives the reassembled record body and never re-encodes it.

##### Pipeline

The validator runs a fixed pipeline; any step that produces an `error`-severity issue still allows later steps to run, and all issues are collected and emitted together (sorted by `path`).

1. **Canonical CBOR decode.** The bytes MUST be decoded with a canonical decoder enforcing the deterministic-encoding rules of RFC 8949 §4.2.1: definite lengths, bytewise-lexicographically sorted map keys, no duplicate keys, valid UTF-8 text strings, minimal integer encodings. Any decode failure — including non-canonical ordering, indefinite-length encodings, and duplicate map keys — surfaces as the single code `MALFORMED_CBOR`. There is no separate duplicate-key code: canonical-decode rejection covers it.
2. **Schema parse.** The decoded value is run through a closed-schema parser ([`../schemas/`](https://github.com/cardanowall/cip309/blob/main/schemas)). The schema is the structural authority: type checks, length bounds (the 64-byte chunk limit on chunked byte/text arrays, the 32-byte length checks on `supersedes` and on commitment roots), and a strict object mode that rejects unknown fields. The schema imposes **no** numeric cap on `items[]`, `sigs[]`, or `slots[]` entry counts — the only ceiling is the ledger's maximum transaction size, enforced at submission by Cardano nodes; a validator MUST NOT emit an error solely because an entry count is high.
3. **Domain checks.** A second pass enforces cross-field constraints the schema cannot express ergonomically: registry membership for every algorithm identifier, URI reconstruction and scheme checks, per-slot key-material and wrap lengths, COSE structural decode, parallel-array length, and `crit[]` shape. The domain pass walks each item, then the record-level `sigs[]`, then `merkle[]`.
4. **Result emission.** If any `error`-severity issue was collected, the record is reported `valid: false` with the full sorted issue list. Otherwise it is reported `valid: true` with the decoded record plus any `warnings` / `info` issues.

##### Error families (Part A)

Every code below is emitted by `validatePoeRecord` and carries `severity: error` unless noted. The registry [`../registries/error-codes.json`](https://github.com/cardanowall/cip309/blob/main/registries/error-codes.json) is authoritative for the complete list and the exact trigger of each code.

| Family                                 | Codes                                                                                                                                                                                                                                                                                                                                            | Triggered by                                                                                                                                                                                                                                                                                                                                                                                                                 |
| -------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `MALFORMED_CBOR`                       | `MALFORMED_CBOR`                                                                                                                                                                                                                                                                                                                                 | any canonical-CBOR decode failure (RFC 8949 §4.2.1) — non-canonical ordering, indefinite length, duplicate keys, invalid UTF-8, non-minimal integers.                                                                                                                                                                                                                                                                        |
| `SCHEMA_*`                             | `SCHEMA_TYPE_MISMATCH`, `SCHEMA_MISSING_REQUIRED`, `SCHEMA_UNKNOWN_FIELD`, `SCHEMA_INVALID_LITERAL`, `SCHEMA_EMPTY_RECORD`                                                                                                                                                                                                                       | wrong CBOR type; a REQUIRED field absent; an unknown field in a closed map; `v` ≠ `1`; a record committing to neither `items[]` nor `merkle[]` with ≥ 1 entry.                                                                                                                                                                                                                                                               |
| `HASH_*`                               | `HASH_DIGEST_LENGTH_MISMATCH`, `UNSUPPORTED_HASH_ALG`, `UNSUPPORTED_MERKLE_COMMIT_ALG`                                                                                                                                                                                                                                                           | a digest length ≠ the length pinned for its algorithm; a `hashes` key outside the hash-algorithm registry; a `merkle[].alg` outside the Merkle-commitment registry.                                                                                                                                                                                                                                                          |
| `ENC_*` (envelope shape)               | `UNAUTHENTICATED_CIPHER_FORBIDDEN`, `UNSUPPORTED_AEAD_ALG`, `NONCE_LENGTH_MISMATCH`, `UNSUPPORTED_ENVELOPE_SCHEME`, `ENC_SLOTS_EMPTY`, `ENC_SLOT_INVALID_SHAPE`, `ENC_SLOTS_MAC_INVALID_LENGTH`, `ENC_SLOTS_MAC_REQUIRED`, `ENC_SLOTS_REQUIRED`, `ENC_EXCLUSIVITY_VIOLATION`, `ENC_NO_KEY_PATH`, `ENC_KEM_REQUIRED`, `ENC_REQUIRES_CONTENT_HASH` | `enc.aead` names an unauthenticated cipher family, or an unknown AEAD; nonce length ≠ the AEAD's (24 for XChaCha20-Poly1305); `enc.scheme` ≠ `1`; empty / malformed / mutually-exclusive key-path violations; `slots` without `slots_mac` (or vice versa); `slots` without `kem`; an `enc`-bearing item carrying no content-hash entry.                                                                                      |
| `ENC_PASSPHRASE_*`                     | `ENC_PASSPHRASE_ALG_UNSUPPORTED`, `ENC_PASSPHRASE_SALT_TOO_SHORT`, `ENC_PASSPHRASE_SALT_TOO_LONG`, `ENC_PASSPHRASE_ARGON2_PARAMS_TOO_LOW`, `ENC_PASSPHRASE_PARAMS_EXCEED_POLICY`                                                                                                                                                                 | `enc.passphrase.alg` outside the KDF registry (`{argon2id}`); salt length outside `[16, 64]`; Argon2id parameters below the floor (`m ≥ 65536`, `t ≥ 3`, `p ≥ 1`); parameters above an operator-configured upper bound (policy-dependent, not a wire MUST).                                                                                                                                                                  |
| `KEM_*`                                | `UNSUPPORTED_KEM_ALG`, `KEM_EPK_LENGTH_MISMATCH`, `KEM_CT_LENGTH_MISMATCH`, `WRAP_LENGTH_MISMATCH`                                                                                                                                                                                                                                               | `enc.kem` outside `{x25519, mlkem768x25519}`; `slot.epk` ≠ 32 bytes (`x25519`); reassembled `slot.kem_ct` ≠ 1120 bytes (`mlkem768x25519`); `slot.wrap` ≠ 48 bytes. All four are pure byte-length checks; the validator runs no decapsulation.                                                                                                                                                                                |
| `SIG_*`                                | `MALFORMED_SIG_COSE_SIGN1`, `SIGNATURE_UNSUPPORTED` (info), `SIG_ENTRY_INVALID_SHAPE`, `SIG_ENTRY_KID_COSE_KEY_CONFLICT`, `SIG_PRIVATE_KEY_LEAKED`                                                                                                                                                                                               | a `sigs[i].cose_sign1` blob that is not a 4-element COSE_Sign1, or carries a non-null (attached) payload, or carries a malformed inline `cose_key`; an unrecognized signature `alg` (tagged, not rejected); a `sigs[i]` entry that is not the closed `{cose_sign1, ?cose_key}` map; both an in-signature `kid` and an inline `cose_key` present (mutually exclusive); a private-key label leaking into an inline `cose_key`. |
| `MERKLE_*`                             | `UNSUPPORTED_MERKLE_COMMIT_ALG` (Part A)                                                                                                                                                                                                                                                                                                         | a `merkle[].alg` outside the Merkle-commitment registry. (The Merkle codes that require off-chain leaves — root recomputation, leaf-count binding, leaves availability — are verifier-layer codes, below.)                                                                                                                                                                                                                   |
| `URI_*`                                | `INVALID_URI`, `CHUNK_TOO_LARGE`                                                                                                                                                                                                                                                                                                                 | a reconstructed `uri-chunk-array` that is not valid UTF-8, is not an absolute URI per RFC 3986 §4.3, carries a fragment, or names a scheme outside the closed fetch set `{ar://, ipfs://}`; a chunk outside `[1, 64]` bytes.                                                                                                                                                                                                 |
| `SUPERSEDES_*` / `CRIT_*` / extensions | `SUPERSEDES_TX_INVALID_LENGTH`, `CRIT_SHAPE_INVALID`, `EXTENSION_UNSUPPORTED_CRITICAL`                                                                                                                                                                                                                                                           | `supersedes` is bytes but ≠ 32 bytes; a `crit[]` entry that is a base key, fails the extension-key regex, names an absent field, or duplicates another; a well-formed `crit[]` entry naming an extension this verifier does not implement.                                                                                                                                                                                   |

A small number of cross-field rules — content-commitment presence, digest length, nonce length, key-path exclusivity, the chunk-size limit, the `sigs[i]` map shape, and the `supersedes` length — MAY be encoded as schema refinements rather than in the domain pass; either way the validator MUST surface the canonical code, never a parser-internal code (`invalid_type`, `too_small`, …).

##### Closed schema and forward compatibility

v1 records use a closed map schema. Unknown keys at any level are invalid, and unknown values in the cryptographic registries are invalid. The governing principle is: **never accept what a verifier cannot reproduce, and never create an open-ended metadata surface under label 309.** Two behaviours follow:

- **Reject-and-fail (security-critical).** A future protocol major (`v ≠ 1`) MUST be rejected (`SCHEMA_INVALID_LITERAL`); an unknown `enc.aead` / `enc.passphrase.alg` / `enc.kem` MUST be rejected (the corresponding `UNSUPPORTED_*` / `*_UNSUPPORTED` code); an unknown content-hash or Merkle-commitment identifier MUST be rejected; a non-null COSE_Sign1 payload MUST be rejected (`MALFORMED_SIG_COSE_SIGN1` — detached-only); a private-key label in an inline `cose_key` MUST be rejected (`SIG_PRIVATE_KEY_LEAKED`); a critical extension the verifier does not implement MUST be rejected (`EXTENSION_UNSUPPORTED_CRITICAL`, with IETF precedent in RFC 7515 §4.1.11 and RFC 9052 §3.1); and a field outside the closed grammar MUST be rejected (`SCHEMA_UNKNOWN_FIELD`).
- **Accept-and-tag (unverifiable signature only).** An unrecognized COSE_Sign1 `alg` MUST be tagged `SIGNATURE_UNSUPPORTED` (severity `info`, not `error`) on the offending `sigs[i]` entry and MUST NOT fail the record on that ground alone. The content claim — the on-chain `hashes` commitments — is structurally valid regardless of which signature algorithms a verifier supports. The signature case is the only accept-and-tag case in v1: an unverifiable cipher/KEM/KDF would mean claiming to have verified cryptography the verifier cannot reproduce, so those reject hard, whereas an unverifiable signature leaves the proof-of-existence claim intact.

##### Service-independence of the validator

Because the validator is a pure function, anyone holding a CIP-309 byte string can validate it offline — no service, no API key, no telemetry. This makes it usable by producers pre-submission, by third-party verifiers built against the public vectors, and by archival tools confirming long-term well-formedness. Implementations in different languages MUST reproduce the same algorithm and the same error codes byte-exact; a record that validates in one language but not another is a conformance bug.

#### Part B — the public verifier and the recipient verifier

The verifier accepts a Cardano transaction reference plus a small set of optional inputs and produces a structured report. A sibling entry point runs the same pipeline from the structural-validator step onward over caller-supplied label-309 metadata bytes plus a block-info tuple (existence, confirmation depth, block time/slot) — the path a server-rendered viewer uses to display on-chain data without a render-time chain fetch.

##### Inputs

The relevant optional inputs are:

- An ordered Cardano explorer chain plus an optional fallback explorer, for resolving the transaction.
- Ordered Arweave and IPFS gateway chains, for resolving `ar://` / `ipfs://` URIs.
- A confirmation-depth threshold (deployment policy; RECOMMENDED ≥ 15 blocks ≈ 5 minutes, raised for high-value notarisation).
- A `denyHosts` list of hosts that MUST NOT be contacted (see the service-independence property).
- A `maxFetchBytes` per-URI ceiling (default 64 MiB) the verifier MUST enforce incrementally during streaming.
- A `verifyMerkle` master switch (default true) that, when false, suppresses every outbound URI/leaves fetch so a Merkle- or sealed-bearing record renders from indexed CBOR alone.
- A `decryption[]` array whose entries are a discriminated union keyed by the on-wire key path: `recipientSecretKey` (the recipient KEM private key — a 32-byte X25519 scalar or a 32-byte X-Wing decapsulation seed) for the `enc.slots` path, or `passphrase` for the `enc.passphrase` path. Supplying the wrong shape for the on-wire path MUST emit `WRONG_DECRYPTION_INPUT_SHAPE`.
- Optional out-of-band ciphertext bytes and out-of-band Merkle leaves-list bytes, keyed by item / commit index, used when a producer chose out-of-band delivery.

CIP-309 production is mainnet-only: the report's network identifier is the constant `cardano:mainnet`, and the verifier MUST NOT trust any network value from the record body (records carry none).

##### Pipeline

The verifier executes the following steps in order; an `error`-verdict step short-circuits the rest. Every outbound network call MUST pass through a single recording wrapper (see the service-independence property).

1. **Resolve the transaction.** Resolve via the configured explorer chain — a public, open Cardano explorer; an open indexer API (for example, a Koios-compatible endpoint) and a freemium explorer API (for example, Blockfrost) are non-normative examples, and either suffices. The verifier MUST fetch the **raw on-chain transaction CBOR**, not the explorer's metadata-JSON projection. The JSON projection is lossy — it discards map-key ordering, definite-vs-indefinite length, integer/float/sign discrimination, and bytes-vs-text discrimination — so a verifier that re-encoded from it could not reproduce the byte-exact signing input, and every Ed25519 verification on conforming records would fail. The verifier unwraps the transaction's auxiliary data (CBOR tag 259 for post-Alonzo / Conway transactions, with a bare untagged map accepted as the pre-Alonzo fallback; any other tag at that position MUST be rejected as `MALFORMED_CBOR`) and byte-concatenates the label-309 chunk array to reconstruct the record body, returning the concatenated bytes raw with no re-encode pass. If the resolved transaction has no metadata under label 309, the verifier emits `METADATA_NOT_FOUND`; if every explorer in the chain is unreachable or returns a definitive "no metadata", it emits `PROVIDER_UNAVAILABLE` (network class).
2. **Structurally validate.** Run `validatePoeRecord` over the reassembled bytes. A validator rejection short-circuits the report with verdict `failed` (integrity class) and the validator's issue list.
3. **Check confirmation depth.** A transaction below the verifier's confirmation-depth threshold MUST be reported with `INSUFFICIENT_CONFIRMATIONS` and verdict `pending` (NOT `failed`): the record is structurally well-formed and may settle on retry. The threshold guards the orphaned-block reorg window under Ouroboros Praos; a verifier that reported depth-1 records as valid would let an attacker obtain a "valid" verdict on both sides of a fork.
4. **Verify record signatures (strict Ed25519, detached-only).** For each `sigs[i]`: concatenate the `cose_sign1` chunks, decode the 4-element COSE_Sign1 (non-null payload → `MALFORMED_SIG_COSE_SIGN1`), preserve the producer's original `protected` bytes verbatim, and rebuild the canonical `Sig_structure` with `external_aad = h''` and a `to_sign` of the 25-byte UTF-8 domain prefix `cardano-poe-record-sig-v1` concatenated with the canonical CBOR of the record body **with `sigs` removed**. Resolve the signer's 32-byte Ed25519 public key via exactly one of the two mutually-exclusive paths (in-signature protected-header `kid`, or the inline `cose_key` CIP-30 wallet side-channel); failure to resolve → `SIGNER_KEY_UNRESOLVED`. Verify with **strict** Ed25519 per RFC 8032 §5.1.7 — canonical R/S, low-order public-key rejection, no cofactor multiplication; the cofactored / ZIP-215 variant MUST NOT be used. A failed verification → `SIGNATURE_INVALID`. For a wallet-path signature, the verifier MUST additionally recompute `network_header || Blake2b-224(pubkey)` and compare it to the protected-header `address`; a mismatch (or a missing `address`) → `WALLET_ADDRESS_MISMATCH`, distinct from `SIGNATURE_INVALID`. An unrecognized signature `alg` surfaces as `SIGNATURE_UNSUPPORTED` (info). Record signatures are OPTIONAL: a public hash-only PoE remains valid even when every signature entry is unverifiable; the proof-of-existence claim rests on the on-chain commitment, not on any identity binding.
5. **Fetch and hash-check content / Merkle leaves.** For each non-`enc` item that proceeds to fetch, the verifier resolves the item's URIs against the scheme-appropriate gateway chain, enforcing `maxFetchBytes` incrementally and trying gateways in order; a per-attempt failure is `URI_FETCH_FAILED` (warning), an exhausted chain is `CONTENT_UNAVAILABLE` (error, network class). It then recomputes every digest in `item.hashes` (registry `{sha2-256, blake2b-256}`) over the fetched bytes and emits `URI_INTEGRITY_MISMATCH` on any mismatch. A URI scheme outside `{ar://, ipfs://}` that bypassed structural validation is refused defence-in-depth with `URI_TARGET_FORBIDDEN`. For each `merkle[i]`, the verifier obtains the leaves-list (from the supplied bytes or by fetching `merkle[i].uris[]`), validates its `format` and `leaf_count` against the on-chain commitment (`SCHEMA_MERKLE_LEAVES_FORMAT_UNSUPPORTED` / `SCHEMA_MERKLE_LEAVES_MALFORMED` / `SCHEMA_MERKLE_LEAF_COUNT_MISMATCH`), recomputes the RFC 9162 §2.1.1 root, and compares byte-exact (`MERKLE_ROOT_MISMATCH`); a missing leaves-list is the non-fatal `MERKLE_LEAVES_UNAVAILABLE` (warning). A verifier that does not implement Merkle-fold records each commitment as `MERKLE_UNSUPPORTED` — `info` when the record also carries an `items[]` content claim the verifier validated, `error` for the merkle-only case.
6. **Decrypt (recipient verifier only).** For each `decryption[i]` the verifier acquires the ciphertext (from supplied out-of-band bytes, or by fetching `item.uris[]`; neither available for an `enc`-bearing item → `CIPHERTEXT_UNAVAILABLE`) and dispatches on the on-wire key path. The two paths are mutually exclusive. On the `slots` path it runs the sealed-PoE unwrap (per [Sealed PoE: multi-recipient encryption](#sealed-poe-multi-recipient-encryption)): per-slot trial-decrypt of `wrap` (all slots reject → `WRONG_RECIPIENT_KEY`), slot-set MAC recomputation (mismatch → `TAMPERED_HEADER`), and content AEAD with AAD `nonce || slots_mac` (tag failure → `TAMPERED_CIPHERTEXT`). On the `passphrase` path it derives the CEK from the on-chain Argon2id parameters (a runtime KDF rejection → `KDF_DERIVATION_FAILED`) and AEAD-decrypts with empty AAD; a wrong passphrase is indistinguishable from a tampered ciphertext and MUST surface as `TAMPERED_CIPHERTEXT`. After a successful unwrap on either path, the verifier MUST recompute every digest in `item.hashes` over the recovered plaintext and report `plaintextHashOk` (mismatch → `URI_INTEGRITY_MISMATCH`). Because every `enc`-bearing item MUST carry at least one content-hash entry, `plaintextHashOk` is always a concrete boolean.
7. **Resolve `supersedes` (optional, one hop).** When present, the verifier MAY perform a single-hop existence check of the prior transaction; it MUST NOT recurse (a DoS vector) and MUST NOT treat the pointer as an authoritative invalidation. Supersedence is an advisory pointer; the chain remains append-only and both records remain cryptographically valid.
8. **Emit the report.** The machine verdict MUST be one of `valid | pending | failed`, with a four-state exit code so callers can distinguish record-attributable failures from transient operational ones without parsing the structured report: `valid` → exit 0; `failed` (integrity / structural / signature / Merkle-mismatch / service-independence-violation class) → exit 1; `failed` (network class — `CONTENT_UNAVAILABLE`, `PROVIDER_UNAVAILABLE`) → exit 2; `pending` (`INSUFFICIENT_CONFIRMATIONS`) → exit 3; verifier-host runtime failures that are not record-attributable → exit 4 and higher. The report MUST include a complete audit trail of every outbound network call (URL, method, status, byte count, purpose); a verifier that omits or pre-filters this trail cannot prove service-independence.

##### Error families (Part B)

The verifier-layer codes are never emitted by the structural validator; they appear only in the verifier's report. The registry [`../registries/error-codes.json`](https://github.com/cardanowall/cip309/blob/main/registries/error-codes.json) is authoritative.

| Family                  | Representative codes                                                                                                                                                                                                                                  | Triggered by                                                                                                                                                                                                               |
| ----------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| explorer / metadata     | `METADATA_NOT_FOUND`, `PROVIDER_UNAVAILABLE`, `INSUFFICIENT_CONFIRMATIONS` (pending)                                                                                                                                                                  | no label-309 metadata on the resolved tx; every explorer unreachable; on-chain but below the confirmation-depth threshold.                                                                                                 |
| `SIG_*` (cryptographic) | `SIGNATURE_INVALID`, `SIGNER_KEY_UNRESOLVED`, `WALLET_ADDRESS_MISMATCH`                                                                                                                                                                               | strict-Ed25519 verification returned false; no key-resolution path yielded a 32-byte public key; a wallet-path signature's `address` does not bind to the resolved key.                                                    |
| `URI_*` / content       | `URI_INTEGRITY_MISMATCH`, `URI_FETCH_FAILED` (warning), `CONTENT_UNAVAILABLE`, `URI_TARGET_FORBIDDEN`, `CIPHERTEXT_UNAVAILABLE`                                                                                                                       | fetched/decrypted bytes do not match the `hashes` commitment; a single gateway attempt failed; every gateway exhausted; a URI scheme outside the closed fetch set; no path to obtain ciphertext for an `enc`-bearing item. |
| `MERKLE_*` / leaves     | `MERKLE_ROOT_MISMATCH`, `MERKLE_LEAVES_UNAVAILABLE` (warning), `MERKLE_UNSUPPORTED` (dual), `SCHEMA_MERKLE_LEAF_COUNT_MISMATCH`, `SCHEMA_MERKLE_LEAVES_FORMAT_UNSUPPORTED`, `SCHEMA_MERKLE_LEAVES_MALFORMED`, `MERKLE_LEAVES_INFORMATIVE_FORM` (info) | recomputed root ≠ on-chain root; leaves-list expected but unavailable; verifier does not implement Merkle-fold; leaf-count / format / shape disagreement; informative JSON projection accepted as a fallback.              |
| `ENC_*` / decrypt       | `WRONG_DECRYPTION_INPUT_SHAPE`, `WRONG_RECIPIENT_KEY`, `TAMPERED_HEADER`, `TAMPERED_CIPHERTEXT`, `KDF_DERIVATION_FAILED`                                                                                                                              | decryption-entry shape does not match the on-wire key path; every slot rejected the key; slot-set MAC mismatch; content AEAD tag failure (or wrong passphrase); Argon2id rejected the parameters at runtime.               |
| profile / egress        | `OUT_OF_PROFILE_SKIPPED` (dual), `SERVICE_INDEPENDENCE_VIOLATION`                                                                                                                                                                                     | a verifier reading a v1-schema field outside its declared profile (info in render mode, error in strict end-to-end mode); an outbound call to a `denyHosts` entry.                                                         |

**Severity contract.** A `valid` verdict MUST NOT be reported when any `error`-severity code is present. A record MAY be valid with a non-empty `warnings` and/or `info` list. `INSUFFICIENT_CONFIRMATIONS` maps to `pending`, neither `valid` nor `failed`. Two codes (`MERKLE_UNSUPPORTED`, `OUT_OF_PROFILE_SKIPPED`) carry dual severity: their default reading is `info`, and a strict / merkle-only verifier promotes them to `error`. Neither layer is permitted to soften an `error` into a `warning` to make a record pass.

##### Profiles

Conformance profiles are a property of the verifier layer, not of the structural parser — the parser always validates the full v1 grammar uniformly. A verifier advertises which profile it implements:

- **core** — structural validation plus on-chain content-hash checks; no signature verification, no Merkle-fold, no decryption.
- **signed** — core plus record-signature verification.
- **sealed** — signed plus the structural surface of the encryption envelope.
- **recipient-sealed** — sealed plus sealed-PoE decryption with a held recipient KEM private key.

A verifier reading a v1-schema field outside its declared profile (for example, a core verifier encountering `enc` or `sigs`) emits `OUT_OF_PROFILE_SKIPPED` per affected field and still reports the hash claim; the record is NOT marked invalid solely because the verifier does not implement a profile extension. The registry of profiles and the per-profile algorithm sets are described in [Algorithm registries and conformance profiles](#algorithm-registries-and-conformance-profiles).

#### Service independence

The central property of CIP-309 is that **a proof verifies with no operator server in the loop**. A conformant verifier MUST work using only the operator-configured public Cardano / Arweave / IPFS gateway chains; it MUST NOT embed any operator's domain in its default configuration, and every operator domain MUST be deny-able via `denyHosts` without breaking verification of any conformant record. All record identity comes from the on-chain transaction hash; all signer identity comes from the in-signature `kid` or the inline `cose_key`. There is no proprietary off-chain index, no proprietary record id, and no authentication step.

This claim MUST be **structurally testable**, not a source-code grep heuristic. Two layers establish it:

- **Recording egress wrapper.** Every outbound network call MUST go through a single egress function that records `{url, method, status, bytes, durationMs, purpose}` to the report's audit trail for every call (success, failure, retry). That function MUST be the only path with network access in the verifier — direct use of lower-level HTTP primitives elsewhere is a structural violation. It enforces the closed scheme set (`purpose ∈ {cardano, arweave, ipfs}`; any other target → `URI_TARGET_FORBIDDEN`) and hard-fails any call to a `denyHosts` entry with `SERVICE_INDEPENDENCE_VIOLATION`. The `denyHosts` list is a deployment input — it scopes to network hazards (hosts that MUST NOT be contacted), not to any vendor; a conformance suite populates it with whatever domains the operator wishes to forbid.
- **Network-namespace assertion.** A test harness runs the verifier against a frozen fixture set in a network namespace where DNS resolution of an operator-supplied hostname set returns NXDOMAIN (or an unroutable address that fails to connect at the OS layer), while all other resolution is unrestricted. The verifier MUST complete every fixture with verdict `valid` despite the denial. The harness asserts at the OS-network layer, not the source layer — a verifier reaching a forbidden host through a hardcoded IP would pass a source grep but fail this test.

Trust-anchor analysis — how a deployment binds an on-record signer public key to a real-world identity — is out of scope for the verifier algorithm. The verifier resolves the on-record public key and reports the strict-Ed25519 result; whether that key represents the identity a consumer should attribute the record to is a deployment policy, addressed in [Security and Privacy Considerations](#security-and-privacy-considerations).

## Security and Privacy Considerations

This section states the security and privacy properties that follow directly
from the record schema and the sealed-PoE construction. Every claim here is a
property of the on-wire bytes: a verifier consuming only the transaction
metadata, optionally the content bytes, and a public blockchain explorer can
establish each one without any issuer server, certificate authority, or trusted
intermediary. How a 32-byte master seed is generated, stored, unlocked, or
rotated is OUT OF SCOPE (see [Seed and key derivation](#seed-and-key-derivation));
the properties below depend only on the format and the cryptographic
constructions this document defines.

### Adversary model

CIP-309's security claims hold against the following adversaries. Each row lists
what the adversary can and cannot achieve against the on-wire format alone.

| Adversary                                  | Capabilities                                                                                                                              | Cannot                                                                                                                                                                                                                                                                                                                                                                                                            | Can                                                                                                                                                                                                                                                                                                                                                      |
| ------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Network (passive or active MitM)**       | Observes and modifies traffic between any verifier and the Cardano / Arweave / IPFS gateways it consults.                                 | Decrypt sealed-PoE ciphertext, recover any master seed or recipient private key, or forge a `COSE_Sign1` signature. AEAD-only on-chain encryption (XChaCha20-Poly1305 content layer + ChaCha20-Poly1305 per-slot wrap) defeats payload eavesdropping; per-record ephemeral KEM material defeats traffic-analysis correlation.                                                                                     | Observe transaction identifiers, request timing, and fetch volume — metadata that the format does not attempt to hide.                                                                                                                                                                                                                                   |
| **Chain observer (permanent global read)** | Full read of every Cardano transaction, forever.                                                                                          | Decrypt the sealed-PoE ciphertext referenced by a content-addressed URI: the ciphertext lives off-chain, and even with both halves the observer lacks the recipient KEM private key and the per-record KEK derived via HKDF-SHA-256.                                                                                                                                                                              | See every record's on-chain metadata: content hashes, signer Ed25519 public keys, `COSE_Sign1` signatures, and slot count. An author signing with a stake-linked CIP-30 wallet key accepts that this binding is permanent and public (see [Privacy](#privacy)).                                                                                          |
| **Off-chain storage observer**             | Full read of every sealed-PoE ciphertext at its content-addressed `ar://` / `ipfs://` URI, forever.                                       | Decrypt the ciphertext — it is XChaCha20-Poly1305 over a CEK wrapped under a KEM-derived KEK, AAD-bound to `nonce ‖ slots_mac` (see [Sealed PoE: multi-recipient encryption](#sealed-poe-multi-recipient-encryption)). Enumerate recipients: recipient public keys never appear on the wire.                                                                                                                      | See the ciphertext bytes and their length.                                                                                                                                                                                                                                                                                                               |
| **Cardano gateway (malicious indexer)**    | Returns false data to a verifier: a synthetic transaction body, a forged confirmation count, a withheld reorg, or a mis-reported network. | Forge a record that passes signature verification — the verifier reproduces the canonical CBOR of the record body and verifies the `COSE_Sign1` against the embedded `kid`; the gateway does not hold the signer's Ed25519 private key. Induce a verifier to accept a record below the verifier's locally configured confirmation threshold (the threshold is verifier policy, not a normative wire requirement). | Delay verification with slow or incomplete responses (a denial-of-service shape, not a forgery shape). A verifier that consults more than one independent gateway and aborts on byte divergence escalates "single malicious gateway" to "collusion across providers".                                                                                    |
| **Malicious recipient**                    | Holds a recipient KEM private key; by construction decrypts every sealed PoE addressed to a slot wrapped under that key.                  | Decrypt sealed PoE addressed to a _different_ recipient's key — other slots in the same record are independently wrapped and fail closed under the wrong private key. Retroactively insert itself as a recipient on a published record — `enc.slots` is covered by `slots_mac` and, if the record is signed, by the `COSE_Sign1`; tampering invalidates one or the other.                                         | Do anything a legitimate recipient can do with the recovered plaintext, including leaking it. Sealed PoE has **no recipient forward secrecy by design**: once a record is sealed to a long-term recipient key, the holder of the matching private key can decrypt forever. This is a property of public-key encryption to a long-term key, not a defect. |

### Standalone verifiability and zero server custody

Two service-level invariants underwrite the format's trust model and are
testable against the on-wire bytes alone.

- **Standalone verifiability.** A verifier MUST be able to validate any CIP-309
  record using only public Cardano + Arweave + IPFS gateways and, for a
  recipient verifier, the recipient's own decryption material — without
  contacting any issuer-operated domain. A consumer holding the transaction
  reference and a Cardano gateway URL MUST be able to verify a proof even if the
  publisher's service no longer exists. Verification of the on-chain commitment
  is independent of decryption: a verifier MUST emit a structural verdict before
  any decryption is attempted.
- **Zero server custody.** No publishing service holds private cryptographic
  material that a verifier must trust. Because CIP-309 has no issuer field, any
  wallet MAY publish a conformant record; compromise of a publisher's signing
  key lets the attacker do only what any Cardano holder can already do — publish
  further conformant records — and is therefore not a privilege escalation
  against any user. A verifier that depends on a single centralised gateway and
  trusts everything it returns reduces this to an honest-versus-malicious gateway
  question; a verifier that consults two or more independent providers and
  aborts on byte divergence raises the bar to collusion across providers.

### Hash collision and second preimage

CIP-309 requires content-hash algorithms with at least 128-bit collision
resistance and at least 256-bit second-preimage resistance. `sha2-256` and
`blake2b-256` (registered in [`../registries/hash-algorithms.json`](https://github.com/cardanowall/cip309/blob/main/registries/hash-algorithms.json),
both 32-byte digests) qualify; the authoritative threat — a second preimage at
`2^256` classical / `2^128` Grover — is infeasible in both settings. A record
that opts into the multi-hash pattern (`sha2-256` _and_ `blake2b-256` in the
same `hashes` map) further requires a concurrent break of two independent design
families. If a registered algorithm is later weakened, a successor revision MUST
remove the identifier; verifiers SHOULD then mark dependent records "unreliable"
without erasing the underlying claim, because the chain is append-only.

### Merkle list commitment: second preimage and off-chain backup

The `rfc9162-sha256` list-commitment construction (see
[`../registries/merkle-commitment-algorithms.json`](https://github.com/cardanowall/cip309/blob/main/registries/merkle-commitment-algorithms.json))
inherits SHA-256's second-preimage strength: forging a different leaf list whose
canonical root equals a published root requires an SHA-256 second preimage,
which is infeasible. The RFC 9162 §2.1.1 prefix discipline — `0x00` for leaves,
`0x01` for internal nodes — prevents the duplicate-last-leaf malleability bugs of
the CVE-2012-2459 family, so an attacker cannot construct a tree of different
shape that yields the same root.

The **off-chain backup property** is a structural concern, not a cryptographic
one: loss of the producer's leaf list renders the on-chain Merkle commitment
unverifiable for any specific leaf. A 32-byte root by itself proves only that
_some_ leaf set with that root existed at the block time; it does not let any
party reconstruct or query the set. Producers using `rfc9162-sha256` MUST treat
the leaf list (and per-leaf positions, for selective disclosure) as a primary
archival artefact. The recommended pattern is to publish the leaf-list file at
the same content-addressed URI carried in the `merkle` entry's `uris`, so the
list is discoverable from the chain itself; the `merkle` and `items` arrays are
independent and the structural validator enforces no cross-array binding.

### Signature replay

A `COSE_Sign1` is bound to its signing input — the domain-prefixed canonical
CBOR of the record body with `sigs` removed (see
[Record-level signatures (COSE_Sign1)](#record-level-signatures-cose_sign1)).
Replay against a _different_ record is detectable: the signature does not verify
against the substituted signing input. There is no anti-replay across
_identical_ records — the same signed body MAY be submitted in two transactions.
In practice distinct PoE transactions carry distinct body bytes because they
reference different content; a producer concerned about identical-body cross-tx
replay SHOULD include a `supersedes` pointer, which by definition references a
unique prior transaction hash.

**Cross-protocol replay.** The 25-byte UTF-8 prefix `cardano-poe-record-sig-v1`,
prepended to the signing input, binds the signature to its CIP-309 role. A
future Cardano metadata schema that happens to share the body shape cannot reuse
a CIP-309 signature against itself: the replayer's signing input would carry a
different prefix (or none), the byte stream would differ, and verification would
fail. Implementations MUST embed this literal byte sequence as the leading bytes
of the signing input exactly. Omitting it — signing only the raw canonical CBOR —
leaves the door open to cross-protocol replay if a future schema reuses the body
shape, and is non-conformant.

### Plaintext-hash binding

`hashes` commits to the **plaintext**, even when an `enc` envelope is present. A
verifier holding only ciphertext cannot confirm the plaintext claim without
decrypting; this is intentional. AEAD tags fail closed on any bit-flip.
Whole-ciphertext substitution under a different CEK is detected after
decryption, when the recomputed plaintext digest fails to match. Integrity of
the ciphertext bytes _as published_ comes from the storage layer — an IPFS CIDv1
is a direct multihash of the content, and an Arweave transaction identifier
commits to the data via the signed transaction's `data_root` under consensus —
so a public verifier can confirm that the fetched bytes match the producer's
published bytes from the URI alone. There is no separate ciphertext hash and no
ciphertext-size field in the record.

### Partitioning-oracle defence

A multi-recipient sealed-PoE record carries an unauthenticated structure — the
`slots` array — that is parsed before any AEAD primitive is invoked. An adversary
who could submit malformed records and observe which slot's trial-decrypt fails
first could in principle learn which slot a given recipient occupies, partially
defeating the hidden-recipient property. Conformant verifiers and trial-decrypt
agents MUST therefore validate **all** structural length constraints **before**
invoking any AEAD primitive:

- `slots` array length ≥ 1;
- the KEM-discriminated per-slot encapsulation length — for `x25519`,
  `slot.epk` length `== 32`; for `mlkem768x25519`, the reassembled `slot.kem_ct`
  length `== 1120`;
- each `slot.wrap` length `== 48` (32-byte CEK + 16-byte ChaCha20-Poly1305 tag);
- `slots_mac` length `== 32`.

Length mismatches MUST emit the typed structural errors `ENC_SLOTS_EMPTY`,
`KEM_EPK_LENGTH_MISMATCH` / `KEM_CT_LENGTH_MISMATCH`, `WRAP_LENGTH_MISMATCH`, and
`ENC_SLOTS_MAC_INVALID_LENGTH` (see
[`../registries/error-codes.json`](https://github.com/cardanowall/cip309/blob/main/registries/error-codes.json)) — with no
length-dependent branch reaching the cryptographic primitives. There is no fixed
numeric slot cap; the upper bound is the per-record byte budget the producer
enforces before submission and ultimately the Cardano maximum transaction size.

### Constant-time trial decryption

A recipient verifier decrypts a sealed PoE by trial-decapsulating each slot with
its private key. To preserve the hidden-recipient property, recipient decryption
MUST be constant-time across all slots within each private key's pass: the time
to process a record MUST NOT reveal which slot — if any — that key unwraps. The
`slots` array is published in CSPRNG-shuffled order, so wire position carries no
"primary recipient first" information; combined with the constant-time pass, an
observer with timing access learns only the slot count, never the recipient
identity or position. Byte comparisons on `slots_mac` and on AEAD/MAC tags MUST
likewise be constant-time; a data-dependent comparison loop on any of these
surfaces is a timing oracle and is non-conformant.

### Anonymity of unsigned sealed PoE

When a sealed-PoE record carries **no `sigs`**, the on-wire bytes MUST be
independent of the sender's identity. Concretely:

- **No sender public key on the wire.** Each slot carries only per-record,
  per-slot ephemeral KEM material — the X25519 ephemeral public key in
  `slot.epk` for `x25519`, or the X-Wing ciphertext in `slot.kem_ct` for
  `mlkem768x25519` — freshly generated for each record and disclosing nothing
  about the sender. The sender's long-term X25519 and Ed25519 keys never appear.
- **CSPRNG-shuffled slots.** Slot ordering is not a side-channel for recipient
  metadata.
- **Hidden recipient keys.** Recipient public keys are not on the wire; an
  observer learns only `slots.length`, never _who_ the record was sealed to.
- **No descriptive fields.** No filename, MIME type, language tag, or size field
  is on the wire (see [Privacy](#privacy)); nothing constrains who plausibly
  authored the record.

**Forward anonymity across later signed records.** A producer who publishes a
sequence of unsigned sealed-PoE records and later publishes a signed record under
the same identity does **not** retroactively deanonymise the earlier records.
The signed record discloses the producer's identity Ed25519 public key, but that
byte sequence appears in no earlier unsigned record, and there is no cryptographic
operation that maps the per-slot ephemerals in the earlier records back to the
identity X25519 key — the two keys derive from the same seed via _different_
HKDF context strings (see [Seed and key derivation](#seed-and-key-derivation)),
and the Ed25519 public key cannot be used to derive or match the X25519 public
key.

**Fee-payer correlation is out of scope.** A Cardano transaction is paid for by
a wallet whose address is on chain. If the same wallet pays for both an unsigned
and a signed transaction, a chain observer can correlate them by fee-payer,
independent of CIP-309. The same applies to the producer's IP address as seen by
gateways and to any metadata in the off-chain ciphertext blob. CIP-309 cannot
defend against these channels because it lives inside the metadata, not in the
transaction inputs or the transport; producers requiring fee-payer-level
anonymity MUST address it at the transaction-construction layer (rotating
wallets, relays, mixers).

**Wallet signatures deliberately deanonymise.** A producer who opts into wallet
signing (a `sigs` entry of the `{ cose_sign1, cose_key }` shape, carrying the
CIP-30 wallet key) cryptographically binds the record to the wallet's Cardano
address — a publicly queryable identifier. This is a deliberate disclosure for a
public-attribution use case, not a defect. Producer-side interfaces SHOULD
default wallet signing to off and SHOULD warn the producer that opting in binds
the record to their wallet address before they do so.

### Supersedence semantics

Supersedence is advisory, not deletion. A verifier MUST treat the prior record
as existent and valid; the `supersedes` pointer affects only how records are
displayed, never the cryptographic verdict on the prior record. Anyone MAY
publish a record whose `supersedes` value points at a record they did not author,
so interfaces SHOULD surface supersedence only when the superseding record is
signed by a key also present in the superseded record. There is no on-chain
primitive that deletes or invalidates a prior record; doing so would violate the
durability property that makes proof-of-existence meaningful.

### Signer-key compromise

Because issuer identity is not part of the standard, a leaked signing key cannot
retroactively change, alter, or invalidate records signed before the compromise —
those signatures verify against the compromised public key exactly as before,
and this durability is load-bearing. The consequence is forward-looking: _new_
records signed by the leaked key are untrustworthy. A compromised signer SHOULD
rotate to a fresh key, republish the new public key through the same out-of-band
channels used originally, and MAY publish a new record whose `supersedes` points
at a record to be disavowed, signed under the new key. The pointer is a
caveat-emptor signal for downstream consumers, not an authoritative invalidation:
an adversary controlling the old key can also publish contradictory records, and
the chain cannot distinguish intent without external trust context. A verifier
MUST treat a signature as valid if, and only if, it verifies cryptographically;
"authorisation" is a social concept, not a cryptographic one. As a
defence-in-depth check against accidental key publication, a structural validator
rejects any `sigs` entry whose decoded `cose_key` carries the COSE_Key private
scalar `d` (label `-4`) with `SIG_PRIVATE_KEY_LEAKED` before the record reaches
the network.

### Pre-dating

CIP-309 establishes an **upper bound** on when content existed: the block time of
the transaction carrying the record is a cryptographic witness that the committed
content existed no later than that moment. It does **not** establish a lower
bound. A claim such as "I created this in 2020" carried inside a 2026 transaction
is, at most, evidence that the author had access to the content by 2026; nothing
in the record cryptographically attests to an earlier date. An author who wishes
to assert an earlier creation date SHOULD include that assertion inside the
content itself (for example in a PDF, signed document, or README) where it
becomes part of the hashed plaintext.

### Privacy

Every byte in a PoE record is on chain forever. CIP-309 deliberately omits
filenames, MIME types, titles, descriptions, language tags, free-form notes, and
size fields, because each can leak content context — a filename can reveal the
subject of an encrypted document, a MIME type can reveal the content class, and a
byte size can fingerprint a known file. Even a content hash can fingerprint a
known document. For sensitive claims, encrypt the content off-chain and publish
only its plaintext hash plus the sealed-PoE envelope. An application that needs
human-readable context SHOULD carry it inside the hashed content (for example as
an in-content manifest, see
[Rationale: how does this CIP achieve its goals?](#rationale-how-does-this-cip-achieve-its-goals)),
not as a label-309 field.

---

## Rationale: how does this CIP achieve its goals?

### Why CBOR rather than JSON

Cardano transaction metadata is natively CBOR; JSON inside a CBOR wrapper
double-encodes. CBOR carries raw binary as a first-class type — no base64
inflation for 32-byte digests and signatures — and has a deterministic encoding
([RFC 8949 §4.2.1](https://www.rfc-editor.org/rfc/rfc8949#section-4.2.1)) that
JSON lacks without an external profile. Metadata bytes are billed; the savings
matter.

### Why label 309

[CIP-10](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0010/registry.json)
already reserves label 309 for "Proof of Existence record"; this CIP formalises
that slot rather than claiming a new number. Alternatives considered and
rejected: claiming a fresh label (unnecessary, and disrespects an existing
reservation); nesting inside CIP-20's label 674 (would conflate plain-text
message metadata with PoE).

### Why a single content hash is sufficient

The `hashes` map requires at least one entry from the content-hash registry; a
single hash is fully conformant, and a structural validator emits no warning when
only one entry is present. The SHA-2 and BLAKE2 families have each been analysed
for decades without a practical second-preimage attack, so over the realistic
archival lifetime of a record a single sound 256-bit hash already covers the
threat model. The single-hash floor is the right trade-off:

- **Byte cost.** A second 32-byte digest plus its identifier adds roughly 38
  bytes per item entry on a metered ledger; the marginal cryptanalytic margin of
  a second family does not justify that per-record tax for every producer.
- **Defence-in-depth stays opt-in.** A producer who wants concurrent-family
  insurance pairs `sha2-256` with `blake2b-256` — independent design families
  breakable only by a simultaneous cryptanalytic collapse of both. The pair is
  permitted and recommended for users who accept the byte cost; it is not
  required.

### Why Merkle-mode is opt-in on both sides

The `rfc9162-sha256` list-commitment identifier is optional for producers and
verifiers alike because Merkle is a batching feature, not part of the interactive
single-file flow. A core-profile verifier need not implement the Merkle-fold
algorithm: it surfaces a `merkle` entry as `MERKLE_UNSUPPORTED` and verifies the
record's `items` content claims normally. Implementations that _do_ support
Merkle (typically automated batchers — CI/CD timestamping, IoT aggregation,
archival pipelines) gain two properties no plain content hash can provide: commit
millions of leaves to one 32-byte root and one transaction, and selectively
disclose individual leaves via `O(log n)` inclusion proofs without revealing
siblings. The cost is loaded entirely onto the producer's off-chain backup
discipline — the on-chain root is useless without the leaf list. The construction
is the [RFC 9162 §2.1.1](https://www.rfc-editor.org/rfc/rfc9162#section-2.1.1)
binary SHA-256 Merkle tree (a re-publication of
[RFC 6962 §2.1](https://www.rfc-editor.org/rfc/rfc6962#section-2.1) with identical
`0x00` leaf / `0x01` internal-node prefixes), chosen over a Bitcoin-style
duplicate-last-leaf rule to avoid the CVE-2012-2459 family of second-preimage
malleability bugs.

### Why ephemeral-static ECDH

Static-static ECDH between a known sender and recipient produces a deterministic
shared secret; CEK reuse would enable adaptive attacks, and all records to the
same recipient would be linkable by their shared key. Ephemeral-static ECDH with
**per-slot** ephemerals gives forward secrecy of the CEK against compromise of a
sender's long-term key, unlinkability across records, and per-slot independence —
a recipient who later leaks their slot wrap reveals only their own slot, not the
other recipients' slots in the same record.

### Why no issuer, network, or descriptive fields

- **No issuer field.** The PoE claim is about content, not about who submitted
  it. Any wallet can publish a conformant record. An issuer field would imply
  that some publishers are more authoritative than others, invite impersonation
  on key leaks, and conflict with pseudonymous use. Authorship is opt-in via
  record-level signatures: the signer's public key _is_ the cryptographic
  identity, voluntarily and content-bound.
- **No network field.** The Cardano network is determined by the transaction
  being verified, not by a self-declared metadata field. A mainnet transaction is
  a mainnet record. Repeating that fact inside label 309 would add bytes and a
  validation branch without strengthening the claim. Network selection belongs in
  verifier inputs and gateway configuration, not in the record.
- **No descriptive fields.** Filenames, media types, titles, descriptions,
  language tags, notes, and byte sizes are not needed to verify existence, and
  each leaks context. CIP-309 treats the content bytes as the only semantic
  payload. An application that needs human-readable context **MAY** carry it as an
  in-content manifest: assemble the files plus a manifest describing the bundle,
  archive them into one byte sequence, hash the whole sequence into `items`, and
  (when sealed) encrypt the bundle bytes. Any tampering with the manifest changes
  the bundle bytes and therefore the on-chain hash. The manifest format is
  entirely outside CIP-309's scope.

### Why URIs are content-addressed only

The fetch set `{ ar://, ipfs:// }` excludes `https://`, `http://`, `data:`,
`file://`, and every other host-trust scheme. A content-addressed URI binds the
URI bytes to the fetched content bytes through the storage layer's cryptographic
construction — an IPFS CID is a multihash of the content; an Arweave transaction
ID commits to the chunks via the signed-transaction `data_root` under consensus.
Detecting substituted bytes is therefore reducible to a public hash and
public-key cryptography, both of which a self-hosted verifier can implement
offline, and depends on no DNS, TLS, certificate authority, or specific gateway
operator. A host-trust URI would make the same assertion conditional on the DNS
owner, the TLS CA, the host, and the gateway all behaving — four trust
dependencies that defeat standalone verifiability. A verifier accepting
`https://` would either inherit all four or pair every such URI with an explicit
per-URI content digest, a wire-format addition this version declines to make. A
future record-schema version MAY add an opt-in `https://` + content-digest mode;
that is a schema-version change, not a patch.

### Why algorithm identifiers are strings, not integers

Inside the `COSE_Sign1` envelope this CIP follows COSE, which registers
algorithms by negative integer (EdDSA = `-8`). For PoE record fields — the
`hashes` map keys, `merkle` algorithm, `enc.aead`, `enc.kem`, and
`enc.passphrase.alg` — this CIP uses short ASCII strings instead: human-auditable
in explorers, self-documenting in code, and not gated on IANA code-point
allocation when a new hash or AEAD is registered. The cost — a handful of bytes
per identifier — is small relative to the 32-byte digests they describe.

### Why `hashes` commits to plaintext, not ciphertext

A PoE's purpose is to let an author later reveal plaintext and prove it existed
at a given time. Hashing the ciphertext would prove only that a particular
encrypted blob existed, not that the underlying plaintext existed. For sealed
PoE, the storage layer binds the URI to the referenced ciphertext bytes, so a
public verifier confirms "the ciphertext fetched is the ciphertext the producer
published" from the URI alone; the AEAD tag binds ciphertext to the CEK at
decrypt time; and after decryption a recipient verifier recomputes the plaintext
`hashes`. No separate ciphertext hash or ciphertext size is part of the record.

### Why `items` is optional

A record's substantive claim is its cryptographic commitment to content. The
format supports two parallel ways to express that commitment — per-leaf content
hashes (`items[i].hashes`) and Merkle list-commitment roots (`merkle[i].root`) —
and either suffices on its own. A record MAY therefore consist of a single Merkle
root over an off-chain leaf list with no `items` array at all, an
industry-validated pattern for high-volume batched PoE. The "at least one of
`items` or `merkle` is non-empty" invariant ensures a record always commits to
something while permitting either array to be absent. Requiring a paired `items`
entry for every Merkle record would force a redundant content-hash of the
leaf-list file, adding bytes without changing what the record commits to. The two
arrays are orthogonal: the structural validator enforces no cross-array binding,
and a producer who wants to commit to the leaf-list file's bytes simply adds a
separate `items` entry, treated no differently from any other content claim.

### Why there is no revocation primitive

The chain is append-only. A `revoked: true` field could not erase the prior
transaction; it could only add another statement. `supersedes` provides a minimal
pointer from a later record to an earlier one without pretending to invalidate
the earlier record.

### Why domain separation is embedded in the signing input

A natural choice for cross-protocol replay protection in a `COSE_Sign1` setting
is to place the domain separator in the `external_aad` field of the
`Sig_structure`. CIP-309 does **not** do this, for CIP-30 compatibility: the
[CIP-30](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0030/README.md)
`signData` interface — the standard wallet-signing path on Cardano — stipulates
that the payload is not hashed and no `external_aad` is used. A dApp has no way
to pass an `external_aad` to a CIP-30 wallet, so requiring a non-empty value
would make every wallet-produced signature fail CIP-309 verification. Embedding
the separator as a fixed UTF-8 prefix at the start of the signed input preserves
the anti-replay property with cryptographic strength equivalent to the
`external_aad` placement; the difference is purely wire-side, and it is the
difference that makes wallet signing feasible. A successor revision MAY revisit
this if a future wallet-signing standard lets the dApp supply `external_aad`.

### Why authorship is expressed only at the record level

CIP-309 places signatures at the record level, not at the per-item level. A
per-item `sig` field — enabling co-authors of a multi-item record to sign their
own contributions — is rejected on three grounds: a wallet-signed multi-item PoE
under that model would require one wallet prompt per signed item, pure friction
for the dominant single-author case; genuine multi-author records have a cleaner
shape as N independent records, each with one author's record-level signature,
linked via `supersedes` if desired; and a single record-level signature slot
keeps the wire surface minimal, with no second signing-structure flavour and no
second domain-separator namespace. The signature list stays plural at the record
level — multiple signers MAY independently endorse the _same_ whole record body,
each producing an independent `COSE_Sign1` — and each entry is a self-contained
map carrying its own optional wallet-key field rather than a parallel array
indexed in lockstep, which eliminates a cross-field length invariant and the
placeholder semantics that real implementations get wrong.

---

## Path to Active

Per [CIP-0001 §3.3](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0001/README.md#document-lifecycle),
this CIP proposes the following Acceptance Criteria and Implementation Plan.

### Acceptance Criteria

1. **Reference implementations exist and pass conformance.** At least one
   open-source reference implementation of both a producer (record writer) and a
   verifier (chain reader + structural validator + public verifier). Reference
   implementations in [TypeScript](https://github.com/cardanowall/cip309-ts),
   [Python](https://github.com/cardanowall/cip309-py), and
   [Rust](https://github.com/cardanowall/cip309-rs) are published as open-source
   sibling repositories, with worked examples under
   [`../examples/`](https://github.com/cardanowall/cip309/blob/main/examples); all consume the byte-pinned vectors in
   [`../conformance/`](https://github.com/cardanowall/cip309/blob/main/conformance).
2. **Conformance suite.** A public conformance suite exists — valid and invalid
   fixtures, with every error code in
   [`../registries/error-codes.json`](https://github.com/cardanowall/cip309/blob/main/registries/error-codes.json) covered by
   at least one fixture — and serves as the cross-implementation interop gate. At
   least one third-party language port demonstrates byte-identical canonical-CBOR
   output against the suite. The valid-fixture set MUST include at least one
   **mixed-signature** record that combines an in-signature-`kid` entry
   (`{ cose_sign1 }` only) and a CIP-30 wallet entry (`{ cose_sign1, cose_key }`)
   in a single record's signature list, in both orderings; this fixture exercises
   per-entry shape independence and the signing-path discrimination where
   independent implementations most commonly diverge.
3. **Software-wallet signing demonstrated** (REQUIRED for Active, not for
   Proposed). At least **two** mainstream software wallets produce a CIP-30
   `signData` signature against the embedded-prefix signing input that the
   reference public verifier accepts under default strict configuration — strict
   non-cofactored Ed25519
   ([RFC 8032 §5.1.7](https://www.rfc-editor.org/rfc/rfc8032#section-5.1.7)), the
   wallet-binding check, and the closed `{ ar://, ipfs:// }` URI scheme set. Two
   independently developed wallets agreeing on the byte format make wallet-side
   regression unlikely. Hardware-wallet support remains explicitly best-effort:
   CIP-30 `signData` is unevenly implemented across hardware firmware and is
   outside CIP-309's scope to enforce. The identity-key signing path (raw Ed25519
   public key in the in-signature `kid`) is the primary signing path and is
   independently testable without any wallet; this criterion covers the wallet
   path on top of it, not in place of it.
4. **Public mainnet records.** At least three independently authored CIP-309
   records on Cardano mainnet, covering the `core` profile (hash-only), the
   `signed` profile, and the `sealed` profile.
5. **Standalone public verifier published.** A standalone verifier that contacts
   only operator-configured Cardano / Arweave / IPFS gateways and is self-hostable
   has a public release and a documented use page.
6. **External cryptographic review.** A short external cryptographic review of the
   sealed-PoE construction has been completed; the findings (or an explicit "no
   findings" statement) are published as part of the submission package.
7. **Public review.** A pull request against `cardano-foundation/CIPs` opens a
   public discussion; the CIP moves from Proposed to Active when the criteria
   above are met and the CIP editors approve.

### Implementation Plan

Reaching Proposed and then Active status requires a coordinated rollout. The
load-bearing artefacts are:

1. **Conformance fixture set.** Publish the machine-readable fixtures under
   [`../conformance/`](https://github.com/cardanowall/cip309/blob/main/conformance) and a runner that maps every error code in
   [`../registries/error-codes.json`](https://github.com/cardanowall/cip309/blob/main/registries/error-codes.json) to at least
   one negative fixture. The suite is the explicit cross-implementation interop
   gate.
2. **Reference SDKs.** Publish a [TypeScript SDK](https://github.com/cardanowall/cip309-ts),
   a [Python SDK](https://github.com/cardanowall/cip309-py), and a
   [Rust SDK](https://github.com/cardanowall/cip309-rs) as open-source packages
   under permissive licenses. All MUST pass the conformance suite, MUST work
   without any implementer-specific account or service, and MUST produce
   byte-identical canonical CBOR for the same logical inputs. Worked examples for
   the reference implementations live under [`../examples/`](https://github.com/cardanowall/cip309/blob/main/examples).
3. **Standalone public verifier and CLI.** Ship a
   [verifier-only CLI](https://github.com/cardanowall/cip309-cli) and a static
   web verifier. Both load from [`../conformance/`](https://github.com/cardanowall/cip309/blob/main/conformance) for unit tests
   and from a small set of mainnet PoE records for end-to-end tests. The verifier
   MUST run against operator-configured Cardano / Arweave / IPFS gateways without
   requiring any vendor-specific endpoint (Acceptance Criterion 5).
4. **Implementor recruitment.** Publicise the CIP on the `cardano-foundation/CIPs`
   discussion thread and through Cardano-developer channels; third-party SDK ports
   are explicitly invited, with the conformance suite as the interop gate
   (Acceptance Criterion 2).
5. **Wallet outreach.** Coordinate with wallet teams to demonstrate CIP-30
   `signData` interop with the reference implementation (Acceptance Criterion 3)
   and to surface CIP-309 records as a first-class metadata view.
6. **Explorer outreach.** Engage major Cardano block-explorer teams to render
   label-309 records as "Proof of Existence" with the canonical hash digests and
   reassembled URIs; without explorer awareness, end-users see raw chunked CBOR.
   This is a coordination task, not a CIP-text task.
7. **External cryptographic review.** Commission a short external review of the
   sealed-PoE construction, primarily covering the multi-recipient wrap (per-slot
   KEK derivation, zero-nonce safety), the slot-set MAC, and the AAD binding to
   `nonce ‖ slots_mac` (Acceptance Criterion 6).
8. **Maintenance.** Editorial corrections that do not change wire bytes are
   non-breaking and may land by PR against the merged CIP. Adding a new algorithm
   identifier to a registry is additive and bumps no version — v1 verifiers reject
   unknown identifiers as the corresponding `UNSUPPORTED_*` error. A change that
   re-interprets existing on-wire bytes requires either an `enc.scheme` bump (for
   a cross-KEM sealed-PoE construction change) or a top-level `v` bump (for a
   record-schema change).

CIP-309 reaches Proposed when Acceptance Criteria 1, 2, 5, and 6 are
demonstrated; Criteria 3 (two-wallet signing), 4 (public mainnet records), and 7
(public review) gate Active.

---

## Copyright

This CIP is licensed under [CC-BY-4.0](https://github.com/cardanowall/cip309/blob/main/LICENSE-docs).
