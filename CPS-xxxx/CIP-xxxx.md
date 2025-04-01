---
CPS: ????
Title: Merkle Root of Transactions in Cardano Block Header
Status: Open
Category: Ledger
Authors:
  - Alexander Slesarenko <alex.slesarenko@iohk.io>
  - Philip DiSarro <philip.disarro@iohk.io>
Implementors: []
Discussions: 
  - [PR](https://github.com/cardano-foundation/CIPs/pull/964)             
Created: 2025-03-27
License: CC-BY-4.0
---

## Abstract
This CIP introduces a **Merkle root of all transaction IDs** into the
block header for the upcoming Dijkstra ledger era. It proposes extending the Cardano block header
(specifically the `HeaderBody` structure) with a **Patricia-Merkle root** of transaction
identifiers. By committing to a Merkle root in each header, Cardano blocks can support efficient
**transaction inclusion proofs** (analogous to Bitcoin’s SPV proofs ([the block in blockchain
explained (merkle
trees)](https://haroldcarr.com/posts/2017-07-31-the-block-in-blockchain-merkle-trees.html#:~:text=data%20BlockHeader%20%3D%20BlockHeader%20,deriving%20%28Eq%2C%20Show)))
without relying on full block data. We leverage the **Merkle Patricia Forestry** trie structure
(already used in Plutarch and Aiken libraries) to minimize proof sizes and ensure compatibility with
on-chain smart contract verification. The proposal details the necessary changes to the in-memory
Haskell ledger structures and the CBOR encoding of block headers, and discusses rationale such as
proof-size efficiency, light client support, cross-chain verification, and backward compatibility.

## Motivation
**The need for on-chain inclusion proofs:** Currently, while each block header does contain a *block
body hash*, it’s computed in a way that doesn’t easily support per-transaction proofs. 

```haskell
-- | The body of the header is the part which gets hashed to form the hash
-- chain.
data HeaderBody crypto = HeaderBody
{ -- | block number
hbBlockNo  :: !BlockNo,
-- | block slot
hbSlotNo   :: !SlotNo,
-- | Hash of the previous block header
hbPrev     :: !(PrevHash crypto),
-- | verification key of block issuer
hbVk       :: !(VKey 'BlockIssuer crypto),
-- | VRF verification key for block issuer
hbVrfVk    :: !(VerKeyVRF crypto),
-- | Certified VRF value
hbVrfRes   :: !(CertifiedVRF crypto InputVRF),
-- | Size of the block body
hbBodySize :: !Word32,
-- | Hash of block body
hbBodyHash :: !(Hash crypto EraIndependentBlockBody),
-- | operational certificate
hbOCert    :: !(OCert crypto),
-- | protocol version
hbProtVer  :: !ProtVer
}
```

Consequently:

1. **No direct inclusion proofs**  
   Light clients, cross-chain bridges, or other verifiers cannot confirm a transaction’s membership in a block without downloading and hashing the entire block body.

2. **Lack of time-bound transaction proofs**  
   Even though schemes like Mithril can certify transactions individually, these transactions lack any temporal link to a specific block header. Block headers in Cardano provide time information (via slot and block numbers), but they are not themselves certified in Mithril. As a result, there is no simple way to prove a transaction was included at a particular point in chain history without referencing full blocks.

3. **Inefficient or ad-hoc workarounds**  
   An alternative is to package `(transaction, header)` as an entirely new certified data type to link transaction hashes with time data. However, this is a patchwork approach and does not solve the fundamental omission of a transaction root in the block header. A cohesive protocol-level fix is preferable to ad-hoc solutions.

4. **Underutilized opportunities for synergy with Mithril**  
   Although Mithril provides a powerful framework for certifying various data types, it currently does not offer “header certificates.” If Cardano’s block headers included a transaction root, then adding a corresponding header certification in Mithril would unlock more robust, lightweight proofs of time-bound transaction inclusion.

### **Use cases driving this proposal:** 
By adding a Merkle root of transaction IDs (TXIDs) to block headers, we enable:

- **Light client support (SPV):** A light node or wallet can download only block headers and still
  verify that a transaction was confirmed by requesting a Merkle proof from a full node.
  The light client checks the proof against the header’s Merkle root (which it trusts as part of the
  longest valid chain) to confirm inclusion, without needing the entire block. This reduces
  dependence on trusted servers and enhances decentralization of wallet and L2 infrastructure.

- **Cross-chain verification and bridges:** Other blockchains or sidechains can verify Cardano
  transactions by inspecting Cardano headers and Merkle proofs. For example, a bridge smart contract
  on another chain (or a sidechain consensus) could hold the latest Cardano block header (via an
  oracle or relay) and use the Merkle root to validate proofs of Cardano transactions, enabling
  **trustless cross-chain bridges** ([Merkle Patricia Tries: Dive into Data Structure
  Security](https://cardanofoundation.org/blog/merkle-patricia-tries-deep-dive#:~:text=amount%20of%20data%20and%20computing,Github%20stats%20directly%20on%20chain)).

- **Timestamped proofs of existence:** Inclusion in a Cardano block provides a timestamp (via the
  slot number/time of that block). By presenting a transaction’s Merkle inclusion proof anchored in
  a block header, one can prove a piece of data or event existed on Cardano at a certain time,
  without revealing the entire block. This could be useful for auditing, legal evidence of document
  existence, or any scenario requiring a *compact and timestamped proof* of storage on Cardano.

- **Complementing Mithril and other solutions:** Mithril provides aggregated signatures to verify
  **state** snapshots efficiently ([Understanding Mithril | Cardano
  Explorer](https://cexplorer.io/article/understanding-mithril#:~:text=Mithril%20will%20enable%20the%20creation,a%20more%20scalable%20blockchain%2C%20etc)),
  but it does not by itself allow verifying inclusion of individual transactions in a specific
  block. A Merkle root in block headers is a simpler, complementary primitive that directly
  addresses transaction inclusion proofs. It can work in tandem with Mithril (e.g., [Mithril could
  certify checkpointed headers](https://github.com/input-output-hk/mithril/issues/2242)) to enable
  fully trustless light clients and sidechain verifiers.

### Goals

1. **Enable Efficient Inclusion Proofs**  
   Add a Merkle-like commitment to the header so that transaction membership can be verified with
   minimal data.

2. **Preserve Time/Slot Context**  
   Retain the existing Cardano notion of time (slot or similar) in the certified entity to allow proofs
   of “when” a transaction was included.

3. **Avoid Ad-hoc Bundling**  
   Eliminate the need for special data types that bundle transaction data with a block header,
   preventing proliferation of patchwork solutions.

4. **Lay Foundation for Header Certification**  
   Provide a clear path for Cardano’s broader ecosystem (e.g., Mithril) to introduce “header
   certificates,” so that verifying a transaction inclusion proof also entails trusting its position in
   chain history.

5. **Support Ecosystem Growth**  
   Foster new use cases (light clients, cross-chain protocols, specialized auditors) that rely on
   compact, time-bound proofs.


In summary, this CIP aims to improve **Cardano’s interoperability and light client capabilities** by
aligning with a proven design used in other blockchains (e.g. Bitcoin block headers include a Merkle
root for SPV). 

## Specification

### HeaderBody Structure Changes
We introduce a new field in the Cardano block header’s body to commit to the transactions in the
block. In the existing implementation, a block header (specifically the `HeaderBody`) contains
fields shown in the listing above. (see also [Understanding block minting in Cardano | Cardano
Explorer](https://cexplorer.io/article/understanding-block-minting-in-cardano#:~:text=,transaction%20and%20data)).
We propose to add a **new field** for the *Merkle root of all transaction IDs*.

Concretely, in the Cardano node’s Haskell code, the `HeaderBody` data structure will be extended:

```haskell
data HeaderBody crypto = HeaderBody {
    hbBlockNo      :: !BlockNo,                   -- Block number
    hbSlotNo       :: !SlotNo,                    -- Slot number
    hbPrevHash     :: !(HashHeader crypto),       -- Prev header hash
    hbIssuer       :: !(VKey 'BlockIssuer crypto),-- Block issuer’s VKey
    hbVrfVk        :: !(VerKeyVRF crypto),        -- VRF verification key
    hbVrfResult    :: !VRFResult crypto,          -- VRF output (leader proof)
    hbBodySize     :: !Natural,                   -- Block body size in bytes
    hbBodyHash     :: !(Hash crypto (TxSeq crypto)),  -- Existing block body hash
    hbOCert        :: !(OCert crypto),            -- Operational certificate
    hbProtVer      :: !ProtVer                    -- Protocol version
    hbTxRoot       :: !(Hash crypto TxIdSet) ,    -- **New**: Merkle root of TXIDs
}
```

The new `hbTxRoot` is a 32-byte hash (of type `Hash crypto TxIdSet`) that represents the root of a
Merkle tree built over all transaction IDs in the block. The set of transaction IDs can be
considered as having the `TxIdSet` type (???). We use the **Merkle Patricia Forestry** structure
(explained below) to compute this root. Each transaction ID (TxId) in the block is inserted into a
Merkle Patricia Trie (radix-16 trie) and the root hash of that trie is placed in `hbTxRoot`.

This design choice means that `hbTxRoot` is deterministically computed by the block producer from
the block’s transactions. All Cardano nodes will independently compute and verify this
root as part of block validation (similar to how they compute and check `hbBodyHash` today). If the
computed root of the block’s TxIDs does not match the `hbTxRoot` in the header, the block is
invalid.

### Block Header Serialization Changes
Including the additional field requires an update to the block header serialization. Cardano block
headers are serialized in CBOR format. In previous eras (e.g. Babbage),
the header body might be encoded as a CBOR array of 10 elements (corresponding to the fields listed
above, excluding the signature). We propose to append the new **TxIDs Merkle root** field as an additional
element. This changes the expected length of the serialized header body array.

The **Concise Data Definition Language (CDDL)** for the new block header can be specified as
follows (noting new additions):

```cddl
; Block header structure for Dijkstra era (CBOR)
block_header = [ header_body, header_signature ]

header_body = [
  block_number:       uint,            ; BlockNo
  slot_number:        uint,            ; SlotNo
  prev_header_hash:   bytes .size 32 / null,  ; hash of previous header (32 bytes) or null for genesis
  issuer_vkey:        bytes,           ; block issuer’s VKey (Ed25519, ~32 bytes)
  vrf_vkey:           bytes,           ; VRF verification key
  vrf_output:         bytes,           ; VRF output (proof of leader election)
  block_body_size:    uint,            ; Size of block body in bytes
  block_body_hash:    bytes .size 32,  ; Hash of block body (existing field)
  op_cert:            bytes,           ; Operator’s KES operational certificate
  protocol_version:   [uint, uint]     ; Protocol version (major, minor)
  txids_merkle_root:  bytes .size 32,  ; **New field**: Merkle root of transaction IDs
]

header_signature = bytes               ; KES signature of the header body
```

The critical change is the insertion of the 32-byte `txids_merkle_root` as the 11th element in
`header_body` (at the end of the list). 

**Decoding/Encoding considerations:** A Dijkstra-era block header must include this field. Older-era
block headers (without `txids_merkle_root`) will continue to be decoded under their prior schema.
The presence of the new field is guarded by the **protocol version** and era context:
- The `protocol_version` field in the header (and the hard-fork combinator’s era tags) will signal
  to nodes that a block is Dijkstra-era and thus has the extra field. For example, if Dijkstra is
  introduced with protocol version *N*, any block with protocol version ≥ N will be expected to have
  the `txids_merkle_root` in its header.
- Cardano’s hard fork combinator will ensure that blocks from previous eras (Byron, Shelley,
  Allegra, Mary, Alonzo, Babbage, etc.) are decoded with their old format (10-field header body),
  whereas Dijkstra blocks use the new 11-field format.

Existing serialization libraries and tooling (e.g. cardano-serialization-lib, cardano-api) will need
to be updated to handle the new field. The addition will break compatibility with older decoders
that assume a fixed length. However, since this change corresponds with a deliberate era transition,
it is acceptable – nodes not upgraded to Dijkstra era will reject the new block format as unknown, the
same way they would reject any block from a future protocol version.

**Computing the Merkle root:** The Merkle root of transaction IDs is computed as follows. Let the
transactions in the block be `tx1, tx2, ..., txN`. We take the identifier (hash) of each transaction
– these are typically 32-byte hashes (TxIds). We insert each TxId as a key into a Merkle-Patricia
trie (radix 16). The trie does not store any value (or stores a constant placeholder) since we only
care about set membership. The resulting Patricia trie is then hashed down to produce a single
32-byte root hash. This hash is encoded in the header. Any consistent implementation of the trie
(with the agreed hashing algorithm) will produce the same root given the same set of TxIds, ensuring
consensus on the value.

**Hashing specifics:** We reuse Cardano’s existing cryptographic primitives for hashing. For
compatibility with Plutus on-chain verification and existing libraries, the hashing algorithm should
be Blake2b-256 (which is widely used in Cardano for addresses and script integrity hashes). The
Merkle-Patricia library in Aiken uses Blake2b for on-chain tries, which
should be aligned with this CIP. 

**Proof format:** While the CIP primarily concerns the addition of the root, it implies a standard
for the Merkle proof format (to be used by light clients and others). We adopt the Patricia Forestry
proof format already used by Aiken’s library: a proof consists of a series of hashed nodes and
sibling hashes organized possibly in subtrees. However, specifying the full proof serialization
format is out of scope for the CIP (as it doesn’t need to be on-chain). It’s expected that client
implementations will use the same library (or standard) to produce and verify proofs against the
header’s root. The important point is that **anyone can take a transaction ID and verify, against
the header, that it was included**, by reconstructing the trie path using the proof. This may
involve Plutus scripts (for on-chain verification in cross-chain applications) or off-chain code for
light wallets.

## Rationale

### Why include a Merkle root in block headers?
Including a transaction Merkle root in each block header brings Cardano in line with a
well-established best practice in blockchain design (used by Bitcoin, Ethereum, Ergo, and others) for
**efficient verification**. In Bitcoin’s design, the block header’s Merkle root allows SPV clients
to verify transactions with only the block header chain and a Merkle branch ([the block in
blockchain explained (merkle
trees)](https://haroldcarr.com/posts/2017-07-31-the-block-in-blockchain-merkle-trees.html#:~:text=The%20merkle%20root%20is%20a,that%20make%20up%20each%20transaction)).
As Cardano usage grows and cross-chain interactions become more important, the absence of an
inclusion proof mechanism has become a drawback and obstacle for many projects. 
This CIP directly addresses that by adding an **authenticable structure** for transactions.

The **alternatives** to this approach are less optimal:
  - Relying solely on the `block_body_hash` for inclusion proofs is not feasible, because that hash is
  a monolithic commitment. There is no standardized way to extract a subset proof; one would
  essentially have to provide all transactions to prove one transaction’s inclusion (defeating the
  purpose).
  - **Not doing anything (status quo)** leaves light clients insecure or overly reliant on trusted
  servers, which contradicts Cardano’s decentralization ethos.
  - Using an external scheme like **Mithril** for transaction proofs would be overkill: Mithril
  focuses on compressing chain state and history via stake-based signatures ([Understanding Mithril
  | Cardano
  Explorer](https://cexplorer.io/article/understanding-mithril#:~:text=Mithril%20will%20enable%20the%20creation,a%20more%20scalable%20blockchain%2C%20etc)),
  but still doesn’t give a per-transaction membership proof related to a point in time.
  - Another alternative could have been a **binary Merkle tree** of transactions (as in Bitcoin).
  While binary Merkle trees are simpler, they are less flexible for certain use cases (they rely on
  an implicit ordering of transactions) and proofs grow with log₂(N). For typical Cardano block
  sizes, binary Merkle proofs would be on the order of a few hundred bytes, which is comparable to
  our approach. However, as explained below, the Patricia trie approach offers additional advantages
  in a Cardano context (like on-chain verification and extensibility).

Given these considerations, adding an explicit Merkle root of TXIDs is the most straightforward and
**backwards-compatible** way to enable SPV proofs. It does not change any UTXO semantics or
transaction formats – it only augments the header, which is external to ledger state. Thus, it
cleanly separates the *chain security* improvement from the transaction processing logic.

### Why **Merkle Patricia Forestry** (Patricia Trie) instead of a simple binary Merkle tree?
We choose a **Patricia Merkle Trie** (specifically the Merkle-Patricia “Forestry” variant) for the
transaction authentication, for several reasons:

- **Efficient proof size scaling:** A naive binary Merkle tree proof requires sending all sibling
  hashes along the path, which in worst case is `log₂(N)` siblings for N leaves. With N up to a few
  thousand, this is on the order of 10–12 hashes (~384 bytes) for a proof – which is already quite
  good. However, if Cardano blocks were to grow larger (e.g., with input endorsers or other scaling,
  block could have many more transactions), binary proof size grows as O(log N). A radix-16 Patricia
  trie has a different trade-off: the depth is up to 64 nibbles (for 32-byte hashes as keys), but
  the **Merkle Patricia Forestry** optimization drastically reduces the number of siblings at each
  node. Instead of up to 15 sibling hashes at each trie node, siblings are grouped into a *sparse
  Merkle subtree*, requiring at most 4 hashes per level ([Merkle Patricia Tries: Dive into Data
  Structure
  Security](https://cardanofoundation.org/blog/merkle-patricia-tries-deep-dive#:~:text=The%20Merkle%20Patricia%20Forestry%20structure%2C,cost%20of%20verification%20increases%20marginally)).
  This yields proof sizes comparable to a binary Merkle tree even in worst-case depth. In fact,
  benchmarks from the Aiken library show that even for extremely large tries (up to 10^9 entries),
  proofs remain under ~1KB ([GitHub - aiken-lang/merkle-patricia-forestry:  Libraries (Aiken &
  Node.js) for working with Merkle Patricia Tries on
  Cardano.](https://github.com/aiken-lang/merkle-patricia-forestry#:~:text=trie%20size%20avg%20proof%20size,79M%20%280.56)).
  For context, a trie with 1000 entries (roughly a large Cardano block’s transaction count) might
  have proofs on the order of 300–500 bytes, which is very manageable.

- **On-chain verification capability:** The choice of Patricia trie is heavily influenced by the
  need for compatibility with Plutus smart contracts. Cardano’s smart contracts (Plutus) currently
  lack efficient bit-level operations,
  which makes verifying binary Merkle proofs on-chain more expensive. Ethereum’s solution to
  on-chain proofs was also to use a Patricia Trie (nibble-based) for its state, precisely to avoid
  large binary proofs in a system with many keys. By using a radix-16 trie, we align with existing
  Cardano on-chain libraries that implement Merkle tries. The **Merkle Patricia Forestry** library
  in Aiken provides Plutus-native support for verifying proofs of inclusion in a trie ([GitHub -
  aiken-lang/merkle-patricia-forestry:  Libraries (Aiken & Node.js) for working with Merkle Patricia
  Tries on Cardano.](https://github.com/aiken-lang/merkle-patricia-forestry#:~:text=Overview)). 
  Similarly, the Plutarch Merkle Tree project (Funded in Catalyst) provides Merkle verification
  capabilities in Plutus scripts ([GitHub -
  Anastasia-Labs/plutarch-merkle-tree](https://github.com/Anastasia-Labs/plutarch-merkle-tree#:~:text=The%20Plutarch%20Merkle%20Tree%20project,integrity%20and%20efficient%20data%20verification)).
  Using the same structure in the block header means a Plutus script on Cardano could, for example,
  verify that a given transaction (identified by TxId) was included in a certain block, by taking
  the block header’s `txids_merkle_root` (perhaps provided via an oracle or reference input) and a
  proof, and running the verification logic on-chain. This could open the door to *smart contracts
  reacting to main-chain events* in a trustless way, or **trustless sidechains** where Cardano
  mainnet proofs are verified by sidechain validators or contracts. In short, Patricia trie roots
  are **Plutus-friendly** in a way binary Merkle roots are not, due to available libraries and the
  nature of the data structure.

- **Dynamic set operations (future use):** While for this CIP we only require *static membership
  proofs* (the set of TXIDs in a block is fixed upon block creation), the Patricia trie structure
  allows naturally for extensions like insertions and deletions with proofs ([GitHub -
  aiken-lang/merkle-patricia-forestry:  Libraries (Aiken & Node.js) for working with Merkle Patricia
  Tries on Cardano.](https://github.com/aiken-lang/merkle-patricia-forestry#:~:text=Features)). The
  term “Forestry” refers to organizing the trie nodes in many small sparse Merkle trees, enabling
  efficient updates ([Merkle Patricia Tries: Dive into Data Structure
  Security](https://cardanofoundation.org/blog/merkle-patricia-tries-deep-dive#:~:text=The%20Merkle%20Patricia%20Forestry%20structure%2C,cost%20of%20verification%20increases%20marginally)).
  This might be useful for future Cardano features. For example, if we ever wanted to maintain a
  rolling **state commitment** (like a UTxO set Merkle root in each block), a similar structure
  could be used. Having support and familiarity with Patricia tries in the ecosystem now could pave
  the way for more advanced uses later (such as an on-chain domain name registry, sidechain state
  commitments, etc., which the Cardano Foundation has noted as potential use cases ([Merkle Patricia
  Tries: Dive into Data Structure
  Security](https://cardanofoundation.org/blog/merkle-patricia-tries-deep-dive#:~:text=amount%20of%20data%20and%20computing,Github%20stats%20directly%20on%20chain))).

- **Keyed structure (order-independence):** A minor but nice property of a trie of TxIDs is that it
  is agnostic to the order of transactions. In a binary Merkle tree, the position of a transaction
  in the list matters for the proof; if transactions are reordered, the Merkle root changes even if
  the set is the same. In a Patricia trie (used as a set), the root depends only on the set of
  TxIDs, not their order. Cardano blocks do not permit reordering without changing meaning (since
  order can affect scripts, fees, etc.), but the order-independence means our inclusion proof does
  not need to encode an index or path direction—just the key (TxId itself) guides the path. This
  simplifies verification logic and avoids any possibility of ambiguity about “which transaction”
  the proof is for (the proof explicitly includes the key at each step). It also means multiple
  transactions with the same prefix (e.g., very similar hashes) are handled gracefully via the trie
  branching.

**Why not stick with binary Merkle trees?** The main reason is to leverage the existing work done in
the Cardano community around Patricia tries. Ethereum’s success with Merkle Patricia Tries for not
just transactions but state is evidence that tries are robust for blockchain usage ([Merkle Patricia
Tries: Dive into Data Structure
Security](https://cardanofoundation.org/blog/merkle-patricia-tries-deep-dive#:~:text=The%20Merkle%20Patricia%20Trie%20,structure%20combining%20the%20strengths%20of)).
In Cardano’s case, a binary Merkle tree would certainly solve the basic inclusion proof problem, but
it would require introducing a separate proof-verification logic (likely off-chain only, since
on-chain binary Merkle verification would be costly without bit operations). By using
PatriciaForestry, we get a solution that is already optimized for Plutus on-chain verification and
has known proof-size characteristics.
The **Forestry** variant specifically was chosen because it *compresses the proofs significantly* by
bundling sibling hashes into small subtrees.
As a result, the difference in proof size between a binary tree and our radix-16 trie is minimal for
moderate N, and for very large N the trie remains efficient where a binary might become too large.

In summary, the rationale for using PatriciaForestry is to choose a **future-proof, efficient, and
Cardano-aligned** Merkle structure. It achieves nearly the same minimal proof sizes as an ideal
binary Merkle tree (because of the sparse hashing optimization), while offering better integration
with Cardano’s smart contract languages and potential for extended functionality.

### Light Clients, Cross-Chain Verification, and Inclusion Proofs
The primary goal of this CIP is to enable new functionalities around proofs of inclusion:

- **Light client (SPV) support:** With the Merkle root in place, a *trustless light wallet* mode
  becomes possible. A light client can synchronize the chain by downloading block headers (which are
  only hundreds of bytes each) and verify the chain’s correctness via the Ouroboros consensus rules (VRF
  checks, KES signatures, etc.). When the user wants to check the status of a
  transaction, the client can ask a full node for a Merkle proof of that TxID in the block it was
  supposedly included in. The client then checks that the provided proof hashes up to the
  `txids_merkle_root` in the known header of that block, confirming the transaction was indeed in
  the block.
  All of this can be done without trusting the full node (if the node lies, the proof won’t match
  the header root). Essentially, Cardano can support **Simplified Payment Verification** similar to
  Bitcoin’s, improving the decentralization of light wallets. Users could run a mobile wallet that
  doesn’t connect to a centralized server or require a full node – it only needs some block header
  source (which could even be P2P) and any peer for transaction proofs. This significantly lowers
  the barrier for secure Cardano usage on resource-constrained devices.

- **Cross-chain and sidechain verification:** By having transaction inclusion proofs, we open the
  possibility for **Cardano-to-other-chain communication**. For instance, consider a scenario where
  an Ethereum smart contract needs to know that a certain Cardano transaction happened (perhaps to
  release funds or trigger an event). Without this CIP, one would need to trust an oracle or a
  multi-sig group to attest the transaction occurred. With this CIP, it becomes feasible to design a
  protocol where Cardano block headers are regularly posted to Ethereum (either by an honest relay
  or via a client contract) and then a Merkle proof of the transaction can be verified against the
  posted header. The heavy lifting of Ouroboros consensus might still require some trust or
  aggregated signature (since Ethereum cannot easily verify VRFs and KES signatures without a lot of
  gas), but the **transaction inclusion** part can be trustlessly verified *given an accepted
  header*. A similar approach could be used for Cardano sidechains or layer-2s: the sidechain can
  include Cardano mainnet headers in its checkpoints, and prove mainnet transactions to sidechain
  smart contracts. The Cardano Foundation explicitly notes that structures like PatriciaForestry can
  “support solutions like trustless bridges between different blockchains” ([Merkle Patricia Tries:
  Dive into Data Structure
  Security](https://cardanofoundation.org/blog/merkle-patricia-tries-deep-dive#:~:text=amount%20of%20data%20and%20computing,Github%20stats%20directly%20on%20chain)).
  This CIP is a step toward such bridges, providing the cryptographic backbone (a commitment and
  proof system) needed for cross-chain communication.

- **Time-stamped inclusion proofs:** Every Cardano block header is associated with a **slot number**
  (and thus a timestamp, via the slot-to-time mapping). By proving a transaction’s inclusion in a
  block, one inherently proves it happened before the end of that slot (and roughly at the time of
  that slot, within a known margin). This is valuable for **timestamping applications**. For
  example, imagine proving in a court or to a patent office that a document was committed to the
  blockchain at or before a certain date – one could embed a hash of the document in a Cardano
  transaction, and later provide the Merkle proof of that transaction in block X along with the
  block’s timestamp from Cardano’s timeline. Because Cardano’s consensus is secure, that is as good
  as a notarization. Prior to this CIP, doing so would require producing the entire block or relying
  on a third-party to attest the transaction was in that block. With the Merkle root, the proof is
  succinct and self-contained. We anticipate use cases in data integrity and IoT as well, where
  devices might log events to Cardano and later produce inclusion proofs to auditors without sending
  large logs.

- **Improved fraud proofs / partial validation:** In the long run, having Merkle commitments in each
  block could enable **partial validation clients**. For instance, a client could choose to download
  only certain transactions (like those involving a set of addresses of interest) and still follow
  the chain by trusting that if anything was wrong, a proof could be generated. This strays into
  future territory, but the key is that a Merkle root makes the block content *commitment*
  first-class, so any discrepancy can theoretically be exposed by a proof of mis-inclusion or
  absence. This CIP directly enables **membership proofs** (a transaction is in the block). With
  some extensions, it could also enable *non-membership* proofs (a transaction is not in a given
  block, if the proof format is augmented appropriately), which might help in constructing more
  complex light-client protocols or fraud proofs for sidechains.

In summary, by adding this single 32-byte field, we empower the Cardano ecosystem with a versatile
cryptographic tool. It strengthens light clients and decentralizes access, fosters interoperability
via trust-minimized proofs, and offers new capabilities for timestamping and verification use cases.

### Backward Compatibility and Deployment Strategy
Introducing a new field in the block header is a **consensus-breaking change**, meaning all nodes
must upgrade to understand and produce the new header format. However, due to Cardano’s use of
**hard fork combinator** (HFC), this change can be deployed in a controlled, backward-compatible
manner at the network level.

**Backward compatibility for older blocks:** Blocks from all pre-Dijkstra eras remain valid and
unchanged. This CIP does **not** retroactively add Merkle roots to existing blocks (since that is
impossible without altering history). For blocks before the upgrade, the `txids_merkle_root` field
is simply *absent*. In implementation, this will be handled by context: the ledger will know that,
e.g., all blocks with protocol version less than `ConwayMajor` have a header without the new field.
We can conceptualize that in a unified way by treating the field as `Maybe Hash` (optional) where
it’s `Nothing` for old blocks and `Just merkleRoot` for new blocks. But practically, separate data
types or parsing depending on era will be used. This means there is no impact on historical data or
block storage – older blocks maintain their original binary format and hashes.

**Ensuring a smooth hard fork:** To deploy, the following will occur:
- The change will be implemented in Cardano Node (ledger and consensus code). It will likely be
  bundled with other Dijkstra-era changes (for instance, CIP-1694 governance changes) as part of a
  major release. The protocol version in the software will be bumped (e.g., from protocol version 8
  to 9, hypothetically).
- During the hard fork transition epoch, once the required majority of stake is running the new node
  version, the protocol transition to Dijkstra era will be triggered. From that point on, block
  producers will start including the `txids_merkle_root` in new block headers. All nodes that have
  upgraded will accept these blocks and verify the Merkle root; any node that has not upgraded will
  reject these blocks (since the header does not match the expected older format) and will fall off
  the main chain. This is the normal behavior of an intended hard fork – it’s an *opt-in upgrade*
  enforced by consensus rules.
- **No explicit downtime or manual intervention** is needed beyond upgrading nodes. Thanks to the
  HFC mechanism, the ledger can seamlessly switch to the new format at the boundary of an epoch.
- **Old clients and tools:** Wallets and exchanges that use Cardano node or cardano-wallet
  indirectly will just need to upgrade to the Dijkstra-compatible version – they typically do so for
  every hard fork. If a tool directly parses block data (e.g., a block explorer that decodes CBOR),
  it will need to be updated to account for the new field. If not updated, it might display
  incorrect block information or crash when encountering a Dijkstra block header. Part of the
  deployment will involve communicating this change to such infrastructure providers well in
  advance.

**Optional adoption for historical usage:** While the network will not have Merkle roots for past
blocks, we note that it’s *optionally* possible for third-party services to compute Merkle roots for
old blocks and supply them to interested clients. For example, a block explorer, a community tool or
Mithril network could publish a file (or certificate) of “backfilled” Merkle roots for all
pre-Dijkstra blocks (computed off-chain by taking each block’s transactions). A light client could use
those for inclusion proofs of older transactions (with the caveat that, since those roots aren’t
part of the blockchain, the client would have to trust the source of these backfilled roots, or
perhaps cross-verify them among multiple sources). This approach is out of scope for the CIP (which
concerns the consensus changes), but it’s worth noting for completeness: *after* this CIP, all new
blocks will have trustless inclusion proofs, and for old blocks one could still get unofficial
proofs if needed for historical data verification. We expect the need for verifying very old
transactions via SPV to be low, but the community could address it via such auxiliary projects if
desired.

**Impact on block propagation and validation performance:** Adding the Merkle root has minimal
impact on block propagation. The header grows by 32 bytes (which is negligible relative to typical
block sizes of, say, 4KB–80KB). Computing the Merkle root is efficient: it requires hashing each
transaction ID and combining them in the trie structure. The complexity is O(N * cost(hash)) for N
transactions (with a small overhead for trie pointers). In practical terms, if a block has 100
transactions, that’s 100 hash operations plus some overhead for node hashing; if a block has 2000
transactions, that’s 2000 hash ops, etc. Modern block producers can handle thousands of hashes per
second easily (they already perform cryptographic operations for signatures and script validation
far more expensive than this). Moreover, this computation can be done in parallel with other tasks:
as transactions are selected for a block, the node can incrementally build the Merkle trie.

During validation, a node will recompute the root from the received block’s transactions. This is
also a small overhead compared to verifying all those transactions (signatures, scripts, etc.). For
example, if verifying a block takes 500ms currently, computing the Merkle root might add only a few
milliseconds to that. Thus, the performance impact on node operation is minimal. Memory overhead is
also negligible – a few extra stack allocations for the trie, and storing one extra 32-byte value
per block in memory or disk.

### Acceptance and Activation
**Acceptance Criteria:** This proposal will be considered accepted and `Active` when it has been
implemented in the Cardano node, integrated into the Cardano Ledger/Consensus code for Dijkstra era,
and successfully deployed via a network hard fork. Specifically:
- The Cardano core development team (or contributing developers) must implement the new `HeaderBody`
  structure with the `txids_merkle_root` field and update the CBOR encoders/decoders accordingly.
- The implementation must be consistent across nodes such that all upgraded nodes agree on the
  computed Merkle root for a given block (this will be ensured by tests and by the determinism of
  the spec).
- The change should be covered by conformance tests: e.g., create a block in a test environment,
  ensure the Merkle root in the header matches an independently computed root for that block’s
  transactions, test parsing/serialization, etc.
- Consensus of the community and stake pool operators to activate the change via a hard fork (likely
  through governance processes or CIP-1694 once in place) must be achieved. In practice, this means
  the new node release is widely adopted by SPOs.
- When the hard fork occurs, the first Dijkstra block that includes the Merkle root is successfully
  accepted by the network majority, marking the feature as live. At that point, the CIP status can
  move from *Proposed* to *Active*.

**Measure of success:** After activation, light client implementations should be able to retrieve
Merkle proofs from full nodes (by introducing a Cardano-node RPC or P2P method to get a proof for
a tx by id and block, if one isn’t already available) and verify them against the headers.
Additionally, block explorer APIs could start providing inclusion proofs on demand. These would
indicate that the ecosystem is utilizing the new capability.

### Implementation Plan
The implementation will involve coordinated changes across several components of the Cardano stack:

- **Cardano Ledger Library:** Update the definition of the block header for the Dijkstra era. In the
  formal ledger specification, add the new field in the header body. Update or add a CDDL
  specification for the Dijkstra header (as provided above). Ensure the hash of the header
  (`hashHeader`) is defined to cover the new field as well (the header hash will naturally change
  because we hash the CBOR encoding of the header body + signature; including the new field in that
  ensures the header hash commits to the Merkle root too). The ledger rules (specifically the block
  validation rule) should be updated to compute `txids_merkle_root` from the `TxSeq` (sequence of
  transactions) and check it against the header value. A function like `calcTxIdsRoot(txSeq) ->
  Hash` will be added and invoked in the Block validation rule.

- **Ouroboros Consensus / Cardano Node:** Update the consensus code that constructs blocks (the
  block forging logic) to compute the Merkle root and include it in the header. Block forging
  already computes the body hash and other fields; the trie computation can be integrated there. Use
  the existing crypto library (or incorporate the Aiken Merkle trie implementation in Haskell) for
  building the trie of TxIDs. The node’s decoder for blocks must handle the new field – since the
  consensus layer often uses an era tag to pick the decoder, this will likely be straightforward
  (define a new codec for Dijkstra headers). We must also bump the protocol version number that is
  embedded in the block header (the `ProtVer` field) to indicate this new format. For example, if
  the previous era had protocol version N, Dijkstra could use N+1; the node’s consensus logic uses
  this to know when to switch encoding.

- **Serialization libraries and APIs:** The Cardano API (which wallet backend and exchanges use)
  will expose a new data constructor or field for the block header. For instance, in cardano-api’s
  BlockHeader type, there will be something like `BlockHeaderConway { headerBodyConway ::
  HeaderBodyConway, signature :: KESSignature }`. The cardano-serialization-lib (Rust) will need a
  new version release that can decode/encode the Dijkstra header with the extra field. This typically
  involves adding new branches in their enum for block era. Tests vectors should be created to
  ensure third-party libraries can validate the new format (for example, a known block’s CBOR and
  its fields).

- **Backward compatibility in code:** The new field will be implemented in a way that does not break
  handling of older eras. Likely approach is to use pattern matching on the era to decide if
  `txids_merkle_root` is expected or not. In Haskell, this might mean `HeaderBody` becomes an
  era-parametrized GADT or there are separate types like `HeaderBodyBabbage` vs `HeaderBodyConway`.
  The node already has infrastructure for multi-era support (through the `HardForkBlock` type).
  We leverage that to introduce `ConwayBlock` type that includes the new field. The hard fork
  combinator will be configured to transition at the epoch boundary once the protocol version is
  updated.

- **Testing and Testnet rollout:** Once implemented, the feature will be tested in several stages.
  Unit tests in the ledger should check that for a given list of mock transactions (with known
  hashes), the computed `hbTxRoot` is correct. Property tests might generate random sets of TxIDs
  and compare the trie root from our implementation with an independent implementation (e.g.,
  cross-check with the Aiken off-chain JavaScript library for Merkle Patricia Forest). Integration
  tests will run a local cluster of nodes in multiple eras, ensuring that before the fork blocks
  have no `txids_root` and after the fork they do, and that a node that didn’t upgrade indeed
  rejects the new blocks (to simulate the importance of upgrade). Next is a testnet deployment
  (likely an ad-hoc testnet or the preview testnet) where the hard fork can be triggered at will to
  observe the behavior in a live setting. Light client prototype implementations (maybe in
  cardano-cli or other tools) should be used to fetch proofs from a testnet full node and verify
  them.

- **Documentation and adoption:** Update the CIP documentation (this document) status accordingly,
  and communicate with the community. Wallet developers should be informed how they can utilize the
  new capability. CLI command might be introduced or node RPC like `cardano-cli query
  tx-inclusion-proof --tx <txid> --block <hash_or_number>` that returns the proof in some format
  (maybe JSON). Also, Cardano’s networking protocol could be extended (e.g., a mini-protocol for
  chain-sync could have an option to request inclusion proofs or an existing protocol like
  TxSubmission might be extended).

- **Deployment in a hard fork event:** Coordinate with IOG, Cardano Foundation, and SPOs to schedule
  this change in a hard fork (likely the Dijkstra hard fork). The activation epoch and protocol
  version are decided and announced. SPOs upgrade nodes, and the hard fork occurs as planned.

- **Post-deployment monitoring:** After activation, monitor that blocks are being produced with
  non-null Merkle roots and that no unexpected issues arise (e.g., if a bug caused inconsistent
  Merkle root calculation, the chain would split – tests should prevent this). If all goes well, the
  feature is fully live.

This implementation plan assumes that the core developers and stake pool operators are on board with
the change. The change is self-contained and does not require changes from ADA users or exchanges
beyond normal node upgrades. 

By following this plan, we ensure that the introduction of the transaction ID Merkle root is done
safely, with thorough testing, and with minimal disruption to the existing ecosystem. Once deployed,
Cardano will have improved capabilities for light clients and interoperability.

## References

- Cardano block header fields (block number, slot, prev hash, issuer, VRF output/proof, block size,
  body hash, op-cert, protocol version) are described in Cardano Explorer documentation
  ([Understanding block minting in Cardano | Cardano
  Explorer](https://cexplorer.io/article/understanding-block-minting-in-cardano#:~:text=,transaction%20and%20data)).

- Light client and SPV concept for Cardano (and limitations of light nodes without inclusion proofs)
  ([Understanding Mithril | Cardano
  Explorer](https://cexplorer.io/article/understanding-mithril#:~:text=Light%20nodes%20are%20able%20to,and%20confirmed%20by%20the%20network)).

- Standard blockchain design (e.g., Bitcoin) includes a Merkle root in the block header for
  transaction inclusion verification ([the block in blockchain explained (merkle
  trees)](https://haroldcarr.com/posts/2017-07-31-the-block-in-blockchain-merkle-trees.html#:~:text=data%20BlockHeader%20%3D%20BlockHeader%20,deriving%20%28Eq%2C%20Show)).

- Merkle Patricia Trie (radix-16) combines a compressed trie with Merkle hashing. Cardano’s
  Merkle-Patricia “Forestry” variant optimizes proof sizes by using sparse Merkle trees reducing
  neighbors from 15 to 4 and keeping proofs compact. ([Merkle Patricia Tries: Dive into Data
  Structure
  Security](https://cardanofoundation.org/blog/merkle-patricia-tries-deep-dive#:~:text=The%20Merkle%20Patricia%20Trie%20,structure%20combining%20the%20strengths%20of));

- Merkle Patricia Forestry library (Aiken) demonstrates <1KB proofs for up to billions of elements
  ([GitHub - aiken-lang/merkle-patricia-forestry:  Libraries (Aiken & Node.js) for working with
  Merkle Patricia Tries on
  Cardano.](https://github.com/aiken-lang/merkle-patricia-forestry#:~:text=Features)) and outlines
  use cases of rapid membership proofs, insertions, deletions with a 32-byte root hash.

- Demonstration by Matthias Benkort (Cardano Foundation) of storing Bitcoin’s entire block header
  chain in a Merkle Patricia Forest on Cardano (850k+ headers compressed into a 32-byte root)
  ([Cardano Tech Lead Packs The Entire Bitcoin Blockchain Into One
  Block](https://www.mitrade.com/insights/news/live-news/article-3-194502-20240603#:~:text=UTxO%20containing%20the%20root%20hash,of%20over%20850%2C000%20blocks%20with)),
  showcasing the viability of this structure for large data.

- Plutarch Merkle Tree project provides Plutus support for Merkle tree verification in smart
  contracts ([GitHub -
  Anastasia-Labs/plutarch-merkle-tree](https://github.com/Anastasia-Labs/plutarch-merkle-tree#:~:text=The%20Plutarch%20Merkle%20Tree%20project,integrity%20and%20efficient%20data%20verification)),
  and Aiken’s on-chain library similarly supports Merkle Patricia trie verification, ensuring the
  chosen Merkle root scheme is verifiable on-chain within Cardano’s cost model.