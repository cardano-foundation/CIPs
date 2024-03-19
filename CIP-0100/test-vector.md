# Test Vector for CIP-0100

Here we explain how the [example.json](./example.json) was created and give context to supporting files.

## Common Context

### Common Fields
The context fields which could be added to CIP-100 compliant jsonld metadata.
See [cip-0100.common.jsonld](./cip-0100.common.jsonld).

### Common Fields Schema
A json schema for the common context fields.
See [cip-0100.common.schema.json](./cip-0100.common.schema.json).

## Example

CIP-100 off-chain metadata json example: [example.json](./example.json)

Blake2b-256 hash of the canonicalize example (to go on-chain): `64beba3cb329afb5f2901e666b1d403dce85566da3598da58b25d3b0105a3a15`

### How-to Recreate

#### 1. Create the example.json's `body`

Using the [cip-0100.common.jsonld](./cip-0100.common.jsonld) add in the body property with the example data.

This creates [example.body.jsonld](./example.body.jsonld).

#### 2. Canonicalize the `body`

Using a tool which complies with the [RDF Dataset Canonicalization](https://w3c-ccg.github.io/rdf-dataset-canonicalization/spec/), create a canonicalized representation of [example.body.jsonld](./example.body.jsonld).
One such tool is the [JSON-LD Playground](https://json-ld.org/playground/).
Ensure the results ends in a newline.

This creates [example.body.canonical](./example.body.canonical).

#### 3. Hash the canonicalized `body`

Using a tool create a Blake2b-256 hash of the canonicalized [example.body.canonical](./example.body.canonical).
One such tool is the [ToolKit Bay](https://toolkitbay.com/tkb/tool/BLAKE2b_256).

This will result in: `cc4ab8ead604ddb498ed4b2916af7b454c65ac783b5d836fddf388e72a40eccb`.

#### 4. Authors witness over the hash of canonicalized `body`

Use the hash produced in [3.](#3-hash-the-canonicalized-body) as the payload for the witness as described in [Hashing and Signatures](./README.md#hashing-and-signatures).

In the provided [example.json](./example.json) we just add mock placeholder of `abcd` for the produced signature.

#### 5. Add other properties to example.json

We can go back to our [example.body.json](./example.body.json) and now add in all missing properties, from outside of `body`.
- Adding the `hashAlgorithm` of `blake2b-256`.
- Adding the `authors` with a single entry, including information of our `witness` where our placeholder of `abcd` goes to the `signature`.

By adding this information we create our [example.json](example.json).

#### 6. Canonicalize example.json

To be able to create a final metadata hash which can be attached on-chain we must first canonicalize the [example.json](example.json).
Ensure the results ends in a newline.

This creates [example.canonical](./example.canonical).

#### 7. Hash the canonicalized example.json

We then use the specified `hashAlgorithm` on [example.canonical](./example.canonical).

This results in: `64beba3cb329afb5f2901e666b1d403dce85566da3598da58b25d3b0105a3a15`.

#### 8. Submit to chain

We can then host [example.json](./example.json) somewhere easily accessible following [Best Practices](./README.md#best-practices).

Then at submission time of the governance metadata anchor we can provide the on-chain transaction both the URI to the hosted [example.json](./example.json) but also the hash generated via [7.](#7-hash-the-canonicalized-examplejson).
