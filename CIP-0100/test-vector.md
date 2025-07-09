# Test Vector for CIP-0100

Here we give some supporting files, give an example and explain how the [example.json](./example.json) was created.

## Common Context

### Common Fields

The context fields which could be added to CIP-100 compliant jsonld metadata.
See [cip-0100.common.jsonld](./cip-0100.common.jsonld).

### Common Fields Schema

A json schema for the common context fields.
See [cip-0100.common.schema.json](./cip-0100.common.schema.json).

## Example

CIP-100 off-chain metadata json example: [example.json](./example.json)

Blake2b-256 hash of the file (to go on-chain): `7b7d4a28a599bbb8c08b239be2645fa82d63a848320bf4760b07d86fcf1aabdc`

### Intermediate files

Files produced to articulate process, these are not necessary in implementations.

Body files, used to correctly generate author's witness:
- [example.body.json](./example.body.json)
- [example.body.nq](./example.body.nq)

Blake2b-256 hash digest of canonicalized body: `6d17e71c5793ed5945f58bf48e13bb1b3543187ab9c2afbd280a21afb4a90d35`

Whole document canonical representation, used to generate final hash:

- [example.nq](./example.nq)

### How-to Recreate

This tutorial creates additional intermediate files, these are not required in implementations but are shown here to articulate the process.

#### Author

Private extended signing key (hex):
`105d2ef2192150655a926bca9cccf5e2f6e496efa9580508192e1f4a790e6f53de06529129511d1cacb0664bcf04853fdc0055a47cc6d2c6d205127020760652`

Public verification key (hex):
`7ea09a34aebb13c9841c71397b1cabfec5ddf950405293dee496cac2f437480a`

#### 1. Create the example.json's `body`

Create the `example.json` file adding in all available values.
Then remove from this document any top-level field that is not `@context` or `body`.

This creates a intermediate file of [example.body.json](./example.body.json).

#### 2. Canonicalize the `body`

Using a tool which complies with the [RDF Dataset Canonicalization](https://w3c-ccg.github.io/rdf-dataset-canonicalization/spec/), create a canonicalized representation of [example.body.json](./example.body.json).
One such tool is the [JSON-LD Playground](https://json-ld.org/playground/).
Ensure the result ends in a newline.

This creates a intermediate file of [example.body.nq](./example.body.nq).

#### 3. Hash the canonicalized `body`

Using a tool create a Blake2b-256 hash of the canonicalized [example.body.nq](./example.body.nq).
One such tool is the [ToolKit Bay](https://toolkitbay.com/tkb/tool/BLAKE2b_256).

For our example this will result in: `6d17e71c5793ed5945f58bf48e13bb1b3543187ab9c2afbd280a21afb4a90d35`.

#### 4. Authors witness over the hash of canonicalized `body`

Use the hash produced in [3.](#3-hash-the-canonicalized-body) as the payload for the witness as described in [Hashing and Signatures](./README.md#hashing-and-signatures) for the chosen `witnessAlgorithm`.

One tool for Ed25519 signatures is [Ed25519 Online Tool](https://cyphr.me/ed25519_tool/ed.html).

For the provided [example.json](./example.json), we use the keys described in [Author](#author) resulting in a `signature` of: `68078efeff90970d2320a2bb5021d1aea81bc4907bf33d54fd17989f020719f3f5c4da3dccf7aa61d51c1e6fececd95309c37e7eef331b199cd5f8e78992ea0d`

#### 5. Add `authors` and `hashAlgorithm` to example.json

We can go back to our [example.body.json](./example.body.json) and now add in properties from outside of `body`.
- Adding the `hashAlgorithm` of `blake2b-256`.
- Adding the `authors`, including information of our `witness` produced via [4.](#4-authors-witness-over-the-hash-of-canonicalized-body).

By adding this information we create our [example.json](example.json).

#### 6. Hash example.json

To be able to create a final metadata hash which can be attached on-chain we simply hash the content of the file [example.json](example.json) as is

This results in: `7b7d4a28a599bbb8c08b239be2645fa82d63a848320bf4760b07d86fcf1aabdc`.

#### 7. Submit to chain

We can then host [example.json](./example.json) somewhere easily accessible following [Best Practices](./README.md#best-practices).

Then at submission time of the governance metadata anchor we can provide the on-chain transaction both the URI to the hosted [example.json](./example.json) but also the hash generated via [6.](#6-hash-examplejson).
