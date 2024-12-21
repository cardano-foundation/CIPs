---
CPS: ???
Title: eBTC – A Trustless BTC Bridge on Cardano
Category: Standards / Token
Authors:
  - An <anrodz42@gmail.com>
Implementors:
  - TBD
Status: Draft
Created: 2024-12-21
License: CC-BY-4.0
Discussions:
  - https://forum.cardano.org/t/ebtc-a-trustless-btc-bridge-on-cardano/141117
---

## Abstract

This document defines eBTC: a trustless, one-way bridge for bringing Bitcoin (BTC) value onto Cardano as a native token. Users burn BTC on Bitcoin’s chain and submit cryptographic proofs (e.g., using NIPoPoW [1]) to a Cardano smart contract, which mints a corresponding quantity of eBTC. Unlike custodial “wrapped” models, eBTC requires no trusted third parties or oracles. Instead, proofs rely on Bitcoin’s proof-of-work, maintaining a decentralized approach. The aim is to create a **Cardano Proposed Standard (CPS)** for seamlessly integrating BTC liquidity and functionality within Cardano’s ecosystem—without modifying core Cardano or Bitcoin protocols.

## Motivation: Why is this CPS necessary?

1. **Expand BTC Use Cases**
   Bitcoin’s scripting is limited, preventing direct DeFi, NFT, or complex smart contract interactions. By bridging BTC onto Cardano (via eBTC), BTC holders can access decentralized finance, identity solutions, token swaps, and other advanced features built on Cardano.

2. **Trustless Design**
   Existing wrapped BTC tokens generally depend on custodians, exposing users to counterparty and management risks. eBTC eliminates this reliance by using cryptographic proofs of BTC “burn” directly validated through a Cardano smart contract.

3. **One-Way Migration**
   Burning BTC is irreversible, which simplifies the bridging mechanism and preserves decentralization. Users trade the finality of BTC for eBTC’s functionality on Cardano. This is ideal for those who want direct, trust-minimized access to Cardano’s DeFi and dApp ecosystem.

4. **Avoiding Protocol Changes**
   Since eBTC does not require alterations to the Cardano ledger rules or Bitcoin’s consensus, it remains a purely application-layer standard, making it suitable as a CPS rather than a CIP.

5. **Decimal Expansion**
   BTC transactions can involve many decimal places, so eBTC must provide enough precision (e.g., 8 or more decimals) to handle fractional satoshis. This approach prevents rounding or liquidity fragmentation.

## Specification

### Core Components

1. **Burn Operation**
   - The user sends their BTC to a publicly known “burn address” on Bitcoin, rendering those BTC unspendable.
   - This action permanently removes the burned BTC from circulation in Bitcoin.

2. **Proof Construction**
   - The user collects a minimal set of Bitcoin block headers and Non-Interactive Proofs of Proof-of-Work (NIPoPoW) [1].
   - This proof demonstrates that the burn transaction is included in the main Bitcoin chain up to a certain block height.

3. **Proof Submission**
   - The user submits the proof to a dedicated Plutus contract on Cardano.
   - Upon successful verification, the contract mints new eBTC for the user, at a 1:1 ratio with the burned BTC amount.

4. **State Management (Cumulative Burn Model)**
   - Users periodically provide updated proofs referencing progressively higher Bitcoin block heights.
   - The contract maintains each user’s “cumulative burned BTC” total.
   - When a new proof shows a higher burn total, the script mints the difference in eBTC.
   - This approach avoids logging each transaction ID individually, simplifying on-chain data.

5. **User Ownership**
   - Users demonstrate control over their unique Bitcoin burn address (e.g., by signing a message).
   - Once associated with a Cardano address, only that user can claim eBTC tied to burns from that specific BTC address.
   - No central registry is needed; all verification is done through cryptographic proofs on-chain.

### Rationale: How does this CPS achieve its goals?

- **Decentralized**: No single custodian or oracle is involved. The security model relies on Bitcoin’s proof-of-work, validated via NIPoPoW in Plutus.
- **Secure**: The burn transaction is irreversible, ensuring no double-spend. The minimal block headers and proofs reduce the attack surface.
- **Simple & Scalable**: A one-way bridge is conceptually simpler. The cumulative burn approach avoids state bloat.
- **Self-Contained**: Because the approach uses existing Cardano smart-contract capabilities (Plutus) and standard Bitcoin transactions, no changes to either network’s consensus or ledger rules are required.

## Path to Acceptance

Since this is a CPS, its path to acceptance involves:

1. **Community Discussion**
   - Ongoing reviews and debates in public forums, e.g., Cardano Forum threads, developer chats, or GitHub PRs.
   - Incorporate feedback from SPOs, wallet devs, DApp builders, and other stakeholders.

2. **Prototype Implementation**
   - A reference Plutus script or library demonstrating how to parse minimal Bitcoin headers and validate proofs.
   - Example transactions burned on Bitcoin testnet for demonstration, then minted as eBTC on a Cardano test environment.

3. **Open-Source Release**
   - Publish code repositories under permissive licenses (e.g., Apache 2.0 or MIT).
   - Provide documentation guiding users on how to generate proofs, submit them, and interact with the contract.

4. **Adoption & Tooling**
   - Encourage wallet providers and DApps to add eBTC support.
   - If widely adopted, eBTC can become a de facto standard for bridging BTC to Cardano.

## Security Considerations

1. **Bitcoin Forks or Reorgs**
   - The smart contract should only trust burn proofs after sufficient confirmations to reduce risk of chain reorganization.
   - The number of confirmations is configurable (e.g., 6, 12, or more), balancing user convenience and safety.

2. **Header Validation**
   - The Plutus script or an off-chain aggregator needs to validate chain difficulty and check proof-of-work compliance.
   - NIPoPoW data must match actual Bitcoin main chain history.

3. **Proof Spam / DOS**
   - Because each on-chain submission requires Cardano transaction fees, spam should be uneconomical.
   - Off-chain proof generation is intentionally computational, limiting frivolous creation.

4. **Irreversibility**
   - BTC burned is permanently lost to the user if they decide they no longer want eBTC. This tradeoff must be clear.

## Implementation Plan

1. **MVP**
   - Implement a sample Plutus script that checks minimal block headers and NIPoPoW-based inclusion proofs.
   - Test with small burns on Bitcoin testnet, verifying eBTC minting on Cardano testnet.

2. **Public Testing & Audit**
   - Invite experts to review code and logic.
   - Address performance constraints, storage challenges, or potential exploits.

3. **Mainnet Deployment**
   - Deploy final contract on Cardano mainnet once robustly tested and audited.
   - Establish recommended best practices (e.g., block confirmation thresholds).

4. **Ecosystem Integration**
   - Approach wallet providers and DEXes to list eBTC.
   - Encourage dApps to adopt eBTC as collateral or payment.

## References

[1] Non-Interactive Proofs of Proof-of-Work (NIPoPoWs). A. Kiayias et al. https://eprint.iacr.org/2017/963.pdf.
