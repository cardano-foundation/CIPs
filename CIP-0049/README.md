---
CIP: 49
Title: ECDSA and Schnorr signatures in Plutus Core
Authors: Koz Ross (koz@mlabs.city), Michael Peyton-Jones (michael.peyton-jones@iohk.io), Iñigo Querejeta Azurmendi (querejeta.azurmendi@iohk.io)
Discussions-To: koz@mlabs.city
Status: Proposed
Type: Standards Track
Created: 2022-04-27
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
Renbridge, which use SECP256k1 signatures for verification. Lastly, if we can
verify Schnorr signatures, we can also verify Schnorr-compatible multi or
threshold signatures, such as [MuSig2](https://eprint.iacr.org/2020/1261.pdf) or
[Frost](https://eprint.iacr.org/2020/852).

## Specification

Two new builtin functions would be provided:

* A verification function for ECDSA signatures using the SECP256k1 curve; and
* A verification function for Schnorr signatures using the SECP256k1 curve.

These would be based on [`secp256k1`](https://github.com/bitcoin-core/secp256k1), 
a reference implementation of both kinds of signature scheme in C. This 
implementation would be called from Haskell using direct bindings to C. These
bindings would be defined in `cardano-base`, using its existing `DSIGN`
interface, with new builtins in Plutus Core on the basis of the `DSIGN`
interface for both schemes.

The builtins would be costed as follows: ECDSA signature verification has
constant cost, as the message, verification key and signature are all
fixed-width; Schnorr signature verification is instead linear in the message
length, as this can be arbitrary, but as the length of the verification key and
signature are constant, the costing will be constant in both.

More specifically, Plutus would gain the following primitive operations:

* `verifyEcdsaSecp256k1Signature :: BuiltinByteString -> BuiltinByteString ->
  BuiltinByteString -> BuiltinBool`, for verifying 32-byte message hashes signed 
  using the ECDSA signature scheme on the SECP256k1 curve; and
* `verifySchnorrSecp256k1Signature :: BuiltinByteString -> BuiltinByteString
  -> BuiltinByteString -> BuiltinBool`, for verifying arbitrary binary messages 
  signed using the Schnorr signature scheme on the SECP256k1 curve.

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

For the [ECDSA signature
scheme](https://en.bitcoin.it/wiki/Elliptic_Curve_Digital_Signature_Algorithm),
the requirements are as follows. Note that these differ from the serialization
used by Bitcoin, as the serialisation of signatures uses DER-encoding, which 
result in variable size signatures up to 72 bytes (instead of the 64 byte encoding
we describe in this document).

* The verification key must correspond to the _(x, y)_ coordinates of a point 
  on the SECP256k1 curve, where _x, y_ are unsigned integers in big-endian form.
* The verification key must correspond to a result produced by
  [``secp256k1_ec_pubkey_serialize``](https://github.com/bitcoin-core/secp256k1/blob/master/include/secp256k1.h#L394), 
  when given a length argument of 33, and the ``SECP256K1_EC_COMPRESSED`` flag.
  This implies all of the following:
    * The verification key is 33 bytes long.
    * The first byte corresponds to the parity of the _y_ coordinate; this is
      `0x02` if _y_ is even, and `0x03` otherwise.
    * The remaining 32 bytes are the bytes of the _x_ coordinate.
* The input to verify must be a 32-byte hash of the message to be checked. We 
  assume that the caller of `verifyEcdsaSecp256k1Signature` receives the 
  message and hashes it, rather than accepting a hash directly: doing so 
  [can be dangerous](https://bitcoin.stackexchange.com/a/81116/35586).
  Typically, the hashing function used would be SHA256; however, this is not
  required, as only the length is checked.
* The signature must correspond to two unsigned integers in big-endian form;
  henceforth _r_ and _s_.
* The signature must correspond to a result produced by
  [``secp256k1_ecdsa_serialize_compact``](https://github.com/bitcoin-core/secp256k1/blob/master/include/secp256k1.h#L487).
  This implies all of the following:
    * The signature is 64 bytes long.
    * The first 32 bytes are the bytes of _r_.
    * The last 32 bytes are the bytes of _s_.
  ``` 
      ┏━━━━━━━━━━━━━━┯━━━━━━━━━━━━━━━┓
      ┃ r <32 bytes> │ s <32 bytes>  ┃
      ┗━━━━━━━━━━━━━━┷━━━━━━━━━━━━━━━┛
      <--------- signature ---------->
  ```
For the Schnorr signature scheme, we have the following requirements, as
described in the requirements for [BIP-340](https://github.com/bitcoin/bips/blob/master/bip-0340.mediawiki):

* The verification key must correspond to the _(x, y)_ coordinates of a point 
  on the SECP256k1 curve, where _x, y_ are unsigned integers in big-endian form.
* The verification key must correspond to a result produced by 
  [``secp256k1_xonly_pubkey_serialize``](https://github.com/bitcoin-core/secp256k1/blob/master/include/secp256k1_extrakeys.h#L61).
  This implies all of the following:
    * The verification key is 32 bytes long.
    * The bytes of the signature correspond to the _x_ coordinate.
* The input to verify is the message to be checked; this can be of any length,
  and can contain any bytes in any position.
* The signature must correspond to a point _R_ on the SECP256k1 curve, and an
  unsigned integer _s_ in big-endian form.
* The signature must follow the BIP-340 standard for encoding. This implies all
  of the following:
    * The signature is 64 bytes long.
    * The first 32 bytes are the bytes of the _x_ coordinate of _R_, as a 
      big-endian unsigned integer.
    * The last 32 bytes are the bytes of `s`.
  ``` 
      ┏━━━━━━━━━━━━━━┯━━━━━━━━━━━━━━━┓
      ┃ R <32 bytes> │ s <32 bytes>  ┃
      ┗━━━━━━━━━━━━━━┷━━━━━━━━━━━━━━━┛
      <--------- signature ---------->
  ```

The builtin operations will error with a descriptive message if given inputs
that don't correspond to the constraints above, return `False` if the signature
fails to verify the input given the key, and `True` otherwise.

## Rationale

We consider the implementation trustworthy: `secp256k1` is the reference
implementation for both signature schemes, and is already being used in
production by Bitcoin. Specifically, ECDSA signatures over the SECP256k1 curve
were used by Bitcoin before Taproot, while Schnorr signatures over the same
curve have been used since Taproot.

An alternative approach could be to provide low-level primitives, which would
allow any signature scheme (not just the ones under consideration here) to be
implemented by whoever needs them. While this approach is certainly more
flexible, it has two significant drawbacks:

* It requires 'rolling your own crypto', rather than re-using existing
  implementations. This has been shown historically to be a bad idea;
  furthermore, if existing implementations have undergone review and audit, any
  such re-implementations would give us the same assurances as those that have
  been reviewed and audited.
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
