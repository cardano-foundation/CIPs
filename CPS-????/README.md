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
This CPS describes the challenge and motivation for having light client protocols for Cardano to enhance blockchain accessibility and verification efficiency and overcome the blockchain inherent challenge of linearly growing participation costs typically endorsing a non-trust-minimized access pattern based on centralized API services that also sacrifices on the security features of the respective consensus protocol.

Light clients would allow various applications and devices to interact securely with the Cardano blockchain while using fewer computational resources compared to full nodes (see for example [full node wallet challenges of Daedalus](https://github.com/IntersectMBO/cardano-node/issues/5918) and the research being done for Lace light client wallet features [[7](https://iohk.io/en/research/library/papers/sok-a-taxonomy-of-cryptocurrency-wallets/)]).

Furthermore, there are various cross blockchain communication protocols that leverage light clients at the foundation of their security model (see e.g. the Inter Blockchain Communication Protocol ([IBC](https://github.com/cosmos/ibc)) or the bridging concept proposed by the BitSNARK whitepaper [[4](https://assets-global.website-files.com/661e3b1622f7c56970b07a4c/662a7a89ce097389c876db57_BitSNARK__Grail.pdf)]).

The general idea of this CPS is to outline areas of application, summarize the main challenges when designing a light client protocol for the type of consensus Cardano is using, define common terms and provide a definition for what a light client actually is (and not is) so that CIPs can be created that implement concrete light client protocols based on the various building blocks available.

## Problem
Currently, Cardano does not provide a standardized light client protocol that meets modern blockchain verification and interaction needs. The absence of this feature restricts efficient access for low-resource devices, inhibiting broader ecosystem growth and user participation. It also sets the stage for neglecting one of Cardano's biggest assets which is decentralization, by endorsing interaction patterns that are working on the foundation of a Web2-ish or centralized API based access approach when it comes to reading data from the blockchain and e.g. submitting transactions to it.

Cardano operates as a Proof-of-Stake blockchain, with its Ouroboros family of consensus algorithms employing a Nakamoto-style approach based on the longest-chain paradigm, which poses significant challenges in designing a secure and efficient light client protocol. Another challenge lies in the fact that final settlement of transactions on Cardano takes 12 to 36 hours, due to the current mainnet parameters. Specifically, the security parameter *k*, currently set to 2160, requires blocks to reach a depth of at least 2160 before finality can be assumed.

### Definition
There are various resources that give a comprehensive overview about light clients in the context of blockchain applications (see e.g. [[1](https://a16zcrypto.com/posts/article/an-introduction-to-light-clients/)] or a more scientific approach in *Systemization of Knowledge (SoK): Blockchain Light Clients* [[2](https://eprint.iacr.org/2021/1657.pdf)]). However, the basic concept was already introduced by the Bitcoin whitepaper in 2009 [[3](https://bitcoin.org/bitcoin.pdf)].

For the sake of common language we are using [[2](https://eprint.iacr.org/2021/1657.pdf)] as a reference as it provides a complete and comprehensive overview about the problem space.

[[2](https://eprint.iacr.org/2021/1657.pdf)] defines a light client informally as follows and provides a more formal definition in section 3.1 subdividing requirements in functional, security and efficiency related:
>..., we can envision an “ideal” light client as a client having very low computation, storage, communication and initial setup requirements (making such a client feasible even in mobile devices or browsers). However, the light client should retain the security guarantees (*of the blockchain's consensus*) without introducing additional trust assumptions. Therefore, it still needs to act as the verifier of efficient cryptographic proofs, which will convince the client on the received query replies (e.g. on an account’s balance or the state of a transaction). These proofs would be created by entities in the blockchain in the prover role (e.g. miners or full nodes), ideally without introducing a significant overhead.

### Challenges of Designing a Light Client Protocol for Cardano
Building a light client protocol involves enabling full nodes—those that participate in consensus and have sufficient blockchain state information—to generate proofs about the ledger's state. These proofs can be verified by a client that does not participate in consensus and does not need to download the entire blockchain. Instead, the client can request specific data, such as account balances, transaction inclusion, or submit transactions using the correct state (e.g., the UTXO set) for inclusion in future blocks.

In a trust-minimized setup, there is no need to rely on a single entity or group (as in typical notary schemes) to validate query results. Existing light client protocols generally use one of four approaches to achieve this:
- **Header Verification and Consensus Evolution** Commonly used in PoW blockchains, this verifies block headers without the full block body. For PoS chains like Cardano, challenges such as long-range attacks and minimal header information complicate this method. Solutions include overlay networks where validators (e.g., Stake Pool Operators) sign state proofs. Mithril’s recently introduced features partially address this.
- **Compressed State Representations** Cryptographic methods like SNARKs can generate proofs of state inclusion (e.g., transactions) without full state data. However, applying zero-knowledge proofs to Cardano’s consensus and ledger rules is currently infeasible. Mithril could provide SNARK-based certificates verifying claims tied to operator stake.
- **Stateless Protocols** Techniques that remove state altogether, as seen in the Mina protocol, offer an alternative.
- **Game-Theoretic Approaches** Smart contracts use locked collateral (e.g., in “arbiter” contracts) to discourage dishonesty, leveraging economic incentives to ensure trustworthiness.

These methods illustrate the diversity of strategies for building trust-minimized light client protocols, each with trade-offs and technical hurdles.

Beyond constructing state proofs for verifying client queries, Cardano faces additional challenges with transaction finality. Like other Nakamoto-consensus blockchains, Cardano does not achieve immediate finality. Instead, settlement times range from 12 to 36 hours on the mainnet, depending on current protocol parameters (e.g., the security parameter *k* = 2160). This delay complicates applications like cross-chain communication, where state transitions on one blockchain trigger actions on another. For example, assets locked or burned on one chain might only be mirrored on the second chain after final settlement is confirmed to avoid the risk of rollbacks.

While rollbacks deeper than 10 blocks are rare, applications requiring certainty must wait until finality, potentially delaying user interactions by up to 36 hours. Mithril addresses this partially by waiting for 120 blocks (40 minutes to 2 hours) before generating certain proofs. Full resolution of these challenges may require deploying innovations like [Ouroboros Peras](https://peras.cardano-scaling.org/), which Input Output Global (IOG) is developing. However, these improvements are unlikely to reach the mainnet for at least another year. In the meantime, applications must account for these finality constraints, potentially addressing them at a level beyond proof generation.

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