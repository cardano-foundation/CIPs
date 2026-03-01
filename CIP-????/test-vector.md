# Test Vectors for CIP-00XX

This file defines reproducible vectors for:
- Single-question and multi-question survey definitions.
- Built-in, numeric, and custom method responses.
- Latest-valid-response-wins behavior.
- Invalid response detection for unresolved survey binding.
- Governance action anchor linkage validation.
- Weighting, eligibility, and role-validation behavior.

## Survey Definition Vectors

### Vector 1: Single-choice (single-question survey)

Source file: [examples/survey-single-choice.json](./examples/survey-single-choice.json)

### Vector 2: Multi-select (single-question survey)

Source file: [examples/survey-multi-select.json](./examples/survey-multi-select.json)

### Vector 3: Numeric range (single-question survey)

Source file: [examples/survey-numeric-range.json](./examples/survey-numeric-range.json)

### Vector 4: Custom method with schema integrity (single-question survey)

Source file: [examples/survey-custom-method.json](./examples/survey-custom-method.json)

### Vector 5: Multi-question same-type (numeric-range)

Source file: [examples/survey-multi-question-same-type.json](./examples/survey-multi-question-same-type.json)

### Vector 6: Multi-question mixed-type

Source file: [examples/survey-multi-question-mixed-type.json](./examples/survey-multi-question-mixed-type.json)

All survey definition examples are expected to include explicit `voteWeighting`.

## Survey Response Vectors

### Vector 7: Single-choice response

Source file: [examples/response-single-choice.json](./examples/response-single-choice.json)

Canonical CBOR payload (hex):
```text
a111a16e737572766579526573706f6e7365a367616e737765727381a26973656c656374696f6e81006a7175657374696f6e4964726369705f303133365f696e636c7573696f6e6a737572766579547849647840626262626262626262626262626262626262626262626262626262626262626262626262626262626262626262626262626262626262626262626262626262626b7370656356657273696f6e65312e302e30
```

### Vector 8: Multi-select response

Source file: [examples/response-multi-select.json](./examples/response-multi-select.json)

Canonical CBOR payload (hex):
```text
a111a16e737572766579526573706f6e7365a367616e737765727381a26973656c656374696f6e8201036a7175657374696f6e49646d6369705f73686f72746c6973746a737572766579547849647840656665666566656665666566656665666566656665666566656665666566656665666566656665666566656665666566656665666566656665666566656665666b7370656356657273696f6e65312e302e30
```

### Vector 9: Multi-select response (no selections)

Source file: [examples/response-multi-select-empty.json](./examples/response-multi-select-empty.json)

Canonical CBOR payload (hex):
```text
a111a16e737572766579526573706f6e7365a367616e737765727381a26973656c656374696f6e806a7175657374696f6e49646d6369705f73686f72746c6973746a737572766579547849647840656665666566656665666566656665666566656665666566656665666566656665666566656665666566656665666566656665666566656665666566656665666b7370656356657273696f6e65312e302e30
```

This vector is valid and demonstrates that `selection: []` is allowed for `multi-select`.

### Vector 10: Numeric response

Source file: [examples/response-numeric-range.json](./examples/response-numeric-range.json)

Canonical CBOR payload (hex):
```text
a111a16e737572766579526573706f6e7365a367616e737765727381a26a7175657374696f6e49647819706172616d657465725f785f696e697469616c5f76616c75656c6e756d6572696356616c75651901456a737572766579547849647840636363636363636363636363636363636363636363636363636363636363636363636363636363636363636363636363636363636363636363636363636363636b7370656356657273696f6e65312e302e30
```

### Vector 11: Custom method response

Source file: [examples/response-custom-method.json](./examples/response-custom-method.json)

Canonical CBOR payload (hex):
```text
a111a16e737572766579526573706f6e7365a367616e737765727381a26a7175657374696f6e49646c726f61646d61705f72616e6b6b637573746f6d56616c7565a16772616e6b696e67830200016a737572766579547849647840646464646464646464646464646464646464646464646464646464646464646464646464646464646464646464646464646464646464646464646464646464646b7370656356657273696f6e65312e302e30
```

### Vector 12: Multi-question same-type response

Source file: [examples/response-multi-question-same-type.json](./examples/response-multi-question-same-type.json)

Canonical CBOR payload (hex):
```text
a111a16e737572766579526573706f6e7365a367616e737765727382a26a7175657374696f6e4964736d61785f626c6f636b5f626f64795f73697a656c6e756d6572696356616c756518a0a26a7175657374696f6e49646b6d61785f74785f73697a656c6e756d6572696356616c756518206a737572766579547849647840616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616b7370656356657273696f6e65312e302e30
```

### Vector 13: Multi-question mixed-type response

Source file: [examples/response-multi-question-mixed-type.json](./examples/response-multi-question-mixed-type.json)

Canonical CBOR payload (hex):
```text
a111a16e737572766579526573706f6e7365a367616e737765727383a26973656c656374696f6e8200026a7175657374696f6e49646d6369705f73686f72746c697374a26973656c656374696f6e81016a7175657374696f6e49646e72656c656173655f74696d696e67a26a7175657374696f6e49646c626c6f636b5f6275646765746c6e756d6572696356616c7565066a737572766579547849647840616261626162616261626162616261626162616261626162616261626162616261626162616261626162616261626162616261626162616261626162616261626b7370656356657273696f6e65312e302e30
```

## Duplicate Resolution Vector

Sources:
- Older response: [examples/response-duplicate-older.json](./examples/response-duplicate-older.json)
- Latest response: [examples/response-duplicate-latest.json](./examples/response-duplicate-latest.json)

Given both responses resolve to the same `(surveyTxId, responseCredential)`:
- Older chain position: `(slot=120100000, txIndexInBlock=2, metadataPosition=0)`.
- Latest chain position: `(slot=120100005, txIndexInBlock=0, metadataPosition=0)`.

Expected tally behavior:
- Ignore the older response.
- Keep only the latest response (`answers = [{"questionId": "cip_0136_inclusion", "selection": [0]}]`).

## Invalid Binding Vector

Source:
- Invalid response: [examples/response-invalid-mismatch.json](./examples/response-invalid-mismatch.json)

Expected validation behavior:
- Response is invalid because `surveyTxId` does not resolve to a `surveyDetails` transaction under label `17`.
- Response MUST be ignored in tallies.

## Governance Action Anchor Linkage Vectors

Source:
- [examples/governance-action-anchor-survey-link.json](./examples/governance-action-anchor-survey-link.json)

Expected validation behavior:
- If top-level `surveyTxId` resolves to a `surveyDetails` transaction, the governance action is linked to that survey.
- The legacy nested form `surveyRef.surveyTxId` is invalid for this version.
- If validation fails, tooling MUST treat the action-to-survey linkage as invalid and MUST NOT attach that survey to the governance action.

Current anchor reference:
- `surveyTxId = bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb`

## Weighting and Eligibility Security Vectors

### Vector 14: Governance-linked response source requirement

Expected validation behavior:
- For governance-linked surveys, response transactions MUST include governance voting procedures.
- A signer-only response (without governance voting procedures) is invalid for linked surveys.

### Vector 15: Linked eligibility intersection

Expected validation behavior:
- For linked surveys, tooling derives `actionEligibility` from the governance action.
- If `surveyDetails.eligibility` is present, effective eligibility is the intersection with `actionEligibility`.
- If the intersection is empty, the linked survey configuration is invalid and responses MUST be ignored.

### Vector 16: CredentialBased role verification

Expected validation behavior:
- In `CredentialBased`, if effective eligibility includes `DRep`, `SPO`, or `CC`, each response MUST be role-verifiable from chain data.
- Unverifiable role membership is invalid.
- `Stakeholder` does not require role-membership verification.

### Vector 17: StakeBased role-domain constraints

Expected validation behavior:
- `StakeBased` with `CC` eligibility is invalid.
- If multiple stake roles are eligible (for example `DRep` and `SPO`), canonical tally output is per-role.
- Tools MAY additionally publish merged/composite outputs.

### Vector 18: Standalone StakeBased identity extraction and snapshot

Expected validation behavior:
- Standalone `StakeBased` surveys MUST define `lifecycle.endSlot`; stake snapshot is taken at `lifecycle.endSlot`.
- Tooling MUST derive exactly one stake credential from stake-credential signals in chain data.
- If zero or multiple distinct stake credentials are derivable, the response is invalid.

### Vector 19: voteWeighting is mandatory

Expected validation behavior:
- A survey definition without `voteWeighting` is invalid.
