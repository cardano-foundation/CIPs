---
CIP: ???
Title: Social Governance - Treasury Budget Process
Category: Governance
Status: Proposed
Authors:
  - Binh Mai <mai.thanh.binh@gmail.com>
Implementors: N/A
Discussions:
  - https://github.com/Crypto2099/CIPs/tree/social-governance-cps/CPS-XXXX
  - https://github.com/cardano-foundation/CIPs/pull/936
  -   
Created: 2024-11-09
License: CC-BY-4.0
---

## Abstract

The current Cardano (Draft) Constitution specifies a rough budget proposal and
approval process with a handful of very loose guardrails dictating when, where,
and how withdrawals from the Cardano Treasury should occur. The detailed guardrails
are being proposed and discussed by Adam Dean in this CIP
https://github.com/Crypto2099/CIPs/tree/social-governance-budget-guardrails/CIP-XXXX 
The budget process and methodology, should also be more formally defined to 
provide clarity for budget proposers and the Cardano community.

## Motivation: why is this CIP necessary?

The Draft Cardano Constitution currently states:

> The Cardano community is expected to propose, not less than on an annual
> basis, a budget for the ongoing maintenance and future development of the
> Cardano Blockchain. All owners of ada are expected to periodically approve the
> Cardano Blockchain budget through an on-chain governance action. No
> withdrawals from the Cardano Blockchain treasury shall be permitted unless a
> budget for the Cardano Blockchain is then in effect as required by the Cardano
> Blockchain Guardrails. Cardano Blockchain budgets shall specify a process for
> overseeing use of funds from Cardano Blockchain treasury withdrawals including
> designating one or more administrators who shall be responsible for such
> oversight.
>
> — Cardano (Draft) Constitution, Article III, Section 8

> ### GUARDRAILS AND GUIDELINES ON TREASURY WITHDRAWAL ACTIONS
>
> **Treasury withdrawal** actions specify the destination and amount of a number
> of withdrawals from the Cardano treasury.
>
> #### Guardrails
>
> TREASURY-01 (x) DReps **must** define a net change limit for the Cardano
> Treasury's balance per period of time.
>
> TREASURY-02 (x) The budget for the Cardano Treasury **must not** exceed the
> net change limit for the Cardano Treasury's balance per period of time.
>
> TREASURY-03 (x) The budget for the Cardano Treasury **must** be denominated in
> ada.
>
> TREASURY-04 (x) Treasury withdrawals **must not** be ratified until there is a
> community approved Cardano budget then in effect pursuant to a previous
> on-chain governance action agreed by the DReps with a threshold of greater
> than 50% of the active voting stake.
>
> — Cardano (Draft) Constitution, Appendix I: Cardano Blockchain Guardrails),
> Section 3

More detailed guardrails are being proposed and discussed here, this document will
adjust to follow these new guardrails as they become approved by DReps through a 
governance Info Action.
https://github.com/Crypto2099/CIPs/tree/social-governance-budget-guardrails/CIP-XXXX 

### Constitutional Requirements

The following requirements are currently specified within the content of the
Cardano (Draft) Constitution as specified in
the [Motiviaton](#motivation-why-is-this-cip-necessary).

> Changing or modifying these requirements would require a Constitution change.
> This section **MUST** be updated if or when the verbiage of the
> Constitution, specifically related to the budgetary process, is modified.

* A budget for ongoing maintenance and future development **MUST** be proposed
  at least once per year. _Budgets **MAY** be proposed more frequently._
* Withdrawals from the Cardano Treasury **MUST NOT** be permitted unless a
  budget is currently in effect.
* A budget proposal **MUST** specify the process to be used for overseeing use
  of funds.
* A budget proposal **MUST** designate one or more administrators who will be
  responsible for the oversight process.
* A _net change limit_ for the Cardano Treasury balance **MUST** be specified
  prior to a budget being proposed or ratified.
* A _net change period_ for the Cardano Treasury **MUST** be specified prior to
  a budget being proposed or ratified.
* A budget proposal (in aggregate with other proposals within the same time
  period), **MUST NOT** exceed the _net change limit_.
* A budget proposal **MUST** be denominated in Ada.
* A budget **MUST** be proposed as an _Info Action_ on-chain and **MUST** only
  be considered ratified after receiving approval from greater than 50% of
  active voting stake from DRep voters.


## Executive Summary

* The Budget Process is designed to be trust-minimized, where every transactions 
must have a maker & a checker
* The Treasury Process tries to keep transactions on-chain as much as possible to 
ensure transparency. Keeping Treasury on-chain to participate in approved opensource 
& audited protocol will also grow Cardano Defi ecosystem while encouraging dapps to 
adopt opensource culture.
* DReps will participate in 5-10 Budget Info Action votes per year to strike balance 
between control & overloading DReps with every single budget item. We can combine 
buckets to reduce number of votes DReps need to make to 3-5 if necessary. 
* DReps will participate in 1-2 Committee selection Info Action votes per year. We 
can reduce number of votes DReps need to make by allow Civic Committee to appoint the 
other Committees.
* DReps will participate in 4 Treasury Withdrawal votes per year. These votes should 
be easy as long as the numbers match with previous ratified Budget Info Action.  

### CIP Budget Process
1. A _net change limit_ and _net change period_ for the Cardano Treasury balance are 
ratified on-chain via a Governance Budget Info Action.
2. Each Committee will draft new budget proposal transparently as CIP-XXXX
3. The proposed budget CIP **MUST** be publicly published and socialized for a period 
of not less than 30 days. This provides sufficient time for community feedback, 
criticism, and refinement.
4. **On-Chain Ratification**: Following the community feedback phase, an _Info_governance 
action must be submitted to the chain. This Info Action **MUST** contain the unaltered 
and final version of the [Specification section](#specification) of the budget CIP. 
The _Info Action_ may be considered ratified when it achieves the same criteria as the current,
on-chain, Constitutionally-mandated requirements governing adoption of a _Budget Info Action_.
5. Treasury withdrawal will be done quarterly, combined all the projected expenditure for 
the coming quarter from all different budget buckets. Treasury Withdrawal governance action 
**MUST** include exact details of all payment to each Vendor in each Bucket.
6. Treasury Committee will be responsible to instruct Custodian to make payment to vendors 
according to the Ratified Treasury Withdrawal Governance Action.

### Administrators

#### Budget Committee Roles & Responsibilities
* Collate all buckets total budget and payment schedules from all Administrators
* Produce annual report on overview of Treasury & Budget utilization
* Prepare combined quarterly payment schedules to be submited as Treasury Withdrawal Governance Action
* Select Custodian to hold withdraw after withdrawal

#### Treasury Committee Roles & Responsibilities
* Manage Treasury withdraw held by Custodian to optimize yield during price fluctuation.
* Not allowed to speculate on any Cardano token besides ADA & approved stable coins
* Not allowed to stake in any SPO to earn staking rewards
* Not allowed to participate in governance voting Process
* Only allowed to participate in Opensourced & Audited Decentralized Finance Protocol on 
Cardano with ADA & approved stable coins.
* Must make payment onchain directly to Vendors according the payment schedule included 
in the Ratified Treasury Withdrawal Governance Action.

#### Bucket Administrator 

There are currently 6 proposed bucket as follow
1. Research Bucket to be administered by Product Committee
2. Development Bucket to be administered by Techonology Steering Committee
3. Core Infrastructure Bucket to be administered by Open Source Committee
4. Governance Support Bucket to be administered by Civic Committee
5. Outreach & Education Budget to be administered by Marketing Committee
6. Community Grant Bucket to be administered by Catalyst

##### Bucket Administrator Roles & Responsibilities
* Propose Annual Budget for the bucket following CIP Budget Process above
* After the proposed Budget for the bucket is Ratified by a Governance Info Action, 
select vendors & negotiate payment schedules
* Produce quarterly report on results of previous payments and payment schedules 
for the next quarter.

<hr />
## Rationale: how does this CIP achieve its goals?

This CIP achieves its goals by providing clear steps to budget
proposers and a clear set of rules that the community and governance entities
(DReps + CC members) may use to judge the quality and completeness of any
proposed budget.

The primary goal of this CIP is to serve as a living document that can grow,
change, and adapt with the Cardano community over time. It is the hope that
rules will be added, removed, and modified to suite the specific and evolving
needs of the community.

## Path to Active

### Acceptance Criteria

To be accepted and considered ratified, both this initial CIP and any subsequent
changes or modifications to it **MUST** follow the following procedure.

While any future edits or modifications to this initial CIP are being made, the
previous version shall be considered to be in force and active until such time
as this CIP is formally repealed, modified, or replaced.

#### Procedure

1. **Community Feedback**: The proposed changes **MUST** be publicly published
   and socialized for a period of not less than 30 days. This provides
   sufficient time for community feedback, criticism, and refinement.
2. **On-Chain Ratification**: Following the community feedback phase, an _Info_
   governance action must be submitted to the chain. This Info Action **MUST**
   contain the unaltered and final version of
   the [Specification section](#specification) of this CIP. The _Info Action_
   may be considered ratified when it achieves the same criteria as the current,
   on-chain, Constitutionally-mandated requirements governing adoption of a
   _Budget Info Action_.
3. **CIP Merging**: The current (or newly proposed) version of this CIP **MUST**
   only be merged once on-chain ratification (and subsequent proof) have been
   provided by the author(s) to the CIP Editor panel.

### Implementation Plan

N/A

## Copyright

This CIP is licensed
under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).

[RFC2119]: <https://datatracker.ietf.org/doc/html/rfc2119> "RFC 2119: Key words to indicate requirement levels"
