---
CPS: 7
Title: Voltaire era Governance
Status: Open
Category: Ledger
Authors: 
  - Pi Lanningham <pi@sundaeswap.finance>
Proposed Solutions:
  - CIP-1694
Discussions:
  - https://discord.gg/hdqHwSgWvG
Created: 2023-03-14
License: CC-BY-4.0
---

## Abstract

It has long been part of Cardano's vision for the "final" roadmap era to be one of Governance: allowing the community of ADA token holders to meaningfully own the decision making process by which the chain evolves.

To frame this discussion, it's important to outline a set of goals and baseline truths. Some of these will be neutral and uncontroversial, while others are in need of community discussion.

### Acknowledgements
<details>
<summary> Thank you to the following people who helped review this draft before it was published: </summary>

 * Adam K. Dean
 * Jared Corduan
 * Vanessa Harris
 * HeptaSean

</details>

## Problem

At the core of it, a system of governance boils down to how decisions are made and enforced.  Cardano currently has 3 core decisions that greatly impact the operation of the chain:

 - When and how to change the ledger rules (a "Controlled Hard Fork")
   - These changes are often drastic, with fundamental tradeoffs and extremely high risks
 - When and how to update various protocol parameters
   - These parameter changes, while limited in scope compared to a hard fork, can still have potentially existential risks on the chain
 - When and to whom to disburse funds from the treasury
   - Over the last several years, this treasury has accumulated nearly 1 billion ADA, currently worth hundreds of millions of dollars

The impact of these decisions are also often closely intertwined: development of the next hard fork may need funding from the treasury; parameters may need to be tweaked after a hard fork; etc.

Today, these decisions are primarily made by the founding entities (IOG, Cardano Foundation, and Emurgo). While these entities often consult the community when making these decisions, the final power lies in their hands, with very little that can be done beyond an uncontrolled hard fork by the stake pool operators.

For a variety of reasons, including moral, philosophical, financial, and possibly regulatory, these founding entities want to dilute their own power substantially, and share the burden of governance of the chain with the community that has arisen around it.

IOG in particular has continued to provide skill and resources for years longer than initially intended, and is significantly over-budget and over-extended. IOG has said that they may be unable or unwilling to support development of the chain indefinitely, and so an expedient and iterative approach to governance is likely to have higher positive impact on our ability to maintain velocity as an ecosystem.

However, diluting that power to the community comes with substantial risks and challenges, not the least of which is ensuring that the will of the community is captured *accurately*. For example, one barrier to that accuracy is the possibility of "sybil attacks", wherein the anonymity of the blockchain allows someone to cast their vote many times.

## Use cases
<!-- A concrete set of examples written from a user's perspective, describing what and why they are trying to do. When they exist, this section should give a sense of the current alternatives and highlight why they are not suitable. -->

## Goals

Synthesizing from the above, and with input from the broader Cardano community, the following goals, constraints, considerations, or ground truths for any governance system arise:

1. A system of on-chain rules should allow decisions to be made and enacted regarding (at a minimum) the three types of changes listed above.
2. Every (or nearly every) ADA holder should be able to meaningfully participate in this decision making process.
3. This system should not materially undermine the security of the chain.
4. This system should not undermine its ability to serve its financial function, such as overburdening the chain, damaging the monetary policy, etc.
5. This system should be implementable within a reasonable time frame and budget.
6. This system should be recursively updatable; if improvements or changes to the system of governance are needed, they should be voted on and enacted via this system.
7. This system is highly dependent on the off chain user experience and community tooling, since very few users are reading raw CBOR dumps from the chain.
8. This system should be cognizant of the fact that different decisions can have different impact and risk thresholds.
9. This system cannot avoid the fact that stake pool operators of the network, collectively, always maintain control over a "pocket nuke": under sufficient discontent and misalignment with the will of governance, they can modify the code and initiate an uncontrolled hard fork to produce a separate chain aligned with their values.

Additionally, here is a more opinionated (and potentially controversial) list of potential considerations for a CIP, presented purely to foster discussion:

1. There is currently no known decentralized "proof of personhood" system that is well specified and easily implementable, and without such a system, "one lovelace one vote" systems are the most effective defense against sybil attacks.
2. Given the current near total control over these decisions that these founding powers have, any dilution of power that doesn't compromise the security of the chain or risk a deadlock is a worthwhile step to take.
3. The system loses legitimacy if participation is extremely low, or participation is severely uninformed; If a significant portion of the Cardano community has not yet had a reasonable opportunity to participate, or the majority of participation is indinstinguishable from randomness, then any decisions made during this time are illegitimate.
4. Not every ADA holder is interested in *directly* participating in every decision. Often an ADA holders voice can still be heard through delegation to another ADA holder.
5. If the system contains such a notion of delegation, the ability to withdraw, redirect, or reclaim that voice at any time is an important tool in fighting corruption.
6. While it may be useful to draw inspiration from existing real-world systems, it should also be understood that blockchain governance will have an entirely different set of constraints.  For example, the ADA community does not share one culture or geographic locality. Additionally, the decisions being made are not the same kinds of decisions that a world government needs to make.
7. The uncontrolled hard fork described above is dangerous (from a safety standpoint) and disruptive (from an economic standpoint); it will likely seriously undermine the cohesion of the Cardano community. For this reason, it should be considered a tool of absolute last resort.

## Open Questions

Based on the goals above, an incomplete set of questions arises that any proposed solution likely ought to answer:

1. What are the exact categories of actors considered by the proposed system, and what actions are available to them under what conditions? What are the explicit justifications for the additional complexity added by distinguishing each category as a separate category?
2. How is the weight of each vote determined in the proposed system, and how does it defend against fraud and manipulation?
3. How does the proposed system decide that it has "reached quorum", and can legitimately enforce the decision that has been reached?
4. What vectors for denial of service (at both the protocol level and social level), and how does the proposed system mitigate these?
5. What is the proposed path to adoption of the proposed system?
6. What "transitionary" periods does the solution include, and what are the justifications for them? Or, conversely, what is the justification for *not* having a transitionary period?
7. What is an estimated timeline and budget for implementation of the proposed system?
8. Who is going to implement the proposed solution, and how will it be paid for?

### Philosophical Questions

Below are a set of philosophical questions applicable across a broad range of solutions that are being discussed by the community:

1. Are there any "fundamental rights" of ecosystem participants that should be protected by the governance system?
2. Must any and all voting related to governance matters occur directly on the layer 1 ledger?
3. What role, if any, do the founding entities play after governance is adopted?
4. What kinds of community standards are needed outside of the scope of a specific solution at the ledger layer?
5. What kinds of incentives (or disinsentives) should we use to align behavior with our goals? Should we try to compensate actors for the time and effort they put in, or does that create corrupt and misaligned incentives of their own?
6. Is the ability to delegate overall more helpful or harmful? Does the risk of "popularity" based delegation (as opposed to trust / expertise based delegation) dilute the votes of others more than it increases inclusivity?

## Copyright

This CPS is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
