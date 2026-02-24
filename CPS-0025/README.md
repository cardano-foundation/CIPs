---
CPS: 25
Title: Small pool disadvantage in VRF tiebreakers
Category: Consensus
Status: Open
Authors:
    - Ryan Wiley <rian222@gmail.com>
Proposed Solutions: []
Discussions:
    - https://github.com/IntersectMBO/ouroboros-consensus/pull/1548
    - https://github.com/cardano-foundation/CIPs/pull/1130
Created: 2026-01-09
License: CC-BY-4.0
---

## Abstract

Slot/height battles are infrequent on Cardano, but for small pools they can dominate realized rewards and create outsized ROI variance. This CPS formalizes the problem and constraints, including the historical shift from the leader VRF (the "L hash") to the block VRF (the "B hash") as the tiebreaker and the resulting community concern. It frames the open questions around whether any bias is desirable, how it should be governed, and how to balance fairness with security and Sybil-resistance objectives.

## Problem

Cardano height battles and slot battles are relatively infrequent, but when they occur they can have a disproportionate impact on very small pools that produce few blocks. A single lost battle can materially change a small pool's epoch rewards and create larger ROI swings for both operators and delegators compared to large pools that make many blocks.

Historically, the ledger used the leader VRF (range-extended value, sometimes described as the "L hash") as a tiebreaker. This introduced a small bias in favor of smaller pools because winning a leader election already implies a smaller VRF value. Later, the implementation shifted to using the non-range-extended block VRF (the "B hash") as the tiebreaker, removing that small-pool advantage in favor of a more uniformly random outcome. This change was not preceded by a CPS and led to pushback in the SPO community.

The 2025 Input Output Engineering Core Development Proposal included a line item titled "Revised Stake Pool Incentive Scheme" with the description: "Investigate and evaluate potential adjustments to the SPO incentive scheme, focusing on improving viability/fairness for smaller pools by considering existing proposals and analyzing costs/benefits. Aims to enhance decentralization and ecosystem health." The community voted in favor of this proposal, and this CPS complements that initiative by clarifying a concrete fairness issue that affects small pools.

Available empirical data suggests that slot battles occur on the order of hundreds per epoch (e.g., a rough upper bound of ~550 per epoch based on mainnet parameters, with PoolTool observing lower counts), while height battles appear much rarer (on the order of tens per epoch under current network conditions). This makes the aggregate, network-wide effect of tiebreaker bias relatively small, yet the variance impact on individual small pools can remain meaningful. An analysis of using the L hash as the tiebreaker suggests that mean reward changes are bounded (e.g., an upper theoretical bound around +5.263% for maximum bias). Empirical analysis (epoch 562 stake distribution) reports that the smallest 2560 pools (43% combined stake) benefit, the largest 205 pools (57% combined stake) lose, the smallest pool that loses has 0.185% stake, and the largest relative benefit/loss are approximately +2.6% and -1.4%, respectively. These figures are summarized in the HackMD note referenced below, but they can mask large ROI swings for pools with low expected block production.

In other words, the average effect can be small while the variance impact on individual small pools remains large.

There is an open question about whether intentionally biasing some or all tiebreakers toward smaller pools is acceptable from a security and game-theoretic perspective, especially given that slot/height battles are relatively rare. It has also been suggested that if bias is desired, it should be introduced in a principled, tunable way (e.g., via a protocol parameter) rather than by reintroducing a historical behavior that was arguably an implementation bug. This CPS formalizes the problem space and constraints so the community can evaluate whether bias is desirable, how much bias is acceptable, and what class of solutions should be considered.

## Use Cases

- Two small pools are each about to mint what would be their only block of the epoch. Both win leadership in the same slot or height, but only one wins the tiebreaker. The winning pool appears to have "performed," while the losing pool appears to have "failed," even though both were elected. This single outcome can materially change ROI and how potential delegators perceive the pool's reliability.
- A small SPO operating a low-stake pool experiences large swings in ROI because one lost slot/height battle can erase a material share of their expected epoch rewards. The SPO wants predictable performance so delegators can evaluate the pool fairly.
- A delegator comparing small pools sees volatile rewards that are driven by rare battles rather than operator performance, making it harder to choose or remain with a small pool.
- Protocol designers and governance participants need to evaluate whether a tiebreaker bias (e.g., via L hash) is acceptable given Sybil-resistance and fairness goals, or whether variance should be addressed elsewhere (e.g., in rewards).
- Stake pool operators want clarity and process around tiebreaker rules so changes do not occur without community consensus.

## Goals

- Explain in plain terms why slot/height battles hit small pools harder and why that matters to delegators and operators.
- Ground the discussion in known facts (battle frequency and expected reward impacts) so the problem is sized realistically.
- Call out the constraints any fix must respect, including security, Sybil-resistance, and governance process.
- Make it clear that changes to tiebreaker behavior should go through transparent, community-backed governance.
- Provide a clear foundation for a future CIP that proposes a concrete solution.

## Open Questions

- Should any tiebreaker bias exist at all, and if so, how much bias is acceptable?
- Would 100% bias toward the smaller pool in slot/height battles be a security issue, and if so, what range of bias could be considered safe?
- If bias is desired, should it be parameterized (governable), and what would the control surface look like?
- What are the security and game-theoretic implications of biasing slot/height battles toward smaller pools?
- Should bias treat slot battles and height battles differently?
- Would it be more appropriate to reduce variance at the reward level rather than at chain selection?
- How should changes to tiebreaker behavior be governed and communicated to avoid unannounced shifts?

## References

- https://github.com/IntersectMBO/ouroboros-consensus/pull/1548
- https://hackmd.io/hX7q5s8JSKSP-j3525J0bA (Alexander Esgen)
- 2025 Input Output Engineering Core Development Proposal ("Revised Stake Pool Incentive Scheme")

## Copyright

This CPS is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
