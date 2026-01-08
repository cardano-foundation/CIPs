---
CIP: 127
Title: ripemd-160 hashing in Plutus Core
Status: Active
Category: Plutus
Authors:
  - Tomasz Rybarczy <tomasz.rybarczyk@iohk.io>
Implementors: []
Discussions:
  - https://github.com/cardano-foundation/CIPs/pull/826
Created: 2024-05-22
License: Apache-2.0
---

## Abstract
This CIP follows closely the (CIP-0101)[^1] and proposes an extension of the current Plutus functions with another hashing primitive [`RIPEMD-160`](https://en.bitcoin.it/wiki/RIPEMD-160). Primary goal is to introduce compatibility with Bitcoin's cryptographic infrastructure.

## Motivation: Why is this CIP necessary?

The [integration](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0049/README.md) of the ECDSA and Schnorr signatures over the secp256k1 curve into Plutus was a significant step towards interoperability with Ethereum and Bitcoin ecosystems. However, full compatibility is still impossible due to the absence of the `RIPEMD-160` hashing algorithm in Plutus interpreter, which is a fundamental component of Bitcoin's cryptographic framework.
Most of common addresses in Bitcoin are derived from double [hashing procedure](https://learnmeabitcoin.com/technical/cryptography/hash-function/#hash160) involving `SHA-256` followed by `RIPEMD-160` function:
- [P2KH](https://learnmeabitcoin.com/technical/script/p2pkh/)
- [P2WPKH](https://learnmeabitcoin.com/technical/script/p2wpkh/)
- [P2SH](https://learnmeabitcoin.com/technical/script/p2sh/)
- [P2WSH](https://learnmeabitcoin.com/technical/script/p2wsh/)

Adding `RIPEMD-160` to Plutus would enhance the potential for cross-chain solutions between Cardano and Bitcoin blockchains and complements the set of primitives which we already have in that regard. It would allow for the verification of Bitcoin addresses and transactions on-chain. This addition enables also the verification of signed messages that identify the signer by the public key hash, which has not yet been witnessed on the Bitcoin blockchain.

The RIPEMD-160 is not only relevant to Bitcoin - other chains like [Cosmos](https://docs.cosmos.network/main/build/architecture/adr-028-public-key-addresses#legacy-public-key-addresses-dont-change) or [BNB](https://docs.bnbchain.org/docs/beaconchain/learn/accounts/#address) also use it for address generation.

## Specification
This proposal aims to introduce a new built-in hash function `RIPEMD-160`.

This function will be developed following the [`RIP-160`](https://homes.esat.kuleuven.be/~bosselae/ripemd160/pdf/AB-9601/AB-9601.pdf) specification and will utilize the [`cryptonite`](https://github.com/haskell-crypto/cryptonite/blob/master/Crypto/Hash/RIPEMD160.hs)

Since `cardano-base` already relies on `cryptonite` in the context of [`keccak-256`](https://github.com/input-output-hk/cardano-base/blob/master/cardano-crypto-class/src/Cardano/Crypto/Hash/Keccak256.hs) we would like to expose `RIPEMD-160` through the same library, to facilitate its integration into Plutus.

More specifically, Plutus will gain the following primitive operation:

* `ripemd_160` :: ByteString -> ByteString

The input to this function can be a `ByteString` of arbitrary size, and the output will be a `ByteString` of 20 bytes. 
Note that this function aligns with the format of existing hash functions in Plutus, such as [blake2b_256](https://github.com/input-output-hk/plutus/blob/75267027f157f1312964e7126280920d1245c52d/plutus-core/plutus-core/src/Data/ByteString/Hash.hs#L25)

## Rationale: How does this CIP achieve its goals?
While the `RIPEMD-160` function might be implemented in on-chain scripts, doing so would be computationally unfeasible.

The library, cryptonite, is not implemented by and under control of the Plutus team. However,
* It is a library already used in the Plutus stack to expose KECCAK-256, and can be considered as a trustworthy implementation.
* Its behaviour is predictable and computationally efficient. The cost of the function is linear with respect to the size of the message provided as input. This is the same behaviour that other hash functions exposed in plutus (blake, sha3, keccak-256) have.

## Path to Active

### Acceptance Criteria
- [X] A `cardano-base` binding is created for the `ripemd-160` function and included in a new version of the library.
- [X] A Plutus binding is created for the `ripemd_160` function and included in a new version of Plutus.
- [X] Integration tests, similar to those of the existing Plutus hash functions, are added to the testing infrastructure.
- [X] The function is benchmarked to assess its cost. As for other hash functions available in Plutus (blake2b, sha256 and keccak_256), we expect the cost of `ripemd_160` to be linear with respect to the size of the message. The Plutus team determines the exact costing functions empirically.
- [x] The ledger is updated to include new protocol parameters to control costing of the new builtins.
  - Included within the haskell cardano-node implementation from [10.1.1](https://github.com/IntersectMBO/cardano-node/releases/tag/10.1.1).
- [x] This CIP may transition to active status once the Plutus version containing the `ripemd_160` function is introduced in a node release and becomes available on Mainnet.
  - Enabled by Plomin hardfork

### Implementation Plan
The Plutus team will develop the binding, integration tests, and benchmarks. The E2E tests will be designed and implemented collaboratively by the testing team, the Plutus team, and community members planning to use this primitive.

## Copyright
This CIP is licensed under [Apache-2.0][https://www.apache.org/licenses/LICENSE-2.0].

[^1]: I did not hesitate to reuse parts of the original text of (CIP-0101)[../CIP-0101/README.md) without explicit quotations. This approach was approved by the original authors.
