---
CIP: ?
Title: Utilization-Scaled Pledge Bonus
Category: Ledger
Status: Proposed
Authors:
    - John Shearing <johnshearing@gmail.com>
Implementors: []
Discussions:
    - https://github.com/cardano-foundation/CIPs/pull/?
Created: 2026-05-15
License: CC-BY-4.0
---

## Abstract

Cardano's reward formula contains a structural defect in the pledge bonus term `A`: under the current specification, `A = r · a₀ · P / (1 + a₀)` depends on the operator's pledge `P` but not on the pool's total stake `S`. As delegation arrives at a high-pledge pool, the per-delegator share `(A − F)/S` strictly falls, so adding stake dilutes everyone already there. The very behavior the protocol's Nash equilibrium assumes — rational delegators concentrating stake into high-pledge, well-operated pools — is punished by the formula itself.

This CIP proposes a parameter-free reshape of the existing pledge bonus by multiplying it by pool utilization `u = min(S, S_sat) / S_sat`. The new bonus is `A = r · a₀ · P · min(S, S_sat) / (S_sat · (1 + a₀))`. A saturated pool earns exactly today's pledge bonus; a half-utilized pool earns half; an empty pledged pool earns nothing from pledge until delegators arrive. No new parameter is introduced — `a₀` retains its name, governance dial, and Sybil-resistance role. The change removes the dilution regime entirely, strengthens Sybil resistance at the formula level, makes "fill pools to saturation" self-enforcing at every utilization level, and gives small honest operators a viable on-ramp through delegation rather than personal capital.

> **▶ Interactive simulator with guided tutorials.** A companion page lets readers manipulate `P`, `S`, `r`, `a₀`, `m`, `F`, and the blending coefficient `b`, and watch the formula's behavior in real time against side-by-side current-vs-proposed curves. Four narrated walkthroughs are built in: (1) **the math explainer** — what changes, why, with the formula derivation; (2) **who benefits, and by how much** — stakeholder-by-stakeholder tour of saturated SPOs, below-saturation SPOs, small honest operators, delegators, cooperatives, decentralization, and treasury; (3) **the multi-pool operator problem** — the quantitative case for how the CIP deters MPO behavior at the formula level without lowering Sybil resistance; (4) **free-form exploration** — manipulate every parameter freely. Live page: https://johnshearing.github.io/pool_ranger/CIP_UTILIZATION_SCALED_PLEDGE_BONUS.html. The same file is also included in this folder as `CIP_UTILIZATION_SCALED_PLEDGE_BONUS.html` and runs offline in any modern browser.

## Motivation: why is this CIP necessary?

The standard Cardano delegator return formula (Reward Sharing Scheme, CIP-0084) reduces to:

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
2. **Cooperative delegation has no protocol-level instrument.** Coordinators that perform the rational-delegator function for many small holders (e.g., Pool Ranger) suffer the dilution most acutely. Bringing 25 M ADA into a pool to gain bargaining leverage simultaneously erodes the ROA of the members on whose behalf the coordinator acts. Today's workaround — informal off-chain negotiation between large delegators and SPOs — is opaque and unverifiable.
3. **Small honest SPOs cannot compete on the pledge-bonus axis.** A small operator with modest pledge is structurally disadvantaged regardless of operational quality, because the bonus is tied to capital declared rather than capital actually attracted.
4. **The Sybil deterrent leans entirely on the delegator-preference channel.** Splitting `X` ADA into `N` pools leaves the total pledge bonus unchanged under the current formula; only delegator avoidance makes the split unprofitable. The formula itself does no Sybil work beyond setting `A`'s magnitude.
5. **Empty pledged pools earn the same per-pledge bonus as filled pools.** The protocol pays for an entitlement that has not yet produced the equilibrium it is meant to incentivize.

The obvious direct fix — lowering `a₀` — is unacceptable because `a₀` carries the Sybil-resistance load. Removing or weakening it reopens the stake-splitting channel. Any acceptable fix must preserve `a₀`'s deterrent role while removing the dilution.

A fuller treatment of the problem, the derivation of the proposed formula, numerical examples, and game-theoretic analysis of `a₀` under both regimes lives in two supporting documents shipped alongside this CIP:

- `utilization_scaled_pledge_bonus.md` (in this folder) — full written analysis with derivations.
- `CIP_UTILIZATION_SCALED_PLEDGE_BONUS.html` (in this folder) — an interactive simulator. Live URL: https://johnshearing.github.io/pool_ranger/CIP_UTILIZATION_SCALED_PLEDGE_BONUS.html

## Specification

### Notation

All symbols carry their standard CIP-0084 / Reward Sharing Scheme meaning:

- `r` — per-epoch reward rate (fraction of total ADA supply distributed per epoch).
- `a₀` — pledge influence factor (existing protocol parameter, currently `0.3`, governance-tunable).
- `k` — target stake-pool count (currently `500`).
- `P` — operator pledge (ADA, declared on-chain).
- `S` — total live stake delegated to the pool, including pledge.
- `S_sat` — saturation cap, defined as `(active network stake) / k`.
- `u` — pool utilization, defined as `min(S, S_sat) / S_sat`. `u ∈ [0, 1]`.

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

## Rationale: how does this CIP achieve its goals?

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
| CIP-50 leverage cap                   | Limit delegation/pledge ratio per pool               | No — addresses SPO leverage, not the dilution mechanism |
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

A fuller game-theoretic analysis, including numerical anchors and edge cases, is in the supporting documents shipped in this folder.

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

- CIP-0001 — CIP process and document structure.
- CIP-0084 — Reward Sharing Scheme (the formula this CIP modifies).
- CIP-1694 — On-chain governance actions (the mechanism this CIP would be activated through).
- CIP-50 — Pool leverage cap proposal (related; addresses a different symptom).
- Brünjes, Kiayias, Koutsoupias, Stouka — *Reward Sharing Schemes for Stake Pools* (the original RSS paper formalizing the formula this CIP modifies).
- `utilization_scaled_pledge_bonus.md` (in this folder) — Full written derivation, numerical anchors, and risk analysis.
- `CIP_UTILIZATION_SCALED_PLEDGE_BONUS.html` (in this folder) — Interactive simulator with four guided tutorials, runnable offline. Live page: https://johnshearing.github.io/pool_ranger/CIP_UTILIZATION_SCALED_PLEDGE_BONUS.html. Tutorials:
  - **The math explainer** — derivation of `A_new` from the existing reward formula, with the blending coefficient `b` and the current-vs-proposed curves side by side.
  - **Who benefits, and by how much** — stakeholder-by-stakeholder walkthrough: saturated SPOs, below-saturation SPOs, small honest operators, delegators, cooperatives, decentralization, treasury.
  - **The multi-pool operator problem** — quantitative tour showing today's formula imposes no cost on splitting, while the proposal taxes it proportional to `N` without lowering `a₀`.
  - **Free-form exploration** — every slider unlocked; sweep parameters and watch both formulas respond.

## Acknowledgements

This proposal was drafted with assistance from Claude (Anthropic). The mathematical derivation, the constraint that `a₀` must be preserved, the proposed `u` scaling, and the analysis of cooperative-delegation effects emerged from extended dialog between the author and the model. All claims have been independently re-derived by the author. Any errors are the author's.

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
