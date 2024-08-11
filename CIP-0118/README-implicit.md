---
CIP: 118
Title: Validation Zones - Implicit Value Flow
Category: Ledger
Status: Proposed
Authors:
    - Polina Vinogradova <polina.vinogradova@iohk.io>
    - Michael Peyton Jones <michael.peyton-jones@iohk.io>    
    - Will Gould <will.gould@iohk.io>
Implementors: []
Discussions:
    - https://github.com/cardano-foundation/CIPs/pull/780
    - https://github.com/cardano-foundation/CIPs/pull/862
Created: 2024-03-11
License: CC-BY-4.0
---

## Abstract

We propose a set of changes that revolve around validation zones, a construct for allowing
certain kinds of _underspecified transactions_. In particular, for the Babel-fees usecase
we discuss here, we allow transactions that specify
_part of a swap request_. A validation zone is a list of transactions such that
earlier transactions in the list may be underspecified, while later transactions must
complete all partial specifications. In the Babel-fees usecase, transactions do not 
need to be balanced, i.e they do not require specifying where any missing funds come from, 
or any extra funds go. A complete valid zone, however, must be balanced,
with transactions providing all missing funds for other transactions in the zone, and 
directing all "extra" funds to outputs/fees/etc.

## Motivation: why is this CIP necessary?

This CIP provides a partial solution to the problems described in CPS-15.
In particular, it describes some ledger changes that allow intent settlement
of intents that require “counterparty irrelevance”, including many of the swap use cases
and dApp fee sponsorship. The motivation behind designing this solution is _Babel fees_,
which is a requirement to support "paying transaction fees in a non-Ada currency".
The Babel-fees usecase is a special case of a swap. Supporting swaps is very desirable functionality for cryptocurrency
ledgers.

Some of the primary contenders for implementing swaps
are two-way off-chain communication (co-signing a single swapping transaction),
smart contracts implementing DEX functionality, or ledger changes implementing
an on-chain order matching DEX. We argue that our solution is the most versatile,
least expensive for users, and maintains formal guarantees
of the current Cardano ledger, among other benefits.

We discuss additional possible solutions to problems outlined
in CPS-15 that could make use of much of the same validation zones infrastructure,
but with varying kinds of underspecified transactions.


## Specification


### Validation zones

A validation zone is a list of transactions. This structure replaces singleton transactions
as a unit of validation. Specifically, instead of singleton transactions,
validation zones are

- sent across the Cardano network
- entered into a mempool, and
- placed in block bodies.  

When validating a zone (i.e. for placement in the mempool or when validating an
incoming block), each transaction is checked against the current ledger
state, however, additional checks
are done at the zone level.

#### Missing and extra assets 

For a given transaction, let `produced` and `consumed` be the produced and consumed 
values, respectively. Then

extra assets/currency `:= { aid ↦ v | aid ↦ v ∈ consumed - produced , v > 0 }`

missing assets/currency `:= { aid ↦ v | aid ↦ v ∈ produced - consumed , v > 0 }`

### Transaction structure changes

The structure of transactions has three new fields in `TxBody` : 

1. `missing : Value`, which is a field computed at the time of deserialization, and is set to 
missing assets/currency (defined above).
2. `extra : Value`, which is a field computed at the time of deserialization, and is set to 
extra assets/currency (defined above).
3. `requiredTxs : TxId ↦ B`, which contains all the IDs of the transactions that have to be included 
in the zone, associated to a boolean value that specifies whether the full `TxInfo` value for the 
transaction with a given `txId` is exposed to Plutus scripts that are executed as part of validating 
that transaction 

The field `requiredFullTxBodies : Tx` is included in `Tx` to enable passing the full transaction data 
to Plutus scripts. This field is computed at the time of deserialization to contain all transactions 
corresponding to each `(txId, True)` in `requiredTxs`, with the `requiredTxs` field instantiated to `{}`.
Possibly, this field should be of type `TxInfo` instead.

### TxInfo

The `TxInfo` shown to a Plutus script is replaced with `(TxInfo, List TxInfo)` where the first
element of the pair is the usual `TxInfo`, including fields (1) and (2), the missing and extra value. 
The second element is a list of `TxInfo` values for all the transactions for which `TxInfo` (or `Tx`) is included 
in the `requiredFullTxBodies` field.


### Ledger Rule Changes

The prototype for the changes can be found
[here](https://github.com/IntersectMBO/formal-ledger-specifications/compare/polina-babel?expand=1)

#### ZONE

Currently, the top-level transaction-processing transition system in the ledger system is `LEDGERS`.
It considers a list of transactions in the block body valid whenever `LEDGER` is valid for
each transaction, checked in the order they appear in that list. We propose replacing `LEDGERS`
with

`ZONES ⊆ LEnv x LState x List (List Tx) x LState`

as the top level transition, which processes each zone in the block by
validating it with the transition

`ZONE ⊆ LEnv x LState x List Tx x LState`

The `ZONE` system includes two rules : `ZONE-V` may be applicable when all transactions are tagged with
`isValid` tag that is `True`, and `ZONE-N` may be applicable otherwise. The reason
for differentiating phase-2 valid and invalid _zones_ (and not just at the level
of individual transactions) is that it may not be possible to apply subsequent
transactions in a zone once a single transaction is found to be phase-2 invalid.
Recall that  
it is not possible to exclude only _some_ transactions from a zone in a general way,
so, unlike the existing design, the mempool is no able to reject individual zone transactions
dependent on a preceding transaction being phase-2 valid. We design the `ZONE-N`
rule to deal with this situation in a special way. 

The following checks are done by both rules :

1. the sum total of the sizes of all transactions in the zone is less than the `maxTxSize`
protocol parameter (see [Network Requirements and Changes](#network-requirements-and-changes)), and
2. the collateral provided by each transaction `tx` for script execution is sufficient
to cover **the size-based fees for all transactions corresponding to transactions in `requiredTxs`**
(see [DDoS](#ddos))
3. the `LEDGERS` transition is valid for the zone environment, transaction list,
and initial `LState` of `ZONE` transition
4. all collateral inputs must be in the initial `LState` UTxO set (see [DDoS](#ddos))
5. no transaction in a zone spends an output of another transaction in the same zone (see [Flash Loans](#flash-loans))
6. the sum total of the fees of all transactions in the zone is at least the sum of the 
required fees for all transactions in the zone (note that there are changes to fee and collateral requirements,
discussed below)
7. the sum of all `produced` calculations for all transactions in the zone is equal to
the sum of all `consumed` calculations for all transactions in that zone
8. the scripts and datums required for witnessing each of the transactions are present in 
the witness set of (at least one of) the transactions in the zone 
9. a transaction corresponding to each `txId` in the set of `requiredTxs` of each transaction
in the zone is also present in the zone


**`ZONE-V`**. This rule has no additional checks.

The updated state in this rule is computed by applying `LEDGERS` to the starting state,
environment, and list of transactions in the zone.

**`ZONE-N`**. This rule has additional checks :

1. the first transaction in the zone is phase-1 valid but phase-2 invalid

The updated state in this rule is the state computed by applying `LEDGERS`
by applying just that one transaction. 

#### UTXOW 

The `UTXOW` rule additionally checks that 

1. If any of the three new transaction fields are non-empty, the transaction being validated has 
only scripts written in the new version of Plutus.

The following checks are removed :

1. The checks that all scripts and all datums are present in the transaction is removed

#### UTXO

The `UTXO` rule is updated by :

1. removing the `produced = consumed` check (this is moved to the `ZONE` rule)
2. removing the sufficient fees check from `feesOK`
2. in `feesOK`, the collateral must now include `+ pp .b`, so that 

`(coin bal * 100) ≥ᵇ (txfee * pp .collateralPercentage) + pp .b`


#### UTXOS

The `UTXOS` rule is the one that actually computes the updates to
the UTxO state done by a transaction. The UTxO set update remains the same
as in the existing design. 


### System Component Changes

### Ledger

The ledger changes follow the specification changes outlined above, however,
we discuss additional things to consider in the process of integrating them into
the current ledger design in a way that follows
its principles and constraints. The prototype for ledger changes can be found
[here](https://github.com/IntersectMBO/cardano-ledger/pull/4477/files)

#### New Era

Since the validation zone/babel fees changes will constitute a hard fork, we define
a new era, `Babel`, alongside the existing ones. Everything that is unchanged is inherited from `Conway`.
Changes made to the following components require converting
certain existing types to associated types that differ across eras.

#### Block Structure

All blocks types in all previous eras contain sequences of transactions. We must allow Babel blocks to contain zones instead.

The component of the existing (old) block structure we're most concerned with is `TxSeq`. The purpose of `TxSeq` is to act as an abstract representation of a block's transaction structure, including some metadata.

```
-- OLD BLOCK STRUCTURE

data Block h era
  = Block' h (TxSeq era) BSL.ByteString

class
  EraSegWits era
  where
  type TxSeq era = (r :: Type) | r -> era
  fromTxSeq :: TxSeq era -> StrictSeq (Tx era)
  toTxSeq :: StrictSeq (Tx era) -> TxSeq era
```

We've changed the name of `TxSeq` to `TxZones`, and added a new `TxStructure` type to represent the underlying
concrete structure of transactions (without the metadata). Note that this change is likely to be specific
to the needs of the Haskell ledger codebase, but the concept of a per-era block structure is universal.

```
-- NEW BLOCK STRUCTURE

data Block h era
  = Block' h (TxZones era) BSL.ByteString

class
  EraSegWits era
  where
  type TxStructure era :: Type -> Type
  type TxZones era = (r :: Type) | r -> era

  fromTxZones :: TxZones era -> TxStructure era (Tx era)
  toTxZones :: TxStructure era (Tx era) -> TxZones era
```

The important change we've made is the addition of the `TxStructure` associated type. This allows us to be very clear with our intent; we can specify what concrete type the abstract `TxZones` represents per era, rather than mapping from `StrictSeq (StrictSeq (Tx era))` in eras which don't support zones. In other words, this allows us to specify the underlying transaction structure on a per-era basis.

  ```
  -- NEW CONCRETE INSTANCE OF TRANSACTION STRUCTURE

  instance Crypto c => EraSegWits (ConwayEra c) where
    type TxStructure (ConwayEra c) = StrictSeq
    ...

  instance Crypto c => Core.EraSegWits (BabelEra c) where
    type TxStructure (BabelEra c) = Compose StrictSeq StrictSeq
    ...
  ```

Understand, however, that `TxStructure` itself is very specific to the Haskell ledger codebase. The important change to make is to ensure the block's transaction structure can be different depending on the era.

Omitting `TxStructure` and mapping per era should also be acceptable, if desired:
  ```
  fromTxZones :: TxZones era -> StrictSeq (StrictSeq (Tx era))
  toTxZones :: StrictSeq (StrictSeq (Tx era)) -> TxZones era
  ```

An example of how this looks, in full, for two eras supporting different structures:
  ```
  instance Crypto c => EraSegWits (ConwayEra c) where
    type TxStructure (ConwayEra c) = StrictSeq
    type TxZones (ConwayEra c) = AlonzoTxSeq (ConwayEra c)
    fromTxZones = txSeqTxns
    toTxZones = AlonzoTxSeq

  instance Crypto c => Core.EraSegWits (BabelEra c) where
    type TxStructure (BabelEra c) = Compose StrictSeq StrictSeq
    type TxZones (BabelEra c) = BabelTxZones (BabelEra c)
    fromTxZones = Compose . txZonesTxns
    toTxZones = BabelTxZones . getCompose
  ```

For more information, search for `CIP-0118#block-structure-0` in the codebase, which can be found [here](https://github.com/willjgould/cardano-ledger/tree/wg/babel-fees-prototyping-babel-erafirstrule).
Please note that the most up-to-date prototype branch is `babel-fees-prototyping-babel-erafirstrule`.

#### Transaction structure

...

#### Ledger State

Probably no changes

#### Ledger State

The changes follow the specification changes

#### CBOR

...

### New Plutus Version

A new Plutus version is required. This version must accept the new structure of `TxInfo`.

### Consensus

We do not expect that any functional changes are required for consensus - the only
change needed is likely the updating of any references to the block body type,
which will be `List (List Tx)` instead of `List Tx`.

### Mempool

The mempool must switch to operating on zones instead of singleton transactions.
It must also support adding _part of a zone_ to a block in the case of phase-2
validation failure. That is, if a phase-2 invalid transaction is encountered
during zone validation, subsequent transactions are not validated, and only that 
phase-2 failing transaction, together with its required transactions, are included in the
zone. This partial zone is then included in the block.

### Network Requirements and Changes

Zones replace singleton transactions as units sent across the network. Zones must
therefore have IDs (e.g. zone hashes) for a node to determine whether it has
already downloaded the corresponding zone based on an ID it is observing on the network.
To maintain network functionality, zone sizes must be limited by the current `maxTxSize`
protocol parameter.

**Decision Required**. Is this an acceptable constraint for the usecases we
want to support?

### CLI and API

The node CLI should support the construction of the new type of transaction body,
as well as the construction and (local) validation of a zone.
The transaction balancing must also be modified in a way that lets the user explicitly 
(locally) specify the amounts they want to be missing or extra in a transaction. 

#### Zone Construction

Zones are either

- constructed from scratch locally (e.g. using the node CLI), or
- a (possibly incomplete) zone comes across a (non-Cardano) network, and a user
adds more transactions to it locally

The CLI should support both. Zone construction should give the user the ability to start a new zone and browse
an existing one, as well as add,
remove, and reorder transactions within an existing one. Determining the size of
a zone, and submitting a zone
to the network must be possible. Some special zone-level collateral calculation
functionality must also be implemented to accommodate `requiredTxs` (see [DDoS](#ddos)).

Note that it may be possible that a part of a (valid) validation zone itself constitutes
a valid validation zone, e.g. if the partial zone is balanced. 
Such a zone, when observed on the network, can be (locally)
deconstructed into smaller zone(s), which can be re-transmitted on the network.
An arbitrary zone can also be deconstructed and completed with new balancing transactions.
In both cases, resulting zone(s) are considered an entirely new validation units.


### Wallet and DBSync

We do not anticipate drastic changes to either, but this requires further investigation.
The DBSync will likely need to include a way to track the zone ID of transactions it records.
It may be desirable but not immediately necessary to integrate support for aspects of the required off-chain
infrastructure, e.g. order-matching and communication.

### Off-Chain

The off-chain component required for the functioning of this proposal
should be made up of at least the a way for users to :

- track market prices of non-Ada tokens
- communicate (partially valid) transactions
    - note here that it may be useful to transmit additional data about such transactions, such 
    as the amount of funds missing or extra
- perform intents matching

No off-chain component design is planned as part of this CIP. The reason
for this is that we hope to encourage pluralism in the approaches to
off-chain implementation. Off-chain intents-matching solutions are also more likely
to be less restrictive and able to evolve more quickly both in their design and the
rates they offer. Different approach are likely to be preferred by
users for the details of their usecases (see [Callout to the Community](#callout-to-the-community))

## Attacks and Mitigations

### DDoS

**Off-Chain**.
Since we do not propose an off-chain component, we do not discuss mitigation of
an off-chain DDoS attack, however, we note that such an attack consists of
communicating intents that may never be fulfilled. This is because either they
offer undesirable tokens for swaps, or set prices too high. It will be difficult
to determine whether any intent _will_ ever be fulfilled, or even whether it was
created with a malicious intent (spam).

**On-Chain (Mempool)**.
The possibility of un-fulfillable intents is an important reason for
transmitting only entire zones across the Cardano network. Upon validating an
incoming zone, a node is able to
determine whether to discard it or add it to the mempool. This is not the
case for intent-containing transactions. If we were to allow the mempool to
contain intent-containing transactions outside zones, such a transaction
could be placed in a mempool indefinitely, waiting for an appropriate
partially-valid counterpart to complete the zone. An attacker could fill up
a node's mempool with such transactions, rendering it unable to record
additional incoming transactions. Zone-based validation
prevents this attack.

**On-Chain (Phase-1)**.
Since zones are size-restricted by the constraint that currently restricts the
size of a single transaction (`maxTxSize`), we assume that the phase-1 validation cost
has the same limitations as before. So, phase-1 validation of a single
zone is likely to cost the same as phase-1 validation of a single transaction
currently costs. Therefore, we conjecture that the risks of a spam attack using phase-1
invalid entities is not increased as compared to what it currently is.

**On-Chain (Phase-2)**. The mempool attack scenario describes mitigation of an attack
which results in a DDoS by using up all the node's mempool storage. Another kind of
DDoS attack which we must defend against is one that involves a malicious
party sending transactions with large (i.e. memory- or CPU-use-intensive)
failing scripts. We refer to a script failure in a transaction as a _phase-2_ failure.

In the current ledger design, this is mitigated by requiring a transaction to provide
an amount of Ada collateral that is proportional to the sum of the sizes of all
its scripts. This collateral is collected in the case of script failure.
A phase-2 transaction failure in the design proposed in this CIP may result in phase-1 validation
failures of subsequent transactions.
To address this problem, we have defined the `ZONE-N` rule of `ZONE`. It requires
that the collateral of each transaction

- comes from the UTxO set to which the _zone_, rather than the transaction, is applied
- covers the size-based fee for the transactions corresponding to `requiredTxs` transactions 
in addition to itself

The `ZONE-N` rule only applies whenever there is one phase-2 invalid transaction `tx`
in the list. The only other transactions in the zone must necessarily be 
the transactions corresponding to `requiredTxs` specified by the invalid transaction. We do no validate
the `requiredTxs` at all, but the memory they take up in a block must be 
covered by collateral collected from `tx`. For this reason, the collateral of `tx` 
must be enough to cover the requirement for `tx` itself, plus the size-based 
fee required to cover the transactions in `requiredTxs`. 

It is not the case that we expect that a zone will always phase-2 fail at
the last transaction. Rather, a mempool should stop validating a zone, and 
instead construct a new zone, including only the script-failing transaction 
and its `requiredTxs` (so that scripts can be executed on the data they require). 
This new zone should be included 
in the block (see [Mempool](#mempool)).

### Flash Loans

A flash loan is a form of uncollateralized lending, e.g. done for the purpose of manipulating
the market price of an asset. Allowing dependencies between transactions in a zone makes
arbitrary flash loans possible that can easily be resolved by subsequent transactions in
the zone. This is particularly harmful in the case of flash-loaning tokens that 
serve a special purpose in the operation of smart contracts, such as role tokens, 
the presence of which is required for a transaction to update the state of a particular 
contract. E.g. consider the zone `[Tx1; Tx2]` :

`Tx1 : `

`(Resolved) inputs : txIn -> (out1)`

`Outputs: (1RoleToken, …) , (out2)`

`Tx2 :`

`(Resolved) inputs : (hash (Tx1), 1) -> (1RoleToken, …)`

where `out1` and `out2` are some outputs containing the state of some contract which can 
only be updated (from `out1` to `out2`) if the transaction contains a `RoleToken` that allows 
such an update to be made. 

Our design provides protection against this type of attack.
The `ZONE` transition always checks that there are no dependencies between zone transactions,
i.e. that no transaction in the zone is spending the output of another transaction in the 
same zone.

This requirement is the major driving difference between the design
in this CIP and the one published in the "Babel Fees via Limited Liabilities" paper.
The design presented in that work prevented flash loan attacks by
relying on the use of minting policies - a currency's minting policy is executed
whenever a transaction changes the total (positive or negative) amount of that currency. E.g.
if a transaction has 0 Ada in its inputs, but makes a request with the amount of Ada
it requires to pay transaction fees, the policy-running solution will not work for our design.
This is because many existing minting policies, e.g. of Ada, will fail in the usecases
we require for this CIP. Minting policies of existing tokens cannot be changed.

#### Price Manipulation and Frontrunning

Flash loans have to do with price manipulation via changing the total quantities of
tokens in existence by creating some in association with uncollateralized loans.
They can be considered a specific a kind of frontrunning.
Frontrunning, in general, has to do with the ability of certain entities to manipulate transactions
through displacement, suppression, or insertion. This amounts to manipulating
asset prices as well as controlling who gets to benefit from the trades.

We conjecture that outside of the possibility of flash loans (addressed above),
the opportunity for doing this on the Cardano network with the
CIP features implemented
are similar to that which existed prior to its implementation. Transaction
cancellation (see [Cancellation](#cancellation)) plays an important role in
preventing insertion of old (but previously not included) transactions making
requests at unfavourable prices.

As before,
every block producer gets to decide which transactions/zones will be included
in the block they are constructing, but
the specific block producer for a given block cannot be predicted ahead of
schedule. Also like in the current design, better offers are more likely to be
accepted.


#### Additional Risks

No obvious additional risks related to the expected functionality of this
proposal are predicted at this time. However, there are questions related to
community behaviour, such as the the likelihood of adoption of this feature,
and the likelihood that a robust off-chain mechanism will be built. 

## Rationale: how does this CIP achieve its goals?

### Design

We discuss a number of principles, requirements, and usecases to be supported by
this proposal.

**Supports paying fees in currency other than Ada (Babel Fees)**. This is achieved by allowing
users to construct transactions that do not spend any Ada inputs. Instead, the
transaction simply specifies the amount of fee that will be paid, and expects 
another transaction in the zone to provide it. Usually,
extra assets are also included to compensate any user that chooses to complete the
zone by submitting a transaction providing the missing Ada amount. See
[Usecases](#usecases). 

**Supports atomic swaps**. Atomic swaps work the exact same way as paying fees in
non-Ada currencies, with the difference being that instead of specifically Ada missing from 
the transaction balance, a user may have any currency missing, and any currency as extra 
in the transaction. 

**Counterparty irrelevance**. A desirable property expected of a system in which
atomic swaps are possible is that arbitrary users should have the ability to
engage with a swap offer, i.e.
you don’t have to specify who is on the other side of that part of the trade.
The design in this proposal naturally allows users to
build transactions that create both offers (i.e. extra assets) and requests
(i.e. missing assets) that can be balanced by arbitrary other users' transactions,
and therefore allow arbitrary users can engage with them to perform swaps.

**Does not interfere with existing ledger features**. Our design does not make
changes to the majority of transaction application protocols, e.g.
governance, staking/delegation, etc. Introducing zone structure into block
body should not affect transaction application. More formal analysis of this
may be required.

**Fee and collateral payment modification makes sense**. Transaction fees have 
three components : per-transaction, per-size, and script execution. The total size-based fees paid by 
all transactions in a zone are always proportional to the zone's size, same as 
in the existing design (but on the transaction level). In this model, fees can be paid by any transaction(s) 
in the zone, so long as the total amount is sufficient to cover all required 
fees for all transactions. Since the maximum zone 
size is the same as max transaction size, the per-transaction component fee is only required 
to be paid once per zone. The collateral must always include the per-transaction 
amount in addition to the script-execution amount of fees. Collateral 
collection works as before.

**Scripts can inspect other transactions in the zone**. The `requiredTxs` field 
allows users to specify additional transactions on which a given transaction 
depends. The resulting dependency graph can be any directed acyclic graph. 
The required transactions can, but do not have to be, shown to Plutus scripts. 
Only new-version scripts can be run in transactions with non-trivial new fields.
Running scripts that do not inspect additional transaction data will require 
less execution units. 

**Value flow modification makes sense**. Proving in Agda the POV property at the 
zone level is in progress, but no problems are foreseen here. The requirement 
that the sums of produced and consumed calculations are balanced at the zone level 
should suffice for this. 

**Minimizes off-chain communication**. Because unbalanced transactions cannot be sent
across the Cardano network, they are transmitted "off-chain". However, two-way
communication is not required in our design. The validation zones feature can be used
by either (off-chain) disseminating an unbalanced transaction 
(after which no further action from the sender is required), or observing an existing 
unbalanced transaction off-chain, and
building a balancing transaction before submitting them in a single zone to the Cardano network. 
Neither require
communicating with the counterparty who constructed the other transaction(s) in the zone.

**Minimizes reliance of smart contracts for key usecases**. This CIP allows
swaps to be performed without the use of smart contracts (at least ones that are
not simply unlocked), as shown in [Usecases](#usecases).
This is not only cheaper in terms of transaction size and
script-running costs, but makes it easier to propose and engage in a trade
within a single block.

**Keep order-matching logic off-chain**. Order matching is complicated task
involving many parties with possibly competing interests. Building such a mechanism
on-chain should only be done if the cost-benefit analysis is well in its favour.
For example, it appears the implementation on the [Stellar](https://stellar.org/blog/developers/introducing-automated-market-makers-on-stellar) system is not heavily used.
The Cardano platform changes we propose are fairly minor, unsophisticated, and comfortably aligned with
existing ledger design principles (e.g. predictable outcomes of transaction application).
This also allows the (off-chain) order-matching solutions to have a lot more flexibility
and adaptability.

**Mitigates Attacks**. The attacks we considered (and their mitigations) are discussed in
[Attacks and Mitigations](#attacks-and-mitigations).

### Other considerations

#### Cancellation

For many intent-based use cases it is useful to be able to cancel an intent, e.g.
for the purpose of updating bids to track changes in asset prices.
While cancellation is really an intent-processing problem, the design here affects
what cancellation approaches are possible.
There are a few approaches to cancellation that are compatible with the current design:

- Accept the lack of cancellation.
    - This is fine for use cases that don't care so much about cancellation, e.g. Babel fees: there we expect fast settlement and we don't expect the user to change their mind.
    - Contrast with e.g. Cardano itself: you can't rescind a transaction once you submit it.
- Cancel by spending an output that is required by your intent transaction, making it invalid.
    - This requires taking an expensive action on-chain, and managing the outputs that you use for this purpose.
    - This also requires being able to pay the transaction fee, which may be a problem for
    Babel fees users
    - This is not guaranteed in the case a fulfillment occurs some time between the user's
    decision to cancel and the cancelling transaction being placed into a block. The valid  
    zone including the fulfillment may make it into a block before the cancellation transaction
    (or, intentionally preferred over the cancellation by the producer)
    - Probably should come with a system to notify intent-processing systems that
    the cancellation has occurred, so that people do not waste time trying to fulfil it.
- Send around unsigned intents.
    - This loses the benefits of uni-directional communication, since intents now have come back to the user to sign, but allows you to cancel things by simply refusing to sign them.
- Use a trusted intermediary, who advertises intents but without some information that is needed to complete them (e.g. they strip the signatures and then advertise the unsigned version).
   - This lets the user go offline but retain many of the benefits of the previous approach.
- Set short TTLs on intent transactions so if they aren't settled quickly they become invalid.
   - This only works if you know ahead of time when you want things to expire: you can't cancel any sooner or later than that.

These approaches have different tradeoffs and different ones may be appropriate for different situations.

#### Era transition

A hard fork (era transition) is required to implement the changes proposed above,
currently implemented as a new `Babel` era.
A full set of features to be included in this era must be determined and agreed upon.
Additional development, analysis, testing, etc. will be required if more changes
are included.
So far, the validation zones proposal is not coupled with additional features.

#### Callout to the Community

Unbalanced transactions containing requests cannot be put on the chain by themselves : they are
fundamentally incomplete. As such, some kind of secondary networking is necessary
to distribute these incomplete transactions to the counterparties who can complete them.
That is: this proposal only addresses the intent-settlement problem, not
the intent-processing problem.

The author’s belief is that this is the right way to go because while on-chain
processing systems have desirable properties (e.g. they have censorship resistance
properties which cannot easily be matched by off-chain systems), designing an intent
settlement (e.g. order-matching)
system is a substantial research problem, and may entail different optimal solutions
for different user needs. Also, the changes to the Cardano platform introduced in this CIP
are merely an improvement on existing ways of doing things. If development of an off-chain
component is done after than the on-chain changes, this will not delay users
ability to perform desired tasks. For these reasons, the implementation of the on-chain and
off-chain mechanisms do not need to be introduced simultaneously.

However, implementing this CIP must include a callout to the community to
implement the off-chain component. Here are examples of two broad categories of  
design possibilities for such a component :

- A shared database for all users to share the assets they are willing to trade and
at what rates
  - This approach is better for buyers because of transparency (market prices are easy to track)
  - Someone has to maintain this
  - Trust model is unclear
  - Not everyone will want to use it, so likely multiple matching mechanism options are needed

- Users keep track of rates and available assets privately
  - No global way to track market prices
  - Easier to order match (optimizing for a single user's profit instead of trying to be "fair")

It is likely that both options will be useful.


## Use cases

### Open (atomic) swaps

A wants to swap 10 Ada for 5 tokens `myT`.

1. Party `A` creates a transaction `tx1` with
    - an output `0` which contains 5 `myT` tokens, and
    - an input containing 10 Ada
2. Party `A` sends `tx1` across some route that will get the swap offer into the hands of interested parties
3. Party `B` sees the transaction, and creates `tx2` with 
    - an output `0` which contains 10 Ada, and
    - an input containing 5 `myT` tokens
4. Party `B` submits a validation zone consisting of `tx1`, `tx2`

Note that:

- Party `B` does not need to go back to Party `A` to finish the swap
- Party `A`’s swap proposal could be fulfilled by anyone, 
- In step (2), we say "sends ... across some route that will get the swap offer into the hands of interested parties".
In subsequent usecases, we instead say "send ... to party X" to imply that X is a party that intends to
fulfill the sent intent(s), and has received them across the network.
- The per-transaction portion of the fee (`pp . b`) can be included in either `tx1`, `tx2`, or split across the two
in any proportion. 

### Partial swaps

A wants to swap 20 Ada for 10 tokens `myT`, but is ok swapping only some of the tokens. 

1. Party `A` creates a transaction `tx1` with
    - an output `0` which contains 10 `myT` tokens, and
    - an input containing 20 Ada
2. Party `A` sends `tx1` across some route that will get the swap offer into the hands of interested parties
3. Party `B` sees the transaction, and creates `tx2` with 
    - an output `0` which contains 10 Ada, and
    - an input containing 5 `myT` tokens
4. Party `B` disseminates `tx1, tx2` across some route such that it gets back to party `A`
5. Party `A` creates a transaction `tx3` with
    - an output `0` which contains 10 Ada, and
    - an input containing 5 `myT` tokens
6. Party `A` submits a validation zone `[tx1 ; tx2 ;  tx3]`

Note that:

- Party `A` has to cover any un-swapped tokens, in this case, `5 myT`
- Party `B` infers the exchange rate is 1:2 of `myT : Ada` based on the `10:20` ratio 
included by `A`, and can choose to follow this rate of not. Whether or not this exchange 
goes on chain eventually depends only on if someone else (`A` or not) completes the zone

### DEX aggregators

This is a simple extension of the previous example.
Instead of Party A, we have a set of parties A1 ... An who want to make various kinds of swap, and a batcher, Party B, who collects these and resolves them using some source of liquidity (in this example a big UTXO). `B` participates in the exchange if the transactions of the 
parties `A1...An` do not balance exactly.

1. Parties A1 ... An create transactions T1 ... Tn missing and extra assets representing their desired trades, as in the previous example.
2. Parties A1 ... An send T1 ... Tn to B
3. Party B creates two transactions:
    - T(n+1) spending Party B’s liquidity UTXO `u` which has enough liquidity to balance any missing assets in the transaction, and 
    includes an output `u'`, which is the updated liquidity pool containing the extra assets + what is left of liquidity in `u`
4. Party B submits a validation zone consisting of T1 ... T(n+1)


### Babel fees

Babel fees is a specific subtype of the first usecase where the missing assets are necessarily
a quantity of Ada. Usually, it also implies that no Ada is contained in the inputs
of such a transaction, and the missing Ada goes towards paying transaction fees.


### DApp fee and min-UTxO sponsorship

Party A wants to use a dApp operated by Party B (specifically, submit a transaction using a script S associated with the dApp).
Party B wants to cover the fees and min-UTxO value for this.

1. Party A creates a transaction T1 that uses script S, and is missing amount of Ada `a` to cover the script fees/min-UTxO.
2. Party A sends T1 to Party B
3. Party B creates a transaction T2 that has extra `a` Ada
4. Party B submits a validation zone consisting of T1 and T2

Note here that no offers are present in T1 because the the point of Dapp sponsorship
is for the Dapp to cover the fees and min-UTxO value without being compensated in
other tokens (although the Dapp itself may require depositing assets into it).
Note also that such a service should also offer a way to cover collateral, which 
is not addressed in this design. 

### Bridges

Centralized approaches to bridging tokens across blockchains have been developed,
e.g. by [SingularityNET](https://singularitynet.gitbook.io/welcome-to-singularitynet/bridge/overview).
A decentralized approach is much more difficult due to the requirement that
there must be some way to verify data about the operation of an external piece of
distributed software (on the side of both chains involved).
This CIP makes the centralized version of the bridging process slightly more
streamlined on the side of Cardano. Let B be a _trusted_ bridge. The untrusted
case requires additional research.

1. Party A sends an transaction T1 disposing of some tokens on chain D (either by burning
  them or putting them in a special token pool) to B as well as to chain D
2. Party A sends a transaction T2 missing the same amount of
  tokens as in (1) on the Cardano platform to B
3. Bridge B waits for T1 to settle on D, then submits the zone `[T2; T3]` to
  Cardano, where `T3` provides the assets missing in `T2`



### Towards Better Designs

### Original Babel Fees Design
When developing this proposal based on the
[Babel fees](https://iohk.io/en/research/library/papers/babel-fees-via-limited-liabilities/)
paper, we have observed a number of clashes between ledger design principles and
the proposal in the paper, as well as possible attack vectors. The key ones are :

**Checking minting policies**.
In the original paper, we attempted to prevent flash loan attacks by forcing
the execution of minting policies for any assets for which the total negative or
positive quantities were changed. This was not a viable strategy for existing
tokens, for which minting policies would overwhelmingly be unequipped to reason
about such cases. In this proposal, we instead perform the independency check
on the transactions in a zone. This ensures that tokens that do not come from 
the UTxO never appear in any (intermediate) outputs. 


### Westberg’s “Smart Transactions”

The design [Smart Transactions](https://github.com/input-output-hk/Developer-Experience-working-group/issues/47)
has a lot of similarities to ours, in particular it follows the approach where
transactions have partially unspecified inputs and outputs.
However, it goes much further and proposes conditions on how those can be satisfied,
as well as some kind of computed conditions for updating datums.
It also proposes that intent-processing be done by the node.

We think that we can eventually move in the direction of adding more of the
intent-settlement features from the proposal (e.g. conditions on values in inputs),
but the major point of disagreement is about intent processing.
As previously discussed, this proposal only focuses on intent settlement, not intent processing.
We now briefly discuss options of how to possibly proceed in this direction.

### CIP-0130 "[Transaction Pieces](https://github.com/cardano-foundation/CIPs/pull/873)"

Transaction pieces proposes a way to compose multiple transaction-like pieces into 
a single valid transaction. It appears that this could be a good solution to 
swaps, however, the following concerns arise as a result of allowing manipulating 
a transaction post-construction :

1. Signature-checking will be significantly affected. It will be necessary to determine 
which parts of a transaction must be signed by what keys (as opposed to checking signatures 
on whole transactions), which may be a non-trivial exercise.

2. Executing contracts that take as inputs transactions that can manipulated post-signing 
poses a potentially significant and unexplored risk. It is possible to make EUTxO contracts
to fail simply by changing the amount of data in a transaction. Making a transaction bigger will require more 
execution units than specified originally (for the smaller transaction). When executioin units 
run out before a script finishes executing, it results in validation failure. There may be other 
ways to make a script fail by maliciously manipulating transactions, at no (or low) cost to the 
adversary. 

### CIP-0118 "Validation Zones"

This version of validation zones has the following advantages over the previous version :

1. The validation zones simplification will remove the need to construct two separate 
transactions to resolve a single intent, one that consumes the offered value, and one that provides the requested value.
This significantly simplifies the expected interactions with the feature. 
An exchange aggregator would be able to spend their liquidity pool once per zone to provide any 
missing value and claim any extra value within a single transaction. 

2. No new version of Plutus is required since transaction structure is not changed. 
Scripts would operate without any disruption. 

3. Transactions will be smaller and cheaper because requests and fulfills do not need to 
be added to the body (missing and extra value is implicit). Transactions also only need to 
pay the per-transaction fee portion once per zone.

4. The feature is minimal, with fewer changes and more straightforward usecases.

The possible downsides of this design as compared to original validation zones include :

1. No option to restrict who can be the counterparty to a swap or impose any conditions on a swap

This can be addressed by introducing more specialized types of intents in the future. 

### Validation zones for settling other types of intents

This CIP establishes the notion of special type of transaction validation environment that may not 
satisfy the strict constraints of a valid ledger state. 
It does so by introducing the concept of a validation zone - a list of transactions that
can be validated as a whole, but it is impossible to check if the individual transactions
are valid outside a zone. We conjecture that infrastructure we propose can be used for processing
other types of underspecified transactions, and therefore more sophisticated
intents. A proof of this requires a
fleshed-out design for the expanded intent-processing system, which is outside the
scope of this CIP. The minimal changes of the 
design presented here are likely to be required for an

There is some risk that the best way to implement intents on Cardano is entirely different from
the underspecified transactions and validation zones approach we are taking here.
In that case such a design might entirely obsolete this one, making it an expensive
and pointless burden to maintain in future. However, the minimal changes of this 
design appear to be very extendible, and would allow for a variety of special transaction 
processing logic within a zone. In fact, it is likely that a validation zone-like feature, along 
with special considerations for accounting and fee payment (such as the one we propose) is 
essential for any kind of intent processing.


## Path to Active

### Software Readiness Level

It is difficult to specify the SRL for this CIP because it effects each component
of the Cardano node. The kind of testing required to thoroughly analyze the
changes we propose can only be done on testnet. We estimate that the SRL
would remain between 3 and 6 until

- an era is specified into which this feature is included
- a testnet containing this feature is launched

### Acceptance Criteria

- The use cases as described here can be implemented and tested on a testnet

### Implementation Plan

- Implementation of the proposed ledger changes in the formal ledger spec
- Updated CIP Specification with full detail
- Validation with community through Intersect
- Implementation in the Cardano node in the context of a new era/hardfork
- Deployment to testnet/mainnet

## Links to implementations




## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
