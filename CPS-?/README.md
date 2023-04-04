---
CPS: ?
Title: Cardano Governance Security
Category: ?
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

Recommendation: The person discovering the vulnerability should document the circumstances and details in which the vulnerability is present and how to reproduce the vulnerability. Then report the vulnerability in a confidential manner using a secure method to the developer team with the resources to correct the vulnerability.

### #2: Emergency group to support the disaster recovery plan.
  -attacks on persons if known
  -we don’t want attackers to know who that group is?

Recommendation:

### #3: Emergency change that needs to be done quickly.
  -a nuclear option
  -change requires “just do it” 
  -a security that fix must be implemented but CANNOT be communicated publicly

Recommendation:

### #4: Operational Security (OPSEC) of the committee.
  -physical security
  -digital security

Recommendation:

### #5: Committee keys lost or stolen or committee keys sold to a bad actor.

Recommendation:

### #6: DRep keys lost or stolen or DRep keys sold to a bad actor.

Recommendation:

### #7: Lack of governance for an extended period of time.
  -Uncontrolled hard forks by SPOs
  -Risk of no confidence

Recommendation:

### #8: Lack of trust in voter tooling.

Recommendation:

### #9: Trust in the wallets.
  -wallet voting attack vector
  -hardware wallet support

Recommendation:


### #10: Corruption - in any form, any number of actors.
  -Code of Conduct mitigation
  -on-chain mitigation


Recommendation:

### #11: Collusion - the bad version of collaboration to do something illegal or undesirable.

Recommendation:

### #12: Vote buying - Ada kickbacks.

Recommendation:

### #13: IGCO - initial governance coin offering
  -offering voters a token of unknown value by a representative to acquire delegators
  -including tokens other than Ada

Recommendation:

### #14: Powerful Voter Collusion
  -demotivates smaller bag holders
  -cause a loss of participation
  -too many voters abstain
  -minority controls the outcome
  -can push through any proposal

Recommendation:

### #15: Persistence - Removal of proposals by attackers.

Recommendation:

### #16: Risk of Proposal overload - Risk of DDOS.

Recommendation:

### #17: Excessive actions.
  -Drawing too much money
  -Changing parameters that break the chain (block size=0 for example)
  -overlapping actions and duplicate actions

Recommendation:

### #18: Lack of technical understanding by DReps.
Education of correct procedures for DReps

Recommendation:

### #19: Sybil behavior - one person acting as multiple DReps.

Recommendation:

### #20: Overpower Risk - One DRep or entity with too much power.

Recommendation:

### #21: Superstar attack - one “superstar” person that everybody delegates to becomes a dictator with little skin in the game.
(Example: Elon Musk as a DRep)

### #22: High chain load impacting governance.

Recommendation:

### #23: Unknown external regulation risks - affecting a specific DRep by country or affecting governance as a whole.

Recommendation:

### #24: Blocking a Constitutional Committee revote after a vote of “no confidence”.


Recommendation:

### #25: Ensuring the legitimacy of side chains involved in governance.

Recommendation:

## Use Cases

Use cases need to be fleshed out. Need more inputs here as each use case would apply to each prolem listed above. Seems like both the CIP and CPS formats is not a good fit for this document.


## Goals

The intent of this CPS is to promote awareness of governance security vulnerabilities and possible mitigation techniques in the Cardano ecosystem. The goal is to provide a comprehensive guide describing all known governance security threats and possible mitigiations techniques, but not to address specific software vulnerabilities. The governance security need is present regardless of the final form of CIP-1694 or any other governance document to minimize malicious activities that may occur within a system of voting, holding elections, and/or on-chain approval of automated actions are present.

## Open Questions

Proposed solutions should strive to address the questions outlined within [Problem](#problem).
