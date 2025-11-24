---
CPS: TBD 
Title: Digital Product Passports on Cardano
Status: Open
Category: Tools
Authors: David Clark <david.clark@cardanofoundation.org>

Implementors: []
Proposed Solutions: []
Discussions: []
Created: 2025-11-24
License: CC-BY-4.0
---

## Abstract

The European Union's Ecodesign for Sustainable Products Regulation (ESPR) mandates Digital Product Passports (DPPs) for numerous product categories starting in 2026. These passports must provide tamperproof, verifiable information about products' materials, origin, lifecycle, and compliance throughout the supply chain.

Currently, the Cardano ecosystem lacks standardized approaches for anchoring DPP data on-chain, creating product identity assets, and enabling multi-party verification. This fragmentation risks incompatible implementations, poor interoperability, and a missed opportunity for Cardano to become a reference platform for supply chain transparency and regulatory compliance.

This CPS articulates the problem space and establishes goals for comprehensive DPP standards that enable regulatory compliance, ecosystem interoperability, and practical implementation.

## Problem

### Background

Digital Product Passports are becoming mandatory under EU regulation to support:

- **Circular economy goals** - Tracking materials for reuse and recycling
- **Consumer transparency** - Providing verifiable product information
- **Regulatory compliance** - Proving adherence to safety, sustainability, and origin requirements
- **Supply chain accountability** - Creating tamperproof audit trails across multiple parties

The ESPR affects industries including textiles, electronics, batteries, construction materials, furniture, and more, impacting millions of businesses globally. First implementations begin in 2026 for batteries, followed by textiles in 2027, with other sectors phasing in through 2030.

DPP implementations must integrate with existing global product identification systems, particularly GS1 standards (GTINs for product identification, Digital Link for web-based resolution, and EPCIS for event tracking). This integration is essential for interoperability with existing supply chain infrastructure.

### Current State

While Cardano provides foundational capabilities through CIP-25 and CIP-68 metadata standards, the ecosystem lacks:

- Standardized data schemas for product lifecycle information
- Guidance on linking physical products (GTINs, QR codes) to on-chain identities
- Reference architectures for different implementation patterns (static passports, event logs, high-throughput registration, privacy-preserving proofs)
- Established approaches for multi-party coordination across supply chains
- Validation frameworks for regulatory compliance claims

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
- Opportunity to lead in open standards development for blockchain-based DPP implementations

**Enterprise Reality:** While ESPR regulations are technology-neutral, market adoption data shows blockchain implementations growing rapidly in multi-party supply chain scenarios where trust, transparency, and long-term data integrity are critical requirements. Industries with long product lifecycles (batteries, automotive, textiles) are increasingly choosing blockchain solutions for immutable audit trails and cross-organizational coordination. Many enterprises adopt hybrid approaches, using public blockchain for critical provenance data and ownership transfer while keeping high-volume operational data in traditional databases.

**Cardano Advantages:**

- Predictable transaction costs suitable for industrial use
- Deterministic execution (UTxO model) for regulated environments
- Energy efficiency aligning with sustainability-focused regulations
- Established governance framework for standards evolution

**Risk of Inaction:**

- Fragmented implementations harm ecosystem cohesion
- Businesses may choose competing platforms with clearer standards
- Missed opportunity to establish Cardano as supply chain infrastructure

## Stakeholders

### Manufacturers (SMEs and Enterprises)

- Need cost-effective ESPR compliance
- Face uncertainty about implementation approaches
- Risk market access restrictions if non-compliant

### Supply Chain Partners

- Need ability to contribute lifecycle events (logistics, installers, recyclers)
- Lack standards for multi-party coordination
- Cannot provide verifiable documentation for circular economy initiatives

### Retailers and Brands

- Need to display verified product information to consumers
- Face integration challenges with multiple supplier formats
- Competitive pressure for product transparency

### Consumers and Regulators

- Need independent verification of product claims
- Lack trusted verification mechanisms
- Cannot effectively enforce compliance or make informed decisions

### Cardano Developers and Integrators

- Need clear specifications for building DPP solutions
- Currently reinventing standards for each project
- Face incompatibility risks across implementations

## Sample Use Cases

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

**Update Mechanisms:**

- For static passports: supersession (new NFT) vs. in-place updates (CIP-68)?
- How to maintain verifiable history across updates?

### ESPR Implementation Uncertainty

**Timeline Risk:**

- Final ESPR technical specifications not yet published by European Commission
- Risk of designing standards that need significant rework post-regulation
- Should standards anticipate requirements or wait for final specifications?

**Scope Evolution:**

- ESPR will expand to additional sectors beyond batteries and textiles
- How to design extensible standards that accommodate unknown future requirements?

## Adoption Indicators

### Adoption Indicators

- Multiple independent implementations demonstrating interoperability
- Production pilots with real businesses and products
- Businesses using standards in production (target: multiple companies within 24 months)
- Production deployments demonstrate viability ahead of February 2027 ESPR compliance deadline
- Significant product volume registered (target: 50,000+ products by Q4 2027 as textile sector compliance takes effect)

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

## Copyright

This CPS is licensed under CC-BY-4.0.
