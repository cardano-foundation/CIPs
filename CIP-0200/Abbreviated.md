## Abstract

We propose two lanes by which a user can submit a transaction to a node: urgent and standard. Only urgent transactions can enter Ranking Blocks. Both urgent and standard transactions can enter Endorser Blocks. Nodes produce Ranking Blocks more frequently than Endorser Blocks, and a Ranking Block enters the chain immediately. When capacity and queue order permit, an urgent transaction can therefore enter an earlier Ranking Block instead of the later Endorser Block path. This creates an earlier inclusion opportunity, not a guarantee of earlier inclusion.

The ledger enforces the urgency signalling rule: every transaction in a valid Ranking Block must carry a fee that covers the urgent quote for that block. In simulation under severe congestion, the mechanism preserves more urgent-class transaction value than linear Leios with today's flat fee. Retained value means the modelled gross transaction value that remains at inclusion, before fees. Urgent-class retained value improved across most simulated loads. At light load, the mechanism slightly reduces overall retained value, because transactions on the standard path wait longer while Endorser Blocks fill. The Rationale gives exact figures.

## Motivation: Why is this CIP necessary?

Some transactions lose value when delayed, but users currently have no protocol-level way to signal that urgency.

Linear Leios introduces a new block type: the Endorser Block. Vanilla linear Leios uses this additional path only when traffic exceeds Ranking Block capacity. This proposal instead routes standard transactions through Endorser Blocks at every load. Endorser Blocks are slightly slower than Ranking Blocks, so latency variability increases. An urgency signal offsets this cost: it lets nodes allocate block space to serve users' intents.

While linear Leios significantly enhances throughput, Praos block (AKA Ranking Block) space will remain scarce. The SundaeSwap launch resulted in saturation of Praos blocks, so a similar event may result in saturation of RBs, so a motivating historical scenario has already occurred.

From CPS-0031:

> During periods of congestion, high-urgency transactions lose value when they cannot obtain timely inclusion. A protocol-recognised urgency signal could help preserve more transaction value during congestion, especially for transactions whose value is highly delay-sensitive.

> Candidate solutions should be evaluated by how they handle prioritising high-urgency transactions, and by how they affect ordinary and low-urgency users during sustained congestion.

<!-- PORTABILITY: once CPS-0031 (PR #1194) merges, repoint this at the repo-relative ../CPS-0031 -->

See [CPS-0031](https://github.com/cardano-foundation/CIPs/pull/1194) for more information.

We initially planned a mechanism based on full tiered pricing, then set it aside in favour of the two-lane design specified here. The Rationale section [Why not full tiered pricing?](#why-not-full-tiered-pricing) gives the comparison.

## Specification

The core of the design rests on a two-lane system:

* Urgent: transactions must offer to pay at least the urgent fee in order to be eligible for inclusion in a Ranking Block

* Standard: transactions offer to pay at least the standard fee in order to be eligible for inclusion to an Endorser Block

### What

#### Fees

Both lanes have dynamic fees, and each lane's fee is controlled independently. That means the standard fee can move when the urgent fee does not and vice versa.

Fee movement is determined by a rolling window of prior blocks. The urgent lane takes into account the previous 5 blocks, while the standard lane takes into account the previous 10. The urgent lane still receives a signal from Endorser Blocks: urgent transactions in an EB act as fill signal. Specifically, an RB's-worth (~90KB) of urgent transactions in an EB provides the equivalent signal to an actual RB full of urgent transactions.

The point at which dynamism activates is determined by the target utilisation value. This simply means a fill fraction. 

The urgent lane has a target utilisation of 0.5, meaning that if RBs are more than 50% full the price increases, and if they are below 50% the price decreases. 

The standard lane has a target utilisation of 0.75, meaning that if EBs are more than 75% full the price increases, and if they are below 75% the price decreases.

#### Block entry eligibility

An urgent transaction's fee must cover the urgent lane's fee at the time of block construction in order to enter an RB. If it does not, it can still enter an EB.

If a transaction in the mempool does not cover either fee at any point after admission, it should be evicted.

An urgent transaction may be put into an EB for any reason, for example if an RB is full of other urgent transactions or carries an EB certificate. In this case, the difference between the urgent fee price and the standard fee price will be refunded to an change account if specified.

#### Refunds

A transaction may specify, in a new field, an account. This account will be used for refunds.

Refunds can occur for one reason: A transaction's offered fee is higher than the current fee of the lane it ended up in.

This can occur in three cases:
* An urgent transaction is added to an EB instead of an RB, and the urgent fee price is higher than the standard fee price
* The transaction fee is higher than required as a buffer to price movement
* The transaction fee is higher than required because the price decreased

### How

#### Mempool

A proof has been written which shows that transactions can be re-ordered without requiring full revalidation under specified conditions. This proof allows us to maintain distinct "urgent" and "standard" portions of the mempool by shifting incoming urgent transactions to the back of the urgent queue, which is at the front of the standard queue.

So, when a priority transaction arrives, if it passes the conflict check, put it at the back of the priority portion of the queue, performing partial revalidation.

A transaction which conflicts with another transaction already in the mempool, for any reason, will not be admitted. This means that an urgent transaction cannot boot out a standard transaction it conflicts with.

When the information of a new block becomes available, evict all transactions whose offered fees don't satisfy the necessary requirement.

#### Node

When creating an RB that contains transactions, add transactions to the block in a FIFO manner from the urgent portion of the mempool.

When creating an EB, add transactions to it in a FIFO manner from the mempool.

#### Ledger

We add a new field to state the transaction's intended lane.

We add a new field for an optional refund account.

We extend the rules to check a tx's fee is appropriate for its block type.

We extend the rules to ensure the only transactions added to an RB are urgent.

If the tx has a refund account specified, refund unused fee portion.

Pricing information in is added to the LedgerState.

Pricing update logic maintains the pricing information.

An EB certificate is invalid is it carries less than 50% of the capacity of an RB, unless it's been 10 blocks since the last included EB certificate.

#### Plutus

New version. Scripts can see the lane and refund account but not the refund amount.

### Common misconceptions: clarified

* Refunds support two cases:
  * The transaction offers the urgent fee but ends up in an EB
  * The transaction offers headroom in its fee to reduce the risk of eviction due to price increases, but not all of that headroom is required at the time of inclusion
* The premium above the ordinary minimum fee goes to the treasury, so producers cannot earn it by favouring urgent transactions over EB certificates.
* Under the normal block-production policy, a ready, qualifying EB certificate takes precedence over a direct RB transaction payload, regardless of urgent backlog. Urgent backlog therefore does not defer that certificate under this policy. Tips paid directly to a producer could give it a reason to break this policy; see [Why not leave priority to the mempool?](#why-not-leave-priority-to-the-mempool).
* A transaction entering the urgent lane is eligible but not guaranteed to be included in an RB. If it instead enters an EB, it pays the standard quote at inclusion time, with the excess being refunded (assuming the transaction specifies a registered refund account).
* Each lane’s quote is a posted price calculated by its controller. A larger fee cap provides headroom against quote increases; under the reference FIFO policy, it does not buy an earlier queue position.
* The standard lane has its own controller; it is not derived from the urgent quote.
* A standard transaction is _never_ eligible to enter an RB, even if a produced RB would be otherwise empty.
* Both lanes are dynamically priced. This doesn't mean, however, that either lane will be priced higher than min fee all the time. Only once windowed utilisation exceeds the target (by default in our specification, 50% for the urgent lane and 75% for the standard lane) does the price increase; below the target, conversely, the price decreases again.
* Standard transactions may never enter RBs in order to make RB entry ledger enforceable, so as to eliminate bribery as a route into the urgent resource for transactions not offering the urgent fee
* A small portion of determinism is given up. If a transaction elects to use a refund account, certainty of collected fees is lost, as is certainty of that refund account's balance after transaction inclusion. This is a per-transaction choice.

### A note on linear Leios, as specified in CIP-0164

Not all transactions go through EBs in unmodified linear Leios as specified in [CIP-0164](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0164). CIP-0164 specifies the timing formula: `A certificate may only be included if RB' is at least 3×Lhdr+Lvote+Ldiff slots after RB` [in the chain inclusion section](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0164#step-5-chain-inclusion). In the [feasible protocol parameters](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0164#feasible-protocol-parameters) section, the CIP specifies an EB cooldown of 14 slots (meaning the next 13 slots after the announcing RB are too early to include that EB's certificate): `Total certificate inclusion delay:3×Lhdr+Lvote+Ldiff=3+4+7=14slots`.

With an RB production probability of 0.05 per slot, the probability of an EB surviving the cooldown is the probability that no RB is produced in the 13 slots following the RB that announced it:

`0.95^13 = ~51.33%`

That means there's a ~51.33% chance of an EB surviving the cooldown period, meaning, statistically, ~48.67% of blocks can be expected to be transaction-carrying RBs.