---
CIP: "?"
Title: ML-DSA-44 KES Leaf for Post Quantum Block Production
Category: Consensus
Status: Proposed
Authors:
  - Quantova Inc <https://github.com/quantova-inc>
Implementors: []
Discussions:
  - Proposal PR: https://github.com/cardano-foundation/CIPs/pull/1341
  - CPS-0030 problem statement: https://github.com/cardano-foundation/CIPs/blob/master/CPS-0030/README.md
  - Falcon KES measurements in CPS-0030: https://github.com/cardano-foundation/CIPs/pull/1320
  - Related CIP-0206 thread: https://github.com/cardano-foundation/CIPs/pull/1300
Created: 2026-11-28
License: CC-BY-4.0
---

## Abstract

CPS-0030 names three cryptographic primitives of the settlement layer at risk
from a quantum adversary, the block signature, the VRF, and the KES. This
proposal addresses one of those three, the KES. It specifies replacing the
Ed25519 leaf of Cardano's KES with an ML-DSA-44 leaf under FIPS 204. The MMM sum
composition that Cardano already runs is leaf agnostic, so this gives a forward
secure post quantum block forging signature with no change to the tree. I give a
working reference instantiation, measured sizes and timings, a versioned leaf
encoding for agility, a header size and propagation analysis, and the one
protocol change this requires, a larger block header limit. I do not claim to
close CPS-0030. The VRF, the operational certificate cold key, and the wider
networking policy for larger artifacts are out of scope here and stay open, and
I note where each belongs.

## Motivation: Why is this CIP necessary?

Cardano block production signs each header with a key evolving signature so that
a compromised hot key cannot forge past blocks. Today the leaf of that KES is
Ed25519, which Shor's algorithm breaks. CPS-0030 ranks the KES as one of the
three settlement layer primitives at risk and leaves open which post quantum
scheme should take its place and how the larger artifacts are carried. This
proposal settles the first of those two questions for the KES and gives measured
input to the second.

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
bytes. Key generation takes the existing 32 byte KES seed path as the ML-DSA
seed, so the seed derivation of the sum tree is unchanged, and leaf keys stay
deterministic in the seed as the KES evolution requires.

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
used in CIP-0206, where a versioned encoding names the scheme rather than
dispatching on field width.

Scope. This proposal changes the KES leaf only. The operational certificate cold
key stays classical in this step. Making the cold key post quantum is a separate
and additive change and I flag it rather than fold it in silently. The VRF is not
touched here and is discussed under Rationale.

### Measured results

I built a reference instantiation of the Cardano sum composition that is a
faithful mirror of cardano-base, same Blake2b pairing, same seed split, same
signature layout. Instantiated with an Ed25519 leaf it reproduces the exact
Cardano Sum6 figure of 448 bytes, verifies at periods 0, 1, 32 and 63 with a
tampered header refused, and measures Ed25519 verify at about 21 microseconds,
which matches the 20.8 microseconds the cardano-base prototype in PR 1320 reports
for the same leaf. Reproducing both the exact size and the baseline timing
anchors the harness to the real construction. The same harness with an ML-DSA-44
leaf measures the following.

    Sum6KES                 Ed25519        ML-DSA-44
    signature               448 bytes      5364 bytes
    verification            about 21 us    about 51 us
    full key generation     about 0.5 ms   about 5.8 ms
    per block leaf sign     about 16 us    about 211 us
    leaf regeneration       about 8 us     about 89 us

The size sweep ran every one of the 64 periods, each signature sized exactly,
verified at its own period, refused at any other period, and refused under a
tampered header. ML-DSA-44 verification is about 51 microseconds against a 20
second slot, so it is not a concern on the critical path. Key generation and
signing stay in the microsecond to low millisecond range. Timings are a single
machine release build and are indicative of relative cost, not a production
costing.

### Header size and propagation

Size is the binding constraint and I state it plainly rather than leave it open.
An ML-DSA-44 KES signature is 5364 bytes, so a full header is about 6 kilobytes,
against a live maxBlockHeaderSize of 1100 bytes at protocol version 11. This leaf
requires raising maxBlockHeaderSize to about 7000 bytes. It does not touch the
block body limit of 90112 bytes, the transaction limit of 16384 bytes, or the
tree structure. A 6 kilobyte header is a small fraction of a full block and sits
inside the existing body budget for diffusion.

The header growth bears on block propagation and on the activeSlotsCoeff margin,
and that is a networking and consensus decision that belongs to the ledger and
consensus maintainers, not a cryptographic one I settle here. What this proposal
contributes to that decision is the exact header size for a named, standardized
leaf and a reference that produces it, so the propagation question can be
evaluated against a fixed number rather than an estimate. Any lattice KES leaf
crosses the 1100 byte limit, so the header change is required for this direction
regardless of which leaf is chosen.

## Rationale: How does this CIP achieve its goals?

Why ML-DSA-44 and not Falcon-512. PR 1320 measures a Falcon-512 leaf in the same
Sum6KES and concludes, correctly, that size is the main constraint. I agree with
that finding and my numbers sit beside it. Two points about the comparison need
stating plainly. First, the Falcon measured in PR 1320 is not the scheme NIST is
standardizing. It is Algorand's deterministic Falcon-512, and FN-DSA, the Falcon
based signature in draft FIPS 206, is not finalized and is not compatible with
it. Choosing a Falcon KES now would commit Cardano to a non standard variant and
a later migration to FN-DSA once it is published, which is a second format break.
Second, a KES leaf must be deterministic in its seed, and to meet that on Falcon
PR 1320 uses integer emulation of the floating point arithmetic Falcon signing
needs. The published literature reports that this emulation runs substantially
slower than native floating point Falcon, so the Falcon key generation and
signing costs reported in PR 1320 include that emulation penalty.

ML-DSA-44 avoids both problems. It is finalized under FIPS 204 today with public
ACVP vectors, and it is integer only by design, so its determinism and its
constant time signing need no floating point and no emulation. In the same sum
composition it generates the full KES key about seventy times faster, 5.8
milliseconds against 411, signs about nine times faster, and regenerates a leaf
on evolution in microseconds rather than the 6 to 210 milliseconds PR 1320
records. Falcon-512 gives the smaller signature at 2884 bytes and the faster
verify at 11.3 microseconds, and that is the one axis where it leads. Since both
leaves cross the 1100 byte header limit, neither avoids the header change, so the
size gap does not change what governance has to do. ML-DSA-44 is also the scheme
already in flight for Cardano in CIP-0206, so a node audits, maintains, and
vendors one lattice scheme rather than two. I have direct experience with ML-DSA.
I authored CIP-0206, which adds an ML-DSA verification builtin to Plutus and is at
Last Check, and I maintain ML-DSA conformance vectors against the NIST ACVP set
that a Bitcoin reference library already vendors. That is the basis for proposing
it as the KES leaf.

What this does not do. It does not change the VRF. A post quantum VRF is still an
open research problem with no standard, and I keep it out of scope here rather
than ship a weak VRF claim. It does not make the cold key post quantum, which is
a separate step. It does not resolve the networking policy for larger artifacts,
which I give measured input to rather than decide. It does not require a new
hashing or tree design, the sum tree is already efficient for a post quantum leaf
because its internal nodes are hashes. This is one of the three CPS-0030
primitives, specified to an implementable target, not a closure of CPS-0030.

## Path to Active

The in node KES change is consensus critical and its adoption needs a hardfork
through the standard Cardano process. That work belongs to the ledger and
consensus maintainers. This proposal fixes the leaf scheme, the encoding and the
verification semantics against FIPS 204 so the change can be implemented against a
precise target with vectors.

### Acceptance Criteria

- The ML-DSA-44 KES leaf and the two byte leaf scheme identifier are implemented
  in the node and pass the conformance vectors published with this CIP.
- maxBlockHeaderSize is raised and guardrail MBHS-01 is lifted so a header
  carrying an ML-DSA-44 KES signature is valid, with the propagation impact
  assessed by the consensus maintainers against the measured header size.
- The change is activated through a hardfork, with block production and
  verification interoperating across the upgrade.

### Implementation Plan

- The ledger and consensus maintainers implement the leaf and the encoding in the
  node against the vectors and semantics fixed here.
- I provide and maintain the reference instantiation and the conformance vectors
  in a Quantova repository and support conformance.
- The parameter and guardrail change is proposed through the normal governance
  process ahead of the hardfork that activates the leaf.

## References

- CPS-0030 Quantum secure settlement layer.
- CPS-0030 PR 1320, measured impact of Falcon as the KES leaf.
- cardano-base Cardano.Crypto.KES.Sum.
- Cardano ledger KES StandardCrypto type.
- MMM, Composition and Efficiency Tradeoffs for Forward Secure Digital Signatures.
- FIPS 204 ML-DSA.
- Cardano Constitution, guardrail MBHS-01, maxBlockHeaderSize must not exceed 5000 bytes.
- Live protocol parameters, epoch 670, protocol version 11.
- Reference and conformance vectors, https://github.com/quantova-inc/cardano-pq-tooling/tree/main/kes-mldsa

## Copyright

This CIP is licensed under CC-BY-4.0.
