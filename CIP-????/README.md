---
CIP: ???
Title: Cardano Governance Security
Category: Ledger
Status: Proposed
Authors:
    - Richard McCracken <rickymac68@icloud.com>
    - Andrew Westberg <andrewwestberg@gmail.com>
Implementors: []
Discussions:
    - https://github.com/cardano-foundation/CIPs/pull/490
Created: 2023-03-27
License: CC-BY-4.0
---


# Abstract

As Cardano community led governance comes online, security of the governance mechanism must be addressed in a manner so that all participants are aware of the security weaknesses and how each weakness can be addressed. The guidelines contained in the CIP are relevant to Constittional Committe members, Delegation Representatives, Stake Pool Operators, voters, and Ada holders at large. The guidelines also contain as to how wallet developers, dApp developers, and infrastructure developers in general to help build situational awareness so that as development progresses in these areas, consideration in design is given to governance security.

# Motivation

This CIP intent is to promote awareness of governance security vulnerabilities and possible mitigation techniques in the Cardano ecosystem. The goal is to provide a comprehensive guide describing all known governance security threats and possible mitigiations techniques, but not to address specific software vulnerabilities. The governance security need is present regardless of the final form of CIP-1694 or any other governance document to minimize financial damage and nefarious activities that may occur when a system of voting, elections, and on-chain approval of automated actions are present.

# Specification

Governance on Cardano in this CIP is defined as on chain decision making that is automatically executed when some threshold of approval by human actors is met. Each threat or vulnerability will be described as a "threat", "description", and the suggested mitigiation technique will be described as a "recommendation" for each type of threat identified in this document. All known threats and mitigations will be made available to public as broadly as possible. The more voters, developers, and governance actors are aware of threats the more likely they are to be identified and mitigated before damage occurs.

On rare occation a threat may be identified that requires responsible reporting procedures in order to prevent exposing an active vulnerability to bad actors who may aim to exploit the vulnerability. In the event responsible reporting is required, notify the appropriate group or entity with the responsiblility and resources to mitigate such threat in a confidential manner.

Assumption: There are no known software back doors. Unknown software vulnerabilities may be discovered.

### #1: Unknown software vulnerability affecting governance is discovered.

Recommendation: The person discovering the vulnerability should document the circumstances and details in which the vulnerability is present and how to reproduce the vulnerability. Then report the vulnerability in a conficential manner using a secure method to the developer team with the resources to correct the vulnerability.

### #2: Emergency group to support the disaster recover plan.
  -attacks on persons if known
  -we don’t want attackers know who that group is?

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
  -on chain mitigation

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

### #24: Blocking a Constitution Committee revote after a vote of “no confidence”.

Recommendation:

### #25: Ensuring the legitimacy of side chains involved in governance.

Recommendation:



# Rational

The threats and recommendations listed here are the result of consultation among cyber security experts, financial experts, game theory experts, and Voltaire workshop attendees which included developoers, stake pool operators, representatives from IOG, Cardano Foundation and Emurgo, memebers of Project Catalyst, and Cardano community members at large.

# Path to active

This CIP will be ready for active when concurrence is established by the Cardano communities of practice for each threat and recommenation listed in this CIP.

# Copyright

This CIP is licensed under CC-BY-4.0
