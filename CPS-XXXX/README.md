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
Created: 2024-08-05
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

- The need to "re-introduce" non-determinism where it is required for the dApp logic (which is commonly done by using multiple transactions for a single user action), makes immediate execution of user actions impossible.
- UTxO contention limits the number of concurrent users a dApp can have, because a single UTxO can be consumed by a single transaction only.

Full determinism *may* be suboptimal as a way to achieve the "good" properties, as the design space for the alternatives haven't been fully explored.

## Problem

It is impossible to build a dApp that has these three properties at the same time on a fully-deterministic ledger:

- **immediate execution**: user's action is completed within a single transaction
- **horizontal scalability**: it is possible for multiple users to interact without experiencing UTxO contention problems, no matter the number of concurrent users
- **shared mutable state**: user actions can depend on the outcomes of the actions of past users

An example of a DeFi primitive that requires all three properties is an AMM DEX. Clearly, Uniswap-style liquidity pool has all three properties:

- A user can interact with it directly and swap in a single transaction
- The number of concurrent users is limited only by the settlement layer of the chain
- Every swap affects the price for the next user

Currently, AMM DEXes on Cardano do not allow for high throughput without batchers. Either way, with or without batchers, they are effectively no better than order books, because immediate execution can't be guaranteed: either because of UTxO contention or due to the need of using a batcher.

### Types of determinism: developer's perspective

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

Here's an excerpt from the paper relevant to this discussion:

> The benefit of this graph-based approach to a cryptocurrency ledger is that
> it plays well with the concurrent and distributed nature of blockchains. In par-
> ticular, it forgoes any notion of shared mutable state, which is known to lead to
> highly complex semantics in the face of concurrent and distributed computations
> involving that shared mutable state.
>
> Nevertheless, the UTXO model, generally, and Bitcoin, specifically, has been
> criticised for the limited expressiveness of programmability achieved by the val-
> idator concept. In particular, Ethereum’s account-based ledger and the associated
> notion of contract accounts has been motivated by the desire to overcome those
> limitations. Unfortunately, it does so by introducing a notion of shared mutable
> state, which significantly complicates the semantics of contract code. In par-
> ticular, contract authors need to understand the subtleties of this semantics or
> risk introducing security issues (such as the vulnerability to recursive contract
> invocations that led to the infamous DAO attack [5]).
>
> [..] The contribution of the present paper is to propose an extension
> to the basic UTXO ledger model, which (a) provably increases expressiveness,
> while simultaneously (b) preserving the dataflow properties of the UTXO graph;
> in particular, it forgoes introducing any notion of shared mutable state. More
> specifically, we make the following contributions: [...]

There is no argument that the absence of mutable state is the only approach that *plays well with the concurrent and distributed nature of blockchains* in the paper. It is just something that is known to be easy (because executing rollbacks on a DAG of transactions does not require to re-do any validator computations).

Arguably, the DAO hack has been caused by specific EVM API design choices, rather than by mere presence of shared mutable state: it is easy to imagine a ledger with shared mutable state, but without reentrancy. Moreover, the re-entrancy problem has a direct analogue in Cardano, called ["multiple satisfaction"](https://github.com/mlabs-haskell/plutus-security?tab=readme-ov-file#7-multiple-satisfaction).

### Non-determinism and atomicity: why is it possible to do better?

It is easy to show that, in principle, atomic transactions are possible even if the validators accept mutable shared state that is not known at the time of transaction construction. The argument below should be considered a proof that this discussion makes sense and is worth having, rather than a concrete proposal.

One of the ways to combine non-determinism and atomicity is allowing mutable state variable validation during phase-1, which must be done in constant time and memory (just like UTxO lookups).

Let's assume that phase-2 scripts somehow provide a way to change the output UTxO distribution, depending on the outcome of script execution. The scripts remain fully deterministic from the ledger perspective, but the values of mutable shared state variables are not known during the construction of a transaction, providing type-II non-determinism for the end users.

#### AMM DEX example

The condition for a successful swap involving a liquidity pool is that the actual price must be within the user-defined slippage settings.

Conceptually, this condition can be expressed like this:

```haskell
let price = readMutableVariable(priceVariable)
in wantedPrice * (1.0 - allowedSlippage) <= price && price <= wantedPrice * (1.0 + allowedSlippage)
```

which can be inlined down to:

```haskell
let price = readMutableVariable(priceVariable)
in minimumPrice <= price && price <= maximumPrice
```

Expressions like this can be evaluated in constant time and memory, with sufficiently restrictive constants. The time required for evaluating a script should be comparable to that of transaction parsing and UTxO lookups. If the validation fails, the transaction can be discarded completely without incurring any fees.

Therefore, a ledger design that accepts user-defined constant-time conditions for phase-1 validation can support both atomic and non-deterministic transactions (from the user's perspective, not the ledger's).

In case the phase-1 validator does not correspond to the phase-2 one (i.e. the first validates, but the latter fails), collateral loss can be triggered in order to compensate the network for the incurred cost of validation.

#### On-chain liquidation example

Liquidating many open positions at once in the presence of a dynamically changing price oracle is not reliable. Lending platform should allow a liquidation to proceed if the price is lower (or higher) than a known threshold, but in reality the need to refer to a particular UTxO containing the price datum makes it so that a liquidation may only proceed if the the price is *the same* as the one known to the liquidation bot during transaction building.

TODO: expand this example

## Goals

The goal of this CPS is to start a discussion about alternative ledger designs.
There are no immediate plans to work on implementing any of the possible alternative ledger rules.

## Open Questions

<!-- A set of questions to which any proposed solution should find an answer. Questions should help guide solutions design by highlighting some foreseen vulnerabilities or design flaws. Solutions in the form of CIP should thereby include these questions as part of their 'Rationale' section and provide an argued answer to each. -->

- What properties of the ledger that stem from determinism are really valuable?
- Is it possible to extend the current ledger with mutable shared state?
- How to process rollbacks efficiently in the presence of mutable shared state?

## Copyright

This CPS is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
