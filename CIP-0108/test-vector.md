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

Blake2b-256 of the canonicalized document (to go onchain): `931f1d8cdfdc82050bd2baadfe384df8bf99b00e36cb12bfb8795beab3ac7fe5`

See:
- [treasury-withdrawal.jsonld](./examples/treasury-withdrawal.jsonld).
- [treasury-withdrawal.body.canonical](./examples/treasury-withdrawal.body.canonical).
- [treasury-withdrawal.canonical](./examples/treasury-withdrawal.canonical).

### Motion of No-Confidence

Blake2b-256 of the canonicalized document (to go onchain): `f5da6b55e1b24e657984a99b1155c307b24284472d409ab3ea8871f8ca1d3194`

See:
- [no-confidence.jsonld](./examples/no-confidence.jsonld).
- [no-confidence.body.canonical](./examples/no-confidence.body.canonical).
- [no-confidence.canonical](./examples/no-confidence.canonical).