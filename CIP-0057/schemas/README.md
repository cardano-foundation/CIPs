# Plutus Contract Blueprint - Meta-Schemas

In these folders you'll find meta JSON-schemas for CIP-0057; Meta-schemas are JSON schemas describing how a Plutus Contract Blueprint should be structured. They also define several common data-types that can be referenced when writing your own specification.

Schema                                                               | Description
---                                                                  | ---
[plutus-blueprint.json](./plutus-blueprint.json)                     | The meta-schema for the blueprint specification document itself
[plutus-blueprint-argument.json](./plutus-blueprint-argument.json)   | The meta-schema for blueprints runtime arguments (i.e datums & redeemers)
[plutus-blueprint-parameter.json](./plutus-blueprint-parameter.json) | The meta-schema for blueprints compile-time parameters
[plutus-data.json](./plutus-data.json)                               | Definitions of the _Plutus Data Schema_ and the various supported keywords
[plutus-builtin.json](./plutus-builtin.json)                         | Definitions of the Untyped Plutus Core builtin types
