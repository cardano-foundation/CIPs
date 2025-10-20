---
CIP: ?
Title: Governance Metadata - On-Chain Effects
Category: Metadata
Status: Proposed
Authors:
  - Ryan Williams <ryan.williams@intersectmbo.org>
Implementors:
  - Ryan Williams <ryan.williams@intersectmbo.org>
Discussions:
  - https://github.com/cardano-foundation/CIPs/pull/1101
Created: 2025-10-15
License: CC-BY-4.0
---

## Abstract

This CIP extends [CIP-100 | Governance Metadata][CIP-100] to introduce a standardized `onChain` property.
The `onChain` property encapsulates the on-chain effects using [CIP-116 | Standard JSON encoding for Domain Types][CIP-116] standard encoding,
enabling verification that metadata content matches on-chain action and preventing metadata replay attacks.
This can be applied to all types of governance metadata, including governance actions, votes, DRep registrations/updates, and Constitutional Committee resignations.

## Motivation: why is this CIP necessary?

Without a standardized mechanism to bind metadata to specific on-chain effects,
there is a security vulnerability in **metadata replay attacks**.

This vulnerability has been discussed via [CIPs Issue #970](https://github.com/cardano-foundation/CIPs/issues/970) by [Crypto2099](https://github.com/Crypto2099) and further within [CIPs Issue #978](http://github.com/cardano-foundation/CIPs/issues/978) by [gitmachtl](https://github.com/gitmachtl).

### Metadata Replay

A malicious actor could;

1. Copy the metadata from a legitimate treasury withdrawal governance action
2. Modify only the destination address in the on-chain action
3. Submit this as a new governance action with the copied metadata

From a voter's perspective, examining the metadata would show legitimate content (proper title, abstract, rationale, references, and author signatures).
However, the actual on-chain effect would send funds to a different, malicious address.

In high-volume voting environments such attacks could succeed if voters don't manually verify that the metadata matches the on-chain effects.
Relying on manual verification by voters is error prone and inefficient.

### Other Author attacks

- discuss attacks where multiple authors are collaborating before constructing on-chain part
- having an onChain property prevents someone from attaching the signed metadata to the wrong thing

## Specification

### The `onChain` Property

The `onChain` property is a new **optional** property within the `body` object of [CIP-100][] governance metadata.

#### JSON-LD Context

The `onChain` property shall be defined in the JSON-LD `@context` as follows:

```json
{
  "@context": {
    "CIP116": "https://github.com/cardano-foundation/CIPs/blob/master/CIP-0116/README.md#",
    "body": {
      "@id": "CIP100:body",
      "@context": {
        "onChain": {
          "@id": "CIPXXX:onChain"
        }
      }
    }
  }
}
```

> [!NOTE]
> `CIPXXX` represents this CIP's number once assigned.

#### Structure

The `onChain` property **MUST** conform to one of the [CIP-116][] Conway-era governance types.
The specific type is indicated by the `@type` field within the `onChain` object.

> ⚠️ Note: any entry of anchor properties within the CIP116 objects must be removed as they constitute a circular dependency

##### Supported Types

**For Governance Actions:**

The `onChain` property conforms to the [CIP-116][] `ProposalProcedure` type:

```typescript
type OnChain = {
  "@type": "ProposalProcedure";
  deposit: number;           // Lovelace
  returnAddr: Address;       // CIP-116 Address type
  govAction: GovAction;      // CIP-116 GovAction type
}
```

Where `GovAction` is one of the [CIP-116][] Conway-era governance action types:

- `InfoAction`
- `ParameterChange`
- `HardForkInitiation`
- `TreasuryWithdrawals`
- `NoConfidence`
- `UpdateCommittee`
- `NewConstitution`

See [CIP-116 cardano-conway.json](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0116/cardano-conway.json) for complete type definitions.

**For Votes:**

The `onChain` property conforms to the [CIP-116][] `VotingProcedure` type:

```typescript
type OnChain = {
  "@type": "VotingProcedure";
  govActionId: {
    txId: string;        // Transaction ID (hex)
    govActionIx: number; // Governance action index
  };
  voter: Voter;          // CIP-116 Voter type (DRep, SPO, or CC)
  vote: Vote;            // "yes" | "no" | "abstain"
}
```

**For DRep Registration:**

The `onChain` property conforms to the [CIP-116][] DRep registration certificate structure:

```typescript
type OnChain = {
  "@type": "RegDRepCert";
  drepCredential: Credential;  // CIP-116 Credential type
  deposit: number;             // Lovelace amount
}
```

**For DRep Update:**

The `onChain` property conforms to the [CIP-116][] DRep update certificate structure:

```typescript
type OnChain = {
  "@type": "UpdateDRepCert";
  drepCredential: Credential;  // CIP-116 Credential type
}
```

**For Committee Cold Credential Resignation:**

The `onChain` property conforms to the [CIP-116][] committee resignation certificate structure:

```typescript
type OnChain = {
  "@type": "ResignCommitteeColdCert";
  committeeColdCredential: Credential;  // CIP-116 Credential type
}
```

### Verification Process

Tools **SHOULD** implement the following verification when processing governance actions:

1. **Parse On-Chain Data**: Extract the on-chain data which the metadata is attached to
2. **Parse Metadata**: Retrieve and parse the governance metadata
3. **Author Signature Check**: Validate the author signatures are all correct
4. **Compare**: Verify that `body.onChain` matches the actual on-chain effect
5. **Alert**: If there are invalid author signatures and/or the `onChain` does not match, warn the user

### Examples

Please see [examples/](./examples/).

## Rationale

By including the on-chain effects within the signed metadata body using the `onChain` property.
Metadata is bound to specific on-chain effects,
with author signature cryptographically locking it in.
This makes any metadata replay attacks, machine detectable.
This allows governance tools to automatically verify this for voters.

### Why Extend CIP-100?

[CIP-100][] provides the base structure for governance metadata.
This extension adds security-critical information while maintaining backward compatibility.

### Why Use CIP-116 Encoding?

[CIP-116][] provides standardized JSON encoding for Cardano domain types.

### Why Optional?

The `onChain` property is optional to maintain backward compatibility.

This CIP is fully backward compatible:

- **Existing Metadata**: Governance actions without `onChain` remain valid
- **Parsers**: Parsers ignoring `onChain` continue to work
- **Validators**: Validators not checking `onChain` continue to work

## Open Questions

- How to handle `anchor` property inside of CIP116 objects in a nice way?

## Path to Active

### Acceptance Criteria

This CIP is considered **Active** when:

1. The specification is merged into the CIPs repository
2. At least two governance metadata authoring tools implement support
3. At least one verification tool implements on-chain comparison
4. Documentation and examples are available

### Implementation Plan

- todo

## Copyright

This CIP is licensed under [CC-BY-4.0][].

[CIP-100]: https://github.com/cardano-foundation/CIPs/blob/master/CIP-0100/README.md
[CIP-108]: https://github.com/cardano-foundation/CIPs/blob/master/CIP-0108/README.md
[CIP-116]: https://github.com/cardano-foundation/CIPs/blob/master/CIP-0116/README.md
[CC-BY-4.0]: https://creativecommons.org/licenses/by/4.0/legalcode
