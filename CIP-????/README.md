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

## Motivation: Why is this CIP necessary?

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
      "roleWeighting": {
        "DRep": "CredentialBased"
      },
      "endEpoch": 504
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
| `roleWeighting` | Object | Yes | Map from responder role to weighting mode. Keys MUST be a subset of `"DRep"`, `"SPO"`, `"CC"`, `"Stakeholder"` and define eligibility exactly. |
| `endEpoch` | Integer | Yes | Inclusive epoch cutoff for response validity, deterministic tally re-verification anchor, and weighting snapshot point for weighted modes. |

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
| `methodSchemaHash` | Hex String | Conditional | Required for custom methods; blake2b-256 hash of raw bytes fetched from `methodSchemaUri`. |

Question objects MUST NOT include `roleWeighting` or `endEpoch`. Those fields are survey-level only and apply uniformly to all questions in the survey.

#### Role weighting configuration rules

- `roleWeighting` MUST be present and MUST include at least one role key.
- Eligible responder classes are exactly the keys present in `roleWeighting`.
- Allowed role-to-weighting mappings:
  - `CC` MAY only use `"CredentialBased"`.
  - `DRep` MAY use `"CredentialBased"` or `"StakeBased"`.
  - `SPO` MAY use `"CredentialBased"`, `"StakeBased"`, or `"PledgeBased"`.
  - `Stakeholder` MAY only use `"StakeBased"`.
- `endEpoch` MUST be present.
- Responses are valid only when `responseEpoch <= endEpoch`.
- Tally inclusion MUST additionally pass mandatory re-verification at `endEpoch`.

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
  - `methodSchemaHash`
- `methodSchemaHash` MUST be computed over the exact raw bytes fetched from `methodSchemaUri` (no canonicalization or reformatting).
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
      "responderRole": "DRep",
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
| `responderRole` | String | Yes | Claimed responder role. MUST be one of `"DRep"`, `"SPO"`, `"CC"`, `"Stakeholder"`. |
| `answers` | Array of Answer Objects | Yes | Response answers keyed by `questionId`. MUST be non-empty. |

#### Answer object fields (`answers[]` items)

| Key | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `questionId` | String | Yes | References a question in `surveyDetails.questions[]`. |
| `selection` | Array of UInt | Conditional | Used by option-based methods (`single-choice`, `multi-select`). |
| `numericValue` | Integer | Conditional | Used by `numeric-range`. |
| `customValue` | Transaction Metadatum | Conditional | Used by custom methods. |

Normative response-shape rules:
- `surveyResponse.responderRole` MUST be present and MUST be one of `"DRep"`, `"SPO"`, `"CC"`, `"Stakeholder"`.
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
- For linked surveys, `actionEligibility` MUST be derived from the linked governance action voter classes.
- For linked surveys, tooling MUST derive the linked governance action id (`linkedActionId`) from the governance action that carries the survey-link anchor.
- For linked surveys, `linkedRoleWeighting` is the intersection of `roleWeighting` keys with `actionEligibility`, preserving configured modes for surviving roles.
- If `linkedRoleWeighting` is empty, the governance-action-to-survey link is invalid.
- For linked surveys, tooling MUST derive the governance action active voting end epoch from ledger rules and require exact equality with survey `endEpoch`.
- If survey `endEpoch` does not exactly match the action voting end epoch, the governance-action-to-survey link is invalid.
- If linkage validation fails, tooling MUST NOT attach that survey to the governance action.
- Linkage invalidity does not invalidate the survey as standalone metadata.

#### Responder identity for deduplication

A tallying tool MUST treat `surveyResponse.responderRole` as a required role claim and MUST validate it against chain-derived role evidence. `responseCredential` (credential key hash) MUST be derived from chain data.
Tools MUST NOT blindly trust role claims that appear in on-chain response metadata.
Validation MUST run in two phases:
- response-time validation (at response inclusion),
- tally-time re-verification (at survey `endEpoch` snapshot).
Only responses that pass both phases are counted.

Deterministic derivation rules:
1. `surveyResponse.responderRole` is mandatory and is a role claim, not authoritative identity by itself.
2. Candidate derivation MUST consider all relevant chain evidence sources:
   - transaction-body `voting_procedures` entries (Conway transaction body field `19`),
   - required signers,
   - and stake-credential signals (for example withdrawals/certificates/`voting_procedures` entries carrying stake credentials).
3. For governance-linked surveys, tooling MUST derive `linkedActionId` from the governance action that links the survey.
4. For governance-linked surveys, response transactions MUST include a non-empty transaction-body `voting_procedures` element.
5. For governance-linked surveys, `voting_procedures` MUST contain exactly one voter entry, and that voter entry MUST contain exactly one `(govActionId, votingProcedure)` entry.
6. For governance-linked surveys, the single `govActionId` in `voting_procedures` MUST equal `linkedActionId`; otherwise the response is invalid.
7. For governance-linked surveys, a response is valid only if:
   - the role derived from the single `voting_procedures` voter entry exactly equals claimed `surveyResponse.responderRole`,
   - claimed `surveyResponse.responderRole` exists in `linkedRoleWeighting`,
   - exactly one eligible `responseCredential` is derivable from that single voter entry.
8. For standalone surveys, a response is valid only if:
   - claimed `surveyResponse.responderRole` exists in `roleWeighting`,
   - candidate derivation is restricted to claimed `surveyResponse.responderRole`,
   - exactly one eligible `responseCredential` is derivable for the claimed role.
9. Stakeholder role derivation (standalone and linked):
   - `Stakeholder` is valid when claimed `surveyResponse.responderRole = "Stakeholder"` and exactly one eligible stake credential is derivable for the signer.
   - The presence of governance-role candidates (`DRep`, `SPO`, `CC`) does not by itself invalidate a `Stakeholder` claim.
   - A signer MAY submit separate responses for different claimed roles, provided each claimed role independently passes all response-time and tally-time checks.
10. A response is invalid when claimed `surveyResponse.responderRole` does not match chain-derived role evidence.
11. For `DRep`, `SPO`, and `CC`, role-membership checks are evaluated at response time.
12. During tallying, tooling MUST re-verify each response at the `endEpoch` snapshot:
   - re-derive role/credential evidence from the response transaction witnesses/signers and other chain evidence sources,
   - re-check role-membership and credential eligibility at `endEpoch`.
13. A response MUST be excluded from tally results when tally-time re-verification fails, even if it passed response-time validation.

### Epoch Semantics

- `endEpoch` is mandatory for every survey definition.
- `responseEpoch` is derived from the response transaction inclusion via ledger epoch mapping.
- Responses with `responseEpoch > endEpoch` are invalid.
- Role-membership and credential eligibility checks are evaluated at response time and MUST be re-verified at tally time.
- Tally-time re-verification is anchored to the survey `endEpoch` snapshot to preserve deterministic, reproducible tallies.
- A response is counted only if it passes both response-time validation and `endEpoch` tally-time re-verification.
- For `StakeBased` and `PledgeBased`, weighting snapshots are taken at `endEpoch` for both linked and standalone surveys.

### Duplicate and Ordering Semantics

For a given tuple `(surveyTxId, responderRole, responseCredential)`:
- If multiple responses pass both validation phases, the latest valid response wins.
- Latest is determined by chain ordering tuple: `(slot, txIndexInBlock, metadataPosition)`.
- `metadataPosition` is the position of label `17` payload in metadata processing order (for this label-specific standard it is typically `0`).

Latest-response semantics replace the full prior response for that tuple.

### Weighting Semantics

- For each role key in:
  - `linkedRoleWeighting` (for linked surveys), or
  - `roleWeighting` (for standalone surveys),
  one valid latest response per `(surveyTxId, responderRole, responseCredential)` contributes to that role's tally.
- `CredentialBased`:
  - Weight is `1` per valid latest response.
  - This mode is not sybil resistant by itself; transaction fees are the primary spam cost.
- `StakeBased`:
  - Snapshot point is `endEpoch`.
  - Weight is role-domain stake at snapshot:
    - `DRep`: governance voting power of `responseCredential` at snapshot.
    - `SPO`: active stake controlled by `responseCredential` across mapped active registered pools at snapshot.
    - `Stakeholder`: ADA stake controlled by `responseCredential` at snapshot.
- `PledgeBased`:
  - `SPO`-only mode.
  - Weight is the sum of live pledge over active registered pools mapped to `responseCredential` at snapshot.
  - Declared pledge MUST NOT be used.
  - Snapshot point is `endEpoch`.
  - If `responseCredential` maps to zero active registered pools at snapshot, the response remains valid and contributes weight `0`.
- Canonical outputs MUST be per-role tallies.
- Tools MAY additionally publish merged/composite outputs only if:
  - the merged/composite output is explicitly labeled as non-canonical,
  - merge logic is disclosed alongside the output,
  - and canonical per-role tallies remain available as primary outputs.

### Tool Output Requirements

- Tools MUST expose canonical per-role tallies as primary outputs whenever multiple roles are configured.
- Tools MUST NOT present merged/composite totals as canonical role results.
- Any merged/composite display (for example "All roles") MUST explicitly disclose its merge policy and weighting interpretation.
- Audit/export output MUST include `responderRole`, `responseCredential`, counted/excluded status, and exclusion reason when applicable.

### Security and Tooling Guidance

- `CredentialBased` can be sybil attacked when governance-role validation is not applied.
- Mixing weighting units across roles (count/stake/pledge) can obscure interpretation. Tools MUST expose per-role canonical tallies and clearly label any merged output as non-canonical.
- Governance-linked surveys inherit stronger anti-sybil guarantees when responses come from transaction-body `voting_procedures` and role eligibility is bounded by action voter classes.
- `PledgeBased` reduces declared-pledge ambiguity by requiring live pledge; tools SHOULD disclose snapshot epoch and mapped pool set used for each weighted response.
- Required `responderRole` claims do not replace chain validation; tools MUST reject responses when claimed role and chain-derived role evidence disagree.
- Standalone and linked surveys both require full tx-level identity verification; tooling MUST verify that claimed role/credential evidence matches the actual signer/witness context (for example, the wallet credentials that created the response transaction).

### Info Action Profile

This CIP is general-purpose. For tools implementing the Info Action profile:
- The Info Action anchor metadata MUST include top-level `surveyTxId` as specified in [Governance action anchor linkage](#governance-action-anchor-linkage).
- The `surveyTxId` linkage MUST satisfy all linked-survey compatibility checks in [Governance action anchor linkage](#governance-action-anchor-linkage).
- Responses MUST include claimed `responderRole`.
- Responses MUST include a non-empty transaction-body `voting_procedures` element.
- For linked responses, `voting_procedures` MUST contain exactly one voter entry and exactly one `(govActionId, votingProcedure)` entry, and that `govActionId` MUST equal the linked action id.
- Tally-time re-verification at `endEpoch` remains mandatory for linked responses.
- `endEpoch` MUST exactly match the ledger-defined active voting end epoch of the referencing Info Action.
- Responses with `responseEpoch > endEpoch` MUST be ignored.
- Other governance action types may also link surveys; additional type-specific profiles are out of scope for this CIP version.

### Transaction-level Constraints

- A single label `17` payload MUST be either `surveyDetails` or `surveyResponse`, not both.
- A response transaction MUST NOT reference itself: `surveyTxId` MUST differ from the response transaction id.
- If governance-action linkage is provided, it MUST be encoded in governance action anchor metadata, not in `surveyDetails`.

### Block Explorer and dApp Implementation Guide

1. Discover survey definitions by scanning metadata label `17` for `surveyDetails`.
2. Optionally discover governance actions with anchor metadata carrying `kind = "cardano-governance-survey-link"`.
3. If present, validate governance-action-to-survey linkage by `surveyTxId`, linked role compatibility, and exact `endEpoch` equality with the action's canonical voting end epoch; derive `linkedActionId`.
4. Discover responses by scanning metadata label `17` for `surveyResponse`.
5. Resolve each response to survey by `surveyTxId`.
6. Validate each response answer against the corresponding survey question method and constraints.
7. Validate claimed `responderRole` and derive exactly one eligible `responseCredential` for that claimed role using [Responder identity for deduplication](#responder-identity-for-deduplication), including linked-survey checks for `voting_procedures` cardinality and `linkedActionId` match.
8. Filter responses by `responseEpoch <= endEpoch`.
9. Enforce role-membership and credential eligibility checks at response time as required by [Responder identity for deduplication](#responder-identity-for-deduplication) and [Weighting Semantics](#weighting-semantics).
10. At or after `endEpoch`, re-verify each response using `endEpoch` snapshot state (role-membership, credential eligibility, and claim-vs-chain consistency); exclude failures.
11. Apply latest-valid-response-wins ordering per `(surveyTxId, responderRole, responseCredential)` over responses that passed both validation phases.
12. Derive `StakeBased` and `PledgeBased` weights from `endEpoch` snapshot state; for `PledgeBased`, derive active pool set mapped to `responseCredential` and resolve live pledge values.
13. Apply selected per-role weighting and produce canonical per-role tallies.
14. If publishing optional merged/composite views, label them as non-canonical and disclose merge logic per [Tool Output Requirements](#tool-output-requirements).

### CDDL Schema

```cddl
; CIP-00XX On-chain Surveys and Polls (Version 1.0.0)

hex_tx_id = tstr .regexp "[0-9a-fA-F]{64}"
hex_blake2b_256 = tstr .regexp "[0-9a-fA-F]{64}"
uri = tstr

; at least one key is required by normative prose
role_weighting = {
  ? DRep: ("CredentialBased" / "StakeBased"),
  ? SPO: ("CredentialBased" / "StakeBased" / "PledgeBased"),
  ? CC: "CredentialBased",
  ? Stakeholder: "StakeBased"
}

responder_role =
  "DRep" / "SPO" / "CC" / "Stakeholder"

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
  ? methodSchemaHash: hex_blake2b_256
}

survey_details = {
  specVersion: tstr,
  title: tstr,
  description: tstr,
  questions: [+ survey_question],
  roleWeighting: role_weighting,
  endEpoch: uint
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
  responderRole: responder_role,
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

### JSON Schema

This CIP also provides machine-readable JSON Schema files under [`./schemas`](./schemas):
- [`schemas/common.schema.json`](./schemas/common.schema.json)
- [`schemas/survey-details.schema.json`](./schemas/survey-details.schema.json)
- [`schemas/survey-response.schema.json`](./schemas/survey-response.schema.json)
- [`schemas/governance-action-anchor-survey-link.schema.json`](./schemas/governance-action-anchor-survey-link.schema.json)

Schema authority and scope:
- CDDL and normative prose in this document are authoritative.
- JSON Schema files are interoperability aids for shape validation and MUST be kept consistent with this specification.
- Cross-transaction and chain-state-dependent semantics (for example governance-link resolution, effective role-weighting derivation, role-membership checks, and stake snapshot/source logic) are normative in prose and test vectors, and are not fully representable in standard JSON Schema.

### Test Vectors

See [test-vector.md](./test-vector.md) for deterministic examples and canonical CBOR payload vectors.

### Versioning

This specification uses semantic versioning in `specVersion`.
This revision defines version `1.0.0`.

## Rationale: How does this CIP achieve its goals?

- Multi-question surveys let authors collect related signals (including mixed method types) in one survey object.
- Survey-level required and governance fields preserve shared end-epoch and role-weighting semantics across all included questions.
- Question-level method fields keep validation explicit and deterministic per question.
- Index-based option responses avoid text-matching ambiguity and improve interoperability.
- Binding responses and action links by `surveyTxId` keeps survey linkage deterministic and interoperable.
- Requiring explicit `roleWeighting` removes ambiguous defaults and forces clear tally intent per role domain.
- Governance-linked surveys can inherit governance voter-class constraints while still allowing surveys to narrow configured roles via intersection.
- Role-aware validation and per-role stake tallies reduce sybil and mixed-domain interpretation risks.
- `PledgeBased` adds an SPO-specific mode that uses live pledge instead of declared pledge for more defensible weighting.
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
- [ ] Implement and demonstrate end-to-end survey creation + response + tally in at least one toolchain.
- [ ] Document interoperability results and edge-case handling.

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
