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

Determinism of transactions gives rise to valuable ledger properties, such as:

- atomicity (a transaction is either fully accepted or fully rejected without a fee)
- predictability of monetary changes and fees

However, it comes at a cost:

- Development becomes more complicated because of the need to "re-invent" non-determinism where it is required for the dApp logic
- UTxO contention limits the number of concurrent users a dApp can have

Full determinism *may* be unnecessarily strict as a way to achieve the "good" properties, as the design space for the alternatives haven't been fully explored.

## Problem

Let's consider two types of determinism:

I. **execution layer determinism**: can we predict the exact result of a *transaction*, if it passes? Enforced on Cardano, does not exist on EVM.

II. **application layer determinism**: can we predict the outcome of a *user action* within a dApp, if it succeeds?

Whenever app layer (type-II) non-determinism is desired, the go-to solution for Cardano developers is to split one non-deterministic *app action* into multiple *transactions*, typically via on-chain orders and order batchers.

Batchers establish ordering and execute concurrent orders from different users. Orders are typically implemented as transactions that create UTxOs with inline datums. Batchers would return the funds if it's impossible to execute an order, and the user has to compensate the tx fee for the batcher in advance.

This solution introduces a whole set of new problems:

- **Uncertain protocol liveness**. Batchers depend on someone initiating the executing transaction. The node does not provide the guarantee that a valid transaction will pass within a certain timeframe, therefore the risk of order getting stuck has to be accounted for by the user: *no immediate execution is provided*.
- **Batcher fees and min-ada compensation**. The cost of initiating a transaction has to be compensated to the batcher. The batcher, no matter how efficient, can't take less than min-ada value (the cost of creating a UTxO), because that is the minimum ADA value a UTxO can have. The change can't be returned to the order initiator easily, because it is usually significantly lower than the min-ada.
- **Doubled action confirmation time**. Two transactions take more time to pass, even assuming immediate order execution.
- **Incentives for centralization**. Although decentralized batchers are possible, in reality designing them is more complex than building a centralized batcher bot. Decentralized batchers *still* don't provide liveness guarantees: it *may just happen* that no executor bots will be available at any given time, despite the incentives.

### Historical context

[The Extended UTXO Model paper](https://jmchapman.io/papers/eutxo.pdf) introduces an extension for the UTxO model and proves that it is as expressive as CEM (Constraint Emitting Machines).

## Use cases

### Automated market maker DEX

An AMM DEX requires many users to interact with the same pool. Every interaction changes the swap price for the next user.

Historically, the improvement of AMM DEXes over traditional order-book-style exchanges has been the ability to execute orders immediately.

Currently, AMM DEXes on Cardano do not allow for high throughput without batchers. Either way, with or without batchers, they are effectively no better than order books, because immediate execution is not provided.

### Lending platform (liquidations)

Liquidating many open positions at once in the presence of a dynamically changing price oracle is not reliable. Lending platform should allow a liquidation to proceed if the price is lower (or higher) than a known threshold, but in reality the need to refer to a particular UTxO containing the price datum makes it so that a liquidation may only proceed if the the price is *the same* as the one known to the liquidation bot during transaction building.

### Non-determinism and atomicity

It is easy to show that, in principle, atomic transactions are possible even if the validators accept mutable shared state. The argument below should be considered a proof that this discussion makes sense and is worth having, rather than a concrete proposal.

One of the ways to combine non-determinism and atomicity is allowing mutable state variable validation during phase-1, which must be done in constant time and memory (just like UTxO lookups).

Let's assume that phase-2 scripts somehow provide a way to change the output UTxO distribution, depending on the outcome of script execution. The scripts remain fully deterministic from the ledger perspective, but the values of mutable shared state variables are not known during the construction of a transaction.

#### AMM DEX example

The condition for a swap involving a liquidity pool is that the actual price must be within the user-defined slippage settings.

Conceptually, this condition can be expressed like this:

```haskell
let price = readMutableVariable(priceVariable)
in wantedPrice * (1.0 - allowedSlippage) <= price && price <= wantedPrice * (1.0 + allowedSlippage)
```

which can be pre-compiled down to:

```haskell
let price = readMutableVariable(priceVariable)
in minimumPrice <= price && price <= maximumPrice
```

Expressions like this can be evaluated in constant time and memory (the constants should be restrictive enough, and the time for evaluating a script should be comparable to that of transaction parsing and UTxO lookups).

#### On-chain liquidation example

TBD

<!-- OPTIONAL SECTIONS: see CIP-9999 > Specification > CPS > Structure table -->

## Goals

The goal of this CPS is to start a discussion about alternative ledger designs.
There are no immediate plans to work on implementing any of the possible alternative ledger rules.

## Open Questions

<!-- A set of questions to which any proposed solution should find an answer. Questions should help guide solutions design by highlighting some foreseen vulnerabilities or design flaws. Solutions in the form of CIP should thereby include these questions as part of their 'Rationale' section and provide an argued answer to each. -->

- What properties of the ledger that stem from determinism are really valuable?


## Copyright

This CPS is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
