---
CIP: ???
Title: Social Governance | Budget and Withdrawal Guardrails
Category: Governance
Status: Proposed
Authors:
  - Adam Dean <adam@crypto2099.io>
Implementors: N/A
Discussions:
  - https://github.com/cardano-foundation/CIPs/pull/?
Created: 2024-11-06
License: CC-BY-4.0
---

## Abstract

The current Cardano (Draft) Constitution specifies a rough budget proposal and
approval process with a handful of very loose guardrails dictating when, where,
and how withdrawals from the Cardano Treasury should occur. The budget process
and methodology, as well as guardrails, should be more formally defined to
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

> ### 3. GUARDRAILS AND GUIDELINES ON TREASURY WITHDRAWAL ACTIONS
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


While this may be satisfactory in general terms from a Constitutional
perspective, it falls far short of a clearly defined set of prescriptive
guardrails guiding the allocation, auditing, and custody of budgetary funds for
both proposers, custodians, and community members to reference.

This CIP aims to define the template for budget proposals specifically in
relation to required and mandatory information that should be included in any
proposed budget.

## Specification

> The keywords "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "
> SHOULD", "SHOULD NOT", "RECOMMENDED",  "MAY", and
> "OPTIONAL" in this document are to be interpreted as described
> in [RFC 2119][RFC2119].

> It is understood that 1 Ada is the equivalent of 1 Million (1 000 000)
> Lovelace, the smallest, non-divisible unit of currency on the Cardano mainnet
> blockchain.

### Constitutional Requirements

The following requirements are currently specified within the content of the
Cardano (Draft) Constitution as specified in
the [Motiviaton](#motivation-why-is-this-cip-necessary).

> Changing or modifying these requirements would require a Constitution change.
> This section **MUST** be updated if or when the verbiage of the
> Constitution, specifically related to the budgetary process, is modified.

* A budget for ongoing maintenance and future development **MUST** be proposed
  once per year. _Budgets **MAY** be proposed more frequently._
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

### CIP Budget Requirements

The following requirements are only specified here, within the context of the
CIP process. Individual requirements **MUST** include a rationale and any
changes or modification (versioning) of these requirements should follow the
same criteria as specified within
the [Acceptance Criteria](#acceptance-criteria).

#### Rule: No (Governance) Leverage Allowed

##### Definition

Budget administrators **MUST NOT** utilize the Cardano Treasury funds, those in
their custody as part of the budget management and administration process, to
participate in any governance including but not limited to staking or delegating
to network validator(s), on-chain governance, or off-chain governance (Project
Catalyst).

##### Rationale

Budget administrators or custodians have a fiduciary responsibility to the
Cardano Community to faithfully oversee and administer the distribution of
withdrawn Treasury funds pursuant to the ratified budget. This may result in the
custodian(s) being in possession of large sums of Ada while awaiting milestone
completion for contracts.

Staking these custodial funds is problematic for a number of reasons:

1. Fairly selecting which stake pool(s) would receive delegation presents
   substantial administrative burden on the budget administrator.
2. Pool(s) receiving delegation may be harmed by approaching or becoming
   saturated from this ephemeral delegation, prohibiting the growth of
   long-term, sustainable delegation.

Using custodial funds in governance is similarly problematic:

1. Given on-chain governance actions may include the approval of future budgets
   or spending that would directly benefit the administrators, there is a clear
   conflict of interest in using custodial Ada for on-chain governance.
2. The custodial Ada held by the administrator is on behalf of the entire
   Cardano community. It would be impossible to fairly and accurately represent
   the will of the entire community through any on- or off-chain governance
   systems.

<hr />

#### Rule: Administrator Transparency

##### Definition

Budget administrators and custodians **MUST** be non-anonymous, legally
recognized, public entities with a publicly disclosed board of directors and/or
responsible parties.

##### Rationale

Individual budgets are likely to account for large amounts of value both in Ada
and fiat computation. The responsible parties to manage and oversee the budget
process should be publicly disclosed to bring confidence and accountability to
the Cardano community.

<hr />

#### Rule: Radical Transparency

##### Definition

Budget allotments earmarked for specific purposes (buckets) **MUST** be kept
separate and **MUST** be kept in secure, publicly disclosed addresses until
disbursed as part of the normal budget process.

##### Rationale

If a single custodian is responsible for multiple facets of the budget (core
development and research, for example) then it is imperative that the community
be capable of auditing the funds distributed from the Treasury to the custodian
and subsequently to contractor(s) engaging in work as part of the budget
process. Co-mingling (pooling) funds from various buckets decreases transparency
and should not be tolerated.

<hr />

#### Rule: Conflict Resolution

##### Definition

A budget proposal **MUST** define a jurisdiction and conflict resolution clause.
Custodial funds **MUST NOT** be used for court or legal expenses by the
administrator without an explicit _governance action_ authorization from the
Cardano Community following the same criteria as budget approval.

##### Rationale

By defining a _forum selection clause_ within the scope of the
community-approved budget we can reduce uncertainty for both the administrators
and the community should a conflict or dispute arise.

<hr />

#### Rule: Administrator Fees

##### Definition

A budget administrator and custodian, in total, **MUST NOT** charge more than 5%
of the total budget amount for administrative costs. All administrative costs
**MUST** be defined as part of the budget proposal.

##### Rationale

It is imperative that the withdrawn Treasury funds be protected from exorbitant
or malicious administrative costs that severely deplete the spendable funds. In
alignment with the goal of community transparency, it's important that all
administrative costs of budget management be disclosed as part of the budget
process.

<hr />

#### Rule: Applicable Period

##### Definition

A budget proposal **MUST** specify its validity period. A budget proposal
**MUST NOT** have a validity period longer than _net change period_ time.

Treasury withdrawals referencing a specific budget **MUST** occur within the
budget's specified validity period.

##### Rationale

Given that governance actors (DReps and CC) are tasked with ensuring that
treasury withdrawals align with a specified budget and do not change the
Treasury balance by greater than _net change limit_ within _net change period_
and that there may be one or more budgets active at any given time, it is
imperative that a given budget proposal specify the time period during which it
should be considered valid.

This provides an easy first point of indexing for governance actors to verify
withdrawal validity and also prevents treasury withdrawals against historical
budgets outside their validity period.

<hr />

#### Rule: Maximum Spend and Surplus Definitions

##### Definition

A budget proposal **MUST** define an absolute maximum spend amount (denominated
in Ada). If a budget is delineated into one or more spending categories
(buckets) then the budget **MUST** specify a maximum spend per category in
addition to a maximum spend for the total budget. A budget proposal **MUST**
define what will be done with any surplus funds at the end of the budget
validity period. A budget proposal **SHOULD** propose to return surplus funds to
the Treasury.

##### Rationale

Given that budgets are generally estimated ranges of spending, it is possible
that multiple withdrawals may be made against the same budget throughout its
validity period. To increase transparency, a budget must define the maximum
amount that may be spent against the entire budget and any specifically
earmarked categories or buckets.

Given that withdrawals will likely be made in large quarterly or semi-annual
batches, it is critical that a budget proposal address the plan of action should
there be any surplus funds remaining at the end of the budget validity period.
It is recommended that budget proposers should return any surplus funds to the
Treasury so these funds may recirculate into future budgets, but this is not
mandatory to leave room for creative surplus management strategies to be
developed and/or proposed.

## Rationale: how does this CIP achieve its goals?

This CIP achieves its goals by providing steering and direction to budget
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
