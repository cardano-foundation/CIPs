---
CIP: "?"
Title: Web-Wallet Bridge - Encryption Keys
Category: Wallets
Status: Proposed
Authors:
    - Thomas Kammerlocher <thomas.kammerlocher@cardanofoundation.org>
    - Mateusz Czeladka <mateusz.czeladka@cardanofoundation.org>
Implementors: []
Discussions:
    - Original PR: https://github.com/cardano-foundation/CIPs/pull/1309
Created: 2026-10-28
License: CC-BY-4.0
---

## Abstract

[CIP-30] lets a dApp ask a wallet to **sign** with the user's keys, but not to use a key for
**encryption**. Every asymmetric encryption scheme a dApp might use — confidential amounts,
encrypted messages, encrypted metadata — needs the same step on the recipient's side: an
elliptic-curve Diffie–Hellman (ECDH) computation between a long-lived private key held by the
recipient and an ephemeral public key chosen by the sender.

This proposal defines a [CIP-30] extension that gives dApps that step without ever disclosing a
private key. A wallet derives, from its existing seed, a separate **encryption key for each
registered purpose**. With an explicit, separate and revocable permission per purpose, a dApp can
read the public key and ask the wallet to compute ECDH shared secrets against ephemeral keys
taken from specific on-chain references. The wallet exposes no export call and no general
decryption call. Purposes and curves are pluggable: this CIP registers the
**confidential-viewing** purpose with the **Jubjub** curve, used today by confidential notes on
[CIP-113] programmable tokens, and defines how further purposes and curves are added.

## Motivation: Why is this CIP necessary?

### The missing primitive

Public-key encryption on elliptic curves follows one pattern (ECIES and its relatives):

1. The recipient holds a keypair `(sk, PK)` and publishes `PK`.
2. The sender picks an ephemeral scalar `e`, publishes `Epk = e·G` next to the ciphertext, and
   derives a symmetric key from the shared secret `S = e·PK`.
3. The recipient computes the same `S = sk·Epk` and decrypts.

Step 3 needs the recipient's private key. On Cardano that key should live in the user's wallet,
derived from the seed the user already backs up. [CIP-30] offers no way to use such a key, and
the alternatives are all unacceptable:

- **Exporting the private key to the dApp.** Any site that obtained it once could decrypt
  forever, and the user could neither see nor revoke that access.
- **Deriving a key from a signature** ("sign this message and we derive your key from it").
  Signatures are not secrets users know to protect, and a deterministic signature over a public
  constant can be requested again by any site.
- **Keeping the feature inside wallet UIs.** Every dApp would need wallet-specific integration,
  which defeats the purpose of a common bridge.

### Use cases

- **Confidential transfers.** This proposal comes directly out of ongoing work on confidential
  transfers for [CIP-113] programmable tokens. That work is a running prototype, being tested on
  Preview and Preprod and reviewed by the community. Its confidential notes hide amounts on chain
  and convey them to the recipient through ECDH with the recipient's **viewing key**. A dApp that
  displays confidential balances or opens received notes needs this step. With the `jubjub`
  profile, the viewing key reveals **incoming** amounts only. This purpose is specified here.
- **Encrypted messages and metadata (candidate purpose).** [CIP-83] encrypts transaction
  messages with a shared passphrase, which both parties must agree out of band, or a publicly
  known default. Encrypting to the recipient's public key removes the shared secret. This CIP does
  not specify that purpose yet, but its design must accommodate it.

### Stakeholders

Wallet implementors, dApp developers building on confidential assets or encrypted data, token
issuers with compliance requirements, and the auditors those issuers or users designate.

Following the precedent of [CIP-95], this is an additive, namespaced [CIP-30] extension and
changes no existing endpoint.

## Specification

The key words "MUST", "MUST NOT", "SHOULD", "SHOULD NOT" and "MAY" are to be interpreted as
described in [RFC 2119].

### Activation

A dApp requests this extension like any [CIP-30] extension:

```ts
const api = await cardano.{walletName}.enable({ extensions: [{ cip: ???? }] });
```

If the wallet enables it, `api.getExtensions()` MUST include `{ cip: ???? }` and the endpoints
below MUST be available under the namespace `api.cip????`.

> Until a CIP number is assigned, implementations MUST expose these endpoints only under
> `api.experimental.encryptionKeys`, as required by [CIP-30]'s
> [Experimental API](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0030#experimental-api),
> and MUST NOT list them in `getExtensions()`.

Enabling the extension grants **nothing** by itself. Every endpoint is also gated by a
[per-purpose permission](#permission).

### Concepts

- **Purpose:** what a key is used for, e.g. `confidential-viewing`. Each purpose has its own key,
  its own permission and its own rules (see [Purposes](#purposes)). Keys of different purposes
  are cryptographically independent, so granting one purpose never exposes another.
- **Algorithm profile:** the group in which the key lives, the encodings, and the validation
  rules for ephemeral keys (see [Algorithm Profiles](#algorithm-profiles)).
- **Generation:** a hardened index that versions a key, so it can be rotated.

### Data Types

#### HexString

A lowercase hexadecimal string with no `0x` prefix.

#### KeySelector

```ts
type KeySelector = {
  purpose: string;        // a registered purpose, e.g. "confidential-viewing"
  algorithm: string;      // an algorithm profile allowed for that purpose, e.g. "jubjub"
  accountIndex?: number;  // default 0
  generation?: number;    // default 0
};
```

`accountIndex` and `generation` MUST be integers in `[0, 2³¹)`.

#### PublicKeyInfo

```ts
type PublicKeyInfo = {
  purpose: string;
  algorithm: string;
  publicKeyHex: HexString; // encoded as defined by the algorithm profile
  accountIndex: number;
  generation: number;
  path: string;            // derivation path of the key material, e.g. "m/1852'/1815'/0'/6/0'"
};
```

#### EcdhRequest

```ts
type EcdhRequest = {
  ephemeralPublicKeyHex: HexString; // Epk, exactly as published by the sender
  ref: string;                      // where Epk was published; format defined by the purpose
};
```

Each ephemeral key is always passed **together with a reference to where it was published**.
This lets the wallet scope its answers (see [Purposes](#purposes)) and makes requests auditable.

### Key Derivation

All encryption keys derive from one new [CIP-1852] role. Role `6` is reserved for encryption
keys, in the same way [CIP-0105] added roles `3`–`5`:

```
m / 1852' / 1815' / account' / 6 / generation'
```

The 64-byte extended private key at this path is the **key material**. The scalar used by a
purpose is derived from it by the algorithm profile's mapping, **domain-separated by purpose,
algorithm and network**:

```
tag = "cip????/" ‖ purpose ‖ "/" ‖ algorithm ‖ "/net" ‖ networkId ‖ "/v1"
sk  = Map_profile( key_material, tag )
PK  = sk · G
```

`networkId` is the decimal value returned by [CIP-30] `getNetworkId()` (`0` for test networks,
`1` for mainnet). Different purposes, profiles or networks therefore yield independent keys from
the same path, and a key used on a test network is never the mainnet key.

- A key of this extension MUST be used only to compute ECDH shared secrets through this API.
  It MUST NOT be used to produce signatures or proofs whose form is `sk · P` for a point `P`
  derived from a message (for example BLS-style signatures), because `ecdh` would then act as a
  signing oracle.
- A key of this extension MUST NOT be, or be derivable from, a signing key or any signature the
  wallet produces on request.
- A wallet MUST derive `sk` per request, MUST erase it after use, and MUST NOT persist it.
- A wallet MUST NOT export the key material, or the extended private key of the role-`6` node,
  under any circumstances. The role level uses non-hardened derivation: with BIP32-Ed25519, a
  leaked child extended private key together with the account's public key reveals the account's
  private key.
- A wallet that cannot derive role `6` (hardware, multi-party, watch-only and similar wallets)
  MUST answer `Refused`. It MUST NOT substitute any other key.
- Accounts controlled by a script stake credential are out of scope.

### Algorithm Profiles

A wallet MUST reject an ephemeral key that fails its profile's validation rules **before** any
key material is derived or the user is prompted. Profile identifiers MUST match `[a-z0-9-]+`, so
that every `tag` decodes unambiguously.

| Profile | Point / secret encoding | Validation of `Epk` |
|---|---|---|
| `jubjub` | the `y` coordinate, 32 bytes big-endian; `S` returned as `S.y` | see [Appendix A](#appendix-a-jubjub-profile): canonical `y`, on the curve, in the prime-order subgroup, not the identity |

This CIP registers the `jubjub` profile only. Further profiles are added by a CIP that extends
this one.

### Purposes

A purpose is registered by this CIP, or by a later CIP that extends it. Each registration MUST
define:

1. the purpose identifier (lowercase, `[a-z0-9-]+`);
2. the algorithm profiles allowed;
3. the format of `EcdhRequest.ref` and any scoping rules;
4. the effect-based wording of the consent prompt;
5. what the scheme derives from `S`. The derivation MUST bind the context, at least `Epk` and the
   reference `ref`, so that one shared secret never yields the same keystream in two places;
6. the requirement on senders that `e` is fresh for every output and every transaction attempt,
   including rebuilt or fee-bumped attempts of the same payment;
7. what the recipient MUST verify after decrypting (for example that a decrypted amount opens
   the on-chain commitment). A shared secret does not, by itself, make a ciphertext valid.

| Purpose | Status | Profiles | `ref` format |
|---|---|---|---|
| `confidential-viewing` | Specified below | `jubjub` | `"<txHash>#<outputIndex>"` of the output carrying the note |

#### Purpose `confidential-viewing`

The key is the account's **viewing key** in a confidential-transfer scheme. A shared secret
returned by `ecdh` opens one confidential output (note).

- **`ref`:** MUST match `^[0-9a-f]{64}#(0|[1-9][0-9]*)$` and name the output carrying the note.
- **Consent wording**, in substance:

  > «origin» is asking to read the confidential amounts in your account. It will not be able to
  > move funds. You can revoke this at any time.

- **Derivation from `S`, sender rules and recipient verification:** as defined by the
  confidential-transfer scheme in use. A dApp MUST verify that each decrypted amount and blinding
  open the note's commitment, and MUST treat a note that fails as unreadable.
- **Scope of disclosure:** the viewing key reveals the amounts of notes **sent to** the account.
  Whether outgoing amounts can be recovered depends on the scheme, not on this extension.
- **Scoping (MAY).** A wallet MAY answer only for notes owned by the connected account. A wallet
  that scopes:
  - MUST resolve each `ref` from chain data it has verified itself (for example by checking that
    the producing transaction hashes to the referenced id). It MUST NOT trust data supplied by
    the dApp.
  - MUST check that the output is owned by the connected account and carries exactly the given
    `Epk`.
  - MUST still answer for spent notes, so that history remains readable.
  - MUST perform these checks **before** prompting the user, and report failures with the `info`
    codes in [Errors](#errors).
  - SHOULD rate-limit the chain lookups each origin can trigger, since they cost the wallet work
    before any prompt.

  Scoping narrows requests to keys that someone has placed at the user's address. **It does not
  prevent a chosen-key request**, because anyone can create a note-shaped output at the user's
  address carrying an `Epk` of their choosing. The [permission](#permission) remains the
  security boundary.

### Permission

Use of a purpose is a permission **separate from** `enable()` and from every other purpose.

- The wallet MUST obtain the user's explicit consent before the first call for a purpose from an
  origin is answered. The prompt MUST use the purpose's effect-based wording and MUST NOT be
  presented as, or combined with, a signature prompt.
- A grant MUST be scoped at least to (wallet, origin, purpose, account index, generation).
- Grants MUST be listed where the user manages connected sites and MUST be revocable with
  immediate effect. Disconnecting an origin MUST revoke all its grants.
- Before releasing any result, the wallet MUST re-check that the grant still holds and that the
  active account is unchanged. If the active account changed, it MUST answer `AccountChange`.
- A wallet SHOULD require user interaction (for example the spending password) for each `ecdh`
  or `ecdhBatch` call. A wallet that answers without per-call interaction MUST rate-limit each
  origin, and SHOULD ask again when an origin's usage changes markedly.

Revocation is not retroactive: whatever an origin has already decrypted, it knows.

### Encryption Keys API

#### `api.cip????.getPublicKey(key: KeySelector): Promise<PublicKeyInfo>`

Errors: `APIError`

Returns the public key selected by `key`. A wallet MAY answer `Refused` for an `accountIndex`
other than that of the connected account.

#### `api.cip????.ecdh(request: EcdhRequest, key: KeySelector): Promise<HexString>`

Errors: `APIError`

Equivalent to `ecdhBatch([request], key)[0]`.

#### `api.cip????.ecdhBatch(requests: EcdhRequest[], key: KeySelector): Promise<HexString[]>`

Errors: `APIError`

For each request, validates `ref` under the purpose and `Epk` under the profile, and returns the
shared secret `S = sk · Epk`, encoded as defined by the profile.

- The result has one entry per request, **in input order**.
- The call is **all or nothing**: if any request fails validation or scoping, the whole call
  fails and no secret is returned.
- The wallet MAY cap the batch size. The cap MUST NOT be lower than 512 requests. A larger batch,
  or an empty one, is `InvalidRequest`.
- The wallet's obligations end at `S`. It does not interpret ciphertexts, keystreams or
  commitments.

### Errors

This extension reuses [CIP-30]'s
[`APIError`](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0030#apierror) codes.

| Condition | Code | `info` |
|---|---|---|
| Origin not connected, wallet locked, permission declined or revoked, wallet cannot derive role `6`, account, purpose or profile not available, or the extension is not offered on this network | `Refused` (−3) | free text |
| Malformed `KeySelector`; profile not allowed for the purpose; batch empty, not an array or over the wallet's cap; malformed `EcdhRequest` or `ref`; `Epk` fails the profile's validation rules | `InvalidRequest` (−1) | free text |
| One or more references are not owned by the connected account, or do not carry the given `Epk` (scoping wallets only) | `InvalidRequest` (−1) | `not-own-ref:[i,…]` |
| One or more references cannot be resolved yet (scoping wallets only) | `InvalidRequest` (−1) | `unresolved-ref:[i,…]` |
| The active account changed during the request | `AccountChange` (−4) | free text |
| Any other failure | `InternalError` (−2) | free text |

Indices are 0-based positions in that call's `requests` array, ascending, written as JSON
without spaces (e.g. `not-own-ref:[1,3]`). When both apply, only `not-own-ref` is reported.

dApps SHOULD validate every `Epk` and `ref` before calling, chunk large requests, and on
`not-own-ref` or `unresolved-ref` mark the affected requests and retry the rest as one batch.
dApps MUST NOT retry after `Refused`, and SHOULD NOT fall back to one call per request, since each
call may cost the user a prompt.

### Versioning

This extension is versioned by its CIP number, as are all [CIP-30] extensions. A
backwards-incompatible change to the API requires a new extension CIP. Registering a new purpose
or algorithm profile is backwards-compatible: dApps select them by name, and wallets that do not
support them answer `Refused`. The `/v1` suffix in the derivation tag versions each key mapping
independently.

## Rationale: How does this CIP achieve its goals?

### Scope: three options considered

| Option | Scope | For | Against |
|---|---|---|---|
| A. Confidential viewing only | One key, one use | Smallest; already prototyped | Messaging or encrypted metadata would need another, overlapping CIP |
| **B. General ECDH, one key per purpose** (chosen) | One API, keys and permissions separated by purpose | Serves confidential transfers now and other encryption uses later; a grant for one purpose never exposes another | Broader design; only one purpose has an implementer today |
| C. Wallet `encrypt` / `decrypt` | Wallet runs the whole scheme | Simplest for dApps | Ties wallets to each scheme's KDF and cipher; turns the wallet into a decryption oracle |

Option B keeps the security properties of A and leaves room for the uses that motivated a
general "asymmetric encryption" capability. It costs little: purposes are a naming and
derivation-tag layer over the same API. The choice is open to change on feedback.

### Why Jubjub only

The curve is dictated by whatever must check the encryption on chain. Confidential notes on
[CIP-113] prove, in a Groth16 circuit over BLS12-381 verified with Plutus's BLS12-381 built-ins,
that each note is encrypted to its recipient's key. Jubjub is defined over BLS12-381's scalar
field, so its arithmetic is native to that circuit and costs a few thousand constraints per
operation. A curve over another field, such as ristretto255 over `2²⁵⁵ − 19`, would need
emulated field arithmetic in the circuit, typically one to two orders of magnitude more
constraints, and Plutus offers no built-ins for it. Such a curve only becomes useful if a future
ledger change verifies it natively. A CIP extending this one can then register it as a profile.

### ECDH, not decryption

The wallet computes the shared secret, not a plaintext. A `decrypt(ciphertext)` endpoint would
tie wallets to one scheme's key derivation, framing and cipher, and would have to change whenever
those do. ECDH between a long-lived key and a per-message ephemeral key is the primitive these
schemes share. It also keeps the unit of disclosure small: a shared secret opens **one** note or
message, whereas the key opens all of them.

### Separate keys per purpose and per network

Reusing one key across purposes would let a site granted access to, for example, encrypted
messages read the user's confidential amounts. Domain separation in the key mapping gives each
purpose an independent key from the same seed and path, so no new backup is needed. Separate
permissions per purpose make the user's consent meaningful.

The network is part of the tag for a similar reason. Without it, a test-network dApp could
plant, at the user's test-network address, a note copied from a mainnet note sealed to that
user, and have it opened after consent. With per-network keys, a mainnet note cannot be opened
by the test-network key.

### Static-key ECDH oracle

The API is, by design, an oracle that returns `sk · P` for points the caller chooses. Two
consequences shape the specification:

- **Key-usage restriction.** `sk · H(m)` is a BLS-style signature on `m`, so the key MUST NOT be
  used for any signature or proof of that form. Schnorr-style proofs, whose responses are scalars,
  are not affected.
- **Repeated queries.** A static Diffie–Hellman oracle allows the Brown–Gallant / Cheon attack,
  which lowers the cost of recovering `sk` when the group order `ℓ` satisfies `d | ℓ − 1` for a
  usable `d` and the attacker can chain about `d` queries. For Jubjub, the small factors of
  `ℓ − 1` are `2 · 3 · 12281` (`d ≈ 2¹⁶`), so about 74 000 chained queries would cut security
  by roughly 8 bits, from about 126 bits. This is negligible, but it is why wallets that answer
  without per-call interaction MUST rate-limit.

### No export; proof of possession is open

- **No key export.** It would reduce the design to "any site that obtained it once has it
  forever". If an auditor ever needs a secret itself, that is a separate and much more severe
  permission, and wallets must remain free not to offer it.
- **Binding a key to an account.** [CIP-30] `signData` already lets a stake key sign a claim
  containing `PK`, since it specifies that *"the staking key will be used for reward
  addresses"*. That proves authority over the **account**. It does **not** prove that anyone holds
  the private key behind `PK`. A buggy wallet, or an account owner setting a trap, could bind a
  key that nobody can use, and payments sent to it would be stranded. Whether this extension
  should also offer a proof of possession is [Open Question 2](#open-questions).

### References, not bare keys

Requiring a `ref` with every `Epk` costs the dApp nothing, because it read `Epk` from that place.
It lets wallets scope requests, reject garbage before prompting, and keep an audit trail. A
bare-key form would make the endpoint a general-purpose ECDH oracle on the key.

### Point validation

The `Epk` is the only place where a page can attack the **key** rather than the data. Jubjub has
cofactor 8, so it has small-order points, and a `y`-only encoding admits values that are not on
the curve at all. A crafted `Epk` of either kind can leak `sk` modulo a small factor: through a
small subgroup, or through an "invalid-curve" computation on the curve's quadratic twist. The
checks in [Appendix A](#appendix-a-jubjub-profile) close both, before any key material is
touched. This is acceptable for a cofactor curve here because the key is used for one operation
only, on validated points, with no homomorphic algebra on attacker-supplied values. It also means
a hostile page cannot cost the user a prompt.

### Relationship to other proposals

- **[CIP-95]** is the template: a namespaced, additive [CIP-30] extension that introduced a new
  key role together with wallet behaviour for it.
- **[CIP-1852] / [CIP-0105]:** role `6` follows the way [CIP-0105] added governance roles. The
  derivation could be split into a separate companion CIP if wallet implementors prefer.
- **[Native Confidential Transfers]** is a ledger-level proposal that depends on future hard
  forks, so it is expected to follow this CIP by a long way. It also proposes role `6` for its
  viewing key. This CIP generalises that role to encryption keys, so that a later ledger-level
  scheme can register its curve as a profile here instead of claiming the role separately.
- **[CIP-83]** is a candidate for a future purpose that would replace shared passphrases with
  public-key encryption.
- **Out of scope: signing [CIP-113] programmable inputs.** Spending confidential notes held as
  [CIP-113] programmable tokens requires wallets to witness inputs at a programmable-logic script
  address when the transaction names the wallet's stake key in `required_signers`. [CIP-30]
  `signTx` with `partialSign` already permits this. Whether and under which safety conditions a
  wallet *should* do it concerns every [CIP-113] token, so it belongs in a separate proposal:
  [Web-Wallet Bridge - Programmable Token Signing]. Confidential transfers through dApps need
  both proposals. Neither depends on the other.

### Backwards Compatibility

This proposal is purely additive. No existing [CIP-30] endpoint changes. dApps and wallets that
do not use the extension are unaffected.

### Open Questions

1. **Path level or tag for purposes.** Purposes are separated in the key mapping, not in the path.
   This keeps one generation index per account, so rotating one purpose's key rotates all of them.
   Should purposes instead get their own path level (`…/6/purpose'/generation'`)?
2. **Proof of possession.** Should the extension offer an endpoint that proves the wallet holds
   `sk` for a published `PK`, such as a Schnorr proof with the account's stake credential bound
   into the challenge? Or is that left to each scheme? For confidential notes, the scheme's
   on-chain check that every note decrypts under its owner's signed key does not detect a key
   nobody holds.
3. **Compatibility with the prototype.** The Gero prototype derives the `jubjub` viewing key with
   the tag `cip1233-poc/viewing-key/jubjub-v1`, with no network separation, and exposes it as
   `api.experimental.confidentialViewing` with different method names. Its keys and test vectors
   therefore differ from this specification. How should existing prototype users migrate?
4. **Generation discovery.** dApps have no way to learn which generations an account has used.
   Should `getPublicKey` report the latest generation, or should purposes define how generations
   are discovered (for example from on-chain registrations)?
5. **Sender-side derivation.** The `jubjub` scheme lets the dApp choose the ephemeral scalar `e`.
   A future scheme may require the sender to derive `e` from its own key, for example to make
   outgoing payments auditable, and a dApp cannot do that without the wallet. Should purposes be
   able to define a sender-side endpoint? This does not block the `jubjub` profile.
6. **Hardware wallets.** Role-`6` derivation is ordinary BIP32-Ed25519 work, but current Cardano
   hardware-wallet apps expose no on-device ECDH. Should the CIP define how a hardware wallet
   signals this, beyond `Refused`?
7. **A second purpose.** Should an encrypted-message purpose for [CIP-83]-style metadata be
   specified in this CIP, or left to a follow-up?

## Path to Active

### Acceptance Criteria

- [ ] A CIP number is assigned, and role `6` is accepted into [CIP-1852], either by this CIP or by
      a companion CIP.
- [ ] Open Questions 1 and 2 are resolved in the specification.
- [ ] Conformance test vectors are published for every registered purpose and profile: key
      derivation for each network, `PK`, ECDH, and rejection of invalid `Epk` values.
- [ ] An independent cryptographic review of the specification is completed.
- [ ] At least two wallets implement the extension under its assigned namespace.
- [ ] At least one dApp uses the extension in production.

### Implementation Plan

- [x] Prototype of the `confidential-viewing` purpose with the `jubjub` profile in Gero Wallet
      (branch `feat/cip30-confidential-transfers`, under `api.experimental.confidentialViewing`;
      Preview and Preprod only, mainnet refused).
- [x] Reference dApp using the prototype to open confidential notes on [CIP-113] programmable
      tokens, verified on Preprod.
- [ ] Align the prototype with this specification (namespace, method names, derivation tag with
      network separation, explicit on-curve check).
- [ ] Engage other wallet implementors via the wallet working groups and [CPS-0010].

## References

- [CIP-8] — Message Signing
- [CIP-30] — Cardano dApp-Wallet Web Bridge
- [CIP-83] — Encrypted Transaction message/comment metadata
- [CIP-95] — Web-Wallet Bridge - Conway ledger era
- [Web-Wallet Bridge - Programmable Token Signing] — CIP-???? (PR #1312)
- [CIP-0105] — Conway era Key Chains for HD Wallets
- [CIP-113] — Programmable token-like assets
- [CIP-1852] — HD (Hierarchy for Deterministic) Wallets for Cardano
- [CPS-0010] — Wallet Connectors
- [Native Confidential Transfers] — CIP-???? (PR #1233)
- [RFC 2119] — Key words for use in RFCs to Indicate Requirement Levels
- [RFC 5869] — HMAC-based Extract-and-Expand Key Derivation Function (HKDF)

## Appendices

### Appendix A: Jubjub profile

- **Group:** the prime-order subgroup of Jubjub (order `ℓ`), the twisted Edwards curve
  `−x² + y² = 1 + d·x²·y²` defined over the BLS12-381 scalar field `p`, with cofactor 8. Used where
  a circuit over that field must prove that data is encrypted to a given key, as in confidential
  notes on [CIP-113].
- **Encoding:** points are represented by their `y` coordinate, 32 bytes big-endian. The sign of
  `x` is irrelevant to the result, since `sk·(±Epk)` has the same `y`.
- **Mapping:** with HKDF-SHA256 as in [RFC 5869],

  ```
  sk = HKDF-SHA256( ikm  = key_material (64 bytes),
                    salt = none,
                    info = tag,
                    L    = 64 ) mod ℓ
  ```

  If the result is `0`, which happens with negligible probability, the wallet MUST answer
  `InternalError`.
- **Validation of `Epk`.** The wallet MUST reject `Epk` unless all of the following hold, in this
  order:
  1. it is exactly 32 bytes, and `y < p`;
  2. **on the curve:** `x² = (1 − y²) / (−1 − d·y²)` has a solution in the field, i.e. the
     right-hand side is defined and is a square. A value of `y` that fails this check has no point
     on Jubjub, and computing with it on a `y`-only ladder would operate on the twist;
  3. **in the prime-order subgroup:** for either recovered point `P`, `ℓ · P` is the identity.
     This excludes every small-order point other than the identity (`y = p − 1`, `y = 0` and the
     two `y` values of the order-8 points) and every mixed-order point;
  4. **not the identity:** `y ≠ 1`.
- **Prototype test vectors (not conformance vectors).** These were produced by the Gero prototype
  with the tag `cip1233-poc/viewing-key/jubjub-v1` and no network separation (see
  [Open Question 3](#open-questions)). They demonstrate the derivation path and mapping, but do
  not match the tag this specification defines. Conformance vectors are an acceptance criterion.
  The seed phrases are the public BIP-39 test vectors.

  | BIP-39 test phrase | Path | `PK.y` |
  |---|---|---|
  | `abandon … abandon about` | `m/1852'/1815'/0'/6/0'` | `68f88716c7eda97e5762dad7165caaf268907c8e6fea6cb525357547fa37c800` |
  | same | `m/1852'/1815'/1'/6/0'` | `28deb51d0fc85bf61360fa2c3fb38fe807c4d8999ce18c67d3e8b5415a3fabf9` |
  | `zoo … zoo wrong` | `m/1852'/1815'/0'/6/0'` | `41c6bb520c96ae265b72186b5ab7efb10ad97687018e07c1412f9797fc5dad17` |
  | `abandon amount liar amount expire adjust cage candy arch gather drum buyer` | `m/1852'/1815'/0'/6/0'` | `67ca6733dba770de0b90689bb87df6dfe1f1c443e1eec4b2149b0cad6fdb1476` |

## Acknowledgements

The API design and the `jubjub` prototype come from the confidential-notes proof of concept on
[CIP-113] programmable tokens and its Gero Wallet integration. The security requirements draw on
the review findings by Dr. Manvir Schneider on [Native Confidential Transfers].

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).

[CIP-8]: https://github.com/cardano-foundation/CIPs/tree/master/CIP-0008
[CIP-30]: https://github.com/cardano-foundation/CIPs/tree/master/CIP-0030
[CIP-83]: https://github.com/cardano-foundation/CIPs/tree/master/CIP-0083
[CIP-95]: https://github.com/cardano-foundation/CIPs/tree/master/CIP-0095
[Web-Wallet Bridge - Programmable Token Signing]: https://github.com/cardano-foundation/CIPs/pull/1312
[CIP-0105]: https://github.com/cardano-foundation/CIPs/tree/master/CIP-0105
[CIP-113]: https://github.com/cardano-foundation/CIPs/tree/master/CIP-0113
[CIP-1852]: https://github.com/cardano-foundation/CIPs/tree/master/CIP-1852
[CPS-0010]: https://github.com/cardano-foundation/CIPs/tree/master/CPS-0010
[Native Confidential Transfers]: https://github.com/cardano-foundation/CIPs/pull/1233
[RFC 2119]: https://www.rfc-editor.org/rfc/rfc2119
[RFC 5869]: https://www.rfc-editor.org/rfc/rfc5869
