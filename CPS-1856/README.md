---
CIP: CIP-XXXX
Title: eBTC: A Trustless BTC Bridge on Cardano
Authors:
  - An <anrodz42@gmail.com>
Discussions-To:
  - https://github.com/siran/CIPs/pull/1856
  - https://forum.cardano.org/t/ebtc-a-trustless-btc-bridge-on-cardano/141117
Status: Draft
Type: Standards
Created: 2024-12-21
License: CC-BY-4.0
---

## Abstract

This proposal defines eBTC: a trustless mechanism for moving Bitcoin (BTC) value onto Cardano as a native token, unlocking BTC liquidity for Cardano DeFi. Originally conceived as a **one-way, burn-and-mint** design, this CIP also explores a more advanced **two-way** approach using on-chain key management. The one-way approach involves burning BTC on the Bitcoin network, presenting cryptographic proofs (NIPoPoW/SPV) to a Cardano smart contract, and minting a corresponding amount of eBTC. The two-way extension allows redeeming BTC by carefully managing a unique Bitcoin wallet private key on-chain. Both approaches aim at allowing BTC to benefit from Cardano’s advanced smart contract functionalities.

## Motivation

Bitcoin (BTC) remains the most recognized and liquid cryptocurrency in the blockchain ecosystem, yet it lacks robust smart contract capabilities on its native chain. Existing wrapped BTC solutions on other chains typically rely on centralized custodians or oracles, introducing trust and counterparty risk.

A trust-minimized bridge helps the Cardano ecosystem tap into BTC’s liquidity while leveraging Cardano’s smart contracts for DeFi applications. This CIP:

- Removes reliance on external custodians.
- Avoids complex bridging or cross-chain custody solutions.
- Enables BTC to participate in Cardano-based lending, decentralized exchanges (DEXs), and other DeFi protocols.

Initially, a simpler one-way approach was proposed: burning BTC to an unspendable address on Bitcoin, then issuing eBTC on Cardano. Subsequent discussions have revealed that a more complex but feasible **two-way** version could be built, where the Cardano contract generates and holds (in encrypted form) the private key of a **unique** Bitcoin address. This key is only released once eBTC is burned, allowing BTC to be reclaimed without trusting a centralized custodian.

## Specification

### Overview of Two Options

1. Option A: One-Way Burn-and-Mint (Simpler)
2. Option B: Two-Way On-Chain Key Management (Advanced)

Below, we detail the simpler, one-way process first (as originally conceived), followed by an extended specification for a fully on-chain, two-way design.

---

### Option A: One-Way Burn-and-Mint

1. Burning BTC on the Bitcoin Chain
   - Burn Address: Define a standard, provably unspendable Bitcoin address, such as one using an `OP_RETURN` script or a well-known “burn” address.
   - Burn Transaction: The user sends BTC to this burn address, removing those BTC from circulation.

2. Proof Generation (NIPoPoW/SPV)
   - The user (or an off-chain service) constructs an SPV or NIPoPoW proof verifying that the burn transaction was included in a valid Bitcoin block on the main chain.
   - This proof, along with relevant block headers, is submitted to Cardano.

3. Cardano Smart Contract Verification
   - A Plutus contract confirms the proof corresponds to a valid burn transaction and that the transaction has sufficient confirmations to mitigate reorg risks.
   - Upon success, the contract mints an equivalent amount of eBTC (1:1) for the user on Cardano.

4. Usage of eBTC
   - eBTC can be used for Cardano DeFi (lending, DEX trading, liquidity provisioning, etc.).
   - Since BTC was burned, there is no “redemption” back to Bitcoin in this one-way model.

5. Key Benefits
   - Extremely simple, minimal trust.
   - No need to store or manage Bitcoin keys.
   - Guaranteed supply limit: the eBTC supply is constrained by the total BTC burned.

---

### Option B: Two-Way On-Chain Key Management

The following specification describes an **on-chain** approach that allows redeeming BTC after eBTC has been minted, without a third-party custodian. It utilizes a unique Bitcoin address per bridging session. The contract encrypts the private key so that no one can move the BTC unless eBTC is first burned.

1. Unique Bitcoin Address Generation
   - The Cardano contract deterministically or randomly generates a fresh Bitcoin public/private keypair on-chain.
   - It displays only the public portion to the user.
   - The private key remains encrypted within the contract’s storage so that no entity (not even the user) can access it yet.

2. Locking BTC to Mint eBTC
   - The user sends BTC to the generated Bitcoin address.
   - Using NIPoPoW or SPV proofs, the user shows the Cardano contract that the BTC is confirmed to be at that address.
   - The contract mints eBTC (1:1 with the locked BTC) and sends it to the user on Cardano.
   - Because the private key to this Bitcoin address is inaccessible, the BTC cannot be moved on the Bitcoin chain until eBTC is destroyed (burned).

3. Burning eBTC to Redeem BTC
   - To reclaim the locked BTC, the user burns eBTC by calling the contract with a “redeem” function.
   - Once eBTC is burned, the contract may reveal the encrypted key only after eBTC is burned.
   - User can then use keys to move its BTC.

4. Security Principles
   - The private key remains encrypted and is never accessible until eBTC is burned.
   - No double-spend is possible: the user cannot move BTC on Bitcoin while still holding eBTC on Cardano.
   - Once eBTC is destroyed, the user can spend the BTC.

5. On-Chain Feasibility
   - All logic (generation of unique addresses, encryption, gating conditions) is handled on Cardano.
   - Proof of BTC locking uses standard SPV or NIPoPoW.
   - Broadcasting the Bitcoin transaction is done by the Bitcoin chain.

6. Considerations
   - This approach is more complex than a straightforward burn-and-mint.
   - The contract must implement robust cryptography to generate and store the private key securely.
   - The Cardano environment must support or expose the cryptographic functions (ECDSA for Bitcoin, encryption, etc.) necessary to sign a Bitcoin transaction on-chain or to release a private key in a secure manner.

---

## Rationale

1. Why a Simple One-Way Bridge (Option A)?
   - Minimal complexity: only requires proving a burn on Bitcoin and minting eBTC on Cardano.
   - Removes custodian risk entirely, with no need for advanced key management.
   - Feels natural for permanent “migration” of BTC into Cardano DeFi.

2. Why Offer a Two-Way Alternative (Option B)?
   - Allows users to exit back to Bitcoin if desired, removing the permanent burn condition.
   - Achieves decentralized custody by storing the Bitcoin private key in the Cardano contract itself.
   - Avoids reliance on multi-signature federations or centralized custodians, maintaining trust-minimized principles.

3. Trade-Offs
   - The two-way approach is feasible with proper cryptographic capabilities and robust contract code.
   - One-way bridging is simpler and presents fewer attack surfaces.
   - Depending on user requirements (e.g., “I want to come back to Bitcoin eventually”), Option B may be worth the added complexity.

---

## Backward Compatibility

- The CIP does not alter Cardano’s consensus or ledger rules; it proposes new smart contracts and token policies.

---

## Reference Implementation

1. On-Chain Key Generation
   - For Option A (One-Way): no key management is needed.
   - For Option B (Two-Way): the contract could generate a Bitcoin keypair on-chain, store it encrypted, and control its release or usage.

2. SPV/NIPoPoW Proof Submission
   - A module or library for constructing minimal proofs from the Bitcoin blockchain.
   - The Cardano contract checks that the proofs reference the correct transaction, block height, and chain of greatest cumulative work.

3. Mint/Burn Mechanism
   - Plutus or other Cardano contract language can define the minting policy to issue eBTC upon verifying the proof.
   - Similarly, the policy and contract ensure eBTC is burned before Option B’s private key is revealed.

4. Example Workflow
   - Option A: (Burn on Bitcoin) → (Prove on Cardano) → (Mint eBTC). No redemption step.
   - Option B: (Generate BTC address on-chain) → (User locks BTC) → (Prove and mint eBTC) → (User burns eBTC) → (Contract finalizes Bitcoin transaction to release locked BTC).

---

## Security Considerations

1. For Option A (One-Way)
   - The main security concern is accurate verification of the Bitcoin burn transaction.
   - Once BTC is burned, it cannot reappear on Bitcoin, ensuring no double-spend.

2. For Option B (Two-Way)
   - The contract must store and manage a Bitcoin private key in a way that absolutely prevents premature access.
   - Cardano’s contract environment must support cryptographic operations for generating BTC addresses.

3. Common Considerations
   - SPV/NIPoPoW proofs need sufficient confirmations to avoid chain reorganizations on Bitcoin.
   - eBTC minting policies must strictly bind to the contract logic, preventing unauthorized minting.

---

## Copyright

This CIP is licensed under CC-BY-4.0. Feel free to share and adapt it with attribution.
