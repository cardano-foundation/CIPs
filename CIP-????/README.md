---
CIP: ?
Title: Beacon Tokens
Category: Tools
Status: Proposed
Authors:
    - fallen-icarus <modern.daidalos@gmail.com>
Implementors: []
Discussions:
Created: 2023-01-23
License: CC-BY-4.0
---

# CIP-XXXX: Beacon Tokens

## Abstract
In the absence of atomic delegation, in order for Dapp users to maintain full delegation control of their assets, each user must have his/her own address while using the Dapp. However, this then creates another problem: if all users have their own addresses while using the Dapp - and therefore their own instances of the Dapp's smart contract - how can users find and interact with each other? This informational CIP explains the usage of Beacon Tokens to solve this "broadcasting" issue. Using beacon tokens, it is possible to create fully decentralized Dapps (e.g., DEXs, p2p lending, etc) where users can not only maintain full delegation control of their assets while using the Dapp, but can also maintain full custody of their assets at all times. These beacon tokens can also be generalized to other use cases such as creating an on-chain personal address book tied to - and fully recoverable by - a user's payment pubkey.

## Motivation: why is this CIP necessary?
To date, there has yet to be a Dapp where users maintain full delegation control of their assets while using it. Instead, Dapps usually end up pooling user assets together and therefore are forced to delegate the assets all together. On Proof-of-Stake (PoS) blockchains, this is an existential security issue. The more popular a Dapp becomes, the more centralized the underlying blockchain will be. Some Dapps try to address this concern by:

1. Fractionalizing the asset pools - instead of all assets being at one address and delegated to only one stake pool, the assets are split among several addresses and delegated to several separate stake pools.
2. Issuing governance tokens - each user gets a vote on where the pooled assets will be delegated.

Unfortunately, the above mitigations do not fully solve the issue; the blockchain is still significantly more centralized than if full delegation control was used. 

### Why are Dapps designed like this?
Pooling user assets together has been deemed to be the more efficient way of designing dapps. Ask yourself the following questions:

- If user assets are segregated into separate addresses, how does the Dapp get liquidity?
- If users have their own smart contracts (by definition of having their own addresses), how can other users find the right reference scripts in order to remotely interact with each user's address?

When assets are pooled together, the above questions are not a concern:

- The assets are centrally located and therefore the liquidity is where the assets are.
- Since all the assets are using the exact same address, there is only one possible smart contract script to use.

It has been assumed that the Cardano blockchain, as it is now, is unable to support a Dapp where users maintain full delegation control of their assets. This CIP shows that this assumption is wrong. Thanks to Cardano's native tokens, it is already possible to design all kinds of Dapps where users can maintain full delegation control of their assets, and by extension, can maintain full custody of their assets while using the Dapp.

## Specification
### What is a Beacon Token?
All native tokens on Cardano broadcast their current address and any transactions they were ever a part of at all times. Take a look at the following off-chain apis:

| Task | Koios Api | Blockfrost Api |
|--|--|--|
| Addresses with asset | [api](https://api.koios.rest/#get-/asset_address_list) | [api](https://docs.blockfrost.io/#tag/Cardano-Assets/paths/~1assets~1%7Basset%7D~1addresses/get) |
| Txs including asset | [api](https://api.koios.rest/#get-/asset_txs) | [api](https://docs.blockfrost.io/#tag/Cardano-Assets/paths/~1assets~1%7Basset%7D~1transactions/get) |

Knowing EXACTLY which addresses/transactions have the token, you can then use the same off-chain api services to take a closer look:

| Task | Koios Api | Blockfrost Api |
|--|--|--|
| UTxO info of address | [api](https://api.koios.rest/#post-/address_info) | [api](https://docs.blockfrost.io/#tag/Cardano-Addresses/paths/~1addresses~1%7Baddress%7D~1utxos/get)|
| Tx metadata | [api](https://api.koios.rest/#post-/tx_metadata) | [api](https://docs.blockfrost.io/#tag/Cardano-Transactions/paths/~1txs~1%7Bhash%7D~1metadata/get)|

Take a look at the apis and to see for yourself how much information can be gleaned from these off-chain queries. *Any reference scripts stored at the address - as well as the info needed to remotely execute them - are returned by the UTxO info query*. 

These queries are always possible for ALL Cardano native tokens. However, while all native tokens always broadcast this information, this broadcasting is usually not the intended purpose of the native token (e.g., governance tokens). **A *Beacon Token* is a native token whose ONLY purpose is to broadcast information**. If you want to broadcast certain transactions, just make sure the beacon token is part of the transaction. If you want to broadcast certain addresses, just make sure the beacon is stored at the address.

### Using Beacon Tokens
To use a beacon token, simply create a native token that is unique to your application. I have created two fully open-sourced reference implementations that you can checkout:

- [Cardano-Swaps](https://github.com/fallen-icarus/cardano-swaps) - a Cardano DEX proof-of-concept that uses composable atomic swaps. It is fully built and can be tested on the Preprod Testnet. It uses the UTxO info api to broadcast all open swaps and their respective reference scripts.
- [Cardano-Address-Book](https://github.com/fallen-icarus/cardano-address-book) - a personal payment address book on Cardano that is tied to a user's payment pubkey. It uses the Tx metadata api to broadcast all metadata attached to the transactions containing the beacon. The address book is the aggregation of all the metadata. This application can be generalized to store ANY information in a way that is unique to, and protected by, the user's payment pubkey.

As the address book example shows, these beacon tokens can be used for more than just Dapps.

## Rationale: how does this CIP achieve its goals?
By being able to easily broadcast the necessary information for a Dapp, user assets can be segregated into separate addresses and therefore enable full delegation control while using the Dapp. Thanks to the broadcasting, the segregated addresses can act as if all the assets were pooled together (checkout the Cardano-Swaps README to see how liquidity is achieved; it arises naturally).

Even better, since users will have their own smart contract instances, the user's payment pubkey can be hardcoded into his/her respective instance to enable "admin control" over all assets at that address. In other words, the user maintains full custody of his/her assets at the address since the assets are protected by his/her payment pubkey. Cardano-Swaps does this to only allow the user to close or update prices of his/her open swaps. Likewise, the Cardano-Address-Book only allows the user to mint/burn his/her personal beacon.

### Does the reliance on off-chain apis create more centralization?
The short answer is no.

When user assets are pooled together, batchers are needed since there aren't enough pools for each user. These batchers are another centralizing factor of any DEX that pools user assets together. When user assets are segregated into separate addresses, the number of UTxOs available grows with the number of users of the Dapp. In other words, Dapps that pool assets have their maximum concurrency "hardcoded" by the number of pools available to interact with while Dapps that segregate user assets have their maximum concurrency expand or contract with the demand on the Dapp. Queues only form when the concurrency is not enough for the demand; batchers are only required in this situation.

It is important to look at what the limiting centralization factors are for any design:

- Pooled assets - the limiting factors are the use of batchers and the lack of full delegation control. While new innovations in the batchers can make the batchers less centralizing, the lack of full delegation control cannot be solved without atomic delegation.
- Segregated assets - the limiting factor is the off-chain api service. New innovations will improve this. For example, Koios is more decentralized than Blockfrost. This is the only centralizing bottleneck for this design. This means that this design is well positioned to naturally grow more decentralized as the off-chain services become more decentralized.

## Copyright
[CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode)
