---
CIP: "?"
Title: Categories for Governance Actions
Category: Metadata
Status: Proposed
Authors:
  - Tommy Kammerer <31965230+katomm@users.noreply.github.com>
Implementors: []
Discussions:
  - Original PR: (not opened yet)
Created: 2026-11-13
License: CC-BY-4.0
---

## Abstract

Governance actions often belong together: an Info Action approves a budget category or a grant round, and later Treasury Withdrawals pay it out. Nothing on chain says which actions belong together, so every tool that groups them or shows how much of an approved allocation has been withdrawn curates that grouping by hand.

This CIP adds one optional field, `category`, to the `body` of [CIP-0108](../CIP-0108/README.md) governance action metadata. An Info Action uses it to define a category. A Treasury Withdrawal or a later Info Action uses it to point at the defining Info Action by its governance action ID. A definition can carry a ceiling, a period and the reward accounts that may receive its funds, so tools can check a withdrawal's claim against its on-chain recipients and compute withdrawn totals.

## Motivation: Why is this CIP necessary?

Treasury spending is often approved first and withdrawn later: an annual budget split into categories, a grant program approved per round, a multi-year commitment paid in tranches. Processes call these groups categories, domains, tracks, funds or rounds. This CIP calls all of them categories.

For each one, DReps, delegators and analysts want to see what was approved, which later actions belong to it, how much has been withdrawn against it, and where the funds went. The approval and the recipients are on chain today. The membership is not, so tools fall back to reading titles or to lists in their own databases. Two tools will disagree, and neither can be checked by a third.

One current example is Intersect's proposal for a more strategic 2027 budget approach ([discussion](https://dreptalk.com/t/a-more-strategic-2027-cardano-budget-approach-released-for-d-jgsvng)), which organizes funding by domain. Each domain could be defined as a category under this CIP. The field does not depend on that proposal or any other process. It works for processes that exist today, ones that are only proposed, and a single proposer who wants to tie a multi-step project to its first approval.

## Specification

The key words MUST, MUST NOT, SHOULD, SHOULD NOT, RECOMMENDED and MAY are to be interpreted as described in RFC 2119.

### Terms

- **Category**: a named group of governance actions that an Info Action defines. It may describe an allocation of treasury funds that later Treasury Withdrawals spend against.
- **Definition action**: an Info Action whose metadata carries a valid `category` with `kind` `definition`. It defines exactly one category.
- **Category ID**: the governance action ID of the definition action. A category has no other identity.
- **Member action**: a Treasury Withdrawal or Info Action whose metadata carries a valid `category` with `kind` `member`.
- **Governance action ID**: always written in [CIP-0129](../CIP-0129/README.md) bech32 form (`gov_action1…`), lower case. A value that is not lower case or does not decode with a valid checksum is invalid.
- **Reward account**: a [CIP-0019](../CIP-0019/README.md) reward address, written in lower-case bech32 (`stake1…`, `stake_test1…`). A value that is not lower case or does not decode with a valid checksum to a reward address is invalid.
- **Enactment epoch**: the epoch in which the ledger enacts a Treasury Withdrawal, one epoch after ratification.

### Placement and JSON-LD context

`category` is a property of the CIP-0108 `body` object, which keeps it inside what [CIP-0100](../CIP-0100/README.md) author witnesses sign.

The CIP-0108 context sets no `@vocab`, so an unmapped property is dropped from the canonical form or rejected in safe mode. Therefore:

1. Writers MUST add the term definition below to the existing `body.@context`. They MUST keep `body`'s `@id` and every term already mapped there, including other extensions such as [CIP-0169](../CIP-0169/README.md) `onChain` and [CIP-0179](../CIP-0179/README.md) `cip179`. Replacing `body` wholesale produces an invalid context.
2. Readers MUST treat `category` as absent unless the context maps `category` and every sub-property present in it, including `period.startEpoch` and `period.endEpoch`, to this CIP's namespace. The `CIPCAT` prefix MUST be defined at the top level of the context. This affects only `category`. The rest of the document is shown as usual.

Term definition to insert into `body.@context`:

```json
"category": {
  "@id": "CIPCAT:category",
  "@context": {
    "@language": null,
    "specVersion": "CIPCAT:specVersion",
    "kind": "CIPCAT:kind",
    "label": { "@id": "CIPCAT:label", "@language": "en-us" },
    "budget": "CIPCAT:budget",
    "period": {
      "@id": "CIPCAT:period",
      "@context": { "startEpoch": "CIPCAT:startEpoch", "endEpoch": "CIPCAT:endEpoch" }
    },
    "recipients": { "@id": "CIPCAT:recipients", "@container": "@set" },
    "process": "CIPCAT:process",
    "categoryId": "CIPCAT:categoryId"
  }
}
```

plus the prefix at the top level of the context:

```json
"CIPCAT": "<namespace IRI, see Namespace>"
```

`@language: null` keeps identifiers, amounts and addresses as plain literals, independent of the document's language.

### Namespace

The namespace IRI goes into every canonical hash and can never change for documents already anchored. It is fixed once, before the first mainnet use: the URL of this CIP's pull request with a trailing `#`, for example `https://github.com/cardano-foundation/CIPs/pull/NNNN#`. The CIP keeps that IRI after it is numbered.

### Definition

Allowed only on Info Actions.

| Property | Required | Type and form | Meaning |
| --- | --- | --- | --- |
| `specVersion` | yes | JSON integer `1` | Version of this CIP. |
| `kind` | yes | `"definition"` | |
| `label` | yes | string, 1 to 80 Unicode code points | Human-readable name of the category. |
| `budget` | no | string matching `^(0\|[1-9][0-9]*)$` | The category's ceiling in lovelace. A JSON number is invalid, because it loses precision above 2^53. |
| `period` | no | object with exactly the two properties `startEpoch` and `endEpoch`, non-negative JSON integers, `startEpoch <= endEpoch` | Inclusive range of enactment epochs in which withdrawals count against this category. |
| `recipients` | no | non-empty array of distinct reward accounts | Reward accounts that may receive this category's withdrawals. |
| `process` | no | governance action ID | An Info Action that set up a wider process this category belongs to, for example an annual budget. Tools MAY show it as a link. Version 1 defines no rule that resolves it. |

The smallest valid definition carries only `specVersion`, `kind` and `label`. It groups actions but has no recipient check, so its checked total stays 0 and every enacted member withdrawal appears in the unchecked figure.

The prose in `abstract`, `motivation` and `rationale` stays authoritative for what the category covers and who runs it. Tools compute with the structured fields and SHOULD link the prose next to every computed figure.

A category changes only through a new definition action with a new Category ID. Version 1 has no link between an old and a new definition.

### Member

Allowed on Treasury Withdrawals and Info Actions.

| Property | Required | Type and form | Meaning |
| --- | --- | --- | --- |
| `specVersion` | yes | JSON integer `1` | Version of this CIP. |
| `kind` | yes | `"member"` | |
| `categoryId` | yes | governance action ID | Category ID of the definition action. |

A member action names exactly one category. A proposal that spans categories is split into one action per category. An Info Action member, such as a report or a scope change, is listed with the category and never adds to any total.

### Validity

A `category` object is valid only when all of the following hold. Otherwise readers MUST treat it as absent and MUST NOT repair or coerce values. Readers check validity on the JSON document as anchored, before JSON-LD expansion, because expansion hides differences such as an empty array, a single string in place of an array, or duplicate entries.

- The context maps it as described above.
- `specVersion` is the JSON integer `1`. Readers that implement version 1 ignore any other value.
- `kind` is `definition` on an Info Action, or `member` on a Treasury Withdrawal or Info Action. Any other combination, including any `category` on another action type, is invalid.
- Every required property is present, and every present property has the type and form given in its table.
- Properties not defined for its `kind` are absent.

### How tools read it

1. **Approval stays a social decision.** Info Actions are never enacted, so the ledger never says whether a category was approved. Tools MUST show the definition action's tally and status next to the category and MUST NOT present a category as approved by protocol. A tool MAY apply a threshold named by the process the category belongs to, and MUST say which one.
2. **Resolving a category.** Tools read `category` only from a document whose bytes match the action's own on-chain anchor hash, for definition and member actions alike. A member action resolves when `categoryId` is the ID of a definition action whose anchor document has been verified at least once. Tools MAY keep verified bytes, and a category stays as read when its anchor URL later stops serving. A member action that does not resolve is shown as unresolved. Tools MUST NOT guess the category from titles.
3. **Recipient check.** When the definition lists `recipients`, a tool decodes each listed account and each reward account in the Treasury Withdrawal's ledger body to its header byte and 28-byte credential, and compares those. A listed account on another network never matches. The result is **matched** when every withdrawal recipient is listed, and **mismatch** otherwise. Without `recipients`, the withdrawal is **unchecked**.
4. **Counting.** A category's checked total is the sum of the ledger amounts of enacted, **matched** member Treasury Withdrawals, attributed by enactment epoch and limited to `period` when given. Amounts always come from the ledger, never from metadata. Tools SHOULD show unchecked and mismatched withdrawals as separate figures and MUST NOT add them to the total. Members not yet enacted, or enacted outside `period`, are listed with the category and appear in no figure.

## Rationale: How does this CIP achieve its goals?

**The Info Action is the identity.** A string such as `"core-infra"` would need a registry and would collide across years and processes. The governance action ID already exists, is unique, and points at the vote that approved the category.

**Optional budget fields.** Grouping is useful on its own, for example a grant round's reports. With the budget fields optional, one mechanism covers a plain group and a funded allocation.

**Only Treasury Withdrawals and Info Actions.** These are the types that approve, spend or report on treasury funds. Other types already have a ledger-recorded type and no figure to compute. A later version can open the field to them without breaking version 1 documents.

**In the action's own metadata.** A separate metadata label could be posted by anyone. In `body`, the link is part of what the proposers signed, and the anchor hash fixes it after submission.

**Recipients make the claim checkable.** Without a check, anyone could tag a withdrawal with a popular category. Withdrawals of a funded program often pay into one or a few accounts, for example Intersect's 2026 withdrawals into a single script reward account. A short list in the definition then checks each withdrawal without a second vote. Comparing decoded credentials avoids false mismatches between text forms of the same account.

**Strict validity and one text form.** Two tools that disagree about a malformed document show different totals, which is the problem this CIP addresses. Ignoring an invalid object entirely is a rule every tool applies the same way. For the same reason only lower-case bech32 is accepted, although bech32 also allows upper case, so that no reader has to choose between rejecting and normalizing. The 80 code point `label` limit keeps a name readable in one line of a list.

**No role for who runs a category.** The names for that role (steward, administrator, committee) carry positions in an ongoing debate about control of treasury funds. `recipients` covers what tools can check, and the rest belongs in the prose and `references`.

**One category per action.** Several categories on one action would count the same lovelace twice, and a per-recipient split would repeat amounts the ledger already holds.

**No supersession in version 1.** A pointer from a new definition to an old one raises questions the chain cannot answer: who may replace a category, which of two replacements wins, and whether totals carry over.

**Relation to other standards and alternatives.**

- *CIP-0100 `references`* can point at another action, but a reference has no defined meaning, so a tool cannot tell a category link from a citation.
- *CIP-0169 `onChain`* restates ledger content. A category is a claim by the proposer that the ledger does not hold.
- *CIP-0179* adds survey links to the same `body`. This CIP follows its context merge.
- *Governance Action Addendums* ([PR 1180](https://github.com/cardano-foundation/CIPs/pull/1180)) publish later updates under a separate label. A category in the anchored `body` cannot change afterwards, which keeps totals stable. Addendums could reuse this field later.
- *A free label without a definition action* would let two processes pick the same word and has nothing to check against.
- *One Info Action defining several categories* would let one tally approve all of them, so DReps could not accept one and reject another.
- *Tool-side curation* has to be repeated by every tool. It remains the fallback for actions submitted before this CIP.

## Backwards compatibility

The field is optional. Tools that do not implement this CIP can ignore it. Earlier actions carry no field and cannot be tagged retroactively.

## Path to Active

### Acceptance criteria

- [ ] At least one mainnet Info Action that defines a category with this field, and at least one mainnet Treasury Withdrawal that is a member of it.
- [ ] At least one tool that writes the field when submitting governance actions, built by people unaffiliated with the author.
- [ ] At least one tool that reads the field and shows per-category totals by the counting rule above, built by such an unaffiliated team, and agreeing with the test vectors.

### Implementation plan

No implementation exists yet. The format is put up for review first, so that tool builders, budget process teams and DReps can shape it before any document carries it.

- [ ] Open the CIP pull request and fix the namespace IRI.
- [ ] Publish test vectors with the CIP: valid documents with and without `onChain` and `cip179`, with anchor and canonical body hashes, one invalid document per validity rule, the three recipient results, and one total fixture covering every member status and the `period` bounds.
- [ ] Ask budget process teams, grant programs and tool builders to review the format.
- [ ] No tool writes the field on mainnet until the editors confirm this CIP. Testnets are fine.

## Open questions

- Is there a need for a lighter mode in which an action carries a category without a definition action?
- Should `budget` be required on definitions?
- Does the Net Change Limit belong here as an optional pointer on definitions?
- Does a later version need a link from a new definition to the one it replaces, and what decides between competing replacements?
- Should a later version open member actions to further action types?

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
