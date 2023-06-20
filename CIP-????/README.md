---
CIP: ?
Title: Integration of `keccak256` into Plutus
Status: Proposed
Category: Plutus
Authors: 
  - Sergei Patrikeev <so.patrikeev@gmail.com>
  - Iñigo Querejeta-Azurmendi <inigo.querejeta@iohk.io>
Implementors: []
Discussions: 
  - https://github.com/cardano-foundation/CIPs/pull/524
Created: 2023-06-13
License: Apache-2.0
---

## Abstract
This CIP proposes an extension of the current Plutus functions to provide support for the [`keccak256`](https://keccak.team/files/Keccak-submission-3.pdf) hashing algorithm,
primarily to ensure compatibility with Ethereum's cryptographic infrastructure.

## Motivation

The [integration](https://github.com/input-output-hk/cardano-base/pull/252) of the ECDSA and Schnorr signatures over the secp256k1 curve into Plutus was a significant 
step towards interoperability with Ethereum and Bitcoin ecosystems. However, full compatibility is still impossible 
due to the absence of the `keccak256` hashing algorithm in Plutus interpreter, 
which is a fundamental component of Ethereum's cryptographic framework:
- data signing standard [EIP-712](https://eips.ethereum.org/EIPS/eip-712), 
- `keccak256` is the hashing algorithm underlying Ethereum's ECDSA signatures. 
- EVM heavily [depends](https://ethereum.github.io/yellowpaper/paper.pdf) on `keccak256` for internal state management

Adding `keccak256` to Plutus would enhance the potential for cross-chain solutions between Cardano and EVM-based blockchains.

## Specification
`keccak256` function is already available in [cardano-base](https://github.com/input-output-hk/cardano-base/blob/master/cardano-crypto-class/src/Cardano/Crypto/Hash/Keccak256.hs).
The changes would require a single function to be added to Plutus.

## Rationale
While the `keccak256` function might be implemented in on-chain scripts, doing so would be computationally unfeasible. 

## Path to Proposed
This Draft is ready to be moved to Proposed.

### Trustworthiness of Implementations
The implementation of `keccak256` is based on the version found in the [cardano-base](https://github.com/input-output-hk/cardano-base/blob/master/cardano-crypto-class/src/Cardano/Crypto/Hash/Keccak256.hs) library.

## Backward Compatibility
The addition of `keccak256` is backward compatible and will not interfere with existing functions within Plutus.

## Path to Active
Upon successful review and evaluation, the `keccak256` function is planned for release in an upcoming update.

## References
- [CIP-49](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0049/README.md): ECDSA and Schnorr signatures in Plutus Core 
- keccak256: https://keccak.team/files/Keccak-submission-3.pdf
- Ethereum Yellow Paper: https://ethereum.github.io/yellowpaper/paper.pdf
- Ethereum standard on signing data: https://eips.ethereum.org/EIPS/eip-712