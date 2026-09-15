---
CPS: "?"
Title: Trustworthy Off-chain Message Dissemination
Category: Network
Status: Open
Authors:
    - Will Wolff <william.wolff@iohk.io>
    - Ezequiel Postan <ezequiel.postan@iohk.io>
    - Denis Firsov <denis.firsov@gmail.com>
    - Jesus Diaz Vico <jesus.diaz.vico@gmail.com>
    - Dana Alibrandi <dalibrandi@gmail.com>
    - Mauro Jaskelioff <mauro.jaskelioff@iohk.io>
Proposed Solutions: []
Discussions:
    - Original PR: https://github.com/cardano-foundation/CIPs/pull/?
Created: 2026-08-20
License: CC-BY-4.0
---

## Abstract

Cardano participants need to exchange time-sensitive messages outside the ledger. Stake pool operators need incident alerts; delegators need pool announcements; governance participants need voting updates; and dApp users need notifications about positions and protocol changes.

These messages commonly travel through mailing lists, chat platforms and provider backends. Such channels can authenticate accounts or carry signed content, but Cardano has no common messaging standard combining publisher authentication, integrity and resistance to targeted suppression. Delivery also depends on infrastructure beyond the chain's consensus guarantees.

A peer-to-peer network can remove dependence on one delivery operator, but its guarantees depend on membership, peer discovery and adversarial participation. An attacker able to surround a recipient with controlled peers may suppress messages without leaving evidence of what was withheld. A communication channel anchored on Cardano also needs to explain how it behaves when that chain halts or forks.

This statement asks for verifiable message origin and integrity, quantified resistance to suppression, and practical participation costs. It distinguishes delivery to directly participating infrastructure from onward delivery to end users, and leaves the choice of protocol and trust mechanism to proposed solutions.

## Problem

### The gap

Cardano's ledger records agreed state. Operational communication around that state has different requirements: it must reach the relevant people and services in time for them to act, without placing every notification in a transaction.

The required properties are:

- **Authenticity:** recipients can verify the claimed publisher through an explicit trust relationship.
- **Integrity:** recipients can verify that content has not changed.
- **Availability:** intended recipients can obtain the message within a stated time and failure budget.

Existing channels provide useful parts of this service. For example, a publisher can sign a notice sent through a mailing list, and a messenger can authenticate its accounts. What is missing is a shared standard connecting publisher authority to Cardano identities while addressing service outages, selective delivery and suppression. A recipient cannot infer from silence whether a message was withheld or never sent.

Confidentiality is not required for the public broadcasts considered here. Applications may have additional privacy requirements, particularly when addressing notifications to individuals.

### Why existing peer-to-peer networks do not close it

Cardano's node-to-node network carries blocks and transactions. Extending it to general application messaging would need to address participation by wallet and dApp infrastructure, isolation of messaging load from consensus traffic, and delivery requirements beyond ledger diffusion. An incident channel running within the affected node software would also share a failure dependency with the system it is meant to help coordinate.

A separate gossip network avoids some of those dependencies, but decentralisation alone does not establish its delivery guarantees. GossipSub, for example, includes peer scoring, mesh hardening and explicit peering support.[^gossipsub] Its deployment still needs an appropriate source of peers and a policy for admission. Freely generated identities can make that source vulnerable to Sybil influence; this is a deployment concern, not a requirement that every GossipSub network use unrestricted membership.[^libp2p]

An **eclipse** occurs when an adversary controls all of a victim's neighbours and therefore its network view. The project's analysis of SecureCyclon found targeted eclipse attacks under a silent adversary in the tested configurations.[^securecyclon][^cyclonreport] That result motivates examining the membership and peer-selection assumptions of a solution. It does not establish that every alternative sampler or gossip deployment fails.

A proposal should therefore explain how an adversary can acquire influence, how that influence affects a chosen recipient, and which assumptions support its delivery estimates.

### Why this is hard to solve on the chain it protects

An emergency channel may be needed precisely when Cardano is disrupted. If it depends on on-chain membership updates or chain-derived randomness, a halt can freeze those inputs. A fork can make participants disagree about them.

A solution should state what continues to work from already available state, what requires fresh chain data, and what happens when participants disagree. Alternative providers may reduce some dependencies, but their trust and availability assumptions also need to be stated.

## Use Cases

The following scenarios are drawn from the project's [use-case survey](https://github.com/input-output-hk/pubsub/blob/5d6391813904159a04908dbdd20b03d1a56f85d1/docs/actor-use-case-analysis.md). Population estimates are planning assumptions to validate with operators.

| User and task | Why delivery matters | Direct recipients and remaining delivery path |
| --- | --- | --- |
| A protocol team warns stake pool operators of an incident | Operators must receive an authentic alert in time to respond | Potentially thousands of always-on operator nodes |
| A stake pool announces retirement or an operational change to delegators | Delegators need time to assess or change their delegation | Wallet backends may relay the notice to their users |
| A governance body or dRep announces a proposal, voting deadline or voting intention | Participants need the information while action is still possible | Governance services and wallet backends may deliver onward to voters |
| A dApp notifies users about positions or protocol changes | Users need to recognise relevant alerts and act within the application's deadline | Wallet or dApp backends may route notifications to individual users |

These scenarios have different delivery requirements. Routine announcements may tolerate best-effort delivery; incident and deadline-driven messages need explicit targets. The population directly exchanging messages can also differ substantially: a topic reaching thousands of operators may use many more peers than one reaching end users through a small number of infrastructure providers.

Delivery to a wallet backend is not delivery to every wallet user. A proposal should identify its endpoint of responsibility and explain which guarantees depend on the onward channel. Existing pool registrations may provide useful identity information, but wallet, governance and dApp participants need not share the same registration mechanism.

### Stakeholders

Stake pool operators receive incident alerts and publish pool notices. Protocol teams, governance bodies, dReps and dApp teams publish messages. Wallet and infrastructure providers connect the dissemination service to end users. Each group should help establish realistic delivery deadlines, availability assumptions and operating costs.

## Goals

Goals are ranked in the order below. Proposed solutions should state the scope and assumptions of their guarantees.

1. **Authenticity and integrity.** Recipients can verify the claimed publisher and unaltered content without trusting the delivery path. The proposal must explain how a key is associated with the publisher it represents.
2. **Censorship resistance.** Quantify the likelihood and duration of suppression against both a chosen recipient and the participant population. State adversarial and availability assumptions, the endpoint of the guarantee, and how recovery or detection works where provided.
3. **Resistance to targeted peer selection.** An adversary must not be able to isolate a chosen recipient cheaply or repeatedly at will. Explain the cost and limits of influence through identities, joining times, discovery or peer selection. The required outcome does not prescribe a particular membership or topology mechanism.
4. **Practical per-node cost.** State connection, bandwidth, computation and storage costs across the intended operating range. Separate dependence on membership from dependence on subscriptions, publication rate and payload size, and explain the limits needed for ordinary operators to participate.
5. **Openness to application payloads.** Support named message streams carrying different kinds of application content, subject to explicit size and resource limits.
6. **Application-level addressing.** Allow an application to indicate the intended recipient of a payload. A solution need not itself provide private or selective transport, but should state whether all subscribers receive the addressed content.

### Non-goals

- **Confidentiality:** the motivating broadcasts are public; applications may impose additional requirements.
- **Long-term message persistence:** storage beyond a stated delivery or recovery window is a separate service.
- **Consensus on a delivery log:** recipients need to authenticate received content, but need not agree on a shared record of delivery.

## Open Questions

- **Adversarial participation:** what fraction or concentration of participants can an adversary realistically control, and how do the admission costs support that assumption?
- **Delivery targets:** what deadlines and failure probabilities do the scenarios require? Distinguish a named recipient's risk from network-wide failure, and state the interval each probability covers.
- **Availability:** how often do intended operators go offline, for how long, and how correlated are their failures?
- **Topic populations:** how many direct participants will each scenario involve, and how do those populations overlap?
- **Small topics:** can the same design serve tens and thousands of participants, or are different mechanisms needed? What evidence supports each range?
- **Participation costs and incentives:** what should joining and continued participation cost, and what behaviour can be verified if incentives depend on it?
- **Dependency failures:** what must continue working during a chain halt or fork, which components can use alternative providers, and what trust or delivery guarantees change?

## References

### Prior art

- Vyzovitis, Napora, McCormick, Dias and Psaras. *GossipSub: Attack-Resilient Message Propagation in the Filecoin and ETH2.0 Networks.* arXiv:2007.02754. <https://arxiv.org/abs/2007.02754>
- *gossipsub v1.1 — Security extensions to improve on attack resilience and bootstrapping.* <https://github.com/libp2p/specs/blob/master/pubsub/gossipsub/gossipsub-v1.1.md>
- libp2p. <https://libp2p.io> — including its Kademlia DHT, one available discovery mechanism: <https://github.com/libp2p/specs/tree/master/kad-dht>
- Antonov and Voulgaris. *SecureCyclon: Dependable Peer Sampling.* 43rd IEEE International Conference on Distributed Computing Systems, ICDCS 2023, pp. 1–12. <https://doi.org/10.1109/ICDCS57875.2023.00041>
- The peer-sampling survey this statement draws on, and the analysis of SecureCyclon under a silent adversary: <https://github.com/input-output-hk/pubsub/blob/5d6391813904159a04908dbdd20b03d1a56f85d1/formal_spec/related_work/related_peersampling.md> and <https://github.com/input-output-hk/pubsub/blob/5d6391813904159a04908dbdd20b03d1a56f85d1/formal_spec/peer_sampling/secure_cyclon/REPORT.md>

### Related documents

- A proposed solution to this statement: [CIP](https://github.com/input-output-hk/pubsub/blob/main/docs/cip/README.md).
- CIP-0137, *Decentralized Message Queue*. <https://github.com/cardano-foundation/CIPs/tree/master/CIP-0137> — an existing Network-category proposal for
  topic-based message diffusion on Cardano. It addresses part of this problem for stake pool
  operators, authenticating participants by their operational certificates so that Sybil
  resistance follows from active stake. It states no delivery guarantee and no resistance to
  targeted censorship, which is what this statement asks a solution to supply.
- The broader survey the four scenarios were drawn from: <https://github.com/input-output-hk/pubsub/blob/5d6391813904159a04908dbdd20b03d1a56f85d1/docs/actor-use-case-analysis.md>
- *PubSub Technical Report 1: Three-Layer Stack Findings and a Path Forward* — the evaluation
  that led to this statement:
  <https://github.com/input-output-hk/pubsub/blob/5d6391813904159a04908dbdd20b03d1a56f85d1/docs/technical-report-1.md>

### Method notes

[^gossipsub]: Dimitris Vyzovitis, Yusef Napora, Dirk McCormick, David Dias and Yiannis Psaras. *GossipSub: Attack-Resilient Message Propagation in the Filecoin and ETH2.0 Networks.* arXiv:2007.02754. <https://arxiv.org/abs/2007.02754>. The peer scoring and mesh hardening referred to here are specified in gossipsub v1.1, *Security extensions to improve on attack resilience and bootstrapping*: <https://github.com/libp2p/specs/blob/master/pubsub/gossipsub/gossipsub-v1.1.md>.

[^securecyclon]: Antonov and Voulgaris. *SecureCyclon: Dependable Peer Sampling.* 43rd IEEE International Conference on Distributed Computing Systems, ICDCS 2023, pp. 1–12. <https://doi.org/10.1109/ICDCS57875.2023.00041> The hardened descendant of CYCLON, and the peer-reviewed state of the art in Byzantine-resilient partial-view peer sampling.

[^cyclonreport]: Silent attacks on SecureCyclon. The adversary is rate-honest and sends only well-formed, single-chain descriptors; it varies only which peer it contacts, which descriptors it forwards, and what it withholds. Four attack shapes were measured, of which three are targeted at a chosen victim. Method and results: <https://github.com/input-output-hk/pubsub/blob/5d6391813904159a04908dbdd20b03d1a56f85d1/formal_spec/peer_sampling/secure_cyclon/REPORT.md>. This is the project's own analysis and has not been separately peer-reviewed.

[^libp2p]: libp2p, the modular networking stack GossipSub is most widely deployed on. <https://libp2p.io>. Its Kademlia DHT uses self-generated peer identities; applications can provide other discovery or admission arrangements: <https://github.com/libp2p/specs/tree/master/kad-dht>.

## Copyright

This CPS is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
