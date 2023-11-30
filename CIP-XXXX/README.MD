---
CIP: ????
Title: Multi-Stake Delegation from a Single Account
Category: Wallets
Status: Proposed
Authors:
    - Angel Castillo <angel.castillo@iohk.io>
    - Fernando Moreno <fernando.moreno@iohk.io>
    - Martynas Kazlauskas <martynas.kazlauskas@iohk.io>
    - Mircea Hasegan <mircea.hasegan@iohk.io>
    - Rhys Bartels-Waller <rhys.bartelswaller@iohk.io>
Implementors:
    - Angel Castillo <angel.castillo@iohk.io>
    - Mircea Hasegan <mircea.hasegan@iohk.io>
Discussions:
    - https://github.com/cardano-foundation/CIPs/pull/628
Created: 2023-11-30
License: CC-BY-4.0
---

## Abstract

This document presents an alternative approach for Cardano sequential wallets to support multiple stake keys by deriving them from a single account. Building
upon the foundations of [CIP-1852](https://github.com/cardano-foundation/CIPs/tree/master/CIP-1852) and [CIP-0011](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0011), this proposal introduces a simple method for managing multiple delegations within a single account.

## Terminology

Before delving into the specifics of the proposal, it's important to define two key terms that will be used throughout this document:

- **First Payment Key:** This refers to the external (role 0) payment key derived at index 0.

- **First Stake Key:** Similarly, this is the stake key (role 2) derived at index 0.

Throughout this proposal, the terms "first payment key" and "first stake key" will be used to refer to these specific keys.

## Motivation: why is this CIP necessary?
The current philosophy of Cardano wallets, centering around a single stake key per wallet, has served well during the initial adoption phase. However, as the Cardano ecosystem expands and matures, the need for more flexible delegation options becomes evident. This proposal introduces a method for the derivation of multiple stake keys from a single account, combining the original simplicity with flexibility.

### Empowering Smaller Actors
In the current system, moderate stakeholders often find themselves constrained, unable to optimize returns due to limited delegation capabilities. This proposal empowers them to delegate across a diverse set of pools, offering a way to hedge against pool underperformance and sudden changes. It allows for a comprehensive view of their balance within a single account, thus combining convenience with enhanced delegation options. Additionally, Cardano projects are often funded via Initial Stake Pool Offering (ISPO). When multiple ISPOs happen at the same time, users might want to participate in more than one. Multi-delegation enables doing this from a single account.

### Addressing the Challenges for Large Stakeholders
Large stakeholders currently face the challenge of distributing their stake without causing pool over-saturation, which affects potential rewards. The current remedy, which involves segmenting funds into multiple distinct accounts, does not provide a good UX, requiring users to constantly switch across multiple accounts for core operations, or requiring wallet developers to add an abstraction layer on top of user accounts to overcome this issue.

### Efficient Fund Tracking with Optional Privacy
By linking all stake keys to the first payment key, this proposal introduces a transparent and simple mechanism for multi-delegation, greatly simplifying the fund tracking process. This association not only simplifies the delegation and deregistration processes but also facilitates easier tracking of funds and delegations. Besides, this method does not preclude the use of the multi-account approach for users desiring enhanced privacy. Stakeholders can still derive multiple accounts, each potentially capable of multi-delegation, granting them granular control while retaining the option for increased privacy.

### Foundation for Advanced Wallet Features and Enhanced User Experience
One of the underlying rationales of this proposal is to provide a robust foundation for more advanced wallet features. The dynamic nature of this approach offers wallets the opportunity to innovate. For example allowing users to support multiple dReps from a single account, or implementing sophisticated heuristics to maintain stake distribution to different pools. .

## Specification

### Overview

Under this proposal, the constraints of [CIP-0011 ](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0011)regarding the sole derivation index for the stake key are removed. While we introduce the ability to derive stake keys beyond the first , there is no strict requirement to do so in a sequential manner, although it is recommended for logical organization. A pivotal change in this approach is that all derived stake keys must be associated with the first payment key. This consistent association to the first payment key serves as the foundation for the efficient discovery of these stake keys by wallet software and services.

### Multi-Delegating
- **Stake Key Derivation:** Begin by deriving the required number of stake keys needed for multi-delegation. While this derivation does not have to be sequential, it is recommended for clarity and orderly management. Ensure that the gap between any two consecutive active stake addresses does not exceed 20, in line with the [BIP-44](https://github.com/bitcoin/bips/blob/master/bip-0044.mediawiki) address gap limit. 

- **Key Registration:** Once derived, register these stake keys. This registration process remains consistent with current procedures, with the added context that all these new stake keys will be associated with a common payment key.

- **Fund Distribution:** Distribute the funds across addresses formed by pairing the first  payment key with each of the newly created stake keys. This creates an association between all stake delegations. The details of how funds are distributed are specified by the user when creating the multi delegation transaction.

Wallet software can then easily discover all stake keys and associated delegations either by sequential discovery or identifying addresses  containing the first payment credential. 

### Updating the Multi-Delegation
The dynamic nature of multi-delegation facilitates not just participation but also continuous optimization of delegations.

#### Adding Pools
To delegate to additional pools, the first step would involve deriving the necessary number of new stake keys. Then, make a transaction that:  registers the new stake keys, delegates and  distributes funds among addresses that pair the new stake keys with the first payment key.

#### Removing Pools
To remove a pool, the wallet first identifies all addresses associated with the stake key designated for removal. Then, make a transaction that
Transfer all funds from these addresses
withdraw all rewards from their associated reward accounts to one of the accounts that are still in delegation. If no other delegating accounts are left, revert the funds to addresses associated with the first payment key. 
. Deregister stake keys

**Note that all rewards calculated but not distributed will be lost.**

#### Interoperability
Live delegation portfolio might drift overtime due to:
- Receiving funds to a single address 
- Building transactions with software that doesn’t support multi-stake delegation (e.g. via dapp connector)

In order to maintain a record of user’s delegation portfolio preferences , all actions pertaining to stake delegation, including funds transfers, stake key registration, and deregistration, must be executed within a single atomic transaction when performing an update. This transaction should also include the delegation portfolio metadata, using the reserved metadata label 6862 (hexadecimal 0x1ace), as outlined in [CIP-0017](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0017) preferably without any of the optional fields.

Example:

``` Json
{
  "pools": [
    {
      "ticker": "DARK",
      "weight": 42
    },
    {
      "id": "5f3833027fe8c8d63bc5e75960d9a22df52e41bdf62af5b689663c50",
      "weight": 14
    },
    {
      "id": "a16abb03d87b86f30bb743aad2e2504b126286fe744d3d2f6a0b4aec",
      "weight": 37
    },
    {
      "id": "9f9bdee3e053e3102815b778db5ef8d55393f7ae83b36f906f4c3a47",
      "weight": 25
    }
  ]
}
```

The inclusion of the delegation portfolio object as transaction metadata serves to reflect any updates to the user's delegation preferences on-chain. This ensures that external applications retrieving this information are always presented with the most current data, without the need to parse through multiple transactions.

External applications can retrieve the most up-to-date delegation portfolio for a given wallet by scanning the blockchain for the latest transaction with the metadata label 6862 originating from the user's wallet. This transaction will contain the metadata with the current delegation portfolio, thereby affirming the wallet owner's latest delegation preferences.


### Change Balancing Algorithm 

Balancing change is a crucial feature designed to maintain a user’s stake distribution, using the portfolio preferences attached to the delegation transaction. As transactions occur over time, the distribution of funds across different pools will deviate from the initial portfolio percentages as the change would otherwise be concentrated onto a single address, and therefore be delegated to a single pool.  This drift can be corrected while constructing transactions for a user who has defined a multi-delegation intent by reading the preferences from the delegation transaction metadata and distributing the change to best adhere

When implementing this feature, it is essential to maintain the integrity of the change outputs as produced by the input selection algorithm. The design of these algorithms, such as the Random Improve input selection, is aimed at optimizing the overall health of the wallet's UTXO (Unspent Transaction Output) set. This optimization includes avoiding the creation of dust and ensuring that the size of outputs aligns with the user's spending habits over time.

Therefore, the following key principle will guide the balancing change process for wallets that are multi-delegating:

Every multi delegation transaction (creation or update) must include the delegation portfolio metadata specifying the percentage of funds they wish to delegate to each pool. This portfolio serves as a guideline for how funds should be distributed across different stake keys.
When following transactions are built, input selection is performed as usual. The resulting change from the transaction is then evaluated for rebalancing. The structure and size of change outputs determined by the input selection algorithm are preserved.
The change outputs will be distributed as-is across multiple addresses associated with different stake keys, without altering the outputs values. Priority is given to stake keys that are most divergent from the set preferences, thereby gradually realigning the actual distribution with the user's delegation strategy.

#### Benefits and Implementation Considerations

Consistent Delegation Strategy: Ensures that the user's delegation strategy is consistently maintained, even as funds are spent and rewards are received.

UTXO Set Optimization: Maintains the health and efficiency of the UTXO set as intended by the input selection algorithm.

Reduced Manual Adjustments: Minimizes the need for users to manually rebalance their stake across different pools, saving time and effort.

## Reference Implementation

An already working implementation can be found in Lace wallet and the Cardano-js-sdk:

- Lace: https://github.com/input-output-hk/lace
- Cardano JS SDK: https://github.com/input-output-hk/cardano-js-sdk/blob/master/packages/e2e/src/tools/multi-delegation-data-gen/index.ts

## Copyright

CC-BY-4.0
