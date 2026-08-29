---
CIP: "?"
Title: Hydra Head UTxO Recognition
Category: Wallets
Status: Proposed
Authors:
    - Sharan Konerira <skoniog@users.noreply.github.com>
Implementors: []
Discussions:
    - Requirements (Hydra issue 2818): https://github.com/cardano-scaling/hydra/issues/2818
    - Original PR: https://github.com/cardano-foundation/CIPs/pull/1254
Created: 2026-08-29
License: CC-BY-4.0
---

## Abstract

Funds committed to a Hydra head disappear from the user's wallet. Because CIP-30 wallets cannot confirm ownership of a layer-2 UTxO against layer 1, wallets such as Lace and Eternl either hide head-committed funds entirely or flag them as suspicious "ghost UTxOs" — treating a user's own money as a phishing attempt. This is widely identified as the single largest adoption blocker for consumer-facing Hydra applications.

This proposal defines a standard by which a wallet can *recognize* and *display* Hydra head-committed UTxOs as legitimate, verified balances — without running any head infrastructure and without introducing any new trust assumption. It specifies (1) the layer-1 anchors a wallet reads (the head state UTxO, its state token, and deposit outputs), (2) a *proof bundle* served by a head's operator — the head's latest confirmed snapshot together with the multisignature every head participant already produces, (3) the exact byte encoding that multisignature covers, (4) how a wallet binds specific UTxOs to the signed snapshot through the head's BLS12-381 UTxO-set accumulator, (5) a discovery mechanism linking on-chain deposits to a proof endpoint, and (6) mandatory display states for verified, pending, and unverifiable funds.

In-head transaction construction, snapshot signing, and head lifecycle management are explicitly out of scope; they belong to a separate, future wallet-participation proposal.

## Motivation: Why is this CIP necessary?

### The problem

When a user commits funds into a Hydra head, the corresponding layer-1 UTxOs are locked at the head validator and the funds thereafter live as layer-2 UTxOs inside the head's off-chain ledger. From the perspective of a conventional wallet, the user's funds are simply *gone*: the wallet sees an outgoing transaction to an unknown script and no incoming balance. Some wallets hide the funds; others display warnings intended for phishing scripts. Either way, no consumer-facing head application can present a coherent wallet experience, because the user's own wallet contradicts the application's balance display.

This is a **recognition** problem, not an interaction problem. Wallets do not need to build, sign, or submit transactions inside a head. They need to correctly interpret a UTxO committed to a known head and display it as legitimate, backed by a link to layer 1 that the wallet can verify independently.

### Why no new attestation scheme is needed

The Hydra protocol already produces exactly the artifact a wallet needs. Every confirmed snapshot of a head's layer-2 ledger is signed by *all* head participants' Hydra keys, and those verification keys are published on chain in the head's datum when the head opens. The layer-1 head validator itself verifies these multisignatures when the head is closed or its state incremented — so a snapshot multisignature is not an "operator's claim"; it is the head's own consensus artifact, and it is *stronger* than any single-party attestation this proposal could invent. This CIP therefore standardizes how a wallet obtains and verifies that existing artifact, rather than defining a new one.

### Stakeholders

- **Users** of head-based applications, who currently cannot see or trust their own committed funds.
- **Wallet implementors** (Lace, Eternl, Typhon, VESPR, …), who need a deployment-independent validation rule instead of bespoke per-application logic.
- **Head operators and application developers** (in particular those running the [delegated head topology](https://hydra.family/head-protocol/topologies/delegated-head), where operator nodes hold the Hydra snapshot keys and serve many light clients), who need a standard way to make their heads recognizable.
- **The Hydra project**, for which wallet recognition converts "support Hydra" from a per-vendor favor into a conformance checkbox.

This proposal responds to the requirements gathered in [cardano-scaling/hydra#2818](https://github.com/cardano-scaling/hydra/issues/2818).

## Specification

### Terminology

| Term | Meaning |
|---|---|
| **Head** | An instance of the Hydra Head protocol: a multi-party layer-2 ledger anchored by a layer-1 state machine. |
| **Head ID** | The 28-byte minting policy ID of the head's token minting policy. Uniquely identifies a head; doubles as the `CurrencySymbol` under which the head's state token and participation tokens are minted. |
| **State token (ST)** | The unique token (quantity 1) with policy = head ID and asset name `"HydraHeadV2"` (11 bytes, ASCII) that sits in the head's layer-1 state UTxO. |
| **Head state UTxO** | The single layer-1 UTxO at the head validator address carrying the ST and an inline datum describing the head's state machine state. |
| **Snapshot** | A confirmed state of the head's layer-2 ledger, multi-signed by all participants. |
| **Proof bundle** | The latest confirmed snapshot together with its multisignature, served over HTTP by a head participant (typically the operator). |
| **Accumulator** | A KZG-style polynomial commitment (BLS12-381 G1 point) over the snapshot's UTxO set; only its 32-byte hash is covered by the snapshot signature. |
| **Deposit** | A layer-1 output at the Hydra deposit validator that escrows funds destined for a head until the head's participants absorb ("claim") it via an increment transaction, or the depositor recovers it after a deadline. |

All hash functions are named explicitly: `sha2_256`, `blake2b_224`, `blake2b_256`. `serialiseData(x)` denotes the CBOR serialization of a Plutus Core `Data` value as produced by the Plutus `serialiseData` builtin, with `toData` the standard `Data` encoding of the value in question (byte strings encode as `Data.B`, integers as `Data.I`).

This specification is written against Hydra protocol version **2** — the version whose state token asset name is `"HydraHeadV2"`. See [Versioning](#versioning).

### Trust model

A conformant wallet verifying a head UTxO trusts only:

1. **Layer 1** — for the head's existence, its participant set (Hydra verification keys), and its current on-chain state version; and
2. **The unanimity of the head's own participants** — a snapshot is accepted only under a valid Ed25519 signature from *every* party listed on chain.

The proof endpoint (operator) is *untrusted*: it can withhold data (a liveness failure the wallet must surface as *unverifiable*, per [Display states](#display-states)) but cannot cause a wallet to display forged balances, because every displayed balance is bound to the on-chain party set through the signature and the accumulator. Note that this matches the trust model users already accepted when entering the head: head safety itself assumes at least one honest, online participant.

### Layer-1 anchors

#### Head state UTxO

A wallet locates a head's state UTxO given a head ID `cid` by finding the unique UTxO containing the asset `(policy = cid, name = "HydraHeadV2", quantity = 1)`. The output sits at the head validator's script address; the address is a function of the head validator script hash, which is fixed per Hydra protocol version.

The inline datum is the head state machine state, encoded as Plutus `Data`:

```cddl
state =
    open              ; constructor 0
  / closed            ; constructor 1
  / final             ; constructor 2
  / fanout-progress   ; constructor 3

open = #6.121([open-datum])            ; Constr 0 [open-datum]

open-datum = #6.121([                  ; Constr 0, fields in order:
    head-seed,                         ; TxOutRef that seeded the minting policy
    head-id,                           ; bytes .size 28, = own currency symbol
    parties,                           ; [* party]
    contestation-period,               ; integer (milliseconds)
    deposit-period,                    ; integer (milliseconds)
    version,                           ; uint — open-state version, bumped by increment/decrement
    accumulator-hash,                  ; bytes .size 32 — blake2b_256 of the G1 accumulator
                                       ;   commitment of the last confirmed snapshot
    head-ada-overhead                  ; integer — min-UTxO ada not belonging to any L2 UTxO
])

party = bytes .size 32                 ; raw Ed25519 verification key (NOT wrapped in a constructor)
```

The `parties` field is the ordered list of raw 32-byte Ed25519 Hydra verification keys of all head participants. **This order is normative**: multisignature verification (below) is positional.

A wallet MUST read `parties`, `version`, and `accumulator-hash` from this datum. A wallet MUST treat a datum it cannot parse under this schema as an unrecognized script output (out of scope of this CIP), not as an error state of a head.

#### Deposit outputs

Funds enter an open head through the deposit validator. A deposit output:

- sits at the deposit validator's script address (fixed per Hydra protocol version);
- is **always output index 0** of its transaction (a protocol invariant enforced on-chain when the deposit is claimed), so `deposit id = transaction id`;
- carries an inline datum:

```cddl
deposit-datum = #6.121([head-id, deadline, commits])   ; Constr 0
head-id   = bytes .size 28
deadline  = integer                                    ; POSIX time, milliseconds
commits   = [* commit]
commit = #6.121([
    input,                 ; TxOutRef of the deposited L1 UTxO
    pre-serialized-output  ; bytes — serialiseData(toData(txOut)) of the deposited output
])
```

Because each `pre-serialized-output` is a complete serialized `TxOut`, a wallet can decode the deposited outputs' addresses and values **from layer 1 alone**, with no operator involvement. This is what makes the *pending deposit* display state trustlessly verifiable.

Reference-script fields of deposited outputs are not representable in the pre-serialized form and are dropped; address, value, and datum are preserved.

#### Transaction metadata (non-normative indexing aid)

Hydra layer-1 transactions carry transaction metadata under label `55555` with the textual value `"HydraV2/<TxName>"` (e.g. `"HydraV2/DepositTx"`, `"HydraV2/IncrementTx"`). Wallets and indexers MAY use this as a cheap discovery filter but MUST NOT rely on it for validation.

### The proof bundle

A proof bundle is the JSON (or CBOR, see below) object returned by the Hydra node HTTP API endpoint:

```
GET <proof-endpoint-base>/snapshot
```

with the shape (JSON encoding):

```json
{
  "tag": "ConfirmedSnapshot",
  "snapshot": {
    "headId": "<hex, 28 bytes>",
    "version": 3,
    "number": 42,
    "confirmed": [ ... ],
    "utxo": { "<txid>#<ix>": { "address": "addr1...", "value": { "lovelace": 1000000 }, ... }, ... },
    "utxoToCommit": null,
    "depositTxId": null,
    "utxoToDecommit": null,
    "accumulator": "<hex, 32 bytes>"
  },
  "signatures": { "multiSignature": [ "<hex, 64 bytes>", ... ] }
}
```

Notes:

- `utxo` is the head's layer-2 UTxO set in standard Cardano wallet shape: an object keyed by `"<txid>#<index>"` with cardano-api `TxOut` values (Conway-era JSON encoding: `address`, `value`, optional `datum`/`datumhash`/`inlineDatum`/`inlineDatumRaw`, `referenceScript`).
- `signatures.multiSignature` is a list of raw 64-byte Ed25519 signatures, hex-encoded, **in the same order as the on-chain `parties` list**.
- A bundle with `"tag": "InitialSnapshot"` denotes a freshly opened head whose layer-2 ledger is empty and carries no signatures; wallets MUST treat funds as in-head under an `InitialSnapshot` only when the on-chain `version` is `0` and the on-chain `accumulator-hash` equals the accumulator hash of the empty set.
- The endpoint responds `404` if the head was never opened.
- The `confirmed`, `utxo`, `utxoToCommit`, and `utxoToDecommit` fields are **not directly covered by the signature**; they are bound to it only through the hashes described next. A wallet MUST NOT treat any of these fields as verified until it has performed the binding checks below.
- The same API is available in CBOR by sending `Accept: application/cbor`; the CBOR encoding uses the same field vocabulary.
- Operators intending browser-wallet consumption MUST serve this endpoint over HTTPS with permissive CORS for `GET`.

### Signable message encoding (`HydraHeadV2`)

The multisignature signs the following message — six fields, each encoded independently as Plutus `Data` and serialized with `serialiseData`, then concatenated **with no framing, tags, or length prefixes between fields**:

```
message = serialiseData(B headId)                 ; bytes .size 28
       || serialiseData(I version)                ; uint
       || serialiseData(I number)                 ; uint
       || serialiseData(B accumulatorHash)        ; bytes .size 32
       || serialiseData(B decommitOutputsHash)    ; bytes .size 32
       || serialiseData(B commitOutputsHash)      ; bytes .size 32
```

where:

```
accumulatorHash     = blake2b_256(compressed G1 accumulator commitment)   ; see next section
decommitOutputsHash = hashOutputs(outputs of utxoToDecommit, or [] if absent)
commitOutputsHash   = sha2_256( hashOutputs(outputs of utxoToCommit, or [] if absent)
                             || depositTxIdBytes )                         ; 32-byte tx id, or empty if absent

hashOutputs(outs)   = sha2_256( concat over outs of serialiseData(toData(txOut)) )
```

Outputs are ordered by ascending `TxOutRef` (lexicographic by transaction id bytes, then numeric by output index) of the input that locates them in the UTxO set. `hashOutputs([])` is `sha2_256` of the empty string.

Each of the `n` signatures is verified as a standard Ed25519 signature of `message` (the message itself, not a pre-hash) under the corresponding party's verification key:

```
valid(bundle) ⟺  |signatures| == |parties|
              ∧  ∀ i.  Ed25519.verify(parties[i], message, signatures[i])
```

Verification MUST fail if the signature count differs from the on-chain party count. This encoding is byte-for-byte the message reconstructed and checked by the layer-1 head validator when the head is closed, contested, incremented, or decremented — a wallet performing this check is running the same verification the chain itself runs.

Test vectors covering every field combination (with/without commit, decommit, deposit) are a required deliverable of the implementation plan; see [Path to Active](#path-to-active).

### Binding UTxOs to the snapshot: the accumulator

The snapshot signature covers only a 32-byte *hash of a commitment* to the UTxO set, so recognizing a specific UTxO as in-head requires binding it to `accumulatorHash`. The accumulator is a KZG-style polynomial commitment over BLS12-381:

1. **Element encoding.** Each `TxOut` in the set contributes one element: `element = sha2_256(serialiseData(toData(txOut)))`, mapped to a scalar as `scalar = blake2b_224(element)` interpreted as a field element.
2. **Set contents.** The committed set is the union of the snapshot's `utxo`, `utxoToCommit` (if present), and `utxoToDecommit` (if present).
3. **Commitment.** The commitment is the multi-scalar multiplication of the set's monomial-basis polynomial coefficients against the public powers-of-tau CRS in G1 — the CRS of the Ethereum **EIP-4844 trusted setup** (a public, widely mirrored artifact). The signed value is `accumulatorHash = blake2b_256(compressed 48-byte G1 commitment)`.

A wallet has two conformant paths to bind UTxOs to the signature:

- **Path A — full recomputation.** Recompute the commitment from the bundle's full UTxO set and check `blake2b_256(commitment) == accumulatorHash` from the signed message. This requires a BLS12-381 MSM of size |set| (available in mature WASM/JS libraries and the EIP-4844 ecosystem tooling) and yields verification of the *entire* displayed set at once.
- **Path B — membership proof.** Verify a per-UTxO KZG membership proof (one pairing check per proof) against the signed commitment. This is cheaper for large heads and requires the proof endpoint to serve membership proofs; the underlying proving machinery already exists in the Hydra node (it is what the layer-1 partial-fanout path consumes), but a public HTTP endpoint for it is a hydra-node deliverable tracked in the [Implementation Plan](#implementation-plan). Path B additionally requires the bundle (or proof response) to include the 48-byte commitment itself, since `accumulatorHash` is a one-way hash of it; the wallet then checks `blake2b_256(commitment) == accumulatorHash` before using it in pairings.

A wallet MUST perform Path A or Path B before displaying any bundle-derived balance as **verified**. A wallet that skips this step MUST NOT use the *verified* display state (a malicious endpoint could otherwise pair a genuine signed header with a fabricated UTxO list).

### Wallet validation algorithm

Given a wallet controlling payment addresses `A` and a discovered head ID `cid` with proof endpoint `E` (see [Discovery](#discovery)):

1. **Anchor.** Locate the head state UTxO by asset `(cid, "HydraHeadV2")`. If absent, the head does not exist or is finalized → no head balance; any prior deposit outputs are evaluated on their own (step 8).
2. **State.** Parse the inline datum. If `Closed` or `FanoutProgress`, go to step 9. If `Open`, extract `parties`, `version`, `accumulator-hash`.
3. **Fetch.** `GET E/snapshot`. On network failure, non-200, or parse failure → display state **UNVERIFIABLE** for any funds previously known to be in this head.
4. **Signature.** Reconstruct the signable message from the bundle's `headId`, `version`, `number`, its recomputed hash fields, and verify all `|parties|` Ed25519 signatures positionally. Any failure → **UNVERIFIABLE**.
5. **Consistency.** Check `bundle.headId == cid` and `bundle.version == datum.version`. A version mismatch means the bundle is stale relative to layer 1 (or ahead of it); the wallet MAY retry/refetch and MUST otherwise report **UNVERIFIABLE** (stale).
6. **Set binding.** Bind the UTxO set to `accumulatorHash` via Path A or Path B. Failure → **UNVERIFIABLE**.
7. **Selection.** Select entries of the verified set whose output address ∈ `A`. Sum for balance display; annotate with the head ID and `"as of snapshot <number> (version <version>)"`. Display state **VERIFIED_IN_HEAD**. Entries in `utxoToDecommit` are in the process of leaving the head and SHOULD be annotated as pending withdrawal.
8. **Deposits.** Independently of steps 3–7, for each unspent output at the deposit validator address whose datum's `commits` decode to outputs paying to addresses in `A`: if `deadline` is in the future → **PENDING_DEPOSIT** (funds escrowed toward head `cid` from the datum); if `deadline` has passed and the deposit is unspent → **RECOVERABLE** (the wallet SHOULD offer recovery, which is an ordinary layer-1 transaction, though constructing it is out of scope of this CIP). A spent deposit needs no display of its own: if claimed by the head, the funds appear via steps 3–7 once a snapshot at the new version confirms; a wallet MAY show a transitional *claimed, awaiting confirmation* annotation when it observes the claiming increment transaction on layer 1 before a matching bundle is available.
9. **Closing head.** If the head datum is `Closed` (or `FanoutProgress`): the wallet MUST NOT present in-head funds as spendable; it SHOULD display the last verified in-head balance annotated as **HEAD_CLOSING** together with the contestation deadline from the datum, and after fanout it will observe the resulting outputs as ordinary layer-1 UTxOs.

Wallets SHOULD cache the last successfully verified bundle per head and use it (clearly marked as *last verified at snapshot N*) when the endpoint is temporarily unreachable, rather than flapping balances.

### Display states

| State | Trigger | Mandatory wallet behavior |
|---|---|---|
| `PENDING_DEPOSIT` | Unspent deposit output, deadline in future, decoded outputs pay the wallet | Show amount + destination head ID; not spendable; verified from L1 alone |
| `RECOVERABLE` | Unspent deposit output, deadline passed | Show amount; indicate recoverability |
| `VERIFIED_IN_HEAD` | Steps 1–7 all pass | Show as legitimate balance, segregated from L1 balance, annotated with head ID and snapshot number; not spendable via ordinary L1 tx building |
| `UNVERIFIABLE` | Endpoint unreachable, signature/binding/consistency failure | MUST be flagged distinctly — neither silently hidden nor shown as a normal balance; SHOULD state the reason (unreachable vs. failed verification) |
| `HEAD_CLOSING` | Head datum `Closed`/`FanoutProgress` | Show last verified balance, contestation deadline; not spendable |

The two non-negotiable rules, mirroring the requirements of hydra#2818: a UTxO with a **valid** verification chain is displayed as a legitimate balance, and a UTxO whose chain **cannot be verified** is *flagged*, never silently hidden and never blended into the spendable L1 balance.

### Discovery

Recognition requires the wallet to learn, for a given head, **where** the proof bundle is served. This proposal standardizes an on-chain hint and permits out-of-band configuration:

1. **On-chain endpoint hint (RECOMMENDED).** The transaction that creates a deposit SHOULD carry transaction metadata, under a metadata label to be registered for this CIP upon number assignment, of the form:

   ```cddl
   endpoint-hint = { 0 : bytes .size 28,       ; head ID
                     1 : [+ tstr] }            ; HTTPS base URIs of proof endpoints, in preference order
   ```

   URIs longer than 64 characters are split into a metadata text array per standard practice (concatenated on read). Since the depositing application constructs the deposit transaction, it is the natural party to embed the hint, and the hint travels with exactly the transaction a wallet already inspects to classify the deposit. The hint is a *pointer, not a claim*: everything obtained from the endpoint is verified against layer 1, so a wrong or malicious hint can only produce `UNVERIFIABLE`, never a forged `VERIFIED_IN_HEAD`.

2. **Out-of-band configuration.** Wallets MAY additionally accept endpoint mappings (head ID → URI) from application-level channels or user configuration. The verification requirements are identical regardless of how the endpoint was discovered.

A conformant wallet MUST NOT require any deployment-specific code: given the on-chain data and a reachable conformant endpoint, recognition works for any head.

### Versioning

Every artifact this CIP depends on — the head validator address, the deposit validator address, the ST asset name, the datum schemas, the signable message layout, and the accumulator construction — is fixed by the deployed Hydra protocol scripts, and those deployments are identified on chain by the ST asset name (`"HydraHeadV2"`) and, more precisely, by the head validator script hash.

This document specifies protocol version 2 exclusively. A future Hydra protocol version that changes any covered encoding is expected to change its ST asset name (as version 2 did); recognition support for it requires a versioned addendum to this CIP mapping the new asset name / script hashes to the new encodings. Wallets MUST NOT apply this specification to heads whose state token asset name differs from `"HydraHeadV2"`, and SHOULD maintain the (asset name → encoding rules) mapping as data rather than assume this CIP's rules are universal.

Within protocol version 2, the signable message layout and datum schemas defined here are a **compatibility commitment** requested of the Hydra project: they are today internal encodings, and their adoption as a public stable interface (with test vectors and a documented deprecation path) is the central ask of this proposal's implementation plan.

## Rationale: How does this CIP achieve its goals?

### Reusing the snapshot multisignature instead of inventing an operator attestation

The requirements in hydra#2818 asked for an "operator attestation" of the L1↔L2 link. During drafting it became clear that Hydra already produces a strictly stronger artifact: the confirmed snapshot multisignature, signed by *every* participant and verified by the layer-1 validator itself during close/contest/increment/decrement. Building the CIP on it has three decisive advantages: (a) **no new trust assumption** — a single operator's signature would let one party fabricate balances, whereas the multisignature requires unanimous collusion, the same bound the head protocol itself has; (b) **no Hydra protocol change** — heads produce this artifact today, and `GET /snapshot` already serves it with signatures; (c) **wallet verification equals chain verification** — the wallet checks the same bytes the on-chain validator checks, so there is no parallel format to drift.

### Why the accumulator-binding step is mandatory

The signature covers only the accumulator hash, not the UTxO list. An earlier Hydra protocol signed a direct hash of the UTxO set, but since protocol 2.2 the set is committed via a KZG accumulator to enable selective/partial fanout. A wallet that verifies the signature but not the set binding would trust the endpoint's UTxO list — precisely the forgery vector this CIP exists to close. The cost is real (an MSM or a pairing check) but bounded, standard (EIP-4844 tooling), and parallelizable; and Path B reduces the per-wallet cost to one pairing per displayed UTxO. The alternative — declaring the endpoint trusted for set contents — was rejected as it degrades the guarantee from "head consensus" to "one server's word" exactly where it matters most.

### Why recognition only

A full wallet-participation standard (in-head signing, head-aware transaction construction, session keys, contest alerting) is a much larger design with open questions about key custody and liveness duties. Recognition is the smallest standard that unblocks adoption — it makes committed funds *visible and trustworthy*, which every head application needs, while leaving participation to applications (as in the delegated head topology, where clients keep their spending keys and operators hold snapshot keys). The display-state machine was deliberately designed so that a future participation CIP extends it (e.g. making `VERIFIED_IN_HEAD` funds spendable through a head-aware path) without changing recognition semantics — this addresses hydra#2818's P2 requirement that recognition not block later interactivity.

### Why deposits get a trustless special case

Because the deposit datum embeds the deposited outputs in full (pre-serialized `TxOut`s), the *pending deposit* state is verifiable purely from layer 1. This closes the worst UX gap — the moment funds "vanish" — even for heads whose proof endpoint is unreachable, and it required no design invention, only documentation of the existing datum.

### Discovery: metadata hint over a registry

Alternatives considered: a global on-chain registry of head endpoints (heavyweight, governance-laden, and stale-prone); putting the URI in the head's own datum (bloats a security-critical datum with display concerns and cannot be updated without a protocol change); CIP-30-extension push from the dApp (couples recognition to a live dApp session — fails the "user opens wallet a week later" case). Transaction metadata on the deposit is cheap, travels with the transaction the wallet already parses, needs no protocol change, and is safe because the endpoint is untrusted. Operators can rotate endpoints for *new* deposits; out-of-band configuration covers rotation for old ones. This remains the design area most open to editor and Hydra-team input; the authors consider the verification chain (the bulk of this CIP) independent of the eventual discovery mechanism.

### Open questions

1. **Encoding freeze.** The signable message layout changed twice in the six months before this draft (binding commit/decommit output sets, then deposit IDs, into the signature). This CIP asks the Hydra team to ratify the version-2 layout as a public interface; the ask is deliberately framed so the interface *commitment* is the Hydra team's decision, with this document as the strawman. (The layout is exercised by the deployed on-chain validators, so within deployed protocol version 2 it is de facto frozen already.)
2. **Membership-proof endpoint.** Path B needs `GET /snapshot/utxo/<txid>#<ix>/membership-proof` (or similar) on hydra-node; naming and shape belong to the Hydra API design.
3. **Metadata label registration** for the endpoint hint, upon CIP number assignment.
4. **Closed-head balance semantics** during contestation: whether wallets should attempt to track contest transactions to refine the displayed outcome, or the conservative `HEAD_CLOSING` state suffices (this draft chooses the latter).

### Backward compatibility

This CIP defines new wallet behavior only; it changes no on-chain or node behavior and cannot conflict with existing wallet function. Heads created by Hydra protocol versions whose state token is not `"HydraHeadV2"` are out of scope. Wallets without this CIP behave as today — which is the problem statement.

## Path to Active

### Acceptance Criteria

- [ ] The Hydra project publishes conformance test vectors for the version-2 signable message encoding (all combinations of present/absent `utxoToCommit`, `depositTxId`, `utxoToDecommit`) and for the accumulator element/commitment construction, and documents the layout in this CIP's terms.
- [ ] A reference validation implementation (TypeScript/WASM) exists that, given a head ID, a layer-1 data source, and a proof endpoint, returns the display state and verified balance for a set of addresses — with no deployment-specific code.
- [ ] Given a UTxO committed to a head and a reachable conformant proof endpoint, at least one production wallet displays the UTxO as a legitimate (verified) balance.
- [ ] Given a missing or failing verification chain, that wallet flags the funds as unverifiable rather than hiding them or displaying them as a normal balance.
- [ ] A conformant wallet recognizes head UTxOs across **at least two independent operator deployments** with no deployment-specific code.

### Implementation Plan

1. **Hydra node (proof surface).** Confirm/stabilize `GET /snapshot` as the proof bundle (already implemented); add the optional membership-proof endpoint for Path B; publish test vectors. The relevant signing, verification, and proving machinery all exists in the node today — this is exposure and documentation work, plus the ADR-level decision to treat the encodings as a public interface.
2. **Reference implementation.** A standalone verification library (the ledger-shape handling generalizing existing SDK work in the ecosystem, e.g. the `@hydra-sdk/*` packages), consuming only public artifacts: chain data, the proof bundle, and the EIP-4844 CRS.
3. **Wallet integration.** Guidance and integration support for at least Lace and Eternl, using the reference library.
4. The authors will maintain the draft through the CIP process and coordinate with the Hydra team via [cardano-scaling/hydra#2818](https://github.com/cardano-scaling/hydra/issues/2818).

## References

- Requirements: [cardano-scaling/hydra#2818 — Hydra UTxO Wallet support](https://github.com/cardano-scaling/hydra/issues/2818)
- [Hydra Head protocol documentation](https://hydra.family/head-protocol/) and formal specification (machine-checked, in-repo under `spec/`)
- [Delegated head topology](https://hydra.family/head-protocol/topologies/delegated-head)
- Hydra ADR-33 (directly open heads, deposits replace commits) and ADR-34 (binary CBOR client API)
- [CIP-30 — Cardano dApp-Wallet Web Bridge](https://cips.cardano.org/cip/CIP-0030)
- [CPS-0010 — Wallet Connectors](https://cips.cardano.org/cps/CPS-0010)
- EIP-4844 KZG ceremony / trusted setup (source of the accumulator CRS)

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).

Portions of this document were drafted with AI assistance (Claude); all protocol facts were verified against the Hydra source repository at version 2.3.0.
