---
CIP: 42069
Title: Network Parameter Adjustment for Staking Competitiveness and Adoption
Category: Ledger
Status: Proposed
Authors:
    - Jonathan Nikkel <nikkelj@gmail.com>
        - dREP ID: drep1yfqkrlpz60efhuhz7atuy60m8ygqtef8ylfw96munn8vxqgj0pq92
        - Bio: https://gov.tools/drep_directory/drep1g9slcgkn72dl9chh2lpxn7eezqz72fe86t3wklyuempszrm80p9
Implementors: []
Discussions:
    - Original PR: https://github.com/cardano-foundation/CIPs/pull/?
Created: 2026-06-07
License: CC-BY-4.0
---

## Abstract

This proposal recommends adjusting two Cardano protocol parameters — the monetary expansion rate (`rho`) and the treasury tax rate (`tau`) — to materially increase staking returns and improve Cardano's competitiveness as a proof-of-stake network. Specifically, it proposes raising `rho` from `0.003` to `0.0042` and reducing `tau` from `0.2` to `0.02`. Together, these changes are projected to raise the annualised staking yield toward approximately 8%, up from the current range of 2–4%, making Cardano staking meaningfully more attractive relative to competing networks and to traditional fixed-income alternatives. This is a pure protocol-parameter update and does not require a hard fork.

## Motivation: Why is this CIP necessary?

### Cardano's Competitive Position is Deteriorating

Cardano is losing ground in the broader proof-of-stake landscape. Delegator yields on Cardano have compressed significantly as the reserve has depleted, and competing networks now routinely offer staking returns in the 5–12% range. For delegators comparing options — whether they are institutional participants, retail users, or developers deciding which chain to build on — yield is one of the most visible and legible signals of network health. A persistently uncompetitive yield drives capital and attention elsewhere.

The community has approximately a two-year window to demonstrably improve Cardano's value proposition before the competitive gap becomes structural. This proposal acts on that window.

### Treasury Accumulation Has Outpaced Deployment

The treasury tax (`tau`) currently stands at 20%, meaning one-fifth of every epoch's reward pot flows into the treasury before stakers see a single lovelace. While a well-funded treasury is important for ecosystem development, the current rate has led to treasury reserves that substantially exceed what can be productively deployed in the near term. Reducing `tau` to 2% redirects the majority of this value back to delegators and stake pool operators (SPOs) who provide security to the network today, while still maintaining a sustainable treasury income stream.

### Reserve Depletion Compounds the Problem

As the reserve depletes epoch by epoch, the absolute ADA available for staking rewards shrinks. Without a compensating adjustment to `rho`, yields will continue to fall. Increasing `rho` from `0.003` to `0.0042` — a 40% increase — partially counteracts reserve depletion by extracting rewards at a somewhat higher rate. This does accelerate the reserve schedule, so the increase is intentionally moderate: large enough to matter for delegator returns, small enough not to materially shorten the protocol's long-term sustainability horizon.

### Staking Yield as an Adoption Signal

New participants entering the Cardano ecosystem — whether through exchanges, DeFi protocols, or direct wallet staking — encounter the displayed APY early in their decision process. An ~8% yield is:

- Credibly high enough to be competitive and to motivate urgency ("why am I not staking?")
- Credibly low enough not to invite the scepticism associated with unsustainable inflationary tokenomics

This is the range where yield functions as a genuine adoption driver rather than either a deterrent or a red flag.

## Specification

### Proposed Parameter Changes

The following two protocol parameters are adjusted:

| Parameter | Current Value | Proposed Value | Change |
|-----------|--------------|----------------|--------|
| `monetaryExpansion` (`rho`) | `0.003` | `0.0042` | +40% |
| `treasuryCut` (`tau`) | `0.2` | `0.02` | −90% |

No other parameters are modified. No changes to the rewards formula, the ledger rules, or the consensus layer are required. Both parameters are adjustable via the standard on-chain governance mechanism introduced by CIP-1694 (Conway governance).

### Reward Formula

The epoch reward pot available for distribution to SPOs and delegators is:

$$R = \bigl(\text{reserve} \times \rho + \text{fees}\bigr) \times (1 - \tau)$$

Under the current parameters:
$$R_{\text{current}} = (\text{reserve} \times 0.003 + \text{fees}) \times 0.80$$

Under the proposed parameters:
$$R_{\text{proposed}} = (\text{reserve} \times 0.0042 + \text{fees}) \times 0.98$$

The combined effect is substantially larger: the 40% increase in reserve extraction is amplified by retaining 98% of the pot rather than 80%, increasing the delegator-visible reward by approximately a factor of 1.7× relative to current levels at the same reserve size.

### Projected Staking Yield

The annualised staking yield for delegators is approximately:

$$\text{APY} \approx \frac{R_{\text{annual}}}{\text{total staked ADA}}$$

where $R_{\text{annual}} = R \times 73$ (73 epochs per year at 5 days per epoch).

Under the proposed parameters, and with plausible current values for the reserve and staked ratio, the projected APY is approximately **8%**. Precise figures will vary with reserve level, staking participation rate, and fee volume at the time of activation; the target APY of ~8% should be validated against current on-chain data prior to final ratification.

### Implementation

Both `monetaryExpansion` and `treasuryCut` are Conway-era updatable protocol parameters. The change is implemented by submitting a `ParameterChange` governance action via the Conway on-chain governance mechanism (CIP-1694). No node software changes are required.

## Rationale: How does this CIP achieve its goals?

### Why reduce `tau` rather than rely on `rho` alone?

`tau` is the more powerful lever for delegator yield. Under current parameters, 20 cents of every reward-eligible ADA goes to the treasury before distribution. Cutting `tau` to 2% returns ~22% more ADA to stakers with no change to the reserve schedule. Raising `rho` alone would require a much larger increase — and therefore faster reserve depletion — to achieve the same yield improvement.

The combination of both adjustments is optimal: `rho` partially offsets reserve depletion pressure while `tau` ensures that what is extracted reaches delegators rather than accumulating in the treasury.

### Why 2% for `tau` rather than 0%?

A non-zero `tau` is desirable. The treasury provides the community with a funding mechanism for development, audits, marketing, and ecosystem grants that does not depend on block reward timing. Zeroing it would risk underfunding the treasury at exactly the moment it may be most needed to fund adoption-driving initiatives. At 2%, the treasury continues to accumulate meaningfully in absolute ADA terms, particularly as transaction volumes grow.

The reduction of tau to 0.02 is a recognition of the AI multiplier. Developers and the treasury require less to make forward progress. We can leverage this gap and feed it back directly as immediate value generation for users on the network.

Should the treasury become depleted, this parameter can be increased again at a later date to refill it. We should be tuning it over time to adapt the network to the present environment, not leaving it fixed forever.

### Why 0.0042 for `rho`?

The proposed value represents a moderate increase designed to:

1. Partially compensate for the lower treasury inflow from the `tau` reduction, maintaining some buffer for the protocol's long-term reserve schedule.
2. Directly increase the reserve-derived component of the reward pot.
3. Remain conservative enough that the long-term reserve runway is not materially compromised — the additional reserve extraction relative to the current rate is incremental.

Rationale to the contrary is that increasing staking rewards to discourage participation in defi. However, this contrarian rationale fails to realize that participation is required in the first place. Cardano is, above all, a store of value, and that store of value must look attractive to users for even entry level participation to occur. Many defi opportunities have produced returns far in excess of 8% APY as well.

### Effect on the Treasury

Reducing `tau` from 0.2 to 0.02 will significantly reduce treasury inflows in the near term. This is an intentional trade-off: the community currently holds substantial treasury reserves, and the marginal value of additional accumulation is lower than the marginal value of returning that ADA to the delegators and SPOs who secure the network. As network transaction volumes grow (driven in part by the improved adoption this proposal aims to catalyse), fee-based treasury income will become a more important contributor independently of `tau`.

### Urgency

Cardano's competitive window is not unlimited. Other proof-of-stake networks continue to attract users, developers, and liquidity. Every epoch that passes with below-competitive yields is an epoch in which potential delegators choose alternatives, potential builders assess other ecosystems, and current participants consider exits. This proposal is intentionally urgent: it should be ratified and activated promptly, not deferred through extended deliberation.

## Path to Active

### Acceptance Criteria

- [ ] A governance action of type `ParameterChange` is submitted on-chain setting `monetaryExpansion = 0.0042` and `treasuryCut = 0.02`.
- [ ] The action achieves the required Constitutional Committee approval and DRep stake-weighted majority as specified by the Conway governance rules (CIP-1694).
- [ ] The parameter changes take effect at an epoch boundary following ratification.

### Implementation Plan

1. Validate projected APY figures against current on-chain reserve and staking data.
2. Engage Constitutional Committee and DRep community to build consensus.
3. Draft and submit the on-chain `ParameterChange` governance action.
4. Monitor yield and treasury metrics post-activation and assess whether further adjustment is warranted.

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).