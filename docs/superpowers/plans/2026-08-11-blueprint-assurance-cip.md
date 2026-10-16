# Plutus Blueprint Assurance Documents CIP — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rewrite `CIP-XXXX/README.md` as the "Plutus Blueprint Assurance Documents" CIP and add a `CIP-XXXX/schemas/assurance.json` meta-schema plus two example documents, per the approved design in `docs/superpowers/specs/2026-08-11-blueprint-assurance-cip-design.md`.

**Architecture:** The CIP defines a *detached* assurance document (`assurance.json`) that publishes reproducible claims about validators in a CIP-57 blueprint. Deliverables are pure documentation + JSON Schema: example documents act as the test suite, validated against the meta-schema with Python's `jsonschema` (Draft 2020-12). The README embeds the example files verbatim; a substring check keeps them in sync.

**Tech Stack:** Markdown (CIP-1 conventions), JSON Schema 2020-12, `python3` + `jsonschema` 4.17.3 (already installed) for validation.

**Working directory:** `/Users/romainsoulat/Documents/GitHub/CIPs` (branch `cip/extended-blueprints-verification`).

**Repo conventions that MUST be respected:**
- Frontmatter `Status: Proposed` (CIP-1 allows only Proposed / Active / Inactive).
- Section headings exactly: `## Abstract`, `## Motivation: why is this CIP necessary?`, `## Specification`, `## Rationale: how does this CIP achieve its goals?`, `## Path to Active` (with `### Acceptance Criteria`, `### Implementation Plan`), `## Copyright`.
- No H1 title in the body (title lives in frontmatter only, like CIP-57).
- Commits on this branch only; the docs/superpowers commits are droppable and must NOT go into the upstream PR.

---

### Task 1: Validation harness + formal-proof example (the first "failing test")

**Files:**
- Create: `CIP-XXXX/examples/assurance-formal-proof.json`

- [ ] **Step 1: Write the formal-proof example document**

Run:

```bash
mkdir -p CIP-XXXX/examples && cat > CIP-XXXX/examples/assurance-formal-proof.json <<'JSONEOF'
{
  "$schema": "https://cips.cardano.org/cips/cipXXXX/schemas/assurance.json",
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
      "uri": "https://github.com/input-output-hk/ual-spec",
      "description": "Property specification language used by Blaster."
    }
  },
  "tools": {
    "blaster": {
      "name": "Blaster",
      "version": "0.3.1",
      "uri": "https://github.com/input-output-hk/blaster",
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
          "method": "formal-proof",
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
          "method": "formal-proof",
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
JSONEOF
python3 -m json.tool CIP-XXXX/examples/assurance-formal-proof.json > /dev/null && echo "WELL-FORMED JSON"
```

Expected: `WELL-FORMED JSON`

- [ ] **Step 2: Run schema validation to verify it fails (schema doesn't exist yet)**

Run:

```bash
python3 - CIP-XXXX/examples/assurance-formal-proof.json <<'PYEOF'
import json, sys
from jsonschema import Draft202012Validator
schema = json.load(open("CIP-XXXX/schemas/assurance.json"))
Draft202012Validator.check_schema(schema)
v = Draft202012Validator(schema)
doc = json.load(open(sys.argv[1]))
errs = sorted(v.iter_errors(doc), key=lambda e: list(e.absolute_path))
for e in errs:
    print("/".join(map(str, e.absolute_path)) or "<root>", "-", e.message)
print("RESULT:", "VALID" if not errs else "INVALID (%d errors)" % len(errs))
PYEOF
```

Expected: FAIL with `FileNotFoundError: ... 'CIP-XXXX/schemas/assurance.json'` — the meta-schema does not exist yet. (Note: `CIP-XXXX/schemas/` currently does not exist at all; only `CIP-XXXX/README.md` does.)

---

### Task 2: Property-test example + negative example

**Files:**
- Create: `CIP-XXXX/examples/assurance-property-test.json`
- Create: `/private/tmp/claude-501/-Users-romainsoulat-Documents-GitHub-CIPs/427973fc-e8ff-4874-a0af-2cd4139b5480/scratchpad/assurance-negative.json` (NOT committed — pure test fixture; if this session scratchpad no longer exists, any directory outside the repo works)

- [ ] **Step 1: Write the property-test example (deliberately minimal: no `languages`, natural-language statement only, references CIP-57's real hello_world example)**

Run:

```bash
cat > CIP-XXXX/examples/assurance-property-test.json <<'JSONEOF'
{
  "$schema": "https://cips.cardano.org/cips/cipXXXX/schemas/assurance.json",
  "preamble": {
    "title": "hello_world — property-test assurance",
    "authors": [
      "Ada Lovelace <ada@example.com>"
    ],
    "created": "2026-08-11"
  },
  "blueprint": {
    "uri": "https://raw.githubusercontent.com/aiken-lang/aiken/main/examples/hello_world/plutus.json"
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
JSONEOF
python3 -m json.tool CIP-XXXX/examples/assurance-property-test.json > /dev/null && echo "WELL-FORMED JSON"
```

Expected: `WELL-FORMED JSON`

- [ ] **Step 2: Write the negative example (must FAIL validation once the schema exists)**

It violates two rules: (a) evidence with a machine-checked `method` (`formal-proof`) missing `tool`, `scriptHash`, and `artifact`; (b) an `outcome` value outside the closed enum.

Run:

```bash
SCRATCH=/private/tmp/claude-501/-Users-romainsoulat-Documents-GitHub-CIPs/427973fc-e8ff-4874-a0af-2cd4139b5480/scratchpad
mkdir -p "$SCRATCH" && cat > "$SCRATCH"/assurance-negative.json <<'JSONEOF'
{
  "$schema": "https://cips.cardano.org/cips/cipXXXX/schemas/assurance.json",
  "preamble": {
    "title": "Negative test document",
    "authors": ["Test Fixture"],
    "created": "2026-08-11"
  },
  "blueprint": {
    "uri": "https://example.com/plutus.json"
  },
  "properties": [
    {
      "id": "bad-property",
      "scope": {
        "validators": ["some-validator"]
      },
      "statement": {
        "text": "Claims a formal proof but omits tool, scriptHash and artifact."
      },
      "evidence": [
        {
          "method": "formal-proof",
          "verifier": "Nobody",
          "outcome": "verified",
          "date": "2026-08-11"
        },
        {
          "method": "audit",
          "verifier": "Nobody",
          "outcome": "passed",
          "date": "2026-08-11"
        }
      ]
    }
  ]
}
JSONEOF
python3 -m json.tool "$SCRATCH"/assurance-negative.json > /dev/null && echo "WELL-FORMED JSON"
```

Expected: `WELL-FORMED JSON`

---

### Task 3: The meta-schema

**Files:**
- Create: `CIP-XXXX/schemas/assurance.json`

- [ ] **Step 1: Write the meta-schema**

Run:

```bash
mkdir -p CIP-XXXX/schemas && cat > CIP-XXXX/schemas/assurance.json <<'JSONEOF'
{
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "https://cips.cardano.org/cips/cipXXXX/schemas/assurance.json",
    "title": "Plutus Blueprint Assurance Document",
    "type": "object",
    "required": [
        "$schema",
        "preamble",
        "blueprint",
        "properties"
    ],
    "properties": {
        "$schema": {
            "type": "string",
            "const": "https://cips.cardano.org/cips/cipXXXX/schemas/assurance.json"
        },
        "preamble": {
            "$ref": "#/$defs/preamble"
        },
        "blueprint": {
            "$ref": "#/$defs/blueprintReference"
        },
        "languages": {
            "type": "object",
            "propertyNames": {
                "pattern": "^[A-Za-z0-9_-]+$"
            },
            "additionalProperties": {
                "$ref": "#/$defs/registryEntry"
            }
        },
        "tools": {
            "type": "object",
            "propertyNames": {
                "pattern": "^[A-Za-z0-9_-]+$"
            },
            "additionalProperties": {
                "$ref": "#/$defs/registryEntry"
            }
        },
        "properties": {
            "type": "array",
            "items": {
                "$ref": "#/$defs/property"
            },
            "minItems": 1
        }
    },
    "$defs": {
        "preamble": {
            "type": "object",
            "required": [
                "title",
                "authors",
                "created"
            ],
            "properties": {
                "title": {
                    "type": "string"
                },
                "description": {
                    "type": "string"
                },
                "version": {
                    "type": "string"
                },
                "authors": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "minItems": 1
                },
                "created": {
                    "$ref": "#/$defs/date"
                },
                "license": {
                    "type": "string"
                }
            }
        },
        "blueprintReference": {
            "type": "object",
            "required": [
                "uri"
            ],
            "properties": {
                "uri": {
                    "type": "string"
                },
                "hash": {
                    "$ref": "#/$defs/digest"
                }
            }
        },
        "registryEntry": {
            "type": "object",
            "required": [
                "name",
                "version"
            ],
            "properties": {
                "name": {
                    "type": "string"
                },
                "version": {
                    "type": "string"
                },
                "uri": {
                    "type": "string"
                },
                "description": {
                    "type": "string"
                }
            }
        },
        "property": {
            "type": "object",
            "required": [
                "id",
                "scope",
                "statement"
            ],
            "properties": {
                "id": {
                    "type": "string",
                    "pattern": "^[A-Za-z0-9_-]+$"
                },
                "title": {
                    "type": "string"
                },
                "scope": {
                    "type": "object",
                    "required": [
                        "validators"
                    ],
                    "properties": {
                        "validators": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            },
                            "minItems": 1
                        }
                    }
                },
                "statement": {
                    "$ref": "#/$defs/statement"
                },
                "assumptions": {
                    "type": "array",
                    "items": {
                        "$ref": "#/$defs/statement"
                    }
                },
                "tags": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                },
                "evidence": {
                    "type": "array",
                    "items": {
                        "$ref": "#/$defs/evidenceRecord"
                    }
                }
            }
        },
        "statement": {
            "type": "object",
            "required": [
                "text"
            ],
            "properties": {
                "text": {
                    "type": "string",
                    "minLength": 1
                },
                "formal": {
                    "type": "object",
                    "required": [
                        "language"
                    ],
                    "properties": {
                        "language": {
                            "type": "string"
                        },
                        "source": {
                            "type": "string"
                        },
                        "uri": {
                            "type": "string"
                        }
                    },
                    "anyOf": [
                        {
                            "required": [
                                "source"
                            ]
                        },
                        {
                            "required": [
                                "uri"
                            ]
                        }
                    ]
                }
            }
        },
        "evidenceRecord": {
            "type": "object",
            "required": [
                "method",
                "verifier",
                "outcome",
                "date"
            ],
            "properties": {
                "method": {
                    "type": "string"
                },
                "verifier": {
                    "type": "string"
                },
                "tool": {
                    "type": "string"
                },
                "outcome": {
                    "type": "string",
                    "enum": [
                        "verified",
                        "falsified",
                        "partial",
                        "inconclusive"
                    ]
                },
                "date": {
                    "$ref": "#/$defs/date"
                },
                "scriptHash": {
                    "type": "string",
                    "pattern": "^[0-9a-f]{56}$",
                    "description": "Blake2b-224 hash digest of the script the verification ran against; for parameterized validators, the hash of the unapplied template."
                },
                "artifact": {
                    "$ref": "#/$defs/artifact"
                },
                "notes": {
                    "type": "string"
                }
            },
            "if": {
                "properties": {
                    "method": {
                        "enum": [
                            "formal-proof",
                            "property-test",
                            "unit-test"
                        ]
                    }
                },
                "required": [
                    "method"
                ]
            },
            "then": {
                "required": [
                    "tool",
                    "scriptHash",
                    "artifact"
                ]
            }
        },
        "artifact": {
            "type": "object",
            "required": [
                "uri",
                "hash"
            ],
            "properties": {
                "uri": {
                    "type": "string"
                },
                "hash": {
                    "$ref": "#/$defs/digest"
                },
                "mediaType": {
                    "type": "string"
                }
            }
        },
        "digest": {
            "type": "object",
            "description": "A content digest: hash algorithm plus lowercase hex-encoded digest value.",
            "required": [
                "alg",
                "digest"
            ],
            "properties": {
                "alg": {
                    "type": "string"
                },
                "digest": {
                    "type": "string",
                    "pattern": "^([0-9a-f]{2})+$"
                }
            }
        },
        "date": {
            "type": "string",
            "pattern": "^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$"
        }
    }
}
JSONEOF
python3 -m json.tool CIP-XXXX/schemas/assurance.json > /dev/null && echo "WELL-FORMED JSON"
```

Expected: `WELL-FORMED JSON`

- [ ] **Step 2: Validate both positive examples — must PASS**

Run:

```bash
for f in CIP-XXXX/examples/assurance-formal-proof.json CIP-XXXX/examples/assurance-property-test.json; do
python3 - "$f" <<'PYEOF'
import json, sys
from jsonschema import Draft202012Validator
schema = json.load(open("CIP-XXXX/schemas/assurance.json"))
Draft202012Validator.check_schema(schema)
v = Draft202012Validator(schema)
doc = json.load(open(sys.argv[1]))
errs = sorted(v.iter_errors(doc), key=lambda e: list(e.absolute_path))
for e in errs:
    print("/".join(map(str, e.absolute_path)) or "<root>", "-", e.message)
print(sys.argv[1], "RESULT:", "VALID" if not errs else "INVALID (%d errors)" % len(errs))
PYEOF
done
```

Expected: both lines end with `RESULT: VALID` and no error lines are printed.

- [ ] **Step 3: Validate the negative example — must FAIL**

Run:

```bash
python3 - /private/tmp/claude-501/-Users-romainsoulat-Documents-GitHub-CIPs/427973fc-e8ff-4874-a0af-2cd4139b5480/scratchpad/assurance-negative.json <<'PYEOF'
import json, sys
from jsonschema import Draft202012Validator
schema = json.load(open("CIP-XXXX/schemas/assurance.json"))
Draft202012Validator.check_schema(schema)
v = Draft202012Validator(schema)
doc = json.load(open(sys.argv[1]))
errs = sorted(v.iter_errors(doc), key=lambda e: list(e.absolute_path))
for e in errs:
    print("/".join(map(str, e.absolute_path)) or "<root>", "-", e.message)
print(sys.argv[1], "RESULT:", "VALID" if not errs else "INVALID (%d errors)" % len(errs))
PYEOF
```

Expected: `RESULT: INVALID` with errors that include the missing `tool`, `scriptHash`, `artifact` requirements (from the `then` clause) and `'passed' is not one of ['verified', 'falsified', 'partial', 'inconclusive']`.

- [ ] **Step 4: Commit**

```bash
git add CIP-XXXX/schemas/assurance.json CIP-XXXX/examples/
git commit -m "CIP-XXXX: add assurance document meta-schema and examples

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 4: README part 1 — frontmatter, Abstract, Motivation

**Files:**
- Modify (full overwrite): `CIP-XXXX/README.md`

- [ ] **Step 1: Overwrite the README with frontmatter + Abstract + Motivation**

Note this intentionally replaces the entire previous draft (including its HTML comments and the old `$vocabulary` design).

Run:

```bash
cat > CIP-XXXX/README.md <<'MDEOF'
---
CIP: XXXX
Title: Plutus Blueprint Assurance Documents
Category: Tools
Status: Proposed
Authors:
    - Jean-Frédéric Etienne <jean-frederic.etienne@iohk.io>
    - Mark Petruska <mark.petruska@iohk.io>
    - Romain Soulat <romain.soulat@iohk.io>
Implementors: []
Discussions:
    - https://github.com/cardano-foundation/CIPs/pull/?
Created: 2026-06-16
License: CC-BY-4.0
---

## Abstract

A [CIP-0057](../CIP-0057) blueprint describes the binary interface of a Plutus validator — its datum, redeemer and parameter schemas — alongside its compiled code. It says nothing about the validator's expected behaviour or the guarantees it provides.

This CIP defines the **assurance document**: a standalone, machine-readable JSON document through which any party — the contract's developers, an external auditor, or an independent community member — can publish claims about the validators described in a blueprint. Each claim states a property in natural language, optionally accompanied by a formal statement in a declared specification language, and is backed by zero or more evidence records stating who verified it, by what method (formal proof, property test, unit test, audit, manual review), with which tool, with what outcome, against which script hash, and where a reproducible verification artifact can be retrieved.

A third party can take an assurance document, confirm that it concerns the exact compiled code shipped in the blueprint, fetch the referenced artifacts, re-run the verification, and obtain the same verdicts. Trust rests on the reproducibility of the evidence and the soundness of the verification tools — not on the author's word.

## Motivation: why is this CIP necessary?

[CIP-0057](../CIP-0057) makes a validator's interface legible; it does not expose anything about the validator's behaviour. Today, "this validator is safe" is established by an off-chain, largely manual process whose end product is typically a PDF report from a trusted auditor. There is no standard, machine-readable way for developers or auditors to state which properties a validator satisfies, how those properties were verified, and how anyone can check the verification themselves.

The blueprint ecosystem is the natural anchor for such claims: a blueprint already carries the compiled validator, the datum and redeemer shapes, the required parameters, and a hash digest linking the validator to on-chain addresses. What is missing is a standard companion format for behavioural claims that binds to those elements.

This proposal enables, building directly on the use cases CIP-0057 already lists:

- **Reproducible verification**: anyone can re-derive a validator's verdicts from the referenced artifacts, rather than trusting an assertion.
- **Communicating guarantees**: wallets, explorers, and registries can display which properties are claimed for a validator, by whom, with what method and outcome — and whether the evidence still matches the deployed code.
- **Third-party assurance**: auditors and community members can publish assurance documents about a deployed contract *without any cooperation from its developers*, and several independent assurance documents about the same blueprint can coexist.
- **Health monitoring of live DApps**: the assumptions under which properties were verified are stated explicitly, so they can be monitored live to check that a running system stays within its verified envelope.
- **Specification-first development**: a property with no evidence records is a stated, unverified claim — a machine-readable specification target that implementations and verification efforts can work towards.
MDEOF
echo "WRITTEN"
```

Expected: `WRITTEN`

- [ ] **Step 2: Verify frontmatter structure**

Run: `head -16 CIP-XXXX/README.md`

Expected: frontmatter delimited by `---` lines, `Status: Proposed`, title `Plutus Blueprint Assurance Documents`.

- [ ] **Step 3: Commit**

```bash
git add CIP-XXXX/README.md
git commit -m "CIP-XXXX: rewrite frontmatter, abstract and motivation for detached assurance documents

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 5: README part 2 — Specification

**Files:**
- Modify (append): `CIP-XXXX/README.md`

- [ ] **Step 1: Append the Specification section**

Run:

````bash
cat >> CIP-XXXX/README.md <<'MDEOF'

## Specification

The key words "MUST", "MUST NOT", "REQUIRED", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119).

### Overview

This specification introduces the notion of an **assurance document**: a standalone JSON document that publishes claims about the on-chain validators described by a [CIP-0057](../CIP-0057) blueprint.

An assurance document is *detached*: it is a separate document from the blueprint, and this CIP requires no change to `plutus.json`. Anyone — the contract's developers, an external auditor, an independent community member — can author and publish an assurance document about any blueprint. Multiple assurance documents about the same blueprint can coexist independently.

By convention, an assurance document authored by the contract developers is named `assurance.json` and located next to `plutus.json` at the root of the project's repository, to facilitate discoverability. Third-party documents can be published anywhere.

The meta-schema for assurance documents (i.e. the schema used for validating assurance documents themselves) is given [in annexe](./schemas/assurance.json). An assurance document identifies the format version it complies with through its `$schema` field.

A **producer** is any tool or person authoring assurance documents. A **consumer** is any tool interpreting them (e.g. a wallet, an explorer, a verification checker).

### Document structure

The document itself is a JSON object with the following fields:

| Fields      | Description                                                        |
| ---         | ---                                                                |
| `$schema`   | URI identifying the assurance document format version (required)   |
| preamble    | An object with meta-information about the assurance document       |
| blueprint   | A reference to the blueprint the claims are about                  |
| ?languages  | A registry of specification languages used by formal statements    |
| ?tools      | A registry of verification tools referenced by evidence records    |
| properties  | The list of claimed properties                                     |

#### `$schema`

The value of this field MUST be the URI of the meta-schema this document complies with. For this version of the specification, it is:

```
https://cips.cardano.org/cips/cipXXXX/schemas/assurance.json
```

The meta-schema pins this value with a `const`: a document claiming compliance with this version of the format carries exactly this URI.

Any breaking change to this specification MUST be published under a new URI. Additions of OPTIONAL fields MAY occur under the same URI. To make such additions possible, objects in an assurance document are deliberately open: consumers MUST ignore fields they do not recognize.

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

The `hash`, when present, MUST be computed over the raw bytes of the blueprint document exactly as retrieved from `uri`. Including it is RECOMMENDED: it makes the binding tamper-evident. Consumers MUST verify it when present and MUST treat the assurance document as *not applicable* to a blueprint whose bytes do not match.

#### digest objects

Everywhere a content digest appears, it is an object:

| Fields | Description                                                     |
| ---    | ---                                                             |
| alg    | The hash algorithm, e.g. `sha256`, `blake2b-256`                |
| digest | The lowercase, hex-encoded digest value                         |

#### languages and tools

Both fields are objects mapping a document-local identifier (used by `formal.language` and `evidence.tool` references) to a registry entry:

| Fields       | Description                                            |
| ---          | ---                                                    |
| name         | The name of the language or tool                       |
| version      | A version number, in any format                        |
| ?uri         | A URI to the language specification or tool homepage   |
| ?description | An informative description                             |

This CIP deliberately does **not** restrict which specification languages or verification tools can be referenced; see the Rationale. A reference to a key absent from the corresponding registry makes the document invalid; consumers MUST reject such documents.

#### properties

The essence of the assurance document: a list of claimed properties. Each property is an object:

| Fields       | Description                                                                                       |
| ---          | ---                                                                                               |
| id           | An identifier unique within the document, matching `^[A-Za-z0-9_-]+$`                             |
| ?title       | A short and descriptive name for the property                                                     |
| scope        | An object with a field `validators`: a non-empty list of [validator references](#referencing-validators) |
| statement    | A [statement object](#statements): what is being claimed                                          |
| ?assumptions | A list of statement objects: hypotheses under which the claim holds                               |
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

At least one of `source` or `uri` MUST be present.

#### Referencing validators

A validator reference is a string that resolves against the blueprint's `validators` list as follows:

1. If exactly one validator has an `id` field equal to the reference, it resolves to that validator.
2. Otherwise, if exactly one validator has a `title` equal to the reference, it resolves to that validator.
3. Otherwise (zero or several matches), the reference is unresolvable and consumers MUST treat it as an error.

To make references robust, this CIP RECOMMENDS that blueprint producers include in each validator entry an OPTIONAL field `id`: a string unique within the blueprint, stable across renames of the validator's `title`. The CIP-0057 meta-schema permits additional fields on validator objects, so blueprints carrying `id` fields remain valid CIP-0057 blueprints, and tools unaware of this CIP ignore them.

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
| ?scriptHash | The blake2b-224 hash digest (56 hex characters) of the script the verification ran against. REQUIRED for machine-checked methods. |
| ?artifact   | A reference to the reproducible verification artifact. REQUIRED for machine-checked methods.    |
| ?notes      | Free-form remarks (e.g. number of test cases, proof effort)                                     |

For parameterized validators, `scriptHash` is the hash of the *unapplied* validator template — the same value as the blueprint's own `hash` field for that validator.

The `artifact` object has the fields:

| Fields     | Description                                                                    |
| ---        | ---                                                                            |
| uri        | A URI from which the artifact can be retrieved                                 |
| hash       | A content digest of the artifact, as a [digest object](#digest-objects)        |
| ?mediaType | An informative media type, e.g. `application/gzip`                             |

Everything needed to re-run the verification (environment, commands, expected results) lives *inside* the artifact and is tool-specific; this CIP does not standardize it.

#### Methods

The `method` field is an **open** enumeration. This CIP defines the meaning of five values:

| Method          | Description                                                              | Machine-checked |
| ---             | ---                                                                      | ---             |
| `formal-proof`  | A machine-checked mathematical proof of the property                     | yes             |
| `property-test` | Randomized/property-based testing against an executable statement       | yes             |
| `unit-test`     | A fixed suite of concrete test cases                                     | yes             |
| `audit`         | A structured review by an auditor (see [CIP-0052](../CIP-0052))          | no              |
| `manual-review` | An informal human review                                                 | no              |

Producers MAY use other method strings. Consumers MUST accept unknown methods and treat them as opaque: display them, but attach no semantics. Method values are case-sensitive: `Formal-Proof` is an unknown method, not a formal proof. The three *machine-checked* methods carry stricter requirements (`tool`, `scriptHash` and `artifact` are REQUIRED) because their whole point is reproducibility.

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

1. MUST validate the document against the meta-schema referenced by its `$schema` and reject invalid documents, including documents whose `formal.language` or `evidence.tool` references do not resolve in the corresponding registry.
2. MUST, when `blueprint.hash` is present, compare it against the actual blueprint bytes, and treat the assurance document as not applicable on mismatch.
3. MUST, when `scriptHash` is present on an evidence record, compare it against the resolved validator's `hash` in the blueprint, and flag the evidence as **stale** on mismatch.
4. MUST verify an artifact's content digest before relying on the artifact's content.
5. MUST treat unresolvable or ambiguous validator references as errors.
MDEOF
echo "APPENDED"
````

Expected: `APPENDED`

- [ ] **Step 2: Commit**

```bash
git add CIP-XXXX/README.md
git commit -m "CIP-XXXX: specification of the assurance document format

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 6: README part 3 — Examples (embedding the example files)

**Files:**
- Modify (append): `CIP-XXXX/README.md`
- Read: `CIP-XXXX/examples/assurance-formal-proof.json`, `CIP-XXXX/examples/assurance-property-test.json`

- [ ] **Step 1: Append the Examples section, embedding both example files verbatim**

The embedded JSON MUST be byte-identical to the files (they are checked in Step 2). Build the section programmatically to guarantee this:

```bash
{
  printf '\n## Examples\n\nThe following complete examples are also available as machine-readable files under [examples](./examples).\n\n<details>\n  <summary>Formal verification with Blaster (formal-proof evidence, UAL formal statements, assumptions)</summary>\n\n```json\n'
  cat CIP-XXXX/examples/assurance-formal-proof.json
  printf '```\n</details>\n\n<details>\n  <summary>Property testing with Aiken (minimal document: no languages registry, natural-language statement only)</summary>\n\n```json\n'
  cat CIP-XXXX/examples/assurance-property-test.json
  printf '```\n</details>\n'
} >> CIP-XXXX/README.md
echo "APPENDED"
```

Expected: `APPENDED`

- [ ] **Step 2: Verify the embedded copies match the files exactly**

Run:

```bash
python3 - <<'PYEOF'
readme = open("CIP-XXXX/README.md").read()
ok = True
for f in ["CIP-XXXX/examples/assurance-formal-proof.json",
          "CIP-XXXX/examples/assurance-property-test.json"]:
    content = open(f).read().strip()
    status = "EMBEDDED" if content in readme else "MISSING-OR-DIFFERS"
    ok = ok and status == "EMBEDDED"
    print(f, status)
print("RESULT:", "OK" if ok else "FAIL")
PYEOF
```

Expected: both files `EMBEDDED`, `RESULT: OK`.

- [ ] **Step 3: Commit**

```bash
git add CIP-XXXX/README.md
git commit -m "CIP-XXXX: embed assurance document examples

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 7: README part 4 — Rationale

**Files:**
- Modify (append): `CIP-XXXX/README.md`

- [ ] **Step 1: Append the Rationale section**

Run:

```bash
cat >> CIP-XXXX/README.md <<'MDEOF'

## Rationale: how does this CIP achieve its goals?

### Why a detached document rather than a blueprint extension

An earlier draft of this proposal extended CIP-0057 blueprints in place, through an additional `$vocabulary` entry and new keywords inside `plutus.json`. The detached design was chosen instead, for three reasons:

1. **Third-party publishing.** The parties best placed to make assurance claims — auditors, independent verification teams — usually do not control the contract's repository. A detached document lets them publish claims about deployed code without any cooperation from the developers, and lets several independent assurance documents about the same blueprint coexist.
2. **Blueprints are compiler output.** `plutus.json` is typically regenerated on every build by the smart-contract framework (Aiken, OpShin, plu-ts, ...). Hand-maintained assurance data embedded in a generated file would be overwritten on each compilation, or would require every framework to learn how to preserve and merge it.
3. **No dialect machinery needed.** An assurance document is not a JSON Schema dialect extension; it is its own document type. Identifying the format by a versioned `$schema` URI is simpler than the `$vocabulary` opt-in mechanism, and CIP-0057 remains entirely untouched.

Developers who want the "blueprint carries its claims" experience simply ship an `assurance.json` next to their `plutus.json`.

### Why the specification language is free

There is today no consensus — on Cardano or elsewhere — on a single property language for smart contracts, and mandating one would gate adoption of this CIP on the outcome of that debate. Instead, the format standardizes the *envelope*: what is claimed (in mandatory natural language), by whom, about which exact code, with what outcome, and where the evidence lives. Formal statements are optional and declare their language through the `languages` registry, so a Blaster user can reference Universal Annotation Language statements while an Aiken user references executable property tests, without either being privileged by the format. If the ecosystem later converges on a standard property language, it slots into the registry like any other.

The mandatory natural-language `text` guarantees that every claim remains legible to every reader — including the users whose funds are at stake — regardless of which formal languages and tools they know.

### Why no signatures in v1

Evidence records name their verifier, but nothing in this version authenticates that name cryptographically. This is deliberate: the trust model of this CIP rests on *reproducibility* — anyone can fetch the artifact, check its digest, re-run the verification and compare verdicts — not on the authority of the verifier. Signing evidence records (e.g. with CIP-0008 message signing or COSE) would add real value against lazy consumers who do not re-run verifications, but it drags key management and identity questions into the format. It can be layered on in a future version, or by wrapping assurance documents in an external attestation, without changing the format defined here.

### Open methods, closed outcomes

New verification methods keep appearing (symbolic execution, model checking, fuzzing variants, ...), so `method` is an open enumeration: unknown values are legal and treated as opaque by consumers. Outcomes, by contrast, are what consumers compare and display at a glance, so `outcome` is a small closed enumeration with fixed semantics. The strength of an outcome is conveyed by its method — which is why consumers are told to always present the two together.

### Relation to CIP-0052

[CIP-0052](../CIP-0052) defines best practices for conducting audits of Cardano smart contracts. This CIP is complementary: it gives an audit performed along CIP-0052 lines a standard, machine-readable, code-bound publication format — an evidence record with `method: audit` whose artifact is the audit report itself, hash-pinned and tied to the audited script hashes.

### Backward compatibility

This CIP requires no change to CIP-0057. The RECOMMENDED validator `id` field is already legal under the CIP-0057 meta-schema (validator objects do not forbid additional fields), and blueprints without `id` fields remain fully usable through `title`-based references. Tools unaware of this CIP are unaffected: assurance documents are separate files they never read.
MDEOF
echo "APPENDED"
```

Expected: `APPENDED`

- [ ] **Step 2: Commit**

```bash
git add CIP-XXXX/README.md
git commit -m "CIP-XXXX: rationale for detached assurance documents

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 8: README part 5 — Path to Active, Copyright

**Files:**
- Modify (append): `CIP-XXXX/README.md`

- [ ] **Step 1: Append Path to Active and Copyright**

Run:

```bash
cat >> CIP-XXXX/README.md <<'MDEOF'

## Path to Active

### Acceptance Criteria

- [ ] The meta-schema is published and has remained stable through community review.
- [ ] At least one producer toolchain emits assurance documents (Blaster, planned).
- [ ] At least one consumer tool validates assurance documents, including binding checks (blueprint hash, validator resolution, script hash comparison) and artifact digest verification.
- [ ] At least one assurance document is published for a real-world, deployed contract.

### Implementation Plan

- [ ] Blaster to emit an `assurance.json` (UAL formal statements, `formal-proof` evidence records, proof artifacts) for the validators it verifies.
- [ ] Develop a standalone checker that performs the consumer obligations of this specification: meta-schema validation, binding checks, and artifact digest verification.
- [ ] Engage explorer, registry and wallet developers on surfacing assurance claims to end users.

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
MDEOF
echo "APPENDED"
```

Expected: `APPENDED`

- [ ] **Step 2: Commit**

```bash
git add CIP-XXXX/README.md
git commit -m "CIP-XXXX: path to active and copyright

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 9: Final verification pass

**Files:**
- Read: `CIP-XXXX/README.md`, `CIP-XXXX/schemas/assurance.json`, `CIP-XXXX/examples/*.json`

- [ ] **Step 1: Re-run the full validation suite (schema well-formed, examples valid, negative invalid, embeds in sync)**

Run:

```bash
python3 -m json.tool CIP-XXXX/schemas/assurance.json > /dev/null && echo "SCHEMA WELL-FORMED"
for f in CIP-XXXX/examples/assurance-formal-proof.json CIP-XXXX/examples/assurance-property-test.json; do
python3 - "$f" <<'PYEOF'
import json, sys
from jsonschema import Draft202012Validator
schema = json.load(open("CIP-XXXX/schemas/assurance.json"))
Draft202012Validator.check_schema(schema)
v = Draft202012Validator(schema)
doc = json.load(open(sys.argv[1]))
errs = list(v.iter_errors(doc))
print(sys.argv[1], "RESULT:", "VALID" if not errs else "INVALID (%d errors)" % len(errs))
PYEOF
done
python3 - <<'PYEOF'
readme = open("CIP-XXXX/README.md").read()
for f in ["CIP-XXXX/examples/assurance-formal-proof.json",
          "CIP-XXXX/examples/assurance-property-test.json"]:
    print(f, "EMBEDDED" if open(f).read().strip() in readme else "MISSING-OR-DIFFERS")
PYEOF
```

Expected: `SCHEMA WELL-FORMED`, both examples `RESULT: VALID`, both examples `EMBEDDED`.

- [ ] **Step 2: Check the README structure against CIP-1 conventions**

Run:

```bash
grep -n "^## " CIP-XXXX/README.md
grep -n "TODO\|TBD\|XXX_PLACEHOLDER\|<!--" CIP-XXXX/README.md || echo "NO LEFTOVER MARKERS"
```

Expected: exactly these H2 headings in order — `## Abstract`, `## Motivation: why is this CIP necessary?`, `## Specification`, `## Examples`, `## Rationale: how does this CIP achieve its goals?`, `## Path to Active`, `## Copyright` — and `NO LEFTOVER MARKERS`. (Note: `CIP: XXXX` and the `cipXXXX` schema URI are intentional until a CIP number is assigned; the grep above does not match them.)

- [ ] **Step 3: Confirm the branch history separates droppable commits from PR content**

Run: `git log --oneline master..HEAD`

Expected: the docs/superpowers commits (design spec, this plan) clearly separate from the `CIP-XXXX:` commits, so they can be dropped before opening the upstream PR.

---

## Out of scope for this plan

- Opening the upstream PR (user does this; requires dropping docs/superpowers commits and filling the `Discussions` link).
- Requesting a CIP number (assigned by CIP editors at PR time; `XXXX` and `cipXXXX` remain placeholders until then).
- Any Blaster/UAL tooling work.
