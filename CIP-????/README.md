---
CIP: 183
Title: Conflict-Based Fee Priority in Mempool
Category: Network
Status: Proposed
Authors:
  - fallen-icarus <modern.daidalos@gmail.com>
Implementors: []
Discussions: []
Created: 2026-04-09
License: CC-BY-4.0
---

## Abstract

The eUTxO model gives Cardano a capability no account-based blockchain possesses: because
transactions explicitly declare their inputs, contention can be attributed to *specific UTxOs*
rather than to the network as a whole. This makes it possible to build a fee market that raises fees
only for the resources under contention, leaving everyone else unaffected.

This CIP implements that capability. When two transactions in a node's mempool attempt to spend an
overlapping UTxO, the node keeps the one paying a higher fee. No ledger rules, fee formulas, or
transaction formats change — only the mempool's admission heuristic for handling conflicting
transactions.

## Motivation: Why is this CIP necessary?

### eUTxO enables per-resource fee markets

On account-based chains like Ethereum, transactions interact with shared global state. When the
network is congested, there is no way to attribute that congestion to specific resources — it is an
emergent property of total demand against total block capacity. Fee markets on these chains are
therefore *global*: when demand rises, fees rise for everyone, whether or not a particular user's
transaction is contributing to the congestion.

| Model             | Contention scope     | Who pays more                        |
|:------------------|:---------------------|:-------------------------------------|
| Bitcoin RBF       | Global (block space) | Everyone in that block               |
| Ethereum EIP-1559 | Global (base fee)    | Everyone on the network              |
| This CIP          | Per-UTxO             | Only parties competing for that UTxO |

Cardano's eUTxO model is structurally different. Every transaction declares exactly which UTxOs it
will consume. When two transactions conflict — meaning they attempt to spend an overlapping UTxO —
the conflict is visible, local, and attributable. This makes it possible to resolve contention at
the level of the individual resource, without any collateral impact on unrelated transactions.

This CIP is the first fee market to exploit that structural property.

### UTxO contention is real and FIFO is arbitrary

On eUTxO, each DeFi intent — a limit order, a liquidity position, a loan offer — lives at its own
UTxO. When multiple parties want to interact with the same UTxO, their transactions conflict and
only one can be included in a block.

Under the current mempool policy, conflicts are resolved by arrival order: whichever transaction
reaches a node's mempool first is kept, and later arrivals are rejected. From the participants'
perspective, this is effectively random — the outcome depends on network propagation timing, not on
anything within their control.

FIFO is not a deliberate design choice. It is the absence of a policy. It discards information (how
much each party is willing to pay) and replaces it with noise (who happened to propagate faster).
The value that participants would willingly pay to secure a contested UTxO is dissipated entirely.

### The obvious solution: an auction

The correct mechanism for allocating a scarce resource to the party who values it most is an
auction. This is not a novel insight — it is backed by thousands of years of economic practice and
centuries of formal theory.

When two transactions conflict over the same UTxO, the mempool runs a trivial auction: keep the
higher-fee transaction, drop the lower-fee one. The winner pays their bid to the network via
transaction fees. The loser's transaction fails cleanly — on eUTxO, a transaction that references a
spent UTxO simply fails validation at no cost to the submitter. It does not execute with a worse
outcome.

This is the entire mechanism. Its simplicity is a feature.

### Why Cardano's implementation is simple

Bitcoin's Replace-By-Fee (RBF) mechanism solves a similar problem but requires substantially more
complexity. The reason is **transaction pinning**: Bitcoin allows spending unconfirmed outputs, so a
"child" transaction can reference an output that exists only in the mempool, creating dependency
chains among pending transactions. An adversary can attach a large, low-feerate child to a parent
transaction, making the parent artificially expensive to replace. Mitigating this required years of
incremental design: descendant package tracking, eviction-weight calculations, cluster mempool
redesigns, and topology restrictions like TRUC/V3 transactions.

Cardano also allows spending unconfirmed outputs, so dependency chains can form in the mempool. In
principle, this creates the same pinning opportunity: an adversary could attach low-fee descendants
to a transaction to inflate its replacement cost. In practice, two structural properties of Cardano
neutralize this attack, eliminating the need for Bitcoin's elaborate countermeasures.

**No depth cap needed.** Bitcoin's mempool can hold ~300 MB of transactions, giving an attacker room
to build deep dependency chains. Bitcoin had to introduce artificial chain depth limits (and
eventually a full cluster mempool redesign) to bound the damage. Cardano's mempool holds roughly two
blocks of transactions. The small mempool naturally limits how deep any dependency chain can grow —
there is simply not enough room for the kind of deep pinning chains that motivated Bitcoin's
complexity.

**No topology restriction needed.** Bitcoin's ~10-minute block time gives an attacker a wide window
to construct and propagate a pinning chain before the contest is resolved. This motivated topology
restrictions like TRUC/V3 transactions, which constrain how descendants can be attached. Cardano's
~20-second block time means dependency chains are confirmed or expired quickly, giving an attacker a
narrow window to build a meaningful pin before the next block resolves the situation.

These structural differences mean the replacement rule only needs one addition beyond the basic
conflict case: when a transaction is evicted, its descendants are evicted with it, and the
replacement must pay more than the total fees of everything it displaces. The full specification
follows below.

### Composability with network-level fee markets

This CIP and a hypothetical block space congestion mechanism address different scarce resources at
different stages of the transaction lifecycle.

This CIP operates at **mempool admission** and resolves a specific kind of scarcity: multiple
parties wanting the same UTxO. It determines which transaction *survives a conflict*. A network-level
congestion mechanism would operate at **block construction** and resolve a different kind of
scarcity: more total transactions than block capacity. It would determine which transactions *get
included in a block*.

The two compose cleanly. The mempool uses this CIP's conflict resolution to ensure the highest-value
transaction survives each UTxO conflict. The block producer then uses whatever congestion pricing
mechanism is in place to pack the most valuable set of surviving transactions into the available
space. Each layer optimizes for the scarce resource it manages, without interfering with the other.

Neither mechanism substitutes for the other. Conflict resolution cannot solve block-level congestion
(it only handles UTxO-specific conflicts). Block-level congestion pricing cannot solve UTxO
contention (it has no way to compare two transactions that want the same input). They are
complementary tools for complementary problems.

### Composability with the application-layer contention market

DeFi order books provide a separate contention management layer at the application level: users
choose *which* order to interact with, and can pay a price premium to target a less contested one.
Choosing a limit order priced 3% above market may reduce the number of competing parties from dozens
to zero.

This CIP adds a second layer underneath. Together, they form a two-dimensional contention market:

| Dimension     | Mechanism                   | What it controls                            |
|:--------------|:----------------------------|:--------------------------------------------|
| Price premium | Choose a worse-priced order | Probability of contention occurring          |
| Fee premium   | Pay higher transaction fees | Probability of winning if contention occurs  |

The first dimension thins the field. The second resolves whatever competition remains. Neither is
sufficient alone — avoiding the crowd doesn't help if someone else picks the same order, and
outbidding doesn't help if dozens of bots are driving fees skyward. But combined, they give users
fine-grained control over their chance of success.

### Sustainability

Under FIFO, contention-driven value — the surplus that participants would willingly pay to secure a
contested UTxO — is left on the table. Winners are chosen randomly and pay minimum fees. This CIP
redirects that surplus into the network: higher fees from contested transactions flow into the
treasury and staking rewards.

This revenue has three useful properties.
1. It is generated precisely when network resources are scarce.
2. It comes exclusively from participants who are voluntarily competing for profitable
   opportunities.
3. It scales naturally with DeFi activity — the more contention the ecosystem produces, the more fee
   revenue it generates.

### Retail users are not priced out

A natural concern is that fee-based replacement will lead to runaway bidding wars where only
well-capitalized bots can compete. In practice, the mechanics of the localized fee market work in
retail's favor.

**Retail users control their bid.** A user who urgently needs a contested UTxO can overpay upfront —
say 5–10x the standard fee, turning a 0.5 ADA fee into 2.5–5.0 ADA. Outside of high-value
arbitrage or liquidation opportunities, bots tend to penny-pinch to preserve their margins. Because
bots can easily retry transactions, they are mathematically better off keeping their bids small and
winning over many contests rather than overpaying for any single one. A retail user who jumps the
bid by a large increment is like an auction bidder who raises by $100 when the room is incrementing
by $1 — the room usually folds.

**Continuing UTxOs defuse escalation.** Many contested DeFi resources are continuing UTxOs: the
resource is immediately recreated at a new UTxO after the current transaction. When a bot sees a
large retail bid, the rational, margin-optimizing choice is not to start a bidding war — it is to
let that UTxO go and grab the next one in the subsequent block for a fraction of the cost. The
contest resets every ~20 seconds.

**Localized fees mean no collateral damage.** On chains with global fee markets, bidding wars are
toxic because normal transactions get caught in the crossfire — everyone must bid for the same block
space. This CIP confines the bidding to the specific UTxO under contention. Instead of one giant
auction, there are many small independent auctions: one UTxO might see a 15 ADA bid while another
sees 1.5 ADA, and every uncontested transaction pays its standard fee as if the bidding wars did not
exist.

Paying 2.5–5.0 ADA for guaranteed priority on a specific contested resource is not "only the rich
can play." It is a modest, voluntary premium — comparable to choosing expedited shipping — available
to anyone who values that particular UTxO highly enough.

### Impact on MEV

On account-based chains, fee markets are associated with harmful MEV extraction — specifically
sandwich attacks, where an adversary inserts transactions before and after a victim's transaction to
manipulate shared state and extract value. This attack vector does not exist on eUTxO. Transactions
are fully deterministic: a user knows exactly what inputs will be consumed and what outputs will be
produced before they sign. There is no shared global state that an adversary's transaction could
modify to change the outcome of yours.

This CIP does not introduce any new MEV. The extractable value in a contested UTxO — the surplus
between a mispriced limit order and the market price — exists regardless of mempool policy. Under
FIFO, bots already race to capture it. The only question is how the contest is decided and how the
surplus is split.

| Regime   | Contest decided by         | Surplus split                                |
|:---------|:--------------------------|:---------------------------------------------|
| FIFO     | Network propagation speed | 100% to bot; minimum fee to network          |
| This CIP | Fee bid                   | Split between bot profit and network revenue  |

Under FIFO, the advantage goes to infrastructure: co-location with block producers, dedicated relay
networks, optimized propagation paths. These are capital-intensive, opaque advantages that retail
users cannot match. A retail user and a bot submitting at the same instant will not arrive at the
same set of nodes — the bot's transaction propagates faster because the bot has invested in topology.
The contest is decided before the user's transaction even arrives.

This CIP replaces that infrastructure race with a fee auction. A retail user cannot deploy a global
relay network, but they can overpay by 5 ADA — and as the retail section above explains, that blunt
instrument is often sufficient because bots penny-pinch to preserve margins and can cheaply retry on
the next continuing UTxO. Fee bidding democratizes access to contested resources by converting the
contest from one where only infrastructure matters to one where willingness to pay matters.

The extraction itself remains non-adversarial: it cannot worsen any user's execution, the limit
order creator receives exactly the price they specified, and the bidding war converts extractable
value into fee revenue for the network. The total MEV is unchanged. What changes is who captures it
and through what mechanism — from topology-advantaged bots keeping the full surplus, to a
permissionless auction that redirects a portion into the treasury and staking rewards.

### Probabilistic guarantees are sufficient

Cardano does not have a single, global mempool. Each node maintains its own local set of pending
transactions. When two transactions conflict, different nodes may hold different ones. Paying a
higher fee does not guarantee victory — it increases the probability.

The mechanism is straightforward: whenever a node holding the lower-fee transaction hears about the
higher-fee one, it switches. The higher-fee transaction spreads across the network, displacing its
competitor node by node. By the time a block producer selects transactions for the next block, the
higher-fee transaction is more likely to be in its mempool — but not certain to be.

This probabilistic nature is a feature, not a limitation. A deterministic guarantee would require a
single global ordering authority — a centralizing force. Probabilistic resolution still enables
rational decision-making: a participant who consistently pays more than their competitors will
consistently win more contests, and can model their expected success rate based on network topology
and competitor behavior. Over many contests, the law of large numbers ensures that the fee signal
is reliable even though any individual outcome is uncertain.

The effectiveness of the fee signal scales with adoption. Each node that adopts the policy benefits
unilaterally — it earns more fees from contested UTxOs by always holding the higher-fee transaction.
As adoption increases, the network-wide probability of the higher-fee transaction winning rises
monotonically. There is no critical threshold below which the mechanism fails; there is only a
gradient of increasing effectiveness.

## Specification

**The following should be adopted as the default mempool behavior.**

### Scope

This CIP modifies only the **mempool transaction admission policy**. It does not modify:

- Ledger validation rules
- Fee calculation formulas
- Block construction algorithms
- Transaction format or structure

Cardano already permits fee overpayment — a transaction may include any amount above the required
minimum fee. This CIP leverages that existing capability.

### Conflict detection

Two transactions **conflict** if the spent inputs of either overlap with the spent inputs or
reference inputs of the other. Formally, transactions `A` and `B` conflict if and only if:

```
spentInputs(A) ∩ allInputs(B) ≠ ∅   ∨   spentInputs(B) ∩ allInputs(A) ≠ ∅
```

where `spentInputs(T)` is the set of UTxO references consumed by transaction `T`, and
`allInputs(T) = spentInputs(T) ∪ referenceInputs(T)` includes both consumed and referenced UTxOs.

Two transactions that both *reference* the same UTxO without spending it do not conflict — they can
coexist in the same block regardless of ordering. A conflict arises only when at least one
transaction *spends* a UTxO that the other spends or references.

### Replacement rule

When a node receives a new transaction `B`, and its mempool already contains a transaction `A` such
that `A` and `B` conflict:

Let `evicted(A)` denote `A` together with all transactions in the mempool that transitively depend
on `A`'s outputs (its **descendants**). Evicting `A` necessarily evicts every descendant, because
their inputs would become invalid.

- **If `fee(B) > totalFee(evicted(A)) + delta`:** Evict `A` and all its descendants from the
  mempool. Admit `B`.
- **Otherwise:** Reject `B`. Retain `A` and its descendants.

The `delta` term is a **minimum replacement increment** that prevents spam replacements. It is
defined as:

```
delta = minFee(B)
```

where `minFee(B)` is the standard minimum fee for transaction `B` as defined by the current protocol
parameters (i.e., the same formula the ledger uses to determine whether a transaction's fee is
sufficient). The delta covers the full cost that the replacement imposes on the network: bandwidth
for propagation and CPU/memory for script validation. The evicted transactions'
propagation and execution costs are already covered by the fee sum requirement: since `fee(B)` must
exceed the total fees of all evicted transactions, and those fees were already sufficient to
compensate for their costs, no separate term is needed. See the Rationale section for a full
discussion of the delta design.

### Multi-conflict replacement

If `B` conflicts with multiple mempool transactions `A₁, A₂, ..., Aₙ`, then `B` must pay strictly
more than the **sum** of all evicted transactions' fees (each conflicting transaction plus its
descendants), plus the replacement delta:

```
fee(B) > totalFee(evicted(A₁)) + totalFee(evicted(A₂)) + ... + totalFee(evicted(Aₙ)) + delta
```

where `delta = minFee(B)` as defined above.

The mempool invariant guarantees that no two co-resident transactions conflict with each other — if
they did, the conflict would have been resolved at admission time. This means all the transactions
that `B` would evict are mutually compatible: they could all be included in the same block. The
network's opportunity cost of admitting `B` is the total fee revenue from all of them, not just the
most expensive one. The sum rule captures this correctly.

### Evicted transaction behavior

When a transaction is evicted due to replacement, it is simply dropped. It is not re-propagated to
peers. The evicted transaction may still exist in other nodes' mempools across the network; whether
it survives depends on whether the replacement reaches those nodes before the next block.

From the user's perspective, detecting eviction is straightforward: monitor the UTxOs that the
submitted transaction attempted to spend. If those UTxOs are consumed by a different transaction
on-chain, the user's transaction was outbid. Wallets can surface this as a clear "outbid" status
rather than an opaque timeout.

> [!NOTE]
> Node implementations may optionally expose eviction events through their local transaction
> submission API. This would be a quality-of-life improvement for users but is not required by
> this CIP and can be implemented separately.

### Backward compatibility

This change is fully backward compatible:

- **Uncontested transactions** are completely unaffected. If no conflict exists, the transaction is
  admitted under standard FIFO rules as before.
- **Existing transactions** that pay minimum fees continue to work. They are only at risk of
  eviction if a conflicting transaction paying higher fees arrives — which is the intended behavior.
- **No transaction format changes.** Fee overpayment is already supported by the ledger.
- **No consensus changes.** Block validity rules are unchanged. This is purely a mempool policy.

Nodes that do not adopt the new policy will continue to operate correctly. They will resolve
conflicts via FIFO, foregoing the fee-priority optimization. Each node benefits unilaterally from
adopting the policy, creating a natural incentive for organic adoption without requiring coordinated
activation.

## Rationale: How does this CIP achieve its goals?

### Fee comparison metric: absolute fee vs. fee rate

The replacement rule uses **absolute fee** (total lovelace paid) rather than **fee rate** (fee per
byte). This is the recommended approach, but the tradeoffs are worth examining since block
conditions may evolve.

**When do the two metrics differ?**

The metrics agree when competing transactions are roughly the same size — the transaction paying
more in total also pays more per byte. They diverge when transaction sizes differ significantly:

| Scenario | Tx A (incumbent) | Tx B (challenger) | Absolute fee winner | Fee rate winner |
|:---------|:-----------------|:------------------|:--------------------|:---------------|
| Similar size | 500 bytes, 0.5 ADA | 520 bytes, 0.8 ADA | B | B |
| Different size | 2000 bytes, 1.0 ADA | 500 bytes, 0.6 ADA | A | B |

In the second scenario, the two metrics give opposite answers. Absolute fee keeps the 1.0 ADA
transaction. Fee rate keeps the 0.6 ADA transaction because its per-byte efficiency is higher.

**The case for absolute fee.**

Conflict resolution is a binary choice: exactly one of two mutually exclusive transactions
survives, and the network earns whichever fee the survivor pays. Fee rate's advantage — that
freed-up space can be filled with other revenue — depends on blocks being consistently full. When
they are not, the freed space generates no revenue and the network simply earns less. On Cardano
today, blocks are typically not full, so absolute fee produces more revenue in the common case.

Absolute fee also avoids penalizing users for transaction size, which is largely outside their
control. Two users may value a UTxO equally, but one holds fragmented wallet UTxOs requiring more
inputs. Fee rate would penalize that user for an accident of wallet state, not a difference in
willingness to pay.

**The case for fee rate.**

If Cardano blocks become consistently full in the future, fee rate becomes more compelling. In a
full-block regime, every byte of block space has an opportunity cost — the revenue from the next
best transaction that could have used it. Fee rate captures this opportunity cost; absolute fee
does not. A large transaction that wins every mempool conflict on absolute fee could be
systematically deprioritized at block construction time if its fee rate doesn't justify the space,
creating a disconnect between mempool and block outcomes.

**Recommendation.**

This CIP recommends absolute fee for two reasons. First, it is the correct metric for Cardano's
current operating conditions. Second, conflict resolution and block construction are separate
stages with separate optimization criteria — the mempool asks "which transaction should survive?"
(binary choice → absolute fee) while the block producer asks "which transactions should I pack?"
(knapsack problem → fee rate). Using different metrics at different stages is not a conflict; it is
each layer using the metric appropriate to its purpose.

If Cardano's block utilization changes materially, the fee comparison metric can be revisited
without modifying any consensus rules — it is a local mempool policy parameter.

### Minimum replacement delta

Each replacement imposes real costs on the network. There are two: the wasted propagation of the
evicted transactions (which the network already downloaded, validated, and forwarded, but whose fees
will never be collected) and the new propagation of the replacement transaction. Without a minimum
increment, an attacker could spam replacements at +1 lovelace, imposing these costs for negligible
economic commitment.

The delta only needs to cover the *second* cost — propagating B. The first cost — the wasted
propagation of evicted transactions — is already covered by the fee sum requirement. The replacement
rule requires `fee(B) > totalFee(evicted) + delta`, and the total evicted fees are at least the sum
of each evicted transaction's minimum fee (which covered its propagation and execution costs). So
B's fee already exceeds the evicted transactions' costs before the delta is even added. The delta
therefore compensates only for the genuinely new burden: downloading, validating, and propagating B
itself.

The delta is defined as `minFee(B)` — the standard minimum fee for B as computed by the existing
protocol parameters. This reuses the ledger's own cost model rather than introducing new parameters.
The minimum fee formula already accounts for the full burden a transaction imposes: bandwidth
(via the size-based term) and CPU/memory (via the execution unit terms). Using it directly ensures
that the replacement increment scales correctly with transaction complexity — a script-heavy
replacement requires a proportionally larger increment, reflecting the real cost it imposes on every
validating node.

In the multi-conflict case, the same logic applies at scale. The total evicted fee sum already
includes each evicted transaction's minimum fee (both directly conflicting transactions and their
descendants), which already covered each transaction's propagation and execution costs. The delta
adds only B's costs because B is the only transaction whose costs are not yet accounted for.

**Magnitude.** For a typical 500-byte transaction with no scripts, the delta is approximately
0.18 ADA (the standard minimum fee). For a script-heavy transaction consuming 10 billion ExUnit
steps and 5 million ExUnit memory, the delta rises to approximately 2.8 ADA. This scaling is
desirable: replacing a computationally expensive transaction should require a proportionally larger
increment, reflecting the real cost each replacement imposes on every validating node.

> [!IMPORTANT]
> The delta is a mempool policy default, not a consensus rule. Node operators can adjust it without
> a hard fork.

## Path to Active

### Acceptance Criteria

- [ ] The Cardano node's default mempool policy implements conflict-based fee priority as specified.
- [ ] Uncontested transactions are demonstrably unaffected by the policy change.
- [ ] At least one testnet demonstrates the replacement behavior under simulated UTxO contention.

### Implementation Plan

- [ ] Implement the conflict detection, fee-comparison, and delta logic in the Cardano node's
  mempool admission module.
- [ ] Add configurable parameters allowing node operators to enable/disable the policy and adjust
  the replacement delta during the rollout period.
- [ ] Deploy to a public testnet for community testing and validation.
- [ ] Gather feedback from stake pool operators, wallet developers, and DeFi protocol teams.
- [ ] Merge as the default mempool policy in a subsequent node release.

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/).
