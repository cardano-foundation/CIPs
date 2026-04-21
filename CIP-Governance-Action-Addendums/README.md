---
CIP: ????
Title: Governance Action Addendums
Category: Metadata, Governance
Status: Proposed
Authors: 
  - Nicolas Cerny <nicolas.cerny@cardanofoundation.org>
Implementors: 
  - N/A
Discussions:
  - https://github.com/cardano-foundation/CIPs/pull/XXXX
Created: 2026-04-21
License: CC-BY-4.0
---

## Abstract

This proposal defines a metadata standard allowing governance action proposers to provide additional, cryptographically verifiable feedback and context to voters after the initial governance action has been submitted. By broadcasting append-only updates via standard transactions using a dedicated metadata label, this standard eliminates information asymmetry while strictly preserving the immutability of the original governance action metadata.

## Motivation

Under the current CIP-1694 and CIP-0108 frameworks, proposers lack a standardized, on-chain mechanism to provide ongoing context or reactions to a governance action once it is submitted. Consequently, proposers often distribute additional information—such as answers to community questions, rationale refinements, or strategic adjustments—through public or private off-chain channels. 

This creates information asymmetry: large DReps with direct communication lines to proposers receive vital context, while smaller DReps and the wider voting public do not. Furthermore, the Cardano Constitution and system design mandate that the original governance action metadata remains strictly immutable, which means that additional context cannot be provided in an updated metadata file. 

To create a level playing field without violating immutability, proposers need a credible, decentralized, append-only mechanism to share updates. These updates must be cryptographically proven to originate from the proposal's author, ensuring equal visibility across all governance explorers and tooling.

**Disclaimer:** These updates are strictly informational. They provide context and rationale but cannot legally or technically alter the on-chain execution payload or promises made in the original, immutable governance action metadata.

## Specification

This standard acts as an extension to the **CIP-0100** (Governance Metadata) framework, utilizing standard Cardano transactions to build an append-only log of contextual updates.

### 1. New Document Type
We introduce a new JSON-LD `@type` named `GovernanceActionUpdate`. 

### 2. Off-chain JSON-LD Schema
Any metadata document claiming to be a `GovernanceActionUpdate` MUST strictly adhere to the following schema structure, extending CIP-0100 and utilizing deep semantic mapping in the `@context`. 

To prevent indexer Denial-of-Service (DoS), the hosted JSON-LD file MUST NOT exceed 50KB in size. Proposers are heavily encouraged to host this payload on decentralized storage (e.g., IPFS, Arweave) to prevent link rot.

```json
{
  "@context": {
    "@language": "en-us",
    "CIP100": "https://github.com/cardano-foundation/CIPs/blob/master/CIP-0100/README.md#",
    "CIPXXXX": "https://github.com/cardano-foundation/CIPs/blob/master/CIP-XXXX/README.md#",
    "hashAlgorithm": "CIP100:hashAlgorithm",
    "body": {
      "@id": "CIPXXXX:body",
      "@context": {
        "references": {
          "@id": "CIPXXXX:references",
          "@container": "@set",
          "@context": {
            "GovernanceMetadata": "CIP100:GovernanceMetadataReference",
            "Other": "CIP100:OtherReference",
            "label": "CIP100:reference-label",
            "uri": "CIP100:reference-uri",
            "referenceHash": {
              "@id": "CIPXXXX:referenceHash",
              "@context": {
                "hashDigest": "CIPXXXX:hashDigest",
                "hashAlgorithm": "CIP100:hashAlgorithm"
              }
            }
          }
        },
        "governanceActionId": "CIPXXXX:governanceActionId",
        "sequenceNumber": "CIPXXXX:sequenceNumber",
        "supersedes": "CIPXXXX:supersedes",
        "updateContext": "CIPXXXX:updateContext"
      }
    },
    "authors": {
      "@id": "CIP100:authors",
      "@container": "@set",
      "@context": {
        "name": "[http://xmlns.com/foaf/0.1/name](http://xmlns.com/foaf/0.1/name)",
        "witness": {
          "@id": "CIP100:witness",
          "@context": {
            "witnessAlgorithm": "CIP100:witnessAlgorithm",
            "publicKey": "CIP100:publicKey",
            "signature": "CIP100:signature"
          }
        }
      }
    }
  },
  "hashAlgorithm": "blake2b-256",
  "body": {
    "governanceActionId": "txHash#index",
    "sequenceNumber": 1,
    "supersedes": null,
    "updateContext": "Following the Town Hall on April 15th, I am providing additional clarity on the budget breakdown...",
    "references": [
      {
        "@type": "Other",
        "label": "Town Hall Recording",
        "uri": "[https://youtube.com/](https://youtube.com/)..."
      }
    ]
  },
  "authors": [
    {
      "name": "Proposer Name",
      "witness": {
        "witnessAlgorithm": "ed25519",
        "publicKey": "<hex-encoded public key>",
        "signature": "<hex-encoded signature of the blake2b-256 hash of the body>"
      }
    }
  ]
}
```

_(Note: `CIPXXXX` will be replaced by the assigned CIP number once merged)._

### 3. Required Body Fields

- `governanceActionId`: The transaction hash and index of the original on-chain governance action this update pertains to.    
- `sequenceNumber`: An integer ensuring chronological order of the append-only updates.    
- `updateContext`: A freeform text field (supporting Markdown) where the proposer provides the additional context.    
- `supersedes`: (Optional) An integer referencing a previous `sequenceNumber`. If present, tooling SHOULD indicate that the referenced previous update has been explicitly retracted or corrected by the author.    
- `references`: (Optional) Links to off-chain discussions, community town halls, FAQs or previous metadata.    

### 4. Cryptographic Provenance and Multi-Author Rules

To prove provenance, the update metadata MUST utilize the `authors` array and `witness` structure defined in CIP-0100.
- The `witness` MUST be a signature generated by the exact same private key whose public verification key was used in the `authors` array of the _original_ governance action's metadata.
- **Multi-Author Rule:** If the original governance action was signed by multiple authors, an update MAY be signed by ANY single author, or combination of authors, present in the original `authors` array.    
- Tooling interfaces MUST verify the signatures and MUST visually demarcate to the user exactly which author(s) from the original proposal signed the update. If a signature does not match an original author, the update MUST be ignored.    

### 5. On-chain Anchoring (Transaction Metadata)

Because the original governance action cannot be altered, the update MUST be anchored via a standard Cardano transaction.
To ensure efficient indexing by governance tooling, this standard requests the dedicated Transaction Metadata Label `1695` via the CIP-0010 registry.
**The 64-Byte Ledger Constraint:** The Cardano ledger strictly rejects any transaction containing a metadata string exceeding 64 bytes.
- Because a 32-byte Blake2b-256 hash or transaction hash is exactly 64 characters when hex-encoded, `txHash` and `dataHash` MAY remain single strings.    
- Because standard URLs and IPFS URIs almost always exceed 64 bytes, the `uri` MUST be chunked into an array of strings, ensuring no single element exceeds the 64-byte limit.

The on-chain transaction metadata MUST follow this structure:

```json
{
  "1695": {
    "txHash": "<32-byte original governance action tx hash>",
    "index": 0,
    "dataHash": "<blake2b-256 hash of the off-chain JSON-LD document>",
    "uri": [
      "ipfs://ipfs/Qm...",
      "...remainder of uri string..."
    ]
  }
}
```

### 6. Indexing, Verification & State Logic Rules

To ensure the integrity of the append-only log, tooling interfaces (indexers and explorers) MUST adhere to the following workflow:

1. **Detection:** Governance tools MUST filter the blockchain for standard transactions containing label `1695`.
2. **URI Reassembly & Fetching:** Indexers MUST concatenate the array of strings found in the `uri` field to reconstruct the full URL. To prevent DoS attacks, indexers MUST enforce a strict timeout (e.g., maximum 5 seconds) when attempting to fetch the off-chain payload.
3. **Hash Verification:** Once fetched, indexers MUST hash the downloaded JSON-LD file using Blake2b-256 and verify it matches the `dataHash` provided in the on-chain metadata. If it does not match, the update MUST be discarded.
4. **Cross-Referencing & Signature Validation:** * Utilizing the `txHash` from the on-chain metadata, resolve the original Governance Action and fetch its original off-chain JSON-LD metadata. 
    * Extract the `publicKey`(s) from the original proposal's `authors` array.
    * Verify that the `publicKey` present in the Addendum's `witness` block exactly matches at least one of the original public keys. 
    * Perform standard CIP-0100 signature verification on the Addendum's `body`. If the keys do not match, or the signature is invalid, the Addendum MUST be discarded.
5. **Conflict Resolution:** If multiple valid updates share the same `sequenceNumber`, indexers MUST prioritize the update contained in the transaction with the lower absolute slot number. If they share the same block, prioritize the lexicographically lower transaction hash.
6. **Terminal State:** Indexers SHOULD NOT render new updates submitted to the chain after the original governance action has reached a finalized state (Ratified, Expired, or Dropped).
    

## Rationale

- **Preserving Immutability:** By using standard transactions to publish updates rather than attempting to alter the governance action itself, this design respects the fundamental immutability requirements of Cardano governance actions outlined in the Constitution.    
- **Authentication via Auxiliary Metadata:** Unlike native CIP-1694 Governance Actions or Votes, which utilize ledger-enforced anchors signed directly by the actor's credential, these updates utilize standard transaction auxiliary metadata (Label 1695). Because any network participant can submit a transaction containing auxiliary metadata, on-chain transaction signatures cannot be used to prove provenance. Therefore, it is strictly mandatory that the off-chain JSON-LD document contains a valid `witness` signature from the original author to prevent malicious actors from broadcasting forged updates.    
- **Hardware Wallet Support:** While hardware wallets cannot natively generate CIP-0100 JSON-LD payloads in isolation, this standard relies on existing ecosystem tooling (such as CLI tools like `cardano-signer` or dedicated frontend DApps) to construct the payload, chunk the on-chain metadata, and request the signature via standard wallet derivation paths.    
- **Separation of Concerns (Label 1695):** Requesting a distinct metadata label (`1695`) instead of overloading `1694` or `674` allows indexers to safely filter for governance updates without routing logic conflicts or having to parse standard transaction comments.    
- **64-Byte Limit Compliance:** Explicitly separating the `txHash` and chunking the `uri` into an array ensures that standard indexers will not fail when attempting to read the on-chain pointer, respecting the hardcoded limits of the Cardano ledger.    

## Path to Active

### Acceptance Criteria

- [ ] The JSON-LD schema for `GovernanceActionUpdate` is finalized.    
- [ ] Label `1695` is successfully registered in the CIP-0010 registry.    
- [ ] At least one major governance interface (e.g., CGOV, GovTool, Adastat) implements the ability to read, verify signatures, and render this append-only metadata log.    
- [ ] At least one metadata creation tool supports generating and signing this specific schema.    

### Implementation Plan

- Gather feedback from tooling providers regarding the indexing of label `1695` transactions.    
- Provide test vectors and sample schemas for wallet and UI developers.