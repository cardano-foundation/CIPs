---
CIP: "?"
Title: Post-Quantum Zero-Knowledge Signatures for Cardano HD Wallets
Category: Wallets
Status: Proposed
Authors:
  - Pawel Jakubas <jakubas.pawel@gmail.com>
Implementors: N/A
Discussions:
  - Original PR: https://github.com/cardano-foundation/CIPs/pull/1242
Created: 2026-08-07
License: CC-BY-4.0
---

## Abstract

An optional, additive post-quantum signing layer for Cardano HD wallets using the
BIP32-Ed25519 derivation of [CIP-1852](#CIP-1852). Keys, addresses, and derivation are
unchanged; the classical Ed25519 signature is replaced by (or, in the recommended
deployment, accompanied by) a zero-knowledge proof of knowledge of the seed witness
underlying the existing public key, per the ZKPoSP construction [ZKPoSP](#ZKPoSP).
Post-quantum security reduces to the conjectured quantum hardness of SHA-256/SHA-512
and the soundness of the STARK proof system — no key re-registration, no address
migration, no change to the derivation path. Adoption is opt-in and phased; the
recommended deployment needs no network upgrade. Covers payment, staking, DRep, and
constitutional-committee roles uniformly.

## Motivation: Why is this CIP necessary?

- Cardano keys are Ed25519, whose security rests on the discrete-logarithm problem,
  broken in polynomial time by a quantum adversary via Shor's algorithm.
- A CIP-1852 wallet derives its whole key hierarchy from one root seed; recovering a
  single signing scalar lets an adversary forge transactions.
- Replacing the derivation scheme (lattice or hash-based keys) would invalidate every
  existing address and break hardware wallets, CIP-1854 multisig, and governance keys.
  A purely additive, signature-layer upgrade avoids that.
- [ZKPoSP](#ZKPoSP) already specialises to BIP32-Ed25519 and to exactly the "three hardened +
  two non-hardened" path shape Cardano uses (`m/1852'/1815'/account'/role/index`),
  making Cardano the natural first deployment.

## Specification

### Background

**How a Cardano wallet makes keys today.** A wallet starts from a single seed (backed
up as a mnemonic [CIP-0009](#CIP-0009)) and derives a whole tree of keys from it, per the
HD-sequential conventions of [CIP-0003](#CIP-0003) and the BIP32-Ed25519 scheme [KL17](#KL17). Each key
is a pair of secret halves: a "left" half that does the actual Ed25519 signing and a
"right" half that acts as extra secret material. Steps down the tree use a keyed hash
(HMAC-SHA512). Steps marked with an apostrophe are *hardened* — they can only be
computed from the private key — while plain steps are *non-hardened*, meaning anyone
who knows the parent's public key can derive the children. The public key is the left
half multiplied onto the Edwards curve (`A = kL·B`), and the Cardano address is a
short hash of it (`blake2b-224(A)`, per [CIP-0019](#CIP-0019)). Cardano's path
`m/1852'/1815'/account'/role/index` consists of three hardened steps followed by two
non-hardened ones.

**What ZKPoSP adds, in plain terms.** Rather than trusting only the Ed25519
signature, the wallet also produces a zero-knowledge proof that it really knows the
seed behind the public key on the address. This proof comes in two parts:

- a **derivation proof**, generated once per account, certifying "this public key was
  derived from this seed along the standard path";
- a **signing proof**, generated per transaction, certifying "I hold the secret half
  of this key and I approve this transaction".

The two parts are bound together by a short hash of the secret witness
(`hkR = SHA256(kRn)`), so a derivation proof from one account cannot be mixed with a
signing proof from another. Verification of both parts is fast and constant time,
independent of how deep the key sits in the tree.

### Relations for the Cardano path

The question every proof must answer is simply: **does this public key really come
from a seed the signer knows?** There are two ways to phrase that statement.

**The pruned relation (recommended).** The proof is anchored at the `account'` node —
the last *hardened* step of the Cardano path — and certifies only the suffix from
`account'` down to the leaf (`role`, `index`), not the whole chain from the seed.
This is just as strong as proving the full chain, because `account'` is hardened:
reaching it requires the private key, so an attacker cannot get there from public
information. In exchange, the proof has a small, fixed size regardless of the path,
and once it is generated the root seed can be removed from the proving device and kept
only in secure long-term storage.

Why the anchor must be hardened: the `role` and `index` steps are non-hardened, so
they can be derived from public keys alone. A proof covering only non-hardened steps
could be faked by anyone who knows the public keys but not the seed (the [ZKPoSP](#ZKPoSP) paper's
unsoundness result, Prop. 6.3/7.2). Every Cardano leaf is non-hardened, which is
precisely why this distinction matters on Cardano.

**The full-path relation.** A seed-to-leaf proof certifying every step from the seed
to the key. Only needed when an application must prove that two keys come from the
same seed (via a linkable commitment `c_seed`). It is roughly three times more
expensive to generate (~440 s vs ~156 s), so the default flow does not use it.

### Protocol

The wallet emits two artefacts.

**A derivation certificate `tau`, created once per account.** It bundles the
derivation proof `pi_deriv` with a hash binding `hkR` — a one-way commitment to the
secret half of the key. It answers: "the public key on this address genuinely comes
from the seed."

**A signature `sigma`, created once per transaction.** It bundles the signing proof
`pi_sign` with the *same* hash binding `hkR`. The signing proof also commits to the
transaction body via a hash `h = SHA256(kRn ∥ M)`. It answers: "I hold the secret
half of this key, and I approve this specific transaction."

**How a verifier checks it** (receiving wallet, exchange, indexer — or the ledger, in
Phase 2):

1. Run the derivation verifier on `pi_deriv`: is the public key really derived along
   the standard path? (Done once per account; the result can be cached.)
2. Run the signing verifier on `pi_sign`: does the signer hold the secret witness and
   approve `M`?
3. Compare the `hkR` values: they must match. This is the glue between the two proofs
   — it shows that the same person who signed the transaction is the person who
   derived the account's public key, and that a signature cannot be lifted from one
   account or replayed against another.

### Instantiation

**The proving system.** Proofs are ZK-STARKs — the proof family that stays secure
against quantum adversaries — produced by the RISC Zero virtual machine [RISC-ZERO](#RISC-ZERO) in
the reference implementation. Using a zkVM means the proof relations are written in
ordinary Rust, reusing well-tested libraries (`curve25519-dalek`, `hmac`, `sha2`)
instead of hand-built arithmetic circuits, which keeps engineering and audit cost
low.

**The hashes.** Binding hashes use SHA-256; the key-derivation MAC remains
HMAC-SHA512, unchanged from BIP32-Ed25519 — so the derivation itself is not touched.

**What it costs.** Reference figures from the paper [ZKPoSP](#ZKPoSP), §9, measured on the paper's
dedicated OVH EU-central cloud server: AMD Ryzen 9 9950X3D, 16 cores / 32 threads at
4.5 GHz, 64 GB RAM, no GPU, running Ubuntu, with the proving code in Rust over RISC Zero
v5.0.0-rc.1. These are the authors' reference numbers, not our own measurements; we will
re-validate them on our reference implementation before they are relied upon:

| Operation | When | Cost |
|---|---|---|
| Signing proof | every transaction | ~12.5 s to prove |
| Derivation proof | once per account | ~156 s to prove |
| Verification | every check | ~9–10 ms, constant |
| Proof size | each proof | ~219 KB |

Two numbers shape the design. The ~219 KB proof is far too large to post on-chain
today, which is why the recommended deployment (Phase 1) verifies proofs
off-chain — see [On-chain constraints](#on-chain-constraints). And verification is
fast and constant, so wallets, exchanges, and indexers can afford to check every
transaction. The one-time derivation proof can be generated lazily or delegated to a
proving server, so it does not slow down or complicate everyday signing.

### Deployment: two phases

The two phases are **not alternatives that preclude each other** — they are
complementary and meant to be adopted in sequence. Both use the exact same proofs
generated by the wallet; they differ only in **where those proofs are verified** and
in what goes on-chain.

- **Phase 1 — off-chain components, adoptable almost immediately (recommended).**
  The classical Ed25519 signature remains the on-chain witness; proofs travel
  out-of-band and are verified by wallets, exchanges, and indexers. No ledger or node
  change, fully backward compatible — quantum *readiness* now. Enforcement of
  quantum-safe *settlement* requires Phase 2 or the post-Q-day rule. Lova [LOVA](#LOVA),
  the lattice-based, quantum-proof descendant of Nova, can also be evaluated as an
  alternative prover-verifier pair within this off-chain Phase 1.
- **Phase 2 — native STARK verifier in the node (future, conditional).** The proofs
  replace the classical witness on-chain and the ledger verifies them via a native
  (non-Plutus) STARK-verifier primitive. Requires a consensus/ledger change, a
  proof-size reduction from ≈219 KB to within `maxTxSize`/`maxBlockBodySize`, and
  parameter/governance action. Not feasible with current proof sizes.

**Why the sequence 1 → 2.** Phase 1 builds everything Phase 2 needs: wallet
integration, the witness format and transport, conformance vectors, and a population
of verifiers already checking proofs. Nothing built for phase 1 is discarded when
phase 2 lands — moving to phase 2 only means the same proofs start being verified by
the ledger too. The two also coexist during the transition: wallets keep emitting
proofs under phase 1 while the consensus change for phase 2 is agreed, deployed, and
only then enforced.

The **post-Q-day rule** can be layered on either phase: consensus rejects classical
signatures entirely, and the leaf signing scalar may then be published, dropping
in-circuit scalar multiplications (derivation proof ≈ 40 s). Valid only after Q-day
activation (network-level assumption); MUST NOT be used before.

### On-chain constraints

The ≈219 KB receipt cannot be posted on-chain today, which is why Phase 1 is the
primary deployment (Conway-era limits; updatable via governance):

| Constraint | Value | Consequence for the ZKPoSP receipt |
|---|---|---|
| `maxTxSize` | 16,384 B | A ≈219 KB receipt is ~13× the entire transaction budget |
| `maxBlockBodySize` | 90,112 B | The receipt exceeds an entire block body |
| Plutus `maxTxExecutionUnits` | 14M memory / 10G steps per tx | No STARK verifier exists in Plutus; verification is orders of magnitude beyond this budget |
| Native scripts (V1–V3) | threshold multisig only | Cannot express arbitrary NIZK verification |

Raising `maxTxSize` alone would not suffice (the receipt also exceeds
`maxBlockBodySize`), and the post-Q-day variant does not reduce proof size — it only
shortens proving time.

### End-to-end flow

```mermaid
sequenceDiagram
    autonumber
    actor U as User
    participant W as "Wallet (cardano-addresses)"
    participant P as "ZKPoSP Prover"
    participant V as "Off-chain Verifier"
    participant N as "Node / Consensus"

    U->>W: seed / mnemonic (CIP-9)
    W->>W: derive m/1852'/1815'/account'/role/index<br>A = kL·B<br>address = blake2b-224(A)
    W->>P: request derivation proof (anchor = account')
    P-->>W: tau = (pi_deriv, hkR)   [one-time]
    U->>W: initiate payment<br>W builds tx body M
    W->>P: request signing proof for M
    P-->>W: sigma = (pi_sign, hkR)
    alt Phase 1 — off-chain verification
        W-->>V: (M, tau, sigma) out-of-band
        V->>V: verify pi_deriv & pi_sign, cross-check hkR, address = blake2b-224(A)
        W->>N: submit tx (witness: classical Ed25519)
        N->>N: validate as today (unchanged)
    else Phase 2 — native verifier (future)
        W->>N: submit tx (witness: tau, sigma) [needs proof-size reduction]
        N->>N: native STARK verification (not Plutus)
    end
    N->>N: include in block
```

Notes: the derivation proof and signing proof are generated the same way in both
phases; only the verification location and the on-chain witness differ. The prover
needs private anchor material and may run on-device or be delegated to a proving
server.

## Rationale: How does this CIP achieve its goals?

- **Why an additive signature layer:** public keys are byte-identical to standard
  BIP32-Ed25519 output, so there is no migration, no re-registration, and no hardware
  wallet or multisig (CIP-1854) breakage. Reusing the existing derivation also keeps
  the two hardened rounds of the Cardano path out of the proof circuit; each hardened
  round costs two HMAC-SHA512 calls (four SHA-512 hashes), which are expensive inside a
  circuit. Anchoring the proof at `account'` (see next bullet) drops that cost entirely,
  decreasing proving time while maintaining the soundness of the goal.
- **Why anchor at `account'`:** proofs over non-hardened leaves are unsound (the tweaks
  are public); only a hardened anchor binds the witness to a legitimate seed — decisive
  for Cardano because every leaf is non-hardened.
- **Alternatives rejected:** monolithic Σ proof (linear proving cost); QBIP32 new
  derivation (incompatible with existing funds — only a future-purpose-field option);
  lattice/isogeny HD wallets (change key material and addresses, no zero-migration
  property); full-path relation (heavier, only where seed linkability is required).
- **Why a hash-based STARK:** post-quantum security is the point, which rules out
  pairing-based SNARKs, Bulletproofs, and classical folding (Nova) — all broken by
  Shor's algorithm. FRI-STARKs are the remaining family: transparent (no trusted
  setup), and a zkVM (RISC Zero) proves the SHA-512/HMAC/Ed25519 relations written in
  ordinary Rust instead of hand-built arithmetic circuits. Verification is constant
  (~9–10 ms). The relations are backend-agnostic, but any backend change must re-open
  the security argument.
- **Transition is non-intrusive and reversible:** nothing is forced on anyone;
  activation is local to a signer (one one-time proof per `account'`), no network
  upgrade for Phase 1, and adoption can be rolled back without impact. Because all
  credential types share the derivation, the transition covers payment, staking, DRep,
  CC, and CIP-1854 cosigners together.

### Open Questions

- Proof size (~219 KB) vs `maxTxSize` (16,384 B): Phase 1 is feasible today; Phase 2
  is gated on reducing proofs to a few KB, and no post-quantum proof system currently
  reaches pairing-SNARK-like sizes (genuine research item, not a parameter tweak).
- Native STARK verifier feasibility in the ledger: Plutus budgets are orders of
  magnitude too small; only a native (non-Plutus) primitive is credible.
- Recursion/folding for the derivation proof; simulation extractability under
  composition is unresolved (paper Rem. 10.1).
- Proof-format versioning and fork/parameter handling.

## Path to Active

### Acceptance Criteria

- Reference implementation of the ZKPoSP scheme for the Cardano path
  `m/1852'/1815'/account'/role/index` over an audited STARK backend (e.g. RISC Zero).
- Conformance test vectors for the Cardano path covering derivation, signing, and
  verification, including the anchor-at-`account'` constraint.
- Public, independent security audit of the proof system and its Cardano integration.
- Benchmark report for the reference implementation on the [ZKPoSP](#ZKPoSP) paper's machine (AMD Ryzen 9
  9950X3D) and on a browser/WASM target, covering proving and verification time, proof
  size, and peak prover memory (including the FRI-commitment-phase peak).
- At least one wallet adopting Phase 1 (off-chain witness).
- A documented proposal for the post-Q-day rule as a protocol parameter.

### Proving Backend Options

The proving backend is an implementation choice with **several viable options**; this CIP
does not mandate one. The only hard constraint is a **post-quantum prover** — pairing- and
discrete-log-based schemes (KZG, standard Nova, out-of-the-box Halo2) are excluded, since
Shor's algorithm breaks them. Within that constraint, the backend is chosen by
benchmarking the same relations, comparing proving time, peak memory, proof size, and
audit cost:

1. **RISC Zero zkVM — the [ZKPoSP](#ZKPoSP) paper's backend; the default baseline.** Proof relations are
   written in ordinary Rust, reusing audited primitives (`curve25519-dalek`, `hmac`,
   `sha2`). Lowest engineering risk (no hand-built constraints), but the zkVM's own
   arithmetization, prover, and commitment scheme still require audit. Reference figures
   (paper §9, AMD Ryzen 9 9950X3D): signing proof ~12.5 s, derivation proof ~156 s,
   verification ~9–10 ms, proof ~219 KB.
2. **Halo2/midnight-zk with a FRI polynomial commitment scheme.** A heavily optimized
   circuit for this relation already exists (≈114k rows @ k=17). The default KZG PCS is
   pairing-based and therefore *not* quantum-safe; swapping it for FRI is real work — it
   changes the commitment scheme, the FRI domain/blow-up, proof size, and soundness
   parameters — and the security argument must be re-opened and re-audited. This is not
   hypothetical: the Tachyon zkVM [TACHYON](#TACHYON) already implements Halo2 with a FRI PCS, and
   Zcash's own quantum-readiness roadmap plans hash-based or STARK-style hardening of its
   Halo2 proofs [ZCASH-QR](#ZCASH-QR), a staged posture that mirrors this CIP's Phase 1 → 2.
3. **Plonky3-style native FRI-STARK circuits.** The [ZKPoSP](#ZKPoSP) paper's own forward plan for
   proof-size reduction; removes the zkVM's fixed per-segment overhead, but requires an
   audited circuit implementation that is at an earlier stage of maturity. The Tachyon
   backend also tracks Plonky3 [TACHYON](#TACHYON).
4. **Nova / groth16-prover [NOVA](#NOVA) — efficiency comparison only.** Efficient and readily
   available, but not quantum-proof and requires a trusted setup; useful as a performance
   bound and for a possible hybrid, not as the primary mechanism.
5. **Lova [LOVA](#LOVA) — lattice-based IVC.** A recursive-SNARK descendant of Nova that
   replaces its pairing-based assumptions with a lattice-based construction, making it
   quantum-proof. Its incrementally verifiable computation gives linear prover time and
   constant verification, which fits the Phase 1 off-chain story; the caveat is early
   maturity — a first-of-its-kind Nova implementation, unproven at Cardano scale — so it
   is a candidate for Phase 1 evaluation alongside the STARK route, not the default
   baseline.

### Implementation Plan

The plan below is **tentative** — it is a menu of options to pursue, not a settled
commitment. The backend is chosen by benchmarking the [Proving Backend
Options](#proving-backend-options) above; nothing here is final.

- Integration with an existing Cardano wallet library (cardano-addresses) to emit
  `tau` and `sigma` out-of-band (Phase 1).
- Browser/WASM benchmark of the wallet integration: verification, the per-transaction
  signing proof, and the one-time derivation proof (timing and peak memory), to confirm
  the Phase 1 off-chain verification story on the worst-case environment.
- Evaluation of proof-size reduction (ZK-friendly hashing, smaller FRI
  configurations) to unlock Phase 2.
- CDDL specification of the witness format for a future native STARK-verifier
  primitive.

## References

- <a id="ZKPoSP"></a>[ZKPoSP] Botta, Pospieszalski, Ragnoli, Ranvier, "ZKPoSP: Post-Quantum
  Zero-Knowledge Proofs for Hierarchical Deterministic Wallets",
  ePrint 2026/1508: https://eprint.iacr.org/2026/1508
- <a id="CIP-0009"></a>[CIP-0009] Wallet Mnemonic Sequence. https://cips.cardano.org/cip/CIP-0009
- <a id="CIP-0019"></a>[CIP-0019] Cardano Addresses. https://cips.cardano.org/cip/CIP-0019
- <a id="CIP-1852"></a>[CIP-1852] HD (Hierarchy for Deterministic) Wallets for Cardano.
  https://cips.cardano.org/cip/CIP-1852
- <a id="CIP-1854"></a>[CIP-1854] Multi-signatures HD Wallets. https://cips.cardano.org/cip/CIP-1854
- <a id="CIP-0003"></a>[CIP-0003] Withdrawal scripts and address formats (HD Random vs HD Sequential).
  https://cips.cardano.org/cip/CIP-0003
- <a id="KL17"></a>[KL17] Khovratovich and Law, "BIP32-Ed25519: Hierarchical Deterministic Keys over a
  Non-linear Keyspace" (EuroS&PW 2017). https://input-output-hk.github.io/adrestia/static/Ed25519_BIP.pdf
- <a id="RISC-ZERO"></a>[RISC-ZERO] RISC Zero zkVM. https://dev.risczero.com/
- <a id="HALO2"></a>[HALO2] zcash/halo2, The Halo2 zero-knowledge proving system.
  https://github.com/zcash/halo2
- <a id="TACHYON"></a>[TACHYON] Tachyon, modular zero-knowledge backend (Halo2 with a FRI polynomial
  commitment scheme, GPU-accelerated). https://github.com/kroma-network/tachyon
- <a id="NOVA"></a>[NOVA] cardano-foundation/bls, groth16-prover (Nova-based proving).
  https://github.com/cardano-foundation/bls/tree/main/groth16-prover
- <a id="LOVA"></a>[LOVA] Fenzi, Knabenhans, Nguyen, Pham, "Lova: Lattice-Based Folding Scheme from
  Unstructured Lattices" (ASIACRYPT 2024), lattice-based and quantum-secure.
  https://eprint.iacr.org/2024/1964
- <a id="ZCASH-QR"></a>[ZCASH-QR] CoinDesk Research, "Building the Zcash Machine: Tachyon and Quantum
  Readiness", June 2026.
  https://www.coindesk.com/research/building-the-zcash-machine-tachyon-and-quantum-readiness

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
