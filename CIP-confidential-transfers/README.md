---
CIP: "?"
Title: Native Confidential Transfers
Category: Ledger
Status: Proposed
Authors:
    - Mateusz Czeladka <mateusz.czeladka@cardanofoundation.org>
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

### Overview

A **confidential output** replaces the cleartext amount of each asset it holds with a homomorphic
**commitment** to that amount, plus a small piece of data that lets the recipient recover the
amount. A transaction that produces or consumes confidential outputs carries a **confidential
proof** demonstrating, in zero knowledge, that:

1. every hidden amount is a valid, non-negative quantity within range, and
2. for **each asset independently**, the hidden inputs, hidden outputs, public movements
   (fees, mint/burn, and any transparent inputs/outputs) balance exactly.

Spending a confidential output is authorised exactly as today — by the address's key witness.
Amount confidentiality is orthogonal to spend authorisation.

### Cryptographic primitives and parameters

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
  secret let the recipient recover the amount and derive its blinding (see [amount transport](#amount-transport)).
- **Balancing proof.** A **Schnorr** signature proving knowledge of the *excess* blinding of a
  commitment to zero value, establishing value conservation per asset (see [value conservation](#value-conservation)).
- **Non-interactivity.** All proofs are made non-interactive with the **Fiat–Shamir** transform,
  using a cryptographic hash and a **domain-separation tag (DST)** bound to the transaction
  context. DSTs are namespaced and versioned: every tag defined by this proposal has the form
  `cardano/ct/<proof>/v<n>`, where `<n>` equals the CDDL alternative tag of the structure being
  proven — concretely `cardano/ct/range/v0` for the aggregated range proof and
  `cardano/ct/balancing/v0` for the per-asset excess signatures. A proof therefore verifies only
  in its intended context and under its intended version: the same bytes can never validate as a
  different proof kind, under a different proof-system version, or in a protocol that reuses
  these primitives. Companion proposals MUST NOT reuse the tags defined here; each allocates its
  own under a distinct path segment (for example `cardano/ct/predicate/v0` for a future
  script-predicate proof). The exact transcript byte encoding (tag placement, field ordering,
  serialisation of the bound transaction context) is part of the final specification and its
  test vectors (see Path to Active).

No trusted setup is required by any of these primitives.

### Keys

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
  Whatever mechanism is chosen, it MUST work uniformly for **any** stake credential type — key
  hash or script hash — and MUST NOT assume the existence of a single stake signing key:
  authorisation follows the credential's standard witness rules, so that script-controlled
  accounts (e.g. multisig treasuries) can bind a viewing key exactly as key-controlled accounts
  do.
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

### Confidential value representation

An asset is identified publicly by `(policy_id, asset_name)`; ADA (lovelace) is treated as a
reserved, distinguished asset. A **confidential value** reveals *which* assets are present but
hides each asset's *quantity* as a Pedersen commitment:

- ADA quantity `v` → `C = v·H + r·G`.
- Each native-asset quantity `q` under `(policy_id, asset_name)` → `C = q·H + r·G`.

[Conservation](#value-conservation) and [range proofs](#range-proofs) are applied **per asset**.

An output is either fully **transparent** (exactly as today) or fully **confidential**; the two
forms do not mix within a single output. Every confidential output **must** include an ADA
commitment, whose quantity is subject to the minimum-ADA rule enforced in zero knowledge (see [range proofs](#range-proofs)).
In this proposal, confidential outputs are restricted to **key-locked (payment-key) addresses**;
outputs at script addresses cannot be confidential (see Open Questions).

### Amount transport

To spend a confidential output, its owner must know the hidden amount **and** its blinding `r`.
Both are conveyed with a Diffie–Hellman shared secret plus a small stored ciphertext:

1. The sender picks a fresh ephemeral scalar `e` and includes the ephemeral public key `E = e·G`
   in the output. `E` must not be the identity element — a predictable shared secret would expose
   the amounts — and validators reject it (see [validation rules](#validation-rules-edge-cases-and-soundness), rule 1).
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
the output (construct the balancing proof of [value conservation](#value-conservation)) **without any interaction** with the original
sender. An auditor given `sk_view` recovers all amounts for the account by the same computation.
Note that the **sender** also retains knowledge of `(v, r)` for outputs it creates — inherent to
Diffie–Hellman transport — but this grants no spend authority, which requires the recipient's
spending key.

### Range proofs

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

### Value conservation

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

### Bridging transparent and confidential amounts (shield / unshield)

Confidential amounts must be backed one-to-one by real value. **Shielding** (making transparent
value confidential) and **unshielding** (revealing confidential value back to transparent) are
not special operations: they are ordinary transactions that mix transparent and confidential
inputs and outputs. All transparent components are public, so the net public movement `Δ` of
each asset (see [value conservation](#value-conservation)) is computed directly from the transaction's public data — transparent inputs and
outputs, the fee, and any mint or burn — and the per-asset balancing equation then enforces that
the confidential side absorbed or released **exactly** that amount. No separate opening proofs
are needed: hidden amounts that do not match the public legs cannot satisfy the balancing
equation without a negative hidden output, which the range proofs forbid.

The total confidential supply of each asset equals (total shielded − total unshielded) — a
public quantity — so the confidential pool is conservation-checked against transparent value at
every step, and no asset can be minted by hiding it. The transparent legs of such transactions
are the only places where amounts entering or leaving the confidential domain are revealed.

### Staking, rewards, and governance

Cardano's stake distribution — used for leader election, rewards, and governance voting power —
is computed from publicly visible ADA amounts. A hidden amount cannot contribute to that
computation without revealing information about itself. In this proposal, therefore:

- **Confidential ADA does not contribute to stake.** ADA held in confidential outputs is
  excluded from the stake of the associated stake credential, from reward calculation, and from
  governance voting power — including the ADA-weight of any **DRep vote delegation** and of SPO
  votes — for as long as it remains confidential.
- **Unshielding restores participation.** Once ADA is returned to a transparent output, it
  counts toward stake, rewards, and voting power exactly as today.

This is an explicit, accepted opportunity cost of confidentiality. Contributing hidden amounts
to the stake distribution in zero knowledge is substantially more complex and is left as future
work (see Open Questions).

### Transaction and output structure (CDDL)

The following CDDL is **illustrative** and describes the additional structures at a design level;
concrete field indices and integration with the existing transaction CDDL are to be finalised
during implementation.

```cddl
; A canonically-encoded ristretto255 point / scalar, 32 bytes each (RFC 9496).
ristretto_point = bytes .size 32
scalar32        = bytes .size 32

commitment      = ristretto_point      ; Pedersen commitment C = v·H + r·G
masked_amount   = bytes .size 8        ; v XOR keystream; recoverable with sk_view (see Amount transport)

; A hidden quantity, as a tagged alternative (cf. Babbage's datum_option).
; Alternative 0 = Pedersen commitment + DH masked amount (this proposal).
; Future commitment schemes — per-asset generators for asset-type blinding,
; post-quantum commitments — are added as new alternatives under a later
; protocol version; an output in the UTXO set therefore always self-describes
; which scheme its hidden quantities use.
confidential_asset = [ 0, commitment, masked_amount ]

; Confidential value: which assets are present is public; every quantity is hidden.
; The lovelace entry (key 0) is mandatory: every output must satisfy minimum-ADA
; (see Range proofs).
confidential_value =
  { 0   : confidential_asset                                       ; lovelace
  , ? 1 : { policy_id => { asset_name => confidential_asset } }    ; native assets
  }

; A confidential output, as a map with numbered keys (cf. the Babbage output
; format): later proposals extend it by adding new optional keys, without
; disturbing keys 0-2. `address` is the ledger's existing address type and is
; deliberately unrestricted here — the key-locked-addresses-only rule (see
; Confidential value representation) is a validation rule, which a later
; proposal may relax, not a data-format restriction.
confidential_output =
  { 0 : address
  , 1 : confidential_value
  , 2 : ristretto_point        ; ephemeral key E = e·G (see Amount transport)
  }

; A Schnorr signature (R, s) proving knowledge of the per-asset excess (see Value conservation).
schnorr_sig = [ ristretto_point, scalar32 ]

; Proof components are tagged alternatives, so the proof system can evolve
; independently of the data it proves (see Versioning).
range_proof     = [ 0, bytes ]                         ; 0 = aggregated Bulletproofs
balancing_proof = [ 0, { asset_ref => schnorr_sig } ]  ; 0 = per-asset Schnorr excess

; Per-transaction confidential proof, carried in the witness set.
; Shield/unshield need no dedicated structures: the public movement of each asset is
; computed from the transaction's public data and enters the balancing check (see Bridging transparent and confidential amounts).
confidential_proof =
  { 0 : range_proof
  , 1 : balancing_proof
  }

policy_id  = bytes .size 28
asset_name = bytes .size (0..32)
asset_ref  = 0 / [ policy_id, asset_name ]     ; 0 denotes ADA (lovelace)
```

### Validation rules, edge cases and soundness

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
   balancing equation of [value conservation](#value-conservation) holds and its Schnorr excess signature verifies. This guarantees, for
   every asset, that hidden outputs plus public movements equal hidden inputs — i.e. the net
   created value is exactly zero. Combined with rule 2, no value can be created and no negative
   output can exist.
4. **Minimum quantity.** For any output subject to minimum-ADA, the aggregated range proof also
   covers the shifted commitment `C − min·H` (see [range proofs](#range-proofs)), proving `v ≥ min`; outputs that cannot prove
   this are rejected. This preserves anti-dust and related economic rules despite hidden amounts.
5. **Transparent–confidential bridging.** The public net movement `Δ` of each asset is computed
   from the transaction's public data only (transparent inputs and outputs, fee, mint/burn) and
   enters that asset's balancing equation (see [value conservation](#value-conservation)). Hidden amounts that do not match the public legs
   cannot balance without a negative hidden output, which rule 2 forbids — so no separate
   opening proofs are required for shielding or unshielding (see [shield / unshield](#bridging-transparent-and-confidential-amounts-shield--unshield)).
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
9. **Unknown forms rejected.** A confidential structure carrying an alternative tag or map key
   not defined at the current protocol version is invalid. Rejecting unknown forms today is what
   allows a later protocol version to activate new tags and keys (see [versioning](#versioning))
   without any ambiguity about how older validators treat them.
10. **No Plutus execution alongside confidential components.** A transaction that contains
    confidential inputs or outputs must not execute Plutus scripts (for any purpose — spending,
    minting, or otherwise). Current script contexts represent every output with a cleartext
    amount and cannot represent a hidden quantity, and a script must never validate blind to
    parts of the transaction it is checking. Consequently, bridging (shield/unshield) is always
    a separate transaction from any script interaction, and mint/burn of Plutus-policy assets
    happens in a separate transaction from confidential transfers of them. Native scripts are
    unaffected as witnesses on *transparent* inputs (they enforce signature and time conditions
    without inspecting amounts), though confidential outputs at native-script addresses remain
    excluded by the key-locked rule (see
    [confidential value representation](#confidential-value-representation)). Defining a
    script-context representation of hidden quantities is deferred to a future proposal (see
    Open Questions).

### Guarantees to future proposals

This proposal is designed to be built upon. The following properties of the confidential
transfer layer are **normative guarantees**, on par with the validation rules above: companion
proposals may rely on them, and any future amendment to this specification that would break
one of them is a **breaking change** — it must be introduced as a new versioned form (a new
alternative tag or map key under a later protocol version, see [versioning](#versioning)) and
must never alter the behaviour of existing forms in place.

1. **Representation.** Every hidden quantity is a Pedersen commitment over ristretto255 under
   the fixed generators `G` and `H`, and the commitment itself is stored in the clear in the
   output — never hashed, truncated, or otherwise made unavailable to chain observers.
2. **Summability.** The commitments of any set of confidential outputs can be added by any
   observer, per asset, yielding a commitment to the sum of the hidden quantities.
3. **Attribution.** Which stake credential a confidential output belongs to remains publicly
   determinable from chain data.
4. **Openings.** The owner of a confidential output recovers its opening `(v, r)` from chain
   data and the account's `sk_view` alone, with no interaction with the sender and no
   off-chain state.
5. **Independent conservation.** Each asset's balancing check is verifiable from the
   transaction alone, without reference to hidden state elsewhere on the chain.

These guarantees are precisely what the extensions anticipated under
[Future extensions and upgrade paths](#future-extensions-and-upgrade-paths) consume:
summability and attribution make voting-weight commitments publicly derivable (governance);
summability and openings enable provable opening of aggregates (staking); attribution and
openings keep disclosure-based audit tooling scan-free; openings underpin multi-party
balancing-proof construction.

### Auditing and selective disclosure

Because only *amounts* are hidden and the transaction graph is public, disclosing an account's
single `sk_view` (one key for the whole account, i.e. the stake address — see [Keys](#keys)) gives the holder of
that key a complete, human-readable history of the **entire account** across all its payment
addresses — which counterparties, which assets, and how much — recovered by the computation of [amount transport](#amount-transport).
This supports auditing and tax reporting: the account owner, of their own volition, hands the
single `sk_view` to **one or more auditors of their choosing** — a tax authority, an accountant,
or tax-reporting software. Disclosure is
verifiable (the disclosed key can be checked against the published `P_view`) and grants read access
only. Whether disclosure is on request or mandatory in some contexts is a policy matter outside
this specification.

Recovering an account's amounts from `sk_view` requires **no chain-wide scanning or trial
decryption**: because addresses are public, an auditor or tool needs only the outputs already
indexed for the account's addresses, plus one Diffie–Hellman computation per output (see [amount transport](#amount-transport)).
Disclosure-based auditing therefore composes directly with existing address-indexing
infrastructure.

### Versioning

The feature is gated by the protocol version and is inert below its activation version. The
on-chain structures defined here are versioned so that future revisions of the proof system
(for example, a newer range-proof construction) can be introduced under a new version while
older transactions continue to verify under the version they were created with.

Versioning uses the ledger's own idioms rather than in-band version fields (no ledger
structure on Cardano carries a `version` integer, and this proposal follows that practice).
**Incompatible** new forms — a new commitment scheme, a new range-proof or balancing-proof
construction — are added as new alternatives to the tagged unions in the CDDL
(`confidential_asset`, `range_proof`, `balancing_proof`); **additive** extensions arrive as
new numbered keys in the `confidential_output` and `confidential_proof` maps. Which tags and
keys are valid is determined solely by the protocol version (validation rule 9). The
domain-separation tags of the Fiat–Shamir transform mirror the same versioning: each
proof-system alternative carries its own DST (`cardano/ct/<proof>/v<n>`, see
[cryptographic primitives](#cryptographic-primitives-and-parameters)), so a proof produced for
one alternative can never verify under another — cross-version replay is excluded by
construction, not by convention. Because
outputs live in the UTXO set across protocol versions, every confidential output
self-describes its form: outputs created under an older version remain spendable and
interpretable unchanged after an upgrade.

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

- **Transaction size — and therefore ADA fees.** Confidential transactions are larger than
  transparent ones — roughly **3–5×** for typical small payments — dominated by the (near-fixed)
  aggregated range proof, and growing with the number of distinct assets whose amounts are hidden
  (each asset needs its own commitment and range contribution). Because Cardano's fee formula is
  proportional to transaction size, a typical confidential payment can be expected to cost
  roughly **3–5× the ADA fee** of its transparent equivalent. Confidentiality is paid for by the
  user who opts into it, not by the network.
- **Size-proportional fees do not price verification.** Cardano's fee formula prices *bytes*;
  script execution is priced separately through execution units, but the proofs defined here are
  verified by the ledger itself, not by a script, so under the current formula their verification
  CPU rides along unpriced. The mismatch is structural: an aggregated range proof grows only
  *logarithmically* in size with the number of committed values, while its verification time
  grows *linearly* — so a heavily aggregated transaction pays barely more per byte while costing
  proportionally more CPU. Mempool pre-checks (see the
  [Appendix](#estimated-node-resource-impact)) bound abuse, but pricing honest usage correctly —
  whether proof verification should carry an explicit fee term, analogous to execution-unit
  pricing — is left open (see Open Questions).
- **Verification cost.** Range-proof verification cost grows with the number of committed values;
  aggregation and batch verification mitigate this, but it remains higher than validating a
  transparent amount — roughly an order of magnitude more CPU per transaction than signature
  checking, while leaving overall node hardware requirements unchanged. Order-of-magnitude
  estimates are given in the [Appendix](#estimated-node-resource-impact); measured benchmarks are
  an acceptance criterion (see Path to Active).
- **Not post-quantum.** Security rests on the elliptic-curve discrete-logarithm and DDH
  assumptions and is not resistant to a future cryptographically-relevant quantum computer;
  amounts recorded today could in principle be recovered by such an adversary
  ("harvest-now-decrypt-later"). This is an accepted trade-off for a fast, small, trusted-setup-free
  design; post-quantum confidentiality is left for future work.
- **Asset type is public.** Only quantities are hidden; the presence and identity of assets in an
  output remain visible.
- **Confidential ADA does not stake.** ADA in confidential outputs is excluded from stake,
  rewards, and governance voting power — including DRep vote-delegation weight — while it remains
  hidden (see [staking, rewards, and governance](#staking-rewards-and-governance)). This is an opportunity cost holders accept when shielding, and a deliberate point
  for community discussion: whether and when hidden ADA should regain staking or governance
  participation is addressed under Open Questions.
- **Confidential value cannot interact with smart contracts while hidden.** Confidential
  outputs exist only at key-locked addresses, and a transaction carrying confidential
  components does not execute Plutus scripts (validation rule 10). While value is hidden it is
  therefore *transfer-only*: plain payments (with metadata), but no participation in anything
  mediated by smart validators on the Plutus VM — whatever the application built on them — on
  top of the staking and governance exclusion above. This is **not a one-way door**: shielding
  and unshielding are ordinary, permissionless transactions available at any time (see
  [shield / unshield](#bridging-transparent-and-confidential-amounts-shield--unshield)), so the
  path to script interaction is unshield → interact transparently → optionally shield the
  proceeds back. Each crossing reveals only the bridged amount, never the remaining
  confidential balance — though timing correlation between an unshield and an immediately
  following script interaction can link the two. Wallets should surface this trade-off clearly
  before users shield funds.
- **Auditor-facing tooling does not exist yet.** As of this writing, no mainstream tax or
  accounting software supports viewing-key import for *any* chain; users of existing privacy
  systems instead export a transaction history (e.g. CSV) from their wallet and import that, and
  the same fallback applies here from day one. Direct viewing-key support in such tools may or
  may not materialise — until it does, producing auditor-readable reports is the wallet's job,
  which is an ongoing complexity cost for users and companies relying on the audit path. The
  design deliberately minimises what a third-party tool must implement — amounts are recoverable
  from already-indexed outputs with one Diffie–Hellman computation each, with no chain-wide
  scanning (see [auditing and selective disclosure](#auditing-and-selective-disclosure)) — but adopters should treat third-party tooling support as an ecosystem
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

### Future extensions and upgrade paths

This proposal is deliberately narrow: amount confidentiality, one viewing key, key-locked
addresses. This section records, for each anticipated extension, whether an upgrade path exists,
whether the present design conflicts with it, and why it is descoped now. The goal is **not** to
design these extensions, but to let the community judge — before ratifying — that today's small
design choices keep tomorrow's doors open rather than closing them. A guiding principle
throughout: confidential outputs remain **homomorphically summable Pedersen commitments,
publicly bound to stake credentials, whose openings their owners keep** — nothing about the
transfer layer destroys information a future extension would need. This principle is not
merely aspirational: it is normative, as the
[guarantees to future proposals](#guarantees-to-future-proposals) in the Specification.

**Each extension below is anticipated as an independent companion CIP layered on top of this
proposal — not as a bundled successor version.** They are separable by design: staking and
governance add machinery *around* the commitments this proposal creates, without changing the
transfer layer; asset-type blinding and post-quantum migration arrive as new **versioned**
output and proof forms (see [versioning](#versioning)); address hiding, if ever pursued, would be a coexisting pool.
Smaller follow-ups also expected as narrow companion proposals: standardisation of the
viewing-key derivation path, support for script-locked confidential outputs (starting with
native scripts — multisig and timelocks — which enforce witness conditions without inspecting
amounts), and multi-party transaction construction (see Open Questions).

#### Staking shielded ADA

*Upgrade path:* the most concrete sketch reuses this proposal's own machinery. Delegation
converts shielded ADA into **pool-specific delegation tokens** whose quantities are hidden by
this very proposal's confidential native-asset mechanism, with rewards accruing through a public
per-epoch **exchange rate** — so no per-member reward computation ever occurs (the pattern
deployed in production by Penumbra). The per-pool totals that leader election requires in the
clear can then be produced at three levels of ambition: **(a)** delegators share their openings
with their chosen pool, which publishes and provably opens the per-epoch aggregate — no new
cryptography at all; **(b)** the same aggregate opened by a **threshold committee** instead, so
no single party learns member amounts — a drop-in upgrade of (a); or **(c)** never opened —
leader election proven in zero knowledge against the committed total
([Ganesh–Orlandi–Tschudi][got], a model whose required public stake-commitment list this design
*already provides*; or, at the maximalist end, [Ouroboros Crypsinous][crypsinous]).
**None of the three requires a trusted setup:** (a) and (b) introduce no new proof system, and
(c) is achievable with transparent proof systems. Every variant additionally needs
epoch-snapshot rules over confidential outputs.

*Conflict with this design:* **none.** Paths (a)–(c) build directly on the commitments this
proposal creates, and (a) upgrades into (b) without redesign. Crypsinous specifically is **not
in conflict either**: it would be a separate, parallel shielded pool plus a consensus-layer
change, coexisting with this design (bridgeable via shield/unshield) rather than replacing it;
this proposal neither blocks nor requires it. One leakage caveat applies to any variant with
public per-pool totals: because pool *membership* is public here (addresses and delegation
certificates are transparent), epoch-to-epoch differences can reveal an individual amount when
few members change — the anonymity set is the pool's per-epoch churn. Stronger privacy would
require hiding the delegation link itself, which is graph-hiding territory (see *Hiding
addresses* below).

*Why descoped:* every path adds consensus-adjacent machinery, new trust assumptions
(committees), or the aggregate-level leakage above, deserving a dedicated companion CIP and its
own community debate; the per-UTXO exclusion rule (see [staking, rewards, and governance](#staking-rewards-and-governance)) is the minimal safe v1 behaviour.

#### Governance and DRep voting with shielded ADA

*Upgrade path:* because ownership is public, an account's ADA-weighted **voting-weight
commitment is already publicly derivable** (the homomorphic sum of its output commitments). The
missing piece is opening only *tallies*, never individual weights — standard homomorphic-tally
techniques (threshold decryption of totals, or aggregate opening proofs), plus snapshot rules.

*Conflict with this design:* **none** — arguably the easiest extension, precisely because public
attribution makes weight commitments free. The genuinely new ingredient is a tally-opening
mechanism (e.g. a decryption committee), which is a new trust assumption for Cardano governance.

*Why descoped:* that trust assumption merits its own community debate; v1 excludes hidden ADA
from voting power (see [staking, rewards, and governance](#staking-rewards-and-governance)) until it happens.

#### Hiding the asset type (policy id and asset name)

*Upgrade path:* blinded asset tags in the style of [Confidential Assets][conf-assets]: each
quantity committed under an asset-derived generator, with proofs that hidden tags are legitimate
and that conservation cannot cancel across assets. Mint/burn authorisation — currently tied to a
public policy — needs rethinking.

*Conflict with this design:* **partial restructuring, not contradiction.** The single value
generator `H` and per-asset public-tag conservation (see [value conservation](#value-conservation)) are the right choice *while asset
identity is public* (see Rationale); a tag-blinding upgrade would introduce a **new, versioned
output form** (see [versioning](#versioning)) with per-asset generators, and existing confidential outputs would migrate by
unshield/re-shield. Nothing in v1 has to be broken in place.

*Why descoped:* substantially harder cryptography, larger proofs, and most compliance-oriented
use cases require the asset type visible anyway.

#### Programmable tokens (CIP-113) and token standards (CIP-26 / CIP-68)

*Upgrade path:* programmable tokens keep the underlying native asset **permanently at
validator-controlled (script) addresses**, with every transfer mediated by the controlling
script. Making such tokens confidential would therefore require three things: **(1)**
confidential outputs at script addresses (see the script-address follow-up under Open
Questions); **(2)** a script-context extension so validator scripts receive commitments where
they receive amounts today; and **(3)** **zero-knowledge predicates** verified by the script
against the commitment — but *only for amount-dependent policies*. Notably, most
programmable-token policies are **identity- and credential-based** (freeze, blacklist,
whitelist, authorised-transfer checks) and read addresses and datums, which remain **public** in
this design — such policies would work over confidential outputs unchanged. Only policies that
read the quantity itself (transfer limits, proportional fees) need the ZK-predicate machinery.
Metadata standards are orthogonal: CIP-26 is off-chain, and CIP-68's reference-NFT/datum
machinery is unaffected by hiding user-held quantities.

*Conflict with this design:* **none — the two are disjoint by construction in v1.** A
programmable token cannot leave script control, and this proposal's confidential outputs cannot
exist at script addresses (see [confidential value representation](#confidential-value-representation)); each side's rule independently guarantees that no programmable
token can be shielded and no programmable-token validator ever encounters a hidden quantity.
There is no interaction surface, no carve-out to implement, and no retroactive state a future
programmable-token standard would have to accommodate.

*Why descoped:* programmable-token semantics (CIP-113) are themselves still being standardised;
ZK predicates over commitments should be co-designed with them, not pre-empted here.

#### Post-quantum security

*Upgrade path:* replace each primitive with a post-quantum counterpart — lattice-based
commitments and range proofs, a PQ KEM in place of the Diffie–Hellman transport, a PQ proof of
knowledge for the balancing proof — under a new proof-system version (see [versioning](#versioning)); value migrates by
unshield/re-shield.

*Conflict with this design:* **none architecturally** — the structure (commitments +
conservation + range proofs + viewing keys) is proof-system-agnostic and the [versioning](#versioning) section anticipates
versioned upgrades. The honest, unavoidable caveat is **harvest-now-decrypt-later**: amounts
hidden under the v1 discrete-log scheme remain recoverable by a future quantum adversary
regardless of any later migration; migration protects future outputs only. This is already
declared in Trade-offs.

*Why descoped:* today's post-quantum equivalents are far larger and slower (conflicting with the
"fast" requirement), and the ledger's own signatures are not post-quantum either — a chain-wide
PQ migration is a broader effort than this proposal.

#### Hiding addresses (who transacted with whom)

*Upgrade path:* receiver unlinkability needs stealth/one-time addresses; sender ambiguity needs
ring signatures or a note-and-nullifier shielded pool. The auditor model would need rebuilding so
the viewing key also reveals counterparties (as Monero and Zcash viewing keys do).

*Conflict with this design:* **this is the extension in most tension with v1** — several v1
properties deliberately exploit public addresses: targeted wallet scanning without trial
decryption, publicly derivable voting-weight commitments, low-cost auditor tooling (see [auditing and selective disclosure](#auditing-and-selective-disclosure)), and
staking attribution. A graph-hiding upgrade would forfeit or rebuild those. It is nonetheless
**not foreclosed**: the amount-confidentiality layer (commitments, conservation, range proofs)
is exactly the amount layer used inside graph-hiding designs, and a shielded pool could be added
*alongside* this design as a separate output type — as transparent and shielded pools coexist in
Zcash — rather than by modifying it.

*Why descoped:* an explicit non-goal (see [Motivation](#motivation-why-is-this-cip-necessary)): this proposal's compliance-first positioning —
confidentiality from the public, not from oversight — depends on the graph remaining public, and
identity hiding would move it into a different regulatory and design category.

### Open Questions

Longer-horizon extensions — staking and governance participation of shielded ADA, hiding the
asset type, programmable tokens, post-quantum security, and address hiding — are analysed in
[Future extensions and upgrade paths](#future-extensions-and-upgrade-paths) above. The open
questions below concern the v1 design itself.

- **Binding `P_view` to an account (stake credential).** The exact mechanism to publish and bind
  the account's single viewing public key to its stake credential (a new address/stake component,
  an on-chain registration, or a wallet-level convention) is to be specified — including how a
  sender learns the recipient account's `P_view` and how key rotation is handled. The leading
  candidate is an on-chain registration **certificate**, alongside the existing stake-key
  certificates. Whatever form is chosen, it must satisfy the credential-type-neutrality
  constraint of [Keys](#keys): key-hash and script-hash stake credentials alike, authorised by
  the credential's standard witness rules, with rotation available to both.
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
  out of scope here. Separately, whether proof **verification cost** should carry an explicit fee
  term — a per-committed-value or per-range-statement price, analogous to script execution-unit
  pricing — or remain covered by size-proportional fees alone is open; the aggregated range
  proof's logarithmic size versus linear verification time (see Trade-offs) is the argument for
  an explicit term.
- **Script addresses.** Confidential outputs are restricted to key-locked addresses (see [confidential value representation](#confidential-value-representation)).
  Extending them to script-locked outputs — including what a validator script may learn about a
  hidden amount — is open. A natural first step is **native scripts** (multisig and timelocks),
  which enforce witness and time conditions without inspecting amounts — important for corporate
  treasuries — and could form a narrow, early companion proposal; Plutus scripts raise the
  amount-visibility questions discussed under Future extensions (programmable tokens). Until a
  script-context representation of hidden quantities is defined there, validation rule 10 keeps
  Plutus execution and confidential components in strictly separate transactions.

## Path to Active

### Acceptance Criteria

- [ ] The design (primitives, transaction/output structure, proofs, and validation rules) is
      reviewed and **ratified by the community** through the CIP process, including review by
      relevant ledger and cryptography stakeholders.
- [ ] A complete, versioned specification of the on-chain structures (final CDDL) and the proving
      and verification procedures, sufficient for **independent, interoperable implementations**.
- [ ] Published **test vectors** (valid and invalid transactions, including the edge cases in
      [validation rules](#validation-rules-edge-cases-and-soundness)) that any implementation must agree on.
- [ ] An independent **security review / audit** of the cryptographic construction and its
      encoding.
- [ ] Published **performance benchmarks** of verification cost — per transaction and per block,
      batched and unbatched, including full-sync replay impact — demonstrating that
      block-validation budgets are met (replacing the derived estimates in the Appendix).
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
`C_in = v_in·H + r_in·G`. A knows `(v_in, r_in)` from having received it (see [amount transport](#amount-transport)). A wants to send
`v_send` to B, keep `v_change`, and pay a public fee `f`, with `v_in = v_send + v_change + f`.

**A builds the transaction:**

1. Output to B: `C_send = v_send·H + r_send·G`, with ephemeral key `E₁ = e₁·G`. From the shared
   secret `s₁ = e₁·P_view(B)` the sender derives `r_send` and a keystream, and stores the 8-byte
   masked amount `v_send ⊕ keystream` in the output (see [amount transport](#amount-transport)).
2. Change to A: `C_change = v_change·H + r_change·G`, with ephemeral key `E₂ = e₂·G`,
   `s₂ = e₂·P_view(A)`, and its own masked amount.
3. Fee `f` is left **public**.
4. **Range proof:** one aggregated Bulletproofs proof that `v_send` and `v_change` are each in
   `[0, 2⁶⁴)`, including the shifted commitments `C − min·H` for the minimum-ADA floor (see [range proofs](#range-proofs)).
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

### Estimated node resource impact

The figures below are **order-of-magnitude estimates**, derived from published benchmarks of the
underlying primitives and this proposal's parameters; they are informative, not normative, and
are to be replaced by measured benchmarks (an acceptance criterion under Path to Active). The
headline: **no change of hardware class for a node** — the real cost is CPU time on the
block-validation path.

**CPU (verification; the node never proves and never decrypts).** For a typical 2-input/2-output
confidential payment (~4 aggregated 64-bit range statements plus one Schnorr excess signature):

| Operation | Approximate cost (one modern core) |
|---|---|
| Aggregated range-proof verification | ~2–3 ms unbatched; ~1 ms amortised with cross-transaction batching |
| Schnorr excess + accumulator arithmetic | ~0.2 ms |
| For comparison: a transparent transaction | ~0.1–0.2 ms |

A confidential transaction therefore costs roughly **10–20× the verification CPU** of a
transparent one. Worst case, a block filled entirely with confidential transactions (~60 at
current block sizes) adds on the order of **0.1–0.2 s** of verification per block unbatched —
about half that with batch verification — against a block-validation budget of well under the
slot interval. Verification parallelises trivially across transactions. Two consequences
follow: **initial sync/replay** time grows with the density of confidential history (strongly
mitigated by large-batch verification during sync), and **mempool admission** must run cheap
structural checks (sizes, encodings, fee coverage) before expensive proof verification to bound
denial-of-service exposure.

**Memory.** Static verification tables are a few megabytes, one-time. The only usage-dependent
term is the UTXO set: a confidential output stores roughly 100–160 bytes more than a transparent
one, so even tens of millions of confidential UTXOs add only gigabyte-scale ledger state. The
decryption side (viewing keys, Diffie–Hellman recovery) is entirely client-side; nodes hold no
decryption material.

**Disk.** Chain growth scales with adoption: a confidential transaction is ~3–5× the size of a
transparent one, so the chain growth *rate* multiplies by roughly `1 + 3×(confidential share)`.

**Available tuning knobs**, all anticipated by this specification: cross-transaction batch
verification with deterministically derived challenges (see [validation rules](#validation-rules-edge-cases-and-soundness)), protocol-parameter caps on
confidential outputs per transaction or per block, and mempool pre-checks.

## References

- [RFC 9496 — The ristretto255 and decaf448 Groups][rfc9496]
- [Bulletproofs: Short Proofs for Confidential Transactions and More (Bünz, Bootle, Boneh, Poelstra, Wuille, Maxwell, 2018)][bulletproofs]
- Confidential Transactions (G. Maxwell) — commitment-based amount hiding with value conservation.
- T. P. Pedersen, "Non-Interactive and Information-Theoretic Secure Verifiable Secret Sharing," CRYPTO 1991.
- C. P. Schnorr, "Efficient signature generation by smart cards," Journal of Cryptology, 1991.
- A. Fiat and A. Shamir, "How to prove yourself: practical solutions to identification and signature problems," CRYPTO 1986.
- T. Kerber, A. Kiayias, M. Kohlweiss, V. Zikas, ["Ouroboros Crypsinous: Privacy-Preserving Proof-of-Stake,"][crypsinous] IEEE S&P 2019 — referenced under Future extensions (staking shielded ADA).
- C. Ganesh, C. Orlandi, D. Tschudi, ["Proof-of-Stake Protocols for Privacy-Aware Blockchains,"][got] Cryptology ePrint Archive 2018/1105 — private leader election over a public list of stake commitments; referenced under Future extensions.
- A. Poelstra, A. Back, M. Friedenbach, G. Maxwell, P. Wuille, ["Confidential Assets,"][conf-assets] Financial Cryptography Workshops 2018 — blinded asset tags; referenced under Future extensions (hiding the asset type).

[rfc9496]: https://www.rfc-editor.org/rfc/rfc9496
[CIP-1852]: https://github.com/cardano-foundation/CIPs/tree/master/CIP-1852
[crypsinous]: https://eprint.iacr.org/2018/1132
[got]: https://eprint.iacr.org/2018/1105
[conf-assets]: https://blockstream.com/bitcoin17-final41.pdf
[bulletproofs]: https://eprint.iacr.org/2017/1066

## Acknowledgements

<!-- To be completed. -->

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
