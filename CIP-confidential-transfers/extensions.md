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

| # | Extension | Problem it solves | Effort | Impact | New cryptography? |
|---|---|---|---|---|---|
| 1 | Native-script confidential outputs | Multisig treasuries cannot hold confidential funds | **Low** | **High** | **None** |
| 2 | Viewing-key rotation | A disclosed or leaked viewing key reads the account **forever** | **Low** | Medium–High | **None** |
| 3 | Multi-party construction | Collaborative transactions need one party to know all blindings | Low–none | Medium | None on-chain |
| 4 | Successor range proof | Proof size/verification dominate transaction cost | Medium | Medium | New proof system |
| 5 | Plutus ristretto255 builtins | Scripts cannot verify anything about a commitment | Medium | Medium–High | None (exposes existing) |
| 6 | Confidential governance | Shielding ADA silently costs its owner voting power | Medium–High | Medium | Mostly existing; threshold decryption if committee-based |
| 7 | Plutus script outputs | Confidential value is locked out of smart contracts entirely | High | High | None |
| 8 | Programmable-token (CIP-113) integration | Regulated/programmable tokens cannot have confidential amounts | High | High | Existing classes (sigma protocols) |
| 9 | Confidential staking | Shielding ADA costs its owner staking rewards (~3–4%/yr) | High | High | Varies by variant: none → threshold → heavy ZK |
| 10 | Stealth addresses | Address reuse lets observers cluster all payments to one party | High | Medium | Existing techniques, new to Cardano |
| 11 | Asset-type blinding | Which asset moves reveals the business activity | Very high | Medium | New (surjection proofs, per-asset generators) |
| 12 | Post-quantum migration | Future quantum adversary reads today's hidden amounts | Very high | Low now | All new (lattice-based) |
| 13 | Shielded pool | The public transaction graph itself reveals relationships | Very high | Non-goal | All new (SNARK/STARK, nullifiers) |

---

## 1. Native-script confidential outputs — *the strongest merge candidate*

**Problem.** The base proposal restricts confidential outputs to key-locked addresses — but
real treasuries are not single keys. A company running confidential payroll, a DAO, any
2-of-3 board-controlled fund: all use **native-script (multisig/timelock) addresses**, and
under the base proposal none of them can *hold* confidential value. The paying company's own
treasury cannot keep confidentially what it pays out confidentially.
**What it adds.** Confidential outputs at native-script payment credentials. Native scripts
enforce signature and time conditions **without ever inspecting amounts**, so no new
cryptography and no script-context work is needed; the viewing-key registration certificate
already accepts script-hash credentials by construction.
**Crypto: none.** Not a single new primitive or proof; the existing witness machinery for
native scripts and the base proposal's unchanged proof set cover it entirely.
**Effort: low.** Relax one validation rule (key-locked-only), which the base proposal
already frames as a relaxable rule rather than a format restriction.

## 2. Viewing-key rotation — *the second merge candidate*

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

## 3. Multi-party transaction construction — *works partially today*

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

## 4. Successor range-proof system

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

## 5. Plutus ristretto255 builtins

**Problem.** Plutus scripts today cannot perform ristretto255 group operations or verify
any of this proposal's proofs — so no contract can ever check *anything* about a commitment,
which blocks the entire script track (items 7–8).
**What it adds.** Group/scalar builtins (and plausibly a Bulletproofs-verification builtin)
with cost-model entries — the analogue of what CIP-0381 did for BLS12-381. Useful beyond
confidential transfers, for any ristretto-based protocol.
**Crypto: none.** No new constructions — it exposes the base proposal's existing primitives
(ristretto255 group operations, Bulletproofs verification) to scripts as builtins; the work
is engineering and cost-modelling, not cryptography.
**Effort: medium**, on an independent track (Plutus version + costing), parallelisable with
everything else.

## 6. Confidential governance participation

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

## 7. Plutus script outputs

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
cryptography (amount-reading policies are item 8's problem).
**Effort: high** — script-context extension and a new Plutus version. Depends on items 1
and 5.

## 8. Programmable-token (CIP-113) integration

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
**Effort: high.** Depends on item 7 and on CIP-113 itself stabilising.

## 9. Confidential staking

**Problem.** Hidden ADA earns no staking rewards and contributes no stake (base proposal) —
an opportunity cost of roughly the network staking yield (~3–4%/yr) that discourages
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

## 10. Stealth (one-time) addresses

**Problem.** Addresses are public and reused, so an observer can cluster every payment a
party receives — amounts are hidden, but *pay-relationships* to a known address are not.
**What it adds.** Receiver unlinkability: recipients publish a meta-address; each payment
derives a fresh, unlinkable address. The transaction graph itself stays visible (senders and
input→output links remain public).
**Crypto: existing techniques, new to Cardano.** Dual-key stealth derivation is deployed at
scale elsewhere (Monero; cf. ERC-5564) — no novel constructions, but a primitive class the
Cardano ledger has never carried, with the audit burden that implies.
**Effort: high** — it sacrifices scan-free decryption (wallets and auditors must trial-DH
outputs) and requires reworking the viewing-key-to-credential binding; a substantial
companion despite its modest privacy gain.

## 11. Asset-type blinding

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
**Effort: very high** — substantially harder cryptography, and most compliance-oriented use
cases want the asset type visible anyway.

## 12. Post-quantum migration

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

## 13. Shielded pool (address/graph hiding)

**Problem.** The transaction graph is fully public: who transacted with whom is visible to
everyone even though amounts are not.
**What it adds.** A separate, coexisting shielded output type (notes + nullifiers), bridged
via shield/unshield — the Zcash coexistence model.
**Crypto: everything new, different paradigm.** Note commitments, nullifiers, incremental
Merkle trees, and succinct membership proofs (zk-SNARK/STARK) — an entirely different proof
stack from the base proposal's, which is why it can only ever be a sibling pool.
**Effort: very high — and an explicit non-goal** of the base proposal, whose
compliance-first positioning depends on the graph remaining public. Listed for completeness:
the base design neither blocks nor requires it.

---

## The question to reviewers

Minimality keeps this proposal reviewable and its audit surface small — but each
separately-shipped extension is a full hard-fork cycle for the entire ecosystem: node
implementations, wallets, hardware devices, explorers, exchanges. The authors' own reading
of the list above: items **1–2** solve problems that bite the proposal's *primary audience
on day one* (a treasury that cannot hold what it pays; a disclosure that cannot be ended)
at low implementation cost, and item **3** deserves a capability note. Whether they should
be **merged into this proposal or scheduled for the same hard fork** — and whether any
higher-effort item is important enough to justify delaying the base proposal — is as much an
ecosystem and business judgement as a technical one, and reviewer input on exactly this is
invited.
