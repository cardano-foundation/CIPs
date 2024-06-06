# Test Vector for CIP-0119

Here we give some supporting files, give an example and explain how the [drep.jsonld](./examples/drep.jsonld) was created.

## Common Context

### Common Fields

The context fields which could be added to CIP-119 compliant jsonld metadata.
See [cip-0119.common.jsonld](./cip-0119.common.jsonld).

### Common Fields Schema

A json schema for the common context fields.
See [cip-0119.common.schema.json](./cip-0119.common.schema.json).

## Example

CIP-119 off-chain metadata json example: [drep.jsonld](./examples/drep.jsonld)

Blake2b-256 hash of the canonicalize example (to go on-chain): `a7a5cf6bfcad40e7b43653dae26344d6fbb5d7a2ef8de56a5e43703b298b94b5`

### Intermediate files

File produced to articulate process, these are not necessary in implementations.

Whole document canonical representation, used to generate final hash:

- [drep.nq](./examples/drep.nq)
