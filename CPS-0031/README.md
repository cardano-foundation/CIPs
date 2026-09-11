---
CPS: 31
Title: Prioritising Urgent Transactions
Category: Consensus
Status: Open
Authors:
  - Will Gould <will.gould@iohk.io>
  - Polina Vinogradova <polina.vinogradova@iohk.io>
  - fallen-icarus <modern.daidalos@gmail.com>
Proposed Solutions:
  - CIP-0183 | Conflict-Based Fee Priority in Mempool: https://github.com/cardano-foundation/CIPs/tree/master/CIP-0183
Discussions: 
   - Original pull request: https://github.com/cardano-foundation/CIPs/pull/1194
Created: 2026-04-07
License: CC-BY-4.0
---

## Abstract

During periods of congestion, high-urgency transactions lose value when they cannot obtain timely inclusion. A protocol-recognised urgency signal could help preserve more transaction value during congestion, especially for transactions whose value is highly delay-sensitive. Urgency may also be causal rather than temporal: a transaction may need inclusion before a conflicting transaction consumes a UTxO it depends on, which can happen even when block space is plentiful.

Candidate solutions should be evaluated by how they handle prioritising high-urgency transactions, and by how they affect ordinary and low-urgency users during sustained congestion. Candidate solutions may address temporal urgency, causal urgency, or both.


## Problem

Cardano does not currently provide a protocol-enforced way for a user or application to signal transaction priority.

Many transactions are time-sensitive: their value to the submitter depends on timely inclusion. A liquidation that lands several slots late may fail to recover the full loan value. An oracle update delayed behind unrelated traffic leaves a stale price on-chain. A loan collateral top-up submitted before a margin call but confirmed after it is worthless. In each case, delay destroys value that timely inclusion could have preserved.

During congestion, these transactions compete for block space on equal terms with traffic that has no particular time sensitivity. The protocol treats all valid transactions alike with respect to urgency: there is no way for a transaction to express that it is urgent, and no mechanism for block producers to commit to honouring such a signal. Urgent and non-urgent transactions queue together, and inclusion order is determined by factors opaque to the submitter.

Urgency is not only a matter of congestion. Two transactions may both be valid against the current ledger state while spending the same UTxO, so that only one can be included. Today the outcome can depend on transaction propagation and which competing transaction a node receives and accepts first, regardless of how much either submitter values precedence. Spare block capacity does not resolve this competition.

Users and protocols lose value to avoidable delay. Block producers leave value uncaptured because users cannot express how much timely inclusion is worth to them. Additionally, the absence of a legitimate priority channel creates pressure toward off-chain arrangements that undermine the permissionless properties of the network.

### Explored Alternatives

From stakeholder interviews at Buidler Fest #3:

* Fee pre-escalation: Transactions can overpay fees, but with no protocol-enforced prioritisation for overpaying transactions

Tried. Produced modest improvement in moderate congestion. Fails under systemic congestion because SPOs are not committed to sort by fee. Bidding is also calibrated blind; there is no standardised mempool signal to know where you stand.

* Multi-relay submission: Where the node is connected to multiple SPO relays to increase the likelihood that the transaction reaches the next block producer quickly

Deployed as standard infrastructure. Improves latency-to-mempool, not confirmation ordering. Once in the queue, the transaction competes equally with everything else.

* Private SPO arrangements: 

Explored and rejected. Even agreements with major SPOs yield next-block probability insufficient for liquidations. More importantly, this produces a worse outcome than a formal mechanism: an opaque, permissioned, off-chain priority market accessible only to well-capitalised incumbents.


## Use Cases

1. **Liquidations**

   **Scenario:** A lending protocol needs to liquidate an unsafe position before collateral value moves further.

   **Example:** A liquidation transaction is delayed during unrelated minting congestion and is included only after the liquidation opportunity has degraded.

   **Who loses today:** Depositors, liquidity providers, and any reserve, insurance, or backstop mechanism that absorbs losses.

2. **Oracle updates**

   **Scenario:** An oracle publisher needs to update a price feed during market volatility.

   **Example:** A stale price remains on-chain because the update competes with non-urgent traffic.

   **Who loses today:** Protocols consuming the stale feed, users trading against incorrect prices, and systems relying on time-dependent parameters.

3. **Collateral top-ups and position protection**

   **Scenario:** A borrower tries to add collateral or repay debt to avoid liquidation.

   **Example:** The user submits a corrective transaction in time, but it is delayed behind unrelated congestion.

   **Who loses today:** Borrowers who attempted to act, and protocols that benefit when users can manage risk before liquidation becomes necessary.

4. **Deadline-sensitive user transactions**

   **Scenario:** A user needs inclusion before a known deadline, such as a mint window, claim period, protocol deadline, or liquidation threshold.

   **Example:** The transaction is valid and submitted before the deadline but confirms too late.

   **Who loses today:** Users who cannot express that deadline sensitivity in a protocol-recognised way.

5. **Competing arbitrage transactions**

   **Scenario:** Multiple traders attempt to capture the same arbitrage opportunity.

   **Example:** Two transactions spend the same liquidity UTxO to exploit a price discrepancy. Inclusion of either transaction invalidates the other as submitted, even when there is enough block space for both. Each trader values inclusion before the competing transaction.

   **Who loses today:** Traders who lose the opportunity and cannot express the value of precedence through a protocol-recognised signal.

6. **Acceptance of standing offers**

   **Scenario:** A user wants to accept an available loan offer or directly execute a limit order.

   **Example:** Two borrowers attempt to accept the same standing loan offer, or two traders attempt to fill the same directly executable limit order. Only one transaction can consume the offer UTxO. The opportunity disappears for the other user as soon as the competing transaction is included, regardless of congestion.

   **Who loses today:** Users whose acceptance loses the race, and users facing pressure to invest in faster submission infrastructure or obtain privileged access to execution.

7. **Registration of unique names or handles**

   **Scenario:** Users compete to register the same available name in an application that permits direct registration and enforces uniqueness on-chain.

   **Example:** Two users submit conflicting claims for the same handle. Once one registration succeeds, the other cannot obtain that handle. The urgency comes from competing for an exclusive opportunity.

   **Who loses today:** Users who cannot express the value of precedence through a public, permissionless mechanism and whose access instead depends on submission speed or application-level intermediaries.


## Goals

1. **Reduce avoidable losses from delay or lost precedence.** Urgent transactions should have a way to avoid value-destroying delay when competing with traffic that has no time sensitivity, or to obtain precedence when competing with a conflicting transaction. Note that where transactions conflict over the same UTxO, precedence can change who captures an opportunity without increasing aggregate retained value, so solutions (or parts of solutions) targeting UTxO conflict need not improve globally retained value. Their contribution is in replacing an arrival-order race with a permissionless, predictable rule, as in goals 2 and 3.

From stakeholder interviews during Buidler Fest #3, hosted by Carlos Lopez De Lara:

2. **Permissionless access.** Priority must be available to anyone willing to fulfil the necessary prerequisites, not negotiated through relationships or in private arrangements.

3. **Predictability over raw speed.** The signal predictably improves access to timely inclusion, or precedence over conflicting transactions, rather than only modestly improving odds. This includes making the wait more consistent for high-urgency transactions.

### Constraints

1. **Ledger determinism.** To prevent attacks making use of Phase 2 validation, the urgency signal (and any related changes to on-chain transaction processing) should not compromise ledger determinism.

2. **On-chain record.** The rules of urgency signalling should be publicly specified, and any cost paid should be recorded on-chain, preferably with the pricing rules in ledger logic. This ensures everyone has equal access to the rules of signalling, and that anyone can verify what was paid.

3. **Censorship resistance.** Candidate solutions should preserve censorship resistance and must evaluate whether urgency signalling creates new opportunities for selective exclusion or preferential treatment.

4. **Linear-Leios compatibility.** Candidate solutions must be compatible with linear-Leios.

### Non-Goals

Guaranteed inclusion of every urgent transaction

Guaranteed precedence over every competing transaction

Guaranteed retention of value for urgent transactions

Elimination of congestion

Any specific pricing mechanism


## Open Questions

How can whatever protocol-level commitments are decided upon be enforced or incentivised?

How should updated fee or priority quotes be propagated?

How would a priority signal interact with the linear-Leios block structure?

Can we achieve our goals without starving low-urgency users of block space (especially in the context of linear-Leios)?

How can we retain fee quote validity across repricing intervals?

What information is leaked when a transaction signals urgency?

What MEV opportunities are created or amplified by public urgency signals?

## Copyright

This CPS is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
