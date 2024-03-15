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

-   Finally we filter the selected Utxos such that it contains the minimum amount of asset required for the selection.
-   However, each selected Utxo that is would create a selected Utxo that is NOT the minimum has a 25% random chance of being kept in the selection. The reason for this is to handle dust cleanup where some utxos are quite small and simply clog the utxo graph due to the increase in dust this algorithm could generate. Therefore it is important to cleanup the dust. 25% is an arbitrary value that has optimization potential.
-   Next we add all of our selected Utxos to the global selected Utxos list and remove the newly selected Utxos from the candidateUtxos list!

-   Step 3: Change Selection Function

The Change Selection function creates change outputs that go back to the payment address that contains all of the extra assets and ada that is not used in the outputs of this transaction. This function will have the following parameters:

    -   Our intial coin selection object
    -   A Balance object containing the aggregated asset
    -   A string change address that the change assets will go back to
    -   An integer representing the fee buffer

The idea behind this function is to create output utxos with change that limit the size of future transactions by splitting large utxos or utxos with a lot of assets. For this we introduce 2 constant parameters that can be adjusted to fit your algorithm needs, the maxChangeOuputs which we set to 4, and the idealMaxAssetsPerOutput which we set to 30.

The maxChangeOutputs parameter indicates that we have a maximum of 4 change outputs unless we require additional outputs due to those ideal 4 reaching their size limits. The idealMaxAssetsPerOutput is the ideal maximum number of assets in an output utxo before we create a new output. This value is set to 30 meaning we try to output at max 30 assets in a change output. Having more then 30 is fine but the algorithm attempts to balance utxos such that it does not exceed 30 if we can avoid it.

-   Step 3a)

-   We first want to create a list of assets, sorted by policy ids. The reason for this is that we want to keep assets of the same policy ids in the same output utxos if possible, even if the amount of assets go above 30 per output. This is because assets are grouped by policy ids in outputs and each output would need to duplicate the policy id data which is uneccesary extra bytes of overhead.

-   We are then going to loop through each asset and add it to the most recently created output. If the assets in that output go above the ideal assets per output we create a new output unless the asset is part of an existing policy id. If a change output is over 2kb we create a new output automatically. The max output size on Cardano is 5kb but we are using 2kb to have more evenly split utxos in users wallet for smaller future transactions

-   Step 3b)

-   After looping through each asset we have a list of change outputs. We want to calculate the ada minUtxos required for all of those change outputs.

-   Using this ada minUtxo number along with the amount of ada in the balance we attempt to evenly distribute ada accross the existing change outputs, with the reaminder going to the final change output.

### Implementation Example

An implementation example for all 3 core functions involved in the Optimized Random Improve selection can be found in this fork of the CardanoSharp Library here:

-   Aggregator Function - https://github.com/Orion-Crypto/cardanosharp-wallet/blob/optimized-coin-selection-example/CardanoSharp.Wallet/CIPs/CIP2/CoinSelectionService.cs
-   Select Inputs Function - https://github.com/Orion-Crypto/cardanosharp-wallet/blob/optimized-coin-selection-example/CardanoSharp.Wallet/CIPs/CIP2/CoinSelectionStrategies/OptimizedRandomImproveStrategy.cs
-   Change Selection Function - https://github.com/Orion-Crypto/cardanosharp-wallet/blob/optimized-coin-selection-example/CardanoSharp.Wallet/CIPs/CIP2/ChangeCreationStrategies/MultiSplitChangeSelectionStrategy.cs

## Path to Active

### Acceptance Criteria

-   [x] There exists one or more reference implementations and review by other dapp developers in the Cardano Ecosystem. Also at least 1 additional dapp developer commiting to implementing this algorithm or a slightly modified verision of it to suit their needs.

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
