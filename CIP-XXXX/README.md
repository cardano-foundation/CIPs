---
CIP: "?"
Title: Web-Wallet Bridge - Balance, sign and submit
Category: Wallets
Status: Proposed
Authors:
    - Mark van Zon <mark@dezons.com>
    - Marcel Baumberg <marcel.baumberg@tastenkunst.io>
Implementors:
    - Eternl <https://eternl.io/>
Discussions:
    - Original PR: https://github.com/cardano-foundation/CIPs/pull/?
    - CIP-0030 balanceTx (closed): https://github.com/cardano-foundation/CIPs/pull/170
Created: 2026-10-27
License: CC-BY-4.0
---

## Abstract

This CIP extends [CIP-30][] with a single method, `api.cipXXXX.balanceAndSignTx(tx)`. It is an upgrade of `signTx`: the dApp passes one CBOR string, and the wallet balances it when needed, signs it, and submits it when it is complete.

The method is designed for the Dijkstra ledger era, where a dApp can express its intent as one or more sub-transactions ([CIP-118][]) and leave fees, collateral, and funding of the enclosing top-level transaction to the wallet. Before Dijkstra, the method works on ordinary Conway transactions.

## Motivation: Why is this CIP necessary?

Today, a dApp must build a fully balanced transaction before calling `signTx`. To do that, it needs the user's UTxOs (`getUtxos`), its own coin selection, fee and collateral logic, and an up-to-date view of protocol parameters. Every dApp re-implements wallet logic, and the wallet, which knows the user's funds best, has no say in how its own inputs are spent.

Dijkstra's nested transactions change the picture. A dApp can describe what it wants as a sub-transaction: a self-contained, signable piece that carries no fee and no collateral. Someone still has to wrap it in a balanced top-level transaction. The natural party to do that is the user's wallet.

An earlier attempt to add `balanceTx` to CIP-30 ([PR #170][PR170]) was closed with the advice to make it a separate, optional extension. This CIP is that extension. It also folds signing and submission into one call, so `partialSign` and the separate `submitTx` round trip are no longer needed for this flow.

## Specification

### Extension

Wallets advertise support through CIP-30 `supportedExtensions` as `{ cip: XXXX }`. A dApp enables it via `cardano.{walletName}.enable({ extensions: [{ cip: XXXX }] })`. The method is exposed under the extension namespace:

```ts
api.cipXXXX.balanceAndSignTx(
  tx: cbor<transaction | sub_transaction | sub_transactions>
): Promise<BalanceSignResult>
```

There are no further parameters. In particular, there is no `partialSign` and no submit flag; see [User confirmation and submission](#user-confirmation-and-submission).

### Accepted input forms

`tx` is a single hex-encoded CBOR string. A conforming wallet MUST accept each of the following forms:

| Form | Meaning | Wallet action |
|------|---------|---------------|
| Complete top-level transaction | Balanced, all required witnesses present | Show it; skip signing; user confirms with Submit |
| Balanced top-level transaction, not fully witnessed | Ready except for signatures | Add own witnesses; submit if then complete |
| Incomplete top-level transaction, with or without sub-transactions (field 23) | Needs funding, fee, collateral | Balance around it, sign, submit if complete |
| One sub-transaction (`sub_transaction`) | dApp intent only | Build a top-level transaction around it, sign, submit if complete |
| Several sub-transactions (`sub_transactions`) | dApp intents only | Build a top-level transaction around them, sign, submit if complete |

How a wallet recognizes which form it received is an implementation detail.

> [!NOTE]
> Informative: in the Dijkstra CDDL a mempool transaction without the deprecated `is_valid` flag and a sub-transaction share the shape `[body, witness_set, auxiliary_data / nil]`. They differ in that a top-level body always has key 2 (fee) and a sub-transaction body never does. Because the fee field is mandatory, an incomplete top-level transaction carries a placeholder fee (for example, `0`) that the wallet replaces.

Sub-transaction forms are valid only once the Dijkstra era is active. Before that, the wallet accepts Conway transactions and applies the same rules without sub-transactions.

### Wallet behaviour

#### Balancing: preserve and add around

When the wallet balances a top-level transaction, it MUST preserve everything the dApp supplied: inputs, outputs and their order, mint, certificates, withdrawals, votes, proposals, reference inputs, guards, validity interval, metadata, datums, scripts and redeemers. The wallet MAY only add:

- inputs;
- outputs of its choosing (for example, change);
- collateral inputs, collateral return and total collateral;
- the fee and the validity interval, where the dApp left them unset.

The wallet decides the change address, fee policy, collateral, and validity interval. The request carries no options to steer them.

If the incomplete top-level transaction contains redeemers, the wallet MUST re-index spend redeemers to match the new sorted input set, re-evaluate execution units, and recompute `script_data_hash` and the fee. Re-indexing is the only change the wallet may make to dApp-supplied witness data; redeemer data is never changed.

#### Sub-transactions

- The wallet MUST NOT modify a sub-transaction body. It MAY add its own witnesses to a sub-transaction's witness set (for example when the sub-transaction spends the user's UTxOs).
- The wallet provides the fee and the collateral for the whole batch, in accordance with the Dijkstra ledger rules.
- The wallet MUST NOT select, for the top-level transaction, any UTxO that a sub-transaction spends. If two supplied sub-transactions spend the same UTxO, the wallet MUST reject the request with `APIError.InvalidRequest`.

> [!NOTE]
> Informative: per the Dijkstra ledger rules, sub-transactions are applied in list order before the top-level transaction, and their scripts see only their own sub-transaction. A sub-transaction is therefore unaffected by what the wallet adds to the top-level transaction, and its witnesses stay valid.

#### Existing witnesses

A vkey witness signs the transaction body, so balancing invalidates any witness already present on the top-level transaction. If the top-level transaction needs balancing and carries a vkey witness from a key the wallet does not control, the wallet MUST reject with `TxSignError.BodyLocked`. It MUST NOT silently drop such witnesses. A balanced top-level transaction may carry foreign witnesses; the wallet only adds its own.

Parties that need to sign before the wallet SHOULD do so on a sub-transaction, or sign after the wallet has balanced the transaction.

#### Guards

Dijkstra replaces `required_signers` with `guards` (field 14), which may be key hashes or credentials. The wallet treats guards on the top-level transaction and on sub-transactions as signing requirements. If the wallet cannot satisfy a guard, it leaves the transaction incomplete.

#### Evaluation

Supporting this CIP requires the ability to evaluate the whole batch (top-level and all sub-transactions), either locally or through the wallet's backend. The wallet MUST evaluate before signing whenever the batch contains scripts, and MUST NOT sign or submit if evaluation fails (`TxSignError.EvaluationFailed`). This protects the user's collateral, which backs every script in the batch. Wallets built on hardware devices evaluate in their host software or backend.

#### User confirmation and submission

- The wallet presents every call to the user. Declining yields `TxSignError.UserDeclined`.
- If the input is already complete, the signing step is skipped, and the user confirms with a Submit button. This differs from CIP-30 `submitTx`, which submits without user interaction.
- The wallet decides whether to submit. If, after signing, the transaction is complete and passes evaluation, the wallet MAY submit it. If it is not complete (missing witnesses or guards of other parties), the wallet returns it unsubmitted.
- A dApp that must hold back a complete transaction (to submit it later or through its own channel) uses CIP-30 `signTx` instead.

### Result

If a transaction was produced, the call resolves with:

```ts
type BalanceSignResult = {
  cbor:         cbor<transaction>, // full transaction as returned by the wallet
  txHash:       hash32,            // top-level transaction id
  complete:     boolean,           // all required witnesses and guards present
  submitted:    boolean,
  submitError?: TxSendError        // only when complete, submission attempted and failed
}
```

| `complete` | `submitted` | `submitError` | Meaning |
|------------|-------------|---------------|---------|
| false | false | – | Wallet signed what it could; other parties still need to sign. |
| true | true | – | Submitted. |
| true | false | – | Complete; the wallet chose not to submit. |
| true | false | set | Submission failed; the signed transaction is still usable (retry or submit elsewhere). |

`submitError` uses the CIP-30 `TxSendError` type (`Refused`, `Failure`).

### Errors

If no usable transaction was produced, the call rejects. Access and input problems use CIP-30 `APIError` (`InvalidRequest`, `Refused`, `AccountChange`, `InternalError`). Signing problems use CIP-30 `TxSignError = { code, info }`, extended with three codes. `info` carries a human-readable explanation.

```ts
TxSignErrorCode {
  ProofGeneration  = 1,  // CIP-30
  UserDeclined     = 2,  // CIP-30
  BodyLocked       = 3,  // needs balancing, but carries foreign vkey witnesses
  CannotBalance    = 4,  // insufficient funds, min-UTxO, size limit or device limitations
  EvaluationFailed = 5   // a script in the batch fails phase-2 evaluation
}
```

Codes 3–5 are returned only by `balanceAndSignTx`. CIP-30 `signTx` never returns them, so existing behavior is unchanged.

### Interaction with other CIPs

| CIP | Relationship |
|-----|--------------|
| [CIP-30][] | Extended. `signTx` and `submitTx` remain unchanged and available. |
| [CIP-21][] | Hardware-wallet restrictions are the wallet's concern. A wallet MAY reject with `CannotBalance` or `ProofGeneration` when its device cannot handle a transaction. |
| [CIP-95][] | Governance certificates, votes, and proposals in the input are preserved like any other dApp-supplied field. |
| [CIP-103][] | Unaffected. This CIP handles one transaction per call; bulk signing stays with CIP-103. |
| [CIP-106][] / [CIP-141][] | Multisig and script wallets sign their own part and return `complete: false`. |
| [CIP-118][] | Provides the sub-transaction model this CIP builds on. |

### Versioning

This extension is identified by its CIP number in `supportedExtensions` and carries no separate version field. Backwards-compatible clarifications may be made to this document. Any change to the method signature, the accepted input forms, the result shape or the error codes requires a new CIP that supersedes this one and is advertised under its own extension number.

## Rationale: How does this CIP achieve its goals?

### Why one method that signs, balances, and submits?

The goal is to make `balanceAndSignTx` a superset of `signTx`. A dApp that sends a balanced transaction gets today's behavior; one that sends an intent gets a funded, signed, and submitted transaction. One call, one user prompt.

### Why does the wallet own the top-level transaction?

Funding, fees, collateral, change, and validity are about the user's UTxO set and the wallet's policy. Keeping them in the wallet removes duplicated coin-selection logic from dApps and lets the wallet append outputs of its choosing. The dApp's business logic lives in sub-transactions or in the fields it supplies, which the wallet preserves.

### Why are sub-transactions never modified?

A sub-transaction has its own body hash, its witnesses sign only that body, and its scripts see only that sub-transaction. As long as the wallet does not touch it, its witnesses stay valid, and its scripts behave exactly as the dApp evaluated them. Co-signers can therefore sign before the wallet sees the transaction.

An alternative where the wallet balances anyway, strips invalidated witnesses and reports which keys must re-sign was rejected: a dApp could forward or submit an incomplete transaction without noticing.

### Why has `partialSign` been dropped?

Whether a transaction is complete is something the wallet can determine itself. Whether to submit is decided by the wallet: the typical reasons not to submit (a co-signer still has to sign, or an intent will be wrapped by someone else) make the transaction incomplete by construction. The function reports `complete` and `submitted`, so the dApp always knows what happened. A dApp-supplied submit flag was considered and rejected in favour of this simpler model.

### Why no balancing options?

Change address, maximum fee, and collateral were considered and rejected as dApp parameters: they are wallet policy. dApp-supplied collateral is not even possible, as any signature on it would be invalidated by balancing.

### Why a single transaction per call?

Supporting an ordered list (superseding CIP-103) has been considered. Dijkstra does not allow chaining inside one batch: all inputs of a batch must exist before it is applied. Chaining across batches is possible on sub-transaction outputs, which are keyed by the sub-transaction's own ID. But a list exposes users to partial execution: an earlier transaction lands, a later one fails, and promised results never arrive. A single Dijkstra batch is all-or-nothing, which is the safer unit for one user approval.

### Why no normative verification procedure for dApps?

A hash comparison only works for fully built transactions, so a mandated check would cover only part of the scope. The CIP states the wallet's obligations; dApps may compare the returned transaction or sub-transaction IDs if they wish.

### Why extend `TxSignError` instead of a new error type?

dApps already handle `TxSignError` from `signTx`. New numeric codes let them react programmatically, while `info` carries the human-readable message.

### Backward compatibility

The extension is opt-in through the CIP-30 extension mechanism. Existing CIP-30 methods, their parameters and their error codes are unchanged. dApps that do not enable the extension are unaffected.

## Path to Active

### Acceptance Criteria

- [ ] At least two wallets implement the extension, including the sub-transaction input forms on a Dijkstra-era testnet.
- [ ] At least one dApp uses the extension in production with more than one of those wallets without wallet-specific code.
- [ ] A test suite covering each input form, `BodyLocked`, `CannotBalance`, `EvaluationFailed`, and the submit-only flow is published.

### Implementation Plan

- [ ] Circulate this proposal among wallet teams and collect feedback.
- [ ] Reference implementation in one wallet on a Dijkstra testnet.

## References

- [CIP-30][] – Cardano dApp-Wallet Web Bridge
- [CIP-103][] – Web-Wallet Bridge, bulk transaction signing
- [CIP-118][] – Nested Transactions
- [PR #170][PR170] – CIP-0030: balanceTx (closed)
- Dijkstra CDDL and ledger rules: [IntersectMBO/cardano-ledger, `eras/dijkstra`](https://github.com/IntersectMBO/cardano-ledger/tree/master/eras/dijkstra)

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).

AI Assistance (Claude) was used for structuring and grammar checking of the text.

[CIP-21]: https://github.com/cardano-foundation/CIPs/tree/master/CIP-0021
[CIP-30]: https://github.com/cardano-foundation/CIPs/tree/master/CIP-0030
[CIP-95]: https://github.com/cardano-foundation/CIPs/tree/master/CIP-0095
[CIP-103]: https://github.com/cardano-foundation/CIPs/tree/master/CIP-0103
[CIP-106]: https://github.com/cardano-foundation/CIPs/tree/master/CIP-0106
[CIP-118]: https://github.com/cardano-foundation/CIPs/tree/master/CIP-0118
[CIP-141]: https://github.com/cardano-foundation/CIPs/tree/master/CIP-0141
[PR170]: https://github.com/cardano-foundation/CIPs/pull/170
