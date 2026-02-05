---
CIP: 175
Title: SPO Governance Voting with Calidus Keys
Category: Ledger
Status: Proposed
Authors:
    - Ryan Wiley <rian222@gmail.com>
Implementors: []
Discussions:
    - CIP-0151 original pull request: https://github.com/cardano-foundation/CIPs/pull/999
    - add SPO governance voting: https://github.com/cardano-foundation/CIPs/pull/1140
Created: 2026-01-22
License: CC-BY-4.0
---

## Abstract

Stake Pool Operators (SPOs) must currently sign on-chain governance votes with
pool cold keys. This CIP enables an alternate, authorized "hot" key for SPO
voting by reusing the Calidus key registration defined in CIP-0151. The ledger
will accept SPO votes signed by either the pool cold key (status quo) or the
currently active Calidus key for that pool, as determined by the highest-nonce
CIP-0151 registration metadata. No new certificate type is introduced. Instead,
ledger state is extended to index validated CIP-0151 registrations (scope: stake
pool), and the governance witness checks are updated to admit the Calidus key as
an additional authorized signer. This change reduces operational risk by keeping
cold keys offline while preserving backward compatibility and the existing vote
format defined in CIP-1694. The proposal is ledger-only and requires a future
hard fork for activation.

## Motivation: Why is this CIP necessary?

CIP-1694 assigns SPOs an on-chain voting role in governance actions, but current
workflow requires pool cold keys to sign vote transactions. Cold keys are
intended to remain offline. Repeated access increases risk of loss or compromise
and adds operational friction. Meanwhile, CIP-0151 already standardizes a
verifiable, on-chain registration of Calidus keys for stake pools, enabling an
SPO-controlled hot key for routine authentication. Reusing that registration as
the authorization source for on-chain voting aligns governance participation
with established security practices and existing ecosystem tooling, while
preserving the ability to vote with cold keys as a fallback.

## Specification

### Terminology

- **Pool cold key**: The Ed25519 key whose hash defines the Pool ID.
- **Pool ID**: The blake2b-224 hash of the pool cold verification key.
- **Calidus key**: The Ed25519 public key registered in CIP-0151 metadata for a
  stake pool (registration payload field 7).
- **Active Calidus key**: The Calidus key from the valid CIP-0151 registration
  with the highest nonce for a given pool. A 32-byte zero key indicates
  revocation (no active key).

### Data Source: CIP-0151 Registration Metadata

The ledger recognizes CIP-0151 registrations recorded under metadata label
`867`, version `2`, with **Scope** = stake pool (`[1, poolID]`). The following
fields are required (as per CIP-0151):

- Version (0) = 2
- Registration Payload (1)
- Registration Witness (2)

Within the Registration Payload, the following fields are required:

- Scope (1)
- Feature Set (2)
- Validation Method (3)
- Nonce (4)

The optional Calidus Key (7) is used as the candidate key to authorize SPO
voting.

### Validation of CIP-0151 Registrations (Ledger Rule Additions)

To prevent unauthorized key claims, the ledger MUST validate CIP-0151
registrations before they can influence voting authorization. A registration is
**valid** for ledger purposes when all of the following hold:

1. The metadata conforms to CIP-0151 version 2 and scope = stake pool.
2. The Registration Payload is CBOR-encoded exactly as specified by CIP-0151.
3. The Registration Witness verifies the payload using a pool cold key whose
   hash equals the specified Pool ID.
4. The Validation Method is one of:
   - **Method 0 (Ed25519 Key Signature)**, or
   - **Method 2 (CIP-0008 Signature)**

Registrations using unsupported methods (including Method 1) are ignored for
on-chain voting authorization.

#### Transaction-level Restrictions

For consensus determinism and to simplify validation, the following additional
constraints MUST hold for any transaction containing CIP-0151 stake-pool
registrations:

1. A transaction MUST NOT contain more than one CIP-0151 registration for the
   same Pool ID. If multiple registrations for the same pool appear, the
   transaction is invalid.
2. A transaction MUST NOT contain both a CIP-0151 stake-pool registration and
   a governance vote by that same pool. If both appear, the transaction is
   invalid.

> [!NOTE]
> Validation Method 1 (Beacon/Reference Token) is intentionally excluded from
> on-chain voting authorization in this CIP. It relies on an additional token
> reference and policy constraints that are not currently validated by the
> ledger for stake pools. Supporting Method 1 would require new on-chain
> constraints tying the beacon policy to the pool cold key, which is outside
> the scope of this proposal.

#### Signature Payload Derivation (Strict)

Let `payload` be the CIP-0151 Registration Payload object (the map at key `1`
under metadata label `867`), encoded as CBOR with map keys in **ascending
numeric order**.

Define:

- `payload_cbor` = CBOR encoding of `payload` (byte string)
- `payload_hex` = ASCII byte string of lowercase hex digits encoding
  `payload_cbor`, with **no prefix**
- `sig_payload` = `blake2b-256(payload_hex)`

All signature verification for stake-pool registrations in this CIP uses
`sig_payload`.

#### Method 0 (Ed25519 Key Signature) Witness Rules

For `validation.method = 0`, the Registration Witness Array MUST contain a
signature from the pool cold key that matches the Pool ID in the registration
scope. The witness may be either:

- **v1_witness**: `[pubkey, signature]`, or
- **v2_witness**: `{ 0: uint, 1: pubkey, 2: signature }`

Where:

- `pubkey` is the Ed25519 cold verification key (32 bytes).
- `signature` is the Ed25519 signature (64 bytes) over `sig_payload`.
- `blake2b-224(pubkey)` equals the Pool ID in the registration scope.

If multiple witnesses are present, at least one MUST satisfy these conditions.

#### Method 2 (CIP-0008 / COSE) Witness Rules

For `validation.method = 2`, the Registration Witness Array MUST contain a
`COSE_Witness` as defined in CIP-0151 v2 CDDL:

```
COSE_Witness = {
  ? 0 : uint,                ; Witness Type Identifier (optional or 0)
    1 : COSE_Headers,        ; COSE Header Object
    2 : COSE_Sign1_Payload,  ; COSE Signature Payload
}
```

Validation MUST proceed as follows:

1. Extract the Ed25519 public key from `COSE_Headers[-2]`. Its
   `blake2b-224` hash MUST equal the Pool ID in the registration scope.
2. Parse `COSE_Sign1_Payload = [protected, hashed, payload, signature]` with
   lengths exactly as specified by CIP-0151 v2 CDDL.
3. The `hashed` flag MUST be `0` (false). The `payload` field MUST equal
   `sig_payload`.
4. Verify the COSE signature according to CIP-0008 using:
   - Ed25519 verification with the public key from step 1.
   - `protected` as the COSE protected header bytes.
   - `external_aad` set to `h''` (empty byte string).
   - If the COSE algorithm header is present, it MUST identify Ed25519.

If multiple witnesses are present, at least one MUST satisfy these conditions.

> [!NOTE]
> The `hashed` flag MUST be `0` to prevent ambiguous interpretation between
> CIP-0008's optional pre-hashing and CIP-0151's required `sig_payload`
> derivation. This ensures all implementations verify the same byte sequence.

### Ledger Rule Integration (Conway)

This CIP integrates at the Conway ledger rule layer and uses existing rule
boundaries:

- **ConwayLEDGER** (module `Cardano.Ledger.Conway.Rules.Ledger`): unchanged
  sequencing, but the subordinate `UTXOW`/`UTXO` behavior is extended as
  described below.
- **UTXOW** (rule `"UTXOW"` in `Cardano.Ledger.Conway.Rules`): extends witness
  verification for SPO votes by expanding the required key hash set.
- **UTXO** (rule `"UTXO"` in `Cardano.Ledger.Conway.Rules`): updates the
  `calidusKeys` map from validated CIP-0151 metadata found in transaction
  auxiliary data.

Within `Cardano.Ledger.Conway.UTxO`, `getConwayWitsVKeyNeeded` is the helper
used to determine required key witnesses, including governance voters. This CIP
extends `getConwayWitsVKeyNeeded` so that for each stake pool voter it admits
either:

- the pool cold key hash (status quo), or
- the hash of the active Calidus key for that pool.

### Ledger State Extension

Introduce a new ledger state mapping:

```
calidusKeys : Map PoolId (Nonce, Maybe CalidusKey)
```

Where `CalidusKey` is a 32-byte Ed25519 public key. The map is updated during
transaction validation by scanning auxiliary data for CIP-0151 registrations
that pass the validation criteria above. For Conway, this map is stored in
ledger state and updated in the `ConwayUTXO` transition so it is available to
`ConwayUTXOW` for witness checks. Per the transaction-level restrictions, a
transaction that contains both a stake-pool registration and a vote by the same
pool is invalid and thus does not update `calidusKeys`.

Update rule:

- If a valid registration is found for pool `p` with nonce `n`:
  - If `n` is greater than the stored nonce for `p`, update `calidusKeys[p]` to
    `(n, k)` where `k` is the Calidus key (or `None` if the key is 32 zero bytes).
  - If `n` is less than or equal to the stored nonce, ignore the registration.

This map is a derived index of existing on-chain metadata and does not introduce
new certificate types.

### Governance Vote Authorization Change

For each SPO vote in a transaction, the ledger currently requires a signature
from the pool cold key (via the pool key hash in the vote credential). This CIP
extends the authorization rule as follows:

Define the authorized signer set for a pool `p` as:

```
AuthKeys(p) = { poolId(p) } ∪ { hash(calidusKey(p)) if active }
```

A vote by an SPO for pool `p` is authorized if the transaction witness set
contains a vkey witness whose key hash is in `AuthKeys(p)`.

All other vote semantics (vote format, anchors, role definitions, and tallying)
remain unchanged.

### Versioning

This CIP depends on CIP-0151 version 2 and ignores registrations with other
versions for ledger authorization. If CIP-0151 is revised with a new version,
this CIP must be updated or superseded to recognize it.

## Rationale: How does this CIP achieve its goals?

- **Security**: Allows routine voting with a hot key while keeping cold keys
  offline, reducing exposure and operational risk.
- **Compatibility**: Retains cold-key voting as a fallback and does not alter
  the on-chain vote structure defined in CIP-1694.
- **Reuse of existing standards**: Leverages CIP-0151 metadata to avoid
  introducing a new certificate type.
- **Operational simplicity**: Key rotation and revocation follow the established
  CIP-0151 nonce and zero-key semantics.

### Backward Compatibility

Existing transactions and wallets remain valid. Pools without a Calidus key
continue to vote with cold keys. Tools may optionally implement Calidus signing
without disrupting current governance flows.

## Path to Active

### Acceptance Criteria

- [ ] Ledger implementation merged in at least one node client.
- [ ] Compatible tooling available to register Calidus keys and submit SPO
      votes signed by Calidus keys.
- [ ] Integrated in a hard fork release.
- [ ] Implementation present within block producing nodes used by 80%+ of stake.

### Implementation Plan

- Update ledger rules to validate CIP-0151 registrations and maintain the
  `calidusKeys` mapping.
- Extend SPO vote witness verification to accept the active Calidus key.
- Update tooling and documentation to support Calidus vote signing.
- Deploy in a future hard fork.

## References

- [CIP-1694: On-chain decentralized governance](https://github.com/cardano-foundation/CIPs/tree/master/CIP-1694)
- [CIP-0151: On-chain registration for stake pools (Calidus keys)](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0151)
- [CIP-0008: Message signing](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0008)
- [Cardano CLI governance vote submission](https://developers.cardano.org/docs/get-started/cardano-cli/governance/submit-votes/)

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
