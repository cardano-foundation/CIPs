---
CPS: 17
Title: eBTC – A Trustless BTC Bridge on Cardano
Category: Standards / Token
Authors: An <anrodz42@gmail.com>
Status: Draft
Created: 2024-12-20
License: CC-BY-4.0
---

## Abstract

This proposal defines **eBTC**: a trustless, one-way bridge allowing BTC to enter Cardano as a native token. Users burn BTC on Bitcoin and present cryptographic proofs (NIPoPoW/SPV) to a Cardano smart contract, which mints a corresponding amount of eBTC. This solution removes reliance on custodians and oracles, enabling purely decentralized conversion and unlocking BTC’s liquidity for Cardano DeFi.

## Motivation

1. **Expand BTC Use Cases**: Enable advanced DeFi, NFTs, and smart contracts for BTC-derived value without centralized wrappers.
2. **Trustless Design**: Existing “wrapped BTC” models rely on custodians. This CIP removes single points of failure.
3. **One-Way Simplification**: Irreversibility ensures finality. No need for complex two-way bridging with Bitcoin’s limited scripting.

## Specification

### Key Components

1. **Burn Operation**
    
    - User sends BTC to an unspendable “burn” address.
    - This permanently removes BTC from circulation.
2. **Proof Construction**
    
    - User gathers minimal block headers to prove transaction inclusion.
    - Uses NIPoPoW or SPV-like approach.
    - Merkle proof shows burned transaction is part of the main chain.
3. **Proof Submission**
    
    - Plutus contract on Cardano verifies the block headers, ensures chain validity.
    - If valid, mints eBTC 1:1 with the burned BTC.
    - Updates the user’s “cumulative burn” state.
4. **State Management**
    
    - Contract stores:
        - **Last Processed Block Height** for each burn address.
        - **Total BTC Burned** at that height.
    - Each proof must demonstrate a block height above the last processed height to avoid double-claims.
5. **User Ownership**
    
    - Users register a unique burn address.
    - Must prove ownership/control of that Bitcoin address.
    - Only that user can mint eBTC from that address’s burns.

### CIP Format Compliance

Follow the [standard CIP file structure](https://github.com/cardano-foundation/CIPs). Provide:

- **CIP header** with metadata.
- **Detailed specification** (this section).
- **Rationale** and **path to implementation**.

## Rationale

- **Full Decentralization**: Eliminates need for centralized custody or oracles.
- **Security**: Proof-of-Work chain verification via NIPoPoW/SPV.
- **Simplicity**: One-way bridging avoids complex BTC redeems.
- **Scalability**: Cumulative burn tracking reduces on-chain storage overhead.

## Security Considerations

1. **Forks & Reorgs**
    - Proof must prove finality with enough confirmations.
    - Contract only updates state when the chain is deemed stable.
2. **Invalid Header Submissions**
    - Plutus logic checks block headers and PoW proofs.
    - Rejects fake or incomplete data.
3. **Spam or DOS**
    - Each proof requires transaction fees.
    - Off-chain proof generation can be expensive, discouraging spam.

## Implementation Details

- **On-Chain Verification**
    - Plutus script needs to parse Bitcoin headers.
    - Validate chain difficulty and Merkle inclusion.
- **Data Structures**
    - Store minimal header data (e.g., block height, prev block hash, Merkle root).
    - Maintain a map of user addresses to (last height, total burned).
- **Transaction Workflow**
    1. User calls `burnBTC` on Bitcoin.
    2. Collects block headers and Merkle paths.
    3. Submits them in a Cardano transaction to `eBTCMintingScript`.
    4. Script verifies and, if passed, mints new eBTC tokens to the user’s Cardano address.

## Reference Implementation

A minimal Plutus code snippet (pseudo-code):