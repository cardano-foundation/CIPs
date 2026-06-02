---
CIP: XXXX
Title: Hydra-Powered Voting Token Standard
Category: Tokens
Status: Proposed
Authors:
    - Adam Dean <adam@crypto2099.io>
    - Mad Orkestra <mad@madorkestra.com>
Implementors:
    - Ekklesia <https://app.ekklesia.vote>
    - Intersect <https://hydra-voting.intersectmbo.org>
    - Civitas <https://www.civitasexplorer.com/>
    - Fetch <https://cardano.fetchswap.io/governance>
Discussions:
    - https://github.com/cardano-foundation/CIPs/pull/?
Created: 2026-05-12
License: Apache-2.0
---

## Abstract

This CIP defines a token standard for conducting verifiable, auditable votes on
Cardano using Hydra L2 state channels. It specifies two paired
[CIP-67][CIP-0067] tokens: a **(600) _Ballot Definition_** token and a
**(601) _Ballot Instance_** token, that together anchor the entire lifecycle of
a ballot: from immutable ballot definition on L1, through high throughput voting
inside a Hydra head, to on-chain settlement of cryptographically verifiable
results.

The standard defines _voter registration tokens_ with credential-typed asset
names, a _vote evidence_ schema with explicit abstain semantics, a
merkle-proof-based inclusion-verification system, and a
[CIP-179][CIP-0179]-compatible question/answer format that supports seven voting
methods (binary, single-choice, multi-choice, range, ranked, weighted, and
likert).

CDDL schemas are provided for the two on-chain datums (600, 601) so an
independent implementer can reproduce the on-chain bytes from this document
alone.

## Motivation: why is this CIP necessary?

Existing on-chain voting mechanisms on Cardano face a fundamental tension
between verifiability and scalability:

- **Fully on-chain voting** (one L1 transaction per vote) is expensive, slow,
  and impractical for elections with thousands of voters.
- **Off-chain voting** (database-backed) is fast but requires trust in the
  operator. Voters cannot independently verify that their vote was recorded
  correctly or that results were tallied honestly.

Hydra L2 state channels resolve this tension by processing votes as real
transactions inside a state channel while settling results on L1. However, there
is currently no standard for how ballot definitions, vote records, and results
should be structured on-chain to enable independent auditing.

This CIP provides that standard. It enables:

1. **Immutable ballot anchoring.** The ballot structure, questions, and rules
   are committed to L1 before voting begins and cannot be altered after the
   voting window opens.
2. **Cryptographic vote recording.** Every vote is a signed transaction inside
   the head with a verifiable datum, providing non-repudiation of each voter's
   recorded selection.
3. **Merkle-proof auditability.** Any voter can prove their vote was included in
   the final results using a merkle inclusion proof against an on-chain root.
4. **Separation of concerns.** The voting infrastructure records *who voted and
   how*. Voting power, eligibility, and threshold decisions are applied
   externally by the voting authority, not by the voting system.
5. **Interoperability with [CIP-179][CIP-0179].** The question/answer format
   attempts to align with the on-chain polling structure proposed in
   [CIP-179][CIP-0179] (Cardano Native Polls), allowing tooling reuse.

### Scope and non-goals

This CIP standardizes **the cryptographic recording of votes and the verifiable
publication of results**. It deliberately does NOT standardize, and an
implementation **MUST NOT** rely on this CIP to prescribe:

- **Voter eligibility.** Who is permitted to register for a given ballot, and
  under what conditions a registration **MUST** be refused.
- **Voting power.** How a voter's recorded selection translates to influence on
  a decision. Stake snapshots, DRep delegation snapshots, SPO pledge snapshots,
  and any weighting formula applied to them are out of scope.
- **Tabulation decisions.** How raw recorded selections translate to a "winning"
  outcome. Quorum rules, supermajority thresholds, vote splitting, and
  Condorcet-style aggregations are out of scope.
- **Authorities and identities.** Identify which on-chain key or organization is
  the legitimate voting authority for a given ballot. This CIP records that
  authority's signing key in the (600) datum but does not opine on its
  legitimacy.
- **Stake or credential snapshots.** Capture procedures for DRep delegation, SPO
  pledge, or stake-credential balances are out of scope. If a tabulation step
  references such a snapshot, the snapshot's provenance is the voting
  authority's responsibility, not the voting infrastructure's.

These concerns are the **voting authority's** responsibility. They are
intentionally separated from the voting record for two reasons:

1. **They are politically contested.** Different ballots in the same ecosystem
   may reasonably use different eligibility, weighting, and tabulation rules.
   Baking any one approach into shared infrastructure makes the infrastructure
   unsuitable for the others.
2. **The same recorded vote set should be re-tabulatable.** A vote recorded
   under this CIP can be re-tallied later under a different weighting or
   eligibility rule without re-running the voting process. The voting record is
   the input to tabulation, not its conclusion.

What this CIP provides is the **proof set**: the cryptographic artifacts that
let any independent observer confirm what was recorded, by whom, and with what
intent. What an entity (the voting authority, a constitutional committee, a
treasury executor) chooses to *do* with that proof set, including how to weight
it, which voters to count, and what threshold constitutes a "pass" is a
separate, deliberately unstandardized layer.

The §7.8 auditor verification algorithm reflects this scope: it validates the
integrity, completeness, and authenticity of the recorded vote set against the
on-chain commitments. It does **not** opine on whether a ballot "passed."

## Specification

### 1. Token architecture

#### 1.1. [CIP-67][CIP-0067] label allocation

This standard defines two [CIP-67][CIP-0067] asset name labels:

| Label | Hex prefix | Name              | Purpose                                   |
|-------|------------|-------------------|-------------------------------------------|
| 600   | `00258a50` | Ballot Definition | Immutable ballot structure, stays on L1   |
| 601   | `00259a20` | Ballot Instance   | Transits Hydra head, carries results back |

Both tokens share the same policy ID and the same 28-byte fingerprint suffix.
The fingerprint is derived from a ballot namespace string:

```text
fingerprint = blake2b_224(utf8_encode(namespace))
```

Where `namespace` is a human-readable identifier for the ballot (e.g.,
`"vote.ekklesia.intersect.budget2026"`).

#### 1.2. Asset name construction

```text
asset_name = cip67_prefix (4 bytes) || fingerprint (28 bytes)
           = 32 bytes total (64 hex characters)
```

Example:

```text
namespace        = "vote.ekklesia.intersect.budget2026"
namespace bytes  = 766f74652e656b6b6c657369612e696e746572736563742e62756467657432303236  (34 bytes, UTF-8)

fingerprint      = blake2b_224(namespace bytes)
                 = 72386e56d8c3e598bfb4b1b003e972cbcdadbce07e0b779330082077        (28 bytes, 56 hex)

(600) asset_name = 00258a50 || 72386e56d8c3e598bfb4b1b003e972cbcdadbce07e0b779330082077
                 = 00258a5072386e56d8c3e598bfb4b1b003e972cbcdadbce07e0b779330082077  (32 bytes, 64 hex)

(601) asset_name = 00259a20 || 72386e56d8c3e598bfb4b1b003e972cbcdadbce07e0b779330082077
                 = 00259a2072386e56d8c3e598bfb4b1b003e972cbcdadbce07e0b779330082077  (32 bytes, 64 hex)
```

An independent implementer can reproduce these bytes from any BLAKE2b
implementation configured to emit a 28-byte (224-bit) digest over the UTF-8
encoding of the namespace string.

#### 1.3. Minting policy

The minting policy **MUST** be a native script with the following structure:

```json
{
  "type": "all",
  "scripts": [
    {
      "type": "sig",
      "keyHash": "<voting_authority_key_hash>"
    },
    {
      "type": "before",
      "slot": "<voting_window_open_slot>"
    }
  ]
}
```

This ensures:

- Only the voting authority can mint or burn ballot tokens.
- After the voting window opens, the policy is permanently locked. No new tokens
  can be minted and existing tokens cannot be burned on L1.

Exactly **one** of each token (600 and 601) **MUST** be minted in a single
transaction.

The native script shape is chosen so the two properties above are **statically
verifiable** from the script bytes alone, with no execution required. The §7.8
auditor relies on this: a structural read of the policy is sufficient to prove
no late mint or burn could ever have been submitted, independent of what was
actually observed on-chain.

A Plutus minting policy could enforce the same two properties, and potentially
add useful ones. Such policies are deliberately out of scope for
`specVersion 0.3.0`: they shift the audit guarantee from structural to semantic,
requiring the auditor to read the script source, trust a reproducible build, and
reason about the script's behavior under all inputs.

A future revision of this standard **MAY** define a Plutus-policy variant by
specifying the normative properties any policy **MUST** enforce (decoupled from
the script type) and the §7.8 augmentations needed to verify those properties
against an arbitrary Plutus script. Until then, conforming ballots
**MUST** use the native script defined above.

#### 1.4. Why not [CIP-68][CIP-0068]?

[CIP-68][CIP-0068] defines reference/user token pairs using labels (100)/(222)
with an NFT-oriented datum schema (`name`, `image`, `mediaType`). These fields
are not applicable to voting. This standard defines purpose-built datum schemas
optimized for ballot data, vote evidence, and result anchoring.

The pairing convention is analogous to [CIP-68][CIP-0068]: same policy, same
fingerprint suffix, different label prefix, with the (600) serving as the
immutable reference and the (601) as the mutable instance.

### 2. Ballot Definition Token (600)

The (600) token is minted on L1 and remains there for the lifetime of the
ballot. It serves as the immutable, publicly verifiable record of what was being
voted on.

#### 2.1. On-chain datum

The (600) token **MUST** carry an inline datum in Plutus `Constr 0` format
wrapping a positional fields list and a schema version integer.

**CDDL:**

```cddl
ballot_definition_datum = #6.121([fields, version])

fields = [
  title:               bstr,   ; UTF-8 short title for on-chain identification
  namespace:           bstr,   ; UTF-8 fingerprint source (e.g. "vote.ekklesia.intersect.budget2026")
  voting_authority:    bstr,   ; UTF-8 bech32 of the voting authority address
  content_hash:        bstr,   ; UTF-8 of 64-char hex (blake2b_256 of question merkle root)
  ballot_cid:          bstr,   ; UTF-8 of the IPFS CID of the full BallotDefinition JSON
  question_count:      uint,   ; Plutus Int, ≥ 1
  voting_window_open:  bstr,   ; UTF-8 ISO-8601 timestamp (UTC), timelock anchor for the policy
  voting_window_close: bstr,   ; UTF-8 ISO-8601 timestamp (UTC)
  end_epoch:           uint    ; Plutus Int, Cardano epoch at which voting ends
]

version = uint                  ; datum schema version (see §8)
```

The datum is intentionally slim. Full ballot content (questions, options,
descriptions, role weighting) is stored on IPFS and referenced by
`ballot_cid`. The `content_hash` provides a tamper-evident link: anyone can
fetch the IPFS content, recompute the per-question merkle tree, and verify its
root matches the on-chain value.

#### 2.2. IPFS ballot definition

The full ballot definition is pinned to IPFS and referenced from the
(600) on-chain datum via `ballot_cid` (the CID) and `content_hash` (the
per-question merkle root of `questions`, see §2.3). The top-level fields
(`specVersion`, `title`, `description`, `questions`, `roleWeighting`,
`endEpoch`) are [CIP-179][CIP-0179] compatible; the `ekklesia` extension block
carries Hydra-specific metadata.

##### 2.2.1. Illustrative document

```json
{
  "specVersion": "0.3.0",
  "title": "Cardano Incentives Working Group: Budget 2026",
  "description": "Decide the 2026 working-group budget envelope and the per-track allocation across the four candidate workstreams.",
  "questions": [
    {
      "questionId": "budget-envelope-2026",
      "question": "Approve the 2026 working-group budget envelope of 5,000,000 ADA?",
      "description": "A simple binary vote on the working-group budget envelope.",
      "method": "single-choice",
      "options": [
        {
          "label": "Approve",
          "value": 1
        },
        {
          "label": "Reject",
          "value": 2
        },
        {
          "label": "Abstain",
          "value": 0
        }
      ],
      "requireAnswer": false,
      "contentHash": "815d74ff47b1c028b66905bc5d3ddebee54ab17aa96ad735d7e7cb17d5c06fbc"
    },
    {
      "questionId": "track-allocation-2026",
      "question": "Allocate 100 points across the working-group tracks for FY2026.",
      "description": "Distribute exactly 100 points across the four candidate workstreams. Sum must equal the budget.",
      "method": "weighted",
      "options": [
        {
          "label": "Education & Outreach",
          "value": 1
        },
        {
          "label": "Technical Standards",
          "value": 2
        },
        {
          "label": "Developer Tools",
          "value": 3
        },
        {
          "label": "Documentation & QA",
          "value": 4
        }
      ],
      "budget": 100,
      "contentHash": "4e79201cd820000f31cdc0bfb07ce73e3ef0aa1a56aa8c54a728a04911a55287"
    }
  ],
  "roleWeighting": {
    "drep": "CredentialBased",
    "pool": "StakeBased",
    "stake": "StakeBased"
  },
  "endEpoch": 612,
  "ekklesia": {
    "namespace": "vote.ekklesia.intersect.budget2026",
    "votingAuthority": "addr1qxy2fxv2d8lp286dft6kc2vr9yu3mhyasjhm0g3q8f8lquprwlav3gxsv3v7k67tljfq2ky9r9kcgy5r8f0xt5qqxue2sng3rrj",
    "context": "hydra-head",
    "acceptedCredentials": [
      "drep",
      "pool",
      "stake"
    ],
    "merkleRoot": "86d49d38c6f8de486e2c34267f57f41e876dfb5adec095f64d49d3c77cf32dcf",
    "ballotIpfsCid": "QmRsYEp3qm4oQa47mvDVfWcsXynMLWjhixNF3ybZnGaWSB",
    "votingWindow": {
      "open": "2026-06-01T00:00:00Z",
      "close": "2026-06-08T00:00:00Z"
    }
  }
}
```

The two `contentHash` values above are `blake2b_256` of each question's
off-chain content blob (rationale, option detail, etc.), pinned independently of
this ballot definition; they do **not** hash the question object itself. The
top-level `merkleRoot` is the root of the per-question merkle tree built per
§2.3 (leaf prefix `0x00`, internal prefix `0x01`, blake2b_256, lexicographic
pair sort), whose leaves are `blake2b_256(JSON.stringify(question))` over each
entire question object using the compact serialization of §7.7. That leaf
computation binds `contentHash` (and every other question field) to the on-chain
commitment. The same value appears as `content_hash` in the (600) on-chain
datum.

##### 2.2.2. JSON Schema

The following JSON Schema (Draft 2020-12) is normative. A document that fails
this schema is not a conforming ballot definition.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://docs.ekklesia.vote/cip/hydra-voting-tokens/ballot-definition.schema.json",
  "title": "BallotDefinition",
  "description": "Full ballot definition pinned to IPFS. Referenced by the (600) token's content_hash + ballot_cid on-chain.",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "specVersion",
    "title",
    "description",
    "questions",
    "roleWeighting",
    "endEpoch",
    "ekklesia"
  ],
  "properties": {
    "specVersion": {
      "type": "string",
      "description": "Semver string. See §8.2 for the versioning rules. Current canonical value is '0.3.0'.",
      "pattern": "^\\d+\\.\\d+\\.\\d+$"
    },
    "title": {
      "type": "string",
      "minLength": 1
    },
    "description": {
      "type": "string"
    },
    "questions": {
      "type": "array",
      "minItems": 1,
      "items": {
        "$ref": "#/$defs/BallotQuestion"
      }
    },
    "roleWeighting": {
      "$ref": "#/$defs/RoleWeighting"
    },
    "endEpoch": {
      "type": "integer",
      "minimum": 0,
      "description": "Cardano epoch at which voting ends. Informational alignment with votingWindow.close."
    },
    "ekklesia": {
      "$ref": "#/$defs/EkklesiaExtension"
    }
  },
  "$defs": {
    "VoteMethod": {
      "type": "string",
      "enum": [
        "binary",
        "single-choice",
        "multi-choice",
        "range",
        "ranked",
        "weighted",
        "likert"
      ]
    },
    "BallotOption": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "label",
        "value"
      ],
      "properties": {
        "label": {
          "type": "string",
          "minLength": 1
        },
        "value": {
          "type": "integer"
        }
      }
    },
    "IntegerGrid": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "min",
        "max"
      ],
      "description": "Arithmetic integer grid {min, min+step, …, max}. Constraint not expressible in JSON Schema: (max - min) MUST be a non-negative multiple of step.",
      "properties": {
        "min": {
          "type": "integer"
        },
        "max": {
          "type": "integer"
        },
        "step": {
          "type": "integer",
          "minimum": 1,
          "default": 1
        }
      }
    },
    "BallotQuestion": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "questionId",
        "question",
        "method"
      ],
      "properties": {
        "questionId": {
          "type": "string",
          "minLength": 1
        },
        "question": {
          "type": "string",
          "minLength": 1
        },
        "description": {
          "type": "string"
        },
        "method": {
          "$ref": "#/$defs/VoteMethod"
        },
        "options": {
          "type": "array",
          "minItems": 1,
          "items": {
            "$ref": "#/$defs/BallotOption"
          }
        },
        "minSelections": {
          "type": "integer",
          "minimum": 1
        },
        "maxSelections": {
          "type": "integer",
          "minimum": 1
        },
        "valueRange": {
          "$ref": "#/$defs/IntegerGrid"
        },
        "rankCount": {
          "type": "integer",
          "minimum": 1
        },
        "budget": {
          "type": "integer",
          "minimum": 1
        },
        "ratingRange": {
          "$ref": "#/$defs/IntegerGrid"
        },
        "requireAnswer": {
          "type": "boolean",
          "default": false
        },
        "contentHash": {
          "type": "string",
          "pattern": "^[0-9a-f]{64}$",
          "description": "Optional blake2b_256 (64 lowercase hex) of the question's off-chain content blob. When present, participates in the question's merkle leaf and therefore in content_hash on the (600) datum."
        }
      },
      "allOf": [
        {
          "if": {
            "properties": {
              "method": {
                "const": "range"
              }
            },
            "required": [
              "method"
            ]
          },
          "then": {
            "required": [
              "valueRange"
            ]
          }
        },
        {
          "if": {
            "properties": {
              "method": {
                "const": "weighted"
              }
            },
            "required": [
              "method"
            ]
          },
          "then": {
            "required": [
              "options",
              "budget"
            ]
          }
        },
        {
          "if": {
            "properties": {
              "method": {
                "const": "likert"
              }
            },
            "required": [
              "method"
            ]
          },
          "then": {
            "required": [
              "options",
              "ratingRange"
            ]
          }
        },
        {
          "if": {
            "properties": {
              "method": {
                "enum": [
                  "binary",
                  "single-choice",
                  "multi-choice",
                  "ranked"
                ]
              }
            },
            "required": [
              "method"
            ]
          },
          "then": {
            "required": [
              "options"
            ]
          }
        }
      ]
    },
    "RoleWeighting": {
      "type": "object",
      "additionalProperties": false,
      "description": "Tabulation hint. The voting infrastructure publishes raw participation only (see §7.3). These keys describe how the voting authority intends to interpret results.",
      "properties": {
        "drep": {
          "type": "string",
          "enum": [
            "CredentialBased",
            "StakeBased"
          ]
        },
        "pool": {
          "type": "string",
          "enum": [
            "CredentialBased",
            "StakeBased",
            "PledgeBased"
          ]
        },
        "stake": {
          "type": "string",
          "enum": [
            "CredentialBased",
            "StakeBased"
          ]
        }
      }
    },
    "EkklesiaExtension": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "namespace",
        "votingAuthority",
        "context",
        "acceptedCredentials",
        "merkleRoot",
        "ballotIpfsCid",
        "votingWindow"
      ],
      "properties": {
        "namespace": {
          "type": "string",
          "minLength": 1,
          "description": "Fingerprint source. See §1.1: fingerprint = blake2b_224(utf8(namespace))."
        },
        "votingAuthority": {
          "type": "string",
          "description": "Informational bech32 address of the intended voting authority. The on-chain (600) datum records the middleware's admin address, not this value, so this field is advisory metadata on IPFS only."
        },
        "context": {
          "type": "string",
          "const": "hydra-head"
        },
        "acceptedCredentials": {
          "type": "array",
          "minItems": 1,
          "uniqueItems": true,
          "items": {
            "type": "string",
            "enum": [
              "drep",
              "pool",
              "calidus",
              "stake",
              "stake_test"
            ]
          },
          "description": "Bech32 HRPs whose holders are permitted to register for this ballot."
        },
        "merkleRoot": {
          "type": "string",
          "pattern": "^[0-9a-f]{64}$",
          "description": "blake2b_256 merkle root over the questions, 64 lowercase hex. Same value as content_hash in the (600) datum."
        },
        "ballotIpfsCid": {
          "type": "string",
          "minLength": 1,
          "description": "Self-referential IPFS CID of this very document, written in by the middleware after the document is pinned."
        },
        "votingWindow": {
          "type": "object",
          "additionalProperties": false,
          "required": [
            "open",
            "close"
          ],
          "properties": {
            "open": {
              "type": "string",
              "format": "date-time",
              "description": "ISO-8601 UTC. Also the timelock anchor for the (600)/(601) minting policy (see §1.3)."
            },
            "close": {
              "type": "string",
              "format": "date-time",
              "description": "ISO-8601 UTC."
            }
          }
        }
      }
    }
  }
}
```

Constraints that cannot be expressed in JSON Schema alone (and that
implementations **MUST** enforce in addition to schema validation):

1. For every `IntegerGrid`, `(max - min)` **MUST** be a non-negative integer
   multiple of `step` (or of 1 if `step` is omitted).
2. For a `multi-choice` question, `minSelections` (if present) **MUST** be ≤
   `maxSelections` (if present), and both **MUST** be ≤ `options.length`.
3. For a `ranked` question, `rankCount` (if present) **MUST** be ≤
   `options.length`.
4. For a `likert` question, the `ratingRange` **MUST** be wide enough to
   meaningfully accommodate per-option ratings; voters submit exactly one rating
   per non-abstain option (see §3.4).
5. `votingWindow.close` **MUST** be strictly later than `votingWindow.open`.
6. `endEpoch` **MUST** correspond to a Cardano epoch whose end is at or after
   `votingWindow.close`.
7. `acceptedCredentials` **MUST** be a subset of the credential HRPs recognized
   in §5.1.

#### 2.3. Ballot content merkle tree

A merkle tree of the ballot content **MUST** be constructed with one leaf per
question:

- **Leaf name**: `questionId`.
- **Leaf content hash**: `blake2b_256(JSON.stringify(question))` over the
  *entire* `BallotQuestion` object, using the compact serialization of §7.7
  (no whitespace, key order preserved), including the optional `contentHash`
  field (§3.1) when present.
- **Leaf hash**: `blake2b_256(0x00 || leafContentHash || utf8(questionId))`
  (`content+path` mode, as in §7.4).
- **Root**: stored as `content_hash` in the (600) on-chain datum.

This allows auditors to verify that the ballot definition on IPFS matches what
was committed on-chain, without storing the full definition on-chain. Any
per-question off-chain supplementary content is bound to `content_hash`
indirectly: the question's `contentHash` field is hashed into the leaf along
with every other question field, so tampering with the off-chain blob (and
updating `contentHash` to match) changes the leaf and breaks the merkle root.

#### 2.4. Extensibility and unknown fields

In `specVersion 0.3.0` the JSON Schemas in this CIP are **strict**: every object
sets `additionalProperties: false`, and a document carrying fields not defined
here is non-conforming. Producers emit only the defined fields, so the hash of
each artifact (§7.7) is taken over a known, closed shape.

`specVersion 0.4.0` opens this up: schemas move to `additionalProperties: true`
and conforming implementations **MUST** accept and **preserve** unknown fields
through every transform, so extension data survives into the bytes that are
hashed (a stripped field would change `content_hash`, `vote_hash`, or
`results_hash` and break verification). The extension model and its namespacing
rules are introduced in 0.4.0 (see §8.2). Until then, implementations **MUST**
treat unknown fields as a validation failure.

### 3. Question and answer format

#### 3.1. Ballot question

Each question in the ballot definition **MUST** include:

| Field           | Type                           | Required | Description                                                                                                                                                                                                          |
|-----------------|--------------------------------|----------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `questionId`    | string                         | Yes      | Unique identifier within this ballot                                                                                                                                                                                 |
| `question`      | string                         | Yes      | The question text                                                                                                                                                                                                    |
| `description`   | string                         | No       | Extended description                                                                                                                                                                                                 |
| `method`        | VoteMethod (§3.2)              | Yes      | Voting method, determines selection shape                                                                                                                                                                            |
| `options`       | BallotOption[]                 | Varies   | Available choices (all methods except `range`)                                                                                                                                                                       |
| `minSelections` | integer                        | No       | Minimum selections (multi-choice; default 1)                                                                                                                                                                         |
| `maxSelections` | integer                        | No       | Maximum selections (multi-choice; default `options.length`)                                                                                                                                                          |
| `valueRange`    | `{ min, max, step? }`          | Varies   | Valid integer grid for the `range` method (`step` defaults to 1)                                                                                                                                                     |
| `rankCount`     | integer                        | No       | How many options must be ranked (ranked; defaults to `options.length`)                                                                                                                                               |
| `budget`        | integer                        | Varies   | Total points to distribute (weighted)                                                                                                                                                                                |
| `ratingRange`   | `{ min, max, step? }`          | Varies   | Discrete integer rating scale for the `likert` method                                                                                                                                                                |
| `requireAnswer` | boolean                        | No       | If `true`, `abstain: true` is rejected on this question (default `false`)                                                                                                                                            |
| `contentHash`   | string (64-char lowercase hex) | No       | Optional `blake2b_256` of the question's off-chain content blob (rationale, references, option detail). When present, participates in the question's merkle leaf and therefore in `content_hash` on the (600) datum. |

Where `BallotOption` is:

```json
{
  "label": "Approve",
  "value": 1
}
```

`value` is always an integer.

#### 3.2. Vote methods

Seven voting methods are defined:

| Method          | Description                                          | CIP-179 URI                                       |
|-----------------|------------------------------------------------------|---------------------------------------------------|
| `binary`        | Yes / No / Abstain (fixed options)                   | `urn:cardano:poll-method:single-choice:v1`        |
| `single-choice` | Select exactly one option                            | `urn:cardano:poll-method:single-choice:v1`        |
| `multi-choice`  | Select between `minSelections` and `maxSelections`   | `urn:cardano:poll-method:multi-select:v1`         |
| `range`         | Submit an integer on the `valueRange` grid           | `urn:cardano:poll-method:numeric-range:v1`        |
| `ranked`        | Rank exactly `rankCount` options by preference       | `urn:ekklesia:poll-method:ranked-choice:v1`       |
| `weighted`      | Distribute `budget` points across options            | `urn:ekklesia:poll-method:weighted-allocation:v1` |
| `likert`        | Rate every option on the discrete `ratingRange` grid | `urn:ekklesia:poll-method:likert:v1`              |

The `binary`, `single-choice`, `multi-choice`, and `range` methods map to
standard [CIP-179][CIP-0179] method URIs. The `ranked`, `weighted`, and `likert`
methods use Ekklesia-namespaced URIs as extensions to [CIP-179][CIP-0179].
The [CIP-179][CIP-0179] URI table above reflects the state
of [CIP-179][CIP-0179] at this CIP's draft date; if [CIP-179][CIP-0179]
finalizes with different URIs, this CIP's URI column will be revised to align.

#### 3.3. Role weighting

Ballots **MAY** specify role-based weighting hints aligned
with [CIP-179][CIP-0179]:

```json
{
  "drep": "CredentialBased | StakeBased",
  "pool": "CredentialBased | StakeBased | PledgeBased",
  "stake": "CredentialBased | StakeBased"
}
```

The three keys correspond to the canonical role-space defined in §5.1
(`drep`, `pool`, `stake`). Role is determined by the voter's credential HRP;
calidus hot keys collapse into the `pool` role.

> **Important.** Role weighting expresses how results *may* be interpreted by
> the voting authority at tabulation time. The voting infrastructure itself
> treats every voter as one voter casting one vote. Weighting is applied at the
> tabulation layer, not at the voting layer. See §7.3 for the consequence:
> published results carry raw participation counts only, not pre-weighted
> tallies.

Legacy role identifiers (uppercase forms such as `DRep` / `SPO`, and the `CC`
role) are reserved and rejected at ballot prepare time.

#### 3.4. Vote selection

Each voter's answer to a question is encoded as a `VoteSelection` with a unified
`selection` field. The shape of `selection` is determined by the question's
`method`:

```typescript
type VoteSelection = {
    questionId: string;
    // Either abstain or selection, mutually exclusive. Abstain is allowed
    // by default; rejected only when the question sets requireAnswer: true.
    abstain?: true;
    selection?:
        | number[]            // binary, single-choice, multi-choice, ranked, range (length 1)
        | { option: number, value: number }[]  // weighted, likert
};
```

Per method:

- `binary`, `single-choice`: `selection: number[]` of length 1.
- `multi-choice`: `selection: number[]`, length in
  `[minSelections, maxSelections]`, no duplicates.
- `range`: `selection: number[]` of length 1, value on the `valueRange`
  grid.
- `ranked`: `selection: number[]` of length exactly `rankCount`, no duplicates,
  in preference order (index 0 = first preference).
- `weighted`: `selection: { option, value }[]`, no duplicate `option`s, every
  `value` a non-negative integer, sum of `value`s equal to
  `budget`.
- `likert`: `selection: { option, value }[]`, exactly one entry per non-abstain
  option, each `value` on the `ratingRange` grid.

Exactly one of `abstain: true` or `selection` **MUST** be present per question.

### 4. Ballot Instance Token (601)

The (601) token is minted alongside the (600) token on L1, then committed into a
Hydra head for the voting period. After voting concludes, it returns to L1
carrying the final results.

#### 4.1. On-chain datum

The (601) token **MUST** carry an inline datum in Plutus `Constr 0` format
wrapping a positional four-field list and a schema version integer.

**CDDL:**

```cddl
ballot_result_datum = #6.121([fields, version])

fields = [
  ballot_id:    bstr,   ; UTF-8 ballot identifier (ULID or tx hash). Empty bytes pre-finalize.
  results_hash: bstr,   ; UTF-8 of 64-char hex (blake2b_256 of FullResults JSON). Empty bytes pre-finalize.
  evidence_cid: bstr,   ; UTF-8 of the IPFS directory CID. Empty bytes pre-finalize.
  merkle_root:  bstr    ; UTF-8 of 64-char hex (merkle root of vote evidence). Empty bytes pre-finalize.
]

version = uint          ; datum schema version (see §8)
```

The datum is intentionally compact. The total voter count, per-role voter
counts, excluded voters, and per-question tallies all live in the
`results.json` file on IPFS (referenced by `evidence_cid`). The on-chain datum
carries only the four cryptographic commitments needed to bind the off-chain
artifacts to the on-chain record.

#### 4.2. Datum evolution

The (601) datum is initialized empty at mint time and populated during
finalization while the Hydra head is still open:

| Phase      | `fields`                                               | `version` |
|------------|--------------------------------------------------------|-----------|
| Minted     | `[bytes(""), bytes(""), bytes(""), bytes("")]`         | 1         |
| In-head    | unchanged                                              | 1         |
| Finalized  | `[ballot_id, results_hash, evidence_cid, merkle_root]` | 1         |
| Settled L1 | same as finalized                                      | 1         |

The finalization update **MUST** occur while the Hydra head is still open.
Closing the head prevents further datum updates.

### 5. Voter registration tokens

Individual voter participation is tracked via per-voter tokens minted inside the
Hydra head under a native-script policy controlled by the voting authority.

#### 5.1. Voter token name

The voter token asset name is 29 bytes (58 hex characters):

```text
token_name = credential_prefix (1 byte) || credential_hash (28 bytes)

credential_hash = blake2b_224(bech32_decode(voter_id).data)
```

Credential prefix mapping:

| Bech32 HRP   | Prefix byte | Canonical role |
|--------------|-------------|----------------|
| `drep`       | `0x22`      | `drep`         |
| `pool`       | `0x06`      | `pool`         |
| `calidus`    | `0x06`      | `pool`         |
| `stake`      | `0xe0`      | `stake`        |
| `stake_test` | `0xe0`      | `stake`        |

Calidus hot keys ([CIP-151][CIP-0151]) represent the SPO behind them and share
the `pool` prefix byte and `pool` canonical role. The `stake_test` HRP is the
testnet form of the stake credential and collapses to the same role.

Payment-only credentials (`addr` / `addr_test`) **MUST NOT** be used as voter
IDs. Voters with only a payment credential register via their stake credential
instead.

#### 5.2. Voter datum

Each voter token carries an inline datum. The shape is `Constr 0` with five
positional fields directly (no nested fields list):

**CDDL:**

```cddl
voter_datum = #6.121([voter_id, version, merkle_root, vote_hash, ipfs_cid])

voter_id    = bstr   ; voter token asset name (UTF-8 of 58-char hex; 29 raw bytes)
version     = uint   ; monotonic vote nonce: 0 on register, N≥1 on cast/update
merkle_root = bstr   ; UTF-8 of 64-char hex (blake2b_256 of signedPayload JSON). Empty bytes on register.
vote_hash   = bstr   ; UTF-8 of 64-char hex (blake2b_256 of VoteEvidence JSON). Empty bytes on register.
ipfs_cid    = bstr   ; UTF-8 IPFS CID of VoteEvidence. Empty bytes on register.
```

The `version` field starts at 0 (registration-only) or 1 (first vote) and
increments with each subsequent vote update. This provides replay protection: a
vote with a version less than or equal to the current on-chain version is
rejected.

The `merkle_root` field binds the vote to a specific payload via
`blake2b_256(JSON.stringify(signedVotePayload))`. The voter's
[CIP-8][CIP-0008] signature covers this root, creating a nonrepudiable link
between identity, choices, and the on-chain record.

#### 5.3. Voter token lifecycle

1. **Register.** Mint voter token with `version = 0` and all three hash fields
   as empty bytes. The voter is now eligible to cast but has not yet submitted a
   vote.
2. **Vote-and-register.** Mint voter token with `version = 1` and the hash
   fields populated by the first vote. Atomic combination of registration plus
   first cast.
3. **Cast vote.** Update an existing voter token's datum: increment
   `version`, replace the hash fields. No minting occurs after the initial
   registration step.
4. **Settlement burn.** All voter tokens are burned during finalization, after
   their evidence has been captured into the merkle tree.

### 6. Vote evidence and signatures

#### 6.1. Signed vote payload

The voter signs the following payload using [CIP-8][CIP-0008] message signing
(the Cardano profile of `COSE_Sign1`). Continuing the §2.2.1 example ballot, a
voter who approves the budget envelope and allocates `30 / 40 / 20 / 10` across
the four tracks signs:

```json
{
  "ballotId": "00259a2072386e56d8c3e598bfb4b1b003e972cbcdadbce07e0b779330082077",
  "nonce": 1,
  "votes": [
    {
      "questionId": "budget-envelope-2026",
      "selection": [
        1
      ]
    },
    {
      "questionId": "track-allocation-2026",
      "selection": [
        {
          "option": 1,
          "value": 30
        },
        {
          "option": 2,
          "value": 40
        },
        {
          "option": 3,
          "value": 20
        },
        {
          "option": 4,
          "value": 10
        }
      ]
    }
  ]
}
```

`ballotId` is the (601) ballot-instance asset name from §1.2 (i.e., the on-chain
identifier for this specific ballot). `nonce` matches the voter datum's
`version` field for this submission (§5.2). The very first cast after
registration uses `nonce = 1`. A subsequent revision of the same vote increments
to `nonce = 2`, and so on.

The signature **MUST** conform to [CIP-8][CIP-0008] message signing. The
`COSE_Sign1` envelope contains:

- Protected header: EdDSA algorithm and voter address bytes, per CIP-8's header
  conventions.
- Payload: `blake2b_256` hash of the JSON-serialized `SignedVotePayload`.
- Signature: Ed25519 signature.

CIP-8 defines the Cardano-specific conventions on top of `COSE_Sign1` (address
encoding in protected headers, supported algorithms, hashable payload form).
Implementations **MUST** follow CIP-8 directly, not derive conformance from the
underlying COSE standards, since the two may diverge over time.

`votes[i].selection` shape is method-dependent per §3.4 (`number[]` for
`single-choice` and `{ option, value }[]` for `weighted` above). A voter who
chose to skip the second question instead would submit
`{ "questionId": "track-allocation-2026", "abstain": true }` in place of the
weighted selection, permitted whenever the question does not set
`requireAnswer: true`.

#### 6.2. Vote evidence (IPFS)

Each vote is accompanied by a full evidence file pinned to IPFS. The schema is
[CIP-179][CIP-0179] surveyResponse core (`specVersion`, `responderRole`,
`answers`) plus an Ekklesia extension block.

##### 6.2.1. Key-based voter (single witness)

Continuing the §6.1 example, the same DRep voter, same ballot:

```json
{
  "specVersion": "0.3.0",
  "responderRole": "drep",
  "answers": [
    {
      "questionId": "budget-envelope-2026",
      "selection": [
        1
      ]
    },
    {
      "questionId": "track-allocation-2026",
      "selection": [
        {
          "option": 1,
          "value": 30
        },
        {
          "option": 2,
          "value": 40
        },
        {
          "option": 3,
          "value": 20
        },
        {
          "option": 4,
          "value": 10
        }
      ]
    }
  ],
  "ekklesia": {
    "voterId": "drep1ytdnkw2l4q7uy2d7d7sj9fhgsun56zg2uleqlfqx2lvcc6gusnw9c",
    "credentialHrp": "drep",
    "nonce": 1,
    "signedPayload": {
      "ballotId": "00259a2072386e56d8c3e598bfb4b1b003e972cbcdadbce07e0b779330082077",
      "nonce": 1,
      "votes": [
        {
          "questionId": "budget-envelope-2026",
          "selection": [
            1
          ]
        },
        {
          "questionId": "track-allocation-2026",
          "selection": [
            {
              "option": 1,
              "value": 30
            },
            {
              "option": 2,
              "value": 40
            },
            {
              "option": 3,
              "value": 20
            },
            {
              "option": 4,
              "value": 10
            }
          ]
        }
      ]
    },
    "witnesses": [
      {
        "coseSign1Hex": "845882a20127044228ac94651c8a97c761416d859d2e1f8b642bd25163a0966b84dd59e8737102fba166686173686564f458fc57a3be7e756f0e2de511d86bf740b3cd0ac5fb57d683bbe382cdabd8e17c1e61191153bac41db7218d0b5b34ced7ad71a36ec50680e6124bf53788e09b12d90e38e994e01b2f5a7acf8af355febcb21891611f11509819a4a805d8bab4b789",
        "coseKeyHex": "a401010327200621582028ac94651c8a97c761416d859d2e1f8b642bd25163a0966b84dd59e8737102fb",
        "key": "a97132992280ab675b8d55ef8368dcd30bd36fa6622524840859b2af",
        "signature": "61191153bac41db7218d0b5b34ced7ad71a36ec50680e6124bf53788e09b12d90e38e994e01b2f5a7acf8af355febcb21891611f11509819a4a805d8bab4b789"
      }
    ],
    "merkleProof": {
      "root": "edc5b3a0915f745a6574e9d2c12cd199ee17518860b1e79e63eb3cd95395987e",
      "steps": [
        {
          "siblingHex": "675b30335a3c0c255b225f92ab1b098c25d7e38d9f745968acea7532d5cdda1a"
        },
        {
          "siblingHex": "545a7da777c6db9e85fb15a2e99ca21eb9abc718aa3a6277dd7ba86fbb88e681"
        }
      ]
    }
  }
}
```

Within `witnesses[0]`:

- `coseSign1Hex` is the full COSE_Sign1 envelope hex from the
  voter's [CIP-30][CIP-0008]
  signing call.
- `coseKeyHex` is the COSE_Key (EdDSA, Ed25519) corresponding to the signing
  key.
- `key` is the 28-byte blake2b_224 of the Ed25519 public key (56 hex chars). For
  DRep voters this matches the `credential_hash` portion of the voter token
  name (§5.1).
- `signature` is the raw 64-byte Ed25519 signature extracted from the
  COSE_Sign1 (128 hex chars).

`responderRole` is the canonical lowercase role (`drep`, `pool`, or
`stake`) derived server-side from `credentialHrp`. The voting infrastructure
does not accept a client-supplied `responderRole`.

##### 6.2.2. Script-based voter (multisig)

For voters with a script credential (e.g., multisig DReps using
the [CIP-129][CIP-0129]
`0x23`
credential type), the evidence file additionally includes a `nativeScript` field
describing the script that must be satisfied, and the `witnesses` array contains
one COSE_Sign1 entry per cosigner. Each cosigner signs the same canonical
`signedPayload`. The script-satisfaction check (e.g. "any 2 of 3") is performed
against the witness set during evidence assembly.

A 2-of-3 multisig example replaces the `witnesses` array of §6.2.1 with two
cosigner witnesses and adds a `nativeScript` field. The top-level fields outside
`ekklesia` (`specVersion`, `responderRole`,
`answers`) and the `ekklesia` fields not shown here (`voterId`,
`credentialHrp`, `nonce`, `signedPayload`, `merkleProof`) are identical in shape
to §6.2.1; only the changed paths are reproduced:

```json
{
  "ekklesia": {
    "witnesses": [
      {
        "coseSign1Hex": "845882a201270442ec4f2d896120bf9521f8c8b8fddc3525e8110754124eb7e41f5564b783c78ef9a166686173686564f4589763a3c11e51da62941d2d2090c48e27a8b93993c0a44e950f9856cc0ebbdda8980ebe5bea06db4f120c39b7c5d14b8085638dcedc6f201e99f1130fc1c46e1df3d97115955867a30b6469adb582c0bc1d05b6c6e8ab72d00015acc72163f8ff",
        "coseKeyHex": "a4010103272006215820ec4f2d896120bf9521f8c8b8fddc3525e8110754124eb7e41f5564b783c78ef9",
        "key": "16e94a4f2c309a82adb3b7f5e78bfaae0b2466aeeb4a14e135a2d949",
        "signature": "980ebe5bea06db4f120c39b7c5d14b8085638dcedc6f201e99f1130fc1c46e1df3d97115955867a30b6469adb582c0bc1d05b6c6e8ab72d00015acc72163f8ff"
      },
      {
        "coseSign1Hex": "845882a201270442b8d909ad55319f09d1d23c7f193743309e2cc4a6611dc21a46757ea77cca6868a166686173686564f45899c091435afd3e0c8c1f44726203d45b851f0f796cecfac9004eef9b64c9756f569e83975ed99b3f5247e248948d69a5e8c8e451adf174cb5ada5cd388198a128eff662a42b876be0b752cc91d12b170a97a0d462e59041c26268e225e22825f",
        "coseKeyHex": "a4010103272006215820b8d909ad55319f09d1d23c7f193743309e2cc4a6611dc21a46757ea77cca6868",
        "key": "84df113fe58eb1c271836ae4b1d6af842a666450459703bdb6177710",
        "signature": "569e83975ed99b3f5247e248948d69a5e8c8e451adf174cb5ada5cd388198a128eff662a42b876be0b752cc91d12b170a97a0d462e59041c26268e225e22825f"
      }
    ],
    "nativeScript": {
      "type": "atLeast",
      "required": 2,
      "scripts": [
        {
          "type": "sig",
          "keyHash": "16e94a4f2c309a82adb3b7f5e78bfaae0b2466aeeb4a14e135a2d949"
        },
        {
          "type": "sig",
          "keyHash": "84df113fe58eb1c271836ae4b1d6af842a666450459703bdb6177710"
        },
        {
          "type": "sig",
          "keyHash": "5d6be0c16c332b2d7dc9ff2d5c016649731a57b5380fd39203133214"
        }
      ]
    }
  }
}
```

The third `keyHash` in the `nativeScript.scripts` list corresponds to the
non-signing third cosigner; under the `atLeast: 2` policy the two witnesses
shown are sufficient.

##### 6.2.3. Calidus hot-key voter ([CIP-151][CIP-0151])

For an SPO voting via a calidus hot key, `credentialHrp` is `calidus`, the
canonical role is `pool`, and the evidence file additionally carries a
`calidusDeclaration` field identifying the hot key (`calidusId`) that signed on
behalf of the pool. Top-level fields outside `ekklesia` and the unchanged
`ekklesia` fields are as in §6.2.1; only the changed paths are reproduced:

```json
{
  "ekklesia": {
    "voterId": "calidus1uyk7m2x5c9hsa3vgyq2ld6tvr8z3p7q4w9n0e6h2m4j8d1f3y5a",
    "credentialHrp": "calidus",
    "calidusDeclaration": {
      "calidusId": "calidus1uyk7m2x5c9hsa3vgyq2ld6tvr8z3p7q4w9n0e6h2m4j8d1f3y5a"
    }
  }
}
```

#### 6.3. Vote-evidence JSON Schema

The following JSON Schema (Draft 2020-12) is normative. The
`vote-{tokenName}-v{version}.json` evidence files in the evidence directory
**MUST** validate against this schema.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://docs.ekklesia.vote/cip/hydra-voting-tokens/vote-evidence.schema.json",
  "title": "VoteEvidence",
  "description": "Per-voter evidence record pinned to IPFS. blake2b_256 of its compact serialization (§7.7) equals the on-chain vote_hash recorded in the voter datum (§5.2).",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "specVersion",
    "responderRole",
    "answers",
    "ekklesia"
  ],
  "properties": {
    "specVersion": {
      "type": "string",
      "pattern": "^\\d+\\.\\d+\\.\\d+$"
    },
    "responderRole": {
      "type": "string",
      "enum": [
        "drep",
        "pool",
        "stake"
      ],
      "description": "Canonical role derived server-side from credentialHrp. Calidus voters MUST report 'pool'."
    },
    "answers": {
      "type": "array",
      "minItems": 1,
      "items": {
        "$ref": "#/$defs/VoteSelection"
      }
    },
    "ekklesia": {
      "$ref": "#/$defs/EkklesiaExtension"
    }
  },
  "$defs": {
    "Hex": {
      "type": "string",
      "pattern": "^[0-9a-f]*$"
    },
    "Hex32": {
      "type": "string",
      "description": "32-byte value as 64 lowercase hex characters.",
      "pattern": "^[0-9a-f]{64}$"
    },
    "Hex28": {
      "type": "string",
      "description": "28-byte value as 56 lowercase hex characters.",
      "pattern": "^[0-9a-f]{56}$"
    },
    "Hex64": {
      "type": "string",
      "description": "64-byte value as 128 lowercase hex characters.",
      "pattern": "^[0-9a-f]{128}$"
    },
    "Bech32": {
      "type": "string",
      "pattern": "^[a-z0-9_]+1[a-z0-9]+$",
      "description": "Bech32-encoded identifier (voter ID, pool ID, etc.)."
    },
    "IpfsCid": {
      "type": "string",
      "minLength": 1,
      "description": "IPFS CID (v0 'Qm...' or v1 'bafy...')."
    },
    "SelectionEntry": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "option",
        "value"
      ],
      "properties": {
        "option": {
          "type": "integer"
        },
        "value": {
          "type": "integer",
          "minimum": 0
        }
      }
    },
    "VoteSelection": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "questionId"
      ],
      "properties": {
        "questionId": {
          "type": "string",
          "minLength": 1
        },
        "abstain": {
          "const": true
        },
        "selection": {
          "oneOf": [
            {
              "type": "array",
              "items": {
                "type": "integer"
              }
            },
            {
              "type": "array",
              "items": {
                "$ref": "#/$defs/SelectionEntry"
              }
            }
          ]
        }
      },
      "oneOf": [
        {
          "required": [
            "abstain"
          ],
          "not": {
            "required": [
              "selection"
            ]
          }
        },
        {
          "required": [
            "selection"
          ],
          "not": {
            "required": [
              "abstain"
            ]
          }
        }
      ]
    },
    "SignedVotePayload": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "ballotId",
        "nonce",
        "votes"
      ],
      "properties": {
        "ballotId": {
          "$ref": "#/$defs/Hex32"
        },
        "nonce": {
          "type": "integer",
          "minimum": 0
        },
        "votes": {
          "type": "array",
          "minItems": 1,
          "items": {
            "$ref": "#/$defs/VoteSelection"
          }
        }
      }
    },
    "CoseWitness": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "coseSign1Hex",
        "coseKeyHex",
        "key",
        "signature"
      ],
      "properties": {
        "coseSign1Hex": {
          "$ref": "#/$defs/Hex"
        },
        "coseKeyHex": {
          "$ref": "#/$defs/Hex"
        },
        "key": {
          "$ref": "#/$defs/Hex28"
        },
        "signature": {
          "$ref": "#/$defs/Hex64"
        }
      }
    },
    "NativeScript": {
      "oneOf": [
        {
          "type": "object",
          "additionalProperties": false,
          "required": [
            "type",
            "keyHash"
          ],
          "properties": {
            "type": {
              "const": "sig"
            },
            "keyHash": {
              "$ref": "#/$defs/Hex28"
            }
          }
        },
        {
          "type": "object",
          "additionalProperties": false,
          "required": [
            "type",
            "scripts"
          ],
          "properties": {
            "type": {
              "enum": [
                "all",
                "any"
              ]
            },
            "scripts": {
              "type": "array",
              "items": {
                "$ref": "#/$defs/NativeScript"
              }
            }
          }
        },
        {
          "type": "object",
          "additionalProperties": false,
          "required": [
            "type",
            "required",
            "scripts"
          ],
          "properties": {
            "type": {
              "const": "atLeast"
            },
            "required": {
              "type": "integer",
              "minimum": 1
            },
            "scripts": {
              "type": "array",
              "items": {
                "$ref": "#/$defs/NativeScript"
              }
            }
          }
        },
        {
          "type": "object",
          "additionalProperties": false,
          "required": [
            "type",
            "slot"
          ],
          "properties": {
            "type": {
              "enum": [
                "before",
                "after"
              ]
            },
            "slot": {
              "type": "integer",
              "minimum": 0
            }
          }
        }
      ]
    },
    "CalidusDeclaration": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "calidusId"
      ],
      "description": "Identifies the CIP-151 calidus hot key that signed on behalf of a pool. The pool binding is resolved by on-chain lookup of calidusId (a self-contained binding declaration arrives in specVersion 0.4.0).",
      "properties": {
        "calidusId": {
          "$ref": "#/$defs/Bech32"
        }
      }
    },
    "MerkleProofSteps": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "root",
        "steps"
      ],
      "properties": {
        "root": {
          "$ref": "#/$defs/Hex32"
        },
        "steps": {
          "type": "array",
          "items": {
            "type": "object",
            "additionalProperties": false,
            "required": [
              "siblingHex"
            ],
            "properties": {
              "siblingHex": {
                "$ref": "#/$defs/Hex32"
              }
            }
          }
        }
      }
    },
    "EkklesiaExtension": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "voterId",
        "credentialHrp",
        "nonce",
        "signedPayload",
        "witnesses",
        "merkleProof"
      ],
      "properties": {
        "voterId": {
          "$ref": "#/$defs/Bech32"
        },
        "credentialHrp": {
          "type": "string",
          "enum": [
            "drep",
            "pool",
            "calidus",
            "stake",
            "stake_test"
          ]
        },
        "nonce": {
          "type": "integer",
          "minimum": 0
        },
        "signedPayload": {
          "$ref": "#/$defs/SignedVotePayload"
        },
        "witnesses": {
          "type": "array",
          "minItems": 1,
          "items": {
            "$ref": "#/$defs/CoseWitness"
          }
        },
        "nativeScript": {
          "$ref": "#/$defs/NativeScript"
        },
        "calidusDeclaration": {
          "$ref": "#/$defs/CalidusDeclaration"
        },
        "merkleProof": {
          "$ref": "#/$defs/MerkleProofSteps"
        }
      },
      "allOf": [
        {
          "if": {
            "properties": {
              "credentialHrp": {
                "const": "calidus"
              }
            },
            "required": [
              "credentialHrp"
            ]
          },
          "then": {
            "required": [
              "calidusDeclaration"
            ]
          }
        }
      ]
    }
  }
}
```

Constraints that JSON Schema cannot express and that implementations **MUST**
enforce in addition:

1. The `signedPayload.votes` array **MUST** be byte-identical (under the compact
   serialization of §7.7) to the top-level `answers` array. The signed bytes are
   what the voter committed to; `answers` is a convenience copy for CIP-179
   compatibility.
2. `signedPayload.nonce` **MUST** equal `ekklesia.nonce`, which **MUST** equal
   `version`
   in the voter datum (§5.2) at submission time.
3. For each `CoseWitness`, `key` **MUST** equal
   `blake2b_224(public_key)` where the public key is recovered from the
   [CIP-8][CIP-0008] (`COSE_Sign1`) envelope. For key-based voters
   (`witnesses` has length 1 and `nativeScript` is absent), the `COSE_Sign1`
   signer key hash **MUST** equal the credential-hash portion of `voterId`'s
   bech32 data (the same value used as the voter token name's 28-byte suffix per
   §5.1).
4. For script-based voters, `witnesses[*].key` **MUST** each satisfy at least
   one
   `sig` leaf in `nativeScript`, and the satisfied set **MUST** meet the
   script's
   `all`/`any`/`atLeast` requirements.
5. `merkleProof.root` **MUST** equal `merkle_root` in the (601) datum
   (§4.1) after settlement; before settlement, `merkleProof.root`
   **MAY** be absent or zero-valued.

### 7. Settlement and results

#### 7.1. Finalization (in-head)

Before the Hydra head is closed, the voting authority:

1. Captures all voter token datums from the head's UTxO set.
2. Verifies each voter's signature against their signed payload.
3. Constructs a merkle tree of all vote evidence (one leaf per voter).
4. Pins the complete evidence directory to IPFS.
5. Updates the (601) token's datum with `ballot_id`, `results_hash`,
   `evidence_cid`, and `merkle_root`.
6. Burns all voter tokens.

The (601) datum carries only these four commitments; voter counts, per-role
breakdowns, exclusions, and tallies all live in
`results.json` on IPFS, anchored by `results_hash`.

#### 7.2. Evidence directory structure

The evidence directory pinned to IPFS **MUST** contain:

```text
evidence/
  results.json                       -- FullResults object (§7.3)
  proof-package.json                 -- Merkle proof package (§7.6)
  pre-burn-ledger.json               -- Snapshot of every voter token minted
                                        in the head, captured before the
                                        settlement burn (§7.8 Step 10)
  exclusions.json                    -- Voters excluded with reasons (omitted
                                        when there are none)
  vote-{tokenName}-v{version}.json   -- Per-voter vote evidence (one file per
                                        voter, in the directory root; the
                                        {version} is the final on-chain nonce)
  proofs/{tokenName}.json            -- Per-voter merkle inclusion proof
  history/{voterId}.json             -- Per-voter vote-update history chain
```

Per-voter evidence files live in the directory **root** (not a `votes/`
sub-directory) and are named `vote-{tokenName}-v{version}.json`. The
`proofs/` files are keyed by the voter **token name** (the 58-hex asset name of
§5.1). `pre-burn-ledger.json` records every voter token observed in the head
before burning, and is the reference set for the silent-suppression check in
§7.8.

#### 7.3. Full results object

Continuing the §2.2.1 example ballot, after a ballot with 1 000 voters
(600 DReps, 250 SPOs, 150 stakeholders) the published `results.json`
looks as follows. The single-choice Q1 received 900 explicit selections
(580 Approve, 270 Reject, 50 "Abstain" as an option value) plus 100 voters who
set `abstain: true`; the weighted Q2 received 900 explicit allocations plus 100
abstainers, distributing 90 000 points across the four tracks.

```json
{
  "specVersion": "0.3.0",
  "ballotId": "00259a2072386e56d8c3e598bfb4b1b003e972cbcdadbce07e0b779330082077",
  "tallies": {
    "budget-envelope-2026": {
      "results": [
        {
          "id": "1",
          "label": "Approve",
          "count": 580,
          "votingPower": 0
        },
        {
          "id": "2",
          "label": "Reject",
          "count": 270,
          "votingPower": 0
        },
        {
          "id": "0",
          "label": "Abstain",
          "count": 50,
          "votingPower": 0
        },
        {
          "id": "abstain",
          "count": 100,
          "votingPower": 0
        }
      ],
      "resultsByGroup": {
        "drep": {
          "totalVotes": 600,
          "results": [
            {
              "id": "1",
              "label": "Approve",
              "count": 370,
              "votingPower": 0
            },
            {
              "id": "2",
              "label": "Reject",
              "count": 170,
              "votingPower": 0
            },
            {
              "id": "0",
              "label": "Abstain",
              "count": 30,
              "votingPower": 0
            },
            {
              "id": "abstain",
              "count": 30,
              "votingPower": 0
            }
          ]
        },
        "pool": {
          "totalVotes": 250,
          "results": [
            {
              "id": "1",
              "label": "Approve",
              "count": 140,
              "votingPower": 0
            },
            {
              "id": "2",
              "label": "Reject",
              "count": 70,
              "votingPower": 0
            },
            {
              "id": "0",
              "label": "Abstain",
              "count": 15,
              "votingPower": 0
            },
            {
              "id": "abstain",
              "count": 25,
              "votingPower": 0
            }
          ]
        },
        "stake": {
          "totalVotes": 150,
          "results": [
            {
              "id": "1",
              "label": "Approve",
              "count": 70,
              "votingPower": 0
            },
            {
              "id": "2",
              "label": "Reject",
              "count": 30,
              "votingPower": 0
            },
            {
              "id": "0",
              "label": "Abstain",
              "count": 5,
              "votingPower": 0
            },
            {
              "id": "abstain",
              "count": 45,
              "votingPower": 0
            }
          ]
        }
      }
    },
    "track-allocation-2026": {
      "results": [
        {
          "id": "1",
          "label": "Education & Outreach",
          "count": 720,
          "votingPower": 0
        },
        {
          "id": "2",
          "label": "Technical Standards",
          "count": 810,
          "votingPower": 0
        },
        {
          "id": "3",
          "label": "Developer Tools",
          "count": 645,
          "votingPower": 0
        },
        {
          "id": "4",
          "label": "Documentation & QA",
          "count": 480,
          "votingPower": 0
        },
        {
          "id": "abstain",
          "count": 100,
          "votingPower": 0
        }
      ],
      "resultsByGroup": {
        "drep": {
          "totalVotes": 600,
          "results": [],
          "weighted": {
            "results": [
              {
                "option": 1,
                "totalPoints": 16200,
                "voterCount": 432
              },
              {
                "option": 2,
                "totalPoints": 21600,
                "voterCount": 486
              },
              {
                "option": 3,
                "totalPoints": 10800,
                "voterCount": 387
              },
              {
                "option": 4,
                "totalPoints": 5400,
                "voterCount": 288
              }
            ]
          }
        },
        "pool": {
          "totalVotes": 250,
          "results": [],
          "weighted": {
            "results": [
              {
                "option": 1,
                "totalPoints": 6750,
                "voterCount": 180
              },
              {
                "option": 2,
                "totalPoints": 9000,
                "voterCount": 203
              },
              {
                "option": 3,
                "totalPoints": 4500,
                "voterCount": 161
              },
              {
                "option": 4,
                "totalPoints": 2250,
                "voterCount": 120
              }
            ]
          }
        },
        "stake": {
          "totalVotes": 150,
          "results": [],
          "weighted": {
            "results": [
              {
                "option": 1,
                "totalPoints": 4050,
                "voterCount": 108
              },
              {
                "option": 2,
                "totalPoints": 5400,
                "voterCount": 121
              },
              {
                "option": 3,
                "totalPoints": 2700,
                "voterCount": 97
              },
              {
                "option": 4,
                "totalPoints": 1350,
                "voterCount": 72
              }
            ]
          }
        }
      }
    }
  },
  "questionTallies": [
    {
      "questionId": "budget-envelope-2026",
      "method": "single-choice",
      "roleResults": {
        "raw": {
          "method": "single-choice",
          "results": [
            {
              "option": 1,
              "count": 580
            },
            {
              "option": 2,
              "count": 270
            },
            {
              "option": 0,
              "count": 50
            }
          ]
        },
        "drep": {
          "method": "single-choice",
          "results": [
            {
              "option": 1,
              "count": 370
            },
            {
              "option": 2,
              "count": 170
            },
            {
              "option": 0,
              "count": 30
            }
          ]
        },
        "pool": {
          "method": "single-choice",
          "results": [
            {
              "option": 1,
              "count": 140
            },
            {
              "option": 2,
              "count": 70
            },
            {
              "option": 0,
              "count": 15
            }
          ]
        },
        "stake": {
          "method": "single-choice",
          "results": [
            {
              "option": 1,
              "count": 70
            },
            {
              "option": 2,
              "count": 30
            },
            {
              "option": 0,
              "count": 5
            }
          ]
        }
      },
      "abstainedByRole": {
        "raw": 100,
        "drep": 30,
        "pool": 25,
        "stake": 45
      }
    },
    {
      "questionId": "track-allocation-2026",
      "method": "weighted",
      "roleResults": {
        "raw": {
          "method": "weighted",
          "results": [
            {
              "option": 1,
              "totalPoints": 27000,
              "voterCount": 720
            },
            {
              "option": 2,
              "totalPoints": 36000,
              "voterCount": 810
            },
            {
              "option": 3,
              "totalPoints": 18000,
              "voterCount": 645
            },
            {
              "option": 4,
              "totalPoints": 9000,
              "voterCount": 480
            }
          ]
        },
        "drep": {
          "method": "weighted",
          "results": [
            {
              "option": 1,
              "totalPoints": 16200,
              "voterCount": 432
            },
            {
              "option": 2,
              "totalPoints": 21600,
              "voterCount": 486
            },
            {
              "option": 3,
              "totalPoints": 10800,
              "voterCount": 387
            },
            {
              "option": 4,
              "totalPoints": 5400,
              "voterCount": 288
            }
          ]
        },
        "pool": {
          "method": "weighted",
          "results": [
            {
              "option": 1,
              "totalPoints": 6750,
              "voterCount": 180
            },
            {
              "option": 2,
              "totalPoints": 9000,
              "voterCount": 203
            },
            {
              "option": 3,
              "totalPoints": 4500,
              "voterCount": 161
            },
            {
              "option": 4,
              "totalPoints": 2250,
              "voterCount": 120
            }
          ]
        },
        "stake": {
          "method": "weighted",
          "results": [
            {
              "option": 1,
              "totalPoints": 4050,
              "voterCount": 108
            },
            {
              "option": 2,
              "totalPoints": 5400,
              "voterCount": 121
            },
            {
              "option": 3,
              "totalPoints": 2700,
              "voterCount": 97
            },
            {
              "option": 4,
              "totalPoints": 1350,
              "voterCount": 72
            }
          ]
        }
      },
      "abstainedByRole": {
        "raw": 100,
        "drep": 30,
        "pool": 25,
        "stake": 45
      }
    }
  ],
  "totalVoters": 1000,
  "headId": "d6e4c66a14cd710fe5891b78cabe147ee8c271d519b21b16444e41b9",
  "finalizedAt": "2026-06-08T00:32:14Z",
  "votersByRole": {
    "drep": 600,
    "pool": 250,
    "stake": 150
  },
  "excludedVoters": [
    {
      "tokenName": "22a97132992280ab675b8d55ef8368dcd30bd36fa6622524840859b2af",
      "reason": "evidence file missing on IPFS"
    }
  ]
}
```

`tallies` and `questionTallies` are two views of the same underlying data.
`tallies` is the backend wire shape (keyed by `questionId`), where
method-specific extension fields hang off each role bucket (the
`weighted` block on Q2's role buckets above, for example). The
`votingPower: 0` constant on every `BackendOptionResult` row is deliberate (see
the weighting note below).

`questionTallies` is the canonical auditor breakdown: a discriminated union per
method, role-bucketed, with a `"raw"` bucket aggregating across roles.
Per-method tally shapes follow the per-method `selection`
shape defined in §3.4: `OptionCount[]` for the four "options-only"
methods, `DistributionEntry[]` for `range`, a pairwise preference matrix for
`ranked`, and per-option point or rating aggregates for
`weighted` and `likert`. Statistical interpretations (mean, median, Borda
scores, etc.) are deliberately omitted; the evidence directory publishes raw
counts and downstream consumers are free to compute their own.

`abstainedByRole` records the per-role count of `abstain: true`
submissions on each question. Abstainers do not contribute to any
`MethodTally` aggregate; the `"raw"` key aggregates across all roles.

> **Important:** No weighting is applied at this layer. The voting
> infrastructure
> publishes raw participation counts only. Post-hoc stake or role weighting, if
> any, is applied by the voting authority at tabulation time using their own
> voter-power snapshots; this CIP does not standardize that step. The
> `roleWeighting` field in the ballot definition is a hint to the voting
> authority
> about how they intend to interpret results, not a directive to the
> infrastructure.

#### 7.4. Merkle proof structure

Each voter receives a merkle inclusion proof. Continuing the §6.2.1 example
evidence file:

```json
{
  "voterId": "22a97132992280ab675b8d55ef8368dcd30bd36fa6622524840859b2af",
  "contentHashHex": "870a3a504a00982ddde22fa1d3451f899c527833c25dd13e8e513524746249cd",
  "leafHashHex": "f3a8c12b6e94d7f5a1083ed7be4196528c3d9f7b40165e8a921faec73b25048d",
  "merkleRoot": "edc5b3a0915f745a6574e9d2c12cd199ee17518860b1e79e63eb3cd95395987e",
  "proof": [
    {
      "siblingHex": "675b30335a3c0c255b225f92ab1b098c25d7e38d9f745968acea7532d5cdda1a"
    },
    {
      "siblingHex": "545a7da777c6db9e85fb15a2e99ca21eb9abc718aa3a6277dd7ba86fbb88e681"
    }
  ]
}
```

- `voterId` is the voter token asset name (58 hex chars per §5.1). It is also
  the leaf `name` (see `leafHashHex` below).
- `contentHashHex` is the per-voter `vote_hash`:
  `blake2b_256(JSON.stringify(evidence))` over the compact serialization of the
  `vote-{tokenName}-v{version}.json` evidence file (see §7.7; this standard uses
  compact JSON, not JCS). Same value as `vote_hash` in the voter datum
  (§5.2), folded into the (601) datum's `merkle_root` during finalization.
- `leafHashHex` is `blake2b_256(0x00 || contentHashHex_bytes || utf8(voterId))`.
  The leaf binds the voter's token name in addition to the content hash, so an
  inclusion proof cannot be replayed under a different token name.
- `merkleRoot` is the evidence-tree root committed on-chain as `merkle_root`
  in the (601) datum.
- `proof` is the ordered list of sibling hashes from leaf to root, each a
  `{ siblingHex }` object. There is **no** direction field: at every level the
  verifier orders the running hash and the sibling by ascending lowercase hex,
  then hashes `0x01 || min || max` with blake2b_256, and continues upward.

The merkle tree uses:

- Leaf hash: `blake2b_256(0x00 || contentHash || utf8(name))`.
- Internal node: `blake2b_256(0x01 || min(L, R) || max(L, R))`, where the two
  children are ordered by ascending lowercase hex.
- Hash function: blake2b_256.
- A node with no sibling at a level is paired with itself.

Any voter can verify their inclusion by:

1. Fetching their evidence file from IPFS at `vote-{tokenName}-v{version}.json`.
2. Computing `contentHashHex = blake2b_256(JSON.stringify(evidence))` (compact)
   and `leafHashHex = blake2b_256(0x00 || contentHashHex || utf8(tokenName))`.
3. Folding each `proof[i].siblingHex` upward (order-by-hex, then hash) to
   reconstruct the root.
4. Comparing against `merkle_root` in the (601) token's on-chain datum.

#### 7.5. Full-results and merkle-proof JSON Schema

The following JSON Schema (Draft 2020-12) is normative. The
`results.json` file and every `proofs/{tokenName}.json` file in the evidence
directory **MUST** validate against it.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://docs.ekklesia.vote/cip/hydra-voting-tokens/results.schema.json",
  "title": "EvidenceArtifacts",
  "description": "Top-level union for the two main results-side artifacts: FullResults (results.json) and VoterInclusionProof (proofs/{tokenName}.json).",
  "oneOf": [
    {
      "$ref": "#/$defs/FullResults"
    },
    {
      "$ref": "#/$defs/VoterInclusionProof"
    }
  ],
  "$defs": {
    "Hex32": {
      "type": "string",
      "pattern": "^[0-9a-f]{64}$"
    },
    "Hex28": {
      "type": "string",
      "pattern": "^[0-9a-f]{56}$"
    },
    "Hex29": {
      "type": "string",
      "pattern": "^[0-9a-f]{58}$"
    },
    "VoteMethod": {
      "type": "string",
      "enum": [
        "binary",
        "single-choice",
        "multi-choice",
        "range",
        "ranked",
        "weighted",
        "likert"
      ]
    },
    "Role": {
      "type": "string",
      "enum": [
        "raw",
        "drep",
        "pool",
        "stake"
      ]
    },
    "OptionCount": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "option",
        "count"
      ],
      "properties": {
        "option": {
          "type": "integer"
        },
        "count": {
          "type": "integer",
          "minimum": 0
        }
      }
    },
    "DistributionEntry": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "value",
        "count"
      ],
      "properties": {
        "value": {
          "type": "integer"
        },
        "count": {
          "type": "integer",
          "minimum": 0
        }
      }
    },
    "WeightedOptionTally": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "option",
        "totalPoints",
        "voterCount"
      ],
      "properties": {
        "option": {
          "type": "integer"
        },
        "totalPoints": {
          "type": "integer",
          "minimum": 0
        },
        "voterCount": {
          "type": "integer",
          "minimum": 0
        }
      }
    },
    "LikertOptionTally": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "option",
        "count",
        "distribution"
      ],
      "properties": {
        "option": {
          "type": "integer"
        },
        "count": {
          "type": "integer",
          "minimum": 0
        },
        "distribution": {
          "type": "object",
          "additionalProperties": {
            "type": "integer",
            "minimum": 0
          }
        }
      }
    },
    "PairwiseMatrix": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "options",
        "matrix"
      ],
      "properties": {
        "options": {
          "type": "array",
          "items": {
            "type": "integer"
          }
        },
        "matrix": {
          "type": "array",
          "items": {
            "type": "array",
            "items": {
              "type": "integer",
              "minimum": 0
            }
          }
        }
      }
    },
    "MethodTally": {
      "oneOf": [
        {
          "type": "object",
          "additionalProperties": false,
          "required": [
            "method",
            "results"
          ],
          "properties": {
            "method": {
              "enum": [
                "binary",
                "single-choice",
                "multi-choice"
              ]
            },
            "results": {
              "type": "array",
              "items": {
                "$ref": "#/$defs/OptionCount"
              }
            }
          }
        },
        {
          "type": "object",
          "additionalProperties": false,
          "required": [
            "method",
            "distribution"
          ],
          "properties": {
            "method": {
              "const": "range"
            },
            "distribution": {
              "type": "array",
              "items": {
                "$ref": "#/$defs/DistributionEntry"
              }
            }
          }
        },
        {
          "type": "object",
          "additionalProperties": false,
          "required": [
            "method",
            "firstPreference",
            "pairwise"
          ],
          "properties": {
            "method": {
              "const": "ranked"
            },
            "firstPreference": {
              "type": "array",
              "items": {
                "$ref": "#/$defs/OptionCount"
              }
            },
            "pairwise": {
              "$ref": "#/$defs/PairwiseMatrix"
            }
          }
        },
        {
          "type": "object",
          "additionalProperties": false,
          "required": [
            "method",
            "results"
          ],
          "properties": {
            "method": {
              "const": "weighted"
            },
            "results": {
              "type": "array",
              "items": {
                "$ref": "#/$defs/WeightedOptionTally"
              }
            }
          }
        },
        {
          "type": "object",
          "additionalProperties": false,
          "required": [
            "method",
            "results"
          ],
          "properties": {
            "method": {
              "const": "likert"
            },
            "results": {
              "type": "array",
              "items": {
                "$ref": "#/$defs/LikertOptionTally"
              }
            }
          }
        }
      ]
    },
    "QuestionTally": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "questionId",
        "method",
        "roleResults"
      ],
      "properties": {
        "questionId": {
          "type": "string",
          "minLength": 1
        },
        "method": {
          "$ref": "#/$defs/VoteMethod"
        },
        "roleResults": {
          "type": "object",
          "additionalProperties": {
            "$ref": "#/$defs/MethodTally"
          },
          "propertyNames": {
            "$ref": "#/$defs/Role"
          }
        },
        "abstainedByRole": {
          "type": "object",
          "additionalProperties": {
            "type": "integer",
            "minimum": 0
          },
          "propertyNames": {
            "$ref": "#/$defs/Role"
          }
        }
      }
    },
    "BackendOptionResult": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "id",
        "count",
        "votingPower"
      ],
      "properties": {
        "id": {
          "type": "string",
          "minLength": 1
        },
        "label": {
          "type": "string"
        },
        "count": {
          "type": "integer",
          "minimum": 0
        },
        "votingPower": {
          "const": 0
        }
      }
    },
    "BackendGroupTally": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "totalVotes",
        "results"
      ],
      "properties": {
        "totalVotes": {
          "type": "integer",
          "minimum": 0
        },
        "results": {
          "type": "array",
          "items": {
            "$ref": "#/$defs/BackendOptionResult"
          }
        },
        "scale": {
          "type": "object",
          "additionalProperties": false,
          "required": [
            "distribution"
          ],
          "properties": {
            "distribution": {
              "type": "array",
              "items": {
                "$ref": "#/$defs/DistributionEntry"
              }
            }
          }
        },
        "ranked": {
          "type": "object",
          "additionalProperties": false,
          "required": [
            "firstPreference",
            "pairwise"
          ],
          "properties": {
            "firstPreference": {
              "type": "array",
              "items": {
                "$ref": "#/$defs/OptionCount"
              }
            },
            "pairwise": {
              "$ref": "#/$defs/PairwiseMatrix"
            }
          }
        },
        "weighted": {
          "type": "object",
          "additionalProperties": false,
          "required": [
            "results"
          ],
          "properties": {
            "results": {
              "type": "array",
              "items": {
                "$ref": "#/$defs/WeightedOptionTally"
              }
            }
          }
        },
        "likert": {
          "type": "object",
          "additionalProperties": false,
          "required": [
            "results"
          ],
          "properties": {
            "results": {
              "type": "array",
              "items": {
                "$ref": "#/$defs/LikertOptionTally"
              }
            }
          }
        }
      }
    },
    "BackendTally": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "results",
        "resultsByGroup"
      ],
      "properties": {
        "results": {
          "type": "array",
          "items": {
            "$ref": "#/$defs/BackendOptionResult"
          }
        },
        "resultsByGroup": {
          "type": "object",
          "additionalProperties": {
            "$ref": "#/$defs/BackendGroupTally"
          },
          "propertyNames": {
            "$ref": "#/$defs/Role"
          }
        }
      }
    },
    "FullResults": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "specVersion",
        "ballotId",
        "tallies",
        "questionTallies",
        "totalVoters",
        "headId",
        "finalizedAt"
      ],
      "properties": {
        "specVersion": {
          "type": "string",
          "pattern": "^\\d+\\.\\d+\\.\\d+$"
        },
        "ballotId": {
          "$ref": "#/$defs/Hex32"
        },
        "tallies": {
          "type": "object",
          "additionalProperties": {
            "$ref": "#/$defs/BackendTally"
          }
        },
        "questionTallies": {
          "type": "array",
          "items": {
            "$ref": "#/$defs/QuestionTally"
          }
        },
        "totalVoters": {
          "type": "integer",
          "minimum": 0
        },
        "headId": {
          "$ref": "#/$defs/Hex28"
        },
        "finalizedAt": {
          "type": "string",
          "format": "date-time"
        },
        "votersByRole": {
          "type": "object",
          "additionalProperties": {
            "type": "integer",
            "minimum": 0
          },
          "propertyNames": {
            "type": "string",
            "enum": [
              "drep",
              "pool",
              "stake"
            ]
          }
        },
        "excludedVoters": {
          "type": "array",
          "items": {
            "type": "object",
            "additionalProperties": false,
            "required": [
              "tokenName",
              "reason"
            ],
            "properties": {
              "tokenName": {
                "$ref": "#/$defs/Hex29"
              },
              "reason": {
                "type": "string",
                "minLength": 1
              }
            }
          }
        }
      }
    },
    "VoterInclusionProof": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "voterId",
        "contentHashHex",
        "leafHashHex",
        "merkleRoot",
        "proof"
      ],
      "properties": {
        "voterId": {
          "$ref": "#/$defs/Hex29"
        },
        "contentHashHex": {
          "$ref": "#/$defs/Hex32"
        },
        "leafHashHex": {
          "$ref": "#/$defs/Hex32"
        },
        "merkleRoot": {
          "$ref": "#/$defs/Hex32"
        },
        "proof": {
          "type": "array",
          "description": "Ordered sibling hashes from leaf to root. Order at each level is recovered by ascending-lowercase-hex comparison (§7.4); no direction field is stored.",
          "items": {
            "type": "object",
            "additionalProperties": false,
            "required": [
              "siblingHex"
            ],
            "properties": {
              "siblingHex": {
                "$ref": "#/$defs/Hex32"
              }
            }
          }
        }
      }
    }
  }
}
```

Constraints not expressible in schema and required of implementations:

1. `FullResults.tallies` keys **MUST** be a superset of every `questionId`
   appearing in any voter's `signedPayload.votes`.
2. `FullResults.questionTallies` **MUST** contain one entry per
   `FullResults.tallies` key. `method` MUST match the corresponding question's
   `method` in the (600) ballot definition.
3. `FullResults.totalVoters` **MUST** equal the count of distinct voter tokens
   whose evidence files are present in `votes/` plus the length of
   `FullResults.excludedVoters`.
4. `BackendOptionResult.id` values **MUST** be lowercase decimal string
   representations of integers, except the literal `"abstain"` which represents
   the `abstain: true` bucket. When any abstainer exists for a scope,`"abstain"`
   **MUST** appear exactly once in that scope's
   `results[]` array.

#### 7.6. Auditor-companion artifacts

Three further artifacts in the evidence directory let an auditor verify
completeness, not merely per-voter integrity: `proof-package.json` (the merkle
package emitted at finalization), the per-voter `history/{voterId}.json`
chains, and `exclusions.json`. Each **MUST** validate against the corresponding
definition below.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://docs.ekklesia.vote/cip/hydra-voting-tokens/companion.schema.json",
  "title": "AuditorCompanionArtifacts",
  "oneOf": [
    {
      "$ref": "#/$defs/ProofPackage"
    },
    {
      "$ref": "#/$defs/VoteHistory"
    },
    {
      "$ref": "#/$defs/Exclusions"
    }
  ],
  "$defs": {
    "Hex32": {
      "type": "string",
      "pattern": "^[0-9a-f]{64}$"
    },
    "Hex29": {
      "type": "string",
      "pattern": "^[0-9a-f]{58}$"
    },
    "IpfsCid": {
      "type": "string",
      "minLength": 1
    },
    "ProofStep": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "siblingHex"
      ],
      "properties": {
        "siblingHex": {
          "$ref": "#/$defs/Hex32"
        }
      }
    },
    "ProofPackageFile": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "name",
        "contentHashHex",
        "leafHashHex",
        "merkleProof"
      ],
      "properties": {
        "name": {
          "type": "string",
          "minLength": 1,
          "description": "Leaf name. For the evidence tree this is the voter token name (58 hex, §5.1); it is folded into the leaf hash (content+path mode, §7.4)."
        },
        "contentHashHex": {
          "$ref": "#/$defs/Hex32",
          "description": "The voter's vote_hash."
        },
        "leafHashHex": {
          "$ref": "#/$defs/Hex32"
        },
        "merkleProof": {
          "type": "array",
          "items": {
            "$ref": "#/$defs/ProofStep"
          }
        }
      }
    },
    "ProofPackage": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "schema",
        "hashAlg",
        "leafPrefixHex",
        "nodePrefixHex",
        "pairSort",
        "rootHex",
        "createdAt",
        "files",
        "leafMode"
      ],
      "description": "proof-package.json: the self-describing merkle package emitted at finalization. Binds every evidence leaf to the on-chain merkle_root.",
      "properties": {
        "schema": {
          "const": "lerna-labs/merkle-proof@v1"
        },
        "hashAlg": {
          "const": "blake2b-256"
        },
        "leafPrefixHex": {
          "const": "00"
        },
        "nodePrefixHex": {
          "const": "01"
        },
        "pairSort": {
          "const": "lexicographic"
        },
        "rootHex": {
          "$ref": "#/$defs/Hex32",
          "description": "Same value as merkle_root in the (601) datum."
        },
        "createdAt": {
          "type": "string",
          "format": "date-time"
        },
        "leafMode": {
          "const": "content+path"
        },
        "files": {
          "type": "array",
          "minItems": 1,
          "items": {
            "$ref": "#/$defs/ProofPackageFile"
          }
        }
      }
    },
    "VoteHistoryEntry": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "version",
        "voteHash",
        "ipfsCid",
        "txHash",
        "timestamp"
      ],
      "properties": {
        "version": {
          "type": "integer",
          "minimum": 0
        },
        "voteHash": {
          "$ref": "#/$defs/Hex32"
        },
        "ipfsCid": {
          "$ref": "#/$defs/IpfsCid"
        },
        "txHash": {
          "type": "string",
          "description": "Hydra transaction hash that committed this vote update."
        },
        "prevTxHash": {
          "type": "string",
          "description": "Transaction hash of the previous update in the chain; absent on the first entry."
        },
        "timestamp": {
          "type": "integer",
          "minimum": 0,
          "description": "Unix epoch milliseconds at submission."
        }
      }
    },
    "VoteHistory": {
      "type": "array",
      "description": "history/{voterId}.json: a chronological array of vote updates for one voter (the filename uses the bech32 voterId), oldest first. The last entry is the vote that participated in the final tally.",
      "items": {
        "$ref": "#/$defs/VoteHistoryEntry"
      }
    },
    "Exclusions": {
      "type": "array",
      "description": "exclusions.json: voters present in the pre-burn ledger whose evidence could not be verified at finalization. The file is omitted entirely when there are no exclusions.",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": [
          "tokenName",
          "reason"
        ],
        "properties": {
          "tokenName": {
            "$ref": "#/$defs/Hex29"
          },
          "reason": {
            "type": "string",
            "minLength": 1,
            "description": "Free-text exclusion reason (typically the verification error message). Not an enumerated set in this version."
          }
        }
      }
    }
  }
}
```

Constraints not expressible in schema and required of implementations:

1. `ProofPackage.files[]` **MUST** contain exactly one entry per published
   `vote-{tokenName}-v{version}.json` evidence file, with `name` equal to that
   voter's token name and `contentHashHex` equal to its `vote_hash`.
2. `ProofPackage.rootHex` **MUST** equal `merkle_root` in the (601) datum.
3. For every `files[i]`, recomputing the leaf
   (`blake2b_256(0x00 || contentHashHex || utf8(name))`) and folding
   `merkleProof` upward per §7.4 **MUST** reproduce `rootHex`.
4. In each `history/{voterId}.json` array, `version` **MUST** be strictly
   greater than the previous entry's `version`, and `prevTxHash` (when present)
   **MUST** equal the previous entry's `txHash`. The last entry's `voteHash`
   **MUST** match the `vote_hash` of that voter's
   `vote-{tokenName}-v{version}.json` evidence file.
5. Every `tokenName` in `exclusions.json` **MUST** appear in
   `FullResults.excludedVoters[*].tokenName`, and vice versa, with matching
   `reason`.

> A per-file content-integrity manifest (`cid` + `sha256Hex` + `sizeBytes`
> per file), enabling an HTTP-only auditor to detect a gateway that serves
> substituted bytes under a valid CID, is planned for `specVersion 0.4.0`
> (see §8.2). It is not produced in 0.3.0.

#### 7.7. JSON canonicalization

This standard does **not** use a sort-based canonicalization such as
[RFC 8785][] JCS. Every hash input is the output of `JSON.stringify` over the
object as the producer constructs it, with keys in **construction (insertion)
order**, not lexicographically sorted. Two serialization variants are used:

- **Compact**: `JSON.stringify(value)`, no whitespace. Used for the
  `signedPayload` (the signature pre-image), the per-voter `vote_hash`
  (evidence), and the ballot-content merkle leaves (§2.3).
- **Pretty**: `JSON.stringify(value, null, 2)`, two-space indentation. Used for
  `results.json`; `results_hash` is computed over those exact pretty bytes,
  which are also the bytes pinned to IPFS.

| Hash                              | Serialization      | Computed over                |
|-----------------------------------|--------------------|------------------------------|
| `merkle_root` (voter datum, §5.2) | compact            | the `signedPayload`          |
| `vote_hash` (§5.2, §7.4)          | compact            | the `VoteEvidence` object    |
| ballot-content merkle leaf (§2.3) | compact            | each `BallotQuestion` object |
| `results_hash` (§4.1, §7.3)       | pretty (`null, 2`) | the `FullResults` object     |

Key ordering is significant: a verifier MUST serialize with the same key order
the producer used. Parsing the published JSON and re-serializing it with an
order-preserving JSON implementation reproduces that order, because every field
is emitted in the order it was added to the object. Implementations MUST NOT
sort keys; sorting (as JCS would) yields a different byte stream and a different
hash, breaking verification end-to-end.

Two consequences for auditors:

- **`results.json` is byte-faithful.** `results_hash` is the hash of the exact
  bytes published to IPFS, so an auditor MAY hash the retrieved file directly.
- **Vote evidence is not byte-faithful in this version.** `vote_hash` is the
  hash of the *compact* serialization, but evidence files are pinned
  *pretty*-printed. To verify `vote_hash`, an auditor MUST parse the evidence
  file and re-serialize it compact (`JSON.stringify` with no whitespace,
  preserving key order) before hashing. This is corrected in a later version
  (see §8.2).

Signature verification recomputes `blake2b_256(compact(signedPayload))` from the
`ekklesia.signedPayload` object carried in the evidence and checks it against
the value the [CIP-8][CIP-0008] witness signed.

The optional per-question `contentHash` (§3.1) is the one hash in this standard
computed over arbitrary external bytes rather than over JSON: it is
`blake2b_256` of the raw bytes of the question's off-chain content blob, so the
serialization rules above do not apply to it. Its *presence* on the question
still participates in that question's merkle leaf via the compact serialization
of the whole `BallotQuestion` object.

#### 7.8. Auditor verification algorithm

The following procedure is the normative end-to-end verification algorithm. An
auditor running this procedure against a settled ballot produces a pass/fail
verdict per check. A ballot is **verified** if every check passes. The procedure
references the schemas defined above; an implementation that schema-validates
each artifact and performs the cross-checks below has performed a complete
audit.

The auditor's scope is strictly the integrity, completeness, and authenticity of
the recorded vote set. Whether the ballot "passed"
under any given tabulation rule, whether the voters were eligible under any
given eligibility rule, and how each voter's recorded selection translates to
influence are all out of scope (see "Scope and non-goals" above).

##### Required inputs

- The voting authority's policy ID (or a way to discover it, e.g. from a
  published voting-authority registry).
- Read access to a Cardano node or indexer (Blockfrost, Koios, etc.).
- Read access to an IPFS gateway.
- BLAKE2b implementation (224-bit and 256-bit output).
- Ed25519 verification library and a [CIP-8][CIP-0008] (`COSE_Sign1`) parser.
- A JSON serializer that preserves object key order and can emit both compact
  and two-space-pretty output (§7.7). No sort-based canonicalizer is required.

##### Procedure

**Step 1: Locate ballot tokens.** Query the policy ID for assets whose names
match the (600) and (601) CIP-67 prefixes (§1.1). Confirm exactly one of each
token exists under the policy and that both share the same 28-byte fingerprint
suffix. **Fail** if zero or multiple tokens match either prefix.

**Step 2: Decode the (600) datum.** Read the inline datum from the
(600) token's UTxO. Decode against the §2.1 CDDL schema. **Fail** if decoding
does not produce a valid `ballot_definition_datum`. Confirm that the fingerprint
derived from `namespace` per §1.1 equals the fingerprint suffix observed in Step
1.

**Step 3: Fetch and validate the ballot definition.** Fetch the IPFS object at
`ballot_cid`. Validate against the §2.2.2 JSON Schema. Recompute the
per-question merkle tree per §2.3 over the
`questions` array and confirm the root equals both `content_hash`
on the (600) datum AND `ekklesia.merkleRoot` inside the document.
**Fail** on any mismatch.

**Step 4: Decode the (601) datum.** Read the inline datum from the
(601) token's UTxO. Decode against the §4.1 CDDL schema. Confirm
`version == 1` and that all four byte fields are populated. **Fail**
if the datum is in any pre-finalize state at audit time.

**Step 5: Fetch and validate the evidence directory.** Fetch the IPFS directory
at `evidence_cid` from the (601) datum. Locate
`proof-package.json` and validate against §7.6. **Fail** if absent or invalid.
Cross-check `proof-package.json.rootHex` equals `(601).fields.merkleRoot`. (The
0.3.0 `proof-package.json` carries only the merkle commitment; the `ballotId`,
`resultsHash`, and `evidenceCid` bindings are checked directly against
`results.json` and the (601) datum in the steps below.)

**Step 6: (reserved for 0.4.0).** The per-file content-integrity manifest and
the gateway-tamper check are introduced in `specVersion 0.4.0` (see §7.6, §8.2).
In 0.3.0 there is no manifest to validate; file integrity rests on IPFS
content-addressing (the CID) plus the per-voter and results hashes verified in
the following steps. Proceed to Step 7.

**Step 7: Validate `results.json`.** Locate `results.json` in the directory.
Validate against the §7.5 `FullResults` schema. `results.json` is byte-faithful
(§7.7): compute `blake2b_256` over the retrieved file bytes directly and confirm
it equals `(601).fields.resultsHash`. **Fail** on any mismatch.

**Step 8: Per-voter evidence verification.** For every
`vote-{tokenName}-v{version}.json` in the directory:

- a) Validate against the §6.3 `VoteEvidence` schema.
- b) Re-serialize the parsed evidence compact (`JSON.stringify`, no whitespace,
  preserving key order, §7.7) and compute `vote_hash = blake2b_256` of those
  bytes.
- c) Recover the voter's public key(s) from
  `ekklesia.witnesses[*].coseSign1Hex`.
- d) Verify each `COSE_Sign1` signature against
  `blake2b_256(JSON.stringify(signedPayload))` (compact, §7.7) per §6.1,
  applying [CIP-8][CIP-0008]'s verification rules.
- e) For key-based voters: confirm the recovered key hash matches the
  credential-hash portion of `tokenName` per §5.1.
- f) For script-based voters: confirm the witness set satisfies
  `ekklesia.nativeScript`.
- g) For calidus voters: resolve `ekklesia.calidusDeclaration.calidusId` to its
  pool via the on-chain CIP-151 registration and confirm the signing key belongs
  to that calidus identity. A self-contained binding check that carries pool id,
  key hash, registration tx, and validity window inline in the declaration
  arrives with `specVersion 0.4.0`.
- h) Read the matching `history/{voterId}.json` array; confirm the last entry's
  `voteHash` equals the `vote_hash` computed in (b) and that `version`s are
  strictly increasing.
- i) Verify the merkle inclusion: load `proofs/{tokenName}.json`, validate
  against the §7.5 `VoterInclusionProof` schema, recompute the leaf and fold the
  proof per §7.4, and confirm the reconstructed root equals
  `(601).fields.merkleRoot`.

> **Fail** the ballot on the first per-voter check that fails.

**Step 9: Recompute the tally.** Independently aggregate the per-voter evidence
(`vote-*-v*.json`) per each question's `method`, produce a `FullResults`-shaped
output, serialize it pretty (`JSON.stringify(..., null, 2)`, §7.7) with the same
field order, and confirm it matches `results.json` byte-for-byte. (Because
`results.json` is byte-faithful, an auditor MAY instead rely on the Step 7 hash
check and treat this as a structural re-tally cross-check.)

**Step 10: Reconcile exclusions.** Load `pre-burn-ledger.json` (the snapshot of
every voter token minted in the head before settlement) and `exclusions.json`.
Every token in the pre-burn ledger **MUST** appear either as a
`vote-{tokenName}-v{version}.json` evidence file (included) or in
`exclusions.json` (excluded); a token in neither is a **silent suppression**
finding. Confirm every `tokenName` in `exclusions.json` also appears in
`FullResults.excludedVoters` with a matching `reason`.

**Step 11: Output verdict.** If every check passes, the ballot is
**verified**. The auditor's output **SHOULD** include the on-chain anchor
(policy ID, (600) asset name, (601) asset name), the IPFS roots audited
(`ballot_cid`, `evidence_cid`), per-step pass/fail counts, and the totals of
voters validated, excluded, and (if applicable) suppressed.

A verified verdict is a statement about the **recorded vote set**, not about the
ballot's political outcome. Whether the recorded set satisfies any specific
quorum, supermajority, or weighting rule is the voting authority's determination
to make against this CIP's output, not part of this CIP's scope.

### 8. Versioning

This standard implements versions for the on-chain datums and the off-chain
documents independently. Both schemes follow rules that allow non-breaking
additions without superseding the CIP.

#### 8.1. On-chain datum versions

Each on-chain datum (600, 601, voter) carries a `version` integer in its Plutus
`Constr 0` envelope. Datum-schema changes that add fields, relax constraints, or
otherwise remain backward-compatible bump the integer; consumers **MUST** be
able to parse all prior schema versions.

Current versions at this CIP draft date:

- **(600) `ballot_definition_datum`**: `version = 1` (original mint).
  `version = 2` is in use for the case where the ballot definition was edited
  via the prepare-update path before the head opened. After the head opens,
  the (600) datum cannot be modified.
- **(601) `ballot_result_datum`**: `version = 1` (mint-time placeholder and
  finalized state). `version = 2` is the analog edited-pre-open case.
- **Voter datum**: no datum-schema versioning; the `version` field is the
  per-voter monotonic nonce (§5.2), not a schema version.

Breaking changes to any of the three datums (renaming a field, changing the byte
encoding, adding a non-optional field) requires either a new schema version with
explicit deprecation of the prior or a new top-level CIP that supersedes this
one.

#### 8.2. Off-chain document versions

The IPFS documents (ballot definition, vote evidence, full results)
carry a top-level `specVersion` string. Current value: `"0.3.0"`.

The `specVersion` follows semver. Backward-compatible additions **MUST**
increment the patch or minor component; structural changes that break existing
consumers **MUST** increment the major component.

A consumer **MUST** accept any document whose `specVersion` major matches its
expected major. A producer **MUST** emit the highest `specVersion`
that all required fields exist at. Where a field name is reused across schema
versions, its semantics **MUST NOT** change without a major bump.

**This document specifies `specVersion 0.3.0` as-built.** It matches the
artifacts the reference implementation produces for ballots conducted under the
current minting policy. The following changes are defined for
`specVersion 0.4.0` and apply only to ballots opened after the 0.4.0 cutover;
0.3.0 ballots remain verifiable under the rules above:

- **Byte-faithful hashing.** Every artifact is hashed over the exact bytes
  pinned to IPFS, and the signed payload is committed as verbatim bytes,
  removing the compact-vs-pretty re-serialization step described in §7.7.
- **Per-question `reference { uri, hash }`** replacing the flat `contentHash`
  string (§3.1), for durable content-addressable supplementary material.
- **Open schemas (`additionalProperties: true`) plus the extensibility model**
  of §2.4: conforming readers accept and preserve unknown fields through
  hashing.
- **Rich `calidusDeclaration`** (`poolId`, `calidusKeyHashHex`,
  `registrationTxHash`, `validFromSlot`, `validToSlot`) enabling the
  self-contained calidus→pool binding check in §7.8 Step 8(g).
- **Per-file content-integrity manifest** (`cid` + `sha256Hex` + `sizeBytes`)
  enabling the gateway-tamper check in §7.8 Step 6.

### 9. Ballot lifecycle summary

```text
Phase 1: PREPARE (L1)
  ├─ Mint (600) + (601) tokens in a single transaction
  ├─ Pin full ballot definition to IPFS
  ├─ (600) remains on L1 as immutable reference
  └─ (601) UTxO prepared for Hydra commit

Phase 2: START (Hydra)
  ├─ Commit (601) token + gas ADA into Hydra head
  └─ Cache ballot definition from IPFS

Phase 3: VOTE (Hydra)
  ├─ Voters register (mint voter token, version = 0)
  ├─ Voters cast / update votes (update voter datum, version monotonic)
  ├─ Each vote signed via CIP-8 / COSE_Sign1
  ├─ Evidence pinned to IPFS, ipfs_cid recorded in voter datum
  └─ Version counter prevents replay attacks

Phase 4: FINALIZE (Hydra, before close)
  ├─ Verify all voter signatures
  ├─ Construct merkle tree of vote evidence
  ├─ Pin evidence directory to IPFS
  ├─ Update (601) datum with [ballot_id, results_hash, evidence_cid, merkle_root]
  └─ Burn all voter tokens

Phase 5: CLOSE (Hydra)
  └─ Close Hydra head (no further updates possible)

Phase 6: SETTLE (L1)
  └─ (601) token returns to L1 via fanout with final datum
```

## Rationale: how does this CIP achieve its goals?

This CIP was borne out of practical experience running Hydra-based votes for
Intersect and the broader Cardano community, where the absence of a shared
standard meant every deployment reinvented the same cryptographic plumbing
(token naming, datum schemas, evidence formats, merkle trees) from scratch. By
defining that plumbing once as a reusable standard, we free implementers to
focus on the parts that actually differ between elections: eligibility,
weighting, and tabulation.

By storing full ballot definitions and vote evidence on IPFS with only hashes
and CIDs on-chain, we keep UTxO sizes small while maintaining full cryptographic
verifiability: the on-chain hashes bind the off-chain documents irrevocably to
the L1 record.

By allocating purpose-built [CIP-67][CIP-0067] labels (600) and (601) rather
than reusing [CIP-68][CIP-0068]'s NFT-oriented datum schema (`name`, `image`,
`mediaType`), we gain datum schemas optimized for ballot data, vote evidence,
and result anchoring while preserving the familiar reference / instance pairing
convention.

By separating the cryptographic recording of votes from power weighting and
eligibility determinations, the voting infrastructure stays neutral as a
recording substrate. Different ballots in the same ecosystem may reasonably use
different eligibility, weighting, and tabulation rules; baking any one approach
into the shared infrastructure would make it unsuitable for the others. The same
recorded vote set can be re-tallied later under a different weighting or
eligibility rule without re-running the voting process.

By defining a unified `selection` field whose shape is determined by the
question's `method`, with `abstain: true` as a first-class alternative mutually
exclusive with `selection`, we make abstention visible in tallies as a distinct
bucket and the voter's intent unambiguous. Per-question `requireAnswer: true`
overrides the default and forces a substantive choice where appropriate.

By aligning the question / answer format with [CIP-179][CIP-0179] for the four
core voting methods, and extending it with Ekklesia-namespaced URIs for
`ranked`, `weighted`, and `likert`, we enable tooling reuse across the ecosystem
while supporting voting mechanisms beyond CIP-179's current scope.

By providing each voter with a merkle inclusion proof against a single on-chain
root, any voter can independently verify their own vote was included without
trusting the voting authority or downloading the entire vote set.

By minting per-voter tokens inside the Hydra head, we enable the Hydra ledger to
enforce one-vote-per-voter at the transaction level. The credential-prefix token
naming scheme supports multiple voter types (DReps, SPOs and their
[CIP-151][CIP-0151] calidus hot keys, stakeholders) within a single ballot.

By deriving `responderRole` server-side from the voter's bech32 HRP rather than
accepting it from the client, we prevent a voter from mislabeling their own
evidence under a role other than what their credential supports, which would
otherwise undermine role-stratified tallies.

### Related work

- **[CIP-8][CIP-0008]** (Message Signing; the basis of CIP-30 / CIP-95 / CIP-103
  wallet signing flows). Voters sign the canonical `SignedVotePayload`
  using CIP-8 / `COSE_Sign1`.
- **[CIP-67][CIP-0067]** (Asset Name Labels). Allocates the (600) and (601)
  labels used by this standard.
- **[CIP-68][CIP-0068]** (Datum Metadata Standard). Inspires the reference /
  instance pairing pattern but is unsuitable for voting datums (see §1.4).
- **[CIP-129][CIP-0129]** (Governance Credentials). Source of the `0x22` DRep
  credential-type byte and the `0x23` script-based credential type referenced in
  §6.2.
- **[CIP-151][CIP-0151]** (Stake Pool Hot Credentials). Defines the calidus
  hot-key mechanism that powers `calidus`-prefixed voter IDs in §5.1.
- **[CIP-179][CIP-0179]** (On-Chain Surveys and Polls). The question / answer
  schema in §2.2 and §3 is CIP-179 compatible for the four core voting methods;
  URIs in §3.2 reflect the state of CIP-179 PR #1107 at this CIP's draft date
  and will be revised to match if CIP-179 finalizes with different identifiers.

## Path to Active

### Acceptance Criteria

- [ ] [CIP-67][CIP-0067] labels 600 and 601 are registered in the official
  registry.
- [ ] At least one production ballot conducted using this standard
  (Ekklesia has conducted ballots on preprod and mainnet, including CIWG and
  Intersect-affiliated votes).
- [ ] Independent auditor successfully verifies a ballot using only on-chain
  data and IPFS evidence per the procedure in §7.4.
- [ ] Reference implementation published as open source.

### Implementation Plan

The Ekklesia voting platform implements this standard and has conducted multiple
ballots on Cardano preprod and mainnet. The implementation consists of:

- **Hydra middleware**: Express.js service managing the ballot lifecycle and
  producing the on-chain commitments described in this CIP.
- **Voting API service**: the broker layer that voters interact with; handles
  voter authentication, draft assembly, and signature collection before
  forwarding evidence to the Hydra middleware.
- **Voter-facing web application**: voter-side UX for ballot selection, signing,
  results display, and auditor verification.
- **Shared helpers library (`@lerna-labs/ekklesia-helpers`)**: open-source,
  Apache-2.0, published on npm. Carries the cryptographic primitives (CIP-8
  signing, blake2b hashing, bech32 decoding, merkle proof construction, and
  verification) used across the platform and reusable by any third party
  building against this standard.

The remaining three components are scheduled to open-source on Apache-2.0
following the conclusion of an external security audit.

## Copyright

This CIP is licensed under
[Apache-2.0](http://www.apache.org/licenses/LICENSE-2.0).

[CIP-0008]: https://github.com/cardano-foundation/CIPs/tree/master/CIP-0008

[CIP-0030]: https://github.com/cardano-foundation/CIPs/tree/master/CIP-0030

[CIP-0067]: https://github.com/cardano-foundation/CIPs/tree/master/CIP-0067

[CIP-0068]: https://github.com/cardano-foundation/CIPs/tree/master/CIP-0068

[CIP-0129]: https://github.com/cardano-foundation/CIPs/tree/master/CIP-0129

[CIP-0151]: https://github.com/cardano-foundation/CIPs/tree/master/CIP-0151

[CIP-0179]: https://github.com/cardano-foundation/CIPs/tree/master/CIP-0179

[RFC 8785]: https://www.rfc-editor.org/rfc/rfc8785