---
CIP: "?"
Title: ML-DSA-44 KES Leaf for Post Quantum Consensus
Category: Consensus
Status: Proposed
Authors:
  - Quantova Inc <https://github.com/quantova-inc>
Implementors: []
Discussions:
  - Proposal PR: https://github.com/cardano-foundation/CIPs/pull/1341
  - CIP-0206? | ML-DSA and SLH-DSA Signatures: https://github.com/cardano-foundation/CIPs/pull/1300
Created: 2026-11-28
License: CC-BY-4.0
---

## Abstract

CPS-0030 flags the KES as one of the base settlement layer primitives at risk
from a quantum adversary, alongside the digital signatures and the VRF. This
proposal addresses the KES. It specifies replacing the Ed25519 leaf of Cardano's
KES with an ML-DSA-44 leaf under FIPS 204. The MMM sum composition that Cardano
already runs is agnostic to its leaf signature, so a post quantum leaf gives a
forward secure block forging signature with no change to the tree. The proposal
provides a reference instantiation, measured sizes and timings, a versioned leaf
encoding for agility, a header size and propagation analysis, and the one
protocol change this requires, a larger block header limit.

This proposal does not claim to close CPS-0030. It settles the KES primitive
only. The VRF, the other digital signatures, the operational certificate cold
key, and the wider networking policy for larger artifacts are out of scope here
and remain open.

## Motivation: Why is this CIP necessary?

Cardano block production signs each header with a key evolving signature so that
a compromised hot key cannot forge past blocks. Today the leaf of that KES is
Ed25519, which Shor's algorithm breaks. CPS-0030 names the KES among the
settlement layer primitives at risk and leaves open which post quantum scheme
should take its place and how the larger artifacts are carried. This proposal
settles the scheme question for the KES and gives measured input to the size
question.

The KES construction is Sum6KES over an Ed25519 leaf with Blake2b_256 internal
nodes, as defined in cardano-base, Cardano.Crypto.KES.Sum, and in the ledger type
KES StandardCrypto. The sum composition carries one real signature at the active
leaf. Every internal node verification key is a 32 byte Blake2b hash. Only the
leaf signature scheme is cryptographic. The MMM construction and CPS-0030 both
state that the composition is agnostic to its leaf signature, so a post quantum
leaf substitutes directly, and the forward security proof is preserved as long as
the leaf is existentially unforgeable.

## Specification

### Leaf and key generation

The depth zero leaf of the KES becomes ML-DSA-44 under FIPS 204. The parameters
are a 1312 byte public key, a 2420 byte signature, a 2560 byte secret key, and a
32 byte seed. Key generation uses the existing 32 byte KES seed path as the
ML-DSA seed, so the seed derivation of the sum tree is unchanged, and leaf keys
stay deterministic in their seed as KES evolution requires. ML-DSA key generation
is seed based in FIPS 204, so this determinism is native and needs no emulation.

### Signature size

The signature serialization is unchanged in shape. A composed signature is the
sub signature followed by the two child verification keys. The two leaf public
keys appear once at the bottom level and every higher level carries a 32 byte
hash. A Sum6 signature under an ML-DSA-44 leaf is therefore

    leaf signature 2420 + two leaf keys 2624 + five hash levels 320 = 5364 bytes

### Verification

Verification is unchanged. Each node hash is recomputed up the path and checked
against the operational certificate key, and the ML-DSA-44 signature is verified
at the leaf.

### Leaf scheme identifier

The operational certificate gains a two byte leaf scheme id so the KES leaf can
move to a later scheme without a second format break. Id 1 is Ed25519, the
current leaf. Id 2 is ML-DSA-44. This is the same agility pattern used in
CIP-0206, where a versioned encoding names the scheme rather than dispatching on
field width.

### Scope of this change

This proposal changes the KES leaf only. The operational certificate cold key
stays classical in this step. A post quantum cold key is a separate and additive
change and is flagged here rather than folded in silently. The VRF is not touched
and is discussed under Rationale.

### Measured results

A reference instantiation of the Cardano sum composition reproduces the
construction faithfully, with the same Blake2b pairing, the same seed split, and
the same signature layout. With an Ed25519 leaf it serializes a Sum6 signature to
exactly 448 bytes, verifies at periods 0, 1, 32 and 63 with a tampered header
refused, and measures Ed25519 verification at about 21 microseconds, which
matches the 20.8 microseconds the cardano-base prototype in PR 1320 reports for
the same leaf. Reproducing both the exact size and the baseline timing anchors
the harness to the real construction before any post quantum number is read from
it. With an ML-DSA-44 leaf the same harness measures the following.

    Sum6KES                 Ed25519        ML-DSA-44
    signature               448 bytes      5364 bytes
    verification            about 21 us    about 51 us
    full key generation     about 0.5 ms   about 5.8 ms
    per block leaf sign     about 16 us    about 211 us
    leaf regeneration       about 8 us     about 89 us

The size sweep ran every one of the 64 periods. Each signature was sized exactly,
verified at its own period, refused at any other period, and refused under a
tampered header. ML-DSA-44 verification at about 51 microseconds is negligible on
the block adoption path, where the budget is measured in seconds. Key generation
and signing stay in the microsecond to low millisecond range. The timings are a
single machine release build and are indicative of relative cost, not a
production costing.

### Header size and propagation

Size is the binding constraint for a post quantum KES leaf and this proposal
states it rather than leaves it open. An ML-DSA-44 KES signature is 5364 bytes,
so a full header is about 6 kilobytes, against a live maxBlockHeaderSize of 1100
bytes at protocol version 11. This leaf therefore requires raising
maxBlockHeaderSize to about 7000 bytes. It does not touch the block body limit of
90112 bytes, the transaction limit of 16384 bytes, the slot schedule, or the tree
structure. A 6 kilobyte header is a small fraction of a full block and sits
inside the existing body budget for diffusion.

The header growth bears on block propagation and on the activeSlotsCoeff margin.
That is a networking and consensus decision for the ledger and consensus
maintainers, not a cryptographic one settled here. What this proposal contributes
to that decision is the exact header size for a named standardized leaf and a
reference that produces it, so the propagation question can be evaluated against a
fixed number rather than an estimate. Any lattice KES leaf crosses the 1100 byte
limit, so the header change is required for this direction regardless of which
leaf is chosen.

## Rationale: How does this CIP achieve its goals?

### Why ML-DSA-44 and not Falcon-512

PR 1320 measures a Falcon-512 leaf in the same Sum6KES and reports that size is
the main constraint. Size is the constraint for any lattice leaf, and the numbers
here sit beside that result, but the Falcon figures do not carry the weight they
appear to carry, for two reasons set out below. Falcon-512 does give the smaller
signature at 2884 bytes and the faster verification at 11.3 microseconds, and
that is the one axis on which it leads. Both leaves cross the 1100 byte header
limit, so neither avoids the header change, and the size gap does not change what
governance has to do.

### Scheme maturity and determinism

The Falcon measured in PR 1320 is not the scheme NIST is standardizing. It is
Algorand's deterministic Falcon-512, and FN-DSA, the Falcon based signature in
draft FIPS 206, is not finalized and is not the same scheme as that variant.
Building a KES on Falcon now would commit Cardano to a non standard variant and a
migration to FN-DSA once it is published, which is a second format break.

A KES leaf must also be deterministic in its seed, and Falcon signing uses
floating point arithmetic, so PR 1320 runs that arithmetic in integer emulation
to make the result independent of hardware and compiler. Those are the real costs
of a deterministic Falcon KES, and PR 1320 records them as a full key generation
of 411 milliseconds and a key evolution of 6 to 210 milliseconds. ML-DSA-44 is
integer by design, so its determinism is native and needs no emulation. In the
same sum composition it generates the full KES key in about 5.8 milliseconds,
signs in about 0.2 milliseconds, and regenerates a leaf on evolution in about 0.1
milliseconds. ML-DSA-44 is finalized under FIPS 204 today, with public ACVP
vectors and a mature constant time reference, which suits a key that signs every
forged block.

ML-DSA-44 is also the scheme behind CIP-0206, which adds an ML-DSA verification
builtin to Plutus and is at Last Check. Quantova authored CIP-0206 and maintains
the ML-DSA conformance vectors against the NIST ACVP set that a Bitcoin reference
library already vendors. Choosing ML-DSA-44 for the KES leaf keeps a node on one
lattice scheme across its Plutus and consensus paths rather than two.

### What this proposal does not do

It does not change the VRF. A post quantum VRF has no standard yet, so it is kept
out of scope rather than carried as a weak claim. It does not make the cold key
post quantum, which is a separate step. It does not resolve the networking policy
for larger artifacts, which it informs with a measured number rather than
decides. It does not require a new hashing or tree design, because the sum tree
is already efficient for a post quantum leaf, its internal nodes being hashes.

## Path to Active

### Acceptance Criteria

- The ML-DSA-44 KES leaf and the two byte leaf scheme identifier are implemented
  in the node and pass the conformance vectors published with this proposal.
- maxBlockHeaderSize is raised and guardrail MBHS-01 is lifted so that a header
  carrying an ML-DSA-44 KES signature is valid.
- Block production and verification interoperate across the activation, with the
  measured header size assessed for propagation by the consensus maintainers.

### Implementation Plan

- The ledger and consensus maintainers implement the leaf and the encoding in the
  node against the vectors and semantics fixed here.
- Quantova provides and maintains the reference instantiation and the conformance
  vectors and supports conformance testing.
- The parameter and guardrail change is proposed through the normal governance
  process ahead of the hardfork that activates the leaf.

## References

- [CPS-0030 Quantum secure settlement layer](https://github.com/cardano-foundation/CIPs/tree/master/CPS-0030)
- [CPS-0030 PR 1320, measured impact of a Falcon KES leaf](https://github.com/cardano-foundation/CIPs/pull/1320)
- [cardano-base, Cardano.Crypto.KES.Sum](https://github.com/IntersectMBO/cardano-base)
- [cardano-ledger, KES StandardCrypto](https://github.com/IntersectMBO/cardano-ledger)
- [FIPS 204, ML-DSA](https://csrc.nist.gov/pubs/fips/204/final)
- [NIST post quantum cryptography, FN-DSA and FIPS 206 status](https://csrc.nist.gov/projects/post-quantum-cryptography)
- [Cardano Constitution, guardrails MBHS-01 and MBHS-03](https://constitution.gov.tools)
- [Reference instantiation and conformance vectors](https://github.com/quantova-inc/cardano-pq-tooling/tree/main/kes-mldsa)

## Copyright

This CIP is licensed under CC-BY-4.0.
