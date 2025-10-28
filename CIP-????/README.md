---
CIP: XXXX
Title: A Standard for On-chain Survey via Info Action
Category: Metadata
Status: Proposed
Authors:
    - Thomas Lindseth <thomas.lindseth@intersectmbo.org>
Implementors: []
Discussions: To-be-added
Created: 2025-10-28
License: CC-BY-4.0
---

## Abstract

This proposal defines a standardized metadata structure for creating and responding to simple, generalized on-chain polls or surveys. It leverages the Conway-era **"Info Action"** and the existing **CIP-0068** metadata standard (using the **674** label) to allow any entity to publish a poll in a machine-readable format. It defines a minimal corresponding structure for voters to use when casting their votes, ensuring that poll data can be reliably created, displayed, and aggregated by any wallet, explorer, or dApp in the Cardano ecosystem. This standard focuses on a simple question, a set of options, and clear aggregation rules, providing a basic, yet powerful, tool for gauging community sentiment.

---

## Motivation: why is this CIP necessary?

While the Cardano governance system is robust for formal decision-making, its tertiary voting mechanism (Yes/No/Abstain) is inherently limited for general community consultation and detailed opinion gathering. This standard allows entities—from foundations and development projects to individual community members—to submit a governance **Info Action** to anchor a structured, multi-option poll on-chain.

It is invaluable for the entire Cardano ecosystem to have a **single, standardized method** for gauging sentiment. This proposal enables the creation of a decentralized, on-chain tool for consultation, ensuring that sentiment and relevant contextual data can be consistently linked to on-chain identity.

By establishing a simple, common standard, we move away from fragmented, off-chain surveys and provide a transparent, reliable signal for the entire community without requiring complex, use-case-specific data structures.

---

## Specification

This specification leverages the **674** message tag for community-defined structured metadata, as established in CIP-0068. It defines two distinct, minimal metadata payloads.

### 1. Poll Definition Payload

This metadata is included in the transaction that creates a governance "**Info Action**" to announce and define the poll. The **674** metadata entry **MUST** contain a `pollDetails` object.

```json
{
  "674": {
    "msg": ["<Short, human-readable title of the poll>"],
    "pollDetails": {
      "specVersion": "1.0", 
      "type": "single-choice",
      "question": "<The full question to be displayed to voters>",
      "description": "<A detailed explanation of the poll (supports markdown)>",
      "options": [
        "<Option 1 text>",
        "<Option 2 text>",
        "<Option N text>"
      ],
      "maxSelections": 1,
      "eligibility": [
        "Stakeholder"
      ],
      "voteWeighting": "StakeBased"
    }
  }
}
````

| Key | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `specVersion` | String | Yes | The version of this polling specification. **MUST** be "1.0". |
| `type` | String | Yes | The type of poll. Supported types are `"single-choice"` and `"multi-select"`. |
| `question` | String | Yes | The primary poll question. Should be concise. |
| `description` | String | Yes | A longer description providing context or rationale. Supports **markdown** for rich text rendering in client applications. |
| `options` | Array of Strings | Yes | An ordered list of the choices available. Min 2 options. The order **MUST** be the order displayed in the UI. |
| `maxSelections` | Positive Integer | Yes | The maximum number of options a user can select. For a `single-choice` poll, this **MUST** be 1. |
| `eligibility` | Array of Strings | No | Defines who is eligible to vote. Valid options: `"DRep"`, `"SPO"`, `"CC"`, `"Stakeholder"` (any address with a registered stake key). If omitted, the poll is open to all stakeholders. |
| `voteWeighting` | String | No | Defines how votes are counted. Options: `"StakeBased"` or `"CredentialBased"`. If omitted, the default is `"StakeBased"`. |

### 2\. Poll Response Payload

This metadata is included in the transaction a voter submits to cast their vote. The **674** metadata entry **MUST** contain a `voteFor` object.

```json
{
  "674": {
    "msg": ["Response to poll: <Title of the poll>"],
    "voteFor": {
        "actionTxId": "<The transaction ID of the Info Action that defined the poll>",
        "selection": [
            "<User's choice (matching option name)>"
        ]
    }
  }
}
```

| Key | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `actionTxId` | String (hex) | Yes | The transaction hash of the "Info Action" that created the poll. This provides an immutable link. |
| `selection` | Array of Strings | Yes | A list of the user's selected options. For `single-choice` polls, this array **MUST** contain exactly one element. Values **MUST** match entries in the `options` array from the `pollDetails`. |

### 3\. Casting a Vote

The method for submitting a poll response depends on the user's role:

  * **For Governance Bodies (DReps, SPOs, CC Members):** The poll response metadata, as defined above, should be included in the same transaction used to cast their formal governance vote (Yes/No/Abstain) on the Info Action.

  * **For Stakeholders:** A stakeholder not casting a formal governance vote **MUST** create a new transaction (e.g., sending a minimal amount of ADA back to their own address) with the sole purpose of including the Poll Response Payload in the transaction's metadata.

### Block Explorer Implementation Guide

Cardano block explorers and other data aggregators should follow these steps to discover, parse, and display poll results:

1.  **Poll Discovery:** Scan transactions for metadata entries with the top-level key **674** containing a `pollDetails` object. The transaction ID of this action is the poll's unique identifier.

2.  **Response Discovery & Linking:** Scan for metadata entries with **674** containing a `voteFor` object, linking them via the `actionTxId` field.

3.  **Voter Eligibility Verification:** If the `eligibility` field is present, verify the credentials of the address that submitted the voting transaction.

4.  **Aggregating Results:** Check the `voteWeighting` field.

      * **If `voteWeighting` is "StakeBased" (or omitted):** For each valid vote, query the on-chain state to determine the voting power (in ADA) associated with the voter's credential at the time of the vote. This ADA value is added to the total for the selected option(s).

      * **If `voteWeighting` is "CredentialBased":** For every valid vote, a weight of **1** (one credential/voter) is added to the total for the selected option(s).

5.  **Displaying Results:** Display the poll's question, description, options, and the total vote count for each option (either in ADA or by credential count).

### CDDL Schema

To ensure unambiguous, machine-readable validation, proposals that define on-chain data structures **MUST** include a CDDL schema.

```cddl
; CIP-00XX On-chain Polls (Version 1.0)

pollDetails = {
  specVersion: "1.0",
  type: "single-choice" / "multi-select",
  question: tstr,
  description: tstr,
  options: [+ tstr],
  maxSelections: uint,
  ? eligibility: [* "DRep" / "SPO" / "CC" / "Stakeholder" ],
  ? voteWeighting: "StakeBased" / "CredentialBased",
}

voteFor = {
  actionTxId: tstr, ; hex-encoded transaction ID of the Info Action
  selection: [+ tstr], ; List of user's selected options
}

; This structure is the content of the CIP-0068 `674` label
cip_00XX_root = {
    "pollDetails" => pollDetails,
    ? "msg" => [ + tstr ],
} / {
    "voteFor" => voteFor,
    ? "msg" => [ + tstr ],
}
```

-----

## Rationale: how does this CIP achieve its goals?

  * **General Purpose:** By removing complex, nested data structures, the metadata payload remains small, cheap to submit, and applicable to any simple question or sentiment check.
  * **Leveraging Existing Standards:** Using CIP-0068 and the Info Action minimizes the need for new on-chain logic, maximizing discoverability and adoption.
  * **Flexible Vote Weighting:** The inclusion of both "StakeBased" and "CredentialBased" weighting makes the standard immediately useful for different contexts, from governance-adjacent questions to simple community temperature checks.

-----

## Path to Active

### Acceptance Criteria

This CIP will be considered Active when the following criteria are met:

  * **Initial Adoption:** At least one poll has been successfully created (via an Info Action) and its details and results are correctly discovered, parsed, and displayed by at least one major Cardano block explorer.
  * **Explorer Support:** At least one major Cardano block explorer has implemented support for discovering, displaying, and correctly aggregating poll results according to the defined `voteWeighting` rules.

### Implementation Plan

  * Gather Community Feedback on this draft via the CIPs repository pull request and Cardano forums.
  * Develop a minimal reference implementation to demonstrate the creation and aggregation of poll data.
  * Encourage Adoption among wallet, explorer, and dApp development teams.

-----

## Copyright

This CIP is licensed under CC-BY-4.0.

```
```
