---
CIP: pending
Title: Plutus Blueprint Assurance Documents
Category: Tools
Status: Proposed
Authors:
    - Jean-Frédéric Etienne <jean-frederic.etienne@iohk.io>
    - Mark Petruska <mark.petruska@iohk.io>
    - Romain Soulat <romain.soulat@iohk.io>
Implementors: []
Discussions:
    - "Original PR: https://github.com/cardano-foundation/CIPs/pull/1285"
Created: 2026-06-16
License: CC-BY-4.0
---

## Abstract

A [CIP-0057](../CIP-0057) blueprint describes the binary interface of a Plutus validator — its datum, redeemer and parameter schemas — alongside its compiled code. It says nothing about the validator's expected behaviour or the guarantees it provides.

This CIP defines the **assurance document**: a standalone, machine-readable JSON document through which any party, the contract's developers, an external auditor, or an independent community member, can publish claims about the validators described in a blueprint. Each claim states a property in natural language, optionally accompanied by a formal statement in a declared specification language, and is backed by zero or more evidence records stating who verified it, by what method (formal proof, SMT check, property test, unit test, audit, manual review), with which tool, with what outcome, against which script hash, and where a reproducible verification artifact can be retrieved.

A third party can take an assurance document, confirm that it concerns the exact compiled code shipped in the blueprint, fetch the referenced artifacts, re-run the verification, and obtain the same verdicts. Trust rests on the reproducibility of the evidence and the soundness of the verification tools and not on the development team claims.

## Motivation: Why is this CIP necessary?

[CIP-0057](../CIP-0057) makes a validator's interface legible. However, it does not expose anything about the validator's behaviour. Today, "this validator is safe" is established by an off-chain, largely manual process whose end product is typically a PDF report from a trusted auditor. There is no standard, machine-readable way for developers or auditors to state which properties a validator satisfies, how those properties were verified, and how anyone can check the verification themselves.

The blueprint ecosystem is the natural anchor for such claims: a blueprint already carries the compiled validator, the datum and redeemer shapes, the required parameters, and a hash digest linking the validator to on-chain addresses. What is missing is a standard companion format for security claims that links to those elements.

Building directly on the use cases CIP-0057 already lists, this proposal enables:

- **Reproducible verification**: anyone can re-derive a validator's verdicts from the referenced artifacts, rather than trusting an assertion.
- **Communicating guarantees**: wallets, explorers, and registries can display which properties are claimed for a validator, by whom, with what method and outcome — and whether the evidence still matches the deployed code.
- **Third-party assurance**: auditors and community members can publish assurance documents about a deployed contract *without any cooperation from its developers*, and several independent assurance documents about the same blueprint can coexist.
- **Health monitoring of live DApps**: the assumptions under which properties were verified are stated explicitly, so they can be monitored live to check that a running protocol stays within its proofs' assumptions.
- **Specification-first development**: a property with no evidence records is a stated, unverified claim — a machine-readable specification target that implementations and verification efforts can work towards.

## Specification

The key words "MUST", "MUST NOT", "REQUIRED", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119).

### Overview

This specification introduces the notion of an **assurance document**: a standalone JSON document that publishes claims about the on-chain validators described by a [CIP-0057](../CIP-0057) blueprint.

An assurance document is *detached*: it is a separate document from the blueprint. The assurance envelope supports existing CIP-57 blueprints. Executable checks using the coordinated [compiled-interface extension](../CIP-0057/extensions/compiled-interface) additionally require its explicit interface metadata; those definitions belong to the blueprint specification. Anyone — the contract's developers, an external auditor, an independent community member — can author and publish an assurance document about any blueprint. Multiple assurance documents about the same blueprint can coexist independently.

By convention, an assurance document authored by the contract developers is named `assurance.json` and located next to `plutus.json` at the root of the project's repository, to facilitate discoverability. Third-party documents can be published anywhere.

The meta-schema for assurance documents (i.e. the schema used for validating assurance documents themselves) is given as an annex: [schemas/assurance-v2.json](./schemas/assurance-v2.json). An assurance document identifies the format version it complies with through its `$schema` field.

A **producer** is any tool or person authoring assurance documents. A **consumer** is any tool interpreting them (e.g. a wallet, an explorer, a verification checker).

### Document structure

The document itself is a JSON object with the following fields. Here and in all field tables below, a leading `?` marks a field as optional; all other fields are required.

| Fields      | Description                                                        |
| ---         | ---                                                                |
| `$schema`   | URI identifying the assurance document format version              |
| preamble    | An object with meta-information about the assurance document       |
| blueprint   | A reference to the blueprint the claims are about                  |
| ?languages  | A registry of specification languages used by formal statements    |
| ?tools      | A registry of verification tools referenced by evidence records    |
| ?formalFragments | Reusable formal definitions referenced by statements |
| ?definitions | Shared value-schema definitions referenced by assurance functions |
| ?functions | Compiled library functions and their ordered input/result wire schemas |
| ?checkingContexts | Registry of digest-bound checking-context artifacts |
| properties  | The list of claimed properties                                     |

#### `$schema`

The value of this field MUST be the URI of the meta-schema this document complies with. For this version of the specification, it is:

```
https://cips.cardano.org/cips/cipXXXX/schemas/assurance-v2.json
```

The meta-schema pins this value with a `const`: a document claiming compliance with this version of the format carries exactly this URI.

Any breaking change to this specification MUST be published under a new URI. Additions of OPTIONAL fields MAY occur under the same URI. Most metadata objects are open to optional additions: consumers ignore unrecognized fields where the schema permits them. Scope, compiled-function entries and checking-context objects explicitly close their vocabularies so a checker cannot silently omit an unknown target or execution setting.

#### preamble

| Fields       | Description                                                          |
| ---          | ---                                                                  |
| title        | A short and descriptive title of the assurance document              |
| ?description | A more elaborate description                                         |
| ?version     | A version number for the assurance document itself                   |
| authors      | A non-empty list of authors of the document (free-form strings)      |
| created      | The creation date, as `YYYY-MM-DD`                                   |
| ?license     | A license under which the assurance document is distributed          |

#### blueprint

A reference to the blueprint the claims are about.

| Fields | Description                                                                              |
| ---    | ---                                                                                      |
| uri    | A URI from which the blueprint document can be retrieved                                 |
| ?hash  | A content digest of the blueprint document, as a [digest object](#digest-objects)        |

The `hash`, when present, MUST be computed over the raw bytes of the blueprint document exactly as retrieved from `uri`. Including it is RECOMMENDED: it makes the binding tamper-evident. Consumers MUST verify it when present and MUST treat the assurance document as *not applicable* to a blueprint whose bytes do not match. When `hash` is absent, consumers SHOULD signal that the binding to the blueprint document is unverified.

#### Checking contexts

`checkingContexts` maps document-local ids (`^[A-Za-z0-9_-]+$`) to artifact
references, each with `uri` and `hash`. A property's optional `checkingContext`
selects one entry. Selecting an unknown id is invalid. Multiple properties may
share an entry. Properties interpreted through the new compiled-interface checking
profile MUST select a context. Informal claims and other profiles need not do so.

The artifact's exact bytes must validate against
[checking-context.json](./schemas/checking-context.json) and match the declared
digest before use. Its fields are:

| Field | Meaning |
| --- | --- |
| `$schema` | The checking-context schema identifier |
| `profile` | A versioned checking-profile identifier; unknown profiles are not executable |
| `environment` | Digest-bound artifact pinning the evaluator, libraries, solver, tool options and any local changes |
| `execution` | Explicit semantics variant, resource accounting and acceptance interpretation |
| `targets` | The exact scoped scripts (purpose and parameter bindings) and functions (content hashes and wire interfaces) |

`execution.budget` is either `{ "kind": "cek-steps", "steps": n }` or
`{ "kind": "ledger-units", "exCPU": n, "exMem": m, "costModel": <artifact> }`.
The units cannot be mixed or converted by guessing. `semanticsVariant` is A–E.
`acceptance: "evaluation"` means evaluation outcomes only. `acceptance:
"ledger-script"` additionally requires ledger units, the cost-model artifact, and
`protocolVersion: { "major": n, "minor": m }`. It means the selected script phase,
not complete transaction validity. The profile checks language/protocol/semantics
compatibility and the language-specific result requirement. A consumer without
the declared evaluator or cost model reports not checked; it does not substitute
its defaults. Exhaustion is distinct from evaluation error and successful return.

Each target has `validator`, `purpose` and `parameters`. Targets must cover exactly
the property's scope, once each, and select existing blueprint invocations. The
parameter mode is either `universal` or `applied`. Universal mode requires the
formal proposition to quantify over every currently unapplied parameter and state
its domain premises; the label itself supplies no theorem. Applied mode contains
an ordered `values` array, a digest-bound `appliedScript` artifact and `appliedScriptHash`. Each value identifies a
`/parameters/i` entry and a digest-bound `term` artifact. The initial profile uses
closed UPLC terms serialized as Flat terms (not programs and not CBOR-wrapped).
All parameters must be bound once and in order; partial specialization requires
a separate blueprint with the remaining interface updated.

For applied mode, the consumer decodes and validates each term under its declared
encoding and applies the values to the exact template in order. It decodes the
`appliedScript` using CIP-57's single-CBOR program convention, requires structural
equality with that ordered application (without optimization), and recomputes
the language-tagged script hash from the supplied artifact bytes. Both Flat
terms and CBOR programs must decode completely, with no trailing payload. A mismatch invalidates the deployment binding. Failure to establish a
schema/domain premise prevents using a universal result for that deployment.
Every artifact URI resolves relative to the document containing that URI.

Machine-checked evidence for a property selecting a context MUST include
`checkingContextHash`, the digest of the exact context bytes used for that run.
A mismatch with the property's selected context makes that evidence stale, even
if its script hash still matches. `scriptHash` continues to identify the blueprint's
template; the applied hash is separate in the context. The reproducible artifact
also retains the original statements and input documents, so changed claims cannot
inherit evidence merely by retaining a property id. A missing or unverified
configuration or environment binding is never reported as a successful check.

#### digest objects

Everywhere a content digest appears, it is an object:

| Fields | Description                                                     |
| ---    | ---                                                             |
| alg    | The hash algorithm, e.g. `sha256`, `blake2b-256`                |
| digest | The lowercase, hex-encoded digest value                         |

#### languages and tools

Both fields are objects mapping a document-local identifier — a key matching `^[A-Za-z0-9_-]+$`, used by `formal.language` and `evidence.tool` references — to a registry entry:

| Fields       | Description                                            |
| ---          | ---                                                    |
| name         | The name of the language or tool                       |
| version      | A version number, in any format                        |
| ?uri         | A URI to the language specification or tool homepage   |
| ?description | An informative description                             |

This CIP deliberately does **not** restrict which specification languages or verification tools can be referenced; see the Rationale. A reference to a key absent from the corresponding registry makes the document invalid; consumers MUST reject such documents.

#### properties

The essence of the assurance document: a non-empty list of claimed properties. Each property is an object:

| Fields       | Description                                                                                       |
| ---          | ---                                                                                               |
| id           | An identifier unique within the document, matching `^[A-Za-z0-9_-]+$`                             |
| ?title       | A short and descriptive name for the property                                                     |
| scope        | An object with nonempty, duplicate-free `validators` and/or `functions` arrays selecting [validators](#referencing-validators) or assurance function ids |
| statement    | A [statement object](#statements): what is being claimed                                          |
| ?assumptions | A list of statement objects: hypotheses under which the claim holds                               |
| ?checkingContext | A key in `checkingContexts` selecting the interpretation and execution settings for this property |
| ?tags        | A list of free-form classification strings (e.g. `safety`, `authorization`)                       |
| ?evidence    | A list of [evidence records](#evidence-records); when absent or empty, the property is a stated, unverified claim |

#### Statements

A statement (used for both the claimed property and its assumptions) is an object:

| Fields  | Description                                                                       |
| ---     | ---                                                                               |
| text    | A natural-language statement of the property. REQUIRED.                           |
| ?formal | A formal counterpart of `text`, in a declared specification language              |

The natural-language `text` is deliberately mandatory: every reader of an assurance document can understand every claim, whatever tooling they have. The `formal` object, when present, has the fields:

| Fields   | Description                                                                        |
| ---      | ---                                                                                |
| language | A key of the document's `languages` registry                                       |
| ?source  | The formal statement itself, inline                                                |
| ?uri     | A URI from which the formal statement can be retrieved                             |
| ?uses    | An array of fragment ids from `formalFragments` whose definitions this statement uses |

At least one of `source` or `uri` MUST be present. `uses` belongs inside the
`formal` object, as defined in the meta-schema at
`$defs.statement.properties.formal.properties.uses`. It is optional: omitting it
declares no fragment dependencies. When present, its fragment ids and their
transitive `imports` supply shared definitions. Every reference MUST resolve,
including references in assumptions.

The formal statement MUST express the complete proposition, including its
quantified premises. The `assumptions` field documents premises represented in
that proposition or external deployment conditions; consumers MUST NOT silently
turn it into trusted axioms. Checking the proposition does not establish external
assumptions or the adequacy of its specification.

A language specification MUST define how scoped scripts and functions denote the compiled
programs and what execution/acceptance predicates mean. Naming a validator in
`scope` alone does not connect a proposition to that code. Consumers SHOULD check
this connection where their language permits it, and MUST distinguish such a
syntactic dependency check from semantic relevance or specification completeness.

#### formalFragments

`formalFragments` is an optional array of objects with required `id`, `language`,
and `source` fields and an optional `imports` array of fragment ids. Fragment ids
match `^[A-Za-z0-9_.-]+$` and MUST be unique. `language` resolves in the language
registry. All `imports` and `uses` references MUST resolve, and imports MUST be
acyclic, even in fragments unused by a checked property. Array order is immaterial.
Consumers make the entire declared dependency closure available; language profiles
define namespaces and compatibility between fragment languages. Definitions from
an undeclared fragment MUST NOT leak into a property's checking environment.
Consumers unaware of a language may display it without executing its source.

#### Referencing validators

A validator reference is a string that resolves against the blueprint's `validators` list as follows:

1. If exactly one validator has an `id` field equal to the reference, it resolves to that validator.
2. Otherwise, if exactly one validator has a `title` equal to the reference, it resolves to that validator.
3. Otherwise (zero or several matches), the reference is unresolvable and consumers MUST treat it as an error.

The coordinated [compiled-interface extension](../CIP-0057/extensions/compiled-interface#stable-identity) defines stable validator `id` values and requires them in its dialect. This CIP references those ids; it does not define a competing blueprint interface. Legacy CIP-57 documents may omit ids and use the title-based resolution rule below. Merely permitting an extra JSON field does not standardize its semantics.

```json
{
  "validators": [
    {
      "id": "escrow-spend",
      "title": "escrow.spend",
      "redeemer": { "...": "..." },
      "compiledCode": "...",
      "hash": "7b3c9d1e5f2a8b4c6d0e9f317a5b8c2d4e6f0a1b3c5d7e9f2a4b6c8d"
    }
  ]
}
```

#### Evidence records

Each evidence record documents one verification act performed against the property:

| Fields      | Description                                                                                     |
| ---         | ---                                                                                             |
| method      | How the verification was performed; see [methods](#methods)                                     |
| verifier    | A free-form string identifying who performed the verification                                   |
| ?tool       | A key of the document's `tools` registry. REQUIRED for machine-checked methods.                 |
| outcome     | One of `verified`, `falsified`, `partial`, `inconclusive`; see [outcomes](#outcomes)            |
| date        | The date the verification was performed, as `YYYY-MM-DD`                                        |
| ?functionHashes | Content digests keyed by scoped function id; required for machine-checked methods with function targets. |
| ?scriptHash | The blake2b-224 hash digest (56 hex characters) of the script the verification ran against. REQUIRED for machine-checked methods when the scope includes validators. |
| ?artifact   | A reference to the reproducible verification artifact. REQUIRED for machine-checked methods.    |
| ?checkingContextHash | Digest of the exact checking-context artifact used for this evidence; required for machine-checked evidence when the property selects a context |
| ?notes      | Free-form remarks (e.g. number of test cases, proof effort)                                     |

`scriptHash` is the on-chain script hash as defined by CIP-0057's validator `hash` field: a blake2b-224 digest of the serialised script, with language tag prefix. For parameterized validators, it is the hash of the *unapplied* validator template — the same value as the blueprint's own `hash` field for that validator.

The `artifact` object has the fields:

| Fields     | Description                                                                    |
| ---        | ---                                                                            |
| uri        | A URI from which the artifact can be retrieved                                 |
| hash       | A content digest of the artifact, as a [digest object](#digest-objects)        |
| ?mediaType | An informative media type, e.g. `application/gzip`                             |

Everything needed to re-run the verification (environment, commands, expected results) lives *inside* the artifact and is tool-specific; this CIP does not standardize it.

#### Methods

The `method` field is an **open** enumeration. This CIP defines the meaning of six values:

| Method          | Description                                                              | Machine-checked |
| ---             | ---                                                                      | ---             |
| `formal-proof`  | A machine-checked mathematical proof of the property                     | yes             |
| `smt-check`     | SMT verification through a trusted translation and solver, without a reconstructed proof | yes |
| `property-test` | Randomized/property-based testing against an executable statement       | yes             |
| `unit-test`     | A fixed suite of concrete test cases                                     | yes             |
| `audit`         | A structured review by an auditor (see [CIP-0052](../CIP-0052))          | no              |
| `manual-review` | An informal human review                                                 | no              |

`smt-check` evidence MUST identify the translation, solver, and relevant model revisions and options in its artifact. It MUST NOT be presented as a reconstructed kernel proof. Producers claiming `formal-proof` SHOULD identify the proof artifact, proof checker, and trusted axioms.

Producers MAY use other method strings. Consumers MUST accept unknown methods and treat them as opaque: display them, but attach no semantics. Method values are case-sensitive: `Formal-Proof` is an unknown method, not a formal proof. The four *machine-checked* methods carry stricter requirements (`tool` and `artifact` are REQUIRED, together with `scriptHash` for validator scopes and `functionHashes` for function scopes) because their whole point is reproducibility.

#### Outcomes

The `outcome` field is a **closed** enumeration:

| Outcome        | Description                                                                                  |
| ---            | ---                                                                                          |
| `verified`     | The method completed and supports the property (proof succeeded, tests passed, audit found no violation) |
| `falsified`    | A counterexample or violation was found                                                      |
| `partial`      | The property was established for a subset of the cases or configurations covered by the statement |
| `inconclusive` | Verification was attempted but reached no conclusion (e.g. timeout, tool limitation)         |

The `method` conveys the strength of an outcome: a `verified` property-test and a `verified` formal-proof are very different levels of assurance. Consumers SHOULD always present the method alongside the outcome and SHOULD NOT collapse evidence into a single unqualified "verified" badge.

#### Consumer obligations

A consumer of assurance documents:

1. MUST validate the document against the meta-schema referenced by its `$schema` and reject invalid documents.
2. MUST additionally reject documents that violate the constraints the meta-schema cannot express: `formal.language` or `evidence.tool` references that do not resolve in the corresponding registry, and property or fragment `id`s that are not unique within the document; unresolved fragment references (including in assumptions); and cyclic fragment imports.
3. MUST, when `blueprint.hash` is present, compare it against the actual blueprint bytes, and treat the assurance document as not applicable on mismatch.
4. MUST, when `scriptHash` is present on an evidence record, compare it against the resolved validator's `hash` in the blueprint, and flag the evidence as **stale** on mismatch. When the blueprint validator carries no `hash` (CIP-0057 makes it optional in the absence of `compiledCode`), consumers MUST treat the evidence as **unverifiable** against that validator — distinct from stale.
5. MUST verify an artifact's content digest before relying on the artifact's content; a consumer that cannot compute the declared `alg` MUST treat the artifact as unverified rather than skip the check.
6. MUST treat unresolvable or ambiguous validator references as errors.
7. MUST recompute a validator's script hash from the compiled bytes and the Plutus language tag before relying on the blueprint's declared `hash`. Inconsistent code/hash pairs are invalid.
8. MUST distinguish a fresh checking result from historical evidence. Recorded outcomes MUST NOT determine the expected fresh verdict or suppress rechecking of partial/inconclusive claims. Unsupported or unavailable formal sources MUST be reported as not checked, never verified.
9. MUST, when a property selects a checking context, resolve and digest-check it and its environment, validate target coverage and parameter bindings, and implement its profile before a fresh check. Machine-checked evidence must bind to those context bytes; mismatched context digests are stale.
10. MUST report an unverified binding when a digest algorithm cannot be checked; an executable verification profile MAY reject such a document outright. An unfetched remote artifact is unverified even if an independent fresh check succeeds.

#### Producers and executable language profiles

Producers SHOULD emit deterministic output and derive document authorship and dates
from project metadata. They MUST hash the blueprint's final written bytes, reject
ambiguous target identities, preserve formal dependencies, and avoid assigning
claims to validators they do not constrain. Compilation without verification
produces properties with no evidence.

The blueprint interface defines argument representation, argument order and calling
convention. Checking profiles consume that interface and define the formal model,
resource bounds and proof trust model; they MUST NOT silently override the wire
encoding or invent a different argument list. Checking settings are carried in
[checking contexts](#checking-contexts), outside the blueprint. A CEK step limit
is not a ledger execution budget, and exhausting it is not script rejection.
Template hashes do not identify parameter-applied deployments on their own.

The existing [UAL 0.5](https://github.com/input-output-hk/UniversalAnnotationLanguage)
prototype uses experimental blueprint `arguments` and `budget` fields. Migration
to this coordinated draft requires a new profile/version and changes to its
producer and consumer; the old example is retained as a regression fixture.
Its initial Blaster consumer performs SMT verification without reconstructed Lean
kernel proofs; evidence MUST disclose that distinction. Language/tool versions
alone do not pin the checking environment: reproducible artifacts must also pin
libraries, solver, settings, and semantics. Third-party formal source is executable
input and must be checked in an isolated environment.

### Examples

The following complete examples are also available as machine-readable files under [examples](./examples).

<details>
  <summary>Formal verification with Blaster (smt-check evidence, UAL formal statements, assumptions)</summary>

```json
{
  "$schema": "https://cips.cardano.org/cips/cipXXXX/schemas/assurance-v2.json",
  "preamble": {
    "title": "Escrow contract — formal verification assurance",
    "description": "Machine-checked safety properties of the escrow validator, verified with Blaster.",
    "version": "1.0.0",
    "authors": [
      "Input Output — Blaster team <blaster@iohk.io>"
    ],
    "created": "2026-08-11",
    "license": "CC-BY-4.0"
  },
  "blueprint": {
    "uri": "https://raw.githubusercontent.com/example-org/escrow/v1.2.0/plutus.json",
    "hash": {
      "alg": "sha256",
      "digest": "3f8a1c2b9d4e5f60718293a4b5c6d7e8f9012a3b4c5d6e7f8091a2b3c4d5e6f7"
    }
  },
  "languages": {
    "ual": {
      "name": "Universal Annotation Language",
      "version": "0.4",
      "uri": "https://github.com/input-output-hk/UniversalAnnotationLanguage",
      "description": "Property specification language used by Blaster."
    }
  },
  "tools": {
    "blaster": {
      "name": "Blaster",
      "version": "0.3.1",
      "uri": "https://github.com/input-output-hk/Lean-blaster",
      "description": "SMT-based formal verification tool for UPLC validators."
    }
  },
  "properties": [
    {
      "id": "no-locked-funds",
      "title": "Funds can always be recovered",
      "scope": {
        "validators": ["escrow-spend"]
      },
      "statement": {
        "text": "For every reachable state of the escrow, either the buyer or the seller can construct a transaction that spends the locked UTxO.",
        "formal": {
          "language": "ual",
          "uri": "https://raw.githubusercontent.com/example-org/escrow/v1.2.0/verification/no-locked-funds.ual"
        }
      },
      "assumptions": [
        {
          "text": "The datum of the escrow UTxO conforms to the blueprint's datum schema."
        },
        {
          "text": "The transaction validity interval is finite."
        }
      ],
      "tags": ["safety", "liveness"],
      "evidence": [
        {
          "method": "smt-check",
          "verifier": "Input Output — Blaster team",
          "tool": "blaster",
          "outcome": "verified",
          "date": "2026-08-01",
          "scriptHash": "7b3c9d1e5f2a8b4c6d0e9f317a5b8c2d4e6f0a1b3c5d7e9f2a4b6c8d",
          "artifact": {
            "uri": "https://github.com/example-org/escrow/releases/download/v1.2.0/escrow-proofs.tar.gz",
            "hash": {
              "alg": "sha256",
              "digest": "ab31c7e2f4d5968a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f708192a3b4c5d6"
            },
            "mediaType": "application/gzip"
          }
        }
      ]
    },
    {
      "id": "redeem-authorized",
      "title": "Only authorized parties can move funds",
      "scope": {
        "validators": ["escrow-spend"]
      },
      "statement": {
        "text": "Before the deadline, only a transaction signed by the buyer can spend the escrow UTxO; after the deadline, only a transaction signed by the seller can.",
        "formal": {
          "language": "ual",
          "uri": "https://raw.githubusercontent.com/example-org/escrow/v1.2.0/verification/redeem-authorized.ual"
        }
      },
      "assumptions": [
        {
          "text": "The datum of the escrow UTxO conforms to the blueprint's datum schema."
        }
      ],
      "tags": ["safety", "authorization"],
      "evidence": [
        {
          "method": "smt-check",
          "verifier": "Input Output — Blaster team",
          "tool": "blaster",
          "outcome": "verified",
          "date": "2026-08-01",
          "scriptHash": "7b3c9d1e5f2a8b4c6d0e9f317a5b8c2d4e6f0a1b3c5d7e9f2a4b6c8d",
          "artifact": {
            "uri": "https://github.com/example-org/escrow/releases/download/v1.2.0/escrow-proofs.tar.gz",
            "hash": {
              "alg": "sha256",
              "digest": "ab31c7e2f4d5968a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f708192a3b4c5d6"
            },
            "mediaType": "application/gzip"
          }
        }
      ]
    }
  ]
}
```
</details>

<details>
  <summary>Property testing with Aiken (minimal document: no languages registry, natural-language statement only)</summary>

```json
{
  "$schema": "https://cips.cardano.org/cips/cipXXXX/schemas/assurance-v2.json",
  "preamble": {
    "title": "hello_world — property-test assurance",
    "authors": [
      "Ada Lovelace <ada@example.com>"
    ],
    "created": "2026-08-11"
  },
  "blueprint": {
    "uri": "https://raw.githubusercontent.com/aiken-lang/aiken/v1.1.5/examples/hello_world/plutus.json"
  },
  "tools": {
    "aiken": {
      "name": "Aiken",
      "version": "1.1.5",
      "uri": "https://aiken-lang.org"
    }
  },
  "properties": [
    {
      "id": "requires-owner-signature",
      "title": "Spending requires the owner's signature and the magic message",
      "scope": {
        "validators": ["hello_world"]
      },
      "statement": {
        "text": "The validator succeeds only if the transaction is signed by the public key hash stored in the datum's 'owner' field and the redeemer's 'msg' field is exactly the UTF-8 bytes of 'Hello, World!'."
      },
      "evidence": [
        {
          "method": "property-test",
          "verifier": "Ada Lovelace",
          "tool": "aiken",
          "outcome": "verified",
          "date": "2026-07-15",
          "scriptHash": "5e1e8fa84f2b557ddc362329413caa3fd89a1be26bfd24be05ce0a02",
          "artifact": {
            "uri": "https://github.com/example-org/hello-world-tests/archive/refs/tags/v1.0.tar.gz",
            "hash": {
              "alg": "sha256",
              "digest": "d9e0f1a2b3c4d5e6f708192a3b4c5d6e7f8091a2b3c4d5e6f70819a2b3c4d5e6"
            }
          },
          "notes": "500 randomized scenarios generated with Aiken's property-testing framework; suite rejects missing signatures and wrong messages."
        }
      ]
    }
  ]
}
```
</details>

## Rationale: How does this CIP achieve its goals?

### Why a detached document rather than a blueprint extension

An earlier draft of this proposal extended CIP-0057 blueprints in place, through an additional `$vocabulary` entry and new keywords inside `plutus.json`. The detached design was chosen instead, for three reasons:

1. **Third-party publishing.** The parties best placed to make assurance claims — auditors, independent verification teams — usually do not control the contract's repository. A detached document lets them publish claims about deployed code without any cooperation from the developers, and lets several independent assurance documents about the same blueprint coexist.
2. **Blueprints are compiler output.** `plutus.json` is typically regenerated on every build by the smart-contract framework (Aiken, OpShin, plu-ts, ...). Hand-maintained assurance data embedded in a generated file would be overwritten on each compilation, or would require every framework to learn how to preserve and merge it.
3. **No dialect machinery needed.** An assurance document is not a JSON Schema dialect extension; it is its own document type. Identifying the format by a versioned `$schema` URI is simpler than the `$vocabulary` opt-in mechanism, and the blueprint interface is standardized independently in the coordinated extension.

Developers who want the "blueprint carries its claims" experience simply ship an `assurance.json` next to their `plutus.json`.

### Why the specification language is free

There is today no consensus — on Cardano or elsewhere — on a single property language for smart contracts, and mandating one would gate adoption of this CIP on the outcome of that debate. Instead, the format standardizes the *envelope*: what is claimed (in mandatory natural language), by whom, about which exact code, with what outcome, and where the evidence lives. Formal statements are optional and declare their language through the `languages` registry, so a Blaster user can reference Universal Annotation Language statements while an Aiken user references executable property tests, without either being privileged by the format. If the ecosystem later converges on a standard property language, it slots into the registry like any other.

The mandatory natural-language `text` guarantees that every claim remains legible to every reader — including the users whose funds are at stake — regardless of which formal languages and tools they know.

### Why no signatures in v1

Evidence records name their verifier, but nothing in this version authenticates that name cryptographically. This is deliberate: the trust model of this CIP rests on *reproducibility* — anyone can fetch the artifact, check its digest, re-run the verification and compare verdicts — not on the authority of the verifier. Signing evidence records (e.g. with [CIP-0008](../CIP-0008) message signing or COSE) would add real value against lazy consumers who do not re-run verifications, but it drags key management and identity questions into the format. It can be layered on in a future version, or by wrapping assurance documents in an external attestation, without changing the format defined here.

### Open methods, closed outcomes

New verification methods keep appearing (symbolic execution, model checking, fuzzing variants, ...), so `method` is an open enumeration: unknown values are legal and treated as opaque by consumers. Outcomes, by contrast, are what consumers compare and display at a glance, so `outcome` is a small closed enumeration with fixed semantics. The strength of an outcome is conveyed by its method — which is why consumers are told to always present the two together.

### Relation to CIP-0052

[CIP-0052](../CIP-0052) defines best practices for conducting audits of Cardano smart contracts. This CIP is complementary: it gives an audit performed along CIP-0052 lines a standard, machine-readable, code-bound publication format — an evidence record with `method: audit` whose artifact is the audit report itself, hash-pinned and tied to the audited script hashes.

### Validators only

Assurance documents annotate validators — the unit of description in CIP-0057 blueprints. Finer-grained specifications (e.g. per-function contracts within a validator) remain out of scope. Richer interface descriptions are handled by the coordinated blueprint extension, not duplicated in assurance documents.

### Backward compatibility

The assurance envelope can reference existing CIP-57 documents, including legacy
title-based references. Executable checks using the compiled-interface profile
require that extension's dialect and stable ids. Older consumers may display
unsupported interfaces but MUST NOT claim to have checked them.

This draft uses `assurance-v2.json` because an external checking context affects a
proposition's interpretation: silently ignoring it would be unsafe. The earlier
unpublished `assurance.json` schema is preserved for the UAL 0.5 regression example.
These are draft version identifiers for editor review, not two published CIPs.
A consumer must recognize the selected schema and checking profile before executing
a claim. Existing evidence is not automatically upgraded to a new profile.

## Path to Active

### Acceptance Criteria

- [ ] Agree with CIP editors on the placement of the coordinated blueprint extension and draft identifiers.
- [ ] Demonstrate producer/checker migration, including Data/native/Scott representations and applied-script binding.
- [ ] The meta-schema is published and has remained stable through community review.
- [ ] At least one producer toolchain emits assurance documents (Blaster, planned).
- [ ] At least one consumer tool validates assurance documents, including binding checks (blueprint hash, validator resolution, script hash comparison) and artifact digest verification.
- [ ] At least one assurance document is published for a real-world, deployed contract.

### Implementation Plan

- [ ] Blaster to emit an `assurance.json` (UAL formal statements, `smt-check` evidence records, reproducible run artifacts) for the validators it verifies.
- [ ] Develop a standalone checker that performs the consumer obligations of this specification: meta-schema validation, binding checks, and artifact digest verification.
- [ ] Engage explorer, registry and wallet developers on surfacing assurance claims to end users.

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).

### Legacy executable UAL example

[The generated game assurance](./examples/assurance-ual-generated.json) binds to
[its compiled blueprint](./examples/ual-game-blueprint.json). It contains UAL 0.5
claims about the Plutus-apps guessing-game rule, ported to current Plinth: matching
hashes succeed, nonmatching hashes fail, and malformed data fails. The formal
claims use SHA-256 as an opaque function and make no collision-freedom assumption.
The producer emits no evidence. Fresh verification and a separate concrete hash
vector test are provided by PlutusCoreBlaster's `Tests/BlueprintVerify/run_generated.py`.
Only after those checks succeed does the runner write a separate assurance document
with `smt-check` evidence bound to the script hash and a reproducible run artifact.

### Draft coordinated example

[The interface-aware assurance](./examples/interface-game-assurance.json) references
[the same compiled game with explicit interface metadata](./examples/interface-game-blueprint.json),
[a checking context](./examples/game-checking.json), and
[an illustrative environment manifest](./examples/game-environment.json). The
compiled bytes are unchanged, but these documents are migration targets, not
outputs supported by the current UAL 0.5 checker. They carry no verification evidence.
The environment manifest explicitly lists prerequisites before execution.

See the [editor discussion notes](./INTERFACE-COORDINATION.md) for the proposal split
and the [draft checking profile](./profiles/uplc-step-check.md) for execution rules.


### Compiled library functions (assurance-v2 draft)

The optional `functions` object maps stable function ids to compiled UPLC and
its interface. Each entry requires `compiledCode` (lowercase hex),
`serialization: "cbor-flat"` (one CBOR bytestring containing Flat UPLC),
`hash` (SHA-256 over the decoded compiledCode bytes), `plutusVersion`, ordered
`arguments` wire schemas, and a `result` wire schema. Function schemas use the
CIP-57 compiled-interface value vocabulary. References resolve against the
assurance document's optional `definitions` registry, preserving recursive graphs.
The function id is its registry key. There is no ledger invocation convention.

Properties select them with `scope.functions`; `scope.validators` continues to
select ledger scripts from the referenced blueprint. Either or both arrays may
be present; present arrays must be nonempty and duplicate-free. Ids are unique
across functions and validators. Checking contexts cover the scope exactly;
a function target contains `function`, `functionHash`, and `functionInterface`.
The latter copies `serialization`, `plutusVersion`, ordered `arguments`, and
`result` from the registry, plus the assurance `definitions` registry (omission
means empty). The profile requires exact equality, binding their
interpretation into `checkingContextHash`. The profile checks
that digest against both the registry and actual bytes before execution.

Machine evidence for a function scope includes `functionHashes`, keyed by every
scoped function id, as well as its artifact and checkingContextHash. Script
scopes continue to use scriptHash. Neither historical evidence nor a matching
content digest alone proves a property. A fresh check evaluates the exact formal
statement under the declared interface and checking context.

Helper code and its specifications belong in this assurance document. They do
not become CIP-57 validator entries. A proof about separately compiled helper
bytes is not automatically a proof about optimized validator code that used the
same source function; a validator property or equivalence argument is needed.

The [compiled helper example](./examples/compiled-function-assurance.json) and
[its checking context](./examples/function-checking.json) illustrate the function
registry using actual compiled bytes. Their environment is illustrative and the
example carries no evidence; capture a real environment before execution.
