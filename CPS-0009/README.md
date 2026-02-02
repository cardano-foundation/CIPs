---
CPS: 9
Title: Coin Selection Including Native Tokens
Category: Wallets
Status: Open
Authors:
  - Hinson Wong <wongkahinhinson@gmail.com>
  - Tsz Wai Wu <wu.tszwai@outlook.com>
Proposed Solutions: []
Discussions:
  - Motivating issue: https://github.com/cardano-foundation/CIPs/issues/232
  - Original pull request: https://github.com/cardano-foundation/CIPs/pull/611
Created: 2023-10-20
License: CC-BY-4.0
---

## Abstract

The introduction of native tokens in Cardano has introduced unique challenges related to coin selection and transaction efficiency. This Cardano Problem Statement (CPS) addresses the need for a specialized coin selection approach to optimize transactions involving native tokens while minimizing transaction size and complexity.

## Problem

The integration of native tokens in Cardano transactions has brought both opportunities and challenges. One of the significant challenges is associated with coin selection when dealing with native tokens.

### 1. Need for Efficient Coin Selection

Cardano transactions involving native tokens require attaching a minUTxO value (lovelace) to the transaction. In scenarios where multiple tokens are associated with a single UTxO, selecting such UTxOs as inputs can lead to inefficient transactions. This inefficiency arises from the increased transaction size due to token information, potentially impacting the decentralized applications and network performance.

### 2. Streamlining the Selection Process

Streamlining the selection process is crucial. Enhancements should be made to the selection algorithms to ensure that, even in complex scenarios, the coin selection process remains efficient and doesn't compromise the user experience.

### 3. Compatibility with Serialization Libraries

The largest off-chain serialization library, `cardano-serialization-lib`, still follows a modified version of the [CIP-2 standard](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0002/README.md), which was established in the pre-native token era. There's a need to ensure that the proposed coin selection approach remains compatible with existing serialization libraries, making it accessible to a wider range of developers and applications.

While CIP-2 certainly works well in an environment where native assets such as tokens and NFTs don't exist, it has been expanded upon differently by each serialization library, with their own custom solutions to select for tokens. It would be useful to once again have some standard for coin selection that is trusted by the community.

### 4. Min UTxO Value for change with tokens

CIP-2 doesn't consider `minUTxOValue` in the change output with tokens, if a pure ADA change output cannot be created that reaches the `minUTxOValue`, it is possible to simply increase the fees paid for the transaction by that small amount to balance the transaction. This, however, doesn't work when tokens are involved, any tokens in the transaction inputs MUST be included in the change output.

## Use Cases

### Native Token Transactions

Users and applications frequently engage in native token transactions, making efficient coin selection essential to minimize transaction costs and network congestion.

### DApps and DeFi

Decentralized applications and DeFi projects require efficient coin selection to maintain the performance and cost-effectiveness of their transactions.

### Example Implementations

Some real world use cases of coin selection algorithms taking Native Tokens into account are listed below:
1. [UTxO utils of Cardano in WASM](https://www.npmjs.com/package/cardano-utxo-wasm)
2. [Cardano Wallet](https://github.com/cardano-foundation/cardano-wallet/tree/master/lib/coin-selection)
3. [cardano-multiplatform-lib](https://github.com/dcSpark/cardano-multiplatform-lib)
4. [RoundTable](https://github.com/ADAOcommunity/round-table)

### Network Scalability

Efficient coin selection contributes to network scalability by reducing the size and complexity of transactions, ensuring smooth and rapid processing.

## Goals

### Specialized Coin Selection Approach

The primary goal of this CPS is to establish a specialized coin selection approach for transactions involving native tokens in Cardano. This approach should prioritize necessary tokens, improve transaction efficiency, and minimize the impact of native token inclusion on transaction size.

### Consider change and fees

In Cardano, there is somewhat of a cyclic dependency between UTxO selection, change output and fees. It would be extremely helpful if some consensus was reached on how to handle this part of transaction building. Since the most naïve approach essentially requires rebuilding the transaction several times, there is potential to significantly reduce latency in DApps with a more efficient approach.

### Useful change outputs

CIP-2 also selects inputs in order to generate "useful" change outputs. This will be a significantly more complex problem when native tokens are considered, but will significantly improve the collective efficiency of transaction generation in wallets.

### Streamlined Transactions

By optimizing coin selection, we aim to streamline Cardano transactions, reducing their size and complexity while preserving the integrity of native token operations.

### Cross-Compatibility

The proposed approach should remain compatible with existing off-chain serialization libraries and protocols, ensuring accessibility to a wide range of developers and projects.

### Improved Network Performance

Efficient coin selection contributes to overall network performance, making Cardano more scalable and reliable for users, DApps, and DeFi.

## Open Questions

### Implementation

1. How can we effectively implement and promote the specialized coin selection approach?
2. What changes, enhancements, or protocols need to be adopted within the Cardano ecosystem to achieve this?
3. Is there any community collective intelligence could gather for this area? Particularly, would engineers from Emurgo (who maintain `cardano-serialization-lib`) and developers of `cardano-multiplatform-lib` have any form of insight to push forth community progress?

### Developer Education

1. Are there any changes on application code itself with improvements on coin selection algorithms?
2. If so, how can developers be educated and informed about any new coin selection approach to ensure its successful adoption and integration into their projects?

### Community Consensus

1. How can we gather and build consensus within the Cardano community regarding any proposed coin selection approach?
2. Do we need any support from academia with formal proof to impose the standard?
3. What methods can be employed to ensure widespread acceptance and adoption? Do we need endorsement from any of IOHK, CF or Emurgo?
4. If academic formal research is not needed for this consensus, how can we set the bar for an acceptable algorithm? Would there be a core committee making the decision?

## Copyright

This CPS is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
