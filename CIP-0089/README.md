---
CIP: 89
Title: Distributed DApps & Beacon Tokens
Category: Tools
Status: Active
Authors:
    - fallen-icarus <modern.daidalos@gmail.com>
    - zhekson1 <zhekson@nomadpool.io>
Implementors: []
Discussions: []
Created: 2023-02-21
License: CC-BY-4.0
---

## Abstract

This CIP describes a general design pattern for creating DApps where all users are given their own
personal DApp addresses. These DApps are called distributed-DApps (dDApps) because assets are
distributed across all of the user addresses. By giving everyone their own DApp address, users are
able to maintain custody *and* delegation control of their assets at all times. In other words, this
CIP describes how to design DeFi so that it does *not* centralize Proof-of-Stake blockchains like
Cardano. And by using beacon tokens, users are able to interact fully peer-to-peer - no third-party
indexing system is required. As a result, dDApps are essentially just extensions to a cardano node.

## Motivation: why is this CIP necessary?

To date, there are very few DeFi Dapps in which users maintain full delegation control of their
assets. In fact, sacrificing delegation control is so common in the blockchain space that many
Proof-of-Work proponents argue that DeFi will ultimately kill Proof-of-Stake blockchains. But this
actually isn't the fault of DeFi; **it's entirely the fault of how DeFi DApps are designed**.

The problem is that DApps are consistently designed as *concentrated-DApps*. Concentrated-DApps have
all users share a smart contract address; any assets than must be locked up for the DApp, are locked
up inside this shared smart contract address. But Cardano's delegation is by address, so sharing a
smart contract address fundamentally requires users to sacrifice delegation control of any assets
they lock up. In order for DeFi to not destroy Cardano's Proof-of-Stake and its on-chain government,
users **must** get their own addresses for DeFi DApps. 

Some DeFi DApps have already switched to giving everyone their own DApp addresses, but then the
indexing piece is still an issue. At a high-level, the problem is: *if users are spread out across
many different addresses, how do they find each other?* So far, most DApps that have tried the
distributed approach have relied on a third-party for this (e.g., centralized indexers or a
data-availability layer).

This CIP describes a general design to distributed-DApps **that does not required a third-party
indexing system.** Users can find and interact with each other *directly*. No middlemen/middlebots
are required. The only thing users need is the current UTxO set which all nodes should already have.
And this design is generalizable enough to be used for all kinds of DeFi Dapps: DEXs, p2p lending,
options trading, etc.

## Specification

> [!IMPORTANT]
> All dDApps are essentially standards - all users of the DApp must use the same smart contracts
> despite getting their own DApp addresses.

### Personal DApp Addresses

All Cardano addresses have two parts:

1. A payment credential
2. An optional staking credential

For dDApps, the payment credential is the DeFi DApp's spending smart contract. But the staking
credential is the user's staking credential. The staking credential can be anything: a pubkey,
native script, or a plutus script.

The spending smart contract *must delegate owner-related spending authorization to the DApp address'
staking credential*. So if Alice wants to close her limit orders that are locked at her personal DEX
address, the staking credential she used for the DEX address must approve the transaction:

- Pubkeys must sign the transaction.
- Scripts must be successfully executed in the transaction (the withdraw 0 trick can be used for
this).

### Peer-to-Peer Discoverability

Finding each other can be done using *Beacon Tokens*.

The main idea is that the current UTxO set can be easily filtered for UTxOs that contain a specific
native asset. All Cardano database/API services support this ability. Beacon tokens are native
assets whose main purpose it to tag UTxOs. 

> [!NOTE]
> The concept is the same as categorizing CIPs so that they can be filtered later. In essence, the
> UTxO set is used as a public message board and beacon tokens allow users to easily find the
> messages relevant to them.

At a high-level, when Alice creates a limit order, she will store a beacon token *with* the limit
order. It is the DApp's responsibility to ensure that beacon tokens are only ever found with
**valid** DApp UTxOs. For example, the DApp should not allow Alice to store a beacon token with an
invalid limit order (e.g., it must have a price).

Beacon tokens **should never be circulating**. They should only ever be found inside valid DApp
UTxOs. This means beacons must be minted whenever DApp UTxOs are created, and burned whenever they
are spent. It is fine if the net change is zero, like when updating a limit order's price, but the
dDApp must still ensure beacon tokens are properly stored.

At a low-level, this requires the DApp's spending smart contract to work together with a set of
minting policies. Some dDApps may only require one minting policy while others may require several.
Generally, the pattern is to pass the spending script's hash into the minting policies as an extra
parameter. The minting policies must ensure that new beacon tokens are only stored with valid DApp
UTxOs. Valid DApp UTxOs are:

- Properly configured for the DApp. The minting policy ID should be included in the DApp UTxOs' datums.
- Only ever created at addresses using the DApp's spending script and a valid staking credential.
**Creating DApp UTxOs at a DApp address without a staking credential should not be allowed.**

The first bullet will depend on the DeFi DApp. For example, a valid limit order should have a
positive price and have the asset in question. But all DApps should include the required minting
policy IDs so that the spending script can ensure beacons are burned whenever DApp UTxOs are spent.

The second bullet is required so that all DApp UTxOs discovered with the beacon tokens are
guaranteed to be governed by the same spending conditions. In other words, users know exactly what
behavior to expect.

DApp UTxOs must go to addresses with staking credentials because, if there is no staking credential,
there is technically no address owner. There is no one to contol assets locked at this address.
Therefore, there is never a reason for users to store assets in this address.

> [!TIP]
> In order to secure DApp UTxO updates where beacons can be re-used (e.g., updating a limit order's
> price), the minting policies can be executed as staking/observer scripts.

### Sharing Reference Scripts

Since all users use the same spending smart contract and minting policies, they can all use the same
reference script UTxOs. **These reference scripts must always be available.** To make them
permanently available, they should be deliberately locked forever inside the DApp address *without*
a staking credential. The reference script UTxOs can be deliberately stored with an invalid datum to
permanently lock them.

Doing this allows frontends to hard-code the reference script UTxOs and prevents any possible
service disruptions due to the reference script UTxOs being spent. By storing it inside the DApp
address without a staking credential, the dDApp standard is effectively "batteries-included".

### Upgrades

Distributed-DApp upgrades occur like with cardano-node:
  
    Users must decide when and if to upgrade their DApp addresses.
    No DAO or multisig is needed.

For example, if Alice has v1 limit orders, she must personally decide to close these limit orders
and create equivalent v2 limit orders. No one can force her to upgrade if she doesn't want to.

> [!IMPORTANT]
> dDApps should take care to ensure backwards compatibility. For example, it should still be
> possible to construct the full order book even if some users are using v1 while others are now
> using v2.

## Rationale: how does this CIP achieve its goals?

By giving all users their own personal DApp addresses, DeFi no longer undermines Cardano's
Ouroboros. And by using beacon tokens to enable easy filtering of the current UTxO set, users can
find and interact with each other fully peer-to-peer. There is absolutely no need for a third-party
indexing system to facilitate interactions.

> [!IMPORTANT]
> In order for the dDApp to work properly, all users must agree on which beacon tokens to use.
> Otherwise, filtering the UTxO set will be very complicated. This is why dDApps are effectively
> standards.

### Censorship Resistant

dDApps, as described in this CIP, use on-chain intents meaning limit orders are directly posted
on-chain. Because of this, on-chain intents are as censorship resistant as the Cardano's base layer.
However, this censorship resistance only applies when it comes to processing intents.

Another possible avenue for censorship is when trying to find the current on-chain intents.
Third-party indexing systems make it possible to censor users by *hiding intents*. For example, the
indexing system can refuse to tell Alice about particular limit orders. By using beacon tokens
instead, no one can stop Alice from finding out about all current on-chain intents.

**dDApps are maximally censorship resistant.**

### Easy Address Recovery

While only knowing the user's staking credential, the user's DApp address can easily be discovered.
This means there is no extra burden on users and wallets. The user's seed phrase is enough to
recover all of their assets in the dDApp.

### Extensions to a Cardano Node

Since dDApps only require filtering the current UTxO set, dDApps are essentially **extensions to a
cardano node**. They do not require any DApp connector. Instead, they are meant to be built directly
into frontends similar to how WiFi support is built into all devices.

> [!IMPORTANT]
> Even light nodes should be able to integrate them.

### Zero Operating Costs

Filtering the current UTxO set can be done client side by nodes. For example,
[kupo](https://github.com/CardanoSolutions/kupo) is a light-weight version of db-sync that can use
native assets to decide what information to add to a local database. This means wallets can support
features like *Trading Pair Watchlists* where users can keep track of the current order book for
their favorite trading pairs. **This is possible without relying on any third-parties.**

Because of how easy it is to filter the UTxO set, there are no operating expenses for dDApps.

### Naturally DDos Resistant

Since all DApp UTxOs must be stored with beacon tokens which are native assets, the Cardano
blockchain requires each UTxO to be stored with a minimum amount of ADA. This minimum amount of ADA
helps prevent creating valid dust DApp UTxOs that would make local filtering of the UTxO set hard.

> [!IMPORTANT]
> The beacon tokens themselves prevent creating *invalid* DApp UTxOs. The minimum UTxO value
> requirement helps prevent creating absurd amounts of *valid* DApp UTxOs.

### Other CIPs for Discoverability

The main difference between beacon tokens and CIPs like
[CIP-68](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0068/README.md) is the
scenarios they were designed to operate in. There are effectively two scenarios:

    Scenario 1: only a single entity can mint a tag for a given use case.
    Scenario 2: anyone can mint a tag for a given use case.

This simple difference results in completely different game theories for each scenario. CIP-68 was
designed for scenario 1 where the business owner (or owners) are the only ones that can mint the
reference NFT. Since the business itself depends on the reference NFT being properly used, proper
usage is naturally incentivized.

For scenario 2, there is no natural incentive for proper usage of the tag. Consider Cardano-Swaps, a
distributed DEX that would be competing with several other DEXs. The value of any activity that
occurs through Cardano-Swaps does not go to the other DEX entities. Therefore, the other DEXs have
an incentive to destroy Cardano-Swaps in a kind of goldfinger attack. Since anyone can mint a tag,
the easiest way to destroy Cardano-Swaps would be to denial-of-service attack it by creating a lot
of mis-tagged UTxOs. Then, when users try to interact with each other, there would be too much noise
in the filtering results to find each other.

CIP-68 does not defend against this kind of attack; it doesn't need to since it operates in
scenario 1. Distributed-DApps operate in scenario 2 and therefore need more assurances than what
CIP-68 can offer.

## Path to Active

This CIP is already active.

- [Cardano-Swaps](https://github.com/fallen-icarus/cardano-swaps) is a distributed order book DEX.
- [Cardano-Loans](https://github.com/fallen-icarus/cardano-loans) is a distributed credit market.
- [Cardano-Options](https://github.com/fallen-icarus/cardano-loans) is a distributed options trading
protocol.
- [Cardano-Aftermarket](https://github.com/fallen-icarus/cardano-loans) is a distributed secondary
market for financial assets.

Finally, the above four protocols were built into a prototype desktop light wallet called
[p2p-wallet](https://github.com/fallen-icarus/p2p-wallet) which showcase how easy it is to integrate
dDApps directly into wallets *without* using a DApp connector.

## Copyright
[CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode)
