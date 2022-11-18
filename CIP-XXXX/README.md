---
CIP: ????
Title: Dealing with traffic congestion by implementing Tiered Pricing
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

# Dealing with traffic congestion by implementing Tiered Pricing

## Abstract <!-- A short (~200 word) description of the technical issue being addressed and the proposed solution -->
As Cardano adoption widens the system is bound to face traffic congestion. During such a situation the system should have predictable behavior, handling gracefully the unavoidable delays users are going to experience. Tiered Pricing deals with this issue by offering users a number of service options to select from when the system is under congestion. Each possible choice consists of a price/delay trade-off, covering a wide spectrum of use-cases. The exact mechanism is described as an extension of the recently introduced [Ouroboros Leios](https://iohk.io/en/research/library/papers/ouroboros-leios-design-goals-and-concepts/) proposal.


## Motivation  <!-- A clear and short explanation introducing the reason behind a proposal. When changing an established design, it must outlines issues in the design that motivates a rework. -->

Fees in the current system are fixed and transactions are included in blocks in a FIFO order.
Unfortunately such an approach is ill-suited to handle traffic congestion, as it does not provide any means for users to signify their urgency and accommodate them based on their needs. Throughput scaling solutions, e.g., Ouroboros Leios, may only temporarily solve the problem, until peak traffic grows larger than available throughput. Traffic congestion is also a possible attack vector that malicious actors may try to exploit to increase the average delay of the system at a moderate cost. Thus, Cardano needs a better way to handle traffic congestion.

Ideally, we would like the system to offer a multitude of options, and have users decide the price/delay trafe-off that suits them. These options should change dynamically to reflect current traffic levels. We would like to have a mechanism that informs users of the current congestion status, and takes in account their preferences in prioritizing transactions.


## Specification <!-- The technical specification should describe the syntax and semantics of any new feature. The specification should be detailed enough to allow competing, interoperable implementations. -->

### Tiered Pricing
Tiered pricing works by dynamically separating available throughput into multiple tiers that offer different price/delay trade-offs. Users are given the choice of selecting which tier better accommodates their needs.

In more detail, the price and delay associated with each tier as well as the number and size of different tiers are determined dynamically based on the demand observed in the ledger; the fuller the space allocated to a certain tier looks, the higher the demand. When the system is not congested, a single high speed/low price/small size tier remains available, with the system optimizing its resource use and behaving more or less as having fixed low fees and no extra delays.  On the other hand, when congestion is detected, tier parameters are selected in such a way that a multitude of price/delay options become available to users.

More specifically, tiers are introduced and modified to achieve at minimum a target ratio between consecutive prices and delays; moving from tier `i` to tier `i+1` both the price must be substantially lower and the delay higher than that of the previous tier. The first tier is always available and its delay is set to the minimum level.
Additional tiers are introduced, if the demand on the last (slowest) tier increases, i.e., its price becomes high enough. Similarly, if the demand of the last tier falls below a certain level, the tier gets deleted and other tiers are resized accordingly, to avoid leaving the allocated space unused.

The price of each tier is updated in similar fashion to [EIP-1559](https://github.com/ethereum/EIPs/blob/master/EIPS/eip-1559.md), disregarding other tier prices.
On the other hand, delays are updated much less frequently than prices and depend on them. In particular, delays observe the average prices between each update and adjust up or down in small steps accordingly, to ensure that prices of consequent tiers are separated enough. Finally, tier additions and deletions happen even less frequently.

Transactions are allowed to specify higher fees than those determined by the tier selected. In the end, they are only going to pay the actual tier price, and get back the change as a reward at the end of the epoch. The reward mechanism should be adjusted accordingly.


### Integration with Ouroboros Leios
Tiered pricing naturally integrates with Ouroboros Leios by assigning to each input block (IB) a single tier type, and restricting its contents to only transactions of this type. The VRF output used to determine whether an SPO is eligible to create a new IB is also used to determine its tier type. The rate at which IBs of a certain type are produced is determined by the tier's size.

Demand for different tiers is tracked by observing the level of fullness of the IBs that were recently added to the main chain in a large enough interval. As specified earlier, tier parameters are adjusted based on the observed demand. IBs are expected to uphold the relevant parameters derived by the ranking block (RB) they reference, otherwise they are deemed invalid.

IBs are prioritized for inclusion in the main chain based on their respective tier delay; IBs are only allowed to be included in an endorsement block (EB), and subsequently to the main chain, after time proportional to their tier delay has passed.




## Rationale  <!-- The rationale fleshes out the specification by describing what motivated the design and why particular design decisions were made. It should describe alternate designs that were considered and related work. The rationale should provide evidence of consensus within the community and discuss important objections or concerns raised during discussion. When applicable, it must also explain how the proposal affects backward-compatibility of existing solutions. -->

The key idea of this proposal is that the fee system should be able to target multiple use cases at once, whenever this is possible. This is done through the use of tiers with varying delays and cannot be achieved by different prices alone. If a tier offers a specific quality of service, its price cannot be reduced to capture every user, because costs can be misreported and off-chain agreements can override the prescribed transaction order. By ensuring that the delay of every tier must be waited out, each tier is only useful to certain users, resulting in lower prices.


### Are we departing from a low-cost system?
While this proposal departs from the low fixed fees approach for the reasons explained earlier, by appropriately setting the relevant parameters it can be guaranteed that a relatively low-cost service option will always be available to users.
This option may come with a high expected delay when the system is congested. Note, that this is also the case in the current system. Moreover, tiered pricing improves in that it offers users a clear view of the delay expected from each tier, compared to the current system where the expected delay can only be estimated by off-chain channels.



### Why not EIP-1559?
While our approach bares similarities to that of EIP-1559 on the way prices are updated, our design is a lot more diverse in that it allows different types of use-cases to be served by the system in a satisfactory manner. We highlight this point further through simulation.

In the following figures we present the evolution of the price, delay and size of each tier of a simplified blockchain with three tiers of equal size. The demand starts low, then changes to 3 clusters with different levels of urgency, then uniform urgency and finally becomes lower than the available throughput. During the low-demand periods, only tier 1 is available and its price and delay are minimal. Moreover, the size of tier 1 periodically fluctuates, in an effort to detect increased traffic. Next, in the 3 cluster period, all 3 tiers become available as the system detects increased traffic. Note, that the delays of Tiers 2 and 3 increase to maintain the price invariant; here the price of subsequent tiers must be at least half of the previous ones. Finally, during the uniform urgency segment, the delays of Tiers 2 and 3 again adjust to maintain the price invariant, as the price of Tier 1 decreases.

In the last figure we show how the Ethereum transaction fee mechanism would have fared against the same traffic. Notice that in periods of low demand the results are similar, while during high congestion the Ethereum price is slightly lower than our Tier 1 price. However, Ethereum is priced in such a way that only transactions with the highest value can make it through. In our proposal, the increased delays of different tiers could make them unattractive for certain applications (such as DeFi), reducing their prices and allowing a more diverse set of users to participate.

![Tiered pricing - prices](https://github.com/abailly-iohk/CIPs/blob/tiered-pricing-protocol/CIP-XXXX/blob/image2.png)
![Tiered pricing - delays](https://github.com/abailly-iohk/CIPs/blob/tiered-pricing-protocol/CIP-XXXX/blob/image4.png)
![Tiered pricing - sizes](https://github.com/abailly-iohk/CIPs/blob/tiered-pricing-protocol/CIP-XXXX/blob/image1.png)
![Ethereuem - prices](https://github.com/abailly-iohk/CIPs/blob/tiered-pricing-protocol/CIP-XXXX/blob/image3.png)


### Fee overshooting
Allowing users to allocate more funds than the observed tier price for fee payment serves as a way of reducing the risk of price fluctuations. This comes without additional costs to users, as change will come back to them in the form of reward at the end of the epoch.

### Tracking demand 
Tracking demand is necessary to properly adjust prices. Given that malicious parties may try to artificially inflate or deflate prices by creating IBs that do not reflect the actual demand, we take advantage of the fact that IBs are created at a high rate, and make use of a “large” enough sample from which we can robustly deduce the actual demand for each tier.

### IB-Tier correspondence
Assigning a single tier type to each IB at a random and verifiable way through the VRF mechanism, is an efficient way of avoiding meddling of malicious actors in the tier selection process. It also easily allows us to regulate the expected rate at which IBs of a certain tier type are produced by adjusting the relevant target threshold.

## Path to Active

### Acceptance Criteria <!-- Describes what are the acceptance criteria whereby a proposal becomes 'Active' -->

* Tiered Pricing is available on Cardano mainnet

### Implementation Plan <!-- A plan to meet those criteria. Or `N/A` if not applicable. -->

While Tiered Pricing will have a deeper impact when deployed on top of Ouroboros Leios, due to the high level of throughput that can be directed to different use-cases, Cardano running Ouroboros Praos could still benefit from it during high congestion periods. A Tiered Pricing implementation should thus be as much as possible agnostic of the actual protocol run.

Should this CIP be accepted, the high-level implementation plan would be:
1. Publish a detailed pricing algorithm
   **NOTE**: This includes fees calculation and distribution
2. Prototype executable implementation suitable for running simulations and formal analysis
3. Simulate the impact of Tiered Pricing on Cardano. This simulation should be able to demonstrate how this proposal impacts the distribution of fees under various conditions of the system, possibly using historical data
4. Implement and deploy on top of Ouroboros Praos (or whatever version of consensus is current on Cardano at that time)
   **NOTE**: From this point on, the proposal will be _Active_
5. Adapt as part of Ouroboros Leios deployment

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode)
