---
CIP: 2
Title: Optimized Coin Selection Algorithms for Cardano
Category: Wallets
Authors:
    - Nicholas Maselli <maselli.nicholas@gmail.com>
Implementors: CardanoSharp 7, SaturnNFT, Levvy Finance
Discussions:
Status: Pending
Created: 2024-14-03
License: CC-BY-4.0
---

## Abstract

Coin Selection algorithms have become a critical part of the Cardano ecosystem. These algorithms choose a set of input Utxos for a given set of new Outputs.

This CIP aims to present optimized coin selection algorithms to enable Wallets and Dapps to interact with smart contracts and native assets such as tokens and NFTs in a more efficient way. The goal of these algorithms is to primarily reduce the size of transactions as well as reduce the mem and step required for smart contract executions.

## Motivation: why is this CIP necessary?

<b>Cardano needs to scale.</b> As the ecosystem grows and new users come in, blocks are regular at 100% load with 88KB per block allocation. Recently, events such as the Lil Sappys NFT mint have pushed the Cardano blockchain loan to over 100% for several hours, preventing anyone from using the chain and providing an awful user experience to new users who complain on social media and give the ecosystem a bad repution.

<b>This can't continue if Cardano is to succeed.</b>

Currently the existing CIP-2 for coin selection is not sufficient as it was developed in a time before native assets and smart contracts were live on the Cardano Blockchain. Many existing dapps are using extremely poor coin selection resulting in transactions that are 2,3, sometimes 5 times larger then neccesary while also creating outputs that are difficult to handle in future coin selections.

This CIP aims to provide at least 1 algorithm and open the conversation for multiple algorithsm to exponentially improve coin selection which will decrease transaction sizes accross the board and increase Cardano's throughput.

Optimizations are priorized in this order for this CIP:

-   Transaction size reduction
-   Change Output size reduction for future transactions
-   Dust manage to prevent large small dust Utxos from piling up.

### Scope

CIP-2 explains the basics of coin selection, so I won't repeat those here. Instead I will simply present an algorithm for optimizating coin selection. This algorithm will include optimizing the standard coin selection with change selection while also containing suggestions for optimizing collateral selection and optimizing smart contract transactions.

This algorithm will be presented with the following composable structure, allowing for coin and change selection starstrategies to be composed together:

-   Aggregator Function
-   Input Selection Function
-   Change Selection Function

### Algorithms

Random improve was an original algorithm presented in CIP-2, this algorithm had a series of good ideas that can be expanded upon here. The first proposed algorithm will simply Optimized Random Improve.

#### Optimized Random Improve

Unlike random improve which operated on a per output basis. This optimized random improve algorithm will operate on a PER ASSET basis. Meaning the algorithm will be designed to operate on and select inputs that satisfy values for the various native assets in this transaction.

-   Step 1: Aggregator Function

The aggregator function is the function that calls all of the other small functions that will be presented. The other functions such as the input selection can be swapped out for input selection functions with the same parameters to allow for coin selection strategies to be interchangable.

The parameters to the aggregator function are as follows:

    -   A list of transaction outputs that we need to select inputs for
    -   A list of candidate input utxos
    -   A string address to send the change too
    -   A token data representing the assets being minted
    -   A list of required input utxos
    -   An integer representing the input utxo limit
    -   An unsigned long representing a Fee buffer, extra ada checks to account for a potential

-   Step 1a)

    -   The first step is to create an object to store the selected Utxos and the Change Outputs which will be evaluated repeatedly throughout the algorithm.
    -   Next, we need to combined all of our assets from all of the outputs into a single list of assets, these should take into account minted assets as well as a fee buffer which will allow the transaction to work for any fee below the buffer.

-   Step 1b)

    -   For each asset in our asset list we will call our "SelectInput" function (which will be described in Step 2)
    -   After selecting inputs, we check to ensure that the inputs selected contain a sufficient balance of the asset for this iteration of the loop. If not we throw an "Insufficient Balance" error
    -   After calling the "SelectInput" function for all assets, we do it one more time for ADA, and once again check to ensure that the inputs selected have the required amount of ada or more.

-   Step 1c)

    -   Now onto change selection, we make a preliminary call to our "CalculateChange" function (which will be described in Step 3) to get a preliminary set of change outputs that we store in our initial coin selection object. These preliminary outputs are mainly meant to calculate the required minUtxos in our change selection.
    -   Next, we calculate the amount of ada in those preliminary change outputs AND we calculate the minimum change Ada required. The intention here is to check to ensure the change amount is greater then the minChangeAdaRequired. If it is not, we need to perform additional calculations.

-   Step 1d)

    -   We need to create a while loop, that will continuously loop while our change value < minChangeAdaRequired && we have available candidate Utxos left
    -   We calculate a new ada value which we need to select input utxos against. This new ada value is the minChangeAdaRequired - change + the sum of the ada in the selected Utxos
    -   We once again call our "SelectInput" function followed by a has sufficient balance check for ADA, and repeat step 1c.
    -   We repeat step 1d until we have no more utxos to select OR until the change < minChangeAdaRequired while loop criteria is false.

-   Step 1e)

    -   Finally, we have our new selected Utxos and our change outputs and we include them in our transaction to be submitted later to the blockchain.

-   Step 2: Select Inputs Function

The select inputs function is where most of the innovation in this CIP exists. This function will have the following parameters:

    -   Our intial coin selection object
    -   A list of candidate input utxos
    -   A long amount repesenting the amount of asset we are selecting inputs for
    -   A token data representing the asset we are selecting inputs for
    -   A list of required input utxos
    -   An integer representing the input utxo limit

-   Step 2a)

-   We first need to get the current amount of asset we have in our already selected utxos. If this amount is greater than or equal to the required amount, we can return.
-   We are going to loop through all of our candidate utxos, but first we perform a filter and then a sort to get the utxos by order of descending asset amount.
-   We we will now perform a while loop until there are no more available utxos, or the amount of asset is greater then the required amount, or we have required the utxo limit. Step 2b describes the functionality of this loop

-   Step 2b)

-   We first need to make sure we havent selected too many utxos such that we are over the limit. If we have and the amount is not larger then the required amount, we need to clear our current selection for this loop and continue through the loop.
-   We select a random Utxo from our descending Utxo list, add it to a temporary new selected Utxos list, and remove it from the descending list.
-   We calculate the amount of asset in that Utxo and add it to our sum, after which we check the while loop conditions again.
-   It is important to note for this loop that we require a minimum of 3 inputs selected (or less depending on the limit) if the asset we are looking for is ada. This is to allow us to choose potentially smaller utxo amounts in later parts of the algorithm without getting unlucky with a single gigantic utxo that we dont need to use.

-   Step 2c)

-   Now we must improve the random selection, we repeat this step twice to get some additional optimization performance
-   We create two a lists of objects that contain a List of utxos, the sum amount of the asset we are looking for in those utxos AND most importantly the quantity of OTHER DISTINCT assets in the selected Utxos. This is critical as we will be optimizing on reducing the total number of OTHER DISTINCT assets in the output utxos

    1. The first object list will have the new selected utxos sorted by descending number of assets such that selected utxos with large numbers of other distinct assets appear first
    2. The second object list will have the remaining utxos sorted by the ascending number of assets such that remaining utxos with small numbers of other distinct assets appear first

-   We loop through all assets in the remaining utxo set while keeping an index pointer for the selectedUtxo list, if the number of assets in the remaining utxo we are looking at is less then the number of assets in the selectedUtxo at our point, we swap them and increment the pointer. NOTE: We only do this if we still have more then required amount of asset we are looking for in the selected Utxo set.

-   Step 2d)

-   Finally

---

---

---

---

---

The algorithm proceeds according to the following sequence of steps:

-   **Step 1**

    If the [available UTxO list](#available-utxo-list) is _empty_:

    -   Terminate with a [UTxO Balance
        Insufficient](#utxo-balance-insufficient) error.

    If the [available UTxO list](#available-utxo-list) is _not empty_:

    -   Remove an UTxO entry from the head of the [available UTxO
        list](#available-utxo-list) and add it to the [selected UTxO
        set](#selected-utxo-set).

-   **Step 2**

    Compare the total size **_n_**<sub>selected</sub> of the [selected UTxO
    set](#selected-utxo-set) with the [maximum input
    count](#maximum-input-count) **_n_**<sub>max</sub>.

    -   If **_n_**<sub>selected</sub> > **_n_**<sub>max</sub> then:

        -   Terminate with a [Maximum Input Count
            Exceeded](#maximum-input-count-exceeded) error.

    -   If **_n_**<sub>selected</sub> ≤ **_n_**<sub>max</sub> then:

        -   Go to step 3.

-   **Step 3**

    Compare the total value **_v_**<sub>selected</sub> of the [selected UTxO
    set](#selected-utxo-set) to the total value **_v_**<sub>requested</sub> of
    the [requested output set](#requested-output-set):

    -   If **_v_**<sub>selected</sub> < **_v_**<sub>requested</sub> then go to
        step 1.
    -   If **_v_**<sub>selected</sub> ≥ **_v_**<sub>requested</sub> then go to
        step 4.

-   **Step 4**

    Return a [coin selection](#coin-selection) result where:

    -   The _inputs_ set is equal to the [selected UTxO
        set](#selected-utxo-set).

    -   The _outputs_ set is equal to the [requested output
        set](#requested-output-set).

    -   If **_v_**<sub>selected</sub> > **_v_**<sub>requested</sub> then:

        -   The _change_ set contains just a single [coin](#coin-value) of value
            (**_v_**<sub>selected</sub> − **_v_**<sub>requested</sub>).

    -   If **_v_**<sub>selected</sub> = **_v_**<sub>requested</sub> then:

        -   The _change_ set is empty.

#### Random-Improve

The **Random-Improve** coin selection algorithm works in _two phases_:

-   In the **first phase**, the algorithm iterates through each of the
    [requested outputs](#requested-output-set) in _descending order of coin
    value_, from _largest_ to _smallest_. For each output, the algorithm
    repeatedly selects entries _at random_ from the [initial UTxO
    set](#initial-utxo-set), until each requested output has been associated
    with a set of UTxO entries whose _total value_ is enough to pay for that
    ouput.

-   In the **second phase**, the algorithm attempts to _expand_ each
    existing UTxO selection with _additional_ values taken at random from the
    [initial UTxO set](#initial-utxo-set), to the point where the total value
    of each selection is as close as possible to _twice_ the value of its
    associated output.

After the above phases are complete, for each output of value
**_v_**<sub>output</sub> and accompanying UTxO selection of value
**_v_**<sub>selection</sub>, the algorithm generates a _single_ change output
of value **_v_**<sub>change</sub>, where:

> **_v_**<sub>change</sub>
> = **_v_**<sub>selection</sub>
> − **_v_**<sub>output</sub>

Since the goal of the second phase was to expand each selection to the point
where its total value is _approximately twice_ the value of its associated
output, this corresponds to a change output whose target value is
_approximately equal_ to the value of the output itself:

> **_v_**<sub>change</sub>
> = **_v_**<sub>selection</sub>
> − **_v_**<sub>output</sub>
>
> **_v_**<sub>change</sub>
> ≈ <span>2</span>**_v_**<sub>output</sub>
> − **_v_**<sub>output</sub>
>
> **_v_**<sub>change</sub>
> ≈ **_v_**<sub>output</sub>

##### Cardinality

The Random-Improve algorithm imposes the following cardinality restriction:

-   Each entry from the [initial UTxO set](#initial-utxo-set) is used to pay
    for _at most one_ output from the [requested output
    set](#requested-output-set).

As a result of this restriction, the algorithm will fail with a [UTxO Not
Fragmented Enough](#utxo-not-fragmented-enough) error if the number of entries
in the [initial UTxO set](#initial-utxo-set) is _smaller than_ the number of
entries in the [requested output set](#requested-output-set).

##### State

At all stages of processing, the algorithm maintains the following pieces of
state:

1.  **Available UTxO Set**

    This is initially equal to the [initial UTxO set](#initial-utxo-set).

2.  **Accumulated Coin Selection**

    The accumulated coin selection is a [coin selection](#coin-selection) where
    all fields are initially equal to the _empty set_.

##### Computation

The algorithm proceeds in two phases.

-   **Phase 1: Random Selection**

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

-   **Phase 2: Improvement**

In this phase, the algorithm attempts to improve upon each of the UTxO
selections made in the previous phase, by conservatively expanding the
selection made for each output in order to generate improved change
values.

During this phase, the algorithm:

-   processes outputs in _ascending order of coin value_.

-   continues to select values from the [available UTxO
    set](#available-utxo-set).

-   incrementally populates the
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

    -   **Condition 1**: we have moved closer to the _ideal_ value:

        abs (_ideal_ − **_v_<sub>1</sub>**) <
        abs (_ideal_ − **_v_<sub>0</sub>**)

    -   **Condition 2**: we have not exceeded the _maximum_ value:

        **_v_<sub>1</sub>** ≤ _maximum_

    -   **Condition 3**: when counting cumulatively across all outputs
        considered so far, we have not selected more than the _maximum_ number
        of UTxO entries specified by [Maximum Input
        Count](#maximum-input-count).

3.  **Creates a _change value_** for the output, equal to the total value
    of the _improved UTxO selection_ for that output minus the value **_v_**
    of that output.

4.  **Updates the [accumulated coin
    selection](#accumulated-coin-selection-1)**:

    -   Adds the _output_ to the _outputs_ field;
    -   Adds the _improved UTxO selection_ to the _inputs_ field;
    -   Adds the _change value_ to the _change values_ field.

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

> | **Title**    | Self Organisation in Coin Selection                                           |
> | :----------- | :---------------------------------------------------------------------------- |
> | **Author**   | [Edsko de Vries](http://www.edsko.net/)                                       |
> | **Year**     | 2018                                                                          |
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

-   [x] There exists one or more reference implementations with appropriate testing illustrating the various properties of coin-selection stated in this document.

### Implementation Plan

#### Reference Implementations

##### Largest-First

Reference implementations of the [Largest-First](#largest-first) algorithm are
available in the following languages:

| _Language_  | _Documentation_                                                                                                                    | _Source_                                                                                                                        |
| ----------- | ---------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| **Haskell** | [Documentation](https://hackage.haskell.org/package/cardano-coin-selection/docs/Cardano-CoinSelection-Algorithm-LargestFirst.html) | [Source](https://hackage.haskell.org/package/cardano-coin-selection/docs/src/Cardano.CoinSelection.Algorithm.LargestFirst.html) |

##### Random-Improve

Reference implementations of the [Random-Improve](#random-improve) algorithm
are available in the following languages:

| _Language_  | _Documentation_                                                                                                                     | _Source_                                                                                                                         |
| ----------- | ----------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| **Haskell** | [Documentation](https://hackage.haskell.org/package/cardano-coin-selection/docs/Cardano-CoinSelection-Algorithm-RandomImprove.html) | [Source](https://hackage.haskell.org/package/cardano-coin-selection/docs/src/Cardano.CoinSelection.Algorithm.RandomImprove.html) |

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
