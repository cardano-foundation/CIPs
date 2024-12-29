# Test Vector for CIP-136

Here we create some useful definitions and some examples.

## Common Context

### Common Fields

The context fields which could be added to CIP-136 compliant jsonld files.
See [cip-0136.common.jsonld](./cip-136.common.jsonld).

### Common Fields Schema

A json schema for the common context fields.
See [cip-0136.common.schema.json](./cip-136.common.schema.json).

## Examples

### Treasury Withdrawal is Unconstitutional

Example metadata document file: [treasury-withdrawal-unconstitutional.jsonld](./examples/treasury-withdrawal-unconstitutional.jsonld).

Blake2b-256 of the file content (to go on-chain): `cf289476f8481aabcd20b62dc9635883d8a0ff092a656a1c9b5914d7cce12285`

#### Intermediate files

Files produced to articulate process, these are not necessary in implementations.

Body files, used to correctly generate author's witness:

- [treasury-withdrawal-unconstitutional.body.jsonld](./examples/treasury-withdrawal-unconstitutional.body.jsonld)

- [treasury-withdrawal-unconstitutional.body.nq](./examples/treasury-withdrawal-unconstitutional.body.nq)

Blake2b-256 hash digest of canonicalized body: `7b2c08cafbdf7b524035c1f7face3af9f0370d2df4d5c841ebb83b4e5a843e64`

## How-to Recreate Examples

This tutorial creates additional intermediate files, these are not required in implementations but are shown here to articulate the process.

### Author

Keys used for author property, provided here for convenience.

Private extended signing key (hex): `105d2ef2192150655a926bca9cccf5e2f6e496efa9580508192e1f4a790e6f53de06529129511d1cacb0664bcf04853fdc0055a47cc6d2c6d205127020760652`

Public verification key (hex):
`7ea09a34aebb13c9841c71397b1cabfec5ddf950405293dee496cac2f437480a`

Public verification key hash (hex): `0fdc780023d8be7c9ff3a6bdc0d8d3b263bd0cc12448c40948efbf42`

Mainnet public enterprize address (hex): `610fdc780023d8be7c9ff3a6bdc0d8d3b263bd0cc12448c40948efbf42`

### 1. Create the example.jsonld's `body`

Create the `example.jsonld` file adding in all available values.
Then remove from this document any top-level field that is not `@context` or `body`.

If recreating the [Treasury Withdrawal Vote](#treasury-withdrawal-is-unconstitutional), this will result in the intermediate file of [treasury-withdrawal-unconstitutional.body.jsonld](./examples/treasury-withdrawal-unconstitutional.body.jsonld).

### 2. Canonicalize the `body`

Using a tool which complies with the [RDF Dataset Canonicalization](https://w3c-ccg.github.io/rdf-dataset-canonicalization/spec/), create a canonicalized representation of `example.body.jsonld`.
One such tool is the [JSON-LD Playground](https://json-ld.org/playground/).
Ensure the result ends in a newline.

This creates `example.body.nq`.

For [Treasury Withdrawal Vote](#treasury-withdrawal-is-unconstitutional), this will result in the intermediate file of [treasury-withdrawal-unconstitutional.body.nq](./examples/treasury-withdrawal-unconstitutional.body.nq).

### 3. Hash the canonicalized `body`

Using a tool create a Blake2b-256 hash of the canonicalized `example.body.nq`.
One such tool is the [ToolKit Bay](https://toolkitbay.com/tkb/tool/BLAKE2b_256).

For [Treasury Withdrawal Vote](#treasury-withdrawal-is-unconstitutional), this will result in: `7b2c08cafbdf7b524035c1f7face3af9f0370d2df4d5c841ebb83b4e5a843e64`.

### 4. Authors witness over the hash of canonicalized `body`

Use the hash produced in [3.](#3-hash-the-canonicalized-body) as the payload for the witnessing. For a `witnessAlgorithm` of `ed25519` refer to [CIP-100 Hashing and Signatures](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0100/README.md#hashing-and-signatures).

One tool for Ed25519 signatures is [Ed25519 Online Tool](https://cyphr.me/ed25519_tool/ed.html).

For [Treasury Withdrawal Vote](#treasury-withdrawal-is-unconstitutional), we use the keys described in [Author](#author) resulting in: `ad071d5a032c6e0eb7ee0ad4422728d0991bc0865473b4e2b0694356448790b0c90a50827cd355fba89fe2c7095b46179a4d3990642cdced6af2cd1363e6af0d`.

### 5. Add other properties to example.jsonld

We can go back to our `example.body.jsonld` and now add in all missing properties, from outside of `body`.

- Adding the `hashAlgorithm` of `blake2b-256`.

- Adding the `authors` with a single entry, including information of our `witness` goes into the `signature`.

By adding this information we create our `example.jsonld`.

For [Treasury Withdrawal Vote](#treasury-withdrawal-is-unconstitutional), this will result in [treasury-withdrawal-is-unconstitutional.jsonld](./examples/treasury-withdrawal-unconstitutional.jsonld).

### 6. Hash example.jsonld

To be able to create a final metadata hash which can be attached on-chain we simply hash the content of the file [Treasury Withdrawal Vote](#treasury-withdrawal-is-unconstitutional) as is.

This results is: `cf289476f8481aabcd20b62dc9635883d8a0ff092a656a1c9b5914d7cce12285`.

### 7. Submit to chain

We can then host `example.jsonld` somewhere easily accessible following [CIP-100 Best Practices](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0100/README.md#best-practices).

Then at submission time of the vote we can provide the on-chain transaction both the URI to the hosted `example.jsonld` but also the hash generated via [6.](#6-hash-examplejsonld).
