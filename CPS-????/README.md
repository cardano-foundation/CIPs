---
CPS: ????
Title: Linking Off-Chain identity solutions to On-Chain Transactions
Status: Open
Category: Tools
Authors:
  - 
Proposed Solutions:
  - 
Discussions:
  - 
Created: 2025-07-09
License: _
---

## Abstract

Transactions often involve multiple parties, including individuals and organisations.
To facilitate these interactions, it is essential to have a reliable way to verify the identities of participants.
Most of the organisations have off-chain identities, which they could leverage to enhance the trust and security of their on-chain transactions. 
Off-chain identities could be solutions like: [GLEIF](https://www.gleif.org/en), [KERI Identifiers](https://identity.foundation/keri/), ...
While Cardano's on-chain data model provides a robust framework for transaction verification, it lacks a standardized mechanism for off-chain identity verification.

This limitation makes it difficult to verify the identity of participants, establish trust, and comply with regulatory requirements.
This problem statement outlines the need for a standardized solution for off-chain identity verification on Cardano to enhance trust, security, and adoption.

## Problem

The core problem is the absence of a standardized, self-sustaining and user-friendly solution for linking decentralized off-chain identifiers to on-chain transaction on the Cardano blockchain.
This gap creates several challenges:
- **Trust and Security**: Without a reliable way to verify identities, it is difficult to establish trust between parties involved in transactions. This can lead to fraud, manipulation, and other security issues.
- **Compliance**: Many industries require strict compliance with regulations related to identity verification. The lack of a standardized solution makes it challenging for businesses and organizations to meet these requirements.
- **User Experience**: Current solutions for off-chain identity verification are often fragmented and complex, leading to a poor user experience. Making it impossible for others to integrate these solutions e.g. explorers

## Use cases
The need for a standardized solution for decentralized off-chain identity verification on Cardano is driven by several use cases, including:
- **Accountability**: When publishing financial reports, it is essential to verify the identity of the individuals or organizations responsible for the report. This helps to ensure that the information is accurate and trustworthy.
- **Supply Chain Tracking**: In supply chain, parties involved in the process need to verify the identity of each other to ensure that the products are genuine and meet quality standards.
  This is particularly important in industries such as pharmaceuticals, where counterfeit products can have serious consequences.

## Goals

The goal of this problem statement is to initiate a discussion within the Cardano community about the need for a standardized framework for off-chain identity verification.
The ultimate objective is to develop a solution that:
- **Is secure and trustworthy**: The solution should provide a high degree of security and be resistant to fraud and manipulation.
- **Is self-sustaining**: The solution should be able to operate independently of any single entity or organization, ensuring decentralization and resilience.
- **Is interoperable**: The solution should be compatible with a wide range of applications and services. (For example easy to integrate into existing solutions, like explorers, wallets, and dApps.)
- **Is compliant with regulations**: The solution should help businesses and organizations to comply with relevant regulations.

The solution should be able to handle different types of identify solutions, so it shouldn't be tied to a specific identity solution, but rather provide a framework for integrating different solutions.