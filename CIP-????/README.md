---
CIP: XXXX
Title: Efficient Proofs for Dynamic Minting and Burning of NFTs
Status: Proposed
Category: Tools
Authors:
  - Pal Dorogi <pal.dorogi@gmail.com>
Implementors: [Pal Dorogi <pal.dorogi@gmail.com>]
Discussions:
  - https://github.com/cardano-foundation/CIPs/pull/816
Created: 2024-09-25
License: CC-BY-4.0
---

## Abstract

This Cardano Improvement Proposal (CIP) describes a solution to enable dynamic minting and burning of NFTs on the Cardano blockchain in a decentralized way.

Due to the deterministic nature of Cardano's Extended UTxO (EUTxO) model, it is currently not possible to dynamically mint NFTs with the same policy ID, as on-chain validation cannot check whether a specific NFT already exists.

This proposal seeks a solution that allows validation of new NFTs' minting or burning in a decentralized and scalable way while maintaining data integrity and preventing duplicate NFTs.

## Motivation

The current Cardano ecosystem restricts dynamic minting, where users can freely mint NFTs without predefined constraints, due to the deterministic nature of the EUTxO model.

Specifically, Plutus scripts cannot access the entire ledger state during transaction execution, making it impossible to validate whether an NFT has already been minted under the same policy ID. As a result, systems requiring unique NFTs under the same policy ID, such as usernames or collectible assets, cannot operate in a fully decentralized manner, as centralized control is often required to ensure uniqueness.

This proposal aims to overcome these limitations by introducing a method that leverages an off-chain dataset containing all previously minted and burned NFTs, which can be rebuilt from past minting and burning transactions. By storing a compact representation (e.g., cryptographic hash or accumulator) of this dataset on-chain as state of the dataset, and additionaly use efficient cryptographic proofs that allow the system to validate each state transition (i.e., minting or burning) while ensuring the uniqueness of NFTs , without requiring access to the full dataset on-chain.

By addressing these challenges, this proposal seeks to enhance the Cardano ecosystem by providing a scalable and decentralized mechanism for dynamic NFT minting, enabling broader adoption and new use cases within the blockchain community.

## Specification

### Dynamic Minting and Dynamic Sets

Dynamic minting refers to the ability of users to freely mint NFTs, where the NFT being minted does not have to be predefined at the time of policy creation. This allows flexibility in creating NFTs without manual constraints on content. Dynamic sets, in this context, represent the set of all minted and burned NFTs that change over time as new NFTs are minted and old ones are burned.

### Off-Chain Dataset

The system relies on an off-chain dataset that tracks all previously minted and burned NFTs. This dataset contain only unique elements. The dataset can be rebuilt and verified by anyone by collecting minting/burning transactions from the blockchain, ensuring full transparency and data integrity.

Since minting and burning transactions represent state changes, the dataset can be reconstructed from these transactions, allowing independent verification of the entire state history off-chain. This ensures that the off-chain dataset remains transparent and trustworthy without needing to store it directly on-chain.

For example, in the case of username-based NFTs, the dataset will store all previously minted usernames. If a user attempts to mint a username that already exists in the dataset, it will be rejected.

### On-Chain Compact Representation

Since large datasets cannot be stored on-chain, a compact representation of the off-chain dataset (such as a cryptographic hash or accumulator) will be maintained on-chain as part of the UTxO state. This representation will be updated each time an NFT is minted or burned.

While the full dataset is stored off-chain, the compact representation acts as the state of the system on-chain. This ensures that on-chain validation can efficiently handle state transitions without the overhead of storing the entire dataset.

The compact representation is stored as an inline datum in a UTxO, bound to a pre-minted authorization token/NFT, ensuring that the system can track the state of the dataset at any given time.

### State Transition and Efficient Proofs

For each minting or burning transaction, the user must present the UTxO that holds the authorization token/NFT, which also stores the current state as an inline datum. The user will also provide a cryptographic proof as the redeemer of the transaction that is used in the validation of the transition between the old state (the current compact representation) and the new state (the updated compact representation).

The transaction validation utilizes Plutus minting script which verifies that:

- The UTxO input contains the authorization token/NFT and the old state stored as the inline datum.
- The provided addition/deletion proof, as redeemer, correctly validates the addition (in the case of minting) or deletion (in the case of burning) of the NFT.
- The UTxO output (containing the authorization token/NFT) stores the new compact representation of the dataset in the inline datum, reflecting the valid state transition from the minting or burning event.

### Efficient Proofs

To make the system scalable and feasible on-chain, the cryptographic proofs used must be efficient. The proofs must be small enough to fit within the transaction size limits (e.g., `m * log(n)` complexity, where `m` is the size of the required proof and `n` is the size of the dataset) and computationally efficient for on-chain execution. The proofs will be included as redeemers in minting or burning transactions that the minting script will validate the state transition from old to new.

The size of the proofs must respect current redeemer size constraints (e.g., 5000 bytes), and the computational complexity for validating the proofs on-chain must be manageable.

### Initial State and Bootstrap

The protocol must be bootstrapped with an initial compact representation of an empty dataset, ensuring that the system starts in a well-defined state, ready to accept new minting and burning transactions.

### Example Workflow

**Initialization**:

The protocol is initialized with an empty dataset and a corresponding compact representation (e.g., a hash) stored on-chain in a UTxO, bound to an authorization token/NFT.

**Minting a New NFT**:

A user wants to mint a new NFT. The off-chain dataset is checked to ensure the NFT doesn’t already exist. The user generates a proof to show that minting the new NFT is valid. The proof is included in the redeemer, and the UTxO output contains the updated compact representation in the inline datum along with the authorization token/NFT.

**Burning an NFT**:

A user wants to burn an existing NFT. The off-chain dataset is checked to verify the NFT’s existence. A deletion proof is generated to validate the removal of the NFT from the dataset. The proof is included in the redeemer, and the UTxO output contains the new compact representation of the dataset along with the authorization token/NFT.

## Rationale

The proposal describes in this CIP achieves the goal of ensuring the uniqueness of NFTs minted on the Cardano blockchain by using an off-chain data structure to track the minting and burning of NFTs, and storing the hash of this data structure together with the proofs on the blockchain. This allows the on-chain code to verify the uniqueness of an NFT at minting time, without requiring the entire data structure to be stored on the blockchain.

Also, it allows anyone to independently build the off-chain data tree by retrieving on-chain minting/burning transactions. Therefore, there is no need for centralized solutions to validate the integrity of the tree, promoting decentralization and transparency within the Cardano ecosystem. Though, any - even un-trusted or adversarial - 3rd-party services can be used to be queried for a proof.

The use of compact representation of the off-chain data structure allows for efficient and secure tracking of the minting and burning of NFTs.

The constructed proof should provide proofs for membership, non-membership, addition, and deletion, with a proof size that scales logarithmically or better with the number of elements.

The use of an accumulator to represent the state allows for the updated state to be verified and recorded on the blockchain in a single transaction. This simplifies the process of updating the state, and reduces the risk of errors or disputes.

As the result, this proposal would allow dynamic minting and burning of NFTs in a secure, decentralized and scalable way. The combination of off-chain datasets, on-chain compact representations together with the cryptographic proofs ensure that the Cardano blockchain remains efficient while maintaining NFT uniqueness.

This approach ensures:

- **Off-Chain Transparency**: The off-chain dataset can be reconstructed and verified by anyone, ensuring transparency and trust.
- **Efficient On-Chain Validation**: The use of compact representations and efficient cryptographic proofs ensures that the system is scalable and can handle growing datasets over time.
- **Cost Efficiency**: By limiting on-chain storage to compact representations and small proofs, the transaction size and cost remain within reasonable bounds.

### Efficiency Considerations:

- **Proof Size**: Proof size must be kept within the current redeemer limits (~5000 bytes).
- **Cost Considerations**: Transaction costs will include the base fee for a redeemer (~220,000 lovelace for a 5000-byte redeemer), the reference script fee (~164,475 lovelace for a 10KB Plutus script), and the Plutus script execution cost. This adds up to approximately 400,000 lovelace, plus execution costs.

## Backward Compatibility

This proposal does not interfere with existing NFT standards or the current EUTxO model. It introduces a complementary system for dynamic minting and burning of NFTs while preserving backward compatibility with current practices.

## Path to Active

### Acceptance Criteria

The acceptance criteria for this CIP to become active are as follows:

- [ ] The solution described in the CIP has been implemented and tested in a live environment (Public testnet).
- [ ] The implementation has been reviewed and approved by subject matter experts.
- [ ] The community has had sufficient time to review and provide feedback on the CIP and the implementation.
- [ ] Any concerns or issues raised during the review and testing process have been addressed and resolved.

## Implementation Plan

The implementation plan for this CIP is as follows:

- [ ] The proposer will submit the implementation for review and approval by subject matter experts.
- [ ] The proposer will make the implementation and the CIP available for review and feedback by the community.
- [ ] The proposer will address and resolve any concerns or issues raised during the review and testing process.
- [ ] Once the acceptance criteria have been met, the proposer will submit a pull request to the Cardano Improvement Proposals repository to update the status of the CIP to active.

## References

- [Strong Accumulators from Collision-Resistant Hashing](https://users.dcc.uchile.cl/~pcamacho/papers/strongacc08.pdf)
- [CONIKS: Bringing Key Transparency to End Users](https://www.usenix.org/system/files/conference/usenixsecurity15/sec15-paper-melara.pdf)
- [Cryptography for Efficiency: New Directions in Authenticated Data Structures](https://user.eng.umd.edu/~cpap/published/theses/cpap-phd.pdf)
- [Transparency Logs via Append-Only Authenticated Dictionaries](https://eprint.iacr.org/2018/721.pdf)
- [Batching non-membership proofs and proving non-repetition with bilinear accumulators](https://eprint.iacr.org/2019/1147.pdf)

## Versioning

The solution described in this CIP does not require any specific versioning approach.

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode)
