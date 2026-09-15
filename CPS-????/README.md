---
CPS: TBD 
Title: Digital Product Passports
Category: Tools
Status: Open
Authors:
- David Clark <david.clark@cardanofoundation.org>
Proposed Solutions: []
Discussions: [https://github.com/cardano-foundation/CIPs/pull/1114,https://github.com/cardano-foundation/cardano-dpp-standards]
Created: 2025-11-24
License: CC-BY-4.0
---

## Abstract

The European Union's Ecodesign for Sustainable Products Regulation (ESPR) mandates Digital Product Passports (DPPs) for numerous product categories, with the first compliance deadline on 18 February 2027 for certain large batteries. These passports must provide tamperproof, verifiable information about products' materials, origin, lifecycle, and compliance throughout the supply chain.

Since this CPS was first drafted, the EU-level foundations have moved from proposal to operation: the central DPP Registry went live in July 2026, and the first six of eight CEN-CENELEC system standards (the EN 1821x series) are now published and cited as harmonised standards. Despite this, the Cardano ecosystem still lacks standardized approaches for anchoring DPP data on-chain, creating product identity assets, and enabling multi-party verification against this now-published EU baseline. This fragmentation risks incompatible implementations, poor interoperability, and a missed opportunity for Cardano to become a reference platform for supply chain transparency and regulatory compliance.

This CPS articulates the problem space and establishes goals for comprehensive DPP standards that enable regulatory compliance, ecosystem interoperability, and practical implementation.

## Problem

### Background

Digital Product Passports are becoming mandatory under EU regulation to support:

- **Circular economy goals** - Tracking materials for reuse and recycling
- **Consumer transparency** - Providing verifiable product information
- **Regulatory compliance** - Proving adherence to safety, sustainability, and origin requirements
- **Supply chain accountability** - Creating tamperproof audit trails across multiple parties

The ESPR affects industries including textiles, electronics, batteries, construction materials, furniture, and more, impacting millions of businesses globally. Practical implementation is already underway for batteries in 2026 (the DPP Registry is live, the core CEN-CENELEC standards are published, and a public testing environment is available), ahead of the mandatory compliance deadline of 18 February 2027 (EV, light-transport, and industrial batteries above 2 kWh). The textile delegated act is expected in 2027, but its compliance deadline follows the standard 18-24 month transition period, landing realistically in 2028-2029; other sectors phase in through 2030.

DPP implementations must integrate with existing global product identification systems, particularly GS1 standards (GTINs for product identification, Digital Link for web-based resolution, and EPCIS for event tracking). This integration is essential for interoperability with existing supply chain infrastructure.

The EU DPP Registry went live on 20 July 2026 alongside a public testing environment, following adoption of its Implementing Regulation. The Registry is a shared index rather than a central data store: it holds unique identifiers and registration metadata (plus a verification and logging framework), while the DPP content itself remains hosted in a decentralised manner by the economic operator or a DPP service provider. Registration is available through a secure UI or an API, and a free semantic repository of machine-readable data models is provided to support interoperability.

Additionally, CEN-CENELEC Joint Technical Committee 24 (JTC 24) has published the first six of eight planned system standards for DPP data models and interoperability (the EN 1821x series), covering unique identifiers, data carriers, data exchange protocols, data storage/persistence, APIs, and system interoperability. These six were cited as harmonised standards in the Official Journal in July 2026, giving conforming implementations a presumption of conformity under ESPR. The remaining two standards, covering access rights/security and data authentication, are expected to follow shortly after. DPP implementations on Cardano should now be designed for direct alignment with this published EN 1821x series, rather than against a moving target.

### Current State

While Cardano provides foundational capabilities through CIP-25 and CIP-68 metadata standards, the ecosystem lacks:

- Standardized data schemas for product lifecycle information
- Guidance on linking physical products (GTINs, QR codes) to on-chain identities
- Reference architectures for different implementation patterns (static passports, event logs, high-throughput and batch/rollup registration, privacy-preserving proofs)
- Established approaches for multi-party coordination across supply chains
- Validation frameworks for regulatory compliance claims

A companion Cardano Foundation working group, which began shortly before this CPS was first drafted, has been publishing early architectural patterns for DPP on Cardano (a draft v0.1 solution-pattern blueprint, open for community feedback), but it has not yet resolved into a ratified reference architecture or standard, so the gaps above remain open.

This creates a "build from scratch" situation where businesses face:

- Incompatible implementations that cannot interoperate
- Expensive custom development for each project
- Uncertainty about regulatory compliance
- Duplication of effort solving common problems

### Why This Matters

**Market Opportunity:**

- EU mandate affects 450 million consumers across 27 countries
- Billions of products across multiple lifecycles annually
- Mandatory compliance creates non-speculative demand
- Opportunity to build general DPP solutions on Cardano, competing on the same commercial terms as conventional-stack platforms
- A distinct opportunity to lead specifically in the DPP problems (below) where a shared ledger provides genuine technical differentiation

**Enterprise Reality:** ESPR regulations are technology-neutral, and the pattern gaining traction through 2026 is hybrid rather than blockchain-native: a public ledger serves as a neutral verification/anchoring layer beneath a standards-compliant passport, while day-to-day operational data stays in existing ERP/PIM systems. This is visible both in the EU's own reference architecture work (CIRPASS-2) and in how Cardano is currently being positioned for DPP: as an integrity layer anchoring evidence over existing product-information systems, rather than as the primary data store. Industries with long product lifecycles (batteries, automotive, textiles) are the ones most often citing this pattern, for immutable audit trails and cross-organizational coordination without surrendering ownership of operational data.

**Where a Shared Ledger Still Adds Value:**

ESPR compliance itself does not require a ledger, and the working assumption behind this CPS should be that most DPP implementations will be, correctly, satisfied by the conventional VC/SD-JWT/GS1-Digital-Link stack alone. A blockchain-native DPP provider and a conventional-stack provider are not really offering competing answers to compliance. They are different entry points to the same optional layer, since a conventional platform can anchor into a ledger just as readily as a blockchain-native one can serve compliance-only clients without ever exposing the ledger to them. The layer becomes relevant once a client wants something beyond the compliance floor. Some of the areas where this currently applies:

- **Multi-party confidential proof verification**, where mutually distrusting parties need to agree on a shared claim or commitment without deferring to any single vendor as the source of truth
- **Item-level anti-counterfeiting and secondary-market provenance**, where an ownership/transfer history needs to remain independently checkable regardless of whether any one platform vendor stays in business
- **Cross-consortium or dataspace bridging**, where a claim genuinely spans two separately governed ecosystems with no shared attestor they agree on; currently a forward-looking scenario rather than a live driver, since most production DPP activity today is single-jurisdiction EU
- **An alternative trust root for suppliers outside the EU/eIDAS-equivalence perimeter** who cannot obtain a qualified electronic signature; this argues more broadly for self-certifying identity approaches (e.g. KERI) than for a ledger specifically, and Cardano is one possible implementation among several, not the obvious default.

The claim here is intentionally narrow: compliance alone does not require a shared ledger. A compliance-only buyer might still choose one for other reasons, such as an existing vendor relationship or onboarding preference, but that's a commercial choice, not a technical requirement. The concrete case for Cardano lies in the use cases above, not in compliance by itself.

**Cardano Advantages:**

Where the use cases above call for a shared ledger at all, several of Cardano's properties are a direct fit for those specific jobs:

- Public and permissionless, so provenance and anti-counterfeiting records stay independently checkable even if a specific platform vendor stopped operating, unlike a permissioned consortium ledger whose continuity depends on its members' ongoing funding
- The UTxO model maps naturally onto item-level ownership and transfer chains (anti-counterfeiting, secondary-market provenance): each transfer is an explicit, individually auditable state transition rather than a mutation of shared contract state
- CIP-25 and CIP-68 give a low-complexity anchoring path (no smart contract required for CIP-25) and a structured update path (CIP-68), lowering the cost of entry for both simple item registration and more complex, updateable proof records
- Formal verification tooling (Aiken) directly derisks the correctness of proof and commitment-checking logic in multi-party confidential verification, where several mutually distrusting parties are relying on the same code being right
- Predictable, low transaction costs support high-frequency use (repeated lifecycle events, resale transfers) without the cost volatility that complicates budgeting for an ongoing verification layer

Separately, and only relevant once a ledger is already the right tool: Cardano's energy footprint is a genuine relative advantage over proof-of-work alternatives, which matters given ESPR's own sustainability framing.

**Risk of Inaction:**

- Fragmented implementations harm ecosystem cohesion
- Businesses may choose competing platforms with clearer standards
- Missed opportunity to establish Cardano as supply chain infrastructure

### Stakeholders

#### Manufacturers (SMEs and Enterprises)

- Need cost-effective ESPR compliance
- Face uncertainty about implementation approaches
- Risk market access restrictions if non-compliant

#### Supply Chain Partners

- Need ability to contribute lifecycle events (logistics, installers, recyclers)
- Lack standards for multi-party coordination
- Cannot provide verifiable documentation for circular economy initiatives

#### Retailers and Brands

- Need to display verified product information to consumers
- Face integration challenges with multiple supplier formats
- Competitive pressure for product transparency

#### Consumers and Regulators

- Need independent verification of product claims
- Lack trusted verification mechanisms
- Cannot effectively enforce compliance or make informed decisions

#### Cardano Developers and Integrators

- Need clear specifications for building DPP solutions
- Currently reinventing standards for each project
- Face incompatibility risks across implementations

## Use Cases

### Static Product Registration

SME textile manufacturers need to register 1,200 products with materials, origin, and care instructions. Updates are rare (2-3 times per year when suppliers change). Requires simple process for non-technical staff, consumer-scannable QR codes, and minimal costs per product per year. Success means regulatory compliance achieved within 3 months and consumers can verify products instantly.

### Multi-Party Lifecycle Tracking

Battery manufacturers track 500,000 batteries from production through recycling, coordinating data from manufacturers, vehicle OEMs, service centers, and recyclers. Needs append-only audit trail with cryptographic proof of each event, support for multiple authorized parties, and 10+ year retention. Success means complete history queryable in seconds and regulatory audits passed with blockchain evidence.

### High-Volume Registration

Retail chain sells 5 million products from 10,000+ suppliers, with consumers scanning 100,000+ QR codes daily. Needs cost-effective registration at scale, sub-second verification response times, and ability to handle millions of daily scans. Success means all products registered affordably with consistent consumer experience.

### Privacy-Preserving Compliance

Chemical manufacturers must prove regulatory compliance without revealing confidential formulas or supplier costs. Needs on-chain cryptographic proof with full data kept private, selective disclosure to authorized regulators only, and integration with existing ERP systems. Success means zero confidential data exposed while regulators can verify specific compliance claims.

### Consumer Verification

Consumers scan product QR codes to verify sustainability claims using standard smartphones without specialized apps or cryptocurrency knowledge. Needs instant verification (under 2 seconds), clear visual indicators of verification status, and privacy protection. Success means high scan success rate and consumer comprehension without technical complexity.

## Goals

### Enable Regulatory Compliance

- Standards cover mandatory ESPR data fields for regulated sectors
- Verification mechanisms satisfy regulatory auditors
- Support for multiple jurisdictions (EU primary, with extensibility for UK, US, Asia)
- Extension framework supports future regulation changes

### Ensure Ecosystem Interoperability

- Implementations can verify each other's DPPs without custom integration
- Common verification processes across products and industries
- Consistent consumer experience regardless of manufacturer
- Integration with existing GS1 standards (GTINs, Digital Link, EPCIS)

### Support Multiple Implementation Patterns

- Static passports for stable products with rare updates
- Updateable passports for evolving data
- Event logs for multi-party lifecycle tracking
- Privacy-preserving proofs for confidential data
- High-throughput solutions for millions of products

### Maintain Privacy

- Confidential business data stays off-chain with on-chain commitments
- Selective disclosure to authorized parties only
- Consumer privacy protection

### Enable Practical Adoption

- Cost-effective for SMEs (thousands of euros annually, not tens of thousands)
- Scalable for enterprises (millions of products)
- Simple enough for non-technical staff
- Integration with existing business systems

## Open Questions

### Technical Standardization

**Data Schema Design:**

- What level of schema flexibility is needed to accommodate industry-specific requirements while maintaining interoperability?
- Should standards prescribe specific metadata formats or allow multiple serializations (JSON, CBOR, etc.)?

**Supply Chain Event Data Exchange:**

- **Question:** Given that stakeholders use different ERP systems (SAP, Oracle, custom solutions, etc.), what standard should be used for exchanging lifecycle event data across the supply chain?
- **Recommendation:** For multi-party lifecycle tracking scenarios (battery tracking, product repairs, refurbishment chains etc.), stakeholders SHOULD use EPCIS 2.0 (ISO/IEC 19987) for lifecycle event data to ensure interoperability across different ERP systems. EPCIS provides standardized capture of "what, when, where, why, and how" for supply chain events including manufacturing, shipping, installation, repair, and recycling. For static product registration scenarios (simple SME product registration with rare updates), simplified formats MAY be used. This tiered approach balances robust supply chain integration for complex scenarios with accessibility for smaller businesses with simpler needs.

**Physical-Digital Linking:**

- Should product identifiers (GTINs) be plaintext or hashed on-chain?
- Map GS1 Digital Links to Decentralized Identifiers for holding verifiable credentials
- EN 18219 (unique identifiers) and EN 18220 (data carriers) are now published, and independent implementations are converging on GS1 Digital Link identifiers resolving to a W3C Verifiable Credential over plain HTTPS, rather than a DID-first resolution path. This is worth validating Cardano identifier/resolver design against directly

**Scalability and Transaction Cost Management:**

- How to balance transaction costs with scalability requirements across different use cases?
- Item-level tracking (individual instances) vs. product-level registration (SKU templates): Do different granularity levels require different technical approaches?
- For high-frequency, item-level scenarios (e.g., millions of individual items with lifecycle events), what strategies ensure cost-effectiveness?
  - Batching mechanisms for bulk registration
  - Layer 2 solutions for high-throughput scenarios
  - Hybrid architectures (critical data on Layer 1, high-volume operational data off-chain or Layer 2)
- How to provide clear guidance on cost/performance trade-offs for different implementation patterns?

**Update Mechanisms:**

- For static passports: supersession (new NFT) vs. in-place updates (CIP-68)?
- How to maintain verifiable history across updates?
- CIRPASS-2's reference architecture recommends treating passports as immutable records, with updates creating new timestamped entries rather than overwriting the original. This aligns naturally with a supersession/new-NFT approach and is worth validating explicitly against CIP-68 in-place update patterns

### ESPR Implementation Uncertainty

**Timeline Risk:**

- System-level technical specifications (the EN 1821x series covering identifiers, carriers, data exchange, storage, APIs, and interoperability) are now published, with six of eight cited as harmonised standards, so this risk has substantially reduced at the system level
- Sector-specific delegated acts (defining what data each product category must disclose) remain in progress and are now the primary remaining source of specification risk
- Cardano-specific guidance can now commit to the published system standards, while keeping sectoral data schemas flexible until the relevant delegated acts land

**Scope Evolution:**

- ESPR will expand to additional sectors beyond batteries and textiles
- How to design extensible standards that accommodate unknown future requirements?

**European Technical Standards Alignment:**

*Where the standards landscape stands now:*
- CEN-CENELEC JTC 24 published the first six of eight DPP system standards on 27 May 2026, covering unique identifiers (EN 18219), data carriers (EN 18220), data exchange protocols (EN 18216), data storage/persistence (EN 18221), APIs (EN 18222), and interoperability (EN 18223); these were cited as harmonised standards in the Official Journal in July 2026 (Commission Implementing Decision (EU) 2026/1736), giving conforming DPPs a presumption of conformity under ESPR Articles 10 and 11. The remaining two (access rights/security, and data authentication) are in final approval and expected shortly.
- The EU DPP Registry went live in July 2026 alongside a testing environment, giving implementers a real integration target rather than a specification on paper.
- Sector-specific data requirements (what fields textiles vs. electronics must actually disclose) are still being finalised through delegated acts and remain the more volatile layer: the system-level "plumbing" is now comparatively stable, the "what data" layer is not.
- Even once defined, data requirements are expected to evolve as regulations are refined and new sustainability metrics emerge
- The CIRPASS-2 project (the EU-funded successor to the original CIRPASS preparatory action) published an updated reference architecture (D4.1 v1.1, June 2026) with 25 implementation recommendations. Notably, it dropped the parallel DID-only identity track present in the original CIRPASS proposal in favour of a single HTTP/Verifiable-Credential-based model. DIDs are now positioned as an optional advanced overlay rather than a requirement.
- Across independent implementations (e.g. the UN Transparency Protocol, and several EU-aligned DPP platforms), a de facto technology stack is emerging: W3C Verifiable Credentials 2.0 for the passport itself, SD-JWT for selective disclosure of individual fields, and GS1 Digital Link for physical-to-digital identifier resolution, served over plain HTTPS rather than DID-first resolution. Separately, broader EU digital-sovereignty policy (the proposed Cloud and AI Development Act, national sovereign-cloud frameworks) is pushing infrastructure hosting generally toward EU-domiciled providers. This compounds ESPR's own requirement that DPP hosting remain durable and available via an EU-accountable economic operator or DPP service provider.
- The EU also runs a separate blockchain initiative, EBSI (European Blockchain Services Infrastructure): a permissioned consortium ledger operated by EU-endorsed institutional node operators, governed since 2024 by EUROPEUM-EDIC (a subset of member states, not all 27), used mainly for institutional verifiable-credential issuance (diplomas, business credentials) rather than product data. It has no regulatory link to ESPR or the DPP Registry, Commission funding and support for it ended in February 2026 with member states now running it, and it is not yet in general production. CIRPASS-2's reference architecture did not adopt it, and early DPP implementers have largely gone a different direction.

*Design Challenges:*
- How should a Cardano-anchored DPP interoperate with this VC/SD-JWT/GS1-Digital-Link stack rather than just compete with it (e.g., using Cardano as a verification/anchoring layer under credentials that remain independently resolvable and verifiable off-chain)?
- How to support industry-specific data schemas while maintaining cross-industry interoperability, given sectoral requirements are still evolving under delegated acts?
- What versioning and extensibility mechanisms are needed to accommodate future data requirement changes without breaking existing implementations?
- Where does an on-chain anchor sit relative to EU data-sovereignty and hosting expectations, given the underlying DPP content is expected to be held by an EU-domiciled operator or service provider regardless of which anchoring technology is used?
- Given that neither the EU's own reference architecture (CIRPASS-2) nor its own blockchain project (EBSI) has converged on a shared-ledger model for DPP, what concrete benefit does anchoring on Cardano provide over the conventional VC/SD-JWT/GS1-Digital-Link stack alone? This CPS should treat that as genuinely open rather than assumed; informal outreach with early implementers so far mostly confirms it isn't a widely felt need, which is itself worth stating plainly rather than glossing over.

*Strategic Options:*
- Align directly to the now-published EN 1821x system standards, treating sectoral (delegated-act) data requirements as the extension point that evolves over time
- Position Cardano as a verification/anchoring layer beneath a standards-compliant VC/SD-JWT passport, rather than simply proposing it as an alternative credential model
- Implement core infrastructure now, add industry-specific schemas iteratively (risk: fragmentation)

### Adoption Indicators

- Multiple independent implementations demonstrating interoperability
- Production pilots with real businesses and products
- Businesses using standards in production (target: multiple companies within 24 months)
- Number of DPP and DPP-adjacent solutions anchoring data on Cardano, whether Cardano-native or via a conventional-stack platform anchoring in
- Production deployments demonstrate viability ahead of each sector's own mandated deadline (batteries: 18 February 2027; textiles: realistically 2028-2029 once the delegated act's transition period runs; other sectors phasing in through 2030)
- Significant product volume registered (target: 50,000+ products by Q4 2027), most plausibly battery-driven at that point, since batteries is the only sector under a confirmed compliance date by then

### Technical Validation

- Implementations can verify each other's DPPs
- Performance suitable for consumer-facing applications (sub-second verification)
- Cost-effective for small businesses
- High availability for verification services

### Ecosystem Development

- Developer tools and libraries supporting standards
- Active community participation in standards evolution
- Comprehensive documentation and implementation guides
- Industry recognition and regulatory acceptance
-  A dedicated Cardano DPP working group already meets monthly and maintains a draft solution-pattern blueprint (`cardano-foundation/cardano-dpp-standards`), to try and coordinate,support, and avoid duplicating effort

## Copyright

This CPS is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
