---
CIP: "?"
Title: Post-Quantum Signature Verification Builtins
Category: Plutus
Status: Proposed
Authors:
    - Quantova Inc <Quantovaorg@gmail.com>
Implementors: []
Discussions:
    - Original PR: https://github.com/cardano-foundation/CIPs/pull/1300
Solution To:
    - CPS-0027: https://github.com/cardano-foundation/CIPs/tree/master/CPS-0027
Created: 2026-10-15
License: CC-BY-4.0
---

## Abstract

This CIP responds to CPS-0027, which asks which post quantum signature scheme Cardano should introduce as a Plutus builtin. It proposes adding two verification builtins, one for ML-DSA under FIPS 204 and one for SLH-DSA under FIPS 205, together with a single self describing encoding for post quantum keys and signatures. Both schemes are NIST standardised and rest on different hard problems, a lattice problem and a hash problem, so a weakness found in one family does not remove Cardano's post quantum coverage. The encoding declares the scheme by an identifier so that a verification builtin dispatches on a named algorithm rather than on the width of a field. Test vectors accompany the proposal, and a reference implementation is linked.

## Motivation: Why is this CIP necessary?

The motivation is set out in full in [CPS-0027](../CPS-0027/README.md). Cardano scripts can verify Ed25519, ECDSA and Schnorr signatures through builtins, and all three fall to a quantum computer running Shor's algorithm. CPS-0027 states that the biggest open question is which scheme to choose, and that a well researched justification is required before that choice is made. This CIP provides a concrete answer, with the evidence CPS-0027 asks for, so that the community has a specification to review rather than an open field.

## Specification

### Schemes

Two verification builtins are added.

- `verifyMlDsaSignature` verifies an ML-DSA signature as defined in [FIPS 204][fips204].
- `verifySlhDsaSignature` verifies an SLH-DSA signature as defined in [FIPS 205][fips205].

Each builtin takes a versioned public key, a message and a versioned signature, and returns a boolean. Verification is pure ML-DSA or pure SLH-DSA with an empty context string, which is the form every reference implementation produces by default.

### Versioned encoding

A post quantum key or signature is carried as a versioned object so that a verifier reads the scheme from a declared identifier and never from the length of a field.

```
object  = version || algId || kind || body
version = 0x01                   ; one byte, this encoding version
algId   = uint16, big endian     ; the scheme identifier
kind    = uint8                  ; 0x01 public key, 0x02 signature
body    = the scheme bytes
```

The initial identifiers are

| algId | scheme | standard | public key | signature |
| --- | --- | --- | --- | --- |
| `0x0001` | ML-DSA-44 | FIPS 204 | 1312 | 2420 |
| `0x0002` | ML-DSA-65 | FIPS 204 | 1952 | 3309 |
| `0x0003` | ML-DSA-87 | FIPS 204 | 2592 | 4627 |
| `0x0004` | SLH-DSA-SHA2-128s | FIPS 205 | 32 | 7856 |

A builtin rejects an object whose version is not `0x01`, whose identifier is not one it supports, whose kind is not valid, or whose body length does not match the table.

### CDDL

```
pq_object = bytes               ; version || algId || kind || body, as above
pq_public_key = pq_object       ; kind 0x01
pq_signature  = pq_object       ; kind 0x02
```

### Builtin signatures

```
verifyMlDsaSignature  :: pq_public_key -> message -> pq_signature -> bool
verifySlhDsaSignature :: pq_public_key -> message -> pq_signature -> bool
```

A builtin returns false on a well formed object whose signature does not verify, and fails evaluation on a malformed object, matching the behaviour of the existing Ed25519 builtin.

### Test vectors

[`test-vectors.json`](./test-vectors.json) fixes the expected behaviour of both builtins, and every entry carries a description of the property it checks. Keys are derived from fixed seeds and signatures use the deterministic signing variant of FIPS 204 and FIPS 205 with an empty context string, so any implementation can reproduce every vector.

- Encoding vectors give a public key and a signature for each of the four identifiers, with the identifier, kind and body length a decoder must report.
- Verification vectors give a public key, a message, a signature and the expected result. For each scheme they check that a genuine signature returns true, that changing one bit of the message returns false, and that changing one bit of the signature returns false. Further vectors check that a signature does not verify under another key of the same scheme, and that evaluation fails when the key and signature declare different schemes, when a key of one family is passed to the builtin of the other, and when a signature is placed in the public key position.
- Rejection vectors are malformed objects that every builtin must refuse, covering an unsupported version, an unassigned and a reserved identifier, an invalid kind, a body one byte short and one byte long, and a truncated header.

Every vector was generated with one implementation and checked against a second, independent one.

## Rationale: How does this CIP achieve its goals?

### Why two schemes and these two

CPS-0027 raises the question of whether more than one scheme should be available, and notes that Cardano already carries three pre quantum builtins. ML-DSA and SLH-DSA are the two signature schemes that NIST has finalised, as [FIPS 204][fips204] and [FIPS 205][fips205], both published in August 2024 at the end of the NIST post quantum standardisation process described in [NIST IR 8413][ir8413]. They rest on unrelated hard problems, so the pair gives Cardano a fallback if one family is weakened. Falcon is cited by CPS-0027 and by earlier work, but it is still in review as the draft FIPS 206, as listed on the [NIST post quantum cryptography project page][nistpqc], and its signing uses floating point, which is a portability and side channel concern on chain. SQIsign is attractive for size but is not standardised and verifies slowly. [NIST IR 8547][ir8547] sets out the transition away from quantum vulnerable signatures, proposing to deprecate them after 2030 and disallow them after 2035, which gives a concrete horizon for having post quantum verification available on chain. This CIP recommends shipping the two finalised schemes first and leaving Falcon and SQIsign to a later identifier once standardised, which the versioned encoding supports without a second format break.

### Sizes and cost

The sizes below are fixed by the standards. The verification times are from a JavaScript reference implementation on a single core and are indicative of relative cost only, not of a native Cardano builtin, which would be faster.

| scheme | public key | signature | reference verify |
| --- | --- | --- | --- |
| ML-DSA-44 | 1312 B | 2420 B | about 0.84 ms |
| ML-DSA-65 | 1952 B | 3309 B | about 1.34 ms |
| ML-DSA-87 | 2592 B | 4627 B | about 2.17 ms |
| SLH-DSA-SHA2-128s | 32 B | 7856 B | about 0.92 ms |

SLH-DSA has the smallest key and the largest signature, and ML-DSA has the opposite balance, which is why both are offered. Final costing against the Plutus cost model needs native benchmarks and is left to implementation.

### Why a versioned encoding

CPS-0027 is a signature problem, but Cardano will also need to name the scheme wherever a post quantum key or signature appears. Declaring the scheme by an identifier, rather than by field width, lets a later identifier be added without a second format break, and lets one builtin serve several parameter sets. This follows the versioned hash precedent that other ecosystems already use.

## Path to Active

### Acceptance Criteria

- [ ] The two builtins are implemented in the Plutus evaluator against the FIPS 204 and FIPS 205 reference vectors.
- [ ] The cost model is calibrated from native benchmarks.
- [ ] The change is scheduled through the standard Cardano hardfork process.

### Implementation Plan

- A reference encoder, decoder and verification check are published at https://github.com/quantova-inc/bnb-pq-tooling/tree/main/registry and are linked rather than included here.
- The test vectors in this CIP are the conformance target for any implementation.
- Quantova Inc maintains the reference vectors and supports the Plutus implementation team with conformance checks.
- The in evaluator builtin and the cost model are the work of the ledger and Plutus maintainers, since they are consensus critical and require a hardfork.

## References

- [FIPS 204, Module Lattice Based Digital Signature Standard][fips204]
- [FIPS 205, Stateless Hash Based Digital Signature Standard][fips205]
- [NIST IR 8413, Status Report on the Third Round of the NIST Post Quantum Cryptography Standardization Process][ir8413]
- [NIST IR 8547, Transition to Post Quantum Cryptography Standards (initial public draft)][ir8547]
- [NIST Post Quantum Cryptography project][nistpqc]

[fips204]: https://csrc.nist.gov/pubs/fips/204/final
[fips205]: https://csrc.nist.gov/pubs/fips/205/final
[ir8413]: https://csrc.nist.gov/pubs/ir/8413/upd1/final
[ir8547]: https://csrc.nist.gov/pubs/ir/8547/ipd
[nistpqc]: https://csrc.nist.gov/projects/post-quantum-cryptography

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
