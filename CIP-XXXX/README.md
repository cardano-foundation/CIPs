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

Tiered pricing works by dynamically separating available throughput to multiple tiers that are expected to serve different needs, ranging from DeFi to low-cost applications. Users are then given the choice of selecting which tier better accommodates their needs, which also determines how much they want to wait until their transaction makes it to the chain and how much they want to pay.

In more detail, the price and delay associated with each tier as well as the number and size of different tiers are determined dynamically, based on the demand observed in the ledger; the fuller the space allocated to a certain tier looks, the higher the demand. When the system is not congested, a single high speed/low price/small size tier remains available, with the system optimizing its resource use and behaving more or less as having fixed low fees and no extra delays.  On the other hand, when congestion is detected, tier parameters are selected in such a way that a multitude of price/delay options are available to users. 

Further, to accommodate users that want to publish transactions as fast as possible, e.g., as in DeFi applications, a tier whose delay is set to the minimum level is always available. Given the observed demand, tiers are introduced and modified to achieve at minimum a target ratio between consecutive prices and waiting times, ensuring that substantially different service options are offered to the users. Specifically, moving from tier i to tier i+1 both the price must be substantially lower and the waiting time higher than that of the previous tier. In addition, if the demand on the last tier increases, i.e., the price becomes high enough, additional tiers are introduced. While, if the demand of the last tier falls below a certain level, the tier gets deleted and other tiers are resized accordingly, to avoid leaving the allocated space unused. By appropriately setting the relevant parameters it can be guaranteed that a low cost service option always remains available.


## Integration with Ouroboros Leios  

Tiered pricing naturally integrates with Ouroboros Leios by randomly associating each input block (IB) with a single tier, and restricting its contents to transactions  that have selected this tier. Demand for different tiers is tracked in a commonly agreed manner, by observing the level of fulness of IBs that were recently introduced into the main chain. Consequently, tier parameters are also adjusted in a commonly agreed manner. 
Transactions in IBs are prioritized for inclusion in the main chain based on their respective tier delay; IBs are only included in an endorsment block (EB) after time proportional their tier has passed. To avoid attackers interfering with the tier selection process, the VRF output used to determine whether an SPO is eligible to create a new IB is also used to determine its tier. Given that tier parameters (price, delay, size, …) are part of the ledger state, the IB is expected to uphold the relevant parameters derived by the likely stable RB it references.

Tracking demand is necessary to properly adjust prices. We   capture changes in demand by observing how full IBs included in the main chain are. Given that malicious parties may try to artificially adjust prices by creating IBs that do not reflect the actual demand, we take advantage of the fact that IBs are created at a high rate, and thus make use of a “large” enough sample from which we can robustly deduce the actual demand for each tier. 


The price of each tier is updated in similar fashion to EIP-1559, disregarding other tier prices. 
On the other hand, delays are updated much less frequently than prices and depend on them. In particular, delays observe the average prices between each update and adjust up or down in small steps accordingly, to ensure that prices of consequent tiers are separated enough. 

In order to reduce the risk of not having enough funds to pay for a transaction targeting a specific tier due to price fluctuations, users are allowed to provide higher fees. In the end they are only going to pay the actual tier price, and get back the change as a reward at the end of the epoch. The reward mechanism should be adjusted accordingly.



# Rationale  <!-- The rationale fleshes out the specification by describing what motivated the design and why particular design decisions were made. It should describe alternate designs that were considered and related work. The rationale should provide evidence of consensus within the community and discuss important objections or concerns raised during discussion. When applicable, it must also explain how the proposal affects backward-compatibility of existing solutions. -->

Traffic diversity refers to the ability of the system to target multiple use cases at once, whenever this is possible. This is done through the use of tiers with varying delays and cannot be achieved by different prices alone. If a tier offers a specific quality of service, its price cannot be reduced to capture every user because costs can be misreported and off-chain agreements can override the prescribed transaction order. By ensuring that the delay of every tier must be waited out, each tier is only useful to certain users. 

# Path to Active

## Acceptance Criteria			

## Implementation Plan

# Copyright
