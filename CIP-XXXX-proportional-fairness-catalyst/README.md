---
cps: 9999
title: Proportional Fairness in Stake-based Voting
status: open
authors:
  - name: Qin Wang
    affiliation: CSIRO Data61
    github: qinwang-git
  - name: Yuzhe Zhang
    affiliation: CSIRO Data61
  - name: Manvir Schneider
    affiliation: Cardano Foundation
  - name: Davide Grossi
    affiliation: University of Groningen & University of Amsterdam
date-created: 2025-08-03
topics:
  - governance
  - treasury
  - stake-based voting
discussions-to: https://github.com/cardano-foundation/CIPs/discussions/XXX
---

## Summary

In Project Catalyst, Cardano’s on-chain treasury system, proposals are approved through stake-based approval voting. However, evidence shows that the current mechanism can lead to disproportionate voting power, where a single large stakeholder (a "whale") can unilaterally determine outcomes. This CPS identifies this governance limitation and calls for a proportionally fair voting mechanism that aligns voting power more closely with stake, yet avoids extreme centralization. 

We propose formalizing the problem using a weighted quota voting rule (WQR) and the Banzhaf power index as a measure of influence. Our goal is to ensure that voting power is proportional to stake, either deterministically or in expectation under reasonable assumptions on stake distributions.

## Problem Statement

Catalyst currently adopts a greedy approval voting mechanism: projects are selected by maximizing the sum of approving stake, subject to the treasury budget. This process leads to the following two issues:

1. **Disproportionate Influence**: Due to skewed stake distributions, a single voter with a large stake can override the collective approval of thousands of smaller stakeholders.
2. **Partial Project Visibility**: Voters cannot feasibly review all proposals, leading to low overlap in voting sets and further compounding the influence imbalance.

In Fund13, for example, our own proposal received 196M votes, 92\% of which came from a single whale. That voter determined the outcome not only of our proposal but also of several others—some passed, some failed, depending solely on how that user allocated their stake.

This CPS seeks to design a voting rule that:
- **Aligns voting power proportionally with stake**, and
- **Avoids single-user dominance**, even under uneven stake distributions.

## Impact

Solving this problem improves fairness in on-chain treasury allocation and strengthens the legitimacy of Catalyst governance. It also provides a reusable methodology for designing stake-aware voting rules in other Cardano governance contexts, such as dReps and constitutional updates.

Expected benefits include:
- More equitable representation of the Cardano community in governance outcomes.
- Stronger incentives for broader participation by reducing whale dominance.
- Mathematical and simulation-based analysis tools to measure fairness and influence.

## Prior Art

While stake-based governance is common in PoS systems, existing designs either rely on simple weighted approval (e.g., Catalyst) or complex ranking rules. The concept of proportional voting power using the **Banzhaf index** has been explored in social choice theory but is underutilized in blockchain systems.

Some recent literature relevant to this CPS includes:
- Rey et al. (2023), *Computational Social Choice for Participatory Budgeting*
- Kiayias et al. (2022), *SoK: Blockchain Governance*

Our approach is novel in its attempt to:
- Theoretically characterize and prove impossibility results under deterministic settings,
- Propose a probabilistic fairness model using stake distributions, and
- Quantify deviations between stake and power via expected Banzhaf ratios.

## Backwards Compatibility

This CPS only identifies the problem and does not mandate changes. Future CIPs can build on this CPS to propose and implement new governance mechanisms. The current Catalyst infrastructure (i.e., voting backend and tallying scripts) would likely require adjustments, but these are manageable and compatible with Catalyst’s modular design.

## Reference Implementation

A full mathematical model and theoretical results are available in our accompanying technical report:
> [Link to PDF report on Google Drive (comment access)](https://drive.google.com/file/d/XXX)
> [Link to Our proposal in Project Catalyst Fund13](https://projectcatalyst.io/funds/13/cardano-use-cases-concept/proportionality-in-stake-based-voting)

Simulation code and quota-weight calibration experiments are under development and will be provided in the next milestone.

## Path to Resolution

This problem can be considered resolved once:
- A CIP proposing a proportionally fair WQR is published and accepted.
- Empirical simulations show that the expected voting power aligns closely with proportional stake (within reasonable variance).
- The new voting rule is tested in a Catalyst pilot round or simulation environment.

---

