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
- One or more poll questions per survey definition.
- Optional linkage to governance actions via governance action anchor metadata.
- Deterministic response binding using survey transaction id.
- Extensibility for custom voting methods.

The standard is general-purpose and can be used for governance and non-governance sentiment gathering. It also defines an Info Action profile for tools that want strict behavior when a survey is attached to a governance Info Action.

## Motivation: why is this CIP necessary?

Formal governance actions are intentionally constrained. Those constraints are useful for protocol safety, but they are not sufficient for many community workflows that need structured sentiment data. This is particularly true for Info Actions, which are frustratingly limited in their ability to collect information from stakeholders.

Examples include:
- Polling candidate CIPs to decide hard-fork prioritization.
- Voting on a line item of a budget proposal.
- Gathering bounded numeric preferences (for example, initialization values for several related parameters).

A core design principle for this CIP is grouping related questions in one survey while keeping shared governance constraints at the survey level. This avoids unnecessary survey proliferation for parameter bundles while preserving deterministic validation and tallying.

Without a shared on-chain format, these workflows fragment across custom off-chain tools and incompatible schemas. This CIP provides a common metadata interface that wallets, explorers, governance dashboards, and indexers can implement consistently.

## Specification

### Overview

This CIP reserves metadata label `17` for two payload types:
- `surveyDetails`: survey definition payload.
- `surveyResponse`: survey response payload.

A transaction MUST include exactly one of these payloads under label `17`.
Survey metadata under label `17` is valid as a standalone mechanism and does not require any governance action.

A survey is identified by:
- `surveyTxId`: transaction id of the transaction that includes the `surveyDetails` payload.

### Survey Definition Payload (`surveyDetails`)

```json
{
  "17": {
    "msg": ["Dijkstra hard-fork CIP shortlist"],
    "surveyDetails": {
      "specVersion": "1.0.0",
      "title": "Dijkstra hard-fork CIP shortlist",
      "description": "Select any number of candidate CIPs for potential inclusion in the Dijkstra hard fork.",
      "questions": [
        {
          "questionId": "cip_shortlist",
          "question": "Which CIPs should be shortlisted for potential inclusion in Dijkstra?",
          "methodType": "urn:cardano:poll-method:multi-select:v1",
          "options": ["CIP-0108", "CIP-0119", "CIP-0136", "CIP-0149"],
          "maxSelections": 4
        }
      ],
      "eligibility": ["DRep"],
      "voteWeighting": "CredentialBased",
      "lifecycle": {
        "startSlot": 120000000,
        "endSlot": 120432000
      }
    }
  }
}
```

#### Survey-level fields

| Key | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `specVersion` | String | Yes | Semantic version for this schema. This document defines `1.0.0`. |
| `title` | String | Yes | Human-readable survey title. |
| `description` | String | Yes | Human-readable survey context or rationale. |
| `questions` | Array of Question Objects | Yes | Survey questions. MUST contain at least one item. |
| `eligibility` | Array of Strings | No | Eligible responder classes. Allowed values: `"DRep"`, `"SPO"`, `"CC"`, `"Stakeholder"`. |
| `voteWeighting` | String | Yes | `"StakeBased"` or `"CredentialBased"`. |
| `lifecycle` | Object | No | Optional lifecycle window using slot bounds: `{ startSlot, endSlot }`. |

#### Question object fields (`questions[]` items)

| Key | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `questionId` | String | Yes | Unique identifier within a survey. |
| `question` | String | Yes | Question prompt. |
| `methodType` | URI String | Yes | Voting method identifier. Built-ins are defined below. |
| `options` | Array of Strings | Conditional | Required for option-based methods. |
| `maxSelections` | Positive Integer | Conditional | Required for `multi-select`; absent or `1` for `single-choice`; forbidden for `numeric-range`. |
| `numericConstraints` | Object | Conditional | Required for `numeric-range` method. |
| `methodSchemaUri` | URI String | Conditional | Required for custom methods. |
| `hashAlgorithm` | String | Conditional | Required for custom methods; MUST be `"blake2b-256"`. |
| `methodSchemaHash` | Hex String | Conditional | Required for custom methods; blake2b-256 hash of custom method schema bytes. |

Question objects MUST NOT include `eligibility`, `voteWeighting`, or `lifecycle`. Those fields are survey-level only and apply uniformly to all questions in the survey.

#### Eligibility and weighting configuration rules

- `voteWeighting` MUST be present.
- If `voteWeighting = "StakeBased"`:
  - `eligibility`, if present, MUST NOT include `"CC"`.
  - For standalone surveys (no governance-action linkage), `lifecycle.endSlot` MUST be present and is used as the snapshot point for stake weighting.
- If `voteWeighting = "CredentialBased"` and `eligibility` includes any of `"DRep"`, `"SPO"`, or `"CC"`, tooling MUST enforce role-membership validation for those roles as specified in [Weighting Semantics](#weighting-semantics).

### Method Types

Built-in `methodType` values in this version:
- `urn:cardano:poll-method:single-choice:v1`
- `urn:cardano:poll-method:multi-select:v1`
- `urn:cardano:poll-method:numeric-range:v1`

Rules (applied per question):
- `single-choice`:
  - `options` MUST be present and contain at least 2 values.
  - `maxSelections` MUST be absent or set to `1`.
  - A response answer MUST contain exactly one selected option index in `selection`.
- `multi-select`:
  - `options` MUST be present and contain at least 2 values.
  - `maxSelections` MUST be present, `>= 1`, and `<= len(options)`.
  - Response selection count MUST be between `0` and `maxSelections`.
- `numeric-range`:
  - `numericConstraints` MUST be present.
  - `numericConstraints` MUST include `minValue` and `maxValue` as integers with `minValue <= maxValue`.
  - Optional `step` MUST be a positive integer.
  - `options` and `maxSelections` MUST be absent.
  - Response answer MUST contain `numericValue` satisfying range and step constraints.

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
      "answers": [
        {
          "questionId": "cip_shortlist",
          "selection": [1, 3]
        }
      ]
    }
  }
}
```

#### Response fields

| Key | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `specVersion` | String | Yes | Semantic version. |
| `surveyTxId` | Hex String | Yes | Transaction id of the `surveyDetails` transaction. |
| `answers` | Array of Answer Objects | Yes | Response answers keyed by `questionId`. MUST be non-empty. |

#### Answer object fields (`answers[]` items)

| Key | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `questionId` | String | Yes | References a question in `surveyDetails.questions[]`. |
| `selection` | Array of UInt | Conditional | Used by option-based methods (`single-choice`, `multi-select`). |
| `numericValue` | Integer | Conditional | Used by `numeric-range`. |
| `customValue` | Transaction Metadatum | Conditional | Used by custom methods. |

Normative response-shape rules:
- For `answers[]`:
  - Each item MUST include `questionId`.
  - Each `questionId` MUST reference an existing question in the referenced survey definition.
  - Each item MUST include exactly one of `selection`, `numericValue`, or `customValue`.
  - The chosen answer value key MUST be compatible with the referenced question's `methodType`.
  - `questionId` values MUST be unique within one response payload.
- For `multi-select`, `selection: []` is valid and indicates no survey options selected.

### Linking and Identity

#### Survey linkage

A response is valid only if:
- `surveyTxId` resolves to a transaction that includes label `17` with `surveyDetails`.
- If `surveyTxId` cannot be resolved to such a transaction, the response is invalid.

#### Governance action anchor linkage

Survey-to-action linkage is canonicalized as **Action -> Survey**.
This linkage is optional and only applies when a governance action wants to attach a survey context.

When a governance action links to a survey, the governance action anchor metadata MUST include:
- `surveyTxId`

Anchor schema:

```json
{
  "specVersion": "1.0.0",
  "kind": "cardano-governance-survey-link",
  "surveyTxId": "efefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefef"
}
```

Validation rules:
- `surveyTxId` MUST resolve to a transaction that includes label `17` with `surveyDetails`.
- Anchor metadata MUST use top-level `surveyTxId`; the legacy nested form `surveyRef.surveyTxId` is invalid for this version.
- If validation fails, the governance-action-to-survey link is invalid and tooling MUST NOT attach that survey to the action.

#### Effective eligibility for governance-linked surveys

For surveys linked to a governance action through valid anchor metadata:
- `actionEligibility` MUST be derived from the linked governance action voter classes.
- If `surveyDetails.eligibility` is absent, `effectiveEligibility = actionEligibility`.
- If `surveyDetails.eligibility` is present, `effectiveEligibility = actionEligibility ∩ surveyDetails.eligibility`.
- If the intersection is empty, the linked survey configuration is invalid and responses MUST be ignored.

#### Responder identity for deduplication

A tallying tool MUST derive a `responseCredential` (credential key hash) from chain data, not from metadata text.

Deterministic derivation rules:
1. For governance-linked surveys, the response transaction MUST include governance voting procedures. The voter credential key hash is the `responseCredential`.
2. For standalone surveys with `voteWeighting = "CredentialBased"`:
   - If governance voting procedures are present, use the voter credential key hash.
   - Otherwise, transaction MUST include exactly one required signer, and that key hash is the `responseCredential`.
3. For standalone surveys with `voteWeighting = "StakeBased"`:
   - Tooling MUST derive exactly one stake credential from stake-credential signals in chain data (for example withdrawals, certificates, or governance voting procedures that carry a stake credential).
   - If zero or multiple distinct stake credentials are derivable, the response is invalid.
   - The derived stake credential key hash is the `responseCredential`.

### Duplicate and Ordering Semantics

For a given tuple `(surveyTxId, responseCredential)`:
- If multiple valid responses exist, the latest valid response wins.
- Latest is determined by chain ordering tuple: `(slot, txIndexInBlock, metadataPosition)`.
- `metadataPosition` is the position of label `17` payload in metadata processing order (for this label-specific standard it is typically `0`).

Latest-response semantics replace the full prior response for that tuple.

### Weighting Semantics

- `CredentialBased`:
  - One valid latest response per `responseCredential` counts as weight `1`.
  - This mode is not sybil resistant by itself; transaction fees are the primary spam cost.
  - If eligibility enforcement includes `"DRep"`, `"SPO"`, or `"CC"`, tooling MUST validate those role memberships from chain data for each response; responses that cannot be verified MUST be treated as invalid.
  - `"Stakeholder"` does not require role-membership validation.
- `StakeBased`:
  - One valid latest response per `responseCredential`, weighted by stake in the applicable role domain.
  - `"CC"` MUST NOT be used with `StakeBased`.
  - For governance-linked surveys, stake weighting MUST mirror the linked governance action's role-specific stake distribution and snapshot logic.
  - For standalone surveys, stake weighting snapshot MUST be taken at `lifecycle.endSlot`.
  - When multiple role domains are eligible, canonical results are per-role tallies. Tools MAY additionally publish merged/composite tallies.

### Security and Tooling Guidance

- `CredentialBased` can be sybil attacked when no governance-role validation is applied.
- Tools SHOULD surface warning text for `CredentialBased` surveys, especially when `eligibility` is absent or includes `"Stakeholder"`.
- Mixing stake domains (for example DRep and SPO) into one opaque total can obscure interpretation. Tools SHOULD always expose per-role canonical tallies even when publishing merged views.
- Governance-linked surveys inherit stronger anti-sybil guarantees when responses come from governance voting procedures and eligibility is bounded by action voter classes.

### Info Action Profile

This CIP is general-purpose. For tools implementing the Info Action profile:
- The Info Action anchor metadata MUST include top-level `surveyTxId` as specified in [Governance action anchor linkage](#governance-action-anchor-linkage).
- The `surveyTxId` binding MUST be valid.
- Responses MUST include governance voting procedures.
- `effectiveEligibility` MUST be derived as specified in [Effective eligibility for governance-linked surveys](#effective-eligibility-for-governance-linked-surveys).
- `lifecycle` MUST be present.
- `lifecycle.startSlot` and `lifecycle.endSlot` MUST match the ledger-defined active lifetime of the referencing Info Action.
- Responses outside the lifecycle window MUST be ignored.

### Transaction-level Constraints

- A single label `17` payload MUST be either `surveyDetails` or `surveyResponse`, not both.
- A response transaction MUST NOT reference itself: `surveyTxId` MUST differ from the response transaction id.
- If governance-action linkage is provided, it MUST be encoded in governance action anchor metadata, not in `surveyDetails`.

### Block Explorer and dApp Implementation Guide

1. Discover survey definitions by scanning metadata label `17` for `surveyDetails`.
2. Optionally discover governance actions with anchor metadata carrying `kind = "cardano-governance-survey-link"`.
3. If present, validate governance-action-to-survey linkage by `surveyTxId`.
4. For linked surveys, compute `effectiveEligibility` from governance action voter classes and optional survey eligibility intersection.
5. Discover responses by scanning metadata label `17` for `surveyResponse`.
6. Resolve each response to survey by `surveyTxId`.
7. Validate each response answer against the corresponding survey question method and constraints.
8. Derive `responseCredential` using [Responder identity for deduplication](#responder-identity-for-deduplication).
9. Enforce role-membership checks required by [Weighting Semantics](#weighting-semantics).
10. Apply latest-valid-response-wins ordering.
11. Apply selected weighting mode and produce per-role canonical tallies (and optional merged views).

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

survey_question = {
  questionId: tstr,
  question: tstr,
  methodType: method_type,
  ? options: [+ tstr],
  ? maxSelections: uint,
  ? numericConstraints: numeric_constraints,
  ? methodSchemaUri: uri,
  ? hashAlgorithm: "blake2b-256",
  ? methodSchemaHash: hex_blake2b_256
}

survey_details = {
  specVersion: tstr,
  title: tstr,
  description: tstr,
  questions: [+ survey_question],
  ? eligibility: [* eligibility_role],
  voteWeighting: vote_weighting,
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

answer_item = {
  questionId: tstr,
  selection: [* uint]
} / {
  questionId: tstr,
  numericValue: int
} / {
  questionId: tstr,
  customValue: transaction_metadatum
}

survey_response = {
  specVersion: tstr,
  surveyTxId: hex_tx_id,
  answers: [+ answer_item]
}

cip_00xx_label_17_payload = {
  "surveyDetails" => survey_details,
  ? "msg" => [+ tstr]
} / {
  "surveyResponse" => survey_response,
  ? "msg" => [+ tstr]
}

cip_00xx_root = cip_00xx_label_17_payload

; Governance action anchor metadata for Action -> Survey linkage
governance_action_anchor_survey_link = {
  specVersion: tstr,
  kind: "cardano-governance-survey-link",
  surveyTxId: hex_tx_id
}
```

CDDL provides shape constraints. Method-specific mandatory and forbidden field rules in this document are normative and MUST also be enforced by tooling.

### Test Vectors

See [test-vector.md](./test-vector.md) for deterministic examples and canonical CBOR payload vectors.

### Versioning

This specification uses semantic versioning in `specVersion`.
This revision defines version `1.0.0`.

## Rationale: how does this CIP achieve its goals?

- Multi-question surveys let authors collect related signals (including mixed method types) in one survey object.
- Survey-level required and governance fields preserve shared lifecycle/eligibility semantics across all included questions.
- Question-level method fields keep validation explicit and deterministic per question.
- Index-based option responses avoid text-matching ambiguity and improve interoperability.
- Binding responses and action links by `surveyTxId` keeps survey linkage deterministic and interoperable.
- Requiring explicit `voteWeighting` removes ambiguous defaults and forces clear tally intent.
- Governance-linked surveys can inherit governance voter-class constraints while still allowing surveys to narrow eligibility via intersection.
- Role-aware validation and per-role stake tallies reduce sybil and mixed-domain interpretation risks.
- Canonical `Action -> Survey` linkage via governance action anchors avoids circular transaction-reference dependencies.
- URI-based method identifiers plus schema hash integrity enable safe extensibility for future/custom methods.
- Latest-valid-response-wins gives participants a correction path while preserving deterministic tally behavior.
- The Info Action profile gives governance tools strict interoperability while keeping the base standard general-purpose.

## Path to Active

### Acceptance Criteria

- [ ] At least two independent tools can create `surveyDetails` payloads with the `questions[]` schema.
- [ ] At least two independent tools can ingest `surveyResponse` payloads with `answers[]` and produce matching tallies for shared test vectors.
- [ ] At least one governance-facing tool implements the Info Action profile.
- [ ] Label `17` is registered in `CIP-0010/registry.json`.

### Implementation Plan

- [ ] Finalize CIP text and examples from PR review feedback.
- [ ] Publish reference test vectors and validation notes.
- [ ] Implement and demonstrate end-to-end survey creation + response + tally in at least two toolchains.
- [ ] Document interoperability results and edge-case handling.

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
