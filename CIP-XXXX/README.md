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


Tiered pricing works by dynamically separating available throughput to multiple tiers that are expected to serve different needs, ranging from DeFi to low-cost applications. Users are then given the choice of selecting which tier better accommodates their needs, which also determines how much they want to wait and how much they want to pay.

In more detail, the price and delay associated with each tier as well as the number and size of different tiers are determined dynamically, based on the demand observed in the ledger; the fuller the space allocated to a certain tier looks, the higher the demand. When demand is generally low, a single high speed/low price/small size tier remains available, with the system behaving more or less as having fixed low fees and no extra delays.  On the other hand, when congestion is detected, tier parameters are selected in such a way that a multitude of price/delay options are available to users. 

More specifically, to accommodate users that want to publish transactions as fast as possible, there is always a tier available whose delay is set to the minimum level. Tiers are introduced and modified to achieve at minimum a target ratio between consecutive prices and waiting times. Specifically, moving from tier i to tier i+1 both the price must be substantially lower and the waiting time significantly higher than that of the previous tier, to ensure that users with different needs are targeted. In addition, if the demand on the last tier increases, i.e., the price becomes high enough, additional tiers are introduced. While, if the demand of the last tier falls below a certain level, the tier gets deleted and other tiers are resized accordingly, to avoid leaving the allocated ledger space unused.

Leios Integration
Tiered pricing naturally integrates with Leios by randomly associating each input block (IB) with a single tier, and restricting its contents to transactions of this tier type. Tier parameters are adjusted in a commonly agreed manner, by observing how full are the IBs of different tiers that make it to the main chain. Moreover, to be sure that transactions of a certain tier are delayed according to the price they have paid, each IB is delayed for the time dictated by its tier  before being eligible to be included in an EB and later on on the main chain. To avoid attackers interfering with the tier selection process, the VRF output used to determine whether an SPO is eligible to create a new IB is also used to determine its tier. Finally, given that tier parameters (price, delay, …) are part of the ledger state, the IB is expected to uphold the relevant parameters derived by the likely stable RB it references.




# Rationale  <!-- The rationale fleshes out the specification by describing what motivated the design and why particular design decisions were made. It should describe alternate designs that were considered and related work. The rationale should provide evidence of consensus within the community and discuss important objections or concerns raised during discussion. When applicable, it must also explain how the proposal affects backward-compatibility of existing solutions. -->

# Path to Active

## Acceptance Criteria			

## Implementation Plan

# Copyright
