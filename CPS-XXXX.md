CPS: ????
Title: Dynamically Minting Unique NFTs on the Cardano Blockchain
Status: Open
Category: Blockchain
Authors: - [Pal Dorogi, pal.dorogi@gmail.com]
Created: 2024-05-31
License: CC-BY-4.0

## Abstract

This Cardano Policy Statement (CPS) addresses the challenge of dynamically minting unique Non-Fungible Tokens (NFTs) with user-chosen token names under a single policy on the Cardano blockchain in a decentralized way.

Current mechanisms lack the capability for users or entities to mint unique NFTs with the same policy ID dynamically without relying on trusted third-party entities.

The goal is to find and/or develop methods that ensure the uniqueness of the asset name for a single policy at minting/burning time, enhancing the reliability and trustworthiness of NFT creation on Cardano.

## Problem

The deterministic EUTXO-based transaction model of the Cardano blockchain provides many benefits, such as determinism, enhanced security, scalability, and predictable transaction fees.

However, it also presents a challenge for dynamically minting unique NFTs.

NFTs are unique digital assets that are stored on a blockchain and can be bought, sold, and traded like traditional physical assets.

However, in the EUTXO-based transaction model, it is not possible to determine the uniqueness of an NFT by the minting policy at minting/burning time.

This limitation arises from the fact that the EUTXO model restricts scripts to the transaction context instead of the whole ledger state, making it impossible to verify the uniqueness of an NFT at minting or burning time.

This means that, without an additional mechanism to ensure uniqueness, adversarial transactions can falsely claim the availability of NFTs, compromising the uniqueness and security of minted NFTs.

Existing solutions for minting unique NFTs, with user-chosen token names, lack dynamic minting/burning capabilities in a decentralized manner:

- Single-issuer policy: Only entities holding a specific set of keys can mint tokens for a particular asset group. This approach relies on centralized, trusted third parties.
- Time-locked mint policy: Tokens are minted based on a predetermined time-lock condition, and no additional tokens are permitted to be minted after the time lock expires. Validation of uniqueness is only possible after the time lock expires.
- One-time mint policy: The complete set of tokens (NFTs) of a given asset group is minted by one specific transaction. This approach limits the number of NFTs and has a transaction size limitation. It is similar to the "Time-locked" mint policy but is implemented using Plutus scripts.

## Use Cases

- Decentralized Naming Service: Users can dynamically mint and burn unique NFTs representing usernames. Ensuring uniqueness within the same policy ID is crucial to prevent conflicts and duplications.
- Decentralized DNS: A fully decentralized Domain Name System (DNS) where each domain is an NFT. Ensuring the uniqueness of NFTs within the same policy ID dynamically is essential for the system's functionality.
- General NFT Marketplaces: Any marketplace that supports on-demand minting of NFTs needs to ensure the uniqueness of NFTs within the same policy ID to maintain integrity and user trust.
- Single-issuer policies: Entities want to demonstrate to users that they can exclusively mint unique NFTs within a specific domain, such as artwork authentication or limited edition collectibles. This use case ensures that each NFT minted by the entity is genuinely unique and authenticated, enhancing trust and value for collectors and investors.
- Verifiable Limited-Edition Collectibles: Artists, creators, or brands may want to issue a limited number of unique NFTs as part of a collectible series. Ensuring the uniqueness of each NFT within the same policy ID is crucial for maintaining the value and authenticity of the collectibles. Users can trust that the NFTs they purchase are genuinely rare and one-of-a-kind.

# Goals

- To enable the minting of unique NFTs with Plutus scripts on the Cardano blockchain, using a mechanism that is secure, scalable, and efficient.
- To ensure that the mechanism is compatible with the EUTXO-based transaction model and does not compromise its benefits.
- To ensure that each NFT minted under a single policy is unique.
- To enable dynamic, on-demand user-chosen token name based NFT minting and, optionally, burning procedures.
- To achieve this without relying on any centralized authority or centralized third-party services.
- To use solutions that are computationally efficient and scalable, capable of handling millions of elements.
- To keep the on-chain state minimal while allowing off-chain reconstruction and verification of the NFT state.
- To provide clear guidance and resources for developers and users who want to implement the mechanism.

# Open Questions

- How can the system prevent adversarial actors from exploiting the minting process to create duplicate NFTs?
- How will the proposed solution scale with increasing numbers of NFTs and users over time?

## Optional Sections

# Acknowledgements

Acknowledge any contributors or inspirations.

# Copyright

This CPS is licensed under CC-BY-4.0.

