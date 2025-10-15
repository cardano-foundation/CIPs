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
  - https://github.com/cardano-foundation/CIPs/pulls/?
Created: 2025-01-14
License: CC-BY-4.0
---

## Abstract

This CIP extends [CIP-100 | Governance Metadata][CIP-100] to introduce a standardized `onChain` property.
The `onChain` property encapsulates the on-chain effects using [CIP-116 | Standard JSON encoding for Domain Types][CIP-116] standard encoding,
enabling verification that metadata content matches on-chain action and preventing metadata replay attacks.
This applies to all types of governance metadata, including governance actions, votes, DRep registrations/updates, and Constitutional Committee resignations.

## Motivation: why is this CIP necessary?

Without a standardized mechanism to bind metadata to specific on-chain effects,
there is a security vulnerability: **metadata replay attacks**.

This vulnerability has been discussed via [CIPs Issue #970](https://github.com/cardano-foundation/CIPs/issues/970) by [Adam Dean](https://github.com/Crypto2099).

### Attack Scenario

A malicious actor could;

1. Copy the metadata from a legitimate treasury withdrawal governance action
2. Modify only the destination address in the on-chain action
3. Submit this as a new governance action with the copied metadata

From a voter's perspective, examining the metadata would show legitimate content (proper title, abstract, rationale, references, and author signatures).
However, the actual on-chain effect would send funds to a different address than described in the metadata.

In high-volume voting environments such attacks could succeed if voters don't manually verify that the metadata matches the on-chain effects.

### Other Author attacks

- discuss attacks where multiple authors are collaborating before constructing on-chain part
- having an onChain property prevents someone from attaching the signed metadata to the wrong thing

### Solution

By including the on-chain effects within the signed metadata body using the `onChain` property.

Metadata is bound to specific on-chain effects,
with author signature cryptographically locking it in.
This makes any metadata replay attacks,
where on-chain effects are edited automatically detectable.

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

> Note: `CIPXXX` represents this CIP's number once assigned.

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
  deposit: number;             // Lovelace
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

### Examples

#### Treasury Withdrawal

```json
{
  "@context": "...",
  "hashAlgorithm": "blake2b-256",
  "body": {
    "title": "Fund Development Team",
    "abstract": "Withdraw ₳100,000 to fund smart contract development team.",
    "motivation": "The team has delivered milestones and requires funding for continued work.",
    "rationale": "Funding will enable completion of the remaining project deliverables.",
    "onChain": {
      "@type": "ProposalProcedure",
      "deposit": 100000000000,
      "returnAddr": {
        "network": "mainnet",
        "paymentCred": null,
        "stakeCred": {
          "keyHash": "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2"
        }
      },
      "govAction": {
        "@type": "TreasuryWithdrawals",
        "withdrawals": {
          "stake1u8xj29v6qhja7zl0yk5u9q8x7w6v5u4t3s2r1q0p9o8n7m6l5k4j3h2g1f0e9d": 100000000000
        }
      }
    }
  },
  "authors": []
}
```

#### Protocol Parameter Change

```json
{
  "@context": "...",
  "hashAlgorithm": "blake2b-256",
  "body": {
    "title": "Increase Block Size to 96KB",
    "abstract": "Update maxBlockBodySize parameter from 90112 to 98304 bytes.",
    "motivation": "Current block size limits are constraining transaction throughput.",
    "rationale": "Analysis shows network can safely handle larger blocks, improving user experience.",
    "onChain": {
      "@type": "ProposalProcedure",
      "deposit": 100000000000,
      "returnAddr": {
        "network": "mainnet",
        "paymentCred": null,
        "stakeCred": {
          "keyHash": "b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3"
        }
      },
      "govAction": {
        "@type": "ParameterChange",
        "protocolParamUpdate": {
          "maxBlockBodySize": 98304
        },
        "policyHash": null,
        "prevGovActionId": null
      }
    }
  },
  "authors": []
}
```

#### Vote on Governance Action

```json
{
  "@context": "...",
  "hashAlgorithm": "blake2b-256",
  "body": {
    "title": "Vote YES on Budget Proposal",
    "abstract": "This metadata explains why I am voting YES on the 2025 budget proposal.",
    "motivation": "The proposed budget aligns with community priorities and includes proper accountability measures.",
    "rationale": "After reviewing the proposal details, the budget allocation is reasonable and the oversight mechanisms are sufficient.",
    "onChain": {
      "@type": "VotingProcedure",
      "govActionId": {
        "txId": "e14de8d9dc4f4ddf3fe9250a8a926e20f10e99b86bd0610b77d7a054981591ee",
        "govActionIx": 0
      },
      "voter": {
        "@type": "DRep",
        "credential": {
          "keyHash": "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2"
        }
      },
      "vote": "yes",
    }
  },
  "authors": []
}
```

#### DRep Registration

```json
{
  "@context": "...",
  "hashAlgorithm": "blake2b-256",
  "body": {
    "title": "DRep Registration - Alice's Delegation Pool",
    "abstract": "Registering as a DRep to represent community interests in governance.",
    "motivation": "I want to actively participate in Cardano governance and represent the interests of delegators who trust my judgment.",
    "rationale": "With 5 years of experience in the Cardano ecosystem and active participation in governance discussions, I am well-positioned to make informed voting decisions.",
    "onChain": {
      "@type": "RegDRepCert",
      "drepCredential": {
        "keyHash": "d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2"
      },
      "deposit": 2000000,
    }
  },
  "authors": []
}
```

### Verification Process

Tools **SHOULD** implement the following verification when processing governance actions:

1. **Parse On-Chain Data**: Extract the actual governance action from the blockchain
2. **Parse Metadata**: Retrieve and parse the governance action metadata
3. **Compare**: Verify that `body.onChain` matches the actual on-chain governance action
4. **Alert**: If mismatch detected, prominently warn users

### Author Signatures

When combined with [CIP-108][] author signatures, the `onChain` property is included in the signed `body` content. This means:

1. Author signature covers the described on-chain effects
2. Any modification to `onChain` invalidates the signature
3. Metadata replay with different on-chain effects is detectable

## Rationale

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

However, **security-conscious voters and tools** should prefer governance actions that include `onChain` and show verification status.

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
