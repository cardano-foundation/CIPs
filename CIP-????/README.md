---
CIP: ????
Title: PostQuantum signatures and native wallets
Category: Plutus
Authors:
  - Michał J. Gajda (mjgajda@migamake.com)
Implementors: []
Discussions-To: https://github.com/cardano-foundation/CIPs/pull/441
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
NIST plans to finalize standardization in 2023/2024 time frame, with US executive branch recommending
all projects to plan for post-quantum resistance by mid-2023.

## Abstract

Provides a way of verifying post-quantum signatures as recommended by NIST in Plutus Core.
New builtins will allow use of these signatures within smart contracts. These builtins work over
`BuiltinByteString`s.

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

## Use cases

Adding multiple PQC signature algorithms will allow the following:

* opt-in migration of wallets and smart contracts to safer cryptographic protocol
* pay-as-you-go for longer signatures required for post-quantum resistance
* opt-in resistance to _cryptocalypse_ - surprise breakage of a single major encryption algorithm -
  by using multiple signature algorithms for redundancy.
* compliance with US government regulations past July 2023, when all agencies
  are expected to plan post-quantum migration.

## Specification

[`DSIGN`]() class instance should be provided for the post-quantum signature algorithms.

### Plutus API

Two new builtin functions would be provided:

* A verification function for CRYSTALS(DILITHIUM) signatures; and
* A verification function for FALCON signatures;
* A verification function for SPHINCS signatures.

These would be based on NIST reference implementations,
as maintained by [`PQClean`](https://github.com/PQClean/PQClean) library.
This is a reference implementation of the three kinds of signature schemes in C. This 
implementation would be called from Haskell using direct bindings to C. These
bindings would be defined in `cardano-base`, using its existing `DSIGN`
interface, with new builtins in Plutus Core on the basis of the `DSIGN`
interface for both schemes.

The builtins would be costed as follows: each signature verification has
linear cost proportional to the number of message bits, and square with respect to key length.
_Constants will be proportional to the ratio of time as benchmarked against
Ed25519._

Since we expect adding more cryptographic signature algorithms as they evolve,
we should add datatype for selecting cryptographic algorithm:

```
data SignAlgo = Ed25519
              | Blake2
              | EcDSA
              | SECP256k1
              | Schnorr
              | Falcon
              | Sphincs
              | Dilithium
```
To facilitate extensibility, the name of algorithm should be rendered as case-insensitive text in JavaScript
([CIP-0030](https://developers.cardano.org/docs/governance/cardano-improvement-proposals/cip-0030/)).

| Cryptographic algorithm | Public key (bytes) | Signature (bytes) | Relative cost of verification (CPU) |
|:------------------------|-------------------:|------------------:|------------------------------------:|
| Ed25519                 |                 64 |                64 |                                   1 |
| Falcon512               |                897 |               666 |                                 0.5 |
| Dilithium2              |               1312 |              2420 |                                 0.5 |
| Sphincs+                |                 32 |              8080^[https://sofiaceli.com/2022/07/05/pq-signatures.html#:~:text=A%20table%20of-,comparison%20of%20sizes,-%3A] |                                 2.8^[Benchmark was for Sphins\*128s] |

  : Reference for signature, key sizes, and time cost multipliers [as suggested here](https://blog.cloudflare.com/nist-post-quantum-surprise/). In the order of preference, with comparison against current default signature algorithm (Ed25519).

The following function should then be used to verify arbitrary binary signed
with permitted signature scheme:

```
verifySignWithAlgo :: SignAlgo
                  -> BuiltinByteString -- ^ public key
                  -> BuiltinByteString -- ^ message or hash
                  -> BuiltinByteString -- ^ signature
                  -> BuiltinBool
```

This function takes parameters of a specific part of the signature scheme, even
though they are all encoded as `BuiltinByteString`s. In order, for both
functions, these are:

1. A verification key (length depends on the algorithm chosen);
2. An input to verify (either the message itself, and a hash);
3. A signature.

The two different schemes handle deserialization internally: specifically, there
is a distinction made between 'external' representations, which are expected as
arguments, and 'internal' representations, used only by the implementations
themselves. This creates different expecations for each argument for both of
these schemes; we describe these below.

For the [all signature
schemes](),
the keys are required to be given in the same format as NIST test vectors.

The builtin operations will error with a descriptive message if given inputs
that don't correspond to the constraints above, return `False` if the signature
fails to verify the input given the key, and `True` otherwise.

### Post-quantum wallets

We should permit using all chosen signature algorithms to lock transactions.

This allows an _opt-in_ migration as more and more wallet apps will support new signature schemes.

For extra safety, users may choose to use conjunction of wallet signatures as they
are already implemented in native ledger.

Note that default would be to query wallet addresses generated by hierarchical wallet schema
for each scheme.
For the signing transactions and data, function should default for existing signature
algorithm to preserve backwards compatibility.

There should be additional attributes as described by [CIP-0030](https://developers.cardano.org/docs/governance/cardano-improvement-proposals/cip-0030):

```
cardano.{walletName}.signAlgo
cardano.{walletName}.hashAlgo
```

There should be additional extension registered if [CIP on wallet extensibility](https://github.com/cardano-foundation/CIPs/pull/462).
```

Wallet providers may choose to automatically generate ultra-secure wallets for multiple quantum signature
algorithms from a single seed. In such case, they are encouraged to provide a visible
hint of what is the current preferred.

### Use of standard hash algorithm

Note that use of hash would require use of quantum-resistant hash algorithm.
[SHA2, SHA3, BLAKE2 are considered quantum-safe](https://cryptobook.nakov.com/quantum-safe-cryptography#quantum-safe-and-quantum-broken-crypto-algorithms),
in particular standard 256-bit hash used in Cardano [should be safe for a long time](https://cryptobook.nakov.com/quantum-safe-cryptography#quantum-safe-and-quantum-broken-crypto-algorithms).
This should be documented in the Plutus documentation of `verifySignature`.

However, in the interest of long-term API evolution we propose to add a flexible hashing interface:

```
data SignAlgo = SHA2_256
              | SHA3_256
              | Blake2

hashWithAlgo :: HashAlgo -> BuiltinByteString -> BuiltinByteString
```

This will also allow for gradual _opt-in_ migration of scripts as the blockchain evolves.

### Long term API evolution

It would be desirable to also offer a long-term API that would not need any changes
as we migrate blockchain to new algorithms.

This would be to provide an implicit embedding of a most secure available hashing algorithm
within the hash itself, and use of interface:

```
data LTSignature = LongTermSignature {
                     ltsHashAlgo :: HashAlgo
                   , ltsSignAlgo :: SignAlgo
                   , ltsSignature :: BuiltinByteString
                   }

verifyLongTermSignature :: BuiltinByteString                       -- ^ public key
                        -> LongTermSignature                       -- ^ message or hash
                        -> BuiltinByteString                       -- ^ signature
                        -> Bool  -- is hash valid

isLongTermSignatureSecure :: LongTermSignature -> Bool
```

Supporting evolution of hash algorithms is much simpler:

```
-- | Long term hash
data LongTermHash = LongTermHash {
                      hashAlgo :: HashAlgo
                    , hash     :: BuiltingByteString
                    }

mostSecureHashAlgo :: HashAlgo

mostSecureHash :: BuiltinByteString -> LongTermHash
mostSecureHash = hashWithAlgo mostSecureHash
```

This API needs additional support from the off-chain applications in order to:

* provide correct public key for the given algorithm
* help users to transfer their euTxOs to new signature algorithms when old algorithms are obsoleted.

Note that `LongTermHash` and `LongTermSignature` can be implemented as standard library functions.

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

## Discussion full quantum resistance

This CIP _does not_ provide for full quantum resistance of the Cardano blockchain yet,
in order to decrease cost of implementation.

SHA-256 hash is considered [_safe for a long-time yet_](https://cryptobook.nakov.com/quantum-safe-cryptography#quantum-safe-and-quantum-broken-crypto-algorithms), and any future upgrade would only need to consider SHA-384 as far as we know.
The main concern would be the public key signatures used for entire wallet infrastructure.
That is why we propose an _opt-in_ scheme, where users may gradually choose to migrate towards safer, post-quantum cryptography
over the course of few years.
That would make Cardano permit **quantum-resistant** smart contracts today at negligible cost,
and assure **long-term viability** of those smart contracts that will be deployed in the near future.

[Long-term document storage](https://adastamp.co) is a killer application for the blockchain.
While any single signature may be obsoleted, this application adds new signatures for each document
that keep integrity of the document and prolong its validity.

## Copyright

This CIP is licensed under Apache-2.0.
