---
CIP: 116
Title: Standard JSON encoding for Domain Types
Category: Tools
Status: Proposed
Authors:
    - Vladimir Kalnitsky <klntsky@gmail.com>
Implementors:
    - Vladimir Kalnitsky <klntsky@gmail.com>
Discussions:
    - https://github.com/cardano-foundation/CIPs/pull/742
    - https://github.com/cardano-foundation/CIPs/pull/766
Created: 2024-02-22
License: CC-BY-4.0
---

## Abstract

Canonical JSON encoding for Cardano domain types lets the ecosystem converge on a single way of serializing data to JSON, thus freeing the developers from repeating roughly the same, but slightly different encoding/decoding logic over and over.

## Motivation: why is this CIP necessary?

Cardano domain types have canonical CDDL definitions (for every era), but when it comes to use in web apps, where JSON is the universally accepted format, there is no definite standard. This CIP aims to change that.

The full motivation text is provided in [CPS-11 | Universal JSON Encoding for Domain Types](https://github.com/cardano-foundation/CIPs/tree/master/CPS-0011).

## Specification

This CIP is expected to contain multiple json-schema definitions for Cardano Eras and breaking intra-era hardforks starting from Babbage.

| Ledger era | Hardfork | Ledger Commit | Schema | Changelog Entry |
| --- | --- | --- | --- |--- |
| Babbage | Vasil | [12dc779](https://github.com/IntersectMBO/cardano-ledger/blob/12dc779d7975cbeb69c7c18c1565964a90f50920/eras/babbage/impl/cddl-files/babbage.cddl) | [cardano-babbage.json](./cardano-babbage.json) | N/A |

### Tests & utilities for JSON validation

[`cip-0116-tests`](https://github.com/mlabs-haskell/cip-0116-tests) repo contains utility functions and a test suite for the schema. In particular, there's a `mkValidatorForType` function that builds a validator function for any type defined in the schema.

### Scope of the Schema

The schemas should cover `Block` type and all of its structural components, which corresponds to the scope of CDDL files located in [the ledger repo](https://github.com/IntersectMBO/cardano-ledger/).

### Schema Design Principles

Below you can find some principles outlining the process of schema creation / modification. They are intended to be applied when there is a need to create a schema for a new Cardano era.

#### Uniqueness of encoding

Every transaction (i.e. CBOR-encoded binary) must have exactly one valid JSON encoding, up to entry ordering in mappings (that are represented as key-value pairs).

For a single JSON fixture, however, there are multiple variants of encoding it as CBOR.

#### Consistency with the previous versions

To simplify transitions of dApps between eras, the scope of changes introduced to the schemas SHOULD be limited to the scope of CDDL changes.

### Schema Conventions

These conventions help to keep the schema uniform in style.

#### Encoding of binary types

Binary data MUST be encoded as lower-case hexademical strings. Restricting the character set to lower-case letters (`a-f`) allows for comparisons and equality checks without the need to normalize the values to a uniform case.

#### Encoding of mapping types

`Map`-like container types MUST be encoded as arrays of key-value pairs.

```json
"Map": {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "key": ...,
            "value": ...
        },
        "required": [
          "key",
          "value"
        ],
        "additionalProperties": false
    }
}
```

Uniqueness of `"key"` objects in a map MUST be preserved (but this property is not expressible via a schema).

Implementations MUST consider mappings with conflicting keys invalid.

Some mapping-like types, specifically `Mint`, allow for duplicate keys. Types like these should not be encoded as maps, instead, `key` and `value` properties should be named differently.

#### Encoding of variant types

Encoding types with variable payloads MUST be done with the use of `oneOf` and an explicit discriminator property: `tag`:

```json
{
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
    }
}
```

Other properties of a tagged object MUST be specified in lower-case snake-case.

#### Encoding of enum types

Enums are a special kind of variant types that carry no payloads. These MUST be encoded as string `enum`s.

Lowercase snake case identifiers MUST be used for the options, e.g.:

```json
{
    "Language": {
      "title": "Language",
      "type": "string",
      "enum": [
        "plutus_v1",
        "plutus_v2"
      ]
    }
}
```

#### Encoding of record types

All record types MUST be encoded as objects with explicit list of `required` properties, and `additionalProperties` set to `false` (see "absence of extensibility" chapter for the motivation behind this suggestion).

#### Encoding of nominal type synonyms

Some of the types have identical representations, differing only by nominal name. For example, `Slot` domain type is expressed as `uint` in CDDL.

For these types, their nominal name SHOULD NOT have a separate definition in the json-schema, and the "representation type" should be used via a `$ref` instead. The domain type name SHOULD be included as `title` string at the point of usage.

### Additional format types

Some non-standard `format` types are used:

- `hex` - lower-case hex-encoded byte string
- `bech32` - [bech32](https://en.bitcoin.it/wiki/Bech32) string
- `base58` - [base58](https://bitcoinwiki.org/wiki/base58) string
- `uint64` - 64-bit unsigned integer
- `int128` - 128-bit signed integer
- `string64` - a unicode string that must not exceed 64 bytes when utf8-encoded.
- `posint64` - a positive (0 excluded) 64-bit integer. `1 .. 2^64-1`

### Limitations

JSON-schema does not allow to express certain properties of some of the types.

#### Uniqueness of mapping keys

See the chapter on encoding of mapping types.

#### Bech32 and Base58 formats

Validity of values of these types can't be expressed as a regular expression, so the implementations MAY validate them separately.

#### Address types

Bech32 strings are not always valid addresses: even if the prefixes are correct, the [binary layout of the payload](https://github.com/IntersectMBO/cardano-ledger/blob/f754084675a1decceed4f309814b09605f443dd5/libs/cardano-ledger-core/src/Cardano/Ledger/Address.hs#L603) must also be valid.

The implementations MAY validate it separately.

#### Byte length limits for strings

In CDDL, the length of a `tstr` value gives the number of bytes, but in `json-schema` there is no way to specify restrictions on byte lengths. So, `maxLength` is not the correct way of specifying the limits, but it is still useful, because no string longer than 64 *characters* satisfies the 64-byte limit.

#### Auxiliary Data encoding

`auxiliary_data` CDDL type is handled specially.

```cddl
auxiliary_data =
  metadata ; Shelley
  / [ transaction_metadata: metadata ; Shelley-ma
    , auxiliary_scripts: [ * native_script ]
    ]
  / #6.259({ ? 0 => metadata         ; Alonzo and beyond
      , ? 1 => [ * native_script ]
      , ? 2 => [ * plutus_v1_script ]
      , ? 3 => [ * plutus_v2_script ]
      })
```

Instead of providing all three variants of encoding, we base the schema on the one that is the most general (the last one):

```json
{
    "AuxiliaryData": {
      "properties": {
        "metadata": {
          "$ref": "cardano-babbage.json#/definitions/TransactionMetadata"
        },
        "native_scripts": {
          "type": "array",
          "items": {
            "$ref": "cardano-babbage.json#/definitions/NativeScript"
          }
        },
        "plutus_scripts": {
          "type": "array",
          "items": {
            "$ref": "cardano-babbage.json#/definitions/PlutusScript"
          }
        }
      },
    }
}
```

It is up to implementors to decide how to serialize the values into CBOR. The property we want to maintain is preserved regardless of the choice: for every block binary there is exactly one JSON encoding.

### Versioning

This CIP should not follow a conventional versioning scheme, rather it should be altered via pull request before a hardforks to add new a JSON schema to align with new ledger ers. Each schema must be standalone and not reuse definitions between eras. Authors MUST follow the [Schema Scope](#scope-of-the-schema), [Schema Design Principles](#schema-design-principles) and [Schema Conventions](#schema-conventions).

Furthermore, for each subsequent schema, the [changelog](./changelog.md) must be updated. Authors must clearly articulate the deltas between schemas.

## Rationale: how does this CIP achieve its goals?

### Scope

We keep the scope of this standard to the data types within Cardano blocks. The rationale for this is that block data is by far the most useful for the majority of Cardano actors. There is also one nice benefit that the definitions can map directly from the provided CDDL file from ledger team.

### Strictness

This CIP lays out strong conventions that future schema authors must follow, along with a large set of design principles. The aim is to minimize the potential for unavoidable deltas between schemas.

By setting sometimes arbitrary conventions we hope to create a single possible interpretation from CBOR to JSON, alleviating any ambiguity.

### Absence of extensibility

The schemas MUST NOT be extensible with additional properties. This may sound counter-intuitive and against the spirit of json-schema, but there are some motivations behind that:

- More safety from typos: object fields that are optional may be specified with slightly incorrect names in dApps' code, leading to inability of the decoders to pick up the values, which may go unnoticed.
- Clear delineation between Cardano domain types and user dApp domain types: forcing the developers to store their dApp domain data separately from Cardano data, or close to it (as opposed to mixing these together in a single object) will indirectly motivate better structured dApp code.

### JSON

JSON was chosen as there is no viable alternative. The majority of Cardano's web tooling is built with Javascript where JSON is the primary object representation format.

Furthermore, even across non-Javascript based stacks, JSON enjoys wide tooling support, this improves the potential for builders to adopt this standard.

### Bech32 for addresses

We choose to use Bech32 as the representation for Cardano addresses. When compared to the alternative of hexademical encoding, Bech32 gives the advantages of an included checksum and a human readable prefix.

## Path to Active

### Acceptance Criteria

- [ ] One future ledger era schema is added
- [ ] This standard is implemented within three separate tools, libraries, etc. 

### Implementation Plan

- [x] Complete the specification for the current Babbage era
- [ ] Provide a test suite validating JSON fixtures for all the types against the schema 
- [x] Provide an implementation of validating functions that uses this json-schema
  - [mlabs-haskell/cip-0116-tests](https://github.com/mlabs-haskell/cip-0116-tests)
- [ ] Collect a list of cardano domain types implementations and negotiate transition to the specified formats with maintainers (if it makes sense and is possible)

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
