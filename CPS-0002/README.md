---
CPS: 2
Title: Coin Selection Approach for Post Native Tokens Era in Cardano
Status: Open
Category: Plutus
Authors:
  - Hinson Wong <wongkahinhinson@gmail.com>
  - Tsz Wai Wu <wu.tszwai@outlook.com>
Proposed Solutions:
  - []
Discussions:
  - https://github.com/sidan-lab/CIPs/discussions
  - https://discord.gg/uznpyACq
Created: 2023-10-20
---

## Abstract

The introduction of native tokens in Cardano has introduced unique challenges related to coin selection and transaction efficiency. This Cardano Problem Statement (CPS) addresses the need for a specialized coin selection approach to optimize transactions involving native tokens while minimizing transaction size and complexity.

## Problem

The integration of native tokens in Cardano transactions has brought both opportunities and challenges. One of the significant challenges is associated with coin selection when dealing with native tokens.

### 1. Need for Efficient Coin Selection

Cardano transactions involving native tokens often require attaching a minUTxO value (lovelace) to the transaction. In scenarios where multiple tokens are associated with a single UTxO, selecting such UTxOs as inputs can lead to inefficient transactions. This inefficiency arises from the increased transaction size due to token information, potentially impacting the decentralized applications and network performance.

### 2. Prioritizing Necessary Tokens

To improve the efficiency of Cardano transactions, there is a need to prioritize the selection of necessary tokens while excluding unnecessary ones. This prioritization will help reduce the inflation of transaction sizes, making them more streamlined and cost-effective.

### 3. Streamlining the Selection Process

In addition to token prioritization, streamlining the selection process is crucial. Enhancements should be made to the selection algorithms to ensure that even in complex scenarios, the coin selection process remains efficient and doesn't compromise the user experience.

### 4. Compatibility with Serialization Libraries

The largest off-chain serialization library, such as cardano-serialization-lib, still follows the CIP-2 standard, which was established in the pre-native token era. There's a need to ensure that the proposed coin selection approach remains compatible with existing serialization libraries, making it accessible to a wider range of developers and applications.

## Use Cases

### Native Token Transactions

Users and applications frequently engage in native token transactions, making efficient coin selection essential to minimize transaction costs and network congestion.

### DApps and DeFi

Decentralized applications and DeFi projects require efficient coin selection to maintain the performance and cost-effectiveness of their transactions.

### Network Scalability

Efficient coin selection contributes to network scalability by reducing the size and complexity of transactions, ensuring smooth and rapid processing.

## Goals

### Specialized Coin Selection Approach

The primary goal of this CPS is to establish a specialized coin selection approach for transactions involving native tokens in Cardano. This approach should prioritize necessary tokens, improve transaction efficiency, and minimize the impact of native token inclusion on transaction size.

### Streamlined Transactions

By optimizing coin selection, we aim to streamline Cardano transactions, reducing their size and complexity while preserving the integrity of native token operations.

### Cross-Compatibility

The proposed approach should remain compatible with existing off-chain serialization libraries and protocols, ensuring accessibility to a wide range of developers and projects.

### Improved Network Performance

Efficient coin selection contributes to overall network performance, making Cardano more scalable and reliable for users, DApps, and DeFi.

## Open Questions

### Implementation

How can we effectively implement and promote the specialized coin selection approach? What changes, enhancements, or protocols need to be adopted within the Cardano ecosystem to achieve this?

### Developer Education

How can developers be educated and informed about the new coin selection approach to ensure its successful adoption and integration into their projects?

### Community Consensus

How can we gather and build consensus within the Cardano community regarding the proposed coin selection approach? What methods can be employed to ensure widespread acceptance and adoption?
