---
CIP: ???
Title: On-Chain DRep Credential & Extended Governance NFTs
Status: Draft
Category: Tokens
Authors:
  - "Derrick Oatway <alpine@malamaproject.org>"
Implementors:
  - DRep Collective
Discussions:
  - "https://github.com/cardano-foundation/CIPs/pull/1007"
Created: "2025-03-01"
License: CC-BY-4.0
---

## Abstract

> "**Poets are the unacknowledged legislators of the world.**"  
> — Percy Bysshe Shelley, _A Defence of Poetry_ (1821)

This CIP introduces structured **on-chain** metadata standards to enhance transparency, accountability, and effectiveness in Cardano’s governance. Building on **CIP-1694**, it provides new mechanisms for Delegated Representatives (DReps) and delegators to record, discover, and analyze governance data in a standardized way. Leveraging the **CIP-68** datum-based NFT model, it defines three specialized token types:

1. **DRep Credential** – An on-chain credential NFT referencing both on- and off-chain metadata (per **CIP-119**), with optional fields (e.g., roles, sectors) for DReps to self-report.
2. **Ballot Note** – A verifiable record capturing a DRep’s vote and accompanying rationale.
3. **Endorsement** – An independently minted NFT serving as decentralized social proof from a DRep’s supporters.

Where large content is required—like detailed profiles, mission statements, or rationales—it can be stored off-chain and anchored via **CIP-119** or **CIP-108**, minimizing on-chain storage. These tokens do not replace the core mechanics of CIP-1694; rather, they offer an **optional**, more transparent framework for tracking DRep credentials, roles, votes, and social endorsements—ultimately enabling delegators and the community to make better-informed decisions.

## Motivation: why is this CIP necessary?

> "**Every man is guilty of all the good he did not do.**"  
> — François-Marie Arouet (Voltaire), 18th century

The **Voltaire** phase of Cardano governance, defined by **CIP-1694**, establishes on-chain voting and delegation. Despite this significant advancement, delegators still struggle to find trustworthy, verifiable data on potential DReps. Relevant information—such as track records, qualifications, or community endorsements—remains scattered off-chain, with no standardized anchor to link it back to the DRep’s on-chain identity.

This CIP addresses these gaps by proposing an **on-chain** credentialing framework that leverages **off-chain** metadata anchors (per **CIP-119** for extended DRep profiles and **CIP-108** where proposal data is relevant). As a result:

- **DReps** can mint concise on-chain credentials referencing richer off-chain information, making their profiles discoverable and verifiable within the ledger.
- **Delegators** gain clearer insights into DReps’ qualifications, roles, endorsements, and historical voting behavior directly at the wallet or analytics-tool level—enabling more informed delegation choices.
- **Community stakeholders** can independently endorse DReps on-chain, establishing verifiable social proof that strengthens the network’s trust fabric.

By integrating these elements, this CIP fosters a more transparent, data-driven governance environment—ultimately encouraging broader participation and deeper accountability across Cardano’s evolving governance ecosystem.

## Specification

> "**We see categories as the best available formal conceptual tool for bridging those multiple worlds that exist in the large scale engineering of practical, robust, evolving systems.**"  
> — Joseph A. Goguen (1997)

This CIP proposes three **governance-oriented NFTs**—the **DRep Credential**, **Ballot Note**, and **Endorsement**—each referencing **CIP-1694** governance IDs (DReps, proposals) and optionally linking to extended off-chain data (via **CIP-119** or **CIP-108**). On-chain fields are stored within a **CIP-68** datum to keep records succinct yet verifiable, while token names follow **CIP-67** labeling.

### 1. Relationship to Existing Standards

- **CIP-1694 (On-Chain Governance)**

  - Defines DRep IDs (blake2b-224 hash) and proposal IDs (transaction hash + index).

- **CIP-68 (Datum-Based NFTs)**

  - Enables storing metadata in a Plutus datum.
  - This proposal uses CIP-68 for on-chain governance data (versioning, optional updatability).

- **CIP-67 (Asset Name Labeling)**

  - Enforces a 4-byte label scheme so wallets/explorers can recognize governance tokens.

- **CIP-119 / CIP-108 (Off-Chain Anchors)**
  - CIP-119: Off-chain JSON for extended DRep profiles.
  - CIP-108: Off-chain metadata for proposals or related governance documents.

**Note:** The technical details of each CIP (hashing, labeling, datum layouts) are **not** restated here. Implementers must consult each CIP’s original documentation.

### 2. Identifiers (DRep & Proposal)

1. **DRep ID**

   - A **28-byte (56-hex)** blake2b-224 hash of the stake key or script credential per CIP-1694.

2. **Proposal ID**
   - A string usually of the form `"txHash + index"`, as outlined by CIP-1694.

All references to DReps or proposals in these NFTs **must** use these official IDs, ensuring consistency with CIP-1694 governance tooling.

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

