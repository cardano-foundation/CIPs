---
CIP: /?
Title: Restricted format for C509 compatibility with Plutus
Category: MetaData
Status: Proposed
Authors:
    - Steven Johnson<steven.johnson@iohk.io>
Implementors: []
Discussions:
    - https://github.com/cardano-foundation/CIPs/pull/812
Created: 2023-10-24
License: CC-BY-4.0
---

## Abstract

Plutus can access metadatums that encode C509 certificates.
This specification documents the restricted feature set of those certificates.

## Motivation: why is this CIP necessary?

To keep complexity low, this specification details a set of restrictions
on-top of a standard C509 certificate definition.
These restrictions help plutus support the important features of
x509 certificates in smart contracts on-chain.

They also help reduce the amount of data stored on-chain.

## Specification

See [c509-cert-plutus-restricted.cddl](./c509-cert-plutus-restricted.cddl).
This is the formal specification which describes the requirements of on-chain x509 certificates.
ust include a CDDL schema in it's specification.

## Rationale: how does this CIP achieve its goals?

By clearly defining the feature set that plutus scripts can accept from C509 certificates it is easier for
script writers and certificate creators to produce interoperable certificates.

## Path to Active

This draft CIP requires extensive collaboration with multiple parties in order to arrive at a
correct and viable specification.

It has been kept deliberately terse in order for that process to be as open and collaborative as possible.

### Acceptance Criteria

* General community consensus on the minimum standard needs to be agreed.

### Implementation Plan

## Copyright

This CIP is licensed under [CC-BY-4.0]

Code samples and reference material are licensed under [Apache 2.0]
