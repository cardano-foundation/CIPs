# Test Vector for CIP-0169

Here we provide worked examples binding governance metadata to its on-chain effect via
the [`onChain`](./README.md#the-onchain-property) property, together with the reproducible
hashes and author signatures for each.

Unlike the other examples in sibling CIPs, **every example here carries a populated
`authors` witness**. This is deliberate: the security guarantee of CIP-0169 is that an
author signature covers a `body` which *includes* `onChain`, so an example with an empty
`authors` array would not demonstrate the standard at all.

## Common Context

### Common Fields

The context fields which could be added to CIP-0169 compliant `.jsonld` files.
See [cip-0169.common.jsonld](./cip-0169.common.jsonld).

This file is a **fragment**: it defines only the `onChain` extension plus the optional
CIP-100 fields (`references`, `comment`, `externalUpdates`). A real document merges it with
its downstream body vocabulary (CIP-108/119/136). The example files below therefore inline a
*merged* `@context` (e.g. CIP-108 `title`/`abstract`/… **and** `onChain`) — this is what an
actual on-chain document looks like, and it is required so the downstream prose is covered by
the author signature.

Inside `onChain`, the context maps the well-known CIP-0116 governance terms explicitly and
adds a `@vocab` default for everything else:

```json
"onChain": {
  "@id": "CIP169:onChain",
  "@context": {
    "@vocab": "https://github.com/cardano-foundation/CIPs/blob/master/CIP-0116/README.md#",
    "deposit": "CIP116:deposit",
    "reward_account": "CIP116:reward_account",
    "gov_action": { "@id": "CIP116:gov_action", "@context": { "...": "..." } }
  }
}
```

The explicit mappings keep the well-known structure self-documenting with precise IRIs. The
`@vocab` default guarantees that **every** other property reachable inside `onChain` — at any
nesting depth, including future CIP-0116 fields — still resolves to an IRI and is therefore
preserved during canonicalization and covered by the signature. Together they satisfy the
requirement that no term be silently dropped, without having to enumerate every CIP-0116
property by hand.

### Common Fields Schema

A JSON schema (2020-12) for the common context fields.
See [cip-0169.common.schema.json](./cip-0169.common.schema.json).

## Authors

Keys used for the `authors` property, provided here so the signatures below can be recreated.

### Author 1 — shared canonical keyset

This is the same keyset published by [CIP-100](../CIP-0100/), [CIP-108](../CIP-0108/test-vector.md#author)
and [CIP-136](../CIP-0136/), reused here so hashes are cross-checkable.

- Private extended signing key (hex): `105d2ef2192150655a926bca9cccf5e2f6e496efa9580508192e1f4a790e6f53de06529129511d1cacb0664bcf04853fdc0055a47cc6d2c6d205127020760652`
- Public verification key (hex): `7ea09a34aebb13c9841c71397b1cabfec5ddf950405293dee496cac2f437480a`
- Public key hash (hex): `0fdc780023d8be7c9ff3a6bdc0d8d3b263bd0cc12448c40948efbf42`

### Author 2 — second signer (for the multi-author example)

A second key, used only by [Treasury Withdrawal](#treasury-withdrawal) to demonstrate joint
authorship. This is a plain (non-extended) Ed25519 key.

- Private key seed (hex): `00112233445566778899aabbccddeeff00112233445566778899aabbccddeeff`
- Public verification key (hex): `3ccd241cffc9b3618044b97d036d8614593d8b017c340f1dee8773385517654b`

Each author's `witness.signature` is an Ed25519 signature over the Blake2b-256 hash of the
canonicalized `body` (the "canonicalized body" hash listed per-example below), exactly as
described in [CIP-100 Hashing and Signatures](../CIP-0100/README.md#hashing-and-signatures).

## Examples

For each example: the **file content hash** (Blake2b-256 of the whole `.jsonld`, this is what
goes on-chain as the metadata anchor hash) and the **canonicalized body hash** (Blake2b-256 of
the RDF-canonicalized `body`, this is what the authors sign).

### Governance Actions

`onChain` is a [CIP-0116 `ProposalProcedure`](./README.md#for-governance-actions) (with `anchor` omitted).

#### Parameter Change

[parameter-change.jsonld](./examples/parameter-change.jsonld) — `parameter_change_action` binding a `max_block_body_size` update.
- File content hash: `b94f944d080a8b412fdd001a24e8c2a214314e46872988d9a11ca9921b7172de`
- Canonicalized body hash: `95328398f4e5ce1312040583aa8ec6654aa22244869389769e599dc87877e0b0`

#### Treasury Withdrawal

[treasury-withdrawal.jsonld](./examples/treasury-withdrawal.jsonld) — `treasury_withdrawals_action`.
**Two authors** sign the same body, and a `references` entry is included: this is the
multi-author scenario from the [Motivation](./README.md#multi-author-misattachment) — both
signatures are bound to the exact `rewards` destination.
- File content hash: `cc09ff83285133765146a2a25a83d08670078e08dbf36441add5d7007561ddf5`
- Canonicalized body hash: `5d95174f81b3ced148e4439df90272d19b5ab66a09282489fd36ed298e1804ba`

#### Info Action

[info-action.jsonld](./examples/info-action.jsonld) — `info_action` (no protocol effect).
Shows that `deposit` and `reward_account` are the only required `ProposalProcedure` fields.
- File content hash: `aa81de55faabe0b83c8259dead46c0d620cc1196553db09fe8762b69a7486257`
- Canonicalized body hash: `3c7d3967df872ecf1a15925f9b8c0481922663560d7b4166a928a59995406ecb`

#### New Constitution

[new-constitution.jsonld](./examples/new-constitution.jsonld) — `new_constitution`. This is
the one action where a nested `anchor` is **retained**: `Constitution.anchor` points to the
constitution document (a separate artifact that is itself part of the on-chain effect), so it
is *not* the self-referential anchor prohibited elsewhere. See the
[Rationale](./README.md#why-exclude-the-self-referential-anchor).
- File content hash: `ae733cc4879586038c72cc8320b66e749095af0cfdfa9ec864aec4e57d207173`
- Canonicalized body hash: `aa5ee2ba2efafc92bb34cb4a790b5ca4532947e0f8335e16272a6756750b9e41`

### Votes

`onChain` is a [CIP-0116 `VotingProcedures`](./README.md#for-votes) map (with each inner `anchor` omitted).

#### DRep Vote

[vote.jsonld](./examples/vote.jsonld) — a `drep_credential` voter casting `yes` on one action.
- File content hash: `ad8c5f7c1b73f13c76371047e96f492ad890f6d1d8d585c9d81ffd240a92c9ae`
- Canonicalized body hash: `94ec7c65ed1342bb9b92e1b524aad04f9c2128eedbae2f3bbf5d7776f49ce72e`

#### Constitutional Committee Vote

[committee-vote.jsonld](./examples/committee-vote.jsonld) — a `cc_credential` voter casting `no`, with a CIP-136 rationale body.
- File content hash: `2eea6d9906e8a5660a3fecc64cafac0815e7b8b170b09a5ad13ba3417a067b67`
- Canonicalized body hash: `8482fc078d8b031eb31b6c898672a0c828ee176b43bd72c24aaa6a8ad1c6cdec`

### Certificates

`onChain` is a CIP-0116 certificate (with `anchor` omitted).

#### DRep Registration

[drep-registration.jsonld](./examples/drep-registration.jsonld) — `register_drep` (`drep_credential` + `coin` deposit), with a CIP-119 profile body.
- File content hash: `f421a41ec0081c16a9b23e75e71f808de4c3e933254a529dfb26d205e031c783`
- Canonicalized body hash: `ffa5db2a497b8b51cc1302def50366aacb3a30aee77a8806d9c762fd0d50ef43`

#### DRep Update

[drep-update.jsonld](./examples/drep-update.jsonld) — `update_drep` (`drep_credential`, no `coin`).
- File content hash: `c7f4b4f42531c6ee02aab761dee349650b07f48ef58a0f3122c7d12377bcf8c9`
- Canonicalized body hash: `1211853ce1cda2fbe07c0512c37310942492687585a8ba1e6eee49fbcc8c18d5`

#### Committee Cold Resignation

[committee-resignation.jsonld](./examples/committee-resignation.jsonld) — `resign_committee_cold` (`committee_cold_credential`).
- File content hash: `3e16fb0d2f6885cb9ad0f2be6417d2162bcd6f57ea0cf1d4da6932ed2dd1ecd6`
- Canonicalized body hash: `b9521ad29fc7bb79f6f790053a7f97a412047323c01c183f0790327ebfbbf309`

## Negative Vectors

These are documents that a correct CIP-0169 implementation **must reject**. They demonstrate
the two distinct failure modes the CIP guards against.

### 1. Forbidden self-referential anchor (schema failure)

[invalid/forbidden-anchor.jsonld](./examples/invalid/forbidden-anchor.jsonld) — a
`ProposalProcedure` that wrongly embeds an `anchor` pointing back at this metadata document.
This is caught **statically** by the schema: `ProposalProcedure` sets
`unevaluatedProperties: false`, so validation reports

```
instancePath: '/body/onChain', keyword: 'unevaluatedProperties', unevaluatedProperty: 'anchor'
```

### 2. On-chain mismatch / metadata replay (comparison failure)

This failure mode **cannot** be caught by schema validation — the document is well-formed and
its author signatures are valid. It is exactly what CIP-0169 exists to detect, and is caught at
step 4 (Compare) of the [Verification Process](./README.md#verification-process):

1. Take [treasury-withdrawal.jsonld](./examples/treasury-withdrawal.jsonld) unchanged — same
   prose, same two valid author signatures, `onChain.gov_action.rewards` pays
   `stake1uxsm9s75uhm20wxf6rsl9ga5chtw079fkrqa9cl55kmv0kqfk32j7`.
2. Attach it to an on-chain `ProposalProcedure` whose `rewards` instead pay a **different**
   stake address.
3. A pre-CIP-0169 verifier sees three legitimate-looking signatures over legitimate-looking
   prose and shows the action as endorsed.
4. A CIP-0169 verifier compares `body.onChain` against the actual on-chain action, finds the
   `rewards` destination differs, and refuses to display the metadata as endorsed.

## How-to Recreate Examples

The examples were generated with standard tooling. The steps below recreate any one of them.

### 1. Assemble `example.jsonld`'s `body`

Author the document with its inlined merged `@context` (downstream body vocabulary +
`onChain`), then take a copy containing only `@context` and `body`.

### 2. Canonicalize the `body`

Using a [RDF Dataset Canonicalization (URDNA2015)](https://w3c-ccg.github.io/rdf-dataset-canonicalization/spec/)
tool — e.g. the [JSON-LD Playground](https://json-ld.org/playground/) or the `jsonld` npm
package — produce the canonical N-Quads of `{ "@context": …, "body": … }`. Ensure the result
ends in a newline. Because the context uses `@vocab` inside `onChain`, every on-chain field
appears in the output; if a field is missing, the binding is incomplete.

### 3. Hash the canonicalized `body`

Blake2b-256 the canonical N-Quads. This is the "canonicalized body hash" listed per-example
and is the payload the authors sign.

### 4. Each author witnesses the body hash

For a `witnessAlgorithm` of `ed25519`, sign the body hash from step 3 with the author's key
(see [Authors](#authors)). Put the result in `authors[].witness.signature`. For a multi-author
document, every author signs the *same* body hash.

### 5. Complete `example.jsonld`

Add `hashAlgorithm: "blake2b-256"` and the populated `authors` array back to the document.

### 6. Hash `example.jsonld`

Blake2b-256 the whole file's content — this is the "file content hash" that goes on-chain as
the metadata anchor hash alongside the document's URI.

### 7. Validate

Validate the document against the schema (see [Validation](./README.md#validation)) and, for a
full check, re-run steps 2–4 and confirm each `signature` verifies against its `publicKey` and
the recomputed body hash.
