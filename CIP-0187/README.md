---
CIP: 187
Title: Utilization-Scaled Pledge Bonus
Category: Ledger
Status: Proposed
Authors:
    - John Shearing <johnshearing@gmail.com>
Implementors: []
Discussions:
    - Original PR: https://github.com/cardano-foundation/CIPs/pull/1193
    - Forum: https://forum.cardano.org/t/cip-utilization-scaled-pledge-bonus-the-multi-pool-buster/154614
Created: 2026-05-15
License: CC-BY-4.0
---

## Abstract

Cardano's reward formula contains a potential weakness in the pledge bonus term `A`: under the current specification, `A = r · a₀ · P / (1 + a₀)` depends on the operator's pledge `P` but not on the pool's total stake `S`. As delegation arrives at a high-pledge pool, the per-delegator share `(A − F)/S` strictly falls, so adding stake dilutes everyone already there. The very behavior the protocol's Nash equilibrium assumes — rational delegators concentrating stake into high-pledge, well-operated pools — is punished by the formula itself.

This CIP proposes a parameter-free reshape of the existing pledge bonus by multiplying it by pool utilization `u = min(S, S_sat) / S_sat`. The new bonus is `A = r · a₀ · P · min(S, S_sat) / (S_sat · (1 + a₀))`. A saturated pool earns exactly today's pledge bonus; a half-utilized pool earns half; an empty pledged pool earns nothing from pledge until delegators arrive. No new parameter is introduced — `a₀` retains its name, governance dial, and Sybil-resistance role. The change removes the dilution regime entirely, strengthens Sybil resistance at the formula level, makes "fill pools to saturation" self-enforcing at every utilization level, and gives small honest operators a viable on-ramp through delegation rather than personal capital.

## Motivation: Why is this CIP necessary?

The standard Cardano delegator return formula (Reward Sharing Scheme) reduces to:

```
ROA = (1 − m) · [ r/(1 + a₀) + (A − F)/S ] · 73 · 100%
where  A = r · a₀ · P / (1 + a₀)
```

The sign of `(A − F)` decides whether per-delegator ROA rises or falls as `S` grows:

| Regime  | `dROA/dS` | Pool type                                | Implication for adding delegation         |
| ------- | --------- | ---------------------------------------- | ----------------------------------------- |
| `A > F` | negative  | high-pledge pool (the rational target)   | adding stake dilutes existing delegators  |
| `A < F` | positive  | low-pledge pool                          | adding stake helps via fee amortization   |
| `A = F` | zero      | edge case                                | ROA flat                                  |

Concretely, a 50 M-pledge pool with `F = 340`, `r = 0.000400`, `S_sat = 75 M` shows `(A − F)/S ≈ 8.55 × 10⁻⁵` at `S = 50 M` and `(A − F)/S ≈ 5.70 × 10⁻⁵` at `S = 75 M` — roughly a **0.21% absolute ROA loss** absorbed by delegators for the act of arriving at the pool.

This defect produces five interacting problems:

1. **Rational delegation is punished.** The protocol's equilibrium analysis assumes delegators rotate toward high-pledge, well-operated pools. The reward formula penalizes that rotation in the regime delegators are supposed to prefer.
2. **Cooperative delegation has no protocol-level instrument.** Coordinators that perform the rational-delegator function for many small holders (e.g., [Pool Ranger](https://github.com/johnshearing/pool_ranger) — a cooperative-delegation platform that pools members' staking credentials and routes delegation toward the highest-yielding pools each epoch) suffer the dilution most acutely. Bringing 25 M ADA into a pool to gain bargaining leverage simultaneously erodes the ROA of the members on whose behalf the coordinator acts. Today's workaround — informal off-chain negotiation between large delegators and SPOs — is opaque and unverifiable.
3. **Small honest SPOs cannot compete on the pledge-bonus axis.** A small operator with modest pledge is structurally disadvantaged regardless of operational quality, because the bonus is tied to capital declared rather than capital actually attracted.
4. **The Sybil deterrent leans entirely on the delegator-preference channel.** Splitting `X` ADA into `N` pools leaves the total pledge bonus unchanged under the current formula; only delegator avoidance makes the split unprofitable. The formula itself does no Sybil work beyond setting `A`'s magnitude.
5. **Empty pledged pools earn the same per-pledge bonus as filled pools.** The protocol pays for an entitlement that has not yet produced the equilibrium it is meant to incentivize.

The obvious direct fix — lowering `a₀` — is unacceptable because `a₀` carries the Sybil-resistance load. Removing or weakening it reopens the stake-splitting channel. Any acceptable fix must preserve `a₀`'s deterrent role while removing the dilution.

A fuller treatment — the derivation of the proposed formula, numerical worked examples, and game-theoretic analysis of `a₀` under both regimes — is in [Appendix A](#appendix-a-detailed-derivation-and-worked-examples) below. An [interactive simulator](https://johnshearing.github.io/pool_ranger/CIP_UTILIZATION_SCALED_PLEDGE_BONUS.html) with adjustable parameters and four guided tutorials accompanies the proposal.

## Specification

### Notation

All symbols carry their standard Ledger Specification / Reward Sharing Scheme meaning:

- `r` — per-epoch reward rate (fraction of total ADA supply distributed per epoch). Drifts down slowly as the reserve depletes; currently ≈ 0.000400.
- `a₀` — pledge influence factor (existing protocol parameter, currently `0.3`, governance-tunable).
- `k` — target stake-pool count (currently `500`).
- `P` — operator pledge (ADA, declared on-chain).
- `S` — total live stake delegated to the pool, including pledge.
- `S_sat` — saturation cap, defined as `(active network stake) / k`. Currently ≈ 65–75 M ADA.
- `u` — pool utilization, defined as `min(S, S_sat) / S_sat`. `u ∈ [0, 1]`.
- `F` — fixed fee in ADA per epoch (flat overhead the SPO takes off the top of gross rewards before margin). SPO-set, subject to protocol minimum.
- `m` — margin (SPO's percentage cut of post-fee rewards before the remainder is split among delegators by stake fraction). SPO-set, 0–100%.
- `p` — performance factor (actual blocks minted divided by blocks the pool's stake fraction would predict, capped at 1.0).
- `A` — pledge bonus per epoch (ADA/epoch advantage a pledged pool earns over an otherwise-identical zero-pledge pool). Defined in `Current pledge bonus` and `Proposed pledge bonus` below.

### Current pledge bonus

The pledge bonus term `A` in the gross-rewards calculation is currently:

```
A_current = r · a₀ · P / (1 + a₀)
```

### Proposed pledge bonus

Replace `A` with:

```
A_new = r · a₀ · P · min(S, S_sat) / (S_sat · (1 + a₀))
      = A_current · u
```

Equivalent restatement, valid for all `S ≥ 0`:

```
A_new = A_current                       when S ≥ S_sat   (u capped at 1)
A_new = A_current · (S / S_sat)         when S <  S_sat
```

The `min(S, S_sat)` cap preserves the existing protocol property that gross rewards do not grow beyond saturation.

No other term in the reward formula is altered. Margin, fixed fee, performance factor, and the saturation cap itself are unchanged.

### Optional governance-controlled blend (phased adoption)

To enable gradual phase-in, governance MAY introduce a blending coefficient `b ∈ [0, 1]` such that:

```
A_blend = A_current · (1 − b + b · u)
```

`b = 0` reproduces today's behavior exactly. `b = 1` produces the full proposal as specified above. Intermediate values are valid. The blend coefficient, if adopted, is a new governance-settable protocol parameter; if `b` is not adopted, the change is a one-step replacement of `A_current` with `A_new` at a hard-fork boundary.

The body of this CIP analyzes the limit case `b = 1`. Implementors MAY choose to introduce the parameter or to switch directly; this CIP does not mandate either path.

### On-chain data structures

This proposal introduces **no new on-chain data, no new transaction types, no new certificates, and no new ledger state**. `S`, `P`, and `S_sat` are already snapshotted per epoch as part of the existing reward calculation pipeline. No CDDL schema changes are required. The Specification change is local to the formula used during reward calculation at the epoch boundary.

### Versioning

This proposal is a single, atomic change to the reward calculation, taking effect at the hard-fork combinator event that activates it. The protocol parameter `a₀` continues to be versioned by the existing governance mechanism. If the optional blending coefficient `b` is adopted, it is versioned identically to `a₀`. No additional versioning scheme is introduced by this CIP.

## Rationale: How does this CIP achieve its goals?

### Why utilization scaling removes dilution

Under the proposed formula, `A_new / S = r · a₀ · P / (S_sat · (1 + a₀))` — a quantity independent of `S`. The per-ADA share of the pledge bonus is fixed per unit pledge. The derivative of `(A_new − F)/S` with respect to `S` is `+F/S²`, strictly positive everywhere. Adding delegation to any pool monotonically increases per-delegator ROA via fixed-fee amortization, with no offsetting pledge-bonus dilution. The high-pledge dilution regime that exists today ceases to be a regime.

The derivative with respect to `P` is similarly clean: `d/dP [(A_new − F)/S] = r · a₀ / (S_sat · (1 + a₀))`, strictly positive and constant in `P`. Every pledge increase visibly lifts every delegator's ROA by the same amount per unit pledge added.

### Why `a₀` is preserved

`a₀` is Cardano's primary defense against Sybil-style stake splitting. A whale with `X` ADA splitting into `N` pools currently earns `r · a₀ · (X/N) / (1 + a₀)` per pool, summing to `r · a₀ · X / (1 + a₀)` across all `N` — unchanged from the unsplit case. Sybil deterrence today is paid for entirely by delegator preference: rational delegators read the small per-pool `A` and avoid the split pools.

Under this proposal, splitting reduces total pledge bonus across the `N` pools by a factor of `N`, because each pool's bonus now multiplies by its own (necessarily small) utilization. The delegator-preference channel continues to operate, reinforced by formula-level penalties for splitting. The Sybil deterrent strengthens; it is not weakened.

### Why utilization, not some other scaling

Three properties recommend `u = min(S, S_sat) / S_sat` over alternatives:

1. **Boundary continuity.** At `u = 1` (saturated pool) the new formula equals the old. SPOs already attracting saturation-level delegation see no change. The equilibrium point the current protocol targets is the same equilibrium point the new protocol targets.
2. **Use of an already-tracked quantity.** `S` and `S_sat` are computed every epoch; no new on-chain state is required.
3. **Linear, monotone, parameter-free.** No new dial, no piecewise behavior, no opaque function. The formula is one multiplication.

Alternative shapings (e.g., `sqrt(u)`, sigmoidal scaling, treasury-funded "trough" subsidies) were considered and rejected: they either introduce new parameters, change the saturation case, or shift cost to the treasury rather than addressing the structural cause.

### Backward-compatibility impact

Off-chain consumers of the reward formula — wallets that show projected ROA, pool-ranking sites, delegation tooling — will need to update their formulas to incorporate the utilization factor. The change is mechanical and well-defined; no on-chain artifact changes shape. Historical rewards and pre-fork transactions are unaffected.

For SPOs and delegators, the saturation case is unchanged. Below-saturation pools earn less pledge bonus than today. SPOs whose pools are currently below saturation see reduced revenue until delegation arrives. This is the intended redirection of incentive — the protocol stops paying pledge bonus to pledged pools that have not yet earned delegator interest.

Wallet operators SHOULD update displayed ROA projections to use the new formula starting at the hard-fork epoch. Block-producing nodes MUST use the new formula; consensus depends on it.

### Treasury and emission impact

Below-saturation pools emit less pledge bonus than today, so total emission shrinks slightly when the network operates below average saturation. The unused share remains in the reserve and is distributed in later epochs — consistent with how the reserve depletes today.

Governance retains an obvious lever: a one-time upward recalibration of `a₀` so that average-utilization total emission matches today's. The recalibration is a single governance vote, computable from current chain data. Alternatively, governance may accept slower reserve depletion as a benign side effect of the change. This CIP does not mandate either path.

### Effect on multi-pool operators (MPO)

A multi-pool operator (MPO) is a single entity running many stake pools simultaneously, capturing more block production, fixed-fee revenue, and on-chain voting weight than they would as a single operator. MPOs undermine Cardano's intended convergence on `k` distinct operators and weaken governance decentralization, where voting power is supposed to be tied to genuinely independent voices.

Today's defense against MPO behavior is purely behavioural — `a₀ = 0.3` makes the per-pool pledge bonus small for split pools, and rational delegators are expected to avoid them. Crucially, **today's formula imposes no cost on splitting itself**. A whale's total pledge bonus is unchanged regardless of how many pools they split into:

| Strategy (50 M ADA pledge, `r = 0.000548`, `a₀ = 0.3`) | Total pledge bonus today |
| ---- | ---- |
| 50 M in 1 pool                  | ≈ 6,323 ADA/epoch (≈ 462 K/yr) |
| 50 M across 10 pools (5 M each) | ≈ 6,323 ADA/epoch (≈ 462 K/yr) |
| 50 M across 100 pools (0.5 M each) | ≈ 6,323 ADA/epoch (≈ 462 K/yr) |

The total is identical. Splitting pays nothing at the formula level. If the operator can attract even a small fraction of delegators per pool — or self-delegate, or buy delegation through marketing — the strategy works.

Under the proposal, each split pool's bonus multiplies by its own utilization. A self-funded MPO's split pools each have low utilization (each can only be filled by the operator's `X/N` share, tiny relative to `S_sat`), so total bonus scales with `1/N`:

| Strategy (same parameters, self-funded splits, `S_sat = 75 M`) | Proposed total pledge bonus |
| ---- | ---- |
| Unsplit (N = 1)         | ≈ 4,218 ADA/epoch (≈ 308 K/yr) |
| 2 self-funded pools     | ≈ 2,109 ADA/epoch (≈ 154 K/yr) |
| 10 self-funded pools    | ≈ &nbsp;&nbsp;422 ADA/epoch (≈ &nbsp;31 K/yr) |
| 100 self-funded pools   | ≈ &nbsp;&nbsp;&nbsp;42 ADA/epoch (≈ &nbsp;&nbsp;3 K/yr) |

A 10-way self-funded split costs roughly **277 K ADA/year in forgone bonus** versus staying in one pool. The cost grows linearly with `N`.

The MPO could in principle recover this by attracting external delegators to fill every split pool to saturation. But that requires `N` times the delegator base of a single legitimate operator — which, by assumption, an MPO splitting for advantage does not have. The formula-level deterrent compounds with the existing delegator-preference channel: small per-pool pledge → small per-pool bonus → few delegators → low utilization → even smaller per-pool bonus.

**Two distinct deterrents now stack:** today's behavioural defense (delegator preference, mediated by `a₀`) continues to operate unchanged, and the proposal adds a formula-level cost proportional to the number of pools an operator splits into. `a₀` itself is not touched — Sybil resistance is preserved exactly as it stands.

### Stakeholder summary

The proposal's net effect across stakeholder classes:

- **SPOs at saturation:** no change. Same pledge bonus, same margin, same fixed fee, same income.
- **SPOs below saturation:** reduced bonus today, with a clear recovery path: court delegators. Pledge becomes a partnership claim, redeemed by attracting delegation rather than declared in isolation.
- **Small honest SPOs:** competitive viability via delegation rather than personal capital. A small-pledge pool that fills to saturation earns the same per-ADA pledge bonus as a whale-pledge pool at saturation.
- **Every delegator:** the central win. Adding delegation to any pool monotonically increases per-delegator ROA. The dilution regime is structurally removed. Pool selection simplifies to "find pools with high `P · u / S` and low `F`."
- **Cooperatives (Pool Ranger and others):** structural bargaining power as a side effect of being any large delegator. No protocol-level recognition, no registry, no stake-credential consolidation required. Withdrawal becomes a publicly observable mathematical event, giving SPOs continuous incentive to retain delegators, not just attract them.
- **Decentralization:** MPO behavior is taxed at the formula level proportional to `N`. Combined with the unchanged `a₀`, Cardano's intended `k`-pool diversity becomes self-enforcing rather than aspirational.
- **Treasury:** governance-tunable. Either reserve depletes slightly slower, or a one-time `a₀` recalibration preserves today's emission exactly. Single governance vote either way.

### Comparison to other proposals

| Proposal                              | Mechanism                                            | Resolves dilution? |
| ------------------------------------- | ---------------------------------------------------- | ------------------ |
| Lower `a₀` directly                   | Weaken pledge bonus everywhere                       | Yes, but reopens Sybil channel |
| [CIP-0050](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0050) leverage cap | Limit delegation/pledge ratio per pool               | No — addresses SPO leverage, not the dilution mechanism |
| Treasury "trough" subsidy             | Pay delegators to fill underused pools               | Partial; treasury-funded, hard to scale |
| **Utilization-scaled pledge bonus**   | **Multiply `A` by `u`. Existing `a₀` reused.**       | **Yes — directly, treasury-tunable, Sybil-strengthening, helps every delegator** |

### Risks considered

| Risk | Response |
| ---- | -------- |
| Cold-start harder for newly-launched pools | The proposal itself creates the cure: a low-utilization pool offers a large `dROA/dS` to arriving delegators, which is precisely the bargaining surface coordinators exploit. Cold start becomes a coordinated act. Optional treasury launch grants may be added separately if desired. |
| Total emission shrinks below average saturation | One-time `a₀` recalibration restores it. Computable from current chain data. |
| Established high-pledge SPOs with unfilled pools lose revenue | Intended redirection. Saturated pools are unaffected. Recovery path: attract delegation. |
| Whales "self-delegate" to lift utilization | Whale's parked ADA earns only as a delegator (after `F`, margin, pro-rata split). No arbitrage advantage over delegating to any equivalent pool. |
| Sybil whales attract delegators to recoup split bonus | Each of `N` split pools must individually reach competitive utilization. The split whale would need `N` times the delegator base, which by assumption they do not have. |

A fuller game-theoretic analysis, including numerical anchors and edge cases, is in [Appendix A](#appendix-a-detailed-derivation-and-worked-examples). Readers can also explore both formulas interactively, with adjustable parameters and four guided tutorials, at the [interactive simulator](https://johnshearing.github.io/pool_ranger/CIP_UTILIZATION_SCALED_PLEDGE_BONUS.html).

## Path to Active

### Acceptance Criteria

- [ ] A formal write-up of the reward-calculation change is reviewed by the Cardano ledger team and the CIP editors, with no unaddressed objections.
- [ ] A reference implementation is available in a Cardano node fork, with test vectors covering: (a) `S = 0`, (b) `S = P`, (c) `S = S_sat`, (d) `S > S_sat`, (e) the optional blend at `b ∈ {0, 0.5, 1}`.
- [ ] Off-chain tooling impact (wallet ROA projections, pool-ranking sites, delegation tools) is enumerated and documented, with reference updates available for at least the major Cardano wallets and explorers.
- [ ] On-chain governance vote (per CIP-1694) passes the activation of the new formula at a hard-fork combinator boundary.
- [ ] Implementation is present within block-producing nodes used by **80% or more of active stake** at the hard-fork activation epoch.

### Implementation Plan

This proposal **requires a hard fork** because it changes the reward calculation used by every block-producing node. Implementation steps:

1. **Reference implementation.** Modify the reward calculation in a Cardano node fork (Haskell, `cardano-ledger`) to apply the utilization factor. Patch is localized to the pledge bonus term in the gross-rewards computation. Approximate effort: a single multiplication plus property-based test coverage.
2. **Test vectors.** Publish a set of input/output vectors covering the boundary cases listed in Acceptance Criteria, computable by any independent implementation.
3. **Governance proposal.** Submit a CIP-1694 governance action to activate the formula change at the next hard-fork combinator event. The action SHOULD specify whether the optional blending coefficient `b` is adopted; if so, its initial value.
4. **Wallet and tooling notice.** Coordinate with major wallet teams (Eternl, Lace, Nami, Yoroi, Flint) and explorers (Cexplorer, pool.pm, ADAPools, PoolTool) to update displayed ROA projections at the hard-fork epoch.
5. **Optional treasury recalibration.** If governance wishes to preserve average-utilization emission at today's level, a follow-up `a₀` recalibration vote MAY be submitted, with the target `a₀` computed from chain data immediately prior to the hard fork.
6. **Activation.** Hard-fork combinator activates the new formula at the chosen epoch.

Implementors have not yet committed; the `Implementors:` field is empty pending review by the ledger team.

## References

- [CIP-1694](https://github.com/cardano-foundation/CIPs/tree/master/CIP-1694) — On-chain governance actions (the mechanism this CIP would be activated through).
- [CIP-0050](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0050) — Pool leverage cap proposal (related; addresses a different symptom).
- Brünjes, Kiayias, Koutsoupias, Stouka — [*Reward Sharing Schemes for Stake Pools*](https://eprint.iacr.org/2018/1145) (the original RSS paper formalizing the formula this CIP modifies).
- [Interactive simulator](https://johnshearing.github.io/pool_ranger/CIP_UTILIZATION_SCALED_PLEDGE_BONUS.html) — adjustable parameters with four guided tutorials: (1) the math explainer, (2) who benefits and by how much, (3) the multi-pool operator problem, (4) free-form exploration. Source repository: [johnshearing/pool_ranger](https://github.com/johnshearing/pool_ranger).

## Acknowledgements

This proposal was drafted with assistance from Claude (Anthropic). The mathematical derivation, the constraint that `a₀` must be preserved, the proposed `u` scaling, and the analysis of cooperative-delegation effects emerged from extended dialog between the author and the model. All claims have been independently re-derived by the author. Any errors are the author's.

## Appendix A: Detailed Derivation and Worked Examples

This appendix provides the full derivation, numerical worked examples, expanded stakeholder analysis, and extended risk discussion that underlies the more compact treatment in the body. Readers can follow the body of this CIP without it; reviewers who want to verify the math, work through the Sybil deterrent quantitatively, or examine the per-stakeholder mechanics in detail will find that material here.

### A.1 The problem in precise terms

The standard Cardano delegator ROA formula is:

```
ROA = (1 − m) · [ r/(1+a₀) + (A − F)/S ] · 73 · 100%
where  A = r · a₀ · P / (1+a₀)
```

Under the current formula, `A` depends on `P` but not on `S`. This is the structural defect. Per-delegator ROA depends on `(A − F)/S`, and when `A` is fixed while `S` grows, that ratio shrinks.

The sign of `(A − F)` decides whether per-delegator ROA *rises* or *falls* as total pool stake `S` grows:

| Regime | `dROA/dS` | Pool type | Implication for adding delegation |
|---|---|---|---|
| `A > F` | negative | high-pledge pool (the kind a rational delegator must pick) | adding stake dilutes existing delegators |
| `A < F` | positive | low-pledge pool | adding stake helps via fixed-fee amortization |
| `A = F` | zero | edge case | ROA flat |

Quantitative anchor: take a 50 M-pledge pool with `F = 340`, `r = 0.000400`, `m = 1%`, `S_sat = 75 M`. With no external delegation, `S = 50 M` and `(A − F)/S ≈ 8.55 × 10⁻⁵`. When 25 M of delegation arrives and saturates the pool, `S = 75 M` and `(A − F)/S ≈ 5.70 × 10⁻⁵`. Roughly a **0.21% absolute ROA loss** for the delegators in the pool, paid for by their own arrival.

The deeper issue: the reward formula's pledge bonus `A` does not scale with the pool's stake `S`. Under the current formula, `A` is set by `P` alone — what the SPO commits — and is the same whether the pool has 1 ADA of delegation or 25 million ADA of delegation. Delegators thus split a fixed bonus pot. The more delegators arrive, the smaller each share.

This is the root cause behind every observed pathology of the current incentive: dilution, the structural conflict between concentration-for-leverage and concentration-for-ROA, the inability of cooperators to negotiate, and the protocol's silence toward "rational delegator" behavior. Fix `A`'s independence from `S` and every symptom resolves at once.

### A.2 Why `a₀` must be preserved

`a₀` is Cardano's primary defense against Sybil-style stake splitting — the scenario in which a single ADA whale creates many small pools to gain disproportionate block production while appearing as many independent operators. The mechanism works through delegator preference, not direct restriction:

- A whale with `X` ADA who splits into `N` pools earns `r · a₀ · (X/N) / (1+a₀)` of pledge bonus per pool — small per pool, total unchanged across all `N` pools.
- Rational delegators read the small `A` on each fake pool, see the unattractive ROA the small pledge bonus produces, and avoid those pools in favor of pools with concentrated pledge.
- Without delegators, the whale's `N`-pool split nets less revenue than concentrating in one pool (each split pool's fixed fee is unearned, margin revenue collapses, saturation budgets go unused). The strategy fails in expectation.

Lowering or removing `a₀` would solve the dilution problem but reopen the Sybil channel. Any acceptable solution must leave the Sybil deterrent intact.

This proposal preserves `a₀` as a parameter — same name, same governance dial. It only changes what `a₀` multiplies. The Sybil deterrent strengthens under the proposal: splitting a whale's pledge across `N` pools now reduces the *total* pledge bonus across those pools by a factor of `N`, rather than leaving it unchanged. The delegator-preference channel that does the Sybil work today continues to do it, with mathematical reinforcement.

### A.3 Why utilization scaling fixes the dilution

Under the proposed formula, `A_new/S = r · a₀ · P / (S_sat · (1+a₀))` — a quantity independent of `S`. The per-ADA pledge bonus share is fixed per unit pledge, regardless of how many delegators arrive.

The per-delegator term in the ROA formula becomes:

```
(A_new − F)/S = A_new/S − F/S
              = r · a₀ · P / (S_sat · (1+a₀))  −  F/S
```

Its derivative with respect to `S` (adding delegation, with `P` fixed):

```
d/dS [(A_new − F)/S] = 0 − (−F/S²) = +F/S²    > 0
```

Strictly positive. Adding delegation to any pool now monotonically increases per-delegator ROA, through the fixed-fee amortization channel alone, with no offsetting pledge-bonus dilution. The high-pledge regime that currently punishes delegators ceases to exist as a regime.

The pledge derivative is similarly clean (adding pledge, with `S` fixed):

```
dA_new/dP                   = r · a₀ · S / (S_sat · (1+a₀))
d/dP [(A_new − F)/S]        = r · a₀ / (S_sat · (1+a₀))      > 0
```

Also strictly positive, and constant in `P`. Pledge growth always lifts ROA uniformly across the pool, regardless of how much pledge already exists. SPOs who add pledge can show their delegators a direct ROA gain — a relationship that is muddled in the current formula.

**Worked numerical example.** Same 50 M-pledge pool, `m = 1%`, `F = 340`, `r = 0.000400`, `S_sat = 75 M`.

*Before delegation arrives* — `P = 50 M`, `S = 50 M` (pledge only), `u = 50/75 ≈ 0.667`:

```
A_new         = 0.000400 · 0.3 · 50M · 50M / (75M · 1.3) ≈ 3077
(A − F)/S     = (3077 − 340) / 50M                       ≈ 5.47 × 10⁻⁵
```

*After 25 M of delegation arrives* — `P = 50 M`, `S = 75 M`, `u = 1.0`:

```
A_new         = 0.000400 · 0.3 · 50M · 75M / (75M · 1.3) ≈ 4615
(A − F)/S     = (4615 − 340) / 75M                       ≈ 5.70 × 10⁻⁵
```

The `(A − F)/S` term *rises* from `5.47 × 10⁻⁵` to `5.70 × 10⁻⁵` — a small structural gain for every delegator in the pool. Under the current formula the same change drops the term from `8.55 × 10⁻⁵` to `5.70 × 10⁻⁵`. The dilution becomes a small gain.

Both formulas land at the same value (`5.70 × 10⁻⁵`) at saturation. This is by construction: `A_new = A_current` when `u = 1`. The saturated pool — the equilibrium point — is unchanged. What changes is the *path* into saturation: under the current formula, delegators are punished for taking that path; under the proposal, they are rewarded for it.

### A.4 Extended stakeholder analysis

This section expands the compact `Stakeholder summary` in the body with the mechanism-level reasoning behind each effect.

#### SPOs

- **Pledge becomes a partnership claim, not an isolated entitlement.** An SPO with high pledge but no delegators earns no pledge bonus under the proposal. To realize the bonus, they must attract delegators. This converts pledge from a one-sided revenue declaration into the SPO's contribution to a joint enterprise — exactly the relationship the formula's authors intended `a₀` to create but never quite achieved.
- **The saturation case is unchanged.** An SPO who runs a near-saturated pool today earns the same pledge bonus, the same margin, the same fixed fee under the proposal. Nothing is taken away from operators who are already attracting the delegation their pledge implies.
- **Small honest operators become structurally viable.** An operator with modest pledge can compete by attracting delegation. The path "build a quality pool → attract delegators → earn pledge bonus through their participation" becomes the explicit incentive. Pool operation no longer requires whale-tier personal capital to make economic sense.
- **A new bargaining surface emerges naturally.** SPOs can lower margin, improve performance, attest to single-pool operation, or otherwise court large delegators with the visible promise that delegation lifts everyone's ROA in their pool. Today an SPO's pledge declaration is the only public commitment they make; under the proposal, every operational improvement becomes legible to delegators because it materializes in `(A − F)/S`.

#### Delegators

- **Adding delegation to any pool always increases per-delegator ROA.** This is the central result. Whether 1 ADA or 25 million ADA arrives, the math agrees with the intuition that joining a pool helps the people there. The high-pledge dilution regime is structurally removed.
- **Sticky stake gets a tailwind.** Delegators who never revisit their decision still benefit when others arrive at their pool. A pool that grows toward saturation lifts its inhabitants' ROA continuously, not just at the moment of saturation.
- **Pool selection simplifies and improves for the rational delegator.** The two ROA terms `r/(1+a₀)` and `(A − F)/S` both have transparent shapes: the first is universal, the second scales with pledge and inversely with `F/S`. A rational delegator's job becomes "find pools with high `P · u / S` and low `F`" — a single comparable metric per pool, replacing the regime-dependent reasoning the current formula forces.
- **Pledge increases visibly lift every delegator's ROA.** When an SPO commits more pledge, every delegator's per-ADA bonus rises by exactly `r · a₀ / (S_sat · (1+a₀))`. The relationship is public, computable, and easy to verify epoch over epoch.

#### Cooperatives

This subsection treats cooperatives as a class. Pool Ranger is cited as an example where it grounds an otherwise abstract claim.

- **Bargaining power becomes structural without any registration or identification.** A cooperative benefits as any large delegator does. There is no need for the protocol to recognize a cooperative as a special party, no need for a registry, no need to consolidate stake credentials. A cooperative's leverage is simply "we bring substantial delegation, and the math of our arrival is visible to your delegators."
- **The bargaining math is the same math every delegator sees.** When a cooperative says "we will bring 25 M to this pool and lift `A_new/S` accordingly — adjust your margin to X% or we go elsewhere," the SPO and the existing delegators can both verify the claim. The credibility of the threat is automatic.
- **Withdrawal is visibly costly.** The day a cooperative leaves a pool, `S` drops, `A_new` drops with it, and every remaining delegator's ROA drops. The credible threat of withdrawal stops being a private negotiation and becomes a publicly observable mathematical event. SPOs have a continuous incentive to retain large delegators, not just attract them.
- **The values-vs-yield trade-off shrinks.** With dilution eliminated, a cooperative can weight pool selection toward community values — governance participation, software contributions, single-pool operators, public-goods funding — without sacrificing yield in any high-pledge regime. The ROA penalty for values-driven selection drops to near zero. This is the operational premise Pool Ranger is built around, and the proposal removes the structural obstacle to it for every comparable cooperative.

#### Decentralization

- **Sybil splitting is more strongly punished than today.** Under the current formula, a whale splitting `X` ADA into `N` pools earns the same total pledge bonus regardless of `N` (Sybil resistance is paid for by the delegator-preference channel). Under the proposal, splitting reduces the total pledge bonus across the split pools by a factor of `N`, because each pool's bonus now multiplies by its own utilization (which is at best `1/N` of the unsplit pool's utilization, given the same delegator base). The deterrent strengthens at the formula level, not just at the equilibrium-behavior level.
- **Small SPOs gain a viable on-ramp.** Today small pools cannot compete with whale-pledge pools on the pledge-bonus axis. Under the proposal, a small pool that attracts delegation earns the full saturated pledge bonus, in proportion to its (modest) pledge. Many small honest pools can each become attractive to a fraction of delegators. The ~3,000-pool population the network maintains today can be productive, not just tolerated.
- **Power tilts from SPOs toward delegators.** Currently SPOs hold pricing power and delegators choose only which pool to accept. The proposal makes every act of delegation a publicly visible contribution to a pool's revenue. SPOs court delegators with operational improvements, not just margin marketing. Two-sided negotiation replaces one-sided extraction.
- **The "fill pools to saturation" equilibrium becomes self-enforcing.** Empty pledged pools no longer earn — so empty pools either fill or fade. Saturated pools continue to earn the same as today. The protocol-intended convergence on `k` well-utilized pools gains a continuous gravitational pull at every utilization level, not just at the saturation boundary.

#### Protocol health

- **The dilution regime is structurally removed.** The current formula's `A > F` regime no longer exists, because `A` now scales with `S`. The rational-delegator function the formula assumes is finally rewarded by the formula it appears in.
- **No new on-chain quantity, no new parameter, no new certificate.** Implementation cost is a single multiplication by `S / S_sat` in the gross-rewards calculation. `S` and `P` are already tracked per epoch.
- **Sybil resistance is preserved and strengthened.** `a₀` continues to do its job. The delegator-preference channel that deters splitting is reinforced by formula-level penalties for splitting.
- **Treasury impact is governance-tunable.** Below-saturation pools emit less pledge bonus than today, so total emission is slightly reduced when the network operates below average saturation. The unused share stays in the reserve and is distributed in later epochs (consistent with how the reserve depletes today). Governance can recalibrate `a₀` upward to compensate exactly if it wants to preserve the current total emission profile, or accept slower reserve depletion as a side effect.
- **The change is observable, monotone, and reversible.** Every effect — on every pool, every delegator, every SPO — is computable from public quantities. The blending coefficient `b` makes adoption arbitrarily gradual. Governance can move it back toward `b = 0` if the equilibrium turns out worse than predicted.

### A.5 Extended risks and mitigations

The body lists the primary risks compactly. The expanded analysis below covers the same risks and three additional cases (whale self-delegation, single-pool high-pledge SPOs, implementation complexity).

| Risk | Mitigation |
|---|---|
| Below-saturation pools earn less pledge bonus, which could make cold-start harder for newly-launched pools | The strongest natural mitigation is that the proposal *creates* an incentive for cooperatives to fill such pools rapidly: arriving at a low-utilization pool with quality SPO behavior produces a large `dROA/dS` gain for everyone, which is the cooperative's bargaining lever. Cold start becomes a coordinated act, not a passive wait. If the network wants additional support for cold-start anyway, an explicit launch grant from treasury can be added separately without changing the formula. |
| Total emission may shrink if pools network-wide operate below average saturation, slowly extending reserve depletion | Easily compensated by a one-time upward recalibration of `a₀` so that average-utilization total bonus matches today's. Saturated pools see a small bonus uplift; below-saturation pools still receive less than today. The recalibration is a single governance vote, computable from current chain data. Alternatively, governance can accept slower reserve depletion as a benign side effect. |
| Established high-pledge SPOs whose pools are not near saturation see reduced rewards | Real. This is the intended redirection: the protocol stops paying pledge bonus to pledged pools that have not earned delegator interest. SPOs in this position can either improve operations to attract delegation, or accept that the pure-pledge revenue stream is no longer available. The saturated pledge bonus is fully preserved. |
| Whales might "self-delegate" — park ADA in their own pool to raise utilization and claim more pledge bonus | The whale's parked ADA earns rewards only as a delegator (after `F`, margin, and pro-rata split). The total emission to the whale net-of-costs is roughly the same as delegating that ADA to any other equivalent pool. There is no arbitrage advantage to self-delegation beyond what any delegator can capture by delegating to the whale's pool. The utilization metric is robust to this behavior. |
| Single-pool SPOs with high pledge and limited delegation see reduced rewards | Same redirection principle. The current formula effectively subsidizes high-pledge pools regardless of demand; the proposal makes the bonus contingent on demand. SPOs in this position have a clear path to recover: court delegators. |
| Sybil-splitting whales could try to attract delegators to each of their `N` pools to recover the lost bonus | Each of the `N` pools would still individually need to reach competitive utilization. The split whale's total available pool capacity is `N · S_sat`, of which they can pledge `X/N` per pool. To earn the same total pledge bonus as the unsplit case (delegated to capacity), they would need `N` times the delegator base — which by assumption they do not have. The formula-level penalty for splitting is robust. |
| Implementation complexity | Negligible. `S` and `P` are already snapshotted per epoch. The change is a single multiplication by `min(S, S_sat) / S_sat`. No new on-chain state, no new transaction types, no new certificates. |

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
