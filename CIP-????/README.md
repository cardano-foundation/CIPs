---
CIP: ?
Title: Beacon Tokens & Distributed Dapps
Category: Tools
Status: Informational
Authors:
    - fallen-icarus <modern.daidalos@gmail.com>
Implementors: []
Discussions:
Created: 2023-02-21
License: CC-BY-4.0
---

## Abstract
In the absence of atomic delegation, in order for Dapp users to maintain full delegation control of their assets, each user must have his/her own address while using the Dapp. However, this then creates another problem: if all users have their own addresses while using the Dapp, how can users find and interact with each other? This informational CIP explains the usage of Beacon Tokens to solve this "broadcasting" issue. Using beacon tokens, it is possible to create distributed Dapps (e.g., DEXs, p2p lending, etc) where users can not only maintain full delegation control of their assets while using the Dapp, but can also maintain full custody of their assets at all times. These beacon tokens can be generalized to other use cases such as creating an on-chain personal address book tied to - and fully recoverable by - a user's payment pubkey and trustlessly sharing reference scripts with other blockchain users.

## Motivation: why is this CIP necessary?
To date, there has yet to be a Dapp where users maintain full delegation control of their assets while using it. Instead, Dapps usually end up pooling user assets together and therefore are forced to delegate the assets all together. On Proof-of-Stake (PoS) blockchains, this is an existential security issue. The more popular a Dapp becomes, the more centralized the underlying blockchain will be. Some Dapps try to address this concern by:

1. Fractionalizing the asset pools - instead of all assets being at one address and delegated to only one stake pool, the assets are split among several addresses and delegated to several separate stake pools.
2. Issuing governance tokens - each user gets a vote on where the pooled assets will be delegated.

This is a general pattern holds for all kinds of Dapps: DAOs, DEXs, p2p lending, etc. Unfortunately, the above mitigations do not fully solve the issue; the blockchain is still significantly more centralized than if full delegation control was used. 

### Why are Dapps designed like this?
Ask yourself the following question:
```
If user assets are segregated into separate addresses, how do users find all of the relevant information (assets, transaction history, etc) for the Dapp?
```

When assets are pooled together, the above questions is not a concern:

```
There is only one address to be concerned with and all of the relevant information is easily accessed by looking up the information for that central address.
```

Some have assumed that the Cardano blockchain, as it is now, is unable to support a Dapp where users maintain full delegation control of their assets. This CIP shows that this assumption is wrong. Thanks to Cardano's native tokens, it is already possible to design all kinds of Dapps where users can maintain full delegation control of their assets, and by extension, can maintain full custody of their assets while using the Dapp.

## Specification

### Beacon Tokens

#### What are Beacon Tokens?
All native tokens on Cardano broadcast their current address and any transactions they were ever a part of at all times. Take a look at the following off-chain apis:

| Task | Koios Api | Blockfrost Api |
|--|--|--|
| Addresses with asset | [api](https://api.koios.rest/#get-/asset_address_list) | [api](https://docs.blockfrost.io/#tag/Cardano-Assets/paths/~1assets~1%7Basset%7D~1addresses/get) |
| Txs including asset | [api](https://api.koios.rest/#get-/asset_txs) | [api](https://docs.blockfrost.io/#tag/Cardano-Assets/paths/~1assets~1%7Basset%7D~1transactions/get) |

Knowing EXACTLY which addresses/transactions have the token, you can then use the same off-chain api services to take a closer look at the addresses/transactions:

| Task | Koios Api | Blockfrost Api |
|--|--|--|
| UTxO info of address | [api](https://api.koios.rest/#post-/address_info) | [api](https://docs.blockfrost.io/#tag/Cardano-Addresses/paths/~1addresses~1%7Baddress%7D~1utxos/get)|
| Tx metadata | [api](https://api.koios.rest/#post-/tx_metadata) | [api](https://docs.blockfrost.io/#tag/Cardano-Transactions/paths/~1txs~1%7Bhash%7D~1metadata/get)|

Take a look at the apis and see for yourself how much information can be gleaned from these off-chain queryies. Here is a short list of what you can get:

1. Any reference scripts stored at the address and their associated UTxO ids.
2. Any datums stored at the address.
3. The stake address of the address.
4. The metadata history of each transaction that had the token.
5. The datum history of each utxo that held the token.

These queries are always possible for ALL Cardano native tokens. However, while all native tokens always broadcast this information, this broadcasting is usually not the intended purpose of the native token (e.g., governance tokens). **A *Beacon Token* is a native token whose ONLY purpose is to broadcast information**. If you want to broadcast certain transactions, just make sure the beacon token is part of those transaction. If you want to broadcast certain addresses, just make sure the beacon is stored at the address. If you want to broadcast certain UTxOs, just make sure the beacon is stored in those UTxOs.

#### Using Beacon Tokens
Every native token has two configurable fields: the policy id and the token name. The policy id will be application specific while the token name can be data specific. To use a beacon token, simply create a native token that is unique to your application and if necessary, control how UTxOs with beacons can be spent.

I have created a few basic reference implementations:

- [Cardano-Address-Book](https://github.com/fallen-icarus/cardano-address-book) - a personal payment address book on Cardano that is tied to a user's payment pubkey. It uses the Tx metadata api to broadcast all metadata attached to the transactions containing the beacon. The address book is the aggregation of all the metadata. This application can be generalized to store ANY information in a way that is unique to, and protected by, the user's payment pubkey. The beacon token name is the user's payment pubkey hash. Minting the beacon requires the signature of the payment pubkey hash used for the token name. This guarantees that only Alice can mint Alice's address book beacon.

- [Cardano-Reference-Scripts](https://github.com/fallen-icarus/cardano-reference-scripts) - trustless p2p sharing of Cardano reference scripts. It uses the UTxO info api to broadcast all of the UTxOs that contain each beacon. The beacon token name is the script hash of the reference script being shared. Minting the beacon requires that the beacon is stored with the reference script whose hash matches the beacons token name. This example also uses a helper plutus spending script to guarantee the burning of the beacon when a reference script UTxO is consumed. 

### Distributed Dapps
As already alluded to, a *distributed Dapp* is one where all users have their own personal address while using the Dapp. This is opposite to *concentrated Dapps* where all users share one or a few addresses while using the Dapp.

All distributed Dapps will use beacon tokens to aggregrate all of the necessary information for using the Dapps. Every distributed Dapp follows the same general design pattern.

1. All user addresses use the same spending script for a given use case.
2. All user addresses MUST have a staking credential.
3. The spending script delegates the authorization of owner related actions to the address' staking credential - i.e., the staking key must sign or the staking script must be executed in the same tx.
4. The spending script's hash is hard-coded into the beacon minting policy and the minting policy enforces that the beacons can only be minted to an address of that spending script.
5. The datums for the spending script must have the policy id of the beacons so that it can force proper usage of the beacons (such as burning when necessary).

#### Advantages
Since each user has his/her own address for the Dapp, the following are now possible:

1. **Full delegation control**
2. Users maintain full custody of their assets while using the Dapp thanks to the staking credential needing to approve owner related actions.
2. The address itself can act as the User ID. There is no need to place this in a datum and guard its usage.

Further, the Dapp itself gains some nice features:

1. Since there are at least as many UTxOs as there are users, the distributed Dapp is naturally concurrent and gets more concurrent as the number of users increases.
2. Upgradability can happen democratically - i.e., users can choose whether to move their assets to an address using a newer version of the Dapp's spending script.
3. The Dapp is easily integratable into any frontend.
4. Since the address itself can act as the User ID, in some cases, the Dapp's logic can be dramatically simplified.

#### Cardano-Swaps: The First Ever Defi Application to Support Full Delegation Control
I created a DEX proof-of-concept that uses the above design principles. The result is the `Cardano-Swaps` DEX; it is fully open-sourced and can be found [here](https://github.com/fallen-icarus/cardano-swaps). As the title of this section states, to the best of my knowledge, `Cardano-Swaps` is the first ever Defi application to support full delegation control for its users. It is fully operational and can be tested on either the PreProd Testnet or the mainnet. In addition to full delegation control, it has the following features:

1. Composable atomic swaps.
2. Users maintain custody of their assets at all times.
3. Naturally concurrent and gets more concurrent the more users there are. No batchers are required.
4. Liquidity naturally spreads to all trading pairs instead of being siloed into specific trading pairs.
5. There is no impermanent loss.
6. ADA is all you need to interact with the DEX.
7. Upgradability can happen democratically.
8. Easy to integrate into any frontend.

## Rationale: how does this CIP achieve its goals?
By being able to easily broadcast the necessary information for a Dapp, user assets can be segregated into separate addresses and therefore enable full delegation control while using the Dapp. Thanks to the broadcasting, the segregated addresses can act as if all the assets were pooled together (checkout the `Cardano-Swaps` README to see how liquidity is achieved; it arises naturally).

The fact that beacon tokens are generalizable for aggregating any information on the blockchain is just a bonus.

### Does the reliance on off-chain apis create MORE centralization?
The short answer is no. It is important to look at what the limiting centralization factors are for any design. 

Concentrated Dapps Centralization Bottlenecks:

1. Full delegation control is not possible without atomic delegation. This is baked into the on-chain design of the Dapp. 

2. Batchers are needed since there aren't enough UTxOs for each user. For most Dapps, it is not easy to become a batcher due to needing to be selected by some entity. Further, these batchers are effectively middlemen that can take advantage of their unique positions. While batcher protocols can be improved, this is a work in progress and is currently an off-chain centralization bottleneck for concentrated Dapps.

Distributed Dapps Centralization Bottlenecks:

1. Reliance on off-chain api services. This is the only centralization bottleneck for distributed Dapps. And similarly to batchers, new innovations are improving this. For example, Koios is more decentralized than Blockfrost.

What should stand out to you is the following:
```
Concentrated Dapps have centralization bottlenecks both in their on-chain design and their off-chain design.

Distributed Dapps only have a centralization bottleneck in their off-chain design.
```

This means that Distributed Dapps are better positioned to naturally grow more decentralized as the off-chain services become more decentralized.

## Path to Active
It is already possible to create distributed Dapps. No updates to Cardano are necessary.

## Copyright
[CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode)