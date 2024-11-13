---
CPS: 17
Title: Settlement Speed
Category: Consensus
Status: Open
Authors:
  - Arnaud Bailly <arnaud.bailly@iohk.io>
  - Brian W. Bush <brian.bush@iohk.io>
  - Hans Lahe <hans.lahe@iohk.io>
Implementors: N/A
Discussions: 
Created: 2024-09-30
License: Apache-2.0
---

## Abstract

Existing and emerging Cardano use cases would greatly benefit from faster "settlement" or "finality" of transactions. Moreover, some current and pending use cases are hampered or blocked by not having transaction settlement within minutes of including of a transaction on a block. Examples are partner chains, bridges, exchanges (centralized and decentralized), Dapps, and ordinary high-value transactions. Although rollbacks of transactions on the Cardano `mainnet` are uncommon because of the careful design of the Ouroboros protocol and the robust implementation of the Cardano node's memory pool and block diffusion, extraordinary adversarial conditions can in principle produce forks that cause impactful rollbacks with some probability: stake-based and CPU-based attacks might seek to create long-lived adversarial forks, for example. The Cardano `mainnet` currently has a 5% active slot coefficient and a security parameter of 2160 blocks (approximately 12 hours). Recent research indicates that for faster settlement (precisely defined in terms of stakeholder use cases) the Ouroboros protocol logic could be modified and the active slot coefficient could be optimized.


## Problem

Fast settlement is a critical part of Cardano scaling, as described in [*Scaling blockchain protocols: a research-based approach*](https://www.youtube.com/watch?v=Czmg9WmSCcI). Under Ouroboros Praos, settlement occurs probabilistically on the Cardano blockchain, where the probability that a block will be rolled back from the preferred chain decreases exponentially as the chain grows beyond the block and where that rate of decrease is slower when adversarial activity is stronger. Some use cases require high assurance that a block (and the transactions within it) will not be rolled back, necessitating a potentially lengthy wait before a transaction is considered "settled" or "finalize". Some major centralized exchanges, for example, require fifteen confirmations (i.e., blocks) before a transaction is considered settled: this amounts to waiting ten minutes before a consumer has their transacted funds or tokens available for subsequent use. This situation is not unique to Cardano: centralized exchanges generally require at least five minutes wait for most of the common blockchains. Partner chains, Dapps, or bridges may have stringent requirements for fast and highly certain settlement.

There are several definitions of "settlement" or "finality", and precision is important when discussing these. Two noteworthy scenarios can be defined precisely. Both scenarios are expressed in terms of the probability a transaction or block that's been observed _locally_ to be part of the chain will be rolled-back in the future. Remember that rollbacks are the natural consequence of the eventually consistent nature of blockchains.

- *Ex ante* settlement probability: "What is the probability that a transaction that I just submitted will ever be rolled back?"
- *Ex post facto* settlement probability: "Given that I submitted my transaction $x$ seconds ago and it has not yet been rolled back, what is the probability that it will ever be rolled back?"

Even better would be to have an on-chain indication that transactions up to a particular point have been settled with high probability.

If one is unwilling or unable to re-submit a rolled-back transaction, then the *ex ante* probability might be of most interest. This matches use cases where there is no opportunities for the parties involved in a transaction to resubmit it: for example, one party might have purchased physical goods and left the vendor's premises, leaving no chance to resubmit a rolled-back transaction.

Other use cases are better suited for *ex post facto* settlement: for example, a partner chain, bridge, or decentralized exchange can monitor the ledger for a fixed time and see that the transaction either is not or is rolled back, knowing that there is only a vanishingly small chance of that status ever changing once they have watched the chain for the fixed amount of time, giving them an opportunity to re-submit the transaction if it was rolled back. Both opportunity and back-end infrastructure distinguish these use cases. Protocol research has historically focused on optimizing *ex post facto* certainty after predefined waiting times.

Settlement failures (i.e., roll backs, "slot battles", and "height battles") can occur naturally as short forks occur due to multiple slot leaders being elected in the same slot or due to network delays. Under typical uncongested conditions such forks often do not create settlement failures because a user's transaction tends to the diffuse throughout the global memory pool and is included in a block on each of the honest, naturally occurring forks. Careful observation might reveal that the transaction was rolled back from one fork but was adopted on the newly preferred fork. Cardano tooling should routinely deal with such situations even though they are rarely apparent to or affect end users. Most wallets do not display information about such short forks and rollbacks to users. Short forks occur hourly at local Cardano nodes, but globally visible forks are much less common, and anecdotal evidence indicates that rollbacks of more than three blocks never occur on a large scale on Cardano `mainnet`.  (There may be one exception to this, however, where a longer rollback is said to have occurred.) As with settlement, a precise definition of near-global rollbacks is required to measure and discuss this phenomenon in detail.

Casual perusal of information about Cardano on the internet reveals a wide variety of conflicting explanations and assertions regarding settlement and finality. The terms "settlement" and "finality" are not clearly defined in the context of Cardano and statements about them range from saying that only one block/confirmation is required to consider a transaction settled to 2160 blocks or 12 hours is required for settlement. The Ouroboros security parameter *k* also seems poorly described.

Many centralized exchanges have published the number of confirmations (blocks) required for them to consider a transaction settled. Taking Kraken as an example,[^1] we see in the following table the significant delay required for transactions to be treated as final. Cardano is not among the cluster of fast-settling blockchains. (Note that the following table contains internal contradictions between the "confirmation" column and the "time" column, a situation which further highlights imprecise understanding of settlement.)

| Blockchain | Confirmations Required | Approximate time (minutes) |
| ---------- | ---------------------: | -------------------------: |
| Algorand   |                     10 |                          1 |
| Aptos      |                     50 |                          5 |
| Avalance   |                     20 |                          1 |
| Bitcoin    |                      3 |                         30 |
| Cardano    |                     15 |                         10 |
| Dogecoin   |                     40 |                         40 |
| Ethereum   |                     70 |                         14 |
| Polkadot   |                    n/a |                          5 |
| Ripple     |                    n/a |                          0 |
| Solana     |                    n/a |                          0 |
| Tezos      |                      6 |                          3 |
[^1]: Data extracted from [https://support.kraken.com/hc/en-us/articles/203325283-Cryptocurrency-deposit-processing-times](https://support.kraken.com/hc/en-us/articles/203325283-Cryptocurrency-deposit-processing-times) on 7 August 2024.

Cardano Dapps and DEXes vary quite a bit regarding how many confirmations they require before they consider a transaction settled. As few as one confirmation is required for some Dapps, but other require twelve hours.

When Cardano becomes used by large institutions or nation states, attacks on settlement may become more attractive and lucrative. Hence, it is not safe to assume that stake-based and grinding attacks will not occur in the future.

## Use cases

Fast settlement primarily benefits use cases where a party needs certainty, after a fixed amount of time, about the settlement status of a transaction. The generic use case follows.

1. The party submits a transaction to the local memory pool.
2. A block producer includes the transaction in a newly forged block.
3. After a fixed time passes or a specific indication is observed, the party considers their transaction settled.
4. Contrarily, the party might observe that their transaction was rolled back from the preferred chain, so they may choose to resubmit it to the memory pool.

Specific use cases involving time-constrained, high-value transactions conform to this generic pattern. When the value at risk is low, a one-in-a-million chance of a rollback might not be as concerning as it would be for a large transaction. Examples follow.

- Centralized exchanges, where fast settlement improves the user convenience and experience
- Partner chains and bridges, where certainty about synchronization between two chains is essential
- Dapps where fixed-horizon certainty is needed to orchestrate transactions
- Ordinary transactions where a brief wait is acceptable but a roll-back is not

For example, the partner-chain use case might leverage faster settlement as follows. The desired target for cross-chain transfers is on the order of minutes.

1. Funds or tokens need to be transferred from the partner chain to the Cardano chain.
2. A smart-contract transaction escrows the funds/tokens on the partner chain.
3. Simultaneously, a mirror of that smart-contract transaction is submitted on Cardano.
4. After a short amount of time, the Cardano transaction has been incorporated into a newly-formed block.
5. Wait for settlement or non-settlement, either by waiting for a specific number of blocks to cover the transaction or by observing some other aspect of the chain.
	1. If the transaction settled, complete the escrow contract on the partner chain.
	2. If the transaction was rolled back, resubmit it.

Two prominent use cases are the Cardano-Midnight ZK Bridge and the Cardano-Bitcoin BOS Grail Bridge. These bridges and partner chains likely will require fast settlement on Cardano if they intend to keep chains in sync and rapidly move value to/from Cardano.


## Goals

The overall goals are to precisely define settlement metrics and to propose protocol or parameter changes that significantly speed settlement without negatively impacting performance or security.

1. Develop precise settlement/finality metrics relevant for stakeholders.
	1. Some metrics should be defined in terms of the whole life cycle of a transaction, from its submission to the memory pool to its becoming settled in a block.
	2. Block- versus slot-based metrics have importance for different use cases.
	3. Embody these metrics in an open-source library or toolkit for estimating settlement times or measuring finality of Cardano transactions.
	4. Create metrics that are practical for wallets to implement and to present clearly to users.
2. Shorten settlement time, as defined by stakeholder-relevant metrics, in the face of even moderate adversarial activity.
	1. Stake-based adversaries.
	2. Attacks utilizing adversarial resources (CPU or network).
	3. Natural disruption of infrastructure or networks (e.g., data-center or internet outages).
4. Fall back to Praos-like security in the face of strongly adversarial conditions.

It addition to the goals above, it is advisable to avoid the following potentially costly changes.

1. Avoid making major changes to the existing Ouroboros protocol parameters or logic.
2. Do not weaken Ouroboros security or substantially enlarge its attack surface.
3. Minimize changes that increase the resource usages of Cardano nodes or the cost of operating them.

Three approaches are under active consideration or development to address the settlement and finality problem. The first two mitigate stake-based and grinding attacks, respectively.

- *Voting approaches* strengthen the weight of the preferred chain, making it extremely difficult to roll back blocks on the prefix of the chain that was made weightier by a quorum (consensus) of stake-based votes. [Ouroboros Peras](https://github.com/cardano-foundation/CIPs/pull/872) is an example of this. This approach does not mitigate CPU-resource attacks.
- *Anti-grinding approaches* make prohibitively expensive any attacks that rely on CPU resources to weaken cryptographic guarantees of the pseudo-randomness of the slot-leadership schedule. This approach does not mitigate stake-based attacks, but grinding requires some stake in order to manipulate the slot-leadership schedule.
- *The protocol-parameter approach* simply lowers the active slot coefficient (currently set to 5% of the slots on `mainnet`) to a somewhat lower value, so that the block production rate and settlement are faster. This approach can only moderately shorten settlement times and does not mitigate against the aforementioned attacks.


## Open questions

- Is finality on the order of a couple of minutes feasible on Cardano? What is the theoretically fastest finality possible for a Praos-like consensus algorithm?
- What definitions of settlement and finality are most relevant to Cardano stakeholder use cases? Is a single definition common to all use cases?
- How best can empirical data on Cardano `mainnet` settlement and finality be collected and communicated?
- Can a single approach to faster settlement work in the face of both stake-based and resource-based adversaries?
- Would faster settlement negatively impact or be undercut by other planned Cardano node updates?
- What are the trade-offs between settlement speed, throughput, performance, and security?
- To what extent would tiered pricing for transactions improve settlement times for high-value transactions.
- Is "rollback insurance" a viable alternative to shortening settlement times?


## Copyright

This CPS is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
