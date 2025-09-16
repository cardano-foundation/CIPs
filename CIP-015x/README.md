---
CIP: "?"
Title: Canonical Ledger State
Category: Ledger
Status: Proposed
Authors:
  - Nicholas Clarke <nicholas.clarke@moduscreate.com>
  - Aleksandr Vershilov <alexander.vershilov@moduscreate.com>
  - João Santos Reis <joao.reis@moduscreate.com>
Implementors:
  - Nicholas Clarke <nicholas.clarke@moduscreate.com>
  - Aleksandr Vershilov <alexander.vershilov@moduscreate.com>
  - João Santos Reis <joao.reis@moduscreate.com>
Discussions:
    - https://github.com/cardano-foundation/CIPs/pull/1083
Created: 2025-08-18
License: CC-BY-4.0
---

## Abstract

This proposal defines the Simple Canonical Ledger State (SCLS), a stable, versioned, and verifiable file format for representing the Cardano ledger state. It specifies a segmented binary container with deterministic CBOR encodings, per-chunk commitments, and a manifest that enables identical snapshots across implementations, supports external tools (e.g., Mithril), and future-proofs distribution and verification of state.

## Motivation: why is this CIP necessary?

Ledger state serialisations are currently implementation details that may change over time. This makes them unsuitable as stable artifacts for distribution, signing, fast sync, or external tooling (e.g., db-sync, conformance testing, and Mithril checkpoints). Without a canonical format, two nodes at the same chain point can legitimately produce different byte streams for the same state, complicating verification and opening room for error in multi-implementation ecosystems.

SCLS addresses these problems by:

- specifying a canonical, language-agnostic container and encoding rules;
- enabling streaming builds and partial verification (per-namespace roots);
- being extensible (e.g., optional indexes/Bloom filters) without breaking compatibility;
- remaining compatible with UTxO-HD/LSM on-disk structures and incremental (delta) updates.

Versioning and Upgrade Complexity: the proposed format defines a solution that will be able to support future protocol extensions with new eras without changing this CIP. Chosen approach allows to define a client that will be interested only in a particular parts of the state, but that will not prevent it from storing, loading and verifying the interesting parts of the state.

The concrete use-case scenarios for this CIP are:

- allow building dump of the Cardano Ledger node state in a canonical format, so any two nodes would generate the same file. This would allow persistence, faster bootstrap and verification.
- such state can be verified by the other node against its own state and signed. It would allow us to fully utilize Mithril, when each node can sign the state independently.
- full conformance testing. Any implementation would be able to reuse test-suite of the Haskell node by importing data applying the test transaction and exporting data back.

## Specification

The Simple Canonical Ledger State (SCLS) is a segmented file format for Cardano ledger states, designed to support streaming and verifiability. Records are sequential, each tagged by type and independently verifiable by hash. Multi-byte values use network byte order (big-endian).

### File Structure

1. Sequence of records `(S, D)*` where `S` is a 32-bit size and `D` is the payload stored in typed record.
1. Each payload begins with a one-byte type tag, defining its type.

Unsupported record types are skipped; core data remains accessible.

### Record Types

| Code | Name     | Purpose                                                 |
| ---- | -------- | ------------------------------------------------------- |
| 0x00 | HDR      | File header: magic, version, network, namespaces        |
| 0x01 | MANIFEST | Global commitments, chunk table, summary                |
| 0x10 | CHUNK    | Ordered entries with per-chunk footer + hash            |
| 0x11 | DELTA    | Incremental updates (overlay; last-writer-wins)         |
| 0x20 | BLOOM    | Per-chunk Bloom filter                                  |
| 0x21 | INDEX    | Optional key→offset or value-hash indexes               |
| 0x30 | DIR      | Directory footer with offsets to metadata/index regions |
| 0x31 | META     | Opaque metadata entries (e.g., signatures, notes)       |

Proposed file layout:

```text
HDR,
(CHUNK[, BLOOM])*,
MANIFEST,
[INDEX]*,
[META]*
[DIR],
[ (DELTA[, BLOOM])* , MANIFEST, [INDEX]*, [DIR] ]*
```

At the first steps of implementation it would be enough to have the simpler structure:

```text
HDR,
(CHUNK)*,
MANIFEST
```

All the other record types allow to introduce additional features, like delta-states, querying data and may be omitted in case if the user does not want those functionality.

For the additional record types (all except `HDR, CHUNK, MANIFEST`) it's possible to keep such records outside of the file and build them iteratively, outside of the main dump process. This is especially useful for indices.

#### HDR Record

**Purpose:** identify file, version, and global properties.

**Structure:**

`REC_HDR` (once at start of file)

- `magic` : `b"SCLS\0"`
- `version` : `u16` (start with `1`)
- `network_id` : `u8`  (`0` — mainnet, `1` — testnet)
- `slot_no` : `u64` identifier of the blockchain point (hash/slot).

**Policy:**

- appears once in the file header;
- must be read and verified first;
- supports magic bytes for file recognition.

#### CHUNK Records

**Purpose:** group entries for streaming and integrity; maintain global canonical order, see namespace and entries for more details.

**Structure:**

- `chunk_seq` : `u64` — sequence number of the record
- `chunk_format` : `u8` - format of the chunks
- `namespace` : `bstr` — namespace of the values stored in the CHUNK
- `entries` — CBOR encoded list of unlimited length
- `footer {entries_count: u64, chunk_hash: u64}` — hash value of the chunk of data, is used to keep integrity of the file.

**Policy:**

- chunk size \~8–16MiB; footer required;
- data is stored in deterministically defined global order; In the lexical order of the keys;
- all keys in the record must be unique;
- all key-values in the record must refer to the same namespace;
- readers should verify footer before relying on the data;
- `chunk_hash = H(concat [ digest(e) | e in entries ])`;
- all keys in `CHUNK` `n` must be lexicographically lower than all keys in `CHUNK` `n+1`.

The format proposes support of data compression. For future-compatibility the format is described by the `chunk_format` field, and following variants are introduced:

| Code | Name  | Description                                   |
| ---- | ----- | --------------------------------------------- |
| 0x00 | RAW   | Raw CBOR Entries                              |
| 0x01 | ZSTD  | All entries are compressed with seekable zstd |
| 0x02 | ZSTDE | Compress each value independently             |

When calculating and verifying hashes, it's build over the uncompressed data.

#### MANIFEST Record

**Purpose:** index of chunks and information for file integrity check.

**Structure:**

- `total_entries`: `u64` — number of data entries in the file (integrity purpose only)
- `total_chunks`: `u64` — number of chunks in the file (integrity purpose only)
- `root_hash`: **Merkle root** of all `entry_e` in the chosen order, see verification for details
- `namespace_hashes`: CBOR table of Merkle roots for each namespace, mapping namespace name to the hash in a multihash format
- `prev_manifest_offset`: `u64` — offset of the previous manifest (used with delta files), zero if there is no previous manifest entry
- `summary`: `{ created_at, tool, comment? }`

**Policy:** used to verify all the chunks.

#### DELTA Record

```text
TODO: exact contents of the DELTA record will be defined later, currently we describe
a high-level proposal.
```

**Purpose:** Delta records are used to build iterative updates, when base format is created and we want to store additional transactions in a fast way. Delta records are designed to be compatible with UTxO-HD, LSM-Tree or other storage types where it's possible to stream list of updates.

Updating of the file in-place is unsafe so instead we store list of updated.

All updates are written in the following way:

- if an entry has a natural key and we want to update data we can store a new value;
- if we want to remove a value with natural key we should write a special tombstone entry, see namespaces;
- if a value has no natural key we must first delete old value and then insert a new one.

**Structure:**

- `transaction:` `u64` — transaction number
- `changes:` `CBOR` array of the entries
- `footer:` `{entries_count, chunk_hash}`

**Policy:**

- chunk size \~8–16MiB; footer required;
- reader should verify hash before relying on data;
- dead entries are marked by the special tombstone entry;
- there must be only one element for the given key in the delta record.

#### BLOOM Record

TODO: define details or move to future work, (we propose to define exact format and properties, after the first milestone, when basic data will be implemented and tested. Then based on the benchmarks we could define exact properties we want to see)

**Purpose:** additional information for allowing fast search and negative search.

**Structure:**

- `chunk_seq: u64` sequence number of the record.
- `m`: `u32` - total number of bits in the Bloom filter’s bitset (the length of the bit array).
- `k`: `u8` - number of independent hash functions used to map a key into bit positions in that array.
- `bitset`: `bytes[ceil(m/8)]` — actual bitset.

#### INDEX Record

```text
TODO: define structure, (we propose to define exact format and properties, after the first milestone, when basic data will be implemented and tested. Then based on the benchmarks we could define exact properties we want to see)
```

**Purpose:** allows fast search based on the value of the entries.

The general idea is that we may want to write a query to the raw data using common format like `json-path` but that will run against CBOR. In this case while building we may build an index. Later queries can use indexes instead of direct traversal.

**Policy:**

- Indices are completely optional and do not change the hash of the entries in data.

### Directory Record

TODO: define structure, (we propose to define exact format and properties, after the first milestone, when basic data will be implemented and tested. Then based on the benchmarks we could define exact properties we want to see)

**Purpose**: If a file has index records then they will be stored after the records with actual data, and directory record allow a fast way to find them. Directory record is intended to be the last record of the file and has a fixed size footer.

**Structure:**

- `metadata_offset:` `u64` offset of the previous metadata record, zero if there is no record
- `index_offset:` `u64` offset of the last index record, zero if there is no record

### META Record

**Purpose:** record with extra metadata that can be used to store 3rd party data, like signatures for Mithril, metadata information. This is an additional record that may be required for in the additional scenarios.

**Structure:**

- `entries: Entry[]` list of metadata entries, stored in lexicographical order
- `footer: {entries_count: u64, entries_hash}`

Entry:

- `subject: URI` — subject stored in the `URI` format
- `value: cbor` — data stored by the metadata entry owner.

**Policy:**

- Meta chunks are completely optional and does not change hash of the entries in data.
- `entries_hash = H(concat (digest e for e in entries))`

### Namespaces and Entries

In order to provide types of the values and be able to store and verify only partial state, a notion of namespaces is introduced. Each SCLS file may store values from one or more namespaces.

#### Supported Namespaces

Each logical table/type is a namespace identified by a canonical string (e.g., `"utxo"`, `"gov"`).

| Shortname    | Content                         |
| ------------ | ------------------------------- |
| utxo/v0      | UTxOs                           |
| stake/v0     | Stake delegation                |
| rewards/v0   | Reward accounts                 |
| params/v0    | Protocol parameters             |
| pots/v0      | Accounting pots (reserves etc.) |
| spo/v0       | SPO state                       |
| drep/v0      | DRep state                      |
| gov/v0       | Governance action state         |
| hdr/v0       | Header state (e.g. nonces)      |
| tombstone/v0 | Marker of the removed entry     |

New namespaces may and will be introduced in the future. With new eras and features, new types of the data will be introduced and stored. In order to define what data is stored in the SCLS file, tools fill the `HDR` record and define namespaces. The order of the namespaces does not change the signatures and other integrity data.

For future compatibility support we added version tag to the name, but it may be a subject of discussion

#### Entries

Data is stored in the list of `Entries`, each entry consist of the namespace and its data:

- `key: bstr` - CBOR-encoded string key.
- `dom : bstr` – CBOR-encoded data (canonical form).

Exact definition of the domain data is left out in this CIP. We propose that ledger team would propose canonical representation for the types in each new era. For the types they must be in a canonical [CBOR format](https://datatracker.ietf.org/doc/html/rfc8949) with restrictions from [deterministic cbor](https://datatracker.ietf.org/doc/draft-mcnally-deterministic-cbor). Values must not be derivable, that is, if some part of the state can be computed based on another part, then only the base one should be in the state."

All concrete formats should be stored in attachment to this CIP and stored in `namespaces/namespaces.cddl`. All the changes should be introduced using current CIP update process.

#### Canonicalization Rules

- CBOR maps must be deterministic with sorted keys and no duplicates.
- Numbers use minimal encoding.
- Arrays follow fixed order.

#### Verification

- Entry digest: `digest(e) = H(0x01 || ns_str || key || value)`,
- Manifest stores overall root and per-namespace commitments.

Merkle root is computed as a root value of the Merkle trees over all the live entry digests in canonical order; tombstones excluded, last-writer-wins for overlays.

To describe in detail, basic chunks store all the values in the canonically ordered based in the key order. After having all values in the order we build a full Merkle tree of those values.

The rule of the thumb is that when we calculate a hash of the data we take into account only the live (non deleted) values in canonical order. In the case when there is a single dump without delta records, this is exactly the order of how values are stored. But when delta—records appear we need to take into account that in the following records there may be values that are smaller than the ones in the base and some values may be deleted or updated. As a result writer should calculate a live-set of values, which can be done by running a streaming multi-merge algorithm (when we search a minimal value from a multiple records). In the case a value exists in multiple records we use a last—writer—wins rule. If there is a tombstone, we consider a value deleted and do not include it in a live-set.

### Extensibility

- Unknown fields in `HDR` or unknown chunk types can be skipped by readers.
- Allows future extension (e.g., index chunks, metadata) without breaking compatibility.

## Rationale: how does this CIP achieve its goals?

This CIP achieves its goals by:

1. Define a canonical format that has the following properties: the format is very simple, it would be easy to write that an implementation in any languages.
2. The format is extensible and agnostic, it provides versioned format that simplified ledger evolution.
3. Removes ambiguity, allows signed checkpoints, and improves auditability

Format defines canonical format and ordering for the stored data, thus allows reproducible and verifiable hashing of the data. It supports Mithril and fast node bootstrap use cases.

### Prior Work and Alternatives

#### Global alternatives:

- **CIP PR #9 by Jean-Philippe Raynaud**:
the CIP that discusses the state and integration with Mithril a lot. Without much details CIP discusses immutable db and indices. Current CIP discussing adding indices as well, we believe that we can combine the approaches from the [work](https://github.com/cardano-scaling/CIPs/pull/9) and related work with our own and use the best of two words.

- **CIP draft by Paul Clark**:
this was an early work of the CIP of the canonical ledger state. The work was more targeted towards what is stored in the files. Proposal also uses deterministic CBOR (canonical CBOR in this CIP). Proposal opens a discussion and rules about how and when snapshots should be created by the nodes, that is deliberately not discussed in the current CIP, as we do not want to impose restrictions on the nodes, and the format allow the nodes not to have any agreement on those rules. As a solution for extensibility and partiality the CIP proposes using a file per "namespace" (in the terminology of the current CIP), in our work we proposed to have a single chunked file that is more friendly for the producer. Currently we are considering at least to have an option for extracting multi-files version. See discussion in open questions.

- **Do Nothing**: rejected due to interoperability and Mithril requirements.

#### Implementation alternatives

##### Container format

More common container file formats: many container formats were evaluated, but most implementations do not meet all the required properties. The container format closest to the required properties are CARv2 and gitpack-files, but they are more complex and would require additional tooling and language support for all node implementations. For simplicity and ease of adoption, a straightforward binary format was chosen. It's still possible to express the current approach in both CARv2 and gitpack files, if it will be shown that the approach is superior.

##### Data encoding

- **gRPC**: current Haskell node is using CBOR-based ecosystem, so nodes have to support CBOR anyway. In contrast to self-describing CBOR, gRPC requires schema to read the document, and that may be a problem for future compatibility.
- **Plain CBOR stream**: easier decoding, but prevents skipping unwanted chunks needed for filtering and additional properties, like querying the data in the file.

**JSON vs CBOR for Canonical Ledger State**


There are strong reasons to prefer CBOR over JSON for representing the canonical ledger state. The ledger state is large and contains binary data; a binary format is therefore much more compact and efficient than JSON.

While JSON libraries are widely available in nearly every language, JSON lacks a notion of canonical form. Two JSON serializations of the same object are not guaranteed to be byte-identical, so additional tooling and specification would be required to achieve determinism.

By contrast, CBOR has a defined deterministic encoding (see [RFC 8949](https://datatracker.ietf.org/doc/html/rfc8949#section-4.2) and [restrictions](https://datatracker.ietf.org/doc/draft-mcnally-deterministic-cbor)), making it suitable for a canonical format. CBOR also has mature implementations across many programming languages (list [here](https://cbor.io/impls.html)).

Importantly, RFC 8949 also defines a mapping between CBOR and JSON. This allows us to specify a JSON view of the format so that downstream applications can consume the data using standard JSON tooling, while the canonical form remains CBOR.


##### Multi-file or single file?

We considered using single file because it's more friendly to the producer, because it's possible to ensure required atomicity and durability properties, together with footers-in records, it's possible to validate that the data was actually written and is correct. In case of failure it's possible to find out exactly the place where the failure happened.

However, we agree that for the consumer who wants to get partial states in will be much simpler to use multiple files.

The proposed SCLS format does not contradict having multiple files, on the contrary for things like additional indices we suggest using additional files, it will work as the records have sequential numbers and we can reconstruct full file and have an order. In this proposal we would file to set an additional constraint of the tooling that will come with the libraries: that the tool should be able to generate multi-files on a request and convert formats between those

##### Should files be byte-identical?

Current approach does not provide byte-identical files, only the domain data that is stored and it's hashes are canonical. It means that tools like Mithril will have to use additional tooling or recalculate hash on their own. It's done for the purpose, this way software may add additional metadata entries, e.g. Mithril can add its own signatures to the file without violating validation properties. Other implementation may add records that are required for them to operate or bootstrap. It's true that other [approaches](https://hackmd.io/Q9eSEMYESICI9c4siTnEfw), does solve that issue by creating multiple files, each of them will be byte-identical.

There are few solutions that we propose:

1. allow tooling to export (or even generate) raw cbor files, that will have required byte-identical property
2. set additional restrictions on the policies for the records, and instead of defining variable size records require all the records to have exact number of entries inside. It will harm some properties of the hardware but the files will be byte-identical in case if they have similar metadata. Or the metadata we can place it in separate file, then everything will be byte-identical.

## Open Questions

**What is the exact implementation for data compression, especially for indexing and search?**

There are many ways to write indices, hashtables or btrees, each of them may have interesting
properties. It's an open question which of them do we want to support.

**Do we want the file be optimized for querying with external tools? If so how to achieve that?**

We are proposing adding additional records types:

- bloom records — they would allow faster search of the values by the key, still require file traversal
- index records - it would allow faster search by key without full file traversal

Both changes will not change the structure of the file.

**Do we want to support entries without natural keys? If so how can we do that?**

There are three options that we see:

- In chunks records make key optional, that will support such values. That will change the spec, as we must allow many of such values in the chunks records.
- Keep value in key, and zero value.
- Create a separate record type for values without keys.

## Path to Active

### Acceptance Criteria

- [ ] Expert review and consensus from Ledger Committee, IOG, and Node teams.
- [ ] Reference implementation in Cardano node with CLI tool for export/import.
- [ ] Verified test vectors showing identical output across implementations, including Mithril compatibility.
- [ ] Full documentation and CDDL schemas.

### Implementation Plan

1. [ ] Prototype SCLS writer/reader.
1. [ ] Refine specification and finalise CDDL.
1. [ ] Integrate into Cardano node CLI.
1. [ ] Validate with Mithril.
1. [ ] Rollout and ecosystem tooling.

## References

1. [CARv2 format documentation](https://ipld.io/specs/transport/car/carv2/)
2. [Draft Canonical ledger state snapshot and immutable data formats CIP](https://github.com/cardano-scaling/CIPs/pull/9)
3. [Mithril](https://docs.cardano.org/developer-resources/scalability-solutions/mithril)
4. [Multihash format](https://github.com/multiformats/multihash)
5. [Canonical ledger state CIP draft by Paul Clark](https://hackmd.io/Q9eSEMYESICI9c4siTnEfw)
6. [Deterministically Encoded CBOR in CBOR RFC](https://datatracker.ietf.org/doc/html/rfc8949#section-4.2)
7. [A Deterministic CBOR Application Profile](https://datatracker.ietf.org/doc/draft-mcnally-deterministic-cbor)

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/).
