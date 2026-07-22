---
CIP: "?"
Title: Native Confidential Transfers
Category: Ledger
Status: Proposed
Authors:
    - Mateusz Czeladka <mateusz.czeladka@cardanofoundation.org>
    - Pawel Jakubas <pawel.jakubas@cardanofoundation.org>
Implementors: []
Discussions:
    - Original PR: https://github.com/cardano-foundation/CIPs/pull/1233
Created: 2026-07-22
License: CC-BY-4.0
---

## Abstract

This proposal introduces **native confidential transfers** for Cardano: the ability to send
ADA and native tokens so that the transferred **amounts** are hidden on chain, while the ledger
can still verify — without decrypting anything — that no value was created or destroyed. Amounts
are carried as additively — i.e. **partially** — homomorphic commitments and accompanied by
zero-knowledge proofs that they are non-negative and that value is conserved. Each account holds a single **confidential viewing key**
that lets its owner (and anyone the owner discloses it to, such as an auditor) recover the hidden
amounts addressed to it. Sender and recipient addresses, the transaction graph, fees, and the
*identity* of native assets remain public; only *quantities* are hidden. The scheme is designed
to fit the extended UTXO (EUTXO) model directly and to rely on a small set of well-established
cryptographic primitives with no trusted setup.

This CIP describes a purely **native** (ledger-level) implementation: confidentiality is provided
by the ledger's own validation rules. It does **not** rely on smart contracts, an escrow, a mixer,
or any off-ledger service. Smart-contract-based approaches to amount privacy or selective
disclosure may be possible, but they are explicitly out of scope here.

## Motivation: Why is this CIP necessary?

On Cardano today, every output's ADA and native-token amount is public. This transparency is
unsuitable for many legitimate uses — payroll, treasury operations, commercial invoicing,
business-to-business settlement, and any activity where revealing exact balances and payment
amounts to the entire world is undesirable — yet those users still need a verifiable,
non-custodial ledger and the ability to satisfy auditors and tax authorities.

Put plainly: some entities need to transact **without the rest of the world learning the details
of their financial activity — above all, how much they transact and hold**. The aim of this
proposal is therefore **confidentiality from the general public, not from oversight**: amounts
are hidden from everyone *except* the parties the owner deliberately authorises.
A user can, of their own will and choosing, designate **one or more auditors** — a tax
authority, an accountant, or tax-reporting software — by sharing the account's single viewing
(decryption) key with them, giving those parties complete read access to the account's amounts
while the rest of the world sees nothing. **Pure privacy or anonymity transfers are explicitly
not the goal of this proposal**: designs that hide identities or break the transaction graph
(mixers, shielded pools, and similar) address a different need and belong to other proposals or
solutions. This CIP targets the common commercial reality in which confidentiality and
auditability must coexist.

There is currently no native mechanism on the Cardano ledger to hide transfer amounts. Existing
cryptographic building blocks in the ecosystem target proof verification inside scripts and do
not provide amount confidentiality at the ledger level. As a result, amount privacy is either
unavailable or pushed entirely off the base ledger.

This CIP addresses that gap at the **ledger** level: it defines how confidential amounts are
represented in transactions, what proofs a transaction must carry, and what validators must
check, so that:

- amounts of **ADA and native tokens** can be hidden;
- the ledger remains **publicly and cheaply verifiable** (no validator ever decrypts);
- **no value can be created or destroyed** by hiding it;
- amounts can be **selectively disclosed** to an auditor or tax authority via a single per-account
  key, without weakening confidentiality for everyone else.

Confidentiality is opt-in per output: transactions that do not use confidential outputs are
entirely unaffected.

## Specification

> **Scope.** This proposal specifies amount confidentiality for ADA and native tokens with the
> asset *type* (policy id and asset name) remaining public. Hiding the asset type, hiding
> sender/recipient identity, confidential outputs at script addresses, and interaction with
> programmable tokens are **out of scope** and discussed under [Open Questions](#open-questions).

### 1. Overview

A **confidential output** replaces the cleartext amount of each asset it holds with a homomorphic
**commitment** to that amount, plus a small piece of data that lets the recipient recover the
amount. A transaction that produces or consumes confidential outputs carries a **confidential
proof** demonstrating, in zero knowledge, that:

1. every hidden amount is a valid, non-negative quantity within range, and
2. for **each asset independently**, the hidden inputs, hidden outputs, public movements
   (fees, mint/burn, and any transparent inputs/outputs) balance exactly.

Spending a confidential output is authorised exactly as today — by the address's key witness.
Amount confidentiality is orthogonal to spend authorisation.

### 2. Cryptographic primitives and parameters

The scheme uses a deliberately small set of primitives, all over a single prime-order group.

- **Group.** The prime-order group **ristretto255** as defined in
  [RFC 9496][rfc9496], with its canonical 32-byte encoding. Group elements ("points") and scalars
  are 32 bytes. Let `ℓ` denote the (prime) group order. Two fixed, independent generators are
  used: `G` (the standard generator) and `H`, derived by hashing a fixed domain-separation string
  to a group element so that the discrete-log relation between `G` and `H` is unknown to everyone.
  A **prime-order** group is required (see [Rationale](#why-a-prime-order-group-ristretto255)):
  the raw Curve25519 group has cofactor 8 (its order is `8·ℓ`), which admits small-subgroup
  elements and non-canonical encodings that would break the commitment and proof machinery.
  ristretto255 removes the cofactor, yielding a clean prime-order group with a unique encoding per
  element, while reusing the same well-studied field as Cardano's existing Ed25519.
- **Pedersen commitment.** A commitment to a scalar value `v` with blinding `r` is
  `C = v·H + r·G`. It is perfectly hiding (reveals nothing about `v`) and computationally binding
  (the committer cannot later open it to a different value). It is additively homomorphic:
  `C(v₁,r₁) + C(v₂,r₂) = C(v₁+v₂, r₁+r₂)`. This homomorphism is deliberately **partial**
  (additive only) — the same class as *partially homomorphic encryption* (PHE): exactly one
  operation, addition (and hence subtraction), is available on hidden values, an unlimited
  number of times. That is precisely what value conservation requires; the scheme is *not*
  fully homomorphic and does not need to be.
- **Range proof.** A **Bulletproofs** [BBBPWM18][bulletproofs] proof that a committed value lies
  in `[0, 2⁶⁴)`, with no trusted setup and logarithmic proof size. Multiple commitments are
  aggregated into a single proof per transaction.
- **Amount transport (Diffie–Hellman).** A per-output ephemeral key and a Diffie–Hellman shared
  secret let the recipient recover the amount and derive its blinding (§5).
- **Balancing proof.** A **Schnorr** signature proving knowledge of the *excess* blinding of a
  commitment to zero value, establishing value conservation per asset (§7).
- **Non-interactivity.** All proofs are made non-interactive with the **Fiat–Shamir** transform,
  using a cryptographic hash and a domain-separation tag bound to the transaction context.

No trusted setup is required by any of these primitives.

### 3. Keys

Confidentiality is keyed at the level of an **account**, defined here as a **single stake address
(stake credential)** — not an individual payment address. All payment addresses that share the
same stake credential share **one** confidential viewing keypair `(sk_view, P_view)` with
`P_view = sk_view·G`. This keeps key management proportional to accounts rather than to the many
payment addresses an account may use.

- `sk_view` lets the account owner recover the amount of **every** confidential output addressed
  to any payment address of that account.
- `P_view` is published/bound to the stake credential so senders can address confidential outputs
  to the account and so a disclosed key can be verified against it (the exact binding — a new
  address/stake component or an on-chain registration — is discussed under Open Questions).
- Disclosing `sk_view` grants **read** access only and never grants spend authority, which
  remains with the separate spending key(s). The account has exactly **one** viewing key; its
  owner may, at their own discretion, share it with **one or more auditors** — each receives the
  same key and the same complete read access.

**Wallet key derivation.** Wallets are expected to derive `sk_view` **deterministically from the
wallet's existing seed**, using a **new, dedicated derivation path** in the hierarchical-
deterministic scheme already used on Cardano (in the spirit of [CIP-1852], e.g. a new role or
purpose index reserved for confidential viewing keys). The viewing key must never be a reused
signing key: it is a Ristretto255 scalar on its own path, cleanly separated from payment and
stake keys. Deriving it from the existing seed means: no new seed or backup is required,
restoring a wallet from its mnemonic also restores the viewing capability (and therefore the
ability to re-read all of the account's confidential amounts from chain data), and **existing
accounts can adopt confidential transfers without creating a new wallet or account**. The exact
derivation path is to be standardised (see Open Questions).

### 4. Confidential value representation

An asset is identified publicly by `(policy_id, asset_name)`; ADA (lovelace) is treated as a
reserved, distinguished asset. A **confidential value** reveals *which* assets are present but
hides each asset's *quantity* as a Pedersen commitment:

- ADA quantity `v` → `C = v·H + r·G`.
- Each native-asset quantity `q` under `(policy_id, asset_name)` → `C = q·H + r·G`.

Conservation (§7) and range proofs (§6) are applied **per asset**.

An output is either fully **transparent** (exactly as today) or fully **confidential**; the two
forms do not mix within a single output. Every confidential output **must** include an ADA
commitment, whose quantity is subject to the minimum-ADA rule enforced in zero knowledge (§6).
In this proposal, confidential outputs are restricted to **key-locked (payment-key) addresses**;
outputs at script addresses cannot be confidential (see Open Questions).

### 5. Amount transport

To spend a confidential output, its owner must know the hidden amount **and** its blinding `r`.
Both are conveyed with a Diffie–Hellman shared secret plus a small stored ciphertext:

1. The sender picks a fresh ephemeral scalar `e` and includes the ephemeral public key `E = e·G`
   in the output. `E` must not be the identity element — a predictable shared secret would expose
   the amounts — and validators reject it (§11, rule 1).
2. The shared secret is `s = e·P_view` (computed by the sender) `= sk_view·E` (computed by the
   recipient) — the same group element.
3. For each asset in the output, a key-derivation function — domain-separated by the **asset
   identifier and the output's position within the transaction** (so that no two derivations
   ever coincide) — derives from `s` the blinding `r` and an amount-encryption keystream. The
   amount itself cannot be *derived* from `s` (it is chosen freely by the sender): it is stored
   in the output as an 8-byte **masked amount** `v ⊕ keystream`.
4. The recipient recomputes `s` from `E` using `sk_view`, derives `r` and the keystream, recovers
   `v` from the stored masked amount, and **must verify `C == v·H + r·G`** before accepting the
   payment. If the check fails, the output was not honestly constructed for this recipient and
   must be treated as unspendable.

Because the blinding is recomputable by whoever holds `sk_view`, the recipient can later spend
the output (construct the balancing proof of §7) **without any interaction** with the original
sender. An auditor given `sk_view` recovers all amounts for the account by the same computation.
Note that the **sender** also retains knowledge of `(v, r)` for outputs it creates — inherent to
Diffie–Hellman transport — but this grants no spend authority, which requires the recipient's
spending key.

### 6. Range proofs

Over a prime-order group, a "negative" amount is indistinguishable from a very large scalar that
wraps modulo `ℓ`; without a bound, a malicious sender could commit to a negative quantity and
mint value. Therefore **every** committed quantity in **every** confidential output carries a
range proof that it lies in `[0, 2⁶⁴)`:

- `2⁶⁴` covers the full range of ADA (max supply is 45 billion ADA = 4.5 × 10¹⁶ lovelace, below
  `2⁵⁶`) and of native-asset quantities, which fit an unsigned 64-bit integer.
- All range proofs in a transaction are **aggregated into a single Bulletproofs proof**.
- Where the ledger requires a minimum ADA quantity for an output, the requirement `v ≥ min` is
  proved by additionally range-proving the **shifted commitment** `C − min·H` — a commitment to
  `v − min` under the same blinding, computable by anyone from the public `min` — at the cost of
  one extra range statement per confidential output. The requirement is thus enforced without
  revealing `v`.

### 7. Value conservation

Cardano requires that value is conserved: for each asset, the sum of inputs equals the sum of
outputs plus any public movement of that asset. For confidential amounts this is checked
**homomorphically, per asset**, without revealing any quantity.

For a given asset, let the confidential inputs have commitments `Cᵢⁿ` and the confidential
outputs `Cᵒᵘᵗ`, and let `Δ` be the **public** net movement of that asset (for ADA this includes
the fee; for native assets it includes any mint or burn and any transparent inputs/outputs of
that asset). A valid transaction satisfies:

```
Σ Cᵢⁿ  −  Σ Cᵒᵘᵗ  −  Δ·H   ==   excess·G ,      excess = Σ rᵢⁿ − Σ rᵒᵘᵗ
```

Because conservation of the hidden quantities forces the `H` (value) components to cancel
exactly, the left-hand side is a commitment to **zero value** — a pure multiple of `G`. The
transaction proves knowledge of `excess` with a **Schnorr signature** under the public key
`excess·G` (the "balancing signature"). Altering any hidden quantity makes the `H` component
fail to cancel, so the equation — and hence verification — fails. Fees remain public and enter
as part of `Δ` for ADA. Each asset has its own balancing check; assets cannot be converted into
one another.

### 8. Bridging transparent and confidential amounts (shield / unshield)

Confidential amounts must be backed one-to-one by real value. **Shielding** (making transparent
value confidential) and **unshielding** (revealing confidential value back to transparent) are
not special operations: they are ordinary transactions that mix transparent and confidential
inputs and outputs. All transparent components are public, so the net public movement `Δ` of
each asset (§7) is computed directly from the transaction's public data — transparent inputs and
outputs, the fee, and any mint or burn — and the per-asset balancing equation then enforces that
the confidential side absorbed or released **exactly** that amount. No separate opening proofs
are needed: hidden amounts that do not match the public legs cannot satisfy the balancing
equation without a negative hidden output, which the range proofs forbid.

The total confidential supply of each asset equals (total shielded − total unshielded) — a
public quantity — so the confidential pool is conservation-checked against transparent value at
every step, and no asset can be minted by hiding it. The transparent legs of such transactions
are the only places where amounts entering or leaving the confidential domain are revealed.

### 9. Staking, rewards, and governance

Cardano's stake distribution — used for leader election, rewards, and governance voting power —
is computed from publicly visible ADA amounts. A hidden amount cannot contribute to that
computation without revealing information about itself. In this proposal, therefore:

- **Confidential ADA does not contribute to stake.** ADA held in confidential outputs is
  excluded from the stake of the associated stake credential, from reward calculation, and from
  governance voting power, for as long as it remains confidential.
- **Unshielding restores participation.** Once ADA is returned to a transparent output, it
  counts toward stake, rewards, and voting power exactly as today.

This is an explicit, accepted opportunity cost of confidentiality. Contributing hidden amounts
to the stake distribution in zero knowledge is substantially more complex and is left as future
work (see Open Questions).

### 10. Transaction and output structure (CDDL)

The following CDDL is **illustrative** and describes the additional structures at a design level;
concrete field indices and integration with the existing transaction CDDL are to be finalised
during implementation.

```cddl
; A canonically-encoded ristretto255 point / scalar, 32 bytes each (RFC 9496).
ristretto_point = bytes .size 32
scalar32        = bytes .size 32

commitment      = ristretto_point      ; Pedersen commitment C = v·H + r·G
masked_amount   = bytes .size 8        ; v XOR keystream; recoverable with sk_view (see section 5)

; A hidden quantity: the commitment plus the recipient's masked amount.
confidential_asset = [ commitment, masked_amount ]

; Confidential value: which assets are present is public; every quantity is hidden.
; The ADA entry is mandatory: every output must satisfy minimum-ADA (section 6).
confidential_value =
  { lovelace : confidential_asset
  , ? assets : { policy_id => { asset_name => confidential_asset } }
  }

; A confidential output. Restricted to key-locked addresses in this proposal (section 4);
; `address` refers to the existing transaction CDDL.
confidential_output =
  { address            : address
  , confidential_value : confidential_value
  , ephemeral_key      : ristretto_point   ; E = e·G, for amount transport (section 5)
  }

; A Schnorr signature (R, s) proving knowledge of the per-asset excess (section 7).
schnorr_sig = [ ristretto_point, scalar32 ]

; Per-transaction confidential proof, carried in the witness set.
; Shield/unshield need no dedicated structures: the public movement of each asset is
; computed from the transaction's public data and enters the balancing check (section 8).
confidential_proof =
  { range_proof : bytes                        ; aggregated Bulletproofs over all commitments
  , balancing   : { asset_ref => schnorr_sig } ; one excess signature per asset
  }

policy_id  = bytes .size 28
asset_name = bytes .size (0..32)
asset_ref  = 0 / [ policy_id, asset_name ]     ; 0 denotes ADA (lovelace)
```

### 11. Validation rules, edge cases and soundness

A transaction containing confidential outputs is **invalid** unless **all** of the following
hold. These rules are what make the construction sound against value creation or theft.

1. **Well-formed encodings.** Every commitment, ephemeral key, and proof element is a *canonical*
   ristretto255 encoding (the canonical encoding of ristretto255 makes this unambiguous);
   non-canonical encodings are rejected. The **ephemeral key must not be the identity element** —
   an identity `E` yields a predictable shared secret, exposing the output's amounts to anyone.
2. **Range (no negative, no overflow).** The aggregated range proof verifies that **every**
   committed quantity is in `[0, 2⁶⁴)`. This is what prevents a "negative amount" (a scalar near
   `ℓ`) from being used to inflate a balance, and prevents per-amount overflow. Because each
   amount is `< 2⁶⁴` and the number of outputs per transaction is bounded, no sum can wrap modulo
   `ℓ` (`ℓ ≈ 2²⁵²`).
3. **Per-asset conservation (balance is preserved, nothing is created).** For **each** asset the
   balancing equation of §7 holds and its Schnorr excess signature verifies. This guarantees, for
   every asset, that hidden outputs plus public movements equal hidden inputs — i.e. the net
   created value is exactly zero. Combined with rule 2, no value can be created and no negative
   output can exist.
4. **Minimum quantity.** For any output subject to minimum-ADA, the aggregated range proof also
   covers the shifted commitment `C − min·H` (§6), proving `v ≥ min`; outputs that cannot prove
   this are rejected. This preserves anti-dust and related economic rules despite hidden amounts.
5. **Transparent–confidential bridging.** The public net movement `Δ` of each asset is computed
   from the transaction's public data only (transparent inputs and outputs, fee, mint/burn) and
   enters that asset's balancing equation (§7). Hidden amounts that do not match the public legs
   cannot balance without a negative hidden output, which rule 2 forbids — so no separate
   opening proofs are required for shielding or unshielding (§8).
6. **Spend authorisation unchanged.** Consuming a confidential output still requires the normal
   key witness(es) for its address; confidential data is bound into the transaction so it cannot
   be reattached to a different transaction (replay/malleability protection via the
   domain-separated Fiat–Shamir context).
7. **Determinism.** Verification is deterministic across all validators; any randomness used in
   batch verification is derived deterministically (via Fiat–Shamir) from the transaction, never
   from a local source, so that all nodes reach identical accept/reject decisions.
8. **Zero-value and empty outputs.** A confidential output committing to zero of every asset is
   subject to the same minimum-quantity rule as any other output (rule 4) and is otherwise a
   valid, well-formed commitment.

### 12. Auditing and selective disclosure

Because only *amounts* are hidden and the transaction graph is public, disclosing an account's
single `sk_view` (one key for the whole account, i.e. the stake address — §3) gives the holder of
that key a complete, human-readable history of the **entire account** across all its payment
addresses — which counterparties, which assets, and how much — recovered by the computation of §5.
This supports auditing and tax reporting: the account owner, of their own volition, hands the
single `sk_view` to **one or more auditors of their choosing** — a tax authority, an accountant,
or tax-reporting software. Disclosure is
verifiable (the disclosed key can be checked against the published `P_view`) and grants read access
only. Whether disclosure is on request or mandatory in some contexts is a policy matter outside
this specification.

Recovering an account's amounts from `sk_view` requires **no chain-wide scanning or trial
decryption**: because addresses are public, an auditor or tool needs only the outputs already
indexed for the account's addresses, plus one Diffie–Hellman computation per output (§5).
Disclosure-based auditing therefore composes directly with existing address-indexing
infrastructure.

### 13. Versioning

The feature is gated by the protocol version and is inert below its activation version. The
on-chain structures defined here are versioned so that future revisions of the proof system
(for example, a newer range-proof construction) can be introduced under a new version while
older transactions continue to verify under the version they were created with.

## Rationale: How does this CIP achieve its goals?

### Design approach

The scheme is a **commitment-based confidential transaction** design: amounts live inside
additively homomorphic Pedersen commitments, value conservation is checked directly on those
commitments per asset, and range proofs prevent the only way commitments could be abused
(negative/overflowing values). This directly matches the EUTXO model, where the ledger already
reasons about value conservation across inputs and outputs; confidentiality replaces the
cleartext value in that reasoning with a commitment and a proof, leaving the structure of the
model intact.

The set of primitives is intentionally minimal for this model: a prime-order group, Pedersen
commitments, Bulletproofs range proofs, a Diffie–Hellman amount transport, one Schnorr balancing
proof per asset, and the Fiat–Shamir transform. None require a trusted setup.

The construction is **partially homomorphic by design**. Like partially homomorphic encryption
(PHE) schemes, it supports exactly one operation over hidden values — addition — an unlimited
number of times. Balance accounting needs nothing more (addition, subtraction, and range
checks), and additive-only homomorphism keeps every ledger operation at microsecond scale.
Fully homomorphic encryption (FHE), which would allow arbitrary computation over hidden data at
orders-of-magnitude higher cost, is neither needed nor practical on-chain (see
[Alternatives considered](#alternatives-considered)).

### Why these choices

- <a id="why-a-prime-order-group-ristretto255"></a>**Why a prime-order group (ristretto255).**
  The commitment and proof machinery needs a group where every non-zero scalar is invertible and
  every element has exactly one encoding. The raw Curve25519 group does **not** qualify: its order
  is `8·ℓ` — it has **cofactor 8**, meaning small "torsion" subgroups and multiple valid encodings
  for what should be the same element. That would enable small-subgroup attacks and would break the
  deterministic, canonical transcript hashing on which the proofs (and cross-node consensus) rely.
  A **cofactor-1** (prime-order) group avoids all of this. Rather than adopt a different curve,
  **ristretto255** (RFC 9496) applies a standard construction over Curve25519 that removes the
  cofactor, giving a clean prime-order group with a unique 32-byte encoding per element, ~128-bit
  security, and reuse of the same well-studied field Cardano already uses for Ed25519.
- **Pedersen commitments.** They are simultaneously hiding, binding, additively homomorphic, and
  directly compatible with efficient range proofs — the exact combination needed to hide amounts
  while keeping conservation checkable. A **single value generator `H` serves all assets**:
  because asset identity is public and each asset's conservation is checked over its own disjoint
  set of commitments, per-asset generators (needed in designs that also blind the asset type,
  such as Confidential Assets) are unnecessary here.
- **Bulletproofs.** Short proofs, aggregation, and — crucially for a public chain — **no trusted
  setup**.
- **Diffie–Hellman amount transport.** Conveys both the amount and its blinding to the recipient
  with no extra ciphertext, enabling non-interactive spending in the EUTXO model.

### Trade-offs

- **Transaction size.** Confidential transactions are larger than transparent ones — roughly
  **3–5×** for typical small payments — dominated by the (near-fixed) aggregated range proof, and
  growing with the number of distinct assets whose amounts are hidden (each asset needs its own
  commitment and range contribution). This increases fees proportionally to size.
- **Verification cost.** Range-proof verification cost grows with the number of committed values;
  aggregation and batch verification mitigate this, but it remains higher than validating a
  transparent amount.
- **Not post-quantum.** Security rests on the elliptic-curve discrete-logarithm and DDH
  assumptions and is not resistant to a future cryptographically-relevant quantum computer;
  amounts recorded today could in principle be recovered by such an adversary
  ("harvest-now-decrypt-later"). This is an accepted trade-off for a fast, small, trusted-setup-free
  design; post-quantum confidentiality is left for future work.
- **Asset type is public.** Only quantities are hidden; the presence and identity of assets in an
  output remain visible.
- **Confidential ADA does not stake.** ADA in confidential outputs is excluded from stake,
  rewards, and governance voting power while it remains hidden (§9) — an opportunity cost holders
  accept when shielding.
- **Auditor-facing tooling does not exist yet.** As of this writing, no mainstream tax or
  accounting software supports viewing-key import for *any* chain; users of existing privacy
  systems instead export a transaction history (e.g. CSV) from their wallet and import that, and
  the same fallback applies here from day one. Direct viewing-key support in such tools may or
  may not materialise — until it does, producing auditor-readable reports is the wallet's job,
  which is an ongoing complexity cost for users and companies relying on the audit path. The
  design deliberately minimises what a third-party tool must implement — amounts are recoverable
  from already-indexed outputs with one Diffie–Hellman computation each, with no chain-wide
  scanning (§12) — but adopters should treat third-party tooling support as an ecosystem
  dependency, not a given.

### Alternatives considered

- **Twisted-ElGamal ciphertexts (commitment plus per-recipient decryption handles).** The
  commitment used here, `C = v·H + r·G`, is exactly the commitment half of a Twisted-ElGamal
  ciphertext; the full scheme would add a decryption handle `D = r·P` per authorised reader,
  allowing each of them to decrypt algebraically from chain data. This was considered and
  dropped: handles cost +32 bytes per reader per output, handle-based decryption lands on `v·H`
  and therefore forces a bounded amount space with a precomputed discrete-log lookup table
  (client-side, megabytes), and under the single-viewing-key model the handles buy nothing — the
  Diffie–Hellman transport already delivers the amount *and* its blinding to every holder of
  `sk_view` in constant time, with full 64-bit amounts. Handle-based designs remain the right
  choice for account-based ledgers, where decryption must operate homomorphically over an
  aggregated balance; the EUTXO model decrypts outputs individually, so that constraint does not
  apply here.
- **Reveal amounts to the recipient out of band, commitments only.** Viable, but pushes amount
  delivery to a side channel and precludes verifiable on-chain auditor disclosure; the
  Diffie–Hellman transport keeps everything on chain and self-contained.
- **General-purpose succinct proofs (zk-SNARK/STARK) over an encrypted note pool.** These can hide
  more (including identities and the graph) but require either a trusted setup or heavier proving,
  a proving circuit, and additional state (note commitments and nullifiers). They are a
  substantially larger change and hide more than this proposal aims to; they are noted as possible
  future or complementary directions.
- **Fully homomorphic encryption.** Overkill for value transfer, with impractical on-chain
  verification cost; not pursued.

### Backward compatibility

The feature is opt-in and additive. Transactions that do not use confidential outputs are
unaffected, and transparent value continues to work exactly as today. Confidential and transparent
value coexist within a transaction via the shield/unshield bridge. Activation requires a protocol
change (see Path to Active).

### Open Questions

- **Programmable tokens (CIP-113).** Interaction with programmable/regulated tokens — whose
  transfer logic may need to inspect amounts — is **out of scope for this proposal** and is left
  as an open question. A confidential quantity is not visible to such logic, so reconciling amount
  confidentiality with amount-dependent transfer policies needs separate design.
- **Hiding asset type.** This proposal hides quantities but not which asset moves. Hiding the
  asset type as well is significantly harder and is left for future work.
- **Binding `P_view` to an account (stake credential).** The exact mechanism to publish and bind
  the account's single viewing public key to its stake credential (a new address/stake component,
  an on-chain registration, or a wallet-level convention) is to be specified — including how a
  sender learns the recipient account's `P_view` and how key rotation is handled.
- **Viewing-key derivation path.** The dedicated hierarchical-deterministic path for `sk_view`
  (a new role index under [CIP-1852], or a separate purpose) needs to be standardised so that
  wallets derive the same key from the same seed interoperably; hardware-wallet firmware support
  for deriving the key and computing the Diffie–Hellman shared secret is part of this question.
- **Balancing-proof form.** A single Schnorr excess signature per asset versus per-output
  consistency proofs — a size/verification trade-off — to be finalised.
- **Multi-party transactions.** Constructing the balancing proof requires the builder to know all
  input and output blindings; collaborative transactions with multiple independent contributors
  need either interaction or partial balancing proofs. Whether to support this initially is open.
- **Range bit-width and aggregation limits.** Confirm `2⁶⁴` and the maximum number of committed
  values (hence assets/outputs) per transaction consistent with a verification-cost budget.
- **Fee treatment.** Fees are public in this design; whether any future variant could hide fees is
  out of scope here.
- **Staking in zero knowledge.** In this proposal confidential ADA does not contribute to stake,
  rewards, or governance voting power (§9). Whether hidden amounts could be counted toward the
  stake distribution without revealing them is left as future work.
- **Script addresses.** Confidential outputs are restricted to key-locked addresses (§4).
  Extending them to script-locked outputs — including what a validator script may learn about a
  hidden amount — is open, and related to the programmable-tokens question above.

## Path to Active

### Acceptance Criteria

- [ ] The design (primitives, transaction/output structure, proofs, and validation rules) is
      reviewed and **ratified by the community** through the CIP process, including review by
      relevant ledger and cryptography stakeholders.
- [ ] A complete, versioned specification of the on-chain structures (final CDDL) and the proving
      and verification procedures, sufficient for **independent, interoperable implementations**.
- [ ] Published **test vectors** (valid and invalid transactions, including the edge cases in
      §11) that any implementation must agree on.
- [ ] An independent **security review / audit** of the cryptographic construction and its
      encoding.
- [ ] Implementation present within block-producing nodes used by **80%+ of stake**, activated
      via the standard protocol-parameter/hard-fork governance process.

### Implementation Plan

- Produce a reference specification and test vectors for the primitives and proofs described here.
- Prototype the verification rules against the specification and validate them on the test
  vectors.
- Commission a security audit of the construction and encoding.
- Propose activation through the on-chain governance process once implementations are available.

## Appendix

### Worked example

A confidential ADA payment from account **A** to account **B**, with change back to **A** and a
public fee. This illustrates what is hidden, what is public, and how the checks fit together.

**Setup.** Account A owns one confidential input committing to `v_in` lovelace:
`C_in = v_in·H + r_in·G`. A knows `(v_in, r_in)` from having received it (§5). A wants to send
`v_send` to B, keep `v_change`, and pay a public fee `f`, with `v_in = v_send + v_change + f`.

**A builds the transaction:**

1. Output to B: `C_send = v_send·H + r_send·G`, with ephemeral key `E₁ = e₁·G`. From the shared
   secret `s₁ = e₁·P_view(B)` the sender derives `r_send` and a keystream, and stores the 8-byte
   masked amount `v_send ⊕ keystream` in the output (§5).
2. Change to A: `C_change = v_change·H + r_change·G`, with ephemeral key `E₂ = e₂·G`,
   `s₂ = e₂·P_view(A)`, and its own masked amount.
3. Fee `f` is left **public**.
4. **Range proof:** one aggregated Bulletproofs proof that `v_send` and `v_change` are each in
   `[0, 2⁶⁴)`, including the shifted commitments `C − min·H` for the minimum-ADA floor (§6).
5. **Balancing:** compute `excess = r_in − r_send − r_change`. Then
   `C_in − C_send − C_change − f·H = excess·G` (the value terms cancel because
   `v_in − v_send − v_change − f = 0`). A includes a Schnorr signature under public key `excess·G`.

**What a validator checks** (never seeing any amount): encodings are canonical; the aggregated
range proof verifies; the balancing equation holds and its Schnorr signature verifies; the spend
of `C_in` is authorised by A's normal key witness. If any amount had been inflated, the value
terms would not cancel and the balancing check would fail.

**What is public:** A's and B's addresses, the fact of the transfer, the fee `f`, the ephemeral
keys, the commitments, and the proofs. **What is hidden:** `v_in`, `v_send`, `v_change`.

**Recipient.** B inspects the outputs at its (public) addresses, computes `s₁ = sk_view(B)·E₁`,
derives `r_send` and the keystream, recovers `v_send` from the stored masked amount, and verifies
`C_send == v_send·H + r_send·G`. B now holds a spendable confidential UTXO.

**Auditor.** Given A's single account viewing key `sk_view(A)`, an auditor recomputes the shared
secret for every output addressed to A (here, the change) and reads all of A's amounts — a full
account view for tax/audit purposes.

**Native token variant.** If the output to B also carried `q` units of a token `(policy, name)`,
the output would include an additional commitment `C_T = q·H + r_T·G` for that asset, the range
proof would also cover `q`, and a **separate** balancing equation and Schnorr signature would be
required for that asset. The token's identity `(policy, name)` stays public; only `q` is hidden.

## References

- [RFC 9496 — The ristretto255 and decaf448 Groups][rfc9496]
- [Bulletproofs: Short Proofs for Confidential Transactions and More (Bünz, Bootle, Boneh, Poelstra, Wuille, Maxwell, 2018)][bulletproofs]
- Confidential Transactions (G. Maxwell) — commitment-based amount hiding with value conservation.
- T. P. Pedersen, "Non-Interactive and Information-Theoretic Secure Verifiable Secret Sharing," CRYPTO 1991.
- C. P. Schnorr, "Efficient signature generation by smart cards," Journal of Cryptology, 1991.
- A. Fiat and A. Shamir, "How to prove yourself: practical solutions to identification and signature problems," CRYPTO 1986.

[rfc9496]: https://www.rfc-editor.org/rfc/rfc9496
[CIP-1852]: https://github.com/cardano-foundation/CIPs/tree/master/CIP-1852
[bulletproofs]: https://eprint.iacr.org/2017/1066

## Acknowledgements

<!-- To be completed. -->

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
