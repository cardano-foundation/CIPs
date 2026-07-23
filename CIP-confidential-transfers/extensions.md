# Anticipated Extensions — Problems, Effort, Impact

*Informative companion to the [proposal](README.md). Linked from its Open Questions: the
proposal is deliberately minimal, and this document exists so reviewers can judge — before
ratification — **which extensions, if any, should be merged into the proposal itself or
scheduled for the same hard fork**, trading a larger initial implementation for fewer
ecosystem upgrade cycles. Every entry states the problem it solves first: the limitation a
user actually hits under the base proposal. To the authors' knowledge none of these is
foreclosed by the base design (see
[Guarantees to future proposals](README.md#guarantees-to-future-proposals)).*

Entries are sorted by **implementation effort (ascending)**, then **impact (descending)** —
so the top of the list is where "bake it in anyway" is most plausible.

The **Compliance** column is measured against the base proposal's audit model (a designated
third party holding the viewing key sees the account's complete history): `-` means the
extension preserves that model by construction; anything else is spelled out.

| # | Extension | What it lets a user do that they cannot today | Effort | Impact | New cryptography? | Compliance |
|---|---|---|---|---|---|---|
| 1 | Viewing-key rotation | As an account owner, I can **end** an auditor's (or a thief's) visibility going forward by switching to a new viewing key | **Low** | Medium–High | **None** | - |
| 2 | Multi-party construction | As users, several of us can co-build one transaction (e.g. through a batcher) **without revealing our amounts to each other** | Low–none | Medium | None on-chain | - |
| 3 | Successor range proof | As a user I pay **lower fees**; as a node operator I verify blocks faster | Medium | Medium | New proof system | - |
| 4 | Plutus ristretto255 builtins | As a dApp developer, my scripts can **verify commitments and proofs** on-chain | Medium | Medium–High | None (exposes existing) | - |
| 5 | Confidential governance | As a holder of shielded ADA, I **keep my governance voting power** | Medium–High | Medium | Mostly existing; threshold decryption if committee-based | - |
| 6 | Plutus script outputs | As a user, I can lock confidential funds **under smart-contract conditions** (escrow, vesting, DeFi) | High | High | None | - |
| 7 | Programmable-token (CIP-113) integration | As a regulated-token issuer, my holders get **confidential balances while my policy rules stay enforced** | High | High | Existing classes (sigma protocols) | - |
| 8 | Confidential staking | As a holder of shielded ADA, I **keep earning staking rewards** | High | High | Varies by variant: none → threshold → heavy ZK | - |
| 9 | Stealth addresses | As a payee, observers can **no longer link my incoming payments** by watching my address | High | Medium | Existing techniques, new to Cardano | ⚠ audit-by-key intact, but AML chain-analytics (receiver clustering) breaks; auditor completeness shifts from public indexing to trusting scanning tools |
| 10 | Asset-type blinding | As a business, observers can no longer see **which tokens** I hold or trade — only that I transact | Very high | Medium | New (surjection proofs, per-asset generators) | ⚠ per-account audit survives **only if** the viewing key is required to reveal asset tags; chain-wide monitoring of a given asset becomes impossible for anyone |
| 11 | Post-quantum migration | As a user, my hidden amounts stay hidden **even against a future quantum computer** | Very high | Low now | All new (lattice-based) | - |
| 12 | Shielded pool | As a user, observers can no longer see **whom I transact with** at all | Very high | Non-goal | All new (SNARK/STARK, nullifiers) | ✗ **not compliant**: graph hiding places it in the mixer / anonymity-enhanced category (cf. Tornado Cash sanctions, exchange delistings of privacy coins); with sender ambiguity, counterparties can be unprovable **even to the account's own auditor** — the reason it is an explicit non-goal |

---

## 1. Viewing-key rotation — *the remaining merge candidate*

**Problem.** The account's viewing keypair is immutable in the base proposal. Two
consequences: a **leaked** `sk_view` reads every future amount forever (it never spends —
but confidentiality is permanently gone for new inflows), and an **auditor** handed the key
for one audit keeps visibility into the account's entire future — "read access for the 2027
audit" silently becomes "read access for life", which undermines the compliance-first story.
**What it adds.** A superseding registration ("current certificate wins"), successive
hardened key indices on the existing derivation path (mnemonic restore recovers all
historical keys, so old outputs stay readable and spendable), and defined sender behaviour
across the transition. Honest limit: rotation protects the *future only* — on-chain history
remains readable by the old key forever.
**Crypto: none.** A new keypair from the already-reserved next derivation index and a new
certificate — the same primitives the base proposal already uses.
**Effort: low.** Both fences are already in the base proposal (indexed path with reserved
indices; immutability stated as a relaxable validation rule).

## 2. Multi-party transaction construction — *works partially today*

**Problem.** Building the balancing proof requires knowing **all** input and output
blindings, so a transaction assembled by several independent parties (collaborative
payments, batcher-style flows) would force them to reveal blindings — and thus amounts — to
one builder.
**What it adds.** Standardised partial balancing proofs. Because Schnorr excess signatures
aggregate linearly, parties can already combine partial signatures off-chain under the
existing witness form with **no ledger change**; a dedicated extension only standardises the
format. Worth a capability note in the base proposal rather than merged machinery.
**Crypto: none on-chain.** Schnorr's linearity is already in the base scheme; what is new
is an off-chain nonce-coordination protocol (MuSig2-style, well-studied) and at most a
standardised partial-signature format.
**Effort: low to none** on-chain; coordination-protocol work off-chain.

## 3. Successor range-proof system

**Problem.** The aggregated range proof dominates confidential transaction size (the main
driver of the ~3–5× fee overhead) and verification CPU.
**What it adds.** A drop-in newer proof system (e.g. Bulletproofs++) with smaller proofs
and/or faster verification, under `range_proof` alternative tag 1 — the upgrade the base
proposal's Versioning section explicitly anticipates.
**Crypto: a new proof system.** Bulletproofs++ (or a successor) is a distinct construction
from the deployed Bulletproofs — same statements, new prover/verifier — hence the fresh
implementation and independent audit that dominate this item's cost.
**Effort: medium** — the cryptography is known, but a new proof system needs its own
implementation, benchmarks, and independent security audit; old transactions keep verifying
under tag 0.

## 4. Plutus ristretto255 builtins

**Problem.** Plutus scripts today cannot perform ristretto255 group operations or verify
any of this proposal's proofs — so no contract can ever check *anything* about a commitment,
which blocks the entire script track (items 6–7).
**What it adds.** Group/scalar builtins (and plausibly a Bulletproofs-verification builtin)
with cost-model entries — the analogue of what CIP-0381 did for BLS12-381. Useful beyond
confidential transfers, for any ristretto-based protocol.
**Crypto: none.** No new constructions — it exposes the base proposal's existing primitives
(ristretto255 group operations, Bulletproofs verification) to scripts as builtins; the work
is engineering and cost-modelling, not cryptography.
**Effort: medium**, on an independent track (Plutus version + costing), parallelisable with
everything else.

## 5. Confidential governance participation

**Problem.** Hidden ADA is excluded from voting power (base proposal), so shielding funds
silently reduces the owner's — and in aggregate the honest economy's — weight in on-chain
governance.
**What it adds.** ADA-weighted voting with hidden amounts. An account's voting-weight
commitment is *already* publicly derivable (homomorphic sum of its output commitments —
guaranteed by the base proposal's extension contract); the missing piece is opening only
**tallies**, never individual weights, via threshold decryption or aggregate opening proofs,
plus snapshot rules.
**Crypto: mostly existing.** Weight commitments and aggregate opening proofs reuse Pedersen
homomorphism and Schnorr-style proofs already in the base scheme. The committee-based tally
variant adds **threshold decryption** — standard cryptography, but a genuinely new primitive
(and trust model) for the Cardano ledger.
**Effort: medium–high.** The cryptography is standard; the genuinely new ingredient is the
tally-opening trust assumption (e.g. a decryption committee), which deserves its own
community debate — the reason it stays out of the base proposal.

## 6. Plutus script outputs

**Problem.** Under the base proposal (validation rule 12 aside, rule 10 in particular),
confidential value cannot interact with smart contracts at all — it is transfer-only money
until unshielded. Every DeFi or contract-mediated use requires revealing amounts at the
boundary.
**What it adds.** Confidential outputs at Plutus script addresses: the script context
carries commitments where it carries amounts today (a new Plutus ledger-language version).
Identity/credential-based policies work unchanged — addresses and datums stay public; only
amount-reading policies need more (item 8).
**Crypto: none.** The commitments and proofs are unchanged; the work is representing them
in the script context and versioning Plutus — ledger and language engineering, not new
cryptography (amount-reading policies are item 7's problem).
**Effort: high** — script-context extension and a new Plutus version. Depends on item 4;
native-script support is already part of the base proposal.

## 7. Programmable-token (CIP-113) integration

**Problem.** Programmable tokens (compliance-constrained stablecoins, permissioned assets)
live permanently at script addresses — so they are doubly excluded: no confidential amounts
for exactly the asset class whose issuers and users most want commercial confidentiality.
**What it adds.** ZK amount-predicates (threshold/limit proofs via the shifted-commitment
technique; linear-relation proofs for proportional fees) supplied in redeemers and verified
by transfer-logic scripts, plus viewing-key resolution for protocol-controlled addresses.
Notably, most programmable-token policies are identity-based (freeze, whitelist) and would
work over confidential outputs unchanged.
**Crypto: existing classes, newly composed.** Threshold/limit predicates reuse the shifted-
commitment range-proof trick the base proposal already uses for minimum-ADA; proportional
relations use Schnorr-style **sigma protocols** — well-studied constructions (and notably
the class the base proposal deliberately dropped), returning here as new proof *statements*
rather than new primitives.
**Effort: high.** Depends on item 6 and on CIP-113 itself stabilising.

## 8. Confidential staking

**Problem.** Hidden ADA earns no staking rewards and contributes no stake (base proposal) —
an opportunity cost equal to the full network staking yield (a few percent per year,
currently around 1–2% and declining as reserves deplete) that discourages
long-term confidential holdings; arguably the single biggest adoption brake in the base
design.
**What it adds.** Delegation converts shielded ADA into pool-specific delegation tokens with
hidden quantities (reusing this proposal's own native-asset machinery), rewards via a public
per-epoch exchange rate (the pattern proven in production by Penumbra), and per-pool totals
via provable aggregate opening — with escalation paths up to fully-ZK leader election.
**Crypto: varies by ambition.** The pool-opened-aggregate variant needs **nothing new**
(provable Pedersen openings); the committee variant adds **threshold decryption**; fully-ZK
leader election needs **heavy new ZK machinery** (Ganesh–Orlandi–Tschudi-style proofs, at
the far end Crypsinous). The escalation path is the point: adoption can start with zero new
cryptography.
**Effort: high** — consensus-adjacent machinery, epoch-snapshot rules, and (in committee
variants) new trust assumptions.

## 9. Stealth (one-time) addresses

**Problem.** Addresses are public and reused, so an observer can cluster every payment a
party receives — amounts are hidden, but *pay-relationships* to a known address are not.
**What it adds.** Receiver unlinkability: recipients publish a meta-address; each payment
derives a fresh, unlinkable address. The transaction graph itself stays visible (senders and
input→output links remain public).
**Crypto: existing techniques, new to Cardano.** Dual-key stealth derivation is deployed at
scale elsewhere (Monero; cf. ERC-5564) — no novel constructions, but a primitive class the
Cardano ledger has never carried, with the audit burden that implies.
**Regulatory posture: caution.** The account's auditor still sees everything via the viewing
key, but completeness changes character — from corroborating against public address indexing
to trusting cryptographic scanning tools — and third-party AML chain-analytics (receiver
clustering) breaks by design, which risks an anonymity-enhanced-adjacent classification.
**Effort: high** — it sacrifices scan-free decryption (wallets and auditors must trial-DH
outputs) and requires reworking the viewing-key-to-credential binding; a substantial
companion despite its modest privacy gain.

## 10. Asset-type blinding

**Problem.** Which assets an output holds is public, so counterparties and competitors see
*what* a business transacts in even when quantities are hidden.
**What it adds.** Blinded asset tags (Confidential-Assets style): quantities committed under
asset-derived generators, proofs that hidden tags are legitimate and cannot cancel across
assets, rethought mint/burn authorisation. Arrives as `confidential_asset` alternative tag 1;
existing outputs migrate by unshield/re-shield.
**Crypto: genuinely new.** Per-asset generators and **asset surjection proofs**
(Confidential-Assets style) proving hidden tags are legitimate and cannot cancel across
assets — a new proof family with real cryptanalytic surface, the core reason this item sits
in the very-high-effort tier.
**Regulatory posture: caution.** Per-account audit survives **only if** the design requires
the viewing key to reveal asset tags — that must be a hard requirement, not an assumption.
Even then, chain-wide monitoring of a specific asset (e.g. tracking a sanctioned token's
flows) becomes impossible for anyone: per-account compliance is preserved, systemic
observability is not.
**Effort: very high** — substantially harder cryptography, and most compliance-oriented use
cases want the asset type visible anyway.

## 11. Post-quantum migration

**Problem.** The base scheme's confidentiality rests on discrete-log/DDH assumptions: a
future cryptographically-relevant quantum computer could recover amounts recorded today
(harvest-now-decrypt-later — already declared in the base proposal's trade-offs).
**What it adds.** Lattice-based commitments and range proofs, a PQ KEM replacing the DH
transport, a PQ balancing proof — under new versioned tags on all three proof/commitment
unions. Honest limit: migration protects *future* outputs only.
**Crypto: everything new.** Lattice-based commitments and range proofs, a post-quantum KEM
replacing the Diffie–Hellman transport, a post-quantum proof of knowledge for balancing —
every primitive in the scheme is replaced, none is a drop-in today.
**Effort: very high** — today's PQ equivalents are far larger and slower, and the ledger's
own signatures are not post-quantum either; a chain-wide effort.

## 12. Shielded pool (address/graph hiding)

**Problem.** The transaction graph is fully public: who transacted with whom is visible to
everyone even though amounts are not.
**What it adds.** A separate, coexisting shielded output type (notes + nullifiers), bridged
via shield/unshield — the Zcash coexistence model.
**Crypto: everything new, different paradigm.** Note commitments, nullifiers, incremental
Merkle trees, and succinct membership proofs (zk-SNARK/STARK) — an entirely different proof
stack from the base proposal's, which is why it can only ever be a sibling pool.
**Regulatory posture: not compliant.** Graph hiding crosses a regulatory category line, not
a technical one: it places the construction in the mixer / anonymity-enhanced bucket (cf.
the Tornado Cash sanctions and exchange delistings of privacy coins), and with sender
ambiguity, counterparties can be unprovable **even to the account's own auditor** — tax and
AML frameworks require exactly what this hides. This is why the base proposal declares it an
explicit non-goal, and why every *other* extension in this list preserves the public graph.
**Effort: very high — and an explicit non-goal** of the base proposal, whose
compliance-first positioning depends on the graph remaining public. Listed for completeness:
the base design neither blocks nor requires it.

---

## The question to reviewers

Minimality keeps this proposal reviewable and its audit surface small — but each
separately-shipped extension is a full hard-fork cycle for the entire ecosystem: node
implementations, wallets, hardware devices, explorers, exchanges. One item has already been
absorbed on exactly this reasoning: **confidential outputs at native-script addresses**
(multisig/timelock treasuries) began as the top entry of this list and were merged into the
base proposal — one relaxed rule, no new cryptography, serving its primary audience. The
authors' reading of what remains: item **1** (viewing-key rotation) solves a problem that
bites the same audience (a disclosure that cannot be ended) at low cost and zero new
cryptography, and item **2** deserves a capability note. Whether rotation should be
**merged into this proposal or scheduled for the same hard fork** — and whether any
higher-effort item is important enough to justify delaying the base proposal — is as much an
ecosystem and business judgement as a technical one, and reviewer input on exactly this is
invited.
