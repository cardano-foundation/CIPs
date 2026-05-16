## Question:

Cardano's reward formula has a structural defect that punishes the very behavior the protocol's Nash equilibrium depends on: when delegators add stake to a high-pledge pool — the only kind of pool a cost-aware delegator should target — per-delegator ROA *falls*. The cause is mechanical. The pledge bonus `A` is fixed by the SPO's pledge alone; it does not grow with pool stake `S`. As `S` rises, the per-ADA share of `A` (and the amortized share of the fixed fee `F`) both shrink. Adding delegation dilutes everyone already there.

A coordinated delegator like Pool Ranger — which performs the rational-delegator function the protocol assumes exists — feels this defect most acutely. To maximize member ROA it must concentrate stake into a high-pledge pool. To gain bargaining leverage over the SPO it must concentrate further still. Both moves dilute. The protocol gives nothing in return and the members pay the cost.

A direct fix — lowering `a₀` (the pledge influence factor) — is blocked: `a₀` is doing important Sybil-resistance work and cannot be removed without replacing the mechanism it carries.

Is there a way to remove the dilution directly, by reshaping the existing pledge-bonus formula so that it scales with pool stake — without inventing new parameters, new on-chain state, or special treatment for any class of delegator? A change that helps SPOs, helps every delegator, helps cooperatives like Pool Ranger, supports decentralization, and preserves protocol health?

## Glossary

This document is intended to stand alone. The tables below define every symbol and term used in the rest of the document. Readers familiar with Cardano staking can skim; readers new to it can return here whenever a term is unclear.

### Variables

| Symbol | Meaning | Current value (mainnet, 2026) |
|---|---|---|
| `r` | Per-epoch reward rate — fraction of total ADA supply distributed as rewards each epoch. Drifts down slowly as the protocol reserve depletes. | ≈ 0.000400 |
| `a₀` | Pledge influence factor — protocol parameter controlling how much extra reward a pool earns based on its pledge. Settable by on-chain governance. | 0.3 |
| `k` | Target number of stake pools the protocol is designed to converge on. Sets the saturation cap. | 500 |
| `F` | Fixed fee in ADA per epoch — flat overhead an SPO takes off the top of gross rewards before splitting the rest. Protocol enforces a minimum. | 170–340 (SPO-set, ≥ protocol minimum) |
| `m` | Margin — percentage of post-fee rewards the SPO takes before the remainder is split among delegators by stake fraction. | SPO-set, 0–100% |
| `P` | Pledge — ADA the SPO commits from their own funds to their own pool. Earns the pledge bonus `A`. | SPO-set |
| `S` | Total stake delegated to a pool, including the SPO's pledge plus all external delegation. | varies per pool |
| `S_sat` | Saturation point — total stake above which a pool's gross rewards stop growing. Approximately `(active network stake) / k`. | ≈ 65–75 M ADA |
| `u` | **Pool utilization** — the fraction `S / S_sat` of the saturation cap currently filled. The central quantity this proposal uses. | 0 to 1 |
| `p` | Performance factor — actual blocks the pool minted divided by the blocks its stake fraction would predict, capped at 1.0. | 0 to 1 |
| `A` (or `A_pledge`) | Pledge bonus per epoch — ADA/epoch advantage a pledged pool earns over an otherwise-identical zero-pledge pool. Under the current protocol equals `r · a₀ · P / (1+a₀)`. **Under the proposal in this document, equals `r · a₀ · P · S / (S_sat · (1+a₀))` — i.e., the current value multiplied by pool utilization `u`.** | derived |

### Terms

| Term | Definition |
|---|---|
| Epoch | A 5-day Cardano time period. Rewards are calculated and paid once per epoch. |
| ROA | Return on ADA — annualized percentage yield a delegator earns from staking. Computed by multiplying per-epoch yield by 73 (Cardano has 73 five-day epochs per year). |
| SPO | Stake Pool Operator — the entity running a Cardano stake pool. Sets `m`, declares `P`, and is paid `F` plus margin plus their pro-rata share. |
| Delegator | An ADA holder who delegates their staking rights to a pool to earn rewards. Retains spending control of their ADA at all times. |
| Cooperator | A coordinator that pools the staking rights of many individual delegators and directs them as a single block — Pool Ranger is the canonical example for this document. |
| Stake credential | The on-chain identity that determines which pool a UTxO's stake is delegated to. Distinct from the spending credential that controls who can spend the ADA. |
| Pledge | The portion of a pool's total stake committed by the SPO themselves. Signals operator commitment and earns a reward bonus via `a₀`. |
| Margin | The SPO's percentage cut of post-fee rewards before the remainder is split among delegators. |
| Fixed fee | A flat ADA-per-epoch overhead the SPO takes off the top of gross rewards, before margin. |
| Gross rewards | The total reward pot a pool earns in an epoch, before any deductions (F, margin, pledge share). |
| Saturation | The level at which adding more stake to a pool stops increasing its gross rewards. Beyond saturation, additional delegation dilutes per-ADA returns for everyone in the pool. |
| Utilization | The pool's current stake as a fraction of its saturation cap. A pool at half saturation has utilization 0.5. The central quantity this proposal uses to scale the pledge bonus. |
| Sybil attack | An attack in which one entity creates many fake identities — here, many small stake pools — to gain disproportionate influence while appearing as many independent participants. |
| Pledge bonus | The extra reward a pool earns through `a₀`-weighted pledge. Redistributed from the network's reward pot, not new emission. Under this proposal, scales with utilization. |
| Dilution | The effect where adding more stake to a pool reduces each existing stakeholder's per-ADA share of a fixed bonus. The defect this proposal removes. |
| Leverage | A cooperator's ability to influence an SPO's behavior through the credible threat of withdrawing or relocating large delegation. Today informal; under this proposal, becomes mathematically visible to every pool participant. |
| Nash equilibrium | A stable configuration in which no individual player can benefit from unilaterally changing strategy. Cardano's reward formula is designed to push the network toward an equilibrium of approximately `k` well-performing pools, assuming delegators behave rationally. |
| CIP | Cardano Improvement Proposal — the formal mechanism for proposing protocol changes. CIPs are debated, refined, voted on through on-chain governance, and activated through hard-fork combinator events. |
| Active stake | Total ADA actively delegated across the network in a given epoch. Used to compute `S_sat`. |
| Pool Ranger | The cooperative-delegation platform this document is written for. Pool Ranger members share their stake credential (never their spending key) with a coordinator that tracks pool parameters every epoch and rotates delegation toward whichever pools currently offer the best return. 99% of staking rewards flow to members, 1% to the coordinator. |

## Answer:

Yes. The proposal is to multiply the pledge bonus by pool utilization. The formula change is a single factor of `S / S_sat`. No new parameter is introduced. `a₀` retains its name and its Sybil-resistance role; what it multiplies is reshaped. The dilution regime that punishes adding delegation disappears entirely. The saturated pool earns exactly what it earns today. Below-saturation pools earn proportionally less pledge bonus — which is the cost — and that cost is the price of giving every delegator a structural reason to fill pools that are under-used, the equilibrium the protocol was designed to produce.

### 1. The problem in precise terms

The standard Cardano delegator ROA formula (variables defined in the Glossary above; original derivation in `SPO_REWARD_ANALYSIS_CHART_COMPANION.md`) is:

```
ROA = (1 − m) · [ r/(1+a₀) + (A − F)/S ] · 73 · 100%
where  A = r · a₀ · P / (1+a₀)
```

Note that under the current formula, `A` depends on `P` but not on `S`. This is the structural defect. Per-delegator ROA depends on `(A − F)/S`, and when `A` is fixed while `S` grows, that ratio shrinks.

The sign of `(A − F)` decides whether per-delegator ROA *rises* or *falls* as total pool stake `S` grows:

| Regime | `dROA/dS` | Pool type | Implication for adding delegation |
|---|---|---|---|
| `A > F` | negative | high-pledge pool (the kind a rational delegator must pick) | adding stake dilutes existing delegators |
| `A < F` | positive | low-pledge pool | adding stake helps via fixed-fee amortization |
| `A = F` | zero | edge case | ROA flat |

Quantitative anchor: take a 50 M-pledge pool with `F = 340`, `r = 0.000400`, `m = 1%`, `S_sat = 75 M`. With no external delegation, `S = 50 M` and `(A − F)/S ≈ 8.55 × 10⁻⁵`. When 25 M of delegation arrives and saturates the pool, `S = 75 M` and `(A − F)/S ≈ 5.70 × 10⁻⁵`. Roughly a **0.21% absolute ROA loss** for the delegators in the pool, paid for by their own arrival.

The deeper issue: **the reward formula's pledge bonus `A` does not scale with the pool's stake `S`.** Under the current formula, `A` is set by `P` alone — what the SPO commits — and is the same whether the pool has 1 ADA of delegation or 25 million ADA of delegation. Delegators thus split a fixed bonus pot. The more delegators arrive, the smaller each share.

This is the root cause behind every observed pathology of the current incentive: dilution, the structural conflict between concentration-for-leverage and concentration-for-ROA, the inability of cooperatives like Pool Ranger to negotiate, and the protocol's silence toward "rational delegator" behavior. Fix `A`'s independence from `S` and every symptom resolves at once.

### 2. Why `a₀` must be preserved

`a₀` is Cardano's primary defense against **Sybil-style stake splitting** — the scenario in which a single ADA whale creates many small pools to gain disproportionate block production while appearing as many independent operators. The mechanism works through delegator preference, not direct restriction:

- A whale with `X` ADA who splits into `N` pools earns `r · a₀ · (X/N) / (1+a₀)` of pledge bonus per pool — small per pool, total unchanged across all `N` pools.
- Rational delegators read the small `A` on each fake pool, see the unattractive ROA the small pledge bonus produces, and avoid those pools in favor of pools with concentrated pledge.
- Without delegators, the whale's `N`-pool split nets less revenue than concentrating in one pool (each split pool's fixed fee is unearned, margin revenue collapses, saturation budgets go unused). The strategy fails in expectation.

Lowering or removing `a₀` would solve the dilution problem but reopen the Sybil channel.

**Constraint for any acceptable solution: leave the Sybil deterrent intact.**

This proposal preserves `a₀` as a parameter — same name, same governance dial. It only changes what `a₀` multiplies. As shown in §6, the Sybil deterrent strengthens under the proposal: splitting a whale's pledge across `N` pools now reduces the *total* pledge bonus across those pools by a factor of `N`, rather than leaving it unchanged. The delegator-preference channel that does the Sybil work today continues to do it, with mathematical reinforcement.

(For a fuller game-theoretic treatment of `a₀`, including why the current value of 0.3 is widely considered too weak in practice and how multi-pool operators exploit it, see `claude_queries/pledge_effects.md`. That document is supporting material, not a prerequisite for the rest of this one.)

### 3. The proposal: scale the pledge bonus by pool utilization

Replace the current pledge-bonus formula:

```
A_current = r · a₀ · P / (1 + a₀)                          [today]
```

with:

```
A_new     = r · a₀ · P · min(S, S_sat) / (S_sat · (1+a₀))  [proposed]
         = A_current · (S/S_sat)                            [for S ≤ S_sat]
         = A_current · u                                    [where u = S/S_sat is utilization]
```

In words: **the pledge bonus is the current pledge bonus times pool utilization.** A pool at full saturation earns exactly today's bonus. A pool at half utilization earns half. An empty pledged pool earns nothing from pledge until delegators arrive.

The `min(S, S_sat)` caps utilization at 1, preserving the existing protocol property that no pool can exploit saturation. Beyond saturation, `A` matches its current saturation value (`r · a₀ · P / (1+a₀)`) and stops growing.

Equivalent reading: under the current protocol, an SPO declares pledge and immediately earns a bonus that grows with that pledge regardless of whether delegators show up. Under the proposal, the SPO's pledge declaration is a *claim* on a bonus pot; the claim is only paid out in proportion to how much delegation the pool actually attracts. Pledge alone is no longer enough.

The change is parameter-free — `a₀` is the only existing knob and it is reused. The change is also reversible by trivial transition: if the protocol wants a smooth phase-in rather than a hard switch, governance can introduce a one-time blending coefficient `b ∈ [0, 1]` and use `A_blend = A_current · (1 − b + b · u)`. At `b = 0` the formula reproduces current behavior exactly; at `b = 1` it equals the proposed form. Any intermediate value is valid. Governance can dial `b` from 0 toward 1 across hard forks if it prefers gradual adoption. The body of this document analyzes the `b = 1` form (full utilization scaling), which is the limit case.

### 4. Why this fixes the dilution problem

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

Strictly positive. **Adding delegation to any pool now monotonically increases per-delegator ROA**, through the fixed-fee amortization channel alone, with no offsetting pledge-bonus dilution. The high-pledge regime that currently punishes delegators ceases to exist as a regime.

The pledge derivative is similarly clean (adding pledge, with `S` fixed):

```
dA_new/dP                   = r · a₀ · S / (S_sat · (1+a₀))
d/dP [(A_new − F)/S]        = r · a₀ / (S_sat · (1+a₀))      > 0
```

Also strictly positive, and constant in `P`. **Pledge growth always lifts ROA uniformly across the pool**, regardless of how much pledge already exists. SPOs who add pledge can show their delegators a direct ROA gain — a relationship that is muddled in the current formula.

Numerical example: same 50 M-pledge pool, `m = 1%`, `F = 340`, `r = 0.000400`, `S_sat = 75 M`.

**Before delegation arrives** — `P = 50 M`, `S = 50 M` (pledge only), `u = 50/75 ≈ 0.667`:

```
A_new         = 0.000400 · 0.3 · 50M · 50M / (75M · 1.3) ≈ 3077
(A − F)/S     = (3077 − 340) / 50M                       ≈ 5.47 × 10⁻⁵
```

**After 25 M of delegation arrives** — `P = 50 M`, `S = 75 M`, `u = 1.0`:

```
A_new         = 0.000400 · 0.3 · 50M · 75M / (75M · 1.3) ≈ 4615
(A − F)/S     = (4615 − 340) / 75M                       ≈ 5.70 × 10⁻⁵
```

The `(A − F)/S` term *rises* from `5.47 × 10⁻⁵` to `5.70 × 10⁻⁵` — a small structural gain for every delegator in the pool. Under the current formula the same change drops the term from `8.55 × 10⁻⁵` to `5.70 × 10⁻⁵`. The dilution becomes a small gain.

Both formulas land at the same value (`5.70 × 10⁻⁵`) at saturation. This is by construction: `A_new = A_current` when `u = 1`. The saturated pool — the equilibrium point — is unchanged. What changes is the *path* into saturation: under the current formula, delegators are punished for taking that path; under the proposal, they are rewarded for it.

### 5. Who benefits, and how

#### SPOs

- **Pledge becomes a partnership claim, not an isolated entitlement.** An SPO with high pledge but no delegators earns no pledge bonus under the proposal. To realize the bonus, they must attract delegators. This converts pledge from a one-sided revenue declaration into the SPO's contribution to a joint enterprise — exactly the relationship the formula's authors intended `a₀` to create but never quite achieved.
- **The saturation case is unchanged.** A SPO who runs a near-saturated pool today earns the same pledge bonus, the same margin, the same fixed fee under the proposal. Nothing is taken away from operators who are already attracting the delegation their pledge implies.
- **Small honest operators become structurally viable.** An operator with modest pledge can compete by attracting delegation. The path "build a quality pool → attract delegators → earn pledge bonus through their participation" becomes the explicit incentive. Pool operation no longer requires whale-tier personal capital to make economic sense.
- **A new bargaining surface emerges naturally.** SPOs can lower margin, improve performance, attest to single-pool operation, or otherwise court large delegators with the visible promise that delegation lifts everyone's ROA in their pool. Today an SPO's pledge declaration is the only public commitment they make; under the proposal, every operational improvement becomes legible to delegators because it materializes in `(A − F)/S`.

#### Delegators (Pool Ranger members and others)

- **Adding delegation to any pool always increases per-delegator ROA.** This is the central result. Whether 1 ADA or 25 million ADA arrives, the math agrees with the intuition that joining a pool helps the people there. The "high-pledge dilution" regime is structurally removed.
- **Sticky stake gets a tailwind.** Delegators who never revisit their decision still benefit when others arrive at their pool. A pool that grows toward saturation lifts its inhabitants' ROA continuously, not just at the moment of saturation.
- **Pool selection simplifies and improves for the rational delegator.** The two ROA terms `r/(1+a₀)` and `(A − F)/S` both have transparent shapes: the first is universal, the second scales with pledge and inversely with `F/S`. A rational delegator's job becomes "find pools with high `P · u / S` and low `F`" — a single comparable metric per pool, replacing the regime-dependent reasoning the current formula forces.
- **Pledge increases visibly lift every delegator's ROA.** When an SPO commits more pledge, every delegator's per-ADA bonus rises by exactly `r · a₀ / (S_sat · (1+a₀))`. The relationship is public, computable, and easy to verify epoch over epoch.

#### Pool Ranger specifically

- **Bargaining power becomes structural without any registration or identification.** Pool Ranger benefits as any large delegator does. There is no need for the protocol to recognize Pool Ranger as a cooperative, no need for a registry, no need to consolidate stake credentials. The per-member-script architecture (Pool Ranger's current anti-saturation design) continues to function unchanged. Pool Ranger's leverage is simply "we bring substantial delegation, and the math of our arrival is visible to your delegators."
- **The bargaining math is the same math every delegator sees.** When Pool Ranger says "we will bring 25 M to this pool and lift `A_new/S` accordingly — adjust your margin to X% or we go elsewhere," the SPO and the existing delegators can both verify the claim. The credibility of the threat is automatic.
- **Withdrawal is visibly costly.** The day Pool Ranger leaves a pool, `S` drops, `A_new` drops with it, and every remaining delegator's ROA drops. The "credible threat of withdrawal" stops being a private negotiation and becomes a publicly observable mathematical event. SPOs have a continuous incentive to retain large delegators, not just attract them.
- **The values-vs-yield trade-off shrinks.** With dilution eliminated, Pool Ranger can weight pool selection toward community values — governance participation, software contributions, single-pool operators, public-goods funding — without sacrificing yield in any high-pledge regime. The ROA penalty for values-driven selection drops to near zero.

#### Decentralization

- **Sybil splitting is more strongly punished than today.** Under the current formula, a whale splitting `X` ADA into `N` pools earns the same total pledge bonus regardless of `N` (Sybil resistance is paid for by the delegator-preference channel). Under the proposal, splitting reduces the total pledge bonus across the split pools by a factor of `N`, because each pool's bonus now multiplies by its own utilization (which is at best `1/N` of the unsplit pool's utilization, given the same delegator base). The deterrent strengthens at the formula level, not just at the equilibrium-behavior level.
- **Small SPOs gain a viable on-ramp.** Today small pools cannot compete with whale-pledge pools on the pledge-bonus axis. Under the proposal, a small pool that attracts delegation earns the full saturated pledge bonus, in proportion to its (modest) pledge. Many small honest pools can each become attractive to a fraction of delegators. The 3,000-pool population the network maintains today can be productive, not just tolerated.
- **Power tilts from SPOs toward delegators.** Currently SPOs hold pricing power and delegators choose only which pool to accept. The proposal makes every act of delegation a publicly visible contribution to a pool's revenue. SPOs court delegators with operational improvements, not just margin marketing. Two-sided negotiation replaces one-sided extraction.
- **The "fill pools to saturation" equilibrium becomes self-enforcing.** Empty pledged pools no longer earn — so empty pools either fill or fade. Saturated pools continue to earn the same as today. The protocol-intended convergence on `k` well-utilized pools gains a continuous gravitational pull at every utilization level, not just at the saturation boundary.

#### Protocol health

- **The dilution regime is structurally removed.** The current formula's `A > F` regime no longer exists, because `A` now scales with `S`. The rational-delegator function the formula assumes is finally rewarded by the formula it appears in.
- **No new on-chain quantity, no new parameter, no new cert.** Implementation cost is a single multiplication by `S / S_sat` in the gross-rewards calculation. `S` and `P` are already tracked per epoch.
- **Sybil resistance is preserved and strengthened.** `a₀` continues to do its job. The delegator-preference channel that deters splitting is reinforced by formula-level penalties for splitting (see §6).
- **Treasury impact is governance-tunable.** Below-saturation pools emit less pledge bonus than today, so total emission is slightly reduced when the network operates below average saturation. The unused share stays in the reserve and is distributed in later epochs (consistent with how the reserve depletes today). Governance can recalibrate `a₀` upward to compensate exactly if it wants to preserve the current total emission profile, or accept slower reserve depletion as a side effect.
- **The change is observable, monotone, and reversible.** Every effect — on every pool, every delegator, every SPO — is computable from public quantities. The blending coefficient `b` (§3) makes adoption arbitrarily gradual. Governance can move it back toward `b = 0` if the equilibrium turns out worse than predicted.

### 6. Risks and mitigations

| Risk | Mitigation |
|---|---|
| Below-saturation pools earn less pledge bonus, which could make cold-start harder for newly-launched pools | The strongest natural mitigation is that the proposal *creates* an incentive for cooperators like Pool Ranger to fill such pools rapidly: arriving at a low-utilization pool with quality SPO behavior produces a large `dROA/dS` gain for everyone, which is the cooperator's bargaining lever. Cold start becomes a coordinated act, not a passive wait. If the network wants additional support for cold-start anyway, an explicit launch grant from treasury can be added separately without changing the formula. |
| Total emission may shrink if pools network-wide operate below average saturation, slowly extending reserve depletion | Easily compensated by a one-time upward recalibration of `a₀` so that average-utilization total bonus matches today's. Saturated pools see a small bonus uplift; below-saturation pools still receive less than today. The recalibration is a single governance vote, computable from current chain data. Alternatively, governance can accept slower reserve depletion as a benign side effect. |
| Established high-pledge SPOs whose pools are not near saturation see reduced rewards | Real. This is the intended redirection: the protocol stops paying pledge bonus to pledged pools that have not earned delegator interest. SPOs in this position can either improve operations to attract delegation, or accept that the pure-pledge revenue stream is no longer available. The saturated pledge bonus is fully preserved. |
| Whales might "self-delegate" — park ADA in their own pool to raise utilization and claim more pledge bonus | The whale's parked ADA earns rewards only as a delegator (after `F`, margin, and pro-rata split). The total emission to the whale net-of-costs is roughly the same as delegating that ADA to any other equivalent pool. There is no arbitrage advantage to self-delegation beyond what any delegator can capture by delegating to the whale's pool. The utilization metric is robust to this behavior. |
| Single-pool SPOs with high pledge and limited delegation see reduced rewards | Same redirection principle. The current formula effectively subsidizes high-pledge pools regardless of demand; the proposal makes the bonus contingent on demand. SPOs in this position have a clear path to recover: court delegators. |
| Sybil-splitting whales could try to attract delegators to each of their `N` pools to recover the lost bonus | Each of the `N` pools would still individually need to reach competitive utilization. The split whale's total available pool capacity is `N · S_sat`, of which they can pledge `X/N` per pool. To earn the same total pledge bonus as the unsplit case (delegated to capacity), they would need `N` times the delegator base — which by assumption they do not have. The formula-level penalty for splitting is robust. |
| Implementation complexity | Negligible. `S` and `P` are already snapshotted per epoch. The change is a single multiplication by `min(S, S_sat) / S_sat`. No new on-chain state, no new transaction types, no new certificates. |

### 7. Comparison to existing CIP energy

| Proposal | What it does | Solves the dilution problem? |
|---|---|---|
| Lower `a₀` directly | Weakens the pledge bonus universally | Yes, but reopens the Sybil channel |
| CIP-50 leverage cap | Limits delegation/pledge ratio per pool | No — addresses SPO leverage, not the dilution mechanism |
| Treasury "trough" subsidy | Pays delegators to fill underused pools | Partial; treasury-funded, hard to scale |
| **Utilization-scaled pledge bonus** | **Reshape `A` to scale with `S/S_sat`. No new parameter; existing `a₀` reused.** | **Yes — directly, treasury-neutral with recalibration, Sybil-strengthening, helps every delegator** |

Comparison to lowering `a₀` directly: lowering `a₀` weakens the pledge bonus everywhere and reopens the Sybil channel that `a₀` is currently policing. Utilization scaling preserves `a₀` and its Sybil work, while changing what `a₀` multiplies. The Sybil deterrent is in fact strengthened, because splitting reduces total pledge bonus by `1/N` rather than leaving it unchanged.

### 8. Summary

Cardano's reward formula has a single structural defect that produces every observed symptom in the cooperative-delegation debate: the pledge bonus `A` is independent of pool stake `S`. As `S` grows, the per-delegator share of `A` shrinks, and delegators in high-pledge pools are punished for arriving. Cooperatives like Pool Ranger, which exist specifically to do the protocol-assumed work of rotating delegation toward best return, suffer the cost most acutely and have no protocol-level instrument to recover it.

The proposal is to multiply the pledge bonus by pool utilization `S / S_sat`. The formula becomes:

```
A = r · a₀ · P · min(S, S_sat) / (S_sat · (1+a₀))
```

A pool at full saturation earns exactly today's pledge bonus. A pool at half utilization earns half. An empty pledged pool earns nothing from pledge until delegators arrive. The change requires no new parameter, no new on-chain quantity, no registration of any party, and no special treatment for any class of delegator.

Adopting this reform would:

- Remove the dilution regime entirely — adding delegation to any pool monotonically increases per-delegator ROA
- Make every pledge increase produce a visible, computable lift in delegator ROA
- Preserve every existing protocol guarantee — Sybil resistance, saturation cap, treasury balance (with optional one-time `a₀` recalibration), `k`-pool convergence target
- Strengthen Sybil resistance at the formula level (splitting reduces total pledge bonus by `1/N`)
- Give cooperatives like Pool Ranger structural bargaining power without requiring any special recognition, registration, or consolidation of stake credentials — their leverage emerges as a side effect of being any large delegator
- Open small honest SPOs to competitive viability through delegation rather than personal pledge
- Make the "fill pools to saturation" equilibrium self-enforcing at every utilization level, not just at the saturation boundary
- Tilt power from SPO-as-price-setter toward two-sided negotiation between SPOs and delegators

It is the most parsimonious mechanism-design fix to the cooperative-delegation gap: it removes the structural cause of dilution rather than working around its symptoms.
