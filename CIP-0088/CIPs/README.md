# CIP-0088: CIP-Specific Details

This document describes the format and standards to be used when adding a CIP-specific extension to CIP-88.

## Why CIP-Specific Extensions?

The CIP-88 Standard was developed to be future-proof and extensible from the beginning and is the primary rationale for
including CIP-Specific fields and information in a separately versioned and documented format to allow individual 
components of the standard to expand and develop at their own pace while keeping the core functionality of the standard
unchanged.

The hope is that this method will provide for ultimate flexibility while making it easy for downstream integrators to
provide functionality for the pieces of information that they choose to explicitly accept.

## Documentation Format

Each CIP-Specific Extension to CIP-88 MUST include a readme documentation of the specified fields as well as a CBOR
CDDL file describing the on-ledger format of the metadata. A JSON example and schema document SHOULD also be included.

CIP-Specific Extensions to CIP-88 SHOULD only be added after the referenced CIP has achieved `Active` status following
community review and CIP-88 Extensions MUST be added as separate pull requests to further undergo community review and
feedback prior to acceptance as part of the CIP-88 standard.

CIP-Specific Extensions documentation MUST be placed within a zero-prefixed directory with the CIP numerical ID within
this directory.

All documents SHOULD follow the format and naming examples found in the [Templates](./template) directory.





