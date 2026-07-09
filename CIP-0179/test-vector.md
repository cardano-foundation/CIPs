# Test Vectors for CIP-0179

These vectors use the version `5` JSON representation of label `17` CBOR metadata:

- Integer CBOR map keys are JSON object keys (`"0"`, `"1"`, ...).
- Byte strings are lowercase hex.
- Definitions and responses are batched as `[tag, [items...]]`.
- Survey references are `[tx_id, survey_index]`.
- Roles are integer eligibility claims, not weighting modes.

## Definition Vectors

| Vector | Source | Main expectation |
|:--|:--|:--|
| 1 | [survey-single-choice.json](./examples/survey-single-choice.json) | One public single-choice survey for `Stakeholder` (`3`). |
| 2 | [survey-multi-select.json](./examples/survey-multi-select.json) | Multi-select question with `min_selections = 0`; an empty present answer is "none selected", not abstain. |
| 3 | [survey-numeric-range.json](./examples/survey-numeric-range.json) | Numeric-range question for `DRep`, `SPO`, and `CC` (`[0, 1, 2]`). |
| 4 | [survey-custom-method.json](./examples/survey-custom-method.json) | Custom tag `0` question with method schema anchored by URI and `blake2b-256` hash. |
| 5 | [survey-multi-question-same-type.json](./examples/survey-multi-question-same-type.json) | Two numeric-range questions at indices `0` and `1`. |
| 6 | [survey-multi-question-mixed-type.json](./examples/survey-multi-question-mixed-type.json) | Multi-select, single-choice, and numeric-range questions at indices `0`, `1`, and `2`. |
| 7 | [survey-mixed-role-shared.json](./examples/survey-mixed-role-shared.json) | Mixed eligibility `[0, 1, 3]`; no weighting field is present or implied. |

External presentation profile: [external-survey-presentation.json](./examples/external-survey-presentation.json) gives the recommended JSON shape for renderable off-chain text referenced by a definition `content_anchor`.

## Response Vectors

| Vector | Source | Main expectation |
|:--|:--|:--|
| 8 | [response-single-choice.json](./examples/response-single-choice.json) | Stakeholder response to `[bbbb..., 0]`, answering question `0` with option `0`. |
| 9 | [response-multi-select.json](./examples/response-multi-select.json) | Answer item `[2, 0, [1, 3]]`. |
| 10 | [response-multi-select-empty.json](./examples/response-multi-select-empty.json) | Answer item `[2, 0, []]`, valid for vector 2 because `min_selections = 0`. |
| 11 | [response-numeric-range.json](./examples/response-numeric-range.json) | Answer item `[4, 0, 325]`, valid for constraints `[10, 1000, 5]`. |
| 12 | [response-custom-method.json](./examples/response-custom-method.json) | Custom answer value is transaction metadatum interpreted by the anchored method schema. |
| 13 | [response-multi-question-same-type.json](./examples/response-multi-question-same-type.json) | Numeric answers for question indices `0` and `1`. |
| 14 | [response-multi-question-mixed-type.json](./examples/response-multi-question-mixed-type.json) | Answer tags match the referenced question tags: `2`, `1`, `4`. |

## Behavior Vectors

### Latest Valid Response Wins

Sources:
- Older response: [response-duplicate-older.json](./examples/response-duplicate-older.json)
- Latest response: [response-duplicate-latest.json](./examples/response-duplicate-latest.json)

Both responses share:

```text
(survey_ref = [bbbb..., 0], role = 3, credential = [0, 1111...1111])
```

Given chain positions:

```text
older  = (slot=120100000, tx_index_in_block=2, response_index=0)
latest = (slot=120100005, tx_index_in_block=0, response_index=0)
```

Expected tally behavior: ignore the older response and keep the latest answer `[1, 0, 0]`.

### Governance Action Linkage

Source: [governance-action-anchor-survey-link.json](./examples/governance-action-anchor-survey-link.json)

Expected: the anchor's `body.cip179` object (with `kind = "survey-link"`) links a governance action of any type to `survey_ref = [bbbb..., 0]` only if the survey exists and its `end_epoch` equals the action's expiry epoch. Failed linkage does not invalidate the standalone survey.

### Optional Governance-Vote Binding

Source: [txctx-linked-valid-single-voter-single-action.json](./examples/txctx-linked-valid-single-voter-single-action.json)

Expected: linked responses do not need `voting_procedures`; if present, the binding must match the response credential, linked action id, and claimed role. A passing binding is sufficient credential proof and is the only defined proof path for Plutus-script credentials.

### Cancellation

Source: [cancellation.json](./examples/cancellation.json)

Expected: the payload cancels `survey_ref = [efef..., 0]` when the transaction proves ownership of that survey definition's owner credential.

## Semantic Checks Beyond JSON Schema

Schema validation covers structure only. Tooling still enforces the README rules, including:

- survey reference resolution
- credential proof and role validation
- response epoch cutoff and tally-time re-verification
- required-question omission
- answer tag and question-index uniqueness
- option bounds and selection/ranking cardinality
- numeric min/max and step constraints
- cancellation authorization
- governance-link and optional-binding checks
