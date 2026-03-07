---
CIP: XXXX
Title: Block Producer Identification and Protocol Version Signaling
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

This CIP proposes two enhancements to Cardano block headers to be introduced in
a future ledger era (potentially Dijkstra): (1) the addition of a free-form text
field for block producers to identify their node software and version, similar
to a user-agent string (RFC 9110, Section 10.1.5)<sup>1</sup>, and (2)
redefining the block version field to represent the maximum protocol version
supported by the node forging the block. These changes enable network analytics
regarding node diversity and upgrade progress while resolving ambiguities in
protocol version reporting. This proposal requires a hard fork as it modifies
the block header CBOR serialization.

## Motivation: Why is this CIP necessary?

### Node Diversity Analytics

Currently, there is no standardized mechanism for block producers to identify
the node implementation and version they are using to forge blocks. This
information is valuable for:

- **Ecosystem Health Monitoring**: Understanding the distribution of different
  node implementations (e.g., cardano-node, and emerging alternatives like Dingo
  and Amaru) across the network
- **Upgrade Progress Tracking**: Analyzing how quickly stake pool operators
  adopt new node versions
- **Network Resilience Assessment**: Identifying potential risks from
  monoculture where a single implementation dominates. With multiple node
  implementations in development (including Dingo and Amaru), visibility into
  their adoption is crucial for network resilience.
- **Debugging and Support**: Helping correlate block production issues with
  specific node versions

Without this capability, the community lacks visibility into critical network
health metrics, especially as the ecosystem diversifies with multiple
block-producing implementations.

### Protocol Version Signaling Ambiguity

The current block version field in block headers has limitations:

1. **Limited Future Version Reporting**: Current consensus rules allow nodes to
   report a protocol version up to 1 higher than the currently active protocol
   version, but reject blocks reporting versions 2 or more higher. This limits
   the ability of nodes to signal readiness for protocol versions beyond the
   immediate next upgrade.
2. **Unclear Semantics**: The meaning of the block version field is ambiguous -
   it could represent the version the block conforms to, or the version the node
   supports

By redefining this field as the maximum supported protocol version, we:

- Enable nodes to signal their upgrade readiness
- Allow analytics of network preparedness for protocol upgrades
- Provide clear semantics for the version field
- Maintain backward compatibility during transitions

## Specification

As a Ledger category CIP per CIP-0084<sup>3</sup>, the specification below is
intended to be sufficiently detailed for inclusion in a formal ledger
specification. The complete CDDL specification for these changes will be added
to Cardano Blueprint<sup>2</sup> as the authoritative reference for all
implementations.

### Block Producer Identification Field

Add a new optional field `block_producer_agent` to the block header structure:

**CDDL Definition**:

```cddl
block_producer_agent = tstr .size (0..64)
```

**ABNF Grammar**:

```abnf
block-producer-agent = product *(SP product) ; Max 64 bytes UTF-8
product = token ["/" version]
token = 1*agent-char
version = 1*agent-char
agent-char = ALPHA / DIGIT / "-" / "." / "_"
```

**Usage Guidelines**:

Following the principles of RFC 9110, Section 10.1.5<sup>1</sup>, the
`block_producer_agent` field is intended solely to identify the node
implementation and its version. Block producers:

- **SHOULD** limit the field to what is necessary to identify the implementation
  and version — a sender **MUST NOT** include advertising, pool metadata, stake
  pool ticker symbols, or other nonessential information within the field
- **SHOULD NOT** generate information in the version portion that is not a
  version identifier (i.e., successive versions of the same implementation ought
  to differ only in the version portion)
- **SHOULD NOT** generate needlessly fine-grained detail, as overly long values
  increase block header size and the risk of operator fingerprinting
- **SHOULD NOT** use the implementation tokens of other implementations to
  declare compatibility with them, as this circumvents the purpose of the field

**Field Properties**:

- **Type**: Text string (UTF-8 encoded)
- **Maximum Length**: 64 bytes
- **Content**: Free-form text chosen by the block producer
- **Recommended Format**: `<implementation>/<version>` with optional
  space-separated additional products (e.g., `cardano-node/10.1.3`,
  `cardano-node/10.1.3 mithril/2.0.0`, `amaru/1.0.0 eu-central`)
- **Validation**: Nodes **MUST** accept blocks with any valid UTF-8 content in
  this field, including empty strings
- **Optional**: Block producers **MAY** omit this field (treated as empty string
  if absent)

**Serialization**:
The field is added to the block header CBOR structure in the new ledger era.
This change requires a hard fork as it modifies the block header serialization
format.

### Protocol Version Signaling

Redefine the semantics of the existing block header version field:

```cddl
; Current definition (reinterpreted)
block_version = [major: uint, minor: uint]
```

**New Semantics**:

- The `block_version` field **SHALL** represent the maximum protocol version
  that the node forging this block claims to support
- Nodes **MAY** report any protocol version, including versions higher than what
  the current network protocol supports
- Consensus rules **SHALL NOT** reject blocks solely because the reported
  version is unknown or higher than the current protocol version
- The version reported **SHOULD** reflect the actual capabilities of the node
  implementation

**Validation Rules**:

- Nodes **MUST** accept blocks with any well-formed version tuple
- Nodes **MUST NOT** use the block version field for block validation beyond
  CBOR structure validation
- The version field remains purely informational for analytics and does not
  affect consensus

### Backward Compatibility

This proposal requires a hard fork and must be introduced as part of a future
ledger era (potentially Dijkstra or later).

**Breaking Changes**:

- The block header CBOR serialization changes with the addition of the
  `block_producer_agent` field
- Nodes running pre-hard-fork software will not be able to deserialize blocks
  produced after activation
- This is a standard era transition requiring coordinated network upgrade

**Era Transition**:

- Prior to the hard fork activation, blocks **MUST NOT** include the
  `block_producer_agent` field
- After hard fork activation, blocks **MAY** include the field (it remains
  optional)
- The protocol version validation rules change at the hard fork boundary

**Historical Blocks**:

- Blocks produced before the hard fork remain valid and unchanged
- The new protocol version semantics do not retroactively affect interpretation
  of historical blocks

## Rationale: How does this CIP achieve its goals?

### Design Decisions

**Free-Form Text vs. Structured Data**:
We chose free-form text for the block producer agent field because:

- **Flexibility**: Allows block producers to include relevant information
  without protocol restrictions
- **Future-Proofing**: New node implementations (such as Dingo and Amaru) can
  participate without requiring protocol updates to register their identifiers
- **Simplicity**: Easier to implement and maintain than structured versioning
  schemes
- **User-Agent Precedent**: Follows successful patterns from HTTP and other
  protocols

**64-Byte Limit**:
The length limit balances:

- **Sufficient Space**: Accommodates implementation name, version, and optional
  additional product tokens
- **Denial-of-Service Prevention**: Prevents abuse through excessive data in
  block headers
- **Network Efficiency**: Minimal impact on block propagation and storage. At
  Cardano's rate of approximately 1 block every 20 seconds (~1,576,800 blocks
  per year), the worst-case annual ledger growth with every block using the full
  64-byte field is approximately 101 MB — roughly 0.2% of the current annual
  chain growth of ~45–50 GB<sup>4,5</sup>. In practice, typical agent strings (
  e.g.,
  `cardano-node/10.7.0` at 19 bytes) would add closer to 30 MB per year

**Optional Field**:
Making the field optional:

- **Gradual Adoption**: Block producers can adopt at their own pace after the
  hard fork
- **Privacy**: Permits operators who prefer not to disclose implementation
  details
- **Flexibility**: No requirement to populate the field even when node software
  supports it

**Reusing Existing Version Field**:
Rather than adding a new field for the protocol version:

- **Efficiency**: No additional header space required
- **Semantic Clarity**: Provides clear meaning to an existing but ambiguous
  field
- **Simplicity**: Fewer changes to block structure

### Analytics Use Cases

**Node Diversity Metrics**:
Network observers can parse the `block_producer_agent` field from recent blocks
to calculate:

- Market share of different implementations (e.g., cardano-node vs. Dingo vs.
  Amaru)
- Version distribution curves for each implementation
- Upgrade velocity metrics across implementations
- Geographic or stake-weighted implementation distribution
- Adoption rates of alternative implementations as they enter block production

**Protocol Upgrade Readiness**:
By analyzing the `block_version` field, the community can assess:

- Percentage of stake ready for upcoming protocol upgrades
- Timeline projections for safe hard fork activation
- Identification of operators who may need support for upgrades

### Alternative Approaches Considered

**Separate Registry System**:
A registration system where operators declare their implementation off-chain was
rejected because:

- Requires additional infrastructure and maintenance
- Cannot guarantee accuracy or timeliness
- Adds complexity for stake pool operators
- Does not provide block-by-block granularity

**Mandatory Structured Format**:
A strictly defined format (like semver) was rejected because:

- Limits innovation and new implementation naming
- Requires protocol updates to accommodate changes
- Reduces flexibility for operators
- Enforcement is difficult and potentially contentious

**New Version Field**:
Adding a separate field for the max supported protocol version was rejected
because:

- Increases block header size unnecessarily
- The existing version field's semantics were already unclear
- Redefining existing fields is more efficient than proliferation

## Path to Active

### Acceptance Criteria

- [ ] CDDL schema updates merged into Cardano Blueprint as the authoritative
  specification
- [ ] All node implementation teams (cardano-node, Dingo, Amaru) have reviewed
  and agreed upon the specification
- [ ] Implementation present in cardano-node (Haskell) and released as part of a
  hard fork-capable version
- [ ] Implementation present in Dingo (Rust) with support for the new block
  header format
- [ ] Implementation present in Amaru (Rust) with support for the new block
  header format
- [ ] The feature is activated on mainnet through a hard fork (e.g., Dijkstra
  era)
- [ ] At least 60% of blocks produced within one epoch after hard fork
  activation include the `block_producer_agent` field
- [ ] Network monitoring tools have been updated to parse and display the new
  fields
- [ ] Block explorers correctly display blocks from both pre and post-hard-fork
  eras

### Implementation Plan

This CIP requires a hard fork and must be coordinated across all node
implementations with a future ledger era activation (potentially Dijkstra).

**Phase 1 - Specification and Review**:

- Finalize CDDL schema for block header changes in Cardano Blueprint
- Review by all node implementation teams (cardano-node, Dingo, Amaru)
- Address feedback and concerns from all implementations
- Coordinate with era planning discussions
- Ensure the specification is implementation-agnostic and follows Cardano
  Blueprint standards

**Phase 2 - Parallel Implementation**:

- **Haskell (cardano-node)**:
    - Implement block header changes according to Cardano Blueprint
      specification
    - Update cardano-node to populate the `block_producer_agent` field
    - Modify consensus rules to accept any block version value
    - Add configuration options for a block producer agent string
- **Go (Dingo)**:
    - Implement block header changes according to Cardano Blueprint
      specification
    - Add support for producing and validating blocks with the new format
    - Implement configuration for block producer agent string
- **Rust (Amaru)**:
    - Implement block header changes according to Cardano Blueprint
      specification
    - Add support for producing and validating blocks with the new format
    - Implement configuration for block producer agent string
- **All implementations**:
    - Follow Cardano Blueprint CDDL specification for serialization and
      deserialization
    - Ensure proper era-boundary handling
    - Coordinate on timing and feature parity

**Phase 3 - Cross-Implementation Testing**:

- Integration testing on development networks with all implementations
- Cross-validation: blocks produced by each implementation are validated by
  others
- Preview and pre-production network deployment with mixed implementations
- Compatibility testing with existing tools and explorers
- Hard fork transition testing across all implementations

**Phase 4 - Hard Fork Activation**:

- Coordinate with Intersect MBO and all node implementation teams
- Community announcement and stake pool operator notification
- Include in planned era hard fork (e.g., Dijkstra)
- Mainnet activation at era boundary
- Monitor block production from all implementations

**Phase 5 - Ecosystem Adoption**:

- Block explorers add display of block producer agent
- Monitoring tools add analytics dashboards for implementation diversity
- Community outreach for adoption across all implementations
- Documentation and best practices for each implementation

## References

- <sup>1</sup>
  [RFC 9110 — User-Agent String](https://www.rfc-editor.org/rfc/rfc9110.html#name-user-agent) —
  The HTTP Semantics specification
- <sup>2</sup>
  [Cardano Blueprint](https://github.com/input-output-hk/cardano-ledger) — The
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

## Acknowledgements

Thanks to the Cardano community for discussions around node diversity and the
importance of network observability. Special thanks to the teams working on
alternative node implementations (Dingo and Amaru) whose efforts toward
ecosystem diversification motivated key aspects of this proposal.

## Copyright

This CIP is licensed
under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
