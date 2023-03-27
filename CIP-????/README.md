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

As Cardano community led governance comes online, security of the governance mechanisme must be addressed in a manner so that all participants are aware of the security weaknesses and how each weakness can be addressed. The guidelines contained in the CIP are relevant to Constittional Committe members, Delegation Representatives, Stake Pool Operators, voters, and Ada holders at large. The guidlines also contain as to how wallet developers, dApp developers, and infrastructure developers in general to help build situational awareness so that as development progresses in these areas, consideration in design is given to governance security.

# Motivation

This CIP intent is to promote awareness of governance security vulnerabilities and possible mitigation techniques in the Cardano ecosystem. The goal is to provide a comprehensive guide describing all known governance security threats and possible mitigiations techniques, but not to address specific software vulnerabilities. The governance security need is present regardless of the final form of CIP-1694 or any other governance document to minimize financial damage and nefarious activities that may occur when a system of voting, elections, and on-chain approval of automated actions are present.

# Specification

Governance on Cardano in this CIP is defined as on chain decision making that is automatically executed when some threshold of approval by human actors is met. Each threat or vulnerability will be described as a "threat", "description", and the suggested mitigiation technique will be described as a "recommendation" for each type of threat identified in this document. All known threats and mitigations will be made available to public as broadly as possible. The more voters, developers, and governance actors are aware of threats the more likely they are to be identified and mitigated before damage occurs.

On rare occation a threat may be identified that requires responsible reporting procedures in order to prevent exposing an active vulnerability to bad actors who may aim to exploit the vulnerability. In the event responsible reporting is required, notify the appropriate group or entity with the responsiblility and resources to mitigate such threat in a confidential manner.

Assumption: there are no known software back doors.

# Rational

The threats and recommendations listed here are the result of consultation among cyber security experts, financial experts, game theory experts, and Voltaire workshop attendees which included developoers, stake pool operators, representatives from IOG, Cardano Foundation and Emurgo, memebers of Project Catalyst, and Cardano community members at large.

# Path to active

This CIP will be ready for active when concurrence is established by the Cardano communities of practice for each threat and recommenation listed in this CIP.

# Copyright

This CIP is licensed under CC-BY-4.0
