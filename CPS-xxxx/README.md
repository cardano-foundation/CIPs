---
CPS: ????
Title: Lack of Concise Transaction Inclusion Proofs
Status: Open
Category: Ledger
Authors:
  - Alexander Slesarenko <alex.slesarenko@iohk.io>
Proposed Solutions: []
Discussions:
Created: 2025-01-17
License: CC-BY-4.0
---

## Abstract

Cardano’s block headers currently omit an explicit Merkle root (or equivalent data structure) for transactions. This omission prevents straightforward creation of compact transaction inclusion proofs, which are crucial for use cases that require trust-minimized verification. While existing solutions like Mithril can certify transaction data itself, they do not certify the header. Consequently, there is no proof that a transaction was included in a specific block at a specific time, unless the entire block is downloaded and verified. The absence of a transaction Merkle root in the header, in turn, reduces opportunities for flexible, lightweight proofs of transaction presence and position in time.

## Problem

Cardano headers do not expose a merkle root hash of all transactions included in a block. 
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

## Use Cases

1. **Light Clients**  
   A wallet that only stores minimal data could verify a single transaction’s presence in a particular block slot by checking a Merkle path against a certified header (if such header and root were available).

2. **Cross-Chain Interoperability**  
   A chain bridge that needs to confirm that a Cardano transaction occurred at a specific time in the ledger could rely on the block header’s Merkle root and a short proof. This eliminates the need for a full block download or complicated custom solutions.

3. **Auditing and Compliance**  
   Regulators or auditors can demand proof that a certain transaction took place during a specified window. Rather than reconstructing the entire chain, the verifier could rely on a succinct proof if headers include transaction roots and are optionally certified (e.g., via Mithril).

4. **Future Proof-of-Reserves and State Channels**  
   Services that want to prove partial ledger contents (e.g., balances or transaction sets up to a point in time) would benefit from having compact, time-stamped proofs of inclusion tied to a block header.

## Goals

1. **Enable Efficient Inclusion Proofs**  
   Add a Merkle-like commitment to the header so that transaction membership can be verified with minimal data.

2. **Preserve Time/Slot Context**  
   Retain the existing Cardano notion of time (slot or similar) in the certified entity to allow proofs of “when” a transaction was included.

3. **Avoid Ad-hoc Bundling**  
   Eliminate the need for special data types that bundle transaction data with a block header, preventing proliferation of patchwork solutions.

4. **Lay Foundation for Header Certification**  
   Provide a clear path for Cardano’s broader ecosystem (e.g., Mithril) to introduce “header certificates,” so that verifying a transaction inclusion proof also entails trusting its position in chain history.

5. **Support Ecosystem Growth**  
   Foster new use cases—light clients, cross-chain protocols, specialized auditors—that rely on compact, time-bound proofs.

## Open Questions

1. **Historical Compatibility**  
   Should this commitment scheme apply only to future blocks, or can a partial scheme be introduced for older blocks? Are “historical header certificates” needed or are they optional?

2. **Security Implications**  
   Are there new attack vectors introduced by splitting transaction verification across separate commitments (the existing block body hash vs. a new transaction root)? How would node operators and stake pool operators adapt?

3. **Integration with Mithril**  
   If headers carry transaction roots, what would a “header certificate” look like in Mithril? Would it become a new certified data type, and how would signers and aggregators handle it?

## Copyright

This Cardano Problem Statement is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).