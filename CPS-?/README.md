---
CPS: ?
Title: Cardano Governance Security
Category: Ledger
Status: Open
Authors:
    - Richard McCracken <rickymac68@icloud.com>
    - Andrew Westberg <andrewwestberg@gmail.com>
Proposed Solutions: N/A
Discussions:
    - https://github.com/cardano-foundation/CIPs/pull/490
    - https://github.com/cardano-foundation/CIPs/pull/491
Created: 2023-03-28
---


## Abstract

As Cardano's community-led governance system goes live, it's crucial to address the security of the governance mechanism in a way that informs all participants of potential weaknesses and how to mitigate them. The guidelines provided in the CIP are relevant to various groups, including Constitutional Committee members, Delegation Representatives, Stake Pool Operators, voters, and all Ada holders. Moreover, the guidelines are applicable to wallet, dApp, and infrastructure developers to help them build situational awareness and design governance security considerations into their development processes.

These recommendations are the result of a collaborative effort among cybersecurity, financial, and game theory experts, as well as participants of the Voltaire workshop, including developers, stake pool operators, representatives from IOG, Cardano Foundation, and Emurgo, members of Project Catalyst, and members of the Cardano community.


## Problem

The Cardano community's on-chain governance mechanism, Voltaire, is susceptible to various types of attacks that may compromise its security. This system defines on-chain decision-making that is automatically executed when a certain threshold of approval by human actors is met. To ensure maximum awareness of potential threats and vulnerabilities, this document will enumerate and describe each threat or vulnerability, including recommended mitigation techniques. It is crucial that all stakeholders, including voters, developers, and governance actors, are informed of these risks to identify and prevent any damage or, in the case of a threat event, facilitate recovery.

In rare instances, a threat may be identified that requires responsible reporting procedures to prevent exposing an active vulnerability to bad actors seeking to exploit it. In such cases, it is essential to notify the appropriate group or entity with the ressources, or are responsible for mitigating the threat in a confidential manner.

### #1: Unknown software vulnerability affecting governance is discovered.

An assumption is that are no known software back doors. Unknown software vulnerabilities may be discovered.

**Recommendation:Pre-planned Response** The person discovering the vulnerability should take the following steps:
* Document the vulnerability: The first step is to document the vulnerability as accurately as possible. This documentation should include a detailed description of the vulnerability, steps to reproduce it, and any other relevant information.
* Notify the relevant parties: The next step is to notify the appropriate parties, including the developers of the software, the blockchain community, and any relevant authorities. It's important to provide as much information as possible, so that the parties involved can understand the scope of the vulnerability and take the necessary steps to address it.
* Keep the vulnerability confidential: It's important to keep the vulnerability confidential until a fix has been implemented. This will prevent hackers from exploiting the vulnerability before it's patched.

### #2: Emergency change that needs to be done quickly.
* A nuclear option where the change requires “just do it” 
* A security fix that must be implemented but the nature cannot be communicated publicly.
* The emergency change may, or may not, require a vote on a hard fork or parameter change.
* This section may be in respose to section #1 above, or for other emergencies bug fixes.
* The emergency change may have to be coordinated by IOG for the Haskell based Cardano nodes, or the primary software provider of any other Cardano node implementations.

**Recommendation: Pre-planned Response 2.A and 2.B**

#### 2.A: For an Emergency change only requiring the SPOs, yet affects governance or voting:
1. IOG provide the Stake Pool Operators with clear and concise instructions for implementing the software change. Emphasize that while the change is not mandatory, but must be implemented without delay. Explain: What is the impact? Communicate the urgency of the change to the SPOs, without providing specific details about the threat or catastrophic failure. The operators should be aware of the importance of the change, but not necessarily the reasons behind it.

2. SMEs provide technical support to the SPOs as needed as they implement the change, if there are any hardware requirements, configuration file requirements, etc... Most SPOs are proficient but be careful to provide necessary details during emergency changes. Optimally software is tested on test nets first but a need may arise where use of the test net is not an option.

3. Monitor the network closely after the change has been implemented, to ensure that it is functioning correctly and that there are no unforeseen issues or problems. Once the change has been successfully implemented across a high % of Cardano nodes and the network is stable, consider whether it is appropriate to provide more information about the reasons for the change. If not, continue to emphasize the importance of keeping the details confidential in order to protect the security and stability of the network.

#### 2.B: For an Emergency change requiring on chain approval Governance Action:
* May require a hard fork or parameter change, or both.
* May require DReps, CC, and SPO coordination.
* May require trusted coordinators from the Cardano Foundation (CF) or IOG.

1. (CF/IOG?) Assemble a team of technical experts to develop and submit the on-chain governance action proposal. This team should include software engineers, network administrators, and other relevant experts who can ensure that the proposal is technically correct and addresses the identified issue.

2. Communicate the governance action proposal to the SPOs, DReps, and CC. Emphasize the importance of maintaining discretion regarding the issue and the need for a prompt vote to approve the proposal. This may take some extensive debate and convincing. Trust may be a factor.

3. SMEs should communicate the urgency of the change to the SPOs, DReps and CC without providing specific details about the threat or catastrophic failure if discretion is required. SMEs may have to communicate the impact if the proposal is not approved.

4. Offer technical support to the voters as needed, as an emergency response may cause people to rush and make mistakes.

9. IOG, CF, SPOs, and dApp creators will have to monitor the network closely after the governance action has been approved and activated, to ensure that it is functioning correctly and that there are no unforeseen issues.

### #3: Emergency Group required to support the Disaster Recovery Plan.
* An Emergency Group may be needed in the event of disaster recovery of the network, or an emergency change must be implented as described in section #3 below. This scenario for an Emergency Group may occur under various unknown conditions. The current disaster recovery scenarios involve "Long Lived Network Wide Partitions" and a scenario involving "Long Lived Global Outage" both referenced at this link https://iohk.io/en/research/library/papers/cardano-disaster-recovery-plan/

* Both disaster scenarios are currently and primarily handled by the stake pool operators, and do not yet require governance individual's private keys to get the Cardano network back to normal operation. 

* In the event that governance individuals and their keys are required to recover the network, a threat exists where attacks on the persons if known and their keys would prevent recovery on the Cardano network. This section offers recomendations to pretect these key critical persons, their governance keys, and the concept that we don’t want attackers to know who the main coordinators are in Disaster Recovery Plan. 

**Recommendation: Pre-planned Response**

Notify the current Constituional Commitee of the person in charge of the Emergeny Group responsible for the disaster recovery so that they know any governance actions submitted by the group are valid, or that some level of trust is established. To minimize the risk of physical and cyber threats, The Emergency Group needs to protect their private keys and identities, and ensure that the Cardano network can be recovered in the event of a disaster. Notify Delegator Representatives as needed in the event that they and their keys are required to recover the Cardano network:

1. (CF?) Identify and select a group of trusted individuals who will be responsible for disaster recovery. These individuals should be chosen based on their experience, skills, and trustworthiness.

2. Ensure that each individual in the group understands the importance of their role in disaster recovery and the need to keep their involvement confidential.

3. Provide training as needed to the Emergency Group on security best practices, including physical security, cybersecurity, and operational security. This training should include:

- Keeping their private keys secure: This includes storing them in secure locations, such as a safe or a safety deposit box, and using strong passwords or passphrase to protect them.
- Limiting access to their keys: Only authorized individuals should have access to their keys, and the keys should be stored in a way that prevents key compromise.
- Using secure communication channels: All communication should be encrypted and transmitted over secure channels to prevent interception and eavesdropping.
- Operational security: The group should be aware of their surroundings and take steps to minimize the risk of physical threats, such as surveillance or theft.

4. Develop a contingency plan for the group in the event of a security breach. This plan should include steps to revoke compromised keys, notify other members of the group of the breach, and initiate recovery procedures. Experts may need to provide guidance to Delegator Representatives. 

5. Implement measures to protect the group's identities, such as using pseudonyms or code names when communicating with each other. Consider the Constitutional Committee or Delegator Representatives may need confirmation from the Emergency Group for actions taken.

6. Limit the number of people who know the identities of the Emergency Group members to minimize the risk of information leaks. The identity of the group members should only be disclosed on a need-to-know basis.

7. When Stake Pool Operators are requred to take action, have trusted experts communicate with them via the normal Stake Pool Operator channels so they know they are getting information from the correct source. Switch to less public channels if the normal channels are suspected of being compromised.

8. Regularly review and update the security measures in place to ensure that they remain effective. Possibly do a periodic practice disaster recovery drill on one of the test networks.

### #4: Operational Security (OPSEC) of the committee.
  * Physical security
  * Digital security

**Recommendation:**

### #5: Committee keys lost or stolen or committee keys sold to a bad actor.

**Recommendation:**

### #6: DRep keys lost or stolen or DRep keys sold to a bad actor.

**Recommendation:**

### #7: Lack of governance for an extended period of time.
  * Uncontrolled hard forks by SPOs
  * Risk of no confidence

**Recommendation:**

### #8: Lack of trust in voter tooling.

**Recommendation:**

### #9: Trust in the wallets.
  * wallet voting attack vector
  * hardware wallet support

**Recommendation:**


### #10: Corruption - in any form, any number of actors.
  * Code of Conduct mitigation
  * on-chain mitigation


**Recommendation:**

### #11: Collusion - the bad version of collaboration to do something illegal or undesirable.

**Recommendation:**

### #12: Vote buying - Ada kickbacks.

**Recommendation:**

### #13: IGCO - initial governance coin offering
  * offering voters a token of unknown value by a representative to acquire delegators
  * including tokens other than Ada

**Recommendation:**

### #14: Powerful Voter Collusion
  * demotivates smaller bag holders
  * cause a loss of participation
  * too many voters abstain
  * minority controls the outcome
  * can push through any proposal

**Recommendation:**

### #15: Persistence - Removal of proposals by attackers.

Recommendation:

### #16: Risk of Proposal overload - Risk of DDOS.

**Recommendation:**

### #17: Excessive actions.
  * Drawing too much money
  * Changing parameters that break the chain (block size=0 for example)
  * overlapping actions and duplicate actions

**Recommendation:**

### #18: Lack of technical understanding by DReps.
Education of correct procedures for DReps

**Recommendation:**

### #19: Sybil behavior - one person acting as multiple DReps.

**Recommendation:**

### #20: Overpower Risk - One DRep or entity with too much power.

**Recommendation:**

### #21: Superstar attack - one “superstar” person that everybody delegates to becomes a dictator with little skin in the game.
(Example: Elon Musk as a DRep)

### #22: High chain load impacting governance.

**Recommendation:**

### #23: Unknown external regulation risks - affecting a specific DRep by country or affecting governance as a whole.

**Recommendation:**

### #24: Blocking a Constitutional Committee revote after a vote of “no confidence”.


**Recommendation:**

### #25: Ensuring the legitimacy of side chains involved in governance.

**Recommendation:**

### #26: Governance capture by a Layer 2.
* Could be enough Ada dedicated to a Hydra head, how does that Ada weight get accounted for in L1 governance?
* This may or may not be an issue for Cardano L2 or Hydra heads. Needs more analysis from experts.

**Recommendation:**


## Use Cases

Use cases need to be fleshed out. Need more inputs here as each use case would apply to each prolem listed above. Seems like both the CIP and CPS formats is not a good fit for this document.


## Goals

The intent of this CPS is to promote awareness of governance security vulnerabilities and possible mitigation techniques in the Cardano ecosystem. The goal is to provide a comprehensive guide describing all known governance security threats and possible mitigiations techniques, but not to address specific software vulnerabilities. The governance security need is present regardless of the final form of CIP-1694 or any other governance document to minimize malicious activities that may occur within a system of voting, holding elections, and/or on-chain approval of automated actions are present.

## Open Questions

Proposed solutions should strive to address the questions outlined within [Problem](#problem).
