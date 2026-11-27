---
CPS: 40
Title: Horizontal Scaling through Sharding
Category: Consensus
Status: Open
Authors:
    - Matthias Fitzi <matthias.fitzi@iohk.io>
    - Giorgos Panagiotakos <giorgos.panagiotakos@iohk.io>
Proposed Solutions: []
Discussions:
    - Original PR: https://github.com/cardano-foundation/CIPs/pull/1325
Created: 2026-11-19
License: CC-BY-4.0
---


## Abstract

Cardano's scaling so far has made each node use its resources more efficiently, an effort that Ouroboros Leios is set to continue. But under Praos, and under Linear or Full Leios as specified today, every node still receives, validates, and stores every transaction and holds the entire ledger state. Capacity therefore stays bounded by the least capable node the network intends to keep.

State and execution sharding is a principal approach to horizontal L1 scaling in which transaction processing and state maintenance are distributed among participants, allowing aggregate capacity to grow without requiring every node to execute and store the entire ledger. Although succinct proofs let nodes check the ledger without re-executing it, every transaction still needs to be initially executed, and, if we require the full ledger state (and its history) to be accessible, the ledger state must still be reliably stored. Dividing that work among nodes is what sharding adds. The [Leios roadmap][Leios-roadmap] already projects this step as UTxO sharding, an extension of Full Leios. This CPS treats sharding as a possible further step on that roadmap, not as an alternative to Leios.

No deployed sharding design meets Cardano's requirements, in particular for cross-shard atomicity and per-shard security under an adaptive adversary. This CPS states the problem, the bar a solution must clear, and the questions it must answer.

## Problem

### Full replication is the binding constraint

Cardano's throughput problem is documented in [CPS-0018][]. [Ouroboros Peras][CIP-0140] shortens settlement latency, [Linear Leios][CIP-0164] and later Full Leios raise throughput, and off-chain systems such as [Hydra][] and [Midgard][] move work off the base layer. All of these make a node do its work *better*; none reduces each node's share of the network's total work. A fully participating node must receive, validate and execute every transaction, hold the entire live UTxO set, and retain or be able to reconstruct the entire history. This *full replication* makes capacity a function of one number: the resources of the weakest node the network intends to keep.

Raising that number is *vertical scaling*, and it has two limits. First, it runs out. Linear Leios is designed to use capacity that current nodes leave idle ([CIP-0164][]). Beyond that, gains require raising the node specification, and hardware improves slowly. Costs grow with throughput in the meantime: at a sustained 150 kB/s the ledger grows by about 4.7 TB a year ([CIP-0164][]). Second, every increase costs decentralization, as it prices out operators running commodity hardware, whom Cardano aims to keep. If requiring more of each node is the only lever, throughput and decentralization are permanently in opposition.

A solution must say which resources it addresses: **bandwidth** (every node receives every transaction; Leios removes the propagation bottleneck of Praos but not this linear growth), **execution**, **live state**, and **history and bootstrap** ([Mithril][] lets a node trust a recent state but does not stop history from growing).

Sharding partitions the ledger so that each node is responsible for a proper subset of it. It is the only known layer-1 architecture in which the work of producing, not only verifying, is divided among nodes, so that per-node costs stay bounded while aggregate capacity grows. Succinct proofs and data availability sampling do not remove the need for it.

### Sharding on the Leios roadmap

Concurrent block production in Full Leios raises a further problem: concurrent blocks may include conflicting or duplicate transactions. Only one can take effect, and the rest waste bandwidth, validation and block space, increasingly so with concurrency, and deliberately so under attack unless conflicting transactions are made to pay ([CIP-0164][]; [Leios roadmap][Leios-roadmap]).

The [Leios roadmap][Leios-roadmap] addresses this with UTxO sharding. The UTxO space is split into shards, each input block (IB) serves a single shard, and the per-shard IB rate is kept low enough that conflicts are mostly avoided. The same mechanism is the roadmap's route to horizontal scaling, where "any new node that runs the protocol increases throughput proportionally to its resources." Nodes track only the shards they choose, and SNARKs and data availability sampling let them check the rest. This is a projection, not settled protocol: [CIP-0164][] does not specify sharding.

This CPS is about full state and execution sharding, along the lines the roadmap projects or otherwise. Because no node then stores all data, a solution also relies on layer-1 data availability for shard data. The companion CPS [*Layer 1 Data Availability for Cardano*][CPS-DA] (number not yet assigned) addresses data availability for applications and layer 2; whether it can also serve shard data, which must be checkable within consensus and retained as history, is open.

### Why EUTxO changes the odds

In an account-based system such as Ethereum, the state a transaction touches is in general only discovered by running it; systems that require it to be declared, such as Solana, add this as an extra rule. In EUTxO it is intrinsic: a transaction *declares* its inputs and outputs, so the state it reads and writes is known before execution. That is exactly the information a partitioning scheme needs, and it comes for free. Shard assignment can be decided locally, cross-shard cases identified rather than guessed, and transactions built to avoid crossing shards. Not all ledger state is UTxO, though: reward withdrawals, certificates and governance actions touch account-like state, which a partitioning scheme must also place.


## Use Cases

**A stake pool operator on commodity hardware.** After one or two increases in the node specification, the operator must upgrade beyond what the pool's margin allows, or stop. They want contributing *some* capacity to be enough for full participation, and growth to come from more operators like them rather than fewer, larger ones.

**An enterprise or partner chain with service-level requirements.** It needs predictable inclusion under load and isolation from unrelated congestion, without a market in purchasable capacity that undermines fair access.

**Light clients and new nodes.** A light client should verify its own transactions at a cost proportional to its own activity, following only the shards holding its state. Likewise, after years at much higher throughput, joining should cost a fraction of total history, or the validator set cannot grow.

## Goals

We state three goals, ranked by importance. A proposed solution should be assessable against each sub-criterion.

### Horizontal scalability

- **Capacity grows with participation.** Aggregate capacity grows with the number of participants while per-node resource use stays bounded. The solution must state which resources it bounds, and the scaling relationship and its limits.
- **Single-shard is the common case.** The solution should use the fact that EUTxO transactions declare their inputs in advance to keep most transactions within one shard. It must measure the share of cross-shard transactions under realistic workloads, not assume it is small.


### No weakening of security or decentralization

- **Ouroboros-grade security.** Security must be established with the same rigor and under the same adversarial model as today, including adaptive corruption and dynamic availability. Shards secured by less than global stake are not disqualifying, but the assumption must be stated, quantified and defended.
- **Decentralization improves.** The minimum viable node specification should fall, or at worst hold, as capacity rises.
- **Sound economics.** Fees and rewards stay incentive-compatible: whoever causes cross-shard work pays for it, operators are paid in proportion to the work they do, and congestion in one shard must not enable censorship or shard capture.

### Preserve EUTxO semantics and deployability

- **EUTxO semantics and composability.** Determinism, local verifiability and predictable fees must be kept. Atomic multi-script composition must remain available across shards, or be replaced by a clearly specified alternative.
- **Shards invisible to users.** Wallets and users should not have to reason about shard placement; where it must be exposed, it should be to applications and infrastructure.
- **Migration from the live ledger.** Deployment must be incremental: existing UTxOs, scripts and addresses keep working, and there is no flag day.
- **Governance, staking and rewards keep working.** Stake distribution, rewards and governance tallies are aggregates over the whole ledger. A solution must say how they are computed and verified when no node holds the entire state, without voting power or rewards depending on shard placement.
- **A bounded complexity budget.** Implementable without an unbounded rewrite, specified precisely enough for formal analysis, and checkable by people other than its authors.

### Non-goals

- **Replacing Leios, Peras or Layer 2.** Sharding builds on them.
- **Immediate deployment.** The goal is a credible path, not a hard fork date.
- **Fixing a shard count or partitioning.** These are outputs of a solution.
- **Privacy.** A separate problem.

### Explored Alternatives

Neither layer 2 nor sharding as deployed elsewhere meets the goals above.

#### Layer 2

Off-chain execution is complementary, not a substitute. It moves execution off the base layer but leaves settlement on it, and a thriving L2 ecosystem *increases* base-layer load. Its savings also hold only while the layer 2 operates normally: disputes and exits fall back to the base layer, and a mass exit can load it heavily at short notice.

#### Sharding elsewhere

**State sharding is in production.** [NEAR][NEAR-Nightshade] and [MultiversX][MultiversX-sharding] run state-sharded chains. Nearly all deployed sharded chains are account-based; [Alephium][Alephium] shards a stateful UTXO model, but none uses EUTxO. Measurements of NEAR on commodity hardware (§IV-A, Fig. 2), with all shards co-located on a single machine and sharing its resources, find aggregate throughput peaking at eight shards (about 1,500 TPS, 40% above one shard) and then declining to about 1,100 TPS at 24 shards. Although co-location avoids physical inter-node communication overhead, it also introduces resource contention. These results illustrate practical bottlenecks in shard coordination and resource sharing, however, without establishing the limits of horizontal scaling across independent machines.


**Ethereum abandoned execution sharding.** Shard chains are [off Ethereum's roadmap][ETH-danksharding]. Only data sharding survived: proto-danksharding (2024) and the first data availability sampling (PeerDAS, 2025) are live, and [full danksharding is still future work][ETH-scaling]. Execution moved to layer-2 rollups instead.

#### Why no existing design fits Cardano

**Cross-shard atomicity.** Cross-shard transactions cannot be avoided altogether: in a partitioning of about 750,000 historical Ethereum transactions, their [fraction grows with the number of shards][Cross-shard] (§3, Fig. 2), staying below 30% when partitioning to minimize cross-shard traffic, against over 90% under random assignment (§1). For plain UTXO, atomicity is well studied: each input shard checks and locks its own inputs and certifies them, and the transaction commits once all inputs are certified, a form of two-phase commit (§1). This relies on each input being validated locally. In EUTxO it is not: a Plutus script sees the whole transaction, including inputs, datums and reference inputs held in other shards, so validation itself becomes cross-shard. Deployed sharded chains process cross-shard transactions asynchronously, leaving them half-applied, which EUTxO semantics do not allow. None yet provides general cross-shard atomic execution, though [NEAR aims to add it][NEAR-SPICE]. A solution must make script validation work across shards, not only the commit step.

**Per-shard security.** If a subset of stake maintains a shard, an adversary below the global threshold may control it. Deployed systems assume that each shard's randomly sampled validators stay within a fault threshold, maintained by periodic random reassignment; in NEAR, chunk validators are resampled at every block while chunk producers rotate per epoch ([NEAR-NEP509][]). This is not adaptive security as Ouroboros defines it.

**State distribution.** Shards become imbalanced and popular applications create hot shards. State migration must be safe and cheap and must not become a censorship vector.

**Live migration.** There is no precedent for partitioning a live ledger like Cardano's. NEAR has split its live state several times, but on an account-based ledger built for sharding from the start. Ethereum planned to add execution shards alongside its existing chain rather than partition it, and dropped the plan.

## Open Questions

A CIP addressing this problem should answer each of the six headline questions in its *Rationale*, covering the sub-questions beneath it.

### What is sharded, and how does a node verify what it does not hold?
- Which of diffusion, execution, live state, history and validation are partitioned, and which stay replicated?
- Does every node still verify the whole ledger? If so, how (direct execution, succinct proofs, data availability sampling, fraud proofs), and under what assumption?
- What is the unit of partitioning: UTxO, address, script, asset, or something else?

### How is each shard secured against an adversary below the global threshold?
- How are block producers assigned to shards, how often is the assignment rotated, and is it public or by private sortition? How does that interact with adaptive corruption and with offline parties?
- Can such an adversary control a shard? What exactly is guaranteed, and what do honest parties observe if a shard misbehaves?
- Are dynamic availability and Genesis-style bootstrapping preserved?

### How do transactions that span shards behave?
- Is a multi-shard transaction atomic? If not, what states can it leave, how are they resolved, and who bears the cost?
- How does a long-lived single-state-thread contract avoid being capped at one shard's throughput without its state forking?

### How is state kept balanced and live across shards?
- How is shard imbalance detected and corrected? What triggers migration, who pays for it, and can it be used as an attack?
- What happens to a congested or spammed shard? Does per-shard pricing create a censorship vector?

### How do fees, rewards, staking and governance work when no node holds the whole state?
- How are fees distributed when validation work is uneven, and what prevents operators from serving only cheap shards?
- How are stake distribution, rewards and governance tallies computed and verified, and at what cost in latency and finality?

### How does the design fit the rest of the protocol, and how is it delivered and validated?
- How does it interact with Peras, Mithril, Hydra, rollup settlement and post-quantum migration? Where does it depart from the UTxO sharding projected on the Leios roadmap, why?
- What must change in ledger rules, transaction and address formats, and Plutus? Which changes are backwards-compatible?
- What is the incremental deployment path, and what is the first independently valuable step?
- Which benchmarks and adversarial scenarios, at what scale, would demonstrate the design works, and what result would falsify it?

## References

- [CPS-0018: Greater Transaction Throughput][CPS-0018]
- [CPS (number not yet assigned): Layer 1 Data Availability for Cardano (working title)][CPS-DA]
- [CIP-0164: Ouroboros Linear Leios][CIP-0164]
- [CIP-0140: Ouroboros Peras][CIP-0140]
- [Ouroboros Leios: design goals and concepts][Leios-paper]
- [The Leios roadmap to solving the blockchain trilemma][Leios-roadmap]
- [The Extended UTxO Model][EUTxO]
- [Hydra: Fast Isomorphic State Channels][Hydra]
- [Midgard][Midgard]
- [Mithril][Mithril]

Prior art:

- [Nightshade: NEAR Protocol Sharding Design 2.0][NEAR-Nightshade]
- [NEP-509: Stateless validation Stage 0][NEAR-NEP509]
- [Separation of Consensus and Execution (SPICE): A preview of NEAR's next major protocol upgrade][NEAR-SPICE]
- [Sahukar, Gandhi, Raicu: Shards on a Shoestring: Empirical Characterization of NEAR Protocol Nightshade Sharding on Commodity Hardware][NEAR-commodity]
- [MultiversX: Sharding][MultiversX-sharding]
- [Alephium documentation][Alephium]
- [Das, Krishnan, Ren: Efficient Cross-Shard Transaction Execution in Sharded Blockchains (Rivet)][Cross-shard]
- [Ethereum: Danksharding][ETH-danksharding]
- [Ethereum: Scaling roadmap][ETH-scaling]

[CPS-0018]: https://github.com/cardano-foundation/CIPs/tree/master/CPS-0018
[CIP-0164]: https://github.com/cardano-foundation/CIPs/tree/master/CIP-0164
[CIP-0140]: https://github.com/cardano-foundation/CIPs/tree/master/CIP-0140
[CPS-DA]: https://github.com/cardano-foundation/CIPs/pull/1310
[Leios-paper]: https://iohk.io/en/research/library/papers/ouroboros-leios-design-goals-and-concepts/
[Leios-roadmap]: https://www.iog.io/news/the-leios-roadmap-to-solving-the-blockchain-trilemma
[EUTxO]: https://iohk.io/en/research/library/papers/the-extended-utxo-model/
[Hydra]: https://iohk.io/en/research/library/papers/hydra-fast-isomorphic-state-channels/
[Midgard]: https://midgardprotocol.com/
[Mithril]: https://mithril.network/
[NEAR-Nightshade]: https://discovery-domain.org/papers/nightshade.pdf
[NEAR-NEP509]: https://github.com/near/NEPs/blob/master/neps/nep-0509.md
[NEAR-SPICE]: https://www.near.org/blog/separation-of-consensus-and-execution
[NEAR-commodity]: https://arxiv.org/abs/2609.12091
[MultiversX-sharding]: https://docs.multiversx.com/learn/sharding
[Alephium]: https://docs.alephium.org/
[Cross-shard]: https://arxiv.org/pdf/2007.14521
[ETH-danksharding]: https://ethereum.org/roadmap/danksharding/
[ETH-scaling]: https://ethereum.org/roadmap/scaling

## Acknowledgements

This problem statement draws on discussions within IO Research and ARC on Leios ledger design and on the horizontal-scaling workstream of the Cardano Vision 2026 program.

The document was drafted with the assistance of Claude Opus 5.5 (Anthropic), which surveyed the CPS process requirements, structured the argument, and produced part of the text; all technical positions, framing and editorial decisions are the author's.

## Copyright

This CPS is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
