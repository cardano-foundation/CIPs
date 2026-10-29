---
CPS: ?
Title: Layer 1 Data Availability
Category: Ledger
Status: Open
Authors:
  - Giorgos Panagiotakos <giorgos.panagiotakos@iohk.io>
Proposed Solutions: []
Discussions:
  - Original PR: https://github.com/cardano-foundation/CIPs/pull/1310
  - Data Availability Technical Workshop, 3 September 2026 
Created: 2026-10-29
License: CC-BY-4.0
---

## Abstract

A growing set of Cardano projects need to publish data that others must be able to retrieve and verify for a short period of time, while not necessarily making it to the ledger’s transaction history. Layer 2 protocols publish state snapshots and commitments; optimistic zero-knowledge systems publish proofs that must be available for challenge; governance applications publish ballots that must remain auditable; rollups and intent-based systems publish batched transaction data. Today these projects choose one of  the following data publishing options: (i) post data directly to the Cardano ledger, which is prohibitively expensive for the volumes involved, (ii) rely on an external system such as Celestia, which does not inherit Cardano's security guarantees and introduces a separate trust assumption, or (iii) use a trusted operator, which comes with strong trust assumptions. None of these options are optimal, and the gap is already shaping architecture decisions, with recent projects selecting external data availability layers by default.

This CPS states the problem: Cardano lacks a dedicated layer 1 data availability capability — a way to publish data that inherits the main chain's security guarantees, guarantees retrievability for a defined period, and supports membership and non-membership  proofs, at a cost and throughput the applications can tolerate. It sets out the requirements gathered from multiple projects through an interactive technical workshop, the goals any solution must meet, and the questions that remain open. 


## Problem

Cardano's ledger guarantees that transaction data is available and correct: every node holds data, verifies data, and anyone can retrieve data. That guarantee is expensive by design, because it is paid for by verification and permanent replication across the entire network. It is the right trade-off for transactions that move value, until more advanced solutions such as succinct correctness proofs or data availability sampling are deployed. It is the wrong trade-off for a growing class of data that must be verifiably available for a period of time, but need not be part of the ledger's permanent record, or need not to be verified by everyone.

### Data types and performance metrics
From the technical workshop [1], four distinct types of data recur:
* State commitments (from layer 2 protocols): a layer 2 must publish enough data for participants to reconstruct state and exit safely if the protocol stalls. Without state commitments and data availability, user withdrawal ability depends on the continued cooperation of the operator.
* Challengeable proofs: optimistic verification schemes and large zero-knowledge (ZK) proofs are only sound if the data underlying a challenge is available to everyone who raises one.
* Auditable records: governance ballots, audit logs, and balance histories need to be verifiable after the fact, sometimes for years, by parties who were not present when they were written.
* High-frequency batched data: Babel fees and intent-based order books combine many small operations into blobs that act as a message-passing layer; so data must be visible quickly and cheaply, and matters only briefly.

Further, the following key performance metrics were highlighted:
* **Cost:** The cost per byte is one of the main limiting factors when publishing large volumes of data through layer 1. 
* **Throughput:** As above, throughput is one of the big constraints of publishing large volumes of data through layer 1.
* **Publication latency:** The maximum time it takes for submitted data to become publicly and verifiably available under stated operating conditions. This metric is important for challenge-based/optimistic applications as it affects their overall latency. E.g., DeFi applications have typically high sensitivity to latency, as the market may move and opportunities may be lost due to high latency.

### Explored alternatives 
The following solutions have been explored by the community:
* **Post the data on-chain as transaction metadata or datums:** inherits Cardano’s security guarantees and ensures data availability. However, at the volumes involved, it may not meet cost and throughput requirements. . It also requires every node to retain data permanently, even when the data only needs to be available temporarily.
* **Celestia, Filecoin, and similar external data availability layers:** purpose-built, mature, and already integrated by some Cardano projects. However, they introduce a second trust assumption and a separate liveness dependency, meaning applications can no longer rely  on Cardano’s security guarantees. 
* **IPFS and content-addressed storage:** inexpensive and widely deployed. However, content addressing does not guarantee availability . Data persists only while someone continues to store and serve it, making availability dependent on an external party. A challenge mechanism cannot safely rely on this assumption.
* **Trusted operator or federated storage:** simple and fast to implement. Reintroduces the trusted intermediary, weakening the goal of trustless data availability

### Providing a competing data availability solution 
This is not a hypothetical problem awaiting future demand. Projects building on Cardano today are making data availability decisions now, and in the absence of a layer 1 option, they are choosing external layers. Two constraints discussed at the workshop [1] make this concrete: a solution arriving more than roughly eight months out may be already too late for projects launching within the year, and a solution arriving later than that must demonstrate a significant throughput improvement, or a clear advance on some other dimension to displace an incumbent a project has already integrated. The cost of inaction may therefore be not a delayed capability, but a permanent one — each project that integrates an external layer is unlikely to migrate.

## Use Cases


Most use cases were sourced and discussed from the Data Availability Technical Workshop [1]: 

1. **A layer 2 protocol publishing state snapshots** 

   **Scenario:** a layer 2 protocol must publish snapshots and commitments so that participants can synchronize and evacuate safely if the protocol stalls, or an operator goes offline. 

   **Example:** Gummiworm (by Sundae Labs) [6] requires storage from one hour to five days, no proof machinery beyond replication, and the ability to reference byte ranges from a Plutus smart contract. Cost sensitivity is reduced when fees are spread across thousands of users. 

   **Who bears the cost today:** layer 2 users, whose exit guarantee currently depends either on posting expensively to layer 1 or on an external availability layer outside Cardano's security perimeter.

2. **An optimistic rollup publishing transaction data** 

   **Scenario:** an optimistic rollup publishes transaction data that must remain available long enough so that any participant can construct a fraud proof if needed; typically fraud proofs rely on data membership or non-membership proofs. 

   **Example:** Midgard (by Anastasia Labs) [7] requires seven-day storage, membership and non-membership proofs, low-cost, and more throughput than what’s on layer 1 today.

   **Who loses today:** rollup users, whose safety rests on multiple trust assumptions.

3. **A zero-knowledge system publishing large proofs for optimistic verification**

   **Scenario:** optimistic verification of large proofs requires the proof data to be available to any party who might challenge it. 

   **Example:** current post-quantum zero-knowledge proofs can exceed 100 kilobytes, which when combined with frequent usage indicates rather high throughput needs.

   **Who loses today:** verifiers, who cannot efficiently and securely use ZK optimistic verification and instead have to rely on an external availability layer outside Cardano's security perimeter.

4. **A governance application publishing a ballot record**

   **Scenario:** a voting system publishes a bulletin board of ballots that participants must be able to verify are included. 

   **Example:** previous Catalyst voting rounds [10] imply a capacity for 100,000 to one million votes and proof of membership. 

   **Who loses today:** voters and observers, who must trust the tallying infrastructure because an independently verifiable record at that scale is not affordable on layer 1.

   (Note: For governance applications, this CPS addresses publication and retrieval during a bounded verification period. Retention for later audits requires a separate archival mechanism and is outside scope.)

5. **An off-chain network publishing service discovery and recovery data** 

   **Scenario:** nodes and off-chain protocols need a shared, low-trust/low-cost place to publish endpoints, keys and credentials, and to retrieve data they missed while disconnected. 

   **Example:** Hydra [9] would use a registry of public service endpoints, public keys and credentials to improve peer connectivity; separately, Pub/Sub [3] participants identified temporary storage as a way for operators to catch up after a network outage or eclipse attack. Neither needs strong proof machinery. 

   **Who loses today:** operators, who fall back on out-of-band coordination or manual recovery, and users whose connectivity depends on it.

6. **A trading application publishing high-frequency batched intents** 

   **Scenario:** many small operations are combined into blobs that function as a message-passing layer, so participants can see the available set and act on it. 

   **Example:** Babel fees [8] and intent-based order books need support for frequent small blobs, visible quickly; individual blobs matter only briefly. 

   **Who loses today:** traders, who cannot see a complete order or intent set, and the protocols, which fragment across bespoke off-chain channels.

### What the requirements have in common

The technical workshop's most useful finding was that participants need relatively little fine-grained control. For most projects, storage for several days was acceptable. Some projects, such as voting, require data to be retained for years. These fall under long-term storage, which is outside the scope of this CPS. There was clear consensus on data integrity guarantees as well as a capability requirement — membership and non-membership proofs. Further, it was broadly agreed that the cost must be materially below current layer 1 posting. However, some applications can spread costs across many users, making a higher overall cost acceptable.


## Goals


The goals of this CPS are derived from requirements stated in the Data Availability Technical Workshop [1], including: 

1. **Security inheritance:** data published through the mechanism inherits the security guarantees of the Cardano main chain, rather than resting on a separate network's validators, economics or liveness. *Acceptance criteria:* the data-availability guarantee must derive from security assumptions already made about Cardano, without relying on an independently trusted storage operator or an external validator set. Proposed solutions must identify and justify any additional cryptographic, network, resource, or participation assumptions.

2. **Verifiable availability in the order of days:** anyone can quickly retrieve published data for a stated number of days; data availability can be efficiently checked. *Acceptance criteria:* A proposed solution must specify when a publication is accepted, when its retention period begins and ends, and the assumptions and retrieval-delay bound under which participants can obtain the data during that period. Plutus scripts must be able to efficiently verify evidence that a publication has been accepted under these guarantees and determine its expiry.

3. **Data integrity:** any party can verify that the data downloaded is correct. *Acceptance criteria:* data integrity of published data can be verified.

4. **Membership and non-membership proofs:** smart contracts support efficient membership  and non-membership proofs on published data. *Acceptance criteria:* Plutus supports efficient membership and non-membership proofs of data blobs on published data.

5. **Cost, throughput, and publication latency that the identified applications can bear:** materially cheaper than posting equivalent data to layer 1, at throughput and publication latency sufficient for the workshop's use cases. *Acceptance criteria:* cost per byte substantially below current layer 1 posting;  throughput above current layer 1 levels; publication latency at a similar level as layer 1 posting; all stated as figures a proposed solution can be measured against.


**Constraints:**

  1. **Timeline determines relevance:** a solution more than roughly eight months away is too late for some projects launching within the year; beyond that horizon,  it must demonstrate a significant throughput improvement or another clear advance to displace an already-integrated alternative.

  2. **Cardano's existing cryptographic standards are the baseline:** post-quantum security (PQS) is desirable, but not a requirement; conformance with Cardano's current standards is.

**Non-Goals:**

* Not a general-purpose storage or archival service. The problem is verifiable availability for a defined period, not durable storage of arbitrary content.

* Not privacy or confidentiality. Published data is public.

* Not application-specific verification. The mechanism must let users verify that their data is included; interpreting that data is the application's concern.

* Not a replacement for on-chain data. Data that belongs in the ledger stays in the ledger.

## Open Questions


1. What proof system supports both membership and non-membership efficiently at the throughput required, and how is it referenced from a Plutus script? 

2. How is publication priced so that occasional small commitments and sustained high-throughput workloads are both viable, and who pays for retention — publisher, retriever, or protocol?

3. What is the simplest first phase solution that is genuinely useful to at least one of the use cases above, and what does it defer?

4. What is the impact of the solution to SPOs’ hardware requirements and costs? How are they incentivized to follow the suggested solution?

5. How fine-grained retention time is?

6. How much time does it take for the submitted data to become publicly available?


## References

- **[1]** Data Availability Technical Workshop. IO Research, 3 September 2026. Requirements gathered from multiple layer 2 projects. [Recording](https://drive.google.com/file/d/1iVEuNebQcVMIlWpO_8GcszGMJigMIGIB/view?referrer=luma). 
- **[2]** Sharding CPS — Horizontal Scaling of Cardano through Sharding. *(CPS number TBC; coupled problem statement.)*
- **[3]** Cardano PubSub: A Verifiable Publish/Subscribe Communication Layer for the Cardano Ecosystem. Project documentation and source-code repository. [GitHub](https://github.com/input-output-hk/pubsub).
- **[4]** Celestia. External data availability layer. [Website](https://celestia.org).
- **[5]** IPFS. Content-addressed storage. [Website](https://ipfs.tech).
- **[6]** Gummiworm Whitepaper. Online protocol documentation. [Whitepaper](https://gummiworm.net/whitepaper/introduction).
- **[7]** Midgard L2: Scaling Cardano with Optimistic Rollups. Technical specification. [PDF](https://anastasia-labs.github.io/midgard/midgard.pdf).
- **[8]** Babel Fees via Limited Liabilities. [Paper](https://arxiv.org/abs/2106.01161).
- **[9]** Hydra: Fast Isomorphic State Channels. Financial Cryptography and Data Security, 2021. [Paper](https://eprint.iacr.org/2020/299.pdf).
- **[10]** Project Catalyst — Fund 14. [Website](https://projectcatalyst.io/funds/14).


## Copyright

This CPS is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).


