---
CIP: TBD
Title: Merkle Patricia Trie Root of Transactions in Cardano Block Header
Category: Ledger
Status: Proposed
Authors:
  - Alexander Slesarenko <alex.slesarenko@iohk.io>
  - Philip DiSarro <philip.disarro@iohk.io>
Implementors: []
Discussions:
  - https://github.com/cardano-foundation/CIPs/pull/964
Created: 2025-03-27
License: CC-BY-4.0
---

## Abstract

This CIP introduces a **Merkle Patricia Trie (MPT) root** committing to the transactions of each
block header for the upcoming Dijkstra ledger era. Concretely, it extends the Cardano block header
(`HeaderBody`) with an additional 32-byte root hash representing a **hexary (radix‑16) Merkle
Patricia Trie** over the block’s transaction identifiers.

By committing to an MPT root in the header, Cardano blocks can support efficient **transaction
inclusion proofs** (analogous to Bitcoin SPV proofs and Ethereum transaction/receipt proofs) without
requiring full block body download. The MPT design is widely deployed in other blockchains (notably
Ethereum), is compatible with nibble-based proof verification, and is amenable to compact proofs and
incremental construction.

This proposal specifies the header changes, CBOR encoding updates, consensus-critical computation of
the root from the block’s transactions, and deployment via a Dijkstra-era hard fork.

## Motivation: why is this CIP necessary?

> NOTE (CPS linkage): This proposal originated as a CPS in PR #964 (“CIP-???? | Merkle Root of
> Transactions in Block Header”). The CIP process recommends that complex proposals link a CPS as
> motivation; at the time of writing, the CPS identifier for this work is not finalized in the PR.

### The need for time-bound inclusion proofs

Currently, each block header contains a *block body hash* (`hbBodyHash`) that commits to the entire
block body, but it does not enable succinct per-transaction membership proofs without providing (or
rehashing) the entire body.

```haskell
-- | The body of the header is the part which gets hashed to form the hash chain.
data HeaderBody crypto = HeaderBody
{ hbBlockNo  :: !BlockNo
, hbSlotNo   :: !SlotNo
, hbPrev     :: !(PrevHash crypto)
, hbVk       :: !(VKey 'BlockIssuer crypto)
, hbVrfVk    :: !(VerKeyVRF crypto)
, hbVrfRes   :: !(CertifiedVRF crypto InputVRF)
, hbBodySize :: !Word32
, hbBodyHash :: !(Hash crypto EraIndependentBlockBody)
, hbOCert    :: !(OCert crypto)
, hbProtVer  :: !ProtVer
}
```

Consequences:

1. **No direct inclusion proofs**
   Light clients, bridges, or external verifiers cannot confirm a transaction’s inclusion without
   downloading and hashing the full block body.

2. **No simple time-bound transaction proofs**
   Even if a transaction can be certified by an external scheme, it is not automatically anchored
   to a specific header’s slot/block number without introducing new bundled certification types.

3. **Ecosystem friction and ad-hoc workarounds**
   Projects must rely on trusted indexers/servers, or invent bespoke “transaction+header” proofs,
   instead of using a standard protocol-level primitive.

### Use cases enabled by a transaction-root in headers

- **Light clients (SPV-like):** sync headers only, request an inclusion proof for a TxID, verify it
  against the header root.
- **Cross-chain verification / bridges:** other systems can verify that a Cardano TxID is included
  in a particular Cardano block, given a trusted header chain (or a header certification layer).
- **Timestamped proofs of existence:** inclusion proofs anchored to a header provide a compact,
  time-bound proof that some data existed by the slot time.
- **Synergy with header certification schemes:** if the ecosystem later certifies headers (e.g.,
  via aggregated signatures), the same inclusion proofs become fully trust-minimized.

### Goals

1. Enable efficient per-transaction inclusion proofs.
2. Preserve slot/block context in the authenticated object (the header).
3. Avoid ad-hoc bundling of transaction data with headers.
4. Provide a foundation for future header certification.
5. Support light clients, interoperability protocols, and auditors with compact proofs.

## Specification

### 1. HeaderBody structure changes

We introduce a new field in the block header body that commits to the block’s transactions via an
MPT root:

```haskell
data HeaderBody crypto = HeaderBody
  { hbBlockNo      :: !BlockNo
  , hbSlotNo       :: !SlotNo
  , hbPrevHash     :: !(HashHeader crypto)
  , hbIssuer       :: !(VKey 'BlockIssuer crypto)
  , hbVrfVk        :: !(VerKeyVRF crypto)
  , hbVrfResult    :: !VRFResult crypto
  , hbBodySize     :: !Natural
  , hbBodyHash     :: !(Hash crypto (TxSeq crypto))
  , hbOCert        :: !(OCert crypto)
  , hbProtVer      :: !ProtVer
  , hbTxTrieRoot   :: !(Hash crypto TxTrie)   -- NEW: MPT root committing to transactions
  }
```

- `hbTxTrieRoot` is a 32-byte hash, consensus-critical.
- `TxTrie` is a conceptual type meaning “the transaction trie committed by the header root”.

### 2. What is committed: a Transaction MPT

This CIP commits to the **ordered transaction IDs in the block**, organized in a deterministic
**Merkle Patricia Trie**.

**Keying rule (deterministic):**
- Let the transactions in the block body be ordered as `tx[0..N-1]` in the block’s canonical order.
- Compute each transaction’s identifier `txid[i]` (32-byte hash, as used in the ledger).
- Construct an MPT whose keys are the **transaction indices** encoded canonically, and whose values
  are the corresponding `txid[i]`.

Rationale for index-keying:
- Matches the dominant “transaction trie” pattern used in other blockchains (e.g., Ethereum keys
  transactions by index), yielding natural inclusion proofs that also pin the transaction’s position
  in the block.
- Avoids ambiguities around duplicate keys or order-independence; the block order is already
  consensus-defined, and the trie commitment reflects it.

**Canonical key encoding (consensus-critical):**
- The key for index `i` MUST be `cbor(i)` (CBOR encoding of the unsigned integer `i`).
- The trie operates on the **nibble expansion of the key bytes**: each byte is split into two 4-bit
  nibbles to walk a radix-16 trie.

**Leaf value (consensus-critical):**
- The leaf value for index `i` MUST be the raw 32-byte `txid[i]`.

**Empty-block root (consensus-critical):**
- If a block has zero transactions (`N = 0`), the trie is empty and the root MUST be:
  `emptyRoot = H(cbor([]))`,
  where `H` is the era-defined 32-byte header commitment hash and `cbor([])` is the canonical CBOR
  encoding of the empty array (single byte `0x80`).

### 3. Trie node format and hashing

To ensure independent implementations converge, the trie node encoding and hashing are
consensus-critical.

This CIP proposes a “Cardano MPT” variant:

- **Trie shape:** hexary Merkle Patricia Trie (radix‑16), with path compression (extension nodes)
  and branch nodes.
- **Node encoding:** CBOR encoding of node variants (branch / extension / leaf).
- **Hash function:** the era’s standard 32-byte hash for header commitments (intended: Blake2b‑256),
  applied to the CBOR-encoded node.
- **Inlining rule (optional but MUST be specified if used):**
  - EITHER: always hash child nodes and store only 32-byte hashes in parents (simple, fixed-size),
  - OR: follow an “inline if short, hash if long” rule (Ethereum-like).
  - This CIP RECOMMENDS the always-hash rule for simplicity and predictable proof structure.

> NOTE: If the ledger mandates a particular hash or header-commitment scheme for Dijkstra era, that
> choice MUST be reflected here. The critical requirement is a fully specified, deterministic
> node-hashing procedure.

### 4. Consensus validation rule

For every Dijkstra-era block:

1. Extract the ordered transaction sequence from the block body.
2. Compute `txid[i]` for each transaction.
3. If `N = 0`, set `root = emptyRoot` as defined above; otherwise build the Transaction MPT as
   specified and set `root` to its root hash.
4. Validate `root == hbTxTrieRoot`.

If the check fails, the block is invalid.

### 5. Block header serialization changes (CBOR / CDDL)

The new `tx_trie_root` is appended to the `header_body` CBOR array for Dijkstra-era blocks.

```cddl
; Block header structure for Dijkstra era (CBOR)
block_header = [ header_body, header_signature ]

header_body = [
  block_number:      uint,
  slot_number:       uint,
  prev_header_hash:  bytes .size 32 / null,
  issuer_vkey:       bytes,
  vrf_vkey:          bytes,
  vrf_output:        bytes,
  block_body_size:   uint,
  block_body_hash:   bytes .size 32,
  op_cert:           bytes,
  protocol_version:  [uint, uint],
  tx_trie_root:      bytes .size 32          ; NEW
]

header_signature = bytes
```

**Era gating / decoding:**
- Dijkstra-era headers MUST include the new field (11-element `header_body`).
- Pre-Dijkstra eras retain their previous header format.
- The Hard Fork Combinator era tag (and/or `ProtVer`) selects the correct codec.

### 6. Proof format (non-consensus, but interoperable)

This CIP introduces the commitment (`hbTxTrieRoot`). Proof exchange can follow established MPT proof
patterns:

- A proof is a sequence of trie nodes (CBOR-encoded) along the path from the root to the leaf for
  the transaction index key.
- Verification recomputes hashes up the path and checks that the resulting root equals
  `hbTxTrieRoot`, and that the leaf value equals the expected `TxId`.

The on-wire/API encoding of proofs is not consensus-critical, but should be standardized by tooling
to ensure interoperability.

## Rationale: how does this CIP achieve its goals?

### Why a transaction commitment in the header?

A header-level transaction commitment enables succinct inclusion proofs anchored to consensus time
(slot/block number) and allows light clients and external verifiers to validate inclusion without
retrieving whole blocks. The existing `hbBodyHash` does not support efficient per-transaction proofs.

### Why a Merkle Patricia Trie?

Merkle Patricia Tries are a proven, widely deployed authenticated data structure for blockchain
commitments:

- **Efficient inclusion proofs:** Proofs are logarithmic in the key length (nibble path), and are
  typically compact for realistically sized blocks.
- **Incremental construction:** A block producer can build the trie as it assembles the block.
- **Interoperability and familiarity:** MPT proofs and implementations exist across ecosystems,
  and the structure is well-studied.

This CIP uses an MPT over transaction indices to mirror “transaction trie” patterns in other
blockchains, while tailoring node encoding/hashing to Cardano’s serialization and hash primitives.

### Backward compatibility and deployment

This is a consensus-breaking change deployed via a Dijkstra-era hard fork. Pre-Dijkstra blocks
remain unchanged and continue to decode under their legacy formats. Dijkstra-era headers include one
additional 32-byte field.

## Path to Active

### Acceptance Criteria

- [ ] Ledger and consensus compute the Transaction MPT root deterministically and validate it for
      every Dijkstra-era block, including the `N = 0` empty-block case.
- [ ] Dijkstra-era header/body codecs are updated to include `tx_trie_root`, while pre-Dijkstra
      decoding/validation remains unchanged and backward compatible.
- [ ] Block-producing node implementations used in production can forge and validate blocks with
      `hbTxTrieRoot` enabled at the hard-fork boundary.
- [ ] Conformance test vectors are published and at least two independent implementations agree on
      roots/proofs for the same blocks.
- [ ] A public testnet rehearsal demonstrates stable operation across the era transition with no
      consensus divergence attributable to the new commitment.

### Implementation Plan

- **Ledger library:** add `hbTxTrieRoot` to the Dijkstra-era header type, implement `calcTxTrieRoot`
  and validate it in the block rule.
- **Consensus / node:** integrate root computation into block forging; update codecs and era
  transitions.
- **Tooling:** update `cardano-api`, `cardano-serialization-lib`, explorers, and parsers to read and
  expose `tx_trie_root`.
- **Testing:** unit tests for known vectors; property tests comparing multiple implementations; a
  testnet fork rehearsal validating post-fork blocks.

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
