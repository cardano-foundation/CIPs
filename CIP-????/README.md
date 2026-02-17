---
CIP: XXXX
Title: On-Chain Surveys and Polls
Category: Metadata
Status: Proposed
Authors:
    - Thomas Lindseth <thomas.lindseth@intersectmbo.org>
    - Ryan Wiley <rian222@gmail.com>
Implementors: []
Discussions:
    - https://github.com/cardano-foundation/CIPs/pull/1107
Created: 2025-10-28
License: CC-BY-4.0
---

## Abstract

This proposal defines a standardized transaction metadata format for creating and responding to on-chain surveys and polls under metadata label `17`.

The format supports:
- A single poll question per survey definition.
- Optional linkage to governance actions.
- Deterministic response binding using both survey transaction id and survey hash.
- Extensibility for custom voting methods.

The standard is general-purpose and can be used for governance and non-governance sentiment gathering. It also defines an Info Action profile for tools that want strict behavior when a survey is attached to a governance Info Action.

## Motivation: why is this CIP necessary?

Formal governance actions are intentionally constrained. Those constraints are useful for protocol safety, but they are not sufficient for many community workflows that need structured sentiment data. This is particularly true for Info Actions, which are frustratingly limited in their ability to collect information from stakeholders.

Examples include:
- Polling candidate CIPs to decide hard-fork prioritization.
- Voting on a line item of a budget proposal.
- Gathering bounded numeric preferences (for example, initialization values for a new parameter).

A core design principle for this CIP is conceptual coherence: one survey corresponds to one question. Unrelated questions (for example, budget approval and CIP inclusion) should be represented as separate surveys.

Without a shared on-chain format, these workflows fragment across custom off-chain tools and incompatible schemas. This CIP provides a common metadata interface that wallets, explorers, governance dashboards, and indexers can implement consistently.

## Specification

### Overview

This CIP reserves metadata label `17` for two payload types:
- `surveyDetails`: survey definition payload.
- `surveyResponse`: survey response payload.

A transaction MUST include exactly one of these payloads under label `17`.

A survey is identified by:
- `surveyTxId`: transaction id of the transaction that includes the `surveyDetails` payload.
- `surveyHash`: blake2b-256 hash of canonical CBOR bytes of the envelope `{17: {"surveyDetails": ...}}` (excluding `msg`).

### Survey Definition Payload (`surveyDetails`)

```json
{
  "17": {
    "msg": ["Dijkstra hard-fork CIP shortlist"],
    "surveyDetails": {
      "specVersion": "1.0.0",
      "title": "Dijkstra hard-fork CIP shortlist",
      "description": "Select any number of candidate CIPs for potential inclusion in the Dijkstra hard fork.",
      "question": "Which CIPs should be shortlisted for potential inclusion in Dijkstra?",
      "methodType": "urn:cardano:poll-method:multi-select:v1",
      "options": ["CIP-0108", "CIP-0119", "CIP-0136", "CIP-0149"],
      "maxSelections": 4,
      "eligibility": ["Stakeholder"],
      "voteWeighting": "CredentialBased",
      "referenceAction": {
        "transactionId": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        "actionIndex": 0
      },
      "lifecycle": {
        "startSlot": 120000000,
        "endSlot": 120432000
      }
    }
  }
}
```

#### Survey fields

| Key | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `specVersion` | String | Yes | Semantic version for this schema. This document defines `1.0.0`. |
| `title` | String | Yes | Human-readable survey title. |
| `description` | String | Yes | Human-readable survey context or rationale. |
| `question` | String | Yes | Single question prompt for this survey. |
| `methodType` | URI String | Yes | Voting method identifier. Built-ins are defined below. |
| `options` | Array of Strings | Conditional | Required for option-based methods. |
| `maxSelections` | Positive Integer | Conditional | Required for `multi-select`; absent or `1` for `single-choice`; forbidden for `numeric-range`. |
| `numericConstraints` | Object | Conditional | Required for `numeric-range` method. |
| `methodSchemaUri` | URI String | Conditional | Required for custom methods. |
| `hashAlgorithm` | String | Conditional | Required for custom methods; MUST be `"blake2b-256"`. |
| `methodSchemaHash` | Hex String | Conditional | Required for custom methods; blake2b-256 hash of custom method schema bytes. |
| `eligibility` | Array of Strings | No | Eligible responder classes. Allowed values: `"DRep"`, `"SPO"`, `"CC"`, `"Stakeholder"`. |
| `voteWeighting` | String | No | `"StakeBased"` or `"CredentialBased"`. Default is `"CredentialBased"` if absent. |
| `referenceAction` | Object | No | Optional governance action linkage as `{ transactionId, actionIndex }`. |
| `lifecycle` | Object | No | Optional lifecycle window using slot bounds: `{ startSlot, endSlot }`. |

### Method Types

Built-in `methodType` values in this version:
- `urn:cardano:poll-method:single-choice:v1`
- `urn:cardano:poll-method:multi-select:v1`
- `urn:cardano:poll-method:numeric-range:v1`

Rules:
- `single-choice`:
  - `options` MUST be present and contain at least 2 values.
  - `maxSelections` MUST be absent or set to `1`.
  - Response MUST contain exactly one selected option index in `selection`.
- `multi-select`:
  - `options` MUST be present and contain at least 2 values.
  - `maxSelections` MUST be present, `>= 1`, and `<= len(options)`.
  - Response selection count MUST be between `0` and `maxSelections`.
- `numeric-range`:
  - `numericConstraints` MUST be present.
  - `numericConstraints` MUST include `minValue` and `maxValue` as integers with `minValue <= maxValue`.
  - Optional `step` MUST be a positive integer.
  - `options` and `maxSelections` MUST be absent.
  - Response MUST contain `numericValue` satisfying range and step constraints.

Custom methods:
- Any URI `methodType` that is not one of the built-ins is a custom method.
- Custom methods MUST include all of:
  - `methodSchemaUri`
  - `hashAlgorithm` set to `blake2b-256`
  - `methodSchemaHash`
- Custom methods MAY use `options`, but their semantics are defined by the referenced schema.

YES/NO/ABSTAIN semantics:
- This CIP does not reserve special option codes.
- Authors MAY express YES/NO/ABSTAIN by placing those labels in `options`.

### Survey Response Payload (`surveyResponse`)

```json
{
  "17": {
    "msg": ["Response to Dijkstra hard-fork CIP shortlist"],
    "surveyResponse": {
      "specVersion": "1.0.0",
      "surveyTxId": "efefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefef",
      "surveyHash": "44b7b4b7bad4dce5634b40f16966f45ee52981a7bc3cdd39542b4beffc25d8e9",
      "selection": [1, 3]
    }
  }
}
```

#### Response fields

| Key | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `specVersion` | String | Yes | Semantic version. |
| `surveyTxId` | Hex String | Yes | Transaction id of the `surveyDetails` transaction. |
| `surveyHash` | Hex String | Yes | Blake2b-256 digest described in [Survey Hashing](#survey-hashing). |
| `selection` | Array of UInt | Conditional | Used by option-based methods (`single-choice`, `multi-select`). |
| `numericValue` | Integer | Conditional | Used by `numeric-range`. |
| `customValue` | Transaction Metadatum | Conditional | Used by custom methods. |

For each `surveyResponse`, exactly one of `selection`, `numericValue`, or `customValue` MUST be present.
For `multi-select`, `selection: []` is valid and indicates no survey options selected.

### Linking and Identity

#### Survey linkage

A response is valid only if:
- `surveyTxId` resolves to a transaction that includes label `17` with `surveyDetails`.
- `surveyHash` equals the computed hash of that survey definition payload.

`surveyTxId` and `surveyHash` are both required. A conflicting pair cannot redefine an existing survey; it only creates an invalid response.

#### Optional governance linkage

If `referenceAction` is present in `surveyDetails`, it MUST contain both:
- `transactionId` (hex transaction id)
- `actionIndex` (uint)

This pair is the canonical governance action reference for this standard.

#### Responder identity for deduplication

A tallying tool MUST derive a `responseCredential` (credential key hash) from chain data, not from metadata text.

Deterministic derivation order:
1. If transaction includes governance voting procedures, use the voter credential key hash.
2. Otherwise, transaction MUST include exactly one required signer, and that key hash is the `responseCredential`.
3. If neither rule applies, the response is invalid for deterministic tallying.

### Survey Hashing

`surveyHash` MUST be computed as follows:
1. Build the envelope object `{17: {"surveyDetails": <surveyDetails object>}}`.
2. Do not include `msg` in the hash preimage.
3. Serialize the envelope as canonical CBOR (deterministic map key ordering).
4. Compute blake2b-256 over those bytes.
5. Encode digest as lowercase hexadecimal.

### Duplicate and Ordering Semantics

For a given tuple `(surveyTxId, responseCredential)`:
- If multiple valid responses exist, the latest valid response wins.
- Latest is determined by chain ordering tuple: `(slot, txIndexInBlock, metadataPosition)`.
- `metadataPosition` is the position of label `17` payload in metadata processing order (for this label-specific standard it is typically `0`).

Latest-response semantics replace the full prior response for that tuple.

### Weighting Semantics

- `CredentialBased`: one valid latest response per `responseCredential` counts as weight `1`.
- `StakeBased`: one valid latest response per `responseCredential`, weighted by stake according to tool policy.

This CIP intentionally does not standardize stake snapshot timing or stake source resolution.

### Info Action Profile

This CIP is general-purpose. For tools implementing the Info Action profile:
- `referenceAction` MUST reference the Info Action’s governance action id.
- `lifecycle` MUST be present.
- `lifecycle.startSlot` and `lifecycle.endSlot` MUST match the ledger-defined active lifetime of the referenced Info Action.
- Responses outside the lifecycle window MUST be ignored.

### Transaction-level Constraints

- A single label `17` payload MUST be either `surveyDetails` or `surveyResponse`, not both.
- A response transaction MUST NOT reference itself: `surveyTxId` MUST differ from the response transaction id.

### Block Explorer and dApp Implementation Guide

1. Discover survey definitions by scanning metadata label `17` for `surveyDetails`.
2. For each survey definition transaction, compute and cache `surveyHash`.
3. Discover responses by scanning metadata label `17` for `surveyResponse`.
4. Resolve each response to survey by `(surveyTxId, surveyHash)`.
5. Validate response shape against the survey's `methodType` and constraints.
6. Derive `responseCredential` using [Responder identity for deduplication](#responder-identity-for-deduplication).
7. Apply latest-valid-response-wins ordering.
8. Apply selected weighting mode and produce final tallies.

### CDDL Schema

```cddl
; CIP-00XX On-chain Surveys and Polls (Version 1.0.0)

hex_tx_id = tstr .regexp "[0-9a-fA-F]{64}"
hex_blake2b_256 = tstr .regexp "[0-9a-fA-F]{64}"
uri = tstr

eligibility_role = "DRep" / "SPO" / "CC" / "Stakeholder"
vote_weighting = "StakeBased" / "CredentialBased"

builtin_method_type =
  "urn:cardano:poll-method:single-choice:v1" /
  "urn:cardano:poll-method:multi-select:v1" /
  "urn:cardano:poll-method:numeric-range:v1"

method_type = builtin_method_type / uri

numeric_constraints = {
  minValue: int,
  maxValue: int,
  ? step: uint
}

survey_details = {
  specVersion: tstr,
  title: tstr,
  description: tstr,
  question: tstr,
  methodType: method_type,
  ? options: [+ tstr],
  ? maxSelections: uint,
  ? numericConstraints: numeric_constraints,
  ? methodSchemaUri: uri,
  ? hashAlgorithm: "blake2b-256",
  ? methodSchemaHash: hex_blake2b_256,
  ? eligibility: [* eligibility_role],
  ? voteWeighting: vote_weighting,
  ? referenceAction: {
    transactionId: hex_tx_id,
    actionIndex: uint
  },
  ? lifecycle: {
    startSlot: uint,
    endSlot: uint
  }
}

transaction_metadatum =
    { * transaction_metadatum => transaction_metadatum }
  / [ * transaction_metadatum ]
  / int
  / bytes .size (0..64)
  / text .size (0..64)

survey_response = {
  specVersion: tstr,
  surveyTxId: hex_tx_id,
  surveyHash: hex_blake2b_256,
  selection: [* uint]
} / {
  specVersion: tstr,
  surveyTxId: hex_tx_id,
  surveyHash: hex_blake2b_256,
  numericValue: int
} / {
  specVersion: tstr,
  surveyTxId: hex_tx_id,
  surveyHash: hex_blake2b_256,
  customValue: transaction_metadatum
}

cip_00xx_label_17_payload = {
  "surveyDetails" => survey_details,
  ? "msg" => [+ tstr]
} / {
  "surveyResponse" => survey_response,
  ? "msg" => [+ tstr]
}

cip_00xx_root = cip_00xx_label_17_payload
```

CDDL provides shape constraints. Method-specific mandatory and forbidden field rules in this document are normative and MUST also be enforced by tooling.

### Test Vectors

See [test-vector.md](./test-vector.md) for deterministic examples, canonical CBOR preimages, and expected hashes.

### Versioning

This specification uses semantic versioning in `specVersion`.
This revision defines version `1.0.0`.

## Rationale: how does this CIP achieve its goals?

- A single-question model keeps each survey semantically coherent and avoids combining unrelated decisions.
- Index-based option responses avoid text-matching ambiguity and improve interoperability.
- Requiring both `surveyTxId` and `surveyHash` prevents weak linkage and reduces confusion between similar surveys.
- URI-based method identifiers plus schema hash integrity enable safe extensibility for future/custom methods.
- Latest-valid-response-wins gives participants a correction path while preserving deterministic tally behavior.
- The Info Action profile gives governance tools strict interoperability while keeping the base standard general-purpose.

## Path to Active

### Acceptance Criteria

- [ ] At least two independent tools can create `surveyDetails` payloads with this single-question schema.
- [ ] At least two independent tools can ingest `surveyResponse` payloads and produce matching tallies for shared test vectors.
- [ ] At least one governance-facing tool implements the Info Action profile.
- [ ] Label `17` is registered in `CIP-0010/registry.json`.

### Implementation Plan

- [ ] Finalize CIP text and examples from PR review feedback.
- [ ] Publish reference test vectors and validation notes.
- [ ] Implement and demonstrate end-to-end survey creation + response + tally in at least two toolchains.
- [ ] Document interoperability results and edge-case handling.

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
