---
CIP: 185
Title: Governance Action Addendums
Category: Metadata
Status: Proposed
Authors:
    - Nicolas Cerny <nicolas.cerny@cardanofoundation.org>
    - Pi Lanningham <pi@sundaeswap.finance>
Implementors: []
Discussions:
    - Original PR: https://github.com/cardano-foundation/CIPs/pull/1180
    - Concurrent PR (closed): https://github.com/cardano-foundation/CIPs/pull/1182
Created: 2026-04-21
License: CC-BY-4.0
---

## Abstract

This proposal defines a metadata standard allowing governance action proposers to provide additional, cryptographically verifiable context to voters after the initial governance action has been submitted. By broadcasting append-only updates via standard transactions anchored under the [CIP-0010][] metadatum label `1694` reserved by [CIP-0100][], this standard reduces information asymmetry between voters while strictly preserving the immutability of the original governance action metadata. Updates are typed (clarifications, corrections, narrowings, commitments, withdrawals, or general updates), witnessed by the original authors with the same keys as the original proposal (or, where a proposal has no valid author signature, by the key of its deposit return account as a clearly labelled fallback), and discoverable by any chain indexer without reliance on a particular off-chain platform.

## Motivation: Why is this CIP necessary?

Under the current CIP-1694 and [CIP-0108][] frameworks, proposers lack a standardized, on-chain mechanism to provide ongoing context or reactions to a governance action once it is submitted. Consequently, proposers often distribute additional information — such as answers to community questions, rationale refinements, or strategic adjustments — through public or private off-chain channels.

This creates information asymmetry: large DReps with direct communication lines to proposers receive vital context, while smaller DReps and the wider voting public do not. Furthermore, the governance action's metadata anchor is immutable by design: the on-chain anchor commits to a hash of the metadata document, so additional context cannot be provided by editing the original document without breaking that anchor.

The consequences extend beyond the voting window. Many governance actions have off-chain effects that someone must later interpret — a treasury withdrawal whose proceeds an administrator disburses against milestones, or acceptance criteria a reviewer must apply. Ambiguities and typos that survive the vote become expensive at that stage, and authors currently have no recognized mechanism to clarify them after submission.

To create a level playing field without violating immutability, proposers need a credible, decentralized, append-only mechanism to share updates. These updates must be cryptographically proven to originate from the proposal's authors, or be clearly labelled where that proof is not possible, ensuring equal visibility across all governance explorers and tooling.

**Disclaimer:** These updates are informational by default. They provide context and rationale but cannot technically alter the on-chain execution payload of the original governance action. The conditions under which downstream interpreters may treat certain updates as authoritative refinements of the original proposal are described in [Authority of updates](#authority-of-updates).

## Specification

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in [RFC 2119][].

This standard acts as an extension to the **CIP-0100** (Governance Metadata) framework, utilizing standard Cardano transactions to build an append-only log of contextual updates against a submitted governance action.

### Document type

We introduce a new JSON-LD `@type` named `GovernanceActionUpdate`. A document of this type inherits the CIP-0100 top-level structure (`hashAlgorithm`, `authors`, `body`). Signing, canonicalization, hashing, and witness validation are performed exactly as specified in CIP-0100.

### Context and schema

This CIP provides the following shared assets:

- [JSON-LD Context](./cip-0185.common.jsonld)
- [JSON Schema](./cip-0185.common.schema.json)
- [Example update document](./examples/update.jsonld)
- [Test vector](./test-vector.md)

The JSON-LD context is complete: it already contains every CIP-0100 term this document type uses. Documents MUST use it as a single context, either inlined (as in the example) or referenced by URL. They MUST NOT combine it with the CIP-0100 context in an `@context` array. Both define `body`, and in JSON-LD the later definition replaces the earlier one, which silently removes the replaced fields from the data that the authors sign.

A document that adds terms from another extension MUST add them inside the scoped `@context` of `body`, keeping the terms already mapped there. Authors MUST NOT sign a document in which any property of `body` is not mapped by its `@context`, and tooling SHOULD warn about such properties because no signature covers them.

### Body fields

The `body` of a `GovernanceActionUpdate` MUST contain:

- `governanceActionId` — the identifier of the on-chain governance action this update pertains to, in lower-case [CIP-0129][] bech32 form (`gov_action1…`).
- `updateType` — one of the following values:
  - `Update` — general informational context with no claim to refine the proposal: answers to community questions, progress reports, links to discussions.
  - `Clarification` — disambiguates language in the original proposal without changing its meaning. Appropriate when two readings are both defensible and the authors specify which was intended.
  - `Correction` — fixes a clear typographical or factual error whose correction does not change the proposal's intent (e.g. a transposed digit in a reference, a misspelled name).
  - `Narrowing` — explicitly restricts the scope of the proposal (e.g. lowering a withdrawal amount, tightening milestone acceptance criteria, removing an optional deliverable).
  - `Commitment` — binds the authors to a specific course of action that was left implicit or discretionary in the original proposal (e.g. "milestone 2 will be evaluated against criteria X, Y, Z").
  - `Withdrawal` — the authors formally disavow the proposal. A ratified on-chain action cannot itself be undone, but a `Withdrawal` gives voters a strong signal to reconsider, and gives downstream interpreters an instruction about the authors' current position.
- `sequenceNumber` — a positive integer establishing the order of the append-only update log for a given governance action, starting at `1` and incrementing by `1` with each new update.
- `updateContext` — a freeform text field (supporting Markdown) where the proposers provide the prose of the update.

The `body` MAY additionally contain:

- `supersedes` — an integer referencing a previous `sequenceNumber`. If present, tooling SHOULD indicate that the referenced previous update has been explicitly retracted or corrected by the authors. The constraints in [Scope constraints](#scope-constraints) apply to superseding updates.
- `bindingStatements` — an array of structured statements that make a `Clarification`, `Correction`, `Narrowing`, or `Commitment` machine-actionable for downstream reviewers. Each entry contains:
  - `field` (REQUIRED) — a human-readable locator for the aspect of the proposal being amended (e.g. `"milestones[2].acceptance"`, `"withdrawal.amount"`).
  - `originalText` (OPTIONAL) — the text from the original proposal being clarified or corrected, quoted verbatim.
  - `revisedText` (REQUIRED) — the replacement or refinement.
  - `rationale` (OPTIONAL) — a brief explanation justifying why this is an update rather than a new proposal.
- `references` — links to off-chain discussions, community town halls, FAQs, or previous metadata, following the CIP-0100 reference shape, with the optional `referenceHash` of CIP-0108.

The CIP-0100 fields `comment` and `externalUpdates` MAY also be present and keep the meaning CIP-0100 gives them.

### Authorship and witnesses

To prove provenance, the update document MUST utilize the `authors` array and `witness` structure defined in CIP-0100. Each witness MAY use any `witnessAlgorithm` defined by CIP-0100 (`ed25519`) or CIP-0108 (`CIP-0008`).

An author is identified by their Ed25519 public key, not by the algorithm. A witness on an update need not use the algorithm that the same key used in the original metadata, and different witnesses in one document MAY use different algorithms. Where `publicKey` is a COSE key, as some `CIP-0008` signers produce, tooling MUST extract the Ed25519 public key from it before comparing.

Tooling first establishes who the original authors are. It MUST use only metadata of the *original* governance action whose raw bytes match the anchor hash recorded on-chain. Let `O` be the set of distinct Ed25519 public keys, compared as decoded bytes, whose witnesses in the `authors` array of that document are valid. Tooling MAY keep bytes it has verified, so that `O` remains known if the anchor URL later stops serving.

If `O` is empty, or the original metadata cannot be verified, no document can be verified as an author update for that action, and no update is author-complete. The only other path is the [deposit return account fallback](#deposit-return-account-fallback). Tooling MUST NOT treat the absence of original authors as an author set that is trivially satisfied.

If the original metadata carries a [CIP-0169][] `onChain` property that does not match the on-chain action, its author signatures may have been copied from another proposal. Tooling SHOULD warn about the mismatch next to every update for that action.

For author updates:

- Every witness on an update MUST verify against a key in `O`. An update MAY be signed by any non-empty subset of `O`; one author can publish an informational update without coordinating signatures from all co-authors.
- An update is **author-complete** when `O` is not empty and the update carries a valid witness for *every* key in `O`. Only author-complete updates are eligible for the authoritative treatment described in [Authority of updates](#authority-of-updates); this prevents a single co-author from unilaterally speaking for the whole author set on anything that refines the proposal.
- Tooling MUST verify witnesses and MUST visually demarcate exactly which authors from the original proposal signed the update — e.g. "signed by 2 of 4 original authors" — and whether the update is author-complete.
- If a document's witnesses do not match any key in `O`, or its signatures are invalid, tooling MUST NOT present it as an author update. Following CIP-0100's display guidance, tooling SHOULD still surface such documents with a prominent warning (e.g. "claims to be an author update but is not signed by the original authors") rather than silently hiding them: suppression can mask both indexer bugs and impersonation attempts that are themselves useful voting signal.

### Deposit return account fallback

A proposal without any valid author witness has no author key to prove an update against. For these proposals only, the key of the deposit return account MAY sign updates instead. The deposit return account is the reward account in the on-chain proposal procedure that receives the governance action deposit back.

An update is a **deposit-account update** when all of the following hold:

1. The original metadata has been verified against the on-chain anchor hash, and `O` is empty.
2. The deposit return account has a key credential. Script credentials have no fallback in this version.
3. The update carries a valid witness whose Ed25519 public key hashes (blake2b-224) to that credential.

The update document, its signed `governanceActionId`, and its anchoring are otherwise the same as for author updates. The fallback has the following limits:

- If `O` is not empty, a witness by the deposit return account has no special meaning, unless its key is itself in `O`. The fallback never overrides or adds to signed authors.
- A deposit-account update is informational. It is never author-complete, and is not eligible for the authoritative treatment described in [Authority of updates](#authority-of-updates), whatever its `updateType`. The [scope constraints](#scope-constraints) apply to it.
- Tooling MUST label it as "signed by the deposit return account" or similar, and MUST NOT describe the signer as an author. The deposit return account shows who receives the deposit, not who wrote or submitted the proposal.
- If the original metadata cannot be retrieved, or does not match its anchor hash, `O` is unknown. Tooling SHOULD show an update that meets conditions 2 and 3 with a prominent warning that the authors are unknown, and MUST NOT present it as a verified deposit-account update. This keeps a submitter from gaining the role by taking the original document offline. If the original metadata is verified later, tooling MUST re-evaluate the update.

### Scope constraints

Updates exist to clarify and narrow, never to expand. An update — regardless of `updateType` — MUST NOT attempt to widen the scope of the original proposal. Specifically:

- An update against a treasury withdrawal MUST NOT increase the withdrawn amount or the set of recipients.
- Where the proposal defines acceptance criteria for an off-chain administrative process, an update MAY add or tighten those criteria but MUST NOT remove or relax them.
- An update MUST NOT extend deadlines or windows beyond those declared in the original proposal.
- An update MUST NOT supersede a prior update in a way that relaxes a narrowing or commitment already made. An author-complete update may be superseded only by another author-complete update; a partially-signed update that names a prior author-complete update in `supersedes` MUST NOT be treated as having displaced it.

The `Withdrawal` type is exempt from these constraints, since disavowing the proposal entirely is by definition not a widening. Tooling SHOULD flag updates that appear to violate these constraints and MUST NOT present them as authoritative refinements; the correct vehicle for widening a proposal is a new governance action.

### On-chain anchoring

Because the original governance action's anchor cannot be altered, updates MUST be published via a standard Cardano transaction carrying transaction metadata under the [CIP-0010][] metadatum label `1694`, which CIP-0100 reserves for governance-related metadata. No new metadatum label is requested by this CIP.

**The 64-byte ledger constraint:** the Cardano ledger rejects any transaction containing a metadata string exceeding 64 bytes; this is enforced at the ledger level, not merely an indexer concern.

- A 32-byte hash is exactly 64 characters when hex-encoded, so `txHash` and `dataHash` MAY remain single strings.
- Standard URLs and IPFS URIs frequently exceed 64 bytes, so the `uri` field MUST be encoded as an array of strings, each element at most 64 bytes, which consumers concatenate in order.

The on-chain transaction metadata MUST follow this structure:

```json
{
  "1694": {
    "@type": "GovernanceActionUpdateAnchor",
    "txHash": "<hex-encoded transaction hash of the original governance action>",
    "index": 0,
    "dataHash": "<hex-encoded blake2b-256 hash of the off-chain JSON-LD document>",
    "uri": [
      "<first part of the URI, at most 64 bytes>",
      "<next part, if the URI is longer than 64 bytes>"
    ]
  }
}
```

- `@type` discriminates update anchors from other documents published under label `1694`, allowing indexers to detect updates without fetching and parsing every payload.
- `txHash` and `index` identify the original governance action, allowing indexers to find updates by action directly from on-chain data. They MUST identify the same action as `body.governanceActionId` in the off-chain document. Only `governanceActionId` is signed by the authors, and anyone can anchor an existing document again, so a mismatch means the document has been attached to an action its authors did not name.
- `dataHash` is the blake2b-256 hash of the raw bytes of the off-chain `GovernanceActionUpdate` document, computed as in CIP-0100.
- `uri` points to the off-chain document. Proposers SHOULD host the payload on content-addressed or decentralized storage (e.g. IPFS, Arweave) to prevent link rot, since on-chain discoverability is only as durable as the hosted content.

### Indexing, verification, and display

To process the append-only log, tooling (indexers and explorers) SHOULD adhere to the following workflow:

1. **Detection:** filter the chain for transactions containing label `1694` metadata with `@type` equal to `GovernanceActionUpdateAnchor`.
2. **URI reassembly and fetching:** concatenate the `uri` array to reconstruct the full URI and fetch the off-chain payload. Indexers SHOULD apply their own resource policies (fetch timeouts, response size limits, retry budgets) appropriate to their infrastructure; specific limits are an implementation concern, not part of this standard. Indexers SHOULD always provide access to the original document regardless of such policies.
3. **Hash verification:** hash the fetched document with blake2b-256 and compare against `dataHash`. On mismatch, the document MUST NOT be presented as a verified update; following CIP-0100 best practice, tooling SHOULD either display it with a prominent integrity warning or bar access to the content, making the mismatch obvious to the user in both cases.
4. **Action match:** decode `body.governanceActionId` and compare it with the anchor's `txHash` and `index`. On mismatch, the document MUST NOT be presented as a verified update to either action; tooling SHOULD surface it with a prominent warning.
5. **Witness validation:** resolve the original governance action, fetch its anchored metadata, verify that metadata against the on-chain anchor hash, establish the original author keys, and validate the update's witnesses as described in [Authorship and witnesses](#authorship-and-witnesses), labelling the result (author-complete, partial, deposit-account, authors unknown, or unverified).
6. **Duplicates:** several anchors with the same `dataHash` for the same action are one update, positioned by the earliest of them in chain order. Re-anchoring a document is not a sequence conflict.
7. **Ordering:** order updates for a given action by `sequenceNumber`. Where chain order is needed to resolve ambiguity, use the canonical transaction order: ascending absolute slot, then the order of transactions within the block. If multiple valid updates share the same `sequenceNumber`, tooling SHOULD display all of them, flag the conflict, and use chain order as the default presentation order, rather than silently discarding any of them.
8. **Late updates:** updates published after the original governance action has reached a terminal state (ratified, enacted, expired, or dropped) remain meaningful — for example, a `Withdrawal` or `Commitment` aimed at administrators of an already-ratified action. Tooling SHOULD display them and clearly mark that they were published after the action reached its terminal state.

In all cases, the guiding display principle is inherited from CIP-0100: surface content and make deviations obvious, rather than suppress it. Hiding content based on validation outcomes risks censoring legitimate voices through indexer bugs at critical moments; a clearly-flagged warning preserves both safety and transparency.

### Authority of updates

This CIP is a metadata standard; it cannot grant updates the power to bind anyone. By default, every verified `GovernanceActionUpdate` — including an author-complete `Narrowing` or `Commitment` — is a well-structured, signed, discoverable, and cryptographically attributable statement: strictly better than an unsigned forum post or tweet conveying the same thing, but carrying no more formal weight.

Downstream interpreters (milestone reviewers, treasury administrators, the constitutional committee) MAY choose, on their own judgment, to treat author-complete `Clarification`, `Correction`, `Narrowing`, `Commitment`, and `Withdrawal` updates as authoritative refinements of the proposals they reference — reading the original proposal *together with* such updates. They are **expected** to do so only once an ecosystem-level acknowledgement of this standard exists, such as:

- a ratified CIP-1694 **Info Action** endorsing updates meeting this CIP's conditions as authoritative refinements of the proposals they reference; or
- recognition in the Cardano constitution or an equivalent constitutional instrument; or
- a scoped commitment by an off-chain administrator (e.g. a body disbursing a treasury withdrawal against milestones) publishing that its reviews will consult conforming updates.

Deposit-account updates do not qualify, as described in [Deposit return account fallback](#deposit-return-account-fallback).

Until one of these holds, tooling SHOULD label qualifying updates as "author-endorsed — not yet ratified as binding" or similar, rather than presenting them as binding without qualification.

No mechanical rule can prevent a bad-faith update — for example, a last-minute `Clarification` published just before a voting deadline. The defense is the same one that protects every off-chain step of governance: human interpreters apply a good-faith standard and refuse to honor abuse. The bar this standard meets is not "mechanically prevents abuse" but "no worse than the status quo of unsigned social-media statements, and meaningfully better for the cooperative case."

Updates never change ledger data or figures computed from it, such as the amounts of a treasury withdrawal or totals derived from them, and they do not alter fields of the original metadata that another standard defines as fixed.

### Versioning

This document describes version `1` of this specification. Changes to the body fields, `updateType` values, or anchoring structure will be introduced through new versions of this CIP (or successor CIPs) with an updated JSON-LD context; the enumerated `updateType` values are open for extension by future CIPs. Tooling that encounters an unrecognized `updateType` SHOULD fall back to rendering the document's prose and structural fields without privileging the unknown semantics.

## Rationale: How does this CIP achieve its goals?

- **Preserving immutability:** by publishing updates as standard transactions referencing the original action rather than attempting to alter the action or its anchored metadata, this design respects the immutability of Cardano governance actions. Editing the original CIP-0100 document in place was rejected because it changes the document's hash and breaks the on-chain anchor.
- **Why not CIP-0100 `externalUpdates`:** CIP-0100 already provides an `externalUpdates` field intended for "additional updates that aren't written yet," such as a blog or RSS feed. It is insufficient for this use case for three reasons: the linked feed is mutable and unsigned, so updates are neither hash-verified nor cryptographically attributable to the authors; the feed location must be declared in the original metadata, so it cannot be added or changed after submission; and CIP-0100 itself instructs tooling to treat such content as second-class. In practice the field has seen no adoption. This CIP instead gives each update first-class CIP-0100 treatment: its own witnesses, its own hash, and its own on-chain anchor.
- **Authentication via document witnesses, not transaction signatures:** unlike native CIP-1694 governance actions or votes, whose anchors are ledger-enforced and signed by the actor's credential, anyone can submit a transaction carrying label `1694` metadata. On-chain transaction signatures therefore prove nothing about authorship. Provenance comes exclusively from the off-chain document's `witness` signatures matching the original authors' keys, or the deposit return account's key where there are none. (An alternative — treating any transaction signed by the same keys that submitted the original action as an authentic update — was considered, but it ties provenance to transaction-level keys rather than the metadata-level author set, breaks for actions submitted on the authors' behalf by a third party, and provides no path for the partial/complete author distinction.)
- **Tiered authorship instead of all-or-nothing:** requiring all original authors to sign every update would make routine informational updates impractical for multi-author proposals, while letting any single author speak for the whole set would be dangerous for updates that refine the proposal. The author-complete distinction serves both needs: low friction for information, a deliberately strict bar for authority.
- **Why a typed update taxonomy:** a general `Update` and a scope-`Narrowing` have fundamentally different implications for a voter or a milestone reviewer. Making the type explicit and machine-readable lets tooling present updates with the right weight and lets downstream interpreters define policies over types, instead of inferring intent from prose.
- **Why "no widening" is a spec-level rule rather than a social norm:** a governance action is approved on the basis of its text at submission time. Voters cannot reasonably be expected to re-evaluate a proposal every time an update appears; allowing scope expansion after voting begins breaks the assumption that a "yes" vote is consent to a specific thing. Making this a MUST NOT lets tooling refuse to present a widening update as authoritative rather than silently propagating it.
- **Reusing metadatum label `1694`:** an earlier draft of this proposal requested a dedicated label (`1695`) for efficient filtering. Review feedback pointed out that CIP-0100 reserves `1694` explicitly for *all* governance-related metadata and that documents are self-describing. This revision follows that convention; the `@type` discriminator in the on-chain anchor preserves cheap filtering without fragmenting governance metadata across labels.
- **64-byte limit compliance:** chunking the `uri` into an array ensures transactions are accepted by the ledger, which rejects metadata strings over 64 bytes, and that indexers can reliably reconstruct the pointer.
- **Always-display philosophy:** an earlier draft required indexers to discard updates that failed validation or arrived after a terminal state. This revision follows CIP-0100's guidance to surface content with prominent warnings instead, because silent suppression risks censoring legitimate voices via indexer bugs and hides impersonation attempts that are themselves relevant signal.
- **Publishing updates as new governance actions** was rejected: it is heavyweight, requires deposits and re-voting, and does not address the post-ratification case where an administrator needs a clarification of an action that has already passed.
- **Why not CIP-0100 augmentations:** CIP-0100 lets anyone extend an earlier document by pointing at it through `references`, and suggests label `1694` for publishing. That covers third-party arguments, translations, and explanations, but gives no way to tell an author's statement from anyone else's, no order between statements, and no link to the governance action itself. This CIP builds on the same label and adds those properties for updates by the authors.
- **Why not third parties:** the roles of DReps, stake pool operators, and Constitutional Committee members can be proven, as [CIP-0179][] shows, so this is a choice about meaning rather than feasibility. An author's update says what the proposal means and, when author-complete, may be read together with it. A statement by a voter says what that voter thinks of it and must never be read as part of the proposal. The update types defined here only make sense for those behind the proposal. Voters can also attach a rationale to their vote. Signed third-party statements are valuable, but belong in a separate document type with their own proof, eligibility, and display rules.
- **Why a deposit return account fallback:** of the 164 governance actions on mainnet as of 2026-11-25, 121 (74%) have valid signatures from all their listed authors. The other 43 do not: 34 list no authors, 2 list an author without a witness, 3 carry an invalid signature, and the metadata of 4 could not be verified against the anchor hash. Without a fallback, the proposers of 39 of these actions could never publish an update, and they include enacted treasury withdrawals, where later clarification matters most. All 43 have a key-based return account, so the fallback does not need script support yet. (Documents were matched to their on-chain anchor hash, and witnesses checked against the canonicalized body, for both `ed25519` and `CIP-0008`.)
- **Why the fallback is limited:** the ledger does not record who submitted an action, and does not require the return account to sign. Among the 121 signed actions, only 6 have an author key that is also the return account's key, and one return account is behind 67 of them, so the account is often an administrator rather than an author. Letting it speak next to signed authors would allow whoever arranged the submission to speak over them, so the fallback applies only where there are none. Keeping it informational preserves the reason to sign proposals. Using the keys that signed the submission transaction instead was considered, but these can belong to fee payers or custodians, and indexers do not always keep transaction witnesses.
- **Binding updates to one action:** the signed `governanceActionId` prevents a genuine update from being replayed against another action, and the on-chain `txHash` and `index` let indexers find it without fetching every document. Requiring them to match gives both. The signed form follows [CIP-0129][], as in other recent governance standards, while the raw form suits on-chain filtering.
- **Relationship to other standards:** [CIP-0204][] records holders' Yes, No, or Abstain answers under label `1695`, and [CIP-0179][] records responses to surveys under label `17`. Both collect opinions and neither lets authors update a proposal. [CIP-0211?][] fixes a category in the signed body of an action and computes totals from the ledger; updates under this CIP change neither.
- **Relationship to the CIP-0184 candidate:** this proposal was drafted concurrently with [CIP-0184?][] (Governance Proposal Feedback and Addenda), and this revision incorporates several of its ideas — the update taxonomy, the author-complete signing rule, the no-widening constraints, structured `bindingStatements`, and the explicit bootstrapping of authority — reflected in its co-authorship. This CIP deliberately retains a narrower scope: a single document type covering author-issued updates to *submitted* governance actions, with a fully-specified on-chain anchoring and indexing flow. Pre-submission draft proposals and third-party feedback documents (the CIP-0184 candidate's `DraftProposal` and `ProposalFeedback`) are complementary concerns and remain out of scope here.

## Path to Active

### Acceptance Criteria

- [ ] The JSON-LD context and schema for `GovernanceActionUpdate` are finalized, with published test vectors (canonicalized forms and blake2b-256 hashes) alongside the example documents, including negative cases.
- [ ] At least one metadata creation tool supports generating, signing, and anchoring documents conforming to this schema.
- [ ] At least one major governance interface (e.g. GovTool, Adastat, Cexplorer, 1694.io) implements detection, witness verification, and rendering of the append-only update log, including author-completeness labelling.

### Implementation Plan

- Solicit feedback from governance tooling providers on the detection and indexing flow for label `1694` update anchors.
- Provide test vectors and reference documents for wallet, CLI, and UI developers.
- Coordinate with at least one governance explorer to prototype the update-log display and use the prototype to pressure-test the schema.

## Copyright

This CIP is licensed under [CC-BY-4.0][].

[CIP-0010]: https://github.com/cardano-foundation/CIPs/blob/master/CIP-0010/README.md
[CIP-0100]: https://github.com/cardano-foundation/CIPs/blob/master/CIP-0100/README.md
[CIP-0108]: https://github.com/cardano-foundation/CIPs/blob/master/CIP-0108/README.md
[CIP-0129]: https://github.com/cardano-foundation/CIPs/blob/master/CIP-0129/README.md
[CIP-0169]: https://github.com/cardano-foundation/CIPs/blob/master/CIP-0169/README.md
[CIP-0179]: https://github.com/cardano-foundation/CIPs/blob/master/CIP-0179/README.md
[CIP-0204]: https://github.com/cardano-foundation/CIPs/blob/master/CIP-0204/README.md
[CIP-0184?]: https://github.com/cardano-foundation/CIPs/pull/1182
[CIP-0211?]: https://github.com/cardano-foundation/CIPs/pull/1322
[RFC 2119]: https://www.rfc-editor.org/rfc/rfc2119
[CC-BY-4.0]: https://creativecommons.org/licenses/by/4.0/legalcode
