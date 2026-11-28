---
CIP: ?
Title: ML-DSA-44 KES Leaf for Post Quantum Block Production
Category: Consensus
Status: Proposed
Authors:
  - Quantova Inc <https://github.com/quantova-inc>
Implementors: []
Discussions:
  - https://github.com/cardano-foundation/CIPs/pull/1300
Solution-To:
  - CPS-0030
Created: 2026-11-28
License: CC-BY-4.0
---

## Abstract

CPS-0030 asks what post quantum schemes fit the base settlement layer and names
KES as one of the three cryptographic primitives at risk. I propose replacing the
Ed25519 leaf of Cardano's KES with an ML-DSA-44 leaf under FIPS 204. The MMM sum
composition that Cardano already runs is leaf agnostic, so this gives a forward
secure post quantum block forging signature with no change to the tree. I give a
working reference instantiation, measured sizes and verify cost, a versioned leaf
encoding for agility, and the one protocol change this requires, a larger block
header limit.

## Motivation

Cardano block production signs each header with a key evolving signature so that a
compromised hot key cannot forge past blocks. Today the leaf of that KES is
Ed25519, which Shor's algorithm breaks. CPS-0030 ranks KES third of the three
settlement layer primitives at risk and leaves open which post quantum scheme
should take its place.

The KES construction is Sum6KES over an Ed25519 leaf with Blake2b_256 internal
nodes. This is source verified in cardano-base, Cardano.Crypto.KES.Sum, and the
ledger type KES StandardCrypto. The sum composition carries one real signature at
the active leaf. Every internal node verification key is a 32 byte Blake2b hash.
Only the leaf signature scheme is cryptographic. The MMM paper and CPS-0030 both
state the composition is agnostic to its leaf signature, so a post quantum leaf
substitutes directly and the forward security proof is preserved as long as the
leaf is existentially unforgeable.

## Specification

Replace the depth zero leaf of the KES with ML-DSA-44 under FIPS 204. Parameters
are public key 1312 bytes, signature 2420 bytes, secret key 2560 bytes, seed 32
bytes. Key generation takes the existing 32 byte KES seed path as the ML-DSA seed,
so the seed derivation of the sum tree is unchanged.

The signature serialization is unchanged in shape. A composed signature is the
sub signature followed by the two child verification keys. The two leaf public
keys appear once at the bottom level and every higher level carries a 32 byte
hash. A Sum6 signature under an ML-DSA-44 leaf is therefore

    leaf_sig 2420 + two leaf keys 2624 + five hash levels 320 = 5364 bytes

Verification is unchanged. Recompute each node hash up the path, check equality
with the operational certificate key, and verify the ML-DSA-44 signature at the
leaf.

Leaf scheme identifier. The operational certificate gains a two byte leaf scheme
id so the KES leaf can move to a later scheme without a second format break. Id 1
is Ed25519, the current leaf. Id 2 is ML-DSA-44. This is the same agility pattern
I used in CIP-0206, where a versioned encoding names the scheme rather than
dispatching on field width.

Scope. This proposal changes the KES leaf only. The operational certificate cold
key stays classical in this step. Making the cold key post quantum is a separate
and additive change and I flag it rather than fold it in silently.

## Measured results

I built a reference instantiation of the Cardano sum composition that is a
faithful mirror of cardano-base, same Blake2b pairing, same seed split, same
signature layout. Instantiated with an Ed25519 leaf it reproduces the exact
Cardano Sum6 figure of 448 bytes and verifies at periods 0, 1, 32 and 63 with a
tampered header refused, which anchors the harness to the real construction. The
same harness with an ML-DSA-44 leaf measures the following.

    leaf       Sum6 KES signature    verify, indicative
    Ed25519    448 bytes             tens of microseconds
    ML-DSA-44  5364 bytes            about 50 microseconds

ML-DSA-44 header verification measures about 50 microseconds in the reference,
the same order as the current Ed25519 KES verification. The size sweep ran every
one of the 64 periods, each signature sized exactly, verified at its own period,
was refused at any other period, and was refused under a tampered header. Timings
are a single machine release build and are indicative only, not a production
costing. Verification cost is not a concern against a 20 second slot.

## Rationale

Why ML-DSA-44. ML-DSA is the NIST standardized lattice signature under FIPS 204.
It has a fixed signature size, which the KES fixed size serialization needs, and a
mature constant time reference. I have direct experience with it. I authored
CIP-0206, which adds an ML-DSA verification builtin to Plutus and is at Last Check.
I maintain ML-DSA conformance vectors against the NIST ACVP set that are already
vendored by a Bitcoin reference library. I know this scheme end to end and I know
it is the right leaf for KES. It is the one choice that is mature, fixed size, and
already specified elsewhere in the Cardano post quantum work, which keeps the
ecosystem on one scheme rather than many.

The one consequence, stated plainly. An ML-DSA-44 KES signature is 5364 bytes. A
full header is therefore about 6 kilobytes. The live block header limit is 1100
bytes at protocol version 11. The Constitution guardrail MBHS-01 caps the header
at 5000 bytes, while MBHS-03 requires the limit to be large enough for the largest
valid header. So this leaf requires raising maxBlockHeaderSize to about 7000 and
lifting MBHS-01 to match. This is a bounded parameter and guardrail change inside
the normal governance process. It does not touch the block body limit of 90112
bytes, the transaction limit of 16384 bytes, the slot schedule, or the tree
structure. The header is a small part of a block and a 6 kilobyte header sits
comfortably inside the existing body budget for diffusion.

What this does not do. It does not change the VRF. A post quantum VRF is still an
open research problem with no standard, and I keep it out of scope here rather
than ship a weak VRF claim. It does not make the cold key post quantum, which is a
separate step. It does not require a new hashing or tree design, the sum tree is
already efficient for a post quantum leaf because its internal nodes are hashes.

## Path to active

The in node KES change is consensus critical and its adoption needs a hardfork
through the standard Cardano process. That work belongs to the ledger and
consensus maintainers. This proposal fixes the leaf scheme, the encoding and the
verification semantics against FIPS 204 so the change can be implemented against a
precise target with vectors. I provide the reference instantiation and conformance
vectors in a Quantova repository and link them here rather than merge code, which
matches how CIP-0206 was handled. I offer to maintain the vectors and support
conformance.

## References

CPS-0030 Quantum secure settlement layer.
cardano-base Cardano.Crypto.KES.Sum.
Cardano ledger KES StandardCrypto type.
MMM, Composition and Efficiency Tradeoffs for Forward Secure Digital Signatures.
FIPS 204 ML-DSA.
Cardano Constitution, guardrail MBHS-01, maxBlockHeaderSize must not exceed 5000 bytes.
Live protocol parameters, epoch 670, protocol version 11.
Reference and conformance vectors, https://github.com/quantova-inc/cardano-pq-tooling/tree/main/kes-mldsa
