# CIP-88: Common Properties

We use this common directory to declare some definitions that are shared across multiple points of the standard to
decrease redundant declarations and hopefully minify errors.

## CIP-88 Master CDDL Specification

The master, top-level CIP-88 CDDL specification is declared in [CIP-88 Master CDDL](./CIP88_Master_v1.cddl).

## URI Array Schema

CIP-88 defines a "URI Array" as a well-formed array that can be used to declare URIs in metadata in a standardized way
that is easy to reconstruct when the length of a URI may exceed the string length available to on-chain metadata objects.

View [URI Array Schema](./uri-array.schema.json) for details.

## Token Project Details Schema

CIP-25 and CIP-68 share commonality in that both represent token project "collections" that have many frequent/recurring
definitions that must be shared with explorers and marketplaces. We declare a common and shared structure for this 
"collection data" that is documented further at [Token Project Details v1](./Token-Project-Details_v1.md).