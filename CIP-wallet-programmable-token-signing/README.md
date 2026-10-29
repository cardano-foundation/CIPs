---
CIP: "?"
Title: Web-Wallet Bridge - Programmable Token Signing
Category: Wallets
Status: Proposed
Authors:
    - Thomas Kammerlocher <thomas.kammerlocher@cardanofoundation.org>
    - Mateusz Czeladka <mateusz.czeladka@cardanofoundation.org>
Implementors: []
Discussions:
    - Original PR: https://github.com/cardano-foundation/CIPs/pull/1312
Created: 2026-10-29
License: CC-BY-4.0
---

## Abstract

[CIP-113] programmable tokens are held at addresses whose payment credential is a shared
**programmable logic base** script, and whose stake credential identifies the owner. The owner
authorises a spend by signing with that owner key. [CIP-30] wallets do not recognise these
holdings as the user's own, and today most of them refuse to sign such transactions or show a
misleading summary.

This proposal defines a [CIP-30] extension in which a wallet agrees to witness transactions that
spend the user's own [CIP-113] holdings, under strict safety rules. The wallet resolves every input
independently. It signs only when the transaction names the owner key in `required_signers` and
does nothing else that the key authorises. It shows the user a summary it computed itself,
including every token that leaves the user's holdings. A dApp can detect support through the
standard extension mechanism, without trying and failing.

## Motivation: Why is this CIP necessary?

### The problem

A [CIP-113] "smart wallet" is the set of UTxOs at `programmableLogicBase ‖ owner credential`. The
payment credential is a script shared by every holder. Ownership is in the stake-credential slot.
When the owner credential is a public-key hash, the base layer accepts a spend only if the
transaction is signed by that key.

Wallets fail at this in three ways:

1. **They don't count the holdings.** UTxO bookkeeping is keyed on payment credentials, so a
   wallet sees these inputs as somebody else's script outputs.
2. **They refuse to sign, or sign blindly.** A wallet that refuses blocks every [CIP-113] token
   from being used through dApps. A wallet that signs whatever lists its key in `required_signers`
   shows the user "you are sending 0" for a transaction that moves all their programmable tokens.
3. **The key in question is powerful.** The owner key is usually the account's **stake key**. A
   stake-key witness also authorises certificates (delegation, DRep registration, votes) and
   reward withdrawals. A dApp that can get it signed with a misleading summary can do much more
   than move tokens.

### Why an extension

The behaviour fits within [CIP-30]'s `signTx`. What is missing is (a) the rules under which a
wallet may safely sign, and (b) a way for a dApp to know that a wallet follows them. A
dApp that cannot detect support has to build the transaction, ask, and handle a refusal halfway
through a user flow. Following the precedent of [CIP-95], which extended `signTx` to governance
content, this proposal is an additive, namespaced [CIP-30] extension.

### Use cases

- **Any [CIP-113] token used from a dApp:** regulated stablecoins and real-world assets with
  transfer rules, tokens with freeze or allowlist logic, and DeFi protocols handling them.
- **Confidential transfers.** This proposal comes from ongoing work on confidential notes held as
  [CIP-113] programmable tokens, prototyped and tested on Preview and Preprod. Together with
  [Web-Wallet Bridge - Encryption Keys] (which lets a dApp *read* confidential notes), it lets users
  *spend* them from any conforming wallet. Each proposal is useful without the other.

### Stakeholders

Wallet implementors, [CIP-113] token issuers and substandard authors, and dApp developers building
on programmable tokens.

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
> `api.experimental.programmableTokens`, as required by [CIP-30]'s
> [Experimental API](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0030#experimental-api),
> and MUST NOT list them in `getExtensions()`.

A wallet MUST NOT enable the extension for an account it cannot sign for under the
[signing rules](#signing-rules), for example a hardware-wallet account whose device cannot display
the [summary](#summary).

### Concepts

- **Programmable logic base (PLB):** the [CIP-113] `programmableLogicBase` spend script of one
  deployment, identified by its script hash. Its hash depends on the deployment's protocol
  parameters, so each network can have several.
- **Recognised PLB:** a PLB hash the wallet has chosen to support on the current network (see
  [Recognised deployments](#recognised-deployments)).
- **Owner credential:** a public-key hash in the stake-credential slot of an address at a
  recognised PLB. [CIP-113] allows either the account's stake key or one of its payment keys here.
- **Own programmable input:** a transaction input whose resolved output is at a recognised PLB
  and whose owner credential is a key of the connected account.
- **Programmable transaction:** a transaction with at least one own programmable input.

### Recognised deployments

- A wallet MUST keep, per network, the list of PLB hashes it recognises, from a source it
  controls (built in, or updated by the wallet vendor).
- A wallet MUST NOT add a PLB hash to that list because a dApp, a transaction or an address says
  so.
- Inputs at a PLB the wallet does not recognise are not own programmable inputs. They take the
  ordinary [CIP-30] path.

### Programmable Tokens API

#### `api.cip????.getProgrammableLogicBases(): Promise<HexString[]>`

Errors: `APIError`

Returns the recognised PLB hashes for the current network, as 28-byte hex strings. An empty array
means the wallet supports the extension but recognises no deployment on this network.

#### `api.cip????.signTx(tx: cbor<transaction>, partialSign: bool = false): Promise<cbor<transaction_witness_set>>`

Errors: `APIError`, `TxSignError`

Extends [CIP-30]'s
[`signTx`](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0030/README.md#apisigntxtx-cbortransaction-partialsign-bool--false-promisecbortransaction_witness_set)
to programmable transactions.

- For a transaction that is not a programmable transaction, it behaves exactly like
  `api.signTx`.
- For a programmable transaction, the wallet MUST apply the [signing rules](#signing-rules) and
  show the [summary](#summary), and MUST NOT return any witness unless every rule holds and the user
  approves.
- If it signs, the wallet returns the witnesses for the account's own keys that the transaction
  requires, including the owner-key witness for the `required_signers` entry. `partialSign` has
  the same meaning as in [CIP-30].

This extension does not change `api.signTx`. A wallet MAY also accept programmable transactions in
`api.signTx`, but only under the same rules.

#### HexString

```ts
type HexString = string; // lowercase hexadecimal, no prefix
```

### Signing rules

All rules are checked before the user is asked to approve, and again before witnesses are
released.

1. **Independent input resolution.** The wallet MUST resolve every input and reference input
   from a source that the dApp does not control. For each input it MUST obtain the producing
   transaction and use the output only if that transaction's body hashes to the input's
   transaction id. If any input cannot be resolved this way, the wallet MUST refuse.
2. **Owner key named by the wallet.** For every own programmable input, the transaction's
   `required_signers` MUST contain the hash of its owner credential. The wallet MUST compute the
   hashes of its own keys itself, and MUST compare credentials as hashes, not as address strings.
3. **Nothing else uses a key credential (allowlist).** If the transaction requires a witness from
   a key that is used as an owner credential, its body MUST contain:
   - no certificates;
   - no voting procedures and no proposal procedures;
   - no treasury donation, or a donation of zero;
   - withdrawals only from **script**-credential reward accounts (the zero withdrawals that
     [CIP-113] uses to run its validators). A withdrawal from any key credential MUST be refused.

   New body fields introduced by later ledger eras MUST be refused until a revision of this CIP
   allows them.
4. **Strict transaction frame.** The request MUST decode as a single well-formed transaction with
   no trailing bytes, MUST NOT contain duplicate inputs, and MUST be marked valid. Own programmable
   inputs MUST NOT appear as collateral.
5. **Approval bound to one transaction.** The user's approval MUST apply to the exact
   transaction body hash shown in the summary. A changed body MUST need a new approval. Witnesses
   MUST be released to the dApp at most once, and only after approval.
6. **Any failure is a refusal.** If any rule fails, or the wallet cannot evaluate it, the wallet
   MUST NOT return witnesses. Each failure MUST be reported as listed in [Errors](#errors).

### Summary

A wallet MUST compute the summary only from the decoded body and the independently resolved
inputs. It MUST NOT use labels, amounts or metadata supplied by the dApp. The summary MUST show:

- the network fee, and the account's **net change** in ADA and in each asset, counting its
  ordinary UTxOs and its own programmable holdings together;
- the programmable inputs spent, with their owner shown as the user, another owner, or a script;
- the programmable outputs, grouped by PLB and owner;
- tokens minted and burned, with full policy ids;
- **outgoing tokens**: every token of a policy held in an own programmable input that ends up
  anywhere other than the account's own holdings at the same PLB, whether moved directly or burned
  and minted again.

If there are outgoing tokens, the wallet MUST require an explicit acknowledgement from the user
(for example a checkbox stating that these tokens will no longer be theirs) before Sign is
enabled.

If an amount cannot be determined, for example because the token hides amounts, the wallet MUST
say so for that line, and MUST NOT show zero or omit the line.

### Token profiles

Some [CIP-113] substandards hide amounts, so the net change can only be computed by a wallet that
understands the token's format. A **token profile** is a specification, published in a CIP, that
lets a wallet open and verify such tokens.

- A wallet MAY implement token profiles. A wallet that implements one MUST use it to show verified
  amounts for the account's own spent tokens and own change.
- If an own spent token cannot be opened under a profile the wallet implements, the wallet MUST
  refuse to sign.
- If own change cannot be opened, or does not match its on-chain commitment, the wallet MUST block
  signing. This stops a dApp from sealing the user's change to someone else.
- A wallet MUST NOT state what another owner receives under a profile that hides amounts.

This CIP registers no token profile. Confidential notes are expected to be the first, specified
alongside [Web-Wallet Bridge - Encryption Keys].

### Errors

This extension reuses [CIP-30]'s
[`APIError`](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0030#apierror) and
[`TxSignError`](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0030#txsignerror) codes.
`info` values in the table are machine-readable and prefixed with `cip????:`.

<!-- prettier-ignore-start -->
| Condition | Error | `info` |
|---|---|---|
| Origin not connected, wallet locked, or the extension is not available for this account or network | `APIError` `Refused` (−3) | free text |
| One or more inputs cannot be independently resolved (rule 1) | `APIError` `Refused` (−3) | `cip????:unresolved-input:[i,…]` |
| The request is not a single well-formed, valid transaction, or has duplicate inputs or programmable collateral (rule 4) | `APIError` `InvalidRequest` (−1) | `cip????:bad-frame` |
| `required_signers` lacks an owner credential (rule 2) | `APIError` `InvalidRequest` (−1) | `cip????:missing-owner-signer` |
| The body contains a field the allowlist forbids (rule 3) | `APIError` `InvalidRequest` (−1) | `cip????:forbidden:<field>` |
| An own spent token cannot be opened under an implemented profile | `APIError` `InvalidRequest` (−1) | `cip????:unverifiable-input:[i,…]` |
| The active account changed during the request | `APIError` `AccountChange` (−4) | free text |
| The user declined, closed the prompt, or let it expire; or signing was blocked by the summary checks | `TxSignError` `UserDeclined` (2) | free text |
| `partialSign` is `false` and the wallet lacks a required key | `TxSignError` `ProofGeneration` (1) | free text |
| Any other failure | `APIError` `InternalError` (−2) | free text |
<!-- prettier-ignore-end -->

Indices are 0-based positions in the transaction body's input set, ascending, written as JSON
without spaces. `<field>` is the CDDL field name, for example `certs` or `withdrawals`.

A block by the summary checks (unopenable or mis-sealed change) is reported as `UserDeclined` on
purpose: its reason is shown to the user, not the dApp.

dApps SHOULD call `getProgrammableLogicBases()` before building a transaction, and SHOULD NOT retry
after `Refused` or `InvalidRequest` without changing the transaction.

### Versioning

This extension is versioned by its CIP number, as are all [CIP-30] extensions. A
backwards-incompatible change requires a new extension CIP. Allowing a new body field in rule 3, or
registering a token profile, is backwards-compatible.

## Rationale: How does this CIP achieve its goals?

### Why a namespaced `signTx`

Changing `api.signTx` would change behaviour for dApps that never asked for it. A namespaced
endpoint, as in [CIP-95], makes the stricter rules an explicit opt-in on both sides. A wallet may
still accept these transactions in `api.signTx`, because some deployed dApps already call it.

### Why an allowlist, not a denylist

The owner key is usually the stake key, which also controls delegation, governance and rewards.
Listing what is forbidden would leave every future ledger feature allowed by default. An
allowlist refuses anything not explicitly permitted, including fields added by future eras.
Script-credential withdrawals stay allowed, because [CIP-113] runs its validators as zero
withdrawals.

### Why resolve inputs independently

The summary is only as honest as the inputs behind it. If a dApp or an indexer could supply input
values, it could make an outgoing transfer look like a self-transfer. Checking that each producing
transaction hashes to the input's transaction id makes substitution detectable, whatever the source.

### Why a summary the wallet computes

For programmable inputs, a payment-credential view of the transaction shows nothing leaving the
wallet. The net change across ordinary and programmable holdings, together with the
outgoing-tokens acknowledgement, gives the user the one fact that matters: what they will stop
owning.

### The validity flag

The `is_valid` flag is outside the signed body hash. A dApp could submit the same body marked
invalid behind a script that fails on purpose, costing the user their collateral. Rule 4 binds what
the wallet verifies. Since the ledger requires collateral at key addresses, the exposure is limited
to the collateral the wallet shows.

### Hardware wallets

Hardware devices sign what they display. If a device cannot show the summary, a software wallet
in front of it would be asking the user to trust the host for exactly what this CIP is meant to
protect. Such accounts do not enable the extension until device apps can display it.

### Relationship to other proposals

- **[CIP-113]** defines the tokens and the ownership model this CIP relies on.
- **[CIP-95]** is the template for extending `signTx` through a namespaced extension.
- **[Web-Wallet Bridge - Encryption Keys]** is the companion proposal for reading confidential
  notes. Confidential transfers through dApps need both. Neither depends on the other.
- **[CIP-30] `signData`** already signs with the stake key for reward addresses. Schemes that
  publish claims signed by the owner (such as viewing-key registration) need no change from
  this CIP.
- **[CPS-0010] / CIP-0144:** the signing rules do not depend on the transport, so a future
  connector can adopt them unchanged.

### Backwards Compatibility

This proposal is purely additive. `api.signTx` is unchanged. dApps and wallets that do not use the
extension are unaffected.

### Open Questions

1. **`api.signTx` or namespaced only.** Should conforming wallets be required to apply these rules
   to programmable transactions in `api.signTx` as well, so that existing dApps benefit?
2. **Deployment discovery.** How should wallets learn which PLB deployments to recognise? Could
   [CIP-113] define a way to verify a deployment from its protocol-parameters NFT instead of each
   wallet vendor keeping a list?
3. **Compatibility with the prototype.** The Gero prototype relaxes `api.signTx` directly, answers
   every rule failure with `Refused` and free-text `info`, and runs on Preview and Preprod only. How
   should it migrate?
4. **Chained transactions.** Rule 1 refuses inputs from unconfirmed transactions. The prototype
   also accepts outputs of transactions it signed itself in the last few minutes. Should the CIP
   allow this?
5. **Owner keys in other scripts.** A signature by the owner key could also satisfy unrelated
   scripts in the same transaction that check for that key. Should the wallet show, or refuse,
   script inputs it cannot classify when an owner key is required?
6. **Where token profiles live.** Should profiles be registered here, or in the substandard CIPs
   that define each token format?

## Path to Active

### Acceptance Criteria

- [ ] A CIP number is assigned.
- [ ] Open Questions 1 and 2 are resolved in the specification.
- [ ] Conformance test transactions are published for each rule and error, on at least one
      testnet deployment of [CIP-113].
- [ ] A security review of the signing rules by wallet and ledger experts is completed.
- [ ] At least two wallets implement the extension under its assigned namespace.
- [ ] At least one dApp uses the extension in production.

### Implementation Plan

- [x] Prototype in Gero Wallet (branch `feat/cip30-confidential-transfers`), relaxing `signTx`
      for own [CIP-113] holdings under these rules. Preview and Preprod only, software accounts
      only, mainnet refused.
- [x] Reference dApp spending confidential [CIP-113] notes through the prototype, verified on
      Preprod.
- [ ] Align the prototype with this specification (namespace, `getProgrammableLogicBases`, error
      codes).
- [ ] Engage other wallet implementors and [CIP-113] substandard authors via the wallet working
      groups and [CPS-0010].

## References

- [CIP-30] — Cardano dApp-Wallet Web Bridge
- [CIP-95] — Web-Wallet Bridge - Conway ledger era
- [CIP-113] — Programmable token-like assets
- [CPS-0010] — Wallet Connectors
- [Web-Wallet Bridge - Encryption Keys] — CIP-???? (PR #1309)
- [RFC 2119] — Key words for use in RFCs to Indicate Requirement Levels

## Acknowledgements

The signing rules come from the confidential-notes proof of concept on [CIP-113] programmable
tokens and its Gero Wallet integration.

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).

[CIP-30]: https://github.com/cardano-foundation/CIPs/tree/master/CIP-0030
[CIP-95]: https://github.com/cardano-foundation/CIPs/tree/master/CIP-0095
[CIP-113]: https://github.com/cardano-foundation/CIPs/tree/master/CIP-0113
[CPS-0010]: https://github.com/cardano-foundation/CIPs/tree/master/CPS-0010
[Web-Wallet Bridge - Encryption Keys]: https://github.com/cardano-foundation/CIPs/pull/1309
[RFC 2119]: https://www.rfc-editor.org/rfc/rfc2119
