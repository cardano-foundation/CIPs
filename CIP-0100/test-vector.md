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

Blake2b-256 hash of the file (to go on-chain): `04af1b48bccbf7cf9b3e3b7952dfbdde0cc851ccb87ae6643521672cc381b00d`

### Intermediate files

Files produced to articulate process, these are not necessary in implementations.

Body files, used to correctly generate author's witness:
- [example.body.json](./example.body.json)
- [example.body.nq](./example.body.nq)

Blake2b-256 hash digest of canonicalized body: `cc4ab8ead604ddb498ed4b2916af7b454c65ac783b5d836fddf388e72a40eccb`

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

For our example this will result in: `cc4ab8ead604ddb498ed4b2916af7b454c65ac783b5d836fddf388e72a40eccb`.

#### 4. Authors witness over the hash of canonicalized `body`

Use the hash produced in [3.](#3-hash-the-canonicalized-body) as the payload for the witness as described in [Hashing and Signatures](./README.md#hashing-and-signatures) for the chosen `witnessAlgorithm`.

For the provided [example.json](./example.json), we use the keys described in [Author](#author) resulting in a `signature` of: `340c2ef8d6abda96769844ab9dca2634ae21ef97ddbfad1f8843bea1058e40d656455a2962143adc603d063bbbe27b54b88d002d23d1dff1cd0e05017cd4f506`

#### 5. Add `authors` and `hashAlgorithm` to example.json

We can go back to our [example.body.json](./example.body.json) and now add in properties from outside of `body`.
- Adding the `hashAlgorithm` of `blake2b-256`.
- Adding the `authors`, including information of our `witness` produced via [4.](#4-authors-witness-over-the-hash-of-canonicalized-body).

By adding this information we create our [example.json](example.json).

#### 6. Hash example.json

To be able to create a final metadata hash which can be attached on-chain we simply hash the content of the file [example.json](example.json) as is

This results in: `04af1b48bccbf7cf9b3e3b7952dfbdde0cc851ccb87ae6643521672cc381b00d`.

#### 7. Submit to chain

We can then host [example.json](./example.json) somewhere easily accessible following [Best Practices](./README.md#best-practices).

Then at submission time of the governance metadata anchor we can provide the on-chain transaction both the URI to the hosted [example.json](./example.json) but also the hash generated via [6.](#6-hash-examplejson).
