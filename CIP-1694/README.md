---
CIP: 1694
Title: A First Step Towards On-Chain Decentralized Governance
Status: Active
Category: Ledger
Authors:
    - Jared Corduan <jared.corduan@iohk.io>
    - Andre Knispel <andre.knispel@iohk.io>
    - Matthias Benkort <matthias.benkort@cardanofoundation.org>
    - Kevin Hammond <kevin.hammond@iohk.io>
    - Charles Hoskinson <charles.hoskinson@iohk.io>
    - Samuel Leathers <samuel.leathers@iohk.io>
Implementors: []
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
    - <https://github.com/cardano-foundation/CIPs/pull/916>
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
2. a group of delegated representatives (henceforth called **DReps**)
3. the stake pool operators (henceforth called **SPOs**)

Every governance action must be ratified by at least two of these three governance bodies using their on-chain **votes**.
The type of action and the state of the governance system determines which bodies must ratify it.

Ratified actions are then **enacted** on-chain, following a set of well-defined rules.

As with stake pools, any Ada holder may register to be a DRep and so choose to
represent themselves and/or others.  Also, as with stake pools, Ada holders may, instead, delegate their voting
rights to any other DRep.
Voting rights will be based on the total Ada that is delegated, as a whole number of Lovelace.

The most crucial aspect of this proposal is therefore the notion of **"one Lovelace = one vote"**.

For the many contributors to this proposal, see [Acknowledgements](#acknowledgements).
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
  - [Terms](#terms)
  - [Guardrails Script](#guardrails-script)
+ [Delegated representatives (DReps)](#delegated-representatives-dreps)
  - [Pre-defined Voting Options](#pre-defined-voting-options)
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
(each associated with a Ed25519 or native or Plutus script credential) that are collectively responsible for **ensuring that the Constitution is respected**.

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

#### Constitutional committee keys

The constitutional committee will use a hot and cold key setup, similar to the existing "genesis delegation certificate" mechanism.

#### Replacing the constitutional committee

The constitutional committee can be replaced via a specific governance action
("Update committee", described below) that requires the approval of both
the **SPOs** and the **DReps**.
The threshold for ratification might be different depending on if the governance is
in a normal state or a state of no confidence.

The new constitutional committee could, in principle, be identical to or partially overlap the outgoing committee as long as the action is properly ratified.
This might happen, for example, if the electorate has collective confidence in all or part of the committee and wishes to extend its term of office.


#### Size of the constitutional committee

Unlike the Shelley governance design, the size of the constitutional committee is not fixed and can be any nonnegative number.
It may be changed whenever a new committee is elected ("Update committee").
Likewise, the committee threshold (the fraction of committee `Yes` votes that are required to ratify governance actions) is not fixed and
can also be varied by the governance action.
This gives a great deal of flexibility to the composition of the committee.
In particular, it is possible to elect an empty committee if the community wishes to abolish the constitutional committee entirely. Note that this is different from a state of no-confidence and still constitutes a governance system capable of enacting proposals.

There will be a new protocol parameter for the minimal size of the committee,
itself a nonnegative number called `committeeMinSize`.

#### Terms

Each newly elected constitutional committee will have a term.
Per-member terms allow for a rotation scheme, such as a third of the committee
expiring every year.
Expired members can no longer vote.
Member can also willingly resign early, which will be marked on-chain as an expired member.

If the number of non-expired committee members falls below the minimal
size of the committee, the constitutional committee will be unable to
ratify governance actions. This means that only governance actions
that don't require votes from the constitutional committee can still
be ratified.

For example, a committee of size five with a threshold of 60% a minimum size
of three and two expired members can still
pass governance actions if two non-expired members vote `Yes`.
However, if one more member expires then the constitutional committee becomes
unable to ratify any more governance actions.

The maximum term is a governance protocol parameter, specified as a number of epochs.
During a state of no-confidence, no action can be ratified,
so the committee should plan for its own replacement if it wishes to avoid disruption.

#### Guardrails Script

While the constitution is an informal, off-chain document, there will
also be an optional script that can enforce some guidelines. This script
acts to supplement the constitutional committee by restricting some
proposal types. For example, if the community wishes to have some hard
rules for the treasury that cannot be violated, a script that enforces
these rules can be voted in as the guardrails script.

The guardrails script applies only to protocol parameter update and
treasury withdrawal proposals.

<!---------------------------           DReps          ------------------------>

### Delegated representatives (DReps)

> **Warning**
> CIP-1694 DReps **should not be conflated** with Project Catalyst DReps.

#### Pre-defined Voting Options

In order to participate in governance, a stake credential must be delegated to a DRep.
Ada holders will generally delegate their voting rights to a registered DRep
that will vote on their behalf. In addition, two pre-defined voting options are available:

* `Abstain`

  If an Ada holder delegates to `Abstain`, then their stake is actively marked
  as not participating in governance.

  The effect of delegating to `Abstain` on chain is that the delegated stake *will not* be considered to be
  a part of the active voting stake.  However, the stake *will* be considered to be registered for the
  purpose of the incentives that are described in [Incentives for Ada holders to delegate voting stake](#incentives-for-ada-holders-to-delegate-voting-stake).

* `No Confidence`

  If an Ada holder delegates to `No Confidence`, then their stake is counted
  as a `Yes` vote on every `No Confidence` action and a `No` vote on every other action.
  The delegated stake *will* be considered part of the active voting stake.
  It also serves as a directly auditable measure of the confidence of Ada holders in the constitutional
  committee.


> **Note**
> The pre-defined voting options do not cast votes inside of transactions, their behavior is accounted for at the protocol level.
> The `Abstain` option may be chosen for a variety of reasons, including the desire to not
> participate in the governance system.

> **Note**
> Any Ada holder may register themselves as a DRep and delegate to themselves if they wish to actively participate in
> voting.

> **Note**
> Any wallet serving as the Registered Reward Wallet for a Stake Pool can be delegated to one of these Pre-defined Voting Options and doing so will serve as the default voting option selected by the SPO for all Governance Action votes, excepting Hard Fork Governance Actions. Due to the need for robust consensus around Hard Fork initiations, these votes must be met as a percentage of the stake held by all stake pools. 

#### Registered DReps

In Voltaire, existing stake credentials will be
able to delegate their stake to DReps for voting purposes,
in addition to the current delegation to stake pools for block production.
DRep delegation will mimic the existing stake delegation mechanisms (via on-chain certificates).
Similarly, DRep registration will mimic the existing stake registration mechanisms.
Additionally, registered DReps will need to vote regularly to still be considered active.
Specifically, if a DRep does not submit any votes for `drepActivity`-many epochs, the DRep is considered inactive,
where `drepActivity` is a new protocol parameter.
Inactive DReps do not count towards the active voting stake anymore, and can become active again for
`drepActivity`-many epochs by voting on any governance actions or submitting a DRep update certificate.
The reason for marking DReps as inactive is so that DReps who stop participating but still have
stake delegated to them do not eventually leave the system in a state where no governance
action can pass.

Registered DReps are identified by a credential that can be either:

* A verification key (Ed25519)
* A native or Plutus script

The blake2b-224 hash digest of a serialized DRep credential is called the _DRep ID_.

The following new types of certificates will be added for DReps:
DRep registration certificates, DRep retirement certificates, and
vote delegation certificates.

##### DRep registration certificates

DRep registration certificates include:

* a DRep ID
* a deposit
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

Note that a DRep is retired immediately upon the chain accepting a retirement certificate,
and the deposit is returned as part of the transaction that submits the retirement certificate
(the same way that stake credential registration deposits are returned).

##### Vote delegation certificates

Vote delegation certificates include:

* the DRep ID to which the stake should be delegated
* the stake credential for the delegator

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
distribution. This distribution will determine how much stake each vote from a DRep
is backed by.

> **Warning**
>
> **Unlike** the distribution that is used for block production, we will always use the most
> current version of the per-DRep stake distribution as given on the epoch boundary.
>
> This means that **for any topic which individual voters care deeply about,
> they have time to delegate to themselves as a DRep and vote directly**.
> However, it means that there may be a difference between the stake that is used for block
> production and the stake that is used for voting in any given epoch.


#### Incentives for Ada holders to delegate voting stake

There will be a short [bootstrapping phase](#bootstrapping-phase) during which rewards will be earned
for stake delegation etc. and may be withdrawn at any time.
After this phase, although rewards will continue to be earned for block delegation etc., reward accounts will be
**blocked from withdrawing any rewards** unless their associated stake credential is also delegated to a DRep or pre-defined voting option.
This helps to ensure high participation, and so, legitimacy.

> **Note**
>
> Even though rewards cannot be withdrawn, they are not lost.  As soon as a stake credential is delegated
> (including to a pre-defined voting option), the rewards can be withdrawn.

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
- An action that fails to be ratified before its deadline is said to have **expired**.
- An action that has been ratified is said to be **enacted** once it has been activated on the network.


| Action                                                        | Description                                                                                                              |
|:--------------------------------------------------------------|:-------------------------------------------------------------------------------------------------------------------------|
| 1. Motion of no-confidence                                    | A motion to create a _state of no-confidence_ in the current constitutional committee                                    |
| 2. Update committee and/or threshold and/or terms             | Changes to the members of the constitutional committee and/or to its signature threshold and/or terms                    |
| 3. New Constitution or Guardrails Script                      | A modification to the Constitution or Guardrails Script, recorded as on-chain hashes                                       |
| 4. Hard-Fork[^2] Initiation                                   | Triggers a non-backwards compatible upgrade of the network; requires a prior software upgrade                            |
| 5. Protocol Parameter Changes                                 | Any change to **one or more** updatable protocol parameters, excluding changes to major protocol versions ("hard forks") |
| 6. Treasury Withdrawals                                       | Withdrawals from the treasury                                                                                            |
| 7. Info                                                       | An action that has no effect on-chain, other than an on-chain record                                                     |

**Any Ada holder** can submit a governance action to the chain.
They must provide a deposit of `govActionDeposit` Lovelace, which will be returned when the action is finalized
(whether it is **ratified** or has **expired**).
The deposit amount will be added to the _deposit pot_, similar to stake key deposits.
It will also be counted towards the stake of the reward address it will be paid back to, to not reduce the submitter's voting power to vote on their own (and competing) actions.

If a guardrails script is present, the transaction must include that
script in the witness set either directly, or via reference inputs,
and any other requirements that the guardrails script makes must be
satisfied.

Note that a motion of no-confidence is an extreme measure that enables Ada holders to revoke the power
that has been granted to the current constitutional committee.

> **Note**
> A **single** governance action might contain **multiple** protocol parameter updates. Many parameters are inter-connected and might require moving in lockstep.

#### Ratification

Governance actions are **ratified** through on-chain voting actions.
Different kinds of governance actions have different ratification requirements but always involve **two of the three** governance bodies,
with the exception of a hard-fork initiation and security-relevant protocol parameters, which requires ratification by all governance bodies.
Depending on the type of governance action, an action will thus be ratified when a combination of the following occurs:

* the constitutional committee approves of the action (the number of members who vote `Yes` meets the threshold of the constitutional committee)
* the DReps approve of the action (the stake controlled by the DReps who vote `Yes` meets a certain threshold of the total active voting stake)
* the SPOs approve of the action (the stake controlled by the SPOs who vote `Yes` meets a certain threshold of the total active voting stake, excepting Hard Fork Governance Actions)

> **Warning**
> As explained above, different stake distributions apply to DReps and SPOs.

A successful motion of no-confidence, update of the constitutional committee,
a constitutional change, or a hard-fork, delays
ratification of all other governance actions until the first epoch after their enactment. This gives
an updated constitutional committee enough time to vote on current proposals, re-evaluate existing proposals
with respect to a new constitution, and ensures that the in principle arbitrary semantic changes caused
by enacting a hard-fork do not have unintended consequences in combination with other actions.

##### Requirements

The following table details the ratification requirements for each governance action scenario. The columns represent:

* **Governance action type**<br/>
  The type of governance action. Note that the protocol parameter updates are grouped into four categories.

* **Constitutional committee (abbrev. CC)**<br/>
  A value of ✓ indicates that the constitutional committee must approve this action.<br/>
  A value of - means that constitutional committee votes do not apply.

* **DReps**<br/>
  The DRep vote threshold that must be met as a percentage of *active voting stake*.

* **SPOs**<br/>
  The SPO vote threshold which must be met as a certain threshold of the total active voting stake, excepting Hard Fork Governance Actions. Due to the need for robust consensus around Hard Fork initiations, these votes must be met as a percentage of the stake held by all stake pools. <br/>
  A value of - means that SPO votes do not apply.

| Governance action type                                               | CC | DReps    | SPOs     |
|:---------------------------------------------------------------------|:---|:---------|:---------|
| 1. Motion of no-confidence                                           | \- | $P_1$    | $Q_1$    |
| 2<sub>a</sub>. Update committee/threshold (_normal state_)           | \- | $P_{2a}$ | $Q_{2a}$ |
| 2<sub>b</sub>. Update committee/threshold (_state of no-confidence_) | \- | $P_{2b}$ | $Q_{2b}$ |
| 3. New Constitution or Guardrails Script                             | ✓  | $P_3$    | \-       |
| 4. Hard-fork initiation                                              | ✓  | $P_4$    | $Q_4$    |
| 5<sub>a</sub>. Protocol parameter changes, network group             | ✓  | $P_{5a}$ | \-       |
| 5<sub>b</sub>. Protocol parameter changes, economic group            | ✓  | $P_{5b}$ | \-       |
| 5<sub>c</sub>. Protocol parameter changes, technical group           | ✓  | $P_{5c}$ | \-       |
| 5<sub>d</sub>. Protocol parameter changes, governance group          | ✓  | $P_{5d}$ | \-       |
| 6. Treasury withdrawal                                               | ✓  | $P_6$    | \-       |
| 7. Info                                                              | ✓  | $100$    | $100$    |

Each of these thresholds is a governance parameter. There is one
additional threshold, `Q5`, related to security relevant protocol
parameters, which is explained below.
The initial thresholds should be chosen by the Cardano community as a whole.
All thresholds for the Info action are set to 100% since setting it any lower
would result in not being able to poll above the threshold.

Some parameters are relevant to security properties of the system. Any
proposal attempting to change such a parameter requires an additional
vote of the SPOs, with the threshold `Q5`.

The security relevant protocol parameters are:
* `maxBlockBodySize`
* `maxTxSize`
* `maxBlockHeaderSize`
* `maxValueSize`
* `maxBlockExecutionUnits`
* `txFeePerByte`
* `txFeeFixed`
* `utxoCostPerByte`
* `govActionDeposit`
* `minFeeRefScriptCostPerByte`

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
2. Update committee/threshold
3. New Constitution or Guardrails Script
4. Hard Fork initiation
5. Protocol parameter changes
6. Treasury withdrawals
7. Info

> **Note** _Info_ actions cannot be ratified or enacted, since they do not have any effect on the protocol.

##### Order of enactment

Governance actions are enacted in order of acceptance to the chain.
This resolves conflicts where, e.g. there are two competing parameter changes.

#### Lifecycle

Governance actions are checked for ratification only on an epoch boundary.
Once ratified, actions are staged for enactment.

All submitted governance actions will therefore either:

1. be **ratified**, then **enacted**
2. or **expire** after a number of epochs

In all of those cases, deposits are returned immediately.

All governance actions are enacted on the epoch boundary after their ratification.

#### Content

Every governance action will include the following:

* a deposit amount (recorded since the amount of the deposit is an updatable protocol parameter)
* a reward address to receive the deposit when it is repaid
* an anchor for any metadata that is needed to justify the action
* a hash digest value to prevent collisions with competing actions of the same type (as described earlier)

<!-- TODO: Provide a CBOR specification in the annexe for these new on-chain entities -->

In addition, each action will include some elements that are specific to its type:

| Governance action type                             | Additional data                                                                                                                                                                                 |
|:---------------------------------------------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 1. Motion of no-confidence                         | None                                                                                                                                                                                            |
| 2. Update committee/threshold                      | The set of verification key hash digests (members to be removed), a map of verification key hash digests to epoch numbers (new members and their term limit), and a fraction (new threshold)    |
| 3. New Constitution or Guardrails Script           | An anchor to the Constitution and an optional script hash of the Guardrails Script                                                                                                              |
| 4. Hard-fork initiation                            | The new (greater) major protocol version                                                                                                                                                        |
| 5. Protocol parameters changes                     | The changed parameters                                                                                                                                                                          |
| 6. Treasury withdrawal                             | A map from stake credentials to a positive number of Lovelace                                                                                                                                   |
| 7. Info                                            | None                                                                                                                                                                                            |

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
* maximum block body size (`maxBlockBodySize`)
* maximum transaction size (`maxTxSize`)
* maximum block header size (`maxBlockHeaderSize`)
* maximum size of a serialized asset value (`maxValueSize`)
* maximum script execution units in a single transaction (`maxTxExecutionUnits`)
* maximum script execution units in a single block (`maxBlockExecutionUnits`)
* maximum number of collateral inputs (`maxCollateralInputs`)

The **economic group** consists of:
* minimum fee coefficient (`txFeePerByte`)
* minimum fee constant (`txFeeFixed`)
* delegation key Lovelace deposit (`stakeAddressDeposit`)
* pool registration Lovelace deposit (`stakePoolDeposit`)
* monetary expansion (`monetaryExpansion`)
* treasury expansion (`treasuryCut`)
* minimum fixed rewards cut for pools (`minPoolCost`)
* minimum Lovelace deposit per byte of serialized UTxO (`utxoCostPerByte`)
* prices of Plutus execution units (`executionUnitPrices`)

The **technical group** consists of:
* pool pledge influence (`poolPledgeInfluence`)
* pool retirement maximum epoch (`poolRetireMaxEpoch`)
* desired number of pools (`stakePoolTargetNum`)
* Plutus execution cost models (`costModels`)
* proportion of collateral needed for scripts (`collateralPercentage`)

The **governance group** consists of all the new protocol parameters that are introduced in this CIP:
* governance voting thresholds ($P_1$, $P_{2a}$, $P_{2b}$, $P_3$, $P_4$, $P_{5a}$, $P_{5b}$, $P_{5c}$, $P_{5d}$, $P_6$, $Q_1$, $Q_{2a}$, $Q_{2b}$, $Q_4$, $Q_5$)
* governance action maximum lifetime in epochs (`govActionLifetime`)
* governance action deposit (`govActionDeposit`)
* DRep deposit amount (`dRepDeposit`)
* DRep activity period in epochs (`dRepActivity`)
* minimal constitutional committee size (`committeeMinSize`)
* maximum term length (in epochs) for the constitutional committee members (`committeeMaxTermLength`)

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

> **Warning** 'Abstain' votes are not included in the "active voting stake".
>
> Note that an explicit vote to abstain differs from abstaining from voting.
> Unregistered stake that did not vote behaves like an 'Abstain' vote,
> while registered stake that did not vote behaves like a 'No' vote.
> To avoid confusion, we will only use the word 'Abstain' from this point onward to mean an on-chain vote to abstain.

The governance credential witness will trigger the appropriate verifications in the ledger according to the existing `UTxOW` ledger rule
(i.e. a signature check for verification keys, and a validator execution with a specific vote redeemer and new Plutus script purpose for scripts).

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
  * The registered stake credential has delegated its voting rights to a DRep.
* Relative to some percentage `P`, a DRep (SPO) **vote threshold has been met** if the sum of the relative stake that has been delegated to the DReps (SPOs)
  that vote `Yes` to a governance action
  is at least `P`.

## Rationale: how does this CIP achieve its goals?

+ [Role of the constitutional committee](#role-of-the-constitutional-committee)
+ [Intentional omission of identity verification](#intentional-omission-of-identity-verification)
+ [Reducing the power of entities with large amounts of Ada](#reducing-the-power-of-entities-with-large-amounts-of-ada)
+ [Piggybacking on stake pool stake distribution](#piggybacking-on-stake-pool-stake-distribution)
+ [Separation of hard-fork initiation from standard protocol parameter changes](#separation-of-hard-fork-initiation-from-standard-protocol-parameter-changes)
+ [The purpose of the DReps](#the-purpose-of-the-dreps)
+ [Ratification requirements table](#ratification-requirements-table)
+ [Motion of no-confidence](#motion-of-no-confidence)
+ [Update committee/threshold (state of no-confidence)](#update-committeethreshold-state-of-no-confidence)
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
* Update committee/threshold (normal state)
* New Constitution
* Protocol parameter changes
* Treasury withdrawal

### Motion of no-confidence

A motion of no-confidence represents a lack of confidence by the Cardano community in the
current constitutional committee, and hence the constitutional committee should not
be included in this type of governance action.
In this situation, the SPOs and the DReps are left to represent the will of the community.

### Update committee/threshold (state of no-confidence)

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

The governance actions, the votes and the certificates and the Constitution use new metadata fields,
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

### Changelog

#### Changes post Longmont workshop (March 2023)

* Thank the workshop attendees.
* We have added Constitutional Committee terms.
* Two new "pre-defined" voting options: abstain and no confidence.
* New "Info" governance action.
* Use the most recent DRep stake distribution for ratification.
  This means that if ever your DRep votes how you do not like,
  you can immediately make yourself a DRep and vote how you want.
* Escrow some ADA from the current treasury for potential future DRep
  incentives.
* Remove the tiered treasury actions in favor of something adaptive
  (so the "yes" threshold would depend on:
    1) how much ada,
    2) how high the registered voting stake, and maybe
    3) how much ada is released every epoch
* Split the protocol parameter updates into four groups:
  network, economic, technical, and governmental.
* Most governance actions can be enacted (upon ratification)
  right away. All but: protocol parameters and hard forks.
* Remove "one action per type per epoch" restriction in favor of
  tracking the last action ID of each type, and including this in
  the action.
* No AVST.
* Bootstrap phase: Until X% of ADA is registered to vote or Y epochs
  have elapsed, only parameter changes and hard forks can happen.
  PP changes just need CC threshold, HFs need CC and SPOs.
  After the bootstrap phase, we put in place the incentive to keep low
  DReps, but this mechanism **automatically** relaxes.
* New plutus script purpose for DReps.
* Multiple treasury withdrawals in one epoch.
* A section on the recursive problem of "how do we ratify this CIP".
* Changes to the local state-query protocol.
* New ideas, time permitting:
  * Weigh SPO stake vote by pledge somehow.
  * DReps can specify which other DRep gets their delegators
    in the event that they retire.
  * Reduced government action deposit if one member of the CC signs off
    on it (which presumably means it has gone through some process).
  * Include hash of (future) genesis configuration within HF proposal.

#### Changes post Edinburgh workshop (July 2023)

* Add guardrails script, which can control what treasury withdrawals and
  protocol parameter changes are allowed.
* Remove dropping of governance actions. The only effect this has is
  that in case a no confidence action passes, actions stay
  around. However, only new committee proposals that have been
  designed to build on top of that no confidence action can be
  enacted. If a new committee gets elected while some of those actions
  haven't expired, those actions can be ratified but the new committee
  has to approve them.
* All governance actions are enacted one epoch after they are ratified.
* Move post-bootstrapping restrictions into 'Other Ideas'.
* Add a section on different deposit amounts to 'Other Ideas'.
* Add a section for a minimum AVS to 'Other Ideas'.
* Rename some protocol parameters.
* Rename `TALLY` to `GOV`.
* Turn the Constitution into an anchor.
* Rework which anchors are required and which are optional.
* Clean up various inconsistencies and leftovers from older versions.

#### Security-relevant changes and other fixes (January 2024)

* Guard security-relevant changes behind SPO votes.
* The system does not enter a state of no confidence with insufficient
  active CC members, the CC just becomes unable to act.
* Clarify that CC members can use any kind of credential.

#### May 2024

* Update the section on the bootstrap period.
* Mention missing `Q_5` parameter.
* Various small fixes/consistency changes.

## Path to Active

### Acceptance Criteria

- [x] A new ledger era is enabled on the Cardano mainnet, which implements the above specification.
 - Bootstrapping phase governance via Chang #1 hardfork
 - Full governance via Plomin hardfork

### Implementation Plan

The features in this CIP require a hard fork.

This document describes an ambitious change to Cardano governance.
We propose to implement the changes via two hard forks: the first
one containing all new features but some being disabled for a bootstrap period
and the second one enabling all features.

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

- [x] Gather opinions from community-held workshops, akin to the Colorado workshop of February-March 2023.
- [ ] Exercise voting actions on a public testnet, with sufficient participation.
- [ ] Poll the established SPOs.
- [ ] Leverage Project Catalyst to gather inputs from the existing voting community (albeit small in terms of active stake).

#### Changes to the transaction body

- [x] New elements will be added to the transaction body, and existing update and MIR capabilities will be removed. In particular,

  The governance actions and votes will comprise two new transaction body fields.

- [x] Three new kinds of certificates will be added in addition to the existing ones:

  * DRep registration
  * DRep de-registration
  * Vote delegation

  And similarly, the current MIR and genesis certificates will be removed.

- [x] A new `Voting` purpose will be added to Plutus script contexts.
  This will provide, in particular, the vote to on-chain scripts.

> **Warning** As usual, we will provide a CDDL specification for each of those changes.

#### Changes to the existing ledger rules

* The `PPUP` transition rule will be rewritten and moved out of the `UTxO` rule and into the `LEDGER` rule as a new `GOV` rule.

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
Thirdly, info actions will be available.
No other actions other than those mentioned in this paragraph are possible during the bootstrap phase.

The bootstrap phase ends when the Constitutional Committee and SPOs
ratify a subsequent hard fork, enabling the remaining governance
actions and DRep participation.
This is likely to be a number of months after the Chang hard fork.
Although all features will be technically available at this point, additional
requirements for using each feature may be specified in the constitution.

Moreover, there will be an interim Constitutional committee with a set term,
also specified in the next ledger era configuration file.
The rotational schedule of the first non-interim committee could be included in the constitution itself.
Note, however, that since the constitutional committee never votes on new committees,
it cannot actually enforce the rotation.

#### Other Ideas / Open Questions

##### Pledge-weighted SPO voting

The SPO vote could additionally be weighted by each SPO's pledge.
This would provide a mechanism for allowing those with literal stake in the game to have a stronger vote.
The weighting should be carefully chosen.

##### Automatic re-delegation of DReps

A DRep could optionally list another DRep credential in their registration certificate.
Upon retirement, all of the DRep's delegations would be automatically transferred to the
given DRep credential.  If that DRep had already retired, the delegation would be transfer
to the 'Abstain' voting option.

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

##### Different deposit amounts for different governance actions

Multiple workshops for this CIP have proposed to introduce a different
deposit amount for each type of governance action. It was not clear
whether a majority was in favor of this idea, but this may be
considered if it becomes clear that it is necessary.

##### Minimum active voting stake

As a further guarantee to ensure governance actions cannot be proposed
right before a hard fork, be voted on by one DRep with a large amount
of stake and be enacted immediately, there could be an additional
requirement that a certain fixed absolute amount of stake needs to
cast a 'Yes' vote on the action to be enacted.

This does not seem necessary in the current design, since the stake of
all registered DReps behaves like a 'No' vote until they have actually
cast a vote. This means that for this scenario to occur, the malicious
actor needs at least to be in control of the fraction of DRep stake
corresponding to the relevant threshold, at which point this might as
well be considered a legitimate action.

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
Similarly, some people have expressed confusion between the state of no-confidence, the motion of no-confidence and the no-confidence voting option.

We could imagine finding better terms for these concepts.

##### Rate-limiting treasury movements

Nothing prevents money being taken out of the treasury other than the proposed votes and voting thresholds. Given that the Cardano treasury is a quite fundamental component of its monetary policy, we could imagine enforcing (at the protocol level) the maximum amount that can removed from the treasury over any period of time.

##### Final safety measure, post bootstrapping

Many people have stated that they believe that the actual voting turnout will not be so large
as to be a strain on the throughput of the system.
We also believe that this is likely to be the case, but when the bootstrap phase ends we might
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

## Acknowledgements

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

<details>
  <summary><strong>2023 Mexico City, Mexico Workshop (20/05)</strong></summary>

In addition, we would like to thank all the attendees of the workshop that was held in Mexico City, Mexico on May 20th 2023 for their valuable contributions
to this CIP, and for their active championing of Cardano's vision for minimal viable governance.  These include:

* Donovan Riaño
* Cristian Jair Rojas
* Victor Hernández
* Ramón Aceves
* Sergio Andrés Cortés
* Isaías Alejandro Galván
* Abigail Guzmán
* Jorge Fernando Murguía
* Luis Guillermo Santana

</details>

<details>
  <summary><strong>2023 Buenos Aires, Argentina Workshop (20/05)</strong></summary>

In addition, we would like to thank all the attendees of the workshop that was held in Buenos Aires, Argentina on May 20th 2023 for their valuable contributions
to this CIP, and for their active championing of Cardano's vision for minimal viable governance.  These include:

* Lucas Macchiavelli
* Alejando Pestchanker
* Juan Manuel Castro Pippo
* Federico Weill
* Jose Otegui
* Mercedes Ruggeri
* Mauro Andreoli
* Elias Aires
* Jorge Nasanovsky
* Ulises Barreiro
* Martin Ochoa
* Facundo Lopez
* Vanina Estrugo
* Luca Pestchanker
</details>

<details>
  <summary><strong>2023 Johannesburg, South Africa Workshop (25/05)</strong></summary>

In addition, we would like to thank all the attendees of the workshop that was held in Johannesburg, South Africa on May 25th 2023 for their valuable contributions to this CIP, and for their active championing of Cardano's vision for minimal viable governance.  These include:

* Celiwe Ngwenya
* Bernard Sibanda
* Dumo Mbobo
* Shaolyn Dzwedere
* Kunoshe Muchemwa
* Siphiwe Mbobo
* Lucas Sibindi
* DayTapoya
* Mdu Ngwenya
* Lucky Khumalo
* Skhangele Malinga
* Joyce Ncube
* Costa Katenhe
* Bramwell Kasanga
* Precious Abimbola
* Ethel Q Tshuma
* Panashe Sibanda
* Radebe Tefo
* Kaelo Lentsoe
* Richmond Oppong
* Israel Ncube
* Sikhangele Malinga
* Nana Safo
* Ndaba Delsie
* Collen Tshepang
* Dzvedere Shaolyn
* Thandazile Sibanda
* Ncube Joyce
* Lucas Sibindi
* Pinky Ferro
* Ishmael Ntuta
* Khumalo Lucky
* Fhulufelo
* Thwasile Ngwenya
* Kunashe Muchemwa
* Dube Bekezela
* Tinyiko Baloi
* Dada Nomathemba
</details>


<details>
  <summary><strong>2023 Bogota, Colombia Workshop (27/05)</strong></summary>

In addition, we would like to thank all the attendees of the workshop that was held in Bogota, Colombia on May 27th 2023 for their valuable contributions
to this CIP, and for their active championing of Cardano's vision for minimal viable governance.  These include:

* Alvaro Moncada
* Jaime Andres Posada Castro
* Jose Miguel De Gamboa
* Nicolas Gomez
* Luis Restrepo (Moxie)
* Juanita Jaramillo R.
* Daniel Vanegas
* Ernesto Rafael Pabon Moreno
* Carlos Eduardo Escobar
* Manuel Fernando Briceño
* Sebastian Pabon
</details>

<details>
  <summary><strong>2023 Caracas, Venezuela Workshop (27/05)</strong></summary>

In addition, we would like to thank all the attendees of the workshop that was held in Caracas, Venezuela on May 27th 2023 for their valuable contributions
to this CIP, and for their active championing of Cardano's vision for minimal viable governance.  These include:

* Jean Carlo Aguilar
* Wilmer Varón
* José Erasmo Colmenares
* David Jaén
* Félix Dávila
* Yaneth Duarte
* Nando Vitti
* Wilmer Rojas
* Andreina García
* Carmen Galban
* Osmarlina Agüero
* Ender Linares
* Carlos A. Palacios R
* Dewar Rodríguez
* Lennys Blanco
* Francys García
* Davidson Arenas
</details>

<details>
  <summary><strong>2023 Manizales, Colombia Workshop (27/05)</strong></summary>

In addition, we would like to thank all the attendees of the workshop that was held in Manizales, Colombia on May 27th 2023 for their valuable contributions
to this CIP, and for their active championing of Cardano's vision for minimal viable governance.  These include:

* Yaris Cruz
* Yaneth Duarte
* Ciro Gelvez
* Kevin Chacon
* Juan Sierra
* Caue Chianca
* Sonia Malagon
* Facundo Ramirez
* Hope R.
</details>

<details>
  <summary><strong>2023 Addis Ababa, Ethiopia Workshop (27/05 & 28/5)</strong></summary>

In addition, we would like to thank all the attendees of the workshop that was held in Addis Ababa, Ethiopia on May 27th and 28th 2023 for their valuable contributions
to this CIP, and for their active championing of Cardano's vision for minimal viable governance.  These include:

* Kaleb Dori
* Eyassu Birru
* Matthew Thornton
* Tamir Kifle
* Kirubel Tabu
* Bisrat Miherete
* Emmanuel Khatchadourian
* Tinsae Teka
* Yoseph Ephrem
* Yonas Eshetu
* Hanna Kaleab
* Tinsae Teka
* Robee Meseret
* Matias Tekeste
* Eyasu Birhanu
* yonatan berihun
* Nasrallah Hassan
* Andinet Assefa
* Tewodros Sintayehu
* KIDUS MENGISTEAB
* Djibril Konate
* Nahom Mekonnen
* Eyasu Birhanu
* Eyob Aschenaki
* Tinsae Demissie
* Yeabsira Tsegaye
* Tihitna Miroche
* Mearaf Tadewos
* Yab Mitiku
* Habtamu Asefa
* Dawit Mengistu
* Nebiyu Barsula
* Nebiyu Sultan
* Nathan Samson
</details>

<details>
  <summary><strong>2023 Kyoto and Fukuoka, Japan Workshop (27/05 & 10/06 )</strong></summary>

In addition, we would like to thank all the attendees of the workshop that was held in Kyoto and Fukuoka, Japan on May 27th and June 10th 2023 for their valuable contributions to this CIP, and for their active championing of Cardano's vision for minimal viable governance.  These include:

* Arimura
* Hidemi
* Nagamaru(SASApool)
* shiodome47(SODMpool)
* Wakuda(AID1pool)
* Yuta(Yuki Oishi)
* Andrew
* BANCpool
* Miyatake
* Muen
* Riekousagi
* SMAN8(SA8pool)
* Tatsuya
* カッシー
* 松
* ポンタ
* リサ
* Mako
* Ririco
* ながまる
* Baku
* マリア
* たりふん
* JUNO
* Kinoko
* Chikara
* ET
* Akira555
* Kent
* Ppp
* Shiodome47
* Sam
* ポール
* Concon
* Sogame
* ハンド
* Demi
* Nonnon
* banC
* SMAN8(SA8pool)
* りんむ
* Kensin
* りえこうさぎ
* アダマンタイト
* の/ゆすけ
* MUEN
* いちごだいふく
* Ranket
* A.yy
* N S
* Kazuya
* Daikon
</details>

<details>
  <summary><strong>2023 Monterey, California Workshop (28/05)</strong></summary>

In addition, we would like to thank all the attendees of the workshop that was held in Monterey, California on May 28th 2023 for their valuable contributions to this CIP, and for their active championing of Cardano's vision for minimal viable governance.  These include:

* Shane Powser
* Rodrigo Gomez
* Adam K. Dean
* John C. Valdez
* Kyle Solomon
* Erick "Mag" Magnana
* Bryant Austin
* John Huthmaker
* Ayori Selassie
* Josh Noriega
* Matthias Sieber
</details>

<details>
  <summary><strong>2023 Tlaxcala, Mexico Workshop (01/06)</strong></summary>

In addition, we would like to thank all the attendees of the workshop that was held in Tlaxcala, Mexico on June 1st 2023 for their valuable contributions to this CIP, and for their active championing of Cardano's vision for minimal viable governance.  These include:

* Victor Hernández
* Cristian Jair Rojas
* Miriam Mejia
* Josmar Cabañas
* Lizbet Delgado
* José Alberto Sánchez
* Fátima Valeria Zamora
* Julio César Montiel
* Jesús Pérez
* José Adrián López
* Lizbeth Calderón
* Zayra Molina
* Nayelhi Pérez
* Josué Armas
* Diego Talavera
* Darían Gutiérrez
</details>

<details>
  <summary><strong>2023 LATAM Virtual Workshop (03/06)</strong></summary>

In addition, we would like to thank all the attendees of the workshop that was held in LATAM Virtual on June 3rd 2023 for their valuable contributions to this CIP, and for their active championing of Cardano's vision for minimal viable governance.  These include:

* Juan Sierra
* @CaueChianca
* Ernesto Rafael
* Pabon Moreno
* Sonia Malagon
* Facundo Ramírez
* Mercedes Ruggeri
* Hope R.
* Yaris Cruz
* Yaneth Duarte
* Ciro Gélvez
* Kevin Chacon
* Juanita Jaramillo
* Sebastian Pabon
</details>

<details>
  <summary><strong>2023 Worcester, Massachusetts Workshop (08/06)</strong></summary>

In addition, we would like to thank all the attendees of the workshop that was held in Worcester, Massachusetts on June 8th 2023 for their valuable contributions to this CIP, and for their active championing of Cardano's vision for minimal viable governance.  These include:

* CardanoSharp
* Kenric Nelson
* Matthias Sieber
* Roberto Mayen
* Ian Burzynski
* omdesign
* Chris Gianelloni
</details>

<details>
  <summary><strong>2023 Chicago, Illinois Workshop (10/06)</strong></summary>

In addition, we would like to thank all the attendees of the workshop that was held in Chicago, Illinois on June 10th 2023 for their valuable contributions to this CIP, and for their active championing of Cardano's vision for minimal viable governance.  These include:

* Adam Rusch
* Jose Martinez
* Michael McNulty
* Vanessa Villanueva Collao
* Maaz Jedh
</details>

<details>
  <summary><strong>2023 Virtual Workshop (12/06)</strong></summary>

In addition, we would like to thank all the attendees of the workshop that was held virtually on June 12th 2023 for their valuable contributions to this CIP, and for their active championing of Cardano's vision for minimal viable governance.  These include:

* Rojo Kaboti
* Tommy Frey
* Tevo Saks
* Slate
* UBIO OBU
</details>

<details>
  <summary><strong>2023 Toronto, Canada Workshop (15/06)</strong></summary>

In addition, we would like to thank all the attendees of the workshop that was held in Toronto, Canada on June 15th 2023 for their valuable contributions to this CIP, and for their active championing of Cardano's vision for minimal viable governance.  These include:

* John MacPherson
* Lawrence Ley
</details>

<details>
  <summary><strong>2023 Philadelphia, Pennsylvania Workshop (17/06)</strong></summary>

In addition, we would like to thank all the attendees of the workshop that was held in Philadelphia, Pennsylvania on June 17th 2023 for their valuable contributions to this CIP, and for their active championing of Cardano's vision for minimal viable governance.  These include:

* NOODZ
* Jarhead
* Jenny Brito
* Shepard
* BONE Pool
* type_biggie
* FLAWWD
* A.I. Scholars
* Eddie
* Joker
* Lex
* Jerome
* Joey
* SwayZ
* Cara Mia
* PHILLY 1694
</details>

<details>
  <summary><strong>2023 Santiago de Chile Workshop (17/06)</strong></summary>

In addition, we would like to thank all the attendees of the workshop that was held in Santiago de Chile on June 17th 2023 for their valuable contributions
to this CIP, and for their active championing of Cardano's vision for minimal viable governance.  These include:

* Rodrigo Oyarsun
* Sebastián Aravena
* Musashi Fujio
* Geo Gavo
* Lucía Escobar
* Juan Cruz Franco
* Natalia Rosa
* Cristian M. García
* Alejandro Montalvo
</details>

<details>
  <summary><strong>2023 Virtual Workshop (17/06)</strong></summary>

In addition, we would like to thank all the attendees of the workshop that was held virtually on June 17th 2023 for their valuable contributions
to this CIP, and for their active championing of Cardano's vision for minimal viable governance.  These include:

* Juana Attieh
* Nadim Karam
* Amir Azem
* Rami Hanania
* LALUL Stake Pool
* HAWAK Stake Pool
</details>

<details>
  <summary><strong>2023 Taipai, Taiwan Workshop (18/06)</strong></summary>

In addition, we would like to thank all the attendees of the workshop that was held in Taipai, Taiwan on June 18th 2023 for their valuable contributions
to this CIP, and for their active championing of Cardano's vision for minimal viable governance.  These include:

* Michael Rogero
* Ted Chen
* Mic
* Jeremy Firster 
* Eric Tsai
* Dylan Chiang
* JohnsonCai
* DavidCHIEN
* Zach Gu
* Jimmy WANG
* JackTsai
* Katherine Hung
* Will Huang
* Kwicil
</details>

<details>
  <summary><strong>2023 Midgard Vikingcenter Horten, Norway Workshop (19/06)</strong></summary>

In addition, we would like to thank all the attendees of the workshop that was held in Midgard Vikingcenter Horten, Norway on June 19th 2023 for their valuable contributions
to this CIP, and for their active championing of Cardano's vision for minimal viable governance.  These include:

* Daniel D. Johnsen
* Thomas Lindseth
* Eystein Hansen
* Gudbrand Tokerud 
* Lally McClay
* $trym
* Arne Rasmussen
* Lise WesselTVVIN
* Bjarne 
* Jostein Aanderaa
* Ken-Erik Ølmheim
* DimSum
</details>

<details>
  <summary><strong>2023 Virtual Workshop (19/06)</strong></summary>

In addition, we would like to thank all the attendees of the workshop that was held virtually on June 19th 2023 for their valuable contributions
to this CIP, and for their active championing of Cardano's vision for minimal viable governance.  These include:

* Nicolas Cerny
* Nils Peuser
* Riley Kilgore
* Alejandro Almanza
* Jenny Brito
* John C. Valdez
* Rhys
* Thyme
* Adam Rusch
* Devryn
</details>

<details>
  <summary><strong>2023 New York City, New York Workshop (20/06)</strong></summary>

In addition, we would like to thank all the attendees of the workshop that was held in New York City, New York on June 20th 2023 for their valuable contributions
to this CIP, and for their active championing of Cardano's vision for minimal viable governance.  These include:

* John Shearing
* Geoff Shearing
* Daniela Balaniuc
* SDuffy
* Garry Golden
* Newman
* Emmanuel Batse
* Ebae
* Mojira
</details>

<details>
  <summary><strong>2023 La Cumbre, Argentina Workshop (23/06)</strong></summary>

In addition, we would like to thank all the attendees of the workshop that was held in La Cumbre, Argentina on June 23rd 2023 for their valuable contributions
to this CIP, and for their active championing of Cardano's vision for minimal viable governance.  These include:

* Ulises Barreiro
* Daniel F. Rodriguez
* Dominique Gromez
* Leandro Chialvo
* Claudia Vogel
* Guillermo Lucero
* Funes, Brian Carrasco
* Melisa Carrasco
* Carlos Carrasco
</details>

<details>
  <summary><strong>2023 Minneapolis, Minnesota Workshop (23/06)</strong></summary>

In addition, we would like to thank all the attendees of the workshop that was held in Minneapolis, Minnesota on June 23rd 2023 for their valuable contributions to this CIP, and for their active championing of Cardano's vision for minimal viable governance.  These include:

* Stephanie King
* Darlington Wleh
</details>

<details>
  <summary><strong>2023 La Plata, Argentina Workshop (23/06)</strong></summary>

In addition, we would like to thank all the attendees of the workshop that was held in La Plata, Argentina on June 23rd 2023 for their valuable contributions
to this CIP, and for their active championing of Cardano's vision for minimal viable governance.  These include:

* Mauro Andreoli
* Rodolfo Miranda
* Agustin Francella
* Federico Sting
* Elias Aires
* Lucas Macchiavelli
* Pablo Hernán Mazzitelli
</details>

<details>
  <summary><strong>2023 Puerto Madryn, Argentina Workshop (23/06)</strong></summary>

In addition, we would like to thank all the attendees of the workshop that was held in Puerto Madryn, Argentina on June 23rd 2023 for their valuable contributions to this CIP, and for their active championing of Cardano's vision for minimal viable governance.  These include:

* Andres Torres Borda
* Federico Ledesma Calatayud
* Maximiliano Torres
* Federico Prado
* Domingo Torres
* Floriana Pérez Barria
* Martin Real
* Florencia García
* Roberto Neme
</details>

<details>
  <summary><strong>2023 Accra, Ghana Workshop (24/06)</strong></summary>

In addition, we would like to thank all the attendees of the workshop that was held in Accra, Ghana on June 24th 2023 for their valuable contributions to this CIP, and for their active championing of Cardano's vision for minimal viable governance.  These include:

* Wada
* Laurentine
* Christopher A.
* Nathaniel D.
* Edufua
* Michael
* Augusta
* Jeremiah
* Boaz
* Mohammed
* Richmond O.
* Ezekiel
* Megan
* Josue
* Michel T.
* Bineta
* Afia O.
* Mercy
* Enoch
* Kofi
* Awura
* Emelia
* Richmond S.
* Solomon
* Phillip
* Faakor
* Manfo
* Josh
* Daniel
* Mermose
</details>

<details>
  <summary><strong>2023 Virtual Workshop (24/06)</strong></summary>

In addition, we would like to thank all the attendees of the workshop that was held virtually on June 24th 2023 for their valuable contributions to this CIP, and for their active championing of Cardano's vision for minimal viable governance.  These include:

* Jonas Riise
* Thomas Lindseth
* André "Eilert" Eilertsen
* Eystein Hansen
</details>

<details>
  <summary><strong>2023 Seoul, South Korea Workshop (24/06)</strong></summary>

In addition, we would like to thank all the attendees of the workshop that was held in Seoul, South Korea on June 24th 2023 for their valuable contributions to this CIP, and for their active championing of Cardano's vision for minimal viable governance.  These include:

* Oscar Hong (JUNGI HONG)
* SPO_COOL (Kevin Kordano)
* SPO_KTOP (KT OH)
* WANG JAE LEE
* JAE HYUN AN
* INYOUNG MOON (Penny)
* HOJIN JEON
* SEUNG KYU BAEK
* SA SEONG MAENG
* JUNG MYEONG HAN
* BRIAN KIM
* JUNG HOON KIM
* SEUNG WOOK JUNG (Peter)
* HYUNG WOO PARK
* EUN JAE CHOI
* NA GYEONG KIM
* JADEN CHOI
</details>

<details>
  <summary><strong>2023 Abu Dhabi, UAE Workshop (25/06)</strong></summary>

In addition, we would like to thank all the attendees of the workshop that was held in Abu Dhabi, UAE on June 25th 2023 for their valuable contributions to this CIP, and for their active championing of Cardano's vision for minimal viable governance.  These include:

* Amir Azem
* Ian Arden
* Madina Abdibayeva
* BTBF (Yu Kagaya)
* محمد الظاهري
* Tegegne Tefera
* Rami Hanania
* Tania Debs
* Khalil Jad
* Mohamed Jamal
* Ruslan Yakubov
* OUSHEK Mohamed eisa
* Shehryar
* Wael Ben Younes
* Santosh Ray
* Juana Attieh
* Nadim Karam
* DubaistakePool
* HAWAK Pool
* LALKUL Stake Pools
</details>

<details>
  <summary><strong>2023 Williamsburg, New York Workshop (25/06)</strong></summary>

In addition, we would like to thank all the attendees of the workshop that was held in Williamsburg, New York on June 25th 2023 for their valuable contributions to this CIP, and for their active championing of Cardano's vision for minimal viable governance.  These include:

* Pi
* Joseph
* Skyler
* Forrest
* Gabriel
* Newman
</details>

<details>
  <summary><strong>2023 Lagos, Nigeria Workshop (28/06)</strong></summary>

In addition, we would like to thank all the attendees of the workshop that was held in Lagos, Nigeria on June 28th 2023 for their valuable contributions to this CIP, and for their active championing of Cardano's vision for minimal viable governance.  These include:

* Jonah Benson
* Augusta
* Ubio Obu
* Olumide Hrosuosegbe
* Veralyn Chinenye
* Ona Ohimer
* William Ese
* Ruth Usoro
* William P
* Esther Simi
* Daniel Effiom
* Akinkurai Toluwalase
</details>

<details>
  <summary><strong>2023 Sao Paulo, Brazil Workshop (01/07)</strong></summary>

In addition, we would like to thank all the attendees of the workshop that was held in Sao Paulo, Brazil on July 1st 2023 for their valuable contributions to this CIP, and for their active championing of Cardano's vision for minimal viable governance.  These include:

* Otávio Lima
* Rodrigo Pacini
* Maria Carmo
* Cauê Chianca
* Daniela Alves
* Jose Lins Dias
* Felipe Barcelos
* Rosana Melo
* Johnny Oliveira
* Lucas Ravacci
* Cristofer Ramos
* Weslei Menck
* Leandro Tsutsumi
* Izaias Pessoa
* Gabriel Melo
* Yuri Nabeshima
* Alexandre Fernandes
* Vinicius Ferreiro
* Lucas Fernandes
* Alessandro Benicio
* Mario Cielho
* Lory Fernandes Lima
* Larissa Nogueira
* Latam Cardano Community
</details>

<details>
  <summary><strong>2023 Brazil Virtual Workshop (04/07)</strong></summary>

In addition, we would like to thank all the attendees of the workshop that was held in Brazil on July 4th 2023 for their valuable contributions
to this CIP, and for their active championing of Cardano's vision for minimal viable governance.  These include:

* Lincon Vidal
* Thiago da Silva Nunes
* Rodrigo Pacini
* Livia Corcino de Albuquerque
* Cauê Chianca
* Otávio Lima
</details>

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode)

[^1]: A formal description of the current rules for governance actions is given in the [Shelley ledger specification](https://github.com/input-output-hk/cardano-ledger/releases/latest/download/shelley-ledger.pdf).

    - For protocol parameter changes (including hard forks), the `PPUP` transition rule (Figure 13) describes how protocol parameter updates are processed, and the `NEWPP` transition rule (Figure 43) describes how changes to protocol parameters are enacted.

    - For funds transfers, the `DELEG` transition rule (Figure 24) describes how MIR certificates are processed, and the `MIR` transition rule (Figure 55) describes how treasury and reserve movements are enacted.

    > **Note**
    > The capabilities of the `MIR` transition rule were expanded in the [Alonzo ledger specification](https://github.com/input-output-hk/cardano-ledger/releases/latest/download/alonzo-ledger.pdf)


[^2]: There are many varying definitions of the term "hard fork" in the blockchain industry. Hard forks typically refer to non-backwards compatible updates of a network. In Cardano, we formalize the definition slightly more by calling any upgrade that would lead to _more blocks_ being validated a "hard fork" and force nodes to comply with the new protocol version, effectively obsoleting nodes that are unable to handle the upgrade.

[^3]: This is the definition used in "active stake" for stake delegation to stake pools, see Section 17.1, Total stake calculation, of the [Shelley ledger specification](https://github.com/input-output-hk/cardano-ledger/releases/latest/download/shelley-ledger.pdf).
