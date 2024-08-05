---
CPS: ?
Title: Full determinism of transactions is unnecessarily restrictive for DeFi
Status: Open
Category: Ledger
Authors:
    - Vladimir Kalnitsky <klntsky@gmail.com>
Proposed Solutions: []
Discussions:
    - https://github.com/cardano-foundation/CIPs/pull/?
Created: YYYY-MM-DD
License: CC-BY-4.0
---

<!-- Existing categories:

- Meta     | For meta-CIPs which typically serves another category or group of categories.
- Wallets  | For standardisation across wallets (hardware, full-node or light).
- Tokens   | About tokens (fungible or non-fungible) and minting policies in general.
- Metadata | For proposals around metadata (on-chain or off-chain).
- Tools    | A broad category for ecosystem tools not falling into any other category.
- Plutus   | Changes or additions to Plutus
- Ledger   | For proposals regarding the Cardano ledger (including Reward Sharing Schemes)
- Catalyst | For proposals affecting Project Catalyst / the Jörmungandr project

-->

## Abstract

Full determinism of transactions gives rise to valuable ledger properties, such as:

- "true" atomicity (the effects of a valid transaction are known before it is accepted)
- fee predictability

However, it comes at a cost: development becomes more complicated because of the need to "re-invent" non-determinism where it is required for the dApp logic.

Full determinism *may* be unnecessarily strict as a way to achieve the "good" properties, as the design space for the alternatives haven't been fully explored.

<!-- A short (\~200 word) description of the target goals and the technical obstacles to those goals. -->

## Problem
<!-- A more elaborate description of the problem and its context. This section should explain what motivates the writing of the CPS document. -->

Let's consider two types of determinism:

I. **execution layer determinism**: can we predict the exact outcome of a *transaction*, if it passes? Enforced on Cardano, does not exist on EVM.

II. **application layer determinism**: can we predict the outcome of a *user action* within a dApp, if it succeeds?

Whenever app layer (type-II) non-determinism is desired, the go-to solution for Cardano developers is to split one non-deterministic *app action* into multiple *transactions*, typically via on-chain orders and order batchers.

Batchers establish ordering and execute concurrent orders from different users. Orders are typically implemented as transactions that create UTxOs with inline datums. Batchers would return the funds if it's impossible to execute an order, and the user has to compensate the tx fee for the batcher in advance.

This solution introduces a whole set of new problems:

- **Uncertain protocol liveness**. Batchers depend on someone initiating the executing transaction. The node does not provide the guarantee that a valid transaction will pass within a certain timeframe, therefore the risk of order getting stuck has to be accounted for by the user: *no immediate execution is provided*.
- **Batcher fees and min-ada compensation**. The cost of initiating a transaction has to be compensated to the batcher. The batcher, no matter how efficient, can't take less than min-ada value (the cost of creating a UTxO), because that is the minimum ADA value a UTxO can have. The change can't be returned to the order initiator easily, because it is usually significantly lower than the min-ada.
- **Doubled action confirmation time**. Two transactions take more time to pass, even assuming immediate order execution.
- **Incentives for centralization**. Although decentralized batchers are possible, in reality designing them is more complex than building a centralized batcher bot.

## Use cases
<!-- A concrete set of examples written from a user's perspective, describing what and why they are trying to do. When they exist, this section should give a sense of the current alternatives and highlight why they are not suitable. -->

### Automated market maker DEX

AMM DEX requires many users to interact with the same pool, every interaction changes the price available for swap to the next user.

Historically, the improvement of AMM DEXes over traditional order-book-style exchanges has been the ability to execute orders immediately.

Currently, AMM DEXes on Cardano do not allow for high throughput without batchers. Either way, with or without batchers they are effectively no better than order books.

### Lending platform (liquidations)

Liquidating many open positions at once in the presence of a dynamically changing price oracle is not reliable. Lending platform should allow a liquidation to proceed if the price is lower (or higher) than a known threshold, but in reality the need to refer to a particular UTxO containing the price datum makes it so that a liquidation may only proceed if the the price is *the same* as the one known to the liquidation bot during transaction building.

## Goals
<!-- A list of goals and non-goals a project is pursuing, ranked by importance. These goals should help understand the design space for the solution and what the underlying project is ultimately trying to achieve.

Goals may also contain requirements for the project. For example, they may include anything from a deadline to a budget (in terms of complexity or time) to security concerns.

Finally, goals may also serve as evaluation metrics to assess how good a proposed solution is. -->

The goal of this CPS is to start a discussion about alternative ledger designs.
There are no immediate plans to work on implementing any of the possible alternative ledger rules.

### A minimal non-deterministic ledger with fully-atomic transactions




## Open Questions
<!-- A set of questions to which any proposed solution should find an answer. Questions should help guide solutions design by highlighting some foreseen vulnerabilities or design flaws. Solutions in the form of CIP should thereby include these questions as part of their 'Rationale' section and provide an argued answer to each. -->



<!-- OPTIONAL SECTIONS: see CIP-9999 > Specification > CPS > Structure table -->

## Copyright

This CPS is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
