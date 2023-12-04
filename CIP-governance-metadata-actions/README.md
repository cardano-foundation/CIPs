---
CIP: ?
Title: Governance Metadata - Governance Actions
Category: Metadata
Status: Proposed
Authors:
  - Ryan Williams <ryan.williams@intersectmbo.org>
Implementors: []
Discussions:
  - https://github.com/cardano-foundation/cips/pulls/632
Created: 2023-11-23
License: CC-BY-4.0
---

## Abstract
The conway ledger era ushers in on-chain governance for Cardano via [CIP-1694 | A First Step Towards On-Chain Decentralized Governance](https://github.com/cardano-foundation/CIPs/blob/master/CIP-1694/README.md), with the addition of many new on-chain governance artifacts.
Some of these artifacts support the linking off-chain metadata, as a way to provide context.

The [CIP-100 | Governance Metadata](https://github.com/cardano-foundation/CIPs/pull/556) standard provides a base framework for how all off-chain governance metadata should be formed and handled.
But this is intentionally limited in scope, so that it can be expanded upon by more specific subsequent CIPs.

This proposal aims to provided a specification for off-chain metadata which gives context to governance actions, building on from the CIP-100 framework.
Without a sufficiently detailed standard for governance actions we introduce the possibility to undermine voters ability to adequately assess governance actions.
Furthermore a lack of such standards risks preventing interoperability between tools, to the detriment of user experiences.

### Acknowledgments

<details>
  <summary><strong>Governance Metadata Working Group - Workshop #1 2023-12-04</strong></summary>

  I would like to thank those that contributed to the Governance Metadata Working Group Workshop #1 hosted by Ryan Williams ([see presentation slides with notes](https://docs.google.com/presentation/d/18OK3vXexCc8ZXq-dC00RDPPKcy2Zu4DiMo8PeIZ47_4/)).

  Thank you to the co-hosts:
  - Adam Dean
  - Thomas Upfield

  Thank you to the participants:
  - Carlos Lopez de Lara
  - Igor Veličković
  - Johnny Kelly
  - Kenric Nelson
  - Kevin Hammond
  - Lorenzo Bruno
  - Rhys Morgan
  - Eric Alton
  - Samuel Leathers
  - Vladimir Kalnitsky

</details>

## Motivation: why is this CIP necessary?
Blockchains are poor choices to act as content databases.
This is why governance metadata anchors were chosen to provide a way to attach long form metadata content to on-chain events.
By only supplying an onchain hash of the off-chain we ensure correctness of data whilst minimizing the amount of data posted to the chain.

### For voters
When observing from the chain level, tooling can only see the content of the governance action and it's anchor.
These on-chain components do not give give any context to the motivation nor off-chain discussion of an governance action.
Although this information would likely be desired context for voters.
By providing rich contextual metadata we enable voters to make well informed decisions.

### For all participants
By standardizing off-chain metadata formats we facilitate interoperability for tooling which creates and/or renders metadata attached to governance actions.
This intern promotes a rich user experience between tooling.
This is good for all governance participants.

## Specification
Although there are seven types of governance action defined via CIP-1694, we focus this proposal on defining core properties which must be attached to all types.
We leave room for future standards to refine and specialize further to cater more specific for each type of governance action.

### Extended Vocabulary
The following properties extend the vocably of [CIP-100's body field](https://github.com/Quantumplation/CIPs/blob/2382cf0c69a11ee1bd53c48a2dbb19c5759515f5/CIP-0100/README.md?plain=1#L171C1-L181C116).

#### Title
- This should be a sentence which should act as a human readable identifier for the GA.
- It should briefly introduce the GA so at a glance users can differentiate actions.
  - i.e; Increase K protocol parameter to 100,000 to increase decentralization of Cardano.
- The intention for this field is to act as a quick and clear differentiator between governance actions.

#### Abstract
- This should be a short amount of free flow text, limited to ~200 words.
- This should a short description of the reason behind the GA, so if a problem is being addressed: what, why and how.
- This should summarizes the problem and how GA fixes the problem - to help voters gain an understanding the context behind the GA without having to dig in too deep.
- This could help a user differentiate two actions which are having the same onchain effect, with similar titles.

#### Motivation
- This should be longer free form text encapsulating context around the problem that the GA is addressing.
- The content should also include mention of the use cases and stakeholders.
- This field is an opportunity for the author to provide full context to the problem being addressed.

#### Rationale
- This should be longer free form text discussing how the GA addresses the problem identified in the motivation.
- i.e "by increasing X parameter we increase rewards for SPOs thus encouraging new SPOs to join the network.
- This section should fully justify the changes being made to Cardano.
- This should include what led to particular design decisions.
- It should describe alternate designs considered and related work.
- The rationale should provide evidence of consensus within the community and discuss significant objections or concerns raised during the discussion.
- For some GAs this section SHOULD to be very long.
- This should include any recommendations made by relevant organizations or committees.

### Versioning
This proposal should not be versioned, to update this standard a new CIP should be proposed.
Although through the JSON-LD mechanism further CIPs can add to the fields defined here.

## Rationale: how does this CIP achieve its goals?

// todo

- base standard, good for MVP, makes this more straight forward to implement and support for all.
- want to start simple with this proposal - MVG.
- fields based on the CIP process with the specification and most of the header removed.

### Open Questions
- Should fields be optional or compulsory?
- How do the above fields relate to the CIP-100 justification field?

## Path to Active

### Acceptance Criteria
- [ ] This standard is supported by two different tooling providers used to submit governance actions to chain.
- [ ] This standard is supported by two different chain indexing tools, used to read and render metadata

### Implementation Plan
Solicitation of feedback
- [ ] Run X number of online workshops to gather insights from stakeholders.
- [ ] Seek community answers on all [Open Questions](#open-questions).
Implementation
- [ ] Author to provide reference implementation in a dApp form.
- [ ] Author to provide example metadata.

## Copyright
This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).