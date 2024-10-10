# Test Vector for CIP-136

Here we create some useful definitions and some examples.

## Common Context

### Common Fields

The context fields which could be added to CIP-136 compliant jsonld files.
See [cip-0136.common.jsonld](./cip-0136.common.jsonld).

### Common Fields Schema

A json schema for the common context fields.
See [cip-0136.common.schema.json](./cip-0136.common.schema.json).

## Examples

### Treasury Withdrawal is Unconstitutional

Example metadata document file: [treasury-withdrawal-unconstitutional.jsonld](./examples/treasury-withdrawal-unconstitutional.jsonld).
Blake2b-256 of the file content (to go onchain): `267e27b987740d55ad4f5eb945ee20f2a9fdbeb604dad4f237276065044da926`

#### Intermediate files

Files produced to articulate process, these are not necessary in implementations.

Body files, used to correctly generate author's witness:
- [treasury-withdrawal-unconstitutional.body.jsonld](./examples/treasury-withdrawal-unconstitutional.body.jsonld)
- [treasury-withdrawal-unconstitutional.body.nq](./examples/treasury-withdrawal-unconstitutional.body.nq)

Blake2b-256 hash digest of canonicalized body: ``

## How-to Recreate Examples

This tutorial creates additional intermediate files, these are not required in implementations but are shown here to articulate the process.

### Author

Keys used for author property, provided here for convenience.

Private extended signing key (hex): `105d2ef2192150655a926bca9cccf5e2f6e496efa9580508192e1f4a790e6f53de06529129511d1cacb0664bcf04853fdc0055a47cc6d2c6d205127020760652`

Public verification key (hex):
`7ea09a34aebb13c9841c71397b1cabfec5ddf950405293dee496cac2f437480a`

Public verification key hash (hex): `0fdc780023d8be7c9ff3a6bdc0d8d3b263bd0cc12448c40948efbf42`

Mainnet public enterprize address (hex): `610fdc780023d8be7c9ff3a6bdc0d8d3b263bd0cc12448c40948efbf42`




