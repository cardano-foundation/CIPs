---
CIP: 209
Title: Web-Wallet Bridge - Dijkstra era
Category: Wallets
Status: Proposed
Authors:
    - Mark van Zon <mark@dezons.com>
    - Marcel Baumberg <marcel.baumberg@tastenkunst.io>
Implementors:
    - Eternl <https://eternl.io/>
Discussions:
    - Original PR: https://github.com/cardano-foundation/CIPs/pull/1319
    - CIP-0030 balanceTx (closed): https://github.com/cardano-foundation/CIPs/pull/170
Created: 2026-10-27
License: CC-BY-4.0
---

## Abstract

This CIP extends [CIP-30][] for the Dijkstra ledger era, where a transaction can carry sub-transactions ([CIP-118][]) and accounts can hold deposited funds ([CIP-159][]). It adds three methods and amends one:

- `api.cip209.balanceAndSignTx(tx)`, an upgrade of `signTx`: the dApp passes one CBOR string, and the wallet balances it when needed, signs it, and submits it when it is complete. A dApp can express its intent as one or more sub-transactions and leave fees, collateral, and funding of the enclosing top-level transaction to the wallet.
- `api.cip209.signSubTxs(subTxs)`: the wallet signs sub-transactions as a participant, for another party to wrap and submit.
- `api.cip209.getBalances()`: the wallet's holdings in one call: its UTxOs, in the same format as `getUtxos`, and the balance of each account, which Dijkstra accounts ([CIP-159][]) can now receive directly.
- `api.signTx`: defined for Dijkstra transactions (guards, sub-transactions) when this extension is enabled, following the [CIP-95][] precedent.

All three methods work in any era: before Dijkstra, `balanceAndSignTx` and `signSubTxs` handle ordinary Conway transactions, so dApps can adopt them early.

## Motivation: Why is this CIP necessary?

Today, a dApp must build a fully balanced transaction before calling `signTx`. To do that, it needs the user's UTxOs (`getUtxos`), its own coin selection, fee and collateral logic, and an up-to-date view of protocol parameters. Every dApp re-implements wallet logic, and the wallet, which knows the user's funds best, has no say in how its own inputs are spent.

Dijkstra's nested transactions change the picture. A dApp can describe what it wants as a sub-transaction: a self-contained, signable piece that carries no fee and no collateral. Someone still has to wrap it in a balanced top-level transaction. The natural party to do that is the user's wallet.

An earlier attempt to add `balanceTx` to CIP-30 ([PR #170][PR170]) was closed with the advice to make it a separate, optional extension. This CIP is that extension. It also folds signing and submission into one call, so `partialSign` and the separate `submitTx` round trip are no longer needed for this flow.

Sub-transactions also create a second role for the wallet. Besides wrapping sub-transactions, a wallet may need to sign one as a participant, so that another party (a dApp, a service, an aggregator) can include it in their batch. CIP-30 has no way to do this, because `signTx` signs whole transactions. And because Dijkstra replaces `required_signers` with `guards` and nests sub-transactions inside the top-level transaction, `signTx` itself needs to be defined for the new era.

Dijkstra also lets accounts (reward addresses) receive direct deposits. CIP-30 `getBalance` is defined as the sum of `getUtxos`, so those funds are invisible to dApps.

This does not take away multi-party flows such as dApp co-signing or multisig. The wallet only submits a transaction that is complete: if witnesses from the dApp or another party are still missing, it returns the transaction with the user's witnesses added, for the remaining parties to sign and submit.

## Specification

### Extension

Wallets advertise support through CIP-30 `supportedExtensions` as `{ cip: 209 }`. A dApp enables it via `cardano.{walletName}.enable({ extensions: [{ cip: 209 }] })`. The extension adds three methods under its namespace and amends `api.signTx` (see [Amendments to CIP-30 endpoints](#amendments-to-cip-30-endpoints)):

```ts
api.cip209.balanceAndSignTx(
  tx: cbor<transaction | sub_transaction | sub_transactions>
): Promise<BalanceSignResult>

api.cip209.signSubTxs(
  subTxs: cbor<sub_transaction | transaction>[],
  format?: "witnessSet" | "full"
): Promise<cbor<transaction_witness_set>[] | cbor<sub_transaction | transaction>[]>

api.cip209.getBalances(utxoPaginate?: Paginate): Promise<Balance>
```

### `api.cip209.balanceAndSignTx`

The sections up to and including [Result](#result) specify `balanceAndSignTx`. It takes no further parameters. In particular, there is no `partialSign` and no submit flag; see [User confirmation and submission](#user-confirmation-and-submission).

#### Accepted input forms

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

#### Wallet behaviour

##### Balancing: preserve and add around

When the wallet balances a top-level transaction, it MUST preserve everything the dApp supplied: inputs, outputs and their order, collateral inputs, mint, certificates, withdrawals, votes, proposals, reference inputs, guards, validity interval, metadata, datums, scripts and redeemers. The wallet MAY only add:

- inputs;
- outputs of its choosing (for example, change);
- collateral inputs, where the dApp supplied none, and collateral return and total collateral;
- the fee and the validity interval, where the dApp left them unset.

The wallet decides the change address, fee policy, and validity interval, and provides collateral when the dApp did not. The request carries no options to steer them.

If the incomplete top-level transaction contains redeemers, the wallet MUST re-index spend redeemers to match the new sorted input set, re-evaluate execution units, and recompute `script_data_hash` and the fee. Re-indexing is the only change the wallet may make to dApp-supplied witness data; redeemer data is never changed. In Dijkstra, redeemers only use the map format; the legacy list format is no longer accepted.

##### Sub-transactions

- The wallet MUST NOT modify a sub-transaction body. It MAY add its own witnesses to a sub-transaction's witness set (for example when the sub-transaction spends the user's UTxOs), before it signs the top-level transaction.
- The top-level body contains the sub-transactions including their witness sets, so every sub-transaction must be fully witnessed before the top-level transaction is signed. If a sub-transaction still lacks witnesses that the wallet cannot provide, the wallet MUST reject with `TxSignError.SubTxWitnessesMissing`. It checks all sub-transactions first and reports every missing witness, per sub-transaction (index and ID), in one error.
- The wallet provides the fee and the collateral for the whole batch, in accordance with the Dijkstra ledger rules.
- The wallet MUST NOT select, for the top-level transaction, any UTxO that a sub-transaction spends. If two supplied sub-transactions spend the same UTxO, the wallet MUST reject the request with `APIError.InvalidRequest`.

> [!NOTE]
> Informative: per the Dijkstra ledger rules, sub-transactions are applied in list order before the top-level transaction, and their scripts see only their own sub-transaction. A sub-transaction is therefore unaffected by what the wallet adds to the top-level transaction, and its witnesses stay valid.

##### Existing witnesses

A vkey witness signs the transaction body, so balancing invalidates any witness already present on the top-level transaction. If the top-level transaction needs balancing and carries a vkey witness from a key the wallet does not control, the wallet MUST reject with `TxSignError.BodyLocked`. It MUST NOT silently drop such witnesses. This is the case where the dApp or another party signed the top-level transaction before it was balanced: that witness would no longer be valid once the wallet balances it. Only the final, balanced top-level transaction should be signed by the other required parties. A balanced top-level transaction may carry foreign witnesses; the wallet only adds its own.

Parties that need to sign before the wallet SHOULD do so on a sub-transaction, or sign after the wallet has balanced the transaction.

##### Guards

Dijkstra replaces `required_signers` with `guards` (field 14), which may be key hashes or credentials. The wallet treats guards on the top-level transaction and on sub-transactions as signing requirements, including guards that native scripts require (`script_require_guard`).

A sub-transaction can require guards of whoever wraps it (`required_top_level_guards`, field 24). The ledger rejects the batch unless every such credential appears in the top-level `guards`. When wrapping, the wallet MUST add the `required_top_level_guards` of every sub-transaction, and of the top-level transaction itself if the dApp's template carries them, to the top-level `guards` (field 14); `required_top_level_guards` states a demand, `guards` meets it. Then:

- for a key the wallet controls, the wallet signs;
- for another party's key, the wallet returns the transaction with `complete: false`, for that party to sign;
- for a native-script guard, the top-level transaction needs the native script, which the dApp supplies in the top-level transaction. The wallet signs for the keys it controls; if the script or other required signatures are missing, it returns `complete: false`;
- for a Plutus-script guard, the top-level transaction needs the script and a redeemer with purpose `guarding` (tag 6). The wallet cannot create these: the dApp supplies them in the top-level transaction, or the wallet rejects with `TxSignError.UnsatisfiedGuard`, naming the credential in `info`.

##### Evaluation

Supporting this CIP requires the ability to evaluate the whole batch (top-level and all sub-transactions), including Plutus V4 scripts, either locally or through the wallet's backend. The wallet MUST evaluate before signing whenever the batch contains scripts, and MUST NOT sign or submit if evaluation fails (`TxSignError.EvaluationFailed`). This protects the user's collateral, which backs every script in the batch. Wallets built on hardware devices evaluate in their host software or backend.

##### User confirmation and submission

- The wallet presents every call to the user. Declining yields `TxSignError.UserDeclined`.
- If the input is already complete, the signing step is skipped, and the user confirms with a Submit button. This differs from CIP-30 `submitTx`, which submits without user interaction.
- The wallet decides whether to submit. If, after signing, the transaction is complete and passes evaluation, the wallet MAY submit it. If it is not complete (missing witnesses or guards of other parties), the wallet returns it unsubmitted.
- A dApp that must hold back a complete transaction (to submit it later or through its own channel) uses CIP-30 `signTx` instead.

#### Result

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

### `api.cip209.signSubTxs`

```ts
api.cip209.signSubTxs(
  subTxs: cbor<sub_transaction | transaction>[],
  format?: "witnessSet" | "full"     // default "witnessSet"
): Promise<cbor<transaction_witness_set>[] | cbor<sub_transaction | transaction>[]>
```

The wallet signs sub-transactions as a participant: another party wraps them in a top-level transaction and submits. The wallet does not balance, wrap or submit.

- The wallet MUST NOT modify a sub-transaction body.
- One user approval covers the whole list.
- The wallet MUST return exactly one entry per input sub-transaction, in the same order, as with [CIP-103][] `signTxs`. One witness set holds all of the wallet's witnesses for that sub-transaction. If the wallet adds no witnesses to a sub-transaction, it returns an empty witness set (`a0`), or with `"full"` the sub-transaction unchanged.
- With `format: "witnessSet"` (the default) the wallet returns witness sets, as `signTx` does. With `"full"` it returns the signed sub-transactions.
- Sub-transactions the wallet has nothing to sign for are accepted.
- An entry may also be an ordinary transaction. The wallet signs it as `signTx` would and returns its witness set (or, with `"full"`, the signed transaction).
- The method works in any era. Whether a signed sub-transaction is usable yet is for the dApp and the user to judge; the wallet does not refuse it.

#### User confirmation

A signed sub-transaction can be included by anyone who holds it, on its own, until its inputs are spent or its validity interval ends. The party that wraps it, not the user, decides which sub-transactions go into a batch. Therefore:

- The wallet MUST show the balance change of each sub-transaction it signs on its own, and MUST NOT count what the user receives in other sub-transactions.
- When signing more than one sub-transaction, the wallet MUST make clear to the user that each can be included on its own, and that signing them together does not guarantee they are executed together.
- Declining yields `TxSignError.UserDeclined`.

Evaluating sub-transaction scripts is RECOMMENDED but not required: the collateral at stake belongs to the wrapping party, not the user.

> [!NOTE]
> Informative: a dApp that wants an exchange to be atomic puts what the user receives in the same sub-transaction as what the user gives; the ledger then applies both or neither. Alternatively, a sub-transaction can require a top-level guard whose script checks the whole batch.

### `api.cip209.getBalances`

```ts
type Balance = {
  utxos:    cbor<transaction_unspent_output>[],   // same format as getUtxos
  accounts: cbor<{* reward_account => value}>     // balance per account
}

api.cip209.getBalances(utxoPaginate?: Paginate): Promise<Balance>
```

Returns the wallet's holdings in one call:

- `utxos`: the wallet's UTxOs, in the same format as CIP-30 `getUtxos`, so dApps can migrate without changing how they read them.
- `accounts`: one CBOR map from each of the wallet's registered reward addresses (accounts) to its balance, including direct deposits ([CIP-159][]). Each balance is a `value`, so native assets fit once accounts can hold them.
- `utxoPaginate` uses CIP-30's `Paginate` and applies only to `utxos`, with the same semantics as in `getUtxos`. `accounts` is always returned in full.
- Accounts with a zero balance are not listed. Unregistered accounts hold no balance and are not listed; registration status is [CIP-95][]'s concern.

The total a dApp can draw on is the sum of `utxos` and `accounts`. Account funds are spent through a withdrawal naming that reward address, which is why balances are given per account. CIP-30 `getBalance` is unchanged.

Errors: `APIError` only, plus CIP-30 `PaginateError` when `utxoPaginate` is out of range.

> [!NOTE]
> Informative: Dijkstra allows partial withdrawals, so a wallet MAY use account balances as a funding source when balancing in `balanceAndSignTx`. That is wallet policy, like coin selection.

### Amendments to CIP-30 endpoints

When a dApp has enabled this extension, the following applies to existing CIP-30 endpoints for Dijkstra-era transactions. Endpoints not listed here are unchanged: outputs, addresses, values and credentials are identical in Conway and Dijkstra.

#### `api.signTx(tx: cbor<transaction>, partialSign: bool = false): Promise<cbor<transaction_witness_set>>`

- Key-hash `guards` count as signing requirements, as `required_signers` did before.
- `signTx` signs the top-level transaction only; the returned witness set is the top-level witness set.
- If a sub-transaction still needs the user's witnesses, the wallet MUST reject with `TxSignError.SubTxWitnessesMissing`. The dApp uses `signSubTxs` for those first, because a sub-transaction witness added after the top-level is signed would change the top-level body.
- The wallet shows direct deposits (field 25) and account balance intervals (fields 26, 27) to the user.

No parameters or return types change.

### Errors

For `balanceAndSignTx`, `signSubTxs` and the amended `signTx`: if no usable result was produced, the call rejects. Access and input problems use CIP-30 `APIError` (`InvalidRequest`, `Refused`, `AccountChange`, `InternalError`). Signing problems use CIP-30 `TxSignError = { code, info }`, extended with five codes. `info` carries a human-readable explanation.

```ts
TxSignErrorCode {
  ProofGeneration  = 1,  // CIP-30
  UserDeclined     = 2,  // CIP-30
  BodyLocked       = 3,  // needs balancing, but carries foreign vkey witnesses
  CannotBalance    = 4,  // insufficient funds, min-UTxO, size limit or device limitations
  EvaluationFailed = 5,  // a script in the batch fails phase-2 evaluation
  UnsatisfiedGuard = 6,  // a required Plutus-script guard lacks its script or redeemer
  SubTxWitnessesMissing = 7  // sub-transactions lack witnesses the wallet cannot provide
}
```

Codes 3–7 are returned only when this extension is enabled: by its methods, and code 7 also by the amended `signTx`. Without the extension, `signTx` never returns them, so existing behavior is unchanged.

### Interaction with other CIPs

| CIP | Relationship |
|-----|--------------|
| [CIP-30][] | Extended. `signTx` is amended for Dijkstra transactions when the extension is enabled; other endpoints are unchanged. |
| [CIP-21][] | Hardware-wallet restrictions are the wallet's concern. A wallet MAY reject with `CannotBalance` or `ProofGeneration` when its device cannot handle a transaction. |
| [CIP-95][] | Governance certificates, votes, and proposals in the input are preserved like any other dApp-supplied field. CIP-95 is also the precedent for amending `signTx` for a new era. |
| [CIP-103][] | Unaffected. `balanceAndSignTx` handles one transaction per call; bulk signing stays with CIP-103. `signSubTxs` follows the `signTxs` pattern. |
| [CIP-106][] / [CIP-141][] | Multisig and script wallets sign their own part and return `complete: false`. Native scripts can now require a guard (`script_require_guard`). |
| [CIP-118][] | Provides the sub-transaction model this CIP builds on. |
| [CIP-159][] | Accounts receiving direct deposits; `getBalances` reports their balances in `accounts`. Token whitelists (CIP-159 phase 2) are not part of Dijkstra as implemented and are left to a later extension. |
| [CIP-198][CIP198] | Service layer for publishing sub-transactions. Publishing and lifecycle of "intents" are out of scope here; see Rationale. |

### Versioning

This extension is identified by its CIP number in `supportedExtensions` and carries no separate version field. Backwards-compatible clarifications may be made to this document. Any change to the method signatures, the accepted input forms, the result shapes, the amendments or the error codes requires a new CIP that supersedes this one and is advertised under its own extension number.

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

Change address, maximum fee, and collateral were considered and rejected as dApp parameters: they are wallet policy. A dApp can still supply its own collateral as part of the transaction, alongside its script inputs and outputs, and the wallet preserves it while balancing. What is not possible is collateral the dApp has already signed for, because balancing would invalidate that signature: the dApp signs after the wallet returns the balanced transaction (`complete: false`), as in today's `signTx` flow.

### Why a single transaction per call?

Supporting an ordered list (superseding CIP-103) has been considered. Dijkstra does not allow chaining inside one batch: all inputs of a batch must exist before it is applied. Chaining across batches is possible on sub-transaction outputs, which are keyed by the sub-transaction's own ID. But a list exposes users to partial execution: an earlier transaction lands, a later one fails, and promised results never arrive. A single Dijkstra batch is all-or-nothing, which is the safer unit for one user approval.

### Why no normative verification procedure for dApps?

A hash comparison only works for fully built transactions, so a mandated check would cover only part of the scope. The CIP states the wallet's obligations; dApps may compare the returned transaction or sub-transaction IDs if they wish.

### Why extend `TxSignError` instead of a new error type?

dApps already handle `TxSignError` from `signTx`. New numeric codes let them react programmatically, while `info` carries the human-readable message.

### Why a separate method for signing sub-transactions?

`balanceAndSignTx` covers the wallet as the one wrapping and submitting. Signing a sub-transaction for someone else's batch is a different role: the wallet must not wrap or submit, and the result is witnesses, not a transaction. `signSubTxs` follows CIP-103 `signTxs` (a list in, one entry per input in the same order out) so that dApps meet a familiar pattern.

The return value follows one principle: the wallet returns what it changed. `balanceAndSignTx` changes the body, so it returns the full transaction; `signSubTxs` only adds witnesses, so a witness set is enough, as with `signTx`. `format: "full"` is a convenience for dApps without a CBOR library; the default keeps responses small. A map keyed by sub-transaction ID was considered, but positional order with a strict one-entry-per-input rule stays closest to CIP-103.

### Why must sub-transactions be complete before the top-level is signed?

The top-level body contains the sub-transactions including their witness sets, so the top-level body hash covers every sub-transaction witness. A sub-transaction witness added after the top-level is signed invalidates the top-level witnesses. This ordering follows from the ledger, which is why both `balanceAndSignTx` and the amended `signTx` reject incomplete sub-transactions with one error that lists everything missing.

### Why amend `signTx`?

`balanceAndSignTx` does not fully replace `signTx`: dApps that must hold back a complete transaction still use `signTx`, so it will receive Dijkstra transactions and needs a definition for them. The amendments are kept to what Dijkstra forces: they make `signTx` stricter and clearer, not more capable. The three methods split the work:

| Method | Role | Who builds the transaction? | Submits? |
|---|---|---|---|
| `signTx` (amended) | Sign a transaction the dApp has fully built | dApp | No, the dApp keeps it |
| `balanceAndSignTx` | Complete, sign and submit | Wallet, around the dApp's part | Wallet decides |
| `signSubTxs` | Sign as participant in someone else's batch | dApp or another party | No, another party wraps it |

### Why `getBalances` instead of changing `getBalance`?

CIP-30 defines `getBalance` as "the same as summing the results of `api.getUtxos()`", and CIP-0001 does not allow substantial changes to Active CIPs. Changing its shape or meaning would break existing dApps, including those calling wallets that adopt the change without the dApp having enabled this extension. CIP-30 itself describes extensions as "a smart versioning scheme", and CIP-95 introduced fundamental Conway features the same way.

One call returning both the UTxOs and the account balances gives dApps the full picture of what they can spend. `utxos` keeps the `getUtxos` format, so existing coin-selection code works unchanged; `accounts` uses the same CBOR map shape the ledger uses for deposits and withdrawals, keyed by reward address because withdrawals name a specific account. A successor to CIP-30 could adopt this as its baseline `getBalance` after the Dijkstra hard fork.

### Why are intents out of scope?

"Intent" is not a ledger concept: in Dijkstra, an intent is a signed sub-transaction waiting to be wrapped, which `signSubTxs` produces. Publishing, discovery, pending state and cancellation happen off-chain, for example in the [CIP-198][CIP198] service layer, which is still a draft, and there is no agreed definition of intents yet. Methods for that lifecycle are better defined once such a layer settles.

### Backward compatibility

The extension is opt-in through the CIP-30 extension mechanism. Without it, existing CIP-30 methods, their parameters and their error codes are unchanged. With it, the `signTx` amendments change no parameters or return types; they define behavior for Dijkstra transactions, which CIP-30 does not cover. dApps that do not enable the extension are unaffected.

## Path to Active

### Acceptance Criteria

- [ ] At least two wallets implement the extension, including the sub-transaction input forms on a Dijkstra-era testnet.
- [ ] At least one dApp uses the extension in production with more than one of those wallets without wallet-specific code.
- [ ] A test suite covering each input form, `signSubTxs`, `getBalances`, the `signTx` amendments, every new error code, and the submit-only flow is published.

### Implementation Plan

- [ ] Circulate this proposal among wallet teams and collect feedback.
- [ ] Reference implementation in one wallet on a Dijkstra testnet.

## References

- [CIP-30][] – Cardano dApp-Wallet Web Bridge
- [CIP-95][] – Web-Wallet Bridge, Conway ledger era
- [CIP-103][] – Web-Wallet Bridge, bulk transaction signing
- [CIP-118][] – Nested Transactions
- [CIP-159][] – Account Address Enhancement
- [PR #170][PR170] – CIP-0030: balanceTx (closed)
- [CIP-198][CIP198] – Nested Transactions, Service Layer (draft)
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
[CIP-159]: https://github.com/cardano-foundation/CIPs/tree/master/CIP-0159
[PR170]: https://github.com/cardano-foundation/CIPs/pull/170
[CIP198]: https://github.com/cardano-foundation/CIPs/pull/1257
