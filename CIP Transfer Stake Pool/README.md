---
CIP: ?
Title: Transferring Stake Pool Ownership
Author: NOMAD Pool (nomadpool.io@protonmail.com)
Comments-URI: https://forum.cardano.org/t/cip-transferring-stake-pool-ownership/95329
Status: Draft
Type: Standards
Created: 2022-03-10
License: CC-BY-4.0
---

# Abstract

This CIP proposes a way to transfer ownership of a stake pool from one pair of cold keys to another. 

------

# Motivation

[CIP 1853](https://github.com/cardano-foundation/CIPs/tree/master/CIP-1853) describes how node operators should derive their stake pool cold keys according to a hierarchical deterministic (HD) standard. However, **many existing stake pool operators have *not* derived their cold keys accordingly, and are thus unable to implement the standard without starting and marketing a new pool from scratch. **

Additionally, the current protocol is such that when stake pools retire, the pool's delegates are responsible for re-delegating to a new pool, lest they miss out on future rewards. A pool-ownership transfer mechanism could "point" the old pool's delegation certificates at the new pool.

Furthermore, a pool-transfer mechanism would allow SPO's who are no longer willing or able to administer their pool to sell their pool to a prospective buyer, without giving up custody of their cold keys. This is an important feature because it allows such operators to maintain custody of the *history* of their time as an SPO.

-------

# Specification

Pool ownership can only be transferred to unused cold keys, such that no pair of keys can ever be responsible for more than one pool. The transfer itself is initiated by specifying the new cold key-pair in the deregistration certificate of the old pool.


### new deregistration-certificate flag
This certificate will act as a "pointer" for a pool's entire history, including its current stake distribution. 

Similar to how any ADA that resides at a stake address is automatically delegated to the pool that address is pointed to, any stake addresses delegating to the old pool are automatically pointed at the new pool. 

Upon pool retirement, all delegation certificates from the current pool are "pointed" to the new pool. This is to ensure that the old pool is not pointed towards an existing pool, but rather a newly registered pool.

A  `--new-cold-verification-key-file` flag is added to the `cardano-cli stake-pool deregistration-certificate` sub-command, requiring signatures from both cold-keys, as follows:

```
cardano-cli stake-pool deregistration-certificate \
--current-cold-verification-key-file current-cold.vkey \
--new-cold-verification-key-file new-cold.vkey \
--epoch <EPOCH_NUMBER>    # bound by the eMax parameter
--out-file <FILE_PATH>
```

**The new pool must be registered on an epoch equal to or  greater than the one specified by the below deregistration certificate.** 

Pool deposit fee of the old pool will be returned to the old reward account, as usual.

--------

# Rationale

This CIP would benefit from being implemented at the same time as additional SPO-related features are implemented that require a HFC. Most notably - alongside a CIP/change that introduces group ownership of pools [Conclave](https://iohk.io/en/research/library/papers/conclavea-collective-stake-pool-protocol/), and/or contingent staking mechanisms ([like this one](https://forum.cardano.org/t/cip-add-the-ability-for-spo-to-refuse-stake-addresses/94087/6))



### Other Possible methods:



##### registration-certificate method:

We can add a `--prev-cold-verification-key-file` flag to the registration certificate command, and require signatures from both cold keys:

```
cardano-cli stake-pool registration-certificate \
--cold-verification-key-file new-cold.vkey \
--prev-cold-verification-key-file old-cold.vkey \
......
<REST_OF_THE_POOL.CERT>
......

```

However, this implementation is sub-optimal because it would require a signature from the old cold key each time the new pool is updated, which is nonsensical in the context of transferring pool ownership. 


##### transfer-certificate method:

We can add a `transfer-certificate` sub-command to  the `cardano-cli stake-pool` command, and require signatures from both cold keys.

```
cardano-cli stake-pool transfer-certificate \
--current-cold-verification-key-file current-cold.vkey \
--new-cold-verification-key-file new-cold.vkey \
--epoch <EPOCH_NUMBER>
--out-file <OUT_FILE>
```


Additionally, to incentivize careful consideration before transferring pool ownership, and/or to prevent sybil-like or malicious pool transfers, there should be a significant fee for the transfer. Considering a pool transfer should be a major event in the pool's lifetime, the fee can be similar, if not exactly the same, as the poolDeposit fee (currently 500 ADA). 


##### Summary of CIP Benefits:

1. Current SPO's have no way of implementing CIP-1853 (unless they have already done so) without creating a new pool.
2. An SPO may become unwilling or unable to continue administering their pool. Instead of de-registering the pool, they may wish to sell the pool to a buyer.
3. Currently, if a pool is retired, each delegator is responsible for delegating to a new pool. This would allow the old pool's delegators to be automatically delegated to the new pool. 
4. If/when shared ownership of stake pools [Conclave](https://iohk.io/en/research/library/papers/conclavea-collective-stake-pool-protocol/) is implemented, transferring one's share of a pool will not only be useful, but necessary. 


Stake Pools are endogenous entities of the Cardano Protocol, and, much like native ADA, should be transferable.

------
# Backwards Compatibility

This CIP requires changes to the core protocol, and thus likely a HFC.

**I don't believe this necessarily creates any breaking changes in the protocol, but I may be wrong - please advise**
