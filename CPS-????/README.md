---
CPS: 24
Title: Canonical CBOR Serialization
Category: Tools
Status: Open
Authors:
    - Hinson Wong <wongkahinhinson@gmail.com>
    - Tsz Wai Wu <tszwaiwu.96@gmail.com>
Proposed Solutions: []
Discussions:
    - https://github.com/cardano-foundation/CIPs/pull/1109
Created: 2025-10-29
License: CC-BY-4.0
---

## Abstract

There is no canonical CBOR serialization standard in Cardano. While this is a delibrate design choice initially, standardizing it has growing popularity in Cardano developer community as evidenced by developer meetups such as Cardano Builder Fest 2025 hosted in Vietnam. This CPS outlines the motivation of the growing concern of fragmented CBOR serialization patterns across in the community.

## Problem

<!-- A more elaborate description of the problem and its context. This section should explain what motivates the writing of the CPS document. -->

The Cardano ledger accepts any valid CBOR encoding for transactions and on-chain data. While this flexibility was intentional to encourage ecosystem diversity, it has created significant interoperability challenges as the tooling landscape has matured. The same logical data can be encoded in multiple ways (map key ordering, integer encoding, definite vs. indefinite length, etc.), leading to different byte representations and transaction hashes.

### Core Issues

**Transaction Hash Instability**: When a transaction is passed between tools or wallets for signing, each may re-serialize it differently. Since transaction hashes are computed over CBOR bytes, logically identical transactions produce different hashes. This breaks:

- Multi-signature workflows where each signer's wallet may re-serialize the transaction
- Cross-tool transaction building where fee calculations depend on exact byte size

**Script Inconsistencies**: Smart contracts suffer from unpredictable script hashes, reference script mismatches across tools. The same compiled script may produce different hashes depending on the library used to apply parameters or cbor serialize the script.

**Development Friction**: Developers face increased testing burden across multiple libraries and wallets, library-specific test fixtures, vendor lock-in risks, and debugging challenges that require logical rather than byte-level comparison.

### Ecosystem Impact

The lack of standardization creates:

- **Security risks**: Hard-to-diagnose bugs and complex audit requirements due to multiple serialization paths
- **Community overhead**: High support burden in addressing serialization issues and maintaining multiple strategies
- **Adoption barriers**: Unpredictable behavior discourages enterprise adoption and increases new developer friction

This problem has become urgent as sophisticated DApps require cross-tool interoperability, multi-signature usage grows, and community feedback (e.g., Cardano Builder Fest 2025) has identified this as a critical pain point.

## Use cases

<!-- A concrete set of examples written from a user's perspective, describing what and why they are trying to do. When they exist, this section should give a sense of the current alternatives and highlight why they are not suitable. -->

**Cross-Library DApp Development**: A DApp developer builds transactions with Lucid in their frontend, but users sign with various wallets built on cardano-serialization-lib or pycardano. Canonical serialization ensures the transaction built equals the transaction signed.

**Script Hash Consistency**: A developer publishes a reference script on-chain, then references it from their off-chain code. Currently, locally computed script hashes may not match the on-chain version due to encoding differences. Canonical serialization guarantees hash consistency across compilation and deployment pipelines.

**Library Maintainers**: Serialization library authors currently must support multiple encoding strategies for compatibility. With a standard, they can focus on a single canonical implementation, reducing maintenance burden and improving deserialization reliability.

## Goals

<!-- A list of goals and non-goals a project is pursuing, ranked by importance. These goals should help understand the design space for the solution and what the underlying project is ultimately trying to achieve.

Goals may also contain requirements for the project. For example, they may include anything from a deadline to a budget (in terms of complexity or time) to security concerns.

Finally, goals may also serve as evaluation metrics to assess how good a proposed solution is. -->

### Primary Goals

1. **Establish a canonical CBOR standard**: A CIP that specifies deterministic encoding rules for all Cardano transaction and on-chain data structures, with clear guiding principles for choosing between encoding alternatives.

2. **Achieve ecosystem adoption**: Widespread implementation across major serialization libraries (cardano-serialization-lib, pycardano, Lucid, Aiken, etc.) and wallets (Nami, Eternl, Lace, Yoroi, etc.), ensuring cross-tool interoperability.

3. **Provide implementation guidance**: Comprehensive documentation including test vectors, reference implementations or validation tools, and migration paths for existing tooling.

### Optional Goals

4. **Ledger-level enforcement**: If community consensus supports it, implement validation rules in the ledger to guarantee compliance (requires hardfork and backward compatibility strategy).

### Success Criteria

This CPS is successfully resolved when:

- A canonical CBOR serialization CIP reaches "Active" status with clear specifications
- At least 80% of major libraries and wallets demonstrate compliance
- Serialization-related issues in community support channels decrease measurably
- Cross-tool transaction building becomes reliably predictable

### Requirements for Solutions

A good solution must:

- **Technical clarity**: Unambiguous encoding rules for all covered data structures
- **Guiding principles**: Clear rationale for choosing specific encodings (efficiency, simplicity, adoption)
- **Comprehensive scope**: Address transactions, scripts, datums, redeemers, and specify what is out-of-scope
- **Path to Active**: Detailed adoption strategy including timeline, stakeholder coordination, and migration tooling
- **Evolution mechanism**: Process for handling future hardforks and new ledger types
- **Verification**: Test vectors or validation tools to verify implementation compliance

## Open Questions

### What are the guiding principles for choosing the canonical form?

When multiple valid CBOR encodings exist, how should we decide which becomes canonical?

- **Efficiency**: Minimize transaction size (e.g., smallest integer encoding, definite over indefinite length)
- **Simplicity**: Choose the most straightforward encoding to implement and verify
- **Existing adoption**: Align with the most widely-used pattern in current tooling (e.g., cardano-serialization-lib as de facto standard)
- **Trade-offs**: How should we balance these potentially conflicting dimensions?

### Should the standard be enforced at the ledger level?

**Enforcing** (ledger validation):

- Pros: Guarantees compliance; eliminates ambiguity; strongest interoperability guarantee
- Cons: Breaks backward compatibility; requires hard fork; existing tools and transactions may become invalid; potentially impractical migration burden

**Not enforcing** (off-chain standard only):

- Pros: No backward compatibility concerns; existing transactions remain valid; easier initial adoption
- Cons: Voluntary compliance may be insufficient; fragmentation may persist; no guarantee of universal adoption

### How should canonical serialization evolve with hardforks?

When a hardfork introduces new ledger types or transaction fields, the CBOR encoding for these new structures must be decided. This raises critical workflow questions:

**Pre-hardfork standardization**: Should the canonical encoding for new ledger types be specified as part of the hardfork proposal itself? This would prevent fragmentation but may slow down hardfork timelines.

**Implementation sequencing**: Should serialization libraries wait for a canonical standard to be ratified before implementing support for new ledger types? Or should they implement independently and risk creating incompatible encodings?

**Governance and responsibility**: Who should define the canonical encoding for new types?

- The team proposing the hardfork (e.g., IOG, Intersect ledger team)?
- CIP editors through a formal proposal process?
- Library maintainers through community consensus?
- A designated standardization working group?

## Copyright

This CPS is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
