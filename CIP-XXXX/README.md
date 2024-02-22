---
CIP: ?
Title: Standard JSON encoding for Domain Types
Category: Tools
Status: Proposed
Authors:
    - Vladimir Kalnitsky <klntsky@gmail.com>
Implementors: []
Discussions:
    - https://github.com/cardano-foundation/cips/pulls/766
Created: 2024-02-22
License: CC-BY-4.0
---

## Abstract

Canonical JSON encoding for Cardano domain types lets the ecosystem converge on a single way of serializing data to JSON, thus freeing the developers from repeating roughly the same, but slightly different encoding/decoding logic over and over.

## Motivation: why is this CIP necessary?

Cardano domain types have canonical CDDL definitions (for every era), but when it comes to use in web apps, where JSON is the universally accepted format, there is no definite standard. This CIP aims to change that.

The full motivation text is provided in [CPS-11 | Universal JSON Encoding for Domain Types](https://github.com/cardano-foundation/CIPs/pull/742).

## Specification

This CIP is expected to contain multiple schema definitions for Cardano Eras starting from Babbage.

- [Babbage](./cardano-babbage.json)

### Schema Design Principles

Below you can find some principles outlining the process of schema creation / modification. They are intended to be applied when there is a need to create a schema for a new Cardano era.

#### Consistency with the previous versions

To simplify transitions of dApps between eras, the scope of changes introduced to the schemas SHOULD be limited to the scope of CDDL changes.

#### Scope of the Schema

The schemas should cover `Block` type and all of its structural components, which corresponds to the scope of CDDL files located in [the ledger repo](https://github.com/IntersectMBO/cardano-ledger/).

#### Absence of extensibility

The schemas MUST NOT be extensible with additional properties. This may sound counter-intuitive and against the spirit of json-schema, but there are some motivations behind that:

- More safety from typos: object fields that are optional may be specified with slightly incorrect names in dApps' code, leading to inability of the decoders to pick up the values, which may go unnoticed.
- Clear delineation between Cardano domain types and user dApp domain types: forcing the developers to store their dApp domain data separately from Cardano data, or close to it (as opposed to mixing these together in a single object) will indirectly motivate better structured dApp code.

### Schema Conventions

These conventions help to keep the schema uniform in style.

#### Encoding of mapping types

`Map`-like container types should be encoded as arrays of key-value pairs. Uniqueness of `"key"` objects in a map MUST be preserved (but this property is not expressible via a schema).

```json
"Map": {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "key": ...,
            "value": ...
        },
        "additionalProperties": false
    }
}
```

Implementations MUST consider mappings with conflicting keys invalid.

#### Encoding of variant types

Encoding types with variable payloads MUST be done with the use of `oneOf` and an explicit discriminator property: `tag`:

```json
    "Credential": {
      "type": "object",
      "discriminator": {
        "propertyName": "tag"
      },
      "oneOf": [
        {
          "type": "object",
          "properties": {
            "tag": {
              "enum": [
                "pubkey_hash"
              ]
            },
            "value": {
              "$ref": "cardano-babbage.json#/definitions/Ed25519KeyHash"
            }
          },
          "required": ["tag", "value"],
          "additionalProperties": false
        },
        {
          "type": "object",
          "properties": {
            "tag": {
              "enum": [
                "script_hash"
              ]
            },
            "value": {
              "$ref": "cardano-babbage.json#/definitions/ScriptHash"
            }
          },
          "required": ["tag", "value"],
          "additionalProperties": false
        }
      ]
    },
```

Other properties of a tagged object MUST be specified in lower-case snake-case.

#### Encoding of enum types

Enums are a special kind of variant types that carry no payloads. These must be encoded as string `enum`s.

Lowercase snake case identifiers should be used for the options, e.g.:

```json
    "Language": {
      "title": "Language",
      "type": "string",
      "enum": [
        "plutus_v1",
        "plutus_v2"
      ]
    },
```

#### Encoding of record types

All record types MUST be encoded as objects with explicit list of `required` properties, and `additionalProperties` set to `false` (see "absence of extensibility" chapter for the motivation behind this suggestion).

#### Encoding of nominal type synonyms

Some of the types have identical representations, differing only by nominal name. For example, Slot domain type is expressed as `uint` in CDDL.

For these types, their nominal name should not have a separate definition in the json-schema, and the "representation type" should be used via a `$ref` instead. The domain type name SHOULD be included as `title` string at the point of usage.

### Additional format types

Some non-standard `format` types are used:

- `hex`
- `bech32`
- `base58`

TODO: describe the formats

### Limitations

#### Byte length limits for strings

In CDDL, the length of a `tstr` value gives the number of bytes, but in `json-schema` there is no way to specify restrictions on byte lengths. So, `maxLength` is not the correct way of specifying the limits, but it is still useful, because no string longer than 64 *characters* satisfies the 64-byte limit.

## Rationale: how does this CIP achieve its goals?

## Path to Active

- [ ] Complete the specification
- [ ] Provide an implementation of validating functions that uses this json-schema
- [ ] Collect a list of cardano domain types implementations and negotiate transition to the specified formats with maintainers (if it makes sense and is possible)

### Acceptance Criteria

### Implementation Plan
<!-- A plan to meet those criteria. Or `N/A` if not applicable. -->

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).

[CC-BY-4.0]: https://creativecommons.org/licenses/by/4.0/legalcode
