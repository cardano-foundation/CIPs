---
CIP: 184
Title: Governance Proposal Feedback and Addenda
Category: Metadata
Status: Proposed
Authors:
    - Pi Lanningham <pi@sundaeswap.finance>
Implementors: []
Discussions:
    - https://github.com/cardano-foundation/CIPs/pulls/????
Created: 2026-04-24
License: CC-BY-4.0
---

## Abstract

This Cardano Improvement Proposal (CIP) extends [CIP-100][] with a
standardized format for **feedback** on in-flight governance proposals and
**binding addenda** issued by proposal authors in response. Feedback
documents allow community members, DReps, SPOs, and constitutional committee
members to register official comments, clarification requests, concerns, or
conditional voting positions against a specific governance action. Addendum
documents allow the original authors of a proposal to issue authenticated,
narrow-scope clarifications or corrections that become a binding part of the
proposal for the purposes of voting, ratification, and any off-chain
administrative interpretation — for example, a custodian disbursing a
treasury-approved grant against off-chain milestones.

## Motivation: why is this CIP necessary?

CIP-100 standardizes the *shape* of metadata attached to a governance
action but deliberately leaves the discourse around a proposal out of
scope. In practice, discourse happens — on Twitter, on Discord, in forum
threads, in Intersect working-group discussions — but none of that is signed, none of it is
reliably discoverable from the anchor, and none of it has any defined
relationship to the on-chain action it pertains to.

This is a problem for two audiences:

1. **Voters.** A DRep or delegator reading a proposal has no canonical
   place to find the structured concerns of other knowledgeable community
   members, nor a way to signal "I will vote yes *if* this one ambiguity
   is resolved." The vote is binary; the discussion that informs it is
   scattered.
2. **Administrators and auditors.** Many governance actions have
   off-chain consequences that live above the ledger: a treasury
   withdrawal whose proceeds a custodian disburses against off-chain
   milestones, a grant program administered by an Intersect working
   group, a constitutional interpretation a CC member must apply.
   Whoever plays that role has to interpret the proposal when it
   comes time to release funds or enforce scope. Ambiguities and
   typos that survive the vote become expensive at that stage, and
   authors currently have no recognized mechanism to clarify them
   after submission.

A governance action, once anchored, is immutable; the authors cannot
edit it in place. But governance is a social process, and treating the
anchor as the sole carrier of intent throws away information the network
clearly needs.

### Governance is social; this spec does not pretend otherwise

Governance on Cardano is fundamentally a social process. The
on-chain rules determine which transactions ratify, which DReps
exist, and what happens to the treasury, but the *meaning* of any
governance action — what a proposal "really" asked for, whether a
milestone has been met, whether a clarification is in good faith —
lives in the heads of the humans who have to interpret it.
Auditors, CC members, custodians, and delegators all exercise
judgment today, and nothing in this CIP changes that.

In particular: yes, an author could in theory publish a last-minute
`Clarification` addendum that reshapes the proposal right before
the voting window closes, after enough "yes" votes are banked to
pass. That would be an abuse, and this CIP does not prevent it,
because no purely mechanical rule can. The defense is the one that
already exists for every off-chain step of governance: a human
auditor or CC member refuses to honor something clearly issued in
bad faith. "Would a reasonable reviewer have accepted this as a
good-faith clarification?" is the standard.

The bar we hold this spec to is therefore not "mechanically
prevents abuse" — that bar is unreachable — but "no worse than the
status quo, meaningfully better for the cooperative cases." The
status quo is unstructured tweets and forum posts that are also not
mechanically auditable. This CIP makes the structured, cooperative
path cheaper and more discoverable without taking away the
reviewer's existing ability to throw out bad-faith content.

This CIP proposes three document types, built on CIP-100, that fill
these gaps:

- **`DraftProposal`** — a signed, unanchored pre-submission version
  of a proposal, circulated for review so authors can iterate before
  paying the cost of an on-chain action.
- **`ProposalFeedback`** — a signed, addressable comment on a
  proposal (draft or submitted). Anyone can publish one; its
  purpose is to contribute structured input into the social
  consensus around the vote.
- **`ProposalAddendum`** — a signed clarification or correction
  issued by the original authors. Its purpose is to bind downstream
  enforcement: when an auditor or administrator is interpreting the
  proposal, they are instructed to read it *together with* its
  validly-witnessed addenda.

The goals of this CIP are:

- Provide a canonical, discoverable, signed format for public commentary
  on governance proposals.
- Provide a canonical, discoverable, signed format for authors to
  clarify, narrow, or correct their own proposals post-submission.
- Define a narrow, well-specified binding semantics for addenda such
  that downstream enforcers know when and how to honor them.
- Enable tooling to surface threads of feedback, conditional votes, and
  author responses alongside the proposal they discuss.
- Be composable: the same vocabulary works whether published as a
  standalone document, embedded in vote metadata anchored from an
  on-chain ballot, or mixed into another governance metadata
  document — without forcing the publisher to commit to one of this
  CIP's `@type` values.

Explicit **non-goals**:

- This CIP does not attempt to replace forum or social-media discussion.
  Casual chatter belongs elsewhere; this format is for input the author
  wants to put their name and signature on.
- This CIP does not grant authors the ability to *expand* the scope of
  an already-submitted proposal. Addenda are strictly narrowing or
  clarifying; see [Binding Semantics](#binding-semantics).
- This CIP does not define a voting mechanism. Votes remain expressed
  via the ledger-level facilities of CIP-1694 and any successor.

## Specification

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT",
"SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this
document are to be interpreted as described in [RFC 2119][].

### Document types

This CIP defines three new JSON-LD document types, all of which are
CIP-100 governance metadata documents:

- `DraftProposal` — a not-yet-submitted proposal being circulated for
  review.
- `ProposalFeedback` — signed public comment on a proposal (draft or
  submitted).
- `ProposalAddendum` — signed author response intended to refine,
  clarify, or narrow a proposal (draft or submitted).

A document declares its type via the top-level `@type` field, and MUST
include this CIP's context (see [Context and Schema](#context-and-schema))
in its `@context` alongside the CIP-100 common context.

All three types inherit the CIP-100 top-level structure:
`hashAlgorithm`, `authors`, and `body`. Signing, canonicalization,
hashing, and witness validation are performed exactly as specified in
CIP-100; readers should refer there for the cryptographic details.

Feedback and addenda use the same `subject` reference shape and the
same threading primitives whether they target a draft or a
submitted proposal, so a single conversation can span both stages.

### `DraftProposal`

A `DraftProposal` document is a signed, unanchored version of a
proposal circulated for public review prior to any on-chain
submission. Its purpose is to host cheap, retractable iteration:
authors can gather feedback, publish revised drafts, and converge
before paying the cost of an on-chain governance action.

Its `body` MUST contain:

- `content` (REQUIRED) — the full prose of the proposed text, in the
  form the authors intend to submit.
- `proposedActionType` (REQUIRED) — a string identifying the kind
  of governance action this draft is intended to become. Drafts
  targeting an action defined by CIP-1694 SHOULD use that CIP's
  exact action name (`treasury_withdrawals_action`,
  `parameter_change_action`, `info_action`,
  `hard_fork_initiation_action`, `update_committee`,
  `new_constitution`, `no_confidence`). Drafts targeting something
  outside CIP-1694 MAY use any other label. Tooling SHOULD use
  this field to route the draft to appropriate reviewers.
- `revision` (REQUIRED) — a monotonically increasing integer starting
  at `1`. Each revision of a draft is a new document with its own
  hash; `revision` makes the sequence obvious to readers.
- `status` (REQUIRED) — one of:
  - `InProgress` — still being iterated on.
  - `ReviewReady` — the authors consider this ready for structured
    public review.
  - `Withdrawn` — the authors are abandoning this draft.
  - `Submitted` — the authors have submitted this (or a derived)
    proposal on-chain. `submittedAs` SHOULD then be populated.

The `body` MAY additionally contain:

- `supersedes` — a URI reference to the prior revision of this draft.
  Tooling SHOULD chain drafts by following `supersedes` to reconstruct
  the revision history.
- `submittedAs` — once `status = Submitted`, a reference identifying
  the final on-chain action and/or its CIP-100 metadata anchor.
  Tooling SHOULD follow this to unify draft-stage discussion with
  post-submission discussion.
- `comment`, `references`, `externalUpdates` — inherited from CIP-100.

Drafts have **no binding authority whatsoever**. They are a
coordination mechanism, not a commitment. In particular, an author
may revise a draft in any direction — widening scope, narrowing
scope, withdrawing entirely — without violating any constraint of
this spec. The constraint only attaches at submission time.

`ProposalFeedback` against a draft behaves identically to feedback
against a submitted proposal; see the next section. `ProposalAddendum`
against a draft is permitted but is never binding regardless of who
signs it, since the draft itself has no binding force. Tooling
SHOULD treat addenda against drafts primarily as a way to publish
small, individually-signed clarifications without bumping the whole
draft's `revision`; authors who want a full re-issue SHOULD instead
publish a new `DraftProposal` with an incremented `revision` and
`supersedes` populated.

### `ProposalFeedback`

A `ProposalFeedback` document is a signed public statement about a
specific governance proposal. Its `body` MUST contain:

- `subject` (REQUIRED) — an object identifying the proposal being
  commented on. See [Subject references](#subject-references).
- `feedbackType` (REQUIRED) — one of:
  - `Comment` — general commentary with no voting implication.
  - `Question` — a request for clarification; implicitly solicits an
    addendum or author response.
  - `Concern` — a raised concern that is not a hard blocker.
  - `Endorsement` — an affirmative signal of support.
  - `Objection` — a negative signal; explicit opposition.
  - `ConditionalSupport` — the author's support is contingent on the
    `conditions` array being addressed.
  - `ConditionalOpposition` — the author opposes the proposal *unless*
    the `conditions` are addressed.
- `content` (REQUIRED) — the prose of the feedback. This MAY be a
  string, or a JSON-LD language map (see CIP-100 on `@language`) for
  multilingual feedback.

The `body` MAY additionally contain:

- `conditions` — an array of condition objects, REQUIRED when
  `feedbackType` is `ConditionalSupport` or `ConditionalOpposition`.
  Each condition object has:
  - `description` (REQUIRED) — prose describing what must be clarified,
    corrected, or committed to.
  - `criticality` (REQUIRED) — one of `Blocking`, `Strong`, or `Weak`.
    `Blocking` indicates the author's vote flips entirely if unaddressed.
    `Strong` indicates a meaningful shift in confidence. `Weak`
    indicates a preference rather than a threshold.
  - `addressedBy` (OPTIONAL) — a reference to a `ProposalAddendum`
    whose publication would, in the author's view, satisfy this
    condition. May be omitted if the condition is open-ended.
- `inReplyTo` — an array of URIs pointing at parent documents
  (`ProposalFeedback` or `ProposalAddendum`) that this feedback is
  replying to. A single reply MAY target multiple parents so that
  one response can acknowledge several related comments or
  addenda. Tooling SHOULD use this to reconstruct threaded
  discussion.
- `votingIntent` — an object describing the author's intended vote:
  - `role` — one of `DRep`, `SPO`, `ConstitutionalCommittee`,
    `Delegator`, or `Other`.
  - `identifier` — a role-specific identifier (e.g. a `drep1…`
    bech32, a pool id, a CC member hash). OPTIONAL; tooling SHOULD
    treat a missing identifier as a claim the witness alone cannot
    prove.
  - `stance` — one of `Yes`, `No`, `Abstain`, `Undecided`.
  - Tooling MUST NOT treat `votingIntent` as the actual vote; the
    on-chain ballot is authoritative. The field exists to inform
    discussion, not to record consensus.

`ProposalFeedback` documents are **never** binding. Their value is
social and informational: they give voters structured inputs and give
authors specific things to respond to.

### `ProposalAddendum`

A `ProposalAddendum` document is a signed clarification, correction, or
narrowing of a previously-submitted governance proposal. Its `body`
MUST contain:

- `subject` (REQUIRED) — an object identifying the proposal being
  amended. See [Subject references](#subject-references).
- `addendumType` (REQUIRED) — one of:
  - `Clarification` — disambiguates language in the original without
    changing its meaning. Appropriate when two readings are both
    defensible and the author specifies which was intended.
  - `Correction` — fixes a clear typographical or factual error whose
    correction does not change the proposal's intent. E.g. a
    transposed digit in a reference, a misspelled name.
  - `Narrowing` — explicitly restricts the scope of the proposal.
    E.g. lowering a treasury withdrawal amount, tightening milestone
    acceptance criteria, removing an optional deliverable. MUST NOT
    widen scope (see [Binding Semantics](#binding-semantics)).
  - `Commitment` — binds the author(s) to a specific course of action
    that was left implicit or discretionary in the original proposal.
    E.g. "milestone 2 will be evaluated against criteria X, Y, Z."
  - `Withdrawal` — the authors formally disavow the proposal. A
    ratified on-chain action cannot itself be undone — a
    `treasury_withdrawals_action` that passes the threshold will
    disburse regardless — but a `Withdrawal` addendum gives
    downstream interpreters a binding instruction about the
    authors' current position. In particular:
    - An administrator or custodian holding disbursed funds SHOULD
      treat a binding `Withdrawal` addendum as an instruction to
      return those funds to the treasury rather than continue the
      program.
    - The constitutional committee MAY treat a binding `Withdrawal`
      addendum as grounds to vote the action unconstitutional, if
      the proposal's authors themselves disavowing it satisfies
      the relevant constitutional test.
    - Before voting closes, a `Withdrawal` addendum is additionally
      a strong signal to delegators and DReps to reconsider their
      vote.
- `content` (REQUIRED) — the prose of the addendum.

The `body` MAY additionally contain:

- `bindingStatements` — an array of structured statements that make
  the addendum's effect machine-actionable for auditors. Each entry:
  - `field` (REQUIRED) — a human-readable locator for the aspect of
    the proposal being amended (e.g. `"milestones[2].acceptance"`,
    `"withdrawal.amount"`, `"timeline"`).
  - `originalText` (OPTIONAL) — the text from the original proposal
    being clarified or corrected, quoted verbatim.
  - `revisedText` (REQUIRED) — the binding replacement or refinement.
  - `rationale` (OPTIONAL) — a brief explanation justifying why this
    is an addendum rather than a new proposal.
- `addresses` — an array of references to `ProposalFeedback` documents
  this addendum responds to. Each entry:
  - `uri` (REQUIRED) — the feedback URI.
  - `disposition` (REQUIRED) — one of `Accepted`, `PartiallyAccepted`,
    `Rejected`, `Noted`.
- `inReplyTo` — an array of URIs pointing at parent documents this
  addendum is replying to, with the same semantics as the
  `ProposalFeedback` field of the same name. Distinct from
  `addresses`: `inReplyTo` is a threading primitive for discussion
  reconstruction, whereas `addresses` records a structured
  disposition for each piece of feedback.
- `supersedes` — an array of URIs of prior addenda this addendum
  replaces. A later addendum MUST NOT undo a narrowing from a prior
  addendum (see [Binding Semantics](#binding-semantics)).

### Subject references

Both `ProposalFeedback` and `ProposalAddendum` point to their target
proposal via a `subject` object. This is a mild extension of the
CIP-100 reference shape, adding a cryptographic integrity hint:

- `@type` (REQUIRED) — one of:
  - `GovernanceMetadata` — the subject is a CIP-100 metadata document
    available at `uri`.
  - `GovernanceAction` — the subject is an on-chain governance
    action; `actionId` identifies it.
  - `DraftProposal` — the subject is a `DraftProposal` document
    available at `uri`.
- `uri` (REQUIRED for `GovernanceMetadata` and `DraftProposal`) — a
  resolvable URI for the referenced document.
- `hash` (RECOMMENDED) — the expected blake2b-256 hash of the
  canonicalized metadata at `uri`. If `hash` is present and does
  not match the hash of the resolved subject, the addendum MUST
  NOT be treated as binding (see
  [Binding Semantics](#binding-semantics)). Tooling SHOULD still
  render the addendum, but SHOULD prominently flag the hash
  mismatch to the user — it usually means the addendum was
  authored against a different version of the proposal than the
  one that was actually anchored.
- `actionId` (REQUIRED for `GovernanceAction`) — the on-chain
  identifier of the governance action (e.g. the transaction id and
  index from CIP-1694).
- `label` (RECOMMENDED) — a human-readable display name.

### Binding Semantics

An addendum is **binding** (subject to the ratification clause in
[Bootstrapping binding authority](#bootstrapping-binding-authority))
iff all of the following hold:

1. The document is a well-formed `ProposalAddendum` per this spec.
2. The `subject` resolves. Specifically: the document at `subject.uri`
   (or the action at `subject.actionId`) exists, and if `subject.hash`
   is supplied, it matches the resolved document's actual hash. A
   hash mismatch makes the addendum non-binding, even though the
   document remains valid and renderable per
   [Subject references](#subject-references). Addenda against
   `DraftProposal` subjects are never binding regardless of who
   signs them; drafts have no binding force to inherit.
3. **The addendum is signed by the same author set as the original,
   using whichever witness scheme the original used.** Let `O` be
   the set of distinct witness public keys from the original
   proposal's `authors` array. The addendum's `authors` array MUST
   include a valid witness for every key in `O`, where "valid" is
   interpreted according to the witness `@context` in use — the
   same validation any CIP-100 consumer would already perform on
   the original. A majority, plurality, or single signer out of
   `O` is not sufficient; the binding rule is deliberately strict.

   No new signing mechanism, witness format, or
   transaction-level-witness substitute is defined here. Authors
   prove endorsement of an addendum the exact same way they proved
   endorsement of the original — whether via the CIP-100 common
   witness scheme or via a later witness `@context` built on
   CIP-8 / CIP-30 `signData` / CIP-95.

   An addendum that fails this condition — for example, one signed
   by three of four original co-authors because the fourth is
   unreachable — is still a valid, publishable, discoverable
   document. It simply is not *binding*. Downstream reviewers MAY
   still weigh it as strong evidence of author intent; see
   [Governance is social](#governance-is-social-this-spec-does-not-pretend-otherwise).

   Tooling MUST make the authorship status of an addendum visible
   to the user: how many of the original authors signed, and
   whether the addendum therefore qualifies as binding under this
   rule.
4. The `addendumType` and `bindingStatements` do not attempt to widen
   the proposal's scope. Specifically:
   - An addendum against a treasury withdrawal MUST NOT increase the
     withdrawn amount or the set of recipients.
   - Where the proposal defines acceptance criteria for an off-chain
     administrative process (e.g. milestone criteria for a custodian
     disbursing funds), an addendum MAY add or tighten those
     criteria but MUST NOT remove or relax them.
   - An addendum MUST NOT extend deadlines or windows beyond those
     declared in the original proposal.
   - An addendum MUST NOT supersede a prior binding addendum in a
     way that relaxes a narrowing already committed to.
   - A binding addendum may be superseded *only* by another binding
     addendum. A later, non-binding addendum that names a prior
     binding addendum in its `supersedes` field MUST NOT be treated
     as having displaced it; the prior binding addendum remains in
     force until a binding successor exists. This prevents an
     incomplete signing quorum from silently retiring a constraint
     that was previously committed to under a complete one.

   The `Withdrawal` addendum type is exempt from these constraints,
   since disavowing the proposal entirely is by definition not a
   widening.

A non-binding `ProposalAddendum` (one that fails any of the above) is
still a valid document; tooling SHOULD display it, but SHOULD
prominently flag it as non-binding and explain why.

Downstream enforcers — milestone auditors, treasury custodians,
dispute resolvers — SHOULD treat the union of the original proposal
and its binding addenda as the authoritative specification of what
the action requires. In particular, where the original is ambiguous
and a binding `Clarification` addendum resolves the ambiguity, the
clarification governs.

### Bootstrapping binding authority

The preceding section describes when an addendum is *well-formed
enough* to be binding. That is a necessary condition, not a
sufficient one. This CIP is a metadata extension; no CIP can grant
itself the power to bind downstream enforcers. The word "binding"
throughout this document is conditional on the ecosystem having
separately acknowledged that authority.

Until such acknowledgement exists, a `ProposalAddendum` is, for all
governance-effect purposes, a well-structured signed comment. It is
discoverable, interlinked, referenceable, and cryptographically
attributable to the original authors — which is strictly better than
an unsigned forum post or tweet clarifying the same thing — but it
carries no more formal weight than those alternatives. Reviewers,
auditors, and CC members MAY choose to honor such clarifications on
their own judgement, exactly as they may choose to honor a signed
forum post today.

An addendum becomes formally binding — such that downstream
enforcers are **expected** to honor it, rather than merely
*permitted* to — only once at least one of the following has
occurred:

- An **Info Action** is ratified under CIP-1694 acknowledging this
  CIP and endorsing `ProposalAddendum` documents meeting the
  conditions in [Binding Semantics](#binding-semantics) as
  authoritative refinements of the proposals they reference.
- The Cardano constitution (or a successor constitutional
  instrument) is amended to recognize the same.
- An equivalent ecosystem-level endorsement is made by a body
  whose scope of authority plausibly covers the enforcer in
  question (e.g. an Intersect working group publishing that their
  milestone reviews will consult binding addenda).

Absent any of these, tooling that presents an addendum as
"binding" is overstating the current state of the art. Tooling
SHOULD label such documents as "authored response — not yet
ratified" or similar until one of the bootstrap conditions above
holds.

### Composing with other governance documents

The vocabulary this CIP introduces — `subject`, `content`,
`conditions`, `inReplyTo`, `votingIntent`, `addresses`,
`bindingStatements` — is a JSON-LD vocabulary, not a closed
schema. Any CIP-100-compliant document that imports this CIP's
`@context` MAY use any subset of these fields, regardless of
whether the document declares one of this CIP's `@type` values.

This matters most for **vote metadata.** Under CIP-1694, a vote
itself can carry an anchor pointing to a CIP-100 document
explaining the voter's reasoning. A DRep voting `No` who wants
to communicate "I would switch to `Yes` if these questions were
answered" can:

- Cast the on-chain vote as `No`.
- Anchor that vote to a CIP-100 metadata document whose `body`
  uses this CIP's `content` and `conditions` fields alongside
  whatever vote-metadata vocabulary is otherwise conventional
  for that voter role.

Such a document does not need `@type: ProposalFeedback`. The
anchor relationship makes the document's subject unambiguous (it
is the metadata for *this vote on this action*), and the actual
ballot is the on-chain vote, not anything in the metadata.
`subject`, `feedbackType`, and `votingIntent` are redundant in
this mode and MAY be omitted; tooling SHOULD recognize this
CIP's vocabulary in the document regardless of `@type`.

The same composition pattern applies to SPO vote metadata, CC
member rationale on votes, DRep registration rationale, and any
future governance metadata document that attaches a CIP-100
anchor. A publisher picks the fields they need, includes this
CIP's `@context`, and is done — no choice of "document type" is
forced on them.

The JSON Schema in this CIP validates standalone `DraftProposal`,
`ProposalFeedback`, and `ProposalAddendum` documents only. It is
not the right validator for embedded use; for that, validate
against whatever schema is canonical for the document doing the
embedding, augmented as needed with term definitions from this
CIP's `@context`.

The enumerated values defined in this CIP — `feedbackType`,
`addendumType`, condition `criticality`, addendum `disposition`,
draft `status`, and `votingIntent` `role` / `stance` — are open
for extension. A future CIP MAY introduce additional values via
a new `@context`. Tooling that encounters an unrecognized value
SHOULD fall back to rendering the document's prose and structural
fields without privileging the unknown semantics, in keeping with
CIP-100's general extensibility guidance.

### Discovery and hosting

The defining feature of these documents is not *where* they live
but that they can be **discovered** and **verified** without
trusting any single host. CIP-1694 already gives Cardano a
primitive for this — the on-chain anchor — and CIP-100 gives the
convention for using it. Feedback and addenda follow the same
pattern, and authors are strongly encouraged to anchor them on
chain rather than rely on external hosting alone.

Concretely: the recommended publication path is to attach the
document, or a `uri + hash` reference to it, to a transaction
using the [CIP-10][] metadatum label `1694` reserved by CIP-100.
This gives a document two properties Cardano is good at delivering
and a casual web host is not:

- **Discoverability.** Anyone indexing Cardano transactions can
  find every document anchored under label 1694, regardless of
  where the underlying content actually lives. Indexers and
  governance tools can group, filter, and thread feedback by
  `subject` without having to crawl arbitrary external URLs or
  scrape walled-garden forums.
- **Censorship-resistance.** Once anchored, the document — or
  its hash — cannot be silently removed, retracted, or rewritten.
  An external host can drop the content, but the on-chain hash
  will continue to attest that something with that hash existed
  and is now missing.

The document itself does not need to live on chain in every case.
Short documents (most feedback, most addenda) MAY be inlined into
the transaction metadata under label 1694. Longer documents — a
draft proposal with extensive prose, for example — MAY be hosted
on IPFS, Arweave, or any other store, and referenced from a
label-1694 transaction by `uri + hash`. The hash protects
integrity; the on-chain reference creates discoverability. The
choice between inlining and referencing is a cost-and-size
trade-off, not a semantic one.

For binding addenda specifically:

- A binding `ProposalAddendum` SHOULD be anchored on chain, by
  whichever of the two patterns above fits its size. The anchor
  gives the addendum a ledger-visible timestamp auditors can use
  to establish ordering relative to the voting window or the
  payout schedule it modifies.
- On-chain anchoring is **not** a substitute for the authorship
  rule in [Binding Semantics](#binding-semantics). Authorship is
  proven by the witness array on the document itself, per the
  witness `@context` the original proposal used.

Tooling authors SHOULD index documents anchored under label 1694,
group them by `subject`, and present them alongside the proposal
they reference — threaded by `inReplyTo` and grouped by
`addresses` where author responses are present. The minimum
useful integration is a "governance metadata" tab that lists
label-1694 metadata as raw JSON; richer integrations add
field-aware rendering for the vocabulary defined here.

[CIP-10]: ../CIP-0010/README.md

### Context and Schema

This CIP provides the following shared assets:

- [JSON-LD Context](./cip-governance-feedback.jsonld)
- [JSON Schema](./cip-governance-feedback.schema.json)
- [Feedback example](./example.feedback.json)
- [Addendum example](./example.addendum.json)

Documents using this extension MUST include both the CIP-100 common
context and this context in their `@context` array.

### Signing and canonicalization

Signing, canonicalization, and hash computation are unchanged from
CIP-100. Witnesses sign the blake2b-256 hash of the canonicalized
`body` node. Readers are referred to CIP-100 §Hashing and Signatures
for the procedure.

### Best practices

- Tooling authors SHOULD render the full thread of feedback attached
  to a proposal, not just the most recent or most-endorsed items.
- Tooling authors SHOULD display binding addenda inline with the
  original proposal text, highlighting which sections are affected
  via `bindingStatements.field`.
- Tooling authors SHOULD validate witnesses against the original
  proposal before labelling an addendum as binding, and SHOULD
  surface the author count explicitly (e.g. "4 of 4 original
  authors signed" vs. "3 of 4").
- Authors SHOULD prefer narrowly-scoped `Clarification` or
  `Correction` addenda over omnibus addenda; smaller, well-targeted
  changes are easier for voters and auditors to evaluate.
- Authors SHOULD NOT attempt to use addenda to respond to feedback
  that would require widening the proposal; the correct response
  there is a new proposal.
- Voters SHOULD consider outstanding `ConditionalSupport` and
  `ConditionalOpposition` feedback when deciding whether to delay a
  vote to give the author time to respond.

## Rationale: how does this CIP achieve its goals?

### Why three document types, not one?

Drafts, feedback, and addenda have fundamentally different trust
semantics. A draft is the author's working text — fully revisable,
non-binding, useful for pre-submission review. Feedback is anyone's
signed opinion; its only binding power is social. Addenda are the
author's binding refinement; they change what downstream enforcers
consider "the proposal." Conflating these into a single document
type would force every tool to decide, per document, which
semantics apply — a recipe for bugs. Distinct `@type` values make
the trust boundary explicit and validatable.

### Why is "no widening" a spec-level rule rather than a social norm?

A governance action is approved on the basis of its text at
submission time. Voters — especially ada delegators relying on a
DRep's published stance — cannot reasonably be expected to
re-evaluate a proposal every time an addendum appears. Allowing
authors to expand scope after the vote has begun breaks the
assumption that a "yes" vote is consent to a specific thing. Making
this a MUST NOT at the spec layer lets tooling refuse to honor a
widening addendum rather than silently propagating it, which is the
behavior voters and auditors need.

### Why sign rather than just federate trust to the forum?

Forum identity is weak; pseudonymous actors can be mistaken for
each other, accounts can be taken over, and content can be silently
edited. For feedback that a voter wants to rely on — "DRep X plans
to vote yes if Y is clarified" — the witness scheme inherited from
CIP-100 is the minimum viable authentication, and it is the only
form an automated indexer or auditor can verify without trusting
an external identity service.

### Why an `actionId` reference in addition to a URI?

The CIP-100 `GovernanceMetadata` reference points at a metadata
document, which is one step removed from the action. For a binding
addendum, the auditor wants to verify the addendum is against the
action that actually passed on-chain, not against a metadata
document that may or may not have been the one anchored. The
`GovernanceAction` subject type lets the addendum cite the on-chain
identity directly.

### Alternatives considered

- **Extend the original CIP-100 document in place.** Rejected:
  changing the original document changes its hash, which breaks the
  on-chain anchor. Addenda must be separate documents that reference
  the original.
- **Publish addenda as new governance actions.** Rejected: this is
  heavyweight, requires re-voting, and does not solve the auditor
  use case (where the original action has already passed and payouts
  are pending).
- **Treat all post-submission statements as non-binding.** Rejected:
  this matches current practice and the problem it creates is
  exactly the motivation for this CIP. The binding mechanism is the
  point.
- **A free-form `amendment` field under CIP-100.** Rejected: the
  trust semantics of addenda are distinct enough from ordinary
  metadata that a dedicated type with defined binding rules is
  warranted.

## Path to Active

### Acceptance Criteria — Phase 1 (spec adoption)

- At least 1 month of feedback solicited, with any broadly-supported
  changes incorporated.
- At least 2 client libraries implement parsing and witness
  validation for all three document types (`DraftProposal`,
  `ProposalFeedback`, `ProposalAddendum`).
- At least 1 governance tool (DRep dashboard, governance explorer,
  Intersect tooling) displays feedback and addenda alongside the
  proposals they reference.
- Test vectors (canonicalized forms and blake2b-256 hashes) are
  published alongside this CIP's example documents.

At Phase 1, the spec is adopted as a standard *format*. Documents
following it are well-formed, discoverable, and attributable, but
addenda carry only the social weight the reviewer chooses to give
them — see [Bootstrapping binding authority](#bootstrapping-binding-authority).

### Acceptance Criteria — Phase 2 (binding authority)

- An **Info Action** under CIP-1694 is proposed, circulated, and
  ratified by DReps, acknowledging this CIP and endorsing addenda
  that satisfy [Binding Semantics](#binding-semantics) as
  authoritative refinements of the proposals they reference. This
  is the explicit on-chain moment at which the ecosystem opts in
  to the "binding" half of this CIP. *Or*
- An amendment to the Cardano constitution (or equivalent
  constitutional instrument) incorporates the same authority. *Or*
- An off-chain administrator overseeing a governance-funded
  program (e.g. an Intersect working group disbursing a treasury
  withdrawal against milestones) publishes their procedure for
  consulting binding addenda and commits to applying it for
  proposals within their scope. This gives partial, scoped
  authority even without full ecosystem ratification.

Only after at least one of these has occurred should tooling label
conforming addenda as "binding" without qualification.

### Implementation Plan

- Solicit feedback from DRep tooling authors, Intersect working
  groups, and CIP-100 implementers.
- Produce reference parsers in Rust and TypeScript alongside the
  CIP-100 reference implementations.
- Coordinate with at least one governance-explorer project to
  prototype the threaded display described in the best practices
  section, and use that prototype to pressure-test the schema.
- Once Phase 1 is complete, draft the Phase 2 Info Action text as a
  companion document, so DReps can evaluate the authority grant
  against a spec that has already demonstrated itself in
  non-binding use.

## Copyright

This CIP is licensed under [CC-BY-4.0][].

[CIP-100]: ../CIP-0100/README.md
[RFC 2119]: https://www.rfc-editor.org/rfc/rfc2119
[CC-BY-4.0]: https://creativecommons.org/licenses/by/4.0/legalcode
