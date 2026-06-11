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

### FIFO is not fair

On eUTxO, each DeFi intent (e.g., a limit order) lives at its own UTxO. When multiple parties want
to interact with the same UTxO, their transactions conflict and only one can be included in a block.

Under the current mempool policy, conflicts are resolved by arrival order: whichever transaction
reaches a node's mempool first is kept, and later arrivals are rejected. **But arrival order is not
neutral.** The advantage goes to infrastructure: co-location with block producers, dedicated relay
networks, and optimized propagation paths. These are capital-intensive, opaque advantages that
retail users cannot match. If a retail user and a bot submit conficting transactions at the same
time, the bot's transaction will propagate faster because the bot has invested in topology.

*FIFO is rigged against retail.*

### FIFO leaves money on the table

Every contested UTxO has multiple parties who want it. Some would pay substantially more than others
to secure it. But under FIFO, there is no mechanism to express that willingness — the winner is
whoever propagated fastest, and they pay the minimum fee regardless. The losers, no matter how much
more they would have paid, are simply rejected.

Consider two bots competing for the same mispriced limit order. Bot A found an arbitrage route worth
15 ADA in profit; Bot B found one worth 5 ADA. Bot A would happily pay a 5 ADA fee to guarantee the
fill — it still profits 10 ADA. But under FIFO, Bot A has no way to outbid Bot B. If Bot B
propagated faster, it wins and pays the minimum 0.5 ADA fee. The network collects 0.5 ADA instead of
5. The 4.5 ADA difference is value the network simply forfeits.

### The solution: a per-UTxO auction

The correct mechanism for allocating a scarce resource to the party who values it most is an
auction. When two transactions conflict over the same UTxO, the mempool runs a trivial one: keep the
higher-fee transaction, drop the lower-fee one. The winner pays their bid to the network via
transaction fees. The loser's transaction fails cleanly — on eUTxO, a transaction that references a
spent UTxO simply fails Phase 1 validation at no cost to the submitter. It does not execute with a
worse outcome.

Returning to the earlier example: Bot A, with 15 ADA of profit at stake, submits a transaction
paying a 5 ADA fee. Bot B's 0.5 ADA transaction is already in the mempool, but the node sees that
Bot A's fee is higher and replaces it. Bot A wins, the network collects 5 ADA instead of 0.5, and
the 4.5 ADA difference flows into the treasury and staking rewards. The bot that valued the resource
more wins, and the network shares in the profit.

What makes this auction local — and unlike fee markets on any other chain — is that eUTxO contention
is structurally attributable. Every transaction declares exactly which UTxOs it will consume, so
when two transactions conflict, the contested resource is identified and the conflict is confined.
Only the parties competing for that specific UTxO bear any cost. **Everyone else is unaffected.**

Fee markets on other chains are addressing a different scarcity problem — total demand exceeding
block capacity — and their fee markets are necessarily global because congestion cannot be
attributed to specific resources:

| Scarcity problem       | Mechanism         | Fee impact scope                     |
|:-----------------------|:------------------|:-------------------------------------|
| Block space (Bitcoin)  | RBF               | Everyone in that block               |
| Block space (Ethereum) | EIP-1559          | Everyone on the network              |
| UTxO contention        | This CIP          | Only parties competing for that UTxO |

This CIP is the first fee market to exploit eUTxO's structural attributability.

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

### Replacement rule

When a node receives a new transaction `B`, and its mempool already contains transactions
`A₁, A₂, ..., Aₙ` that each conflict with `B`:

Let `descendants(A)` denote all transactions in the mempool that transitively depend on `A`'s
outputs. Evicting `A` necessarily evicts every descendant, because their inputs would become invalid.
Define the **chain cost** of a conflicting transaction as:

```
chainCost(A) = fee(A) + totalMinFee(descendants(A))
```

where `fee(A)` is the fee paid by the directly contested transaction, and
`totalMinFee(descendants(A))` is the sum of *minimum* fees for each of its evicted descendants
rather than their actual fees — see the Rationale section for why.

The replacement rule is:

```
fee(B) > minFee(B) + chainCost(A₁) + ... + chainCost(Aₙ)
```

- **If the inequality holds:** Evict `A₁, ..., Aₙ` and all their descendants. Admit `B`.
- **Otherwise:** Reject `B`.

where `minFee(B)` is the minimum fee for `B` as defined by the current protocol parameters (i.e.,
the same formula the ledger uses to determine whether a transaction's fee is sufficient).

> [!IMPORTANT]
> The current Cardano mempool does not track dependency relationships between transactions. This CIP
> likely requires auxiliary mempool data structures so that descendants can be identified and
> evicted efficiently. The details are left to implementors.

### Evicted transaction behavior

When a transaction is evicted due to replacement, it is simply dropped. It is not re-propagated to
peers. The evicted transaction may still exist in other nodes' mempools across the network; whether
it survives depends on whether the replacement transaction reaches those nodes before the next
block.

Node implementations may optionally expose eviction events through their local transaction
submission API. This would be a major quality-of-life improvement, but it is not required by this
CIP.

### Backward compatibility

This change is fully backward compatible:

- **Uncontested transactions** are completely unaffected. If no conflict exists, the transaction is
  admitted under standard FIFO rules as before.
- **Existing transactions** that pay minimum fees continue to work. They are only at risk of
  eviction if a conflicting transaction paying higher fees arrives — which is the intended behavior.
- **No transaction format changes.** Fee overpayment is already supported by the ledger.
- **No consensus changes.** Block validity rules are unchanged. This is purely a mempool change.

Nodes that do not adopt the new policy will continue to operate correctly — they will simply resolve
conflicts via FIFO. The mechanism's effectiveness scales with adoption: the more nodes that
implement this auction, the higher the probability that the higher-fee transaction survives to block
inclusion.

> [!IMPORTANT]
> The majority of nodes need to adopt this CIP for it to work. If bidding higher does not
> predictably result in a transaction being included, people will not bid. See the Rationale section
> on probabilistic guarantees for a fuller discussion.

## Rationale: How does this CIP achieve its goals?

### Probabilistic guarantees are sufficient

Cardano does not have a single, global mempool. Each node maintains its own local set of pending
transactions. When two transactions conflict, different nodes may hold different ones. Paying a
higher fee does not guarantee victory, but it does increases the probability.

The mechanism is straightforward: whenever a node holding the lower-fee transaction hears about the
higher-fee one, it switches. The higher-fee transaction spreads across the network, displacing its
competitor node by node. By the time a block producer selects transactions for the next block, the
higher-fee transaction is more likely to be in its mempool — but not certain to be.

This probabilistic nature is "good enough". A deterministic guarantee would require a single global
ordering authority — a centralizing force. Probabilistic resolution still enables rational
decision-making: a participant who consistently pays more than their competitors will consistently
win more contests, and can model their expected success rate based on network topology and
competitor behavior. Over many contests, the law of large numbers ensures that the fee signal is
reliable even though any individual outcome is uncertain.

This mechanism requires a minimum viable level of network-wide adoption. If paying a higher fee does
not reliably result in transaction inclusion, participants will stop bidding. The exact threshold is
hard to quantify, but a reasonable estimate is that a majority of nodes — and especially block
producers — need to adopt the policy before the fee signal becomes trustworthy enough to sustain a
functioning market.

Adoption is collectively incentivized: the more nodes that adopt the policy, the more consistently
the higher-fee transaction wins inclusion, and the more total fee revenue flows into the treasury
and staking rewards for the entire network.

### Last-minute sniping is self-defeating

A natural concern is that bots will hold their transactions back, attempting to submit just before a
block is produced — hoping to snipe the contested UTxO without giving competitors time to respond.
If most participants adopted this strategy, the result would be bursts of network activity
concentrated right before each block, with little bidding in between.

This strategy is self-defeating because of two properties that combine to make last-minute
submission unreliable.

First, Cardano's slot leader schedule is private. Only the elected slot leader knows it is their
turn to produce a block. No other participant knows which node to target or when the next block will
arrive.

Second, the mempool is sharded — each node maintains its own local set of pending transactions.
Because the block producer's identity is unknown, a transaction cannot be sent directly to them. It
must propagate through the peer-to-peer network, hopping node by node until it reaches the producer
by chance. This takes time, and the propagation path is not deterministic.

Together, these properties mean a bot that waits has no way to predict whether its transaction will
reach the next block producer before a competitor's does. The late submitter is gambling on
propagation luck against an opponent who is already established across the network. By contrast, the
early submitter's transaction is already sitting in mempools and very likely already in the unknown
producer's. A late-arriving transaction must both reach the producer in time *and* pay a higher fee
to displace the incumbent.

The optimal strategy is therefore to establish position early and force competitors to pay the
replacement premium — not to wait for a moment that cannot be predicted.

### Descendants use minimum fee, not actual fee

The replacement formula charges descendants at their required *minimum* fee rather than their actual
fee. This is a deliberate design choice grounded in auction theory: each contested UTxO should be
priced by its own independent auction, not bundled with unrelated activity.

**Actual fees misprice demand.** This fee market prices contention for a *specific UTxO*. Descendant
transactions interact with that continuing UTxO's future states — distinct resources that should be
priced by their own auctions when contention arises. Requiring a challenger to outbid fees paid for
unrelated resources is not pricing demand for the contested UTxO — it is creating a market
inefficiency by conflating independent goods.

**Bundling auctions reduces revenue.** The entire premise of this CIP is that eUTxO enables
per-resource fee markets. Counting descendant fees at actual value merges independent auctions into
one, undermining that property. Consider a continuing UTxO that cycles four times. Without chaining
in the fee comparison, each cycle gets its own auction. If each attracts a 15 ADA bid, the network
earns 60 ADA. With chaining, all four cycles are bundled under a single replacement threshold. A
chain paying 20 ADA total across all four beats out individual 15 ADA bids on each — the network
earns 20 ADA instead of 60. Separate auctions over independent resources yield at least as much
total revenue as bundled ones. This is a standard result in auction theory, and continuing UTxOs are
the dominant case for DeFi contention.

> [!IMPORTANT]
> Bots are likely the dominant entity building transaction chains. They can quickly detect the root
> of a chain has been replaced and rebuild against the new chain. No revenue is actually lost by
> replacing the current transaction chain. Even if the chain is slow to rebuild, those UTxOs will
> still be available and waiting for new bids. The "cost" of eviction is reconstruction effort; not
> permanent revenue loss.

**Actual fees enable pinning and disadvantage retail.** Under a rule that counts descendant fees at
actual value, a transaction can be made artificially expensive to replace by attaching descendants
that inflate the replacement threshold. Bots can build up a chain within seconds of the first
transaction landing in the mempool — retail users cannot. Using actual fees for descendants would
allow bots to pin a contested transaction simply by being first and chaining on top of it,
converting a speed advantage into an insurmountable fee barrier. This recreates the unfairness that
FIFO already suffers from. Charging descendants at minimum fee neutralizes pinning entirely — the
only way to defend a position is to raise the fee on the directly contested transaction, which is
exactly the behavior the auction should incentivize. No depth caps, topology restrictions, or
cluster tracking are needed because the design choice itself eliminates the attack vector.

**Why consider descendant fees at all?** The minimum fee charge covers the real cost eviction
imposes on the network: the bandwidth, CPU, and memory already spent validating and propagating
transactions whose fees will never be collected. This protects against DoS while minimizing any
distortion of the auctions.

### Minimum bid increment

The replacement formula requires `fee(B) > minFee(B) + chainCost(A₁) + ...`. The `minFee(B)` term
is the minimum bid increment — the challenger must not only outbid the incumbents, but exceed them
by at least its own minimum fee. This prevents an attacker from spamming replacements at +1
lovelace, forcing every node on the network to download, validate, and propagate a new transaction
for negligible economic commitment.

The increment is `minFee(B)` rather than a fixed constant because the ledger's minimum fee formula
already prices the real burden a new transaction imposes. A script-heavy replacement transaction
costs the network more to process, so it requires a proportionally larger increment.

### Fee comparison metric: total fee vs. fee rate

The replacement rule relies on **total fee** rather than **fee rate** as seen on Bitcoin. 

**When do the two metrics differ?**

The metrics agree when competing transactions are roughly the same size — the transaction paying
more in total also pays more per byte. They diverge when transaction sizes differ significantly:

| Scenario       | Tx A (incumbent)    | Tx B (challenger)   | Total fee winner | Fee rate winner |
|:---------------|:--------------------|:--------------------|:-----------------|:----------------|
| Similar size   | 500 bytes, 0.5 ADA  | 520 bytes, 0.8 ADA  | B                | B               |
| Different size | 2000 bytes, 1.0 ADA | 500 bytes, 0.6 ADA  | A                | B               |

In the second scenario, the two metrics give opposite answers. Total fee keeps the 1.0 ADA
transaction. Fee rate keeps the 0.6 ADA transaction because its per-byte efficiency is higher.

**The case for total fee.**

Conflict resolution is a binary choice: exactly one of two mutually exclusive transactions
survives, and the network earns whichever fee the survivor pays. Fee rate's advantage — that
freed-up space can be filled with other revenue — depends on blocks being consistently full. When
they are not, the freed space generates no revenue and the network simply earns less. On Cardano
today, blocks are typically not full, so total fee produces more revenue in the common case.

**The case for fee rate.**

If Cardano blocks become consistently full in the future, fee rate becomes more compelling. In a
full-block regime, every byte of block space has an opportunity cost — the revenue from the next
best transaction that could have used it. Fee rate captures this opportunity cost; total fee does
not. A large transaction that wins every mempool conflict on total fee could be systematically
deprioritized at block construction time if its fee rate doesn't justify the space, creating a
disconnect between mempool and block outcomes.

**Recommendation.**

This CIP recommends total fee. It generates more revenue under Cardano's current operating
conditions where blocks are not consistently full. If block utilization changes materially, the
metric can be switched to fee rate without a hard fork — it's just a local mempool configuration.

### Composability with the application-layer contention market

DeFi order books provide a separate contention management layer at the application level: users
choose *which* order to interact with, and can pay a price premium to target a less contested one.
Choosing a limit order priced 3% above market may reduce the number of competing parties from dozens
to zero.

This CIP adds a second layer underneath. Together, they form a two-dimensional contention market:

| Dimension     | Mechanism                   | What it controls                               |
|:--------------|:----------------------------|:-----------------------------------------------|
| Price premium | Choose a worse-priced order | Probability of contention occurring            |
| Fee premium   | Pay higher transaction fees | Probability of winning *if* contention occurs  |

The first dimension thins the field. The second resolves whatever competition remains. Combined,
they give users fine-grained control over their transaction's chance of success.

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
let that UTxO go and grab the next one for a fraction of the cost. The contest resets after each
usage.

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

MEV protection on Cardano is handled at the dApp level, not the mempool level. DApps today fall
into two broad categories, and neither is exposed to MEV by this CIP.

**Batcher-based dApps** (most contemporary dApps) manage contention through off-chain batchers that
sequence user intents and submit a single transaction per batch. Contention for individual UTxOs is
resolved within the batcher's own pipeline. *These dApps are unaffected by this CIP.*

**Direct-interaction dApps** (p2p dApps) have users submit transactions that consume UTxOs directly.
These dApps leverage eUTxO's determinism to eliminate MEV by construction: every transaction
declares its exact inputs and outputs before signing, so there is no shared mutable state an
adversary could manipulate to alter another user's outcome. Sandwich attacks are structurally
impossible. *This group is the target audience for this CIP, and they are already MEV-safe.*

This CIP changes how conflicts among already-safe transactions are resolved; it does not alter the
MEV properties of either category. 

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
