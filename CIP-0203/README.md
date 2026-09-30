---
CIP: 203
Title: Block Producer Identifier Registry
Category: Consensus
Status: Proposed
Authors:
    - Josh Marchand <josh@sundae.fi>
Implementors: []
Discussions:
    - Original PR: https://github.com/cardano-foundation/CIPs/pull/?
    - CPS-0036 draft PR: https://github.com/cardano-foundation/CIPs/pull/1260
    - Early CIP-0180 draft: https://github.com/cardano-foundation/CIPs/pull/1157
Solution To:
    - CPS-0036? | Voluntary Block Producer Software Signalling: https://github.com/cardano-foundation/CIPs/pull/1260
Created: 2026-09-21
License: CC-BY-4.0
---

## Abstract

Cardano has become a multi-implementation network. Blocks on mainnet have been produced publicly by Dingo, Gerolamo, and the Haskell node, with more implementations quickly progressing. In an attempt to measure client diversity, Dingo is using the vestigial minor component of the header `protocol_version` to identify blocks produced by Dingo. The teams behind Geromalo and Amaru have also publicly committed to using the same method.

This CIP fixes a bit layout for the 32-bit field: an 8-bit implementation identifier, a 22-bit implementation-defined payload, and a 2-bit scheme version. It also establishes a machine-readable registry of identifiers in this repository with governing rules for assignment, update, and retirement. This is strictly voluntary, and requires no hard fork or changes in existing nodes.

## Motivation: Why is this CIP necessary?

For the full problem statement, read [the CPS-0036 draft](https://github.com/cardano-foundation/CIPs/pull/1260). In summary, while client diversity becomes a critical metric for Cardano's health, there is currently nothing that attributes individual blocks to a particular implementation. While there has been much discussion on the subject, including a [stalled proposal](https://github.com/cardano-foundation/CIPs/pull/1157), there is already a _de facto_ convention on chain. [Dingo](https://github.com/blinklabs-io/dingo) has begun producing blocks using the minor version `69`, [Geromalo](https://github.com/harmoniclabs/gerolamo) has produced blocks with minor version `67`, and other node implementations have agreed to follow that approach. Without a registry, there could be collisions between implementations, making that metric useless. Introducing a standard encoding scheme makes it simple for anyone to read the on-chain data. The proposed `CIP-0180` stalled because it required a new ledger era. Importantly, this approach avoids a fork completely.

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

Ledger rules only depend on the major version; the minor version has no impact on block validity, hard-fork initiation, or era selection. The header is signed by the pool's KES key under its operational certificate. Therefore, whatever value is placed there is attributable to a specific pool, even though it is self-declared. 

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
- A producer MAY set `payload` to any 22-bit value whose meaning is documented in the payload specification linked from its registry entry. A producer whose registry entry has no payload specification MUST set `payload` to `0`.
- The resulting `minor` MUST be encoded as a CBOR `uint` and MUST NOT exceed `4294967295` (`0xFFFFFFFF`).
- A consumer MUST NOT interpret `payload` or `id` when `scheme` is not `0`.
- A consumer MUST treat `payload` as opaque unless it implements the payload specification published for that `id`.

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
- Payload MAY be any 22-bit value whose meaning is documented at the URL in the implementation's registry entry. It MUST be `0` if the implementation publishes no payload specification.
- SHOULD give the operator a configuration option to emit `255` instead. Some SPOs have operational rules against disclosing software versions.
- SHOULD default to signalling. SHOULD allow a user of their software to opt-out of signalling.

### Registry

- Files: `registry.json` (data) and `registry.schema.json` (JSON schema). Both are in this directory.
- Entry fields (see schema): `scheme`, `id`, `name`, `status` (`active` | `retired`), `maintainers` (array of GitHub accounts), `repository`, `payload_specification` (URL or `null`), `registered` (date), `retired` (date or `null`), `description`.
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
- Payload format changes are the implementation's responsibility. The published payload specification MUST remain able to decode historical values, either by being backward compatible or by carrying its own version marker inside the 22 bits.

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

cardano-node has, historically, used the minor version to different between node releases within a single major protocol version. The values it has set on mainnet are:

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

### Implementation Plan

- [x] Publish `registry.json` and `registry.schema.json` alongside this CIP.
- [ ] Reference decoder: a few lines in two languages, or a link to a shared test-vector file.
- [ ] Reach out to explorers (Cexplorer, PoolTool, Cardanoscan, AdaStat) and node teams.

## References

- [CPS-0036 draft: Voluntary Block Producer Software Signalling](https://github.com/cardano-foundation/CIPs/pull/1260), Alex Moser and Matthias Benkort.
- [CIP-0180 draft: Block Producer Identification](https://github.com/cardano-foundation/CIPs/pull/1157), Samuel Leathers and Adam Dean.
- [CIP-0001: CIP Process](../CIP-0001), [CIP-9999: Cardano Problem Statements](../CIP-9999).
- Registry precedents:
  - [CIP-0005: Common Bech32 Prefixes](../CIP-0005)
  - [CIP-0010: Transaction Metadata Label Registry](../CIP-0010)
  - [CIP-0034: Chain ID Registry](../CIP-0034)
  - [CIP-0067: Asset Name Label Registry](../CIP-0067)
- [RFC 2119: Key words for use in RFCs to Indicate Requirement Levels](https://datatracker.ietf.org/doc/html/rfc2119) and [RFC 8174: Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words](https://datatracker.ietf.org/doc/html/rfc8174).
- [Gerolamo](https://github.com/HarmonicLabs/gerolamo), Harmonic Labs.
- [Amaru](https://github.com/pragma-org/amaru), PRAGMA.
- [BIP 9: Version bits with timeout and delay](https://github.com/bitcoin/bips/blob/master/bip-0009.mediawiki) and [BIP 8: Version bits with lock-in by height](https://github.com/bitcoin/bips/blob/master/bip-0008.mediawiki).
- [Ethereum consensus specification, `BeaconBlockBody.graffiti`](https://github.com/ethereum/consensus-specs/blob/master/specs/phase0/beacon-chain.md#beaconblockbody), the 32-byte free-text field the CIP-0180 draft was modelled on.

## Acknowledgements

- Samuel Leathers and Adam Dean for the CIP-0180 draft.
- Alex Moser and Matthias Benkort for the CPS-0036 draft.
- Matthias Benkort for proposing to fit identification into the minor version without a breaking change.
- Markus Gufler for the compact-encoding counter-proposal, the abuse analysis, and the operator privacy interviews.
- Alexey Kuleshevich for clarifying the ledger semantics of the header protocol version.
- Robert Phair for the deliberate vs indeliberate non-participation requirement and early editorial guidance.
- Martin Lang for pressing on extensibility and hard-fork minor version semantics.
- Blink Labs (Dingo) and Harmonic Labs (Gerolamo) for initial implementations.

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
