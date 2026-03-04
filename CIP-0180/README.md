---
CIP: 180
Title: Block Producer Identification
Category: Ledger
Status: Proposed
Authors:
    - Samuel Leathers <samuel.leathers@iohk.io>
    - Adam Dean <adam@crypto2099.io>
Implementors: []
Discussions:
    - Original PR: https://github.com/cardano-foundation/CIPs/pull/1157
Created: 2026-03-04
License: CC-BY-4.0
---

## Abstract

This CIP proposes a modification to Cardano blocks to be introduced in a
future ledger era Dijkstra:

**Block Producer Identification**: Adds a new optional 6th element to the
block body - an extensible `informational_data_set` containing a free-form text
field (max 32 bytes) similar to HTTP user-agent strings (RFC 9110, Section
10.1.5)<sup>1</sup> that allows block producers to identify their node
implementation and version.

This change enables block production analytics regarding node diversity and
upgrade progress. This proposal requires a new era as it modifies the block CBOR
serialization.

## Motivation: Why is this CIP necessary?

### Node Diversity Analytics

Currently, there is no standardized mechanism for block producers to identify
the node implementation and version they are using to forge blocks. This
information is valuable for analyzing historical block production data:

- **Ecosystem Health Analytics**: Understanding the stake-weighted distribution
  of different node implementations (cardano-node, Amaru, Dingo, Torsten,
  Gerolamo) across block production over epochs
- **Upgrade Progress Tracking**: Analyzing how quickly stake pool operators
  adopt new node versions by examining blocks produced over time
- **Network Resilience Assessment**: Identifying potential risks from
  monoculture where a single implementation dominates. With multiple node
  implementations in development, visibility into their adoption via block
  production is crucial for network resilience.
- **Testnet Feature Tracking**: On testnets, identifying which experimental
  features (Leios, Peras, Mithril) are being used by block producers
- **Debugging and Support**: Correlating block production issues with specific
  node versions through historical block analysis

Without this capability, the community lacks visibility into critical ecosystem
health metrics derived from on-chain block production data, especially as the
ecosystem diversifies with multiple block-producing implementations.

## Specification

As a Ledger category CIP per CIP-0084<sup>3</sup>, the specification below is
intended to be sufficiently detailed for inclusion in a formal ledger
specification. The complete CDDL specification for these changes will be added
to Cardano Blueprint<sup>2</sup> as the authoritative reference for all
implementations.

### Block Structure Modifications

This proposal adds a new optional element to the block body for block producer
identification, wrapped in an extensible `informational_data_set`:

**Modified Block Definition**:

```cddl
; Block structure - 6th element added for producer identification
block =
  [ header
  , transaction_bodies       : [* transaction_body]
  , transaction_witness_sets : [* transaction_witness_set]
  , auxiliary_data_set       : {* transaction_index => auxiliary_data}
  , invalid_transactions     : [* transaction_index]
  , informational_data_set / nil  ; NEW - optional
  ]

informational_data_set =
  [ producer_agent : tstr .size (1..32) / nil ]
```

The `informational_data_set` is a CBOR array designed for future extensibility:
additional fields can be appended in future eras without requiring a new era
boundary for the outer block structure.

### Producer Agent Field

Add a new optional text field inside `informational_data_set` for node
identification:

```cddl
producer_agent = tstr .size (1..32) / nil
```

**Field Specifications**:

- **Type**: UTF-8 text string or `nil`
- **Size**: 1-32 bytes when present as a string (matches Ethereum graffiti
  limit<sup>6</sup>); use `nil` to opt out
- **Format**: Recommended `<implementation>/<version>[+<features>]`
- **Examples**:
  - Mainnet: `"cardano-node/10.7.0"`, `"amaru/1.0.0"`, `"dingo/0.5.2"`
  - Testnets: `"cardano-node/11.0.0+leios"`, `"amaru/1.1.0+peras"`,
    `"dingo/0.6.0+leios+peras"`
- **Validation**: Nodes **MUST** accept any valid UTF-8 content within size limit
- **Optional**: Block producers **MAY** use `nil` for operational privacy

**Content Guidelines** (following RFC 9110, Section 10.1.5<sup>1</sup>):
- **SHOULD** use format `<implementation>/<version>[+<feature>...]`
- **MAY** append build metadata using `+` separator (e.g., "+leios",
  "+peras+mithril")
- Build metadata is particularly useful on testnets for identifying experimental
  features
- **MUST NOT** include advertising, pool metadata, or ticker symbols
- **SHOULD NOT** include pool-specific information that enables fingerprinting

### Validation Rules

**Consensus Layer**:
- Nodes **MUST** accept blocks with `informational_data_set` as `nil`, as a
  1-element array containing `nil`, or as a 1-element array containing any
  well-formed UTF-8 text string within the 32-byte limit
- Nodes **MUST NOT** reject blocks based on `producer_agent` content
- This field is purely informational and does not affect block validation

**Block Body Hash**:
- The `block_body_hash` in the header now includes the 6th element
  (`informational_data_set` or `nil`)
- This is acceptable for new era as all nodes must upgrade

### Era Transition

This proposal requires a new era and must be introduced as part of
a future ledger era Dijkstra.

**Breaking Changes**:

- Block structure changes from 5 to 6 elements
- Block body hash computation changes to include new 6th element
- Nodes running pre-hard-fork software cannot deserialize post-HF blocks

**Pre-HF (Conway)**:
- Blocks **MUST** use 5-element structure
- Block body hash computed over 5 elements

**Post-HF (Dijkstra)**:
- Blocks **MUST** use 6-element structure
- Block body hash computed over 6 elements (including `informational_data_set`)
- `informational_data_set` **MAY** be `nil` or a 1-element array containing
  `producer_agent` as `nil` or a text string (1-32 bytes)

**Historical Blocks**:
- Pre-HF blocks remain valid with original 5-element structure
- No retroactive changes to historical block interpretation

## Rationale: How does this CIP achieve its goals?

### Design Decisions

**Block Body Placement**:
We chose to place the producer identification field in the block body rather
than the header because:

- **Header Performance**: Headers are on the critical path for block propagation
  - keeping them minimal is important for network performance
- **Optional Without Overhead**: A `nil` value in the block body adds only 1
  byte, whereas header fields have higher overhead
- **Clear Separation**: Producer identification is metadata about the block, not
  part of chain validation
- **Future Extensibility**: The `informational_data_set` wrapper allows adding
  producer metadata fields in future without modifying the outer block structure
- **Era Transition**: Block body hash changes are acceptable in a new era as
  all nodes must upgrade anyway

**`informational_data_set` Wrapper**:
The `producer_agent` field is wrapped in an `informational_data_set` array
rather than placed directly in the block body because:

- **Future Extensibility**: Additional informational fields can be appended to
  the array in future eras without changing the outer block structure
- **Semantic Grouping**: Groups related informational metadata together cleanly
- **Minimal Overhead**: A `nil` top-level value still costs only 1 byte when not
  used; the array itself is only a few bytes when present

**Free-Form Text vs. Structured Data**:
We chose free-form text for the `producer_agent` field because:

- **Flexibility**: Allows block producers to include relevant information
  without protocol restrictions
- **Future-Proofing**: New node implementations (cardano-node, Amaru, Dingo,
  Torsten, Gerolamo, and future implementations) can participate without
  requiring protocol updates to register identifiers
- **Simplicity**: Easier to implement and maintain than structured versioning
  schemes or registry systems
- **User-Agent Precedent**: Follows successful patterns from HTTP (RFC 9110) and
  other protocols
- **Testnet Features**: Enables signaling of experimental features (Leios,
  Peras, Mithril) using build metadata notation

**1-32 Byte Range**:
The length range balances functionality with efficiency:

- **Minimum of 1**: Empty strings carry no useful information; `nil` already
  serves as the opt-out value, so a zero-length string would be redundant
- **Maximum of 32**: Accommodates implementation name, version, and build
  metadata
  - `"cardano-node/10.7.0"` = 19 bytes
  - `"cardano-node/11.0.0+leios"` = 25 bytes
  - `"torsten/1.0.0+leios+peras"` = 27 bytes
- **Ethereum Precedent**: Matches Ethereum's graffiti field size
  (32 bytes)<sup>6</sup>, a proven approach
- **Denial-of-Service Prevention**: Prevents abuse through excessive data
- **Network Efficiency**: Minimal storage impact. At Cardano's rate of ~1 block
  per 20 seconds (~1,576,800 blocks/year):
  - Typical case (19-byte strings): ~30-40 MB/year
  - Worst case (32-byte strings): ~50-63 MB/year
  - Current chain growth: ~45-50 GB/year
  - Impact: ~0.05-0.14% increase
- **Human-Readable**: Unlike hash-based approaches, readable by operators and
  analysts

**Optional Field**:
Making `producer_agent` optional via `nil`:

- **Gradual Adoption**: Block producers can adopt at their own pace
- **Privacy**: Permits operators who prefer not to disclose implementation
  details for operational security
- **Flexibility**: No requirement to populate even when node software supports it
- **Minimal Overhead**: `nil` adds only 1 byte when not used

### Alternative Approaches Considered

**Block Header Placement**:
Adding the field to the block header was rejected in favor of block body
placement because:

- Headers are on the critical path for block propagation - avoiding header
  changes preserves performance
- Block body allows cleaner optional semantics (`nil` = 1 byte)
- New era already changes block structure, so block body hash update is
  acceptable
- Preserves existing header semantics and validation logic

**Separate Registry System**:
A registration system where operators declare their implementation off-chain was
rejected because:

- Requires additional infrastructure and maintenance
- Cannot guarantee accuracy or timeliness
- Adds complexity for stake pool operators
- Does not provide block-by-block or epoch-level granularity
- Vulnerable to staleness and synchronization issues

**Hash-Based Node ID**:
Using a 32-byte Blake2b hash of the implementation name was rejected because:

- Not human-readable for operators analyzing blocks
- Requires off-chain registry to map hashes to implementations
- Loses version and build metadata information
- Adds complexity without meaningful benefit

**Mandatory Structured Format**:
A strictly defined format (enum-based or strict semver) was rejected because:

- Limits innovation and new implementation naming
- Requires protocol updates to add new implementations
- Reduces flexibility for build metadata on testnets
- Enforcement is difficult and potentially contentious
- Free-form text with recommended format provides better balance

**64-Byte vs 32-Byte Maximum**:
A 64-byte limit was considered but reduced to 32 bytes to:

- Match Ethereum graffiti precedent (proven approach)
- Reduce storage impact by ~50%
- Still accommodate all realistic use cases
- Discourage verbosity and fingerprinting concerns

## Security Considerations

### Isolation Attacks

The identification of which implementation created a block creates a potential
vector for isolation attacks, where adversarial stake pool operators could
modify their nodes to reject blocks produced by specific implementations. Such
attacks could:

- Create artificial bias in implementation usage statistics, making certain
  implementations appear less successful than they actually are
- Potentially impact network consensus if coordinated by operators controlling
  significant stake

**Mitigations and Detection**:

- **Optional Field**: The `informational_data_set` can be set to `nil` (or its
  `producer_agent` element set to `nil`), allowing operators to disable
  identification if isolation attacks become prevalent
- **Chain Density Detection**: If adversaries control only minor stake,
  isolation attacks would cause observable drops in chain density as they reject
  valid blocks, making such attacks detectable. However, if adversaries control
  significant stake, their chain would have greater density and the entire
  network would follow it, dropping blocks from the targeted implementation -
  requiring coordination among operators with substantial stake to execute
- **Economic Disincentive**: Operators performing isolation attacks harm the
  network in which they hold stake, creating economic disincentive against such
  behavior
- **Community Detection**: Systematic rejection of valid blocks from specific
  implementations would be detectable through block production analytics and
  could trigger community response
- **Consensus Rules**: The consensus layer does not use the `producer_agent`
  field for validation, limiting the technical scope for automated
  discrimination

### Node Software Version Discrimination

The `producer_agent` field could theoretically enable discrimination based on
node software version. However:

- The `producer_agent` field is purely informational and **MUST NOT** be used
  for block validation
- Consensus rules explicitly require accepting blocks with any well-formed
  `producer_agent` text string or `nil`
- This field does not affect the actual protocol version the block conforms to,
  which continues to be determined by the `protocol_version` field in the header

### Operator Fingerprinting

Overly detailed agent strings could enable fingerprinting of individual
operators. The specification mitigates this through:

- 32-byte size limit preventing extensive metadata
- Usage guidelines explicitly discouraging inclusion of pool-specific
  information (ticker symbols, geographic data, etc.)
- Optional field allowing privacy-conscious operators to omit identification
  entirely via `nil`
- Recommended format focuses on implementation and version only

## Limitations

### Block Production Required

This mechanism only provides data for nodes that actually produce blocks. A node
running an alternative implementation that holds no stake, or a relay node, will
leave no on-chain trace. The `producer_agent` field reflects the software that
forged a given block — nothing more. Nodes with no stake or low luck in a given
epoch may produce no blocks at all, making their software invisible during that
period.

## CBOR Encoding Examples

The 6th block element is encoded as either `nil` (1 byte) or a 1-element array:

```
-- With producer agent string
Diagnostic: ["cardano-node/10.7.0"]
Hex: 81                              -- array(1)
     73                              -- text(19)
     636172 64616e6f2d6e6f64652f31302e372e30  -- "cardano-node/10.7.0"

-- Producer agent omitted
Diagnostic: [nil]
Hex: 81 f6                           -- array(1), nil

-- No informational data
Diagnostic: nil
Hex: f6                              -- nil (1 byte)
```

## Path to Active

### Acceptance Criteria

- [ ] CDDL schema updates merged into Cardano Blueprint as the authoritative
  specification
- [ ] All node implementation teams have reviewed and agreed upon the
  specification (cardano-node, Amaru, Dingo, Torsten, Gerolamo)
- [ ] Implementation present in cardano-node (Haskell) released as part of
  Dijkstra hard fork
- [ ] Implementation present in Amaru (Rust)
- [ ] Implementation present in Dingo (Go)
- [ ] Implementation present in Torsten (Rust)
- [ ] Implementation present in Gerolamo (TypeScript)
- [ ] The feature is activated on mainnet through the Dijkstra new era
- [ ] Chain analytics tools have been updated to parse and display producer
  agent data
- [ ] Block explorers correctly display blocks from both pre- and post-hard-fork
  eras

### Implementation Plan

This CIP requires coordination across all node implementations as part of the
Dijkstra era hard fork. Each implementation (cardano-node, Amaru, Dingo,
Torsten, Gerolamo) must add the `informational_data_set` as the 6th block
element, update the block body hash computation accordingly, and add
configuration for the `producer_agent` string. All implementations must follow
the Cardano Blueprint CDDL specification exactly and handle the Conway →
Dijkstra era boundary correctly. Cross-implementation block validation testing
on development and pre-production networks should be completed before mainnet
activation.

## References

- <sup>1</sup>
  [RFC 9110 — User-Agent String](https://www.rfc-editor.org/rfc/rfc9110.html#name-user-agent) —
  The HTTP Semantics specification
- <sup>2</sup>
  [Cardano Blueprint](https://cardano-scaling.github.io/cardano-blueprint/) — The
  authoritative CDDL specification for Cardano ledger structures
- <sup>3</sup>
  [CIP-0084: Cardano Ledger Evolution](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0084) —
  Process for ledger-related CIPs
- <sup>4</sup>
  [Cardano Blockchain's Compact Size and Transaction Statistics (Feb 2025)](https://blockchain.news/flashnews/cardano-blockchain-s-compact-size-and-transaction-statistics) —
  chain size ~186 GB as of February 2025
- <sup>5</sup>
  [Daedalus Size Growth Discussion (May 2022)](https://forum.cardano.org/t/daedalus-size-growth-what-is-the-plan/101221) —
  chain size ~60 GB as of mid-2022
- <sup>6</sup>
  [Ethereum Consensus Spec — Beacon Block Body](https://github.com/ethereum/consensus-specs/blob/dev/specs/bellatrix/beacon-chain.md#beaconblockbody) —
  Ethereum graffiti field (32 bytes)
- <sup>7</sup>
  [Cardano Ledger Specifications](https://github.com/IntersectMBO/cardano-ledger) —
  Ledger CDDL specifications by era

## Acknowledgements

Thanks to the Cardano community for discussions around node diversity and the
importance of block production analytics. Special thanks to the teams working on
alternative node implementations (Amaru, Dingo, Torsten, and Gerolamo) whose
efforts toward ecosystem diversification motivated this proposal, and to the CIP
editors for feedback on the block body placement approach.

## Copyright

This CIP is licensed
under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
