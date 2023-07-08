---
CIP: 1694
Title: A First Step Towards On-Chain Decentralized Governance
Status: Proposed
Category: Ledger
Authors:
    - Jared Corduan <jared.corduan@iohk.io>
    - Matthias Benkort <matthias.benkort@cardanofoundation.org>
    - Kevin Hammond <kevin.hammond@iohk.io>
    - Charles Hoskinson <charles.hoskinson@iohk.io>
    - Andre Knispel <andre.knispel@iohk.io>
    - Samuel Leathers <samuel.leathers@iohk.io>
Discussions:
    - <https://github.com/cardano-foundation/CIPs/pull/380>
    - <https://forum.cardano.org/t/swarm-session-cip-1694/114453>
    - <https://twitter.com/IOHK_Charles/status/1632211417221701632>
    - <https://twitter.com/RichardMcCrackn/status/1632514347195850752>
    - <https://twitter.com/RichardMcCrackn/status/1633135124500865024>
    - <https://twitter.com/_KtorZ_/status/1632356766368382976>
    - <https://twitter.com/_KtorZ_/status/1630087586193584128>
    - <https://twitter.com/_KtorZ_/status/1631430933219012608>
    - <https://twitter.com/technologypoet/status/1632158736985866241>
    - <https://twitter.com/danny_cryptofay/status/1631606919071776768>
    - <https://www.youtube.com/watch?v=2hCnmMG1__8>
    - <https://www.youtube.com/watch?v=KiLhhOVXQOg>
Created: 2022-11-18
License: CC-BY-4.0
---

## Abstract

We propose a revision of Cardano's on-chain governance system to support the new requirements for Voltaire.
The existing specialized governance support for protocol parameter updates and MIR certificates will be removed,
and two new fields will be added to normal transaction bodies for:

1. governance actions
2. votes

**Any Cardano user** will be allowed to submit a **governance action**.
We also introduce three distinct governance bodies that have specific functions in this new governance framework:

1. a constitutional committee
2. a group of delegate representatives (henceforth called **DReps**)
3. the stake pool operators (henceforth called **SPOs**)

Every governance action must be ratified by at least two of these three governance bodies using their on-chain **votes**.
The type of action and the state of the governance system determines which bodies must ratify it.

Ratified actions are then **enacted** on-chain, following a set of well-defined rules.

As with stake pools, any Ada holder may register to be a DRep and so choose to
represent themselves and/or others.  Also, as with stake pools, Ada holders may, instead, delegate their voting
rights to any other DRep.
Voting rights will be based on the total Ada that is delegated, as a whole number of Lovelace.

The most crucial aspect of this proposal is therefore the notion of **"one Lovelace = one vote"**.

#### Acknowledgements

<details>
  <summary><strong>First draft</strong></summary>

Many people have commented on and contributed to the first draft of this document, which was published in November 2022.
We would especially like to thank the following people for providing their wisdom and insights:

 * Jack Briggs
 * Tim Harrison
 * Philip Lazos
 * Michael Madoff
 * Evangelos Markakis
 * Joel Telpner
 * Thomas Upfield

We would also like to thank those who have commented via Github and other channels.
</details>

<details>
  <summary><strong>2023 Colorado Workshop (28/02 → 01/03)</strong></summary>

In addition, we would like to thank all the attendees of the workshop that was held in Longmont, Colorado on February 28th and March 1st 2023 for their valuable contributions
to this CIP, and for their active championing of Cardano's vision for minimal viable governance.  These include:

* Adam Rusch, ADAO & Summon
* Addie Girouard
* Andrew Westberg
* Darlington Wleh, LidoNation
* Eystein Hansen
* James Dunseith, Gimbalabs
* Juana Attieh
* Kenric Nelson
* Lloyd Duhon, DripDropz
* Marcus Jay Allen
* Marek Mahut, 5 Binaries
* Markus Gufler
* Matthew Capps
* Mercy, Wada
* Michael Dogali
* Michael Madoff
* Patrick Tobler, NMKR
* Philip Lazos
* π Lanningham, SundaeSwap
* Rick McCracken
* Romain Pellerin
* Sergio Sanchez Ferreros
* Tim Harrison
* Tsz Wai Wu
</details>

## Motivation: why is this CIP necessary?

+ [Goal](#goal)
+ [Current design](#current-governance-mechanism-design)
+ [Shortcomings of the Shelley governance design](#shortcomings-of-the-shelley-governance-design)
+ [Out of scope](#out-of-scope)

### Goal

We're heading into the age of Voltaire, laying down the foundations for decentralized decision-making.
This CIP describes a mechanism for on-chain governance that will underpin the Voltaire phase of Cardano.
The CIP builds on and extends the original Cardano governance scheme that was based on a fixed number of governance keys.
It aims to provide a **first step** that is both valuable and, importantly, is also technically achievable
in the **near term** as part of the proposed Voltaire governance system.

It also seeks to act as a jumping-off point for continuing community input,
including on appropriate threshold settings and other on-chain settings.

Subsequent proposals may adapt and extend this proposal to meet emerging governance needs.

### Current governance mechanism design

The on-chain Cardano governance mechanism that was introduced in the Shelley ledger era is capable of:

1. modifying the values of the protocol parameters (including initiating "hard forks")
2. transferring Ada out of the reserves and the treasury (and also moving Ada between the reserves and the treasury)

In the current scheme, governance actions are initiated by special transactions that require `Quorum-Many` authorizations
from the governance keys (5 out of 7 on the Cardano mainnet)[^1].
Fields in the transaction body provide details of the proposed governance action:
either i) protocol parameter changes; or ii) initiating funds transfers.
Each transaction can trigger both kinds of governance actions, and a single action can have more than one effect (e.g. changing two or more protocol parameters).

- Protocol parameter updates use [transaction field nº6](https://github.com/input-output-hk/cardano-ledger/blob/8884d921c8c3c6e216a659fca46caf729282058b/eras/babbage/test-suite/cddl-files/babbage.cddl#L56) of the transaction body.
- Movements of the treasury and the reserves use [Move Instantaneous Rewards (abbrev. MIR) certificates](https://github.com/input-output-hk/cardano-ledger/blob/8884d921c8c3c6e216a659fca46caf729282058b/eras/babbage/test-suite/cddl-files/babbage.cddl#L180).

Properly authorized governance actions are applied on an epoch boundary (they are **enacted**).

#### Hard Forks

One of the protocol parameters is sufficiently significant to merit special attention:
changing the major protocol version enables Cardano to enact controlled hard forks.
This type of protocol parameter update therefore has a special status, since stake pools
must upgrade their nodes so they can support the new protocol version once the hard fork is enacted.

### Shortcomings of the Shelley governance design

The Shelley governance design was intended to provide a simple, transitional approach to governance.
This proposal aims to address a number of shortcomings with that design
that are apparent as we move into Voltaire.

1. The Shelley governance design gives no room for active on-chain participation of Ada holders.
While changes to the protocol are usually the results of discussions with selected community actors,
the process is currently driven mainly by the founding entities.
Ensuring that everyone can voice their concern is cumbersome, and can be perceived as arbitrary at times.

2. Movements from the treasury constitute a critical and sensitive topic.
However, they can be hard to track.  It is important to have more transparency
and more layers of control over these movements.

3. While they need to be treated specially by SPOs, hard forks are not differentiated from other protocol parameter changes.

4. Finally, while there is currently a somewhat common vision for _Cardano_ that is shared by its founding entities and also by many community members,
there is no clearly defined document where these guiding principles are recorded.
It makes sense to leverage the Cardano blockchain to record the shared Cardano ethos in an immutable fashion, as a formal Cardano Constitution.

### Out of scope

The following topics are considered to be out of the scope of this CIP.

#### The contents of the constitution

This CIP focuses only on on-chain mechanisms.  The provisions of the initial constitution are extremely important, as are any processes that
will allow it to be amended.  These merit their own separate and focused discussion.

#### The membership of the constitutional committee

This is an off-chain issue.

#### Legal issues

Any potential legal enforcement of either the Cardano protocol or the Cardano Constitution are completely out of scope for this CIP.


#### Off chain standards for governance actions

The Cardano community must think deeply about the correct standards and processes for handling the creation of the governance actions that are specified in this CIP.
In particular, the role of Project Catalyst in creating treasury withdrawal actions is completely outside the scope of this CIP.


#### Ada holdings and delegation

How any private companies, public or private institutions,  individuals etc. choose to hold or delegate their Ada, including delegation to stake pools or DReps, is outside the scope of this CIP.

## Specification

+ [The Cardano Constitution](#the-cardano-constitution)
+ [The constitutional committee](#the-constitutional-committee)
  - [State of no-confidence](#state-of-no-confidence)
  - [Constitutional committee keys](#constitutional-committee-keys)
  - [Replacing the constitutional committee](#replacing-the-constitutional-committee)
  - [Size of the constitutional committee](#size-of-the-constitutional-committee)
  - [Term limits](#term-limits)
+ [Delegated representatives (DReps)](#delegated-representatives-dreps)
  - [Pre-defined DReps](#pre-defined-dreps)
  - [Registered DReps](#registered-dreps)
  - [New stake distribution for DReps](#new-stake-distribution-for-dreps)
  - [Incentives for Ada holders to delegate voting stake](#incentives-for-ada-holders-to-delegate-voting-stake)
  - [DRep incentives](#drep-incentives)
+ [Governance actions](#governance-actions)
  - [Ratification](#ratification)
    * [Requirements](#requirements)
    * [Restrictions](#restrictions)
  - [Enactment](#enactment)
  - [Lifecycle](#lifecycle)
  - [Content](#content)
  - [Protocol parameter groups](#protocol-parameter-groups)
+ [Votes](#votes)
  - [Governance state](#governance-state)
  - [Changes to the stake snapshot](#changes-to-the-stake-snapshot)
  - [Definitions relating to voting stake](#definitions-relating-to-voting-stake)

### The Cardano Constitution

The Cardano Constitution is a text document that defines Cardano's shared values and guiding principles.
At this stage, the Constitution is an informational document that unambiguously captures the core values of Cardano
and acts to ensure its long-term sustainability.
At a later stage, we can imagine the Constitution perhaps evolving into a smart-contract based set of rules that drives the entire governance framework.
For now, however, the Constitution will remain an off-chain document whose hash digest value will be recorded on-chain.
As discussed above, the Constitution is not yet defined and its content is out of scope for this CIP.

<!--------------------------- Constitutional committee ------------------------>

### The constitutional committee

We define a _constitutional committee_ which represents a set of individuals or entities
(each associated with a pair of Ed25519 credentials) that are collectively responsible for **ensuring that the Constitution is respected**.

Though it **cannot be enforced on-chain**, the constitutional committee is **only** supposed to vote
on the constitutionality of governance actions (which should thus ensure the long-term sustainability of the blockchain) and should be replaced
(via the **no confidence** action) if they overstep this boundary.
Said differently, there is a social contract between the constitutional committee and the actors of the network.
Although the constitutional committee could reject certain governance actions (by voting 'No' on them),
they should only do so when those governance actions are in conflict with the Constitution.

For example, if we consider the hypothetical Constitution rule "The Cardano network must always be able to produce new blocks",
then a governance action that would reduce the maximum block size to `0` would be, in effect,
unconstitutional and so might not be ratified by the constitutional committee.  The rule does
not, however, specify the smallest acceptable maximum block size, so the constitutional committee would need to determine this number
and vote accordingly.

#### State of no-confidence

The constitutional committee is considered to be in one of the following two states at all times:

1. a normal state (i.e. a state of confidence)
2. a state of no-confidence

In a _state of no-confidence_, the current committee is no longer able to participate in governance actions
and must be replaced before any governance actions can be ratified (see below).
Any outstanding governance actions are dropped immediately after the protocol enters a state of no-confidence,
and will not be enacted.

#### Constitutional committee keys

The constitutional committee will use a hot and cold key setup, similar to the existing "genesis delegation certificate" mechanism.

#### Replacing the constitutional committee

The constitutional committee can be replaced via a specific governance action
("New constitutional committee", described below) that requires the approval of both
the **SPOs** and the **DReps**.
The threshold for ratification might be different depending on if the governance is
in a state of confidence or a state of no confidence.

The new constitutional committee could, in principle, be identical to or partially overlap the outgoing committee as long as the action is properly ratified.
This might happen, for example, if the electorate has collective confidence in all or part of the committee and wishes to extend its term of office.


#### Size of the constitutional committee

Unlike the Shelley governance design, the size of the constitutional committee is not fixed and can be any nonnegative number.
It may be changed whenever a new committee is elected ("New constitutional committee and/or threshold").
Likewise, the committee threshold (the fraction of committee `Yes` votes that are required to ratify governance actions) is not fixed and
can also be varied by the governance action.
This gives a great deal of flexibility to the composition of the committee.
In particular, it is possible to elect an empty committee if the community wishes to abolish the constitutional committee entirely. Note that this is different from a state of no-confidence and still constitutes a governance system capable of enacting proposals.

There will be a new protocol parameter for the minimal size of the committee,
itself a nonnegative number.

#### Term limits

Each newly elected constitutional committee will have per-member term limits.
Per-member limits allow for a rotation scheme, such as a third of the committee
expiring every year.
Expired members can no longer vote.
Member can also willingly resign early, which will be marked on-chain as an expired member.

The system will automatically enter a state of no-confidence when the number of non-expired
committee members falls below the minimal size of the committee.
For example, a committee of size five with a quorum of three and two expired members can still
pass governance actions if all of non-expired members vote `Yes`.
However, if one more member expires then the system enters a state of no-confidence,
since the two remaining members are not enough to meet quorum.

The maximum term limit is a governance protocol parameter, specified as a number of epochs.
During a state of no-confidence, no action can be ratified,
so the committee should plan for its own replacement if it wishes to avoid disruption.

<!--------------------------- Constitutional committee ------------------------>
<!---------------------------           DReps          ------------------------>

### Delegated representatives (DReps)

> **Warning**
> CIP-1694 DReps **should not be conflated** with Project Catalyst DReps.

<!-- TODO find another name that still points to liquid democracy. -->

#### Pre-defined DReps

In order to participate in governance, each stake credential must be delegated to a DRep.
Ada holders will generally delegate their voting rights to a registered DRep
that will vote on their behalf.  In addition, two pre-defined DRep options are available:

* `Abstain`

  If an Ada holder delegates to `Abstain`, then their stake is actively marked
  as not participating in governance.

  The effect of delegating to `Abstain` on chain is that the delegated stake *will not* be considered to be
  a part of the active voting stake.  However, the stake *will* be considered to be registered for the
  purpose of the incentives that are described in [Incentives for Ada holders to delegate voting stake](#incentives-for-ada-holders-to-delegate-voting-stake).

* `No Confidence`

  If an Ada holder delegates to `No Confidence`, then their stake is counted as
  a **no** vote on every governance action apart from a "Motion of no confidence".
  This also signals that they have no confidence in the existing constitutional committee.

  The effect of delegating to `No Confidence` on chain is that this stake *will* be considered to be
  a part of the active voting stake. It will count as a `Yes` vote on every `No Confidence`
  action and a `No` vote on every other action.
  It also serves as a directly auditable measure of the confidence of Ada holders in the constitutional
  committee.


> **Note**
> The pre-defined DReps do not cast votes inside of transactions, their behavior is accounted for at the protocol level.
> The `Abstain` DRep may be chosen for a variety of reasons, including the desire to not
> participate in the governance system.

> **Note**
> Any Ada holder may register themselves as a DRep and delegate to themselves if they wish to actively participate in
> voting.

#### Registered DReps

In Voltaire, existing stake credentials will be
able to delegate their stake to registered DReps for voting purposes,
in addition to the current delegation to stake pools for block production.
DRep delegation will mimic the existing stake delegation mechanisms (via on-chain certificates).
Similarly, DRep registration will mimic the existing stake registration mechanisms.
Additionally, registered DReps will need to vote regularly to still be considered active.
Specifically, if a DRep does not submit any votes for `drepActivity`-many epochs, the DRep is considered inactive,
where `drepActivity` is a new protocol parameter.
Inactive DReps do not count towards the active voting stake anymore.
The reason for marking DReps as inactive is so that DReps who stop participating but still have
stake delegated to them do not eventually leave the system in a state where no governance
action can pass.

Registered DReps are identified by a credential that can be either:

* A verification key (Ed25519)
* A native or Plutus script

The blake2b-224 hash digest of a serialized DRep credential is called the _DRep ID_.

The following new types of certificates will be added for governance:
DRep registration certificates, DRep retirement certificates, and
vote delegation certificates.

##### DRep registration certificates

DRep registration certificates include:

* a DRep ID
* a deposit
* a stake credential (for the deposit return)
* an optional anchor

An **anchor** is a pair of:

* a URL to a JSON payload of metadata
* a hash of the contents of the metadata URL

The structure and format of this metadata is deliberately left open in this CIP.
The on-chain rules will not check either the URL or the hash.
Client applications should, however, perform the usual sanity checks when fetching content from the provided URL.


##### DRep retirement certificates

DRep retirement certificates include:

* a DRep ID
* the epoch number after which the DRep will retire
* an optional anchor

Note that a DRep is retired immediately upon the chain accepting a retirement certificate,
and the deposit is returned as part of the transaction that submits the retirement certificate
(the same way that stake credential registration deposits are returned).

##### Vote delegation certificates

Vote delegation certificates include:

* the DRep ID to which the stake should be delegated
* the stake credential for the delegator
* an optional anchor

> **Note**
>
> DRep delegation always maps a stake credential to a DRep credential.
> This means that a DRep cannot delegate voting stake to another DRep.

##### Certificate authorization schemes

The authorization scheme (i.e. which signatures are required for registration, retirement or delegation) mimics the existing stake delegation certificate authorization scheme.

<!-- TODO: Provide CBOR specification in the annexe for those new certificates. -->


#### New stake distribution for DReps

In addition to the existing per-stake-credential distribution and the
per-stake-pool distribution, the ledger will now also determine the per-DRep stake
distribution. This distribution will determine how much stake is backed by each
`Yes` vote from a DRep.

> **Warning**
>
> **Unlike** the distribution that is used for block production, we will always use the most
> current version of the per-DRep stake distribution as given on the epoch boundary.
>
> This means that **for any topic which individual voters care deeply about,
> they have time to register themselves as a DRep and vote directly**.
> However, it means that there may be a difference between the stake that is used for block
> production and the stake that is used for voting in any given epoch.


#### Incentives for Ada holders to delegate voting stake

There will be a short [bootstrapping phase](#bootstrapping-phase) during which rewards will be earned
for stake delegation etc. and may be withdrawn at any time.
After this phase, although rewards will continue to be earned for block delegation etc., reward accounts will be
**blocked from withdrawing any rewards** unless their associated stake credential is also delegated to a DRep
(either pre-defined or registered).  This helps to ensure high participation, and so, legitimacy.

> **Note**
>
> Even though rewards cannot be withdrawn, they are not lost.  As soon as a stake credential is delegated
> (including to a pre-defined DRep), the rewards can be withdrawn.

#### DRep incentives

DReps arguably need to be compensated for their work. Research on incentive models is still ongoing,
and we do not wish to hold up implementation of this CIP while this is resolved.

Our interim proposal is therefore to escrow Lovelace from the existing Cardano treasury until this
extremely important decision can be agreed on by the community, through the on-chain governance
mechanism that is being constructed.

Alternatively, DReps could pay themselves through instances of the "Treasury withdrawal" governance action.
Such an action would be auditable on-chain, and should reflect an off-chain agreement between DReps and delegators.

<!---------------------------           DReps          ------------------------>
<!---------------------------    Governance Actions    ------------------------>

### Governance actions

We define seven different types of **governance actions**.
A governance action is an on-chain event that is triggered by a transaction and has a deadline after which it cannot be enacted.

- An action is said to be **ratified** when it gathers enough votes in its favor (through the rules and parameters that are detailed below).
- An action that doesn't collect sufficient `Yes` votes before its deadline is said to have **expired**.
- An action that has been ratified is said to be **enacted** once it has been activated on the network.

Regardless of whether they have been ratified, actions may, however, be **dropped without being enacted** if,
for example, a motion of no confidence is enacted.


| Action                                                              | Description |
| :---                                                                | :--- |
| 1. Motion of no-confidence                                          | A motion to create a _state of no-confidence_ in the current constitutional committee |
| 2. New constitutional committee and/or threshold and/or term limits | Changes to the members of the constitutional committee and/or to its signature threshold and/or term limits|
| 3. Updates to the Constitution                                      | A modification to the off-chain Constitution, recorded as an on-chain hash of the text document |
| 4. Hard-Fork[^2] Initiation                                         | Triggers a non-backwards compatible upgrade of the network; requires a prior software upgrade |
| 5. Protocol Parameter Changes                                       | Any change to **one or more** updatable protocol parameters, excluding changes to major protocol versions ("hard forks") |
| 6. Treasury Withdrawals                                             | Movements from the treasury, sub-categorized into small, medium or large withdrawals (based on the amount of Lovelace to be withdrawn). The thresholds for treasury withdrawals are discussed below. |
| 7. Info                                                             | An action that has no effect on-chain, other than an on-chain record. |

**Any Ada holder** can submit a governance action to the chain.
They must provide a deposit of `govDeposit` Lovelace, which will be returned when the action is finalized
(whether it is **ratified**, has been **dropped**, or has **expired**).
The deposit amount will be added to the _deposit pot_, similar to stake key deposits.
It will also be counted towards the stake of the reward address it will be paid back to, to not reduce the submitter's voting power to vote on their own (and competing) actions.

Note that a motion of no-confidence is an extreme measure that enables Ada holders to revoke the power
that has been granted to the current constitutional committee.
Any outstanding governance actions, including ones that the committee has ratified or ones that would be enacted this epoch,
will be dropped if the motion is enacted.

> **Note**
> A **single** governance action might contain **multiple** protocol parameter updates. Many parameters are inter-connected and might require moving in lockstep.

#### Ratification

Governance actions are **ratified** through on-chain voting actions.
Different kinds of governance actions have different ratification requirements but always involve **two of the three** governance bodies,
with the exception of a hard-fork initiation, which requires ratification by all governance bodies.
Depending on the type of governance action, an action will thus be ratified when a combination of the following occurs:

* the constitutional committee approves of the action (the number of members who vote 'Yes' meet the threshold of the constitutional committee)
* the DReps approve of the action (the stake controlled by the DReps who vote 'Yes' meets a certain threshold of the total active voting stake)
* the SPOs approve of the action (the stake controlled by the SPOs who vote 'Yes' meets a certain threshold over the total registered voting stake)

> **Warning**
> As explained above, different stake distributions apply to DReps and SPOs.

A successful election of a new constitutional committee, a constitutional change or a hard-fork delays
ratification of all other governance actions until the first epoch after their enactment. This gives
a new constitutional committee enough time to vote on current proposals, re-evaluate existing proposals
with respect to a new constitution, and ensures that the in principle arbitrary semantic changes caused
by enacting a hard-fork do not have unintended consequences in combination with other actions.

##### Requirements

The following table details the ratification requirements for each governance action scenario. The columns represent:

* **Governance action type**<br/>
  The type of governance action. Note that the protocol parameter updates are grouped into three categories.

* **Constitutional committee (abbrev. CC)**<br/>
  A value of ✓ indicates that the constitutional committee must approve this action.<br/>
  A value of - means that constitutional committee votes do not apply.

* **DReps**<br/>
  The DRep vote threshold that must be met as a percentage of *active voting stake*.<br/>
  A value of - means that DReps votes do not apply.

* **SPOs**<br/>
  The SPO vote threshold which must be met as a percentage of the stake held by all stake pools.<br/>
  A value of - means that SPO votes do not apply.

| Governance action type                                            | CC   | DReps    | SPOs     |
| :---                                                              | :--- | :---     | :---     |
| 1. Motion of no-confidence                                        | \-   | $P_1$    | $Q_1$    |
| 2<sub>a</sub>. New committee/threshold (_normal state_)           | \-   | $P_{2a}$ | $Q_{2a}$ |
| 2<sub>b</sub>. New committee/threshold (_state of no-confidence_) | \-   | $P_{2b}$ | $Q_{2b}$ |
| 3. Update to the Constitution                                     | ✓    | $P_3$    | \-       |
| 4. Hard-fork initiation                                           | ✓    | $P_4$    | $Q_4$    |
| 5<sub>a</sub>. Protocol parameter changes, network group          | ✓    | $P_{5a}$ | \-       |
| 5<sub>b</sub>. Protocol parameter changes, economic group         | ✓    | $P_{5b}$ | \-       |
| 5<sub>c</sub>. Protocol parameter changes, technical group        | ✓    | $P_{5c}$ | \-       |
| 5<sub>d</sub>. Protocol parameter changes, governance group       | ✓    | $P_{5d}$ | \-       |
| 6. Treasury withdrawal                                            | ✓    | $P_6$    | \-       |
| 7. Info                                                           | ✓    | $100$    | $100$    |

Each of these thresholds is a governance parameter.
The initial thresholds should be chosen by the Cardano community as a whole.
The two thresholds for the Info action are set to 100% since setting it any lower
would result in not being able to poll above the threshold.

> **Note**
> It may make sense for some or all thresholds to be adaptive with respect to the Lovelace that is actively registered to vote.
> For example, a threshold could vary between 51% for a high level of registration and 75% for a low level registration.
> Moreover, the treasury threshold could also be adaptive, depending on the total Lovelace that is being withdrawn,
> or different thresholds could be set for different levels of withdrawal.

> **Note**
> To achieve legitimacy, the minimum acceptable threshold should be no less than 50% of the delegated stake.


##### Restrictions

Apart from _Treasury withdrawals_ and _Infos_, we include a mechanism for ensuring that governance
actions of the same type do not accidentally clash with each other in an unexpected way.

Each governance action must include the governance action ID for the most recently enacted action of its given type.
This means that two actions of the same type can be enacted at the same time,
but they must be *deliberately* designed to do so.


#### Enactment

Actions that have been ratified in the current epoch are prioritized as follows for enactment:

1. Motion of no-confidence
2. New committee/threshold
3. Updates to the Constitution
4. Hard Fork initiation
5. Protocol parameter changes
6. Treasury withdrawals
7. Info

> **Note** Enactment for _Info_ actions is a null action, since they do not have any effect on the protocol.

Enactment of a successful _Motion of no-confidence_ invalidates *all* other **not yet enacted** governance actions (whether or not they have been ratified),
causing them to be immediately **dropped** without ever being enacted.
Deposits for dropped actions will be returned immediately.

##### Order of enactment

Governance actions are enacted in order of acceptance to the chain.
This resolves conflicts where, e.g. there are two competing parameter changes.

#### Lifecycle

Governance actions are checked for ratification only on an epoch boundary.
Once ratified, actions are staged for enactment.

All submitted governance actions will therefore either:

1. be **ratified**, then **enacted**
2. be **dropped** as a result of a successful _Motion of no-confidence_
3. or **expire** after a number of epochs

In all of those cases, deposits are returned immediately.

Some actions will be enacted _immediately_ (i.e. at the same epoch boundary they are ratified), others are enacted only on _the following epoch boundary_.

| Governance action type         | Enactment           |
| :--                            | :--                 |
| 1. Motion of no-confidence     | Immediate           |
| 2. New committee/threshold     | Immediate           |
| 3. Update to the Constitution  | Immediate           |
| 4. Hard-fork initiation        | Next epoch boundary |
| 5. Protocol parameter changes  | Next epoch boundary |
| 6. Treasury withdrawal         | Immediate           |
| 7. Info                        | Immediate           |

<!-- TODO - break up the protocol parameters into those which effect the header/body validation split (so that some can be enacted immediately)? -->

#### Content

Every governance action will include the following:

* a deposit amount (recorded since the amount of the deposit is an updatable protocol parameter)
* a reward address to receive the deposit when it is repaid
* an optional anchor for any metadata that is needed to justify the action
* a hash digest value to prevent collisions with competing actions of the same type (as described earlier)

<!-- TODO: Provide a CBOR specification in the annexe for these new on-chain entities -->

In addition, each action will include some elements that are specific to its type:

| Governance action type         | Additional data                                               |
| :--                            | :--                                                           |
| 1. Motion of no-confidence     | None                                                          |
| 2. New committee/threshold     | The set of verification key hash digests (members to be removed), a map of verification key hash digests to epoch numbers (new members and their term limit),  and a fraction (quorum threshold) |
| 3. Update to the Constitution  | A hash digest of the Constitution document                    |
| 4. Hard-fork initiation        | The new (greater) major protocol version                      |
| 5. Protocol parameters changes | The changed parameters                                        |
| 6. Treasury withdrawal         | A map from stake credentials to a positive number of Lovelace |
| 7. Info                        | None                                                          |

> **Warning**
> For treasury withdrawals, there will be upper and lower thresholds on the amount: the withdrawal threshold is the **total** amount of Lovelace that is withdrawn by the action, not the amount of any single withdrawal if the action specifies more than one withdrawal.

> **Note**
> The new major protocol version must be precisely one greater than the current protocol version.
> Any two consecutive epochs will therefore either have the same major protocol version, or the
> later one will have a major protocol version that is one greater.

> **Note**
> There can be no duplicate committee members - each pair of credentials in a committee must be unique.

Each governance action that is accepted on the chain will be assigned a unique identifier (a.k.a. the **governance action ID**),
consisting of the transaction hash that created it and the index within the transaction body that points to it.

#### Protocol Parameter groups

We have grouped the protocol parameter changes by type,
allowing different thresholds to be set for each group.

We are not, however, restricting each protocol parameter governance action to be contained within one group.
In case where a governance action carries updates for multiple parameters from different groups,
the maximum threshold of all the groups involved will apply to any given such governance action.

The _network_,  _economic_ and _technical_ parameter groups collect existing protocol parameters that were introduced during the Shelley, Alonzo and Babbage eras.
In addition, we introduce a new _governance_ group that is specific to the new governance parameters that will be introduced by CIP-1694.

The **network group** consists of:
* maximum block body size (`maxBBSize`)
* maximum transaction size (`maxTxSize`)
* maximum block header size (`maxBHSize`)
* maximum size of a serialized asset value (`maxValSize`)
* maximum script execution units in a single transaction (`maxTxExUnits`)
* maximum script execution units in a single block (`maxBlockExUnits`)
* maximum number of collateral inputs (`maxCollateralInputs`)

The **economic group** consists of:
* minimum fee coefficient (`minFeeA`)
* minimum fee constant (`minFeeB`)
* delegation key Lovelace deposit (`keyDeposit`)
* pool registration Lovelace deposit (`poolDeposit`)
* monetary expansion (`rho`)
* treasury expansion (`tau`)
* minimum fixed rewards cut for pools (`minPoolCost`)
* minimum Lovelace deposit per byte of serialized UTxO (`coinsPerUTxOByte`)
* prices of Plutus execution units (`prices`)

The **technical group** consists of:
* pool pledge influence (`a0`)
* pool retirement maximum epoch (`eMax`)
* desired number of pools (`nOpt`)
* Plutus execution cost models (`costModels`)
* proportion of collateral needed for scripts (`collateralPercentage`)

The **governance group** consists of all the new protocol parameters that are introduced in this CIP:
* governance voting thresholds ($P_1$, $P_{2a}$, $P_{2b}$, $P_3$, $P_4$, $P_{5a}$, $P_{5b}$, $P_{5c}$, $P_6$, $P_7$, $Q_1$, $Q_{2b}$, $Q_4$)
* constitutional committee term limits
* governance action expiration
* governance action deposit (`govDeposit`)
* DRep deposit amount (`drepDeposit`)
* DRep activity period (`drepActivity`)
* minimal constitutional committee size
* maximum term limit (in epochs) of the constitutional committee

<!-- TODO:
  - Decide on the initial values for the new governance parameters

  - Decide on coherence conditions on the voting thresholds.
    For example, the threshold for a motion of no-confidence should arguably be higher than that of a minor treasury withdrawal.
-->

<!---------------------------    Governance Actions    ------------------------>

<!---------------------------          Votes           ------------------------>

### Votes

Each vote transaction consists of the following:

* a governance action ID
* a role - constitutional committee member, DRep, or SPO
* a governance credential witness for the role
* an optional anchor (as defined above) for information that is relevant to the vote
* a 'Yes'/'No'/'Abstain' vote

For SPOs and DReps, the number of votes that are cast (whether 'Yes', 'No' or 'Abstain') is proportional to the Lovelace that is delegated to them at the point the
action is checked for ratification.  For constitututional committee members, each current committee member has one vote.
Votes from unregistered SPOs or DReps count as having zero stake.

> **Warning** 'Abstain' votes are not included in the "active voting stake".
>
> Note that an explicit vote to abstain differs from abstaining from voting.
> Unregistered stake that did not vote behaves like an 'Abstain' vote,
> while registered stake that did not vote behaves like a 'No' vote.
> To avoid confusion, we will only use the word 'Abstain' from this point onward to mean an on-chain vote to abstain.

The governance credential witness will trigger the appropriate verifications in the ledger according to the existing `UTxOW` ledger rule
(i.e. a signature check for verification keys, and a validator execution with a specific vote redeemer and new Plutus purpose for scripts).

Votes can be cast multiple times for each governance action by a single credential.
Correctly submitted votes override any older votes for the same credential and role.
That is, the voter may change their position on any action if they choose.
As soon as a governance action is ratified, voting ends and transactions containing further votes are invalid.

#### Governance state

When a governance action is successfully submitted to the chain, its progress will be tracked by the ledger state.
In particular, the following will be tracked:

* the governance action ID
* the epoch that the action expires
* the deposit amount
* the rewards address that will receive the deposit when it is returned
* the total 'Yes'/'No'/'Abstain' votes of the constitutional committee for this action
* the total 'Yes'/'No'/'Abstain' votes of the DReps for this action
* the total 'Yes'/'No'/'Abstain' votes of the SPOs  for this action


#### Changes to the stake snapshot

Since the stake snapshot changes at each epoch boundary, a new tally must be calculated when each unratified governance action
is checked for ratification.  This means that an action could be enacted even though the DRep or SPO votes have not changed
(since the vote delegation could have changed).

#### Definitions relating to voting stake

We define a number of new terms related to voting stake:

* Lovelace contained in a transaction output is considered **active for voting** (that is, it forms the "active voting stake"):
  * It contains a registered stake credential.
  * The registered stake credential has delegated its voting rights to a registered DRep.
* Relative to some percentage `P`, a DRep (SPO) **vote threshold has been met** if the sum of the relative stake that has been delegated to the DReps (SPOs)
  that vote 'Yes' to a governance action
  is at least `P`.

## Rationale

+ [Role of the constitutional committee](#role-of-the-constitutional-committee)
+ [Intentional omission of identity verification](#intentional-omission-of-identity-verification)
+ [Reducing the power of entities with large amounts of Ada](#reducing-the-power-of-entities-with-large-amounts-of-ada)
+ [Piggybacking on stake pool stake distribution](#piggybacking-on-stake-pool-stake-distribution)
+ [Separation of hard-fork initiation from standard protocol parameter changes](#separation-of-hard-fork-initiation-from-standard-protocol-parameter-changes)
+ [Treasury withdrawals vs Project Catalyst](#treasury-withdrawals-vs-project-catalyst)
+ [The purpose of the DReps](#the-purpose-of-the-dreps)
+ [Ratification requirements table](#ratification-requirements-table)
+ [Motion of no-confidence](#motion-of-no-confidence)
+ [New committee/threshold (state of no-confidence)](#new-committeethreshold-state-of-no-confidence)
+ [The versatility of the info governance action](#the-versatility-of-the-info-governance-action)
+ [Hard-fork initiation](#hard-fork-initiation)
+ [New metadata structures](#new-metadata-structures)
+ [Controlling the number of active governance actions](#controlling-the-number-of-active-governance-actions)
+ [No AVST](#no-avst)

### Role of the constitutional committee

At first sight, the constitutional committee may appear to be a special committee that has been granted extra power over DReps.
However, because DReps can replace the constitutional committee at any time and DRep votes are also required to ratify every governance action,
the constitutional committee has no more (and may, in fact, have less) power than the DReps.
Given this, what role does the committee play, and why is it not superfluous?
The answer is that the committee solves the bootstrapping problem of the new governance framework.
Indeed, as soon as we pull the trigger and enable this framework to become active on-chain, then without a constitutional committee,
there would rapidly need to be sufficient DReps, so that the system did not rely solely on SPO votes.
We cannot yet predict how active the community will be in registering as DReps, nor how reactive other Ada holders will be regarding delegation of votes.

Thus, the constitutional committee comes into play to make sure that the system can transition from
its current state into fully decentralized governance in due course.
Furthermore, in the long run, the committee can play a mentoring and advisory role in the governance
decisions by being a set of elected representatives who are put under the spotlight for their judgment and guidance in governance decisions.
Above all, the committee is required at all times to adhere to the Constitution and to ratify proposals in accordance with the provisions of the Constitution.

### Intentional Omission of Identity Verification

Note that this CIP does not mention any kind of identity validation or verification for the members of the constitutional committee or the DReps.

This is intentional.

We hope that the community will strongly consider only voting for and delegating to those DReps who provide something like a DID to identify themselves.
However, enforcing identity verification is very difficult without some centralized oracle, which we consider to be a step in the wrong direction.

### Reducing the power of entities with large amounts of Ada

Various mechanisms, such as quadratic voting, have been proposed to guard against entities with a large amount of influence.
In a system based on "1 Lovelace, 1 vote", however, it is trivially easy to split stake into small amounts and undo the protections.
Without an on-chain identity verification system we cannot adopt any such measures.

### Piggybacking on stake pool stake distribution

The Cardano protocol is based on a Proof-of-Stake consensus mechanism, so using a stake-based governance approach is sensible.
However, there are many ways that could be used to define how to record the stake distribution between participants.
As a reminder, network addresses can currently contain two sets of credentials: one to identify who can unlock funds at an address
(a.k.a. payment credentials) and one that can be delegated to a stake pool (a.k.a. delegation credentials).

Rather than defining a third set of credentials, we instead propose to re-use the existing delegation credentials,
using a new on-chain certificate to determine the governance stake distribution. This implies that the set of DReps can (and likely will) differ from the set of SPOs,
so creating balance. On the flip side, it means that the governance stake distribution suffers from the same shortcomings as that for block production:
for example, wallet software providers must support multi-delegation schemes and must facilitate the partitioning of stake into sub-accounts should an Ada holder desire to delegate to multiple DReps,
or an Ada holder must manually split their holding if their wallet does not support this.

However, this choice also limits future implementation effort for wallet providers and minimizes the effort that is needed for end-users to participate in the governance protocol.
The latter is a sufficiently significant concern to justify the decision. By piggybacking on the existing structure,
the system remains familiar to users and reasonably easy to set up. This maximizes both the chance of success of, and the rate of participation in, the governance framework.

### Separation of Hard Fork Initiation from Standard Protocol Parameter Changes

In contrast to other protocol parameter updates, hard forks (or, more correctly, changes to the protocol's major version number) require much more attention.
Indeed, while other protocol parameter changes can be performed without significant software changes,
a hard fork assumes that a super-majority of the network has upgraded the Cardano node to support the new set of features that are introduced by the upgrade.
This means that the timing of a hard fork event must be communicated well ahead of time to all Cardano users, and requires coordination between stake pool operators, wallet providers, DApp developers, and the node release team.

Hence, this proposal, unlike the Shelley scheme, promotes hard fork initiations as a standalone governance action, distinct from protocol parameter updates.

### The purpose of the DReps

Nothing in this proposal limits SPOs from becoming DReps.
Why do we have DReps at all?
The answer is that SPOs are chosen purely for block production and not all SPOs will want to become DReps.
Voters can choose to delegate their vote to DReps without needing to consider whether they are
also a good block producer, and SPOs can choose to represent Ada holders or not.

### Ratification Requirements Table

The requirements in the [ratification requirement table](#requirements) are explained here.
Most of the governance actions have the same kind of requirements:
the constitutional committee and the DReps must reach a sufficient number of
'Yes' votes.
This includes these actions:
* New committee/threshold (normal state)
* Update to the Constitution
* Protocol parameter changes
* Treasury withdrawal

### Motion of no-confidence

A motion of no-confidence represents a lack of confidence by the Cardano community in the
current constitutional committee, and hence the constitutional committee should not
be included in this type of governance action.
In this situation, the SPOs and the DReps are left to represent the will of the community.

### New committee/threshold (state of no-confidence)

Similar to the motion of no-confidence, electing a constitutional committee
depends on both the SPOs and the DReps to represent the will of the community.

### The versatility of the info governance action

While not binding on chain, the Info governance action could be useful in an number of
situations.  These include:

* ratifying a CIP
* deciding on the genesis file for a new ledger era
* recording initial feedback for future governance actions

### Hard-Fork initiation

Regardless of any governance mechanism, SPO participation is needed for any hard fork since they must upgrade their node software.
For this reason, we make their cooperation explicit in the hard fork initiation governance action,
by always requiring their vote.
The constitutional committee also votes, signaling the constitutionality of a hard fork.
The DReps also vote, to represent the will of every stake holder.

### New Metadata structures

Both the governance actions and the votes use new metadata fields,
in the form of URLs and integrity hashes
(mirroring the metadata structure for stake pool registration).
The metadata is used to provide context.
Governance actions need to explain why the action is needed,
what experts were consulted, etc.
Since transaction size constraints should not limit this explanatory data,
we use URLs instead.

This does, however, introduce new problems.
If a URL does not resolve, what should be the expectation for voting on that action?
Should we expect everyone to vote 'No'?
Is this an attack vector against the governance system?
In such a scenario, the hash pre-image could be communicated in other ways, but we should be
prepared for the situation.
Should there be a summary of the justification on chain?

#### Alternative: Use of transaction metadata

Instead of specific dedicated fields in the transaction format, we could instead use the existing transaction metadata field.

Governance-related metadata can be clearly identified by registering a CIP-10 metadata label.
Within that, the structure of the metadata can be determined by this CIP (exact format TBD), using an index to map the vote or governance action ID to the corresponding metadata URL and hash.

This avoids the need to add additional fields to the transaction body, at the risk of making it easier for submitters to ignore.
However, since the required metadata can be empty (or can point to a non-resolving URL),
it is already easy for submitters to not provide metadata, and so it is unclear whether this makes the situation worse.

Note that transaction metadata is never stored in the ledger state, so it would be up to clients
to pair the metadata with the actions and votes in this alternative, and would not be available
as a ledger state query.

### Controlling the number of active governance actions

Since governance actions are available for anyone to submit, we need some mechanism to prevent those
individuals responsible for voting from becoming overwhelmed with a flood of proposals.
A large deposit is one such mechanism, but this comes at the unfortunate cost of being a barrier
for some people to submit an action.
Note, however, that crowd-sourcing with a Plutus script is always an option to gather the deposit.

We could, alternatively, accept the possibility of a large number of actions active at any given
time, and instead depend on off-chain socialization to guide voters' attention to those that merit it.
In this scenario, the constitutional committee might choose to only consider proposals which have
already garnered enough votes from the DReps.

### No AVST

An earlier draft of this CIP included the notion of an "active voting stake threshold", or AVST.
The purpose of AVST was to ensure the legitimacy of each vote, removing the possibility that, for example,
9 out of 10 Lovelace could decide the fate of millions of entities on Cardano.
There are really two concerns here, which are worth separating.

The first concern is that of bootstrapping the system, i.e. reaching the initial moment when
sufficient stake is registered to vote.
The second concern is that the system could lose participation over time.
One problem with the AVST is that it gives an incentive for SPOs to desire a low voting registration
(since their votes then hold more weight).
This is absolutely not a slight on the existing SPOs, but an issue with bad incentives.

We have chosen, therefore, to solve the two concerns differently.
We solve the bootstrapping problem as described in the section on bootstrapping.
We solve the long-term participation problem by not allowing reward withdrawals
(after the bootstrap phase) unless the stake is delegated to a DRep
(including the two special cases, namely 'Abstain' and 'No confidence').

## Path to Active

### Acceptance Criteria

- [ ] A new ledger era is enabled on the Cardano mainnet, which implements the above specification.

### Implementation Plan

The features in this CIP require a hard fork.

This document describes an ambitious change to Cardano governance.
We propose to implement the changes via **one hard fork**.

In the following sections, we give more details about the various implementation work items that have already been identified.
In addition, the final section exposes a few open questions which will need to be finalized.
We hope that those questions can be addressed through community workshops and discussions.

#### Ratification of this proposal

The ratification of this proposal is something of a circular problem: we need some form of governance framework in order to agree on what the final governance framework should be.
As has been stated many times, CIPs are not authoritative, nor are they a governance mechanism.
Rather, they describe technical solutions that have been deemed sound (from a technical standpoint) by community of experts.

CIP-1694 arguably goes beyond the usual scope of the CIP process and there is a strong desire to ratify this CIP through _some process_.
However, that process is yet to be defined and it remains an open question.
The final ratification process is likely to be a blend of various ideas, such as:

- [ ] Gather opinions from community-held workshops, akin to the Colorado workshop of February-March 2023.
- [ ] Exercise voting actions on a public testnet, with sufficient participation.
- [ ] Poll the established SPOs.
- [ ] Leverage Project Catalyst to gather inputs from the existing voting community (albeit small in terms of active stake).

#### Changes to the transaction body

- [ ] New elements will be added to the transaction body, and existing update and MIR capabilities will be removed. In particular,

  The governance actions and votes will comprise two new transaction body fields.

- [ ] Three new kinds of certificates will be added in addition to the existing ones:

  * DRep registration
  * DRep de-registration
  * Vote delegation

  And similarly, the current MIR and genesis certificates will be removed.

- [ ] A new `Voting` purpose will be added to Plutus script contexts.
  This will provide, in particular, the vote to on-chain scripts.

> **Warning** As usual, we will provide a CDDL specification for each of those changes.

#### Changes to the existing ledger rules

* The `PPUP` transition rule will be rewritten and moved out of the `UTxO` rule and into the `LEDGER` rule as a new `TALLY` rule.

  It will process and record the governance actions and votes.

* The `NEWEPOCH` transition rule will be modified.
* The `MIR` sub-rule will be removed.
* A new `RATIFY` rule will be introduced to stage governance actions for enactment.

  It will ratify governance actions, and stage them for enactment in the current or next epoch, as appropriate.

* A new `ENACTMENT` rule will be called immediately after the `EPOCH` rule. This rule will enact governance actions that have previously been ratified.
* The `EPOCH` rule will no longer call the `NEWPP` sub-rule or compute whether the quorum is met on the PPUP state.

#### Changes to the local state-query protocol

The on-chain governance workload is large, but the off-chain workload for tools and applications will arguably be even larger.
To build an effective governance ecosystem, the ledger will have to provide interfaces to various governance elements.

While votes and DReps (de)registrations are directly visible in blocks and will, therefore, be accessible via the existing local-chain-sync protocols; we will need to upgrade the local-state-query protocol to provide extra insights on information which are harder to infer from blocks (i.e. those that require maintaining a ledger state). New state queries should cover (at least):

- Governance actions currently staged for enactment
- Governance actions under ratification, with the total and percentage of yes stake, no stake and abstain stake
- The current constitutional committee, and constitution hash digest

#### Bootstrapping Phase

We will need to be careful how we bootstrap this fledgling government.  All the parties
that are involved will need ample time to register themselves and to become familiar with the process.

Special provisions will apply in the initial bootstrap phase.
Firstly, during the bootstrap phase, a vote from the constitutional committee
is sufficient to change the protocol parameters.
Secondly, during the bootstrap phase, a vote from the constitutional committee,
together with a sufficient SPO vote, is sufficient to initiate a hard fork.
No other actions are possible during the bootstrap phase.

The bootstrap phase ends when a given number of epochs has elapsed,
as specified in the next ledger era configuration file.
This is likely to be a number of months after the hard fork.

Moreover, there will be an interim Constitutional committee,
also specified in the next ledger era configuration file,
whose term limits will be set to expire when the bootstrap phase ends.
The rotational schedule of the first non-bootstrap committee could be included in the constitution itself.
Note, however, that since the constitutional committee never votes on new committees,
it cannot actually enforce the rotation.

#### Final safety measure, post bootstrapping

Many people have stated that they believe that the actual voting turnout will not be so large
as to be a strain on the throughput of the system.
We also believe that this is likely to be the case, but when the bootstrap phase ends we will
put one final, temporary safety	measure in place (this will also allow us to justify a low DRep deposit amount).

For values of $X$ and $Y$ that are still to be determined,
as soon as the bootstrap phase has ended,
when we calculate the DReps stake distribution for the next epoch boundary,
we will consider _only_ those DReps that are _either_ in the top $X$-many DReps ranked by stake amount,
or those DReps that have at least $Y$ Lovelace.
Every epoch, the value of $X$ will _increase_ and the value of $Y$ will decrease,
so that eventually $X$ will be effectively infinite and $Y$ will be zero.
Note that this is only an incentive, and nothing actually stops any DRep from casting their
vote (though it will not be counted if it does not meet the requirements).

If the community decides at some point that there is indeed a problem with congestion,
then a hard fork could be enacted that limits the number of DReps in a more restrictive way.

Reasonable numbers for the initial value of $X$ are probably 5,000-10,000.
Reasonable numbers for the initial value of $Y$ are probably the total number of Lovelace
divided by the initial value of $X$.

The mechanism should be set to relax at a rate where the restriction is completely eliminated after
a period of six months to one year.

#### Other Ideas / Open Questions

##### Pledge-weighted SPO voting

The SPO vote could additionally be weighted by each SPO's pledge.
This would provide a mechanism for allowing those with literal stake in the game to have a stronger vote.
The weighting should be carefully chosen.

##### Automatic re-delegation of DReps

A DRep could optionally list another DRep credential in their registration certificate.
Upon retirement, all of the DRep's delegations would be automatically transferred to the
given DRep credential.  If that DRep had already retired, the delegation would be transfer
to the 'Abstain' DRep.

##### No DRep registration

Since the DRep registration does not perform any necessary functions,
the certificates for (de-)registering DReps could be removed. This
makes the democracy more liquid since it removes some bureaucracy and
also removes the need for the DRep deposit, at the cost of moving the anchor that is part of the
DRep registration certificate into the transaction metadata.

##### Reduced deposits for some government actions

The deposit that is attached to governance actions exists to prevent a flood of non-serious governance
actions, each of which would require time and attention from the Cardano community.
We could reduce this deposit for proposals which go through some agreed upon off-chain process.
This would be marked on-chain by the endorsement of at least one constitutional committee member.
The downside of this idea is that it gives more power to the constitutional committee.

##### Include hash of (future) genesis configuration within hard-fork proposal

Some hard-forks require new genesis configurations.
This has been the case for the Shelley and Alonzo hard forks (but not Allegra, Mary, Vasil or Valentine), may be the case in the future.
At the moment, this proposal doesn't state anything about such a genesis configuration:
it is implicitly assumed to be an off-chain agreement.
We could however, enforce that (the hash of) a specific genesis configuration is also captured within a hard-fork governance action.

##### Adaptive thresholds

As discussed above, it may make sense for some or all thresholds to be adaptive with respect to the Lovelace that is actively registered to vote,
so that the system provides greater legitimacy when there is only a low level of active voting stake.
The bootstrapping mechanism that is proposed above may subsume this, however, by ensuring that the governance system is activated
only when a minimum level of stake has been delegated to DReps.


##### Renaming DReps / state of no-confidence?

It has been stated several times that "DReps" as presented here, might be confused with Project Catalst DReps.
Similarly, some people have expressed confusion between the state of no-confidence, the motion of no-confidence and the no-confidence DReps.

We could imagine finding better terms for these concepts.

##### Rate-limiting treasury movements

Nothing prevents money being taken out of the treasury other than the proposed votes and voting thresholds. Given that the Cardano treasury is a quite fundamental component of its monetary policy, we could imagine enforcing (at the protocol level) the maximum amount that can removed from the treasury over any period of time.

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode)

[^1]: A formal description of the current rules for governance actions is given in the [Shelley ledger specification](https://hydra.iohk.io/job/Cardano/cardano-ledger/shelleyLedgerSpec/latest/download-by-type/doc-pdf/ledger-spec).

    - For protocol parameter changes (including hard forks), the `PPUP` transition rule (Figure 13) describes how protocol parameter updates are processed, and the `NEWPP` transition rule (Figure 43) describes how changes to protocol parameters are enacted.

    - For funds transfers, the `DELEG` transition rule (Figure 24) describes how MIR certificates are processed, and the `MIR` transition rule (Figure 55) describes how treasury and reserve movements are enacted.

    > **Note**
    > The capabilities of the `MIR` transition rule were expanded in the [Alonzo ledger specification](https://hydra.iohk.io/job/Cardano/cardano-ledger/specs.alonzo-ledger/latest/download-by-type/doc-pdf/alonzo-changes)


[^2]: There are many varying definitions of the term "hard fork" in the blockchain industry. Hard forks typically refer to non-backwards compatible updates of a network. In Cardano, we formalize the definition slightly more by calling any upgrade that would lead to _more blocks_ being validated a "hard fork" and force nodes to comply with the new protocol version, effectively obsoleting nodes that are unable to handle the upgrade.

[^3]: This is the definition used in "active stake" for stake delegation to stake pools, see Section 17.1, Total stake calculation, of the [Shelley ledger specification](https://hydra.iohk.io/job/Cardano/cardano-ledger/shelleyLedgerSpec/latest/download-by-type/doc-pdf/ledger-spec).
