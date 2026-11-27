---
CIP: 211
Title: Categories for Governance Actions
Category: Metadata
Status: Proposed
Authors:
  - Tommy Kammerer <31965230+katomm@users.noreply.github.com>
Implementors: []
Discussions:
  - Original PR: https://github.com/cardano-foundation/CIPs/pull/1322
Created: 2026-11-13
License: CC-BY-4.0
---

## Abstract

Treasury Withdrawals often belong to a larger allocation: a budget domain that spends over a year, a grant round, or a program paid in tranches. Nothing on chain says which withdrawals belong to which allocation, so every tool that groups them or shows how much of an allocation has been withdrawn curates that grouping by hand.

This CIP adds one optional field, `category`, to the `body` of [CIP-0108](../CIP-0108/README.md) governance action metadata. An Info Action uses it to define one or more categories. A Treasury Withdrawal or a later Info Action uses it to point at one of them by the defining action's governance action ID and the category's key. A category can carry a ceiling, a period and the reward accounts that may receive its funds, so tools can check a withdrawal's claim against its on-chain recipients and compute withdrawn totals.

## Motivation: Why is this CIP necessary?

Treasury spending is increasingly organized in allocations that span several withdrawals: an annual budget split into domains, a grant program funded per round, a multi-year commitment paid in tranches. Processes call these groups categories, domains, tracks, funds or rounds. This CIP calls all of them categories.

For each one, DReps, delegators and analysts want to see what was allocated, which actions reference it, how much has been withdrawn against it, and where the funds went. Withdrawals and their recipients are on chain today. Which allocation they belong to is not, so tools fall back to reading titles or to lists in their own databases. Two tools will disagree, and neither can be checked by a third.

One current example is Intersect's proposal for a more strategic 2027 budget approach ([discussion](https://dreptalk.com/t/a-more-strategic-2027-cardano-budget-approach-released-for-d-jgsvng)), which organizes funding by domain. Each domain could be defined as a category under this CIP. The field does not depend on that proposal or any other process. It works for processes that exist today, ones that are only proposed, and a single proposer who wants to tie a multi-step project to its first approval.

## Specification

The key words MUST, MUST NOT, SHOULD, SHOULD NOT, RECOMMENDED and MAY are to be interpreted as described in RFC 2119.

### Terms

- **Category**: a named group of governance actions, defined as one entry of a definition action. It may describe an allocation of treasury funds that later Treasury Withdrawals spend against.
- **Definition action**: an Info Action whose metadata carries a valid `category` with `kind` `definition`. It defines one or more categories.
- **Category identity**: the governance action ID of the definition action together with the category's `key`. A category has no other identity. In a member, `categoryId` holds the first part and `categoryKey` the second.
- **Member action**: a Treasury Withdrawal or Info Action whose metadata carries a valid `category` with `kind` `member`.
- **Governance action ID**: always written in [CIP-0129](../CIP-0129/README.md) bech32 form (`gov_action1…`), lower case. A value that is not lower case or does not decode with a valid checksum is invalid.
- **Reward account**: a [CIP-0019](../CIP-0019/README.md) reward address, written in lower-case bech32 (`stake1…`, `stake_test1…`). A value that is not lower case or does not decode with a valid checksum to a reward address is invalid.
- **Enactment epoch**: the epoch in which the ledger enacts a Treasury Withdrawal, one epoch after ratification.

### Placement and JSON-LD context

`category` is a property of the CIP-0108 `body` object, which keeps it inside what [CIP-0100](../CIP-0100/README.md) author witnesses sign.

The CIP-0108 context sets no `@vocab`, so an unmapped property is dropped from the canonical form or rejected in safe mode. Therefore:

1. Writers MUST add the term definition below to the existing `body.@context`. They MUST keep `body`'s `@id` and every term already mapped there, including other extensions such as [CIP-0169](../CIP-0169/README.md) `onChain` and [CIP-0179](../CIP-0179/README.md) `cip179`. Replacing `body` wholesale produces an invalid context.
2. Readers MUST treat `category` as absent unless the context maps `category` and every sub-property present in it, including the properties of each `categories` entry and `period.startEpoch` and `period.endEpoch`, to this CIP's namespace. The `CIPCAT` prefix MUST be defined at the top level of the context. This affects only `category`. The rest of the document is shown as usual.

Term definition to insert into `body.@context`:

```json
"category": {
  "@id": "CIPCAT:category",
  "@context": {
    "@language": null,
    "kind": "CIPCAT:kind",
    "categories": { "@id": "CIPCAT:categories", "@container": "@set" },
    "key": "CIPCAT:key",
    "label": { "@id": "CIPCAT:label", "@language": "en-us" },
    "budget": "CIPCAT:budget",
    "period": {
      "@id": "CIPCAT:period",
      "@context": { "startEpoch": "CIPCAT:startEpoch", "endEpoch": "CIPCAT:endEpoch" }
    },
    "recipients": { "@id": "CIPCAT:recipients", "@container": "@set" },
    "process": "CIPCAT:process",
    "categoryId": "CIPCAT:categoryId",
    "categoryKey": "CIPCAT:categoryKey"
  }
}
```

plus the prefix at the top level of the context:

```json
"CIPCAT": "https://github.com/cardano-foundation/CIPs/pull/1322#"
```

`@language: null` keeps identifiers, amounts and addresses as plain literals, independent of the document's language.

### Namespace

The namespace IRI goes into every canonical hash and can never change for documents already anchored. It is fixed once, before the first mainnet use, as the URL of this CIP's pull request with a trailing `#`:

```
https://github.com/cardano-foundation/CIPs/pull/1322#
```

The CIP keeps that IRI after it is numbered.

Documents carry no version number, like the other CIP-0100 extensions. A later version of this CIP that changes what a property means defines a new term for it in this namespace, so documents already anchored keep their meaning.

### Definition

Allowed only on Info Actions.

| Property | Required | Type and form | Meaning |
| --- | --- | --- | --- |
| `kind` | yes | `"definition"` | |
| `categories` | yes | non-empty array of category entries | The categories this action defines. |
| `process` | no | governance action ID | An Info Action that set up a wider process these categories belong to, for example an annual budget. Tools MAY show it as a link. Version 1 defines no rule that resolves it. |

Each category entry:

| Property | Required | Type and form | Meaning |
| --- | --- | --- | --- |
| `key` | yes | string matching `^[a-z0-9]+(-[a-z0-9]+)*$`, 1 to 32 characters, distinct within the action | Identifies the category within the definition action. |
| `label` | yes | string, 1 to 80 Unicode code points | Human-readable name of the category. |
| `budget` | no | string matching `^(0\|[1-9][0-9]*)$` | The category's ceiling in lovelace. A JSON number is invalid, because it loses precision above 2^53. |
| `period` | no | object with exactly the two properties `startEpoch` and `endEpoch`, non-negative JSON integers, `startEpoch <= endEpoch` | Inclusive range of enactment epochs in which withdrawals count against this category. |
| `recipients` | no | non-empty array of distinct reward accounts | Reward accounts that may receive this category's withdrawals. |

The smallest valid definition carries `kind` and one entry with only `key` and `label`. Such a category groups actions but has no recipient check, so its checked total stays 0 and every enacted member withdrawal appears in the unchecked figure.

The prose in `abstract`, `motivation` and `rationale` stays authoritative for what the category covers and who runs it. Tools compute with the structured fields and SHOULD link the prose next to every computed figure.

A category changes only through a new definition action. Version 1 has no link between an old and a new definition.

### Member

Allowed on Treasury Withdrawals and Info Actions.

| Property | Required | Type and form | Meaning |
| --- | --- | --- | --- |
| `kind` | yes | `"member"` | |
| `categoryId` | yes | governance action ID | Governance action ID of the definition action. |
| `categoryKey` | yes | string in the form of `key` | `key` of the category within that definition action. |

A member action names exactly one category. A proposal that spans categories is split into one action per category. An Info Action member, such as a report or a scope change, is listed with the category and never adds to any total.

### Validity

A `category` object is valid only when all of the following hold. Otherwise readers MUST treat it as absent and MUST NOT repair or coerce values. Readers check validity on the JSON document as anchored, before JSON-LD expansion, because expansion hides differences such as an empty array, a single string or object in place of an array, or duplicate entries.

- The context maps it as described above.
- `kind` is `definition` on an Info Action, or `member` on a Treasury Withdrawal or Info Action. Any other combination, including any `category` on another action type, is invalid.
- Every required property is present, and every present property has the type and form given in its table.
- The `category` object carries only the properties defined for its `kind`.
- Each category entry carries only the properties in the category entry table.
- The `key` values within `categories` are distinct.

### How tools read it

1. **Approval stays a social decision.** Info Actions are never enacted, so the ledger never says whether a category was approved. Tools MUST show the definition action's tally and status next to the category, SHOULD make clear when that tally covers several categories, and MUST NOT present a category as approved by protocol. A tool MAY apply a threshold named by the process the category belongs to, and MUST say which one.
2. **Resolving a category.** Tools read `category` only from a document whose bytes match the action's own on-chain anchor hash, for definition and member actions alike. A member action resolves when `categoryId` is the ID of a definition action whose anchor document has been verified at least once, and `categoryKey` is the `key` of one of its categories. Tools MAY keep verified bytes, and a category stays as read when its anchor URL later stops serving. A member action that does not resolve is shown as unresolved. Tools MUST NOT guess the category from titles. Tools SHOULD show a Treasury Withdrawal without a valid `category` as having no declared category.
3. **Recipient check.** When the category lists `recipients`, a tool decodes each listed account and each reward account in the Treasury Withdrawal's ledger body to its header byte and 28-byte credential, and compares those. A listed account on another network never matches. The result is **matched** when every withdrawal recipient is listed, and **mismatch** otherwise. Without `recipients`, the withdrawal is **unchecked**.
4. **Counting.** A member counts only for the category that its `categoryId` and `categoryKey` together resolve to. A category's checked total is the sum of the ledger amounts of enacted, **matched** member Treasury Withdrawals, attributed by enactment epoch and limited to `period` when given. Amounts always come from the ledger, never from metadata. Tools SHOULD show unchecked and mismatched withdrawals as separate figures and MUST NOT add them to the total. Members not yet enacted, or enacted outside `period`, are listed with the category and appear in no figure. Tools SHOULD make clear that membership rests on the proposer's own reference.
5. **Members that can no longer count.** Tools SHOULD flag a member Treasury Withdrawal that can no longer count towards its category: one submitted in an epoch after the category's `endEpoch`, or one enacted outside `period`. A withdrawal submitted before `startEpoch` is not flagged for that alone, because it can still be enacted within the period. Info Action members, such as reports, are not flagged.

### Example

The `body` of a definition action that defines two categories, abbreviated to `title` and the part this CIP adds. `body.@context` with the term definition from above is left out. IDs and the account are made up for illustration, with valid checksums. `process` points at the Info Action that set up the wider budget, for example one that set a Net Change Limit.

```json
"body": {
  "title": "Budget domains 2027",
  "category": {
    "kind": "definition",
    "process": "gov_action1neayu43mmlucmgpz9nn6z0e683amvdawk08vcush9qkfnmfkgdqsqsnqerx",
    "categories": [
      {
        "key": "core-infra",
        "label": "Core Infrastructure 2027",
        "budget": "50000000000000",
        "period": { "startEpoch": 620, "endEpoch": 692 },
        "recipients": ["stake179xe3t8ka8c52d73a747kxkuqqvrh0hh3urzqwlgnlqursq8p8cvg"]
      },
      {
        "key": "community",
        "label": "Community 2027",
        "period": { "startEpoch": 620, "endEpoch": 692 }
      }
    ]
  }
}
```

Suppose this action is `gov_action1s6seccwg27dtcmktfgrshm2gupk8rx6l68y6082yja59e4mqxj2sql4mr29`. A later Treasury Withdrawal that spends against the first category carries:

```json
"category": {
  "kind": "member",
  "categoryId": "gov_action1s6seccwg27dtcmktfgrshm2gupk8rx6l68y6082yja59e4mqxj2sql4mr29",
  "categoryKey": "core-infra"
}
```

If that withdrawal pays the listed account and is enacted in an epoch from 620 to 692, its ledger amount counts towards the 50 million ada ceiling. If it pays another account, tools show it as a mismatch outside the total. The second category has no `budget` and no `recipients`, so it groups its members, and their withdrawals enacted within its period appear in its unchecked figure.

### Example files and schema

[`cip-0211.common.jsonld`](./cip-0211.common.jsonld) is the CIP-0108 context with this CIP's term definition and prefix merged in. [`examples/`](./examples/) holds complete documents for the definition above, a Treasury Withdrawal in `core-infra` and a report as an Info Action in `community`. They carry no author witnesses. The documents in [`examples/invalid/`](./examples/invalid/) each break one rule.

[`cip-0211.common.schema.json`](./cip-0211.common.schema.json) (JSON Schema 2020-12) checks the form of `category`. It cannot check bech32 checksums, distinct keys, `startEpoch <= endEpoch`, `kind` against the action type, or the context mapping, so readers still apply every rule in the Validity section. With [ajv-cli](https://github.com/ajv-validator/ajv-cli), which picks its parser from the file extension:

```sh
cp examples/definition.jsonld /tmp/example.json
ajv validate --spec=draft2020 -s cip-0211.common.schema.json -d /tmp/example.json --all-errors
```

## Rationale: How does this CIP achieve its goals?

**The definition action and a key identify a category.** A string such as `"core-infra"` on its own would need a registry and would collide across years and processes. The governance action ID already exists, is unique, cannot change once on chain, and points at the vote on the category, so a `key` only has to be unique within one action. The definition does not need an action of its own: a budget process usually submits an Info Action anyway, for example one that sets a Net Change Limit or an annual budget, and that action can carry the categories without an extra deposit.

**One or several categories per definition.** A process can define all its categories in one action, for example an annual budget with its domains, or put each category in its own action so DReps vote on each one separately. The CIP leaves that choice to the process. Categories defined in one action share its tally.

**Optional budget fields.** Grouping is useful on its own, for example a grant round's reports. With the budget fields optional, one mechanism covers a plain group and a funded allocation.

**Only Treasury Withdrawals and Info Actions.** These are the types that set up, spend or report on treasury funds. Other types already have a ledger-recorded type and no figure to compute. A later version can open the field to them without breaking version 1 documents.

**In the action's own metadata.** A separate metadata label could be posted by anyone. In `body`, the link is part of what the proposers signed, and the anchor hash fixes it after submission.

**Recipients make the claim checkable.** Without a check, anyone could tag a withdrawal with a popular category. Withdrawals of a funded program often pay into one or a few accounts, for example Intersect's 2026 withdrawals into a single script reward account. A short list in the definition then checks each withdrawal without a second vote. Comparing decoded credentials avoids false mismatches between text forms of the same account.

**Strict validity and one text form.** Two tools that disagree about a malformed document show different totals, which is the problem this CIP addresses. Ignoring an invalid object entirely is a rule every tool applies the same way. For the same reason only lower-case bech32 is accepted, although bech32 also allows upper case, so that no reader has to choose between rejecting and normalizing. The 80 code point `label` limit keeps a name readable in one line of a list.

**No role for who runs a category.** The names for that role (steward, administrator, committee) carry positions in an ongoing debate about control of treasury funds. `recipients` covers what tools can check, and the rest belongs in the prose and `references`.

**One category per member action.** Several categories on one member action would count the same lovelace twice, and a per-recipient split would repeat amounts the ledger already holds.

**No supersession in version 1.** A pointer from a new definition to an old one raises questions the chain cannot answer: who may replace a category, which of two replacements wins, and whether totals carry over.

**Relation to other standards and alternatives.**

- *CIP-0100 `references`* can point at another action, but a reference has no defined meaning, so a tool cannot tell a category link from a citation.
- *CIP-0169 `onChain`* restates ledger content. A category is a claim by the proposer that the ledger does not hold.
- *CIP-0179* adds survey links to the same `body`. This CIP follows its context merge.
- *Governance Action Addendums* ([CIP-0185?](https://github.com/cardano-foundation/CIPs/pull/1180)) publish later updates under a separate label. A category in the anchored `body` cannot change afterwards, which keeps totals stable. Addendums could reuse this field later.
- *A free label without a definition action* would let two processes pick the same word and has nothing to check against.
- *A registry or a list of categories in a CIP* needs someone to maintain it and decide what goes in, and it would change with every budget cycle.
- *Tool-side curation* has to be repeated by every tool. It remains the fallback for actions submitted before this CIP.

### Backwards compatibility

The field is optional. Tools that do not implement this CIP can ignore it. Earlier actions carry no field and cannot be tagged retroactively.

### Open Questions

- Should definitions keep pointing at an umbrella action only through the generic `process` field, which still fits if the way treasury funds are set up changes, or name the Net Change Limit or another funding mechanism explicitly?
- Is a fixed `recipients` list the right check when a category pays many recipients that are not known when it is defined, or does a later version need another way to confirm membership?
- Does a later version need a link from a new definition to the one it replaces, for example when the receiving account changes mid-period and the ceiling should count only once, and what decides between competing replacements?
- Should a later version let a party other than the proposer confirm, contest or reassign an action's category, for example in a stage before the vote through a [CIP-0179](../CIP-0179/README.md) survey or an addendum ([CIP-0185?](https://github.com/cardano-foundation/CIPs/pull/1180)), which result then counts for the totals, and should tools show such statements from parties eligible to vote on the action next to the proposer's reference?
- Should a later version open member actions to further action types?

## Path to Active

### Acceptance criteria

- [ ] At least one mainnet Info Action that defines a category with this field.
  - [ ] At least one mainnet Treasury Withdrawal that is a member of it.
- [ ] At least one tool that writes the field when submitting governance actions, built by people unaffiliated with the author.
- [ ] At least one tool that reads the field and shows per-category totals by the counting rule above, built by such an unaffiliated team, and agreeing with the test vectors.

### Implementation plan

No implementation exists yet. The format is put up for review first, so that tool builders, budget process teams and DReps can shape it before any document carries it.

- [x] Open the CIP pull request and fix the namespace IRI.
- [x] Publish example documents, the merged context and a JSON Schema for `category`.
- [ ] Publish test vectors with the CIP: valid documents with and without `onChain` and `cip179`, with anchor and canonical body hashes, one invalid document per validity rule, the three recipient results, one total fixture covering every member status and the `period` bounds, and one fixture with a definition of two categories that differ in `recipients` and `period`, members for each key, a member with an unknown key, and the same key under another definition.
- [x] Ask budget process teams, grant programs and tool builders to review the format.

No tool should write the field on Mainnet until this CIP is merged. Testnets are fine.

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
