---
CPS: 20
Title: Governance Stakeholder Incentivization  
Status: Open  
Category: Tools  
Authors:  
- Seomon (Cardano After Dark) <Seomonregister@gmail.com>  
- Martin Marinov <martin.marinov@cardano.marketing>  
- Sebastián Pereira Gutiérrez <sebpereira33@gmail.com> 

Proposed Solutions:
- 

Discussions:  
- https://github.com/cardano-foundation/CIPs/pull/997

Created: 2025-02-13  
License: CC-BY-4.0

---

## Abstract
The Cardano governance framework depends on the active participation of Delegated Representatives (DReps), the Constitutional Committee (CC), and Ada holders, alongside the already incentivized Stake Pool Operators (SPOs), to maintain a highly effective, representative and democratic governance structure. Presently, the system's heavy reliance on the altruistic behavior of governance participants, which poses a significant risk, potentially leading to a concentration of voting power among a small, select group. This situation undermines broader community participation and threatens democratic principles. The primary goal should be to establish a balanced but robust incentivization framework that encourages consistent and informed participation from a diverse range of stakeholders with different levels of governance responsibilities, commitments and impact. However, achieving this objective faces several technical obstacles and game theoretic challenges, including designing fair reward mechanisms, ensuring the sustainability of incentives, and preventing the misuse of incentivization structures. Addressing these challenges is crucial to fostering a more balanced and representative governance model for the Cardano community.

## Problem
The Cardano governance framework relies on Delegated Representatives (DReps), Constitutional Committee (CC), Stake Pool Operators (SPOs), and ADA holders to make informed decisions, exercise veto power, and select both SPOs and DReps that reflect the broader community's interests. However, the current system lacks a structured mechanism to incentivize DReps, CC members, and ADA holders delegating to DReps effectively. Without adequate rewards, DReps and CC members are primarily driven by altruism or self-interest, which is neither sustainable nor scalable in the long term. ADA holders also lack any reason to deeply connect with DReps. This reliance on voluntary participation risks a significant imbalance in governance, where only a small, motivated subset of the community holds disproportionate influence.

The absence of an incentivization framework discourages widespread participation and may lead to voter apathy, reducing the overall quality and representativeness of decisions. This problem is further exacerbated by the potential for centralization, as a few highly active stakeholders can dominate governance processes, marginalizing the voices of the broader community.

The writing of this CPS document is motivated by the urgent need to address these issues and create a comprehensive incentivization system. Such a system aims to ensure that DReps, CC members, and ADA holders are fairly compensated for their efforts, thereby promoting active, informed participation and maintaining a decentralized governance structure that truly reflects the diverse interests of the Cardano community.

Any incentives program for the above mentioned stakeholders should take into account the current SPO rewards. Rewards and incentives have to be considered along the yearly inflows of ada to the treasury. All governance stakeholders must be considered as part of a whole which is the Cardano governance model. 



## Use Cases
### **1. Dedicated DReps Struggle to Stay Engaged**
Bob is a long-time Cardano supporter who wants to actively participate in governance. He has been following governance actions and has taken the time to research and write about important proposals. His insights gain traction, and several small ADA holders delegate their stake to him, recognizing his contributions.

However, despite his dedication, Bob finds it increasingly difficult to justify the time required to analyze governance actions, engage with the community, and vote responsibly. He works a full-time job and has personal responsibilities, leaving him with little bandwidth to commit to governance. While some Stake Pool Operators (SPOs) and project owners have been able to transition into full-time roles within the ecosystem, Bob has no way of sustaining himself as a DRep. Over time, he is forced to step back and delegate his voting power to another DRep, reducing the diversity of governance representation.

A well-designed incentivization framework would allow individuals like Bob to remain engaged by compensating them for their time and effort. This would lead to a more representative governance model and prevent valuable contributors from exiting the system due to financial constraints.

### **2. Constitutional Committee members (CC members)**
The CC is the body with the smallest pool of participants and we expect this to remain the case even after it opens up to more members. As such, CC members will have a bigger workload per individual when compared to other governance bodies. 

CC members run the risk of being overwhelmed by the quantity of proposals they’ll need to consider. Compensation for CC members allows them to dedicate more time to the process and also consider it as part of their professional activities. Members of the CC should be incentivesed by their on-chain votes on all governance actions where their role plays a part. This on-chain information can be the basis to check on their activity and performace. 

### **3. Ada Holders are incentivized but not for governance involvement**
Ada holders play a crucial role in the Cardano ecosystem. While they are incentivized to stake to a DRep, there is no clear motivation for them to stay actively engaged in their DRep’s voting behavior or governance participation. This creates a disconnect between delegation and governance outcomes, weakening the representativeness of governance decisions.

Many Ada holders delegate their stake precisely because they lack the time or expertise to follow governance actions closely. However, the system still requires their periodic engagement, to assess whether their chosen DRep continues to align with their values. Without an incentive to review or reconsider their delegation, Ada holders risk passively contributing to governance stagnation, where ineffective or misaligned DReps retain power simply due to voter inertia.

For governance to be truly decentralized and representative, Ada holders must have a reason to stay informed—even at a minimal level—to ensure their delegation remains an active choice rather than a passive default.


### **4. Stakepool Operators are already incentivized**
While Stake Pool Operators play a dual role in the Cardano ecosystem now, their governance participation is not directly rewarded. 

SPOs who are also DReps face overlapping responsibilities, meaning they have the opportunity to do almost the same amount of work for double the impact in some cases. 

Since there is little additional incentive for them, to engage deeply in governance beyond their required votes this could lead to a passive voting behaviour, where SPOs vote without fully engaging in the governance discourse. Another concern is the Concentration of governance power, if large SPOs who act as DReps accumulate excessive influence over governance decisions as some already have.

### **5. Centralization of Governance Due to a Lack of Incentives and guardrails**
In the absence of financial incentives, only a small group of highly motivated individuals participate in governance. Over time, governance power becomes concentrated among a few active representatives who have the time and resources to engage, while many potential DReps remain on the sidelines.

This concentration of power increases the risk of governance capture, where a small number of stakeholders control the outcome of key decisions and their only financial incentive is voting to serve their own interests. Additionally, inactive DReps or SPOs who continue to hold delegation without participating, or voters who lost their keys but still stake to DReps contribute to governance stagnation, reducing the legitimacy of voting outcomes.

A structured incentive system would mitigate these risks by encouraging broader participation and preventing governance power from consolidating among a select few. Implementing periodic delegation resets for inactive DReps would further ensure that voting power remains in the hands of engaged representatives.

### **6. Uninformed Voting Reduces Governance Effectiveness**
DReps & SPOs are expected to vote in the best interest of the Cardano community, but without the right incentives, there is little motivation to conduct thorough research on governance actions. Some DReps/SPOs may vote based on limited information, personal biases, the current SPO incentives or simply follow the decisions of other prominent representatives without critical evaluation.

This lack of diligence increases the likelihood of errors in leadership and policy, including the approval of poorly structured proposals or the rejection of initiatives that would benefit the ecosystem. Without a mechanism to reward informed voting, governance risks becoming a process of rubber-stamping rather than a meaningful evaluation of proposals.

By introducing performance-based rewards that factor in voting participation, rationalization, and retrospective scoring of governance actions, the system can encourage DReps to engage more thoughtfully in decision-making. This would improve the overall quality of governance and ensure that voting outcomes align with the long-term interests of the Cardano ecosystem.

## Goals
### **Primary Objective**
Establish a structured and sustainable incentivization framework that motivates and rewards governance stakeholders to participate actively and make well-informed governance decisions, therefore upholding democratic, sustainable, ethical as well as decentralized principles of the Cardano ecosystem.

### **Key Goals**
#### Compensate stakeholders for their meaningful work
Governance stakeholders invest significant time and effort into understanding, evaluating, and voting on governance actions. Without financial incentives, this responsibility falls predominantly on individuals who either have the financial freedom to participate voluntarily, are driven purely by altruism or have self-serving motives. A fair and transparent reward mechanism will enable DReps to commit to governance activities without financial strain, ensuring the role remains accessible to all willing participants and serves the greater ecosystem.

#### Increase stakeholder participation
The current system lacks sufficient incentives, leading to a low engagement rate among potential governance participants. This results in a concentration of power among a small number of highly active participants, which increases the risk of centralization and reduces diversity in governance decision-making. By implementing a rewards system, more individuals will be encouraged to participate, leading to a more decentralized and representative governance model. Inclusivity should be considered as a democratic core value to increase stakeholder buy-in and participation.

#### Improve the quality of stakeholder actions
The effectiveness of governance decisions depends on the depth of understanding and thoroughness of analysis conducted by governance stakeholders. A well-designed incentivization mechanism will encourage stakeholders to dedicate time to research governance proposals, critically evaluate their impact, and act in a manner that aligns with the broader interests of the Cardano community. Furthermore, implementing performance-based rewards, such as factoring in participation rates and the quality of voting rationales as well as scoring of governance actions in retrospect will discourage uninformed voting and promote responsible decision-making.

#### Ensure fair and transparent reward distribution
The incentivization model must be structured to fairly distribute rewards based on clear and measurable parameters. Rewards should not be arbitrary or biased toward wealthier or more influential participants but should instead reflect the quality and impact of a DRep’s contributions. The framework must be transparent, allowing the Cardano Community to understand how rewards are calculated and distributed.

#### Encourage long-term engagement and stability
Governance in Cardano is an evolving process that requires consistency and long-term commitment. An effective incentivization structure should not only attract new participants but also encourage existing DReps to remain engaged over extended periods. This will ensure continuity in governance practices, minimize abrupt power shifts, and provide a stable decision-making environment for the ecosystem.

#### Prevent gaming and misuse of incentives
Any reward system carries the risk of exploitation, where participants attempt to maximize rewards through minimal effort, collusion, or other manipulative tactics. The incentive framework must be robust and include safeguards against such behaviors, such as requiring active participation, considering qualitative assessments of governance contributions, and periodically reviewing and adjusting parameters to close potential loopholes.

#### Promote global and cultural diversification
Cardano is a global ecosystem, and its governance should reflect the diverse perspectives and experiences of its community members. A key goal is to encourage participation from a wide range of geographic regions, cultural backgrounds, and socioeconomic contexts. Achieving this will help governance decisions better align with the needs and values of the global Cardano community, rather than being dominated by any single region or demographic.

#### Maximize governance effectiveness
Traditional governance mechanisms often suffer from inefficiencies, slow decision-making, and resource-heavy processes that do not scale well. The incentivization framework for DReps must be designed to optimize governance effectiveness while minimizing unnecessary complexity and resource consumption.


## **Open Questions**
- Is change needed at the Ledger/protocol level or tooling/wallet level?
- What are the current incentives for stakeholders?
- Is the current architecture avoiding or aiding centralization?
- What’s the proper reward amount?
- How much should the rewards be based on ADA delegation, the DRep’s participation or other factors?
- What’s the impact of stakeholder rewards on Cardano’s treasury?

## **References**
- [Reward Schemes and Committee Sizes in Proof of Stake Governance](https://arxiv.org/abs/2406.10525)
- [Should DReps receive compensation? Poll]()
## Copyright
This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
