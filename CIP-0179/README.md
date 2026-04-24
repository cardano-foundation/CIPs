---
CIP: 179
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

This proposal defines a standardized transaction metadata format for creating, responding to, and cancelling on-chain surveys and polls under metadata label `17`.

The format supports:
- One or more survey definitions per transaction.
- One or more survey responses per transaction.
- Five built-in question types (single-choice, multi-select, ranking, numeric-range, custom) via a tagged sum type.
- Optional linkage to governance actions via governance action anchor metadata.
- Deterministic response binding using a survey reference `(TxId, index)` pair.
- Survey cancellation by the original creator.

The standard is general-purpose and can be used for governance and non-governance sentiment gathering. It also defines an Info Action profile for tools that want strict behavior when a survey is attached to a governance Info Action.

## Motivation: Why is this CIP necessary?

Formal governance actions are intentionally constrained. Those constraints are useful for protocol safety, but they are not sufficient for many community workflows that need structured sentiment data. This is particularly true for Info Actions, which are limited in their ability to collect information from stakeholders.

Examples include:
- Polling candidate CIPs to decide hard-fork prioritization.
- Voting on a line item of a budget proposal.
- Gathering bounded numeric preferences (for example, initialization values for several related parameters).
- Ranking candidates or proposals by community preference.

Without a shared on-chain format, these workflows fragment across custom off-chain tools and incompatible schemas. This CIP provides a common metadata interface that wallets, explorers, governance dashboards, and indexers can implement consistently.

## Specification

### Overview

This CIP reserves metadata label `17` for three payload types:
- Survey definitions (tag `0`): one or more survey definitions.
- Survey responses (tag `1`): one or more survey responses.
- Survey cancellations (tag `2`): one or more survey cancellations.

A transaction MUST include at most one label `17` payload. The three payload types MUST NOT be mixed in a single transaction.

Survey metadata under label `17` is valid as a standalone mechanism and does not require any governance action.

A survey is identified by a `survey_ref`: the pair `(tx_id, survey_index)` where `tx_id` is the transaction containing the survey definitions payload and `survey_index` is the position of the definition within that payload's definitions array. This follows the Cardano convention used for UTxOs (`transaction_input`), governance actions (`gov_action_id`), and other on-chain references.

### Encoding Conventions

All map keys and enumeration values use integers for compact CBOR encoding, consistent with how the Cardano ledger encodes transaction bodies, certificates, and voting procedures.

Text fields that may exceed the 64-byte Cardano metadata text limit use chunked text: an array of text strings, each at most 64 bytes, concatenated to reconstruct the full value. This is the same approach used by CIP-20 for the `msg` field.

Transaction IDs and hashes use raw `bytes .size 32` rather than hex-encoded text strings, halving the per-hash cost.

### CDDL Schema

```cddl
; CIP-179 On-chain Surveys and Polls (version 1)
;
; Encoding principles:
;   - Integer keys and enum values for compact CBOR.
;   - Chunked text arrays for strings that may exceed 64 bytes.
;   - Raw bytes for hashes and transaction IDs.
;   - Sum types (tagged unions) for question and answer variants.
;   - (TxId, index) pairs for survey references.

; ---------- Primitives ----------

pos_uint = uint .gt 0
tx_id = bytes .size 32
blake2b_256 = bytes .size 32
chunked_text = [+ tstr]              ; each element <= 64 bytes
survey_ref = [tx_id, uint]           ; (TxId, index in definitions array)

; Standard Cardano transaction metadatum.
transaction_metadatum =
    { * transaction_metadatum => transaction_metadatum }
  / [ * transaction_metadatum ]
  / int
  / bytes .size (0..64)
  / text .size (0..64)

; ---------- Types reused from Conway ledger CDDL ----------
; Included for reference; authoritative definitions are in the ledger spec.

hash28 = bytes .size 28
addr_keyhash = hash28
script_hash = hash28

; A Cardano credential: key-based (tag 0) or script-based (tag 1).
credential = [0, addr_keyhash // 1, script_hash]

; ---------- Enumerations ----------

; Roles
;   0 = DRep
;   1 = SPO
;   2 = CC
;   3 = Stakeholder
role = 0 / 1 / 2 / 3

; Weighting modes
;   0 = CredentialBased
;   1 = StakeBased
;   2 = PledgeBased
weighting_mode = 0 / 1 / 2

; Role-to-weighting map. At least one entry required.
; Allowed pairings enforced by tooling:
;   DRep (0)        -> CredentialBased (0) | StakeBased (1)
;   SPO (1)         -> CredentialBased (0) | StakeBased (1) | PledgeBased (2)
;   CC (2)          -> CredentialBased (0)
;   Stakeholder (3) -> StakeBased (1)
role_weighting = { + role => weighting_mode }

; ---------- Numeric constraints ----------

numeric_constraints = [
  int,              ; minValue
  int,              ; maxValue (>= minValue)
  ? pos_uint        ; step (optional, must be > 0)
]

; ---------- Question types (tagged sum type) ----------

; Tag 0: Single-choice.
;   Exactly one option must be selected in the response.
;   Options array MUST contain at least 2 items.
single_choice_question = [0, chunked_text, [2* tstr]]

; Tag 1: Multi-select.
;   Between 0 and maxSelections options may be selected.
;   Options array MUST contain at least 2 items.
;   maxSelections MUST be >= 1 and <= len(options).
multi_select_question = [1, chunked_text, [2* tstr], pos_uint]

; Tag 2: Ranking.
;   Respondent ranks between 1 and maxRanked options in preference order.
;   Options array MUST contain at least 2 items.
;   maxRanked MUST be >= 1 and <= len(options).
ranking_question = [2, chunked_text, [2* tstr], pos_uint]

; Tag 3: Numeric-range.
;   Answer is an integer satisfying the constraints.
numeric_range_question = [3, chunked_text, numeric_constraints]

; Tag 4: Custom method.
;   Schema at methodSchemaUri defines answer format.
;   methodSchemaHash is blake2b-256 of raw bytes at that URI.
custom_question = [4, chunked_text, chunked_text, blake2b_256]

survey_question = single_choice_question
               / multi_select_question
               / ranking_question
               / numeric_range_question
               / custom_question

; ---------- Survey definition ----------

survey_definition = [
  uint,                        ; specVersion (this document = 1)
  chunked_text,                ; title
  chunked_text,                ; description
  [+ survey_question],         ; questions (at least one)
  role_weighting,              ; eligible roles and weighting modes
  uint                         ; endEpoch (inclusive cutoff)
]

; ---------- Answer types (tag matches question type) ----------

; Tag 0: Single-choice answer. Exactly 1 selected option index.
single_choice_answer = [0, uint, uint]

; Tag 1: Multi-select answer. 0 to maxSelections selected option indices.
multi_select_answer = [1, uint, [* uint]]

; Tag 2: Ranking answer. 1 to maxRanked option indices, most preferred first.
;   Indices MUST NOT contain duplicates.
ranking_answer = [2, uint, [+ uint]]

; Tag 3: Numeric-range answer.
numeric_answer = [3, uint, int]

; Tag 4: Custom answer.
custom_answer = [4, uint, transaction_metadatum]

; In all answer variants, the second element is the question index
; (position in the survey_definition's questions array).
answer_item = single_choice_answer
            / multi_select_answer
            / ranking_answer
            / numeric_answer
            / custom_answer

; ---------- Survey response ----------

; No specVersion: version is determined by the referenced survey.
survey_response = [
  survey_ref,                  ; reference to the survey definition
  role,                        ; claimed responder role
  [+ answer_item]              ; answers (at least one; partial allowed)
]

; ---------- Survey cancellation ----------

; Cancels a previously published survey.
; Transaction required_signers MUST include an addr_keyhash
; that was also in the original survey definition transaction's
; required_signers.
survey_cancellation = survey_ref

; ---------- Top-level payload under metadata label 17 ----------

cip_179_payload = [0, [+ survey_definition]]
               / [1, [+ survey_response]]
               / [2, [+ survey_cancellation]]
```

### Integer Encoding Reference

#### Roles

| Integer | Role |
|:--------|:-----|
| 0 | DRep |
| 1 | SPO |
| 2 | CC |
| 3 | Stakeholder |

#### Weighting modes

| Integer | Mode | Eligible roles |
|:--------|:-----|:---------------|
| 0 | CredentialBased | DRep, SPO, CC |
| 1 | StakeBased | DRep, SPO, Stakeholder |
| 2 | PledgeBased | SPO only |

#### Payload tags

| Tag | Payload type |
|:----|:-------------|
| 0 | Survey definitions |
| 1 | Survey responses |
| 2 | Survey cancellations |

#### Question and answer type tags

| Tag | Question type | Answer format |
|:----|:--------------|:--------------|
| 0 | Single-choice | `[0, qIdx, optionIndex]` |
| 1 | Multi-select | `[1, qIdx, [optionIndex*]]` |
| 2 | Ranking | `[2, qIdx, [optionIndex+]]` |
| 3 | Numeric-range | `[3, qIdx, intValue]` |
| 4 | Custom | `[4, qIdx, metadatum]` |

An answer's tag MUST match the tag of the referenced question.

### Survey Definition

A survey definition is a positional array:

```
[specVersion, title, description, questions, roleWeighting, endEpoch]
```

| Position | Type | Description |
|:---------|:-----|:------------|
| 0 | uint | Schema version. This document defines version `1`. |
| 1 | chunked_text | Human-readable survey title. |
| 2 | chunked_text | Human-readable survey context or rationale. |
| 3 | array | Survey questions. MUST contain at least one item. |
| 4 | role_weighting | Map from role to weighting mode. MUST contain at least one entry. |
| 5 | uint | Inclusive epoch cutoff for response validity and tally snapshot. |

Survey definition transactions SHOULD include the creator's `addr_keyhash` in `required_signers` to enable cancellation verification.

### Question Types

Questions use a tagged sum type. The first element is the type tag. All question types include a `chunked_text` question prompt as their second element.

#### Single-choice (tag 0)

```
[0, question_prompt, options]
```

- `options`: array of `tstr`, at least 2 items. Each option label MUST fit in a single 64-byte text value.
- Response MUST select exactly one option index.

#### Multi-select (tag 1)

```
[1, question_prompt, options, maxSelections]
```

- `options`: array of `tstr`, at least 2 items.
- `maxSelections`: positive integer, `>= 1` and `<= len(options)`.
- Response MUST select between 0 and `maxSelections` option indices (inclusive). An empty selection is valid and indicates no options selected.

#### Ranking (tag 2)

```
[2, question_prompt, options, maxRanked]
```

- `options`: array of `tstr`, at least 2 items.
- `maxRanked`: positive integer, `>= 1` and `<= len(options)`.
- Response MUST provide between 1 and `maxRanked` option indices in preference order (most preferred first). Indices MUST NOT contain duplicates. All indices MUST be valid positions in the options array.

#### Numeric-range (tag 3)

```
[3, question_prompt, [minValue, maxValue, ?step]]
```

- `minValue <= maxValue`.
- Optional `step` MUST be a positive integer (> 0). When present, the response value MUST satisfy `(value - minValue) mod step == 0`.
- Response MUST contain an integer satisfying range and step constraints.

#### Custom method (tag 4)

```
[4, question_prompt, methodSchemaUri, methodSchemaHash]
```

- `methodSchemaUri`: chunked text URI pointing to the method schema document.
- `methodSchemaHash`: blake2b-256 hash (`bytes .size 32`) of the raw bytes at that URI.
- Response uses `transaction_metadatum`, interpreted according to the referenced schema.

YES/NO/ABSTAIN semantics: this CIP does not reserve special option codes. Authors MAY express YES/NO/ABSTAIN by placing those labels in `options`.

### Survey Response

A survey response is a positional array:

```
[survey_ref, role, answers]
```

| Position | Type | Description |
|:---------|:-----|:------------|
| 0 | survey_ref | Reference to the survey: `[tx_id, survey_index]`. |
| 1 | role | Claimed responder role (integer). |
| 2 | array | Non-empty array of answer items. |

There is no `specVersion` in the response. The version is determined by the referenced survey definition.

Respondents MAY answer a subset of questions (partial responses are valid). Each question is tallied independently over responses that include an answer for that question. Question indices in the answers array MUST be unique within one response. Each answer's type tag MUST match the type tag of the referenced question.

A response transaction MUST NOT reference itself: the `tx_id` in `survey_ref` MUST differ from the response transaction's own id.

Multiple responses MAY be batched in a single transaction. Each is validated independently.

### Survey Cancellation

A cancellation payload contains one or more `survey_ref` values, each identifying a survey to cancel.

Validation:
- The `survey_ref` MUST resolve to a previously published survey definition.
- The cancellation transaction's `required_signers` MUST include an `addr_keyhash` that was also in the original survey definition transaction's `required_signers`.
- Once cancelled, tooling MUST treat the survey as inactive. Existing responses remain on-chain but MUST NOT be included in tallies.
- Cancellation does not invalidate the survey definition data itself; it signals that the survey should not be used.

### Responder Identity and Deduplication

Identity verification leverages Cardano's existing transaction-level mechanisms.

#### Response credential

The `response_credential` is a `credential` as defined in the Conway ledger CDDL (`[0, addr_keyhash]` for key-based or `[1, script_hash]` for script-based). It is not included in the survey response metadata; it is derived from chain data by tooling.

Derivation rules:
- **Standalone surveys**: `response_credential` is `[0, k]` where `k` is the `addr_keyhash` from the transaction body's `required_signers` (field 14) that matches a registered credential for the claimed role.
- **Governance-linked surveys**: `response_credential` is derived from the `voter` entry in the transaction body's `voting_procedures` (field 19), following the Conway `voter` type mapping:

| Conway `voter` tag | Role | Credential |
|:--------------------|:-----|:-----------|
| 0 (`addr_keyhash`) | CC (2) | `[0, addr_keyhash]` |
| 1 (`script_hash`) | CC (2) | `[1, script_hash]` |
| 2 (`addr_keyhash`) | DRep (0) | `[0, addr_keyhash]` |
| 3 (`script_hash`) | DRep (0) | `[1, script_hash]` |
| 4 (`addr_keyhash`) | SPO (1) | `[0, addr_keyhash]` |

The response transaction MUST include exactly one `addr_keyhash` in `required_signers` (standalone) or exactly one `voter` entry in `voting_procedures` (governance-linked) that matches the claimed role. When multiple candidates exist, the response is ambiguous and MUST be rejected.

#### Role validation

The claimed role MUST be validated against ledger state:

| Role | Ledger requirement |
|:-----|:-------------------|
| DRep (0) | `response_credential` MUST be a registered DRep credential. |
| SPO (1) | `response_credential` MUST be the cold credential of a registered pool operator. |
| CC (2) | `response_credential` MUST be the hot credential of an active Constitutional Committee member. |
| Stakeholder (3) | `response_credential` MUST be a stake credential with delegated stake. |

Tools MUST NOT trust role claims without validation. A response is invalid when the claimed role does not match ledger-derived role evidence.

A signer MAY submit separate responses for different roles, provided each role claim independently passes validation.

#### Validation phases

Validation runs in two phases:
1. **Response-time validation**: at response inclusion, verify credential proof and role membership.
2. **Tally-time re-verification**: at the survey's `endEpoch` snapshot, re-check role membership and credential eligibility.

Only responses that pass both phases are counted in tallies.

#### Deduplication

The identity tuple for deduplication is `(survey_ref, role, response_credential)`.

If multiple responses from the same tuple pass both validation phases, the latest valid response wins.

### Governance Action Linkage

Survey-to-action linkage is canonicalized as **Action -> Survey**. This linkage is optional and only applies when a governance action wants to attach a survey context.

When a governance action links to a survey, the governance action anchor metadata MUST include:

```json
{
  "specVersion": 1,
  "kind": "cardano-governance-survey-link",
  "surveyTxId": "<hex-encoded 32-byte transaction id>",
  "surveyIndex": 0
}
```

(The anchor metadata is an off-chain document; `surveyTxId` is hex-encoded per JSON convention.)

Validation rules:
- The `(surveyTxId, surveyIndex)` pair MUST resolve to a transaction that includes label `17` with a survey definitions payload, and the survey at the given index MUST exist.
- For linked surveys, `actionEligibility` MUST be derived from the linked governance action's voter classes.
- Tooling MUST derive the linked governance action id (`linkedActionId`) from the governance action that carries the survey-link anchor.
- `linkedRoleWeighting` is the intersection of the survey's `roleWeighting` keys with `actionEligibility`, preserving configured weighting modes for surviving roles.
- If `linkedRoleWeighting` is empty, the governance-action-to-survey link is invalid.
- Survey `endEpoch` MUST exactly match the governance action's active voting end epoch. If they differ, the link is invalid.
- If linkage validation fails, tooling MUST NOT attach that survey to the governance action.
- Linkage invalidity does not invalidate the survey as standalone metadata.

#### Linked survey response rules

For governance-linked surveys:
- Response transactions MUST include a `voting_procedures` entry.
- `voting_procedures` MUST contain exactly one voter entry, and that voter entry MUST contain exactly one `(gov_action_id, voting_procedure)` pair.
- The `gov_action_id` MUST equal `linkedActionId`. Otherwise the response is invalid.
- The claimed role MUST exist in `linkedRoleWeighting`.
- The role derived from the voter entry (per the voter tag mapping above) MUST match the claimed role.

### Epoch Semantics

- `endEpoch` is mandatory in every survey definition.
- `responseEpoch` is derived from the response transaction's inclusion slot via ledger epoch mapping.
- Responses with `responseEpoch > endEpoch` are invalid.
- Role-membership and credential eligibility checks are evaluated at response time and re-verified at tally time using the `endEpoch` snapshot.
- A response is counted only if it passes both response-time validation and `endEpoch` tally-time re-verification.
- For `StakeBased` and `PledgeBased` weighting modes, weight snapshots are taken at `endEpoch`.

### Duplicate and Ordering Semantics

For a given identity tuple `(survey_ref, role, response_credential)`:
- If multiple responses pass both validation phases, the latest valid response wins.
- Latest is determined by the chain ordering tuple `(slot, txIndexInBlock, responseIndex)`, where `responseIndex` is the position within the responses array in the label `17` payload.
- Latest-response semantics replace the full prior response for that tuple.

### Weighting Semantics

For each role key in `linkedRoleWeighting` (linked surveys) or `roleWeighting` (standalone surveys), one valid latest response per `(survey_ref, role, response_credential)` contributes to that role's tally.

- **CredentialBased** (0): weight is `1` per valid latest response. Transaction fees are the primary spam cost.
- **StakeBased** (1): weight is role-domain stake at the `endEpoch` snapshot:
  - DRep: governance voting power of `response_credential`.
  - SPO: active stake controlled by `response_credential` across mapped active registered pools.
  - Stakeholder: ADA stake controlled by `response_credential`.
- **PledgeBased** (2): SPO-only. Weight is the sum of live pledge over active registered pools mapped to `response_credential` at the `endEpoch` snapshot. Declared pledge MUST NOT be used. If `response_credential` maps to zero active registered pools at snapshot, the response remains valid and contributes weight `0`.

Canonical outputs MUST be per-role tallies. Tools MAY additionally publish merged/composite outputs only if:
- The output is explicitly labeled as non-canonical.
- Merge logic is disclosed alongside the output.
- Canonical per-role tallies remain available as primary outputs.

### Tool Output Requirements

- Tools MUST expose canonical per-role tallies as primary outputs whenever multiple roles are configured.
- Tools MUST NOT present merged/composite totals as canonical role results.
- Any merged/composite display MUST explicitly disclose its merge policy and weighting interpretation.
- Audit/export output MUST include role, `response_credential`, counted/excluded status, and exclusion reason when applicable.

### Transaction-level Constraints

- A single label `17` payload MUST contain exactly one of: definitions, responses, or cancellations.
- A response transaction MUST NOT reference itself.
- If governance-action linkage is provided, it MUST be encoded in governance action anchor metadata, not in the survey definition.

### CBOR Diagnostic Examples

#### Survey definition with ranking question

```cbor-diag
{17: [0, [                                    / tag 0 = definitions /
  [                                            / survey_definition /
    1,                                         / specVersion /
    ["Dijkstra hard-fork CIP shortlist"],      / title /
    ["Select candidate CIPs for potential",    / description (chunked) /
     " inclusion in the Dijkstra hard fork."],
    [                                          / questions /
      [1,                                      / multi-select (tag 1) /
        ["Which CIPs should be shortlisted",   / question prompt (chunked) /
         " for Dijkstra?"],
        ["CIP-0108", "CIP-0119",               / options /
         "CIP-0136", "CIP-0149"],
        4                                      / maxSelections /
      ],
      [2,                                      / ranking (tag 2) /
        ["Rank shortlisted CIPs by priority"], / question prompt /
        ["CIP-0108", "CIP-0119",               / options /
         "CIP-0136", "CIP-0149"],
        3                                      / maxRanked: rank top 3 /
      ]
    ],
    {0: 0},                                    / roleWeighting: DRep=CredentialBased /
    504                                        / endEpoch /
  ]
]]}
```

#### Survey response

```cbor-diag
{17: [1, [                                     / tag 1 = responses /
  [                                             / survey_response /
    [h'efefefef...ef', 0],                      / survey_ref: (TxId, index 0) /
    0,                                          / role: DRep /
    [                                           / answers /
      [1, 0, [1, 3]],                           / multi-select: q0, options 1 & 3 /
      [2, 1, [3, 1, 0]]                         / ranking: q1, prefer opt 3 > 1 > 0 /
    ]
  ]
]]}
```

#### Survey cancellation

```cbor-diag
{17: [2, [                                     / tag 2 = cancellations /
  [h'efefefef...ef', 0]                         / survey_ref to cancel /
]]}
```

### Block Explorer and dApp Implementation Guide

1. Discover survey definitions by scanning label `17` for payloads with tag `0`.
2. Discover cancellations (tag `2`) and mark cancelled surveys as inactive.
3. Optionally discover governance actions with anchor metadata carrying `kind = "cardano-governance-survey-link"`.
4. If present, validate governance-action-to-survey linkage by `(surveyTxId, surveyIndex)`, role compatibility, and exact `endEpoch` equality; derive `linkedActionId`.
5. Discover responses by scanning label `17` for payloads with tag `1`.
6. Resolve each response to its survey via `survey_ref`.
7. Reject responses to cancelled surveys.
8. Validate each answer against the corresponding question type and constraints.
9. Derive `response_credential` from `required_signers` (standalone) or `voting_procedures` (linked) and validate role membership against ledger state.
10. Filter responses by `responseEpoch <= endEpoch`.
11. At or after `endEpoch`, re-verify each response using `endEpoch` snapshot state; exclude failures.
12. Apply latest-valid-response-wins per `(survey_ref, role, response_credential)`.
13. Derive weights from `endEpoch` snapshot state per configured weighting mode.
14. Produce canonical per-role tallies.

## Rationale: How does this CIP achieve its goals?

The goal is a compact, deterministic, and interoperable on-chain survey format that integrates naturally with Cardano's existing infrastructure. Each design decision follows from that goal.

### Compact on-chain encoding

On-chain metadata is paid for per byte in transaction fees and stored permanently by every full node. The encoding follows the same conventions as the Cardano ledger CDDL: integer map keys, integer enum tags, and raw bytes for hashes. This avoids the overhead of text-based keys and values, which would multiply the cost of every survey definition and every response.

### Chunked text for human-readable fields

Cardano metadata limits individual text strings to 64 bytes. Survey titles, descriptions, and question prompts routinely exceed this limit. Chunked text arrays (as established by CIP-20) solve this while keeping option labels as plain `tstr` since they are typically short identifiers.

### Tagged sum types for questions and answers

Each question type (single-choice, multi-select, ranking, numeric-range, custom) has distinct required fields. A tagged sum type makes invalid combinations unrepresentable in the schema: a single-choice question cannot carry numeric constraints, and a numeric-range question cannot carry options. This moves validation from prose rules into the data model, reducing the burden on implementors.

### Survey references as (TxId, index)

On-chain artifacts in Cardano use `(TxId, index)` pairs for identification: UTxOs use `transaction_input = [transaction_id, index]`, governance actions use `gov_action_id = [transaction_id, gov_action_index]`. Survey references follow the same pattern, which enables batching multiple definitions in a single transaction and aligns with tooling that already handles this identification scheme.

### Batched definitions and responses

Multiple survey definitions or responses per transaction reduce the number of transactions needed, directly lowering fees for survey creators and active respondents.

### Survey cancellation

A survey with errors wastes respondent effort. A simple cancellation mechanism (referencing the survey and proving creator identity via `required_signers`) lets creators invalidate a broken survey without waiting for `endEpoch`.

### Identity via required_signers and voting_procedures

The Cardano ledger already enforces that `required_signers` entries (Conway `transaction_body` field 14) require a matching signature witness. For standalone surveys, including the responder's `addr_keyhash` in `required_signers` provides a ledger-level identity guarantee. For governance-linked surveys, the `voting_procedures` entry (field 19) serves the same purpose while simultaneously recording the governance vote. This eliminates the need for complex chain-evidence derivation rules.

### Multi-question surveys with partial responses

Grouping related questions in one survey avoids unnecessary proliferation of survey transactions while keeping shared constraints (`roleWeighting`, `endEpoch`) at the survey level. Allowing partial responses gives respondents flexibility; each question is tallied independently over the responses that include it.

### Latest-valid-response-wins

Participants may want to change their answer before `endEpoch`. Accepting the latest valid response per identity tuple provides a correction path while maintaining deterministic, reproducible tallies.

### Per-role canonical tallies

Different roles have different weighting units (credential count, stake, pledge). Mixing them in a single tally obscures interpretation. Canonical per-role tallies keep results clear; optional merged views are permitted only when explicitly labeled as non-canonical.

### Action -> Survey linkage direction

The governance action anchor references the survey (not the other way around). This avoids circular transaction dependencies: the survey is published first, then the governance action references it by `survey_ref`.

## Limitations and Future Extensions

### Optional vs required questions

Version 1 treats all questions as answerable at the respondent's discretion (partial responses are valid). A future version could add a required flag per question, allowing survey creators to enforce that responses include answers to certain questions.

### Script-based credentials for standalone surveys

The `required_signers` field in the Conway transaction body only supports `addr_keyhash` values (key hashes), not script hashes. This means script-based DReps, SPOs, CC members, or stakeholders cannot prove identity in standalone survey responses.

Governance-linked surveys do not have this limitation: the Conway `voter` type in `voting_procedures` supports both key-based (tags 0, 2, 4) and script-based (tags 1, 3) credentials.

A future version could define an alternative identity proof mechanism for script-based credentials in standalone surveys (for example, requiring a specific script witness or output pattern).

### Versioning granularity

Version 1 uses a single integer (`specVersion = 1`). If backward-compatible extensions prove necessary (adding optional fields, new question types), a more granular scheme (e.g., `[major, minor]`) could be adopted. For the scope of this standard, a single integer is sufficient: any breaking change would increment the version and define the new array layout.

## Path to Active

### Acceptance Criteria

- [ ] At least two independent tools can create survey definition payloads.
- [ ] At least two independent tools can ingest survey responses and produce matching tallies for shared test vectors.
- [ ] At least one governance-facing tool implements the Info Action profile.
- [x] Label `17` is registered in `CIP-0010/registry.json`.
- [ ] At least one cooperative test demonstrates cross-tool interoperability (survey created by one tool, tallied by another).

### Implementation Plan

- [ ] Finalize CIP text from PR review feedback.
- [ ] Publish reference test vectors and validation notes.
- [ ] Implement end-to-end survey creation + response + tally in at least one toolchain.
- [ ] Document interoperability results and edge-case handling.

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
