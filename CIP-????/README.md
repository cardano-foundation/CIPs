---
CIP: XXXX
Title: On-Chain Surveys and Polls
Category: Metadata
Status: Proposed
Authors:
    - Thomas Lindseth <thomas.lindseth@intersectmbo.org>
Implementors: []
Discussions:
    - https://github.com/cardano-foundation/CIPs/pull/1107
Created: 2025-10-28
License: CC-BY-4.0
---

## Abstract

This proposal defines a generic, standardized transaction metadata structure for creating and responding to on-chain surveys and polls.

All survey-related metadata is encoded under label `17`, chosen as a reference to the Roman census of 17 BC — one of the earliest organized systems for structured population data collection.  

The specification provides a minimal, interoperable format for survey definition and response — enabling wallets, explorers, and dApps across the Cardano ecosystem to reliably create, display, and aggregate poll data.  

Optionally, a survey may **reference a governance action** by transaction ID and action index, allowing it to be contextually linked to an on-chain proposal while remaining independent.

## Motivation: why is this CIP necessary?

Formal Cardano governance actions are intentionally restrictive and structured, but this rigidity limits the ability to gather **informal or exploratory community sentiment**. Off-chain tools (e.g., Google Forms, Typeform) have been used for this purpose, but they fragment data and trust.  

This CIP proposes a **unified, lightweight survey metadata format** that can be used by anyone to:
- Collect feedback.  
- Gauge sentiment.  
- Display aggregated results.  

By allowing an **optional reference to a governance action**, this model supports both:
- **Standalone surveys** (e.g., community temperature checks).  
- **Governance-linked surveys** (e.g., feedback on a specific proposal or Info Action).  

This separation of concerns provides:
- **Clarity:** Surveys are not mistaken for governance actions.  
- **Flexibility:** No deposits, time limits, or procedural constraints.  
- **Discoverability:** Metadata is consistent, indexed, and linkable.  

## Specification

This specification uses metadata label 0017 and defines two payload types:
`surveyDetails` (definition) and `surveyResponse` (vote).

### Survey Definition Payload

This metadata is included in any transaction that defines a survey.  
It can be completely independent or optionally reference an existing governance action.

```json
{
  "0017": {
    "msg": ["<Short, human-readable title of the survey>"],
    "surveyDetails": {
      "specVersion": "1.0",
      "type": "single-choice",
      "question": "<The full question to be displayed to respondents>",
      "description": "<A detailed explanation of the survey (supports markdown)>",
      "options": [
        "<Option 1 text>",
        "<Option 2 text>",
        "<Option N text>"
      ],
      "maxSelections": 1,
      "eligibility": [
        "Stakeholder"
      ],
      "voteWeighting": "StakeBased",
      "referenceAction": {
        "transactionId": "<optional governance action TxId>",
        "actionIndex": 0
      }
    }
  }
}
```

| Key | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `specVersion` | String | Yes | Version of this survey specification. **MUST** be `"1.0"`. |
| `type` | String | Yes | `"single-choice"` or `"multi-select"`. |
| `question` | String | Yes | The main survey question. |
| `description` | String | Yes | A detailed description or rationale (supports markdown). |
| `options` | Array of Strings | Yes | Ordered list of possible responses (min 2). |
| `maxSelections` | Positive Integer | Yes | Max number of options selectable per respondent. |
| `eligibility` | Array of Strings | No | Who can respond. Valid options: `"DRep"`, `"SPO"`, `"CC"`, `"Stakeholder"`. |
| `voteWeighting` | String | No | `"StakeBased"` (default) or `"CredentialBased"`. |
| `referenceAction` | Object | No | Optional link to a governance action. Contains `transactionId` (hex string) and `actionIndex` (integer). |

### Survey Response Payload

This metadata is included in the transaction a user submits to cast a response.

```json
{
  "0017": {
    "msg": ["Response to survey: <Title of the survey>"],
    "surveyResponse": {
      "surveyTxId": "<Transaction ID of the survey definition>",
      "selection": [
        "<User's selected option text>"
      ]
    }
  }
}
```

| Key | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `surveyTxId` | String (hex) | Yes | The transaction ID of the survey definition. |
| `selection` | Array of Strings | Yes | List of selected option(s); must match survey definition. |

### Casting a Response

- **Governance actors (DReps, SPOs, CCs):**  
  May include a survey response in the same transaction as a governance vote if referencing a related action.  
- **Stakeholders:**  
  Submit a self-transaction including the survey response metadata.

### Block Explorer & dApp Implementation Guide

1. **Survey Discovery:**  
   Scan for transactions with label **0017** containing `surveyDetails`.  
   Each survey is uniquely identified by the transaction ID of that transaction.

2. **Response Linking:**  
   Find transactions containing `surveyResponse` and link via `surveyTxId`.

3. **Governance Context (Optional):**  
   If `referenceAction` exists, display the survey as related to that governance action.

4. **Voter Eligibility Verification:**  
   If `eligibility` is defined, validate that the respondent’s address matches the specified category.

5. **Aggregation:**  
   - `"StakeBased"` → sum responses weighted by ADA stake.  
   - `"CredentialBased"` → one vote per valid credential.

6. **Display:**  
   Present the survey’s question, description, options, and weighted results.

### CDDL Schema

```cddl
; CIP-00XX On-chain Surveys (Version 1.0)

surveyDetails = {
  specVersion: "1.0",
  type: "single-choice" / "multi-select",
  question: tstr,
  description: tstr,
  options: [+ tstr],
  maxSelections: uint,
  ? eligibility: [* "DRep" / "SPO" / "CC" / "Stakeholder" ],
  ? voteWeighting: "StakeBased" / "CredentialBased",
  ? referenceAction: {
      transactionId: tstr,  ; hex-encoded TxId of related governance action
      actionIndex: uint
  }
}

surveyResponse = {
  surveyTxId: tstr,  ; hex-encoded TxId of survey definition
  selection: [+ tstr]
}

cip_00XX_root = {
    "surveyDetails" => surveyDetails,
    ? "msg" => [ + tstr ]
} / {
    "surveyResponse" => surveyResponse,
    ? "msg" => [ + tstr ]
}
```

## Rationale: how does this CIP achieve its goals?

- **General-purpose:**  
  Works for any form of sentiment collection — governance-related or otherwise.  
- **Lightweight & cheap:**  
  Pure metadata, no deposits or complex data structures.  
- **Discoverable & linkable:**  
  Optional `referenceAction` preserves relational context.  
- **Extensible:**  
  Future versions can add optional fields (e.g., categorization or free-text support) without breaking compatibility.

### Design Evolution

Early drafts of this proposal used governance *Info Actions* as the carrier for survey metadata. Through review discussions, this approach was replaced with a **standalone metadata model** to remove deposit and lifetime requirements, simplify tooling integration, and broaden applicability beyond governance-specific use cases. The optional `referenceAction` field was introduced to maintain the ability to link surveys contextually to governance actions when relevant.

## Path to Active

### Acceptance Criteria

- At least one survey is published using this structure and correctly parsed by an explorer or wallet.  
- At least one explorer implements proper discovery, linking, and aggregation logic.  

### Implementation Plan

- Gather feedback via CIP repository and governance forums.  
- Build a reference implementation and indexer.  
- Encourage integration into major wallets and governance dashboards.

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
