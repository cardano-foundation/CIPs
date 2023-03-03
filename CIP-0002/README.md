---
CIP: 2
Title: Coin Selection Algorithms for Cardano
Category: Wallets
Authors:
    - Jonathan Knowles <jonathan.knowles@iohk.io>
Implementors: N/A
Discussions:
    - https://github.com/cardano-foundation/CIPs/pull/2
    - https://github.com/cardano-foundation/CIPs/issues/232
Status: Active
Created: 2020-05-04
License: CC-BY-4.0
---

## Abstract

This article describes, in _human-readable terms_, the coin selection
algorithms used by [Cardano
Wallet](https://github.com/input-output-hk/cardano-wallet/) and other parts of
the Cardano ecosystem.

In the context of this article, **coin selection** refers to the process of
choosing _unspent coins_ from a wallet (or [UTxO set](#utxo-set)) in order to
pay money to one or more recipients.

## Motivation: why is this CIP necessary?

This document was written to help people gain an understanding of the coin
selection algorithms used in Cardano _without_ having to read through and
understand Cardano source code.

We aim to provide descriptions of algorithms that:

  - don't require prior experience with any particular programming language;
  - are understandable for people who are unfamiliar with coin selection;
  - are precise enough for software engineers to be able to reimplement these
    algorithms in their preferred programming languages.

Where appropriate, we also provide mathematical descriptions, for added clarity.

### Scope

Coin selection is a large, complex topic, with many difficult problems to
solve. However, all software that performs coin selection must ultimately deal
with at least the following pair of problems:

  - How to _generate_ a coin selection, by choosing unspent coins from a wallet
    (or [UTxO set](#utxo-set)) in order to pay money to one or more
    recipients.
  - How to _adjust_ a coin selection in order to pay for a _network fee_, so
    that the coin selection can be published as a transaction on the
    blockchain.

This article concerns itself with the _former_ problem of _how to generate_ a
coin selection.

Problems relating to network fees, and how to adjust coin selections to pay for
such fees, are outside the scope of this article.

### Background

This section introduces the fundamental concepts behind coin selection,
provides a discussion of why coin selection is a non-trivial problem, and
describes important goals of coin selection algorithms.

#### What is Coin Selection?

Coin selection is the process of choosing unspent coins from a wallet in order
to pay money to one or more recipients.

##### Coin Selection in the Physical World

In the familiar world of _physical_ money, our wallets hold value in the form
of _coins and banknotes_.

When making a payment to someone, we typically select a combination of coins
and banknotes from a wallet that, when added together, have enough value to
cover the amount required.

Ideally, we'd always be able to select _just enough_ to cover the exact amount.
However, given that coins and banknotes have fixed values (and cannot be
subdivided without destroying their value), it's often impossible to select the
exact amount required. In such cases, we typically give the recipient _more_
than the required amount, and then receive the excess value back as _change_.

> :bulb: **Example**
>
> Alice wishes to pay for her lunch.
>
> The total price comes to €2.50 (2 euros and 50 cents). In her wallet, she has
> **five** _one-euro_ coins, and **one** _ten-euro_ note.
>
> Note that there is _no_ combination of coins (or notes) in her wallet that
> when added together give a total of €2.50, but there _are_ several possible
> combinations that _exceed_ the total.
>
> To solve this problem, Alice selects _one_ of these combinations: **three**
> _one-euro_ coins. She uses the coins to make the payment, and then receives
> **one** 50-cent coin as change.

##### Coin Selection in Cardano

Similarly to how a physical wallet holds value in the form of _unspent coins
and banknotes_, a Cardano wallet holds value in the form of _unspent
transaction outputs_. An [unspent transaction
output](#unspent-transaction-output) is the result of a previous transaction
that transferred money to the wallet, where the value has not yet been spent by
another transaction. Each unspent transaction output has an associated [coin
value](#coin-value), and the total value of a wallet is the _sum_ of these coin
values. Collectively, the set of unspent transaction outputs is known as the
[UTxO set](#utxo-set).

When using a Cardano wallet to make a payment, the wallet software must select
a combination of unspent outputs from the wallet's [UTxO set](#utxo-set), so
that the total value of selected outputs is enough to cover the target amount.

Just as with physical coins and notes, unspent outputs from the UTxO set
_cannot_ be subdivided, and must either be spent completely in a given
transaction, or not be spent at all. Similarly to a transaction with physical
money, the wallet software must select a combination of unspent outputs whose
total value is _greater_ than the target amount, and then arrange that _change_
is paid back to the wallet.

Coin selection refers to the process of selecting a combination of unspent
outputs from a wallet's [UTxO set](#utxo-set) in order to make one or more
payments, and computing the set of change to be paid back to the wallet.

#### Why is Coin Selection Non-Trivial?

There are a number of issues which make the problem of coin selection more
complicated than would initially appear.

##### The Transaction Size Limitation

Each [transaction](#transaction) has a _maximum size_, as defined by the
protocol. The size of a transaction increases as we add more
[inputs](#transaction-input) or [outputs](#transaction-output).

Therefore, there's a practical limit on the number of coins we can select for
any given transaction.

##### The Problem of Dust

One simple strategy for *selecting coins* might be to mimic what we do when
making a payment with coins and banknotes in the physical world. By giving the
recipient an amount that's as close as possible to the amount they're expecting,
we can minimize the amount of change they need to return to us.

However, trying to replicate this strategy with a UTxO-based wallet has an
undesirable effect: minimizing the total value of selected coins will also
minimize the value of change returned to the wallet. When repeated over time,
this strategy will tend to cause an accumulation of tiny outputs in the
wallet's [UTxO set](#utxo-set) known as [**dust**](#dust-output).

Dust outputs are a problem, because even if the total value of dust in a wallet
is more than enough to cover a given target amount, if we attempt to include
that dust in a given transaction, we may run out of space (by reaching the
[transaction size limit](#the-transaction-size-limitation)) before we can cover
the target amount.

For more information on dust avoidance, see [Self Organisation in Coin
Selection](#self-organisation-in-coin-selection).

##### The Problem of Concurrency

One simple strategy for *generating change* might be to mimic what a shop
assistant does when accepting a payment in the real world, which is to minimize
the *number* of coins and banknotes that they return to the customer.  This is
beneficial for the shop, as it reduces the chances of them running out of
change, and beneficial for the customer, as it reduces the amount of change
that they have to carry around in their wallet.

Analogously, when generating change for a UTxO-based wallet, we might be
tempted to use the simple strategy of just creating a single [change
output](#change-output) with the exact excess value.

However, using this strategy has an undesirable effect: the repeated act of
minimizing the number of change outputs will tend (over time) to reduce the
number of entries in a wallet's [UTxO set](#utxo-set). This is bad for two
reasons:

1.  Having a small [UTxO set](#utxo-set) limits the number of future payments
    that we can make in parallel.

2.  The approach of coalescing all change into a single output is widely
    considered to have negative privacy implications.

#### Goals of Coin Selection Algorithms

In light of the issues described above, we'd ideally like for our coin selection
algorithms to be able to:

  * limit, over the course of time, the amount of [dust](#dust-output) that
    accumulates in the [UTxO set](#utxo-set).

  * maintain, over the course of time, a [UTxO set](#utxo-set) with _useful_
    outputs: that is, outputs that allow us to process future payments with a
    reasonably small number of [inputs](#transaction-input).

## Specification

### Structure

The [Background](#background) section introduces the fundamental concepts
behind coin selection, provides a discussion of why coin selection is
a non-trivial problem, and describes the goals of coin selection algorithms.

The [Interface](#interface) section gives a description of the common interface
unifying all coin selection algorithms used within Cardano Wallet, the standard
parameter types, result types, and error types used by this interface, and a
description of the properties that all conforming implementations are expected
to satisfy.

The [Algorithms](#algorithms) section gives detailed descriptions of each of
the individual coin selection algorithms used in Cardano Wallet, along with
step-by-step descriptions of the computations involved.

The [Reference Implementations](#reference-implementations) section provides
links to reference implementations of each algorithm in various languages.

### Contents

* [Abstract](#abstract)
* [Motivation](#motivation-why-is-this-cip-necessary)
  * [Scope](#scope)
  * [Background](#background)
    * [What is Coin Selection?](#what-is-coin-selection)
      * [Coin Selection in the Physical World](#coin-selection-in-the-physical-world)
      * [Coin Selection in Cardano](#coin-selection-in-cardano)
    * [Why is Coin Selection Non-Trivial?](#why-is-coin-selection-non-trivial)
      * [The Transaction Size Limitation](#the-transaction-size-limitation)
      * [The Problem of Dust](#the-problem-of-dust)
      * [The Problem of Concurrency](#the-problem-of-concurrency)
    * [Goals of Coin Selection Algorithms](#goals-of-coin-selection-algorithms)
* [Specification](#specification)
  * [Structure](#structure)
  * [Definitions](#definitions)
    * [Address](#address)
    * [Coin Value](#coin-value)
    * [Transaction](#transaction)
    * [Transaction Input](#transaction-input)
    * [Transaction Output](#transaction-output)
    * [Spent Transaction Output](#spent-transaction-output)
    * [Unspent Transaction Output](#unspent-transaction-output)
    * [UTxO Set](#utxo-set)
    * [Change Output](#change-output)
    * [Dust Output](#dust-output)
  * [Interface](#interface)
    * [Parameters](#parameters)
      * [Requested Output Set](#requested-output-set)
      * [Initial UTxO Set](#initial-utxo-set)
      * [Maximum Input Count](#maximum-input-count)
    * [Results](#results)
      * [Coin Selection](#coin-selection)
      * [Remaining UTxO Set](#remaining-utxo-set)
    * [Properties](#properties)
      * [Coverage of Payments](#coverage-of-payments)
      * [Correctness of Change](#correctness-of-change)
      * [Conservation of UTxO](#conservation-of-utxo)
      * [Conservation of Outputs](#conservation-of-outputs)
    * [Failure Modes](#failure-modes)
      * [UTxO Balance Insufficient](#utxo-balance-insufficient)
      * [UTxO Not Fragmented Enough](#utxo-not-fragmented-enough)
      * [UTxO Fully Depleted](#utxo-fully-depleted)
      * [Maximum Input Count Exceeded](#maximum-input-count-exceeded)
  * [Algorithms](#algorithms)
    * [Largest-First](#largest-first)
      * [State](#state)
        * [Available UTxO List](#available-utxo-list)
        * [Unpaid Output List](#unpaid-output-list)
        * [Accumulated Coin Selection](#accumulated-coin-selection)
      * [Computation](#computation)
    * [Random-Improve](#random-improve)
      * [Cardinality](#cardinality-1)
      * [State](#state-1)
        * [Available UTxO Set](#available-utxo-set)
        * [Accumulated Coin Selection](#accumulated-coin-selection-1)
      * [Computation](#computation-1)
        * [Phase 1: Random Selection](#phase-1-random-selection)
        * [Phase 2: Improvement](#phase-2-improvement)
      * [Termination](#termination-1)
* [Rationale: how does this CIP achieve its goals?](#rationale-how-does-this-cip-achieve-its-goals)
  * [Motivating Principles](#motivating-principles)
    * [LargestFirst](#largest-first-2)
    * [Random-Improve](#random-improve-2)
      * [Principle 1: Dust Management](#principle-1-dust-management)
      * [Principle 2: Change Management](#principle-2-change-management)
      * [Principle 3: Performance Management](#principle-3-performance-management)
  * [External Resources](#external-resources)
    * [Self Organisation in Coin Selection](#self-organisation-in-coin-selection)
* [Path to Active](#path-to-active)
  * [Acceptance Criteria](#acceptance-criteria)
  * [Implementation Plan](#implementation-plan)
    * [Reference Implementations](#reference-implementations)
      * [Largest-First](#largest-first-1)
      * [Random-Improve](#random-improve-1)
* [Copyright](#copyright)

### Definitions

This section defines common terms that are used throughout this document.

#### Address

An _address_ is a unique identifier that represents a payment recipient, a
destination for a payment.

Addresses are typically owned (and generated) by individual wallets.

In general, coin selection algorithms are agnostic to the type of addresses
used to identify payment recipients. Any address type may be used, so long as
the set of possible addresses is totally-ordered.

#### Coin Value

A _coin value_ is a non-negative integer value that represents a number of
[Lovelace](https://cardanodocs.com/cardano/monetary-policy/).

One [Ada](https://cardanodocs.com/cardano/monetary-policy/) is _exactly_ equal
to one million Lovelace.

#### Transaction

In a [UTxO](#utxo-set)-based blockchain, a _transaction_ is a binding between
[inputs](#transaction-input) and [outputs](#transaction-output).

```
input #1  >---+          +---> output #1
               \        /
input #2  >-----+------+
               /        \
input #3  >---+          +---> output #2
```

#### Transaction Input

A _transaction input_ is a _unique reference_ to a single
[output](#transaction-output) from a previous transaction.

In general, coin selection algorithms are agnostic to the type of references
used to identify outputs from previous transactions. Any type may be used, so
long as the set of possible references is totally-ordered, and so long as it is
possible to determine the [coin value](#coin-value) associated with any given
reference.

In the case of Cardano and other UTxO-based blockchains, this reference
generally consists of a pair of values (**_h_**, **_n_**), where:

  * **_h_** is a _unique identifier_ for an existing transaction **_t_**;
  * **_n_** is a 0-based integer index into the output list of transaction
    **_t_**.

#### Transaction Output

A _transaction output_ consists of a pair of values (**_a_**, **_v_**), where:

  * **_a_** is the [address](#address) of a recipient.
  * **_v_** is the [coin value](#coin-value) to pay to the recipient.

#### Spent Transaction Output

A _spent transaction output_ is an [output](#transaction-output) from an
existing [transaction](#transaction) that has already been referenced as an
[input](#transaction-input) within a later transaction on the blockchain.

In effect, the [coin value](#coin-value) associated with that transaction
output has been _spent_, and cannot be reused.

#### Unspent Transaction Output

An _unspent transaction output_ is an [output](#transaction-output) from an
existing [transaction](#transaction) that has not yet been referenced as an
[input](#transaction-input) within a later transaction.

In effect, the [coin value](#coin-value) associated with that transaction
output has _not yet_ been spent, and is still available.

#### UTxO Set

A _UTxO set_ is a set of [unspent transaction
outputs](#unspent-transaction-output).

This term is commonly used in two ways:

  * To describe the _complete set_ of all unspent transaction outputs within a
    _blockchain_.

  * To describe the _subset_ of unspent transaction outputs associated with
    a _wallet_. The UTxO set of a wallet represents the total unspent value
    associated with that wallet.

From the point of view of a coin selection algorithm, each member of a UTxO set
can be represented as a pair of the form (**_u_**, **_v_**), where:

  * **_u_** is a unique reference to an
    [unspent output](#unspent-transaction-output) from a previous transaction.
  * **_v_** is the [coin value](#coin-value) associated with **_u_**.

In general, coin selection algorithms are agnostic to the type of references
used to identify unspent outputs from previous transactions. Any type may be
used, so long as the set of possible references is totally-ordered.

In practice however, the type of each unique reference **_u_** is equivalent
to the type of a [transaction input](#transaction-input), as transaction inputs
are simply references to unspent outputs from previous transactions.

#### Change Output

In the context of a wallet, a _change output_ is a [transaction
output](#transaction-output) that transfers value _back_ to the wallet, rather
than to an external payment recipient. The [address](#address) associated with
a change output is generated by the wallet, and belongs to the wallet.

Change ouputs are necessary in a UTxO-based blockchain, as the value associated
with any given [transaction input](#transaction-input) must be spent _entirely_
by the transaction that includes it.

When selecting entries from a [UTxO set](#utxo-set) to include as inputs in a
transaction, a coin selection algorithm will generally not be able to select
inputs that precisely match the total value of all payments to external
recipients, and will therefore need to select more than is strictly required.
To avoid the destruction of value, selection algorithms create _change outputs_
to return the excess value back to the wallet.

#### Dust Output

A _dust output_ is a [transaction output](#transaction-output) with an
associated [coin value](#coin-value) that is:

  * small in comparison to payments typically made by the user of the wallet;
  * small in comparison to the marginal fee associated with including it in
    a transaction.

Dust outputs are a problem, because even if the total value of dust in a wallet
is more than enough to cover a given payment amount, if we attempt to include
that dust in a given transaction, we may run out of space (by reaching the
[transaction size limit](#the-transaction-size-limitation)) before we can cover
the target amount.

### Interface

All coin selection algorithms used by Cardano Wallet implement a
_common interface_.

At the most fundamental level, a coin selection algorithm is a _mathematical
function_ that when applied to a [requested output
set](#requested-output-set) and an [initial UTxO set](#initial-utxo-set),
will produce a [coin selection](#coin-selection): the basis for a
[transaction](#transaction) in a UTxO-based blockchain.

This section describes:

  * the [parameters](#parameters) accepted by all coin selection algorithms;
  * the [results](#results) they produce when successful;
  * the [error conditions](#failure-modes) that may occur on failure;
  * the [properties](#properties) that apply to all coin selection
    algorithms: mathematical laws governing the relationships between parameters
    and results.

In this section, the terms _coin selection algorithm_ and _coin selection
function_ will be used interchangeably.

#### Parameters

All coin selection functions accept the following parameters:

 1. **Requested Output Set**

    A list of payments to be made to recipient addresses, encoded as a list of
    [transaction outputs](#transaction-output).

 2. **Initial UTxO Set**

    A [UTxO set](#utxo-set) from which the coin selection algorithm can select
    entries, to cover payments listed in the [requested output
    set](#requested-output-set).

    In the context of a wallet, this parameter would normally be assigned with
    the wallet's complete [UTxO set](#utxo-set), giving the coin selection
    algorithm access to the total value associated with that wallet.

 3. **Maximum Input Count**

    An _upper bound_ on the number of UTxO entries that the coin selection
    algorithm is permitted to select from the [initial UTxO
    set](#initial-utxo-set).

    This parameter is necessary for blockchains that impose an upper limit on
    the size of transactions.

#### Results

All coin selection functions produce the following result values:

 1. **Coin Selection**

    A _coin selection_ is the basis for a [transaction](#transaction) in a
    UTxO-based blockchain.

    It is a record with three fields:

      * A set of **_inputs_**, equivalent to a subset of the
        [initial UTxO set](#initial-utxo-set).

        From the point of view of a _wallet_, this represents the value that
        has been selected from the wallet in order to cover the total payment
        value.

      * A set of **_outputs_** (see [transaction output](#transaction-output)).

        Represents the set of payments to be made to recipient addresses.

      * A set of **_change values_** (see [change output](#change-output)),
        where each change value is simply a [coin value](#coin-value).

        From the point of view of a _wallet_, this represents the change to be
        returned to the wallet.

 2. **Remaining UTxO Set**

    The _remaining UTxO set_ is a subset of the [initial UTxO
    set](#initial-utxo-set).

    It represents the set of values that remain after the coin selection
    algorithm has removed values to pay for entries in the [requested output
    set](#requested-output-set).

    In the context of a _wallet_, if a coin selection algorithm is applied to
    the wallet's _complete_ UTxO set, then the _remaining_ UTxO set represents
    the _updated_ UTxO set of that wallet.

#### Properties

All coin selection algorithms satisfy a common set of _properties_: general
rules that govern the relationship between the _parameters_ supplied to coin
selection functions and the _results_ they are allowed to produce.

##### Coverage of Payments

This property states that the total value of _inputs_ in the resulting [coin
selection](#coin-selection) result is sufficient to _cover_ the total value of
the [requested output set](#requested-output-set).

In particular:

  * **_v_**<sub>selected</sub> ≥ **_v_**<sub>requested</sub>

Where:

  * **_v_**<sub>requested</sub>

    is the total value of the [requested output set](#requested-output-set)


  * **_v_**<sub>selected</sub>

    is the total value of the _inputs_ field of the [coin
    selection](#coin-selection) result.

##### Correctness of Change

This property states that the correct amount of _change_ was generated.

In particular:

  * **_v_**<sub>selected</sub>
  = **_v_**<sub>requested</sub> + **_v_**<sub>change</sub>

Where:

  * **_v_**<sub>change</sub>

    is the total value of the _change_ field of the [coin
    selection](#coin-selection) result.

  * **_v_**<sub>requested</sub>

    is the total value of the [requested output set](#requested-output-set)

  * **_v_**<sub>selected</sub>

    is the total value of the _inputs_ field of the [coin
    selection](#coin-selection) result.

##### Conservation of UTxO

This property states that every entry in the [initial UTxO
set](#initial-utxo-set) is included in _either_ the inputs set of the generated
[coin selection](#coin-selection), _or_ in the [remaining UTxO
set](#remaining-utxo-set), but _not both_.

  * If a UTxO entry _is_ selected by the coin selection algorithm, it is
    included in the [coin selection](#coin-selection) inputs set.

  * If a UTxO entry is _not_ selected by the coin selection algorithm, it is
    included in the [remaining UTxO set](#remaining-utxo-set).

The following laws hold:

  * **_U_**<sub>initial  </sub> ⊃ **_U_**<sub>remaining</sub>
  * **_U_**<sub>initial  </sub> ⊇ **_U_**<sub>selected </sub>

And:

  * **_U_**<sub>remaining</sub> ∩ **_U_**<sub>selected </sub> = ∅
  * **_U_**<sub>remaining</sub> ⋃ **_U_**<sub>selected </sub> =
    **_U_**<sub>initial  </sub>

Where:

  * **_U_**<sub>initial</sub>

    is the [initial UTxO set](#initial-utxo-set).

  * **_U_**<sub>remaining</sub>

    is the [remaining UTxO set](#remaining-utxo-set).

  * **_U_**<sub>selected</sub>

    is the value of the _inputs_ field of the [coin selection](#coin-selection)
    result.

##### Conservation of Outputs

This property states that the [requested output set](#requested-output-set)
is _conserved_ in the [coin selection](#coin-selection) result.

In particular, the _outputs_ field of the [coin selection](#coin-selection)
result should be _equal to_ the [requested output set](#requested-output-set).

#### Failure Modes

There are a number of ways in which a coin selection algorithm can fail:

  * **UTxO Balance Insufficient**

    This failure occurs when the total value of the entries within the [initial
    UTxO set](#initial-utxo-set) (the amount of money _available_) is _less
    than_ the the total value of all entries in the [requested output
    set](#requested-output-set) (the amount of money _required_).

  * **UTxO Not Fragmented Enough**

    This failure occurs when the _number_ of entries in the [initial UTxO
    set](#initial-utxo-set) is _smaller than_ the number of entries in the
    [requested output set](#requested-output-set), for algorithms that impose
    the restriction that a single UTxO entry can only be used to pay for _at
    most one_ output.

  * **UTxO Fully Depleted**

    This failure occurs if the algorithm depletes all entries from the [initial
    UTxO set](#initial-utxo-set) _before_ it is able to pay for all outputs in
    the [requested output set](#requested-output-set).

    This can happen _even if_ the total value of entries within the [initial
    UTxO set](#initial-utxo-set) is _greater than_ the total value of all
    entries in the [requested output set](#requested-output-set), due to
    various restrictions that coin selection algorithms impose on themselves
    when selecting UTxO entries.

  * **Maximum Input Count Exceeded**

    This failure occurs when another input must be selected by the algorithm in
    order to continue making progress, but doing so will increase the size of
    the resulting selection beyond an acceptable limit, specified by the
    [maximum input count](#maximum-input-count) parameter.

### Algorithms

This section describes the coin selection algorithms used by Cardano Wallet,
along with step-by-step descriptions of the computations involved.

All algorithms implement a _common interface_, as described in the
[Interface](#interface) section.

There are two main algorithms used by Cardano Wallet:

  * [Largest-First](#largest-first)
  * [Random-Improve](#random-improve)

In general, Cardano Wallet gives _priority_ to the
[Random-Improve](#random-improve) algorithm, as experimental evidence shows
that it performs better at [minimising dust](#goals) and maintaining a UTxO set
with [useful outputs](#goals). (See [Self Organisation in Coin
Selection](#self-organisation-in-coin-selection) for more details.)

However, in rare cases, the [Random-Improve](#random-improve) algorithm may
fail to produce a result. In such cases, Cardano Wallet will fall back to the
[Largest-First](#largest-first) algorithm.

#### Largest-First

The **Largest-First** coin selection algorithm considers UTxO set entries
in _descending order of value_, from largest to smallest.

When applied to a set of [requested outputs](#requested-output-set), the
algorithm repeatedly selects entries from the [initial UTxO
set](#initial-utxo-set) until the total value of selected entries is _greater
than or equal to_ the total value of requested outputs.

The name of the algorithm is taken from the idea that the **largest** UTxO
entry is always selected **first**. Specifically:

> A given UTxO entry **_u_<sub>1</sub>** with
> value **_v_<sub>1</sub>** can be selected if and only if there is no other
> unselected entry **_u_<sub>2</sub>** with value **_v_<sub>2</sub>** where
> **_v_<sub>2</sub>** > **_v_<sub>1</sub>**.

##### State

At all stages of processing, the algorithm maintains the following pieces of
state:

 1. **Available UTxO List**

    This is initially equal to the [initial UTxO set](#initial-utxo-set),
    sorted into _descending order of coin value_.

    The _head_ of the list is always the remaining UTxO entry with the _largest
    coin value_.

    Entries are incrementally removed from the _head_ of the list as the
    algorithm proceeds, until enough value has been selected.

 2. **Selected UTxO Set**

    This is initially equal to the empty set.

##### Computation

The algorithm proceeds according to the following sequence of steps:

  * **Step 1**

    If the [available UTxO list](#available-utxo-list) is _empty_:

      * Terminate with a [UTxO Balance
        Insufficient](#utxo-balance-insufficient) error.

    If the [available UTxO list](#available-utxo-list) is _not empty_:

      * Remove an UTxO entry from the head of the [available UTxO
        list](#available-utxo-list) and add it to the [selected UTxO
        set](#selected-utxo-set).

  * **Step 2**

    Compare the total size **_n_**<sub>selected</sub> of the [selected UTxO
    set](#selected-utxo-set) with the [maximum input
    count](#maximum-input-count) **_n_**<sub>max</sub>.

      * If **_n_**<sub>selected</sub> > **_n_**<sub>max</sub> then:

        * Terminate with a [Maximum Input Count
          Exceeded](#maximum-input-count-exceeded) error.

      * If **_n_**<sub>selected</sub> ≤ **_n_**<sub>max</sub> then:

        * Go to step 3.

  * **Step 3**

    Compare the total value **_v_**<sub>selected</sub> of the [selected UTxO
    set](#selected-utxo-set) to the total value **_v_**<sub>requested</sub> of
    the [requested output set](#requested-output-set):

      * If **_v_**<sub>selected</sub> < **_v_**<sub>requested</sub> then go to
        step 1.
      * If **_v_**<sub>selected</sub> ≥ **_v_**<sub>requested</sub> then go to
        step 4.

  * **Step 4**

    Return a [coin selection](#coin-selection) result where:

      * The _inputs_ set is equal to the [selected UTxO
        set](#selected-utxo-set).

      * The _outputs_ set is equal to the [requested output
        set](#requested-output-set).

      * If **_v_**<sub>selected</sub> > **_v_**<sub>requested</sub> then:

        * The _change_ set contains just a single [coin](#coin-value) of value
          (**_v_**<sub>selected</sub> − **_v_**<sub>requested</sub>).

      * If **_v_**<sub>selected</sub> = **_v_**<sub>requested</sub> then:

        * The _change_ set is empty.

#### Random-Improve

The **Random-Improve** coin selection algorithm works in _two phases_:

  * In the **first phase**, the algorithm iterates through each of the
    [requested outputs](#requested-output-set) in _descending order of coin
    value_, from _largest_ to _smallest_. For each output, the algorithm
    repeatedly selects entries _at random_ from the [initial UTxO
    set](#initial-utxo-set), until each requested output has been associated
    with a set of UTxO entries whose _total value_ is enough to pay for that
    ouput.

  * In the **second phase**, the algorithm attempts to _expand_ each
    existing UTxO selection with _additional_ values taken at random from the
    [initial UTxO set](#initial-utxo-set), to the point where the total value
    of each selection is as close as possible to _twice_ the value of its
    associated output.

After the above phases are complete, for each output of value
**_v_**<sub>output</sub> and accompanying UTxO selection of value
**_v_**<sub>selection</sub>, the algorithm generates a _single_ change output
of value **_v_**<sub>change</sub>, where:

> **_v_**<sub>change</sub>
>   = **_v_**<sub>selection</sub>
>   − **_v_**<sub>output</sub>

Since the goal of the second phase was to expand each selection to the point
where its total value is _approximately twice_ the value of its associated
output, this corresponds to a change output whose target value is
_approximately equal_ to the value of the output itself:

> **_v_**<sub>change</sub>
>   = **_v_**<sub>selection</sub>
>   − **_v_**<sub>output</sub>
>
> **_v_**<sub>change</sub>
>   ≈ <span>2</span>**_v_**<sub>output</sub>
>   − **_v_**<sub>output</sub>
>
> **_v_**<sub>change</sub>
>   ≈ **_v_**<sub>output</sub>

##### Cardinality

The Random-Improve algorithm imposes the following cardinality restriction:

  * Each entry from the [initial UTxO set](#initial-utxo-set) is used to pay
    for _at most one_ output from the [requested output
    set](#requested-output-set).

As a result of this restriction, the algorithm will fail with a [UTxO Not
Fragmented Enough](#utxo-not-fragmented-enough) error if the number of entries
in the [initial UTxO set](#initial-utxo-set) is _smaller than_ the number of
entries in the [requested output set](#requested-output-set).

##### State

At all stages of processing, the algorithm maintains the following pieces of
state:

 1. **Available UTxO Set**

    This is initially equal to the [initial UTxO set](#initial-utxo-set).

 2. **Accumulated Coin Selection**

    The accumulated coin selection is a [coin selection](#coin-selection) where
    all fields are initially equal to the _empty set_.

##### Computation

The algorithm proceeds in two phases.

- **Phase 1: Random Selection**

In this phase, the algorithm iterates through each of the [requested
outputs](#requested-output-set) in descending order of coin value, from
largest to smallest.

For each output of value **_v_**, the algorithm repeatedly selects entries at
**random** from the [available UTxO set](#available-utxo-set), until the _total
value_ of selected entries is greater than or equal to **_v_**. The selected
entries are then _associated with_ that output, and _removed_ from the
[available UTxO set](#available-utxo-set).

This phase ends when _every_ output has been associated with a selection of
UTxO entries.

- **Phase 2: Improvement**

In this phase, the algorithm attempts to improve upon each of the UTxO
selections made in the previous phase, by conservatively expanding the
selection made for each output in order to generate improved change
values.

During this phase, the algorithm:

  * processes outputs in _ascending order of coin value_.

  * continues to select values from the [available UTxO
    set](#available-utxo-set).

  * incrementally populates the
    [accumulated coin selection](#accumulated-coin-selection-1).

For each output of value **_v_**, the algorithm:

 1.  **Calculates a _target range_** for the total value of inputs used to
     pay for that output, defined by the triplet:

     (_minimum_, _ideal_, _maximum_) =
     (**_v_**, <span>2</span>**_v_**, <span>3</span>**_v_**)

 2.  **Attempts to improve upon the existing UTxO selection** for that output,
     by repeatedly selecting additional entries at random from the [available
     UTxO set](#available-utxo-set), stopping when the selection can be
     improved upon no further.

     A selection with value **_v_<sub>1</sub>** is considered to be an
     _improvement_ over a selection with value **_v_<sub>0</sub>** if **all**
     of the following conditions are satisfied:

      * **Condition 1**: we have moved closer to the _ideal_ value:

        abs (_ideal_ − **_v_<sub>1</sub>**) <
        abs (_ideal_ − **_v_<sub>0</sub>**)

      * **Condition 2**: we have not exceeded the _maximum_ value:

        **_v_<sub>1</sub>** ≤ _maximum_

      * **Condition 3**: when counting cumulatively across all outputs
        considered so far, we have not selected more than the _maximum_ number
        of UTxO entries specified by [Maximum Input
        Count](#maximum-input-count).

 3.  **Creates a _change value_** for the output, equal to the total value
     of the _improved UTxO selection_ for that output minus the value **_v_**
     of that output.

 4.  **Updates the [accumulated coin
     selection](#accumulated-coin-selection-1)**:

      * Adds the _output_ to the _outputs_ field;
      * Adds the _improved UTxO selection_ to the _inputs_ field;
      * Adds the _change value_ to the _change values_ field.

This phase ends when every output has been processed, **or** when the
[available UTxO set](#available-utxo-set) has been exhausted, whichever occurs
sooner.

##### Termination

When both phases are complete, the algorithm terminates.

The [accumulated coin selection](#accumulated-coin-selection-1) is returned
to the caller as the [coin selection](#coin-selection) result.

The [available UTxO set](#available-utxo-set) is returned to the caller as the
[remaining UTxO set](#remaining-utxo-set) result.

## Rationale

### Largest-First

\-

### Random-Improve

There are several motivating principles behind the design of the algorithm.

#### Principle 1: Dust Management

The probability that random selection will choose dust entries from a UTxO
set _increases_ with the proportion of dust in the set.

Therefore, for a UTxO set with a large amount of dust, there's a high
probability that a random subset will include a large amount of dust.

Over time, selecting entries randomly in this way will tend to _limit_ the
amount of dust that accumulates in the UTxO set.

#### Principle 2: Change Management

As mentioned in the [Goals](#goals-of-coin-selection-algorithms) section, it is
desirable that coin selection algorithms, over time, are able to create UTxO
sets that have _useful_ outputs: outputs that will allow us to process future
payments with a _reasonably small_ number of inputs.

If for each payment request of value **_v_** we create a change output of
_roughly_ the same value **_v_**, then we will end up with a distribution of
change values that matches the typical value distribution of payment
requests.

> :bulb: **Example**
>
> Alice often buys bread and other similar items that cost around €1.00 each.
>
> When she instructs her wallet software to make a payment for around
> €1.00, the software attempts to select a set of unspent transaction outputs
> with a total value of around €2.00.
>
> As she frequently makes payments for similar amounts, transactions created by
> her wallet will also frequently produce change coins of around €1.00 in value.
>
> Over time, her wallet will self-organize to contain multiple coins of around
> €1.00, which are useful for the kinds of payments that Alice frequently makes.

#### Principle 3: Performance Management

Searching the UTxO set for additional entries to _improve_ our change outputs
is _only_ useful if the UTxO set contains entries that are sufficiently
small enough. But it is precisely when the UTxO set contains many small
entries that it is less likely for a randomly-chosen UTxO entry to push the
total above the upper bound.

### External Resources

#### Self Organisation in Coin Selection

> | **Title** | Self Organisation in Coin Selection |
> |:--|:--|
> | **Author** | [Edsko de Vries](http://www.edsko.net/) |
> | **Year** | 2018 |
> | **Location** | https://iohk.io/en/blog/posts/2018/07/03/self-organisation-in-coin-selection/ |
>
> This article introduces the [Random-Improve](#random-improve) coin selection
> algorithm, invented by [Edsko de Vries](http://www.edsko.net/).
>
> It describes the three principles of self-organisation that inform the
> algorithm's design, and provides experimental evidence to demonstrate the
> algorithm's effectiveness at maintaining healthy UTxO sets over time.

## Path to Active

### Acceptance Criteria

- [x] There exists one or more reference implementations with appropriate testing illustrating the various properties of coin-selection stated in this document.

### Implementation Plan

#### Reference Implementations

##### Largest-First

Reference implementations of the [Largest-First](#largest-first) algorithm are
available in the following languages:

| _Language_ | _Documentation_ | _Source_ |
| -- | -- | -- |
| **Haskell** | [Documentation](https://hackage.haskell.org/package/cardano-coin-selection/docs/Cardano-CoinSelection-Algorithm-LargestFirst.html) | [Source](https://hackage.haskell.org/package/cardano-coin-selection/docs/src/Cardano.CoinSelection.Algorithm.LargestFirst.html) |

##### Random-Improve

Reference implementations of the [Random-Improve](#random-improve) algorithm
are available in the following languages:

| _Language_ | _Documentation_ | _Source_ |
| -- | -- | -- |
| **Haskell** | [Documentation](https://hackage.haskell.org/package/cardano-coin-selection/docs/Cardano-CoinSelection-Algorithm-RandomImprove.html) | [Source](https://hackage.haskell.org/package/cardano-coin-selection/docs/src/Cardano.CoinSelection.Algorithm.RandomImprove.html) |

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
