# Golden CBOR vectors (observability mini-protocol)

Generated with Python `cbor2` (except `neg_duplicate_standard_key`, hand-crafted).
Hex is lowercase, no spaces. Definite-length arrays/maps only.

`publicationVersion` = **1** on every valid publication.

Expected outcomes:

| prefix | meaning |
| --- | --- |
| *(none)* | positive / must **ACCEPT** |
| `bnd_` | boundary / must **ACCEPT** (may ignore unknown keys) |
| `neg_` | negative / must **REJECT** |

Rust and Haskell should agree on accept vs reject for every file.

## Field keys used

Standard:

- `1` = `node_name` (tstr)
- `2` = `node_version_major` (`word16` / uint)
- `3` = `node_version_minor` (`word16` / uint)
- `4` = `node_version_patch` (`word16` / uint)
- `5` = `node_type` (tstr)
- `6` = `git_revision` (tstr)

Amaru experimental catalogue (typed in CDDL; see `field-registry.md`):

- `"amaru.version"` → tstr
- `"amaru.cpu_cores"` / `"amaru.process_rss_bytes"` → uint
- `"amaru.peers_inbound"` / `"amaru.peers_outbound"` /
  `"amaru.peers_outbound_connecting"` / `"amaru.peers_using"` /
  `"amaru.peers_target_upstream"` / `"amaru.peers_target_downstream"` → uint

## Shared constants

- `snapshot_slot` = `123456600` (`0x075bcc58`)
- `publicationVersion` = `1`

---

## Positive messages

### `msgGetPublications` = `[0]` — ACCEPT

```text
8100
```

File: `msg_get_publications.hex`

### `msgPublications` empty = `[1, []]` — ACCEPT

Semantics: protocol enabled; no publication currently in cache.

```text
820180
```

File: `msg_publications_empty.hex`

### `msgPublications` one open — ACCEPT

```text
[1, [[0, 1, 123456600, {1: "amaru", 2: 1}]]]
```

```text
8201818400011a075bcc58a20165616d6172750201
```

File: `msg_publications_one_open.hex`

### `msgPublications` multi open — ACCEPT

```text
8201828400011a075bcc58a20165616d61727502018400011a075bcc58a20165616d6172750202
```

File: `msg_publications_multi_open.hex`

### `msgPublications` one open + all standard keys 1–6 — ACCEPT

```text
[1, [[0, 1, 123456600, {
  1: "amaru", 2: 10, 3: 11, 4: 0, 5: "full", 6: "abcdef1"
}]]]
```

```text
8201818400011a075bcc58a60165616d617275020a030b0400056466756c6c066761626364656631
```

File: `msg_publications_one_open_standard_fields.hex`

### `msgPublications` one open + Amaru experimental catalogue keys — ACCEPT

Representative experimental subset (plus standard `1`/`2`):

```text
[1, [[0, 1, 123456600, {
  1: "amaru",
  2: 1,
  "amaru.cpu_cores": 8,
  "amaru.version": "10.11.0"
}]]]
```

```text
8201818400011a075bcc58a40165616d61727502016f616d6172752e6370755f636f726573086d616d6172752e76657273696f6e6731302e31312e30
```

File: `msg_publications_one_open_with_experimental.hex`

### `msgPublications` one open + full Amaru bag — ACCEPT

Standard keys `1`–`6` plus the Amaru experimental catalogue (example values):

```text
8201818400011a075bcc58af0165616d617275020a030b0400056466756c6c0667616263646566316f616d6172752e6370755f636f7265730873616d6172752e70656572735f696e626f756e640274616d6172752e70656572735f6f7574626f756e6403781f616d6172752e70656572735f6f7574626f756e645f636f6e6e656374696e6701781d616d6172752e70656572735f7461726765745f646f776e73747265616d14781b616d6172752e70656572735f7461726765745f757073747265616d0a71616d6172752e70656572735f7573696e670477616d6172752e70726f636573735f7273735f62797465731a001000006d616d6172752e76657273696f6e6731302e31312e30
```

File: `msg_publications_one_open_amaru_catalogue.hex`

---

## Negative and boundary (10)

### 1. `neg_unknown_message_tag.hex` — REJECT

Unknown message tag `[3]` (also covers retired `msgDone` tag `2` as unknown if seen).

```text
8103
```

### 2. `neg_malformed_get_publications_len.hex` — REJECT

`MsgGetPublications` must be a 1-element array; this is `[0, 0]`.

```text
820000
```

### 3. `neg_observer_pubkey_wrong_len.hex` — REJECT

Encrypted publication with 16-byte `observerPublicKey` (must be 32).

Logical shape: `[1, [[1, 1, slot, h'11'×16, h'00'×64]]]`

### 4. `neg_wrong_type_node_name.hex` — REJECT

Standard key `1` (`node_name`) encoded as `true` instead of tstr.

```text
8201818400011a075bcc58a101f5
```

### 5. `neg_wrong_type_version_major.hex` — REJECT

Standard key `2` (`node_version_major`) encoded as tstr `"hello"` instead of uint.

```text
8201818400011a075bcc58a1026568656c6c6f
```

### 6. `neg_duplicate_standard_key.hex` — REJECT

Open payload CBOR map with duplicate key `1` (`"amaru"` then `"x"`).
Hand-crafted (maps from `cbor2` cannot emit duplicate keys).

```text
8201818400011a075bcc58a20165616d617275016178
```

### 7. `bnd_unknown_future_integer_key.hex` — ACCEPT

Valid open publication that also carries unknown integer key `99`.
Decoder must **accept** the message and **ignore** key `99`.

```text
8201818400011a075bcc58a30165616d6172750201186307
```

### 8. `bnd_max_publications_6.hex` — ACCEPT

`MsgPublications` with exactly **6** open publications (CDDL `*6` upper bound).

### 9. `neg_publications_over_max_7.hex` — REJECT

Same shape with **7** publications (over CDDL max).

### 10. `neg_invalid_publication_version.hex` — REJECT

Open publication with `publicationVersion = 2` (only `1` is defined).

```text
8201818400021a075bcc58a20165616d6172750201
```

---

## Summary table

| file | expect |
| --- | --- |
| `msg_get_publications.hex` | ACCEPT |
| `msg_publications_empty.hex` | ACCEPT |
| `msg_publications_one_open.hex` | ACCEPT |
| `msg_publications_multi_open.hex` | ACCEPT |
| `msg_publications_one_open_standard_fields.hex` | ACCEPT |
| `msg_publications_one_open_with_experimental.hex` | ACCEPT |
| `msg_publications_one_open_amaru_catalogue.hex` | ACCEPT |
| `neg_unknown_message_tag.hex` | REJECT |
| `neg_malformed_get_publications_len.hex` | REJECT |
| `neg_observer_pubkey_wrong_len.hex` | REJECT |
| `neg_wrong_type_node_name.hex` | REJECT |
| `neg_wrong_type_version_major.hex` | REJECT |
| `neg_duplicate_standard_key.hex` | REJECT |
| `bnd_unknown_future_integer_key.hex` | ACCEPT (ignore key 99) |
| `bnd_max_publications_6.hex` | ACCEPT |
| `neg_publications_over_max_7.hex` | REJECT |
| `neg_invalid_publication_version.hex` | REJECT |

## Still deferred

- ciphertext exactly at / over 16384 bytes
- total encoded `MsgPublications` over 16384 bytes
- openPayload encoding over 8192 bytes
- sealed-box encrypt/decrypt round-trip vectors
- malformed `snapshotSlot` type

## Removed

- `msgDone` — one-shot protocol ends after `MsgPublications`; no Done message on the wire.
