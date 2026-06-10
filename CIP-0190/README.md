---
CIP: 190
Title: Proof of Existence Transaction Metadata
Category: Metadata
Status: Proposed
Authors:
  - Igor Shubovsky <igor@cardanowall.com>
Implementors:
  - CardanoWall <https://github.com/cardanowall>
Discussions:
  - https://github.com/cardano-foundation/CIPs/pull/1205
Created: 2026-06-02
License: CC-BY-4.0
---

## Abstract

This CIP specifies the schema, algorithm registries, canonical encoding rules, and verification procedure for a **Proof of Existence (PoE)** record embedded in Cardano transaction metadata under metadata label **309** ("Proof of Existence record", reserved in [CIP-10](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0010/registry.json)). A PoE record commits one or more cryptographic content hashes to the chain; the block time of the transaction carrying the record is the authoritative witness that the content existed no later than that moment. Because the claim is content-addressed by a cryptographic digest, it is independent of where the content is hosted and of who published it.

A conformant verifier needs only the transaction metadata, optionally the content bytes, and a public blockchain explorer — **no issuer-controlled intermediary is required at any step**; the chain and storage gateways it consults are untrusted data sources, verified cryptographically where possible and cross-checked for inclusion and finality. Alongside the hash claim, the schema carries optional content-addressed discovery URIs (`ar://`, `ipfs://`), an OPTIONAL multi-recipient encryption envelope for off-chain ciphertext, OPTIONAL record-level [CIP-8](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0008/README.md) `COSE_Sign1` signatures, and supersedence pointers to prior records. Signatures attach at the record level only, are never required, and never name a publisher to trust. The record deliberately carries no filename, MIME type, title, description, free-form note, plaintext/ciphertext size field, issuer-identity field, certificate chain, or revocation primitive.

> Metadata **label 309** is reserved for "Proof of Existence record" in the
> [CIP-10 registry](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0010/registry.json)
> and is the load-bearing on-chain identifier for this specification.
> Implementations cite this specification by its on-chain metadata label (309);
> the assigned CIP number (CIP-0190) carries no wire-format consequence.

## Motivation: Why is this CIP necessary?

A Proof of Existence is one of the simplest and most universally useful primitives an append-only public ledger can offer: "this content existed on or before this block." It underpins notarisation, intellectual-property timestamping, supply-chain attestation, journalism, and — with optional signatures — authorship attribution. Because the claim is content-addressed via a cryptographic hash, it is independent of where the content is hosted.

### Why Cardano native transaction metadata

A PoE is a structured cryptographic record — content hashes, optional encryption envelopes, optional signatures, optional URIs, optional supersedence pointers — not a single opaque blob. The substrate it anchors on materially affects how that structure is expressed and what it costs.

Cardano is unusually well-suited to a structured PoE record because its transaction metadata is a first-class, CBOR-structured, schema-agnostic field indexed by an integer label registered under [CIP-10](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0010/registry.json). Any transaction MAY carry any well-formed CBOR map under any label without invoking a script, without ABI-encoding, and without per-byte gas above the baseline transaction fee. CBOR natively supports raw byte strings, definite-length arrays, and integer-keyed maps — exactly the primitives a cryptographic record needs, with no base64 inflation for 32-byte digests and no JSON ambiguity at canonicalisation time.

By contrast:

- **Bitcoin** has no dedicated metadata field. `OP_RETURN` was introduced to mark a script output as unspendable, not as a metadata channel; community usage repurposed it. It carries an unstructured byte sequence with no schema layer and no label namespace — sufficient for a single Merkle root, insufficient for a record that bundles multiple hashes, a signature envelope, and recipient slots in one structured, independently addressable metadata value.
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
5. **Algorithm-agile.** Every cryptographic algorithm is referenced by a named identifier drawn from the extensible registries this CIP defines. Post-quantum protection of the sealed-PoE key path ships in v1 (the `mlkem768x25519` X-Wing hybrid KEM is registered alongside classical `x25519`); further post-quantum migration adds new identifiers, and existing verifiers degrade predictably rather than break — an envelope under an identifier a verifier does not implement becomes opaque to it while the record's content-hash claim still validates (see [Structural validation, verifier roles, and error codes](#structural-validation-verifier-roles-and-error-codes)).

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
- **Content hash** — a cryptographic digest of the content under a named hash algorithm from the hash registry [`../registries/hash-algorithms.json`](https://github.com/cardanowall/label-309/blob/main/registries/hash-algorithms.json); the primary claim of a PoE record.
- **Block time** — the time of the block containing the PoE transaction; the authoritative timestamp of the record. A PoE record carries no submitter-asserted timestamp.
- **Sealed PoE** — a PoE record whose content is encrypted off-chain, with the content-encryption key wrapped to one or more recipient public keys (or derived from a passphrase) through the on-chain `enc` envelope (see [Sealed PoE: multi-recipient encryption](#sealed-poe-multi-recipient-encryption)). The ciphertext lives off-chain, published at a content-addressed `ar://` or `ipfs://` URI or delivered out of band.
- **Slot** — one recipient entry inside a sealed-PoE envelope, holding the key-encapsulation material and the wrapped content-encryption key for a single recipient public key (see [Sealed PoE: multi-recipient encryption](#sealed-poe-multi-recipient-encryption)).
- **Verifier** — software that checks a PoE record against this specification. Three roles are distinguished and defined in [Structural validation, verifier roles, and error codes](#structural-validation-verifier-roles-and-error-codes): a **structural validator** (a pure function over the record-body CBOR; no I/O, no signature cryptography, no decryption), a **public verifier** (fetches on-chain metadata, runs structural validation, and verifies record signatures; does not decrypt), and a **recipient verifier** (a public verifier that additionally holds decryption credentials — recipient KEM private keys and/or passphrases — and performs sealed-PoE decryption plus plaintext-hash recomputation). Used without a qualifier, "verifier" denotes whichever role is relevant in context; prose that requires a specific role names it explicitly.

## Specification

The machine-readable grammar for the record body is the CDDL schema in
[`../cddl/label-309.cddl`](label-309.cddl); per-component JSON Schemas in
[`../schemas/`](https://github.com/cardanowall/label-309/blob/main/schemas) mirror it for tooling. Algorithm identifiers are
drawn from the registries in [`../registries/`](https://github.com/cardanowall/label-309/blob/main/registries). Conformance
vectors are pinned under [`../conformance/`](https://github.com/cardanowall/label-309/blob/main/conformance). Each artefact is
authoritative for its own layer: the CDDL is authoritative for the **permissive
structural grammar** — the superset of well-formed shapes it deliberately
over-admits (see [CDDL grammar and JSON Schemas](#cddl-grammar-and-json-schemas));
this prose together with the registries defines the typed invariants and the
accepted identifier sets, enforced in the typed validation pass; and the
conformance vectors are authoritative in any byte-level dispute.

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
protocol parameter `maxTxSize` (16 384 bytes at protocol major version 10 on
mainnet, subject to ledger parameter updates). `maxTxSize` caps the **whole
transaction** — inputs, outputs, witnesses, and fee structure as well as the
auxiliary data — so a record's practical ceiling is `maxTxSize` minus the rest
of the carrying transaction: somewhat below 16 KiB in practice. This ledger
bound is the **only** size cap this CIP imposes — the schema itself has no hard
byte ceiling beyond what the ledger enforces at submission time. Records that
exceed it are rejected by Cardano nodes before any verifier sees them; a
structural validator **MAY** emit an advisory warning for records approaching
the limit, but **MUST NOT** impose a size cap below `maxTxSize`.

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
**MUST NOT** report `valid: true`. The set of critical extensions a validator
implements is its `supportedCriticalExtensions` option (see
[Structural validation, verifier roles, and error codes](#structural-validation-verifier-roles-and-error-codes));
its default is the **empty set**, so a default-configured validator fails every
`crit`-bearing record — by design, since claiming to validate a record whose
producer demanded an unimplemented extension would be a false verdict.

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
the base spec register their namespace prefix in the companion-CIP registry
([`../registries/companion-cips.json`](https://github.com/cardanowall/label-309/blob/main/registries/companion-cips.json),
initial content: empty) and do **not** bump the top-level `v` — additive fields
under a registered namespace are not a v1-breaking change.

**Extension-key admissibility.** An extension key is admissible when its full
text matches `^x-.+` or `^[a-z]+-.+` **and** contains no control characters
(U+0000–U+001F, U+007F–U+009F); a key whose suffix consists of or contains
control characters **MUST** be rejected as `SCHEMA_UNKNOWN_FIELD` (and a `crit`
entry naming such a key as `CRIT_SHAPE_INVALID`), regardless of whether a
permissive regex engine would match it. The single-letter prefix `x` is
**reserved** for the vendor / experimental namespace: a companion CIP **MUST
NOT** register `x` as its namespace prefix, so an `x-…` key is never ambiguous
between the two namespaces. Companion-CIP namespace registration is
**advisory** — the registry exists so extension authors can avoid prefix
collisions, and it carries no wire enforcement: a validator does **not** check
that a prefix is registered, and a record carrying an unregistered
companion-style key remains structurally valid (the key is surfaced
informationally like any other extension key).

**Extension surface is top-level only.** Every map below the top level is
closed by design: `items[i]`, `merkle[i]`, `sigs[i]`, `enc`, `enc.passphrase`,
`enc.passphrase.params`, and each slot admit no extension keys — an
unrecognised key inside any of them is `SCHEMA_UNKNOWN_FIELD`, except inside a
slot, where a stray key makes the slot's shape mismatch the declared `enc.kem`
and the more specific `ENC_SLOT_INVALID_SHAPE` fires instead. A top-level
extension that refers to a specific item **SHOULD** key its reference by that
item's content hash (one of its `hashes` digests), not by positional index:
array positions renumber when a record is regenerated, while the content hash
names the claim itself.

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
  "uris":   [ <tstr>, ... ],        ; OPTIONAL — list of discovery URIs, one text string each
  "enc":    <encryption-envelope>   ; OPTIONAL — sealed-PoE envelope. When present, the
                                    ;   item MUST also carry at least one content-hash entry in `hashes`.
}
```

v1 has **no per-item signature slot**. Authorship is expressed exclusively
through optional record-level signatures (see
[Record-level signatures (COSE_Sign1)](#record-level-signatures-cose_sign1)),
which cover every item entry in the record.

`hashes` is a non-empty **CBOR map** whose keys are hash-algorithm identifiers
(CBOR text strings from [`../registries/hash-algorithms.json`](https://github.com/cardanowall/label-309/blob/main/registries/hash-algorithms.json))
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
CBOR map invariant in [`../cddl/label-309.cddl`](label-309.cddl)). A
single-entry record is fully conformant; producers **MAY** add a second entry
from a distinct hash family (e.g. `sha2-256` paired with `blake2b-256`) as
optional defense-in-depth against future cryptanalytic progress against one
family, but this is not required and structural validators **MUST NOT** emit a
warning for single-entry records (see [Hash algorithms](#hash-algorithms)).

If `uris` is present it **MUST** be a non-empty array of CBOR text strings,
each carrying exactly one URI. There is no per-URI length cap and no per-field
wrapping shape: the record body travels under label 309 as the whole-body
chunk array defined in
[Canonical CBOR and metadata label 309 carriage](#canonical-cbor-and-metadata-label-309-carriage),
and that transport layer — not the individual field — satisfies the Cardano
ledger's 64-byte string cap, so a long `ipfs://<CIDv1>/<path>` URI is a single
text string like any other. A single-URI item uses the array form
`[ "ar://example-txid" ]`.

URIs **MUST** be absolute per
[RFC 3986 §4.3](https://www.rfc-editor.org/rfc/rfc3986#section-4.3) — they
**MUST** include a scheme and a hierarchical part, and **MUST NOT** contain a
fragment identifier (the `#` character is forbidden because PoE is a claim about
content bytes, not about a sub-component of a document). The v1 URI scheme
registry is:

| Scheme    | Self-authenticating | Notes                                                                                                                                                                                                                                                                    |
| --------- | ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `ar://`   | Yes                 | Arweave transaction id (43-char base64url). Form: `ar://<txid>`.                                                                                                                                                                            |
| `ipfs://` | Yes (via CID)       | IPFS CIDv1 preferred. Form: `ipfs://<cid>` or `ipfs://<cid>/<path>` (the path navigates within the CID's DAG per standard IPFS URI semantics; the CID commits the entire DAG). |

The v1 fetch set is exactly `{ar://, ipfs://}` — content-addressed schemes only.
Producers **MUST NOT** emit URIs with any other scheme (`https://`, `http://`,
`file://`, `ftp://`, `data:`, etc.). PoE uses content-addressed storage
exclusively: each URI is bound to the referenced bytes by the storage layer's
integrity model — IPFS CIDs are direct multihashes of the content; Arweave
transaction IDs commit to the data via the signed transaction's `data_root` (a
Merkle root over the chunks) under Arweave consensus. Verification therefore does
not depend on host trustworthiness or availability beyond the storage layer. A
conformant structural validator **MUST** reject any URI whose
scheme is not in `{ar://, ipfs://}` with `INVALID_URI`; this fails records before
any verifier-side network step. The closed set is a deliberate design choice, not
a temporary restriction — see
[Rationale: How does this CIP achieve its goals?](#rationale-how-does-this-cip-achieve-its-goals)
for the adoption trade-off.

An item entry **MAY** list multiple URIs (one array entry per URI). This is
a **producer obligation**: at publication time, every listed URI **MUST** resolve
to plaintext bytes that satisfy the record's hash assertions (for unencrypted
entries) or to ciphertext bytes that decrypt to plaintext bytes satisfying those
assertions (for encrypted entries). Multiple URIs are alternative sources for
the **same** bytes, never variants: a verifier treats the list as
first-success-for-availability — once one URI yields bytes that satisfy the
commitment, the remaining URIs MAY be skipped — and fetched bytes that fail the
commitment are a hard integrity error regardless of what the other URIs hold
**when they are attributable to the URI** (verified against its content
address); mismatching bytes that cannot be attributed indict the serving
gateway, never the record (see
[Content-address binding of fetched bytes](#content-address-binding-of-fetched-bytes)). For a sealed
item the obligation is structural rather than behavioural: one record has one
`enc.nonce` and one `payload_key`, so a single ciphertext exists and every
listed URI necessarily resolves to byte-identical ciphertext — a producer
cannot list divergent ciphertexts under one envelope.

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
all 256-bit hashes in [`../registries/hash-algorithms.json`](https://github.com/cardanowall/label-309/blob/main/registries/hash-algorithms.json),
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
| `alg`        | tstr                | REQUIRED | Registered list-commitment algorithm identifier (see [`../registries/merkle-commitment-algorithms.json`](https://github.com/cardanowall/label-309/blob/main/registries/merkle-commitment-algorithms.json)) |
| `root`       | bytes .size 32      | REQUIRED | Canonical root over the producer's ordered leaf list                                                                                                       |
| `leaf_count` | uint                | REQUIRED | Number of leaves committed by `root`, in `1 .. 2^32 − 1` (binds the on-chain commitment to the off-chain leaves-list size)                                 |
| `uris`       | [+ tstr]            | OPTIONAL | Content-addressed URI(s) at which the off-chain leaves-list file is fetchable                                                                              |

The v1 merkle-commitment registry holds one identifier:

| Identifier       | Root length | Construction                                                                                                                                                                                                                                                                                                                                                                                           |
| ---------------- | ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `rfc9162-sha256` | 32 bytes    | Binary Merkle tree per [RFC 9162 §2.1.1](https://www.rfc-editor.org/rfc/rfc9162#section-2.1.1), using SHA-256. A `0x00` byte prefixes each leaf input (`leaf = SHA-256(0x00 ‖ d)`) and a `0x01` byte prefixes each internal-node input (`internal = SHA-256(0x01 ‖ L ‖ R)`), which prevents second-preimage attacks that swap a leaf for an internal node. The root is the SHA-256 output of the tree. |

`root` **MUST** be 32 bytes; any other length is rejected as
`HASH_DIGEST_LENGTH_MISMATCH`. An unregistered `alg` is rejected as
`UNSUPPORTED_MERKLE_COMMIT_ALG`. `leaf_count` **MUST** be a uint in
`1 .. 2^32 − 1`: a `leaf_count` of `0`, or one above `2^32 − 1`, is rejected as
`SCHEMA_MERKLE_LEAF_COUNT_INVALID` — a structural check that needs no off-chain
bytes, distinct from the leaves-list comparison code
`SCHEMA_MERKLE_LEAF_COUNT_MISMATCH` below.

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
the leaves-list document (the normative CBOR container defined below) at the
content-addressed URI listed in `merkle[i].uris`; a verifier resolves the URI,
parses the document, recomputes the canonical root, and matches it against
`merkle[i].root` byte-for-byte. A `merkle[i]` entry that omits `uris` denotes a
producer-only commitment with no public leaf list: the leaves-list bytes remain
in producer custody and verification is possible only when the producer (or a
recipient the producer entrusts) supplies the bytes out-of-band. Loss of the
leaf list renders the on-chain commitment unverifiable for any specific leaf.

##### The leaves-list document

The off-chain leaves-list artefact is a single canonical-CBOR map — encoded
under the same RFC 8949 §4.2.1 deterministic-encoding profile as the record
body — with the following grammar. This CBOR container is the **only** normative
leaves-list form; there is no JSON projection or alternative serialisation, so
two implementations exchanging a leaves-list always exchange byte-comparable
documents.

```cddl
leaves-list = {
  "format":     "cardano-poe-merkle-leaves-v1",
  "tree_alg":   tstr,                ; registered list-commitment algorithm id
  "root":       bytes .size 32,
  "leaves":     [ + bytes .size 32 ],
  "leaf_count": 1..4294967295,       ; 1 .. 2^32-1; MUST equal the length of `leaves`
  ? "leaf_alg": tstr,
}
```

- `format` — REQUIRED. The document-format identifier, exactly
  `cardano-poe-merkle-leaves-v1`. A document whose `format` is a text string
  outside the registered set is rejected as
  `SCHEMA_MERKLE_LEAVES_FORMAT_UNSUPPORTED` — the bytes are recognisably a
  leaves-list container of a format this verifier does not implement. Bytes that
  are **not** this container at all — not a CBOR map, a missing or
  wrongly-typed key, a wrong-length `root` or leaf — are rejected as
  `SCHEMA_MERKLE_LEAVES_MALFORMED`. The two codes are disjoint by construction:
  `…_FORMAT_UNSUPPORTED` requires a well-typed `format` key carrying an
  unrecognised value; everything else unparseable is `…_MALFORMED`. One
  carve-out: fetched bytes that are not CBOR at all may be a `tlog-checkpoint`
  file (the text-format scale-out form for high-volume trees — see the
  scale-out note below); a verifier that does not implement `tlog-tiles`
  dispositions those as `MERKLE_UNSUPPORTED` per that note, reserving
  `…_MALFORMED` for CBOR bytes that fail this grammar.
- `tree_alg` — REQUIRED. The registered list-commitment algorithm identifier
  under which `root` was computed. It **MUST** equal the `alg` of the on-chain
  `merkle[i]` entry the document is being verified against; a disagreement is
  `SCHEMA_MERKLE_LEAVES_MALFORMED` (the document does not describe this
  commitment).
- `root` — REQUIRED. The 32-byte root over `leaves`, included so the document
  is self-checking offline. A verifier recomputes the root from `leaves` and
  **MUST** reject the document on any mismatch with this field, and **MUST**
  reject the record with `MERKLE_ROOT_MISMATCH` when the recomputed root does
  not byte-equal the on-chain `merkle[i].root`.
- `leaves` — REQUIRED. The producer's ordered leaf list, each entry exactly
  32 bytes, in tree order.
- `leaf_count` — REQUIRED. A uint in `1 .. 2^32 − 1` that **MUST** equal the
  length of `leaves`, and **MUST** equal the on-chain `merkle[i].leaf_count`;
  either disagreement is `SCHEMA_MERKLE_LEAF_COUNT_MISMATCH`.
- `leaf_alg` — OPTIONAL. An informative annotation naming how the leaves were
  produced (for example `sha2-256` when each leaf is the SHA-256 of a file's
  content). It carries **no** verification semantics — the tree construction is
  agnostic to leaf provenance — and a verifier **MUST NOT** reject a document
  for any `leaf_alg` value.

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
primitives; the leaves-list document above is the normative off-chain format.
Reference implementations and the pinned 4-leaf-tree vector (root plus
per-leaf inclusion proofs) live under [`../conformance/`](https://github.com/cardanowall/label-309/blob/main/conformance).

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
by a policy the UI defines). Supersedence display therefore applies in practice
only to **signed pairs**: a producer who intends a supersedence link to be
honoured **SHOULD** sign both the original record and its successor with the
same key — an unsigned record on either end of the link gives consumers no
basis to attribute the pointer, and conformant UIs will not display it.

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

The cost of the split is one Cardano transaction fee per record; the wire
format imposes no penalty. The convention is a recommendation, not a
requirement: a record bundling multiple unrelated claims under one signature is
on-wire valid, but the producer's trade-off against future supersedence
granularity should be deliberate.

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

Signers and verifiers **MUST** agree on this canonicalisation bit-for-bit; implementations **SHOULD** use a CBOR library that supports RFC 8949 deterministic encoding natively. The complete grammar for the canonical record body is the CDDL at [`../cddl/label-309.cddl`](label-309.cddl); conformance vectors that pin exact canonical bytes are at [`../conformance/`](https://github.com/cardanowall/label-309/blob/main/conformance).

##### `canonicalEncode`: deterministic encoding of protocol context objects

The sealed-PoE construction binds several **context objects** — the slots transcript, the passphrase transcript, and the item's `hashes` map digested into `hashes_hash` (see [Sealed PoE: multi-recipient encryption](#sealed-poe-multi-recipient-encryption)) — into the cryptographic computation by serialising them to a single canonical byte string. That serialisation is the named function `canonicalEncode(obj)`, and producer/verifier byte-identity over it is a **MUST**: a single bit of disagreement silently yields a `slots_mac` or a passphrase commitment that another implementation cannot reproduce, with no typed error to localise the fault. Every context object **MUST** be serialised through `canonicalEncode`, and every conformant implementation **MUST** produce byte-identical output for the same logical object.

`canonicalEncode(obj)` is the record-body canonical-CBOR profile above, narrowed to the small closed-map shapes these context objects use:

1. **RFC 8949 §4.2.1 Core Deterministic Encoding.** Shortest-form integers and lengths; definite-length items only (no indefinite-length); map keys sorted in bytewise-lexicographic order of their deterministic encodings; no duplicate map keys.
2. **Closed-map schema.** The two transcript objects are **closed maps** carrying exactly the keys specified for each — no others. An encoder **MUST NOT** emit an unspecified key and a decoder reconstructing a transcript **MUST** reject one. The item's `hashes` map is encoded exactly as it appears in the record body: registry-identifier keys mapping to 32-byte digests.
3. **Pinned value types.** Text-string values are exact ASCII as written in this document; byte-string values are definite-length byte strings of the pinned length. Integer values are encoded tag-free in shortest form.

Map keys are **never** hand-ordered: the §4.2.1 sort determines wire order, and the key lists this document gives for each context object are **sets**, not an ordering. Because these objects are recomputed independently on both sides of every sealed-PoE operation, the encoder **MUST** be a single shared implementation, or implementations validated against one shared reference vector set, so that the serialisation cannot drift between languages. The conformance vectors at [`../conformance/`](https://github.com/cardanowall/label-309/blob/main/conformance) pin the exact `canonicalEncode` bytes for each context object.

#### Metadata label 309 and the chunk-array transport

A PoE record **MUST** be placed under Cardano transaction metadata label `309`. A transaction **MUST NOT** carry more than one PoE record — a natural consequence of Cardano metadata being a map from integer label to value. A transaction **MAY** carry additional metadata under other labels; a verifier **MUST** ignore every label other than 309 when processing PoE.

The Cardano ledger caps **both** CBOR byte strings (`bstr`, major type 2) and text strings (`tstr`, major type 3) inside transaction metadata at **64 bytes each**. This is a ledger constraint, not a convention of this CIP: a transaction carrying any single metadata `bstr` or `tstr` longer than 64 bytes is rejected by Cardano nodes at submission time, before any verifier sees it. A serialised record body routinely exceeds 64 bytes, so the body crosses the ledger as an **opaque whole-body chunk array**: a single CBOR array of ≤ 64-byte byte strings whose in-order concatenation is the body. This transport split is the **only** chunking this CIP performs — it is the one genuinely ledger-forced step in the format. Because the ledger sees only the transport array and never the fields inside the reassembled body, those fields are ordinary CBOR values with no per-field chunk wrappers and no 64-byte field-level cap: a URI is a single text string, a `COSE_Sign1` is a single byte string, an X-Wing `kem_ct` is a single 1120-byte byte string.

**Producer rule.** A producer **MUST** serialise the record body once to canonical CBOR per the rules above, split that byte string into chunks of 1 to 64 bytes each, and store the resulting definite-length CBOR array of definite-length byte strings (`[ 1* bstr .size (1..64) ]`) as the label-309 value. The chunk-array form is required **regardless of body length**: a body of 64 bytes or fewer is still emitted as a one-element array — never as a bare map, bare byte string, or any other shape. Producers **SHOULD** use the minimal split (every chunk except the last exactly 64 bytes) and **SHOULD NOT** emit zero-length chunks; over-chunking wastes transaction bytes without benefit.

**Verifier rule.** A verifier **MUST** byte-concatenate the array elements in order to reassemble the canonical record body before structural validation, and **MUST** reject any label-309 value that is not such an array (the carriage-error taxonomy below pins the rejection codes). Chunk boundaries carry **no** semantic meaning: two transport arrays whose concatenations are byte-identical denote the same record. Everything in the rest of this document operates on the reassembled record-body bytes; the CDDL at [`../cddl/label-309.cddl`](label-309.cddl) describes that reassembled body — **plain deterministic CBOR, not a ledger `transaction_metadatum`** — and does not model the transport wrapper.

The maximum byte size of a label-309 record is bounded only by the live Cardano protocol parameter `maxTxSize` — which caps the whole transaction, so the record's practical ceiling is `maxTxSize` minus the rest of the carrying transaction, somewhat below 16 KiB in practice. This CIP imposes no schema-level byte ceiling below it: records exceeding the ledger bound are rejected by Cardano nodes before any verifier sees them. A structural validator **MUST NOT** reject a record solely on the basis of size below `maxTxSize`, and **MUST NOT** reject on a high entry count below that ceiling; producers pay per-byte fees that naturally bound record size.

##### Practical size budget (informative)

Approximate reassembled-body sizes for common record shapes, computed from the canonical CBOR encoding of minimal fields — informative only; actual sizes vary with optional fields and entry counts:

| Record shape                                                                | Approximate body bytes                       |
| --------------------------------------------------------------------------- | -------------------------------------------- |
| Hash-only item, single `sha2-256`                                            | ≈ 65 B                                       |
| Dual-hash item (`sha2-256` + `blake2b-256`)                                  | ≈ 110 B                                      |
| Each `ar://` URI                                                             | + ≈ 56 B                                     |
| Each record signature                                                        | + ≈ 130 B (`kid` path) / ≈ 190 B (wallet path) |
| Sealed envelope, fixed fields (`scheme`, `aead`, `nonce`, `kem`, `slots_mac`) | + ≈ 140–150 B                                |
| Each `x25519` recipient slot                                                 | + 94 B                                       |
| Each `mlkem768x25519` recipient slot                                         | + 1 186 B                                    |

The chunk-array transport adds two bytes per 64-byte chunk (≈ 3 %), and the carrying transaction's skeleton — inputs, outputs, fee, witnesses, `auxiliary_data_hash` — typically consumes a few hundred bytes of the 16 384-byte mainnet `maxTxSize`, leaving roughly 15.5 KiB of usable record body. That admits on the order of **160 `x25519` recipients**, or **12 `mlkem768x25519` recipients**, in a single sealed record. The binding constraint on Cardano is therefore the carriage, never `MAX_SLOTS = 1024`: that constant is a decode-time resource bound for validators handling caller-supplied bytes, not an on-chain capacity.

##### Auxiliary-data envelope forms

The metadata map that carries label 309 travels inside the transaction's **auxiliary data**, and the current Cardano ledger era (Conway) admits three auxiliary-data encodings, all of them valid for newly submitted transactions (see the Conway era CDDL in [`cardano-ledger`](https://github.com/IntersectMBO/cardano-ledger)):

| Form                        | Top-level CBOR shape                                                            | Where the metadata map sits   |
| --------------------------- | ------------------------------------------------------------------------------- | ----------------------------- |
| Metadata map                | an untagged map                                                                  | the value itself              |
| Metadata-with-scripts array | a two-element array `[ transaction_metadata, auxiliary_scripts ]`               | element 0                     |
| Tagged map                  | tag 259 — `#6.259({ ? 0 => metadata, ... })`, with further keys carrying scripts | the value under integer key 0 |

A verifier — and any tool that unwraps fetched transaction bytes down to the label-309 value — **MUST** accept all three forms. Dispatch is purely syntactic, on the top-level CBOR type and tag of the auxiliary-data value: a tag-259 value is the keyed-map form; an untagged array is the two-element form; and an **untagged map is always the metadata map itself**. Implementations **MUST NOT** inspect a map's keys to guess which shape it is — a metadata map is keyed by integer labels, so any key-sniffing heuristic (for example, treating a map that happens to contain a small-integer key as a keyed wrapper) would silently mis-parse legitimate metadata. Any other top-level shape, and any tag other than 259 at the top of the auxiliary data, **MUST** be rejected as `MALFORMED_CBOR`. A tag-259 map with no key `0`, and a metadata map with no entry under label 309, are well-formed auxiliary data that simply carry no PoE record; the verifier-layer outcome for that case is pinned in [Structural validation, verifier roles, and error codes](#structural-validation-verifier-roles-and-error-codes).

Producers MAY emit any of the three forms; the choice carries no PoE semantics, and the chunk array reassembles identically under all of them. Whichever form a producer chose, the transaction body's `auxiliary_data_hash` commits to the serialised auxiliary-data bytes exactly as they appear on chain — the binding a verifier checks before reading anything out of fetched transaction bytes.

##### Carriage-error taxonomy

A conformant label-309 value has exactly one shape — the whole-body chunk array — and the non-conformant shapes a consumer can encounter form a small closed set. A verifier, and any structural-validation entry point that accepts caller-supplied label-309 bytes, **MUST** disposition them as follows:

| Label-309 value shape | Disposition |
| --- | --- |
| Definite-length array of definite-length byte strings, each ≤ 64 bytes | **Accepted.** Concatenate the elements in order; the result is the record body. |
| A zero-length byte-string element inside that array | **Tolerated.** Zero-length chunks contribute no bytes to the reassembly and **MUST NOT** be rejected: chunk boundaries are semantics-free, including degenerate ones. |
| A byte-string element longer than 64 bytes | **Rejected — `CHUNK_TOO_LARGE`.** Such a value cannot appear on chain (Cardano nodes refuse the oversized metadata string at submission), but an implementation validating caller-supplied bytes **MUST** still pin this rejection. |
| An array containing any non-byte-string element (text string, integer, map, array, …) | **Rejected — `MALFORMED_CBOR`.** |
| A non-array value: bare map, bare byte string, bare text string, integer, … | **Rejected — `MALFORMED_CBOR`.** |
| An indefinite-length array, or an indefinite-length byte-string element | **Rejected — `MALFORMED_CBOR`.** |

A transport array whose concatenation is empty — an empty array, or one containing only zero-length chunks — reassembles to zero bytes; the failure then surfaces from the canonical decode of the empty body as `MALFORMED_CBOR`, not from the transport layer. The per-chunk 64-byte ceiling is the **single** carriage-level size rule in this CIP; no field inside the reassembled body carries a chunking rule or a 64-byte rule of its own. The error codes named above are defined in [`../registries/error-codes.json`](https://github.com/cardanowall/label-309/blob/main/registries/error-codes.json) and in [Structural validation, verifier roles, and error codes](#structural-validation-verifier-roles-and-error-codes).

#### URI shape rules

Each `uris[]` entry is a single text string carrying exactly one **absolute** URI with no fragment, whose scheme is in the closed fetch set `{ ar://, ipfs:// }`. The following shape checks run on the URI string, offline, before any verifier-side network step, so a malformed URI fails at the earliest possible layer.

**Scheme case-folding.** The URI scheme is case-insensitive per [RFC 3986 §3.1](https://www.rfc-editor.org/rfc/rfc3986#section-3.1): `ar://`, `Ar://`, and `AR://` denote the same scheme. A validator **MUST** lowercase the scheme component before matching it against the fetch set and dispatching to the per-scheme body rules; a mixed-case scheme is therefore not rejected on case grounds, and its body **MUST** still be shape-checked. Only the scheme is case-folded — the remainder of the URI (the Arweave txid, the IPFS CID, any path) is matched **verbatim**, because those are case-sensitive content addresses where a lowercased character would name different bytes. Producers **SHOULD** emit lowercase schemes.

- **`ar://<txid>` (Arweave).** The URI **MUST** match `^ar://[A-Za-z0-9_-]{43}$` — 43 base64url characters, no padding, encoding Arweave's 256-bit transaction id. A mismatch emits `INVALID_URI` (reason `ar_txid_shape`). A query string, path, or fragment on an `ar://` URI is forbidden; the txid alone is the content address.
- **`ipfs://<cid>[/<path>]` (IPFS).** The URI **MUST** be `ipfs://` followed by a CID, optionally followed by a `/`-prefixed path. The CID commits the entire DAG, so a path component navigates within already-committed bytes and does not weaken integrity. A validator **MUST** perform the full offline CID parse — split authority from path at the first `/`, multibase-decode, read the version byte, then the codec and multihash varints — and enforce the CID profile below, emitting `INVALID_URI` (reason `ipfs_cid_unsupported`) for any CID outside the profile. The parse is purely offline, so this mandate applies even to deployments that decline to fetch IPFS content; such a deployment accepts a well-formed CID structurally and then refuses every `ipfs://` URI at fetch time with `URI_TARGET_FORBIDDEN`.

These structural shape checks are independent of verifier-time fetch-policy checks: a URI that passes structural validation MAY still be refused at fetch time, but a URI that fails structural validation never reaches the fetch step.

#### CID profile

The phrase "valid CID" above resolves to the following normative profile. It constrains the multiformats space to a set small enough that every conformant validator can make deterministic accept/reject decisions, while preserving IPFS's self-authentication property (the URI binds the bytes via the multihash). Producers **MUST** emit only CIDs that fit this profile; validators **MUST** reject everything else with `INVALID_URI` (reason `ipfs_cid_unsupported`).

| Component                    | Accepted values                                                                                 | Notes                                                                                                                                                                                              |
| ---------------------------- | ----------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Version**                  | CIDv0, CIDv1                                                                                    | CIDv0 is the fixed shape `Qm…` (46-char base58btc, sha2-256 multihash, no path). New producers **SHOULD** emit CIDv1.                                                                              |
| **Multibase prefix (CIDv1)** | `b` (base32 lower), `B` (base32 upper), `f` (base16 lower), `F` (base16 upper), `z` (base58btc) | All other prefixes (e.g. `m`/`M` base64) **MUST** be rejected. Producers **SHOULD** prefer `b`.                                                                                                    |
| **Multicodec (CIDv1)**       | `0x55` (raw), `0x70` (dag-pb), `0x71` (dag-cbor)                                                | Covers single-file payloads (raw), directory roots for `ipfs://<cid>/<path>` (dag-pb), and structured payloads (dag-cbor). Other codecs **MUST** be rejected.                                      |
| **Multihash**                | `0x12` (sha2-256, 32-byte digest), `0xb220` (blake2b-256, 32-byte digest)                       | Mirrors the content-hash registry ([`../registries/hash-algorithms.json`](https://github.com/cardanowall/label-309/blob/main/registries/hash-algorithms.json)), so an implementer can reuse the same primitives. Other codes **MUST** be rejected. |

Future additions to this profile follow this CIP's algorithm-agility model: any new multibase prefix, multicodec, or multihash code requires an amendment to this document and matching conformance vectors before a producer may emit it.

### Record-level signatures (COSE_Sign1)

Authorship in this CIP is an **opt-in claim, never a requirement.** A record
verifies as a Proof of Existence on the strength of its content hashes and the
block time of its transaction alone; a signature adds _who attests to this
record body_, and its absence does not weaken the existence claim. This CIP (v1)
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
[`../registries/signature-algorithms.json`](https://github.com/cardanowall/label-309/blob/main/registries/signature-algorithms.json).

#### Sig-entry shape

Each `sigs[i]` is a **closed CBOR map** carrying:

- `cose_sign1` — REQUIRED. A `COSE_Sign1` structure ([CIP-8](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0008/README.md),
  [RFC 9052](https://www.rfc-editor.org/rfc/rfc9052)), CBOR-encoded and carried
  as a single CBOR byte string. The whole-body transport of
  [Canonical CBOR and metadata label 309 carriage](#canonical-cbor-and-metadata-label-309-carriage)
  already satisfies the ledger's string cap, so the field carries no length
  bound and no wrapping shape of its own.
- `cose_key` — OPTIONAL. A CBOR-encoded `COSE_Key` blob carrying the signer's
  **public** key, likewise a single CBOR byte string. Present only on the
  CIP-30 wallet path (see [Signer-key identification](#signer-key-identification)).

```
sigs = [
  { "cose_sign1": <bstr> },                       ; in-signature kid (identity-key signer)
  { "cose_sign1": <bstr>, "cose_key": <bstr> },   ; cose_key side-channel (CIP-30 wallet)
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
   empty in a conforming v1 record. Verifiers MUST take the bytes of
   `COSE_Sign1[0]` **exactly as published** and place them in
   `Sig_structure[1]` verbatim; they MUST NOT decode-and-re-encode,
   re-canonicalise, or otherwise normalise the protected header — even where
   the published bytes are not the canonical encoding of the header map —
   because any re-encoding changes `Sig_structure` and fails verification of a
   signature that is in fact valid. This is the one deliberate asymmetry of the
   signing input: the record body in `Sig_structure[3]` is **recomputed** by
   canonical re-encoding (the verifier decodes the record, removes `sigs`, and
   re-encodes), while the protected header in `Sig_structure[1]` is
   **byte-preserved** from the wire.
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
   share the body shape cannot reuse a PoE signature against itself, because
   its `to_sign` would carry a different prefix (or none).

**Detached payload.** The published `COSE_Sign1[2]` (the payload field of the
outer 4-element `COSE_Sign1` array, RFC 9052 §4.2) MUST be CBOR `null` (`0xF6`).
Any attached payload — including a zero-length byte string `h''` — MUST be
rejected as `MALFORMED_SIG_COSE_SIGN1`. The detached form pins the signed bytes
to the canonical record body the verifier recomputes; an attached payload would
let a producer sign borrowed bytes while the COSE structure still validates.

A [CIP-30](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0030/README.md)
`signData` result carries an **attached** payload: the wallet returns a
`COSE_Sign1` whose payload field holds the signed bytes. Before embedding such
a result into `sigs[i].cose_sign1`, the producer **MUST** replace
`COSE_Sign1[2]` with CBOR `null` (`0xF6`). The signature remains valid under
this transformation because the signed `Sig_structure` carries the payload
independently of the published payload field — the verifier reconstructs
`to_sign` from the record body and never reads `COSE_Sign1[2]`. A producer
that embeds the wallet output unmodified ships a non-conformant record
(`MALFORMED_SIG_COSE_SIGN1`) and, worse, republishes the whole record body a
second time inside the signature entry.

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
| `-19` | `Ed25519`, fully-specified ([RFC 9864 §2.2](https://www.rfc-editor.org/rfc/rfc9864#section-2.2) IANA assignment)                | **Optional.** Verified identically to `-8` under the same strict Ed25519 primitive when accepted.                         |

Both labels are recorded in
[`../registries/signature-algorithms.json`](https://github.com/cardanowall/label-309/blob/main/registries/signature-algorithms.json).
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
Although `hashed` sits in the **unprotected** header, its malleability is not an
integrity surface: flipping the flag in transit changes which bytes the verifier
reconstructs as `Sig_structure[3]`, so verification of an honest signature
simply fails — a denial-of-service-grade nuisance, never a forgery.

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
> key identifier — typically a pointer to look up a key out of band. This CIP's
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
record, the producer MUST place the wallet's `COSE_Key` blob into the
**same** `sigs[i]` entry under the key `cose_key`. The `COSE_Key` describes an
Ed25519 public key: label `1` (`kty`) = `1` (OKP), label `-1` (`crv`) = `6`
(Ed25519), label `-2` (`x`) = the 32-byte public key. If `alg` (label `3`) is
present it MUST be `-8`.

**Public key only — never a private key.** `sigs[i].cose_key` MUST describe only
the public half of the key pair. Producers MUST NOT include any private-key
material (the OKP/EC2 `d` field, COSE_Key label `-4`, or any other private-key
label in the [IANA COSE Key Type Parameters registry](https://www.iana.org/assignments/cose)).
A structural validator MUST decode the `cose_key` blob and MUST reject
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
`Blake2b-224` hash of the stake verification key. The protected-header
`address` is **REQUIRED** on path 2: a path-2 signature whose protected header
carries no `address` **MUST** be rejected with `WALLET_ADDRESS_MISMATCH` — the
wallet binding is the path's whole point, and an address-less wallet signature
gives the verifier nothing to bind. The Ed25519 signature alone proves only
that the key in `cose_key` signed the record body — the `address` field is
otherwise an unverified claim. Verifiers **MUST** derive the expected network
header byte from the network of the **transaction containing the record**
(`0xe1` when it is a mainnet transaction, `0xe0` for a testnet one), recompute
`address_derived = expected_network_header || Blake2b-224(pubkey)` from the
resolved 32-byte public key, and reject the signature with
`WALLET_ADDRESS_MISMATCH` unless `address_derived` byte-equals the **full
29 bytes** of the protected-header `address`. Deriving the header byte from the
containing transaction — never echoing the byte found in the record — rejects a
signature produced for one network and replayed under another. UI consumers
MUST NOT surface the stake address as authenticated metadata without this check
passing. v1 binds the wallet path to **stake (reward) addresses only** — a
non-stake-address-format `"address"` fails the recomputation and is rejected as
`WALLET_ADDRESS_MISMATCH`; producers using CIP-30 wallets MUST request
`signData` with a stake-address argument. Path-1 records carry no `address`
claim and skip this step.

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
2. Otherwise, if `sigs[i].cose_key` is present, decode it as `COSE_Key` and
   extract the Ed25519 public key from label `-2`. The
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

A PoE cryptographic identity is exactly one thing: a 32-byte master
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
| Validity      | Any 32-byte value is a valid input. Implementations MUST NOT reject a seed for low-entropy patterns at the derivation API; the all-zero seed is a valid input and is used by the conformance vectors (see [`../conformance/`](https://github.com/cardanowall/label-309/blob/main/conformance)) for byte-exact reproducibility |
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
bytes. The same zero-length-octet-string convention applies wherever this CIP
writes `salt=""` for an HKDF-Extract step (notably the slot-set MAC-key
derivation; see [Slot-set MAC](#slot-set-mac)). This is pinned by a byte-exact
conformance vector rather than left to a library default, so an implementation
that mishandles the absent salt fails the vector. The requested HKDF expansion
length MUST be 32 bytes for each of the three derivations.

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
| Public-key role | The recipient key for the `x25519` KEM. It is NOT carried on a PoE record's encryption envelope; recipients trial-decrypt with their private key |
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
its registry entry is [`../registries/kem-algorithms.json`](https://github.com/cardanowall/label-309/blob/main/registries/kem-algorithms.json).

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

A recipient public key never appears on a PoE record. Each
encryption slot carries only per-slot key material and a wrapped CEK; the
KEM identifier appears once on the encryption envelope. Senders obtain a
recipient public key out-of-band; this standard mandates no single discovery
channel, and key provenance is the sender's responsibility.

#### Recipient public-key and secret encodings

A sealed-PoE sender needs the recipient's KEM public key in a portable
string form. This CIP reuses the age ecosystem's Bech32 encodings, one
human-readable prefix (HRP) per registered KEM. The HRPs are pinned in the
KEM registry [`../registries/kem-algorithms.json`](https://github.com/cardanowall/label-309/blob/main/registries/kem-algorithms.json).

In Bech32 the `1` is the HRP-to-data separator, so the human-visible prefix of a
string carries the HRP plus that `1`: an `age1…` string has HRP `age`. The two are
listed separately below.

| KEM              | Recipient public key     | Public-key HRP | Public-key visible prefix          | Secret / identity HRP | Secret visible prefix |
| ---------------- | ------------------------ | -------------- | ---------------------------------- | --------------------- | --------------------- |
| `x25519`         | 32 B X25519 public key   | `age`          | `age1…` (standard age v1, 62 chars) | `AGE-SECRET-KEY-`     | `AGE-SECRET-KEY-1…`   |
| `mlkem768x25519` | 1216 B X-Wing public key | `age1pqc`      | `age1pqc1…` (1960 chars)           | `AGE-SECRET-KEY-PQ-`  | `AGE-SECRET-KEY-PQ-1…` |

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
encode and decode the `age1pqc1…` string **without** enforcing the
90-character limit, while still applying the Bech32 checksum and charset
rules. The HRP is `age1pqc` (NOT `age1pq`) by design — the shorter `age1pq`
prefix is claimed by an upstream native ML-KEM-768 + X25519 encoding for the
same primitive, and the distinct `age1pqc` HRP guarantees the two recipient
encodings never collide on the wire. The classical `age1…` string stays
within ordinary lengths; its handling is unchanged.

Both encodings are recipient-discovery conveniences. The KEM public key
never appears on a PoE record; senders obtain it out-of-band and the
standard mandates no single discovery channel.

### Sealed PoE: multi-recipient encryption

A **sealed PoE** publishes a public, permanent, timestamped commitment to a
plaintext digest while keeping the plaintext itself readable only by an intended
audience. The on-chain record carries the plaintext hash (public, anchored to
block time) and an encryption envelope (`enc`) carrying the key-delivery
material; the **ciphertext** lives off-chain — published at a content-addressed
URI (`ar://` or `ipfs://`) or delivered out of band — and is undecryptable
without a matching unlock secret. PoE alone
gives the time claim but no audience binding; PoE plus open ciphertext gives no
privacy. Sealed PoE bridges the two.

The construction is an **age-style multi-recipient KEM-then-wrap** design: a
single content-encryption key (CEK) encrypts the plaintext once, and that CEK is
independently wrapped to each recipient under a per-slot key. It is **not** RFC
9180 HPKE: there is no `suite_id`, no `LabeledExtract`/`LabeledExpand` cascade.
Reviewers SHOULD evaluate it against the ECIES/DHIES literature and the
[age v1 specification](https://github.com/C2SP/C2SP/blob/main/age.md), from which
its stanza pattern derives.

This construction uses the age stanza pattern — per-recipient KEM material plus a
symmetric wrap of the file key — for **both** registered KEMs. The classical
`x25519` path closely mirrors age's native X25519 recipient. The hybrid
`mlkem768x25519` path deliberately **diverges** from age's own post-quantum
choice: age v1.3.0 ships native post-quantum recipients (human-readable prefix
`age1pq`) that wrap the file key via HPKE `SealBase`
([RFC 9180](https://www.rfc-editor.org/rfc/rfc9180)) over an ML-KEM-768 + X25519
KEM, **not** the stanza pattern. This CIP keeps the stanza wrap for the hybrid
path so that one uniform wrap and one uniform header-binding (see
[Slot-set MAC](#slot-set-mac)) cover both KEMs with no HPKE dependency. The
hybrid wrap therefore does **not**
inherit age's HPKE construction, and no age-inheritance claim is made for it; the
`age1pqc` recipient encoding (distinct from age's `age1pq`) reflects that the two
hybrid encodings are independent.

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
of `slots`/`passphrase` is present, and consequently in where the key commitment
lives — the slots path commits to the CEK **on chain** via `slots_mac`, while the
passphrase path commits in a 32-byte header **inside the ciphertext blob** (see
[Passphrase path](#passphrase-path)). The grammar admits both as a permissive
superset; the cross-field rules are normative (see
[Envelope shape and exclusivity](#envelope-shape-and-exclusivity)).

#### Envelope shape and exclusivity

The sealed-PoE envelope carries its own version integer, `enc.scheme`, separate
from the top-level record `v`. `enc.scheme` is the construction-**family**
version: it fixes the cross-KEM parts of the construction — the slot-set MAC
schedule and the segmented-STREAM content format. The per-slot KEM is **not**
selected by `enc.scheme`; it is selected by the `enc.kem` field, which fixes the
slot shape and the per-slot KEK derivation. Verifiers **MUST** require
`enc.scheme == 1` before processing an envelope: the recipient verifier, and
any verifier in strict sealed-crypto mode, rejects any other value
(`UNSUPPORTED_ENVELOPE_SCHEME`); in the default public-verifier reading an
unrecognised `scheme` makes the whole envelope opaque and the item is tagged
`ENC_UNSUPPORTED` while the content-hash claim still validates (see
[Structural validation, verifier roles, and error codes](#structural-validation-verifier-roles-and-error-codes)).
Adding or changing a per-slot KEM is an additive registry entry under the
**same** `enc.scheme`; a change to the MAC algorithm, its key derivation, the
transcript schemas, or the content STREAM layout — which applies to all KEMs at
once — is what bumps `enc.scheme`. More broadly, `enc.scheme: 1` identifies the
**entire** cryptographic suite, not merely the MAC and the content format: the
`canonicalEncode` rules, the slot schema, the HKDF hash, the HMAC hash, the
per-slot wrap AEAD, the segmented-STREAM content format, the slots and
passphrase transcript schemas (including the `hashes_hash` item binding), the
in-ciphertext passphrase commitment, the pinned X-Wing revision, the
domain-separation labels, the Argon2id version and profile, and the passphrase
normalization profile are all fixed by it, so a change to **any** of them
requires a new `enc.scheme` value.

The `enc` map under the multi-recipient path:

| field        | type  | rule                                                                                            |
| ------------ | ----- | ----------------------------------------------------------------------------------------------- |
| `scheme`     | uint  | REQUIRED. `1`.                                                                                  |
| `aead`       | tstr  | REQUIRED. Content-format identifier; `chacha20-poly1305-stream64k`.                             |
| `nonce`      | bstr  | REQUIRED. 24 bytes, envelope-unique (drawn fresh per `enc` envelope); salts the content `payload_key` and both per-slot KEK salts. |
| `kem`        | tstr  | REQUIRED when `slots` present (`x25519` or `mlkem768x25519`).                                   |
| `slots`      | array | REQUIRED on this path. `[ 1* slot ]`, N ≥ 1.                                                    |
| `slots_mac`  | bstr  | REQUIRED when `slots` present. 32 bytes.                                                        |
| `passphrase` | map   | FORBIDDEN on this path.                                                                         |

The cross-field invariants the structural validator **MUST** enforce:

1. Records carrying both `slots` and `passphrase` → `ENC_EXCLUSIVITY_VIOLATION`.
2. Records carrying neither `slots` nor `passphrase` → `ENC_NO_KEY_PATH`.
3. `slots` present but `kem` absent → `ENC_KEM_REQUIRED`.
4. `slots` present but `slots_mac` absent → `ENC_SLOTS_MAC_REQUIRED`.
5. `slots_mac` present but `slots` absent → `ENC_SLOTS_REQUIRED`. (Such an
   envelope, lacking `passphrase` too, also satisfies rule 2 — `ENC_SLOTS_REQUIRED`
   and `ENC_NO_KEY_PATH` co-fire by construction.)
6. `passphrase` present together with any of `kem` / `slots` / `slots_mac` →
   `ENC_EXCLUSIVITY_VIOLATION`.
7. `slots` present but empty → `ENC_SLOTS_EMPTY`.

An item carrying an `enc` envelope **MUST** also declare at least one content
hash under a key **from the content-hash registry** in its `hashes` map: the
ciphertext is bound to the plaintext only through that digest (see
[Plaintext-hash binding](#plaintext-hash-binding-and-the-sender-identity-verdict-split)).
`ENC_REQUIRES_CONTENT_HASH` fires exactly when `enc` is present and no `hashes`
key is a registered content-hash identifier — for example, a map whose only key
is an unregistered identifier; it MAY co-fire with `UNSUPPORTED_HASH_ALG` on
the same item.

The full grammar for `enc`, `slot`, and `passphrase-block` is the authoritative
machine artifact [`../cddl/label-309.cddl`](label-309.cddl); the cross-field
rules above are not expressible in CDDL and are enforced in a second pass.

#### KEM selection and the no-mixing rule

Two per-slot KEMs are registered under `enc.scheme = 1` **from the first release**
— the post-quantum hybrid is part of v1, not a later migration. `enc.kem` selects
the KEM, the slot shape, and the KEK derivation.

| `enc.kem`        | KEM                                   | recipient public key | slot shape                               | KEK info label                      | HRP       |
| ---------------- | ------------------------------------- | -------------------- | ---------------------------------------- | ----------------------------------- | --------- |
| `x25519`         | X25519 (classical)                    | 32 B                 | `{ epk: bstr(32), wrap: bstr(48) }`      | `cardano-poe-kek-v1`                | `age`     |
| `mlkem768x25519` | X-Wing = ML-KEM-768 + X25519 (hybrid) | 1216 B               | `{ kem_ct: bstr(1120), wrap: bstr(48) }` | `cardano-poe-kek-mlkem768x25519-v1` | `age1pqc` |

These identifiers are the registry entries
[`../registries/kem-algorithms.json`](https://github.com/cardanowall/label-309/blob/main/registries/kem-algorithms.json); the
content format is [`../registries/aead-algorithms.json`](https://github.com/cardanowall/label-309/blob/main/registries/aead-algorithms.json).
An unregistered `enc.kem` → `UNSUPPORTED_KEM_ALG`; an unregistered `enc.aead` →
`UNSUPPORTED_AEAD_ALG` — both in the strict reading (the recipient verifier and
strict sealed-crypto mode); the default public-verifier reading instead treats
the envelope as opaque and tags the item `ENC_UNSUPPORTED` (see
[Structural validation, verifier roles, and error codes](#structural-validation-verifier-roles-and-error-codes)).

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
secrets. That "never below X25519 classical security" floor is scoped to **validly
generated** recipient keys: it presumes the public key passes the pinned X-Wing
revision's key-validity check (see slot construction below). The classical `x25519`
KEM remains available for recipients whose published key is X25519-only; sealing
with it is NOT RECOMMENDED where confidentiality must outlive the elliptic-curve
era (see
[Harvest-now, decrypt-later and the `x25519` KEM](#harvest-now-decrypt-later-and-the-x25519-kem)).

The identifier `mlkem768x25519` deliberately omits hyphens, matching the
X-Wing/age ecosystem name for the construction. X-Wing parameters (see
[draft-connolly-cfrg-xwing-kem-10](https://datatracker.ietf.org/doc/draft-connolly-cfrg-xwing-kem/10/)):

```text
public key   : 1216 bytes = ML-KEM-768 ek (1184) || X25519 pk (32)
ciphertext   : 1120 bytes = ML-KEM-768 ct (1088) || X25519 ephemeral (32)
shared secret: 32 bytes
combiner     : SHA3-256( ss_MLKEM || ss_X25519 || ct_X25519 || pk_X25519 || label )
```

The X-Wing decapsulation key is a 32-byte seed (the public key derives
deterministically from the seed); ML-KEM uses implicit rejection.

#### Slot construction (sender)

For each `enc`-bearing item the sender selects that envelope's KEM, obtains N
recipient public keys out-of-band in that KEM's encoding (N ≥ 1), generates the
envelope's 32-byte CEK and its 24-byte `enc.nonce` (both fresh from a CSPRNG
per envelope; the nonce is an input to every per-slot KEK salt below), then for
each recipient derives a per-slot KEK and wraps the **same** CEK under it.

**`x25519` (classical).** A fresh ephemeral X25519 keypair per slot:

```text
priv_epk_i : randomBytes(32)                         ; fresh per slot
pub_epk_i  : x25519_publicKey(priv_epk_i)
shared_i   : x25519_sharedSecret(priv_epk_i, pub_R_i)
kek_salt_i : SHA-256("cardano-poe-x25519-kek-salt-v1" || enc.nonce || pub_epk_i || pub_R_i)  ; 32 B
KEK_i      : HKDF-SHA-256(ikm  = shared_i,
                          salt = kek_salt_i,             ; binds nonce, epk, and pub_R
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
enc_i    = XWing.Encapsulate(pub_R_i)    ; named fields — MUST NOT consume positional order
kem_ct_i = enc_i.ct                       ; 1120 B
shared_i = enc_i.ss                       ; 32 B
kek_salt_i : SHA-256("cardano-poe-xwing-kek-salt-v1" || enc.nonce || kem_ct_i || pub_R_i)   ; 32 B
KEK_i  : HKDF-SHA-256(ikm  = shared_i,
                      salt = kek_salt_i,                               ; binds nonce, kem_ct, and pub_R
                      info = "cardano-poe-kek-mlkem768x25519-v1",      ; 33 ASCII bytes
                      L    = 32)
wrap_i : ChaCha20-Poly1305(key=KEK_i, nonce=zeros(12),
                           ad="cardano-poe-kek-mlkem768x25519-v1", plaintext=CEK)  ; 48 B
slot_i : { "kem_ct": kem_ct_i, "wrap": wrap_i }
```

`kem_ct_i` in the salt input is the slot's 1120-byte X-Wing ciphertext exactly
as carried in `slot.kem_ct`, and `pub_R_i` is the 1216-byte X-Wing recipient
public key the slot is sealed to. `XWing.Encapsulate` **MUST** apply the pinned
X-Wing revision's public-key validity check to `pub_R_i` and reject an invalid
key rather than encapsulating to it; this is the precondition under which the
hybrid floor never drops below X25519 classical security. The construction
consumes X-Wing through an adapter with **named fields only**: `Encapsulate(pk)`
yields `.ct` (1120 B) and `.ss` (32 B); `Decapsulate(sk, ct)` yields the 32-byte
shared secret. Implementations **MUST** map to the pinned revision's API by name
and **MUST NOT** consume positional return values — the pinned revision returns
`(ss, ct)` from encapsulation and writes decapsulation as `Decapsulate(ct, sk)`,
the reverse of a naive left-to-right reading. Both KEK-salt label literals
(`cardano-poe-x25519-kek-salt-v1`, `cardano-poe-xwing-kek-salt-v1`) are exact
ASCII with no terminator and no length prefix; `||` is byte concatenation.

The X25519 ephemeral is the trailing 32 bytes of `kem_ct_i`; a hybrid slot has
**no** separate `epk` field. `kem_ct` is carried as a single CBOR byte string of
exactly 1120 bytes.

**Per-slot KEK domain separation.** Both KEMs derive a 32-byte KEK with
HKDF-SHA-256, each with a KEM-specific labelled-hash salt and a KEM-specific
`info`. The salt has one uniform shape under both KEMs —
`SHA-256(label || enc.nonce || <slot KEM material> || pub_R)` — and binds three
values. The slot's own KEM material (the X25519 ephemeral `epk`, or the X-Wing
ciphertext `kem_ct`) anchors the KEK to a slot-unique value. The recipient
public key `pub_R` binds the KEK to the specific recipient, defeating
confused-deputy relay of a slot's KEM material against a different recipient.
And the envelope-unique `enc.nonce` anchors the KEK to one envelope: a CSPRNG
failure that repeats KEM randomness across two envelopes then degrades to mere
cross-envelope linkability instead of reproducing the same `(KEK, zero-nonce)`
wrap pair (see the zero-nonce condition below). This binding is computed
**outside** the KEM, over the slot's own wire bytes, so it holds X-Wing as a
black-box KEM and does not rely on any property of the combiner's internal
hashing. The distinct `info` labels additionally supply cross-KEM domain
separation, so that no KEK derived under one KEM can equal a KEK derived under
the other on an identical 32-byte shared secret. The `pub_R` term in both salts
is the recipient key's **canonical wire encoding** — exactly the 32-byte
`x25519_publicKey(priv_R)` for `x25519`, exactly the pinned 1216-byte X-Wing
public-key byte string for `mlkem768x25519`; producer and verifier **MUST** use
that exact encoding and **MUST NOT** substitute any non-canonical or re-encoded
equivalent, or the two sides derive different KEKs. The two `info` labels and
the two salt labels **MUST** match the literals above byte-for-byte. The KDF and
the SHA-256 salt construction are internal building blocks (see
[Sealed-PoE internal labels](#sealed-poe-internal-labels)): they carry no wire
identifier — they are fixed, not selectable.

**Per-slot wrap: zero-nonce ChaCha20-Poly1305.** The wrap uses RFC 8439
ChaCha20-Poly1305 (the 12-byte-nonce variant) as a single-shot AEAD with a
12-byte **zero** nonce, AAD set to the KEM's `info` label literal (never empty
AAD), producing exactly 48 bytes (32-byte CEK ciphertext + 16-byte Poly1305 tag).
The zero nonce is safe **only** because `KEK_i` is per-slot and used for exactly
one wrap: each slot draws fresh KEM randomness (a fresh X25519 ephemeral, or a
fresh X-Wing encapsulation), so `KEK_i` is unique per slot at negligible
collision probability, and the envelope-unique `enc.nonce` in every KEK salt keeps
KEKs distinct across envelopes even where KEM randomness repeats. The safety
condition is therefore exactly **per-slot KEK uniqueness**, and every
producer-side mechanism that could repeat a `(KEK_i, nonce)` pair violates it: a
CSPRNG failure that repeats KEM randomness within a record; deterministic or
colliding encapsulation; reuse of a slot (or of `enc.nonce` together with a
slot) across records; caching of a derived KEK keyed by `(pub_R, epk)` alone; or
recipient deduplication that reuses one slot for two appearances of the same
recipient. A producer **MUST NOT** introduce any of these
(see [Forbidden patterns](#forbidden-patterns)). A verifier cannot detect
cross-record or cross-key KEK reuse — that stays a producer obligation; the
verifiable slice is the **within-record duplicate**, so a conformance vector
**MUST** exercise two slots sharing an `epk` (or `kem_ct`) and require rejection
with `ENC_SLOTS_DUPLICATE_KEM_MATERIAL`. Were a future revision to permit
KEK reuse, the zero nonce **MUST** be replaced with a fresh nonce in the same
change. Any modification of either KEM's KEK derivation is security-critical.

**Slot shuffle (REQUIRED).** The order in which a sender supplies recipient keys
is privileged metadata (e.g. "primary recipient first"). Publishing slots in
input order leaks it. The sender **MUST** shuffle `slots[]` with a CSPRNG (an
unbiased Fisher-Yates permutation — a plain `u32 % m` index draw skews toward low
residues and **MUST** be rejection-sampled to a uniform index) **before**
computing the slot-set MAC. The MAC binds the shuffled on-wire order.

#### Sealed-PoE internal labels

The per-record sealed-PoE construction draws its domain separation from a fixed
set of internal label literals. Each is exact ASCII with no terminator and no
length prefix; each is a **fixed constant** of `enc.scheme: 1`, never serialised
on the wire and never selectable through any registry. They partition into HKDF
`info` tags and SHA-256 prefix labels (KEK-salt prefixes, transcript prefixes,
and the item-hashes prefix):

| Label                                  | Role                                                          | Used in                                                                        |
| -------------------------------------- | ------------------------------------------------------------- | ------------------------------------------------------------------------------ |
| `cardano-poe-kek-v1`                   | HKDF `info` for the per-slot KEK on the `x25519` path         | [Slot construction](#slot-construction-sender)                                 |
| `cardano-poe-kek-mlkem768x25519-v1`    | HKDF `info` for the per-slot KEK on the `mlkem768x25519` path | [Slot construction](#slot-construction-sender)                                 |
| `cardano-poe-x25519-kek-salt-v1`       | SHA-256 prefix for the `x25519` KEK HKDF `salt`               | [Slot construction](#slot-construction-sender)                                 |
| `cardano-poe-xwing-kek-salt-v1`        | SHA-256 prefix for the `mlkem768x25519` KEK HKDF `salt`       | [Slot construction](#slot-construction-sender)                                 |
| `cardano-poe-item-hashes-v1`           | SHA-256 prefix for the item-hashes digest `hashes_hash`       | [Slot-set MAC](#slot-set-mac), [Passphrase path](#passphrase-path)             |
| `cardano-poe-slots-transcript-v1`      | SHA-256 prefix for the slots-transcript hash `slots_hash`     | [Slot-set MAC](#slot-set-mac)                                                  |
| `cardano-poe-slots-mac-v1`             | HKDF `info` for the slot-set MAC key                          | [Slot-set MAC](#slot-set-mac)                                                  |
| `cardano-poe-passphrase-transcript-v1` | SHA-256 prefix for the passphrase-transcript hash `pw_hash`   | [Passphrase path](#passphrase-path)                                            |
| `cardano-poe-passphrase-mac-v1`        | HKDF `info` for the passphrase commitment MAC key             | [Passphrase path](#passphrase-path)                                            |
| `cardano-poe-payload-v1`               | HKDF `info` for the slots-path content `payload_key`          | [Content encryption](#content-encryption)                                      |
| `cardano-poe-payload-passphrase-v1`    | HKDF `info` for the passphrase-path content `payload_key`     | [Content encryption](#content-encryption), [Passphrase path](#passphrase-path) |

These labels are distinct from the seed-derivation `info` strings of
[Seed and key derivation](#seed-and-key-derivation) and from the record-signing
domain prefix `cardano-poe-record-sig-v1`; no per-record sealed-PoE label shares a
byte sequence with a long-term-key-derivation label, so identity-key derivation
and per-record key wrapping never collide. The set is moreover **collision-free
and prefix-free**: no label in this table equals, or is a byte-prefix of, any
other label in the table or of any seed-derivation label, so the input to one
labelled hash or HKDF can never be reinterpreted as the input to another. A
verifier **MUST** use each literal byte-for-byte; a single divergent byte yields
a `slots_mac`, commitment, or AEAD tag that the honest producer cannot
reproduce.

#### Slot-set MAC

After the shuffle, the sender binds the full slot set — together with the
cross-KEM header fields that fix how the slots are interpreted, and the item's
plaintext-hash claim — to the CEK. The binding is a two-step construction: a
**slots transcript** is hashed once to a 32-byte `slots_hash`, and that hash is
the message of a CEK-keyed HMAC.

```text
hashes_hash : SHA-256("cardano-poe-item-hashes-v1" || canonicalEncode(item.hashes))   ; 32 bytes

SLOTS_TRANSCRIPT = {                            ; closed map; keys are a set, not an order
    "scheme":      1,                           ; uint
    "path":        "slots",                     ; text
    "aead":        <enc.aead>,                  ; text: the content-format identifier
    "kem":         <enc.kem>,                   ; text: "x25519" | "mlkem768x25519"
    "nonce":       <enc.nonce>,                 ; bytes(24)
    "slots":       <slots>,                     ; the shuffled on-wire slot array
    "hashes_hash": hashes_hash                  ; bytes(32)
}
slots_hash : SHA-256("cardano-poe-slots-transcript-v1" || canonicalEncode(SLOTS_TRANSCRIPT))  ; 32 bytes
HMAC_KEY   : HKDF-SHA-256(ikm=CEK, salt="", info="cardano-poe-slots-mac-v1", L=32)
                                                ; info = 24 ASCII bytes
slots_mac  : HMAC-SHA-256(key=HMAC_KEY, msg=slots_hash)   ; 32 bytes
```

`SLOTS_TRANSCRIPT` is a closed map carrying exactly the seven-key set above; it
is serialised by `canonicalEncode` (see [`canonicalEncode`: deterministic encoding of
protocol context objects](#canonicalencode-deterministic-encoding-of-protocol-context-objects)),
and its key order is determined by the RFC 8949 §4.2.1 sort, never hand-arranged.
The `slots` value is the shuffled array of closed slot maps exactly as they
appear on the wire — `{ epk, wrap }` for `x25519`, `{ kem_ct, wrap }` for
`mlkem768x25519` — so the full per-slot wire content of every slot is inside the
transcript. The transcript additionally pins `scheme`, `path`, `aead`, `kem`,
and `nonce`: a relay that flips any of those header fields while leaving the
slot shapes valid produces a different `slots_hash`, so the MAC fails. The
`slots_hash` and `hashes_hash` SHA-256 prefixes
(`cardano-poe-slots-transcript-v1`, `cardano-poe-item-hashes-v1`) are exact
ASCII with no terminator and no length prefix.

**The transcript binds the item's hash claim.** `hashes_hash` is a labelled
SHA-256 over the `canonicalEncode` of this item's complete `hashes` map — every
algorithm entry, canonically ordered. Because the recipient recomputes
`slots_mac` from on-chain bytes alone, a MAC match confirms the envelope was
sealed for **this item's hash claim**: an envelope spliced onto an item with a
different `hashes` map fails the on-chain match step, before any ciphertext
fetch. In a record with multiple `enc`-bearing items, each item's envelope
computes its own `hashes_hash` over its own `item.hashes` and binds it into that
item's own transcript. The item's `uris[]` are deliberately **not** bound:
ciphertext may be re-hosted or mirrored at a new content-addressed URI without
invalidating the envelope — the storage-agnostic invariant working as intended —
and a sender for whom the URI list is part of the claim binds it with a
record-level signature instead (see
[Record-level signatures (COSE_Sign1)](#record-level-signatures-cose_sign1)).

`slots_hash` is computed **once per `enc`-bearing item** — each envelope hashes
its own transcript, over its own `item.hashes`, before that item's trial-decrypt
loop runs — and is **constant** across that loop: the per-slot MAC check re-keys
HMAC from each candidate CEK but always over the same 32-byte `slots_hash`. The commitment
property is preserved because the HMAC key is still `HKDF-SHA-256(CEK, …)`: pre-
hashing the transcript only changes the HMAC **message** from the full transcript
to its SHA-256, leaving the CEK-keyed binding intact.

The MAC algorithm (HMAC-SHA-256), its key derivation (HKDF-SHA-256 with info
`cardano-poe-slots-mac-v1`), and the slots-transcript schema are **fixed by
`enc.scheme`** and identical for both KEMs. There is no on-wire identifier for the
slot-set MAC; exactly one construction is defined per `enc.scheme` value.

**Why 32 bytes is enough.** `slots_mac` is a key commitment, and the adversary
who attacks a commitment is the **sender at sealing time** — the party who
chooses the slots and the CEKs and who would need two distinct CEKs that verify
against one transcript. That is a collision search mounted _before_
publication, so harvest-now-decrypt-later cost models do not apply to the
commitment; the governing bound is the generic ~2^128 classical collision
resistance of HMAC-SHA-256's 256-bit output. The HMAC key is always the
fixed-length 32-byte HKDF output, which structurally excludes the well-known
HMAC ambiguity in which an over-block-length key and its hash verify
identically — no key this construction can produce has such a colliding
partner.

The `slots_mac` length **MUST** be exactly 32 bytes (`ENC_SLOTS_MAC_INVALID_LENGTH`
on a wrong length) and **MUST** be verified in constant time.

#### Content encryption

The plaintext is encrypted once under a content `payload_key` derived from the
CEK, in the segmented-STREAM format named by the content-format identifier
`chacha20-poly1305-stream64k`:

```text
payload_key : HKDF-SHA-256(ikm=CEK, salt=enc.nonce, info="cardano-poe-payload-v1", L=32)            ; slots path
            : HKDF-SHA-256(ikm=CEK, salt=enc.nonce, info="cardano-poe-payload-passphrase-v1", L=32)  ; passphrase path

STREAM:
  cipher          : ChaCha20-Poly1305 (RFC 8439; 12-byte nonce, 16-byte tag)
  CHUNK_SIZE      : 65536 bytes of plaintext per non-final chunk
  chunk nonce     : uint88_be(counter) || final_flag           ; 12 bytes
                    counter starts at 0, +1 per chunk;
                    final_flag = 0x01 on the final chunk, 0x00 otherwise
  per-chunk AAD   : empty
  final chunk     : 0 to 65536 plaintext bytes; every non-final chunk is exactly 65536
  empty plaintext : exactly one final chunk of zero-length plaintext (a lone 16-byte tag)

ciphertext = seal(chunk_0) || seal(chunk_1) || ... || seal(chunk_final)
                                                ; each sealed chunk = plaintext length + 16 bytes
```

This is the STREAM layout of the
[age v1 specification](https://github.com/C2SP/C2SP/blob/main/age.md): each
chunk is sealed with ChaCha20-Poly1305 under `payload_key` and a 12-byte nonce
formed from an 11-byte big-endian chunk counter followed by a one-byte final
flag. The final flag domain-separates the last chunk, so truncation is
detectable: a stream whose last chunk does not carry the `0x01` flag, a `0x01`
flag on a chunk that is not last, data following the final chunk, or a
non-final chunk shorter than `CHUNK_SIZE` **MUST** all fail decryption. The
layout also implies a structural floor: every sealed chunk is at least 16 bytes
(its tag), so a well-formed slots-path ciphertext blob is never shorter than
16 bytes — the lone tag of an empty final chunk. A blob shorter than that
floor, or whose tail cannot form a well-formed final chunk, is malformed
ciphertext and **MUST** fail decryption as a chunk-layout violation
(`TAMPERED_CIPHERTEXT`). The
segmented format exists so a verifier can authenticate and release a multi-GiB
payload incrementally with bounded memory instead of buffering it whole.

The content is encrypted under `payload_key`, not under the CEK directly: the
CEK is the wrap target the slots (or the passphrase KDF) deliver, and the
content key is a separate HKDF leaf of it (salt = `enc.nonce`, path-specific
`info`), so the wrap layer and the content layer never key the same primitive
on the same bytes. The counter-based chunk nonces are safe because
`payload_key` is **single-use**: it derives from a fresh CEK salted by the
envelope-unique `enc.nonce`, so no two streams ever share a `(key, nonce)` pair
and stateless producers (browser tabs, CLI invocations, workers, retries) never
coordinate nonces across envelopes.

The per-chunk AAD is empty by design: all context is bound to the content
**transitively**. `payload_key` derives from the CEK, and the CEK is committed
to the full header by `slots_mac` on the slots path (whose transcript covers
`scheme`, `path`, `aead`, `kem`, `nonce`, the slot set, and `hashes_hash`) or by
the in-ciphertext commitment on the passphrase path (see
[Passphrase path](#passphrase-path)). Flipping any header field changes what
the recipient derives or accepts, and decryption fails; a per-chunk AAD would
re-bind the same context on every chunk without adding security.

**Tentative release.** Each chunk's Poly1305 tag is verified before that
chunk's plaintext is released, and truncation is caught by the final flag — but
the plaintext-hash recheck (see
[Plaintext-hash binding](#plaintext-hash-binding-and-the-sender-identity-verdict-split))
runs over the **whole** plaintext, post-hoc. A streaming consumer **MUST**
therefore treat released bytes as **tentative** — no side effects, no
acknowledgement, no "received" status — until the final plaintext-hash check
passes.

The plaintext input is the exact original content bytes; the ciphertext **MUST**
decrypt back to those bytes and only those. The construction does **not** prepend,
append, or encrypt a filename, MIME type, size field, or any metadata wrapper.

**Ciphertext blob layout.** The published ciphertext is a single object:

```text
slots path      : ciphertext blob = [ STREAM chunks ]
passphrase path : ciphertext blob = [ commitment: 32 bytes ] || [ STREAM chunks ]
```

On the passphrase path a 32-byte key-commitment header (see
[Passphrase path](#passphrase-path)) is prepended **inside the same blob** —
same object, same URI, same fetch; there is never a second stored object.

**Bounds.** The format's pinned constants are `CHUNK_SIZE = 65536` and
`TAG_SIZE = 16`; the 88-bit counter admits at most `2^88` chunks, far above any
realisable payload. Each chunk is sealed under a distinct `(key, nonce)` pair
well within the RFC 8439 single-invocation limits, so the format imposes no
cryptographic payload ceiling — the practical maximum payload is a deployment
denial-of-service policy, not a wire constant. Producers and verifiers **MUST**
reject a stream whose chunk layout violates the format rules above.

The assembled `enc` map (`{ scheme, aead, kem, nonce, slots, slots_mac }`) is
carried in the on-chain PoE record; the **ciphertext bytes are not placed on
chain**. The ciphertext is published to a content-addressed store and the
resulting URI lands in the item's `uris[]` — see
[Ciphertext storage](#ciphertext-storage-and-integrity).

Invariants for both KEMs: each `wrap` MUST be exactly 48 bytes
(`WRAP_LENGTH_MISMATCH` otherwise); `slots_mac` MUST be exactly 32 bytes; `nonce`
MUST be exactly 24 bytes (`NONCE_LENGTH_MISMATCH` otherwise); each `x25519` slot's
`epk` MUST be exactly 32 bytes (`KEM_EPK_LENGTH_MISMATCH` otherwise); each
`mlkem768x25519` slot's `kem_ct` MUST be exactly 1120 bytes
(`KEM_CT_LENGTH_MISMATCH` otherwise) and the slot MUST NOT carry an `epk` field;
`slots[]` MUST contain at least one entry. The `canonicalEncode` input to the
slots transcript and to the passphrase transcript MUST follow
[RFC 8949](https://www.rfc-editor.org/rfc/rfc8949) §4.2.1 plus the closed-map
rules of [`canonicalEncode`](#canonicalencode-deterministic-encoding-of-protocol-context-objects).
Implementations **MUST** zeroize `priv_epk_i`, `shared_i`, `KEK_i`, `CEK`,
`payload_key`, `HMAC_KEY`, and (on the passphrase path) `PW_MAC_KEY` on scope
exit where the language exposes mutable byte buffers, and SHOULD limit their
lifetime via local scope where byte sequences are immutable.

#### Recipient decryption (trial-decrypt)

A recipient holds one KEM private key (a 32-byte X25519 scalar for `x25519`, or a
32-byte X-Wing decapsulation seed for `mlkem768x25519`). They iterate `slots[]`
and trial-decrypt each slot; recipient public keys are **not** on the wire, so
the recipient discovers their slot by attempting to open it. The slot-set MAC
check is folded **into** the slot loop: a slot is accepted only when its candidate
CEK also reproduces the on-wire `slots_mac`.

Before any KEM or AEAD primitive is invoked, the verifier **MUST** run shape
checks (see
[Pre-decryption structural validation](#pre-decryption-structural-validation)):
`scheme == 1`, `aead` registered, `kem`
registered, `nonce` 24 bytes, `slots_mac` 32 bytes, `slots` non-empty, the
recipient secret 32 bytes, and each `slot.wrap` exactly 48 bytes; for `x25519`
each `epk` 32 bytes with no `kem_ct`; for `mlkem768x25519` each `kem_ct`
exactly 1120 bytes with no `epk`. The encapsulation material **MUST** be
distinct within one `slots[]`: for `x25519` all `epk` values **MUST** differ, for
`mlkem768x25519` all `kem_ct` values **MUST** differ; a duplicate is
rejected here, before any KEM or AEAD primitive, with `ENC_SLOTS_DUPLICATE_KEM_MATERIAL`.
Verifiers **MUST** bound parser resource use before invoking any primitive: the
reference bounds are `MAX_SLOTS = 1024` slots and `65536` bytes for the decoded
`enc` envelope, both far above the ~16 KiB Cardano transaction-metadata ceiling
that bounds honest records, so a record exceeding either bound is malformed and is
rejected here (`ENC_SLOTS_TOO_MANY` / `ENC_ENVELOPE_TOO_LARGE`). These are
verifier-enforced, deployment-pinned constants — not wire fields, and deployments
**MAY** tighten them. Under the reference values the two bounds overlap: more
than 1024 slots of either shape necessarily encodes past 65 536 bytes, so
`ENC_SLOTS_TOO_MANY` co-fires with `ENC_ENVELOPE_TOO_LARGE`; only a deployment
that raises the envelope byte bound can observe `ENC_SLOTS_TOO_MANY` alone.

```text
; hashes_hash, SLOTS_TRANSCRIPT, and slots_hash are recomputed once, before the
; loop, and held constant across it (see the Slot-set MAC step):
hashes_hash = SHA-256("cardano-poe-item-hashes-v1" || canonicalEncode(item.hashes))
slots_hash  = SHA-256("cardano-poe-slots-transcript-v1" || canonicalEncode(SLOTS_TRANSCRIPT))
if kem == "x25519": pub_R = x25519_publicKey(priv_R)      ; recipient public key, 32 B
else:               pub_R = XWing.publicKey(priv_R)       ; recipient X-Wing public key, 1216 B

found        = false
cek_conflict = false
selected_CEK = 0^32
for slot in envelope.slots:                ; iterate ALL slots — no early break
    kem_ok = true
    if kem == "x25519":
        shared    = x25519_sharedSecret(priv_R, slot.epk)
        kem_ok    = NOT constantTimeEqual(shared, 0^32)         ; explicit all-zero rejection, secret-independent
        kek_salt  = SHA-256("cardano-poe-x25519-kek-salt-v1" || envelope.nonce || slot.epk || pub_R)
        real_KEK  = HKDF-SHA-256(shared, salt=kek_salt, info="cardano-poe-kek-v1", L=32)
        dummy_KEK = HKDF-SHA-256(0^32,   salt=kek_salt, info="cardano-poe-kek-v1", L=32)
        KEK       = ct_select(kem_ok, real_KEK, dummy_KEK)      ; constant-time, no early exit
        ad_wrap   = "cardano-poe-kek-v1"
    else:                                   ; mlkem768x25519
        shared   = XWing.Decapsulate(sk=priv_R, ct=slot.kem_ct)   ; pinned API writes Decapsulate(ct, sk)
        kek_salt = SHA-256("cardano-poe-xwing-kek-salt-v1" || envelope.nonce || slot.kem_ct || pub_R)
        KEK      = HKDF-SHA-256(shared, salt=kek_salt,
                                info="cardano-poe-kek-mlkem768x25519-v1", L=32)
        ad_wrap  = "cardano-poe-kek-mlkem768x25519-v1"

    open_ok, candidate_CEK = ChaCha20-Poly1305_open_or_dummy(KEK, zeros(12), ad_wrap, slot.wrap)
    HMAC_KEY = HKDF-SHA-256(candidate_CEK, salt="", info="cardano-poe-slots-mac-v1", L=32)
    mac_ok   = constantTimeEqual(HMAC-SHA-256(HMAC_KEY, slots_hash), envelope.slots_mac)
    ok       = kem_ok AND open_ok AND mac_ok    ; per-slot acceptance: KEM, wrap, and MAC all fold in
    first        = ok AND NOT found                             ; first matching slot
    cek_conflict = cek_conflict OR (ok AND found AND NOT constantTimeEqual(candidate_CEK, selected_CEK))
    selected_CEK = ct_select(first, candidate_CEK, selected_CEK)   ; constant-time
    found        = found OR ok

if NOT found:    reject (single generic failure)
if cek_conflict: reject (single generic failure)
payload_key = HKDF-SHA-256(selected_CEK, salt=envelope.nonce, info="cardano-poe-payload-v1", L=32)
plaintext   = STREAM_open(payload_key, ciphertext)   ; per-chunk authenticated release
                                                     ; (see Content encryption)
if STREAM_open fails at any chunk: reject (single generic failure)
```

For `mlkem768x25519`, `pub_R` in `kek_salt` is the recipient's own 1216-byte
X-Wing public key, recomputed from the held decapsulation seed — the same value
the producer bound into the salt. The X25519 all-zero shared-secret rejection is
**explicit** here rather than relied upon transitively: a slot crafted to drive
the shared secret to `0^32` ([RFC 7748](https://www.rfc-editor.org/rfc/rfc7748)
§6.1) sets the secret-independent validity bit `kem_ok` to false, the KEK is
constant-time-selected to a dummy derived from `0^32` so the loop performs the
same work, and `kem_ok` is folded into `ok` — so an invalid-ECDH slot can never be
accepted regardless of the wrap or MAC outcome, and the record surfaces the single
generic failure if nothing else matches.

The wrap `open_or_dummy` primitive is **atomic**: on AEAD tag failure it returns
no plaintext, and the returned `candidate_CEK` is a fixed or pseudorandom dummy
that is independent of the failed ciphertext — no unverified plaintext is ever
released to the caller. `STREAM_open` releases each chunk's plaintext only after
that chunk's tag verifies; the tentative-output rule of
[Content encryption](#content-encryption) still applies to verified chunks until
the final plaintext-hash check passes.

The per-slot MAC fold is load-bearing. A malicious sender can construct a slot
that wrap-opens under a recipient's `priv_R` with an attacker-chosen CEK (no
`priv_R` knowledge required — standard encryption to the recipient's public key
suffices). Because a slot is accepted only when `kem_ok AND open_ok AND mac_ok`,
such a forged slot is inert: its attacker-chosen CEK does not reproduce
`slots_mac`, the slot is skipped exactly like a non-matching one, and an honest
slot anywhere later in the array still wins — the record decrypts under the
honest CEK. Requiring the candidate CEK to also produce the `slots_mac` over
`slots_hash` likewise defeats slot-substitution, slot-removal, and slot-reorder
attacks. Implementations **MUST NOT** accept a slot on wrap-open success alone
and **MUST NOT** skip the `slots_mac` verification.

**Multiple matching slots: duplication is permitted, a CEK conflict is not.** A
recipient's private key **MAY** legitimately match more than one slot: a producer
may seal the same CEK to the same recipient in several slots to pad the recipient
count, a valid privacy technique. The verifier selects the **first** match's CEK
and **MUST NOT** reject merely because more than one slot matched. This is
distinct from the within-record duplicate-encapsulation-material rejection
(`ENC_SLOTS_DUPLICATE_KEM_MATERIAL`; see [Slot construction](#slot-construction-sender)):
that rule fires on a repeated `epk` / `kem_ct`, whereas honest
duplication still draws **fresh** per-slot KEM randomness for each appearance, so
its `epk` / `kem_ct` differ and it never collides with that check. The narrow
anomaly the verifier **MUST** reject is two matching slots that recover
**different** CEKs (compared in constant time): the loop tracks a `cek_conflict`
bit across all slots and surfaces the single generic failure if any further match
recovers a CEK that differs from the selected one. This is defence-in-depth: under
the [Slot-set commitment assumption](#slot-set-commitment-assumption) a
distinct-CEK match is already infeasible — it is exactly the multi-key collision
that assumption rules out — and the check fails closed against a broken
implementation or a future weakening of that assumption.

**Single generic error to untrusted callers.** An untrusted caller **MUST**
receive exactly one generic failure **shape** regardless of why decryption failed
— no slot opened, the slot set was tampered, or the content stream failed to
open — and the
**response** **MUST NOT** distinguish these, nor reveal which slot matched. An
implementation **MAY** surface internal typed codes (`WRONG_RECIPIENT_KEY` /
`TAMPERED_HEADER` / `TAMPERED_CIPHERTEXT`; defined in **Decryption outcomes**
below) to a trusted local caller for diagnostics, but those codes **MUST NOT** leak
to an external observer through a distinguishable response. On timing: the verifier
**MAY** return at the no-match check (`if NOT found`) before content decryption.
This reveals only **recipient-vs-non-recipient**, never which slot matched and no
key material. Uniform timing between the non-recipient case and a recipient whose
ciphertext fails to open is **NOT** required, and a dummy content open **MUST NOT**
be mandated — it would impose content-decryption cost on every non-recipient. The
constant-time guarantee that does hold is the across-slots invariant of the next
paragraph, which hides which slot, if any, a given key unwraps.

**Constant-time-across-slots requirement.** Within a single private key's pass,
the trial-decrypt loop **MUST** run over **all** slots regardless of an early
match — i.e. a constant number of slot operations per private key — so a
network-level observer cannot infer which slot index matched. A recipient who has
multiple private keys (e.g. archived keys across an identity rotation) iterates
private-key × slot; the per-private-key constant-time-N invariant holds for each
key. The loop **MAY** short-circuit across private keys (variable time leaks only
the weak "which key matched" signal, a documented trade-off), but **MUST** remain
constant-time across the slots of any single key. Both KEMs bind the recipient's
own public key into the per-slot KEK salt, so when iterating multiple keys that
binding **MUST** be re-derived per key from the current private key — the
`pub_R` term inside the salt digest
`SHA-256(label || enc.nonce || <epk | kem_ct> || pub_R)` under either KEM.
Reusing a single `pub_R` across keys computes the wrong KEK for every key but
one under either KEM.

**Decryption outcomes** (typed; internal — surfaced only as the single generic
failure to untrusted callers): no slot opens under `priv_R` (trial-decrypt
exhausted) → `WRONG_RECIPIENT_KEY`; a slot opens but no candidate CEK reproduces
the `slots_mac` over `slots_hash` (a slot, a header field, the item's `hashes`
map, or `slots_mac` itself was tampered) → `TAMPERED_HEADER`; the STREAM open
fails after a CEK is recovered and the MAC verified (a chunk tag fails, the
stream is truncated, data follows the final chunk, or the chunk layout is
otherwise violated) → `TAMPERED_CIPHERTEXT`. These three codes are in
[`../registries/error-codes.json`](https://github.com/cardanowall/label-309/blob/main/registries/error-codes.json); a conformant
implementation maps all three to one generic external failure that an untrusted
caller cannot distinguish by response shape. Timing follows variant (b) above: a
permitted early no-match return separates `WRONG_RECIPIENT_KEY` (non-recipient)
from the two recipient-side tamper outcomes, which carry no further distinction.

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
recipient **MUST** refuse to act on the plaintext. For a verifier this outcome
is a **`failed`** verdict (integrity class), surfaced as
`URI_INTEGRITY_MISMATCH`: a record whose decryption succeeds but whose
plaintext-hash recheck fails **MUST NOT** be reported with a `valid` — or any
"decrypted" — top-level verdict. For a streaming consumer this
check is the point at which tentatively released chunk plaintext becomes final
(see [Content encryption](#content-encryption)). The structural validator
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

The alternative key-delivery path replaces recipient slots with a passphrase.
The producer derives the CEK directly from a normalised passphrase; there is no
ephemeral keypair, no `epk`, no per-slot wrap, no trial-decrypt loop, and no
on-chain `slots_mac`. The key commitment that `slots_mac` provides on the slots
path lives instead in a 32-byte header **inside the ciphertext blob**, prepended
before the STREAM chunks — same object, same URI, same fetch.

```text
passphrase_bytes = utf8(normalize(passphrase))   ; cardano-poe-pw-norm-v1 (see below)
CEK = argon2id(passphrase_bytes,
               salt   = enc.passphrase.salt,
               params = enc.passphrase.params,
               L      = 32)

hashes_hash = SHA-256("cardano-poe-item-hashes-v1" || canonicalEncode(item.hashes))

PASSPHRASE_TRANSCRIPT = {                        ; closed map; keys are a set, not an order
    "scheme":      1,                            ; uint
    "path":        "passphrase",                 ; text
    "aead":        <enc.aead>,                   ; text: the content-format identifier
    "nonce":       <enc.nonce>,                  ; bytes(24)
    "hashes_hash": hashes_hash,                  ; bytes(32), over this item's hashes
    "passphrase": {                              ; closed map
        "alg":           "argon2id",             ; text
        "salt":          enc.passphrase.salt,    ; bytes
        "params":        { "m": m, "t": t, "p": p },   ; closed map of uints
        "normalization": "cardano-poe-pw-norm-v1"      ; scheme-fixed constant, NOT on the wire
    }
}
pw_hash    = SHA-256("cardano-poe-passphrase-transcript-v1" || canonicalEncode(PASSPHRASE_TRANSCRIPT))
PW_MAC_KEY = HKDF-SHA-256(ikm=CEK, salt="", info="cardano-poe-passphrase-mac-v1", L=32)
commitment = HMAC-SHA-256(key=PW_MAC_KEY, msg=pw_hash)    ; 32 bytes

ciphertext blob = commitment || STREAM chunks
payload_key     = HKDF-SHA-256(ikm=CEK, salt=enc.nonce,
                               info="cardano-poe-payload-passphrase-v1", L=32)
```

`PASSPHRASE_TRANSCRIPT` is a closed map carrying exactly the six-key set above,
with `passphrase` itself a closed sub-map; it is serialised by `canonicalEncode`
(see [`canonicalEncode`: deterministic encoding of protocol context
objects](#canonicalencode-deterministic-encoding-of-protocol-context-objects)).
The transcript binds the passphrase-KDF parameters, the header fields, and the
item's hash claim into the commitment: the verifier recomputes the transcript
from the received `enc` map and the item's `hashes`, so tampering with `salt`,
any `params` value, `nonce`, `aead`, or splicing the envelope onto a different
hash claim yields a different `pw_hash` and the commitment check fails. The
content itself is then encrypted in the same segmented STREAM format as the
slots path, under the passphrase-path `payload_key` (see
[Content encryption](#content-encryption)).

The `"normalization"` value is a **scheme-fixed constant** fed into the
transcript to pin the exact normalization profile the CEK was derived under; it
is **never** serialised on the wire (it is not part of the `enc.passphrase` map
a producer emits).

**Verification order.** The verifier derives the candidate CEK from the entered
passphrase, reads the leading 32 bytes of the ciphertext blob, recomputes the
commitment, and compares **in constant time** — all **before** opening any
STREAM chunk. A passphrase-path blob shorter than 48 bytes — the 32-byte
commitment header plus the 16-byte minimum STREAM (the lone tag of an empty
final chunk) — cannot be well-formed and is malformed ciphertext
(`TAMPERED_CIPHERTEXT`). On mismatch — wrong passphrase, tampered parameters,
tampered header, or a spliced envelope — it **MUST** surface the same single
generic failure as any other decryption failure and **MUST NOT** begin
streaming. A
wrong passphrase is therefore indistinguishable from a tampered record, while
the commitment (not merely a Poly1305 tag deep in the stream) is what a correct
passphrase must reproduce.

**Why the commitment is off-chain.** The commitment is deliberately **not** an
on-chain field. The Cardano metadata is public and permanent; an on-chain
passphrase commitment would hand every observer a free offline test oracle —
derive a candidate CEK from a guessed passphrase, check it against the chain —
for every passphrase record, forever, **including records whose ciphertext is
withheld** (never published, or shared only through a private channel). Placing
the commitment inside the ciphertext blob means testing a guess requires the
blob itself: a withheld-ciphertext record exposes no passphrase-guessable
material on the permanent ledger. The passphrase path is not discovered by a
key-scan over chain data, so reading a 32-byte header before testing a
passphrase costs a legitimate recipient nothing.

The `enc.passphrase.salt` **MUST** be freshly drawn from a CSPRNG for every
record (see [Forbidden patterns](#forbidden-patterns)): the salt is the sole
cross-record separator for a reused passphrase — a fixed or derived salt makes
equal passphrases yield equal CEKs across records.

##### Passphrase normalization profile

The normalization applied to the passphrase before Argon2id is the fixed profile
`cardano-poe-pw-norm-v1`. It is normative: two implementations **MUST** derive a
byte-identical CEK from the same passphrase, and the only way to guarantee that is
a pinned normalization. The profile, applied in order, is:

1. **Reject unassigned codepoints.** A passphrase containing any codepoint that
   is **unassigned in Unicode 16.0** is rejected with
   `ENC_PASSPHRASE_UNNORMALIZABLE` before any normalization step runs.
2. **NFKC.** Apply Normalization Form KC per [UAX #15](https://www.unicode.org/reports/tr15/) under **Unicode 16.0**.
3. **Whitespace.** Define "whitespace" as every character carrying the Unicode `White_Space` property under **Unicode 16.0**. Collapse every maximal run of such characters to a single U+0020 SPACE.
4. **Trim.** Remove leading and trailing whitespace (a leading or trailing collapsed U+0020).
5. **Reject empty.** If the result is the empty string, reject with
   `ENC_PASSPHRASE_EMPTY`: a whitespace-only or otherwise vacuous passphrase
   normalizes to zero bytes, which Argon2id would silently accept — keying the
   record to a CEK any party can derive.
6. **Encode.** Encode the result as UTF-8; those bytes are the Argon2id password input.

Step 1 is what makes the profile deterministic across implementations and
across time. The
[Unicode Normalization Stability Policy](https://www.unicode.org/policies/stability_policy.html)
guarantees that the normalization of a string is stable across future Unicode
versions only when every codepoint in it is **assigned** in the version where
it was normalized; an unassigned codepoint may acquire a decomposition later
and silently change the derived CEK. Rejecting unassigned codepoints closes
that hole entirely, and is invisible to honest users — every character in
actual written use is assigned.

Before normalization and Argon2id, an implementation **MUST** bound the raw
passphrase input length so an oversized passphrase cannot drive a pre-KDF
denial-of-service: the reference bound is `MAX_PASSPHRASE_INPUT_BYTES = 4096`
UTF-8 bytes of raw input, rejected before any normalization or hashing work.
Like the `MAX_SLOTS` and
decoded-`enc`-envelope bounds (see [Sealed PoE: multi-recipient
encryption](#sealed-poe-multi-recipient-encryption)), this is a verifier-enforced,
deployment-pinned constant — not a wire field — and deployments **MAY** tighten it.

The Unicode version is pinned at **Unicode 16.0** literally and **MUST NOT** float:
the `White_Space` property set, the assigned-codepoint set, and the NFKC mapping
tables are all version-dependent, and a verifier resolving the profile against a
different Unicode version could derive a different CEK from the same passphrase
and fail to decrypt an honest record. Implementations **MUST** therefore resolve
the profile against pinned Unicode 16.0 data (an embedded NFKC mapping,
assigned-codepoint set, and `White_Space` table — or a normalization library
pinned to exactly that version), **never** against whatever Unicode version the
platform's runtime happens to ship. A future revision that adopts a newer
Unicode version does so under a new profile identifier, not by re-interpreting
`cardano-poe-pw-norm-v1`.

The `enc.passphrase` map is `{ alg, salt, params }`. The sole registered KDF is
`argon2id` (see [`../registries/kdf-algorithms.json`](https://github.com/cardanowall/label-309/blob/main/registries/kdf-algorithms.json));
an unregistered `alg` → `ENC_PASSPHRASE_ALG_UNSUPPORTED`. The Argon2 version is
pinned at **`0x13` (19)** per [RFC 9106](https://www.rfc-editor.org/rfc/rfc9106);
there is no version field on the wire, and no other Argon2 version is admissible
under `enc.scheme: 1`. The validator enforces:

- `salt` length 16–64 bytes inclusive (`ENC_PASSPHRASE_SALT_TOO_SHORT` /
  `ENC_PASSPHRASE_SALT_TOO_LONG`).
- `params` is a **closed** map of exactly `{ m, t, p }` — an unknown sub-field is
  rejected (`SCHEMA_UNKNOWN_FIELD`) — with `m ≥ 65 536` (KiB ≈ 64 MiB), `t ≥ 3`,
  `p ≥ 1`; any floor violation → `ENC_PASSPHRASE_ARGON2_PARAMS_TOO_LOW`. Each
  value is a uint in the pinned wire range `0 .. 2^32 − 1` (a value above it →
  `SCHEMA_TYPE_MISMATCH`); see the integer-range rule in
  [CDDL grammar and JSON Schemas](#cddl-grammar-and-json-schemas). The
  output length is fixed at 32 bytes and is not carried in `params`.

Implementations **SHOULD** also enforce **upper** bounds against verifier-side DoS,
reporting `ENC_PASSPHRASE_PARAMS_EXCEED_POLICY`; such ceilings are non-normative
(hardware-dependent) and **MUST NOT** be conflated with the floor code.

> **Security trade-off (informative).** `salt` and `params` are public on chain
> in perpetuity, and once the ciphertext blob is obtained an attacker has
> unlimited offline time to brute-force the passphrase against the published
> parameters — the in-ciphertext commitment gates guessing on possession of the
> blob, not on any online party. Passphrase entropy is the only barrier.
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
Arweave). That check is the verifier's
[content-address binding](#content-address-binding-of-fetched-bytes), and it
also decides attribution: a decryption-layer failure over fetched ciphertext
counts against the record only when the binding was verified — unattributable
bytes indict the gateway instead. The stored object is the ciphertext blob exactly as defined in
[Content encryption](#content-encryption): the STREAM chunk sequence, preceded
on the passphrase path by the 32-byte commitment header — the URI therefore
commits to the header together with the chunks. `uris[]` MAY be absent even when
`enc` is present (out-of-band ciphertext delivery), in which case the verifier
acquires the ciphertext from local input.

#### Forbidden patterns

- **MUST NOT** reuse a per-slot ephemeral across slots or records: a fresh X25519
  ephemeral per `x25519` slot, a fresh X-Wing encapsulation per `mlkem768x25519`
  slot. The zero-nonce wrap relies on per-slot KEK uniqueness.
- **MUST NOT** reuse a CEK across envelopes — a fresh CSPRNG CEK per
  `enc`-bearing item, within a record and across records alike. The CEK is the
  one secret an envelope delivers: reusing it grants every recipient of one
  envelope the decryption capability for the other regardless of its slot
  list, and links the sealed items to anyone holding either.
- **MUST** generate a fresh CSPRNG `enc.passphrase.salt` for every passphrase
  envelope — never a fixed, derived, or all-zero salt. The pinned conformance
  vectors carry recorded salts for byte-exact reproducibility; they are
  fixtures, not a sanction for salt reuse.
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
- **MUST NOT** log `CEK`, `KEK_i`, `HMAC_KEY`, `PW_MAC_KEY`, `payload_key`,
  `shared_i`, `priv_epk_i`, `priv_R`, or the passphrase at any level; zeroize or
  scope-limit these secrets.
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
the `x25519` recipient uses HRP `age` (visible prefix `age1…`, 32-byte X25519
public key) with secret-key HRP `AGE-SECRET-KEY-`; the `mlkem768x25519` recipient
uses HRP `age1pqc` (visible prefix `age1pqc1…`,
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

Conformance vectors for the sealed-PoE construction are under
[`../conformance/sealed-poe/`](https://github.com/cardanowall/label-309/blob/main/conformance/sealed-poe). They are produced from
deterministic inputs (every normally-random value — CEK, `enc.nonce`, per-slot
X25519 ephemerals, X-Wing encapsulation randomness, passphrase salt, shuffle
permutation — pinned to recorded test seeds) and derived from one shared
reference `canonicalEncode` so the transcript bytes are byte-identical across
implementations. The vector set **MUST** include:

- **positive:** `x25519` and `mlkem768x25519` single- and multi-recipient,
  mixed-N, multi-private-key iteration, and the passphrase path (commitment
  header plus STREAM chunks in one blob);
- **positive — STREAM layout:** an empty plaintext (exactly one zero-length
  final chunk), a single-chunk payload, and a multi-chunk payload crossing the
  65536-byte boundary;
- vectors pinning both KEK salts,
  `SHA-256("cardano-poe-x25519-kek-salt-v1" || enc.nonce || epk || pub_R)` and
  `SHA-256("cardano-poe-xwing-kek-salt-v1" || enc.nonce || kem_ct || pub_R)`;
- a vector pinning `hashes_hash` and its position in both transcripts;
- **positive — forged shadow slot:** a slot that wrap-opens under the
  recipient's key with an attacker-chosen CEK, placed **before** an honest
  slot; the record **MUST** decrypt under the honest CEK (the per-slot MAC fold
  skips the forgery);
- **positive — recipient/CEK duplication:** the same CEK sealed to the same
  recipient in two slots (each with fresh per-slot KEM material); it **MUST**
  decrypt, exercising that multiple matches are not rejected;
- **negative — header binding:** flip `kem`, `aead`, or `scheme` while leaving
  the slot shapes structurally valid; the record **MUST** fail (the acceptance
  test for transcript header-binding);
- **negative — hashes splice:** an honest envelope paired with an item whose
  `hashes` map differs from the one it was sealed for; the on-chain MAC match
  (or the passphrase commitment) **MUST** fail;
- **negative — cross-path confusion:** a record shaped to look cross-path; it
  **MUST** fail;
- **negative — passphrase commitment:** a wrong passphrase, a tampered `salt`
  or `params`, and a tampered commitment header; each **MUST** fail with the
  single generic failure before any STREAM chunk is opened;
- **negative — passphrase normalization:** a passphrase containing a codepoint
  unassigned in Unicode 16.0 (`ENC_PASSPHRASE_UNNORMALIZABLE`), and a
  whitespace-only passphrase that normalizes to the empty string
  (`ENC_PASSPHRASE_EMPTY`);
- **negative — all-zero X25519 shared secret:** a slot crafted to yield an
  all-zero shared secret; the slot **MUST** be treated as failed;
- **negative — within-record duplicate slot:** two slots sharing an `epk` (or
  `kem_ct`); it **MUST** be rejected with
  `ENC_SLOTS_DUPLICATE_KEM_MATERIAL`;
- **negative — STREAM tampering:** a flipped chunk tag, a truncated stream
  (missing final chunk), trailing data after the final chunk, and a non-final
  chunk shorter than 65536 bytes; each **MUST** fail;
- **negative — CEK conflict:** two slots that both match one recipient and both
  satisfy `slots_mac` yet recover **distinct** CEKs **MUST** be rejected. No
  byte vector can pin this case — constructing one would require a collision in
  the CEK-keyed commitment, exactly the multi-key collision the
  [Slot-set commitment assumption](#slot-set-commitment-assumption) rules out —
  so the property is asserted by implementation-level behavioural tests, like
  the constant-time properties below;
- the standard tamper negatives (`slots_mac` flip, wrap flip), regenerated
  against `slots_hash`.

Constant-time behaviour and the single-generic-error property are not fully
expressible as byte vectors; implementations assert them with timing/structure
tests alongside the byte-pinned vectors.

### Algorithm registries and conformance profiles

This CIP references every cryptographic algorithm by a **named string identifier** drawn from one of six registries. An identifier is a stable, opaque token (for example `sha2-256`, `chacha20-poly1305-stream64k`, `mlkem768x25519`); each token is bound to exactly one algorithm with a stable public reference (an RFC, a FIPS publication, a CIP, an IANA codepoint, or a named internet-draft). This named-identifier ↔ stable-public-reference model is what makes the standard algorithm-agile: a verifier that does not recognise an identifier disposes of it with a typed code — a typed rejection where the identifier is load-bearing for the record's commitments (content hash, passphrase KDF), a typed degradation tag where it is not (an unrecognised sealed-envelope identifier in the public reading, an unrecognised signature or list-commitment identifier; see [Structural validation, verifier roles, and error codes](#structural-validation-verifier-roles-and-error-codes)) — it MUST NOT crash and MUST NOT silently accept.

The identifier strings in this section are normative. Conformant implementations **MUST** encode them on-wire byte-for-byte as written.

The normative machine-readable form of every registry lives under [`../registries/`](https://github.com/cardanowall/label-309/blob/main/registries):

| Registry                          | File                                                                                                 | Wire role                              |
| --------------------------------- | ---------------------------------------------------------------------------------------------------- | -------------------------------------- |
| Hash algorithms                   | [`../registries/hash-algorithms.json`](https://github.com/cardanowall/label-309/blob/main/registries/hash-algorithms.json)                           | `items[i].hashes` map keys             |
| Merkle list-commitment algorithms | [`../registries/merkle-commitment-algorithms.json`](https://github.com/cardanowall/label-309/blob/main/registries/merkle-commitment-algorithms.json) | `merkle[i].alg`                        |
| AEAD algorithms                   | [`../registries/aead-algorithms.json`](https://github.com/cardanowall/label-309/blob/main/registries/aead-algorithms.json)                           | `enc.aead`                             |
| KEM algorithms                    | [`../registries/kem-algorithms.json`](https://github.com/cardanowall/label-309/blob/main/registries/kem-algorithms.json)                             | `enc.kem`                              |
| KDF algorithms                    | [`../registries/kdf-algorithms.json`](https://github.com/cardanowall/label-309/blob/main/registries/kdf-algorithms.json)                             | `enc.passphrase.alg`                   |
| Signature algorithms              | [`../registries/signature-algorithms.json`](https://github.com/cardanowall/label-309/blob/main/registries/signature-algorithms.json)                 | `COSE_Sign1` protected `alg`           |
| Error codes                       | [`../registries/error-codes.json`](https://github.com/cardanowall/label-309/blob/main/registries/error-codes.json)                                   | structural-validator / verifier output |

Where this prose and the registry JSON differ, the registry JSON is authoritative for the identifier set, the pinned length constants, and the typed error code emitted on each failure mode.

#### Identifier-carriage forms

This CIP carries algorithm identifiers in three on-wire shapes, selected by the structural needs of each registry:

1. **Direct value** — `<role>: "<alg-id>"` — for identifiers that carry no algorithm-specific parameters (e.g. `enc.aead: "chacha20-poly1305-stream64k"`, `enc.kem: "x25519"`).
2. **`alg`-field map** — `<role>: {"alg": "<id>", ...parameters}` — for identifiers that require algorithm-specific parameters (e.g. `merkle[i] = {"alg": "rfc9162-sha256", "root": ..., "leaf_count": ..., ...}`, `enc.passphrase = {"alg": "argon2id", "salt": ..., "params": ...}`).
3. **Map-key form** — `{<alg-id>: <value>}` — for identifiers used as CBOR map keys, which inherits RFC 8949 §3.1 duplicate-key uniqueness and §4.2.1 deterministic ordering (e.g. `items[i].hashes = {"sha2-256": <digest>, "blake2b-256": <digest>}`).

The three forms minimise wire bytes for each role: a single-token identifier is a bare string; a parameterised identifier lives in a structured map; map-key identifiers exploit CBOR's native uniqueness semantics. The inconsistency is byte-justified, not stylistic.

#### Conformance profiles

This CIP (v1) defines four **conformance profiles** so that an implementation can advertise the subset of the standard it supports without having to implement every cryptographic primitive in the registry. A consumer (verifier, indexer, explorer plug-in, archival tool) is conformant if it correctly handles every record that uses **only** algorithms in its declared profile, and cleanly rejects records that require a higher profile with the appropriate `UNSUPPORTED_*` code.

| Profile                | Reads (what records this profile can process)                                                                                                                                                                                                                                  | Implementation surface (algorithms a verifier must implement)                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| ---------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **`core`**             | Hash-only PoE records — `items[i].hashes`, optional `uris`, optional top-level `merkle[]`, optional `supersedes`, no `enc`, no `sigs`.                                                                                                                                         | SHA-256, BLAKE2b-256, canonical CBOR (RFC 8949 §4.2.1), the Cardano metadata fetch / decode path, and the offline multibase / multihash CID parser. The `rfc9162-sha256` list-commitment identifier is **OPT-INFO** within `core`: a verifier MAY implement RFC 9162 §2.1.1 Merkle-fold + per-leaf inclusion-proof verification. A verifier that does not implement Merkle-fold reports each `merkle[i]` commitment as `MERKLE_UNSUPPORTED` (info-severity) and verifies the record's `items[i].hashes` content claim normally. |
| **`signed`**           | Everything `core` reads, plus records carrying record-level `sigs[]` (each entry a closed `{cose_sign1, cose_key?}` map; see [Record-level signatures (COSE_Sign1)](#record-level-signatures-cose_sign1)).                                                                     | All of `core`, plus strict non-cofactored Ed25519 (RFC 8032 §5.1.7), COSE_Sign1 (RFC 9052), and HMAC-SHA-256 / HKDF-SHA-256 where the spec requires them outside the `enc` envelope.                                                                                                                                                                                                                                                                                                                                            |
| **`sealed`**           | Everything `signed` reads, plus records carrying `enc` (sealed multi-recipient or passphrase). A `sealed` verifier is **public-verifier**-conformant: it parses the envelope, enforces the length checks, and verifies any `sigs[]` over the record body. It does NOT decrypt. | All of `signed`, plus **registered-identifier and length constants only** (no new crypto primitives): the `enc.nonce` length (24 B for `chacha20-poly1305-stream64k`), the per-KEM slot-shape length constants (`x25519` — 32 B `epk`; `mlkem768x25519` — 1120 B `kem_ct`), the per-slot `wrap` length (48 B), the `slots_mac` length (32 B), and the KDF identifier `argon2id`. A `sealed`-profile verifier never invokes X25519, ML-KEM, HKDF, or any AEAD primitive.                                                         |
| **`recipient-sealed`** | Everything `sealed` reads, **and** decrypts records when given the recipient's KEM private key (an X25519 private key for `x25519` slots, an X-Wing decapsulation seed for `mlkem768x25519` slots).                                                                            | All of `sealed`, plus the full sealed-PoE decrypt path for both KEMs and the post-decryption plaintext-hash recomputation (see [Sealed PoE: multi-recipient encryption](#sealed-poe-multi-recipient-encryption)).                                                                                                                                                                                                                                                                                                               |

Profiles are **strict supersets**: `recipient-sealed` ⊃ `sealed` ⊃ `signed` ⊃ `core`. Every conformant implementation MUST declare its profile; third-party reviewers can then audit conformance against a defined subset rather than the full surface. A producer MAY emit records targeting any profile; the producer's own profile is the lowest profile a verifier must implement to read its output. Hash-only PoE records — the simplest and most adoptable case — require only the `core` profile, so a third-party `core`-only verifier is a meaningful interop target.

The structural validator and the verifier profile are orthogonal. The structural validator parses the full v1 schema regardless of profile — it MUST recognise `enc`, `sigs`, `COSE_Sign1` shapes, KDF parameter maps, and every registry identifier well enough to emit the typed `UNSUPPORTED_*`/`SCHEMA_*`/`MALFORMED_*` codes. The structural validator answers "is this a well-formed v1 record?"; the profile answers "can this verifier verify this record end-to-end?".

#### Identifier-level conformance levels

Inside a given profile, every algorithm identifier carries one of these normative statuses:

- **MANDATORY-to-implement (M).** A conformant verifier in the relevant profile **MUST** be able to consume records carrying this identifier (parse, validate length constraints, perform the corresponding cryptographic operation when the rest of the record permits).
- **OPTIONAL-to-produce (O).** A v1 producer **MAY** emit this identifier; the verifier-side capability is still mandatory.
- **OPTIONAL-on-both-sides (OPT).** A v1 producer **MAY** emit this identifier and a verifier **MAY** implement it. A verifier that does not implement it **MUST** reject records carrying it with the corresponding `UNSUPPORTED_*` code, rather than silently downgrading or skipping.
- **OPTIONAL-with-info-on-skip (OPT-INFO).** A verifier that does **not** implement an OPT-INFO identifier surfaces the affected record element as an **info-severity** entry (e.g. `MERKLE_UNSUPPORTED`, `SIGNATURE_UNSUPPORTED`) and **continues** validating the rest of the record. This differs from OPT: an unimplemented OPT identifier rejects the record, whereas an unimplemented OPT-INFO identifier is skipped without invalidating the record. The OPT-INFO tier is reserved for identifiers whose presence does not invalidate other commitments in the record.

  **Severity escalation.** When an OPT-INFO identifier represents the record's **only** content commitment (e.g. a merkle-only record where the verifier does not implement Merkle-fold), the info-severity entry MUST escalate to `error` severity and the record-level verdict MUST be `failed`. A verifier that emits `valid` has, by construction, verified at least one content commitment.

- **Reserved (R).** Identifier is reserved for future revisions; no v1 producer emits it. v1 verifiers reject hash and KDF Reserved identifiers as the corresponding `UNSUPPORTED_*` code (these primitives are load-bearing for the content claim and for key derivation). AEAD and KEM Reserved identifiers follow the unknown-envelope rule of [Structural validation, verifier roles, and error codes](#structural-validation-verifier-roles-and-error-codes): in the default public reading the envelope becomes opaque and the item is tagged `ENC_UNSUPPORTED` while the content-hash claim still validates; the recipient verifier and strict sealed-crypto mode reject hard with the specific `UNSUPPORTED_*` code. Signature-algorithm Reserved identifiers are tagged: a `sigs[i]` carrying a Reserved `alg` is reported as `SIGNATURE_UNSUPPORTED` (informational) and does not by itself invalidate the record.

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

An empty tree (`n == 0`) is **forbidden**; producers **MUST NOT** create records under this identifier with an empty leaf list. The `merkle[i].leaf_count` field (REQUIRED) lets a structural validator detect `leaf_count == 0` directly, rejecting it as `SCHEMA_MERKLE_LEAF_COUNT_INVALID` with no off-chain bytes needed; it is also compared against the fetched leaves-list's `leaf_count`, emitting `SCHEMA_MERKLE_LEAF_COUNT_MISMATCH` on disagreement. Each `d_i` is a 32-byte sequence; the typical use places `d_i = SHA-256(content_i)`, but the construction is agnostic to leaf provenance — each leaf MUST be exactly 32 bytes.

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

The `enc.aead` field carries the **content-format identifier only** — the symmetric construction that encrypts the plaintext under the content `payload_key`. KEM identifiers live in the KEM registry below (`enc.kem`); the two fields are orthogonal, and the content format is KEM-independent. The per-slot CEK-wrap construction (`chacha20-poly1305` with a fixed zero nonce; see [Sealed PoE: multi-recipient encryption](#sealed-poe-multi-recipient-encryption)) is **not** wire-selectable and is deliberately absent from this registry.

| Identifier                    | Algorithm                                                                                                                                                                                                                                                                                                                                                                | Key  | Per-chunk nonce       | Tag          | Status                                                                                                                                                                                  |
| ----------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---- | --------------------- | ------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `chacha20-poly1305-stream64k` | ChaCha20-Poly1305 ([RFC 8439](https://www.rfc-editor.org/rfc/rfc8439)) in the 64 KiB segmented STREAM layout of [age v1](https://github.com/C2SP/C2SP/blob/main/age.md): 65536 plaintext bytes per non-final chunk, per-chunk nonce `uint88_be(counter) ‖ final_flag`, empty per-chunk AAD; the 24-byte `enc.nonce` is the envelope-unique salt of the `payload_key` HKDF. | 32 B | 12 B (counter ‖ flag) | 16 B / chunk | **M.** The sole MANDATORY-to-implement content format for `enc.scheme: 1`; producers **MUST** emit this identifier.                                                                     |
| `aes-256-gcm`                 | (reserved) AES-256-GCM ([NIST SP 800-38D](https://csrc.nist.gov/pubs/sp/800/38/d/final), [RFC 5116](https://www.rfc-editor.org/rfc/rfc5116))                                                                                                                                                                                                                             | —    | —                     | —            | **R.** Reserved for a future `enc.scheme` profile targeting RFC-only AEAD constraints. Not part of `enc.scheme: 1`; a record using it follows the unknown-envelope rule (`ENC_UNSUPPORTED` in the public reading; `UNSUPPORTED_AEAD_ALG` in the strict reading). |

The AEAD (authenticated-encryption) property is mandatory: unauthenticated ciphers (e.g. AES-CBC without a MAC, AES-CTR, raw ChaCha20) **MUST NOT** be used and **MUST** be rejected with `UNAUTHENTICATED_CIPHER_FORBIDDEN`. The on-wire spelling is exactly `chacha20-poly1305-stream64k`; alternative spellings **MUST NOT** be produced. The `enc.nonce` length MUST equal the registered `enc.nonce` length of the content format (24 bytes for `chacha20-poly1305-stream64k`); a mismatch emits `NONCE_LENGTH_MISMATCH`.

The segmented layout exists so a verifier can authenticate and release large payloads incrementally with bounded memory; the per-chunk counter nonces are safe because `payload_key` is single-use — an HKDF leaf of a fresh CEK salted by the envelope-unique `enc.nonce` — so stateless producers never coordinate nonces across envelopes. A future requirement for a different content format (e.g. an RFC-only AEAD) MUST be handled as a new sealed-PoE construction version (`enc.scheme: 2`); `enc.scheme: 1` records always mean the construction pinned in the conformance vectors.

#### KEM identifiers (`enc.kem`)

Both KEMs below are registered under `enc.scheme: 1` from the first release. `enc.kem` selects the per-slot KEM, the per-slot encapsulation shape, and the per-slot KEK derivation. The slot-set MAC, content AEAD, slot shuffle, and constant-time trial-decrypt are KEM-independent.

| Identifier       | Algorithm                                                                                                                                                                                                                                                                                                                                               | Public (encapsulation) key                                            | Ciphertext                                                                                         | Shared secret | Status                                                                                   |
| ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------- | ------------- | ---------------------------------------------------------------------------------------- |
| `x25519`         | X25519 ECDH ([RFC 7748](https://www.rfc-editor.org/rfc/rfc7748))                                                                                                                                                                                                                                                                                        | 32 B                                                                  | 32 B (the per-slot ephemeral public key carried as `slot.epk`)                                     | 32 B          | **M.** Classical; every conformant verifier MUST support it. Producer-side, NOT RECOMMENDED where confidentiality must outlive the elliptic-curve era (see [Harvest-now, decrypt-later and the `x25519` KEM](#harvest-now-decrypt-later-and-the-x25519-kem)). |
| `mlkem768x25519` | X-Wing hybrid KEM ([draft-connolly-cfrg-xwing-kem-10](https://datatracker.ietf.org/doc/draft-connolly-cfrg-xwing-kem/10/)): ML-KEM-768 ([FIPS 203](https://csrc.nist.gov/pubs/fips/203/final)) ⊕ X25519 ([RFC 7748](https://www.rfc-editor.org/rfc/rfc7748)), combined with a SHA3-256 combiner ([FIPS 202](https://csrc.nist.gov/pubs/fips/202/final)) | 1216 B (ML-KEM-768 encapsulation key 1184 B ‖ X25519 public key 32 B) | 1120 B (ML-KEM-768 ciphertext 1088 B ‖ X25519 ephemeral public key 32 B), carried as `slot.kem_ct` | 32 B          | **M.** Post-quantum hybrid; the RECOMMENDED producer default.                            |

`mlkem768x25519` is the X-Wing KEM. The shared secrets are combined by `SHA3-256(ss_MLKEM ‖ ss_X25519 ‖ ct_X25519 ‖ pk_X25519 ‖ label)`, where `label` is the six bytes `0x5c 0x2e 0x2f 0x2f 0x5e 0x5c`. The decapsulation key is a 32-byte seed (implicit-rejection KEM); the public key is derived from it. X-Wing is used here as a **black-box** KEM: the sealed-PoE construction consumes only its public interface (encapsulate, decapsulate, the 32-byte shared secret) and makes no assumption about the combiner's internal hashing. Recipient, slot, and record binding are provided **outside** the KEM by the labelled-hash KEK salt, `SHA-256("cardano-poe-xwing-kek-salt-v1" ‖ enc.nonce ‖ kem_ct ‖ pub_R)`, computed over the slot's own wire bytes — the same salt shape the classical path uses under its own label. The full byte-level construction is normative in [Sealed PoE: multi-recipient encryption](#sealed-poe-multi-recipient-encryption).

`mlkem768x25519` (no internal hyphens) is the registry identifier, matching the X-Wing / age ecosystem spelling; this is a deliberate, documented exception to the otherwise-hyphenated identifier convention. Implementations **MUST** emit and accept exactly this spelling. Producers **SHOULD** default to `mlkem768x25519`. The `x25519` identifier exists for recipients whose published key is X25519-only; its smaller slot (≈94 B encoded versus ≈1.2 KB for a hybrid slot) is a packing consequence, not a selection rationale — the KEM choice governs the record's confidentiality lifetime, and sealing with `x25519` is NOT RECOMMENDED where confidentiality must outlive the elliptic-curve era (see [Harvest-now, decrypt-later and the `x25519` KEM](#harvest-now-decrypt-later-and-the-x25519-kem)). An unregistered `enc.kem` value follows the unknown-envelope rule of [Structural validation, verifier roles, and error codes](#structural-validation-verifier-roles-and-error-codes): the envelope becomes opaque with `ENC_UNSUPPORTED` in the default public reading, and the recipient verifier / strict sealed-crypto mode rejects with `UNSUPPORTED_KEM_ALG`. Under a registered `enc.kem`, verifiers **MUST** reject a wrong-length `epk` / `kem_ct` with `KEM_EPK_LENGTH_MISMATCH` / `KEM_CT_LENGTH_MISMATCH`, and a slot whose shape does not match `enc.kem` with `ENC_SLOT_INVALID_SHAPE`.

The Bech32 human-readable prefix of the recipient public-key encoding is `age` for `x25519` (visible prefix `age1…`, the `1` being the Bech32 separator) and `age1pqc` for `mlkem768x25519` (visible prefix `age1pqc1…`). The hybrid prefix is `age1pqc` — **NOT** `age1pq`, which collides with an upstream native ML-KEM-768 + X25519 encoding.

##### X-Wing construction reference

The `mlkem768x25519` identifier is frozen on the byte behaviour of
[draft-connolly-cfrg-xwing-kem-10](https://datatracker.ietf.org/doc/draft-connolly-cfrg-xwing-kem/10/);
a byte-divergent successor revision enters this registry under a new identifier,
and the pinned conformance vectors under [`../conformance/`](https://github.com/cardanowall/label-309/blob/main/conformance) are
authoritative over the Internet-Draft in any byte-level dispute (see
[X-Wing revision pinning](#x-wing-revision-pinning)). Because Internet-Drafts
expire, the construction is reproduced here normatively so that it remains
implementable from this document alone:

```text
XWingLabel  = 0x5c 0x2e 0x2f 0x2f 0x5e 0x5c   ; the 6-byte label, normative as
                                      ; these byte values (informally, the
                                      ; ASCII rendering is \.//^\ — backslash,
                                      ; dot, slash, slash, caret, backslash)
X25519_BASE = 9                       ; the RFC 7748 base point (u = 9, 32-byte little-endian)

expand(sk):                           ; sk: the 32-byte decapsulation seed
    expanded = SHAKE-256(sk, 96)      ; 96-byte output
    d        = expanded[0:32]         ; ML-KEM-768 keygen coin
    z        = expanded[32:64]        ; ML-KEM-768 implicit-rejection coin
    sk_X     = expanded[64:96]        ; X25519 scalar
    (ek_M, dk_M) = ML-KEM-768.KeyGen_internal(d, z)   ; FIPS 203 deterministic keygen
    pk_X     = X25519(sk_X, X25519_BASE)
    return (ek_M, dk_M, sk_X, pk_X)

GenerateKeyPair():
    sk = CSPRNG(32)
    (ek_M, _, _, pk_X) = expand(sk)
    pk = ek_M || pk_X                 ; 1216 bytes = 1184 || 32
    return (sk, pk)                   ; the 32-byte seed IS the decapsulation key

Combiner(ss_M, ss_X, ct_X, pk_X):
    return SHA3-256(ss_M || ss_X || ct_X || pk_X || XWingLabel)   ; 32 bytes

Encapsulate(pk):                      ; pk: 1216 bytes
    ek_M = pk[0:1184];  pk_X = pk[1184:1216]
    ek_X = CSPRNG(32)                 ; ephemeral X25519 scalar
    ct_X = X25519(ek_X, X25519_BASE)
    ss_X = X25519(ek_X, pk_X)
    (ss_M, ct_M) = ML-KEM-768.Encaps(ek_M)   ; includes the FIPS 203 §7.2
                                             ; encapsulation-key validity check
    ss = Combiner(ss_M, ss_X, ct_X, pk_X)
    ct = ct_M || ct_X                 ; 1120 bytes = 1088 || 32
    return (ss, ct)                   ; named fields: .ss, .ct — see the
                                      ; named-field adapter rule in
                                      ; Slot construction (sender)

Decapsulate(ct, sk):                  ; ct: 1120 bytes; sk: the 32-byte seed
    (ek_M, dk_M, sk_X, pk_X) = expand(sk)
    ct_M = ct[0:1088];  ct_X = ct[1088:1120]
    ss_M = ML-KEM-768.Decaps(dk_M, ct_M)   ; implicit rejection — never throws
                                           ; on attacker-supplied wire bytes
    ss_X = X25519(sk_X, ct_X)
    return Combiner(ss_M, ss_X, ct_X, pk_X)
```

The FIPS 203 §7.2 encapsulation-key check inside `Encapsulate` is the
key-validity precondition under which the hybrid's "never below X25519 classical
security" floor holds (see
[KEM selection and the no-mixing rule](#kem-selection-and-the-no-mixing-rule)).
Decapsulation is total over well-lengthed inputs: a malformed ciphertext yields
a wrong-but-well-distributed shared secret through ML-KEM's implicit rejection,
never an exception, and surfaces downstream as an ordinary failed slot. The
conformance vectors pin keygen, encapsulation (with recorded encapsulation
randomness), and decapsulation byte-for-byte against this construction.

#### Passphrase-KDF identifiers (`enc.passphrase.alg`)

The KDF registry has two layers — the passphrase-style KDF that MAY appear on the wire as `enc.passphrase.alg`, and internal building blocks that MUST NOT appear there.

| Identifier | Algorithm                                                                          | Required params                                                                                                                                                                                                                                                                                       | Status                                                                                         |
| ---------- | ---------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| `argon2id` | Argon2id, version `0x13` (19) ([RFC 9106](https://www.rfc-editor.org/rfc/rfc9106)) | `params` is a **closed** map of exactly `m` (memory KiB, **MUST** be ≥ 65 536 ≈ 64 MiB), `t` (iterations, **MUST** be ≥ 3), and `p` (parallelism, **MUST** be ≥ 1); each value is a uint **≤ 2^32 − 1**; an unknown sub-field is rejected (`SCHEMA_UNKNOWN_FIELD`). The output length is fixed at 32 bytes and is NOT carried in `params`. | **M.** The sole MANDATORY-to-implement passphrase KDF; v1 producers MUST emit this identifier. |

Argon2id is memory-hard, which raises the cost of offline brute-force against the published parameters, salt, and ciphertext. The Argon2 version is pinned at `0x13` (19) per [RFC 9106](https://www.rfc-editor.org/rfc/rfc9106); there is no version field on the wire and no other version is admissible under `enc.scheme: 1`. The `p ≥ 1` floor reflects a deliberate browser-compatibility constraint; security is dominated by the `m × t` product, and with `m ≥ 65 536 KiB` and `t ≥ 3` the margin under `p = 1` is adequate. Where the platform supports it, producers **SHOULD** use `p = 4` (the second recommended profile of [RFC 9106 §4](https://www.rfc-editor.org/rfc/rfc9106#section-4)); verifiers **MAY** accept any `p ≥ 1`, subject to the deployment ceilings (`ENC_PASSPHRASE_PARAMS_EXCEED_POLICY`). The accompanying `enc.passphrase.salt` byte string **MUST** be between 16 and 64 bytes inclusive and **MUST** be freshly drawn from a CSPRNG for every passphrase envelope (see [Forbidden patterns](#forbidden-patterns)). Validators **MUST** reject a salt shorter than 16 bytes with `ENC_PASSPHRASE_SALT_TOO_SHORT`, longer than 64 bytes with `ENC_PASSPHRASE_SALT_TOO_LONG`, and `argon2id` params below the minima with `ENC_PASSPHRASE_ARGON2_PARAMS_TOO_LOW`. Implementations MAY enforce non-normative upper bounds against verifier-side DoS, reporting `ENC_PASSPHRASE_PARAMS_EXCEED_POLICY` (a distinct code — the floor and ceiling codes MUST NOT be conflated).

**Internal building-block KDFs (MUST NOT appear as `enc.passphrase.alg`):** `hkdf-sha256` (HKDF-SHA-256, [RFC 5869](https://www.rfc-editor.org/rfc/rfc5869)) is the fixed extract-and-expand construction used for per-slot KEK derivation, slot-set MAC-key derivation, passphrase-commitment MAC-key derivation, content `payload_key` derivation, and seed → key derivation (see [Seed and key derivation](#seed-and-key-derivation) and [Sealed PoE: multi-recipient encryption](#sealed-poe-multi-recipient-encryption)). It carries no wire identifier and is not selectable. A record carrying `enc.passphrase.alg = "hkdf-sha256"` MUST be rejected as `ENC_PASSPHRASE_ALG_UNSUPPORTED` — HKDF is designed for high-entropy inputs, not for stretching low-entropy passphrases.

#### Signature algorithms (`COSE_Sign1` protected `alg`)

Record-level signatures are **always OPTIONAL** in this CIP: authorship is an opt-in claim, never required for a record to verify. A signature's COSE protected `alg` MUST name a registered label; any other label surfaces as `SIGNATURE_UNSUPPORTED` at info severity and does not fail the record. Verification is strict, non-cofactored Ed25519 (RFC 8032 §5.1.7) regardless of which registered label is used (see [Record-level signatures (COSE_Sign1)](#record-level-signatures-cose_sign1)).

| COSE alg | Algorithm                                                                                                                                                                                                                                                         | Status                                                                                                                                                                                                                                                                       |
| -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `-8`     | EdDSA, curve-agnostic ([RFC 9053 §2.2](https://www.rfc-editor.org/rfc/rfc9053#section-2.2), [RFC 8032](https://www.rfc-editor.org/rfc/rfc8032); curve pinned to Ed25519 by the `kty=1`/`crv=6` COSE_Key constraint and the path-1 `kid`-as-public-key convention) | **M.** Mandatory for verifiers; the only `alg` CIP-30 wallets emit on the `signData` path.                                                                                                                                                                                   |
| `-19`    | Ed25519, fully-specified ([RFC 8032 §5.1](https://www.rfc-editor.org/rfc/rfc8032#section-5.1); [RFC 9864 §2.2](https://www.rfc-editor.org/rfc/rfc9864#section-2.2) IANA assignment)                                                                               | **OPT-INFO.** SDK-originated signatures MAY use `-19`. A verifier that implements it verifies it identically to `-8` under the Ed25519 primitive; a verifier that does not surfaces the `sigs[i]` as `SIGNATURE_UNSUPPORTED` and the record's content claim still validates. |
| `-7`     | (reserved) ES256 — ECDSA w/ SHA-256 over P-256 ([RFC 9053 §2.1](https://www.rfc-editor.org/rfc/rfc9053#section-2.1))                                                                                                                                              | **R.** Not standardised in v1; reported as `SIGNATURE_UNSUPPORTED`.                                                                                                                                                                                                          |
| `-49`    | (reserved) ML-DSA-65 ([RFC 9964](https://www.rfc-editor.org/rfc/rfc9964))                                                                                                                                                                                         | **R.** Post-quantum signature; not in v1; reported as `SIGNATURE_UNSUPPORTED`.                                                                                                                                                                                               |

The IANA COSE Algorithms registry marks `-8` (EdDSA, curve-agnostic) as deprecated as of RFC 9864 in favour of the fully-specified `-19`. This CIP (v1) nonetheless **keeps `alg = -8` as the MANDATORY signature identifier** because CIP-30 wallets emit `alg = -8` on the `signData` path, and v1 pins the curve to Ed25519 explicitly at two layers — the COSE_Key carries `kty = 1` (OKP) and `crv = 6` (Ed25519), and the path-1 32-byte protected-header `kid` convention is unambiguously an Ed25519 public key — so the deprecation's curve-ambiguity concern does not apply. The fully-specified `-19` codepoint is registered alongside `-8` at OPT-INFO tier.

#### Registry scope and provenance

The algorithm identifiers above form the **internal algorithm registry**: they live inside this CIP, are normative for it, and are extended only by a future revision of this CIP (a new identifier requires a successor version that lists it). This CIP deliberately does **not** propose registering these strings in [CIP-10](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0010/registry.json), because CIP-10 registers integer `transaction_metadatum_label` values — its scope is the top-level integer namespace `309` (already reserved by CIP-10 for "Proof of Existence record"), not the algorithm strings that live inside the value under that label.

COSE signature algorithm identifiers (the integers `-8`, `-19`, `-7`, `-49`) live in the [IANA COSE registry](https://www.iana.org/assignments/cose), not in this CIP's internal registry, and are referenced by their IANA codepoints when used inside a `COSE_Sign1` protected header. The `rfc9162-sha256` Merkle identifier likewise references the IANA "COSE Verifiable Data Structure Algorithms" registry (codepoint 1).

#### Algorithm agility: the additive-only rule

This CIP uses string identifiers for every algorithm slot precisely so the registry can grow without breaking decoders for older records. To add a new identifier:

1. The primitive **MUST** have a stable public reference (RFC / FIPS / CIP / IANA codepoint / named internet-draft). **No novel cryptography** is admissible.
2. Add the identifier to the appropriate registry under [`../registries/`](https://github.com/cardanowall/label-309/blob/main/registries) with its pinned length constant and the typed error code emitted on each failure mode.
3. Ship a byte-pinned conformance vector under [`../conformance/`](https://github.com/cardanowall/label-309/blob/main/conformance) that exercises the new identifier.

Registry additions are **additive** and do **NOT** bump the wire `v` integer: an existing v1 verifier disposes of the new identifier predictably — a typed rejection for a load-bearing content-hash or KDF identifier, envelope opacity with `ENC_UNSUPPORTED` for a sealed-envelope identifier in the public reading (with the hard `UNSUPPORTED_*` reject preserved in the recipient role and strict sealed-crypto mode), and an info tag for an OPT-INFO identifier — and a new v1 producer MAY emit the identifier as soon as the revision publishes. The algorithm-agility invariant guarantees that an unrecognised identifier produces a clean typed disposition — never silent acceptance, never a crash. Wire-format `v` bumps are reserved for breaking schema changes (a new REQUIRED key, a removed key, a changed type, or a digest length the current grammar cannot express) — not for registry additions.

**Post-quantum migration is already additive.** Post-quantum protection of the sealed-PoE key path ships in v1: the hybrid KEM `mlkem768x25519` (X-Wing) is registered alongside classical `x25519` under `enc.scheme: 1`, selected per-record via `enc.kem`. A further PQ migration (e.g. adding a standalone `ml-kem-768`, or a `ml-dsa-65` / `slh-dsa-sha2-128s` record signature) is a registry addition under the rule above — it requires no new `enc.scheme` profile and no wire-format version bump. Verifiers predating such an addition degrade rather than break: they continue to validate the content-hash claim of a record sealed under the new identifier, tagging its envelope `ENC_UNSUPPORTED`; only sealed-delivery processing of such records requires an updated verifier.

The following identifiers are **reserved** — they appear in the migration roadmap but MUST NOT be emitted by conformant producers and MUST be rejected by conformant verifiers with the appropriate code until they are registered:

- `ml-kem-768` — NIST ML-KEM-768 ([FIPS 203](https://csrc.nist.gov/pubs/fips/203/final)) used **standalone**, without the X25519 hybrid wrapper. Distinct from the registered hybrid `mlkem768x25519`. Goes in `enc.kem`; a verifier that does not implement it applies the unknown-envelope rule (`ENC_UNSUPPORTED` public reading; `UNSUPPORTED_KEM_ALG` in the recipient role and strict sealed-crypto mode).
- `aes-256-gcm` — AES-256-GCM ([NIST SP 800-38D](https://csrc.nist.gov/pubs/sp/800/38/d/final)), an RFC-only content AEAD reserved for a future `enc.scheme` profile; v1 verifiers apply the unknown-envelope rule (`ENC_UNSUPPORTED` public reading; `UNSUPPORTED_AEAD_ALG` in the strict reading).
- `ml-dsa-65` — NIST ML-DSA ([FIPS 204](https://csrc.nist.gov/pubs/fips/204/final)), a signature alternate to Ed25519; v1 verifiers surface `SIGNATURE_UNSUPPORTED` and the content claim remains valid.
- `slh-dsa-sha2-128s` — NIST SLH-DSA ([FIPS 205](https://csrc.nist.gov/pubs/fips/205/final)), a hash-based signature alternate; v1 verifiers surface `SIGNATURE_UNSUPPORTED` and the content claim remains valid.

#### Forbidden primitives

The following are explicitly excluded. Any code path that introduces one is a defect:

- **Unauthenticated symmetric encryption** — AES-CBC without a separate MAC, AES-CTR without a MAC, raw ChaCha20 without Poly1305, RC4 of any kind. Only AEADs from the registry above; an unauthenticated cipher in `enc.aead` is rejected with `UNAUTHENTICATED_CIPHER_FORBIDDEN`.
- **Non-deterministic CBOR for any signature payload** — all bytes that enter Ed25519 sign / verify MUST be produced by the canonical CBOR encoder (RFC 8949 §4.2.1). Indefinite-length encoding, non-canonical map ordering, and duplicate keys MUST be rejected on decode (see [Canonical CBOR and metadata label 309 carriage](#canonical-cbor-and-metadata-label-309-carriage)).
- **Re-deriving a key from a CIP-30 wallet signature** — CIP-30 wallet signatures are kept for record-signing only; re-deriving a key from a `signData` response is unsound and forbidden (see [Seed and key derivation](#seed-and-key-derivation)).
- **SHA-1, MD5, RIPEMD (any variant)** — not for hashing, not for HMAC, not for HKDF. Producers and verifiers MUST NOT emit or accept these algorithms.

#### CDDL grammar and JSON Schemas

The canonical machine-readable grammar for the record body is the CDDL ([RFC 8610](https://www.rfc-editor.org/rfc/rfc8610)) reproduced below; [`../cddl/label-309.cddl`](label-309.cddl) is the extracted canonical copy, and the JSON Schemas under [`../schemas/`](https://github.com/cardanowall/label-309/blob/main/schemas) are the same grammar expressed for JSON tooling. The grammar models the **reassembled record body** — the canonical-CBOR bytes obtained after byte-concatenating the ≤ 64-byte chunk array stored under metadata label 309; the chunk-array transport wrapper is reassembled before structural validation and is not modelled here (see [Canonical CBOR and metadata label 309 carriage](#canonical-cbor-and-metadata-label-309-carriage)). The reassembled body is plain deterministic CBOR — it is not itself a ledger `transaction_metadatum`, and its fields are not subject to the ledger's 64-byte string cap, which the transport wrapper alone satisfies.

The grammar and the JSON Schemas model only the **permissive structural superset** of well-formed shapes: the closed map shapes and the core byte lengths. They do **not** express cross-field invariants (e.g. `enc` key-path exclusivity, the items-or-merkle presence rule, algorithm-dependent nonce length, Merkle leaf-count binding) and they do **not** express registry membership of algorithm identifiers — every identifier rule below is the open `tstr` type, deliberately not a closed enum, because the registries above are authoritative for the accepted value set. Those constraints, and the precise typed error code a conformant verifier emits, are the second, typed-error pass over the decoded structure described in [Structural validation, verifier roles, and error codes](#structural-validation-verifier-roles-and-error-codes). A generic CDDL or JSON-Schema tool confirms only that a candidate record matches the permissive superset; full conformance requires the typed pass. One disposition the grammar does encode structurally is the unknown-envelope rule of that section: `enc` is a choice between the scheme-1 envelope shape and a bounded opaque map (`enc-opaque`), so a record sealed under an identifier this revision does not define still parses at the schema layer instead of being rejected before the typed pass can degrade it. The opaque alternative carries no licence to relax validation: whenever `scheme`, `kem`, and `aead` are all supported identifiers, the typed pass holds the envelope to the scheme-1 shape rules.

**Integer range and exactness.** Every numeric field this CIP defines — `v`,
`merkle[i].leaf_count`, the Argon2id `params` values `m` / `t` / `p`, and the
leaves-list document's `leaf_count` — is a CBOR unsigned integer pinned to the
range `0 .. 2^32 − 1` (`uint32` in the grammar below; `v` is further pinned to
the literal `1`, both `leaf_count` fields to `≥ 1`). Implementations **MUST** decode and compare these values as **exact
integers**: an implementation whose native number type loses integer precision
(for example above `2^53`) **MUST** decode through an exact-width path rather
than a lossy float, and a value outside the pinned range **MUST** be rejected
with the field's typed code rather than wrapped, truncated, or coerced. The
`2^32 − 1` ceiling makes exact handling trivially available in every mainstream
language, so two implementations can never disagree about a boundary value.

```cddl
; A conformant PoE record MUST carry at least one of `items` (>= 1 entry) or
; `merkle` (>= 1 entry); a record with both arrays absent (or both present but
; empty) is rejected as SCHEMA_EMPTY_RECORD. The invariant is enforced in the
; typed pass, not at the CDDL layer.
;
; Extension-key tolerance: keys matching the `^x-.+` or `^[a-z]+-.+` patterns
; are accepted; unknown keys outside either pattern — and keys containing
; control characters, which the typed pass rejects regardless of regex match —
; are rejected as SCHEMA_UNKNOWN_FIELD. The CDDL admits any
; extension-key text string under the open `extension-key` rule below.
;
; An extension value is any CBOR value admitted by this CIP's canonical
; (deterministic) encoding profile: integers, byte strings, text strings,
; arrays, maps, and the simple values false/true/null. Floats and semantic
; tags are excluded by the canonical profile itself (rejected as
; MALFORMED_CBOR at decode), so the exclusion is not repeated here. The
; record body travels under label 309 as an opaque whole-body chunk array,
; so the ledger constrains only that transport wrapper — extension values,
; like every other field in the body, carry no 64-byte string cap. Total
; record size is bounded through the transport by the ledger's maxTxSize,
; so no field-level byte ceiling is imposed.
extension-value =
    { * extension-value => extension-value }
  / [ * extension-value ]
  / int
  / bstr
  / tstr
  / bool
  / null

poe-record = {
  poe-common,
  ? "items": [ 1* item-entry ],
  ? "crit":  [ 1* tstr ],
  * extension-key => extension-value
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
  ? "uris": [ 1* uri ],
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
; `leaf_count` is REQUIRED, MUST be 1 or greater (a zero or out-of-range value
; is rejected as SCHEMA_MERKLE_LEAF_COUNT_INVALID by the typed pass), and binds
; the on-chain commitment to the off-chain leaves-list size (a disagreement
; with the fetched leaves-list is SCHEMA_MERKLE_LEAF_COUNT_MISMATCH).
merkle-commit = {
  "alg":        merkle-commit-alg,
  "root":       bytes32,
  "leaf_count": uint32,
  ? "uris":     [ 1* uri ],
}

; `enc` is a choice between the scheme-1 envelope shape and an opaque envelope.
; The choice exists so the grammar never forecloses the degrade-to-opaque rule
; (the unknown-envelope rule of the validation section): an envelope whose
; `scheme` / `kem` / `aead` names an identifier the implementation does not
; support is NOT validated against the scheme-1 shape rules — it is parsed as
; opaque bounded metadata (generic decode limits only) and dispositioned per
; that rule (ENC_UNSUPPORTED in the public reading; the specific UNSUPPORTED_*
; code in the recipient role and strict sealed-crypto mode). The opaque
; alternative is a verifier escape hatch, never a producer surface, and it
; MUST NOT weaken validation of supported envelopes: when `scheme`, `kem`, and
; `aead` are all supported identifiers, the typed pass MUST hold the envelope
; to the scheme-1 shape and key-path rules — an envelope that fails them is
; rejected with its typed code, never reclassified as opaque.
enc = enc-scheme-1 / enc-opaque

; The scheme-1 shape is itself a permissive superset: a single map rule admits
; both the recipient-slot key path and the passphrase key path. Cross-field
; invariants are NOT expressed in the CDDL; the typed pass enforces them.
; Specifically:
;   - if `slots` is present, then `kem` and `slots_mac` are REQUIRED, and
;     `passphrase` is FORBIDDEN;
;   - if `passphrase` is present, then `kem` / `slots` / `slots_mac` are
;     FORBIDDEN;
;   - exactly one of `slots` or `passphrase` MUST be present
;     (ENC_NO_KEY_PATH and ENC_EXCLUSIVITY_VIOLATION cover the absence /
;     conflict cases).
enc-scheme-1 = {
  "scheme": 1,
  "aead":   aead-alg,
  "nonce":  bstr,
  ? "kem":        kem-alg,
  ? "slots":      [ 1* slot ],
  ? "slots_mac":  bytes32,
  ? "passphrase": passphrase-block,
}

; The opaque reading of an envelope under an unsupported identifier: `scheme`
; is the only structurally required key, and every other entry is any key/value
; pair the canonical encoding profile admits (the `extension-value` set above),
; subject to the generic decode bounds. Scheme-1 slot shapes, byte lengths, and
; key-path rules apply only in the typed pass over a supported envelope; an
; unknown-identifier envelope receives no shape validation beyond this rule.
enc-opaque = {
  "scheme": uint,
  * tstr => extension-value
}

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

; enc.kem = "mlkem768x25519": the 1120-byte X-Wing ciphertext plus the wrapped
; CEK. There is NO `epk` — the X25519 ephemeral is the trailing 32 bytes of the
; X-Wing ciphertext inside `kem_ct`. The typed pass enforces the exact length
; (KEM_CT_LENGTH_MISMATCH).
hybrid-slot = {
  "kem_ct": bstr .size 1120,
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
  "params": { "m": uint32, "t": uint32, "p": uint32 },
}

; A sig-entry is a closed CBOR map. "cose_sign1" is REQUIRED and carries the
; CBOR-encoded COSE_Sign1 produced by the signer as a single byte string.
; "cose_key" is OPTIONAL and, when present, carries the CBOR-encoded COSE_Key
; for the CIP-30 wallet path as a single byte string; it is omitted for the
; in-signature `kid` (identity-key) path. The field names describe what the
; bytes are on the wire: `cose_sign1` = COSE_Sign1, `cose_key` = COSE_Key.
; No other keys are permitted. The normative path-selection rules make
; path 1 (32-byte protected-header `kid`) and path 2 (`cose_key`
; side-channel) mutually exclusive at the wire level;
; SIG_ENTRY_KID_COSE_KEY_CONFLICT rejects records carrying both.
sig-entry = {
  "cose_sign1":  bstr,
  ? "cose_key":  bstr,
}

; A uri is one absolute URI in a single text string. UTF-8 well-formedness is
; guaranteed by the canonical CBOR decode; the URI shape rules (absolute per
; RFC 3986 §4.3, no fragment, closed scheme set {ar://, ipfs://}, per-scheme
; body shape) are enforced in the typed pass, which emits INVALID_URI. The
; rule carries no length cap: the whole-body transport satisfies the ledger's
; string cap, so a long ipfs:// CID-plus-path URI is a single tstr.
uri = tstr

bytes32 = bstr .size 32

; uint32 is the pinned range of every numeric field in this CIP: an unsigned
; integer representable in 4 bytes (0 .. 2^32-1), handled as an exact integer
; by every implementation. See "Integer range and exactness" above.
uint32 = uint .size 4

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
; The `enc-scheme-1` rule admits any combination of `kem` / `slots` /
; `slots_mac` / `passphrase` keys at the CDDL layer; the following cross-field
; invariants are enforced by the typed-error pass, not the grammar:
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
; SCHEMA_MERKLE_LEAF_COUNT_INVALID, SIG_ENTRY_INVALID_SHAPE,
; SIG_ENTRY_KID_COSE_KEY_CONFLICT, SIG_PRIVATE_KEY_LEAKED, and so on). A
; single-pass implementation that emits a generic CDDL-mismatch error is
; conformant to the wire format but is NOT conformant to the typed-error
; contract; conformant verifiers MUST emit the precise codes.
; ---------------------------------------------------------------------------
```

### Structural validation, verifier roles, and error codes

Correctness in this CIP is checked in three layers. Each layer is a strict superset of the one before it, and each can be implemented and shipped independently.

1. **Structural validator (Part A).** A pure function over the reassembled CBOR bytes that claim to be a PoE record. It performs schema and domain-rule conformance only: it MUST NOT touch the network, MUST NOT verify any signature cryptographically, and MUST NOT decrypt. It is profile-agnostic — it parses the full v1 schema (the grammar in [`../cddl/label-309.cddl`](label-309.cddl)) regardless of which subset a downstream verifier validates end-to-end.
2. **Public verifier (Part B, default mode).** Layers on top of the structural validator. Given a Cardano transaction reference it fetches the transaction metadata from a public blockchain explorer, runs the structural validator, verifies every embedded Ed25519 record signature, and optionally fetches and hash-checks plaintext content at `ar://` / `ipfs://` URIs. It does not decrypt.
3. **Recipient verifier (Part B, sealed-decrypt mode).** A public verifier that additionally holds one or more decryption credentials — recipient KEM private keys (a 32-byte X25519 scalar for `x25519`, or a 32-byte X-Wing decapsulation seed for `mlkem768x25519`) and/or passphrases — and performs sealed-PoE decryption plus post-decryption plaintext-hash recomputation (see [Sealed PoE: multi-recipient encryption](#sealed-poe-multi-recipient-encryption)).

All three layers MUST run **without contacting any single-operator infrastructure**. This is a binding property of this CIP — a proof verifies given only the transaction metadata, optionally the content bytes, and a public blockchain explorer. It is restated as the service-independence property at the end of this section.

The authoritative error catalogue is the machine-readable registry [`../registries/error-codes.json`](https://github.com/cardanowall/label-309/blob/main/registries/error-codes.json); the conformance vectors that pin each failure mode to its code live under [`../conformance/`](https://github.com/cardanowall/label-309/blob/main/conformance) (validator-rejection cases in [`../conformance/validator/`](https://github.com/cardanowall/label-309/blob/main/conformance/validator), cross-service / service-independence cases in [`../conformance/cross-service/`](https://github.com/cardanowall/label-309/blob/main/conformance/cross-service)). A conformant implementation MUST emit exactly the `SCREAMING_SNAKE_CASE` codes defined there for the failure modes defined there; it MUST NOT introduce lowercase synonyms, `schema_*`-prefixed parser-internal codes, or free-form reason strings. The families summarized below are the index into that registry, not a substitute for it.

#### Part A — the structural validator

##### Function shape and purity

The structural validator is a single function from a byte string (plus a small options object) to a result:

```ts
validatePoeRecord(bytes: Uint8Array, options?: ValidatorOptions): ValidationResult

interface ValidatorOptions {
  // Names of the critical extensions this validator implements.
  // Default: the empty set — a default-configured validator therefore fails
  // every `crit`-bearing record with EXTENSION_UNSUPPORTED_CRITICAL, by design.
  supportedCriticalExtensions?: Set<string>;
}

type ValidationResult =
  | { valid: true;  record: PoeRecord; warnings?: ValidationIssue[]; info?: ValidationIssue[] }
  | { valid: false; issues: ValidationIssue[] };

interface ValidationIssue {
  path: (string | number)[];  // segments from the record root: text map keys and
                              // integer array indices, e.g. ["items", 0, "hashes", "sha2-256"]
                              // (rendered dotted for display: "items.0.hashes.sha2-256")
  code: string;     // SCREAMING_SNAKE_CASE code from the registry
  severity?: 'error' | 'warning' | 'info';  // defaults to 'error' if omitted
  message: string;  // human-readable explanation including the offending value
}
```

The validator MUST be **pure**: it performs no I/O, allocates no global state, and emits deterministic output for any given `(bytes, options)` pair. The issue `path` is normatively an ordered list of **segments** — text-string map keys and integer array indices, exactly as traversed from the record root; the dotted string shown in examples is a display rendering, not the wire/API form (a rendering must contend with map keys that themselves contain `.`, which the segment list represents without escaping). All issues MUST be sorted by `path` **segment-wise**: paths are compared element by element from the root — two integer segments compare numerically, two text segments compare by the bytewise order of their UTF-8 encodings, and where the segment kinds differ the integer segment orders first; a path that is a strict prefix of another orders before it. Issues carrying an identical path tie-break by the order in which their `code` values appear in the error-code registry. No locale-dependent collation is permitted: the ordering MUST be byte-stable across runs and across language implementations. A record's `valid: true` verdict MUST NOT be reported when any `error`-severity issue is present; `warning`- and `info`-severity issues MUST be surfaced but MUST NOT by themselves fail the record.

The reassembly of the chunked record body — byte-concatenation of the metadata-label-309 array of ≤ 64-byte byte strings — and the unwrapping of the carrying transaction's auxiliary data happen **before** the validator runs (see [Canonical CBOR and metadata label 309 carriage](#canonical-cbor-and-metadata-label-309-carriage)); the validator receives the reassembled record body and never re-encodes it. Carriage-shape rejections (`MALFORMED_CBOR` for a non-chunk-array label-309 value, `CHUNK_TOO_LARGE` for an oversized transport chunk — see the carriage-error taxonomy) are emitted by that reassembly step, not by the validator itself.

##### Pipeline

The validator runs a fixed pipeline; any step that produces an `error`-severity issue still allows later steps to run, and all issues are collected and emitted together (sorted by `path`).

1. **Canonical CBOR decode.** The bytes MUST be decoded with a canonical decoder enforcing the deterministic-encoding rules of RFC 8949 §4.2.1: definite lengths, bytewise-lexicographically sorted map keys, no duplicate keys, valid UTF-8 text strings, minimal integer encodings. Any decode failure — including non-canonical ordering, indefinite-length encodings, and duplicate map keys — surfaces as the single code `MALFORMED_CBOR`. There is no separate duplicate-key code: canonical-decode rejection covers it.
2. **Schema parse.** The decoded value is run through a closed-schema parser ([`../schemas/`](https://github.com/cardanowall/label-309/blob/main/schemas)). The schema is the structural authority: type checks, length bounds (the 32-byte length checks on `supersedes` and on commitment roots, the pinned key-material lengths), and a strict object mode that rejects unknown fields. The schema imposes **no** numeric cap on `items[]`, `sigs[]`, or `slots[]` entry counts — the only ceiling is the ledger's maximum transaction size, enforced at submission by Cardano nodes; a validator MUST NOT emit an error solely because an entry count is high.
3. **Domain checks.** A second pass enforces cross-field constraints the schema cannot express ergonomically: registry membership for every algorithm identifier, URI shape and scheme checks, per-slot key-material and wrap lengths, COSE structural decode, and `crit[]` shape. The domain pass walks each item, then the record-level `sigs[]`, then `merkle[]`.
4. **Result emission.** If any `error`-severity issue was collected, the record is reported `valid: false` with the full sorted issue list. Otherwise it is reported `valid: true` with the decoded record plus any `warnings` / `info` issues.

##### Error families (Part A)

Every code below is emitted by `validatePoeRecord` and carries `severity: error` unless noted. The registry [`../registries/error-codes.json`](https://github.com/cardanowall/label-309/blob/main/registries/error-codes.json) is authoritative for the complete list and the exact trigger of each code.

| Family                                 | Codes                                                                                                                                                                                                                                                                                                                                            | Triggered by                                                                                                                                                                                                                                                                                                                                                                                                                 |
| -------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `MALFORMED_CBOR`                       | `MALFORMED_CBOR`                                                                                                                                                                                                                                                                                                                                 | any canonical-CBOR decode failure (RFC 8949 §4.2.1) — non-canonical ordering, indefinite length, duplicate keys, invalid UTF-8, non-minimal integers.                                                                                                                                                                                                                                                                        |
| `SCHEMA_*`                             | `SCHEMA_TYPE_MISMATCH`, `SCHEMA_MISSING_REQUIRED`, `SCHEMA_UNKNOWN_FIELD`, `SCHEMA_INVALID_LITERAL`, `SCHEMA_EMPTY_RECORD`                                                                                                                                                                                                                       | wrong CBOR type; a REQUIRED field absent; an unknown field in a closed map; `v` ≠ `1`; a record committing to neither `items[]` nor `merkle[]` with ≥ 1 entry.                                                                                                                                                                                                                                                               |
| `HASH_*`                               | `HASH_DIGEST_LENGTH_MISMATCH`, `UNSUPPORTED_HASH_ALG`                                                                                                                                                                                                                                                                                            | a digest length ≠ the length pinned for its algorithm; a `hashes` key outside the hash-algorithm registry.                                                                                                                                                                                                                                                                                                                   |
| `ENC_*` (envelope shape)               | `UNAUTHENTICATED_CIPHER_FORBIDDEN`, `UNSUPPORTED_AEAD_ALG`, `NONCE_LENGTH_MISMATCH`, `UNSUPPORTED_ENVELOPE_SCHEME`, `ENC_UNSUPPORTED` (dual), `ENC_SLOTS_EMPTY`, `ENC_SLOT_INVALID_SHAPE`, `ENC_SLOTS_DUPLICATE_KEM_MATERIAL`, `ENC_SLOTS_TOO_MANY`, `ENC_ENVELOPE_TOO_LARGE`, `ENC_SLOTS_MAC_INVALID_LENGTH`, `ENC_SLOTS_MAC_REQUIRED`, `ENC_SLOTS_REQUIRED`, `ENC_EXCLUSIVITY_VIOLATION`, `ENC_NO_KEY_PATH`, `ENC_KEM_REQUIRED`, `ENC_REQUIRES_CONTENT_HASH` | `enc.aead` names an unauthenticated cipher family; an `enc.scheme` / `enc.kem` / `enc.aead` outside the implemented set — `ENC_UNSUPPORTED` (info) with the envelope opaque in the public reading, the specific `UNSUPPORTED_ENVELOPE_SCHEME` / `UNSUPPORTED_KEM_ALG` / `UNSUPPORTED_AEAD_ALG` (error) in the recipient role and strict sealed-crypto mode (see the unknown-envelope rule below); nonce length ≠ the content format's registered `enc.nonce` length (24 bytes for `chacha20-poly1305-stream64k`); empty / malformed / mutually-exclusive key-path violations; two slots sharing `epk` / `kem_ct`; `slots[]` above the verifier's slot-count bound; a decoded `enc` envelope above its size bound (reference bounds `MAX_SLOTS` = 1024 / 65536 bytes, deployment-pinned); `slots` without `slots_mac` (or vice versa); `slots` without `kem`; an `enc`-bearing item whose `hashes` map carries no key from the content-hash registry (`ENC_REQUIRES_CONTENT_HASH` — e.g. a map whose only key is an unregistered identifier; it MAY co-fire with `UNSUPPORTED_HASH_ALG` on the same item).                                                                                      |
| `ENC_PASSPHRASE_*`                     | `ENC_PASSPHRASE_ALG_UNSUPPORTED`, `ENC_PASSPHRASE_SALT_TOO_SHORT`, `ENC_PASSPHRASE_SALT_TOO_LONG`, `ENC_PASSPHRASE_ARGON2_PARAMS_TOO_LOW`, `ENC_PASSPHRASE_PARAMS_EXCEED_POLICY`                                                                                                                                                                 | `enc.passphrase.alg` outside the KDF registry (`{argon2id}`); salt length outside `[16, 64]`; Argon2id parameters below the floor (`m ≥ 65536`, `t ≥ 3`, `p ≥ 1`); parameters above an operator-configured upper bound (policy-dependent, not a wire MUST).                                                                                                                                                                  |
| `KEM_*`                                | `UNSUPPORTED_KEM_ALG`, `KEM_EPK_LENGTH_MISMATCH`, `KEM_CT_LENGTH_MISMATCH`, `WRAP_LENGTH_MISMATCH`                                                                                                                                                                                                                                               | `enc.kem` outside `{x25519, mlkem768x25519}`; `slot.epk` ≠ 32 bytes (`x25519`); `slot.kem_ct` ≠ 1120 bytes (`mlkem768x25519`); `slot.wrap` ≠ 48 bytes. All four are pure byte-length checks; the validator runs no decapsulation.                                                                                                                                                                                |
| `SIG_*`                                | `MALFORMED_SIG_COSE_SIGN1`, `SIGNATURE_UNSUPPORTED` (info), `SIG_ENTRY_INVALID_SHAPE`, `SIG_ENTRY_KID_COSE_KEY_CONFLICT`, `SIG_PRIVATE_KEY_LEAKED`                                                                                                                                                                                               | a `sigs[i].cose_sign1` blob that is not a 4-element COSE_Sign1, or carries a non-null (attached) payload, or carries a malformed inline `cose_key`; an unrecognized signature `alg` (tagged, not rejected); a `sigs[i]` entry that is not the closed `{cose_sign1, ?cose_key}` map; both an in-signature `kid` and an inline `cose_key` present (mutually exclusive); a private-key label leaking into an inline `cose_key`. |
| `MERKLE_*`                             | `UNSUPPORTED_MERKLE_COMMIT_ALG`, `SCHEMA_MERKLE_LEAF_COUNT_INVALID` (Part A)                                                                                                                                                                                                                                                                     | a `merkle[].alg` outside the Merkle-commitment registry; a `merkle[].leaf_count` of `0` or above `2^32 − 1` — a structural check requiring no off-chain bytes. (The Merkle codes that require off-chain leaves — root recomputation, leaf-count binding, leaves availability — are verifier-layer codes, below.)                                                                                                             |
| `URI_*`                                | `INVALID_URI`                                                                                                                                                                                                                                                                                                                                    | a `uris[]` entry that is not an absolute URI per RFC 3986 §4.3, carries a fragment, names a scheme outside the closed fetch set `{ar://, ipfs://}`, or fails the per-scheme shape rules (`ar://` txid shape, the CID profile).                                                                                                                                                                                               |
| `SUPERSEDES_*` / `CRIT_*` / extensions | `SUPERSEDES_TX_INVALID_LENGTH`, `CRIT_SHAPE_INVALID`, `EXTENSION_UNSUPPORTED_CRITICAL`                                                                                                                                                                                                                                                           | `supersedes` is bytes but ≠ 32 bytes; a `crit[]` entry that is a base key, fails the extension-key regex, names an absent field, or duplicates another; a well-formed `crit[]` entry naming an extension this verifier does not implement.                                                                                                                                                                                   |

A small number of cross-field rules — content-commitment presence, digest length, nonce length, key-path exclusivity, the `sigs[i]` map shape, and the `supersedes` length — MAY be encoded as schema refinements rather than in the domain pass; either way the validator MUST surface the canonical code, never a parser-internal code (`invalid_type`, `too_small`, …).

##### Closed schema and forward compatibility

v1 records use a closed map schema. Unknown keys at any level are invalid, and unknown values in the cryptographic registries never validate. The governing principle is: **never claim to have verified what a verifier cannot reproduce, and never create an open-ended metadata surface under label 309.** Three behaviours follow:

- **Reject-and-fail (security-critical).** A future protocol major (`v ≠ 1`) MUST be rejected (`SCHEMA_INVALID_LITERAL`); an unknown content-hash or Merkle-commitment identifier MUST be rejected (`UNSUPPORTED_HASH_ALG` / `UNSUPPORTED_MERKLE_COMMIT_ALG`); an unknown `enc.passphrase.alg` MUST be rejected (`ENC_PASSPHRASE_ALG_UNSUPPORTED`); a non-null COSE_Sign1 payload MUST be rejected (`MALFORMED_SIG_COSE_SIGN1` — detached-only); a private-key label in an inline `cose_key` MUST be rejected (`SIG_PRIVATE_KEY_LEAKED`); a critical extension outside the validator's `supportedCriticalExtensions` set MUST be rejected (`EXTENSION_UNSUPPORTED_CRITICAL`, with IETF precedent in RFC 7515 §4.1.11 and RFC 9052 §3.1); and a field outside the closed grammar MUST be rejected (`SCHEMA_UNKNOWN_FIELD`). These reject hard because each is load-bearing for the very claim being validated: an unknown content-hash identifier leaves nothing the record can be verified against.
- **Accept-and-tag (unverifiable signature).** An unrecognized COSE_Sign1 `alg` MUST be tagged `SIGNATURE_UNSUPPORTED` (severity `info`, not `error`) on the offending `sigs[i]` entry and MUST NOT fail the record on that ground alone. The content claim — the on-chain `hashes` commitments — is structurally valid regardless of which signature algorithms a verifier supports; an unverifiable signature leaves the proof-of-existence claim intact, and the verifier never claims to have verified it.
- **Degrade-to-opaque (the unknown-envelope rule).** An `enc` envelope whose `scheme`, `kem`, or `aead` names an identifier the implementation does not support — whether registered by a successor revision or simply unknown; the two are indistinguishable to an older verifier — becomes **opaque**: the implementation MUST NOT half-validate the remaining envelope surface against an unknown identifier (no slot-shape checks under an unknown `kem`, no nonce-length check under an unknown `aead`, no key-path cross-field rules under an unknown `scheme`); the envelope is parsed only as bounded CBOR metadata, subject to the generic decode bounds — the grammar's `enc-opaque` alternative (see [CDDL grammar and JSON Schemas](#cddl-grammar-and-json-schemas)), so the schema layer admits the envelope rather than rejecting it before this rule can apply. The opaque reading is available **only** under an unsupported identifier: when `scheme`, `kem`, and `aead` are all supported, the scheme-1 shape and key-path rules are mandatory, and an envelope that fails them is rejected with its typed code — never reclassified as opaque. One carve-out: an `enc.aead` naming a forbidden unauthenticated cipher family (see [Forbidden primitives](#forbidden-primitives)) never takes the opaque reading — it is rejected with `UNAUTHENTICATED_CIPHER_FORBIDDEN` in every role, because a forbidden primitive is a recognised hazard, not an unknown identifier. The affected item is tagged per-item `ENC_UNSUPPORTED`, carrying the unrecognised identifier(s) in the message; the item's content-hash claim is still validated, and `ENC_REQUIRES_CONTENT_HASH` still applies (it inspects the item's `hashes` map, not the envelope). `ENC_UNSUPPORTED` carries **dual severity**. In the default public-verifier reading it is `info`: a public verifier never decrypts, so an envelope it cannot shape-validate subtracts nothing from the claim it actually verifies — the timestamped hash commitment. For the **recipient verifier**, and for any verifier operating in **strict sealed-crypto mode** (a deployment configuration for consumers that must not surface partially-validated sealed records), the same condition is a hard reject: `ENC_UNSUPPORTED` escalates to `error`, co-firing with the specific code naming the unrecognised identifier (`UNSUPPORTED_ENVELOPE_SCHEME` / `UNSUPPORTED_KEM_ALG` / `UNSUPPORTED_AEAD_ALG`) — a sealed delivery MUST NOT be processed under an envelope the verifier cannot fully validate. In every role, a UI MUST NOT present a record tagged `ENC_UNSUPPORTED` as a verified sealed delivery: only the timestamp/hash claim is verified, and the rendering must say so.

##### Service-independence of the validator

Because the validator is a pure function, anyone holding a PoE byte string can validate it offline — no service, no API key, no telemetry. This makes it usable by producers pre-submission, by third-party verifiers built against the public vectors, and by archival tools confirming long-term well-formedness. Implementations in different languages MUST reproduce the same algorithm and the same error codes byte-exact; a record that validates in one language but not another is a conformance bug.

#### Part B — the public verifier and the recipient verifier

The verifier accepts a Cardano transaction reference plus a small set of optional inputs and produces a structured report. A sibling entry point runs the same pipeline from the structural-validator step onward over caller-supplied label-309 metadata bytes plus a block-info tuple (existence, confirmation depth, `block_time`, optionally `block_slot`; see [Chain facts: block time and confirmation depth](#chain-facts-block-time-and-confirmation-depth)) — the path a server-rendered viewer uses to display on-chain data without a render-time chain fetch.

##### Inputs

The relevant optional inputs are:

- An ordered Cardano explorer chain plus an optional fallback explorer, for resolving the transaction.
- Ordered Arweave and IPFS gateway chains, for resolving `ar://` / `ipfs://` URIs.
- A confirmation-depth threshold (deployment policy; RECOMMENDED ≥ 15 blocks ≈ 5 minutes, raised for high-value notarisation).
- A `denyHosts` list of hosts that MUST NOT be contacted (see the service-independence property).
- A `maxFetchBytes` per-URI fetch ceiling the verifier MUST enforce incrementally during streaming. The ceiling is deployment policy, like `MAX_SLOTS`: this CIP pins no default, because content size is unbounded by design and a deployment serving large-content use cases sets the ceiling to match. A fetch that reaches the ceiling is aborted and surfaced as `CONTENT_FETCH_LIMIT_EXCEEDED` (network/policy class) — a statement about the verifier's policy, never about the record.
- A `fetchContent` master switch (default true) that, when false, suppresses every outbound content fetch — item URIs, Merkle leaves-lists, and ciphertext alike — so a record renders **offline** from indexed CBOR alone, with every content claim reported as not checked.
- A `decryption[]` array — the verification run's **keyring**: a set of decryption credentials global to the run, not positionally paired with encrypted items. Entries are a discriminated union: `recipientSecretKey` (the recipient KEM private key — a 32-byte X25519 scalar or a 32-byte X-Wing decapsulation seed) applies to items on the `enc.slots` path, and `passphrase` applies to items on the `enc.passphrase` path. For each `enc`-bearing item the verifier attempts every applicable credential independently — each supplied private key through that item's trial-decrypt loop, each supplied passphrase through that item's passphrase path — and reports the outcome per item in the report's per-item entries; one credential may open several items, and different credentials may succeed on different items. An `enc`-bearing item for which the keyring holds no credential of the applicable shape (for example, only passphrases supplied against a slots-path item) MUST be reported with `WRONG_DECRYPTION_INPUT_SHAPE`.
- Optional out-of-band ciphertext bytes and out-of-band Merkle leaves-list bytes, keyed by item / commit index, used when a producer chose out-of-band delivery.

The report's network identifier names the network of the **resolved transaction** (for example `cardano:mainnet`), as established by the explorer chain the verifier is configured against; the verifier MUST NOT trust any network value from the record body (records carry none). Production deployments of this CIP target mainnet — that is deployment guidance for operators, not a wire rule, and a verifier pointed at a test network reports that network's identifier.

##### Pipeline

The verifier executes the following steps in order; a step whose outcome forecloses the rest — a failed integrity binding, a structural rejection, or (recommended) a `pending` confirmation — short-circuits the pipeline. Every outbound network call MUST pass through a single recording wrapper (see the service-independence property).

1. **Resolve the transaction.** Resolve via the configured explorer chain — a public, open Cardano explorer; an open indexer API (for example, a Koios-compatible endpoint) and a freemium explorer API (for example, Blockfrost) are non-normative examples, and either suffices. The verifier MUST fetch the **raw on-chain transaction CBOR**, not the explorer's metadata-JSON projection. The JSON projection is lossy — it discards map-key ordering, definite-vs-indefinite length, integer/float/sign discrimination, and bytes-vs-text discrimination — so a verifier that re-encoded from it could not reproduce the byte-exact signing input, and every Ed25519 verification on conforming records would fail. Resolution distinguishes two negative outcomes. A provider that answers it knows no transaction under the requested hash yields `TX_NOT_FOUND` (network class): a single provider's negative answer is **not** authoritative for the chain — the transaction may be on chain and merely unknown to, not yet indexed by, or withheld by that provider — so the verifier SHOULD consult every remaining provider in the chain before emitting it. If every provider is unreachable or returns no usable response, the verifier emits `PROVIDER_UNAVAILABLE` (network class).
2. **Bind the fetched bytes to the transaction reference.** Before reading anything out of a fetched transaction, the verifier MUST recompute `blake2b-256` over the fetched transaction-body bytes — by ledger definition, the transaction id — and reject the response on any mismatch with the requested transaction hash. It MUST then recompute `blake2b-256` over the fetched auxiliary-data bytes and reject on any mismatch with the `auxiliary_data_hash` field of the now-verified transaction body (a response whose body carries no `auxiliary_data_hash` while auxiliary data is present fails the same check; such a transaction cannot exist on chain). Both digests MUST be computed over the bytes exactly as fetched, never over a re-encoding. A response that fails either check carries provably wrong bytes: the verifier MUST discard it and SHOULD try the next provider in the chain; if no provider yields a response that survives the binding, the report carries `TX_INTEGRITY_MISMATCH` — a provider actively served bytes that do not match the requested reference, which is distinct from mere unavailability. The mismatch is provable against the **providers**, not the record: no record bytes were ever obtained, so nothing record-attributable was established, and the verdict is `unverifiable`, never `failed` — the code in the issue list is what distinguishes active provider misbehaviour from simple unreachability. After this step every byte of the record body and of the surrounding transaction is cryptographically committed to the caller-supplied transaction hash; no explorer can substitute, amend, or truncate the record without producing a blake2b-256 second preimage. The chain facts the binding does **not** establish — inclusion, block height, confirmation depth, block slot, block time — are treated in [Chain facts: block time and confirmation depth](#chain-facts-block-time-and-confirmation-depth).
3. **Unwrap the auxiliary data and reassemble the record body.** The verifier unwraps the bound auxiliary-data bytes — accepting all three Conway-era envelope forms and dispatching on the top-level CBOR type and tag only, never on map-key inspection (see [Auxiliary-data envelope forms](#auxiliary-data-envelope-forms)) — and byte-concatenates the label-309 chunk array to reconstruct the record body, returning the concatenated bytes raw with no re-encode pass; a non-conformant label-309 value is rejected per the [carriage-error taxonomy](#carriage-error-taxonomy). If the bound transaction carries no metadata under label 309, the verifier emits `METADATA_NOT_FOUND` — a record-attributable outcome, not a network one: because the bytes are hash-bound to the requested transaction (step 2), the absence is proven by the transaction itself, and no provider could have stripped the metadata without failing the binding.
4. **Structurally validate.** Run `validatePoeRecord` over the reassembled bytes. A validator rejection short-circuits the report with verdict `failed` (integrity class) and the validator's issue list.
5. **Check confirmation depth.** Confirmation depth is the explorer-asserted quantity defined in [Chain facts: block time and confirmation depth](#chain-facts-block-time-and-confirmation-depth). A transaction below the verifier's confirmation-depth threshold MUST be reported with `INSUFFICIENT_CONFIRMATIONS` and verdict `pending` (NOT `failed`): the record is structurally well-formed and may settle on retry. The threshold guards the orphaned-block reorg window under Ouroboros Praos; a verifier that reported depth-1 records as valid would let an attacker obtain a "valid" verdict on both sides of a fork. A `pending` outcome SHOULD halt the pipeline here: the signature, content-fetch, and decryption steps below are skipped and the report states they did not run — content and signature results computed against a transaction that may yet be orphaned would invite consumers to act on them. A deployment MAY nonetheless run the later steps for preview purposes, but the verdict remains `pending` and no result from a pending record may be presented as final.
6. **Verify record signatures (strict Ed25519, detached-only).** For each `sigs[i]`: decode the `cose_sign1` byte string as the 4-element COSE_Sign1 (non-null payload → `MALFORMED_SIG_COSE_SIGN1`), preserve the producer's original `protected` bytes verbatim, and rebuild the canonical `Sig_structure` with `external_aad = h''` and a `to_sign` of the 25-byte UTF-8 domain prefix `cardano-poe-record-sig-v1` concatenated with the canonical CBOR of the record body **with `sigs` removed**. Resolve the signer's 32-byte Ed25519 public key via exactly one of the two mutually-exclusive paths (in-signature protected-header `kid`, or the inline `cose_key` CIP-30 wallet side-channel); failure to resolve → `SIGNER_KEY_UNRESOLVED`. Verify with **strict** Ed25519 per RFC 8032 §5.1.7 — canonical R/S, low-order public-key rejection, no cofactor multiplication; the cofactored / ZIP-215 variant MUST NOT be used. A failed verification → `SIGNATURE_INVALID`. For a wallet-path signature, the verifier MUST additionally recompute `expected_network_header || Blake2b-224(pubkey)` — deriving the expected network header byte from the **containing transaction's network**, never echoing the byte found in the record — and compare it against the full 29 bytes of the protected-header `address`; a mismatch (or a missing `address`, which is REQUIRED on the wallet path) → `WALLET_ADDRESS_MISMATCH`, distinct from `SIGNATURE_INVALID`. An unrecognized signature `alg` surfaces as `SIGNATURE_UNSUPPORTED` (info). Record signatures are OPTIONAL: a public hash-only PoE remains valid even when every signature entry is unverifiable; the proof-of-existence claim rests on the on-chain commitment, not on any identity binding.
7. **Fetch and hash-check content / Merkle leaves** (skipped entirely when `fetchContent` is false; every claim is then reported as not checked). **Integrity, attribution, and availability are distinct outcomes throughout this step**: fetched bytes that fail a commitment are a record-attributable integrity failure only when they are **attributable** — bound to the URI's content address per [Content-address binding of fetched bytes](#content-address-binding-of-fetched-bytes); unattributable mismatching bytes indict the serving provider; bytes that could not be fetched leave the claim unchecked and contribute a non-`failed` verdict (see step 10). For each non-`enc` item that proceeds to fetch, the verifier resolves the item's URIs in order against the scheme-appropriate gateway chain, enforcing `maxFetchBytes` incrementally (ceiling reached → abort that fetch with `CONTENT_FETCH_LIMIT_EXCEEDED`, network/policy class). Multiple URIs are alternative sources for the same bytes, processed **first-success-for-availability**: once one URI yields bytes satisfying every digest in `item.hashes` (registry `{sha2-256, blake2b-256}`), the item's content claim is checked and the remaining URIs MAY be skipped. Fetched bytes that fail a digest split on attribution: **attributable** bytes — content-address binding verified — are a hard `URI_INTEGRITY_MISMATCH` (error, integrity class) regardless of what any other URI holds, because the producer asserted at publication that every listed URI resolves to committed bytes, so one provably mismatching URI condemns the record even if a sibling URI matches; **unattributable** bytes — binding not verified, or verified and failed — are `URI_PROVIDER_INTEGRITY_MISMATCH` (warning): the serving provider, not the record, is indicted, and the verifier continues with the remaining URIs and gateways. A per-attempt fetch failure is `URI_FETCH_FAILED` (warning); a URI list exhausted with no attributable bytes satisfying the commitment is `CONTENT_UNAVAILABLE` (error, network class — the claim is unchecked, the record is not condemned). A URI scheme outside `{ar://, ipfs://}` that bypassed structural validation is refused defence-in-depth with `URI_TARGET_FORBIDDEN`. For each `merkle[i]`, the verifier obtains the leaves-list document (from the supplied bytes, or by fetching `merkle[i].uris[]` under the same first-success / attribution / fetch-ceiling semantics), validates it against [the leaves-list document](#the-leaves-list-document) grammar and the on-chain commitment (`SCHEMA_MERKLE_LEAVES_FORMAT_UNSUPPORTED` for a recognisable container of an unsupported format, `SCHEMA_MERKLE_LEAVES_MALFORMED` for bytes that are not the container, `SCHEMA_MERKLE_LEAF_COUNT_MISMATCH` on any leaf-count disagreement), recomputes the RFC 9162 §2.1.1 root, and compares byte-exact (`MERKLE_ROOT_MISMATCH`). These record-attributable outcomes hold the record to account only for an **attributable** leaves-list — supplied out-of-band, or fetched with a verified content-address binding; an unattributable fetched document that fails them is `URI_PROVIDER_INTEGRITY_MISMATCH` (warning) and the verifier continues with the remaining sources. A claim left with no attributable leaves-list is `MERKLE_LEAVES_UNAVAILABLE` — a warning when at least one other content commitment of the record was verified in this step, escalating to `error` (network class, verdict `unverifiable` per step 10) when the unavailability leaves the record with no verified content commitment, as on a merkle-only record. A verifier that does not implement Merkle-fold records each commitment as `MERKLE_UNSUPPORTED` — `info` when the record also carries an `items[]` content claim the verifier validated, `error` for the merkle-only case.
8. **Decrypt (recipient verifier only).** For each `enc`-bearing item — when the `decryption[]` keyring is non-empty — the verifier acquires the ciphertext blob (from supplied out-of-band bytes, or by fetching `item.uris[]`; neither available → `CIPHERTEXT_UNAVAILABLE`), dispatches on the item's on-wire key path, and attempts every applicable keyring credential independently (see Inputs above). The two paths are mutually exclusive. On the `slots` path it runs the sealed-PoE trial-decrypt loop (per [Sealed PoE: multi-recipient encryption](#sealed-poe-multi-recipient-encryption)): per-slot acceptance folding the KEM validity bit, the wrap-open, and the slot-set MAC over `slots_hash` into one constant-time decision (no slot accepted → `WRONG_RECIPIENT_KEY`; a slot wrap-opened but no candidate CEK reproduces `slots_mac` → `TAMPERED_HEADER`), then derives `payload_key` from the recovered CEK and `enc.nonce` and opens the segmented STREAM ciphertext chunk by chunk, verifying each chunk's tag before releasing that chunk's plaintext (a chunk-tag failure, truncation, trailing data, or any other chunk-layout violation → `TAMPERED_CIPHERTEXT`). On the `passphrase` path it derives the candidate CEK from the entered passphrase and the on-chain Argon2id parameters (a runtime KDF rejection → `KDF_DERIVATION_FAILED`), reads the leading 32-byte key-commitment header of the ciphertext blob, recomputes the commitment over the passphrase transcript, and compares in constant time **before** opening any chunk — a mismatch (wrong passphrase, tampered `salt` / `params` / header fields, or an envelope spliced onto a different hash claim) is indistinguishable by design and surfaces as `TAMPERED_CIPHERTEXT`; on a match it derives the passphrase-path `payload_key` and opens the STREAM identically. Fetched ciphertext is subject to the same attribution rule as any fetched bytes ([Content-address binding of fetched bytes](#content-address-binding-of-fetched-bytes)): `TAMPERED_CIPHERTEXT` — on either path — holds the blob against the record (or the supplied credential) only when the blob is **attributable**, i.e. supplied out-of-band or fetched with a verified content-address binding; the same failures over an unattributable fetched blob are `URI_PROVIDER_INTEGRITY_MISMATCH` (warning), the verifier tries the remaining URIs and gateways, and exhaustion without an attributable blob ends as `CIPHERTEXT_UNAVAILABLE`. On both paths, released chunk plaintext is **tentative** — no side effects, no acknowledgement — until the post-decryption recheck passes: after the final chunk the verifier MUST recompute every digest in `item.hashes` over the recovered plaintext and report `plaintextHashOk`. A mismatch is `URI_INTEGRITY_MISMATCH` and the record's verdict is **`failed`** (integrity class): a record whose decryption succeeds but whose plaintext-hash recheck fails MUST NOT surface a `valid` — or any "decrypted" — top-level verdict. Because every `enc`-bearing item MUST carry at least one content-hash entry, `plaintextHashOk` is always a concrete boolean.
9. **Resolve `supersedes` (optional, one hop).** When present, the verifier MAY perform a single-hop existence check of the prior transaction; it MUST NOT recurse (a DoS vector) and MUST NOT treat the pointer as an authoritative invalidation. Supersedence is an advisory pointer; the chain remains append-only and both records remain cryptographically valid.
10. **Emit the report.** The machine verdict MUST be one of `valid | pending | unverifiable | failed`. `failed` is reserved for **record-attributable** outcomes: integrity, structural, signature, Merkle-mismatch, and service-independence-violation classes, including `METADATA_NOT_FOUND` — record-attributable because the absence is proven by the integrity-bound transaction itself. Condemnation requires evidence that the record's own bytes — or bytes attributably bound to its references — actually provide; no provider misbehaviour can manufacture it. `unverifiable` is the verdict when no record-attributable error is present but a required check could not run — or could not be attributed — for network, policy, or provider-integrity reasons: the transaction could not be resolved (`TX_NOT_FOUND`, `PROVIDER_UNAVAILABLE`), no provider response survived the transaction-reference binding (`TX_INTEGRITY_MISMATCH`), or committed content or ciphertext could not be obtained, fully fetched, or attributed (`CONTENT_UNAVAILABLE`, `CONTENT_FETCH_LIMIT_EXCEEDED`, `CIPHERTEXT_UNAVAILABLE`, with `URI_PROVIDER_INTEGRITY_MISMATCH` warnings recording what indicted the providers): the record is not condemned, and the same record may verify `valid` on retry or under a different gateway configuration. Availability is additionally subject to a **commitment floor**: when content checking ran (`fetchContent` true) but availability failures — unreachable content URIs, unobtainable leaves-lists — left **no** content commitment of the record actually verified, the verdict MUST be `unverifiable`, never `valid`. For unfetchable item content this already follows from the `CONTENT_UNAVAILABLE` mapping; the floor extends the same posture to `MERKLE_LEAVES_UNAVAILABLE`, whose warning severity presumes at least one other verified content commitment — on a record whose only content commitment is the Merkle root, an unavailable leaves-list means no content commitment was checked, and the record reports `unverifiable`. A record with at least one verified content commitment retains the warning reading for an unavailable leaves-list on its remaining commitments. Integrity outcomes are untouched by the floor: attributable bytes that fail a commitment (`URI_INTEGRITY_MISMATCH`, `MERKLE_ROOT_MISMATCH`) produce `failed` regardless of what else was or was not available. The verdict maps to a four-state exit code so callers can distinguish record-attributable failures from transient operational ones without parsing the structured report: `valid` → exit 0; `failed` → exit 1; `unverifiable` → exit 2; `pending` (`INSUFFICIENT_CONFIRMATIONS`) → exit 3; verifier-host runtime failures that are not record-attributable → exit 4 and higher. The report MUST carry, at minimum: the verdict and exit code; the resolved confirmation depth alongside the threshold it was compared against; `block_time` — and, when available, `block_slot` — in the representation pinned in [Chain facts: block time and confirmation depth](#chain-facts-block-time-and-confirmation-depth); the structural-validation issue list with per-issue severity; a per-claim content-check status for every item and list commitment — checked, mismatched, or **not checked** (`fetchContent` off, availability failure, or fetch ceiling), so an unchecked claim can never masquerade as a verified one; and a complete audit trail of every outbound network call (URL, method, status, byte count, purpose) — a verifier that omits or pre-filters this trail cannot prove service-independence. The JSON Schemas under [`../schemas/`](https://github.com/cardanowall/label-309/blob/main/schemas) express the report shape for tooling.

##### Content-address binding of fetched bytes

Both fetch schemes are content-addressed, so fetched bytes can be verified against the URI itself — independently of whichever gateway served them. The binding check per scheme:

- **`ipfs://`** — recompute the CID over the fetched content: for a raw-codec CID, the multihash directly over the bytes; for a DAG-form CID (e.g. UnixFS), obtain the content in a block-verifiable form (block-by-block, or a CAR stream as in the IPFS trustless-gateway interface) and verify every block's digest against its CID along the resolved path.
- **`ar://`** — for a layer-1 Arweave transaction, validate the signed transaction header and recompute the chunk Merkle tree over the fetched bytes against its `data_root`; for an ANS-104 data item, obtain the complete item (owner, signature, tags, data), recompute the deep-hash, verify the owner signature over it, and check that the SHA-256 of the signature equals the id in the URI.

A verifier SHOULD apply the applicable binding check to every fetched byte stream. Bytes that satisfy every digest of the record's own commitment need no binding check — the record's commitment is at least as strong as the storage layer's. The check decides **attribution**, and attribution decides what a mismatch means:

- **Attributable bytes** — binding verified, or supplied out-of-band by the caller — are held against the record when they fail a commitment: item content failing a digest is `URI_INTEGRITY_MISMATCH` and a leaves-list failing its validation or root recompute is the `SCHEMA_MERKLE_LEAVES_*` / `MERKLE_ROOT_MISMATCH` family (record-attributable, verdict `failed`); an attributable ciphertext blob failing the decryption layer is the `TAMPERED_CIPHERTEXT` outcome of pipeline step 8, surfaced under the sealed-PoE single-generic-failure rule.
- **Unattributable bytes** — binding not verified, or verified and failed — indict the serving provider, never the record: `URI_PROVIDER_INTEGRITY_MISMATCH` (warning). The verifier continues with the remaining URIs and gateways; a claim left with no attributable bytes satisfying it ends in the applicable availability outcome (`CONTENT_UNAVAILABLE`, `MERKLE_LEAVES_UNAVAILABLE`, `CIPHERTEXT_UNAVAILABLE`), verdict `unverifiable` — exactly as if nothing had been fetched.

The rule exists so that a misbehaving storage gateway can degrade only availability, never the verdict — condemning a record requires evidence a gateway cannot fabricate. It is the storage-side counterpart of the transaction-reference binding of step 2. A verifier that skips the binding check loses nothing it was entitled to assert: it still reports `valid` on matching bytes (the record's own digests carry that conclusion) and `unverifiable` on garbage; what it cannot do is convert unverified garbage into a `failed` verdict. The post-decryption plaintext-hash recheck needs no attribution qualifier of its own: ciphertext that opens under the authenticated envelope is attributed by the AEAD itself, so its `URI_INTEGRITY_MISMATCH` is always record-attributable.

##### Chain facts: block time and confirmation depth

The integrity binding of pipeline step 2 makes the transaction **content** trustless: record bytes, surrounding metadata, and signatures are hash-bound to the caller-supplied transaction reference, and no explorer can alter them undetected. The binding does not extend to the **chain facts about** the transaction. Chain inclusion, block height, confirmation depth, block slot, and block time are not derivable from the transaction bytes — transaction CBOR carries no timestamp or height, and an optional validity interval bounds only when a transaction _could_ have been accepted, not when it _was_ — so each of these facts is asserted by the resolving explorer and accepted on that explorer's word. It is RECOMMENDED that verifiers resolve these facts from at least two independent explorers and surface any divergence rather than silently choosing one answer.

**Block time.** The block time of a PoE record — the time `T` in the claim "this content existed on or before `T`", wherever this document uses the phrase — is the POSIX timestamp, in integer seconds UTC, of the slot of the block that includes the transaction, sourced from the resolving explorer's block/transaction time field. The slot-to-wall-clock mapping is a chain-parameter computation the explorer performs; the verifier consumes the result and does not recompute it. Block time is therefore explorer-asserted: deployments for which it is load-bearing — legal notarisation, deadline disputes — MUST cross-check it across independent explorers. The verifier report MUST carry `block_time` in exactly this representation (integer POSIX seconds, UTC) and MAY additionally carry `block_slot`, the slot number of the including block.

**Confirmation depth.** Confirmation depth is counted in blocks: `depth = (resolving explorer's tip height) − (height of the block including the transaction) + 1`, so a transaction in the explorer's tip block has depth exactly 1. Both heights are explorer-asserted, and depth inherits the same trust posture as block time. Pipeline step 5 compares this depth against the verifier's confirmation-depth threshold.

##### Error families (Part B)

The verifier-layer codes are never emitted by the structural validator; they appear only in the verifier's report. The registry [`../registries/error-codes.json`](https://github.com/cardanowall/label-309/blob/main/registries/error-codes.json) is authoritative.

| Family                  | Representative codes                                                                                                                                                                                                                                  | Triggered by                                                                                                                                                                                                               |
| ----------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| explorer / metadata     | `TX_NOT_FOUND`, `PROVIDER_UNAVAILABLE`, `TX_INTEGRITY_MISMATCH`, `METADATA_NOT_FOUND`, `INSUFFICIENT_CONFIRMATIONS` (pending)                                                                                                                         | no consulted provider knows the requested transaction (a single provider's negative answer is not chain-authoritative); every explorer unreachable; no provider response survived the transaction-hash / `auxiliary_data_hash` binding (provider-attributable — verdict `unverifiable`); the integrity-bound transaction carries no label-309 metadata; on-chain but below the confirmation-depth threshold. |
| `SIG_*` (cryptographic) | `SIGNATURE_INVALID`, `SIGNER_KEY_UNRESOLVED`, `WALLET_ADDRESS_MISMATCH`                                                                                                                                                                               | strict-Ed25519 verification returned false; no key-resolution path yielded a 32-byte public key; a wallet-path signature's `address` does not bind to the resolved key.                                                    |
| `URI_*` / content       | `URI_INTEGRITY_MISMATCH`, `URI_PROVIDER_INTEGRITY_MISMATCH` (warning), `URI_FETCH_FAILED` (warning), `CONTENT_UNAVAILABLE`, `CONTENT_FETCH_LIMIT_EXCEEDED`, `URI_TARGET_FORBIDDEN`, `CIPHERTEXT_UNAVAILABLE`                                          | attributable fetched (or decrypted) bytes do not match the `hashes` commitment (integrity — hard, regardless of other URIs); fetched bytes mismatch but cannot be attributed to the URI's content address, indicting the serving provider; a single gateway attempt failed; every URI exhausted with no attributable committed bytes (network — claim unchecked, not condemned); a fetch aborted at the deployment's `maxFetchBytes` ceiling (network/policy); a URI scheme outside the closed fetch set; no path to obtain ciphertext for an `enc`-bearing item. |
| `MERKLE_*` / leaves     | `MERKLE_ROOT_MISMATCH`, `MERKLE_LEAVES_UNAVAILABLE` (dual), `MERKLE_UNSUPPORTED` (dual), `SCHEMA_MERKLE_LEAF_COUNT_MISMATCH`, `SCHEMA_MERKLE_LEAVES_FORMAT_UNSUPPORTED`, `SCHEMA_MERKLE_LEAVES_MALFORMED`                                          | recomputed root ≠ on-chain root; leaves-list expected but unavailable (warning beside a verified content commitment; error → `unverifiable` when no content commitment of the record was verified — see the severity contract); verifier does not implement Merkle-fold; leaf-count disagreement (document-internal or against the on-chain commitment); a leaves-list container of an unsupported `format`; bytes that are not the leaves-list container.                          |
| `ENC_*` / decrypt       | `WRONG_DECRYPTION_INPUT_SHAPE`, `WRONG_RECIPIENT_KEY`, `TAMPERED_HEADER`, `TAMPERED_CIPHERTEXT`, `KDF_DERIVATION_FAILED`, `ENC_PASSPHRASE_UNNORMALIZABLE`, `ENC_PASSPHRASE_EMPTY`                                                                     | the keyring holds no credential of the shape the item's on-wire key path requires; every slot rejected the key; slot-set MAC mismatch; content AEAD tag failure (or wrong passphrase); Argon2id rejected the parameters at runtime; a supplied passphrase carries a codepoint unassigned in Unicode 16.0; a supplied passphrase normalizes to the empty string (see [Passphrase normalization profile](#passphrase-normalization-profile)). |
| profile / egress        | `OUT_OF_PROFILE_SKIPPED` (dual), `SERVICE_INDEPENDENCE_VIOLATION`                                                                                                                                                                                     | a verifier reading a v1-schema field outside its declared profile (info in render mode, error in strict end-to-end mode); an outbound call to a `denyHosts` entry.                                                         |

**Severity contract.** A `valid` verdict MUST NOT be reported when any `error`-severity code is present. A record MAY be valid with a non-empty `warnings` and/or `info` list. `INSUFFICIENT_CONFIRMATIONS` maps to `pending`; the network/policy codes (`TX_NOT_FOUND`, `PROVIDER_UNAVAILABLE`, `CONTENT_UNAVAILABLE`, `CONTENT_FETCH_LIMIT_EXCEEDED`, `CIPHERTEXT_UNAVAILABLE`) — and `TX_INTEGRITY_MISMATCH`, whose mismatch is provable against the providers rather than the record — map to `unverifiable`: error-severity in the issue list (they block a `valid` verdict) but not record-attributable, so they never produce `failed`. `URI_PROVIDER_INTEGRITY_MISMATCH` is a per-fetch warning under the same principle — it records that a provider served unattributable mismatching bytes and never condemns the record. Three codes (`ENC_UNSUPPORTED`, `MERKLE_UNSUPPORTED`, `OUT_OF_PROFILE_SKIPPED`) carry dual severity: their default reading is `info`, and the strict context promotes them to `error` — the recipient role / strict sealed-crypto mode for `ENC_UNSUPPORTED`, the merkle-only escalation for `MERKLE_UNSUPPORTED`, strict end-to-end mode for `OUT_OF_PROFILE_SKIPPED`. `MERKLE_LEAVES_UNAVAILABLE` is likewise context-dependent: `warning` when at least one other content commitment of the record was verified, escalating to `error` (network class, verdict `unverifiable`) when the unavailability leaves the record with no verified content commitment — the commitment floor of pipeline step 10. Neither layer is permitted to soften an `error` into a `warning` to make a record pass.

##### Profiles

Conformance profiles are a property of the verifier layer, not of the structural parser — the parser always validates the full v1 grammar uniformly. A verifier advertises which profile it implements:

- **core** — structural validation plus on-chain content-hash checks; no signature verification, no Merkle-fold, no decryption.
- **signed** — core plus record-signature verification.
- **sealed** — signed plus the structural surface of the encryption envelope.
- **recipient-sealed** — sealed plus sealed-PoE decryption with held decryption credentials (recipient KEM private keys and/or passphrases).

A verifier reading a v1-schema field outside its declared profile (for example, a core verifier encountering `enc` or `sigs`) emits `OUT_OF_PROFILE_SKIPPED` per affected field and still reports the hash claim; the record is NOT marked invalid solely because the verifier does not implement a profile extension. The registry of profiles and the per-profile algorithm sets are described in [Algorithm registries and conformance profiles](#algorithm-registries-and-conformance-profiles).

#### Service independence

The central property of this CIP is that **a proof verifies with no operator server in the loop**. A conformant verifier MUST work using only the operator-configured public Cardano / Arweave / IPFS gateway chains; it MUST NOT embed any operator's domain in its default configuration, and every operator domain MUST be deny-able via `denyHosts` without breaking verification of any conformant record. All record identity comes from the on-chain transaction hash; all signer identity comes from the in-signature `kid` or the inline `cose_key`. There is no proprietary off-chain index, no proprietary record id, and no authentication step.

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

This CIP's security claims hold against the following adversaries. Each row lists
what the adversary can and cannot achieve against the on-wire format alone.

| Adversary                                  | Capabilities                                                                                                                              | Cannot                                                                                                                                                                                                                                                                                                                                                                                                            | Can                                                                                                                                                                                                                                                                                                                                                      |
| ------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Network (passive or active MitM)**       | Observes and modifies traffic between any verifier and the Cardano / Arweave / IPFS gateways it consults.                                 | Decrypt sealed-PoE ciphertext, recover any master seed or recipient private key, or forge a `COSE_Sign1` signature. The content layer is the per-chunk-authenticated `chacha20-poly1305-stream64k` STREAM format and the per-slot wrap is ChaCha20-Poly1305 under a KEM-derived KEK, so payload eavesdropping yields nothing; per-record, per-slot ephemeral KEM material defeats traffic-analysis correlation.                                                                                     | Observe transaction identifiers, request timing, and fetch volume — metadata that the format does not attempt to hide.                                                                                                                                                                                                                                   |
| **Chain observer (permanent global read)** | Full read of every Cardano transaction, forever.                                                                                          | Decrypt the sealed-PoE ciphertext referenced by a content-addressed URI: the ciphertext lives off-chain, and even with both halves the observer lacks the recipient KEM private key and the per-record KEK derived via HKDF-SHA-256.                                                                                                                                                                              | See every record's on-chain metadata: content hashes, signer Ed25519 public keys, `COSE_Sign1` signatures, and slot count. An author signing with a stake-linked CIP-30 wallet key accepts that this binding is permanent and public (see [Privacy](#privacy)).                                                                                          |
| **Off-chain storage observer**             | Full read of every sealed-PoE ciphertext at its content-addressed `ar://` / `ipfs://` URI, forever.                                       | Decrypt the ciphertext — it is encrypted in the `chacha20-poly1305-stream64k` per-chunk-authenticated STREAM format under a `payload_key` derived from a CEK that is itself wrapped under KEM-derived KEKs, and the CEK is committed to the full header context by the CEK-keyed `slots_mac` over the slots transcript (slots path) or by the in-ciphertext commitment header (passphrase path); see [Sealed PoE: multi-recipient encryption](#sealed-poe-multi-recipient-encryption). Enumerate recipients: recipient public keys never appear on the wire.                                                                                                                      | See the ciphertext bytes and their length.                                                                                                                                                                                                                                                                                                               |
| **Cardano gateway (malicious indexer)**    | Returns false data to a verifier: altered or synthetic transaction bytes, a forged confirmation count or block time, a withheld reorg, a false "transaction not found". | Alter, substitute, or truncate any byte of the transaction or its metadata: the verifier recomputes `blake2b-256` over the fetched transaction body against the requested transaction hash and verifies the body's `auxiliary_data_hash` over the fetched auxiliary data, so serving different content requires a blake2b-256 second preimage (anything less surfaces as `TX_INTEGRITY_MISMATCH`). Forge a record that passes signature verification — the gateway does not hold the signer's Ed25519 private key. Induce a verifier to accept a record below its locally configured confirmation threshold (the threshold is verifier policy, not a normative wire requirement). | Misstate the chain facts that are not derivable from transaction bytes — inclusion, block height and therefore confirmation depth, block slot, block time — withhold a reorg, falsely answer "not found", or delay verification with slow or incomplete responses: denial and misdating shapes, not content forgery. A verifier that resolves chain facts from two or more independent explorers and aborts on divergence escalates "single malicious gateway" to "collusion across providers".                                                                                    |
| **Malicious recipient**                    | Holds a recipient KEM private key; by construction decrypts every sealed PoE addressed to a slot wrapped under that key.                  | Decrypt sealed PoE addressed to a _different_ recipient's key — other slots in the same record are independently wrapped and fail closed under the wrong private key. Retroactively insert itself as a recipient on a published record — `enc.slots` is covered by `slots_mac` and, if the record is signed, by the `COSE_Sign1`; tampering invalidates one or the other.                                         | Do anything a legitimate recipient can do with the recovered plaintext, including leaking it. Sealed PoE has **no recipient forward secrecy by design**: once a record is sealed to a long-term recipient key, the holder of the matching private key can decrypt forever. This is a property of public-key encryption to a long-term key, not a defect. |
| **Quantum-capable adversary (future CRQC)** | Archives today's permanent public artifacts — on-chain envelopes, signer public keys, content-addressed ciphertext — and applies a cryptographically relevant quantum computer to them at some future date.                                | Break the content-hash claim, the `mlkem768x25519` confidentiality (while ML-KEM-768 holds), the `slots_mac` commitment, or the symmetric layer — every one is Grover-bounded or post-quantum by construction (see [Quantum adversaries and per-claim durability](#quantum-adversaries-and-per-claim-durability)).                                                                                                | Retroactively decrypt every record sealed under `x25519` alone, and forge Ed25519 signatures from the CRQC epoch onward. The per-claim durability table below is the authoritative breakdown; producer-side guidance follows from it.                                                                                                                    |

### Quantum adversaries and per-claim durability

A PoE record outlives cryptographic eras: the chain is append-only, the
ciphertext URI is permanent, and nothing published can be recalled when a
cryptographically relevant quantum computer (CRQC) arrives. Each claim a record
makes therefore has its own quantum durability, and the differences are stark:

| Claim                                          | Primitive                                          | Durability against a CRQC                                                                                                                                                                                                                                                                                                                |
| ---------------------------------------------- | -------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Content-hash claim ("existed on or before `T`") | SHA-256 / BLAKE2b-256                              | **Durable.** Generic quantum attacks on hash functions are Grover-bounded: a second preimage against a 256-bit digest costs on the order of 2^128 quantum work. The core proof-of-existence claim of every record — sealed or open, signed or unsigned — survives the quantum transition.                                              |
| Sealed-PoE confidentiality, `mlkem768x25519`   | X-Wing (ML-KEM-768 + X25519)                       | **Durable while ML-KEM-768 holds.** The combiner preserves the stronger component: a CRQC removes the X25519 contribution, and the CEK's confidentiality reduces to ML-KEM-768's post-quantum IND-CCA security.                                                                                                                          |
| Sealed-PoE confidentiality, `x25519`           | X25519 ECDH                                        | **Falls to the first CRQC, retroactively.** Shor's algorithm recovers an X25519 private key from its public key. Every `x25519`-sealed record ever published becomes decryptable by an adversary holding the recipient's circulated public key — see [Harvest-now, decrypt-later and the `x25519` KEM](#harvest-now-decrypt-later-and-the-x25519-kem). |
| Record authorship (`sigs[]`)                   | Ed25519                                            | **Forgeable from the CRQC epoch onward.** Signer public keys are on chain forever, and Shor's algorithm recovers the private key from the public key. What an already-anchored signature still proves is governed by its block time — see [Ed25519 authorship across the quantum transition](#ed25519-authorship-across-the-quantum-transition). |
| Symmetric and commitment layer                 | ChaCha20-Poly1305, HKDF-SHA-256, HMAC-SHA-256      | **Durable.** 256-bit keys and outputs are Grover-bounded to ~128-bit quantum security; the wrap, the STREAM content format, the `slots_mac` commitment, and every key derivation in this CIP retain an ample margin.                                                                                                                     |

The passphrase path carries no public-key material in its key-delivery path, so
a quantum adversary gains at most a Grover-style speed-up of offline guessing
against the Argon2id-stretched passphrase; passphrase entropy remains the only
barrier, quantum or not.

**The hybrid guarantee is bounded by ML-KEM-768, not by the symmetric layer.**
HKDF-SHA-256, HMAC-SHA-256, and ChaCha20-Poly1305 sit far above the post-quantum
security of any KEM in the registry, so in the post-CRQC setting the binding
constraint of a `mlkem768x25519` record is exactly ML-KEM-768's IND-CCA
security. The X25519 half contributes the **classical floor** — protection
against a present-day cryptanalytic break of ML-KEM-768 — which is why the
hybrid, not standalone ML-KEM, is the v1 construction.

**Leaf-key isolation under derivation.** The three long-term keypairs are
independent one-way HKDF-SHA-256 expansions of the master seed under distinct
`info` strings (see [Seed and key derivation](#seed-and-key-derivation)). A CRQC
that recovers the X25519 private scalar from a recipient's circulated classical
public key has obtained one HKDF output; recovering the master seed from it is a
preimage search against HKDF-SHA-256 (Grover-bounded, ~2^128 quantum work), and
the `mlkem768x25519` decapsulation seed is a sibling expansion with no
derivational relationship the adversary can traverse. A classical-key compromise
therefore strands at the classical key: neither the master seed nor the hybrid
identity falls with it. The X25519 public key embedded inside the X-Wing public
key is not an additional exposure — recovering its scalar is exactly the event
already priced into "durable while ML-KEM-768 holds".

**Algorithm agility protects future records only.** Registry additions are
additive and change nothing about bytes already on chain: a record sealed under
`x25519` is `x25519` forever, and a record signed only with Ed25519 carries only
that signature forever. The agility mechanism (see
[Algorithm agility: the additive-only rule](#algorithm-agility-the-additive-only-rule))
is how *new* records adopt stronger primitives; it is not a remediation channel
for published ones. Producer-side defaults must therefore be conservative now,
not after a quantum event.

**Why ML-KEM-768, and the Category-5 path.** The hybrid's lattice parameter set
is ML-KEM-768 (NIST security Category 3) rather than ML-KEM-1024 (Category 5)
for three reasons: the parameter set is fixed by X-Wing, which is defined over
ML-KEM-768 only; it is the parameter set deployed as the hybrid default across
the wider ecosystem (notably the TLS X25519 + ML-KEM-768 hybrid), concentrating
implementation availability and cryptanalytic review on the exact construction
this CIP uses; and its 1216-byte public key and 1120-byte ciphertext fit the
per-slot on-chain byte budget of metadata-carried envelopes. A deployment that
requires Category-5 margins is not stranded: a higher-category KEM enters the
KEM registry as an additive identifier under the same `enc.scheme` — no schema
change, no version bump — per the additive-only rule.

### Harvest-now, decrypt-later and the `x25519` KEM

Sealed PoE is an unusually favourable target for a harvest-now, decrypt-later
adversary — one who archives ciphertext today and decrypts when a CRQC exists.
Nothing needs to be intercepted: the `enc` envelope sits on a permanent public
ledger and the ciphertext at a permanent content-addressed URI, both
world-readable by design. The adversary's archive is the system's normal
operating state.

For a record sealed under `x25519`, the entire key-delivery path is
elliptic-curve: a CRQC that recovers the recipient's X25519 private key from
their circulated public key gains exactly the legitimate recipient's capability
and decrypts every `x25519` record ever sealed to that key. There is no
mitigation after publication — sealed PoE has no recipient forward secrecy by
design, and the chain preserves the envelope forever.

Sealing with `x25519` is therefore **NOT RECOMMENDED** for content whose
confidentiality must outlive the elliptic-curve era. The identifier remains
registered, and verifier-side support remains mandatory, because the recipient —
not the sender — chooses which keys to publish, and some recipients publish an
X25519 key only; a sender who seals classically is accepting the
harvest-now, decrypt-later exposure on the content's behalf. Producer interfaces
SHOULD surface a harvest-now, decrypt-later notice when `x25519` is selected for
sealing: the consequence of the choice is invisible in the published artifact
and irreversible after publication.

This exposure is a confidentiality property only. It does not weaken the
record's hash claim, and it does not apply to the `slots_mac` commitment, whose
relevant adversary acts at sealing time (see [Slot-set MAC](#slot-set-mac)).

### Ed25519 authorship across the quantum transition

Every signed record publishes its signer's Ed25519 public key on chain forever,
and Shor's algorithm recovers an Ed25519 private key from its public key. From
the epoch at which a CRQC exists, a freshly produced Ed25519 signature can have
been made by anyone, not only the original key holder.

Block time gives existing signatures **epoch semantics**. A signature anchored
at block time `T`, where `T` precedes the CRQC epoch, remains strong authorship
evidence indefinitely: at `T`, only the private-key holder could have produced
it, and the chain witnesses that it existed then. The same signature shape
anchored after the CRQC epoch proves nothing about authorship — the verifier's
cryptographic verdict is unchanged, but the evidentiary weight a consumer should
attach to it collapses. Verifier reports carry the block time precisely so
consumers can make this assessment; the wire format does not (and cannot)
encode where the CRQC epoch falls.

The forward path is dual-signing, and the format already accommodates it. The
signature registry reserves the post-quantum identifiers `ml-dsa-65` and
`slh-dsa-sha2-128s` (see
[Algorithm agility: the additive-only rule](#algorithm-agility-the-additive-only-rule));
registering one is an additive change. Once a post-quantum signature identifier
is registered, producers for whom the authorship claim must outlive the
elliptic-curve era are RECOMMENDED to dual-sign: one Ed25519 `sigs[]` entry and
one post-quantum entry over the same record body. Dual-signing is non-breaking
for older verifiers by construction — `sigs[]` is plural, and an unrecognised
signature algorithm surfaces as `SIGNATURE_UNSUPPORTED` at info severity without
failing the record — so an older verifier verifies the Ed25519 entry and the
content claim exactly as before, while an updated verifier verifies both.

### X-Wing revision pinning

The identifier `mlkem768x25519` denotes the byte behaviour of X-Wing exactly as
specified in
[draft-connolly-cfrg-xwing-kem-10](https://datatracker.ietf.org/doc/draft-connolly-cfrg-xwing-kem/10/):
the 32-byte decapsulation seed and its SHAKE-256 expansion, the 1216-byte public
key, the 1120-byte ciphertext, and the SHA3-256 combiner over
`ss_M ‖ ss_X ‖ ct_X ‖ pk_X ‖ label`. The identifier is **frozen** on that
behaviour. If a later revision of the draft — or an eventual RFC — changes any
byte behaviour, the changed construction enters the KEM registry under a **new**
identifier per the additive-only rule; `mlkem768x25519` never silently tracks a
moving document.

Two consequences follow. First, the pinned conformance vectors under
[`../conformance/`](https://github.com/cardanowall/label-309/blob/main/conformance), not the Internet-Draft, are authoritative
in any byte-level dispute: an implementation that reproduces the vectors is
conformant. Second, because Internet-Drafts expire, the complete
keygen/encapsulate/decapsulate behaviour is reproduced normatively in
[X-Wing construction reference](#x-wing-construction-reference), so the
construction remains implementable from this document alone.

The sealed-PoE construction additionally does not lean on X-Wing's internal
bindings. X-Wing's combiner already binds the X25519 ciphertext and recipient
public key; the per-slot KEK salt
`SHA-256("cardano-poe-xwing-kek-salt-v1" ‖ enc.nonce ‖ kem_ct ‖ pub_R)` re-binds
the slot's full wire bytes and the envelope-unique nonce **outside** the KEM, as
defence in depth — the security argument holds X-Wing as a black-box IND-CCA KEM
(see [Slot construction (sender)](#slot-construction-sender)).

### Standalone verifiability and zero server custody

Two service-level invariants underwrite the format's trust model and are
testable against the on-wire bytes alone.

- **Standalone verifiability.** A verifier MUST be able to validate any PoE
  record using only public Cardano + Arweave + IPFS gateways and, for a
  recipient verifier, the recipient's own decryption material — without
  contacting any issuer-operated domain. A consumer holding the transaction
  reference and a Cardano gateway URL MUST be able to verify a proof even if the
  publisher's service no longer exists. Verification of the on-chain commitment
  is independent of decryption: a verifier MUST emit a structural verdict before
  any decryption is attempted.
- **Zero server custody.** No publishing service holds private cryptographic
  material that a verifier must trust. Because this CIP has no issuer field, any
  wallet MAY publish a conformant record; compromise of a publisher's signing
  key lets the attacker do only what any Cardano holder can already do — publish
  further conformant records — and is therefore not a privilege escalation
  against any user. No gateway's bytes are taken on trust either: the verifier
  binds every fetched transaction to the requested transaction hash and to the
  body's `auxiliary_data_hash` (see
  [Structural validation, verifier roles, and error codes](#structural-validation-verifier-roles-and-error-codes)),
  so no single provider can alter record content undetected. What a single
  provider can still misstate are the chain facts not derivable from those
  bytes — inclusion, block height and depth, block time; a verifier that
  resolves those facts from two or more independent providers and aborts on
  divergence raises that residual bar to collusion across providers.

### Hash collision and second preimage

This CIP requires content-hash algorithms with at least 128-bit collision
resistance and at least 256-bit second-preimage resistance. `sha2-256` and
`blake2b-256` (registered in [`../registries/hash-algorithms.json`](https://github.com/cardanowall/label-309/blob/main/registries/hash-algorithms.json),
both 32-byte digests) qualify; the authoritative threat — a second preimage at
`2^256` classical / `2^128` Grover — is infeasible in both settings. A record
that opts into the multi-hash pattern (`sha2-256` _and_ `blake2b-256` in the
same `hashes` map) further requires a concurrent break of two independent design
families. If a registered algorithm is later weakened, a successor revision MUST
remove the identifier; verifiers SHOULD then mark dependent records "unreliable"
without erasing the underlying claim, because the chain is append-only.

### Merkle list commitment: second preimage and off-chain backup

The `rfc9162-sha256` list-commitment construction (see
[`../registries/merkle-commitment-algorithms.json`](https://github.com/cardanowall/label-309/blob/main/registries/merkle-commitment-algorithms.json))
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
prepended to the signing input, binds the signature to its role. A
future Cardano metadata schema that happens to share the body shape cannot reuse
a PoE signature against itself: the replayer's signing input would carry a
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

### Sender authenticity of sealed PoE

The sealed-PoE construction authenticates **delivery to recipients**, never
**origin**. Three properties follow from the construction and are stated plainly
so that applications do not assume otherwise:

- **Decryption authenticates nothing about origin.** Sealing to a recipient
  requires only the recipient's public key — public by virtue of being
  circulated. A successful trial-decrypt plus plaintext-hash recheck proves
  "this envelope was sealed for my key, and the plaintext matches the on-chain
  commitment"; it proves nothing about who sealed it. The KEM path is
  sender-anonymous by design — no sender key material appears on the wire (see
  [Anonymity of unsigned sealed PoE](#anonymity-of-unsigned-sealed-poe)).
- **Signature stripping.** A record-level signature covers the record body with
  `sigs` removed, so the signature itself is detachable from the bytes it
  covers. Anyone may take a published signed record, drop its `sigs[]`, and
  republish the body in a new transaction as an unsigned record. The original
  record is untouched, but a stripped copy circulates with the same content
  claim and no authorship; the absence of a signature on one record is never
  evidence that the content's author did not sign elsewhere.
- **Recipient rewrap.** `slots_mac` is CEK-keyed, and every legitimate recipient
  recovers the CEK. A recipient — or any party who obtains the CEK — can
  therefore construct a **sibling envelope** around the same CEK and ciphertext:
  a different recipient set, fresh slots, a recomputed `slots_mac`, the same
  `hashes`. The sibling is valid in every structural and cryptographic respect
  and indistinguishable on the wire from a sender-produced unsigned envelope.
  (For a signed record the signature covers `enc`, so a rewrapped sibling cannot
  carry the original signature — it can only circulate unsigned.)

The normative consequence: an application for which the recipient set, the URI
set, or any other expression of **sender intent** is authoritative MUST require
record-level signatures by policy and MUST verify them. Absent a verified
signature, the only claims a sealed record supports are the timestamped hash
commitment and "decryptable by whoever holds a matching private key".

### Cross-record envelope replay

For an unsigned record, every input to a valid sealed item is public: the
`hashes` map, the `enc` envelope (including `slots_mac`), and the `uris[]`. A
third party can therefore copy a published item **verbatim** into a new record
and submit it in a later transaction. The replayed item passes every structural
and on-chain check — `slots_mac` binds the envelope to the item's `hashes`,
which the replayer copies unchanged — and the original recipients' keys still
match it. This is the sealed analogue of the identical-body case in
[Signature replay](#signature-replay) and is inherent to a format whose unsigned
records carry no origin binding.

What replay cannot do: alter the content (the CEK and the plaintext hashes
commit to it), redirect the envelope to a different hash claim (the splice fails
the on-chain match), rewrap to new recipients without holding the CEK (see the
rewrap property above), or **backdate** — a replayed record carries a later
block time, so the earliest transaction carrying the item remains the one whose
timestamp has evidentiary weight.

Applications that present sealed records as incoming deliveries MUST gate on
the end of the pipeline, not the start: a record MUST NOT be surfaced as
**received content** until its post-decryption plaintext-hash recheck has
passed (see
[Plaintext-hash binding](#plaintext-hash-binding-and-the-sender-identity-verdict-split)).
On observing more than one record carrying an identical envelope for the same
plaintext claim, such an application SHOULD collapse the duplicates to the
record with the earliest block time, surfacing later copies as duplicates of it
rather than as new deliveries.

### Pre-decryption structural validation

A multi-recipient sealed-PoE record carries an unauthenticated structure — the
`slots` array — that is parsed before any cryptographic primitive is invoked. An
adversary who could submit malformed records and observe which slot's processing
fails first — through a typed error, a crash, or resource exhaustion — could in
principle learn which slot a given recipient occupies, partially defeating the
hidden-recipient property. Conformant verifiers and trial-decrypt agents MUST
therefore validate **all** structural length constraints **before** invoking any
KEM, KDF, or AEAD primitive:

- `slots` array length ≥ 1;
- the KEM-discriminated per-slot encapsulation length — for `x25519`,
  `slot.epk` length `== 32`; for `mlkem768x25519`, `slot.kem_ct`
  length `== 1120`;
- within one `slots[]`, encapsulation material is distinct — all `epk` values
  differ for `x25519`, all `kem_ct` values differ for `mlkem768x25519`;
- each `slot.wrap` length `== 48` (32-byte CEK + 16-byte ChaCha20-Poly1305 tag);
- `slots_mac` length `== 32`;
- the slot count and the decoded-`enc`-envelope size are within the verifier's
  deployment-pinned resource bounds (reference values in
  [Recipient decryption (trial-decrypt)](#recipient-decryption-trial-decrypt)).

Length mismatches MUST emit the typed structural errors `ENC_SLOTS_EMPTY`,
`KEM_EPK_LENGTH_MISMATCH` / `KEM_CT_LENGTH_MISMATCH`, `WRAP_LENGTH_MISMATCH`, and
`ENC_SLOTS_MAC_INVALID_LENGTH`; a within-`slots[]` duplicate emits
`ENC_SLOTS_DUPLICATE_KEM_MATERIAL`; a slot count or decoded-envelope size above
the resource bounds emits `ENC_SLOTS_TOO_MANY` / `ENC_ENVELOPE_TOO_LARGE` (see
[`../registries/error-codes.json`](https://github.com/cardanowall/label-309/blob/main/registries/error-codes.json)) — with no
length-dependent branch reaching the cryptographic primitives. These resource
bounds are deployment-pinned reference values, not wire fields; they sit far above
the per-record byte budget the producer enforces before submission and ultimately
the Cardano maximum transaction size, so a conformant record never trips them. The
structural validator and the recipient verifier apply the identical bounds before
invoking any primitive.

### Partitioning-oracle resistance

Multi-recipient encryption whose acceptance test is a non-committing AEAD tag is
the setting of partitioning-oracle attacks
([Len–Grubbs–Ristenpart, USENIX Security 2021](https://www.usenix.org/conference/usenixsecurity21/presentation/len)):
an adversary crafts a single ciphertext that decrypts under many candidate keys
at once, submits it to an accept/reject oracle, and partitions the candidate key
space with every query — devastating when the keys derive from low-entropy
secrets. The two key-delivery paths close this oracle differently.

**Slots path: committing acceptance.** A slot is never accepted on its wrap's
Poly1305 tag alone — the per-slot ChaCha20-Poly1305 wrap is not a committing
AEAD and is not asked to be one. Acceptance requires the candidate CEK to
reproduce the CEK-keyed `slots_mac` over the slots transcript, folded into the
same per-slot decision (`kem_ok AND open_ok AND mac_ok`; see
[Recipient decryption (trial-decrypt)](#recipient-decryption-trial-decrypt)). An
envelope accepted under two distinct CEKs would be exactly the multi-key
collision in the HKDF-then-HMAC-SHA-256 commitment that the
[Slot-set commitment assumption](#slot-set-commitment-assumption) rules out at
the ~2^128 level. Independently, the per-slot KEKs derive from fresh KEM shared
secrets — high-entropy values no oracle query can enumerate — so the slots path
offers a partitioning adversary no searchable key space even before the
committing check applies.

**Passphrase path: committing acceptance plus a minimised oracle surface.** The
passphrase is precisely the low-entropy secret partitioning oracles exploit, and
the defence is layered. Acceptance is gated on the in-ciphertext key
commitment — an HMAC-SHA-256 over the passphrase transcript under a CEK-derived
key, verified in constant time before any STREAM chunk is opened (see
[Passphrase path](#passphrase-path)) — a committing check, not an AEAD tag. And
the testable surface is kept off the permanent ledger: the commitment lives only
inside the ciphertext blob, so the chain carries nothing a candidate passphrase
can be tested against. A **withheld-ciphertext record is therefore not
offline-guessable at all**: a passphrase record whose ciphertext is never
published, or is shared only through a private channel, exposes no guessable
material on chain — the salt and Argon2id parameters alone admit no test — and
its passphrase cannot be attacked until the blob itself is obtained.

What the construction cannot remove is an oracle a deployment builds on top of
it. Producers and deployments MUST NOT expose an automated or remote
passphrase-decryption oracle — any interface that accepts candidate passphrases
for a sealed record and answers accept/reject, or answers measurably
differently — because an online oracle reintroduces exactly the query surface
the format keeps off the chain. Passphrase decryption is a local,
recipient-side operation; rate-unlimited remote testing of a record's
passphrase is a deployment defect, not a wire-format property.

### Constant-time trial decryption

A recipient verifier decrypts a sealed PoE by trial-decapsulating each slot with
its private key. To preserve the hidden-recipient property, recipient decryption
MUST be constant-time across all slots within each private key's pass — every
slot processed, no early break, constant per-slot work: the time to process the
slot loop MUST NOT reveal which slot — if any — that key unwraps. The
`slots` array is published in CSPRNG-shuffled order, so wire position carries no
"primary recipient first" information; combined with the constant-time pass,
slot-level timing reveals neither the recipient's identity nor its position.
Byte comparisons on `slots_mac`, on the passphrase commitment header, and on
AEAD/MAC tags MUST likewise be constant-time; a data-dependent comparison loop
on any of these surfaces is a timing oracle and is non-conformant. What
end-to-end timing is permitted to reveal — the recipient-versus-non-recipient
distinction — is treated in
[Recipient-match timing and feed scanning](#recipient-match-timing-and-feed-scanning).

On managed runtimes the across-slots guarantee is necessarily **best-effort**.
JIT-compiled and garbage-collected runtimes can recompile, cache, or pause in
data-dependent ways the implementation cannot control, so constant-time
discipline in source code does not extend to a hard guarantee at the hardware
boundary. An implementation on such a runtime MUST still structure its own code
constant-time — fixed iteration counts, branchless selection, constant-time
comparison primitives; the requirement is not waived — and SHOULD document that
the guarantee extends only down to the runtime. Deployments whose threat model
includes a co-located timing adversary SHOULD prefer implementations backed by
native constant-time primitives.

### Recipient-match timing and feed scanning

The constant-time requirement above is scoped to the slot loop; it is
deliberately not extended to the whole pipeline. A verifier MAY return at the
no-match check before fetching or decrypting any content (see
[Recipient decryption (trial-decrypt)](#recipient-decryption-trial-decrypt)):
mandating a dummy content decryption for every non-recipient would impose
content-scale cost on every scan of every record. End-to-end timing therefore
distinguishes a recipient from a non-recipient — a non-recipient stops after the
slot pass, a recipient proceeds to ciphertext fetch and STREAM decryption — and
this CIP claims no timing indistinguishability between those two outcomes.

Feed-scanning deployments amplify that signal. A consumer that trial-decrypts
every record in a public feed and fetches ciphertext only on a match exhibits an
observable per-record profile: to a network observer or a storage gateway, the
ciphertext fetch itself announces "this scanner's key matched this record",
turning the permitted timing difference into an explicit network event
correlated with a recipient identity. Such deployments SHOULD scan on a
constant schedule decoupled from record arrival times, SHOULD decouple
ciphertext fetching from match time — deferring or batching fetches rather than
fetching at the moment of match — and SHOULD avoid issuing match-triggered
fetches from a network identity linkable to the scanning key's owner.

### Slot-set commitment assumption

The slot-set MAC is what makes the recovered CEK a **commitment** to the
envelope the recipient matched. The slots transcript binds the cross-KEM header
fields (`scheme`, `path`, `aead`, `kem`, `nonce`), the shuffled slot set, and —
through `hashes_hash` — the item's plaintext-hash claim, and the MAC over it is
checked inside every slot's acceptance decision (see
[Recipient decryption (trial-decrypt)](#recipient-decryption-trial-decrypt)): a
malicious sender cannot construct two distinct transcripts — two slot sets, two
header configurations, or two hash claims — that a single recipient accepts
under matching CEKs as "theirs". The property required here is
**restricted key commitment for the envelope CEK** in the sense of
[RFC 9771](https://www.rfc-editor.org/rfc/rfc9771) — the recovered CEK binds to a
single slots transcript — **not** a full committing AEAD over arbitrary inputs. This
property rests on the multi-key collision resistance of the map

```
CEK ↦ HMAC-SHA-256( HKDF-SHA-256(CEK, info="cardano-poe-slots-mac-v1"), slots_hash )
```

for **adversarially chosen** CEKs and transcripts. Because the adversary controls
both the CEK and the transcript, the relevant bound is a generic-collision bound:
finding two `(CEK, transcript)` pairs that produce the same `slots_mac` is a
~128-bit search (the birthday bound on a 256-bit output), **not** the 256-bit
second-preimage level. A 128-bit generic-collision margin is the security level
this commitment relies on, and is adequate for the threat model.

Pre-hashing the transcript to `slots_hash` before the HMAC does not weaken this:
`slots_hash` is a collision-resistant SHA-256 digest of the full transcript, so a
`slots_mac` collision implies either a `slots_hash` collision (an SHA-256
collision) or a collision of the keyed HMAC over equal `slots_hash`, both at the
~128-bit level. Tamper-evidence of the transcript itself therefore inherits
SHA-256's ~2^128 collision bound: any change to the committed header fields or slot
bytes alters `slots_hash`, and forging an unchanged `slots_hash` over a different
transcript is exactly that ~2^128 collision search. The per-slot `wrap` AEAD
therefore need **not** be a committing AEAD: the commitment is supplied by
`slots_mac`, not by the wrap, so a non-committing `wrap` (the default
ChaCha20-Poly1305) is sound here.

The adversary for this bound acts at **sealing time** — the colliding pair must
be found before publication — so harvest-now, decrypt-later cost models do not
apply to the commitment, and the fixed 32-byte HKDF-derived HMAC key
structurally excludes the over-block-length HMAC key ambiguity (see the
"Why 32 bytes is enough" analysis in [Slot-set MAC](#slot-set-mac), with which
this section is aligned).

### Recipient-string transport integrity

Recipient public keys travel out-of-band as Bech32 strings (see
[Recipient public-key and secret encodings](#recipient-public-key-and-secret-encodings)),
and the hybrid string is far outside the envelope the Bech32 checksum was
designed for. The [BIP-173](https://github.com/bitcoin/bips/blob/master/bip-0173.mediawiki)
BCH checksum guarantees detection of any error pattern of up to four character
substitutions only for strings up to 90 characters; the 1960-character
`age1pqc1…` string is beyond that design length, where the guarantee degrades to
probabilistic detection — a random corruption still fails the checksum with
probability ≈ 1 − 2^−30, but small error patterns are no longer guaranteed to be
caught.

Two rules compensate. Implementations MUST decode a recipient string to exactly
the registered payload length — 32 bytes for `age`, 1216 bytes for `age1pqc` —
and reject any other decoded length, eliminating truncation and extension shapes
regardless of checksum behaviour. And because a corrupted-but-checksum-passing
string yields a well-formed key that no party holds — content sealed to it is
sealed to nobody, a silent delivery failure discovered only when no recipient
can decrypt — senders SHOULD confirm a recipient string against an out-of-band
fingerprint (a short digest of the decoded public-key bytes) before first use.
The fingerprint check also covers wholesale substitution of the recipient string
in transit, which no checksum addresses; key provenance remains the sender's
trust decision (see
[Recipient public-key discovery](#recipient-public-key-discovery-out-of-scope-non-normative)).

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
- **No recipient public key on the wire.** Recipient public keys never appear in
  the record; an observer with no candidate keys learns only `slots.length`, the
  KEM family (`enc.kem`), and the sealed-vs-open distinction — never the recipient
  keys themselves.
- **No descriptive fields.** No filename, MIME type, language tag, or size field
  is on the wire (see [Privacy](#privacy)); nothing constrains who plausibly
  authored the record.

**Recipient anonymity is a per-KEM property, claimed only for `x25519`.** The
stronger claim — that an adversary who *holds a set of candidate recipient public
keys* cannot test whether a given slot is addressed to one of them — depends on
the KEM, and this CIP claims it only for the classical path:

- **`x25519` (key-private).** The per-slot encapsulation is a fresh ephemeral
  public key `slot.epk` that is statistically independent of the recipient key.
  An adversary holding candidate recipient public keys cannot, from `slot.epk` and
  `slot.wrap` alone, decide which candidate (if any) the slot targets without the
  matching private key. The classical path is therefore key-private.
- **`mlkem768x25519` (not claimed).** Recipient anonymity against an adversary
  holding candidate recipient public keys is a **separate property not implied by
  the IND-CCA security** of the hybrid KEM. This CIP does **not** claim it for the
  X-Wing path unless and until it is independently justified for X-Wing. The
  published analyses of ML-KEM's anonymity properties trend positive — the
  post-quantum anonymity (ANO-CCA) line of work on Kyber/ML-KEM has produced
  proofs for the underlying KEM rather than counterexamples — so the omission
  reflects the absence of a pinned analysis covering this exact hybrid
  construction, not a known break. Until one exists, a deployment whose threat
  model requires recipient anonymity against a key-holding adversary
  **MUST NOT** rely on the hybrid path for that property; the honest leakages
  below still hold for both KEMs.

For both KEMs the honest leakages are the same — the **slot count**, the
**sealed-vs-open** distinction, and the **classical-vs-hybrid** KEM family
(`enc.kem`) are visible to any observer; nothing more about the recipients is.

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
independent of this CIP. The same applies to the producer's IP address as seen by
gateways and to any metadata in the off-chain ciphertext blob. This CIP cannot
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

This CIP establishes an **upper bound** on when content existed: the block time of
the transaction carrying the record is a cryptographic witness that the committed
content existed no later than that moment. It does **not** establish a lower
bound. A claim such as "I created this in 2020" carried inside a 2026 transaction
is, at most, evidence that the author had access to the content by 2026; nothing
in the record cryptographically attests to an earlier date. An author who wishes
to assert an earlier creation date SHOULD include that assertion inside the
content itself (for example in a PDF, signed document, or README) where it
becomes part of the hashed plaintext. The block time in this claim is the chain
fact defined in
[Chain facts: block time and confirmation depth](#chain-facts-block-time-and-confirmation-depth) —
an explorer-asserted quantity that deployments with load-bearing dates MUST
cross-check across independent explorers, per that section.

### Privacy

Every byte in a PoE record is on chain forever. This CIP deliberately omits
filenames, MIME types, titles, descriptions, language tags, free-form notes, and
size fields, because each can leak content context — a filename can reveal the
subject of an encrypted document, a MIME type can reveal the content class, and a
byte size can fingerprint a known file. Even a content hash can fingerprint a
known document. For sensitive claims, encrypt the content off-chain and publish
only its plaintext hash plus the sealed-PoE envelope. An application that needs
human-readable context SHOULD carry it inside the hashed content (for example as
an in-content manifest, see
[Rationale: How does this CIP achieve its goals?](#rationale-how-does-this-cip-achieve-its-goals)),
not as a label-309 field.

## Rationale: How does this CIP achieve its goals?

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
  each leaks context. This CIP treats the content bytes as the only semantic
  payload. An application that needs human-readable context **MAY** carry it as an
  in-content manifest: assemble the files plus a manifest describing the bundle,
  archive them into one byte sequence, hash the whole sequence into `items`, and
  (when sealed) encrypt the bundle bytes. Any tampering with the manifest changes
  the bundle bytes and therefore the on-chain hash. The manifest format is
  entirely outside this CIP's scope.

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
`Sig_structure`. This CIP does **not** do this, for CIP-30 compatibility: the
[CIP-30](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0030/README.md)
`signData` interface — the standard wallet-signing path on Cardano — stipulates
that the payload is not hashed and no `external_aad` is used. A dApp has no way
to pass an `external_aad` to a CIP-30 wallet, so requiring a non-empty value
would make every wallet-produced signature fail PoE verification. Embedding
the separator as a fixed UTF-8 prefix at the start of the signed input preserves
the anti-replay property with cryptographic strength equivalent to the
`external_aad` placement; the difference is purely wire-side, and it is the
difference that makes wallet signing feasible. A successor revision MAY revisit
this if a future wallet-signing standard lets the dApp supply `external_aad`.

### Why authorship is expressed only at the record level

This CIP places signatures at the record level, not at the per-item level. A
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

## Path to Active

Per [CIP-0001 §3.3](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0001/README.md#document-lifecycle),
this CIP proposes the following Acceptance Criteria and Implementation Plan.

### Acceptance Criteria

1. **Reference implementations exist and pass conformance.** At least one
   open-source reference implementation of both a producer (record writer) and a
   verifier (chain reader + structural validator + public verifier). Reference
   implementations in [TypeScript](https://github.com/cardanowall/label-309-ts),
   [Python](https://github.com/cardanowall/label-309-py), and
   [Rust](https://github.com/cardanowall/label-309-rs) are published as open-source
   sibling repositories, with worked examples under
   [`../examples/`](https://github.com/cardanowall/label-309/blob/main/examples); all consume the byte-pinned vectors in
   [`../conformance/`](https://github.com/cardanowall/label-309/blob/main/conformance).
2. **Conformance suite.** A public conformance suite exists — valid and invalid
   fixtures, with every error code in
   [`../registries/error-codes.json`](https://github.com/cardanowall/label-309/blob/main/registries/error-codes.json) covered by
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
   outside this CIP's scope to enforce. The identity-key signing path (raw Ed25519
   public key in the in-signature `kid`) is the primary signing path and is
   independently testable without any wallet; this criterion covers the wallet
   path on top of it, not in place of it.
4. **Public mainnet records.** At least three independently authored PoE
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
   [`../conformance/`](https://github.com/cardanowall/label-309/blob/main/conformance) and a runner that maps every error code in
   [`../registries/error-codes.json`](https://github.com/cardanowall/label-309/blob/main/registries/error-codes.json) to at least
   one negative fixture. The suite is the explicit cross-implementation interop
   gate.
2. **Reference SDKs.** Publish a [TypeScript SDK](https://github.com/cardanowall/label-309-ts),
   a [Python SDK](https://github.com/cardanowall/label-309-py), and a
   [Rust SDK](https://github.com/cardanowall/label-309-rs) as open-source packages
   under permissive licenses. All MUST pass the conformance suite, MUST work
   without any implementer-specific account or service, and MUST produce
   byte-identical canonical CBOR for the same logical inputs. Worked examples for
   the reference implementations live under [`../examples/`](https://github.com/cardanowall/label-309/blob/main/examples).
3. **Standalone public verifier and CLI.** Ship a
   [verifier-only CLI](https://github.com/cardanowall/label-309-cli) and a static
   web verifier. Both load from [`../conformance/`](https://github.com/cardanowall/label-309/blob/main/conformance) for unit tests
   and from a small set of mainnet PoE records for end-to-end tests. The verifier
   MUST run against operator-configured Cardano / Arweave / IPFS gateways without
   requiring any vendor-specific endpoint (Acceptance Criterion 5).
4. **Implementor recruitment.** Publicise the CIP on the `cardano-foundation/CIPs`
   discussion thread and through Cardano-developer channels; third-party SDK ports
   are explicitly invited, with the conformance suite as the interop gate
   (Acceptance Criterion 2).
5. **Wallet outreach.** Coordinate with wallet teams to demonstrate CIP-30
   `signData` interop with the reference implementation (Acceptance Criterion 3)
   and to surface PoE records as a first-class metadata view.
6. **Explorer outreach.** Engage major Cardano block-explorer teams to render
   label-309 records as "Proof of Existence" with the canonical hash digests and
   listed URIs; without explorer awareness, end-users see raw chunked CBOR.
   This is a coordination task, not a CIP-text task.
7. **External cryptographic review.** Commission a short external review of the
   sealed-PoE construction, primarily covering the multi-recipient wrap (per-slot
   KEK derivation including the hybrid external salt-binding, zero-nonce safety),
   the slot-set MAC over the slots transcript, the transcript-bound segmented
   STREAM content layer, and the passphrase path's in-ciphertext key commitment
   (Acceptance Criterion 6).
8. **Maintenance.** Editorial corrections that do not change wire bytes are
   non-breaking and may land by PR against the merged CIP. Adding a new algorithm
   identifier to a registry is additive and bumps no version — v1 verifiers reject
   unknown identifiers as the corresponding `UNSUPPORTED_*` error. A change that
   re-interprets existing on-wire bytes requires either an `enc.scheme` bump (for
   a cross-KEM sealed-PoE construction change) or a top-level `v` bump (for a
   record-schema change).

This CIP reaches Proposed when Acceptance Criteria 1, 2, 5, and 6 are
demonstrated; Criteria 3 (two-wallet signing), 4 (public mainnet records), and 7
(public review) gate Active.

## Copyright

This CIP is licensed under [CC-BY-4.0](https://github.com/cardanowall/label-309/blob/main/LICENSE-docs).
