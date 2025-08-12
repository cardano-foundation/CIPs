---
CIP: ?
Title: Proportional Fairness in Stake-based Voting for Project Catalyst
Status: Proposed
Category: Meta
Authors:
  - Qin Wang <qin.wang@data61.csiro.au>
  - Yuzhe Zhang <yuzhe.zhang@data61.csiro.au>
  - Manvir Schneider <manvir.schneider@cardanofoundation.org>
  - Davide Grossi <d.grossi@uva.nl>
Implementors: N/A
Discussions:
  - https://github.com/cardano-foundation/CIPs/pull/XXX
  - https://github.com/cardano-foundation/CIPs/discussions/XXX
Created: 2025-08-13
License: CC-BY-4.0
---

## Abstract

In Project Catalyst, Cardano's on-chain treasury system, proposals are approved through stake-based approval voting. However, evidence shows that the current mechanism leads to disproportionate voting power, where single large stakeholders can unilaterally determine outcomes. This CIP proposes a proportionally fair voting mechanism using weighted quota voting rules (WQR) and the Banzhaf power index to measure influence. The goal is to ensure voting power is proportional to stake while avoiding extreme centralization, addressing the governance limitation where whales can override collective decisions of thousands of smaller stakeholders.

## Motivation: why is this CIP necessary?

Project Catalyst currently uses a greedy approval voting mechanism where projects are selected by maximizing the sum of approving stake, subject to treasury budget constraints. This process creates significant governance issues that undermine the democratic principles of Cardano's treasury system.

**Evidence of the Problem**: In Fund13, empirical data shows extreme concentration of voting power. For example, one proposal received 196M votes, with 92% coming from a single whale voter. This single stakeholder determined not only that proposal's outcome but influenced multiple other proposals - some passed, some failed, based solely on one user's stake allocation decisions.

**Core Issues**:
1. **Disproportionate Influence**: Skewed stake distributions allow individual large stakeholders to override collective decisions of thousands of smaller participants
2. **Partial Project Visibility**: Voters cannot feasibly review all proposals, leading to low overlap in voting sets and further compounding influence imbalances
3. **Undermined Legitimacy**: The current system questions the fairness and democratic nature of Cardano's governance

This CIP addresses a fundamental governance challenge that affects the entire Cardano ecosystem's treasury allocation and community representation.

## Specification

This CIP proposes implementing a **Weighted Quota Voting Rule (WQR)** system that ensures proportional fairness in stake-based voting for Project Catalyst. The specification includes theoretical foundations, mathematical models, and implementation guidelines.

### Theoretical Framework

**Weighted Quota Voting Rule (WQR)**:
- Each voter $i$ has weight $w_i$ proportional to their stake
- A proposal passes if the sum of approving weights exceeds quota $q$: $\sum_{i \in S} w_i \geq q$ where $S$ is the set of approving voters
- Multiple proposals can be approved subject to budget constraints

**Banzhaf Power Index**:
- Measures actual voting influence of each participant
- For voter $i$: $\beta_i = \frac{\text{number of coalitions where } i \text{ is pivotal}}{\text{total number of coalitions}}$
- Proportional fairness achieved when $\frac{\beta_i}{\beta_j} \approx \frac{w_i}{w_j}$ for all voters $i, j$

### Data Types

#### VotingWeight
```typescript
type VotingWeight = {
  voter_id: string,
  stake_amount: bigint,
  normalized_weight: number
}
```

#### QuotaRule
```typescript
type QuotaRule = {
  quota_threshold: number,  // Between 0 and 1
  total_stake: bigint,
  required_approval_stake: bigint
}
```

#### FairnessMetrics
```typescript
type FairnessMetrics = {
  banzhaf_index: Map<string, number>,
  proportionality_ratio: Map<string, number>,
  concentration_coefficient: number
}
```

### Voting Mechanism

**Phase 1: Stake-Weighted Quota Calculation**
1. Calculate total participating stake: $W = \sum_i w_i$
2. Set quota threshold: $q = \alpha \cdot W$ where $\alpha \in (0.5, 1)$
3. Normalize weights: $\tilde{w_i} = w_i / W$

**Phase 2: Proposal Evaluation**
1. For each proposal, collect approving voter weights
2. Proposal passes if $\sum_{i \in \text{approvers}} w_i \geq q$
3. Apply budget constraints using optimization algorithm

**Phase 3: Fairness Verification**
1. Calculate Banzhaf power indices for all voters
2. Measure proportionality ratios: $r_i = \frac{\beta_i/\sum_j \beta_j}{w_i/\sum_j w_j}$
3. Flag proposals if concentration exceeds threshold

### Implementation Parameters

- **Quota Range**: $\alpha \in [0.6, 0.8]$ (configurable per fund)
- **Maximum Individual Influence**: No single voter should have $\beta_i > 0.3$
- **Proportionality Tolerance**: $|r_i - 1| < 0.2$ for voters with $w_i > 0.01W$

## Rationale: how does this CIP achieve its goals?

### Design Decisions

**Choice of Weighted Quota Voting Rules (WQR)**:
We selected WQR over alternative mechanisms (e.g., quadratic voting, liquid democracy) because:
- **Mathematical Tractability**: WQR allows precise calculation of voting power via Banzhaf indices
- **Stake Preservation**: Maintains the principle that voting power should correlate with economic stake
- **Implementation Simplicity**: Requires minimal changes to existing Catalyst infrastructure
- **Proven Theory**: Extensive literature in social choice theory provides theoretical foundations

**Banzhaf Power Index as Fairness Metric**:
The Banzhaf index captures actual influence better than stake weights because:
- It accounts for coalition dynamics and pivotal positions
- It measures the probability that a voter's decision changes the outcome
- It provides a normalized measure allowing cross-voter comparisons

**Probabilistic vs. Deterministic Fairness**:
Our analysis shows that deterministic proportional fairness is impossible under realistic stake distributions. Therefore, we adopt a probabilistic model where fairness holds in expectation over reasonable stake distribution assumptions.

### Alternative Designs Considered

**Quadratic Voting**: Rejected due to:
- Difficulty in preventing Sybil attacks in permissionless systems
- Unclear relationship between economic stake and voting rights
- Complex implementation requiring significant infrastructure changes

**Liquid Democracy**: Considered but rejected due to:
- Potential for delegation cycles and manipulation
- Complexity in tracking and verifying delegation chains
- Cultural mismatch with Cardano's direct participation principles

**Simple Majority with Stake Caps**: Rejected because:
- Arbitrary caps lack theoretical justification
- Still allows coordination attacks below the cap threshold
- Reduces economic alignment between stake and governance

### Backward Compatibility

**Catalyst Infrastructure**:
- Voting collection mechanisms remain unchanged
- Proposal submission process unaffected
- Only the tallying algorithm requires modification

**Wallet Integration**:
- No changes required to voting interfaces
- Stake calculation methods remain identical
- Results display may need updates to show fairness metrics

**Community Impact**:
- Gradual transition possible through pilot programs
- Educational materials needed to explain new fairness concepts
- Monitoring tools required to track proportionality metrics

### Security Considerations

**Manipulation Resistance**:
- Quota thresholds prevent small coalition attacks
- Banzhaf calculations are manipulation-resistant when quota is properly set
- Multiple proposal approval reduces single-point-of-failure risks

**Computational Security**:
- Banzhaf index calculation is computationally intensive for large voter sets
- Approximation algorithms may be needed for real-time calculations
- Verification mechanisms required to ensure correct power index calculations

**Economic Security**:
- Maintains stake-based security model of Cardano
- Prevents costless attacks while preserving economic alignment
- Quota parameters must be carefully calibrated to prevent deadlock scenarios

## Path to Active

### Acceptance Criteria

This CIP becomes 'Active' when the following criteria are met:

1. **Theoretical Validation**:
   - Mathematical proofs of proportional fairness properties are peer-reviewed and accepted
   - Impossibility results under deterministic settings are formally established
   - Probabilistic fairness model is validated through theoretical analysis

2. **Empirical Validation**:
   - Simulation studies demonstrate improved proportionality over current mechanism
   - Historical Catalyst data analysis shows significant reduction in whale dominance
   - Expected Banzhaf power ratios align closely with stake proportions (within 20% variance)

3. **Implementation Readiness**:
   - Reference implementation of WQR tallying algorithm is available
   - Banzhaf index calculation tools are developed and tested
   - Performance benchmarks show feasibility for Catalyst scale (10K+ voters, 1K+ proposals)

4. **Community Acceptance**:
   - Successful pilot testing in a Catalyst fund or simulation environment
   - Community feedback demonstrates understanding and support for fairness improvements
   - Integration plan with existing Catalyst infrastructure is approved by Project Catalyst team

5. **Governance Integration**:
   - Parameter setting process for quota thresholds is established
   - Monitoring and adjustment mechanisms for fairness metrics are deployed
   - Educational materials for voters and proposal submitters are available

### Implementation Plan

**Phase 1: Theoretical Foundation (Months 1-3)**
- Complete mathematical formalization of proportional fairness in WQR systems
- Publish peer-reviewed research on Banzhaf index applications to blockchain governance
- Develop theoretical framework for quota parameter optimization

**Phase 2: Software Development (Months 2-5)**
- Implement reference WQR tallying algorithm
- Develop efficient Banzhaf index calculation methods
- Create simulation framework for testing various stake distributions
- Build monitoring dashboard for fairness metrics

**Phase 3: Empirical Validation (Months 4-6)**
- Conduct comprehensive analysis of historical Catalyst voting data
- Run simulations comparing current mechanism vs. proposed WQR system
- Validate theoretical predictions against empirical observations
- Optimize quota parameters based on real-world stake distributions

**Phase 4: Pilot Implementation (Months 6-9)**
- Deploy pilot version in Catalyst testnet or dedicated simulation environment
- Gather community feedback on user experience and fairness improvements
- Iterate on implementation based on pilot results
- Prepare integration documentation and educational materials

**Phase 5: Production Deployment (Months 9-12)**
- Integrate WQR system into Catalyst production infrastructure
- Deploy monitoring and alerting systems for fairness metrics
- Train community moderators and Catalyst team on new system
- Establish ongoing parameter tuning and system maintenance processes

**Implementors**: Research team from CSIRO Data61, University of Groningen, and Cardano Foundation, with development support from IOG Catalyst team.

## References

### Academic Literature

1. Rey, S., Endriss, U., & de Haan, R. (2023). *Computational Social Choice for Participatory Budgeting*. Proceedings of IJCAI 2023.

2. Kiayias, A., Lazos, P., Oikonomou, P., & Zakynthinos, M. (2022). *SoK: Blockchain Governance*. Proceedings of Financial Cryptography and Data Security.

3. Banzhaf, J. F. (1965). *Weighted voting doesn't work: A mathematical analysis*. Rutgers Law Review, 19(2), 317-343.

4. Penrose, L. S. (1946). *The elementary statistics of majority voting*. Journal of the Royal Statistical Society, 109(1), 53-57.

5. Felsenthal, D. S., & Machover, M. (1998). *The Measurement of Voting Power: Theory and Practice, Problems and Paradoxes*. Edward Elgar Publishing.

### Cardano Ecosystem References

6. **CIP-1694**: Voltaire era governance structure and constitutional framework
7. **CIP-0030**: Cardano dApp-Wallet Web Bridge (for voting interface standards)
8. **Project Catalyst Documentation**: [https://docs.projectcatalyst.io/](https://docs.projectcatalyst.io/)

### Related Work

9. Buterin, V., Hitzig, Z., & Weyl, E. G. (2018). *Liberal Radicalism: A Flexible Design for Philanthropic Matching Funds*. Available at SSRN.

10. Zhang, Y., & Wang, Q. (2024). *Proportional Representation in Stake-based Governance Systems*. Technical Report, CSIRO Data61.

### Data Sources

11. **Project Catalyst Fund13 Results**: [https://projectcatalyst.io/funds/13](https://projectcatalyst.io/funds/13)
12. **Cardano Stake Distribution Data**: Available through Cardano blockchain explorers
13. **Voting Behavior Analysis**: Proprietary dataset from Catalyst voting records (anonymized)

### Implementation Resources

14. **Technical Report**: *Mathematical Framework for Proportional Fairness in Project Catalyst* - [Link to be provided upon publication]
15. **Simulation Code Repository**: [GitHub repository to be made public upon CIP acceptance]
16. **Catalyst Fund13 Proposal**: [Proportionality in Stake-based Voting](https://projectcatalyst.io/funds/13/cardano-use-cases-concept/proportionality-in-stake-based-voting)

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
