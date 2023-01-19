---
CIP: ??? 
Title: PostQuantum signatures in Plutus Core
Category: Plutus
Authors:
  - Michał J. Gajda (mjgajda@migamake.com)
Implementors: []
Discussions-To: https://github.com/cardano-foundation/cips/pulls/?
Comments-Summary: 
Comments-URI:  
Status: Proposed
Type: Standards Track
Created: 2023-01-19  
License: Apache-2.0
---
## Simple Summary

Support post-quantum signatures (Dilithium+CRYSTALS, FALCON) as recommended by NIST standardization effort in Plutus Core;
allow validation of such signatures as builtins.

## Abstract

Provides a way of verifying post-quantum signatures as recommended by NIST in Plutus Core.
New builtins will allow use of these signatures within smart contracts. These builtins work over
``BuiltinByteString``s.

## Motivation

NIST estimates that pre-quantum cryptographic algorithms may be no longer safe
by 2035. However, the smart contracts have long development and lifetime,
so migration to post-quantum cryptography algorithms should start several
years before they would become insecure.
This summer NIST has recommended three PQC signature algorithms
for standardization, publishing their reference implementations,
and finishing initial comment period.

Supporting PQC signatures will bring the following benefits:

* smart contracts may use future standard algorithms today;
* early support for PQC will simplify future PQC migration, if needed;
* future PQC migration would be smooth and require less changes;
* support for PQC may increase industry acceptance for long running projects;
* users that want their wallets to survive over ten years may
  use smart contracts verifying multiple algorithms today;
* Cardano will become first blockchain to verify PQC standard signatures,
  thus getting first-mover advantage.

## Specification

Two new builtin functions would be provided:

* A verification function for CRYSTALS(DILITHIUM) signatures; and
* A verification function for FALCON signatures;
* A verification function for SPHINCS signatures.

These would be based on NIST reference implementations,
as maintained by [``](https://github.com/bitcoin-core/secp256k1) library.
This is a reference implementation of the three kinds of signature schemes in C. This 
implementation would be called from Haskell using direct bindings to C. These
bindings would be defined in `cardano-base`, using its existing `DSIGN`
interface, with new builtins in Plutus Core on the basis of the `DSIGN`
interface for both schemes.

The builtins would be costed as follows: each signature verification has
linear cost proportional to the number of message bits, and square with respect to key length.
_Constants will be proportional to the ratio of time as benchmarked against
Ed25519._

More specifically, Plutus would gain the following primitive operations:

* `verifyCrystalsDilithiumSignature :: BuiltinByteString -> BuiltinByteString ->
  BuiltinByteString -> BuiltinBool`, for verifying arbitrary binary signed 
  using the CRYSTALS signature scheme; and
* `verifyFalconSignature :: BuiltinByteString -> BuiltinByteString
  -> BuiltinByteString -> BuiltinBool`, for verifying arbitrary binary messages 
  signed using the Falcon signature scheme; and
* `verifySphincsSignature :: BuiltinByteString -> BuiltinByteString
  -> BuiltinByteString -> BuiltinBool`, for verifying arbitrary binary messages 
  signed using the Sphincs signature scheme; and

Both functions take parameters of a specific part of the signature scheme, even
though they are all encoded as `BuiltinByteString`s. In order, for both
functions, these are:

1. A verification key;
2. An input to verify (either the message itself, or a hash);
3. A signature.

The two different schemes handle deserialization internally: specifically, there
is a distinction made between 'external' representations, which are expected as
arguments, and 'internal' representations, used only by the implementations
themselves. This creates different expecations for each argument for both of
these schemes; we describe these below.

For the [all signature
schemes](https://en.bitcoin.it/wiki/Elliptic_Curve_Digital_Signature_Algorithm),
the keys are required to be given in the same format as NIST test vectors.

The verification key must correspond to a result produced by [`...`]()
from the reference implementation library. The key will be ... bytes long.
The input must be ...

* The input to verify must be a message to be checked. We 
  assume that the caller of `...` receives the 
  message and hashes it.
* The signature must correspond to the format used by NIST reference test vectors.
* The signature must correspond to a result produced by
  [``...``]().

The builtin operations will error with a descriptive message if given inputs
that don't correspond to the constraints above, return `False` if the signature
fails to verify the input given the key, and `True` otherwise.

## Rationale

We consider the implementation trustworthy after passing long comment period,
considering that many competitors were eliminated by publishing weaknesses.

An alternative approach could be to provide low-level primitives from the reference library,
but that would decrease compatibility and security, since the reference implementation
will likely be supported by other software.

While lattice cryptography may require increased signature sizes, security-conscious
users will be willing to pay the price.

## Backward Compatibility

At the Plutus Core level, implementing this proposal induces no
backwards-incompatibility: the proposed new primitives do not break any existing
functionality or affect any other builtins. Likewise, at levels above Plutus
Core (such as `PlutusTx`), no existing functionality should be affected.

On-chain, this requires a hard fork.

## Path to Active

An implementation will require the following steps:

1. Linking to PQC library.
2. Providing the patch implementing new Plutus primitives just like for [EcDSA and Schnorr](https://github.com/input-output-hk/plutus/pull/4368).
3. Providing the PQC primitives using `Crypto` interface for ease of use.0

## Copyright

This CIP is licensed under Apache-2.0.
