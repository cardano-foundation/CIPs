---
CIP: ?
Title: Token-Owned Addresses
Category: Tokens
Status: Proposed
Authors:
    - Marius Georgescu <georgescumarius@live.com>
Implementors:
    - Marius Georgescu <georgescumarius@live.com>
Discussions:
    - https://github.com/cardano-foundation/CIPs/pull/1200
Created: 2026-05-19
License: CC-BY-4.0
---

## Abstract

Token-Owned Addresses (TOA) define a deterministic Cardano enterprise script address for a controlling asset class intended to represent a unique non-fungible token. For TOA v1, the address is derived from the hash of a canonical Plutus V3 validator applied to a single canonical parameter value containing `(toa_version = 1, policy_id, asset_name)`.

A TOA is spendable by any transaction that consumes exactly one unit of the controlling asset class as input, produces exactly one unit of that same asset class as output, and does not mint or burn that asset class in the same transaction. The TOA validator does not require a specific signer, wallet identity, or external ownership registry; authorisation is based on the presence of the controlling NFT in consumed transaction inputs.

The standard is an off-chain interoperability CIP. It does not introduce a new ledger address type. It standardises the validator artifact, parameter encoding, address derivation, validator rules, wallet and indexer behaviour, and test vectors needed for wallets, explorers, dApps, and libraries to derive and display the same TOA for the same controlling asset class.

## Motivation: Why is this CIP necessary?

On Cardano, there is no native concept of an account owned by a token. Other ecosystems address this need through different patterns:

- **Ethereum / EVM:** [ERC-6551](https://eips.ethereum.org/EIPS/eip-6551) Token-Bound Accounts are the closest conceptual prior art — every NFT has a deterministic account address derived from its contract address and token ID.
- **Solana:** Associated Token Accounts (ATAs) demonstrate deterministic address derivation from canonical inputs. ATAs are token accounts owned by the SPL Token program, derived from a wallet/mint pair; they are not token-*owned* accounts, but they are prior art for the derivation-from-canonical-inputs pattern.
- **Object-based chains:** Sui and Aptos provide object/resource ownership models that make asset-owned state more native than it is on Cardano.

Token-gating patterns can already be implemented on Cardano today using Plutus validators, but each dApp implements them differently. This produces three concrete problems:

1. **Fragmentation.** dApp-specific address derivation means an NFT may be associated with one address in one dApp and a different address in another, with no canonical answer.
2. **Wallet UX.** Wallets cannot display NFT-controlled balances, deposit into NFT-derived addresses, or warn about NFT-control transfer because there is no standard pattern to recognise.
3. **Indexer and explorer support.** Indexers cannot label addresses as token-owned because there is no canonical derivation to follow.

This CIP standardises the pattern. A single canonical validator, applied to a single canonical parameter shape, yields a single canonical address per `(policy_id, asset_name)`. Every wallet, indexer, and dApp implementing the standard derives the same address for the same controlling asset class.

**Representative use cases:**

- **NFT-owned vaults and inventories** — character or item NFTs holding ADA, sub-tokens, equipment, or per-NFT state. Control transfers atomically with the NFT.
- **Revenue routing per NFT** — royalties, licenses, and subscription proceeds sent directly to the NFT's address. The party or script able to consume the controlling NFT is the current revenue controller; no re-keying is required on transfer.
- **Role and authority NFTs** — a `Treasurer`, `Admin`, or governance NFT controls an operational address. Transferring the NFT transfers the authority without redeploying scripts or rotating signers.
- **DeFi-position auxiliary state** — LP-receipt or strategy NFTs holding ancillary state — accumulated rewards, sub-positions, history markers, or receipts — that the host protocol does not encode in its own UTxOs.
- **Account-by-NFT (token-bound accounts)** — the NFT acts as a transferable identity primitive. The TOA is "the account belonging to this NFT," and inherits the control logic of whatever script currently holds the NFT — lending, escrow, fractionalisation, marketplace, DAO. This composability is intentional; see *Security Considerations — Temporary control during lending, escrow, or rental*.

**Stakeholders.** Wallets (display, deposit, spend); indexers and explorers (canonical derivation, labelling); dApp authors (target a single standard rather than a bespoke pattern); NFT issuers (predictable per-NFT addressing for vault, royalty, and membership use cases).

## Specification

The key words **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, and **MAY** in this document are to be interpreted as described in [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119) and [RFC 8174](https://www.rfc-editor.org/rfc/rfc8174) when, and only when, they appear in all capitals.

The TOA address is obtained as follows:

1. A canonical Plutus V3 validator is defined (`TOA Validator v1`).
2. The validator is parameterised with a **single compile-time parameter**: the PlutusData value `TOAParamsV1` defined in *Canonical Parameter Encoding* below, containing `(toa_version, policy_id, asset_name)`.
3. The parameterised script is canonically serialised.
4. The script hash is computed as the Cardano ledger Plutus V3 script hash of the applied script.
5. The hash becomes the payment credential of a Cardano address.
6. No stake credential is attached in TOA v1.
7. The result is a deterministic enterprise script address for that NFT.

TOA v1 commits explicitly to **one** parameter. Implementations MUST apply the validator with a single PlutusData argument matching the CDDL `toa_params_v1` shape. An implementation that applies the validator with three separately-encoded arguments produces a different UPLC byte string after parameter application — and therefore a different script hash — even when the three underlying values are identical. Such an implementation is non-conforming.

Delegated/staking TOAs are explicitly out of scope for v1: any optional stake credential would create multiple valid addresses for the same controlling NFT, breaking the address-per-asset-class invariant. A future CIP may introduce a delegated variant under a new `toa_version`.

### Definitions

- **Token-Owned Address (TOA):** a Cardano enterprise script address whose payment credential is the hash of the `TOA v1` validator applied to a specific `(toa_version, policy_id, asset_name)`. The TOA exists conceptually whether or not any UTxO currently sits at it.
- **Controlling NFT:** the asset class `(policy_id, asset_name)` baked into a TOA's parameters. The term "Controlling NFT" is used throughout this CIP for readability, but TOA v1 operates mechanically on an asset class; historical uniqueness of that asset class is not proven by the validator (see *Policy Classification*).
- **Controller:** any party able to construct a transaction that consumes a UTxO containing the controlling NFT and preserves that NFT in the outputs. In the ordinary case this is the NFT holder. If the controlling NFT is inside its own TOA (see *Self-deposit*), control becomes permissionless.
- **Carry-through:** the validator requirement that the controlling NFT must appear in transaction outputs with total quantity exactly 1. The recipient of the carry-through output is unconstrained by the validator.
- **Self-deposit:** the case where the controlling NFT is sent to its own TOA. Self-deposit intentionally makes the TOA permissionlessly spendable (subject only to standard ledger witness requirements such as a datum preimage for a `Datum Hash` UTxO); see *Security Considerations — Self-deposit of the controlling NFT* for the full explanation.
- **TOA deposit:** a UTxO sent to a TOA address. Classified by the *datum shape* of the UTxO into one of four categories:
  - **Unit Datum** — inline datum `Constr 0 []` (CBOR `d8 79 80`). RECOMMENDED for generic deposits intended to be spendable by any conforming TOA wallet.
  - **Inline Datum** — any non-unit inline datum. MAY carry application-specific payloads (offer markers, inventory metadata, badges, receipts, state markers). Wallets that do not recognise the schema MUST treat the deposit as opaque value plus an unknown datum payload; they MUST NOT assume the datum is semantically meaningful unless they understand the schema.
  - **Datum Hash** — a bare 32-byte hash with no on-chain preimage. Spending requires the off-chain datum preimage.
  - **No Datum** — no datum attached.

  The TOA v1 validator MUST NOT reject a UTxO based on its datum classification.
- **`toa_version`:** an integer baked into the validator parameters that pins the standard revision. A change in `toa_version` yields a different address for the same `(policy_id, asset_name)`.

### Canonical Parameter Encoding (CDDL)

```cddl
toa_params_v1 = #6.121([
    toa_version : uint,                ; = 1 in v1
    policy_id   : bytes .size 28,      ; blake2b-224 of minting script
    asset_name  : bytes .size (0..32), ; raw asset name bytes
])
```

`#6.121` is the CBOR tag for `Constr 0` in PlutusData. Serialisation MUST be canonical CBOR per RFC 8949 §4.2.1 — definite-length items, smallest integer form. This is the standard PlutusData canonical encoding.

### Address Derivation

TOA v1 targets **Plutus V3**. Validator hashes depend on the Plutus language version, so this is pinned. V2 fallback is out of scope for `toa_version = 1`.

```
1. params       := toa_params_v1(toa_version = 1, policy_id, asset_name)
2. applied      := apply_params(toa_v1_compiled, params)
3. script_bytes := ledger_serialised_plutus_script(applied)
4. hash         := blake2b_224(0x03 || script_bytes)        // 0x03 = Plutus V3 language tag
5. cred         := payment_credential(script_hash = hash)
6. address      := enterprise_address(network, cred)        // no stake credential in v1
7. bech32       := encode_bech32(prefix in {addr, addr_test}, address)
```

The TOA script hash is the **Cardano ledger Plutus V3 script hash of the applied Plutus V3 script**, not a CIP-defined formula computed in isolation. Implementations MUST compute this hash exactly as `cardano-ledger` / `cardano-api` does for `PlutusScriptV3`; the pseudocode above is an **explanatory form**, not an independent normative algorithm.

The explanatory form unwraps to: `blake2b_224(language_tag ‖ ledger_serialised_script_bytes)`, where the Plutus V3 language tag is `0x03` and `ledger_serialised_script_bytes` is the form documented in `Cardano.Ledger.Plutus.Language.hashPlutusScript`. Concretely, that is the **single** CBOR bytestring wrapping the flat-encoded UPLC program after parameter application — the same bytes that appear in the transaction's `script` field. The CIP test vectors are the authoritative cross-check: any implementation that reproduces them byte-for-byte has the encoding right regardless of which intermediate representation it computes through.

Implementations MUST NOT hash a `cardano-cli` TextEnvelope JSON file directly. The two common encoding mistakes that yield non-conforming hashes are:

- Hashing the raw flat bytes without the surrounding CBOR bytestring wrapper.
- Hashing a `cardano-cli` TextEnvelope `cborHex` field directly: that field is itself a CBOR-encoded bytestring whose *content* is the serialised script, so one CBOR-decode step is required before hashing.

Header bytes follow [CIP-0019](https://cips.cardano.org/cip/CIP-0019); the resulting addresses are type-7 (enterprise script), header byte `0b0111_xxxx` where the low nibble encodes the network (`0x0` testnet, `0x1` mainnet) — i.e., concrete header bytes `0x70` and `0x71`.

### Validator Rules

Let `ac = (policy_id, asset_name)` be the controlling asset class.

A TOA-spending transaction is valid only if **all** of the following hold:

1. **No mint or burn of the controlling asset class.**
  ```
  valueOf(txInfoMint, ac) == 0
  ```

2. **Total quantity of `ac` in consumed transaction inputs is exactly 1.**
  ```
  sumSpentInputs(ac) == 1
  ```
  `sumSpentInputs(ac)` is computed over **regular spent (consumed) transaction inputs only**. **Reference inputs are explicitly excluded** and do not authorise TOA spending; including the controlling NFT in a reference input MUST NOT contribute toward satisfying this rule.

3. **Total output quantity of `ac` is exactly 1.**
  ```
  sumOutputs(ac) == 1
  ```

The validator does **not** require the controlling NFT input to come from a key wallet, from the transaction signer, or from an address different from the TOA itself. Control is defined purely by NFT presence in **spent** transaction inputs.

**Self-deposit.** If the controlling NFT is locked inside its own TOA, any transaction author who can provide the required ledger witnesses — including any required datum preimage for a `Datum Hash` UTxO — may spend that TOA UTxO by consuming it and carrying the NFT through. See *Security Considerations — Self-deposit of the controlling NFT*.

Through these rules, the standard states clearly:

> You can spend from a token-owned address only if exactly one unit of the controlling NFT enters as input and exactly one unit leaves as output, and no minting or burning of that asset class occurs in the same transaction.

The rationale for choosing transaction-local NFT uniqueness over an attempt at historical-supply enforcement, and for excluding reference inputs, is in *Rationale — Design Decisions*.

### Datum and Redeemer Schema

For Plutus V3 spending scripts, the datum is **not** a required validator argument: per [CIP-0069](https://cips.cardano.org/cip/CIP-0069), the datum argument is removed from the validator interface, and the script accesses the spending UTxO's datum (if any) via `ScriptInfo` — the `SpendingScript` variant carries `Maybe Datum`. TOA v1 does not inspect this field, so absence of datum, hash-only datum, and non-unit inline datum MUST NOT by themselves cause the spend to fail. Wallet and indexer conventions are stated below as SHOULD-level guidance.

**TOA deposits SHOULD use Unit Datum**, i.e. the inline PlutusData value `Constr 0 []` (CBOR `#6.121([])`, byte sequence `d8 79 80`). This makes such deposits trivially recognisable to wallets, explorers, and indexers, and lets any conforming wallet spend them without recovering an off-chain datum preimage.

Deposits MAY use **Inline Datum** when they carry application-specific data — marketplace offer markers, state markers, inventory, badges, receipts. The TOA validator does not inspect or interpret application datums; wallets that do not recognise the schema MUST treat the deposit as opaque value plus an unknown datum payload (and SHOULD surface the `Inline Datum` classification in UI rather than silently swallowing it).

**The TOA v1 validator MUST NOT fail based on the datum classification.** Datum shape determines *wallet and indexer interpretation*, not on-chain spend validity. UTxOs classified as **No Datum**, **Datum Hash**, or non-unit **Inline Datum** remain spendable if and only if the rules in *Validator Rules* are satisfied. See *Definitions — TOA deposit*.

**The spend redeemer SHOULD be unit** (`Constr 0 []`, same encoding as above). The validator does not inspect the redeemer; using a canonical redeemer improves recognisability and avoids unnecessary implementation divergence, but a non-unit redeemer does not by itself cause a TOA spend to fail.

### Policy Classification

TOA v1 cannot prove on-chain that the controlling asset class is historically unique. Implementations therefore use the following policy classifications to determine what safety claims they may make to users.

- **`ProvenClosed`** — the controlling asset's minting policy has been verified to be incapable of further minting or burning. `ProvenClosed` SHOULD be reserved for cases such as: native scripts whose relevant time-lock has provably expired; policies listed in an accepted audited registry; or policies verified by an implementation-specific trusted analysis mechanism. Implementations MUST NOT tag a policy as `ProvenClosed` without one of these grounds.
- **`KnownOpen`** — the minting policy is known to permit further minting or burning under some condition — e.g. an unrestricted native multi-sig, or a Plutus policy with a visible mint/burn path.
- **`Unknown`** — closure has not been proven. By default, **every controlling policy is `Unknown`** unless explicitly upgraded to `ProvenClosed` or downgraded to `KnownOpen`. Static analysis of arbitrary Plutus policies is not generally automatable, so most policies encountered in the wild will remain `Unknown`.

Wallets, indexers, and other tooling that claim TOA v1 support MUST assign each displayed TOA's controlling policy one of these three classifications. The default classification MUST be `Unknown`. Implementations MAY upgrade a policy to `ProvenClosed` or downgrade it to `KnownOpen` using implementation-specific analysis, audited registries, or trusted attestations; the **classification mechanism itself** (static analysis, registry lookup, audited list, third-party attestation) is out of scope for TOA v1. Implementations MUST NOT present a TOA as safely controlled by a unique NFT unless the controlling policy is classified as `ProvenClosed`. See *Wallet Behaviour*, *Indexer and Explorer Behaviour*, and *Security Considerations — Permanent loss and policy-permissiveness risks*.

### Mandatory Normative Artifacts

Two hashes are distinguished throughout this CIP:

- **Template hash** — the hash of the un-parameterised `TOA v1` validator (a single value pinned by this CIP), concretely `blake2b_224(0x03 || unapplied_script_bytes)`. It identifies the TOA validator code itself, independently of any NFT.
- **Applied script hash** — the hash of the validator **after** parameter application; this is the per-NFT TOA script hash and the payment credential of every TOA address, computed the same way over the applied script bytes.

The compiled, **unapplied** Plutus V3 validator artifact, its build toolchain version(s), and its resulting template hash are the normative reference for every derived TOA address. Per *Reference Artifacts — What lives where*, these artifacts are published in an external repository identified by content hash; the CIP folder itself contains only this README and the parameter-encoding CDDL. The Plinth source alone is not sufficient to define the standard, because different compiler/toolchain versions may produce different UPLC bytes for the same source, which would change the template hash and therefore every derived address — implementations MUST verify they hold the exact bytes referenced below.

| Artifact | Reference |
|---|---|
| Plinth source | [`Onchain/Validators/ToaV1Validator.hs`](https://github.com/en7angled/toa/blob/0.1.1/src/lib/onchain-lib/Onchain/Validators/ToaV1Validator.hs) at `en7angled/toa@0.1.1` |
| Compiled unapplied UPLC artifact | [`validators/ToaV1.uplc`](https://github.com/en7angled/toa/blob/0.1.1/validators/ToaV1.uplc) — 476 bytes, blake2b-256 = `7f78c5524a00852eb51ee760f86a3f0cce4535b446e0c03d6cdc35eb6de0092b` |
| Pinned toolchain | GHC 9.6 series; Plutus Core target version 1.1.0 (`-fplugin-opt PlutusTx.Plugin:target-version=1.1.0`, i.e. `plcVersion110`); `plutus-tx`, `plutus-tx-plugin`, `plutus-ledger-api` (Conway-era IOG CHaP pin). Reproducible via the [`cabal.project.freeze`](https://github.com/en7angled/toa/blob/0.1.1/cabal.project.freeze) snapshot at tag `0.1.1`. |
| Template hash — `blake2b_224(0x03 \|\| unapplied_script_bytes)` (28-byte output) | `129181a58ca3716aada61244d3d4210bff5a7235f709189af2596dc0` |

The compiled validator artifact is authoritative. Source-level implementation choices (which Plutus ledger API surface is used, which optimisation techniques are applied, etc.) are non-normative except insofar as they produce the referenced compiled artifact and template hash. Such notes belong in the validator's own README, audit notes, or an implementation appendix.

### Wallet Behaviour

Wallets that integrate TOA have the following obligations.

**MUST:**

- **Derive TOA addresses using the canonical algorithm** in *Address Derivation*. Wallets MUST NOT infer TOA identity from any other heuristic.
- **Surface the TOA version** to the user before any deposit or spend. A v1 TOA and a hypothetical v2 TOA with the same `(policy_id, asset_name)` resolve to different addresses; users must know which version they are interacting with. (See also: *Versioning*.)
- **Warn that TOA control follows the ability to consume the controlling NFT.** Any party or script that can cause the controlling NFT to be consumed as a transaction input controls the TOA for that transaction. Sending, lending, escrowing, renting, or otherwise transferring practical control of the controlling NFT may transfer practical control of the TOA. Sending the controlling NFT to its own TOA MUST be described as making the TOA permissionlessly spendable, subject to ordinary ledger witness requirements such as datum-preimage availability for `Datum Hash` UTxOs, not merely as "transferring the NFT to another address." (See *Security Considerations — Self-deposit of the controlling NFT* and *Security Considerations — Temporary control during lending, escrow, or rental* for the full explanations.)
- **Assign a policy classification, default `Unknown`.** Wallets MUST assign each TOA's controlling policy one of `ProvenClosed`, `KnownOpen`, or `Unknown` (see *Policy Classification*). The default MUST be `Unknown`. Implementations MUST NOT present a TOA as safely controlled by a unique NFT unless the controlling policy is classified as `ProvenClosed`. Wallets MUST warn for `KnownOpen` and `Unknown` policies (see *Security Considerations — Permanent loss and policy-permissiveness risks*).
- **Satisfy minimum-UTxO ADA for TOA deposits.** TOA outputs are normal Cardano UTxOs; wallets MUST ensure each TOA deposit output satisfies the current **minimum-UTxO** requirement for the full `Value` and datum shape being deposited. Token-heavy TOA deposits (many policy IDs, many asset names, or a large inline datum) may require substantially more ADA than a pure-ADA deposit. Wallets SHOULD compute the min-UTxO from **current protocol parameters at the moment of transaction construction**, not from cached or hard-coded defaults.
- **Surface the datum classification** of every TOA UTxO. Each UTxO falls into exactly one of `Unit Datum`, `Inline Datum`, `Datum Hash`, or `No Datum` (see *Definitions — TOA deposit*). Wallets MUST display this classification before any spend, because it affects whether spending requires off-chain data (a `Datum Hash` UTxO cannot be spent without the off-chain datum preimage) and whether the deposit followed the canonical TOA convention. Wallets MUST NOT silently coerce all classifications into a single bucket.

**SHOULD:**

- **Display the [CIP-0014](https://cips.cardano.org/cip/CIP-0014) fingerprint** of the controlling NFT (`asset1...`) alongside the TOA address, so users can recognise which asset controls a given TOA without manually decoding `(policy_id, asset_name)`.
- **Label TOA addresses** distinctly from regular wallet addresses in UI (e.g. "Token-Owned Address for asset X"), so users do not confuse a TOA with a personal address.
- **Default the NFT carry-through recipient to the spending user's own wallet.** The validator permits any recipient (e.g. atomic-sale spends), but the safe default in a wallet UI is to return the NFT to the user; any other recipient should require an explicit confirmation to avoid accidental NFT loss. If the carry-through recipient is the TOA itself, the wallet MUST warn that this makes the TOA permissionlessly spendable, subject to ordinary ledger witness requirements such as datum-preimage availability for `Datum Hash` UTxOs (per the MUST "Warn that TOA control follows the ability to consume the controlling NFT" above).
- **Treat self-deposit as an advanced action.** Wallets should require explicit confirmation before allowing the controlling NFT to be sent to its own TOA. Wallets MAY also offer the action only behind an "advanced" toggle.
- **Warn when key-loss risk is elevated.** Wallets should warn before deposits to a TOA whose controlling NFT is held in cold storage or otherwise at elevated key-loss risk, since loss of the controlling key renders the TOA permanently inaccessible.
- **Warn before constructing a spend of a `Datum Hash` UTxO.** The UTxO is spendable per *Validator Rules*, but spending requires the off-chain datum preimage in the witness set. Wallets SHOULD surface this requirement and SHOULD NOT attempt to build the spend transaction without the preimage available.
- **Surface `No Datum` and non-unit `Inline Datum` UTxOs as outside the canonical convention.** These deposits are spendable per *Validator Rules* but did not arrive through a recognised `Unit Datum` workflow. Wallets SHOULD surface the classification so users understand the UTxO does not match the recommended TOA pattern.

**MAY:**

- **Accept a CIP-0014 fingerprint** as a lookup key, resolving it to `(policy_id, asset_name)` via an indexer before address derivation.
- **Filter or hide spam UTxOs** at a TOA in the UI, to reduce visual clutter and improve spend-cost predictability. The validator does not require this; it is a UX choice. Wallets that filter spam MUST still preserve access to the raw UTxO set when the user requests it (e.g. an "advanced" view or an explicit reveal).

### Indexer and Explorer Behaviour

Indexers and explorers that claim TOA v1 support address the read-side of TOA: derivation, display, and UTxO enumeration. Where their obligations overlap with *Wallet Behaviour*, this section back-references rather than restates.

**MUST:**

- **Derive TOA addresses from the canonical applied validator hash** per *Address Derivation*. Indexers MUST NOT infer TOA identity from datum content, address-labelling conventions, or any other heuristic.
- **Preserve raw UTxO access.** Even when the UI hides or collapses spam UTxOs (see MAY below), the indexer MUST expose the full raw UTxO set at a TOA address — via an "advanced" view, an explicit reveal, or an API endpoint that returns the unfiltered UTxO set.
- **Assign a policy classification, default `Unknown`**, per *Policy Classification*. Indexers MUST attach the classification to every TOA they display and MUST NOT present a TOA as safely controlled by a unique NFT unless the controlling policy is `ProvenClosed`.

**SHOULD:**

- **Display the TOA version**, the controlling policy ID, the controlling asset name as both raw hex and (where decodable) UTF-8, the CIP-0014 fingerprint, the policy classification, and whether the controlling NFT currently appears at its own TOA (self-deposit state).
- **Label TOA addresses** distinctly from regular script addresses (e.g. "Token-Owned Address for asset X").
- **Surface the control-follows-NFT warning** described in *Wallet Behaviour* on any UI that displays a TOA balance or recent activity. A self-deposited TOA SHOULD be signalled as currently permissionlessly spendable, subject to ordinary ledger witness requirements such as datum-preimage availability for `Datum Hash` UTxOs.

**MAY:**

- **Filter or hide spam UTxOs** in UI, subject to the raw-UTxO-access MUST above.
- **Accept a CIP-0014 fingerprint** as a lookup key, resolving it to `(policy_id, asset_name)` before address derivation.

### Public API and Transaction Shapes

The *Validator Rules* and *Test Vector Format* define TOA v1 conformance. Any implementation that derives the expected addresses (per *Address Derivation* and the address-derivation test vectors) and constructs transactions satisfying *Validator Rules* (cross-checked against the validator-scenario test vectors) is conforming. Wallets and libraries are free to construct transactions in any language and using any builder; no specific transaction-template DSL or codegen toolchain is required.

A non-normative [Tx3](https://github.com/tx3-lang) transaction-shape file (`toa.tx3`) MAY be published externally as a reference for implementers. Where any reference artifact (including a Tx3 file or its generated bindings) disagrees with the validator rules or test vectors, the validator rules and test vectors prevail (see *Reference Artifacts — Normative components*).

### Reference Artifacts

#### Normative components

The normative components of TOA v1 are:

- the compiled, **unapplied** Plutus V3 validator artifact and its documented template hash (see *Mandatory Normative Artifacts*);
- the canonical parameter encoding (the CDDL in *Canonical Parameter Encoding*);
- the address-derivation procedure (in *Address Derivation*);
- the validator rules (in *Validator Rules*);
- the normative test vectors (in *Test Vector Format*).

The Plinth source is required for auditability and reproducibility, but conformance is determined by the compiled, unapplied Plutus V3 validator artifact, its documented template hash, and the normative test vectors. The Haskell reference off-chain library, any `toa.tx3` file, and any generated bindings are **non-normative reference artifacts**.

A conflict between a non-normative reference artifact and any normative component is resolved in favour of the normative component. A conflict among normative components is a specification erratum and MUST be corrected.

#### What lives where

The CIP folder contains only:

- this README;
- the parameter-encoding CDDL (inline in *Canonical Parameter Encoding*).

Every other normative artifact — the Plinth source, the compiled un-applied Plutus V3 validator artifact, the template hash, the pinned toolchain version(s), and the normative test vectors — is **published in an external repository** ([en7angled/toa](https://github.com/en7angled/toa)) and pinned from this CIP by **immutable git tag**. Binary artifacts whose byte representation determines on-chain behaviour (the compiled UPLC, and the test-vector JSON file) are additionally identified by **blake2b-256 content hash**, so any implementer can verify byte-for-byte that they hold the exact bytes the standard refers to. Text artifacts auditable through the git tag (the Plinth source, the toolchain freeze) are pinned by tag and path only, because their bytes are not directly hashed into ledger state. **The validator artifact specifically** (compiled, unapplied UPLC) is identifiable by an immutable content hash regardless of where it is stored, because every derived TOA address depends on it byte-for-byte; see *Mandatory Normative Artifacts*.

Non-normative artifacts — transaction-shape files, SDKs, generated bindings, demo frontends, and full reference implementations — also live in external repositories linked from this CIP, not inside the CIP folder. This includes any `toa.tx3` reference file, the Haskell + Atlas reference library, the HTTP API exposing TOA operations, the demo frontend, and any supplementary language bindings.

#### Reference validator (Plinth)

The canonical validator is written in **Plinth** (Haskell compiled to Plutus Core) and published at [`Onchain/Validators/ToaV1Validator.hs`](https://github.com/en7angled/toa/blob/0.1.1/src/lib/onchain-lib/Onchain/Validators/ToaV1Validator.hs) in the reference repository (see *Mandatory Normative Artifacts* for the compiled artifact, template hash, and pinned toolchain). Anyone can apply the canonical `TOAParamsV1` PlutusData value for a given `(toa_version, policy_id, asset_name)` and verify the resulting per-NFT script hash matches the address-derivation algorithm.

#### Address derivation helper

Specified normatively in *Address Derivation* above. A reference implementation in Haskell accompanies the CIP and is packaged alongside the off-chain library. The helper is intentionally *outside* Tx3 because Tx3 currently lacks a primitive for parameterised-script-address derivation; if and when that primitive lands upstream, a future revision of the CIP can fold it back in. Supplementary TypeScript and Rust ports of the helper are encouraged for ecosystem reach but are non-normative.

#### Reference off-chain library — external repository

A non-normative Haskell reference implementation is published at [en7angled/toa](https://github.com/en7angled/toa) (tag [`0.1.1`](https://github.com/en7angled/toa/releases/tag/0.1.1)), comprising:

- `onchain-lib` — the canonical Plinth validator (`Onchain.Validators.ToaV1Validator`) and `TOAParamsV1` parameter type;
- `offchain-lib` — Atlas-based transaction building, queries, CIP-14 fingerprinting, RFC-8949 canonical CBOR encoding of `TOAParamsV1`, and address derivation;
- `webapi-lib` + `interaction-api` — a Servant HTTP service exposing `/toa/derive`, `/toa/utxos`, `/toa/spend`, and basic transaction submission, with a Swagger UI;
- `toa-gen-vectors` — the executable that deterministically emits both `test-vectors/toa-v1.json` and `validators/ToaV1.uplc` from a single in-process generation step (no node interaction);
- `toa-bench` — a synthetic-context micro-benchmark for the validator with baseline-diff support for regression checks on execution units and script size.

The off-chain library, HTTP API, generator, and benchmark are non-normative. Conformance is determined by the validator artifact and the normative test vectors, per *Reference Artifacts — Normative components*.

#### Generated bindings (supplementary) — external

Supplementary language bindings MAY be generated from the externally-published `toa.tx3` reference file or produced on demand; all such bindings are non-normative.

#### Demo frontend — external

A non-normative reference frontend exercising address derivation, deposit, spend, and inspection is hosted at [toa.e7d.tech](https://toa.e7d.tech). The frontend consumes the HTTP API exposed by `interaction-api` in the reference repository and is provided for illustrative purposes only — conformance is determined by the validator artifact and the normative test vectors, not by the frontend.

### Test Vector Format

The normative test-vector file is [`test-vectors/toa-v1.json`](https://github.com/en7angled/toa/blob/0.1.1/test-vectors/toa-v1.json) — published at `en7angled/toa@0.1.1`, blake2b-256 = `f835348a178c5da4632d17c79321a7b6fc9274e8602b51bd71def22108c3a515`. The file is regenerated deterministically from the same Plinth source as the validator artifact, by the [`toa-gen-vectors`](https://github.com/en7angled/toa/blob/0.1.1/src/exe/toa-gen-vectors/Main.hs) executable.

Test vectors are split into two categories with **distinct conformance rules**:

- **(a) Address-derivation vectors.** Implementations MUST reproduce the `expected_script_hash`, `expected_address_mainnet`, and `expected_address_testnet` fields **byte-for-byte** for the corresponding `(toa_version, policy_id, asset_name)`. Six such vectors are currently published (see *Coverage* below).
- **(b) Validator scenarios.** Each scenario specifies the situation (inputs, outputs, mint, datums, redeemers) and the expected pass/fail result. Implementations need not produce byte-identical transaction bodies unless a scenario explicitly includes canonical transaction CBOR — different transaction builders may legitimately differ on input ordering, fee balancing, change outputs, collateral selection, and reference-script handling. Validator scenarios are not yet published in `toa-v1.json`; they are tracked as outstanding work in *Path to Active — Acceptance Criteria*.

Conformance for category (b) is **pass/fail correctness only**. Execution-unit usage and transaction-size budgets are deliberately not part of the standard: the validator's correctness is independent of the Plutus cost model, and pinning a cost model would impose ongoing erratum maintenance every time governance amends it. The reference repository's [`toa-bench`](https://github.com/en7angled/toa/blob/0.1.1/src/exe/toa-bench/Main.hs) tool tracks ExUnits and script-size as a non-normative regression baseline; it is informational and has no bearing on conformance.

Field-level schema documentation — the JSON envelope shape, top-level field semantics, and per-vector field semantics — is published alongside the vectors at [`test-vectors/README.md`](https://github.com/en7angled/toa/blob/0.1.1/test-vectors/README.md), identified by blake2b-256 content hash `1f321ce00df00d339f5acb4083063050cf9001a09b5cdec6bd3ce3b5ee3284af`.

Coverage MUST include at minimum:

- ASCII asset name — **published** (`ascii`);
- empty asset name — **published** (`empty`);
- maximum-length (32-byte) asset name — **published** (`max32`);
- [CIP-0067](https://cips.cardano.org/cip/CIP-0067) / [CIP-0068](https://cips.cardano.org/cip/CIP-0068) label 100 asset name (reference NFT) — **published** (`cip67-100`);
- CIP-0067 / CIP-0068 label 222 asset name (user NFT) — **published** (`cip67-222`);
- `toa_version` isolation — at least one vector with `toa_version` ≠ 1 that produces a distinct script hash and addresses for the same `(policy_id, asset_name)` as a v1 vector, confirming version-bump address-divergence — **published** (`ascii-v2`);
- UTF-8 / non-ASCII Unicode asset name — outstanding;
- **self-deposit spend case** — the controlling NFT is at its own TOA and is spent permissionlessly — outstanding;
- **reference-input attack case** — the controlling NFT appears only in a reference input; regular spent inputs contain zero units; expected result: **fail** (the reference input does not satisfy `sumSpentInputs(ac) == 1`) — outstanding;
- **datum-classification coverage — all four must be spendable:** (i) **Unit Datum**, (ii) **Inline Datum** (non-unit), (iii) **Datum Hash**, (iv) **No Datum** — outstanding;
- **permissive-policy warning fixture** — a vector documenting (as metadata, not validator proof) that the controlling minting policy permits further mints, so wallets and indexers can verify their warning UX against a concrete example — outstanding.

## Rationale: How does this CIP achieve its goals?

### Design Decisions

- **Why a parameterised validator (vs. a datum-carried params + a single shared validator)?** Parameters baked into the script hash mean the address itself uniquely encodes the controlling NFT. Anyone can pay in to the correct, predictable address without trusting a datum.
- **Why a hash-derived address (vs. a CIP-0068-style reference-NFT pointer)?** Determinism: any wallet can compute the address from `(policy_id, asset_name)` alone, with no indexer lookups, no chain queries, no metadata fetches.
- **Why an off-chain CIP (vs. a ledger change introducing a new address kind)?** TOA works today on Plutus V3 with zero protocol modifications. A future ledger-level token-bound account remains an option for a separate CIP; TOA is the standard that ships now.
- **Why Plutus V3 specifically?** V3 is the Conway-era Plutus ledger language version and supports the [CIP-0069](https://cips.cardano.org/cip/CIP-0069) unified script interface, where spending validators receive only the redeemer and `ScriptInfo` rather than a separate datum argument. This lets TOA v1 avoid making datum presence part of the authorisation rule (see *Datum and Redeemer Schema*) and keeps the validator's predicate purely about input and output value and minting. V3 is also the intended target for new Conway-era Plutus standards. Any future Plutus ledger language version (V4+) would require a new `toa_version`, because the language tag is part of the script hash and therefore part of every derived TOA address.
- **Why not normative transaction-shape DSL?** Conformance is fully defined by *Validator Rules* and *Test Vector Format*. Constraining the *shape* of valid transactions beyond what the validator enforces would force every implementation through a specific DSL or codegen toolchain without strengthening the on-chain guarantee. A non-normative Tx3 reference file may be published as an aid to implementers, but no implementation is required to consume it.
- **Why no stake credential in v1?** Any optional stake credential is an interop fork — two wallets disagreeing on the canonical choice produce different addresses for the same NFT. v1 picks the safest single value (none); delegated TOAs are deferred to a future CIP.
- **Why transaction-local NFT uniqueness (`sumSpentInputs(ac) == 1`, `sumOutputs(ac) == 1`) rather than "validator enforces supply = 1"?** The validator cannot prove historical total supply on-chain — it sees only one transaction at a time. Transaction-local uniqueness over *spent* inputs is the strongest invariant the validator can actually enforce: it rules out in-transaction multi-copy edge cases and reference-input attacks (where the NFT is observed but not consumed), while leaving the responsibility of choosing a sound minting policy to the NFT issuer (and to wallet warnings, per *Wallet Behaviour*).
- **Why total quantity rather than "some input contains the NFT"?** Checking `sumSpentInputs(ac) == 1` and `sumOutputs(ac) == 1` rejects three failure modes that "some input contains the NFT" would miss: (1) zero NFT inputs, (2) multi-copy NFT inputs (only possible if the upstream minting policy is permissive), and (3) an NFT visible only as a *reference* input. The third case is particularly important: a reference input lets a transaction observe a UTxO without consuming it, and treating reference-input visibility as authorisation would let any party who finds a UTxO containing the controlling NFT (anywhere on the ledger) drain the TOA. The validator MUST count only spent inputs.
- **Why permit self-deposit rather than forbid it?** TOA control is defined by NFT presence in transaction inputs, *not* by external ownership. Disallowing self-deposit is technically possible — a Plutus V3 spending validator can recover its own input via `ScriptInfo`'s `SpendingScript` purpose and reject transactions where the controlling NFT input originates at the same TOA script credential — but TOA v1 deliberately does not add such an input-origin restriction. The chosen semantics define control solely by NFT presence in transaction inputs, which keeps the design eUTxO-natural and lets the NFT flow through wallets, escrow scripts, lending scripts, marketplace scripts, and, intentionally, its own TOA. The permissionless-spend consequence of self-deposit is made explicit in *Definitions* and *Security Considerations*, and wallets MUST warn before performing self-deposit.

### Related Work and Prior Art

External prior art is discussed in *Motivation* — chiefly [ERC-6551](https://eips.ethereum.org/EIPS/eip-6551) (Ethereum Token-Bound Accounts), Solana Associated Token Accounts, and the object-ownership models of Sui and Aptos. TOA's contribution is to bring the *deterministic, NFT-derived address* idea to Cardano in a form that requires no ledger changes.

**Within the Cardano CIPs corpus:**

- [CIP-0113](https://cips.cardano.org/cip/CIP-0113) (Programmable Token-Like Assets) — incorporating the now-`Inactive` [CIP-0143](https://cips.cardano.org/cip/CIP-0143) and addressing [CPS-0003](https://cips.cardano.org/cps/CPS-0003) (Smart Tokens) — is architecturally related to TOA but uses a different deterministic-derivation mechanism. CIP-0113 keeps the **payment credential** fixed (a shared `programmableLogicBase` script used by programmable-token addresses) and varies the **stake credential** per holder/user credential, producing "smart wallet" addresses under that shared script. TOA varies the **payment credential** instead — by parameter application of `(toa_version, policy_id, asset_name)` into the validator — and carries no **stake credential** in v1, producing one address per controlling asset class under a per-asset script hash. The two are complementary rather than overlapping: CIP-0113 standardises programmable transfer behaviour for token-like Cardano native assets via per-user smart-wallet addresses; TOA standardises NFT-controlled vault addresses via per-asset scripts.
- [CIP-0160](https://cips.cardano.org/cip/CIP-0160) (Receiving Script Purpose and Addresses) proposes a ledger-level mechanism — a new `Receiving` script purpose plus a `ProtectedAddress` concept — that would let scripts validate UTxO creation at their address. TOA v1 does not depend on CIP-0160 and remains compatible with the current unprotected script-address model; if CIP-0160 is adopted, a future TOA version may use it to restrict or validate deposits into TOAs (see *Open Questions and Limitations*).

**CIPs TOA builds on directly:** [CIP-0019](https://cips.cardano.org/cip/CIP-0019) (Cardano Addresses) for the enterprise script address format; [CIP-0014](https://cips.cardano.org/cip/CIP-0014) (User-Facing Asset Fingerprint) for the `asset1...` identifier displayed alongside TOA addresses; CIP-0069 (Plutus Script Type Uniformization) for the V3 spending validator interface; and CIP-0067 / [CIP-0068](https://cips.cardano.org/cip/CIP-0068) (asset name labels and datum-based metadata) for asset-name handling in test vectors. None of these require modification.

### Backward Compatibility

TOA is purely additive — no existing standard or implementation changes behaviour because of TOA.

- **[CIP-0014](https://cips.cardano.org/cip/CIP-0014) (user-facing asset fingerprint):** TOA derivation operates on raw `(policy_id, asset_name)` bytes; the CIP-0014 fingerprint (`asset1...`) is a parallel user-facing identifier and is independent of address derivation. Wallets and explorers SHOULD display the CIP-0014 fingerprint of the controlling NFT alongside the TOA address so users can recognise which asset controls a given TOA. Tooling MAY accept a CIP-0014 fingerprint as a lookup key, resolving it to `(policy_id, asset_name)` via an indexer before derivation. No conflict.
- **[CIP-0025](https://cips.cardano.org/cip/CIP-0025) (NFT metadata):** TOA addresses are derived from `(policy_id, asset_name)` regardless of which metadata standard the asset uses. No conflict.
- **[CIP-0067](https://cips.cardano.org/cip/CIP-0067) (asset name labels):** TOA derivation treats `asset_name` as raw bytes. CIP-0067 labels are not interpreted by the TOA validator; they are simply part of the asset name bytes, so different labelled asset names produce different TOAs. No conflict.
- **[CIP-0068](https://cips.cardano.org/cip/CIP-0068) (datum-based metadata):** TOA derivation is independent of datum content and equally agnostic to CIP-0068 label semantics. A CIP-0068 reference NFT (label 100) and its corresponding user NFT (label 222) have distinct asset names and therefore each have their own TOA. No conflict.
- **Existing token-gating implementations:** TOA does not invalidate any current pattern. It offers a standard target that new implementations should converge on, with no requirement to migrate existing dApps.

#### L2 Interoperability

Because TOA derivation depends only on the Plutus V3 validator and `(toa_version, policy_id, asset_name)`, the same applied script hash and payment credential can be derived in any Plutus-compatible environment that uses Cardano-ledger address semantics. Cross-ledger semantics — bridge transit, head admission, rollup confirmation windows, and settlement guarantees — are out of scope for TOA v1 and are the responsibility of the specific L2 system.

## Security Considerations

These risks are intrinsic to the design and must be addressed by implementers and surfaced to users.

### Permanent loss and policy-permissiveness risks

A TOA is recoverable only by a party that can construct a transaction consuming the controlling NFT as an input. If the controlling NFT is **burned** (only possible if the minting policy permits burns) or becomes locked in a script from which no valid transaction can consume it, **all assets at the TOA become permanently inaccessible** — there is no recovery path at the ledger level. The mirror failure mode is *Self-deposit* (below), in which the TOA becomes not inaccessible but *permissionlessly spendable*.

If the controlling NFT's minting policy is **not `ProvenClosed`** (i.e. is classified `KnownOpen` or `Unknown` per *Policy Classification*), the policy may permit duplication or burning of the controlling asset by a party with mint authority — and TOA v1 cannot prove on-chain that this isn't the case. The validator's `mint == 0` rule closes only the **single-transaction** variant of any duplication-then-drain attack: an attacker cannot atomically mint-and-drain in one transaction. It does **not** close the two-transaction variant (mint in tx A, then spend the TOA in tx B). The validator's contribution is removing the atomic coupling and making any duplication observable on-chain between the two transactions; the residual risk is mitigated at the wallet/UX layer via the policy-class warning MUSTs in *Wallet Behaviour*, which treat `KnownOpen` and `Unknown` policies as unsafe unless independently verified.

Wallets MUST warn for `KnownOpen` and `Unknown` controlling-asset policies (see *Wallet Behaviour — Assign a policy classification, default `Unknown`*), and SHOULD additionally warn before any deposit to a TOA whose controlling NFT is held in cold storage or otherwise at elevated key-loss risk.

### Self-deposit of the controlling NFT

If the controlling NFT is locked inside its own TOA, any transaction author who can provide the required ledger witnesses — including any required datum preimage for a `Datum Hash` UTxO — may spend that TOA UTxO by consuming it and carrying the NFT through. This is what we mean by "permissionlessly spendable."

For `Unit Datum`, `Inline Datum`, and `No Datum` outputs no off-chain datum preimage is needed; the TOA UTxO containing the NFT is both the value being spent and the proof of authorisation. For `Datum Hash` outputs the datum preimage is still required by the ledger even though the TOA validator itself does not inspect it.

A self-deposited TOA is therefore **publicly controllable**: subject to the above witness requirement, any transaction author can move the TOA contents anywhere while carrying the controlling NFT forward to any address (including back into the same TOA, perpetuating the public-control state). The TOA validator does not require a specific signer, wallet identity, or other off-chain credential — it authorises the spend purely from the on-chain state.

This is **not** a validator bug. It is an intentional consequence of defining control by NFT presence in transaction inputs rather than by signatures or by an external ownership address. Disallowing self-deposit would require enforcing an "input must not come from this script address" predicate, which breaks the eUTxO-natural design and the symmetry that lets the NFT itself flow through lending, escrow, and marketplace scripts.

Wallets MUST warn users before sending the controlling NFT to its own TOA, and MUST describe the action as making the TOA publicly spendable rather than merely as transferring the NFT to another address (see *Wallet Behaviour — Warn that TOA control follows the ability to consume the controlling NFT*).

### Authorisation scope: one NFT input authorises any number of TOA UTxOs

A single valid controlling-NFT input authorises the transaction to spend **any number** of UTxOs at that NFT's TOA, subject only to transaction-size and execution-unit limits. This is intentional: authorisation is per transaction, not per TOA UTxO. It enables efficient batched cleanup of spam deposits and atomic multi-output spends from a TOA, and it is what allows the carry-through rule (`sumOutputs(ac) == 1`) to remain coherent in spite of multiple TOA inputs.

Test vectors include a positive case demonstrating this (one NFT input → many TOA UTxOs in / single carry-through out) and negative cases that reject `sumSpentInputs(ac) ≠ 1`, `sumOutputs(ac) ≠ 1`, or `mint(ac) ≠ 0`, including a reference-input attack vector where the NFT appears only as a reference input (see *Path to Active — Acceptance Criteria*).

### Value-cost and dust risks

TOA addresses are open vaults; the validator cannot disallow foreign tokens without destroying the use case. Two consequences:

- TOA-spending transactions traverse the full `Value` of every TOA UTxO they consume, so cost grows with the size of the token map. Worst-case behaviour must be covered by test vectors and by sensible transaction-builder defaults (UTxO selection, output coalescing).
- Spam deposits (covered separately in *Spam and DoS via deposits*) compound this risk by inflating UTxO counts. Wallets SHOULD coalesce conservatively when constructing TOA spends and SHOULD allow the user to select which TOA UTxOs to include rather than consuming the full set.

### Validator bugs are unrecoverable

A bug in the canonical `TOA v1` validator could allow assets to be drained from every TOA derived from it. Because the validator hash is baked into every TOA address, no fix can be retrofitted to existing addresses — a corrected validator is a new `toa_version` with new addresses, and funds on the old version remain at the old version. The canonical validator therefore requires extensive independent audit before publication, and any future revision MUST be released as a new `toa_version` per the *Versioning* section.

### Spam and DoS via deposits

Any party can send UTxOs to a TOA, and the standard does not (and cannot) prevent this at the validator level — this is fundamental to the deterministic-address model. High UTxO counts inflate the cost of TOA-spending transactions and can in extreme cases push them over the transaction-size or execution-unit limits. [CIP-0160](https://cips.cardano.org/cip/CIP-0160) is the proposed ledger-level mitigation (see *Open Questions and Limitations*). Wallets MAY filter spam in UI and SHOULD coalesce UTxOs sensibly when constructing TOA spends.

### Temporary control during lending, escrow, or rental

Any party or script that can cause the controlling NFT to be consumed as a transaction input can control the TOA for that transaction. This includes borrowers, escrow contracts, marketplaces, lending protocols, and any other script that temporarily holds or controls the NFT.

This is intentional (see *Open Questions and Limitations*) and is what makes TOA composable with the rest of the eUTxO ecosystem, but it does mean that any borrower can drain a TOA before returning the NFT. The wallet-side MUST for surfacing this risk is stated normatively in *Wallet Behaviour* and is the same obligation, not an additional one. Lending protocols built on top of TOA-controlling NFTs SHOULD treat the TOA balance as part of the economic exposure of lending the controlling NFT, and SHOULD ensure the TOA balance is part of the loan collateral terms.

### TOA is not an escrow

A TOA is controlled by whichever party can consume the controlling NFT as a transaction input. Assets sent to a TOA can be spent by that party at any time, without giving the depositor anything in return. The TOA validator enforces NFT carry-through; it does **not** enforce any payment-for-NFT, time-lock, or exchange semantics.

**Binding marketplace offers that escrow real value MUST use a separate offer validator** that enforces the exchange (e.g. "pay X ADA, receive the controlling NFT atomically"). A TOA MAY serve as a discovery channel for such offers — the offer validator's address can be referenced from data deposited at the TOA, or the offer UTxO can be created at the TOA with an inline datum describing the terms — but the TOA v1 validator alone does not enforce sale semantics.

Wallets and dApp authors MUST NOT present a TOA deposit as "escrowed" to the depositor unless an external offer validator with appropriate escrow semantics also locks the assets. Treating a TOA as escrow is the most likely user-level misuse of this standard.

### Front-running

In the **ordinary case** (controlling NFT outside the TOA, held by a wallet or specific script), spend transactions are NFT-gated at the input level: a mempool observer cannot front-run a TOA spend without also being able to consume the UTxO containing the controlling NFT. No additional mitigation is required beyond what the validator already enforces.

In the **self-deposit case** (controlling NFT inside its own TOA), spending is intentionally permissionless for any transaction author able to provide the required ledger witnesses. Mempool competition is expected and is not treated as front-running against an owner — it is a direct consequence of self-deposit semantics, surfaced to the user by the *Self-deposit warning* MUST in *Wallet Behaviour*.

## Open Questions and Limitations

The following known limitations are intentionally left unresolved in TOA v1. Each is listed with an explicit **Disposition** so reviewers don't have to guess what stance the CIP takes.

### 1. UTxO spam and junk deposits

Anyone can send UTxOs to an ordinary Cardano script address. TOA v1 deliberately uses ordinary enterprise script addresses, so it cannot prevent unsolicited deposits at the validator level — this is fundamental to the deterministic-address model.

**Disposition:** Out of scope for v1. Wallets and indexers MAY filter or hide spam UTxOs in UI. Transaction builders SHOULD allow users to select which TOA UTxOs to consume. [CIP-0160](https://cips.cardano.org/cip/CIP-0160) ("Receiving Script Purpose and Addresses") proposes a ledger-level mechanism — a new `Receiving` script purpose plus a `ProtectedAddress` concept — that would let scripts validate UTxO creation at their address. If CIP-0160 is adopted, a future TOA version may use it to restrict or validate deposits into TOAs. TOA v1 does not depend on CIP-0160 and remains compatible with the current unprotected script-address model.

### 2. Token lending and temporary delegation

If the NFT owner lends the NFT, the borrower temporarily controls the TOA.

**Disposition:** Intentional feature, not a bug. See *Security Considerations — Temporary control during lending, escrow, or rental*.

### 3. Multiple address variants

Changes to `stake_credential`, `toa_version`, or the validator template all produce different addresses.

**Disposition:** Resolved in v1 by pinning a single template, `toa_version = 1`, and no stake credential. Future variants (delegated TOAs, alternative templates) live in separate CIPs.

### 4. Multi-quantity asset classes

What if the controlling asset has total supply > 1?

**Disposition:** Out of scope for v1. The validator cannot prove historical total supply on-chain; instead it enforces transaction-local uniqueness (`sumSpentInputs(ac) == 1`, `sumOutputs(ac) == 1`, `mint == 0`). Asset classes with intended supply > 1 fall outside this CIP's scope. See *Validator Rules* and *Rationale — Design Decisions*.

### 5. Reference scripts

Could publishing the TOA validator as a reference script change the derived address?

**Disposition:** No — reference scripts do not change the derived TOA address. The address is determined by the hash of the **applied** validator script, not by which UTxO carries the reference script. Reference scripts are safe and encouraged to reduce transaction size.

However, because TOA uses a parameterised validator, a reference script must correspond to the **applied** script for the specific `(toa_version, policy_id, asset_name)` being spent. A reference script for the *unapplied* template is not sufficient to spend a concrete TOA — each TOA needs (or shares with peers) a reference UTxO carrying its own applied script bytes.

## Path to Active

### Acceptance Criteria

These are the concrete, testable conditions for the CIP to move from `Proposed` to `Active`.

- [x] *Mandatory Normative Artifacts* in the reference implementation at [en7angled/toa](https://github.com/en7angled/toa) (tag [`0.1.1`](https://github.com/en7angled/toa/releases/tag/0.1.1))
  - [x] Canonical Plinth source for the TOA v1 validator published (external, content-hash-referenced).
  - [x] Compiled, **unapplied** Plutus V3 validator artifact (binary UPLC bytes) published — 476 bytes, blake2b-256 = `7f78c5524a00852eb51ee760f86a3f0cce4535b446e0c03d6cdc35eb6de0092b`.
  - [x] Compiler/toolchain versions pinned — GHC 9.6 series, Plutus Core target version 1.1.0, plutus-tx / plutus-tx-plugin / plutus-ledger-api at Conway-era IOG CHaP pins frozen via `cabal.project.freeze`.
  - [x] Template hash documented, computed as `blake2b_224(0x03 || unapplied_script_bytes)` per *Mandatory Normative Artifacts* — `129181a58ca3716aada61244d3d4210bff5a7235f709189af2596dc0`.
  - [x] Address-derivation helper published (Haskell reference in `offchain-lib`; supplementary TypeScript/Rust ports encouraged but non-normative — outstanding).
  - [x] At least one non-normative reference off-chain implementation published, including address derivation, deposit, spend, and NFT carry-through (`offchain-lib`, exercised by the test suite via [CLB](https://github.com/mlabs-haskell/clb) scenarios).
  - [x] A testnet demonstration or reference workflow exercises address derivation, deposit, spend, and NFT carry-through end-to-end on a public testnet — [toa.e7d.tech](https://toa.e7d.tech) runs the reference frontend against the Cardano Preview testnet (and mainnet) and exercises all four operations.
- [ ] Normative test vectors published per *Test Vector Format* and verified against **at least two independent implementations**. Address-derivation vectors are published; validator-scenario vectors and second-implementation verification are outstanding.
- [ ] At least two independent integrations: e.g. one wallet displaying TOA addresses with proper labelling, and one explorer/indexer (Cexplorer, Pool.pm, Cardanoscan, or equivalent) labelling TOA addresses as such.

### Implementation Plan

The Implementation Plan describes the **ordered work** required to move TOA v1 from `Proposed` to `Active`. It is distinct from *Acceptance Criteria* (the conditions that must hold at the moment of activation) — this section is the sequence of steps that produce those conditions.

1. **Publish the canonical Plinth validator source** and the compiled, unapplied Plutus V3 artifact (binary UPLC bytes), with pinned toolchain versions and the documented template hash. Identify the validator artifact by its immutable content hash, published as an external immutable release per *Reference Artifacts — What lives where*. (Done — see *Mandatory Normative Artifacts* and *Acceptance Criteria*.)
2. **Publish the parameter-encoding CDDL** and confirm it round-trips through at least two independent CBOR libraries. (CDDL published inline in *Canonical Parameter Encoding*; multi-library round-trip verification outstanding.)
3. **Publish the address-derivation test vectors** (category (a) in *Test Vector Format*) covering ASCII / non-ASCII Unicode / empty / max-length / CIP-0067 label 100 / CIP-0067 label 222 asset names. (Done for ASCII / empty / max-length / label-100 / label-222 plus a `toa_version`-isolation vector; non-ASCII Unicode outstanding — see *Test Vector Format — Coverage*.)
4. **Publish the validator-scenario test vectors** (category (b)) covering all positive, negative, authorisation-scope, value-shape stress, spend, and reference-input cases enumerated in *Test Vector Format — Coverage*. Each scenario asserts pass/fail correctness only; ExUnit and tx-size measurements are tracked non-normatively in `toa-bench`.
5. **Publish the address-derivation helper** (Haskell reference; supplementary TypeScript/Rust ports as non-normative). (Done — `offchain-lib` in the reference repository; supplementary ports outstanding.)
6. **Publish at least one non-normative reference off-chain implementation**, including address derivation, deposit, spend, and NFT carry-through. (Done — `offchain-lib` + `interaction-api` + [toa.e7d.tech](https://toa.e7d.tech).)
7. **Verify against independent implementation #1** — an external party (wallet team, library author, or auditor) reproduces every test vector byte-for-byte for address derivation and pass/fail-correct for validator scenarios.
8. **Verify against independent implementation #2** — a second independent party does the same against a different stack (e.g. lucid-evolution, MeshJS, cardano-transaction-lib, or PyCardano).
9. **Integrate explorer and wallet display** — at least one Cardano explorer (Cexplorer / Pool.pm / Cardanoscan / equivalent) and at least one mainstream wallet label TOA addresses as such and surface the policy classification (`ProvenClosed` / `KnownOpen` / `Unknown`) and self-deposit state.

Steps 1–6 are owned by the CIP authors. Steps 7–9 are owned by the ecosystem and are the primary gating condition for activation.

## Versioning

`toa_version` is a script parameter and therefore part of the hashed input. Concrete consequences:

- A TOA v1 address and a hypothetical TOA v2 address for the same `(policy_id, asset_name)` resolve to **different addresses**.
- Addresses **do not migrate** between versions. Funds on a v1 TOA stay on the v1 TOA.
- Wallets MUST surface the TOA version to the user before any deposit or spend.
- Each new version is a new validator and lives in its own CIP (or as a versioned addendum to this one).

## References

**Cardano CIPs referenced:**

- [CIP-0014](https://cips.cardano.org/cip/CIP-0014) — User-Facing Asset Fingerprint
- [CIP-0019](https://cips.cardano.org/cip/CIP-0019) — Cardano Addresses
- [CIP-0025](https://cips.cardano.org/cip/CIP-0025) — Media NFT Metadata Standard
- [CIP-0030](https://cips.cardano.org/cip/CIP-0030) — Cardano dApp-Wallet Web Bridge
- [CIP-0067](https://cips.cardano.org/cip/CIP-0067) — Asset Name Label Registry
- [CIP-0068](https://cips.cardano.org/cip/CIP-0068) — Datum Metadata Standard
- [CIP-0069](https://cips.cardano.org/cip/CIP-0069) — Plutus Script Type Uniformization
- [CIP-0113](https://cips.cardano.org/cip/CIP-0113) — Programmable Token-Like Assets (candidate; incorporates CIP-0143)
- [CIP-0143](https://cips.cardano.org/cip/CIP-0143) — Interoperable Programmable Tokens (Inactive; incorporated into candidate CIP-0113)
- [CIP-0160](https://cips.cardano.org/cip/CIP-0160) — Receiving Script Purpose and Addresses
- [CPS-0003](https://cips.cardano.org/cps/CPS-0003) — Smart Tokens

**External standards and tools:**

- [ERC-6551](https://eips.ethereum.org/EIPS/eip-6551) — Token-Bound Accounts (Ethereum)
- [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119) — Key words for use in RFCs to Indicate Requirement Levels
- [RFC 8174](https://www.rfc-editor.org/rfc/rfc8174) — Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words
- [RFC 8949](https://www.rfc-editor.org/rfc/rfc8949) — Concise Binary Object Representation (CBOR), §4.2.1 "Core Deterministic Encoding"
- [Atlas](https://atlas-app.io) — Haskell transaction-building framework used by the reference off-chain library

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
