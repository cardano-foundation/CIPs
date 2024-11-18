---
CPS: ?
Title: Light Client Protocols for Cardano
Status: Open
Category: Tools
Authors:
    - Sebastian Bode <sebastian.bode@cardanofoundation.org>
Proposed Solutions: []
Discussions:
    - https://github.com/cardano-foundation/CIPs/pull/?
Created: 2024-11-18
License: CC-BY-4.0
---

<!-- Existing categories:

- Meta     | For meta-CIPs which typically serves another category or group of categories.
- Wallets  | For standardisation across wallets (hardware, full-node or light).
- Tokens   | About tokens (fungible or non-fungible) and minting policies in general.
- Metadata | For proposals around metadata (on-chain or off-chain).
- Tools    | A broad category for ecosystem tools not falling into any other category.
- Plutus   | Changes or additions to Plutus
- Ledger   | For proposals regarding the Cardano ledger (including Reward Sharing Schemes)
- Catalyst | For proposals affecting Project Catalyst / the Jörmungandr project

-->

## Abstract
This CPS describes the challenge and motivation for having light client protocols for Cardano to enhance blockchain accessibility and verification efficiency and overcome the blockchain inherent challenge of linearly growing participation costs typically endorsing a non-trust-minimized access pattern based on centralized API services.

Light clients would allow various applications and devices to interact securely with the Cardano blockchain while using fewer computational resources compared to full nodes (see for example [full node wallet challenges of Daedalus](https://github.com/IntersectMBO/cardano-node/issues/5918) and the research being done for Lace light client wallet features [[7](https://iohk.io/en/research/library/papers/sok-a-taxonomy-of-cryptocurrency-wallets/)]). It would also enable light client based cross blockchain communication protocols like the Inter Blockchain Communication Protocol ([IBC](https://github.com/cosmos/ibc)) or the bridging concept proposed by the BitSNARK whitepaper [[4](https://assets-global.website-files.com/661e3b1622f7c56970b07a4c/662a7a89ce097389c876db57_BitSNARK__Grail.pdf)], essentially enabling secure cross chain communication of the Bitcoin network with other blockchains in an economically sustainable way at least compared to the requirement for each validator of one chain to also operate a full node of the other chain to not sacrifice on security guarantees provided by the other protocol.

The general idea of this CPS is to outline areas of application, summarize the main challenges when designing a light client protocol for the type of consensus Cardano is using, define common terms and provide a definition for what a light client actually is (and not is) so that CIPs can be created that implement concrete light client protocols based on the various building blocks available.

## Problem
Currently, Cardano does not provide a standardized light client protocol that meets modern blockchain verification and interaction needs. The absence of this feature restricts efficient access for low-resource devices, inhibiting broader ecosystem growth and user participation. It also sets the stage for neglecting one of Cardano's biggest assets which is decentralization, by endorsing interaction patterns that are working on the foundation of a Web2-ish or centralized API based access approach when it comes to reading data from the blockchain and e.g. submitting transactions to it.

### Definition
There are various resources that give a comprehensive overview about Light Clients in the context of blockchain applications (see e.g. [[1](https://a16zcrypto.com/posts/article/an-introduction-to-light-clients/)] or a more scientific approach in *Systemization of Knowledge* (SoK): Blockchain Light Clients [[2](https://eprint.iacr.org/2021/1657.pdf)]). However, the basic concept was already introduced by the Bitcoin whitepaper in 2009 [[3](https://bitcoin.org/bitcoin.pdf)].

For the sake of common language we are using [[2](https://eprint.iacr.org/2021/1657.pdf)] as a reference as it provides a complete and comprehensive overview about the problem space.

[[2](https://eprint.iacr.org/2021/1657.pdf)] defines a light client informally as follows and provides a more formal definition in section 3.1 subdividing requirements in functional, security and efficiency related:
>..., we can envision an “ideal” light client as a client having very low computation, storage, communication and initial setup requirements (making such a client feasible even in mobile devices or browsers). However, the light client should retain the security guarantees without introducing additional trust assumptions. Therefore, it still needs to act as the verifier of efficient cryptographic proofs, which will convince the client on the received query replies (e.g. on an account’s balance or the state of a transaction). These proofs would be created by entities in the blockchain in the prover role (e.g. miners or full nodes), ideally without introducing a significant overhead.

### Challenges of Designing a Light Client Protocol for Cardano
Constructing a light client protocol effectively boils down to implementing a mechanism for full nodes (or nodes that participate in the consensus and hold sufficiently enough information about the state of the blockchain) to generate proofs about the state of the ledger that can be verified by an entity (the client) that does not necessarily have to participate in the chains consensus and does not have to download the complete state of the blockchain but instead only queries for specific information like the balance of an account, inclusion of a transaction in the global set of transactions or submits a transaction based on a sound state (e.g. correct UTXO set) to the blockchain network for being included in one of the next blocks.

In a trust-minimized setup there is no need to trust a single entity or even a consortium of entities (typical notary scheme approach) that attests that the result of a query is valid. To achieve this there are typically four generic approaches implemented in existing light client protocols:
- **Header verification and consensus evolution** This approach is predestined for PoW blockchains and typically consists of the verification of block headers only, ignoring the actual block body. However, it requires further consideration when applied to PoS blockchains because of the risk of long range attacks and due to the header structure of Cardano blocks (only containing the signature of the actual block producer and not of other consensus participants that signed off on the correctness of the block) and the absence of any slashing or other punishment mechanisms. This challenge can be overcome by an overlay network whereas network validators (in the case of Cardano Stake Pool Operators) sign off on state proofs (e.g. the correctness of a block header) and in case enough signatures are collected the state can be trusted. Mithril with it's recent updates implemented only in 2024 can provide this to a certain degree.
- **Compressing state** A compressed representation of the blockchain state can be achieved by the application of cryptographic methods like e.g. SNARKs and other succinct argument systems. This results in the generation of a proof that can be efficiently verified by the client and e.g. attest that a certain transaction was included in the global transaction set without sharing the complete state. A challenge for Cardano is that it would require to implement the complex Consensus and Ledger rules in a zero knowledge proof system which at the time of writing this CPS is deemed to be infeasible. However, again what could be done is to implement SNARK based certificate outputs by Mithril which would in that case attest that the amount of stake held by Mithril network operators agrees with the correctness of a specific claim or result of a query made by the client.
- **Removing the state** As an extension to the above and e.g. applied by the Mina protocol.
- **Game-theoretic approaches** Whereas smart contracts based implementations are applied that are based on participants locking up funds in so called "arbiter" contracts as collateral to discourage dishonest behavior.

Besides the construction of state proofs that allow for the verification of query results made by clients, there is the additional challenge of Cardano's finality. Like in other Nakamoto-type consensus (longest chain) based blockchains, the definite finality of settlements is not immediately achieved which might (depending on current protocol parameters in place) lead to settlement times of multiple hours (with the current protocol parameter deployed to Cardano mainnet this period ranges from optimistically 12 hours to worst case 36 hours). This is not beneficial for certain applications as typically a state transition on the one blockchain is used to trigger any downstream activity on the other blockchain (in the case of light client based cross blockchain communication). A typical scenario is e.g. that certain assets are locked or burned on one chain and based on this event a representation of similar assets is issues on the other blockchain. Within the finality window described above, roll backs can not be excluded meaning, that actually the other blockchain has to wait until an event happened on the source blockchain has finally been settled or the target blockchain risks triggering actions which might no longer reflect the state of the source blockchain. From a user perspective this means in worst case a user would have to wait for 12 to 36 hours or in other terms a block depth of 2160 blocks until any assets are released on the target blockchain. Whereas this is only the worst case assumption and rollbacks based on slot or height battles of more than 10 blocks have barely been observed on mainnet, it still is critical for certain applications. Mithril accounts for this by e.g. waiting for 120 blocks (still a window of 40 minutes to 2 hours) until certain types of proofs are generated. This challenge might only be overcome to a certain degree when the Ouroboros Peras work is deployed to mainnet that IOG innovation and engineering teams are currently working on, but this will most likely not be the case for another year from now on. In summary, those finality related constraints have to be taken into account and potentially catered for on a different level than during the proof generation.

## Use cases
Like already mentioned above there are numerous use cases for blockchain light clients in general and in particular for Cardano. The most prominent ones known to the authors of this CPS at the time of writing are:
- Light Client based wallets, that provide a more trust-minimized approach for users interacting for value exchange with the blockchain compared to the typical CIP-30 non-custodial wallets while at the same time not requiring significant hardware resources for users to run a full node wallet like cardano-wallet as a standalone application or in combination with the Daedalus frontend.
- Enable Dapps running on devices or in environments with limited available resources like on mobile- or IoT devices and in browser environments
- Enable light client based cross blockchain communication protocols like IBC and others

## Goals
Like previously described the CPS aims to provide a root and common point of reference for others that are trying to implement light client protocols for Cardano. Concrete projects currently working on implementations or evaluating possibilities for light client protocols on Cardano are:
- Cardano IBC implementation currently in incubating state [[6](https://github.com/cardano-foundation/cardano-ibc-incubator)]
- Lace related research from the IOG research teams
- BitcoinOS related work to provide the technical decentralized, trust-minimized bridging between Bitcoin and Cardano based on [[4](https://assets-global.website-files.com/661e3b1622f7c56970b07a4c/662a7a89ce097389c876db57_BitSNARK__Grail.pdf)]

The CPS does not provide a concrete solution for a light client protocol. Those shall be defined in CIPs, referring back to this CPS. There is currently a draft CIP in the works to reflect the work done so far on the [Mithril](https://github.com/input-output-hk/mithril) based light client used within the IBC project mentioned above.

## Open Questions
Open questions when designing light client protocols for Cardano's consensus algorithm are:
- How to provide provably secure state proofs of Cardano or what are trust-minimized schemes for providing state proofs?
- How to overcome the challenges based on not having fast finality or more precisely how to overcome the challenge that the finality of settlements provided by Cardano's consensus and the current configuration active on mainnet might not be fast enough to meet the requirements of specific applications from a user experience or security perspective?
- How to compress the size of Cardano state proofs?

## References
- [[1](https://a16zcrypto.com/posts/article/an-introduction-to-light-clients)] Sorgente, M. (2023) Don’t trust, verify: An introduction to light clients, a16z crypto. Available at: https://a16zcrypto.com/posts/article/an-introduction-to-light-clients (Accessed: 18 November 2024).
- [[2](https://eprint.iacr.org/2021/1657.pdf)] Panagiotis Chatzigiannis, Foteini Baldimtsi, and Konstantinos Chalkias. (2021). SoK: Blockchain Light Clients.
- [[3](https://bitcoin.org/bitcoin.pdf)] Nakamoto, S. (2008) Bitcoin: A Peer-to-Peer Electronic Cash System.
- [[4](https://assets-global.website-files.com/661e3b1622f7c56970b07a4c/662a7a89ce097389c876db57_BitSNARK__Grail.pdf)] Ariel Futoransky, Yago and Gadi Guy. (2024). BitSNARK & Grail: Bitcoin Rails for Unlimited Smart Contracts & Scalability.
- [[5](https://github.com/cosmos/ibc)] Interchain Foundation. (2024). Inter-blockchain Communication Protocol specification.
- [[6](https://github.com/cardano-foundation/cardano-ibc-incubator)] Cardano Foundation IBC incubator project on GitHub.
- [[7](https://iohk.io/en/research/library/papers/sok-a-taxonomy-of-cryptocurrency-wallets/)] Representing IOHK research on Light Wallets or cryptocurrency wallets in general (Accessed: 18 November 2024).

## Copyright
This CPS is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).