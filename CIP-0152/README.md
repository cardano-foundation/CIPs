---
CIP: ???
Title: On-Chain DRep Credential & Extended Governance NFTs
Status: Draft
Category: Governance
Authors:
  - "Derrick Oatway <alpine@malamaproject.org>"
Implementors:
  - DRep Collective
Discussions:
  - "https://github.com/cardano-foundation/CIPs/pull/1007"
Created: "2025-03-01"
License: CC-BY-4.0
---

## Table of Contents

- [Table of Contents](#table-of-contents)
- [1. Abstract](#1-abstract)
- [2. Motivation](#2-motivation)
- [3. Specification](#3-specification)
  - [3.1 Relationship to Existing Standards (CIPs)](#31-relationship-to-existing-standards-cips)
  - [3.2 Identifiers (DRep \& Proposal)](#32-identifiers-drep--proposal)
  - [3.3 Off-Chain Metadata (Anchors)](#33-off-chain-metadata-anchors)
  - [3.4 NFT Metadata Format (CIP-68)](#34-nft-metadata-format-cip-68)
  - [3.5 NFT Naming (CIP-67 Labels)](#35-nft-naming-cip-67-labels)
  - [3.6 NFT Types Explained](#36-nft-types-explained)
    - [3.6.1 DRep Credential](#361-drep-credential)
    - [3.6.2 Ballot Note](#362-ballot-note)
    - [3.6.3 Endorsement](#363-endorsement)
  - [3.7 Conceptual Data Schema (Simplified)](#37-conceptual-data-schema-simplified)
  - [3.8 Practical Implementation Notes](#38-practical-implementation-notes)
  - [3.9 Summary of Key Requirements (Quick Reference)](#39-summary-of-key-requirements-quick-reference)
- [This simplified specification ensures **CIP-152** NFTs are straightforward to implement, widely compatible, and effectively improve transparency and community participation in Cardano governance.](#this-simplified-specification-ensures-cip-152-nfts-are-straightforward-to-implement-widely-compatible-and-effectively-improve-transparency-and-community-participation-in-cardano-governance)
  - [3.10 Extending CIP-152 (Proposing New NFT Types)](#310-extending-cip-152-proposing-new-nft-types)
- [4. Rationale: How Does This CIP Achieve Its Goals?](#4-rationale-how-does-this-cip-achieve-its-goals)
- [5. Path to Active](#5-path-to-active)
  - [Acceptance Criteria](#acceptance-criteria)
  - [Implementation Plan (Step-by-Step Roadmap)](#implementation-plan-step-by-step-roadmap)
- [6. Versioning](#6-versioning)
- [7. Copyright](#7-copyright)

---

## Abstract

> "**Poets are the unacknowledged legislators of the world.**"  
> — Percy Bysshe Shelley, _A Defence of Poetry_ (1821)

This CIP introduces a structured on-chain metadata standard designed to enhance the transparency, accountability, and effectiveness of Cardano’s governance system as outlined by **CIP-1694**. Utilizing the existing **CIP-68** datum-based NFT standard, this proposal defines three distinct token types:

1. **DRep Credential** – An on-chain credential NFT referencing extended metadata such as qualifications, experience, or motivations (anchored via **CIP-119**).
2. **Ballot Note** – A transparent, verifiable record of a Delegated Representative’s (DRep’s) voting choice and rationale.
3. **Endorsement** – An independently minted NFT serving as decentralized social proof from community stakeholders supporting a particular DRep.

By storing large metadata off-chain and anchoring it through CIP-119, **CIP-???** reduces ledger bloat and allows for scalable governance metadata management. These NFTs collectively create a verifiable information ecosystem, empowering delegators with comprehensive insights and enabling analytics tools to systematically map Cardano’s governance landscape. Crucially, **CIP-???** complements but does not alter CIP-1694’s core governance mechanisms, thereby offering enhanced transparency without imposing additional complexity on existing governance operations.

## Motivation: why is this CIP necessary?

> "**Every man is guilty of all the good he did not do.**"  
> — François-Marie Arouet (Voltaire), 18th century

Cardano’s transition into the Voltaire era, through the introduction of **CIP-1694**, provides the infrastructure for decentralized governance via on-chain voting and delegation. However, delegators face significant challenges in identifying trustworthy and competent Delegated Representatives (DReps) due to fragmented, off-chain sources and limited verifiable information. This opacity risks suboptimal delegation choices, diminished trust, and reduced governance participation.

This CIP directly addresses these limitations by creating a standardized metadata framework for verifiable, structured governance data. By leveraging on-chain NFTs linked to off-chain metadata anchors (**CIP-119** and related proposals), this CIP enables:

- **DReps** to transparently communicate their credentials, track records, and motivations in a standardized, verifiable format.
- **Delegators** to easily evaluate DReps’ historical performance, voting rationales, and endorsements, facilitating informed delegation choices.
- **Community stakeholders** (including SPOs, DAOs, and active participants) to independently endorse DReps, strengthening trust through decentralized social proof.

In establishing this robust metadata standard, this CIP provides the necessary foundation for advanced governance analytics, clearer ecosystem mapping, and deeper community engagement, thereby promoting informed, active, and effective governance participation across the Cardano ecosystem.

## Specification

> "**We see categories as the best available formal conceptual tool for bridging those multiple worlds that exist in the large scale engineering of practical, robust, evolving systems.**"  
> — Joseph A. Goguen (1997)

This CIP introduces three specialized NFT types to enhance transparency and accountability in Cardano's governance. These NFTs use existing Cardano standards to ensure compatibility and simplicity:

1. **DRep Credential** – An NFT representing a Delegated Representative’s (DRep’s) profile.
2. **Ballot Note** – An NFT recording a DRep’s vote and optional reasoning.
3. **Endorsement** – An NFT created by third parties to publicly support a DRep.

These NFTs rely on existing Cardano Improvement Proposals (CIPs) to keep things simple and consistent:

- **CIP-1694:** Defines how governance IDs (DReps and proposals) work.
- **CIP-68:** Provides a standardized format (datum-based NFTs) for on-chain metadata.
- **CIP-119 & CIP-108:** Allow large metadata (documents, profiles, rationales) to be stored off-chain securely.
- **CIP-67:** Ensures NFTs are clearly labeled and discoverable.

### Relationship to Existing Standards (CIPs)

- **CIP-1694 (Governance IDs)**  
  Defines unique IDs for DReps and proposals. This CIP uses these exactly as defined.

- **CIP-100 Family (Off-Chain Metadata Anchors)**  
  Stores large documents off-chain, using secure links (anchors) defined by CIP-100 and its extensions, CIP-119 (for DReps) and CIP-108 (for proposals).

- **CIP-68 (Datum-based NFTs)**  
  Ensures all NFTs defined by this CIP share a common metadata structure, simplifying their usage across different tools and wallets.

- **CIP-67 (Asset Labeling)**  
  Clearly identifies this CIP NFTs, making them easy for wallets and explorers to recognize and categorize.

### Identifiers (DRep & Proposal)

These identifiers link NFTs directly to Cardano’s governance system (CIP-1694):

- **DRep ID**:  
  A unique identifier derived from a DRep’s on-chain identity, exactly matching CIP-1694’s definition.

- **Proposal ID**:  
  A unique identifier combining a transaction hash and index, directly matching CIP-1694.

Example:

```yaml
proposalId: "txHash: 1234abcd...ff, index: 1"
```

### Off-Chain Metadata (Anchors)

To avoid overwhelming the blockchain, large data like profiles, rationales, and detailed documents are stored off-chain, linked securely through:

- **DRep data (profiles, qualifications):** anchored using CIP-119.
- **Proposal details (rationale, context):** anchored using CIP-108.

These anchors include a URL and a secure hash (`blake2b-256`) for verification.

### NFT Metadata Format (CIP-68)

All NFTs in this CIP follow a simple, standardized format provided by CIP-68:

```
#6.121([ metadataMap, version:int, extra:{} ])
```

- **metadataMap**: clearly structured information (e.g., IDs, URLs).
- **version**: indicates the NFT’s schema version (always ≥ 1).
- **extra**: reserved for future or special use (usually empty).

### NFT Naming (CIP-67 Labels)

NFT names follow an easy-to-understand structure:

```
(???)drepCredential-<uniqueId>
(???)ballotNote-<proposalId>
(???)endorsement-<endorserId>-<drepId>
```

This makes NFTs easily identifiable across wallets, explorers, and analytics tools.

### NFT Types Explained

#### DRep Credential

- **Minted by:** The Delegated Representative (DRep)
- **Purpose:** Shares the DRep’s profile, credentials, and motivation.
- **Required Fields:**
  - `dRepId`: Unique ID from CIP-1694.
- **Optional Fields:**
  - Links (`cip119AnchorUrl`, `cip119AnchorHash`) to off-chain detailed data.
  - Additional personal or qualification details.

#### Ballot Note

- **Minted by:** The DRep who voted.
- **Purpose:** Publicly records the vote and optionally explains the reason behind it.
- **Required Fields:**
  - `type`: Always `"ballotNote"`
  - `dRepId`: Voter’s ID.
  - `proposalId`: The proposal being voted on.
  - `voteChoice`: "Yes", "No", or "Abstain".
- **Optional Fields:**
  - `rationale`: Short text or link explaining the vote.
  - `timestamp`: When the vote was cast.

#### Endorsement

- **Minted by:** A third-party supporter (SPOs, DAOs, community members).
- **Purpose:** Provides public, verifiable support for a DRep.
- **Required Fields:**
  - `type`: Always `"endorsement"`
  - `endorses`: The DRep’s ID being supported.
  - `endorser`: The supporter’s stake address.
- **Optional Fields:**
  - `identityProof`: Proof of identity or credibility of endorser.
  - `comment`: Brief supportive statement or link.

### Conceptual Data Schema (Simplified)

This illustrates the minimal required metadata clearly:

```cddl
cip???-datum = #6.121([
  metadata-map,
  version,
  extra
])

; General structure for metadata-map:
metadata-map = {
  * key => value
}

; DRep Credential example:
drep-credential = {
  "dRepId": "unique DRep ID",
  ? "cip119AnchorUrl": "URL to off-chain profile",
  ? "cip119AnchorHash": "secure hash of profile"
}

; Ballot Note example:
ballot-note = {
  "type": "ballotNote",
  "dRepId": "unique DRep ID",
  "proposalId": "proposal identifier",
  "voteChoice": "Yes",
  ? "rationale": "reason or URL",
  ? "timestamp": "ISO date/time"
}

; Endorsement example:
endorsement = {
  "type": "endorsement",
  "endorses": "DRep ID",
  "endorser": {
    "stakeKey": "endorser stake key",
    ? "identityProof": "optional proof"
  },
  ? "comment": "optional supportive statement"
}
```

### Practical Implementation Notes

- **Data Storage:** Keep large files and data off-chain (IPFS, decentralized storage). Store only short references (URLs and hashes) on-chain.
- **Minting Rules:**
  - DReps mint their Credential and Ballot Notes.
  - Third parties independently mint Endorsements.
- **Verification:** Tools must validate that stored IDs exactly match CIP-1694’s definitions.
- **Asset Naming:** Clearly label NFTs using CIP-67 format `(???)` for easy recognition.

### Summary of Key Requirements (Quick Reference)

- **Use existing CIP standards** (1694, 68, 67, 119, 108).
- Clearly link NFTs to CIP-1694 IDs for accuracy.
- Store large content securely **off-chain**.
- Follow a consistent NFT metadata format (CIP-68).
- Clearly label NFT assets for easy discovery (CIP-67).

**This simplified specification ensures NFTs defined by this standard are straightforward to implement, widely compatible, and effectively improve transparency and community participation in Cardano governance.**

### Extending this CIP (Proposing New NFT Types)

This standard is designed for extensibility. If additional NFT types become necessary, they can be proposed through the following process:

1. Start a public discussion in the Cardano CIP repository clearly outlining:

   - Purpose and necessity of the new NFT type.
   - Detailed metadata structure proposal.
   - Minting responsibilities and policy guidelines.

2. Obtain community feedback and consensus.

3. Upon approval, the new NFT type can be officially documented as part of an updated version of this standard.

This ensures this standard evolves transparently, driven by community needs.

## Rationale: How Does This CIP Achieve Its Goals?

> "**If I do not write to empty my mind, I go mad.**"  
> — Attributed to Lord Byron (circa 1818–1822)

This standard enhances Cardano's governance system by providing richer on-chain metadata while remaining fully compatible with existing proposals like **CIP-1694** and **CIP-119**. Rather than introducing new, complex structures or drastically altering established processes, this CIP builds directly upon proven standards. This ensures existing governance participants remain fully valid and unaffected, while those adopting this standard gain enhanced transparency, richer context, and improved accountability.

Using the **CIP-68 datum-based NFT standard** offers two major advantages:

- **Updatability**: Delegated Representatives (DReps) can refine or extend their on-chain credentials over time, adapting to changing circumstances or adding further endorsements and credentials.
- **Verifiability**: CIP-68 metadata is accessible to Cardano’s smart-contract layer (Plutus), enabling advanced decentralized applications (dApps) and tools to validate DRep credentials, voting rationales, and endorsements directly on-chain.

By leveraging secure **off-chain metadata anchors** (via CIP-119 for DRep profiles and CIP-108 for proposals), this CIP ensures Cardano’s ledger remains lean and efficient. This avoids the costly and inefficient practice of storing large amounts of data on-chain, thus significantly reducing transaction costs and complexity.

Addressing community concerns regarding potential spam or misleading endorsements, this standard clearly separates third-party endorsements from self-issued credentials. Endorsements must come independently from external participants, enabling the community and analytical tools to gauge their credibility and detect patterns indicative of manipulation or spam.

Crucially, this standard is designed as an **optional enhancement**, complementing but not replacing CIP-1694’s core governance logic. This ensures flexibility for participants—those seeking simple participation need not adopt this standard, while delegators and DReps seeking deeper insights, accountability, and community engagement gain powerful new tools for informed governance decisions.

## Path to Active

### Acceptance Criteria

> "**Do not seek to follow in the footsteps of the wise; seek what they sought.**"  
> — Matsuo Bashō (17th century)

To achieve **Active** status, this CIP must fulfill the following clear criteria:

1. **Reference Implementations**  
    - [ ] At least **two independent teams** publish open-source reference implementations demonstrating:
        - [ ] Minting of all three NFT types (DRep Credential, Ballot Note, Endorsement).
        - [ ] Correct usage of CIP-68 datum structure.
        - [ ] Proper referencing of CIP-1694 identifiers (`dRepId`, `proposalId`).
        - [ ] Parsing and verification of metadata fields.

2. **Wallet & Explorer Support**  
    - [ ] At least **one wallet** and **one block explorer** publicly demonstrate:
        - [ ] Recognition and display of this CIP's NFT labels (CIP-67).
        - [ ] User-friendly presentation of NFT metadata fields.
        - [ ] Proper handling and verification of off-chain metadata anchors (CIP-119/CIP-108).

3. **Governance Tool Integration**  
    - [ ] At least **one governance dashboard or analytics tool** publicly incorporates these NFTs, providing:
        - [ ] Visualization of DRep Credentials alongside off-chain profiles.
        - [ ] Display of Ballot Notes with voting rationale.
        - [ ] Tracking and visual representation of Endorsements.
        - [ ] Verification of identifiers consistent with CIP-1694.

4. **Community Approval**
    - [ ] Conduct a public review lasting a minimum of **four weeks**, collecting input from DReps, SPOs, wallet developers, governance experts, and CIP editors.
        - [ ] Resolve or address all major concerns, ensuring compatibility with CIP-1694, CIP-68, CIP-119, and CIP-108.
        - [ ] Obtain broad community consensus confirming tangible benefits without introducing contradictory governance assumptions.

Once these criteria are satisfied, authors will formally request the CIP editors to transition this CIP from **Proposed** to **Active** according to the guidelines outlined in CIP-0001.

### Implementation Plan (Step-by-Step Roadmap)

1. **Initial Reference Implementation & Documentation**

   - Publish minimal open-source scripts or libraries for NFT minting and metadata handling.
   - Provide clear documentation and practical examples of asset naming (CIP-67), datum structure (CIP-68), and off-chain metadata anchors (CIP-119, CIP-108).

2. **Testnet Demonstrations**

   - Deploy example NFTs on a Cardano testnet (Preview or Preprod).
   - Verify correctness of NFT minting, datum fields, and metadata linking to off-chain resources.

3. **Wallet & Explorer Integration**

   - Collaborate directly with wallet and block explorer developers to demonstrate practical NFT support.
   - Ensure easy discoverability, clear asset naming, and intuitive metadata display in user interfaces.

4. **Governance Analytics & Dashboard Integration**

   - Integrate these NFTs into at least one governance-focused analytics platform.
   - Showcase a practical, live example of governance insights derived from the metadata defined in this standard.

5. **Community Review & Finalization**
   - Publish results, openly inviting community review and expert feedback.
   - Conduct a structured community review for a minimum of four weeks.
   - Resolve any identified issues and ensure consensus around this standard’s compatibility and utility.
   - After successful resolution and broad approval, formally request activation.

## Versioning

The NFTs defined by this standard include a `version` field in their datum (starting at `1`). Any future updates or improvements to this CIP that modify the datum structure MUST increment this `version`. Applications and tools reading these NFTs:

- **MUST** gracefully handle unknown or additional fields to remain forward-compatible.
- **SHOULD** support older datum versions to maintain backward compatibility.

Significant breaking changes require proposing a new CIP or explicitly updating this CIP with clear documentation, preserving compatibility with NFTs minted under earlier versions.

Special thanks to the numerous DReps, SPOs, wallet developers, and CIP editors whose contributions and feedback greatly shaped this proposal.

## Copyright

This work is licensed under the **Creative Commons Attribution 4.0 International License (CC-BY-4.0)**. You are free to share and adapt this CIP for any purpose, provided you give appropriate credit and indicate clearly if any modifications have been made. A full copy of this license is available at:  
[https://creativecommons.org/licenses/by/4.0/](https://creativecommons.org/licenses/by/4.0/)

