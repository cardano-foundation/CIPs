---
CIP: 175
Title: Stake Pool Hot Credentials
Category: Ledger
Status: Proposed
Authors:
    - Ryan Wiley <rian222@gmail.com>
Implementors: []
Discussions:
    - CIP-0151: https://github.com/cardano-foundation/CIPs/pull/999
    - Original PR: https://github.com/cardano-foundation/CIPs/pull/1140
Created: 2026-01-22
License: CC-BY-4.0
---

## Abstract

Stake Pool Operators (SPOs) currently sign on-chain governance votes with pool
cold keys. This CIP introduces new on-chain certificates that let a pool cold
key authorize a hot credential for a stake pool. For
`StakePoolVoter poolId`, the ledger accepts either:

- the pool cold key witness, or
- a witness that satisfies the currently authorized hot credential.

Hot credentials are defined as `Credential` values (key hash or
script hash), so native and Plutus script voting paths are supported.
The proposal preserves the existing `StakePoolVoter` model from CIP-1694 and
requires a future hard fork for activation.

## Motivation: Why is this CIP necessary?

CIP-1694 gave SPOs an on-chain voting role, but cold-key-only operation is
high-friction and increases operational risk because cold keys are meant to
remain offline.

Authorization for consensus-critical voting must be ledger-visible and
ledger-validated. Existing Calidus keys from CIP-0151 rely on transaction
metadata, but is not the right substrate for on-chain voting.
A certificate-based design provides explicit state transitions,
deterministic validation, and consistent tooling semantics.

This CIP enables day-to-day governance operation through authorized hot
credentials while preserving cold-key voting as it already works today.

## Specification

### Terminology

- **Pool cold key**: The Ed25519 key whose hash defines the Pool ID.
- **Pool ID**: The blake2b-224 hash of the pool cold verification key.
- **Hot credential**: A governance `Credential` authorized for a pool's
  governance voting role. It may be either a key hash credential or script hash
  credential.
- **Hot authorization map**: Ledger state map
  `poolGovHotCreds : Map PoolId Credential`.
- **Vote source**: Authorization source for a recorded SPO vote:
  `Cold | Hot`.

### Certificate Semantics

This CIP introduces two new stake-pool governance certificates:

- `AuthStakePoolHotKey(poolId, hotCred)`
- `ResignStakePoolHotKey(poolId)`

### Certificate Validation Rules

For both certificates:

1. `poolId` MUST identify a currently registered pool.
2. The transaction MUST include a valid witness by that pool's cold key.

Additional transaction restrictions to prevent ambiguity:

1. A transaction MUST NOT include more than one of these certificates for the
   same `poolId`. If it does, the transaction is invalid.
2. A transaction MUST NOT include any SPO governance vote for `poolId` if it
   also includes one of these certificates for `poolId`. If it does, the
   transaction is invalid.

`ResignStakePoolHotKey(poolId)` is valid even if no hot credential is currently
authorized for `poolId`; it is a no-op in that case.

### Ledger State Extension

Introduce:

```
poolGovHotCreds : Map PoolId Credential
```

State transitions:

- `AuthStakePoolHotKey(poolId, hotCred)` sets
  `poolGovHotCreds[poolId] = hotCred` (overwrite allowed).
- `ResignStakePoolHotKey(poolId)` removes `poolId` from the map if present.

No uniqueness constraint is imposed on `hotCred`. The same hot credential MAY be
authorized for multiple pools.

Pool retirement lifecycle:

- If a pool has a retirement certificate scheduled but not yet enacted, its hot
  credential remains valid.
- When retirement is enacted, the ledger clears that pool's
  `poolGovHotCreds` entry.

### Governance Vote Authorization Change

For each vote with `Voter = StakePoolVoter poolId`, authorization succeeds if
either of the following holds:

1. The transaction includes a valid witness by the pool cold key for `poolId`.
2. `poolGovHotCreds[poolId] = hotCred` exists and transaction witnesses satisfy
   `hotCred`.

Hot credential satisfaction rules:

- If `hotCred` is a key credential, the corresponding vkey witness is required.
- If `hotCred` is a script credential, a valid governance voting script witness
  is required under existing Conway voting-script rules for
  `StakePoolVoter poolId`.
- Both native scripts and Plutus scripts are supported.

All other vote semantics (vote options, anchors, role structure, timing windows,
and tallying model) remain as defined by CIP-1694 unless explicitly modified by
this CIP.

### Cold Key Override

For each `(govActionId, poolId)` vote slot, the ledger records both vote value
and `VoteSource` (`Cold` or `Hot`).

Overwrite rules:

1. A `Cold` vote overwrites any existing `Hot` vote for the same
   `(govActionId, poolId)`.
2. A `Hot` vote MUST NOT overwrite an existing `Cold` vote for the same
   `(govActionId, poolId)`.
3. A later `Cold` vote MAY overwrite an earlier `Cold` vote.
4. A later `Hot` vote MAY overwrite an earlier `Hot` vote, unless a `Cold` vote
   has already been recorded for that pair.

Effectively, once any cold-authorized vote exists for a given
`(govActionId, poolId)`, that pair is locked against hot-authorized overwrites.
This applies regardless of transaction or block ordering history.

### Ledger Rule Integration (Conway)

This CIP integrates at existing Conway rule boundaries:

- **`UTXO`** applies certificate-driven updates to `poolGovHotCreds` and
  enforces transaction-level constraints for these certificates.
- **`UTXOW`** extends SPO vote witness authorization checks to allow either
  pool cold or authorized hot credential satisfaction.
- **`GOV`** (vote state handling) records `VoteSource` for stake-pool votes and
  applies the cold-over-hot overwrite rules.

The proposal does not require new voter types and keeps `StakePoolVoter` as the
canonical SPO governance voter identity.

## Rationale: How does this CIP achieve its goals?

- **Certificates, not metadata**: Governance authorization must be explicit
  ledger state with deterministic rule evaluation.
- **Operational security**: Day-to-day activity uses hot credentials while cold
  keys remain available for high-assurance override and recovery.
- **Compatibility**: Cold-key voting and `StakePoolVoter` semantics remain
  intact.
- **Future-proofing**: Credential-based payload supports key and script custody
  models without a second hard-fork change.
- **MPO support**: Explicitly permitting hot credential reuse across pools
  supports multi-pool operational workflows.

### Backward Compatibility

- Existing cold-key SPO voting remains valid and unchanged.
- `StakePoolVoter poolId` remains the SPO voter representation.
- This CIP introduces no dependency on transaction metadata.
- CIP-0151 remains compatible as an off-chain identity/authentication mechanism.
  Operators MAY reuse the same underlying key material for both systems, but it
  is not required by consensus.

### Security Considerations

- **Hot credential compromise near deadline**:
  Cold key override gives SPOs a failsafe in case their hot keys are suspected
  to be compromised.  Additionally, large stake pool groups can mitigate this
  risk further by choosing to use a multisig hot credential.
- **Blast radius for shared hot credentials across multiple pools**:
  This is allowed by design. Operators should consider script credentials (for
  example multisig and timelock designs) to reduce single-key compromise risk.

## Path to Active

### Acceptance Criteria

- [ ] Ledger implementation merged in at least one node client.
- [ ] Ledger implementation includes:
      `AuthStakePoolHotKey`/`ResignStakePoolHotKey`,
      `poolGovHotCreds` state management, SPO vote authorization extension, and
      cold-over-hot precedence behavior.
- [ ] Compatible tooling available to create/submit new certificates and submit
      SPO votes using key or script hot credentials.
- [ ] Integrated in a hard fork release.
- [ ] Implementation present within block producing nodes used by 80%+ of stake.

### Implementation Plan

- Add certificate constructors and semantic validation for pool hot
  authorization/resignation.
- Add and maintain `poolGovHotCreds` in Conway ledger state.
- Extend SPO vote witness verification for authorized hot credentials
  (key and script forms).
- Implement vote-source tracking and cold-over-hot overwrite behavior.
- Update tooling and documentation for certificate flows and hot credential
  voting.
- Deploy in a future hard fork.

## References

- [CIP-1694: On-chain decentralized governance](https://github.com/cardano-foundation/CIPs/tree/master/CIP-1694)
- [CIP-0151: On-chain registration for stake pools (Calidus keys)](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0151)
- [Cardano CLI governance vote submission](https://developers.cardano.org/docs/get-started/cardano-cli/governance/submit-votes/)

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
