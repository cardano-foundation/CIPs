---
CIP: 23
Title: Fair Min Fees
Authors:
  - Shawn McMurdo <shawn_mcmurdo@yahoo.com>
  - Ryan Wiley <rian222@gmail.com>
Category: Ledger
Status: Proposed
Created: 2021-02-04
Discussions:
 - https://forum.cardano.org/t/fair-min-fees-cip/47534
 - https://github.com/cardano-foundation/CIPs/pull/66
Implementors: []
License: CC-BY-4.0
---

## Abstract

This CIP introduces a new protocol parameter, `minPoolMargin`, which specifies a lower bound on the variable fee (margin) a stake pool may set. The parameter is introduced initially set to `0` to avoid disrupting existing pool certificates.  This proposal does not change or reduce the existing minimum fixed pool fee (`minPoolCost`).

## Motivation: Why is this CIP necessary?

The current minimum fixed pool fee places a large and unfair burden on delegators to pools with smaller amounts of stake.
This incentivizes people to delegate to pools with higher stake causing centralization and creating an unequal playing field for stake pool operators.

Using a minimum variable pool fee reduces the imbalance between stake pools with less or more stake to a more reasonable range that allows for more fair competition between stake pools and more fair rewards for delegators to stake pools with less stake.

This creates a more fair marketplace for all stake pool operators and increases decentralization, which is a goal of Cardano.

## Specification

This CIP introduces a new protocol parameter, `minPoolMargin`, which represents the
minimum variable fee (margin) that a stake pool can set. This parameter is
distinct from the existing `minPoolCost`, which represents the minimum fixed
fee a pool can set. Both limits are enforced independently by the ledger.

- `minPoolMargin` defines the lower bound for the pool margin (variable fee), i.e.,
  the minimum allowable percentage of rewards a pool can take. Pool
  registration and update certificates MUST have `margin >= minPoolMargin`.
- `minPoolCost` retains its current meaning and enforcement as the minimum
  fixed fee a pool can set.

This CIP does not prescribe specific values for either parameter. Concrete
values for `minPoolMargin` and `minPoolCost` are to be chosen and enacted through
the standard protocol parameter update process.

### Backward Compatibility

To maintain compatibility for existing pool certificates whose current margin is below the new `minPoolMargin`, the ledger's rewards calculation should treat the protocol parameter `minPoolMargin` as the effective margin for those pools. In other words, if a pool's margin is less than `minPoolMargin`, the protocol-level `minPoolMargin` overrides the pool's registered `margin` during reward calculation. This minimizes disruption and lets legacy pool certificates remain valid while ensuring the ledger enforces the new minimum fee during reward distribution.

It is also recommended to introducce the hard-fork with `minPoolMargin` initially set to `0`. Doing so minimizes migration friction for stake pool operators and gives governance time to raise the parameter to its target value through the normal paramater change governance action process.

Should this clamping approach prove infeasible, pool certificates with a margin lower than `minPoolMargin` would need to be re-registered with compliant values, but the goal is to avoid disruption as much as possible.

## Rationale: How does this CIP achieve its goals?

The PHP code in minfees.php in the pull request allows exploration of the effects of choosing different values for the minimum fixed and variable fees.
Running minfees without any arguments gives the usage message as below.

```
php minfees.php

Usage: php minfees.php <min_fixed_fee> <min_rate_fee> <pledge>
  min_fixed_fee:  Minimum fixed fee in ADA.
               An integer greater than or equal to 0.
  min_rate_fee: Minimum rate fee in decimal. Example: 1.5% = .015
                    A real number greater than or equal to 0.
  pledge: Optional pledge amount in ADA. Defaults to 100000
                    A real number greater than or equal to 0.
```

Running minfees with the proposed values gives the following comparison of current and proposed pool operator and staker results at various pool stake levels.

```
php minfees.php 50 .015 100000

Reserve: 13b
Total stake: 32b
Tx fees: 0
Rewards available in epoch: 31.2m
Pool saturation: 64m
Pledge: 100k
Staker Delegation: 100k
Current Fixed Fee: 340
Current Rate: 0%
New Fixed Fee: 50
New Rate: 1.5%

                +---------- Current ----------+ +-------- Proposed ---------+
Pool    Total   Pool    Staker  Staker  Current Pool    Staker  Staker  New
Stake   Rewards Cur Fee Cur Fee Cur Rew Fee %   New Fee New Fee New Rew Fee %
2m      1501    340     17      58.1    22.7%   71.8    3.6     71.5    4.8%
5m      3752    340     6.8     68.2    9.1%    105.5   2.1     72.9    2.8%
10m     7503    340     3.4     71.6    4.5%    161.8   1.6     73.4    2.2%
20m     15007   340     1.7     73.3    2.3%    274.4   1.4     73.7    1.8%
30m     22511   340     1.1     73.9    1.5%    386.9   1.3     73.7    1.7%
64m     48023   340     0.5     74.5    0.7%    769.6   1.2     73.8    1.6%
```

Definitions:
Pool Stake - Total stake delegated to pool.
Total Rewards - Total rewards generated by the pool in one epoch.
Pool Cur Fee - The total amount of fees taken by the pool with current parameters.
Staker Cur Fee - The amount of fees paid by a staker who delegates 100k ADA  with current parameters.
Staker Cur Rew - The amount of rewards received by a staker who delegates 100k ADA  with current parameters.
Current Fee % - The percentage of rewards taken by the pool as fees  with current parameters.
Pool New Fee - The total amount of fees taken by the pool with proposed parameters.
Staker New Fee - The amount of fees paid by a staker who delegates 100k ADA with proposed parameters.
Staker New Rew - The amount of rewards received by a staker who delegates 100k ADA with proposed parameters.
New Fee % - The percentage of rewards taken by the pool as fees with proposed parameters.
Note: All amounts other than %s are in ADA.

The table above shows that currently a delegator staking 100k ADA to a stake pool with 2m ADA total delegation to the pool is paying an exorbitant 22.7% in fees while the same delegator staking with a fully saturated pool would only pay 0.7% in fees.
This is a substantial and unfair advantage that large pools have in the stake pool marketplace.
This is a strong incentive to centralize stake to fewer larger pools which reduces the resiliency of the network.

The proposed minimum fees bring this imbalance into a more reasonable range of 1.6% to 4.8%.
It is much more likely that a small stake pool with other advantages or selling points would be able to convince a delegator to accept about 2 less ADA in rewards per epoch for their 100k delegation than about 17 ADA as in the current case.
This is particularly true as the price of ADA increases.
At current price of $0.90 USD, a delegator staking 100k ADA is giving up over $1000 USD per year by delegating to a small pool!
This does not even include the amount lost by comounding rewards being staked over the year.

16.5 ADA/epoch * 73 epochs/year =  1204.5 ADA/year
1204.5 ADA/year * $0.90 USD/ADA = $1084.05 USD/year

With proposed parameters the same delegator would only be giving up about $150 USD per year to support a small pool.

2.3 ADA/epoch * 73 epochs/year =  167.9 ADA/year
167.9 ADA/year * $0.90 USD/ADA = $151.11 USD/year

The calculations below show that given the price increase in ADA compared to when the protocol parameters were first set, we can maintain viable funding for stake pool operators with the proposed parameter changes.

Annual pool operator funding given initial parameters:
340 ADA/epoch * $0.08 USD/ADA = $27.20 USD/epoch
$27.20 USD/epoch * 73 epochs/year = $1985.60 USD/year

Annual pool operator funding given proposed parameters for stake pool with 2 million ADA delegation:
71.8 ADA/epoch * $0.90 USD/ADA = $64.62 USD/epoch
$64.62 USD/epoch * 73 epochs/year = $4717.26 USD/year

Annual pool operator funding given proposed parameters for fully saturated stake pool:
769.6 ADA/epoch * $0.90 USD/ADA = $692.64 USD/epoch
$692.64 USD/epoch * 73 epochs/year = $50,562.72 USD/year

In summary, the proposed parameter changes would create a more fair marketplace for stake pools, provide more fair rewards for delegators to smaller pools and would lower incentives for centralization providing a more resilient network.

### Test Cases

See the minfees.php code to test different potential values of the parameters.

## Path to Active

### Acceptance Criteria

- Consensus on initial parameter value – An initial value for the new protocol parameter `minPoolMargin` must be agreed upon before hard-fork combinator (HFC) activation. The choice should consider operational viability, empirical analyses, and community feedback.
- Endorsement by Technical Bodies – The Cardano Parameter-Change Proposals (PCP) Committee and the Intersect Technical Steering Committee (TSC) should both recommend the proposal as technically sound and aligned with the protocol’s long-term roadmap.
- Stakeholder Concurrence – A majority of stake pool operators (SPOs), ecosystem tooling maintainers, dReps, and other infrastructure providers must signal readiness to upgrade.
- Governance Ratification – The on-chain Hard-Fork Governance Action must pass the requisite dRep and Constitutional Committee thresholds, establishing legal-constitutional legitimacy and stakeholder support for the change.

### Implementation Plan

- Community Deliberation (Preparation Phase)
  - Publish the finalized CIP revision and present it to the PCP committee, TSC, CIP Editors, and wider community channels (Discord, X, Cardano Forum, etc.).
  - Collect structured feedback, particularly on candidate values for the new parameter values and iterate until broad technical consensus emerges.
- Specification & Code Integration (Development Phase)
  - Once initial parameter values are determined, integrate the new rewards calculation logic and governance features for the new parameter into cardano-node and related libraries (ledger, CLI, wallet APIs).
  - Determine the best method to deal with existing pool registration certificates that currently have a variable fee lower than what the new `minPoolMargin` parameter allows.
  - Submit pull requests to the canonical repositories; obtain code reviews from IOG, CF, and community contributors.
  - Release a new protocol version that includes the changes made in this CIP.
  - Use a dedicated pre-production testnet that mirrors main-net parameters but enforces the new changes, allowing SPOs and exchanges to test end-to-end flows.
- Readiness Sign-off (Testing Phase)
  - Require at least two weeks of uninterrupted testnet stability plus green results from regression and property-based tests.
  - Monitor ecosystem dApps and tooling to confirm that major node implementations, explorers, wallets, and exchange integrations support the new rule set.
- On-chain Governance (Ratification Phase)
  - File the Hard-Fork Governance Action on-chain with the agreed initial parameter value tagged for the next hard fork event.
  - Modify the existing Cardano Constitution to include definitions and guardrails for the new protocol parameters and have it ratified by the tripartite government of Cardano.
  - Mobilize dRep outreach to ensure quorum and super-majority passage; concurrently, the Constitutional Committee validates procedural compliance.
- Hard-Fork Activation (Deployment Phase)
  - Upon successful vote, the hard fork event is automatically triggered upon epoch turnover.
  - Monitor main-net metrics during the changeover epoch; provide real-time support for any late-upgrading SPOs.

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode)