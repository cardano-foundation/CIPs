# Test Vector for CIP-0108

Here we create some useful definitions and some example metadata.

## Common Context

### Common Fields
The context fields which could be added to CIP-108 compliant jsonld files.
See [cip-0108.common.jsonld](./cip-0108.common.jsonld).

### Common Fields Schema
A json schema for the common context fields.
See [cip-0108.common.schema.json](./cip-0108.common.schema.json).

## Examples

### Treasury Withdrawal

Example metadata document file: [treasury-withdrawal.jsonld](./examples/treasury-withdrawal.jsonld).
Blake2b-256 of the canonicalized document (to go onchain): `6685960f5884922e135a951f8acb581ff7202fc111ec405a7e014ae725927aae`

#### Intermediate files

Body files, used to correctly generate author's witness:
- [treasury-withdrawal.body.jsonld](./examples/treasury-withdrawal.body.jsonld)
- [treasury-withdrawal.body.canonical](./examples/treasury-withdrawal.body.canonical)

Blake2b-256 hash digest of canonicalized body: `68d6fe27087457acf0164e65414238c43573192c99f30341926d1524924d71ca`
  
Whole document canonical representation, used to generate final hash:
- [treasury-withdrawal.canonical](./examples/treasury-withdrawal.canonical)

### Motion of No-Confidence

Example metadata document file: [no-confidence.jsonld](./examples/no-confidence.jsonld).
Blake2b-256 of the canonicalized document (to go onchain): `c382be96dd98c4bbd6d3afe81f0c8143e70fbb6b8855303e69a6606991a4e909`

#### Intermediate files

Body files, used to correctly generate author's witness:
- [no-confidence.body.jsonld](./examples/no-confidence.body.jsonld)
- [no-confidence.body.canonical](./examples/no-confidence.body.canonical)

Blake2b-256 hash digest of canonicalized body: `4a7ecc544559df67ece3f7f90f76c4e3e7e329a274c79a06dcfbf28351db600e`

Whole document canonical representation, used to generate final hash:
- [no-confidence.canonical](./examples/no-confidence.canonical)

## How-to Recreate Examples

### Author

Keys used for author property, provided here for convenience.

Private extended signing key (hex):
```
105d2ef2192150655a926bca9cccf5e2f6e496efa9580508192e1f4a790e6f53de06529129511d1cacb0664bcf04853fdc0055a47cc6d2c6d205127020760652
```

Public verification key (hex):
```
7ea09a34aebb13c9841c71397b1cabfec5ddf950405293dee496cac2f437480a
```

Public verification key hash (hex):
```
0fdc780023d8be7c9ff3a6bdc0d8d3b263bd0cc12448c40948efbf42
```

Mainnet public enterprize address (hex):
```
610fdc780023d8be7c9ff3a6bdc0d8d3b263bd0cc12448c40948efbf42
```

### 1. Create the example.jsonld's `body`

Create a `example.body.jsonld` and copy in all content from [cip-0108.common.jsonld](./cip-0108.common.jsonld) then fill in the body property with example data.

If recreating the [Treasury Withdrawal](#treasury-withdrawal), this will result in [treasury-withdrawal.body.jsonld](./examples/treasury-withdrawal.body.jsonld).

### 2. Canonicalize the `body`

Using a tool which complies with the [RDF Dataset Canonicalization](https://w3c-ccg.github.io/rdf-dataset-canonicalization/spec/), create a canonicalized representation of `example.body.jsonld`.
One such tool is the [JSON-LD Playground](https://json-ld.org/playground/).
Ensure the results ends in a newline.

This creates `example.body.canonical`.

For [Treasury Withdrawal](#treasury-withdrawal), this will result in [treasury-withdrawal.body.canonical](./examples/treasury-withdrawal.body.canonical).

### 3. Hash the canonicalized `body`

Using a tool create a Blake2b-256 hash of the canonicalized `example.body.canonical`.
One such tool is the [ToolKit Bay](https://toolkitbay.com/tkb/tool/BLAKE2b_256).

For [Treasury Withdrawal](#treasury-withdrawal), this will result in: `68d6fe27087457acf0164e65414238c43573192c99f30341926d1524924d71ca`.

### 4. Authors witness over the hash of canonicalized `body`

Use the hash produced in [3.](#3-hash-the-canonicalized-body) as the payload for the witnessing. For a `witnessAlgorithm` of `ed25519` refer to [CIP-100 Hashing and Signatures](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0100/README.md#hashing-and-signatures), for `cip-0008` refer to [CIP-108 New Witness Type](./README.md#new-witness-type).

For [Treasury Withdrawal](#treasury-withdrawal), we use the keys described in [Author](#author) resulting in: `a476985b4cc0d457f247797611799a6f6a80fc8cb7ec9dcb5a8223888d0618e30de165f3d869c4a0d9107d8a5b612ad7c5e42441907f5b91796f0d7187d64a01`.

### 5. Add other properties to example.jsonld

We can go back to our `example.body.jsonld` and now add in all missing properties, from outside of `body`.
- Adding the `hashAlgorithm` of `blake2b-256`.
- Adding the `authors` with a single entry, including information of our `witness` goes into the `signature`.

By adding this information we create our `example.jsonld`.

For [Treasury Withdrawal](#treasury-withdrawal), this will result in [treasury-withdrawal.jsonld](./examples/treasury-withdrawal.jsonld).

### 6. Canonicalize example.jsonld

To be able to create a final metadata hash which can be attached on-chain we must first canonicalize the `example.jsonld`.
Ensure the results ends in a newline.

This creates `example.canonical`.

For [Treasury Withdrawal](#treasury-withdrawal), this will result in [treasury-withdrawal.canonical](./examples/treasury-withdrawal.canonical).

### 7. Hash the canonicalized example.jsonld

We then use the specified `hashAlgorithm` on `example.canonical`.

For [Treasury Withdrawal](#treasury-withdrawal), this will result in `6685960f5884922e135a951f8acb581ff7202fc111ec405a7e014ae725927aae`.

### 8. Submit to chain

We can then host `example.jsonld` somewhere easily accessible following [CIP-100 Best Practices](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0100/README.md#best-practices).

Then at submission time of the governance metadata anchor we can provide the on-chain transaction both the URI to the hosted `example.jsonld` but also the hash generated via [7.](#7-hash-the-canonicalized-examplejsonld).