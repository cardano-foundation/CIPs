---
CPS: 31
Title: Prioritising Urgent Transactions
Category: Consensus
Status: Open
Authors:
  - Will Gould <will.gould@iohk.io>
  - Polina Vinogradova <polina.vinogradova@iohk.io>
Proposed Solutions: []
Discussions: 
   - Original pull request: https://github.com/cardano-foundation/CIPs/pull/1194
Created: 2026-04-07
License: CC-BY-4.0
---

## Abstract

During periods of congestion, high-urgency transactions lose value when they cannot obtain timely inclusion. A protocol-recognised urgency signal could help preserve more transaction value during congestion, especially for transactions whose value is highly delay-sensitive.

Candidate solutions should be evaluated by how they handle prioritising high-urgency transactions, and by how they affect ordinary and low-urgency users during sustained congestion.


## Problem

Cardano does not currently provide a protocol-enforced way for a user or application to signal transaction priority.

Many transactions are time-sensitive: their value to the submitter depends on timely inclusion. A liquidation that lands several slots late may fail to recover the full loan value. An oracle update delayed behind unrelated traffic leaves a stale price on-chain. A loan collateral top-up submitted before a margin call but confirmed after it is worthless. In each case, delay destroys value that timely inclusion could have preserved.

During congestion, these transactions compete for block space on equal terms with traffic that has no particular time sensitivity. The protocol treats all valid transactions alike with respect to urgency: there is no way for a transaction to express that it is urgent, and no mechanism for block producers to commit to honouring such a signal. Urgent and non-urgent transactions queue together, and inclusion order is determined by factors opaque to the submitter.

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


## Goals

1. **Reduce value destroyed by avoidable delay.** Urgent transactions should have a way to avoid value-destroying delay when competing with traffic that has no time sensitivity.

From stakeholder interviews during Buidler Fest #3, hosted by Carlos Lopez De Lara:

2. **Permissionless access.** Priority must be available to anyone willing to fulfil the necessary prerequisites, not negotiated through relationships or in private arrangements.

3. **Predictability over raw speed.** The signal predictably improves access to timely inclusion, rather than only modestly improving odds. This includes a reduction in wait time variance for high-urgency transactions.

### Constraints

1. **Automatable semantics.** The urgency signal must be encodable in smart contract logic and readable by automated systems, not just manually configured.

2. **Censorship resistance.** Candidate solutions should preserve censorship resistance and must evaluate whether urgency signalling creates new opportunities for selective exclusion or preferential treatment.

3. **Linear-Leios compatibility.** Candidate solutions must target linear-Leios.

### Non-Goals

Guaranteed inclusion of every urgent transaction

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
