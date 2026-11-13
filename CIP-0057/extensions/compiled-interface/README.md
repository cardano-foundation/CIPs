# Compiled program interfaces — proposed CIP-57 extension

**Draft for discussion with the CIP editors.** This document proposes interface
semantics separately from [blueprint assurance](../../../CIP-XXXX). Whether these
changes become an amendment to CIP-57 or a separately numbered extension is open.
The versioned identifiers below are proposed identifiers, not published standards.
No CIP number has been assigned to this extension.

## Purpose and boundary

A consumer needs to know how to apply the exact compiled program, including any
unapplied parameters, before it can generate transactions or check properties.
CIP-57 already distinguishes Data representations (`integer`, `bytes`, etc.) from
native UPLC values (`#integer`, `#bytes`, etc.). This proposal preserves that
distinction, adds an explicitly specified Scott representation, and describes
complete argument lists and ledger calling conventions.

The blueprint describes the program interface. Claims, checking bounds, selected
protocol/cost model, solver settings, and verification results belong in the
[assurance proposal and its checking contexts](../../../CIP-XXXX#checking-contexts).
A tool MUST NOT infer these facts merely because an unknown field passes an open
JSON meta-schema.

## Dialect and compatibility

The proposed `$schema` is:

```
https://cips.cardano.org/cips/cip57/extensions/compiled-interface/v1/schema.json
```

Its [meta-schema](./schemas/blueprint.json) declares the required vocabulary:

```
https://cips.cardano.org/cips/cip57/extensions/compiled-interface/v1/vocabulary
```

A document using this dialect declares that vocabulary as `true` in `$vocabulary`.
A consumer that does not implement it MUST decline executable interpretation;
it MAY display the document. In particular it MUST NOT reinterpret a Scott
parameter as Data, or ignore an unfamiliar calling convention.

The existing CIP-57 schema URI and the meaning of existing `dataType` values are
unchanged. Ordinary CIP-57 documents remain usable for existing interfaces and
for assurance that does not need this extension. The new dialect requires an
`id` and `interface` on each validator. Code remains optional for interface-only
publication; an executable check requires `compiledCode` and its matching `hash`.
The extension requires `hash` whenever `compiledCode` is present.

The experimental top-level validator fields `arguments` and `budget` are not
part of this dialect. `interface` replaces the former; checking contexts hold
the latter. The legacy UAL 0.5 fixture is preserved separately for reproducibility.

## Stable identity

Each validator has an `id` matching `^[A-Za-z0-9_-]+$`, unique in the blueprint.
It is stable across display-title changes. Assurance scopes refer to it.
An id is not a code digest: consumers still bind the exact blueprint bytes and
recompute script hashes with the Plutus language tag.

## Parameter schemas and representations

`parameters[i].schema` is the single description of that parameter's wire
representation. The ordered invocation references this entry; it does not repeat
its schema or independently override its encoding.

| Schema | Value passed to the UPLC program |
| --- | --- |
| `{"dataType":"integer"}` | `Const (Data (I n))` |
| `{"dataType":"#integer"}` | `Const (Integer n)` |
| `{"dataType":"bytes"}` | A Data bytes value |
| `{"dataType":"#bytes"}` | A native ByteString constant |
| `{}` | Raw Data; no additional well-formedness restriction is implied |
| `{"dataType":"#scott", ...}` | A Scott term under its declared encoding profile |

The remaining existing Data and native constructors retain CIP-57's meaning,
including `#unit`, `#boolean`, `#string`, `#list`, and `#pair`. Data containers
contain Data; builtin lists/pairs in CIP-57 contain Data elements. An exporter
MUST NOT label a native value as `integer` and rely on an independent `asNative`
flag to reverse that meaning. Internal type representations in consumers must
preserve the wire distinction even when two representations share a host type.

Local `#/definitions/...` references use JSON Pointer escaping. Consumers resolve
references and preserve representation through every nested field. Reference
cycles are not by themselves errors: finite recursive values may have recursive
type definitions. A consumer without a required recursive encoder MUST reject
that invocation. A runtime datum, redeemer or context is always passed as Data
under the ledger profiles below; a Scott or native schema is not legal there.

The [value meta-schema](./schemas/value-schema.json) checks structural syntax.
Consumers additionally enforce CIP-57's datatype-specific constraints, resolve
references, check container element representations and reject unsupported or
ambiguous encodings. The meta-schema alone cannot implement these semantics.

## Scott profile: `scott-cbv-v1`

A Scott schema has `dataType: "#scott"`, a versioned `encoding` identifier and a
nonempty `constructors` array. Each constructor has a unique nonempty `name` and
an ordered `fields` array of value schemas. Array position determines constructor
selection. Names are descriptive; reordering constructors changes the encoding.
Fields can use existing Data/native schemas or another Scott schema. No type
parameters, function-typed fields or implicit compiler defaults are specified by
this initial profile.

The proposed encoding identifier is:

```
https://cips.cardano.org/cips/cip57/extensions/compiled-interface/v1/encodings/scott-cbv-v1
```

For a value of constructor `i` in a type with `k` constructors and field values
`x0 ... xn`, the encoding is the closed UPLC value:

```
λ b0 ... b(k-1). (force bi) E(x0) ... E(xn)
```

Application associates to the left. `E` recursively follows each field's own
schema. For a nullary constructor the body is just `force bi`. A case consumer
supplies each branch as `delay handler`; the selected handler takes its fields
in declared order. Thus all branch handlers are delayed, only the selected
handler is forced, and unselected branches are not evaluated. Bound variables
must be fresh; alpha-renaming does not change the encoding. Encoding finite
recursive values recurses structurally over those values.

For example, `None | Some #integer` encodes `None` as
`λ b0 b1. force b0`, and `Some 7` as `λ b0 b1. (force b1) (Const Integer 7)`.
See [encoding vectors](./examples/encoding-vectors.json), including the distinct
Data/native integer cases, and the [parameter example](./examples/parameter-encodings.json).
The vectors use explicit named-term notation, not serialized Flat script bytes.

This is a proposed concrete profile, not an assertion that existing Plinth,
Aiken, Scalus or other compilers use these exact Scott conventions. A producer
must establish the match. Other conventions require a different versioned
profile and conformance vectors; consumers MUST reject unknown profiles.

## Complete invocation interface

`interface` has these fields:

| Field | Meaning |
| --- | --- |
| `callingConvention` | `ledger-v1`, `ledger-v2` or `ledger-v3`; must agree with `preamble.plutusVersion` |
| `invocations` | A nonempty array of supported purposes, each with a complete ordered argument list |

An invocation has `purpose` and `arguments`. The purpose is one of `spend`,
`mint`, `withdraw`, `publish`, `vote`, or `propose`. The latter two are available
only in `ledger-v3`. Purposes must be unique within an interface.

| Argument role | Required reference | Meaning |
| --- | --- | --- |
| `parameter` | `source: "/parameters/i"` | The parameter entry at zero-based index `i` in this validator |
| `datum` | `source: "/datum"` | The validator's existing datum description |
| `redeemer` | `source: "/redeemer"` | The validator's existing redeemer description |
| `context` | No `source` | The raw Data script context defined by the selected ledger calling convention |

All currently unapplied parameters come first, exactly once, in parameter-array
order. Then the complete runtime suffix is:

| Calling convention | Purpose | Runtime roles, in order | Successful result requirement |
| --- | --- | --- | --- |
| `ledger-v1` / `ledger-v2` | `spend` | `datum`, `redeemer`, `context` | Normal evaluation termination |
| `ledger-v1` / `ledger-v2` | Other supported purposes | `redeemer`, `context` | Normal evaluation termination |
| `ledger-v3` | Every supported purpose | `context` | Native UPLC unit |

The last row follows the unified context interface in [CIP-69](../../../CIP-0069).
The ledger implementation's language-specific result rules remain authoritative;
this table does not impose the V3 unit requirement on older languages. Successful
phase-two evaluation does not establish the other transaction-validation rules.

For V3, the existing redeemer/datum descriptions describe the corresponding
payloads inside the context; they are not extra positional arguments. Missing
optional spending datums remain possible. The calling convention defines their
placement, so no independent context-path mapping is introduced here.

If a datum/redeemer description is selected by a `oneOf` purpose discriminator,
the invocation's purpose must select exactly one alternative. Parameter entries
are positional and never change order with purpose. A producer must export a
separate validator/template if parameter lists genuinely differ by purpose.
References must resolve, and any declared purpose restrictions must agree with
the invocation. A schema's well-formedness restriction is not an automatic premise
for all verification: claims about malformed Data must still be expressible.

A consumer applies exactly the listed arguments to the referenced compiled
program and uses the declared ledger result rule. It must not infer a convention
from the validator's title, invent omitted parameters, or equate a successful
partial application with complete invocation according to this declaration.
The producer is responsible for agreement with the compiled program; the
interface declaration alone is not a proof of that agreement.

## Application and deployment

`compiledCode` and `hash` describe the program as supplied in this blueprint.
`parameters` lists only parameters still to be applied. After specialization,
a newly generated blueprint must update the code, hash, remaining parameters
and invocation references together. A descriptive id alone cannot connect the
template to its specialization.

A universal parameter claim quantifies over all parameter values in its stated
domain. A concrete deployment claim records the exact encoded parameter terms,
application order, template identity and recomputed applied script hash in the
assurance checking context. Importing a template hash alone establishes no
binding to a deployed address. The checker must establish any schema/domain
premises for those concrete values before using a universal result.

## Editor review and acceptance

The proposed placement, schema/vocabulary identifiers, and Scott-profile details
need editor and compiler-maintainer review. They are intentionally not added to
the active CIP-57 meta-schema under its existing URI.

Before adoption:

- Agree whether to amend CIP-57 or publish a companion extension.
- Validate the complete interface with at least two producer/consumer implementations.
- Test Data/native distinction, Scott branch forcing and constructor order,
  recursive schemas, parameter application and V1/V2/V3 invocation/result rules.
- Check existing blueprints continue to use their existing dialect unchanged.
- Implement the coordinated assurance checking-context profile and demonstrate
  checks over actual compiled bytes, including rejection and exhaustion cases.

The Python checks in `CIP-XXXX/tests/test_interface_drafts.py` validate the draft
schemas, examples and selected cross-document rules. They are not a Scott encoder,
a UPLC interpreter, a deployment applier, or a proof checker.


Separately compiled library functions are carried by the companion assurance
CIP's `functions` registry, with their input/result wire schemas and properties.
This extension keeps blueprint entries limited to ledger scripts. The value
schema vocabulary can be reused by assurance without adding helper programs
to `validators` or introducing a blueprint `functions` field.

The initial UAL checker now supports guarded recursive Data schemas by retaining
raw Data at the parameter boundary. Recursive Lean datatype generation is not
required for this path. A cycle must cross a constructor field or container
element; a pure alias cycle is invalid. Native values cannot be hidden inside
a recursive Data container. Execution remains bounded by the checking context.
