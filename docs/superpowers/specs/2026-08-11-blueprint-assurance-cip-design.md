# Design: CIP "Plutus Blueprint Assurance Documents"

Date: 2026-08-11
Status: Approved by Romain Soulat (brainstorming session)
Replaces: initial draft in `CIP-XXXX/README.md` (embedded `$vocabulary` design)

## Goal

Define a CIP that lets anyone publish machine-readable, reproducible assurance
claims (properties, tests, audits, formal proofs) about validators described in
a CIP-57 Plutus blueprint, so that blueprint readers can see what guarantees
are claimed, by whom, with what method, and re-derive the verdicts themselves.

## Decisions made

| Question | Decision |
| --- | --- |
| Claim scope | Broad assurance registry (tests, audits, formal proofs, …). First user: Blaster formal verification with the Universal Annotation Language (UAL). |
| CIP structure | One CIP, validators only. Function-level specs and data-encoding extensions are out of scope (possible future CIP). |
| Property form | Free property language. Fields declare language name + version and tool name + version. Natural language is admissible. Nothing tool- or language-specific is hardcoded. |
| Placement | **Detached only**: claims live in a standalone *assurance document* (conventional name `assurance.json`), never inside `plutus.json`. The original draft's `$vocabulary` extension mechanism is dropped. |
| Validator referencing | Blueprint producers SHOULD add an optional unique `id` field per validator (legal today: CIP-57's meta-schema does not set `additionalProperties: false` on validator objects). Claims reference validators by `id`, falling back to `title`. |
| Status model | Property + N evidence records. A property states WHAT is claimed; each evidence record states WHO verified it, with what method/tool, and the outcome. Status is per-record. |
| Evidence contents | Verifier, tool + version, method, outcome, date, script hash verified, artifact reference (URI + content hash). Reproduction instructions live inside the artifact. |
| Signatures | Out of scope for v1. Trust rests on reproducibility, not identity. |

## Architecture

- **New document type**, not a blueprint extension: the assurance document is
  its own JSON document with its own versioned meta-schema, identified by
  `"$schema": "https://cips.cardano.org/cips/cipXXXX/schemas/assurance.json"`.
  Breaking changes to the format MUST be published under a new URI.
- **Anyone can publish**: developer, auditor, community member. Multiple
  assurance documents about the same blueprint coexist independently. No
  cooperation from the blueprint author is needed.
- **Binding chain** (what makes a claim provably about real code):
  1. Document-level `blueprint` reference: URI of the blueprint + optional
     content hash of the blueprint file (tamper evidence).
  2. Property-level `scope`: target validators by `id` (preferred) or `title`.
     If a reference is ambiguous (e.g. duplicate titles in the blueprint),
     consumers MUST treat it as an error.
  3. Evidence-level `scriptHash`: the blake2b-224 script hash the verification
     actually ran against. Consumers MUST compare it with the blueprint
     validator's `hash` and flag mismatches (stale-claim detection). For
     parameterized validators this is the hash of the unapplied template,
     matching the blueprint's own `hash` field.

## Document structure

```json
{
  "$schema": "https://cips.cardano.org/cips/cipXXXX/schemas/assurance.json",
  "preamble": {
    "title": "…", "description": "…", "version": "1.0.0",
    "authors": ["…"], "created": "2026-08-11", "license": "CC-BY-4.0"
  },
  "blueprint": {
    "uri": "https://…/plutus.json",
    "hash": { "alg": "sha256", "digest": "…" }
  },
  "languages": {
    "<langId>": { "name": "…", "version": "…", "uri": "…", "description": "…" }
  },
  "tools": {
    "<toolId>": { "name": "…", "version": "…", "uri": "…", "description": "…" }
  },
  "properties": [
    {
      "id": "…", "title": "…",
      "scope": { "validators": ["<validator id or title>"] },
      "statement": {
        "text": "natural-language statement (REQUIRED)",
        "formal": { "language": "<langId>", "source": "inline …", "uri": "…" }
      },
      "assumptions": [ { "text": "…", "formal": { … } } ],
      "tags": ["safety", "…"],
      "evidence": [
        {
          "method": "formal-proof | property-test | unit-test | audit | manual-review | <open>",
          "verifier": "who ran it (informal string in v1)",
          "tool": "<toolId>",
          "outcome": "verified | falsified | partial | inconclusive",
          "date": "YYYY-MM-DD",
          "scriptHash": "…",
          "artifact": { "uri": "…", "hash": { "alg": "…", "digest": "…" }, "mediaType": "…" },
          "notes": "…"
        }
      ]
    }
  ]
}
```

### Field rules

- `statement.text` (natural language) is **mandatory** on every property;
  `statement.formal` is optional. Formal statements declare their `language`
  (registry entry with name + version + optional spec URI) and carry either
  inline `source` or a `uri`.
- `assumptions`: list of statements (same text+formal shape) under which the
  claims hold. Feeds live monitoring ("is the system still within the verified
  assumption bounds?") and keeps formal claims honest.
- `method` is an **open enum**: the five values above are defined by the CIP;
  unknown values are allowed and treated as opaque by tools.
- `outcome` is a **closed enum** (`verified` / `falsified` / `partial` /
  `inconclusive`) so consumers can compare at a glance. The `method` conveys
  strength: a `verified` property-test is weaker than a `verified`
  formal-proof.
- `tool` is REQUIRED on evidence for machine-checked methods, OPTIONAL for
  `audit` and `manual-review` (an audit may involve no tool).
- `scriptHash` is REQUIRED on evidence for machine-checked methods
  (`formal-proof`, `property-test`, `unit-test`), OPTIONAL for `audit` and
  `manual-review`. When present, consumers MUST flag mismatches against the
  blueprint.
- `artifact`: URI + content hash (+ optional `mediaType`). How to re-run lives
  inside the artifact (tool-specific), not in the assurance document.

## Deliverables

1. **Rewritten `CIP-XXXX/README.md`**, CIP-1 compliant:
   - Frontmatter: Title **"Plutus Blueprint Assurance Documents"**, Category:
     Tools, existing authors, Created date kept.
   - Abstract: detached model — standalone documents making reproducible,
     code-bound claims about blueprint validators.
   - Motivation: keep existing text (audit-PDF problem, reproducible
     verification, live assumption monitoring) + third-party publishing angle.
   - Specification: document structure tables in CIP-57 style, field-by-field
     definitions, binding rules, validator-`id` recommendation, versioning
     policy.
   - Examples (embedded `<details>`): (a) Blaster/UAL formal-proof document,
     (b) property-test document (e.g. Aiken tests) demonstrating breadth.
   - Rationale: why detached rather than `$vocabulary`-embedded; why free
     property language; why no signatures in v1; why open `method` / closed
     `outcome`; relation to CIP-52 (audits become publishable evidence);
     backward compatibility (CIP-57 untouched).
   - Path to Active: ≥1 producer (Blaster) + ≥1 consumer tool; implementation
     plan (Blaster emits `assurance.json`; a checker tool validates and
     re-verifies).
   - Copyright: CC-BY-4.0.
2. **`CIP-XXXX/schemas/assurance.json`**: JSON Schema 2020-12 meta-schema
   validating assurance documents (must validate both embedded examples).

## Out of scope (v1)

- Function-level specifications and data-encoding extensions to CIP-57.
- Cryptographic attestation / signatures of evidence records.
- A standardized property language.
- Embedding assurance content inside `plutus.json`.
