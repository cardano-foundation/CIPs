---
CIP: 101
Title: Integration of keccak256 into Plutus
Status: Proposed
Category: Plutus
Authors: 
  - Sergei Patrikeev <so.patrikeev@gmail.com>
  - Iñigo Querejeta-Azurmendi <inigo.querejeta@iohk.io>
Implementors:
  - Michael Peyton Jones <michael.peyton-jones@iohk.io>
Discussions: 
  - https://github.com/cardano-foundation/CIPs/pull/524
Created: 2023-06-13
License: Apache-2.0
---

## Abstract
This CIP proposes an extension of the current Plutus functions to provide support for the [`keccak256`](https://keccak.team/files/Keccak-submission-3.pdf) hashing algorithm,
primarily to ensure compatibility with Ethereum's cryptographic infrastructure.

## Motivation: Why is this CIP necessary?

The [integration](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0049/README.md) of the ECDSA and Schnorr signatures over the secp256k1 curve into Plutus was a significant 
step towards interoperability with Ethereum and Bitcoin ecosystems. However, full compatibility is still impossible 
due to the absence of the `keccak256` hashing algorithm in Plutus interpreter, 
which is a fundamental component of Ethereum's cryptographic framework:
- data signing standard [EIP-712](https://eips.ethereum.org/EIPS/eip-712), 
- `keccak256` is the hashing algorithm underlying Ethereum's ECDSA signatures. 
- EVM heavily [depends](https://ethereum.github.io/yellowpaper/paper.pdf) on `keccak256` for internal state management

Adding `keccak256` to Plutus would enhance the potential for cross-chain solutions between Cardano and EVM-based blockchains.

A compelling integration that would greatly benefit from `keccak256` support on the Cardano blockchain is [Hyperlane](https://hyperlane.xyz/).
Hyperlane is a permissionless interoperability layer that facilitates communication of arbitrary data between smart contracts across multiple blockchains. Hyperlane's [interchain security modules](https://docs.hyperlane.xyz/docs/protocol/sovereign-consensus)
rely on the verification of specific cryptographic proofs from one chain to another. These proofs utilize the `keccak256` hash to calculate consistent cross-chain message IDs.
The multi-signature module verifies that a majority of off-chain validators have signed an ECDSA signature over a `keccak256` digest, a common practice in EVM.

While Hyperlane [can support](https://github.com/hyperlane-xyz/hyperlane-monorepo/issues/2399) different cryptographic primitives for non-EVM chains, doing so could compromise censorship resistance, resulting in only limited support for Cardano in Hyperlane. By implementing this CIP, Cardano could fully integrate with Hyperlane's security modules, enabling Cardano smart contracts to communicate with any blockchain supported by Hyperlane.

## Specification
This proposal aims to introduce a new built-in hash function `keccak_256`.

This function will be developed following the [`keccak256`](https://keccak.team/files/Keccak-submission-3.pdf) specification 
and will utilize the [cryptonite](https://github.com/haskell-crypto/cryptonite/blob/master/Crypto/Hash/Keccak.hs) implementation. 
Since `cryptonite` is already a part of the [`cardano-base`](https://github.com/input-output-hk/cardano-base/blob/master/cardano-crypto-class/src/Cardano/Crypto/Hash/Keccak256.hs), 
this simplifies its integration into Plutus. The cost of the `keccak_256` operation will scale linearly with the length of the message.

More specifically, Plutus will gain the following primitive operation:

* `keccak_256` :: ByteString -> ByteString

The input to this function can be a `ByteString` of arbitrary size, and the output will be a `ByteString` of 32 bytes. 
Note that this function aligns with the format of existing hash functions in Plutus, such as [blake2b_256](https://github.com/input-output-hk/plutus/blob/75267027f157f1312964e7126280920d1245c52d/plutus-core/plutus-core/src/Data/ByteString/Hash.hs#L25)

## Rationale: How does this CIP achieve its goals?
While the `keccak256` function might be implemented in on-chain scripts, doing so would be computationally unfeasible. 

The library, cryptonite, is not implemented by and under control of the Plutus team. However, 
* It is a library already used in the Cardano stack to expose SHA3, and can be considered as a trustworthy implementation. 
* The function does not throw any exceptions as hash functions are defined to work with any ByteString input. It does not expect a particular particular structure. 
* It's behaviour is predictable. As mentioned above, the cost of the function is linear with respect to the size of the message provided as input. This is the same behaviour that other hash functions exposed in plutus (blake, sha3) have.
## Path to Active
This CIP may transition to active status once the Plutus version containing the `keccak_256` function is introduced 
in a node release and becomes available on Mainnet.

### Acceptance Criteria
* A Plutus binding is created for the `keccak256` function and included in a new version of Plutus.
* Integration tests, similar to those of the existing Plutus hash functions, are added to the testing infrastructure.
* The function is benchmarked to assess its cost. As for other hash functions available in Plutus (blake2b and sha256), we expect the cost of keccak to be linear with respect to the size of the message. The Plutus team determines the exact costing functions empirically.
* The ledger is updated to include new protocol parameters to control costing of the new builtins.

### Implementation Plan
The Plutus team will develop the binding, integration tests, and benchmarks. The E2E tests will be designed and implemented 
collaboratively by the testing team, the Plutus team, and community members planning to use this primitive.

## Copyright
This CIP is licensed under [Apache-2.0][https://www.apache.org/licenses/LICENSE-2.0]. 
