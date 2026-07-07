# Test Vector for CIP-0169

Here we provide worked examples binding governance metadata to its on-chain effect via
the [`onChain`](./README.md#the-onchain-property) property, with the reproducible
hashes and author signatures for each.

## Common Context

### Common Fields

The context fields which could be added to CIP-0169 compliant `.jsonld` files.
See [cip-0169.common.jsonld](./cip-0169.common.jsonld).

This file is a **fragment**: it defines only the `onChain` extension plus the optional
CIP-100 fields (`references`, `comment`, `externalUpdates`). A real document merges it with
its downstream body vocabulary (CIP-108/119/136).

The example files below therefore inline a *merged* `@context` (e.g. CIP-108 `title`/`abstract`/… **and** `onChain`) this is what an actual on-chain document looks like, and it is required so the downstream prose is covered by the author signature.

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
`@vocab` default guarantees that **every** other property reachable inside `onChain`, at any
nesting depth, including future CIP-0116 fields, still resolves to an IRI and is therefore
preserved during canonicalization and covered by the signature. Together they satisfy the
requirement that no term be silently dropped, without having to enumerate every CIP-0116
property by hand.

### Common Fields Schema

A JSON schema (2020-12) for the common context fields.
See [cip-0169.common.schema.json](./cip-0169.common.schema.json).

## Authors

Keys used for the `authors` property, provided here so the signatures below can be recreated.

### Author 1

This is the same keyset published by [CIP-100](../CIP-0100/), [CIP-108](../CIP-0108/test-vector.md#author)
and [CIP-136](../CIP-0136/).

- Private extended signing key (hex): `105d2ef2192150655a926bca9cccf5e2f6e496efa9580508192e1f4a790e6f53de06529129511d1cacb0664bcf04853fdc0055a47cc6d2c6d205127020760652`
- Public verification key (hex): `7ea09a34aebb13c9841c71397b1cabfec5ddf950405293dee496cac2f437480a`
- Public key hash (hex): `0fdc780023d8be7c9ff3a6bdc0d8d3b263bd0cc12448c40948efbf42`

### Author 2

A second key, used only by [Treasury Withdrawal](#treasury-withdrawal) to demonstrate joint
authorship. This is a plain (non-extended) Ed25519 key.

- Private key seed (hex): `00112233445566778899aabbccddeeff00112233445566778899aabbccddeeff`
- Public verification key (hex): `3ccd241cffc9b3618044b97d036d8614593d8b017c340f1dee8773385517654b`

### Governance Actions

`onChain` is a [CIP-0116 `ProposalProcedure`](./README.md#for-governance-actions) (with `anchor` omitted).

#### Parameter Change

[parameter-change.jsonld](./examples/parameter-change.jsonld) — `parameter_change_action`.
- File content hash: `519e82090dfe6a0156bd700fd8cba8aa821fd5ea2103be9b36896efea58a5ffe`
- Canonicalized body hash: `1b5315408e7b9d28920eb3acc1e0a3c54028ca7e2914ab8947be10c7ebbc5592`

#### Treasury Withdrawal

[treasury-withdrawal.jsonld](./examples/treasury-withdrawal.jsonld) — `treasury_withdrawals_action`.
- File content hash: `b43eeecfcc96e15aff04031bd89cacbaa8a8320d2e686d57442b4a11bfa44468`
- Canonicalized body hash: `271919c67490332f838362794907860f84a1121d809677d307ec120c23a248fb`

#### Info Action

[info-action.jsonld](./examples/info-action.jsonld) — `info_action`.
- File content hash: `aa81de55faabe0b83c8259dead46c0d620cc1196553db09fe8762b69a7486257`
- Canonicalized body hash: `3c7d3967df872ecf1a15925f9b8c0481922663560d7b4166a928a59995406ecb`

#### New Constitution

[new-constitution.jsonld](./examples/new-constitution.jsonld) — `new_constitution`.
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

[drep-registration.jsonld](./examples/drep-registration.jsonld) — `register_drep`.
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

## Live Examples (Preview testnet)

### Governance actions

| Example | Transaction | Gov action id |
|---|---|---|
| [`info_action`](./examples/preview/info-action.jsonld) | `3ff13ad85117e9cde53d67dada19eb80a9c7971efdee95d73020f3b3c467d8b5` | `gov_action18lcn4kz3zl5umefavldd5x0tsz5u09c7lhhft4esyrem83r8mz6sq6faha5` |
| [`treasury_withdrawals_action`](./examples/preview/treasury-withdrawal.jsonld) (2 authors) | `c0efa6a3419b67769001f5446ee34bdf779f707b0abe53593da933ab674b4b07` | `gov_action1crh6dg6pndnhdyqp74zxac6tmame7urmp2l9xkfa4ye6ke6tfvrsqfjanrz` |
| [`parameter_change_action`](./examples/preview/parameter-change.jsonld) | `8bd727c7aab758be609958b9bdaf84096b8f30bc7cfa0956d6a3ddc91b816550` | `gov_action130tj03a2kavtucyetzummtuyp94c7v9u0naqj4kk50wujxupv4gqqurtz7k` |
| [`new_constitution`](./examples/preview/new-constitution.jsonld) | `1173b9b3bf1c606a6217be2f94260b85c9f03ef301ae0a6cf4956cc82ef7900f` | `gov_action1z9emnvalr3sx5cshhchegfstshylq0hnqxhq5m85j4kvsthhjq8sqd5unce` |

### Vote and certificates

| Example | Transaction | Subject |
|---|---|---|
| [DRep vote](./examples/preview/vote.jsonld) (`VotingProcedures`, `yes`) | `dd878dc48fc7c194d657114605c4a56d5473d8f4c44f278803692c24ac7e2e7a` | DRep `03ccae79…` voting on the `info_action` above |
| [`register_drep`](./examples/preview/drep-registration.jsonld) | `947a2d1646dc32535067c70b3dffecba4740f8f4e3578de5d72565fc926d3ead` | fresh DRep `fa128333…` |
| [`update_drep`](./examples/preview/drep-update.jsonld) | `16d782f99c418d644df691e6801942681adc871256a49175bd18b7a6fed676f3` | existing DRep `03ccae79…` (anchor was null, now set) |

### Anchors

Each anchor hash is the Blake2b-256 of the verbatim document in
[`examples/preview/`](./examples/preview/) and matches the anchor hash recorded on-chain.

| Document | Anchor URL | Anchor hash (= file content hash) |
|---|---|---|
| info-action | `ipfs://bafkreifs6tuhffydrble3v6dk4lnkeagz4fygmk5st763utxlttbtskme4` | `13a7e4b127b18ad62f39ca6d72cb73d7bcd0eab00a0a5a1dc65a25fab84f223f` |
| treasury-withdrawal | `ipfs://bafkreibjzs4nmng3hi7hfgr3pvskiqw3dtvyeoqhheeh7lnh64putd3mua` | `b85c007f9838ffe73e3fa6878db3e2ec2b2e9d901037782b1e384453174fc85a` |
| parameter-change | `ipfs://bafkreigd2wq5hfu5rz5p572ncybogjmtjpiljwahquscuuzilugmcrsvii` | `831056012804ea41a1ecd1e3ca0dbd9c58a46550942f2dc5dce93e033e31d4e2` |
| new-constitution | `ipfs://bafkreigmyzlwehwlxmpq6tncxjnbuw4nydu5y2prmh3b26optsmxv4frey` | `25c51a11d0e946c1959e851e3a6413bb89734be624da4673fd83a08524ec6648` |
| vote | `ipfs://bafkreihniyugf4bq5h22bymtpnl23n75g5p2cq562cfznuvx74z4wirrpm` | `7f95c810df8e66cc9bccc2dd08303342b99a3600326c75939da4009dc498d1e2` |
| drep-registration | `ipfs://bafkreihnd5vsgmuvjbgv74cytzbpfspfx62i2h6zcjydm4bt2fbhte5n74` | `c92199160c7915a92c3e3e7469a61912a8f5c706d31162b2a5f5a1f73db6a405` |
| drep-update | `ipfs://bafkreifgycv6octwh7x3pyjmsh6sqkj6f2vznjyoydsjjqphaiemdk2yca` | `1bd1c918a0f7684320299c1b3999006ec8ba56f785dbebd3b0455681501e8b7d` |

## Negative Vectors

These are documents that a correct CIP-0169 implementation **must reject**.
They demonstrate the two distinct failure modes the CIP guards against.

### 1. Forbidden self-referential anchor (schema failure)

[invalid/forbidden-anchor.jsonld](./examples/invalid/forbidden-anchor.jsonld) — a
`ProposalProcedure` that wrongly embeds an `anchor` pointing back at this metadata document.

### 2. On-chain mismatch / metadata replay (comparison failure)

This failure mode **cannot** be caught by schema validation — the document is well-formed and
its author signatures are valid.

It is exactly what CIP-0169 exists to detect, and is caught at step 4 (Compare) of the [Verification Process](./README.md#verification-process):

1. Take [treasury-withdrawal.jsonld](./examples/treasury-withdrawal.jsonld) unchanged — same
   prose, same two valid author signatures, `onChain.gov_action.rewards` pays
   `stake1uxsm9s75uhm20wxf6rsl9ga5chtw079fkrqa9cl55kmv0kqfk32j7`.
2. Attach it to an on-chain `ProposalProcedure` whose `rewards` instead pay a **different**
   stake address.
3. A pre-CIP-0169 verifier sees three legitimate-looking signatures over legitimate-looking
   prose and shows the action as endorsed.
4. A CIP-0169 verifier compares `body.onChain` against the actual on-chain action, finds the
   `rewards` destination differs, and refuses to display the metadata as endorsed.

### 3. Real-world incomplete binding (superseded Preview actions)

The same failure mode was observed live on Preview, by accident. The first submissions of the
[treasury withdrawal](#live-examples-preview-testnet) and parameter change (2026-07-03) omitted
`policy_hash` from `onChain.gov_action`. On-chain, the ledger attaches the constitution's
guardrails script hash to both `treasury_withdrawals_action` and `parameter_change_action`, so a
CIP-0169 verifier comparing `body.onChain` against the action correctly flagged
`gov_action.policy_hash does not match this transaction` — even though both documents were
well-formed, schema-valid, and carried valid author signatures.

| Superseded action | Transaction | Gov action id |
|---|---|---|
| `treasury_withdrawals_action` (2 authors) | `8c5ec528313a2997aed822e44bc5251721bbdc9bbc30e6bbf6914bf65c1ac4a4` | `gov_action1330v22p38g5e0tkcytjyh3f9zusmhhymhscwdwlkj99lvhq6cjjqqezhfxq` |
| `parameter_change_action` | `8009f3a24731320244568273a4d7eed1b436067c91aeb98bdb2872e45ef5b1d6` | `gov_action1sqyl8gj8xyeqy3zksfe6f4lw6x6rvpnujxhtnz7m9pewghh4k8tqq4gpgsj` |

Both were corrected by adding `policy_hash: fa24fb305126805cf2164c161d852a0e7330cf988f1fe558cf7d4a64`,
re-signed, and resubmitted.

## How-to Recreate Examples

Each example is two artifacts with a one-way dependency:

- the **metadata document** (`*.jsonld`), whose `body.onChain` describes the on-chain effect
- the **on-chain effect** (a proposal, vote, or certificate) that carries an `anchor` pointing back at that document.

### Part A — the metadata document

#### 1. Assemble `example.jsonld`'s `body`

Author the document with its inlined merged `@context` (downstream body vocabulary +
`onChain`), then take a copy containing only `@context` and `body`.

#### 2. Canonicalize the `body`

Using a [RDF Dataset Canonicalization (URDNA2015)](https://w3c-ccg.github.io/rdf-dataset-canonicalization/spec/)
tool — e.g. the [JSON-LD Playground](https://json-ld.org/playground/) or the `jsonld` npm
package — produce the canonical N-Quads of `{ "@context": …, "body": … }`. Ensure the result
ends in a newline. Because the context uses `@vocab` inside `onChain`, every on-chain field
appears in the output; if a field is missing, the binding is incomplete.

#### 3. Hash the canonicalized `body`

Blake2b-256 the canonical N-Quads. This is the "canonicalized body hash" listed per-example
and is the payload the authors sign.

#### 4. Each author witnesses the body hash

For a `witnessAlgorithm` of `ed25519`, sign the body hash from step 3 with the author's key
(see [Authors](#authors)). Put the result in `authors[].witness.signature`. For a multi-author
document, every author signs the *same* body hash.

#### 5. Complete `example.jsonld`

Add `hashAlgorithm: "blake2b-256"` and the populated `authors` array back to the document.

#### 6. Hash `example.jsonld`

Blake2b-256 the whole file's content — this is the "file content hash" that goes on-chain as
the metadata anchor hash alongside the document's URI.

#### 7. Validate

Validate the document against the schema (see [Validation](./README.md#validation)) and, for a
full check, re-run steps 2–4 and confirm each `signature` verifies against its `publicKey` and
the recomputed body hash.

### Part B — the on-chain effect (Preview)

The Preview effects were built with [`cardano-cli`](https://github.com/IntersectMBO/cardano-cli). The resulting text envelopes are checked in beside each document in
[`examples/preview/`](./examples/preview/): `*.action` (proposals), `*.vote` (votes), and
`*.cert` (certificates), each with a human-readable `*.json` view.

#### 1. Reuse the document's parameters

Take the exact values encoded in `body.onChain` — deposit, return / reward account, governance
action contents, DRep or committee credential, target gov action id, vote decision — so the
submitted effect is byte-for-byte the effect the authors signed over. Everything in `onChain`
maps to a `cardano-cli` argument.

#### 2. Supply the anchor

The anchor is the *only* field not mirrored in `onChain`. Point it at the finished document: the
IPFS URL where it is pinned plus its file content hash from [Part A step 6](#6-hash-examplejsonld).

#### 3. Create the effect

Use the `cardano-cli` command to build the action, vote or certificate.

#### 4. Build, sign, and submit the transaction

Wrap the `.action` / `.vote` / `.cert` into a transaction with `cardano-cli`.
The resulting transaction hash and gov action id are the values listed in the [Live Examples](#live-examples-preview-testnet) tables.

#### 5. Confirm the binding holds

Fetch the document from its on-chain anchor and run the
[Verification Process](./README.md#verification-process): the anchor hash must equal the
document's file content hash, and `body.onChain` (with the self-referential anchor dropped) must
equal the effect re-derived from the submitted transaction.
