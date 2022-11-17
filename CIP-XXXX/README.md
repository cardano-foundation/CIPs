---
CIP: ????
Title: Increase Cardano service diversity by implementing Tiered Pricing
Status: Draft
Category: Fees
Authors:
    - Giorgos Panagiotakos <giorgos.panagiotakos@iohk.io>
    - Philip Lazos <philip.lazos@iohk.io>
Implementors: N/A
Discussions:
    - https://github.com/cardano-foundation/cips/pulls/1
Created: 2022-11-17
License: CC-BY-4.0
---

# Abstract <!-- A short (~200 word) description of the technical issue being addressed and the proposed solution -->



# Motivation  <!-- A clear and short explanation introducing the reason behind a proposal. When changing an established design, it must outlines issues in the design that motivates a rework. -->
		
Due to the introduction of smart contracts and the general increase in traffic in Cardano, the system is bound to face congestion issues at some point. 
Fees are currently fixed and transactions are included in blocks in a FIFO order. 
Unfortunately such an approach is ill-suited to handle congestion, as it does not provide any means for users to signify their urgency and accommodate them based on their needs. Even with the introduction of Ouroboros Leios which will substantially increase throughput, the system needs a better way of prioritizing transaction inclusion in the face of congestion.

Ideally, we would like the system to offer a multitude of options, and have users decide how much they want to pay based on their urgency. 
The system should offer options ranging from fast service with high fees to slower service with lower fees.
The current fee system cannot provide such flexibility as it does not allow users to signify their urgency, and thus changes are required.
 

# Specification <!-- The technical specification should describe the syntax and semantics of any new feature. The specification should be detailed enough to allow competing, interoperable implementations. -->

## Tiered Pricing

Tiered pricing works by dynamically separating available throughput to multiple tiers that offer different price/delay tradeoffs. Users are given the choice of selecting which tier better accommodates their needs. 

In more detail, the price and delay associated with each tier as well as the number and size of different tiers are determined dynamically, based on the demand observed in the ledger; the fuller the space allocated to a certain tier looks, the higher the demand. When the system is not congested, a single high speed/low price/small size tier remains available, with the system optimizing its resource use and behaving more or less as having fixed low fees and no extra delays.  On the other hand, when congestion is detected, tier parameters are selected in such a way that a multitude of price/delay options become available to users. 

More specifically, tiers are introduced and modified to achieve at minimum a target ratio between consecutive prices and waiting times; moving from tier i to tier i+1 both the price must be substantially lower and the waiting time higher than that of the previous tier. The first tier is always available and its delay is set to the minimum level.
Additional tiers are introduced, if the demand on the last (slowest) tier increases, i.e., its price becomes high enough. Similarly, if the demand of the last tier falls below a certain level, the tier gets deleted and other tiers are resized accordingly, to avoid leaving the allocated space unused. 

The price of each tier is updated in similar fashion to EIP-1559, disregarding other tier prices. 
On the other hand, delays are updated much less frequently than prices and depend on them. In particular, delays observe the average prices between each update and adjust up or down in small steps accordingly, to ensure that prices of consequent tiers are separated enough. Finally, tier additions and deletions happen even less frequently.

Transactions are allowed to specify higher fees than those determined by the tier selected. In the end, they are only going to pay the actual tier price, and get back the change as a reward at the end of the epoch. The reward mechanism should be adjusted accordingly.


## Integration with Ouroboros Leios  

Tiered pricing naturally integrates with Ouroboros Leios by associating each input block (IB) with a single tier type, and restricting its contents to transactions of this type. The VRF output used to determine whether an SPO is eligible to create a new IB is also used to determine its tier type. The rate at which IBs of a certain type are produced is determined by the tier's size.

Demand for different tiers is tracked by observing the level of fullness of IBs that were recently added to the main chain in a large enough interval. As specified earlier, tier parameters are adjusted based on the observed demand. IBs are expected to uphold the relevant parameters derived by the ranking block (RB) they reference. 

IBs are prioritized for inclusion in the main chain based on their respective tier delay; IBs are only included in an endorsement block (EB) after time proportional to their tier delay has passed.




# Rationale  <!-- The rationale fleshes out the specification by describing what motivated the design and why particular design decisions were made. It should describe alternate designs that were considered and related work. The rationale should provide evidence of consensus within the community and discuss important objections or concerns raised during discussion. When applicable, it must also explain how the proposal affects backward-compatibility of existing solutions. -->

The key idea of this proposal is that the fee system should be able to target multiple use cases at once, whenever this is possible. This is done through the use of tiers with varying delays and cannot be achieved by different prices alone. If a tier offers a specific quality of service, its price cannot be reduced to capture every user because costs can be misreported and off-chain agreements can override the prescribed transaction order. By ensuring that the delay of every tier must be waited out, each tier is only useful to certain users. 

## Are we departing from a low-cost system?

While this proposal departs from the low fixed fees approach, for reasons explained earlier, by appropriately setting the relevant parameters it can be guaranteed that a relatively low-fees service option will always be available. 
This option may come with a high expected delay when the system is congested. However, this is also the case in the current system. 
<!-- a numerical example may help here -->
Moreover, tiered pricing clearly improves in that it offers users a clear view of the delay expected from each tier, compared to the current system when the expected delayed can only be estimated by off-chain channels.

## Why not EIP-1559?

While our approach bares similarities with that of EIP-1559 on the way prices are updated, our design is a lot more diverse in that it allows for different types of users to be served by the system in a satisfactory manner.

<!-- add simulations here -->

## Fee overshooting 

Allowing users to offer higher funds for fee payment serves as a way of reducing the risk of price fluctuations. This comes without additional costs to users, as change comes back to them in the form of reward.

## Demand tracking
Tracking demand is necessary to properly adjust prices. Given that malicious parties may try to artificially inflate or deflate prices by creating IBs that do not reflect the actual demand, we take advantage of the fact that IBs are created at a high rate, and make use of a “large” enough sample from which we can robustly deduce the actual demand for each tier. 

## IB-Tier correspondence
Assigning a single tier type to each IB at a random and verifiable way through the VRF mechanism, is an efficient way of avoiding meddling of malicious actors in the tier selection process. It also easily allows us to regulate the expected rate at which IBs of a certain tier type are produced.

# Path to Active

## Acceptance Criteria			

## Implementation Plan

# Copyright
