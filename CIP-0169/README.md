---
CIP: 169
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
The `onChain` property encapsulates the on-chain effects using [CIP-0116 | Standard JSON encoding for Domain Types][CIP-0116] standard encoding,
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

### Multi-Author Misattachment

When metadata is jointly authored multiple parties signing the same `body` before the on-chain action is constructed there is a window between *signing* and *submission* in which the signed payload can be attached to the *wrong* on-chain effect.

Concretely, consider a multi-author treasury withdrawal:

1. Authors A, B, and C draft and sign metadata describing a withdrawal of ₳50,000 to address `stake1...legit`.
2. Author C, who controls submission, swaps the on-chain `ProposalProcedure` to send the funds elsewhere or to a *different recipient* in a list of withdrawals and submits using the original signed metadata.
3. Verifiers see three valid author signatures over a body that *describes* the legitimate withdrawal, but the actual on-chain effect differs.

Without `onChain`,
the author signatures only attest to the prose narrative.
Anchoring the signed body to the exact on-chain effect closes this gap: any divergence between the bound `onChain` value and the submitted action invalidates the binding, and tools can refuse to display the metadata as endorsed.

## Specification

### The `onChain` Property

The `onChain` property is a new **optional** property within the `body` object of [CIP-100][] governance metadata.

#### JSON-LD Context

The `onChain` property is defined in the JSON-LD `@context` under the `CIP169` namespace,
with each CIP-0116 sub-property (`deposit`, `reward_account`, `gov_action`, `tag`, `rewards`, `gov_action_id`, `transaction_id`, `gov_action_index`, `voter`, `voting_procedure`, `vote`, `protocol_param_update`, `protocol_version`, `policy_hash`, `committee`, `members_to_remove`, `signature_threshold`, `constitution`, `script_hash`, `drep_credential`, `committee_cold_credential`, `coin`, etc.) mapped under the `CIP116` namespace.
Mapping every reachable property is **required**: any term left undefined is dropped during canonicalization, which would silently exclude the on-chain payload from the author signature and defeat the purpose of this CIP.

A example (see [`cip-0169.common.jsonld`](./cip-0169.common.jsonld) for the complete context):

```json
{
  "@context": {
    "CIP100": "https://github.com/cardano-foundation/CIPs/blob/master/CIP-0100/README.md#",
    "CIP116": "https://github.com/cardano-foundation/CIPs/blob/master/CIP-0116/README.md#",
    "CIP169": "https://github.com/cardano-foundation/CIPs/blob/master/CIP-0169/README.md#",
    "body": {
      "@id": "CIP100:body",
      "@context": {
        "onChain": {
          "@id": "CIP169:onChain",
          "@context": {
            "tag": "CIP116:tag",
            "deposit": "CIP116:deposit",
            "reward_account": "CIP116:reward_account",
            "gov_action": { "@id": "CIP116:gov_action", "@context": { "...": "..." } }
          }
        }
      }
    }
  }
}
```

> [!NOTE]
> This CIP uses `CIP169` as the namespace identifier for the `onChain` property itself, while every property *inside* `onChain` lives in the `CIP116` namespace.

#### Structure

The `onChain` property **MUST** conform to one of the [CIP-0116][] Conway-era governance types listed below.
Field names and discriminator values follow CIP-0116 verbatim — that is,
snake_case property names (e.g. `reward_account`, `gov_action`, `gov_action_id`) and a `tag` discriminator carrying snake_case enum values (e.g. `treasury_withdrawals_action`, `register_drep`).
Inner certificate/governance-action variants are discriminated by their own `tag` field per CIP-0116.

> [!WARNING]
> The `anchor` property **MUST** be omitted from any CIP-0116 object whose `anchor` points to *this* metadata document. Including such an `anchor` would create a circular dependency, and it is not part of the on-chain effect being verified.
> This applies to:
> - `ProposalProcedure.anchor`
> - The inner `VotingProcedure.anchor` (when present)
> - `register_drep`, `update_drep`, and `resign_committee_cold` certificate `anchor` fields
>
> **Exception:** `Constitution.anchor` (inside `new_constitution` actions) is **retained**. That anchor points to the constitution document itself — a separate artifact from the governance metadata — so it is part of the on-chain effect and must be bound into the signed body.

##### Supported Types

**For Governance Actions:**

The `onChain` property conforms to the [CIP-0116][] `ProposalProcedure` type (without `anchor`),
whose `gov_action` field's `tag` is one of the Conway-era governance action types:

- `info_action`
- `parameter_change_action`
- `hard_fork_initiation_action`
- `treasury_withdrawals_action`
- `no_confidence`
- `update_committee`
- `new_constitution`

See [CIP-0116 cardano-conway.json](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0116/cardano-conway.json) for complete type definitions.

**For Votes:**

The `onChain` property conforms to the [CIP-0116][] `VotingProcedures` type — a map of `Voter` → `GovActionId` → `VotingProcedure` — with each inner `VotingProcedure`'s `anchor` omitted. Reusing the existing CIP-0116 container naturally binds the metadata to the (voter, action, vote) tuple(s) being attested without introducing a CIP-0169-specific wrapper type.

**For DRep Registration:**

The `onChain` property conforms to the [CIP-0116][] `register_drep` certificate (without `anchor`).

**For DRep Update:**

The `onChain` property conforms to the [CIP-0116][] `update_drep` certificate (without `anchor`).

**For Committee Cold Credential Resignation:**

The `onChain` property conforms to the [CIP-0116][] `resign_committee_cold` certificate (without `anchor`).

### Verification Process

Tools **SHOULD** implement the following verification when processing governance actions:

1. **Parse On-Chain Data**: Extract the on-chain data which the metadata is attached to
2. **Parse Metadata**: Retrieve and parse the governance metadata
3. **Author Signature Check**: Validate the author signatures are all correct
4. **Compare**: Verify that `body.onChain` matches the actual on-chain effect
5. **Alert**: If there are invalid author signatures and/or the `onChain` does not match, warn the user

### Examples

Please see [examples/](./examples/).

### Validation

The schema uses JSON Schema 2020-12 and references the CIP-0116 Conway domain types.
Validate an instance with [ajv-cli](https://github.com/ajv-validator/ajv-cli):

```sh
ajv validate --spec=draft2020 \
  -s cip-0169.common.schema.json \
  -r ../CIP-0116/cardano-conway.json \
  -d examples/<file>.json \
  --all-errors --strict=false
```

`-r` registers the referenced CIP-0116 schema so `$ref`s resolve offline.
`--strict=false` allows the OpenAPI-style `discriminator` keyword (advisory, not enforced).

## Rationale

By including the on-chain effects within the signed metadata body using the `onChain` property.
Metadata is bound to specific on-chain effects,
with author signature cryptographically locking it in.
This makes any metadata replay attacks, machine detectable.
This allows governance tools to automatically verify this for voters.

### Why Extend CIP-100?

[CIP-100][] provides the base structure for governance metadata.
This extension adds security-critical information while maintaining backward compatibility.

### Why Use CIP-0116 Encoding?

[CIP-0116][] provides standardized JSON encoding for Cardano domain types.

### Why Exclude the Self-Referential Anchor?

`ProposalProcedure`, `VotingProcedure`, and the DRep / committee resignation certificates each carry an `anchor` whose URL and hash point at *this* metadata document. Embedding that anchor inside the metadata it describes would create a circular dependency — the document would have to be hashed before it could be assembled. It also adds nothing to verification: the verifier already has the document in hand, so a pointer to it is redundant.

These self-referential anchors are therefore excluded from the `onChain` encoding. All other CIP-0116 properties — including anchors that point to *other* artifacts — are retained.

The notable example is `Constitution.anchor` inside a `new_constitution` action: it points to the constitution document, which is a separate artifact from the governance metadata, and is itself part of the on-chain effect being voted on. That anchor is kept as-is.

## Open Questions

- Whether downstream metadata CIPs (CIP-108, CIP-119, CIP-136) should `require` `onChain` once tooling adopts it, or keep it optional indefinitely. Making it required is a hard backward-compatibility break and probably best deferred.

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
[CIP-0116]: https://github.com/cardano-foundation/CIPs/blob/master/CIP-0116/README.md
[CC-BY-4.0]: https://creativecommons.org/licenses/by/4.0/legalcode
