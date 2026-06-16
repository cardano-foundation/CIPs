---
CIP: 179
Title: On-Chain Surveys and Polls
Category: Metadata
Status: Proposed
Authors:
    - Thomas Lindseth <thomas.lindseth@intersectmbo.org>
    - Ryan Wiley <rian222@gmail.com>
    - Matthieu Pizenberg <matthieu.pizenberg@gmail.com>
Implementors: []
Discussions:
    - Original PR: https://github.com/cardano-foundation/CIPs/pull/1107
Created: 2025-10-28
License: CC-BY-4.0
---

## Abstract

This proposal defines a standardized transaction metadata format for creating, responding to, and cancelling on-chain surveys and polls under metadata label `17`.

The format supports:
- Batched survey definitions, responses, and cancellations (one or more per transaction).
- Seven question types. Six built-in (single-choice, multi-select, ranking, numeric-range, points-allocation, rating) plus a custom extension type, via a tagged sum type.
- Deterministic response binding using a survey reference `(TxId, index)` pair.
- Survey cancellation by the original creator.
- Public or sealed responses, the latter using timelock encryption (Drand `tlock`) for delayed reveal.
- Optional off-chain content anchors (URI + hash) for bulky presentation text, custom-method schemas, and voter rationales.
- Optional linkage to governance Info Actions via anchor metadata.
- Eligibility expressed as a set of roles; result weighting and aggregation are deliberately out of scope.

The standard is general-purpose: it serves governance and non-governance sentiment gathering alike.

## Motivation: Why is this CIP necessary?

Formal governance actions are intentionally constrained for protocol safety, leaving many community workflows without a way to collect structured sentiment data, Info Actions in particular. Examples: polling candidate CIPs for hard-fork prioritization, voting on a budget line item, gathering bounded numeric preferences (e.g. initialization values for related parameters), or ranking candidates.

Without a shared on-chain format, these workflows fragment across incompatible off-chain tools. This CIP provides a common metadata interface that wallets, explorers, governance dashboards, and indexers can implement consistently.

## Specification

### Overview

This CIP reserves metadata label `17` for three payload types: survey definitions (tag `0`), survey responses (tag `1`), and survey cancellations (tag `2`). A transaction MUST include at most one label `17` payload, containing exactly one of the three types. Label `17` metadata is a standalone mechanism; no governance action is required.

A survey is identified by a `survey_ref`: the pair `(tx_id, survey_index)`, where `tx_id` is the transaction carrying the definitions payload and `survey_index` is the definition's position in that payload's array. It’s the same `(TxId, index)` convention as UTxOs (`transaction_input`) and governance actions (`gov_action_id`).

### Encoding Conventions

- **Integers everywhere.** Map keys and enumeration values are integers, matching the ledger's CBOR conventions.
- **Maps on top, tagged arrays below.** The two top-level records, `survey_definition` and `survey_response`, are integer-keyed CBOR maps (the Conway `transaction_body` pattern): future optional fields can be added at new keys without renumbering, and decoders SHOULD ignore unrecognized keys (reserved for future versions). The discriminated unions below them (`survey_question`, `answer_item`, and nested structures) stay tagged positional arrays. They evolve by adding new tags, not new fields, so a map would only bloat them.
- **Deterministic maps.** Encoders MUST emit these maps with integer keys in ascending numeric order and no duplicates (RFC 8949 §4.2), keeping any hashing, equality, or deduplication over payloads unambiguous.
- **Chunked text.** Fields that may exceed Cardano's 64-byte metadata text limit are either a single `bounded_text` (when it fits) or an array of ≤64-byte strings concatenated to reconstruct the value, as in CIP-20. Implementations MUST accept both forms.
- **Raw bytes.** Transaction IDs and hashes are `bytes .size 32`, half the cost of hex-encoded text.
- **Off-chain anchors.** Bulky human-readable text MAY move off-chain behind a `content_anchor` (URI + `blake2b-256` hash); see [External Survey Definitions](#external-survey-definitions).
- **Naming.** Field names are documentation only. On the wire, fields are identified by position or integer key. On-chain names use `snake_case` (matching the Conway CDDL); off-chain JSON keys use `camelCase`.

### CDDL Schema

```cddl
; CIP-179 On-chain Surveys and Polls (version 4)

; ---------- Primitives ----------

pos_uint = uint .gt 0
tx_id = bytes .size 32
blake2b_256 = bytes .size 32
drand_chain_hash = bytes .size 32     ; Drand chain hash for tlock
bounded_text = text .size (0..64)     ; Cardano metadata text limit
chunked_text = bounded_text / [+ bounded_text]  ; single string or chunked array
survey_ref = [tx_id, uint .size 2]    ; (TxId, index in definitions array)

; A reference to off-chain content, tamper-evident via its hash. Used for:
; external survey presentation text, custom-method schemas, and voter rationales.
content_anchor = [
  chunked_text,   ; URI (e.g. ipfs://..., https://...)
  blake2b_256     ; blake2b-256 of the raw bytes at that URI
]

; Standard Cardano transaction metadatum.
transaction_metadatum =
    { * transaction_metadatum => transaction_metadatum }
  / [ * transaction_metadatum ]
  / int
  / bytes .size (0..64)
  / bounded_text

; ---------- Types reused from Conway ledger CDDL ----------
; Included for reference; authoritative definitions are in the ledger spec.

hash28 = bytes .size 28
addr_keyhash = hash28
script_hash = hash28

; A Cardano credential: key-based (tag 0) or script-based (tag 1).
credential = [0, addr_keyhash // 1, script_hash]

; ---------- Top-level payload under metadata label 17 ----------

cip_179_payload = [0, [+ survey_definition]]
                / [1, [+ survey_response]]
                / [2, [+ survey_cancellation]]

; ---------- Survey definition ----------

; Integer-keyed deterministic map; unknown keys reserved for future versions
; (see Encoding Conventions).
survey_definition = {
  0 => uint,                   ; spec_version (this document = 4)
  1 => credential,             ; owner (for cancellation authorization)
  2 => chunked_text,           ; title (MAY be empty in external-content mode)
  3 => chunked_text,           ; description (MAY be empty in external-content mode)
  4 => eligible_roles,         ; roles permitted to respond
  5 => uint,                   ; end_epoch (inclusive cutoff)
  6 => submission_mode,        ; how responses are submitted
  7 => [+ survey_question],    ; questions (at least one)
  ? 8 => content_anchor        ; OPTIONAL external presentation document
}

; ---------- Eligible roles ----------

; A role declares eligibility (which credential type may respond) and hints to
; UIs which key to present. It is NOT a weighting directive (see "Weighting and
; Aggregation (out of scope)").
;   0 = DRep
;   1 = SPO
;   2 = CC
;   3 = Stakeholder
;   4 = Owner          (control of a payment/spending credential)
role = 0 / 1 / 2 / 3 / 4

; Roles permitted to respond. Non-empty; entries SHOULD be unique.
eligible_roles = [+ role]

; ---------- Submission mode (tagged sum type) ----------

submission_mode = public_submission_mode / sealed_submission_mode

; Tag 0: Public. Responses carry plaintext answer items.
public_submission_mode = [0]

; Tag 1: Sealed. Responses carry a timelock-encrypted (Drand `tlock`) ciphertext
;   instead of plaintext answers. Answers are encrypted at submission and become
;   decryptable by anyone once `round` publishes on the pinned Drand chain. No
;   one, not even the survey owner, can open them earlier. This is delayed reveal,
;   not permanent secrecy. `padding_size` is the minimum plaintext byte length
;   each response is padded to before encryption.
sealed_submission_mode = [1, drand_chain_hash, pos_uint, pos_uint]
                      ;   chain_hash        round     padding_size

; ---------- Question types (tagged sum type) ----------

survey_question = custom_question
                / single_choice_question
                / multi_select_question
                / ranking_question
                / numeric_range_question
                / points_allocation_question
                / rating_question

; Tag 0 is reserved for the custom (extension) type, so new built-in types are
; appended at higher tags without ever disturbing it.
;
; Every question ends with an OPTIONAL `required` flag (bool, default false):
; when true, a response MUST NOT omit the question. Omission of a non-required
; question means abstain (see "Abstain semantics").

; Tag 0: Custom method. Answer format defined by the schema at the anchor.
custom_question = [0, chunked_text, content_anchor, ? bool]

; Tag 1: Single-choice. Exactly one option selected.
single_choice_question = [1, chunked_text, options_or_count, ? bool]

; Tag 2: Multi-select. Between min_selections and max_selections options.
;   0 <= min_selections <= max_selections <= number_of_options.
;   min_selections may be 0: a present, empty selection is a valid answer
;   ("none selected"), distinct from omitting the question (abstain).
multi_select_question = [2, chunked_text, options_or_count, uint, pos_uint, ? bool]
                     ;   tag  prompt        opts/count       min_sel  max_sel

; Tag 3: Ranking. Between min_ranked and max_ranked options, preference order.
;   1 <= min_ranked <= max_ranked <= number_of_options.
ranking_question = [3, chunked_text, options_or_count, pos_uint, pos_uint, ? bool]
                ;   tag  prompt        opts/count      min_ranked max_ranked

; Tag 4: Numeric-range. Answer is an integer satisfying the constraints.
numeric_range_question = [4, chunked_text, numeric_constraints, ? bool]

; Tag 5: Points-allocation. Distribute exactly `budget` points across options.
points_allocation_question = [5, chunked_text, options_or_count, pos_uint, ? bool]
                          ;   tag  prompt        opts/count       budget

; Tag 6: Rating. Rate options on the scale given by rating_scale.
rating_question = [6, chunked_text, options_or_count, rating_scale, ? bool]

; ---------- Rating scale ----------

; Numeric grid (array of ints), ordered worst-to-best label list (array of
; text), or, in external-content mode, a level count (bare uint >= 2); the
; three CBOR shapes are distinct. See "Rating (tag 6)".
rating_scale = numeric_constraints / options_or_count

; ---------- Numeric constraints ----------

numeric_constraints = [
  int,              ; min_value
  int,              ; max_value (>= min_value)
  ? pos_uint        ; step (optional, must be > 0)
]

; ---------- Options ----------

; Inline labels (>= 2) or, in external-content mode (survey_definition carries
; a content_anchor), an option count (>= 2). The CBOR shapes are distinct.
options          = [2* bounded_text]
option_count     = uint .ge 2
options_or_count = options / option_count

; ---------- Survey response ----------

; Integer-keyed deterministic map, like survey_definition; future optional
; fields (e.g. the deferred CIP-8 proof's signature material) get new keys.
; spec_version lets a response be decoded (answer encoding, public-vs-sealed
; shape) without first resolving the survey.
survey_response = {
  0 => uint,                   ; spec_version (this document = 4)
  1 => survey_ref,             ; reference to the survey definition
  2 => role,                   ; claimed responder role
  3 => credential,             ; responder's credential
  4 => response_answers,       ; answers (an omitted question = abstain)
  ? 5 => content_anchor        ; OPTIONAL voter rationale
}

; Response answers depend on the referenced survey's submission_mode:
;   - Public: an array of plaintext answer items.
;   - Sealed: a timelock-encrypted (Drand tlock) ciphertext (chunked bytes),
;     opaque until the survey's round publishes. Distinguished from the public
;     form by shape: byte string(s) rather than an array of answer-item arrays.
response_answers = [+ answer_item] / chunked_bytes

; Chunked byte blob: payloads exceeding the 64-byte metadata limit are split
; into an array of <=64-byte byte strings, concatenated to reconstruct.
chunked_bytes = (bytes .size (0..64)) / [+ bytes .size (0..64)]

; ---------- Answer types (tag matches question type) ----------

answer_item = custom_answer
            / single_choice_answer
            / multi_select_answer
            / ranking_answer
            / numeric_answer
            / points_allocation_answer
            / rating_answer

; In all answer variants, the second element is the question index
; (position in the survey_definition's questions array).

; Tag 0: Custom answer.
custom_answer = [0, uint, transaction_metadatum]

; Tag 1: Single-choice answer. Exactly 1 selected option index.
single_choice_answer = [1, uint, uint]

; Tag 2: Multi-select answer. min_selections..max_selections unique, valid
;   option indices. MAY be empty when min_selections is 0 ("none selected").
multi_select_answer = [2, uint, [* uint]]

; Tag 3: Ranking answer. min_ranked..max_ranked unique, valid option indices,
;   most preferred first.
ranking_answer = [3, uint, [+ uint]]

; Tag 4: Numeric-range answer.
numeric_answer = [4, uint, int]

; Tag 5: Points-allocation answer. (option_index, points) pairs.
;   points >= 0; option indices unique; unlisted options receive 0;
;   sum of points MUST equal `budget`.
points_allocation_answer = [5, uint, [+ [uint, uint]]]

; Tag 6: Rating answer. (option_index, rating) pairs.
;   rating MUST satisfy the rating scale; option indices unique.
rating_answer = [6, uint, [+ [uint, int]]]

; ---------- Survey cancellation ----------

; Cancels a previously published survey. The cancellation transaction MUST
; prove ownership of the survey definition's owner credential.
survey_cancellation = survey_ref
```

### Method Identifier Registry

Built-in question types are identified on-chain solely by their integer tag. For interoperability with tools and standards that name methods with strings/URNs, each tag has a documented URN alias. **These URNs never appear in metadata**. They are a documentation/registry cross-walk, suitable for mirroring into the CIP-10 registry. The one place a URN legitimately appears in data is the `custom` type's `content_anchor` URI, which MAY name an external method schema.

| Tag | CIP-179 type | Interop URN |
|:----|:-------------|:------------|
| 0 | Custom | (per-method, via the anchor URI) |
| 1 | Single-choice | `urn:cardano:poll-method:single-choice:v2` |
| 2 | Multi-select | `urn:cardano:poll-method:multi-select:v2` |
| 3 | Ranking | `urn:cardano:poll-method:ranking:v1` |
| 4 | Numeric-range | `urn:cardano:poll-method:numeric-range:v2` |
| 5 | Points-allocation | `urn:cardano:poll-method:points-allocation:v1` |
| 6 | Rating | `urn:cardano:poll-method:rating:v1` |

**URN versioning.** The suffix versions a method's *semantic contract*, not this CIP's document version, and bumps only on incompatible answer-semantics changes. `single-choice`, `multi-select`, and `numeric-range` are at `:v2` because their `:v1` (CIP-179 v1's string-based encoding) is materially redefined here (CBOR-first encoding, abstain-by-omission, meaningful empty multi-select). The other three begin at `:v1` as first definitions under this namespace. The correspondence with CIP-191 (Ekklesia) method names, which reference the `:v1` URNs, is tabulated in [CIP-179 vs CIP-191](./cip-179-vs-cip-191.md).

### Survey Definition

A survey definition is an integer-keyed CBOR map (deterministically encoded; see [Encoding Conventions](#encoding-conventions)). Keys 0–7 are mandatory, key 8 optional:

| Key | Type | Description |
|:----|:-----|:------------|
| 0 | uint | Schema version. This document defines version `4`. |
| 1 | credential | Survey owner; authorizes cancellation. |
| 2 | chunked_text | Survey title. MAY be empty in external-content mode. |
| 3 | chunked_text | Survey context or rationale. MAY be empty in external-content mode. |
| 4 | eligible_roles | Non-empty set of roles permitted to respond. |
| 5 | uint | `end_epoch`: inclusive cutoff for response validity and tally snapshot reference. |
| 6 | submission_mode | `[0]` public, or `[1, chain_hash, round, padding_size]` sealed (timelock). |
| 7 | array | Survey questions (at least one). |
| 8 | content_anchor | OPTIONAL external presentation document; its presence signals external-content mode. |

The definition transaction MUST prove ownership of the `owner` credential: key-based via `required_signers`, native-script via script satisfaction (mechanism A of [Credential proof](#credential-proof); mechanism B applies only to responses). A Plutus-script `owner` therefore has no proof path, so owners SHOULD use key-based or native-script credentials.

### Question Types

Every question is a tagged array: type tag, then a `chunked_text` prompt, then type-specific fields, then an OPTIONAL trailing `required` flag (default `false`; when `true`, a response MUST NOT omit the question; see [Abstain semantics](#abstain-semantics)).

Option-bearing questions (all but custom and numeric-range) carry an `options_or_count`: an inline array of at least 2 `bounded_text` labels, or, in external-content mode, a `uint >= 2` option count with labels supplied by the external document.

#### Custom (tag 0)

```
[0, question_prompt, content_anchor, ?required]
```

- `content_anchor`: `[method_schema_uri, method_schema_hash]`, the `blake2b-256` of the raw bytes at the URI.
- Response: a `transaction_metadatum`, interpreted per the referenced schema.

#### Single-choice (tag 1)

```
[1, question_prompt, options_or_count, ?required]
```

- Response: exactly one valid option index.

#### Multi-select (tag 2)

```
[2, question_prompt, options_or_count, min_selections, max_selections, ?required]
```

- `0 <= min_selections <= max_selections <= number_of_options`, `max_selections >= 1`.
- Response: between `min_selections` and `max_selections` unique, valid option indices.
- When `min_selections = 0`, a **present but empty** selection (`[2, q_idx, []]`) is a valid answer meaning "none selected" (e.g. "which of these do you deem acceptable?" — none). It is distinct from omitting the question (abstain). When `min_selections >= 1`, the only way to not answer is to omit the question.

#### Ranking (tag 3)

```
[3, question_prompt, options_or_count, min_ranked, max_ranked, ?required]
```

- `1 <= min_ranked <= max_ranked <= number_of_options`.
- Response: between `min_ranked` and `max_ranked` unique, valid option indices, most preferred first.

#### Numeric-range (tag 4)

```
[4, question_prompt, [min_value, max_value, ?step], ?required]
```

- `min_value <= max_value`; optional `step` is a positive integer.
- Response: an integer in range; when `step` is present, `(value - min_value) mod step == 0`.

#### Points-allocation (tag 5)

```
[5, question_prompt, options_or_count, budget, ?required]
```

- `budget`: positive integer, the total points to distribute.
- Response: `(option_index, points)` pairs with `points >= 0`, option indices unique and valid, points summing exactly to `budget`. Unlisted options receive `0`.

#### Rating (tag 6)

```
[6, question_prompt, options_or_count, rating_scale, ?required]
```

- `rating_scale` is either a `numeric_constraints` grid `[min_rating, max_rating, ?step]` presented as numbers (e.g. a 1–5 Likert scale), or an ordered list of at least 2 level labels from worst to best (e.g. `["bad", "average", "good"]`) presented as text. In external-content mode the labels MAY be a level count (`uint >= 2`).
- The rating in a response is always an integer, a value on the grid, or the 0-based label index (`0 = "bad"`), keeping tallies numeric regardless of presentation.
- Response: `(option_index, rating)` pairs, each rating valid for the scale, option indices unique and valid. A respondent MAY rate a subset of options.

### Abstain semantics

A response MAY answer a subset of questions; **a question with no answer item counts as an abstain on that question** within that response. Abstention is thus the default, costs zero bytes, and needs no dedicated encoding.

- Each question is tallied independently; tools SHOULD report abstain counts alongside per-option tallies.
- A respondent who never submits any response is a non-participant, not an abstainer.
- A response omitting a `required = true` question is invalid as a whole and MUST NOT be tallied.
- Authors who want abstain as a *selectable, counted* option MAY add an explicit "Abstain" label to an option-based question.
- Omission (abstain) differs from a present, empty multi-select answer ("none selected", valid when `min_selections = 0`), which is a deliberate, tallied answer.

### Survey Response

A survey response is an integer-keyed CBOR map (deterministically encoded; see [Encoding Conventions](#encoding-conventions)). Keys 0–4 are mandatory, key 5 optional:

| Key | Type | Description |
|:----|:-----|:------------|
| 0 | uint | Schema version; MUST match the referenced survey's. Lets a response be decoded (answer encoding, public-vs-sealed shape) without resolving the survey. |
| 1 | survey_ref | `[tx_id, survey_index]` of the survey. MUST NOT reference the response's own transaction. |
| 2 | role | Claimed responder role (integer). |
| 3 | credential | Responder's credential: `[0, addr_keyhash]` or `[1, script_hash]`. |
| 4 | response_answers | Plaintext answer items (public survey), or a chunked-bytes tlock ciphertext (sealed survey). |
| 5 | content_anchor | OPTIONAL voter rationale: an off-chain document explaining the choices, tamper-evident via its hash, mirroring governance rationale conventions (CIP-100 / CIP-108). Purely informational; no effect on validation or tallies. |

Question indices in the answers array MUST be unique, and each answer's type tag MUST match the referenced question's tag. Omitted questions are abstains ([Abstain semantics](#abstain-semantics)).

Multiple responses MAY be batched in one transaction; each is validated independently.

### Survey Cancellation

A cancellation payload contains one or more `survey_ref` values. Each MUST resolve to a previously published survey definition, and the cancellation transaction MUST prove ownership of that definition's `owner` credential (same rules as for definition transactions). A cancellation submitted after the survey's `end_epoch` is invalid.

A cancelled survey is inactive as a whole: tooling MUST NOT tally any of its responses. The definition data remains on-chain; cancellation only signals that the survey should not be used.

### External Survey Definitions

In large surveys most bytes are human-readable text. A definition carrying a `content_anchor` (key 8, "external-content mode") MAY move that text off-chain:

- `title`, `description`, and question prompts MAY be empty strings.
- Option-bearing questions MAY use the `option_count` form instead of inline labels.
- Everything validation-relevant, question count, type tags, all constraints, `eligible_roles`, `end_epoch`, `owner`, `submission_mode`, stays on-chain.

The anchored document supplies the missing presentation text: at minimum a title, description, and, per question in definition order, a prompt and option labels in option-index order. Its `blake2b-256` hash MUST equal the anchor hash (tamper-evidence).

For generic web rendering, publishers SHOULD use the JSON profile below (schema: `schemas/external-survey-presentation.schema.json`). Tools SHOULD ignore unrecognized fields.

```json
{
  "specVersion": 4,
  "kind": "cardano-survey-presentation",
  "title": "Dijkstra budget allocation",
  "description": "Allocate priority points across proposed work streams.",
  "questions": [
    {
      "prompt": "Allocate 100 points across these work streams.",
      "options": [
        "Ledger simplification",
        "Governance UX",
        "Committee tooling",
        "Developer experience"
      ]
    }
  ]
}
```

The `questions` array is in survey-definition order. `options`, when present, is in option-index order. Rating questions whose on-chain `rating_scale` is a level count SHOULD use `ratingLabels` in rating-index order.

Because answers reference option *indices* and every constraint is on-chain, responses are validated and tallied entirely from on-chain data; if the off-chain document is unavailable, only labels cannot be rendered. The on-chain structure is never replaced by a bare reference, so a survey is never uninterpretable for protocol purposes.

### Responder Identity and Deduplication

Identity verification uses Cardano's existing transaction-level mechanisms: the response names its `credential`, and the transaction proves control of it.

#### Credential proof

Control of the response `credential` MUST be proven by **at least one** of two alternative mechanisms:

**Mechanism A: `required_signers` (standalone or linked):**
- **Key-based** `[0, addr_keyhash]`: the `addr_keyhash` MUST be in the transaction body's `required_signers` (field 14); the ledger enforces the corresponding signature witness.
- **Native-script** `[1, script_hash]`: tooling MUST resolve the script (via chain indexing) and verify the transaction's `required_signers` satisfy it.
- **Plutus-script** `[1, script_hash]`: not provable this way, a Plutus script needs a redeemer, and metadata has no redeemer tag.

**Mechanism B: governance-vote binding (governance-linked surveys only):** the transaction carries a `voting_procedures` entry whose voter credential equals the response `credential` and votes on `linked_action_id`. The ledger already enforced that voter's witness (key witness, native-script satisfaction, or Plutus redeemer evaluation) when accepting the vote, so the binding **is** the credential proof on its own. The credential need not also appear in `required_signers`. B is the *only* mechanism for Plutus-script credentials ([Plutus script credentials](#plutus-script-credentials)); for the rest it is optional, additionally tying the response to an on-chain governance vote. B's cross-checks are in [Linked survey response rules](#linked-survey-response-rules).

#### Role validation

The claimed role MUST be validated against ledger state; tools MUST NOT trust unvalidated role claims.

| Role | Ledger requirement |
|:-----|:-------------------|
| DRep (0) | Registered DRep credential. |
| SPO (1) | Cold credential of a registered pool operator. |
| CC (2) | Hot credential of an active Constitutional Committee member. |
| Stakeholder (3) | Stake credential with delegated stake. |
| Owner (4) | Payment/spending credential. Further eligibility (e.g. NFT ownership) is enforced off-chain. |

A signer MAY submit separate responses for different roles, provided each role claim independently passes validation.

> **SPO via calidus (open).** Letting SPOs prove the SPO role with a CIP-151 calidus hot key instead of the cold credential likely depends on the CIP-8 proof design pass ([Limitations and Future Extensions](#limitations-and-future-extensions)). Until then, the cold-credential path is the defined one.

#### Validation phases

1. **Response time**: at inclusion, verify credential proof and role membership.
2. **Tally time**: at the `end_epoch` snapshot, re-verify role membership and credential eligibility.

Only responses passing both phases are tallied.

#### Deduplication

The identity tuple is `(survey_ref, role, credential)`. When multiple responses from one tuple pass both phases, the latest valid response wins, replacing the prior response in full. "Latest" follows chain order `(slot, tx_index_in_block, response_index)`, where `response_index` is the position in the payload's responses array.

### Governance Action Linkage

Linkage is canonicalized as **Action → Survey** and restricted to **Info Actions**, which is the only governance action type guaranteed to run its full validity period without on-chain side effects.

Linkage is a **discovery/advertisement** relationship plus an **epoch-alignment** invariant. It does **not** restrict who may respond: every role in `eligible_roles` participates exactly as it would standalone, and casting a governance vote on the linked action is an *optional* enrichment, not a precondition ([Linked survey response rules](#linked-survey-response-rules)).

An Info Action linking to a survey MUST include in its anchor metadata (an off-chain JSON document; `surveyTxId` hex-encoded per JSON convention):

```json
{
  "specVersion": 4,
  "kind": "cardano-governance-survey-link",
  "surveyTxId": "<hex-encoded 32-byte transaction id>",
  "surveyIndex": 0
}
```

Validation rules:
- The action MUST be an Info Action; linkage to any other action type is invalid.
- `(surveyTxId, surveyIndex)` MUST resolve to an existing survey definition under label `17`.
- Tooling MUST derive `linked_action_id` from the Info Action carrying the anchor.
- Survey `end_epoch` MUST exactly equal the Info Action's voting end epoch.
- If linkage validation fails, tooling MUST NOT attach the survey to the Info Action; the survey remains valid standalone.

#### Conway voter tag to CIP-179 role mapping

| Conway voter tag | Conway meaning | CIP-179 role |
|:-----------------|:---------------|:-------------|
| 0 | CC hot key credential | CC (2) |
| 1 | CC hot script credential | CC (2) |
| 2 | DRep key credential | DRep (0) |
| 3 | DRep script credential | DRep (0) |
| 4 | SPO pool cold key credential | SPO (1) |

#### Linked survey response rules

A linked response is validated exactly like a standalone one, credential proof plus role validation, and MUST be accepted on that basis alone; it is **not** required to carry a `voting_procedures` entry.

A response MAY additionally **bind** itself to the linked governance vote with a `voting_procedures` entry, which is the only mechanism supporting Plutus-script credentials. When present:
- It MUST contain a voter entry whose credential matches the response `credential`.
- That entry MUST vote on `linked_action_id`.
- The role derived from the voter tag (mapping above) MUST match the claimed role, necessarily one of `{DRep, SPO, CC}`, the roles with a Conway voter type; Stakeholder and Owner cannot use the binding.

A binding passing these checks satisfies credential proof on its own (mechanism B). A present-but-failing binding invalidates the response; an absent binding is not a failure.

### Epoch Semantics

- `end_epoch` MUST be greater than the current epoch when the definition transaction is included.
- `response_epoch` is derived from the response transaction's inclusion slot; responses with `response_epoch > end_epoch` are invalid.
- `end_epoch` is the snapshot epoch for tally-time re-verification ([Validation phases](#validation-phases)) and the canonical snapshot reference for any downstream weighting/aggregation.

### Weighting and Aggregation (out of scope)

This CIP records *who responded, in what role, with what selection*. Every valid response is one recorded response. How recorded selections are weighted or aggregated into an outcome (one-per-credential, by stake, by pledge, quadratic, Borda, …) is decided by the consumer of the recorded vote set, outside this CIP. Weighting changes nothing the respondent signs, only result interpretation; keeping it out of scope lets the same recorded set be re-tallied under any rule and avoids baking an inevitably incomplete enumeration of modes into the format. `role` is an eligibility/UI hint, never a weighting mode.

### Tool Output Requirements

- Tools SHOULD expose per-role participation tallies (with per-question abstain counts) as primary outputs whenever multiple roles are eligible.
- Tools MUST NOT present a weighted or merged total as produced or sanctioned by this CIP; downstream weighting MUST disclose its policy and snapshot basis.
- Audit/export output SHOULD include role, `credential`, counted/excluded status, and exclusion reason.
- A canonical tally interchange format is deferred; see [Limitations and Future Extensions](#limitations-and-future-extensions).

### CBOR Diagnostic Examples

#### Survey definition with multi-select and ranking questions

```cbor-diag
{17: [0, [                                      / tag 0 = definitions /
  {                                             / survey_definition (map) /
    0: 4,                                       / spec_version /
    1: [0, h'cdcdcdcd...cd'],                   / owner: key-based /
    2: "Dijkstra hard-fork CIP shortlist",      / title (fits in 64 bytes) /
    3: ["Select candidate CIPs for potential",  / description (chunked) /
        " inclusion in the Dijkstra hard fork."],
    4: [0],                                     / eligible_roles: DRep /
    5: 504,                                     / end_epoch /
    6: [0],                                     / submission_mode: public /
    7: [                                        / questions /
      [2,                                       / multi-select (tag 2) /
        ["Which CIPs should be shortlisted",    / prompt (chunked) /
         " for Dijkstra?"],
        ["CIP-0108", "CIP-0119",                / options /
         "CIP-0136", "CIP-0149"],
        1,                                      / min_selections /
        4                                       / max_selections /
      ],
      [3,                                       / ranking (tag 3) /
        "Rank shortlisted CIPs by priority",    / prompt (fits in 64 bytes) /
        ["CIP-0108", "CIP-0119",                / options /
         "CIP-0136", "CIP-0149"],
        1,                                      / min_ranked /
        3                                       / max_ranked: rank up to top 3 /
      ]
    ]
  }
]]}
```

#### Survey definition in external-content mode with a points-allocation question

```cbor-diag
{17: [0, [                                      / tag 0 = definitions /
  {                                             / survey_definition (map) /
    0: 4,                                       / spec_version /
    1: [0, h'cdcdcdcd...cd'],                   / owner /
    2: "",                                      / title empty (external) /
    3: "",                                      / description empty (external) /
    4: [0, 1, 3],                               / eligible_roles: DRep, SPO, Stakeholder /
    5: 612,                                     / end_epoch /
    6: [0],                                     / submission_mode: public /
    7: [
      [5,                                       / points-allocation (tag 5) /
        "",                                     / prompt empty (external) /
        4,                                      / option_count = 4 (labels off-chain) /
        100                                     / budget = 100 points /
      ]
    ],
    8: [ "ipfs://bafy...survey", h'aaaa...aa' ] / content_anchor: external text + hash /
  }
]]}
```

#### Survey response

```cbor-diag
{17: [1, [                                         / tag 1 = responses /
  {                                                / survey_response (map) /
    0: 4,                                          / spec_version /
    1: [h'efefefef...ef', 0],                      / survey_ref: (TxId, index 0) /
    2: 0,                                          / role: DRep /
    3: [0, h'abababab...ab'],                      / credential: key-based /
    4: [                                           / answers /
      [2, 0, [1, 3]],                              / multi-select: q0, options 1 & 3 /
      [3, 1, [3, 1, 0]]                            / ranking: q1, prefer opt 3 > 1 > 0 /
    ],
    5: [ "ipfs://bafy...rationale", h'bbbb...bb' ] / optional voter rationale /
  }
]]}
```

(Had the q0 answer been omitted, it would count as an abstain on q0.)

#### Survey cancellation

```cbor-diag
{17: [2, [                               / tag 2 = cancellations /
  [h'efefefef...ef', 0]                  / survey_ref to cancel /
]]}
```

### Block Explorer and dApp Implementation Guide

1. Discover survey definitions by scanning label `17` for payloads with tag `0`.
2. Discover cancellations (tag `2`) and mark cancelled surveys as inactive.
3. Optionally discover Info Actions whose anchor metadata carries `kind = "cardano-governance-survey-link"`.
4. If present, validate that the action is an Info Action, resolve `(surveyTxId, surveyIndex)`, check exact `end_epoch` equality, and derive `linked_action_id`. (Linkage does not restrict which roles may respond.)
5. Discover responses (tag `1`) and resolve each to its survey via `survey_ref`.
6. Reject responses to cancelled surveys.
7. Validate each answer against its question's type and constraints; treat questions without an answer item as abstains (reject the whole response if a `required` question is omitted).
8. Verify each response's `credential` by either mechanism of [Credential proof](#credential-proof): (A) `required_signers` or (B) a ledger-validated `voting_procedures` binding (sufficient alone; the only path for Plutus-script credentials). When a binding is present, cross-check the Conway voter tag against the claimed role. Then validate role membership against ledger state.
9. Filter responses by `response_epoch <= end_epoch`.
10. At or after `end_epoch`, re-verify each response against snapshot state; exclude failures.
11. Apply latest-valid-response-wins per `(survey_ref, role, credential)`.
12. Produce per-role participation tallies and per-question abstain counts; weighting/aggregation is downstream and out of scope.
13. If the definition carries a `content_anchor`, fetch and hash-verify the external document to render presentation text; validation and tallying do not depend on it.

## Rationale: How does this CIP achieve its goals?

The goal is a compact, deterministic, interoperable on-chain survey format that integrates naturally with existing Cardano infrastructure.

### Compact encoding, chunked text

Metadata is paid per byte and stored forever, so the encoding mirrors the ledger CDDL: integer keys, integer tags, raw byte hashes, avoiding the multiplied cost of text-based keys. Titles, descriptions, and prompts may exceed the 64-byte metadata text limit and therefore use chunked text (CIP-20 style); option labels stay plain `bounded_text` since they are typically short.

### Tagged sum types; custom type at tag 0

Each question type has distinct required fields; a tagged sum type makes invalid combinations unrepresentable (a single-choice question cannot carry numeric constraints), moving validation from prose into the data model. The custom (extension) type sits at the fixed tag `0` so appending built-in types at higher tags never disturbs the extension point. Points-allocation and rating earn their own tags because budget distribution and discrete rating scales are common polling needs the option-only types cannot express, keeping the method space aligned with other polling standards ([CIP-179 vs CIP-191](./cip-179-vs-cip-191.md)).

### Abstain by omission

Abstention is the most common non-answer, so it gets the zero-byte encoding; `required` lets authors force an explicit answer, and an explicit "Abstain" option remains available when authors want it counted as a selection.

### Off-chain content anchors

One `content_anchor` primitive (URI + `blake2b-256` hash) serves external presentation text, custom-method schemas, and voter rationales: small on-chain footprint, tamper-evident, and, for definitions, full on-chain validation and tally determinism are preserved because only presentation text moves off-chain.

### (TxId, index) references and batching

Survey references reuse the identification pattern of UTxOs and governance actions, which existing tooling already handles, and allow several definitions or responses per transaction, for fewer transactions, lower fees.

### Survey cancellation

A broken survey wastes respondent effort; cancellation (referencing the survey, proving the explicit `owner` credential) invalidates it without waiting for `end_epoch`.

### Explicit credential in response

Naming the responder's `credential` in the response removes ambiguity about which signer is the responder and supports native multisig in standalone surveys; verification rides on `required_signers` (or, when linked, `voting_procedures`).

### Multi-question surveys, partial responses, latest-wins

Grouping related questions in one survey shares the definition-level constraints (`eligible_roles`, `end_epoch`) and avoids transaction proliferation; partial responses cost respondents nothing since omissions are abstains tallied per question. Latest-valid-response-wins gives respondents a correction path before `end_epoch` while keeping tallies deterministic.

### Eligibility as a role set, weighting out of scope

*Who may respond* (eligibility, which affects validation) and *how results are interpreted* (weighting, which affects nothing the respondent signs) are separable concerns. Pairing each role with a weighting mode would conflate them, and any enumeration of modes (`CredentialBased` / `StakeBased` / `PledgeBased`, …) is inherently incomplete: it cannot express schemes such as quadratic voting. A plain role set keeps the definition honest about what the chain enforces, still gives UIs a key-selection hint, and lets any weighting scheme be applied downstream to the same recorded set.

### Info Action linkage

Only Info Actions are guaranteed to complete their validity period without on-chain side effects. The action references the survey (not vice versa), avoiding circular dependencies: survey first, then the Info Action points at it.

Linkage is discovery plus epoch alignment, not an eligibility gate: an Info Action linking a survey advertises it, which should widen reach, not narrow it. Requiring linked responses to carry a governance vote would make the vote the proof mechanism and silently exclude the two roles without a Conway voter type (Stakeholder, Owner); since standalone credential proof and role validation already cover every role, the vote binding is optional. It exists at all because it is the only mechanism yielding ledger-evaluated verification of Plutus-script credentials, which `required_signers` cannot provide.

### Limitations and Future Extensions

### CIP-8 message-signing proof (and calidus support)

`required_signers` is ledger-enforced and simple, but only covers credentials that sign *transactions*. It cannot serve message-signing credential types, notably CIP-151 calidus hot keys, which would let SPOs respond without their cold credential. An optional CIP-8 (`COSE_Sign1`) proof mode would cover them and also allow third parties to batch-submit message-signed responses. Specifying it requires a design pass on: the signed payload (binding at least `survey_ref` against cross-survey replay, plus a per-response nonce), where the signature and recovered key live in the response, within-survey replay handling (the `(survey_ref, role, credential)` dedup helps), and how batched submission appears in the label `17` payload.

### Canonical tally interchange format

Tallies are derived independently from on-chain data and no tally artifact is committed, so no rigid normative schema is needed. Still, a *recommended, non-normative* interchange shape for per-method tallies (option counts, numeric distributions, ranking first-preferences and pairwise matrices, points and rating aggregates, per-role and abstain breakdowns) would help independent tools confirm matching results on shared test vectors. Deferred to its own pass.

### Plutus script credentials

Key-based and native-script credentials are provable via `required_signers` in any survey. Plutus-script credentials are not. They need a redeemer, and metadata has none. So their only path is the optional governance-vote binding of a linked survey: Conway voters include Plutus script voters (tags 1 and 3), and the ledger evaluates the voting redeemer. This is the concrete reason the optional binding exists even though linkage itself is pure discovery. There is **no standalone path** for Plutus-script credentials today; a future version could define one.

## Versioning

### Version granularity

A single integer `spec_version` suffices: the integer-keyed top-level maps already absorb backward-compatible additions (new optional field at a new key; decoders ignore unrecognized keys), and any breaking change increments the version and defines the new layout. A finer scheme (e.g. `[major, minor]`) could be adopted if needed.

### Version history

Version 2 (breaking, over v1): integer keys and enum values replace string-based encoding (64-byte text limit, per-byte cost); ranking question type added; `(TxId, index)` survey references enable batching; cancellation payload added; credential proof moves from explicit hex inclusion to `required_signers` / native-script satisfaction.

Version 3 (breaking, over v2): `submission_mode` added to `survey_definition` (`[0]` public, `[1, chain_hash, round, padding_size]` sealed), enabling sealed responses via timelock encryption (Drand `tlock`), delayed reveal, not permanent secrecy; definition fields reordered so the variable-length `questions` array comes last; `spec_version` restored as the first element of `survey_response`.

Version 4 (breaking, over v3):
- **Question tags renumbered; custom moves to tag 0** (stable extension point; built-ins follow at 1–6).
- **Two new question types:** `points_allocation` (tag 5) and `rating` (tag 6, numeric grid or ordered text labels, always integer-encoded).
- **`min` constraints added** to multi-select (`min_selections`, may be `0`: a present empty selection is a counted "none selected") and ranking (`min_ranked >= 1`).
- **Per-question `required` flag** (optional trailing bool, default false) forcing an explicit answer.
- **Abstain by omission**: an answerless question is an abstain; present empty multi-select answers are valid only when `min_selections = 0` and mean "none selected".
- **`role_weighting` → `eligible_roles`; weighting modes removed** (purely interpretive, inexpressive enumeration, same set re-talliable under any rule); new `Owner` role added.
- **`content_anchor` primitive** introduced for external presentation text, custom-method schemas, and voter rationales.
- **Method Identifier Registry** added (URNs off-chain only); `single-choice`/`multi-select`/`numeric-range` URNs bumped to `:v2`, the rest start at `:v1`.
- **Top-level records become integer-keyed maps** (Conway `transaction_body` pattern) for renumbering-free future fields; nested tagged unions stay positional.
- **Governance linkage decoupled from eligibility**: all `eligible_roles` may respond to a linked survey (previously only `{DRep, SPO, CC}`, each required to cast a governance vote); the `voting_procedures` vote becomes an optional binding, retained as the only ledger-evaluated path for Plutus-script credentials.

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
- [x] Implement end-to-end survey creation + response + tally in at least one toolchain.
- [ ] Document interoperability results and edge-case handling.

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
