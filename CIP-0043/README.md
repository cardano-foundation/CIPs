CIP: ?0043 
Title: ECDSA and Schnorr signatures in Plutus Core  
Authors: Koz Ross (koz@mlabs.city), Michael Peyton-Jones 
Discussions-To: koz@mlabs.city
Comments-Summary: 
Comments-URI:  
Status: Proposed
Type: Standards Track
Created: 2022-04-27  
* License:   
* License-Code:   
* Post-History:  
* Requires:
* Replaces:  
Superseded-By:
---
## Simple Summary

Support ECDSA and Schnorr signatures over the SECP256k1 curve in Plutus Core; 
specifically, allow validation of such signatures as builtins.

## Abstract

Provides a way of verifying ECDSA and Schnorr signatures over the SECP256k1
curve in Plutus Core, specifically with new builtins. These builtins work over
``BuiltinByteString``s.

## Motivation

Signature schemes based on the SECP256k1 curve are common in the blockchain
industry; a notable user of these is Bitcoin. Supporting signature schemes which
are used in other parts of the industry provides an interoperability benefit: we
can verify signatures produced by other systems as they are today, without
requiring other people to produce signatures specifically for us. This not only
provides us with improved interoperability with systems based on Bitcoin, but
also compatibility with other interoperability systems, such as Wanchain and
Renbridge, which use SECP256k1 signatures for verification.

## Specification

Two new builtin functions would be provided:

* A verification function for ECDSA signatures using the SECP256k1 curve; and
* A verification function for Schnorr signatures using the SECP256k1 curve.

These would be based on `libsecp256k1`, a reference implementation of both kinds
of signature scheme in C. This implementation would be called from Haskell using
direct bindings to C. This implementation would be implemented in
`cardano-base`, with new builtins in Plutus Core on the basis of the
`cardano-base`-provided interface for signature schemes.

The builtins would be costed as follows: ECDSA signature verification has
constant cost, as the message, verification key and signature are all
fixed-width; Schnorr signature verification is instead linear in the message
length, as this can be arbitrary, but as the length of the verification key and
signature are constant, the costing will be constant in both.

More specifically, Plutus would gain the following primitive operations:

* ```verifyEcdsaSecp256k1Signature :: BuiltinByteString -> BuiltinByteString ->
  BuiltinByteString -> BuiltinBool```, for verifying 32-byte message hashes signed 
  using the ECDSA signature scheme on the SECP256k1 curve; and
* ```verifySchnorrSecp256k1Signature :: BuiltinByteString -> BuiltinByteString
  -> BuiltinByteString -> BuiltinBool```, for verifying arbitrary binary messages 
  signed using the Schnorr signature scheme on the SECP256k1 curve.

Both functions take parameters of a specific part of the signature scheme, even
though they are all encoded as `BuiltinByteString`s. In order, for both
functions, these are:

1. A verification key;
2. A message (possibly hashed);
3. A signature.

The two different schemes have different expectations of each argument and how
it is encoded into a `BuiltinByteString`. We describe these below.

For the ECDSA signature scheme, we have the following requirements:

* The verification key must be 33 bytes. Furthermore, the encoding must
  correspond to the result produced by
  [``secp256k1_ec_pubkey_serialize``](https://github.com/bitcoin-core/secp256k1/blob/master/include/secp256k1.h#L394),
  given a length argument of 33, and the ``SECP256K1_EC_COMPRESSED`` flag.
* The message must be a 32-byte hash. This is typically SHA256, but in practice,
  as long as the signature was computed against the same form as the message
  hash being verified, it will work.
* The signature must be 64 bytes. Furthermore, the encoding must correspond to
  the result produced by
  [``secp256k1_ecdsa_serialize_compact``](https://github.com/bitcoin-core/secp256k1/blob/master/include/secp256k1.h#L487).

For the Schnorr signature scheme, we have the following requirements:

* The verification key must be 32 bytes. Furthermore, the encoding must
  correspond to the result produced by
  [``secp256k1_xonly_pubkey_serialize``](https://github.com/bitcoin-core/secp256k1/blob/master/include/secp256k1_extrakeys.h#L61).
* The message can be of any length, and can contain any bytes in any position.
* The signature must be 64 bytes.

The builtin operations will error with a descriptive message if given inputs
that don't correspond to the constraints above, return `False` if the signature
fails to verify the message given the key, and `True` otherwise.

## Rationale

Implementing these functions as direct builtins in Plutus Core permits a
workflow involving interoperability services like Wanchain and Renbridge. An
example of such a workflow would be: given some Cardano assets, their Bitcoin
equivalent could be minted, but only if the correct Schnorr signature can be
provided. 

We consider the implementation trustworthy: `libsecp256k1` is the reference
implementation for both signature schemes, and is already being used in
production by Bitcoin. 

An alternative approach could be to provide low-level primitives, which would
allow any signature scheme (not just the ones under consideration here) to be
implemented by whoever needs them. While this approach is certainly more
flexible, it has two significant drawbacks:

* It requires 'rolling your own crypto', rather than re-using existing
  implementations. This has been shown historically to be a bad idea;
  furthermore, if existing implementations have undergone review and audit, and
  such re-implementations would not benefit.
* It would be significantly costlier, as the computation would happen in Plutus
  Core. Given the significant on-chain size restrictions, this would likely be
  too costly for general use: many such schemes rely on large precomputed
  tables, for example, which are totally unviable on-chain.

It may be possible that some set of primitive can avoid both of these issues
(for example, the suggestions in [this
CIP](https://github.com/cardano-foundation/CIPs/pull/220)); in the meantime,
providing direct support for commonly-used schemes such as these is worthwhile.

## Backward Compatibility

At the Plutus Core level, implementing this proposal induces no
backwards-incompatibility: the proposed new primitives do not break any existing
functionality or affect any other builtins. Likewise, at levels above Plutus
Core (such as `PlutusTx`), no existing functionality should be affected.

On-chain, this requires a hard fork.

## Path to Active

An implementation by MLabs already exists, and has been [merged into
Plutus](https://github.com/input-output-hk/plutus/pull/4368). Tests of the
functionality have also been included, although costing is currently
outstanding, as it cannot be done by MLabs due to limitations in how costing is
calculated. Costing will instead be done by the Plutus Core team.

## Copyright

This CIP is licensed under Apache-2.0.
