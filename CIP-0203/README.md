---
CIP: 203
Title: Block Producer Identifier Registry
Category: Consensus
Status: Proposed
Authors:
    - Josh Marchand <josh@sundae.fi>
    - Adam Dean <adam@crypto2099.io>
Implementors: []
Discussions:
    - Original PR: https://github.com/cardano-foundation/CIPs/pull/1276
    - Block Producer Payloads PR (merged into this CIP): https://github.com/cardano-foundation/CIPs/pull/1282
    - CPS-0036 draft PR: https://github.com/cardano-foundation/CIPs/pull/1260
    - Early CIP-0180 draft: https://github.com/cardano-foundation/CIPs/pull/1157
Solution To:
    - CPS-0036? | Voluntary Block Producer Software Signalling: https://github.com/cardano-foundation/CIPs/pull/1260
Created: 2026-09-21
License: CC-BY-4.0
---

## Abstract

Cardano has become a multi-implementation network. Blocks on mainnet have been produced by Amaru, Dingo, Gerolamo, and cardano-node, among others. In an attempt to measure client diversity across the network, Dingo, Amaru and Gerolamo have committed to using the vestigial minor component of the header `protocol_version` to identify blocks produced by each implementation.

This CIP fixes a bit layout for the 32-bit field: an 8-bit implementation identifier, a 22-bit implementation-defined payload, and a 2-bit scheme version. It also establishes a machine-readable registry of identifiers in this repository with governing rules for assignment, update, and retirement. Finally, it defines a small JSON format with which an implementation can describe how its payload bits decode into named values, so that generic consumers can read any registered payload without implementation-specific code. This is strictly voluntary, and requires no hard fork or changes in existing nodes.

Importantly, such a signalling mechanism will only ever represent a "best-effort" measurement of node diversity. It is a self-reported value, and there is no way to validate the block was actually produced by the software that it is claiming.

## Motivation: Why is this CIP necessary?

For the full problem statement, read [the CPS-0036 draft](https://github.com/cardano-foundation/CIPs/pull/1260). In summary, while client diversity becomes a critical metric for Cardano's health, there is currently nothing that attributes individual blocks to a particular implementation. While there has been much discussion on the subject, including a [stalled proposal](https://github.com/cardano-foundation/CIPs/pull/1157), there is already a _de facto_ convention on chain. [Dingo](https://github.com/blinklabs-io/dingo) and [Gerolamo](https://github.com/harmoniclabs/gerolamo) have produced mainnet blocks with a minor `protocol_version` value `69` and `67` respectively. Other node implementations have agreed to follow this approach. Without a registry, it would be impossible to attribute a block to the reported node implementation. Introducing a standard encoding scheme makes it simple for anyone to read the on-chain data. The proposed `CIP-0180` stalled because it required a new ledger era. Importantly, this approach avoids a fork completely.

The 22 payload bits let an implementation report more than its identity: a release, enabled capabilities, configuration state, or readiness for an upcoming hard fork. If each implementation describes its payload only in prose, every explorer, dashboard and monitoring tool has to write and maintain a decoder per implementation, and payload data ends up useful only to the teams who emitted it. A shared, machine-readable description of the payload bit layout lets a consumer read the identifier, look up the registry entry, fetch the payload definition, and decode the payload with one generic parser. The meaning of the decoded values stays with each implementation.

## Specification

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in [RFC 2119](https://datatracker.ietf.org/doc/html/rfc2119) and [RFC 8174](https://datatracker.ietf.org/doc/html/rfc8174) when, and only when, they appear in all capitals, as shown here.

### Background: the header `protocol_version` field

After the Shelley-era, every `header_body` carries a `protocol_version` with a `major` and a `minor`:

```cddl
header_body =
  [ block_number     : block_number
  , slot             : slot
  , prev_hash        : hash32/ nil
  , issuer_vkey      : vkey
  , vrf_vkey         : vrf_vkey
  , vrf_result       : vrf_cert
  , block_body_size  : uint .size 4
  , block_body_hash  : hash32       ; merkle triple root
  , operational_cert
  , protocol_version
  ]
  
protocol_version = [major_protocol_version, uint .size 4]
major_protocol_version = 0 .. 12
```

Ledger rules only depend on the major version; the minor version has no impact on block validity, hard-fork initiation, or era selection. In the Dijkstra era, the ledger makes this explicit. The header carries `header_version_info` instead of `protocol_version`, with the second field being renamed to `self_reported_software_tag`. This document uses "minor version" throughout, since that is the term used generally by the ecosystem.


```cddl
header_version_info =
  [ highest_supported_major_version : uint .size 4
  , self_reported_software_tag : uint .size 4
  ]
```


The header is signed by the pool's KES key under its operational certificate. Therefore, whatever value is placed there is attributable to a specific pool, even though it is self-declared. 

### Bit layout of the minor version

The 32-bit minor version is divided into three fields. Bit 0 is the least significant bit of the integer value. The layout is defined on the integer value, not on its CBOR byte serialization: the field is a CBOR `uint`, and the encoder chooses the shortest major-type-0 encoding for the value as usual.

```
  31 30  | 29                                            8 | 7                    0
+--------+-------------------------------------------------+------------------------+
| scheme |          implementation-defined payload         |   implementation id    |
| 2 bits |                    22 bits                      |         8 bits         |
+--------+-------------------------------------------------+------------------------+
```

| Field     | Bits    | Width | Range           | Meaning |
|-----------|---------|-------|-----------------|---------|
| `scheme`  | 31 - 30 | 2     | 0 - 3           | Version of this layout. `0` denotes the layout defined by this CIP. |
| `payload` | 29 - 8  | 22    | 0 - 4,194,303   | Defined by the implementation identified by `id`. |
| `id`      | 7 - 0   | 8     | 0 - 255         | Implementation identifier, resolved through the [registry](#registry). |

#### Construction and extraction

```
minor   = (scheme << 30) | (payload << 8) | id

scheme  =  minor >> 30
payload = (minor >> 8) & 0x3FFFFF
id      =  minor       & 0xFF
```

#### Field rules

- A producer MUST set `scheme` to `0`. Values `1`, `2` and `3` are reserved for future CIPs. A future CIP defining a new scheme MAY keep the layout of bits 29 - 0 and use the new scheme value only as a fresh identifier space, or MAY redefine those bits entirely. A future CIP MUST NOT change the meaning of `scheme = 0`.
- A producer MUST set `id` to a value it is entitled to use under the [registry](#registry) for `scheme = 0`.
- A producer MUST NOT reserve an `id` defined in [Reserved identifiers](#reserved-identifiers), or an existing entry in the [registry](#registry).
- A producer MAY set `payload` to any 22-bit value that decodes under the payload definition linked from its registry entry. A producer whose registry entry has no payload definition MUST set `payload` to `0`.
- The resulting `minor` MUST be encoded as a CBOR `uint` and MUST NOT exceed `4294967295` (`0xFFFFFFFF`).
- A consumer MUST NOT interpret `payload` or `id` when `scheme` is not `0`.
- A consumer MUST treat `payload` as opaque unless the registry entry for that `id` links a payload definition in a `definition_format` the consumer supports.

#### Test vectors

Values are shown as the decimal integer that appears in the header, its 32-bit hexadecimal form, and the decoded fields.

| `minor` (decimal) | `minor` (hex) | `scheme` | `payload`   | `id` | Note |
|-------------------|---------------|----------|-------------|------|------|
| 0                 | `0x00000000`  | 0        | 0           | 0    | No signal. |
| 7                 | `0x00000007`  | 0        | 0           | 7    | Legacy cardano-node at release minor 7. Reserved; MUST NOT be emitted by an implementation of this CIP. |
| 67                | `0x00000043`  | 0        | 0           | 67   | Gerolamo, no payload. |
| 69                | `0x00000045`  | 0        | 0           | 69   | Dingo, no payload. |
| 315973            | `0x0004D245`  | 0        | 1234        | 69   | `id` 69 with payload 1234. |
| 1073741637        | `0x3FFFFF45`  | 0        | 4194303     | 69   | Maximum payload. |
| 1073741823        | `0x3FFFFFFF`  | 0        | 4194303     | 255  | Largest value valid under `scheme = 0`. |
| 1073741893        | `0x40000045`  | 1        | ignored     | ignored | `scheme = 1`. A consumer implementing only this CIP MUST NOT decode the remaining bits. |

A value above `4294967295` is not a valid `minor` under any scheme.

### Reserved identifiers

| `id`      | Meaning                                              |
|-----------|------------------------------------------------------|
| 0         | No signal. Default value of implementations that do not participate. MUST NOT be registered. |
| 1 - 15    | Legacy cardano-node. Before adopting this CIP, cardano-node sets the minor to its release number within a major version, and has reached `8`. Reserved so that historical blocks decode unambiguously. MUST NOT be emitted or registered. |
| 16 - 254  | Assignable through the registry.                     |
| 255       | Deliberate opt-out. An operator who actively declines to identify their software, to distinguish deliberate from non-participation. |

Reserved identifiers are defined here and do not appear in `registry.json`. A consumer MAY attribute a block with `scheme = 0`, `payload = 0` and `id` in `1 - 15` to cardano-node at release minor `id`.

### Producer requirements

- MUST use either an `id` registered to that implementation, `0`, or `255`.
- MUST NOT use an `id` registered to a different implementation.
- MUST NOT use a reserved `id` in `1 - 15`.
- Payload MAY be any 22-bit value that decodes under the payload definition linked from the implementation's registry entry. It MUST be `0` if the implementation publishes no payload definition.
- SHOULD give the operator a configuration option to emit `255` instead. Some SPOs have operational rules against disclosing software versions.
- SHOULD default to signalling. SHOULD allow a user of their software to opt-out of signalling.

### Registry

- Files: `registry.json` (data) and `registry.schema.json` (JSON schema). Both are in this directory.
- Entry fields (see schema): `scheme`, `id`, `name`, `status` (`active` | `retired`), `maintainers` (array of GitHub accounts), `repository`, `payload_documentation` (URL or `null`), `payload_definition` (URL or `null`), `registered` (date), `retired` (date or `null`), `description`.
- `payload_definition` links a machine-readable payload definition conforming to [Payload definitions](#payload-definitions). It is the only normative description of how the payload bits decode.
- `payload_documentation` links human-readable documentation of what decoded payload values mean. It MUST NOT be used in place of a `payload_definition`, and MUST be `null` when `payload_definition` is `null`.
- The registry lists only identifiers assigned to implementations. Reserved identifiers are defined by this document and MUST NOT be added to `registry.json`.
- The registry is partitioned by `scheme`. An identifier is the pair `(scheme, id)`, and that pair is unique. The same `id` under two different schemes refers to two unrelated entries. This CIP defines only entries with `scheme = 0`; a future CIP that defines a new scheme adds entries under that scheme to the same file.
- The schema cannot enforce uniqueness of `(scheme, id)` across entries; editors check it at review. Consider a small CI script later.

#### Assignment

- Open a PR against `registry.json` only.
- Eligibility: a node implementation that produces, or is about to produce, blocks on a public Cardano network (mainnet or a public testnet). One `id` per implementation, not per version.
- Requester MAY propose a specific number in 16–254; otherwise editors assign. First come, first served; no meaning attached to the number.
- PR MUST list at least one GitHub account under `maintainers` and a public repository. The listed accounts are the ones entitled to amend the entry.
- No CIP is required per entry.

#### Update

- Name, maintainers, repository and payload URL change by PR from a listed maintainer (or with their visible consent).
- Payload format changes are the implementation's responsibility. The published payload definition MUST remain able to decode historical values, either by being backward compatible or by carrying its own version marker inside the 22 bits (see [Layout version](#layout-version)).

#### Retirement

- A listed maintainer, or editors after a documented period of inactivity, set `status = retired` and `retired = <date>`.
- Retired identifiers are never reassigned within their scheme. Blocks are permanent, so the mapping must be too.
- Retired entries stay in `registry.json`.
- If the assignable range of a scheme is exhausted, whether by active or retired entries, the remedy is a new CIP defining the next `scheme` value, which opens a fresh identifier space. Identifiers are never reclaimed.

#### Transfer

- Ownership moves by PR with consent from a listed maintainer. Disputes go to CIP editors.

### Versioning

- The layout is versioned by the 2 `scheme` bits. A future CIP MAY define `scheme` 1, 2 or 3 and MUST NOT change the meaning of `scheme = 0`.
- The identifier space is versioned by the same bits. Each scheme has its own range of identifiers in `registry.json`, so a new scheme can be introduced purely to obtain more identifiers, without changing the layout.
- The registry is versioned by git history. Entries are append-or-amend; never delete.

### Payload definitions

A payload definition is a JSON document that describes how an implementation's 22-bit `payload` decodes into named values. The implementation chooses what its payload contains and how its bits are allocated. This section standardizes only how that choice is described, and does not assign meaning to any payload bit.

An implementation that emits a non-zero `payload` MUST publish a payload definition and link it from the `payload_definition` field of its registry entry. A prose description of the payload layout does not satisfy this requirement. An implementation whose payload layout cannot be expressed in any defined `definition_format` MUST emit a payload of `0` until a future `definition_format` can express it (see [Format versioning](#format-versioning)).

#### Schema

The JSON Schema for `definition_format` `0` is [payload-definition.format-0.schema.json](payload-definition.format-0.schema.json). A document linked from `payload_definition` MUST be valid JSON and MUST validate against the schema for the `definition_format` it declares.

#### Bit numbering

Payload bits are numbered from least significant to most significant, from `0` to `21`. Payload bit `n` is bit `n + 8` of the `minor` value.

```
bit 21                                        bit 0
  |                                             |
  v                                             v
+-----------------------------------------------+
|                    payload                    |
+-----------------------------------------------+
```

Bit ranges are written as a two-element array `[low, high]` and are inclusive. `[4, 9]` identifies the six bits numbered 4 through 9. A field's value is `(payload >> low) & ((1 << (high - low + 1)) - 1)`, read as an unsigned integer.

#### Document structure

The top-level document contains a `definition_format` and exactly one of:

- `fields`, an array of field definitions that apply to every payload; or
- `layout_version`, which reads a bit range and chooses one of several layouts by its value.

The `definition_format` identifies which version of this CIP's definition language the document is written in. It says what the JSON document may contain, and nothing about the payload. An implementation versions its own payload layout with `layout_version`.

#### Field types

Format `0` defines three field types. Every field has a `name`, a `type`, and a `bits` range.

**`integer`** reads its bit range as an unsigned integer.

```json
{ "name": "build", "type": "integer", "bits": [0, 15] }
```

**`boolean`** reads exactly one bit. `0` decodes to `false` and `1` decodes to `true`.

```json
{ "name": "p2p", "type": "boolean", "bits": [16, 16] }
```

**`enum`** reads its bit range as an unsigned integer and maps it to a label through `values`. Keys of `values` are unsigned integers written in decimal.

```json
{
  "name": "release",
  "type": "enum",
  "bits": [0, 21],
  "values": {
    "1": "1.0.0",
    "2": "1.1.0-beta",
    "3": "10.11.20260925^beta"
  }
}
```

#### Layout version

An implementation MAY reserve some payload bits as a layout version, so that its payload layout can change incompatibly without breaking the decoding of historical blocks. A `layout_version` reads its `bits` as an unsigned integer and uses the value to choose a layout from `layouts`. Each layout is an object with its own `fields`. An implementation SHOULD decide whether to reserve layout version bits before emitting any non-zero payload.

Adding a field over previously uncovered bits does not need a new layout version, because those bits were required to be `0` (see [Structural constraints](#structural-constraints)). A `layout_version` is only needed when an existing field changes or is removed.

#### Reserved names

A payload definition MUST NOT redefine information established by the registry or the enclosing signal. The following field names are reserved and MUST NOT be used:

- `name`, which comes from the registry entry;
- `id`, which comes from the `id` bits and the registry entry;
- `scheme`, which comes from the `scheme` bits;
- `definition_format`, which is defined by this section.

The schema rejects these names exactly as written. Consumers SHOULD compare field names against the reserved names case-insensitively.

#### Structural constraints

JSON Schema cannot express every relationship between bit ranges. A conforming payload definition MUST also satisfy the following:

1. The first value of every `bits` range MUST be less than or equal to the second.
2. A `boolean` field's two `bits` values MUST be equal.
3. Fields within the same layout MUST NOT overlap.
4. Field names within the same layout MUST be unique.
5. When `layout_version` is used, no field range in any of its layouts may overlap the `layout_version` bit range.
6. Every key in an `enum`'s `values` MUST be representable in the width of its `bits` range.
7. Every key in a `layout_version`'s `layouts` MUST be representable in the width of its `bits` range.

A producer MUST set every payload bit not covered by a field, or by `layout_version`, in the active layout to `0`.

#### Producer requirements for payload definitions

An implementation publishing a payload definition:

1. MUST publish valid JSON at a stable URL.
2. MUST declare `definition_format`.
3. MUST describe only the 22 payload bits.
4. MUST use the bit numbering defined in this section.
5. MUST satisfy the [structural constraints](#structural-constraints).
6. SHOULD keep field names stable once deployed.
7. MUST keep historical payload values decoding to the same values they had when emitted. The only permitted changes to a published layout are adding `enum` values and adding fields over previously uncovered bits. Any other change MUST be made under a new `layout_version` value.
8. SHOULD document in its `payload_documentation` what its decoded values mean, where the field names and labels alone do not make that clear.

Field names SHOULD be concise, stable, and suitable for use by generic software, for example `release`, `p2p`, `hardForkReady` or `networkMode`.

#### Consumer requirements

A consumer implementing this section:

1. MUST decode the 32-bit `minor` as defined in [Bit layout of the minor version](#bit-layout-of-the-minor-version).
2. MUST resolve `(scheme, id)` through the registry to find the entry and its `payload_definition`.
3. MAY retrieve the payload definition.
4. MUST interpret the definition according to its declared `definition_format`, and MUST treat a definition with an unsupported `definition_format` as absent rather than guess its meaning.
5. MUST preserve the numeric value of an `enum` or `layout_version` value not listed in the definition.
6. SHOULD NOT assume two implementations share semantics because they use the same field name.
7. SHOULD keep decoded payload values separate from registry and signal data rather than merge them into one namespace.

Decoding a payload does not necessarily mean a consumer can interpret it. A definition tells a consumer that bits `0 - 15` hold an integer called `releaseDay`. What that number refers to, and how it maps to source code, is documented by the implementation in its `payload_documentation`.

#### Example

An implementation registered with `id` `100` first identified each release by an enum. It later moved to version components and capability flags, and reserved bits `20 - 21` as a `layout_version` from the start so that it could.

Layout `1`:

```
+-----------+-------------+-------------+-------------+--------+--------+
|  layout   |    major    |    minor    |    patch    |  HFR   |  P2P   |
|  21 - 20  |   19 - 14   |   13 - 8    |    7 - 2    |   1    |   0    |
+-----------+-------------+-------------+-------------+--------+--------+
```

```json
{
  "definition_format": 0,
  "layout_version": {
    "bits": [20, 21],
    "layouts": {
      "0": {
        "fields": [
          {
            "name": "release",
            "type": "enum",
            "bits": [0, 19],
            "values": { "1": "1.0.0", "2": "1.1.0" }
          }
        ]
      },
      "1": {
        "fields": [
          { "name": "releaseMajor",  "type": "integer", "bits": [14, 19] },
          { "name": "releaseMinor",  "type": "integer", "bits": [8, 13] },
          { "name": "releasePatch",  "type": "integer", "bits": [2, 7] },
          { "name": "hardForkReady", "type": "boolean", "bits": [1, 1] },
          { "name": "p2p",           "type": "boolean", "bits": [0, 0] }
        ]
      }
    }
  }
}
```

A block with `minor = 310577508` (`0x12830964`) decodes as follows.

1. Split the `minor`: `scheme = 0`, `payload = 1213193` (`0x128309`), `id = 100`.
2. Resolve `(0, 100)` through the registry and fetch its `payload_definition`.
3. Read `layout_version` bits `20 - 21` of the payload: `1`.
4. Decode each field of layout `1`:

| Field           | Bits     | Raw | Decoded |
|-----------------|----------|-----|---------|
| `releaseMajor`  | 19 - 14  | 10  | `10`    |
| `releaseMinor`  | 13 - 8   | 3   | `3`     |
| `releasePatch`  | 7 - 2    | 2   | `2`     |
| `hardForkReady` | 1        | 0   | `false` |
| `p2p`           | 0        | 1   | `true`  |

An older block from the same implementation with `minor = 612` (`0x00000264`) has `payload = 2`. Its `layout_version` bits are `0`, so layout `0` applies and the payload decodes to `release = "1.1.0"`. Both blocks decode with the same document.

#### Format versioning

- A payload layout that an implementation needs but cannot express in any defined `definition_format` is grounds for a new one. The implementation SHOULD raise it as a counterexample against this CIP rather than describe the layout in prose.
- A future CIP MAY define a new payload definition format with additional field types or capabilities. Each new format MUST use a `definition_format` value greater than every existing one and MUST publish its own schema file.
- A future format MUST NOT change the meaning of an existing `definition_format` value.
- Payload definition formats are independent of `scheme`. The outer layout of the `minor` remains governed by `scheme`.

## Rationale: How does this CIP achieve its goals?

### Why the header minor version

The minor component of the header `protocol_version` has never been consulted by a ledger rule, therefore it does not require a breaking change. It is covered by the block producer's KES signature, and costs nothing to populate. Therefore, it is the cheapest possible channel for a per-block, producer-bound signal. It requires no hard fork, no new era, and zero additional bytes on chain.

Consumers already parse this field. Before each hard fork, explorers report the share of blocks carrying each major version as a proxy for upgrade readiness. Reading the minor version is the same code path.

Most importantly, this is the mechanism the ecosystem has already chosen. Matthias Benkort proposed fitting implementation identity inside the minor version during review of the CIP-0180 draft and at a node diversity workshop. Dingo has produced blocks on mainnet with the value `69`, Gerolamo followed with `67`, and Amaru has committed to the same approach. Any other proposal would be asking those three implementations to change working code and would leave blocks on mainnet without a standard interpretation.

### Why 8 bits for the identifier

The `id` needs to be large enough that no plausible number of block-producing implementations exhausts it, but small enough to leave room for the implementation to provide additional useful data. Eight bits gives us 239 assignable values. Two-letter codes, as suggested during the CIP-0180 review, would give more values (676), but would greatly reduce the usable bits for a payload. Eight bits gives us a reasonable allocation to do both.

### Why the identifier is in the low-order byte

The low-order byte preserves backwards compatibility. Dingo and Gerolamo have produced blocks that use a plain integer. Under this scheme, those values would decode as identifier `69` and `67` respectively, with an empty payload and scheme `0`. It also means that an explorer that already displays the decimal value of the minor version shows the identifier, and a reader who knows the registry can resolve it easily.

### Why identifiers 1 to 15 are reserved

cardano-node has, historically, used the minor version to differentiate between node releases within a single major protocol version. The values it has set on mainnet are:

| Major | Minors set |
|-------|------------|
| 3 - 5 | 0 |
| 6 - 7 | 0, 1, 2 |
| 8 - 9 | 0, 1 |
| 10    | 0, 2, 3, 7, 8 |

Reserving `1 - 15` keeps those blocks unambiguous and leaves headroom for further releases before cardano-node adopts this CIP. Sixteen is a nibble boundary, so a decoder can test `id < 16`.

### Why a scheme version

Two bits at the top of the field let a future CIP redefine the remaining thirty without ambiguity. Every value emitted so far has these bits clear, so this preserves backwards compatibility. Bitcoin's BIP 9 reserves the top bits of the block version field for the same reason.

The scheme bits also solve identifier exhaustion. Because retired identifiers are never reassigned, the 239 assignable values under scheme `0` can only shrink over time. If they run out, or if enough have been retired that the remaining range is awkward, a new CIP can define scheme `1` with the same layout and a fresh set of 254 identifiers. The registry is keyed by scheme for exactly this reason: an entry for identifier `69` under scheme `1` is unrelated to Dingo's identifier `69` under scheme `0`, and both remain decodable forever. Four schemes give roughly a thousand identifiers in total before the layout itself would need to change, which is well beyond any plausible number of block-producing implementations.

### Why the payload is implementation-defined

The obvious alternative is a fixed encoding of software version; for example six bits of major, eight bits each of minor and patch. However, implementations do not share a versioning scheme, and some implementations may choose to encode other information they find more important. Additionally, fixing semantics in this CIP would mean any change requires a new CIP, whereas the registry can be updated by the maintainer.

### Why the payload description format is part of this CIP

The payload definition format was first proposed as a separate CIP in [#1282](https://github.com/cardano-foundation/CIPs/pull/1282), so that any debate over it would not prevent this CIP from progressing. Keeping the two apart had real appeal; The identifier alone is enough to attribute a block to its claimed software, and a separate payload CIP would let an implementation pick whichever description method suited it, whether prose, this JSON format, or something else.

Two companion CIPs that need not both be followed would be worse for consumers, though. An explorer could not count on any payload being decodable, and payload data would drift towards being useful only to the team that emitted it. The two documents would also be maintained separately and fall out of alignment over time. One CIP gives consumers a single place to look and a single standard to implement.

For the same reason, a machine-readable definition is required for every non-zero payload. Allowing prose definitions as a fallback would bring back the per-implementation decoders this section exists to remove, and any payload described that way would be opaque to generic consumers. The cost is some flexibility. If an implementation finds a payload layout that `definition_format` `0` cannot express, that counterexample is a reason to extend the format in a future CIP, and in the meantime the implementation can still identify itself with a zero payload.

### Why the payload description is generic

Standardizing how a payload is described leaves each implementation free to decide what it contains and how its bits are allocated. A consumer that implements one small parser can decode every conforming payload, and no implementation has to invent its own description format or ship a decoder to explorers.

Decoding is not the same as interpreting. Amaru, for example, encodes a release as the number of days since 2026-01-01, because its versions are date based. A generic parser can turn the bits into that integer, but only Amaru's documentation says what the integer means. The format therefore names and types bit ranges, and leaves meaning to the `payload_documentation`.

### Why a small set of field types

`definition_format` `0` supports only unsigned integers, single-bit booleans, and enumerations, plus `layout_version` for versioned layouts. These cover the common cases of release identifiers, numeric version components and capability flags. A more expressive bit description language would make both producing and consuming definitions harder without materially improving the primary use case. New types can be added by a future `definition_format` if a real need appears.

### Why a registry in this repository

Cardano already maintains several registries here: CIP-0010 for transaction metadata labels, CIP-0067 for asset name labels, CIP-0005 for bech32 prefixes and CIP-0034 for chain identifiers. Each is a JSON file with a schema, amended by pull request and merged by the CIP editors. The process is public, versioned, and needs no new infrastructure.

Asking the CIP editors to manage editorial decisions is a real burden, and it is reasonable to ask whether it is appropriate. The precedents of other registry CIPs, which have processed dozens of registrations, suggest the load is manageable. Registrations here will likely be rare, since there are typically fewer node implementations than metadata standards.

### Why identifiers are never reassigned

Blocks are permanent and immutable. It is useful for historical record to have an immutable identifier too. Retirement therefore changes an entry's status and records a date; it never removes the entry or frees the identifier. Updating the `scheme` version may free retired identifiers.

### Why an explicit opt-out value

An operator who does not want to disclose their software could simply emit `0`, which is indistinguishable from an implementation that never adopted this CIP. However, ensuring conscious non-participation is distinguishable from inattention means both that operators can be sure their silence is recorded as a choice and consumers do not count them as legacy.

### Alternatives considered

**A free-form producer agent string in the block body.** The CIP-0180 draft by Samuel Leathers and Adam Dean proposed a UTF-8 string of up to 32 bytes, modelled on HTTP user agents and Ethereum's graffiti field. It would have been human-readable and expressive. It also required a new ledger era, which meant it could not ship before Dijkstra at the earliest, and it drew sustained objection during review. Markus Gufler estimated the storage cost at 60 to 80 MB per year and argued that a field no ledger rule can validate would attract content unrelated to its purpose, as graffiti has on Ethereum. Alexey Kuleshevich noted that any change to its meaning would require another era.

**Marker transactions.** The CPS-0036 draft lists small metadata-labelled transactions as a second candidate. They are flexible and could carry far more data than 32 bits. However, they are not necessarily bound to the block producer. They also cost fees. Nothing in this CIP prevents a later proposal from layering marker transactions on top of the identifier for richer, occasional signals.

**A compact enumeration in a new header field.** Also proposed during the CIP-0180 review, a two-byte identifier in the header would resemble this design but would still require a serialization change and a new era. Using the existing field achieves the same result with none of that cost.

### Backward compatibility

Every block produced before this CIP decodes to a value this document already accounts for: `0 - 15` for cardano-node releases, and `67` or `69` for Gerolamo and Dingo, which match their registry entries. Producers that never adopt this CIP continue to emit `0` and are attributed correctly either way.

## Path to Active

### Acceptance Criteria

- [x] `registry.json` merged with initial entries and at least one additional implementation registered through the PR process.
- [ ] At least two independent implementations producing blocks on mainnet or a public testnet with their registered identifier.
- [ ] At least one public explorer or dashboard decoding the identifier per this CIP.
- [ ] At least one public explorer or dashboard decoding payloads through registered payload definitions.

### Implementation Plan

- [x] Publish `registry.json` and `registry.schema.json` alongside this CIP.
- [x] Publish `payload-definition.format-0.schema.json` alongside this CIP.
- [ ] Reference decoder: a few lines in two languages, or a link to a shared test-vector file.
- [ ] Reach out to explorers (Cexplorer, PoolTool, Cardanoscan, AdaStat) and node teams.
- [ ] cardano-node: populate `self_reported_software_tag` with its registered identifier when building Dijkstra headers, in place of the release minor.

## References

- [CPS-0036 draft: Voluntary Block Producer Software Signalling](https://github.com/cardano-foundation/CIPs/pull/1260), Alex Moser and Matthias Benkort.
- [CIP-0180 draft: Block Producer Identification](https://github.com/cardano-foundation/CIPs/pull/1157), Samuel Leathers and Adam Dean.
- [Block Producer Payloads draft](https://github.com/cardano-foundation/CIPs/pull/1282), Adam Dean, merged into this CIP.
- [CIP-0202 draft: Node Observability Snapshot Protocol](https://github.com/cardano-foundation/CIPs/pull/1275), Markus Gufler.
- [JSON Schema 2020-12](https://json-schema.org/draft/2020-12).
- [Amaru `software_tag`](https://github.com/pragma-org/amaru/blob/main/crates/amaru-kernel/src/cardano/software_tag.rs), an example of a payload that decodes to an integer whose meaning is implementation-defined.
- [CIP-0001: CIP Process](../CIP-0001), [CIP-9999: Cardano Problem Statements](../CIP-9999).
- Registry precedents:
  - [CIP-0005: Common Bech32 Prefixes](../CIP-0005)
  - [CIP-0010: Transaction Metadata Label Registry](../CIP-0010)
  - [CIP-0034: Chain ID Registry](../CIP-0034)
  - [CIP-0067: Asset Name Label Registry](../CIP-0067)
- [RFC 2119: Key words for use in RFCs to Indicate Requirement Levels](https://datatracker.ietf.org/doc/html/rfc2119) and [RFC 8174: Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words](https://datatracker.ietf.org/doc/html/rfc8174).
- [Dijkstra CDDL, `header_version_info`](https://github.com/IntersectMBO/cardano-ledger/blob/master/eras/dijkstra/impl/cddl/data/dijkstra.cddl), cardano-ledger.
- [Change semantics of protocol version in BlockHeader](https://github.com/IntersectMBO/cardano-ledger/issues/5763), Alexey Kuleshevich, the ledger issue defining `self_reported_software_tag`.
- [Gerolamo](https://github.com/HarmonicLabs/gerolamo), Harmonic Labs.
- [Amaru](https://github.com/pragma-org/amaru), PRAGMA.
- [BIP 9: Version bits with timeout and delay](https://github.com/bitcoin/bips/blob/master/bip-0009.mediawiki) and [BIP 8: Version bits with lock-in by height](https://github.com/bitcoin/bips/blob/master/bip-0008.mediawiki).
- [Ethereum consensus specification, `BeaconBlockBody.graffiti`](https://github.com/ethereum/consensus-specs/blob/master/specs/phase0/beacon-chain.md#beaconblockbody), the 32-byte free-text field the CIP-0180 draft was modelled on.

## Acknowledgements

- Samuel Leathers and Adam Dean for the CIP-0180 draft.
- Adam Dean for the payload definition format, first proposed in #1282.
- Markus Gufler for pushing to merge the payload definition format into this CIP.
- Alex Moser and Matthias Benkort for the CPS-0036 draft.
- Matthias Benkort for proposing to fit identification into the minor version without a breaking change.
- Markus Gufler for the compact-encoding counter-proposal, the abuse analysis, and the operator privacy interviews.
- Robert Phair for the deliberate vs indeliberate non-participation requirement and early editorial guidance.
- Martin Lang for pressing on extensibility and hard-fork minor version semantics.
- Blink Labs (Dingo) and Harmonic Labs (Gerolamo) for initial implementations.

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
