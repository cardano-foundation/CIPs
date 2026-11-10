# CIP-0100 Extension Index

An informative index of the CIPs that extend [CIP-0100](./README.md), how they combine, and their known gotchas.
If this index disagrees with a CIP, the CIP is authoritative.
Please update it when a CIP-0100 extension is merged or revised.

## Extensions

| CIP | Adds to `body` | Use for anchor | Kind | Signed? |
| --- | --- | --- | --- | --- |
| [CIP-0108](../CIP-0108/README.md) | `title`, `abstract`, `motivation`, `rationale`, `references[].referenceHash` | Governance actions | Document type | Yes |
| [CIP-0119](../CIP-0119/README.md) | `givenName`, `image`, `objectives`, `motivations`, `qualifications`, `paymentAddress`, `doNotList` | DRep registration / update | Document type | **No** (by design) |
| [CIP-0136](../CIP-0136/README.md) | `summary`, `rationaleStatement`, `precedentDiscussion`, `counterargumentDiscussion`, `conclusion`, `internalVote` | Constitutional Committee votes | Document type | Yes |
| [CIP-0169](../CIP-0169/README.md) | `onChain` (the on-chain effect in CIP-0116 JSON) | Any of the above | Add-on | Relies on it |
| [CIP-0179](../CIP-0179/README.md) | `cip179` (link to a label `17` survey) | Governance actions only | Add-on | Relies on it |

A document uses **one document type** plus any add-ons. Never mix document types in one document.

Anchors with no dedicated extension use plain CIP-0100, optionally with CIP-0169. These are DRep and SPO votes (put the rationale in `comment`) and CC cold-key resignations.
`Constitution.anchor` is **not** CIP-0100: it points to the plain-text document defined by [CIP-0120](../CIP-0120/README.md).

## Combining extensions: merge contexts by hand

Every context defines its own `body` term (`CIP108:body`, `CIP119:body`, `CIP136:body`, `CIP100:body` in CIP-0169).
In JSON-LD a later term definition **replaces** an earlier one, so a `@context` array silently loses fields:

- `[cip108, cip169]` drops `title`, `abstract`, `motivation` and `rationale`.
- `[cip169, cip108]` drops `onChain`, `comment` and `externalUpdates`.

Dropped fields still appear in the raw JSON, but the author signatures **do not cover them**. These results were checked with jsonld.js 8.3.3.
Instead, write one inline context: keep the document type's `body` and add the add-on terms inside its scoped `@context`. See [`CIP-0169/examples/`](../CIP-0169/examples/).
Before signing, canonicalize the document and check that every expected field is present.

## Gotchas

**Across all extensions**

- **The anchor hash and the signatures cover different things.** The anchor hash is blake2b-256 of the raw bytes, so reformatting the JSON breaks it. The signatures cover the RDF-canonicalized `body`, so a field without a context term is not signed.
- **Context terms are missing in several places.** No context uses `@vocab` (except inside CIP-0169 `onChain`), so any undefined field is silently left unsigned. The CIP-0108, CIP-0119 and CIP-0136 contexts omit `comment` and `externalUpdates`. The base CIP-0100 context defines lowercase `governanceMetadata`/`other`, while the spec and every extension use `GovernanceMetadata`/`Other`.
- **Reference types are per extension:** `Link` and `Identity` (CIP-0119) and `RelevantArticles` (CIP-0136). Only CIP-0108 adds `referenceHash`. Show unknown types as plain links.
- **CIP-0100 contradicts itself on the anchor hash.** One section says to hash the canonical RDF. The hashing section and the test vectors use raw bytes, which is the rule in practice.
- **On-chain hosting under label `1694` has a string limit.** Metadata strings are capped at 64 bytes, and CIP-0100 does not say how to split longer ones.

**CIP-0108**

- The compulsory fields (`title`, `abstract`, `motivation`, `rationale`) are listed only under *Open Questions* and in the schema. The schema also requires `authors[].name`.
- `title` is limited to 80 characters and `abstract` to 2500. Markdown is allowed in `abstract`, `motivation` and `rationale`, but not in `title`.
- The `CIP-0008` witness algorithm (CIP-30 `signData`) is allowed. Verifiers that only support `ed25519` should report it as unverified, not invalid.
- The spec mentions referencing "via the index", but no index field exists.

**CIP-0119**

- Authors are meant to be left empty, and tools need not warn that the document is unsigned. The context has no `authors` term, so authors are dropped if added.
- `doNotList` is a boolean in the README but the string `"true"`/`"false"` in the schema, so accept both. It is advisory only.
- These are dropped when canonicalized because the context does not define them: `doNotList`, `image.contentUrl`, `image.sha256`, the `Link`/`Identity` types, and any other schema.org `Person` property.
- Image hashes use **SHA-256**, not blake2b-256.

**CIP-0136**

- `summary` (300 characters, no markdown) and `rationaleStatement` are required. `conclusion` has no markdown.
- In `internalVote`, `againstVote` counts votes *not to vote*, which is different from `unconstitutional`.
- The context uses `@language: "en-us"`. CIP-0169 uses `"en"`. Pick one language when merging.

**CIP-0169**

- Remove the self-referential `anchor` from the encoded procedure or certificate. Keep `Constitution.anchor`.
- Fields inside `onChain` are snake_case, per CIP-0116.
- Verify the signatures first, then compare `onChain` with the chain. On unsigned CIP-0119 documents, `onChain` only catches verbatim copies, because an attacker can rewrite it and re-hash.

**CIP-0179**

- `body.cip179` is valid only in CIP-0108 documents, and its terms must be added to the context. Without them, the link is not signed.
- The survey `end_epoch` must equal the action's expiry epoch. A missing `surveyIndex` breaks the link, so never default it to `0`.
- Surveys themselves are CBOR under label `17`, not CIP-0100 documents.
