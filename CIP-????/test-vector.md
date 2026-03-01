# Test Vectors for CIP-00XX

This file defines reproducible vectors for:
- Single-question and multi-question survey definitions.
- Built-in, numeric, and custom method responses.
- Latest-valid-response-wins behavior.
- Invalid response detection for unresolved survey binding.
- Governance action anchor linkage validation.
- Linked-response tx-context validation for `voting_procedures` cardinality and linked action-id matching.
- Role-weighting, role-validation, and mixed-role behavior.
- Required `responderRole` claims with claim-vs-chain role validation.
- `PledgeBased` live-pledge weighting behavior.

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

All survey definition examples are expected to include explicit `roleWeighting`.

## Survey Response Vectors

### Vector 7: Single-choice response

Source file: [examples/response-single-choice.json](./examples/response-single-choice.json)

Canonical CBOR payload (hex):
```text
a111a16e737572766579526573706f6e7365a467616e737765727381a26973656c656374696f6e81006a7175657374696f6e4964726369705f303133365f696e636c7573696f6e6a737572766579547849647840626262626262626262626262626262626262626262626262626262626262626262626262626262626262626262626262626262626262626262626262626262626b7370656356657273696f6e65312e302e306d726573706f6e646572526f6c656b5374616b65686f6c646572
```

### Vector 8: Multi-select response

Source file: [examples/response-multi-select.json](./examples/response-multi-select.json)

Canonical CBOR payload (hex):
```text
a111a16e737572766579526573706f6e7365a467616e737765727381a26973656c656374696f6e8201036a7175657374696f6e49646d6369705f73686f72746c6973746a737572766579547849647840656665666566656665666566656665666566656665666566656665666566656665666566656665666566656665666566656665666566656665666566656665666b7370656356657273696f6e65312e302e306d726573706f6e646572526f6c656444526570
```

### Vector 9: Multi-select response (no selections)

Source file: [examples/response-multi-select-empty.json](./examples/response-multi-select-empty.json)

Canonical CBOR payload (hex):
```text
a111a16e737572766579526573706f6e7365a467616e737765727381a26973656c656374696f6e806a7175657374696f6e49646d6369705f73686f72746c6973746a737572766579547849647840656665666566656665666566656665666566656665666566656665666566656665666566656665666566656665666566656665666566656665666566656665666b7370656356657273696f6e65312e302e306d726573706f6e646572526f6c656444526570
```

This vector is valid and demonstrates that `selection: []` is allowed for `multi-select`.

### Vector 10: Numeric response

Source file: [examples/response-numeric-range.json](./examples/response-numeric-range.json)

Canonical CBOR payload (hex):
```text
a111a16e737572766579526573706f6e7365a467616e737765727381a26a7175657374696f6e49647819706172616d657465725f785f696e697469616c5f76616c75656c6e756d6572696356616c75651901456a737572766579547849647840636363636363636363636363636363636363636363636363636363636363636363636363636363636363636363636363636363636363636363636363636363636b7370656356657273696f6e65312e302e306d726573706f6e646572526f6c656444526570
```

### Vector 11: Custom method response

Source file: [examples/response-custom-method.json](./examples/response-custom-method.json)

Canonical CBOR payload (hex):
```text
a111a16e737572766579526573706f6e7365a467616e737765727381a26a7175657374696f6e49646c726f61646d61705f72616e6b6b637573746f6d56616c7565a16772616e6b696e67830200016a737572766579547849647840646464646464646464646464646464646464646464646464646464646464646464646464646464646464646464646464646464646464646464646464646464646b7370656356657273696f6e65312e302e306d726573706f6e646572526f6c656444526570
```

### Vector 12: Multi-question same-type response

Source file: [examples/response-multi-question-same-type.json](./examples/response-multi-question-same-type.json)

Canonical CBOR payload (hex):
```text
a111a16e737572766579526573706f6e7365a467616e737765727382a26a7175657374696f6e4964736d61785f626c6f636b5f626f64795f73697a656c6e756d6572696356616c756518a0a26a7175657374696f6e49646b6d61785f74785f73697a656c6e756d6572696356616c756518206a737572766579547849647840616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616b7370656356657273696f6e65312e302e306d726573706f6e646572526f6c656b5374616b65686f6c646572
```

### Vector 13: Multi-question mixed-type response

Source file: [examples/response-multi-question-mixed-type.json](./examples/response-multi-question-mixed-type.json)

Canonical CBOR payload (hex):
```text
a111a16e737572766579526573706f6e7365a467616e737765727383a26973656c656374696f6e8200026a7175657374696f6e49646d6369705f73686f72746c697374a26973656c656374696f6e81016a7175657374696f6e49646e72656c656173655f74696d696e67a26a7175657374696f6e49646c626c6f636b5f6275646765746c6e756d6572696356616c7565066a737572766579547849647840616261626162616261626162616261626162616261626162616261626162616261626162616261626162616261626162616261626162616261626162616261626b7370656356657273696f6e65312e302e306d726573706f6e646572526f6c656444526570
```

## Duplicate Resolution Vector

Sources:
- Older response: [examples/response-duplicate-older.json](./examples/response-duplicate-older.json)
- Latest response: [examples/response-duplicate-latest.json](./examples/response-duplicate-latest.json)

Given both responses resolve to the same `(surveyTxId, responderRole, responseCredential)`:
- Both responses are in the same epoch.
- Older chain position: `(slot=120100000, txIndexInBlock=2, metadataPosition=0)`.
- Latest chain position: `(slot=120100005, txIndexInBlock=0, metadataPosition=0)`.

Expected tally behavior:
- Ignore the older response.
- Keep only the latest response (`answers = [{"questionId": "cip_0136_inclusion", "selection": [0]}]`).

## Invalid Binding Vector

Expected validation behavior:
- A response is invalid when `surveyTxId` does not resolve to a `surveyDetails` transaction under label `17`.
- Response MUST be ignored in tallies.

## Governance Action Anchor Linkage Vectors

Source:
- [examples/governance-action-anchor-survey-link.json](./examples/governance-action-anchor-survey-link.json)

Expected validation behavior:
- If top-level `surveyTxId` resolves to a `surveyDetails` transaction, the governance action is linked to that survey.
- The legacy nested form `surveyRef.surveyTxId` is invalid for this version.
- Linkage MUST additionally pass compatibility checks:
  - `linkedRoleWeighting = roleWeighting ∩ actionEligibility` is non-empty.
  - Survey `endEpoch` exactly matches the governance action active voting end epoch.
- If validation fails, tooling MUST treat the action-to-survey linkage as invalid and MUST NOT attach that survey to the governance action.
- Linkage invalidity does not invalidate the survey as standalone metadata.

Current anchor reference:
- `surveyTxId = bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb`

## Role Weighting and Security Vectors

### Vector 14: Governance-linked response source requirement

Source:
- Linked tx context: [examples/txctx-linked-valid-single-voter-single-action.json](./examples/txctx-linked-valid-single-voter-single-action.json)

Expected validation behavior:
- For governance-linked surveys, response transactions MUST include a non-empty transaction-body `voting_procedures` element.
- For governance-linked surveys, `voting_procedures` MUST contain exactly one voter entry and exactly one `(govActionId, votingProcedure)` entry.
- The single `govActionId` MUST equal the linked governance action id.
- A signer-only response (without transaction-body `voting_procedures`) is invalid for linked surveys.

### Vector 15: Invalid link compatibility (endEpoch or role mismatch)

Sources:
- Survey definition: [examples/survey-mixed-role-shared.json](./examples/survey-mixed-role-shared.json)
- Governance anchor link object: [examples/governance-action-anchor-survey-link.json](./examples/governance-action-anchor-survey-link.json)

Expected validation behavior:
- If `roleWeighting ∩ actionEligibility` is empty, the action-to-survey link is invalid.
- If survey `endEpoch` does not exactly equal the action voting end epoch, the action-to-survey link is invalid.
- In both cases, tooling MUST ignore the linkage while keeping the survey valid as standalone metadata.

### Vector 16: CredentialBased role verification

Expected validation behavior:
- Every response MUST include claimed `responderRole`.
- In `CredentialBased`, if active role set includes `DRep`, `SPO`, or `CC`, each response MUST be role-verifiable from chain data at response time.
- A response is invalid when claimed `responderRole` is not part of the active role set.
- A response is invalid when claimed `responderRole` disagrees with chain-derived role evidence.
- Unverifiable role membership is invalid.
- `Stakeholder` is residual-only:
  - if exactly one stake credential is derivable after governance-role candidates fail, tooling MUST classify as `Stakeholder`,
  - if zero or multiple stake credentials are derivable, the response is invalid.

### Vector 17: Role-to-weighting compatibility constraints

Expected validation behavior:
- `CC: StakeBased` is invalid.
- `Stakeholder: CredentialBased` is invalid.
- Canonical tally output is per-role. Tools MAY additionally publish merged/composite outputs with disclosed logic.

### Vector 18: End-epoch and timing semantics

Expected validation behavior:
- All surveys MUST define `endEpoch`.
- Responses are valid only when `responseEpoch <= endEpoch`.
- Role-membership and credential eligibility checks are evaluated at response time.
- `StakeBased` and `PledgeBased` weights are read at `endEpoch`.
- `CredentialBased` weight is `1` per valid latest response.

### Vector 19: roleWeighting is mandatory

Expected validation behavior:
- A survey definition without `roleWeighting` is invalid.
- A survey definition without `endEpoch` is invalid.
- Legacy `eligibility` and `voteWeighting` fields are invalid for this draft model.

### Vector 20: Valid linked mixed-role weighting

Sources:
- Survey definition: [examples/survey-mixed-role-shared.json](./examples/survey-mixed-role-shared.json)
- Response: [examples/response-mixed-role-shared.json](./examples/response-mixed-role-shared.json)

Expected validation behavior:
- Survey is valid with mixed role weighting (`DRep: StakeBased`, `SPO: PledgeBased`).
- Linked response identity is derived from the single voter entry in transaction-body `voting_procedures`.
- Claimed `responderRole` in the response MUST exactly match the role derived from that single voter entry.
- Canonical output is role-separated tally results.

### Vector 21: Valid standalone mixed-role weighting

Sources:
- Survey definition: [examples/survey-mixed-role-shared.json](./examples/survey-mixed-role-shared.json)
- Response: [examples/response-mixed-role-shared.json](./examples/response-mixed-role-shared.json)

Expected validation behavior:
- Survey is valid with mixed role weighting and required `endEpoch`.
- Standalone response must include claimed `responderRole`, and derivation is scoped to that claimed role.
- Standalone response is valid only if exactly one eligible `responseCredential` is derivable for claimed `responderRole`.
- Membership checks occur at response time. Weighting uses `endEpoch`.

### Vector 22: Invalid linked response (`voting_procedures` action-id mismatch)

Sources:
- Survey definition: [examples/survey-mixed-role-shared.json](./examples/survey-mixed-role-shared.json)
- Governance anchor link object: [examples/governance-action-anchor-survey-link.json](./examples/governance-action-anchor-survey-link.json)
- Response: [examples/response-mixed-role-shared.json](./examples/response-mixed-role-shared.json)

Expected validation behavior:
- Response is invalid because the single `govActionId` in `voting_procedures` does not match the linked governance action id.

### Vector 23: Invalid linked response (`voting_procedures` cardinality)

Sources:
- Survey definition: [examples/survey-mixed-role-shared.json](./examples/survey-mixed-role-shared.json)
- Governance anchor link object: [examples/governance-action-anchor-survey-link.json](./examples/governance-action-anchor-survey-link.json)
- Response: [examples/response-mixed-role-shared.json](./examples/response-mixed-role-shared.json)

Expected validation behavior:
- Response is invalid because linked responses MUST have exactly one voter entry and exactly one `(govActionId, votingProcedure)` entry.

### Vector 24: Valid linked response (`voting_procedures` strict shape)

Sources:
- Survey definition: [examples/survey-mixed-role-shared.json](./examples/survey-mixed-role-shared.json)
- Governance anchor link object: [examples/governance-action-anchor-survey-link.json](./examples/governance-action-anchor-survey-link.json)
- Response: [examples/response-mixed-role-shared.json](./examples/response-mixed-role-shared.json)
- Linked tx context: [examples/txctx-linked-valid-single-voter-single-action.json](./examples/txctx-linked-valid-single-voter-single-action.json)

Expected validation behavior:
- Linked response source requirement is satisfied when `voting_procedures` is non-empty, contains exactly one voter entry, contains exactly one inner `(govActionId, votingProcedure)` entry, and that `govActionId` matches the linked governance action id.

### Vector 25: `PledgeBased` zero active pools at snapshot => zero weight

Source:
- Pledge weighting context: [examples/txctx-pledge-zero-pools-at-end.json](./examples/txctx-pledge-zero-pools-at-end.json)

Expected validation behavior:
- Response remains valid when SPO credential validity was established at response time.
- If mapped active pool set is empty at `endEpoch`, `PledgeBased` contribution is weight `0`.

## Invalid Scenarios

Expected validation behavior:
- `CC: StakeBased` is invalid because `CC` MAY only use `CredentialBased`.
- `Stakeholder: CredentialBased` is invalid because `Stakeholder` MAY only use `StakeBased`.
- A response is invalid if `responderRole` is missing.
- A response is invalid if claimed `responderRole` is not eligible under the survey active role set.
- A response is invalid if claimed `responderRole` disagrees with chain-derived role evidence.
- A standalone response is invalid if more than one eligible `responseCredential` is derivable for the claimed role.
- A standalone response is invalid if no eligible `responseCredential` is derivable for the claimed role.

## Schema vs Semantic Validation Boundary

Expected implementation behavior:
- JSON Schema validation SHOULD be used for payload shape validation.
- Successful JSON Schema validation does not imply semantic validity.
- Tools MUST additionally enforce semantic rules from CIP text, including:
  - governance-link resolution by `surveyTxId`
  - linked role/end-epoch compatibility checks and invalid-link handling
  - governance-linked response source requirements (non-empty transaction-body `voting_procedures`, exactly-one voter+entry, and linked action-id match)
  - required `responderRole` claim and claim-vs-chain role consistency checks
  - role-membership verification requirements
  - single eligible `responseCredential` derivation requirement within the claimed role scope
  - end-epoch response cutoff and snapshot rules
  - `PledgeBased` signer-to-pool mapping and live-pledge resolution rules
