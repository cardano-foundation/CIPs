---
CPS: ?
Title: Cardano Pointer Address Removal
Status: Open
Category: Core
Authors:
    - Andrew Westberg <andrewwestberg@gmail.com>
Proposed Solutions: []
Discussions:
    - https://github.com/cardano-foundation/cips/pulls/?
Created: 2022-11-11
---

## Abstract
On Cardano, pointer addresses (having address prefix 0x41 or 0x51) have existed since the launch of Shelley Mainnet. There is a grand total of 11 of them in the ledger state as of the writing of this document. Of those, only 3 are correctly formatted and point to an actual stake address registration location on chain. Due to their lack of usage and inherent negative qualities discussed below, I propose we deprecate pointer addresses. 

## Problem
The `minUTxO` amount on Cardano depends on the length of the address holding it. For example, sending a token to an Enterprise address requires less ada be locked than sending it to a typical wallet receiving address. In the same vein, pointer addresses are shorter than typical receiving addresses. On the surface, this seems like a good thing (less locked ada), but pointer addresses have other downsides if they were to become widely adopted.

### Problem 1
Pointer Addresses require a secondary chain lookup. One of the larger jobs of cardano-node is to maintain the ledger state and be able to take an epoch snapshot determining how much stake is owned by every staked address. For a typical receive address containing both a payment part and a staking part, there is no issue. The cardano-node can simply scan the ledger and categorize all the ada into stake addresses appropriately. If Pointer addresses were to see widespread use, every pointer address would require an additional lookup on the chain to find the actual staking address associated with it. At minimum, it would require an additional temporary cache to map pointers to their stake address. There is a performance penalty for this lookup.

### Problem 2
Pointer Addresses demonstrate an anti-incentive pattern. Given that they reduce locked ada, they are less expensive to use. However, since they actually increase processing requirements of the node, they should be more expensive to use.

### Problem 3
Pointer Addresses require additional steps for a Wallet to get a user's ada into a staked state. In a typical wallet, ada is put into receive addresses containing both payment/stake addresses. The minute a stake key is registered and delegated, often within the same transaction, all of the user's ada becomes staked. If a wallet was using pointer addresses, it would first have to register the stake key on chain and wait for it to settle. Then, all ada would need to be moved into new pointer addresses referencing the stake key registration location. Finally, the wallet would need to be delegated. At minimum, it requires two transactions to get a wallet staked, where it only requires a single transaction with a typical wallet.

## Use cases
There's no real use case other than to close the door on a technology that isn't useful to Cardano. The idea is to remove the perverse incentives brought about by pointer addresses before wallet makers realize that they can be cheaper to operate for users who have large amounts of token types. By deprecating pointer addresses, we remove the potential performance impact that a wallet employing pointer addresses would have on the ecosystem.


## Goals
 1. Remove perverse incentives of Pointer Addresses
 2. Prevent performance impacts of Pointer Addresses
 3. Continue using a single transaction to both register a staking key and delegate all ada in a wallet to a pool.

## Open Questions
What is the best way to deprecate pointer addresses?
 - Hardfork and not allow them to be used at all for output utxos? 
 - Hardfork and allow them to be used, but don't count them as staked?