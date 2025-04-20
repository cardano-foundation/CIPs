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

This CIP introduces structured **on-chain** metadata standards to enhance transparency, accountability, and effectiveness in Cardano’s governance. Building on **CIP-1694**, it provides new mechanisms for Delegated Representatives (DReps) and delegators to record, discover, and analyze governance data in a standardized way. Leveraging the **CIP-68** datum-based NFT model, it defines three specialized token types:

1. **DRep Credential** – An on-chain credential NFT referencing both on- and off-chain metadata (per **CIP-119**), with optional fields (e.g., roles, sectors) for DReps to self-report.
2. **Ballot Note** – A verifiable record capturing a DRep’s vote and accompanying rationale.
3. **Endorsement** – An independently minted NFT serving as decentralized social proof from a DRep’s supporters.

Where large content is required—like detailed profiles, mission statements, or rationales—it can be stored off-chain and anchored via **CIP-119** or **CIP-108**, minimizing on-chain storage. These tokens do not replace the core mechanics of CIP-1694; rather, they offer an **optional**, more transparent framework for tracking DRep credentials, roles, votes, and social endorsements—ultimately enabling delegators and the community to make better-informed decisions.

## Motivation: why is this CIP necessary?

The **Voltaire** phase of Cardano governance, defined by **CIP-1694**, establishes on-chain voting and delegation. Despite this significant advancement, delegators still struggle to find trustworthy, verifiable data on potential DReps. Relevant information—such as track records, qualifications, or community endorsements—remains scattered off-chain, with no standardized anchor to link it back to the DRep’s on-chain identity.

This CIP addresses these gaps by proposing an **on-chain** credentialing framework that leverages **off-chain** metadata anchors (per **CIP-119** for extended DRep profiles and **CIP-108** where proposal data is relevant). As a result:

- **DReps** can mint concise on-chain credentials referencing richer off-chain information, making their profiles discoverable and verifiable within the ledger.
- **Delegators** gain clearer insights into DReps’ qualifications, roles, endorsements, and historical voting behavior directly at the wallet or analytics-tool level—enabling more informed delegation choices.
- **Community stakeholders** can independently endorse DReps on-chain, establishing verifiable social proof that strengthens the network’s trust fabric.

By integrating these elements, this CIP fosters a more transparent, data-driven governance environment—ultimately encouraging broader participation and deeper accountability across Cardano’s evolving governance ecosystem.

## Specification

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

### 3. On-Chain vs. Off-Chain Metadata

**On-Chain**

- The CIP-68 datum holds minimal but essential governance fields—IDs, short texts, timestamps.
- Self-reported data (e.g., a DRep’s focus areas or a quick rationale) is possible but should remain concise to avoid high on-chain storage costs.

**Off-Chain**

- Large or frequently updated content (e.g., multi-paragraph mission statements, proposal PDFs, rich media) is stored off-ledger.
- References take the form of a **URL + blake2b-256 hash** (per CIP-119 or CIP-108), allowing client apps to verify integrity while avoiding ledger bloat.

### 4. Governance NFT Types

All governance NFTs proposed here share a **new CIP-67 label** (placeholder `(1694)`). Example asset names:

- `"(1694)drepCredential-<dRepAlias>"`
- `"(1694)ballotNote-<proposalId>"`
- `"(1694)endorsement-<endorserKey>-<dRepId>"`

#### 4.1 DRep Credential

**Minted by:** The DRep or an authorized delegate.  
**Purpose:**

- Captures key DRep info on-chain (e.g., `dRepId`, name, roles).
- Optionally anchors extended data via CIP-119.
- Reflects the “DRep Credential Form” mockup fields.

**Core Field:**

- `dRepId` (CIP-1694 hash)

**Recommended Optional Fields (Self-Reported):**

- **Title/Role**: Short descriptor (e.g., “DeFi Developer”).
- **Name (or Alias)**, **Profile Image URL**, **Website**, **Mission/Goals**.
- **Primary Focus Areas** (e.g., DeFi, Governance, Education).
- **Roles** (SPO, Dev/Builder, Community Manager, etc.).
- **Sectors** (NFTs, Identity, Gaming, DAO Tools).
- **Social Links** (Twitter handle, Discord handle).
- **Off-Chain Anchor** (`cip119AnchorUrl`, `cip119AnchorHash`) for extended profiles.

**Minimal JSON Example:**

```jsonc
{
  "version": 1,
  "dRepId": "b2f0...20fb",
  "titleOrRole": "DeFi Developer",
  "nameOrAlias": "Alice The Builder",
  "missionOrGoals": "Promoting transparent DeFi governance on Cardano",
  "primaryFocusAreas": ["DeFi", "Governance"],
  "roles": ["Dev/Builder", "Community Manager"],
  "website": "https://mydrepwebsite.com",
  "twitterHandle": "@aliceBuilder",
  "cip119AnchorUrl": "ipfs://bafy123...",
  "cip119AnchorHash": "blake2b256:abc123..."
}
```

#### 4.2 Ballot Note

**Minted by:** A DRep publishing a stance on a proposal.  
**Purpose:**

- Declares the DRep’s intended vote (`Yes`, `No`, or `Abstain`) for a CIP-1694 proposal.
- Can include a short rationale or reference CIP-108 anchor for deeper explanation.

**Core Fields:**

- `type = "ballotNote"`
- `dRepId` (CIP-1694)
- `proposalId` (CIP-1694)
- `voteChoice`: `"Yes" | "No" | "Abstain"`

**Optional Fields:**

- `rationale`, `timestamp`
- CIP-108 anchor (`anchorUrl`, `anchorHash`)

**Minimal JSON Example:**

```jsonc
{
  "version": 1,
  "type": "ballotNote",
  "dRepId": "b2f0...20fb",
  "proposalId": "abcd1234+0",
  "voteChoice": "Yes",
  "rationale": "Supports Cardano's long-term growth",
  "timestamp": "2025-03-10T12:00:00Z",
  "anchorUrl": "ipfs://proposalDoc",
  "anchorHash": "blake2b256:def456..."
}
```

#### 4.3 Endorsement

**Minted by:** Any stakeholder (SPO, DAO, community member) wishing to show support for a DRep.  
**Purpose:**

- On-chain “vote of confidence,” optionally with a comment or identity proof.
- May include a **minimum ADA** amount to discourage spam.
- Optionally allows endorsers to attach **additional** ADA to assist new DReps (e.g., raising the 500 ADA deposit) or provide financial backing.

**Core Fields:**

- `type = "endorsement"`
- `endorses` = CIP-1694 DRep ID
- `endorserStakeKey` (the minter’s stake key)

**Optional Fields:**

- `identityProof` (e.g., a social media link)
- `comment` (why the endorser supports this DRep)
- `timestamp` (ISO-8601)
- **Financial Contribution**: Some platforms **may** store or display the ADA attached to this NFT (e.g., `"attachedAda": "<lovelaceAmount>"`) if relevant.
- CIP-119 / CIP-108 anchor for more detailed statements.

**Minimum or Additional ADA Considerations**

- **Minimum ADA**: A platform can require a base amount (e.g., 2 ADA) to mint the endorsement NFT, helping deter zero-cost spam.
- **Extra ADA**: Endorsers can optionally contribute a higher amount (e.g., 10 ADA, 500 ADA) to support the DRep’s deposit or other governance activities.
- **Implementation**: Each wallet or dApp **decides** how to handle this attached ADA. For instance, they might introduce tiers of endorsements, each with a distinct cost/benefit.
- **On-Chain Recording**: While the attached ADA is part of the transaction, the NFT’s datum could include a field (`"attachedAda"`) indicating the actual lovelace contributed.

**Minimal JSON Example:**

```jsonc
{
  "version": 1,
  "type": "endorsement",
  "endorses": "b2f0...20fb",
  "endorserStakeKey": "stake1u9xyz...",
  "identityProof": "https://twitter.com/endorserProfile",
  "comment": "I trust this DRep’s track record",
  "timestamp": "2025-03-15T09:00:00Z"

  // If relevant, a field could note how much ADA was attached:
  // "attachedAda": "10000000" // (10 ADA in lovelace)
}
```

### 5. Implementation Guidelines

1. **Datum Format (CIP-68)**

   - Each NFT **must** include a Plutus datum referencing the CIP-1694 IDs and any optional fields above.
   - CIP-68’s reference token mechanism can allow updates if desired (not mandated by this CIP).

2. **Asset Naming & Labels (CIP-67)**

   - Use the same CIP-67 label for these governance NFTs.
   - Actual label allocation requires a **CIP-67 registry entry**.
   - Tools can rely on this label for discovery and classification.

3. **Reference Integrity**

   - Check that `dRepId` and `proposalId` are valid CIP-1694 hashes/IDs.
   - If linking off-chain data, confirm the `url` + `hash` match the CIP-119 or CIP-108 format.

4. **Spam & Authorization**

   - Anyone can mint these tokens; spam or fake endorsements may occur.
   - Governance UIs might validate minter signatures (e.g., does a Ballot Note come from the real DRep stake key?).
   - Endorsements from unknown or low-stake addresses could be flagged by analytics tools.

5. **Extensibility**
   - Additional keys can be introduced over time (CIP-68 is flexible).
   - Future CIP revisions may define new governance NFT types (e.g., “Attestations,” “Milestone Achievements”).

By adopting these definitions and guidelines, builders and governance participants can publish data-rich yet concise NFTs that are **compatible** with CIP-1694 governance flows, **verifiable** on-chain, and **extendable** through CIP-119/CIP-108 anchors.

## Rationale: How Does This CIP Achieve Its Goals?

The principal goal of this CIP is to **improve transparency and accountability** in Cardano governance by adding optional on-chain artifacts—**DRep Credentials**, **Ballot Notes**, and **Endorsements**—without disrupting CIP-1694’s foundational mechanics. Below is a breakdown of the **key rationale** and **design decisions** that guided this proposal.

### Key Motivations

1. **Bridging On-Chain & Off-Chain Data**

   - CIP-1694 does not itself specify how DReps might share their profiles, qualifications, or endorsements on-chain.
   - By using **CIP-68** and **CIP-67**, this CIP standardizes how minimal DRep info (or vote details) can appear directly on-chain, while larger data (e.g., mission statements, proposals) is kept off-chain via **CIP-119** or **CIP-108** anchors.

2. **Reducing Trust Friction**

   - Delegators frequently rely on fragmented off-chain sources (social media, personal websites).
   - Minting an **official** CIP-68 NFT from a DRep’s stake key reduces confusion about who is _really_ behind a given profile or voting stance.

3. **Minimizing Ledger Overhead**

   - Storing massive profile data or extended governance proposals on-chain is costly.
   - By anchoring big files off-chain, transaction costs stay low, while integrity is assured via a **URL + hash**.

4. **Encouraging Verifiable Support**
   - The **Endorsement** NFT type allows stakeholders to provide on-chain “votes of confidence,” potentially with attached ADA (helping new DReps meet deposit needs).
   - Requiring a **minimum ADA** to mint endorsements can mitigate spam and surface only the more substantial supports.

### Key Design Decisions

1. **Optional, Not Mandatory**

   - This CIP neither replaces CIP-1694 nor forces off-chain data onto the ledger.
   - DReps and delegators can opt in if they want more discoverable or **script-readable** metadata; otherwise, CIP-1694’s existing structure remains fully valid.

2. **Modular Anchoring**

   - Leveraging **CIP-119** (DRep Profiles) and **CIP-108** (Proposal Metadata) keeps large data off-chain but verifiable.
   - CIP-68 provides the minimal on-chain “pointer” (datum fields), making it trivial for wallets and governance dashboards to link to or display the anchored data.

3. **Alignment with Existing Governance IDs**

   - DRep IDs remain the **blake2b-224** hash from CIP-1694.
   - Proposals are identified by the existing **txHash + index** format.
   - This ensures no duplication or confusion with alternate IDs.

4. **CIP-67 Labeling for Easier Discovery**

   - All NFTs here use a single new CIP-67 label, making them easily recognized across the ecosystem.
   - Tools can filter these tokens by label for specialized governance dashboards or analytics.

5. **Extensibility & Backward Compatibility**
   - Additional fields or new token types can be introduced by updating the CIP, thanks to **CIP-68**’s flexible key-value approach.
   - Existing off-chain data standards (CIP-119, CIP-108) remain valid even if participants do not adopt these governance NFTs.

## Path to Active

### Acceptance Criteria

To move from **Draft** to **Active**, the following milestones **must** be achieved:

1. **Reference Implementations**

   - [ ] At least two open-source implementations (e.g., scripts, libraries, or dApps) demonstrating:
     - [ ] Minting of all three NFT types (**DRep Credential**, **Ballot Note**, and **Endorsement**) with CIP-68 datums.
     - [ ] Correct CIP-67 naming to identify these governance NFTs.
     - [ ] Proper CIP-1694 ID references and optional CIP-119/CIP-108 off-chain anchors.
   - **Note:** The DRep Collective’s prototype at [https://preview-drep.vercel.app/](https://preview-drep.vercel.app/) is currently being developed and will adapt to changes made in this document.

2. **Wallet & Explorer Support**

   - [ ] At least one Cardano wallet and one block explorer must publicly demonstrate:
     - [ ] Recognition of the CIP-67 asset label for governance NFTs.
     - [ ] Human-readable presentation of CIP-68 fields (DRep IDs, vote choices, etc.).
     - [ ] Proper linkage to off-chain content anchored by CIP-119 or CIP-108.

3. **Governance Tool Integration**

   - [ ] At least one governance analytics or dashboard platform (e.g., a specialized governance app, an updated version of the DRep Collective interface) integrates:
     - [ ] Display of DRep Credentials with CIP-119-based profile data.
     - [ ] Ballot Notes, including any rationale text or CIP-108-linked proposals.
     - [ ] Endorsements, visually mapping relationships between DReps and their supporters, as well as ADA contribution details if relevant.

4. **Community Review**

   - [ ] A public review period of **at least four weeks** must be held, inviting feedback from:
     - CIP editors, DReps, SPOs, wallet/explorer maintainers, and governance experts.
   - [ ] Reviewers confirm:
     - Compatibility with CIP-1694, CIP-119, CIP-108, CIP-68, and CIP-67 (i.e., no conflicts).
     - Tangible value added to Cardano governance without burdensome on-chain overhead.
   - [ ] Consensus is reached to proceed toward **Active** status.

After successful completion of these steps, the authors will formally request the CIP editors to transition this proposal from **Draft** to **Active** in accordance with **CIP-0001**.

### Implementation Plan (Step-by-Step)

1. **Open-Source Reference Implementation**

   - DRep Collective and at least one additional team publish minimal code or tutorials demonstrating NFT minting flows for each governance NFT type.
   - Document CIP-68 usage (datum schemas), CIP-67 labeling, and CIP-119/CIP-108 anchors.

2. **Testnet Deployments**

   - Deploy example DRep Credentials, Ballot Notes, and Endorsements on a public testnet (e.g., Preprod).
   - Validate correct retrieval and verification of off-chain data.

3. **Wallet & Explorer Collaboration**

   - Partner with at least one wallet and explorer team to enable CIP-67 filtering, display on-chain fields from CIP-68, and link to CIP-119/CIP-108 metadata.
   - Provide user feedback, refine UI/UX around governance NFTs.

4. **Governance Dashboard Integration**

   - Incorporate minted governance NFTs into a governance analytics dashboard.
   - Demonstrate improved DRep discovery, advanced analytics (endorsements, voting records), and user-friendly CIP-119/CIP-108 references.

5. **Community Review & Finalization**
   - Document findings from testnet usage and gather open feedback (≥4 weeks).
   - Address concerns or suggested improvements.
   - Request CIP editors to mark this CIP as **Active** once broad support is established.

## Versioning

A `version` field in the NFT datum (starting at `1`) tracks changes to this specification:

- Future revisions **MUST** increment `version` if the on-chain datum format changes.
- Implementations **SHOULD** handle unknown fields gracefully to maintain forward compatibility.
- Major structural overhauls require a new CIP or explicit updates to this one, ensuring backward compatibility for earlier NFT versions.

## Copyright

This work is licensed under the **Creative Commons Attribution 4.0 International License (CC-BY-4.0)**. You are free to share and adapt this CIP for any purpose, provided you give appropriate credit and indicate clearly if any modifications have been made. A full copy of this license is available at:

[https://creativecommons.org/licenses/by/4.0/](https://creativecommons.org/licenses/by/4.0/)
