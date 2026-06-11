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
cold keys. This CIP introduces a new on-chain certificate that lets a pool cold
key authorize a hot credential for a stake pool. It also makes SPO vote
authorization explicit in the voter representation:

- `StakePoolVoter poolId Nothing` requires the pool cold key witness.
- `StakePoolVoter poolId (Just hotCred)` requires witnesses that satisfy
  `hotCred`, and the ledger verifies that `hotCred` matches the pool's
  currently authorized hot credential.

Hot credentials are defined as `Credential` values (key hash or
script hash), so native and Plutus script voting paths are supported. For each
`(govActionId, poolId)`, the ledger only needs to track the latest SPO vote and
whether it was cast as `Cold` or `Hot`. The proposal requires a future hard
fork for activation.

## Motivation: Why is this CIP necessary?

CIP-1694 gave SPOs an on-chain voting role, but cold-key-only operation is
high-friction and increases operational risk because cold keys are meant to
remain offline.

Authorization for consensus-critical voting must be ledger-visible and
ledger-validated. Existing Calidus keys from CIP-0151 rely on transaction
metadata, but metadata is not the right substrate for on-chain voting.
A certificate-based design provides explicit state transitions,
deterministic validation, and consistent tooling semantics.

This CIP enables day-to-day governance operation through authorized hot
credentials while preserving cold-key voting. It does so with explicit voter
contents rather than by inferring authorization mode indirectly during witness
validation.

## Specification

### Terminology

- **Pool cold key**: The Ed25519 key whose hash defines the Pool ID.
- **Pool ID**: The blake2b-224 hash of the pool cold verification key.
- **Hot credential**: A governance `Credential` authorized for a pool's
  governance voting role. It may be either a key hash credential or script hash
  credential.
- **SPO voter**: `StakePoolVoter !(KeyHash 'StakePool) (Maybe (Credential Hot))`.
- **Cold vote**: An SPO vote with `StakePoolVoter poolId Nothing`.
- **Hot vote**: An SPO vote with `StakePoolVoter poolId (Just hotCred)`.
- **Hot authorization map**: Ledger state map
  `poolGovHotCreds : Map PoolId Credential`.
- **Vote source**: Authorization source for a recorded SPO vote:
  `Cold | Hot`.

### Certificate Semantics

This CIP introduces one new stake-pool governance certificate:

- `AssignStakePoolHotCredential(poolId, hotCredOpt)`

`hotCredOpt` semantics:

- If `hotCredOpt = hotCred` (a `Credential`), the pool's hot credential is
  set to `hotCred` (overwrite allowed).
- If `hotCredOpt = null`, any existing hot credential for `poolId` is revoked.
  If none exists, this is a valid no-op.

### Certificate CDDL

```cddl
; Numeric certificate tag allocation is TBD in Ledger CDDL integration.
assign_stake_pool_hot_credential_tag = uint

assign_stake_pool_hot_credential_cert = [
  assign_stake_pool_hot_credential_tag,
  pool_id : pool_keyhash,
  hot_credential : null / credential
]
```

### Certificate Validation Rules

For `AssignStakePoolHotCredential(poolId, hotCredOpt)`:

1. `poolId` MUST identify a currently registered pool.
2. The transaction MUST include a valid witness by that pool's cold key.
3. If multiple `AssignStakePoolHotCredential` certificates for the same
   `poolId` appear in one transaction, they are processed in transaction order;
   the last one determines the final hot credential state for that `poolId`.

### Ledger State Extension

Introduce:

```
poolGovHotCreds : Map PoolId Credential
```

State transitions:

- `AssignStakePoolHotCredential(poolId, hotCredOpt)` with
  `hotCredOpt = hotCred` sets `poolGovHotCreds[poolId] = hotCred`
  (overwrite allowed).
- `AssignStakePoolHotCredential(poolId, hotCredOpt)` with
  `hotCredOpt = null` removes `poolId` from the map if present (otherwise
  no-op).

No uniqueness constraint is imposed on `hotCred`. The same hot credential MAY be
authorized for multiple pools.

Pool retirement lifecycle:

- If a pool has a retirement certificate scheduled but not yet enacted, its hot
  credential remains valid.
- When retirement is enacted, the ledger clears that pool's
  `poolGovHotCreds` entry.

### SPO Voter Representation and Authorization

This CIP changes the SPO voter representation to:

```haskell
StakePoolVoter !(KeyHash 'StakePool) (Maybe (Credential Hot))
```

Authorization semantics:

1. `StakePoolVoter poolId Nothing` is a cold-authorized SPO vote. The
   transaction MUST include a valid witness by the pool cold key for `poolId`.
2. `StakePoolVoter poolId (Just hotCred)` is a hot-authorized SPO vote. The
   transaction MUST include witnesses that satisfy `hotCred`, and the ledger
   MUST verify that `poolGovHotCreds[poolId] = hotCred`.

Hot credential satisfaction rules:

- If `hotCred` is a key credential, the corresponding vkey witness is required.
- If `hotCred` is a script credential, a valid governance voting script witness
  is required under existing governance voting-script rules for
  `StakePoolVoter poolId (Just hotCred)`.
- Both native scripts and Plutus scripts are supported.

All other vote semantics (vote options, anchors, role structure, timing windows,
and tallying model) remain as defined by CIP-1694 unless explicitly modified by
this CIP.

### Vote Type and Overwrite Rules

For each active `(govActionId, poolId)` vote slot, the ledger records only the
latest SPO vote together with its `VoteSource` (`Cold` or `Hot`). Historical
overwritten SPO votes do not need to be retained.

Overwrite rules:

1. A `Cold` vote MAY replace the current vote (`Cold` or `Hot`) for the same
   `(govActionId, poolId)`.
2. A `Hot` vote MAY replace the current `Hot` vote for the same
   `(govActionId, poolId)`.
3. A `Hot` vote MUST NOT replace the current `Cold` vote for the same
   `(govActionId, poolId)`.

Effectively, once any cold-authorized vote exists for a given
`(govActionId, poolId)`, that pair is locked against hot-authorized overwrites.

### Authorization-Change Vote Invalidation

If `AssignStakePoolHotCredential(poolId, hotCredOpt)` results in an actual
authorization-state change for `poolId`, the ledger MUST clear the current SPO
votes for that `poolId` across still-active governance actions whose recorded
`VoteSource` is `Hot`.

If `AssignStakePoolHotCredential(poolId, hotCredOpt)` does not change the
resulting authorization state for `poolId`, no vote invalidation occurs.

Current `Cold` votes remain valid.

### Ledger Rule Integration

This CIP integrates at existing governance ledger rule boundaries:

- **`UTXO`** applies certificate-driven updates to `poolGovHotCreds` and
  enforces transaction-level constraints for this certificate type.
- **`UTXOW`** validates the explicit SPO voter form, requiring either the pool
  cold witness for `StakePoolVoter poolId Nothing` or witnesses satisfying
  `hotCred` plus `poolGovHotCreds[poolId] = hotCred` for
  `StakePoolVoter poolId (Just hotCred)`.
- **`GOV`** (vote state handling) records `VoteSource` for stake-pool votes and
  stores only the latest current vote per `(govActionId, poolId)`, applying
  cold/hot overwrite rules plus hot-vote invalidation on actual
  authorization-state changes.

The proposal does not introduce a new governance role. It extends
`StakePoolVoter` so the SPO vote explicitly carries whether it is using cold
authorization or a specific hot credential.

## Rationale: How does this CIP achieve its goals?

- **Certificates, not metadata**: Governance authorization must be explicit
  ledger state with deterministic rule evaluation.
- **Deterministic vote validation**: The SPO vote itself states whether it uses
  cold authorization or a specific hot credential, and the ledger checks that
  claim directly.
- **Operational security**: Day-to-day activity uses hot credentials while cold
  keys remain available for high-assurance override and recovery.
- **Compatibility**: The SPO governance role remains `StakePoolVoter`, while
  its payload is extended to carry hot-credential information explicitly.
- **Future-proofing**: Credential-based payload supports key and script custody
  models without a second hard-fork change.
- **MPO support**: Explicitly permitting hot credential reuse across pools
  supports multi-pool operational workflows.
- **Simplicity**: A single certificate with nullable payload reduces complexity
  in specification, validation, and tooling, and the ledger only needs the
  latest vote and its type.

### Backward Compatibility

- Existing cold-key SPO voting remains valid through
  `StakePoolVoter poolId Nothing`.
- This CIP extends the SPO voter payload to include
  `Maybe (Credential Hot)` explicitly.
- This CIP introduces no dependency on transaction metadata.
- CIP-0151 remains compatible as an off-chain identity/authentication mechanism.
  Operators MAY reuse the same underlying key material for both systems, but it
  is not required by consensus.

### Security Considerations

- **Hot credential compromise near deadline**:
  If hot keys are suspected to be compromised, changing or revoking the
  authorized hot credential immediately invalidates current hot-authorized SPO
  votes for that pool on still-active governance actions, while current
  cold-authorized votes remain valid. Operators can then recast under current
  authorization (including with the cold key). Additionally, large stake pool
  groups can mitigate this risk further by choosing to use a multisig hot
  credential.
- **Blast radius for shared hot credentials across multiple pools**:
  This is allowed by design. Operators should consider script credentials (for
  example multisig and timelock designs) to reduce single-key compromise risk.
- **Intentional delegation via shared or third-party hot credentials**:
  A pool cold key can authorize any `Credential`, including one controlled by a
  different operator or reused across multiple pools. Votes cast as
  `StakePoolVoter poolId (Just hotCred)` then count for each pool that has
  authorized that `hotCred`. This representative behavior is an intentional
  capability, not a validation flaw, but it can concentrate SPO voting
  influence. If that outcome is undesirable, pool operators can revoke or
  replace the hot credential and, for the current governance action, reassert
  intent with a cold-authorized vote.

## Path to Active

### Acceptance Criteria

- [ ] Ledger implementation merged in at least one node client.
- [ ] Ledger implementation includes:
      `AssignStakePoolHotCredential`,
      `poolGovHotCreds` state management, the explicit SPO voter
      representation, latest-vote-plus-type tracking, and cold/hot overwrite
      plus authorization-change invalidation behavior.
- [ ] Compatible tooling available to create/submit new certificates and submit
      SPO votes using either cold authorization or key/script hot credentials.
- [ ] Integrated in a hard fork release.
- [ ] Implementation present within block producing nodes used by 80%+ of stake.

### Implementation Plan

- Add certificate constructors and semantic validation for pool hot
  credential assignment/revocation via a nullable payload.
- Add and maintain `poolGovHotCreds` in ledger state.
- Extend the SPO voter representation to carry `Maybe (Credential Hot)` and
  validate explicit cold/hot vote authorization.
- Implement latest-vote-plus-type tracking, cold/hot overwrite behavior, and
  hot-vote invalidation on authorization-state changes.
- Update tooling and documentation for certificate flows and hot credential
  voting.
- Deploy in a future hard fork.

## References

- [CIP-1694: On-chain decentralized governance](https://github.com/cardano-foundation/CIPs/tree/master/CIP-1694)
- [CIP-0151: On-chain registration for stake pools (Calidus keys)](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0151)
- [Cardano CLI governance vote submission](https://developers.cardano.org/docs/get-started/cardano-cli/governance/submit-votes/)

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
