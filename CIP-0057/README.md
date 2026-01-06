---
CIP: 57
Title: Plutus Contract Blueprint
Status: Active
Category: Tools
Authors:
  - KtorZ <matthias.benkort@cardanofoundation.org>
  - scarmuega <santiago@carmuega.me>
Implementors:
  - Aiken <https://aiken-lang.org>
  - Plu-Ts <https://github.com/HarmonicPool/plu-ts>
  - OpShin <https://github.com/OpShin>
  - Lucid <https://lucid.spacebudz.io/>
  - Mesh.js <https://martify.io/>
Discussions:
  - https://github.com/cardano-foundation/CIPs/pull/258
  - https://discord.gg/yUkkhqBnyV
  - https://github.com/aiken-lang/aiken/issues/972
Created: 2022-05-15
License: CC-BY-4.0
---

## Abstract

This document specifies a language for documenting Plutus contracts in a machine-readable manner. This is akin to what [OpenAPI](https://swagger.io/specification) or [AsyncAPI](https://www.asyncapi.com/docs/specifications/v2.4.0) are for, documenting HTTP services and asynchronous services respectively. In a similar fashion, A Plutus contract has a binary interface which is mostly defined by its datum and redeemer.

This document is therefore a meta-specification defining the vocabulary and validation rules with which one can specify a Plutus contract interface, a.k.a **Plutus contract blueprint**.

## Motivation: Why is this CIP necessary?

While publicly accessible, on-chain contracts are currently inscrutable. Ideally, one would want to get an understanding of transactions revolving around script executions. This is both useful to visualize and to control the evolution of a contract life-cycle; but also, as a user interacting with a contract, to ensure that one is authorizing a transaction to do what it's intended to. Having a machine-readable specification in the form of a JSON-schema makes it easier (or even, possible) to enable a wide variety of use cases from a single concise document, such as:

- Code generators for serialization/deserialization of Contract's elements
- Contract API Reference / Documentation, also automatically generated
- Extra automated transaction validation layers
- Better wallet UI / integration with DApps
- Automated Plutus-code scaffolding

Moreover, by making the effort to write a clear specification of their contracts, DApps developers make their contracts easier to audit (as they're able to specify the expected behavior).

## Specification

### Overview

This specification introduces the notion of a _Plutus contract blueprint_, as a JSON document which it itself a _JSON-schema_ as per the definition of given in [JSON Schema: A Media Type for Describing JSON Documents: Draft 2020-12](https://json-schema.org/draft/2020-12/json-schema-core.html).

Said differently, Plutus blueprints are first and foremost, valid JSON schemas (according to the specification linked above). This specification defines a core vocabulary and additional keywords which are tailored to the specification of Plutus contracts. Tools supporting this specification must implement the semantic and validation rules specified in this document.

Meta-schemas for Plutus blueprints (i.e. schemas used for validating Plutus blueprints themselves) are given [in annexe](./schemas/README.md).

A _Plutus contract blueprint_ is made of a single document describing one or more on-chain validators. By convention, the document is named `plutus.json` and should be located at the root of a project's repository to facilitate its discoverability.

### Document Structure

The document itself is a JSON object with the following fields:

| Fields                       | Description                                               |
| ---                          | ---                                                       |
| [preamble](#preamble)        | An object with meta-information about the contract        |
| [validators](#validators)    | An object of named validators                             |
| ?[definitions](#definitions) | A registry of definition re-used across the specification |

Note that examples of specifications are given later in the document to keep the specification succinct enough and not bloated with examples.

#### preamble

The `preamble` fields stores meta-information about the contract such as version numbers or a short description. This field is mainly meant for humans as a mean to contextualize a specification.

| Fields         | Description                                                                  |
| ---            | ---                                                                          |
| title          | A short and descriptive title of the application                             |
| ?description   | A more elaborate description                                                 |
| ?version       | A version number for the project.                                            |
| ?compiler      | Information about the compiler or framework used to produce the validator(s) |
| ?plutusVersion | The Plutus version assumed for all validators                                |
| ?license       | A license under which the specification and contract code is distributed     |

#### compiler

The `compiler` field is optional, but allows specifying metadata about the toolkit that produced the validator and blueprint.

| Fields   | Description                                                      |
| ---      | ---                                                              |
| name     | The name of the compiler/framework/tool that generated the file. |
| ?version | An optional version number in any format.                        |

#### validators

Validators are the essence of the blueprint. This section describes each validator involved in the contract (simple applications will likely have only a single validator). A validator is mainly defined by three things: a title, arguments (i.e parameters, redeemer and/or datum) and some compiled code. Parameters refer to compile-time arguments that can be applied to a validator template. They must be instantiated to produce a final compiled code as they are embedded in the code of the validator itself. This is often the case for validators that must hold on unique external nonce to produce unique hashes.

| Fields        | Description                                                                                                                     |
| ---           | ---                                                                                                                             |
| title         | A short and descriptive name for the validator                                                                                  |
| ?description  | An informative description of the validator                                                                                     |
| redeemer      | A description of the redeemer format expected by this validator                                                                 |
| ?datum        | A description of the datum format expected by this validator                                                                    |
| ?parameters   | A list of parameters required by the script in addition of the datum and redeemer                                               |
| ?compiledCode | The full compiled and cbor-encoded serialized flat script                                                                       |
| ?hash         | A blake2b-224 hash digest of the validator script, as found in addresses. Optional, but mandatory if `compiledCode` is provided |

##### redeemer, datum and parameters

`redeemer`, `datum` and `parameters` items all share the same schema structure. They must define a `schema` that describes how to construct valid on-chain values for each of these fields, and they also specify a purpose (`spend`, `mint`, `withdraw` or `publish`) that indicates in which context it can figure. The purpose is either a string, or an applicator `oneOf` that specifies multiple (distinct) purposes. Similarly, an argument is either an object as described below, or an applicator `oneOf` of such objects. In case where it is defined as an applicator, `purpose` values between objects must be strictly non-overlapping as they are used as discriminant in chosing a schema. This allows, for example, to define different redeemer schemas for different purposes.

| Fields       | Description                                                                                                      |
| ---          | ---                                                                                                              |
| ?title       | A short and descriptive name for the redeemer, datum or parameter                                                |
| ?description | An informative description of the redeemer, datum or parameter                                                   |
| ?purpose     | One of `"spend"`, `"mint"`, `"withdraw"` or `"publish"`, or a `oneOf` applicator of those                        |
| schema       | A _Plutus Data Schema_ using the core vocabulary defined below, or a `oneOf` applicator of _Plutus Data Schemas_ |

#### definitions

A set of extra schemas to be re-used as references across the specification.

### Core vocabulary

Plutus blueprints ultimately describes on-chain data value that can be found at the validator's interface boundaries. This means that while we would generally operate at the level of _Plutus Data_, the vocabulary covers in practice any of the possible Untyped Plutus Core (abbrev. UPLC) primitives that can appear at a validator's boundary (e.g. compile-time parameters). Any UPLC primitive is therefore represented as a schema with a `dataType` keyword. The possible values for `dataType` are detailed just below. In addition, and depending on the value of `dataType`, we may find additional keywords in the vocabulary.

| dataType      | UPLC Type  | Description                                                               |
| ---           | ---        | ---                                                                       |
| `integer`     | Data       | A signed integer at an arbitrary precision, wrapped as `iData`.           |
| `bytes`       | Data       | A bytes string of an arbitrary length, wrapped as `bData`.                |
| `list`        | Data       | An ordered list of Plutus data, wrapped as `listData`                     |
| `map`         | Data       | An associative list of Plutus data keys and values, wrapped as `mapData`. |
| `constructor` | Data       | A constructor with zero, one or many fields, wrapped as `constrData`.     |
| `#unit`       | Unit       | A builtin unit value (the unary constructor).                             |
| `#boolean`    | Boolean    | A builtin boolean value.                                                  |
| `#integer`    | Integer    | A builtin signed integer at an arbitrary precision.                       |
| `#bytes`      | ByteString | A builtin bytes string of an arbitrary length.                            |
| `#string`     | String     | A builtin UTF-8 text string.                                              |
| `#pair`       | ProtoPair  | A builtin pair of `Data` elements.                                        |
| `#list`       | ProtoList  | A builtin list of `Data` elements.                                        |

> **Warning**
>
> While they exist for completeness, frameworks are strongly discouraged to use any of the constructs starting with a `#` as they refer to Plutus Core builtins types used by the Plutus virtual machines but aren't meant to figure in outward-facing interfaces. Validators should, as much as possible, stick to `integer`, `bytes`, `list`, `map` and `constructor` (and any composition of those) for their binary interface.

Using these primitives, it becomes possible to represent the entire domain (i.e. possible values) which can be manipulated by Plutus contracts.

### Additional keywords

Similarly to JSON schemas, we provide extra validation keywords and keywords for applying subschemas with logic to further refine the definition of core primitives. Keywords allow to combine core data-types into bigger types and we'll later give some pre-defined definitions which we assume to be part of the core vocabulary and therefore, recognized by any tool supporting this standard.

When presented with a validation keyword with a malformed value (e.g. `"maxLength": "foo"`), programs are expected to return an appropriate error.

Beside, we define a _Plutus Data Schema_ as a JSON object with a set of fields depending on its corresponding data-type. When we refer to a _Plutus Data Schema_, we refer to the entire schema definition, with its validations and with the semantic of each keywords applied.

Unless otherwise specified, keywords are all considered optional.

Here below are detailed all the accepted keywords for each data-type.

#### For any data-type

> **Note** Keywords in this section applies to any instance data-type described above.

##### `dataType`

The value of this keyword must be a string, with one of the following value listed in the first column of the table above. This keyword is **optional**. When missing, the instance is implicitly typed as an opaque Plutus Data. When set, it defines the realm of other applicable keywords for that instance.

##### `title`

This keyword's value must be a string. This keyword can be used to decorate a user interface and qualify an instance with some short title.

##### `description`

This keyword's value must be a string. This keyword can be used to decorate a user interface and provide explanation about the purpose of the instance described by this schema.

##### `$comment`

This keyword's value must be a string. It is meant mainly for programmers and humans reading the specification. This keyword should be ignored by programs.

##### `allOf`

This keyword's value must be a non-empty array.  Each item of the array MUST be a valid _Plutus Data Schema_. An instance validates successfully against this keyword if it validates successfully against all schemas defined by this keyword's value.

##### `anyOf`

This keyword's value must be a non-empty array. Each item of the array must be a valid _Plutus Data Schema_. An instance validates successfully against this keyword if it validates successfully against at least one schema defined by this keyword's value.

##### `oneOf`

This keyword's value must be a non-empty array. Each item of the array must be a valid _Plutus Data Schema_. An instance validates successfully against this keyword if it validates successfully against exactly one schema defined by this keyword's value.

##### `not`

This keyword's value must be a valid _Plutus Data Schema_. An instance is valid against this keyword if it fails to validate successfully against the schema defined by this keyword.

#### For `{ "dataType": "bytes" }`

> **Note** Keywords in this section only applies to `bytes`. Using them in conjunction with an invalid data-type should result in an error.

##### `enum`

The value of this keyword must be an array of hex-encoded string literals. An instance validates successfully against this keyword if once hex-encoded, its value matches one of the elements of the keyword's values.

##### `maxLength`

The value of this keyword must be a non-negative integer. A bytes instance is valid against this keyword if its length is less than, or equal to, the value of this keyword.

##### `minLength`

The value of this keyword must be a non-negative integer. A bytes instance is valid against this keyword if its length is greater than, or equal to, the value of this keyword.

#### For `{ "dataType": "integer" }`

> **Note** Keywords in this section only applies to `integer`. Using them in conjunction with an invalid type should result in an error.

##### `multipleOf`

The value of "multipleOf" must be a integer, strictly greater than 0. The instance is valid if division by this keyword's value results in an integer.

##### `maximum`

The value of "maximum" must be a integer, representing an inclusive upper limit. This keyword validates only if the instance is less than or exactly equal to "maximum".

##### `exclusiveMaximum`

The value of "exclusiveMaximum" must be an integer, representing an exclusive upper limit. The instance is valid only if it has a value strictly less than (not equal to) "exclusiveMaximum".

##### `minimum`

The value of "minimum" must be an integer, representing an inclusive lower limit. This keyword validates only if the instance is greater than or exactly equal to "minimum".

##### `exclusiveMinimum`

The value of "exclusiveMinimum" must be a integer, representing an exclusive lower limit. The instance is valid only if it has a value strictly greater than (not equal to) "exclusiveMinimum".

#### For `{ "dataType": "list" }`

> **Note** Keywords in this section only applies to `list`. Using them in conjunction with an invalid data-type should result in an error.

##### `items`

The value of this keyword must be either another _Plutus Data Schema_ or a list of _Plutus Data Schema_. When this keyword is a single schema, it applies its subschema to all child instances of the list. When it is a list, then the list is expected to have exactly the same number of elements as specified by the keyword and each element must match against the schema corresponding to its position. The list variation is useful to represent product types such as tuples.

##### `maxItems`

The value of this keyword must be a non-negative integer. An array instance is valid against "maxItems" if its size is less than, or equal to, the value of this keyword.

##### `minItems`

The value of this keyword must be a non-negative integer. A list instance is valid against "minItems" if its size is greater than, or equal to, the value of this keyword. Omitting this keyword has the same behavior as a value of 0.

##### `uniqueItems`

The value of this keyword must be a boolean. If this keyword has boolean value false, the instance validates successfully. If it has boolean value true, the instance validates successfully if all of its elements are unique.

#### For `{ "dataType": "map" }`

> **Note** Keywords in this section only applies to `map`. Using them in conjunction with an invalid data-type should result in an error.

##### `keys`

The value of this keyword must be another _Plutus Data Schema_. This keyword applies its subschema to all keys of the map.

##### `values`

The value of this keyword must be another _Plutus Data Schema_. This keyword applies its subschema to all values of the map.

##### `maxItems`

The value of this keyword must be a non-negative integer. An object instance is valid against "maxItems" if its number of key-value pair elements is less than, or equal to, the value of this keyword.

##### `minItems`

The value of this keyword must be a non-negative integer. An object instance is valid against "minItems" if its number of key-value pair elements is greater than, or equal to, the value of this keyword.

#### For `{ "dataType": "constructor" }`

> **Note** Keywords in this section only applies to `constructor`. Using them in conjunction with an invalid data-type should result in an error.

##### `index`

This keyword's value must be a non-negative integer. An instance is valid against this keyword if it represents a Plutus constructor whose index is the same as this keyword's value. This keyword is mandatory.

##### `fields`

This keyword's value must be an array of valid _Plutus Data Schema_; possibly empty. An instance is valid against this keyword if it represents a Plutus constructor for which each field is valid under each subschema given by this keyword's value. Fields are compared positionally. This keyword is mandatory.

## Example(s)

<details>
  <summary>Aiken's Hello World</summary>

```json
{
  "$schema": "https://cips.cardano.org/cips/cip57/schemas/plutus-blueprint.json",

  "$id": "https://github.com/aiken-lang/aiken/blob/main/examples/hello_world/plutus.json",

  "$vocabulary": {
    "https://json-schema.org/draft/2020-12/vocab/core": true,
    "https://json-schema.org/draft/2020-12/vocab/applicator": true,
    "https://json-schema.org/draft/2020-12/vocab/validation": true,
    "https://cips.cardano.org/cips/cip57": true
  },

  "preamble": {
    "title": "aiken-lang/hello_world",
    "description": "Aiken contracts for project 'aiken-lang/hello_world'",
    "version": "1.0.0",
    "plutusVersion": "v2"
  },

  "validators": [
    {
      "title": "hello_world",
      "datum": {
        "title": "Datum",
        "purpose": "spend",
        "schema": {
          "anyOf": [
            {
              "title": "Datum",
              "dataType": "constructor",
              "index": 0,
              "fields": [
                {
                  "title": "owner",
                  "dataType": "bytes"
                }
              ]
            }
          ]
        }
      },
      "redeemer": {
        "title": "Redeemer",
        "schema": {
          "anyOf": [
            {
              "title": "Redeemer",
              "dataType": "constructor",
              "index": 0,
              "fields": [
                {
                  "title": "msg",
                  "dataType": "bytes"
                }
              ]
            }
          ]
        }
      },
      "compiledCode": "58ad0100003232322225333004323253330063372e646e64004dd7198009801002240009210d48656c6c6f2c20576f726c64210013233300100137586600460066600460060089000240206eb8cc008c00c019200022253335573e004294054ccc024cdc79bae300a00200114a226660060066016004002294088c8ccc0040052000003222333300a3370e008004016466600800866e0000d2002300d001001235573c6ea8004526165734ae855d11",
      "hash": "5e1e8fa84f2b557ddc362329413caa3fd89a1be26bfd24be05ce0a02"
    }
  ]
}
```
</details>

## Rationale: How does this CIP achieve its goals?

### Documenting binary interfaces

THe primary goal of this CIP is to offer a mean of interoperability between tools of the ecosystem. In a world where every step of a contract development happens within a single framework -- like it's been the case with PlutusTx, this may not be seen as particularly useful. However, as soon as we start having an ecosystem of tools that operate a different levels (e.g. a language compiler, a transaction building library, an chain explorer, ...) we need some level of interoperability between them. Because the on-chain binary interface is the ultimate source of truth, it only makes sense to find an adequate way to capture it.

### Choice of JSON-Schemas as a foundation

JSON schemas are pervasively used in the industry for describing all sort of data models. Over the years, they have matured enough to be well understood by and familiar to a large portion of developers. Plus, tooling now exists in pretty much any major language to parse and process JSON schemas. Thus, using it as a foundation for the blueprint only makes sense.

### Divergence from JSON-Schemas primitives

This specification defines a new set of primitives types such as `integer`, `bytes`, `list`, `map` and `constructor` instead of the classic `integer`, `number`, `string`, `bool`, `array`, `object`, `null`. This is not only to reflect better the underlying structure of Plutus data which differs from JSON by many aspects, but also to allow defining or re-defining logic and validation keywords for each of those primitives.

Note however that apart from the keyword `type`, the terminology (and semantic) used for JSON schemas has been preserved to not "reinvent the wheel" and makes it easier to build tools on top by leveraging what already exists. Plutus schemas do not use `type` but use `dataType` instead to avoid possible confusion with JSON-schemas. A Plutus data schema is almost a JSON-schemas, but only supports a subset of the available keywords and has subtle differences for some of them (e.g. keywords for the `bytes` data-type operate mostly on hex-encoded strings).

### UPLC builtins

In the original design specification of CIP-0057, we did not include UPLC builtins. But, there are a few legitimate cases where they might be found in the binary interface of validators. In particular, the `ProtoPair` builtin for constructing 2-tuples. This poses a problem of exhaustiveness (why only include ProtoPair and not the others where similar arguments could probably be made anyway). This is solved by being exhaustive in the capabilities of the blueprint specification, while discouraging their usage.

Another point of designs here is to make `Data` rather transparent and promote Data's constructor variants as first-class data-types even though it's not faithfully representing what is really happening on-chain. An alternative, more faithful, representation to what's proposed would have been to have `data` as one of the data-type, and then keywords that identifies which of the data variant we are dealing with. So for example, instead of writing:

```
{ "dataType": "integer" }
```

One would have written:

```
{ "dataType": "data", "variant": "iData" }
```

Yet, because we do want `Data` to be the primary binary interface medium, we keep the former notation as it's more succinct and is a unambiguous shorthand. This also allows to segregate all builtins behind a common notation -- that is, prefixed with a `#`.

### Purpose

Originally, blueprints did not include any notion of _purpose_. However, as one of the end goal is to utilize blueprint as an input source for user interfaces, it becomes useful to:

1. indicates under what circumstances is a certain validator expected to be used.
2. provides different schemas based on the purpose

Yet, whereas there's a notion of purpose on-chain that is tightly coupled to the script context, different on-chain framework may handle the purpose differently. Some may chose, for example, to abstract that concern away from their users. Which is why we only make the purpose an _optional_ field (except for `datum`) to leave a bit of flexibility for blueprint producers. For consumers, we recommend to treat purposes as discriminants to refine interfaces, but assume that a validator without purpose simply apply to _any_ purpose.

### Additional Resources

- https://json-schema.org/draft/2020-12/json-schema-core.html
- https://json-schema.org/draft/2020-12/json-schema-validation.html

## Path to Active

### Acceptance criteria

- [x] Blueprints are produced by one or (ideally) more smart-contract frameworks on Cardano.
  - [x] Aiken (implemented)
  - [ ] Plu-ts (under way)
  - [x] OpShin (implemented)
  - [ ] Helios (under consideration)
  - [ ] PlutusTx (?)
  - [ ] Plutarch (?)
  - [ ] Scalus (?)

- [x] There exist one or (ideally) more tools leveraging the blueprints
  - [x] [Aiken](https://aiken-lang.org/)
  - [x] [Mesh.js](https://meshjs.dev/)
  - [x] [Lucid](https://lucid.spacebudz.io/)
  - [x] [Bloxbean/cardano-client-lib](https://github.com/bloxbean/cardano-client-lib)
  - [ ] [PyCardano](https://pycardano.readthedocs.io)
  - [ ] [Demeter](https://demeter.run/)

### Implementation Plan

- [x] Write specifications for a few real-world contracts, identify and fix gaps
- [x] PoC of a toolkit generating blueprint definitions for a validator
- [x] Parse and interpret blueprints to produce smart-constructors for datums and redeemers in various languages
  - [x] JavaScript
  - [x] TypeScript
  - [ ] Python
- [x] (optional) develop a tool for rendering Plutus blueprint specifications as documentation
  - [paima/aiken-mdx](https://www.npmjs.com/package/@paima/aiken-mdx)

## Copyright

CC-BY-4.0
